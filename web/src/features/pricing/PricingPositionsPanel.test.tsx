import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import type { ApiClient } from "../../infrastructure/api";
import type { PricingPositions, PositionReviewInput } from "../../shared/types";
import { PricingPositionsPanel } from "./PricingPositionsPanel";
import { PricingPositionPendingStore } from "./pricingPositionPending";
import { formatPositionMoney } from "./positionMoney";
function data(): PricingPositions {
  return {
    case_id: "case-a",
    batch_id: "batch-a",
    dce_version_id: null,
    coverage_state: "UNKNOWN",
    offset: 0,
    next_offset: null,
    sources_limited: {
      costs: false,
      requirements: false,
      offers: false,
      scopes: false
    },
    sources: {
      requirements: [],
      offers: [],
      scopes: [],
      costs: [{
        line_id: "cost-a",
        report_id: "report-a",
        report_revision: 1,
        report_state: "DRAFT",
        category: "DIRECT_COST",
        label: "Achat pompe",
        quantity_decimal: "1",
        unit: "u",
        amount_minor: "12000",
        currency_code: "EUR"
      }]
    },
    positions: [{
      position_id: "p-a",
      source_state: "CURRENT_SOURCE",
      position_context_sha256: "a".repeat(64),
      import_source: {
        position_id: "p-a",
        batch_id: "batch-a",
        batch_revision: 1,
        row_number: 2,
        designation: "Pompe",
        quantity_decimal: "2",
        unit: "u",
        total_minor: "20000",
        errors: [],
        source_locator: {
          sheet: "Lot 1",
          row: 2,
          cells: {
            designation: "B2"
          }
        }
      },
      review_id: null,
      revision: 0,
      actor_id: null,
      created_at: null,
      justification: null,
      state: "CURRENT",
      cost_state: "UNKNOWN",
      declared_cost_minor: null,
      currency_code: null,
      coverage_state: "UNKNOWN",
      applicability: "UNKNOWN",
      costs: [],
      requirement: null,
      offer: null,
      scope: null,
      limitations: ["NO_REGISTERED_COST"]
    }]
  };
}
function setup(overrides = {}) {
  const api = {
    getPricingPositions: vi.fn().mockResolvedValue(data()),
    getPricingPosition: vi.fn().mockResolvedValue(data()),
    recordPricingPosition: vi.fn(),
    getPricingPositionHistory: vi.fn()
  };
  const store = new PricingPositionPendingStore();
  const props = {
    api: api as unknown as ApiClient,
    enabled: true,
    caseId: "case-a",
    batchId: "batch-a",
    ownerKey: "owner-a",
    scopeKey: "session-a",
    pendingStore: store,
    ...overrides
  };
  return {
    ...render(<PricingPositionsPanel {...props} />),
    api,
    store,
    props
  };
}
it("keeps missing costs UNKNOWN, shows cell sources and never infers coverage", async () => {
  setup();
  expect(await screen.findByText("Pompe")).toBeInTheDocument();
  expect(screen.getByText(/Lot 1 · ligne 2/)).toBeInTheDocument();
  expect(screen.getByText(/Aucun coût enregistré/)).toBeInTheDocument();
  expect(screen.getByText(/Couverture économique : UNKNOWN/)).toBeInTheDocument();
});
it("masks immediately after context or role change", async () => {
  const s = setup();
  await screen.findByText("Pompe");
  s.rerender(<PricingPositionsPanel {...s.props} caseId="case-b" />);
  expect(screen.queryByText("Pompe")).not.toBeInTheDocument();
  s.rerender(<PricingPositionsPanel {...s.props} enabled={false} />);
  expect(screen.queryByText("Pompe")).not.toBeInTheDocument();
});
it("refuses discordant case and batch responses", async () => {
  const bad = data();
  bad.case_id = "foreign";
  const api = {
    getPricingPositions: vi.fn().mockResolvedValue(bad)
  } as unknown as ApiClient;
  setup({
    api
  });
  await waitFor(() => expect(screen.getByRole("alert")).toBeInTheDocument());
  expect(screen.queryByText("Pompe")).not.toBeInTheDocument();
});
it("freezes UNKNOWN and retries the identical intent after MFA refusal", async () => {
  const s = setup();
  s.api.recordPricingPosition.mockRejectedValueOnce(new Error("lost")).mockRejectedValueOnce(Object.assign(new Error("MFA"), {
    status: 403
  }));
  await screen.findByText("Pompe");
  fireEvent.click(screen.getByRole("button", {
    name: "Rapprocher ce poste"
  }));
  const option = screen.getByRole("option", {
    name: /Achat pompe/
  }) as HTMLOptionElement;
  option.selected = true;
  fireEvent.change(screen.getByLabelText("Coûts enregistrés à rattacher"));
  fireEvent.change(screen.getByLabelText("Justification du rapprochement"), {
    target: {
      value: "Source relue, limites conservées"
    }
  });
  fireEvent.click(screen.getByRole("button", {
    name: "Vérifier les choix"
  }));
  fireEvent.click(screen.getByLabelText(/Je confirme ce rapprochement/));
  fireEvent.click(screen.getByRole("button", {
    name: "Enregistrer le rapprochement"
  }));
  await screen.findByRole("button", {
    name: "Rejouer exactement cette intention"
  });
  expect(s.api.recordPricingPosition).toHaveBeenCalledTimes(1);
  const original = s.api.recordPricingPosition.mock.calls[0][3] as PositionReviewInput;
  expect(original.cost_refs).toHaveLength(1);
  fireEvent.click(screen.getByRole("button", {
    name: "Rejouer exactement cette intention"
  }));
  await waitFor(() => expect(s.api.recordPricingPosition).toHaveBeenCalledTimes(2));
  expect(s.api.recordPricingPosition.mock.calls[1][3]).toEqual(original);
  expect(s.api.getPricingPosition).not.toHaveBeenCalled();
  expect(s.api.getPricingPositions).toHaveBeenCalledTimes(1);
  expect(screen.queryByRole("button", {
    name: "Enregistrer le rapprochement"
  })).not.toBeInTheDocument();
});
it("formats large native minor amounts without Number rounding", () => {
  const text = formatPositionMoney("9007199254740993", "EUR").replace(/[\s\u202f\u00a0]/g, "");
  expect(text).toBe("90071992547409,93EUR");
  expect(formatPositionMoney(null, "EUR")).toBe("UNKNOWN");
});
it("keeps a known receipt read-only when the projection is stale", async () => {
  const s = setup();
  s.api.recordPricingPosition.mockImplementation(async (_c, _b, _p, input: PositionReviewInput) => ({
    record_id: input.record_id,
    position_id: "p-a",
    revision: 1,
    command_id: input.command_id,
    idempotency_key: input.idempotency_key,
    replayed: false
  }));
  await screen.findByText("Pompe");
  fireEvent.click(screen.getByRole("button", {
    name: "Rapprocher ce poste"
  }));
  fireEvent.change(screen.getByLabelText("Justification du rapprochement"), {
    target: {
      value: "Sources absentes : déclaration inconnue explicite"
    }
  });
  fireEvent.click(screen.getByRole("button", {
    name: "Vérifier les choix"
  }));
  fireEvent.click(screen.getByLabelText(/Je confirme ce rapprochement/));
  fireEvent.click(screen.getByRole("button", {
    name: "Enregistrer le rapprochement"
  }));
  await waitFor(() => expect(s.api.getPricingPosition).toHaveBeenCalledTimes(1));
  expect(await screen.findByRole("button", {
    name: "Relire uniquement après le reçu ou le conflit"
  })).toBeInTheDocument();
  expect(s.api.recordPricingPosition).toHaveBeenCalledTimes(1);
  expect(screen.queryByText("Rapprochement enregistré et relu. Couverture économique : UNKNOWN.")).not.toBeInTheDocument();
});
it("reads after 409 before permitting a fresh human intent", async () => {
  const s = setup();
  s.api.recordPricingPosition.mockRejectedValueOnce(Object.assign(new Error("conflict"), {
    status: 409
  }));
  await screen.findByText("Pompe");
  fireEvent.click(screen.getByRole("button", {
    name: "Rapprocher ce poste"
  }));
  fireEvent.change(screen.getByLabelText("Justification du rapprochement"), {
    target: {
      value: "Rattachement à instruire"
    }
  });
  fireEvent.click(screen.getByRole("button", {
    name: "Vérifier les choix"
  }));
  fireEvent.click(screen.getByLabelText(/Je confirme ce rapprochement/));
  fireEvent.click(screen.getByRole("button", {
    name: "Enregistrer le rapprochement"
  }));
  await waitFor(() => expect(s.api.getPricingPosition).toHaveBeenCalledTimes(1));
  expect(await screen.findByText(/Conflit relu/)).toBeInTheDocument();
  expect(s.api.recordPricingPosition).toHaveBeenCalledTimes(1);
  expect(s.store.getSnapshot().size).toBe(0);
  s.rerender(<PricingPositionsPanel {...s.props} caseId="case-b"/>);
  expect(screen.queryByText(/Conflit relu/)).not.toBeInTheDocument();
});

