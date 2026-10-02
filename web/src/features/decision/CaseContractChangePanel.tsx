import { useEffect, useLayoutEffect, useRef, useState, type FormEvent } from "react";
import type { ApiClient } from "../../infrastructure/api";
import type {
  CaseContractChangeApplicability,
  CaseContractChangeEvent,
  CaseContractChangeKind,
  ContractInstrumentVersion,
  RecordCaseContractChangeActionInput,
  RecordCaseContractChangeApplicabilityInput,
  RecordCaseContractChangeEventInput,
} from "../../shared/types";

type ReadState = "LOADING" | "READY" | "UNAVAILABLE";
type IntentInput =
  | RecordCaseContractChangeEventInput
  | RecordCaseContractChangeApplicabilityInput
  | RecordCaseContractChangeActionInput;
type PendingIntent = { caseId: string; key: string; input: IntentInput };

const CHANGE_KINDS: Array<{ value: CaseContractChangeKind; label: string }> = [
  { value: "ORDER_OF_SERVICE", label: "Ordre de service / instruction" },
  { value: "CHANGE_REQUEST", label: "Demande de changement" },
  { value: "ADDENDUM", label: "Avenant" },
  { value: "SCHEDULE_CHANGE", label: "Changement de calendrier" },
];
const APPLICABILITY_CHOICES: Array<{ value: CaseContractChangeApplicability; label: string }> = [
  { value: "APPLICABLE_TO_HANDOVER", label: "À relier à cette passation" },
  { value: "NOT_APPLICABLE", label: "Non relié à cette passation" },
  { value: "NEEDS_CLARIFICATION", label: "À clarifier" },
];
const ids = () => ({
  command_id: crypto.randomUUID(),
  idempotency_key: crypto.randomUUID(),
  correlation_id: crypto.randomUUID(),
});
const refs = (value: string) => value.split("\n").map((item) => item.trim()).filter(Boolean);

