import type { ComponentProps } from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { SubmissionPanel } from "./SubmissionPanel";

type PanelProps = ComponentProps<typeof SubmissionPanel>;

const evidenceForm: PanelProps["evidenceForm"] = {
  evidence_type: "MANUAL_RECEIPT",
  external_reference_hash: "a".repeat(64),
  evidence_sha256: "b".repeat(64),
  notes_redacted: "Preuve de recette expurgée",
};

function renderPanel(overrides: Partial<PanelProps> = {}) {
  const props: PanelProps = {
    preparationPackageId: "preparation-1",
    preparationRevision: "1",
    submissionPackageId: "",
    submissionPackageVersion: "1",
    submissionAuthorizationRationale: "Paquet relu et autorisé pour la remise humaine.",
    submissionMode: "FULL",
    candidatureOnlyReason: "",
    submissionAuthorized: false,
    submissionManifest: null,
    submissionEvidence: [],
    submissionExported: false,
    submissionExportState: "IDLE",
    signatureId: "",
    signaturePackageVersion: "1",
    signatureStatus: null,
    signatureProvider: "",
    signatureRevision: null,
    evidenceForm,
    setPreparationPackageId: vi.fn(),
    setPreparationRevision: vi.fn(),
    setSubmissionPackageId: vi.fn(),
    setSubmissionPackageVersion: vi.fn(),
    setSubmissionAuthorizationRationale: vi.fn(),
    setSubmissionMode: vi.fn(),
    setCandidatureOnlyReason: vi.fn(),
    setSignatureId: vi.fn(),
    setSignaturePackageVersion: vi.fn(),
    setEvidenceForm: vi.fn(),
    onPrepare: vi.fn(),
    onAuthorize: vi.fn(),
    onLoadManifest: vi.fn(),
    onLoadEvidence: vi.fn(),
    onRequestSignature: vi.fn(),
    onLoadSignature: vi.fn(),
    onExport: vi.fn(),
    onRecordEvidence: vi.fn(),
    ...overrides,
  };
  return { ...render(<SubmissionPanel {...props} />), props };
}

