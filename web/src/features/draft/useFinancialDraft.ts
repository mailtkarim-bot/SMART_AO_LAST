import type { Dispatch, FormEvent, SetStateAction } from "react";
import { useEffect, useRef, useState } from "react";

import type { ApiClient, FinancialCommandIdentity } from "../../infrastructure/api";
import type { DraftReport, FinancialCategory, PublishedFinancialReport } from "../../shared/types";

type Message = { tone: "success" | "error" | "warning"; text: string };
type SetMessage = Dispatch<SetStateAction<Message | null>>;
export type FinancialLineForm = { category: FinancialCategory; label: string; quantity_decimal: string; unit: string; amount_minor: string };
const initialLineForm: FinancialLineForm = { category: "SALES", label: "", quantity_decimal: "1", unit: "forfait", amount_minor: "" };
const commandIdentity = (): FinancialCommandIdentity => ({ command_id: crypto.randomUUID(), idempotency_key: crypto.randomUUID(), correlation_id: crypto.randomUUID() });
export type FinancialPublicationState = "IDLE" | "PUBLISHING" | "UNKNOWN" | "CONFIRMED" | "REJECTED";
type Publication = { key: string; reportId: string; state: FinancialPublicationState; revision: number | null; expectedRevision: number | null; error: string | null };
const emptyPublication: Publication = { key: "", reportId: "", state: "IDLE", revision: null, expectedRevision: null, error: null };

