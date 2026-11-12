import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { ResponseCoveragePanel } from './ResponseCoveragePanel';

const selected = {draft_id:'draft-1',version:1,content_sha256:'a'.repeat(64)};
const report = {cited_annexes:[],package_id:'package-1',dce_version_id:'dce-1',selected_response:selected,content_format:'DOCX' as const,
 coverage:'UNKNOWN' as const,signature:'UNKNOWN' as const,annexes:'UNKNOWN' as const,inventory:'CURRENT_NON_FINANCIAL_SIGNALS_ONLY' as const,
 requirements:[{requirement_id:'req-1',document_family:'RC',source_state:'CURRENT_SOURCE',confirmation:'CONFIRMED',source_locator:'Ligne 6',source_anchor:null,
 lot_candidates:[6],applicability:'UNKNOWN' as const,coverage:'UNKNOWN' as const,signature:'UNKNOWN' as const,response_state:'MISSING' as const,pieces:[]}]};

describe('ResponseCoveragePanel',()=>{
 it('reads only the chosen piece and keeps missing requirements, annexes and signatures explicit',async()=>{
  const api={readResponseCoverage:vi.fn().mockResolvedValue(report)};
  render(<ResponseCoveragePanel api={api} packageId="package-1" selection={selected} scopeKey="owner-case" collaborator/>);
  fireEvent.click(screen.getByRole('button',{name:'Vérifier les liens de la pièce choisie'}));
  await screen.findByText('Réponse manquante');
  expect(api.readResponseCoverage).toHaveBeenCalledWith('package-1',selected,true);
  expect(screen.getByText(/Lot candidat : 6/)).toBeInTheDocument();
  expect(screen.getByText(/Annexes incluses : UNKNOWN/)).toBeInTheDocument();
  expect(screen.getByText(/Signature : UNKNOWN/)).toBeInTheDocument();
 });
 it('discards late reads and clears the previous report after owner or selection changes',async()=>{
  let resolve!:(value:typeof report)=>void;
  const api={readResponseCoverage:vi.fn(()=>new Promise<typeof report>(r=>{resolve=r}))};
  const view=render(<ResponseCoveragePanel api={api} packageId="package-1" selection={selected} scopeKey="owner-a"/>);
  fireEvent.click(screen.getByRole('button',{name:'Vérifier les liens de la pièce choisie'}));
  view.rerender(<ResponseCoveragePanel api={api} packageId="package-1" selection={selected} scopeKey="owner-b"/>);
  await act(async()=>resolve(report));
  expect(screen.queryByText('Réponse manquante')).toBeNull();
  expect(screen.getByText(/Lecture non effectuée.*UNKNOWN/)).toBeInTheDocument();
 });
 it('refuses a report for different selected bytes',async()=>{
  const api={readResponseCoverage:vi.fn().mockResolvedValue({...report,selected_response:{...selected,version:2}})};
  render(<ResponseCoveragePanel api={api} packageId="package-1" selection={selected} scopeKey="a"/>);
  fireEvent.click(screen.getByRole('button',{name:'Vérifier les liens de la pièce choisie'}));
  await waitFor(()=>expect(screen.getByRole('alert')).toHaveTextContent('UNKNOWN'));
  expect(screen.queryByText('Réponse manquante')).toBeNull();
 });
});

it('removes a completed report on scope changes and never restores it when returning',async()=>{
 const api={readResponseCoverage:vi.fn().mockResolvedValue(report)};
 const view=render(<ResponseCoveragePanel api={api} packageId="package-1" selection={selected} scopeKey="owner-a"/>);
 fireEvent.click(screen.getByRole('button',{name:'Vérifier les liens de la pièce choisie'}));
 await screen.findByText('Réponse manquante');
 view.rerender(<ResponseCoveragePanel api={api} packageId="package-1" selection={selected} scopeKey="owner-b"/>);
 expect(screen.queryByText('Réponse manquante')).toBeNull();
 view.rerender(<ResponseCoveragePanel api={api} packageId="package-1" selection={selected} scopeKey="owner-a"/>);
 expect(screen.queryByText('Réponse manquante')).toBeNull();
});

it('keeps unknown lots in the inventory and filters candidates without asserting applicability',async()=>{
 const value={...report,requirements:[...report.requirements,{...report.requirements[0],requirement_id:'req-unknown',lot_candidates:[]}]};
 const api={readResponseCoverage:vi.fn().mockResolvedValue(value)};
 render(<ResponseCoveragePanel api={api} packageId="package-1" selection={selected} scopeKey="a"/>);
 fireEvent.click(screen.getByRole('button',{name:'Vérifier les liens de la pièce choisie'}));
 await screen.findByText(/Exigence req-unknown/);
 fireEvent.change(screen.getByRole('combobox'),{target:{value:'6'}});
 expect(screen.queryByText(/Exigence req-unknown/)).toBeNull();
 expect(screen.getByText(/Exigence req-1/)).toBeInTheDocument();
 fireEvent.change(screen.getByRole('combobox'),{target:{value:'UNKNOWN'}});
 expect(screen.getByText(/Exigence req-unknown/)).toBeInTheDocument();
 expect(screen.queryByText(/Exigence req-1/)).toBeNull();
});

it('shows a readable buyer excerpt alongside its exact source',async()=>{
 const api={readResponseCoverage:vi.fn().mockResolvedValue({...report,requirements:[{...report.requirements[0],source_excerpt:'Le DC1 est obligatoire pour le lot 6.'}]})};
 render(<ResponseCoveragePanel api={api} packageId="package-1" selection={selected} scopeKey="a"/>);
 fireEvent.click(screen.getByRole('button',{name:'Vérifier les liens de la pièce choisie'}));
 await screen.findByText('Réponse manquante');
 expect(screen.getByText('Le DC1 est obligatoire pour le lot 6.')).toBeInTheDocument();
});

it('selects a cited exact annex only after an explicit checkbox action',async()=>{
 const annex={requirement_id:'req-1',section_code:'METHOD',document_id:'proof-1',sha256:'b'.repeat(64),inclusion:'UNKNOWN' as const};
 const api={readResponseCoverage:vi.fn().mockResolvedValue({...report,cited_annexes:[annex]})};
 const change=vi.fn();
 render(<ResponseCoveragePanel api={api} packageId="package-1" selection={selected} scopeKey="a" selectedAnnexes={[]} onAnnexesChange={change}/>);
 fireEvent.click(screen.getByRole('button',{name:'Vérifier les liens de la pièce choisie'}));
 const choice=await screen.findByRole('checkbox');
 expect(change).not.toHaveBeenCalled();
 fireEvent.click(choice);
 expect(change).toHaveBeenCalledWith([{requirement_id:'req-1',document_id:'proof-1',sha256:'b'.repeat(64)}]);
});
