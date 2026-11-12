import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { expect, test, vi } from "vitest";
import type { ApiClient } from "../../infrastructure/api";
import type { CaseHandoverOfferOptions, CaseHandoverSnapshots } from "../../shared/types";
import { CaseHandoverPanel } from "./CaseHandoverPanel";
import { HandoverIntentStore } from "./HandoverIntentStore";
import { HandoverSnapshotRead } from "./HandoverSnapshotRead";
const options: CaseHandoverOfferOptions = {
  case_id: "case-1",
  items: [{
    outcome_id: "outcome-won",
    lot_reference: "01",
    submission_package_id: "package-p5",
    package_version: 3,
    manifest_sha256: "a".repeat(64),
    dce_version_id: "dce-v2",
    technical_document_id: "technical-doc",
    technical_document_version: 2,
    technical_document_kind: "TECHNICAL_RESPONSE",
    technical_document_sha256: "c".repeat(64)
  }]
};
const snapshots: CaseHandoverSnapshots = {
  case_id: "case-1",
  items: [{
    snapshot_id: "handover-1",
    outcome_id: "outcome-won",
    lot_reference: "01",
    submission_package_id: "package-p5",
    package_version: 3,
    manifest_sha256: "a".repeat(64),
    revision: 1,
    created_at: "2026-10-01T12:00:00Z",
    snapshot: {
      schema_version: 1,
      kind: "P7_HANDOVER_SNAPSHOT",
      p7_is_order_service: false,
      award: {
        outcome_id: "outcome-won",
        lot_reference: "01",
        source_locator: "attribution://notice/01",
        recorded_at: "2026-10-01T11:00:00Z"
      },
      offer: {
        submission_package_id: "package-p5",
        package_version: 3,
        manifest_sha256: "a".repeat(64),
        dce_version_id: "dce-v2",
        technical_document_id: "technical-doc",
        technical_document_version: 2,
        technical_document_kind: "TECHNICAL_RESPONSE",
        technical_document_sha256: "c".repeat(64),
        financial_content: "NOT_INCLUDED"
      },
      decision: {
        state: "KNOWN",
        decision_id: "decision-1",
        revision: 4,
        outcome: "CONDITIONAL_GO",
        context_id: "context-1",
        context_fingerprint: "b".repeat(64),
        conditions_state: "KNOWN",
        open_conditions: [{
          condition_id: "condition-1",
          label: "Réserve de lancement à lever",
          status: "OPEN",
          due_at: null
        }],
        condition_sources: []
      },
      contract_comparison: {
        state: "UNKNOWN",
        reason: "Aucun rapprochement de recette."
      },
      excluded: ["DONNEES_FINANCIERES_PRIVEES"]
    }
  }]
};
function makeApi(recordCaseHandover = vi.fn().mockImplementation(async (_caseId,input) => ({
  status: "SUCCEEDED",
  result_code: "CASE_HANDOVER_SNAPSHOT_RECORDED",
  command_id: input.command_id, idempotency_key: input.idempotency_key,
  replayed: false
}))) {
  return {
    listCaseHandoverSnapshots: vi.fn().mockImplementation(async () => {
      const input = recordCaseHandover.mock.calls.at(-1)?.[1];
      return input ? {
        ...snapshots,
        items: [{
          ...snapshots.items[0],
          snapshot_id: input.snapshot_id,
          outcome_id: input.outcome_id,
          submission_package_id: input.submission_package_id
        }]
      } : snapshots;
    }),
    listCaseHandoverOfferOptions: vi.fn().mockResolvedValue(options),
    listCaseHandoverContracts: vi.fn().mockResolvedValue({case_id:"case-1",source_context_sha256:"b".repeat(64),items:[],condition_options:[],truncated:false}),
    downloadCaseHandoverOffer: vi.fn().mockResolvedValue(new Blob(["offre technique"])),
    recordCaseHandover
  } as unknown as ApiClient;
}
test("transmet le paquet P5 exact et affiche la condition ouverte au Responsable", async () => {
  vi.stubGlobal("crypto", {
    randomUUID: vi.fn(() => "stable-id")
  });
  const api = makeApi();
  const record = api.recordCaseHandover as ReturnType<typeof vi.fn>;
  const {
    rerender
  } = render(<CaseHandoverPanel api={api} caseId="case-1" canManage />);
  fireEvent.change(await screen.findByLabelText("Offre gagnée exacte à transmettre"), {
    target: {
      value: "outcome-won:package-p5"
    }
  });
  fireEvent.change(await screen.findByLabelText("Point opérationnel 1"), {target:{value:"Transport exclu de la fourniture."}});
  fireEvent.change(screen.getByLabelText("Justification de la revue"), {target:{value:"Sources relues pour transmission opérationnelle."}});
  fireEvent.click(screen.getByLabelText(/Je confirme la publication opérationnelle/));
  fireEvent.click(screen.getByRole("button", {name:"Publier la revue et transmettre"}));
  await waitFor(() => expect(record).toHaveBeenCalledOnce());
  expect(record).toHaveBeenCalledWith("case-1", expect.objectContaining({
    outcome_id: "outcome-won",
    submission_package_id: "package-p5"
  }));
  expect(await screen.findByText("Réserve de lancement à lever · échéance UNKNOWN")).toBeInTheDocument();
  expect(screen.getByText(/P7 ≠ ordre de service/)).toBeInTheDocument();
  expect(screen.getByText(/Rapprochement contrat \/ offre : UNKNOWN/)).toBeInTheDocument();
  expect(screen.queryByText(/marge brute/i)).not.toBeInTheDocument();
  vi.stubGlobal("URL", {
    createObjectURL: vi.fn(() => "blob:test"),
    revokeObjectURL: vi.fn()
  });
  fireEvent.click(screen.getByRole("button", {
    name: "Télécharger l’offre technique exacte"
  }));
  await waitFor(() => expect(api.downloadCaseHandoverOffer).toHaveBeenCalledWith("case-1", "stable-id"));
  rerender(<CaseHandoverPanel api={api} caseId="case-1" canManage={false} />);
  expect(await screen.findByText("Réserve de lancement à lever · échéance UNKNOWN")).toBeInTheDocument();
  expect(screen.queryByRole("button", {
    name: "Transmettre au Conducteur"
  })).not.toBeInTheDocument();
  vi.unstubAllGlobals();
});
test("un résultat de transmission non confirmé rejoue les mêmes identifiants", async () => {
  vi.stubGlobal("crypto", {
    randomUUID: vi.fn(() => "same-id")
  });
  const record = vi.fn().mockRejectedValueOnce(new Error("network interruption")).mockResolvedValueOnce({
    status: "SUCCEEDED",
    result_code: "CASE_HANDOVER_SNAPSHOT_RECORDED",
    replayed: true
  });
  const api = makeApi(record);
  render(<CaseHandoverPanel api={api} caseId="case-1" canManage />);
  fireEvent.change(await screen.findByLabelText("Offre gagnée exacte à transmettre"), {
    target: {
      value: "outcome-won:package-p5"
    }
  });
  fireEvent.change(await screen.findByLabelText("Point opérationnel 1"), {target:{value:"Transport exclu de la fourniture."}});
  fireEvent.change(screen.getByLabelText("Justification de la revue"), {target:{value:"Sources relues pour transmission opérationnelle."}});
  fireEvent.click(screen.getByLabelText(/Je confirme la publication opérationnelle/));
  fireEvent.click(screen.getByRole("button", {name:"Publier la revue et transmettre"}));
  expect(await screen.findByText(/résultat non confirmé/i)).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", {
    name: "Réessayer la même passation"
  }));
  await waitFor(() => expect(record).toHaveBeenCalledTimes(2));
  expect(record.mock.calls[1]).toEqual(record.mock.calls[0]);
  vi.unstubAllGlobals();
});
test("masque immédiatement l’ancienne Affaire et refuse son GET tardif", async () => {
  let finish!: (value: CaseHandoverSnapshots) => void;
  const first = new Promise<CaseHandoverSnapshots>(resolve => {
    finish = resolve;
  });
  const api = makeApi();
  vi.mocked(api.listCaseHandoverSnapshots).mockReturnValueOnce(first).mockResolvedValueOnce({
    case_id: "case-2",
    items: []
  });
  const {
    rerender
  } = render(<CaseHandoverPanel api={api} caseId="case-1" canManage={false} ownerKey="owner-a" />);
  rerender(<CaseHandoverPanel api={api} caseId="case-2" canManage={false} ownerKey="owner-a" />);
  finish(snapshots);
  expect(await screen.findByText(/aucune passation P7/)).toBeInTheDocument();
  expect(screen.queryByText("Réserve de lancement à lever · échéance UNKNOWN")).not.toBeInTheDocument();
});
test("un reçu inconnu fige la vue et rejoue le même acte conducteur", async () => {
  const api = makeApi();
  const row = {
    ...snapshots.items[0],
    view_sha256: "d".repeat(64),
    source_state: "CURRENT",
    receipts: []
  };
  vi.mocked(api.listCaseHandoverSnapshots).mockResolvedValue({
    case_id: "case-1",
    items: [row]
  });
  const acknowledge = vi.fn().mockRejectedValue(new Error("lost receipt"));
  api.acknowledgeCaseHandover = acknowledge;
  render(<CaseHandoverPanel api={api} caseId="case-1" canManage={false} canReceive ownerKey="driver" />);
  fireEvent.change(await screen.findByLabelText("Note de réception"), {
    target: {
      value: "Reçu avec les inconnus affichés."
    }
  });
  fireEvent.click(screen.getByRole("checkbox"));
  fireEvent.click(screen.getByRole("button", {
    name: "Enregistrer le reçu du dossier"
  }));
  expect(await screen.findByText(/UNKNOWN · intention figée/)).toBeInTheDocument();
  expect(screen.queryByLabelText("Note de réception")).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", {
    name: "Réessayer la même passation"
  }));
  await waitFor(() => expect(acknowledge).toHaveBeenCalledTimes(2));
  expect(acknowledge.mock.calls[1]).toEqual(acknowledge.mock.calls[0]);
  expect(api.listCaseHandoverSnapshots).toHaveBeenCalledOnce();
});
test("un changement de session masque les points et n’expose pas l’intention privée", async () => {
  const api = makeApi();
  const {
    rerender
  } = render(<CaseHandoverPanel api={api} caseId="case-1" canManage ownerKey="patron-session" />);
  expect(await screen.findByText("Réserve de lancement à lever · échéance UNKNOWN")).toBeInTheDocument();
  let finish!: (value: CaseHandoverSnapshots) => void;
  vi.mocked(api.listCaseHandoverSnapshots).mockReturnValue(new Promise(resolve => {
    finish = resolve;
  }));
  rerender(<CaseHandoverPanel api={api} caseId="case-1" canManage={false} ownerKey="other-session" />);
  expect(screen.queryByText("Réserve de lancement à lever · échéance UNKNOWN")).not.toBeInTheDocument();
  expect(screen.queryByLabelText("Offre gagnée exacte à transmettre")).not.toBeInTheDocument();
  finish({
    case_id: "case-1",
    items: []
  });
});

