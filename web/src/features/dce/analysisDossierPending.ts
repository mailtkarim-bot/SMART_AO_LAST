import type {AnalysisDossierInput} from "../../shared/types";
/** Like point intents, review intents remain private and live only for the App lifetime. */
export class AnalysisDossierPendingStore {
 private snapshot:ReadonlyMap<string,AnalysisDossierInput>=new Map();private listeners=new Set<()=>void>();
 getSnapshot=()=>this.snapshot;
 subscribe=(listener:()=>void)=>{this.listeners.add(listener);return()=>{this.listeners.delete(listener);};};
 put(key:string,payload:AnalysisDossierInput){const old=this.snapshot.get(key);if(old&&JSON.stringify(old)!==JSON.stringify(payload))throw Error("PENDING_DOSSIER_CONFLICT");const copy=structuredClone(payload);copy.axes.forEach(Object.freeze);Object.freeze(copy.axes);const next=new Map(this.snapshot);next.set(key,Object.freeze(copy));this.snapshot=next;this.listeners.forEach(l=>l());}
 remove(key:string){const next=new Map(this.snapshot);next.delete(key);this.snapshot=next;this.listeners.forEach(l=>l());}
}
