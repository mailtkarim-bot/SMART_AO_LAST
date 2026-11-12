import {useEffect,useRef,useState,useSyncExternalStore,useId} from "react";
import type {AnalysisDossierInput,AnalysisDossierReceipt,CaseAnalysisSummary,DossierAxisReview} from "../../shared/types";
import {analysisAxisCodes} from "../../shared/types";
import {axisLabels} from "./AnalysisTreatmentFields";
import {AnalysisDossierPendingStore} from "./analysisDossierPending";

type Props={summary:CaseAnalysisSummary|null;scope:string;store:AnalysisDossierPendingStore;disabled:boolean;save:(input:AnalysisDossierInput)=>Promise<AnalysisDossierReceipt>;onLock:(v:boolean)=>void;onNotice:(t:string)=>void;onRefresh:()=>void};
export function AnalysisDossierForm({summary,scope,store,disabled,save,onLock,onNotice,onRefresh}:Props){
 const snapshot=useSyncExternalStore(store.subscribe,store.getSnapshot);const restored=snapshot.get(scope);
 const previous=summary?.dossier_review?.state==="CURRENT"&&summary.dossier_review.dossier_sha256===summary.dossier_sha256?summary.dossier_review:null;
 const[axes,setAxes]=useState<DossierAxisReview[]>(restored?.axes??previous?.axes??analysisAxisCodes.map(code=>({code,state:"UNKNOWN",note:"",follow_up:null,responsible:"SELF"})));
 const[justification,setJustification]=useState(restored?.justification??"");const[confirmed,setConfirmed]=useState(Boolean(restored));
 const[phase,setPhase]=useState<"IDLE"|"SENDING"|"UNKNOWN">(restored?"UNKNOWN":"IDLE");const[message,setMessage]=useState(restored?"Résultat inconnu pour un acte de dossier antérieur.":"");const id=useId();
 const intent=useRef<AnalysisDossierInput|null>(restored??null);const uncertain=useRef(Boolean(restored));const busy=useRef(false);const mounted=useRef(true);
 useEffect(()=>{mounted.current=true;return()=>{mounted.current=false;};},[]);
 const points=summary?.axes.flatMap(a=>a.items)??[];
 const missing=points.filter(p=>p.source_state!=="CURRENT_SOURCE"||p.human_assessment?.state!=="CURRENT"||!p.human_assessment.treatment);
 const invalidReviewedAxis=axes.some(axis=>axis.state==="POINTS_REVIEWED"&&!summary?.axes.find(a=>a.code===axis.code)?.items.length);
 const reviewReady=!invalidReviewedAxis&&previous?.phase==="PREPARED"&&previous.dossier_sha256===summary?.dossier_sha256&&missing.length===0&&!summary?.truncated&&JSON.stringify(axes)===JSON.stringify(previous.axes);
 const locked=disabled||phase!=="IDLE";
 function update(code:string,patch:Partial<DossierAxisReview>){setAxes(old=>old.map(a=>a.code===code?{...a,...patch}:a));}
 function clearHistoricalDraft(payload:AnalysisDossierInput){
  if(payload.dossier_sha256!==summary?.dossier_sha256){
   setAxes(previous?.axes??analysisAxisCodes.map(code=>({code,state:"UNKNOWN",note:"",follow_up:null,responsible:"SELF"})));
   setJustification("");
  }
 }
 async function send(){
  if(busy.current||!intent.current)return;busy.current=true;onLock(true);onNotice("");setPhase("SENDING");const payload=intent.current;
  try{const receipt=await save(payload);if(!mounted.current)return;
   if(receipt.review_id!==payload.review_id||receipt.command_id!==payload.command_id||receipt.idempotency_key!==payload.idempotency_key||receipt.revision!==payload.expected_revision+1)throw Error("DISCORDANT_RECEIPT");
   clearHistoricalDraft(payload);uncertain.current=false;store.remove(scope);intent.current=null;setPhase("IDLE");setConfirmed(false);onLock(false);onNotice(payload.dossier_sha256!==summary?.dossier_sha256?"Reçu de l’acte antérieur retrouvé ; aucun accord transféré au dossier courant.":payload.phase==="PREPARED"?"Préparation du dossier enregistrée; relisez les douze axes avant la revue.":"Revue humaine du dossier exact enregistrée; aucune conformité ni porte n’est confirmée.");onRefresh();
  }catch(error){if(!mounted.current)return;const status=(error as {status?:number}).status;
   if(status===409){clearHistoricalDraft(payload);uncertain.current=false;store.remove(scope);intent.current=null;setPhase("IDLE");setConfirmed(false);onLock(false);onNotice("Le dossier ou sa préparation a changé : relisez les sources avant un nouvel acte.");onRefresh();}
   else if(!uncertain.current&&status!==undefined&&[400,401,403,404,422].includes(status)){store.remove(scope);intent.current=null;setPhase("IDLE");setConfirmed(false);onLock(false);setMessage("Revue refusée : vérifiez les points non préparés, la session et les douze axes.");}
   else{uncertain.current=true;setPhase("UNKNOWN");setMessage("Résultat inconnu. Conservez le même acte; aucun nouvel enregistrement ou rechargement avant reçu ou conflit.");}
  }finally{busy.current=false;}
 }
 function submit(target:"PREPARED"|"REVIEWED"){
  if(locked||busy.current||!summary?.dossier_sha256)return;
  if(!confirmed||!justification.trim()||axes.some(a=>!a.note.trim()||(a.state==="UNKNOWN"&&!a.follow_up?.trim()))){setMessage("Chaque axe nécessite une note et chaque inconnu une action; justification et confirmation sont obligatoires.");return;}
  if(target==="REVIEWED"&&!reviewReady)return;
  const payload:AnalysisDossierInput={command_id:crypto.randomUUID(),idempotency_key:crypto.randomUUID(),review_id:crypto.randomUUID(),expected_revision:summary.dossier_review?.revision??0,dossier_sha256:summary.dossier_sha256,phase:target,axes,justification:justification.trim(),human_confirmed:true};
  intent.current=payload;store.put(scope,payload);void send();
 }
 return <section aria-label="Préparation et revue du dossier d’analyse">
  <h3>Préparer puis revoir le dossier exact</h3>
  <p>Traitez d’abord chaque point critique ci-dessus, puis consignez les douze axes. Un axe inconnu reste à instruire; cette revue ne déclare jamais l’analyse complète.</p>
  {summary?.dossier_review&&<p>Dernier acte : {summary.dossier_review.phase==="PREPARED"?"Préparation":"Revue humaine"} · Révision {summary.dossier_review.revision} · {summary.dossier_review.state==="CURRENT"?"Dossier concordant":"REVIEW_REQUIRED — dossier modifié"} · {summary.dossier_review.created_at}</p>}
  {previous&&<details><summary>Notes et responsabilité de l’acte enregistré</summary><p>Patron {previous.actor_id} · {previous.justification}</p><ul>{previous.axes.map(a=><li key={a.code}>{axisLabels[a.code]} : {a.state} · {a.note} · Action : {a.follow_up??"Pas d’action d’inconnu déclarée"}</li>)}</ul></details>}
  {invalidReviewedAxis&&<p role="status">Un axe sans point sourcé ne peut pas être déclaré « points relus ». Déclarez son inconnu et son action, puis préparez à nouveau.</p>}
  {missing.length>0&&<p role="status">{missing.length} point(s) sans traitement courant complet : la revue restera indisponible.</p>}
  {summary?.truncated&&<p role="status">Dossier limité : revue indisponible tant que les éléments masqués ne sont pas qualifiés.</p>}
  <p>Empreinte du dossier : {restored?.dossier_sha256??summary?.dossier_sha256??"UNKNOWN"}</p>
  <fieldset disabled={locked||!summary?.dossier_sha256||summary.source_context_state!=="CURRENT"}>
   <legend>Douze axes — responsabilité explicite du Patron</legend>
   {axes.map(axis=><details key={axis.code}><summary>{axisLabels[axis.code]} — {axis.state==="UNKNOWN"?"UNKNOWN":"Points relus"}</summary>
    <label htmlFor={`${id}-${axis.code}-state`}>Disposition — {axisLabels[axis.code]}</label><select id={`${id}-${axis.code}-state`} value={axis.state} onChange={e=>update(axis.code,{state:e.target.value as DossierAxisReview["state"]})}><option>UNKNOWN</option><option value="POINTS_REVIEWED" disabled={!summary?.axes.find(a=>a.code===axis.code)?.items.length}>Points sourcés relus — pas de complétude déduite</option></select>
    <label htmlFor={`${id}-${axis.code}-note`}>Note de revue — {axisLabels[axis.code]}</label><textarea id={`${id}-${axis.code}-note`} value={axis.note} maxLength={2000} onChange={e=>update(axis.code,{note:e.target.value})}/>
    <label htmlFor={`${id}-${axis.code}-action`}>Action pour l’inconnu — {axisLabels[axis.code]}</label><textarea id={`${id}-${axis.code}-action`} value={axis.follow_up??""} maxLength={2000} onChange={e=>update(axis.code,{follow_up:e.target.value||null})}/>
   </details>)}
   <label htmlFor={`${id}-why`}>Justification du dossier</label><textarea id={`${id}-why`} value={justification} maxLength={2000} onChange={e=>setJustification(e.target.value)}/>
   <label><input type="checkbox" checked={confirmed} onChange={e=>setConfirmed(e.target.checked)}/>Je confirme la préparation ou revue du dossier affiché et prends en charge les actions des axes inconnus, sans confirmer la conformité ni lever de porte.</label>
   <button className="secondary-button compact-button" type="button" onClick={()=>submit("PREPARED")}>Enregistrer la préparation du dossier</button>
   <button className="secondary-button compact-button" type="button" disabled={!reviewReady} onClick={()=>submit("REVIEWED")}>Enregistrer la revue du dossier préparé</button>
  </fieldset>
  {message&&<p role="status">{message}</p>}
  {phase==="UNKNOWN"&&<button className="secondary-button compact-button" type="button" onClick={()=>void send()}>Réessayer le même acte de dossier</button>}
 </section>;
}
