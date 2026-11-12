import {useEffect,useLayoutEffect,useRef,useState} from 'react';
import type {ApiClient} from '../../infrastructure/api';
import type {TechnicalResponseDraft} from '../../shared/types';
type Props={api:ApiClient;scopeKey:string;packageId:string;draft:Pick<TechnicalResponseDraft,'draft_id'|'version'|'content_format'|'content_sha256'>;collaborator?:boolean};
export function ResponseDraftDownload({api,scopeKey,packageId,draft,collaborator=false}:Props){
 const key=JSON.stringify([scopeKey,packageId,draft.draft_id,draft.version,draft.content_sha256]);
 const latest=useRef({key,api});const alive=useRef(true);
 useLayoutEffect(()=>{latest.current={key,api}});useEffect(()=>{alive.current=true;return()=>{alive.current=false}},[]);
 const[busy,setBusy]=useState(false),[notice,setNotice]=useState<{key:string;text:string}|null>(null);
 async function download(){
  if(!draft.content_sha256)return;setBusy(true);const current=()=>alive.current&&latest.current.key===key&&latest.current.api===api;
  try{const blob=await api.downloadResponseDraft(packageId,draft.draft_id,draft.version,collaborator);if(!current())return;
   if(blob.size>5*1024*1024)throw Error('Pièce trop volumineuse · UNKNOWN.');
   const bytes=await blob.arrayBuffer();const sha=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');if(!current())return;
   if(sha!==draft.content_sha256)throw Error('SHA-256 discordant : téléchargement refusé.');
   const url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download=`reponse-v${draft.version}.${draft.content_format==='DOCX'?'docx':'md'}`;link.click();URL.revokeObjectURL(url);
   setNotice({key,text:'Fichier exact téléchargé; empreinte vérifiée. Aucune revue déduite.'});
  }catch(error){if(current())setNotice({key,text:error instanceof Error?error.message:'Pièce non relue · UNKNOWN.'})}finally{if(current())setBusy(false)}
 }
 return <div><button type="button" className="secondary-button" disabled={busy||!draft.content_sha256} onClick={()=>void download()}>Télécharger la pièce exacte</button>{notice?.key===key&&<p role="status">{notice.text}</p>}</div>;
}