test("ne propose aucun raccourci d’écriture sans revue humaine confirmée", async () => {
  const api=makeApi();
  render(<CaseHandoverPanel api={api} caseId="case-1" canManage />);
  await screen.findByLabelText("Offre gagnée exacte à transmettre");
  expect(screen.queryByRole("button",{name:"Transmettre au Conducteur"})).not.toBeInTheDocument();
  expect(api.recordCaseHandover).not.toHaveBeenCalled();
});

test.each(["COMMAND_IN_PROGRESS", undefined])("un409 non terminal conserve l’intention incertaine (%s)", async detail => {
  const record=vi.fn().mockRejectedValue(Object.assign(new Error("Command not confirmed"),{status:409,detail}));
  const api=makeApi(record);
  render(<CaseHandoverPanel api={api} caseId="case-1" canManage />);
  fireEvent.change(await screen.findByLabelText("Offre gagnée exacte à transmettre"),{target:{value:"outcome-won:package-p5"}});
  fireEvent.change(await screen.findByLabelText("Point opérationnel 1"),{target:{value:"Transport exclu."}});
  fireEvent.change(screen.getByLabelText("Justification de la revue"),{target:{value:"Sources relues pour le conducteur."}});
  fireEvent.click(screen.getByLabelText(/Je confirme la publication opérationnelle/));
  fireEvent.click(screen.getByRole("button",{name:"Publier la revue et transmettre"}));
  expect(await screen.findByText("UNKNOWN · intention figée")).toBeInTheDocument();
  expect(screen.getByRole("button",{name:"Publier la revue et transmettre"})).toBeDisabled();
  fireEvent.click(screen.getByRole("button",{name:"Réessayer la même passation"}));
  await waitFor(()=>expect(record).toHaveBeenCalledTimes(2));
  expect(record.mock.calls[1]).toEqual(record.mock.calls[0]);
});


