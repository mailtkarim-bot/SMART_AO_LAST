import { useLayoutEffect, useRef, useState } from "react";
import type { Dispatch, SetStateAction } from "react";
import type { ApiClient } from "../../infrastructure/api";
import type { PricingImportBatchRead } from "../../shared/types";

type Message = { tone: "success" | "error" | "warning"; text: string };
type SetMessage = Dispatch<SetStateAction<Message | null>>;
export type PricingImportState = "IDLE" | "PREVIEWED" | "COMMITTED" | "REPLAYED" | "UNKNOWN";
export type PricingImportUnknownAction = "PREVIEW" | "COMMIT" | null;
export type PricingImportReloadState = "NOT_ATTEMPTED" | "SUCCEEDED" | "FAILED";

type PricingImportActions = {
  pricingImportBatchId: string;
  pricingImportBatchRevision: string;
  pricingImportReportRevision: string;
  pricingImportState: PricingImportState;
  pricingImportUnknownAction: PricingImportUnknownAction;
  pricingImportPreview: PricingImportBatchRead | null;
  pricingImportUploading: boolean;
  pricingImportLoading: boolean;
  pricingImportReloadState: PricingImportReloadState;
  pricingImportSubmitting: boolean;
  previewPricingImport: (file: File) => Promise<void>;
  retryPricingImportPreview: () => Promise<void>;
  reloadPricingImport: () => Promise<void>;
  setPricingImportBatchId: Dispatch<SetStateAction<string>>;
  setPricingImportBatchRevision: Dispatch<SetStateAction<string>>;
  setPricingImportReportRevision: Dispatch<SetStateAction<string>>;
  commitPricingImport: () => Promise<void>;
  retryPricingImportCommit: () => Promise<void>;
};

type PendingPreview = {
  file: File;
  command_id: string;
  idempotency_key: string;
  correlation_id: string;
};

type PendingCommit = {
  signature: string;
  command_id: string;
  idempotency_key: string;
};

type ImportView = {
  pricingImportBatchId: string;
  pricingImportBatchRevision: string;
  pricingImportReportRevision: string;
  pricingImportState: PricingImportState;
  pricingImportUnknownAction: PricingImportUnknownAction;
  pricingImportPreview: PricingImportBatchRead | null;
  pricingImportUploading: boolean;
  pricingImportLoading: boolean;
  pricingImportReloadState: PricingImportReloadState;
  pricingImportSubmitting: boolean;
};
const emptyView: ImportView = {
  pricingImportBatchId: "", pricingImportBatchRevision: "1", pricingImportReportRevision: "0",
  pricingImportState: "IDLE", pricingImportUnknownAction: null, pricingImportPreview: null,
  pricingImportUploading: false, pricingImportLoading: false,
  pricingImportReloadState: "NOT_ATTEMPTED", pricingImportSubmitting: false,
};
type Intents = { preview: { current: PendingPreview | null }; commit: { current: PendingCommit | null }; busy: boolean };
function isUnknownResult(error: unknown): boolean {
  const status = error instanceof Error ? (error as { status?: unknown }).status : undefined;
  return typeof status !== "number" || status >= 500 || status === 408;
}

