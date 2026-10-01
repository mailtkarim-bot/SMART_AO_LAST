import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { CaseInterview, RecordCaseInterviewInput } from "../../shared/types";
import { CaseInterviewsPanel } from "./CaseInterviewsPanel";

const interviews: CaseInterview[] = [
  {
    interview_id: "interview-usable",
    case_id: "case-1",
    held_on: "2026-09-29",
    source_locator: "fixture://interview/usable",
    rationale: "Revue d’entretien sous conditions",
    expires_on: "2026-10-01",
    snapshot: {
      captured_at: "2026-09-29T10:00:00Z",
      rex: [{ rex_id: "rex-1", lot_reference: "01", motif: "UNKNOWN", scope: "CASE_ONLY", validation: "PENDING" }],
    },
    status: "USABLE",
    created_at: "2026-09-29T10:05:00Z",
  },
  {
    interview_id: "interview-expired",
    case_id: "case-1",
    held_on: "2026-03-01",
    source_locator: "fixture://interview/expired",
    rationale: "Ancien entretien arrivé à expiration",
    expires_on: "2026-03-02",
    snapshot: { rex: [] },
    status: "EXPIRED",
    created_at: "2026-03-01T10:05:00Z",
  },
];

function renderPanel(overrides: Partial<React.ComponentProps<typeof CaseInterviewsPanel>> = {}) {
  return render(
    <CaseInterviewsPanel
      caseId="case-1"
      caseLabel="Extension de collège"
      status="READY"
      interviews={interviews}
      canManage
      onRefresh={vi.fn()}
      onRecordInterview={vi.fn(async (_input: RecordCaseInterviewInput) => undefined)}
      {...overrides}
    />,
  );
}

describe("CaseInterviewsPanel in C13", () => {
  it("shows the selected case, server expiry statuses, and captured snapshot", () => {
    renderPanel();

    expect(screen.getByRole("region", { name: "Entretiens Patron C13" })).toBeVisible();
    expect(screen.getByText("Affaire active : Extension de collège.")).toBeVisible();
    expect(screen.getByText(/réemploi sous conditions jusqu’au 2026-10-01/)).toBeVisible();
    expect(screen.getByText(/EXPIRED · réemploi à réinterroger/)).toBeVisible();
    expect(screen.getByText(/Snapshot à date : 1 enseignement capturé/)).toBeVisible();
  });

  it("records a sourced interview with an explicit holding date and expiry", async () => {
    const onRecordInterview = vi.fn(async (_input: RecordCaseInterviewInput) => undefined);
    const onRefresh = vi.fn();
    renderPanel({ interviews: [], onRecordInterview, onRefresh });

    fireEvent.change(screen.getByLabelText("Date de l’entretien"), { target: { value: "2026-09-30" } });
    fireEvent.change(screen.getByLabelText("Source de l’entretien"), { target: { value: "fixture://interview/2026-09-30" } });
    fireEvent.change(screen.getByLabelText("Motif de l’entretien"), { target: { value: "Revue des enseignements du lot 01" } });
    fireEvent.change(screen.getByLabelText("Expiration du réemploi"), { target: { value: "2026-10-01" } });
    fireEvent.click(screen.getByRole("button", { name: "Enregistrer l’entretien" }));

    await waitFor(() => expect(onRecordInterview).toHaveBeenCalledTimes(1));
    expect(onRecordInterview).toHaveBeenCalledWith(expect.objectContaining({
      case_id: "case-1",
      held_on: "2026-09-30",
      source_locator: "fixture://interview/2026-09-30",
      rationale: "Revue des enseignements du lot 01",
      expires_on: "2026-10-01",
    }));
    expect(onRefresh).toHaveBeenCalledTimes(1);
  });

  it("reuses the same interview command identifiers after an unconfirmed response", async () => {
    const onRecordInterview = vi.fn()
      .mockRejectedValueOnce(new Error("acknowledgement lost"))
      .mockResolvedValueOnce(undefined);
    const onRefresh = vi.fn();
    renderPanel({ interviews: [], onRecordInterview, onRefresh });

    fireEvent.change(screen.getByLabelText("Date de l’entretien"), { target: { value: "2026-09-30" } });
    fireEvent.change(screen.getByLabelText("Source de l’entretien"), { target: { value: "fixture://interview/retry" } });
    fireEvent.change(screen.getByLabelText("Motif de l’entretien"), { target: { value: "Revue à rejouer" } });
    fireEvent.change(screen.getByLabelText("Expiration du réemploi"), { target: { value: "2026-10-01" } });
    fireEvent.click(screen.getByRole("button", { name: "Enregistrer l’entretien" }));
    await screen.findByText(/Entretien non confirmé/);

    fireEvent.click(screen.getByRole("button", { name: "Réessayer l’entretien" }));
    await waitFor(() => expect(onRecordInterview).toHaveBeenCalledTimes(2));
    expect(onRecordInterview.mock.calls[1][0]).toEqual(onRecordInterview.mock.calls[0][0]);
    expect(onRefresh).toHaveBeenCalledTimes(1);
  });

  it("refuses to retry an unconfirmed interview from another case", async () => {
    const onRecordInterview = vi.fn().mockRejectedValueOnce(new Error("acknowledgement lost"));
    const { rerender } = renderPanel({ interviews: [], onRecordInterview });

    fireEvent.change(screen.getByLabelText("Date de l’entretien"), { target: { value: "2026-09-30" } });
    fireEvent.change(screen.getByLabelText("Source de l’entretien"), { target: { value: "fixture://interview/case-isolation" } });
    fireEvent.change(screen.getByLabelText("Motif de l’entretien"), { target: { value: "Revue à confirmer" } });
    fireEvent.change(screen.getByLabelText("Expiration du réemploi"), { target: { value: "2026-10-01" } });
    fireEvent.click(screen.getByRole("button", { name: "Enregistrer l’entretien" }));
    await screen.findByText(/Entretien non confirmé/);

    rerender(<CaseInterviewsPanel caseId="case-2" caseLabel="Autre Affaire" status="READY" interviews={[]} canManage onRefresh={vi.fn()} onRecordInterview={onRecordInterview} />);
    expect(screen.getByText(/Résultat non confirmé pour l’Affaire case-1/)).toBeVisible();
    expect(screen.getByRole("button", { name: "Réessayer l’entretien" })).toBeDisabled();
    expect(onRecordInterview).toHaveBeenCalledTimes(1);

    rerender(<CaseInterviewsPanel caseId="case-1" caseLabel="Extension de collège" status="READY" interviews={[]} canManage onRefresh={vi.fn()} onRecordInterview={onRecordInterview} />);
    fireEvent.click(screen.getByRole("button", { name: "Réessayer l’entretien" }));
    await waitFor(() => expect(onRecordInterview).toHaveBeenCalledTimes(2));
    expect(onRecordInterview.mock.calls[1][0]).toEqual(onRecordInterview.mock.calls[0][0]);
  });

  it("keeps UNAVAILABLE distinct from an empty interview list and refuses writes", () => {
    renderPanel({ status: "UNAVAILABLE", interviews: [] });

    expect(screen.getByText(/UNAVAILABLE · lecture des entretiens Patron impossible/)).toBeVisible();
    expect(screen.queryByText(/aucun entretien n’est enregistré/)).toBeNull();
    expect(screen.queryByRole("form", { name: "Enregistrer un entretien Patron" })).toBeNull();
  });
});
