import { useCallback, useEffect, useRef, useState } from "react";

import type { ApiClient } from "../../infrastructure/api";
import type { CollaboratorTaskList, CommandReceipt, ProposeCapabilityInput } from "../../shared/types";

export type CapabilityProposalSource = {
  kind: "REQUIREMENT" | "TASK";
  id: string;
  requirementId: string;
  label: string;
  state?: string;
};

export type CapabilityProposalTask = { id: string; requirementId: string | null; title: string };

export type CapabilityProposalDraft = {
  capability_id: string;
  capability_version_id: string;
  justification: string;
} & (
  | { requirement_id: string; task_id?: never }
  | { task_id: string; requirement_id?: never }
);

export type CapabilityProposalStatus =
  | "IDLE"
  | "SUBMITTING"
  | "UNKNOWN"
  | "READING"
  | "RECEIVED"
  | "CONFLICT"
  | "REJECTED"
  | "RECEIPT_READ_FAILED"
  | "CONFLICT_READ_FAILED";

type Flow = { key: string; status: CapabilityProposalStatus; error: string | null };
type TaskReading = { key: string; tasks: CapabilityProposalTask[]; loading: boolean; error: string | null };
const emptyFlow: Flow = { key: "", status: "IDLE", error: null };
const emptyTasks: TaskReading = { key: "", tasks: [], loading: false, error: null };

function validTaskList(value: unknown, caseId: string): value is CollaboratorTaskList {
  if (!value || typeof value !== "object") return false;
  const list = value as CollaboratorTaskList;
  return list.case_id === caseId && Array.isArray(list.tasks) && list.tasks.every((task) =>
    task && task.case_id === caseId && typeof task.task_id === "string" && task.task_id.length > 0
    && (task.requirement_id === null || typeof task.requirement_id === "string") && typeof task.title === "string",
  );
}

function matchingReceipt(value: unknown, input: ProposeCapabilityInput): value is CommandReceipt {
  if (!value || typeof value !== "object") return false;
  const receipt = value as CommandReceipt;
  return receipt.status === "SUCCEEDED" && receipt.command_id === input.command_id
    && receipt.idempotency_key === input.idempotency_key && typeof receipt.result_code === "string"
    && Array.isArray(receipt.aggregate_refs) && receipt.aggregate_refs.length > 0 && Array.isArray(receipt.event_ids);
}

export type CapabilityProposalController = {
  tasks: CapabilityProposalTask[];
  taskLoading: boolean;
  taskError: string | null;
  status: CapabilityProposalStatus;
  error: string | null;
  propose: (draft: CapabilityProposalDraft) => Promise<void>;
  retry: () => Promise<void>;
  retryRead: () => Promise<void>;
  reset: () => void;
};

