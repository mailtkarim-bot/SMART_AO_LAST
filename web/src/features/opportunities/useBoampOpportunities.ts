import {useRef,useState,useLayoutEffect} from 'react';
import type {Dispatch,SetStateAction} from 'react';
import type {ApiClient} from '../../infrastructure/api';
import type {BoampObservation,BoampSourceStatus,BoampCaseCreationInput,BoampCaseCreationResponse,BoampQualificationDecision,BoampQualificationForm,BoampQualificationReason,BoampQualificationReceipt,BoampQualificationInput} from '../../shared/types';

type Message={tone:'success'|'error'|'warning';text:string};
export type BoampPending={kind:'qualification'|'creation';phase:'NEW'|'SENDING'|'UNKNOWN'|'READ_REQUIRED';observation:BoampObservation;input:BoampQualificationInput & BoampCaseCreationInput|BoampCaseCreationInput;receipt?:BoampQualificationReceipt|BoampCaseCreationResponse};
const initialForm:BoampQualificationForm={decision:'QUALIFIED',reason_code:'RELEVANT_PUBLIC_SIGNAL'};
export function useBoampOpportunities(api:ApiClient,setMessage:Dispatch<SetStateAction<Message|null>>,onCaseCreated?:(result:BoampCaseCreationResponse)=>Promise<void>|void,ownerKey='legacy'){
 const [data,setData]=useState<{owner:string;observations:BoampObservation[];sourceStatus:BoampSourceStatus|null;selected:string}>({owner:ownerKey,observations:[],sourceStatus:null,selected:''});
 const [form,setForm]=useState({owner:ownerKey,value:initialForm});
 const [reading,setReading]=useState<string|null>(null);
 const [blockedOwner,setBlockedOwner]=useState<string|null>(null);
 const [intents,setIntents]=useState(()=>new Map<string,BoampPending>());
 const intentRef=useRef(intents),owner=useRef(ownerKey),generation=useRef(0),reads=useRef(0);
 useLayoutEffect(()=>{if(owner.current!==ownerKey){owner.current=ownerKey;generation.current++;reads.current++;}},[ownerKey]);
 const pending=intents.get(ownerKey)??null;
 const visible=data.owner===ownerKey&&blockedOwner!==ownerKey?data:{owner:ownerKey,observations:[],sourceStatus:null,selected:''};
 const observations=blockedOwner===ownerKey?[]:visible.observations.length?visible.observations:pending?[pending.observation]:[];
 const selectedObservationId=pending?.observation.observation_id??visible.selected;
 const qualificationForm=form.owner===ownerKey?form.value:initialForm;
 const qualifiedObservationIds=new Set(observations.filter(o=>o.p0_state==='TARGETED').map(o=>o.observation_id));
 function update(key:string,value:BoampPending|null){const next=new Map(intentRef.current);if(value)next.set(key,value);else next.delete(key);intentRef.current=next;setIntents(next);}
 async function read(key=ownerKey,epoch=generation.current){
  if(!key||owner.current!==key||generation.current!==epoch)return false;
  const sequence=++reads.current;setReading(key);
  try{const result=await api.listBoampObservations();if(!Array.isArray(result.observations))throw Error("Réponse BOAMP discordante.");
   if(owner.current!==key||generation.current!==epoch||sequence!==reads.current)return false;
   setBlockedOwner(null);
   setData(old=>({owner:key,observations:result.observations,sourceStatus:result.source_status??null,
    selected:old.owner===key&&result.observations.some(o=>o.observation_id===old.selected)?old.selected:result.observations[0]?.observation_id??''}));
   return true;
  }catch(error){if(owner.current===key&&generation.current===epoch){if([401,403,404].includes((error as {status?:number}).status??0))setBlockedOwner(key);setData({owner:key,observations:[],sourceStatus:null,selected:''});setMessage({tone:'error',text:error instanceof Error?error.message:'Impossible de charger les opportunités BOAMP.'});}return false;
  }finally{if(owner.current===key&&generation.current===epoch)setReading(null);}
 }
 async function finish(intent:BoampPending,key:string,epoch:number){
  if(!await read(key,epoch))return;
  if(owner.current!==key||generation.current!==epoch)return;
  if(intent.kind==='creation'&&intent.receipt){
   try{await onCaseCreated?.(intent.receipt as BoampCaseCreationResponse);}
   catch{if(owner.current===key&&generation.current===epoch)setMessage({tone:'warning',text:'Affaire reçue : la navigation doit être relue.'});return;}
  }
  update(key,null);
  if(owner.current!==key||generation.current!==epoch)return;
  const replayed=intent.receipt?.replayed;
  setMessage({tone:'success',text:intent.kind==='qualification'?(replayed?'Qualification déjà enregistrée : rejeu idempotent.':'Qualification BOAMP enregistrée.'):(replayed?'Affaire BOAMP déjà créée : rejeu idempotent.':`Affaire créée depuis BOAMP. Révision ${(intent.receipt as BoampCaseCreationResponse).version} · ${(intent.receipt as BoampCaseCreationResponse).case_id}`)});
 }
 async function send(intent:BoampPending,key=ownerKey){
  if(!key||owner.current!==key)return;
  if(intentRef.current.get(key)?.phase==='SENDING')return;
  const epoch=generation.current;update(key,{...intent,phase:'SENDING'});
  try{
   const receipt=intent.kind==='qualification'?await api.qualifyBoampObservation(intent.observation.observation_id,intent.input as BoampQualificationInput):await api.createCaseFromBoampObservation(intent.observation.observation_id,intent.input);
   if(typeof receipt.replayed!=='boolean')throw Error('DISCORDANT_RECEIPT');
   if(intent.kind==='creation'){
    const r=receipt as BoampCaseCreationResponse;
    if(r.command_id!==intent.input.command_id||r.idempotency_key!==intent.input.idempotency_key||r.status!=='SUCCEEDED'||r.result_code!=='CASE_CREATED'||!r.case_id||!Number.isSafeInteger(r.version)||r.version<0)throw Error('DISCORDANT_RECEIPT');
   }else{const r=receipt as BoampQualificationReceipt;if(!r.qualification_id||!r.event_id)throw Error('DISCORDANT_RECEIPT');}
   const next={...intent,phase:'READ_REQUIRED' as const,receipt};update(key,next);
   if(owner.current===key&&generation.current===epoch)await finish(next,key,epoch);
   return intent.kind==='creation'?receipt as BoampCaseCreationResponse:undefined;
  }catch(error){const failure=error as {status?:number;message?:string};
   if([401,403,404].includes(failure.status??0)&&owner.current===key){setBlockedOwner(key);setData({owner:key,observations:[],sourceStatus:null,selected:''});}
   if(failure.status===409){update(key,{...intent,phase:'READ_REQUIRED'});if(await read(key,epoch)){update(key,null);if(owner.current===key)setMessage({tone:'warning',text:'Conflit : état courant relu. Une Affaire peut déjà être liée à cet avis ; confirmez toute nouvelle intention.'});}return;}
   // Only explicit initial refusals allow correction; an unknown original result stays frozen.
   if(intent.phase==='NEW'&&[400,401,403,404,422].includes(failure.status??0)){
    update(key,null);if(owner.current===key&&generation.current===epoch)setMessage({tone:'error',text:failure.message??'Opération refusée.'});return;
   }
   update(key,{...intent,phase:'UNKNOWN'});
   if(owner.current===key&&generation.current===epoch)setMessage({tone:'warning',text:'Résultat UNKNOWN : intention et identifiants figés. Réessayez uniquement la même opération.'});
  }
 }
 async function resume(){const current=intentRef.current.get(ownerKey);if(!current||current.phase==='SENDING')return;if(current.phase==='READ_REQUIRED'){if(current.receipt)await finish(current,ownerKey,generation.current);else if(await read()){update(ownerKey,null);}return;}return send(current);}
 async function refreshObservations(){if(intentRef.current.has(ownerKey)){await resume();return;}await read();}
 function selectObservation(id:string){if(intentRef.current.has(ownerKey))return;setData(old=>old.owner===ownerKey?{...old,selected:id}:old);setForm({owner:ownerKey,value:initialForm});}
 function setDecision(decision:BoampQualificationDecision){if(intentRef.current.has(ownerKey))return;setForm({owner:ownerKey,value:{decision,reason_code:decision==='QUALIFIED'?'RELEVANT_PUBLIC_SIGNAL':decision==='REJECTED'?'NOT_RELEVANT':'INSUFFICIENT_PUBLIC_DATA'}});}
 function setReason(reason_code:BoampQualificationReason){if(intentRef.current.has(ownerKey))return;setForm({owner:ownerKey,value:{...qualificationForm,reason_code}});}
 async function qualifySelected(){
  const previous=intentRef.current.get(ownerKey);if(previous){if(previous.kind==='qualification')await resume();return;}
  const observation=observations.find(o=>o.observation_id===selectedObservationId);
  if(!observation){setMessage({tone:'warning',text:'Sélectionnez une opportunité BOAMP avant de qualifier.'});return;}
  const input={...qualificationForm,command_id:crypto.randomUUID(),idempotency_key:crypto.randomUUID(),correlation_id:crypto.randomUUID()};
  // Store SENDING before yielding, so a double click cannot start a second request.
  await send({kind:'qualification',phase:'NEW',observation,input});
 }
 async function createCaseFromSelected(){
  const previous=intentRef.current.get(ownerKey);if(previous){if(previous.kind==='creation')return resume();return;}
  const observation=observations.find(o=>o.observation_id===selectedObservationId);
  if(!observation){setMessage({tone:'warning',text:'Sélectionnez une opportunité BOAMP avant de créer une affaire.'});return;}
  if(!qualifiedObservationIds.has(selectedObservationId)){setMessage({tone:'warning',text:'Qualifiez l’opportunité BOAMP avant de créer une affaire.'});return;}
  return send({kind:'creation',phase:'NEW',observation,input:{command_id:crypto.randomUUID(),idempotency_key:crypto.randomUUID(),correlation_id:crypto.randomUUID()}});
 }
 return {observations,sourceStatus:visible.sourceStatus,selectedObservationId,qualificationForm,
  loading:reading===ownerKey,qualifying:pending?.kind==='qualification'&&pending.phase==='SENDING',creatingCase:pending?.kind==='creation'&&pending.phase==='SENDING',qualifiedObservationIds,pending,
  refreshObservations,selectObservation,setDecision,setReason,qualifySelected,createCaseFromSelected,resume};
}
