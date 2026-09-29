import { useCallback, useEffect, useState } from "react";
import type { ApiClient } from "../../infrastructure/api";
import type { CaseExecutionResults } from "../../shared/types";

export type CaseExecutionResultsStatus = "LOADING" | "READY" | "UNAVAILABLE";
type ReadState = { caseId: string; data: CaseExecutionResults | null; status: CaseExecutionResultsStatus };

export function useCaseExecutionResults(api: ApiClient, caseId: string) {
  const [state, setState] = useState<ReadState>({ caseId, data: null, status: "LOADING" });
  const load = useCallback(async (showLoading: boolean, isActive: () => boolean = () => true) => {
    if (!caseId || typeof api.listCaseExecutionResults !== "function") {
      setState((current) => current.caseId === caseId && current.status === "UNAVAILABLE"
        ? current
        : { caseId, data: null, status: "UNAVAILABLE" });
      return;
    }
    setState((current) => {
      if (current.caseId !== caseId) return { caseId, data: null, status: "LOADING" };
      if (showLoading && current.status !== "LOADING") return { caseId, data: current.data, status: "LOADING" };
      return current;
    });
    try {
      const data = await api.listCaseExecutionResults(caseId);
      if (!isActive()) return;
      if (data.case_id !== caseId || !Array.isArray(data.lot_references) || !Array.isArray(data.results)) {
        setState((current) => current.caseId === caseId && current.status === "UNAVAILABLE"
          ? current
          : { caseId, data: current.caseId === caseId ? current.data : null, status: "UNAVAILABLE" });
        return;
      }
      setState((current) => current.caseId === caseId && current.status === "READY"
        && JSON.stringify(current.data) === JSON.stringify(data)
        ? current
        : { caseId, data, status: "READY" });
    } catch {
      if (isActive()) setState((current) => current.caseId === caseId && current.status === "UNAVAILABLE"
        ? current
        : { caseId, data: current.caseId === caseId ? current.data : null, status: "UNAVAILABLE" });
    }
  }, [api, caseId]);

  useEffect(() => {
    let active = true;
    void load(false, () => active);
    return () => { active = false; };
  }, [load]);

  const refresh = useCallback(() => load(true), [load]);

  const visible = state.caseId === caseId ? state : { caseId, data: null, status: "LOADING" as const };
  return { data: visible.data, status: visible.status, refresh };
}
