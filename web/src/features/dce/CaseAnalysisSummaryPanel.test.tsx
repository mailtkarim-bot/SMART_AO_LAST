import {AnalysisAssessmentPendingStore} from "./analysisAssessmentPending";
import type {AnalysisAssessmentInput} from "../../shared/types";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CaseAnalysisSummaryPanel } from "./CaseAnalysisSummaryPanel";
import { analysisFixture } from "./analysisFixture.test-helper";

function panel(props={}) {return render(<CaseAnalysisSummaryPanel allowed caseId="case-a" dceVersionId="version-a" summary={analysisFixture()} loading={false} error={null} onRefresh={vi.fn()} {...props}/>);}

it("shows table headers, conditions and negations with separate cell provenance and no inherited lot",()=>{
 const summary=analysisFixture();
 const anchor={source_anchor_id:"fragment-a",dce_version_id:"version-a",dce_document_id:"doc-a",extraction_id:"extract-a",fragment_ordinal:1,source_sha256:"a".repeat(64),extractor_id:"smart-ao-deterministic",extractor_version:"4",fragment_sha256:"b".repeat(64),locator_state:"RESOLVED" as const,locator:{kind:"docx_table_cell" as const,coordinates:{table:1,row:2,column:2,paragraph:1}}};
 summary.axes[2].items=[{item_id:"point-a",kind:"REQUIREMENT",native_type:"TECHNICAL_PRESCRIPTION",native_state:"PENDING_HUMAN_CONFIRMATION",title:null,source_state:"CURRENT_SOURCE",source_anchor:anchor,start_byte_offset:0,end_byte_offset:4,lot_numbers:[],lot_state:"UNKNOWN",applicability:"UNKNOWN",responsible:null,action:null,consequences:"UNKNOWN",table_context:{state:"EXACT_SOURCE",applicability:"UNKNOWN",unknown_reason:null,cells:["Lot 2","Si le support est accepté","Ne pas intervenir sans consignation"].map((text,index)=>({text,source_anchor:{...anchor,source_anchor_id:`cell-${index}`,locator:{kind:"docx_table_cell",coordinates:{table:1,row:index+1,column:1,paragraph:1}}}}))}}];
 const {rerender}=panel({summary});
 expect(screen.getByText("Lot 2")).toBeInTheDocument();
 expect(screen.getByText("Si le support est accepté")).toBeInTheDocument();
 expect(screen.getByText("Ne pas intervenir sans consignation")).toBeInTheDocument();
 expect(screen.getByText(/Aucune portée ni condition héritée/)).toBeInTheDocument();
 expect(screen.getAllByText(/Références de la source · tableau 1/)).toHaveLength(4);
 rerender(<CaseAnalysisSummaryPanel allowed={false} caseId="case-a" dceVersionId="version-a" summary={summary} loading={false} error={null} onRefresh={vi.fn()}/>);
 expect(screen.queryByText("Ne pas intervenir sans consignation")).not.toBeInTheDocument();
});
describe("CaseAnalysisSummaryPanel",()=>{
 it("shows twelve axes without calling them complete",()=>{panel();expect(screen.getAllByText("Non évalué")).toHaveLength(12);expect(screen.getByText(/ne vaut pas analyse complète/i)).toBeInTheDocument();});
 it("never renders a patron summary for an unauthorized role",()=>{const {container}=panel({allowed:false});expect(container).toBeEmptyDOMElement();});
 it("does not show another case or version",()=>{panel({caseId:"case-b"});expect(screen.queryByRole("table")).not.toBeInTheDocument();});
 it("exposes a read-only refresh and a clear error state",()=>{const refresh=vi.fn();panel({summary:null,error:"Sources à revalider.",onRefresh:refresh});fireEvent.click(screen.getByRole("button",{name:/charger la synthèse/i}));expect(refresh).toHaveBeenCalledOnce();expect(screen.getByRole("alert")).toHaveTextContent("Sources à revalider.");});
 it("does not infer coverage from an empty inventory",()=>{panel({summary:{...analysisFixture(),truncated:true}});expect(screen.getByText(/vue limitée/i)).toBeInTheDocument();});
});

it("makes the scrolling table keyboard reachable",()=>{panel();expect(screen.getByRole("region",{name:"Axes métier — tableau défilant"})).toHaveAttribute("tabindex","0");});

