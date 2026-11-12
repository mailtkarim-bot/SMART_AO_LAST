import type {CapacityRun} from "../features/capacity/types";
export type AssignedCase = {
  aggregate_revision?: number;
  case_id: string;
  work_label: string;
  case_lifecycle: string;
  commercial_stage: string;
  dce_availability: string;
  consultation_id: string | null;
  applicable_dce_version_id: string | null;
};

export type CaseEconomicCoverageState =
  | "PROVEN"
  | "NOT_DEMONSTRATED"
  | "UNKNOWN"
  | "INFEASIBLE"
  | "FORECAST_PRESENT";

export type CaseEconomicCoverageStatus = {
  state: CaseEconomicCoverageState;
  source_refs: string[];
  note: string;
};

export type CaseEconomicCoverage = {
  assumptions: CaseEconomicCoverageStatus;
  quote_validity: CaseEconomicCoverageStatus;
  capacity: CaseEconomicCoverageStatus;
  financing: CaseEconomicCoverageStatus;
};

export const caseResolutionItemKinds = ["REQUIREMENT", "INFORMATION_REQUEST", "TASK_BLOCKER", "CONTRADICTION", "RISK", "UNKNOWN", "CAPABILITY_GAP"] as const;
export type CaseResolutionItemKind = typeof caseResolutionItemKinds[number];

export type CaseResolutionItem = {
  item_id: string;
  item_kind: CaseResolutionItemKind;
  native_state: string;
  source_refs: string[];
  resolution_owner: string | null;
  next_action: string;
  due_at: string | null;
  impact: string | null;
};

export type CaseResolution = {
  case_id: string;
  work_label: string;
  coverage: "PARTIAL";
  items: CaseResolutionItem[];
  economic_coverage: CaseEconomicCoverage | null;
};

export type CreateCaseInput = {
  command_id?: string;
  idempotency_key?: string;
  correlation_id?: string;
  title: string;
  object_description: string;
  scope_kind: "SINGLE_LOT" | "MULTI_LOT" | "TRANCHE" | "VARIANT" | "CUSTOM";
  lot_numbers: string[];
  tranche_reference?: string;
  variant_reference?: string;
  scope_justification?: string;
  origin_kind?: "MANUAL" | "OPPORTUNITY" | "IMPORT" | "CLIENT_REQUEST";
};

export type CreateCaseResponse = {
  status: "SUCCEEDED";
  command_id: string;
  idempotency_key: string;
  result_code: "CASE_CREATED";
  case_id: string;
  version: number;
  event_ids: string[];
  navigation: "CASE_OVERVIEW";
  replayed: boolean;
};

export type HandoverInput = {
  handover_id?: string;
  successor_membership_id: string;
  assignment_ids: string[];
  command_id?: string;
  idempotency_key?: string;
  rationale: string;
  correlation_id?: string;
};

export type HandoverReceipt = {
  record_id: string;
  state: "REQUESTED" | "ACCEPTED";
  replayed: boolean;
};

export type BoampCaseCreationInput = {
  command_id?: string;
  idempotency_key?: string;
  correlation_id?: string;
};

export type BoampCaseCreationResponse = {
  status: "SUCCEEDED";
  command_id: string;
  idempotency_key: string;
  result_code: "CASE_CREATED";
  case_id: string;
  version: number;
  event_ids: string[];
  replayed: boolean;
};

export type FinancialCategory =
  | "SALES"
  | "DIRECT_COST"
  | "OVERHEAD"
  | "SUBCONTRACTING"
  | "CONTINGENCY"
  | "GROSS_MARGIN"
  | "FORECAST_CASHFLOW";

export type FinancialLine = {
  line_id: string;
  category: FinancialCategory;
  label: string;
  quantity_decimal: string;
  unit: string;
  amount_minor: number;
  currency_code: string;
};

export type FinancialSummary = {
  sales_total_minor: number;
  direct_cost_total_minor: number;
  overhead_total_minor: number;
  subcontracting_total_minor: number;
  contingency_total_minor: number;
  gross_margin_minor: number;
  gross_margin_rate_bps: number;
  forecast_cashflow_minor: number;
};

export type DraftReport = {
  report_id: string;
  case_id: string;
  status: "DRAFT";
  aggregate_revision: number;
  currency_code: string;
  calculated_at: string;
  ruleset_version: number;
  summary: FinancialSummary;
  lines: FinancialLine[];
  margin_calculation?: {
    state: "CALCULATED" | "UNKNOWN";
    basis: "DECLARED_BASE_CATEGORIES";
    missing_categories: Array<"SALES" | "DIRECT_COST" | "OVERHEAD" | "SUBCONTRACTING" | "CONTINGENCY">;
    basis_line_ids: string[];
    total_cost_minor: number | null;
    gross_margin_minor: number | null;
    gross_margin_rate_bps: number | null;
    unknown_reason: "MISSING_BASE_CATEGORY" | "INVALID_BASE_AMOUNT" | null;
    rate_unknown_reason: "ZERO_SALES" | null;
  } | null;
};

export type CommandReceipt = {
  status: "SUCCEEDED";
  command_id: string;
  idempotency_key: string;
  result_code: string;
  aggregate_refs: Array<{
    aggregate_type: string;
    aggregate_id: string;
    aggregate_revision: number;
    content_hash?: string;
  }>;
  event_ids: string[];
  replayed: boolean;
};

export type SelectedResponseDraft = {
  draft_id: string;
  version: number;
  content_sha256: string;
};

export type ResponseCoverage = {
  cited_annexes: Array<{requirement_id:string;section_code:string;document_id:string;sha256:string;inclusion:"UNKNOWN"}>;
  package_id: string;
  dce_version_id: string;
  selected_response: SelectedResponseDraft;
  content_format: "MARKDOWN" | "DOCX";
  coverage: "UNKNOWN";
  signature: "UNKNOWN";
  annexes: "UNKNOWN";
  inventory: "CURRENT_NON_FINANCIAL_SIGNALS_ONLY";
  requirements: Array<{
    requirement_id: string;
    document_family: string;
    source_state: string;
    confirmation: string;
    source_locator: string;
    source_anchor: Record<string, unknown> | null;
    source_excerpt?: string | null;
    lot_candidates: number[];
    applicability: "UNKNOWN";
    coverage: "UNKNOWN";
    signature: "UNKNOWN";
    response_state: "TEXT_PRESENT" | "TEXT_WITH_GAPS" | "MISSING" | "UNKNOWN";
    pieces: Array<{
      section_code: string;
      locator: string;
      sha256: string;
      start_byte: number | null;
      end_byte: number | null;
      text_present: boolean;
      missing: string;
    }>;
  }>;
};

export type SelectedResponseAnnex = {requirement_id:string;document_id:string;sha256:string};

export type CreatePreparationSnapshotInput = {
  selected_annexes?: SelectedResponseAnnex[];
  annex_justification?: string;
  selected_response_draft?: SelectedResponseDraft;
  snapshot_id: string;
  expected_package_revision: number;
  command_id?: string;
  idempotency_key?: string;
  correlation_id?: string;
};

export type TransmitPreparationSnapshotInput = {
  snapshot_id: string;
  transmission_id: string;
  expected_package_revision: number;
  command_id?: string;
  idempotency_key?: string;
  correlation_id?: string;
};

export type PublishedFinancialReport = Omit<DraftReport, "status" | "margin_calculation"> & {
  status: "PUBLISHED";
  margin_calculation: NonNullable<DraftReport["margin_calculation"]>;
};

export type FinancialReportPublicationReceipt = CommandReceipt & {
  result_code: "FINANCIAL_REPORT_PUBLISHED";
};

export type PatronAssignment = {
  assignment_id: string;
  case_id: string;
  case_title: string;
  case_lifecycle: "ACTIVE" | "STOPPED" | "ARCHIVED";
  state: "ACTIVE" | "SUSPENDED" | "ENDED" | "EXPIRED";
  aggregate_revision: number;
  starts_at: string;
  ends_at: string | null;
  ended_at: string | null;
  scope_actions: string[];
  scope_classifications: ["INTERNAL_OPERATIONAL"];
};

export type PatronAssignmentJournalItem = {
  record_id: string;
  recorded_at: string;
  event_type:
    | "ASSIGNMENT_CREATED"
    | "ASSIGNMENT_SCOPE_AMENDED"
    | "ASSIGNMENT_SUSPENDED"
    | "ASSIGNMENT_REACTIVATED"
    | "ASSIGNMENT_ENDED";
  resulting_revision: number;
  resulting_state: PatronAssignment["state"];
  reason_code: string | null;
};

export type PatronAssignmentInteractions = {
  assignment_id: string;
  case_id: string;
  case_lifecycle: PatronAssignment["case_lifecycle"];
  items: Array<{
    record_id: string;
    kind: "ACKNOWLEDGEMENT" | "CLARIFICATION_REQUEST" | "UNAVAILABILITY_REPORT";
    recorded_at: string;
    operational_state: "RECORDED" | "OPEN";
    priority?: string | null;
    clarification_kind?: string | null;
    reason_kind?: string | null;
    known_deadline_impact?: boolean | null;
  }>;
};

export type ApiError = Error & { status?: number; detail?: string };

export type PatronAction = {
  action_id: string;
  case_id: string | null;
  functional_key: string;
  action_type: "REVIEW_PREPARATION" | "CONTROL_SUBMISSION" | "VALIDATE_PRICE" | "DECIDE_GO_NO_GO";
  severity: "URGENT" | "BLOCKING" | "AT_RISK" | "MONITOR";
  state: "OPEN" | "IN_PROGRESS" | "WAITING" | "COMPLETED" | "ABANDONED";
  title: string;
  why_now: string;
  impact: string;
  recommended_action: string;
  due_at: string | null;
  source_refs: string[];
  aggregate_revision: number;
};

export type DecisionContextReferenceInput = {
  aggregate_type: "CASE" | "DCE_VERSION" | "DCE_REQUIREMENT" | "DECISION_RISK" | "PRICING_SCENARIO" | "BUSINESS_METHOD_PROFILE" | "CONTRACT_BASELINE_IMPACT" | "ANALYSIS_ASSESSMENT" | "CAPACITY_RUN";
  aggregate_id: string;
  aggregate_revision: number;
  content_hash?: string;
  reference_role: string;
};

export type CreateDecisionRequest = {
  scope_fingerprint?: string;
  command_id?: string;
  idempotency_key?: string;
};

export type FreezeDecisionContextRequest = {
  context_id: string;
  expected_revision: number;
  rationale: string;
  unknowns?: string[];
  risks?: string[];
  references: DecisionContextReferenceInput[];
  command_id?: string;
  idempotency_key?: string;
};

export type ResolveDecisionConditionRequest = {
  transition_id?: string;
  expected_revision: number;
  target_status: "SATISFIED" | "FAILED";
  evidence_reference?: string;
  failure_reason?: string;
  command_id?: string;
  idempotency_key?: string;
};

type DecisionCommandReceipt = Omit<CommandReceipt, "result_code"> & {
  result_code: string;
};

export type CreateDecisionResponse = DecisionCommandReceipt & {
  result_code: "DECISION_DRAFT_CREATED";
  decision_id: string;
  version: number;
};

export type FreezeDecisionContextResponse = DecisionCommandReceipt & {
  result_code: "DECISION_CONTEXT_FROZEN";
  decision_id: string;
  context_id: string;
  fingerprint: string;
  version: number;
};

export type ResolveDecisionConditionResponse = DecisionCommandReceipt & {
  result_code: "DECISION_CONDITION_RESOLVED";
  decision_id: string;
  condition_id: string;
  status: "SATISFIED" | "FAILED";
  version: number;
};

export type ConditionalGoConditionRequest = {
  condition_id: string;
  label: string;
  owner_actor_id: string;
  due_at?: string;
  due_date_absence_reason?: string;
  failure_consequence: string;
};

export type FinalizeGoNoGoDecisionRequest = {
  expected_revision: number;
  displayed_fingerprint: string;
  outcome: "GO" | "CONDITIONAL_GO" | "NO_GO";
  justification: string;
  conditions?: ConditionalGoConditionRequest[];
  command_id?: string;
  idempotency_key?: string;
};

export type FinalizeGoNoGoDecisionResponse = DecisionCommandReceipt & {
  result_code: "DECISION_FINALIZED";
  decision_id: string;
  outcome: "GO" | "CONDITIONAL_GO" | "NO_GO";
  condition_count: number;
  version: number;
};

export type PatronDecisionDossier = {
  decision_id: string;
  aggregate_revision: number;
  case_id: string;
  decision_type: string;
  lifecycle: string;
  outcome: string;
  validity: string;
  context_status: string;
  final_justification: string | null;
  known: unknown[];
  unknowns: unknown[];
  risks: unknown[];
  conditions: Array<{ condition_id: string; label: string; status: string; due_at: string | null; failure_consequence: string }>;
  sources: Array<{ aggregate_type: string; aggregate_id: string; aggregate_revision: number; role: string }>;
  contract_evidence_links: Array<DecisionConditionContractEvidenceLink>;
  context_fingerprint: string | null;
};

export type DecisionConditionContractEvidenceLink = {
  link_id: string;
  condition_id: string;
  context_id: string;
  dce_requirement_id: string;
  dce_requirement_revision: number;
  contract_impact_id: string;
  proof_revision: number;
  profile_version_id: string;
  profile_version: number;
  profile_content_sha256: string;
};

export type RecordContractBaselineImpactInput = {
  command_id: string;
  idempotency_key: string;
  correlation_id: string;
  proof_id: string;
  dce_requirement_id: string;
  dce_requirement_revision: number;
  baseline_source_refs: string[];
  baseline_statement: string;
  deviation_statement?: string;
  impact_statement: string;
};

