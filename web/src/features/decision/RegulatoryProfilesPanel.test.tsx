import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { RegulatoryProfileProjection } from "../../shared/types";
import { RegulatoryProfilesPanel } from "./RegulatoryProfilesPanel";

const profile: RegulatoryProfileProjection = {
  profile_id: "profile-1",
  case_id: "case-1",
  profile_version: 2,
  status: "UNKNOWN_APPLICABILITY",
  facts: { market_kind: "PUBLIC", work_kind: "INFRASTRUCTURE" },
  source_refs: ["dce:rc:p4"],
  effective_from: null,
  effective_until: null,
};

describe("RegulatoryProfilesPanel", () => {
  it("keeps unknown applicability visible and read-only", () => {
    render(
      <RegulatoryProfilesPanel
        caseId="case-1"
        profiles={[profile]}
        loading={false}
        onRefresh={vi.fn()}
      />,
    );

    expect(screen.getByText("Applicabilité inconnue")).toBeInTheDocument();
    expect(screen.getByText("PUBLIC")).toBeInTheDocument();
    expect(screen.getByText(/aucune conclusion juridique/i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /enregistrer|valider|appliquer/i })).not.toBeInTheDocument();
  });
});
