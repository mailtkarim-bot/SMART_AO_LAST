import type { FormEvent, ReactNode } from "react";
import { useEffect, useState } from "react";
import type {
  CaseExecutionResults,
  RecordCaseOutcomeInput,
  RecordCaseOrderInput,
  RecordCaseP6ControlInput,
  RecordCaseP7ResultInput,
} from "../../shared/types";
import type { CaseExecutionResultsStatus } from "./useCaseExecutionResults";

type PendingInput = Record<string, unknown>;
type WriteFailure = { key: string; kind: "UNCONFIRMED" | "REJECTED" };
const ids = () => ({ command_id: crypto.randomUUID(), idempotency_key: crypto.randomUUID(), correlation_id: crypto.randomUUID() });
const lines = (value: string) => value.split("\n").map((line) => line.trim()).filter(Boolean);

function labelOutcome(outcome: CaseExecutionResults["results"][number]["outcome"]) {
  return outcome === "WON" ? "Attribution déclarée (WON)" : outcome === "LOST" ? "Perdu (LOST)" : "Résultat inconnu (UNKNOWN)";
}

function statusText(status: CaseExecutionResultsStatus, data: CaseExecutionResults | null) {
  if (status === "LOADING") return data ? "Relecture serveur en cours ; affichage de la dernière lecture confirmée." : "Chargement des résultats par lot…";
  if (status === "UNAVAILABLE") return data ? "UNAVAILABLE · dernière lecture confirmée affichée ; aucune écriture disponible." : "UNAVAILABLE · lecture des résultats par lot impossible.";
  return "Les faits, décisions et états d’exécution restent séparés ; aucun résultat externe n’est présumé.";
}

