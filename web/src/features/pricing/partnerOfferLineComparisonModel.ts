import type {
  CaseExecutionCommandReceipt,
  PartnerOfferLineComparison,
  PartnerOfferScopeReview,
  PartnerOfferScopeReviewList,
  RecordPartnerOfferLineComparisonInput,
} from "../../shared/types";

export type FieldKey = "line_locator" | "item_reference" | "designation" | "unit" | "quantity";
export type FieldDraft = { state: "UNKNOWN" | "DECLARED"; value: string | null };
export type MemberDraft = { receipt_event_id: string; fields: Record<FieldKey, FieldDraft> };
export type GroupDraft = {
  group_id: string;
  disposition: "LINKED_BY_PATRON" | "DISTINCT_POSITIONS" | "NEEDS_CLARIFICATION";
  rationale: string;
  members: MemberDraft[];
};
export type Draft = {
  caseId: string;
  scopeReviewId: string;
  scopeReviewRevision: number;
  comparisonId: string;
  recordId: string;
  groups: GroupDraft[];
  stage: "EDITING" | "REVIEW";
  confirmed: boolean;
  input: RecordPartnerOfferLineComparisonInput | null;
};
export type Intent = {
  caseId: string;
  scopeReviewId: string;
  scopeReviewRevision: number;
  input: RecordPartnerOfferLineComparisonInput;
  editableDraft: Draft;
};

export const fields: Array<{ key: FieldKey; label: string; maxLength: number }> = [
  { key: "line_locator", label: "Repère de ligne", maxLength: 500 },
  { key: "item_reference", label: "Référence article", maxLength: 120 },
  { key: "designation", label: "Désignation", maxLength: 500 },
  { key: "unit", label: "Unité", maxLength: 32 },
  { key: "quantity", label: "Quantité", maxLength: 80 },
];

export function emptyFields(): Record<FieldKey, FieldDraft> {
  return Object.fromEntries(fields.map(({ key }) => [key, { state: "UNKNOWN", value: null }])) as Record<FieldKey, FieldDraft>;
}

export function currentScopeReviews(list: PartnerOfferScopeReviewList | null, caseId: string): PartnerOfferScopeReview[] {
  if (!list || list.case_id !== caseId) return [];
  const latest = new Map<string, PartnerOfferScopeReview>();
  for (const review of list.reviews) {
    if (review.revision > (latest.get(review.comparison_id)?.revision ?? 0)) latest.set(review.comparison_id, review);
  }
  return [...latest.values()].sort((left, right) => right.recorded_at.localeCompare(left.recorded_at));
}

export function isComparableScopeReview(review: PartnerOfferScopeReview): boolean {
  return review.decision === "SAME_SCOPE_CONFIRMED"
    && !review.requires_reassessment
    && review.offers.length >= 2
    && review.offers.length <= 20
    && review.offers.every((offer) => offer.receipt_is_current)
    && new Set(review.offers.map((offer) => offer.receipt_event_id)).size === review.offers.length;
}

export function createGroup(review: PartnerOfferScopeReview): GroupDraft {
  return {
    group_id: crypto.randomUUID(),
    disposition: "NEEDS_CLARIFICATION",
    rationale: "",
    members: [...review.offers]
      .sort((left, right) => left.receipt_event_id.localeCompare(right.receipt_event_id))
      .map((offer) => ({ receipt_event_id: offer.receipt_event_id, fields: emptyFields() })),
  };
}

export function makeLineInput(draft: Draft): RecordPartnerOfferLineComparisonInput {
  return {
    command_id: crypto.randomUUID(),
    idempotency_key: crypto.randomUUID(),
    correlation_id: crypto.randomUUID(),
    record_id: draft.recordId,
    comparison_id: draft.comparisonId,
    scope_review_id: draft.scopeReviewId,
    expected_revision: 0,
    groups: draft.groups.map((group) => ({
      group_id: group.group_id,
      disposition: group.disposition,
      rationale: group.rationale.trim(),
      members: group.members.map((member) => Object.fromEntries([
        ["receipt_event_id", member.receipt_event_id],
        ...fields.flatMap(({ key }) => [
          [`${key}_state`, member.fields[key].state],
          [key, member.fields[key].state === "UNKNOWN" ? null : member.fields[key].value?.trim() ?? null],
        ]),
      ])) as RecordPartnerOfferLineComparisonInput["groups"][number]["members"],
    })),
  };
}

