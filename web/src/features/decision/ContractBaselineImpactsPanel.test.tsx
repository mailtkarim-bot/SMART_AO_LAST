import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import { ContractBaselineImpactsPanel } from "./ContractBaselineImpactsPanel";

test("affiche la chronologie sans action de mutation", () => {
  render(<ContractBaselineImpactsPanel caseId="case-1" items={[]} reviews={[{ review_id: "r1", proof_id: "p1", reviewer_id: "u1", reviewed_revision: 2, decision: "NEEDS_CLARIFICATION", rationale: "Rectificatif à vérifier" }]} loading={false} onRefresh={() => undefined} />);
  expect(screen.getByText("Rectificatif à vérifier")).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /accepter|rejeter/i })).not.toBeInTheDocument();
});
