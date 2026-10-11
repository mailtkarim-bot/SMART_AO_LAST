import type { Dispatch, SetStateAction } from "react";
import { act, renderHook } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { ApiClient } from "../../infrastructure/api";
import type {
  SubmissionEvidenceReceipt,
  SubmissionEvidenceProjection,
  SubmissionPackageAuthorizationReceipt,
  SubmissionPackageManifestProjection,
  SubmissionPackageReceipt,
  SubmissionSignatureProjection,
  SubmissionSignatureReceipt,
} from "../../shared/types";
import { useSubmissionActions } from "./useSubmissionActions";

type HookMessage = { tone: "success" | "error" | "warning"; text: string };
type SubmissionApi = Pick<
  ApiClient,
  | "prepareSubmissionPackage"
  | "authorizeSubmissionPackage"
  | "getSubmissionPackageManifest"
  | "getSubmissionEvidence"
  | "downloadSubmissionPackage"
  | "recordSubmissionEvidence"
>;
type SignatureApi = SubmissionApi &
  Pick<ApiClient, "requestSubmissionSignature" | "getSubmissionSignature">;

const packageReceipt = (replayed = false): SubmissionPackageReceipt => ({
  status: "SUCCEEDED",
  command_id: "command-submission-1",
  idempotency_key: "idempotency-submission-1",
  result_code: "SUBMISSION_PACKAGE_PREPARED",
  aggregate_refs: [
    {
      aggregate_type: "SubmissionPackage",
      aggregate_id: "submission-package-1",
      aggregate_revision: 1,
    },
  ],
  event_ids: ["event-submission-1"],
  replayed,
});

const authorizationReceipt = (replayed = false): SubmissionPackageAuthorizationReceipt => ({
  status: "SUCCEEDED",
  command_id: "command-authorization-1",
  idempotency_key: "idempotency-authorization-1",
  result_code: "SUBMISSION_PACKAGE_AUTHORIZED",
  aggregate_refs: [
    {
      aggregate_type: "SubmissionPackageAuthorization",
      aggregate_id: "authorization-1",
      aggregate_revision: 1,
    },
  ],
  event_ids: ["event-authorization-1"],
  replayed,
});

const manifestProjection = (authorized: "AUTHORIZED" | "NOT_AUTHORIZED" = "NOT_AUTHORIZED"): SubmissionPackageManifestProjection => ({
  submission_package_id: "submission-package-1",
  package_version: 3,
  state: authorized === "AUTHORIZED" ? "AUTORISE_DEPOT" : "PRET_CONTROLE",
  manifest_sha256: "c".repeat(64),
  manifest: { entries: [{ path: "dce/index.pdf" }], exclusions: ["storage_key", "amounts"] },
  authorization_status: authorized,
  external_submission: "NOT_PERFORMED",
});

const c10ManifestProjection = (): SubmissionPackageManifestProjection => ({
  ...manifestProjection(),
  manifest: {
    ...manifestProjection().manifest,
    preparation_source: { snapshot_id: "snapshot-1" },
  },
});

const evidenceProjection = (): SubmissionEvidenceProjection[] => [{
  evidence_id: "evidence-1",
  submission_package_id: "submission-package-1",
  package_version: 3,
  manifest_sha256: "c".repeat(64),
  evidence_type: "MANUAL_RECEIPT",
  status: "RECEIVED",
  reconciliation_status: "PARTIAL",
  external_submission: "NOT_PERFORMED",
}];

const signatureReceipt = (): SubmissionSignatureReceipt => ({
  status: "SUCCEEDED",
  command_id: "command-signature-1",
  idempotency_key: "idempotency-signature-1",
  result_code: "SUBMISSION_SIGNATURE_REQUESTED",
  aggregate_refs: [
    {
      aggregate_type: "SubmissionSignature",
      aggregate_id: "signature-1",
      aggregate_revision: 1,
    },
  ],
  event_ids: ["event-signature-1"],
  replayed: false,
  external_submission: "NOT_PERFORMED",
});

const signatureProjection = (): SubmissionSignatureProjection => ({
  signature_id: "signature-1",
  submission_package_id: "submission-package-1",
  case_id: "case-1",
  provider: "TEST_PROVIDER",
  status: "SIGNED",
  expected_package_version: 2,
  manifest_sha256: "c".repeat(64),
  revision: 2,
  external_submission: "NOT_PERFORMED",
});

const evidenceReceipt = (): SubmissionEvidenceReceipt => ({
  status: "SUCCEEDED",
  command_id: "command-evidence-1",
  idempotency_key: "idempotency-evidence-1",
  result_code: "SUBMISSION_EVIDENCE_RECORDED",
  aggregate_refs: [
    {
      aggregate_type: "SubmissionPackage",
      aggregate_id: "submission-package-1",
      aggregate_revision: 2,
    },
  ],
  event_ids: ["event-evidence-1"],
  replayed: false,
  external_submission: "NOT_PERFORMED",
});

