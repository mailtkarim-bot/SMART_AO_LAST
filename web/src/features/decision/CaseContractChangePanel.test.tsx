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
        a1_engagements_state: "UNKNOWN",
        a1_engagements: [],
        engagement_linkage_state: "UNKNOWN",
        engagement_linkage_history: [],
        impact_declarations: [],
        action_impact_relations: [],
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
    recordCaseContractChangeEngagementLink: vi.fn(async () => ({
      result_code: "CASE_CONTRACT_CHANGE_ENGAGEMENT_LINK_RECORDED",
    })),
    recordCaseContractChangeImpactDeclaration: vi.fn(async () => ({
      result_code: "CASE_CONTRACT_CHANGE_IMPACT_DECLARED",
    })),
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
  expect(screen.getByText(/Action r1 · RECORDED/)).toBeInTheDocument();
  expect(screen.getByText(/Aucun delta de coût\/délai\/cash ni effet juridique n’est calculé automatiquement/)).toBeInTheDocument();
  vi.unstubAllGlobals();
});

test("shows the frozen A1 sources and records the Patron selection for a C1 event", async () => {
  vi.stubGlobal("crypto", { randomUUID: vi.fn(() => "stable-id") });
  const source = {
    condition_id: "condition-1",
    requirement_id: "requirement-1",
    requirement_revision: 3,
    impact_id: "impact-1",
    impact_revision: 2,
    profile_version_id: "profile-version-1",
    profile_version: 4,
    profile_sha256: "c".repeat(64),
  };
  const event: CaseContractChangeEvent = {
    event_id: "os-1",
    case_id: "case-1",
    handover_snapshot_id: "handover-1",
    outcome_id: "won-1",
    lot_reference: "01",
    offer_package_id: "p5-1",
    offer_package_version: 2,
    offer_manifest_sha256: "a".repeat(64),
    offer_source_locator: null,
    change_kind: "ORDER_OF_SERVICE",
    issuer: "MOA",
    summary: "Changement d’accès",
    scope_note: "Périmètre déclaré",
    source_refs: ["os://14"],
    evidence_refs: ["document://os/14"],
    declared_received_at: "2026-10-01T12:00:00Z",
    declared_instrument: null,
    applicability_state: "UNKNOWN",
    applicability_history: [],
    actions: [],
    a1_engagements_state: "KNOWN",
    a1_engagements: [source],
    engagement_linkage_state: "UNKNOWN",
    engagement_linkage_history: [],
    impact_declarations: [],
    action_impact_relations: [],
  };
  const api = {
    listCaseHandoverSnapshots: vi.fn().mockResolvedValue({ case_id: "case-1", items: [handover] }),
    listCaseContractChangeEvents: vi.fn().mockResolvedValue({ case_id: "case-1", events: [event] }),
    recordCaseContractChangeEngagementLink: vi.fn(async () => ({
      result_code: "CASE_CONTRACT_CHANGE_ENGAGEMENT_LINK_RECORDED",
    })),
  } as unknown as ApiClient;
  render(<CaseContractChangePanel api={api} caseId="case-1" versions={[]} />);

  expect(await screen.findByText(/exigence requirement-1 r3 · impact impact-1 r2/)).toBeInTheDocument();
  fireEvent.change(screen.getByLabelText("État du lien A1/C1 os-1"), {
    target: { value: "LINKED" },
  });
  fireEvent.click(screen.getByLabelText("Sélectionner la condition A1 condition-1"));
  fireEvent.change(screen.getByLabelText("Justification Patron"), {
    target: { value: "Le Patron relie l’OS à la condition ouverte." },
  });
  fireEvent.click(screen.getByRole("button", { name: "Enregistrer le lien Patron A1/C1" }));
  await waitFor(() => expect(api.recordCaseContractChangeEngagementLink).toHaveBeenCalledWith(
    "case-1",
    "os-1",
    expect.objectContaining({
      expected_revision: 0,
      state: "LINKED",
      selected_sources: [source],
      rationale: "Le Patron relie l’OS à la condition ouverte.",
      unknown_reason: null,
    }),
  ));
  vi.unstubAllGlobals();
});

