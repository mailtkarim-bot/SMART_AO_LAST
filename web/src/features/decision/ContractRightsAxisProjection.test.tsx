import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import type { PostReceptionObligation } from "../../shared/types";
import { ContractRightsAxisProjection } from "./ContractRightsAxisProjection";

const obligation: PostReceptionObligation = {
  obligation_id: "opr-1", case_id: "case-1", obligation_type: "DOE_DIUO", summary: "Remettre le DOE",
  origin_reception_act_id: null, origin_reception_summary: null, origin_reception_outcome: "UNKNOWN",
  source_refs: ["ccap://clause/12"], due_date: "2026-10-01", resource_note: null, cost_estimate_note: null,
  fulfillment_proof_refs: [], sanction_ref: null, status: "REVIEW_REQUIRED", revision: 0,
  latest_transition_id: null, latest_transition_actor_id: null, latest_transition_at: null,
  latest_transition_rationale: null, completion_proof_refs: [], actor_id: "patron-1", created_at: "2026-09-28T00:00:00Z",
};

test("sépare obligations de réception de la preuve d’acte et conserve les dates déclaratives", () => {
  render(<ContractRightsAxisProjection obligations={[obligation]} acts={[]} actsStatus="READY" />);
  const projection = screen.getByLabelText(/Carte d’Engagement axe 12/);
  expect(projection).toHaveTextContent("UNKNOWN · aucun acte enregistré ; cela ne prouve pas son absence.");
  expect(projection).toHaveTextContent("DOE_DIUO · Remettre le DOE");
  expect(projection).toHaveTextContent("2026-10-01 (déclarée, non recalculée)");
  expect(projection).toHaveTextContent("elles ne prouvent pas sa tenue");
  expect(projection).toHaveTextContent(/aucun délai, DGD tacite ou forclusion n’est calculé ni conclu/i);
});

test("distingue une lecture indisponible d’une absence d’acte", () => {
  render(<ContractRightsAxisProjection obligations={[]} acts={[]} actsStatus="UNAVAILABLE" />);
  expect(screen.getAllByText(/UNAVAILABLE · impossible de lire les actes/i)).toHaveLength(3);
  expect(screen.queryByText(/UNKNOWN · aucun acte enregistré/)).not.toBeInTheDocument();
});
