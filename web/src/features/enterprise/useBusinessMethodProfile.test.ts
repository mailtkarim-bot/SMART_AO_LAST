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
    listBusinessMethodProfileAdoptions: vi.fn().mockResolvedValue([]),
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
      listBusinessMethodProfileAdoptions: vi.fn().mockResolvedValue([]),
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


it("refuse un nouvel intent de publication tant que le précédent reste UNKNOWN", async () => {
  const publish = vi.fn().mockRejectedValue(new Error("Résultat inconnu"));
  const api = apiWith(publish);
  const setMessage = vi.fn();
  const { result } = renderHook(() => useBusinessMethodProfile(api, setMessage, "company-1", "case-1"));
  await waitFor(() => expect(result.current.status).toBe("AVAILABLE"));
  await act(async () => { await result.current.publish(content); });
  await act(async () => { await result.current.publish({ ...content, terminology: { lot: "Autre" } }); });
  expect(publish).toHaveBeenCalledTimes(1);
});


it("bloque double clic et GET de réconciliation pendant l’acte non résolu", async () => {
  let resolve!: (receipt: unknown) => void;
  const publish = vi.fn(() => new Promise((done) => { resolve = done; }));
  const api = apiWith(publish);
  const setMessage = vi.fn();
  const { result } = renderHook(() => useBusinessMethodProfile(api, setMessage, "company-1", "case-1"));
  await waitFor(() => expect(result.current.status).toBe("AVAILABLE"));
  let first!: Promise<boolean>;
  act(() => { first = result.current.publish(content); void result.current.publish(content); });
  act(() => result.current.refresh());
  expect(publish).toHaveBeenCalledTimes(1);
  expect(api.listBusinessMethodProfileVersions).toHaveBeenCalledTimes(1);
  await act(async () => { resolve({ aggregate_refs: [{ aggregate_type: "BusinessMethodProfile", aggregate_id: "profile-1", aggregate_revision: 1, content_hash: "a".repeat(64) }] }); await first; });
});


it("reprend l’intent UNKNOWN original après un aller-retour de périmètre", async () => {
  const publish = vi.fn().mockRejectedValueOnce(new Error("UNKNOWN")).mockResolvedValue({aggregate_refs:[{aggregate_type:"BusinessMethodProfile",aggregate_id:"profile-1",aggregate_revision:1,content_hash:"a".repeat(64)}]});
  const api = apiWith(publish);const setMessage = vi.fn();
  const { result, rerender } = renderHook(({ company }) => useBusinessMethodProfile(api,setMessage,company,"case-1"),{initialProps:{company:"company-1"}});
  await waitFor(()=>expect(result.current.status).toBe("AVAILABLE"));
  await act(async()=>{await result.current.publish(content);});
  const first=publish.mock.calls[0][1];
  rerender({company:"company-2"});await waitFor(()=>expect(result.current.status).toBe("AVAILABLE"));
  rerender({company:"company-1"});
  await act(async()=>{await result.current.publish(content);});
  expect(publish).toHaveBeenCalledTimes(2);
  expect(publish.mock.calls[1][1]).toEqual(first);
});
