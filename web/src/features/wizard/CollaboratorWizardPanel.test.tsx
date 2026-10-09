import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { CollaboratorTask, PreparationPackage } from "../../shared/types";
import type { WizardResponsePlan } from "./useCollaboratorWizard";
import { CollaboratorWizardPanel } from "./CollaboratorWizardPanel";

const packageProjection: PreparationPackage = {
  package_id: "package-1",
  case_id: "case-1",
  assignment_id: "assignment-1",
  dce_version_id: "dce-1",
  state: "A_REVIEW",
  aggregate_revision: 7,
  latest_readiness: {
    readiness_id: "readiness-1",
    revision: 2,
    state: "READY_WITH_WARNINGS",
    blocker_codes: [],
    warning_codes: ["OPTIONAL_REFERENCE_MISSING"],
    checked_requirement_count: 4,
    checked_task_count: 2,
  },
  generated_documents: [
    {
      document_id: "document-1",
      version: 1,
      document_kind: "TECHNICAL_RESPONSE",
      state: "GENERATED",
      readiness_revision: 2,
    },
  ],
  response_drafts: [
    {
      draft_id: "draft-1",
      version: 1,
      state: "DRAFT",
      section_codes: ["METHOD", "SOURCES"],
      source_refs: ["requirement-1"],
      responsible_role: "COLLABORATEUR",
    },
  ],
};

const task: CollaboratorTask = {
  task_id: "task-1",
  case_id: "case-1",
  assignment_id: "assignment-1",
  requirement_id: "requirement-1",
  task_kind: "EVIDENCE_COLLECTION",
  title: "Collecter la référence chantier",
  objective: "Structurer la preuve de référence",
  priority: "HIGH",
  state: "OPEN",
  due_at: null,
  aggregate_revision: 4,
};

const responsePlan: WizardResponsePlan = {
  loading: false,
  readState: "READY",
  requestState: "IDLE",
  draftRequestState: "IDLE",
  error: null,
  requirements: [{ requirement_id: "private-requirement-id", confirmation_revision: 1, requirement_type: "Méthodologie", directive_signal: "REQUIRED", confirmation_outcome: "CONFIRMED", uncertainty_status: "KNOWN", document_family: "CCTP", source_locator_label: "Article 4", source_anchor: null }],
  proposals: [{ proposal_id: "private-proposal-id", case_id: "case-1", assignment_id: "assignment-1", capability_id: "private-capability-id", capability_version_id: "private-version-id", requirement_id: "private-requirement-id", task_id: null, state: "PROPOSED", validity_state: "CURRENT", justification: "private justification", source_locator: "private locator", source_evidence_state: "UNKNOWN", source_evidence_evaluated_at: null }],
  candidates: [{ capability_id: "private-capability-id", capability_kind: "METHOD", name: "Méthodologie travaux", version_id: "private-version-id", version_number: 2, title: "Organisation de chantier", valid_from: "2026-10-01T00:00:00Z", valid_until: null, validity_state: "CURRENT", source_evidence_state: "UNKNOWN", evaluated_at: null }],
  items: [{ requirement_id: "private-requirement-id", section_code: "", source_proposal_id: null }],
  planId: null,
  hasPriorDcePlan: false,
  exactPlan: null,
  draftedPlanVersion: null,
};

