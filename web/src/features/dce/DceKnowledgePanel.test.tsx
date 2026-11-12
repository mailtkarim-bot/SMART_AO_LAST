import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { CaseDceReading, KnowledgeSearchResult } from "../../shared/types";
import { DceKnowledgePanel } from "./DceKnowledgePanel";

const reading: CaseDceReading = {
  case_id: "case-1",
  work_label: "Réhabilitation du groupe scolaire",
  case_lifecycle: "PREPARATION",
  commercial_stage: "QUALIFICATION",
  dce_freshness: "CURRENT",
  availability: "AVAILABLE",
  dce: {
    dce_version_id: "dce-1",
    lifecycle: "ADMITTED",
    integrity: "VERIFIED",
    classification_readiness: "READY",
    analysis_readiness: "READY",
    source_received_at: "2026-08-20T12:00:00Z",
  },
  counters: {
    total: 2,
    pending_human_confirmation: 1,
    confirmed: 1,
    review_required: 0,
    not_applicable: 0,
  },
  requirements: [
    {
      requirement_id: "requirement-1",
      confirmation_revision: null,
      requirement_type: "DELAI_EXECUTION",
      directive_signal: "EXPLICIT",
      confirmation_outcome: "PENDING",
      uncertainty_status: "TO_CONFIRM",
      document_family: "CCTP",
      source_locator_label: "CCTP · page 12",
      source_anchor: {
        source_anchor_id: "fragment-1",
        dce_version_id: "dce-1",
        dce_document_id: "document-1",
        extraction_id: "extraction-1",
        fragment_ordinal: 2,
        source_sha256: "a".repeat(64),
        extractor_id: "smart-ao-native",
        extractor_version: "2",
        fragment_sha256: "b".repeat(64),
        locator_state: "RESOLVED",
        locator: { kind: "pdf_page", coordinates: { page: 12, part: 1 } },
      },
    },
  ],
};

const result: KnowledgeSearchResult = {
  source_fragment_id: "fragment-1",
  dce_version_id: "dce-1",
  score: 0.91,
  locator: { label: "CCTP · page 12" },
  embedding_model: "TEST_PROVIDER",
};

function renderPanel(overrides: Partial<React.ComponentProps<typeof DceKnowledgePanel>> = {}) {
  return render(
    <DceKnowledgePanel
      selectedCaseId="case-1"
      reading={null}
      results={[]}
      query=""
      loading={false}
      searching={false}
      onQueryChange={vi.fn()}
      onLoad={vi.fn()}
      onSearch={vi.fn()}
      onResetSearch={vi.fn()}
      {...overrides}
    />,
  );
}

