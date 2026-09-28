import { useEffect, useState } from "react";
import type { Dispatch, SetStateAction } from "react";
import type { ApiClient } from "../../infrastructure/api";
import type { PaymentCycle } from "../../shared/types";

type SetMessage = Dispatch<SetStateAction<{ tone: "success" | "error" | "warning"; text: string } | null>>;
export function usePaymentCycles(api: ApiClient, setMessage: SetMessage, caseId: string) {
  const [cycles, setCycles] = useState<PaymentCycle[]>([]);
  const [loading, setLoading] = useState(false);
  async function refresh(target = caseId) {
    if (!target) return setCycles([]);
    if (typeof api.listPaymentCycles !== "function") return setCycles([]);
    setLoading(true);
    try {
      const result = await api.listPaymentCycles(target);
      const candidate = result as PaymentCycle[] | { items?: PaymentCycle[] } | undefined;
      setCycles(Array.isArray(candidate) ? candidate : candidate?.items ?? []);
    }
    finally { setLoading(false); }
  }
  useEffect(() => {
    setCycles([]);
    if (!caseId) { setCycles([]); return; }
    void refresh().catch((error) => setMessage({ tone: "error", text: error instanceof Error ? error.message : "Impossible de charger le cycle paiement." }));
    // Selected case is the resource key for this read model.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [caseId]);
  return { cycles, loading, refresh };
}