test("shows DOCX paragraph provenance without presenting text offsets as ZIP offsets", () => {
  const item = structuredClone(snapshots.items[0]);
  item.snapshot.operational_review = {state:"PUBLISHED",points:[{
    point_id:"docx-point",kind:"ENGAGEMENT",statement:"Relire la pièce.",
    offer_excerpt:"KBIS à relire.",offer_locator:"Mémoire exact",difference_state:"UNKNOWN",
    criticality:"CRITICAL",responsible:null
  }],missing:["RESPONSIBLE:docx-point"],completeness:"PARTIAL",analysis_complete:false};
  item.snapshot.offer_point_proofs = {"docx-point":{
    state:"EXACT_DOCX_TEXT_MATCH",document_id:"technical-doc",document_version:2,
    source_sha256:"c".repeat(64),start_byte_offset:null,end_byte_offset:null,
    contract_excerpt_state:"UNKNOWN",locator:"word/document.xml:/w:document/w:body/w:p[2]",
    part_sha256:"d".repeat(64),text_sha256:"e".repeat(64),text_start_byte_offset:4,text_end_byte_offset:19
  }};
  render(<HandoverSnapshotRead item={item} canReceive={false} disabled={false} onDownload={vi.fn()} onReceive={vi.fn()}/>);
  expect(screen.getByText(/Source DOCX : word\/document.xml:/)).toBeInTheDocument();
  expect(screen.getByText(/Plage UTF-8 du paragraphe : 4–19/)).toBeInTheDocument();
  expect(screen.getByText(/Responsable déclaré : UNKNOWN/)).toBeInTheDocument();
  expect(screen.getByText(/aucune complétude déduite/)).toBeInTheDocument();
});

