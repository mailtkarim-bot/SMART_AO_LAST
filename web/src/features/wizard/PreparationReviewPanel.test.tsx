import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ApiClient } from "../../infrastructure/api";
import { PreparationReviewPanel } from "./PreparationReviewPanel";

function renderPanel() {
  const api = {
    listPreparationReviews: vi.fn().mockResolvedValue({
      package_id: "package-1",
      reviews: [{
        review_id: "review-1",
        package_id: "package-1",
        target_document_id: "document-1",
        target_version: 2,
        target_draft_id: "draft-1",
        target_draft_version: 1,
        target_content_sha256: "a".repeat(64),
        revision: 1,
        state: "REQUESTED",
        decision_code: null,
        decision_note: null,
        corrections: [],
      }],
    }),
    listPreparationResponseDrafts: vi.fn().mockResolvedValue({
      package_id: "package-1",
      drafts: [{
        draft_id: "draft-1",
        version: 1,
        state: "DRAFT",
        section_codes: ["METHOD"],
        source_refs: ["requirement-1"],
        responsible_role: "COLLABORATEUR",
        content_sha256: "a".repeat(64),
        response_plan_id: "plan-1",
        response_plan_version: 3,
        content: "Contenu exact du brouillon.",
      }],
    }),
    listPreparationTransmissions: vi.fn().mockResolvedValue({ package_id: "package-1", deliveries: [] }),
    decidePreparationReview: vi.fn().mockResolvedValue({ result_code: "PREPARATION_REVIEW_DECIDED" }),
    requestPreparationReview: vi.fn().mockResolvedValue({ result_code: "PREPARATION_REVIEW_REQUESTED" }),
    addPreparationCorrection: vi.fn().mockResolvedValue({ result_code: "PREPARATION_CORRECTION_ADDED" }),
  } as unknown as ApiClient;
  const setMessage = vi.fn();
  render(<PreparationReviewPanel api={api} setMessage={setMessage} />);
  return { api, setMessage };
}

describe("PreparationReviewPanel", () => {
  it("loads latest reviews and sends a server-revisioned acceptance", async () => {
    const { api } = renderPanel();
    fireEvent.change(screen.getByPlaceholderText("UUID du package"), { target: { value: "package-1" } });
    fireEvent.click(screen.getByRole("button", { name: "Charger les revues" }));
    expect(await screen.findAllByText("Brouillon draft-1 · v1")).toHaveLength(2);
    expect(screen.getByText("Brouillons C10 reçus")).toBeInTheDocument();
    expect(screen.getByText("Contenu exact du brouillon.")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Accepter" }));
    await waitFor(() => expect(api.decidePreparationReview).toHaveBeenCalledWith("package-1", expect.objectContaining({
      review_id: "review-1",
      target_document_id: "document-1",
      target_draft_id: "draft-1",
      target_draft_version: 1,
      target_content_sha256: "a".repeat(64),
      expected_review_revision: 1,
      decision_code: "ACCEPTED",
    })));
  });

  it("requests review against the displayed exact draft hash", async () => {
    const api = {
      listPreparationReviews: vi.fn().mockResolvedValue({ package_id: "package-1", reviews: [] }),
      listPreparationResponseDrafts: vi.fn().mockResolvedValue({
        package_id: "package-1",
        package_revision: 7,
        drafts: [{
          draft_id: "draft-2",
          version: 4,
          state: "DRAFT",
          section_codes: ["METHOD"],
          source_refs: [],
          responsible_role: "COLLABORATEUR",
          content_sha256: "b".repeat(64),
          response_plan_id: "plan-2",
          response_plan_version: 2,
          content: "Texte synthétique à examiner.",
        }],
      }),
      listPreparationTransmissions: vi.fn().mockResolvedValue({ package_id: "package-1", deliveries: [] }),
      requestPreparationReview: vi.fn().mockResolvedValue({ result_code: "PREPARATION_REVIEW_REQUESTED" }),
    } as unknown as ApiClient;
    render(<PreparationReviewPanel api={api} setMessage={vi.fn()} />);
    fireEvent.change(screen.getByPlaceholderText("UUID du package"), { target: { value: "package-1" } });
    fireEvent.click(screen.getByRole("button", { name: "Charger les revues" }));
    expect(await screen.findByText("Texte synthétique à examiner.")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Demander la revue exacte" }));
    await waitFor(() => expect(api.requestPreparationReview).toHaveBeenCalledWith("package-1", expect.objectContaining({
      target_draft_id: "draft-2",
      target_draft_version: 4,
      target_content_sha256: "b".repeat(64),
      expected_package_revision: 7,
    })));
  });

  it("renders persisted snapshot and transmission receipts with their exact revisions", async () => {
    const snapshotReceipt = {
      status: "SUCCEEDED",
      command_id: "snapshot-command",
      idempotency_key: "snapshot-key",
      result_code: "PREPARATION_SNAPSHOT_CREATED",
      aggregate_refs: [{ aggregate_type: "PreparationSnapshot", aggregate_id: "snapshot-1", aggregate_revision: 3 }],
      event_ids: ["snapshot-event"],
      replayed: false,
    };
    const transmissionReceipt = {
      status: "SUCCEEDED",
      command_id: "transmission-command",
      idempotency_key: "transmission-key",
      result_code: "PREPARATION_TRANSMITTED_TO_PATRON",
      aggregate_refs: [{ aggregate_type: "PreparationTransmission", aggregate_id: "transmission-1", aggregate_revision: 9 }],
      event_ids: ["transmission-event"],
      replayed: false,
    };
    const api = {
      listPreparationReviews: vi.fn().mockResolvedValue({ package_id: "package-1", reviews: [] }),
      listPreparationResponseDrafts: vi.fn().mockResolvedValue({ package_id: "package-1", package_revision: 9, drafts: [] }),
      listPreparationTransmissions: vi.fn().mockResolvedValue({
        package_id: "package-1",
        deliveries: [{
          snapshot_id: "snapshot-1",
          snapshot_version: 3,
          snapshot_state: "READY_FOR_PATRON_REVIEW",
          snapshot_created_at: "2026-10-09T12:00:00Z",
          snapshot_manifest_sha256: "a".repeat(64),
          snapshot_manifest: { response_drafts: [{ draft_id: "draft-1", version: 2 }] },
          snapshot_receipt: snapshotReceipt,
          transmission_id: "transmission-1",
          transmission_state: "TRANSMITTED_TO_PATRON",
          transmitted_at: "2026-10-09T12:01:00Z",
          transmission_receipt: transmissionReceipt,
        }],
      }),
    } as unknown as ApiClient;
    render(<PreparationReviewPanel api={api} setMessage={vi.fn()} />);
    fireEvent.change(screen.getByPlaceholderText("UUID du package"), { target: { value: "package-1" } });
    fireEvent.click(screen.getByRole("button", { name: "Charger les revues" }));
    expect(await screen.findByText("Snapshots transmis au Patron")).toBeInTheDocument();
    expect(screen.getByText(/Snapshot v3 · snapshot-1/)).toBeInTheDocument();
    expect(screen.getByText("Transmission transmission-1")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Reçus et révisions exacts"));
    expect(screen.getByText(/transmission-command/)).toBeInTheDocument();
    expect(screen.getByText(/aggregate_revision": 9/)).toBeInTheDocument();
  });
});