it("freezes a manually allocated amount in the exact retry intent", async () => {
  const result = data();
  const record = vi.fn().mockRejectedValue({status:503});
  const api = { getPricingPositions:vi.fn().mockResolvedValue(result), recordPricingPosition:record } as unknown as ApiClient;
  render(<PricingPositionsPanel api={api} enabled caseId="case-a" batchId="batch-a" ownerKey="owner-a" scopeKey="scope-a" pendingStore={new PricingPositionPendingStore()} />);
  fireEvent.click(await screen.findByRole("button",{name:"Rapprocher ce poste"}));
  (screen.getByRole("option",{name:/Achat pompe/}) as HTMLOptionElement).selected=true;
  fireEvent.change(screen.getByLabelText("Coûts enregistrés à rattacher"));
  fireEvent.change(screen.getByLabelText(/Montant affecté à Achat pompe/),{target:{value:"4500"}});
  fireEvent.change(screen.getByLabelText("Justification du rapprochement"),{target:{value:"Partage déclaré entre les postes, reste non affecté"}});
  fireEvent.click(screen.getByRole("button",{name:"Vérifier les choix"}));
  fireEvent.click(screen.getByLabelText(/Je confirme ce rapprochement/));
  fireEvent.click(screen.getByRole("button",{name:"Enregistrer le rapprochement"}));
  fireEvent.click(await screen.findByRole("button",{name:"Rejouer exactement cette intention"}));
  await waitFor(()=>expect(record).toHaveBeenCalledTimes(2));
  expect(record.mock.calls[0][3].cost_refs[0].allocated_amount_minor).toBe("4500");
  expect(record.mock.calls[1]).toEqual(record.mock.calls[0]);
});

