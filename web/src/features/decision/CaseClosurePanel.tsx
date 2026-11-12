import { Fragment, useCallback, useEffect, useRef, useState, type ComponentProps } from 'react';
import type { CaseTeachingSource } from '../../shared/types';
import type { ApiClient } from '../../infrastructure/api';
import { ChangeConfirmedForm, type ChangeConsent } from './ChangeConfirmedForm';
import type { ClosureDossier, ClosureIntent, ClosureOperation, ClosurePendingStore, ClosureRow } from './closureTypes';
const ops: Record<ClosureOperation, [string, string]> = {
  acts: ['act_id', 'CONTRACT_EXECUTION_EVIDENCE_RECORDED'],
  obligations: ['obligation_id', 'POST_RECEPTION_OBLIGATION_RECORDED'],
  'obligation-transitions': ['transition_id', 'POST_RECEPTION_OBLIGATION_TRANSITION_RECORDED'],
  cycles: ['cycle_id', 'PAYMENT_CYCLE_RECORDED'],
  'payment-facts': ['fact_id', 'PAYMENT_FACT_RECORDED'],
  rex: ['rex_id', 'EXECUTION_REX_RECORDED'],
  interviews: ['interview_id', 'CASE_INTERVIEW_RECORDED'],
  'teaching-reuse': ['applicability_id', 'CASE_TEACHING_APPLICABILITY_RECORDED']
};
const factLabels: Record<string, string> = {
  INVOICE_DECLARED: "Facture déclarée",
  PAYMENT_EXPECTED: "Paiement attendu",
  COLLECTION_RECORDED: "Encaissement déclaré humainement"
};
const refs = (value: FormDataEntryValue | null) => String(value ?? '').split('\n').map(s => s.trim()).filter(Boolean);
const text = (form: FormData, name: string) => String(form.get(name) ?? '').trim();
type Props = {
  api: ApiClient;
  caseId: string;
  ownerKey: string;
  scopeKey?:string;
  pendingStore?: ClosurePendingStore;
  sourceReadBlocked?: boolean;
};
export function CaseClosurePanel(props: Props) {
  const [localStore] = useState<ClosurePendingStore>(() => new Map());
  const scope = JSON.stringify([props.ownerKey, props.caseId]);
  if (props.sourceReadBlocked) return <section id="case-closure" className="section-block decision-section handover-panel" aria-label="Réception paiement et sortie de l’Affaire"><h2>Réception, réserves et paiement</h2><p role="status">Sources en cours de reprise : dossier suspendu jusqu’à la relecture du DCE. Aucun accord reconduit.</p></section>;
  return <ClosureWorkspace key={JSON.stringify([scope,props.scopeKey])} {...props} scope={scope} store={props.pendingStore ?? localStore} />;
}
function ClosureWorkspace({
  api,
  caseId,
  scope,
  store
}: {
  api: ApiClient;
  caseId: string;
  scope: string;
  store: ClosurePendingStore;
}) {
  const [notice, setNotice] = useState('');
  const [dossier, setDossier] = useState<ClosureDossier | null>(null),
    [unavailable, setUnavailable] = useState(false),
    [version, setVersion] = useState(0),
    [stage, setStage] = useState('reception');
  const [pending, setPendingState] = useState<ClosureIntent | null>(() => store.get(scope) ?? null);
  const pendingRef = useRef(pending),
    alive = useRef(true),
    readSequence = useRef(0);
  const sourceDossier = useRef<string | null>(null);
  useEffect(() => {
    alive.current = true;
    return () => {
      alive.current = false;
    };
  }, []);
  const update = useCallback((intent: ClosureIntent | null) => {
    pendingRef.current = intent;
    if (intent) store.set(scope, structuredClone(intent));else store.delete(scope);
    if (alive.current) setPendingState(intent);
  }, [scope, store]);
  const read = useCallback(async function read(reconcile?: ClosureIntent) {
    const sequence = ++readSequence.current;
    try {
      const value = await api.getCaseClosure(caseId);
      if (!alive.current || sequence !== readSequence.current) return;
      if (value.case_id !== caseId || !/^[a-f0-9]{64}$/.test(value.dossier_sha256)) throw Error('DISCORDANT_DOSSIER');
      if (sourceDossier.current !== null && sourceDossier.current !== value.dossier_sha256) setVersion(v => v + 1);
      sourceDossier.current = value.dossier_sha256;
      setDossier(value);
      setUnavailable(false);
      if (reconcile && (reconcile.terminalRefusal || reconciles(value, reconcile))) {
        if (reconcile.terminalRefusal) setNotice("Acte refusé sans effet : dossier relu. Préparez et confirmez un nouvel acte.");
        update(null);
        setVersion(v => v + 1);
      }
    } catch {
      if (alive.current && sequence === readSequence.current) {
        setDossier(null);
        setUnavailable(true);
      }
    }
  }, [api, caseId, update]);
  useEffect(() => {
    const old = store.get(scope);
    if (old?.phase === 'UNKNOWN' || old?.phase === 'SENDING') {
      if (old.phase === 'SENDING') update({
        ...old,
        phase: 'UNKNOWN'
      });
      return;
    }
    void read(old);
  }, [read, scope, store, update]); // Scope unmounts before another actor or Case can observe this state.
  async function send(intent: ClosureIntent) {
    if (pendingRef.current?.phase === 'SENDING') return;
    update({
      ...intent,
      phase: 'SENDING'
    });
    try {
      const receipt = await api.recordClosureOperation(caseId, intent.operation, intent.input);
      if (receipt.command_id !== intent.input.command_id || receipt.idempotency_key !== intent.input.idempotency_key || receipt[intent.identity] !== intent.input[intent.identity] || receipt.result_code !== intent.resultCode) throw Error('DISCORDANT_RECEIPT');
      const awaiting = {
        ...intent,
        phase: 'READ_REQUIRED' as const
      };
      update(awaiting);
      if (alive.current) await read(awaiting);
    } catch (error) {
      const failure = error as {
        status?: number;
        detail?: string;
      };
      if ([400, 401, 403, 404, 422].includes(failure.status ?? 0) && intent.phase === 'SENDING') {
        update(null);
        setVersion(v => v + 1);
        setNotice('Déclaration refusée : corrigez les valeurs et confirmez un nouvel acte.');
        return;
      }
      const terminal = failure.status === 409 && ['CLOSURE_VIEW_CONFLICT', 'PAYMENT_COMPARISON_SOURCE_CHANGED', 'EXECUTION_REX_SOURCE_CHANGED', 'EXECUTION_REX_SOURCE_CHANGED_OR_EXPIRED'].includes(failure.detail ?? '');
      const next = {
        ...intent,
        phase: terminal ? 'CONFLICT' as const : 'UNKNOWN' as const,
        terminalRefusal: terminal
      };
      update(next);
      if (failure.status === 409 && alive.current) await read(terminal ? next : undefined);
    }
  }
  function record(operation: ClosureOperation, input: Record<string, unknown>) {
    if (pendingRef.current || !dossier) return;
    setNotice('');
    const [identity, resultCode] = ops[operation];
    const body = {
      command_id: crypto.randomUUID(),
      idempotency_key: crypto.randomUUID(),
      [identity]: crypto.randomUUID(),
      ...input
    };
    void send({
      operation,
      input: structuredClone(body),
      identity,
      resultCode,
      phase: 'SENDING'
    });
  }
  const locked = Boolean(pending);
  function comparisons(form: FormData) {
    const options = dossier?.reference_options ?? [];
    const expected = options.find(r => r.kind + ':' + r.record_id === text(form, 'expected_ref'));
    const actual = options.find(r => r.kind + ':' + r.record_id === text(form, 'actual_ref'));
    if (!expected && !actual) return [];
    if (!expected || !actual || !text(form, 'comparison_note')) throw Error('COMPARE_BOTH_EXACT_SOURCES');
    const source = (r: typeof expected) => ({
      kind: r.kind,
      record_id: r.record_id,
      sha256: r.sha256
    });
    return [{
      expected: source(expected),
      actual: source(actual),
      note: text(form, 'comparison_note')
    }];
  }
  const review = (consent: ChangeConsent, form: FormData) => ({
    human_confirmed: true,
    justification: consent.justification,
    expected_dossier_sha256: dossier!.dossier_sha256,
    responsible: text(form, 'responsible') || null,
    expected_evidence: text(form, 'expected_evidence') || null,
    acknowledged_open_obligation_ids: form.get('acknowledge') ? dossier!.open_obligation_ids : [],
    comparisons: comparisons(form)
  });
  return <section id="case-closure" className="section-block decision-section handover-panel" aria-label="Réception paiement et sortie de l’Affaire">
  <div className="section-heading"><div><span className="section-kicker">RÉCEPTION ET SORTIE</span><h2>Réception, réserves et paiement</h2><p>Actes déclarés et preuves référencées. Aucun effet juridique, réception externe ou solde déduit.</p></div></div>
  {notice && <p role="status">{notice}</p>}
  {pending && <div className="detail-panel" role="status"><p>{pending.phase === 'UNKNOWN' ? 'Résultat UNKNOWN : cet acte reste figé.' : pending.phase === 'CONFLICT' ? 'Conflit : relisez le dossier et les sources avant toute autre action.' : pending.phase === 'READ_REQUIRED' ? 'Acte reçu : relecture exacte du dossier requise.' : 'Enregistrement en cours.'}</p>{pending.phase === 'UNKNOWN' && <button type="button" className="secondary-button" onClick={() => void send(pending)}>Réessayer le même acte</button>}{(pending.phase === 'CONFLICT' || pending.phase === 'READ_REQUIRED') && <button type="button" className="secondary-button" onClick={() => void read(pending)}>Relire le dossier</button>}</div>}
  {unavailable && <p role="alert">Dossier indisponible : les sources de cette Affaire ne peuvent pas être affichées.</p>}
  {!dossier && !unavailable && !pending && <p role="status">Chargement du dossier de sortie…</p>}
  {!pending && <button type="button" className="secondary-button" onClick={() => void read()}>Relire le dossier et ses sources</button>}
  {dossier && <Fragment key={version}>
   <p className="panel-empty">Version DCE : {dossier.dce_version_id ?? 'UNKNOWN'} · Complétude : {dossier.completeness_state} · Effet juridique : UNKNOWN · Règlement complet : UNKNOWN</p>
   <details><summary>Empreinte et portée du dossier relu</summary><p>{dossier.dossier_sha256}</p><p>Portée : {String(dossier.case_source.scope_fingerprint ?? 'UNKNOWN')} · Fraîcheur : {String(dossier.case_source.dce_freshness ?? 'UNKNOWN')}</p></details>
   <nav className="workflow-summary" aria-label="Étapes de réception et sortie">{[['reception', 'Réception'], ['reserves', 'Réserves et actions'], ['payment', 'Paiement'], ['exit', 'Sortie et REX']].map(([id, label]) => <button type="button" key={id} aria-pressed={stage === id} className="secondary-button" onClick={() => setStage(id)}>{label}</button>)}</nav>
   {stage === 'reception' && <>
    <h3>Actes de réception déclarés</h3>
    {dossier.acts.filter(a => a.act_kind === 'WORK_RECEPTION').length === 0 && <p>Aucune réception déclarée.</p>}
    {dossier.acts.filter(a => a.act_kind === 'WORK_RECEPTION').map(a => <SourceRow key={a.id} row={a} />)}
    <ClosureForm key={'reception' + version} label="Déclarer la réception" locked={locked} submit="Enregistrer la réception déclarée" onRecord={(form, consent) => record('acts', {
          act_kind: 'WORK_RECEPTION',
          reception_outcome: text(form, 'outcome'),
          summary: text(form, 'summary'),
          source_refs: refs(form.get('sources')),
          evidence_refs: refs(form.get('proofs')),
          declared_event_date: text(form, 'date') || null,
          contract_instrument_version_id: text(form, 'contract') || null,
          closure_review: review(consent, form)
        })}>
     <Field label="Résumé de réception" name="summary" /><Field label="Sources de réception" name="sources" /><Field label="Preuves de réception" name="proofs" />
     <label>État déclaré de réception<select name="outcome"><option value="WITH_RESERVATIONS">Avec réserves</option><option value="UNDER_RESERVATIONS">Sous réserves</option><option value="WITHOUT_RESERVATIONS">Sans réserves déclarées</option></select></label>
     <Field label="Date déclarée de réception" name="date" type="date" required={false} /><ContractSelect dossier={dossier} label="Version de contrat exacte (facultative)" /><FollowupFields />
    </ClosureForm>
   </>}
   {stage === 'reserves' && <>
    <h3>Réserves, obligations et responsables</h3>
    {!dossier.obligations.length && <p>Aucune obligation déclarée ; couverture UNKNOWN.</p>}
    {dossier.obligations.map(o => <article className="detail-panel" key={o.id}><SourceRow row={o} /><p>{o.declared_status} · Responsable : {o.responsible} · Preuve attendue : {o.expected_evidence}</p><p>Dernière transition déclarée : {o.history?.at(-1)?.rationale as string ?? 'UNKNOWN'}</p>
     {o.declared_status !== 'COMPLETED' && <ClosureForm label={'Suivre ' + o.summary} locked={locked} submit="Enregistrer le suivi déclaré" onRecord={(form, consent) => record('obligation-transitions', {
            obligation_id: o.id,
            expected_revision: o.history?.at(-1)?.revision ?? 0,
            resulting_status: text(form, 'status'),
            rationale: consent.justification,
            evidence_refs: refs(form.get('proofs'))
          })}><label>État du suivi<select name="status"><option value="IN_PROGRESS">En cours déclaré</option><option value="FOLLOW_UP_REQUIRED">Suivi requis</option><option value="UNKNOWN">UNKNOWN</option><option value="COMPLETED">Achevé déclaré avec preuve</option></select></label><Field label="Preuves du suivi" name="proofs" required={false} /></ClosureForm>}
    </article>)}
    <ClosureForm key={'obligation' + version} label="Déclarer une réserve ou obligation" locked={locked} submit="Enregistrer l’obligation" onRecord={(form, consent) => record('obligations', {
          obligation_type: text(form, 'type'),
          origin_reception_act_id: text(form, 'origin') || null,
          summary: text(form, 'summary'),
          source_refs: refs(form.get('sources')),
          due_date: text(form, 'date') || null,
          closure_review: review(consent, form)
        })}>
     <label>Type d’obligation<select name="type"><option value="RESERVES_LIFTING">Levée de réserve</option><option value="DOE_DIUO">DOE / DIUO</option><option value="GUARANTEE_RELEASE">Libération de garantie à suivre</option><option value="ADMIN_CLOSURE">Clôture administrative à suivre</option><option value="OPR">OPR</option><option value="TESTS">Essais</option><option value="COMMISSIONING">Mise en service</option><option value="TRAINING">Formation</option><option value="GPA">GPA à suivre</option><option value="INITIAL_MAINTENANCE">Maintenance initiale</option><option value="SPARE_STOCK">Stock de rechange</option><option value="ON_CALL">Astreinte</option></select></label>
     <label>Réception origine (réserves uniquement)<select name="origin"><option value="">UNKNOWN / sans lien</option>{dossier.acts.filter(a => a.act_kind === 'WORK_RECEPTION' && ['WITH_RESERVATIONS', 'UNDER_RESERVATIONS'].includes(a.reception_outcome ?? '')).map(a => <option key={a.id} value={a.id}>{a.summary}</option>)}</select></label>
     <Field label="Résumé de l’obligation" name="summary" /><Field label="Sources de l’obligation" name="sources" /><Field label="Date de suivi déclarée (aucun délai légal calculé)" name="date" type="date" required={false} /><FollowupFields />
    </ClosureForm>
   </>}
   {stage === 'payment' && <>
    <h3>Facture, paiement attendu et encaissement déclaré</h3><p>Encaissement : {dossier.financial_observations.collection_state} · Solde : UNKNOWN. Chaque montant conserve sa devise et sa date déclarée.</p>
    {dossier.facts.map(f => <article key={f.fact_id} className="detail-panel"><div className="panel-heading"><h3>{factLabels[f.kind ?? ""] ?? "Nature UNKNOWN"}</h3><span className="state-badge">{f.context_state}</span></div><p className="panel-empty">{f.amount_minor?.toLocaleString("fr-FR")} unités monétaires mineures · {f.currency_code} · {f.declared_date}</p><SourceRow row={f} /></article>)}
    {dossier.financial_observations.comparisons.map(c => <p key={c.recorded_fact_id}>Écart de cette paire déclarée : {c.difference_minor ?? 'UNKNOWN'} unités mineures {c.currency_code} · {c.source_state}. Aucune conclusion sur le solde.</p>)}
    <ClosureForm key={'cycle' + version} label="Déclarer un cycle de paiement" locked={locked} submit="Enregistrer le cycle déclaré" onRecord={(form, consent) => record('cycles', {
          source_refs: refs(form.get('sources')),
          trigger_event: text(form, 'trigger'),
          status: 'REVIEW_REQUIRED',
          cash_assumption: consent.justification
        })}><Field label="Déclencheur déclaré" name="trigger" /><Field label="Sources du cycle" name="sources" /></ClosureForm>
    {dossier.cycles.length > 0 && <ClosureForm key={'fact' + version} label="Déclarer un fait financier" locked={locked} submit="Enregistrer le fait financier déclaré" onRecord={(form, consent) => record('payment-facts', {
          cycle_id: text(form, 'cycle'),
          kind: text(form, 'kind'),
          amount_minor: Number(text(form, 'amount')),
          currency_code: text(form, 'currency'),
          declared_date: text(form, 'date'),
          source_refs: refs(form.get('sources')),
          evidence_refs: refs(form.get('proofs')),
          compared_to_fact_id: text(form, 'parent') || null,
          justification: consent.justification,
          human_confirmed: true,
          expected_dossier_sha256: dossier.dossier_sha256
        })}>
     <label>Cycle exact<select name="cycle" required>{dossier.cycles.map(c => <option value={c.id} key={c.id}>{c.trigger_event} · {c.id}</option>)}</select></label>
     <label>Nature du fait<select name="kind"><option value="INVOICE_DECLARED">Facture déclarée</option><option value="PAYMENT_EXPECTED">Paiement attendu</option><option value="COLLECTION_RECORDED">Encaissement constaté et déclaré humainement</option></select></label>
     <Field label="Montant entier en unités monétaires mineures" name="amount" type="number" min="1" step="1" /><Field label="Devise déclarée à trois lettres" name="currency" defaultValue="EUR" pattern="[A-Z]{3}" /><Field label="Date du fait déclarée" name="date" type="date" />
     <Field label="Sources du fait financier" name="sources" /><Field label="Preuves du fait financier" name="proofs" />
     <label>Paire prévue/réalisée explicite<select name="parent"><option value="">Aucune comparaison (UNKNOWN)</option>{dossier.facts.filter(f => f.kind !== 'COLLECTION_RECORDED').map(f => <option value={f.fact_id} key={f.fact_id}>{f.kind} · {f.amount_minor} {f.currency_code} · {f.fact_id}</option>)}</select></label>
    </ClosureForm>}
   </>}
   {stage === 'exit' && <>
    <h3>Sortie déclarée et enseignements</h3><p>{dossier.open_obligation_ids.length} obligation(s) encore ouvertes. Une sortie déclarée ne les efface pas.</p>
    {dossier.acts.filter(a => a.act_kind !== 'WORK_RECEPTION').map(a => <SourceRow key={a.id} row={a} />)}
    <ClosureForm key={'exit' + version} label="Déclarer la sortie" locked={locked} submit="Enregistrer la sortie déclarée" onRecord={(form, consent) => record('acts', {
          act_kind: 'CONTRACT_EXIT',
          summary: text(form, 'summary'),
          source_refs: refs(form.get('sources')),
          evidence_refs: refs(form.get('proofs')),
          declared_event_date: text(form, 'date') || null,
          contract_instrument_version_id: text(form, 'contract') || null,
          closure_review: review(consent, form)
        })}>
     <Field label="Résumé de sortie" name="summary" /><Field label="Sources de sortie" name="sources" /><Field label="Preuves de sortie" name="proofs" /><Field label="Date de sortie déclarée" name="date" type="date" required={false} /><ContractSelect dossier={dossier} label="Contrat source de sortie (facultatif)" /><FollowupFields />
     {dossier.open_obligation_ids.map(id => <p key={id}>{id} · {dossier.obligations.find(o => o.id === id)?.summary} · UNKNOWN / suivi restant</p>)}
     {!!dossier.open_obligation_ids.length && <label><input type="checkbox" name="acknowledge" required />J’ai relu ces obligations ouvertes ; elles restent ouvertes après cette sortie déclarée.</label>}
     <label>Source prévue exacte<select name="expected_ref"><option value="">UNKNOWN / non comparée</option>{(dossier.reference_options ?? []).map(r => <option key={r.kind + r.record_id} value={r.kind + ':' + r.record_id}>{r.kind} · {r.label} · {r.context_state}</option>)}</select></label>
     <label>Source réalisée exacte<select name="actual_ref"><option value="">UNKNOWN / non comparée</option>{(dossier.reference_options ?? []).map(r => <option key={r.kind + r.record_id} value={r.kind + ':' + r.record_id}>{r.kind} · {r.label} · {r.context_state}</option>)}</select></label>
     <Field label="Écart prévu/réalisé déclaré entre ces deux sources" name="comparison_note" required={false} />
     <p>Sans les deux sources et une lecture humaine : comparaison UNKNOWN. Aucun effet juridique ou solde déduit.</p>
    </ClosureForm>
    <ExecutionRex dossier={dossier} locked={locked} version={version} record={record} />
    <TeachingReuse key={caseId} api={api} dossier={dossier} locked={locked} version={version} record={record} />
   </>}
  </Fragment>}
 </section>;
}
function Field({
  label,
  ...props
}: {
  label: string;
} & ComponentProps<'input'>) {
  return <label>{label}<input required maxLength={2000} {...props} /></label>;
}
function FollowupFields() {
  return <><Field label="Responsable déclaré (sinon UNKNOWN)" name="responsible" required={false} maxLength={500} /><Field label="Preuve attendue (sinon UNKNOWN)" name="expected_evidence" required={false} /></>;
}
function SourceRow({
  row
}: {
  row: ClosureRow;
}) {
  return <div className="panel-empty">{row.summary && <strong>{row.summary}</strong>}<p>{row.reception_outcome ?? row.context_state ?? 'UNKNOWN'} · {row.id ?? row.fact_id}</p><p>État source : {row.context_state ?? 'UNKNOWN'}</p><p>Sources : {row.source_refs_json?.join(' · ') || 'UNKNOWN'}</p><p>Preuves référencées : {row.evidence_refs_json?.join(' · ') || 'UNKNOWN'}</p></div>;
}
function ClosureForm({
  label,
  locked,
  submit,
  onRecord,
  children
}: {
  label: string;
  locked: boolean;
  submit: string;
  onRecord: (form: FormData, consent: ChangeConsent) => void;
  children: React.ReactNode;
}) {
  const [invalid, setInvalid] = useState(false);
  const consent = useRef<ChangeConsent>({
    human_confirmed: true,
    justification: '',
    publish: false
  });
  return <ChangeConfirmedForm className="workflow-form" aria-label={label} locked={locked} onApprove={value => {
    consent.current = value;
  }} onSubmit={event => {
    event.preventDefault();
    if (!locked) {
      try {
        onRecord(new FormData(event.currentTarget), consent.current);
        setInvalid(false);
      } catch {
        setInvalid(true);
      }
    }
  }}><fieldset className="workflow-form" disabled={locked}><legend>{label}</legend>{children}{invalid && <p role="alert">Choisissez les deux sources exactes et décrivez leur écart, ou laissez les deux inconnues.</p>}<button type="submit" className="secondary-button">{submit}</button></fieldset></ChangeConfirmedForm>;
}
function ExecutionRex({
  dossier,
  locked,
  version,
  record
}: {
  dossier: ClosureDossier;
  locked: boolean;
  version: number;
  record: (op: ClosureOperation, input: Record<string, unknown>) => void;
}) {
  return <>
  {dossier.rex.map(r => <article className="detail-panel" key={r.id}><strong>{r.observation}</strong><p>{r.consequence} · Action REX : {r.follow_up}</p><p>Lot : {r.lot_reference} · {r.validation} · Réemploi jamais automatique</p></article>)}
  {!!dossier.acts.filter(a => a.act_kind === 'CONTRACT_EXIT' && a.closure_review_json).length && <ClosureForm key={'rex' + version} label="Publier un enseignement d’exécution" locked={locked} submit="Enregistrer le REX humain" onRecord={(form, consent) => record('rex', {
      exit_act_id: text(form, 'exit'),
      lot_reference: text(form, 'lot'),
      scope: text(form, 'scope'),
      validation: text(form, 'validation'),
      observation: text(form, 'observation'),
      consequence: text(form, 'consequence'),
      follow_up: text(form, 'follow_up'),
      source_locator: text(form, 'source'),
      human_confirmed: true,
      publish_to_rex: true,
      justification: consent.justification,
      expected_dossier_sha256: dossier.dossier_sha256
    })}>
   <label>Sortie exacte<select name="exit" required>{dossier.acts.filter(a => a.act_kind === 'CONTRACT_EXIT' && a.closure_review_json).map(a => <option value={a.id} key={a.id}>{a.summary} · {a.context_state}</option>)}</select></label>
   <label>Lot prouvé ou UNKNOWN<select required name="lot">{(dossier.lot_references?.length ? dossier.lot_references : ["UNKNOWN"]).map(lot => <option key={lot}>{lot}</option>)}</select></label><Field label="Observation REX à publier" name="observation" /><Field label="Conséquence observée déclarée" name="consequence" /><Field label="Action ou recommandation REX" name="follow_up" /><Field label="Source opérationnelle du REX" name="source" />
   <label>Portée humaine du réemploi<select name="scope"><option value="CASE_ONLY">Cette Affaire seulement</option><option value="LOT_PATTERN">Motif de lot à réexaminer humainement</option></select></label>
   <label>Revue de l’enseignement<select name="validation"><option value="PENDING">À revoir</option><option value="APPROVED">Approuvé humainement pour examen ultérieur</option></select></label>
   <label><input type="checkbox" required />Je publie ces seuls textes opérationnels dans le REX ; aucune donnée financière privée n’y est copiée.</label>
  </ClosureForm>}
  {!!dossier.rex.length && <ClosureForm key={'interview' + version} label="Figer la revue REX" locked={locked} submit="Figer l’entretien humain" onRecord={(form, consent) => record('interviews', {
      held_on: text(form, 'date'),
      expires_on: text(form, 'expiry'),
      source_locator: text(form, 'source'),
      rationale: consent.justification
    })}><Field label="Date d’entretien déclarée" name="date" type="date" /><Field label="Fin de validité déclarée" name="expiry" type="date" /><Field label="Source de l’entretien" name="source" /></ClosureForm>}
  {dossier.interviews.map(i => <p key={i.id}>Entretien figé {i.id} · {i.held_on} · Validité déclarée jusqu’au {i.expires_on}</p>)}
  <p>Choisissez l’Affaire cible, puis sa source et l’enseignement figé dans le réemploi ci-dessous. Aucune application implicite.</p>
 </>;
}
function reconciles(dossier: ClosureDossier, intent: ClosureIntent) {
  const groups: Record<ClosureOperation, ClosureRow[]> = {
    acts: dossier.acts,
    obligations: dossier.obligations,
    'obligation-transitions': dossier.obligations.flatMap(o => o.history ?? []),
    cycles: dossier.cycles,
    'payment-facts': dossier.facts,
    rex: dossier.rex,
    interviews: dossier.interviews,
    'teaching-reuse': dossier.reuse_history
  };
  const id = intent.input[intent.identity];
  const row = groups[intent.operation].find(r => (r.id ?? r.fact_id) === id);
  if (!row) return false;
  return Object.entries(intent.input).every(([key, value]) => {
    if (['command_id', 'idempotency_key', intent.identity, 'human_confirmed', 'expected_dossier_sha256', 'publish_to_rex'].includes(key)) return true;
    if (key === 'exit_act_id') return row.execution_exit_act_id === value;
    if (key === 'justification' && intent.operation === 'rex') return (row.execution_source_json as Record<string, unknown>)?.human_justification === value;
    const column = key === 'source_refs' ? 'source_refs_json' : key === 'evidence_refs' ? 'evidence_refs_json' : key === 'closure_review' ? 'closure_review_json' : key;
    if (key === 'expected_revision') return row.revision === Number(value) + 1;
    if (key === 'expected_target_dossier_sha256') return ((row.source_snapshot_json as Record<string, unknown>)?.execution_reuse as Record<string, unknown>)?.expected_target_dossier_sha256 === value;
    return subset(row[column], value);
  });
}
function subset(actual: unknown, expected: unknown): boolean {
  if (Array.isArray(expected)) return Array.isArray(actual) && actual.length === expected.length && expected.every((v, i) => subset(actual[i], v));
  if (expected !== null && typeof expected === 'object') return actual !== null && typeof actual === 'object' && Object.entries(expected).every(([k, v]) => subset((actual as Record<string, unknown>)[k], v));
  return actual === expected;
}
function TeachingReuse({
  api,
  dossier,
  locked,
  version,
  record
}: {
  api: ApiClient;
  dossier: ClosureDossier;
  locked: boolean;
  version: number;
  record: (op: ClosureOperation, input: Record<string, unknown>) => void;
}) {
  const [sources, setSources] = useState<CaseTeachingSource[] | null>(null);
  useEffect(() => {
    let current = true;
    api.listCaseTeachingSources?.(dossier.case_id).then(value => {
      if (current && value.case_id === dossier.case_id) setSources(value.sources.filter(s => s.snapshot.execution_exit_act_id));
    }).catch(() => {
      if (current) setSources(null);
    });
    return () => {
      current = false;
    };
  }, [api, dossier.case_id, version]);
  return <div className="detail-panel"><h3>Réemploi humain dans cette Affaire cible</h3><p>Le motif de lot, l’état de la source et la validité doivent être relus pour cette nouvelle situation.</p>{sources?.length === 0 && <p>Aucun enseignement d’exécution figé disponible pour ce réemploi.</p>}{sources === null && <p>Bibliothèque de réemploi indisponible / UNKNOWN.</p>}
 {Boolean(sources?.length) && <ClosureForm key={'reuse' + version} label="Décider le réemploi humain" locked={locked} submit="Enregistrer la décision de réemploi" onRecord={(form, consent) => {
      const chosen = sources!.find(s => s.source_interview_id + ':' + s.source_rex_id === text(form, 'teaching'));
      if (!chosen) return;
      record('teaching-reuse', {
        target_case_id: dossier.case_id,
        source_case_id: chosen.source_case_id,
        source_interview_id: chosen.source_interview_id,
        source_rex_id: chosen.source_rex_id,
        decision: text(form, 'decision'),
        rationale: consent.justification,
        target_source_locator: text(form, 'target_source'),
        human_confirmed: true,
        expected_target_dossier_sha256: dossier.dossier_sha256
      });
    }}>
 <label>Enseignement et entretien sources exacts<select required name="teaching">{sources!.map(s => <option key={s.source_interview_id + s.source_rex_id} value={s.source_interview_id + ':' + s.source_rex_id}>{s.source_case_label} · {s.snapshot.observation} · {s.source_validity} · {s.snapshot.scope} · {s.snapshot.validation}</option>)}</select></label>
 <label>Décision humaine pour cette Affaire<select name="decision"><option value="REVIEW_REQUIRED">À revoir</option><option value="NOT_APPLICABLE">Non applicable</option><option value="APPLICABLE">Applicable selon la revue humaine</option></select></label><Field label="Source exacte dans l’Affaire cible" name="target_source" /></ClosureForm>}
 {dossier.reuse_history.map(r => <p key={r.id}>Décision de réemploi déclarée : {String(r.decision)} · Contexte actuel : {String(r.context_state ?? "UNKNOWN")} · {String(r.rationale)} · Source cible : {String(r.target_source_locator)}. Aucun effet automatique.</p>)}
 </div>;
}
function ContractSelect({
  dossier,
  label
}: {
  dossier: ClosureDossier;
  label: string;
}) {
  return <label>{label}<select name="contract"><option value="">UNKNOWN / non relié</option>{(dossier.contract_versions ?? []).map(c => <option value={c.id} key={c.id}>{String(c.version_reference)} · {c.id}</option>)}</select></label>;
}
