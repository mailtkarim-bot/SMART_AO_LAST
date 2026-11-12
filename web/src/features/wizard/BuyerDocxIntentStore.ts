import type {CreateBuyerDocxResponseDraftInput,CommandReceipt} from '../../shared/types';
export type BuyerDocxPending = {packageId:string;caseId:string;input:CreateBuyerDocxResponseDraftInput;phase:'SENDING'|'UNKNOWN'|'READ_REQUIRED';receipt?:CommandReceipt};
/** Only app-lifetime memory: changing the view never changes an uncertain intent. */
export class BuyerDocxIntentStore {
 private values:ReadonlyMap<string,BuyerDocxPending>=new Map();
 private listeners=new Set<()=>void>();
 getSnapshot=()=>this.values;
 subscribe=(listener:()=>void)=>{this.listeners.add(listener);return()=>{this.listeners.delete(listener)}};
 put(key:string,value:BuyerDocxPending){const prior=this.values.get(key);if(prior&&JSON.stringify(prior.input)!==JSON.stringify(value.input))throw Error('BUYER_DOCX_INTENT_CONFLICT');this.values=new Map(this.values).set(key,structuredClone(value));this.listeners.forEach(f=>f())}
 remove(key:string){const next=new Map(this.values);next.delete(key);this.values=next;this.listeners.forEach(f=>f())}
}
