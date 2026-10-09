import type { Dispatch, SetStateAction } from "react";
import { act, renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ApiClient } from "../../infrastructure/api";
import type { CollaboratorTask, PreparationPackage } from "../../shared/types";
import { useCollaboratorWizard } from "./useCollaboratorWizard";

type HookMessage = { tone: "success" | "error" | "warning"; text: string };
type WizardApi = Pick<
  ApiClient,
  | "getCollaboratorPreparation"
  | "listCollaboratorTasks"
  | "evaluatePreparationReadiness"
  | "generateTechnicalDocument"
  | "createTechnicalResponseDraft"
  | "claimCollaboratorTask"
  | "recordCollaboratorTaskResult"
  | "completeCollaboratorTask"
  | "transmitPreparationSnapshot"
> & Partial<Pick<ApiClient,
  | "getCaseDceReading"
  | "getCapabilityAssessments"
  | "getCapabilityCandidates"
  | "getPreparationResponsePlans"
  | "createPreparationResponsePlan"
  | "createPreparationSnapshot"
>>;

const preparation = (): PreparationPackage => ({
  package_id: "package-1",
  case_id: "case-1",
  assignment_id: "assignment-1",
  dce_version_id: "dce-1",
  state: "IN_PREPARATION",
  aggregate_revision: 7,
  latest_readiness: {
    readiness_id: "readiness-1",
    revision: 3,
    state: "READY_WITH_WARNINGS",
    blocker_codes: [],
    warning_codes: ["OPTIONAL_REFERENCE_MISSING"],
    checked_requirement_count: 4,
    checked_task_count: 2,
  },
  generated_documents: [],
  response_drafts: [],
});

const task = (id = "task-1"): CollaboratorTask => ({
  task_id: id,
  case_id: "case-1",
  assignment_id: "assignment-1",
  requirement_id: "requirement-1",
  task_kind: "REQUIREMENT_RESPONSE",
  title: "Répondre à la clause technique",
  objective: "Produire une preuve structurée",
  priority: "HIGH",
  state: "OPEN",
  due_at: null,
  aggregate_revision: 4,
});

function renderWizardHook(
  api: WizardApi,
  setMessage: Dispatch<SetStateAction<HookMessage | null>>,
) {
  const planDefaults: Partial<ApiClient> = {
    getCaseDceReading: vi.fn().mockResolvedValue({
      case_id: "case-1", work_label: "Affaire synthétique", case_lifecycle: "ACTIVE", commercial_stage: "PREPARATION", dce_freshness: "CURRENT", availability: "AVAILABLE",
      dce: { dce_version_id: "dce-1", lifecycle: "ADMITTED", integrity: "VERIFIED", classification_readiness: "CLASSIFIED", analysis_readiness: "READY", source_received_at: "2026-10-09T10:00:00Z" },
      counters: { total: 1, pending_human_confirmation: 0, confirmed: 1, review_required: 0, not_applicable: 0 },
      requirements: [{ requirement_id: "requirement-1", confirmation_revision: 1, requirement_type: "Méthodologie", directive_signal: "REQUIRED", confirmation_outcome: "CONFIRMED", uncertainty_status: "KNOWN", document_family: "CCTP", source_locator_label: "Article synthétique", source_anchor: null }],
    }),
    getCapabilityAssessments: vi.fn().mockResolvedValue({ proposals: [{ proposal_id: "proposal-1", case_id: "case-1", assignment_id: "assignment-1", capability_id: "capability-1", capability_version_id: "version-1", requirement_id: "requirement-1", task_id: null, state: "PROPOSED", validity_state: "CURRENT", justification: "Synthétique", source_locator: null, source_evidence_state: "CURRENT", source_evidence_evaluated_at: "2026-10-09T10:00:00Z" }], gaps: [] }),
    getCapabilityCandidates: vi.fn().mockResolvedValue([{ capability_id: "capability-1", capability_kind: "METHOD", name: "Méthodologie travaux", version_id: "version-1", version_number: 1, title: "Organisation de chantier", valid_from: "2026-10-01T00:00:00Z", valid_until: null, validity_state: "CURRENT", source_evidence_state: "CURRENT", evaluated_at: "2026-10-09T10:00:00Z" }]),
    getPreparationResponsePlans: vi.fn().mockResolvedValue({ package_id: "package-1", plans: [] }),
    createPreparationResponsePlan: vi.fn().mockResolvedValue({ status: "SUCCEEDED", command_id: "command-1", idempotency_key: "retry-1", result_code: "PREPARATION_RESPONSE_PLAN_CREATED", aggregate_refs: [], event_ids: [], replayed: false }),
  };
  return renderHook(() => useCollaboratorWizard({ ...planDefaults, ...api } as ApiClient, setMessage));
}