test("records a human C3 impact on the current C2 source without calculation", async () => {
  vi.stubGlobal("crypto", { randomUUID: vi.fn(() => "impact-id") });
  const source = {
    condition_id: "condition-1",
    requirement_id: "requirement-1",
    requirement_revision: 3,
    impact_id: "impact-1",
    impact_revision: 2,
    profile_version_id: "profile-version-1",
    profile_version: 4,
    profile_sha256: "c".repeat(64),
  };
  const event: CaseContractChangeEvent = {
    event_id: "os-1",
    case_id: "case-1",
    handover_snapshot_id: "handover-1",
    outcome_id: "won-1",
    lot_reference: "01",
    offer_package_id: "p5-1",
    offer_package_version: 2,
    offer_manifest_sha256: "a".repeat(64),
    offer_source_locator: null,
    change_kind: "ORDER_OF_SERVICE",
    issuer: "MOA",
    summary: "Changement d’accès",
    scope_note: "Périmètre déclaré",
    source_refs: ["os://14"],
    evidence_refs: ["document://os/14"],
    declared_received_at: "2026-10-01T12:00:00Z",
    declared_instrument: null,
    applicability_state: "UNKNOWN",
    applicability_history: [],
    actions: [],
    a1_engagements_state: "KNOWN",
    a1_engagements: [source],
    engagement_linkage_state: "LINKED",
    engagement_linkage_history: [{
      linkage_id: "c2-link-1",
      revision: 1,
      state: "LINKED",
      selected_sources: [source],
      rationale: "Lien Patron confirmé.",
      unknown_reason: null,
      recorded_at: "2026-10-03T10:00:00Z",
    }],
    impact_declarations: [],
    action_impact_relations: [],
  };
  const api = {
    listCaseHandoverSnapshots: vi.fn().mockResolvedValue({ case_id: "case-1", items: [handover] }),
    listCaseContractChangeEvents: vi.fn().mockResolvedValue({ case_id: "case-1", events: [event] }),
    recordCaseContractChangeImpactDeclaration: vi.fn(async () => ({
      result_code: "CASE_CONTRACT_CHANGE_IMPACT_DECLARED",
    })),
  } as unknown as ApiClient;
  render(<CaseContractChangePanel api={api} caseId="case-1" versions={[]} />);

  fireEvent.change(await screen.findByLabelText("État de l’impact C3 os-1"), {
    target: { value: "DECLARED" },
  });
  fireEvent.change(screen.getByLabelText("Description de l’impact déclaré"), {
    target: { value: "Mobilisation supplémentaire déclarée." },
  });
  fireEvent.change(screen.getByLabelText("État de la mesure C3 os-1"), {
    target: { value: "DECLARED" },
  });
  fireEvent.change(screen.getByLabelText("Valeur déclarée, sans calcul"), {
    target: { value: "0.00" },
  });
  fireEvent.change(screen.getByLabelText("Devise déclarée"), {
    target: { value: "EUR" },
  });
  fireEvent.change(screen.getByLabelText("Preuves, une par ligne"), {
    target: { value: "document://impact/estimate-01" },
  });
  fireEvent.change(screen.getByLabelText("Justification Patron C3"), {
    target: { value: "Le Patron saisit cette valeur telle que déclarée." },
  });
  fireEvent.click(screen.getByRole("button", { name: "Enregistrer l’impact Patron C3" }));

  await waitFor(() => expect(api.recordCaseContractChangeImpactDeclaration).toHaveBeenCalledWith(
    "case-1",
    "os-1",
    expect.objectContaining({
      linkage_id: "c2-link-1",
      source,
      expected_revision: 0,
      axis: "COST",
      impact_state: "DECLARED",
      measurement_state: "DECLARED",
      value_as_declared: "0.00",
      currency_code: "EUR",
      unit: null,
      impact_summary: "Mobilisation supplémentaire déclarée.",
    }),
  ));
  vi.unstubAllGlobals();
});

