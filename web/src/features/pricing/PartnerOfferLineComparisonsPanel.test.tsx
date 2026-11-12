import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ApiClient } from "../../infrastructure/api";
import type {
  PartnerOfferLineComparisonList,
  PartnerOfferScopeReviewList,
  RecordPartnerOfferLineComparisonInput,
} from "../../shared/types";
import { PartnerOfferLineComparisonsPanel } from "./PartnerOfferLineComparisonsPanel";

const comparisons: PartnerOfferLineComparisonList = {
  case_id: "case-1",
  comparisons: [
    {
      record_id: "record-2",
      comparison_id: "comparison-1",
      revision: 2,
      scope_review_id: "scope-review-3",
      scope_review_revision: 3,
      scope_review_decision: "SAME_SCOPE_CONFIRMED",
      requires_reassessment: false,
      actor_id: "patron-1",
      recorded_at: "2026-10-07T09:42:00Z",
      groups: [{
        group_id: "group-7",
        disposition: "LINKED_BY_PATRON",
        rationale: "Le repère est commun; la quantité reste à vérifier.",
        members: [
          {
            receipt_event_id: "receipt-alpha-2",
            partner_id: "partner-alpha",
            partner_kind: "SUBCONTRACTOR",
            partner_label: "Partenaire Alpha",
            source_locator: "offre-alpha-v2.pdf · page 4 · ligne 12",
            receipt_is_current: true,
            line_locator_state: "DECLARED",
            line_locator: "tableau A / ligne 12",
            item_reference_state: "DECLARED",
            item_reference: "LOT-04.12",
            designation_state: "DECLARED",
            designation: "Cloison 72 mm",
            unit_state: "DECLARED",
            unit: "m²",
            quantity_state: "DECLARED",
            quantity: "18",
          },
          {
            receipt_event_id: "receipt-beta-1",
            partner_id: "partner-beta",
            partner_kind: "SUPPLIER",
            partner_label: "Partenaire Bêta",
            source_locator: "bordereau-beta.xlsx · feuille Cloisons · ligne 8",
            receipt_is_current: true,
            line_locator_state: "DECLARED",
            line_locator: "Cloisons!8",
            item_reference_state: "UNKNOWN",
            item_reference: null,
            designation_state: "DECLARED",
            designation: "Système de cloison 72 mm",
            unit_state: "DECLARED",
            unit: "m²",
            quantity_state: "UNKNOWN",
            quantity: null,
          },
        ],
      }],
    },
    {
      record_id: "record-1",
      comparison_id: "comparison-1",
      revision: 1,
      scope_review_id: "scope-review-2",
      scope_review_revision: 2,
      scope_review_decision: "NEEDS_CLARIFICATION",
      requires_reassessment: true,
      actor_id: "patron-1",
      recorded_at: "2026-10-05T16:18:00Z",
      groups: [{
        group_id: "group-1",
        disposition: "NEEDS_CLARIFICATION",
        rationale: "La pièce jointe ne précise pas l’unité.",
        members: [{
          receipt_event_id: "receipt-alpha-1",
          partner_id: "partner-alpha",
          partner_kind: "SUBCONTRACTOR",
          partner_label: "Partenaire Alpha",
          source_locator: "offre-alpha-v1.pdf · page 3",
          receipt_is_current: false,
          line_locator_state: "UNKNOWN",
          line_locator: null,
          item_reference_state: "UNKNOWN",
          item_reference: null,
          designation_state: "DECLARED",
          designation: "Cloison en plaques de plâtre",
          unit_state: "UNKNOWN",
          unit: null,
          quantity_state: "UNKNOWN",
          quantity: null,
        }],
      }],
    },
  ],
};

