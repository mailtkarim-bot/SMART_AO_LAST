import { useEffect, useState } from "react";
import type { ApiClient } from "../../infrastructure/api";
import type { PaymentCollectionRejectionReview } from "../../shared/types";
export function usePaymentCollectionRejectionReview(api: ApiClient, caseId: string) {
  const [review, setReview] = useState<PaymentCollectionRejectionReview | null>(null);
  const [reload, setReload] = useState(0);
  useEffect(() => { let active = true; setReview(null); if (!caseId || typeof api.getPaymentCollectionRejectionReview !== "function") return () => { active = false; }; void Promise.resolve().then(() => api.getPaymentCollectionRejectionReview(caseId)).then((value) => { if (active && value?.case_id === caseId) setReview(value); }).catch(() => {}); return () => { active = false; }; }, [api, caseId, reload]);
  return { review, refresh: () => setReload((value) => value + 1) };
}
