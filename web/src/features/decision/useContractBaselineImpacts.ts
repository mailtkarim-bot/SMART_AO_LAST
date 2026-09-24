import { useEffect, useState } from "react";
import type { Dispatch, SetStateAction } from "react";
import type { ApiClient } from "../../infrastructure/api";
import type { ContractBaselineImpact } from "../../shared/types";

type SetMessage = Dispatch<SetStateAction<{ tone: "success" | "error" | "warning"; text: string } | null>>;
export function useContractBaselineImpacts(api: ApiClient, setMessage: SetMessage, caseId: string) {
  const [items, setItems] = useState<ContractBaselineImpact[]>([]);
  const [loading, setLoading] = useState(false);
  async function refresh(target = caseId) {
    if (!target) return setItems([]);
    setLoading(true);
    try {
      const page = await api.listContractBaselineImpacts(target);
      setItems(page?.items ?? []);
    }
    catch (error) { setItems([]); setMessage({ tone: "error", text: error instanceof Error ? error.message : "Impossible de charger la preuve contractuelle." }); }
    finally { setLoading(false); }
  }
  useEffect(() => {
    void refresh();
    // The selected case is the resource key for this read model.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [caseId]);
  return { items, loading, refresh };
}
