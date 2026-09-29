import { act, renderHook, waitFor } from "@testing-library/react";
import { expect, test, vi } from "vitest";
import type { ApiClient } from "../../infrastructure/api";
import type { CaseExecutionResults } from "../../shared/types";
import { useCaseExecutionResults } from "./useCaseExecutionResults";

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

const response = (caseId: string): CaseExecutionResults => ({ case_id: caseId, lot_references: ["01"], results: [] });

test("case change hides prior lot data and late responses cannot cross cases", async () => {
  const case1 = deferred<CaseExecutionResults>();
  const case2 = deferred<CaseExecutionResults>();
  const api = { listCaseExecutionResults: vi.fn((caseId: string) => caseId === "case-1" ? case1.promise : case2.promise) } as unknown as ApiClient;
  const { result, rerender } = renderHook(({ caseId }) => useCaseExecutionResults(api, caseId), { initialProps: { caseId: "case-1" } });
  rerender({ caseId: "case-2" });
  expect(result.current.data).toBeNull();
  act(() => case1.resolve(response("case-1")));
  act(() => case2.resolve(response("case-2")));
  await waitFor(() => expect(result.current.data?.case_id).toBe("case-2"));
  expect(result.current.status).toBe("READY");
});

test("a failed refresh keeps data explicitly unavailable and disables optimistic assumptions", async () => {
  const api = { listCaseExecutionResults: vi.fn().mockResolvedValueOnce(response("case-1")).mockRejectedValueOnce(new Error("offline")) } as unknown as ApiClient;
  const { result } = renderHook(() => useCaseExecutionResults(api, "case-1"));
  await waitFor(() => expect(result.current.status).toBe("READY"));
  await act(async () => { await result.current.refresh(); });
  await waitFor(() => expect(result.current.status).toBe("UNAVAILABLE"));
  expect(result.current.data?.case_id).toBe("case-1");
});