export type LinkDecisionConditionContractEvidenceInput = {
  link_id: string;
  command_id: string;
  idempotency_key: string;
  correlation_id: string;
  contract_impact_id: string;
  proof_revision: number;
  expected_decision_revision: number;
};

export type StructuredRiskTreatment = "OPEN" | "ACCEPTED" | "MITIGATED";
export type StructuredRiskSeverity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type StructuredRiskLikelihood = "RARE" | "POSSIBLE" | "LIKELY" | "ALMOST_CERTAIN";

export type StructuredRiskProjection = {
  risk_id: string;
  case_id: string;
  dce_version_id: string;
  risk_code: string;
  category: "CCAP" | "CCTP";
  title: string;
  severity: StructuredRiskSeverity;
  likelihood: StructuredRiskLikelihood;
  treatment: StructuredRiskTreatment;
  revision: number;
  due_at: string | null;
  latest_treatment_evidence: {
    locator: Record<string, unknown>;
    start_byte_offset: number;
    end_byte_offset: number;
    excerpt: string;
    rationale: string;
  } | null;
};

export type TransitionStructuredRiskTreatmentInput = {
  expected_revision: number;
  to_treatment: Exclude<StructuredRiskTreatment, "OPEN">;
  evidence_excerpt: string;
  evidence_locator: Record<string, unknown>;
  evidence_start_byte_offset: number;
  evidence_end_byte_offset: number;
  rationale: string;
};

export type StructuredRiskTreatmentResponse = {
  command_id: string;
  idempotency_key: string;
  result_code: "DECISION_RISK_TREATMENT_TRANSITIONED";
  risk_id: string;
  version: number;
  treatment: Exclude<StructuredRiskTreatment, "OPEN">;
  event_ids: string[];
  replayed: boolean;
};

export type DceContractRiskSignal = {
  observation_id: string;
  dce_version_id: string;
  document_family: "CCAP" | "CCTP";
  requirement_kind:
    | "CCAP_PENALTIES"
    | "CCAP_RETENTION_GUARANTEE"
    | "CCAP_GUARANTEE"
    | "CCAP_INSURANCE"
    | "CCTP_VARIANTS"
    | "CCAP_SUBCONTRACTING"
    | "CCAP_QUALIFICATIONS";
  rule_id: string;
  rule_version: string;
  directive: "REQUIRED_SIGNAL" | "OPTIONAL_SIGNAL" | "UNSPECIFIED";
  fragment_id: string;
  source_locator_label: string;
  start_byte_offset: number;
  end_byte_offset: number;
  verification_status: "REVIEW_REQUIRED";
};

export type DceContractRiskSignalPage = {
  case_id: string;
  items: DceContractRiskSignal[];
};

export type RegulatoryProfileStatus =
  | "ACTIVE"
  | "FUTURE"
  | "EXPIRED"
  | "UNKNOWN_APPLICABILITY"
  | "REVIEW_REQUIRED";

export type RegulatoryProfileProjection = {
  profile_id: string;
  case_id: string;
  profile_version: number;
  status: RegulatoryProfileStatus;
  facts: Record<string, unknown>;
  source_refs: string[];
  effective_from: string | null;
  effective_until: string | null;
};

export type RegulatoryProfilePage = {
  case_id: string;
  items: RegulatoryProfileProjection[];
};