export function useFinancialDraft(api: Pick<ApiClient, "createDraft" | "getDraft" | "addLine" | "publishFinancialReport" | "getPublishedFinancialReport">, setMessage: SetMessage, selectedCaseId: string, scopeKey: string) {
  const key = scopeKey && selectedCaseId ? JSON.stringify([scopeKey, selectedCaseId]) : "";
  const [selection, setSelection] = useState({ key: "", value: "" });
  const [reading, setReading] = useState<{ key: string; draft: DraftReport | null }>({ key: "", draft: null });
  const [form, setForm] = useState({ key: "", value: initialLineForm });
  const [busy, setBusy] = useState({ key: "", value: false });
  const requests = useRef(0);
  const writing = useRef<{ key: string; request: number } | null>(null);
  const creationIntent = useRef<{ key: string; identity: FinancialCommandIdentity } | null>(null);
  const lineIntent = useRef<{ signature: string; input: Parameters<ApiClient["addLine"]>[2] } | null>(null);
  const publicationIntent = useRef<{ key: string; reportId: string; input: Parameters<ApiClient["publishFinancialReport"]>[2]; confirmedRevision: number | null } | null>(null);
  const [publication, setPublication] = useState<Publication>(emptyPublication);
  const [publishedReading, setPublishedReading] = useState<{ key: string; reportId: string; report: PublishedFinancialReport | null; error: string | null }>({ key: "", reportId: "", report: null, error: null });
  const reportId = key && selection.key === key ? selection.value : "";
  const currentPublication = key && publication.key === key && publication.reportId === reportId.trim() ? publication : emptyPublication;
  const currentPublished = key && publishedReading.key === key && publishedReading.reportId === reportId.trim() ? publishedReading : null;
  const publishedReport = currentPublished?.report ?? null;
  const publicationLocked = ["PUBLISHING", "UNKNOWN", "CONFIRMED"].includes(currentPublication.state) || publishedReport !== null;
  const draft = !publicationLocked && key && reading.key === key && reading.draft?.report_id === reportId.trim() ? reading.draft : null;
  const lineForm = key && form.key === key ? form.value : initialLineForm;

  useEffect(() => {
    requests.current++;
    writing.current = null;
    creationIntent.current = null;
    lineIntent.current = null;
    publicationIntent.current = null;
    setPublication(emptyPublication);
    setPublishedReading({ key: "", reportId: "", report: null, error: null });
    setSelection({ key, value: "" });
    setReading({ key, draft: null });
    setForm({ key, value: initialLineForm });
    setBusy({ key, value: false });
    return () => {
      // Request generation deliberately invalidates the latest pending operation.
      // eslint-disable-next-line react-hooks/exhaustive-deps
      requests.current++;
    };
  }, [key]);

  const setReportId: Dispatch<SetStateAction<string>> = (value) => {
    if (["PUBLISHING", "UNKNOWN"].includes(currentPublication.state)) return;
    requests.current++;
    setSelection((previous) => ({ key, value: typeof value === "function" ? value(previous.key === key ? previous.value : "") : value }));
    setReading({ key, draft: null });
    setForm({ key, value: initialLineForm });
    setBusy({ key, value: false });
    publicationIntent.current = null;
    setPublication(emptyPublication);
    setPublishedReading({ key: "", reportId: "", report: null, error: null });
  };
  const setLineForm: Dispatch<SetStateAction<FinancialLineForm>> = (value) => {
    setForm((previous) => ({ key, value: typeof value === "function" ? value(previous.key === key ? previous.value : initialLineForm) : value }));
  };
  function checked(value: DraftReport, targetReportId: string) {
    if (value.case_id !== selectedCaseId || value.report_id !== targetReportId || value.status !== "DRAFT") throw new Error("Projection financière indisponible pour ce contexte.");
    return value;
  }

  async function createDraft() {
    if (!selectedCaseId) { setMessage({ tone: "error", text: "Sélectionnez une affaire avant de créer un brouillon." }); return; }
    if (!key || writing.current?.key === key || currentPublication.state === "UNKNOWN") return;
    const request = ++requests.current;
    writing.current = { key, request };
    if (creationIntent.current?.key !== key) creationIntent.current = { key, identity: commandIdentity() };
    const intent = creationIntent.current;
    setBusy({ key, value: true });
    setMessage(null);
    try {
      const receipt = await api.createDraft(selectedCaseId, intent.identity);
      if (request !== requests.current) return;
      const newReportId = receipt.aggregate_refs[0]?.aggregate_id;
      if (!newReportId) throw new Error("Le serveur n’a pas retourné l’identifiant du brouillon.");
      setSelection({ key, value: newReportId });
      const loaded = checked(await api.getDraft(selectedCaseId, newReportId), newReportId);
      if (request !== requests.current) return;
      setReading({ key, draft: loaded });
      if (creationIntent.current === intent) creationIntent.current = null;
      setMessage({ tone: "success", text: receipt.replayed ? "Brouillon existant rechargé." : "Nouveau brouillon créé." });
    } catch (error) {
      if (request !== requests.current) return;
      setReading({ key, draft: null });
      setMessage({ tone: "error", text: error instanceof Error ? error.message : "Impossible de créer le brouillon." });
    } finally {
      if (writing.current?.request === request) writing.current = null;
      if (request === requests.current) setBusy({ key, value: false });
    }
  }

  async function loadDraft() {
    if (!key || publicationLocked) return;
    if (!selectedCaseId || !reportId.trim()) { setMessage({ tone: "error", text: "Sélectionnez une affaire et renseignez l’identifiant du brouillon." }); return; }
    const request = ++requests.current;
    setBusy({ key, value: true });
    setMessage(null);
    try {
      const loaded = checked(await api.getDraft(selectedCaseId, reportId.trim()), reportId.trim());
      if (request !== requests.current) return;
      setReading({ key, draft: loaded });
      if (currentPublication.state === "REJECTED") {
        publicationIntent.current = null;
        setPublication(emptyPublication);
      }
      setMessage({ tone: "success", text: "Brouillon chargé en lecture seule contrôlée." });
    } catch (error) {
      if (request !== requests.current) return;
      setReading({ key, draft: null });
      setMessage({ tone: "error", text: error instanceof Error ? error.message : "Impossible de charger le brouillon." });
    } finally {
      if (request === requests.current) setBusy({ key, value: false });
    }
  }

  async function submitLine(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!key || !draft || publicationLocked || writing.current?.key === key) return;
    const amount = Number(lineForm.amount_minor);
    if (!/^-?\d+$/.test(lineForm.amount_minor.trim()) || !Number.isSafeInteger(amount)) {
      setMessage({ tone: "error", text: "Le montant doit être exprimé en centimes entiers." }); return;
    }
    const request = ++requests.current;
    writing.current = { key, request };
    // An unknown outcome keeps the original revision and identity, even after a newer read-back.
    const signature = JSON.stringify([key, draft.report_id, lineForm.category, lineForm.label, lineForm.quantity_decimal, lineForm.unit, amount]);
    if (lineIntent.current?.signature !== signature) lineIntent.current = { signature, input: { ...lineForm, amount_minor: amount, expected_revision: draft.aggregate_revision, ...commandIdentity() } };
    const intent = lineIntent.current;
    setBusy({ key, value: true });
    try {
      const receipt = await api.addLine(selectedCaseId, draft.report_id, intent.input);
      if (request !== requests.current) return;
      setForm({ key, value: { ...lineForm, label: "", amount_minor: "" } });
      const loaded = checked(await api.getDraft(selectedCaseId, draft.report_id), draft.report_id);
      if (request !== requests.current) return;
      setReading({ key, draft: loaded });
      if (lineIntent.current === intent) lineIntent.current = null;
      setMessage({ tone: "success", text: receipt.replayed ? "Ajout rejoué sans doublon." : "Ligne ajoutée au brouillon." });
    } catch (error) {
      if (request !== requests.current) return;
      if ([409, 422].includes((error as { status?: number }).status ?? 0) && lineIntent.current === intent) lineIntent.current = null;
      setReading({ key, draft: null });
      setMessage({ tone: "error", text: error instanceof Error ? error.message : "L’ajout de la ligne a échoué." });
    } finally {
      if (writing.current?.request === request) writing.current = null;
      if (request === requests.current) setBusy({ key, value: false });
    }
  }
  async function readPublished(target: string, request: number, expectedRevision: number | null) {
    try {
      const value = await api.getPublishedFinancialReport(selectedCaseId, target);
      if (request !== requests.current) return;
      if (value.case_id !== selectedCaseId || value.report_id !== target || value.status !== "PUBLISHED"
        || !Number.isSafeInteger(value.aggregate_revision) || value.aggregate_revision < 0
        || !Array.isArray(value.lines) || !value.summary || !value.margin_calculation
        || !["CALCULATED", "UNKNOWN"].includes(value.margin_calculation.state)
        || !Array.isArray(value.margin_calculation.missing_categories)
        || (expectedRevision !== null && value.aggregate_revision !== expectedRevision)) {
        throw new Error("Invalid published source");
      }
      setPublishedReading({ key, reportId: target, report: value, error: null });
      setReading({ key, draft: null });
    } catch {
      if (request !== requests.current) return;
      setPublishedReading({ key, reportId: target, report: null, error: "La source publiée n’a pas pu être vérifiée pour ce contexte. Relisez-la." });
    }
  }

  async function loadPublishedReport() {
    const target = reportId.trim();
    if (!key || !target || writing.current?.key === key) return;
    const request = ++requests.current;
    setBusy({ key, value: true });
    setPublishedReading({ key, reportId: target, report: null, error: null });
    const intent = publicationIntent.current;
    const expectedRevision = intent?.key === key && intent.reportId === target
      ? intent.confirmedRevision ?? intent.input.expected_revision + 1 : null;
    try { await readPublished(target, request, expectedRevision); }
    finally { if (request === requests.current) setBusy({ key, value: false }); }
  }

  async function publishReport() {
    const target = reportId.trim();
    if (!key || !target || writing.current?.key === key || currentPublication.state === "CONFIRMED"
      || (publishedReport && currentPublication.state !== "UNKNOWN")) return;
    let intent = publicationIntent.current;
    if (intent?.key !== key || intent.reportId !== target) {
      if (!draft) return;
      if (lineIntent.current || creationIntent.current) {
        setMessage({ tone: "warning", text: "Résolvez l’écriture du brouillon avant de le publier." });
        return;
      }
      intent = { key, reportId: target, input: { ...commandIdentity(), expected_revision: draft.aggregate_revision }, confirmedRevision: null };
      publicationIntent.current = intent;
    }
    const request = ++requests.current;
    writing.current = { key, request };
    setBusy({ key, value: true });
    setMessage(null);
    setPublication({ key, reportId: target, state: "PUBLISHING", revision: null, expectedRevision: intent.input.expected_revision, error: null });
    setPublishedReading({ key, reportId: target, report: null, error: null });
    try {
      const receipt = await api.publishFinancialReport(selectedCaseId, target, intent.input);
      if (request !== requests.current) return;
      const ref = receipt.aggregate_refs[0];
      if (receipt.status !== "SUCCEEDED" || receipt.result_code !== "FINANCIAL_REPORT_PUBLISHED"
        || receipt.command_id !== intent.input.command_id || receipt.idempotency_key !== intent.input.idempotency_key
        || receipt.aggregate_refs.length !== 1 || ref?.aggregate_type !== "FinancialReportSnapshot"
        || ref.aggregate_id !== target || ref.aggregate_revision !== intent.input.expected_revision + 1) {
        throw new Error("Invalid publication receipt");
      }
      publicationIntent.current = { ...intent, confirmedRevision: ref.aggregate_revision };
      setReading({ key, draft: null });
      setPublication({ key, reportId: target, state: "CONFIRMED", revision: ref.aggregate_revision, expectedRevision: intent.input.expected_revision, error: null });
      await readPublished(target, request, ref.aggregate_revision);
    } catch (error) {
      if (request !== requests.current) return;
      const status = (error as { status?: number })?.status;
      const detail = (error as { detail?: string })?.detail;
      const rejected = [400, 401, 403, 404, 422].includes(status ?? 0)
        || (status === 409 && detail === "VERSION_CONFLICT");
      if (rejected) publicationIntent.current = null;
      setReading({ key, draft: null });
      setPublication({ key, reportId: target, state: rejected ? "REJECTED" : "UNKNOWN", revision: null, expectedRevision: intent.input.expected_revision,
        error: rejected ? "Publication refusée. Relisez le brouillon avant une nouvelle intention." : "Résultat de publication UNKNOWN. Le rejeu conserve l’identité et la révision initiales." });
    } finally {
      if (writing.current?.request === request) writing.current = null;
      if (request === requests.current) setBusy({ key, value: false });
    }
  }

  return { reportId, draft, loadingDraft: Boolean(key) && busy.key === key && busy.value, lineForm, setReportId, setLineForm, createDraft, loadDraft, submitLine,
    publicationState: currentPublication.state, publicationRevision: currentPublication.revision, publicationExpectedRevision: currentPublication.expectedRevision, publicationError: currentPublication.error,
    publicationLocked, publishedReport, publishedReadError: currentPublished?.error ?? null, publishReport, loadPublishedReport };
}
