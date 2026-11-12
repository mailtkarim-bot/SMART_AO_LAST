import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { CommandReceipt, ProposeCapabilityInput } from "../../shared/types";
import { useCapabilityProposal } from "./useCapabilityProposal";

const draft = { capability_id: "cap-1", capability_version_id: "version-2", requirement_id: "requirement-1", justification: "Justification humaine synthétique." };
const receipt = (input: ProposeCapabilityInput): CommandReceipt => ({
  status: "SUCCEEDED" as const, command_id: input.command_id, idempotency_key: input.idempotency_key,
  result_code: "CAPABILITY_PROPOSED", aggregate_refs: [{ aggregate_type: "CapabilityProposal", aggregate_id: "proposal-1", aggregate_revision: 1 }], event_ids: ["event-1"], replayed: false,
});
const tasks = { case_id: "case-a", tasks: [{ task_id: "task-1", case_id: "case-a", assignment_id: "private-assignment", requirement_id: "requirement-1", title: "Tâche synthétique", task_kind: "DCE_REQUIREMENT", objective: "Synthétique", priority: "NORMAL" as const, state: "OPEN" as const, due_at: null, aggregate_revision: 0 }] };

describe("useCapabilityProposal", () => {
  it("refuses task data from another Case and hides it", async () => {
    const api = { listCollaboratorTasks: vi.fn().mockResolvedValue({ ...tasks, case_id: "case-b" }), proposeCapability: vi.fn(async () => { throw new Error("unexpected"); }) };
    const { result } = renderHook(() => useCapabilityProposal(api, "case-a", "tenant-a:session-a", vi.fn()));
    await waitFor(() => expect(result.current.taskError).toBeTruthy());
    expect(result.current.tasks).toEqual([]);
    expect(api.proposeCapability).not.toHaveBeenCalled();
  });

  it("sends one exact source without assignment_id and performs only GET after a matching receipt", async () => {
    const refresh = vi.fn().mockResolvedValue(true);
    const api = { listCollaboratorTasks: vi.fn().mockResolvedValue(tasks), proposeCapability: vi.fn(async (_caseId: string, input: ProposeCapabilityInput) => receipt(input)) };
    const { result } = renderHook(() => useCapabilityProposal(api, "case-a", "tenant-a:session-a", refresh));
    await waitFor(() => expect(result.current.tasks).toHaveLength(1));
    await act(async () => result.current.propose(draft));
    const input = api.proposeCapability.mock.calls[0][1];
    expect(input).toMatchObject(draft);
    expect(input).toMatchObject({ command_id: expect.any(String), idempotency_key: expect.any(String), correlation_id: expect.any(String) });
    expect(input).not.toHaveProperty("assignment_id");
    expect(input).not.toHaveProperty("task_id");
    expect(refresh).toHaveBeenCalledTimes(1);
    expect(result.current.status).toBe("RECEIVED");
  });

  it("reuses the exact intent after an unknown result and does not read assessments", async () => {
    const proposeCapability = vi.fn((_caseId: string, _input: ProposeCapabilityInput): Promise<CommandReceipt> => Promise.reject(new Error("connection lost")))
      .mockImplementationOnce(() => Promise.reject(new Error("connection lost")))
      .mockImplementationOnce(async (_caseId: string, input: ProposeCapabilityInput) => receipt(input));
    const api = { listCollaboratorTasks: vi.fn().mockResolvedValue(tasks), proposeCapability };
    const refresh = vi.fn().mockResolvedValue(true);
    const { result } = renderHook(() => useCapabilityProposal(api, "case-a", "tenant-a:session-a", refresh));
    await waitFor(() => expect(result.current.tasks).toHaveLength(1));
    await act(async () => result.current.propose(draft));
    expect(result.current.status).toBe("UNKNOWN");
    expect(refresh).not.toHaveBeenCalled();
    const firstIntent = api.proposeCapability.mock.calls[0][1];
    await act(async () => result.current.retry());
    expect(api.proposeCapability.mock.calls[1][1]).toEqual(firstIntent);
    expect(refresh).toHaveBeenCalledTimes(1);
    expect(result.current.status).toBe("RECEIVED");
  });

  it("reads assessments after HTTP 409 and never retries automatically", async () => {
    const api = { listCollaboratorTasks: vi.fn().mockResolvedValue(tasks), proposeCapability: vi.fn((_caseId: string, _input: ProposeCapabilityInput): Promise<CommandReceipt> => Promise.reject(Object.assign(new Error("conflict"), { status: 409 }))) };
    const refresh = vi.fn().mockResolvedValue(true);
    const { result } = renderHook(() => useCapabilityProposal(api, "case-a", "tenant-a:session-a", refresh));
    await waitFor(() => expect(result.current.tasks).toHaveLength(1));
    await act(async () => result.current.propose(draft));
    expect(result.current.status).toBe("CONFLICT");
    expect(api.proposeCapability).toHaveBeenCalledTimes(1);
    expect(refresh).toHaveBeenCalledTimes(1);
  });

  it("does not read assessments or retry after a definitive source refusal", async () => {
    const api = { listCollaboratorTasks: vi.fn().mockResolvedValue(tasks), proposeCapability: vi.fn((_caseId: string, _input: ProposeCapabilityInput): Promise<CommandReceipt> => Promise.reject(Object.assign(new Error("source refused"), { status: 404 }))) };
    const refresh = vi.fn().mockResolvedValue(true);
    const { result } = renderHook(() => useCapabilityProposal(api, "case-a", "tenant-a:session-a", refresh));
    await waitFor(() => expect(result.current.tasks).toHaveLength(1));
    await act(async () => result.current.propose(draft));
    expect(result.current.status).toBe("REJECTED");
    expect(result.current.error).toMatch(/périmètre autorisé/i);
    expect(refresh).not.toHaveBeenCalled();
    expect(api.proposeCapability).toHaveBeenCalledTimes(1);
  });

  it("blocks a double click while the first POST is unresolved", async () => {
    let resolvePost!: (value: CommandReceipt) => void;
    const api = { listCollaboratorTasks: vi.fn().mockResolvedValue(tasks), proposeCapability: vi.fn((_caseId: string, _input: ProposeCapabilityInput) => new Promise<CommandReceipt>((resolve) => { resolvePost = resolve; })) };
    const refresh = vi.fn().mockResolvedValue(true);
    const { result } = renderHook(() => useCapabilityProposal(api, "case-a", "tenant-a:session-a", refresh));
    await waitFor(() => expect(result.current.tasks).toHaveLength(1));
    let first!: Promise<void>;
    let second!: Promise<void>;
    act(() => { first = result.current.propose(draft); second = result.current.propose(draft); });
    expect(api.proposeCapability).toHaveBeenCalledOnce();
    const input = api.proposeCapability.mock.calls[0][1];
    await act(async () => { resolvePost(receipt(input)); await Promise.all([first, second]); });
    expect(result.current.status).toBe("RECEIVED");
    expect(refresh).toHaveBeenCalledOnce();
  });

  it("retries only GET if a successful POST receipt cannot be reconciled", async () => {
    const api = { listCollaboratorTasks: vi.fn().mockResolvedValue(tasks), proposeCapability: vi.fn(async (_caseId: string, input: ProposeCapabilityInput) => receipt(input)) };
    const refresh = vi.fn().mockResolvedValueOnce(false).mockResolvedValueOnce(true);
    const { result } = renderHook(() => useCapabilityProposal(api, "case-a", "tenant-a:session-a", refresh));
    await waitFor(() => expect(result.current.tasks).toHaveLength(1));
    await act(async () => result.current.propose(draft));
    expect(result.current.status).toBe("RECEIPT_READ_FAILED");
    await act(async () => result.current.retryRead());
    expect(api.proposeCapability).toHaveBeenCalledTimes(1);
    expect(refresh).toHaveBeenCalledTimes(2);
    expect(result.current.status).toBe("RECEIVED");
  });

  it("masks task and proposal state immediately when Case/session scope changes", async () => {
    let resolvePost!: (value: CommandReceipt) => void;
    const api = { listCollaboratorTasks: vi.fn().mockResolvedValue(tasks), proposeCapability: vi.fn((_caseId: string, _input: ProposeCapabilityInput) => new Promise<CommandReceipt>((resolve) => { resolvePost = resolve; })) };
    const refresh = vi.fn().mockResolvedValue(true);
    const { result, rerender } = renderHook(({ caseId, scope }) => useCapabilityProposal(api, caseId, scope, refresh), { initialProps: { caseId: "case-a", scope: "tenant-a:session-a" } });
    await waitFor(() => expect(result.current.tasks).toHaveLength(1));
    act(() => { void result.current.propose(draft); });
    expect(result.current.status).toBe("SUBMITTING");
    const input = api.proposeCapability.mock.calls[0][1];
    rerender({ caseId: "case-b", scope: "tenant-b:session-b" });
    expect(result.current.tasks).toEqual([]);
    expect(result.current.status).toBe("IDLE");
    await act(async () => resolvePost(receipt(input)));
    expect(result.current.status).toBe("IDLE");
    expect(refresh).not.toHaveBeenCalled();
  });
});
