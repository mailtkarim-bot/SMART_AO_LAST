import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { PricingScenario, PublishedFinancialReport, CreatePricingScenarioInput } from "../../shared/types";
import type { ApiClient } from "../../infrastructure/api";
import { usePricingScenarios } from "./usePricingScenarios";

const withCreate = (api: Pick<ApiClient, "listPricingScenarios">) => ({ createPricingScenario: vi.fn(), selectPricingScenario: vi.fn(), archivePricingScenario: vi.fn(), ...api });
const scenario = (caseId: string): PricingScenario => ({ scenario_id: "synthetic", case_id: caseId, scenario_key: "BASE", scenario_type: "BASE", version: 1, state: "DRAFT", assumptions: {}, sales_total_minor: 100, total_cost_minor: 0, gross_margin_minor: 100, gross_margin_rate_bps: 10000, source_snapshot_revision: 1 });
function pending<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((yes) => { resolve = yes; });
  return { promise, resolve };
}

const source: PublishedFinancialReport = {
  report_id: "source-1", case_id: "a", status: "PUBLISHED", aggregate_revision: 2, currency_code: "EUR", calculated_at: "2026-10-07T10:00:00Z", ruleset_version: 1,
  summary: { sales_total_minor: 10000, direct_cost_total_minor: 2000, overhead_total_minor: 0, subcontracting_total_minor: 0, contingency_total_minor: 0, gross_margin_minor: 0, gross_margin_rate_bps: 0, forecast_cashflow_minor: 0 },
  lines: ["SALES", "DIRECT_COST", "OVERHEAD", "SUBCONTRACTING", "CONTINGENCY"].map((category, i) => ({ line_id: `line-${i}`, category: category as PublishedFinancialReport["lines"][number]["category"], label: "Source synthétique", quantity_decimal: "1", unit: "forfait", amount_minor: i === 0 ? 10000 : i === 1 ? 2000 : 0, currency_code: "EUR" })),
  margin_calculation: { state: "CALCULATED", basis: "DECLARED_BASE_CATEGORIES", missing_categories: [], basis_line_ids: ["line-0", "line-1", "line-2", "line-3", "line-4"], total_cost_minor: 2000, gross_margin_minor: 8000, gross_margin_rate_bps: 8000, unknown_reason: null, rate_unknown_reason: null },
};

function ack(input: CreatePricingScenarioInput) {
  return { status: "SUCCEEDED" as const, command_id: input.command_id, idempotency_key: input.idempotency_key, result_code: "PRICING_SCENARIO_CREATED" as const, scenario_id: input.scenario_id, version: 1, event_ids: ["event-synthetic"], replayed: false };
}

function creationApi() {
  let rows: PricingScenario[] = [];
  return {
    selectPricingScenario: vi.fn(), archivePricingScenario: vi.fn(),
    listPricingScenarios: vi.fn().mockImplementation(async () => rows),
    createPricingScenario: vi.fn().mockImplementation(async (_caseId: string, input: CreatePricingScenarioInput) => {
      rows = [{ ...scenario("a"), scenario_id: input.scenario_id, scenario_key: input.scenario_key, scenario_type: input.scenario_type, assumptions: Object.fromEntries(Object.entries(input.assumptions).reverse()), source_snapshot_id: input.source_snapshot_id, source_snapshot_revision: 2, source_basis_state: "DECLARED_COMPLETE", source_basis_reason: null, currency_code: "EUR", penalty_reserve_minor: input.penalty_reserve_minor, retention_reserve_minor: input.retention_reserve_minor, guarantee_reserve_minor: input.guarantee_reserve_minor, floor_margin_rate_bps: input.floor_margin_rate_bps, target_margin_rate_bps: input.target_margin_rate_bps }];
      return ack(input);
    }),
  };
}

async function fillCreation(result: { current: ReturnType<typeof usePricingScenarios> }) {
  await waitFor(() => expect(result.current.loading).toBe(false));
  act(() => result.current.creation.setForm({ ...result.current.creation.form, scenario_key: "Synthétique", assumptions: "Hypothèse saisie par le Patron." }));
}