it("shows recorded follow ups, explicit owner and declared consequences",()=>{
 const summary=analysisFixture();
 summary.axes[4].items=[{item_id:"risk-a",kind:"RISK",native_type:"CCAP",native_state:"OPEN",title:null,source_state:"CURRENT_SOURCE",source_anchor:null,start_byte_offset:0,end_byte_offset:3,lot_numbers:[],lot_state:"UNKNOWN",applicability:"UNKNOWN",responsible:null,action:null,consequences:"UNKNOWN",follow_up_state:"RECORDED",follow_ups:[{kind:"CONDITION",record_id:"condition-a",revision:2,state:"OPEN",relation_id:"evidence-a",risk_id:null,requirement_id:"requirement-a",description:"Confirmer accès",consequence:"Réexamen du délai",responsible_actor_id:"assigned-owner",due_at:null,scope:"EXACT_RECORDED_RELATION"}]}];
 panel({summary});
 expect(screen.getByText("Confirmer accès")).toBeInTheDocument();
 expect(screen.getByText(/Réexamen du délai/)).toBeInTheDocument();
 expect(screen.getByText(/assigned-owner/)).toBeInTheDocument();
 expect(screen.getByText(/conséquence déclarée/i)).toBeInTheDocument();
});

it("keeps distinct native risk-requirement relations as distinct rendered entries",()=>{
 const error=vi.spyOn(console,"error").mockImplementation(()=>{});
 try {
  const summary=analysisFixture();
  const base={kind:"CONTRACT_IMPACT" as const,record_id:"same-impact",revision:1,state:"HUMAN_REVIEW_REQUIRED",relation_id:null,risk_id:"risk-a",requirement_id:"req-a",description:"Conséquence rattachée",consequence:null,responsible_actor_id:null,due_at:null,scope:"EXACT_RECORDED_RELATION" as const};
  summary.axes[4].items=[{item_id:"risk-a",kind:"RISK",native_type:"CCAP",native_state:"OPEN",title:null,source_state:"CURRENT_SOURCE",source_anchor:null,start_byte_offset:0,end_byte_offset:3,lot_numbers:[],lot_state:"UNKNOWN",applicability:"UNKNOWN",responsible:null,action:null,consequences:"UNKNOWN",follow_up_state:"RECORDED",follow_ups:[{...base,risk_requirement_link_id:"link-impacts"},{...base,risk_requirement_link_id:"link-constrains"}]}];
  panel({summary});expect(screen.getAllByText("Conséquence rattachée")).toHaveLength(2);
  expect(error).not.toHaveBeenCalled();
 } finally {error.mockRestore();}
});

it("renders exact source wording, declared severity and unrecorded evidence or residual UNKNOWN",()=>{
 const summary=analysisFixture();
 summary.axes[4].items=[{item_id:"risk-a",kind:"RISK",native_type:"CCAP",native_state:"MITIGATED",title:"Accès à vérifier",source_state:"CURRENT_SOURCE",source_anchor:null,start_byte_offset:12,end_byte_offset:43,lot_numbers:[],lot_state:"UNKNOWN",applicability:"UNKNOWN",responsible:null,action:null,consequences:"UNKNOWN",source_excerpt:"Échéance à confirmer : jamais zéro.",source_excerpt_state:"EXACT_SOURCE",severity:"CRITICAL",expected_evidence:"UNKNOWN",residual_risk:"UNKNOWN"}];
 panel({summary});
 expect(screen.getByText("Échéance à confirmer : jamais zéro.")).toBeInTheDocument();
 expect(screen.getByText(/Criticité déclarée : critique/)).toBeInTheDocument();
 expect(screen.getByText(/Preuve attendue : UNKNOWN/)).toBeInTheDocument();
 expect(screen.getByText(/Risque résiduel : UNKNOWN/)).toBeInTheDocument();
});

it("blocks reloading an unresolved case and restores only its exact pending intent",()=>{
 const registry=new AnalysisAssessmentPendingStore();const scope="owner/case-a";
 const payload:AnalysisAssessmentInput={command_id:"c",idempotency_key:"i",assessment_id:"a",point_kind:"RISK",point_id:"risk-a",expected_revision:0,source_context_sha256:"a".repeat(64),expected_evidence_state:"UNKNOWN",expected_evidence:null,residual_risk_state:"UNKNOWN",residual_risk:null,unknown_reason:"À qualifier",justification:"Relecture",human_confirmed:true};
 registry.put(JSON.stringify([scope,"RISK","risk-a"]),payload);
 const refresh=vi.fn();panel({summary:null,pendingIntents:registry,intentScope:scope,api:{recordCaseAnalysisAssessment:vi.fn()},onRefresh:refresh});
 expect(screen.getByRole("button",{name:/Charger la synthèse/})).toBeDisabled();
 expect(screen.getByText(/Acte antérieur au résultat inconnu/)).toBeInTheDocument();expect(refresh).not.toHaveBeenCalled();
});

it("makes absent price evidence explicitly UNKNOWN",()=>{
 panel();expect(screen.getByText(/Aucun scénario économique qualifié : UNKNOWN/)).toBeInTheDocument();
});

it("makes absent cash declarations explicitly UNKNOWN without inventing a funding peak",()=>{
 panel();expect(screen.getByText(/Aucune déclaration de trésorerie publiée : UNKNOWN/)).toBeInTheDocument();
 expect(screen.getByText(/Pic de financement : UNKNOWN/)).toBeInTheDocument();
});

