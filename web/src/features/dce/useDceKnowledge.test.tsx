import type { Dispatch, SetStateAction } from "react";

import { act, renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ApiClient } from "../../infrastructure/api";
import type { CaseDceReading, KnowledgeSearchResponse, KnowledgeSearchResult } from "../../shared/types";
import { useDceKnowledge } from "./useDceKnowledge";

type HookMessage = { tone: "success" | "error" | "warning"; text: string };
type DceApi = Pick<ApiClient, "getCaseDceReading" | "searchCaseKnowledge">;

const reading: CaseDceReading = {
  case_id: "case-1",
  work_label: "Réhabilitation du groupe scolaire",
  case_lifecycle: "PREPARATION",
  commercial_stage: "QUALIFICATION",
  dce_freshness: "CURRENT",
  availability: "AVAILABLE",
  dce: {
    dce_version_id: "dce-1",
    lifecycle: "ADMITTED",
    integrity: "VERIFIED",
    classification_readiness: "READY",
    analysis_readiness: "READY",
    source_received_at: "2026-08-20T12:00:00Z",
  },
  counters: {
    total: 3,
    pending_human_confirmation: 1,
    confirmed: 2,
    review_required: 0,
    not_applicable: 0,
  },
  requirements: [],
};

const result: KnowledgeSearchResult = {
  source_fragment_id: "fragment-1",
  dce_version_id: "dce-1",
  score: 0.91,
  locator: { label: "CCTP · page 12" },
  embedding_model: "TEST_PROVIDER",
};

function renderDceHook(
  api: DceApi,
  setMessage: Dispatch<SetStateAction<HookMessage | null>>,
  caseId = "case-1",
) {
  return renderHook(() => useDceKnowledge(api as ApiClient, setMessage, caseId));
}

function deferredSearch() {
  let resolve!: (value: KnowledgeSearchResponse) => void;
  let reject!: (reason: Error) => void;
  const promise = new Promise<KnowledgeSearchResponse>((resolvePromise, rejectPromise) => {
    resolve = resolvePromise;
    reject = rejectPromise;
  });
  return { promise, resolve, reject };
}

const searchResponse: KnowledgeSearchResponse = { case_id: "case-1", query: "délai", results: [result] };

function renderScopedSearch(api: DceApi, setMessage = vi.fn()) {
  return renderHook(({ caseId, scope }) => useDceKnowledge(api as ApiClient, setMessage, caseId, scope), {
    initialProps: { caseId: "case-1", scope: "tenant-a:session-a:patron" },
  });
}

