import { render, screen, fireEvent } from "@testing-library/react";
import { expect, test, vi } from "vitest";
import { HandoverReviewForm } from "./HandoverReviewForm";
test("publishes only an explicit operational review and keeps the contract UNKNOWN", () => {
  const submit = vi.fn();
  render(<HandoverReviewForm contracts={[]} conditions={[]} expectedRevision={0} sourceContextSha={"b".repeat(64)} offerSha={"a".repeat(64)} disabled={false} onSubmit={submit} />);
  expect(screen.getByRole("button", {
    name: "Publier la revue et transmettre"
  })).toBeDisabled();
  fireEvent.change(screen.getByLabelText("Point opérationnel 1"), {
    target: {
      value: "Transport exclu de la fourniture."
    }
  });
  fireEvent.change(screen.getByLabelText("Justification de la revue"), {
    target: {
      value: "Revue des sources pour le conducteur."
    }
  });
  fireEvent.click(screen.getByLabelText(/Je confirme la publication opérationnelle/));
  fireEvent.click(screen.getByRole("button", {
    name: "Publier la revue et transmettre"
  }));
  expect(submit).toHaveBeenCalledWith(expect.objectContaining({
    contract_instrument_version_id: null,
    human_confirmed: true,
    points: [expect.objectContaining({
      statement: "Transport exclu de la fourniture.",
      difference_state: "UNKNOWN",
      responsible: null
    })]
  }));
});
