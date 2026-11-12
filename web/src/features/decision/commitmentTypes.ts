import type { AnalysisTreatment, CaseAnalysisItem, CaseAnalysisSummary, DecisionContextReferenceInput, CreateDecisionRequest, FreezeDecisionContextRequest, FinalizeGoNoGoDecisionRequest } from "../../shared/types";
export type CardReference = Omit<DecisionContextReferenceInput, "content_hash"> & {
  content_hash: string | null;
};
export type CardAssessmentLink = {
  link_id: string;
  condition_id: string;
  context_id: string;
  assessment_id: string;
  assessment_revision: number;
  source_context_sha256: string;
  justification: string;
  actor_id: string;
  created_at: string;
};
export type CardPoint = {
  point_key: string;
  axes: string[];
  point: CaseAnalysisItem;
  hypotheses: string | null;
  relations_state: string;
  condition_links: CardAssessmentLink[];
};
export type CardCondition = {
  condition_id: string;
  label: string;
  status: string;
  owner_actor_id: string | null;
  due_at: string | null;
  due_date_absence_reason: string | null;
  failure_consequence: string;
  satisfied_evidence: Record<string, unknown> | null;
  failure_reason: string | null;
};
export type CardDecision = {
  decision_id: string;
  aggregate_revision: number;
  cycle_number: number;
  case_scope_fingerprint: string;
  lifecycle: string;
  outcome: string;
  validity: string;
  context_status: string;
  state: string;
  final_justification: string | null;
  finalized_at: string | null;
  finalized_by_actor_id: string | null;
  context_id: string | null;
  context_fingerprint: string | null;
  rationale: string | null;
  unknowns: unknown[];
  references: CardReference[];
  assessment_snapshots: {
    assessment_id: string;
    revision: number;
    source: Record<string, unknown>;
    treatment: AnalysisTreatment | null;
    expected_evidence: string | null;
    residual_risk: string | null;
    actor_id: string;
    created_at: string;
    justification: string;
    state: string;
  }[];
  assessment_links: CardAssessmentLink[];
  conditions: CardCondition[];
  transitions: {
    transition_id: string;
    condition_id: string;
    from_status: string;
    to_status: string;
    evidence: Record<string, unknown> | null;
    failure_reason: string | null;
    actor_id: string;
    created_at: string;
    revision: number;
  }[];
  truncated: boolean;
};
export type CommitmentCard = {
  unbound_contract_impacts?: string[];
  case_id: string;
  case_scope_fingerprint: string;
  dce_version_id: string | null;
  source_context_state: string;
  axes: Pick<CaseAnalysisSummary["axes"][number], "code" | "label" | "status">[];
  points: CardPoint[];
  coverage: CaseAnalysisSummary["coverage"];
  dossier_review: CaseAnalysisSummary["dossier_review"];
  references: CardReference[];
  truncated: boolean;
  analysis_complete: false;
  gate_effect: "NONE";
  current_decision: CardDecision | null;
  history: CardDecision[];
  history_has_more: boolean;
};
export type AssessmentLinkInput = {
  command_id: string;
  idempotency_key: string;
  link_id: string;
  assessment_id: string;
  assessment_revision: number;
  source_context_sha256: string;
  expected_decision_revision: number;
  justification: string;
  human_confirmed: true;
};
export type CardReceipt = {
  command_id: string;
  idempotency_key: string;
  decision_id?: string;
  confirmation_id?: string;
  version: number;
  context_id?: string;
  link_id?: string;
};
export type RequirementConfirmationInput = {
  command_id: string;
  idempotency_key: string;
  confirmation_id: string;
  expected_confirmation_revision: number;
  outcome: "CONFIRMED";
  reason_code: "SOURCE_REVIEWED";
};
export type CardIntent = {
  kind: "CONFIRM";
  requirementId: string;
  dceVersionId: string;
  input: RequirementConfirmationInput;
} | {
  kind: "CREATE";
  input: CreateDecisionRequest;
} | {
  kind: "FREEZE";
  decisionId: string;
  input: FreezeDecisionContextRequest;
} | {
  kind: "FINALIZE";
  decisionId: string;
  input: FinalizeGoNoGoDecisionRequest;
} | {
  kind: "LINK";
  decisionId: string;
  conditionId: string;
  input: AssessmentLinkInput;
};
