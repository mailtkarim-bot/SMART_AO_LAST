import { useEffect, useRef, useState, type FormEvent } from "react";

import type { ApiClient } from "../../infrastructure/api";
import type {
  CaseExecutionCommandReceipt,
  PartnerOfferLineComparisonList,
  PartnerOfferScopeReview,
  PartnerOfferScopeReviewList,
} from "../../shared/types";
import { PartnerOfferLineComparisonDraft } from "./PartnerOfferLineComparisonDraft";
import {
  createGroup,
  currentReviewMatches,
  currentScopeReviews,
  isComparableScopeReview,
  makeLineInput,
  projectionMatches,
  receiptMatches,
  validateDraft,
  type Draft,
  type GroupDraft,
  type Intent,
} from "./partnerOfferLineComparisonModel";

type ReadStatus = "LOADING" | "READY" | "FORBIDDEN" | "UNAVAILABLE" | "NO_CASE" | "INACTIVE";
type CommandPhase = "SENDING" | "UNKNOWN" | "READING" | "READ_UNKNOWN" | "CONFLICT" | "MISMATCH" | "REVIEW_REQUIRED" | "COMPLETE";
type PendingCommand = {
  caseId: string;
  intent: Intent;
  phase: CommandPhase;
  rereadKind: "RECEIPT" | "CONFLICT";
  receipt: CaseExecutionCommandReceipt | null;
  receiptMatchesIntent: boolean;
  message: string;
};

function apiErrorStatus(error: unknown): number | undefined {
  const value = (error as { status?: unknown })?.status;
  return typeof value === "number" ? value : undefined;
}

