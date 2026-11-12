import type { FormEvent } from "react";
import type { Dispatch, SetStateAction } from "react";
import { act, renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ApiClient } from "../../infrastructure/api";
import type { CommandReceipt, DraftReport, PublishedFinancialReport, FinancialReportPublicationReceipt } from "../../shared/types";
import { useFinancialDraft } from "./useFinancialDraft";

type HookMessage = { tone: "success" | "error" | "warning"; text: string };
type DraftApi = Pick<ApiClient, "createDraft" | "getDraft" | "addLine">;
const withPublication = (api: DraftApi & Partial<Pick<ApiClient, "publishFinancialReport" | "getPublishedFinancialReport">>) => ({ publishFinancialReport: vi.fn(), getPublishedFinancialReport: vi.fn(), ...api });

const receipt = (replayed = false): CommandReceipt => ({
  status: "SUCCEEDED",
  command_id: "command-draft-1",
  idempotency_key: "idempotency-draft-1",
  result_code: "FINANCIAL_REPORT_DRAFT_LINE_ADDED",
  aggregate_refs: [
    {
      aggregate_type: "FinancialReportSnapshot",
      aggregate_id: "report-1",
      aggregate_revision: 3,
    },
  ],
  event_ids: ["event-draft-1"],
  replayed,
});

const draft = (revision = 2): DraftReport => ({
  report_id: "report-1",
  case_id: "case-1",
  status: "DRAFT",
  aggregate_revision: revision,
  currency_code: "EUR",
  calculated_at: "2026-08-20T12:00:00Z",
  ruleset_version: 1,
  summary: {
    sales_total_minor: 0,
    direct_cost_total_minor: 0,
    overhead_total_minor: 0,
    subcontracting_total_minor: 0,
    contingency_total_minor: 0,
    gross_margin_minor: 0,
    gross_margin_rate_bps: 0,
    forecast_cashflow_minor: 0,
  },
  lines: [],
});

const published: PublishedFinancialReport = {
  ...draft(3), status: "PUBLISHED",
  margin_calculation: { state: "UNKNOWN", basis: "DECLARED_BASE_CATEGORIES", missing_categories: ["SALES"], basis_line_ids: [], total_cost_minor: null, gross_margin_minor: null, gross_margin_rate_bps: null, unknown_reason: "MISSING_BASE_CATEGORY", rate_unknown_reason: null },
};

function publicationReceipt(input: Parameters<ApiClient["publishFinancialReport"]>[2]): FinancialReportPublicationReceipt {
  return { ...receipt(), command_id: input.command_id, idempotency_key: input.idempotency_key, result_code: "FINANCIAL_REPORT_PUBLISHED", aggregate_refs: [{ aggregate_type: "FinancialReportSnapshot", aggregate_id: "report-1", aggregate_revision: input.expected_revision + 1 }] };
}

function publicationApi() {
  return {
    createDraft: vi.fn(), getDraft: vi.fn().mockResolvedValue(draft()), addLine: vi.fn(),
    publishFinancialReport: vi.fn().mockImplementation(async (_case: string, _report: string, input: Parameters<ApiClient["publishFinancialReport"]>[2]) => publicationReceipt(input)),
    getPublishedFinancialReport: vi.fn().mockResolvedValue(published),
  };
}

async function readForPublication(result: { current: ReturnType<typeof useFinancialDraft> }) {
  act(() => result.current.setReportId("report-1"));
  await act(async () => result.current.loadDraft());
}

