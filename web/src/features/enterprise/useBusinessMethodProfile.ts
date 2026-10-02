import { useEffect, useState } from "react";
import type { Dispatch, SetStateAction } from "react";

import type { ApiClient } from "../../infrastructure/api";
import type {
  AdoptBusinessMethodProfileInput,
  BusinessMethodProfileAdoption,
  BusinessMethodProfileContent,
  BusinessMethodProfileVersion,
  PublishBusinessMethodProfileInput,
} from "../../shared/types";

type Message = { tone: "success" | "error" | "warning"; text: string };
type SetMessage = Dispatch<SetStateAction<Message | null>>;
export type BusinessMethodProfileStatus = "NO_COMPANY" | "LOADING" | "AVAILABLE" | "UNAVAILABLE";

export function useBusinessMethodProfile(
  api: ApiClient,
  setMessage: SetMessage,
  companyId: string,
  caseId: string,
) {
  const resourceKey = `${companyId}:${caseId}`;
  const [versions, setVersions] = useState<BusinessMethodProfileVersion[]>([]);
  const [adoption, setAdoption] = useState<BusinessMethodProfileAdoption | null>(null);
  const [loadedFor, setLoadedFor] = useState("");
  const [selectedVersionId, setSelectedVersionId] = useState("");
  const [status, setStatus] = useState<BusinessMethodProfileStatus>("LOADING");
  const [refreshKey, setRefreshKey] = useState(0);
  const [publishing, setPublishing] = useState(false);
  const [adopting, setAdopting] = useState(false);
  const [pendingPublish, setPendingPublish] = useState<PublishBusinessMethodProfileInput | null>(null);
  const [pendingAdoption, setPendingAdoption] = useState<AdoptBusinessMethodProfileInput | null>(null);
  const currentResourceLoaded = loadedFor === resourceKey;
  const currentVersions = currentResourceLoaded ? versions : [];
  const currentAdoption = currentResourceLoaded ? adoption : null;
  const currentStatus = !companyId || !caseId
    ? "NO_COMPANY"
    : currentResourceLoaded
      ? status
      : "LOADING";

  useEffect(() => setPendingPublish(null), [companyId]);
  useEffect(() => setPendingAdoption(null), [caseId]);

  useEffect(() => {
    let active = true;
    if (!companyId || !caseId) {
      setVersions([]);
      setAdoption(null);
      setSelectedVersionId("");
      setStatus("NO_COMPANY");
      setLoadedFor(resourceKey);
      return () => { active = false; };
    }
    setStatus("LOADING");
    void Promise.all([
      api.listBusinessMethodProfileVersions(companyId),
      api.getBusinessMethodProfileAdoption(caseId),
    ]).then(([page, currentAdoption]) => {
      if (!active) return;
      setVersions(page.versions);
      setAdoption(currentAdoption);
      setSelectedVersionId((current) => {
        if (page.versions.some((item) => item.profile_version_id === current)) return current;
        return currentAdoption?.profile_version_id ?? page.versions.at(-1)?.profile_version_id ?? "";
      });
      setStatus("AVAILABLE");
      setLoadedFor(resourceKey);
    }).catch((error: unknown) => {
      if (!active) return;
      setVersions([]);
      setAdoption(null);
      setStatus("UNAVAILABLE");
      setLoadedFor(resourceKey);
      setMessage({
        tone: "error",
        text: error instanceof Error ? error.message : "Impossible de lire les profils métier.",
      });
    });
    return () => { active = false; };
  }, [api, caseId, companyId, refreshKey, resourceKey, setMessage]);

  async function publish(profile: BusinessMethodProfileContent): Promise<boolean> {
    if (!companyId) return false;
    const expectedVersion = currentVersions.at(-1)?.version ?? 0;
    const input = pendingPublish && pendingPublish.expected_version === expectedVersion &&
      JSON.stringify(pendingPublish.profile) === JSON.stringify(profile)
      ? pendingPublish
      : {
          command_id: crypto.randomUUID(),
          idempotency_key: crypto.randomUUID(),
          correlation_id: crypto.randomUUID(),
          expected_version: expectedVersion,
          profile,
        };
    setPendingPublish(input);
    setPublishing(true);
    try {
      const receipt = await api.publishBusinessMethodProfile(companyId, input);
      const reference = receipt.aggregate_refs.find((item) => item.aggregate_type === "BusinessMethodProfile");
      if (reference?.aggregate_id) setSelectedVersionId(String(reference.aggregate_id));
      setPendingPublish(null);
      setRefreshKey((current) => current + 1);
      setMessage({ tone: "success", text: "Nouvelle version de profil publiée. Les décisions existantes conservent leur snapshot." });
      return true;
    } catch (error) {
      const apiError = error as { status?: number; detail?: string };
      if (apiError.status === 409 && apiError.detail === "STALE_PROFILE_VERSION") {
        setPendingPublish(null);
        setRefreshKey((current) => current + 1);
      }
      setMessage({ tone: "error", text: error instanceof Error ? error.message : "Publication du profil refusée." });
      return false;
    } finally {
      setPublishing(false);
    }
  }

  async function adopt(version: BusinessMethodProfileVersion): Promise<boolean> {
    if (!caseId) return false;
    const expectedAdoptionRevision = currentAdoption?.adoption_revision ?? 0;
    const input = pendingAdoption &&
      pendingAdoption.expected_adoption_revision === expectedAdoptionRevision &&
      pendingAdoption.profile_version_id === version.profile_version_id &&
      pendingAdoption.profile_content_sha256 === version.content_sha256
      ? pendingAdoption
      : {
          command_id: crypto.randomUUID(),
          idempotency_key: crypto.randomUUID(),
          correlation_id: crypto.randomUUID(),
          expected_adoption_revision: expectedAdoptionRevision,
          profile_version_id: version.profile_version_id,
          profile_version: version.version,
          profile_content_sha256: version.content_sha256,
        };
    setPendingAdoption(input);
    setAdopting(true);
    try {
      const receipt = await api.adoptBusinessMethodProfile(caseId, input);
      const reference = receipt.aggregate_refs.find((item) => item.aggregate_type === "BusinessMethodProfileAdoption");
      setAdoption({
        adoption_id: String(reference?.aggregate_id ?? ""),
        case_id: caseId,
        adoption_revision: Number(reference?.aggregate_revision ?? expectedAdoptionRevision + 1),
        profile_version_id: version.profile_version_id,
        profile_version: version.version,
        profile_content_sha256: version.content_sha256,
      });
      setPendingAdoption(null);
      setRefreshKey((current) => current + 1);
      setMessage({ tone: "success", text: `Profil v${version.version} adopté pour cette Affaire. Les décisions précédentes restent figées.` });
      return true;
    } catch (error) {
      const apiError = error as { status?: number; detail?: string };
      if (apiError.status === 409 && apiError.detail === "STALE_PROFILE_ADOPTION") {
        setPendingAdoption(null);
        setRefreshKey((current) => current + 1);
      }
      setMessage({ tone: "error", text: error instanceof Error ? error.message : "Adoption du profil refusée." });
      return false;
    } finally {
      setAdopting(false);
    }
  }

  function refresh() {
    setRefreshKey((current) => current + 1);
  }

  return {
    versions: currentVersions,
    adoption: currentAdoption,
    selectedVersionId,
    setSelectedVersionId,
    status: currentStatus,
    publishing,
    adopting,
    publish,
    adopt,
    refresh,
  };
}
