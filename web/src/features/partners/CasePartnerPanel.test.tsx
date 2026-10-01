import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type {
  CasePartnerEvent,
  CasePartnerEventList,
  DeclareCasePartnerEngagementInput,
  RecordCasePartnerReceiptInput,
  RecordCasePartnerRequestInput,
} from "../../shared/types";
import { CasePartnerPanel } from "./CasePartnerPanel";

const requestEvent: CasePartnerEvent = {
  event_id: "request-1",
  partner_id: "partner-1",
  case_id: "case-1",
  revision: 1,
  event_type: "REQUESTED",
  partner_kind: "CO_CONTRACTOR",
  partner_label: "Groupement déclaré",
  related_event_id: null,
  source_locator: "dce://target/lot-01",
  rationale: "Consultation déclarée, pas encore transmise par SmartAO.",
  valid_until: null,
  validity_at_recording: "UNKNOWN",
  validity_current: "UNKNOWN",
  exclusions_state: "UNKNOWN",
  exclusions: [],
  mandate_state: "UNKNOWN",
  mandate_source_locator: null,
  actor_id: "patron-1",
  recorded_at: "2026-09-30T12:00:00Z",
};

const receiptEvent: CasePartnerEvent = {
  ...requestEvent,
  event_id: "receipt-1",
  revision: 2,
  event_type: "RECEIVED",
  related_event_id: "request-1",
  source_locator: "offer://received/1",
  rationale: "Proposition reçue.",
  valid_until: "2027-03-30",
  validity_at_recording: "VALID",
  validity_current: "VALID",
  exclusions_state: "DECLARED",
  exclusions: [],
  mandate_state: "RECEIVED",
  mandate_source_locator: "mandate://received/1",
};

function list(events: CasePartnerEvent[] = [], overrides: Partial<CasePartnerEventList> = {}): CasePartnerEventList {
  return {
    case_id: "case-1",
    events,
    can_request: true,
    can_receive: true,
    can_declare_engagement: false,
    ...overrides,
  };
}

function renderPanel(overrides: Partial<React.ComponentProps<typeof CasePartnerPanel>> = {}) {
  return render(
    <CasePartnerPanel
      caseId="case-1"
      caseLabel="Gymnase municipal"
      status="READY"
      list={list()}
      onRequest={vi.fn(async (_input: RecordCasePartnerRequestInput) => undefined)}
      onReceive={vi.fn(async (_input: RecordCasePartnerReceiptInput) => undefined)}
      onDeclareEngagement={vi.fn(async (_input: DeclareCasePartnerEngagementInput) => undefined)}
      onRefresh={vi.fn()}
      {...overrides}
    />,
  );
}