export type ContractBaselineImpactStatus = "SOURCE_SIGNAL_ONLY" | "HUMAN_REVIEW_REQUIRED" | "CONFIRMED" | "UNKNOWN" | "SUPERSEDED";
export type ContractBaselineImpact = {
  proof_id: string;
  case_id: string;
  baseline_observation_id: string;
  dce_requirement_id: string | null;
  dce_requirement_revision: number | null;
  proof_revision: number;
  baseline_source_refs: string[];
  baseline_statement: string;
  deviation_statement: string | null;
  impact_statement: string | null;
  status: ContractBaselineImpactStatus;
};
export type ContractBaselineImpactPage = { case_id: string; items: ContractBaselineImpact[] };
export type ContractProofReview = { review_id: string; proof_id: string; reviewer_id: string; reviewed_revision: number; decision: "ACCEPTED" | "REJECTED" | "NEEDS_CLARIFICATION"; rationale: string };
export type ContractProofReviewPage = { case_id: string; items: ContractProofReview[] };
export type ContractQueryExportAudit = { export: { export_id: string; case_id: string; filters: Record<string, unknown>; status: "REQUESTED" | "READY" | "UNKNOWN" | "REFUSED"; actor_id: string; created_at: string }; transitions: { transition_id: string; from_status: string; to_status: string; local_proof_ref: string | null; created_at: string }[] };
export type ExportProofVerification = { status: "MATCH" | "MISMATCH" | "UNAVAILABLE"; calculated_sha256: string | null };
export type PaymentCycle = { cycle_id: string; case_id: string; source_refs: string[]; trigger_event: string; status: "SOURCE_SIGNAL_ONLY" | "REVIEW_REQUIRED" | "UNKNOWN"; cash_assumption: string | null; post_reception_cost_note: string | null };
export type PaymentCycleReview = { review_id: string; cycle_id: string; reviewer_id: string; decision: "ACCEPTED_FOR_PLANNING" | "REVIEW_REQUIRED" | "REJECTED"; rationale: string; created_at: string };
export type PaymentUnknownAudit = { status_counts: Record<string, number>; entries: Array<{ cycle_id: string; status: "SOURCE_SIGNAL_ONLY" | "REVIEW_REQUIRED" | "UNKNOWN"; source_refs: string[]; trigger_event: string }>; rejected_count?: number };
export type PaymentUnknownAuditOwnerAct = { owner_act_id: string; case_id: string; owner_id: string; approved: boolean; rationale: string; created_at: string };
export type PaymentCollectionRejectionReview = { review_id: string; case_id: string; reviewer_id: string; rejected_count: number; decision: "ACKNOWLEDGED" | "FOLLOW_UP_REQUIRED"; rationale: string; created_at: string };
export type CaseOutcomeValue = "WON" | "LOST" | "UNKNOWN";
export type CaseExecutionResults = {
  case_id: string;
  lot_references: string[];
  results: Array<{
    outcome_id: string; lot_reference: string; outcome: CaseOutcomeValue;
    source_locator: string | null; reservations: string[]; unknown_reason: string | null;
    actor_id: string; recorded_at: string;
    transmission: { transmission_id: string; outcome_id: string; recipient: string; reservations: string[]; actor_id: string; recorded_at: string } | null;
    order: { order_id: string; outcome_id: string; decision: "ACCEPTED" | "REJECTED"; source_locator: string; reservations: string[]; rationale: string; actor_id: string; recorded_at: string } | null;
    p6: { p6_control_id: string; order_id: string; decision: "APPROVED" | "REJECTED"; reservations: string[]; rationale: string; actor_id: string; recorded_at: string } | null;
    p7: { p7_result_id: string; p6_control_id: string; result: "COMPLETED" | "UNKNOWN" | "INTERRUPTED"; source_locator: string | null; reason: string | null; reservations: string[]; actor_id: string; recorded_at: string } | null;
  }>;
};
export type HandoverOperationalPoint = {
  point_id: string; kind: string; statement: string;
  offer_excerpt?: string | null; offer_locator?: string | null; contract_locator?: string | null;
  difference_state: "UNKNOWN" | "DECLARED_EQUIVALENT" | "DECLARED_DIFFERENCE";
  difference_note?: string | null; responsible?: string | null; action?: string | null;
  expected_evidence?: string | null; due_date?: string | null;
  criticality: "CRITICAL" | "IMPORTANT" | "UNKNOWN"; condition_id?: string | null;
};
export type HandoverOperationalReview = {
 expected_source_context_sha256:string;
  expected_handover_revision: number; expected_offer_manifest_sha256: string;
  contract_instrument_version_id: string | null; expected_contract_record_sha256: string | null;
  justification: string; human_confirmed: true; points: HandoverOperationalPoint[];
};
export type HandoverContractOption = {instrument_version_id:string;instrument_kind:string;version_reference:string;record_sha256:string;state:string};
export type HandoverConditionOption = {condition_id:string;private_label:string;status:string;decision_id:string;decision_revision:number;due_at:string|null};
export type HandoverContractOptions = {source_context_sha256:string;case_id:string;items:HandoverContractOption[];condition_options:HandoverConditionOption[];truncated:boolean};
export type AcknowledgeHandoverInput = {command_id:string;idempotency_key:string;correlation_id:string;receipt_id:string;expected_snapshot_revision:number;expected_view_sha256:string;receipt_kind:"RECEIVED"|"RECEIVED_WITH_GAPS";note:string;human_confirmed:true};
export type HandoverDocumentReceipt = {receipt_id:string;snapshot_revision:number;view_sha256:string;receipt_kind:string;note:string;actor_id:string;membership_id:string;created_at:string;scope_state:string};
export type CaseHandoverOfferOption = {
  outcome_id: string; lot_reference: string; submission_package_id: string; package_version: number;
  manifest_sha256: string; dce_version_id: string; technical_document_id: string;
  technical_document_version: number; technical_document_kind: string; technical_document_sha256: string;
};
export type CaseHandoverOfferOptions = { case_id: string; items: CaseHandoverOfferOption[] };
export type CaseHandoverSnapshot = {
  schema_version: number; kind: "P7_HANDOVER_SNAPSHOT"; p7_is_order_service: false;
  award: { outcome_id: string; lot_reference: string; source_locator: string | null; recorded_at: string };
  offer: { submission_package_id: string; package_version: number; manifest_sha256: string; dce_version_id: string; technical_document_id: string; technical_document_version: number; technical_document_kind: string; technical_document_sha256: string; financial_content: "NOT_INCLUDED" };
  decision: { state: "KNOWN" | "UNKNOWN"; decision_id: string | null; revision: number | null; outcome: string; context_id: string | null; context_fingerprint: string | null; conditions_state: "KNOWN" | "UNKNOWN"; open_conditions: Array<{ condition_id: string; label: string; status: "OPEN"; due_at: string | null }>; condition_sources: Array<{ condition_id: string; requirement_id: string; requirement_revision: number; impact_id: string; impact_revision: number; profile_version_id: string; profile_version: number; profile_sha256: string }> };
  contract_comparison: { state: string; reason?: string; instrument_version_id?: string; instrument_kind?: string; record_sha256?: string; file_sha256?: string; authority_state?: string };
  operational_review?: {state:string;points:HandoverOperationalPoint[];missing:string[];completeness:string;analysis_complete:false;justification?:string;published_at?:string;publisher_id?:string};
  offer_point_proofs?: Record<string,{state:string;document_id:string;document_version:number;source_sha256:string;start_byte_offset:number|null;end_byte_offset:number|null;contract_excerpt_state:string;locator?:string;part_sha256?:string;text_sha256?:string;text_start_byte_offset?:number;text_end_byte_offset?:number}>;
  excluded: string[];
};
export type CaseHandoverSnapshotItem = { snapshot_id: string; outcome_id: string; lot_reference: string; submission_package_id: string; package_version: number; manifest_sha256: string; revision: number; created_at: string; snapshot: CaseHandoverSnapshot;view_sha256?:string|null;source_state?:string;source_reasons?:string[];receipts?:HandoverDocumentReceipt[];receipts_truncated?:boolean };
export type CaseHandoverSnapshots = { case_id: string; items: CaseHandoverSnapshotItem[];next_cursor?:string|null;truncated?:boolean };
export type RecordCaseHandoverInput = { operational_review?:HandoverOperationalReview;command_id: string; idempotency_key: string; correlation_id: string; snapshot_id: string; outcome_id: string; submission_package_id: string };
export type RecordCaseHandoverReceipt = { command_id: string; idempotency_key: string; status: "SUCCEEDED"; result_code: "CASE_HANDOVER_SNAPSHOT_RECORDED" | "CASE_HANDOVER_RECEIPT_RECORDED"; replayed: boolean };
export type CaseContractChangeKind = "ORDER_OF_SERVICE" | "CHANGE_REQUEST" | "ADDENDUM" | "SCHEDULE_CHANGE";
export type CaseContractChangeApplicability = "APPLICABLE_TO_HANDOVER" | "NOT_APPLICABLE" | "NEEDS_CLARIFICATION";
export type CaseContractChangeInstrument = { contract_instrument_version_id: string; instrument_kind: "SIGNED_CONTRACT" | "AMENDMENT"; version_reference: string; source_refs: string[]; evidence_refs: string[] };
export type A1EngagementSource = { condition_id: string; requirement_id: string; requirement_revision: number; impact_id: string; impact_revision: number; profile_version_id: string; profile_version: number; profile_sha256: string };
export type CaseContractChangeImpactAxis = "SCOPE" | "COST" | "CASH" | "SCHEDULE" | "CAPACITY";
export type CaseContractChangeImpactDeclaration = {
  declaration_id: string; linkage_id: string; source: A1EngagementSource; axis: CaseContractChangeImpactAxis;
  revision: number; impact_state: "DECLARED" | "UNKNOWN"; impact_summary: string | null;
  impact_unknown_reason: string | null; measurement_state: "DECLARED" | "UNKNOWN" | "NOT_APPLICABLE";
  value_as_declared: string | null; currency_code: string | null; unit: string | null;
  measurement_unknown_reason: string | null; assumptions: string[]; source_refs: string[]; evidence_refs: string[];
  rationale: string; linkage_state: "CURRENT" | "REVIEW_REQUIRED"; recorded_at: string;
};
export type CaseContractChangeActionImpactRelation = {
  relation_id: string; action_id: string; applicability_review_id: string; revision: number;
  state: "LINKED" | "UNKNOWN" | "NOT_APPLICABLE"; declaration_ids: string[];
  rationale: string; unknown_reason: string | null; projection_state: "CURRENT" | "REVIEW_REQUIRED";
  recorded_at: string;
};
export type CaseContractChangeEvidenceObject = {
  evidence_object_id: string; action_id: string; c4_relation_id: string; version: 1;
  evidence_kind: "EXECUTION_EVIDENCE" | "EXTERNAL_CONFIRMATION";
  sha256: string | null; actual_byte_size: number | null; media_type: string | null;
  state: "AWAITING_UPLOAD" | "UPLOADING" | "CLEAN" | "REJECTED";
  expires_at: string; recorded_at: string;
};
export type CaseContractChangeActionExecution = { operational_publication?:OperationalChangeConsent|null;source_state?:string;
  act_id: string; action_id: string; c4_relation_id: string; revision: number;
  declared_state: "DECLARED_PERFORMED" | "DECLARED_PARTIAL" | "DECLARED_NOT_PERFORMED" | "UNKNOWN";
  declared_summary: string | null; unknown_reason: string | null; evidence_refs: string[];
  evidence_state: "UNKNOWN" | "REFERENCED" | "RETRIEVED";
  evidence_objects: CaseContractChangeEvidenceObject[];
  external_confirmation_state: "UNKNOWN" | "NOT_CONFIRMED" | "CONFIRMED";
  external_confirmation_note: string | null;
  external_confirmation_acts: Array<{
    confirmation_id: string; act_id: string; evidence_object_id: string; evidence_sha256: string;
    revision: number; received_at: string; external_party: string | null; rationale: string;
    actor_id: string; recorded_at: string;
  }>;
  c4_projection_state: "CURRENT" | "REVIEW_REQUIRED" | "SUPERSEDED";
  actor_id: string; recorded_at: string;
};
export type CaseContractChangeEvent = {
 operational_context?:StoredOperationalChangeContext|null;
 current_operational_context?:StoredOperationalChangeContext|null;
 source_state?:string;source_reasons?:string[];operational_timeline?:{kind:string;record_id:string;recorded_at:string;source_state?:string}[];

  event_id: string; case_id: string; handover_snapshot_id: string; outcome_id: string | null; lot_reference: string;
  offer_package_id: string | null; offer_package_version: number | null; offer_manifest_sha256: string | null; offer_source_locator: string | null;
  change_kind: CaseContractChangeKind; issuer: string | null; summary: string; scope_note: string; source_refs: string[];
  evidence_refs: string[]; declared_received_at: string; declared_instrument: CaseContractChangeInstrument | null;
  applicability_state: "UNKNOWN" | CaseContractChangeApplicability;
  applicability_history: Array<{ operational_review?:StoredOperationalChangeContext|null;source_state?:string;handover_snapshot_id?:string; review_id: string; revision: number; contract_instrument_version_id: string; decision: CaseContractChangeApplicability; delta_state: "UNKNOWN" | "DECLARED"; delta_note: string | null; rationale: string; evidence_refs: string[]; recorded_at: string; contract_instrument: CaseContractChangeInstrument | null }>;
  actions: Array<{ operational_details?:OperationalActionDetails|null;source_state?:string; action_id: string; revision: number; applicability_review_id: string; summary: string; evidence_refs: string[]; due_at: string | null; due_date_absence_reason: string | null; state: "RECORDED"; recorded_at: string }>;
  a1_engagements_state: "KNOWN" | "UNKNOWN"; a1_engagements: A1EngagementSource[];
  engagement_linkage_state: "LINKED" | "UNKNOWN";
  engagement_linkage_history: Array<{ linkage_id: string; revision: number; state: "LINKED" | "UNKNOWN"; selected_sources: A1EngagementSource[]; rationale: string; unknown_reason: string | null; recorded_at: string }>;
  impact_declarations: CaseContractChangeImpactDeclaration[];
  action_impact_relations: CaseContractChangeActionImpactRelation[];
  action_execution_acts: CaseContractChangeActionExecution[];
  evidence_objects: CaseContractChangeEvidenceObject[];
};
export type CaseContractChangeEventList = { truncated?:boolean; case_id: string; events: CaseContractChangeEvent[] };
export type RecordCaseContractChangeEventInput = { operational_context?:OperationalChangeContext; command_id: string; idempotency_key: string; correlation_id: string; event_id: string; handover_snapshot_id: string; change_kind: CaseContractChangeKind; contract_instrument_version_id: string | null; issuer: string | null; summary: string; scope_note: string; source_refs: string[]; evidence_refs: string[]; declared_received_at: string };
export type RecordCaseContractChangeApplicabilityInput = { operational_review?:OperationalChangeContext; command_id: string; idempotency_key: string; correlation_id: string; review_id: string; handover_snapshot_id: string; contract_instrument_version_id: string; expected_revision: number; decision: CaseContractChangeApplicability; delta_state: "UNKNOWN" | "DECLARED"; delta_note: string | null; rationale: string; evidence_refs: string[] };
export type RecordCaseContractChangeActionInput = { operational_details?:OperationalActionDetails; command_id: string; idempotency_key: string; correlation_id: string; action_id: string; applicability_review_id: string; expected_revision: number; action_summary: string; evidence_refs: string[]; due_at: string | null; due_date_absence_reason: string | null };
export type RecordCaseContractChangeEngagementLinkInput = { command_id: string; idempotency_key: string; correlation_id: string; linkage_id: string; expected_revision: number; state: "LINKED" | "UNKNOWN"; selected_sources: A1EngagementSource[]; rationale: string; unknown_reason: string | null };
export type RecordCaseContractChangeImpactDeclarationInput = {
  command_id: string; idempotency_key: string; correlation_id: string; declaration_id: string;
  linkage_id: string; source: A1EngagementSource; expected_revision: number; axis: CaseContractChangeImpactAxis;
  impact_state: "DECLARED" | "UNKNOWN"; impact_summary: string | null; impact_unknown_reason: string | null;
  measurement_state: "DECLARED" | "UNKNOWN" | "NOT_APPLICABLE"; value_as_declared: string | null;
  currency_code: string | null; unit: string | null; measurement_unknown_reason: string | null;
  assumptions: string[]; source_refs: string[]; evidence_refs: string[]; rationale: string;
};
export type RecordCaseContractChangeActionImpactRelationInput = {
  command_id: string; idempotency_key: string; correlation_id: string; relation_id: string;
  expected_revision: number; state: "LINKED" | "UNKNOWN" | "NOT_APPLICABLE";
  declaration_ids: string[]; rationale: string; unknown_reason: string | null;
};
export type RecordCaseContractChangeActionExecutionInput = { operational_publication?:OperationalChangeConsent;
  command_id: string; idempotency_key: string; correlation_id: string; act_id: string;
  c4_relation_id: string; expected_revision: number;
  declared_state: "DECLARED_PERFORMED" | "DECLARED_PARTIAL" | "DECLARED_NOT_PERFORMED" | "UNKNOWN";
  declared_summary: string | null; unknown_reason: string | null; evidence_refs: string[];
  evidence_object_ids: string[];
  external_confirmation_state: "UNKNOWN" | "NOT_CONFIRMED";
  external_confirmation_note: string | null;
};
export type PrepareCaseContractChangeEvidenceUploadInput = {
  command_id: string; idempotency_key: string; correlation_id: string;
  evidence_object_id: string; c4_relation_id: string;
  evidence_kind: "EXECUTION_EVIDENCE" | "EXTERNAL_CONFIRMATION"; expected_byte_size: number;
};
export type PrepareCaseContractChangeEvidenceUploadResponse = {
  evidence_object_id: string; state: "AWAITING_UPLOAD" | "UPLOADING" | "CLEAN" | "REJECTED";
  expires_at: string; replayed: boolean;
};
export type CaseContractChangeEvidenceUploadResponse = {
  evidence_object_id: string; version: 1; state: "CLEAN"; sha256: string;
  actual_byte_size: number; media_type: string;
};
export type RecordCaseContractChangeExternalConfirmationInput = {
  command_id: string; idempotency_key: string; correlation_id: string;
  confirmation_id: string; c4_relation_id: string; evidence_object_id: string;
  expected_revision: number; received_at: string; external_party: string | null; rationale: string;
};
export type RecordCaseOutcomeInput = { command_id: string; idempotency_key: string; correlation_id: string; outcome_id: string; case_id: string; lot_reference: string; outcome: CaseOutcomeValue; source_locator: string | null; reservations: string[]; unknown_reason: string | null };
export type RecordCaseOrderInput = { command_id: string; idempotency_key: string; correlation_id: string; order_id: string; outcome_id: string; case_id: string; decision: "ACCEPTED" | "REJECTED"; rationale: string };
export type RecordCaseP6ControlInput = { command_id: string; idempotency_key: string; correlation_id: string; p6_control_id: string; order_id: string; case_id: string; decision: "APPROVED" | "REJECTED"; reservations: string[]; rationale: string };
export type RecordCaseP7ResultInput = { command_id: string; idempotency_key: string; correlation_id: string; p7_result_id: string; p6_control_id: string; case_id: string; result: "COMPLETED" | "UNKNOWN" | "INTERRUPTED"; source_locator: string | null; reason: string | null; reservations: string[] };
export type CaseRex = { rex_id: string; p7_result_id: string | null; execution_exit_act_id?: string | null; lot_reference: string; motif: "KNOWN" | "UNKNOWN"; scope: "CASE_ONLY" | "LOT_PATTERN" | "ENTERPRISE_PATTERN"; validation: "PENDING" | "APPROVED"; observation: string; consequence: string; follow_up: string; source_locator: string | null; created_at: string };
export type RecordCaseRexInput = { command_id: string; idempotency_key: string; correlation_id: string; rex_id: string; p7_result_id: string; case_id: string; motif: "KNOWN" | "UNKNOWN"; scope: "CASE_ONLY" | "LOT_PATTERN" | "ENTERPRISE_PATTERN"; validation: "PENDING" | "APPROVED"; observation: string; consequence: string; follow_up: string; source_locator: string | null };
export type CaseRexList = { case_id: string; rex: CaseRex[] };
export type CaseInterview = { interview_id: string; case_id: string; held_on: string; source_locator: string; rationale: string; expires_on: string; snapshot: { captured_at?: string; rex?: Array<{ rex_id: string; lot_reference: string; motif: string; scope: string; validation: string; observation?: string; consequence?: string; follow_up?: string; source_locator?: string | null }> }; status: "USABLE" | "EXPIRED"; created_at: string };
export type RecordCaseInterviewInput = { command_id: string; idempotency_key: string; correlation_id: string; interview_id: string; case_id: string; held_on: string; source_locator: string; rationale: string; expires_on: string };
export type CaseInterviewList = { case_id: string; interviews: CaseInterview[] };
export type CaseTeachingSnapshot = NonNullable<CaseInterview["snapshot"]["rex"]>[number] & {execution_exit_act_id?:string;execution_source?:Record<string,unknown>};
export type CaseTeachingSource = { source_case_id: string; source_case_label: string; source_interview_id: string; source_rex_id: string; held_on: string; source_locator: string; interview_rationale: string; expires_on: string; source_validity: "USABLE" | "EXPIRED"; snapshot: CaseTeachingSnapshot; can_assess: boolean; block_reason: string | null };
export type CaseTeachingSources = { case_id: string; sources: CaseTeachingSource[] };
export type CaseTeachingApplicabilityDecision = "APPLICABLE" | "NOT_APPLICABLE" | "REVIEW_REQUIRED";
export type CaseTeachingApplicability = { applicability_id: string; target_case_id: string; source_case_id: string; source_case_label: string; source_interview_id: string; source_rex_id: string; decision: CaseTeachingApplicabilityDecision; rationale: string; target_source_locator: string; source_expires_on: string; source_validity_at_recording: "USABLE" | "EXPIRED"; source_validity_current: "USABLE" | "EXPIRED"; context_state?: "CURRENT" | "UNKNOWN" | "REVIEW_REQUIRED"; source_snapshot: CaseTeachingSnapshot; actor_id: string; recorded_at: string };
export type CaseTeachingApplicabilityList = { case_id: string; applicabilities: CaseTeachingApplicability[] };
export type RecordCaseTeachingApplicabilityInput = { command_id: string; idempotency_key: string; correlation_id: string; applicability_id: string; target_case_id: string; source_case_id: string; source_interview_id: string; source_rex_id: string; decision: CaseTeachingApplicabilityDecision; rationale: string; target_source_locator: string };
export type CasePartnerKind = "SUPPLIER" | "SUBCONTRACTOR" | "CO_CONTRACTOR";
export type CasePartnerEventType = "REQUESTED" | "RECEIVED" | "ENGAGEMENT_DECLARED";
export type CasePartnerValidity = "UNKNOWN" | "VALID" | "EXPIRED";
export type CasePartnerEvent = { event_id: string; partner_id: string; case_id: string; revision: number; event_type: CasePartnerEventType; partner_kind: CasePartnerKind; partner_label: string; related_event_id: string | null; source_locator: string; rationale: string; valid_until: string | null; validity_at_recording: CasePartnerValidity; validity_current: CasePartnerValidity; exclusions_state: "UNKNOWN" | "DECLARED"; exclusions: string[]; mandate_state: "NOT_APPLICABLE" | "UNKNOWN" | "REQUESTED" | "RECEIVED" | "REVIEW_REQUIRED"; mandate_source_locator: string | null; actor_id: string; recorded_at: string };
export type CasePartnerEventList = { case_id: string; events: CasePartnerEvent[]; can_request: boolean; can_receive: boolean; can_declare_engagement: boolean };
export type RecordCasePartnerRequestInput = { command_id: string; idempotency_key: string; correlation_id: string; event_id: string; partner_id: string; case_id: string; expected_revision: number; partner_kind: CasePartnerKind; partner_label: string; source_locator: string; rationale: string };
export type RecordCasePartnerReceiptInput = { command_id: string; idempotency_key: string; correlation_id: string; event_id: string; partner_id: string; case_id: string; expected_revision: number; request_event_id: string | null; partner_kind: CasePartnerKind; partner_label: string; source_locator: string; rationale: string; valid_until: string | null; exclusions_state: "UNKNOWN" | "DECLARED"; exclusions: string[]; mandate_state: "NOT_APPLICABLE" | "UNKNOWN" | "REQUESTED" | "RECEIVED" | "REVIEW_REQUIRED"; mandate_source_locator: string | null };
export type DeclareCasePartnerEngagementInput = { command_id: string; idempotency_key: string; correlation_id: string; event_id: string; partner_id: string; case_id: string; expected_revision: number; receipt_event_id: string; source_locator: string; rationale: string };
export type PartnerOfferPriceDeclaration = { declaration_id: string; revision: number; amount_as_declared: string; currency_code: string; actor_id: string; created_at: string };
export type PartnerOfferPriceView = { receipt_event_id: string; partner_id: string; partner_kind: CasePartnerKind; partner_label: string; partner_revision: number; source_locator: string; source_rationale: string; valid_until: string | null; validity_current: CasePartnerValidity; exclusions_state: "UNKNOWN" | "DECLARED"; exclusions: string[]; mandate_state: "NOT_APPLICABLE" | "UNKNOWN" | "REQUESTED" | "RECEIVED" | "REVIEW_REQUIRED"; is_latest_receipt: boolean; price_state: "UNKNOWN" | "DECLARED"; declarations: PartnerOfferPriceDeclaration[] };
export type PartnerOfferPriceList = { case_id: string; offers: PartnerOfferPriceView[] };
export type DeclarePartnerOfferPriceInput = { command_id: string; idempotency_key: string; correlation_id: string; declaration_id: string; expected_revision: number; amount_as_declared: string; currency_code: string };
export type PartnerOfferScopeDecision = "SAME_SCOPE_CONFIRMED" | "DIFFERENT_SCOPE" | "NEEDS_CLARIFICATION";
export type PartnerOfferScopeFactInput = { receipt_event_id: string; inclusion_state: "UNKNOWN" | "DECLARED"; included_scope_note: string | null; exclusions_review_state: "UNKNOWN" | "REVIEWED"; transport_state: "UNKNOWN" | "INCLUDED" | "EXCLUDED" | "SEPARATE"; transport_note: string | null };
export type PartnerOfferScopeReview = { review_id: string; comparison_id: string; revision: number; decision: PartnerOfferScopeDecision; rationale: string; actor_id: string; recorded_at: string; requires_reassessment: boolean; offers: Array<PartnerOfferScopeFactInput & { partner_id: string; partner_kind: CasePartnerKind; partner_label: string; source_locator: string; source_rationale: string; validity_current: CasePartnerValidity; exclusions_state: "UNKNOWN" | "DECLARED"; exclusions: string[]; receipt_is_current: boolean }> };
export type PartnerOfferScopeReviewList = { case_id: string; reviews: PartnerOfferScopeReview[] };
export type RecordPartnerOfferScopeReviewInput = { command_id: string; idempotency_key: string; correlation_id: string; review_id: string; comparison_id: string; expected_revision: number; decision: PartnerOfferScopeDecision; rationale: string; offers: PartnerOfferScopeFactInput[] };
export type PartnerOfferLineComparisonDisposition = "LINKED_BY_PATRON" | "DISTINCT_POSITIONS" | "NEEDS_CLARIFICATION";
export type PartnerOfferLineComparisonMember = {
  receipt_event_id: string; partner_id: string; partner_kind: CasePartnerKind; partner_label: string;
  source_locator: string; receipt_is_current: boolean;
  line_locator_state: "UNKNOWN" | "DECLARED"; line_locator: string | null;
  item_reference_state: "UNKNOWN" | "DECLARED"; item_reference: string | null;
  designation_state: "UNKNOWN" | "DECLARED"; designation: string | null;
  unit_state: "UNKNOWN" | "DECLARED"; unit: string | null;
  quantity_state: "UNKNOWN" | "DECLARED"; quantity: string | null;
};
export type PartnerOfferLineComparison = {
  record_id: string; comparison_id: string; revision: number;
  scope_review_id: string; scope_review_revision: number; scope_review_decision: PartnerOfferScopeDecision;
  requires_reassessment: boolean; actor_id: string; recorded_at: string;
  groups: Array<{ group_id: string; disposition: PartnerOfferLineComparisonDisposition; rationale: string; members: PartnerOfferLineComparisonMember[] }>;
};
export type PartnerOfferLineComparisonList = { case_id: string; comparisons: PartnerOfferLineComparison[] };
export type PartnerOfferLineComparisonMemberInput = {
  receipt_event_id: string;
  line_locator_state: "UNKNOWN" | "DECLARED"; line_locator: string | null;
  item_reference_state: "UNKNOWN" | "DECLARED"; item_reference: string | null;
  designation_state: "UNKNOWN" | "DECLARED"; designation: string | null;
  unit_state: "UNKNOWN" | "DECLARED"; unit: string | null;
  quantity_state: "UNKNOWN" | "DECLARED"; quantity: string | null;
};
export type RecordPartnerOfferLineComparisonInput = {
  command_id: string; idempotency_key: string; correlation_id: string | null;
  record_id: string; comparison_id: string; scope_review_id: string; expected_revision: number;
  groups: Array<{
    group_id: string;
    disposition: PartnerOfferLineComparisonDisposition;
    rationale: string;
    members: PartnerOfferLineComparisonMemberInput[];
  }>;
};
export type CaseExecutionCommandReceipt = { status: "SUCCEEDED"; result_code: string; aggregate_refs: Array<{ aggregate_type: string; aggregate_id: string; aggregate_revision: number }>; event_ids: string[]; replayed?: boolean };
export type PostReceptionObligation = {
  obligation_id: string; case_id: string; obligation_type: "OPR" | "TESTS" | "COMMISSIONING" | "TRAINING" | "DOE_DIUO" | "RESERVES_LIFTING" | "GPA" | "INITIAL_MAINTENANCE" | "SPARE_STOCK" | "ON_CALL" | "ADMIN_CLOSURE" | "GUARANTEE_RELEASE";
  origin_reception_act_id: string | null; origin_reception_summary: string | null;
  origin_reception_outcome: ContractReceptionOutcome | "UNKNOWN";
  summary: string; source_refs: string[]; due_date: string | null; resource_note: string | null; cost_estimate_note: string | null; fulfillment_proof_refs: string[]; sanction_ref: string | null;
  status: "REVIEW_REQUIRED" | "IN_PROGRESS" | "FOLLOW_UP_REQUIRED" | "UNKNOWN" | "COMPLETED"; revision: number;
  latest_transition_id: string | null; latest_transition_actor_id: string | null; latest_transition_at: string | null; latest_transition_rationale: string | null; completion_proof_refs: string[];
  actor_id: string; created_at: string;
};