const currentScopeReviews: PartnerOfferScopeReviewList = {
  case_id: "case-1",
  reviews: [{
    review_id: "scope-review-current",
    comparison_id: "scope-comparison-1",
    revision: 3,
    decision: "SAME_SCOPE_CONFIRMED",
    rationale: "Périmètre déclaré commun pour la revue humaine.",
    actor_id: "patron-1",
    recorded_at: "2026-10-08T10:00:00Z",
    requires_reassessment: false,
    offers: [
      {
        receipt_event_id: "receipt-a",
        inclusion_state: "DECLARED",
        included_scope_note: "Lot 4, tel que déclaré.",
        exclusions_review_state: "REVIEWED",
        transport_state: "INCLUDED",
        transport_note: "Transport déclaré inclus.",
        partner_id: "partner-a",
        partner_kind: "SUPPLIER",
        partner_label: "Fournisseur Alpha",
        source_locator: "Offre A · feuille 2",
        source_rationale: "Réponse reçue du fournisseur.",
        validity_current: "UNKNOWN",
        exclusions_state: "DECLARED",
        exclusions: [],
        receipt_is_current: true,
      },
      {
        receipt_event_id: "receipt-b",
        inclusion_state: "DECLARED",
        included_scope_note: "Lot 4, tel que déclaré.",
        exclusions_review_state: "REVIEWED",
        transport_state: "INCLUDED",
        transport_note: "Transport déclaré inclus.",
        partner_id: "partner-b",
        partner_kind: "SUBCONTRACTOR",
        partner_label: "Sous-traitant Bêta",
        source_locator: "Offre B · page 3",
        source_rationale: "Réponse reçue du sous-traitant.",
        validity_current: "UNKNOWN",
        exclusions_state: "DECLARED",
        exclusions: [],
        receipt_is_current: true,
      },
    ],
  }],
};

function projectedLines(input: RecordPartnerOfferLineComparisonInput): PartnerOfferLineComparisonList {
  const review = currentScopeReviews.reviews[0]!;
  return {
    case_id: "case-1",
    comparisons: [{
      record_id: input.record_id,
      comparison_id: input.comparison_id,
      revision: input.expected_revision + 1,
      scope_review_id: input.scope_review_id,
      scope_review_revision: review.revision,
      scope_review_decision: review.decision,
      requires_reassessment: false,
      actor_id: "patron-1",
      recorded_at: "2026-10-08T10:05:00Z",
      groups: input.groups.map((group) => ({
        ...group,
        members: group.members.map((member) => {
          const source = review.offers.find((offer) => offer.receipt_event_id === member.receipt_event_id)!;
          return {
            ...member,
            partner_id: source.partner_id,
            partner_kind: source.partner_kind,
            partner_label: source.partner_label,
            source_locator: source.source_locator,
            receipt_is_current: source.receipt_is_current,
          };
        }),
      })),
    }],
  };
}

function lineReceipt(input: RecordPartnerOfferLineComparisonInput) {
  return {
    status: "SUCCEEDED" as const,
    result_code: "PARTNER_OFFER_LINE_COMPARISON_RECORDED",
    aggregate_refs: [{
      aggregate_type: "PARTNER_OFFER_LINE_COMPARISON",
      aggregate_id: input.comparison_id,
      aggregate_revision: input.expected_revision + 1,
    }],
    event_ids: ["event-line-1"],
    replayed: false,
  };
}

function client(listPartnerOfferLineComparisons: ApiClient["listPartnerOfferLineComparisons"]) {
  return {
    listPartnerOfferLineComparisons,
    listPartnerOfferScopeReviews: vi.fn().mockResolvedValue({ case_id: "case-1", reviews: [] }),
  } as unknown as ApiClient;
}

async function confirmSyntheticLine() {
  fireEvent.change(await screen.findByLabelText("Revue de périmètre à utiliser"), {
    target: { value: "scope-review-current" },
  });
  fireEvent.click(await screen.findByRole("button", { name: "Créer un rapprochement" }));
  fireEvent.change(screen.getByLabelText("Motif humain · obligatoire"), {
    target: { value: "Déclaration humaine synthétique, sans conclure à une couverture." },
  });
  fireEvent.click(screen.getByRole("button", { name: "Vérifier les déclarations" }));
  fireEvent.click(screen.getByRole("checkbox", { name: /J’ai relu les groupes/ }));
  fireEvent.click(screen.getByRole("button", { name: "Confirmer et enregistrer" }));
}