export function PartnerOfferLineComparisonCommand({
  api,
  caseId,
  enabled,
  onComparisonsRead,
}: {
  api: ApiClient;
  caseId: string;
  enabled: boolean;
  onComparisonsRead: (list: PartnerOfferLineComparisonList) => void;
}) {
  const [scopeStatus, setScopeStatus] = useState<ReadStatus>(() => !enabled ? "INACTIVE" : caseId ? "LOADING" : "NO_CASE");
  const [scopeList, setScopeList] = useState<PartnerOfferScopeReviewList | null>(null);
  const [selectedReviewByCase, setSelectedReviewByCase] = useState<Record<string, string>>({});
  const [draftByCase, setDraftByCase] = useState<Record<string, Draft>>({});
  const [pendingByCase, setPendingByCase] = useState<Record<string, PendingCommand | undefined>>({});
  const [archivedByCase, setArchivedByCase] = useState<Record<string, PendingCommand[]>>({});
  const [errorByCase, setErrorByCase] = useState<Record<string, string>>({});
  const [savingByCase, setSavingByCase] = useState<Record<string, boolean>>({});
  const inFlight = useRef(new Set<string>());
  const draft = draftByCase[caseId] ?? null;
  const pending = pendingByCase[caseId] ?? null;
  const selectedReviewId = selectedReviewByCase[caseId] ?? "";
  const latestReviews = currentScopeReviews(scopeList, caseId);
  const selectedReview = latestReviews.find((review) => review.review_id === selectedReviewId && isComparableScopeReview(review));

  useEffect(() => {
    if (!enabled) {
      setScopeStatus("INACTIVE");
      setScopeList(null);
      return;
    }
    if (!caseId) {
      setScopeStatus("NO_CASE");
      setScopeList(null);
      return;
    }
    let active = true;
    setScopeStatus("LOADING");
    setScopeList(null);
    void api.listPartnerOfferScopeReviews(caseId).then((result) => {
      if (!active) return;
      if (result.case_id !== caseId || !Array.isArray(result.reviews)) {
        setScopeStatus("UNAVAILABLE");
        return;
      }
      setScopeList(result);
      setScopeStatus("READY");
    }).catch((error: unknown) => {
      if (!active) return;
      setScopeList(null);
      setScopeStatus(apiErrorStatus(error) === 403 ? "FORBIDDEN" : "UNAVAILABLE");
    });
    return () => { active = false; };
  }, [api, caseId, enabled]);

  function setDraft(update: (current: Draft) => Draft) {
    setDraftByCase((current) => {
      const existing = current[caseId];
      return existing ? { ...current, [caseId]: update(existing) } : current;
    });
  }

  function startDraft(review: PartnerOfferScopeReview) {
    if (inFlight.current.has(caseId) || (pending && !["COMPLETE", "CONFLICT"].includes(pending.phase))) return;
    if (pending) setArchivedByCase((current) => ({ ...current, [caseId]: [...(current[caseId] ?? []), pending] }));
    const newDraft: Draft = {
      caseId,
      scopeReviewId: review.review_id,
      scopeReviewRevision: review.revision,
      comparisonId: crypto.randomUUID(),
      recordId: crypto.randomUUID(),
      groups: [createGroup(review)],
      stage: "EDITING",
      confirmed: false,
      input: null,
    };
    setDraftByCase((current) => ({ ...current, [caseId]: newDraft }));
    setPendingByCase((current) => ({ ...current, [caseId]: undefined }));
    setErrorByCase((current) => ({ ...current, [caseId]: "" }));
  }

  function updateGroup(groupIndex: number, update: (group: GroupDraft) => GroupDraft) {
    setDraft((current) => ({
      ...current,
      groups: current.groups.map((group, index) => index === groupIndex ? update(group) : group),
    }));
  }

  function prepareReview(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!draft || draft.stage !== "EDITING") return;
    const problem = validateDraft(draft, scopeList);
    if (problem) {
      setErrorByCase((current) => ({ ...current, [caseId]: problem }));
      return;
    }
    const input = makeLineInput(draft);
    setDraft((current) => ({ ...current, stage: "REVIEW", confirmed: false, input }));
    setErrorByCase((current) => ({ ...current, [caseId]: "" }));
  }

  async function reread(intent: Intent, receipt: CaseExecutionCommandReceipt | null, receiptMatches: boolean, rereadKind: "RECEIPT" | "CONFLICT") {
    setPendingByCase((current) => ({
      ...current,
      [intent.caseId]: {
        caseId: intent.caseId,
        intent,
        phase: "READING",
        rereadKind,
        receipt,
        receiptMatchesIntent: receiptMatches,
        message: "Relecture GET en cours. Le reçu technique seul ne confirme pas la projection.",
      },
    }));
    const [scopeResult, comparisonResult] = await Promise.allSettled([
      api.listPartnerOfferScopeReviews(intent.caseId),
      api.listPartnerOfferLineComparisons(intent.caseId),
    ]);
    const scopeRead = scopeResult.status === "fulfilled"
      && scopeResult.value.case_id === intent.caseId
      && Array.isArray(scopeResult.value.reviews)
      ? scopeResult.value
      : null;
    const comparisonRead = comparisonResult.status === "fulfilled"
      && comparisonResult.value.case_id === intent.caseId
      && Array.isArray(comparisonResult.value.comparisons)
      ? comparisonResult.value
      : null;
    if (intent.caseId === caseId) {
      if (scopeRead) {
        setScopeList(scopeRead);
        setScopeStatus("READY");
      } else {
        setScopeStatus(scopeResult.status === "rejected" && apiErrorStatus(scopeResult.reason) === 403 ? "FORBIDDEN" : "UNAVAILABLE");
      }
      if (comparisonRead) onComparisonsRead(comparisonRead);
    }
    if (!scopeRead || !comparisonRead) {
      setPendingByCase((current) => ({
        ...current,
        [intent.caseId]: {
          caseId: intent.caseId,
          intent,
          phase: "READ_UNKNOWN",
          rereadKind,
          receipt,
          receiptMatchesIntent: receiptMatches,
          message: "UNKNOWN · la relecture GET est indisponible ou discordante. L’intention et le reçu éventuel sont conservés; seule une nouvelle relecture GET est permise.",
        },
      }));
      return;
    }

    const refreshedScopes = scopeRead;
    const refreshedComparisons = comparisonRead;
    if (rereadKind === "CONFLICT") {
      setPendingByCase((current) => ({
        ...current,
        [intent.caseId]: {
          caseId: intent.caseId,
          intent,
          phase: "CONFLICT",
          rereadKind,
          receipt: null,
          receiptMatchesIntent: false,
          message: "409 · l’état courant a été relu. Aucun retry POST n’est autorisé; choisissez ensuite une nouvelle intention depuis une revue actuelle.",
        },
      }));
      return;
    }

    const currentReview = currentScopeReviews(refreshedScopes, intent.caseId)
      .find((review) => review.review_id === intent.scopeReviewId);
    if (!currentReview || currentReview.revision !== intent.scopeReviewRevision || !currentReviewMatches(refreshedScopes, intent)) {
      setPendingByCase((current) => ({
        ...current,
        [intent.caseId]: {
          caseId: intent.caseId,
          intent,
          phase: "REVIEW_REQUIRED",
          rereadKind,
          receipt,
          receiptMatchesIntent: receiptMatches,
          message: "REVIEW_REQUIRED · la revue, sa révision ou un reçu a changé. Le reçu éventuel est conservé et la déclaration n’est pas présentée comme actuelle.",
        },
      }));
      return;
    }
    const comparison = refreshedComparisons.comparisons.find((candidate) => (
      candidate.record_id === intent.input.record_id
      && candidate.comparison_id === intent.input.comparison_id
      && candidate.revision === intent.input.expected_revision + 1
    ));
    if (!receiptMatches || !receipt || !comparison || !projectionMatches(comparison, intent)) {
      setPendingByCase((current) => ({
        ...current,
        [intent.caseId]: {
          caseId: intent.caseId,
          intent,
          phase: "MISMATCH",
          rereadKind,
          receipt,
          receiptMatchesIntent: receiptMatches,
          message: "UNKNOWN / REVIEW_REQUIRED · la réponse technique et la projection relue ne concordent pas exactement. Aucune réussite n’est déduite; seule une relecture GET reste disponible.",
        },
      }));
      return;
    }
    setPendingByCase((current) => ({
      ...current,
      [intent.caseId]: {
        caseId: intent.caseId,
        intent,
        phase: "COMPLETE",
        rereadKind,
        receipt,
        receiptMatchesIntent: true,
        message: "Projection relue · acte retrouvé avec la révision, la revue et les déclarations exactes.",
      },
    }));
  }

  async function refreshCurrentState() {
    if (!caseId || !enabled || draft || savingByCase[caseId] === true || pending?.phase === "UNKNOWN" || pending?.phase === "SENDING" || pending?.phase === "READING") return;
    if (pending) {
      await reread(pending.intent, pending.receipt, pending.receiptMatchesIntent, pending.rereadKind);
      return;
    }
    setScopeStatus("LOADING");
    const [scopeResult, comparisonResult] = await Promise.allSettled([
      api.listPartnerOfferScopeReviews(caseId),
      api.listPartnerOfferLineComparisons(caseId),
    ]);
    if (scopeResult.status === "fulfilled" && scopeResult.value.case_id === caseId && Array.isArray(scopeResult.value.reviews)) {
      setScopeList(scopeResult.value);
      setScopeStatus("READY");
    } else {
      setScopeStatus(scopeResult.status === "rejected" && apiErrorStatus(scopeResult.reason) === 403 ? "FORBIDDEN" : "UNAVAILABLE");
    }
    if (comparisonResult.status === "fulfilled" && comparisonResult.value.case_id === caseId && Array.isArray(comparisonResult.value.comparisons)) {
      onComparisonsRead(comparisonResult.value);
    }
  }

  async function sendIntent(intent: Intent) {
    if (inFlight.current.has(intent.caseId)) return;
    inFlight.current.add(intent.caseId);
    setSavingByCase((current) => ({ ...current, [intent.caseId]: true }));
    setPendingByCase((current) => ({
      ...current,
      [intent.caseId]: {
        caseId: intent.caseId,
        intent,
        phase: "SENDING",
        rereadKind: "RECEIPT",
        receipt: null,
        receiptMatchesIntent: false,
        message: "Écriture humaine en cours.",
      },
    }));
    try {
      const receipt = await api.recordPartnerOfferLineComparison(intent.caseId, intent.input);
      await reread(intent, receipt, receiptMatches(receipt, intent), "RECEIPT");
    } catch (error) {
      const responseStatus = apiErrorStatus(error);
      if (responseStatus === 409) {
        await reread(intent, null, false, "CONFLICT");
      } else if (responseStatus === undefined || responseStatus >= 500) {
        setPendingByCase((current) => ({
          ...current,
          [intent.caseId]: {
            caseId: intent.caseId,
            intent,
            phase: "UNKNOWN",
            rereadKind: "RECEIPT",
            receipt: null,
            receiptMatchesIntent: false,
            message: "UNKNOWN · résultat du POST non confirmé. Corps et identités figés; seul le retry exact de cette intention est autorisé.",
          },
        }));
      } else {
        setPendingByCase((current) => ({ ...current, [intent.caseId]: undefined }));
        setDraftByCase((current) => ({
          ...current,
          [intent.caseId]: { ...intent.editableDraft, stage: "EDITING", confirmed: false, input: null },
        }));
        setErrorByCase((current) => ({ ...current, [intent.caseId]: `Refus confirmé · aucune déclaration n’a été enregistrée (HTTP ${responseStatus}).` }));
      }
    } finally {
      inFlight.current.delete(intent.caseId);
      setSavingByCase((current) => ({ ...current, [intent.caseId]: false }));
    }
  }

  async function confirmIntent() {
    if (!draft || draft.stage !== "REVIEW" || !draft.confirmed || !draft.input || pending) return;
    const problem = validateDraft(draft, scopeList);
    if (problem) {
      setErrorByCase((current) => ({ ...current, [caseId]: problem }));
      return;
    }
    setDraftByCase((current) => {
      const next = { ...current };
      delete next[caseId];
      return next;
    });
    await sendIntent({
      caseId: draft.caseId,
      scopeReviewId: draft.scopeReviewId,
      scopeReviewRevision: draft.scopeReviewRevision,
      input: draft.input,
      editableDraft: draft,
    });
  }

  function archivePendingAndResetSelection() {
    if (pending) setArchivedByCase((current) => ({ ...current, [caseId]: [...(current[caseId] ?? []), pending] }));
    setPendingByCase((current) => ({ ...current, [caseId]: undefined }));
    setSelectedReviewByCase((current) => ({ ...current, [caseId]: "" }));
  }

  const scopeOptions = currentScopeReviews(scopeList, caseId);
  const canStart = !!selectedReview
    && enabled
    && scopeStatus === "READY"
    && !draft
    && !savingByCase[caseId]
    && (!pending || ["COMPLETE", "CONFLICT"].includes(pending.phase));

  if (!enabled) return null;

  return (
      <div className="partner-line-command-panel" aria-label="Commande humaine de rapprochement de lignes C08">
      <div className="partner-line-command-toolbar">
        <p>Revue de périmètre source · FINANCIAL_PRIVATE</p>
        <button
          type="button"
          className="secondary-button"
          onClick={() => void refreshCurrentState()}
          disabled={!caseId || scopeStatus === "LOADING" || !!draft || pending?.phase === "UNKNOWN" || pending?.phase === "SENDING" || pending?.phase === "READING" || savingByCase[caseId] === true}
        >
          {scopeStatus === "LOADING" ? "Chargement…" : pending ? "Relire uniquement (GET)" : "Actualiser les revues et rapprochements"}
        </button>
      </div>

      {scopeStatus === "LOADING" && <p role="status">Lecture de la revue de périmètre source…</p>}
      {scopeStatus === "NO_CASE" && <p role="status">UNKNOWN · sélectionnez une Affaire.</p>}
      {scopeStatus === "INACTIVE" && <p role="status">Ouvrez C08 pour lire les revues privées.</p>}
      {scopeStatus === "FORBIDDEN" && <p role="status">FORBIDDEN · création réservée au Patron Admin FINANCIAL_PRIVATE.</p>}
      {scopeStatus === "UNAVAILABLE" && <p role="status">UNKNOWN · la revue de périmètre n’a pas pu être relue; préparation bloquée.</p>}

      <section className="partner-line-command" aria-label="Déclaration humaine d’un rapprochement">
        <div className="partner-line-command-heading">
          <div>
            <h4>Déclarer un rapprochement de lignes</h4>
            <p>Choisissez une revue actuelle et ses reçus exacts. Aucun calcul ni engagement n’est produit.</p>
          </div>
          {pending?.phase === "COMPLETE" && <span className="partner-line-state">Projection relue</span>}
        </div>

        {scopeStatus === "READY" && (
          <div className="partner-line-scope-picker">
            <label htmlFor={`line-scope-review-${caseId}`}>Revue de périmètre à utiliser</label>
            <select
              id={`line-scope-review-${caseId}`}
              value={selectedReviewId}
              disabled={!!draft || (!!pending && !["COMPLETE", "CONFLICT"].includes(pending.phase))}
              onChange={(event) => setSelectedReviewByCase((current) => ({ ...current, [caseId]: event.target.value }))}
            >
              <option value="">Choisissez une revue actuelle…</option>
              {scopeOptions.map((review) => (
                <option key={review.review_id} value={review.review_id} disabled={!isComparableScopeReview(review)}>
                  {review.review_id} · rév. {review.revision} · {review.decision}{review.requires_reassessment || review.offers.some((offer) => !offer.receipt_is_current) ? " · REVIEW_REQUIRED" : ""}
                </option>
              ))}
            </select>
            {scopeOptions.length === 0 && <p role="status">UNKNOWN · aucune revue de périmètre relue.</p>}
            {scopeOptions.length > 0 && !scopeOptions.some(isComparableScopeReview) && (
              <p role="status">UNKNOWN / REVIEW_REQUIRED · aucune revue SAME_SCOPE_CONFIRMED actuelle avec tous ses reçus courants.</p>
            )}
            <button type="button" onClick={() => selectedReview && startDraft(selectedReview)} disabled={!canStart}>
              Créer un rapprochement
            </button>
          </div>
        )}

        <PartnerOfferLineComparisonDraft
          draft={draft?.caseId === caseId && !pending ? draft : null}
          scopeList={scopeList}
          error={errorByCase[caseId]}
          saving={savingByCase[caseId] === true}
          onGroupUpdate={updateGroup}
          onAddGroup={() => setDraft((current) => {
            const review = scopeList?.reviews.find((candidate) => candidate.review_id === current.scopeReviewId);
            return review ? { ...current, groups: [...current.groups, createGroup(review)] } : current;
          })}
          onRemoveGroup={(groupIndex) => setDraft((current) => ({
            ...current,
            groups: current.groups.filter((_, index) => index !== groupIndex),
          }))}
          onCancel={() => setDraftByCase((current) => {
            const next = { ...current };
            delete next[caseId];
            return next;
          })}
          onPrepare={prepareReview}
          onBack={() => setDraft((current) => ({ ...current, stage: "EDITING", confirmed: false, input: null }))}
          onConfirmChange={(confirmed) => setDraft((current) => ({ ...current, confirmed }))}
          onConfirm={() => void confirmIntent()}
        />

        {pending && (
          <div className="partner-line-command-outcome" aria-live="polite">
            <p role="status">{pending.message}</p>
            {pending.receipt && (
              <details>
                <summary>Réponse technique conservée</summary>
                <dl>
                  <dt>Résultat</dt><dd>{pending.receipt.result_code}</dd>
                  <dt>Comparaison exacte</dt><dd><code>{pending.intent.input.comparison_id} · révision {pending.intent.input.expected_revision + 1}</code></dd>
                  <dt>Événements techniques</dt><dd><code>{pending.receipt.event_ids.join(" · ") || "UNKNOWN"}</code></dd>
                </dl>
              </details>
            )}
            {pending.phase === "UNKNOWN" && (
              <button type="button" onClick={() => void sendIntent(pending.intent)} disabled={savingByCase[caseId] === true}>
                Réessayer la même intention
              </button>
            )}
            {pending.phase === "CONFLICT" && (
              <button type="button" className="secondary-button" onClick={archivePendingAndResetSelection}>
                Après relecture, choisir une nouvelle intention
              </button>
            )}
            {pending.phase === "REVIEW_REQUIRED" && (
              <button type="button" className="secondary-button" onClick={archivePendingAndResetSelection}>
                Conserver la réponse technique et choisir une revue actuelle
              </button>
            )}
          </div>
        )}
        {(archivedByCase[caseId] ?? []).length > 0 && (
          <details className="partner-line-command-archive">
            <summary>Réponses techniques antérieures conservées · {(archivedByCase[caseId] ?? []).length}</summary>
            {(archivedByCase[caseId] ?? []).map((archived, index) => (
              <p key={`${archived.intent.input.command_id}-${index}`}>
                {archived.phase} · <code>{archived.intent.input.comparison_id}</code> · revue <code>{archived.intent.scopeReviewId} · rév. {archived.intent.scopeReviewRevision}</code>
                {archived.receipt?.event_ids.length ? <> · événements <code>{archived.receipt.event_ids.join(" · ")}</code></> : null}
              </p>
            ))}
          </details>
        )}
      </section>
      </div>
  );
}
