import type {SelectedResponseAnnex} from "../../shared/types";
import { ResponseCoveragePanel } from "./ResponseCoveragePanel";
import {ResponseDraftDownload} from "./ResponseDraftDownload";
import type {ApiClient} from "../../infrastructure/api";
import {BuyerDocxForm} from "./BuyerDocxForm";
import type {BuyerDocxIntentStore} from "./BuyerDocxIntentStore";
import { useEffect, useState } from "react";
import type { Dispatch, SetStateAction } from "react";

import type {
  CollaboratorTask,
  CollaboratorTaskWorkflow,
  CreateInformationRequestInput,
  DeclareTaskBlockerInput,
  PreparationPackage,
  PreparationResponsePlanSection,
  RecordInformationResponseInput,
  ResolveTaskBlockerInput,
  CommandReceipt,
  ResponseContribution,
  SelectedResponseDraft,
} from "../../shared/types";
import type { ResponsePlanItemDraft, WizardResponsePlan } from "./useCollaboratorWizard";
import { ResponseDraftContent } from "./ResponseDraftContent";
import { TaskWorkflowPanel } from "./TaskWorkflowPanel";

type WizardOutcome = "RECORDED" | "NOT_APPLICABLE" | "UNABLE_TO_COMPLETE";

const responsePlanSections: Array<[PreparationResponsePlanSection, string]> = [
  ["COVER", "Présentation"],
  ["UNDERSTANDING", "Compréhension du besoin"],
  ["METHOD", "Méthodologie"],
  ["RESOURCES", "Moyens mobilisés"],
  ["SCHEDULE", "Planning"],
  ["RISKS", "Risques et prévention"],
  ["SOURCES", "Références"],
];

type CollaboratorWizardPanelProps = {
  buyerDocxTools?: {api:ApiClient;store:BuyerDocxIntentStore;onRecorded:()=>void|Promise<void>};
  wizardCaseId: string;
  wizardPackageId: string;
  wizardPackage: PreparationPackage | null;
  wizardTasks: CollaboratorTask[];
  wizardTaskId: string;
  wizardResultText: string;
  wizardOutcome: WizardOutcome;
  wizardSnapshotId: string;
  wizardTransmissionId: string;
  wizardSnapshotReceipt: { snapshot_id: string; receipt: CommandReceipt } | null;
  wizardTransmissionReceipt: { snapshot_id: string; transmission_id: string; receipt: CommandReceipt } | null;
  wizardSnapshotBusy: boolean;
  wizardTransmissionBusy: boolean;
  wizardSnapshotRetryPending: boolean;
  wizardSnapshotSelection?: SelectedResponseDraft | null;
  wizardSnapshotAnnexes?: SelectedResponseAnnex[];
  wizardTransmissionRetryPending: boolean;
  canCreateWizardSnapshot: boolean;
  canTransmitWizardSnapshot: boolean;
  wizardPreviewDocumentId: string | null;
  wizardPreviewContent: string | null;
  wizardDocumentBusy: boolean;
  wizardDocumentKind: "TECHNICAL_RESPONSE" | "DC1" | "DC2" | "DC4";
  wizardResponsePlan: WizardResponsePlan;
  canSaveWizardResponsePlan: boolean;
  isWizardResponsePlanCurrent: boolean;
  canCreateWizardResponseDraft: boolean;
  canRetryWizardResponseDraft: boolean;
  setWizardCaseId: Dispatch<SetStateAction<string>>;
  setWizardPackageId: Dispatch<SetStateAction<string>>;
  setWizardTaskId: Dispatch<SetStateAction<string>>;
  setWizardResultText: Dispatch<SetStateAction<string>>;
  setWizardOutcome: Dispatch<SetStateAction<WizardOutcome>>;
  setWizardSnapshotId: Dispatch<SetStateAction<string>>;
  setWizardTransmissionId: Dispatch<SetStateAction<string>>;
  setWizardDocumentKind: Dispatch<SetStateAction<"TECHNICAL_RESPONSE" | "DC1" | "DC2" | "DC4">>;
  onChangeResponsePlanItem: (requirementId: string, patch: Partial<ResponsePlanItemDraft>) => void;
  onCreateResponsePlan: () => void;
  onRetryResponsePlan: () => void;
  onReadResponsePlan: () => void;
  onLoad: () => void;
  onClaimTask: () => void;
  onRecordResult: () => void | Promise<boolean | void>;
  onCompleteTask: () => void;
  onEvaluateReadiness: () => void;
  onGenerateDocument: () => void;
  onCreateResponseDraft: (contributions?: ResponseContribution[]) => void;
  contributionOwnerKey?: string;
  onRetryResponseDraft: () => void;
  onCreateSnapshot: (selection?: SelectedResponseDraft, annexes?:SelectedResponseAnnex[], justification?:string) => void;
  onTransmitSnapshot: () => void;
  onPreviewDocument: (documentId: string) => void;
  onDownloadDocument: (documentId: string) => void;
  taskWorkflow: CollaboratorTaskWorkflow | null;
  onLoadTaskWorkflow: () => void;
  onCreateInformationRequest: (input: CreateInformationRequestInput) => void;
  onRecordInformationResponse: (requestId: string, input: RecordInformationResponseInput) => void;
  onDeclareTaskBlocker: (input: DeclareTaskBlockerInput) => void;
  onResolveTaskBlocker: (blockerId: string, input: ResolveTaskBlockerInput) => void;
};

