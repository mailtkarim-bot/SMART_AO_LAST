import { useEffect, useState } from "react";
import type { ApiClient } from "../../infrastructure/api";
import type { PostReceptionObligation } from "../../shared/types";

const EMPTY_OBLIGATIONS: PostReceptionObligation[] = [];

export function usePostReceptionObligations(api: ApiClient, caseId: string) {
  const [items, setItems] = useState<PostReceptionObligation[]>(EMPTY_OBLIGATIONS);
  const [reload, setReload] = useState(0);
  useEffect(() => {
    let active = true;
    setItems((current) => current.length === 0 ? current : EMPTY_OBLIGATIONS);
    if (!caseId || typeof api.listPostReceptionObligations !== "function") return () => { active = false; };
    void Promise.resolve().then(() => api.listPostReceptionObligations(caseId)).then((result) => {
      if (active && Array.isArray(result)) setItems(result.filter((item) => item.case_id === caseId));
    }).catch(() => { if (active) setItems((current) => current.length === 0 ? current : EMPTY_OBLIGATIONS); });
    return () => { active = false; };
  }, [api, caseId, reload]);
  return { items, refresh: () => setReload((value) => value + 1) };
}
