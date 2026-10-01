import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type {
  CaseTeachingApplicability,
  CaseTeachingSource,
  RecordCaseTeachingApplicabilityInput,
} from "../../shared/types";
import { TeachingApplicabilityPanel } from "./TeachingApplicabilityPanel";

const source: CaseTeachingSource = {
  source_case_id: "source-case-1",
  source_case_label: "Extension de collège",
  source_interview_id: "interview-1",
  source_rex_id: "rex-1",
  held_on: "2026-09-29",
  source_locator: "entretien://source/1",
  interview_rationale: "Revue des enseignements",
  expires_on: "2026-10-01",
  source_validity: "USABLE",
  snapshot: {
    rex_id: "rex-1",
    lot_reference: "01",
    motif: "KNOWN",
    scope: "ENTERPRISE_PATTERN",
    validation: "APPROVED",
    observation: "Coordination entreprise à vérifier",
    consequence: "Risque de retard",
    follow_up: "Contrôle au démarrage",
    source_locator: "dce://source/section-4",
  },
  can_assess: true,
  block_reason: null,
};

const act: CaseTeachingApplicability = {
  applicability_id: "app-1",
  target_case_id: "target-1",
  source_case_id: "source-case-1",
  source_case_label: "Extension de collège",
  source_interview_id: "interview-1",
  source_rex_id: "rex-1",
  decision: "REVIEW_REQUIRED",
  rationale: "À confirmer sur le CCTP cible",
  target_source_locator: "dce://target/lot-01",
  source_expires_on: "2026-10-01",
  source_validity_at_recording: "USABLE",
  source_validity_current: "USABLE",
  source_snapshot: source.snapshot,
  actor_id: "patron-1",
  recorded_at: "2026-09-30T12:00:00Z",
};

function renderPanel(overrides: Partial<React.ComponentProps<typeof TeachingApplicabilityPanel>> = {}) {
  const props = {
    targetCaseId: "target-1",
    targetCaseLabel: "Gymnase municipal",
    readStatus: "READY" as const,
    sources: [source],
    applicabilities: [] as CaseTeachingApplicability[],
    onRecord: vi.fn(async (_input: RecordCaseTeachingApplicabilityInput) => undefined),
    onRefresh: vi.fn(),
    ...overrides,
  };
  return { ...render(<TeachingApplicabilityPanel {...props} />), props };
}

describe("TeachingApplicabilityPanel C13", () => {
  it("shows source validity and approval/scope separately from applicability", () => {
    renderPanel({ applicabilities: [act] });

    expect(screen.getByText("Affaire cible : Gymnase municipal.")).toBeVisible();
    expect(screen.getByText(/Validité : USABLE · portée : ENTERPRISE_PATTERN · revue source : APPROVED/)).toBeVisible();
    expect(screen.getByText(/REVIEW_REQUIRED · validité lors de la déclaration : USABLE · validité actuelle : USABLE/)).toBeVisible();
    expect(screen.queryByText(/Acte automatique/)).toBeNull();
    expect(screen.getByText(/ne transfère aucun contenu, ne prolonge pas la validité/)).toBeVisible();
  });

  it("records a sourced human applicability act against the exact target case", async () => {
    const { props } = renderPanel();
    fireEvent.change(screen.getByLabelText("Décision humaine d’applicabilité"), { target: { value: "APPLICABLE" } });
    fireEvent.change(screen.getByLabelText("Motif de la revue"), { target: { value: "Le lot cible impose la même coordination." } });
    fireEvent.change(screen.getByLabelText("Source consultée sur l’Affaire cible"), { target: { value: "dce://target/cctp/lot-01" } });
    fireEvent.click(screen.getByRole("button", { name: "Enregistrer la revue" }));

    await waitFor(() => expect(props.onRecord).toHaveBeenCalledTimes(1));
    expect(props.onRecord).toHaveBeenCalledWith(expect.objectContaining({
      target_case_id: "target-1",
      source_case_id: "source-case-1",
      source_interview_id: "interview-1",
      source_rex_id: "rex-1",
      decision: "APPLICABLE",
      rationale: "Le lot cible impose la même coordination.",
      target_source_locator: "dce://target/cctp/lot-01",
    }));
    expect(props.onRefresh).toHaveBeenCalledTimes(1);
  });

  it("retries the same command only when the original target Affaire is selected", async () => {
    const onRecord = vi.fn()
      .mockRejectedValueOnce(Object.assign(new Error("COMMAND_IN_PROGRESS"), { status: 409 }))
      .mockResolvedValueOnce(undefined);
    const { rerender } = renderPanel({ onRecord });
    fireEvent.change(screen.getByLabelText("Motif de la revue"), { target: { value: "À comparer" } });
    fireEvent.change(screen.getByLabelText("Source consultée sur l’Affaire cible"), { target: { value: "dce://target/1" } });
    fireEvent.click(screen.getByRole("button", { name: "Enregistrer la revue" }));
    await screen.findByText(/Résultat non confirmé · le rejeu conserve les mêmes identifiants/);
    const firstInput = onRecord.mock.calls[0]?.[0];

    rerender(<TeachingApplicabilityPanel targetCaseId="target-2" targetCaseLabel="Autre Affaire" readStatus="READY" sources={[source]} applicabilities={[]} onRecord={onRecord} onRefresh={vi.fn()} />);
    expect(screen.getByRole("button", { name: "Réessayer la revue" })).toBeDisabled();
    expect(screen.getByText(/Résultat non confirmé pour l’Affaire target-1/)).toBeVisible();
    expect(onRecord).toHaveBeenCalledTimes(1);

    rerender(<TeachingApplicabilityPanel targetCaseId="target-1" targetCaseLabel="Gymnase municipal" readStatus="READY" sources={[source]} applicabilities={[]} onRecord={onRecord} onRefresh={vi.fn()} />);
    fireEvent.click(screen.getByRole("button", { name: "Réessayer la revue" }));
    await waitFor(() => expect(onRecord).toHaveBeenCalledTimes(2));
    expect(onRecord.mock.calls[1]?.[0]).toEqual(firstInput);
  });

  it("keeps expired and incomplete sources visible without allowing a false applicable decision", () => {
    renderPanel({ sources: [{ ...source, source_validity: "EXPIRED", can_assess: false, block_reason: "SOURCE_SNAPSHOT_INCOMPLETE", snapshot: { ...source.snapshot, observation: undefined } }] });

    expect(screen.getByText(/EXPIRED · cette revue ne renouvelle pas la validité/)).toBeVisible();
    expect(screen.getByText(/SOURCE_SNAPSHOT_INCOMPLETE/)).toBeVisible();
    expect(screen.queryByRole("form", { name: /Revoir rex-1/ })).toBeNull();
  });
});
