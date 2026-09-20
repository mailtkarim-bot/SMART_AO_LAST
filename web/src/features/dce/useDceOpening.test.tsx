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

function makeApi(overrides: Partial<OpeningApi> = {}): OpeningApi {
  return {
    getConsultation: vi.fn().mockResolvedValue(consultation),
    prepareDceStaging: vi.fn().mockResolvedValue(preparation),
    uploadDceStagedObjectContent: vi.fn().mockResolvedValue(upload),
    registerDceVersion: vi.fn().mockResolvedValue(admission),
    linkCaseDceVersion: vi.fn().mockResolvedValue({
      ...admission,
      result_code: "CASE_DCE_APPLICABILITY_SET",
    }),
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
      prepareDceStaging: vi.fn().mockImplementation(async () => {
        calls.push("prepare");
        return preparation;
      }),
      uploadDceStagedObjectContent: vi.fn().mockImplementation(async () => {
        calls.push("upload");
        return upload;
      }),
      registerDceVersion: vi.fn().mockImplementation(async () => {
        calls.push("register");
        return admission;
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
      "idempotency-prepare-1",
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
      prepareDceStaging: vi.fn().mockResolvedValue({ ...preparation, replayed: true }),
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
