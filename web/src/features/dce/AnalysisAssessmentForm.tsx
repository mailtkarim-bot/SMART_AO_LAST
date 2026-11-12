import {AnalysisTreatmentFields,emptyTreatment} from "./AnalysisTreatmentFields";
import type {AnalysisTreatment} from "../../shared/types";
import {AnalysisAssessmentPendingStore} from "./analysisAssessmentPending";
import {useEffect,useId,useRef,useState,useLayoutEffect,useSyncExternalStore} from "react";
import type {AnalysisAssessmentInput,AnalysisAssessmentReceipt,CaseAnalysisItem} from "../../shared/types";

type Props={historical?:boolean;axisCode?:AnalysisTreatment["axis_code"];pendingIntents?:AnalysisAssessmentPendingStore;intentScope?:string;item:Pick<CaseAnalysisItem,"item_id"|"kind"|"source_context_sha256"|"human_assessment">;disabled:boolean;save:(input:AnalysisAssessmentInput)=>Promise<AnalysisAssessmentReceipt>;onLock:(value:boolean)=>void;onNotice:(text:string)=>void;onRefresh:()=>void};
export function AnalysisAssessmentForm({historical=false,axisCode="TECHNICAL",item,disabled,save,onLock,onNotice,onRefresh,pendingIntents,intentScope="local"}:Props){
 const[localRegistry]=useState(()=>new AnalysisAssessmentPendingStore());
 const registry=pendingIntents??localRegistry;
 const pending=useSyncExternalStore(registry.subscribe,registry.getSnapshot);
 const registryKey=JSON.stringify([intentScope,item.kind,item.item_id]);
 const restored=pending.get(registryKey);
 useLayoutEffect(()=>{if(restored)onLock(true);},[restored,onLock]);
 const id=useId();const [evidenceState,setEvidenceState]=useState<"DECLARED"|"UNKNOWN">(restored?.expected_evidence_state??"UNKNOWN");const[evidence,setEvidence]=useState(restored?.expected_evidence??"");const[residualState,setResidualState]=useState<"DECLARED"|"UNKNOWN">(restored?.residual_risk_state??"UNKNOWN");const[residual,setResidual]=useState(restored?.residual_risk??"");const[reason,setReason]=useState(restored?.unknown_reason??"");const[justification,setJustification]=useState(restored?.justification??"");const[confirmed,setConfirmed]=useState(Boolean(restored));const[phase,setPhase]=useState<"IDLE"|"SENDING"|"UNKNOWN">(restored?"UNKNOWN":"IDLE");const[message,setMessage]=useState(restored?"Résultat inconnu pour un acte antérieur. Réessayez uniquement le même acte avant toute relecture.":"");
 const[treatment,setTreatment]=useState<AnalysisTreatment|null>(restored?.treatment??null);
 const intent=useRef<AnalysisAssessmentInput|null>(restored??null);const busy=useRef(false);const uncertain=useRef(Boolean(restored));const mounted=useRef(true);
 useEffect(()=>{mounted.current=true;return()=>{mounted.current=false;};},[]);
 const locked=disabled||phase!=="IDLE";
 async function sendPending(){
  if(busy.current||!intent.current)return;
  busy.current=true;setPhase("SENDING");onLock(true);onNotice("");setMessage("");
  const payload=intent.current;
  try{
   const receipt=await save(payload);if(!mounted.current)return;
   if(receipt.assessment_id!==payload.assessment_id||receipt.command_id!==payload.command_id||receipt.idempotency_key!==payload.idempotency_key||receipt.revision!==payload.expected_revision+1)throw new Error("DISCORDANT_RECEIPT");
   uncertain.current=false;registry.remove(registryKey);intent.current=null;setPhase("IDLE");setConfirmed(false);onLock(false);onNotice(historical?"Reçu de l’acte antérieur retrouvé ; aucun accord transféré au point courant.":"Déclaration humaine enregistrée. Elle ne vaut ni confirmation de conformité ni levée de porte.");onRefresh();
  }catch(error){
   if(!mounted.current)return;
   const status=(error as {status?:number}).status;
   if(status===409){uncertain.current=false;registry.remove(registryKey);intent.current=null;setPhase("IDLE");setConfirmed(false);onLock(false);onNotice("Conflit de source ou de révision : relisez la synthèse avant tout nouvel acte.");onRefresh();}
   else if(uncertain.current&&status!==undefined&&[400,401,403,404,422].includes(status)){setPhase("UNKNOWN");setMessage("Résultat inconnu pour l’acte initial. Session ou droits à revalider avant de réessayer le même acte.");}
   else if(status!==undefined&&[400,401,403,404,422].includes(status)){uncertain.current=false;registry.remove(registryKey);intent.current=null;setPhase("IDLE");setConfirmed(false);onLock(false);setMessage("Déclaration refusée. Vérifiez votre session et les valeurs saisies.");}
   else{uncertain.current=true;setPhase("UNKNOWN");setMessage("Résultat inconnu. Réessayez uniquement le même acte ; aucune nouvelle déclaration ni relecture automatique.");}
  }finally{busy.current=false;}
 }
 function submit(event:React.FormEvent){
  event.preventDefault();if(locked||busy.current||!item.source_context_sha256)return;
  if(!confirmed||!justification.trim()||((evidenceState==="UNKNOWN"||residualState==="UNKNOWN")&&!reason.trim())||(evidenceState==="DECLARED"&&!evidence.trim())||(residualState==="DECLARED"&&!residual.trim())){setMessage("Justification, valeurs et confirmation explicite requises.");return;}
  intent.current={...(treatment?{treatment}:{}),command_id:crypto.randomUUID(),idempotency_key:crypto.randomUUID(),assessment_id:crypto.randomUUID(),point_kind:item.kind,point_id:item.item_id,expected_revision:item.human_assessment?.revision??0,source_context_sha256:item.source_context_sha256,expected_evidence_state:evidenceState,expected_evidence:evidenceState==="DECLARED"?evidence.trim():null,residual_risk_state:residualState,residual_risk:residualState==="DECLARED"?residual.trim():null,unknown_reason:reason.trim()||null,justification:justification.trim(),human_confirmed:true};
  registry.put(registryKey,intent.current);
  void sendPending();
 }
 return <details><summary>Déclarer preuve attendue et risque résiduel</summary><form aria-label="Revue humaine du point critique" onSubmit={submit}>
  <p>Point : {item.kind} · {item.item_id} · Empreinte de contexte : {item.source_context_sha256}</p>
  <p>Acte Patron · session MFA requise. Déclaration liée au point et à la source affichés. Les inconnus restent explicites.</p>
  <fieldset disabled={locked}><legend>Nouvelle révision de revue</legend>
   <label htmlFor={`${id}-es`}>État de la preuve attendue</label><select id={`${id}-es`} value={evidenceState} onChange={e=>setEvidenceState(e.target.value as typeof evidenceState)}><option value="UNKNOWN">Inconnue (UNKNOWN)</option><option value="DECLARED">Déclarée par le Patron</option></select>
   {evidenceState==="DECLARED"&&<><label htmlFor={`${id}-e`}>Preuve attendue</label><textarea id={`${id}-e`} value={evidence} maxLength={2000} onChange={e=>setEvidence(e.target.value)} required/></>}
   <label htmlFor={`${id}-rs`}>État du risque résiduel</label><select id={`${id}-rs`} value={residualState} onChange={e=>setResidualState(e.target.value as typeof residualState)}><option value="UNKNOWN">Inconnu (UNKNOWN)</option><option value="DECLARED">Déclaré par le Patron</option></select>
   {residualState==="DECLARED"&&<><label htmlFor={`${id}-r`}>Risque résiduel déclaré</label><textarea id={`${id}-r`} value={residual} maxLength={2000} onChange={e=>setResidual(e.target.value)} required/></>}
   <label htmlFor={`${id}-u`}>Raison des inconnus</label><textarea id={`${id}-u`} value={reason} maxLength={2000} onChange={e=>setReason(e.target.value)} required={evidenceState==="UNKNOWN"||residualState==="UNKNOWN"}/>
   <label><input type="checkbox" checked={Boolean(treatment)} onChange={e=>setTreatment(e.target.checked?(item.human_assessment?.state==="CURRENT"&&item.human_assessment.treatment?item.human_assessment.treatment:emptyTreatment(axisCode)):null)}/>Compléter le traitement et me désigner responsable de préparation</label>
   {treatment&&<AnalysisTreatmentFields id={id} value={treatment} onChange={setTreatment}/>}
   <label htmlFor={`${id}-j`}>Justification de la revue</label><textarea id={`${id}-j`} value={justification} maxLength={2000} onChange={e=>setJustification(e.target.value)} required/>
   <label><input type="checkbox" checked={confirmed} onChange={e=>setConfirmed(e.target.checked)}/>Je confirme cette déclaration sur le point et la source affichés, sans confirmer la conformité ni lever une porte.</label>
   <button type="submit" className="secondary-button compact-button">Enregistrer la déclaration humaine</button>
  </fieldset>
  {message&&<p role="status">{message}</p>}
  {phase==="UNKNOWN"&&<button className="secondary-button compact-button" type="button" onClick={()=>void sendPending()}>Réessayer le même acte</button>}
  {phase==="SENDING"&&<p role="status">Enregistrement en cours…</p>}
 </form></details>;
}
