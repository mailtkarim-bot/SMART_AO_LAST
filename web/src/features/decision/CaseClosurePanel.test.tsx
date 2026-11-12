import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { expect, test, vi } from 'vitest';
import { CaseClosurePanel } from './CaseClosurePanel';
import type { ApiClient } from '../../infrastructure/api';
const dossier = (id: string) => ({
  case_id: id,
  dossier_sha256: 'a'.repeat(64),
  dce_version_id: null,
  acts: [],
  obligations: [],
  cycles: [],
  facts: [],
  rex: [],
  interviews: [],
  reuse_history: [],
  contract_replacements: [],
  open_obligation_ids: [],
  financial_observations: {
    collection_state: 'UNKNOWN',
    settlement_state: 'UNKNOWN',
    comparisons: []
  },
  legal_effect_state: 'UNKNOWN',
  external_receipt_state: 'UNKNOWN',
  completeness_state: 'REVIEW_REQUIRED',
  case_source: {}
});
test('requires a precise confirmed declaration and freezes identical retry after UNKNOWN', async () => {
  const post = vi.fn().mockRejectedValueOnce(Error('timeout')).mockImplementation(async (_id, _op, body) => ({
    command_id: body.command_id,
    idempotency_key: body.idempotency_key,
    act_id: body.act_id,
    result_code: 'CONTRACT_EXECUTION_EVIDENCE_RECORDED',
    replayed: true
  }));
  const api = {
    getCaseClosure: vi.fn(async id => dossier(id)),
    recordClosureOperation: post
  } as unknown as ApiClient;
  render(<CaseClosurePanel api={api} caseId="a" ownerKey="session1" />);
  await screen.findByText('Aucune réception déclarée.');
  fireEvent.change(screen.getByLabelText('Résumé de réception'), {
    target: {
      value: 'Réception déclarée avec réserve'
    }
  });
  fireEvent.change(screen.getByLabelText('Sources de réception'), {
    target: {
      value: 'pv://synthetic/1'
    }
  });
  fireEvent.change(screen.getByLabelText('Preuves de réception'), {
    target: {
      value: 'proof://synthetic/1'
    }
  });
  fireEvent.click(screen.getByText('Enregistrer la réception déclarée'));
  expect(post).not.toHaveBeenCalled();
  const form = screen.getByLabelText('Déclarer la réception');
  fireEvent.change(form.querySelector('textarea[name="change_justification"]')!, {
    target: {
      value: 'Lecture humaine du PV.'
    }
  });
  fireEvent.click(form.querySelector('input[name="change_human_confirmed"]')!);
  fireEvent.click(screen.getByText('Enregistrer la réception déclarée'));
  await screen.findByText(/Résultat UNKNOWN/);
  fireEvent.click(screen.getByText('Réessayer le même acte'));
  await waitFor(() => expect(post).toHaveBeenCalledTimes(2));
  expect(post.mock.calls[1]).toEqual(post.mock.calls[0]);
});
test('masks the previous Case immediately and rejects late or discordant replies', async () => {
  let resolveA: (v: unknown) => void = () => {};
  const api = {
    getCaseClosure: vi.fn(id => id === 'a' ? new Promise(resolve => {
      resolveA = resolve;
    }) : Promise.resolve(dossier('wrong')))
  } as unknown as ApiClient;
  const {
    rerender
  } = render(<CaseClosurePanel api={api} caseId="a" ownerKey="s1" />);
  rerender(<CaseClosurePanel api={api} caseId="b" ownerKey="s2" />);
  resolveA({
    ...dossier('a'),
    acts: [{
      id: 'secret',
      summary: 'Source ancienne secrète',
      act_kind: 'WORK_RECEPTION'
    }]
  });
  await screen.findByText(/Dossier indisponible/);
  expect(screen.queryByText('Source ancienne secrète')).toBeNull();
  expect(screen.queryByText('Enregistrer la réception déclarée')).toBeNull();
});
test('offers sourced expected/actual comparison and explicit human REX reuse on the target Case', async () => {
  const api = {
    getCaseClosure: vi.fn(async id => dossier(id)),
    listCaseTeachingSources: vi.fn(async id => ({
      case_id: id,
      sources: []
    }))
  } as unknown as ApiClient;
  render(<CaseClosurePanel api={api} caseId="target" ownerKey="s1" />);
  await screen.findByText('Aucune réception déclarée.');
  fireEvent.click(screen.getByText('Sortie et REX'));
  expect(screen.getByLabelText('Source prévue exacte')).toBeInTheDocument();
  expect(screen.getByLabelText('Source réalisée exacte')).toBeInTheDocument();
  await screen.findByText('Aucun enseignement d’exécution figé disponible pour ce réemploi.');
});
test('releases a definitively refused stale intent only after a current scoped read', async () => {
  const rejected = Object.assign(Error('stale'), {
    status: 409,
    detail: 'CLOSURE_VIEW_CONFLICT'
  });
  const post = vi.fn().mockRejectedValue(rejected);
  const api = {
    getCaseClosure: vi.fn(async id => dossier(id)),
    recordClosureOperation: post
  } as unknown as ApiClient;
  render(<CaseClosurePanel api={api} caseId="a" ownerKey="s1" />);
  await screen.findByText('Aucune réception déclarée.');
  const form = screen.getByLabelText('Déclarer la réception');
  fireEvent.change(screen.getByLabelText('Résumé de réception'), {
    target: {
      value: 'PV déclaré'
    }
  });
  fireEvent.change(screen.getByLabelText('Sources de réception'), {
    target: {
      value: 'source://1'
    }
  });
  fireEvent.change(screen.getByLabelText('Preuves de réception'), {
    target: {
      value: 'proof://1'
    }
  });
  fireEvent.change(form.querySelector('textarea[name="change_justification"]')!, {
    target: {
      value: 'Lecture humaine'
    }
  });
  fireEvent.click(form.querySelector('input[name="change_human_confirmed"]')!);
  fireEvent.click(screen.getByText('Enregistrer la réception déclarée'));
  await screen.findByText(/Acte refusé sans effet/);
  expect(screen.getByText('Enregistrer la réception déclarée')).not.toBeDisabled();
  expect(post).toHaveBeenCalledTimes(1);
});
test('a definitive validation refusal leaves a corrected new act possible without an automatic POST', async () => {
  const post = vi.fn().mockRejectedValue(Object.assign(Error('invalid source'), {
    status: 422,
    detail: 'INVALID_DECLARATION'
  }));
  const api = {
    getCaseClosure: vi.fn(async id => dossier(id)),
    recordClosureOperation: post
  } as unknown as ApiClient;
  render(<CaseClosurePanel api={api} caseId="a" ownerKey="s1" />);
  await screen.findByText('Aucune réception déclarée.');
  const form = screen.getByLabelText('Déclarer la réception');
  for (const [label, value] of [['Résumé de réception', 'Réception déclarée'], ['Sources de réception', 'source://1'], ['Preuves de réception', 'proof://1']]) fireEvent.change(screen.getByLabelText(label), {
    target: {
      value
    }
  });
  fireEvent.change(form.querySelector('textarea[name="change_justification"]')!, {
    target: {
      value: 'Relecture humaine'
    }
  });
  fireEvent.click(form.querySelector('input[name="change_human_confirmed"]')!);
  fireEvent.click(screen.getByText('Enregistrer la réception déclarée'));
  await screen.findByText(/Déclaration refusée/);
  expect(screen.getByText('Enregistrer la réception déclarée')).not.toBeDisabled();
  expect(post).toHaveBeenCalledTimes(1);
});

