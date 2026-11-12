import {useCallback,useEffect,useRef,useState} from 'react';
import type {ApiClient} from '../../infrastructure/api';
import {ChangeConfirmedForm,type ChangeConsent} from '../decision/ChangeConfirmedForm';
import type {CashDeclaration,CashFlow,CashIntent,CashPendingStore,CashRevision,CashView} from './cashScheduleTypes';

const refs=(value:string)=>value.split('\n').map(v=>v.trim()).filter(Boolean);
const integer=(value:string):number|null=>{if(!value.trim())return null; if(!/^-?\d+$/.test(value))throw Error('Montant entier requis.'); const n=Number(value);if(!Number.isSafeInteger(n)||Math.abs(n)>9e15)throw Error('Montant hors limite.');return n;};
const minor=(value:string|null)=>value===null?'UNKNOWN':BigInt(value).toLocaleString('fr-FR');
type Props={api:ApiClient;caseId:string;ownerKey:string;scopeKey?:string;pendingStore?:CashPendingStore;sourceReadBlocked?:boolean};
export function CashSchedulePanel(props:Props){
 const [local]=useState<CashPendingStore>(()=>new Map());
 const scope=JSON.stringify([props.ownerKey,props.caseId]);
 if(props.sourceReadBlocked)return <section className="section-block scenario-creation" aria-label="Échéancier déclaré par Affaire"><h2>Trésorerie déclarée de l’Affaire</h2><p role="status">Sources en cours de reprise : échéancier suspendu jusqu’à la relecture du DCE. Aucun accord reconduit.</p></section>;
 return <CashWorkspace key={JSON.stringify([scope,props.scopeKey])} {...props} scope={scope} store={props.pendingStore??local}/>;
}
function CashWorkspace({api,caseId,scope,store}:{api:ApiClient;caseId:string;scope:string;store:CashPendingStore}){
 const [view,setView]=useState<CashView|null>(null),[notice,setNotice]=useState(''),[version,setVersion]=useState(0);
 const [pending,setPending]=useState<CashIntent|null>(()=>store.get(scope)??null);
 const live=useRef(true),intentRef=useRef(pending),sequence=useRef(0);
 const sourceView=useRef<string|null>(null);
 const reportSource=view?.sources.find(s=>s.financial_report)?.financial_report;
 const update=useCallback((next:CashIntent|null)=>{intentRef.current=next;if(next)store.set(scope,next);else store.delete(scope);if(live.current)setPending(next);},[scope,store]);
 const read=useCallback(async(receipt?:CashIntent)=>{
  const run=++sequence.current;
  try{const result=await api.getCashSchedule(caseId);if(!live.current||run!==sequence.current)return;
   if(result.case_id!==caseId)throw Error('Affaire discordante');
   if(receipt?.phase==='READ_REQUIRED'&&!result.history.some(r=>r.id===receipt.input.revision_id))throw Error('Reçu non retrouvé');
   if(sourceView.current!==null&&sourceView.current!==result.view_sha256)setVersion(v=>v+1);
   sourceView.current=result.view_sha256;
   setView(result);setNotice('');
   if(receipt){update(null);setVersion(v=>v+1);}
  }catch{if(live.current&&run===sequence.current){setView(null);setNotice('Échéancier indisponible : résultat à relire.');}}
 },[api,caseId,update]);
 useEffect(()=>{live.current=true;const old=store.get(scope);
  if(old?.phase==='UNKNOWN'||old?.phase==='SENDING')update({...old,phase:'UNKNOWN'});
  else void read(old??undefined);
  return()=>{live.current=false;};
 },[read,scope,store,update]);
 async function send(intent:CashIntent){
  if(intentRef.current?.phase==='SENDING')return;
  update({...intent,phase:'SENDING'});
  try{const receipt=await api.recordCashSchedule(caseId,intent.input);
   if(receipt.command_id!==intent.input.command_id||receipt.idempotency_key!==intent.input.idempotency_key||receipt.revision_id!==intent.input.revision_id||receipt.result_code!=='CASH_SCHEDULE_RECORDED')throw Error('Reçu discordant');
   const next={...intent,phase:'READ_REQUIRED' as const};update(next);if(live.current)await read(next);
  }catch(error){const e=error as {status?:number;detail?:string};
   if([401,403,404].includes(e.status??0)&&live.current)setView(null);
   if(intent.phase==='NEW'&&[400,401,403,404,422].includes(e.status??0)){update(null);if(live.current){setNotice('Déclaration refusée : corrigez et confirmez un nouvel acte.');setVersion(v=>v+1);}return;}
   const conflict=e.status===409&&['CASH_VIEW_CONFLICT','CASH_REVISION_CONFLICT'].includes(e.detail??'');
   const next={...intent,phase:conflict?'CONFLICT' as const:'UNKNOWN' as const};update(next);
   if(e.status===409&&live.current)await read(conflict?next:undefined);
  }
 }
 function record(declaration:CashDeclaration,consent:ChangeConsent){
  if(!view||intentRef.current)return;
  const input={case_id:caseId,command_id:crypto.randomUUID(),idempotency_key:crypto.randomUUID(),revision_id:crypto.randomUUID(),expected_revision:view.revision,expected_view_sha256:view.view_sha256,declaration,human_confirmed:true,justification:consent.justification};
  void send({input,phase:'NEW'});
 }
 return <section className="section-block scenario-creation" aria-label="Échéancier déclaré par Affaire">
  <h2>Trésorerie déclarée de l’Affaire</h2>
  <p>Flux et dates déclarés, par devise. Les cumuls portent sur vos seules hypothèses : ni liquidité, ni financement, ni date juridique certains. Périmètre partiel.</p>
  {notice&&<p role="alert">{notice}</p>}
  {pending&&<div role="status"><p>{pending.phase==='UNKNOWN'?'Résultat UNKNOWN : la déclaration est figée.':pending.phase==='READ_REQUIRED'?'Acte reçu : relecture exacte requise.':pending.phase==='SENDING'?'Enregistrement en cours.':'Conflit : relisez les sources.'}</p>
   {pending.phase==='UNKNOWN'&&<button className="secondary-button" onClick={()=>void send(pending)}>Réessayer la même déclaration</button>}
   {['READ_REQUIRED','CONFLICT'].includes(pending.phase)&&<button className="secondary-button" onClick={()=>void read(pending)}>Relire le résultat reçu</button>}
  </div>}
  {!pending&&<button className="secondary-button" onClick={()=>void read()}>Relire l’échéancier et ses sources</button>}
  {view&&<>
   {!view.current?<p>Aucun échéancier déclaré.</p>:<CashResult row={view.current}/>}
   {view.catalog_truncated&&<p role="alert">Liste des sources bornée : toutes les sources natives ne sont pas proposées.</p>}
   {reportSource&&<p style={{overflowWrap:"anywhere"}}>Rapport publié proposé : {reportSource.report_id} · révision {reportSource.revision} · {reportSource.state}. Date de flux et solde initial restent des déclarations humaines ; aucun paiement certain déduit.</p>}
   <CashEditor key={`declaration:${version}`} view={view} locked={!!pending} onRecord={record} onError={setNotice}/>
   {view.current?.declaration.status==='ACTIVE'&&<ChangeConfirmedForm key={`cancellation:${version}`} className="workflow-form" onSubmit={event=>event.preventDefault()} aria-label="Annuler la déclaration" locked={!!pending} onApprove={consent=>record({...view.current!.declaration,status:'CANCELLED',flows:[],openings:[]},consent)}><button>Enregistrer une annulation déclarée</button></ChangeConfirmedForm>}
   <details><summary>Historique des déclarations</summary>{view.history.map(row=><CashResult key={row.id} row={row}/>)}{view.history_truncated&&<p>50 dernières révisions affichées ; historique antérieur conservé.</p>}</details>
  </>}
 </section>;
}
function CashResult({row}:{row:CashRevision}){
 return <article className="detail-panel" style={{overflowWrap:"anywhere"}}><h3>Révision {row.revision} · {row.declaration.status==='CANCELLED'?'Annulation déclarée':'Flux déclarés'}</h3>
  <p>Contexte : {row.context_state} · {row.declaration.period_start} → {row.declaration.period_end} · {row.created_at}</p>
  <p>Hypothèses : {row.declaration.assumptions}</p><p>Justification : {row.justification}</p>
  <p>Source DCE : {row.source_snapshot.case_source.dce_version_id??'UNKNOWN'}. Sources référencées, validité externe non vérifiée.</p>
  {row.context_state==='REVIEW_REQUIRED'&&<p role="alert">Source changée : relisez et confirmez une nouvelle révision. Les cumuls courants sont indisponibles.</p>}
  {row.projection.currencies.map(group=><div key={group.currency_code}><h4>{group.currency_code} · unités monétaires mineures</h4><p>Solde de départ déclaré : {minor(group.opening_minor)} · Cumul déclaré : {minor(group.closing_minor)}</p>
   {!!group.missing.length&&<p role="alert">Manques : {group.missing.map(m=>m.startsWith('OPENING')?'solde de départ':m.startsWith('DATE')?'date de flux':'montant de flux').join(', ')}. Aucun zéro déduit.</p>}
   <ul>{group.rows.map(flow=><li key={flow.flow_id}>{flow.declared_date??'Date UNKNOWN'} · {flow.direction==='INFLOW'?'Entrée':'Sortie'} : {minor(flow.amount_minor)} · Cumul : {minor(flow.cumulative_minor)}<p>Sources : {flow.source_refs.join(' ; ')}{flow.native_source_id?` · ${flow.native_source_id}`:''}</p></li>)}</ul>
  </div>)}<p>Complétude : PARTIAL · Solde réel et financement : UNKNOWN.</p>
  {Object.values(row.source_snapshot.source_details??{}).filter(source=>source.financial_report).map(source=><p key={source.id}>Rapport source enregistré : {source.financial_report!.report_id} · révision {source.financial_report!.revision} · {source.financial_report!.state} · source {source.id}</p>)}
  {!row.source_snapshot.source_details&&row.declaration.flows.some(flow=>flow.native_source_id?.startsWith('LINE:'))&&<p>Version du rapport source enregistré : UNKNOWN dans cette ancienne déclaration. Aucun enrichissement rétroactif.</p>}
  <details><summary>Empreintes des sources natives sélectionnées</summary>{Object.entries(row.source_snapshot.sources).map(([id,hash])=><p key={id}>{id} · {hash}</p>)}</details>
 </article>;
}
function CashEditor({view,locked,onRecord,onError}:{view:CashView;locked:boolean;onRecord:(d:CashDeclaration,c:ChangeConsent)=>void;onError:(s:string)=>void}){
 const initial=view.current?.declaration;
 const [flowIds,setFlows]=useState(()=>initial?.flows.map(f=>f.flow_id)??[]);
 const [openingCount,setOpenings]=useState(()=>initial?.openings.length??0);
 const form=useRef<HTMLFormElement>(null);
 const approve=(consent:ChangeConsent)=>{
  if(!form.current)return; const data=new FormData(form.current);const text=(key:string)=>String(data.get(key)??'').trim();
  try{const flows=flowIds.map((id,i):CashFlow=>({flow_id:id,direction:text(`direction${i}`) as CashFlow['direction'],currency_code:text(`currency${i}`),amount_minor:integer(text(`amount${i}`)),declared_date:text(`date${i}`)||null,source_refs:refs(text(`sources${i}`)),native_source_id:text(`native${i}`)||null}));
   onRecord({period_start:text('start'),period_end:text('end'),status:'ACTIVE',assumptions:text('assumptions'),flows,openings:Array.from({length:openingCount},(_,i)=>({currency_code:text(`openingCurrency${i}`),amount_minor:integer(text(`opening${i}`)),source_refs:refs(text(`openingSource${i}`))}))},consent);
  }catch(e){onError((e as Error).message);}
 };
 return <ChangeConfirmedForm className="workflow-form" onSubmit={event=>event.preventDefault()} aria-label="Déclarer l’échéancier" ref={form} locked={locked} onApprove={approve}><fieldset disabled={locked}>
  <h3>Nouvelle révision déclarée</h3>
  <label>Début de période<input name="start" type="date" required defaultValue={initial?.period_start}/></label>
  <label>Fin de période<input name="end" type="date" required defaultValue={initial?.period_end}/></label>
  <label>Hypothèses et limites<textarea name="assumptions" required maxLength={4000} defaultValue={initial?.assumptions}/></label>
  <p>Solde initial absent = UNKNOWN. Montants entiers en unités mineures ; aucune conversion entre devises.</p>
  {Array.from({length:openingCount},(_,i)=><fieldset key={i}><legend>Solde de départ {i+1}</legend><label>Devise du solde {i+1}<input name={`openingCurrency${i}`} required pattern="[A-Z]{3}" defaultValue={initial?.openings[i]?.currency_code??'EUR'}/></label><label>Solde de départ {i+1} (vide = UNKNOWN)<input name={`opening${i}`} inputMode="numeric" defaultValue={initial?.openings[i]?.amount_minor??''}/></label><label>Sources du solde {i+1}<textarea name={`openingSource${i}`} required defaultValue={initial?.openings[i]?.source_refs.join('\n')}/></label></fieldset>)}
  <button className="secondary-button" type="button" disabled={locked||openingCount===0} onClick={()=>{const confirm=form.current?.elements.namedItem('change_human_confirmed') as HTMLInputElement;if(confirm?.checked)confirm.click();setOpenings(n=>n-1);}}>Retirer le dernier solde de départ</button>
  <button className="secondary-button" type="button" disabled={locked||openingCount>=8} onClick={()=>setOpenings(n=>n+1)}>Ajouter un solde de départ</button>
  {flowIds.map((id,i)=>{const old=initial?.flows.find(f=>f.flow_id===id);return <fieldset key={id}><legend>Flux {i+1}</legend>
   <label>Source native du flux {i+1}<select name={`native${i}`} defaultValue={old?.native_source_id??''} onChange={event=>{const source=view.sources.find(s=>s.id===event.target.value);if(!source||!form.current)return;for(const [key,value]of Object.entries({direction:source.direction,currency:source.currency_code,amount:String(source.amount_minor),sources:source.source_refs.join('\n'),date:source.declared_date??''})){const el=form.current.elements.namedItem(`${key}${i}`) as HTMLInputElement;el.value=value;}}}><option value="">Déclaration manuelle sourcée</option>{old?.native_source_id&&!view.sources.some(s=>s.id===old.native_source_id)&&<option value={old.native_source_id}>Ancienne source indisponible — nouveau choix requis</option>}{view.sources.map(source=><option key={source.id} value={source.id}>{source.label}</option>)}</select></label>
   <label>Sens du flux {i+1}<select name={`direction${i}`} defaultValue={old?.direction??'OUTFLOW'}><option value="OUTFLOW">Sortie</option><option value="INFLOW">Entrée</option></select></label>
   <label>Devise du flux {i+1}<input name={`currency${i}`} required pattern="[A-Z]{3}" defaultValue={old?.currency_code??'EUR'}/></label>
   <label>Montant du flux {i+1} (vide = UNKNOWN)<input name={`amount${i}`} inputMode="numeric" defaultValue={old?.amount_minor??''}/></label>
   <label>Date déclarée du flux {i+1}<input name={`date${i}`} type="date" defaultValue={old?.declared_date??''}/></label>
   <label>Sources du flux {i+1}<textarea name={`sources${i}`} required defaultValue={old?.source_refs.join('\n')}/></label>
   <button className="secondary-button" type="button" onClick={()=>{const confirm=form.current?.elements.namedItem('change_human_confirmed') as HTMLInputElement;if(confirm?.checked)confirm.click();setFlows(ids=>ids.filter(value=>value!==id));}}>Retirer le flux {i+1}</button>
  </fieldset>;})}
  <button className="secondary-button" type="button" disabled={locked||flowIds.length>=120} onClick={()=>setFlows(rows=>[...rows,crypto.randomUUID()])}>Ajouter un flux</button>
  <button className="secondary-button" disabled={locked}>Enregistrer la révision déclarée</button>
 </fieldset></ChangeConfirmedForm>;
}
