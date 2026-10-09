import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { CaseResolution, CaseResolutionItemKind } from "../../shared/types";
import { CaseResolutionPanel } from "./CaseResolutionPanel";

const kinds: CaseResolutionItemKind[] = ["REQUIREMENT", "INFORMATION_REQUEST", "TASK_BLOCKER", "CONTRADICTION", "RISK", "UNKNOWN", "CAPABILITY_GAP"];
const data = (items = kinds): CaseResolution => ({
  case_id: "case-a", work_label: "Affaire synthétique ALPHA", coverage: "PARTIAL", economic_coverage: null,
  items: items.map((kind) => ({ item_id: "shared-id", item_kind: kind, native_state: kind === "UNKNOWN" ? "UNKNOWN" : "REVIEW_REQUIRED", source_refs: [`fixture://${kind}`], next_action: "Vérifier dans la source", resolution_owner: null, due_at: null, impact: null })),
});

function panel(projection: CaseResolution | null = data(), overrides = {}) {
  return render(<CaseResolutionPanel caseId="case-a" projection={projection} loading={false} error={null} onRefresh={vi.fn()} {...overrides} />);
}

describe("CaseResolutionPanel", () => {
  it("keeps all seven natures and native states distinct, even with shared ids", () => {
    panel();
    for (const label of ["Exigences", "Demandes d’information", "Blocages de tâche", "Contradictions", "Risques", "Inconnus", "Écarts de capacité"]) {
      expect(screen.getByRole("heading", { name: label })).toBeVisible();
    }
    expect(screen.getAllByText("REVIEW_REQUIRED")).toHaveLength(6);
    expect(screen.getByText("UNKNOWN")).toBeVisible();
    expect(screen.getByText("Couverture partielle")).toBeVisible();
    expect(screen.getAllByRole("button")).toHaveLength(1);
    expect(screen.getAllByText("Responsable inconnu")).toHaveLength(7);
    expect(screen.getAllByText("Échéance inconnue")).toHaveLength(7);
  });

  it("shows returned provenance as text and ignores private economic coverage", () => {
    const projection = data(["UNKNOWN"]);
    projection.items[0].source_refs = ['<script>private()</script>', "fixture://source/1"];
    projection.items[0].impact = "Périmètre à vérifier";
    projection.economic_coverage = { assumptions: { state: "UNKNOWN", source_refs: [], note: "PRIVATE ECONOMIC NOTE" }, quote_validity: { state: "UNKNOWN", source_refs: [], note: "" }, capacity: { state: "UNKNOWN", source_refs: [], note: "" }, financing: { state: "UNKNOWN", source_refs: [], note: "" } };
    const view = panel(projection);
    fireEvent.click(screen.getByText("Sources et identifiant"));
    expect(screen.getByText('<script>private()</script>')).toBeInTheDocument();
    expect(view.container.querySelector("script")).toBeNull();
    expect(screen.getByText("Périmètre à vérifier")).toBeVisible();
    expect(screen.queryByText("PRIVATE ECONOMIC NOTE")).toBeNull();
  });

  it("keeps empty coverage PARTIAL without declaring the case resolved", () => {
    panel(data([]));
    expect(screen.getByText("Couverture partielle")).toBeVisible();
    expect(screen.getByText("Aucun point retourné dans le périmètre disponible")).toBeVisible();
    expect(screen.getByText(/ne vaut ni validation ni clôture/)).toBeVisible();
  });

  it("hides stale items during loading and errors, with a read-only retry", () => {
    const refresh = vi.fn();
    const view = panel(data(), { loading: true, onRefresh: refresh });
    expect(screen.queryByRole("heading", { name: "Risques" })).toBeNull();
    expect(screen.getByRole("button", { name: "Chargement…" })).toBeDisabled();
    view.rerender(<CaseResolutionPanel caseId="case-a" projection={data()} loading={false} error="Lecture indisponible" onRefresh={refresh} />);
    expect(screen.getByRole("alert")).toHaveTextContent("Lecture indisponible");
    expect(screen.queryByRole("heading", { name: "Risques" })).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Actualiser" }));
    expect(refresh).toHaveBeenCalledOnce();
  });

  it("does not display a projection belonging to another case", () => {
    panel({ ...data(), case_id: "foreign-case" });
    const region = screen.getByRole("region", { name: "À résoudre" });
    expect(within(region).queryByText("Affaire synthétique ALPHA")).toBeNull();
    expect(within(region).queryByRole("heading", { name: "Risques" })).toBeNull();
  });
});