describe("DceKnowledgePanel", () => {
  it("asks for a case before exposing DCE data", () => {
    renderPanel({ selectedCaseId: "" });
    expect(screen.getByText("Sélectionnez une affaire")).toBeInTheDocument();
    expect(screen.queryByText("Réhabilitation du groupe scolaire")).not.toBeInTheDocument();
  });

  it("renders DCE counters, requirements and sourced results", () => {
    renderPanel({ reading, results: [result], query: "délai" });

    expect(screen.getByText("Réhabilitation du groupe scolaire")).toBeInTheDocument();
    expect(screen.getByText("DELAI_EXECUTION")).toBeInTheDocument();
    expect(screen.getByText("CCTP · page 12")).toBeInTheDocument();
    expect(screen.getByText("91%")).toBeInTheDocument();
    expect(screen.queryByText("texte intégral secret")).not.toBeInTheDocument();
  });

  it("renders read-only source provenance without source text", () => {
    renderPanel({ reading });

    expect(screen.getByText(/Provenance de la source · RESOLVED/)).toBeInTheDocument();
    expect(screen.getByText(/smart-ao-native · v2/)).toBeInTheDocument();
    expect(screen.getByText("a".repeat(64))).toBeInTheDocument();
    expect(screen.getByText("b".repeat(64))).toBeInTheDocument();
    expect(screen.queryByText("Texte source confidentiel")).not.toBeInTheDocument();
  });

  it("keeps unresolved source locators visibly UNKNOWN", () => {
    const unknownReading: CaseDceReading = {
      ...reading,
      requirements: [
        {
          ...reading.requirements[0],
          source_anchor: {
            ...reading.requirements[0].source_anchor!,
            locator_state: "UNKNOWN",
            locator: null,
          },
        },
      ],
    };

    renderPanel({ reading: unknownReading });

    expect(screen.getByText("Provenance de la source · UNKNOWN")).toBeInTheDocument();
    expect(screen.getByText("Localisation source non résolue")).toBeInTheDocument();
  });

  it("keeps a missing source anchor visibly UNKNOWN", () => {
    const unanchoredReading: CaseDceReading = {
      ...reading,
      requirements: [{ ...reading.requirements[0], source_anchor: null }],
    };

    renderPanel({ reading: unanchoredReading });

    expect(screen.getByText("Provenance de la source · UNKNOWN")).toBeInTheDocument();
    expect(screen.getByText("UNKNOWN · ancre de fragment non disponible")).toBeInTheDocument();
  });

  it("makes a partial classification explicit", () => {
    renderPanel({ reading: { ...reading, dce: { ...reading.dce, classification_readiness: "PARTIALLY_CLASSIFIED" } } });

    expect(screen.getByText("PARTIALLY_CLASSIFIED")).toBeInTheDocument();
    expect(screen.getByText(/La synthèse reste partielle/)).toBeInTheDocument();
  });

  it("delegates query, search, reset and reload actions", () => {
    const onQueryChange = vi.fn();
    const onLoad = vi.fn();
    const onSearch = vi.fn();
    const onResetSearch = vi.fn();
    renderPanel({
      reading,
      query: "délai",
      results: [result],
      onQueryChange,
      onLoad,
      onSearch,
      onResetSearch,
    });

    fireEvent.change(screen.getByRole("textbox", { name: "Question ou terme" }), { target: { value: "garantie" } });
    fireEvent.click(screen.getByRole("button", { name: "Actualiser la lecture" }));
    fireEvent.click(screen.getByRole("button", { name: /Rechercher/ }));
    fireEvent.click(screen.getByRole("button", { name: "Effacer" }));

    expect(onQueryChange).toHaveBeenCalledWith("garantie");
    expect(onLoad).toHaveBeenCalledOnce();
    expect(onSearch).toHaveBeenCalledOnce();
    expect(onResetSearch).toHaveBeenCalledOnce();
  });
});


it("does not claim completeness when the server has no coverage", () => {
  renderPanel({ reading });
  expect(screen.getByText("Couverture documentaire non disponible")).toBeInTheDocument();
});

it("shows every admitted piece and keeps unknown lot and criticality explicit", () => {
  const documents = Array.from({ length: 12 }, (_, i) => ({
    document_id: `piece-${i}`, extraction_id: i === 0 ? null : `extract-${i}`,
    document_family: "RC", extraction_status: i === 0 ? "NOT_STARTED" as const : "COMPLETED" as const,
  }));
  renderPanel({ reading: { ...reading, coverage: {
    case_scope_kind: "SINGLE_LOT", documents, total_documents: 12, completed_extractions: 11,
    unread_documents: 1, inventory_scope: "ADMITTED_DOCUMENTS_ONLY", inventory_completeness: "UNKNOWN",
    lot_applicability: "UNKNOWN", critical_unread_documents: null,
    status: "REVIEW_REQUIRED", analysis_complete: false,
  } } });
  expect(screen.getByText("Analyse complète non démontrée")).toBeInTheDocument();
  expect(screen.getByText("Non extraite")).toBeInTheDocument();
  expect(screen.getByText("Pièce piece-11")).toBeInTheDocument();
  expect(screen.getByText(/Criticité et applicabilité par lot inconnues/)).toBeInTheDocument();
  expect(screen.queryByText("Analyse complète")).not.toBeInTheDocument();
});

