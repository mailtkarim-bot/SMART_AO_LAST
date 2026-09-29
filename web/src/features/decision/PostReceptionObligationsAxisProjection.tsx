import type { PostReceptionObligation } from "../../shared/types";

export function PostReceptionObligationsAxisProjection({
  obligations,
  loading = false,
}: {
  obligations: PostReceptionObligation[];
  loading?: boolean;
}) {
  return <div className="detail-panel" aria-label="Carte d’Engagement axe 11 obligations post-réception">
    <div className="panel-heading"><div><h3>Carte d’Engagement · Axe 11</h3><p>Obligations d’exécution après réception</p></div><span className="state-badge">PARTIAL</span></div>
    <p>Projection sourcée des obligations enregistrées. Elle ne prouve pas que la liste est complète et ne calcule aucun coût.</p>
    {loading ? <p role="status">Chargement des obligations sourcées…</p> : obligations.length === 0
      ? <p className="panel-empty">Aucune obligation enregistrée ; cela n’établit pas l’absence d’obligation.</p>
      : <ul aria-label="Obligations projetées dans la Carte d’Engagement">{obligations.map((obligation) => <li key={`${obligation.case_id}:${obligation.obligation_id}`}>
        <strong>{obligation.obligation_type} · {obligation.summary}</strong>
        <span>État : {obligation.status} · Échéance : {obligation.due_date ?? "UNKNOWN"} · Coût : {obligation.cost_estimate_note ?? "UNKNOWN"}</span>
        <span>Sources : {obligation.source_refs.join(" · ")}</span>
      </li>)}</ul>}
  </div>;
}
