import type { ComponentProps } from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { PricingImportBatchRead, PricingScenario } from "../../shared/types";
import { initialScenarioForm } from "./usePricingScenarios";
import { PricingPanel } from "./PricingPanel";

type PanelProps = ComponentProps<typeof PricingPanel>;

const preview: PricingImportBatchRead = {
  batch_id: "batch-1",
  case_id: "case-1",
  document_kind: "BPU",
  state: "PREVIEWED",
  aggregate_revision: 1,
  row_count: 1,
  valid_row_count: 1,
  error_count: 0,
  total_minor: 1500,
  rows: [
    {
      row_number: 2,
      code: "A-01",
      designation: "Terrassement",
      unit: "m2",
      quantity_decimal: "1",
      unit_price_minor: 1500,
      total_minor: 1500,
      errors: [],
    },
  ],
};

const scenario: PricingScenario = {
  scenario_id: "scenario-1",
  case_id: "case-1",
  scenario_key: "BASELINE",
  scenario_type: "BASELINE",
  version: 2,
  state: "SELECTED",
  assumptions: {},
  sales_total_minor: 100000,
  total_cost_minor: 70000,
  gross_margin_minor: 30000,
  gross_margin_rate_bps: 3000,
  source_snapshot_revision: 4,
  source_snapshot_id: "snapshot-1",
  source_basis_state: "DECLARED_COMPLETE",
  source_basis_reason: null,
  currency_code: "EUR",
};

function renderPanel(overrides: Partial<PanelProps> = {}) {
  const props: PanelProps = {
    scenarioTransition: { key: "", state: "IDLE", target: null, action: "selection", reason: "", error: null, receipt: null, projection: null, readingBack: false, locked: false, prepare: vi.fn(), setReason: vi.fn(), submit: vi.fn(), readBack: vi.fn(), reload: vi.fn() },
    scenarioCreation: { key: "", state: "IDLE", error: null, receipt: null, scenario: null, readingBack: false, source: null, sourceReason: "UNKNOWN · source absente", form: initialScenarioForm, locked: false, setForm: vi.fn(), submit: vi.fn(), readBack: vi.fn(), reset: vi.fn() },
    scenarios: [],
    formatMoney: (minor) => `${minor} EUR`,
    selectedCaseId: "case-1",
    reportId: "report-1",
    pricingImportBatchId: "batch-1",
    pricingImportBatchRevision: "1",
    pricingImportReportRevision: "0",
    pricingImportState: "IDLE",
    pricingImportUnknownAction: null,
    pricingImportPreview: null,
    pricingImportReloadState: "NOT_ATTEMPTED",
    pricingImportUploading: false,
    pricingImportLoading: false,
    pricingImportSubmitting: false,
    setPricingImportBatchId: vi.fn(),
    setPricingImportBatchRevision: vi.fn(),
    setPricingImportReportRevision: vi.fn(),
    onPreview: vi.fn(),
    onRetryPreview: vi.fn(),
    onRetryCommit: vi.fn(),
    onReload: vi.fn(),
    onCommit: vi.fn(),
    ...overrides,
  };
  return { ...render(<PricingPanel {...props} />), props };
}

