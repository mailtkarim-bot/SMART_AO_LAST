import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { expect, test, vi } from "vitest";
import type { CaseExecutionResults, RecordCaseOutcomeInput, RecordCaseOrderInput, RecordCaseP6ControlInput, RecordCaseP7ResultInput, RecordCaseRexInput } from "../../shared/types";
import { CaseOutcomePanel } from "./CaseOutcomePanel";

const empty: CaseExecutionResults = { case_id: "case-1", lot_references: ["01"], results: [] };

test("affiche explicitement UNKNOWN quand aucun résultat n'est enregistré pour le lot", () => {
  render(<CaseOutcomePanel caseId="case-1" canManage status="READY" data={empty} onRefresh={vi.fn()} onRecordOutcome={vi.fn()} />);
  expect(screen.getByText(/UNKNOWN · aucun résultat n’est enregistré pour ces lots/i)).toBeInTheDocument();
  expect(screen.getByRole("option", { name: "Lot 01" })).toBeInTheDocument();
  expect(screen.getByLabelText("Résultat déclaré du lot")).toHaveValue("UNKNOWN");
  expect(screen.queryByText(/Attribution déclarée \(WON\)/)).not.toBeInTheDocument();
});

test("préserve un résultat UNKNOWN enregistré avec son motif et n'ouvre aucune commande", () => {
  const unknown = {
    outcome_id: "out-unknown", lot_reference: "01", outcome: "UNKNOWN" as const,
    source_locator: null, reservations: [], unknown_reason: "Le retour du donneur d'ordre reste attendu.",
    actor_id: "patron-1", recorded_at: "2026-09-29T12:00:00Z",
    transmission: null, order: null, p6: null, p7: null,
  };
  render(<CaseOutcomePanel caseId="case-1" canManage status="READY" data={{ ...empty, results: [unknown] }} onRefresh={vi.fn()} onRecordOutcome={vi.fn()} />);
  expect(screen.getByRole("heading", { name: /Lot 01 · Résultat inconnu \(UNKNOWN\)/ })).toBeInTheDocument();
  expect(screen.getByText(/Le retour du donneur d'ordre reste attendu/)).toBeInTheDocument();
  expect(screen.getByText(/Commande non ouverte · le résultat est UNKNOWN/)).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /décision sur la commande/i })).not.toBeInTheDocument();
});

test("une lecture indisponible n'est pas transformée en liste vide ou état perdu", () => {
  render(<CaseOutcomePanel caseId="case-1" canManage status="UNAVAILABLE" data={null} onRefresh={vi.fn()} onRecordOutcome={vi.fn()} />);
  expect(screen.getByText(/UNAVAILABLE · lecture des résultats par lot impossible/i)).toBeInTheDocument();
  expect(screen.queryByText(/aucun résultat n’est enregistré/i)).not.toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /enregistrer/i })).not.toBeInTheDocument();
});

