import { useEffect, useState } from "react";
import type { ApiClient } from "../../infrastructure/api";
import type {
  ContractExecutionEvidence,
  ContractExecutionEvidenceRequalification,
  ContractExecutionEvidenceTimelineEvent,
} from "../../shared/types";

const EMPTY_EVIDENCE: ContractExecutionEvidence[] = [];
const EMPTY_REQUALIFICATIONS: ContractExecutionEvidenceRequalification[] = [];
const EMPTY_TIMELINE: ContractExecutionEvidenceTimelineEvent[] = [];
export type ContractExecutionEvidenceReadStatus = "LOADING" | "READY" | "UNAVAILABLE";
type ReadState = {
  caseId: string;
  items: ContractExecutionEvidence[];
  requalifications: ContractExecutionEvidenceRequalification[];
  timeline: ContractExecutionEvidenceTimelineEvent[];
  status: ContractExecutionEvidenceReadStatus;
};

export function useContractExecutionEvidence(api: ApiClient, caseId: string) {
  const [state, setState] = useState<ReadState>({
    caseId, items: EMPTY_EVIDENCE, requalifications: EMPTY_REQUALIFICATIONS,
    timeline: EMPTY_TIMELINE, status: "LOADING",
  });
  const [reload, setReload] = useState(0);

  useEffect(() => {
    let active = true;
    if (
      !caseId
      || typeof api.listContractExecutionEvidence !== "function"
      || typeof api.listContractExecutionEvidenceRequalifications !== "function"
      || typeof api.listContractExecutionEvidenceTimeline !== "function"
    ) {
      setState((current) => current.caseId === caseId && current.status === "UNAVAILABLE"
        ? current
        : { caseId, items: EMPTY_EVIDENCE, requalifications: EMPTY_REQUALIFICATIONS, timeline: EMPTY_TIMELINE, status: "UNAVAILABLE" });
      return () => { active = false; };
    }
    setState((current) => current.caseId === caseId
      ? current
      : { caseId, items: EMPTY_EVIDENCE, requalifications: EMPTY_REQUALIFICATIONS, timeline: EMPTY_TIMELINE, status: "LOADING" });
    void Promise.all([
      api.listContractExecutionEvidence(caseId),
      api.listContractExecutionEvidenceRequalifications(caseId),
      api.listContractExecutionEvidenceTimeline(caseId),
    ]).then(([result, requalificationResult, timelineResult]) => {
      if (!active) return;
      if (!Array.isArray(result) || !Array.isArray(requalificationResult) || !Array.isArray(timelineResult)) {
        setState((current) => current.caseId === caseId && current.status === "UNAVAILABLE"
          ? current
          : { caseId, items: EMPTY_EVIDENCE, requalifications: EMPTY_REQUALIFICATIONS, timeline: EMPTY_TIMELINE, status: "UNAVAILABLE" });
        return;
      }
      const items = result.filter((item) => item.case_id === caseId);
      const requalifications = requalificationResult.filter((item) => item.case_id === caseId);
      const timeline = timelineResult.filter((item) => item.case_id === caseId);
      setState((current) => {
        const actsUnchanged = current.items.length === items.length
          && current.items.every((item, index) => JSON.stringify(item) === JSON.stringify(items[index]));
        const reviewsUnchanged = current.requalifications.length === requalifications.length
          && current.requalifications.every((item, index) => (
            item.requalification_id === requalifications[index]?.requalification_id
          ));
        const timelineUnchanged = current.timeline.length === timeline.length
          && current.timeline.every((item, index) => JSON.stringify(item) === JSON.stringify(timeline[index]));
        return current.caseId === caseId && current.status === "READY"
          && actsUnchanged && reviewsUnchanged && timelineUnchanged
          ? current
          : { caseId, items, requalifications, timeline, status: "READY" };
      });
    }).catch(() => {
      if (active) setState((current) => current.caseId === caseId && current.status === "UNAVAILABLE"
        ? current
        : { caseId, items: EMPTY_EVIDENCE, requalifications: EMPTY_REQUALIFICATIONS, timeline: EMPTY_TIMELINE, status: "UNAVAILABLE" });
    });
    return () => { active = false; };
  }, [api, caseId, reload]);

  const visible = state.caseId === caseId ? state : {
    caseId, items: EMPTY_EVIDENCE, requalifications: EMPTY_REQUALIFICATIONS,
    timeline: EMPTY_TIMELINE, status: "LOADING" as const,
  };
  return {
    items: visible.items,
    requalifications: visible.requalifications,
    timeline: visible.timeline,
    status: visible.status,
    refresh: () => setReload((value) => value + 1),
  };
}
