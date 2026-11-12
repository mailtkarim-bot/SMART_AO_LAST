import type { CaseAnalysisSummary } from "../../shared/types";
export function analysisFixture(): CaseAnalysisSummary {
 const axes=["COMMERCIAL","CANDIDATURE","TECHNICAL","CONSTRUCTIBILITY","CONTRACT","PRICE","CASH","CAPACITY","PARTNERS","HSE","DOCUMENTS","RIGHTS"] as const;
 return {case_id:"case-a",dce_version_id:"version-a",case_scope_kind:"SINGLE_LOT",status:"REVIEW_REQUIRED",analysis_complete:false,
  coverage_scope:"CURRENT_DCE_ONLY",source_context_state:"CURRENT",truncated:false,coverage:null,axes:axes.map(code=>({code,label:code,status:"NON_EVALUATED",mapping_basis:"NATIVE_REGISTER_TYPE_ONLY",items:[]}))};
}
