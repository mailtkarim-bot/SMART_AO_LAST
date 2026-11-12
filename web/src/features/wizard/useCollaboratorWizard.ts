import { useState, useRef, useLayoutEffect } from "react";
import type { Dispatch, SetStateAction } from "react";

import type { ApiClient } from "../../infrastructure/api";
import type {
  CollaboratorTask,
  CollaboratorTaskWorkflow,
  CreateInformationRequestInput,
  DeclareTaskBlockerInput,
  RecordInformationResponseInput,
  ResolveTaskBlockerInput,
  PreparationPackage,
  ResponseContribution,
  CaseDceReading,
  CapabilityAssessments,
  CapabilityCandidate,
  CreatePreparationResponsePlanInput,
  CreatePreparationSnapshotInput,
  SelectedResponseDraft,
  SelectedResponseAnnex,
  CommandReceipt,
  CreateTechnicalResponseDraftInput,
  PreparationResponsePlan,
  PreparationResponsePlanSection,
  TransmitPreparationSnapshotInput,
} from "../../shared/types";

type Message = { tone: "success" | "error" | "warning"; text: string };
type SetMessage = Dispatch<SetStateAction<Message | null>>;
type WizardOutcome = "RECORDED" | "NOT_APPLICABLE" | "UNABLE_TO_COMPLETE";
type WizardSnapshotReceipt = { snapshot_id: string; receipt: CommandReceipt };
type WizardTransmissionReceipt = {
  snapshot_id: string;
  transmission_id: string;
  receipt: CommandReceipt;
};
type ActionOwner = string | object;
type ScopedAction<I, R> = { intent: I | null; receipt: R | null; busy: boolean };
type ActionScopes<I, R> = ReadonlyMap<ActionOwner, ReadonlyMap<string, ScopedAction<I, R>>>;
function putScopedAction<I, R>(states: ActionScopes<I, R>, owner: ActionOwner, key: string, patch: Partial<ScopedAction<I, R>>) {
  const scopes = new Map(states.get(owner));
  scopes.set(key, {intent:null,receipt:null,busy:false,...scopes.get(key),...patch});
  return new Map(states).set(owner, scopes);
}

export type ResponsePlanItemDraft = {
  requirement_id: string;
  section_code: PreparationResponsePlanSection | "";
  source_proposal_id: string | null;
};
export type WizardResponsePlan = {
  loading: boolean;
  readState: "UNREAD" | "READY" | "ERROR";
  requestState: "IDLE" | "SUBMITTING" | "UNKNOWN" | "READING" | "CONFLICT" | "ERROR";
  draftRequestState: "IDLE" | "SUBMITTING" | "UNKNOWN" | "SOURCE_UNKNOWN" | "CONFLICT" | "RECEIVED" | "ERROR";
  error: string | null;
  requirements: CaseDceReading["requirements"];
  proposals: CapabilityAssessments["proposals"];
  candidates: CapabilityCandidate[];
  items: ResponsePlanItemDraft[];
  planId: string | null;
  hasPriorDcePlan: boolean;
  exactPlan: PreparationResponsePlan | null;
  draftedPlanVersion: number | null;
};

const emptyResponsePlan: WizardResponsePlan = {
  loading: false,
  readState: "UNREAD",
  requestState: "IDLE",
  draftRequestState: "IDLE",
  error: null,
  requirements: [],
  proposals: [],
  candidates: [],
  items: [],
  planId: null,
  hasPriorDcePlan: false,
  exactPlan: null,
  draftedPlanVersion: null,
};

function newCommandIds() {
  return { command_id: crypto.randomUUID(), idempotency_key: crypto.randomUUID(), correlation_id: crypto.randomUUID() };
}

function isDefinitiveClientError(error: unknown): boolean {
  if (!(error instanceof Error)) return false;
  const {status,detail} = error as Error & {status?:number;detail?:string};
  // Timeout, throttling and unqualified conflicts cannot prove that the command had no effect.
  return [400,401,403,404,405,422].includes(status ?? 0)
    || (status === 409 && detail === "VERSION_CONFLICT");
}

function responsePlanMatchesDraft(plan: PreparationResponsePlan, items: ResponsePlanItemDraft[]) {
  return plan.content.items.length === items.length && items.every((draft) => plan.content.items.some((item) =>
    item.requirement_id === draft.requirement_id
      && item.section_code === draft.section_code
      && item.source_proposal_id === draft.source_proposal_id,
  ));
}