describe("SubmissionPanel integration", () => {
  it("prepares a patron package and keeps external submission explicitly disabled", () => {
    const onPrepare = vi.fn();
    renderPanel({ onPrepare });

    expect(screen.getByText("Dépôt externe non effectué")).toBeInTheDocument();
    expect(screen.getAllByText("external_submission: NOT_PERFORMED")).toHaveLength(2);

    fireEvent.click(screen.getByRole("button", { name: /préparer le paquet/i }));
    expect(onPrepare).toHaveBeenCalledOnce();
    expect(screen.queryByRole("button", { name: /exporter le dossier zip/i })).not.toBeInTheDocument();
  });

  it("exposes an explicit reason before preparing a candidature-only package", () => {
    const setSubmissionMode = vi.fn();
    const setCandidatureOnlyReason = vi.fn();
    renderPanel({ submissionMode: "CANDIDATURE_ONLY", setSubmissionMode, setCandidatureOnlyReason });

    fireEvent.change(screen.getByLabelText("Mode de remise"), {
      target: { value: "CANDIDATURE_ONLY" },
    });
    fireEvent.change(screen.getByLabelText("Justification de la candidature seule"), {
      target: { value: "Pièces financières non disponibles à la date de dépôt." },
    });

    expect(setSubmissionMode).toHaveBeenCalledWith("CANDIDATURE_ONLY");
    expect(setCandidatureOnlyReason).toHaveBeenCalledWith("Pièces financières non disponibles à la date de dépôt.");
  });

  it("reveals the audited export action only after a package exists", () => {
    const onExport = vi.fn();
    const { rerender, props } = renderPanel({
      submissionPackageId: "submission-1",
      submissionAuthorized: true,
      submissionExported: true,
      onExport,
    });

    rerender(<SubmissionPanel {...props} submissionPackageId="submission-1" submissionExported />);
    fireEvent.click(screen.getByRole("button", { name: /exporter le dossier zip/i }));

    expect(onExport).toHaveBeenCalledOnce();
    expect(screen.getByText("Export audité")).toBeInTheDocument();
  });

  it("shows a bounded signature status and delegates patron actions", () => {
    const onRequestSignature = vi.fn();
    const onLoadSignature = vi.fn();
    renderPanel({
      signatureId: "signature-1",
      signatureStatus: "SIGNED",
      signatureProvider: "TEST_PROVIDER",
      signatureRevision: 2,
      onRequestSignature,
      onLoadSignature,
    });

    expect(screen.getByText("Signature électronique")).toBeInTheDocument();
    expect(screen.getByText("SIGNED")).toBeInTheDocument();
    expect(screen.getByText("Provider : TEST_PROVIDER")).toBeInTheDocument();
    expect(screen.getByText("Révision signature : 2")).toBeInTheDocument();
    expect(screen.getAllByText("external_submission: NOT_PERFORMED")).toHaveLength(2);
    expect(screen.queryByText(/provider_reference_hash|signature_sha256/i)).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /demander la signature/i }));
    fireEvent.click(screen.getByRole("button", { name: /recharger l’état/i }));
    expect(onRequestSignature).toHaveBeenCalledOnce();
    expect(onLoadSignature).toHaveBeenCalledOnce();
  });

  it("requires P5 authorization before revealing the export action", () => {
    const onAuthorize = vi.fn();
    const { rerender, props } = renderPanel({
      submissionPackageId: "submission-1",
      onAuthorize,
    });

    expect(screen.getByText("Autorisation P5")).toBeInTheDocument();
    expect(screen.getByLabelText("Version du paquet")).toHaveValue(1);
    expect(screen.queryByRole("button", { name: /exporter le dossier zip/i })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /autoriser la remise humaine/i }));
    expect(onAuthorize).toHaveBeenCalledOnce();

    rerender(
      <SubmissionPanel
        {...props}
        submissionPackageId="submission-1"
        submissionAuthorized
      />,
    );
    expect(screen.getByRole("button", { name: /exporter le dossier zip/i })).toBeInTheDocument();
  });

  it("shows the exact manifest preview and delegates its reload", () => {
    const onLoadManifest = vi.fn();
    renderPanel({
      submissionPackageId: "submission-1",
      onLoadManifest,
      submissionManifest: {
        submission_package_id: "submission-1",
        package_version: 3,
        state: "PRET_CONTROLE",
        manifest_sha256: "c".repeat(64),
        manifest: {
          entries: [{ path: "dce/index.pdf" }],
          scope: { kind: "SINGLE_LOT", lot_numbers: ["01"] },
          exclusions: ["private_storage", "financial_amounts", "external_submission_result"],
        },
        authorization_status: "NOT_AUTHORIZED",
        external_submission: "NOT_PERFORMED",
      },
    });

    fireEvent.click(screen.getByRole("button", { name: /prévisualiser le manifeste/i }));

    expect(onLoadManifest).toHaveBeenCalledOnce();
    expect(screen.getByText("Manifeste exact · v3")).toBeInTheDocument();
    expect(screen.getByText(/1 entrée\(s\) partagée\(s\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Périmètre gelé.*SINGLE_LOT/i)).toBeInTheDocument();
    expect(screen.getByText(/P5 à autoriser/i)).toBeInTheDocument();
    expect(screen.getByText(/Exclus : private_storage, financial_amounts, external_submission_result/i)).toBeInTheDocument();
  });

  it("records only the redacted manual evidence action", () => {
    const onRecordEvidence = vi.fn();
    const setEvidenceForm = vi.fn();
    renderPanel({ onRecordEvidence, setEvidenceForm });

    fireEvent.change(screen.getByLabelText("Type de preuve"), {
      target: { value: "MANUAL_PORTAL_REFERENCE" },
    });
    fireEvent.change(screen.getByLabelText("Notes expurgées"), {
      target: { value: "Référence sans données sensibles" },
    });
    fireEvent.click(screen.getByRole("button", { name: /enregistrer la preuve/i }));

    expect(setEvidenceForm).toHaveBeenCalled();
    expect(onRecordEvidence).toHaveBeenCalledOnce();
    expect(screen.getByPlaceholderText("Aucune donnée sensible")).toBeInTheDocument();
  });

  it("shows partial receipt evidence without claiming external success", () => {
    const onLoadEvidence = vi.fn();
    renderPanel({
      submissionPackageId: "submission-1",
      onLoadEvidence,
      submissionEvidence: [{
        evidence_id: "evidence-1",
        submission_package_id: "submission-1",
        package_version: 3,
        manifest_sha256: "c".repeat(64),
        evidence_type: "MANUAL_RECEIPT",
        status: "RECEIVED",
        reconciliation_status: "PARTIAL",
        external_submission: "NOT_PERFORMED",
      }],
    });

    fireEvent.click(screen.getByRole("button", { name: /relire les preuves/i }));

    expect(onLoadEvidence).toHaveBeenCalledOnce();
    expect(screen.getByText("Réception partielle · v3")).toBeInTheDocument();
    expect(screen.getByText(/Rapprochement incomplet/i)).toBeInTheDocument();
  });
});
