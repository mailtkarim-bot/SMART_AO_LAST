import type { Dispatch, SetStateAction } from "react";
import { act, renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ApiClient } from "../../infrastructure/api";
import type {
  PricingImportBatchRead,
  PricingImportCommitReceipt,
  PricingImportPreview,
} from "../../shared/types";
import { usePricingImport } from "./usePricingImport";

type HookMessage = { tone: "success" | "error" | "warning"; text: string };
type PricingApi = Partial<Pick<
  ApiClient,
  "commitPricingImport" | "createPricingImportPreview" | "getPricingImport"
>>;

const preview = (overrides: Partial<PricingImportPreview> = {}): PricingImportPreview => ({
  batch_id: "batch-2",
  case_id: "case-1",
  document_kind: "EXCEL",
  state: "PREVIEWED",
  aggregate_revision: 1,
  row_count: 2,
  valid_row_count: 2,
  error_count: 0,
  total_minor: 32500,
  rows: [],
  filename: "pricing.xlsx",
  truncated: false,
  limit_reason: null,
  result_code: "PRICING_IMPORT_PREVIEWED",
  command_id: "command-preview",
  idempotency_key: "idempotency-preview",
  event_ids: ["event-preview"],
  replayed: false,
  ...overrides,
});

type CommitInput = Parameters<ApiClient["commitPricingImport"]>[2];
const receipt = (replayed = false, input?: Pick<CommitInput, "command_id" | "idempotency_key">): PricingImportCommitReceipt => ({
  status: "SUCCEEDED",
  command_id: input?.command_id ?? "command-1",
  idempotency_key: input?.idempotency_key ?? "idempotency-1",
  result_code: "PRICING_IMPORT_COMMITTED",
  aggregate_refs: [
    {
      aggregate_type: "FinancialReportSnapshot",
      aggregate_id: "report-1",
      aggregate_revision: 4,
    },
    {
      aggregate_type: "PricingImportBatch",
      aggregate_id: "batch-1",
      aggregate_revision: 3,
    },
  ],
  event_ids: ["event-1"],
  replayed,
});

const echoReceipt = (replayed = false) => async (_caseId: string, _batchId: string, input: CommitInput) => receipt(replayed, input);

function renderPricingHook(
  api: PricingApi,
  setMessage: Dispatch<SetStateAction<HookMessage | null>>,
  onDraftReload: () => Promise<void> = vi.fn().mockResolvedValue(undefined),
) {
  return renderHook(() =>
    usePricingImport(
      api as ApiClient,
      setMessage,
      "report-1",
      "case-1",
      onDraftReload,
    ),
  );
}

function setBatch(result: { current: ReturnType<typeof usePricingImport> }) {
  act(() => {
    result.current.setPricingImportBatchId(" batch-1 ");
  });
}

