import type { ContractQueryExportAudit } from "../../shared/types";

export function ContractQueryExportAuditPanel({ audit }: { audit: ContractQueryExportAudit | null }) {
  if (!audit) return <div className="empty-card"><strong>Aucun audit d’export</strong><p>Aucune demande d’export locale sélectionnée.</p></div>;
  return <article className="detail-panel" aria-label="Audit export local"><div className="panel-heading"><h3>Export local</h3><span className="state-badge">{audit.export.status}</span></div><p>Filtres : {JSON.stringify(audit.export.filters)}</p><ol>{audit.transitions.map((transition) => <li key={transition.transition_id}>{transition.from_status} → {transition.to_status}{transition.local_proof_ref ? ` · ${transition.local_proof_ref}` : ""}</li>)}</ol><p className="panel-empty">Lecture seule : aucune réception externe présumée.</p></article>;
}
