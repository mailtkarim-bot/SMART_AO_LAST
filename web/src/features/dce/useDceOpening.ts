import { useState } from "react";
import type { Dispatch, SetStateAction } from "react";

import type { ApiClient } from "../../infrastructure/api";
import type {
  AssignedCase,
  ConsultationProjection,
  DceDocumentInventory,
  DceProvenanceChannel,
  DceVersionMetadata,
} from "../../shared/types";

type Message = { tone: "success" | "error" | "warning"; text: string };
type SetMessage = Dispatch<SetStateAction<Message | null>>;

export type DceOpeningStep = "IDLE" | "PREPARING" | "UPLOADING" | "ADMITTING";

async function sha256Hex(data: BufferSource): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", data);
  return Array.from(new Uint8Array(digest))
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}

export function useDceOpening(
  api: ApiClient,
  setMessage: SetMessage,
  selectedCase: AssignedCase | undefined,
  onAdmitted: () => Promise<void> | void,
) {
  const [consultation, setConsultation] = useState<ConsultationProjection | null>(null);
  const [dceVersionMetadata, setDceVersionMetadata] = useState<DceVersionMetadata | null>(null);
  const [inventory, setInventory] = useState<DceDocumentInventory | null>(null);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [sourceChannel, setSourceChannel] = useState<DceProvenanceChannel>("MANUAL_UPLOAD");
  const [file, setFile] = useState<File | null>(null);
  const [step, setStep] = useState<DceOpeningStep>("IDLE");

  async function openSpace() {
    const consultationId = selectedCase?.consultation_id;
    if (!consultationId) {
      setConsultation(null);
      setDceVersionMetadata(null);
      setInventory(null);
      if (selectedCase) {
        setMessage({ tone: "warning", text: "Cette affaire n'est liée à aucune consultation. Aucune action possible." });
      }
      return;
    }
    setLoading(true);
    try {
      const projection = await api.getConsultation(consultationId);
      setConsultation(projection);
      const dceVersionId = selectedCase?.applicable_dce_version_id;
      if (dceVersionId) {
        const [metadata, documents] = await Promise.all([
          api.getDceVersion(dceVersionId),
          api.listDceVersionDocuments(dceVersionId),
        ]);
        setDceVersionMetadata(metadata);
        setInventory(documents);
      } else {
        setDceVersionMetadata(null);
        setInventory(null);
      }
    } catch (error) {
      setMessage({
        tone: "error",
        text: error instanceof Error ? error.message : "Impossible d'ouvrir l'espace DCE.",
      });
    } finally {
      setLoading(false);
    }
  }

  async function admitSelectedFile() {
    const consultationId = selectedCase?.consultation_id;
    if (!consultationId) {
      setMessage({ tone: "warning", text: "Cette affaire n'est liée à aucune consultation. Aucune action possible." });
      return;
    }
    if (!file) {
      setMessage({ tone: "warning", text: "Sélectionnez un document DCE à admettre." });
      return;
    }
    if (!consultation) {
      setMessage({ tone: "warning", text: "Ouvrez l'espace DCE avant d'admettre un document." });
      return;
    }
    setBusy(true);
    try {
      setStep("PREPARING");
      const bytes = new Uint8Array(await file.arrayBuffer());
      const fileHash = await sha256Hex(bytes);
      const expiresAt = new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString();
      const preparation = await api.prepareDceStaging({
        consultation_id: consultationId,
        consultation_revision: consultation.aggregate_revision,
        original_filename: file.name,
        expected_byte_size: file.size,
        source_channel: sourceChannel,
        expires_at: expiresAt,
      });
      if (preparation.replayed) {
        setMessage({ tone: "success", text: "Rejeu idempotent confirmé pour la préparation du staging." });
      }

      setStep("UPLOADING");
      const upload = await api.uploadDceStagedObjectContent(
        preparation.staging.storage_object_id,
        preparation.idempotency_key,
        file,
      );

      setStep("ADMITTING");
      const manifest = [fileHash].sort().join("\n");
      const corpusHash = await sha256Hex(new TextEncoder().encode(manifest));
      const dceVersionId = crypto.randomUUID();
      const admission = await api.registerDceVersion({
        dce_version_id: dceVersionId,
        consultation_id: consultationId,
        consultation_revision: consultation.aggregate_revision,
        corpus_hash: corpusHash,
        provenance_channel: sourceChannel,
        source_received_at: new Date().toISOString(),
        documents: [
          { document_id: crypto.randomUUID(), storage_object_id: upload.storage_object_id },
        ],
      });
      await api.linkCaseDceVersion(selectedCase.case_id, {
        dce_version_id: dceVersionId,
        reason: "Version DCE admise depuis l'espace DCE de l'affaire.",
      });
      if (admission.replayed) {
        setMessage({ tone: "success", text: "Rejeu idempotent confirmé pour l'admission de la version DCE." });
      }
      setMessage({
        tone: "success",
        text: `Document DCE admis : ${admission.result_code} · version ${admission.aggregate_refs[0]?.aggregate_revision ?? "nouvelle"}.`,
      });
      setFile(null);
      await onAdmitted();
      await openSpace();
    } catch (error) {
      const status = (error as { status?: number }).status;
      const detail = (error as { detail?: string }).detail;
      if (status === 409 && detail === "IDEMPOTENCY_KEY_REUSED") {
        setMessage({ tone: "warning", text: "Clé d'idempotence déjà utilisée. Rechargez l'espace DCE." });
      } else {
        setMessage({
          tone: "error",
          text: error instanceof Error ? error.message : "Admission du document impossible.",
        });
      }
    } finally {
      setBusy(false);
      setStep("IDLE");
    }
  }

  return {
    consultation,
    dceVersionMetadata,
    inventory,
    loading,
    busy,
    sourceChannel,
    file,
    step,
    setSourceChannel,
    setFile,
    openSpace,
    admitSelectedFile,
  };
}