test('keeps the exact uncertain business intent after same owner reauthentication',async()=>{
 const store=new Map();
 const api={getCaseClosure:vi.fn(async(id)=>dossier(id)),recordClosureOperation:vi.fn().mockRejectedValue(Error('lost receipt'))} as unknown as ApiClient;
 const {rerender}=render(<CaseClosurePanel api={api} caseId="a" ownerKey="same-owner" scopeKey="session1" pendingStore={store}/>);
 await screen.findByText('Aucune réception déclarée.');
 const form=screen.getByLabelText('Déclarer la réception');
 for(const [label,value] of [['Résumé de réception','Réception déclarée'],['Sources de réception','source://1'],['Preuves de réception','proof://1']])fireEvent.change(screen.getByLabelText(label),{target:{value}});
 fireEvent.change(form.querySelector('textarea[name="change_justification"]')!,{target:{value:'Relecture humaine'}});fireEvent.click(form.querySelector('input[name="change_human_confirmed"]')!);fireEvent.click(screen.getByText('Enregistrer la réception déclarée'));
 await screen.findByText(/Résultat UNKNOWN/);
 rerender(<CaseClosurePanel api={api} caseId="a" ownerKey="same-owner" scopeKey="session2" pendingStore={store}/>);
 await screen.findByText(/Résultat UNKNOWN/);
 expect(screen.queryByLabelText('Résumé de réception')).toBeNull();
 fireEvent.click(screen.getByText('Réessayer le même acte'));
 await waitFor(()=>expect(api.recordClosureOperation).toHaveBeenCalledTimes(2));
 expect(vi.mocked(api.recordClosureOperation).mock.calls[1]).toEqual(vi.mocked(api.recordClosureOperation).mock.calls[0]);
});


