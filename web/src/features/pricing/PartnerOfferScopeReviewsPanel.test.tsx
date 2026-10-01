import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ApiClient } from "../../infrastructure/api";
import type { PartnerOfferPriceView, PartnerOfferScopeReviewList } from "../../shared/types";
import { PartnerOfferScopeReviewsPanel } from "./PartnerOfferScopeReviewsPanel";

function offer(
  receiptEventId: string,
  partnerLabel: string,
  exclusionsState: "UNKNOWN" | "DECLARED" = "DECLARED",
): PartnerOfferPriceView {
  return {
    receipt_event_id: receiptEventId,
    partner_id: `partner-${receiptEventId}`,
    partner_kind: "SUPPLIER",
    partner_label: partnerLabel,
    partner_revision: 1,
    source_locator: `offer://${receiptEventId}`,
    source_rationale: `Périmètre déclaré ${partnerLabel}`,
    valid_until: null,
    validity_current: "UNKNOWN",
    exclusions_state: exclusionsState,
    exclusions: exclusionsState === "UNKNOWN" ? [] : [`Exclusion ${partnerLabel}`],
    mandate_state: "NOT_APPLICABLE",
    is_latest_receipt: true,
    price_state: "UNKNOWN",
    declarations: [],
  };
}

function apiClient(api: Partial<ApiClient>) {
  return api as ApiClient;
}

function emptyReviews(): PartnerOfferScopeReviewList {
  return { case_id: "case-1", reviews: [] };
}

