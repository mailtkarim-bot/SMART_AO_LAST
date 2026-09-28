import { useEffect, useState } from "react";
import type { ApiClient } from "../../infrastructure/api";
import type { PaymentUnknownAudit } from "../../shared/types";

export function usePaymentUnknownAudit(api: ApiClient, caseId: string) {
  const [audit, setAudit] = useState<PaymentUnknownAudit | null>(null);
  const [reload, setReload] = useState(0);
  useEffect(() => {
    let active = true;
    setAudit(null);
    if (!caseId || typeof api.getPaymentUnknownAudit !== "function") { setAudit(null); return () => { active = false; }; }
    void Promise.resolve().then(() => api.getPaymentUnknownAudit(caseId)).then((value) => {
      if (!active) return;
      const candidate = value as PaymentUnknownAudit | undefined;
      setAudit(candidate && candidate.status_counts && Array.isArray(candidate.entries) ? candidate : null);
    }).catch(() => { if (active) setAudit(null); });
    return () => { active = false; };
  }, [api, caseId, reload]);
  return { audit, refresh: () => setReload((value) => value + 1) };
}
