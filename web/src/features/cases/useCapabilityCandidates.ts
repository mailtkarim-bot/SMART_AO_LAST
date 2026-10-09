import { useCallback, useEffect, useRef, useState } from "react";

import type { ApiClient } from "../../infrastructure/api";
import type { CapabilityCandidate } from "../../shared/types";

export type Candidate = {
  capabilityId: string;
  kind: CapabilityCandidate["capability_kind"];
  name: string;
  versionId: string;
  versionNumber: number;
  title: string;
  validFrom: string | null;
  validUntil: string | null;
  validityState: CapabilityCandidate["validity_state"] | "UNKNOWN";
  sourceEvidenceState: CapabilityCandidate["source_evidence_state"];
  evaluatedAt: string | null;
};

type Reading = {
  key: string;
  candidates: Candidate[] | null;
  loading: boolean;
  error: string | null;
};

const empty: Reading = { key: "", candidates: null, loading: false, error: null };
const kinds: CapabilityCandidate["capability_kind"][] = ["QUALIFICATION", "REFERENCE", "EQUIPMENT", "TEAM", "METHOD"];

function validIsoDate(value: string | null | undefined): value is string {
  if (!value || !/^\d{4}-\d{2}-\d{2}T(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d(?:\.\d{1,6})?(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)$/.test(value) || !Number.isFinite(Date.parse(value))) return false;
  const [year, month, day] = value.slice(0, 10).split("-").map(Number);
  return month >= 1 && month <= 12 && day >= 1 && day <= new Date(Date.UTC(year, month, 0)).getUTCDate();
}

function isCandidate(value: unknown): value is CapabilityCandidate {
  if (!value || typeof value !== "object") return false;
  const row = value as Record<string, unknown>;
  return typeof row.capability_id === "string" && row.capability_id.length > 0
    && typeof row.version_id === "string" && row.version_id.length > 0
    && typeof row.name === "string" && typeof row.title === "string"
    && kinds.includes(row.capability_kind as CapabilityCandidate["capability_kind"])
    && Number.isInteger(row.version_number) && Number(row.version_number) > 0
    && typeof row.valid_from === "string"
    && (row.valid_until === null || typeof row.valid_until === "string")
    && (row.evaluated_at === null || typeof row.evaluated_at === "string")
    && (row.valid_until === null || validIsoDate(row.valid_until as string))
    && ["CURRENT", "EXPIRED"].includes(String(row.validity_state))
    && ["CURRENT", "EXPIRED", "UNKNOWN"].includes(String(row.source_evidence_state));
}

export function useCapabilityCandidates(
  api: Pick<ApiClient, "getCapabilityCandidates">,
  caseId: string,
  scopeKey: string,
) {
  const [reading, setReading] = useState<Reading>(empty);
  const apiRef = useRef(api);
  const requestSequence = useRef(0);
  const key = scopeKey && caseId ? JSON.stringify([scopeKey, caseId]) : "";
  useEffect(() => { apiRef.current = api; }, [api]);

  const refresh = useCallback(async () => {
    const request = ++requestSequence.current;
    if (!key) {
      setReading(empty);
      return;
    }
    setReading({ key, candidates: null, loading: true, error: null });
    try {
      const response = await apiRef.current.getCapabilityCandidates(caseId);
      if (!Array.isArray(response) || !response.every(isCandidate)) throw new Error("Invalid capability candidate projection");
      const candidates = response.map((item): Candidate => {
        const validPeriod = validIsoDate(item.valid_from)
          && (item.valid_until === null || validIsoDate(item.valid_until));
        return {
        capabilityId: item.capability_id,
        kind: item.capability_kind,
        name: item.name,
        versionId: item.version_id,
        versionNumber: item.version_number,
        title: item.title,
        validFrom: validPeriod ? item.valid_from : null,
        validUntil: validPeriod ? item.valid_until : null,
        validityState: validPeriod ? item.validity_state : "UNKNOWN",
        sourceEvidenceState: validIsoDate(item.evaluated_at) ? item.source_evidence_state : "UNKNOWN",
        evaluatedAt: validIsoDate(item.evaluated_at) ? item.evaluated_at : null,
      };
      });
      if (request === requestSequence.current) setReading({ key, candidates, loading: false, error: null });
    } catch {
      if (request === requestSequence.current) {
        setReading({ key, candidates: null, loading: false, error: "La liste des moyens proposés est indisponible. Réessayez." });
      }
    }
  }, [caseId, key]);

  useEffect(() => {
    void refresh();
    return () => {
      // This counter invalidates the pending request when the active scope changes.
      // eslint-disable-next-line react-hooks/exhaustive-deps
      requestSequence.current++;
    };
  }, [refresh]);

  const current = key && reading.key === key ? reading : empty;
  return {
    candidates: current.candidates,
    loading: Boolean(key) && (reading.key !== key || current.loading),
    error: current.error,
    refresh,
  };
}
