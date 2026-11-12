import type { Dispatch, SetStateAction } from "react";

import { act, renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ApiClient } from "../../infrastructure/api";
import type {
  AssignedCase,
  ConsultationProjection,
  DceDocumentInventory,
  DceStagingPreparationReceipt,
  DceUploadReceipt,
  RegisterDceVersionReceipt,
  DceVersionMetadata,
} from "../../shared/types";
import { useDceOpening } from "./useDceOpening";

type HookMessage = { tone: "success" | "error" | "warning"; text: string };
type OpeningApi = Pick<
  ApiClient,
  | "getConsultation"
  | "prepareDceStaging"
  | "uploadDceStagedObjectContent"
  | "registerDceVersion"
  | "linkCaseDceVersion"
  | "getDceVersion"
  | "listDceVersionDocuments"
>;

const selectedCase: AssignedCase = {
  case_id: "case-1",
  work_label: "Réhabilitation du groupe scolaire",
  case_lifecycle: "PREPARATION",
  commercial_stage: "QUALIFICATION",
  dce_availability: "AVAILABLE",
  consultation_id: "consultation-server-1",
  applicable_dce_version_id: "dce-version-server-1",
};

const unlinkedCase: AssignedCase = {
  ...selectedCase,
  case_id: "case-2",
  consultation_id: null,
  applicable_dce_version_id: null,
};

const consultation: ConsultationProjection = {
  id: "consultation-server-1",
  buyer_legal_name: "Ville d'Exemple",
  external_reference: "REF-2026-001",
  object_label: "Travaux de réhabilitation",
  location_label: "Exemple-sur-Mer",
  lifecycle: "PUBLISHED",
  freshness: "CURRENT",
  aggregate_revision: 4,
  lots: ["01", "02"],
  tranches: [],
  projection_status: "READY",
};

const metadata: DceVersionMetadata = {
  id: "dce-version-server-1",
  consultation_id: "consultation-server-1",
  predecessor_dce_version_id: null,
  source_received_at: "2026-09-01T10:00:00Z",
  lifecycle: "ADMITTED",
  integrity: "VERIFIED",
  classification_readiness: "CLASSIFIED",
  analysis_readiness: "READY",
  aggregate_revision: 2,
};

const inventory: DceDocumentInventory = {
  dce_version_id: "dce-version-server-1",
  items: [],
};

const preparation: DceStagingPreparationReceipt = {
  status: "SUCCEEDED",
  command_id: "command-prepare-1",
  idempotency_key: "idempotency-prepare-1",
  result_code: "DCE_STAGING_PREPARED",
  aggregate_refs: [],
  event_ids: ["event-prepare-1"],
  staging: {
    storage_object_id: "storage-object-1",
    state: "AWAITING_UPLOAD",
    expires_at: "2026-09-20T14:00:00Z",
  },
  replayed: false,
};

const upload: DceUploadReceipt = {
  storage_object_id: "storage-object-1",
  state: "CLEAN",
};

const admission: RegisterDceVersionReceipt = {
  status: "SUCCEEDED",
  command_id: "command-admission-1",
  idempotency_key: "idempotency-admission-1",
  result_code: "DCE_VERSION_REGISTERED",
  aggregate_refs: [
    { aggregate_type: "DCE_VERSION", aggregate_id: "dce-version-2", aggregate_revision: 1 },
  ],
  event_ids: ["event-admission-1"],
  replayed: false,
};

async function sha256Hex(data: BufferSource): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", data);
  return Array.from(new Uint8Array(digest))
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}

function renderOpeningHook(
  api: OpeningApi,
  setMessage: Dispatch<SetStateAction<HookMessage | null>>,
  currentCase: AssignedCase | undefined = selectedCase,
  onAdmitted: () => Promise<void> | void = vi.fn(),
) {
  return renderHook(() =>
    useDceOpening(api as ApiClient, setMessage, currentCase, onAdmitted),
  );
}

