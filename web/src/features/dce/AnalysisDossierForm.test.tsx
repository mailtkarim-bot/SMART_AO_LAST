import {act,fireEvent,render,screen} from "@testing-library/react";
import {expect,it,vi} from "vitest";
import {AnalysisDossierForm} from "./AnalysisDossierForm";
import {AnalysisDossierPendingStore} from "./analysisDossierPending";
import {analysisFixture} from "./analysisFixture.test-helper";

it("requires twelve explicit notes/actions and freezes an uncertain dossier act for identical retry",async()=>{
 const summary={...analysisFixture(),dossier_sha256:"a".repeat(64)};
 const save=vi.fn().mockRejectedValueOnce(Error("lost")).mockImplementationOnce(async input=>({...input,revision:1,replayed:true}));
 render(<AnalysisDossierForm summary={summary} scope="own-case-a" store={new AnalysisDossierPendingStore()} disabled={false} save={save} onLock={vi.fn()} onNotice={vi.fn()} onRefresh={vi.fn()}/>);
 fireEvent.click(screen.getByLabelText(/Je confirme la préparation/));fireEvent.change(screen.getByLabelText("Justification du dossier"),{target:{value:"Relecture synthétique"}});
 await act(async()=>fireEvent.click(screen.getByRole('button',{name:'Enregistrer la préparation du dossier'})));
 expect(save).not.toHaveBeenCalled();
 for(const input of screen.getAllByLabelText(/Note de revue —/))fireEvent.change(input,{target:{value:"Source ou portée à instruire"}});
 for(const input of screen.getAllByLabelText(/Action pour l’inconnu —/))fireEvent.change(input,{target:{value:"Relire les pièces concernées"}});
 await act(async()=>fireEvent.click(screen.getByRole('button',{name:'Enregistrer la préparation du dossier'})));
 expect(save).toHaveBeenCalledOnce();expect(screen.getByLabelText("Justification du dossier")).toBeDisabled();
 await act(async()=>fireEvent.click(screen.getByRole('button',{name:'Réessayer le même acte de dossier'})));
 expect(save.mock.calls[0][0]).toEqual(save.mock.calls[1][0]);
});

it("does not offer final review when an empty axis was labelled as points reviewed",()=>{
 const summary={...analysisFixture(),dossier_sha256:"a".repeat(64),dossier_review:{review_id:"prior",revision:1,phase:"PREPARED" as const,state:"CURRENT" as const,dossier_sha256:"a".repeat(64),actor_id:"patron",created_at:"2026-10-21T10:00:00Z",axes:analysisFixture().axes.map(a=>({code:a.code,state:(a.code==="HSE"?"POINTS_REVIEWED":"UNKNOWN") as "POINTS_REVIEWED"|"UNKNOWN",note:"À instruire",follow_up:"Relire",responsible:"SELF" as const})),justification:"Préparer"}};
 render(<AnalysisDossierForm summary={summary} scope="case-a" store={new AnalysisDossierPendingStore()} disabled={false} save={vi.fn()} onLock={vi.fn()} onNotice={vi.fn()} onRefresh={vi.fn()}/>);
 expect(screen.getByRole('button',{name:'Enregistrer la revue du dossier préparé'})).toBeDisabled();
});


it("reconstruit douze champs vides après invalidation sans transférer les anciens axes",()=>{
 const summary={...analysisFixture(),dossier_sha256:"b".repeat(64),dossier_review:{review_id:"old",revision:2,phase:"REVIEWED" as const,state:"REVIEW_REQUIRED" as const,dossier_sha256:"a".repeat(64),actor_id:null,created_at:"2026-11-03T00:00:00Z",axes:[],justification:null}};
 render(<AnalysisDossierForm summary={summary} scope="case-a" store={new AnalysisDossierPendingStore()} disabled={false} save={vi.fn()} onLock={vi.fn()} onNotice={vi.fn()} onRefresh={vi.fn()}/>);
 expect(screen.getAllByLabelText(/Note de revue —/)).toHaveLength(12);
 expect(screen.getByLabelText(/Je confirme la préparation/)).not.toBeChecked();
});

it("vide les notes V1 après reçu d’un ancien intent résolu sous V2",async()=>{
 const summary={...analysisFixture(),dossier_sha256:"b".repeat(64)};const store=new AnalysisDossierPendingStore();
 const input={command_id:"c",idempotency_key:"i",review_id:"old",expected_revision:0,dossier_sha256:"a".repeat(64),phase:"PREPARED" as const,axes:summary.axes.map(a=>({code:a.code,state:"UNKNOWN" as const,note:"NOTE_V1",follow_up:"ACTION_V1",responsible:"SELF" as const})),justification:"JUSTIFICATION_V1",human_confirmed:true as const};
 store.put("case-a",input);const save=vi.fn(async value=>({...value,revision:1,replayed:true}));
 render(<AnalysisDossierForm summary={summary} scope="case-a" store={store} disabled={false} save={save} onLock={vi.fn()} onNotice={vi.fn()} onRefresh={vi.fn()}/>);
 await act(async()=>fireEvent.click(screen.getByRole("button",{name:"Réessayer le même acte de dossier"})));
 expect(save).toHaveBeenCalledTimes(1);expect(save.mock.calls[0][0]).toEqual(input);
 for(const field of screen.getAllByLabelText(/Note de revue —/))expect(field).toHaveValue("");
 expect(screen.getByLabelText("Justification du dossier")).toHaveValue("");
 expect(screen.getByLabelText(/Je confirme la préparation/)).not.toBeChecked();
});
