import { useState } from "react";
import type { Dispatch, SetStateAction } from "react";
import type { ApiClient } from "../../infrastructure/api";
import type {
  SubmissionEvidenceProjection,
  SubmissionMode,
  SubmissionPackageManifestProjection,
} from "../../shared/types";
import type { SubmissionEvidenceForm } from "./SubmissionPanel";

type Message = { tone: "success" | "error" | "warning"; text: string };
type SetMessage = Dispatch<SetStateAction<Message | null>>;

type SubmissionActions = {
  preparationPackageId: string;
  preparationRevision: string;
  submissionPackageId: string;
  submissionPackageVersion: string;
  submissionAuthorizationRationale: string;
  submissionMode: SubmissionMode;
  candidatureOnlyReason: string;
  submissionAuthorized: boolean;
  submissionManifest: SubmissionPackageManifestProjection | null;
  submissionEvidence: SubmissionEvidenceProjection[];
  submissionExported: boolean;
  submissionExportState: "IDLE" | "EXPORTED" | "UNKNOWN";
  signatureId: string;
  signaturePackageVersion: string;
  signatureStatus: "REQUESTED" | "SIGNED" | "REJECTED" | null;
  signatureProvider: string;
  signatureRevision: number | null;
  evidenceForm: SubmissionEvidenceForm;
  setPreparationPackageId: Dispatch<SetStateAction<string>>;
  setPreparationRevision: Dispatch<SetStateAction<string>>;
  setSubmissionPackageId: Dispatch<SetStateAction<string>>;
  setSubmissionPackageVersion: Dispatch<SetStateAction<string>>;
  setSubmissionAuthorizationRationale: Dispatch<SetStateAction<string>>;
  setSubmissionMode: Dispatch<SetStateAction<SubmissionMode>>;
  setCandidatureOnlyReason: Dispatch<SetStateAction<string>>;
  setSignatureId: Dispatch<SetStateAction<string>>;
  setSignaturePackageVersion: Dispatch<SetStateAction<string>>;
  setEvidenceForm: Dispatch<SetStateAction<SubmissionEvidenceForm>>;
  prepareSubmissionPackage: () => Promise<void>;
  authorizeSubmissionPackage: () => Promise<void>;
  loadSubmissionPackageManifest: () => Promise<void>;
  loadSubmissionEvidence: () => Promise<void>;
  requestSignature: () => Promise<void>;
  loadSignature: () => Promise<void>;
  exportSubmissionPackage: () => Promise<void>;
  recordSubmissionEvidence: () => Promise<void>;
};