describe("human scenario creation", () => {
  it("uses the exact published source and reads back a DRAFT without automatic selection", async () => {
    const api = creationApi();
    const { result } = renderHook(() => usePricingScenarios(api, "a", "private", source));
    await fillCreation(result);
    expect(api.createPricingScenario).not.toHaveBeenCalled();
    await act(async () => result.current.creation.submit());
    const input = api.createPricingScenario.mock.calls[0][1];
    expect(input.source_snapshot_id).toBe(source.report_id);
    expect(input.assumptions).toEqual({ note: "Hypothèse saisie par le Patron.", sales_adjustment_bps: 0, cost_adjustment_bps: 0 });
    expect(result.current.creation.state).toBe("CONFIRMED");
    expect(result.current.creation.scenario?.source_snapshot_revision).toBe(2);
    expect(result.current.creation.scenario?.state).toBe("DRAFT");
  });

  it.each([null, { ...source, case_id: "foreign" }, { ...source, margin_calculation: { ...source.margin_calculation, state: "UNKNOWN" as const } }, { ...source, margin_calculation: { ...source.margin_calculation, gross_margin_rate_bps: null } }])("does not send a creation without a qualified private source", async (value) => {
    const api = creationApi();
    const { result } = renderHook(() => usePricingScenarios(api, "a", "private", value));
    await fillCreation(result);
    await act(async () => result.current.creation.submit());
    expect(api.createPricingScenario).not.toHaveBeenCalled();
    expect(result.current.creation.sourceReason).toBeTruthy();
  });

  it.each(["1.5", "1e2", "-5001", "9007199254740992"])("rejects an invalid integer adjustment %s", async (value) => {
    const api = creationApi();
    const { result } = renderHook(() => usePricingScenarios(api, "a", "private", source));
    await fillCreation(result);
    act(() => result.current.creation.setForm({ ...result.current.creation.form, sales_adjustment_bps: value }));
    await act(async () => result.current.creation.submit());
    expect(api.createPricingScenario).not.toHaveBeenCalled();
    expect(result.current.creation.error).toBeTruthy();
  });

  it("freezes parameters and identities after UNKNOWN and replays the same intention", async () => {
    const api = creationApi();
    api.createPricingScenario.mockRejectedValueOnce({ status: 503 });
    const { result } = renderHook(() => usePricingScenarios(api, "a", "private", source));
    await fillCreation(result);
    await act(async () => result.current.creation.submit());
    expect(result.current.creation.state).toBe("UNKNOWN");
    expect(result.current.creation.locked).toBe(true);
    act(() => result.current.creation.setForm({ ...result.current.creation.form, scenario_key: "Changed" }));
    await act(async () => result.current.creation.submit());
    expect(api.createPricingScenario.mock.calls[0]).toEqual(api.createPricingScenario.mock.calls[1]);
    expect(result.current.creation.scenario?.scenario_key).toBe("Synthétique");
  });

  it("retains a confirmed receipt on failed GET and recovery only reads", async () => {
    const api = creationApi();
    const { result } = renderHook(() => usePricingScenarios(api, "a", "private", source));
    await fillCreation(result);
    api.listPricingScenarios.mockRejectedValueOnce({ status: 503 });
    await act(async () => result.current.creation.submit());
    expect(result.current.creation.state).toBe("CONFIRMED");
    expect(result.current.creation.scenario).toBeNull();
    await act(async () => result.current.creation.readBack());
    expect(api.createPricingScenario).toHaveBeenCalledOnce();
    expect(result.current.creation.scenario?.source_snapshot_id).toBe(source.report_id);
  });

  it("does not reveal a discordant read-back after creation", async () => {
    const api = creationApi();
    const { result } = renderHook(() => usePricingScenarios(api, "a", "private", source));
    await fillCreation(result);
    api.listPricingScenarios.mockResolvedValueOnce([{ ...scenario("a"), source_snapshot_id: "foreign" }]);
    await act(async () => result.current.creation.submit());
    expect(result.current.creation.state).toBe("CONFIRMED");
    expect(result.current.creation.scenario).toBeNull();
  });

  it("sends one effect on double click and preserves the existing transition state", async () => {
    const api = creationApi();
    const wait = pending<ReturnType<typeof ack>>();
    api.createPricingScenario.mockImplementationOnce(() => wait.promise);
    const { result } = renderHook(() => usePricingScenarios(api, "a", "private", source));
    await fillCreation(result);
    let write!: Promise<void>;
    act(() => { write = result.current.creation.submit(); void result.current.creation.submit(); });
    expect(api.createPricingScenario).toHaveBeenCalledOnce();
    const input = api.createPricingScenario.mock.calls[0][1];
    await act(async () => { wait.resolve(ack(input)); await write; });
    expect(result.current.creation.receipt?.scenario_id).toBe(input.scenario_id);
    expect(result.current.creation.scenario).toBeNull();
  });

  it("keeps a definitive source refusal UNKNOWN and allows a new corrected intention", async () => {
    const api = creationApi();
    api.createPricingScenario.mockRejectedValueOnce({ status: 422, detail: "SCENARIO_SOURCE_UNKNOWN" });
    const { result } = renderHook(() => usePricingScenarios(api, "a", "private", source));
    await fillCreation(result);
    await act(async () => result.current.creation.submit());
    expect(result.current.creation.state).toBe("REJECTED");
    expect(result.current.creation.error).toContain("UNKNOWN");
    expect(result.current.creation.receipt).toBeNull();
    await act(async () => result.current.creation.submit());
    expect(api.createPricingScenario.mock.calls[0][1].command_id).not.toBe(api.createPricingScenario.mock.calls[1][1].command_id);
  });

  it("masks a late acknowledgment after the private scope is revoked", async () => {
    const api = creationApi();
    const wait = pending<ReturnType<typeof ack>>();
    api.createPricingScenario.mockImplementationOnce(() => wait.promise);
    const { result, rerender } = renderHook(({ scope }) => usePricingScenarios(api, "a", scope, source), { initialProps: { scope: "private" } });
    await fillCreation(result);
    let write!: Promise<void>;
    act(() => { write = result.current.creation.submit(); });
    const input = api.createPricingScenario.mock.calls[0][1];
    rerender({ scope: "" });
    await act(async () => { wait.resolve(ack(input)); await write; });
    expect(result.current.creation.source).toBeNull();
    expect(result.current.creation.receipt).toBeNull();
    expect(result.current.scenarios).toEqual([]);
  });
});

