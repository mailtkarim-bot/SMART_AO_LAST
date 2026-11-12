import {fireEvent, render, screen, waitFor} from '@testing-library/react';
import {vi, expect, test} from 'vitest';
import type {ApiClient} from '../../infrastructure/api';
import {CashSchedulePanel} from './CashSchedulePanel';

const view = {case_id:'a',revision:0,view_sha256:'a'.repeat(64),current:null,history:[],sources:[],history_truncated:false,catalog_truncated:false};
test('requires a deliberate cash declaration and freezes the identical intent after UNKNOWN',async()=>{
 const post=vi.fn().mockRejectedValue(new Error('lost response'));
 const get=vi.fn().mockResolvedValue(view);
 render(<CashSchedulePanel api={{getCashSchedule:get,recordCashSchedule:post} as unknown as ApiClient} caseId="a" ownerKey="session"/>);
 await screen.findByText('Aucun échéancier déclaré.');
 fireEvent.change(screen.getByLabelText('Début de période'),{target:{value:'2026-11-01'}});
 fireEvent.change(screen.getByLabelText('Fin de période'),{target:{value:'2026-11-30'}});
 fireEvent.change(screen.getByLabelText('Hypothèses et limites'),{target:{value:'Déclaration synthétique partielle.'}});
 fireEvent.click(screen.getByText('Enregistrer la révision déclarée'));
 expect(post).not.toHaveBeenCalled();
 fireEvent.change(screen.getByLabelText('Justification de cet acte'),{target:{value:'Sources relues.'}});
 fireEvent.click(screen.getByLabelText(/Je confirme cet acte/));
 fireEvent.click(screen.getByText('Enregistrer la révision déclarée'));
 await screen.findByText(/Résultat UNKNOWN/);
 fireEvent.click(screen.getByText('Réessayer la même déclaration'));
 await waitFor(()=>expect(post).toHaveBeenCalledTimes(2));
 expect(post.mock.calls[0]).toEqual(post.mock.calls[1]);
 expect(get).toHaveBeenCalledTimes(1);
});

test('ignores a late reply after changing Case and refuses a discordant Case',async()=>{
 let finish:(value:unknown)=>void=()=>{};
 const get=vi.fn((id:string)=>id==='a'?new Promise(resolve=>{finish=resolve;}):Promise.resolve({...view,case_id:'b'}));
 const api={getCashSchedule:get} as unknown as ApiClient;
 const {rerender}=render(<CashSchedulePanel api={api} caseId="a" ownerKey="session"/>);
 rerender(<CashSchedulePanel api={api} caseId="b" ownerKey="session"/>);
 await screen.findByText('Aucun échéancier déclaré.');
 finish({...view,case_id:'a',current:{declaration:{assumptions:'PRIVATE_A'}}});
 await waitFor(()=>expect(screen.queryByText('PRIVATE_A')).not.toBeInTheDocument());
 const wrong={getCashSchedule:vi.fn().mockResolvedValue({...view,case_id:'foreign'})} as unknown as ApiClient;
 rerender(<CashSchedulePanel api={wrong} caseId="b" ownerKey="new-session"/>);
 await screen.findByText('Échéancier indisponible : résultat à relire.');
 expect(screen.queryByText('Aucun échéancier déclaré.')).not.toBeInTheDocument();
});

test('removes abandoned flows and opening balances only in the new revision',async()=>{
 const declaration={period_start:'2026-11-01',period_end:'2026-11-30',status:'ACTIVE',assumptions:'Déclaration initiale.',openings:[{currency_code:'EUR',amount_minor:0,source_refs:['opening://test']}],flows:[{flow_id:'f1',direction:'OUTFLOW',currency_code:'EUR',amount_minor:100,declared_date:'2026-11-02',source_refs:['cost://test']}]};
 const current={id:'r1',revision:1,context_state:'CURRENT',created_at:'2026-11-01',justification:'Revue initiale.',human_confirmed:true,declaration,source_snapshot:{case_source:{dce_version_id:null},sources:{}},projection:{currencies:[]}};
 const post=vi.fn().mockRejectedValue(new Error('lost'));
 const api={getCashSchedule:vi.fn().mockResolvedValue({...view,revision:1,current}),recordCashSchedule:post} as unknown as ApiClient;
 render(<CashSchedulePanel api={api} caseId="a" ownerKey="session"/>);
 await screen.findByLabelText('Sources du flux 1');
 fireEvent.click(screen.getByText('Retirer le flux 1'));
 fireEvent.click(screen.getByText('Retirer le dernier solde de départ'));
 expect(screen.queryByLabelText('Sources du flux 1')).not.toBeInTheDocument();
 expect(screen.queryByLabelText('Sources du solde 1')).not.toBeInTheDocument();
 const form=screen.getByLabelText('Déclarer l’échéancier');
 fireEvent.change(form.querySelector('textarea[name="change_justification"]')!,{target:{value:'Flux et solde abandonnés, historique conservé.'}});
 fireEvent.click(form.querySelector('input[name="change_human_confirmed"]')!);
 fireEvent.click(screen.getByText('Enregistrer la révision déclarée'));
 await waitFor(()=>expect(post).toHaveBeenCalledTimes(1));
 expect(post.mock.calls[0][1].declaration.flows).toEqual([]);
 expect(post.mock.calls[0][1].declaration.openings).toEqual([]);
 expect(declaration.flows).toHaveLength(1);
 expect(declaration.openings).toHaveLength(1);
});

