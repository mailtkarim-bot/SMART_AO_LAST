import {useEffect,useLayoutEffect,useRef,useState,useSyncExternalStore} from 'react';
import type {ApiClient} from '../../infrastructure/api';
import type {BuyerDocxInputs,CreateBuyerDocxResponseDraftInput,SelectedResponseDraft,CommandReceipt} from '../../shared/types';
import {BuyerDocxIntentStore} from './BuyerDocxIntentStore';
import type {BuyerDocxPending} from './BuyerDocxIntentStore';

type Props={api:ApiClient;store:BuyerDocxIntentStore;ownerKey:string;caseId:string;packageId:string;source:SelectedResponseDraft|null;onRecorded:()=>void|Promise<void>};
function same(a:unknown,b:unknown):boolean {
 if(a===b)return true;
 if(a===null||b===null||typeof a!=='object'||typeof b!=='object'||Array.isArray(a)!==Array.isArray(b))return false;
 const left=a as Record<string,unknown>,right=b as Record<string,unknown>;
 const keys=Object.keys(left);
 return keys.length===Object.keys(right).length&&keys.every(key=>Object.hasOwn(right,key)&&same(left[key],right[key]));
}
export function BuyerDocxForm({api,store,ownerKey,caseId,packageId,source,onRecorded}:Props){
 const key=JSON.stringify([ownerKey,caseId,packageId]);
 const sourceKey=JSON.stringify(source);
 const latest=useRef({key,post:api.createBuyerDocxResponseDraft});
 const alive=useRef(true);
 useLayoutEffect(()=>{latest.current={key,post:api.createBuyerDocxResponseDraft}});
 useEffect(()=>{alive.current=true;return()=>{alive.current=false}},[]);
 const current=()=>alive.current&&latest.current.key===key&&(ownerKey!==''||latest.current.post===api.createBuyerDocxResponseDraft);
 const pending=useSyncExternalStore(store.subscribe,store.getSnapshot).get(key);
 const [loaded,setLoaded]=useState<{key:string;source:string;data:BuyerDocxInputs}|null>(null);
 const [selection,setSelection]=useState<{key:string;source:string;template:string;values:Record<string,string>;confirmed:boolean}>({key:'',source:'',template:'',values:{},confirmed:false});
 const [notice,setNotice]=useState<{key:string;text:string}|null>(null);
 const [reading,setReading]=useState(false);
 const readSequence=useRef(0);
 const data=loaded?.key===key&&loaded.source===sourceKey?loaded.data:null;
 const draft=selection.key===key&&selection.source===sourceKey?selection:{template:'',values:{} as Record<string,string>,confirmed:false};
 const template=data?.templates.find(t=>t.template.document_id===draft.template&&t.state==='CANDIDATE');
 const locked=Boolean(pending)||reading;
 function update(patch:Partial<typeof selection>){setSelection({key,source:sourceKey,...draft,...patch})}
 async function inspect(){
  if(!source||pending)return;const request=++readSequence.current;setReading(true);
  try{const result=await api.inspectBuyerDocxInputs(packageId,source);
   if(!current()||request!==readSequence.current)return;
   if(result.package_id!==packageId||!same(result.source_response,source))throw Error('BUYER_DOCX_INPUT_CONTEXT_UNKNOWN');
   setLoaded({key,source:sourceKey,data:result});setSelection({key,source:sourceKey,template:'',values:{},confirmed:false});setNotice(null);
  }catch(error){if(current())setNotice({key,text:error instanceof Error?error.message:'Cadre non relu · UNKNOWN.'})}
  finally{if(current())setReading(false)}
 }
 async function readback(value:BuyerDocxPending){
  const result=await api.getCollaboratorPreparation(packageId);
  if(!current())return;
  const revision=value.receipt?.aggregate_refs.find(r=>r.aggregate_type==='TechnicalResponseDraft'&&r.aggregate_id===value.input.draft_id)?.aggregate_revision;
  const output=result.response_drafts.find(d=>d.draft_id===value.input.draft_id&&d.version===revision);
  if(result.case_id!==caseId||result.package_id!==packageId||result.dce_version_id!==value.input.template.dce_version_id
   ||!output||output.content_format!=='DOCX'||!output.content||!/^[a-f0-9]{64}$/.test(output.content_sha256??'')
   ||!same(output.content_provenance?.source_response,value.input.source_response)||!same(output.content_provenance?.template,value.input.template)
   ||!same(output.content_provenance?.fields,value.input.fields))throw Error('BUYER_DOCX_READBACK_UNKNOWN');
  store.remove(key);setLoaded(null);setNotice({key,text:`DOCX enregistré v${output.version} · SHA-256 ${output.content_sha256}. Revue Patron de cette pièce exacte requise.`});await onRecorded();
 }
 function validReceipt(receipt:CommandReceipt,input:CreateBuyerDocxResponseDraftInput){return receipt.command_id===input.command_id&&receipt.idempotency_key===input.idempotency_key
  &&receipt.result_code==='BUYER_DOCX_RESPONSE_DRAFT_CREATED'&&receipt.aggregate_refs.some(r=>r.aggregate_type==='TechnicalResponseDraft'&&r.aggregate_id===input.draft_id)}
 async function send(value:BuyerDocxPending){
  if(value.phase==='READ_REQUIRED'){try{await readback(value)}catch{if(current())setNotice({key,text:'Reçu DOCX obtenu; relecture indisponible · UNKNOWN. Aucun nouveau POST.'})}return}
  store.put(key,{...value,phase:'SENDING'});
  try{const receipt=await api.createBuyerDocxResponseDraft(packageId,value.input);
   if(!validReceipt(receipt,value.input))throw Error('BUYER_DOCX_RECEIPT_UNKNOWN');
   const received={...value,phase:'READ_REQUIRED' as const,receipt};store.put(key,received);
   if(current())await readback(received);
  }catch(error){
   const stored=store.getSnapshot().get(key);if(!stored)return;
   if(stored.phase==='READ_REQUIRED'){if(current())setNotice({key,text:'Reçu DOCX obtenu; relecture indisponible · UNKNOWN. Aucun nouveau POST.'});return}
   const status=(error as {status?:number})?.status,detail=(error as {detail?:string})?.detail;
   const terminal=[400,401,403,404,405,422].includes(status??0)||(status===409&&detail==='VERSION_CONFLICT');
   if(terminal&&current()){
    try{const result=await api.getCollaboratorPreparation(packageId);if(!current())return;
     if(result.case_id!==caseId||result.package_id!==packageId)throw new Error('context',{cause:error});
     store.remove(key);setLoaded(null);setNotice({key,text:'Remplissage refusé, package relu. Relisez les cadres avant une nouvelle intention.'});await onRecorded();return;
    }catch{/* Keep the original intent until its refusal can be reconciled in this scope. */}
   }
   store.put(key,{...value,phase:'UNKNOWN'});
   if(current())setNotice({key,text:'Résultat DOCX UNKNOWN : rejouez le même remplissage, avec les mêmes régions et identifiants.'});
  }
 }
 function create(){
  if(pending||!source||!data||!template||!draft.confirmed)return;
  const fields=template.regions.flatMap(region=>{const selected=data.contributions.find(c=>`${c.requirement_id}/${c.section_code}`===draft.values[region.locator]);return selected?[{locator:region.locator,expected_xml_sha256:region.xml_sha256,requirement_id:selected.requirement_id,section_code:selected.section_code}]:[]});
  if(!fields.length)return;
  const input={command_id:crypto.randomUUID(),idempotency_key:crypto.randomUUID(),draft_id:crypto.randomUUID(),expected_package_revision:data.package_revision,
   source_response:structuredClone(source),template:structuredClone(template.template),fields};
  void send({caseId,packageId,input,phase:'SENDING'});
 }
 const mappingsReady=Boolean(template?.regions.some(r=>draft.values[r.locator]));
 return <section className="response-plan" aria-label="Remplissage du cadre acheteur DOCX">
  <h4>Cadre acheteur DOCX</h4><p>Seuls les paragraphes/cellules dédiés sont remplis. Toute région sans contribution reste UNKNOWN. Le DOCX doit être revu séparément.</p>
  {notice?.key===key&&<p role="status">{notice.text}</p>}
  {pending&&<div><p>Résultat DOCX {pending.phase==='SENDING'?'en cours':pending.phase==='READ_REQUIRED'?'à relire':'UNKNOWN'} · source {pending.input.source_response.draft_id} v{pending.input.source_response.version} · SHA-256 {pending.input.source_response.content_sha256}</p>
   <button type="button" className="secondary-button" disabled={pending.phase==='SENDING'} onClick={()=>void send(pending)}>{pending.phase==='READ_REQUIRED'?'Relire le DOCX enregistré':'Rejouer le même remplissage'}</button></div>}
  {!source&&!pending&&<p>Choisissez un assemblage Markdown revu pour lire ses cadres · UNKNOWN.</p>}
  <button type="button" className="secondary-button" disabled={!source||locked} onClick={()=>void inspect()}>Lire les cadres DOCX</button>
  {data&&<fieldset disabled={locked} style={{minWidth:0,overflowWrap:'anywhere'}}><legend>Régions et contributions exactes</legend>
   {data.truncated&&<p>Cadres supplémentaires non projetés · UNKNOWN.</p>}
   <label>Cadre acheteur DOCX<select value={draft.template} onChange={e=>update({template:e.target.value,values:{},confirmed:false})}><option value="">Choisir le cadre…</option>{data.templates.map(t=><option key={t.template.document_id} value={t.template.document_id} disabled={t.state!=='CANDIDATE'}>{t.filename} · {t.state} {t.reason??''}</option>)}</select></label>
   {template&&<><small>Version DCE {template.template.dce_version_id} · SHA-256 {template.template.sha256}</small>
    {template.regions.map(region=><div key={region.locator} className="response-plan-item"><strong>{region.locator} · {region.text}</strong><small>SHA-256 région : {region.xml_sha256}</small>
     <label>Contribution pour {region.locator}<select value={draft.values[region.locator]??''} onChange={e=>update({values:{...draft.values,[region.locator]:e.target.value},confirmed:false})}><option value="">Laisser UNKNOWN</option>{data.contributions.map(c=><option key={`${c.requirement_id}/${c.section_code}`} value={`${c.requirement_id}/${c.section_code}`}>{c.section_code} · {c.requirement_id}</option>)}</select></label>
     <p>{data.contributions.find(c=>`${c.requirement_id}/${c.section_code}`===draft.values[region.locator])?.text??'UNKNOWN — contribution non renseignée.'}</p></div>)}
    <label><input type="checkbox" checked={draft.confirmed} onChange={e=>update({confirmed:e.target.checked})}/>Je confirme les régions, les contributions choisies et les champs UNKNOWN.</label></>}
   <button type="button" className="secondary-button" disabled={!template||!mappingsReady||!draft.confirmed} onClick={create}>Créer le brouillon DOCX</button>
  </fieldset>}
 </section>;
}