describe("financial publication", () => {
  it("publishes the exact draft then reads its exact immutable revision while preserving UNKNOWN", async () => {
    const api = publicationApi();
    const { result } = renderDraftHook(api, vi.fn());
    await readForPublication(result);
    await act(async () => result.current.publishReport());
    expect(api.publishFinancialReport).toHaveBeenCalledWith("case-1", "report-1", expect.objectContaining({ expected_revision: 2 }));
    expect(result.current.publicationState).toBe("CONFIRMED");
    expect(result.current.publicationRevision).toBe(3);
    expect(result.current.publishedReport).toEqual(published);
    expect(result.current.publishedReport?.margin_calculation.state).toBe("UNKNOWN");
    expect(result.current.draft).toBeNull();
    expect(api.addLine).not.toHaveBeenCalled();
  });

  it("retries an unknown outcome with identical identities and revision and blocks draft editing", async () => {
    const api = publicationApi();
    api.publishFinancialReport.mockRejectedValueOnce({ status: 503 });
    const { result } = renderDraftHook(api, vi.fn());
    await readForPublication(result);
    await act(async () => result.current.publishReport());
    expect(result.current.publicationState).toBe("UNKNOWN");
    expect(result.current.draft).toBeNull();
    expect(result.current.publicationLocked).toBe(true);
    await act(async () => result.current.publishReport());
    expect(api.publishFinancialReport.mock.calls[0]).toEqual(api.publishFinancialReport.mock.calls[1]);
    expect(result.current.publicationState).toBe("CONFIRMED");
  });

  it("keeps the confirmed receipt when read-back fails and retries only GET", async () => {
    const api = publicationApi();
    api.getPublishedFinancialReport.mockRejectedValueOnce({ status: 503 });
    const { result } = renderDraftHook(api, vi.fn());
    await readForPublication(result);
    await act(async () => result.current.publishReport());
    expect(result.current.publicationState).toBe("CONFIRMED");
    expect(result.current.publicationRevision).toBe(3);
    expect(result.current.publishedReport).toBeNull();
    await act(async () => result.current.loadPublishedReport());
    expect(api.publishFinancialReport).toHaveBeenCalledOnce();
    expect(result.current.publishedReport).toEqual(published);
  });

  it.each([{ ...published, case_id: "foreign" }, { ...published, report_id: "foreign" }, { ...published, aggregate_revision: 4 }, { ...published, status: "DRAFT" }, { ...published, margin_calculation: null }])("does not reveal a discordant published source", async (projection) => {
    const api = publicationApi();
    api.getPublishedFinancialReport.mockResolvedValue(projection);
    const { result } = renderDraftHook(api, vi.fn());
    await readForPublication(result);
    await act(async () => result.current.publishReport());
    expect(result.current.publicationState).toBe("CONFIRMED");
    expect(result.current.publishedReport).toBeNull();
    expect(result.current.publishedReadError).toBeTruthy();
  });

  it("can read an existing PUBLISHED source without fabricating a publication receipt", async () => {
    const api = publicationApi();
    const { result } = renderDraftHook(api, vi.fn());
    act(() => result.current.setReportId("report-1"));
    await act(async () => result.current.loadPublishedReport());
    expect(result.current.publishedReport).toEqual(published);
    expect(result.current.publicationState).toBe("IDLE");
    expect(api.publishFinancialReport).not.toHaveBeenCalled();
  });

  it("does not apply a late publication acknowledgment after a session scope changes", async () => {
    const api = publicationApi();
    let resolve!: (value: FinancialReportPublicationReceipt) => void;
    api.publishFinancialReport.mockImplementationOnce(() => new Promise((r) => { resolve = r; }));
    const { result, rerender } = renderHook(({ scope }) => useFinancialDraft(api, vi.fn(), "case-1", scope), { initialProps: { scope: "session-a" } });
    await readForPublication(result);
    let pending!: Promise<void>;
    act(() => { pending = result.current.publishReport(); });
    const input = api.publishFinancialReport.mock.calls[0][2];
    rerender({ scope: "session-b" });
    await act(async () => { resolve(publicationReceipt(input)); await pending; });
    expect(result.current.publishedReport).toBeNull();
    expect(result.current.publicationState).toBe("IDLE");
    expect(api.getPublishedFinancialReport).not.toHaveBeenCalled();
  });

  it("does not query or publish without a private authorized scope", async () => {
    const api = publicationApi();
    const { result } = renderHook(() => useFinancialDraft(api, vi.fn(), "case-1", ""));
    await act(async () => { await result.current.publishReport(); await result.current.loadPublishedReport(); });
    expect(api.publishFinancialReport).not.toHaveBeenCalled();
    expect(api.getPublishedFinancialReport).not.toHaveBeenCalled();
  });

  it("masks a late published read after the session context is revoked", async () => {
    const api = publicationApi();
    let resolve!: (value: PublishedFinancialReport) => void;
    api.getPublishedFinancialReport.mockImplementationOnce(() => new Promise((r) => { resolve = r; }));
    const { result, rerender } = renderHook(({ scope }) => useFinancialDraft(api, vi.fn(), "case-1", scope), { initialProps: { scope: "session-a" } });
    await readForPublication(result);
    let pending!: Promise<void>;
    act(() => { pending = result.current.publishReport(); });
    await act(async () => { await Promise.resolve(); });
    expect(result.current.publicationState).toBe("CONFIRMED");
    rerender({ scope: "" });
    expect(result.current.publicationState).toBe("IDLE");
    await act(async () => { resolve(published); await pending; });
    expect(result.current.publishedReport).toBeNull();
  });

  it("sends only one publication on a double click", async () => {
    const api = publicationApi();
    let resolve!: (value: FinancialReportPublicationReceipt) => void;
    api.publishFinancialReport.mockImplementationOnce(() => new Promise((r) => { resolve = r; }));
    const { result } = renderDraftHook(api, vi.fn());
    await readForPublication(result);
    let pending!: Promise<void>;
    act(() => { pending = result.current.publishReport(); void result.current.publishReport(); });
    expect(api.publishFinancialReport).toHaveBeenCalledOnce();
    await act(async () => { resolve(publicationReceipt(api.publishFinancialReport.mock.calls[0][2])); await pending; });
    expect(result.current.publicationState).toBe("CONFIRMED");
  });

  it("requires a fresh draft read after a definitive revision conflict", async () => {
    const api = publicationApi();
    api.publishFinancialReport.mockRejectedValueOnce({ status: 409, detail: "VERSION_CONFLICT" });
    const { result } = renderDraftHook(api, vi.fn());
    await readForPublication(result);
    await act(async () => result.current.publishReport());
    expect(result.current.publicationState).toBe("REJECTED");
    expect(result.current.draft).toBeNull();
    await act(async () => result.current.publishReport());
    expect(api.publishFinancialReport).toHaveBeenCalledOnce();
    api.getDraft.mockResolvedValueOnce(draft(4));
    await act(async () => result.current.loadDraft());
    api.getPublishedFinancialReport.mockResolvedValueOnce({ ...published, aggregate_revision: 5 });
    await act(async () => result.current.publishReport());
    expect(api.publishFinancialReport.mock.calls[1][2].expected_revision).toBe(4);
    expect(api.publishFinancialReport.mock.calls[1][2].idempotency_key).not.toBe(api.publishFinancialReport.mock.calls[0][2].idempotency_key);
    expect(result.current.publicationState).toBe("CONFIRMED");
  });

  it("keeps an ambiguous idempotency conflict as UNKNOWN with the same intent", async () => {
    const api = publicationApi();
    api.publishFinancialReport.mockRejectedValueOnce({ status: 409, detail: "IDEMPOTENCY_CONFLICT" });
    const { result } = renderDraftHook(api, vi.fn());
    await readForPublication(result);
    await act(async () => result.current.publishReport());
    expect(result.current.publicationState).toBe("UNKNOWN");
    await act(async () => result.current.publishReport());
    expect(api.publishFinancialReport.mock.calls[0]).toEqual(api.publishFinancialReport.mock.calls[1]);
  });

  it("does not accept a receipt for another source or read that source", async () => {
    const api = publicationApi();
    api.publishFinancialReport.mockImplementationOnce(async (_case, _report, input) => ({ ...publicationReceipt(input), aggregate_refs: [{ aggregate_type: "FinancialReportSnapshot", aggregate_id: "foreign", aggregate_revision: 3 }] }));
    const { result } = renderDraftHook(api, vi.fn());
    await readForPublication(result);
    await act(async () => result.current.publishReport());
    expect(result.current.publicationState).toBe("UNKNOWN");
    expect(result.current.publishedReport).toBeNull();
    expect(api.getPublishedFinancialReport).not.toHaveBeenCalled();
  });
});

