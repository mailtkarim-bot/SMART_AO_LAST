import type { AnalysisTreatment } from "../../shared/types";
import {analysisAxisCodes} from "../../shared/types";
export const axisLabels:Record<typeof analysisAxisCodes[number],string>={COMMERCIAL:"Intérêt commercial",CANDIDATURE:"Candidature",TECHNICAL:"Périmètre technique",CONSTRUCTIBILITY:"Constructibilité et logistique",CONTRACT:"Contrat",PRICE:"Prix et marge",CASH:"Trésorerie et garanties",CAPACITY:"Capacité et ressources",PARTNERS:"Partenaires",HSE:"HSE, environnement et réglementation",DOCUMENTS:"Documents et engagements de l’offre",RIGHTS:"Droits, réception et sortie"};
const consequences={technical:"technique",price:"prix et marge",delay:"délai",cash:"trésorerie",contract:"contractuelle"} as const;
export function emptyTreatment(axis:AnalysisTreatment["axis_code"]):AnalysisTreatment{return {axis_code:axis,applicability:"UNKNOWN",applicability_reason:"",consequences:{technical:null,price:null,delay:null,cash:null,contract:null},unknown_reason:null,action:"",responsible:"SELF",due_at:null};}
function localInputTime(iso:string){const date=new Date(iso);const pad=(v:number)=>String(v).padStart(2,"0");return `${date.getFullYear()}-${pad(date.getMonth()+1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;}
export function AnalysisTreatmentFields({id,value,onChange}:{id:string;value:AnalysisTreatment;onChange:(v:AnalysisTreatment)=>void}){
 return <fieldset><legend>Traitement déclaré du point critique</legend>
  <label htmlFor={`${id}-axis`}>Axe qualifié humainement</label><select id={`${id}-axis`} value={value.axis_code} onChange={e=>onChange({...value,axis_code:e.target.value as AnalysisTreatment["axis_code"]})}>{analysisAxisCodes.map(c=><option value={c} key={c}>{axisLabels[c]}</option>)}</select>
  <label htmlFor={`${id}-app`}>Applicabilité déclarée à la portée affichée</label><select id={`${id}-app`} value={value.applicability} onChange={e=>onChange({...value,applicability:e.target.value as AnalysisTreatment["applicability"]})}><option>UNKNOWN</option><option value="APPLIES">Applicable — déclaration humaine</option><option value="NOT_APPLICABLE">Non applicable — déclaration humaine</option></select>
  <label htmlFor={`${id}-scope`}>Motif d’applicabilité</label><textarea id={`${id}-scope`} required maxLength={2000} value={value.applicability_reason} onChange={e=>onChange({...value,applicability_reason:e.target.value})}/>
  {Object.entries(consequences).map(([key,label])=><div key={key}><label htmlFor={`${id}-${key}`}>Conséquence {label} — vide signifie UNKNOWN</label><textarea id={`${id}-${key}`} maxLength={2000} value={value.consequences[key as keyof typeof consequences]??""} onChange={e=>onChange({...value,consequences:{...value.consequences,[key]:e.target.value||null}})}/></div>)}
  <label htmlFor={`${id}-unknown`}>Raison des conséquences ou échéance inconnues</label><textarea id={`${id}-unknown`} maxLength={2000} value={value.unknown_reason??""} onChange={e=>onChange({...value,unknown_reason:e.target.value||null})}/>
  <label htmlFor={`${id}-hypotheses`}>Hypothèses déclarées — vide signifie UNKNOWN</label><textarea id={`${id}-hypotheses`} maxLength={2000} value={value.hypotheses??""} onChange={e=>onChange({...value,hypotheses:e.target.value||null})}/>
  <label htmlFor={`${id}-action`}>Action de préparation déclarée</label><textarea id={`${id}-action`} required maxLength={2000} value={value.action} onChange={e=>onChange({...value,action:e.target.value})}/>
  <label htmlFor={`${id}-due`}>Échéance — vide signifie UNKNOWN</label><input id={`${id}-due`} type="datetime-local" value={value.due_at?localInputTime(value.due_at):""} onChange={e=>onChange({...value,due_at:e.target.value?new Date(e.target.value).toISOString():null})}/>
  <p>Responsable de préparation : vous, Patron. Il s’agit d’un traitement déclaré; aucune tâche exécutée, confirmation ou porte n’est déduite.</p>
 </fieldset>;
}
export function AnalysisTreatmentRead({value,actorId}:{value:AnalysisTreatment;actorId:string|null}){
 return <div aria-label="Traitement humain enregistré"><p>Axe déclaré : {axisLabels[value.axis_code]} · Applicabilité : {value.applicability} · Motif : {value.applicability_reason}</p>
  <p>Hypothèses déclarées : {value.hypotheses??"UNKNOWN"}</p>
  <ul>{Object.entries(consequences).map(([key,label])=><li key={key}>Conséquence {label} : {value.consequences[key as keyof typeof consequences]??"UNKNOWN"}</li>)}</ul>
  <p>Action déclarée : {value.action} · Responsable Patron : {actorId??"UNKNOWN"} · Échéance : {value.due_at??"UNKNOWN"}</p><p>Raison des inconnus : {value.unknown_reason??"Aucun inconnu déclaré"}</p>
 </div>;
}