export type ContractExecutionActKind = "WORK_RECEPTION" | "RIGHTS_PRESERVATION" | "CONTRACT_EXIT";
export type ContractReceptionOutcome = "WITH_RESERVATIONS" | "UNDER_RESERVATIONS" | "WITHOUT_RESERVATIONS";
export type ContractInstrumentKind = "SIGNED_CONTRACT" | "AMENDMENT";
export type ContractInstrumentVersion = {
  contract_instrument_version_id: string; case_id: string; instrument_kind: ContractInstrumentKind;
  version_reference: string; source_refs: string[]; evidence_refs: string[]; actor_id: string; recorded_at: string;
};
export type ContractInstrumentSupersession = {
  supersession_id: string; case_id: string;
  replacing_contract_instrument_version_id: string; replacing_instrument_kind: ContractInstrumentKind; replacing_version_reference: string;
  replaced_contract_instrument_version_id: string; replaced_instrument_kind: ContractInstrumentKind; replaced_version_reference: string;
  rationale: string; actor_id: string; recorded_at: string;
};
export type ContractExecutionEvidence = {
  act_id: string; case_id: string; act_kind: ContractExecutionActKind; summary: string;
  reception_outcome: ContractReceptionOutcome | "UNKNOWN";
  source_refs: string[]; evidence_refs: string[]; declared_event_date: string | null;
  case_dce_version_id_at_recording: string | null;
  version_relation: "MATCHES_CASE_CURRENT" | "REVIEW_REQUIRED" | "UNKNOWN";
  contract_instrument_version_relation: "DECLARED" | "REVIEW_REQUIRED" | "UNKNOWN";
  contract_instrument_version_id: string | null;
  contract_instrument_version: Omit<ContractInstrumentVersion, "case_id" | "actor_id" | "recorded_at"> | null;
  actor_id: string; recorded_at: string;
};
export type ContractExecutionEvidenceRequalification = {
  requalification_id: string; case_id: string; act_id: string; act_kind: ContractExecutionActKind;
  act_summary: string; supersession_id: string; review_revision: number;
  decision: "RETAINED_AS_DECLARED" | "RELINKED_TO_DECLARED_VERSION" | "NEEDS_CLARIFICATION";
  resulting_contract_instrument_version_id: string | null;
  resulting_instrument_kind: ContractInstrumentKind | null; resulting_version_reference: string | null;
  rationale: string; actor_id: string; recorded_at: string;
};
export type ContractExecutionEvidenceTimelineInstrumentVersion = {
  contract_instrument_version_id: string; instrument_kind: ContractInstrumentKind;
  version_reference: string; source_refs: string[]; evidence_refs: string[];
};
export type ContractExecutionEvidenceTimelineEvent =
  | {
      event_type: "EXECUTION_EVIDENCE"; event_id: string; case_id: string; revision: 1;
      status: "RECORDED"; status_origin: "HUMAN_ACT"; actor_id: string; recorded_at: string;
      act: {
        act_id: string; act_kind: ContractExecutionActKind; reception_outcome: ContractReceptionOutcome | "UNKNOWN"; summary: string; declared_event_date: string | null;
        source_refs: string[]; evidence_refs: string[]; case_dce_version_id_at_recording: string | null;
        current_dce_relation: "MATCHES_CASE_CURRENT" | "REVIEW_REQUIRED" | "UNKNOWN";
        contract_instrument_version_id: string | null;
        current_instrument_relation: "DECLARED" | "REVIEW_REQUIRED" | "UNKNOWN";
        contract_instrument_version: ContractExecutionEvidenceTimelineInstrumentVersion | null;
      };
    }
  | {
      event_type: "INSTRUMENT_SUPERSESSION"; event_id: string; case_id: string; revision: 1;
      status: "SUPERSEDED"; status_origin: "PATRON_DECLARATION"; actor_id: string; recorded_at: string;
      supersession_id: string; rationale: string;
      replacing: ContractExecutionEvidenceTimelineInstrumentVersion;
      replaced: ContractExecutionEvidenceTimelineInstrumentVersion;
    }
  | {
      event_type: "EVIDENCE_REQUALIFICATION"; event_id: string; case_id: string; revision: number;
      status: "RETAINED_AS_DECLARED" | "RELINKED_TO_DECLARED_VERSION" | "NEEDS_CLARIFICATION";
      status_origin: "PATRON_DECISION"; actor_id: string; recorded_at: string;
      requalification_id: string; act_id: string; supersession_id: string;
      act_kind: ContractExecutionActKind; act_summary: string; act_source_refs: string[]; act_evidence_refs: string[];
      resulting_contract_instrument_version_id: string | null;
      resulting_instrument_kind: ContractInstrumentKind | null; resulting_version_reference: string | null;
      rationale: string;
    };
export type RecordContractExecutionEvidenceInput = {
  command_id: string; idempotency_key: string; act_id: string; act_kind: ContractExecutionActKind;
  reception_outcome: ContractReceptionOutcome | null;
  summary: string; source_refs: string[]; evidence_refs: string[]; declared_event_date: string | null;
  contract_instrument_version_id: string | null;
};
export type RecordContractExecutionEvidenceRequalificationInput = {
  command_id: string; idempotency_key: string; requalification_id: string; act_id: string;
  supersession_id: string; expected_revision: number;
  decision: "RETAINED_AS_DECLARED" | "RELINKED_TO_DECLARED_VERSION" | "NEEDS_CLARIFICATION";
  resulting_contract_instrument_version_id: string | null; rationale: string;
};
export type RecordContractInstrumentVersionInput = {
  command_id: string; idempotency_key: string; contract_instrument_version_id: string;
  instrument_kind: ContractInstrumentKind; version_reference: string;
  source_refs: string[]; evidence_refs: string[];
};
export type DeclareContractInstrumentSupersessionInput = {
  command_id: string; idempotency_key: string; supersession_id: string;
  replacing_contract_instrument_version_id: string; replaced_contract_instrument_version_id: string;
  rationale: string;
};