test("révèle commande, P6 puis P7 seulement après les actes serveurs précédents", async () => {
  const outcomes: RecordCaseOutcomeInput[] = [];
  const orders: RecordCaseOrderInput[] = [];
  const p6s: Array<{ orderId: string; input: RecordCaseP6ControlInput }> = [];
  const p7s: Array<{ p6Id: string; input: RecordCaseP7ResultInput }> = [];
  const onRecordOutcome = vi.fn(async (input: RecordCaseOutcomeInput) => { outcomes.push(input); });
  const onRecordOrder = vi.fn(async (input: RecordCaseOrderInput) => { orders.push(input); });
  const onRecordP6 = vi.fn(async (orderId: string, input: RecordCaseP6ControlInput) => { p6s.push({ orderId, input }); });
  const onRecordP7 = vi.fn(async (p6Id: string, input: RecordCaseP7ResultInput) => { p7s.push({ p6Id, input }); });
  const callbacks = { onRefresh: vi.fn(), onRecordOutcome, onRecordOrder, onRecordP6, onRecordP7 };
  const { rerender } = render(<CaseOutcomePanel caseId="case-1" canManage status="READY" data={empty} {...callbacks} />);

  fireEvent.change(screen.getByLabelText("Lot concerné"), { target: { value: "01" } });
  fireEvent.change(screen.getByLabelText("Résultat déclaré du lot"), { target: { value: "WON" } });
  fireEvent.change(screen.getByLabelText("Référence de preuve du résultat"), { target: { value: "notification://lot-01" } });
  fireEvent.click(screen.getByRole("button", { name: "Enregistrer le résultat par lot" }));
  await waitFor(() => expect(outcomes).toHaveLength(1));
  expect(outcomes[0]).toMatchObject({ case_id: "case-1", lot_reference: "01", outcome: "WON", source_locator: "notification://lot-01" });
  expect(screen.queryByRole("button", { name: /enregistrer la décision sur la commande/i })).not.toBeInTheDocument();

  const result = { outcome_id: outcomes[0].outcome_id, lot_reference: "01", outcome: "WON" as const, source_locator: "notification://lot-01", reservations: [], unknown_reason: null, recorded_at: "2026-09-29T12:00:00Z", actor_id: "patron-1", transmission: null, order: null, p6: null, p7: null };
  rerender(<CaseOutcomePanel caseId="case-1" canManage status="READY" data={{ ...empty, results: [result] }} {...callbacks} />);
  fireEvent.change(screen.getByLabelText("Décision Patron sur la commande"), { target: { value: "ACCEPTED" } });
  fireEvent.change(screen.getByLabelText("Motif de la commande"), { target: { value: "Commande rapprochée" } });
  fireEvent.click(screen.getByRole("button", { name: "Enregistrer la décision sur la commande" }));
  await waitFor(() => expect(orders).toHaveLength(1));
  expect(orders[0]).toMatchObject({ case_id: "case-1", outcome_id: outcomes[0].outcome_id, decision: "ACCEPTED" });
  expect(screen.queryByLabelText("Décision Patron P6")).not.toBeInTheDocument();

  const withOrder = { ...result, order: { order_id: orders[0].order_id, outcome_id: outcomes[0].outcome_id, decision: "ACCEPTED" as const, source_locator: "notification://lot-01", reservations: [], rationale: "Commande rapprochée", recorded_at: "2026-09-29T12:01:00Z", actor_id: "patron-1" } };
  rerender(<CaseOutcomePanel caseId="case-1" canManage status="READY" data={{ ...empty, results: [withOrder] }} {...callbacks} />);
  fireEvent.change(screen.getByLabelText("Décision Patron P6"), { target: { value: "APPROVED" } });
  fireEvent.change(screen.getByLabelText("Motif P6"), { target: { value: "Clarifications clôturées" } });
  fireEvent.click(screen.getByRole("button", { name: "Enregistrer la décision P6" }));
  await waitFor(() => expect(p6s).toHaveLength(1));
  expect(p6s[0].orderId).toBe(orders[0].order_id);
  expect(p6s[0].input).toMatchObject({ order_id: orders[0].order_id, decision: "APPROVED" });

  const withP6 = { ...withOrder, p6: { p6_control_id: p6s[0].input.p6_control_id, order_id: orders[0].order_id, decision: "APPROVED" as const, reservations: [], rationale: "Clarifications clôturées", recorded_at: "2026-09-29T12:02:00Z", actor_id: "patron-1" } };
  rerender(<CaseOutcomePanel caseId="case-1" canManage status="READY" data={{ ...empty, results: [withP6] }} {...callbacks} />);
  expect(screen.getByText(/P7 ne vaut pas ordre de service/i)).toBeInTheDocument();
  fireEvent.change(screen.getByLabelText("Résultat P7"), { target: { value: "UNKNOWN" } });
  fireEvent.change(screen.getByLabelText("Motif du résultat P7"), { target: { value: "Retour de chantier en attente" } });
  fireEvent.click(screen.getByRole("button", { name: "Enregistrer le résultat P7" }));
  await waitFor(() => expect(p7s).toHaveLength(1));
  expect(p7s[0]).toMatchObject({ p6Id: p6s[0].input.p6_control_id, input: { result: "UNKNOWN", reason: "Retour de chantier en attente", source_locator: null } });
});

