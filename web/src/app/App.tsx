import { useEffect, useRef, useState, type MouseEvent as ReactMouseEvent } from "react";
import { PricingPanel } from "../features/pricing/PricingPanel";
import { usePricingImport } from "../features/pricing/usePricingImport";
import { SubmissionPanel } from "../features/submission/SubmissionPanel";
import { useSubmissionActions } from "../features/submission/useSubmissionActions";
import { EnterpriseLibraryPanel } from "../features/enterprise/EnterpriseLibraryPanel";
import { useEnterpriseLibrary } from "../features/enterprise/useEnterpriseLibrary";
import { CollaboratorWizardPanel } from "../features/wizard/CollaboratorWizardPanel";
import { useCollaboratorWizard } from "../features/wizard/useCollaboratorWizard";
import { PatronCockpitPanel } from "../features/cockpit/PatronCockpitPanel";
import { PatronDecisionPanel } from "../features/decision/PatronDecisionPanel";
import { DecisionRiskRequirementsPanel } from "../features/decision/DecisionRiskRequirementsPanel";
import { DecisionRisksPanel } from "../features/decision/DecisionRisksPanel";
import { DceContractRiskSignalsPanel } from "../features/decision/DceContractRiskSignalsPanel";
import { DecisionCrossChecksPanel } from "../features/decision/DecisionCrossChecksPanel";
import { RegulatoryProfilesPanel } from "../features/decision/RegulatoryProfilesPanel";
import { ContractBaselineImpactsPanel } from "../features/decision/ContractBaselineImpactsPanel";
import { useDecisionRiskRequirements } from "../features/decision/useDecisionRiskRequirements";
import { useDecisionRisks } from "../features/decision/useDecisionRisks";
import { useDceContractRiskSignals } from "../features/decision/useDceContractRiskSignals";
import { useDecisionCrossChecks } from "../features/decision/useDecisionCrossChecks";
import { useRegulatoryProfiles } from "../features/decision/useRegulatoryProfiles";
import { useContractBaselineImpacts } from "../features/decision/useContractBaselineImpacts";
import { usePatronCockpit } from "../features/cockpit/usePatronCockpit";
import { BoampOpportunityPanel } from "../features/opportunities/BoampOpportunityPanel";
import { useBoampOpportunities } from "../features/opportunities/useBoampOpportunities";
import { FinancialDraftPanel } from "../features/draft/FinancialDraftPanel";
import { useFinancialDraft } from "../features/draft/useFinancialDraft";
import { DceKnowledgePanel } from "../features/dce/DceKnowledgePanel";
import { DceOpeningPanel } from "../features/dce/DceOpeningPanel";
import { useDceOpening } from "../features/dce/useDceOpening";
import { CreateCasePanel } from "../features/cases/CreateCasePanel";
import { useDceKnowledge } from "../features/dce/useDceKnowledge";
import { useAuthentication } from "../features/auth/useAuthentication";
import { MfaPanel } from "../features/auth/MfaPanel";
import { PreparationReviewPanel } from "../features/wizard/PreparationReviewPanel";
import { useBackendReadiness } from "../features/connection/useBackendReadiness";
import {
  assertRuntimeApiUrl,
  resolveApiBaseUrl,
} from "../infrastructure/runtimeConfig";
import type {
  AssignedCase,
  CaseResolution,
  FinancialCategory,
  PatronAction,
  PatronDecisionDossier,
  FreezeDecisionContextRequest,
  ResolveDecisionConditionRequest,
  FinalizeGoNoGoDecisionRequest,
  PricingScenario,
  StructuredRiskProjection,
  TransitionStructuredRiskTreatmentInput,
  DceContractRiskSignal,
  RegisterStructuredRiskInput,
  CreateCaseInput,
} from "../shared/types";
import { buildDeepLink, readDeepLink, type NavKey } from "./deepLink";
import "./styles.css";

const CATEGORIES: Array<{ value: FinancialCategory; label: string }> = [
  { value: "SALES", label: "Ventes" },
  { value: "DIRECT_COST", label: "Coûts directs" },
  { value: "OVERHEAD", label: "Frais généraux" },
  { value: "SUBCONTRACTING", label: "Sous-traitance" },
  { value: "CONTINGENCY", label: "Provision" },
  { value: "GROSS_MARGIN", label: "Marge brute" },
  { value: "FORECAST_CASHFLOW", label: "Trésorerie prévisionnelle" },
];

const categoryLabel = (category: FinancialCategory) =>
  CATEGORIES.find((item) => item.value === category)?.label ?? category;

const formatMoney = (minor: number, currency = "EUR") =>
  new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(minor / 100);

const formatDate = (value: string) =>
  new Intl.DateTimeFormat("fr-FR", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));

const ACTION_DESTINATIONS: Record<
  PatronAction["action_type"],
  { sectionId: string; navKey: NavKey }
> = {
  REVIEW_PREPARATION: { sectionId: "preparation-section", navKey: "preparation" },
  CONTROL_SUBMISSION: { sectionId: "submission-section", navKey: "submission" },
  VALIDATE_PRICE: { sectionId: "pricing-section", navKey: "review" },
  DECIDE_GO_NO_GO: { sectionId: "decision-section", navKey: "decision" },
};

type ConfirmedView = {
  identityId: string;
  tenantSlug: string;
  actorKind: string;
  caseId: string;
  nav: NavKey;
};

