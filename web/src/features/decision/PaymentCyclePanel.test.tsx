import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";
import { PaymentCyclePanel } from "./PaymentCyclePanel";

test("affiche les hypothèses cash en lecture seule", () => {
  render(<PaymentCyclePanel cycles={[{ cycle_id: "c1", case_id: "a1", source_refs: ["ccap://p12"], trigger_event: "RECEPTION", status: "REVIEW_REQUIRED", cash_assumption: "À confirmer", post_reception_cost_note: "À qualifier" }]} />);
  expect(screen.getByText("REVIEW_REQUIRED")).toBeInTheDocument();
  expect(screen.getByText(/À confirmer/)).toBeInTheDocument();
  expect(screen.queryByRole("button")).not.toBeInTheDocument();
});

test("déclenche la revue Patron sans modifier le cycle", async () => {
  const onReview = vi.fn().mockResolvedValue(undefined);
  render(<PaymentCyclePanel cycles={[{ cycle_id: "c1", case_id: "a1", source_refs: ["ccap://p12"], trigger_event: "RECEPTION", status: "REVIEW_REQUIRED", cash_assumption: "À confirmer", post_reception_cost_note: null }]} onReview={onReview} />);
  await screen.getByRole("button", { name: /marquer revue requise/i }).click();
  expect(onReview).toHaveBeenCalledOnce();
});

test("affiche l'audit des inconnus en lecture seule", () => {
  render(<PaymentCyclePanel cycles={[{ cycle_id: "c1", case_id: "a1", source_refs: ["ccap://p12"], trigger_event: "RECEPTION", status: "UNKNOWN", cash_assumption: null, post_reception_cost_note: null }]} unknownAudit={{ status_counts: { UNKNOWN: 1, REVIEW_REQUIRED: 0, SOURCE_SIGNAL_ONLY: 0 }, entries: [{ cycle_id: "c1", status: "UNKNOWN", trigger_event: "RECEPTION", source_refs: ["ccap://p20"] }] }} />);
  expect(screen.getByLabelText("Audit des inconnus paiement")).toHaveTextContent("UNKNOWN : 1");
  expect(screen.getByLabelText("Entrées inconnues paiement")).toHaveTextContent("ccap://p20");
  expect(screen.queryByRole("button")).not.toBeInTheDocument();
});

test("permet au Patron d'enregistrer l'acte sans modifier l'audit", async () => {
  const onOwnerAct = vi.fn().mockResolvedValue(undefined);
  render(<PaymentCyclePanel cycles={[{ cycle_id: "c1", case_id: "a1", source_refs: ["ccap://p12"], trigger_event: "RECEPTION", status: "UNKNOWN", cash_assumption: null, post_reception_cost_note: null }]} unknownAudit={{ status_counts: { UNKNOWN: 1 }, entries: [] }} onOwnerAct={onOwnerAct} />);
  await screen.getByRole("button", { name: /valider l.audit patron/i }).click();
  expect(onOwnerAct).toHaveBeenCalledOnce();
});

test("n'autorise pas l'acte Patron sans audit disponible", () => {
  const onOwnerAct = vi.fn().mockResolvedValue(undefined);
  render(<PaymentCyclePanel cycles={[{ cycle_id: "c1", case_id: "a1", source_refs: ["ccap://p12"], trigger_event: "RECEPTION", status: "UNKNOWN", cash_assumption: null, post_reception_cost_note: null }]} onOwnerAct={onOwnerAct} />);
  expect(screen.queryByRole("button", { name: /valider l.audit patron/i })).not.toBeInTheDocument();
});

test("bloque le double clic pendant l'écriture de l'acte Patron", async () => {
  let release!: () => void;
  const onOwnerAct = vi.fn(() => new Promise<void>((resolve) => { release = resolve; }));
  render(<PaymentCyclePanel cycles={[{ cycle_id: "c1", case_id: "a1", source_refs: ["ccap://p12"], trigger_event: "RECEPTION", status: "UNKNOWN", cash_assumption: null, post_reception_cost_note: null }]} unknownAudit={{ status_counts: { UNKNOWN: 1 }, entries: [] }} onOwnerAct={onOwnerAct} />);
  const button = screen.getByRole("button", { name: /valider l.audit patron/i });
  await button.click();
  await button.click();
  expect(onOwnerAct).toHaveBeenCalledOnce();
  release();
});