describe("private scenario reading", () => {
  it("does not read without an authorized scope and masks on logout", async () => {
    const api = { listPricingScenarios: vi.fn().mockResolvedValue([scenario("a")]) };
    const { result, rerender } = renderHook(({ scope }) => usePricingScenarios(withCreate(api), "a", scope), { initialProps: { scope: "" } });
    expect(api.listPricingScenarios).not.toHaveBeenCalled();
    rerender({ scope: "tenant-admin-session1" });
    await waitFor(() => expect(result.current.scenarios).toHaveLength(1));
    rerender({ scope: "" });
    expect(result.current.scenarios).toEqual([]);
  });

  it.each(["case", "scope"])("ignores late responses after changing %s", async (changed) => {
    const old = pending<PricingScenario[]>();
    const next = pending<PricingScenario[]>();
    const api = { listPricingScenarios: vi.fn().mockReturnValueOnce(old.promise).mockReturnValueOnce(next.promise) };
    const { result, rerender } = renderHook(({ caseId, scope }) => usePricingScenarios(withCreate(api), caseId, scope), { initialProps: { caseId: "a", scope: "session1" } });
    const caseId = changed === "case" ? "b" : "a";
    rerender({ caseId, scope: changed === "scope" ? "session2" : "session1" });
    expect(result.current.scenarios).toEqual([]);
    await act(async () => next.resolve([{ ...scenario(caseId), scenario_key: "CURRENT" }]));
    await act(async () => old.resolve([{ ...scenario("a"), scenario_key: "OLD" }]));
    expect(result.current.scenarios[0].scenario_key).toBe("CURRENT");
  });

  it("refuses an unexpected case and clears previous private data on failure", async () => {
    const api = { listPricingScenarios: vi.fn().mockResolvedValueOnce([scenario("a")]).mockResolvedValueOnce([scenario("foreign")]).mockRejectedValueOnce(new Error("private server detail")) };
    const { result } = renderHook(() => usePricingScenarios(withCreate(api), "a", "admin"));
    await waitFor(() => expect(result.current.scenarios).toHaveLength(1));
    await act(async () => { await result.current.refresh(); });
    expect(result.current.scenarios).toEqual([]);
    expect(result.current.error).toContain("indisponibles");
    await act(async () => { await result.current.refresh(); });
    expect(result.current.error).not.toContain("private server detail");
  });
});


