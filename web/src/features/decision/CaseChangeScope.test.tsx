import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { expect, test, vi } from 'vitest';
import type { ApiClient } from '../../infrastructure/api';
import type { CaseContractChangeEvent } from '../../shared/types';
import { CaseContractChangePanel } from './CaseContractChangePanel';
import { ChangeIntentStore } from './ChangeIntentStore';
const event = {
  event_id: 'e1',
  case_id: 'case-1',
  handover_snapshot_id: 'h1',
  summary: 'Note Direction privée',
  scope_note: 'Lot01',
  source_refs: [],
  evidence_refs: [],
  declared_instrument: null,
  applicability_state: 'UNKNOWN',
  applicability_history: [],
  actions: [],
  a1_engagements: [],
  a1_engagements_state: 'UNKNOWN',
  engagement_linkage_history: [],
  engagement_linkage_state: 'UNKNOWN',
  impact_declarations: [],
  action_impact_relations: [],
  action_execution_acts: [],
  evidence_objects: []
} as unknown as CaseContractChangeEvent;
function apiFor(events: CaseContractChangeEvent[] = []) {
  return {
    listCaseContractChangeEvents: vi.fn(async (caseId: string) => ({
      case_id: caseId,
      events: caseId === 'case-1' ? events : []
    })),
    listOperationalCaseContractChangeEvents: vi.fn(async (caseId: string) => ({
      case_id: caseId,
      events: [],
      truncated: false
    })),
    listCaseHandoverSnapshots: vi.fn(async (caseId: string) => ({
      case_id: caseId,
      items: caseId === 'case-1' ? [{
        snapshot_id: 'h1',
        revision: 1,
        lot_reference: '01',
        package_version: 1,
        manifest_sha256: 'a'.repeat(64),
        snapshot: {}
      }] : []
    })),
    recordCaseContractChangeEvent: vi.fn().mockRejectedValue(new Error('uncertain transport'))
  } as unknown as ApiClient;
}
test('role/session change masks private rows immediately and uses only the public reader', async () => {
  const api = apiFor([event]);
  const {
    rerender
  } = render(<CaseContractChangePanel api={api} caseId="case-1" ownerKey="patron-session" versions={[]} />);
  expect(await screen.findByText(/Note Direction privée/)).toBeInTheDocument();
  rerender(<CaseContractChangePanel api={api} caseId="case-1" ownerKey="driver-session" canManage={false} versions={[]} />);
  expect(screen.queryByText(/Note Direction privée/)).not.toBeInTheDocument();
  expect(await screen.findByText(/aucun changement opérationnel publié/)).toBeInTheDocument();
  expect(api.listCaseContractChangeEvents).toHaveBeenCalledOnce();
  expect(api.listOperationalCaseContractChangeEvents).toHaveBeenCalledOnce();
});
test('an UNKNOWN act survives leaving its case and retries exactly on return', async () => {
  const api = apiFor(),
    store = new ChangeIntentStore();
  const {
    rerender
  } = render(<CaseContractChangePanel api={api} caseId="case-1" ownerKey="patron" pendingStore={store} versions={[]} />);
  fireEvent.change(await screen.findByLabelText('Passation de départ'), {
    target: {
      value: 'h1'
    }
  });
  for (const [label, value] of [['Résumé déclaré', 'Instruction accès'], ['Périmètre/delta décrit, sans calcul automatique', 'Déviation lot01'], ['Références source, une par ligne', 'instruction://1'], ['Preuves de réception/événement, une par ligne', 'document://1'], ['Justification de cet acte', 'Instruction et références relues.']]) fireEvent.change(screen.getByLabelText(label), {
    target: {
      value
    }
  });
  fireEvent.click(screen.getByLabelText(/Je confirme cet acte/));
  fireEvent.click(screen.getByRole('button', {
    name: 'Enregistrer l’événement sourcé'
  }));
  expect(await screen.findByText('UNKNOWN · intention de changement figée')).toBeInTheDocument();
  rerender(<CaseContractChangePanel api={api} caseId="case-2" ownerKey="patron" pendingStore={store} versions={[]} />);
  expect(screen.queryByText('UNKNOWN · intention de changement figée')).not.toBeInTheDocument();
  rerender(<CaseContractChangePanel api={api} caseId="case-1" ownerKey="patron" pendingStore={store} versions={[]} />);
  expect(await screen.findByText('UNKNOWN · intention de changement figée')).toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', {
    name: 'Réessayer exactement cet acte'
  }));
  await waitFor(() => expect(api.recordCaseContractChangeEvent).toHaveBeenCalledTimes(2));
  const calls = vi.mocked(api.recordCaseContractChangeEvent).mock.calls;
  expect(calls[1]).toEqual(calls[0]);
});
