import { useLayoutEffect, useRef, useState } from "react";
import type { Dispatch, SetStateAction } from "react";
import type { ApiClient } from "../../infrastructure/api";
import type { AssignedCase, ConsultationProjection, DceDocumentInventory, DceProvenanceChannel, DceVersionMetadata, RegisterDceVersionInput, LinkCaseDceVersionInput } from "../../shared/types";

type Message = { tone: "success" | "error" | "warning"; text: string };
type SetMessage = Dispatch<SetStateAction<Message | null>>;
export type DceOpeningStep = "IDLE" | "PREPARING" | "UPLOADING" | "ADMITTING";
type Snapshot = { key: string; consultation: ConsultationProjection; metadata: DceVersionMetadata | null; inventory: DceDocumentInventory | null };
type SourceUpload = {
  file: File;
  documentId: string;
  prepare: Parameters<ApiClient["prepareDceStaging"]>[0];
  preparation?: Awaited<ReturnType<ApiClient["prepareDceStaging"]>>;
  upload?: Awaited<ReturnType<ApiClient["uploadDceStagedObjectContent"]>>;
};
type Intent = {
  sources: SourceUpload[];
  target: AssignedCase;
  admission: RegisterDceVersionInput;
  link: LinkCaseDceVersionInput;
  admitted?: Awaited<ReturnType<ApiClient["registerDceVersion"]>>;
  linked?: boolean;
};
async function sha256Hex(data: BufferSource) {
  return Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", data))).map(b => b.toString(16).padStart(2, "0")).join("");
}

