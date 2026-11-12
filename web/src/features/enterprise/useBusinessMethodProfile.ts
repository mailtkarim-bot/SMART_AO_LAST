import { useEffect, useLayoutEffect, useRef, useState } from "react";
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
  ownerKey = "legacy",
) {
  const resourceKey = `${ownerKey}:${companyId}:${caseId}`;
  const publishKey = `${ownerKey}:${companyId}`;
  const adoptionKey = `${ownerKey}:${caseId}`;
  const activeResource = useRef(resourceKey);
  const busy = useRef(new Set<string>());
  useLayoutEffect(() => { activeResource.current = resourceKey; }, [resourceKey]);
  const [versions, setVersions] = useState<BusinessMethodProfileVersion[]>([]);
  const [history, setHistory] = useState<BusinessMethodProfileAdoption[]>([]);
  const [adoption, setAdoption] = useState<BusinessMethodProfileAdoption | null>(null);
  const [loadedFor, setLoadedFor] = useState("");
  const [selectedVersionId, setSelectedVersionId] = useState("");
  const [status, setStatus] = useState<BusinessMethodProfileStatus>("LOADING");
  const [refreshKey, setRefreshKey] = useState(0);
  const [publishing, setPublishing] = useState(false);
  const [adopting, setAdopting] = useState(false);
  const [pendingPublications, setPendingPublications] = useState<Record<string, PublishBusinessMethodProfileInput | null>>({});
  const [pendingAdoptions, setPendingAdoptions] = useState<Record<string, AdoptBusinessMethodProfileInput | null>>({});
  const pendingPublish = pendingPublications[publishKey] ?? null;
  const pendingAdoption = pendingAdoptions[adoptionKey] ?? null;
  const setPendingPublish = (input: PublishBusinessMethodProfileInput | null) => setPendingPublications((current) => ({ ...current, [publishKey]: input }));
  const setPendingAdoption = (input: AdoptBusinessMethodProfileInput | null) => setPendingAdoptions((current) => ({ ...current, [adoptionKey]: input }));
  const currentResourceLoaded = loadedFor === resourceKey;
  const currentVersions = currentResourceLoaded ? versions : [];
  const currentAdoption = currentResourceLoaded ? adoption : null;
  const currentStatus = !companyId || !caseId
    ? "NO_COMPANY"
    : currentResourceLoaded
      ? status
      : "LOADING";


  useEffect(() => {
    let active = true;
    if (pendingPublish || pendingAdoption) return;
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
      api.listBusinessMethodProfileAdoptions(caseId),
    ]).then(([page, currentAdoption, adoptions]) => {
      if (!active) return;
      setVersions(page.versions);
      setAdoption(currentAdoption);
      setHistory(adoptions);
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
  }, [api, caseId, companyId, refreshKey, resourceKey, setMessage, pendingPublish, pendingAdoption]);

  async function publish(profile: BusinessMethodProfileContent): Promise<boolean> {
    if (!companyId || (!pendingPublish && currentStatus !== "AVAILABLE") || busy.current.has(publishKey)) return false;
    if (pendingPublish && JSON.stringify(pendingPublish.profile) !== JSON.stringify(profile)) return false;
    busy.current.add(publishKey);
    const expectedVersion = pendingPublish?.expected_version ?? currentVersions.at(-1)?.version ?? 0;
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
      if (activeResource.current !== resourceKey) return false;
      const reference = receipt.aggregate_refs.find((item) => item.aggregate_type === "BusinessMethodProfile");
      if (!reference?.aggregate_id || reference.aggregate_revision !== input.expected_version + 1 ||
        typeof reference.content_hash !== "string" || !/^[a-f0-9]{64}$/.test(reference.content_hash)) {
        throw new Error("UNKNOWN : reçu de publication incomplet.");
      }
      setSelectedVersionId(String(reference.aggregate_id));
      setPendingPublish(null);
      setRefreshKey((current) => current + 1);
      setMessage({ tone: "success", text: "Nouvelle version de profil publiée. Les décisions existantes conservent leur snapshot." });
      return true;
    } catch (error) {
      if (activeResource.current !== resourceKey) return false;
      const apiError = error as { status?: number; detail?: string };
      if (apiError.status === 409 && apiError.detail === "STALE_PROFILE_VERSION") {
        setPendingPublish(null);
        setRefreshKey((current) => current + 1);
      }
      setMessage({ tone: "error", text: error instanceof Error ? error.message : "Publication du profil refusée." });
      return false;
    } finally {
      busy.current.delete(publishKey);
      setPublishing(false);
    }
  }

  async function adopt(version: Pick<BusinessMethodProfileVersion, "profile_version_id" | "version" | "content_sha256">): Promise<boolean> {
    if (!caseId || (!pendingAdoption && currentStatus !== "AVAILABLE") || busy.current.has(adoptionKey)) return false;
    if (pendingAdoption && (pendingAdoption.profile_version_id !== version.profile_version_id ||
      pendingAdoption.profile_version !== version.version ||
      pendingAdoption.profile_content_sha256 !== version.content_sha256)) return false;
    busy.current.add(adoptionKey);
    const expectedAdoptionRevision = pendingAdoption?.expected_adoption_revision ?? currentAdoption?.adoption_revision ?? 0;
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
      if (activeResource.current !== resourceKey) return false;
      const reference = receipt.aggregate_refs.find((item) => item.aggregate_type === "BusinessMethodProfileAdoption");
      if (!reference?.aggregate_id || reference.aggregate_revision !== input.expected_adoption_revision + 1) {
        throw new Error("UNKNOWN : reçu d’adoption incomplet.");
      }
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
      if (activeResource.current !== resourceKey) return false;
      const apiError = error as { status?: number; detail?: string };
      if (apiError.status === 409 && apiError.detail === "STALE_PROFILE_ADOPTION") {
        setPendingAdoption(null);
        setRefreshKey((current) => current + 1);
      }
      setMessage({ tone: "error", text: error instanceof Error ? error.message : "Adoption du profil refusée." });
      return false;
    } finally {
      busy.current.delete(adoptionKey);
      setAdopting(false);
    }
  }

  async function resume() {
    if (pendingPublish) return publish(pendingPublish.profile);
    if (pendingAdoption) return adopt({
      profile_version_id: pendingAdoption.profile_version_id,
      version: pendingAdoption.profile_version,
      content_sha256: pendingAdoption.profile_content_sha256,
    });
    return false;
  }

  function refresh() {
    if (pendingPublish || pendingAdoption || (busy.current.has(publishKey) || busy.current.has(adoptionKey))) return;
    setRefreshKey((current) => current + 1);
  }

  return {
    versions: currentVersions,
    history: currentResourceLoaded && status === "AVAILABLE" ? history : [],
    adoption: currentAdoption,
    selectedVersionId,
    setSelectedVersionId,
    status: currentStatus,
    publishing,
    adopting,
    pendingPublish: Boolean(pendingPublish),
    pendingAdoption: Boolean(pendingAdoption),
    publish,
    adopt,
    refresh,
    resume,
  };
}
