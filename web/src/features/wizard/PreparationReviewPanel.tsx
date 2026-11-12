import { ResponseCoveragePanel } from "./ResponseCoveragePanel";
import {ResponseDraftDownload} from "./ResponseDraftDownload";
import { useState, useLayoutEffect, useRef, type Dispatch, type FormEvent, type SetStateAction } from "react";

import type { ApiClient } from "../../infrastructure/api";
import type {
  AddPreparationCorrectionInput,
  DecidePreparationReviewInput,
  PreparationResponseDraftList,
  PreparationReviewList,
  PreparationTransmissionList,
  RequestPreparationReviewInput,
  TechnicalResponseDraft,
} from "../../shared/types";

import { ResponseDraftContent } from "./ResponseDraftContent";

type Message = { tone: "success" | "error" | "warning"; text: string };
type PreparationReviewPanelProps = {
  api: ApiClient;
  ownerKey?: string;
  setMessage: Dispatch<SetStateAction<Message | null>>;
};

export function PreparationReviewPanel({ api, setMessage, ownerKey="" }: PreparationReviewPanelProps) {
  const [packageId, setPackageId] = useState("");
  const [packageRevision, setPackageRevision] = useState("0");
  const [documentId, setDocumentId] = useState("");
  const [documentVersion, setDocumentVersion] = useState("1");
  const [storedReviews, setReviews] = useState<PreparationReviewList | null>(null);
  const [storedDrafts, setDrafts] = useState<PreparationResponseDraftList | null>(null);
  const [storedTransmissions, setTransmissions] = useState<PreparationTransmissionList | null>(null);
  const [note, setNote] = useState("");
  const [correctionInstruction, setCorrectionInstruction] = useState("");
  const [correctedContent, setCorrectedContent] = useState("");
  const [correctionCode, setCorrectionCode] = useState<AddPreparationCorrectionInput["correction_code"]>("SECTION_INCOMPLETE");
  const [busy, setBusy] = useState(false);

  const owner=ownerKey||api;
  const scopeId=packageId.trim();
  const latest=useRef({owner,scopeId});
  useLayoutEffect(()=>{latest.current={owner,scopeId}});
  const sequence=useRef(0);
  const [loadedScope,setLoadedScope]=useState<{owner:typeof owner;scopeId:string}|null>(null);
  const matches=()=>latest.current.owner===owner&&latest.current.scopeId===scopeId;
  const visible=loadedScope?.owner===owner&&loadedScope.scopeId===scopeId;
  const reviews=visible?storedReviews:null,drafts=visible?storedDrafts:null,transmissions=visible?storedTransmissions:null;
  useLayoutEffect(()=>{setBusy(false);setNote("");setCorrectedContent("");setCorrectionInstruction("");},[owner,scopeId]);

  async function loadReviews(): Promise<boolean> {
    if (!packageId.trim()) return false;
    const request=++sequence.current;
    const current=()=>matches()&&request===sequence.current;
    setBusy(true);
    setTransmissions(null);
    try {
      const [reviewResult, draftResult] = await Promise.all([
        api.listPreparationReviews(packageId.trim()),
        api.listPreparationResponseDrafts(packageId.trim()),
      ]);
      if(!current())return false;
      if(reviewResult.package_id!==packageId.trim()||draftResult.package_id!==packageId.trim())throw Error("REVIEW_CONTEXT_UNKNOWN");
      setLoadedScope({owner,scopeId});
      setReviews(reviewResult);
      setDrafts(draftResult);
      if (draftResult.package_revision !== undefined) {
        setPackageRevision(String(draftResult.package_revision));
      }
      let receiptsLoaded = true;
      try {
        const delivery=await api.listPreparationTransmissions(packageId.trim());
        if(!current())return false;
        if(delivery.package_id!==packageId.trim())throw Error("REVIEW_CONTEXT_UNKNOWN");
        setTransmissions(delivery);
      } catch (error) {
        if(!current())return false;
        receiptsLoaded = false;
        setTransmissions(null);
        setMessage({ tone: "warning", text: error instanceof Error ? error.message : "Impossible de relire les transmissions." });
      }
      return receiptsLoaded;
    } catch (error) {
      if(!current())return false;
      setMessage({ tone: "error", text: error instanceof Error ? error.message : "Impossible de charger les revues." });
      return false;
    } finally {
      if(current())setBusy(false);
    }
  }

  async function requestDocumentReview(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!packageId.trim() || !documentId.trim()) return;
    const input: RequestPreparationReviewInput = {
      expected_package_revision: Number(packageRevision),
      target_document_id: documentId.trim(),
      target_version: Number(documentVersion),
    };
    await mutate(() => api.requestPreparationReview(packageId.trim(), input), "Revue demandée.");
  }

  async function requestDraftReview(draft: TechnicalResponseDraft) {
    if (!packageId.trim() || !draft.content_sha256 || !draft.response_plan_id) return;
    const input: RequestPreparationReviewInput = {
      expected_package_revision: Number(packageRevision),
      target_draft_id: draft.draft_id,
      target_draft_version: draft.version,
      target_content_sha256: draft.content_sha256,
    };
    await mutate(() => api.requestPreparationReview(packageId.trim(), input), "Revue exacte demandée.");
  }

  async function decide(review: PreparationReviewList["reviews"][number], decisionCode: DecidePreparationReviewInput["decision_code"]) {
    if (!packageId.trim()) return;
    await mutate(() => api.decidePreparationReview(packageId.trim(), {
      expected_review_revision: review.revision,
      review_id: review.review_id,
      target_document_id: review.target_document_id,
      target_draft_id: review.target_draft_id,
      target_draft_version: review.target_draft_version,
      target_content_sha256: review.target_content_sha256,
      decision_code: decisionCode,
      decision_note: note.trim() || null,
    }), `Revue ${decisionCode.toLowerCase()} enregistrée.`);
    setNote("");
  }

  async function addCorrection(review: PreparationReviewList["reviews"][number]) {
    if (!packageId.trim() || !correctionInstruction.trim()) return;
    await mutate(() => api.addPreparationCorrection(packageId.trim(), {
      review_id: review.review_id,
      target_document_id: review.target_document_id,
      target_draft_id: review.target_draft_id,
      target_draft_version: review.target_draft_version,
      target_content_sha256: review.target_content_sha256,
      correction_code: correctionCode,
      instruction: correctionInstruction.trim(),
      corrected_content: review.target_draft_id ? correctedContent : undefined,
    }), "Correction ajoutée à la revue.");
    setCorrectionInstruction("");
    setCorrectedContent("");
  }

  async function mutate(command: () => Promise<unknown>, success: string) {
    setBusy(true);
    try {
      await command();
      if(!matches())return;
      const receiptsLoaded = await loadReviews();
      if(!matches())return;
      setMessage({
        tone: receiptsLoaded ? "success" : "warning",
        text: receiptsLoaded ? success : `${success} Les reçus restent à relire.`,
      });
    } catch (error) {
      if(!matches())return;
      setMessage({ tone: "error", text: error instanceof Error ? error.message : "La commande de revue a échoué." });
    } finally {
      if(matches())setBusy(false);
    }
  }

  return (
    <section className="section-block review-section" id="preparation-review-section">
      <div className="section-heading"><div><span className="section-kicker">CONTRÔLE PATRONAL</span><h2>Revue des documents générés</h2></div><span className="count-pill">REVUE</span></div>
      <div className="review-toolbar">
        <label><span>Package de préparation</span><input value={packageId} onChange={(event) => setPackageId(event.target.value)} placeholder="UUID du package" /></label>
        <button className="secondary-button" type="button" disabled={busy || !packageId.trim()} onClick={() => void loadReviews()}>Charger les revues</button>
      </div>
      {drafts && <div className="response-plan patron-response-plan"><div className="panel-heading"><div><h3>Brouillons C10 reçus</h3><p>Chaque revue porte sur le contenu exact et son empreinte recalculée.</p></div><span className="rule-tag">{drafts.drafts.length} brouillon{drafts.drafts.length > 1 ? "s" : ""}</span></div>{drafts.drafts.length === 0 ? <p className="panel-empty">Aucun brouillon reçu.</p> : drafts.drafts.map((draft) => <article className="response-plan-row" key={`${draft.draft_id}-${draft.version}`}><div><strong>Brouillon {draft.draft_id} · v{draft.version}</strong><small>{draft.state} · {draft.responsible_role} · plan {draft.response_plan_id ?? "historique"} v{draft.response_plan_version ?? "?"}</small><small>SHA-256 du contenu : {draft.content_sha256 ?? "UNKNOWN"}</small></div><span>{draft.section_codes.join(" · ")}</span>{draft.content !== undefined && <ResponseDraftContent content={draft.content} format={draft.content_format} provenance={draft.content_provenance}/>
        }{draft.response_plan_id && draft.content_sha256 && <ResponseCoveragePanel api={api} packageId={packageId}
          scopeKey={JSON.stringify([ownerKey, packageId, drafts?.package_revision])}
          selection={{draft_id:draft.draft_id,version:draft.version,content_sha256:draft.content_sha256}}/>}
        {draft.content_format==="DOCX" && <ResponseDraftDownload api={api} scopeKey={JSON.stringify([ownerKey,packageId])} packageId={packageId} draft={draft}/>}
        {draft.response_plan_id && !reviews?.reviews.some((review) => review.target_draft_id === draft.draft_id && review.target_draft_version === draft.version && review.target_content_sha256 === draft.content_sha256) && <button className="secondary-button" type="button" disabled={busy || !draft.content_sha256} onClick={() => void requestDraftReview(draft)}>Demander la revue exacte</button>}</article>)}</div>}
      {transmissions && <div className="response-plan patron-response-plan"><div className="panel-heading"><div><h3>Snapshots transmis au Patron</h3><p>Les manifestes et reçus ci-dessous sont relus depuis les enregistrements internes.</p></div><span className="rule-tag">{transmissions.deliveries.length} transmission{transmissions.deliveries.length === 1 ? "" : "s"}</span></div>{transmissions.deliveries.length === 0 ? <p className="panel-empty">Aucun snapshot transmis pour ce package.</p> : transmissions.deliveries.map((delivery) => <article className="review-card" key={delivery.transmission_id}><strong>Snapshot v{delivery.snapshot_version} · {delivery.snapshot_id}</strong><small>{delivery.snapshot_state} · créé {delivery.snapshot_created_at}</small><small>SHA-256 du manifeste : {delivery.snapshot_manifest_sha256}</small><strong>Transmission {delivery.transmission_id}</strong><small>{delivery.transmission_state} · {delivery.transmitted_at}</small><details><summary>Manifeste figé</summary><pre className="review-draft-content">{JSON.stringify(delivery.snapshot_manifest, null, 2)}</pre></details><details><summary>Reçus et révisions exacts</summary><pre className="review-draft-content">{JSON.stringify({ snapshot: delivery.snapshot_receipt, transmission: delivery.transmission_receipt }, null, 2)}</pre></details></article>)}</div>}
      <div className="review-request-grid">
        <form className="workflow-form" onSubmit={requestDocumentReview}><h3>Revue historique de document</h3><label><span>Révision package</span><input required min="0" type="number" value={packageRevision} onChange={(event) => setPackageRevision(event.target.value)} /></label><label><span>Document</span><input required value={documentId} onChange={(event) => setDocumentId(event.target.value)} placeholder="UUID du document" /></label><label><span>Version</span><input required min="1" type="number" value={documentVersion} onChange={(event) => setDocumentVersion(event.target.value)} /></label><button className="primary-button" type="submit" disabled={busy}>Demander la revue historique</button></form>
        <div className="workflow-form"><h3>Note de décision</h3><textarea aria-label="Note de décision" rows={4} value={note} onChange={(event) => setNote(event.target.value)} placeholder="Note facultative appliquée à la prochaine décision" /></div>
      </div>
      {reviews === null ? <p className="panel-empty">Chargez un package pour afficher ses dernières révisions de revue.</p> : reviews.reviews.length === 0 ? <p className="panel-empty">Aucune revue demandée pour ce package.</p> : <div className="review-list">{reviews.reviews.map((review) => <article className="review-card" key={review.review_id}><div className="workflow-item-top"><strong>{review.target_draft_id ? `Brouillon ${review.target_draft_id} · v${review.target_draft_version}` : `${review.target_document_id} · v${review.target_version}`}</strong><span className="state-badge">{review.state}</span></div><small>Revue {review.review_id} · Révision {review.revision}{review.target_content_sha256 ? ` · SHA-256 ${review.target_content_sha256}` : ""}</small>{review.decision_note && <p>{review.decision_note}</p>}<div className="review-actions"><button className="secondary-button" type="button" disabled={busy || review.state !== "REQUESTED"} onClick={() => void decide(review, "ACCEPTED")}>Accepter</button><button className="secondary-button" type="button" disabled={busy || review.state !== "REQUESTED"} onClick={() => void decide(review, "CORRECTIONS_REQUIRED")}>Demander corrections</button><button className="secondary-button danger-button" type="button" disabled={busy || review.state !== "REQUESTED"} onClick={() => void decide(review, "REJECTED")}>Rejeter</button></div>{review.state === "RETURNED_WITH_CORRECTIONS" && review.target_draft_id && drafts?.drafts.find(d=>d.draft_id===review.target_draft_id&&d.version===review.target_draft_version)?.content_format!=="DOCX" && <div className="correction-inline"><label><span>Contenu corrigé</span><textarea rows={8} value={correctedContent} onChange={(event) => setCorrectedContent(event.target.value)} /></label><select value={correctionCode} onChange={(event) => setCorrectionCode(event.target.value as AddPreparationCorrectionInput["correction_code"])}><option value="SOURCE_MISSING">SOURCE_MISSING</option><option value="SOURCE_WRONG">SOURCE_WRONG</option><option value="SECTION_INCOMPLETE">SECTION_INCOMPLETE</option><option value="WORDING_UNCLEAR">WORDING_UNCLEAR</option></select><input value={correctionInstruction} onChange={(event) => setCorrectionInstruction(event.target.value)} placeholder="Instruction de correction" /><button className="secondary-button" type="button" disabled={busy || !correctionInstruction.trim() || !correctedContent.trim()} onClick={() => void addCorrection(review)}>Enregistrer une nouvelle version</button></div>}{review.state === "RETURNED_WITH_CORRECTIONS" && drafts?.drafts.find(d=>d.draft_id===review.target_draft_id&&d.version===review.target_draft_version)?.content_format==="DOCX" && <p>Corrigez les contributions sources puis remplissez à nouveau le cadre DOCX. Une correction texte ne remplace pas cette pièce.</p>}{review.corrections.map((correction) => <div className="workflow-response" key={correction.correction_id}><strong>{correction.correction_code}</strong><span>{correction.instruction}</span></div>)}</article>)}</div>}
    </section>
  );
}
