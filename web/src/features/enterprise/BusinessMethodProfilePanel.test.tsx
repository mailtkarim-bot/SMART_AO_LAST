import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ApiClient } from "../../infrastructure/api";
import type {
  BusinessMethodProfileAdoption,
  BusinessMethodProfileVersion,
} from "../../shared/types";
import { BusinessMethodProfilePanel } from "./BusinessMethodProfilePanel";
import { useBusinessMethodProfile } from "./useBusinessMethodProfile";

const v1: BusinessMethodProfileVersion = {
  profile_version_id: "profile-1",
  version: 1,
  schema_version: 1,
  profile: { schema_version: 1, terminology: { lot: "Lot" }, additional_checks: [] },
  content_sha256: "1".repeat(64),
};
const v2: BusinessMethodProfileVersion = {
  profile_version_id: "profile-2",
  version: 2,
  schema_version: 1,
  profile: { schema_version: 1, terminology: { lot: "Zone" }, additional_checks: [] },
  content_sha256: "2".repeat(64),
};
const initialAdoption: BusinessMethodProfileAdoption = {
  adoption_id: "adoption-1",
  case_id: "case-1",
  adoption_revision: 1,
  profile_version_id: "profile-1",
  profile_version: 1,
  profile_content_sha256: v1.content_sha256,
};

function renderPanel(overrides: Record<string, unknown> = {}) {
  const api = {
    listBusinessMethodProfileVersions: vi.fn().mockResolvedValue({ company_id: "company-1", versions: [v1, v2] }),
    getBusinessMethodProfileAdoption: vi.fn().mockResolvedValue(initialAdoption),
    publishBusinessMethodProfile: vi.fn().mockResolvedValue({ aggregate_refs: [{ aggregate_type: "BusinessMethodProfile", aggregate_id: "profile-3", aggregate_revision: 3, content_hash: "3".repeat(64) }] }),
    adoptBusinessMethodProfile: vi.fn().mockResolvedValue({ aggregate_refs: [{ aggregate_type: "BusinessMethodProfileAdoption", aggregate_id: "adoption-2", aggregate_revision: 2 }] }),
    ...overrides,
  } as unknown as ApiClient;
  const setMessage = vi.fn();
  function Harness() {
    const manager = useBusinessMethodProfile(api, setMessage, "company-1", "case-1");
    return <BusinessMethodProfilePanel companyId="company-1" caseId="case-1" canManage manager={manager} />;
  }
  return { ...render(<Harness />), api };
}

describe("BusinessMethodProfilePanel", () => {
  it("prévisualise seulement le schéma borné avant de publier une nouvelle version", async () => {
    const { api } = renderPanel();
    await screen.findByText("profile-1");
    fireEvent.change(screen.getByLabelText("Vocabulaire · Lot"), { target: { value: "Zone travaux" } });
    fireEvent.click(screen.getByRole("button", { name: "Ajouter un contrôle informatif" }));
    fireEvent.change(screen.getByLabelText("Clé"), { target: { value: "site_access" } });
    fireEvent.change(screen.getByLabelText("Libellé"), { target: { value: "Accès au site occupé" } });
    fireEvent.click(screen.getByText("Aperçu local du profil à publier"));
    const preview = screen.getByLabelText("Aperçu JSON local du profil");
    expect(preview).toHaveTextContent(/"schema_version": 1/);
    expect(preview).toHaveTextContent(/"Zone travaux"/);
    expect(preview).toHaveTextContent(/"site_access"/);

    fireEvent.click(screen.getByRole("button", { name: "Publier la version v3" }));
    await waitFor(() => expect(api.publishBusinessMethodProfile).toHaveBeenCalledOnce());
    expect(api.publishBusinessMethodProfile).toHaveBeenCalledWith("company-1", expect.objectContaining({
      expected_version: 2,
      profile: {
        schema_version: 1,
        terminology: { lot: "Zone travaux" },
        additional_checks: [{ key: "site_access", label: "Accès au site occupé", axis: "CONTRACT" }],
      },
    }));
  });

  it("adopte une version publiée par identifiant, numéro et empreinte exacts", async () => {
    const refreshedAdoption = vi.fn()
      .mockResolvedValueOnce(initialAdoption)
      .mockResolvedValue({
        ...initialAdoption,
        adoption_id: "adoption-2",
        adoption_revision: 2,
        profile_version_id: v2.profile_version_id,
        profile_version: v2.version,
        profile_content_sha256: v2.content_sha256,
      });
    const { api } = renderPanel({ getBusinessMethodProfileAdoption: refreshedAdoption });
    await screen.findByText("profile-1");
    fireEvent.change(screen.getByLabelText("Version à prévisualiser ou adopter"), { target: { value: "profile-2" } });
    fireEvent.click(screen.getByRole("button", { name: "Adopter v2 pour l’Affaire" }));
    await waitFor(() => expect(api.adoptBusinessMethodProfile).toHaveBeenCalledOnce());
    expect(api.adoptBusinessMethodProfile).toHaveBeenCalledWith("case-1", expect.objectContaining({
      expected_adoption_revision: 1,
      profile_version_id: "profile-2",
      profile_version: 2,
      profile_content_sha256: v2.content_sha256,
    }));
  });
});