test("suspends handover reads while DCE sources are uncertain", () => {
  const api = makeApi();
  render(<CaseHandoverPanel api={api} caseId="case-1" canManage sourceReadBlocked/>);
  expect(screen.getByRole("status")).toHaveTextContent("Sources en cours de reprise");
  expect(api.listCaseHandoverSnapshots).not.toHaveBeenCalled();
  expect(screen.queryByLabelText("Offre gagnée exacte à transmettre")).not.toBeInTheDocument();
});

test("rereads a new source scope and ignores the late previous reply", async () => {
  let finish!: (value: CaseHandoverSnapshots) => void;
  const get = vi.fn().mockImplementationOnce(() => new Promise<CaseHandoverSnapshots>(resolve => {finish=resolve;})).mockResolvedValue({...snapshots,items:[]});
  const api = {...makeApi(),listCaseHandoverSnapshots:get} as ApiClient;
  const {rerender} = render(<CaseHandoverPanel api={api} caseId="case-1" canManage={false} ownerKey="owner" scopeKey="v1"/>);
  rerender(<CaseHandoverPanel api={api} caseId="case-1" canManage={false} ownerKey="owner" scopeKey="v2"/>);
  await waitFor(() => expect(get).toHaveBeenCalledTimes(2));
  finish(snapshots);
  await screen.findByText(/aucune passation P7 n’a encore été enregistrée/);
  expect(screen.queryByText("Réserve de lancement à lever · échéance UNKNOWN")).not.toBeInTheDocument();
});