export function usePricingImport(
  api: ApiClient,
  setMessage: SetMessage,
  reportId: string,
  selectedCaseId: string,
  onDraftReload: () => Promise<void>,
  ownerKey = "local",
): PricingImportActions {
  const key = JSON.stringify([ownerKey, selectedCaseId, reportId.trim()]);
  const activeKey = useRef(key);
  useLayoutEffect(() => { activeKey.current = key; }, [key]);
  const [views, setViews] = useState<Record<string, ImportView>>({});
  const intents = useRef(new Map<string, Intents>());
  function getIntent() {
    let intent = intents.current.get(key);
    if (!intent) {
      intent = { preview: { current: null }, commit: { current: null }, busy: false };
      intents.current.set(key, intent);
    }
    return intent;
  }
  const view = views[key] ?? emptyView;
  const { pricingImportBatchId, pricingImportBatchRevision, pricingImportReportRevision, pricingImportState, pricingImportUnknownAction, pricingImportPreview, pricingImportUploading, pricingImportLoading, pricingImportReloadState, pricingImportSubmitting } = view;
  function setter<K extends keyof ImportView>(field: K): Dispatch<SetStateAction<ImportView[K]>> {
    return (value) => setViews((all) => {
      const current = all[key] ?? emptyView;
      return { ...all, [key]: { ...current, [field]: typeof value === "function"
        ? (value as (previous: ImportView[K]) => ImportView[K])(current[field]) : value } };
    });
  }
  const notify: SetMessage = (message) => { if (activeKey.current === key) setMessage(message); };
  const setPricingImportBatchId = setter("pricingImportBatchId");
  const setPricingImportBatchRevision = setter("pricingImportBatchRevision");
  const setPricingImportReportRevision = setter("pricingImportReportRevision");
  const setPricingImportState = setter("pricingImportState");
  const setPricingImportUnknownAction = setter("pricingImportUnknownAction");
  const setPricingImportPreview = setter("pricingImportPreview");
  const setPricingImportUploading = setter("pricingImportUploading");
  const setPricingImportLoading = setter("pricingImportLoading");
  const setPricingImportReloadState = setter("pricingImportReloadState");
  const setPricingImportSubmitting = setter("pricingImportSubmitting");

  async function previewPricingImport(file: File) {
    const currentIntent = getIntent();
    const pendingPreview = currentIntent.preview;
    const pendingCommit = currentIntent.commit;
    if (!ownerKey || currentIntent.busy || pendingCommit.current || (pendingPreview.current && pendingPreview.current.file !== file)) return;
    if (!selectedCaseId) {
      notify({ tone: "error", text: "Sélectionnez une affaire avant l’import." });
      return;
    }
    const command =
      pendingPreview.current?.file === file
        ? pendingPreview.current
        : {
            file,
            command_id: crypto.randomUUID(),
            idempotency_key: crypto.randomUUID(),
            correlation_id: crypto.randomUUID(),
          };
    pendingPreview.current = command;
    currentIntent.busy = true;
    setPricingImportUploading(true);
    try {
      const preview = await api.createPricingImportPreview(selectedCaseId, file, "EXCEL", command);
      if (preview.case_id !== selectedCaseId) throw new Error("Réponse d’import hors contexte.");
      pendingPreview.current = null;
      setPricingImportUnknownAction(null);
      setPricingImportPreview(preview);
      setPricingImportBatchId(preview.batch_id);
      setPricingImportBatchRevision(String(preview.aggregate_revision));
      setPricingImportState("PREVIEWED");
      notify({
        tone: preview.truncated ? "warning" : "success",
        text: preview.truncated
          ? `Preview incomplète : le fichier dépasse la limite ${
              preview.limit_reason === "ROW_LIMIT" ? "de lignes (10 000)" : "d’erreurs (100)"
            }. Seules les lignes listées sont importables — fractionnez le fichier.`
          : preview.replayed
            ? "Preview déjà enregistrée : rejeu idempotent."
            : "Preview validée et enregistrée dans un batch patronal.",
      });
    } catch (error) {
      if (isUnknownResult(error)) {
        setPricingImportState("UNKNOWN");
        setPricingImportUnknownAction("PREVIEW");
        notify({
          tone: "warning",
          text: "Preview à vérifier : la réponse du serveur n’a pas été reçue. Rejouez avec les mêmes identifiants.",
        });
      } else {
        pendingPreview.current = null;
        notify({
          tone: "error",
          text: error instanceof Error ? error.message : "La preview de l’import a échoué.",
        });
      }
    } finally {
      currentIntent.busy = false;
      setPricingImportUploading(false);
    }
  }

  async function retryPricingImportPreview() {
    const pendingPreview = getIntent().preview;
    const file = pendingPreview.current?.file;
    if (!file) {
      notify({ tone: "error", text: "Aucune preview inconnue à rejouer." });
      return;
    }
    await previewPricingImport(file);
  }

  async function reloadPricingImport() {
    const currentIntent = getIntent();
    const pendingPreview = currentIntent.preview;
    const pendingCommit = currentIntent.commit;
    if (!ownerKey || currentIntent.busy || pendingPreview.current || pendingCommit.current) return;
    if (!selectedCaseId || !pricingImportBatchId.trim()) {
      notify({ tone: "error", text: "Sélectionnez une affaire et un batch avant la lecture." });
      return;
    }
    currentIntent.busy = true;
    setPricingImportLoading(true);
    try {
      const projection = await api.getPricingImport(
        selectedCaseId,
        pricingImportBatchId.trim(),
      );
      if (projection.case_id !== selectedCaseId || projection.batch_id !== pricingImportBatchId.trim()) {
        throw new Error("Lecture d’import hors contexte.");
      }
      setPricingImportPreview(projection);
      setPricingImportUnknownAction(null);
      setPricingImportBatchRevision(String(projection.aggregate_revision));
      setPricingImportState(projection.state === "COMMITTED" ? "COMMITTED" : "PREVIEWED");
      notify({ tone: "success", text: "Batch pricing relu côté patron." });
    } catch (error) {
      notify({
        tone: "error",
        text: error instanceof Error ? error.message : "La lecture du batch pricing a échoué.",
      });
    } finally {
      currentIntent.busy = false;
      setPricingImportLoading(false);
    }
  }

  async function commitPricingImport() {
    const currentIntent = getIntent();
    const pendingPreview = currentIntent.preview;
    const pendingCommit = currentIntent.commit;
    if (!ownerKey || currentIntent.busy || pendingPreview.current) return;
    if (!selectedCaseId || !pricingImportBatchId.trim() || !reportId.trim()) {
      notify({ tone: "error", text: "Sélectionnez une affaire, un batch et un brouillon avant le commit." });
      return;
    }
    const expectedBatchRevision = Number(pricingImportBatchRevision);
    const expectedReportRevision = Number(pricingImportReportRevision);
    if (
      !Number.isSafeInteger(expectedBatchRevision) ||
      expectedBatchRevision < 1 ||
      !Number.isSafeInteger(expectedReportRevision) ||
      expectedReportRevision < 0
    ) {
      notify({ tone: "error", text: "Les révisions attendues doivent être des entiers valides." });
      return;
    }
    const signature = [
      selectedCaseId,
      pricingImportBatchId.trim(),
      reportId.trim(),
      expectedBatchRevision,
      expectedReportRevision,
    ].join(":");
    if (pendingCommit.current && pendingCommit.current.signature !== signature) return;
    const command =
      pendingCommit.current?.signature === signature
        ? pendingCommit.current
        : {
            signature,
            command_id: crypto.randomUUID(),
            idempotency_key: crypto.randomUUID(),
          };
    pendingCommit.current = command;
    currentIntent.busy = true;
    setPricingImportSubmitting(true);
    setPricingImportReloadState("NOT_ATTEMPTED");
    try {
      const receipt = await api.commitPricingImport(selectedCaseId, pricingImportBatchId.trim(), {
        report_id: reportId.trim(),
        expected_batch_revision: expectedBatchRevision,
        expected_report_revision: expectedReportRevision,
        command_id: command.command_id,
        idempotency_key: command.idempotency_key,
      });
      const reportReference = receipt.aggregate_refs.find(
        (reference) => reference.aggregate_type === "FinancialReportSnapshot",
      );
      const batchReference = receipt.aggregate_refs.find(
        (reference) => reference.aggregate_type === "PricingImportBatch",
      );
      if (receipt.status !== "SUCCEEDED" || receipt.command_id !== command.command_id
        || receipt.idempotency_key !== command.idempotency_key
        || reportReference?.aggregate_id !== reportId.trim()
        || batchReference?.aggregate_id !== pricingImportBatchId.trim()
        || !Number.isSafeInteger(reportReference.aggregate_revision)
        || !Number.isSafeInteger(batchReference.aggregate_revision)
        || reportReference.aggregate_revision <= expectedReportRevision
        || batchReference.aggregate_revision <= expectedBatchRevision) {
        throw new Error("Reçu d’import non vérifié.");
      }
      pendingCommit.current = null;
      setPricingImportUnknownAction(null);
      if (reportReference) setPricingImportReportRevision(String(reportReference.aggregate_revision));
      if (batchReference) setPricingImportBatchRevision(String(batchReference.aggregate_revision));
      setPricingImportState(receipt.replayed ? "REPLAYED" : "COMMITTED");
      notify({
        tone: "success",
        text: receipt.replayed
          ? "Import déjà commité : rejeu idempotent sans nouvelle ligne."
          : "Import commité dans le brouillon financier patronal.",
      });
      try {
        if (activeKey.current !== key) return;
        await onDraftReload();
        setPricingImportReloadState("SUCCEEDED");
      } catch {
        setPricingImportReloadState("FAILED");
        notify({
          tone: "warning",
          text: "Import confirmé, mais le brouillon n’a pas pu être rechargé. Relancez sa lecture.",
        });
      }
    } catch (error) {
      if (isUnknownResult(error)) {
        setPricingImportState("UNKNOWN");
        setPricingImportUnknownAction("COMMIT");
        notify({
          tone: "warning",
          text: "Commit à vérifier : la réponse du serveur n’a pas été reçue. Rejouez avec les mêmes identifiants.",
        });
      } else {
        pendingCommit.current = null;
        notify({ tone: "error", text: error instanceof Error ? error.message : "Le commit de l’import a échoué." });
      }
    } finally {
      currentIntent.busy = false;
      setPricingImportSubmitting(false);
    }
  }

  async function retryPricingImportCommit() {
    const pendingCommit = getIntent().commit;
    if (!pendingCommit.current) {
      notify({ tone: "error", text: "Aucun commit inconnu à rejouer." });
      return;
    }
    await commitPricingImport();
  }

  return {
    pricingImportBatchId,
    pricingImportBatchRevision,
    pricingImportReportRevision,
    pricingImportState,
    pricingImportUnknownAction,
    pricingImportPreview,
    pricingImportUploading,
    pricingImportLoading,
    pricingImportReloadState,
    pricingImportSubmitting,
    previewPricingImport,
    retryPricingImportPreview,
    reloadPricingImport,
    setPricingImportBatchId: (value) => { const intent = getIntent(); if (!intent.busy && !intent.preview.current && !intent.commit.current) setPricingImportBatchId(value); },
    setPricingImportBatchRevision: (value) => { const intent = getIntent(); if (!intent.busy && !intent.preview.current && !intent.commit.current) setPricingImportBatchRevision(value); },
    setPricingImportReportRevision: (value) => { const intent = getIntent(); if (!intent.busy && !intent.preview.current && !intent.commit.current) setPricingImportReportRevision(value); },
    commitPricingImport,
    retryPricingImportCommit,
  };
}
