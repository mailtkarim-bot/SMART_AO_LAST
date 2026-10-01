import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ApiClient } from "../../infrastructure/api";
import type { PartnerOfferPriceList } from "../../shared/types";
import { PartnerOfferPricesPanel } from "./PartnerOfferPricesPanel";

const unknownOffer: PartnerOfferPriceList = {
  case_id: "case-1",
  offers: [{
    receipt_event_id: "receipt-1",
    partner_id: "partner-1",
    partner_kind: "SUPPLIER",
    partner_label: "Fournisseur A",
    partner_revision: 2,
    source_locator: "offre://consultation-7/v2.pdf",
    source_rationale: "Devis fournisseur pour le lot 7.",
    valid_until: null,
    validity_current: "UNKNOWN",
    exclusions_state: "UNKNOWN",
    exclusions: [],
    mandate_state: "NOT_APPLICABLE",
    is_latest_receipt: true,
    price_state: "UNKNOWN",
    declarations: [],
  }],
};

const declaredOffer: PartnerOfferPriceList = {
  ...unknownOffer,
  offers: [{
    ...unknownOffer.offers[0],
    price_state: "DECLARED",
    declarations: [{
      declaration_id: "decl-1",
      revision: 1,
      amount_as_declared: "1234,50",
      currency_code: "MAD",
      actor_id: "owner-1",
      created_at: "2026-09-30T12:00:00Z",
    }],
  }],
};

function client(api: Partial<ApiClient>) {
  return api as ApiClient;
}

describe("PartnerOfferPricesPanel", () => {
  it("shows missing prices as UNKNOWN and records only a declared total against the receipt", async () => {
    const api = {
      listPartnerOfferPrices: vi.fn()
        .mockResolvedValueOnce(unknownOffer)
        .mockResolvedValueOnce(declaredOffer),
      listPartnerOfferScopeReviews: vi.fn().mockResolvedValue({ case_id: "case-1", reviews: [] }),
      declarePartnerOfferPrice: vi.fn().mockResolvedValue({
        status: "SUCCEEDED",
        result_code: "PARTNER_OFFER_PRICE_DECLARED",
        aggregate_refs: [],
        event_ids: ["decl-1"],
        replayed: false,
      }),
    };
    render(<PartnerOfferPricesPanel api={client(api)} caseId="case-1" enabled />);

    expect(await screen.findByText("UNKNOWN · aucun montant déclaré pour ce reçu.")).toBeInTheDocument();
    expect(screen.getByText(/offre:\/\/consultation-7\/v2\.pdf/)).toBeInTheDocument();
    expect(screen.getByText(/Empreinte de la pièce : UNKNOWN/)).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Total exactement déclaré par la source"), {
      target: { value: "1234,50" },
    });
    fireEvent.change(screen.getByLabelText("Code devise source (3 lettres)"), {
      target: { value: "mad" },
    });
    fireEvent.submit(screen.getByRole("form", { name: "Déclarer le total de Fournisseur A" }));

    expect(await screen.findByText("Révision 1 : 1234,50 MAD · déclarée 2026-09-30T12:00:00Z")).toBeInTheDocument();
    expect(api.declarePartnerOfferPrice).toHaveBeenCalledWith(
      "case-1",
      "receipt-1",
      expect.objectContaining({
        expected_revision: 0,
        amount_as_declared: "1234,50",
        currency_code: "MAD",
      }),
    );
    expect(screen.getByText(/Aucun coût couvert, classement, engagement ou GO P3/)).toBeInTheDocument();
  });

  it("reuses the same command identifiers when the declaration result is unknown", async () => {
    const api = {
      listPartnerOfferPrices: vi.fn()
        .mockResolvedValueOnce(unknownOffer)
        .mockResolvedValueOnce(declaredOffer),
      listPartnerOfferScopeReviews: vi.fn().mockResolvedValue({ case_id: "case-1", reviews: [] }),
      declarePartnerOfferPrice: vi.fn()
        .mockRejectedValueOnce({ status: 500 })
        .mockResolvedValueOnce({
          status: "SUCCEEDED",
          result_code: "PARTNER_OFFER_PRICE_DECLARED",
          aggregate_refs: [],
          event_ids: ["decl-1"],
          replayed: true,
        }),
    };
    render(<PartnerOfferPricesPanel api={client(api)} caseId="case-1" enabled />);
    await screen.findByText("UNKNOWN · aucun montant déclaré pour ce reçu.");
    fireEvent.change(screen.getByLabelText("Total exactement déclaré par la source"), {
      target: { value: "1234,50" },
    });
    fireEvent.change(screen.getByLabelText("Code devise source (3 lettres)"), {
      target: { value: "MAD" },
    });
    const form = screen.getByRole("form", { name: "Déclarer le total de Fournisseur A" });
    fireEvent.submit(form);
    fireEvent.click(await screen.findByRole("button", { name: "Réessayer la déclaration" }));

    expect(await screen.findByText(/Révision 1 : 1234,50 MAD/)).toBeInTheDocument();
    const first = api.declarePartnerOfferPrice.mock.calls[0];
    const second = api.declarePartnerOfferPrice.mock.calls[1];
    expect(first).toEqual(second);
  });

  it("does not query private offer values while C08 is inactive", () => {
    const api = { listPartnerOfferPrices: vi.fn() };
    render(<PartnerOfferPricesPanel api={client(api)} caseId="case-1" enabled={false} />);
    expect(screen.getByRole("status")).toHaveTextContent("Ouvrez C08");
    expect(api.listPartnerOfferPrices).not.toHaveBeenCalled();
  });

  it("renders a neutral refusal when the financial endpoint denies access", async () => {
    const api = { listPartnerOfferPrices: vi.fn().mockRejectedValue({ status: 403 }) };
    render(<PartnerOfferPricesPanel api={client(api)} caseId="case-1" enabled />);
    expect(await screen.findByText("FORBIDDEN · lecture financière réservée au Patron habilité.")).toBeInTheDocument();
    expect(screen.queryByText("1234,50")).not.toBeInTheDocument();
  });
});