test("n'affiche pas de succès quand l'écriture Patron échoue", async () => {
  const onOwnerAct = vi.fn().mockRejectedValue(new Error("interrompu"));
  render(<PaymentCyclePanel cycles={[{ cycle_id: "c1", case_id: "a1", source_refs: ["ccap://p12"], trigger_event: "RECEPTION", status: "UNKNOWN", cash_assumption: null, post_reception_cost_note: null }]} unknownAudit={{ status_counts: { UNKNOWN: 1 }, entries: [] }} onOwnerAct={onOwnerAct} />);
  await screen.getByRole("button", { name: /valider l.audit patron/i }).click();
  expect(await screen.findByRole("alert")).toHaveTextContent("non confirmée");
  expect(screen.queryByText(/Validation Patron : approuvée/)).not.toBeInTheDocument();
});

test("réutilise les identifiants après un résultat non confirmé", async () => {
  const inputs: Record<string, unknown>[] = [];
  const onOwnerAct = vi.fn((input: Record<string, unknown>) => { inputs.push(input); return Promise.reject(new Error("interrompu")); });
  render(<PaymentCyclePanel cycles={[{ cycle_id: "c1", case_id: "a1", source_refs: ["ccap://p12"], trigger_event: "RECEPTION", status: "UNKNOWN", cash_assumption: null, post_reception_cost_note: null }]} unknownAudit={{ status_counts: { UNKNOWN: 1 }, entries: [] }} onOwnerAct={onOwnerAct} />);
  const button = screen.getByRole("button", { name: /valider l.audit patron/i });
  await button.click();
  await screen.findByRole("alert");
  await button.click();
  expect(inputs[0].command_id).toBe(inputs[1].command_id);
  expect(inputs[0].idempotency_key).toBe(inputs[1].idempotency_key);
  expect(inputs[0].owner_act_id).toBe(inputs[1].owner_act_id);
});

test("réinitialise les identifiants quand l'Affaire change", async () => {
  const inputs: Record<string, unknown>[] = [];
  const onOwnerAct = vi.fn((input: Record<string, unknown>) => { inputs.push(input); return Promise.resolve(); });
  const first = { cycle_id: "c1", case_id: "a1", source_refs: ["ccap://p12"], trigger_event: "RECEPTION", status: "UNKNOWN" as const, cash_assumption: null, post_reception_cost_note: null };
  const { rerender } = render(<PaymentCyclePanel cycles={[first]} unknownAudit={{ status_counts: { UNKNOWN: 1 }, entries: [] }} onOwnerAct={onOwnerAct} />);
  await screen.getByRole("button", { name: /valider l.audit patron/i }).click();
  const firstId = inputs[0].owner_act_id;
  rerender(<PaymentCyclePanel cycles={[{ ...first, cycle_id: "c2", case_id: "a2" }]} unknownAudit={{ status_counts: { UNKNOWN: 1 }, entries: [] }} onOwnerAct={onOwnerAct} />);
  await screen.getByRole("button", { name: /valider l.audit patron/i }).click();
  expect(inputs[1].owner_act_id).not.toBe(firstId);
});

test("affiche uniquement l'acte Patron relu depuis le serveur", () => {
  render(<PaymentCyclePanel cycles={[{ cycle_id: "c1", case_id: "a1", source_refs: ["ccap://p12"], trigger_event: "RECEPTION", status: "UNKNOWN", cash_assumption: null, post_reception_cost_note: null }]} unknownAudit={{ status_counts: { UNKNOWN: 1 }, entries: [] }} ownerAct={{ owner_act_id: "oa1", case_id: "a1", owner_id: "o1", approved: true, rationale: "Revue persistée", created_at: "2026-09-28T00:00:00Z" }} />);
  expect(screen.getByLabelText("Validation Patron audit paiement")).toHaveTextContent("Revue persistée");
});

