import type { ContractExecutionEvidenceTimelineEvent } from "../../shared/types";
import type { ContractExecutionEvidenceReadStatus } from "../pricing/useContractExecutionEvidence";

function instrumentLabel(kind: "SIGNED_CONTRACT" | "AMENDMENT", reference: string): string {
  return `${kind === "SIGNED_CONTRACT" ? "Contrat signé" : "Avenant"} · ${reference}`;
}

function decisionLabel(status: Extract<ContractExecutionEvidenceTimelineEvent, { event_type: "EVIDENCE_REQUALIFICATION" }> ["status"]): string {
  switch (status) {
    case "RETAINED_AS_DECLARED": return "RETAINED_AS_DECLARED · rattachement conservé tel que déclaré";
    case "RELINKED_TO_DECLARED_VERSION": return "RELINKED_TO_DECLARED_VERSION · nouveau rattachement déclaré";
    case "NEEDS_CLARIFICATION": return "NEEDS_CLARIFICATION · précisions requises";
  }
}

function TimelineEvent({ event }: { event: ContractExecutionEvidenceTimelineEvent }) {
  if (event.event_type === "EXECUTION_EVIDENCE") {
    return <li>
      <strong>ACTE INITIAL · {event.act.summary}</strong>
      {event.act.act_kind === "WORK_RECEPTION" && <span>Réception déclarée : {event.act.reception_outcome}</span>}
      <span>Enregistré par {event.actor_id} le {event.recorded_at} · révision {event.revision} · état {event.status}</span>
      <span>Version DCE au moment de l’acte : {event.act.case_dce_version_id_at_recording ?? "UNKNOWN"} · relation actuelle {event.act.current_dce_relation}</span>
      <span>Version contrat/avenant liée à l’acte : {event.act.contract_instrument_version
        ? `${instrumentLabel(event.act.contract_instrument_version.instrument_kind, event.act.contract_instrument_version.version_reference)} · relation actuelle ${event.act.current_instrument_relation}`
        : `UNKNOWN · relation actuelle ${event.act.current_instrument_relation}`}</span>
      <span>Sources de l’acte : {event.act.source_refs.join(" · ")}</span>
      <span>Preuves de l’acte : {event.act.evidence_refs.join(" · ")}</span>
    </li>;
  }

  if (event.event_type === "INSTRUMENT_SUPERSESSION") {
    return <li>
      <strong>SUPERSEDED · déclaration Patron, non vérifiée</strong>
      <span>Le Patron déclare que {instrumentLabel(event.replacing.instrument_kind, event.replacing.version_reference)} remplace {instrumentLabel(event.replaced.instrument_kind, event.replaced.version_reference)}.</span>
      <span>Déclaré par {event.actor_id} le {event.recorded_at} · révision {event.revision}</span>
      <span>Sources de la version remplaçante : {event.replacing.source_refs.join(" · ")}</span>
      <span>Pièces de la version remplaçante : {event.replacing.evidence_refs.join(" · ")}</span>
      <span>Sources de la version remplacée : {event.replaced.source_refs.join(" · ")}</span>
      <span>Pièces de la version remplacée : {event.replaced.evidence_refs.join(" · ")}</span>
      <span>Justification : {event.rationale} · cette déclaration ne qualifie pas l’applicabilité juridique.</span>
    </li>;
  }

  return <li>
    <strong>{decisionLabel(event.status)}</strong>
    <span>Acte d’origine : {event.act_summary} · {event.act_kind} · acte {event.act_id}</span>
    <span>Déclaration examinée : {event.supersession_id} · révision de revue {event.revision} · par {event.actor_id} le {event.recorded_at}</span>
    <span>Version déclarée après revue : {event.resulting_version_reference ?? "UNKNOWN"}</span>
    <span>Sources de l’acte d’origine : {event.act_source_refs.join(" · ")}</span>
    <span>Preuves de l’acte d’origine : {event.act_evidence_refs.join(" · ")}</span>
    <span>Justification : {event.rationale} · applicabilité juridique non évaluée.</span>
  </li>;
}

export function ContractExecutionEvidenceTimeline({
  events,
  status,
}: {
  events: ContractExecutionEvidenceTimelineEvent[];
  status: ContractExecutionEvidenceReadStatus;
}) {
  return <section className="detail-panel" aria-label="Chronologie C07 axe 12">
    <h3>Chronologie · actes, remplacements et requalifications</h3>
    <p>Les événements restent séparés et suivent l’ordre serveur par révision puis date. La chronologie ne conclut pas à l’applicabilité juridique.</p>
    {status === "LOADING" ? <p role="status">Chargement de la chronologie contractuelle…</p>
      : status === "UNAVAILABLE" ? <p>UNAVAILABLE · chronologie indisponible ; les événements ne peuvent pas être réputés absents.</p>
        : events.length === 0 ? <p>UNKNOWN · aucun événement de cette chronologie n’est enregistré.</p>
          : <ol aria-label="Événements de la chronologie contractuelle">{events.map((event) => (
            <TimelineEvent key={`${event.revision}:${event.event_type}:${event.event_id}`} event={event} />
          ))}</ol>}
  </section>;
}