function admissionFor(input: Parameters<OpeningApi["registerDceVersion"]>[0]) {
 return { ...admission, command_id: input.command_id!, idempotency_key: input.idempotency_key!, aggregate_refs: [{aggregate_type:"DCE",aggregate_id:input.dce_version_id,aggregate_revision:0}] };
}
function preparationFor(input: Parameters<OpeningApi["prepareDceStaging"]>[0]) {
 return {...preparation, command_id:input.command_id!, idempotency_key:input.idempotency_key!};
}
function makeApi(overrides: Partial<OpeningApi> = {}): OpeningApi {
  return {
    getConsultation: vi.fn().mockResolvedValue(consultation),
    prepareDceStaging: vi.fn().mockImplementation(preparationFor),
    uploadDceStagedObjectContent: vi.fn().mockResolvedValue(upload),
    registerDceVersion: vi.fn().mockImplementation(admissionFor),
    linkCaseDceVersion: vi.fn().mockImplementation(async (caseId, input) => ({
      ...admission, command_id: input.command_id!, idempotency_key: input.idempotency_key!,
      result_code: "CASE_DCE_APPLICABILITY_SET", aggregate_refs: [{aggregate_type:"AFF",aggregate_id:caseId,aggregate_revision:(input.expected_case_revision ?? 0)+1}],
    })),
    getDceVersion: vi.fn().mockResolvedValue(metadata),
    listDceVersionDocuments: vi.fn().mockResolvedValue(inventory),
    ...overrides,
  } satisfies OpeningApi;
}

