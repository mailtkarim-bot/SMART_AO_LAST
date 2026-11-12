import {fireEvent,render,screen,waitFor} from "@testing-library/react";
import {expect,it,vi} from "vitest";
import {AnalysisDossierHistory} from "./AnalysisDossierHistory";
import {analysisFixture} from "./analysisFixture.test-helper";
import type {ApiClient} from "../../infrastructure/api";
import type {AnalysisDossierHistoryPage} from "../../shared/types";

function page():AnalysisDossierHistoryPage{return {case_id:"case-a",next_before_revision:null,entries:[{review_id:"review-a",revision:1,phase:"PREPARED",state:"HISTORICAL",dossier_sha256:"a".repeat(64),actor_id:"patron-a",created_at:"2026-10-21T10:00:00Z",axes:analysisFixture().axes.map(a=>({code:a.code,state:"UNKNOWN",note:"Texte historique privé",follow_up:"Relire",responsible:"SELF"})),justification:"Revue ancienne",dce_version_id:"version-a",snapshot:analysisFixture()}]};}
it("shows historical reviews explicitly without promoting them to current conclusions",async()=>{
 const api={getCaseAnalysisDossierHistory:vi.fn().mockResolvedValue(page())} as unknown as ApiClient;
 render(<AnalysisDossierHistory api={api} caseId="case-a" disabled={false}/>);fireEvent.click(screen.getByRole('button',{name:'Consulter l’historique du dossier'}));
 expect(await screen.findByText(/Historique — Préparation/)).toBeInTheDocument();expect(screen.getByText(/Version DCE historique : version-a/)).toBeInTheDocument();expect(screen.getByText(/ne sont pas des conclusions courantes/)).toBeInTheDocument();
});
it("rejects a history response belonging to another Case without showing its notes",async()=>{
 const value=page();value.case_id="case-b";const api={getCaseAnalysisDossierHistory:vi.fn().mockResolvedValue(value)} as unknown as ApiClient;
 render(<AnalysisDossierHistory api={api} caseId="case-a" disabled={false}/>);fireEvent.click(screen.getByRole('button',{name:'Consulter l’historique du dossier'}));
 await waitFor(()=>expect(screen.getByRole('alert')).toBeInTheDocument());expect(screen.queryByText(/Texte historique privé/)).not.toBeInTheDocument();
});