test("un rejeu non confirmé réutilise la même intention idempotente", async () => {
  const intents: RecordCaseOutcomeInput[] = [];
  const onRecordOutcome = vi.fn(async (input: RecordCaseOutcomeInput) => {
    intents.push(input);
    if (intents.length === 1) throw new Error("network interruption");
  });
  render(<CaseOutcomePanel caseId="case-1" canManage status="READY" data={empty} onRefresh={vi.fn()} onRecordOutcome={onRecordOutcome} />);
  fireEvent.change(screen.getByLabelText("Lot concerné"), { target: { value: "01" } });
  fireEvent.change(screen.getByLabelText("Résultat déclaré du lot"), { target: { value: "UNKNOWN" } });
  fireEvent.change(screen.getByLabelText("Motif du résultat inconnu"), { target: { value: "Aucune notification disponible" } });
  fireEvent.click(screen.getByRole("button", { name: "Enregistrer le résultat par lot" }));
  expect(await screen.findByText(/résultat non confirmé/i)).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Réessayer le résultat par lot" }));
  await waitFor(() => expect(intents).toHaveLength(2));
  expect(intents[1]).toEqual(intents[0]);
});

test("un refus HTTP déterministe n'est ni affiché comme succès ni rejoué comme inconnu", async () => {
  const intents: RecordCaseOutcomeInput[] = [];
  const onRecordOutcome = vi.fn(async (input: RecordCaseOutcomeInput) => {
    intents.push(input);
    if (intents.length === 1) throw Object.assign(new Error("UNKNOWN_REASON_REQUIRED"), { status: 422 });
  });
  render(<CaseOutcomePanel caseId="case-1" canManage status="READY" data={empty} onRefresh={vi.fn()} onRecordOutcome={onRecordOutcome} />);
  fireEvent.change(screen.getByLabelText("Lot concerné"), { target: { value: "01" } });
  fireEvent.change(screen.getByLabelText("Motif du résultat inconnu"), { target: { value: "Motif revu" } });
  fireEvent.click(screen.getByRole("button", { name: "Enregistrer le résultat par lot" }));
  expect(await screen.findByText(/Refus serveur confirmé · aucune nouvelle preuve/)).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Corriger et réessayer" })).toBeInTheDocument();
  fireEvent.change(screen.getByLabelText("Motif du résultat inconnu"), { target: { value: "Motif corrigé" } });
  fireEvent.click(screen.getByRole("button", { name: "Corriger et réessayer" }));
  await waitFor(() => expect(intents).toHaveLength(2));
  expect(intents[1].unknown_reason).toBe("Motif corrigé");
  expect(intents[1].idempotency_key).not.toBe(intents[0].idempotency_key);
});

test("isole les données et garde la même intention quand une écriture traverse les Affaires", async () => {
  const intents: RecordCaseOutcomeInput[] = [];
  const onRecordOutcome = vi.fn(async (input: RecordCaseOutcomeInput) => {
    intents.push(input);
    if (intents.length === 1) throw new Error("network interruption");
  });
  const { rerender } = render(<CaseOutcomePanel caseId="case-1" canManage status="READY" data={empty} onRefresh={vi.fn()} onRecordOutcome={onRecordOutcome} />);
  fireEvent.change(screen.getByLabelText("Lot concerné"), { target: { value: "01" } });
  fireEvent.change(screen.getByLabelText("Motif du résultat inconnu"), { target: { value: "Fait privé case 1" } });
  fireEvent.click(screen.getByRole("button", { name: "Enregistrer le résultat par lot" }));
  expect(await screen.findByText(/résultat non confirmé/i)).toBeInTheDocument();

  rerender(<CaseOutcomePanel caseId="case-2" canManage status="READY" data={{ ...empty, case_id: "case-2" }} onRefresh={vi.fn()} onRecordOutcome={onRecordOutcome} />);
  expect(screen.getByText(/reste non confirmée pour une autre affaire/i)).toBeInTheDocument();
  expect(screen.queryByText("Fait privé case 1")).not.toBeInTheDocument();
  expect(screen.queryByLabelText("Lot concerné")).not.toBeInTheDocument();

  rerender(<CaseOutcomePanel caseId="case-1" canManage status="READY" data={empty} onRefresh={vi.fn()} onRecordOutcome={onRecordOutcome} />);
  fireEvent.click(screen.getByRole("button", { name: "Réessayer le résultat par lot" }));
  await waitFor(() => expect(intents).toHaveLength(2));
  expect(intents[1]).toEqual(intents[0]);
});

