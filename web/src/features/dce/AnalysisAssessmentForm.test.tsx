import {AnalysisAssessmentPendingStore} from "./analysisAssessmentPending";
import {act,fireEvent,render,screen} from "@testing-library/react";
import {describe,it,expect,vi} from "vitest";
import {AnalysisAssessmentForm} from "./AnalysisAssessmentForm";

function receipt(input:Record<string,unknown>){return {...input,revision:Number(input.expected_revision)+1,replayed:false};}
function setup(save=vi.fn().mockImplementation(async(input)=>receipt(input)),pendingIntents=new AnalysisAssessmentPendingStore()) {
 const refresh=vi.fn(); const lock=vi.fn();
 const item={item_id:"risk-a",kind:"RISK" as const,source_context_sha256:"a".repeat(64),human_assessment:null};
 const view=render(<AnalysisAssessmentForm item={item} pendingIntents={pendingIntents} intentScope="owner/case-a" save={save} disabled={false} onLock={lock} onNotice={vi.fn()} onRefresh={refresh}/>);
 return {save,refresh,lock,...view};
}
function fill(){fireEvent.change(screen.getByLabelText("Justification de la revue"),{target:{value:"Relecture du point exact"}});fireEvent.change(screen.getByLabelText("Raison des inconnus"),{target:{value:"Preuve restant à obtenir"}});fireEvent.click(screen.getByLabelText(/Je confirme cette déclaration/));}
describe("human analysis assessment",()=>{
 it("does not send without explicit confirmation and justification",async()=>{const h=setup();await act(async()=>{fireEvent.submit(screen.getByRole("form",{hidden:true}));});expect(h.save).not.toHaveBeenCalled();});
 it("sends one exact human intent and refreshes only after receipt",async()=>{const h=setup();fill();await act(async()=>{fireEvent.submit(screen.getByRole("form",{hidden:true}));});expect(h.save).toHaveBeenCalledOnce();const payload=h.save.mock.calls[0][0];expect(payload.expected_revision).toBe(0);expect(payload.source_context_sha256).toBe("a".repeat(64));expect(payload.human_confirmed).toBe(true);expect(h.refresh).toHaveBeenCalledOnce();});
 it("freezes UNKNOWN and retries identical ids without GET reconciliation",async()=>{const save=vi.fn().mockRejectedValueOnce(new Error("network")).mockImplementationOnce(async(input)=>receipt(input));const h=setup(save);fill();await act(async()=>{fireEvent.submit(screen.getByRole("form",{hidden:true}));});expect(screen.getByText(/Résultat inconnu/)).toBeInTheDocument();expect(h.refresh).not.toHaveBeenCalled();expect(screen.getByLabelText("Justification de la revue")).toBeDisabled();await act(async()=>{fireEvent.click(screen.getByRole("button",{name:/Réessayer le même acte/,hidden:true}));});expect(save.mock.calls[1][0]).toEqual(save.mock.calls[0][0]);expect(h.refresh).toHaveBeenCalledOnce();});
 it("reloads source after a known 409 and does not resubmit automatically",async()=>{const h=setup(vi.fn().mockRejectedValue({status:409}));fill();await act(async()=>{fireEvent.submit(screen.getByRole("form",{hidden:true}));});expect(h.refresh).toHaveBeenCalledOnce();expect(h.save).toHaveBeenCalledOnce();});
});

it("retains an UNKNOWN intent across leaving and returning to its context",async()=>{
 const registry=new AnalysisAssessmentPendingStore();const save=vi.fn().mockRejectedValueOnce(new Error("network")).mockImplementationOnce(async input=>receipt(input));
 const first=setup(save,registry);fill();await act(async()=>{fireEvent.submit(screen.getByRole("form",{hidden:true}));});const payload=save.mock.calls[0][0];first.unmount();
 const next=setup(save,registry);expect(screen.getByText(/Résultat inconnu/)).toBeInTheDocument();expect(next.refresh).not.toHaveBeenCalled();
 await act(async()=>{fireEvent.click(screen.getByRole("button",{name:/Réessayer le même acte/,hidden:true}));});expect(save.mock.calls[1][0]).toEqual(payload);
});

it("keeps an already UNKNOWN act frozen when a retry requires MFA again",async()=>{
 const save=vi.fn().mockRejectedValueOnce(new Error("network")).mockRejectedValueOnce({status:403}).mockImplementationOnce(async input=>receipt(input));
 const h=setup(save);fill();await act(async()=>{fireEvent.submit(screen.getByRole("form",{hidden:true}));});
 await act(async()=>{fireEvent.click(screen.getByRole("button",{name:/Réessayer le même acte/,hidden:true}));});
 expect(screen.getByText(/Résultat inconnu/)).toBeInTheDocument();expect(h.refresh).not.toHaveBeenCalled();expect(screen.getByLabelText("Justification de la revue")).toBeDisabled();
 await act(async()=>{fireEvent.click(screen.getByRole("button",{name:/Réessayer le même acte/,hidden:true}));});expect(save.mock.calls[2][0]).toEqual(save.mock.calls[0][0]);
});


it("exige un nouveau consentement après un reçu avant une autre déclaration",async()=>{
 const h=setup();fill();await act(async()=>{fireEvent.submit(screen.getByRole("form",{hidden:true}));});
 expect(screen.getByLabelText(/Je confirme cette déclaration/)).not.toBeChecked();
 fireEvent.change(screen.getByLabelText("Justification de la revue"),{target:{value:"Autre déclaration"}});
 await act(async()=>{fireEvent.submit(screen.getByRole("form",{hidden:true}));});expect(h.save).toHaveBeenCalledTimes(1);
});
