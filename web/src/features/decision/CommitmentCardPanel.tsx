import { useEffect, useState, useRef, useSyncExternalStore, type FormEvent } from "react";
import type { ApiClient } from "../../infrastructure/api";
import type { ConditionalGoConditionRequest, DecisionContextReferenceInput } from "../../shared/types";
import { AnalysisTreatmentRead, axisLabels } from "../dce/AnalysisTreatmentFields";
import type { CardDecision, CardIntent, CardPoint, CardReceipt, CommitmentCard, CardCondition } from "./commitmentTypes";
type Pending = {
  intent: CardIntent;
  phase: "SENDING" | "UNKNOWN" | "READ_REQUIRED" | "CONFLICT";
  receipt: CardReceipt | null;
};
/** App-lifetime recovery; private intents never enter browser storage. */
export class CommitmentPendingStore {
  private snapshot: ReadonlyMap<string, Pending> = new Map();
  private listeners = new Set<() => void>();
  getSnapshot = () => this.snapshot;
  subscribe = (fn: () => void) => {
    this.listeners.add(fn);
    return () => {
      this.listeners.delete(fn);
    };
  };
  put(key: string, value: Pending) {
    const old = this.snapshot.get(key);
    if (old && JSON.stringify(old.intent) !== JSON.stringify(value.intent)) throw Error("COMMITMENT_INTENT_CONFLICT");
    const next = new Map(this.snapshot);
    next.set(key, structuredClone(value));
    this.snapshot = next;
    this.listeners.forEach(fn => fn());
  }
  remove(key: string) {
    const next = new Map(this.snapshot);
    next.delete(key);
    this.snapshot = next;
    this.listeners.forEach(fn => fn());
  }
}
type Props = {
  api: ApiClient;
  enabled: boolean;
  sourceReadBlocked?: boolean;
  caseId: string;
  actorId: string;
  ownerKey: string;
  scopeKey: string;
  dceVersionId?: string | null;
  pendingStore: CommitmentPendingStore;
  onDecisionChanged?: () => void;
  onOpenAnalysis?: () => void;
};
type ConditionDraft = {
  id: string;
  label: string;
  date: string;
  absence: string;
  consequence: string;
};
const newIds = () => ({
  command_id: crypto.randomUUID(),
  idempotency_key: crypto.randomUUID()
});
export function CommitmentCardPanel(props: Props) {
  if (!props.enabled || !props.caseId) return null;
  if (props.sourceReadBlocked) return <section className="section-block" id="commitment-card-section"><h2>Carte d’engagement de l’Affaire</h2><p role="status">Carte suspendue : un acte sur le DCE ou le dossier reste à résoudre. Les accords antérieurs ne sont pas repris ; résolvez l’acte exact avant toute relecture.</p></section>;
  return <CardEditor key={JSON.stringify([props.ownerKey, props.scopeKey, props.caseId, {
    version: props.dceVersionId
  }])} {...props} />;
}
function CardEditor({
  api,
  caseId,
  actorId,
  ownerKey,
  pendingStore,
  onDecisionChanged,
  onOpenAnalysis,
  dceVersionId
}: Props) {
  const key = JSON.stringify([ownerKey, caseId]);
  const pending = useSyncExternalStore(pendingStore.subscribe, pendingStore.getSnapshot).get(key);
  const [data, setData] = useState<CommitmentCard | null>(null);
  const [error, setError] = useState("");
  const [formError, setFormError] = useState("");
  const [refresh, setRefresh] = useState(0);
  const [why, setWhy] = useState("");
  const [unknowns, setUnknowns] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [confirmationPoint, setConfirmationPoint] = useState("");
  const [requalificationConfirmed, setRequalificationConfirmed] = useState(false);
  const [outcome, setOutcome] = useState<"" | "CONDITIONAL_GO" | "NO_GO" | "GO">("");
  const [conditions, setConditions] = useState<ConditionDraft[]>([]);
  const [conditionId, setConditionId] = useState("");
  const [assessmentId, setAssessmentId] = useState("");
  const [older, setOlder] = useState<{
    entries: CardDecision[];
    next: string | null;
  } | null>(null);
  const [historyBusy, setHistoryBusy] = useState(false);
  const historyInFlight = useRef(false);
  useEffect(() => {
    if (pending?.phase === "UNKNOWN" || pending?.phase === "SENDING") return;
    let alive = true;
    api.getCommitmentCard(caseId).then(async value => {
      if (!alive) return;
      if (value.case_id !== caseId || !Array.isArray(value.points) || !Array.isArray(value.axes) || value.axes.length !== 12 || value.gate_effect !== "NONE" || value.analysis_complete !== false) throw Error("Projection discordante");
      if (dceVersionId !== undefined && value.dce_version_id !== dceVersionId) throw Error("Version discordante");
      if (value.points.some(row => row.point.source_state === "CURRENT_SOURCE" && row.point.source_anchor?.dce_version_id !== value.dce_version_id)) throw Error("Ancre discordante");
      if (pending?.receipt && pending.intent.kind === "CONFIRM") {
        const intent = pending.intent; const receipt = pending.receipt;
        if (value.dce_version_id === intent.dceVersionId && !value.references.some(ref => ref.aggregate_type === "DCE_REQUIREMENT" && ref.aggregate_id === intent.requirementId && ref.aggregate_revision >= receipt.version)) throw Error("Confirmation non retrouvée dans les références courantes");
      }
      if (pending?.receipt && pending.intent.kind !== "CONFIRM") {
        const receipt = pending.receipt;
        if (!receipt.decision_id) throw Error("Décision absente du reçu");
        const records = [value.current_decision, ...value.history];
        let decision = records.find(d => d && d.decision_id === receipt.decision_id && d.aggregate_revision >= receipt.version);
        if (!decision) {
          const exact = await api.getCommitmentDecision(caseId, receipt.decision_id);
          if (!alive) return;
          if (exact.case_id !== caseId || exact.decision.decision_id !== receipt.decision_id || exact.decision.aggregate_revision < receipt.version) throw Error("Relecture discordante");
          decision = exact.decision;
        }
        if (!decision || receipt.context_id && decision.context_id !== receipt.context_id || receipt.link_id && !decision.assessment_links.some(l => l.link_id === receipt.link_id)) throw Error("Relecture du reçu non prouvée");
      }
      setData(value);
      setConfirmationPoint("");
      setRequalificationConfirmed(false);
      setError("");
      setOlder(null);
      setConfirmed(false);
      setConditionId("");
      setAssessmentId("");
      if (pending?.phase === "CONFLICT") setFormError("L’acte a été refusé pour conflit. L’état courant est relu ; aucune réussite de cet envoi n’est présumée.");
      if (pending) {
        pendingStore.remove(key);
        setWhy("");
        setConfirmed(false);
        setConditions([]);
        setOutcome("");
        setConditionId("");
        setAssessmentId("");
        onDecisionChanged?.();
      }
    }).catch(() => {
      if (alive) {
        setData(null);
        setError("Lecture indisponible ou discordante : UNKNOWN. Réessayez la lecture.");
      }
    });
    return () => {
      alive = false;
    };
  }, [api, caseId, key, pending, pendingStore, refresh, onDecisionChanged, dceVersionId]);
  async function loadOlder() {
    const before = older ? older.next : data?.history_has_more ? data.history.at(-1)?.decision_id : null;
    if (!before || historyInFlight.current) return;
    historyInFlight.current = true;
    setHistoryBusy(true);
    try {
      const page = await api.getCommitmentHistory(caseId, before);
      if (page.case_id !== caseId || !Array.isArray(page.history) || page.history.some(d => d.decision_id === before) || page.next_before_decision_id === before) throw Error("Historique discordant");
      setOlder(previous => ({
        entries: [...(previous?.entries ?? []), ...page.history],
        next: page.next_before_decision_id
      }));
    } catch {
      setFormError("Historique indisponible : réessayez sa lecture.");
    } finally {
      historyInFlight.current = false;
      setHistoryBusy(false);
    }
  }
  async function send(intent: CardIntent) {
    if (pendingStore.getSnapshot().get(key)?.phase === "SENDING") return;
    pendingStore.put(key, {
      intent,
      phase: "SENDING",
      receipt: null
    });
    try {
      let receipt: CardReceipt;
      switch (intent.kind) {
        case "CONFIRM": {
          const result = await api.confirmDceRequirement(intent.requirementId, intent.input);
          const ref = result.aggregate_refs.find(ref => ref.aggregate_type === "DCE_REQUIREMENT_CONFIRMATION");
          if (result.status !== "SUCCEEDED" || result.result_code !== "DCE_REQUIREMENT_CONFIRMED" || !ref) throw Error("Reçu de confirmation incomplet");
          receipt = {command_id: result.command_id, idempotency_key: result.idempotency_key, confirmation_id: ref.aggregate_id, version: ref.aggregate_revision};
          break;
        }
        case "CREATE":
          receipt = await api.createDecision(caseId, intent.input);
          break;
        case "FREEZE":
          receipt = await api.freezeDecisionContext(caseId, intent.decisionId, intent.input);
          break;
        case "FINALIZE":
          receipt = await api.finalizeDecision(caseId, intent.decisionId, intent.input);
          break;
        case "LINK":
          receipt = await api.linkConditionAssessment(caseId, intent.decisionId, intent.conditionId, intent.input);
          break;
      }
      if (receipt.command_id !== intent.input.command_id || receipt.idempotency_key !== intent.input.idempotency_key || !Number.isSafeInteger(receipt.version) || receipt.version < 0) throw Error("Reçu discordant");
      if (intent.kind === "CONFIRM") {
        if (receipt.confirmation_id !== intent.input.confirmation_id || receipt.version !== intent.input.expected_confirmation_revision + 1) throw Error("Confirmation discordante");
      } else {
        if (!receipt.decision_id) throw Error("Décision absente du reçu");
      if (intent.kind !== "CREATE" && receipt.version !== (intent.kind === "LINK" ? intent.input.expected_decision_revision : intent.input.expected_revision) + 1) throw Error("Révision de reçu discordante");
      if (intent.kind !== "CREATE" && receipt.decision_id !== intent.decisionId) throw Error("Décision discordante");
      if (intent.kind === "FREEZE" && receipt.context_id !== intent.input.context_id) throw Error("Contexte discordant");
      if (intent.kind === "LINK" && receipt.link_id !== intent.input.link_id) throw Error("Lien discordant");
      }
      pendingStore.put(key, {
        intent,
        phase: "READ_REQUIRED",
        receipt
      });
    } catch (failure) {
      pendingStore.put(key, {
        intent,
        phase: (failure as {
          status?: number;
        }).status === 409 ? "CONFLICT" : "UNKNOWN",
        receipt: null
      });
    }
  }
  function references(): DecisionContextReferenceInput[] {
    return (data?.references ?? []).map(({
      content_hash,
      ...ref
    }) => ({
      ...ref,
      ...(content_hash ? {
        content_hash
      } : {})
    }));
  }
  function freeze(event: FormEvent) {
    event.preventDefault();
    if (!data?.current_decision || pending || !confirmed || !why.trim()) return;
    const missing = [...unknowns.split("\n").map(v => v.trim()).filter(Boolean), ...(data.unbound_contract_impacts ?? []).map(id => `Impact contractuel ${id} hors références faute de profil courant : UNKNOWN`)];
    if (missing.length > 100) {
      setFormError("Maximum cent inconnus, un par ligne.");
      return;
    }
    setConfirmed(false);
    void send({
      kind: "FREEZE",
      decisionId: data.current_decision.decision_id,
      input: {
        ...newIds(),
        context_id: crypto.randomUUID(),
        expected_revision: data.current_decision.aggregate_revision,
        rationale: why.trim(),
        unknowns: missing,
        references: references()
      }
    });
  }
  function finalize(event: FormEvent) {
    event.preventDefault();
    const decision = data?.current_decision;
    if (!decision?.context_fingerprint || pending || !confirmed || !why.trim() || !outcome) return;
    try {
      const declared: ConditionalGoConditionRequest[] = outcome === "CONDITIONAL_GO" ? conditions.map(c => {
        if (!c.label.trim() || !c.consequence.trim() || !c.date && !c.absence.trim()) throw Error("Chaque condition exige un libellé, un responsable, une conséquence et une date ou sa raison d’absence.");
        return {
          condition_id: c.id,
          label: c.label.trim(),
          owner_actor_id: actorId,
          failure_consequence: c.consequence.trim(),
          ...(c.date ? {
            due_at: new Date(c.date).toISOString()
          } : {
            due_date_absence_reason: c.absence.trim()
          })
        };
      }) : [];
      if (outcome === "CONDITIONAL_GO" && !declared.length) throw Error("Ajoutez au moins une condition.");
      setFormError("");
      setConfirmed(false);
      void send({
        kind: "FINALIZE",
        decisionId: decision.decision_id,
        input: {
          ...newIds(),
          expected_revision: decision.aggregate_revision,
          displayed_fingerprint: decision.context_fingerprint,
          outcome,
          justification: why.trim(),
          conditions: declared
        }
      });
    } catch (failure) {
      setFormError((failure as Error).message);
    }
  }
  const decision = data?.current_decision;
  const linkable = (data?.points ?? []).filter(row => row.point.human_assessment?.state === "CURRENT" && decision?.references.some(ref => ref.aggregate_type === "ANALYSIS_ASSESSMENT" && ref.aggregate_id === row.point.human_assessment?.assessment_id && ref.aggregate_revision === row.point.human_assessment?.revision));
  function link(event: FormEvent) {
    event.preventDefault();
    const point = linkable.find(row => row.point.human_assessment?.assessment_id === assessmentId);
    const act = point?.point.human_assessment;
    if (!decision || !act || !confirmed || !why.trim() || !decision.conditions.some(c => c.condition_id === conditionId && c.status === "OPEN") || pending) return;
    setConfirmed(false);
    void send({
      kind: "LINK",
      decisionId: decision.decision_id,
      conditionId,
      input: {
        ...newIds(),
        link_id: crypto.randomUUID(),
        assessment_id: act.assessment_id,
        assessment_revision: act.revision,
        source_context_sha256: act.source_context_sha256,
        expected_decision_revision: decision.aggregate_revision,
        justification: why.trim(),
        human_confirmed: true
      }
    });
  }
  const common = <><label>Justification de l’acte sur la carte<textarea required maxLength={4000} value={why} onChange={e => {
        setConfirmed(false);
        setWhy(e.target.value);
      }} /></label><label><input type="checkbox" checked={confirmed} onChange={e => setConfirmed(e.target.checked)} />Je confirme l’acte, les sources et les inconnus affichés pour cette Affaire. MFA requise.</label></>;
  return <section className="section-block scenario-creation" aria-label="Carte d’engagement"><h2>Carte d’engagement de l’Affaire</h2>
  <p>Lecture des douze axes et des actes enregistrés. Une relation absente reste UNKNOWN. Aucun score, prix, analyse complète ou passage de porte n’est déduit de cette carte.</p>
  {pending ? <div role="status"><p>{pending.phase === "UNKNOWN" ? "UNKNOWN — résultat de l’acte inconnu. Données et identifiants conservés." : pending.phase === "SENDING" ? "Enregistrement de l’acte…" : "Relecture nécessaire après reçu ou conflit."}</p>{pending.phase === "UNKNOWN" ? <button type="button" className="secondary-button" onClick={() => void send(pending.intent)}>Réessayer exactement cet acte</button> : pending.phase !== "SENDING" && <button type="button" className="secondary-button" onClick={() => setRefresh(v => v + 1)}>Réessayer la relecture</button>}</div> : <>
  {!data && !error && <p role="status">Lecture de la carte…</p>}
  {data && <><p>Contexte source : {data.source_context_state}. Analyse exhaustive : non démontrée.{data.truncated && " Données tronquées : consultez les registres et affinez le dossier avant décision."}</p>
   <p>Pièces non lues : {data.coverage?.unread_documents ?? "UNKNOWN"}.</p>
   <p>Revue du dossier : {data.dossier_review?.state ?? "UNKNOWN"} · {data.dossier_review?.phase ?? "Revue globale non enregistrée"}.</p>
   <div className="line-table-wrap" role="region" tabIndex={0} aria-label="Les douze axes, défilement horizontal"><table><thead><tr><th>Axe</th><th>État de lecture</th></tr></thead><tbody>{data.axes.map(axis => <tr key={axis.code}><td>{axisLabels[axis.code]}</td><td>{axis.status}</td></tr>)}</tbody></table></div>
   <p><a href="#case-analysis-summary-section" onClick={event => {if(onOpenAnalysis){event.preventDefault();onOpenAnalysis();}}}>Préparer ou revoir les points dans le dossier d’analyse</a></p>
   {data.points.length === 0 ? <p>Aucun point critique disponible — UNKNOWN.</p> : data.points.map(row => <Point key={row.point_key} row={row} conditions={decision?.conditions ?? []} />)}
   {(data.unbound_contract_impacts?.length ?? 0) > 0 && <p>Impacts contractuels hors références : {data.unbound_contract_impacts!.length}. Profil métier courant à qualifier. Ces liens restent UNKNOWN dans le contexte proposé.</p>}
   {data.points.filter(row => row.point.kind === "REQUIREMENT" && row.point.source_state === "CURRENT_SOURCE" && row.point.native_state !== "CONFIRMED").map(row => <section key={row.point_key} aria-label={`Confirmation du signal ${row.point.item_id}`}>
    <h3>{row.point.source_excerpt ?? row.point.title ?? row.point.native_type}</h3>
    <p>Exigence {row.point.item_id} · révision {row.point.native_revision ?? "UNKNOWN"} · DCE {data.dce_version_id ?? "UNKNOWN"} · document {row.point.source_anchor?.dce_document_id ?? "UNKNOWN"} · SHA-256 {row.point.source_anchor?.source_sha256 ?? "UNKNOWN"}.</p>
    <p>Le traitement d’analyse ne confirme pas l’exigence native. Relisez le signal et sa source exacte ; la confirmation change son contexte et impose un traitement actualisé avant gel.</p>
    <label><input type="checkbox" checked={confirmationPoint === row.point.item_id} onChange={event => setConfirmationPoint(event.target.checked ? row.point.item_id : "")} />Je confirme avoir relu ce signal et sa source exacte, sans confirmer sa conformité ni lever de porte.</label>
    <button type="button" className="secondary-button" disabled={confirmationPoint !== row.point.item_id || !data.dce_version_id || !Number.isSafeInteger(row.point.native_revision) || row.point.native_revision! < 0} onClick={() => {if(typeof row.point.native_revision!=="number")return;setConfirmationPoint("");void send({kind:"CONFIRM",requirementId:row.point.item_id,dceVersionId:data.dce_version_id!,input:{...newIds(),confirmation_id:crypto.randomUUID(),expected_confirmation_revision:row.point.native_revision,outcome:"CONFIRMED",reason_code:"SOURCE_REVIEWED"}});}}>Confirmer le signal source</button>
   </section>)}
   {!data.references.some(ref => ref.aggregate_type === "DCE_REQUIREMENT") && <p>Gel indisponible : aucune exigence DCE confirmée dans les références courantes. Les contrôles natifs restent souverains.</p>}
   {decision?.lifecycle === "FINALIZED" && decision.state === "REVIEW_REQUIRED" && data.source_context_state === "CURRENT" && <section>
    <p>La décision finale reste historique. Le serveur vérifie le changement de DCE avant tout nouveau cycle ; un refus ne crée ni brouillon ni accord.</p>
    <label><input type="checkbox" checked={requalificationConfirmed} onChange={event => setRequalificationConfirmed(event.target.checked)} />Je confirme la préparation d’un nouveau brouillon sur le DCE courant, sans reprendre l’accord antérieur.</label>
    <button type="button" className="secondary-button" disabled={!requalificationConfirmed} onClick={() => {setRequalificationConfirmed(false);void send({kind:"CREATE",input:{...newIds(),scope_fingerprint:data.case_scope_fingerprint}});}}>Demander un nouveau brouillon</button>
   </section>}
   <h3>Décision Patron</h3>{decision ? <Decision value={decision} /> : <p>Aucune décision enregistrée.</p>}
   {!decision && <button type="button" className="secondary-button" onClick={() => void send({
          kind: "CREATE",
          input: {
            ...newIds(),
            scope_fingerprint: data.case_scope_fingerprint
          }
        })}>Créer un brouillon de décision</button>}
   {decision?.lifecycle === "DRAFT" && <form onSubmit={freeze}><h3>Présenter ces références à la décision</h3><p>Les références ci-dessous seront gelées par cet acte explicite.</p><details className="case-resolution-sources"><summary>Références exactes proposées</summary><ul>{data.references.map(ref => <li key={`${ref.aggregate_type}:${ref.aggregate_id}`}>{ref.aggregate_type} · {ref.aggregate_id} · révision {ref.aggregate_revision} · {ref.content_hash ?? "Hash non requis par ce type de référence"}</li>)}</ul></details>
    <label>Inconnus à conserver, un par ligne<textarea maxLength={4000} value={unknowns} onChange={e => {
              setConfirmed(false);
              setUnknowns(e.target.value);
            }} /></label>{common}
    {!data.references.some(ref => ref.aggregate_type === "ANALYSIS_ASSESSMENT") && <p>Enregistrez le traitement sourcé d’au moins un point avant de présenter cette carte.</p>}
    <button className="primary-button" type="submit" disabled={!confirmed || !why.trim() || data.truncated || !data.references.some(ref => ref.aggregate_type === "ANALYSIS_ASSESSMENT") || !data.references.some(ref => ref.aggregate_type === "DCE_REQUIREMENT")}>Geler ces références pour revue</button></form>}
   {decision?.lifecycle === "PENDING_PATRON" && decision.context_status === "FROZEN" && decision.state === "CURRENT" && <form onSubmit={finalize}><h3>Décider explicitement</h3>
    <label>Décision motivée<select required value={outcome} onChange={e => {
              setConfirmed(false);
              setOutcome(e.target.value as typeof outcome);
            }}><option value="">Choisir une décision</option><option value="NO_GO">NO-GO</option><option value="CONDITIONAL_GO">GO sous conditions</option><option value="GO">GO explicite selon les contrôles existants</option></select></label>
    {outcome === "CONDITIONAL_GO" && <><p>Chaque condition reste ouverte jusqu’à un acte de résolution distinct.</p>{conditions.map((condition, index) => <fieldset key={condition.id}><legend>Condition {index + 1}</legend>{([['label', 'Objet'], ['date', 'Échéance déclarée'], ['absence', 'Raison de date inconnue'], ['consequence', 'Conséquence si non levée']] as const).map(([field, label]) => <label key={field}>{label}<input aria-label={`Condition ${index + 1} — ${label}`} type={field === "date" ? "datetime-local" : "text"} required={field === "label" || field === "consequence"} maxLength={field === "label" ? 500 : 1000} value={condition[field]} onChange={e => {
                  setConfirmed(false);
                  setConditions(rows => rows.map(row => row.id === condition.id ? {
                    ...row,
                    [field]: e.target.value
                  } : row));
                }} /></label>)}<p>Responsable : vous, Patron ({actorId}).</p><button className="secondary-button" type="button" onClick={() => {
                setConfirmed(false);
                setConditions(rows => rows.filter(row => row.id !== condition.id));
              }}>Retirer la condition {index + 1}</button></fieldset>)}<button className="secondary-button" type="button" disabled={conditions.length >= 32} onClick={() => {
              setConfirmed(false);
              setConditions(rows => [...rows, {
                id: crypto.randomUUID(),
                label: "",
                date: "",
                absence: "",
                consequence: ""
              }]);
            }}>Ajouter une condition</button></>}
    {common}<button type="submit" className="primary-button" disabled={!confirmed || !why.trim() || !outcome}>Enregistrer cette décision humaine</button></form>}
   {decision?.lifecycle === "FINALIZED" && decision.outcome === "CONDITIONAL_GO" && decision.state === "CURRENT" && <form onSubmit={link}><h3>Relier une condition au point qui la justifie</h3>
    <label>Condition ouverte<select required value={conditionId} onChange={e => {
              setConfirmed(false);
              setConditionId(e.target.value);
            }}><option value="">Choisir une condition</option>{decision.conditions.filter(c => c.status === "OPEN").map(c => <option key={c.condition_id} value={c.condition_id}>{c.label}</option>)}</select></label>
    <label>Acte d’analyse exact<select required value={assessmentId} onChange={e => {
              setConfirmed(false);
              setAssessmentId(e.target.value);
            }}><option value="">Choisir le point et sa révision</option>{linkable.map(row => <option key={row.point_key} value={row.point.human_assessment!.assessment_id}>{row.point.title ?? row.point.source_excerpt ?? row.point.native_type} · révision {row.point.human_assessment!.revision}</option>)}</select></label>
    {assessmentId && <p>Preuve attendue : {linkable.find(row => row.point.human_assessment?.assessment_id === assessmentId)?.point.human_assessment?.expected_evidence ?? "UNKNOWN"}</p>}
    {common}<button type="submit" className="primary-button" disabled={!confirmed || !why.trim() || why.trim().length > 2000 || !conditionId || !assessmentId}>Enregistrer le lien sans lever la condition</button></form>}
   {data.history.length > 0 && <details><summary>Historique des décisions et de leurs sources</summary>{[...data.history, ...(older?.entries ?? [])].map(value => <Decision key={value.decision_id} value={value} />)}{(older ? older.next !== null : data.history_has_more) && <button type="button" className="secondary-button" disabled={historyBusy} onClick={() => void loadOlder()}>Lire les décisions plus anciennes</button>}</details>}
  </>}
  {error && <p role="alert">{error}</p>}{formError && <p role="alert">{formError}</p>}<button type="button" className="secondary-button" onClick={() => setRefresh(v => v + 1)}>Relire la carte et l’historique</button></>}
 </section>;
}
function Point({
  row,
  conditions
}: {
  row: CardPoint;
  conditions: CardCondition[];
}) {
  const point = row.point;
  const act = point.human_assessment?.state === "CURRENT" ? point.human_assessment : null;
  return <article className="detail-panel case-resolution-sources"><h3>{point.title ?? (point.source_excerpt ? point.source_excerpt.slice(0, 120) + (point.source_excerpt.length > 120 ? "…" : "") : "Point critique")} — {point.severity ?? "UNKNOWN"}</h3><p>Axes : {row.axes.map(code => axisLabels[code as keyof typeof axisLabels] ?? code).join(" · ")}. Portée lot : {point.lot_numbers.length ? point.lot_numbers.join(", ") : "UNKNOWN"} ({point.lot_state}).</p>
  <p>Fait/extrait source : {point.source_excerpt ?? "UNKNOWN"}</p><p>État de source : {point.source_state}</p>
  {point.source_anchor && <details><summary>Source, version, hash et région exacts</summary><pre className="review-draft-content">{JSON.stringify({
          anchor: point.source_anchor,
          start: point.start_byte_offset,
          end: point.end_byte_offset
        }, null, 2)}</pre></details>}
  {act?.treatment ? <AnalysisTreatmentRead value={act.treatment} actorId={act.actor_id} /> : <><p>Hypothèses déclarées : UNKNOWN.</p><p>Applicabilité, conséquences, responsable et action : UNKNOWN.</p></>}
  {act && <details><summary>Acte humain enregistré · révision {act.revision}</summary><p>Auteur : {act.actor_id} · {act.created_at}</p><p>Justification : {act.justification}</p></details>}
  <p>Preuve attendue : {act?.expected_evidence ?? "UNKNOWN"}. Risque résiduel : {act?.residual_risk ?? "UNKNOWN"}.</p>
  <p>Liens enregistrés : {row.relations_state}. Action référencée : {point.follow_ups?.some(r => r.kind === "ACTION") ? "RECORDED" : "UNKNOWN"}. Impact contractuel relié : {point.follow_ups?.some(r => r.kind === "CONTRACT_IMPACT") ? "RECORDED" : "UNKNOWN"}. Condition reliée : {row.condition_links.length || point.follow_ups?.some(r => r.kind === "CONDITION") ? "RECORDED" : "UNKNOWN"}.</p>
  {point.follow_ups?.map(rel => <p key={`${rel.kind}:${rel.record_id}`}>{rel.kind} · {rel.description} · conséquence : {rel.consequence ?? "UNKNOWN"} · {rel.state}</p>)}
  {row.condition_links.map(link => <p key={link.link_id}>Condition reliée : {conditions.find(c => c.condition_id === link.condition_id)?.label ?? link.condition_id} · {conditions.find(c => c.condition_id === link.condition_id)?.status ?? "UNKNOWN"} · acte {link.assessment_id} v{link.assessment_revision} · {link.justification}</p>)}
 </article>;
}
function Decision({
  value
}: {
  value: CardDecision;
}) {
  return <article className="detail-panel case-resolution-sources"><h4>Cycle {value.cycle_number} — {value.outcome} — {value.state}</h4><p>Révision {value.aggregate_revision} · {value.lifecycle} · {value.validity}</p><p>Motivation : {value.final_justification ?? value.rationale ?? "UNKNOWN"}</p><p>Auteur de décision : {value.finalized_by_actor_id ?? "UNKNOWN"} · {value.finalized_at ?? "Date non enregistrée"}</p>
  <p>Inconnus explicites du contexte :</p>{value.unknowns.length ? <ul>{value.unknowns.map((unknown, index) => <li key={index}>{typeof unknown === "string" ? unknown : JSON.stringify(unknown)}</li>)}</ul> : <p>UNKNOWN — liste non renseignée ; consulter les points et leurs sources.</p>}
  {value.state === "REVIEW_REQUIRED" && <p>Sources ou actes remplacés : revue requise. Aucun accord antérieur transféré à la carte courante.</p>}
  {value.conditions.map(condition => <div key={condition.condition_id}><h4>{condition.label} — {condition.status}</h4><p>Responsable : {condition.owner_actor_id ?? "UNKNOWN"}. Échéance : {condition.due_at ?? "UNKNOWN"} · {condition.due_date_absence_reason ?? ""}</p><p>Conséquence : {condition.failure_consequence}</p><p>Preuve de levée : {condition.satisfied_evidence ? JSON.stringify(condition.satisfied_evidence) : "UNKNOWN — aucune levée déduite"}</p></div>)}
  <details><summary>Contexte et actes sources historiques</summary><p>Contexte : {value.context_id ?? "UNKNOWN"} · empreinte : {value.context_fingerprint ?? "UNKNOWN"}</p>{value.assessment_snapshots.map(act => <div key={act.assessment_id}><p>Acte {act.assessment_id} · révision {act.revision} · auteur {act.actor_id} · {act.created_at}</p><p>Hypothèses : {act.treatment?.hypotheses ?? "UNKNOWN"}. Preuve attendue : {act.expected_evidence ?? "UNKNOWN"}. Risque résiduel : {act.residual_risk ?? "UNKNOWN"}.</p>{act.treatment && <AnalysisTreatmentRead value={act.treatment} actorId={act.actor_id} />}<p>Justification : {act.justification}</p><pre className="review-draft-content">{JSON.stringify(act.source, null, 2)}</pre></div>)}<ul>{value.references.map(ref => <li key={`${ref.aggregate_type}:${ref.aggregate_id}`}>{ref.aggregate_type} · {ref.aggregate_id} v{ref.aggregate_revision} · {ref.content_hash ?? "Hash non requis"}</li>)}</ul></details>
  {value.transitions.length > 0 && <details><summary>Historique des conditions</summary>{value.transitions.map(t => <p key={t.transition_id}>{t.from_status} → {t.to_status} · acteur {t.actor_id} · {t.created_at} · preuve : {t.evidence ? JSON.stringify(t.evidence) : "UNKNOWN"} · {t.failure_reason ?? ""}</p>)}</details>}
  {value.truncated && <p>Historique partiel : limites de lecture atteintes.</p>}
 </article>;
}