export type RegisterStructuredRiskInput = {
  risk_id: string;
  dce_version_id: string;
  source_fragment_id: string;
  category: "CCAP" | "CCTP";
  risk_code: string;
  title: string;
  statement: string;
  severity: StructuredRiskSeverity;
  likelihood: StructuredRiskLikelihood;
  source_excerpt: string;
  source_locator: Record<string, unknown>;
  start_byte_offset: number;
  end_byte_offset: number;
  due_at?: string | null;
};

export type StructuredRiskRegistrationResponse = {
  command_id: string;
  idempotency_key: string;
  result_code: "DECISION_RISK_REGISTERED";
  risk_id: string;
  version: number;
  event_ids: string[];
  replayed: boolean;
};

export type DecisionCctpPricingCrossingItem = {
  dce_version_id: string;
  source_fragment_id: string;
  source_locator_label: string;
  source_start_byte_offset: number;
  source_end_byte_offset: number;
  batch_id: string;
  document_kind: string;
  row_number: number;
  code: string | null;
  designation: string | null;
  unit: string | null;
  match_score_bps: number;
  match_basis: string;
  verification_status: string;
};

export type DecisionCctpPricingCrossingResponse = {
  case_id: string;
  items: DecisionCctpPricingCrossingItem[];
};

export type DecisionDocumentContradictionItem = {
  contradiction_id: string;
  dce_version_id: string;
  contradiction_type: string;
  source_fragment_id: string;
  source_locator_label: string;
  source_start_byte_offset: number;
  source_end_byte_offset: number;
  related_batch_id: string;
  related_document_kind: string;
  related_row_number: number;
  related_code: string | null;
  related_designation: string | null;
  related_unit: string | null;
  comparison_basis: string;
  verification_status: string;
};

export type DecisionDocumentContradictionsResponse = {
  case_id: string;
  items: DecisionDocumentContradictionItem[];
};

export type DecisionRiskRequirementLink = {
  link_id: string;
  case_id: string;
  risk_id: string;
  requirement_id: string;
  dce_version_id: string;
  relationship: string;
  rationale: string;
  source_refs: string[];
  created_at: string;
  action_id: string | null;
  action_state: string | null;
  action_severity: string | null;
  action_revision: number | null;
};

export type DecisionRiskRequirementPage = {
  items: DecisionRiskRequirementLink[];
  next_cursor: string | null;
};

export type DecisionPricingReconciliationItem = {
  link_id: string;
  batch_id: string;
  document_kind: string;
  batch_state: string;
  row_number: number;
  code: string | null;
  designation: string | null;
  unit: string | null;
  match_basis: string;
  verification_status: string;
};

export type DecisionPricingReconciliationResponse = {
  link_id: string;
  search: string;
  items: DecisionPricingReconciliationItem[];
};

export type PricingScenario = {
  scenario_id: string;
  case_id: string;
  scenario_key: string;
  scenario_type: string;
  version: number;
  state: "DRAFT" | "SELECTED" | "ARCHIVED";
  assumptions: Record<string, unknown>;
  sales_total_minor: number;
  total_cost_minor: number;
  gross_margin_minor: number;
  gross_margin_rate_bps: number;
  source_snapshot_revision: number;
  source_snapshot_id?: string | null;
  source_basis_state?: "DECLARED_COMPLETE" | "UNKNOWN";
  source_basis_reason?: string | null;
  currency_code?: string | null;
  penalty_reserve_minor?: number;
  retention_reserve_minor?: number;
  guarantee_reserve_minor?: number;
  floor_margin_rate_bps?: number;
  target_margin_rate_bps?: number;
};

export type CreatePricingScenarioInput = {
  command_id: string; idempotency_key: string; correlation_id: string;
  scenario_id: string; source_snapshot_id: string; scenario_key: string;
  scenario_type: "BASE" | "PRUDENT" | "CUSTOM";
  sales_adjustment_bps: number; cost_adjustment_bps: number;
  penalty_reserve_minor: number; retention_reserve_minor: number; guarantee_reserve_minor: number;
  floor_margin_rate_bps: number; target_margin_rate_bps: number;
  assumptions: Record<string, unknown>;
};

export type PricingScenarioStateChangeInput = {
  command_id: string; idempotency_key: string; correlation_id?: string;
  transition_id: string; expected_version: number; reason_code: string;
};

export type PricingScenarioTransitionReceipt = Omit<CommandReceipt, "aggregate_refs" | "result_code"> & {
  result_code: "PRICING_SCENARIO_TRANSITIONED"; scenario_id: string; version: number;
};

export type PricingScenarioCreationReceipt = Omit<CommandReceipt, "aggregate_refs" | "result_code"> & {
  result_code: "PRICING_SCENARIO_CREATED"; scenario_id: string; version: number;
};

export type EnterpriseDocumentKind = "INSURANCE" | "KBIS" | "RIB";

export type EnterpriseDocument = {
  sha256?: string | null;
  document_id: string;
  document_kind: EnterpriseDocumentKind;
  document_label: string;
  issued_at: string;
  expires_at: string | null;
  verification_status: "PENDING" | "VALIDATED" | "EXPIRED" | "REJECTED";
  verification_revision: number;
};

export type EnterpriseCompany = {
  company_id: string;
  aggregate_revision: number;
  legal_name: string;
  trade_name: string | null;
  siren: string;
  siret: string;
  vat_number: string;
  address_line1: string;
  postal_code: string;
  city: string;
  country_code: string;
  documents: EnterpriseDocument[];
};

export type BusinessMethodProfileTerm =
  | "affair"
  | "lot"
  | "owner"
  | "collaborator"
  | "evidence";
export type BusinessMethodProfileAxis =
  | "CONTRACT"
  | "COST"
  | "CASH"
  | "SCHEDULE"
  | "CAPACITY"
  | "PARTNER"
  | "DOCUMENT";
export type BusinessMethodProfileCheck = {
  key: string;
  label: string;
  axis: BusinessMethodProfileAxis;
};
export type BusinessMethodProfileContent = {
  schema_version: 1;
  terminology: Partial<Record<BusinessMethodProfileTerm, string>>;
  additional_checks: BusinessMethodProfileCheck[];
};
export type BusinessMethodProfileVersion = {
  profile_version_id: string;
  version: number;
  schema_version: 1;
  profile: BusinessMethodProfileContent;
  content_sha256: string;
};
export type BusinessMethodProfileVersions = {
  company_id: string;
  versions: BusinessMethodProfileVersion[];
};
export type BusinessMethodProfileAdoption = {
  adoption_id: string;
  case_id: string;
  adoption_revision: number;
  profile_version_id: string;
  profile_version: number;
  profile_content_sha256: string;
};
export type PublishBusinessMethodProfileInput = {
  command_id?: string;
  idempotency_key?: string;
  correlation_id?: string;
  expected_version: number;
  profile: BusinessMethodProfileContent;
};
export type AdoptBusinessMethodProfileInput = {
  command_id?: string;
  idempotency_key?: string;
  correlation_id?: string;
  expected_adoption_revision: number;
  profile_version_id: string;
  profile_version: number;
  profile_content_sha256: string;
};

export type EnterpriseReceipt = CommandReceipt;
export type BusinessMethodProfileReceipt = CommandReceipt;

export type EnterpriseUploadReceipt = {
  upload_id: string;
  state: "CLEAN";
};

export type EnterpriseCompanyInput = {
  legal_name: string;
  trade_name?: string;
  siren: string;
  siret: string;
  vat_number: string;
  address_line1: string;
  postal_code: string;
  city: string;
  country_code: string;
};

export type EnterpriseDocumentUploadInput = {
  document_kind: EnterpriseDocumentKind;
  document_label: string;
  original_filename: string;
  expected_byte_size: number;
  expires_at: string;
};

export type EnterpriseCapabilityKind = "QUALIFICATION" | "REFERENCE" | "EQUIPMENT" | "TEAM" | "METHOD";

export type EnterpriseCapabilityVersion = {
  version_id: string;
  version_number: number;
  title: string;
  description: string;
  valid_from: string;
  valid_until: string | null;
  usage_scope: string;
  proof_document_ids: string[];
};

export type EnterpriseCapability = {
  capability_id: string;
  company_id: string;
  aggregate_revision: number;
  capability_kind: EnterpriseCapabilityKind;
  name: string;
  summary: string;
  state: "ACTIVE" | "SUSPENDED" | "RETIRED";
  versions: EnterpriseCapabilityVersion[];
};

export type EnterpriseCapabilityInput = {
  capability_kind: EnterpriseCapabilityKind;
  name: string;
  summary: string;
  state?: "ACTIVE" | "SUSPENDED" | "RETIRED";
};

export type EnterpriseCapabilityVersionInput = {
  expected_revision: number;
  title: string;
  description: string;
  valid_from: string;
  valid_until?: string;
  usage_scope: string;
  proof_document_ids?: string[];
};

export type EnterpriseDocumentVerificationInput = {
  expected_verification_revision: number;
  outcome: "VALIDATED" | "REJECTED";
  reason_code:
    | "DOCUMENT_ACCEPTED"
    | "DOCUMENT_ILLEGIBLE"
    | "DOCUMENT_EXPIRED"
    | "DOCUMENT_MISMATCH"
    | "DOCUMENT_DUPLICATE";
};

export type PricingImportRow = {
  source_locator?: {sheet:string;row:number;cells:Record<string,string>}|null;
  row_number: number;
  code: string | null;
  designation: string | null;
  unit: string | null;
  quantity_decimal: string | null;
  unit_price_minor: number | null;
  total_minor: number | null;
  errors: string[];
};

export type PricingImportBatchRead = {
  batch_id: string;
  case_id: string;
  document_kind: "DPGF" | "BPU" | "EXCEL";
  state: "PREVIEWED" | "COMMITTED";
  aggregate_revision: number;
  row_count: number;
  valid_row_count: number;
  error_count: number;
  total_minor: number;
  rows: PricingImportRow[];
};

export type PricingImportPreview = PricingImportBatchRead & {
  filename: string;
  truncated: boolean;
  limit_reason: "ROW_LIMIT" | "ERROR_LIMIT" | null;
  result_code: "PRICING_IMPORT_PREVIEWED";
  command_id: string;
  idempotency_key: string;
  event_ids: string[];
  replayed: boolean;
};

export type CommitPricingImportRequest = {
  command_id: string;
  idempotency_key: string;
  correlation_id?: string;
  report_id: string;
  expected_batch_revision: number;
  expected_report_revision: number;
};

export type PricingImportCommitReceipt = {
  status: "SUCCEEDED";
  command_id: string;
  idempotency_key: string;
  result_code: "PRICING_IMPORT_COMMITTED";
  aggregate_refs: Array<{
    aggregate_type: string;
    aggregate_id: string;
    aggregate_revision: number;
  }>;
  event_ids: string[];
  replayed: boolean;
};

export type SubmissionPackageReceipt = CommandReceipt & {
  result_code: "SUBMISSION_PACKAGE_PREPARED";
};

export type SubmissionMode = "FULL" | "CANDIDATURE_ONLY";

export type SubmissionPackageAuthorizationReceipt = CommandReceipt & {
  result_code: "SUBMISSION_PACKAGE_AUTHORIZED";
};

export type SubmissionPackageManifestProjection = {
  submission_package_id: string;
  package_version: number;
  state: "PRET_CONTROLE" | "AUTORISE_DEPOT";
  manifest_sha256: string;
  manifest: Record<string, unknown>;
  authorization_status: "AUTHORIZED" | "NOT_AUTHORIZED";
  external_submission: "NOT_PERFORMED";
};

export type SubmissionEvidenceReceipt = CommandReceipt & {
  result_code: "SUBMISSION_EVIDENCE_RECORDED";
  external_submission: "NOT_PERFORMED";
};

export type SubmissionEvidenceProjection = {
  evidence_id: string;
  submission_package_id: string;
  package_version: number;
  manifest_sha256: string;
  evidence_type: "MANUAL_RECEIPT" | "MANUAL_PORTAL_REFERENCE" | "HUMAN_DEPOSIT_ATTEMPT";
  status: "RECEIVED" | "REJECTED" | "UNKNOWN";
  reconciliation_status: "PARTIAL";
  external_submission: "NOT_PERFORMED";
};

export type SubmissionSignatureReceipt = CommandReceipt & {
  result_code: "SUBMISSION_SIGNATURE_REQUESTED" | "SUBMISSION_SIGNATURE_RECORDED";
  external_submission: "NOT_PERFORMED";
};

export type SubmissionSignatureProjection = {
  signature_id: string;
  submission_package_id: string;
  case_id: string;
  provider: string;
  status: "REQUESTED" | "SIGNED" | "REJECTED";
  expected_package_version: number;
  manifest_sha256: string;
  revision: 1 | 2;
  external_submission: "NOT_PERFORMED";
};

export type DecisionDossierItem = Record<string, unknown>;

export type PreparationReadiness = {
  readiness_id: string;
  revision: number;
  state: "READY" | "READY_WITH_WARNINGS" | "BLOCKED";
  blocker_codes: string[];
  warning_codes: string[];
  checked_requirement_count: number;
  checked_task_count: number;
};

export type GeneratedDocument = {
  content_format?: "MARKDOWN" | "DOCX";
  document_id: string;
  version: number;
  document_kind: "TECHNICAL_RESPONSE" | "DC1" | "DC2" | "DC4";
  state: "GENERATED" | "FAILED_SAFE";
  readiness_revision: number;
};

export type TechnicalResponseDraft = {
  content_format?: "MARKDOWN" | "DOCX";
  content_provenance?: Record<string, unknown> | null;
  draft_id: string;
  version: number;
  state: "DRAFT" | "SUBMITTED_FOR_REVIEW" | "RETURNED_WITH_CORRECTIONS" | "ACCEPTED_CANDIDATE";
  section_codes: string[];
  source_refs: string[];
  responsible_role: "COLLABORATEUR" | "PATRON_REVIEWER";
  content_sha256?: string | null;
  response_plan_id?: string | null;
  response_plan_version?: number | null;
  content?: string | null;
};

