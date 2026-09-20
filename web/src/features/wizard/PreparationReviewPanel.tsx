import { useState, type Dispatch, type FormEvent, type SetStateAction } from "react";

import type { ApiClient } from "../../infrastructure/api";
import type {
  AddPreparationCorrectionInput,
  DecidePreparationReviewInput,
  PreparationResponseDraftList,
  PreparationReviewList,
  RequestPreparationReviewInput,
} from "../../shared/types";

type Message = { tone: "success" | "error" | "warning"; text: string };
type PreparationReviewPanelProps = {
  api: ApiClient;
  setMessage: Dispatch<SetStateAction<Message | null>>;
};

export function PreparationReviewPanel({ api, setMessage }: PreparationReviewPanelProps) {
  const [packageId, setPackageId] = useState("");
  const [packageRevision, setPackageRevision] = useState("0");
  const [documentId, setDocumentId] = useState("");
  const [documentVersion, setDocumentVersion] = useState("1");
  const [reviews, setReviews] = useState<PreparationReviewList | null>(null);
  const [drafts, setDrafts] = useState<PreparationResponseDraftList | null>(null);
  const [note, setNote] = useState("");
  const [correctionInstruction, setCorrectionInstruction] = useState("");
  const [correctionCode, setCorrectionCode] = useState<AddPreparationCorrectionInput["correction_code"]>("SECTION_INCOMPLETE");
  const [busy, setBusy] = useState(false);

  async function loadReviews() {
    if (!packageId.trim()) return;
    setBusy(true);
    try {
      const [reviewResult, draftResult] = await Promise.all([
        api.listPreparationReviews(packageId.trim()),
        api.listPreparationResponseDrafts(packageId.trim()),
      ]);
      setReviews(reviewResult);
      setDrafts(draftResult);
    } catch (error) {
      setMessage({ tone: "error", text: error instanceof Error ? error.message : "Impossible de charger les revues." });
    } finally {
      setBusy(false);
    }
  }

  async function requestReview(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!packageId.trim() || !documentId.trim()) return;
    const input: RequestPreparationReviewInput = {
      expected_package_revision: Number(packageRevision),
      target_document_id: documentId.trim(),
      target_version: Number(documentVersion),
    };
    await mutate(() => api.requestPreparationReview(packageId.trim(), input), "Revue demandée.");
  }

  async function decide(reviewId: string, targetDocumentId: string, decisionCode: DecidePreparationReviewInput["decision_code"]) {
    if (!packageId.trim()) return;
    await mutate(() => api.decidePreparationReview(packageId.trim(), {
      expected_review_revision: reviews?.reviews.find((review) => review.review_id === reviewId)?.revision ?? 0,
      review_id: reviewId,
      target_document_id: targetDocumentId,
      decision_code: decisionCode,
      decision_note: note.trim() || null,
    }), `Revue ${decisionCode.toLowerCase()} enregistrée.`);
    setNote("");
  }

  async function addCorrection(reviewId: string, targetDocumentId: string) {
    if (!packageId.trim() || !correctionInstruction.trim()) return;
    await mutate(() => api.addPreparationCorrection(packageId.trim(), {
      review_id: reviewId,
      target_document_id: targetDocumentId,
      correction_code: correctionCode,
      instruction: correctionInstruction.trim(),
    }), "Correction ajoutée à la revue.");
    setCorrectionInstruction("");
  }

  async function mutate(command: () => Promise<unknown>, success: string) {
    setBusy(true);
    try {
      await command();
      await loadReviews();
      setMessage({ tone: "success", text: success });
    } catch (error) {
      setMessage({ tone: "error", text: error instanceof Error ? error.message : "La commande de revue a échoué." });
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="section-block review-section" id="preparation-review-section">
      <div className="section-heading"><div><span className="section-kicker">CONTRÔLE PATRONAL</span><h2>Revue des documents générés</h2></div><span className="count-pill">REVUE</span></div>
      <div className="review-toolbar">
        <label><span>Package de préparation</span><input value={packageId} onChange={(event) => setPackageId(event.target.value)} placeholder="UUID du package" /></label>
        <button className="secondary-button" type="button" disabled={busy || !packageId.trim()} onClick={() => void loadReviews()}>Charger les revues</button>
      </div>
      {drafts && <div className="response-plan patron-response-plan"><div className="panel-heading"><div><h3>Plans de réponse reçus</h3><p>Versions, sections et sources ; le contenu reste privé et non financier.</p></div><span className="rule-tag">{drafts.drafts.length} brouillon{drafts.drafts.length > 1 ? "s" : ""}</span></div>{drafts.drafts.length === 0 ? <p className="panel-empty">Aucun brouillon reçu.</p> : drafts.drafts.map((draft) => <div className="response-plan-row" key={`${draft.draft_id}-${draft.version}`}><div><strong>Brouillon v{draft.version}</strong><small>{draft.state} · {draft.responsible_role}</small></div><span>{draft.section_codes.join(" · ")}</span></div>)}</div>}
      <div className="review-request-grid">
        <form className="workflow-form" onSubmit={requestReview}><h3>Demander une revue</h3><label><span>Révision package</span><input required min="0" type="number" value={packageRevision} onChange={(event) => setPackageRevision(event.target.value)} /></label><label><span>Document</span><input required value={documentId} onChange={(event) => setDocumentId(event.target.value)} placeholder="UUID du document" /></label><label><span>Version</span><input required min="1" type="number" value={documentVersion} onChange={(event) => setDocumentVersion(event.target.value)} /></label><button className="primary-button" type="submit" disabled={busy}>Demander la revue</button></form>
        <div className="workflow-form"><h3>Note de décision</h3><textarea rows={4} value={note} onChange={(event) => setNote(event.target.value)} placeholder="Note facultative appliquée à la prochaine décision" /></div>
      </div>
      {reviews === null ? <p className="panel-empty">Chargez un package pour afficher ses dernières révisions de revue.</p> : reviews.reviews.length === 0 ? <p className="panel-empty">Aucune revue demandée pour ce package.</p> : <div className="review-list">{reviews.reviews.map((review) => <article className="review-card" key={review.review_id}><div className="workflow-item-top"><strong>{review.target_document_id} · v{review.target_version}</strong><span className="state-badge">{review.state}</span></div><small>Revue {review.review_id} · Révision {review.revision}</small>{review.decision_note && <p>{review.decision_note}</p>}<div className="review-actions"><button className="secondary-button" type="button" disabled={busy} onClick={() => void decide(review.review_id, review.target_document_id, "ACCEPTED")}>Accepter</button><button className="secondary-button" type="button" disabled={busy} onClick={() => void decide(review.review_id, review.target_document_id, "CORRECTIONS_REQUIRED")}>Demander corrections</button><button className="secondary-button danger-button" type="button" disabled={busy} onClick={() => void decide(review.review_id, review.target_document_id, "REJECTED")}>Rejeter</button></div><div className="correction-inline"><select value={correctionCode} onChange={(event) => setCorrectionCode(event.target.value as AddPreparationCorrectionInput["correction_code"])}><option value="SOURCE_MISSING">SOURCE_MISSING</option><option value="SOURCE_WRONG">SOURCE_WRONG</option><option value="SECTION_INCOMPLETE">SECTION_INCOMPLETE</option><option value="WORDING_UNCLEAR">WORDING_UNCLEAR</option></select><input value={correctionInstruction} onChange={(event) => setCorrectionInstruction(event.target.value)} placeholder="Instruction de correction" /><button className="secondary-button" type="button" disabled={busy || !correctionInstruction.trim()} onClick={() => void addCorrection(review.review_id, review.target_document_id)}>Ajouter correction</button></div>{review.corrections.map((correction) => <div className="workflow-response" key={correction.correction_id}><strong>{correction.correction_code}</strong><span>{correction.instruction}</span></div>)}</article>)}</div>}
    </section>
  );
}
