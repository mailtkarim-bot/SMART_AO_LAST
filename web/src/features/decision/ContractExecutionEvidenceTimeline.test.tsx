import { render, screen, within } from "@testing-library/react";
import { expect, test } from "vitest";
import type { ContractExecutionEvidenceTimelineEvent } from "../../shared/types";
import { ContractExecutionEvidenceTimeline } from "./ContractExecutionEvidenceTimeline";

const timeline: ContractExecutionEvidenceTimelineEvent[] = [
  {
    event_type: "EXECUTION_EVIDENCE", event_id: "act-1", case_id: "case-1", revision: 1,
    status: "RECORDED", status_origin: "HUMAN_ACT", actor_id: "patron-1", recorded_at: "2026-09-28T10:00:00Z",
    act: {
      act_id: "act-1", act_kind: "RIGHTS_PRESERVATION", reception_outcome: "UNKNOWN", summary: "Réserve envoyée",
      declared_event_date: "2026-09-28", source_refs: ["contract://clause/18"],
      evidence_refs: ["document://courrier/sha256:abc"], case_dce_version_id_at_recording: null,
      current_dce_relation: "UNKNOWN", contract_instrument_version_id: "signed-v1",
      current_instrument_relation: "REVIEW_REQUIRED",
      contract_instrument_version: {
        contract_instrument_version_id: "signed-v1", instrument_kind: "SIGNED_CONTRACT",
        version_reference: "MARCHE-SIGNE-1", source_refs: ["contract://signed/1"], evidence_refs: ["document://signed/1"],
      },
    },
  },
  {
    event_type: "INSTRUMENT_SUPERSESSION", event_id: "sup-1", case_id: "case-1", revision: 1,
    status: "SUPERSEDED", status_origin: "PATRON_DECLARATION", actor_id: "patron-1",
    recorded_at: "2026-09-29T10:00:00Z", supersession_id: "sup-1", rationale: "Avenant reçu et rattaché.",
    replacing: {
      contract_instrument_version_id: "amendment-v2", instrument_kind: "AMENDMENT",
      version_reference: "AVENANT-2", source_refs: ["contract://amendment/2"], evidence_refs: ["document://amendment/2"],
    },
    replaced: {
      contract_instrument_version_id: "signed-v1", instrument_kind: "SIGNED_CONTRACT",
      version_reference: "MARCHE-SIGNE-1", source_refs: ["contract://signed/1"], evidence_refs: ["document://signed/1"],
    },
  },
  {
    event_type: "EVIDENCE_REQUALIFICATION", event_id: "review-1", case_id: "case-1", revision: 1,
    status: "NEEDS_CLARIFICATION", status_origin: "PATRON_DECISION", actor_id: "patron-1",
    recorded_at: "2026-09-29T11:00:00Z", requalification_id: "review-1", act_id: "act-1",
    supersession_id: "sup-1", act_kind: "RIGHTS_PRESERVATION", act_summary: "Réserve envoyée",
    act_source_refs: ["contract://clause/18"], act_evidence_refs: ["document://courrier/sha256:abc"],
    resulting_contract_instrument_version_id: null, resulting_instrument_kind: null,
    resulting_version_reference: null, rationale: "Le lien doit être confirmé.",
  },
];

test("présente l’acte, le remplacement et la requalification comme trois événements sourcés distincts", () => {
  render(<ContractExecutionEvidenceTimeline events={timeline} status="READY" />);
  const list = within(screen.getByLabelText("Chronologie C07 axe 12")).getAllByRole("listitem");

  expect(list).toHaveLength(3);
  expect(list[0]).toHaveTextContent("ACTE INITIAL · Réserve envoyée");
  expect(list[0]).toHaveTextContent("contract://clause/18");
  expect(list[1]).toHaveTextContent("SUPERSEDED · déclaration Patron, non vérifiée");
  expect(list[1]).toHaveTextContent("contract://signed/1");
  expect(list[1]).toHaveTextContent("contract://amendment/2");
  expect(list[2]).toHaveTextContent("NEEDS_CLARIFICATION");
  expect(list[2]).toHaveTextContent("Le lien doit être confirmé");
  expect(list[2]).toHaveTextContent("applicabilité juridique non évaluée");
});

test("ne convertit pas une chronologie indisponible en absence d’événements", () => {
  render(<ContractExecutionEvidenceTimeline events={[]} status="UNAVAILABLE" />);
  expect(screen.getByText(/UNAVAILABLE · chronologie indisponible/i)).toBeInTheDocument();
  expect(screen.queryByText(/aucun événement enregistré/i)).not.toBeInTheDocument();
});
