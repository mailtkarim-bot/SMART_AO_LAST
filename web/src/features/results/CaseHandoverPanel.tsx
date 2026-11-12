import { useEffect, useLayoutEffect, useRef, useState, useSyncExternalStore } from "react";
import type { ApiClient } from "../../infrastructure/api";
import type { CaseHandoverSnapshotItem, CaseHandoverOfferOption, HandoverContractOptions, HandoverOperationalReview } from "../../shared/types";
import { HandoverIntentStore, type HandoverIntent } from "./HandoverIntentStore";
import { HandoverReviewForm } from "./HandoverReviewForm";
import { HandoverSnapshotRead } from "./HandoverSnapshotRead";
const ids = () => ({
  command_id: crypto.randomUUID(),
  idempotency_key: crypto.randomUUID(),
  correlation_id: crypto.randomUUID()
});
const apiKeys = new WeakMap<object, string>();
let apiSequence = 0;
function apiKey(api: ApiClient) {
  let key = apiKeys.get(api);
  if (!key) {
    key = `connection-${++apiSequence}`;
    apiKeys.set(api, key);
  }
  return key;
}
type Props = {
  api: ApiClient;
  caseId: string;
  canManage: boolean;
  canReceive?: boolean;
  ownerKey?: string;
  pendingStore?: HandoverIntentStore;
  scopeKey?: string;
  sourceReadBlocked?: boolean;
};
export function CaseHandoverPanel(props: Props) {
  const [localStore] = useState(() => new HandoverIntentStore());
  const owner = props.ownerKey ?? JSON.stringify([apiKey(props.api), props.canManage, props.canReceive ?? false]);
  const scope = JSON.stringify([owner, props.caseId]);
  if (props.sourceReadBlocked) return <section className="section-block decision-section handover-panel" aria-label="Passation P7 au Conducteur"><h2>Passation au Conducteur</h2><p role="status">Sources en cours de reprise : passation suspendue jusqu’à la relecture du DCE. Aucun accord ni reçu reconduit.</p></section>;
  return <HandoverScope key={JSON.stringify([scope, props.scopeKey, props.canManage, props.canReceive])} {...props} scope={scope} store={props.pendingStore ?? localStore} />;
}
function HandoverScope({
  api,
  caseId,
  canManage,
  canReceive = false,
  scope,
  store
}: Props & {
  scope: string;
  store: HandoverIntentStore;
}) {
  const [items, setItems] = useState<CaseHandoverSnapshotItem[]>([]);
  const [options, setOptions] = useState<CaseHandoverOfferOption[]>([]);
  const [contracts, setContracts] = useState<HandoverContractOptions | null>(null);
  const [selected, setSelected] = useState('');
  const [readState, setReadState] = useState<'LOADING' | 'READY' | 'UNAVAILABLE'>('LOADING');
  const [optionsLoaded, setOptionsLoaded] = useState(false);
  const [message, setMessage] = useState('');
  const [history, setHistory] = useState<CaseHandoverSnapshotItem[]>([]);
  const [cursor, setCursor] = useState<string | null>(null);
  const [historyStarted, setHistoryStarted] = useState(false);
  const [historyBusy, setHistoryBusy] = useState(false);
  const [downloading, setDownloading] = useState<string | null>(null);
  const [editorEpoch, setEditorEpoch] = useState(0);
  const mounted = useRef(true);
  const reads = useRef(0);
  const posting = useRef(false);
  useLayoutEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);
  const pending = useSyncExternalStore(store.subscribe, store.getSnapshot).get(scope);
  const locked = !!pending;
  const uncertain = pending?.phase === 'UNKNOWN' || pending?.phase === 'SENDING';
  const choice = options.find(o => `${o.outcome_id}:${o.submission_package_id}` === selected);
  async function refresh() {
    const sequence = ++reads.current;
    const current = () => mounted.current && sequence === reads.current;
    try {
      const response = await api.listCaseHandoverSnapshots(caseId);
      if (!current()) return false;
      if (response.case_id !== caseId) throw Error('HANDOVER_CASE_MISMATCH');
      setItems(response.items);
      setReadState('READY');
      const saved = store.getSnapshot().get(scope);
      if (saved && (saved.phase === 'READ_REQUIRED' || saved.phase === 'CONFLICT')) {
        const intent = saved.intent;
        let candidates = response.items;
        const match = (row: CaseHandoverSnapshotItem) => intent.kind === 'PUBLISH' ? row.snapshot_id === intent.input.snapshot_id && row.outcome_id === intent.input.outcome_id && row.submission_package_id === intent.input.submission_package_id && (!intent.input.operational_review || row.manifest_sha256 === intent.input.operational_review.expected_offer_manifest_sha256) : row.snapshot_id === intent.snapshotId && !!row.receipts?.some(receipt => receipt.receipt_id === intent.input.receipt_id && receipt.view_sha256 === intent.input.expected_view_sha256);
        if (!candidates.some(match)) {
          try {
            const exact = await api.getCaseHandoverSnapshot(caseId, intent.kind === 'PUBLISH' ? intent.input.snapshot_id : intent.snapshotId);
            if (!current()) return false;
            candidates = [...candidates, exact];
          } catch {/* A missing read never confirms the act. */}
        }
        const found = candidates.some(match);
        if (found) {
          store.remove(scope);
          setMessage('Acte exact relu depuis le serveur.');
          setEditorEpoch(v => v + 1);
        } else if (saved.phase === 'CONFLICT') {
          store.remove(scope);
          setMessage('Conflit confirmé : relisez les sources avant une nouvelle intention.');
          setEditorEpoch(v => v + 1);
        } else setMessage('Reçu obtenu, projection exacte encore indisponible. Relisez sans créer de nouvel acte.');
      }
    } catch {
      if (current()) {
        setReadState('UNAVAILABLE');
        setItems([]);
      }
      return false;
    }
    if (canManage) {
      try {
        const response = await api.listCaseHandoverOfferOptions(caseId);
        if (!current()) return false;
        if (response.case_id !== caseId) throw Error('HANDOVER_CASE_MISMATCH');
        setOptions(response.items);
        setOptionsLoaded(true);
      } catch {
        if (current()) {
          setOptions([]);
          setOptionsLoaded(false);
        }
      }
      try {
        const response = await api.listCaseHandoverContracts(caseId);
        if (!current()) return false;
        if (response.case_id !== caseId) throw Error('HANDOVER_CASE_MISMATCH');
        setContracts(response);
      } catch {
        if (current()) setContracts(null);
      }
    }
    return true;
  }
  useEffect(() => {
    if (!uncertain) void refresh();else setReadState('LOADING'); /* scope owns and cancels these reads */
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  async function execute(intent: HandoverIntent) {
    if (posting.current) return;
    const previous = store.getSnapshot().get(scope);
    if (previous && JSON.stringify(previous.intent) !== JSON.stringify(intent)) return;
    posting.current = true;
    store.put(scope, {
      intent,
      phase: 'SENDING'
    });
    setMessage('');
    try {
      const receipt = intent.kind === 'PUBLISH' ? await api.recordCaseHandover(intent.caseId, intent.input) : await api.acknowledgeCaseHandover(intent.caseId, intent.snapshotId, intent.input);
      const expected = intent.kind === 'PUBLISH' ? 'CASE_HANDOVER_SNAPSHOT_RECORDED' : 'CASE_HANDOVER_RECEIPT_RECORDED';
      if (receipt.status !== 'SUCCEEDED' || receipt.result_code !== expected
        || receipt.command_id !== intent.input.command_id
        || receipt.idempotency_key !== intent.input.idempotency_key) throw Error('DISCORDANT_HANDOVER_RECEIPT');
      store.put(scope, {
        intent,
        phase: 'READ_REQUIRED'
      });
      if (mounted.current) await refresh();
    } catch (error) {
      const failure = error as { status?: number; detail?: string };
      const status = failure?.status;
      const terminalConflict = status === 409 && [
        'VERSION_CONFLICT', 'HANDOVER_OUTCOME_STALE', 'HANDOVER_CASE_CONTEXT_CONFLICT',
        'HANDOVER_OFFER_VERSION_CONFLICT', 'HANDOVER_CONTRACT_VERSION_CONFLICT',
        'HANDOVER_CONTRACT_SUPERSEDED', 'HANDOVER_VIEW_CONFLICT'
      ].includes(failure.detail ?? '');
      const phase = terminalConflict ? 'CONFLICT' : status === 409 ? 'UNKNOWN' : status !== undefined && status >= 400 && status < 500 && status !== 401 && status !== 403 && previous?.phase !== 'UNKNOWN' ? 'REJECTED' : 'UNKNOWN';
      store.put(scope, {
        intent,
        phase
      });
      if (mounted.current) {
        setMessage(phase === 'REJECTED' ? 'Refus confirmé : corrigez la revue avant une nouvelle intention.' : phase === 'CONFLICT' ? 'Conflit confirmé : relecture nécessaire.' : 'Résultat non confirmé. Réessayez uniquement le même acte, avec les mêmes identifiants.');
        if (phase === 'CONFLICT') await refresh();
      }
    } finally {
      posting.current = false;
    }
  }
  function publish(review: HandoverOperationalReview) {
    if (!canManage || !choice || locked) return;
    void execute({
      kind: 'PUBLISH',
      caseId,
      selected,
      input: {
        ...ids(),
        snapshot_id: crypto.randomUUID(),
        outcome_id: choice.outcome_id,
        submission_package_id: choice.submission_package_id,
        ...(review ? {
          operational_review: review
        } : {})
      }
    });
  }
  function receive(row: CaseHandoverSnapshotItem, kind: 'RECEIVED' | 'RECEIVED_WITH_GAPS', note: string) {
    if (!canReceive || !row.view_sha256 || locked) return;
    void execute({
      kind: 'RECEIVE',
      caseId,
      snapshotId: row.snapshot_id,
      input: {
        ...ids(),
        receipt_id: crypto.randomUUID(),
        expected_snapshot_revision: row.revision,
        expected_view_sha256: row.view_sha256,
        receipt_kind: kind,
        note,
        human_confirmed: true
      }
    });
  }
  async function download(row: CaseHandoverSnapshotItem) {
    if (downloading) return;
    setDownloading(row.snapshot_id);
    try {
      const blob = await api.downloadCaseHandoverOffer(caseId, row.snapshot_id);
      if (!mounted.current) return;
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = blob.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ? 'offre-technique.docx' : 'offre-technique.md';
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      if (mounted.current) setMessage('Téléchargement indisponible · vérifiez les droits Conducteur et l’intégrité du P5.');
    } finally {
      if (mounted.current) setDownloading(null);
    }
  }
  async function readHistory() {
    if (historyBusy) return;
    setHistoryBusy(true);
    try {
      const result = await api.listCaseHandoverHistory(caseId, cursor ?? undefined);
      if (!mounted.current) return;
      if (result.case_id !== caseId) throw Error('HANDOVER_CASE_MISMATCH');
      setHistory(previous => [...previous, ...result.items.filter(row => !previous.some(p => p.snapshot_id === row.snapshot_id))]);
      setCursor(result.next_cursor ?? null);
      setHistoryStarted(true);
    } catch {
      if (mounted.current) setMessage('Historique indisponible · UNKNOWN.');
    } finally {
      if (mounted.current) setHistoryBusy(false);
    }
  }
  return <section className="section-block decision-section handover-panel" aria-label="Passation P7 au Conducteur">
 <div className="section-heading"><h2>Passation au Conducteur</h2></div><p>P7 conserve l’offre attribuée, ses références et les conditions ouvertes. Cette passation ne crée pas un ordre de service.</p><p>Les données financières privées et le contenu financier du paquet P5 ne sont pas inclus. Lecture réservée au Patron et au Responsable affecté.</p>
 {message && <p role="status">{message}</p>}
 {pending && <div role="status"><strong>{pending.phase === 'SENDING' ? 'Acte en cours…' : pending.phase === 'UNKNOWN' ? 'UNKNOWN · intention figée' : pending.phase === 'REJECTED' ? 'Refus confirmé' : 'Relecture de l’acte nécessaire'}</strong>
 {pending.phase === 'UNKNOWN' && <button className="secondary-button" type="button" onClick={() => void execute(pending.intent)}>Réessayer la même passation</button>}
 {(pending.phase === 'READ_REQUIRED' || pending.phase === 'CONFLICT') && <button className="secondary-button" type="button" onClick={() => void refresh()}>Relire l’acte exact</button>}
 {pending.phase === 'REJECTED' && <button className="secondary-button" type="button" onClick={() => {
        store.remove(scope);
        setEditorEpoch(v => v + 1);
        setMessage('');
      }}>Reprendre la revue</button>}
 </div>}
 {canManage && <fieldset disabled={locked}><legend>Offre gagnée exacte</legend><label>Offre gagnée exacte à transmettre<select value={selected} disabled={!optionsLoaded} onChange={e => {
          setSelected(e.target.value);
          setEditorEpoch(v => v + 1);
          setMessage('');
        }}><option value="">Choisir une attribution WON et son paquet P5 autorisé</option>{options.map(o => <option key={`${o.outcome_id}:${o.submission_package_id}`} value={`${o.outcome_id}:${o.submission_package_id}`}>Lot {o.lot_reference} · paquet P5 v{o.package_version} · {o.manifest_sha256.slice(0, 12)}</option>)}</select></label>
 {optionsLoaded && options.length === 0 && <p>UNKNOWN · aucune offre P5 autorisée reliée à une attribution WON de cette Affaire.</p>}
 {choice && contracts && !contracts.truncated && <HandoverReviewForm key={`${selected}/${choice.manifest_sha256}/${contracts.source_context_sha256}/${editorEpoch}/${items.filter(i => i.outcome_id === choice.outcome_id).map(i => i.revision).join('/')}/${JSON.stringify(contracts.condition_options)}/${contracts.items.map(c => c.record_sha256).join('/')}`} contracts={contracts.items} conditions={contracts.condition_options} expectedRevision={Math.max(0, ...items.filter(i => i.outcome_id === choice.outcome_id).map(i => i.revision))} sourceContextSha={contracts.source_context_sha256} offerSha={choice.manifest_sha256} disabled={locked} onSubmit={publish} />}
 {choice && !contracts && <p>Revue contractuelle UNKNOWN · source ou droits financiers indisponibles. Aucune publication de texte privé.</p>}
 {contracts?.truncated && <p>Liste contractuelle ou conditions tronquée · UNKNOWN. La revue structurée reste verrouillée.</p>}

 </fieldset>}
 {!uncertain && <button className="secondary-button" type="button" onClick={() => void refresh()}>Relire la passation</button>}
 {readState === 'LOADING' && <p>Lecture serveur de la passation…</p>}
 {readState === 'UNAVAILABLE' && <p role="status">UNAVAILABLE · aucune passation confirmée n’est affichée. Vérifiez l’affectation Responsable si vous êtes Conducteur.</p>}
 {!uncertain && readState === 'READY' && items.length === 0 && <p>UNKNOWN · aucune passation P7 n’a encore été enregistrée.</p>}
 {!uncertain && readState === 'READY' && items.map(row => <HandoverSnapshotRead key={`${row.snapshot_id}/${row.view_sha256 ?? 'legacy'}`} item={row} canReceive={canReceive} disabled={locked || !!downloading} onDownload={() => void download(row)} onReceive={(kind, note) => receive(row, kind, note)} />)}
 {!uncertain && <><button className="secondary-button" type="button" disabled={historyBusy || historyStarted && !cursor} onClick={() => void readHistory()}>{historyStarted ? 'Lire les révisions précédentes' : 'Lire l’historique de passation'}</button>{history.map(row => <HandoverSnapshotRead key={`history/${row.snapshot_id}`} item={row} canReceive={false} disabled={locked || !!downloading} onDownload={() => void download(row)} onReceive={() => undefined} />)}</>}
 </section>;
}
