import { useEffect, useRef, useState, type FormEvent } from "react";

import type { ApiClient } from "../../infrastructure/api";
import type {
  PartnerOfferPriceView,
  PartnerOfferScopeDecision,
  PartnerOfferScopeFactInput,
  PartnerOfferScopeReviewList,
  RecordPartnerOfferScopeReviewInput,
} from "../../shared/types";

type ReadStatus = "LOADING" | "READY" | "FORBIDDEN" | "UNAVAILABLE" | "INACTIVE" | "NO_CASE";
type Failure = "UNCONFIRMED" | "REJECTED";
type Pending = { input: RecordPartnerOfferScopeReviewInput; failure?: Failure; message?: string };
type OfferFactDraft = Omit<PartnerOfferScopeFactInput, "receipt_event_id">;
type Draft = {
  comparisonId: string;
  expectedRevision: number;
  selectedReceiptIds: string[];
  facts: Record<string, OfferFactDraft>;
  decision: PartnerOfferScopeDecision;
  rationale: string;
  pending?: Pending;
  errorMessage?: string;
  confirmedMessage?: string;
};

const emptyFact: OfferFactDraft = {
  inclusion_state: "UNKNOWN",
  included_scope_note: null,
  exclusions_review_state: "UNKNOWN",
  transport_state: "UNKNOWN",
  transport_note: null,
};

function newDraft(): Draft {
  return {
    comparisonId: crypto.randomUUID(),
    expectedRevision: 0,
    selectedReceiptIds: [],
    facts: {},
    decision: "NEEDS_CLARIFICATION",
    rationale: "",
  };
}

function apiErrorStatus(error: unknown): number | undefined {
  const value = (error as { status?: unknown })?.status;
  return typeof value === "number" ? value : undefined;
}

function apiErrorDetail(error: unknown): string | undefined {
  const value = (error as { detail?: unknown })?.detail;
  return typeof value === "string" ? value : undefined;
}