export function CollaboratorWizardPanel({
  buyerDocxTools,
  wizardCaseId,
  contributionOwnerKey = "",
  wizardPackageId,
  wizardPackage,
  wizardTasks,
  wizardTaskId,
  wizardResultText,
  wizardOutcome,
  wizardSnapshotId,
  wizardTransmissionId,
  wizardSnapshotReceipt,
  wizardTransmissionReceipt,
  wizardSnapshotBusy,
  wizardTransmissionBusy,
  wizardSnapshotRetryPending,
  wizardSnapshotSelection = null,
  wizardSnapshotAnnexes = [],
  wizardTransmissionRetryPending,
  canCreateWizardSnapshot,
  canTransmitWizardSnapshot,
  setWizardCaseId,
  setWizardPackageId,
  setWizardTaskId,
  setWizardResultText,
  setWizardOutcome,
  setWizardSnapshotId,
  setWizardTransmissionId,
  setWizardDocumentKind,
  wizardResponsePlan,
  canSaveWizardResponsePlan,
  isWizardResponsePlanCurrent,
  canCreateWizardResponseDraft,
  canRetryWizardResponseDraft,
  onChangeResponsePlanItem,
  onCreateResponsePlan,
  onRetryResponsePlan,
  onReadResponsePlan,
  wizardPreviewDocumentId,
  wizardPreviewContent,
  wizardDocumentBusy,
  wizardDocumentKind,
  onLoad,
  onClaimTask,
  onRecordResult,
  onCompleteTask,
  onEvaluateReadiness,
  onGenerateDocument,
  onCreateResponseDraft,
  onRetryResponseDraft,
  onCreateSnapshot,
  onTransmitSnapshot,
  onPreviewDocument,
  onDownloadDocument,
  taskWorkflow,
  onLoadTaskWorkflow,
  onCreateInformationRequest,
  onRecordInformationResponse,
  onDeclareTaskBlocker,
  onResolveTaskBlocker,
}: CollaboratorWizardPanelProps) {
  const [captureState, setCaptureState] = useState<"NONE" | "LOCAL" | "PENDING" | "CONFIRMED">("NONE");

  useEffect(() => {
    setCaptureState("NONE");
  }, [wizardTaskId]);

  function saveTerrainCaptureLocally() {
    if (wizardResultText.trim()) setCaptureState("LOCAL");
  }

  async function synchronizeTerrainCapture() {
    if (!wizardResultText.trim() || !wizardTaskId) return;
    if (typeof navigator !== "undefined" && navigator.onLine === false) return;
    setCaptureState("PENDING");
    const result = await onRecordResult();
    setCaptureState(result === false ? "PENDING" : "CONFIRMED");
  }

  const contributionScope = JSON.stringify([contributionOwnerKey, wizardCaseId, wizardPackageId, wizardPackage?.package_id, wizardPackage?.dce_version_id, wizardResponsePlan.exactPlan?.plan_id, wizardResponsePlan.exactPlan?.version]);
  const [contributionEntry, setContributionEntry] = useState<{ scope: string; values: Record<string, { content: string; missing: string }> }>({ scope: "", values: {} });
  const contributionValues = contributionEntry.scope === contributionScope ? contributionEntry.values : {};
  const contributionItems = wizardResponsePlan.exactPlan?.content.items ?? [];
  const contributions: ResponseContribution[] = contributionItems.map((item) => ({ requirement_id: item.requirement_id, section_code: item.section_code, content: contributionValues[`${item.requirement_id}/${item.section_code}`]?.content ?? "", missing: contributionValues[`${item.requirement_id}/${item.section_code}`]?.missing ?? "" }));
  const contributionsReady = contributions.length > 0 && contributions.every((item) => item.content.trim() || item.missing.trim());
  const contributionContextCurrent = wizardPackage?.case_id === wizardCaseId && wizardPackage?.package_id === wizardPackageId && isWizardResponsePlanCurrent;
  function updateContribution(key: string, patch: { content?: string; missing?: string }) {
    setContributionEntry({ scope: contributionScope, values: { ...contributionValues, [key]: { ...(contributionValues[key] ?? { content: "", missing: "" }), ...patch } } });
  }

  const responseSelectionCurrent = wizardPackage?.case_id === wizardCaseId.trim()
    && wizardPackage?.package_id === wizardPackageId.trim()
    && wizardResponsePlan.readState === "READY" && !wizardResponsePlan.loading
    && wizardResponsePlan.requestState === "IDLE"
    && wizardResponsePlan.exactPlan?.package_id === wizardPackage.package_id
    && wizardResponsePlan.exactPlan?.dce_version_id === wizardPackage.dce_version_id
    && wizardResponsePlan.exactPlan?.state === "SOURCES_CURRENT";
  const requiresResponseChoice = Boolean(wizardResponsePlan.exactPlan || wizardPackage?.response_drafts.some(draft => draft.response_plan_id));
  const [responseChoice, setResponseChoice] = useState<{scope: string; key: string}>({scope:"",key:""});
  const currentDrafts = (responseSelectionCurrent ? wizardPackage?.response_drafts.filter(draft =>
    draft.response_plan_id === wizardResponsePlan.exactPlan?.plan_id
    && draft.response_plan_version === wizardResponsePlan.exactPlan?.version
    && /^[0-9a-f]{64}$/.test(draft.content_sha256 ?? "")
    && !wizardPackage.response_drafts.some(other => other.draft_id === draft.draft_id && other.version > draft.version)
  ) : []) ?? [];
  const draftKey = (draft: {draft_id:string;version:number;content_sha256?:string|null}) => JSON.stringify([draft.draft_id,draft.version,draft.content_sha256]);
  const chosenResponse = responseSelectionCurrent && responseChoice.scope === contributionScope
    ? currentDrafts.find(draft => draftKey(draft) === responseChoice.key && typeof draft.content === "string") : undefined;

  const annexKey = JSON.stringify([contributionScope,chosenResponse && draftKey(chosenResponse)]);
  const [annexEntry,setAnnexEntry] = useState<{key:string;items:SelectedResponseAnnex[];note:string;confirmed:boolean}>({key:"",items:[],note:"",confirmed:false});
  const selectedAnnexes = annexEntry.key===annexKey?annexEntry.items:[];
  const annexNote = annexEntry.key===annexKey?annexEntry.note:"";
  const annexConfirmed = annexEntry.key===annexKey && annexEntry.confirmed;
  function setAnnexes(items:SelectedResponseAnnex[]){setAnnexEntry({key:annexKey,items,note:annexNote,confirmed:false})}
  const responsePlanStatus = isWizardResponsePlanCurrent && wizardResponsePlan.requestState === "IDLE" ? "SOURCES_CURRENT" : "UNKNOWN";
  const responsePlanControlsDisabled = wizardResponsePlan.loading
    || ["SUBMITTING", "UNKNOWN", "READING"].includes(wizardResponsePlan.requestState)
    || wizardResponsePlan.draftRequestState === "UNKNOWN";

  return (
    <section className="section-block wizard-section" id="collaborator-wizard-section">
      <div className="section-heading">
        <div>
          <span className="section-kicker">PARCOURS COLLABORATEUR</span>
          <h2>Wizard de préparation</h2>
        </div>
        <span className="count-pill">{wizardPackage?.state ?? "À charger"}</span>
      </div>
      <div className="wizard-toolbar">
        <label>
          <span>Identifiant de l’affaire</span>
          <input
            value={wizardCaseId}
            onChange={(event) => setWizardCaseId(event.target.value)}
            placeholder="UUID de l’affaire"
          />
        </label>
        <label>
          <span>Identifiant du package</span>
          <input
            value={wizardPackageId}
            onChange={(event) => setWizardPackageId(event.target.value)}
            placeholder="UUID de préparation"
          />
        </label>
        <button className="primary-button" type="button" onClick={onLoad}>
          Charger le wizard <span>→</span>
        </button>
      </div>
      {!wizardPackage || wizardPackage.case_id !== wizardCaseId.trim() || wizardPackage.package_id !== wizardPackageId.trim() ? (
        <div className="empty-card">
          <strong>Le wizard est prêt à être chargé</strong>
          <p>
            Les projections de préparation et les tâches sont lues dans le périmètre collaborateur
            autorisé. Aucune donnée financière n’est exposée ici.
          </p>
        </div>
      ) : (
        <div className="wizard-body">
          <div className="wizard-steps">
            <div className="wizard-step complete">
              <span>1</span>
              <strong>Tâches</strong>
              <small>
                {wizardTasks.filter((task) => task.state === "COMPLETED").length}/
                {wizardTasks.length} terminées
              </small>
            </div>
            <div className={`wizard-step ${wizardPackage.latest_readiness ? "complete" : ""}`}>
              <span>2</span>
              <strong>Complétude</strong>
              <small>{wizardPackage.latest_readiness?.state ?? "À vérifier"}</small>
            </div>
            <div
              className={`wizard-step ${
                wizardPackage.generated_documents.length ? "complete" : ""
              }`}
            >
              <span>3</span>
              <strong>Document</strong>
              <small>{wizardPackage.generated_documents.length ? "Généré" : "À générer"}</small>
            </div>
            <div className="wizard-step">
              <span>4</span>
              <strong>Transmission</strong>
              <small>Contrôle patron</small>
            </div>
          </div>
          <div className="wizard-grid">
            <div className="detail-panel">
              <div className="panel-heading">
                <div>
                  <h3>Tâches de l’affaire</h3>
                  <p>Chaque résultat est structuré, révisé et traçable.</p>
                </div>
                <span className="rule-tag">
                  {wizardTasks.length} tâche{wizardTasks.length > 1 ? "s" : ""}
                </span>
              </div>
              {wizardTasks.length === 0 ? (
                <p className="panel-empty">Aucune tâche projetée.</p>
              ) : (
                <div className="wizard-task-list">
                  {wizardTasks.map((task) => (
                    <button
                      type="button"
                      className={`wizard-task ${task.task_id === wizardTaskId ? "selected" : ""}`}
                      key={task.task_id}
                      onClick={() => setWizardTaskId(task.task_id)}
                    >
                      <div>
                        <strong>{task.title}</strong>
                        <small>
                          {task.task_kind} · {task.priority} · Révision {task.aggregate_revision}
                        </small>
                      </div>
                      <span className={`state-badge state-${task.state.toLowerCase()}`}>
                        {task.state}
                      </span>
                    </button>
                  ))}
                </div>
              )}
              {wizardTaskId && (
                <div className="wizard-task-actions">
                  <button className="secondary-button" type="button" onClick={onClaimTask}>
                    Prendre en charge
                  </button>
                  <label>
                    <span>Résultat</span>
                    <textarea
                      rows={2}
                      value={wizardResultText}
                      onChange={(event) => setWizardResultText(event.target.value)}
                      placeholder="Constat ou preuve structurée, sans donnée financière"
                    />
                  </label>
                  <label>
                    <span>Issue</span>
                    <select
                      value={wizardOutcome}
                      onChange={(event) =>
                        setWizardOutcome(event.target.value as WizardOutcome)
                      }
                    >
                      <option value="RECORDED">Enregistré</option>
                      <option value="NOT_APPLICABLE">Non applicable</option>
                      <option value="UNABLE_TO_COMPLETE">Impossible à compléter</option>
                    </select>
                  </label>
                  <div className="wizard-action-row">
                    <button className="primary-button" type="button" onClick={onRecordResult}>
                      Enregistrer le résultat
                    </button>
                    <button className="secondary-button" type="button" onClick={onCompleteTask}>
                      Clôturer
                    </button>
                  </div>
                  <div className="detail-panel terrain-capture-card">
                    <strong>Capture terrain</strong>
                    <p>
                      Disponibilité réelle : seules les pièces déjà chargées sont visibles ; aucun
                      dossier complet hors connexion n’est promis.
                    </p>
                    <p>
                      La capture locale reste visible comme locale ou en attente ; elle ne confirme
                      la synchronisation qu’après l’enregistrement serveur.
                    </p>
                    <div className="workflow-summary">
                      <span>État : <strong>{captureState}</strong></span>
                      {captureState === "LOCAL" && <span>Risque : perte possible avant synchronisation</span>}
                    </div>
                    <div className="wizard-action-row">
                      <button className="secondary-button" type="button" disabled={!wizardResultText.trim()} onClick={saveTerrainCaptureLocally}>
                        Conserver localement
                      </button>
                      <button className="secondary-button" type="button" disabled={!wizardResultText.trim() || !wizardTaskId || captureState === "CONFIRMED"} onClick={() => void synchronizeTerrainCapture()}>
                        Synchroniser la capture
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
            <div className="detail-panel">
              <div className="panel-heading">
                <div>
                  <h3>Complétude et production</h3>
                  <p>La readiness est recalculée côté serveur avant toute génération.</p>
                </div>
              </div>
              <label className="document-kind-selector">
                <span>Type à générer</span>
                <select value={wizardDocumentKind} onChange={(event) => setWizardDocumentKind(event.target.value as "TECHNICAL_RESPONSE" | "DC1" | "DC2" | "DC4")}>
                  <option value="TECHNICAL_RESPONSE">Réponse technique</option>
                  <option value="DC1">DC1</option>
                  <option value="DC2">DC2</option>
                  <option value="DC4">DC4</option>
                </select>
              </label>
              <div className="wizard-action-row">
                <button className="primary-button" type="button" onClick={onEvaluateReadiness}>
                  Vérifier la complétude
                </button>
                <button
                  className="secondary-button"
                  type="button"
                  disabled={!wizardPackage.latest_readiness}
                  onClick={onGenerateDocument}
                >
                  Générer la réponse technique
                </button>
              </div>
              <section className="response-plan" aria-labelledby="response-plan-title" aria-busy={wizardResponsePlan.loading}>
                <div className="response-plan-header">
                  <div>
                    <h4 id="response-plan-title">Plan de réponse</h4>
                    <p>Reliez chaque exigence DCE à une section et, si elle existe, à une proposition de capacité versionnée.</p>
                  </div>
                  <span className={`state-badge ${responsePlanStatus === "SOURCES_CURRENT" ? "state-success" : "state-warning"}`}>
                    {responsePlanStatus}
                  </span>
                </div>
                {wizardResponsePlan.loading && <p className="response-plan-message" role="status">Lecture des exigences et du plan…</p>}
                {wizardResponsePlan.error && <p className="response-plan-message response-plan-error" role="alert">{wizardResponsePlan.error}</p>}
                {wizardResponsePlan.hasPriorDcePlan && <p className="response-plan-message" role="status">Le plan précédent est lié à une autre version DCE. Recomposez les correspondances depuis les exigences de la version courante; l’ancien plan reste conservé.</p>}
                {!wizardResponsePlan.loading && wizardResponsePlan.readState === "READY" && wizardResponsePlan.requirements.length === 0 && (
                  <p className="response-plan-message">Aucune exigence DCE n’est disponible dans cette version. Aucun plan ne peut être enregistré.</p>
                )}
                {wizardResponsePlan.readState === "READY" && wizardResponsePlan.requirements.length > 0 && (
                  <div className="response-plan-items">
                    {wizardResponsePlan.requirements.map((requirement, index) => {
                      const item = wizardResponsePlan.items.find((candidate) => candidate.requirement_id === requirement.requirement_id);
                      const choices = wizardResponsePlan.proposals
                        .filter((proposal) => proposal.requirement_id === requirement.requirement_id && proposal.task_id === null)
                        .map((proposal) => ({ proposal, candidate: wizardResponsePlan.candidates.find((candidate) => candidate.capability_id === proposal.capability_id && candidate.version_id === proposal.capability_version_id) }))
                        .filter((choice) => choice.candidate !== undefined);
                      const sectionId = `response-plan-section-${index}`;
                      const sourceId = `response-plan-source-${index}`;
                      return (
                        <fieldset className="response-plan-item" key={`${requirement.requirement_id}-${index}`}>
                          <legend><span>Exigence {index + 1}</span><strong>{requirement.requirement_type}</strong></legend>
                          <p className="response-plan-requirement-state">{requirement.document_family} · {requirement.confirmation_outcome}</p>
                          <label htmlFor={sectionId}>Section de réponse</label>
                          <select
                            id={sectionId}
                            value={item?.section_code ?? ""}
                            disabled={responsePlanControlsDisabled}
                            onChange={(event) => onChangeResponsePlanItem(requirement.requirement_id, { section_code: event.target.value as PreparationResponsePlanSection | "" })}
                          >
                            <option value="">Choisir une section…</option>
                            {responsePlanSections.map(([code, label]) => <option key={code} value={code}>{label}</option>)}
                          </select>
                          <label htmlFor={sourceId}>Proposition de capacité (facultatif)</label>
                          <select
                            id={sourceId}
                            value={item?.source_proposal_id ?? ""}
                            disabled={responsePlanControlsDisabled}
                            onChange={(event) => onChangeResponsePlanItem(requirement.requirement_id, { source_proposal_id: event.target.value || null })}
                          >
                            <option value="">Aucune proposition · le plan restera UNKNOWN</option>
                            {choices.map(({ proposal, candidate }) => candidate ? (
                              <option
                                key={proposal.proposal_id}
                                value={proposal.proposal_id}
                                disabled={proposal.validity_state === "EXPIRED" || proposal.source_evidence_state === "EXPIRED" || candidate.validity_state === "EXPIRED" || candidate.source_evidence_state === "EXPIRED"}
                              >
                                {candidate.name} · {candidate.title} · v{candidate.version_number} · {proposal.source_evidence_state}
                              </option>
                            ) : null)}
                          </select>
                        </fieldset>
                      );
                    })}
                  </div>
                )}
                <div className="response-plan-actions">
                  <button className="primary-button" type="button" disabled={!canSaveWizardResponsePlan || wizardResponsePlan.requestState === "SUBMITTING" || wizardResponsePlan.requestState === "READING"} onClick={onCreateResponsePlan}>
                    {wizardResponsePlan.requestState === "SUBMITTING" ? "Enregistrement…" : "Enregistrer le plan"}
                  </button>
                  {wizardResponsePlan.requestState === "UNKNOWN" && <button className="secondary-button" type="button" onClick={onRetryResponsePlan}>Réessayer le même enregistrement</button>}
                  <button className="secondary-button" type="button" disabled={!wizardPackage || responsePlanControlsDisabled} onClick={onReadResponsePlan}>Relire le plan</button>
                </div>
                <div className="response-plan-readback" aria-live="polite">
                  <div className="response-plan-header">
                    <h4>Lecture serveur</h4>
                    {wizardResponsePlan.exactPlan && <span>Révision {wizardResponsePlan.exactPlan.version}</span>}
                  </div>
                  {wizardResponsePlan.exactPlan ? (
                    <ul className="response-plan-readback-list">
                      {wizardResponsePlan.exactPlan.content.items.map((planItem, index) => {
                        const requirement = wizardResponsePlan.requirements.find((candidate) => candidate.requirement_id === planItem.requirement_id);
                        const proposal = planItem.source_proposal_id ? wizardResponsePlan.proposals.find((candidate) => candidate.proposal_id === planItem.source_proposal_id) : undefined;
                        const capability = proposal ? wizardResponsePlan.candidates.find((candidate) => candidate.capability_id === proposal.capability_id && candidate.version_id === planItem.source_capability_version_id) : undefined;
                        const sectionLabel = responsePlanSections.find(([code]) => code === planItem.section_code)?.[1] ?? "Section non résolue";
                        return <li key={`${planItem.requirement_id}-${index}`}><strong>{requirement?.requirement_type ?? "Exigence DCE"}</strong><span>{sectionLabel}</span><span>{capability ? `${capability.name} · ${capability.title} · v${capability.version_number}` : "Proposition non résolue · UNKNOWN"}</span></li>;
                      })}
                    </ul>
                  ) : (
                    <p>Aucun plan exact n’a été relu. UNKNOWN reste opposable.</p>
                  )}
                </div>
                {contributionContextCurrent && <fieldset className="workflow-form" disabled={!canCreateWizardResponseDraft || responsePlanControlsDisabled || wizardResponsePlan.draftRequestState === "SUBMITTING"}>
                  <legend>Contributions de réponse acheteur</legend>
                  <p>Rédaction humaine à relire par le Patron sur son SHA-256 exact. Une saisie ne prouve pas la couverture. Indiquez explicitement chaque manque.</p>
                  {contributions.map((item, index) => <div className="response-plan-item" key={`${item.requirement_id}/${item.section_code}`}>
                    <strong>Exigence {index + 1} · {responsePlanSections.find(([code]) => code === item.section_code)?.[1]}</strong>
                    <p>{wizardResponsePlan.requirements.find((requirement) => requirement.requirement_id === item.requirement_id)?.source_locator_label ?? "Source UNKNOWN"}</p>
                    <label>Contribution humaine — exigence {index + 1}<textarea maxLength={12000} rows={5} value={item.content} onChange={(event) => updateContribution(`${item.requirement_id}/${item.section_code}`, { content: event.target.value })} /></label>
                    <label>Manques à confirmer — exigence {index + 1}<textarea maxLength={2000} rows={2} value={item.missing} onChange={(event) => updateContribution(`${item.requirement_id}/${item.section_code}`, { missing: event.target.value })} /></label>
                    <p>Couverture : UNKNOWN · {item.missing.trim() || (!item.content.trim() ? "Contenu non rédigé : préciser le manque avant enregistrement." : "Absence de manque non démontrée.")}</p>
                  </div>)}
                </fieldset>}
                <div className="response-plan-draft-gate">
                  <div>
                    <strong>{canCreateWizardResponseDraft ? "Plan SOURCES_CURRENT relu" : "Création du brouillon verrouillée"}</strong>
                    <p>{canCreateWizardResponseDraft
                      ? "Le brouillon utilisera cette révision exacte et les sections et propositions relues."
                      : wizardResponsePlan.draftRequestState === "CONFLICT"
                        ? "Conflit détecté. Relisez le plan explicitement avant toute nouvelle intention."
                        : wizardResponsePlan.draftRequestState === "UNKNOWN"
                          ? "Résultat incertain. Réessayez le même brouillon; ne créez pas une nouvelle intention."
                        : wizardResponsePlan.draftRequestState === "SOURCE_UNKNOWN"
                          ? "Les octets d’une pièce sont indisponibles ou leur hash discordant. UNKNOWN bloque la création; rétablissez la pièce ou modifiez le plan avant un nouvel essai."
                        : wizardResponsePlan.draftRequestState === "ERROR"
                          ? "Le serveur a refusé ce brouillon. Relisez le plan et ses sources avant toute nouvelle tentative."
                          : wizardResponsePlan.requestState === "CONFLICT" || wizardResponsePlan.requestState === "ERROR"
                            ? "Relisez explicitement le plan après ce conflit ou refus avant de continuer."
                          : wizardResponsePlan.draftedPlanVersion === wizardResponsePlan.exactPlan?.version
                            ? "Un brouillon a déjà été créé depuis cette révision du plan."
                            : wizardResponsePlan.exactPlan?.state === "SOURCES_CURRENT"
                              ? "Les choix courants diffèrent du plan relu, ou le document technique manque. Relisez et vérifiez le plan avant de continuer."
                              : "UNKNOWN, source absente ou plan non relu : aucun brouillon ne peut être créé."}</p>
                  </div>
                  <button className="secondary-button" type="button" disabled={!canCreateWizardResponseDraft || !contributionContextCurrent || !contributionsReady || wizardResponsePlan.draftRequestState === "SUBMITTING"} onClick={() => onCreateResponseDraft(structuredClone(contributions))}>Créer le brouillon de réponse</button>
                  {canRetryWizardResponseDraft && <button className="secondary-button" type="button" onClick={onRetryResponseDraft}>Réessayer la relecture de source</button>}
                </div>
              </section>
              {wizardPackage.latest_readiness ? (
                <div className="readiness-card">
                  <div className="case-top">
                    <strong>{wizardPackage.latest_readiness.state}</strong>
                    <span>Révision {wizardPackage.latest_readiness.revision}</span>
                  </div>
                  <p>
                    {wizardPackage.latest_readiness.checked_task_count} tâche(s) et {" "}
                    {wizardPackage.latest_readiness.checked_requirement_count} exigence(s)
                    contrôlée(s).
                  </p>
                  {wizardPackage.latest_readiness.blocker_codes.length > 0 && (
                    <div className="code-list">
                      <strong>Blocages</strong>
                      {wizardPackage.latest_readiness.blocker_codes.map((code) => (
                        <span key={code}>{code}</span>
                      ))}
                    </div>
                  )}
                  {wizardPackage.latest_readiness.warning_codes.length > 0 && (
                    <div className="code-list warning">
                      <strong>Avertissements</strong>
                      {wizardPackage.latest_readiness.warning_codes.map((code) => (
                        <span key={code}>{code}</span>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <p className="panel-empty">La complétude n’a pas encore été vérifiée.</p>
              )}
              {wizardPackage.generated_documents.length > 0 && (
                <div className="document-list">
                  {wizardPackage.generated_documents.map((document) => (
                    <div className="document-row" key={document.document_id}>
                      <div>
                        <strong>{document.document_kind}</strong>
                        <span>
                          v{document.version} · {document.state}
                        </span>
                      </div>
                      <div className="wizard-action-row">
                        <button
                          className="secondary-button"
                          type="button"
                          disabled={wizardDocumentBusy}
                          onClick={() => onPreviewDocument(document.document_id)}
                        >
                          {wizardPreviewDocumentId === document.document_id ? "Actualiser l’aperçu" : "Aperçu"}
                        </button>
                        <button
                          className="secondary-button"
                          type="button"
                          disabled={wizardDocumentBusy}
                          onClick={() => onDownloadDocument(document.document_id)}
                        >
                          Télécharger
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {wizardPackage.response_drafts.length > 0 && (
                <div className="response-draft-history" aria-labelledby="response-draft-history-title">
                  <div className="panel-heading">
                    <div>
                      <h3 id="response-draft-history-title">Brouillons enregistrés</h3>
                      <p>Versions créées depuis un plan relu; leur contenu reste distinct du plan.</p>
                    </div>
                    <span className="rule-tag">
                      {wizardPackage.response_drafts.length} brouillon{wizardPackage.response_drafts.length > 1 ? "s" : ""}
                    </span>
                  </div>
                  {wizardPackage.response_drafts.map((draft) => (
                    <div className="response-plan-row" key={`${draft.draft_id}-${draft.version}`}>
                      <div>
                        <strong>Brouillon v{draft.version}</strong>
                        <small>{draft.state} · {draft.responsible_role}</small>
                      </div>
                      <span>{draft.section_codes.join(" · ")}</span>
                    </div>
                  ))}
                </div>
              )}
              {wizardPreviewContent !== null && (
                <div className="document-preview" aria-live="polite">
                  <div className="panel-heading">
                    <div>
                      <h3>Aperçu du document sélectionné</h3>
                      <p>Contenu relu depuis le stockage privé ; aucun lien public n’est créé.</p>
                    </div>
                  </div>
                  <pre>{wizardPreviewContent}</pre>
                </div>
              )}
            </div>
            <div className="detail-panel wizard-transmission">
              <div className="panel-heading">
                <div>
                  <h3>Transmettre au patron</h3>
                  <p>Cette transmission ne dépose jamais le dossier sur un portail externe.</p>
                </div>
              </div>
              {buyerDocxTools && <BuyerDocxForm api={buyerDocxTools.api} store={buyerDocxTools.store}
                ownerKey={contributionOwnerKey} caseId={wizardCaseId} packageId={wizardPackageId}
                source={chosenResponse && chosenResponse.content_format!=="DOCX" ? {draft_id:chosenResponse.draft_id,version:chosenResponse.version,content_sha256:chosenResponse.content_sha256!}:null}
                onRecorded={buyerDocxTools.onRecorded}/>}
              {requiresResponseChoice && <fieldset style={{minWidth:0,overflowWrap:"anywhere"}} disabled={!responseSelectionCurrent || wizardSnapshotBusy || wizardSnapshotRetryPending || wizardTransmissionBusy || wizardTransmissionRetryPending}>
                <legend>Réponse unique à figer</legend>
                {wizardSnapshotRetryPending && wizardSnapshotSelection && <p>Intention figée · UNKNOWN : {wizardSnapshotSelection.draft_id} · version {wizardSnapshotSelection.version} · SHA-256 {wizardSnapshotSelection.content_sha256}. Le retry conserve exactement cette sélection.</p>}
                <p>Choisissez les octets du plan enregistré. Les choix non enregistrés ne sont pas inclus. La revue Patron de ce SHA-256 reste obligatoire; la couverture reste UNKNOWN.</p>
                {currentDrafts.map(draft => <div key={draftKey(draft)} className="response-plan-item">
                  <label><input type="radio" name="assembled-response-choice" checked={chosenResponse === draft}
                    disabled={typeof draft.content !== "string"}
                    onChange={() => {setResponseChoice({scope:contributionScope,key:draftKey(draft)});setAnnexEntry({key:"",items:[],note:"",confirmed:false})}}/>
                    <span>Choisir le brouillon {draft.draft_id} · version {draft.version} · {draft.section_codes.join(" · ")}</span>
                  </label>
                  <small>SHA-256 : {draft.content_sha256}</small>
                  <details><summary>Relire l’assemblage exact, ses sources et ses manques</summary>
                    <ResponseDraftContent content={draft.content ?? null} format={draft.content_format} provenance={draft.content_provenance}/>
                    {buyerDocxTools && draft.content_format==="DOCX" && <ResponseDraftDownload api={buyerDocxTools.api} scopeKey={contributionScope} packageId={wizardPackageId} draft={draft} collaborator/>}
                  </details>
                </div>)}
                {chosenResponse?.content_sha256 && buyerDocxTools && <ResponseCoveragePanel api={buyerDocxTools.api}
                  packageId={wizardPackageId} scopeKey={contributionScope} collaborator
                  selection={{draft_id:chosenResponse.draft_id,version:chosenResponse.version,content_sha256:chosenResponse.content_sha256}}
                  selectedAnnexes={selectedAnnexes} onAnnexesChange={setAnnexes}/>}
                {selectedAnnexes.length>0 && <div className="workflow-form"><p>{selectedAnnexes.length} lien(s) d’annexe choisi(s). Les droits administratifs restent nécessaires; la sélection ne les étend pas. Signature et couverture UNKNOWN.</p>
                  <label>Justification du choix des annexes<textarea maxLength={2000} value={annexNote} onChange={event=>setAnnexEntry({key:annexKey,items:selectedAnnexes,note:event.target.value,confirmed:false})}/></label>
                  <label className="capability-proposal-confirm"><input type="checkbox" checked={annexConfirmed} onChange={event=>setAnnexEntry({key:annexKey,items:selectedAnnexes,note:annexNote,confirmed:event.target.checked})}/>Je confirme ces annexes et leurs empreintes pour ce snapshot.</label>
                </div>}
                {wizardSnapshotRetryPending && wizardSnapshotAnnexes.map(item=><p key={item.requirement_id+item.document_id}>Annexe figée · {item.document_id} · SHA-256 {item.sha256}. Même sélection au retry.</p>)}
                {!currentDrafts.length && <p>Aucun assemblage courant sélectionnable · UNKNOWN.</p>}
              </fieldset>}
              <label>
                <span>Identifiant du snapshot (laisser vide pour en générer un)</span>
                <input
                  value={wizardSnapshotId}
                  onChange={(event) => setWizardSnapshotId(event.target.value)}
                  placeholder="UUID du snapshot"
                  disabled={wizardSnapshotBusy || wizardSnapshotRetryPending || wizardTransmissionBusy || wizardTransmissionRetryPending}
                />
              </label>
              <button
                className="secondary-button"
                type="button"
                disabled={!canCreateWizardSnapshot || (requiresResponseChoice && !chosenResponse && !wizardSnapshotRetryPending) || (!wizardSnapshotRetryPending && selectedAnnexes.length>0 && (!annexConfirmed || !annexNote.trim()))}
                onClick={() => {const selected=chosenResponse ? {draft_id:chosenResponse.draft_id,version:chosenResponse.version,content_sha256:chosenResponse.content_sha256!} : undefined;
                  if(selectedAnnexes.length)onCreateSnapshot(selected,selectedAnnexes,annexNote);else onCreateSnapshot(selected)}}
              >
                {wizardSnapshotBusy ? "Création en cours…" : wizardSnapshotRetryPending ? "Rejouer la même création" : requiresResponseChoice ? "Créer le snapshot choisi" : "Créer le snapshot complet"}
              </button>
              {wizardSnapshotReceipt && <div className="workflow-response">
                <strong>Snapshot créé · {wizardSnapshotReceipt.snapshot_id}</strong>
                <span>{wizardSnapshotReceipt.receipt.aggregate_refs.find((ref) => ref.aggregate_type === "PreparationSnapshot")?.aggregate_revision ?? "Révision inconnue"} · reçu {wizardSnapshotReceipt.receipt.command_id}</span>
              </div>}
              <label>
                <span>Identifiant de transmission (laisser vide pour en générer un)</span>
                <input
                  value={wizardTransmissionId}
                  onChange={(event) => setWizardTransmissionId(event.target.value)}
                  placeholder="UUID de transmission"
                  disabled={wizardTransmissionBusy || wizardTransmissionRetryPending}
                />
              </label>
              <button className="primary-button" type="button" disabled={!canTransmitWizardSnapshot} onClick={onTransmitSnapshot}>
                {wizardTransmissionRetryPending ? "Rejouer la même transmission" : "Transmettre au patron"} <span>→</span>
              </button>
              {wizardTransmissionReceipt && <div className="workflow-response">
                <strong>Reçu de transmission · {wizardTransmissionReceipt.transmission_id}</strong>
                <span>Snapshot {wizardTransmissionReceipt.snapshot_id} · révision package {wizardTransmissionReceipt.receipt.aggregate_refs.find((ref) => ref.aggregate_type === "PreparationTransmission")?.aggregate_revision ?? "UNKNOWN"}</span>
              </div>}
              <small className="invariant-note">
                Sortie : contexte non financier, blocages et preuves structurées uniquement.
              </small>
            </div>
          </div>
          <TaskWorkflowPanel
            taskId={wizardTaskId}
            workflow={taskWorkflow}
            onLoad={onLoadTaskWorkflow}
            onCreateRequest={onCreateInformationRequest}
            onRecordResponse={onRecordInformationResponse}
            onDeclareBlocker={onDeclareTaskBlocker}
            onResolveBlocker={onResolveTaskBlocker}
          />
        </div>
      )}
    </section>
  );
}