describe("useDceOpening", () => {
  it("opens the space from the server references only", async () => {
    const api = makeApi();
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result: hook } = renderOpeningHook(api, setMessage);

    await act(async () => {
      await hook.current.openSpace();
    });

    expect(api.getConsultation).toHaveBeenCalledWith("consultation-server-1");
    expect(api.getDceVersion).toHaveBeenCalledWith("dce-version-server-1");
    expect(api.listDceVersionDocuments).toHaveBeenCalledWith("dce-version-server-1");
    expect(hook.current.consultation?.aggregate_revision).toBe(4);
    expect(hook.current.inventory?.dce_version_id).toBe("dce-version-server-1");
  });

  it("refuses cleanly when the case has no linked consultation", async () => {
    const api = makeApi();
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result: hook } = renderOpeningHook(api, setMessage, unlinkedCase);

    await act(async () => {
      await hook.current.openSpace();
    });

    expect(api.getConsultation).not.toHaveBeenCalled();
    expect(api.getDceVersion).not.toHaveBeenCalled();
    expect(api.listDceVersionDocuments).not.toHaveBeenCalled();
    expect(hook.current.consultation).toBeNull();
    expect(setMessage).toHaveBeenCalledWith(
      expect.objectContaining({ tone: "warning" }),
    );
  });

  it("runs prepare, upload then register in order with the canonical corpus hash", async () => {
    const bytes = new TextEncoder().encode("contenu dce connu");
    const file = new File([bytes], "cce.pdf", { type: "application/pdf" });
    const calls: string[] = [];
    const api = makeApi({
      prepareDceStaging: vi.fn().mockImplementation(async input => {
        calls.push("prepare");
        return preparationFor(input);
      }),
      uploadDceStagedObjectContent: vi.fn().mockImplementation(async () => {
        calls.push("upload");
        return upload;
      }),
      registerDceVersion: vi.fn().mockImplementation(async input => {
        calls.push("register");
        return admissionFor(input);
      }),
    });
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result: hook } = renderOpeningHook(api, setMessage);
    await act(async () => {
      await hook.current.openSpace();
    });
    await act(async () => {
      hook.current.setFile(file);
    });

    await act(async () => {
      await hook.current.admitSelectedFile();
    });

    expect(calls).toEqual(["prepare", "upload", "register"]);
    expect(api.prepareDceStaging).toHaveBeenCalledWith(
      expect.objectContaining({
        consultation_id: "consultation-server-1",
        consultation_revision: 4,
        original_filename: "cce.pdf",
        expected_byte_size: bytes.length,
        source_channel: "MANUAL_UPLOAD",
      }),
    );
    const expiresAt = (api.prepareDceStaging as ReturnType<typeof vi.fn>).mock
      .calls[0]?.[0] as { expires_at: string };
    expect(new Date(expiresAt.expires_at).getTime() - Date.now()).toBeGreaterThan(0);

    expect(api.uploadDceStagedObjectContent).toHaveBeenCalledWith(
      "storage-object-1",
      vi.mocked(api.prepareDceStaging).mock.calls[0][0].idempotency_key,
      file,
    );

    const fileHash = await sha256Hex(bytes);
    const expectedCorpus = await sha256Hex(
      new TextEncoder().encode([fileHash].sort().join("\n")),
    );
    const registerInput = (api.registerDceVersion as ReturnType<typeof vi.fn>).mock
      .calls[0]?.[0] as Record<string, unknown>;
    expect(registerInput.corpus_hash).toBe(expectedCorpus);
    expect(registerInput.consultation_id).toBe("consultation-server-1");
    expect(registerInput.consultation_revision).toBe(4);
    expect(registerInput.documents).toEqual([
      { document_id: expect.any(String), storage_object_id: "storage-object-1" },
    ]);
    expect(api.linkCaseDceVersion).toHaveBeenCalledWith(
      "case-1",
      expect.objectContaining({
        dce_version_id: expect.any(String),
        reason: expect.stringContaining("Version DCE admise"),
      }),
    );
  });

  it("confirms an idempotent replay without raising an error", async () => {
    const api = makeApi({
      prepareDceStaging: vi.fn().mockImplementation(input => ({ ...preparationFor(input), replayed: true })),
    });
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result: hook } = renderOpeningHook(api, setMessage);
    await act(async () => {
      await hook.current.openSpace();
    });
    await act(async () => {
      hook.current.setFile(new File(["x"], "cce.pdf"));
    });

    await act(async () => {
      await hook.current.admitSelectedFile();
    });

    expect(setMessage).toHaveBeenCalledWith(
      expect.objectContaining({ text: expect.stringContaining("Rejeu idempotent confirmé") }),
    );
    expect(api.registerDceVersion).toHaveBeenCalled();
  });

  it("stops the chain when the upload fails and never registers the version", async () => {
    const api = makeApi({
      uploadDceStagedObjectContent: vi
        .fn()
        .mockRejectedValue(Object.assign(new Error("UPLOAD_REJECTED"), { status: 422 })),
    });
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result: hook } = renderOpeningHook(api, setMessage);
    await act(async () => {
      await hook.current.openSpace();
    });
    await act(async () => {
      hook.current.setFile(new File(["x"], "cce.pdf"));
    });

    await act(async () => {
      await hook.current.admitSelectedFile();
    });

    expect(api.prepareDceStaging).toHaveBeenCalled();
    expect(api.registerDceVersion).not.toHaveBeenCalled();
    expect(setMessage).toHaveBeenCalledWith(
      expect.objectContaining({ tone: "error", text: "UPLOAD_REJECTED" }),
    );
  });

  it("calls onAdmitted then reloads the space after a successful admission", async () => {
    const api = makeApi();
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const calls: string[] = [];
    const onAdmitted = vi.fn().mockImplementation(async () => {
      calls.push("onAdmitted");
    });
    const getConsultation = vi.fn().mockImplementation(async () => {
      calls.push("getConsultation");
      return consultation;
    });
    api.getConsultation = getConsultation;
    const { result: hook } = renderOpeningHook(api, setMessage, selectedCase, onAdmitted);

    await act(async () => {
      await hook.current.openSpace();
    });
    calls.length = 0;
    await act(async () => {
      hook.current.setFile(new File(["x"], "cce.pdf"));
    });

    await act(async () => {
      await hook.current.admitSelectedFile();
    });

    expect(onAdmitted).toHaveBeenCalledOnce();
    expect(calls[0]).toBe("onAdmitted");
    expect(calls[1]).toBe("getConsultation");
    expect(setMessage).toHaveBeenCalledWith(
      expect.objectContaining({ tone: "success" }),
    );
  });
});


