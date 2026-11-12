import {useEffect,useRef,useState} from "react";
import type {ApiClient} from "../../infrastructure/api";
import type {AnalysisDossierHistoryPage} from "../../shared/types";
import {axisLabels} from "./AnalysisTreatmentFields";

export function AnalysisDossierHistory({api,caseId,disabled}:{api:ApiClient;caseId:string;disabled:boolean}){
 const[page,setPage]=useState<AnalysisDossierHistoryPage|null>(null);const[loading,setLoading]=useState(false);const[error,setError]=useState("");const active=useRef<object|null>(null);
 useEffect(()=>()=>{active.current=null;},[]);
 async function load(before?:number){
  if(disabled||loading)return;const request={};active.current=request;setLoading(true);setPage(null);setError("");
  try{const value=await api.getCaseAnalysisDossierHistory(caseId,before);if(active.current!==request)return;
   if(value.case_id!==caseId||value.entries.some(e=>e.state!=="HISTORICAL"||e.snapshot.case_id!==caseId||e.snapshot.dce_version_id!==e.dce_version_id||e.snapshot.analysis_complete!==false))throw Error("HISTORY_CONTEXT_MISMATCH");
   setPage(value);
  }catch{if(active.current===request)setError("Historique indisponible ou non concordant. Aucune ancienne conclusion n’est rendue courante.");}
  finally{if(active.current===request)setLoading(false);}
 }
 return <section aria-label="Historique des dossiers d’analyse"><h3>Historique des préparations et revues</h3>
  <p>Lecture historique privée : sources, traitement et hypothèses conservés au moment de l’acte. Ces éléments ne sont pas des conclusions courantes ni une analyse complète.</p>
  <button className="secondary-button compact-button" type="button" disabled={disabled||loading} onClick={()=>void load()}>Consulter l’historique du dossier</button>
  {error&&<p role="alert">{error}</p>}{loading&&<p role="status">Chargement de l’historique…</p>}
  {page?.entries.length===0&&<p>Aucune préparation ou revue historique enregistrée.</p>}
  {page?.entries.map(entry=><details key={entry.review_id}><summary>Historique — {entry.phase==="PREPARED"?"Préparation":"Revue"} · Révision {entry.revision} · {entry.created_at}</summary>
   <p>Version DCE historique : {entry.dce_version_id} · Empreinte du dossier : {entry.dossier_sha256} · Patron : {entry.actor_id}</p><p>Justification historique : {entry.justification}</p>
   <ul>{entry.axes.map(a=><li key={a.code}>{axisLabels[a.code]} : {a.state} · {a.note} · Action : {a.follow_up??"Aucune action d’inconnu déclarée"}</li>)}</ul>
   {entry.snapshot.axes.map(axis=><div key={axis.code}><h4>{axisLabels[axis.code]}</h4>{axis.items.map(point=><div key={`${point.kind}:${point.item_id}`}>
    <p>Point historique {point.item_id} · Extrait enregistré :</p><blockquote style={{whiteSpace:"pre-wrap",overflowWrap:"anywhere"}}>{point.source_excerpt??"UNKNOWN"}</blockquote>
    <p>Source : {point.source_anchor?.dce_document_id??"UNKNOWN"} · Empreinte : {point.source_anchor?.source_sha256??"UNKNOWN"} · Région : {point.start_byte_offset??"UNKNOWN"}–{point.end_byte_offset??"UNKNOWN"}</p>
    <p>Action déclarée historique : {point.human_assessment?.treatment?.action??"UNKNOWN"} · Responsable Patron : {point.human_assessment?.actor_id??"UNKNOWN"}</p>
    <p>Preuve attendue historique : {point.human_assessment?.expected_evidence??"UNKNOWN"} · Risque résiduel historique : {point.human_assessment?.residual_risk??"UNKNOWN"}</p>
   </div>)}</div>)}
  </details>)}
  {page?.next_before_revision!=null&&<button className="secondary-button compact-button" type="button" disabled={disabled||loading} onClick={()=>void load(page.next_before_revision!)}>Consulter les actes plus anciens</button>}
 </section>;
}
