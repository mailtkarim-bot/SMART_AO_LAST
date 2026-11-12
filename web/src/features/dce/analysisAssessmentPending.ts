import type {AnalysisAssessmentInput} from "../../shared/types";

/** App-lifetime intent store: private bodies never enter browser storage. */
export class AnalysisAssessmentPendingStore {
 private snapshot:ReadonlyMap<string,AnalysisAssessmentInput>=new Map();
 private listeners=new Set<()=>void>();
 getSnapshot=()=>this.snapshot;
 subscribe=(listener:()=>void)=>{this.listeners.add(listener);return()=>{this.listeners.delete(listener);};};
 put(key:string,payload:AnalysisAssessmentInput){
  const existing=this.snapshot.get(key);
  if(existing&&JSON.stringify(existing)!==JSON.stringify(payload))throw new Error("PENDING_INTENT_CONFLICT");
  const next=new Map(this.snapshot);const copy=structuredClone(payload);if(copy.treatment){Object.freeze(copy.treatment.consequences);Object.freeze(copy.treatment);}next.set(key,Object.freeze(copy));this.snapshot=next;this.listeners.forEach(listener=>listener());
 }
 remove(key:string){const next=new Map(this.snapshot);next.delete(key);this.snapshot=next;this.listeners.forEach(listener=>listener());}
}
