import { useRef, useState, type FormEvent } from "react";

import type { CaseInterview, RecordCaseInterviewInput } from "../../shared/types";

export type CaseInterviewReadStatus = "LOADING" | "READY" | "UNAVAILABLE";

type WriteFailure = "UNCONFIRMED" | "REJECTED";

type CaseInterviewsPanelProps = {
  caseId: string;
  caseLabel: string;
  status: CaseInterviewReadStatus;
  interviews: CaseInterview[] | null;
  canManage: boolean;
  onRecordInterview?: (input: RecordCaseInterviewInput) => Promise<void>;
  onRefresh: () => void | Promise<void>;
};

export function CaseInterviewsPanel({
  caseId,
  caseLabel,
  status,
  interviews,
  canManage,
  onRecordInterview,
  onRefresh,
}: CaseInterviewsPanelProps) {
  const [heldOn, setHeldOn] = useState("");
  const [sourceLocator, setSourceLocator] = useState("");
  const [rationale, setRationale] = useState("");
  const [expiresOn, setExpiresOn] = useState("");
  const [pendingInput, setPendingInput] = useState<RecordCaseInterviewInput | null>(null);
  const pendingInputRef = useRef<RecordCaseInterviewInput | null>(null);
  const submittingRef = useRef(false);
  const [submitting, setSubmitting] = useState(false);
  const [failure, setFailure] = useState<WriteFailure | null>(null);

  async function recordInterview(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!caseId || !canManage || !onRecordInterview || submittingRef.current) return;
    if (pendingInputRef.current && pendingInputRef.current.case_id !== caseId) return;

    const input = pendingInputRef.current ?? {
      command_id: crypto.randomUUID(),
      idempotency_key: crypto.randomUUID(),
      correlation_id: crypto.randomUUID(),
      interview_id: crypto.randomUUID(),
      case_id: caseId,
      held_on: heldOn,
      source_locator: sourceLocator.trim(),
      rationale: rationale.trim(),
      expires_on: expiresOn,
    };
    if (!pendingInputRef.current) {
      pendingInputRef.current = input;
      setPendingInput(input);
    }

    submittingRef.current = true;
    setSubmitting(true);
    setFailure(null);
    try {
      await onRecordInterview(input);
      await onRefresh();
      pendingInputRef.current = null;
      setPendingInput(null);
      setHeldOn("");
      setSourceLocator("");
      setRationale("");
      setExpiresOn("");
    } catch (error) {
      const statusCode = (error as { status?: number })?.status;
      if (statusCode !== undefined && statusCode >= 400 && statusCode < 500) {
        pendingInputRef.current = null;
        setPendingInput(null);
        setFailure("REJECTED");
      } else {
        setFailure("UNCONFIRMED");
      }
    } finally {
      submittingRef.current = false;
      setSubmitting(false);
    }
  }

  const interviewsReady = status === "READY" && interviews !== null;
  const lockedForRetry = failure === "UNCONFIRMED" && pendingInput !== null;
  const retryTargetsDifferentCase = lockedForRetry && pendingInput?.case_id !== caseId;
  const formDisabled = submitting || lockedForRetry || !interviewsReady || !caseId;
  const buttonDisabled = submitting || !interviewsReady || !caseId || !canManage || !onRecordInterview || retryTargetsDifferentCase;

  return (
    <section className="section-block" aria-label="Entretiens Patron C13">
      <div className="section-heading">
        <div>
          <span className="section-kicker">C13 · ENTREPRISE</span>
          <h3>Entretiens Patron · réemploi sous conditions</h3>
        </div>
        <span className="count-pill">{interviewsReady ? interviews.length : "—"} entretien(s)</span>
      </div>
      <p>Affaire active : {caseLabel || "UNKNOWN · aucune Affaire sélectionnée"}.</p>
      <p>Chaque entretien fige un snapshot des enseignements à date et une expiration ; aucun réemploi automatique, aucune conclusion juridique.</p>
      {status === "LOADING" && <p role="status">Chargement des entretiens Patron…</p>}
      {status === "UNAVAILABLE" && <p role="status">UNAVAILABLE · lecture des entretiens Patron impossible.</p>}
      {status === "READY" && caseId && interviews?.length === 0 && <p>UNKNOWN · aucun entretien n’est enregistré pour cette Affaire.</p>}
      {interviewsReady && interviews.map((entry) => (
        <article key={entry.interview_id} className="detail-panel">
          <h4>Entretien du {entry.held_on}</h4>
          <p>{entry.status === "USABLE" ? `USABLE · réemploi sous conditions jusqu’au ${entry.expires_on}` : "EXPIRED · réemploi à réinterroger"}</p>
          <p>Motif : {entry.rationale}</p>
          <p>Source déclarée : {entry.source_locator}</p>
          <p>Snapshot à date : {(entry.snapshot.rex ?? []).length} enseignement{(entry.snapshot.rex ?? []).length === 1 ? "" : "s"} capturé{(entry.snapshot.rex ?? []).length === 1 ? "" : "s"}</p>
        </article>
      ))}
      {retryTargetsDifferentCase && <p role="alert">Résultat non confirmé pour l’Affaire {pendingInput?.case_id} · revenez à cette Affaire pour rejouer la même commande.</p>}
      {caseId && canManage && onRecordInterview && status === "READY" && (
        <form aria-label="Enregistrer un entretien Patron" onSubmit={(event) => void recordInterview(event)}>
          <label>Date de l’entretien<input aria-label="Date de l’entretien" type="date" required value={heldOn} disabled={formDisabled} onChange={(event) => setHeldOn(event.target.value)} /></label>
          <label>Source de l’entretien<input aria-label="Source de l’entretien" required maxLength={500} value={sourceLocator} disabled={formDisabled} onChange={(event) => setSourceLocator(event.target.value)} /></label>
          <label>Motif de l’entretien<textarea aria-label="Motif de l’entretien" required maxLength={2000} value={rationale} disabled={formDisabled} onChange={(event) => setRationale(event.target.value)} /></label>
          <label>Expiration du réemploi<input aria-label="Expiration du réemploi" type="date" required value={expiresOn} disabled={formDisabled} onChange={(event) => setExpiresOn(event.target.value)} /></label>
          <button type="submit" disabled={buttonDisabled}>
            {submitting ? "Enregistrement…" : failure === "UNCONFIRMED" && pendingInput ? "Réessayer l’entretien" : failure === "REJECTED" ? "Corriger et réessayer" : "Enregistrer l’entretien"}
          </button>
          {failure === "UNCONFIRMED" && pendingInput && <p role="alert">Entretien non confirmé · la relance réutilise les mêmes identifiants.</p>}
          {failure === "REJECTED" && <p role="alert">Refus serveur confirmé · aucun entretien n’a été enregistré. Corrigez les données avant une nouvelle intention.</p>}
        </form>
      )}
    </section>
  );
}
