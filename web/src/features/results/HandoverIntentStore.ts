import type { AcknowledgeHandoverInput, RecordCaseHandoverInput } from "../../shared/types";
export type HandoverIntent = {
  kind: "PUBLISH";
  caseId: string;
  selected: string;
  input: RecordCaseHandoverInput;
} | {
  kind: "RECEIVE";
  caseId: string;
  snapshotId: string;
  input: AcknowledgeHandoverInput;
};
export type PendingHandover = {
  intent: HandoverIntent;
  phase: "SENDING" | "UNKNOWN" | "READ_REQUIRED" | "CONFLICT" | "REJECTED";
};
/** App-lifetime only: no private intent is persisted in browser storage. */
export class HandoverIntentStore {
  private snapshot: ReadonlyMap<string, PendingHandover> = new Map();
  private listeners = new Set<() => void>();
  getSnapshot = () => this.snapshot;
  subscribe = (listener: () => void) => {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  };
  put(key: string, value: PendingHandover) {
    const previous = this.snapshot.get(key);
    if (previous && JSON.stringify(previous.intent) !== JSON.stringify(value.intent)) throw Error("HANDOVER_INTENT_CONFLICT");
    const next = new Map(this.snapshot);
    next.set(key, structuredClone(value));
    this.snapshot = next;
    this.listeners.forEach(listener => listener());
  }
  remove(key: string) {
    const next = new Map(this.snapshot);
    next.delete(key);
    this.snapshot = next;
    this.listeners.forEach(listener => listener());
  }
}