export function CaseOutcomePanel({
  caseId,
  canManage,
  status,
  data,
  onRefresh,
  onRecordOutcome,
  onRecordOrder,
  onRecordP6,
  onRecordP7,
}: {
  caseId: string;
  canManage: boolean;
  status: CaseExecutionResultsStatus;
  data: CaseExecutionResults | null;
  onRefresh: () => void | Promise<void>;
  onRecordOutcome?: (input: RecordCaseOutcomeInput) => Promise<void>;
  onRecordOrder?: (input: RecordCaseOrderInput) => Promise<void>;
  onRecordP6?: (orderId: string, input: RecordCaseP6ControlInput) => Promise<void>;
  onRecordP7?: (p6Id: string, input: RecordCaseP7ResultInput) => Promise<void>;
}) {
  const [lotReference, setLotReference] = useState("");
  const [outcome, setOutcome] = useState<RecordCaseOutcomeInput["outcome"]>("UNKNOWN");
  const [sourceLocator, setSourceLocator] = useState("");
  const [unknownReason, setUnknownReason] = useState("");
  const [outcomeReservations, setOutcomeReservations] = useState("");
  const [draftCaseId, setDraftCaseId] = useState(caseId);
  const [pending, setPending] = useState<Record<string, { caseId: string; input: PendingInput }>>({});
  const [submitting, setSubmitting] = useState<string | null>(null);
  const [failure, setFailure] = useState<WriteFailure | null>(null);
  const failedKey = failure?.key ?? null;
  const isCurrent = status === "READY" && data?.case_id === caseId;
  const blockedByUnknownWrite = Object.keys(pending).length > 0;
  const pendingOtherCase = Object.values(pending).some((attempt) => attempt.caseId !== caseId);

  useEffect(() => {
    if (draftCaseId !== caseId && !pendingOtherCase) {
      setLotReference("");
      setOutcome("UNKNOWN");
      setSourceLocator("");
      setUnknownReason("");
      setOutcomeReservations("");
      setDraftCaseId(caseId);
    }
  }, [caseId, draftCaseId, pendingOtherCase]);
  const outcomeKey = lotReference ? `outcome:${lotReference}` : "";
  const outcomeControlsDisabled = blockedByUnknownWrite || !!submitting || !isCurrent;
  const outcomeButtonDisabled = !!submitting || (blockedByUnknownWrite && !pending[outcomeKey]) || !isCurrent;

  async function submitIntent<T extends PendingInput>(
    key: string,
    create: () => T,
    send: (input: T) => Promise<void>,
  ) {
    if (!canManage || !isCurrent || submitting || pendingOtherCase) return;
    const existing = pending[key]?.caseId === caseId ? pending[key].input as T : undefined;
    const input = existing ?? create();
    if (!existing) setPending((current) => ({ ...current, [key]: { caseId, input } }));
    setSubmitting(key);
    setFailure(null);
    try {
      await send(input);
      await onRefresh();
      setPending((current) => {
        const next = { ...current };
        delete next[key];
        return next;
      });
    } catch (error) {
      const status = (error as { status?: number })?.status;
      if (status !== undefined && status >= 400 && status < 500) {
        setPending((current) => {
          const next = { ...current };
          delete next[key];
          return next;
        });
        setFailure({ key, kind: "REJECTED" });
      } else {
        setFailure({ key, kind: "UNCONFIRMED" });
      }
    } finally {
      setSubmitting(null);
    }
  }

  async function recordOutcome(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!onRecordOutcome || !lotReference) return;
    await submitIntent(
      `outcome:${lotReference}`,
      () => ({
        ...ids(), outcome_id: crypto.randomUUID(), case_id: caseId, lot_reference: lotReference,
        outcome, source_locator: sourceLocator.trim() || null,
        reservations: outcome === "LOST" ? [] : lines(outcomeReservations),
        unknown_reason: unknownReason.trim() || null,
      }),
      onRecordOutcome,
    );
  }

  if (!caseId) return <section className="section-block decision-section" aria-label="Résultats et passation C12"><p>UNKNOWN · aucune Affaire sélectionnée.</p></section>;
  return <section className="section-block decision-section" aria-label="Résultats et passation C12">
    <div className="section-heading"><div><span className="section-kicker">C12 · RÉSULTAT ET PASSATION</span><h2>Résultat par lot · P6 · P7</h2></div></div>
    <p>{statusText(status, data)}</p>
    {pendingOtherCase && <p role="status">Une écriture de résultat reste non confirmée pour une autre Affaire. Revenez à cette Affaire pour rejouer la même intention ; ses détails restent masqués ici.</p>}
    {!pendingOtherCase && data?.case_id === caseId && <>
      {canManage && isCurrent && onRecordOutcome && <form aria-label="Enregistrer le résultat d’un lot" onSubmit={(event) => void recordOutcome(event)}>
        <label>Lot concerné
          <select aria-label="Lot concerné" required value={lotReference} disabled={outcomeControlsDisabled} onChange={(event) => setLotReference(event.target.value)}>
            <option value="">Choisir un lot de cette Affaire</option>
            {data.lot_references.map((lot) => <option key={lot} value={lot}>Lot {lot}</option>)}
          </select>
        </label>
        <label>Résultat déclaré du lot
          <select aria-label="Résultat déclaré du lot" value={outcome} disabled={outcomeControlsDisabled} onChange={(event) => setOutcome(event.target.value as RecordCaseOutcomeInput["outcome"])}>
            <option value="WON">Attribué (WON)</option><option value="LOST">Perdu (LOST)</option><option value="UNKNOWN">Résultat inconnu (UNKNOWN)</option>
          </select>
        </label>
        <label>Référence de preuve du résultat{outcome === "WON" ? " · obligatoire pour WON" : " · si disponible"}<input aria-label="Référence de preuve du résultat" maxLength={500} required={outcome === "WON"} value={sourceLocator} disabled={outcomeControlsDisabled} onChange={(event) => setSourceLocator(event.target.value)} /></label>
        {outcome === "UNKNOWN" && <label>Motif du résultat inconnu<textarea aria-label="Motif du résultat inconnu" required maxLength={1000} value={unknownReason} disabled={outcomeControlsDisabled} onChange={(event) => setUnknownReason(event.target.value)} /></label>}
        {outcome !== "LOST" && <label>Réserves déclarées, une par ligne<textarea aria-label="Réserves déclarées" maxLength={32000} value={outcomeReservations} disabled={outcomeControlsDisabled} onChange={(event) => setOutcomeReservations(event.target.value)} /></label>}
        <button type="submit" disabled={outcomeButtonDisabled}>{submitting === outcomeKey ? "Enregistrement…" : failedKey === outcomeKey && failure?.kind === "UNCONFIRMED" ? "Réessayer le résultat par lot" : failedKey === outcomeKey ? "Corriger et réessayer" : "Enregistrer le résultat par lot"}</button>
        {failedKey === outcomeKey && <p role="alert">{failure?.kind === "REJECTED" ? "Refus serveur confirmé · aucune nouvelle preuve n’a été enregistrée. Corrigez les données avant une nouvelle intention." : "Résultat non confirmé · vérifiez la lecture serveur ou rejouez la même intention idempotente avant toute nouvelle saisie."}</p>}
      </form>}
      {data.lot_references.length === 0 && <p>UNKNOWN · le périmètre de lots de l’Affaire n’est pas renseigné ; aucun lot n’est inventé.</p>}
      {data.results.length === 0 && data.lot_references.length > 0 && <p>UNKNOWN · aucun résultat n’est enregistré pour ces lots ; cela ne prouve ni perte ni attribution.</p>}
      {data.results.length > 0 && <div className="decision-grid">{data.results.map((item) => {
        const orderKey = `order:${item.outcome_id}`;
        const p6Key = `p6:${item.order?.order_id ?? ""}`;
        const p7Key = `p7:${item.p6?.p6_control_id ?? ""}`;
        const stepControlsDisabled = (key: string) => !isCurrent || !!submitting || !!pending[key] || (blockedByUnknownWrite && !pending[key]);
        const stepButtonDisabled = (key: string) => !isCurrent || !!submitting || (blockedByUnknownWrite && !pending[key]);
        return <article className="detail-panel" key={`${item.outcome_id}:${item.lot_reference}`}>
          <h3>Lot {item.lot_reference} · {labelOutcome(item.outcome)}</h3>
          <p>Résultat enregistré le {item.recorded_at} par {item.actor_id}.</p>
          <p>Source déclarée : {item.source_locator ?? "UNKNOWN · aucune référence"} · référence non vérifiée automatiquement.</p>
          {item.unknown_reason && <p>Motif UNKNOWN : {item.unknown_reason}</p>}
          <p>Réserves déclarées : {item.reservations.join(" · ") || "Aucune indiquée"}</p>
          {item.transmission
            ? <p>Transmission interne enregistrée à {item.transmission.recorded_at} au destinataire {item.transmission.recipient} ; aucune réception externe présumée.</p>
            : <p>Transmission interne : UNKNOWN · aucun acte de transmission enregistré.</p>}
          {item.order
            ? <div><h4>Décision sur la commande · {item.order.decision}</h4><p>{item.order.rationale} · {item.order.recorded_at}</p></div>
            : item.outcome === "WON" ? <>
                <p>UNKNOWN · aucune décision Patron sur la commande n’est enregistrée.</p>
                {canManage && isCurrent && onRecordOrder && <OrderForm outcomeId={item.outcome_id} caseId={caseId} disabled={stepControlsDisabled(orderKey)} buttonDisabled={stepButtonDisabled(orderKey)} pending={!!pending[orderKey]} failure={failedKey === orderKey ? failure : null} submitting={submitting === orderKey} onSubmit={(input) => submitIntent(orderKey, () => input, onRecordOrder)} />}
              </> : <p>{item.outcome === "LOST" ? "Commande non applicable · le lot est déclaré perdu." : "Commande non ouverte · le résultat est UNKNOWN."}</p>}
          {item.order?.decision === "ACCEPTED" && item.p6
            ? <div><h4>Contrôle P6 · {item.p6.decision}</h4><p>{item.p6.rationale} · {item.p6.recorded_at}</p><p>Réserves P6 : {item.p6.reservations.join(" · ") || "Aucune indiquée"}</p></div>
            : item.order?.decision === "ACCEPTED" ? <>
                <p>UNKNOWN · la décision P6 n’est pas enregistrée.</p>
                {canManage && isCurrent && onRecordP6 && <P6Form orderId={item.order.order_id} caseId={caseId} disabled={stepControlsDisabled(p6Key)} buttonDisabled={stepButtonDisabled(p6Key)} pending={!!pending[p6Key]} failure={failedKey === p6Key ? failure : null} submitting={submitting === p6Key} onSubmit={(input) => submitIntent(p6Key, () => input, (value) => onRecordP6(item.order!.order_id, value))} />}
              </>
              : item.order?.decision === "REJECTED" ? <p>P6 indisponible · commande rejetée.</p> : <p>UNKNOWN · P6 en attente d’une décision sur la commande.</p>}
          {item.p6?.decision === "APPROVED" && item.p7
            ? <div><h4>Résultat P7 · {item.p7.result}</h4><p>Déclaré le {item.p7.recorded_at}.</p><p>Référence d’exécution : {item.p7.source_locator ?? "Aucune"}</p><p>Motif : {item.p7.reason ?? "Aucun"}</p><p>Réserves : {item.p7.reservations.join(" · ") || "Aucune indiquée"}</p><p>P7 ne vaut pas ordre de service.</p></div>
            : item.p6?.decision === "APPROVED" ? <>
                <p>UNKNOWN · aucun résultat P7 n’est enregistré.</p><p>P7 ne vaut pas ordre de service.</p>
                {canManage && isCurrent && onRecordP7 && <P7Form p6Id={item.p6.p6_control_id} caseId={caseId} disabled={stepControlsDisabled(p7Key)} buttonDisabled={stepButtonDisabled(p7Key)} pending={!!pending[p7Key]} failure={failedKey === p7Key ? failure : null} submitting={submitting === p7Key} onSubmit={(input) => submitIntent(p7Key, () => input, (value) => onRecordP7(item.p6!.p6_control_id, value))} />}
              </>
              : item.p6?.decision === "REJECTED" ? <p>P7 indisponible · décision P6 rejetée.</p> : <p>UNKNOWN · P7 attend une décision P6 approuvée.</p>}
        </article>;
      })}</div>}
    </>}
  </section>;
}