function renderPanel(
  overrides: Partial<React.ComponentProps<typeof CollaboratorWizardPanel>> = {},
) {
  const props: React.ComponentProps<typeof CollaboratorWizardPanel> = {
    wizardCaseId: "case-1",
    wizardPackageId: "package-1",
    wizardPackage: null,
    wizardTasks: [],
    wizardTaskId: "",
    wizardResultText: "",
    wizardOutcome: "RECORDED",
    wizardSnapshotId: "",
    wizardTransmissionId: "",
    wizardSnapshotReceipt: null,
    wizardTransmissionReceipt: null,
    wizardSnapshotBusy: false,
    wizardTransmissionBusy: false,
    wizardSnapshotRetryPending: false,
    wizardTransmissionRetryPending: false,
    canCreateWizardSnapshot: false,
    canTransmitWizardSnapshot: false,
    wizardPreviewDocumentId: null,
    wizardPreviewContent: null,
    wizardDocumentBusy: false,
    wizardDocumentKind: "TECHNICAL_RESPONSE",
    wizardResponsePlan: responsePlan,
    canSaveWizardResponsePlan: false,
    isWizardResponsePlanCurrent: false,
    canCreateWizardResponseDraft: false,
    canRetryWizardResponseDraft: false,
    setWizardCaseId: vi.fn(),
    setWizardPackageId: vi.fn(),
    setWizardTaskId: vi.fn(),
    setWizardResultText: vi.fn(),
    setWizardOutcome: vi.fn(),
    setWizardSnapshotId: vi.fn(),
    setWizardTransmissionId: vi.fn(),
    setWizardDocumentKind: vi.fn(),
    onChangeResponsePlanItem: vi.fn(),
    onCreateResponsePlan: vi.fn(),
    onRetryResponsePlan: vi.fn(),
    onReadResponsePlan: vi.fn(),
    onLoad: vi.fn(),
    onClaimTask: vi.fn(),
    onRecordResult: vi.fn(),
    onCompleteTask: vi.fn(),
    onEvaluateReadiness: vi.fn(),
    onGenerateDocument: vi.fn(),
    onCreateResponseDraft: vi.fn(),
    onRetryResponseDraft: vi.fn(),
    onCreateSnapshot: vi.fn(),
    onTransmitSnapshot: vi.fn(),
    onPreviewDocument: vi.fn(),
    onDownloadDocument: vi.fn(),
    taskWorkflow: null,
    onLoadTaskWorkflow: vi.fn(),
    onCreateInformationRequest: vi.fn(),
    onRecordInformationResponse: vi.fn(),
    onDeclareTaskBlocker: vi.fn(),
    onResolveTaskBlocker: vi.fn(),
    ...overrides,
  };
  return render(<CollaboratorWizardPanel {...props} />);
}

