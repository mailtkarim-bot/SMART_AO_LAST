import { useCallback, useEffect, useRef, useState } from "react";

import type { ApiClient } from "../../infrastructure/api";
import type { PricingScenario, PublishedFinancialReport, CreatePricingScenarioInput, PricingScenarioCreationReceipt, PricingScenarioStateChangeInput, PricingScenarioTransitionReceipt } from "../../shared/types";

export const scenarioParameterFields = [
  { key: "sales_adjustment_bps", label: "Ajustement ventes (points de base)", min: -5000, max: 10000 },
  { key: "cost_adjustment_bps", label: "Ajustement coûts (points de base)", min: -5000, max: 10000 },
  { key: "penalty_reserve_minor", label: "Réserve pénalités (unités mineures)", min: 0, max: Number.MAX_SAFE_INTEGER },
  { key: "retention_reserve_minor", label: "Réserve retenue (unités mineures)", min: 0, max: Number.MAX_SAFE_INTEGER },
  { key: "guarantee_reserve_minor", label: "Réserve garanties (unités mineures)", min: 0, max: Number.MAX_SAFE_INTEGER },
  { key: "floor_margin_rate_bps", label: "Marge plancher (points de base)", min: 0, max: 9999 },
  { key: "target_margin_rate_bps", label: "Marge cible (points de base)", min: 0, max: 9999 },
] as const;
type Parameter = typeof scenarioParameterFields[number]["key"];
export type ScenarioCreationForm = Record<Parameter, string> & { scenario_key: string; scenario_type: CreatePricingScenarioInput["scenario_type"]; assumptions: string };
export const initialScenarioForm: ScenarioCreationForm = { scenario_key: "", scenario_type: "BASE", assumptions: "", sales_adjustment_bps: "0", cost_adjustment_bps: "0", penalty_reserve_minor: "0", retention_reserve_minor: "0", guarantee_reserve_minor: "0", floor_margin_rate_bps: "0", target_margin_rate_bps: "0" };
type Creation = { key: string; state: "IDLE" | "SUBMITTING" | "UNKNOWN" | "REJECTED" | "CONFIRMED"; error: string | null; receipt: PricingScenarioCreationReceipt | null; scenario: PricingScenario | null; readingBack: boolean };
const emptyCreation: Creation = { key: "", state: "IDLE", error: null, receipt: null, scenario: null, readingBack: false };
type Intent = { key: string; input: CreatePricingScenarioInput; sourceRevision: number; currency: string; receipt: PricingScenarioCreationReceipt | null };

type TransitionAction = "selection" | "archive";
type Transition = { key: string; state: "IDLE" | "SUBMITTING" | "UNKNOWN" | "CONFLICT" | "REJECTED" | "CONFIRMED"; target: PricingScenario | null; action: TransitionAction; reason: string; error: string | null; receipt: PricingScenarioTransitionReceipt | null; projection: PricingScenario | null; readingBack: boolean };
const emptyTransition: Transition = { key: "", state: "IDLE", target: null, action: "selection", reason: "", error: null, receipt: null, projection: null, readingBack: false };
type TransitionIntent = { key: string; target: PricingScenario; action: TransitionAction; input: PricingScenarioStateChangeInput; receipt: PricingScenarioTransitionReceipt | null };

type Reading = {
  key: string;
  scenarios: PricingScenario[];
  loading: boolean;
  error: string | null;
};

const empty: Reading = { key: "", scenarios: [], loading: false, error: null };

