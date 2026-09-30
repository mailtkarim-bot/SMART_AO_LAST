import { useCallback, useEffect, useState } from "react";
import type { ApiClient } from "../../infrastructure/api";
import type { CaseInterview } from "../../shared/types";

export type CaseInterviewStatus = "LOADING" | "READY" | "UNAVAILABLE";
type ReadState = { caseId: string; interviews: CaseInterview[] | null; status: CaseInterviewStatus };

export function useCaseInterview(api: ApiClient, caseId: string) {
  const [state, setState] = useState<ReadState>({ caseId, interviews: null, status: "LOADING" });
  const load = useCallback(async (showLoading: boolean, isActive: () => boolean = () => true) => {
    if (!caseId || typeof api.listCaseInterviews !== "function") {
      setState((current) => current.caseId === caseId && current.status === "UNAVAILABLE"
        ? current
        : { caseId, interviews: null, status: "UNAVAILABLE" });
      return;
    }
    setState((current) => {
      if (current.caseId !== caseId) return { caseId, interviews: null, status: "LOADING" };
      if (showLoading && current.status !== "LOADING") return { caseId, interviews: current.interviews, status: "LOADING" };
      return current;
    });
    try {
      const data = await api.listCaseInterviews(caseId);
      if (!isActive()) return;
      if (data.case_id !== caseId || !Array.isArray(data.interviews)) {
        setState((current) => current.caseId === caseId && current.status === "UNAVAILABLE"
          ? current
          : { caseId, interviews: current.caseId === caseId ? current.interviews : null, status: "UNAVAILABLE" });
        return;
      }
      setState((current) => current.caseId === caseId && current.status === "READY"
        && JSON.stringify(current.interviews) === JSON.stringify(data.interviews)
        ? current
        : { caseId, interviews: data.interviews, status: "READY" });
    } catch {
      if (isActive()) setState((current) => current.caseId === caseId && current.status === "UNAVAILABLE"
        ? current
        : { caseId, interviews: current.caseId === caseId ? current.interviews : null, status: "UNAVAILABLE" });
    }
  }, [api, caseId]);

  useEffect(() => {
    let active = true;
    void load(false, () => active);
    return () => { active = false; };
  }, [load]);

  const refresh = useCallback(() => load(true), [load]);

  const visible = state.caseId === caseId ? state : { caseId, interviews: null, status: "LOADING" as const };
  return { interviews: visible.interviews, status: visible.status, refresh };
}