it.each([
 ["TECHNICAL_PRESCRIPTION","Prescription technique à revoir"],
 ["LOGISTICS_CONSTRAINT","Contrainte logistique à revoir"],
 ["SCHEDULE_CONSTRAINT","Contrainte de planning ou de ressources à revoir"],
 ["HSE_CONSTRAINT","Contrainte HSE à revoir"],
 ["PAYMENT_TERM_SIGNAL","Condition de paiement à revoir"],
 ["ACCEPTANCE_TERM_SIGNAL","Condition de réception à revoir"],
])("renders the review label for %s",(native_type,label)=>{
 const summary=analysisFixture();
 summary.axes[2].items=[{item_id:"execution-a",kind:"REQUIREMENT",native_type,native_state:"PENDING_HUMAN_CONFIRMATION",title:null,source_state:"CURRENT_SOURCE",source_anchor:null,start_byte_offset:0,end_byte_offset:45,lot_numbers:[5],lot_state:"CANDIDATE",applicability:"UNKNOWN",responsible:null,action:null,consequences:"UNKNOWN",source_excerpt:"Lot 5 : ne pas installer sans validation.",source_excerpt_state:"EXACT_SOURCE",severity:"UNKNOWN",expected_evidence:"UNKNOWN",residual_risk:"UNKNOWN"}];
 panel({summary});expect(screen.getByText(label)).toBeInTheDocument();
 expect(screen.getByText("Lot 5 : ne pas installer sans validation.")).toBeInTheDocument();
});

it.each([
 ["text_line",{line:7},"ligne 7"],
 ["docx_paragraph",{paragraph:4},"paragraphe 4"],
 ["docx_table_cell",{table:2,row:3,column:4,paragraph:1},"tableau 2 · ligne 3 · colonne 4 · paragraphe 1 · contexte entre cellules UNKNOWN"],
 ["docx_table_cell",{table:2,row:0,column:4,paragraph:1},"localisation UNKNOWN"],
 ["xlsx_cell",{sheet:"Prix",cell:"B8"},"feuille Prix · cellule B8"],
 ["pdf_page",{page:2},"page 2"],
 ["text_line",{line:0},"localisation UNKNOWN"],
] as const)("shows only proven %s coordinates",(kind,coordinates,expected)=>{
 const summary=analysisFixture();
 summary.axes[2].items=[{item_id:"trace-a",kind:"REQUIREMENT",native_type:"TECHNICAL_PRESCRIPTION",native_state:"PENDING_HUMAN_CONFIRMATION",title:null,source_state:"CURRENT_SOURCE",source_anchor:{source_anchor_id:"fragment-a",dce_version_id:"version-a",dce_document_id:"doc-a",extraction_id:"extract-a",fragment_ordinal:1,source_sha256:"a".repeat(64),extractor_id:"native",extractor_version:"2",fragment_sha256:"b".repeat(64),locator_state:"RESOLVED",locator:{kind,coordinates}},start_byte_offset:0,end_byte_offset:4,lot_numbers:[],lot_state:"UNKNOWN",applicability:"UNKNOWN",responsible:null,action:null,consequences:"UNKNOWN"}];
 panel({summary});expect(screen.getByText("Références de la source · "+expected)).toBeInTheDocument();
});


it("suspend la synthèse et ses actions pendant une admission DCE UNKNOWN",()=>{
 const onRefresh=vi.fn();panel({sourceReadBlocked:true,onRefresh});
 expect(screen.queryByRole("table")).toBeNull();
 expect(screen.getByText(/Admission DCE en cours ou UNKNOWN/)).toBeVisible();
 expect(screen.queryByRole("button",{name:"Charger la synthèse"})).toBeNull();
});


it("rend l’ancien intent UNKNOWN reprenable même quand le dossier V2 est affiché",()=>{
 const registry=new AnalysisAssessmentPendingStore();const scope="owner/case-a";
 const payload:AnalysisAssessmentInput={command_id:"c",idempotency_key:"i",assessment_id:"a",point_kind:"RISK",point_id:"old-v1-risk",expected_revision:0,source_context_sha256:"a".repeat(64),expected_evidence_state:"UNKNOWN",expected_evidence:null,residual_risk_state:"UNKNOWN",residual_risk:null,unknown_reason:"À qualifier",justification:"Acte V1",human_confirmed:true};
 registry.put(JSON.stringify([scope,"RISK","old-v1-risk"]),payload);
 panel({pendingIntents:registry,intentScope:scope,api:{recordCaseAnalysisAssessment:vi.fn()}});
 const toggle=screen.queryByText("Déclarer preuve attendue et risque résiduel");if(toggle)fireEvent.click(toggle);
 expect(screen.getByRole("button",{name:"Réessayer le même acte"})).toBeVisible();
 expect(screen.getByRole("button",{name:"Charger la synthèse"})).toBeDisabled();
});
