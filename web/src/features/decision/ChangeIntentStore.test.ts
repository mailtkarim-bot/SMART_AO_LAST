import { expect, test } from 'vitest';
import { ChangeIntentStore } from './ChangeIntentStore';
import type { PendingIntent } from './CaseContractChangePanel';
test('keeps the original body immutable in its original owner/case scope', () => {
  const store = new ChangeIntentStore();
  const input = {
    command_id: 'cmd',
    idempotency_key: 'key',
    event_id: 'event',
    source_refs: ['source']
  } as unknown as PendingIntent['input'];
  store.update('owner-a/case-a', {
    pending: {
      caseId: 'case-a',
      key: 'event',
      input,
      phase: 'UNKNOWN'
    }
  });
  (input as {
    command_id: string;
  }).command_id = 'changed';
  expect(store.getSnapshot().get('owner-a/case-a')?.pending?.input.command_id).toBe('cmd');
  expect(store.getSnapshot().get('owner-b/case-a')).toBeUndefined();
});
