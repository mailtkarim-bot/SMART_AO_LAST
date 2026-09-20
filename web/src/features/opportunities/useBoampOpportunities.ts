import { useRef, useState } from "react";
import type { Dispatch, SetStateAction } from "react";

import type { ApiClient } from "../../infrastructure/api";
import type {
  BoampObservation,
  BoampSourceStatus,
  BoampCaseCreationInput,
  BoampCaseCreationResponse,
  BoampQualificationDecision,
  BoampQualificationForm,
  BoampQualificationReason,
} from "../../shared/types";

type Message = { tone: "success" | "error" | "warning"; text: string };
type SetMessage = Dispatch<SetStateAction<Message | null>>;
type CaseCreatedHandler = (result: BoampCaseCreationResponse) => Promise<void> | void;

const initialForm: BoampQualificationForm = {
  decision: "QUALIFIED",
  reason_code: "RELEVANT_PUBLIC_SIGNAL",
};

export function useBoampOpportunities(
  api: ApiClient,
  setMessage: SetMessage,
  onCaseCreated?: CaseCreatedHandler,
) {
  const [observations, setObservations] = useState<BoampObservation[]>([]);
  const [sourceStatus, setSourceStatus] = useState<BoampSourceStatus | null>(null);
  const [selectedObservationId, setSelectedObservationId] = useState("");
  const [qualificationForm, setQualificationForm] = useState(initialForm);
  const [loading, setLoading] = useState(false);
  const [qualifying, setQualifying] = useState(false);
  const [qualifiedObservationIds, setQualifiedObservationIds] = useState<ReadonlySet<string>>(
    () => new Set(),
  );
  const [creatingCase, setCreatingCase] = useState(false);
  const caseCommands = useRef(new Map<string, BoampCaseCreationInput>());

  async function refreshObservations() {
    setLoading(true);
    try {
      const result = await api.listBoampObservations();
      setObservations(result.observations);
      setSourceStatus(result.source_status ?? null);
      setQualifiedObservationIds((current) => {
        const next = new Set(current);
        for (const item of result.observations) {
          if (item.p0_state === "TARGETED") next.add(item.observation_id);
          if (item.p0_state === "SNOOZED" || item.p0_state === "DISCARDED") {
            next.delete(item.observation_id);
          }
        }
        return next;
      });
      if (
        selectedObservationId &&
        !result.observations.some((item) => item.observation_id === selectedObservationId)
      ) {
        setSelectedObservationId("");
      }
      if (!selectedObservationId && result.observations[0]) {
        setSelectedObservationId(result.observations[0].observation_id);
      }
    } catch (error) {
      setMessage({
        tone: "error",
        text: error instanceof Error ? error.message : "Impossible de charger les opportunités BOAMP.",
      });
    } finally {
      setLoading(false);
    }
  }

  function selectObservation(observationId: string) {
    setSelectedObservationId(observationId);
  }

  function setDecision(decision: BoampQualificationDecision) {
    setQualificationForm((current) => ({ ...current, decision }));
  }

  function setReason(reason_code: BoampQualificationReason) {
    setQualificationForm((current) => ({ ...current, reason_code }));
  }

  async function qualifySelected() {
    if (!selectedObservationId) {
      setMessage({ tone: "warning", text: "Sélectionnez une opportunité BOAMP avant de qualifier." });
      return;
    }
    setQualifying(true);
    try {
      const receipt = await api.qualifyBoampObservation(selectedObservationId, qualificationForm);
      setQualifiedObservationIds((current) => {
        const next = new Set(current);
        if (qualificationForm.decision === "QUALIFIED") next.add(selectedObservationId);
        else next.delete(selectedObservationId);
        return next;
      });
      setMessage({
        tone: "success",
        text: receipt.replayed ? "Qualification déjà enregistrée : rejeu idempotent." : "Qualification BOAMP enregistrée.",
      });
      await refreshObservations();
    } catch (error) {
      setMessage({
        tone: "error",
        text: error instanceof Error ? error.message : "Impossible d’enregistrer la qualification BOAMP.",
      });
    } finally {
      setQualifying(false);
    }
  }

  async function createCaseFromSelected() {
    if (!selectedObservationId) {
      setMessage({ tone: "warning", text: "Sélectionnez une opportunité BOAMP avant de créer une affaire." });
      return;
    }
    if (!qualifiedObservationIds.has(selectedObservationId)) {
      setMessage({ tone: "warning", text: "Qualifiez l’opportunité BOAMP avant de créer une affaire." });
      return;
    }
    setCreatingCase(true);
    try {
      let input = caseCommands.current.get(selectedObservationId);
      if (!input) {
        input = { command_id: crypto.randomUUID(), idempotency_key: crypto.randomUUID(), correlation_id: crypto.randomUUID() };
        caseCommands.current.set(selectedObservationId, input);
      }
      const result = await api.createCaseFromBoampObservation(selectedObservationId, input);
      await onCaseCreated?.(result);
      setMessage({
        tone: "success",
        text: result.replayed
          ? "Affaire BOAMP déjà créée : rejeu idempotent."
          : `Affaire créée depuis BOAMP. Révision ${result.version} · ${result.case_id}`,
      });
      return result;
    } catch (error) {
      setMessage({
        tone: "error",
        text: error instanceof Error ? error.message : "Impossible de créer l’affaire depuis BOAMP.",
      });
      throw error;
    } finally {
      setCreatingCase(false);
    }
  }

  return {
    observations,
    sourceStatus,
    selectedObservationId,
    qualificationForm,
    loading,
    qualifying,
    qualifiedObservationIds,
    creatingCase,
    refreshObservations,
    selectObservation,
    setDecision,
    setReason,
    qualifySelected,
    createCaseFromSelected,
  };
}