test("signale l'audit indisponible et suspend la validation", () => {
  const onOwnerAct = vi.fn().mockResolvedValue(undefined);
  render(<PaymentCyclePanel cycles={[{ cycle_id: "c1", case_id: "a1", source_refs: ["ccap://p12"], trigger_event: "RECEPTION", status: "UNKNOWN", cash_assumption: null, post_reception_cost_note: null }]} onOwnerAct={onOwnerAct} />);
  expect(screen.getByRole("status")).toHaveTextContent("Audit paiement indisponible");
  expect(screen.queryByRole("button", { name: /valider l.audit patron/i })).not.toBeInTheDocument();
});

test("projette le signal externe et la revue Patron sans certitude de cash", () => {
  render(<PaymentCyclePanel cycles={[{ cycle_id: "c1", case_id: "a1", source_refs: ["external://payment-signal/1"], trigger_event: "EXTERNAL_PAYMENT_SIGNAL", status: "SOURCE_SIGNAL_ONLY", cash_assumption: null, post_reception_cost_note: "À qualifier" }]} reviews={{ c1: [{ review_id: "r1", cycle_id: "c1", reviewer_id: "o1", decision: "REVIEW_REQUIRED", rationale: "Signal externe à confirmer", created_at: "2026-09-28T00:00:00Z" }] }} />);
  expect(screen.getByText("SOURCE_SIGNAL_ONLY")).toBeInTheDocument();
  expect(screen.getByText(/Signal externe à confirmer/)).toBeInTheDocument();
  expect(screen.getByText(/aucune certitude de cash/)).toBeInTheDocument();
});

test("affiche séparément les rejets de collecte", () => {
  render(<PaymentCyclePanel cycles={[{ cycle_id: "c1", case_id: "a1", source_refs: ["fixture://valid"], trigger_event: "EXTERNAL_PAYMENT_SIGNAL", status: "SOURCE_SIGNAL_ONLY", cash_assumption: null, post_reception_cost_note: null }]} unknownAudit={{ status_counts: { SOURCE_SIGNAL_ONLY: 1 }, entries: [], rejected_count: 2 }} />);
  expect(screen.getByLabelText("Audit des inconnus paiement")).toHaveTextContent("Rejets de collecte : 2");
});

test("bloque la validation Patron tant que des rejets partiels sont à traiter", () => {
  const onOwnerAct = vi.fn().mockResolvedValue(undefined);
  render(<PaymentCyclePanel cycles={[{ cycle_id: "c1", case_id: "a1", source_refs: ["fixture://valid"], trigger_event: "EXTERNAL_PAYMENT_SIGNAL", status: "SOURCE_SIGNAL_ONLY", cash_assumption: null, post_reception_cost_note: null }]} unknownAudit={{ status_counts: { SOURCE_SIGNAL_ONLY: 1 }, entries: [], rejected_count: 1 }} onOwnerAct={onOwnerAct} />);
  expect(screen.getByRole("status")).toHaveTextContent("Rejets de collecte à traiter");
  expect(screen.queryByRole("button", { name: /valider l.audit patron/i })).not.toBeInTheDocument();
});

test("permet au Patron d'enregistrer l'acte de traitement des rejets partiels", async () => {
  const onRejectionReview = vi.fn().mockResolvedValue(undefined);
  render(<PaymentCyclePanel cycles={[{ cycle_id: "c1", case_id: "a1", source_refs: ["fixture://valid"], trigger_event: "EXTERNAL_PAYMENT_SIGNAL", status: "SOURCE_SIGNAL_ONLY", cash_assumption: null, post_reception_cost_note: null }]} unknownAudit={{ status_counts: { SOURCE_SIGNAL_ONLY: 1 }, entries: [], rejected_count: 2 }} onRejectionReview={onRejectionReview} />);
  fireEvent.change(screen.getByLabelText("Justification des rejets"), { target: { value: "Deux fixtures invalides écartées" } });
  await screen.getByRole("button", { name: /traiter les rejets de collecte/i }).click();
  expect(onRejectionReview).toHaveBeenCalledOnce();
  expect(onRejectionReview.mock.calls[0][0]).toMatchObject({ rejected_count: 2, decision: "ACKNOWLEDGED", rationale: "Deux fixtures invalides écartées" });
  expect(onRejectionReview.mock.calls[0][0].command_id).toBeDefined();
  expect(onRejectionReview.mock.calls[0][0].idempotency_key).toBeDefined();
  expect(onRejectionReview.mock.calls[0][0].review_id).toBeDefined();
});