it("masque immédiatement l’inventaire V1 lorsque la version applicable devient V2", async()=>{
  const api=makeApi();const setMessage=vi.fn();
  const {result,rerender}=renderHook(({current})=>useDceOpening(api as ApiClient,setMessage,current,vi.fn()),{initialProps:{current:selectedCase}});
  await act(async()=>{await result.current.openSpace();});
  expect(result.current.inventory?.dce_version_id).toBe("dce-version-server-1");
  rerender({current:{...selectedCase,applicable_dce_version_id:"v2"}});
  expect(result.current.inventory).toBeNull();
  expect(result.current.dceVersionMetadata).toBeNull();
});


it("reprend l’admission UNKNOWN avec les mêmes IDs sans refaire le staging", async()=>{
 const api=makeApi({registerDceVersion:vi.fn().mockRejectedValueOnce(new Error("UNKNOWN")).mockImplementation(admissionFor)});const setMessage=vi.fn();
 const {result}=renderOpeningHook(api,setMessage);
 await act(async()=>{await result.current.openSpace();});
 const file=new File(["source"],"rc.txt",{type:"text/plain"});Object.defineProperty(file,"arrayBuffer",{value:async()=>new TextEncoder().encode("source").buffer});
 act(()=>result.current.setFile(file));
 await act(async()=>{await result.current.admitSelectedFile();});
 await act(async()=>{await result.current.admitSelectedFile();});
 expect(api.prepareDceStaging).toHaveBeenCalledTimes(1);
 expect(api.uploadDceStagedObjectContent).toHaveBeenCalledTimes(1);
 expect(api.registerDceVersion).toHaveBeenCalledTimes(2);
 const calls=vi.mocked(api.registerDceVersion).mock.calls;expect(calls[1][0]).toEqual(calls[0][0]);
});


it("ne rattache aucune version sur un reçu d’admission discordant", async()=>{
 const api=makeApi({registerDceVersion:vi.fn().mockResolvedValue(admission)});const setMessage=vi.fn();const {result}=renderOpeningHook(api,setMessage);
 await act(async()=>{await result.current.openSpace();});
 const file=new File(["source"],"rc.txt",{type:"text/plain"});Object.defineProperty(file,"arrayBuffer",{value:async()=>new TextEncoder().encode("source").buffer});
 act(()=>result.current.setFile(file));await act(async()=>{await result.current.admitSelectedFile();});
 expect(api.linkCaseDceVersion).not.toHaveBeenCalled();
 expect(result.current.pending).toBe(true);
});


it("conserve la reprise en lecture après rattachement confirmé si la relecture échoue",async()=>{
 const getConsultation=vi.fn().mockResolvedValueOnce(consultation).mockRejectedValueOnce(new Error("READ_FAILED")).mockResolvedValue(consultation);
 const api=makeApi({getConsultation,getDceVersion:vi.fn(async id=>({...metadata,id})),listDceVersionDocuments:vi.fn(async id=>({...inventory,dce_version_id:id}))});
 const setMessage=vi.fn();const {result}=renderOpeningHook(api,setMessage);await act(async()=>{await result.current.openSpace();});
 const file=new File(["source"],"rc.txt");Object.defineProperty(file,"arrayBuffer",{value:async()=>new TextEncoder().encode("source").buffer});act(()=>result.current.setFile(file));
 await act(async()=>{await result.current.admitSelectedFile();});expect(result.current.pending).toBe(true);
 await act(async()=>{await result.current.admitSelectedFile();});
 expect(api.registerDceVersion).toHaveBeenCalledTimes(1);expect(api.linkCaseDceVersion).toHaveBeenCalledTimes(1);
 expect(result.current.pending).toBe(false);
});


