import { render, screen } from '@testing-library/react';
import { expect, test, vi } from 'vitest';
import type { ApiClient } from '../../infrastructure/api';
import type { OperationalChangeView, StoredOperationalChangeContext } from '../../shared/types';
import { OperationalChangeRead } from './OperationalChangeRead';

const context: StoredOperationalChangeContext = {
  human_confirmed:true,publish:true,justification:'Source relue.',expected_view_sha256:'a'.repeat(64),
  point_ids:['point-v2'],handover_snapshot_id:'handover-v2',handover_revision:2,
  offer_manifest_sha256:'b'.repeat(64),recorded_at:'2026-11-02T10:00:00Z',
  points:[{point_id:'point-v2',kind:'ENGAGEMENT',statement:'Contrôle à organiser.',
    difference_state:'UNKNOWN',criticality:'CRITICAL'}]
};
const row: OperationalChangeView = {
  event_id:'event-v2',case_id:'case-1',summary:'Instruction à relire.',scope_note:'Lot 1.',
  change_kind:'CHANGE_REQUEST',lot_reference:'1',source_state:'CURRENT',source_reasons:[],
  operational_context:{...context,handover_snapshot_id:'origin-v1'},
  current_operational_context:context,legal_effect_state:'UNKNOWN',
  source_refs:['instruction://synthetic/v2'],evidence_refs:['piece://synthetic/declared'],
  applicability_history:[],actions:[{action_id:'action-v2',summary:'Faire relire.',source_state:'CURRENT',
    operational_details:{human_confirmed:true,publish:true,justification:'Action relue.',responsible:null,expected_evidence:null},due_at:null}],
  action_execution_acts:[],operational_timeline:[]
};

function apiFor(value: OperationalChangeView) {
  return {listOperationalCaseContractChangeEvents:vi.fn().mockResolvedValue({case_id:'case-1',events:[value],truncated:false})} as unknown as ApiClient;
}

test('shows the current exact handover and declared instruction sources, with missing fields visible',async()=>{
  render(<OperationalChangeRead api={apiFor(row)} caseId="case-1"/>);
  expect(await screen.findByText(/Passation source : handover-v2 · révision 2/)).toBeInTheDocument();
  expect(screen.getByText(new RegExp('Empreinte offre : '+ 'b'.repeat(64)))).toBeInTheDocument();
  expect(screen.getByText(/Instruction déclarée : instruction:\/\/synthetic\/v2/)).toBeInTheDocument();
  expect(screen.getByText(/Pièces référencées : piece:\/\/synthetic\/declared/)).toBeInTheDocument();
  expect(screen.getByText(/Responsable déclaré : UNKNOWN/)).toBeInTheDocument();
  expect(screen.getByText(/Preuve attendue : UNKNOWN/)).toBeInTheDocument();
});

test('legacy missing provenance stays UNKNOWN rather than displaying undefined',async()=>{
  const legacy=structuredClone(row);
  delete legacy.current_operational_context;
  delete legacy.operational_context.handover_revision;
  delete legacy.operational_context.offer_manifest_sha256;
  delete legacy.source_refs;
  delete legacy.evidence_refs;
  render(<OperationalChangeRead api={apiFor(legacy)} caseId="case-1"/>);
  expect(await screen.findByText(/Passation source : origin-v1 · révision UNKNOWN/)).toBeInTheDocument();
  expect(screen.getByText(/Empreinte offre : UNKNOWN/)).toBeInTheDocument();
  expect(screen.getByText(/Instruction déclarée : UNKNOWN/)).toBeInTheDocument();
  expect(screen.queryByText(/undefined/)).not.toBeInTheDocument();
});