function transitionApi(basis: "DECLARED_COMPLETE" | "UNKNOWN" = "DECLARED_COMPLETE") {
  let row: PricingScenario = { ...scenario("a"), source_snapshot_id: "source-1", source_snapshot_revision: 2, currency_code: "EUR", source_basis_state: basis };
  const change = (state: "SELECTED" | "ARCHIVED") => vi.fn().mockImplementation(async (_case: string, id: string, input: { command_id: string; idempotency_key: string }) => {
    row = { ...row, state, version: row.version + 1 };
    return { status: "SUCCEEDED", command_id: input.command_id, idempotency_key: input.idempotency_key, result_code: "PRICING_SCENARIO_TRANSITIONED", scenario_id: id, version: row.version, event_ids: ["event"], replayed: false };
  });
  return { setRow: (value: PricingScenario) => { row = value; }, createPricingScenario: vi.fn(), listPricingScenarios: vi.fn().mockImplementation(async () => [row]), selectPricingScenario: change("SELECTED"), archivePricingScenario: change("ARCHIVED") };
}
async function prepareTransition(result: { current: ReturnType<typeof usePricingScenarios> }, action: "selection" | "archive" = "selection") {
  await waitFor(() => expect(result.current.scenarios).toHaveLength(1));
  act(() => result.current.transition.prepare("synthetic", action));
  act(() => result.current.transition.setReason("HUMAN_REVIEW"));
}
describe("human scenario transitions", () => {
  it("prepares without writing, then confirms the captured version and source", async () => {
    const api = transitionApi();
    const { result } = renderHook(() => usePricingScenarios(api, "a", "private"));
    await prepareTransition(result);
    expect(api.selectPricingScenario).not.toHaveBeenCalled();
    expect(result.current.transition.target?.source_snapshot_revision).toBe(2);
    await act(async () => result.current.transition.submit());
    expect(api.selectPricingScenario.mock.calls[0].slice(0, 2)).toEqual(["a", "synthetic"]);
    expect(api.selectPricingScenario.mock.calls[0][2]).toMatchObject({ expected_version: 1, reason_code: "HUMAN_REVIEW" });
    expect(result.current.transition.projection?.state).toBe("SELECTED");
  });
  it("freezes the UNKNOWN intention and retries identical IDs, reason and version", async () => {
    const api = transitionApi();
    api.selectPricingScenario.mockRejectedValueOnce({ status: 503 });
    const { result } = renderHook(() => usePricingScenarios(api, "a", "private"));
    await prepareTransition(result);
    await act(async () => result.current.transition.submit());
    expect(result.current.transition.state).toBe("UNKNOWN");
    act(() => { result.current.transition.setReason("CHANGED"); result.current.transition.prepare("synthetic", "archive"); });
    await act(async () => result.current.transition.submit());
    expect(api.selectPricingScenario.mock.calls[0]).toEqual(api.selectPricingScenario.mock.calls[1]);
    expect(api.archivePricingScenario).not.toHaveBeenCalled();
  });
  it("retains the receipt and recovers by GET alone", async () => {
    const api = transitionApi();
    const { result } = renderHook(() => usePricingScenarios(api, "a", "private"));
    await prepareTransition(result);
    api.listPricingScenarios.mockRejectedValueOnce(new Error("private failure"));
    await act(async () => result.current.transition.submit());
    expect(result.current.transition.receipt?.version).toBe(2);
    expect(result.current.transition.projection).toBeNull();
    await act(async () => result.current.transition.readBack());
    expect(api.selectPricingScenario).toHaveBeenCalledOnce();
    expect(result.current.transition.projection?.version).toBe(2);
  });
  it("requires GET and a new human intention after VERSION_CONFLICT", async () => {
    const api = transitionApi();
    api.selectPricingScenario.mockRejectedValueOnce({ status: 409, detail: "VERSION_CONFLICT" });
    const { result } = renderHook(() => usePricingScenarios(api, "a", "private"));
    await prepareTransition(result);
    await act(async () => result.current.transition.submit());
    expect(result.current.transition.state).toBe("CONFLICT");
    await act(async () => result.current.transition.submit());
    expect(api.selectPricingScenario).toHaveBeenCalledOnce();
    api.setRow({ ...scenario("a"), state: "SELECTED", version: 2, source_snapshot_id: "source-1", source_snapshot_revision: 2, currency_code: "EUR", source_basis_state: "DECLARED_COMPLETE" });
    await act(async () => result.current.transition.reload());
    await prepareTransition(result, "archive");
    await act(async () => result.current.transition.submit());
    expect(api.archivePricingScenario.mock.calls[0][2].expected_version).toBe(2);
    expect(result.current.transition.state).toBe("CONFIRMED");
    expect(result.current.transition.projection?.version).toBe(3);
    expect(api.archivePricingScenario.mock.calls[0][2].command_id).not.toBe(api.selectPricingScenario.mock.calls[0][2].command_id);
  });
  it("keeps history UNKNOWN on explicit archive and refuses selection", async () => {
    const api = transitionApi("UNKNOWN");
    const { result } = renderHook(() => usePricingScenarios(api, "a", "private"));
    await prepareTransition(result);
    expect(result.current.transition.target).toBeNull();
    await prepareTransition(result, "archive");
    await act(async () => result.current.transition.submit());
    expect(api.selectPricingScenario).not.toHaveBeenCalled();
    expect(result.current.transition.projection?.source_basis_state).toBe("UNKNOWN");
  });
  it("refuses an invalid motif without making a command", async () => {
    const api = transitionApi();
    const { result } = renderHook(() => usePricingScenarios(api, "a", "private"));
    await prepareTransition(result);
    act(() => result.current.transition.setReason("free text"));
    await act(async () => result.current.transition.submit());
    expect(api.selectPricingScenario).not.toHaveBeenCalled();
  });
  it("rejects a discordant receipt as UNKNOWN without reading or inventing confirmation", async () => {
    const api = transitionApi();
    const { result } = renderHook(() => usePricingScenarios(api, "a", "private"));
    await prepareTransition(result);
    api.selectPricingScenario.mockResolvedValueOnce({ status: "SUCCEEDED", scenario_id: "foreign", version: 2 });
    await act(async () => result.current.transition.submit());
    expect(result.current.transition.state).toBe("UNKNOWN");
    expect(result.current.transition.receipt).toBeNull();
    expect(api.listPricingScenarios).toHaveBeenCalledOnce();
  });
  it("retains a receipt when read-back has another source revision", async () => {
    const api = transitionApi();
    const { result } = renderHook(() => usePricingScenarios(api, "a", "private"));
    await prepareTransition(result);
    api.listPricingScenarios.mockResolvedValueOnce([{ ...scenario("a"), state: "SELECTED", version: 2, source_snapshot_id: "source-1", source_snapshot_revision: 3, currency_code: "EUR" }]);
    await act(async () => result.current.transition.submit());
    expect(result.current.transition.receipt?.version).toBe(2);
    expect(result.current.transition.projection).toBeNull();
  });
  it("blocks a double click synchronously", async () => {
    const api = transitionApi();
    const wait = pending<unknown>();
    api.selectPricingScenario.mockImplementationOnce(() => wait.promise);
    const { result } = renderHook(() => usePricingScenarios(api, "a", "private"));
    await prepareTransition(result);
    let write!: Promise<void>;
    act(() => { write = result.current.transition.submit(); void result.current.transition.submit(); });
    expect(api.selectPricingScenario).toHaveBeenCalledOnce();
    await act(async () => { wait.resolve({}); await write; });
  });
  it("ignores a late receipt after private scope revocation", async () => {
    const api = transitionApi();
    const wait = pending<unknown>();
    api.selectPricingScenario.mockImplementationOnce(() => wait.promise);
    const { result, rerender } = renderHook(({ scope }) => usePricingScenarios(api, "a", scope), { initialProps: { scope: "private" } });
    await prepareTransition(result);
    let write!: Promise<void>;
    act(() => { write = result.current.transition.submit(); });
    rerender({ scope: "" });
    await act(async () => { wait.resolve({}); await write; });
    expect(result.current.transition.receipt).toBeNull();
    expect(result.current.transition.target).toBeNull();
  });
});
