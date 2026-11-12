import {fireEvent,render,screen,waitFor} from '@testing-library/react';
import {expect,test,vi} from 'vitest';
import {BuyerDocxForm} from './BuyerDocxForm';
import {BuyerDocxIntentStore} from './BuyerDocxIntentStore';
import type {ApiClient} from '../../infrastructure/api';
import type {BuyerDocxFieldMapping} from '../../shared/types';

const source={draft_id:'md-1',version:1,content_sha256:'a'.repeat(64)};
const template={document_id:'template-1',dce_version_id:'dce-1',sha256:'b'.repeat(64)};
const inputs={package_id:'pkg-1',package_revision:7,source_response:source,truncated:false,
 contributions:[{requirement_id:'req-1',section_code:'METHOD',text:'Ne pas intervenir sans validation.',missing:'Date UNKNOWN',start_byte:0,end_byte:20,raw_sha256:'c'.repeat(64)}],
 templates:[{template,filename:'cadre.docx',state:'CANDIDATE',reason:null,regions:[{locator:'p:3',xml_sha256:'d'.repeat(64),text:'[[REPONSE:METHODE]]'},{locator:'p:4',xml_sha256:'e'.repeat(64),text:'[[REPONSE:INCONNU]]'}]}]};
test.each([new Error('lost after commit'),Object.assign(new Error('busy'),{status:409,detail:'LOCK_BUSY'}),Object.assign(new Error('timeout'),{status:408}),Object.assign(new Error('rate limited'),{status:429})])('freezes exact template, source and anchor mappings through UNKNOWN and navigation: %s',async(failure)=>{
 const create=vi.fn().mockRejectedValueOnce(failure).mockImplementationOnce(async(_pkg,input)=>({status:'SUCCEEDED',command_id:input.command_id,idempotency_key:input.idempotency_key,result_code:'BUYER_DOCX_RESPONSE_DRAFT_CREATED',aggregate_refs:[{aggregate_type:'TechnicalResponseDraft',aggregate_id:input.draft_id,aggregate_revision:1}],event_ids:[],replayed:true}));
 const api={inspectBuyerDocxInputs:vi.fn().mockResolvedValue(inputs),createBuyerDocxResponseDraft:create,
  getCollaboratorPreparation:vi.fn().mockImplementation(async()=>({package_id:'pkg-1',case_id:'case-1',dce_version_id:'dce-1',response_drafts:[{draft_id:create.mock.calls[0][1].draft_id,version:1,content_sha256:'f'.repeat(64),content_format:'DOCX',content:'texte',content_provenance:{source_response:{content_sha256:source.content_sha256,version:source.version,draft_id:source.draft_id},template:{sha256:template.sha256,dce_version_id:template.dce_version_id,document_id:template.document_id},fields:create.mock.calls[0][1].fields.map((f:BuyerDocxFieldMapping)=>({section_code:f.section_code,requirement_id:f.requirement_id,expected_xml_sha256:f.expected_xml_sha256,locator:f.locator}))}}]}))} as unknown as ApiClient;
 const store=new BuyerDocxIntentStore();const recorded=vi.fn();const props={api,store,ownerKey:'owner-a',caseId:'case-1',packageId:'pkg-1',source,onRecorded:recorded};
 const view=render(<BuyerDocxForm {...props}/>);
 fireEvent.click(screen.getByRole('button',{name:'Lire les cadres DOCX'}));
 await screen.findByLabelText('Cadre acheteur DOCX');
 fireEvent.change(screen.getByLabelText('Cadre acheteur DOCX'),{target:{value:'template-1'}});
 fireEvent.change(screen.getByLabelText('Contribution pour p:3'),{target:{value:'req-1/METHOD'}});
 fireEvent.click(screen.getByLabelText(/Je confirme les régions/));
 fireEvent.click(screen.getByRole('button',{name:'Créer le brouillon DOCX'}));
 await screen.findAllByText(/Résultat DOCX UNKNOWN/);
 const first=structuredClone(create.mock.calls[0][1]);expect(first.source_response).toEqual(source);expect(first.template).toEqual(template);expect(first.fields).toHaveLength(1);expect(first.fields[0].locator).toBe('p:3');
 view.rerender(<BuyerDocxForm {...props} caseId="case-2"/>);expect(screen.queryAllByText(/Résultat DOCX UNKNOWN/)).toHaveLength(0);
 view.rerender(<BuyerDocxForm {...props}/>);await screen.findAllByText(/Résultat DOCX UNKNOWN/);
 fireEvent.click(screen.getByRole('button',{name:'Rejouer le même remplissage'}));
 await waitFor(()=>expect(recorded).toHaveBeenCalledOnce());expect(create.mock.calls[1]).toEqual(create.mock.calls[0]);
});

test('a receipt permits only guarded readback, never a second POST',async()=>{
 const store=new BuyerDocxIntentStore();const input={command_id:'cmd',idempotency_key:'idem',draft_id:'docx',expected_package_revision:7,source_response:source,template,fields:[{locator:'p:3',expected_xml_sha256:'d'.repeat(64),requirement_id:'req-1',section_code:'METHOD' as const}]};
 const receipt={status:'SUCCEEDED' as const,command_id:'cmd',idempotency_key:'idem',result_code:'BUYER_DOCX_RESPONSE_DRAFT_CREATED',aggregate_refs:[{aggregate_type:'TechnicalResponseDraft',aggregate_id:'docx',aggregate_revision:1}],event_ids:[],replayed:false};
 store.put(JSON.stringify(['owner-a','case-1','pkg-1']),{caseId:'case-1',packageId:'pkg-1',input,phase:'READ_REQUIRED',receipt});
 const read=vi.fn().mockRejectedValueOnce(new Error('read lost')).mockResolvedValue({case_id:'case-1',package_id:'pkg-1',dce_version_id:'dce-1',response_drafts:[{draft_id:'docx',version:1,content_format:'DOCX',content:'text',content_sha256:'f'.repeat(64),content_provenance:{source_response:source,template,fields:input.fields}}]});
 const post=vi.fn(),recorded=vi.fn();const api={getCollaboratorPreparation:read,createBuyerDocxResponseDraft:post} as unknown as ApiClient;
 render(<BuyerDocxForm api={api} store={store} ownerKey="owner-a" caseId="case-1" packageId="pkg-1" source={source} onRecorded={recorded}/>);
 fireEvent.click(screen.getByRole('button',{name:'Relire le DOCX enregistré'}));await screen.findByText(/Aucun nouveau POST/);
 fireEvent.click(screen.getByRole('button',{name:'Relire le DOCX enregistré'}));await waitFor(()=>expect(recorded).toHaveBeenCalledOnce());expect(read).toHaveBeenCalledTimes(2);expect(post).not.toHaveBeenCalled();
});
