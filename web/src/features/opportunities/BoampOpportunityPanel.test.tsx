import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { BoampObservation, BoampQualificationForm, BoampSourceStatus } from "../../shared/types";
import { BoampOpportunityPanel } from "./BoampOpportunityPanel";

const observation: BoampObservation = {
  observation_id: "observation-1",
  source_notice_id: "BOAMP-1",
  title: "Réhabilitation d’une école",
  observed_at: "2026-08-23T12:00:00Z",
  publication_date: "2026-08-20",
  response_deadline: "2026-09-15T12:00:00Z",
  department_codes: ["59"],
  market_types: ["TRAVAUX"],
  source_status: "EN_COURS",
  score_version: "BOAMP_PUBLIC_V1",
  score: 82,
  score_explanation: {
    factors: [
      {
        code: "TITLE_KEYWORD_MATCH",
        points: 50,
        matched: true,
        explanation: "1 mot-clé du profil trouvé dans le titre public",
      },
      {
        code: "ACTIVE_SOURCE_STATUS",
        points: 0,
        matched: false,
        explanation: "Le statut public n’est pas actif",
      },
    ],
  },
  fingerprint_sha256: "a".repeat(64),
  p0_state: "UNREVIEWED",
  p0_decision: null,
  p0_reason_code: null,
  p0_qualification_id: null,
  p0_decided_at: null,
  p1_state: "NOT_OPEN",
  p1_case_id: null,
  p1_opened_at: null,
  lot_scope_state: "UNKNOWN",
  lot_references: [],
  lot_scope_source: "BOAMP",
  deadline_state: "KNOWN",
  deadline_source: "BOAMP",
  deadline_source_timezone: null,
  deadline_normalized_timezone: "UTC",
  unknowns: [],
};

const form: BoampQualificationForm = {
  decision: "QUALIFIED",
  reason_code: "RELEVANT_PUBLIC_SIGNAL",
};

function renderPanel(overrides: Partial<React.ComponentProps<typeof BoampOpportunityPanel>> = {}) {
  return render(
    <BoampOpportunityPanel
      observations={[]}
      selectedObservationId=""
      qualificationForm={form}
      loading={false}
      qualifying={false}
      qualifiedObservationIds={new Set()}
      creatingCase={false}
      onRefresh={vi.fn()}
      onSelect={vi.fn()}
      onDecisionChange={vi.fn()}
      onReasonChange={vi.fn()}
      onQualify={vi.fn()}
      onCreateCase={vi.fn()}
      {...overrides}
    />,
  );
}