describe("CollaboratorWizardPanel", () => {
  it("renders the non-financial empty state and delegates loading", () => {
    const onLoad = vi.fn();
    renderPanel({ onLoad });

    expect(screen.getByText("Le wizard est prêt à être chargé")).toBeInTheDocument();
    expect(screen.getByText(/Aucune donnée financière n’est exposée ici/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Charger le wizard/ }));
    expect(onLoad).toHaveBeenCalledTimes(1);
  });

  it("offers explicit snapshot creation and delegates the human action", () => {
    const onCreateSnapshot = vi.fn();
    renderPanel({
      wizardPackage: packageProjection,
      canCreateWizardSnapshot: true,
      onCreateSnapshot,
    });

    fireEvent.click(screen.getByRole("button", { name: "Créer le snapshot complet" }));

    expect(onCreateSnapshot).toHaveBeenCalledTimes(1);
  });

  it("renders readiness, generated document and task controls from server projections", () => {
    renderPanel({
      wizardPackage: packageProjection,
      wizardTasks: [task],
      wizardTaskId: "task-1",
    });

    expect(screen.getByText("Collecter la référence chantier")).toBeInTheDocument();
    expect(screen.getAllByText("READY_WITH_WARNINGS")).toHaveLength(2);
    expect(screen.getByText("OPTIONAL_REFERENCE_MISSING")).toBeInTheDocument();
    expect(screen.getByText("TECHNICAL_RESPONSE")).toBeInTheDocument();
    expect(screen.getAllByText("Plan de réponse").length).toBeGreaterThan(0);
    expect(screen.getByText("METHOD · SOURCES")).toBeInTheDocument();
    expect(screen.getByText("Enregistrer le résultat")).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "DC4" })).toBeInTheDocument();
  });

  it("shows human-readable DCE and capability choices while keeping identifiers and proof locators out of the UI", () => {
    renderPanel({ wizardPackage: packageProjection, wizardResponsePlan: responsePlan });

    expect(screen.getAllByText("Méthodologie").length).toBeGreaterThan(0);
    expect(screen.getByText(/Méthodologie travaux.*Organisation de chantier.*v2/)).toBeInTheDocument();
    expect(screen.queryByText(/private-(requirement|proposal|capability|version)-id|private justification|private locator/i)).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Créer le brouillon/ })).toBeDisabled();
  });

  it("records only the collaborator's explicit requirement-section and versioned-proposal choices", () => {
    const onChangeResponsePlanItem = vi.fn();
    renderPanel({ wizardPackage: packageProjection, wizardResponsePlan: responsePlan, onChangeResponsePlanItem });

    fireEvent.change(screen.getByLabelText("Section de réponse"), { target: { value: "METHOD" } });
    fireEvent.change(screen.getByLabelText("Proposition de capacité (facultatif)"), { target: { value: "private-proposal-id" } });

    expect(onChangeResponsePlanItem).toHaveBeenNthCalledWith(1, "private-requirement-id", { section_code: "METHOD" });
    expect(onChangeResponsePlanItem).toHaveBeenNthCalledWith(2, "private-requirement-id", { source_proposal_id: "private-proposal-id" });
  });

  it("requires a server-read SOURCES_CURRENT plan before enabling draft creation", () => {
    const currentPlan: WizardResponsePlan = {
      ...responsePlan,
      items: [{ requirement_id: "private-requirement-id", section_code: "METHOD", source_proposal_id: "private-proposal-id" }],
      exactPlan: {
        plan_id: "private-plan-id", version: 2, package_id: "package-1", dce_version_id: "dce-1", state: "SOURCES_CURRENT", plan_sha256: "a".repeat(64),
        content: { schema_version: 1, case_id: "case-1", package_id: "package-1", dce_version_id: "dce-1", items: [{ requirement_id: "private-requirement-id", requirement_state: "CONFIRMED", section_code: "METHOD", source_proposal_id: "private-proposal-id", source_capability_version_id: "private-version-id", source_validity_state: "CURRENT", source_evidence_state: "CURRENT" }] },
      },
    };
    renderPanel({ wizardPackage: packageProjection, wizardResponsePlan: currentPlan, isWizardResponsePlanCurrent: true, canCreateWizardResponseDraft: true });

    expect(screen.getAllByText("SOURCES_CURRENT").length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Révision 2/).length).toBeGreaterThan(0);
    expect(screen.getByRole("button", { name: /Créer le brouillon/ })).toBeEnabled();
    expect(screen.queryByText(/private-plan-id|private-proposal-id|a{20}/)).not.toBeInTheDocument();
  });

  it("shows UNKNOWN and offers only the exact retry after source-byte verification fails", () => {
    renderPanel({
      wizardPackage: packageProjection,
      wizardResponsePlan: { ...responsePlan, draftRequestState: "SOURCE_UNKNOWN", error: "RESPONSE_PLAN_UNKNOWN" },
      canRetryWizardResponseDraft: true,
    });

    expect(screen.getByText(/les octets d’une pièce sont indisponibles|leur hash discordant/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Réessayer la relecture de source" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Créer le brouillon de réponse/ })).toBeDisabled();
  });

  it("delegates document preview and download actions", () => {
    const onPreviewDocument = vi.fn();
    const onDownloadDocument = vi.fn();
    renderPanel({
      wizardPackage: packageProjection,
      onPreviewDocument,
      onDownloadDocument,
    });

    fireEvent.click(screen.getByRole("button", { name: "Aperçu" }));
    fireEvent.click(screen.getByRole("button", { name: "Télécharger" }));

    expect(onPreviewDocument).toHaveBeenCalledWith("document-1");
    expect(onDownloadDocument).toHaveBeenCalledWith("document-1");
  });

  it("renders the selected document preview without exposing storage metadata", () => {
    renderPanel({
      wizardPackage: packageProjection,
      wizardPreviewDocumentId: "document-1",
      wizardPreviewContent: "# Réponse technique\n\nContenu contrôlé",
    });

    expect(screen.getByRole("heading", { name: "Aperçu du document sélectionné" })).toBeInTheDocument();
    expect(screen.getByText(/# Réponse technique/)).toBeInTheDocument();
    expect(screen.queryByText(/storage_key|content_sha256/)).not.toBeInTheDocument();
  });

  it("renders the task workflow requests and blockers", () => {
    renderPanel({
      wizardPackage: packageProjection,
      wizardTaskId: "task-1",
      taskWorkflow: {
        task_id: "task-1",
        state: "BLOCKED",
        aggregate_revision: 5,
        information_requests: [{
          request_id: "request-1",
          task_id: "task-1",
          request_kind: "CLARIFICATION",
          subject: "Préciser le délai",
          question: "Quel délai faut-il confirmer ?",
          requested_object: "Délai",
          reason: "Le DCE est ambigu",
          priority: "HIGH",
          state: "OPEN",
          due_at: null,
          aggregate_revision: 5,
          responses: [],
        }],
        blockers: [{
          blocker_id: "blocker-1",
          task_id: "task-1",
          task_revision: 5,
          blocker_kind: "SOURCE_CONFLICT",
          description: "Contradiction entre deux sources",
          source_locator: "CCAP:12",
          resolution_owner: "PATRON_ADMIN",
          state: "OPEN",
          resolution_note: null,
          resolved_at: null,
        }],
      },
    });

    expect(screen.getByText("Préciser le délai")).toBeInTheDocument();
    expect(screen.getAllByText("SOURCE_CONFLICT")).toHaveLength(2);
    expect(screen.getByText(/1 demande\(s\)/)).toBeInTheDocument();
    expect(screen.getByText(/1 bloqueur\(s\) ouvert\(s\)/)).toBeInTheDocument();
  });

  it("delegates task, readiness and transmission actions without external deposit semantics", () => {
    const onClaimTask = vi.fn();
    const onRecordResult = vi.fn();
    const onCompleteTask = vi.fn();
    const onEvaluateReadiness = vi.fn();
    const onGenerateDocument = vi.fn();
    const onTransmitSnapshot = vi.fn();
    renderPanel({
      wizardPackage: packageProjection,
      wizardTasks: [task],
      wizardTaskId: "task-1",
      canTransmitWizardSnapshot: true,
      onClaimTask,
      onRecordResult,
      onCompleteTask,
      onEvaluateReadiness,
      onGenerateDocument,
      onTransmitSnapshot,
    });

    fireEvent.click(screen.getByRole("button", { name: "Prendre en charge" }));
    fireEvent.click(screen.getByRole("button", { name: "Enregistrer le résultat" }));
    fireEvent.click(screen.getByRole("button", { name: "Clôturer" }));
    fireEvent.click(screen.getByRole("button", { name: "Vérifier la complétude" }));
    fireEvent.click(screen.getByRole("button", { name: "Générer la réponse technique" }));
    fireEvent.click(screen.getByRole("button", { name: /Transmettre au patron/ }));

    expect(onClaimTask).toHaveBeenCalledTimes(1);
    expect(onRecordResult).toHaveBeenCalledTimes(1);
    expect(onCompleteTask).toHaveBeenCalledTimes(1);
    expect(onEvaluateReadiness).toHaveBeenCalledTimes(1);
    expect(onGenerateDocument).toHaveBeenCalledTimes(1);
    expect(onTransmitSnapshot).toHaveBeenCalledTimes(1);
    expect(screen.getByText(/ne dépose jamais le dossier sur un portail externe/)).toBeInTheDocument();
  });

  it("keeps a terrain capture local until the server confirms synchronization", async () => {
    const onRecordResult = vi.fn().mockResolvedValue(true);
    renderPanel({
      wizardPackage: packageProjection,
      wizardTasks: [task],
      wizardTaskId: "task-1",
      wizardResultText: "Photo de la zone de stockage.",
      onRecordResult,
    });

    fireEvent.click(screen.getByRole("button", { name: "Conserver localement" }));
    expect(screen.getByText(/Risque : perte possible/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Synchroniser la capture" }));

    await waitFor(() => expect(screen.getByText(/État :/)).toHaveTextContent("CONFIRMED"));
    expect(onRecordResult).toHaveBeenCalledTimes(1);
  });
});
