import { useEffect, useState } from "react";
import type { ApiClient } from "../../infrastructure/api";
import type { PaymentUnknownAuditOwnerAct } from "../../shared/types";
export function usePaymentUnknownAuditOwnerAct(api: ApiClient, caseId: string) {
  const [act, setAct] = useState<PaymentUnknownAuditOwnerAct | null>(null);
  const [reload, setReload] = useState(0);
  useEffect(() => {
    let active = true;
    setAct(null);
    if (!caseId || typeof api.getPaymentUnknownAuditOwnerAct !== "function") { setAct(null); return () => { active = false; }; }
    void Promise.resolve().then(() => api.getPaymentUnknownAuditOwnerAct(caseId)).then((value) => {
      if (!active) return;
      const candidate = value as PaymentUnknownAuditOwnerAct | null | undefined;
      setAct(candidate && candidate.case_id === caseId && typeof candidate.approved === "boolean" && typeof candidate.rationale === "string" ? candidate : null);
    }).catch(() => { if (active) setAct(null); });
    return () => { active = false; };
  }, [api, caseId, reload]);
  return { act, refresh: () => setReload((value) => value + 1) };
}