export function useCollaboratorWizard(api: ApiClient, setMessage: SetMessage, contributionOwnerKey = "") {
  const [wizardCaseId, setWizardCaseId] = useState("");
  const [wizardPackageId, setWizardPackageId] = useState("");
  const [wizardPackage, setWizardPackage] = useState<PreparationPackage | null>(null);
  const [wizardTasks, setWizardTasks] = useState<CollaboratorTask[]>([]);
  const [wizardTaskId, setWizardTaskId] = useState("");
  const [wizardResultText, setWizardResultText] = useState("");
  const [wizardOutcome, setWizardOutcome] = useState<WizardOutcome>("RECORDED");
  const [wizardSnapshotId, setWizardSnapshotId] = useState("");
  const [wizardTransmissionId, setWizardTransmissionId] = useState("");
  const [wizardPreviewDocumentId, setWizardPreviewDocumentId] = useState<string | null>(null);
  const [wizardPreviewContent, setWizardPreviewContent] = useState<string | null>(null);
  const [wizardDocumentBusy, setWizardDocumentBusy] = useState(false);
  const [wizardDocumentKind, setWizardDocumentKind] = useState<"TECHNICAL_RESPONSE" | "DC1" | "DC2" | "DC4">("TECHNICAL_RESPONSE");
  const [wizardResponsePlan, setWizardResponsePlan] = useState<WizardResponsePlan>(emptyResponsePlan);
  const [pendingResponsePlanIntent, setPendingResponsePlanIntent] = useState<CreatePreparationResponsePlanInput | null>(null);
  const [pendingDraftIntent, setPendingDraftIntent] = useState<CreateTechnicalResponseDraftInput | null>(null);
  const [wizardTaskWorkflow, setWizardTaskWorkflow] = useState<CollaboratorTaskWorkflow | null>(null);

  const actionOwner = contributionOwnerKey || api.createPreparationSnapshot;
  const actionKey = JSON.stringify([wizardCaseId.trim(),wizardPackageId.trim()]);
  const [wizardPackageOwner, setWizardPackageOwner] = useState<ActionOwner | null>(null);
  const wizardContextCurrent = wizardPackageOwner === actionOwner && wizardPackage?.case_id === wizardCaseId.trim() && wizardPackage?.package_id === wizardPackageId.trim();
  const latestActionScope = useRef({owner:actionOwner,key:actionKey});
  useLayoutEffect(()=>{latestActionScope.current={owner:actionOwner,key:actionKey};});
  const wizardReadSequence = useRef(0);
  const [snapshotScopes, setSnapshotScopes] = useState<ActionScopes<CreatePreparationSnapshotInput, WizardSnapshotReceipt>>(new Map());
  const [transmissionScopes, setTransmissionScopes] = useState<ActionScopes<TransmitPreparationSnapshotInput, WizardTransmissionReceipt>>(new Map());
  const snapshotAction = snapshotScopes.get(actionOwner)?.get(actionKey);
  const transmissionAction = transmissionScopes.get(actionOwner)?.get(actionKey);
  const pendingSnapshotIntent = snapshotAction?.intent ?? null;
  const pendingTransmissionIntent = transmissionAction?.intent ?? null;
  const wizardSnapshotReceipt = snapshotAction?.receipt ?? null;
  const wizardTransmissionReceipt = transmissionAction?.receipt ?? null;
  const wizardSnapshotBusy = snapshotAction?.busy ?? false;
  const wizardTransmissionBusy = transmissionAction?.busy ?? false;
  function setPendingSnapshotIntent(intent: CreatePreparationSnapshotInput | null) {setSnapshotScopes(states=>putScopedAction(states,actionOwner,actionKey,{intent}));}
  function setPendingTransmissionIntent(intent: TransmitPreparationSnapshotInput | null) {setTransmissionScopes(states=>putScopedAction(states,actionOwner,actionKey,{intent}));}
  function setWizardSnapshotReceipt(receipt: WizardSnapshotReceipt | null) {setSnapshotScopes(states=>putScopedAction(states,actionOwner,actionKey,{receipt}));}
  function setWizardTransmissionReceipt(receipt: WizardTransmissionReceipt | null) {setTransmissionScopes(states=>putScopedAction(states,actionOwner,actionKey,{receipt}));}
  function setWizardSnapshotBusy(busy: boolean) {setSnapshotScopes(states=>putScopedAction(states,actionOwner,actionKey,{busy}));}
  function setWizardTransmissionBusy(busy: boolean) {setTransmissionScopes(states=>putScopedAction(states,actionOwner,actionKey,{busy}));}
  const hasAction = Boolean(pendingSnapshotIntent || pendingTransmissionIntent || wizardSnapshotReceipt || wizardTransmissionReceipt);
  const previousActionScope = useRef({owner:actionOwner,key:actionKey,hasAction});
  useLayoutEffect(()=>{
    const previous=previousActionScope.current;
    if((previous.owner!==actionOwner || previous.key!==actionKey) && (previous.hasAction || hasAction)) {
      setWizardSnapshotId(pendingSnapshotIntent?.snapshot_id ?? wizardSnapshotReceipt?.snapshot_id ?? pendingTransmissionIntent?.snapshot_id ?? wizardTransmissionReceipt?.snapshot_id ?? "");
      setWizardTransmissionId(pendingTransmissionIntent?.transmission_id ?? wizardTransmissionReceipt?.transmission_id ?? "");
    }
    previousActionScope.current={owner:actionOwner,key:actionKey,hasAction};
  },[actionOwner,actionKey,hasAction,pendingSnapshotIntent,pendingTransmissionIntent,wizardSnapshotReceipt,wizardTransmissionReceipt]);

  const currentDraftScope = { owner: contributionOwnerKey, post: api.createTechnicalResponseDraft, caseId: wizardCaseId.trim(), packageId: wizardPackageId.trim(), loadedPackageId: wizardPackage?.package_id, dceVersion: wizardPackage?.dce_version_id, planVersion: wizardResponsePlan.exactPlan?.version };
  const latestDraftScope = useRef(currentDraftScope);
  useLayoutEffect(() => { latestDraftScope.current = currentDraftScope; });
  const [pendingDraftScope, setPendingDraftScope] = useState<(typeof currentDraftScope & { uncertain?: boolean }) | null>(null);
  function sameDraftScope(expected: typeof currentDraftScope | null, current: typeof currentDraftScope, includePlan = true) {
    return expected !== null && expected.owner === current.owner && (expected.owner !== "" || expected.post === current.post) && expected.caseId === current.caseId && expected.packageId === current.packageId && expected.loadedPackageId === current.loadedPackageId && expected.dceVersion === current.dceVersion && (!includePlan || expected.planVersion === current.planVersion);
  }
  function draftScopeMatches(expected: typeof currentDraftScope | null, includePlan = true) {
    return sameDraftScope(expected, latestDraftScope.current, includePlan);
  }


  function markPendingDraftUncertain(expected: typeof currentDraftScope | null) {
    setPendingDraftScope((previous) => previous && expected && sameDraftScope(previous, expected)
      ? { ...previous, uncertain: true }
      : previous);
  }
  const pendingDraftUncertainHere = Boolean(pendingDraftIntent && pendingDraftScope?.uncertain && sameDraftScope(pendingDraftScope, currentDraftScope));

  const responsePlanReadSequence = useRef(0);
  async function loadWizardResponsePlan(packageProjection: PreparationPackage, isCurrent = () => true): Promise<boolean> {
    if (!isCurrent()) return false;
    const sequence = ++responsePlanReadSequence.current;
    const currentRead = () => isCurrent() && sequence === responsePlanReadSequence.current;
    setWizardResponsePlan((current) => ({ ...current, loading: true, readState: "UNREAD", exactPlan: null, error: null }));
    try {
      const [dce, assessment, candidates, planList] = await Promise.all([
        api.getCaseDceReading(packageProjection.case_id),
        api.getCapabilityAssessments(packageProjection.case_id),
        api.getCapabilityCandidates(packageProjection.case_id),
        api.getPreparationResponsePlans(packageProjection.package_id),
      ]);
      if (!currentRead()) return false;
      if (dce.case_id !== packageProjection.case_id
        || dce.dce.dce_version_id !== packageProjection.dce_version_id
        || dce.dce_freshness !== "CURRENT"
        || dce.dce.lifecycle !== "ADMITTED"
        || dce.dce.integrity !== "VERIFIED") {
        throw new Error("DCE_VERSION_CONFLICT");
      }
      if (planList.package_id !== packageProjection.package_id || !Array.isArray(planList.plans)) {
        throw new Error("INVALID_RESPONSE_PLAN_PROJECTION");
      }
      const requirementIds = dce.requirements.map((item) => item.requirement_id);
      if (new Set(requirementIds).size !== requirementIds.length) throw new Error("DUPLICATE_DCE_REQUIREMENT");
      if (planList.plans.some((plan) => plan.package_id !== packageProjection.package_id)) throw new Error("RESPONSE_PLAN_PACKAGE_MISMATCH");
      const planIds = new Set(planList.plans.map((plan) => plan.plan_id));
      if (planIds.size > 1) throw new Error("MULTIPLE_RESPONSE_PLANS");
      const latestPlan = [...planList.plans].sort((left, right) => right.version - left.version)[0] ?? null;
      const exactPlan = latestPlan?.dce_version_id === packageProjection.dce_version_id ? latestPlan : null;
      const planItems = exactPlan?.content.items ?? [];
      if (planItems.some((item) => !requirementIds.includes(item.requirement_id)) || new Set(planItems.map((item) => item.requirement_id)).size !== planItems.length) {
        throw new Error("RESPONSE_PLAN_REQUIREMENT_MISMATCH");
      }
      const byRequirement = new Map(planItems.map((item) => [item.requirement_id, item]));
      const items = dce.requirements.map((requirement): ResponsePlanItemDraft => {
        const existing = byRequirement.get(requirement.requirement_id);
        return {
          requirement_id: requirement.requirement_id,
          section_code: existing?.section_code ?? "",
          source_proposal_id: existing?.source_proposal_id ?? null,
        };
      });
      const proposals = assessment.proposals.filter((proposal) =>
        proposal.case_id === packageProjection.case_id
          && proposal.assignment_id === packageProjection.assignment_id
          && proposal.requirement_id !== null
          && proposal.task_id === null,
      );
      setWizardResponsePlan((current) => ({
        ...current,
        loading: false,
        readState: "READY",
        requestState: pendingResponsePlanIntent ? current.requestState : "IDLE",
        requirements: dce.requirements,
        proposals,
        candidates,
        items,
        planId: latestPlan?.plan_id ?? null,
        hasPriorDcePlan: Boolean(latestPlan && !exactPlan),
        exactPlan,
        error: null,
      }));
      return true;
    } catch {
      if (!currentRead()) return false;
      setWizardResponsePlan((current) => ({
        ...current,
        loading: false,
        readState: "ERROR",
        exactPlan: null,
        error: "Le plan ou ses sources ne sont pas disponibles dans le périmètre DCE courant. Le brouillon reste verrouillé.",
      }));
      return false;
    }
  }

  async function loadCollaboratorWizard(notify = true) {
    if (!wizardPackageId.trim() || !wizardCaseId.trim()) {
      setMessage({ tone: "error", text: "Renseignez l’affaire et le package de préparation collaborateur." });
      return;
    }
    const sequence=++wizardReadSequence.current;
    const owner=actionOwner, key=actionKey;
    const isCurrent=()=>latestActionScope.current.owner===owner && latestActionScope.current.key===key && sequence===wizardReadSequence.current;
    try {
      const [packageResult, taskResult] = await Promise.all([
        api.getCollaboratorPreparation(wizardPackageId.trim()),
        api.listCollaboratorTasks(wizardCaseId.trim()),
      ]);
      if(!isCurrent())return;
      if (packageResult.case_id !== wizardCaseId.trim() || taskResult.case_id !== packageResult.case_id) {
        throw new Error("L’affaire et le package de préparation ne correspondent pas.");
      }
      setWizardPackage(packageResult);
      setWizardPackageOwner(() => owner);
      setWizardTasks(taskResult.tasks);
      await loadWizardResponsePlan(packageResult,isCurrent);
      if(!isCurrent())return;
      if (!wizardTaskId && taskResult.tasks[0]) setWizardTaskId(taskResult.tasks[0].task_id);
      if (notify) {
        setMessage({ tone: "success", text: "Wizard collaborateur chargé depuis les projections serveur." });
      }
    } catch (error) {
      if(!isCurrent())return;
      setWizardPackage(null);
      setWizardTasks([]);
      if (notify) {
        setMessage({
          tone: "error",
          text: error instanceof Error ? error.message : "Impossible de charger le wizard collaborateur.",
        });
      }
    }
  }

  async function refreshCollaboratorWizard() {
    if (wizardPackageId.trim() && wizardCaseId.trim()) await loadCollaboratorWizard(false);
  }

  async function evaluateWizardReadiness() {
    if (!wizardPackage) return;
    try {
      await api.evaluatePreparationReadiness(wizardPackage.case_id, {
        package_id: wizardPackage.package_id,
        assignment_id: wizardPackage.assignment_id,
        dce_version_id: wizardPackage.dce_version_id,
        expected_revision: wizardPackage.aggregate_revision,
      });
      setMessage({ tone: "success", text: "Complétude recalculée. Les blocages restent opposables au serveur." });
      await refreshCollaboratorWizard();
    } catch (error) {
      setMessage({
        tone: "error",
        text: error instanceof Error ? error.message : "La vérification de complétude a échoué.",
      });
    }
  }

  async function generateWizardDocument() {
    if (!wizardPackage?.latest_readiness) return;
    try {
      await api.generateTechnicalDocument(wizardPackage.package_id, {
        expected_revision: wizardPackage.aggregate_revision,
        readiness_revision: wizardPackage.latest_readiness.revision,
        document_kind: wizardDocumentKind,
      });
      setMessage({ tone: "success", text: "Génération documentaire demandée avec contrôle de complétude." });
      await refreshCollaboratorWizard();
    } catch (error) {
      setMessage({
        tone: "error",
        text: error instanceof Error ? error.message : "La génération documentaire a échoué.",
      });
    }
  }

  function setWizardResponsePlanItem(requirementId: string, patch: Partial<ResponsePlanItemDraft>) {
    if (pendingResponsePlanIntent || (pendingDraftIntent && wizardResponsePlan.draftRequestState !== "SOURCE_UNKNOWN")) return;
    if (pendingDraftIntent) setPendingDraftIntent(null);
    setWizardResponsePlan((current) => ({
      ...current,
      items: current.items.map((item) => item.requirement_id === requirementId ? { ...item, ...patch } : item),
      requestState: pendingResponsePlanIntent ? current.requestState : "IDLE",
    }));
  }

  function responsePlanHasFullCoverage(items = wizardResponsePlan.items) {
    const requirementIds = wizardResponsePlan.requirements.map((item) => item.requirement_id);
    return requirementIds.length > 0
      && requirementIds.length <= 64
      && items.length === requirementIds.length
      && items.every((item) => requirementIds.includes(item.requirement_id) && item.section_code !== "")
      && new Set(items.map((item) => item.requirement_id)).size === requirementIds.length;
  }

  function responsePlanHasCurrentSources(plan = wizardResponsePlan.exactPlan) {
    if (!plan || plan.state !== "SOURCES_CURRENT") return false;
    return plan.content.items.every((item) => {
      if (!item.source_proposal_id || item.source_validity_state !== "CURRENT" || item.source_evidence_state !== "CURRENT") return false;
      const proposal = wizardResponsePlan.proposals.find((candidate) =>
        candidate.proposal_id === item.source_proposal_id
          && candidate.case_id === plan.content.case_id
          && candidate.assignment_id === wizardPackage?.assignment_id
          && candidate.requirement_id === item.requirement_id
          && candidate.task_id === null
          && candidate.validity_state === "CURRENT"
          && candidate.source_evidence_state === "CURRENT",
      );
      return Boolean(proposal && wizardResponsePlan.candidates.some((candidate) =>
        candidate.capability_id === proposal.capability_id
          && candidate.version_id === item.source_capability_version_id
          && candidate.validity_state === "CURRENT"
          && candidate.source_evidence_state === "CURRENT",
      ));
    });
  }

  function canSaveWizardResponsePlan() {
    const savedSelectionMatches = wizardResponsePlan.exactPlan
      ? responsePlanMatchesDraft(wizardResponsePlan.exactPlan, wizardResponsePlan.items)
      : false;
    const sourceSelectionsValid = wizardResponsePlan.items.every((item) => {
      if (!item.source_proposal_id) return true;
      const proposal = wizardResponsePlan.proposals.find((candidate) => candidate.proposal_id === item.source_proposal_id);
      return Boolean(proposal
        && proposal.requirement_id === item.requirement_id
        && proposal.task_id === null
        && proposal.case_id === wizardPackage?.case_id
        && proposal.assignment_id === wizardPackage?.assignment_id
        && proposal.validity_state !== "EXPIRED"
        && proposal.source_evidence_state !== "EXPIRED"
        && wizardResponsePlan.candidates.some((candidate) =>
          candidate.capability_id === proposal.capability_id
            && candidate.version_id === proposal.capability_version_id
            && candidate.validity_state !== "EXPIRED"
            && candidate.source_evidence_state !== "EXPIRED",
        ));
    });
    return Boolean(
      wizardPackage
        && wizardCaseId.trim() === wizardPackage.case_id
        && wizardPackageId.trim() === wizardPackage.package_id
        && wizardResponsePlan.readState === "READY"
        && !wizardResponsePlan.loading
        && wizardResponsePlan.requestState === "IDLE"
        && !pendingResponsePlanIntent
        && !pendingDraftIntent
        && responsePlanHasFullCoverage()
        && sourceSelectionsValid
        && !savedSelectionMatches,
    );
  }

  function isWizardResponsePlanCurrent() {
    const plan = wizardResponsePlan.exactPlan;
    return Boolean(
      wizardPackage
        && wizardCaseId.trim() === wizardPackage.case_id
        && wizardPackageId.trim() === wizardPackage.package_id
        && wizardResponsePlan.readState === "READY"
        && !wizardResponsePlan.loading
        && wizardResponsePlan.requestState === "IDLE"
        && plan
        && plan.package_id === wizardPackage.package_id
        && plan.dce_version_id === wizardPackage.dce_version_id
        && plan.state === "SOURCES_CURRENT"
        && responsePlanHasFullCoverage()
        && responsePlanMatchesDraft(plan, wizardResponsePlan.items)
        && responsePlanHasCurrentSources(plan),
    );
  }

  function canCreateWizardResponseDraft() {
    const plan = wizardResponsePlan.exactPlan;
    return Boolean(
      wizardPackage
        && plan
        && isWizardResponsePlanCurrent()
        && wizardPackage.generated_documents.some((document) => document.document_kind === "TECHNICAL_RESPONSE")
        && wizardResponsePlan.draftRequestState !== "CONFLICT"
        && wizardResponsePlan.draftRequestState !== "SOURCE_UNKNOWN"
        && wizardResponsePlan.draftRequestState !== "ERROR"
        && wizardResponsePlan.draftedPlanVersion !== plan.version
        && !pendingDraftIntent,
    );
  }

  async function refreshPreparationAfterCommand(isCurrent = () => true): Promise<boolean> {
    if (!wizardPackage || !isCurrent()) return false;
    const packageResult = await api.getCollaboratorPreparation(wizardPackage.package_id);
    if (!isCurrent()) return false;
    if (packageResult.case_id !== wizardPackage.case_id || packageResult.dce_version_id !== wizardPackage.dce_version_id) {
      throw new Error("VERSION_CONFLICT");
    }
    setWizardPackage(packageResult);
    setWizardPackageOwner(() => actionOwner);
    return loadWizardResponsePlan(packageResult, isCurrent);
  }

  async function submitWizardResponsePlan(intent: CreatePreparationResponsePlanInput) {
    if (!wizardPackage) return;
    const previousPlanVersion = wizardResponsePlan.exactPlan?.version ?? null;
    setWizardResponsePlan((current) => ({ ...current, requestState: "SUBMITTING", error: null }));
    try {
      await api.createPreparationResponsePlan(wizardPackage.package_id, intent);
    } catch (error) {
      const status = (error as { status?: number }).status;
      if (status === 409) {
        setPendingResponsePlanIntent(null);
        setWizardResponsePlan((current) => ({ ...current, requestState: "CONFLICT", exactPlan: null }));
        const readback = await refreshPreparationAfterCommand().catch(() => false);
        setWizardResponsePlan((current) => ({ ...current, requestState: readback ? "CONFLICT" : "ERROR", ...(readback ? {} : { error: "Le conflit est détecté, mais le plan n’a pas pu être relu. Aucun nouvel enregistrement n’a été envoyé." }) }));
        setMessage({ tone: "warning", text: readback ? "Conflit de révision : le plan a été relu. Vérifiez les correspondances avant toute nouvelle intention." : "Conflit détecté, lecture du plan indisponible. Aucun nouvel enregistrement n’a été envoyé." });
      } else if (status === undefined || status >= 500) {
        setWizardResponsePlan((current) => ({ ...current, requestState: "UNKNOWN", exactPlan: null, error: "Résultat incertain. Réessayez la même intention; le brouillon reste verrouillé." }));
        setMessage({ tone: "warning", text: "Résultat incertain : réessayez le même enregistrement. Aucun nouvel identifiant ne sera créé." });
      } else {
        setPendingResponsePlanIntent(null);
        setWizardResponsePlan((current) => ({ ...current, requestState: "ERROR", error: "Le serveur a refusé ce plan. Vérifiez les exigences et les sources avant de réessayer." }));
        setMessage({ tone: "error", text: "Le plan n’a pas été accepté par le serveur." });
      }
      return;
    }
    setPendingResponsePlanIntent(null);
    setWizardResponsePlan((current) => ({ ...current, requestState: "READING", exactPlan: null }));
    const readback = await refreshPreparationAfterCommand().catch(() => false);
    if (!readback) {
      setWizardResponsePlan((current) => ({ ...current, requestState: "ERROR", exactPlan: null, error: "Le reçu est obtenu, mais la relecture du plan est indisponible. Seule une nouvelle lecture est autorisée." }));
      setMessage({ tone: "warning", text: "Plan enregistré; relecture indisponible. Relisez le plan avant toute nouvelle action." });
      return;
    }
    setWizardResponsePlan((current) => ({
      ...current,
      requestState: "IDLE",
      draftRequestState:
        current.draftRequestState === "SOURCE_UNKNOWN"
          && current.exactPlan?.version !== previousPlanVersion
          ? "IDLE"
          : current.draftRequestState,
    }));
    setMessage({ tone: "success", text: "Plan enregistré puis relu depuis le serveur. Son état reste opposable au brouillon." });
  }

  async function createWizardResponsePlan() {
    if (!wizardPackage || !canSaveWizardResponsePlan()) return;
    const items = wizardResponsePlan.items
      .map((item) => ({ requirement_id: item.requirement_id, section_code: item.section_code as PreparationResponsePlanSection, source_proposal_id: item.source_proposal_id }))
      .sort((left, right) => left.requirement_id.localeCompare(right.requirement_id));
    const intent: CreatePreparationResponsePlanInput = {
      ...newCommandIds(),
      plan_id: wizardResponsePlan.exactPlan?.plan_id ?? wizardResponsePlan.planId ?? crypto.randomUUID(),
      expected_package_revision: wizardPackage.aggregate_revision,
      items,
    };
    setPendingResponsePlanIntent(intent);
    await submitWizardResponsePlan(intent);
  }

  async function retryWizardResponsePlan() {
    if (!pendingResponsePlanIntent) return;
    await submitWizardResponsePlan(pendingResponsePlanIntent);
  }

  async function readWizardResponsePlan() {
    if (!wizardPackage) return;
    setWizardResponsePlan((current) => ({ ...current, requestState: "READING", error: null }));
    const read = await loadWizardResponsePlan(wizardPackage);
    if (read) {
      setWizardResponsePlan((current) => ({
        ...current,
        requestState: "IDLE",
        draftRequestState: current.draftRequestState === "CONFLICT" || current.draftRequestState === "ERROR" ? "IDLE" : current.draftRequestState,
      }));
    }
  }

  async function submitWizardDraft(intent: CreateTechnicalResponseDraftInput, expectedScope = pendingDraftScope) {
    if (!wizardPackage || !draftScopeMatches(expectedScope)) return;
    setPendingDraftScope((previous) => previous && expectedScope && sameDraftScope(previous, expectedScope) ? { ...previous, uncertain: false } : previous);
    setWizardResponsePlan((current) => ({ ...current, draftRequestState: "SUBMITTING", error: null }));
    try {
      await api.createTechnicalResponseDraft(wizardPackage.package_id, intent);
    } catch (error) {
      if (!draftScopeMatches(expectedScope)) { markPendingDraftUncertain(expectedScope); return; }
      const status = (error as { status?: number }).status;
      const detail = (error as { detail?: string }).detail;
      if (status === 409) {
        setPendingDraftIntent(null);
        const readback = await refreshPreparationAfterCommand(() => draftScopeMatches(expectedScope, false)).catch(() => false);
        if (!draftScopeMatches(expectedScope, false)) return;
        setWizardResponsePlan((current) => ({ ...current, draftRequestState: "CONFLICT", ...(readback ? {} : { readState: "ERROR", exactPlan: null, error: "Le conflit est détecté, mais le plan n’a pas pu être relu." }) }));
        setMessage({ tone: "warning", text: readback ? "Conflit de révision : le plan a été relu. Vérifiez-le avant une nouvelle action." : "Conflit détecté, lecture du plan indisponible." });
      } else if (status === undefined || status >= 500) {
        setWizardResponsePlan((current) => ({ ...current, draftRequestState: "UNKNOWN", error: "Résultat incertain. Réessayez la même intention; le serveur conserve le contrôle du plan." }));
        setMessage({ tone: "warning", text: "Résultat incertain : réessayez le même brouillon sans créer de nouvelle intention." });
      } else if (status === 422 && (detail === "RESPONSE_PLAN_UNKNOWN" || detail === "CONTRIBUTION_SOURCE_UNKNOWN")) {
        setWizardResponsePlan((current) => ({ ...current, draftRequestState: "SOURCE_UNKNOWN", error: "Une pièce source est indisponible ou son SHA-256 relu ne concorde pas avec le manifeste privé. UNKNOWN est conservé; aucun brouillon n’a été créé." }));
        setMessage({ tone: "warning", text: "Source UNKNOWN : aucune pièce n’a été réutilisée et aucun brouillon n’a été créé." });
      } else {
        setPendingDraftIntent(null);
        setWizardResponsePlan((current) => ({ ...current, draftRequestState: "ERROR", error: "Le serveur a refusé le brouillon. Le plan n’a pas été promu." }));
        setMessage({ tone: "error", text: "Le brouillon n’a pas été accepté par le serveur." });
      }
      return;
    }
    if (!draftScopeMatches(expectedScope)) { markPendingDraftUncertain(expectedScope); return; }
    setPendingDraftScope(null);
    setPendingDraftIntent(null);
    setWizardResponsePlan((current) => ({ ...current, draftRequestState: "RECEIVED", draftedPlanVersion: current.exactPlan?.version ?? null }));
    const readback = await refreshPreparationAfterCommand(() => draftScopeMatches(expectedScope, false)).catch(() => false);
    if (!draftScopeMatches(expectedScope, false)) return;
    setMessage({
      tone: readback ? "success" : "warning",
      text: readback ? "Brouillon de réponse créé depuis le plan exact relu." : "Reçu de création obtenu; le plan ne peut pas être relu pour l’instant.",
    });
  }

  async function createWizardResponseDraft(contributions?: ResponseContribution[]) {
    if (!wizardPackage || !canCreateWizardResponseDraft()) return;
    const plan = wizardResponsePlan.exactPlan;
    const document = [...wizardPackage.generated_documents]
      .filter((item) => item.document_kind === "TECHNICAL_RESPONSE")
      .sort((left, right) => right.version - left.version)[0];
    if (!plan || !document) return;
    const intent: CreateTechnicalResponseDraftInput = {
      ...newCommandIds(),
      draft_id: crypto.randomUUID(),
      ...(contributions ? { contributions: structuredClone(contributions) } : {}),
      expected_package_revision: wizardPackage.aggregate_revision,
      source_document_id: document.document_id,
      section_codes: [...new Set(plan.content.items.map((item) => item.section_code))].sort(),
      source_refs: [...new Set(plan.content.items.map((item) => item.source_proposal_id).filter((value): value is string => value !== null))].sort(),
    };
    setPendingDraftScope(currentDraftScope);
    setPendingDraftIntent(intent);
    await submitWizardDraft(intent, currentDraftScope);
  }

  async function retryWizardResponseDraft() {
    if (!pendingDraftIntent) return;
    await submitWizardDraft(pendingDraftIntent);
  }

  async function loadWizardTaskWorkflow(taskId = wizardTaskId) {
    if (!taskId) return;
    try {
      setWizardTaskWorkflow(await api.getCollaboratorTaskWorkflow(taskId));
    } catch (error) {
      setMessage({ tone: "error", text: error instanceof Error ? error.message : "Impossible de charger le workflow." });
    }
  }

  async function createWizardInformationRequest(input: CreateInformationRequestInput) {
    if (!wizardTaskId) return;
    try {
      await api.createInformationRequest(wizardTaskId, input);
      await loadWizardTaskWorkflow();
      setMessage({ tone: "success", text: "Demande d’information créée." });
    } catch (error) {
      setMessage({ tone: "error", text: error instanceof Error ? error.message : "Impossible de créer la demande." });
    }
  }

  async function recordWizardInformationResponse(requestId: string, input: RecordInformationResponseInput) {
    try {
      await api.recordInformationResponse(requestId, input);
      await loadWizardTaskWorkflow();
      setMessage({ tone: "success", text: "Réponse à la demande enregistrée." });
    } catch (error) {
      setMessage({ tone: "error", text: error instanceof Error ? error.message : "Impossible d’enregistrer la réponse." });
    }
  }

  async function declareWizardTaskBlocker(input: DeclareTaskBlockerInput) {
    if (!wizardTaskId) return;
    try {
      await api.declareTaskBlocker(wizardTaskId, input);
      await loadWizardTaskWorkflow();
      await refreshCollaboratorWizard();
      setMessage({ tone: "success", text: "Bloqueur déclaré et opposable." });
    } catch (error) {
      setMessage({ tone: "error", text: error instanceof Error ? error.message : "Impossible de déclarer le bloqueur." });
    }
  }

  async function resolveWizardTaskBlocker(blockerId: string, input: ResolveTaskBlockerInput) {
    if (!wizardTaskId) return;
    try {
      await api.resolveTaskBlocker(wizardTaskId, blockerId, input);
      await loadWizardTaskWorkflow();
      await refreshCollaboratorWizard();
      setMessage({ tone: "success", text: "Bloqueur résolu." });
    } catch (error) {
      setMessage({ tone: "error", text: error instanceof Error ? error.message : "Impossible de résoudre le bloqueur." });
    }
  }

  async function previewWizardDocument(documentId: string) {
    if (!wizardPackage) return;
    setWizardDocumentBusy(true);
    try {
      const blob = await api.getGeneratedDocumentContent(wizardPackage.package_id, documentId);
      setWizardPreviewDocumentId(documentId);
      setWizardPreviewContent(await blob.text());
    } catch (error) {
      setMessage({
        tone: "error",
        text: error instanceof Error ? error.message : "Impossible de prévisualiser le document.",
      });
    } finally {
      setWizardDocumentBusy(false);
    }
  }

  async function downloadWizardDocument(documentId: string) {
    if (!wizardPackage) return;
    setWizardDocumentBusy(true);
    try {
      const blob = await api.getGeneratedDocumentContent(wizardPackage.package_id, documentId, true);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "document-genere.md";
      anchor.click();
      URL.revokeObjectURL(url);
      setMessage({ tone: "success", text: "Document généré téléchargé." });
    } catch (error) {
      setMessage({
        tone: "error",
        text: error instanceof Error ? error.message : "Impossible de télécharger le document.",
      });
    } finally {
      setWizardDocumentBusy(false);
    }
  }

  async function claimWizardTask() {
    const task = wizardTasks.find((item) => item.task_id === wizardTaskId);
    if (!task) return;
    try {
      await api.claimCollaboratorTask(task.task_id, task.aggregate_revision);
      setMessage({ tone: "success", text: "Tâche prise en charge." });
      await refreshCollaboratorWizard();
    } catch (error) {
      setMessage({ tone: "error", text: error instanceof Error ? error.message : "La prise en charge a échoué." });
    }
  }

  async function recordWizardTaskResult(): Promise<boolean> {
    const task = wizardTasks.find((item) => item.task_id === wizardTaskId);
    if (!task || !wizardResultText.trim()) return false;
    try {
      await api.recordCollaboratorTaskResult(task.task_id, {
        expected_revision: task.aggregate_revision,
        result_text: wizardResultText.trim(),
        outcome: wizardOutcome,
      });
      setWizardResultText("");
      setMessage({ tone: "success", text: "Résultat structuré enregistré." });
      await refreshCollaboratorWizard();
      return true;
    } catch (error) {
      setMessage({
        tone: "error",
        text: error instanceof Error ? error.message : "Le résultat n’a pas été enregistré.",
      });
      return false;
    }
  }

  async function completeWizardTask() {
    const task = wizardTasks.find((item) => item.task_id === wizardTaskId);
    if (!task) return;
    try {
      await api.completeCollaboratorTask(task.task_id, task.aggregate_revision);
      setMessage({ tone: "success", text: "Tâche clôturée avec révision optimiste." });
      await refreshCollaboratorWizard();
    } catch (error) {
      setMessage({
        tone: "error",
        text: error instanceof Error ? error.message : "La clôture de la tâche a échoué.",
      });
    }
  }

  async function createWizardSnapshot(selection?: SelectedResponseDraft, annexes:SelectedResponseAnnex[]=[], justification="") {
    if (!wizardContextCurrent || !wizardPackage || wizardPackage.package_id !== wizardPackageId.trim() || wizardPackage.case_id !== wizardCaseId.trim()) return;
    const intent = pendingSnapshotIntent ?? {
      ...newCommandIds(), snapshot_id: wizardSnapshotId.trim() || crypto.randomUUID(),
      expected_package_revision: wizardPackage.aggregate_revision,
      ...(selection ? {selected_response_draft:structuredClone(selection)} : {}),
      ...(annexes.length ? {selected_annexes:structuredClone(annexes),annex_justification:justification.trim()} : {}),
    };
    const operationScope=currentDraftScope;
    const isCurrent=()=>draftScopeMatches(operationScope,false);
    setWizardSnapshotId(intent.snapshot_id);
    setPendingSnapshotIntent(intent);setWizardSnapshotBusy(true);
    let received=false;
    try {
      const receipt=await api.createPreparationSnapshot(wizardPackage.package_id,intent);
      setWizardSnapshotReceipt({snapshot_id:intent.snapshot_id,receipt});
      setPendingSnapshotIntent(null);received=true;
      if(!isCurrent())return;
      const readback=await refreshPreparationAfterCommand(isCurrent);
      if(!isCurrent())return;
      setMessage({tone:readback?"success":"warning",text:readback
        ? `Snapshot ${intent.snapshot_id} créé depuis les octets revus sélectionnés.`
        : "Reçu snapshot enregistré; sources non relues · UNKNOWN."});
    } catch(error) {
      if(!isCurrent())return;
      if(received){setMessage({tone:"warning",text:"Reçu snapshot enregistré; relecture indisponible · UNKNOWN."});return;}
      const terminal=isDefinitiveClientError(error);
      const status=(error as {status?:number})?.status;
      const readback=(terminal||status===409) ? await refreshPreparationAfterCommand(isCurrent).catch(()=>false) : false;
      if(!isCurrent())return;
      if(terminal&&readback)setPendingSnapshotIntent(null);
      setMessage({tone:"error",text:terminal&&readback
        ? "Le serveur a refusé le snapshot; package relu, vérifiez les sources avant une nouvelle intention."
        : "Résultat snapshot UNKNOWN; rejouez la même intention, sélection et identifiants conservés."});
    } finally {setWizardSnapshotBusy(false);}
  }

  async function transmitWizardSnapshot() {
    if(!wizardContextCurrent || !wizardPackage || wizardPackage.package_id!==wizardPackageId.trim() || wizardPackage.case_id!==wizardCaseId.trim() || !wizardSnapshotId.trim())return;
    const intent=pendingTransmissionIntent??{...newCommandIds(),snapshot_id:wizardSnapshotId.trim(),
      transmission_id:wizardTransmissionId.trim()||crypto.randomUUID(),expected_package_revision:wizardPackage.aggregate_revision};
    const operationScope=currentDraftScope;
    const isCurrent=()=>draftScopeMatches(operationScope,false);
    setWizardTransmissionId(intent.transmission_id);
    setPendingTransmissionIntent(intent);setWizardTransmissionBusy(true);
    let received=false;
    try {
      const receipt=await api.transmitPreparationSnapshot(wizardPackage.package_id,intent);
      setWizardTransmissionReceipt({snapshot_id:intent.snapshot_id,transmission_id:intent.transmission_id,receipt});
      setPendingTransmissionIntent(null);received=true;
      if(!isCurrent())return;
      const readback=await refreshPreparationAfterCommand(isCurrent);
      if(!isCurrent())return;
      setMessage({tone:readback?"success":"warning",text:readback
        ? `Snapshot transmis au patron (reçu ${intent.transmission_id}). Aucun dépôt externe n’est effectué par cette action.`
        : "Reçu de transmission enregistré; sources non relues · UNKNOWN."});
    } catch(error) {
      if(!isCurrent())return;
      if(received){setMessage({tone:"warning",text:"Reçu de transmission enregistré; relecture indisponible · UNKNOWN."});return;}
      const terminal=isDefinitiveClientError(error);
      const status=(error as {status?:number})?.status;
      const readback=(terminal||status===409) ? await refreshPreparationAfterCommand(isCurrent).catch(()=>false) : false;
      if(!isCurrent())return;
      if(terminal&&readback)setPendingTransmissionIntent(null);
      setMessage({tone:"error",text:terminal&&readback
        ? "Le serveur a refusé la transmission; package relu, vérifiez le reçu Patron avant une nouvelle intention."
        : "Résultat transmission UNKNOWN; rejouez la même intention et les mêmes identifiants."});
    } finally {setWizardTransmissionBusy(false);}
  }

  return {
    wizardCaseId,
    wizardPackageId,
    wizardPackage: wizardContextCurrent ? wizardPackage : null,
    wizardTasks: wizardContextCurrent ? wizardTasks : [],
    wizardTaskId,
    wizardResultText,
    wizardOutcome,
    wizardSnapshotId,
    wizardTransmissionId,
    wizardSnapshotReceipt,
    wizardTransmissionReceipt,
    wizardSnapshotBusy,
    wizardTransmissionBusy,
    wizardSnapshotRetryPending: Boolean(pendingSnapshotIntent),
    wizardSnapshotSelection: pendingSnapshotIntent?.selected_response_draft ?? null,
    wizardSnapshotAnnexes: pendingSnapshotIntent?.selected_annexes ?? [],
    wizardTransmissionRetryPending: Boolean(pendingTransmissionIntent),
    canCreateWizardSnapshot: Boolean(
      wizardContextCurrent && wizardPackage
        && wizardPackage.package_id === wizardPackageId.trim()
        && !wizardSnapshotBusy
        && (
          pendingSnapshotIntent
          || wizardSnapshotReceipt?.snapshot_id !== wizardSnapshotId.trim()
        ),
    ),
    canTransmitWizardSnapshot: Boolean(
      wizardContextCurrent && wizardPackage
        && wizardPackage.package_id === wizardPackageId.trim()
        && (wizardSnapshotId.trim() || pendingTransmissionIntent)
        && !wizardTransmissionBusy
        && wizardTransmissionReceipt?.snapshot_id !== wizardSnapshotId.trim(),
    ),
    wizardPreviewDocumentId,
    wizardPreviewContent: wizardContextCurrent ? wizardPreviewContent : null,
    wizardDocumentBusy,
    wizardTaskWorkflow,
    wizardDocumentKind,
    wizardResponsePlan: !wizardContextCurrent ? emptyResponsePlan : pendingDraftUncertainHere ? { ...wizardResponsePlan, draftRequestState: "UNKNOWN" as const } : wizardResponsePlan,
    canSaveWizardResponsePlan: wizardContextCurrent && canSaveWizardResponsePlan(),
    isWizardResponsePlanCurrent: wizardContextCurrent && isWizardResponsePlanCurrent(),
    canCreateWizardResponseDraft: wizardContextCurrent && canCreateWizardResponseDraft(),
    setWizardCaseId,
    setWizardPackageId,
    setWizardTaskId,
    setWizardResultText,
    setWizardOutcome,
    setWizardSnapshotId,
    setWizardTransmissionId,
    setWizardDocumentKind,
    setWizardResponsePlanItem,
    previewWizardDocument,
    downloadWizardDocument,
    loadWizardTaskWorkflow,
    createWizardInformationRequest,
    recordWizardInformationResponse,
    declareWizardTaskBlocker,
    resolveWizardTaskBlocker,
    loadCollaboratorWizard,
    refreshCollaboratorWizard,
    evaluateWizardReadiness,
    generateWizardDocument,
    createWizardResponsePlan,
    retryWizardResponsePlan,
    readWizardResponsePlan,
    createWizardResponseDraft,
    retryWizardResponseDraft,
    canRetryWizardResponseDraft: Boolean(
      pendingDraftIntent
        && sameDraftScope(pendingDraftScope, currentDraftScope)
        && (pendingDraftUncertainHere || wizardResponsePlan.draftRequestState === "UNKNOWN"
          || wizardResponsePlan.draftRequestState === "SOURCE_UNKNOWN"),
    ),
    claimWizardTask,
    recordWizardTaskResult,
    completeWizardTask,
    createWizardSnapshot,
    transmitWizardSnapshot,
  };
}