test.each(["command_id","idempotency_key"])("keeps a discordant %s UNKNOWN without reconciling, then retries exactly", async field => {
  const record = vi.fn().mockImplementationOnce(async (_case, input) => ({status:"SUCCEEDED",result_code:"CASE_HANDOVER_SNAPSHOT_RECORDED",command_id:input.command_id,idempotency_key:input.idempotency_key,[field]:"foreign-receipt"})).mockImplementationOnce(async (_case,input) => ({status:"SUCCEEDED",result_code:"CASE_HANDOVER_SNAPSHOT_RECORDED",command_id:input.command_id,idempotency_key:input.idempotency_key}));
  const api = makeApi(record);
  render(<CaseHandoverPanel api={api} caseId="case-1" canManage/>);
  fireEvent.change(await screen.findByLabelText("Offre gagnée exacte à transmettre"),{target:{value:"outcome-won:package-p5"}});
  fireEvent.change(await screen.findByLabelText("Point opérationnel 1"),{target:{value:"Point sourcé avec manques explicites."}});
  fireEvent.change(screen.getByLabelText("Justification de la revue"),{target:{value:"Sources relues pour cet acte exact."}});
  fireEvent.click(screen.getByLabelText(/Je confirme la publication opérationnelle/));
  fireEvent.click(screen.getByRole("button",{name:"Publier la revue et transmettre"}));
  await screen.findByText(/UNKNOWN · intention figée/);
  expect(api.listCaseHandoverSnapshots).toHaveBeenCalledTimes(1);
  fireEvent.click(screen.getByRole("button",{name:"Réessayer la même passation"}));
  await waitFor(() => expect(record).toHaveBeenCalledTimes(2));
  expect(record.mock.calls[1]).toEqual(record.mock.calls[0]);
  await screen.findByText("Acte exact relu depuis le serveur.");
});

test("preserves the frozen publication through source suspension and resumes the identical intent", async () => {
  const record = vi.fn().mockRejectedValueOnce(new Error("reply lost")).mockImplementationOnce(async (_case,input) => ({status:"SUCCEEDED",result_code:"CASE_HANDOVER_SNAPSHOT_RECORDED",command_id:input.command_id,idempotency_key:input.idempotency_key}));
  const api = makeApi(record);
  const props = {api,caseId:"case-1",canManage:true,ownerKey:"owner",pendingStore:new HandoverIntentStore()};
  const {rerender} = render(<CaseHandoverPanel {...props} scopeKey="v1"/>);
  fireEvent.change(await screen.findByLabelText("Offre gagnée exacte à transmettre"),{target:{value:"outcome-won:package-p5"}});
  fireEvent.change(await screen.findByLabelText("Point opérationnel 1"),{target:{value:"Point synthétique déclaré."}});
  fireEvent.change(screen.getByLabelText("Justification de la revue"),{target:{value:"Acte exact à reprendre."}});
  fireEvent.click(screen.getByLabelText(/Je confirme la publication opérationnelle/));
  fireEvent.click(screen.getByRole("button",{name:"Publier la revue et transmettre"}));
  await screen.findByText(/UNKNOWN · intention figée/);
  rerender(<CaseHandoverPanel {...props} scopeKey="v2" sourceReadBlocked/>);
  expect(screen.queryByRole("button",{name:"Réessayer la même passation"})).not.toBeInTheDocument();
  rerender(<CaseHandoverPanel {...props} scopeKey="v2"/>);
  expect(api.listCaseHandoverSnapshots).toHaveBeenCalledTimes(1);
  fireEvent.click(await screen.findByRole("button",{name:"Réessayer la même passation"}));
  await screen.findByText("Acte exact relu depuis le serveur.");
  expect(record.mock.calls[1]).toEqual(record.mock.calls[0]);
});