function App() {
  const [baseUrl, setBaseUrl] = useState(() =>
    resolveApiBaseUrl(
      import.meta.env.VITE_API_BASE_URL,
      window.location.protocol,
      window.location.origin,
    ),
  );
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [tenantId, setTenantId] = useState("");
  const [cases, setCases] = useState<AssignedCase[]>([]);
  const [caseResolution, setCaseResolution] = useState<CaseResolution | null>(null);
  const [actions, setActions] = useState<PatronAction[]>([]);
  const [scenarios, setScenarios] = useState<PricingScenario[]>([]);
  const [decisionDossier, setDecisionDossier] = useState<PatronDecisionDossier | null>(null);
  const initialDeepLink = readDeepLink(window.location.hash);
  const [selectedCaseId, setSelectedCaseId] = useState(initialDeepLink.caseId);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ tone: "success" | "error" | "warning"; text: string } | null>(null);
  const [showConnection, setShowConnection] = useState(false);
  const connectionDialogRef = useRef<HTMLFormElement | null>(null);
  const connectionReturnFocus = useRef<HTMLElement | null>(null);
  const [contextConfirmed, setContextConfirmed] = useState(false);
  const [resumePending, setResumePending] = useState(false);
  const lastConfirmedView = useRef<ConfirmedView | null>(null);
  const [activeNav, setActiveNav] = useState<NavKey>(initialDeepLink.section);
  const {
    currentActor,
    isRestoring,
    sessionExpired,
    hasSession,
    isAuthenticated,
    api,
    login,
    refreshActor,
    logout,
  } = useAuthentication(baseUrl);
  const isPatron =
    currentActor?.actor_kind === "PATRON_ADMIN" ||
    currentActor?.actor_kind === "PATRON_DELEGATE";
  const isCollaborator = currentActor?.actor_kind === "COLLABORATEUR";
  const roleLabel = currentActor?.actor_kind === "PATRON_ADMIN"
    ? "Propriétaire et Patron administrateur"
    : currentActor?.actor_kind === "PATRON_DELEGATE"
      ? "Patron délégué"
      : currentActor?.operational_profile === "RESPONSABLE"
        ? "Responsable"
        : currentActor?.operational_profile === "EXPERT"
          ? "Expert"
          : "Collaborateur";
  const businessReady = isAuthenticated && contextConfirmed;
  const {
    backendReadiness,
    backendReadinessState,
    checkBackendReadiness,
  } = useBackendReadiness(api);
  const {
    enterpriseCompany,
    enterpriseCapabilities,
    enterpriseCapabilityForm,
    enterpriseCapabilityVersionForm,
    enterpriseCompanyForm,
    enterpriseDocumentForm,
    enterpriseFile,
    enterpriseUploading,
    enterpriseVerificationDocumentId,
    enterpriseVerificationOutcome,
    enterpriseVerificationReason,
    setEnterpriseCapabilityForm,
    setEnterpriseCapabilityVersionForm,
    setEnterpriseCompanyForm,
    setEnterpriseDocumentForm,
    setEnterpriseFile,
    setEnterpriseVerificationDocumentId,
    setEnterpriseVerificationOutcome,
    setEnterpriseVerificationReason,
    refreshEnterpriseCompany,
    createEnterpriseCompany,
    createEnterpriseCapability,
    addEnterpriseCapabilityVersion,
    uploadEnterpriseDocument,
    verifyEnterpriseDocument,
  } = useEnterpriseLibrary(api, setMessage);
  const {
    wizardCaseId,
    wizardPackageId,
    wizardPackage,
    wizardTasks,
    wizardTaskId,
    wizardResultText,
    wizardOutcome,
    wizardSnapshotId,
    wizardTransmissionId,
    wizardPreviewDocumentId,
    wizardPreviewContent,
    wizardDocumentBusy,
    wizardTaskWorkflow,
    wizardDocumentKind,
    wizardDraftSourceDocumentId,
    wizardDraftSections,
    wizardDraftSourceRefs,
    setWizardCaseId,
    setWizardPackageId,
    setWizardTaskId,
    setWizardResultText,
    setWizardOutcome,
    setWizardSnapshotId,
    setWizardTransmissionId,
    setWizardDocumentKind,
    setWizardDraftSourceDocumentId,
    setWizardDraftSections,
    setWizardDraftSourceRefs,
    loadCollaboratorWizard,
    evaluateWizardReadiness,
    generateWizardDocument,
    createWizardResponseDraft,
    claimWizardTask,
    recordWizardTaskResult,
    completeWizardTask,
    transmitWizardSnapshot,
    previewWizardDocument,
    downloadWizardDocument,
    loadWizardTaskWorkflow,
    createWizardInformationRequest,
    recordWizardInformationResponse,
    declareWizardTaskBlocker,
    resolveWizardTaskBlocker,
  } = useCollaboratorWizard(api, setMessage);
  const financialDraft = useFinancialDraft(api, setMessage, selectedCaseId);
  const cockpit = usePatronCockpit(api, setMessage, async (caseId) => {
    setSelectedCaseId(caseId);
    await refreshScenarios(caseId);
  });
  const boamp = useBoampOpportunities(api, setMessage, async (result) => {
    setSelectedCaseId(result.case_id);
    setActiveNav("review");
    await refreshCases();
  });
  const dceKnowledge = useDceKnowledge(api, setMessage, selectedCaseId);
  const decisionRiskRequirements = useDecisionRiskRequirements(
    api,
    setMessage,
    isPatron ? selectedCaseId : "",
  );
  const decisionRisks = useDecisionRisks(
    api,
    setMessage,
    isPatron ? selectedCaseId : "",
    decisionDossier?.sources ?? [],
  );
  const dceContractRiskSignals = useDceContractRiskSignals(
    api,
    setMessage,
    isPatron ? selectedCaseId : "",
  );
  const decisionCrossChecks = useDecisionCrossChecks(
    api,
    setMessage,
    isPatron ? selectedCaseId : "",
  );
  const regulatoryProfiles = useRegulatoryProfiles(
    api,
    setMessage,
    isPatron ? selectedCaseId : "",
  );
  const contractBaselineImpacts = useContractBaselineImpacts(
    api,
    setMessage,
    isPatron ? selectedCaseId : "",
  );
  const {
    assignments,
    selectedAssignmentId,
    journal,
    interactions,
    refreshAssignments,
    selectAssignment,
  } = cockpit;
  const pricingImport = usePricingImport(
    api,
    setMessage,
    financialDraft.reportId,
    selectedCaseId,
    financialDraft.loadDraft,
  );
  const {
    reportId,
    draft,
    loadingDraft,
    lineForm,
    setReportId,
    setLineForm,
    createDraft,
    loadDraft,
    submitLine,
  } = financialDraft;
  const submissionActions = useSubmissionActions(api, setMessage);
  const selectedCase = cases.find((item) => item.case_id === selectedCaseId) ?? cases[0];
  const dceOpening = useDceOpening(api, setMessage, selectedCase, async () => {
    await refreshCases();
    await dceKnowledge.loadReading(selectedCaseId);
  });
  const primaryAction = actions[0];
  const watchItems = actions.filter((action) => action.action_id !== primaryAction?.action_id).slice(0, 3);
  const summaryCards = draft
    ? [
        { label: "Ventes", value: formatMoney(draft.summary.sales_total_minor, draft.currency_code), accent: "blue" },
        { label: "Coûts directs", value: formatMoney(draft.summary.direct_cost_total_minor, draft.currency_code), accent: "amber" },
        { label: "Marge brute", value: formatMoney(draft.summary.gross_margin_minor, draft.currency_code), accent: "green" },
        { label: "Trésorerie", value: formatMoney(draft.summary.forecast_cashflow_minor, draft.currency_code), accent: "violet" },
      ]
    : [];

  useEffect(() => {
    function handleHashChange() {
      const link = readDeepLink(window.location.hash);
      setActiveNav(link.section);
      if (link.caseId) setSelectedCaseId(link.caseId);
    }
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  useEffect(() => {
    window.history.replaceState(null, "", buildDeepLink({ caseId: selectedCaseId, section: activeNav }));
  }, [selectedCaseId, activeNav]);

  useEffect(() => {
    if (!businessReady || !currentActor) return;
    const confirmedCaseId = cases.some((item) => item.case_id === selectedCaseId)
      ? selectedCaseId
      : cases[0]?.case_id ?? "";
    lastConfirmedView.current = {
      identityId: currentActor.identity_id,
      tenantSlug: currentActor.tenant_slug,
      actorKind: currentActor.actor_kind,
      caseId: confirmedCaseId,
      nav: activeNav,
    };
  }, [activeNav, businessReady, cases, currentActor, selectedCaseId]);

  useEffect(() => {
    if (!sessionExpired) return;
    setCases([]);
    setCaseResolution(null);
    setActions([]);
    setScenarios([]);
    setDecisionDossier(null);
    setSelectedCaseId("");
    setMessage(null);
    setResumePending(lastConfirmedView.current !== null);
    setContextConfirmed(false);
  }, [sessionExpired]);

  useEffect(() => {
    if (!businessReady) return;
    void refreshCases();
    if (isPatron) {
      void refreshAssignments();
      void refreshActions();
      void refreshEnterpriseCompany();
      void boamp.refreshObservations();
    }
  // These effects are keyed to authenticated session, role and selected case. The hook APIs are
  // imperative callbacks recreated by feature hooks and must not trigger a fetch on every render.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [businessReady, isPatron]);

  useEffect(() => {
    if (!showConnection) return;
    const dialog = connectionDialogRef.current;
    if (!dialog) return;
    const focusable = () =>
      Array.from(
        dialog.querySelectorAll<HTMLElement>(
          'button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [href], [tabindex]:not([tabindex="-1"])',
        ),
      );
    const first = focusable()[0];
    first?.focus();
    function trapFocus(event: KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        closeConnection();
        return;
      }
      if (event.key !== "Tab") return;
      const items = focusable();
      if (items.length === 0) return;
      const firstItem = items[0];
      const lastItem = items[items.length - 1];
      if (event.shiftKey && document.activeElement === firstItem) {
        event.preventDefault();
        lastItem.focus();
      } else if (!event.shiftKey && document.activeElement === lastItem) {
        event.preventDefault();
        firstItem.focus();
      }
    }
    document.addEventListener("keydown", trapFocus);
    return () => document.removeEventListener("keydown", trapFocus);
  }, [showConnection]);

  useEffect(() => {
    if (!selectedCaseId || !businessReady) return;
    if (isPatron) {
      void refreshScenarios(selectedCaseId);
      void refreshDecisionDossier(selectedCaseId);
    }
    if (isPatron || isCollaborator) void dceKnowledge.loadReading(selectedCaseId);
    void dceOpening.openSpace();
  // See the session/case keying rationale above; feature-hook commands are intentionally omitted.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCaseId, businessReady, isCollaborator, isPatron]);

  useEffect(() => {
    if (!selectedCaseId || !businessReady) {
      setCaseResolution(null);
      return;
    }
    void refreshCaseResolution(selectedCaseId);
  // Resolution is keyed by the confirmed Case and current session only.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCaseId, businessReady]);

  useEffect(() => {
    setContextConfirmed(false);
  }, [currentActor?.actor_id]);

  async function refreshCases() {
    setLoading(true);
    setMessage(null);
    try {
      const result = await api.listAssignedCases();
      setCases(result);
      const requestedCase = result.find((item) => item.case_id === selectedCaseId);
      if (requestedCase) setSelectedCaseId(requestedCase.case_id);
      else if (!selectedCaseId && result[0]) setSelectedCaseId(result[0].case_id);
      else if (selectedCaseId && !requestedCase) setSelectedCaseId(result[0]?.case_id ?? "");
      setMessage({ tone: "success", text: `${result.length} affaire${result.length > 1 ? "s" : ""} chargée${result.length > 1 ? "s" : ""}.` });
      setResumePending(false);
    } catch (error) {
      setMessage({ tone: "error", text: error instanceof Error ? error.message : "Impossible de charger les affaires." });
    } finally {
      setLoading(false);
    }
  }

  async function createCase(input: CreateCaseInput) {
    if (!isPatron) {
      setMessage({ tone: "warning", text: "Seul un espace patron peut créer une affaire." });
      return;
    }
    try {
      const result = await api.createCase(input);
      setSelectedCaseId(result.case_id);
      setActiveNav("review");
      await refreshCases();
      setMessage({
        tone: "success",
        text: `Affaire créée. Révision ${result.version} · ${result.case_id}`,
      });
    } catch (error) {
      setMessage({
        tone: "error",
        text: error instanceof Error ? error.message : "Impossible de créer l’affaire.",
      });
      throw error;
    }
  }

  async function refreshActions() {
    try {
      const result = await api.listPatronActions();
      setActions(result.items);
    } catch (error) {
      setMessage({
        tone: "error",
        text: error instanceof Error ? error.message : "Impossible de charger les actions.",
      });
    }
  }

  async function refreshScenarios(caseId: string) {
    try {
      setScenarios(await api.listPricingScenarios(caseId));
    } catch (error) {
      setMessage({
        tone: "error",
        text:
          error instanceof Error
            ? error.message
            : "Impossible de charger les scénarios de chiffrage.",
      });
    }
  }

  async function refreshCaseResolution(caseId: string) {
    try {
      setCaseResolution(await api.getCaseResolution(caseId));
    } catch (error) {
      setCaseResolution(null);
      const status = (error as { status?: number }).status;
      if (status === 403 || status === 404) return;
      setMessage({
        tone: "error",
        text:
          error instanceof Error
            ? error.message
            : "Impossible de charger la couverture de l’affaire.",
      });
    }
  }

  async function createDecision() {
    if (!selectedCaseId || currentActor?.actor_kind !== "PATRON_ADMIN") {
      setMessage({ tone: "warning", text: "Sélectionnez une affaire avec un compte patron administrateur." });
      return;
    }
    try {
      await api.createDecision(selectedCaseId, {});
      await refreshDecisionDossier(selectedCaseId);
      setMessage({ tone: "success", text: "Brouillon de décision créé." });
    } catch (error) {
      setMessage({
        tone: "error",
        text: error instanceof Error ? error.message : "Impossible de créer la décision.",
      });
    }
  }

  async function freezeDecisionContext(input: FreezeDecisionContextRequest) {
    if (!selectedCaseId || !decisionDossier || currentActor?.actor_kind !== "PATRON_ADMIN") return;
    try {
      await api.freezeDecisionContext(selectedCaseId, decisionDossier.decision_id, input);
      await refreshDecisionDossier(selectedCaseId);
      setMessage({ tone: "success", text: "Contexte de décision gelé." });
    } catch (error) {
      setMessage({
        tone: "error",
        text: error instanceof Error ? error.message : "Impossible de geler le contexte.",
      });
    }
  }

  async function resolveDecisionCondition(
    conditionId: string,
    input: ResolveDecisionConditionRequest,
  ) {
    if (!selectedCaseId || !decisionDossier || currentActor?.actor_kind !== "PATRON_ADMIN") return;
    try {
      await api.resolveDecisionCondition(
        selectedCaseId,
        decisionDossier.decision_id,
        conditionId,
        input,
      );
      await refreshDecisionDossier(selectedCaseId);
      setMessage({ tone: "success", text: "Condition de décision mise à jour." });
    } catch (error) {
      setMessage({
        tone: "error",
        text: error instanceof Error ? error.message : "Impossible de résoudre la condition.",
      });
    }
  }

  async function transitionDecisionRisk(
    risk: StructuredRiskProjection,
    input: Omit<TransitionStructuredRiskTreatmentInput, "expected_revision">,
  ) {
    if (currentActor?.actor_kind !== "PATRON_ADMIN") return;
    await decisionRisks.transitionRisk(risk, input);
  }

  async function registerDceContractRiskSignal(
    signal: DceContractRiskSignal,
    input: RegisterStructuredRiskInput,
  ) {
    if (currentActor?.actor_kind !== "PATRON_ADMIN") return;
    await dceContractRiskSignals.registerSignal(signal, input);
  }

  async function finalizeDecision(input: FinalizeGoNoGoDecisionRequest) {
    if (!selectedCaseId || !decisionDossier || currentActor?.actor_kind !== "PATRON_ADMIN") return;
    try {
      await api.finalizeDecision(selectedCaseId, decisionDossier.decision_id, input);
      await refreshDecisionDossier(selectedCaseId);
      setMessage({ tone: "success", text: `Décision ${input.outcome} finalisée.` });
    } catch (error) {
      setMessage({
        tone: "error",
        text: error instanceof Error ? error.message : "Impossible de finaliser la décision.",
      });
    }
  }

  async function refreshDecisionDossier(caseId: string) {
    try {
      setDecisionDossier(await api.getDecisionDossier(caseId));
    } catch (error) {
      setDecisionDossier(null);
      // 404 = pas encore de dossier de décision pour cette affaire : état normal.
      if ((error as { status?: number }).status === 404) return;
      setMessage({
        tone: "error",
        text:
          error instanceof Error
            ? error.message
            : "Impossible de charger le dossier de décision.",
      });
    }
  }

  function navigateTo(sectionId: string, navKey: NavKey) {
    setActiveNav(navKey);
    document.getElementById(sectionId)?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function openConnection(event?: ReactMouseEvent<HTMLElement>) {
    connectionReturnFocus.current = event?.currentTarget ?? (
      document.activeElement instanceof HTMLElement ? document.activeElement : null
    );
    setShowConnection(true);
  }

  function closeConnection() {
    setShowConnection(false);
    window.setTimeout(() => connectionReturnFocus.current?.focus(), 0);
  }

  function openHomePrimaryAction() {
    if (primaryAction) {
      if (primaryAction.case_id) setSelectedCaseId(primaryAction.case_id);
      const destination = ACTION_DESTINATIONS[primaryAction.action_type];
      navigateTo(destination.sectionId, destination.navKey);
      return;
    }
    if (selectedCase) {
      setSelectedCaseId(selectedCase.case_id);
      navigateTo("review-section", "review");
      return;
    }
    if (isPatron) navigateTo("create-case-section", "create-case");
  }

  function confirmContext() {
    const snapshot = lastConfirmedView.current;
    const canResume = Boolean(
      resumePending &&
      snapshot &&
      currentActor &&
      snapshot.identityId === currentActor.identity_id &&
      snapshot.tenantSlug === currentActor.tenant_slug &&
      snapshot.actorKind === currentActor.actor_kind,
    );
    if (canResume && snapshot) {
      if (snapshot.caseId) setSelectedCaseId(snapshot.caseId);
      setActiveNav(snapshot.nav);
    } else if (resumePending) {
      lastConfirmedView.current = null;
      setResumePending(false);
    }
    setContextConfirmed(true);
  }

  async function saveConnection(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      const normalizedBaseUrl = assertRuntimeApiUrl(
        baseUrl,
        window.location.protocol,
        window.location.origin,
      );
      if (normalizedBaseUrl !== baseUrl) {
        setBaseUrl(normalizedBaseUrl);
        setMessage({ tone: "warning", text: "URL API enregistrée. Validez de nouveau la connexion avec cette origine." });
        return;
      }
      await checkBackendReadiness();
      await login({ email: loginEmail, password: loginPassword, tenant_id: tenantId });
      setLoginPassword("");
      closeConnection();
      setMessage({ tone: "success", text: "Connexion sécurisée active." });
    } catch (error) {
      setMessage({
        tone: "error",
        text: error instanceof Error ? error.message : "Connexion impossible.",
      });
    }
  }

  async function signOut() {
    lastConfirmedView.current = null;
    setResumePending(false);
    try {
      await logout();
      setMessage({ tone: "success", text: "Session fermée." });
    } catch (error) {
      setMessage({
        tone: "error",
        text: error instanceof Error ? error.message : "Impossible de fermer la session.",
      });
    }
  }

  if (!hasSession) {
    return (
      <main className="content">
        <header className="topbar">
          <div><div className="eyebrow">ACCÈS SMART AO</div><h1>{isRestoring ? "Restauration de la session" : "Connectez-vous"}</h1><p className="lede">Les données métier restent masquées jusqu’à l’établissement d’une session sécurisée.</p></div>
        </header>
        {resumePending && <div className="notice warning" role="status"><span>!</span>Votre session a expiré. Après reconnexion et validation du contexte, le dernier état confirmé sera repris.</div>}
        {!isRestoring && (
          <form className="connection-modal connection-page" onSubmit={saveConnection}>
            <div className="modal-top"><div><span className="section-kicker">CONNEXION SÉCURISÉE</span><h2>Votre espace de travail</h2></div></div>
            <label><span>URL API</span><input required value={baseUrl} onChange={(event) => setBaseUrl(event.target.value)} /></label>
            <div className={`readiness-indicator readiness-${backendReadinessState}`} role="status"><strong>{backendReadinessState === "checking" ? "Vérification en cours…" : backendReadinessState === "ready" ? "Backend prêt" : backendReadinessState === "not_ready" ? "Backend non prêt" : backendReadinessState === "error" ? "Backend inaccessible" : "Backend non vérifié"}</strong>{backendReadiness && <small>PostgreSQL : {backendReadiness.checks.database} · ClamAV : {backendReadiness.checks.clamav}</small>}</div>
            <label><span>Email</span><input required type="email" autoComplete="username" value={loginEmail} onChange={(event) => setLoginEmail(event.target.value)} /></label>
            <label><span>Tenant ID</span><input required value={tenantId} onChange={(event) => setTenantId(event.target.value)} /></label>
            <label><span>Mot de passe</span><input required type="password" autoComplete="current-password" value={loginPassword} onChange={(event) => setLoginPassword(event.target.value)} /></label>
            <button className="primary-button" type="submit">Se connecter <span>→</span></button>
          </form>
        )}
      </main>
    );
  }

  if (hasSession && !isAuthenticated) {
    return (
      <main className="content">
        <header className="topbar">
          <div><div className="eyebrow">ACCÈS SÉCURISÉ</div><h1>Validez votre second facteur</h1><p className="lede">Aucune donnée métier n'est accessible avant cette validation.</p></div>
          <button className="secondary-button" onClick={() => void signOut()}>Se déconnecter</button>
        </header>
        {message && <div className={`notice ${message.tone}`} role={message.tone === "error" ? "alert" : "status"}><span aria-hidden="true">!</span>{message.text}</div>}
        <MfaPanel api={api} setMessage={setMessage} onAuthenticationChanged={refreshActor} />
      </main>
    );
  }

  if (isAuthenticated && !contextConfirmed) {
    return (
      <main className="content">
        <header className="topbar">
          <div><div className="eyebrow">VOTRE ESPACE SMART AO</div><h1>Confirmez votre contexte</h1><p className="lede">Vérifiez l’entreprise et le rôle résolus par le serveur avant d’accéder aux Affaires.</p></div>
          <button className="secondary-button" onClick={() => void signOut()}>Se déconnecter</button>
        </header>
        <section className="section-block">
          <div className="section-heading"><div><span className="section-kicker">ENTREPRISE ACTIVE</span><h2>{currentActor?.tenant_slug}</h2></div><span className="count-pill">MFA validée</span></div>
          <div className="detail-panel">
            <h3>Votre rôle effectif</h3>
            <p>{roleLabel}</p>
            <p>Vos droits dépendent de ce rôle et de votre périmètre autorisé.</p>
            {resumePending && <p className="form-status" role="status">Reprise du dernier état confirmé en cours. Les données seront rechargées avant de confirmer la reprise.</p>}
            <button className="primary-button" type="button" onClick={confirmContext}>Confirmer et continuer</button>
          </div>
        </section>
      </main>
    );
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">S</span><span>SMART_AO <em>V8</em></span></div>
        <div className="workspace-label">{isCollaborator ? "ESPACE COLLABORATEUR" : "ESPACE PATRON"}</div>
        <nav className="nav-list" aria-label="Navigation principale">
          {isPatron && <button className={`nav-item ${activeNav === "overview" ? "active" : ""}`} onClick={() => navigateTo("overview-section", "overview")}><span className="nav-icon">▦</span>Vue d’ensemble</button>}
          {isPatron && <button className={`nav-item ${activeNav === "create-case" ? "active" : ""}`} onClick={() => navigateTo("create-case-section", "create-case")}><span className="nav-icon">＋</span>Nouvelle affaire</button>}
          <button className={`nav-item ${activeNav === "preparation" ? "active" : ""}`} onClick={() => navigateTo("preparation-section", "preparation")}><span className="nav-icon">◇</span>Préparation</button>
          <button className={`nav-item ${activeNav === "review" ? "active" : ""}`} onClick={() => navigateTo("review-section", "review")}><span className="nav-icon">◌</span>Revue</button>
          {isPatron && <button className={`nav-item ${activeNav === "opportunities" ? "active" : ""}`} onClick={() => navigateTo("boamp-section", "opportunities")}><span className="nav-icon">◎</span>Opportunités BOAMP</button>}
          <button className={`nav-item ${activeNav === "dce" ? "active" : ""}`} onClick={() => navigateTo("dce-knowledge-section", "dce")}><span className="nav-icon">⌕</span>Lecture DCE / RAG</button>
          <button className={`nav-item ${activeNav === "dce-opening" ? "active" : ""}`} onClick={() => navigateTo("dce-opening-section", "dce-opening")}><span className="nav-icon">⤓</span>Espace DCE</button>
          <button className={`nav-item ${activeNav === "wizard" ? "active" : ""}`} onClick={() => navigateTo("collaborator-wizard-section", "wizard")}><span className="nav-icon">⌁</span>Wizard collaborateur</button>
          {isPatron && <button className={`nav-item ${activeNav === "library" ? "active" : ""}`} onClick={() => navigateTo("library-section", "library")}><span className="nav-icon">▤</span>Bibliothèque</button>}
          {isPatron && <button className={`nav-item ${activeNav === "decision" ? "active" : ""}`} onClick={() => navigateTo("decision-section", "decision")}><span className="nav-icon">◇</span>Décision</button>}
          {isPatron && <button className={`nav-item ${activeNav === "submission" ? "active" : ""}`} onClick={() => navigateTo("submission-section", "submission")}><span className="nav-icon">↗</span>Dépôt</button>}
        </nav>
        <div className="sidebar-bottom">
          <button className="nav-item" onClick={openConnection}><span className="nav-icon" aria-hidden="true">⚙</span>{isAuthenticated ? "Session" : "Connexion"}</button>
          {isAuthenticated && <button className="nav-item" onClick={() => void signOut()}><span className="nav-icon">↪</span>Se déconnecter</button>}
          <div className="operator-card"><div className="avatar">{currentActor?.actor_kind === "COLLABORATEUR" ? "CO" : "PA"}</div><div><strong>{currentActor ? roleLabel : "Utilisateur non connecté"}</strong><span>{currentActor ? `Membership ${currentActor.membership_state}` : "Authentification requise"}</span></div></div>
        </div>
      </aside>

      <main className="content">
        <header className="topbar">
          <div><div className="eyebrow">{currentActor?.tenant_slug} · {roleLabel}</div><h1>Accueil</h1><p className="lede">Voici ce qui demande votre attention maintenant, dans votre périmètre autorisé.</p></div>
          <div className="top-actions"><div className="secure-pill"><span className="status-dot" />Données confidentielles</div><button className="refresh-button" onClick={() => void refreshCases()} disabled={loading}><span>↻</span> Actualiser</button></div>
        </header>

        {message && <div className={`notice ${message.tone}`} role={message.tone === "error" ? "alert" : "status"}><span aria-hidden="true">{message.tone === "success" ? "✓" : "!"}</span>{message.text}</div>}
        {resumePending && <div className="notice warning" role="status"><span>!</span>Reprise du dernier état confirmé en cours ; aucune donnée nouvelle n’est considérée comme confirmée avant le rechargement.</div>}

        <section className="section-block home-section" id="overview-section" aria-labelledby="home-title">
          <div className="section-heading">
            <div><span className="section-kicker">PREMIER ACCUEIL COMPOSÉ</span><h2 id="home-title">Bonjour. Voici votre point de reprise.</h2></div>
            <span className="count-pill">{loading ? "Actualisation…" : `${cases.length} affaire${cases.length > 1 ? "s" : ""}`}</span>
          </div>
          <div className="home-grid">
            <article className="home-card home-primary">
              <span className="section-kicker">À FAIRE MAINTENANT</span>
              <h3>{primaryAction?.title ?? (selectedCase ? `Reprendre ${selectedCase.work_label}` : isPatron ? "Créer votre première Affaire" : "Aucune Affaire assignée")}</h3>
              <p>{primaryAction?.why_now ?? (selectedCase ? `Dernier état confirmé : ${selectedCase.commercial_stage} · ${selectedCase.case_lifecycle}.` : isPatron ? "Commencez par définir le périmètre connu. Les compléments viendront au moment utile." : "Aucune action métier n’est disponible dans votre périmètre actuel.")}</p>
              {(primaryAction || selectedCase || isPatron) && <button className="primary-button" type="button" onClick={openHomePrimaryAction}>{primaryAction?.recommended_action ?? (selectedCase ? "Ouvrir l’Affaire" : "Créer une Affaire")} <span>→</span></button>}
            </article>
            <article className="home-card">
              <span className="section-kicker">À SURVEILLER</span>
              {watchItems.length > 0 ? <div className="home-list">{watchItems.map((action) => <div key={action.action_id}><strong>{action.title}</strong><span>{action.why_now}</span></div>)}</div> : selectedCase && selectedCase.dce_availability !== "AVAILABLE" ? <div className="home-list"><div><strong>Lecture DCE non disponible</strong><span>État confirmé : {selectedCase.dce_availability}.</span></div></div> : <p>Aucun point à surveiller n’est disponible dans les projections actuelles.</p>}
            </article>
            <article className="home-card">
              <span className="section-kicker">ÉVÉNEMENTS RÉCENTS</span>
              {journal.length > 0 ? <div className="home-list">{journal.slice(0, 3).map((entry) => <div key={entry.record_id}><strong>{entry.event_type}</strong><span>{entry.resulting_state} · {formatDate(entry.recorded_at)}</span></div>)}</div> : <p>Aucun événement d’affectation autorisé n’est disponible.</p>}
              <small>Lire cet historique ne ferme aucune action métier.</small>
            </article>
          </div>
        </section>

        {isPatron && <CreateCasePanel onCreate={createCase} disabled={!businessReady} />}

        {isPatron && (
          <EnterpriseLibraryPanel
          enterpriseCompany={enterpriseCompany}
          enterpriseCapabilities={enterpriseCapabilities}
          enterpriseCapabilityForm={enterpriseCapabilityForm}
          enterpriseCapabilityVersionForm={enterpriseCapabilityVersionForm}
          enterpriseCompanyForm={enterpriseCompanyForm}
          enterpriseDocumentForm={enterpriseDocumentForm}
          enterpriseFile={enterpriseFile}
          enterpriseUploading={enterpriseUploading}
          enterpriseVerificationDocumentId={enterpriseVerificationDocumentId}
          enterpriseVerificationOutcome={enterpriseVerificationOutcome}
          enterpriseVerificationReason={enterpriseVerificationReason}
          setEnterpriseCapabilityForm={setEnterpriseCapabilityForm}
          setEnterpriseCapabilityVersionForm={setEnterpriseCapabilityVersionForm}
          setEnterpriseCompanyForm={setEnterpriseCompanyForm}
          setEnterpriseDocumentForm={setEnterpriseDocumentForm}
          setEnterpriseFile={setEnterpriseFile}
          setEnterpriseVerificationDocumentId={setEnterpriseVerificationDocumentId}
          setEnterpriseVerificationOutcome={setEnterpriseVerificationOutcome}
          setEnterpriseVerificationReason={setEnterpriseVerificationReason}
          formatDate={formatDate}
          onCreateCompany={() => void createEnterpriseCompany()}
          onCreateCapability={() => void createEnterpriseCapability()}
          onAddCapabilityVersion={() => void addEnterpriseCapabilityVersion()}
          onUploadDocument={() => void uploadEnterpriseDocument()}
            onVerifyDocument={() => void verifyEnterpriseDocument()}
          />
        )}

        {isPatron && (
          <section className="section-block" id="pricing-section">
          <PricingPanel
            scenarios={scenarios}
            formatMoney={formatMoney}
            selectedCaseId={selectedCaseId}
            reportId={reportId}
            pricingImportBatchId={pricingImport.pricingImportBatchId}
            pricingImportBatchRevision={pricingImport.pricingImportBatchRevision}
            pricingImportReportRevision={pricingImport.pricingImportReportRevision}
            pricingImportState={pricingImport.pricingImportState}
            pricingImportUnknownAction={pricingImport.pricingImportUnknownAction}
            pricingImportPreview={pricingImport.pricingImportPreview}
            pricingImportReloadState={pricingImport.pricingImportReloadState}
            pricingImportUploading={pricingImport.pricingImportUploading}
            pricingImportLoading={pricingImport.pricingImportLoading}
            pricingImportSubmitting={pricingImport.pricingImportSubmitting}
            setPricingImportBatchId={pricingImport.setPricingImportBatchId}
            setPricingImportBatchRevision={pricingImport.setPricingImportBatchRevision}
            setPricingImportReportRevision={pricingImport.setPricingImportReportRevision}
            onPreview={(file) => void pricingImport.previewPricingImport(file)}
            onRetryPreview={() => void pricingImport.retryPricingImportPreview()}
            onRetryCommit={() => void pricingImport.retryPricingImportCommit()}
            onReload={() => void pricingImport.reloadPricingImport()}
            onCommit={() => void pricingImport.commitPricingImport()}
            />
          </section>
        )}

        <section className="hero-grid" id="preparation-section">
          <div className="hero-card"><div className="hero-copy"><span className="hero-kicker">CETTE SEMAINE</span><h2>Décider avec la<br /><strong>bonne information.</strong></h2><p>Retrouvez vos affaires actives et reprenez chaque chiffrage là où vous l’avez laissé.</p><button className="primary-button" onClick={() => document.getElementById("draft-section")?.scrollIntoView({ behavior: "smooth" })}>Ouvrir un chiffrage <span>→</span></button></div><div className="hero-orbit"><div className="orbit orbit-one" /><div className="orbit orbit-two" /><div className="orbit-core">AO<br /><small>V8</small></div></div></div>
          <div className="metric-stack"><div className="small-metric"><span className="metric-label">AFFAIRES ACTIVES</span><strong>{cases.length.toString().padStart(2, "0")}</strong><span className="metric-meta">dans votre périmètre</span></div><div className="small-metric"><span className="metric-label">ÉTAT DE LA CONNEXION</span><strong className={isAuthenticated ? "text-green" : "text-amber"}>{isAuthenticated ? "Prête" : isRestoring ? "Restauration…" : "À configurer"}</strong><span className="metric-meta">{baseUrl}</span></div></div>
        </section>

        <section className="section-block" id="review-section"><div className="section-heading"><div><span className="section-kicker">PORTEFEUILLE</span><h2>Mes affaires</h2></div><span className="count-pill">{cases.length} visible{cases.length > 1 ? "s" : ""}</span></div><div className="case-grid">{cases.length === 0 ? <div className="empty-card"><strong>Aucune affaire chargée</strong><p>Connectez-vous avec votre compte pour charger les affaires auxquelles vous avez accès.</p><button className="secondary-button" onClick={openConnection}>Configurer la connexion</button></div> : cases.map((item) => <button key={item.case_id} className={`case-card ${item.case_id === selectedCaseId ? "selected" : ""}`} onClick={() => setSelectedCaseId(item.case_id)}><div className="case-top"><span className="case-status">{item.dce_availability}</span><span className="case-arrow" aria-hidden="true">↗</span></div><h3>{item.work_label}</h3><p>{item.case_id}</p><div className="case-footer"><span>{item.commercial_stage}</span><span>{item.case_lifecycle}</span></div></button>)}</div>{isPatron && caseResolution?.economic_coverage && <div className="economic-coverage" aria-label="Couverture économique de l’affaire"><div className="subheading"><strong>COUVERTURE ÉCONOMIQUE</strong><span>lecture sourcée · aucun feu vert implicite</span></div><div className="economic-coverage-grid"><div><span>Hypothèses</span><strong className={`coverage-state coverage-${caseResolution.economic_coverage.assumptions.state.toLowerCase()}`}>{caseResolution.economic_coverage.assumptions.state}</strong><small>{caseResolution.economic_coverage.assumptions.note}</small></div><div><span>Validité des devis</span><strong className={`coverage-state coverage-${caseResolution.economic_coverage.quote_validity.state.toLowerCase()}`}>{caseResolution.economic_coverage.quote_validity.state}</strong><small>{caseResolution.economic_coverage.quote_validity.note}</small></div><div><span>Capacité</span><strong className={`coverage-state coverage-${caseResolution.economic_coverage.capacity.state.toLowerCase()}`}>{caseResolution.economic_coverage.capacity.state}</strong><small>{caseResolution.economic_coverage.capacity.note}</small></div><div><span>Financement</span><strong className={`coverage-state coverage-${caseResolution.economic_coverage.financing.state.toLowerCase()}`}>{caseResolution.economic_coverage.financing.state}</strong><small>{caseResolution.economic_coverage.financing.note}</small></div></div></div>}</section>

        {isPatron && (
          <BoampOpportunityPanel
          observations={boamp.observations}
          selectedObservationId={boamp.selectedObservationId}
          qualificationForm={boamp.qualificationForm}
          loading={boamp.loading}
          qualifying={boamp.qualifying}
          qualifiedObservationIds={boamp.qualifiedObservationIds}
          creatingCase={boamp.creatingCase}
          sourceStatus={boamp.sourceStatus}
          onRefresh={() => void boamp.refreshObservations()}
          onSelect={boamp.selectObservation}
          onDecisionChange={boamp.setDecision}
          onReasonChange={boamp.setReason}
            onQualify={() => void boamp.qualifySelected()}
            onCreateCase={() => void boamp.createCaseFromSelected()}
            onManualEntry={() => navigateTo("create-case-section", "create-case")}
          />
        )}

        <DceKnowledgePanel
          selectedCaseId={selectedCaseId}
          reading={dceKnowledge.reading}
          results={dceKnowledge.results}
          query={dceKnowledge.query}
          loading={dceKnowledge.loading}
          searching={dceKnowledge.searching}
          onQueryChange={dceKnowledge.setQuery}
          onLoad={() => void dceKnowledge.loadReading()}
          onSearch={() => void dceKnowledge.searchKnowledge()}
          onResetSearch={dceKnowledge.resetSearch}
        />

        <DceOpeningPanel
          selectedCase={selectedCase}
          consultation={dceOpening.consultation}
          dceVersionMetadata={dceOpening.dceVersionMetadata}
          inventory={dceOpening.inventory}
          loading={dceOpening.loading}
          busy={dceOpening.busy}
          sourceChannel={dceOpening.sourceChannel}
          file={dceOpening.file}
          step={dceOpening.step}
          onSourceChannelChange={dceOpening.setSourceChannel}
          onFileChange={dceOpening.setFile}
          onOpen={() => void dceOpening.openSpace()}
          onAdmit={() => void dceOpening.admitSelectedFile()}
        />

        {isAuthenticated && <MfaPanel api={api} setMessage={setMessage} onAuthenticationChanged={refreshActor} />}
        {isPatron && <PreparationReviewPanel api={api} setMessage={setMessage} />}

        <CollaboratorWizardPanel
          wizardCaseId={wizardCaseId}
          wizardPackageId={wizardPackageId}
          wizardPackage={wizardPackage}
          wizardTasks={wizardTasks}
          wizardTaskId={wizardTaskId}
          wizardResultText={wizardResultText}
          wizardOutcome={wizardOutcome}
          wizardSnapshotId={wizardSnapshotId}
          wizardTransmissionId={wizardTransmissionId}
          wizardPreviewDocumentId={wizardPreviewDocumentId}
          wizardPreviewContent={wizardPreviewContent}
          wizardDocumentBusy={wizardDocumentBusy}
          taskWorkflow={wizardTaskWorkflow}
          wizardDocumentKind={wizardDocumentKind}
          wizardDraftSourceDocumentId={wizardDraftSourceDocumentId}
          wizardDraftSections={wizardDraftSections}
          wizardDraftSourceRefs={wizardDraftSourceRefs}
          setWizardDocumentKind={setWizardDocumentKind}
          setWizardDraftSourceDocumentId={setWizardDraftSourceDocumentId}
          setWizardDraftSections={setWizardDraftSections}
          setWizardDraftSourceRefs={setWizardDraftSourceRefs}
          setWizardCaseId={setWizardCaseId}
          setWizardPackageId={setWizardPackageId}
          setWizardTaskId={setWizardTaskId}
          setWizardResultText={setWizardResultText}
          setWizardOutcome={setWizardOutcome}
          setWizardSnapshotId={setWizardSnapshotId}
          setWizardTransmissionId={setWizardTransmissionId}
          onLoad={() => void loadCollaboratorWizard()}
          onClaimTask={() => void claimWizardTask()}
          onRecordResult={() => recordWizardTaskResult()}
          onCompleteTask={() => void completeWizardTask()}
          onEvaluateReadiness={() => void evaluateWizardReadiness()}
          onGenerateDocument={() => void generateWizardDocument()}
          onCreateResponseDraft={() => void createWizardResponseDraft()}
          onTransmitSnapshot={() => void transmitWizardSnapshot()}
          onPreviewDocument={(documentId) => void previewWizardDocument(documentId)}
          onDownloadDocument={(documentId) => void downloadWizardDocument(documentId)}
          onLoadTaskWorkflow={() => void loadWizardTaskWorkflow()}
          onCreateInformationRequest={(input) => void createWizardInformationRequest(input)}
          onRecordInformationResponse={(requestId, input) => void recordWizardInformationResponse(requestId, input)}
          onDeclareTaskBlocker={(input) => void declareWizardTaskBlocker(input)}
          onResolveTaskBlocker={(blockerId, input) => void resolveWizardTaskBlocker(blockerId, input)}
        />

        {isPatron && (
          <PatronCockpitPanel
          assignments={assignments}
          selectedAssignmentId={selectedAssignmentId}
          journal={journal}
          interactions={interactions}
            onSelectAssignment={(assignment) => void selectAssignment(assignment)}
          />
        )}

        {isPatron && (
          <PatronDecisionPanel
            decisionDossier={decisionDossier}
            formatDate={formatDate}
            canManage={currentActor?.actor_kind === "PATRON_ADMIN"}
            onCreateDecision={() => void createDecision()}
            onFreezeContext={(input) => void freezeDecisionContext(input)}
            onResolveCondition={(conditionId, input) =>
              void resolveDecisionCondition(conditionId, input)
            }
            onFinalize={(input) => void finalizeDecision(input)}
          />
        )}

        {isPatron && (
          <DecisionCrossChecksPanel
            caseId={selectedCaseId}
            crossings={decisionCrossChecks.crossings}
            contradictions={decisionCrossChecks.contradictions}
            loading={decisionCrossChecks.loading}
            onRefresh={() => void decisionCrossChecks.refresh()}
          />
        )}

        {isPatron && (
          <DceContractRiskSignalsPanel
            caseId={selectedCaseId}
            signals={dceContractRiskSignals.signals}
            loading={dceContractRiskSignals.loading}
            registeringObservationId={dceContractRiskSignals.registeringObservationId}
            canManage={currentActor?.actor_kind === "PATRON_ADMIN"}
            onRefresh={() => void dceContractRiskSignals.refresh()}
            onRegister={(signal, input) => void registerDceContractRiskSignal(signal, input)}
          />
        )}

        {isPatron && (
          <DecisionRisksPanel
            caseId={selectedCaseId}
            risks={decisionRisks.risks}
            loading={decisionRisks.loading}
            transitioningRiskId={decisionRisks.transitioningRiskId}
            canManage={currentActor?.actor_kind === "PATRON_ADMIN"}
            onRefresh={() => void decisionRisks.refresh()}
            onTransition={(risk, input) => void transitionDecisionRisk(risk, input)}
          />
        )}

        {isPatron && (
          <RegulatoryProfilesPanel
            caseId={selectedCaseId}
            profiles={regulatoryProfiles.profiles}
            loading={regulatoryProfiles.loading}
            onRefresh={() => void regulatoryProfiles.refresh()}
          />
        )}

        {isPatron && (
          <ContractBaselineImpactsPanel
            caseId={selectedCaseId}
            items={contractBaselineImpacts.items}
            loading={contractBaselineImpacts.loading}
            onRefresh={() => void contractBaselineImpacts.refresh()}
          />
        )}

        {isPatron && (
          <DecisionRiskRequirementsPanel
            caseId={selectedCaseId}
            links={decisionRiskRequirements.links}
            nextCursor={decisionRiskRequirements.nextCursor}
            selectedLinkId={decisionRiskRequirements.selectedLinkId}
            pricingItems={decisionRiskRequirements.pricingItems}
            search={decisionRiskRequirements.search}
            loading={decisionRiskRequirements.loading}
            searching={decisionRiskRequirements.searching}
            formatDate={formatDate}
            onRefresh={() => void decisionRiskRequirements.refresh()}
            onLoadMore={() => void decisionRiskRequirements.loadMore()}
            onSelectLink={decisionRiskRequirements.setSelectedLinkId}
            onSearchChange={decisionRiskRequirements.setSearch}
            onReconcilePricing={() => void decisionRiskRequirements.reconcilePricing()}
          />
        )}

        {isPatron && (
          <SubmissionPanel
          preparationPackageId={submissionActions.preparationPackageId}
          preparationRevision={submissionActions.preparationRevision}
          submissionPackageId={submissionActions.submissionPackageId}
          submissionPackageVersion={submissionActions.submissionPackageVersion}
          submissionAuthorizationRationale={submissionActions.submissionAuthorizationRationale}
          submissionMode={submissionActions.submissionMode}
          candidatureOnlyReason={submissionActions.candidatureOnlyReason}
          submissionAuthorized={submissionActions.submissionAuthorized}
          submissionManifest={submissionActions.submissionManifest}
          submissionEvidence={submissionActions.submissionEvidence}
          submissionExported={submissionActions.submissionExported}
          submissionExportState={submissionActions.submissionExportState}
          signatureId={submissionActions.signatureId}
          signaturePackageVersion={submissionActions.signaturePackageVersion}
          signatureStatus={submissionActions.signatureStatus}
          signatureProvider={submissionActions.signatureProvider}
          signatureRevision={submissionActions.signatureRevision}
          evidenceForm={submissionActions.evidenceForm}
          setPreparationPackageId={submissionActions.setPreparationPackageId}
          setPreparationRevision={submissionActions.setPreparationRevision}
          setSubmissionPackageId={submissionActions.setSubmissionPackageId}
          setSubmissionPackageVersion={submissionActions.setSubmissionPackageVersion}
          setSubmissionAuthorizationRationale={submissionActions.setSubmissionAuthorizationRationale}
          setSubmissionMode={submissionActions.setSubmissionMode}
          setCandidatureOnlyReason={submissionActions.setCandidatureOnlyReason}
          setSignatureId={submissionActions.setSignatureId}
          setSignaturePackageVersion={submissionActions.setSignaturePackageVersion}
          setEvidenceForm={submissionActions.setEvidenceForm}
          onPrepare={() => void submissionActions.prepareSubmissionPackage()}
          onAuthorize={() => void submissionActions.authorizeSubmissionPackage()}
          onLoadManifest={() => void submissionActions.loadSubmissionPackageManifest()}
          onLoadEvidence={() => void submissionActions.loadSubmissionEvidence()}
          onRequestSignature={() => void submissionActions.requestSignature()}
          onLoadSignature={() => void submissionActions.loadSignature()}
          onExport={() => void submissionActions.exportSubmissionPackage()}
            onRecordEvidence={() => void submissionActions.recordSubmissionEvidence()}
          />
        )}

        {isPatron && (
          <FinancialDraftPanel
          cases={cases}
          selectedCaseId={selectedCaseId}
          setSelectedCaseId={setSelectedCaseId}
          reportId={reportId}
          setReportId={setReportId}
          draft={draft}
          loadingDraft={loadingDraft}
          lineForm={lineForm}
          setLineForm={setLineForm}
          summaryCards={summaryCards}
          createDraft={() => void createDraft()}
          loadDraft={() => void loadDraft()}
          submitLine={submitLine}
          formatMoney={formatMoney}
          formatDate={formatDate}
            categoryLabel={categoryLabel}
          />
        )}

        <footer className="footer"><span>SMART_AO V8</span><span>Architecture sécurisée · Tenant-scoped · Auditée</span><span>API {baseUrl}</span></footer>
      </main>

      {showConnection && <div className="modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.currentTarget === event.target) closeConnection(); }}><form ref={connectionDialogRef} className="connection-modal" role="dialog" aria-modal="true" aria-labelledby="connection-modal-title" aria-describedby="connection-modal-description" onSubmit={saveConnection}><div className="modal-top"><div><span className="section-kicker">CONFIGURATION</span><h2 id="connection-modal-title">Connexion au backend</h2></div><button type="button" className="close-button" aria-label="Fermer la configuration de connexion" onClick={closeConnection}>×</button></div><p id="connection-modal-description">La session utilise un cookie de renouvellement HttpOnly et un jeton d’accès conservé uniquement en mémoire.</p><label><span>URL API</span><input required value={baseUrl} onChange={(event) => setBaseUrl(event.target.value)} /></label><div className={`readiness-indicator readiness-${backendReadinessState}`} role="status"><strong>{backendReadinessState === "checking" ? "Vérification en cours…" : backendReadinessState === "ready" ? "Backend prêt" : backendReadinessState === "not_ready" ? "Backend non prêt" : backendReadinessState === "error" ? "Backend inaccessible" : "Backend non vérifié"}</strong>{backendReadiness && <small>PostgreSQL : {backendReadiness.checks.database} · ClamAV : {backendReadiness.checks.clamav}</small>}</div><label><span>Email</span><input required type="email" autoComplete="username" value={loginEmail} onChange={(event) => setLoginEmail(event.target.value)} /></label><label><span>Tenant ID</span><input required value={tenantId} onChange={(event) => setTenantId(event.target.value)} /></label><label><span>Mot de passe</span><input required type="password" autoComplete="current-password" value={loginPassword} onChange={(event) => setLoginPassword(event.target.value)} /></label><button className="primary-button" type="submit">Se connecter <span aria-hidden="true">→</span></button></form></div>}
    </div>
  );
}

export default App;
