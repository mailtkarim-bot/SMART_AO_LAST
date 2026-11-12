import { useCallback, useEffect, useRef, useState } from "react";

import type { ApiClient } from "../../infrastructure/api";
export type DocumentaryAssessment = { state: "CURRENT" | "EXPIRED" | "UNKNOWN"; evaluatedAt: string | null };

function validEvaluation(value: string | null | undefined): value is string {
  if (!value || !/^\d{4}-\d{2}-\d{2}T(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d(?:\.\d{1,6})?(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)$/.test(value) || !Number.isFinite(Date.parse(value))) return false;
  const [year, month, day] = value.slice(0, 10).split("-").map(Number);
  return month >= 1 && month <= 12 && day >= 1 && day <= new Date(Date.UTC(year, month, 0)).getUTCDate();
}

type Reading = {
  key: string;
  projection: DocumentaryAssessment[] | null;
  loading: boolean;
  error: string | null;
};

const empty: Reading = { key: "", projection: null, loading: false, error: null };

export function useCapabilityAssessments(
  api: Pick<ApiClient, "getCapabilityAssessments">,
  caseId: string,
  scopeKey: string,
) {
  const [reading, setReading] = useState<Reading>(empty);
  const apiRef = useRef(api);
  const requestSequence = useRef(0);
  const key = scopeKey && caseId ? JSON.stringify([scopeKey, caseId]) : "";

  useEffect(() => { apiRef.current = api; }, [api]);

  const refresh = useCallback(async (): Promise<boolean> => {
    const request = ++requestSequence.current;
    if (!key) {
      setReading(empty);
      return false;
    }
    setReading({ key, projection: null, loading: true, error: null });
    try {
      const response = await apiRef.current.getCapabilityAssessments(caseId);
      if (!Array.isArray(response.proposals) || !Array.isArray(response.gaps) || !response.proposals.every(item => item && item.case_id === caseId && (item.source_evidence_state === undefined || ["CURRENT", "EXPIRED", "UNKNOWN"].includes(item.source_evidence_state)))) {
        throw new Error("Invalid documentary assessment projection");
      }
      const projection: DocumentaryAssessment[] = response.proposals.map(item => {
        const evaluatedAt = validEvaluation(item.source_evidence_evaluated_at) ? item.source_evidence_evaluated_at : null;
        return { state: evaluatedAt ? item.source_evidence_state ?? "UNKNOWN" : "UNKNOWN", evaluatedAt };
      });
      if (request === requestSequence.current) {
        setReading({ key, projection, loading: false, error: null });
        return true;
      }
      return false;
    } catch {
      if (request === requestSequence.current) {
        setReading({ key, projection: null, loading: false, error: "La lecture documentaire est indisponible. Réessayez." });
      }
      return false;
    }
  }, [caseId, key]);

  useEffect(() => {
    void refresh();
    return () => {
      // This is a request counter, not a DOM ref; cleanup must invalidate its latest value.
      // eslint-disable-next-line react-hooks/exhaustive-deps
      requestSequence.current++;
    };
  }, [refresh]);

  // Mask the previous scope during render, before the new effect starts its request.
  const current = key && reading.key === key ? reading : empty;
  return {
    projection: current.projection,
    loading: Boolean(key) && (reading.key !== key || current.loading),
    error: current.error,
    refresh,
  };
}