it("shows excluded archive entries and declared missing pieces without private references", () => {
  renderPanel({ reading: { ...reading, coverage: {
    case_scope_kind: "SINGLE_LOT", documents: [], total_documents: 0, completed_extractions: 0,
    unread_documents: 0, inventory_scope: "ADMITTED_DOCUMENTS_ONLY", inventory_completeness: "UNKNOWN",
    lot_applicability: "UNKNOWN", critical_unread_documents: null, status: "REVIEW_REQUIRED",
    analysis_complete: false, exceptions: [
      { observation_id: "issue-1", kind: "ARCHIVE_ENTRY", state: "EXCLUDED_UNSAFE", document_id: "doc-1", extraction_id: "run-1", entry_path: [2, 1], document_family: "SOURCE_UNCLASSIFIED", source_state: "RESOLVED", lot_applicability: "UNKNOWN", criticality: "UNKNOWN" },
      { observation_id: "missing-1", kind: "DECLARED_MISSING", state: "DECLARED_MISSING", document_id: null, extraction_id: null, entry_path: [], document_family: "CCAP", source_state: "UNKNOWN", lot_applicability: "UNKNOWN", criticality: "UNKNOWN" },
    ],
  } } });
  expect(screen.getByText("Entrée d’archive 2 › 1")).toBeInTheDocument();
  expect(screen.getByText("Chemin dangereux exclu")).toBeInTheDocument();
  expect(screen.getByText("Pièce annoncée manquante · CCAP")).toBeInTheDocument();
  expect(screen.getByText("Source non qualifiée · UNKNOWN")).toBeInTheDocument();
  expect(screen.getByText("Analyse complète non démontrée")).toBeInTheDocument();
});

it("keeps RC announcements and family matches candidate-only with exact source metadata", () => {
  renderPanel({ reading: { ...reading, coverage: {
    case_scope_kind: "SINGLE_LOT", documents: [], total_documents: 0, completed_extractions: 0,
    unread_documents: 0, inventory_scope: "ADMITTED_DOCUMENTS_ONLY", inventory_completeness: "UNKNOWN",
    lot_applicability: "UNKNOWN", critical_unread_documents: null, status: "REVIEW_REQUIRED",
    analysis_complete: false, announcement_scan_state: "CANDIDATES_ONLY", announcements: [{
      candidate_id: "candidate-1", document_family: "CCAP", claim: "NOT_PROVIDED_SIGNAL", lot_numbers: [2],
      source_document_id: "source-doc", source_extraction_id: "source-run", source_fragment_id: "source-fragment",
      source_locator_label: "RC · page 2", source_locator_state: "RESOLVED", start_byte_offset: 10, end_byte_offset: 50,
      context_start_byte_offset: null, context_end_byte_offset: null, family_candidate_document_ids: ["family-doc"],
      presence_status: "UNKNOWN", applicability: "UNKNOWN", criticality: "UNKNOWN", conflict_state: "CONFLICTING_CANDIDATES", rule_version: "1",
    }],
  } } });
  expect(screen.getByText("Annonces de pièces du RC · candidats")).toBeInTheDocument();
  expect(screen.getByText("Annonce de pièce non fournie · à vérifier")).toBeInTheDocument();
  expect(screen.getByText("RC · page 2")).toBeInTheDocument();
  expect(screen.getByText("Rapprochement exact non prouvé · UNKNOWN")).toBeInTheDocument();
  expect(screen.getByText("Signaux opposés à confronter")).toBeInTheDocument();
});

it("distinguishes the heading page and fragment from the list source", () => {
  renderPanel({ reading: { ...reading, coverage: {
    case_scope_kind: "SINGLE_LOT", documents: [], total_documents: 0, completed_extractions: 0,
    unread_documents: 0, inventory_scope: "ADMITTED_DOCUMENTS_ONLY", inventory_completeness: "UNKNOWN",
    lot_applicability: "UNKNOWN", critical_unread_documents: null, status: "REVIEW_REQUIRED",
    analysis_complete: false, announcement_scan_state: "CANDIDATES_ONLY", announcements: [{
      candidate_id: "candidate-1", document_family: "CCAP", claim: "NOT_PROVIDED_SIGNAL", lot_numbers: [2],
      source_document_id: "source-doc", source_extraction_id: "source-run", source_fragment_id: "source-fragment",
      source_locator_label: "RC · page 2", source_locator_state: "RESOLVED", start_byte_offset: 10, end_byte_offset: 50,
      context_start_byte_offset: 2, context_end_byte_offset: 30, context_fragment_id: "heading-fragment", context_locator_label: "RC · page 1", family_candidate_document_ids: ["family-doc"],
      presence_status: "UNKNOWN", applicability: "UNKNOWN", criticality: "UNKNOWN", conflict_state: "CONFLICTING_CANDIDATES", rule_version: "2",
    }],
  } } });
  expect(screen.getByText(/En-tête lié · RC · page 1 · fragment heading-fragment/)).toBeInTheDocument();
  expect(screen.queryByText(/dans le même fragment/)).not.toBeInTheDocument();
  expect(screen.getByText("Annonce de pièce non fournie · à vérifier")).toBeInTheDocument();
  expect(screen.getByText("RC · page 2")).toBeInTheDocument();
  expect(screen.getByText("Rapprochement exact non prouvé · UNKNOWN")).toBeInTheDocument();
  expect(screen.getByText("Signaux opposés à confronter")).toBeInTheDocument();
});

