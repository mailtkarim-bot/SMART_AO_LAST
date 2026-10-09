import { useRef, useState } from "react";
import type { Dispatch, SetStateAction } from "react";

import type { ApiClient } from "../../infrastructure/api";
import type { CaseDceReading, KnowledgeSearchResult } from "../../shared/types";

type Message = { tone: "success" | "error" | "warning"; text: string };
type SetMessage = Dispatch<SetStateAction<Message | null>>;

export function useDceKnowledge(
  api: ApiClient,
  setMessage: SetMessage,
  selectedCaseId: string,
  scopeKey = selectedCaseId,
) {
  const [readingEntry, setReadingEntry] = useState<{ key: string; value: CaseDceReading } | null>(null);
  const [results, setResults] = useState<KnowledgeSearchResult[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [searching, setSearching] = useState(false);
  const readingSequence = useRef(0);
  const readingKey = scopeKey && selectedCaseId ? JSON.stringify([scopeKey, selectedCaseId]) : "";
  const reading = readingKey && readingEntry?.key === readingKey ? readingEntry.value : null;

  async function loadReading(caseId = selectedCaseId) {
    const request = ++readingSequence.current;
    const key = scopeKey && caseId ? JSON.stringify([scopeKey, caseId]) : "";
    if (!caseId) {
      setReadingEntry(null);
      setResults([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const value = await api.getCaseDceReading(caseId);
      if (request === readingSequence.current) {
        setReadingEntry(value.case_id === caseId ? { key, value } : null);
      }
    } catch (error) {
      if (request === readingSequence.current) setReadingEntry(null);
      if ((error as { status?: number }).status === 404) return;
      setMessage({
        tone: "error",
        text: error instanceof Error ? error.message : "Impossible de charger la lecture DCE.",
      });
    } finally {
      if (request === readingSequence.current) setLoading(false);
    }
  }

  async function searchKnowledge() {
    const normalized = query.trim();
    if (!selectedCaseId) {
      setMessage({ tone: "warning", text: "Sélectionnez une affaire avant de rechercher dans le DCE." });
      return;
    }
    if (!normalized) {
      setMessage({ tone: "warning", text: "Saisissez un terme de recherche DCE." });
      setResults([]);
      return;
    }
    setSearching(true);
    try {
      const response = await api.searchCaseKnowledge(selectedCaseId, normalized, 5);
      setResults(response.results);
    } catch (error) {
      setResults([]);
      const apiError = error as { status?: number; detail?: string };
      const text = apiError.status === 503 || apiError.detail === "KNOWLEDGE_RETRIEVAL_UNAVAILABLE"
        ? "Assistance IA indisponible. La lecture des sources et les contrôles manuels restent disponibles."
        : error instanceof Error ? error.message : "Recherche knowledge indisponible.";
      setMessage({
        tone: "error",
        text,
      });
    } finally {
      setSearching(false);
    }
  }

  function resetSearch() {
    setQuery("");
    setResults([]);
  }

  return {
    reading,
    results,
    query,
    loading,
    searching,
    setQuery,
    loadReading,
    searchKnowledge,
    resetSearch,
  };
}
