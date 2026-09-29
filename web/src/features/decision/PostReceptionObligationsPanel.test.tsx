import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";
import { PostReceptionObligationsPanel } from "./PostReceptionObligationsPanel";

test("affiche une obligation sourcée en revue requise sans clôture automatique", () => {
  render(<PostReceptionObligationsPanel caseId="case1" obligations={[{
    obligation_id: "opr1", case_id: "case1", obligation_type: "DOE_DIUO", summary: "Remettre le DOE",
    origin_reception_act_id: null, origin_reception_summary: null, origin_reception_outcome: "UNKNOWN" as const,
    source_refs: ["ccap://clause/12"], due_date: "2027-03-31", resource_note: "Conducteur travaux",
    cost_estimate_note: null, fulfillment_proof_refs: ["document://doe"], sanction_ref: null,
    status: "REVIEW_REQUIRED", revision: 0, latest_transition_id: null, latest_transition_actor_id: null,
    latest_transition_at: null, latest_transition_rationale: null, completion_proof_refs: [],
    actor_id: "patron1", created_at: "2026-09-28T00:00:00Z",
  }]} />);
  expect(screen.getByText(/DOE_DIUO · Remettre le DOE/)).toBeInTheDocument();
  expect(screen.getByText("REVIEW_REQUIRED")).toBeInTheDocument();
  expect(screen.queryByRole("button")).not.toBeInTheDocument();
});

test("exige une preuve humaine pour terminer puis envoie la transition avec révision", async () => {
  const onTransition = vi.fn().mockResolvedValue(undefined);
  const obligation = {
    obligation_id: "opr2", case_id: "case1", obligation_type: "RESERVES_LIFTING" as const, summary: "Lever les réserves",
    origin_reception_act_id: null, origin_reception_summary: null, origin_reception_outcome: "UNKNOWN" as const,
    source_refs: ["ccap://clause/22"], due_date: null, resource_note: null, cost_estimate_note: null,
    fulfillment_proof_refs: [], sanction_ref: null, status: "IN_PROGRESS" as const, revision: 3,
    latest_transition_id: "tr3", latest_transition_actor_id: "patron1", latest_transition_at: "2026-09-28T00:00:00Z",
    latest_transition_rationale: "Intervention commencée", completion_proof_refs: [], actor_id: "patron1", created_at: "2026-09-28T00:00:00Z",
  };
  render(<PostReceptionObligationsPanel caseId="case1" obligations={[obligation]} onTransition={onTransition} />);
  fireEvent.click(screen.getByRole("button", { name: /marquer terminée/i }));
  expect(screen.getByRole("alert")).toHaveTextContent("référence de preuve est obligatoire");
  expect(onTransition).not.toHaveBeenCalled();
  fireEvent.change(screen.getByLabelText("Preuve de levée Lever les réserves"), { target: { value: "document://pv-levee" } });
  fireEvent.click(screen.getByRole("button", { name: /marquer terminée/i }));
  expect(await onTransition).toHaveBeenCalledOnce();
  const payload = onTransition.mock.calls[0][1] as Record<string, unknown>;
  expect(payload.resulting_status).toBe("COMPLETED");
  expect(payload.expected_revision).toBe(3);
  expect(payload.evidence_refs).toEqual(["document://pv-levee"]);
});

test("enregistre les champs connus sans inventer échéance ou coût", async () => {
  const onCreate = vi.fn().mockResolvedValue(undefined);
  render(<PostReceptionObligationsPanel caseId="case1" obligations={[]} onCreate={onCreate} />);
  fireEvent.change(screen.getByLabelText("Résumé de l’obligation"), { target: { value: "Lever les réserves" } });
  fireEvent.change(screen.getByLabelText("Source de l’obligation"), { target: { value: "ccap://clause/20" } });
  fireEvent.click(screen.getByRole("button", { name: /enregistrer l’obligation/i }));
  expect(await onCreate).toHaveBeenCalledOnce();
  const payload = onCreate.mock.calls[0][0] as Record<string, unknown>;
  expect(payload.status).toBeUndefined();
  expect(payload.due_date).toBeNull();
  expect(payload.cost_estimate_note).toBeNull();
});