export function CaseContractChangePanel({
  api,
  caseId,
  versions,
}: {
  api: ApiClient;
  caseId: string;
  versions: ContractInstrumentVersion[];
}) {
  const [events, setEvents] = useState<CaseContractChangeEvent[]>([]);
  const [handovers, setHandovers] = useState<Array<{
    snapshot_id: string; lot_reference: string; package_version: number; manifest_sha256: string;
  }>>([]);
  const [state, setState] = useState<ReadState>("LOADING");
  const [pending, setPending] = useState<PendingIntent | null>(null);
  const [submitting, setSubmitting] = useState<string | null>(null);
  const [failure, setFailure] = useState<{ key: string; kind: "UNCONFIRMED" | "REJECTED" } | null>(null);
  const [message, setMessage] = useState("");
  const [handoverId, setHandoverId] = useState("");
  const [changeKind, setChangeKind] = useState<CaseContractChangeKind>("ORDER_OF_SERVICE");
  const [declaredVersionId, setDeclaredVersionId] = useState("");
  const [issuer, setIssuer] = useState("");
  const [summary, setSummary] = useState("");
  const [scopeNote, setScopeNote] = useState("");
  const [sourceRefs, setSourceRefs] = useState("");
  const [evidenceRefs, setEvidenceRefs] = useState("");
  const [receivedAt, setReceivedAt] = useState(() => new Date().toISOString().slice(0, 16));
  const [reviewDrafts, setReviewDrafts] = useState<Record<string, {
    versionId: string; decision: CaseContractChangeApplicability; deltaState: "UNKNOWN" | "DECLARED";
    deltaNote: string; rationale: string; evidenceRefs: string;
  }>>({});
  const [actionDrafts, setActionDrafts] = useState<Record<string, {
    summary: string; evidenceRefs: string; dueAt: string; noDueReason: string;
  }>>({});
  const activeCaseId = useRef(caseId);

  useLayoutEffect(() => {
    activeCaseId.current = caseId;
    return () => { activeCaseId.current = ""; };
  }, [caseId]);

  async function refresh(targetCaseId = caseId) {
    const [eventResult, handoverResult] = await Promise.all([
      api.listCaseContractChangeEvents(targetCaseId),
      api.listCaseHandoverSnapshots(targetCaseId),
    ]);
    if (activeCaseId.current !== targetCaseId
      || eventResult.case_id !== targetCaseId
      || handoverResult.case_id !== targetCaseId) return;
    setEvents(eventResult.events);
    setHandovers(handoverResult.items);
    setState("READY");
  }

  useEffect(() => {
    setEvents([]);
    setHandovers([]);
    setPending(null);
    setSubmitting(null);
    setFailure(null);
    setMessage("");
    setHandoverId("");
    setReviewDrafts({});
    setActionDrafts({});
    let active = true;
    setState("LOADING");
    void refresh(caseId).catch(() => {
      if (active) setState("UNAVAILABLE");
    });
    return () => {
      active = false;
      activeCaseId.current = "";
    };
    // Both reads are keyed to the active, confirmed Case.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [api, caseId]);

  async function submit<T extends IntentInput>(
    key: string,
    create: () => T,
    send: (input: T) => Promise<unknown>,
  ) {
    if (pending && (pending.caseId !== caseId || pending.key !== key)) return;
    const existing = pending?.caseId === caseId && pending.key === key ? pending.input as T : null;
    const input = existing ?? create();
    if (!existing) setPending({ caseId, key, input });
    setSubmitting(key);
    setFailure(null);
    setMessage("");
    try {
      await send(input);
      if (activeCaseId.current !== caseId) return;
      await refresh();
      setPending(null);
      setMessage("Act Patron enregistré et relu depuis le serveur.");
    } catch (error) {
      if (activeCaseId.current !== caseId) return;
      const status = (error as { status?: number })?.status;
      if (status !== undefined && status >= 400 && status < 500) {
        setPending(null);
        setFailure({ key, kind: "REJECTED" });
      } else {
        setFailure({ key, kind: "UNCONFIRMED" });
      }
    } finally {
      if (activeCaseId.current === caseId) setSubmitting(null);
    }
  }

  function recordEvent(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!handoverId || !summary.trim() || !scopeNote.trim() || !receivedAt) return;
    const sourceRefsList = refs(sourceRefs);
    const evidenceRefsList = refs(evidenceRefs);
    if (!sourceRefsList.length || !evidenceRefsList.length) return;
    void submit(
      "event",
      () => ({
        ...ids(),
        event_id: crypto.randomUUID(),
        handover_snapshot_id: handoverId,
        change_kind: changeKind,
        contract_instrument_version_id: declaredVersionId || null,
        issuer: issuer.trim() || null,
        summary: summary.trim(),
        scope_note: scopeNote.trim(),
        source_refs: sourceRefsList,
        evidence_refs: evidenceRefsList,
        declared_received_at: new Date(receivedAt).toISOString(),
      }),
      (input) => api.recordCaseContractChangeEvent(caseId, input),
    );
  }

  function recordApplicability(event: CaseContractChangeEvent) {
    const draft = reviewDrafts[event.event_id];
    const versionId = event.declared_instrument?.contract_instrument_version_id ?? draft?.versionId;
    if (!versionId || !draft?.rationale.trim() || !refs(draft.evidenceRefs).length
      || (draft.deltaState === "DECLARED" && !draft.deltaNote.trim())) return;
    void submit(
      "review:" + event.event_id,
      () => ({
        ...ids(),
        review_id: crypto.randomUUID(),
        handover_snapshot_id: event.handover_snapshot_id,
        contract_instrument_version_id: versionId,
        expected_revision: event.applicability_history.length,
        decision: draft.decision,
        delta_state: draft.deltaState,
        delta_note: draft.deltaState === "DECLARED" ? draft.deltaNote.trim() : null,
        rationale: draft.rationale.trim(),
        evidence_refs: refs(draft.evidenceRefs),
      }),
      (input) => api.recordCaseContractChangeApplicability(caseId, event.event_id, input),
    );
  }

  function recordAction(event: CaseContractChangeEvent) {
    const draft = actionDrafts[event.event_id];
    const latestReview = event.applicability_history.at(-1);
    if (!latestReview || latestReview.decision !== "APPLICABLE_TO_HANDOVER"
      || !draft?.summary.trim() || !refs(draft.evidenceRefs).length
      || (!draft.dueAt && !draft.noDueReason.trim())) return;
    void submit(
      "action:" + event.event_id,
      () => ({
        ...ids(),
        action_id: crypto.randomUUID(),
        applicability_review_id: latestReview.review_id,
        expected_revision: event.actions.length,
        action_summary: draft.summary.trim(),
        evidence_refs: refs(draft.evidenceRefs),
        due_at: draft.dueAt ? new Date(draft.dueAt).toISOString() : null,
        due_date_absence_reason: draft.dueAt ? null : draft.noDueReason.trim(),
      }),
      (input) => api.recordCaseContractChangeAction(caseId, event.event_id, input),
    );
  }

  const blocked = !!pending;
  return (
    <section className="section-block decision-section" aria-label="Événements contractuels C1">
      <div className="section-heading"><div><span className="section-kicker">VERTICALE C · C1</span><h2>Changement contractuel lié à la passation</h2></div></div>
      <p>Événement, version, applicabilité humaine, action et preuve restent des actes séparés. Aucun delta de coût/délai/cash ni effet juridique n’est calculé automatiquement.</p>
      {state === "LOADING" && <p role="status">Lecture des événements contractuels…</p>}
      {state === "UNAVAILABLE" && <p role="status">UNAVAILABLE · aucune projection confirmée n’est affichée.</p>}
      {state === "READY" && events.length === 0 && <p>UNKNOWN · aucun événement contractuel n’est relié à une passation B1.</p>}
      {events.map((event) => {
        const review = reviewDrafts[event.event_id] ?? {
          versionId: "",
          decision: "NEEDS_CLARIFICATION" as const,
          deltaState: "UNKNOWN" as const,
          deltaNote: "",
          rationale: "",
          evidenceRefs: "",
        };
        const action = actionDrafts[event.event_id] ?? {
          summary: "",
          evidenceRefs: "",
          dueAt: "",
          noDueReason: "",
        };
        const latestReview = event.applicability_history.at(-1);
        return <article className="detail-panel" key={event.event_id}>
          <h3>{CHANGE_KINDS.find((kind) => kind.value === event.change_kind)?.label ?? event.change_kind} · lot {event.lot_reference}</h3>
          <p>Passation B1 : paquet P5 v{event.offer_package_version} · SHA-256 {event.offer_manifest_sha256}</p>
          <p>Événement reçu : {event.declared_received_at} · source : {event.source_refs.join(" · ")}</p>
          <p>Émetteur déclaré : {event.issuer ?? "UNKNOWN"} · preuves : {event.evidence_refs.join(" · ")}</p>
          <p>{event.summary} · périmètre déclaré : {event.scope_note}</p>
          <p>Version contrat déclarée : {event.declared_instrument
            ? event.declared_instrument.instrument_kind + " · " + event.declared_instrument.version_reference
            : "UNKNOWN · aucun lien versionnel déclaré"}.</p>
          <p>Applicabilité à cette passation : {event.applicability_state}. Ce statut ne constitue pas une conclusion juridique.</p>
          {event.applicability_history.map((item) => <p key={item.review_id}>
            Revue Patron r{item.revision} : {item.decision} · version déclarée {item.contract_instrument?.version_reference ?? item.contract_instrument_version_id} · delta {item.delta_state}{item.delta_note ? " · " + item.delta_note : ""} · {item.rationale} · preuves : {item.evidence_refs.join(" · ")}
          </p>)}
          {event.applicability_state !== "APPLICABLE_TO_HANDOVER" && <form onSubmit={(formEvent) => { formEvent.preventDefault(); recordApplicability(event); }}>
            <label>{event.applicability_history.length ? "Réviser le lien humain vers la version contrat" : "Version contrat retenue par le Patron"}
              <select required aria-label={"Version contrat retenue " + event.event_id} value={review.versionId} disabled={blocked || !!event.declared_instrument} onChange={(formEvent) => setReviewDrafts((current) => ({ ...current, [event.event_id]: { ...review, versionId: formEvent.target.value } }))}>
                <option value="">Choisir une version déclarée, ou conserver UNKNOWN</option>
                {versions.map((version) => <option key={version.contract_instrument_version_id} value={version.contract_instrument_version_id}>{version.instrument_kind} · {version.version_reference}</option>)}
              </select>
            </label>
            <label>Décision humaine sur le lien
              <select aria-label={"Décision d’applicabilité " + event.event_id} value={review.decision} disabled={blocked} onChange={(formEvent) => setReviewDrafts((current) => ({ ...current, [event.event_id]: { ...review, decision: formEvent.target.value as CaseContractChangeApplicability } }))}>
                {APPLICABILITY_CHOICES.map((choice) => <option key={choice.value} value={choice.value}>{choice.label}</option>)}
              </select>
            </label>
            <label>État du delta déclaré
              <select aria-label={"État du delta " + event.event_id} value={review.deltaState} disabled={blocked} onChange={(formEvent) => setReviewDrafts((current) => ({ ...current, [event.event_id]: { ...review, deltaState: formEvent.target.value as "UNKNOWN" | "DECLARED" } }))}>
                <option value="UNKNOWN">UNKNOWN · aucun delta évalué</option>
                <option value="DECLARED">Delta déclaré par le Patron</option>
              </select>
            </label>
            {review.deltaState === "DECLARED" && <label>Delta résumé déclaré (aucun calcul automatique)<textarea required maxLength={2000} value={review.deltaNote} disabled={blocked} onChange={(formEvent) => setReviewDrafts((current) => ({ ...current, [event.event_id]: { ...review, deltaNote: formEvent.target.value } }))} /></label>}
            <label>Justification de revue<textarea required maxLength={2000} value={review.rationale} disabled={blocked} onChange={(formEvent) => setReviewDrafts((current) => ({ ...current, [event.event_id]: { ...review, rationale: formEvent.target.value } }))} /></label>
            <label>Sources/preuves de la décision, une par ligne<textarea required value={review.evidenceRefs} disabled={blocked} onChange={(formEvent) => setReviewDrafts((current) => ({ ...current, [event.event_id]: { ...review, evidenceRefs: formEvent.target.value } }))} /></label>
            <button type="submit" disabled={blocked || !versions.length}>{submitting === "review:" + event.event_id ? "Enregistrement…" : failure?.key === "review:" + event.event_id && failure.kind === "UNCONFIRMED" ? "Réessayer la même revue" : "Enregistrer la revue Patron"}</button>
          </form>}
          {event.applicability_state === "APPLICABLE_TO_HANDOVER" && latestReview && <form onSubmit={(formEvent) => { formEvent.preventDefault(); recordAction(event); }}>
            <h4>Action et preuve Patron</h4>
            <label>Action déclarée<textarea required maxLength={2000} value={action.summary} disabled={blocked} onChange={(formEvent) => setActionDrafts((current) => ({ ...current, [event.event_id]: { ...action, summary: formEvent.target.value } }))} /></label>
            <label>Sources/preuves liées à l’action, une par ligne<textarea required value={action.evidenceRefs} disabled={blocked} onChange={(formEvent) => setActionDrafts((current) => ({ ...current, [event.event_id]: { ...action, evidenceRefs: formEvent.target.value } }))} /></label>
            <label>Date d’action déclarée (facultative, non calculée)<input type="datetime-local" value={action.dueAt} disabled={blocked} onChange={(formEvent) => setActionDrafts((current) => ({ ...current, [event.event_id]: { ...action, dueAt: formEvent.target.value } }))} /></label>
            {!action.dueAt && <label>Motif d’échéance inconnue<input required value={action.noDueReason} disabled={blocked} onChange={(formEvent) => setActionDrafts((current) => ({ ...current, [event.event_id]: { ...action, noDueReason: formEvent.target.value } }))} /></label>}
            <button type="submit" disabled={blocked}>{submitting === "action:" + event.event_id ? "Enregistrement…" : failure?.key === "action:" + event.event_id && failure.kind === "UNCONFIRMED" ? "Réessayer la même action" : "Enregistrer l’action et la preuve"}</button>
          </form>}
          {event.actions.map((item) => <p key={item.action_id}>Action r{item.revision} · {item.state} · {item.summary} · preuves : {item.evidence_refs.join(" · ")} · échéance : {item.due_at ?? item.due_date_absence_reason}</p>)}
        </article>;
      })}
      {message && <p role="status">{message}</p>}
      {failure && <p role="alert">{failure.kind === "UNCONFIRMED" ? "Résultat non confirmé · le rejeu conserve les mêmes identifiants." : "Refus confirmé par le serveur ; aucune nouvelle révision n’a été créée."}</p>}
      {state === "READY" && <form aria-label="Enregistrer un événement contractuel sourcé" onSubmit={recordEvent}>
        <h3>Enregistrer un événement contractuel</h3>
        <label>Passation P7 de départ
          <select required aria-label="Passation de départ" value={handoverId} disabled={blocked} onChange={(formEvent) => setHandoverId(formEvent.target.value)}>
            <option value="">Choisir la passation gagnée</option>
            {handovers.map((handover) => <option key={handover.snapshot_id} value={handover.snapshot_id}>Lot {handover.lot_reference} · P5 v{handover.package_version} · {handover.manifest_sha256.slice(0, 12)}</option>)}
          </select>
        </label>
        <label>Type d’événement
          <select aria-label="Type d’événement contractuel" value={changeKind} disabled={blocked} onChange={(formEvent) => setChangeKind(formEvent.target.value as CaseContractChangeKind)}>
            {CHANGE_KINDS.map((kind) => <option key={kind.value} value={kind.value}>{kind.label}</option>)}
          </select>
        </label>
        <label>Version contractuelle déclarée (facultatif)
          <select aria-label="Version contractuelle déclarée" value={declaredVersionId} disabled={blocked} onChange={(formEvent) => setDeclaredVersionId(formEvent.target.value)}>
            <option value="">UNKNOWN · version non établie</option>
            {versions.map((version) => <option key={version.contract_instrument_version_id} value={version.contract_instrument_version_id}>{version.instrument_kind} · {version.version_reference}</option>)}
          </select>
        </label>
        <label>Émetteur déclaré<input maxLength={240} value={issuer} disabled={blocked} onChange={(formEvent) => setIssuer(formEvent.target.value)} /></label>
        <label>Résumé déclaré<input required maxLength={2000} value={summary} disabled={blocked} onChange={(formEvent) => setSummary(formEvent.target.value)} /></label>
        <label>Périmètre/delta décrit, sans calcul automatique<textarea required maxLength={2000} value={scopeNote} disabled={blocked} onChange={(formEvent) => setScopeNote(formEvent.target.value)} /></label>
        <label>Références source, une par ligne<textarea required value={sourceRefs} disabled={blocked} onChange={(formEvent) => setSourceRefs(formEvent.target.value)} /></label>
        <label>Preuves de réception/événement, une par ligne<textarea required value={evidenceRefs} disabled={blocked} onChange={(formEvent) => setEvidenceRefs(formEvent.target.value)} /></label>
        <label>Date/heure de réception déclarée<input required type="datetime-local" value={receivedAt} disabled={blocked} onChange={(formEvent) => setReceivedAt(formEvent.target.value)} /></label>
        <button type="submit" disabled={blocked || !handovers.length}>{submitting === "event" ? "Enregistrement…" : failure?.key === "event" && failure.kind === "UNCONFIRMED" ? "Réessayer le même événement" : "Enregistrer l’événement sourcé"}</button>
      </form>}
    </section>
  );
}