test("links a recorded C1 action to an exact current C3 act without marking it executed", async () => {
  vi.stubGlobal("crypto", { randomUUID: vi.fn(() => "c4-id") });
  const c3 = {
    declaration_id: "c3-declaration-1", linkage_id: "c2-link-1", source: {
      condition_id: "condition-1", requirement_id: "requirement-1", requirement_revision: 1,
      impact_id: "impact-1", impact_revision: 1, profile_version_id: "profile-1",
      profile_version: 1, profile_sha256: "a".repeat(64),
    },
    axis: "COST" as const, revision: 1, impact_state: "UNKNOWN" as const,
    impact_summary: null, impact_unknown_reason: "Montant non établi.",
    measurement_state: "UNKNOWN" as const, value_as_declared: null, currency_code: null,
    unit: null, measurement_unknown_reason: null, assumptions: [], source_refs: ["os://14"],
    evidence_refs: [], rationale: "Impact conservé UNKNOWN.", linkage_state: "CURRENT" as const,
    recorded_at: "2026-10-03T10:00:00Z",
  };
  const event: CaseContractChangeEvent = {
    event_id: "os-1", case_id: "case-1", handover_snapshot_id: "handover-1",
    outcome_id: "won-1", lot_reference: "01", offer_package_id: "p5-1",
    offer_package_version: 2, offer_manifest_sha256: "a".repeat(64), offer_source_locator: null,
    change_kind: "ORDER_OF_SERVICE", issuer: "MOA", summary: "OS 14", scope_note: "Périmètre",
    source_refs: ["os://14"], evidence_refs: ["document://os/14"],
    declared_received_at: "2026-10-03T10:00:00Z", declared_instrument: null,
    applicability_state: "APPLICABLE_TO_HANDOVER",
    applicability_history: [{
      review_id: "review-1", revision: 1, contract_instrument_version_id: "contract-1",
      decision: "APPLICABLE_TO_HANDOVER", delta_state: "UNKNOWN", delta_note: null,
      rationale: "Applicabilité déclarée.", evidence_refs: ["review://1"],
      recorded_at: "2026-10-03T10:00:00Z", contract_instrument: null,
    }],
    actions: [{
      action_id: "action-1", revision: 1, applicability_review_id: "review-1",
      summary: "Vérifier le chiffrage", evidence_refs: ["devis://a"], due_at: null,
      due_date_absence_reason: "Échéance inconnue.", state: "RECORDED",
      recorded_at: "2026-10-03T10:00:00Z",
    }],
    a1_engagements_state: "UNKNOWN", a1_engagements: [],
    engagement_linkage_state: "LINKED", engagement_linkage_history: [],
    impact_declarations: [c3], action_impact_relations: [],
  };
  const api = {
    listCaseHandoverSnapshots: vi.fn().mockResolvedValue({ case_id: "case-1", items: [handover] }),
    listCaseContractChangeEvents: vi.fn().mockResolvedValue({ case_id: "case-1", events: [event] }),
    recordCaseContractChangeActionImpactRelation: vi.fn(async () => ({
      result_code: "CASE_CONTRACT_CHANGE_ACTION_IMPACT_RELATED",
    })),
  } as unknown as ApiClient;
  render(<CaseContractChangePanel api={api} caseId="case-1" versions={[]} />);

  fireEvent.click(await screen.findByLabelText("Sélectionner l’impact C3 c3-declaration-1"));
  fireEvent.change(screen.getByLabelText("Justification Patron C4"), {
    target: { value: "L’action traite explicitement cet impact inconnu." },
  });
  fireEvent.click(screen.getByRole("button", { name: "Enregistrer la liaison Patron C4" }));

  await waitFor(() => expect(api.recordCaseContractChangeActionImpactRelation).toHaveBeenCalledWith(
    "case-1", "os-1", "action-1", expect.objectContaining({
      expected_revision: 0,
      state: "LINKED",
      declaration_ids: ["c3-declaration-1"],
      rationale: "L’action traite explicitement cet impact inconnu.",
    }),
  ));
  expect(screen.getByText(/état RECORDED/)).toBeInTheDocument();
  expect(screen.getByText(/ne prouve ni son exécution ni sa clôture/)).toBeInTheDocument();
  vi.unstubAllGlobals();
});
