import { formatBasisPoints, formatMinorMoney } from "../../shared/financialFormatting";
import type { AnalysisPricingScenario } from "../../shared/types";

export function AnalysisPricing({ scenarios, caseId, current }: { scenarios: AnalysisPricingScenario[]; caseId: string; current: boolean }) {
  if (!scenarios.length) return <p>Aucun scénario économique qualifié : UNKNOWN.</p>;
  return <div aria-label="Scénarios économiques enregistrés">
    <p>Lecture privée des catégories déclarées. Applicabilité au DCE et au lot : UNKNOWN. Cette lecture ne vaut pas GO économique.</p>
    <ul>{scenarios.map(item => {
      const d = item.details;
      const qualified = current && item.state === "RECORDED" && d?.case_id === caseId &&
        d.scenario_id === item.scenario_id && d.version === item.revision && d.state !== "ARCHIVED" &&
        d.source_basis_state === "DECLARED_COMPLETE" && d.source_snapshot_id && d.currency_code;
      return <li key={item.scenario_id}>
        <p>Scénario {item.scenario_id} · Révision {item.revision}</p>
        {qualified && d ? <>
          <strong>{d.scenario_key}</strong>
          <p>{d.state === "SELECTED" ? "Sélectionné — état enregistré" : "Brouillon"} · {d.scenario_type}</p>
          <dl>
            <dt>Vente</dt><dd>{formatMinorMoney(d.sales_total_minor, d.currency_code!)}</dd>
            <dt>Coût total</dt><dd>{formatMinorMoney(d.total_cost_minor, d.currency_code!)}</dd>
            <dt>Marge brute</dt><dd>{formatMinorMoney(d.gross_margin_minor, d.currency_code!)} · {formatBasisPoints(d.gross_margin_rate_bps)} %</dd>
          </dl>
          <details><summary>Hypothèses et provenance financières</summary>
            <p>Snapshot {d.source_snapshot_id} · Révision source {d.source_snapshot_revision} · Devise {d.currency_code}. Empreinte documentaire et portée lot : UNKNOWN.</p>
            <p>Réserve pénalités : {d.penalty_reserve_minor === undefined ? "UNKNOWN" : formatMinorMoney(d.penalty_reserve_minor,d.currency_code!)} · Retenue : {d.retention_reserve_minor === undefined ? "UNKNOWN" : formatMinorMoney(d.retention_reserve_minor,d.currency_code!)} · Garantie : {d.guarantee_reserve_minor === undefined ? "UNKNOWN" : formatMinorMoney(d.guarantee_reserve_minor,d.currency_code!)}</p>
            <p>Seuil plancher : {d.floor_margin_rate_bps === undefined ? "UNKNOWN" : formatBasisPoints(d.floor_margin_rate_bps)+" %"} · Cible : {d.target_margin_rate_bps === undefined ? "UNKNOWN" : formatBasisPoints(d.target_margin_rate_bps)+" %"}</p>
            <ul aria-label="Hypothèses enregistrées">{Object.entries(d.assumptions).map(([key,value])=><li key={key}>{key} : {JSON.stringify(value)}</li>)}</ul>
            {Object.keys(d.assumptions).length===0&&<p>Hypothèses non renseignées : UNKNOWN.</p>}
          </details>
        </> : <p>Valeurs économiques : UNKNOWN. Source, scénario ou contexte à revalider.</p>}
      </li>;
    })}</ul>
  </div>;
}