export function PartnerOfferScopeReviewsPanel({
  api,
  caseId,
  offers,
  enabled,
}: {
  api: ApiClient;
  caseId: string;
  offers: PartnerOfferPriceView[];
  enabled: boolean;
}) {
  const [status, setStatus] = useState<ReadStatus>(() => !enabled ? "INACTIVE" : caseId ? "LOADING" : "NO_CASE");
  const [reviewList, setReviewList] = useState<PartnerOfferScopeReviewList | null>(null);
  const [drafts, setDrafts] = useState<Record<string, Draft>>({});
  const [savingByCase, setSavingByCase] = useState<Record<string, boolean>>({});
  const inFlight = useRef(new Set<string>());
  const [reload, setReload] = useState(0);
  const draft = drafts[caseId];
  const currentOffers = offers.filter((offer) => offer.is_latest_receipt);
  const offerByReceipt = new Map(offers.map((offer) => [offer.receipt_event_id, offer]));
  const latestRevisionByComparison = new Map<string, number>();
  for (const review of reviewList?.reviews ?? []) {
    latestRevisionByComparison.set(
      review.comparison_id,
      Math.max(latestRevisionByComparison.get(review.comparison_id) ?? 0, review.revision),
    );
  }

  useEffect(() => {
    if (!enabled) {
      setStatus("INACTIVE");
      setReviewList(null);
      return;
    }
    if (!caseId) {
      setStatus("NO_CASE");
      setReviewList(null);
      return;
    }
    let active = true;
    setStatus("LOADING");
    setReviewList(null);
    void api.listPartnerOfferScopeReviews(caseId).then((result) => {
      if (!active) return;
      if (result.case_id !== caseId || !Array.isArray(result.reviews)) {
        setStatus("UNAVAILABLE");
        return;
      }
      setReviewList(result);
      setStatus("READY");
    }).catch((error: unknown) => {
      if (!active) return;
      setReviewList(null);
      setStatus(apiErrorStatus(error) === 403 ? "FORBIDDEN" : "UNAVAILABLE");
    });
    return () => { active = false; };
  }, [api, caseId, enabled, reload]);

  function updateDraft(update: (current: Draft) => Draft) {
    if (!caseId) return;
    setDrafts((current) => ({
      ...current,
      [caseId]: update(current[caseId] ?? newDraft()),
    }));
  }

  function toggleReceipt(receiptEventId: string, checked: boolean) {
    updateDraft((current) => {
      if (current.expectedRevision > 0) return current;
      const selected = new Set(current.selectedReceiptIds);
      if (checked) selected.add(receiptEventId);
      else selected.delete(receiptEventId);
      return {
        ...current,
        selectedReceiptIds: [...selected],
        facts: checked
          ? { ...current.facts, [receiptEventId]: current.facts[receiptEventId] ?? { ...emptyFact } }
          : current.facts,
      };
    });
  }

  function revise(review: PartnerOfferScopeReviewList["reviews"][number]) {
    if (review.requires_reassessment || review.revision !== latestRevisionByComparison.get(review.comparison_id)) return;
    setDrafts((current) => ({
      ...current,
      [caseId]: {
        comparisonId: review.comparison_id,
        expectedRevision: review.revision,
        selectedReceiptIds: review.offers.map((offer) => offer.receipt_event_id),
        facts: Object.fromEntries(review.offers.map((offer) => [offer.receipt_event_id, {
          inclusion_state: offer.inclusion_state,
          included_scope_note: offer.included_scope_note,
          exclusions_review_state: offer.exclusions_review_state,
          transport_state: offer.transport_state,
          transport_note: offer.transport_note,
        }])),
        decision: review.decision,
        rationale: review.rationale,
      },
    }));
  }

  function startNewReview() {
    updateDraft((current) => current.pending?.failure === "UNCONFIRMED" ? current : newDraft());
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!caseId || !draft || inFlight.current.has(caseId)) return;
    const input = draft.pending?.input ?? {
      command_id: crypto.randomUUID(),
      idempotency_key: crypto.randomUUID(),
      correlation_id: crypto.randomUUID(),
      review_id: crypto.randomUUID(),
      comparison_id: draft.comparisonId,
      expected_revision: draft.expectedRevision,
      decision: draft.decision,
      rationale: draft.rationale.trim(),
      offers: draft.selectedReceiptIds.map((receiptEventId) => ({
        receipt_event_id: receiptEventId,
        ...(draft.facts[receiptEventId] ?? emptyFact),
      })),
    };
    if (!draft.pending) {
      updateDraft((current) => ({ ...current, pending: { input }, errorMessage: undefined }));
    }
    inFlight.current.add(caseId);
    setSavingByCase((current) => ({ ...current, [caseId]: true }));
    try {
      try {
        await api.recordPartnerOfferScopeReview(caseId, input);
      } catch (error) {
        const responseStatus = apiErrorStatus(error);
        const detail = apiErrorDetail(error);
        const confirmedConflict = responseStatus === 409
          && detail !== undefined
          && detail !== "IDEMPOTENCY_CONFLICT";
        if (!confirmedConflict && (responseStatus === 409 || responseStatus === undefined || responseStatus >= 500)) {
          updateDraft((current) => ({
            ...current,
            pending: {
              input,
              failure: "UNCONFIRMED",
              message: "Résultat non confirmé · le rejeu reprend les mêmes identifiants et les mêmes reçus.",
            },
          }));
        } else {
          updateDraft((current) => ({
            ...current,
            pending: undefined,
            errorMessage: confirmedConflict
              ? "Conflit confirmé · la source ou la révision a changé ; actualisez C08 avant une nouvelle revue."
              : "Refus confirmé · aucune revue n’a été enregistrée.",
          }));
        }
        return;
      }
      updateDraft((current) => ({
        ...current,
        expectedRevision: current.expectedRevision + 1,
        pending: undefined,
        confirmedMessage: "Revue humaine enregistrée ; l’historique append-only est conservé.",
      }));
      try {
        const refreshed = await api.listPartnerOfferScopeReviews(caseId);
        if (refreshed.case_id === caseId && Array.isArray(refreshed.reviews)) {
          setReviewList(refreshed);
          setStatus("READY");
        } else {
          setReviewList(null);
          setStatus("UNAVAILABLE");
        }
      } catch {
        setReviewList(null);
        setStatus("UNAVAILABLE");
      }
    } finally {
      inFlight.current.delete(caseId);
      setSavingByCase((current) => ({ ...current, [caseId]: false }));
    }
  }

  const selectedOffers = (draft?.selectedReceiptIds ?? [])
    .map((id) => offerByReceipt.get(id))
    .filter((offer): offer is PartnerOfferPriceView => !!offer);
  const sameScopeIncomplete = selectedOffers.some((offer) => {
    const fact = draft?.facts[offer.receipt_event_id] ?? emptyFact;
    return fact.inclusion_state !== "DECLARED"
      || fact.transport_state === "UNKNOWN"
      || fact.exclusions_review_state !== "REVIEWED"
      || offer.exclusions_state !== "DECLARED";
  });
  const canSubmit = !!draft
    && selectedOffers.length >= 2
    && !!draft.rationale.trim()
    && !(draft.decision === "SAME_SCOPE_CONFIRMED" && sameScopeIncomplete)
    && savingByCase[caseId] !== true
    && (!draft.pending || draft.pending.failure === "UNCONFIRMED");

  return (
    <section className="detail-panel" aria-label="Revue humaine de périmètre des offres">
      <div className="panel-heading">
        <div>
          <h3>Revue humaine des périmètres</h3>
          <p>Le Patron consigne si les offres couvrent le même périmètre ; l’application ne le déduit pas et ne calcule aucun coût couvert.</p>
        </div>
        <div className="button-row">
          <button type="button" className="secondary-button" onClick={() => setReload((value) => value + 1)} disabled={!enabled || !caseId || status === "LOADING"}>
            {status === "LOADING" ? "Chargement…" : "Actualiser l’historique"}
          </button>
          <button type="button" className="secondary-button" onClick={startNewReview} disabled={draft?.pending?.failure === "UNCONFIRMED"}>
            Nouvelle comparaison
          </button>
        </div>
      </div>
      {status === "LOADING" && <p role="status">Chargement de l’historique des revues…</p>}
      {status === "FORBIDDEN" && <p role="status">FORBIDDEN · revue financière Patron uniquement.</p>}
      {status === "UNAVAILABLE" && <p role="status">UNAVAILABLE · l’historique des revues doit être relu.</p>}
      {draft && status !== "FORBIDDEN" && status !== "UNAVAILABLE" && (
        <form className="detail-panel" aria-label="Enregistrer une revue de périmètre" onSubmit={(event) => void submit(event)}>
          <h4>{draft.expectedRevision ? `Révision ${draft.expectedRevision + 1}` : "Nouvelle comparaison"}</h4>
          <fieldset disabled={draft.expectedRevision > 0 || !!draft.pending}>
            <legend>Reçus partenaires à comparer</legend>
            {currentOffers.length === 0 && <p>UNKNOWN · aucun reçu courant à comparer.</p>}
            {currentOffers.map((offer) => (
              <label key={offer.receipt_event_id}>
                <input
                  type="checkbox"
                  checked={draft.selectedReceiptIds.includes(offer.receipt_event_id)}
                  onChange={(event) => toggleReceipt(offer.receipt_event_id, event.target.checked)}
                />
                {offer.partner_label} · {offer.source_locator} · exclusions {offer.exclusions_state}
              </label>
            ))}
          </fieldset>
          {selectedOffers.map((offer) => {
            const fact = draft.facts[offer.receipt_event_id] ?? emptyFact;
            const prefix = `scope-${caseId}-${offer.receipt_event_id}`;
            return (
              <fieldset key={offer.receipt_event_id} disabled={!!draft.pending}>
                <legend>{offer.partner_label} · source {offer.source_locator}</legend>
                <p>Exclusions reçues : {offer.exclusions_state}{offer.exclusions.length ? ` · ${offer.exclusions.join("; ")}` : ""}</p>
                <label htmlFor={`${prefix}-exclusions-review`}>Revue humaine des exclusions</label>
                <select id={`${prefix}-exclusions-review`} value={fact.exclusions_review_state} onChange={(event) => updateDraft((current) => ({
                  ...current,
                  facts: { ...current.facts, [offer.receipt_event_id]: { ...fact, exclusions_review_state: event.target.value as OfferFactDraft["exclusions_review_state"] } },
                }))}>
                  <option value="UNKNOWN">UNKNOWN · exclusions à relire</option>
                  <option value="REVIEWED" disabled={offer.exclusions_state !== "DECLARED"}>Exclusions de la source relues</option>
                </select>
                <label htmlFor={`${prefix}-inclusion`}>État du périmètre inclus</label>
                <select id={`${prefix}-inclusion`} value={fact.inclusion_state} onChange={(event) => updateDraft((current) => ({
                  ...current,
                  facts: { ...current.facts, [offer.receipt_event_id]: { ...fact, inclusion_state: event.target.value as OfferFactDraft["inclusion_state"], included_scope_note: event.target.value === "UNKNOWN" ? null : fact.included_scope_note } },
                }))}>
                  <option value="UNKNOWN">UNKNOWN · à confirmer</option>
                  <option value="DECLARED">Déclaré dans la source</option>
                </select>
                {fact.inclusion_state === "DECLARED" && <>
                  <label htmlFor={`${prefix}-included-note`}>Périmètre inclus tel que relu</label>
                  <textarea id={`${prefix}-included-note`} required maxLength={2000} value={fact.included_scope_note ?? ""} onChange={(event) => updateDraft((current) => ({
                    ...current,
                    facts: { ...current.facts, [offer.receipt_event_id]: { ...fact, included_scope_note: event.target.value } },
                  }))} />
                </>}
                <label htmlFor={`${prefix}-transport`}>Traitement du transport</label>
                <select id={`${prefix}-transport`} value={fact.transport_state} onChange={(event) => updateDraft((current) => ({
                  ...current,
                  facts: { ...current.facts, [offer.receipt_event_id]: { ...fact, transport_state: event.target.value as OfferFactDraft["transport_state"], transport_note: event.target.value === "UNKNOWN" ? null : fact.transport_note } },
                }))}>
                  <option value="UNKNOWN">UNKNOWN · non établi</option>
                  <option value="INCLUDED">Inclus</option>
                  <option value="EXCLUDED">Exclu</option>
                  <option value="SEPARATE">Traitement séparé</option>
                </select>
                {fact.transport_state !== "UNKNOWN" && <>
                  <label htmlFor={`${prefix}-transport-note`}>Note source sur le transport</label>
                  <input id={`${prefix}-transport-note`} required maxLength={1000} value={fact.transport_note ?? ""} onChange={(event) => updateDraft((current) => ({
                    ...current,
                    facts: { ...current.facts, [offer.receipt_event_id]: { ...fact, transport_note: event.target.value } },
                  }))} />
                </>}
              </fieldset>
            );
          })}
          <label htmlFor={`scope-decision-${caseId}`}>Décision humaine de périmètre</label>
          <select id={`scope-decision-${caseId}`} value={draft.decision} disabled={!!draft.pending} onChange={(event) => updateDraft((current) => ({ ...current, decision: event.target.value as PartnerOfferScopeDecision }))}>
            <option value="NEEDS_CLARIFICATION">À clarifier</option>
            <option value="DIFFERENT_SCOPE">Périmètres différents</option>
            <option value="SAME_SCOPE_CONFIRMED">Même périmètre confirmé par le Patron</option>
          </select>
          {draft.decision === "SAME_SCOPE_CONFIRMED" && sameScopeIncomplete && <p role="status">La confirmation reste bloquée : inclusions, exclusions et transport doivent être explicitement déclarés.</p>}
          <label htmlFor={`scope-rationale-${caseId}`}>Motif de la revue</label>
          <textarea id={`scope-rationale-${caseId}`} required maxLength={2000} value={draft.rationale} disabled={!!draft.pending} onChange={(event) => updateDraft((current) => ({ ...current, rationale: event.target.value }))} />
          <button type="submit" disabled={!canSubmit}>{savingByCase[caseId] ? "Enregistrement…" : draft.pending?.failure === "UNCONFIRMED" ? "Réessayer la même revue" : draft.expectedRevision ? "Enregistrer une nouvelle révision" : "Enregistrer la revue humaine"}</button>
          {draft.pending?.message && <p role="alert">{draft.pending.message}</p>}
          {draft.errorMessage && <p role="alert">{draft.errorMessage}</p>}
          {draft.confirmedMessage && <p role="status">{draft.confirmedMessage}</p>}
        </form>
      )}
      {reviewList?.reviews.map((review) => (
        <article className="detail-panel" key={review.review_id}>
          <h4>{review.comparison_id} · révision {review.revision} · {review.decision}</h4>
          {review.requires_reassessment && <p role="status">REVIEW_REQUIRED · au moins un reçu partenaire a été remplacé ; cette revue historique n’est pas réécrite.</p>}
          <p>{review.rationale} · {review.recorded_at}</p>
          {review.offers.map((offer) => (
            <p key={offer.receipt_event_id}>
              {offer.partner_label} · {offer.inclusion_state} : {offer.included_scope_note ?? "UNKNOWN"} · exclusions {offer.exclusions_state}/{offer.exclusions_review_state}{offer.exclusions.length ? ` : ${offer.exclusions.join("; ")}` : ""} · transport {offer.transport_state}
            </p>
          ))}
          {review.revision === latestRevisionByComparison.get(review.comparison_id) && !review.requires_reassessment && (
            <button type="button" className="secondary-button" onClick={() => revise(review)}>Réviser cette revue</button>
          )}
        </article>
      ))}
    </section>
  );
}
