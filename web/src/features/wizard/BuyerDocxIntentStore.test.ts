import {expect,test} from 'vitest';
import {BuyerDocxIntentStore} from './BuyerDocxIntentStore';
import type {BuyerDocxPending} from './BuyerDocxIntentStore';
test('keeps an uncertain native DOCX intent scoped, immutable and reusable',()=>{
 const store=new BuyerDocxIntentStore();const value={caseId:'case-a',packageId:'package-a',phase:'UNKNOWN',input:{command_id:'command-a',idempotency_key:'key-a',draft_id:'docx-a',expected_package_revision:7,source_response:{draft_id:'md-a',version:1,content_sha256:'a'.repeat(64)},template:{document_id:'template-a',dce_version_id:'version-a',sha256:'b'.repeat(64)},fields:[{locator:'p:3',expected_xml_sha256:'c'.repeat(64),requirement_id:'requirement-a',section_code:'METHOD'}]}} as BuyerDocxPending;
 store.put('owner-a/case-a',value);value.input.draft_id='changed';expect(store.getSnapshot().get('owner-a/case-a')?.input.draft_id).toBe('docx-a');expect(store.getSnapshot().get('owner-b/case-a')).toBeUndefined();expect(()=>store.put('owner-a/case-a',value)).toThrow('INTENT_CONFLICT');
});
