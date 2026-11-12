import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { AssignedCase, DraftReport } from "../../shared/types";
import type { FinancialLineForm } from "./useFinancialDraft";
import { FinancialDraftPanel } from "./FinancialDraftPanel";

const cases: AssignedCase[] = [
  {
    case_id: "case-1",
    work_label: "Réhabilitation du groupe scolaire",
    case_lifecycle: "ACTIVE",
    commercial_stage: "REVIEW",
    dce_availability: "READY",
    consultation_id: null,
    applicable_dce_version_id: null,
  },
];

const draft: DraftReport = {
  report_id: "report-1",
  case_id: "case-1",
  status: "DRAFT",
  aggregate_revision: 2,
  currency_code: "EUR",
  calculated_at: "2026-08-20T12:00:00Z",
  ruleset_version: 1,
  summary: {
    sales_total_minor: 250000,
    direct_cost_total_minor: 100000,
    overhead_total_minor: 25000,
    subcontracting_total_minor: 0,
    contingency_total_minor: 0,
    gross_margin_minor: 125000,
    gross_margin_rate_bps: 5000,
    forecast_cashflow_minor: 125000,
  },
  lines: [
    {
      line_id: "line-1",
      category: "SALES",
      label: "Étude technique",
      quantity_decimal: "2",
      unit: "jour",
      amount_minor: 250000,
      currency_code: "EUR",
    },
  ],
};

const lineForm: FinancialLineForm = {
  category: "SALES",
  label: "",
  quantity_decimal: "1",
  unit: "forfait",
  amount_minor: "",
};
const httpProof = (globalThis as typeof globalThis & { __smartAoC08Proof?: { complete: DraftReport; incomplete: DraftReport } }).__smartAoC08Proof;

function renderPanel(
  overrides: Partial<React.ComponentProps<typeof FinancialDraftPanel>> = {},
) {
  const props: React.ComponentProps<typeof FinancialDraftPanel> = {
    cases,
    selectedCaseId: "case-1",
    setSelectedCaseId: vi.fn(),
    reportId: "report-1",
    setReportId: vi.fn(),
    draft: null,
    loadingDraft: false,
    lineForm,
    setLineForm: vi.fn(),
    summaryCards: [
      { label: "Ventes", value: "2 500 €", accent: "blue" },
      { label: "Marge brute", value: "1 250 €", accent: "green" },
    ],
    createDraft: vi.fn(),
    loadDraft: vi.fn(),
    publishedReport: null,
    publicationState: "IDLE",
    publicationRevision: null,
    publicationExpectedRevision: null,
    publicationError: null,
    publishedReadError: null,
    publicationLocked: false,
    publishReport: vi.fn(),
    loadPublishedReport: vi.fn(),
    submitLine: vi.fn(),
    formatMoney: (minor, currency) => `${minor} ${currency}`,
    formatDate: () => "20 août 2026",
    categoryLabel: (category) => (category === "SALES" ? "Ventes" : category),
    ...overrides,
  };
  return render(<FinancialDraftPanel {...props} />);
}