it("shows every heading bridge and source region in the provenance chain", () => {
  renderPanel({ reading: { ...reading, coverage: {
    case_scope_kind: "SINGLE_LOT", documents: [], total_documents: 0, completed_extractions: 0,
    unread_documents: 0, inventory_scope: "ADMITTED_DOCUMENTS_ONLY", inventory_completeness: "UNKNOWN",
    lot_applicability: "UNKNOWN", critical_unread_documents: null, status: "REVIEW_REQUIRED",
    analysis_complete: false, announcement_scan_state: "CANDIDATES_ONLY", announcements: [{
      candidate_id: "candidate-1", document_family: "CCAP", claim: "NOT_PROVIDED_SIGNAL", lot_numbers: [2],
      source_document_id: "source-doc", source_extraction_id: "source-run", source_fragment_id: "source-fragment",
      source_locator_label: "RC · page 2", source_locator_state: "RESOLVED", start_byte_offset: 10, end_byte_offset: 50,
      context_start_byte_offset: 2, context_end_byte_offset: 30, context_fragment_id: "heading-fragment", context_locator_label: "RC · page 1", family_candidate_document_ids: ["family-doc"],
      presence_status: "UNKNOWN", applicability: "UNKNOWN", criticality: "UNKNOWN", conflict_state: "CONFLICTING_CANDIDATES", rule_version: "3", anchor_chain: [
        { fragment_id: "heading-fragment", fragment_ordinal: 1, locator_label: "RC · page 1", part: 1, kind: "HEADING", start_byte_offset: 2, end_byte_offset: 30 },
        { fragment_id: "bridge-fragment", fragment_ordinal: 2, locator_label: "RC · page 2", part: 1, kind: "BRIDGE", start_byte_offset: 0, end_byte_offset: 20 },
        { fragment_id: "source-fragment", fragment_ordinal: 3, locator_label: "RC · page 3", part: 1, kind: "SOURCE", start_byte_offset: 10, end_byte_offset: 50 },
      ],
    }],
  } } });
  expect(screen.getByText(/En-tête lié · RC · page 1 · fragment heading-fragment/)).toBeInTheDocument();
  expect(screen.getByText("Chaîne de provenance · 3 régions")).toBeInTheDocument();
  expect(screen.getByText(/Continuité · RC · page 2 · partie 1 · fragment bridge-fragment/)).toBeInTheDocument();
  expect(screen.getByText(/Annonce · RC · page 3 · partie 1 · fragment source-fragment/)).toBeInTheDocument();
  expect(screen.getByText("Annonce de pièce non fournie · à vérifier")).toBeInTheDocument();
  expect(screen.getByText("RC · page 2")).toBeInTheDocument();
  expect(screen.getByText("Rapprochement exact non prouvé · UNKNOWN")).toBeInTheDocument();
  expect(screen.getByText("Signaux opposés à confronter")).toBeInTheDocument();
});

