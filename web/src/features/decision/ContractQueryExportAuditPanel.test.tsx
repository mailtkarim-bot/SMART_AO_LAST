import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import { ContractQueryExportAuditPanel } from "./ContractQueryExportAuditPanel";

test("affiche les transitions d’audit sans action de mutation", () => {
  render(<ContractQueryExportAuditPanel audit={{ export: { export_id: "e1", case_id: "c1", filters: { status: "SUPERSEDED" }, status: "UNKNOWN", actor_id: "u1", created_at: "2026-09-25T10:00:00Z" }, transitions: [{ transition_id: "t1", from_status: "REQUESTED", to_status: "UNKNOWN", local_proof_ref: null, created_at: "2026-09-25T10:01:00Z" }] }} />);
  expect(screen.getByText("UNKNOWN")).toBeInTheDocument();
  expect(screen.getByText(/REQUESTED → UNKNOWN/)).toBeInTheDocument();
  expect(screen.queryByRole("button")).not.toBeInTheDocument();
});