export type PreparationPackage = {
  package_id: string;
  case_id: string;
  assignment_id: string;
  dce_version_id: string;
  state: "IN_PREPARATION" | "A_REVIEW" | "READY" | "BLOCKED" | "GENERATED";
  aggregate_revision: number;
  latest_readiness: PreparationReadiness | null;
  generated_documents: GeneratedDocument[];
  response_drafts: TechnicalResponseDraft[];
};

export type CollaboratorTask = {
  task_id: string;
  case_id: string;
  assignment_id: string;
  requirement_id: string | null;
  task_kind: string;
  title: string;
  objective: string;
  priority: "URGENT" | "HIGH" | "NORMAL" | "LOW";
  state: "OPEN" | "CLAIMED" | "IN_PROGRESS" | "BLOCKED" | "COMPLETED" | "NOT_APPLICABLE";
  due_at: string | null;
  aggregate_revision: number;
};

export type CollaboratorTaskList = {
  case_id: string;
  tasks: CollaboratorTask[];
};

export type InformationResponse = {
  response_id: string;
  request_revision: number;
  outcome: "ANSWERED" | "NOT_AVAILABLE" | "NEEDS_CLARIFICATION";
  response_text: string;
  source_locator: string | null;
  created_at: string;
};

export type InformationRequest = {
  request_id: string;
  task_id: string;
  request_kind: "MISSING_SOURCE" | "CLARIFICATION" | "OWNER_CONFIRMATION" | "DEADLINE_CONFIRMATION";
  subject: string;
  question: string;
  requested_object: string;
  reason: string;
  priority: "LOW" | "NORMAL" | "HIGH" | "CRITICAL";
  state: "OPEN" | "ANSWERED" | "CLOSED" | "CANCELLED";
  due_at: string | null;
  aggregate_revision: number;
  responses: InformationResponse[];
};

export type TaskBlocker = {
  blocker_id: string;
  task_id: string;
  task_revision: number;
  blocker_kind: "MISSING_INFORMATION" | "EXTERNAL_DEPENDENCY" | "SOURCE_CONFLICT" | "REVIEW_REQUIRED";
  description: string;
  source_locator: string | null;
  resolution_owner: "COLLABORATEUR" | "PATRON_ADMIN" | "EXTERNAL_PARTY";
  state: "OPEN" | "RESOLVED";
  resolution_note: string | null;
  resolved_at: string | null;
};

export type CollaboratorTaskWorkflow = {
  task_id: string;
  state: CollaboratorTask["state"];
  aggregate_revision: number;
  information_requests: InformationRequest[];
  blockers: TaskBlocker[];
};

export type CreateInformationRequestInput = {
  expected_task_revision: number;
  request_kind: InformationRequest["request_kind"];
  subject: string;
  question: string;
  requested_object: string;
  reason: string;
  priority: InformationRequest["priority"];
  due_at?: string | null;
};

export type RecordInformationResponseInput = {
  expected_revision: number;
  response_text: string;
  source_locator?: string | null;
  outcome: InformationResponse["outcome"];
};

export type DeclareTaskBlockerInput = {
  expected_revision: number;
  blocker_kind: TaskBlocker["blocker_kind"];
  description: string;
  source_locator?: string | null;
  resolution_owner: TaskBlocker["resolution_owner"];
};

export type ResolveTaskBlockerInput = {
  expected_revision: number;
  resolution_note: string;
};

export type PreparationReviewCorrection = {
  correction_id: string;
  review_revision: number;
  revision: number;
  target_document_id: string;
  target_draft_id?: string | null;
  target_draft_version?: number | null;
  target_content_sha256?: string | null;
  correction_code: "SOURCE_MISSING" | "SOURCE_WRONG" | "SECTION_INCOMPLETE" | "WORDING_UNCLEAR";
  instruction: string;
  source_locator: string | null;
};

export type PreparationReview = {
  review_id: string;
  package_id: string;
  target_document_id: string;
  target_version: number;
  target_draft_id?: string | null;
  target_draft_version?: number | null;
  target_content_sha256?: string | null;
  revision: number;
  state: "REQUESTED" | "ACCEPTED" | "RETURNED_WITH_CORRECTIONS" | "REJECTED";
  decision_code: "ACCEPTED" | "CORRECTIONS_REQUIRED" | "REJECTED" | null;
  decision_note: string | null;
  corrections: PreparationReviewCorrection[];
};

export type PreparationReviewList = {
  package_id: string;
  reviews: PreparationReview[];
};

export type PreparationResponseDraftList = {
  package_id: string;
  package_revision?: number;
  drafts: TechnicalResponseDraft[];
};

export type PreparationTransmissionDelivery = {
  snapshot_id: string;
  snapshot_version: number;
  snapshot_state: "READY_FOR_PATRON_REVIEW";
  snapshot_created_at: string;
  snapshot_manifest_sha256: string;
  snapshot_manifest: Record<string, unknown>;
  snapshot_receipt: PreparationStoredCommandReceipt;
  transmission_id: string;
  transmission_state: "TRANSMITTED_TO_PATRON";
  transmitted_at: string;
  transmission_receipt: PreparationStoredCommandReceipt;
};

export type PreparationStoredCommandReceipt = {
  status: "SUCCEEDED";
  command_id: string;
  idempotency_key: string;
  result_code: "PREPARATION_SNAPSHOT_CREATED" | "PREPARATION_TRANSMITTED_TO_PATRON";
  aggregate_refs: Array<{
    aggregate_type: string;
    aggregate_id: string;
    aggregate_revision: number;
  }>;
  event_ids: string[];
};

export type PreparationTransmissionList = {
  package_id: string;
  deliveries: PreparationTransmissionDelivery[];
};

export type PreparationResponsePlanSection =
  | "COVER"
  | "UNDERSTANDING"
  | "METHOD"
  | "RESOURCES"
  | "SCHEDULE"
  | "RISKS"
  | "SOURCES";

export type PreparationResponsePlanItem = {
  requirement_id: string;
  requirement_state: "CONFIRMED" | "REVIEW_REQUIRED" | "NOT_APPLICABLE" | "UNKNOWN";
  section_code: PreparationResponsePlanSection;
  source_proposal_id: string | null;
  source_capability_version_id: string | null;
  source_validity_state: "CURRENT" | "EXPIRED" | "UNKNOWN";
  source_evidence_state: "CURRENT" | "EXPIRED" | "UNKNOWN";
};

export type PreparationResponsePlan = {
  plan_id: string;
  version: number;
  package_id: string;
  dce_version_id: string;
  state: "UNKNOWN" | "SOURCES_CURRENT";
  plan_sha256: string;
  content: {
    schema_version: 1;
    case_id: string;
    package_id: string;
    dce_version_id: string;
    items: PreparationResponsePlanItem[];
  };
};

export type PreparationResponsePlanList = {
  package_id: string;
  plans: PreparationResponsePlan[];
};

export type CreatePreparationResponsePlanInput = {
  command_id: string;
  idempotency_key: string;
  correlation_id: string;
  plan_id: string;
  expected_package_revision: number;
  items: Array<{
    requirement_id: string;
    section_code: PreparationResponsePlanSection;
    source_proposal_id: string | null;
  }>;
};

export type RequestPreparationReviewInput = {
  expected_package_revision: number;
  target_document_id?: string | null;
  target_version?: number | null;
  target_draft_id?: string;
  target_draft_version?: number;
  target_content_sha256?: string;
};

export type DecidePreparationReviewInput = {
  expected_review_revision: number;
  review_id: string;
  target_document_id?: string | null;
  target_draft_id?: string | null;
  target_draft_version?: number | null;
  target_content_sha256?: string | null;
  decision_code: PreparationReview["decision_code"] & string;
  decision_note?: string | null;
};

export type AddPreparationCorrectionInput = {
  review_id: string;
  target_document_id?: string | null;
  target_draft_id?: string | null;
  target_draft_version?: number | null;
  target_content_sha256?: string | null;
  correction_code: PreparationReviewCorrection["correction_code"];
  instruction: string;
  source_locator?: string | null;
  corrected_content?: string | null;
};

export type ResponseContribution = {
  requirement_id: string;
  section_code: PreparationResponsePlanSection;
  content: string;
  missing: string;
};

export type CreateTechnicalResponseDraftInput = {
  contributions?: ResponseContribution[];
  expected_package_revision: number;
  source_document_id: string;
  section_codes: string[];
  source_refs: string[];
  command_id?: string;
  idempotency_key?: string;
  correlation_id?: string;
  draft_id?: string;
};

export type TotpEnrollment = {
  factor_id: string;
  otpauth_uri: string;
  recovery_codes: string[];
  expires_at: string;
};

export type TotpStepUpResponse = {
  access_token: string;
  token_type: "Bearer";
  expires_in: number;
  used_recovery_code: boolean;
};

export type BackendReadiness = {
  status: "ok" | "not_ready";
  service: "smart-ao-v8";
  checks: {
    database: "unknown" | "ok" | "failed";
    schema: "unknown" | "ok" | "failed";
    clamav: "unknown" | "ok" | "failed";
  };
};


export type AuthSession = {
  access_token: string;
  token_type: "Bearer";
  expires_in: number;
};

export type ActorKind = "PATRON_ADMIN" | "PATRON_DELEGATE" | "COLLABORATEUR";
export type MembershipState = "ACTIVE" | "SUSPENDED" | "REVOKED";
export type OperationalProfile = "RESPONSABLE" | "EXPERT";

export type CurrentActor = {
  actor_id: string;
  identity_id: string;
  tenant_slug: string;
  actor_kind: ActorKind;
  operational_profile: OperationalProfile | null;
  membership_state: MembershipState;
  mfa_verified: boolean;
};


export type BoampObservation = {
  observation_id: string;
  source_notice_id: string;
  title: string | null;
  observed_at: string;
  publication_date: string | null;
  response_deadline: string | null;
  department_codes: string[];
  market_types: string[];
  source_status: string | null;
  score_version: string;
  score: number;
  score_explanation: Record<string, unknown>;
  fingerprint_sha256: string;
  p0_state: "UNREVIEWED" | "TARGETED" | "SNOOZED" | "DISCARDED";
  p0_decision: BoampQualificationDecision | null;
  p0_reason_code: BoampQualificationReason | null;
  p0_qualification_id: string | null;
  p0_decided_at: string | null;
  p1_state: "NOT_OPEN" | "OPEN_WITH_UNKNOWNS";
  p1_case_id: string | null;
  p1_opened_at: string | null;
  lot_scope_state: "UNKNOWN" | "IDENTIFIED" | "CONFLICTING" | "NOT_APPLICABLE";
  lot_references: string[];
  lot_scope_source: string | null;
  deadline_state: "KNOWN" | "MISSING" | "EXPIRED" | "CONFLICTING";
  deadline_source: string | null;
  deadline_source_timezone: string | null;
  deadline_normalized_timezone: "UTC" | null;
  source_captures: BoampSourceCapture[];
  unknowns: Array<{
    code: "LOT_SCOPE" | "DCE_NOT_RECEIVED" | "DEADLINE_MISSING" | "DEADLINE_CONFLICT";
    missing: string;
    why_it_matters: string;
    possible_impact: string;
    responsible: string | null;
    next_action: string;
    due_at: string | null;
    state: "OPEN";
    source_ref: string;
  }>;
};

export type BoampSourceCapture = {
  ingestion_run_id: string;
  source_mode: "LIVE" | "REPLAY";
  run_recorded_at: string;
  source_contract_version: string | null;
  source_response_sha256: string | null;
};

export type BoampSourceStatus = {
  source: "BOAMP";
  state: "AVAILABLE" | "UNAVAILABLE" | "UNKNOWN";
  checked_at: string;
  last_success_at: string | null;
  retryable: boolean;
  manual_entry_available: boolean;
};

export type BoampQualificationDecision = "QUALIFIED" | "REJECTED" | "SNOOZED";
export type BoampQualificationReason =
  | "RELEVANT_PUBLIC_SIGNAL"
  | "NOT_RELEVANT"
  | "INSUFFICIENT_PUBLIC_DATA"
  | "EXPIRED";

export type BoampQualificationInput = {
  command_id?: string;
  idempotency_key?: string;
  correlation_id?: string;
  decision: BoampQualificationDecision;
  reason_code: BoampQualificationReason;
};

export type BoampQualificationReceipt = {
  qualification_id: string;
  event_id: string;
  replayed: boolean;
};

export type BoampQualificationForm = {
  decision: BoampQualificationDecision;
  reason_code: BoampQualificationReason;
};

export type BoampOpportunity = BoampObservation;


export type DceCoverageException = {
  observation_id: string;
  kind: "ARCHIVE_ENTRY" | "DECLARED_MISSING";
  state: "EXCLUDED_COMPRESSION" | "NOT_EXTRACTED" | "NESTED_ARCHIVE" | "DIRECTORY" | "EXCLUDED_UNSAFE" | "EXCLUDED_SYMLINK" | "EXCLUDED_ENCRYPTED" | "EXCLUDED_LIMIT" | "UNREADABLE" | "INVENTORY_LIMIT" | "DECLARED_MISSING";
  document_id: string | null;
  extraction_id: string | null;
  entry_path: number[];
  document_family: string;
  source_state: "RESOLVED" | "UNKNOWN";
  lot_applicability: "UNKNOWN";
  criticality: "UNKNOWN";
};