test('suspends cash reads while the DCE source outcome is uncertain',async()=>{
 const get=vi.fn().mockResolvedValue(view);
 render(<CashSchedulePanel api={{getCashSchedule:get} as unknown as ApiClient} caseId="a" ownerKey="session" sourceReadBlocked/>);
 expect(screen.getByRole('status')).toHaveTextContent('Sources en cours de reprise');
 expect(get).not.toHaveBeenCalled();
 expect(screen.queryByLabelText('Déclarer l’échéancier')).not.toBeInTheDocument();
});

test('rereads cash sources and removes consent from the replaced context',async()=>{
 const declaration={period_start:'2026-11-01',period_end:'2026-11-30',status:'ACTIVE',assumptions:'Sources remplacées à relire.',openings:[],flows:[]};
 const current={id:'r1',revision:1,context_state:'REVIEW_REQUIRED',created_at:'2026-11-01',justification:'Historique.',human_confirmed:true,declaration,source_snapshot:{case_source:{dce_version_id:'v1'},sources:{}},projection:{currencies:[]}};
 const get=vi.fn().mockResolvedValueOnce(view).mockResolvedValue({...view,revision:1,view_sha256:'b'.repeat(64),current});
 const post=vi.fn();
 render(<CashSchedulePanel api={{getCashSchedule:get,recordCashSchedule:post} as unknown as ApiClient} caseId="a" ownerKey="session"/>);
 await screen.findByText('Aucun échéancier déclaré.');
 fireEvent.change(screen.getByLabelText('Justification de cet acte'),{target:{value:'Ancien consentement.'}});
 fireEvent.click(screen.getByLabelText(/Je confirme cet acte/));
 fireEvent.click(screen.getByRole('button',{name:'Relire l’échéancier et ses sources'}));
 await screen.findByText(/Source changée : relisez/);
 expect(screen.getByLabelText('Déclarer l’échéancier').querySelector('input[name="change_human_confirmed"]')).not.toBeChecked();
 expect(screen.getByLabelText('Hypothèses et limites')).toHaveValue('Sources remplacées à relire.');
 expect(post).not.toHaveBeenCalled();
});

test('does not transfer cancellation consent to a replacement source view',async()=>{
 const declaration={period_start:'2026-11-01',period_end:'2026-11-30',status:'ACTIVE',assumptions:'Déclaratif.',openings:[],flows:[]};
 const current={id:'r1',revision:1,context_state:'CURRENT',created_at:'2026-11-01',justification:'Historique.',human_confirmed:true,declaration,source_snapshot:{case_source:{dce_version_id:'v1'},sources:{}},projection:{currencies:[]}};
 const get=vi.fn().mockResolvedValueOnce({...view,revision:1,current}).mockResolvedValue({...view,revision:2,view_sha256:'b'.repeat(64),current:{...current,id:'r2',revision:2}});
 const post=vi.fn();
 render(<CashSchedulePanel api={{getCashSchedule:get,recordCashSchedule:post} as unknown as ApiClient} caseId="a" ownerKey="session"/>);
 await screen.findByLabelText('Annuler la déclaration');
 const old=screen.getByLabelText('Annuler la déclaration');
 fireEvent.change(old.querySelector('textarea[name="change_justification"]')!,{target:{value:'Ancien consentement d’annulation.'}});
 fireEvent.click(old.querySelector('input[name="change_human_confirmed"]')!);
 fireEvent.click(screen.getByRole('button',{name:'Relire l’échéancier et ses sources'}));
 await waitFor(()=>expect(screen.getByText(/Révision 2 · Flux déclarés/)).toBeInTheDocument());
 expect(screen.getByLabelText('Annuler la déclaration').querySelector('input[name="change_human_confirmed"]')).not.toBeChecked();
 expect(post).not.toHaveBeenCalled();
});