describe("CasePartnerPanel C09", () => {
  it("keeps request and receipt separate and never shows receipt as engagement", () => {
    renderPanel({ list: list([requestEvent, receiptEvent]) });

    expect(screen.getByText("Affaire active : Gymnase municipal.")).toBeVisible();
    expect(screen.getByText(/REQUESTED · demande déclarée, non transmise par SmartAO/)).toBeVisible();
    expect(screen.getByText(/RECEIVED · preuve reçue/)).toBeVisible();
    expect(screen.getByText(/Validité actuelle : VALID · à l’enregistrement : VALID/)).toBeVisible();
    expect(screen.getByText(/Exclusions : DECLARED · aucune déclarée/)).toBeVisible();
    expect(screen.getByText(/Mandat : RECEIVED · mandate:\/\/received\/1/)).toBeVisible();
    expect(screen.queryByText(/ENGAGEMENT_DECLARED · acte humain Patron/)).toBeNull();
  });

  it("records a manual request without calling or presuming an external transmission", async () => {
    const onRequest = vi.fn(async (_input: RecordCasePartnerRequestInput) => undefined);
    renderPanel({ onRequest });
    const form = screen.getByRole("form", { name: "Tracer une demande partenaire" });
    fireEvent.change(within(form).getByLabelText("Type de partenaire"), { target: { value: "SUBCONTRACTOR" } });
    fireEvent.change(within(form).getByLabelText("Entité partenaire déclarée"), { target: { value: "Électricité déclarée" } });
    fireEvent.change(within(form).getByLabelText("Source de la demande"), { target: { value: "dce://lot-01/electricity" } });
    fireEvent.change(within(form).getByLabelText("Motif"), { target: { value: "Besoin de capacité du lot 01" } });
    fireEvent.click(within(form).getByRole("button", { name: "Tracer la demande" }));

    await waitFor(() => expect(onRequest).toHaveBeenCalledTimes(1));
    expect(onRequest).toHaveBeenCalledWith(expect.objectContaining({
      case_id: "case-1",
      partner_kind: "SUBCONTRACTOR",
      partner_label: "Électricité déclarée",
      expected_revision: 0,
      source_locator: "dce://lot-01/electricity",
    }));
    expect(screen.getByText(/La trace ne transmet rien au partenaire/)).toBeVisible();
  });

  it("records a receipt as a separate version linked to its request", async () => {
    const onReceive = vi.fn(async (_input: RecordCasePartnerReceiptInput) => undefined);
    renderPanel({ list: list([requestEvent]), onReceive });
    const form = screen.getByRole("form", { name: "Enregistrer le reçu Groupement déclaré" });
    expect(within(form).getByText(/Ne saisissez pas de montant ici/)).toBeVisible();
    fireEvent.change(within(form).getByLabelText("Source du reçu"), { target: { value: "offer://received/groupement" } });
    fireEvent.change(within(form).getByLabelText("Motif / périmètre reçu"), { target: { value: "Offre couvrant le lot 01" } });
    fireEvent.change(within(form).getByLabelText("État du mandat"), { target: { value: "RECEIVED" } });
    fireEvent.change(within(form).getByLabelText("Source du mandat reçu"), { target: { value: "mandate://received/1" } });
    fireEvent.click(within(form).getByRole("button", { name: "Enregistrer le reçu" }));

    await waitFor(() => expect(onReceive).toHaveBeenCalledTimes(1));
    expect(onReceive).toHaveBeenCalledWith(expect.objectContaining({
      case_id: "case-1",
      partner_id: "partner-1",
      request_event_id: "request-1",
      expected_revision: 1,
      exclusions_state: "UNKNOWN",
      exclusions: [],
      mandate_state: "RECEIVED",
      mandate_source_locator: "mandate://received/1",
    }));
  });

  it("declares engagement only from a specific received event with source and rationale", async () => {
    const onDeclareEngagement = vi.fn(async (_input: DeclareCasePartnerEngagementInput) => undefined);
    renderPanel({
      list: list([receiptEvent], { can_declare_engagement: true }),
      onDeclareEngagement,
    });
    fireEvent.change(screen.getByLabelText("Source de l’engagement"), { target: { value: "agreement://signed/1" } });
    fireEvent.change(screen.getByLabelText("Motif de la déclaration"), { target: { value: "Preuve de conclusion reçue" } });
    fireEvent.click(screen.getByRole("button", { name: "Déclarer l’engagement Patron" }));

    await waitFor(() => expect(onDeclareEngagement).toHaveBeenCalledTimes(1));
    expect(onDeclareEngagement).toHaveBeenCalledWith(expect.objectContaining({
      case_id: "case-1",
      partner_id: "partner-1",
      receipt_event_id: "receipt-1",
      expected_revision: 2,
      source_locator: "agreement://signed/1",
      rationale: "Preuve de conclusion reçue",
    }));
  });

  it("blocks cotraitant engagement until a mandate source is received", () => {
    renderPanel({
      list: list([{ ...receiptEvent, mandate_state: "REQUESTED", mandate_source_locator: null }], {
        can_declare_engagement: true,
      }),
    });

    expect(screen.getByText(/Mandat cotraitant non reçu\/sourcé/)).toBeVisible();
    expect(screen.getByRole("button", { name: "Déclarer l’engagement Patron" })).toBeDisabled();
  });

  it("reuses the same command after an uncertain write and blocks retry on another Affaire", async () => {
    const onDeclareEngagement = vi.fn()
      .mockRejectedValueOnce(Object.assign(new Error("COMMAND_IN_PROGRESS"), { status: 409 }))
      .mockResolvedValueOnce(undefined);
    const { rerender } = renderPanel({
      list: list([receiptEvent], { can_declare_engagement: true }),
      onDeclareEngagement,
    });
    fireEvent.change(screen.getByLabelText("Source de l’engagement"), { target: { value: "agreement://signed/1" } });
    fireEvent.change(screen.getByLabelText("Motif de la déclaration"), { target: { value: "Acte Patron" } });
    fireEvent.click(screen.getByRole("button", { name: "Déclarer l’engagement Patron" }));
    await screen.findByText(/Résultat non confirmé · le rejeu conserve les mêmes identifiants/);
    const first = onDeclareEngagement.mock.calls[0]?.[0];

    rerender(<CasePartnerPanel caseId="case-2" caseLabel="Autre Affaire" status="READY" list={{ ...list([receiptEvent], { can_declare_engagement: true }), case_id: "case-2" }} onRequest={vi.fn()} onReceive={vi.fn()} onDeclareEngagement={onDeclareEngagement} onRefresh={vi.fn()} />);
    expect(screen.getByRole("button", { name: "Réessayer la déclaration" })).toBeDisabled();
    expect(screen.getByText(/Résultat non confirmé pour l’Affaire case-1/)).toBeVisible();
    expect(onDeclareEngagement).toHaveBeenCalledTimes(1);

    rerender(<CasePartnerPanel caseId="case-1" caseLabel="Gymnase municipal" status="READY" list={list([receiptEvent], { can_declare_engagement: true })} onRequest={vi.fn()} onReceive={vi.fn()} onDeclareEngagement={onDeclareEngagement} onRefresh={vi.fn()} />);
    fireEvent.click(screen.getByRole("button", { name: "Réessayer la déclaration" }));
    await waitFor(() => expect(onDeclareEngagement).toHaveBeenCalledTimes(2));
    expect(onDeclareEngagement.mock.calls[1]?.[0]).toEqual(first);
  });
});
