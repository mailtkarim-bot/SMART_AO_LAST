import { useLayoutEffect, useRef, useState } from "react";
import type { ApiClient } from "../../infrastructure/api";
import { analysisAxisCodes } from "../../shared/types";
import type { CaseAnalysisSummary, CaseAnalysisItem } from "../../shared/types";

function hasDiscordantAnatomy(item:CaseAnalysisItem) {
 const assessment=item.human_assessment;
 if(assessment?.state==="CURRENT"&&(item.source_state!=="CURRENT_SOURCE"||!item.source_context_sha256||assessment.source_context_sha256!==item.source_context_sha256))return true;
 if(assessment?.state==="REVIEW_REQUIRED"&&(assessment.expected_evidence!==null||assessment.residual_risk!==null||assessment.justification!==null||assessment.unknown_reason!==null||assessment.treatment!=null))return true;
 const exact=item.source_excerpt_state==="EXACT_SOURCE";
 if (exact!==(typeof item.source_excerpt==="string" && item.source_excerpt.length>0)) return true;
 if (item.source_state!=="CURRENT_SOURCE" && (exact || (item.severity!==undefined && item.severity!=="UNKNOWN"))) return true;
 return exact && (item.start_byte_offset===null || item.end_byte_offset===null ||
   item.source_excerpt_unknown_reason!=null ||
   new TextEncoder().encode(item.source_excerpt!).length!==item.end_byte_offset-item.start_byte_offset);
}

export function useCaseAnalysisSummary(api: ApiClient, caseId: string, scope: string, version: string | null) {
  const key = scope && caseId && version ? JSON.stringify([scope,caseId,version]) : "";
  const [entry,setEntry]=useState<{key:string;summary:CaseAnalysisSummary|null;loading:boolean;error:string|null}|null>(null);
  const request=useRef<object|null>(null);
  useLayoutEffect(()=>{request.current=null;setEntry(null);return ()=>{request.current=null;};},[key]);
  const current=key && entry?.key===key ? entry : null;
  async function refresh() {
    if (!key) return;
    const token={};request.current=token;
    setEntry({key,summary:null,loading:true,error:null});
    try {
      const value=await api.getCaseAnalysisSummary(caseId);
      if (request.current!==token) return;
      if ((value.dossier_review?.state==="CURRENT"&&value.dossier_review.dossier_sha256!==value.dossier_sha256)||(value.dossier_review?.state==="REVIEW_REQUIRED"&&(value.dossier_review.axes.length>0||value.dossier_review.justification!==null||value.dossier_review.actor_id!==null))||value.case_id!==caseId || value.dce_version_id!==version || value.analysis_complete!==false ||
          value.axes.length!==12 || new Set(value.axes.map(a=>a.code)).size!==12 ||
          value.axes.some(a=>!analysisAxisCodes.includes(a.code) || a.items.some(i=>hasDiscordantAnatomy(i) || (i.source_anchor && i.source_anchor.dce_version_id!==version) || (value.source_context_state!=="CURRENT" && i.source_state==="CURRENT_SOURCE") ||
            Boolean(i.follow_ups?.length && (i.source_state!=="CURRENT_SOURCE" || i.follow_up_state!=="RECORDED")) ||
            Boolean(i.follow_ups?.some(f=>(i.kind==="REQUIREMENT"?f.requirement_id:f.risk_id)!==i.item_id))))) {
        throw new Error("SOURCE_CONTEXT_MISMATCH");
      }
      setEntry({key,summary:value,loading:false,error:null});
    } catch (error) {
      if (request.current!==token) return;
      setEntry({key,summary:null,loading:false,error:(error as {status?:number}).status===409
        ? "Le dossier a changé. Rechargez la lecture DCE."
        : "Synthèse indisponible. Rechargez les sources courantes."});
    }
  }
  return {summary:current?.summary??null,loading:current?.loading??false,error:current?.error??null,refresh};
}
