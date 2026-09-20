import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type {
  AssignedCase,
  ConsultationProjection,
  DceDocumentInventory,
  DceVersionMetadata,
} from "../../shared/types";
import { DceOpeningPanel } from "./DceOpeningPanel";

const selectedCase: AssignedCase = {
  case_id: "case-1",
  work_label: "Réhabilitation du groupe scolaire",
  case_lifecycle: "PREPARATION",
  commercial_stage: "QUALIFICATION",
  dce_availability: "AVAILABLE",
  consultation_id: "consultation-server-1",
  applicable_dce_version_id: "dce-version-server-1",
};

const consultation: ConsultationProjection = {
  id: "consultation-server-1",
  buyer_legal_name: "Ville d'Exemple",
  external_reference: "REF-2026-001",
  object_label: "Travaux de réhabilitation",
  location_label: "Exemple-sur-Mer",
  lifecycle: "PUBLISHED",
  freshness: "CURRENT",
  aggregate_revision: 4,
  lots: ["01", "02"],
  tranches: ["T1"],
  projection_status: "READY",
};

const metadata: DceVersionMetadata = {
  id: "dce-version-server-1",
  consultation_id: "consultation-server-1",
  predecessor_dce_version_id: null,
  source_received_at: "2026-09-01T10:00:00Z",
  lifecycle: "ADMITTED",
  integrity: "VERIFIED",
  classification_readiness: "CLASSIFIED",
  analysis_readiness: "READY",
  aggregate_revision: 2,
};

function inventoryWith(
  items: Array<Partial<DceDocumentInventory["items"][number]> & { document_id: string }>,
): DceDocumentInventory {
  return {
    dce_version_id: "dce-version-server-1",
    items: items.map((item) => ({
      original_filename: "cce.pdf",
      media_type: "application/pdf",
      byte_size: 2048,
      received_from: "MANUAL_UPLOAD",
      processing_state: "RECEIVED",
      issue_code: null,
      ...item,
    })),
  };
}

function renderPanel(overrides: Partial<React.ComponentProps<typeof DceOpeningPanel>> = {}) {
  return render(
    <DceOpeningPanel
      selectedCase={selectedCase}
      consultation={null}
      dceVersionMetadata={null}
      inventory={null}
      loading={false}
      busy={false}
      sourceChannel="MANUAL_UPLOAD"
      file={null}
      step="IDLE"
      onSourceChannelChange={vi.fn()}
      onFileChange={vi.fn()}
      onOpen={vi.fn()}
      onAdmit={vi.fn()}
      {...overrides}
    />,
  );
}

describe("DceOpeningPanel", () => {
  it("asks for a case before exposing the DCE space", () => {
    renderPanel({ selectedCase: undefined });

    expect(screen.getByText("Sélectionnez une affaire")).toBeInTheDocument();
  });

  it("explains that nothing can be done for a case without a linked consultation", () => {
    renderPanel({
      selectedCase: { ...selectedCase, consultation_id: null, applicable_dce_version_id: null },
    });

    expect(screen.getByText("Affaire sans consultation liée")).toBeInTheDocument();
    expect(screen.queryByText("Préparer et admettre le document")).not.toBeInTheDocument();
  });

  it("renders the consultation projection from server references", () => {
    renderPanel({ consultation });

    expect(screen.getByText("Travaux de réhabilitation")).toBeInTheDocument();
    expect(screen.getByText(/Ville d'Exemple/)).toBeInTheDocument();
    expect(screen.getByText("Révision : 4")).toBeInTheDocument();
    expect(screen.getByText("Lots : 01, 02")).toBeInTheDocument();
    expect(screen.getByText(/Consultation : consulta…er-1/)).toBeInTheDocument();
    expect(screen.getByText(/Version DCE applicable : dce-vers…er-1/)).toBeInTheDocument();
  });

  it("renders every processing state in french and surfaces issue codes", () => {
    renderPanel({
      consultation,
      dceVersionMetadata: metadata,
      inventory: inventoryWith([
        { document_id: "doc-1", original_filename: "cce.pdf", processing_state: "RECEIVED" },
        { document_id: "doc-2", original_filename: "cctp.pdf", processing_state: "READ" },
        {
          document_id: "doc-3",
          original_filename: "plan.dwg",
          processing_state: "REVIEW_REQUIRED",
          issue_code: "HUMAN_REVIEW_REQUIRED",
        },
        {
          document_id: "doc-4",
          original_filename: "archive.rar",
          processing_state: "UNSUPPORTED",
          issue_code: "UNSUPPORTED_MEDIA_TYPE",
        },
        {
          document_id: "doc-5",
          original_filename: "gros.pdf",
          processing_state: "LIMIT_REACHED",
          issue_code: "SIZE_LIMIT_REACHED",
        },
        {
          document_id: "doc-6",
          original_filename: "protégé.pdf",
          processing_state: "PROTECTED",
          issue_code: "PROTECTED_DOCUMENT",
        },
        {
          document_id: "doc-7",
          original_filename: "illisible.pdf",
          processing_state: "UNREADABLE",
          issue_code: "EXTRACTION_FAILED",
        },
      ]),
    });

    expect(screen.getByText("Reçu")).toBeInTheDocument();
    expect(screen.getByText("Lu")).toBeInTheDocument();
    expect(screen.getByText("Revue humaine requise")).toBeInTheDocument();
    expect(screen.getByText("Format non pris en charge")).toBeInTheDocument();
    expect(screen.getByText("Limite atteinte")).toBeInTheDocument();
    expect(screen.getByText("Document protégé")).toBeInTheDocument();
    expect(screen.getByText("Illisible")).toBeInTheDocument();
    expect(screen.getByText("HUMAN_REVIEW_REQUIRED")).toBeInTheDocument();
    expect(screen.getByText("EXTRACTION_FAILED")).toBeInTheDocument();
  });

  it("renders an empty inventory explicitly", () => {
    renderPanel({ consultation, inventory: inventoryWith([]) });

    expect(screen.getByText("Aucun document dans la version DCE applicable.")).toBeInTheDocument();
  });

  it("disables the admission form while a transfer is running", () => {
    const onAdmit = vi.fn();
    renderPanel({
      consultation,
      busy: true,
      step: "UPLOADING",
      file: new File(["x"], "cce.pdf"),
      onAdmit,
    });

    expect(screen.getByRole("button", { name: /Transfert…/ })).toBeDisabled();
    expect(screen.getByRole("status")).toHaveTextContent("Transfert du flux binaire…");
    fireEvent.click(screen.getByRole("button", { name: /Transfert…/ }));
    expect(onAdmit).not.toHaveBeenCalled();
  });

  it("delegates open and admission actions", () => {
    const onOpen = vi.fn();
    const onAdmit = vi.fn();
    const onFileChange = vi.fn();
    renderPanel({
      consultation,
      file: new File(["x"], "cce.pdf"),
      onOpen,
      onAdmit,
      onFileChange,
    });

    fireEvent.click(screen.getByRole("button", { name: "Ouvrir / actualiser l'espace" }));
    fireEvent.change(screen.getByLabelText("Document DCE"), {
      target: { files: [new File(["y"], "cctp.pdf")] },
    });
    fireEvent.click(screen.getByRole("button", { name: /Préparer et admettre le document/ }));

    expect(onOpen).toHaveBeenCalledOnce();
    expect(onFileChange).toHaveBeenCalledWith(expect.any(File));
    expect(onAdmit).toHaveBeenCalledOnce();
  });
});