describe("PartnerOfferScopeReviewsPanel", () => {
  it("records a human same-scope review against the exact receipts without amounts", async () => {
    const api = {
      listPartnerOfferScopeReviews: vi.fn().mockResolvedValue(emptyReviews()),
      recordPartnerOfferScopeReview: vi.fn().mockResolvedValue({
        status: "SUCCEEDED",
        result_code: "PARTNER_SCOPE_REVIEW_RECORDED",
        aggregate_refs: [],
        event_ids: ["review-1"],
        replayed: false,
      }),
    };
    render(
      <PartnerOfferScopeReviewsPanel
        api={apiClient(api)}
        caseId="case-1"
        offers={[offer("r1", "Fournisseur A"), offer("r2", "Fournisseur B")]}
        enabled
      />,
    );

    await screen.findByText("Le Patron consigne si les offres couvrent le même périmètre ; l’application ne le déduit pas et ne calcule aucun coût couvert.");
    fireEvent.click(screen.getByRole("button", { name: "Nouvelle comparaison" }));
    fireEvent.click(screen.getByLabelText(/Fournisseur A/));
    fireEvent.click(screen.getByLabelText(/Fournisseur B/));
    const inclusionStates = screen.getAllByLabelText("État du périmètre inclus");
    for (const input of inclusionStates) {
      fireEvent.change(input, { target: { value: "DECLARED" } });
    }
    const inclusionNotes = screen.getAllByLabelText("Périmètre inclus tel que relu");
    for (const [index, input] of inclusionNotes.entries()) {
      fireEvent.change(input, { target: { value: `Périmètre inclus ${index + 1}` } });
    }
    const exclusionReviews = screen.getAllByLabelText("Revue humaine des exclusions");
    for (const input of exclusionReviews) {
      fireEvent.change(input, { target: { value: "REVIEWED" } });
    }
    const transportStates = screen.getAllByLabelText("Traitement du transport");
    for (const input of transportStates) {
      fireEvent.change(input, { target: { value: "INCLUDED" } });
    }
    const transportNotes = screen.getAllByLabelText("Note source sur le transport");
    for (const [index, input] of transportNotes.entries()) {
      fireEvent.change(input, { target: { value: `Transport ${index + 1}` } });
    }
    fireEvent.change(screen.getByLabelText("Décision humaine de périmètre"), {
      target: { value: "SAME_SCOPE_CONFIRMED" },
    });
    fireEvent.change(screen.getByLabelText("Motif de la revue"), {
      target: { value: "Les sources indiquent le même périmètre." },
    });
    fireEvent.submit(screen.getByRole("form", { name: "Enregistrer une revue de périmètre" }));

    await waitFor(() => expect(api.recordPartnerOfferScopeReview).toHaveBeenCalledOnce());
    const input = api.recordPartnerOfferScopeReview.mock.calls[0]?.[1];
    expect(input).toMatchObject({
      expected_revision: 0,
      decision: "SAME_SCOPE_CONFIRMED",
      offers: [
        expect.objectContaining({ receipt_event_id: "r1", transport_state: "INCLUDED" }),
        expect.objectContaining({ receipt_event_id: "r2", transport_state: "INCLUDED" }),
      ],
    });
    expect(JSON.stringify(input)).not.toContain("amount_as_declared");
  });

  it("does not allow SAME_SCOPE_CONFIRMED when exclusions are unknown or not reviewed", async () => {
    const api = {
      listPartnerOfferScopeReviews: vi.fn().mockResolvedValue(emptyReviews()),
      recordPartnerOfferScopeReview: vi.fn(),
    };
    render(
      <PartnerOfferScopeReviewsPanel
        api={apiClient(api)}
        caseId="case-1"
        offers={[offer("r1", "Fournisseur A", "UNKNOWN"), offer("r2", "Fournisseur B")]}
        enabled
      />,
    );
    await screen.findByRole("heading", { name: "Revue humaine des périmètres" });
    fireEvent.click(screen.getByRole("button", { name: "Nouvelle comparaison" }));
    fireEvent.click(screen.getByLabelText(/Fournisseur A/));
    fireEvent.click(screen.getByLabelText(/Fournisseur B/));
    fireEvent.change(screen.getAllByLabelText("Revue humaine des exclusions")[0]!, {
      target: { value: "REVIEWED" },
    });
    fireEvent.change(screen.getByLabelText("Décision humaine de périmètre"), {
      target: { value: "SAME_SCOPE_CONFIRMED" },
    });
    expect(screen.getByText(/La confirmation reste bloquée/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Enregistrer la revue humaine" })).toBeDisabled();
    expect(api.recordPartnerOfferScopeReview).not.toHaveBeenCalled();
  });

  it("requires explicit review of known exclusions before confirming same scope", async () => {
    const api = {
      listPartnerOfferScopeReviews: vi.fn().mockResolvedValue(emptyReviews()),
      recordPartnerOfferScopeReview: vi.fn(),
    };
    render(
      <PartnerOfferScopeReviewsPanel
        api={apiClient(api)}
        caseId="case-1"
        offers={[offer("r1", "Fournisseur A"), offer("r2", "Fournisseur B")]}
        enabled
      />,
    );
    await screen.findByRole("heading", { name: "Revue humaine des périmètres" });
    fireEvent.click(screen.getByRole("button", { name: "Nouvelle comparaison" }));
    fireEvent.click(screen.getByLabelText(/Fournisseur A/));
    fireEvent.click(screen.getByLabelText(/Fournisseur B/));
    fireEvent.change(screen.getByLabelText("Décision humaine de périmètre"), {
      target: { value: "SAME_SCOPE_CONFIRMED" },
    });
    expect(screen.getByText(/La confirmation reste bloquée/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Enregistrer la revue humaine" })).toBeDisabled();
    expect(api.recordPartnerOfferScopeReview).not.toHaveBeenCalled();
  });

  it("reuses the same review and idempotency identifiers after an unknown response", async () => {
    const api = {
      listPartnerOfferScopeReviews: vi.fn().mockResolvedValue(emptyReviews()),
      recordPartnerOfferScopeReview: vi.fn()
        .mockRejectedValueOnce({ status: 500 })
        .mockResolvedValueOnce({ status: "SUCCEEDED", result_code: "PARTNER_SCOPE_REVIEW_RECORDED", aggregate_refs: [], event_ids: [], replayed: true }),
    };
    render(
      <PartnerOfferScopeReviewsPanel
        api={apiClient(api)}
        caseId="case-1"
        offers={[offer("r1", "Fournisseur A"), offer("r2", "Fournisseur B")]}
        enabled
      />,
    );
    await screen.findByText("Le Patron consigne si les offres couvrent le même périmètre ; l’application ne le déduit pas et ne calcule aucun coût couvert.");
    fireEvent.click(screen.getByRole("button", { name: "Nouvelle comparaison" }));
    fireEvent.click(screen.getByLabelText(/Fournisseur A/));
    fireEvent.click(screen.getByLabelText(/Fournisseur B/));
    fireEvent.change(screen.getByLabelText("Motif de la revue"), { target: { value: "Périmètre à revoir." } });
    fireEvent.submit(screen.getByRole("form", { name: "Enregistrer une revue de périmètre" }));
    fireEvent.click(await screen.findByRole("button", { name: "Réessayer la même revue" }));

    expect(api.recordPartnerOfferScopeReview).toHaveBeenCalledTimes(2);
    expect(api.recordPartnerOfferScopeReview.mock.calls[0]).toEqual(
      api.recordPartnerOfferScopeReview.mock.calls[1],
    );
  });
});