const responsePlan = (state: "UNKNOWN" | "SOURCES_CURRENT" = "SOURCES_CURRENT") => ({
  plan_id: "plan-1", version: 1, package_id: "package-1", dce_version_id: "dce-1", state, plan_sha256: "a".repeat(64),
  content: { schema_version: 1 as const, case_id: "case-1", package_id: "package-1", dce_version_id: "dce-1", items: [{ requirement_id: "requirement-1", requirement_state: "CONFIRMED" as const, section_code: "METHOD" as const, source_proposal_id: state === "SOURCES_CURRENT" ? "proposal-1" : null, source_capability_version_id: state === "SOURCES_CURRENT" ? "version-1" : null, source_validity_state: state === "SOURCES_CURRENT" ? "CURRENT" as const : "UNKNOWN" as const, source_evidence_state: state === "SOURCES_CURRENT" ? "CURRENT" as const : "UNKNOWN" as const }] },
});

describe("useCollaboratorWizard", () => {
  it("requires both the case and preparation package identifiers", async () => {
    const api = {
      getCollaboratorPreparation: vi.fn(),
      listCollaboratorTasks: vi.fn(),
      evaluatePreparationReadiness: vi.fn(),
      generateTechnicalDocument: vi.fn(),
      createTechnicalResponseDraft: vi.fn(),
      claimCollaboratorTask: vi.fn(),
      recordCollaboratorTaskResult: vi.fn(),
      completeCollaboratorTask: vi.fn(),
      transmitPreparationSnapshot: vi.fn(),
    } satisfies WizardApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderWizardHook(api, setMessage);

    await act(async () => {
      await result.current.loadCollaboratorWizard();
    });

    expect(api.getCollaboratorPreparation).not.toHaveBeenCalled();
    expect(api.listCollaboratorTasks).not.toHaveBeenCalled();
    expect(setMessage).toHaveBeenCalledWith({
      tone: "error",
      text: "Renseignez l’affaire et le package de préparation collaborateur.",
    });
  });

  it("loads the preparation projection and selects the first task", async () => {
    const api = {
      getCollaboratorPreparation: vi.fn().mockResolvedValue(preparation()),
      listCollaboratorTasks: vi.fn().mockResolvedValue({ case_id: "case-1", tasks: [task()] }),
      evaluatePreparationReadiness: vi.fn(),
      generateTechnicalDocument: vi.fn(),
      createTechnicalResponseDraft: vi.fn(),
      claimCollaboratorTask: vi.fn(),
      recordCollaboratorTaskResult: vi.fn(),
      completeCollaboratorTask: vi.fn(),
      transmitPreparationSnapshot: vi.fn(),
    } satisfies WizardApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderWizardHook(api, setMessage);

    act(() => {
      result.current.setWizardCaseId(" case-1 ");
      result.current.setWizardPackageId(" package-1 ");
    });
    await act(async () => {
      await result.current.loadCollaboratorWizard();
    });

    expect(api.getCollaboratorPreparation).toHaveBeenCalledWith("package-1");
    expect(api.listCollaboratorTasks).toHaveBeenCalledWith("case-1");
    expect(result.current.wizardPackage?.package_id).toBe("package-1");
    expect(result.current.wizardTaskId).toBe("task-1");
    expect(setMessage).toHaveBeenLastCalledWith({
      tone: "success",
      text: "Wizard collaborateur chargé depuis les projections serveur.",
    });
  });

  it("recalculates readiness with the package revision and refreshes the projection", async () => {
    const api = {
      getCollaboratorPreparation: vi.fn().mockResolvedValue(preparation()),
      listCollaboratorTasks: vi.fn().mockResolvedValue({ case_id: "case-1", tasks: [task()] }),
      evaluatePreparationReadiness: vi.fn().mockResolvedValue({}),
      generateTechnicalDocument: vi.fn(),
      createTechnicalResponseDraft: vi.fn(),
      claimCollaboratorTask: vi.fn(),
      recordCollaboratorTaskResult: vi.fn(),
      completeCollaboratorTask: vi.fn(),
      transmitPreparationSnapshot: vi.fn(),
    } satisfies WizardApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderWizardHook(api, setMessage);

    act(() => {
      result.current.setWizardCaseId("case-1");
      result.current.setWizardPackageId("package-1");
    });
    await act(async () => {
      await result.current.loadCollaboratorWizard();
    });
    await act(async () => {
      await result.current.evaluateWizardReadiness();
    });

    expect(api.evaluatePreparationReadiness).toHaveBeenCalledWith("case-1", {
      package_id: "package-1",
      assignment_id: "assignment-1",
      dce_version_id: "dce-1",
      expected_revision: 7,
    });
    expect(api.getCollaboratorPreparation).toHaveBeenCalledTimes(2);
    expect(setMessage).toHaveBeenLastCalledWith({
      tone: "success",
      text: "Complétude recalculée. Les blocages restent opposables au serveur.",
    });
  });

  it("records a trimmed structured result using the optimistic task revision", async () => {
    const api = {
      getCollaboratorPreparation: vi.fn().mockResolvedValue(preparation()),
      listCollaboratorTasks: vi.fn().mockResolvedValue({ case_id: "case-1", tasks: [task()] }),
      evaluatePreparationReadiness: vi.fn(),
      generateTechnicalDocument: vi.fn(),
      createTechnicalResponseDraft: vi.fn(),
      claimCollaboratorTask: vi.fn(),
      recordCollaboratorTaskResult: vi.fn().mockResolvedValue({}),
      completeCollaboratorTask: vi.fn(),
      transmitPreparationSnapshot: vi.fn(),
    } satisfies WizardApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderWizardHook(api, setMessage);

    act(() => {
      result.current.setWizardCaseId("case-1");
      result.current.setWizardPackageId("package-1");
      result.current.setWizardTaskId("task-1");
      result.current.setWizardResultText("  preuve technique expurgée  ");
      result.current.setWizardOutcome("RECORDED");
    });
    await act(async () => {
      await result.current.loadCollaboratorWizard();
    });
    await act(async () => {
      await result.current.recordWizardTaskResult();
    });

    expect(api.recordCollaboratorTaskResult).toHaveBeenCalledWith("task-1", {
      expected_revision: 4,
      result_text: "preuve technique expurgée",
      outcome: "RECORDED",
    });
    expect(result.current.wizardResultText).toBe("");
  });

  it("does not create a draft from an UNKNOWN response-plan readback", async () => {
    const api = {
      getCollaboratorPreparation: vi.fn().mockResolvedValue(preparation()),
      listCollaboratorTasks: vi.fn().mockResolvedValue({ case_id: "case-1", tasks: [] }),
      evaluatePreparationReadiness: vi.fn(),
      generateTechnicalDocument: vi.fn(),
      createTechnicalResponseDraft: vi.fn(),
      claimCollaboratorTask: vi.fn(),
      recordCollaboratorTaskResult: vi.fn(),
      completeCollaboratorTask: vi.fn(),
      transmitPreparationSnapshot: vi.fn(),
      getPreparationResponsePlans: vi.fn().mockResolvedValue({ package_id: "package-1", plans: [responsePlan("UNKNOWN")] }),
    } satisfies WizardApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderWizardHook(api, setMessage);

    act(() => {
      result.current.setWizardCaseId("case-1");
      result.current.setWizardPackageId("package-1");
    });
    await act(async () => {
      await result.current.loadCollaboratorWizard();
    });
    await act(async () => {
      await result.current.createWizardResponseDraft();
    });

    expect(result.current.wizardResponsePlan.exactPlan?.state).toBe("UNKNOWN");
    expect(result.current.canCreateWizardResponseDraft).toBe(false);
    expect(api.createTechnicalResponseDraft).not.toHaveBeenCalled();
  });

  it("retries one response-plan intent with the same IDs and then reads the exact plan", async () => {
    const current = responsePlan("SOURCES_CURRENT");
    const api = {
      getCollaboratorPreparation: vi.fn().mockResolvedValue({ ...preparation(), generated_documents: [{ document_id: "document-1", version: 1, document_kind: "TECHNICAL_RESPONSE", state: "GENERATED", readiness_revision: 3 }] }),
      listCollaboratorTasks: vi.fn().mockResolvedValue({ case_id: "case-1", tasks: [] }),
      evaluatePreparationReadiness: vi.fn(),
      generateTechnicalDocument: vi.fn(),
      createTechnicalResponseDraft: vi.fn(),
      claimCollaboratorTask: vi.fn(),
      recordCollaboratorTaskResult: vi.fn(),
      completeCollaboratorTask: vi.fn(),
      transmitPreparationSnapshot: vi.fn(),
      getPreparationResponsePlans: vi.fn().mockResolvedValueOnce({ package_id: "package-1", plans: [] }).mockResolvedValue({ package_id: "package-1", plans: [current] }),
      createPreparationResponsePlan: vi.fn().mockRejectedValueOnce(new TypeError("Synthetic network failure")).mockResolvedValue({ status: "SUCCEEDED", command_id: "command-1", idempotency_key: "retry-1", result_code: "PREPARATION_RESPONSE_PLAN_CREATED", aggregate_refs: [], event_ids: [], replayed: false }),
    } satisfies WizardApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderWizardHook(api, setMessage);
    act(() => { result.current.setWizardCaseId("case-1"); result.current.setWizardPackageId("package-1"); });
    await act(async () => { await result.current.loadCollaboratorWizard(); });
    expect(result.current.canSaveWizardResponsePlan).toBe(false);
    act(() => result.current.setWizardResponsePlanItem("requirement-1", { section_code: "METHOD", source_proposal_id: "proposal-1" }));
    expect(result.current.canSaveWizardResponsePlan).toBe(true);

    await act(async () => { await result.current.createWizardResponsePlan(); });
    expect(result.current.wizardResponsePlan.requestState).toBe("UNKNOWN");
    await act(async () => { await result.current.retryWizardResponsePlan(); });

    expect(api.createPreparationResponsePlan).toHaveBeenCalledTimes(2);
    expect(api.createPreparationResponsePlan.mock.calls[0]).toEqual(api.createPreparationResponsePlan.mock.calls[1]);
    expect(result.current.wizardResponsePlan.exactPlan?.state).toBe("SOURCES_CURRENT");
    expect(result.current.wizardResponsePlan.requestState).toBe("IDLE");
    expect(result.current.isWizardResponsePlanCurrent).toBe(true);
    expect(result.current.canCreateWizardResponseDraft).toBe(true);
    expect(api.createTechnicalResponseDraft).not.toHaveBeenCalled();
    expect(api.getPreparationResponsePlans).toHaveBeenCalledTimes(2);
  });

  it("keeps the logical plan identity when the DCE version changes", async () => {
    const oldPlan = { ...responsePlan("UNKNOWN"), dce_version_id: "dce-old", content: { ...responsePlan("UNKNOWN").content, dce_version_id: "dce-old" } };
    const currentPlan = { ...responsePlan("UNKNOWN"), version: 2 };
    const api = {
      getCollaboratorPreparation: vi.fn().mockResolvedValue(preparation()),
      listCollaboratorTasks: vi.fn().mockResolvedValue({ case_id: "case-1", tasks: [] }),
      evaluatePreparationReadiness: vi.fn(),
      generateTechnicalDocument: vi.fn(),
      createTechnicalResponseDraft: vi.fn(),
      claimCollaboratorTask: vi.fn(),
      recordCollaboratorTaskResult: vi.fn(),
      completeCollaboratorTask: vi.fn(),
      transmitPreparationSnapshot: vi.fn(),
      getPreparationResponsePlans: vi.fn().mockResolvedValueOnce({ package_id: "package-1", plans: [oldPlan] }).mockResolvedValue({ package_id: "package-1", plans: [currentPlan] }),
      createPreparationResponsePlan: vi.fn().mockResolvedValue({ status: "SUCCEEDED", command_id: "command-1", idempotency_key: "retry-1", result_code: "PREPARATION_RESPONSE_PLAN_CREATED", aggregate_refs: [], event_ids: [], replayed: false }),
    } satisfies WizardApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderWizardHook(api, setMessage);
    act(() => { result.current.setWizardCaseId("case-1"); result.current.setWizardPackageId("package-1"); });
    await act(async () => { await result.current.loadCollaboratorWizard(); });

    expect(result.current.wizardResponsePlan.hasPriorDcePlan).toBe(true);
    expect(result.current.wizardResponsePlan.exactPlan).toBeNull();
    act(() => result.current.setWizardResponsePlanItem("requirement-1", { section_code: "METHOD", source_proposal_id: "proposal-1" }));
    await act(async () => { await result.current.createWizardResponsePlan(); });

    expect(api.createPreparationResponsePlan.mock.calls[0]?.[1].plan_id).toBe("plan-1");
    expect(result.current.wizardResponsePlan.exactPlan?.dce_version_id).toBe("dce-1");
  });

  it("creates a draft only from the exact current plan and retries the same draft identity", async () => {
    const current = responsePlan("SOURCES_CURRENT");
    const packageWithDocument: PreparationPackage = {
      ...preparation(),
      aggregate_revision: 8,
      generated_documents: [{ document_id: "document-1", version: 1, document_kind: "TECHNICAL_RESPONSE", state: "GENERATED", readiness_revision: 3 }],
    };
    const receipt = { status: "SUCCEEDED" as const, command_id: "draft-command", idempotency_key: "draft-retry", result_code: "TECHNICAL_RESPONSE_DRAFT_CREATED", aggregate_refs: [], event_ids: [], replayed: false };
    const api = {
      getCollaboratorPreparation: vi.fn().mockResolvedValue(packageWithDocument),
      listCollaboratorTasks: vi.fn().mockResolvedValue({ case_id: "case-1", tasks: [] }),
      evaluatePreparationReadiness: vi.fn(),
      generateTechnicalDocument: vi.fn(),
      createTechnicalResponseDraft: vi.fn().mockRejectedValueOnce(new TypeError("Synthetic network failure")).mockResolvedValue(receipt),
      claimCollaboratorTask: vi.fn(),
      recordCollaboratorTaskResult: vi.fn(),
      completeCollaboratorTask: vi.fn(),
      transmitPreparationSnapshot: vi.fn(),
      getPreparationResponsePlans: vi.fn().mockResolvedValue({ package_id: "package-1", plans: [current] }),
    } satisfies WizardApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderWizardHook(api, setMessage);
    act(() => { result.current.setWizardCaseId("case-1"); result.current.setWizardPackageId("package-1"); });
    await act(async () => { await result.current.loadCollaboratorWizard(); });

    expect(result.current.canCreateWizardResponseDraft).toBe(true);
    await act(async () => { await result.current.createWizardResponseDraft(); });
    expect(result.current.wizardResponsePlan.draftRequestState).toBe("UNKNOWN");
    expect(result.current.canCreateWizardResponseDraft).toBe(false);
    expect(api.createTechnicalResponseDraft).toHaveBeenCalledTimes(1);
    await act(async () => { await result.current.retryWizardResponseDraft(); });

    expect(api.createTechnicalResponseDraft).toHaveBeenCalledTimes(2);
    expect(api.createTechnicalResponseDraft.mock.calls[0]).toEqual(api.createTechnicalResponseDraft.mock.calls[1]);
    expect(api.createTechnicalResponseDraft.mock.calls[0]?.[1]).toMatchObject({
      expected_package_revision: 8,
      source_document_id: "document-1",
      section_codes: ["METHOD"],
      source_refs: ["proposal-1"],
    });
    expect(result.current.wizardResponsePlan.draftRequestState).toBe("RECEIVED");
  });

  it("keeps a source byte verification failure UNKNOWN and retries only the same draft intent", async () => {
    const current = responsePlan("SOURCES_CURRENT");
    const packageWithDocument: PreparationPackage = {
      ...preparation(),
      aggregate_revision: 8,
      generated_documents: [{ document_id: "document-1", version: 1, document_kind: "TECHNICAL_RESPONSE", state: "GENERATED", readiness_revision: 3 }],
    };
    const receipt = { status: "SUCCEEDED" as const, command_id: "draft-command", idempotency_key: "draft-retry", result_code: "TECHNICAL_RESPONSE_DRAFT_CREATED", aggregate_refs: [], event_ids: [], replayed: false };
    const sourceUnknown = Object.assign(new Error("RESPONSE_PLAN_UNKNOWN"), {
      status: 422,
      detail: "RESPONSE_PLAN_UNKNOWN",
    });
    const api = {
      getCollaboratorPreparation: vi.fn().mockResolvedValue(packageWithDocument),
      listCollaboratorTasks: vi.fn().mockResolvedValue({ case_id: "case-1", tasks: [] }),
      evaluatePreparationReadiness: vi.fn(),
      generateTechnicalDocument: vi.fn(),
      createTechnicalResponseDraft: vi.fn().mockRejectedValueOnce(sourceUnknown).mockResolvedValue(receipt),
      claimCollaboratorTask: vi.fn(),
      recordCollaboratorTaskResult: vi.fn(),
      completeCollaboratorTask: vi.fn(),
      transmitPreparationSnapshot: vi.fn(),
      getPreparationResponsePlans: vi.fn().mockResolvedValue({ package_id: "package-1", plans: [current] }),
    } satisfies WizardApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderWizardHook(api, setMessage);
    act(() => { result.current.setWizardCaseId("case-1"); result.current.setWizardPackageId("package-1"); });
    await act(async () => { await result.current.loadCollaboratorWizard(); });

    await act(async () => { await result.current.createWizardResponseDraft(); });
    expect(result.current.wizardResponsePlan.draftRequestState).toBe("SOURCE_UNKNOWN");
    expect(result.current.canCreateWizardResponseDraft).toBe(false);
    await act(async () => { await result.current.retryWizardResponseDraft(); });
    expect(api.createTechnicalResponseDraft).toHaveBeenCalledTimes(2);
    expect(api.createTechnicalResponseDraft.mock.calls[0]).toEqual(api.createTechnicalResponseDraft.mock.calls[1]);
    expect(result.current.wizardResponsePlan.draftRequestState).toBe("RECEIVED");
  });

  it("transmits a selected snapshot with an optimistic package revision and no external deposit", async () => {
    const api = {
      getCollaboratorPreparation: vi.fn().mockResolvedValue(preparation()),
      listCollaboratorTasks: vi.fn().mockResolvedValue({ case_id: "case-1", tasks: [] }),
      evaluatePreparationReadiness: vi.fn(),
      generateTechnicalDocument: vi.fn(),
      createTechnicalResponseDraft: vi.fn(),
      claimCollaboratorTask: vi.fn(),
      recordCollaboratorTaskResult: vi.fn(),
      completeCollaboratorTask: vi.fn(),
      transmitPreparationSnapshot: vi.fn()
        .mockRejectedValueOnce(new Error("Connexion interrompue"))
        .mockResolvedValueOnce({}),
    } satisfies WizardApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderWizardHook(api, setMessage);

    act(() => {
      result.current.setWizardCaseId("case-1");
      result.current.setWizardPackageId("package-1");
      result.current.setWizardSnapshotId(" snapshot-1 ");
      result.current.setWizardTransmissionId(" transmission-1 ");
    });
    await act(async () => {
      await result.current.loadCollaboratorWizard();
    });
    await act(async () => {
      await result.current.transmitWizardSnapshot();
    });
    const firstIntent = (api.transmitPreparationSnapshot as ReturnType<typeof vi.fn>).mock.calls[0];
    await act(async () => {
      await result.current.transmitWizardSnapshot();
    });

    expect(api.transmitPreparationSnapshot).toHaveBeenNthCalledWith(1, "package-1", expect.objectContaining({
      snapshot_id: "snapshot-1",
      transmission_id: "transmission-1",
      expected_package_revision: 7,
      command_id: expect.any(String),
      idempotency_key: expect.any(String),
      correlation_id: expect.any(String),
    }));
    expect(api.transmitPreparationSnapshot).toHaveBeenNthCalledWith(2, "package-1", firstIntent[1]);
    expect(setMessage).toHaveBeenLastCalledWith({
      tone: "success",
      text: expect.stringContaining("transmission-1"),
    });
  });

  it("creates a complete snapshot with the same command identity after an unknown response", async () => {
    const snapshotReceipt = {
      status: "SUCCEEDED" as const,
      command_id: "snapshot-command",
      idempotency_key: "snapshot-key",
      result_code: "PREPARATION_SNAPSHOT_CREATED",
      aggregate_refs: [{ aggregate_type: "PreparationSnapshot", aggregate_id: "snapshot-1", aggregate_revision: 2 }],
      event_ids: ["snapshot-event"],
      replayed: false,
    };
    const api = {
      getCollaboratorPreparation: vi.fn().mockResolvedValue(preparation()),
      listCollaboratorTasks: vi.fn().mockResolvedValue({ case_id: "case-1", tasks: [] }),
      evaluatePreparationReadiness: vi.fn(),
      generateTechnicalDocument: vi.fn(),
      createTechnicalResponseDraft: vi.fn(),
      claimCollaboratorTask: vi.fn(),
      recordCollaboratorTaskResult: vi.fn(),
      completeCollaboratorTask: vi.fn(),
      createPreparationSnapshot: vi.fn()
        .mockRejectedValueOnce(new Error("Connexion interrompue"))
        .mockResolvedValueOnce(snapshotReceipt),
      transmitPreparationSnapshot: vi.fn(),
    } satisfies WizardApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderWizardHook(api, setMessage);
    act(() => {
      result.current.setWizardCaseId("case-1");
      result.current.setWizardPackageId("package-1");
      result.current.setWizardSnapshotId("snapshot-1");
    });
    await act(async () => {
      await result.current.loadCollaboratorWizard();
    });
    await act(async () => {
      await result.current.createWizardSnapshot();
    });
    expect(result.current.wizardSnapshotRetryPending).toBe(true);
    await act(async () => {
      await result.current.createWizardSnapshot();
    });
    expect(api.createPreparationSnapshot).toHaveBeenCalledTimes(2);
    expect(api.createPreparationSnapshot.mock.calls[1]).toEqual(api.createPreparationSnapshot.mock.calls[0]);
    expect(result.current.wizardSnapshotReceipt).toEqual({
      snapshot_id: "snapshot-1",
      receipt: snapshotReceipt,
    });
    expect(result.current.wizardSnapshotId).toBe("snapshot-1");
  });
});
