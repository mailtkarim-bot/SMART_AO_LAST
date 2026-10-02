import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { expect, test, vi } from "vitest";
import type { ApiClient } from "../../infrastructure/api";
import type {
  CaseHandoverOfferOptions,
  CaseHandoverSnapshots,
} from "../../shared/types";
import { CaseHandoverPanel } from "./CaseHandoverPanel";

const options: CaseHandoverOfferOptions = {
  case_id: "case-1",
  items: [{
    outcome_id: "outcome-won",
    lot_reference: "01",
    submission_package_id: "package-p5",
    package_version: 3,
    manifest_sha256: "a".repeat(64),
    dce_version_id: "dce-v2",
    technical_document_id: "technical-doc",
    technical_document_version: 2,
    technical_document_kind: "TECHNICAL_RESPONSE",
    technical_document_sha256: "c".repeat(64),
  }],
};

const snapshots: CaseHandoverSnapshots = {
  case_id: "case-1",
  items: [{
    snapshot_id: "handover-1",
    outcome_id: "outcome-won",
    lot_reference: "01",
    submission_package_id: "package-p5",
    package_version: 3,
    manifest_sha256: "a".repeat(64),
    revision: 1,
    created_at: "2026-10-01T12:00:00Z",
    snapshot: {
      schema_version: 1,
      kind: "P7_HANDOVER_SNAPSHOT",
      p7_is_order_service: false,
      award: {
        outcome_id: "outcome-won",
        lot_reference: "01",
        source_locator: "attribution://notice/01",
        recorded_at: "2026-10-01T11:00:00Z",
      },
      offer: {
        submission_package_id: "package-p5",
        package_version: 3,
        manifest_sha256: "a".repeat(64),
        dce_version_id: "dce-v2",
        technical_document_id: "technical-doc",
        technical_document_version: 2,
        technical_document_kind: "TECHNICAL_RESPONSE",
        technical_document_sha256: "c".repeat(64),
        financial_content: "NOT_INCLUDED",
      },
      decision: {
        state: "KNOWN",
        decision_id: "decision-1",
        revision: 4,
        outcome: "CONDITIONAL_GO",
        context_id: "context-1",
        context_fingerprint: "b".repeat(64),
        conditions_state: "KNOWN",
        open_conditions: [{
          condition_id: "condition-1",
          label: "Réserve de lancement à lever",
          status: "OPEN",
          due_at: null,
        }],
        condition_sources: [],
      },
      contract_comparison: {
        state: "UNKNOWN",
        reason: "Aucun rapprochement de recette.",
      },
      excluded: ["DONNEES_FINANCIERES_PRIVEES"],
    },
  }],
};

function makeApi(recordCaseHandover = vi.fn().mockResolvedValue({
  status: "SUCCEEDED",
  result_code: "CASE_HANDOVER_SNAPSHOT_RECORDED",
  replayed: false,
})) {
  return {
    listCaseHandoverSnapshots: vi.fn().mockResolvedValue(snapshots),
    listCaseHandoverOfferOptions: vi.fn().mockResolvedValue(options),
    downloadCaseHandoverOffer: vi.fn().mockResolvedValue(new Blob(["offre technique"])),
    recordCaseHandover,
  } as unknown as ApiClient;
}

test("transmet le paquet P5 exact et affiche la condition ouverte au Responsable", async () => {
  vi.stubGlobal("crypto", { randomUUID: vi.fn(() => "stable-id") });
  const api = makeApi();
  const record = api.recordCaseHandover as ReturnType<typeof vi.fn>;
  const { rerender } = render(<CaseHandoverPanel api={api} caseId="case-1" canManage />);

  fireEvent.change(await screen.findByLabelText("Offre gagnée exacte à transmettre"), {
    target: { value: "outcome-won:package-p5" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Transmettre au Conducteur" }));
  await waitFor(() => expect(record).toHaveBeenCalledOnce());
  expect(record).toHaveBeenCalledWith("case-1", expect.objectContaining({
    outcome_id: "outcome-won",
    submission_package_id: "package-p5",
  }));
  expect(await screen.findByText("Réserve de lancement à lever · échéance UNKNOWN")).toBeInTheDocument();
  expect(screen.getByText(/P7 ≠ ordre de service/)).toBeInTheDocument();
  expect(screen.getByText(/Rapprochement contrat \/ offre : UNKNOWN/)).toBeInTheDocument();
  expect(screen.queryByText(/marge brute/i)).not.toBeInTheDocument();
  vi.stubGlobal("URL", {
    createObjectURL: vi.fn(() => "blob:test"),
    revokeObjectURL: vi.fn(),
  });
  fireEvent.click(screen.getByRole("button", { name: "Télécharger l’offre technique exacte" }));
  await waitFor(() => expect(api.downloadCaseHandoverOffer).toHaveBeenCalledWith("case-1", "handover-1"));

  rerender(<CaseHandoverPanel api={api} caseId="case-1" canManage={false} />);
  expect(await screen.findByText("Réserve de lancement à lever · échéance UNKNOWN")).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: "Transmettre au Conducteur" })).not.toBeInTheDocument();
  vi.unstubAllGlobals();
});

test("un résultat de transmission non confirmé rejoue les mêmes identifiants", async () => {
  vi.stubGlobal("crypto", { randomUUID: vi.fn(() => "same-id") });
  const record = vi.fn()
    .mockRejectedValueOnce(new Error("network interruption"))
    .mockResolvedValueOnce({
      status: "SUCCEEDED",
      result_code: "CASE_HANDOVER_SNAPSHOT_RECORDED",
      replayed: true,
    });
  const api = makeApi(record);
  render(<CaseHandoverPanel api={api} caseId="case-1" canManage />);

  fireEvent.change(await screen.findByLabelText("Offre gagnée exacte à transmettre"), {
    target: { value: "outcome-won:package-p5" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Transmettre au Conducteur" }));
  expect(await screen.findByText(/résultat non confirmé/i)).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Réessayer la même passation" }));
  await waitFor(() => expect(record).toHaveBeenCalledTimes(2));
  expect(record.mock.calls[1]).toEqual(record.mock.calls[0]);
  vi.unstubAllGlobals();
});