export function validateDraft(draft: Draft, scopeReviews: PartnerOfferScopeReviewList | null): string | null {
  const review = scopeReviews?.reviews.find((candidate) => (
    candidate.review_id === draft.scopeReviewId && candidate.revision === draft.scopeReviewRevision
  ));
  if (!review || !currentScopeReviews(scopeReviews, draft.caseId).some((candidate) => candidate.review_id === review.review_id)
    || !isComparableScopeReview(review)) {
    return "La revue ou un reçu a changé. Relisez le périmètre avant de préparer un nouvel acte.";
  }
  if (draft.groups.length < 1 || draft.groups.length > 8
    || new Set(draft.groups.map((group) => group.group_id)).size !== draft.groups.length) {
    return "Ajoutez entre un et huit groupes avec des identifiants distincts.";
  }
  const receiptIds = review.offers.map((offer) => offer.receipt_event_id).sort();
  for (const group of draft.groups) {
    if (!group.rationale.trim() || group.rationale.length > 2_000) return "Chaque groupe exige un motif humain de 1 à 2 000 caractères.";
    if (JSON.stringify(group.members.map((member) => member.receipt_event_id).sort()) !== JSON.stringify(receiptIds)) {
      return "Chaque groupe doit reprendre exactement tous les reçus de la revue.";
    }
    for (const member of group.members) {
      for (const { key, maxLength } of fields) {
        const field = member.fields[key];
        if (field.state === "UNKNOWN" && field.value !== null) return "UNKNOWN doit conserver une valeur nulle.";
        if (field.state === "DECLARED" && (!field.value?.trim() || field.value.length > maxLength)) {
          return `La valeur ${fields.find((item) => item.key === key)?.label ?? key} doit être explicitement renseignée dans la limite de ${maxLength} caractères.`;
        }
      }
    }
  }
  return null;
}

export function receiptMatches(receipt: CaseExecutionCommandReceipt, intent: Intent): boolean {
  return receipt?.status === "SUCCEEDED"
    && receipt.result_code === "PARTNER_OFFER_LINE_COMPARISON_RECORDED"
    && Array.isArray(receipt.aggregate_refs)
    && receipt.aggregate_refs.some((reference) => (
      reference.aggregate_type === "PARTNER_OFFER_LINE_COMPARISON"
      && reference.aggregate_id === intent.input.comparison_id
      && reference.aggregate_revision === intent.input.expected_revision + 1
    ))
    && Array.isArray(receipt.event_ids)
    && receipt.event_ids.length > 0;
}

type ComparableMember = {
  receipt_event_id: string;
  line_locator_state: "UNKNOWN" | "DECLARED"; line_locator: string | null;
  item_reference_state: "UNKNOWN" | "DECLARED"; item_reference: string | null;
  designation_state: "UNKNOWN" | "DECLARED"; designation: string | null;
  unit_state: "UNKNOWN" | "DECLARED"; unit: string | null;
  quantity_state: "UNKNOWN" | "DECLARED"; quantity: string | null;
};

function normalizeGroups(groups: Array<{
  group_id: string;
  disposition: string;
  rationale: string;
  members: ComparableMember[];
}>) {
  return groups.map((group) => ({
    group_id: group.group_id,
    disposition: group.disposition,
    rationale: group.rationale,
    members: group.members.map((member) => ({
      receipt_event_id: member.receipt_event_id,
      line_locator_state: member.line_locator_state,
      line_locator: member.line_locator,
      item_reference_state: member.item_reference_state,
      item_reference: member.item_reference,
      designation_state: member.designation_state,
      designation: member.designation,
      unit_state: member.unit_state,
      unit: member.unit,
      quantity_state: member.quantity_state,
      quantity: member.quantity,
    })).sort((left, right) => left.receipt_event_id.localeCompare(right.receipt_event_id)),
  })).sort((left, right) => left.group_id.localeCompare(right.group_id));
}

export function projectionMatches(comparison: PartnerOfferLineComparison, intent: Intent): boolean {
  if (
    comparison.record_id !== intent.input.record_id
    || comparison.comparison_id !== intent.input.comparison_id
    || comparison.revision !== intent.input.expected_revision + 1
    || comparison.scope_review_id !== intent.scopeReviewId
    || comparison.scope_review_revision !== intent.scopeReviewRevision
    || comparison.scope_review_decision !== "SAME_SCOPE_CONFIRMED"
    || comparison.requires_reassessment
  ) return false;
  return JSON.stringify(normalizeGroups(intent.input.groups)) === JSON.stringify(normalizeGroups(comparison.groups));
}

export function currentReviewMatches(list: PartnerOfferScopeReviewList, intent: Intent): boolean {
  const review = list.reviews.find((candidate) => candidate.review_id === intent.scopeReviewId);
  if (!review || review.revision !== intent.scopeReviewRevision || !isComparableScopeReview(review)) return false;
  const latest = currentScopeReviews(list, intent.caseId).find((candidate) => candidate.comparison_id === review.comparison_id);
  if (!latest || latest.review_id !== review.review_id) return false;
  const receiptIds = review.offers.map((offer) => offer.receipt_event_id).sort();
  return intent.input.groups.every((group) => (
    JSON.stringify(group.members.map((member) => member.receipt_event_id).sort()) === JSON.stringify(receiptIds)
  ));
}
