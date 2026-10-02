import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { expect, test, vi } from "vitest";
import type { ApiClient } from "../../infrastructure/api";
import type {
  CaseContractChangeEvent,
  ContractInstrumentVersion,
} from "../../shared/types";
import { CaseContractChangePanel } from "./CaseContractChangePanel";

const handover = {
  snapshot_id: "handover-1",
  outcome_id: "won-1",
  lot_reference: "01",
  submission_package_id: "p5-1",
  package_version: 2,
  manifest_sha256: "a".repeat(64),
  revision: 1,
  created_at: "2026-10-01T12:00:00Z",
  snapshot: {} as never,
};
const instrument: ContractInstrumentVersion = {
  contract_instrument_version_id: "contract-version-1",
  case_id: "case-1",
  instrument_kind: "SIGNED_CONTRACT",
  version_reference: "CONTRAT-SIGNE-2026-01",
  source_refs: ["document://contract/01"],
  evidence_refs: ["sha256:" + "b".repeat(64)],
  actor_id: "patron-1",
  recorded_at: "2026-10-01T11:00:00Z",
};

test("keeps a sourced change UNKNOWN until Patron applicability, then records action and proof", async () => {
  vi.stubGlobal("crypto", { randomUUID: vi.fn(() => "os-event") });
  let events: CaseContractChangeEvent[] = [];
  const api = {
    listCaseHandoverSnapshots: vi.fn().mockResolvedValue({ case_id: "case-1", items: [handover] }),
    listCaseContractChangeEvents: vi.fn(async () => ({ case_id: "case-1", events })),
    recordCaseContractChangeEvent: vi.fn(async (_caseId, input) => {
      events = [{
        event_id: input.event_id,
        case_id: "case-1",
        handover_snapshot_id: input.handover_snapshot_id,
        outcome_id: "won-1",
        lot_reference: "01",
        offer_package_id: "p5-1",
        offer_package_version: 2,
        offer_manifest_sha256: "a".repeat(64),
        offer_source_locator: "attribution://result/01",
        change_kind: input.change_kind,
        issuer: input.issuer,
        summary: input.summary,
        scope_note: input.scope_note,
        source_refs: input.source_refs,
        evidence_refs: input.evidence_refs,
        declared_received_at: input.declared_received_at,
        declared_instrument: null,
        applicability_state: "UNKNOWN",
        applicability_history: [],
        actions: [],
      }];
      return { result_code: "CASE_CONTRACT_CHANGE_EVENT_RECORDED" };
    }),
    recordCaseContractChangeApplicability: vi.fn(async (_caseId, eventId, input) => {
      const event = events.find((item) => item.event_id === eventId)!;
      events = [{
        ...event,
        applicability_state: input.decision,
        applicability_history: [{
          review_id: input.review_id,
          revision: 1,
          contract_instrument_version_id: input.contract_instrument_version_id,
          decision: input.decision,
          delta_state: input.delta_state,
          delta_note: input.delta_note,
          rationale: input.rationale,
          evidence_refs: input.evidence_refs,
          recorded_at: "2026-10-01T13:00:00Z",
          contract_instrument: {
            contract_instrument_version_id: instrument.contract_instrument_version_id,
            instrument_kind: instrument.instrument_kind,
            version_reference: instrument.version_reference,
            source_refs: instrument.source_refs,
            evidence_refs: instrument.evidence_refs,
          },
        }],
      }];
      return { result_code: "CASE_CONTRACT_CHANGE_APPLICABILITY_RECORDED" };
    }),
    recordCaseContractChangeAction: vi.fn(async (_caseId, eventId, input) => {
      const event = events.find((item) => item.event_id === eventId)!;
      events = [{
        ...event,
        actions: [{
          action_id: input.action_id,
          revision: 1,
          applicability_review_id: input.applicability_review_id,
          summary: input.action_summary,
          evidence_refs: input.evidence_refs,
          due_at: input.due_at,
          due_date_absence_reason: input.due_date_absence_reason,
          state: "RECORDED",
          recorded_at: "2026-10-01T14:00:00Z",
        }],
      }];
      return { result_code: "CASE_CONTRACT_CHANGE_ACTION_RECORDED" };
    }),
  } as unknown as ApiClient;

  render(<CaseContractChangePanel api={api} caseId="case-1" versions={[instrument]} />);
  fireEvent.change(await screen.findByLabelText("Passation de départ"), {
    target: { value: "handover-1" },
  });
  fireEvent.change(screen.getByLabelText("Résumé déclaré"), {
    target: { value: "OS 14 reçu" },
  });
  fireEvent.change(screen.getByLabelText(/Périmètre\/delta décrit/), {
    target: { value: "Modification déclarée du phasage" },
  });
  fireEvent.change(screen.getByLabelText("Références source, une par ligne"), {
    target: { value: "os://14" },
  });
  fireEvent.change(screen.getByLabelText("Preuves de réception/événement, une par ligne"), {
    target: { value: "document://os/14" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Enregistrer l’événement sourcé" }));
  expect(await screen.findByText(/Applicabilité à cette passation : UNKNOWN/)).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /Enregistrer l’action et la preuve/ })).not.toBeInTheDocument();

  fireEvent.change(screen.getByLabelText(/Version contrat retenue par le Patron/), {
    target: { value: instrument.contract_instrument_version_id },
  });
  fireEvent.change(screen.getByLabelText(/Décision d’applicabilité/), {
    target: { value: "APPLICABLE_TO_HANDOVER" },
  });
  fireEvent.change(screen.getByLabelText(/État du delta/), {
    target: { value: "DECLARED" },
  });
  fireEvent.change(screen.getByLabelText(/Delta résumé déclaré/), {
    target: { value: "Périmètre déclaré modifié ; coût et délai restent non calculés." },
  });
  fireEvent.change(screen.getByLabelText("Justification de revue"), {
    target: { value: "Le Patron relie l’OS à la passation." },
  });
  fireEvent.change(screen.getByLabelText("Sources/preuves de la décision, une par ligne"), {
    target: { value: "document://review/01" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Enregistrer la revue Patron" }));
  expect(await screen.findByText(/Applicabilité à cette passation : APPLICABLE_TO_HANDOVER/)).toBeInTheDocument();
  expect(api.recordCaseContractChangeApplicability).toHaveBeenCalledWith("case-1", "os-event", expect.objectContaining({
    delta_state: "DECLARED",
    delta_note: "Périmètre déclaré modifié ; coût et délai restent non calculés.",
  }));
  expect(screen.getByRole("heading", { name: "Action et preuve Patron" })).toBeInTheDocument();

  fireEvent.change(screen.getByLabelText("Action déclarée"), {
    target: { value: "Faire chiffrer la modification" },
  });
  fireEvent.change(screen.getByLabelText("Sources/preuves liées à l’action, une par ligne"), {
    target: { value: "document://devis/actualise" },
  });
  fireEvent.change(screen.getByLabelText("Motif d’échéance inconnue"), {
    target: { value: "Aucune échéance validée." },
  });
  fireEvent.click(screen.getByRole("button", { name: "Enregistrer l’action et la preuve" }));
  await waitFor(() => expect(api.recordCaseContractChangeAction).toHaveBeenCalledWith(
    "case-1",
    "os-event",
    expect.objectContaining({
      action_summary: "Faire chiffrer la modification",
      due_at: null,
      due_date_absence_reason: "Aucune échéance validée.",
    }),
  ));
  expect(screen.getByText(/RECORDED/)).toBeInTheDocument();
  expect(screen.getByText(/Aucun delta de coût\/délai\/cash ni effet juridique n’est calculé automatiquement/)).toBeInTheDocument();
  vi.unstubAllGlobals();
});