function rcReading(): CaseDceReading {
  const item = structuredClone(reading.requirements[0]);
  return { ...reading, requirements: [{ ...item, document_family: "RC", requirement_type: "CANDIDATURE_DOCUMENT", confirmation_outcome: "PENDING_HUMAN_CONFIRMATION", structured_candidate: {
    projector_version: "1", state: "CANDIDATES_ONLY", reason_code: "SOURCE_VALUES_CANDIDATE", source_fragment_id: "fragment-1",
    documents: ["DC1"], document_state: "CANDIDATE", date_iso: "2034-11-21", date_state: "CANDIDATE", time_local: "10:30", time_state: "CANDIDATE", timezone: null, timezone_state: "UNKNOWN", lot_numbers: [2], lot_state: "CANDIDATE", applicability: "UNKNOWN",
    evidence: [
      { field: "DOCUMENT", value: "DC1", start_byte_offset: 7, end_byte_offset: 10 },
      { field: "DATE", value: "2034-11-21", start_byte_offset: 20, end_byte_offset: 30 },
      { field: "TIME", value: "10:30", start_byte_offset: 34, end_byte_offset: 39 },
      { field: "LOT", value: "2", start_byte_offset: 49, end_byte_offset: 50 },
    ],
  } }] };
}

describe("RC structured candidates", () => {
  it("shows source-only values and independent UNKNOWN without confirming anything", () => {
    renderPanel({ reading: rcReading() });
    expect(screen.getByText("DC1")).toBeInTheDocument();
    expect(screen.getByText("2034-11-21")).toBeInTheDocument();
    expect(screen.getByText("10:30")).toBeInTheDocument();
    expect(screen.getByText("Fuseau : UNKNOWN")).toBeInTheDocument();
    expect(screen.getByText("Applicabilité : UNKNOWN")).toBeInTheDocument();
    expect(screen.getByText("PENDING_HUMAN_CONFIRMATION")).toBeInTheDocument();
    expect(screen.getByText(/DOCUMENT · DC1 · octets 7–10/)).toBeInTheDocument();
    expect(screen.getByText(/Version dce-1 · pièce document-1 · extraction extraction-1/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /confirmer|autoriser|exporter/i })).not.toBeInTheDocument();
  });

  it.each(["UNKNOWN", "REVIEW_REQUIRED"] as const)("never displays values carried by state %s", state => {
    const value = rcReading(); value.requirements[0].structured_candidate!.state = state;
    renderPanel({ reading: value });
    expect(screen.queryByText("DC1")).not.toBeInTheDocument();
    expect(screen.queryByText("2034-11-21")).not.toBeInTheDocument();
    expect(screen.getByText(/Valeurs.*UNKNOWN|Valeurs.*REVIEW_REQUIRED/)).toBeInTheDocument();
  });

  it.each(["fragment", "version", "locator", "stale", "family", "proof"])("masks values when source proof is invalid: %s", failure => {
    const value = rcReading(); const item = value.requirements[0];
    if (failure === "fragment") item.structured_candidate!.source_fragment_id = "other";
    if (failure === "version") item.source_anchor!.dce_version_id = "other";
    if (failure === "locator") item.source_anchor!.locator_state = "UNKNOWN";
    if (failure === "stale") value.dce_freshness = "STALE";
    if (failure === "family") item.document_family = "CCTP";
    if (failure === "proof") item.structured_candidate!.evidence = [];
    renderPanel({ reading: value });
    expect(screen.queryByText("DC1")).not.toBeInTheDocument();
    expect(screen.queryByText("2034-11-21")).not.toBeInTheDocument();
  });

  it("masks the whole reading if its case differs from the selection", () => {
    renderPanel({ selectedCaseId: "case-other", reading: rcReading() });
    expect(screen.queryByText(reading.work_label)).not.toBeInTheDocument();
  });

  it("does not silently omit candidate values after the eighth requirement", () => {
    const value = rcReading(); value.requirements = Array.from({ length: 9 }, (_, i) => ({ ...value.requirements[0], requirement_id: `rc-${i}` }));
    renderPanel({ reading: value });
    expect(screen.getAllByText("DC1")).toHaveLength(9);
  });
});


it("suspend les anciennes sources et la recherche tant que l’admission est inconnue",()=>{
 const onLoad=vi.fn(),onSearch=vi.fn();renderPanel({reading,results:[result],query:"source",sourceReadBlocked:true,onLoad,onSearch});
 expect(screen.queryByText("Version dce-1")).toBeNull();
 expect(screen.getByRole("button",{name:"Actualiser la lecture"})).toBeDisabled();
 expect(screen.getByText(/Admission DCE en cours ou UNKNOWN/)).toBeVisible();
});