describe("FinancialDraftPanel", () => {
  it("requires a human click to publish and warns that this freezes the draft", () => {
    const publishReport = vi.fn();
    renderPanel({ draft, publishReport });
    expect(publishReport).not.toHaveBeenCalled();
    expect(screen.getByText(/La publication fige ce brouillon/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Publier et figer ce rapport" }));
    expect(publishReport).toHaveBeenCalledOnce();
  });

  it("renders a published source as immutable and keeps its incomplete margin UNKNOWN", () => {
    renderPanel({ publishedReport: { ...draft, lines: [], status: "PUBLISHED", aggregate_revision: 3, margin_calculation: { state: "UNKNOWN", basis: "DECLARED_BASE_CATEGORIES", missing_categories: ["CONTINGENCY"], basis_line_ids: [], total_cost_minor: null, gross_margin_minor: null, gross_margin_rate_bps: null, unknown_reason: "MISSING_BASE_CATEGORY", rate_unknown_reason: null } }, publicationState: "CONFIRMED", publicationRevision: 3, publicationLocked: true });
    expect(screen.getByText("PUBLISHED · Révision 3")).toBeInTheDocument();
    expect(screen.getByText("report-1 · révision 3")).toBeInTheDocument();
    expect(screen.getByText(/ne vaut pas éligibilité aux scénarios/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Publier et figer/ })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Ajouter/ })).not.toBeInTheDocument();
    expect(screen.getByText("UNKNOWN")).toBeInTheDocument();
    expect(screen.queryByText(/Ajoutez le premier/)).not.toBeInTheDocument();
    expect(screen.getByText("Aucune ligne enregistrée dans ce rapport publié.")).toBeInTheDocument();
  });

  it("offers a stable replay for UNKNOWN and no editable draft", () => {
    const publishReport = vi.fn();
    renderPanel({ publicationState: "UNKNOWN", publicationExpectedRevision: 2, publicationLocked: true, publishReport, publicationError: "Résultat de publication UNKNOWN." });
    fireEvent.click(screen.getByRole("button", { name: "Réessayer la même publication" }));
    expect(publishReport).toHaveBeenCalledOnce();
    expect(screen.queryByRole("button", { name: /Ajouter/ })).not.toBeInTheDocument();
  });

  it("retains confirmed publication metadata when read-back is unavailable and offers GET only", () => {
    const loadPublishedReport = vi.fn();
    renderPanel({ publicationState: "CONFIRMED", publicationRevision: 3, publicationLocked: true, publishedReadError: "Relecture indisponible.", loadPublishedReport });
    expect(screen.getByText(/Publication confirmée.*révision 3/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Relire le rapport publié" }));
    expect(loadPublishedReport).toHaveBeenCalledOnce();
    expect(screen.queryByRole("button", { name: /publication/ })).not.toBeInTheDocument();
  });

  it("shows the controlled empty state and delegates draft commands", () => {
    const createDraft = vi.fn();
    const loadDraft = vi.fn();
    renderPanel({ createDraft, loadDraft });

    expect(screen.getByText("Sélectionnez un brouillon pour commencer.")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Nouveau brouillon/ }));
    fireEvent.click(screen.getByRole("button", { name: /Lire le brouillon/ }));
    expect(createDraft).toHaveBeenCalledTimes(1);
    expect(loadDraft).toHaveBeenCalledTimes(1);
  });

  it("renders financial amounts only inside the patron draft projection", () => {
    renderPanel({ draft });

    expect(screen.getByText("Étude technique")).toBeInTheDocument();
    expect(screen.getByText("250000 EUR")).toBeInTheDocument();
    expect(screen.getByText("Les montants restent visibles uniquement dans cet espace patron.")).toBeInTheDocument();
    expect(screen.getByText("DRAFT · Révision 2")).toBeInTheDocument();
  });

  it("submits the line form through the hook boundary", () => {
    const submitLine = vi.fn((event: React.FormEvent<HTMLFormElement>) => event.preventDefault());
    renderPanel({ draft, submitLine });

    fireEvent.submit(screen.getByRole("button", { name: /Ajouter/ }).closest("form")!);

    expect(submitLine).toHaveBeenCalledTimes(1);
  });

  it("keeps a legacy or incomplete margin unknown instead of showing stored zero rates", () => {
    renderPanel({ draft });
    expect(screen.getByText("UNKNOWN")).toBeVisible();
    expect(screen.getByText("Taux UNKNOWN")).toBeVisible();
    expect(screen.queryByText("1 250 €")).toBeNull();
    expect(screen.queryByText(/50.0.*%/)).toBeNull();
  });

  it("renders the exact server-calculated amount and basis points", () => {
    renderPanel({ draft: { ...draft, margin_calculation: { state: "CALCULATED", basis: "DECLARED_BASE_CATEGORIES", missing_categories: [], basis_line_ids: ["line-1"], total_cost_minor: 67_003, gross_margin_minor: 33_000, gross_margin_rate_bps: 3299, unknown_reason: null, rate_unknown_reason: null } } });
    expect(screen.getByText("33000 EUR")).toBeVisible();
    expect(screen.getByText("32.99 % du chiffre d’affaires")).toBeVisible();
  });

  it("does not turn an undefined zero-sales rate into zero percent", () => {
    renderPanel({ draft: { ...draft, margin_calculation: { state: "CALCULATED", basis: "DECLARED_BASE_CATEGORIES", missing_categories: [], basis_line_ids: [], total_cost_minor: 10, gross_margin_minor: -10, gross_margin_rate_bps: null, unknown_reason: null, rate_unknown_reason: "ZERO_SALES" } } });
    expect(screen.getByText("-10 EUR")).toBeVisible();
    expect(screen.getByText("Taux UNKNOWN")).toBeVisible();
  });

  it("formats large safe integer basis points without losing the last hundredth", () => {
    renderPanel({ draft: { ...draft, margin_calculation: { state: "CALCULATED", basis: "DECLARED_BASE_CATEGORIES", missing_categories: [], basis_line_ids: [], total_cost_minor: 9007199254710001, gross_margin_minor: -9007199254700001, gross_margin_rate_bps: -9007199254700001, unknown_reason: null, rate_unknown_reason: null } } });
    expect(screen.getByText("-90071992547000.01 % du chiffre d’affaires")).toBeVisible();
  });

  it.skipIf(!httpProof)("renders the fresh synthetic PostgreSQL/HTTP complete and incomplete responses", () => {
    const first = renderPanel({ draft: httpProof!.complete, selectedCaseId: httpProof!.complete.case_id, reportId: httpProof!.complete.report_id });
    expect(screen.getByText("33000 EUR")).toBeVisible();
    expect(screen.getByText("32.99 % du chiffre d’affaires")).toBeVisible();
    first.unmount();
    renderPanel({ draft: httpProof!.incomplete, selectedCaseId: httpProof!.incomplete.case_id, reportId: httpProof!.incomplete.report_id });
    expect(screen.getByText("UNKNOWN")).toBeVisible();
    expect(screen.getByText("Taux UNKNOWN")).toBeVisible();
    expect(screen.getByText(/postes de base absents/)).toBeVisible();
  });
});