describe("PricingPanel integration", () => {
  it("prepares an explicit selection without calling a mutation", () => {
    const { props, unmount } = renderPanel(); unmount();
    const prepare = vi.fn();
    renderPanel({ scenarios: [{ ...scenario, state: "DRAFT" }], scenarioTransition: { ...props.scenarioTransition, prepare } });
    fireEvent.click(screen.getByRole("button", { name: "Préparer la sélection" }));
    expect(prepare).toHaveBeenCalledWith("scenario-1", "selection");
    expect(props.scenarioTransition.submit).not.toHaveBeenCalled();
  });
  it("locks the UNKNOWN form but offers only the same retry", () => {
    const { props, unmount } = renderPanel(); unmount();
    const submit = vi.fn();
    renderPanel({ scenarioTransition: { ...props.scenarioTransition, target: scenario, reason: "HUMAN_REVIEW", state: "UNKNOWN", locked: true, submit } });
    expect(screen.getByLabelText("Motif codifié")).toBeDisabled();
    fireEvent.click(screen.getByRole("button", { name: "Réessayer le même acte" }));
    expect(submit).toHaveBeenCalledOnce();
  });
  it("keeps an absent historical source revision UNKNOWN during archive preparation", () => {
    const { props, unmount } = renderPanel(); unmount();
    renderPanel({ scenarioTransition: { ...props.scenarioTransition, action: "archive", target: { ...scenario, source_snapshot_id: undefined, source_snapshot_revision: 0, source_basis_state: "UNKNOWN" } } });
    expect(screen.getByRole("region", { name: "Acte humain sur scénario privé" })).toHaveTextContent("Source : UNKNOWN · révision UNKNOWN");
  });
  it("shows human creation only with an explicitly reread source", () => {
    renderPanel();
    expect(screen.getByRole("heading", { name: "Créer un scénario" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Créer ce scénario" })).toBeDisabled();
  });
  it("locks UNKNOWN parameters while offering only the identical retry", () => {
    const { props, unmount } = renderPanel();
    unmount();
    const submit = vi.fn();
    renderPanel({ scenarioCreation: { ...props.scenarioCreation, state: "UNKNOWN", sourceReason: null, locked: true, submit } });
    expect(screen.getByLabelText("Nom du scénario")).toBeDisabled();
    fireEvent.click(screen.getByRole("button", { name: "Réessayer la même création" }));
    expect(submit).toHaveBeenCalledOnce();
  });

  it("retains the receipt and only offers read recovery when projection is unavailable", () => {
    const { props, unmount } = renderPanel();
    unmount();
    const readBack = vi.fn();
    renderPanel({ scenarioCreation: { ...props.scenarioCreation, state: "CONFIRMED", sourceReason: null, locked: true, readBack, receipt: { status: "SUCCEEDED", command_id: "c", idempotency_key: "i", result_code: "PRICING_SCENARIO_CREATED", scenario_id: "exact-created-id", version: 1, event_ids: [], replayed: false } } });
    expect(screen.getByText("exact-created-id")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Créer ce scénario" })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Relire le scénario créé" }));
    expect(readBack).toHaveBeenCalledOnce();
  });

  it("renders private scenarios and commits from the patron panel", () => {
    const onCommit = vi.fn();
    renderPanel({ scenarios: [scenario], onCommit });

    expect(screen.getByText("BASELINE · v2")).toBeInTheDocument();
    expect(screen.getByText("30000 EUR")).toBeInTheDocument();
    expect(screen.getByText("Source snapshot-1 · révision 4")).toBeInTheDocument();
    expect(screen.getByText("Marge 30.00 % · SELECTED")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /commiter les lignes validées/i }));
    expect(onCommit).toHaveBeenCalledOnce();
  });

  it.each([undefined, "UNKNOWN"] as const)("keeps historical or unqualified scenarios unknown (%s)", (source_basis_state) => {
    renderPanel({ scenarios: [{ ...scenario, source_basis_state, source_basis_reason: "MISSING_BASE_CATEGORY" }] });
    expect(screen.getByText("Marge UNKNOWN · SELECTED")).toBeInTheDocument();
    expect(screen.queryByText("30000 EUR")).not.toBeInTheDocument();
  });

  it("uses the exact currency and keeps unsafe amounts unknown", () => {
    const formatMoney = vi.fn(() => "synthetic USD");
    renderPanel({ scenarios: [{ ...scenario, currency_code: "USD", gross_margin_minor: Number.MAX_SAFE_INTEGER + 1 }], formatMoney });
    expect(formatMoney).not.toHaveBeenCalled();
    expect(screen.queryByText("synthetic USD")).not.toBeInTheDocument();
  });

  it.each([
    ["selectedCaseId", { selectedCaseId: "" }],
    ["reportId", { reportId: "" }],
    ["batch", { pricingImportBatchId: "" }],
    ["submitting", { pricingImportSubmitting: true }],
  ])("disables commit when %s is unavailable", (_reason, override) => {
    renderPanel(override);

    const button = screen.getByRole("button", { name: /commiter les lignes validées|commit en cours/i });
    expect(button).toBeDisabled();
  });

  it("renders the persisted preview and exposes patron reload/upload actions", () => {
    const onPreview = vi.fn();
    const onReload = vi.fn();
    renderPanel({ pricingImportPreview: preview, onPreview, onReload });

    expect(screen.getByText(/BPU · PREVIEWED/)).toBeInTheDocument();
    expect(screen.getByText(/#2 · Terrassement/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /relire le batch/i }));
    expect(onReload).toHaveBeenCalledOnce();
    fireEvent.change(screen.getByLabelText(/fichier dpgf/i), {
      target: { files: [new File(["xlsx"], "pricing.xlsx")] },
    });
    expect(onPreview).toHaveBeenCalledOnce();
  });

  it("shows a processing label while the hook is submitting", () => {
    renderPanel({ pricingImportSubmitting: true });

    expect(screen.getByRole("button", { name: /commit en cours/i })).toBeDisabled();
  });

  it("keeps a confirmed commit visible when the reload failed", () => {
    renderPanel({ pricingImportState: "COMMITTED", pricingImportReloadState: "FAILED" });

    expect(screen.getByText("COMMITTED")).toBeInTheDocument();
    expect(screen.getByText("Commit confirmé. Rechargez le brouillon pour resynchroniser l’affichage.")).toBeInTheDocument();
  });
});

const proof = (globalThis as typeof globalThis & { __smartAoC08Proof?: { scenarios_complete: PricingScenario[]; scenarios_incomplete: PricingScenario[] } }).__smartAoC08Proof;
it.skipIf(!proof?.scenarios_complete)("renders exact PostgreSQL/HTTP source and preserves unknown history", () => {
  const complete = proof!.scenarios_complete[0];
  const first = renderPanel({ scenarios: [complete], selectedCaseId: complete.case_id });
  expect(screen.getByText(`Source ${complete.source_snapshot_id} · révision 6`)).toBeInTheDocument();
  expect(screen.getByText("33000 EUR")).toBeInTheDocument();
  expect(screen.getByText("Marge 32.99 % · DRAFT")).toBeInTheDocument();
  first.unmount();
  const history = proof!.scenarios_incomplete[0];
  renderPanel({ scenarios: [history], selectedCaseId: history.case_id });
  expect(screen.getByText("Marge UNKNOWN · DRAFT")).toBeInTheDocument();
  expect(screen.queryByText("0 EUR")).toBeNull();
});

it("distinguishes failed loading from an empty authorized list and offers retry", () => {
  const refresh = vi.fn();
  renderPanel({ scenariosError: "Lecture indisponible", onRefreshScenarios: refresh });
  expect(screen.getByRole("alert")).toHaveTextContent("Lecture indisponible");
  expect(screen.queryByText("Aucun scénario chargé")).toBeNull();
  fireEvent.click(screen.getByRole("button", { name: "Réessayer les scénarios" }));
  expect(refresh).toHaveBeenCalledOnce();
});
