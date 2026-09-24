import { useEffect, useState } from "react";
import type { Dispatch, SetStateAction } from "react";
import type { ApiClient } from "../../infrastructure/api";
import type { ContractProofReview } from "../../shared/types";
type SetMessage = Dispatch<SetStateAction<{ tone: "success" | "error" | "warning"; text: string } | null>>;
export function useContractProofReviews(api: ApiClient, setMessage: SetMessage, caseId: string) {
  const [reviews, setReviews] = useState<ContractProofReview[]>([]);
  const [loading, setLoading] = useState(false);
  async function refresh(target = caseId) {
    if (!target) return setReviews([]);
    setLoading(true);
    try { setReviews((await api.listContractProofReviews(target))?.items ?? []); }
    catch (error) { setReviews([]); setMessage({ tone: "error", text: error instanceof Error ? error.message : "Impossible de charger la revue contractuelle." }); }
    finally { setLoading(false); }
  }
  useEffect(() => { void refresh(); // selected case is the resource key
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [caseId]);
  return { reviews, loading, refresh };
}
