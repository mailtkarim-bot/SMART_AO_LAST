import { useEffect, useState } from "react";
import type { ApiClient } from "../../infrastructure/api";
import type { PaymentCycleReview } from "../../shared/types";

export function usePaymentCycleReviews(api: ApiClient, cycleIds: string[]) {
  const [reviews, setReviews] = useState<Record<string, PaymentCycleReview[]>>({});
  const [reload, setReload] = useState(0);
  const cycleKey = cycleIds.join(",");
  useEffect(() => {
    let active = true;
    setReviews({});
    if (typeof api.listPaymentCycleReviews !== "function") { setReviews({}); return () => { active = false; }; }
    void Promise.all(cycleIds.map(async (id) => [id, (await api.listPaymentCycleReviews(id)) ?? []] as const)).then((entries) => { if (active) setReviews(Object.fromEntries(entries)); }).catch(() => { if (active) setReviews({}); });
    return () => { active = false; };
    // API client is stable for this resource; cycleKey controls reloads.
    // API client and cycle ids are stable resource inputs for this read model.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cycleKey, reload]);
  return { reviews, refresh: () => setReload((value) => value + 1) };
}
