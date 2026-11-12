import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AnalysisPricing } from "./AnalysisPricing";
import type { AnalysisPricingScenario } from "../../shared/types";

export function pricingFixture(): AnalysisPricingScenario {
 return {scenario_id:"scenario-a",revision:3,state:"RECORDED",unknown_reason:null,dce_applicability:"UNKNOWN",details:{scenario_id:"scenario-a",case_id:"case-a",scenario_key:"Prudent synthétique",scenario_type:"PRUDENT",version:3,state:"SELECTED",assumptions:{origine:"estimation utilisateur",hypothese:"ne pas oublier les pénalités"},sales_total_minor:100000,total_cost_minor:80000,gross_margin_minor:20000,gross_margin_rate_bps:2000,source_snapshot_id:"snapshot-a",source_snapshot_revision:2,source_basis_state:"DECLARED_COMPLETE",source_basis_reason:null,currency_code:"EUR"}};
}
describe("AnalysisPricing",()=>{
 it("reads recorded money, assumptions and source revision without proving applicability",()=>{
  render(<AnalysisPricing scenarios={[pricingFixture()]} caseId="case-a" current/>);
  expect(screen.getByText("Prudent synthétique")).toBeInTheDocument();
  expect(screen.getByText(/origine : "estimation utilisateur"/)).toBeInTheDocument();
  expect(screen.getByText(/Snapshot snapshot-a · Révision source 2/)).toBeInTheDocument();
  expect(screen.getByText(/Applicabilité au DCE et au lot : UNKNOWN/)).toBeInTheDocument();
 });
 it.each(["foreign_case","version","stale","unknown","archived"])("masks all private values for %s",mode=>{
  const item=pricingFixture();if(mode==="foreign_case")item.details!.case_id="other";if(mode==="version")item.details!.version=2;if(mode==="unknown")item.state="UNKNOWN";if(mode==="archived")item.details!.state="ARCHIVED";
  render(<AnalysisPricing scenarios={[item]} caseId="case-a" current={mode!=="stale"}/>);
  expect(screen.queryByText("Prudent synthétique")).not.toBeInTheDocument();
  expect(screen.queryByText(/estimation utilisateur/)).not.toBeInTheDocument();
  expect(screen.getByText(/Valeurs économiques : UNKNOWN/)).toBeInTheDocument();
 });
});