describe("usePricingImport", () => {
  it("keeps the same uncertain intent when only report whitespace changes", async () => {
    const api = { commitPricingImport: vi.fn().mockRejectedValue(new TypeError("response lost")) };
    const { result, rerender } = renderHook(({ reportId }) => usePricingImport(api as unknown as ApiClient, vi.fn(), reportId, "case-1", vi.fn()), { initialProps: { reportId: "report-1" } });
    setBatch(result);
    await act(async () => { await result.current.commitPricingImport(); });
    rerender({ reportId: " report-1 " });
    expect(result.current.pricingImportState).toBe("UNKNOWN");
    act(() => { result.current.setPricingImportBatchId("replacement"); });
    expect(result.current.pricingImportBatchId).toBe(" batch-1 ");
  });

  it("keeps a mismatched receipt unknown without reading the draft", async () => {
    const api = { commitPricingImport: vi.fn().mockResolvedValue(receipt()) };
    const reload = vi.fn();
    const { result } = renderPricingHook(api, vi.fn(), reload);
    setBatch(result);
    await act(async () => { await result.current.commitPricingImport(); });
    expect(result.current.pricingImportState).toBe("UNKNOWN");
    expect(reload).not.toHaveBeenCalled();
  });

  it("does not expose a preview returned for another affair", async () => {
    const api = { createPricingImportPreview: vi.fn().mockResolvedValue(preview({ case_id: "foreign-case" })) };
    const { result } = renderPricingHook(api, vi.fn());
    await act(async () => { await result.current.previewPricingImport(new File(["xlsx"], "prices.xlsx")); });
    expect(result.current.pricingImportPreview).toBeNull();
    expect(result.current.pricingImportState).toBe("UNKNOWN");
  });

  it("masks the prior owner and blocks a synchronous double commit", async () => {
    let resolve!: (value: PricingImportCommitReceipt) => void;
    const api = { commitPricingImport: vi.fn().mockImplementation(() => new Promise<PricingImportCommitReceipt>((done) => { resolve = done; })) };
    const reload = vi.fn();
    const { result, rerender } = renderHook(({ owner }) => usePricingImport(api as unknown as ApiClient, vi.fn(), "report-1", "case-1", reload, owner), { initialProps: { owner: "owner-1" } });
    setBatch(result);
    let pending!: Promise<void>;
    act(() => { pending = result.current.commitPricingImport(); void result.current.commitPricingImport(); });
    expect(api.commitPricingImport).toHaveBeenCalledTimes(1);
    rerender({ owner: "owner-2" });
    await act(async () => { resolve(receipt(false, api.commitPricingImport.mock.calls[0][2])); await pending; });
    expect(result.current.pricingImportState).toBe("IDLE");
    expect(result.current.pricingImportBatchId).toBe("");
    expect(reload).not.toHaveBeenCalled();
  });

  it("keeps a 503 preview uncertain, blocks replacement and GET, then replays exactly", async () => {
    const api = {
      createPricingImportPreview: vi.fn().mockRejectedValueOnce(Object.assign(new Error("unavailable"), { status: 503 })).mockResolvedValueOnce(preview()),
      getPricingImport: vi.fn(),
    } satisfies PricingApi;
    const { result } = renderPricingHook(api, vi.fn());
    const file = new File(["xlsx"], "pricing.xlsx");
    await act(async () => { await result.current.previewPricingImport(file); });
    expect(result.current.pricingImportState).toBe("UNKNOWN");
    await act(async () => {
      await result.current.previewPricingImport(new File(["other"], "other.xlsx"));
      result.current.setPricingImportBatchId("other-batch");
      await result.current.reloadPricingImport();
    });
    expect(api.createPricingImportPreview).toHaveBeenCalledTimes(1);
    expect(api.getPricingImport).not.toHaveBeenCalled();
    await act(async () => { await result.current.retryPricingImportPreview(); });
    expect(api.createPricingImportPreview.mock.calls[1]).toEqual(api.createPricingImportPreview.mock.calls[0]);
  });

  it("suppresses a synchronous double preview and isolates its late response", async () => {
    let resolve!: (value: PricingImportPreview) => void;
    const api = { createPricingImportPreview: vi.fn().mockImplementation(() => new Promise<PricingImportPreview>((done) => { resolve = done; })) };
    const setMessage = vi.fn();
    const { result, rerender } = renderHook(({ caseId }) => usePricingImport(api as unknown as ApiClient, setMessage, "report-1", caseId, vi.fn()), { initialProps: { caseId: "case-1" } });
    const file = new File(["xlsx"], "pricing.xlsx");
    let pending!: Promise<void>;
    act(() => { pending = result.current.previewPricingImport(file); void result.current.previewPricingImport(file); });
    expect(api.createPricingImportPreview).toHaveBeenCalledTimes(1);
    rerender({ caseId: "case-2" });
    await act(async () => { resolve(preview()); await pending; });
    expect(result.current.pricingImportPreview).toBeNull();
    expect(result.current.pricingImportBatchId).toBe("");
    expect(setMessage).not.toHaveBeenCalled();
  });

  it("retries an uncertain commit in its original context with frozen revisions", async () => {
    const api = { commitPricingImport: vi.fn().mockRejectedValueOnce(Object.assign(new Error("unavailable"), { status: 503 })).mockImplementationOnce(echoReceipt()) };
    const { result, rerender } = renderHook(({ caseId }) => usePricingImport(api as unknown as ApiClient, vi.fn(), "report-1", caseId, vi.fn()), { initialProps: { caseId: "case-1" } });
    setBatch(result);
    await act(async () => { await result.current.commitPricingImport(); });
    expect(result.current.pricingImportState).toBe("UNKNOWN");
    act(() => { result.current.setPricingImportBatchRevision("99"); });
    rerender({ caseId: "case-2" });
    expect(result.current.pricingImportState).toBe("IDLE");
    rerender({ caseId: "case-1" });
    expect(result.current.pricingImportState).toBe("UNKNOWN");
    await act(async () => { await result.current.retryPricingImportCommit(); });
    expect(api.commitPricingImport.mock.calls[1]).toEqual(api.commitPricingImport.mock.calls[0]);
    expect(result.current.pricingImportState).toBe("COMMITTED");
  });

  it("persists an uploaded preview and exposes its batch revision", async () => {
    const api = {
      createPricingImportPreview: vi.fn().mockResolvedValue(preview()),
    } satisfies PricingApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderPricingHook(api, setMessage);
    const file = new File(["xlsx"], "pricing.xlsx");

    await act(async () => {
      await result.current.previewPricingImport(file);
    });

    expect(api.createPricingImportPreview).toHaveBeenCalledWith(
      "case-1",
      file,
      "EXCEL",
      expect.objectContaining({
        command_id: expect.any(String),
        idempotency_key: expect.any(String),
        correlation_id: expect.any(String),
      }),
    );
    expect(result.current.pricingImportBatchId).toBe("batch-2");
    expect(result.current.pricingImportBatchRevision).toBe("1");
    expect(result.current.pricingImportState).toBe("PREVIEWED");
    expect(result.current.pricingImportPreview?.total_minor).toBe(32500);
  });

  it("warns the patron when the preview hit a safety budget and was truncated", async () => {
    const api = {
      createPricingImportPreview: vi.fn().mockResolvedValue(
        preview({ truncated: true, limit_reason: "ROW_LIMIT" }),
      ),
    } satisfies PricingApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderPricingHook(api, setMessage);
    const file = new File(["xlsx"], "pricing.xlsx");

    await act(async () => {
      await result.current.previewPricingImport(file);
    });

    expect(result.current.pricingImportState).toBe("PREVIEWED");
    const mockSetMessage = setMessage as unknown as { mock: { calls: [HookMessage][] } };
    const message = mockSetMessage.mock.calls.at(-1)?.[0] ?? null;
    expect(message?.tone).toBe("warning");
    expect(message?.text).toContain("limite de lignes");
  });

  it("keeps an unknown preview and replays it with the same identifiers", async () => {
    const api = {
      createPricingImportPreview: vi
        .fn()
        .mockRejectedValueOnce(new TypeError("network unavailable"))
        .mockResolvedValueOnce(preview({ replayed: true })),
    } satisfies PricingApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderPricingHook(api, setMessage);
    const file = new File(["xlsx"], "pricing.xlsx");

    await act(async () => {
      await result.current.previewPricingImport(file);
    });
    expect(result.current.pricingImportState).toBe("UNKNOWN");
    expect(result.current.pricingImportUnknownAction).toBe("PREVIEW");

    await act(async () => {
      await result.current.retryPricingImportPreview();
    });
    expect(result.current.pricingImportState).toBe("PREVIEWED");
    const first = api.createPricingImportPreview.mock.calls[0]?.[3];
    const second = api.createPricingImportPreview.mock.calls[1]?.[3];
    expect(second).toEqual(first);
  });

  it("reloads a persisted batch and reflects its committed state", async () => {
    const committed: PricingImportBatchRead = {
      ...preview({ batch_id: "batch-1" }),
      state: "COMMITTED",
      aggregate_revision: 2,
    };
    const api = {
      getPricingImport: vi.fn().mockResolvedValue(committed),
    } satisfies PricingApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderPricingHook(api, setMessage);
    setBatch(result);

    await act(async () => {
      await result.current.reloadPricingImport();
    });

    expect(api.getPricingImport).toHaveBeenCalledWith("case-1", "batch-1");
    expect(result.current.pricingImportState).toBe("COMMITTED");
    expect(result.current.pricingImportBatchRevision).toBe("2");
  });

  it("rejects a commit without a batch", async () => {
    const api = { commitPricingImport: vi.fn() } satisfies PricingApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderPricingHook(api, setMessage);

    await act(async () => {
      await result.current.commitPricingImport();
    });

    expect(api.commitPricingImport).not.toHaveBeenCalled();
    expect(setMessage).toHaveBeenCalledWith({
      tone: "error",
      text: "Sélectionnez une affaire, un batch et un brouillon avant le commit.",
    });
  });

  it("commits validated rows, updates revisions and confirms reload", async () => {
    const api = { commitPricingImport: vi.fn().mockImplementation(echoReceipt()) } satisfies PricingApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const onDraftReload = vi.fn().mockResolvedValue(undefined);
    const { result } = renderPricingHook(api, setMessage, onDraftReload);
    setBatch(result);

    await act(async () => {
      await result.current.commitPricingImport();
    });

    expect(api.commitPricingImport).toHaveBeenCalledWith("case-1", "batch-1", {
      report_id: "report-1",
      expected_batch_revision: 1,
      expected_report_revision: 0,
      command_id: expect.any(String),
      idempotency_key: expect.any(String),
    });
    expect(onDraftReload).toHaveBeenCalledOnce();
    expect(result.current.pricingImportState).toBe("COMMITTED");
    expect(result.current.pricingImportReloadState).toBe("SUCCEEDED");
    expect(result.current.pricingImportBatchRevision).toBe("3");
    expect(result.current.pricingImportReportRevision).toBe("4");
    expect(result.current.pricingImportSubmitting).toBe(false);
  });

  it("keeps the commit confirmed when reload fails", async () => {
    const api = { commitPricingImport: vi.fn().mockImplementation(echoReceipt()) } satisfies PricingApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const onDraftReload = vi.fn().mockRejectedValue(new Error("reload unavailable"));
    const { result } = renderPricingHook(api, setMessage, onDraftReload);
    setBatch(result);

    await act(async () => {
      await result.current.commitPricingImport();
    });

    expect(result.current.pricingImportState).toBe("COMMITTED");
    expect(result.current.pricingImportReloadState).toBe("FAILED");
    expect(setMessage).toHaveBeenLastCalledWith({
      tone: "warning",
      text: "Import confirmé, mais le brouillon n’a pas pu être rechargé. Relancez sa lecture.",
    });
  });

  it("reports an idempotent replay without changing the business outcome", async () => {
    const api = { commitPricingImport: vi.fn().mockImplementation(echoReceipt(true)) } satisfies PricingApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderPricingHook(api, setMessage);
    setBatch(result);

    await act(async () => {
      await result.current.commitPricingImport();
    });

    expect(result.current.pricingImportState).toBe("REPLAYED");
    expect(setMessage).toHaveBeenCalledWith({
      tone: "success",
      text: "Import déjà commité : rejeu idempotent sans nouvelle ligne.",
    });
  });

  it("keeps an unknown commit and replays it with the same identifiers", async () => {
    const api = {
      commitPricingImport: vi
        .fn()
        .mockRejectedValueOnce(new TypeError("network unavailable"))
        .mockImplementationOnce(echoReceipt(true)),
    } satisfies PricingApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderPricingHook(api, setMessage);
    setBatch(result);

    await act(async () => {
      await result.current.commitPricingImport();
    });
    expect(result.current.pricingImportState).toBe("UNKNOWN");
    expect(result.current.pricingImportUnknownAction).toBe("COMMIT");

    await act(async () => {
      await result.current.retryPricingImportCommit();
    });
    expect(result.current.pricingImportState).toBe("REPLAYED");
    const first = api.commitPricingImport.mock.calls[0]?.[2];
    const second = api.commitPricingImport.mock.calls[1]?.[2];
    expect(second).toEqual(first);
  });

  it("ignores a second invocation while the first commit is pending", async () => {
    let release!: (value: PricingImportCommitReceipt) => void;
    const pending = new Promise<PricingImportCommitReceipt>((resolve) => {
      release = resolve;
    });
    const api = { commitPricingImport: vi.fn().mockReturnValue(pending) } satisfies PricingApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderPricingHook(api, setMessage);
    setBatch(result);

    let firstCommit!: Promise<void>;
    await act(async () => {
      firstCommit = result.current.commitPricingImport();
      await Promise.resolve();
    });
    expect(result.current.pricingImportSubmitting).toBe(true);

    await act(async () => {
      await result.current.commitPricingImport();
    });
    expect(api.commitPricingImport).toHaveBeenCalledOnce();

    release(receipt(false, api.commitPricingImport.mock.calls[0][2]));
    await act(async () => {
      await firstCommit;
    });
    expect(result.current.pricingImportSubmitting).toBe(false);
  });

  it("resets the visible state when the pricing context changes", async () => {
    const api = { commitPricingImport: vi.fn().mockImplementation(echoReceipt()) } satisfies PricingApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const onDraftReload = vi.fn().mockResolvedValue(undefined);
    const { result, rerender } = renderHook(
      ({ caseId, reportId }) =>
        usePricingImport(api as unknown as ApiClient, setMessage, reportId, caseId, onDraftReload),
      { initialProps: { caseId: "case-1", reportId: "report-1" } },
    );
    setBatch(result);

    await act(async () => {
      await result.current.commitPricingImport();
    });
    expect(result.current.pricingImportState).toBe("COMMITTED");

    rerender({ caseId: "case-2", reportId: "report-2" });
    expect(result.current.pricingImportState).toBe("IDLE");
  });
});
