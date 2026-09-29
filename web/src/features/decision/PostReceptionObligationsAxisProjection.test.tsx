import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import type { PostReceptionObligation } from "../../shared/types";
import { PostReceptionObligationsAxisProjection } from "./PostReceptionObligationsAxisProjection";

const obligation: PostReceptionObligation = {
  obligation_id: "opr-1", case_id: "case-1", obligation_type: "DOE_DIUO", summary: "Remettre le DOE",
  origin_reception_act_id: null, origin_reception_summary: null, origin_reception_outcome: "UNKNOWN",
  source_refs: ["ccap://clause/12"], due_date: null, resource_note: null, cost_estimate_note: null,
  fulfillment_proof_refs: [], sanction_ref: "ccap://clause/18", status: "REVIEW_REQUIRED", revision: 0,
  latest_transition_id: null, latest_transition_actor_id: null, latest_transition_at: null,
  latest_transition_rationale: null, completion_proof_refs: [], actor_id: "patron-1", created_at: "2026-09-28T00:00:00Z",
};

test("projette les obligations sourcées et conserve les échéances et coûts inconnus", () => {
  render(<PostReceptionObligationsAxisProjection obligations={[obligation]} />);
  const projection = screen.getByLabelText("Carte d’Engagement axe 11 obligations post-réception");
  expect(projection).toHaveTextContent("PARTIAL");
  expect(projection).toHaveTextContent("REVIEW_REQUIRED");
  expect(projection).toHaveTextContent("ccap://clause/12");
  expect(projection).toHaveTextContent("Échéance : UNKNOWN · Coût : UNKNOWN");
});

test("ne présente pas une liste vide comme preuve d’absence d’obligation", () => {
  render(<PostReceptionObligationsAxisProjection obligations={[]} />);
  expect(screen.getByText(/n’établit pas l’absence d’obligation/)).toBeInTheDocument();
});