function renderSubmissionHook(
  api: SubmissionApi,
  setMessage: Dispatch<SetStateAction<HookMessage | null>>,
) {
  return renderHook(() => useSubmissionActions(api as ApiClient, setMessage));
}

describe("useSubmissionActions", () => {
  it("rejects preparation without a preparation package identifier", async () => {
    const api = {
      prepareSubmissionPackage: vi.fn(),
      authorizeSubmissionPackage: vi.fn(),
      getSubmissionPackageManifest: vi.fn(),
      getSubmissionEvidence: vi.fn(),
      downloadSubmissionPackage: vi.fn(),
      recordSubmissionEvidence: vi.fn(),
    } satisfies SubmissionApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderSubmissionHook(api, setMessage);

    await act(async () => {
      await result.current.prepareSubmissionPackage();
    });

    expect(api.prepareSubmissionPackage).not.toHaveBeenCalled();
    expect(setMessage).toHaveBeenCalledWith({
      tone: "error",
      text: "Renseignez l’identifiant de la préparation à déposer.",
    });
  });

  it("prepares the submission package and stores the returned aggregate identifier", async () => {
    const api = {
      prepareSubmissionPackage: vi.fn().mockResolvedValue(packageReceipt()),
      authorizeSubmissionPackage: vi.fn(),
      getSubmissionPackageManifest: vi.fn(),
      getSubmissionEvidence: vi.fn(),
      downloadSubmissionPackage: vi.fn(),
      recordSubmissionEvidence: vi.fn(),
    } satisfies SubmissionApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderSubmissionHook(api, setMessage);

    act(() => {
      result.current.setPreparationPackageId(" preparation-1 ");
      result.current.setPreparationRevision("3");
    });
    await act(async () => {
      await result.current.prepareSubmissionPackage();
    });

    expect(api.prepareSubmissionPackage).toHaveBeenCalledWith("preparation-1", 3, {
      submission_mode: "FULL",
      candidature_only_reason: undefined,
    });
    expect(result.current.submissionPackageId).toBe("submission-package-1");
    expect(setMessage).toHaveBeenCalledWith({
      tone: "success",
      text: "Paquet préparé pour contrôle patronal. Aucun dépôt externe n’a été effectué.",
    });
  });

  it("requires a reason for a candidature-only package", async () => {
    const api = {
      prepareSubmissionPackage: vi.fn(),
      authorizeSubmissionPackage: vi.fn(),
      getSubmissionPackageManifest: vi.fn(),
      getSubmissionEvidence: vi.fn(),
      downloadSubmissionPackage: vi.fn(),
      recordSubmissionEvidence: vi.fn(),
    } satisfies SubmissionApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderSubmissionHook(api, setMessage);

    act(() => {
      result.current.setPreparationPackageId("preparation-1");
      result.current.setSubmissionMode("CANDIDATURE_ONLY");
    });
    await act(async () => {
      await result.current.prepareSubmissionPackage();
    });

    expect(api.prepareSubmissionPackage).not.toHaveBeenCalled();
    expect(setMessage).toHaveBeenCalledWith({
      tone: "error",
      text: "Justifiez la candidature seule avant de préparer le paquet.",
    });
  });

  it("replays P5 authorization with the same identifiers after an unknown result", async () => {
    const authorize = vi
      .fn()
      .mockRejectedValueOnce(new Error("résultat réseau inconnu"))
      .mockResolvedValueOnce(authorizationReceipt(true));
    const api = {
      prepareSubmissionPackage: vi.fn(),
      authorizeSubmissionPackage: authorize,
      getSubmissionPackageManifest: vi.fn().mockResolvedValue(manifestProjection()),
      getSubmissionEvidence: vi.fn(),
      downloadSubmissionPackage: vi.fn(),
      recordSubmissionEvidence: vi.fn(),
    } satisfies SubmissionApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderSubmissionHook(api, setMessage);

    act(() => {
      result.current.setSubmissionPackageId("submission-package-1");
      result.current.setSubmissionAuthorizationRationale("Contrôle P5 validé.");
    });
    await act(async () => {
      await result.current.loadSubmissionPackageManifest();
    });
    await act(async () => {
      await result.current.authorizeSubmissionPackage();
    });
    await act(async () => {
      await result.current.authorizeSubmissionPackage();
    });

    expect(authorize).toHaveBeenCalledTimes(2);
    expect(authorize.mock.calls[0]).toEqual(authorize.mock.calls[1]);
    expect(authorize).toHaveBeenCalledWith(
      "submission-package-1",
      3,
      "Contrôle P5 validé.",
      expect.objectContaining({
        command_id: expect.any(String),
        idempotency_key: expect.any(String),
        authorization_id: expect.any(String),
      }),
      "c".repeat(64),
    );
    expect(result.current.submissionAuthorized).toBe(true);
    expect(setMessage).toHaveBeenLastCalledWith({
      tone: "success",
      text: "Autorisation P5 déjà enregistrée; état rechargé.",
    });
  });

  it("requires the exact C10 manifest to be loaded before P5", async () => {
    const authorize = vi.fn();
    const api = {
      prepareSubmissionPackage: vi.fn(),
      authorizeSubmissionPackage: authorize,
      getSubmissionPackageManifest: vi.fn(),
      getSubmissionEvidence: vi.fn(),
      downloadSubmissionPackage: vi.fn(),
      recordSubmissionEvidence: vi.fn(),
    } satisfies SubmissionApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderSubmissionHook(api, setMessage);

    act(() => {
      result.current.setSubmissionPackageId("submission-package-1");
      result.current.setSubmissionPackageVersion("3");
    });
    await act(async () => {
      await result.current.authorizeSubmissionPackage();
    });

    expect(authorize).not.toHaveBeenCalled();
    expect(setMessage).toHaveBeenLastCalledWith({
      tone: "error",
      text: "Relisez le manifeste exact du candidat C10 avant l’autorisation P5.",
    });
  });

  it("sends the reviewed C10 manifest hash with P5", async () => {
    const authorize = vi.fn().mockResolvedValue(authorizationReceipt());
    const api = {
      prepareSubmissionPackage: vi.fn(),
      authorizeSubmissionPackage: authorize,
      getSubmissionPackageManifest: vi.fn().mockResolvedValue(c10ManifestProjection()),
      getSubmissionEvidence: vi.fn(),
      downloadSubmissionPackage: vi.fn(),
      recordSubmissionEvidence: vi.fn(),
    } satisfies SubmissionApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderSubmissionHook(api, setMessage);

    act(() => result.current.setSubmissionPackageId("submission-package-1"));
    await act(async () => {
      await result.current.loadSubmissionPackageManifest();
    });
    await act(async () => {
      await result.current.authorizeSubmissionPackage();
    });

    expect(authorize).toHaveBeenCalledWith(
      "submission-package-1",
      3,
      "Paquet relu et autorisé pour la remise humaine.",
      expect.objectContaining({
        command_id: expect.any(String),
        idempotency_key: expect.any(String),
        authorization_id: expect.any(String),
      }),
      "c".repeat(64),
    );
  });

  it("sends only one P5 request while a double-click is in flight", async () => {
    const authorize = vi.fn().mockResolvedValue(authorizationReceipt());
    const api = {
      prepareSubmissionPackage: vi.fn(),
      authorizeSubmissionPackage: authorize,
      getSubmissionPackageManifest: vi.fn().mockResolvedValue(c10ManifestProjection()),
      getSubmissionEvidence: vi.fn(),
      downloadSubmissionPackage: vi.fn(),
      recordSubmissionEvidence: vi.fn(),
    } satisfies SubmissionApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderSubmissionHook(api, setMessage);

    act(() => result.current.setSubmissionPackageId("submission-package-1"));
    await act(async () => {
      await result.current.loadSubmissionPackageManifest();
    });
    await act(async () => {
      const first = result.current.authorizeSubmissionPackage();
      const second = result.current.authorizeSubmissionPackage();
      await Promise.all([first, second]);
    });

    expect(authorize).toHaveBeenCalledTimes(1);
  });

  it("does not let an old duplicate P5 response erase a newer UNKNOWN intent", async () => {
    let finishFirst: ((receipt: SubmissionPackageAuthorizationReceipt) => void) | undefined;
    let finishDuplicate: ((receipt: SubmissionPackageAuthorizationReceipt) => void) | undefined;
    let failSecond: ((error: Error) => void) | undefined;
    const authorize = vi.fn().mockImplementation((id: string) => {
      if (id === "submission-package-1") {
        return new Promise<SubmissionPackageAuthorizationReceipt>((resolve) => {
          if (!finishFirst) finishFirst = resolve;
          else finishDuplicate = resolve;
        });
      }
      return new Promise<SubmissionPackageAuthorizationReceipt>((_resolve, reject) => {
        failSecond = reject;
      });
    });
    const api = {
      prepareSubmissionPackage: vi.fn(),
      authorizeSubmissionPackage: authorize,
      getSubmissionPackageManifest: vi.fn()
        .mockResolvedValueOnce(c10ManifestProjection())
        .mockResolvedValueOnce({ ...c10ManifestProjection(), submission_package_id: "submission-package-2" }),
      getSubmissionEvidence: vi.fn(),
      downloadSubmissionPackage: vi.fn(),
      recordSubmissionEvidence: vi.fn(),
    } satisfies SubmissionApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderSubmissionHook(api, setMessage);
    act(() => result.current.setSubmissionPackageId("submission-package-1"));
    await act(async () => { await result.current.loadSubmissionPackageManifest(); });
    let first: Promise<void> | undefined;
    let duplicate: Promise<void> | undefined;
    act(() => {
      first = result.current.authorizeSubmissionPackage();
      duplicate = result.current.authorizeSubmissionPackage();
    });
    await act(async () => { finishFirst?.(authorizationReceipt()); await first; });
    act(() => result.current.setSubmissionPackageId("submission-package-2"));
    await act(async () => { await result.current.loadSubmissionPackageManifest(); });
    let second: Promise<void> | undefined;
    act(() => { second = result.current.authorizeSubmissionPackage(); });
    await act(async () => { finishDuplicate?.(authorizationReceipt()); await duplicate; });
    await act(async () => { failSecond?.(new Error("Résultat UNKNOWN")); await second; });
    act(() => result.current.setSubmissionAuthorizationRationale("Autre motif après UNKNOWN."));
    let changedRetry: Promise<void> | undefined;
    act(() => { changedRetry = result.current.authorizeSubmissionPackage(); });
    await act(async () => { failSecond?.(new Error("Résultat UNKNOWN")); await changedRetry; });
    expect(authorize.mock.calls.filter(([id]) => id === "submission-package-2")).toHaveLength(1);
  });

  it.each(["IN_FLIGHT", "UNKNOWN"])("keeps P5 %s when an earlier prepare response arrives", async (state) => {
    let finishPreparation: ((receipt: SubmissionPackageReceipt) => void) | undefined;
    let failAuthorization: ((error: Error) => void) | undefined;
    const authorize = vi.fn().mockImplementation(() => new Promise((_resolve, reject) => {
      failAuthorization = reject;
    }));
    const api = {
      prepareSubmissionPackage: vi.fn().mockImplementation(() => new Promise((resolve) => {
        finishPreparation = resolve;
      })),
      authorizeSubmissionPackage: authorize,
      getSubmissionPackageManifest: vi.fn().mockResolvedValue(c10ManifestProjection()),
      getSubmissionEvidence: vi.fn(),
      downloadSubmissionPackage: vi.fn(),
      recordSubmissionEvidence: vi.fn(),
    } satisfies SubmissionApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderSubmissionHook(api, setMessage);
    act(() => {
      result.current.setSubmissionPackageId("submission-package-1");
      result.current.setPreparationPackageId("preparation-2");
    });
    await act(async () => { await result.current.loadSubmissionPackageManifest(); });
    let preparation: Promise<void> | undefined;
    let authorization: Promise<void> | undefined;
    act(() => { preparation = result.current.prepareSubmissionPackage(); });
    act(() => { authorization = result.current.authorizeSubmissionPackage(); });
    if (state === "UNKNOWN") {
      await act(async () => { failAuthorization?.(new Error("Résultat UNKNOWN")); await authorization; });
    }
    await act(async () => {
      finishPreparation?.({ ...packageReceipt(), aggregate_refs: [{ aggregate_type: "SubmissionPackage", aggregate_id: "submission-package-2", aggregate_revision: 1 }] });
      await preparation;
    });
    if (state === "IN_FLIGHT") {
      await act(async () => { failAuthorization?.(new Error("Résultat UNKNOWN")); await authorization; });
    }
    expect(result.current.submissionPackageId).toBe("submission-package-1");
    act(() => result.current.setSubmissionAuthorizationRationale("Motif modifié."));
    let retry: Promise<void> | undefined;
    act(() => { retry = result.current.authorizeSubmissionPackage(); });
    await act(async () => { failAuthorization?.(new Error("Résultat UNKNOWN")); await retry; });
    expect(authorize).toHaveBeenCalledTimes(1);
  });

  it("ignores a stale manifest read while preserving an exact UNKNOWN retry", async () => {
    let finishManifest: ((projection: SubmissionPackageManifestProjection) => void) | undefined;
    const authorize = vi.fn()
      .mockRejectedValueOnce(new Error("Résultat UNKNOWN"))
      .mockResolvedValueOnce(authorizationReceipt(true));
    const api = {
      prepareSubmissionPackage: vi.fn(),
      authorizeSubmissionPackage: authorize,
      getSubmissionPackageManifest: vi.fn()
        .mockResolvedValueOnce(c10ManifestProjection())
        .mockImplementationOnce(() => new Promise((resolve) => { finishManifest = resolve; })),
      getSubmissionEvidence: vi.fn(),
      downloadSubmissionPackage: vi.fn(),
      recordSubmissionEvidence: vi.fn(),
    } satisfies SubmissionApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderSubmissionHook(api, setMessage);
    act(() => result.current.setSubmissionPackageId("submission-package-1"));
    await act(async () => { await result.current.loadSubmissionPackageManifest(); });
    act(() => result.current.setSubmissionPackageId("submission-package-2"));
    let read: Promise<void> | undefined;
    act(() => { read = result.current.loadSubmissionPackageManifest(); });
    act(() => result.current.setSubmissionPackageId("submission-package-1"));
    await act(async () => { await result.current.authorizeSubmissionPackage(); });
    await act(async () => {
      finishManifest?.({ ...c10ManifestProjection(), submission_package_id: "submission-package-2" });
      await read;
    });
    await act(async () => { await result.current.authorizeSubmissionPackage(); });
    expect(authorize).toHaveBeenCalledTimes(2);
    expect(authorize.mock.calls[0]).toEqual(authorize.mock.calls[1]);
  });

  it("does not overwrite a confirmed P5 with a manifest read started before the act", async () => {
    let finishManifest: ((projection: SubmissionPackageManifestProjection) => void) | undefined;
    const api = {
      prepareSubmissionPackage: vi.fn(),
      authorizeSubmissionPackage: vi.fn().mockResolvedValue(authorizationReceipt()),
      getSubmissionPackageManifest: vi.fn().mockResolvedValueOnce(c10ManifestProjection())
        .mockImplementationOnce(() => new Promise((resolve) => { finishManifest = resolve; })),
      getSubmissionEvidence: vi.fn(),
      downloadSubmissionPackage: vi.fn(),
      recordSubmissionEvidence: vi.fn(),
    } satisfies SubmissionApi;
    const { result } = renderSubmissionHook(api, vi.fn());
    act(() => result.current.setSubmissionPackageId("submission-package-1"));
    await act(async () => { await result.current.loadSubmissionPackageManifest(); });
    let read: Promise<void> | undefined;
    act(() => { read = result.current.loadSubmissionPackageManifest(); });
    await act(async () => { await result.current.authorizeSubmissionPackage(); });
    await act(async () => { finishManifest?.(c10ManifestProjection()); await read; });
    expect(result.current.submissionAuthorized).toBe(true);
  });

  it("does not download an export response after its scoped component unmounts", async () => {
    let finishExport: ((archive: Blob) => void) | undefined;
    const api = {
      prepareSubmissionPackage: vi.fn(),
      authorizeSubmissionPackage: vi.fn(),
      getSubmissionPackageManifest: vi.fn(),
      getSubmissionEvidence: vi.fn(),
      downloadSubmissionPackage: vi.fn().mockImplementation(() => new Promise((resolve) => { finishExport = resolve; })),
      recordSubmissionEvidence: vi.fn(),
    } satisfies SubmissionApi;
    const createObjectURL = vi.fn().mockReturnValue("blob:old-session");
    const setMessage = vi.fn();
    vi.stubGlobal("URL", { ...URL, createObjectURL, revokeObjectURL: vi.fn() });
    const { result, unmount } = renderSubmissionHook(api, setMessage);
    act(() => result.current.setSubmissionPackageId("submission-package-1"));
    let request: Promise<void> | undefined;
    act(() => { request = result.current.exportSubmissionPackage(); });
    unmount();
    await act(async () => { finishExport?.(new Blob(["private-old-session"])); await request; });
    expect(createObjectURL).not.toHaveBeenCalled();
    expect(setMessage).not.toHaveBeenCalled();
    vi.unstubAllGlobals();
  });

  it("does not turn an unknown P5 result into a different intent", async () => {
    const authorize = vi
      .fn()
      .mockRejectedValueOnce(new Error("réponse réseau inconnue"))
      .mockResolvedValueOnce(authorizationReceipt(true));
    const api = {
      prepareSubmissionPackage: vi.fn(),
      authorizeSubmissionPackage: authorize,
      getSubmissionPackageManifest: vi.fn().mockResolvedValue(c10ManifestProjection()),
      getSubmissionEvidence: vi.fn(),
      downloadSubmissionPackage: vi.fn(),
      recordSubmissionEvidence: vi.fn(),
    } satisfies SubmissionApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderSubmissionHook(api, setMessage);

    act(() => result.current.setSubmissionPackageId("submission-package-1"));
    await act(async () => {
      await result.current.loadSubmissionPackageManifest();
    });
    await act(async () => {
      await result.current.authorizeSubmissionPackage();
    });
    act(() => result.current.setSubmissionAuthorizationRationale("Motif différent."));
    await act(async () => {
      await result.current.authorizeSubmissionPackage();
    });

    expect(authorize).toHaveBeenCalledTimes(1);
    expect(setMessage).toHaveBeenLastCalledWith({
      tone: "warning",
      text: "Une autorisation P5 reste à confirmer pour le candidat relu. Restaurez cette intention exacte pour la rejouer.",
    });

    act(() => result.current.setSubmissionAuthorizationRationale("Paquet relu et autorisé pour la remise humaine."));
    await act(async () => {
      await result.current.authorizeSubmissionPackage();
    });
    expect(authorize).toHaveBeenCalledTimes(2);
    expect(authorize.mock.calls[0]).toEqual(authorize.mock.calls[1]);
  });

  it("reconciles a P5 conflict with the exact manifest GET", async () => {
    const conflict = Object.assign(new Error("conflit de version"), { status: 409 });
    const getManifest = vi
      .fn()
      .mockResolvedValueOnce(c10ManifestProjection())
      .mockResolvedValueOnce(manifestProjection("AUTHORIZED"));
    const api = {
      prepareSubmissionPackage: vi.fn(),
      authorizeSubmissionPackage: vi.fn().mockRejectedValue(conflict),
      getSubmissionPackageManifest: getManifest,
      getSubmissionEvidence: vi.fn(),
      downloadSubmissionPackage: vi.fn(),
      recordSubmissionEvidence: vi.fn(),
    } satisfies SubmissionApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderSubmissionHook(api, setMessage);

    act(() => result.current.setSubmissionPackageId("submission-package-1"));
    await act(async () => {
      await result.current.loadSubmissionPackageManifest();
    });
    await act(async () => {
      await result.current.authorizeSubmissionPackage();
    });

    expect(getManifest).toHaveBeenCalledTimes(2);
    expect(result.current.submissionAuthorized).toBe(true);
    expect(result.current.submissionManifest?.authorization_status).toBe("AUTHORIZED");
  });

  it("does not project a conflict GET onto a different currently selected package", async () => {
    const conflict = Object.assign(new Error("conflit de version"), { status: 409 });
    let resolveConflictManifest: ((projection: SubmissionPackageManifestProjection) => void) | undefined;
    let notifyConflictGetStarted: (() => void) | undefined;
    const conflictGetStarted = new Promise<void>((resolve) => {
      notifyConflictGetStarted = resolve;
    });
    const getManifest = vi.fn().mockImplementationOnce(() => Promise.resolve(c10ManifestProjection()));
    getManifest.mockImplementationOnce(
      () => {
        notifyConflictGetStarted?.();
        return new Promise<SubmissionPackageManifestProjection>((resolve) => {
          resolveConflictManifest = resolve;
        });
      },
    );
    const api = {
      prepareSubmissionPackage: vi.fn(),
      authorizeSubmissionPackage: vi.fn().mockRejectedValue(conflict),
      getSubmissionPackageManifest: getManifest,
      getSubmissionEvidence: vi.fn(),
      downloadSubmissionPackage: vi.fn(),
      recordSubmissionEvidence: vi.fn(),
    } satisfies SubmissionApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderSubmissionHook(api, setMessage);

    act(() => result.current.setSubmissionPackageId("submission-package-1"));
    await act(async () => {
      await result.current.loadSubmissionPackageManifest();
    });
    let request: Promise<void> | undefined;
    act(() => {
      request = result.current.authorizeSubmissionPackage();
    });
    await conflictGetStarted;
    act(() => result.current.setSubmissionPackageId("submission-package-2"));
    resolveConflictManifest?.(manifestProjection("AUTHORIZED"));
    await act(async () => {
      await request;
    });

    expect(result.current.submissionAuthorized).toBe(false);
    expect(result.current.submissionManifest?.submission_package_id).toBe("submission-package-1");
  });

  it("releases a P5 intent only after a definitive client refusal", async () => {
    const refusal = Object.assign(new Error("source C10 périmée"), { status: 422 });
    const authorize = vi
      .fn()
      .mockRejectedValueOnce(refusal)
      .mockResolvedValueOnce(authorizationReceipt());
    const api = {
      prepareSubmissionPackage: vi.fn(),
      authorizeSubmissionPackage: authorize,
      getSubmissionPackageManifest: vi.fn().mockResolvedValue(c10ManifestProjection()),
      getSubmissionEvidence: vi.fn(),
      downloadSubmissionPackage: vi.fn(),
      recordSubmissionEvidence: vi.fn(),
    } satisfies SubmissionApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderSubmissionHook(api, setMessage);

    act(() => result.current.setSubmissionPackageId("submission-package-1"));
    await act(async () => {
      await result.current.loadSubmissionPackageManifest();
    });
    await act(async () => {
      await result.current.authorizeSubmissionPackage();
    });
    act(() => result.current.setSubmissionAuthorizationRationale("Nouveau contrôle après refus."));
    await act(async () => {
      await result.current.authorizeSubmissionPackage();
    });

    expect(authorize).toHaveBeenCalledTimes(2);
    expect(authorize.mock.calls[1]?.[2]).toBe("Nouveau contrôle après refus.");
    expect(authorize.mock.calls[0]?.[3]).not.toEqual(authorize.mock.calls[1]?.[3]);
  });

  it("does not project a P5 receipt onto a different currently selected package", async () => {
    let resolveAuthorization: ((receipt: SubmissionPackageAuthorizationReceipt) => void) | undefined;
    const authorize = vi.fn().mockImplementation(
      () => new Promise<SubmissionPackageAuthorizationReceipt>((resolve) => {
        resolveAuthorization = resolve;
      }),
    );
    const api = {
      prepareSubmissionPackage: vi.fn(),
      authorizeSubmissionPackage: authorize,
      getSubmissionPackageManifest: vi.fn().mockResolvedValue(c10ManifestProjection()),
      getSubmissionEvidence: vi.fn(),
      downloadSubmissionPackage: vi.fn(),
      recordSubmissionEvidence: vi.fn(),
    } satisfies SubmissionApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderSubmissionHook(api, setMessage);

    act(() => result.current.setSubmissionPackageId("submission-package-1"));
    await act(async () => {
      await result.current.loadSubmissionPackageManifest();
    });
    let request: Promise<void> | undefined;
    act(() => {
      request = result.current.authorizeSubmissionPackage();
    });
    act(() => result.current.setSubmissionPackageId("submission-package-2"));
    resolveAuthorization?.(authorizationReceipt());
    await act(async () => {
      await request;
    });

    expect(result.current.submissionAuthorized).toBe(false);
  });

  it("loads the exact bounded manifest and reflects the P5 status", async () => {
    const api = {
      prepareSubmissionPackage: vi.fn(),
      authorizeSubmissionPackage: vi.fn(),
      getSubmissionPackageManifest: vi.fn().mockResolvedValue(manifestProjection("AUTHORIZED")),
      getSubmissionEvidence: vi.fn(),
      downloadSubmissionPackage: vi.fn(),
      recordSubmissionEvidence: vi.fn(),
    } satisfies SubmissionApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderSubmissionHook(api, setMessage);

    act(() => {
      result.current.setSubmissionPackageId(" submission-package-1 ");
    });
    await act(async () => {
      await result.current.loadSubmissionPackageManifest();
    });

    expect(api.getSubmissionPackageManifest).toHaveBeenCalledWith("submission-package-1");
    expect(result.current.submissionManifest?.manifest_sha256).toBe("c".repeat(64));
    expect(result.current.submissionPackageVersion).toBe("3");
    expect(result.current.submissionAuthorized).toBe(true);
    expect(setMessage).toHaveBeenLastCalledWith({
      tone: "success",
      text: "Manifeste exact rechargé. Les exclusions et l’état P5 sont visibles.",
    });
  });

  it("loads partial receipt evidence bound to the package manifest", async () => {
    const api = {
      prepareSubmissionPackage: vi.fn(),
      authorizeSubmissionPackage: vi.fn(),
      getSubmissionPackageManifest: vi.fn(),
      getSubmissionEvidence: vi.fn().mockResolvedValue(evidenceProjection()),
      downloadSubmissionPackage: vi.fn(),
      recordSubmissionEvidence: vi.fn(),
    } satisfies SubmissionApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderSubmissionHook(api, setMessage);

    act(() => {
      result.current.setSubmissionPackageId(" submission-package-1 ");
    });
    await act(async () => {
      await result.current.loadSubmissionEvidence();
    });

    expect(api.getSubmissionEvidence).toHaveBeenCalledWith("submission-package-1");
    expect(result.current.submissionEvidence[0]?.reconciliation_status).toBe("PARTIAL");
    expect(result.current.submissionEvidence[0]?.manifest_sha256).toBe("c".repeat(64));
    expect(setMessage).toHaveBeenLastCalledWith({
      tone: "success",
      text: "Preuves de réception rechargées. Le rapprochement reste explicitement partiel.",
    });
  });

  it("downloads a Blob as an audited ZIP export and marks the package exported", async () => {
    const archive = new Blob(["zip-content"], { type: "application/zip" });
    const objectUrl = "blob:submission-package-1";
    const createObjectURL = vi.fn().mockReturnValue(objectUrl);
    const revokeObjectURL = vi.fn();
    const click = vi.fn();
    const originalCreateElement = document.createElement.bind(document);
    const api = {
      prepareSubmissionPackage: vi.fn(),
      authorizeSubmissionPackage: vi.fn(),
      getSubmissionPackageManifest: vi.fn(),
      getSubmissionEvidence: vi.fn(),
      downloadSubmissionPackage: vi.fn().mockResolvedValue(archive),
      recordSubmissionEvidence: vi.fn(),
    } satisfies SubmissionApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;

    vi.stubGlobal("URL", { ...URL, createObjectURL, revokeObjectURL });
    vi.spyOn(document, "createElement").mockImplementation((tagName, options) => {
      if (tagName === "a") {
        return { href: "", download: "", click } as unknown as HTMLAnchorElement;
      }
      return originalCreateElement(tagName, options);
    });

    const { result } = renderSubmissionHook(api, setMessage);
    act(() => {
      result.current.setSubmissionPackageId(" submission-package-1 ");
    });
    await act(async () => {
      await result.current.exportSubmissionPackage();
    });

    expect(api.downloadSubmissionPackage).toHaveBeenCalledWith("submission-package-1");
    expect(createObjectURL).toHaveBeenCalledWith(archive);
    expect(click).toHaveBeenCalledOnce();
    expect(revokeObjectURL).toHaveBeenCalledWith(objectUrl);
    expect(result.current.submissionExported).toBe(true);
    expect(setMessage).toHaveBeenCalledWith({
      tone: "success",
      text: "Dossier exporté. L’audit et la notification de téléchargement ont été enregistrés.",
    });

    vi.restoreAllMocks();
  });

  it("keeps a network export result unknown until verification", async () => {
    const api = {
      prepareSubmissionPackage: vi.fn(),
      authorizeSubmissionPackage: vi.fn(),
      getSubmissionPackageManifest: vi.fn(),
      getSubmissionEvidence: vi.fn(),
      downloadSubmissionPackage: vi.fn().mockRejectedValue(new Error("network closed")),
      recordSubmissionEvidence: vi.fn(),
    } satisfies SubmissionApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderSubmissionHook(api, setMessage);
    act(() => result.current.setSubmissionPackageId("submission-package-1"));

    await act(async () => {
      await result.current.exportSubmissionPackage();
    });

    expect(result.current.submissionExportState).toBe("UNKNOWN");
    expect(result.current.submissionExported).toBe(false);
    expect(setMessage).toHaveBeenCalledWith({
      tone: "warning",
      text: "Résultat de l’export non confirmé. Vérifiez l’état avant toute nouvelle tentative.",
    });
  });

  it("requests a signature with the explicit package version", async () => {
    const api = {
      prepareSubmissionPackage: vi.fn(),
      authorizeSubmissionPackage: vi.fn(),
      getSubmissionPackageManifest: vi.fn(),
      getSubmissionEvidence: vi.fn(),
      downloadSubmissionPackage: vi.fn(),
      recordSubmissionEvidence: vi.fn(),
      requestSubmissionSignature: vi.fn().mockResolvedValue(signatureReceipt()),
      getSubmissionSignature: vi.fn(),
    } satisfies SignatureApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderSubmissionHook(api, setMessage);

    act(() => {
      result.current.setSubmissionPackageId(" submission-package-1 ");
      result.current.setSignaturePackageVersion("2");
    });
    await act(async () => {
      await result.current.requestSignature();
    });

    expect(api.requestSubmissionSignature).toHaveBeenCalledWith("submission-package-1", 2);
    expect(result.current.signatureId).toBe("signature-1");
    expect(result.current.signatureStatus).toBe("REQUESTED");
    expect(result.current.signatureRevision).toBe(1);
    expect(setMessage).toHaveBeenCalledWith({
      tone: "success",
      text: "Demande de signature enregistrée. Aucun dépôt externe n’a été effectué.",
    });
  });

  it("loads only the bounded signature projection", async () => {
    const api = {
      prepareSubmissionPackage: vi.fn(),
      authorizeSubmissionPackage: vi.fn(),
      getSubmissionPackageManifest: vi.fn(),
      getSubmissionEvidence: vi.fn(),
      downloadSubmissionPackage: vi.fn(),
      recordSubmissionEvidence: vi.fn(),
      requestSubmissionSignature: vi.fn(),
      getSubmissionSignature: vi.fn().mockResolvedValue(signatureProjection()),
    } satisfies SignatureApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderSubmissionHook(api, setMessage);

    act(() => {
      result.current.setSignatureId("signature-1");
    });
    await act(async () => {
      await result.current.loadSignature();
    });

    expect(api.getSubmissionSignature).toHaveBeenCalledWith("signature-1");
    expect(result.current.signatureStatus).toBe("SIGNED");
    expect(result.current.signatureProvider).toBe("TEST_PROVIDER");
    expect(result.current.signatureRevision).toBe(2);
    expect(result.current.signaturePackageVersion).toBe("2");
  });

  it("records redacted manual evidence without changing the external submission invariant", async () => {
    const api = {
      prepareSubmissionPackage: vi.fn(),
      authorizeSubmissionPackage: vi.fn(),
      getSubmissionPackageManifest: vi.fn(),
      getSubmissionEvidence: vi.fn(),
      downloadSubmissionPackage: vi.fn(),
      recordSubmissionEvidence: vi.fn().mockResolvedValue(evidenceReceipt()),
    } satisfies SubmissionApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderSubmissionHook(api, setMessage);

    act(() => {
      result.current.setSubmissionPackageId("submission-package-1");
      result.current.setEvidenceForm({
        evidence_type: "MANUAL_PORTAL_REFERENCE",
        external_reference_hash: "a".repeat(64),
        evidence_sha256: "b".repeat(64),
        notes_redacted: "  preuve expurgée  ",
      });
    });
    await act(async () => {
      await result.current.recordSubmissionEvidence();
    });

    expect(api.recordSubmissionEvidence).toHaveBeenCalledWith("submission-package-1", {
      evidence_type: "MANUAL_PORTAL_REFERENCE",
      external_reference_hash: "a".repeat(64),
      evidence_sha256: "b".repeat(64),
      notes_redacted: "  preuve expurgée  ",
    });
    expect(setMessage).toHaveBeenCalledWith({
      tone: "success",
      text: "Preuve append-only enregistrée. Le dépôt externe reste à effectuer manuellement.",
    });
  });
});


afterEach(() => {
  vi.restoreAllMocks();
});