test("relie une levée de réserves à une réception admissible de la même affaire", async () => {
  const onCreate = vi.fn().mockResolvedValue(undefined);
  const receptionActs = [{
    act_id: "receipt-1", case_id: "case-1", act_kind: "WORK_RECEPTION" as const,
    reception_outcome: "WITH_RESERVATIONS" as const, summary: "PV lot 2 avec réserves",
    source_refs: ["ccap://clause/24"], evidence_refs: ["document://pv"], declared_event_date: null,
    case_dce_version_id_at_recording: null, version_relation: "UNKNOWN" as const,
    contract_instrument_version_relation: "UNKNOWN" as const, contract_instrument_version_id: null,
    contract_instrument_version: null, actor_id: "patron", recorded_at: "2026-09-29T00:00:00Z",
  }, {
    act_id: "foreign-receipt", case_id: "case-other", act_kind: "WORK_RECEPTION" as const,
    reception_outcome: "WITH_RESERVATIONS" as const, summary: "PV autre affaire",
    source_refs: ["ccap://clause/24"], evidence_refs: ["document://foreign-pv"], declared_event_date: null,
    case_dce_version_id_at_recording: null, version_relation: "UNKNOWN" as const,
    contract_instrument_version_relation: "UNKNOWN" as const, contract_instrument_version_id: null,
    contract_instrument_version: null, actor_id: "patron", recorded_at: "2026-09-29T00:00:00Z",
  }];
  render(<PostReceptionObligationsPanel caseId="case-1" obligations={[]} receptionActs={receptionActs} onCreate={onCreate} />);
  fireEvent.change(screen.getByLabelText("Type d’obligation"), { target: { value: "RESERVES_LIFTING" } });
  fireEvent.change(screen.getByLabelText("Résumé de l’obligation"), { target: { value: "Lever la réserve du lot 2" } });
  fireEvent.change(screen.getByLabelText("Source de l’obligation"), { target: { value: "ccap://clause/24" } });
  fireEvent.click(screen.getByRole("button", { name: /enregistrer l’obligation/i }));
  expect(onCreate).not.toHaveBeenCalled();
  fireEvent.change(screen.getByLabelText("Acte de réception source"), { target: { value: "receipt-1" } });
  fireEvent.click(screen.getByRole("button", { name: /enregistrer l’obligation/i }));
  expect(await onCreate).toHaveBeenCalledOnce();
  expect(onCreate.mock.calls[0][0]).toMatchObject({ origin_reception_act_id: "receipt-1", obligation_type: "RESERVES_LIFTING" });
});

test("affiche UNKNOWN pour une ancienne levée sans acte source", () => {
  render(<PostReceptionObligationsPanel caseId="case-1" obligations={[{
    obligation_id: "old-reserve", case_id: "case-1", obligation_type: "RESERVES_LIFTING", summary: "Ancienne réserve",
    origin_reception_act_id: null, origin_reception_summary: null, origin_reception_outcome: "UNKNOWN",
    source_refs: ["ccap://clause/20"], due_date: null, resource_note: null, cost_estimate_note: null,
    fulfillment_proof_refs: [], sanction_ref: null, status: "REVIEW_REQUIRED", revision: 0,
    latest_transition_id: null, latest_transition_actor_id: null, latest_transition_at: null,
    latest_transition_rationale: null, completion_proof_refs: [], actor_id: "patron", created_at: "2026-09-29T00:00:00Z",
  }]} />);
  expect(screen.getByText(/UNKNOWN · obligation historique non reliée à un acte de réception/)).toBeInTheDocument();
});