test("ne propose pas P6 après commande rejetée et ne propose pas d'écriture en lecture seule", () => {
  const rejected = { outcome_id: "out-1", lot_reference: "01", outcome: "WON" as const, source_locator: "notification://lot-01", reservations: [], unknown_reason: null, recorded_at: "2026-09-29T12:00:00Z", actor_id: "patron-1", transmission: null,
    order: { order_id: "ord-1", outcome_id: "out-1", decision: "REJECTED" as const, source_locator: "notification://lot-01", reservations: [], rationale: "Document incomplet", recorded_at: "2026-09-29T12:01:00Z", actor_id: "patron-1" }, p6: null, p7: null };
  render(<CaseOutcomePanel caseId="case-1" canManage={false} status="READY" data={{ ...empty, results: [rejected] }} onRefresh={vi.fn()} />);
  expect(screen.getByText(/P6 indisponible · commande rejetée/i)).toBeInTheDocument();
  expect(screen.queryByLabelText("Décision Patron P6")).not.toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /enregistrer/i })).not.toBeInTheDocument();
});

test("isole une commande non confirmée lors d'un changement d'Affaire puis permet le même rejeu", async () => {
  const intents: RecordCaseOutcomeInput[] = [];
  const onRecordOutcome = vi.fn(async (input: RecordCaseOutcomeInput) => {
    intents.push(input);
    if (intents.length === 1) throw new Error("interrupted");
  });
  const { rerender } = render(<CaseOutcomePanel caseId="case-1" canManage status="READY" data={empty} onRefresh={vi.fn()} onRecordOutcome={onRecordOutcome} />);
  fireEvent.change(screen.getByLabelText("Lot concerné"), { target: { value: "01" } });
  fireEvent.change(screen.getByLabelText("Motif du résultat inconnu"), { target: { value: "Preuve confidentielle de case 1" } });
  fireEvent.click(screen.getByRole("button", { name: "Enregistrer le résultat par lot" }));
  expect(await screen.findByText(/résultat non confirmé/i)).toBeInTheDocument();

  rerender(<CaseOutcomePanel caseId="case-2" canManage status="READY" data={{ ...empty, case_id: "case-2" }} onRefresh={vi.fn()} onRecordOutcome={onRecordOutcome} />);
  expect(screen.getByText(/reste non confirmée pour une autre affaire/i)).toBeInTheDocument();
  expect(screen.queryByText("Preuve confidentielle de case 1")).not.toBeInTheDocument();
  expect(screen.queryByRole("button", { name: "Enregistrer le résultat par lot" })).not.toBeInTheDocument();

  rerender(<CaseOutcomePanel caseId="case-1" canManage status="READY" data={empty} onRefresh={vi.fn()} onRecordOutcome={onRecordOutcome} />);
  fireEvent.click(screen.getByRole("button", { name: "Réessayer le résultat par lot" }));
  await waitFor(() => expect(intents).toHaveLength(2));
  expect(intents[1]).toEqual(intents[0]);
});

const baseChain = {
  outcome_id: "out-1", lot_reference: "01", outcome: "WON" as const, source_locator: "notification://lot-01", reservations: [], unknown_reason: null, recorded_at: "2026-09-29T12:00:00Z", actor_id: "patron-1", transmission: null,
  order: { order_id: "ord-1", outcome_id: "out-1", decision: "ACCEPTED" as const, source_locator: "notification://lot-01", reservations: [], rationale: "Commande rapprochée", recorded_at: "2026-09-29T12:01:00Z", actor_id: "patron-1" },
  p6: { p6_control_id: "p6-1", order_id: "ord-1", decision: "APPROVED" as const, reservations: [], rationale: "Clarifications clôturées", recorded_at: "2026-09-29T12:02:00Z", actor_id: "patron-1" },
  p7: { p7_result_id: "p7-1", p6_control_id: "p6-1", result: "UNKNOWN" as const, source_locator: null, reason: "Retour de chantier en attente", reservations: [], actor_id: "patron-1", recorded_at: "2026-09-29T12:03:00Z" },
};

