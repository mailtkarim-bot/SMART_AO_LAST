import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import { ExportProofVerificationPanel } from "./ExportProofVerificationPanel";

test("affiche MISMATCH sans action d’envoi", () => {
  render(<ExportProofVerificationPanel verification={{ status: "MISMATCH", calculated_sha256: "a".repeat(64) }} />);
  expect(screen.getByText("MISMATCH")).toBeInTheDocument();
  expect(screen.getByText(/aucune réception externe/i)).toBeInTheDocument();
  expect(screen.queryByRole("button")).not.toBeInTheDocument();
});