export function useDceOpening(api: ApiClient, setMessage: SetMessage, selectedCase: AssignedCase | undefined, onAdmitted: () => Promise<void> | void, ownerKey = "legacy") {
  const caseKey = JSON.stringify([ownerKey, selectedCase?.case_id]);
  const keyFor = (target: AssignedCase | undefined) => JSON.stringify([ownerKey, target?.case_id, target?.consultation_id, target?.applicable_dce_version_id, target?.dce_availability]);
  const resourceKey = keyFor(selectedCase);
  const active = useRef({ caseKey, resourceKey });
  const readRequest = useRef<{ key: string } | null>(null);
  const sending = useRef(new Set<string>());
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [loadingKey, setLoadingKey] = useState<string | null>(null);
  const [busyKey, setBusyKey] = useState<string | null>(null);
  const [intents, setIntents] = useState<Record<string, Intent | null>>({});
  const pending = intents[caseKey] ?? null;
  const [channelEntry, setChannel] = useState<{key: string; value: DceProvenanceChannel} | null>(null);
  const sourceChannel: DceProvenanceChannel = channelEntry?.key === caseKey ? channelEntry.value : "MANUAL_UPLOAD";
  const [fileEntry, setFileEntry] = useState<{ key: string; files: File[]; selection: number } | null>(null);
  const files = fileEntry?.key === caseKey ? fileEntry.files : [];
  const file = files[0] ?? null;
  const [step, setStep] = useState<DceOpeningStep>("IDLE");
  const [reasonEntry, setReasonEntry] = useState<{key: string; value: string} | null>(null);
  const replacementReason = reasonEntry?.key === caseKey ? reasonEntry.value : "";
  function setReplacementReason(value: string) {
    if (!pending && !sending.current.has(caseKey)) setReasonEntry({key: caseKey, value});
  }
  const [confirmationKey, setConfirmationKey] = useState("");
  const confirmationIntent = JSON.stringify([resourceKey, files.map(item => [item.name, item.size, item.lastModified]), fileEntry?.selection, sourceChannel, replacementReason]);
  const replacementConfirmed = confirmationKey === confirmationIntent;
  const current = snapshot?.key === resourceKey ? snapshot : null;
  useLayoutEffect(() => {
    active.current = { caseKey, resourceKey };
    if (readRequest.current?.key !== resourceKey) readRequest.current = null;
  }, [caseKey, resourceKey]);
  useLayoutEffect(() => () => { readRequest.current = null; active.current = { caseKey: "", resourceKey: "" }; }, []);

  function setFiles(value: File[]) {
    if (!pending && !sending.current.has(caseKey)) setFileEntry(current => ({ key: caseKey, files: [...value], selection: (current?.selection ?? 0) + 1 }));
  }
  function setFile(value: File | null) { setFiles(value ? [value] : []); }
  function setSourceChannel(value: DceProvenanceChannel) { if (!pending && !sending.current.has(caseKey)) setChannel({key: caseKey, value}); }
  const store = (value: Intent | null) => setIntents(current => ({ ...current, [caseKey]: value }));

  async function load(target: AssignedCase) {
    const key = keyFor(target), request = { key };
    readRequest.current = request;
    setSnapshot(null);
    setLoadingKey(key);
    try {
      const consultation = await api.getConsultation(target.consultation_id!);
      if (readRequest.current !== request || active.current.caseKey !== caseKey) return false;
      if (consultation.id !== target.consultation_id) throw new Error("Référence consultation discordante.");
      const version = target.applicable_dce_version_id;
      const [metadata, inventory] = version ? await Promise.all([api.getDceVersion(version), api.listDceVersionDocuments(version)]) : [null, null];
      if (metadata && (metadata.id !== version || metadata.consultation_id !== consultation.id || inventory?.dce_version_id !== version)) throw new Error("Inventaire de version discordant ; aucune source présentée comme courante.");
      if (readRequest.current === request && active.current.caseKey === caseKey) {
        setSnapshot({ key, consultation, metadata, inventory });
        return true;
      }
      return false;
    } catch (error) {
      if (readRequest.current !== request || active.current.caseKey !== caseKey) return false;
      setSnapshot(null);
      setMessage({ tone: "error", text: error instanceof Error ? error.message : "Impossible d’ouvrir l’espace DCE." });
      return false;
    } finally { if (readRequest.current === request) setLoadingKey(null); }
  }
  async function openSpace() {
    if (pending || sending.current.has(caseKey)) return;
    if (!selectedCase?.consultation_id) {
      setSnapshot(null);
      if (selectedCase) setMessage({ tone: "warning", text: "Cette affaire n'est liée à aucune consultation. Aucune action possible." });
      return;
    }
    await load(selectedCase);
  }

  async function admitSelectedFile() {
    if (sending.current.has(caseKey)) return;
    if (!pending && (!selectedCase?.consultation_id || !file || !current)) {
      setMessage({ tone: "warning", text: !selectedCase?.consultation_id ? "Cette affaire n'est liée à aucune consultation. Aucune action possible." : !file ? "Sélectionnez un document DCE à admettre." : "Ouvrez l'espace DCE avant d'admettre un document." });
      return;
    }
    if (!pending && sourceChannel === "RECTIFICATION" && (!replacementConfirmed || !replacementReason.trim() || !current?.metadata || current.metadata.lifecycle !== "ADMITTED")) {
      setMessage({ tone: "warning", text: "Confirmez le prédécesseur exact et le motif du rectificatif." });
      return;
    }
    sending.current.add(caseKey); setBusyKey(caseKey);
    let intent = pending;
    try {
      if (!intent) {
        const target = selectedCase!;
        if (files.length > 100 || files.some(item => item.size > 150_000_000 || item.size === 0)) {
          throw new Error("Limite locale : 100 fichiers, 150 Mo par fichier, aucun fichier vide. Aucun envoi effectué.");
        }
        const hashes: string[] = [];
        for (const source of files) hashes.push(await sha256Hex(new Uint8Array(await source.arrayBuffer())));
        if (new Set(hashes).size !== hashes.length) throw new Error("Deux fichiers ont les mêmes octets ; retirez explicitement le doublon avant admission.");
        const corpusHash = await sha256Hex(new TextEncoder().encode(hashes.sort().join("\n")));
        if (active.current.caseKey !== caseKey) return;
        const ids = () => ({ command_id: crypto.randomUUID(), idempotency_key: crypto.randomUUID(), correlation_id: crypto.randomUUID() });
        const version = crypto.randomUUID();
        intent = { target,
          sources: files.map(source => ({ file: source, documentId: crypto.randomUUID(), prepare: { ...ids(), consultation_id: target.consultation_id!, consultation_revision: current!.consultation.aggregate_revision, original_filename: source.name, expected_byte_size: source.size, source_channel: sourceChannel, expires_at: new Date(Date.now() + 7200000).toISOString() } })),
          admission: { ...ids(), dce_version_id: version, consultation_id: target.consultation_id!, consultation_revision: current!.consultation.aggregate_revision, corpus_hash: corpusHash, provenance_channel: sourceChannel, source_received_at: new Date().toISOString(), documents: [], ...(sourceChannel === "RECTIFICATION" ? { predecessor_dce_version_id: current!.metadata!.id, expected_predecessor_revision: current!.metadata!.aggregate_revision, replacement_reason: replacementReason.trim() } : {}) },
          link: { ...ids(), dce_version_id: version, ...(target.aggregate_revision === undefined ? {} : { expected_case_revision: target.aggregate_revision + (sourceChannel === "RECTIFICATION" ? 1 : 0) }), reason: "Version DCE admise depuis l’espace DCE ; rattachement explicite à cette Affaire." },
        };
        readRequest.current = null;
        setSnapshot(null);
        store(intent);
      }
      const owned = () => active.current.caseKey === caseKey;
      for (const source of intent.sources) {
        if (!source.preparation) {
          setStep("PREPARING");
          const receipt = await api.prepareDceStaging(source.prepare);
          if (receipt.status !== "SUCCEEDED" || receipt.command_id !== source.prepare.command_id || receipt.idempotency_key !== source.prepare.idempotency_key || !receipt.staging?.storage_object_id) throw new Error("UNKNOWN : reçu de staging discordant.");
          source.preparation = receipt; store({ ...intent });
          if (receipt.replayed && owned()) setMessage({ tone: "success", text: "Rejeu idempotent confirmé pour la préparation du staging." });
        }
        if (!owned()) return;
        if (!source.upload) {
          setStep("UPLOADING");
          const uploaded = await api.uploadDceStagedObjectContent(source.preparation.staging.storage_object_id, source.preparation.idempotency_key, source.file);
          if (uploaded.state !== "CLEAN" || uploaded.storage_object_id !== source.preparation.staging.storage_object_id) throw new Error("UNKNOWN : reçu de transfert discordant.");
          source.upload = uploaded; store({ ...intent });
        }
        if (!owned()) return;
      }
      intent.admission.documents = intent.sources.map(source => ({ document_id: source.documentId, storage_object_id: source.upload!.storage_object_id }));
      if (!intent.admitted) {
        setStep("ADMITTING");
        const admitted = await api.registerDceVersion(intent.admission);
        if (admitted.status !== "SUCCEEDED" || admitted.command_id !== intent.admission.command_id || admitted.idempotency_key !== intent.admission.idempotency_key || !admitted.aggregate_refs.some(ref => ref.aggregate_type === "DCE" && ref.aggregate_id === intent!.admission.dce_version_id)) throw new Error("UNKNOWN : reçu d’admission discordant.");
        intent.admitted = admitted;
        store({ ...intent });
      }
      if (!owned()) return;
      if (!intent.linked) {
        const linked = await api.linkCaseDceVersion(intent.target.case_id, intent.link);
        if (linked.status !== "SUCCEEDED" || linked.command_id !== intent.link.command_id || linked.idempotency_key !== intent.link.idempotency_key || !linked.aggregate_refs.some(ref => ref.aggregate_type === "AFF" && ref.aggregate_id === intent!.target.case_id)) throw new Error("UNKNOWN : reçu de rattachement discordant.");
        intent.linked = true; store({ ...intent });
      }
      if (!owned()) return;
      setSnapshot(null);
      setMessage({ tone: "success", text: `Version ${intent.admission.dce_version_id} admise et rattachée ; relecture en cours.` });
      await onAdmitted();
      if (!owned()) return;
      if (!await load({ ...intent.target, applicable_dce_version_id: intent.admission.dce_version_id, dce_availability: "CURRENT" })) return;
      store(null); setFileEntry({ key: caseKey, files: [], selection: 0 });
      setMessage({ tone: "success", text: `Document DCE admis et rattaché : ${intent.admitted.result_code} · ${intent.admission.dce_version_id}. Les anciennes sources restent historiques.` });
    } catch (error) {
      if (active.current.caseKey === caseKey) setMessage({ tone: "error", text: error instanceof Error ? error.message : "Admission du document impossible ; résultat UNKNOWN." });
    } finally { sending.current.delete(caseKey); setBusyKey(current => current === caseKey ? null : current); setStep("IDLE"); }
  }
  const visibleFiles = pending ? pending.sources.map(source => source.file) : files;
  return {
    consultation: current?.consultation ?? null,
    dceVersionMetadata: current?.metadata ?? null,
    inventory: current?.inventory ?? null,
    loading: loadingKey === resourceKey,
    busy: busyKey === caseKey,
    sourceChannel: pending?.admission.provenance_channel ?? sourceChannel,
    file: visibleFiles[0] ?? null,
    files: visibleFiles,
    step: busyKey === caseKey ? step : "IDLE" as DceOpeningStep,
    setSourceChannel, setFile, setFiles, openSpace, admitSelectedFile,
    pending: Boolean(pending),
    pendingVersionId: pending?.admission.dce_version_id,
    pendingPredecessorId: pending?.admission.predecessor_dce_version_id,
    pendingPredecessorRevision: pending?.admission.expected_predecessor_revision,
    pendingCorpusHash: pending?.admission.corpus_hash,
    replacementReason: pending?.admission.replacement_reason ?? replacementReason,
    setReplacementReason,
    replacementConfirmed,
    setReplacementConfirmed: (value: boolean) => setConfirmationKey(value ? confirmationIntent : ""),
  };
}