test("affiche l’enseignement REX lié à son P7 avec revue avant réemploi visible", () => {
  const rex = [{ rex_id: "rex-1", p7_result_id: "p7-1", lot_reference: "01", motif: "UNKNOWN" as const, scope: "CASE_ONLY" as const, validation: "PENDING" as const, observation: "Délai de DOE sous-estimé", consequence: "Marge érodée sur le lot", follow_up: "Modèle de délai à revoir", source_locator: null, created_at: "2026-09-29T12:04:00Z" }];
  render(<CaseOutcomePanel caseId="case-1" canManage status="READY" data={{ ...empty, results: [baseChain] }} rex={rex} onRefresh={vi.fn()} />);
  expect(screen.getByText(/Enseignement REX · motif UNKNOWN/i)).toBeInTheDocument();
  expect(screen.getByText(/PENDING · revue avant réemploi requise/i)).toBeInTheDocument();
  expect(screen.getByText(/Délai de DOE sous-estimé/)).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /enregistrer l’enseignement rex/i })).not.toBeInTheDocument();
});

test("enregistre un enseignement REX à portée explicite, validation en attente par défaut", async () => {
  const rexInputs: Array<{ p7ResultId: string; input: RecordCaseRexInput }> = [];
  const onRecordRex = vi.fn(async (p7ResultId: string, input: RecordCaseRexInput) => { rexInputs.push({ p7ResultId, input }); });
  render(<CaseOutcomePanel caseId="case-1" canManage status="READY" data={{ ...empty, results: [baseChain] }} rex={[]} onRefresh={vi.fn()} onRecordRex={onRecordRex} />);
  fireEvent.change(screen.getByLabelText("Motif de l’enseignement"), { target: { value: "KNOWN" } });
  fireEvent.change(screen.getByLabelText("Portée de réemploi"), { target: { value: "LOT_PATTERN" } });
  fireEvent.change(screen.getByLabelText("Observation de l’enseignement"), { target: { value: "Prix unitaire gagnant visible" } });
  fireEvent.change(screen.getByLabelText("Conséquence de l’enseignement"), { target: { value: "Calibration marge à ajuster" } });
  fireEvent.change(screen.getByLabelText("Suivi de l’enseignement"), { target: { value: "Revue avant prochain lot" } });
  fireEvent.click(screen.getByRole("button", { name: "Enregistrer l’enseignement REX" }));
  await waitFor(() => expect(rexInputs).toHaveLength(1));
  expect(rexInputs[0].p7ResultId).toBe("p7-1");
  expect(rexInputs[0].input).toMatchObject({ case_id: "case-1", p7_result_id: "p7-1", motif: "KNOWN", scope: "LOT_PATTERN", validation: "PENDING", observation: "Prix unitaire gagnant visible", consequence: "Calibration marge à ajuster", follow_up: "Revue avant prochain lot", source_locator: null });
  expect(rexInputs[0].input.command_id).toBeDefined();
  expect(rexInputs[0].input.idempotency_key).toBeDefined();
});

test("n’affiche la section REX que lorsqu’un P7 existe pour le lot", () => {
  const withoutP7 = { ...baseChain, p7: null };
  render(<CaseOutcomePanel caseId="case-1" canManage status="READY" data={{ ...empty, results: [withoutP7] }} rex={[]} onRefresh={vi.fn()} onRecordRex={vi.fn()} />);
  expect(screen.queryByLabelText("Motif de l’enseignement")).not.toBeInTheDocument();
  expect(screen.queryByText(/Enseignement REX/)).not.toBeInTheDocument();
});
