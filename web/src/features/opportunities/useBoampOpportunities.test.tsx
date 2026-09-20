import type { Dispatch, SetStateAction } from "react";

import { act, renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ApiClient } from "../../infrastructure/api";
import type { BoampObservation } from "../../shared/types";
import { useBoampOpportunities } from "./useBoampOpportunities";

type HookMessage = { tone: "success" | "error" | "warning"; text: string };
type BoampApi = Pick<
  ApiClient,
  "listBoampObservations" | "qualifyBoampObservation" | "createCaseFromBoampObservation"
>;

const observation = (id = "observation-1"): BoampObservation => ({
  observation_id: id,
  source_notice_id: `BOAMP-${id}`,
  title: "Réhabilitation d’une école",
  observed_at: "2026-08-23T12:00:00Z",
  publication_date: "2026-08-20",
  response_deadline: "2026-09-15T12:00:00Z",
  department_codes: ["59"],
  market_types: ["TRAVAUX"],
  source_status: "EN_COURS",
  score_version: "BOAMP_PUBLIC_V1",
  score: 82,
  score_explanation: { keyword_hits: ["réhabilitation"] },
  fingerprint_sha256: "a".repeat(64),
  p0_state: "UNREVIEWED",
  p0_decision: null,
  p0_reason_code: null,
  p0_qualification_id: null,
  p0_decided_at: null,
  p1_state: "NOT_OPEN",
  p1_case_id: null,
  p1_opened_at: null,
  lot_scope_state: "UNKNOWN",
  lot_references: [],
  lot_scope_source: "BOAMP",
  deadline_state: "KNOWN",
  deadline_source: "BOAMP",
  deadline_source_timezone: null,
  deadline_normalized_timezone: "UTC",
  unknowns: [],
});

function renderBoampHook(
  api: BoampApi,
  setMessage: Dispatch<SetStateAction<HookMessage | null>>,
) {
  return renderHook(() => useBoampOpportunities(api as ApiClient, setMessage));
}

describe("useBoampOpportunities", () => {
  it("loads observations and selects the first item", async () => {
    const api = {
      listBoampObservations: vi.fn().mockResolvedValue({ observations: [observation()] }),
      qualifyBoampObservation: vi.fn(),
      createCaseFromBoampObservation: vi.fn(),
    } satisfies BoampApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderBoampHook(api, setMessage);

    await act(async () => {
      await result.current.refreshObservations();
    });

    expect(result.current.observations).toHaveLength(1);
    expect(result.current.selectedObservationId).toBe("observation-1");
    expect(result.current.qualificationForm.decision).toBe("QUALIFIED");
  });

  it("qualifies the selected observation and reports an idempotent replay", async () => {
    const api = {
      listBoampObservations: vi.fn().mockResolvedValue({ observations: [observation()] }),
      qualifyBoampObservation: vi.fn().mockResolvedValue({
        qualification_id: "qualification-1",
        event_id: "event-1",
        replayed: true,
      }),
      createCaseFromBoampObservation: vi.fn(),
    } satisfies BoampApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderBoampHook(api, setMessage);

    await act(async () => {
      await result.current.refreshObservations();
    });
    await act(async () => {
      await result.current.qualifySelected();
    });

    expect(api.qualifyBoampObservation).toHaveBeenCalledWith("observation-1", {
      decision: "QUALIFIED",
      reason_code: "RELEVANT_PUBLIC_SIGNAL",
    });
    expect(setMessage).toHaveBeenCalledWith({
      tone: "success",
      text: "Qualification déjà enregistrée : rejeu idempotent.",
    });
  });

  it("does not call the API without a selected observation", async () => {
    const api = {
      listBoampObservations: vi.fn().mockResolvedValue({ observations: [] }),
      qualifyBoampObservation: vi.fn(),
      createCaseFromBoampObservation: vi.fn(),
    } satisfies BoampApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderBoampHook(api, setMessage);

    await act(async () => {
      await result.current.qualifySelected();
    });

    expect(api.qualifyBoampObservation).not.toHaveBeenCalled();
    expect(setMessage).toHaveBeenCalledWith({
      tone: "warning",
      text: "Sélectionnez une opportunité BOAMP avant de qualifier.",
    });
  });

  it("reports a projection failure", async () => {
    const api = {
      listBoampObservations: vi.fn().mockRejectedValue(new Error("BOAMP unavailable")),
      qualifyBoampObservation: vi.fn(),
      createCaseFromBoampObservation: vi.fn(),
    } satisfies BoampApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderBoampHook(api, setMessage);

    await act(async () => {
      await result.current.refreshObservations();
    });

    expect(result.current.observations).toEqual([]);
    expect(setMessage).toHaveBeenCalledWith({ tone: "error", text: "BOAMP unavailable" });
  });

  it("creates a qualified case and reuses the same command after an unknown result", async () => {
    const createCaseFromBoampObservation = vi.fn()
      .mockRejectedValueOnce(new Error("résultat inconnu"))
      .mockResolvedValue({
        status: "SUCCEEDED",
        command_id: "command-1",
        idempotency_key: "idempotency-1",
        result_code: "CASE_CREATED",
        case_id: "case-1",
        version: 1,
        event_ids: ["event-1"],
        replayed: true,
      });
    const api = {
      listBoampObservations: vi.fn().mockResolvedValue({ observations: [observation()] }),
      qualifyBoampObservation: vi.fn().mockResolvedValue({
        qualification_id: "qualification-1",
        event_id: "event-1",
        replayed: false,
      }),
      createCaseFromBoampObservation,
    } satisfies BoampApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderBoampHook(api, setMessage);

    await act(async () => { await result.current.refreshObservations(); });
    await act(async () => { await result.current.qualifySelected(); });
    await act(async () => {
      await expect(result.current.createCaseFromSelected()).rejects.toThrow("résultat inconnu");
    });
    await act(async () => { await result.current.createCaseFromSelected(); });

    expect(createCaseFromBoampObservation).toHaveBeenCalledTimes(2);
    expect(createCaseFromBoampObservation.mock.calls[0]?.[0]).toBe("observation-1");
    expect(createCaseFromBoampObservation.mock.calls[0]?.[1]).toEqual(
      createCaseFromBoampObservation.mock.calls[1]?.[1],
    );
    expect(setMessage).toHaveBeenLastCalledWith({
      tone: "success",
      text: "Affaire BOAMP déjà créée : rejeu idempotent.",
    });
  });

  it("requires a qualified observation before conversion", async () => {
    const api = {
      listBoampObservations: vi.fn().mockResolvedValue({ observations: [observation()] }),
      qualifyBoampObservation: vi.fn(),
      createCaseFromBoampObservation: vi.fn(),
    } satisfies BoampApi;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<HookMessage | null>>;
    const { result } = renderBoampHook(api, setMessage);

    await act(async () => { await result.current.refreshObservations(); });
    await act(async () => { await result.current.createCaseFromSelected(); });

    expect(api.createCaseFromBoampObservation).not.toHaveBeenCalled();
    expect(setMessage).toHaveBeenLastCalledWith({
      tone: "warning",
      text: "Qualifiez l’opportunité BOAMP avant de créer une affaire.",
    });
  });
});