function renderDraftHook(
  api: DraftApi,
  setMessage: Dispatch<SetStateAction<HookMessage | null>>,
  selectedCaseId = "case-1",
) {
  return renderHook(() => useFinancialDraft(withPublication(api), setMessage, selectedCaseId, "fixture-scope"));
}

describe("useFinancialDraft", () => {
  it("requires a selected case before creating a draft", async () => {
    const api = {
      createDraft: vi.fn(),
      getDraft: vi.fn(),
      addLine: vi.fn(),
    } satisfies DraftApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderDraftHook(api, setMessage, "");

    await act(async () => {
      await result.current.createDraft();
    });

    expect(api.createDraft).not.toHaveBeenCalled();
    expect(setMessage).toHaveBeenCalledWith({
      tone: "error",
      text: "Sélectionnez une affaire avant de créer un brouillon.",
    });
  });

  it("creates a draft, stores its report identifier and loads its projection", async () => {
    const api = {
      createDraft: vi.fn().mockResolvedValue(receipt()),
      getDraft: vi.fn().mockResolvedValue(draft()),
      addLine: vi.fn(),
    } satisfies DraftApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderDraftHook(api, setMessage);

    await act(async () => {
      await result.current.createDraft();
    });

    expect(api.createDraft).toHaveBeenCalledWith("case-1", expect.objectContaining({ command_id: expect.any(String), idempotency_key: expect.any(String), correlation_id: expect.any(String) }));
    expect(api.getDraft).toHaveBeenCalledWith("case-1", "report-1");
    expect(result.current.reportId).toBe("report-1");
    expect(result.current.draft?.aggregate_revision).toBe(2);
    expect(result.current.loadingDraft).toBe(false);
    expect(setMessage).toHaveBeenLastCalledWith({
      tone: "success",
      text: "Nouveau brouillon créé.",
    });
  });

  it("rejects a draft read without a report identifier", async () => {
    const api = {
      createDraft: vi.fn(),
      getDraft: vi.fn(),
      addLine: vi.fn(),
    } satisfies DraftApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderDraftHook(api, setMessage);

    await act(async () => {
      await result.current.loadDraft();
    });

    expect(api.getDraft).not.toHaveBeenCalled();
    expect(setMessage).toHaveBeenCalledWith({
      tone: "error",
      text: "Sélectionnez une affaire et renseignez l’identifiant du brouillon.",
    });
  });

  it("rejects non-integer cent amounts before calling the API", async () => {
    const api = {
      createDraft: vi.fn(),
      getDraft: vi.fn().mockResolvedValue(draft()),
      addLine: vi.fn(),
    } satisfies DraftApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderDraftHook(api, setMessage);

    act(() => {
      result.current.setReportId("report-1");
      result.current.setLineForm((current) => ({ ...current, amount_minor: "12.5", label: "Étude" }));
    });
    await act(async () => {
      await result.current.loadDraft();
    });
    await act(async () => {
      await result.current.submitLine({ preventDefault: vi.fn() } as unknown as FormEvent<HTMLFormElement>);
    });

    expect(api.addLine).not.toHaveBeenCalled();
    expect(setMessage).toHaveBeenLastCalledWith({
      tone: "error",
      text: "Le montant doit être exprimé en centimes entiers.",
    });
  });

  it.each(["", "   ", "9007199254740993"])("never converts an absent or unsafe amount %j into a declared amount", async (amount_minor) => {
    const api = { createDraft: vi.fn(), getDraft: vi.fn().mockResolvedValue(draft()), addLine: vi.fn() } satisfies DraftApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderDraftHook(api, setMessage);
    act(() => { result.current.setReportId("report-1"); result.current.setLineForm((value) => ({ ...value, label: "Synthétique", amount_minor })); });
    await act(async () => result.current.loadDraft());
    await act(async () => result.current.submitLine({ preventDefault: vi.fn() } as unknown as FormEvent<HTMLFormElement>));
    expect(api.addLine).not.toHaveBeenCalled();
  });

  it("adds a line with the current optimistic revision and reloads the draft", async () => {
    const api = {
      createDraft: vi.fn(),
      getDraft: vi.fn().mockResolvedValueOnce(draft()).mockResolvedValueOnce(draft(3)),
      addLine: vi.fn().mockResolvedValue(receipt()),
    } satisfies DraftApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderDraftHook(api, setMessage);

    act(() => {
      result.current.setReportId("report-1");
    });
    await act(async () => {
      await result.current.loadDraft();
    });
    act(() => {
      result.current.setLineForm((current) => ({
        ...current,
        label: "Étude technique",
        quantity_decimal: "2",
        unit: "jour",
        amount_minor: "125000",
      }));
    });
    await act(async () => {
      await result.current.submitLine({ preventDefault: vi.fn() } as unknown as FormEvent<HTMLFormElement>);
    });

    expect(api.addLine).toHaveBeenCalledWith("case-1", "report-1", expect.objectContaining({
      category: "SALES",
      label: "Étude technique",
      quantity_decimal: "2",
      unit: "jour",
      amount_minor: 125000,
      expected_revision: 2,
    }));
    expect(api.getDraft).toHaveBeenCalledTimes(2);
    expect(result.current.draft?.aggregate_revision).toBe(3);
    expect(result.current.lineForm.label).toBe("");
    expect(result.current.lineForm.amount_minor).toBe("");
    expect(setMessage).toHaveBeenCalledWith({
      tone: "success",
      text: "Ligne ajoutée au brouillon.",
    });
  });

  it("does not read or write financial data without a permitted context", async () => {
    const api = { createDraft: vi.fn(), getDraft: vi.fn(), addLine: vi.fn() } satisfies DraftApi;
    const { result } = renderHook(() => useFinancialDraft(withPublication(api), vi.fn(), "case-1", ""));
    act(() => result.current.setReportId("report-1"));
    await act(async () => { await result.current.createDraft(); await result.current.loadDraft(); });
    expect(api.createDraft).not.toHaveBeenCalled();
    expect(api.getDraft).not.toHaveBeenCalled();
  });

  it("masks a settled draft and ignores a pending private read after context changes", async () => {
    let finish!: (value: DraftReport) => void;
    const api = { createDraft: vi.fn(), getDraft: vi.fn().mockResolvedValueOnce(draft()).mockReturnValueOnce(new Promise<DraftReport>((resolve) => { finish = resolve; })), addLine: vi.fn() } satisfies DraftApi;
    const { result, rerender } = renderHook(({ scope }) => useFinancialDraft(withPublication(api), vi.fn(), "case-1", scope), { initialProps: { scope: "tenant-a-session" } });
    act(() => result.current.setReportId("report-1"));
    await act(async () => result.current.loadDraft());
    let pending!: Promise<void>;
    act(() => { pending = result.current.loadDraft(); });
    rerender({ scope: "tenant-b-session" });
    expect(result.current.draft).toBeNull();
    expect(result.current.reportId).toBe("");
    await act(async () => { finish(draft()); await pending; });
    expect(result.current.draft).toBeNull();
  });

  it("preserves an explicitly declared zero amount", async () => {
    const api = { createDraft: vi.fn(), getDraft: vi.fn().mockResolvedValue(draft()), addLine: vi.fn().mockResolvedValue(receipt()) } satisfies DraftApi;
    const { result } = renderDraftHook(api, vi.fn());
    act(() => { result.current.setReportId("report-1"); result.current.setLineForm((value) => ({ ...value, amount_minor: "0", label: "Zéro déclaré" })); });
    await act(async () => result.current.loadDraft());
    await act(async () => result.current.submitLine({ preventDefault: vi.fn() } as unknown as FormEvent<HTMLFormElement>));
    expect(api.addLine.mock.calls[0][2].amount_minor).toBe(0);
  });

  it("retries an unknown line result with the same intent after server read-back", async () => {
    const api = { createDraft: vi.fn(), getDraft: vi.fn().mockResolvedValueOnce(draft(2)).mockResolvedValue(draft(3)), addLine: vi.fn().mockRejectedValueOnce(new Error("unknown result")).mockResolvedValueOnce(receipt(true)) } satisfies DraftApi;
    const { result } = renderDraftHook(api, vi.fn());
    act(() => { result.current.setReportId("report-1"); result.current.setLineForm((value) => ({ ...value, amount_minor: "125000", label: "Même intention" })); });
    await act(async () => result.current.loadDraft());
    const event = { preventDefault: vi.fn() } as unknown as FormEvent<HTMLFormElement>;
    await act(async () => result.current.submitLine(event));
    await act(async () => result.current.loadDraft());
    await act(async () => result.current.submitLine(event));
    expect(api.addLine.mock.calls[1]).toEqual(api.addLine.mock.calls[0]);
    expect(api.addLine.mock.calls[0][2].command_id).toEqual(expect.any(String));
  });

  it("preserves draft creation identity after a lost acknowledgement", async () => {
    const api = { createDraft: vi.fn().mockRejectedValueOnce(new Error("unknown result")).mockResolvedValueOnce(receipt(true)), getDraft: vi.fn().mockResolvedValue(draft()), addLine: vi.fn() } satisfies DraftApi;
    const { result } = renderDraftHook(api, vi.fn());
    await act(async () => result.current.createDraft());
    await act(async () => result.current.createDraft());
    expect(api.createDraft.mock.calls[1]).toEqual(api.createDraft.mock.calls[0]);
    expect(result.current.draft?.report_id).toBe("report-1");
  });

  it("blocks a double click while a financial line write is pending", async () => {
    let acknowledge!: (value: CommandReceipt) => void;
    const api = { createDraft: vi.fn(), getDraft: vi.fn().mockResolvedValue(draft()), addLine: vi.fn().mockReturnValue(new Promise<CommandReceipt>((resolve) => { acknowledge = resolve; })) } satisfies DraftApi;
    const { result } = renderDraftHook(api, vi.fn());
    act(() => { result.current.setReportId("report-1"); result.current.setLineForm((value) => ({ ...value, label: "Synthétique", amount_minor: "0" })); });
    await act(async () => result.current.loadDraft());
    const event = { preventDefault: vi.fn() } as unknown as FormEvent<HTMLFormElement>;
    let pending!: Promise<void>;
    act(() => { pending = result.current.submitLine(event); void result.current.submitLine(event); });
    expect(api.addLine).toHaveBeenCalledTimes(1);
    await act(async () => { acknowledge(receipt()); await pending; });
  });
});