test("permet au Patron d'exiger un suivi sur les rejets partiels", async () => {
  const onRejectionReview = vi.fn().mockResolvedValue(undefined);
  render(<PaymentCyclePanel cycles={[{ cycle_id: "c1", case_id: "a1", source_refs: ["fixture://valid"], trigger_event: "EXTERNAL_PAYMENT_SIGNAL", status: "SOURCE_SIGNAL_ONLY", cash_assumption: null, post_reception_cost_note: null }]} unknownAudit={{ status_counts: { SOURCE_SIGNAL_ONLY: 1 }, entries: [], rejected_count: 1 }} onRejectionReview={onRejectionReview} />);
  fireEvent.change(screen.getByLabelText("Décision des rejets"), { target: { value: "FOLLOW_UP_REQUIRED" } });
  fireEvent.change(screen.getByLabelText("Justification des rejets"), { target: { value: "Source externe à requalifier" } });
  await screen.getByRole("button", { name: /traiter les rejets de collecte/i }).click();
  expect(onRejectionReview.mock.calls[0][0]).toMatchObject({ rejected_count: 1, decision: "FOLLOW_UP_REQUIRED", rationale: "Source externe à requalifier" });
});

test("affiche uniquement l'acte rejets relu depuis le serveur", () => {
  render(<PaymentCyclePanel cycles={[{ cycle_id: "c1", case_id: "a1", source_refs: ["fixture://valid"], trigger_event: "EXTERNAL_PAYMENT_SIGNAL", status: "SOURCE_SIGNAL_ONLY", cash_assumption: null, post_reception_cost_note: null }]} unknownAudit={{ status_counts: { SOURCE_SIGNAL_ONLY: 1 }, entries: [], rejected_count: 2 }} rejectionReview={{ review_id: "rr1", case_id: "a1", reviewer_id: "o1", rejected_count: 2, decision: "ACKNOWLEDGED", rationale: "Rejets persistés", created_at: "2026-09-28T00:00:00Z" }} />);
  expect(screen.getByLabelText("Revue rejets de collecte")).toHaveTextContent("Rejets persistés");
  expect(screen.queryByRole("button", { name: /traiter les rejets de collecte/i })).not.toBeInTheDocument();
});

test("réutilise les identifiants après un rejet non confirmé", async () => {
  const inputs: Record<string, unknown>[] = [];
  const onRejectionReview = vi.fn((input: Record<string, unknown>) => { inputs.push(input); return Promise.reject(new Error("interrompu")); });
  render(<PaymentCyclePanel cycles={[{ cycle_id: "c1", case_id: "a1", source_refs: ["fixture://valid"], trigger_event: "EXTERNAL_PAYMENT_SIGNAL", status: "SOURCE_SIGNAL_ONLY", cash_assumption: null, post_reception_cost_note: null }]} unknownAudit={{ status_counts: { SOURCE_SIGNAL_ONLY: 1 }, entries: [], rejected_count: 2 }} onRejectionReview={onRejectionReview} />);
  fireEvent.change(screen.getByLabelText("Justification des rejets"), { target: { value: "Rejets à traiter" } });
  const button = screen.getByRole("button", { name: /traiter les rejets de collecte/i });
  await button.click();
  expect(await screen.findByRole("alert")).toHaveTextContent("non confirmée");
  await button.click();
  expect(inputs).toHaveLength(2);
  expect(inputs[0].command_id).toBe(inputs[1].command_id);
  expect(inputs[0].idempotency_key).toBe(inputs[1].idempotency_key);
  expect(inputs[0].review_id).toBe(inputs[1].review_id);
});