describe("BoampOpportunityPanel", () => {
  it("renders a tenant-scoped empty state", () => {
    renderPanel();
    expect(screen.getByText("Aucune opportunité BOAMP disponible")).toBeInTheDocument();
    expect(screen.getByText(/Aucune donnée financière/)).toBeInTheDocument();
  });

  it("renders the selected public projection and delegates actions", () => {
    const onSelect = vi.fn();
    const onQualify = vi.fn();
    const onCreateCase = vi.fn();
    const targeted = {
      ...observation,
      p0_state: "TARGETED" as const,
      p0_decision: "QUALIFIED" as const,
      p0_reason_code: "RELEVANT_PUBLIC_SIGNAL" as const,
      p0_qualification_id: "qualification-1",
      p0_decided_at: "2026-08-23T12:01:00Z",
    };
    renderPanel({
      observations: [targeted],
      selectedObservationId: targeted.observation_id,
      onSelect,
      onQualify,
      onCreateCase,
      qualifiedObservationIds: new Set([targeted.observation_id]),
    });

    expect(screen.getAllByText("Réhabilitation d’une école")).toHaveLength(2);
    expect(screen.getByText("BOAMP-1")).toBeInTheDocument();
    expect(screen.getByText("23 août 2026")).toBeInTheDocument();
    expect(screen.getByText("82")).toBeInTheDocument();
    expect(screen.getByText(/Pertinence publique · tri uniquement · BOAMP_PUBLIC_V1/)).toBeInTheDocument();
    fireEvent.click(screen.getByText("Pourquoi ce classement ?"));
    expect(screen.getByText("1 mot-clé du profil trouvé dans le titre public")).toBeInTheDocument();
    expect(screen.getAllByText("P0 Ciblée")).toHaveLength(2);
    expect(screen.getByText("P1 Non ouverte")).toBeInTheDocument();
    expect(screen.getByText("État échéance")).toBeInTheDocument();
    expect(screen.getByText("Connue")).toBeInTheDocument();
    expect(screen.getByText("Périmètre de lots")).toBeInTheDocument();
    expect(screen.getByText("À confirmer")).toBeInTheDocument();
    expect(screen.queryByText("a".repeat(64))).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /Réhabilitation d’une école/ }));
    fireEvent.click(screen.getByRole("button", { name: /Enregistrer la décision P0/ }));
    fireEvent.click(screen.getByRole("button", { name: /Créer une affaire/ }));
    expect(onSelect).toHaveBeenCalledWith("observation-1");
    expect(onQualify).toHaveBeenCalledOnce();
    expect(onCreateCase).toHaveBeenCalledOnce();
  });

  it("keeps the score separate from an explicit P0 decision", () => {
    renderPanel({
      observations: [observation],
      selectedObservationId: observation.observation_id,
      qualifiedObservationIds: new Set([observation.observation_id]),
    });

    expect(screen.getAllByText("P0 Non revu")).toHaveLength(2);
    expect(screen.getByText("Aucune décision")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Créer une affaire/ })).not.toBeInTheDocument();
  });

  it("shows P1 unknowns and hides conversion once already open", () => {
    const opened = {
      ...observation,
      p0_state: "TARGETED" as const,
      p0_decision: "QUALIFIED" as const,
      p0_reason_code: "RELEVANT_PUBLIC_SIGNAL" as const,
      p0_qualification_id: "qualification-1",
      p0_decided_at: "2026-08-23T12:01:00Z",
      p1_state: "OPEN_WITH_UNKNOWNS" as const,
      p1_case_id: "case-1",
      p1_opened_at: "2026-08-23T12:02:00Z",
      unknowns: [
        {
          code: "LOT_SCOPE" as const,
          missing: "Référence(s) de lot",
          why_it_matters: "P1 exige un périmètre de lot connu ou signalé manquant.",
          possible_impact: "Périmètre d’étude et de prix non démontré.",
          responsible: null,
          next_action: "Obtenir le RC/DCE ou saisir une référence de lot sourcée.",
          due_at: null,
          state: "OPEN" as const,
          source_ref: "BOAMP:BOAMP-1",
        },
      ],
    };

    renderPanel({
      observations: [opened],
      selectedObservationId: opened.observation_id,
      qualifiedObservationIds: new Set([opened.observation_id]),
    });

    expect(screen.getAllByText("P0 Ciblée")).toHaveLength(2);
    expect(screen.getByText("P1 Ouverte avec inconnues")).toBeInTheDocument();
    expect(screen.getByText("INCONNUES À LEVER")).toBeInTheDocument();
    expect(screen.getByText("Référence(s) de lot")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Créer une affaire/ })).not.toBeInTheDocument();
  });

  it("delegates refresh and selection changes", () => {
    const onRefresh = vi.fn();
    const onSelect = vi.fn();
    renderPanel({ observations: [observation], onRefresh, onSelect });

    fireEvent.click(screen.getByRole("button", { name: "Actualiser" }));
    fireEvent.click(screen.getByRole("button", { name: /Réhabilitation d’une école/ }));
    expect(onRefresh).toHaveBeenCalledOnce();
    expect(onSelect).toHaveBeenCalledWith("observation-1");
  });

  it("shows an outage, the last success and manual entry action", () => {
    const onManualEntry = vi.fn();
    const sourceStatus: BoampSourceStatus = {
      source: "BOAMP",
      state: "UNAVAILABLE",
      checked_at: "2026-09-15T00:00:00Z",
      last_success_at: "2026-09-14T21:30:00Z",
      retryable: true,
      manual_entry_available: true,
    };
    renderPanel({ sourceStatus, onManualEntry });

    expect(screen.getByText("Source indisponible")).toBeInTheDocument();
    expect(screen.getByText(/Dernier succès : 14 sept\. 2026/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Saisie manuelle" }));
    expect(onManualEntry).toHaveBeenCalledOnce();
  });
});
