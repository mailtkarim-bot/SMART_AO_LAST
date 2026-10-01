import { useCallback, useEffect, useRef, useState } from "react";

import type { ApiClient } from "../../infrastructure/api";
import type { CaseTeachingApplicability, CaseTeachingSource } from "../../shared/types";

export type TeachingApplicabilityReadStatus = "LOADING" | "READY" | "UNAVAILABLE";
type ReadState = {
  caseId: string;
  sources: CaseTeachingSource[] | null;
  applicabilities: CaseTeachingApplicability[] | null;
  status: TeachingApplicabilityReadStatus;
};

export function useCaseTeachingApplicability(api: ApiClient, caseId: string) {
  const apiRef = useRef(api);
  const [state, setState] = useState<ReadState>({
    caseId,
    sources: null,
    applicabilities: null,
    status: "LOADING",
  });

  useEffect(() => {
    apiRef.current = api;
  }, [api]);

  const load = useCallback(async (isActive: () => boolean = () => true) => {
    const currentApi = apiRef.current;
    if (!caseId || typeof currentApi.listCaseTeachingSources !== "function"
      || typeof currentApi.listCaseTeachingApplicabilities !== "function") {
      if (isActive()) setState((current) => current.caseId === caseId && current.status === "UNAVAILABLE"
        ? current
        : { caseId, sources: null, applicabilities: null, status: "UNAVAILABLE" });
      return;
    }
    setState((current) => current.caseId === caseId
      ? current
      : { caseId, sources: null, applicabilities: null, status: "LOADING" });
    try {
      const [sourceData, applicabilityData] = await Promise.all([
        currentApi.listCaseTeachingSources(caseId),
        currentApi.listCaseTeachingApplicabilities(caseId),
      ]);
      if (!isActive()) return;
      if (sourceData.case_id !== caseId || !Array.isArray(sourceData.sources)
        || applicabilityData.case_id !== caseId || !Array.isArray(applicabilityData.applicabilities)) {
        setState((current) => current.caseId === caseId && current.status === "UNAVAILABLE"
          ? current
          : { caseId, sources: null, applicabilities: null, status: "UNAVAILABLE" });
        return;
      }
      setState((current) => current.caseId === caseId && current.status === "READY"
        && JSON.stringify(current.sources) === JSON.stringify(sourceData.sources)
        && JSON.stringify(current.applicabilities) === JSON.stringify(applicabilityData.applicabilities)
        ? current
        : {
          caseId,
          sources: sourceData.sources,
          applicabilities: applicabilityData.applicabilities,
          status: "READY",
        });
    } catch {
      if (isActive()) setState((current) => current.caseId === caseId && current.status === "UNAVAILABLE"
        ? current
        : { caseId, sources: null, applicabilities: null, status: "UNAVAILABLE" });
    }
  }, [caseId]);

  useEffect(() => {
    let active = true;
    void load(() => active);
    return () => { active = false; };
  }, [load]);

  const refresh = useCallback(() => load(), [load]);
  const visible = state.caseId === caseId
    ? state
    : { caseId, sources: null, applicabilities: null, status: "LOADING" as const };
  return { ...visible, refresh };
}