test("débloque la validation Patron après traitement des rejets", async () => {
  const onOwnerAct = vi.fn().mockResolvedValue(undefined);
  render(<PaymentCyclePanel cycles={[{ cycle_id: "c1", case_id: "a1", source_refs: ["fixture://valid"], trigger_event: "EXTERNAL_PAYMENT_SIGNAL", status: "SOURCE_SIGNAL_ONLY", cash_assumption: null, post_reception_cost_note: null }]} unknownAudit={{ status_counts: { SOURCE_SIGNAL_ONLY: 1 }, entries: [], rejected_count: 1 }} rejectionReview={{ review_id: "rr1", case_id: "a1", reviewer_id: "o1", rejected_count: 1, decision: "ACKNOWLEDGED", rationale: "Rejets persistés", created_at: "2026-09-28T00:00:00Z" }} onOwnerAct={onOwnerAct} />);
  expect(screen.queryByRole("status")).not.toBeInTheDocument();
  await screen.getByRole("button", { name: /valider l.audit patron/i }).click();
  expect(onOwnerAct).toHaveBeenCalledOnce();
});

test("n'exige pas de traitement des rejets quand aucun rejet n'est signalé", async () => {
  const onOwnerAct = vi.fn().mockResolvedValue(undefined);
  render(<PaymentCyclePanel cycles={[{ cycle_id: "c1", case_id: "a1", source_refs: ["fixture://valid"], trigger_event: "EXTERNAL_PAYMENT_SIGNAL", status: "SOURCE_SIGNAL_ONLY", cash_assumption: null, post_reception_cost_note: null }]} unknownAudit={{ status_counts: { SOURCE_SIGNAL_ONLY: 1 }, entries: [] }} onOwnerAct={onOwnerAct} />);
  expect(screen.queryByRole("status")).not.toBeInTheDocument();
  await screen.getByRole("button", { name: /valider l.audit patron/i }).click();
  expect(onOwnerAct).toHaveBeenCalledOnce();
});

test("permet au Patron de qualifier le coût post-réception et l'hypothèse de cash prudentienne", async () => {
  const onQualify = vi.fn().mockResolvedValue(undefined);
  render(<PaymentCyclePanel cycles={[{ cycle_id: "c1", case_id: "a1", source_refs: ["external://payment-signal/1"], trigger_event: "EXTERNAL_PAYMENT_SIGNAL", status: "SOURCE_SIGNAL_ONLY", cash_assumption: null, post_reception_cost_note: null }]} onQualify={onQualify} />);
  fireEvent.change(screen.getByLabelText("Coût post-réception"), { target: { value: "Levée de réserves à chiffrer" } });
  fireEvent.change(screen.getByLabelText("Hypothèse cash prudentière"), { target: { value: "Délai prudent 75 jours" } });
  await screen.getByRole("button", { name: /qualifier coût et cash/i }).click();
  expect(onQualify).toHaveBeenCalledOnce();
  expect(onQualify.mock.calls[0][0]).toBe("c1");
  expect(onQualify.mock.calls[0][1]).toMatchObject({ cash_assumption: "Délai prudent 75 jours", post_reception_cost_note: "Levée de réserves à chiffrer" });
  expect(onQualify.mock.calls[0][1].command_id).toBeDefined();
  expect(onQualify.mock.calls[0][1].idempotency_key).toBeDefined();
});

test("n'affiche la qualification que si un gestionnaire est fourni", () => {
  render(<PaymentCyclePanel cycles={[{ cycle_id: "c1", case_id: "a1", source_refs: ["external://payment-signal/1"], trigger_event: "EXTERNAL_PAYMENT_SIGNAL", status: "SOURCE_SIGNAL_ONLY", cash_assumption: null, post_reception_cost_note: null }]} />);
  expect(screen.queryByRole("button", { name: /qualifier coût et cash/i })).not.toBeInTheDocument();
});