export function usePricingScenarios(
  api: Pick<ApiClient, "listPricingScenarios" | "createPricingScenario" | "selectPricingScenario" | "archivePricingScenario">,
  caseId: string,
  scopeKey: string,
  publishedSource: PublishedFinancialReport | null = null,
) {
  const [reading, setReading] = useState<Reading>(empty);
  const apiRef = useRef(api);
  const requestSequence = useRef(0);
  const key = scopeKey && caseId ? JSON.stringify([scopeKey, caseId]) : "";

  useEffect(() => { apiRef.current = api; }, [api]);

  const refresh = useCallback(async () => {
    const request = ++requestSequence.current;
    if (!key) {
      setReading(empty);
      return;
    }
    setReading({ key, scenarios: [], loading: true, error: null });
    try {
      const scenarios = await apiRef.current.listPricingScenarios(caseId);
      if (!Array.isArray(scenarios) || !scenarios.every((scenario) => scenario.case_id === caseId)) {
        throw new Error("Invalid scenario projection");
      }
      if (request === requestSequence.current) {
        setReading({ key, scenarios, loading: false, error: null });
        return scenarios;
      }
    } catch {
      if (request === requestSequence.current) {
        setReading({ key, scenarios: [], loading: false, error: "Les scénarios privés sont indisponibles. Réessayez." });
      }
    }
    return null;
  }, [caseId, key]);

  useEffect(() => {
    void refresh();
    return () => {
      // This is a request counter, not a DOM ref; cleanup must invalidate its latest value.
      // eslint-disable-next-line react-hooks/exhaustive-deps
      requestSequence.current++;
    };
  }, [refresh]);

  // Mask the previous scope during render, before the new effect starts its request.
  const current = key && reading.key === key ? reading : empty;
  const source = key && publishedSource?.case_id === caseId && publishedSource.status === "PUBLISHED"
    && Number.isSafeInteger(publishedSource.aggregate_revision) && publishedSource.aggregate_revision >= 0
    ? publishedSource : null;
  const sourceReason = !source ? "UNKNOWN · relisez un rapport publié de cette Affaire."
    : source.margin_calculation?.state !== "CALCULATED" || source.margin_calculation.missing_categories.length !== 0
      ? "UNKNOWN · base publiée incomplète; création indisponible."
      : !Number.isSafeInteger(source.margin_calculation.gross_margin_rate_bps)
        ? "UNKNOWN · taux de marge source indéfini; création indisponible." : null;
  const creationKey = source && key ? JSON.stringify([key, source.report_id, source.aggregate_revision]) : "";
  const [creation, setCreation] = useState<Creation>(emptyCreation);
  const [form, setFormState] = useState({ key: "", value: initialScenarioForm });
  const intention = useRef<Intent | null>(null);
  const creationRequests = useRef(0);
  const writing = useRef<number | null>(null);
  const activeCreation = creationKey && creation.key === creationKey ? creation : emptyCreation;
  const activeForm = creationKey && form.key === creationKey ? form.value : initialScenarioForm;
  const locked = ["SUBMITTING", "UNKNOWN"].includes(activeCreation.state)
    || activeCreation.state === "CONFIRMED" && activeCreation.scenario === null;

  useEffect(() => {
    creationRequests.current++;
    writing.current = null;
    intention.current = null;
    setCreation(emptyCreation);
    setFormState({ key: creationKey, value: initialScenarioForm });
    return () => {
      // Invalidate the captured creation context, not an element reference.
      // eslint-disable-next-line react-hooks/exhaustive-deps
      creationRequests.current++;
    };
  }, [creationKey]);

  const [transitionState, setTransitionState] = useState<Transition>(emptyTransition);
  const transitionIntent = useRef<TransitionIntent | null>(null);
  const transitionSequence = useRef(0);
  const transitionWriting = useRef<number | null>(null);
  const transition = key && transitionState.key === key ? transitionState : emptyTransition;
  const transitionLocked = ["SUBMITTING", "UNKNOWN", "CONFLICT", "REJECTED"].includes(transition.state)
    || transition.state === "CONFIRMED" && transition.projection === null;

  useEffect(() => {
    transitionSequence.current++;
    transitionWriting.current = null;
    transitionIntent.current = null;
    setTransitionState(emptyTransition);
    return () => {
      // Invalidate commands captured in the former private scope.
      // eslint-disable-next-line react-hooks/exhaustive-deps
      transitionSequence.current++;
    };
  }, [key]);

  function prepareTransition(id: string, action: TransitionAction) {
    if (!key || locked || writing.current !== null || transitionLocked || transitionWriting.current !== null) return;
    const target = current.scenarios.find((item) => item.scenario_id === id);
    if (!target || !Number.isSafeInteger(target.version) || target.version < 1
      || !["DRAFT", "SELECTED"].includes(target.state) || !["selection", "archive"].includes(action)) return;
    if (action === "selection" && (target.state !== "DRAFT" || target.source_basis_state !== "DECLARED_COMPLETE"
      || !target.source_snapshot_id || !Number.isSafeInteger(target.source_snapshot_revision)
      || target.source_snapshot_revision < 0 || !target.currency_code || !Number.isSafeInteger(target.gross_margin_rate_bps))) return;
    transitionIntent.current = null;
    setTransitionState({ ...emptyTransition, key, target: { ...target }, action });
  }

  function setReason(reason: string) {
    if (!transition.target || transitionLocked || transitionWriting.current !== null || transition.state === "CONFIRMED") return;
    setTransitionState({ ...transition, reason });
  }

  async function readTransition(intent: TransitionIntent, request: number) {
    const rows = await refresh();
    if (request !== transitionSequence.current) return;
    const row = rows?.find((item) => item.scenario_id === intent.target.scenario_id);
    const valid = row && row.source_snapshot_id === intent.target.source_snapshot_id
      && row.source_snapshot_revision === intent.target.source_snapshot_revision
      && row.currency_code === intent.target.currency_code && Number.isSafeInteger(row.version)
      && row.version >= intent.receipt!.version && ["DRAFT", "SELECTED", "ARCHIVED"].includes(row.state)
      && (intent.action === "archive" ? row.state === "ARCHIVED" : row.state === "SELECTED" || row.version > intent.receipt!.version && row.state === "ARCHIVED");
    setTransitionState({ key, state: "CONFIRMED", target: intent.target, action: intent.action, reason: intent.input.reason_code,
      receipt: intent.receipt, projection: valid ? row : null, readingBack: false,
      error: valid ? null : "Reçu confirmé; projection indisponible ou discordante. Relisez le scénario." });
    if (valid) setCreation((previous) => previous.scenario?.scenario_id === row.scenario_id ? { ...previous, scenario: row } : previous);
  }

  async function submitTransition() {
    if (!key || !transition.target || locked || writing.current !== null || transitionWriting.current !== null
      || ["CONFIRMED", "CONFLICT", "REJECTED"].includes(transition.state)) return;
    let intent = transitionIntent.current;
    if (intent?.key !== key) {
      const reason = transition.reason.trim();
      if (!/^[A-Z0-9_]{2,64}$/.test(reason)) {
        setTransitionState({ ...transition, error: "Motif requis : 2 à 64 caractères A–Z, 0–9 ou underscore." }); return;
      }
      const latest = current.scenarios.find((item) => item.scenario_id === transition.target!.scenario_id);
      if (!latest || latest.version !== transition.target.version || latest.state !== transition.target.state
        || latest.source_snapshot_id !== transition.target.source_snapshot_id
        || latest.source_snapshot_revision !== transition.target.source_snapshot_revision
        || latest.source_basis_state !== transition.target.source_basis_state || latest.currency_code !== transition.target.currency_code) {
        setTransitionState({ ...transition, state: "CONFLICT", error: "REVIEW_REQUIRED · projection changée. Relisez avant une nouvelle intention." }); return;
      }
      intent = { key, target: transition.target, action: transition.action, receipt: null,
        input: { command_id: crypto.randomUUID(), idempotency_key: crypto.randomUUID(), correlation_id: crypto.randomUUID(), transition_id: crypto.randomUUID(), expected_version: transition.target.version, reason_code: reason } };
      transitionIntent.current = intent;
    }
    const request = ++transitionSequence.current;
    transitionWriting.current = request;
    setTransitionState({ ...transition, state: "SUBMITTING", error: null });
    try {
      const method = intent.action === "selection" ? "selectPricingScenario" : "archivePricingScenario";
      const receipt = await apiRef.current[method](caseId, intent.target.scenario_id, intent.input);
      if (request !== transitionSequence.current) return;
      if (receipt.status !== "SUCCEEDED" || receipt.result_code !== "PRICING_SCENARIO_TRANSITIONED"
        || receipt.command_id !== intent.input.command_id || receipt.idempotency_key !== intent.input.idempotency_key
        || receipt.scenario_id !== intent.target.scenario_id || receipt.version !== intent.input.expected_version + 1
        || !Number.isSafeInteger(receipt.version) || !Array.isArray(receipt.event_ids) || receipt.event_ids.length === 0) throw new Error("Invalid transition receipt");
      const confirmed = { ...intent, receipt };
      transitionIntent.current = confirmed;
      setTransitionState({ ...transition, state: "CONFIRMED", receipt, projection: null, error: null });
      await readTransition(confirmed, request);
    } catch (error) {
      if (request !== transitionSequence.current) return;
      const status = (error as { status?: number })?.status;
      const detail = (error as { detail?: string })?.detail;
      const conflict = status === 409 && ["VERSION_CONFLICT", "SCENARIO_ALREADY_SELECTED", "SCENARIO_ALREADY_ARCHIVED"].includes(detail ?? "");
      const rejected = [400, 401, 403, 404, 422].includes(status ?? 0);
      if (conflict || rejected) transitionIntent.current = null;
      setTransitionState({ ...transition, state: conflict ? "CONFLICT" : rejected ? "REJECTED" : "UNKNOWN", receipt: null, projection: null,
        error: conflict ? `${detail} · REVIEW_REQUIRED : relisez avant une nouvelle intention.` : rejected ? "REVIEW_REQUIRED · acte refusé. Relisez avant une nouvelle intention." : "UNKNOWN · résultat inconnu. Réessayez uniquement la même intention." });
    } finally { if (transitionWriting.current === request) transitionWriting.current = null; }
  }

  async function recoverTransition(reload: boolean) {
    if (!key || transitionWriting.current !== null || writing.current !== null) return;
    const intent = transitionIntent.current;
    if (reload ? !["CONFLICT", "REJECTED"].includes(transition.state) : !intent?.receipt || intent.key !== key) return;
    const request = ++transitionSequence.current;
    transitionWriting.current = request;
    setTransitionState({ ...transition, readingBack: true });
    try {
      if (!reload) await readTransition(intent!, request);
      else {
        const rows = await refresh();
        if (request !== transitionSequence.current) return;
        if (rows) { transitionIntent.current = null; setTransitionState({ ...emptyTransition, key, error: "Scénarios relus. Préparez une nouvelle intention depuis la version affichée." }); }
        else setTransitionState({ ...transition, readingBack: false, error: "Relecture indisponible. Aucune nouvelle intention autorisée." });
      }
    } finally { if (transitionWriting.current === request) transitionWriting.current = null; }
  }

  function setForm(value: ScenarioCreationForm) {
    if (!creationKey || locked || transitionLocked || transitionWriting.current !== null || writing.current !== null || activeCreation.state === "CONFIRMED") return;
    setFormState({ key: creationKey, value });
  }

  async function readCreated(intent: Intent, request: number) {
    const rows = await refresh();
    if (request !== creationRequests.current) return;
    const found = rows?.find((item) => item.scenario_id === intent.input.scenario_id);
    const persisted = ["penalty_reserve_minor", "retention_reserve_minor", "guarantee_reserve_minor", "floor_margin_rate_bps", "target_margin_rate_bps"] as const;
    const valid = found && found.source_snapshot_id === intent.input.source_snapshot_id
      && found.source_snapshot_revision === intent.sourceRevision && found.currency_code === intent.currency
      && found.source_basis_state === "DECLARED_COMPLETE" && found.scenario_key === intent.input.scenario_key
      && found.scenario_type === intent.input.scenario_type && Number.isSafeInteger(found.version)
      && found.version >= (intent.receipt?.version ?? 1)
      && ["DRAFT", "SELECTED", "ARCHIVED"].includes(found.state)
      && Object.keys(found.assumptions).length === Object.keys(intent.input.assumptions).length
      && Object.entries(intent.input.assumptions).every(([name, value]) => Object.hasOwn(found.assumptions, name) && found.assumptions[name] === value)
      && persisted.every((field) => found[field] === intent.input[field]);
    setCreation({ key: creationKey, state: "CONFIRMED", receipt: intent.receipt, readingBack: false,
      scenario: valid ? found : null, error: valid ? null : "Création confirmée; la projection du scénario n’a pas pu être vérifiée. Relisez-la." });
  }

  async function readBack() {
    const intent = intention.current;
    if (!creationKey || intent?.key !== creationKey || !intent.receipt || writing.current !== null) return;
    const request = ++creationRequests.current;
    writing.current = request;
    setCreation({ ...activeCreation, readingBack: true });
    try { await readCreated(intent, request); }
    finally { if (writing.current === request) writing.current = null; }
  }

  async function submit() {
    if (!creationKey || !source || sourceReason || transitionLocked || transitionWriting.current !== null || writing.current !== null || activeCreation.state === "CONFIRMED") return;
    let intent = intention.current;
    if (intent?.key !== creationKey) {
      const name = activeForm.scenario_key.trim();
      const note = activeForm.assumptions.trim();
      const numbers = {} as Record<Parameter, number>;
      let error = !name || name.length > 120 || !note || note.length > 2000
        || !["BASE", "PRUDENT", "CUSTOM"].includes(activeForm.scenario_type)
        ? "Renseignez un nom, un type et des hypothèses explicites." : null;
      for (const field of scenarioParameterFields) {
        const raw = activeForm[field.key].trim();
        const value = Number(raw);
        if (!/^-?\d+$/.test(raw) || !Number.isSafeInteger(value) || value < field.min || value > field.max) error = `${field.label} : entier dans les limites requises.`;
        numbers[field.key] = value;
      }
      if (error) { setCreation({ ...emptyCreation, key: creationKey, error }); return; }
      intent = { key: creationKey, sourceRevision: source.aggregate_revision, currency: source.currency_code, receipt: null,
        input: { command_id: crypto.randomUUID(), idempotency_key: crypto.randomUUID(), correlation_id: crypto.randomUUID(), scenario_id: crypto.randomUUID(), source_snapshot_id: source.report_id, scenario_key: name, scenario_type: activeForm.scenario_type, ...numbers,
          assumptions: { note, sales_adjustment_bps: numbers.sales_adjustment_bps, cost_adjustment_bps: numbers.cost_adjustment_bps } } };
      intention.current = intent;
    }
    const request = ++creationRequests.current;
    writing.current = request;
    setCreation({ ...emptyCreation, key: creationKey, state: "SUBMITTING" });
    try {
      const receipt = await apiRef.current.createPricingScenario(caseId, intent.input);
      if (request !== creationRequests.current) return;
      if (receipt.status !== "SUCCEEDED" || receipt.result_code !== "PRICING_SCENARIO_CREATED"
        || receipt.command_id !== intent.input.command_id || receipt.idempotency_key !== intent.input.idempotency_key
        || receipt.scenario_id !== intent.input.scenario_id || !Number.isSafeInteger(receipt.version) || receipt.version < 1) throw new Error("Invalid creation receipt");
      const confirmed = { ...intent, receipt };
      intention.current = confirmed;
      setCreation({ ...emptyCreation, key: creationKey, state: "CONFIRMED", receipt });
      await readCreated(confirmed, request);
    } catch (error) {
      if (request !== creationRequests.current) return;
      const status = (error as { status?: number })?.status;
      const detail = (error as { detail?: string })?.detail;
      const rejected = [400, 401, 403, 404, 422].includes(status ?? 0);
      if (rejected) intention.current = null;
      setCreation({ ...emptyCreation, key: creationKey, state: rejected ? "REJECTED" : "UNKNOWN",
        error: detail === "SCENARIO_SOURCE_UNKNOWN" || detail === "SCENARIO_RATE_UNKNOWN"
          ? "UNKNOWN · le serveur refuse la base ou le taux source. Aucun scénario confirmé."
          : rejected ? "Création refusée. Corrigez la saisie avant une nouvelle intention." : "Résultat UNKNOWN. Le retry conserve la source, les paramètres et les mêmes identifiants." });
    } finally { if (writing.current === request) writing.current = null; }
  }

  function reset() {
    if (locked || transitionLocked || transitionWriting.current !== null || writing.current !== null) return;
    intention.current = null;
    setCreation(emptyCreation);
    setFormState({ key: creationKey, value: initialScenarioForm });
  }
  return {
    scenarios: current.scenarios,
    loading: Boolean(key) && (reading.key !== key || current.loading),
    error: current.error,
    refresh,
    transition: { ...transition, locked: transitionLocked, prepare: prepareTransition, setReason, submit: submitTransition, readBack: () => recoverTransition(false), reload: () => recoverTransition(true) },
    creation: { ...activeCreation, source, sourceReason, form: activeForm, locked: locked || transitionLocked, setForm, submit, readBack, reset },
  };
}
