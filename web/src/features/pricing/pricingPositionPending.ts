import type { PositionReviewInput, PositionReviewReceipt } from "../../shared/types";
export type PositionPending = {
  caseId: string;
  batchId: string;
  positionId: string;
  intent: PositionReviewInput;
  phase: "SENDING" | "UNKNOWN" | "READ_REQUIRED" | "CONFLICT";
  receipt: PositionReviewReceipt | null;
  message: string;
};
/** App-lifetime recovery only; private commands never enter browser storage. */
export class PricingPositionPendingStore {
  private snapshot: ReadonlyMap<string, PositionPending> = new Map();
  private listeners = new Set<() => void>();
  getSnapshot = () => this.snapshot;
  subscribe = (fn: () => void) => {
    this.listeners.add(fn);
    return () => {
      this.listeners.delete(fn);
    };
  };
  put(key: string, value: PositionPending) {
    const old = this.snapshot.get(key);
    if (old && JSON.stringify(old.intent) !== JSON.stringify(value.intent)) throw Error("PENDING_INTENT_CONFLICT");
    const copy = structuredClone(value);
    copy.intent.cost_refs.forEach(Object.freeze);
    Object.freeze(copy.intent.cost_refs);
    Object.freeze(copy.intent);
    Object.freeze(copy);
    const next = new Map(this.snapshot);
    next.set(key, copy);
    this.snapshot = next;
    this.listeners.forEach(fn => fn());
  }
  remove(key: string) {
    const next = new Map(this.snapshot);
    next.delete(key);
    this.snapshot = next;
    this.listeners.forEach(fn => fn());
  }
}