export function useCapabilityProposal(
  api: Pick<ApiClient, "listCollaboratorTasks" | "proposeCapability">,
  caseId: string,
  scopeKey: string,
  refreshAssessments: () => Promise<boolean>,
): CapabilityProposalController {
  const key = scopeKey && caseId ? JSON.stringify([scopeKey, caseId]) : "";
  const [flow, setFlow] = useState<Flow>(emptyFlow);
  const [taskReading, setTaskReading] = useState<TaskReading>(emptyTasks);
  const apiRef = useRef(api);
  const refreshRef = useRef(refreshAssessments);
  const taskSequence = useRef(0);
  // ponytail: retry IDs live only in the active Case/session; reload/scope changes need server reconciliation, never persisted justification.
  const intent = useRef<{ key: string; input: ProposeCapabilityInput } | null>(null);
  const postingKey = useRef("");

  useEffect(() => { apiRef.current = api; refreshRef.current = refreshAssessments; });

  useEffect(() => {
    let active = true;
    const request = ++taskSequence.current;
    if (!key) {
      setTaskReading(emptyTasks);
      return () => {
        active = false;
        if (intent.current?.key === key) intent.current = null;
        if (postingKey.current === key) postingKey.current = "";
      };
    }
    setTaskReading({ key, tasks: [], loading: true, error: null });
    void apiRef.current.listCollaboratorTasks(caseId).then((response) => {
      if (!validTaskList(response, caseId)) throw new Error("Invalid task projection");
      if (active && request === taskSequence.current) {
        setTaskReading({
          key,
          tasks: response.tasks.map((task) => ({ id: task.task_id, requirementId: task.requirement_id, title: task.title })),
          loading: false,
          error: null,
        });
      }
    }).catch(() => {
      if (active && request === taskSequence.current) setTaskReading({ key, tasks: [], loading: false, error: "Les tâches du DCE ne sont pas disponibles." });
    });
    return () => {
      active = false;
      if (intent.current?.key === key) intent.current = null;
      if (postingKey.current === key) postingKey.current = "";
    };
  }, [caseId, key]);

  const readAssessments = useCallback(async (readKey: string, kind: "RECEIPT" | "CONFLICT") => {
    setFlow({ key: readKey, status: "READING", error: null });
    try {
      const read = await refreshRef.current();
      if (readKey === key) setFlow({ key: readKey, status: read ? kind === "RECEIPT" ? "RECEIVED" : "CONFLICT" : kind === "RECEIPT" ? "RECEIPT_READ_FAILED" : "CONFLICT_READ_FAILED", error: read ? null : "La lecture des évaluations est indisponible. Réessayez uniquement cette lecture." });
    } catch {
      if (readKey === key) setFlow({ key: readKey, status: kind === "RECEIPT" ? "RECEIPT_READ_FAILED" : "CONFLICT_READ_FAILED", error: "La lecture des évaluations est indisponible. Réessayez uniquement cette lecture." });
    }
  }, [key]);

  const send = useCallback(async (input: ProposeCapabilityInput, wasUnknown: boolean) => {
    if (!key || postingKey.current === key) return;
    postingKey.current = key;
    setFlow({ key, status: "SUBMITTING", error: null });
    try {
      const receipt = await apiRef.current.proposeCapability(caseId, input);
      if (intent.current?.key !== key || intent.current.input !== input) return;
      if (!matchingReceipt(receipt, input)) {
        setFlow({ key, status: "UNKNOWN", error: "Réponse de proposition non confirmée. Réessayez la même intention." });
      } else {
        await readAssessments(key, "RECEIPT");
      }
    } catch (error) {
      if (intent.current?.key !== key || intent.current.input !== input) return;
      const status = (error as { status?: number })?.status;
      if (status === 409) await readAssessments(key, "CONFLICT");
      else if (wasUnknown || status === undefined || status >= 500) setFlow({ key, status: "UNKNOWN", error: "Résultat du POST inconnu. Seul le rejeu de cette même intention est permis." });
      else setFlow({ key, status: "REJECTED", error: status === 403 || status === 404 ? "Proposition refusée dans le périmètre autorisé." : "Proposition refusée. Relisez la source et la justification." });
    } finally {
      if (postingKey.current === key) postingKey.current = "";
    }
  }, [caseId, key, readAssessments]);

  const propose = useCallback(async (draft: CapabilityProposalDraft) => {
    if (!key || postingKey.current === key) return;
    if (flow.key === key && !["IDLE", "REJECTED"].includes(flow.status)) return;
    const justification = draft.justification.trim();
    if (!draft.capability_id || !draft.capability_version_id || !justification || justification.length > 2000) {
      setFlow({ key, status: "REJECTED", error: "Choisissez une version exacte et fournissez une justification valide." });
      return;
    }
    const sourceId = "requirement_id" in draft ? draft.requirement_id : draft.task_id;
    if (!sourceId) {
      setFlow({ key, status: "REJECTED", error: "Sélectionnez une source du DCE courant." });
      return;
    }
    const input: ProposeCapabilityInput = {
      command_id: crypto.randomUUID(),
      idempotency_key: crypto.randomUUID(),
      correlation_id: crypto.randomUUID(),
      capability_id: draft.capability_id,
      capability_version_id: draft.capability_version_id,
      justification,
      ...( "requirement_id" in draft ? { requirement_id: draft.requirement_id } : { task_id: draft.task_id }),
    };
    intent.current = { key, input };
    await send(input, false);
  }, [flow, key, send]);

  const retry = useCallback(async () => {
    const current = intent.current;
    if (!key || postingKey.current === key || flow.key !== key || flow.status !== "UNKNOWN" || current?.key !== key) return;
    await send(current.input, true);
  }, [flow, key, send]);

  const retryRead = useCallback(async () => {
    if (!key || flow.key !== key) return;
    if (flow.status === "RECEIPT_READ_FAILED") await readAssessments(key, "RECEIPT");
    else if (flow.status === "CONFLICT_READ_FAILED") await readAssessments(key, "CONFLICT");
  }, [flow, key, readAssessments]);

  const reset = useCallback(() => {
    if (flow.key !== key || !["RECEIVED", "CONFLICT", "REJECTED"].includes(flow.status)) return;
    intent.current = null;
    setFlow({ key, status: "IDLE", error: null });
  }, [flow, key]);

  const currentFlow = key && flow.key === key ? flow : { ...emptyFlow, key };
  const currentTasks = key && taskReading.key === key ? taskReading : { ...emptyTasks, key, loading: Boolean(key) };
  return {
    tasks: currentTasks.tasks,
    taskLoading: currentTasks.loading,
    taskError: currentTasks.error,
    status: currentFlow.status,
    error: currentFlow.error,
    propose,
    retry,
    retryRead,
    reset,
  };
}
