import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { CaseResolution, CaseResolutionItemKind } from "../../shared/types";
import { useCaseResolution } from "./useCaseResolution";

function projection(caseId = "case-a", kind: CaseResolutionItemKind = "REQUIREMENT"): CaseResolution {
  return { case_id: caseId, work_label: "Affaire synthétique", coverage: "PARTIAL", items: [{ item_id: kind, item_kind: kind, native_state: "UNKNOWN", source_refs: ["fixture://source"], resolution_owner: null, next_action: "REVIEW_REQUIREMENT", due_at: null, impact: null }], economic_coverage: null };
}

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (error: Error) => void;
  const promise = new Promise<T>((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

describe("useCaseResolution", () => {
  it("loads the explicit case only within an authorized context", async () => {
    const api = { getCaseResolution: vi.fn().mockResolvedValue(projection()) };
    const { result, rerender } = renderHook(({ scope }) => useCaseResolution(api, "case-a", scope), { initialProps: { scope: "" } });
    expect(api.getCaseResolution).not.toHaveBeenCalled();
    rerender({ scope: "tenant-a:patron" });
    await waitFor(() => expect(result.current.projection?.case_id).toBe("case-a"));
    expect(api.getCaseResolution).toHaveBeenCalledWith("case-a");
    rerender({ scope: "" });
    expect(result.current.projection).toBeNull();
  });

  it("ignores a late response after switching cases", async () => {
    const old = deferred<CaseResolution>();
    const api = { getCaseResolution: vi.fn().mockReturnValueOnce(old.promise).mockResolvedValueOnce(projection("case-b")) };
    const { result, rerender } = renderHook(({ caseId }) => useCaseResolution(api, caseId, "tenant-a:patron"), { initialProps: { caseId: "case-a" } });
    rerender({ caseId: "case-b" });
    await waitFor(() => expect(result.current.projection?.case_id).toBe("case-b"));
    await act(async () => old.resolve(projection("case-a")));
    expect(result.current.projection?.case_id).toBe("case-b");
  });

  it("hides the old scope immediately and ignores its late result", async () => {
    const old = deferred<CaseResolution>();
    const next = deferred<CaseResolution>();
    const api = { getCaseResolution: vi.fn().mockReturnValueOnce(old.promise).mockReturnValueOnce(next.promise) };
    const { result, rerender } = renderHook(({ scope }) => useCaseResolution(api, "case-a", scope), { initialProps: { scope: "tenant-a:patron" } });
    rerender({ scope: "tenant-b:collaborator" });
    expect(result.current.projection).toBeNull();
    await act(async () => next.resolve(projection("case-a", "TASK_BLOCKER")));
    await act(async () => old.resolve(projection("case-a", "RISK")));
    expect(result.current.projection?.items[0].item_kind).toBe("TASK_BLOCKER");
  });

  it("ignores a pending response after logout and reentry into the same scope", async () => {
    const old = deferred<CaseResolution>();
    const api = { getCaseResolution: vi.fn().mockReturnValueOnce(old.promise).mockResolvedValueOnce(projection("case-a", "TASK_BLOCKER")) };
    const { result, rerender } = renderHook(({ scope }) => useCaseResolution(api, "case-a", scope), { initialProps: { scope: "tenant-a:patron" } });
    rerender({ scope: "" });
    await act(async () => old.resolve(projection("case-a", "RISK")));
    expect(result.current.projection).toBeNull();
    rerender({ scope: "tenant-a:patron" });
    await waitFor(() => expect(result.current.projection?.items[0].item_kind).toBe("TASK_BLOCKER"));
  });

  it("clears stale data on failure and allows retry", async () => {
    const api = { getCaseResolution: vi.fn().mockRejectedValueOnce(new Error("unavailable")).mockResolvedValueOnce(projection()).mockRejectedValueOnce(new Error("failed refresh")) };
    const { result } = renderHook(() => useCaseResolution(api, "case-a", "tenant-a:patron"));
    await waitFor(() => expect(result.current.error).toBeTruthy());
    expect(result.current.projection).toBeNull();
    await act(async () => result.current.refresh());
    expect(result.current.projection?.case_id).toBe("case-a");
    await act(async () => result.current.refresh());
    expect(result.current.projection).toBeNull();
    expect(result.current.error).toBeTruthy();
  });

  it("refuses a response for another case", async () => {
    const api = { getCaseResolution: vi.fn().mockResolvedValue(projection("foreign-case")) };
    const { result } = renderHook(() => useCaseResolution(api, "case-a", "tenant-a:patron"));
    await waitFor(() => expect(result.current.error).toBeTruthy());
    expect(result.current.projection).toBeNull();
  });

  it("refuses an unsupported nature instead of silently hiding it", async () => {
    const unsupported = { ...projection(), items: [{ ...projection().items[0], item_kind: "UNSUPPORTED" }] };
    const api = { getCaseResolution: vi.fn().mockResolvedValue(unsupported) };
    const { result } = renderHook(() => useCaseResolution(api, "case-a", "tenant-a:patron"));
    await waitFor(() => expect(result.current.error).toBeTruthy());
    expect(result.current.projection).toBeNull();
  });

  it("keeps the newest refresh when an older request fails", async () => {
    const old = deferred<CaseResolution>();
    const newest = deferred<CaseResolution>();
    const api = { getCaseResolution: vi.fn().mockResolvedValueOnce(projection()).mockReturnValueOnce(old.promise).mockReturnValueOnce(newest.promise) };
    const { result } = renderHook(() => useCaseResolution(api, "case-a", "tenant-a:patron"));
    await waitFor(() => expect(result.current.projection).not.toBeNull());
    let first!: Promise<void>;
    let second!: Promise<void>;
    act(() => { first = result.current.refresh(); second = result.current.refresh(); });
    await act(async () => { newest.resolve(projection("case-a", "UNKNOWN")); await second; });
    await act(async () => { old.reject(new Error("late failure")); await first; });
    expect(result.current.projection?.items[0].item_kind).toBe("UNKNOWN");
    expect(result.current.error).toBeNull();
  });
});