describe("useDceKnowledge", () => {
  it("loads the case DCE reading", async () => {
    const api = {
      getCaseDceReading: vi.fn().mockResolvedValue(reading),
      searchCaseKnowledge: vi.fn(),
    } satisfies DceApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result: hook } = renderDceHook(api, setMessage);

    await act(async () => {
      await hook.current.loadReading();
    });

    expect(api.getCaseDceReading).toHaveBeenCalledWith("case-1");
    expect(hook.current.reading?.counters.pending_human_confirmation).toBe(1);
  });

  it("masks a DCE reading immediately after the authenticated scope changes", async () => {
    const api = { getCaseDceReading: vi.fn().mockResolvedValue(reading), searchCaseKnowledge: vi.fn() } satisfies DceApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result, rerender } = renderHook(({ scope }) => useDceKnowledge(api as unknown as ApiClient, setMessage, "case-1", scope), { initialProps: { scope: "tenant-a:session-a" } });
    await act(async () => { await result.current.loadReading(); });
    expect(result.current.reading?.case_id).toBe("case-1");
    rerender({ scope: "tenant-b:session-b" });
    expect(result.current.reading).toBeNull();
  });

  it("searches the selected case and keeps the top-k bound", async () => {
    const api = {
      getCaseDceReading: vi.fn(),
      searchCaseKnowledge: vi.fn().mockResolvedValue({
        case_id: "case-1",
        query: "délai",
        results: [result],
      }),
    } satisfies DceApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result: hook } = renderDceHook(api, setMessage);

    await act(async () => {
      hook.current.setQuery("  délai  ");
    });
    await act(async () => {
      await hook.current.searchKnowledge();
    });

    expect(api.searchCaseKnowledge).toHaveBeenCalledWith("case-1", "délai", 5);
    expect(hook.current.results).toEqual([result]);
  });

  it("validates an empty search before calling the API", async () => {
    const api = {
      getCaseDceReading: vi.fn(),
      searchCaseKnowledge: vi.fn(),
    } satisfies DceApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result: hook } = renderDceHook(api, setMessage);

    await act(async () => {
      await hook.current.searchKnowledge();
    });

    expect(api.searchCaseKnowledge).not.toHaveBeenCalled();
    expect(setMessage).toHaveBeenCalledWith({ tone: "warning", text: "Saisissez un terme de recherche DCE." });
  });

  it("keeps a normal 404 reading absence silent", async () => {
    const api = {
      getCaseDceReading: vi.fn().mockRejectedValue(Object.assign(new Error("missing"), { status: 404 })),
      searchCaseKnowledge: vi.fn(),
    } satisfies DceApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result: hook } = renderDceHook(api, setMessage);

    await act(async () => {
      await hook.current.loadReading();
    });

    expect(hook.current.reading).toBeNull();
    expect(setMessage).not.toHaveBeenCalled();
  });

  it("keeps manual reading available when knowledge retrieval is unavailable", async () => {
    const api = {
      getCaseDceReading: vi.fn(),
      searchCaseKnowledge: vi.fn().mockRejectedValue(
        Object.assign(new Error("KNOWLEDGE_RETRIEVAL_UNAVAILABLE"), {
          status: 503,
          detail: "KNOWLEDGE_RETRIEVAL_UNAVAILABLE",
        }),
      ),
    } satisfies DceApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result: hook } = renderDceHook(api, setMessage);
    await act(async () => {
      hook.current.setQuery("délai");
    });
    await act(async () => {
      await hook.current.searchKnowledge();
    });

    expect(hook.current.results).toEqual([]);
    expect(setMessage).toHaveBeenCalledWith({
      tone: "error",
      text: "Assistance IA indisponible. La lecture des sources et les contrôles manuels restent disponibles.",
    });
  });

  it.each([
    { caseId: "case-2", scope: "tenant-a:session-a:patron" },
    { caseId: "case-1", scope: "tenant-b:session-b:patron" },
    { caseId: "case-1", scope: "tenant-a:session-a:collaborator" },
    { caseId: "case-1", scope: "" },
  ])("masks search results, query and busy state immediately for $caseId / $scope", async (context) => {
    const pending = deferredSearch();
    const api = { getCaseDceReading: vi.fn(), searchCaseKnowledge: vi.fn().mockResolvedValueOnce(searchResponse).mockReturnValueOnce(pending.promise) };
    const { result: hook, rerender } = renderScopedSearch(api);
    await act(async () => { hook.current.setQuery("délai"); });
    await act(async () => { await hook.current.searchKnowledge(); });
    expect(hook.current.results).toEqual([result]);
    let request!: Promise<void>;
    act(() => { request = hook.current.searchKnowledge(); });
    expect(hook.current.searching).toBe(true);
    rerender(context);
    expect(hook.current.results).toEqual([]);
    expect(hook.current.query).toBe("");
    expect(hook.current.searching).toBe(false);
    await act(async () => { pending.resolve(searchResponse); await request; });
    expect(hook.current.results).toEqual([]);
  });

  it("does not revive a delayed response after leaving and returning to the same scope", async () => {
    const pending = deferredSearch();
    const api = { getCaseDceReading: vi.fn(), searchCaseKnowledge: vi.fn().mockReturnValue(pending.promise) };
    const { result: hook, rerender } = renderScopedSearch(api);
    await act(async () => { hook.current.setQuery("délai"); });
    let request!: Promise<void>;
    act(() => { request = hook.current.searchKnowledge(); });
    rerender({ caseId: "case-2", scope: "tenant-a:session-a:patron" });
    rerender({ caseId: "case-1", scope: "tenant-a:session-a:patron" });
    await act(async () => { pending.resolve(searchResponse); await request; });
    expect(hook.current.results).toEqual([]);
    expect(hook.current.searching).toBe(false);
  });

  it("ignores an old failure without clearing a newer result or showing its message", async () => {
    const pending = deferredSearch();
    const api = { getCaseDceReading: vi.fn(), searchCaseKnowledge: vi.fn().mockReturnValueOnce(pending.promise).mockResolvedValueOnce(searchResponse) };
    const message = vi.fn();
    const { result: hook } = renderScopedSearch(api, message);
    await act(async () => { hook.current.setQuery("délai"); });
    let oldRequest!: Promise<void>;
    act(() => { oldRequest = hook.current.searchKnowledge(); });
    await act(async () => { await hook.current.searchKnowledge(); });
    await act(async () => { pending.reject(new Error("old private error")); await oldRequest; });
    expect(hook.current.results).toEqual([result]);
    expect(hook.current.searching).toBe(false);
    expect(message).not.toHaveBeenCalled();
  });

  it("keeps the newest search when responses arrive out of order", async () => {
    const first = deferredSearch();
    const second = deferredSearch();
    const api = { getCaseDceReading: vi.fn(), searchCaseKnowledge: vi.fn().mockReturnValueOnce(first.promise).mockReturnValueOnce(second.promise) };
    const { result: hook } = renderScopedSearch(api);
    await act(async () => { hook.current.setQuery("délai"); });
    let oldRequest!: Promise<void>;
    act(() => { oldRequest = hook.current.searchKnowledge(); });
    await act(async () => { hook.current.setQuery("visite"); });
    let newRequest!: Promise<void>;
    act(() => { newRequest = hook.current.searchKnowledge(); });
    const newer = { ...result, source_fragment_id: "fragment-2" };
    await act(async () => { second.resolve({ ...searchResponse, query: "visite", results: [newer] }); await newRequest; });
    await act(async () => { first.resolve(searchResponse); await oldRequest; });
    expect(hook.current.results).toEqual([newer]);
    expect(hook.current.query).toBe("visite");
  });

  it.each(["reset", "edit"])("invalidates an in-flight search on %s", async (action) => {
    const pending = deferredSearch();
    const api = { getCaseDceReading: vi.fn(), searchCaseKnowledge: vi.fn().mockReturnValue(pending.promise) };
    const { result: hook } = renderScopedSearch(api);
    await act(async () => { hook.current.setQuery("délai"); });
    let request!: Promise<void>;
    act(() => { request = hook.current.searchKnowledge(); });
    act(() => { if (action === "reset") hook.current.resetSearch(); else hook.current.setQuery("visite"); });
    expect(hook.current.results).toEqual([]);
    expect(hook.current.searching).toBe(false);
    await act(async () => { pending.resolve(searchResponse); await request; });
    expect(hook.current.results).toEqual([]);
  });

  it.each([
    { case_id: "case-other", query: "délai" },
    { case_id: "case-1", query: "other-query" },
  ])("refuses a response with mismatched identity $case_id / $query", async (identity) => {
    const api = { getCaseDceReading: vi.fn(), searchCaseKnowledge: vi.fn().mockResolvedValue({ ...searchResponse, ...identity }) };
    const { result: hook } = renderScopedSearch(api);
    await act(async () => { hook.current.setQuery("délai"); });
    await act(async () => { await hook.current.searchKnowledge(); });
    expect(hook.current.results).toEqual([]);
    expect(hook.current.searching).toBe(false);
  });

  it("refuses results from a DCE version different from the loaded reading", async () => {
    const api = { getCaseDceReading: vi.fn().mockResolvedValue(reading), searchCaseKnowledge: vi.fn().mockResolvedValue({ ...searchResponse, results: [{ ...result, dce_version_id: "old-dce" }] }) };
    const { result: hook } = renderScopedSearch(api);
    await act(async () => { await hook.current.loadReading(); });
    await act(async () => { hook.current.setQuery("délai"); });
    await act(async () => { await hook.current.searchKnowledge(); });
    expect(hook.current.results).toEqual([]);
    expect(hook.current.reading?.dce.dce_version_id).toBe("dce-1");
  });

  it("masks previous results when the loaded DCE version changes", async () => {
    const api = { getCaseDceReading: vi.fn().mockResolvedValueOnce(reading).mockResolvedValueOnce({ ...reading, dce: { ...reading.dce, dce_version_id: "dce-2" } }), searchCaseKnowledge: vi.fn().mockResolvedValue(searchResponse) };
    const { result: hook } = renderScopedSearch(api);
    await act(async () => { await hook.current.loadReading(); });
    await act(async () => { hook.current.setQuery("délai"); });
    await act(async () => { await hook.current.searchKnowledge(); });
    expect(hook.current.results).toEqual([result]);
    await act(async () => { await hook.current.loadReading(); });
    expect(hook.current.results).toEqual([]);
  });

  it("ignores an old reading error after a new case reading has succeeded", async () => {
    let reject!: (error: Error) => void;
    const oldReading = new Promise<CaseDceReading>((_, rejectPromise) => { reject = rejectPromise; });
    const api = { getCaseDceReading: vi.fn().mockReturnValueOnce(oldReading).mockResolvedValueOnce({ ...reading, case_id: "case-2" }), searchCaseKnowledge: vi.fn() };
    const message = vi.fn();
    const { result: hook, rerender } = renderScopedSearch(api, message);
    let request!: Promise<void>;
    act(() => { request = hook.current.loadReading(); });
    rerender({ caseId: "case-2", scope: "tenant-a:session-a:patron" });
    await act(async () => { await hook.current.loadReading(); });
    await act(async () => { reject(new Error("old case detail")); await request; });
    expect(hook.current.reading?.case_id).toBe("case-2");
    expect(message).not.toHaveBeenCalled();
  });

  it("invalidates reading state and errors when the scope changes without another load", async () => {
    let reject!: (error: Error) => void;
    const oldReading = new Promise<CaseDceReading>((_, rejectPromise) => { reject = rejectPromise; });
    const api = { getCaseDceReading: vi.fn().mockReturnValue(oldReading), searchCaseKnowledge: vi.fn() };
    const message = vi.fn();
    const { result: hook, rerender } = renderScopedSearch(api, message);
    let request!: Promise<void>;
    act(() => { request = hook.current.loadReading(); });
    expect(hook.current.loading).toBe(true);
    rerender({ caseId: "case-1", scope: "tenant-b:session-b:patron" });
    expect(hook.current.loading).toBe(false);
    await act(async () => { reject(new Error("old scope detail")); await request; });
    expect(hook.current.reading).toBeNull();
    expect(message).not.toHaveBeenCalled();
  });
});
