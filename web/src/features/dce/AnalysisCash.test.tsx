import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AnalysisCash } from "./AnalysisCash";
import type { AnalysisCashReport } from "../../shared/types";

export function cashFixture():AnalysisCashReport {
 return {report_id:"cash-report-a",revision:2,state:"DECLARED",unknown_reason:null,schedule_state:"UNKNOWN",funding_peak_state:"UNKNOWN",scope_state:"UNKNOWN",details:{case_id:"case-a",currency_code:"EUR",calculated_at:"2026-10-20T12:00:00Z",ruleset_version:1,forecast_cashflow_minor:0,lines:[{line_id:"line-a",label:"Déclaration de solde synthétique",amount_minor:0}]}};
}
describe("AnalysisCash",()=>{
 it("reads an explicitly declared zero with exact line and source while peak remains UNKNOWN",()=>{
  render(<AnalysisCash reports={[cashFixture()]} scenarios={[]} caseId="case-a" current/>);
  expect(screen.getByText(/Solde prévisionnel déclaré : 0,00/)).toBeInTheDocument();
  expect(screen.getByText(/Ligne line-a/)).toBeInTheDocument();
  expect(screen.getByText(/Pic de financement : UNKNOWN/)).toBeInTheDocument();
  expect(screen.getByText(/Rapport publié cash-report-a · Révision 2/)).toBeInTheDocument();
 });
 it.each(["stale","foreign","missing","discordant","unsafe","unknown"])("masks declaration details for %s",mode=>{
  const item=cashFixture();if(mode==="foreign")item.details!.case_id="other";if(mode==="missing")item.details!.lines=[];if(mode==="discordant")item.details!.forecast_cashflow_minor=1;if(mode==="unsafe")item.details!.forecast_cashflow_minor=Number.MAX_SAFE_INTEGER+1;if(mode==="unknown")item.state="UNKNOWN";
  render(<AnalysisCash reports={[item]} scenarios={[]} caseId="case-a" current={mode!=="stale"}/>);
  expect(screen.queryByText(/Solde prévisionnel déclaré/)).not.toBeInTheDocument();
  expect(screen.queryByText(/Ligne line-a/)).not.toBeInTheDocument();
  expect(screen.getByText(/Déclaration de trésorerie : UNKNOWN/)).toBeInTheDocument();
 });
});

it.each([true,false])("keeps each scenario reserve and its assumptions separate, current=%s",current=>{
 const scenario={scenario_id:"reserve-a",revision:3,state:"RECORDED" as const,unknown_reason:null,dce_applicability:"UNKNOWN" as const,details:{scenario_id:"reserve-a",case_id:"case-a",scenario_key:"Prudent réserve",scenario_type:"PRUDENT",version:3,state:"SELECTED" as const,assumptions:{condition:"ne pas présumer la libération"},sales_total_minor:100,total_cost_minor:80,gross_margin_minor:20,gross_margin_rate_bps:2000,source_snapshot_id:"source-a",source_snapshot_revision:2,source_basis_state:"DECLARED_COMPLETE" as const,currency_code:"EUR",retention_reserve_minor:0,guarantee_reserve_minor:3000,penalty_reserve_minor:1000}};
 render(<AnalysisCash reports={[]} scenarios={[scenario]} caseId="case-a" current={current}/>);
 if(current){expect(screen.getByText(/Réserve de retenue : 0,00/)).toBeInTheDocument();expect(screen.getByText(/ne pas présumer la libération/)).toBeInTheDocument();expect(screen.getByText(/Snapshot source-a · Révision source 2/)).toBeInTheDocument();}
 else{expect(screen.queryByText("Prudent réserve")).not.toBeInTheDocument();expect(screen.queryByText(/ne pas présumer/)).not.toBeInTheDocument();expect(screen.getByText(/Réserves : UNKNOWN/)).toBeInTheDocument();}
});