export type DceAnnouncementAnchor = {
  fragment_id: string;
  fragment_ordinal: number;
  locator_label: string;
  part: number;
  kind: "HEADING" | "BRIDGE" | "SOURCE";
  start_byte_offset: number;
  end_byte_offset: number;
};

export type DceDocumentAnnouncement = {
  candidate_id: string;
  document_family: string;
  claim: "PROVIDED_SIGNAL" | "NOT_PROVIDED_SIGNAL" | "SUBMISSION_SIGNAL" | "NOT_REQUIRED_SIGNAL" | "PROHIBITED_SUBMISSION_SIGNAL" | "AMBIGUOUS";
  lot_numbers: number[];
  source_document_id: string;
  source_extraction_id: string;
  source_fragment_id: string;
  source_locator_label: string;
  source_locator_state: "RESOLVED" | "UNKNOWN";
  start_byte_offset: number;
  end_byte_offset: number;
  context_fragment_id?: string | null;
  context_locator_label?: string | null;
  context_start_byte_offset: number | null;
  context_end_byte_offset: number | null;
  family_candidate_document_ids: string[];
  presence_status: "UNKNOWN";
  applicability: "UNKNOWN";
  criticality: "UNKNOWN";
  conflict_state: "UNKNOWN" | "CONFLICTING_CANDIDATES";
  rule_version: "1" | "2" | "3";
  anchor_chain?: DceAnnouncementAnchor[];
};

export type DceDocumentCoverage = {
  announcements?: DceDocumentAnnouncement[];
  announcement_scan_state?: "UNKNOWN" | "CANDIDATES_ONLY" | "REVIEW_REQUIRED" | "REJECTED_LIMIT";
  exceptions?: DceCoverageException[];
  case_scope_kind: string;
  documents: Array<{
    document_id: string;
    extraction_id: string | null;
    document_family: string;
    extraction_status: "NOT_STARTED" | "COMPLETED" | "REVIEW_REQUIRED" | "UNSUPPORTED" | "REJECTED_LIMIT" | "FAILED_SAFE";
  }>;
  total_documents: number;
  completed_extractions: number;
  unread_documents: number;
  inventory_scope: "ADMITTED_DOCUMENTS_ONLY";
  inventory_completeness: "UNKNOWN";
  lot_applicability: "UNKNOWN";
  critical_unread_documents: null;
  status: "REVIEW_REQUIRED";
  analysis_complete: false;
};

export type CaseDceReading = {
  coverage?: DceDocumentCoverage | null;
  case_id: string;
  work_label: string;
  case_lifecycle: string;
  commercial_stage: string;
  dce_freshness: string;
  availability: "AVAILABLE";
  dce: {
    dce_version_id: string;
    lifecycle: string;
    integrity: string;
    classification_readiness: string;
    analysis_readiness: string;
    source_received_at: string;
  };
  counters: {
    total: number;
    pending_human_confirmation: number;
    confirmed: number;
    review_required: number;
    not_applicable: number;
  };
  requirements: Array<{
    requirement_id: string;
    confirmation_revision: number | null;
    requirement_type: string;
    directive_signal: string;
    confirmation_outcome: string;
    uncertainty_status: string;
    document_family: string;
    source_locator_label: string;
    source_anchor: DceSourceAnchor | null;
    structured_candidate?: DceStructuredRequirementCandidate | null;
  }>;
};

export type DceStructuredRequirementCandidate = {
  projector_version: "1";
  state: "UNKNOWN" | "CANDIDATES_ONLY" | "REVIEW_REQUIRED";
  reason_code: string;
  source_fragment_id: string | null;
  documents: Array<"DC1" | "DC2" | "DC4" | "DUME" | "MEMOIRE_TECHNIQUE" | "AE" | "BPU" | "DPGF">;
  document_state: "CANDIDATE" | "UNKNOWN";
  date_iso: string | null;
  date_state: "CANDIDATE" | "UNKNOWN";
  time_local: string | null;
  time_state: "CANDIDATE" | "UNKNOWN";
  timezone: string | null;
  timezone_state: "CANDIDATE" | "UNKNOWN";
  lot_numbers: number[];
  lot_state: "CANDIDATE" | "UNKNOWN";
  applicability: "UNKNOWN";
  evidence: Array<{
    field: "DOCUMENT" | "DATE" | "TIME" | "TIMEZONE" | "LOT";
    value: string;
    start_byte_offset: number;
    end_byte_offset: number;
  }>;
};

export type DceSourceAnchor = {
  source_anchor_id: string;
  dce_version_id: string;
  dce_document_id: string;
  extraction_id: string;
  fragment_ordinal: number;
  source_sha256: string;
  extractor_id: string;
  extractor_version: string;
  fragment_sha256: string;
  locator_state: "RESOLVED" | "UNKNOWN";
  locator: {
    kind:
      | "pdf_page"
      | "pymupdf_block"
      | "ocr_page"
      | "docx_paragraph"
      | "docx_table_cell"
      | "xlsx_cell"
      | "text_line"
      | "docling_markdown";
    coordinates: Record<string, unknown>;
  } | null;
};

export type KnowledgeSearchResult = {
  source_fragment_id: string;
  dce_version_id: string;
  score: number;
  locator: Record<string, unknown>;
  embedding_model: string;
};

export type KnowledgeSearchResponse = {
  case_id: string;
  query: string;
  results: KnowledgeSearchResult[];
};

export type ConsultationProjection = {
  id: string;
  buyer_legal_name: string;
  external_reference: string;
  object_label: string;
  location_label: string;
  lifecycle: string;
  freshness: string;
  aggregate_revision: number;
  lots: string[];
  tranches: string[];
  projection_status: string;
};

export type DceStagingPreparationReceipt = {
  status: "SUCCEEDED";
  command_id: string;
  idempotency_key: string;
  result_code: "DCE_STAGING_PREPARED";
  aggregate_refs: CommandReceipt["aggregate_refs"];
  event_ids: string[];
  staging: {
    storage_object_id: string;
    state: "AWAITING_UPLOAD";
    expires_at: string;
  };
  replayed: boolean;
};

export type DceUploadReceipt = {
  storage_object_id: string;
  state: "CLEAN";
};

export type RegisterDceVersionReceipt = CommandReceipt & {
  result_code: "DCE_VERSION_REGISTERED";
};

export type DceVersionMetadata = {
  id: string;
  consultation_id: string;
  predecessor_dce_version_id: string | null;
  source_received_at: string;
  lifecycle: string;
  integrity: string;
  classification_readiness: string;
  analysis_readiness: string;
  aggregate_revision: number;
};

export type DceDocumentProcessingState =
  | "RECEIVED"
  | "READ"
  | "REVIEW_REQUIRED"
  | "UNSUPPORTED"
  | "LIMIT_REACHED"
  | "PROTECTED"
  | "UNREADABLE";

export type DceDocumentInventoryItem = {
  document_id: string;
  original_filename: string;
  media_type: string;
  byte_size: number;
  received_from: string;
  processing_state: DceDocumentProcessingState;
  issue_code: string | null;
};

export type DceDocumentInventory = {
  dce_version_id: string;
  items: DceDocumentInventoryItem[];
};

export type LinkCaseDceVersionInput = {
  command_id?: string;
  idempotency_key?: string;
  correlation_id?: string;
  dce_version_id: string;
  expected_case_revision?: number;
  reason: string;
};

export type LinkCaseDceVersionReceipt = CommandReceipt & {
  result_code: "CASE_DCE_APPLICABILITY_SET";
};

export type DceProvenanceChannel =
  | "BUYER_PLATFORM"
  | "EMAIL"
  | "MANUAL_UPLOAD"
  | "RECTIFICATION";

export type PrepareDceStagingInput = {
  command_id?: string;
  idempotency_key?: string;
  correlation_id?: string | null;
  consultation_id: string;
  consultation_revision: number;
  original_filename: string;
  expected_byte_size: number;
  source_channel: DceProvenanceChannel;
  expires_at: string;
};

export type RegisterDceVersionInput = {
  predecessor_dce_version_id?: string;
  expected_predecessor_revision?: number;
  replacement_reason?: string;
  command_id?: string;
  idempotency_key?: string;
  correlation_id?: string;
  dce_version_id: string;
  consultation_id: string;
  consultation_revision: number;
  corpus_hash: string;
  provenance_channel: DceProvenanceChannel;
  provenance_reference?: string;
  provenance_url?: string;
  source_received_at: string;
  documents: Array<{ document_id: string; storage_object_id: string }>;
};


export type CapabilityProposal = {
  proposal_id: string;
  case_id: string;
  assignment_id: string;
  capability_id: string;
  capability_version_id: string;
  requirement_id: string | null;
  task_id: string | null;
  state: "PROPOSED" | "TO_REVIEW";
  validity_state: "CURRENT" | "EXPIRED" | "UNKNOWN";
  justification: string;
  source_locator: string | null;
  source_evidence_state: "CURRENT" | "EXPIRED" | "UNKNOWN";
  source_evidence_evaluated_at: string | null;
};

export type CapabilityAssessments = {
  proposals: CapabilityProposal[];
  gaps: unknown[];
};


export type CapabilityCandidate = {
  capability_id: string;
  capability_kind: "QUALIFICATION" | "REFERENCE" | "EQUIPMENT" | "TEAM" | "METHOD";
  name: string;
  version_id: string;
  version_number: number;
  title: string;
  valid_from: string;
  valid_until: string | null;
  validity_state: "CURRENT" | "EXPIRED";
  source_evidence_state: "CURRENT" | "EXPIRED" | "UNKNOWN";
  evaluated_at: string | null;
};

export type ProposeCapabilityInput = {
  command_id: string;
  idempotency_key: string;
  correlation_id: string;
  capability_id: string;
  capability_version_id: string;
  requirement_id?: string | null;
  task_id?: string | null;
  justification: string;
  assignment_id?: string;
};


export const analysisAxisCodes = ["COMMERCIAL", "CANDIDATURE", "TECHNICAL", "CONSTRUCTIBILITY", "CONTRACT", "PRICE", "CASH", "CAPACITY", "PARTNERS", "HSE", "DOCUMENTS", "RIGHTS"] as const;
export type CaseAnalysisFollowUp = {
  risk_requirement_link_id?: string | null;
  contract_impact_id?: string | null;
  contract_impact_revision?: number | null;
  decision_id?: string | null;
  context_id?: string | null;
  kind: "ACTION" | "CONTRACT_IMPACT" | "CONDITION";
  record_id: string;
  revision: number;
  state: string;
  relation_id: string | null;
  risk_id: string | null;
  requirement_id: string | null;
  description: string;
  consequence: string | null;
  responsible_actor_id: string | null;
  due_at: string | null;
  scope: "EXACT_RECORDED_RELATION";
};
export type AnalysisTreatment = {
 hypotheses?:string|null;
 axis_code: typeof analysisAxisCodes[number];
 applicability: "APPLIES"|"NOT_APPLICABLE"|"UNKNOWN";
 applicability_reason:string;
 consequences:Record<"technical"|"price"|"delay"|"cash"|"contract",string|null>;
 unknown_reason:string|null; action:string; responsible:"SELF";due_at:string|null;
};
export type DossierAxisReview={code:typeof analysisAxisCodes[number];state:"POINTS_REVIEWED"|"UNKNOWN";note:string;follow_up:string|null;responsible:"SELF"};
export type AnalysisDossierInput={command_id:string;idempotency_key:string;review_id:string;expected_revision:number;dossier_sha256:string;phase:"PREPARED"|"REVIEWED";axes:DossierAxisReview[];justification:string;human_confirmed:true};
export type AnalysisDossierReceipt={review_id:string;revision:number;command_id:string;idempotency_key:string;replayed:boolean};
export type AnalysisDossierReview={review_id:string;revision:number;phase:"PREPARED"|"REVIEWED";state:"CURRENT"|"REVIEW_REQUIRED";dossier_sha256:string;actor_id:string|null;created_at:string;axes:DossierAxisReview[];justification:string|null};
export type AnalysisAssessmentInput = {
 treatment?:AnalysisTreatment|null;
 command_id:string;idempotency_key:string;assessment_id:string;point_kind:"REQUIREMENT"|"RISK";point_id:string;expected_revision:number;source_context_sha256:string;expected_evidence_state:"DECLARED"|"UNKNOWN";expected_evidence:string|null;residual_risk_state:"DECLARED"|"UNKNOWN";residual_risk:string|null;unknown_reason:string|null;justification:string;human_confirmed:true;
};
export type AnalysisAssessmentReceipt={assessment_id:string;revision:number;command_id:string;idempotency_key:string;replayed:boolean};
export type HumanAnalysisAssessment={treatment?:AnalysisTreatment|null;assessment_id:string;revision:number;previous_assessment_id:string|null;state:"CURRENT"|"REVIEW_REQUIRED";source_context_sha256:string;actor_id:string|null;created_at:string;expected_evidence_state:"DECLARED"|"UNKNOWN";expected_evidence:string|null;residual_risk_state:"DECLARED"|"UNKNOWN";residual_risk:string|null;unknown_reason:string|null;justification:string|null};
export type CaseAnalysisItem = {
  table_context?: {state:"EXACT_SOURCE"|"UNKNOWN"; applicability:"UNKNOWN"; unknown_reason:"SOURCE_UNPROVEN"|"READ_BUDGET_EXCEEDED"|null; cells:{text:string;source_anchor:NonNullable<CaseDceReading["requirements"][number]["source_anchor"]>}[]}|null;
  native_revision?:number;
  source_context_sha256?:string|null;
  human_assessment?:HumanAnalysisAssessment|null;
  source_excerpt?: string | null;
  source_excerpt_state?: "EXACT_SOURCE" | "UNKNOWN";
  source_excerpt_unknown_reason?: "SOURCE_UNPROVEN" | "READ_BUDGET_EXCEEDED" | null;
  severity?: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL" | "UNKNOWN";
  expected_evidence?: "UNKNOWN";
  residual_risk?: "UNKNOWN";
  item_id: string;
  kind: "REQUIREMENT" | "RISK";
  native_type: string;
  native_state: string;
  title: string | null;
  source_state: "CURRENT_SOURCE" | "UNKNOWN";
  start_byte_offset: number | null;
  end_byte_offset: number | null;
  source_anchor: NonNullable<CaseDceReading["requirements"][number]["source_anchor"]> | null;
  lot_numbers: number[];
  lot_state: "CANDIDATE" | "UNKNOWN";
  applicability: "UNKNOWN";
  responsible: null;
  action: null;
  consequences: "UNKNOWN";
  follow_ups?: CaseAnalysisFollowUp[];
  follow_up_state?: "RECORDED" | "UNKNOWN";
};
export type AnalysisPricingScenario = {
  scenario_id: string;
  revision: number;
  state: "RECORDED" | "UNKNOWN";
  unknown_reason: string | null;
  dce_applicability: "UNKNOWN";
  details: PricingScenario | null;
};
export type AnalysisCashReport = {
  report_id: string;
  revision: number;
  state: "DECLARED" | "UNKNOWN";
  unknown_reason: string | null;
  schedule_state: "UNKNOWN";
  funding_peak_state: "UNKNOWN";
  scope_state: "UNKNOWN";
  details: {
    case_id: string;
    currency_code: string;
    calculated_at: string;
    ruleset_version: number;
    forecast_cashflow_minor: number;
    lines: {line_id: string; label: string; amount_minor: number}[];
  } | null;
};
export type AnalysisDossierHistoryPage={case_id:string;entries:(Omit<AnalysisDossierReview,"state">&{state:"HISTORICAL";dce_version_id:string;snapshot:CaseAnalysisSummary})[];next_before_revision:number|null};
export type CaseAnalysisSummary = {
 dossier_sha256?:string|null;
 case_scope_fingerprint?:string|null;
 dossier_review?:AnalysisDossierReview|null;
  case_id: string;
  dce_version_id: string;
  case_scope_kind: "SINGLE_LOT" | "MULTI_LOT" | "TRANCHE" | "VARIANT" | "CUSTOM";
  status: "REVIEW_REQUIRED";
  analysis_complete: false;
  coverage_scope: "CURRENT_DCE_ONLY";
  source_context_state: "CURRENT" | "REVIEW_REQUIRED" | "UNKNOWN";
  truncated: boolean;
  coverage: NonNullable<CaseDceReading["coverage"]> | null;
  axes: {code: typeof analysisAxisCodes[number]; label: string; status: "NON_EVALUATED" | "REVIEW_REQUIRED"; mapping_basis: "NATIVE_REGISTER_TYPE_ONLY"; items: CaseAnalysisItem[]; pricing_scenarios?: AnalysisPricingScenario[]; cash_reports?: AnalysisCashReport[]; capacity_plans?:AnalysisCapacityPlan[]}[];
};

