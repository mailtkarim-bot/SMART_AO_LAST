import { useCallback, useEffect, useRef, useState } from "react";

import type { ApiClient } from "../../infrastructure/api";
import { caseResolutionItemKinds, type CaseResolution } from "../../shared/types";

type Reading = {
  key: string;
  projection: CaseResolution | null;
  loading: boolean;
  error: string | null;
};

const empty: Reading = { key: "", projection: null, loading: false, error: null };

export function useCaseResolution(
  api: Pick<ApiClient, "getCaseResolution">,
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
    setReading({ key, projection: null, loading: true, error: null });
    try {
      const projection = await apiRef.current.getCaseResolution(caseId);
      if (projection.case_id !== caseId || projection.coverage !== "PARTIAL" || !Array.isArray(projection.items) || !projection.items.every((item) => caseResolutionItemKinds.includes(item.item_kind))) {
        throw new Error("Invalid resolution projection");
      }
      if (request === requestSequence.current) {
        setReading({ key, projection, loading: false, error: null });
      }
    } catch {
      if (request === requestSequence.current) {
        setReading({ key, projection: null, loading: false, error: "Les points à résoudre sont indisponibles. Réessayez." });
      }
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