it.each([false,true])("shows sourced allocation and remainder, existing allocation=%s", async (existing) => {
  const result=data();
  result.sources.costs[0].allocation_summary={state:"DECLARED",allocated_amount_minor:"4500",remaining_amount_minor:"7500",explicit_reference_count:1,unresolved_reference_count:0};
  if(existing) result.positions[0].costs=[{...data().sources.costs[0],allocated_amount_minor:"4500"}];
  setup({api:{getPricingPositions:vi.fn().mockResolvedValue(result)} as unknown as ApiClient});
  fireEvent.click(await screen.findByRole("button",{name:"Rapprocher ce poste"}));
  (screen.getByRole("option",{name:/Achat pompe/}) as HTMLOptionElement).selected=true;
  fireEvent.change(screen.getByLabelText("Coûts enregistrés à rattacher"));
  expect(screen.getByText(/Déjà affecté : 45,00 EUR · Restant non affecté : 75,00 EUR/)).toBeInTheDocument();
  expect(screen.getByLabelText(/Montant affecté à Achat pompe/)).toHaveValue(existing ? "4500" : "");
});

it("drops unconfirmed allocation inputs after a manual source reread", async () => {
  const s=setup();
  fireEvent.click(await screen.findByRole("button",{name:"Rapprocher ce poste"}));
  (screen.getByRole("option",{name:/Achat pompe/}) as HTMLOptionElement).selected=true;
  fireEvent.change(screen.getByLabelText("Coûts enregistrés à rattacher"));
  fireEvent.change(screen.getByLabelText(/Montant affecté à Achat pompe/),{target:{value:"4500"}});
  fireEvent.click(screen.getByRole("button",{name:"Actualiser les postes et sources"}));
  await waitFor(()=>expect(s.api.getPricingPositions).toHaveBeenCalledTimes(2));
  await screen.findByRole("button",{name:"Rapprocher ce poste"});
  expect(screen.queryByLabelText(/Montant affecté à Achat pompe/)).not.toBeInTheDocument();
});

it("identifies the published source without merging allocations into the published totals", async () => {
  const result=data();
  result.positions[0].costs=[{...result.sources.costs[0],report_state:"PUBLISHED",report_revision:2,allocated_amount_minor:"4500"}];
  setup({api:{getPricingPositions:vi.fn().mockResolvedValue(result)} as unknown as ApiClient});
  expect(await screen.findByText(/Rapport source report-a · révision 2 · PUBLISHED/)).toBeInTheDocument();
  expect(screen.getByText(/La répartition déclarée est distincte des totaux du rapport publié/)).toBeInTheDocument();
  expect(screen.getByText(/Couverture économique : UNKNOWN/)).toBeInTheDocument();
});