export type PositionCostSource={line_id:string;report_id:string;report_revision:number;report_state:string;category:string;label:string;quantity_decimal:string;unit:string;amount_minor:string;currency_code:string;allocated_amount_minor?:string;allocation_summary?:{state:"DECLARED"|"UNKNOWN";allocated_amount_minor:string|null;remaining_amount_minor:string|null;explicit_reference_count:number;unresolved_reference_count:number}};
export type PositionRequirementSource={requirement_id:string;revision:number;native_type:string;source_context_sha256:string;source_anchor:NonNullable<CaseDceReading["requirements"][number]["source_anchor"]>;excerpt:string|null;start_byte_offset:number|null;end_byte_offset:number|null;applicability:"UNKNOWN"};
export type PositionOfferSource={price_id:string;revision:number;receipt_event_id:string;receipt_revision:number;partner_id:string;partner_label:string;source_locator:string;amount_as_declared:string;currency_code:string;valid_until:string|null;exclusions_state:"UNKNOWN"|"DECLARED";exclusions:string[]};
export type PositionScopeSource={review_id:string;revision:number;comparison_id:string;decision:string;receipt_event_id:string;transport_state:string;transport_note:string|null;exclusions_review_state:string};
export type PricingPositionImportSource=Omit<PricingImportRow,"total_minor"|"unit_price_minor"|"code">&{position_id:string;batch_id:string;batch_revision:number;total_minor:string|null};
export type PricingPosition={import_origin?:{state:"MATCHED_BY_HASH"|"UNKNOWN";document_id:string|null;dce_version_id:string|null;filename:string|null;reason:string|null};position_id:string;source_state:"CURRENT_SOURCE"|"UNKNOWN";position_context_sha256:string;import_source:PricingPositionImportSource;review_id:string|null;revision:number;actor_id:string|null;created_at:string|null;justification:string|null;state:"CURRENT"|"REVIEW_REQUIRED";cost_state:"DECLARED"|"UNKNOWN";declared_cost_minor:string|null;currency_code:string|null;coverage_state:"UNKNOWN";applicability:"UNKNOWN";costs:PositionCostSource[];requirement:PositionRequirementSource|null;offer:PositionOfferSource|null;scope:PositionScopeSource|null;limitations:string[]};
export type PricingPositions={case_id:string;batch_id:string;dce_version_id:string|null;coverage_state:"UNKNOWN";positions:PricingPosition[];offset:number;next_offset:number|null;sources:{costs:PositionCostSource[];requirements:PositionRequirementSource[];offers:PositionOfferSource[];scopes:PositionScopeSource[]};sources_limited:{costs:boolean;requirements:boolean;offers:boolean;scopes:boolean}};
export type PositionReviewInput={command_id:string;idempotency_key:string;record_id:string;expected_revision:number;position_context_sha256:string;requirement_id:string|null;requirement_revision:number|null;cost_refs:{line_id:string;report_revision:number;allocated_amount_minor?:string}[];offer_price_id:string|null;offer_price_revision:number|null;scope_review_id:string|null;justification:string;human_confirmed:true};
export type PositionReviewReceipt={record_id:string;position_id:string;revision:number;command_id:string;idempotency_key:string;replayed:boolean};
export type PositionHistory={case_id:string;batch_id:string;position_id:string;entries:{record_id:string;revision:number;previous_id:string|null;state:"HISTORICAL"|"UNPROVEN";created_at:string;actor_id:string|null;justification:string|null;snapshot:{import:PricingPositionImportSource;costs:PositionCostSource[];requirement:PositionRequirementSource|null;offer:PositionOfferSource|null;scope:PositionScopeSource|null}|null}[];next_before_revision:number|null};

export type OperationalChangeConsent={human_confirmed:true;justification:string;publish:boolean};
export type OperationalChangeContext=OperationalChangeConsent&{expected_view_sha256:string;point_ids:string[]};
export type OperationalActionDetails=OperationalChangeConsent&{responsible?:string|null;expected_evidence?:string|null};
export type StoredOperationalChangeContext=OperationalChangeContext&{handover_snapshot_id:string;handover_revision?:number;offer_manifest_sha256?:string;points:HandoverOperationalPoint[];recorded_at:string};

export type OperationalChangeView={event_id:string;case_id:string;source_refs?:string[];evidence_refs?:string[];summary:string;scope_note:string;change_kind:string;lot_reference:string;source_state:string;source_reasons:string[];operational_context:StoredOperationalChangeContext;current_operational_context?:StoredOperationalChangeContext|null;legal_effect_state:"UNKNOWN";applicability_history:{review_id:string;decision:string;delta_state:string;delta_note:string|null;source_state:string}[];actions:{action_id:string;summary:string;source_state:string;operational_details:OperationalActionDetails;due_at:string|null}[];action_execution_acts:{act_id:string;action_id:string;declared_state:string;declared_summary:string|null;evidence_retrieval_state:string}[];operational_timeline:{kind:string;record_id:string;recorded_at:string;source_state?:string}[]};

export type AnalysisCapacityPlan={run_id:string;revision:number;input_sha256:string;state:'RECORDED'|'REVIEW_REQUIRED';unknown_reason:string|null;lot_state:'UNKNOWN';dce_applicability:'UNKNOWN';details:{case_id:string;status:string;inputs:CapacityRun['inputs'];result:CapacityRun['result'];reservation_state:'NOT_RESERVED';coverage_state:'UNKNOWN'}|null};


export type BuyerDocxFieldMapping = {locator:string;expected_xml_sha256:string;requirement_id:string;section_code:PreparationResponsePlanSection};
export type BuyerDocxTemplateReference = {document_id:string;dce_version_id:string;sha256:string};
export type BuyerDocxInputs = {package_id:string;package_revision:number;source_response:SelectedResponseDraft;
  contributions:Array<{requirement_id:string;section_code:PreparationResponsePlanSection;text:string|null;missing:string;start_byte:number;end_byte:number;raw_sha256:string}>;
  templates:Array<{template:BuyerDocxTemplateReference;filename:string;state:"CANDIDATE"|"REVIEW_REQUIRED";reason:string|null;regions:Array<{locator:string;xml_sha256:string;text:string}>}>;truncated:boolean};
export type CreateBuyerDocxResponseDraftInput = {command_id:string;idempotency_key:string;correlation_id?:string;draft_id:string;expected_package_revision:number;source_response:SelectedResponseDraft;template:BuyerDocxTemplateReference;fields:BuyerDocxFieldMapping[]};

export type SubmissionFinalControl = {
  pricing_reference?: {
    state: 'CURRENT' | 'REVIEW_REQUIRED' | 'UNKNOWN' | 'NOT_APPLICABLE';
    referenced: {report_id: string; revision: number} | null;
    latest_published: {report_id: string; revision: number} | null;
    reason_code: 'REFERENCE_NOT_VERIFIED' | 'LATEST_PUBLISHED_REFERENCE' | 'NEWER_PUBLISHED_REPORT' | 'CANDIDATURE_ONLY';
  };
  submission_package_id: string;
  package_version: number;
  manifest_sha256: string;
  dce_version_id: string;
  state: 'PARTIAL' | 'REVIEW_REQUIRED' | 'UNKNOWN';
  source_state: 'CURRENT' | 'REVIEW_REQUIRED' | 'UNKNOWN';
  local_delivery_mode?: 'LOCAL_ZIP' | 'UNKNOWN';
  buyer_formats_state?: 'OBSERVATIONS_AVAILABLE' | 'UNKNOWN';
  buyer_names_sizes_state?: 'OBSERVATIONS_AVAILABLE' | 'UNKNOWN';
  name_size_comparisons?: Array<{
    requirement_id: string; source_excerpt: string | null; source_locator: string;
    source_anchor: Record<string, unknown> | null; confirmation: string;
    scope: 'TECHNICAL_RESPONSE' | 'KBIS' | 'KNOWN_DOCUMENT_FILES' | 'UNSPECIFIED';
    criterion: 'EXACT_NAME' | 'NO_WHITESPACE' | 'MAX_BYTES' | 'UNKNOWN';
    requested_name: string | null; max_bytes: number | null;
    files: SubmissionFinalControl['files'];
    state: 'OBSERVED_MATCH' | 'OBSERVED_MISMATCH' | 'UNKNOWN'; reason_code: string;
    applicability: 'UNKNOWN'; conformity: 'UNKNOWN';
  }>;
  format_comparisons?: Array<{
    requirement_id: string; source_excerpt: string | null; source_locator: string;
    source_anchor: Record<string,unknown> | null; confirmation: string;
    scope: 'TECHNICAL_RESPONSE' | 'KBIS' | 'DELIVERY' | 'UNSPECIFIED';
    requested: 'PDF' | 'DOCX' | 'PNG' | 'ZIP' | 'NO_ZIP' | 'INDIVIDUAL_FILES' | 'UNKNOWN';
    files: SubmissionFinalControl['files'];
    state: 'OBSERVED_MATCH' | 'OBSERVED_MISMATCH' | 'UNKNOWN'; reason_code: string;
    applicability: 'UNKNOWN'; conformity: 'UNKNOWN';
  }>;
  files: Array<{
    archive_path: string; document_id: string; sha256: string; byte_size: number | null;
    document_kind?: string; media_type?: string | null; validity?: "UNKNOWN";
    requirement_ids: string[]; presence: 'VERIFIED_SOURCE' | 'UNKNOWN'; signature: 'UNKNOWN';
  }>;
  requirements: ResponseCoverage['requirements'];
  missing_cited_annexes: ResponseCoverage['cited_annexes'];
  entries_without_exported_file: string[];
  patron_review_ids: string[];
  p5_authorization_status: 'RECORDED' | 'NOT_RECORDED';
  p5_authorization_id: string | null;
  signature_visibility: "RESTRICTED";
  signature_records: [];
  inventory: 'CURRENT_NON_FINANCIAL_SIGNALS_ONLY';
  signature_requirement: 'UNKNOWN';
  signature_verification: 'UNKNOWN';
  signer_authority: 'UNKNOWN';
  conformity: 'UNKNOWN';
  external_submission: 'NOT_PERFORMED';
};

export type SubmissionSignatureIntentMetadata = {
  command_id: string;
  idempotency_key: string;
  signature_id: string;
  expected_manifest_sha256: string;
  rationale: string;
};
