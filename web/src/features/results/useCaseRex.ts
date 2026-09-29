import { useCallback, useEffect, useState } from "react";
import type { ApiClient } from "../../infrastructure/api";
import type { CaseRex } from "../../shared/types";

export type CaseRexStatus = "LOADING" | "READY" | "UNAVAILABLE";
type ReadState = { caseId: string; rex: CaseRex[] | null; status: CaseRexStatus };

export function useCaseRex(api: ApiClient, caseId: string) {
  const [state, setState] = useState<ReadState>({ caseId, rex: null, status: "LOADING" });
  const load = useCallback(async (showLoading: boolean, isActive: () => boolean = () => true) => {
    if (!caseId || typeof api.listCaseRex !== "function") {
      setState((current) => current.caseId === caseId && current.status === "UNAVAILABLE"
        ? current
        : { caseId, rex: null, status: "UNAVAILABLE" });
      return;
    }
    setState((current) => {
      if (current.caseId !== caseId) return { caseId, rex: null, status: "LOADING" };
      if (showLoading && current.status !== "LOADING") return { caseId, rex: current.rex, status: "LOADING" };
      return current;
    });
    try {
      const data = await api.listCaseRex(caseId);
      if (!isActive()) return;
      if (data.case_id !== caseId || !Array.isArray(data.rex)) {
        setState((current) => current.caseId === caseId && current.status === "UNAVAILABLE"
          ? current
          : { caseId, rex: current.caseId === caseId ? current.rex : null, status: "UNAVAILABLE" });
        return;
      }
      setState((current) => current.caseId === caseId && current.status === "READY"
        && JSON.stringify(current.rex) === JSON.stringify(data.rex)
        ? current
        : { caseId, rex: data.rex, status: "READY" });
    } catch {
      if (isActive()) setState((current) => current.caseId === caseId && current.status === "UNAVAILABLE"
        ? current
        : { caseId, rex: current.caseId === caseId ? current.rex : null, status: "UNAVAILABLE" });
    }
  }, [api, caseId]);

  useEffect(() => {
    let active = true;
    void load(false, () => active);
    return () => { active = false; };
  }, [load]);

  const refresh = useCallback(() => load(true), [load]);

  const visible = state.caseId === caseId ? state : { caseId, rex: null, status: "LOADING" as const };
  return { rex: visible.rex, status: visible.status, refresh };
}
