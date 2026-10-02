import type { Dispatch, SetStateAction } from "react";
import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ApiClient } from "../../infrastructure/api";
import type { BusinessMethodProfileContent } from "../../shared/types";
import { useBusinessMethodProfile } from "./useBusinessMethodProfile";

type Message = { tone: "success" | "error" | "warning"; text: string };

const content: BusinessMethodProfileContent = {
  schema_version: 1,
  terminology: { lot: "Zone travaux" },
  additional_checks: [{ key: "site_access", label: "Accès à vérifier", axis: "CONTRACT" }],
};

function apiWith(publishBusinessMethodProfile: ReturnType<typeof vi.fn>): ApiClient {
  return {
    listBusinessMethodProfileVersions: vi.fn().mockResolvedValue({ company_id: "company-1", versions: [] }),
    getBusinessMethodProfileAdoption: vi.fn().mockResolvedValue(null),
    publishBusinessMethodProfile,
    adoptBusinessMethodProfile: vi.fn(),
  } as unknown as ApiClient;
}

describe("useBusinessMethodProfile", () => {
  it("réutilise le même command_id et la même idempotency_key après une réponse inconnue", async () => {
    const publishBusinessMethodProfile = vi.fn()
      .mockRejectedValueOnce(new Error("Résultat à vérifier"))
      .mockResolvedValueOnce({ aggregate_refs: [{ aggregate_type: "BusinessMethodProfile", aggregate_id: "profile-1", aggregate_revision: 1, content_hash: "a".repeat(64) }] });
    const api = apiWith(publishBusinessMethodProfile);
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<Message | null>>;
    const { result } = renderHook(() => useBusinessMethodProfile(api, setMessage, "company-1", "case-1"));
    await waitFor(() => expect(result.current.status).toBe("AVAILABLE"));

    let first = false;
    await act(async () => { first = await result.current.publish(content); });
    expect(first).toBe(false);
    let retry = false;
    await act(async () => { retry = await result.current.publish(content); });
    expect(retry).toBe(true);
    expect(publishBusinessMethodProfile).toHaveBeenCalledTimes(2);
    expect(publishBusinessMethodProfile.mock.calls[1][1]).toEqual(
      publishBusinessMethodProfile.mock.calls[0][1],
    );
    expect(publishBusinessMethodProfile.mock.calls[0][1]).toMatchObject({
      expected_version: 0,
      profile: content,
    });
  });

  it("masque le profil adopté de l’ancienne Affaire pendant le changement de périmètre", async () => {
    const api = {
      listBusinessMethodProfileVersions: vi.fn().mockResolvedValue({ company_id: "company-1", versions: [] }),
      getBusinessMethodProfileAdoption: vi.fn(async (caseId: string) => ({
        adoption_id: `adoption-${caseId}`,
        case_id: caseId,
        adoption_revision: 1,
        profile_version_id: `profile-${caseId}`,
        profile_version: 1,
        profile_content_sha256: "a".repeat(64),
      })),
      publishBusinessMethodProfile: vi.fn(),
      adoptBusinessMethodProfile: vi.fn(),
    } as unknown as ApiClient;
    const setMessage = vi.fn() as unknown as Dispatch<SetStateAction<Message | null>>;
    const { result, rerender } = renderHook(
      ({ caseId }) => useBusinessMethodProfile(api, setMessage, "company-1", caseId),
      { initialProps: { caseId: "case-1" } },
    );
    await waitFor(() => expect(result.current.adoption?.case_id).toBe("case-1"));
    rerender({ caseId: "case-2" });
    expect(result.current.adoption).toBeNull();
    await waitFor(() => expect(result.current.adoption?.case_id).toBe("case-2"));
  });
});
