import { formatMinorMoney } from "../../shared/financialFormatting";
import type { AnalysisCashReport, AnalysisPricingScenario } from "../../shared/types";

export function AnalysisCash({ reports, scenarios, caseId, current }: {reports: AnalysisCashReport[]; scenarios: AnalysisPricingScenario[]; caseId: string; current: boolean}) {
  return <div aria-label="Trésorerie et garanties enregistrées">
    <p>Échéancier de ces rapports : UNKNOWN · Pic de financement : UNKNOWN · Date et durée du pic : UNKNOWN · Portée DCE/lot : UNKNOWN.</p>
    <p>Les déclarations et réserves ci-dessous ne constituent pas une courbe de trésorerie ni un GO économique. Les scénarios restent distincts; leurs réserves ne sont pas additionnées.</p>
    {reports.length === 0 && <p>Aucune déclaration de trésorerie publiée : UNKNOWN.</p>}
    <p>Consultez « Trésorerie déclarée de l’Affaire » pour les flux datés et leurs cumuls. Les rapports ci-dessous gardent leur portée déclarée.</p>
    <ul>{reports.map(report => {
      const d = report.details;
      const qualified = current && report.state === "DECLARED" && d?.case_id === caseId &&
        d.lines.length > 0 && Number.isSafeInteger(d.forecast_cashflow_minor) &&
        d.lines.every(line=>Number.isSafeInteger(line.amount_minor)) &&
        d.lines.reduce((sum,line)=>sum+BigInt(line.amount_minor),0n)===BigInt(d.forecast_cashflow_minor);
      return <li key={report.report_id}>
        <p>Rapport publié {report.report_id} · Révision {report.revision}</p>
        {qualified && d ? <>
          <p>Solde prévisionnel déclaré : {formatMinorMoney(d.forecast_cashflow_minor,d.currency_code)}</p>
          <details><summary>Déclarations et provenance de trésorerie</summary>
            <p>Date de calcul enregistrée : {d.calculated_at} · Règles de calcul : {d.ruleset_version} · Devise : {d.currency_code}. Hypothèses de calendrier et empreinte documentaire : UNKNOWN.</p>
            <ul>{d.lines.map(line=><li key={line.line_id}>{line.label} : {formatMinorMoney(line.amount_minor,d.currency_code)} · Ligne {line.line_id}</li>)}</ul>
          </details>
        </> : <p>Déclaration de trésorerie : UNKNOWN. Rapport, lignes ou contexte à revalider.</p>}
      </li>;
    })}</ul>
    <h3>Réserves des scénarios enregistrés</h3>
    {scenarios.length === 0 && <p>Aucune réserve de scénario qualifiée : UNKNOWN.</p>}
    <ul>{scenarios.map(item=>{
      const d=item.details;
      const qualified=current&&item.state==="RECORDED"&&d?.case_id===caseId&&d.scenario_id===item.scenario_id&&
        d.version===item.revision&&d.state!=="ARCHIVED"&&d.source_basis_state==="DECLARED_COMPLETE"&&d.source_snapshot_id&&d.currency_code;
      return <li key={item.scenario_id}>
        <p>Scénario {item.scenario_id} · Révision {item.revision}</p>
        {qualified&&d?<>
          <strong>{d.scenario_key}</strong>
          <p>Réserve de retenue : {d.retention_reserve_minor===undefined?"UNKNOWN":formatMinorMoney(d.retention_reserve_minor,d.currency_code!)} · Réserve de garantie : {d.guarantee_reserve_minor===undefined?"UNKNOWN":formatMinorMoney(d.guarantee_reserve_minor,d.currency_code!)} · Réserve de pénalités : {d.penalty_reserve_minor===undefined?"UNKNOWN":formatMinorMoney(d.penalty_reserve_minor,d.currency_code!)}</p>
          <details><summary>Hypothèses et source des réserves</summary>
            <p>Snapshot {d.source_snapshot_id} · Révision source {d.source_snapshot_revision}. Calendrier de paiement/libération et portée : UNKNOWN.</p>
            <ul>{Object.entries(d.assumptions).map(([key,value])=><li key={key}>{key} : {JSON.stringify(value)}</li>)}</ul>
            {Object.keys(d.assumptions).length===0&&<p>Hypothèses non renseignées : UNKNOWN.</p>}
          </details>
        </>:<p>Réserves : UNKNOWN. Scénario, source ou contexte à revalider.</p>}
      </li>;
    })}</ul>
  </div>;
}