it("admet un seul corpus pour plusieurs fichiers sélectionnés",async()=>{
 const api=makeApi({prepareDceStaging:vi.fn(input=>Promise.resolve({...preparationFor(input),staging:{...preparation.staging,storage_object_id:input.original_filename}})),uploadDceStagedObjectContent:vi.fn(id=>Promise.resolve({...upload,storage_object_id:id}))});
 const {result}=renderOpeningHook(api,vi.fn());await act(async()=>{await result.current.openSpace();});
 const files=["a","b"].map(name=>{const f=new File([name],name+".pdf");Object.defineProperty(f,"arrayBuffer",{value:async()=>new TextEncoder().encode(name).buffer});return f;});
 expect(result.current).toHaveProperty("setFiles");act(()=>{result.current.setFiles(files);});
 await act(async()=>{await result.current.admitSelectedFile();});
 expect(api.prepareDceStaging).toHaveBeenCalledTimes(2);expect(api.registerDceVersion).toHaveBeenCalledTimes(1);
 const input=vi.mocked(api.registerDceVersion).mock.calls[0][0];expect(input.documents).toHaveLength(2);
 const hashes=await Promise.all(files.map(async f=>sha256Hex(await f.arrayBuffer())));
 expect(input.corpus_hash).toBe(await sha256Hex(new TextEncoder().encode(hashes.sort().join("\n"))));
});


it("ne conclut pas au rattachement sur un reçu discordant",async()=>{
 const api=makeApi({linkCaseDceVersion:vi.fn().mockResolvedValue({...admission,result_code:"CASE_DCE_APPLICABILITY_SET"})});const done=vi.fn();const {result}=renderOpeningHook(api,vi.fn(),selectedCase,done);
 await act(async()=>{await result.current.openSpace();});const file=new File(["source"],"rc.txt");Object.defineProperty(file,"arrayBuffer",{value:async()=>new TextEncoder().encode("source").buffer});act(()=>result.current.setFile(file));
 await act(async()=>{await result.current.admitSelectedFile();});expect(done).not.toHaveBeenCalled();expect(result.current.pending).toBe(true);
});

it("arrête les lectures dépendantes lorsque la consultation tardive appartient à l’ancien périmètre",async()=>{
 let release!:(value:ConsultationProjection)=>void;const api=makeApi({getConsultation:vi.fn(()=>new Promise<ConsultationProjection>(done=>{release=done;}))});const setMessage=vi.fn();
 const {result,rerender}=renderHook(({current})=>useDceOpening(api as ApiClient,setMessage,current,vi.fn()),{initialProps:{current:selectedCase}});let request!:Promise<void>;
 act(()=>{request=result.current.openSpace();});rerender({current:{...selectedCase,case_id:"new-case",applicable_dce_version_id:"new-version"}});
 await act(async()=>{release(consultation);await request;});expect(api.getDceVersion).not.toHaveBeenCalled();expect(result.current.inventory).toBeNull();
});

it.each(["vide","volume","nombre","doublon"])("refuse le corpus %s avant tout staging",async(kind)=>{
 const api=makeApi();const {result}=renderOpeningHook(api,vi.fn());await act(async()=>{await result.current.openSpace();});const file=new File(kind==="vide"?[]:["x"],"source.pdf");Object.defineProperty(file,"arrayBuffer",{value:async()=>new TextEncoder().encode("x").buffer});
 if(kind==="volume")Object.defineProperty(file,"size",{value:150000001});const files=kind==="nombre"?Array(101).fill(file):kind==="doublon"?[file,file]:[file];
 act(()=>result.current.setFiles(files));await act(async()=>{await result.current.admitSelectedFile();});expect(api.prepareDceStaging).not.toHaveBeenCalled();expect(api.registerDceVersion).not.toHaveBeenCalled();
});


it("ne montre pas le motif privé ou la sélection d’un autre propriétaire",()=>{
 const api=makeApi();const setMessage=vi.fn();const {result,rerender}=renderHook(({owner})=>useDceOpening(api as ApiClient,setMessage,selectedCase,vi.fn(),owner),{initialProps:{owner:"owner-A"}});
 act(()=>{result.current.setSourceChannel("RECTIFICATION");result.current.setReplacementReason("PRIVATE_OWNER_A");result.current.setFiles([new File(["a"],"private-A.pdf")]);});
 rerender({owner:"owner-B"});expect(result.current.replacementReason).toBe("");expect(result.current.sourceChannel).toBe("MANUAL_UPLOAD");expect(result.current.file).toBeNull();expect(result.current.step).toBe("IDLE");
});
