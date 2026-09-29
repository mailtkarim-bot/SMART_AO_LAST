import { useEffect, useState } from "react";
import type { ApiClient } from "../../infrastructure/api";
import type { ContractInstrumentSupersession, ContractInstrumentVersion } from "../../shared/types";

const EMPTY_VERSIONS: ContractInstrumentVersion[] = [];
const EMPTY_SUPERSESSIONS: ContractInstrumentSupersession[] = [];
export type ContractInstrumentVersionReadStatus = "LOADING" | "READY" | "UNAVAILABLE";
type ReadState = {
  caseId: string;
  items: ContractInstrumentVersion[];
  supersessions: ContractInstrumentSupersession[];
  status: ContractInstrumentVersionReadStatus;
};

export function useContractInstrumentVersions(api: ApiClient, caseId: string) {
  const [state, setState] = useState<ReadState>({
    caseId, items: EMPTY_VERSIONS, supersessions: EMPTY_SUPERSESSIONS, status: "LOADING",
  });
  const [reload, setReload] = useState(0);

  useEffect(() => {
    let active = true;
    if (
      !caseId
      || typeof api.listContractInstrumentVersions !== "function"
      || typeof api.listContractInstrumentSupersessions !== "function"
    ) {
      setState((current) => current.caseId === caseId && current.status === "UNAVAILABLE"
        ? current
        : { caseId, items: EMPTY_VERSIONS, supersessions: EMPTY_SUPERSESSIONS, status: "UNAVAILABLE" });
      return () => { active = false; };
    }
    setState((current) => current.caseId === caseId
      ? current
      : { caseId, items: EMPTY_VERSIONS, supersessions: EMPTY_SUPERSESSIONS, status: "LOADING" });
    void Promise.all([
      api.listContractInstrumentVersions(caseId),
      api.listContractInstrumentSupersessions(caseId),
    ]).then(([versionResult, supersessionResult]) => {
      if (!active) return;
      if (!Array.isArray(versionResult) || !Array.isArray(supersessionResult)) {
        setState((current) => current.caseId === caseId && current.status === "UNAVAILABLE"
          ? current
          : { caseId, items: EMPTY_VERSIONS, supersessions: EMPTY_SUPERSESSIONS, status: "UNAVAILABLE" });
        return;
      }
      const items = versionResult.filter((item) => item.case_id === caseId);
      const supersessions = supersessionResult.filter((item) => item.case_id === caseId);
      setState((current) => {
        const versionsUnchanged = current.items.length === items.length
          && current.items.every((item, index) => (
            item.contract_instrument_version_id === items[index]?.contract_instrument_version_id
          ));
        const supersessionsUnchanged = current.supersessions.length === supersessions.length
          && current.supersessions.every((item, index) => (
            item.supersession_id === supersessions[index]?.supersession_id
          ));
        return current.caseId === caseId && current.status === "READY"
          && versionsUnchanged && supersessionsUnchanged
          ? current
          : { caseId, items, supersessions, status: "READY" };
      });
    }).catch(() => {
      if (active) setState({ caseId, items: EMPTY_VERSIONS, supersessions: EMPTY_SUPERSESSIONS, status: "UNAVAILABLE" });
    });
    return () => { active = false; };
  }, [api, caseId, reload]);

  const visible = state.caseId === caseId ? state : {
    caseId, items: EMPTY_VERSIONS, supersessions: EMPTY_SUPERSESSIONS, status: "LOADING" as const,
  };
  return {
    items: visible.items,
    supersessions: visible.supersessions,
    status: visible.status,
    refresh: () => setReload((value) => value + 1),
  };
}
