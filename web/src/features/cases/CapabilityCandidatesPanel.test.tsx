import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CapabilityCandidatesPanel } from "./CapabilityCandidatesPanel";
import type { CapabilityProposalController, CapabilityProposalSource } from "./useCapabilityProposal";
import type { Candidate } from "./useCapabilityCandidates";

const rows: Candidate[] = [
  {capabilityId:"private-cap-id",kind:"EQUIPMENT",name:"Levage local",versionId:"private-v1",versionNumber:2,title:"Version chantier",validFrom:"2026-10-01T00:00:00Z",validUntil:null,validityState:"CURRENT",sourceEvidenceState:"UNKNOWN",evaluatedAt:"2026-10-08T09:00:00.123456Z"},
  {capabilityId:"private-cap2",kind:"METHOD",name:"Méthode synthétique",versionId:"private-v2",versionNumber:1,title:"Édition locale",validFrom:"2025-01-01T00:00:00Z",validUntil:"2026-01-01T00:00:00Z",validityState:"EXPIRED",sourceEvidenceState:"EXPIRED",evaluatedAt:"2026-10-08T09:00:00Z"},
];
const props = {caseId:"case-a",scopeKey:"tenant-a:session-1",candidates:rows,loading:false,error:null,onRefresh:vi.fn(),requirements:[] as CapabilityProposalSource[],dceSourceReady:true,dceVersionId:"dce-1",proposal:{tasks:[],taskLoading:false,taskError:null,status:"IDLE" as const,error:null,propose:vi.fn(),retry:vi.fn(),retryRead:vi.fn(),reset:vi.fn()}};
const requirements: CapabilityProposalSource[] = [{kind:"REQUIREMENT",id:"requirement-1",requirementId:"requirement-1",label:"Exigence DCE · méthode de contrôle",state:"UNKNOWN"}];
const proposal = (patch: Partial<CapabilityProposalController> = {}): CapabilityProposalController => ({
  tasks: [{id:"task-1",requirementId:"requirement-1",title:"Tâche DCE synthétique"},{id:"foreign-task",requirementId:"foreign-requirement",title:"Tâche hors DCE"}],
  taskLoading:false, taskError:null, status:"IDLE", error:null,
  propose:vi.fn(), retry:vi.fn(), retryRead:vi.fn(), reset:vi.fn(), ...patch,
});
describe("CapabilityCandidatesPanel",()=>{
  it("shows only the allowlisted labels and states; selection remains local",()=>{
    const {container,rerender}=render(<CapabilityCandidatesPanel {...props}/>);
    expect(screen.getByRole("heading",{name:"Moyens que vous pouvez proposer"})).toBeVisible();
    expect(screen.getByText("Levage local")).toBeVisible();
    expect(screen.getByText(/Version chantier/)).toBeVisible();
    expect(screen.getByText(/2026-10-08T09:00:00\.123456Z/)).toBeVisible();
    expect(screen.getAllByRole("button",{name:/Sélectionner/})).toHaveLength(2);
    fireEvent.click(screen.getByRole("button",{name:/Sélectionner Levage local/}));
    expect(screen.getByRole("button",{name:/Retirer Levage local/})).toHaveAttribute("aria-pressed","true");
    rerender(<CapabilityCandidatesPanel {...props} scopeKey="tenant-b:session-2"/>);
    expect(screen.getByRole("button",{name:/Sélectionner Levage local/})).toHaveAttribute("aria-pressed","false");
    expect(container.textContent).not.toMatch(/private-cap-id|private-v1|private-cap2|private-v2|proof_document_ids|sha256|storage_key|description|usage_scope/);
    expect(screen.queryByRole("button",{name:/Proposer|Réserver|Engager/})).toBeNull();
    expect(screen.getByText(/aucun état ne confirme la disponibilité.*réservation.*engagement/i)).toBeVisible();
  });
  it("does not display malformed validity dates as facts",()=>{
    const invalid = {...rows[0],validityState:"UNKNOWN" as const,validFrom:null,validUntil:null};
    render(<CapabilityCandidatesPanel {...props} candidates={[invalid]}/>);
    expect(screen.getByText(/Dates de validité inconnues/)).toBeVisible();
    expect(screen.queryByText("invalid")).toBeNull();
  });
  it("separates loading, error, no candidate and missing Case",()=>{
    const {rerender}=render(<CapabilityCandidatesPanel {...props} caseId=""/>);
    expect(screen.getByText(/Sélectionnez une affaire/)).toBeVisible();
    rerender(<CapabilityCandidatesPanel {...props} loading candidates={rows}/>);
    expect(screen.getByRole("status")).toBeVisible();expect(screen.queryByText("Levage local")).toBeNull();
    rerender(<CapabilityCandidatesPanel {...props} error="Liste indisponible" candidates={rows}/>);
    expect(screen.getByRole("alert")).toHaveTextContent("Liste indisponible");expect(screen.queryByText("Levage local")).toBeNull();
    rerender(<CapabilityCandidatesPanel {...props} candidates={[]}/>);
    expect(screen.getByText(/Aucun moyen enregistré/)).toBeVisible();
  });
  it("keeps UNKNOWN visible and selection alone never proposes",()=>{
    const controller=proposal();
    render(<CapabilityCandidatesPanel {...props} proposal={controller} requirements={requirements} dceSourceReady/>);
    expect(screen.getByText(/État documentaire : UNKNOWN/)).toBeVisible();
    fireEvent.click(screen.getByRole("button",{name:/Sélectionner Levage local/}));
    expect(screen.getByText(/Exigence DCE · méthode de contrôle/)).toBeVisible();
    expect(screen.getByText(/Tâche DCE synthétique/)).toBeVisible();
    expect(screen.queryByText(/Tâche hors DCE/)).toBeNull();
    expect(controller.propose).not.toHaveBeenCalled();
  });
  it("requires exact source, human justification and explicit confirmation before POST",()=>{
    const propose=vi.fn();
    const controller=proposal({propose});
    render(<CapabilityCandidatesPanel {...props} proposal={controller} requirements={requirements} dceSourceReady/>);
    fireEvent.click(screen.getByRole("button",{name:/Sélectionner Levage local/}));
    fireEvent.change(screen.getByLabelText(/Justification humaine/),{target:{value:"Justification humaine pour la proposition."}});
    fireEvent.click(screen.getByRole("button",{name:"Préparer la proposition"}));
    expect(controller.propose).not.toHaveBeenCalled();
    expect(screen.getAllByRole("alert").map((item)=>item.textContent).join(" ")).toMatch(/exigence ou tâche.*confirmez explicitement/i);
    fireEvent.click(screen.getByRole("radio",{name:/Tâche DCE synthétique/}));
    fireEvent.click(screen.getByLabelText(/Je confirme explicitement/));
    fireEvent.click(screen.getByRole("button",{name:"Préparer la proposition"}));
    expect(propose).toHaveBeenCalledWith({capability_id:"private-cap-id",capability_version_id:"private-v1",task_id:"task-1",justification:"Justification humaine pour la proposition."});
    expect(JSON.stringify(propose.mock.calls)).not.toMatch(/assignment_id/);
  });
  it("retries only the frozen intention after UNKNOWN and reads assessments after 409",()=>{
    const unknownPropose=vi.fn();
    const unknown=proposal({status:"UNKNOWN",propose:unknownPropose});
    const {rerender}=render(<CapabilityCandidatesPanel {...props} proposal={unknown} requirements={requirements} dceSourceReady/>);
    expect(screen.getByRole("button",{name:"Réessayer la même proposition"})).toBeVisible();
    expect(screen.getByLabelText(/Justification humaine/)).toBeDisabled();
    fireEvent.click(screen.getByRole("button",{name:"Réessayer la même proposition"}));
    expect(unknown.retry).toHaveBeenCalledOnce(); expect(unknownPropose).not.toHaveBeenCalled();
    const conflict=proposal({status:"CONFLICT"});
    rerender(<CapabilityCandidatesPanel {...props} proposal={conflict} requirements={requirements} dceSourceReady/>);
    expect(screen.getByText(/HTTP 409.*lecture actualisée.*revue humaine/i)).toBeVisible();
    expect(screen.getByRole("button",{name:"Préparer une autre proposition"})).toBeVisible();
    expect(conflict.propose).not.toHaveBeenCalled();
  });
  it("hides all sources when the current DCE scope is not ready",()=>{
    render(<CapabilityCandidatesPanel {...props} proposal={proposal()} requirements={requirements} dceSourceReady={false}/>);
    expect(screen.getByText(/source du DCE courant n’est pas disponible/i)).toBeVisible();
    expect(screen.queryByRole("radio")).toBeNull();
    expect(screen.getByRole("button",{name:"Préparer la proposition"})).toBeDisabled();
  });
  it("keeps the exact source summary frozen for an UNKNOWN intent after the DCE version changes",()=>{
    const ready=proposal();
    const {rerender}=render(<CapabilityCandidatesPanel {...props} proposal={ready} requirements={requirements} dceSourceReady dceVersionId="dce-1"/>);
    fireEvent.click(screen.getByRole("button",{name:/Sélectionner Levage local/}));
    fireEvent.click(screen.getByRole("radio",{name:/Exigence DCE/}));
    const unknownPropose=vi.fn();
    const unknown=proposal({status:"UNKNOWN",propose:unknownPropose});
    rerender(<CapabilityCandidatesPanel {...props} proposal={unknown} requirements={requirements} dceSourceReady dceVersionId="dce-1"/>);
    rerender(<CapabilityCandidatesPanel {...props} proposal={unknown} requirements={[{...requirements[0],id:"requirement-2",requirementId:"requirement-2",label:"Nouvelle exigence DCE"}]} dceSourceReady dceVersionId="dce-2"/>);
    expect(screen.getByText(/Source choisie : Exigence DCE · méthode de contrôle.*DCE courant a changé/i)).toBeVisible();
    expect(screen.getByRole("button",{name:"Réessayer la même proposition"})).toBeVisible();
    expect(screen.getByRole("button",{name:/Retirer Levage local/})).toBeDisabled();
    expect(unknownPropose).not.toHaveBeenCalled();
  });
  it("masks draft text and source immediately when the authenticated scope changes",()=>{
    const {rerender}=render(<CapabilityCandidatesPanel {...props} proposal={proposal()} requirements={requirements} dceSourceReady/>);
    fireEvent.click(screen.getByRole("button",{name:/Sélectionner Levage local/}));
    fireEvent.click(screen.getByRole("radio",{name:/Exigence DCE/}));
    fireEvent.change(screen.getByLabelText(/Justification humaine/),{target:{value:"Texte de session précédente."}});
    rerender(<CapabilityCandidatesPanel {...props} scopeKey="tenant-b:session-b" proposal={proposal()} requirements={requirements} dceSourceReady/>);
    expect(screen.getByLabelText(/Justification humaine/)).toHaveValue("");
    expect(screen.queryByText(/Source choisie :/)).toBeNull();
    expect(screen.queryAllByRole("radio",{checked:true})).toHaveLength(0);
    expect(screen.getAllByRole("button",{name:/Sélectionner|Retirer/}).every((button)=>button.getAttribute("aria-pressed")==="false")).toBe(true);
    expect(screen.getByRole("button",{name:"Préparer la proposition"})).toBeDisabled();
  });
});
