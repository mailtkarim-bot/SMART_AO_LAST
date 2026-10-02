import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { expect, test, vi } from "vitest";
import { ContractBaselineImpactsPanel } from "./ContractBaselineImpactsPanel";

test("affiche la chronologie et garde l’écriture hors accès délégué", () => {
  render(<ContractBaselineImpactsPanel caseId="case-1" items={[]} reviews={[{ review_id: "r1", proof_id: "p1", reviewer_id: "u1", reviewed_revision: 2, decision: "NEEDS_CLARIFICATION", rationale: "Rectificatif à vérifier" }]} requirements={[]} loading={false} canManage={false} onRefresh={() => undefined} onRecord={vi.fn()} />);
  expect(screen.getByText("Rectificatif à vérifier")).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /enregistrer pour revue/i })).not.toBeInTheDocument();
});

test("déclare un impact sur l’exigence confirmée et conserve les identifiants au retry", async () => {
  const onRecord = vi.fn().mockResolvedValueOnce(false).mockResolvedValueOnce(true);
  render(<ContractBaselineImpactsPanel caseId="case-1" items={[]} reviews={[]} requirements={[{ requirement_id: "req-1", confirmation_revision: 2, requirement_type: "CONTRACT_RISK_SIGNAL", directive_signal: "REQUIRED_SIGNAL", confirmation_outcome: "CONFIRMED", uncertainty_status: "SOURCE_SIGNAL_ONLY", document_family: "CCAP", source_locator_label: "CCAP · article 4" }]} loading={false} canManage onRefresh={() => undefined} onRecord={onRecord} />);
  fireEvent.change(screen.getByLabelText("Localisateur exact de la source baseline"), { target: { value: "CCAP · article 4 · page 12" } });
  fireEvent.change(screen.getByLabelText("Baseline déclarée"), { target: { value: "Délai de paiement déclaré" } });
  fireEvent.change(screen.getByLabelText("Impact déclaré, sans calcul automatique"), { target: { value: "Trésorerie à examiner" } });
  fireEvent.click(screen.getByRole("button", { name: "Enregistrer pour revue humaine" }));
  await waitFor(() => expect(onRecord).toHaveBeenCalledTimes(1));
  fireEvent.click(screen.getByRole("button", { name: "Enregistrer pour revue humaine" }));
  await waitFor(() => expect(onRecord).toHaveBeenCalledTimes(2));
  expect(onRecord.mock.calls[1][0]).toEqual(onRecord.mock.calls[0][0]);
  expect(onRecord.mock.calls[0][0]).toMatchObject({ dce_requirement_id: "req-1", dce_requirement_revision: 2 });
});