function CommandFields({ pending, failure, submitting, buttonDisabled, button, retryButton, children, onSubmit }: {
  pending: boolean; failure: WriteFailure | null; submitting: boolean; buttonDisabled: boolean; button: string; retryButton: string;
  children: ReactNode; onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return <form onSubmit={onSubmit}>
    {children}
    <button type="submit" disabled={buttonDisabled}>{submitting ? "Enregistrement…" : failure?.kind === "UNCONFIRMED" && pending ? retryButton : failure?.kind === "REJECTED" ? "Corriger et réessayer" : button}</button>
    {failure?.kind === "UNCONFIRMED" && pending && <p role="alert">Résultat non confirmé · la relance réutilise les mêmes identifiants.</p>}
    {failure?.kind === "REJECTED" && <p role="alert">Refus serveur confirmé · aucune décision n’a été enregistrée. Corrigez les données avant une nouvelle intention.</p>}
  </form>;
}

function OrderForm({ outcomeId, caseId, disabled, buttonDisabled, pending, failure, submitting, onSubmit }: {
  outcomeId: string; caseId: string; disabled: boolean; buttonDisabled: boolean; pending: boolean; failure: WriteFailure | null; submitting: boolean;
  onSubmit: (input: RecordCaseOrderInput) => Promise<void>;
}) {
  const [decision, setDecision] = useState<RecordCaseOrderInput["decision"]>("ACCEPTED");
  const [rationale, setRationale] = useState("");
  return <CommandFields pending={pending} failure={failure} submitting={submitting} buttonDisabled={buttonDisabled} button="Enregistrer la décision sur la commande" retryButton="Réessayer la décision sur la commande" onSubmit={(event) => { event.preventDefault(); void onSubmit({ ...ids(), order_id: crypto.randomUUID(), outcome_id: outcomeId, case_id: caseId, decision, rationale: rationale.trim() }); }}>
    <label>Décision Patron sur la commande<select aria-label="Décision Patron sur la commande" value={decision} disabled={disabled || submitting} onChange={(event) => setDecision(event.target.value as RecordCaseOrderInput["decision"])}><option value="ACCEPTED">Commande acceptée</option><option value="REJECTED">Commande rejetée</option></select></label>
    <label>Motif de la commande<textarea aria-label="Motif de la commande" required maxLength={1000} value={rationale} disabled={disabled || submitting} onChange={(event) => setRationale(event.target.value)} /></label>
  </CommandFields>;
}

function P6Form({ orderId, caseId, disabled, buttonDisabled, pending, failure, submitting, onSubmit }: {
  orderId: string; caseId: string; disabled: boolean; buttonDisabled: boolean; pending: boolean; failure: WriteFailure | null; submitting: boolean;
  onSubmit: (input: RecordCaseP6ControlInput) => Promise<void>;
}) {
  const [decision, setDecision] = useState<RecordCaseP6ControlInput["decision"]>("APPROVED");
  const [rationale, setRationale] = useState("");
  const [reservations, setReservations] = useState("");
  return <CommandFields pending={pending} failure={failure} submitting={submitting} buttonDisabled={buttonDisabled} button="Enregistrer la décision P6" retryButton="Réessayer la décision P6" onSubmit={(event) => { event.preventDefault(); void onSubmit({ ...ids(), p6_control_id: crypto.randomUUID(), order_id: orderId, case_id: caseId, decision, reservations: lines(reservations), rationale: rationale.trim() }); }}>
    <label>Décision Patron P6<select aria-label="Décision Patron P6" value={decision} disabled={disabled || submitting} onChange={(event) => setDecision(event.target.value as RecordCaseP6ControlInput["decision"])}><option value="APPROVED">P6 approuvée</option><option value="REJECTED">P6 rejetée</option></select></label>
    <label>Motif P6<textarea aria-label="Motif P6" required maxLength={1000} value={rationale} disabled={disabled || submitting} onChange={(event) => setRationale(event.target.value)} /></label>
    <label>Réserves P6, une par ligne<textarea aria-label="Réserves P6" maxLength={32000} value={reservations} disabled={disabled || submitting} onChange={(event) => setReservations(event.target.value)} /></label>
  </CommandFields>;
}

function P7Form({ p6Id, caseId, disabled, buttonDisabled, pending, failure, submitting, onSubmit }: {
  p6Id: string; caseId: string; disabled: boolean; buttonDisabled: boolean; pending: boolean; failure: WriteFailure | null; submitting: boolean;
  onSubmit: (input: RecordCaseP7ResultInput) => Promise<void>;
}) {
  const [result, setResult] = useState<RecordCaseP7ResultInput["result"]>("UNKNOWN");
  const [sourceLocator, setSourceLocator] = useState("");
  const [reason, setReason] = useState("");
  const [reservations, setReservations] = useState("");
  return <CommandFields pending={pending} failure={failure} submitting={submitting} buttonDisabled={buttonDisabled} button="Enregistrer le résultat P7" retryButton="Réessayer le résultat P7" onSubmit={(event) => { event.preventDefault(); void onSubmit({ ...ids(), p7_result_id: crypto.randomUUID(), p6_control_id: p6Id, case_id: caseId, result, source_locator: sourceLocator.trim() || null, reason: reason.trim() || null, reservations: lines(reservations) }); }}>
    <label>Résultat P7<select aria-label="Résultat P7" value={result} disabled={disabled || submitting} onChange={(event) => setResult(event.target.value as RecordCaseP7ResultInput["result"])}><option value="COMPLETED">Exécution déclarée terminée</option><option value="UNKNOWN">Résultat d’exécution inconnu</option><option value="INTERRUPTED">Exécution interrompue</option></select></label>
    {result === "COMPLETED" && <label>Référence de preuve d’exécution<input aria-label="Référence de preuve d’exécution" required value={sourceLocator} disabled={disabled || submitting} onChange={(event) => setSourceLocator(event.target.value)} /></label>}
    {(result === "UNKNOWN" || result === "INTERRUPTED") && <label>Motif du résultat P7<textarea aria-label="Motif du résultat P7" required maxLength={1000} value={reason} disabled={disabled || submitting} onChange={(event) => setReason(event.target.value)} /></label>}
    <label>Réserves P7, une par ligne<textarea aria-label="Réserves P7" maxLength={32000} value={reservations} disabled={disabled || submitting} onChange={(event) => setReservations(event.target.value)} /></label>
  </CommandFields>;
}