export function useSubmissionActions(api: ApiClient, setMessage: SetMessage): SubmissionActions {
  const [preparationPackageId, setPreparationPackageId] = useState("");
  const [preparationRevision, setPreparationRevision] = useState("1");
  const [submissionPackageId, setSubmissionPackageId] = useState("");
  const [submissionPackageVersion, setSubmissionPackageVersion] = useState("1");
  const [submissionAuthorizationRationale, setSubmissionAuthorizationRationale] = useState(
    "Paquet relu et autorisé pour la remise humaine.",
  );
  const [submissionMode, setSubmissionMode] = useState<SubmissionMode>("FULL");
  const [candidatureOnlyReason, setCandidatureOnlyReason] = useState("");
  const [submissionAuthorized, setSubmissionAuthorized] = useState(false);
  const [submissionManifest, setSubmissionManifest] = useState<SubmissionPackageManifestProjection | null>(null);
  const [submissionEvidence, setSubmissionEvidence] = useState<SubmissionEvidenceProjection[]>([]);
  const [authorizationMetadata, setAuthorizationMetadata] = useState<{
    command_id: string;
    idempotency_key: string;
    authorization_id: string;
  } | null>(null);
  const [submissionExported, setSubmissionExported] = useState(false);
  const [submissionExportState, setSubmissionExportState] = useState<"IDLE" | "EXPORTED" | "UNKNOWN">("IDLE");
  const [signatureId, setSignatureId] = useState("");
  const [signaturePackageVersion, setSignaturePackageVersion] = useState("1");
  const [signatureStatus, setSignatureStatus] = useState<"REQUESTED" | "SIGNED" | "REJECTED" | null>(null);
  const [signatureProvider, setSignatureProvider] = useState("");
  const [signatureRevision, setSignatureRevision] = useState<number | null>(null);
  const [evidenceForm, setEvidenceForm] = useState<SubmissionEvidenceForm>({
    evidence_type: "MANUAL_RECEIPT",
    external_reference_hash: "",
    evidence_sha256: "",
    notes_redacted: "",
  });

  async function prepareSubmissionPackage() {
    if (!preparationPackageId.trim()) {
      setMessage({ tone: "error", text: "Renseignez l’identifiant de la préparation à déposer." });
      return;
    }
    const reason = candidatureOnlyReason.trim();
    if (submissionMode === "CANDIDATURE_ONLY" && !reason) {
      setMessage({ tone: "error", text: "Justifiez la candidature seule avant de préparer le paquet." });
      return;
    }
    try {
      const receipt = await api.prepareSubmissionPackage(
        preparationPackageId.trim(),
        Number(preparationRevision),
        {
          submission_mode: submissionMode,
          candidature_only_reason: submissionMode === "CANDIDATURE_ONLY" ? reason : undefined,
        },
      );
      const packageId = receipt.aggregate_refs[0]?.aggregate_id;
      if (packageId) {
        if (packageId !== submissionPackageId.trim()) {
          setSubmissionAuthorized(false);
          setSubmissionManifest(null);
          setSubmissionEvidence([]);
          setAuthorizationMetadata(null);
          setSubmissionExported(false);
          setSubmissionExportState("IDLE");
        }
        setSubmissionPackageId(packageId);
      }
      setMessage({
        tone: "success",
        text: receipt.replayed
          ? "Paquet de dépôt déjà préparé, identifiant rechargé."
          : "Paquet préparé pour contrôle patronal. Aucun dépôt externe n’a été effectué.",
      });
    } catch (error) {
      setMessage({ tone: "error", text: error instanceof Error ? error.message : "Impossible de préparer le paquet." });
    }
  }

  async function loadSubmissionPackageManifest() {
    if (!submissionPackageId.trim()) {
      setMessage({ tone: "error", text: "Préparez ou renseignez un paquet avant de prévisualiser son manifeste." });
      return;
    }
    try {
      const projection = await api.getSubmissionPackageManifest(submissionPackageId.trim());
      setSubmissionManifest(projection);
      setSubmissionPackageVersion(String(projection.package_version));
      setSubmissionAuthorized(projection.authorization_status === "AUTHORIZED");
      setMessage({ tone: "success", text: "Manifeste exact rechargé. Les exclusions et l’état P5 sont visibles." });
    } catch (error) {
      setMessage({ tone: "error", text: error instanceof Error ? error.message : "Impossible de lire le manifeste." });
    }
  }

  async function authorizeSubmissionPackage() {
    if (!submissionPackageId.trim()) {
      setMessage({ tone: "error", text: "Préparez ou renseignez un paquet avant de l’autoriser." });
      return;
    }
    const expectedVersion = Number(submissionPackageVersion);
    if (!Number.isInteger(expectedVersion) || expectedVersion < 1) {
      setMessage({ tone: "error", text: "La version du paquet doit être un entier positif." });
      return;
    }
    const rationale = submissionAuthorizationRationale.trim();
    if (!rationale) {
      setMessage({ tone: "error", text: "Saisissez la justification de l’autorisation P5." });
      return;
    }
    const metadata = authorizationMetadata ?? {
      command_id: crypto.randomUUID(),
      idempotency_key: crypto.randomUUID(),
      authorization_id: crypto.randomUUID(),
    };
    if (authorizationMetadata === null) setAuthorizationMetadata(metadata);
    try {
      const receipt = await api.authorizeSubmissionPackage(
        submissionPackageId.trim(),
        expectedVersion,
        rationale,
        metadata,
      );
      setSubmissionAuthorized(true);
      setMessage({
        tone: "success",
        text: receipt.replayed
          ? "Autorisation P5 déjà enregistrée; état rechargé."
          : "Paquet autorisé pour remise humaine. Aucun dépôt externe n’a été effectué.",
      });
    } catch (error) {
      setMessage({ tone: "error", text: error instanceof Error ? error.message : "Impossible d’autoriser le paquet." });
    }
  }

  async function loadSubmissionEvidence() {
    if (!submissionPackageId.trim()) {
      setMessage({ tone: "error", text: "Préparez ou renseignez un paquet avant de relire ses preuves." });
      return;
    }
    try {
      const projection = await api.getSubmissionEvidence(submissionPackageId.trim());
      setSubmissionEvidence(projection);
      setMessage({ tone: "success", text: "Preuves de réception rechargées. Le rapprochement reste explicitement partiel." });
    } catch (error) {
      setMessage({ tone: "error", text: error instanceof Error ? error.message : "Impossible de lire les preuves." });
    }
  }

  async function exportSubmissionPackage() {
    if (!submissionPackageId.trim()) {
      setMessage({ tone: "error", text: "Préparez ou renseignez un paquet avant de l’exporter." });
      return;
    }
    try {
      const archive = await api.downloadSubmissionPackage(submissionPackageId.trim());
      const url = URL.createObjectURL(archive);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `submission-${submissionPackageId.trim()}.zip`;
      anchor.click();
      URL.revokeObjectURL(url);
      setSubmissionExported(true);
      setSubmissionExportState("EXPORTED");
      setMessage({ tone: "success", text: "Dossier exporté. L’audit et la notification de téléchargement ont été enregistrés." });
    } catch (error) {
      const status = error instanceof Error ? (error as Error & { status?: number }).status : undefined;
      if (typeof status !== "number") {
        setSubmissionExportState("UNKNOWN");
        setMessage({
          tone: "warning",
          text: "Résultat de l’export non confirmé. Vérifiez l’état avant toute nouvelle tentative.",
        });
      } else {
        setMessage({ tone: "error", text: error instanceof Error ? error.message : "Impossible d’exporter le dossier." });
      }
    }
  }

  async function requestSignature() {
    if (!submissionPackageId.trim()) {
      setMessage({ tone: "error", text: "Préparez ou renseignez un paquet avant de demander sa signature." });
      return;
    }
    const expectedVersion = Number(signaturePackageVersion);
    if (!Number.isInteger(expectedVersion) || expectedVersion < 1) {
      setMessage({ tone: "error", text: "La révision du paquet doit être un entier positif." });
      return;
    }
    try {
      const receipt = await api.requestSubmissionSignature(submissionPackageId.trim(), expectedVersion);
      const nextSignatureId = receipt.aggregate_refs[0]?.aggregate_id;
      if (nextSignatureId) setSignatureId(nextSignatureId);
      setSignatureStatus("REQUESTED");
      setSignatureRevision(1);
      setMessage({
        tone: "success",
        text: receipt.replayed
          ? "Demande de signature déjà enregistrée; état rechargé."
          : "Demande de signature enregistrée. Aucun dépôt externe n’a été effectué.",
      });
    } catch (error) {
      setMessage({ tone: "error", text: error instanceof Error ? error.message : "Impossible de demander la signature." });
    }
  }

  async function loadSignature() {
    if (!signatureId.trim()) {
      setMessage({ tone: "error", text: "Renseignez l’identifiant de signature à consulter." });
      return;
    }
    try {
      const projection = await api.getSubmissionSignature(signatureId.trim());
      setSignatureId(projection.signature_id);
      setSignatureStatus(projection.status);
      setSignatureProvider(projection.provider);
      setSignaturePackageVersion(String(projection.expected_package_version));
      setSignatureRevision(projection.revision);
      setMessage({ tone: "success", text: "État de signature rechargé. Le dépôt externe reste non effectué." });
    } catch (error) {
      setMessage({ tone: "error", text: error instanceof Error ? error.message : "Impossible de lire l’état de signature." });
    }
  }

  async function recordSubmissionEvidence() {
    if (!submissionPackageId.trim()) {
      setMessage({ tone: "error", text: "Préparez ou renseignez un paquet avant d’enregistrer sa preuve." });
      return;
    }
    try {
      const receipt = await api.recordSubmissionEvidence(submissionPackageId.trim(), {
        ...evidenceForm,
        notes_redacted: evidenceForm.notes_redacted || undefined,
      });
      setMessage({
        tone: "success",
        text: receipt.external_submission === "NOT_PERFORMED"
          ? "Preuve append-only enregistrée. Le dépôt externe reste à effectuer manuellement."
          : "Preuve enregistrée.",
      });
    } catch (error) {
      setMessage({ tone: "error", text: error instanceof Error ? error.message : "Impossible d’enregistrer la preuve." });
    }
  }

  return {
    preparationPackageId,
    preparationRevision,
    submissionPackageId,
    submissionPackageVersion,
    submissionAuthorizationRationale,
    submissionMode,
    candidatureOnlyReason,
    submissionAuthorized,
    submissionManifest,
    submissionEvidence,
    submissionExported,
    submissionExportState,
    signatureId,
    signaturePackageVersion,
    signatureStatus,
    signatureProvider,
    signatureRevision,
    evidenceForm,
    setPreparationPackageId,
    setPreparationRevision,
    setSubmissionPackageId,
    setSubmissionPackageVersion,
    setSubmissionAuthorizationRationale,
    setSubmissionMode,
    setCandidatureOnlyReason,
    setSignatureId,
    setSignaturePackageVersion,
    setEvidenceForm,
    prepareSubmissionPackage,
    authorizeSubmissionPackage,
    loadSubmissionPackageManifest,
    loadSubmissionEvidence,
    requestSignature,
    loadSignature,
    exportSubmissionPackage,
    recordSubmissionEvidence,
  };
}
