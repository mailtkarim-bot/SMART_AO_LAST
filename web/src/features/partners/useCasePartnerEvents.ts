import { useCallback, useEffect, useRef, useState } from "react";

import type { ApiClient } from "../../infrastructure/api";
import type { CasePartnerEvent, CasePartnerEventList } from "../../shared/types";

export type CasePartnerReadStatus = "LOADING" | "READY" | "FORBIDDEN" | "UNAVAILABLE" | "NO_CASE";
type ReadState = {
  caseId: string;
  events: CasePartnerEvent[];
  canRequest: boolean;
  canReceive: boolean;
  canDeclareEngagement: boolean;
  status: CasePartnerReadStatus;
};

function empty(caseId: string, status: CasePartnerReadStatus): ReadState {
  return {
    caseId,
    events: [],
    canRequest: false,
    canReceive: false,
    canDeclareEngagement: false,
    status,
  };
}

export function useCasePartnerEvents(api: ApiClient, caseId: string) {
  const apiRef = useRef(api);
  const [state, setState] = useState(() => empty(caseId, caseId ? "LOADING" : "NO_CASE"));

  useEffect(() => {
    apiRef.current = api;
  }, [api]);

  const load = useCallback(async (isActive: () => boolean = () => true) => {
    if (!caseId) {
      if (isActive()) {
        setState((current) => current.caseId === caseId && current.status === "NO_CASE"
          ? current
          : empty(caseId, "NO_CASE"));
      }
      return;
    }
    setState((current) => current.caseId === caseId ? current : empty(caseId, "LOADING"));
    try {
      const data: CasePartnerEventList = await apiRef.current.listCasePartnerEvents(caseId);
      if (!isActive()) return;
      if (data.case_id !== caseId || !Array.isArray(data.events)) {
        setState((current) => current.caseId === caseId && current.status === "UNAVAILABLE"
          ? current
          : empty(caseId, "UNAVAILABLE"));
        return;
      }
      setState((current) => current.caseId === caseId && current.status === "READY"
        && JSON.stringify(current.events) === JSON.stringify(data.events)
        && current.canRequest === data.can_request
        && current.canReceive === data.can_receive
        && current.canDeclareEngagement === data.can_declare_engagement
        ? current
        : {
          caseId,
          events: data.events,
          canRequest: data.can_request,
          canReceive: data.can_receive,
          canDeclareEngagement: data.can_declare_engagement,
          status: "READY",
        });
    } catch (error) {
      if (!isActive()) return;
      const status = (error as { status?: number })?.status === 403 ? "FORBIDDEN" : "UNAVAILABLE";
      setState((current) => current.caseId === caseId && current.status === status
        ? current
        : empty(caseId, status));
    }
  }, [caseId]);

  useEffect(() => {
    let active = true;
    void load(() => active);
    return () => { active = false; };
  }, [load]);

  const refresh = useCallback(() => load(), [load]);
  const visible = state.caseId === caseId ? state : empty(caseId, caseId ? "LOADING" : "NO_CASE");
  const list: CasePartnerEventList | null = visible.status === "READY"
    ? {
      case_id: visible.caseId,
      events: visible.events,
      can_request: visible.canRequest,
      can_receive: visible.canReceive,
      can_declare_engagement: visible.canDeclareEngagement,
    }
    : null;
  return { status: visible.status, list, refresh };
}
