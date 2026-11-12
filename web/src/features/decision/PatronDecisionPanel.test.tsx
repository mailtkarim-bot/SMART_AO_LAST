import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { PatronDecisionDossier } from "../../shared/types";
import { PatronDecisionPanel } from "./PatronDecisionPanel";

const decisionDossier: PatronDecisionDossier = {
  decision_id: "decision-1",
  aggregate_revision: 1,
  case_id: "case-1",
  decision_type: "GO_CONDITIONNEL",
  lifecycle: "FINALIZED",
  outcome: "GO_CONDITIONAL",
  validity: "VALID",
  context_status: "CURRENT",
  final_justification: "Les conditions opérationnelles restent à suivre.",
  known: [],
  unknowns: [{ code: "MISSING_REFERENCE", label: "Référence à confirmer" }],
  risks: [{ code: "DEADLINE", label: "Échéance à surveiller" }],
  conditions: [
    {
      condition_id: "condition-1",
      label: "Confirmer la référence chantier",
      status: "OPEN",
      due_at: "2026-09-01T00:00:00Z",
      failure_consequence: "Revue patronale requise",
    },
  ],
  sources: [
    {
      aggregate_type: "PreparationPackage",
      aggregate_id: "package-1",
      aggregate_revision: 4,
      role: "TECHNICAL_PREPARATION",
    },
  ],
  contract_evidence_links: [],
  context_fingerprint: null,
};

const frozenDecisionDossier: PatronDecisionDossier = {
  ...decisionDossier,
  lifecycle: "PENDING_PATRON",
  outcome: "UNDECIDED",
  context_status: "FROZEN",
  final_justification: null,
  context_fingerprint: "b".repeat(64),
  conditions: [],
};

describe("PatronDecisionPanel", () => {
  it("renders the controlled empty state", () => {
    render(<PatronDecisionPanel decisionDossier={null} formatDate={() => ""} />);

    expect(screen.getByText("Aucun dossier de décision disponible")).toBeInTheDocument();
    expect(screen.getByText(/contexte, les inconnus, les risques/)).toBeInTheDocument();
  });

  it("renders bounded decision facts, conditions and sources", () => {
    render(<PatronDecisionPanel decisionDossier={decisionDossier} formatDate={() => "1 sept. 2026"} />);

    expect(screen.getByText("GO_CONDITIONNEL")).toBeInTheDocument();
    expect(screen.getByText("Les conditions opérationnelles restent à suivre.")).toBeInTheDocument();
    expect(screen.getByText(/MISSING_REFERENCE/)).toBeInTheDocument();
    expect(screen.getByText(/DEADLINE/)).toBeInTheDocument();
    expect(screen.getByText("Confirmer la référence chantier")).toBeInTheDocument();
    expect(screen.getByText(/Échéance 1 sept\. 2026/)).toBeInTheDocument();
    expect(screen.getByText("PreparationPackage")).toBeInTheDocument();
    expect(screen.queryByText(/montant|marge|prix/i)).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Finaliser et enregistrer" })).not.toBeInTheDocument();
  });

  it("links exact evidence to an existing open condition without promoting the decision", async () => {
    const onLink = vi.fn().mockResolvedValue(true);
    const dossier: PatronDecisionDossier = {
      ...decisionDossier,
      outcome: "CONDITIONAL_GO",
      sources: [
        { aggregate_type: "DCE_REQUIREMENT", aggregate_id: "req-1", aggregate_revision: 2, role: "REQUIREMENT" },
        { aggregate_type: "CONTRACT_BASELINE_IMPACT", aggregate_id: "proof-1", aggregate_revision: 1, role: "IMPACT" },
        { aggregate_type: "BUSINESS_METHOD_PROFILE", aggregate_id: "profile-1", aggregate_revision: 3, role: "ADOPTED_METHOD" },
      ],
      contract_evidence_links: [],
    };
    const impact = { proof_id: "proof-1", case_id: "case-1", baseline_observation_id: "obs-1", dce_requirement_id: "req-1", dce_requirement_revision: 2, proof_revision: 1, baseline_source_refs: ["CCAP · article 4"], baseline_statement: "Baseline", deviation_statement: null, impact_statement: "Impact déclaré", status: "HUMAN_REVIEW_REQUIRED" as const };
    render(<PatronDecisionPanel decisionDossier={dossier} contractBaselineImpacts={[impact]} onLinkContractEvidence={onLink} canManage formatDate={() => ""} />);
    fireEvent.click(screen.getByRole("button", { name: "Relier l’impact v1 à cette condition" }));
    await waitFor(() => expect(onLink).toHaveBeenCalledOnce());
    expect(onLink.mock.calls[0][0]).toBe("condition-1");
    expect(onLink.mock.calls[0][1]).toMatchObject({ contract_impact_id: "proof-1", proof_revision: 1, expected_decision_revision: 1 });
  });

  it("submits the server fingerprint for a frozen patron decision", () => {
    const onFinalize = vi.fn();
    render(
      <PatronDecisionPanel
        decisionDossier={frozenDecisionDossier}
        formatDate={() => ""}
        canManage
        onFinalize={onFinalize}
      />,
    );

    fireEvent.change(screen.getByLabelText("Issue"), { target: { value: "NO_GO" } });
    fireEvent.change(screen.getByLabelText("Justification finale"), {
      target: { value: "Décision motivée après revue patronale." },
    });
    fireEvent.click(screen.getByRole("button", { name: "Finaliser et enregistrer" }));

    expect(onFinalize).toHaveBeenCalledWith({
      expected_revision: 1,
      displayed_fingerprint: "b".repeat(64),
      outcome: "NO_GO",
      justification: "Décision motivée après revue patronale.",
      conditions: [],
    });
  });
});