test('keeps recorded financial provenance distinct from the newly proposed published source',async()=>{
 const oldSource={id:'LINE:old',label:'Ancien coût',sha256:'a'.repeat(64),direction:'OUTFLOW',currency_code:'EUR',amount_minor:12000,declared_date:null,source_refs:['financial-report://old/line/one'],financial_report:{report_id:'old-report',revision:2,state:'PUBLISHED'}};
 const freshSource={...oldSource,id:'LINE:new',financial_report:{report_id:'new-report',revision:3,state:'PUBLISHED'}};
 const declaration={period_start:'2026-11-01',period_end:'2026-11-30',status:'ACTIVE',assumptions:'Date et solde inconnus.',openings:[],flows:[]};
 const current={id:'cash-one',revision:1,context_state:'REVIEW_REQUIRED',created_at:'2026-11-05',justification:'Ancienne source relue.',human_confirmed:true,declaration,source_snapshot:{case_source:{dce_version_id:null},sources:{'LINE:old':'a'.repeat(64)},source_details:{'LINE:old':oldSource}},projection:{currencies:[]}};
 const api={getCashSchedule:vi.fn().mockResolvedValue({...view,current,sources:[freshSource]})} as unknown as ApiClient;
 render(<CashSchedulePanel api={api} caseId="a" ownerKey="owner"/>);
 expect(await screen.findByText(/Rapport publié proposé : new-report · révision 3/)).toBeInTheDocument();
 expect(screen.getByText(/Rapport source enregistré : old-report · révision 2/)).toBeInTheDocument();
 expect(screen.getByText(/Date de flux et solde initial restent des déclarations humaines/)).toBeInTheDocument();
});

test('does not fill legacy source versions from the current catalogue',async()=>{
 const flow={flow_id:'old-flow',direction:'OUTFLOW',currency_code:'EUR',amount_minor:12000,declared_date:null,source_refs:['financial-report://old/line/cost'],native_source_id:'LINE:cost'};
 const declaration={period_start:'2026-11-01',period_end:'2026-11-30',status:'ACTIVE',assumptions:'Ancienne hypothèse conservée.',openings:[],flows:[flow]};
 const current={id:'legacy',revision:1,context_state:'CURRENT',created_at:'2026-11-01',justification:'Acte historique.',human_confirmed:true,declaration,source_snapshot:{case_source:{dce_version_id:null},sources:{'LINE:cost':'a'.repeat(64)}},projection:{currencies:[]}};
 render(<CashSchedulePanel api={{getCashSchedule:vi.fn().mockResolvedValue({...view,current})} as unknown as ApiClient} caseId="a" ownerKey="owner"/>);
 expect(await screen.findByText(/Version du rapport source enregistré : UNKNOWN/)).toBeInTheDocument();
 expect(screen.queryByText(/Rapport source enregistré :/)).not.toBeInTheDocument();
});

test('keeps exactly one declaration editor after repeated source rereads',async()=>{
 const declaration={period_start:'2026-11-01',period_end:'2026-11-30',status:'ACTIVE',assumptions:'Hypothèses relues.',openings:[],flows:[]};
 const row={id:'r1',revision:1,context_state:'CURRENT',created_at:'2026-11-01',justification:'Historique.',human_confirmed:true,declaration,source_snapshot:{case_source:{dce_version_id:null},sources:{}},projection:{currencies:[]}};
 let revision=0;
 const get=vi.fn().mockImplementation(()=>{revision++;return Promise.resolve({...view,revision,view_sha256:String(revision).repeat(64),current:{...row,id:`r${revision}`,revision}});});
 render(<CashSchedulePanel api={{getCashSchedule:get} as unknown as ApiClient} caseId="a" ownerKey="owner"/>);
 await screen.findByText(/Révision 1 · Flux déclarés/);
 for(let n=2;n<=4;n++){
  fireEvent.click(screen.getByRole('button',{name:'Relire l’échéancier et ses sources'}));
  await screen.findByText(new RegExp(`Révision ${n} · Flux déclarés`));
  expect(screen.getAllByLabelText('Déclarer l’échéancier')).toHaveLength(1);
  expect(screen.getAllByLabelText('Annuler la déclaration')).toHaveLength(1);
 }
});