describe("PartnerOfferLineComparisonsPanel", () => {
  it("shows exact review and receipt revisions, explicit field states, and stale history", async () => {
    const read = vi.fn().mockResolvedValue(comparisons);
    render(<PartnerOfferLineComparisonsPanel api={client(read)} caseId="case-1" enabled />);

    expect(await screen.findByText("record-2")).toBeInTheDocument();
    expect(screen.getByText("comparison-1 · révision 2")).toBeInTheDocument();
    expect(screen.getByText("scope-review-3 · révision 3")).toBeInTheDocument();
    expect(screen.getByText("SAME_SCOPE_CONFIRMED")).toBeInTheDocument();
    expect(screen.getByText("receipt-alpha-2")).toBeInTheDocument();
    expect(screen.getByText("record-2").closest("details")).toHaveAttribute("open");
    expect(screen.getByText("offre-alpha-v2.pdf · page 4 · ligne 12")).toBeInTheDocument();
    expect(screen.getAllByText("UNKNOWN")).toHaveLength(6);
    expect(screen.getByText("18")).toBeInTheDocument();
    expect(screen.getByText("REVIEW_REQUIRED")).toBeInTheDocument();
    expect(screen.getByText("record-1").closest("details")).not.toHaveAttribute("open");
    expect(screen.getByText(/Historique conservé/)).toBeInTheDocument();
    expect(screen.getByText("Reçu historique")).toBeInTheDocument();
    expect(screen.getByText("offre-alpha-v1.pdf · page 3")).toBeInTheDocument();
    expect(screen.queryByText(/montant|marge|total/i)).not.toBeInTheDocument();
    expect(read).toHaveBeenCalledOnce();
  });

  it("does not request or reveal private comparisons while disabled", () => {
    const read = vi.fn();
    const readScopes = vi.fn();
    const api = { ...client(read), listPartnerOfferScopeReviews: readScopes } as ApiClient;
    render(<PartnerOfferLineComparisonsPanel api={api} caseId="case-1" enabled={false} />);

    expect(read).not.toHaveBeenCalled();
    expect(readScopes).not.toHaveBeenCalled();
    expect(screen.queryByText("record-2")).not.toBeInTheDocument();
  });

  it("fails closed when the Patron endpoint denies the read", async () => {
    const read = vi.fn().mockRejectedValue({ status: 403 });
    render(<PartnerOfferLineComparisonsPanel api={client(read)} caseId="case-1" enabled />);

    expect(await screen.findByText("FORBIDDEN · lecture privée réservée au Patron habilité.")).toBeInTheDocument();
    expect(screen.queryByText("record-2")).not.toBeInTheDocument();
  });

  it("does not render a response scoped to another case", async () => {
    const read = vi.fn().mockResolvedValue({ ...comparisons, case_id: "case-foreign" });
    render(<PartnerOfferLineComparisonsPanel api={client(read)} caseId="case-1" enabled />);

    expect(await screen.findByText("UNAVAILABLE · les rapprochements n’ont pas pu être relus.")).toBeInTheDocument();
    expect(screen.queryByText("record-2")).not.toBeInTheDocument();
  });

  it("does not render the human command when the scope review is forbidden", async () => {
    const api = {
      ...client(vi.fn().mockResolvedValue(comparisons)),
      listPartnerOfferScopeReviews: vi.fn().mockRejectedValue({ status: 403 }),
      recordPartnerOfferLineComparison: vi.fn(),
    } as ApiClient;
    render(<PartnerOfferLineComparisonsPanel api={api} caseId="case-1" enabled />);

    expect(await screen.findByText("FORBIDDEN · création réservée au Patron Admin FINANCIAL_PRIVATE.")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Créer un rapprochement" })).not.toBeInTheDocument();
    expect(api.recordPartnerOfferLineComparison).not.toHaveBeenCalled();
  });

  it("ignores a late read after the selected case changes", async () => {
    let resolveOld!: (value: PartnerOfferLineComparisonList) => void;
    const old = new Promise<PartnerOfferLineComparisonList>((resolve) => { resolveOld = resolve; });
    const read = vi.fn()
      .mockReturnValueOnce(old)
      .mockResolvedValueOnce({ case_id: "case-2", comparisons: [] });
    const api = client(read);
    const view = render(<PartnerOfferLineComparisonsPanel api={api} caseId="case-1" enabled />);
    view.rerender(<PartnerOfferLineComparisonsPanel api={api} caseId="case-2" enabled />);

    expect(await screen.findByText(/Aucun rapprochement de lignes enregistré/)).toBeInTheDocument();
    await act(async () => resolveOld(comparisons));
    expect(screen.queryByText("record-2")).not.toBeInTheDocument();
  });

  it("requires an explicit human confirmation and sends the exact current review with UNKNOWN fields", async () => {
    let written: RecordPartnerOfferLineComparisonInput | null = null;
    const read = vi.fn().mockImplementation(async () => {
      return written ? projectedLines(written) : { case_id: "case-1", comparisons: [] };
    });
    const record = vi.fn().mockImplementation(async (_caseId: string, input: RecordPartnerOfferLineComparisonInput) => {
      written = input;
      return lineReceipt(input);
    });
    const readScopeReviews = vi.fn().mockResolvedValue(currentScopeReviews);
    const api = {
      ...client(read),
      listPartnerOfferScopeReviews: readScopeReviews,
      recordPartnerOfferLineComparison: record,
    } as ApiClient;
    render(
      <PartnerOfferLineComparisonsPanel
        api={api}
        caseId="case-1"
        enabled
      />,
    );

    fireEvent.change(await screen.findByLabelText("Revue de périmètre à utiliser"), {
      target: { value: "scope-review-current" },
    });
    fireEvent.click(await screen.findByRole("button", { name: "Créer un rapprochement" }));
    expect(screen.getAllByText(/scope-review-current/).length).toBeGreaterThan(0);
    expect(screen.getByText("receipt-a")).toBeInTheDocument();
    expect(screen.getByText("receipt-b")).toBeInTheDocument();
    expect(screen.getAllByText("UNKNOWN · null")).toHaveLength(10);
    expect(record).not.toHaveBeenCalled();

    fireEvent.change(screen.getByLabelText("Motif humain · obligatoire"), {
      target: { value: "Déclarations comparées manuellement, sans conclure à une couverture." },
    });
    fireEvent.click(screen.getByRole("button", { name: "Vérifier les déclarations" }));
    expect(record).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("checkbox", { name: /J’ai relu les groupes/ }));
    fireEvent.click(screen.getByRole("button", { name: "Confirmer et enregistrer" }));

    await waitFor(() => expect(record).toHaveBeenCalledOnce());
    expect(record).toHaveBeenCalledWith("case-1", expect.objectContaining({
      scope_review_id: "scope-review-current",
      expected_revision: 0,
      groups: [expect.objectContaining({
        members: [
          expect.objectContaining({ receipt_event_id: "receipt-a", line_locator_state: "UNKNOWN", line_locator: null }),
          expect.objectContaining({ receipt_event_id: "receipt-b", quantity_state: "UNKNOWN", quantity: null }),
        ],
      })],
    }));
    expect(JSON.stringify(written)).not.toMatch(/amount_as_declared|currency_code|engagement/);
    await waitFor(() => expect(screen.getByText(/Projection relue · acte retrouvé/)).toBeInTheDocument());
    expect(read.mock.calls.length).toBeGreaterThanOrEqual(2);
  });

  it("blocks preparation when the selected scope review or a receipt is stale", async () => {
    const stale: PartnerOfferScopeReviewList = {
      ...currentScopeReviews,
      reviews: [{
        ...currentScopeReviews.reviews[0]!,
        offers: currentScopeReviews.reviews[0]!.offers.map((offer, index) => ({
          ...offer,
          receipt_is_current: index !== 0,
        })),
      }],
    };
    const record = vi.fn();
    const api = {
      ...client(vi.fn().mockResolvedValue({ case_id: "case-1", comparisons: [] })),
      listPartnerOfferScopeReviews: vi.fn().mockResolvedValue(stale),
      recordPartnerOfferLineComparison: record,
    } as ApiClient;
    render(<PartnerOfferLineComparisonsPanel api={api} caseId="case-1" enabled />);

    expect(await screen.findByText(/aucune revue SAME_SCOPE_CONFIRMED actuelle/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Créer un rapprochement" })).toBeDisabled();
    expect(record).not.toHaveBeenCalled();
  });

  it("retries an UNKNOWN POST with the identical body and performs GET only after a receipt", async () => {
    let written: RecordPartnerOfferLineComparisonInput | null = null;
    const read = vi.fn().mockImplementation(async () => written ? projectedLines(written) : { case_id: "case-1", comparisons: [] });
    const record = vi.fn()
      .mockImplementationOnce(async (_caseId: string, input: RecordPartnerOfferLineComparisonInput) => {
        written = input;
        throw new Error("transport ended without a response");
      })
      .mockImplementationOnce(async (_caseId: string, input: RecordPartnerOfferLineComparisonInput) => {
        written = input;
        return lineReceipt(input);
      });
    const readScopeReviews = vi.fn().mockResolvedValue(currentScopeReviews);
    const api = { ...client(read), listPartnerOfferScopeReviews: readScopeReviews, recordPartnerOfferLineComparison: record } as ApiClient;
    render(<PartnerOfferLineComparisonsPanel api={api} caseId="case-1" enabled />);

    await confirmSyntheticLine();
    expect(await screen.findByText(/UNKNOWN · résultat du POST non confirmé/)).toBeInTheDocument();
    expect(record).toHaveBeenCalledOnce();
    expect(read).toHaveBeenCalledOnce();
    expect(screen.getByRole("button", { name: "Réessayer la même intention" })).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Réessayer la même intention" }));
    await waitFor(() => expect(record).toHaveBeenCalledTimes(2));
    expect(record.mock.calls[0]).toEqual(record.mock.calls[1]);
    await waitFor(() => expect(screen.getByText(/Projection relue · acte retrouvé/)).toBeInTheDocument());
    expect(read).toHaveBeenCalledTimes(2);
  });

  it("a 409 permits GET rereads only and never retries the write", async () => {
    const changedReview: PartnerOfferScopeReviewList = {
      ...currentScopeReviews,
      reviews: [{ ...currentScopeReviews.reviews[0]!, review_id: "scope-review-next", revision: 4 }],
    };
    const readScopeReviews = vi.fn()
      .mockResolvedValueOnce(currentScopeReviews)
      .mockResolvedValueOnce(changedReview);
    const read = vi.fn().mockResolvedValue({ case_id: "case-1", comparisons: [] });
    const record = vi.fn().mockRejectedValue({ status: 409, detail: "PARTNER_OFFER_LINE_COMPARISON_VERSION_CONFLICT" });
    const api = { ...client(read), listPartnerOfferScopeReviews: readScopeReviews, recordPartnerOfferLineComparison: record } as ApiClient;
    render(<PartnerOfferLineComparisonsPanel api={api} caseId="case-1" enabled />);

    await confirmSyntheticLine();
    expect(await screen.findByText(/409 · l’état courant a été relu/)).toBeInTheDocument();
    expect(record).toHaveBeenCalledOnce();
    expect(read).toHaveBeenCalledTimes(2);
    expect(readScopeReviews).toHaveBeenCalledTimes(2);
    expect(screen.queryByRole("button", { name: "Réessayer la même intention" })).not.toBeInTheDocument();
  });

  it("keeps the receipt after a failed GET and recovers through a GET-only reread", async () => {
    let written: RecordPartnerOfferLineComparisonInput | null = null;
    const read = vi.fn()
      .mockResolvedValueOnce({ case_id: "case-1", comparisons: [] })
      .mockRejectedValueOnce({ status: 503 })
      .mockImplementationOnce(async () => written ? projectedLines(written) : { case_id: "case-1", comparisons: [] });
    const record = vi.fn().mockImplementation(async (_caseId: string, input: RecordPartnerOfferLineComparisonInput) => {
      written = input;
      return lineReceipt(input);
    });
    const api = {
      ...client(read),
      listPartnerOfferScopeReviews: vi.fn().mockResolvedValue(currentScopeReviews),
      recordPartnerOfferLineComparison: record,
    } as ApiClient;
    render(<PartnerOfferLineComparisonsPanel api={api} caseId="case-1" enabled />);

    await confirmSyntheticLine();
    expect(await screen.findByText(/relecture GET est indisponible/)).toBeInTheDocument();
    expect(screen.getByText("PARTNER_OFFER_LINE_COMPARISON_RECORDED")).toBeInTheDocument();
    expect(record).toHaveBeenCalledOnce();
    fireEvent.click(screen.getByRole("button", { name: "Relire uniquement (GET)" }));
    await waitFor(() => expect(screen.getByText(/Projection relue · acte retrouvé/)).toBeInTheDocument());
    expect(record).toHaveBeenCalledOnce();
    expect(read).toHaveBeenCalledTimes(3);
  });

  it("does not infer success from a discordant projection and rereads by GET only", async () => {
    let written: RecordPartnerOfferLineComparisonInput | null = null;
    let rereads = 0;
    const read = vi.fn().mockImplementation(async () => {
      if (!written) return { case_id: "case-1", comparisons: [] };
      rereads += 1;
      const projection = projectedLines(written);
      if (rereads === 1) projection.comparisons[0]!.scope_review_revision = 2;
      return projection;
    });
    const record = vi.fn().mockImplementation(async (_caseId: string, input: RecordPartnerOfferLineComparisonInput) => {
      written = input;
      return lineReceipt(input);
    });
    const api = {
      ...client(read),
      listPartnerOfferScopeReviews: vi.fn().mockResolvedValue(currentScopeReviews),
      recordPartnerOfferLineComparison: record,
    } as ApiClient;
    render(<PartnerOfferLineComparisonsPanel api={api} caseId="case-1" enabled />);

    await confirmSyntheticLine();
    expect(await screen.findByText(/réponse technique et la projection relue ne concordent pas/)).toBeInTheDocument();
    expect(record).toHaveBeenCalledOnce();
    fireEvent.click(screen.getByRole("button", { name: "Relire uniquement (GET)" }));
    await waitFor(() => expect(screen.getByText(/Projection relue · acte retrouvé/)).toBeInTheDocument());
    expect(record).toHaveBeenCalledOnce();
    expect(read).toHaveBeenCalledTimes(3);
  });
});
