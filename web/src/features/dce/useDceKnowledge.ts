import { useLayoutEffect, useRef, useState } from "react";
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
  const [queryEntry, setQueryEntry] = useState<{ key: string; value: string } | null>(null);
  const [searchEntry, setSearchEntry] = useState<{
    key: string;
    results: KnowledgeSearchResult[];
    searching: boolean;
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const searchRequest = useRef<object | null>(null);
  const readingRequest = useRef<object | null>(null);
  const readingKey = scopeKey && selectedCaseId ? JSON.stringify([scopeKey, selectedCaseId]) : "";
  const reading = readingKey && readingEntry?.key === readingKey ? readingEntry.value : null;
  const contextKey = readingKey ? JSON.stringify([readingKey, reading?.dce.dce_version_id ?? null]) : "";
  const query = contextKey && queryEntry?.key === contextKey ? queryEntry.value : "";
  const searchKey = contextKey ? JSON.stringify([contextKey, query.trim()]) : "";
  const results = searchKey && searchEntry?.key === searchKey ? searchEntry.results : [];
  const searching = Boolean(searchKey && searchEntry?.key === searchKey && searchEntry.searching);

  useLayoutEffect(() => {
    readingRequest.current = null;
    setReadingEntry(null);
    setLoading(false);
    return () => { readingRequest.current = null; };
  }, [readingKey]);

  useLayoutEffect(() => {
    searchRequest.current = null;
    setQueryEntry(null);
    setSearchEntry(null);
    return () => { searchRequest.current = null; };
  }, [contextKey]);

  function setQuery(value: string) {
    searchRequest.current = null;
    setQueryEntry({ key: contextKey, value });
    setSearchEntry(null);
  }

  async function loadReading(caseId = selectedCaseId) {
    const request = {};
    readingRequest.current = request;
    const key = scopeKey && caseId ? JSON.stringify([scopeKey, caseId]) : "";
    if (!caseId) {
      setReadingEntry(null);
      resetSearch();
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const value = await api.getCaseDceReading(caseId);
      if (request === readingRequest.current) {
        setReadingEntry(value.case_id === caseId ? { key, value } : null);
      }
    } catch (error) {
      if (request !== readingRequest.current) return;
      setReadingEntry(null);
      if ((error as { status?: number }).status === 404) return;
      setMessage({
        tone: "error",
        text: error instanceof Error ? error.message : "Impossible de charger la lecture DCE.",
      });
    } finally {
      if (request === readingRequest.current) setLoading(false);
    }
  }

  async function searchKnowledge() {
    const normalized = query.trim();
    if (!selectedCaseId || !contextKey) {
      setMessage({ tone: "warning", text: "Sélectionnez une affaire avant de rechercher dans le DCE." });
      return;
    }
    if (!normalized) {
      setMessage({ tone: "warning", text: "Saisissez un terme de recherche DCE." });
      resetSearch();
      return;
    }
    const request = {};
    searchRequest.current = request;
    const key = searchKey;
    setSearchEntry({ key, results: [], searching: true });
    try {
      const response = await api.searchCaseKnowledge(selectedCaseId, normalized, 5);
      if (request !== searchRequest.current) return;
      if (response.case_id !== selectedCaseId || response.query !== normalized ||
          (reading && response.results.some((item) => item.dce_version_id !== reading.dce.dce_version_id))) {
        throw new Error("Résultat de recherche incompatible avec le contexte courant.");
      }
      setSearchEntry({ key, results: response.results, searching: false });
    } catch (error) {
      if (request !== searchRequest.current) return;
      setSearchEntry({ key, results: [], searching: false });
      const apiError = error as { status?: number; detail?: string };
      const text = apiError.status === 503 || apiError.detail === "KNOWLEDGE_RETRIEVAL_UNAVAILABLE"
        ? "Assistance IA indisponible. La lecture des sources et les contrôles manuels restent disponibles."
        : error instanceof Error ? error.message : "Recherche knowledge indisponible.";
      setMessage({ tone: "error", text });
    }
  }

  function resetSearch() {
    searchRequest.current = null;
    setQueryEntry(null);
    setSearchEntry(null);
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
