import type { PendingIntent, EvidenceUploadIntent } from './CaseContractChangePanel';
import type { RecordCaseContractChangeExternalConfirmationInput } from '../../shared/types';
export type ChangePendingCache = {
  pending: PendingIntent | null;
  uploads: Record<string, EvidenceUploadIntent>;
  confirmations: Record<string, {
    upload: EvidenceUploadIntent;
    confirmation: RecordCaseContractChangeExternalConfirmationInput;
  }>;
};
export class ChangeIntentStore {
  private snapshot: ReadonlyMap<string, ChangePendingCache> = new Map();
  private listeners = new Set<() => void>();
  getSnapshot = () => this.snapshot;
  subscribe = (listener: () => void) => {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  };
  update(key: string, patch: Partial<ChangePendingCache>) {
    const before = this.snapshot.get(key) ?? {
      pending: null,
      uploads: {},
      confirmations: {}
    };
    if (before.pending && patch.pending && JSON.stringify(before.pending.input) !== JSON.stringify(patch.pending.input)) throw Error('CHANGE_INTENT_CONFLICT');
    const safe = {
      ...patch
    };
    if (safe.pending) safe.pending = {
      ...safe.pending,
      input: structuredClone(safe.pending.input)
    };
    const next = new Map(this.snapshot);
    next.set(key, {
      ...before,
      ...safe
    });
    this.snapshot = next;
    this.listeners.forEach(fn => fn());
  }
}