test('shows source invalidation even when a reception outcome is present',async()=>{
  const data={...dossier('a'),acts:[{id:'reception-old',act_kind:'WORK_RECEPTION',
    reception_outcome:'WITH_RESERVATIONS',context_state:'REVIEW_REQUIRED',
    summary:'Réception historique à revoir.',source_refs_json:['pv://synthetic'],evidence_refs_json:[]}]};
  const api={getCaseClosure:vi.fn(async()=>data)} as unknown as ApiClient;
  render(<CaseClosurePanel api={api} caseId="a" ownerKey="reader"/>);
  expect(await screen.findByText(/WITH_RESERVATIONS/)).toBeInTheDocument();
  expect(screen.getByText('État source : REVIEW_REQUIRED')).toBeInTheDocument();
});

test('suspends closure reads and forms while DCE source outcome is uncertain',()=>{
 const get=vi.fn().mockResolvedValue(dossier('a'));
 render(<CaseClosurePanel api={{getCaseClosure:get} as unknown as ApiClient} caseId="a" ownerKey="owner" sourceReadBlocked/>);
 expect(screen.getByRole('status')).toHaveTextContent('Sources en cours de reprise');
 expect(get).not.toHaveBeenCalled();
 expect(screen.queryByLabelText('Déclarer la réception')).not.toBeInTheDocument();
});

test.each(['reception','reserve'])('does not transfer %s consent when a reread changes dossier hash',async stage=>{
 const obligations=[{id:'reserve-1',summary:'Réserve synthétique',declared_status:'OPEN',context_state:'CURRENT',history:[]}];
 const first={...dossier('a'),obligations};
 const second={...first,dossier_sha256:'b'.repeat(64),dce_version_id:'dce-v2'};
 const api={getCaseClosure:vi.fn().mockResolvedValue(first)} as unknown as ApiClient;
 const {rerender}=render(<CaseClosurePanel api={api} caseId="a" ownerKey="owner"/>);
 await screen.findByText('Aucune réception déclarée.');
 if(stage==='reserve')fireEvent.click(screen.getByRole('button',{name:'Réserves et actions'}));
 const label=stage==='reserve'?'Suivre Réserve synthétique':'Déclarer la réception';
 const form=screen.getByLabelText(label);
 fireEvent.change(form.querySelector('textarea[name="change_justification"]')!,{target:{value:'Accord sur l’ancienne source.'}});
 fireEvent.click(form.querySelector('input[name="change_human_confirmed"]')!);
 const changed={getCaseClosure:vi.fn().mockResolvedValue(second)} as unknown as ApiClient;
 rerender(<CaseClosurePanel api={changed} caseId="a" ownerKey="owner"/>);
 await screen.findByText(/Version DCE : dce-v2/);
 const refreshed=screen.getByLabelText(label);
 expect(refreshed.querySelector('input[name="change_human_confirmed"]')).not.toBeChecked();
 expect(refreshed.querySelector('textarea[name="change_justification"]')).toHaveValue('');
});

test('offers an explicit reread of the dossier and its sources',async()=>{
 const get=vi.fn().mockResolvedValue(dossier('a'));
 render(<CaseClosurePanel api={{getCaseClosure:get} as unknown as ApiClient} caseId="a" ownerKey="owner"/>);
 await screen.findByText('Aucune réception déclarée.');
 fireEvent.click(screen.getByRole('button',{name:'Relire le dossier et ses sources'}));
 await waitFor(()=>expect(get).toHaveBeenCalledTimes(2));
});
