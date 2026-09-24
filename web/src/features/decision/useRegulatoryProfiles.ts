import { useEffect, useState } from "react";
import type { Dispatch, SetStateAction } from "react";

import type { ApiClient } from "../../infrastructure/api";
import type { RegulatoryProfileProjection } from "../../shared/types";

type Message = { tone: "success" | "error" | "warning"; text: string };
type SetMessage = Dispatch<SetStateAction<Message | null>>;

export function useRegulatoryProfiles(api: ApiClient, setMessage: SetMessage, caseId: string) {
  const [profiles, setProfiles] = useState<RegulatoryProfileProjection[]>([]);
  const [loading, setLoading] = useState(false);

  async function refresh(targetCaseId = caseId) {
    if (!targetCaseId) {
      setProfiles([]);
      return;
    }
    setLoading(true);
    try {
      const page = await api.listRegulatoryProfiles(targetCaseId);
      setProfiles(page.items);
    } catch (error) {
      setProfiles([]);
      setMessage({
        tone: "error",
        text: error instanceof Error ? error.message : "Impossible de charger le profil réglementaire.",
      });
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refresh();
    // The selected case is the resource key for this read model.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [caseId]);

  return { profiles, loading, refresh };
}
