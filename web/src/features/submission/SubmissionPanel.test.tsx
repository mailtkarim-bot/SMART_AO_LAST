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
    finalControl: null, onLoadFinalControl: vi.fn(), signatureConfirmed: false,
    setSignatureConfirmed: vi.fn(), signatureRationale: "", setSignatureRationale: vi.fn(),
    signatureBusy: false, signatureIntent: null,
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
      signatureConfirmed: true,
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

it('exposes each selected annex and hash without inferring P5 authorization or signature',()=>{
 renderPanel({submissionPackageId:'submission-1',submissionManifest:{submission_package_id:'submission-1',package_version:3,state:'PRET_CONTROLE',manifest_sha256:'c'.repeat(64),authorization_status:'NOT_AUTHORIZED',external_submission:'NOT_PERFORMED',manifest:{entries:[{kind:'SOURCE_ANNEX',archive_path:'annexes/proof-1.pdf',document_id:'proof-1',sha256:'b'.repeat(64),requirement_ids:['req-1'],signature:'UNKNOWN'}]}}});
 expect(screen.getByText(/Annexe incluse dans le paquet exact.*annexes\/proof-1.pdf/)).toBeInTheDocument();
 expect(screen.getByText(/Document proof-1.*SHA-256/)).toHaveTextContent('b'.repeat(64));
 expect(screen.getByText(/Exigences.*req-1.*Signature.*UNKNOWN/)).toBeInTheDocument();
 expect(screen.getByText(/P5 à autoriser/)).toBeInTheDocument();
});

it('shows final-control gaps independently of a recorded signature and P5', () => {
  renderPanel({
    submissionPackageId: 'submission-1',
    finalControl: {
      submission_package_id: 'submission-1', package_version: 3, manifest_sha256: 'd'.repeat(64),
      dce_version_id: 'dce-1', state: 'PARTIAL', source_state: 'CURRENT',
      local_delivery_mode: 'LOCAL_ZIP', buyer_formats_state: 'OBSERVATIONS_AVAILABLE',
      format_comparisons: [{requirement_id:'format-rule-1',source_excerpt:'Le mémoire technique doit être remis au format PDF.',
        source_locator:'RC · ligne 10',source_anchor:{source_sha256:'d'.repeat(64)},confirmation:'CONFIRMED',
        scope:'TECHNICAL_RESPONSE',requested:'PDF',files:[],state:'OBSERVED_MISMATCH',reason_code:'MIME_DIFFERS',
        applicability:'UNKNOWN',conformity:'UNKNOWN'},
        {requirement_id:'format-rule-2',source_excerpt:'Le format PDF est obligatoire.',source_locator:'RC · ligne 12',
        source_anchor:null,confirmation:'CONFIRMED',scope:'UNSPECIFIED',requested:'PDF',files:[],
        state:'UNKNOWN',reason_code:'TARGET_SCOPE_UNKNOWN',applicability:'UNKNOWN',conformity:'UNKNOWN'}],
      buyer_names_sizes_state:'OBSERVATIONS_AVAILABLE',
      name_size_comparisons:[{requirement_id:'name-rule-1',source_excerpt:'Le mémoire technique doit être nommé «Memoire.pdf».',
        source_locator:'RC · ligne 20',source_anchor:{source_sha256:'e'.repeat(64)},confirmation:'CONFIRMED',
        scope:'TECHNICAL_RESPONSE',criterion:'EXACT_NAME',requested_name:'Memoire.pdf',max_bytes:null,
        files:[{archive_path:'technical-response.md',document_id:'document-1',sha256:'a'.repeat(64),byte_size:42,
          requirement_ids:[],presence:'VERIFIED_SOURCE',signature:'UNKNOWN'}],
        state:'OBSERVED_MISMATCH',reason_code:'NAME_DIFFERS',applicability:'UNKNOWN',conformity:'UNKNOWN'},
        {requirement_id:'size-rule-1',source_excerpt:'La taille du KBIS ne doit pas dépasser 10 Mo.',
         source_locator:'RC · ligne 21',source_anchor:null,confirmation:'CONFIRMED',scope:'UNSPECIFIED',
         criterion:'UNKNOWN',requested_name:null,max_bytes:null,files:[],state:'UNKNOWN',
         reason_code:'SIZE_UNIT_UNKNOWN',applicability:'UNKNOWN',conformity:'UNKNOWN'}],
      files: [{ archive_path: 'technical-response.md', document_id: 'document-1', sha256: 'a'.repeat(64),
        byte_size: null, requirement_ids: [], presence: 'VERIFIED_SOURCE', signature: 'UNKNOWN' },
        {archive_path:'annexes/kbis.pdf',document_id:'kbis-1',sha256:'b'.repeat(64),byte_size:50,
         requirement_ids:['requirement-1'],presence:'VERIFIED_SOURCE',signature:'UNKNOWN',
         document_kind:'KBIS',media_type:'application/pdf',validity:'UNKNOWN'}],
      requirements: [{ requirement_id: 'requirement-1', document_family: 'RC', source_state: 'CURRENT',
        confirmation: 'CONFIRMED', source_locator: 'page:2', source_anchor: null, source_excerpt: 'Joindre une attestation.',
        lot_candidates: [1], applicability: 'UNKNOWN', coverage: 'UNKNOWN', signature: 'UNKNOWN',
        response_state: 'MISSING', pieces: [] }],
      missing_cited_annexes: [], entries_without_exported_file: ['OFFICIAL_PRICING_VERSION'],
      patron_review_ids: ['review-1'], p5_authorization_status: 'RECORDED', p5_authorization_id: 'p5-1',
      signature_visibility: 'RESTRICTED', signature_records: [],
      inventory: 'CURRENT_NON_FINANCIAL_SIGNALS_ONLY', signature_requirement: 'UNKNOWN',
      signature_verification: 'UNKNOWN', signer_authority: 'UNKNOWN', conformity: 'UNKNOWN',
      external_submission: 'NOT_PERFORMED',
    },
  });
  expect(screen.getByRole('heading', { name: 'Contrôle final du pli exact' })).toBeInTheDocument();
  expect(screen.getByText('Joindre une attestation.')).toBeInTheDocument();
  expect(screen.getByText(/Nature : KBIS/)).toBeInTheDocument();
  expect(screen.getByRole('heading',{name:'Formats demandés et pli exact'})).toBeInTheDocument();
  expect(screen.getByRole('heading',{name:'Noms et tailles des fichiers'})).toBeInTheDocument();
  expect(screen.getByText(/Nom demandé : Memoire.pdf/)).toBeInTheDocument();
  expect(screen.getByText(/Unité de taille ambiguë/)).toBeInTheDocument();
  expect(screen.getByText(/Nom exporté : technical-response.md · Taille : 42 octets/)).toBeInTheDocument();
  expect(screen.getByText('Le mémoire technique doit être remis au format PDF.')).toBeInTheDocument();
  expect(screen.getAllByText(/Écart observé/)).toHaveLength(2);
  expect(screen.getByText(/Portée de la demande non établie/)).toBeInTheDocument();
  expect(screen.getByText(/Format : PDF/)).toBeInTheDocument();
  expect(screen.getAllByText(/Validité : UNKNOWN/).length).toBeGreaterThan(0);
  expect(screen.getByText(/Réponse manquante/)).toBeInTheDocument();
  expect(screen.getByText(/Validité cryptographique : UNKNOWN/)).toBeInTheDocument();
  expect(screen.getByText(/Référence sans fichier exporté : OFFICIAL_PRICING_VERSION/)).toBeInTheDocument();
});
