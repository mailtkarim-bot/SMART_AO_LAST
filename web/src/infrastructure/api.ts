import type {
  AssignedCase,
  CaseResolution,
  CreateCaseInput,
  CreateCaseResponse,
  HandoverInput,
  HandoverReceipt,
  AuthSession,
  CurrentActor,
  BackendReadiness,
  CommandReceipt,
  DraftReport,
  FinancialCategory,
  PatronAssignment,
  PatronAssignmentInteractions,
  PatronAssignmentJournalItem,
  PatronAction,
  PatronDecisionDossier,
  PricingScenario,
  SubmissionEvidenceReceipt,
  SubmissionEvidenceProjection,
  SubmissionPackageReceipt,
  SubmissionMode,
  SubmissionPackageAuthorizationReceipt,
  SubmissionPackageManifestProjection,
  SubmissionSignatureProjection,
  SubmissionSignatureReceipt,
  CollaboratorTaskList,
  CollaboratorTaskWorkflow,
  CreateInformationRequestInput,
  RecordInformationResponseInput,
  DeclareTaskBlockerInput,
  ResolveTaskBlockerInput,
  TotpEnrollment,
  TotpStepUpResponse,
  PreparationReviewList,
  PreparationResponseDraftList,
  RequestPreparationReviewInput,
  DecidePreparationReviewInput,
  AddPreparationCorrectionInput,
  CreateTechnicalResponseDraftInput,
  PreparationPackage,
  CommitPricingImportRequest,
  PricingImportCommitReceipt,
  PricingImportPreview,
  PricingImportBatchRead,
  EnterpriseCompany,
  EnterpriseCompanyInput,
  EnterpriseDocumentUploadInput,
  EnterpriseDocumentVerificationInput,
  EnterpriseReceipt,
  EnterpriseUploadReceipt,
  EnterpriseCapability,
  EnterpriseCapabilityInput,
  EnterpriseCapabilityVersionInput,
  BoampObservation,
  BoampSourceStatus,
  BoampCaseCreationInput,
  BoampCaseCreationResponse,
  BoampQualificationInput,
  BoampQualificationReceipt,
  CaseDceReading,
  CaseExecutionCommandReceipt,
  CaseExecutionResults,
  CaseRexList,
  CaseInterviewList,
  RecordCaseInterviewInput,
  RecordCaseOutcomeInput,
  RecordCaseRexInput,
  RecordCaseOrderInput,
  RecordCaseP6ControlInput,
  RecordCaseP7ResultInput,
  KnowledgeSearchResponse,
  CreateDecisionRequest,
  CreateDecisionResponse,
  FreezeDecisionContextRequest,
  FreezeDecisionContextResponse,
  ResolveDecisionConditionRequest,
  ResolveDecisionConditionResponse,
  FinalizeGoNoGoDecisionRequest,
  FinalizeGoNoGoDecisionResponse,
  DecisionRiskRequirementPage,
  DecisionPricingReconciliationResponse,
  StructuredRiskProjection,
  StructuredRiskTreatmentResponse,
  TransitionStructuredRiskTreatmentInput,
  DceContractRiskSignalPage,
  RegulatoryProfilePage,
  ContractBaselineImpactPage,
  ContractProofReviewPage,
  ContractQueryExportAudit,
  PaymentCycle,
  PaymentCycleReview,
  PaymentUnknownAudit,
  PaymentUnknownAuditOwnerAct,
  PaymentCollectionRejectionReview,
  PostReceptionObligation,
  ContractExecutionEvidence,
  ContractExecutionEvidenceRequalification,
  ContractExecutionEvidenceTimelineEvent,
  ContractInstrumentVersion,
  ContractInstrumentSupersession,
  DeclareContractInstrumentSupersessionInput,
  RecordContractExecutionEvidenceInput,
  RecordContractExecutionEvidenceRequalificationInput,
  RecordContractInstrumentVersionInput,
  RegisterStructuredRiskInput,
  StructuredRiskRegistrationResponse,
  DecisionCctpPricingCrossingResponse,
  DecisionDocumentContradictionsResponse,
  ConsultationProjection,
  DceStagingPreparationReceipt,
  DceUploadReceipt,
  RegisterDceVersionReceipt,
  DceVersionMetadata,
  DceDocumentInventory,
  PrepareDceStagingInput,
  RegisterDceVersionInput,
  LinkCaseDceVersionInput,
  LinkCaseDceVersionReceipt,
} from "../shared/types";

const makeId = () => crypto.randomUUID();

function readCookie(name: string): string | undefined {
  if (typeof document === "undefined") return undefined;
  const prefix = `${encodeURIComponent(name)}=`;
  const cookie = document.cookie
    .split("; ")
    .find((entry) => entry.startsWith(prefix));
  return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : undefined;
}

function isAuthSession(value: unknown): value is AuthSession {
  if (typeof value !== "object" || value === null) return false;
  const candidate = value as Record<string, unknown>;
  return (
    typeof candidate.access_token === "string" &&
    candidate.token_type === "Bearer" &&
    typeof candidate.expires_in === "number"
  );
}

function apiError(status: number, body: unknown): Error & { status?: number; detail?: string } {
  const detail = responseDetail(body);
  const error = new Error(
    detail ?? `La requête a échoué (${status}).`,
  ) as Error & { status?: number; detail?: string };
  error.status = status;
  error.detail = detail;
  return error;
}

async function parseResponseBody(response: Response): Promise<unknown> {
  const body = await response.text();
  if (!body) return undefined;
  try {
    return JSON.parse(body);
  } catch {
    return undefined;
  }
}

function responseDetail(body: unknown): string | undefined {
  if (typeof body !== "object" || body === null || !("detail" in body)) {
    return undefined;
  }
  const detail = (body as { detail?: unknown }).detail;
  return typeof detail === "string" ? detail : undefined;
}

const REQUEST_TIMEOUT_MS = 30_000;

type SessionExpiredListener = () => void;

async function fetchWithTimeout(
  input: RequestInfo | URL,
  init: RequestInit,
  timeoutMs = REQUEST_TIMEOUT_MS,
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = globalThis.setTimeout(() => controller.abort(), timeoutMs);
  const abortFromCaller = () => controller.abort();
  init.signal?.addEventListener("abort", abortFromCaller, { once: true });
  try {
    return await fetch(input, { ...init, signal: controller.signal });
  } finally {
    globalThis.clearTimeout(timeoutId);
    init.signal?.removeEventListener("abort", abortFromCaller);
  }
}

function isReplayableBody(body: BodyInit | null | undefined): boolean {
  return (
    body === undefined ||
    body === null ||
    typeof body === "string" ||
    body instanceof FormData ||
    body instanceof Blob ||
    body instanceof ArrayBuffer ||
    body instanceof URLSearchParams
  );
}

export type ApiClient = ReturnType<typeof createApiClient>;

type CommandMetadata = {
  command_id?: string;
  idempotency_key?: string;
  correlation_id?: string;
  authorization_id?: string;
};

type TokenRefreshListener = (session: AuthSession) => void;

export function createApiClient(
  baseUrl: string,
  token: string,
  onTokenRefreshed?: TokenRefreshListener,
  onSessionExpired?: SessionExpiredListener,
) {
  const root = baseUrl.replace(/\/$/, "");
  let currentToken = token;
  let refreshPromise: Promise<AuthSession | null> | null = null;

  function csrfHeaders(): Record<string, string> | undefined {
    const csrfToken = readCookie("smart_ao_csrf");
    return csrfToken ? { "X-CSRF-Token": csrfToken } : undefined;
  }

  async function refreshSession(): Promise<AuthSession | null> {
    if (refreshPromise) return refreshPromise;
    refreshPromise = (async () => {
      const csrfToken = readCookie("smart_ao_csrf");
      if (!csrfToken) return null;
      const response = await fetchWithTimeout(`${root}/api/v1/auth/refresh`, {
        method: "POST",
        credentials: "include",
        headers: { Accept: "application/json", "X-CSRF-Token": csrfToken },
      });
      const parsed = await parseResponseBody(response);
      if (!response.ok || !isAuthSession(parsed)) return null;
      currentToken = parsed.access_token;
      onTokenRefreshed?.(parsed);
      return parsed;
    })().finally(() => {
      refreshPromise = null;
    });
    return refreshPromise;
  }

  async function request<T>(
    path: string,
    init: RequestInit = {},
    hasRetried = false,
  ): Promise<T> {
    const headers = new Headers(init.headers);
    headers.set("Accept", "application/json");
    if (typeof init.body === "string") {
      headers.set("Content-Type", "application/json");
    }
    if (currentToken.trim()) {
      headers.set("Authorization", `Bearer ${currentToken.trim()}`);
    }

    const response = await fetchWithTimeout(`${root}${path}`, {
      ...init,
      credentials: "include",
      headers,
    });
    const parsed = await parseResponseBody(response);
    const canRetry =
      !hasRetried &&
      response.status === 401 &&
      path !== "/api/v1/auth/me" &&
      path !== "/api/v1/auth/login" &&
      path !== "/api/v1/auth/refresh" &&
      path !== "/api/v1/auth/logout" &&
      isReplayableBody(init.body);
    if (canRetry) {
      const refreshed = await refreshSession();
      if (refreshed) return request<T>(path, init, true);
      currentToken = "";
      onSessionExpired?.();
    }
    if (!response.ok) {
      throw apiError(response.status, parsed);
    }
    return parsed as T;
  }

  async function requestBlob(
    path: string,
    init: RequestInit = {},
    hasRetried = false,
  ): Promise<Blob> {
    const headers = new Headers(init.headers);
    headers.set("Accept", headers.get("Accept") ?? "application/octet-stream");
    if (currentToken.trim()) {
      headers.set("Authorization", `Bearer ${currentToken.trim()}`);
    }
    const response = await fetchWithTimeout(`${root}${path}`, {
      ...init,
      credentials: "include",
      headers,
    });
    if (response.status === 401 && !hasRetried) {
      const refreshed = await refreshSession();
      if (refreshed) return requestBlob(path, init, true);
      currentToken = "";
      onSessionExpired?.();
    }
    if (!response.ok) {
      const parsed = await parseResponseBody(response);
      throw apiError(response.status, parsed);
    }
    return response.blob();
  }

  async function login(input: {
    email: string;
    password: string;
    tenant_id: string;
  }): Promise<AuthSession> {
    const result = await request<AuthSession>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify(input),
    });
    currentToken = result.access_token;
    onTokenRefreshed?.(result);
    return result;
  }

  async function logout(): Promise<void> {
    const csrfToken = readCookie("smart_ao_csrf");
    await request<void>("/api/v1/auth/logout", {
      method: "POST",
      headers: csrfToken ? { "X-CSRF-Token": csrfToken } : undefined,
    });
    currentToken = "";
  }

  return {
    login,
    beginTotpEnrollment: () =>
      request<TotpEnrollment>("/api/v1/auth/mfa/totp/enroll", {
        method: "POST",
        headers: csrfHeaders(),
      }),
    confirmTotpEnrollment: (factorId: string, code: string) =>
      request<TotpStepUpResponse>("/api/v1/auth/mfa/totp/confirm", {
        method: "POST",
        headers: csrfHeaders(),
        body: JSON.stringify({ factor_id: factorId, code }),
      }),
    stepUpTotp: (code: string) =>
      request<TotpStepUpResponse>("/api/v1/auth/mfa/totp/step-up", {
        method: "POST",
        headers: csrfHeaders(),
        body: JSON.stringify({ code }),
      }),
    disableTotp: (code: string) =>
      request<void>("/api/v1/auth/mfa/totp/disable", {
        method: "POST",
        headers: csrfHeaders(),
        body: JSON.stringify({ code }),
      }),
    refresh: refreshSession,
    getCurrentActor: () => request<CurrentActor>("/api/v1/auth/me"),
    logout,
    getBackendReadiness: () => request<BackendReadiness>("/healthz/ready"),
    listAssignedCases: () => request<AssignedCase[]>("/api/v1/cases/assigned"),
    listCaseExecutionResults: (caseId: string) =>
      request<CaseExecutionResults>(`/api/v1/patron/cases/${encodeURIComponent(caseId)}/execution-results`),
    listCaseRex: (caseId: string) =>
      request<CaseRexList>(`/api/v1/patron/cases/${encodeURIComponent(caseId)}/rex`),
    listCaseInterviews: (caseId: string) =>
      request<CaseInterviewList>(`/api/v1/patron/cases/${encodeURIComponent(caseId)}/interviews`),
    recordCaseInterview: (input: RecordCaseInterviewInput) =>
      request<CaseExecutionCommandReceipt>(`/api/v1/patron/cases/${encodeURIComponent(input.case_id)}/interviews`, { method: "POST", body: JSON.stringify(input) }),
    recordCaseRex: (p7ResultId: string, input: RecordCaseRexInput) =>
      request<CaseExecutionCommandReceipt>(`/api/v1/patron/case-p7/${encodeURIComponent(p7ResultId)}/rex`, { method: "POST", body: JSON.stringify(input) }),
    recordCaseOutcome: (input: RecordCaseOutcomeInput) =>
      request<CaseExecutionCommandReceipt>("/api/v1/patron/case-outcomes", { method: "POST", body: JSON.stringify(input) }),
    recordCaseOrder: (input: RecordCaseOrderInput) =>
      request<CaseExecutionCommandReceipt>("/api/v1/patron/case-orders", { method: "POST", body: JSON.stringify(input) }),
    recordCaseP6Control: (orderId: string, input: RecordCaseP6ControlInput) =>
      request<CaseExecutionCommandReceipt>(`/api/v1/patron/case-orders/${encodeURIComponent(orderId)}/p6`, { method: "POST", body: JSON.stringify(input) }),
    recordCaseP7Result: (p6ControlId: string, input: RecordCaseP7ResultInput) =>
      request<CaseExecutionCommandReceipt>(`/api/v1/patron/case-p6/${encodeURIComponent(p6ControlId)}/p7`, { method: "POST", body: JSON.stringify(input) }),
    createCase: (input: CreateCaseInput) =>
      request<CreateCaseResponse>("/api/v1/cases", {
        method: "POST",
        body: JSON.stringify({
          ...input,
          command_id: input.command_id ?? makeId(),
          idempotency_key: input.idempotency_key ?? makeId(),
          correlation_id: input.correlation_id ?? makeId(),
      }),
      }),
    requestHandover: (input: HandoverInput) =>
      request<HandoverReceipt>("/api/v1/continuity/handovers", {
        method: "POST",
        body: JSON.stringify({
          ...input,
          handover_id: input.handover_id ?? makeId(),
          command_id: input.command_id ?? makeId(),
          idempotency_key: input.idempotency_key ?? makeId(),
          correlation_id: input.correlation_id ?? makeId(),
        }),
      }),
    acceptHandover: (handoverId: string, reason: string) =>
      request<HandoverReceipt>(
        `/api/v1/continuity/handovers/${encodeURIComponent(handoverId)}/acceptance`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: makeId(),
            correlation_id: makeId(),
            reason,
          }),
        },
      ),
    listPatronAssignments: () =>
      request<{ items: PatronAssignment[] }>("/api/v1/patron/assignments"),
    getAssignmentJournal: (assignmentId: string) =>
      request<{ assignment: PatronAssignment; items: PatronAssignmentJournalItem[] }>(
        `/api/v1/patron/assignments/${encodeURIComponent(assignmentId)}/journal`,
      ),
    getAssignmentInteractions: (assignmentId: string) =>
      request<PatronAssignmentInteractions>(
        `/api/v1/patron/assignments/${encodeURIComponent(assignmentId)}/interactions`,
      ),
    listPatronActions: () =>
      request<{ items: PatronAction[]; open_count: number }>("/api/v1/patron/actions"),
    listBoampObservations: () =>
      request<{ observations: BoampObservation[]; source_status?: BoampSourceStatus }>(
        "/api/v1/patron/boamp-opportunities",
      ),
    qualifyBoampObservation: (
      observationId: string,
      input: BoampQualificationInput,
    ) =>
      request<BoampQualificationReceipt>(
        `/api/v1/patron/boamp-opportunities/${encodeURIComponent(observationId)}/qualification`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: makeId(),
            idempotency_key: makeId(),
            ...input,
          }),
        },
      ),
    createCaseFromBoampObservation: (
      observationId: string,
      input: BoampCaseCreationInput = {},
    ) =>
      request<BoampCaseCreationResponse>(
        `/api/v1/patron/boamp-opportunities/${encodeURIComponent(observationId)}/case`,
        {
          method: "POST",
          body: JSON.stringify({
            ...input,
            command_id: input.command_id ?? makeId(),
            idempotency_key: input.idempotency_key ?? makeId(),
            correlation_id: input.correlation_id ?? makeId(),
          }),
        },
      ),
    getCaseDceReading: (caseId: string) =>
      request<CaseDceReading>(
        `/api/v1/cases/${encodeURIComponent(caseId)}/dce-reading`,
      ),
    getConsultation: (consultationId: string) =>
      request<ConsultationProjection>(
        `/api/v1/consultations/${encodeURIComponent(consultationId)}`,
      ),
    prepareDceStaging: (input: PrepareDceStagingInput) =>
      request<DceStagingPreparationReceipt>("/api/v1/dce-staged-objects", {
        method: "POST",
        body: JSON.stringify({
          ...input,
          command_id: input.command_id ?? makeId(),
          idempotency_key: input.idempotency_key ?? makeId(),
          correlation_id: input.correlation_id ?? makeId(),
        }),
      }),
    uploadDceStagedObjectContent: (
      storageObjectId: string,
      idempotencyKey: string,
      file: File,
    ) =>
      request<DceUploadReceipt>(
        `/api/v1/dce-staged-objects/${encodeURIComponent(storageObjectId)}/content`,
        {
          method: "PUT",
          headers: { "Idempotency-Key": idempotencyKey },
          body: file,
        },
      ),
    registerDceVersion: (input: RegisterDceVersionInput) =>
      request<RegisterDceVersionReceipt>("/api/v1/dce-versions", {
        method: "POST",
        body: JSON.stringify({
          ...input,
          command_id: input.command_id ?? makeId(),
          idempotency_key: input.idempotency_key ?? makeId(),
          correlation_id: input.correlation_id ?? makeId(),
        }),
      }),
    getDceVersion: (dceVersionId: string) =>
      request<DceVersionMetadata>(
        `/api/v1/dce-versions/${encodeURIComponent(dceVersionId)}`,
      ),
    listDceVersionDocuments: (dceVersionId: string) =>
      request<DceDocumentInventory>(
        `/api/v1/dce-versions/${encodeURIComponent(dceVersionId)}/documents`,
      ),
    linkCaseDceVersion: (caseId: string, input: LinkCaseDceVersionInput) =>
      request<LinkCaseDceVersionReceipt>(
        `/api/v1/cases/${encodeURIComponent(caseId)}/dce-applicability`,
        {
          method: "POST",
          body: JSON.stringify({
            ...input,
            command_id: makeId(),
            idempotency_key: makeId(),
            correlation_id: makeId(),
          }),
        },
      ),
    getCaseResolution: (caseId: string) =>
      request<CaseResolution>(
        `/api/v1/cases/${encodeURIComponent(caseId)}/resolution`,
      ),
    searchCaseKnowledge: (caseId: string, query: string, topK = 5) => {
      const params = new URLSearchParams({ q: query, top_k: String(topK) });
      return request<KnowledgeSearchResponse>(
        `/api/v1/cases/${encodeURIComponent(caseId)}/knowledge/search?${params.toString()}`,
      );
    },
    getDecisionDossier: (caseId: string) =>
      request<PatronDecisionDossier>(
        `/api/v1/patron/cases/${encodeURIComponent(caseId)}/decision-dossier`,
      ),
    getDecisionRisk: (caseId: string, riskId: string) =>
      request<StructuredRiskProjection>(
        `/api/v1/patron/cases/${encodeURIComponent(caseId)}/risks/${encodeURIComponent(riskId)}`,
      ),
    listDceContractRiskSignals: (caseId: string, limit = 50) =>
      request<DceContractRiskSignalPage>(
        `/api/v1/patron/cases/${encodeURIComponent(caseId)}/dce-contract-risk-signals?limit=${limit}`,
      ),
    listRegulatoryProfiles: (caseId: string) =>
      request<RegulatoryProfilePage>(
        `/api/v1/patron/cases/${encodeURIComponent(caseId)}/regulatory-profiles`,
      ),
    listContractBaselineImpacts: (caseId: string) =>
      request<ContractBaselineImpactPage>(
        `/api/v1/patron/cases/${encodeURIComponent(caseId)}/contract-baseline-impacts`,
      ),
    listContractProofReviews: (caseId: string) =>
      request<ContractProofReviewPage>(
        `/api/v1/patron/cases/${encodeURIComponent(caseId)}/contract-proof-reviews`,
      ),
    getContractQueryExportAudit: (caseId: string, exportId: string) =>
      request<ContractQueryExportAudit>(`/api/v1/patron/cases/${encodeURIComponent(caseId)}/contract-query-exports/${encodeURIComponent(exportId)}/audit`),
    listPaymentCycles: (caseId: string) => request<PaymentCycle[]>(`/api/v1/patron/cases/${encodeURIComponent(caseId)}/payment-post-reception-cycles`),
    recordPaymentCycle: (caseId: string, input: Record<string, unknown>) => request(`/api/v1/patron/cases/${encodeURIComponent(caseId)}/payment-post-reception-cycles`, { method: "POST", body: JSON.stringify(input) }),
    qualifyPaymentCycle: (caseId: string, cycleId: string, input: Record<string, unknown>) => request(`/api/v1/patron/cases/${encodeURIComponent(caseId)}/payment-cycles/${encodeURIComponent(cycleId)}/cash-assumptions`, { method: "POST", body: JSON.stringify(input) }),
    recordPaymentCycleReview: (cycleId: string, input: Record<string, unknown>) => request(`/api/v1/patron/payment-cycles/${encodeURIComponent(cycleId)}/reviews`, { method: "POST", body: JSON.stringify(input) }),
    listPaymentCycleReviews: (cycleId: string) => request<PaymentCycleReview[]>(`/api/v1/patron/payment-cycles/${encodeURIComponent(cycleId)}/reviews`),
    getPaymentUnknownAudit: (caseId: string) => request<PaymentUnknownAudit>(`/api/v1/patron/cases/${encodeURIComponent(caseId)}/payment-post-reception-unknown-audit`),
    getPaymentUnknownAuditOwnerAct: (caseId: string) => request<PaymentUnknownAuditOwnerAct | null>(`/api/v1/patron/cases/${encodeURIComponent(caseId)}/payment-post-reception-unknown-audit-owner-act`),
    recordPaymentUnknownAuditOwnerAct: (caseId: string, input: Record<string, unknown>) => request(`/api/v1/patron/cases/${encodeURIComponent(caseId)}/payment-post-reception-unknown-audit-owner-acts`, { method: "POST", body: JSON.stringify(input) }),
    getPaymentCollectionRejectionReview: (caseId: string) => request<PaymentCollectionRejectionReview | null>(`/api/v1/patron/cases/${encodeURIComponent(caseId)}/payment-collection-rejection-review`),
    recordPaymentCollectionRejectionReview: (caseId: string, input: Record<string, unknown>) => request(`/api/v1/patron/cases/${encodeURIComponent(caseId)}/payment-collection-rejection-reviews`, { method: "POST", body: JSON.stringify(input) }),
    listPostReceptionObligations: (caseId: string) => request<PostReceptionObligation[]>(`/api/v1/patron/cases/${encodeURIComponent(caseId)}/post-reception-obligations`),
    recordPostReceptionObligation: (caseId: string, input: Record<string, unknown>) => request(`/api/v1/patron/cases/${encodeURIComponent(caseId)}/post-reception-obligations`, { method: "POST", body: JSON.stringify(input) }),
    transitionPostReceptionObligation: (caseId: string, obligationId: string, input: Record<string, unknown>) => request(`/api/v1/patron/cases/${encodeURIComponent(caseId)}/post-reception-obligations/${encodeURIComponent(obligationId)}/transitions`, { method: "POST", body: JSON.stringify(input) }),
    listContractExecutionEvidence: (caseId: string) => request<ContractExecutionEvidence[]>(`/api/v1/patron/cases/${encodeURIComponent(caseId)}/contract-execution-evidence`),
    recordContractExecutionEvidence: (caseId: string, input: RecordContractExecutionEvidenceInput) => request(`/api/v1/patron/cases/${encodeURIComponent(caseId)}/contract-execution-evidence`, { method: "POST", body: JSON.stringify(input) }),
    listContractExecutionEvidenceRequalifications: (caseId: string) => request<ContractExecutionEvidenceRequalification[]>(`/api/v1/patron/cases/${encodeURIComponent(caseId)}/contract-execution-evidence-requalifications`),
    recordContractExecutionEvidenceRequalification: (caseId: string, input: RecordContractExecutionEvidenceRequalificationInput) => request(`/api/v1/patron/cases/${encodeURIComponent(caseId)}/contract-execution-evidence-requalifications`, { method: "POST", body: JSON.stringify(input) }),
    listContractExecutionEvidenceTimeline: (caseId: string) => request<ContractExecutionEvidenceTimelineEvent[]>(`/api/v1/patron/cases/${encodeURIComponent(caseId)}/contract-execution-evidence-timeline`),
    listContractInstrumentVersions: (caseId: string) => request<ContractInstrumentVersion[]>(`/api/v1/patron/cases/${encodeURIComponent(caseId)}/contract-instrument-versions`),
    recordContractInstrumentVersion: (caseId: string, input: RecordContractInstrumentVersionInput) => request(`/api/v1/patron/cases/${encodeURIComponent(caseId)}/contract-instrument-versions`, { method: "POST", body: JSON.stringify(input) }),
    listContractInstrumentSupersessions: (caseId: string) => request<ContractInstrumentSupersession[]>(`/api/v1/patron/cases/${encodeURIComponent(caseId)}/contract-instrument-supersessions`),
    declareContractInstrumentSupersession: (caseId: string, input: DeclareContractInstrumentSupersessionInput) => request(`/api/v1/patron/cases/${encodeURIComponent(caseId)}/contract-instrument-supersessions`, { method: "POST", body: JSON.stringify(input) }),
    registerStructuredRisk: (caseId: string, input: RegisterStructuredRiskInput) =>
      request<StructuredRiskRegistrationResponse>(
        `/api/v1/patron/cases/${encodeURIComponent(caseId)}/risks`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: makeId(),
            idempotency_key: makeId(),
            correlation_id: makeId(),
            ...input,
          }),
        },
      ),
    transitionDecisionRiskTreatment: (
      caseId: string,
      riskId: string,
      input: TransitionStructuredRiskTreatmentInput,
    ) =>
      request<StructuredRiskTreatmentResponse>(
        `/api/v1/patron/cases/${encodeURIComponent(caseId)}/risks/${encodeURIComponent(riskId)}/treatment`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: makeId(),
            idempotency_key: makeId(),
            risk_id: riskId,
            ...input,
          }),
        },
      ),
    crossCctpPricing: (caseId: string, limit = 25) =>
      request<DecisionCctpPricingCrossingResponse>(
        `/api/v1/patron/cases/${encodeURIComponent(caseId)}/cctp-pricing-crossing?limit=${limit}`,
      ),
    listDocumentContradictions: (caseId: string, limit = 25) =>
      request<DecisionDocumentContradictionsResponse>(
        `/api/v1/patron/cases/${encodeURIComponent(caseId)}/document-contradictions?limit=${limit}`,
      ),
    listDecisionRiskRequirementLinks: (
      caseId: string,
      limit = 20,
      cursor?: string,
    ) => {
      const params = new URLSearchParams({ limit: String(limit) });
      if (cursor) params.set("cursor", cursor);
      return request<DecisionRiskRequirementPage>(
        `/api/v1/patron/cases/${encodeURIComponent(caseId)}/risk-requirement-links?${params.toString()}`,
      );
    },
    reconcileDecisionPricing: (
      caseId: string,
      linkId: string,
      search: string,
      limit = 20,
    ) => {
      const params = new URLSearchParams({ search, limit: String(limit) });
      return request<DecisionPricingReconciliationResponse>(
        `/api/v1/patron/cases/${encodeURIComponent(caseId)}/risk-requirement-links/${encodeURIComponent(linkId)}/pricing-reconciliation?${params.toString()}`,
      );
    },
    createDecision: (caseId: string, input: CreateDecisionRequest) =>
      request<CreateDecisionResponse>(
        `/api/v1/patron/cases/${encodeURIComponent(caseId)}/decisions`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: input.command_id ?? makeId(),
            idempotency_key: input.idempotency_key ?? makeId(),
            scope_fingerprint: input.scope_fingerprint,
          }),
        },
      ),
    freezeDecisionContext: (
      caseId: string,
      decisionId: string,
      input: FreezeDecisionContextRequest,
    ) =>
      request<FreezeDecisionContextResponse>(
        `/api/v1/patron/cases/${encodeURIComponent(caseId)}/decisions/${encodeURIComponent(decisionId)}/context`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: input.command_id ?? makeId(),
            idempotency_key: input.idempotency_key ?? makeId(),
            context_id: input.context_id,
            expected_revision: input.expected_revision,
            rationale: input.rationale,
            unknowns: input.unknowns ?? [],
            risks: input.risks ?? [],
            references: input.references,
          }),
        },
      ),
    resolveDecisionCondition: (
      caseId: string,
      decisionId: string,
      conditionId: string,
      input: ResolveDecisionConditionRequest,
    ) =>
      request<ResolveDecisionConditionResponse>(
        `/api/v1/patron/cases/${encodeURIComponent(caseId)}/decisions/${encodeURIComponent(decisionId)}/conditions/${encodeURIComponent(conditionId)}/resolve`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: input.command_id ?? makeId(),
            idempotency_key: input.idempotency_key ?? makeId(),
            transition_id: input.transition_id ?? makeId(),
            expected_revision: input.expected_revision,
            target_status: input.target_status,
            evidence_reference: input.evidence_reference,
            failure_reason: input.failure_reason,
          }),
        },
      ),
    finalizeDecision: (
      caseId: string,
      decisionId: string,
      input: FinalizeGoNoGoDecisionRequest,
    ) =>
      request<FinalizeGoNoGoDecisionResponse>(
        `/api/v1/patron/cases/${encodeURIComponent(caseId)}/decisions/${encodeURIComponent(decisionId)}/go-no-go`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: input.command_id ?? makeId(),
            idempotency_key: input.idempotency_key ?? makeId(),
            expected_revision: input.expected_revision,
            displayed_fingerprint: input.displayed_fingerprint,
            outcome: input.outcome,
            justification: input.justification,
            conditions: input.conditions ?? [],
          }),
        },
      ),
    listPricingScenarios: (caseId: string) =>
      request<PricingScenario[]>(
        `/api/v1/patron/cases/${encodeURIComponent(caseId)}/pricing-scenarios`,
      ),
    listEnterpriseCapabilities: (companyId: string) =>
      request<{ capabilities: EnterpriseCapability[] }>(
        `/api/v1/patron/enterprise/companies/${encodeURIComponent(companyId)}/capabilities`,
      ),
    createEnterpriseCapability: (companyId: string, input: EnterpriseCapabilityInput) =>
      request<EnterpriseReceipt>(
        `/api/v1/patron/enterprise/companies/${encodeURIComponent(companyId)}/capabilities`,
        {
          method: "POST",
          body: JSON.stringify({ command_id: makeId(), idempotency_key: makeId(), ...input }),
        },
      ),
    addEnterpriseCapabilityVersion: (
      capabilityId: string,
      input: EnterpriseCapabilityVersionInput,
    ) =>
      request<EnterpriseReceipt>(
        `/api/v1/patron/enterprise/capabilities/${encodeURIComponent(capabilityId)}/versions`,
        {
          method: "POST",
          body: JSON.stringify({ command_id: makeId(), idempotency_key: makeId(), ...input }),
        },
      ),
    getEnterpriseCompany: () =>
      request<EnterpriseCompany>("/api/v1/patron/enterprise/company"),
    createEnterpriseCompany: (input: EnterpriseCompanyInput) =>
      request<EnterpriseReceipt>("/api/v1/patron/enterprise/company", {
        method: "POST",
        body: JSON.stringify({
          command_id: makeId(),
          idempotency_key: makeId(),
          ...input,
        }),
      }),
    prepareEnterpriseDocumentUpload: (companyId: string, input: EnterpriseDocumentUploadInput) =>
      request<EnterpriseReceipt>(
        `/api/v1/patron/enterprise/companies/${encodeURIComponent(companyId)}/documents/upload`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: makeId(),
            idempotency_key: makeId(),
            ...input,
          }),
        },
      ),
    uploadEnterpriseDocumentContent: (
      companyId: string,
      uploadId: string,
      file: File,
    ) =>
      request<EnterpriseUploadReceipt>(
        `/api/v1/patron/enterprise/companies/${encodeURIComponent(companyId)}/documents/uploads/${encodeURIComponent(uploadId)}/content`,
        {
          method: "PUT",
          headers: { "Idempotency-Key": makeId() },
          body: file,
        },
      ),
    verifyEnterpriseDocument: (
      companyId: string,
      documentId: string,
      input: EnterpriseDocumentVerificationInput,
    ) =>
      request<EnterpriseReceipt>(
        `/api/v1/patron/enterprise/companies/${encodeURIComponent(companyId)}/documents/${encodeURIComponent(documentId)}/verification`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: makeId(),
            idempotency_key: makeId(),
            ...input,
          }),
        },
      ),
    createPricingImportPreview: (
      caseId: string,
      file: File,
      documentKind: "DPGF" | "BPU" | "EXCEL" = "EXCEL",
      metadata: CommandMetadata = {},
    ) => {
      const form = new FormData();
      form.append("upload", file);
      const query = new URLSearchParams({ document_kind: documentKind });
      return request<PricingImportPreview>(
        `/api/v1/patron/cases/${encodeURIComponent(caseId)}/pricing-import/preview?${query}`,
        {
          method: "POST",
          headers: {
            "X-Command-Id": metadata.command_id ?? makeId(),
            "Idempotency-Key": metadata.idempotency_key ?? makeId(),
            ...(metadata.correlation_id
              ? { "X-Correlation-Id": metadata.correlation_id }
              : {}),
          },
          body: form,
        },
      );
    },
    getPricingImport: (caseId: string, batchId: string) =>
      request<PricingImportBatchRead>(
        `/api/v1/patron/cases/${encodeURIComponent(caseId)}/pricing-import/${encodeURIComponent(batchId)}`,
      ),
    commitPricingImport: (
      caseId: string,
      batchId: string,
      input: Omit<CommitPricingImportRequest, "command_id" | "idempotency_key"> & {
        command_id?: string;
        idempotency_key?: string;
      },
    ) =>
      request<PricingImportCommitReceipt>(
        `/api/v1/patron/cases/${encodeURIComponent(caseId)}/pricing-import/${encodeURIComponent(batchId)}/commit`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: input.command_id ?? makeId(),
            idempotency_key: input.idempotency_key ?? makeId(),
            ...input,
          }),
        },
      ),
    prepareSubmissionPackage: (
      preparationPackageId: string,
      expectedRevision: number,
      options: { submission_mode?: SubmissionMode; candidature_only_reason?: string } = {},
    ) =>
      request<SubmissionPackageReceipt>(
        `/api/v1/patron/preparation/${encodeURIComponent(preparationPackageId)}/submission-packages`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: makeId(),
            idempotency_key: makeId(),
            expected_preparation_revision: expectedRevision,
            ...options,
          }),
        },
      ),
    authorizeSubmissionPackage: (
      submissionPackageId: string,
      expectedPackageVersion: number,
      rationale: string,
      metadata: CommandMetadata = {},
    ) =>
      request<SubmissionPackageAuthorizationReceipt>(
        `/api/v1/patron/submission-packages/${encodeURIComponent(submissionPackageId)}/authorize`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: metadata.command_id ?? makeId(),
            idempotency_key: metadata.idempotency_key ?? makeId(),
            authorization_id: metadata.authorization_id ?? makeId(),
            ...(metadata.correlation_id ? { correlation_id: metadata.correlation_id } : {}),
            expected_package_version: expectedPackageVersion,
            rationale,
          }),
        },
      ),
    getSubmissionPackageManifest: (submissionPackageId: string) =>
      request<SubmissionPackageManifestProjection>(
        `/api/v1/patron/submission-packages/${encodeURIComponent(submissionPackageId)}/manifest`,
      ),
    downloadSubmissionPackage: (submissionPackageId: string): Promise<Blob> =>
      requestBlob(
        `/api/v1/patron/submission-packages/${encodeURIComponent(submissionPackageId)}/export`,
        { headers: { Accept: "application/zip" } },
      ),
    listPreparationReviews: (packageId: string) =>
      request<PreparationReviewList>(
        `/api/v1/preparation/${encodeURIComponent(packageId)}/reviews`,
      ),
    listPreparationResponseDrafts: (packageId: string) =>
      request<PreparationResponseDraftList>(
        `/api/v1/preparation/${encodeURIComponent(packageId)}/response-drafts`,
      ),
    requestPreparationReview: (packageId: string, input: RequestPreparationReviewInput) =>
      request<CommandReceipt>(
        `/api/v1/preparation/${encodeURIComponent(packageId)}/reviews`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: makeId(),
            idempotency_key: makeId(),
            review_id: makeId(),
            ...input,
          }),
        },
      ),
    decidePreparationReview: (packageId: string, input: DecidePreparationReviewInput) =>
      request<CommandReceipt>(
        `/api/v1/preparation/${encodeURIComponent(packageId)}/reviews/${encodeURIComponent(input.review_id)}/decision`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: makeId(),
            idempotency_key: makeId(),
            ...input,
          }),
        },
      ),
    addPreparationCorrection: (packageId: string, input: AddPreparationCorrectionInput) =>
      request<CommandReceipt>(
        `/api/v1/preparation/${encodeURIComponent(packageId)}/reviews/${encodeURIComponent(input.review_id)}/corrections`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: makeId(),
            idempotency_key: makeId(),
            ...input,
          }),
        },
      ),
    createTechnicalResponseDraft: (
      packageId: string,
      input: CreateTechnicalResponseDraftInput,
    ) =>
      request<CommandReceipt>(
        `/api/v1/preparation/${encodeURIComponent(packageId)}/response-drafts`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: makeId(),
            idempotency_key: makeId(),
            draft_id: makeId(),
            ...input,
          }),
        },
      ),
    getCollaboratorTaskWorkflow: (taskId: string) =>
      request<CollaboratorTaskWorkflow>(
        `/api/v1/collaborator/tasks/${encodeURIComponent(taskId)}/workflow`,
      ),
    createInformationRequest: (
      taskId: string,
      input: CreateInformationRequestInput,
    ) =>
      request<CommandReceipt>(
        `/api/v1/collaborator/tasks/${encodeURIComponent(taskId)}/information-requests`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: makeId(),
            idempotency_key: makeId(),
            ...input,
          }),
        },
      ),
    recordInformationResponse: (
      requestId: string,
      input: RecordInformationResponseInput,
    ) =>
      request<CommandReceipt>(
        `/api/v1/collaborator/information-requests/${encodeURIComponent(requestId)}/responses`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: makeId(),
            idempotency_key: makeId(),
            ...input,
          }),
        },
      ),
    declareTaskBlocker: (taskId: string, input: DeclareTaskBlockerInput) =>
      request<CommandReceipt>(
        `/api/v1/collaborator/tasks/${encodeURIComponent(taskId)}/blockers`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: makeId(),
            idempotency_key: makeId(),
            ...input,
          }),
        },
      ),
    resolveTaskBlocker: (
      taskId: string,
      blockerId: string,
      input: ResolveTaskBlockerInput,
    ) =>
      request<CommandReceipt>(
        `/api/v1/collaborator/tasks/${encodeURIComponent(taskId)}/blockers/${encodeURIComponent(blockerId)}/resolve`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: makeId(),
            idempotency_key: makeId(),
            ...input,
          }),
        },
      ),
    getCollaboratorPreparation: (packageId: string) =>
      request<PreparationPackage>(
        `/api/v1/collaborator/preparation/${encodeURIComponent(packageId)}`,
      ),
    listCollaboratorTasks: (caseId: string) =>
      request<CollaboratorTaskList>(
        `/api/v1/collaborator/cases/${encodeURIComponent(caseId)}/tasks`,
      ),
    evaluatePreparationReadiness: (
      caseId: string,
      input: {
        package_id: string;
        assignment_id: string;
        dce_version_id: string;
        expected_revision: number;
      },
    ) =>
      request<CommandReceipt>(
        `/api/v1/collaborator/cases/${encodeURIComponent(caseId)}/preparation/readiness`,
        {
          method: "POST",
          body: JSON.stringify({ command_id: makeId(), idempotency_key: makeId(), ...input }),
        },
      ),
    getGeneratedDocumentContent: (
      packageId: string,
      documentId: string,
      download = false,
    ): Promise<Blob> =>
      requestBlob(
        `/api/v1/collaborator/preparation/${encodeURIComponent(packageId)}/documents/${encodeURIComponent(documentId)}/content${download ? "?download=true" : ""}`,
        { headers: { Accept: "text/markdown" } },
      ),
    generateTechnicalDocument: (
      packageId: string,
      input: {
        expected_revision: number;
        readiness_revision: number;
        document_kind?: "TECHNICAL_RESPONSE" | "DC1" | "DC2" | "DC4";
      },
    ) =>
      request<CommandReceipt>(
        `/api/v1/collaborator/preparation/${encodeURIComponent(packageId)}/documents`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: makeId(),
            idempotency_key: makeId(),
            document_kind: input.document_kind ?? "TECHNICAL_RESPONSE",
            ...input,
          }),
        },
      ),
    claimCollaboratorTask: (taskId: string, expectedRevision: number) =>
      request<CommandReceipt>(
        `/api/v1/collaborator/tasks/${encodeURIComponent(taskId)}/claim`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: makeId(),
            idempotency_key: makeId(),
            expected_revision: expectedRevision,
          }),
        },
      ),
    recordCollaboratorTaskResult: (
      taskId: string,
      input: {
        expected_revision: number;
        result_text: string;
        source_locator?: string;
        outcome: "RECORDED" | "NOT_APPLICABLE" | "UNABLE_TO_COMPLETE";
      },
    ) =>
      request<CommandReceipt>(
        `/api/v1/collaborator/tasks/${encodeURIComponent(taskId)}/results`,
        {
          method: "POST",
          body: JSON.stringify({ command_id: makeId(), idempotency_key: makeId(), ...input }),
        },
      ),
    completeCollaboratorTask: (taskId: string, expectedRevision: number) =>
      request<CommandReceipt>(
        `/api/v1/collaborator/tasks/${encodeURIComponent(taskId)}/complete`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: makeId(),
            idempotency_key: makeId(),
            expected_revision: expectedRevision,
          }),
        },
      ),
    createPreparationSnapshot: (
      packageId: string,
      input: { snapshot_id: string; expected_package_revision: number },
    ) =>
      request<CommandReceipt>(
        `/api/v1/collaborator/preparation/${encodeURIComponent(packageId)}/snapshots`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: makeId(),
            idempotency_key: makeId(),
            package_id: packageId,
            ...input,
          }),
        },
      ),
    transmitPreparationSnapshot: (
      packageId: string,
      input: { snapshot_id: string; transmission_id: string; expected_package_revision: number },
    ) =>
      request<CommandReceipt>(
        `/api/v1/collaborator/preparation/${encodeURIComponent(packageId)}/transmissions`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: makeId(),
            idempotency_key: makeId(),
            package_id: packageId,
            ...input,
          }),
        },
      ),
    requestSubmissionSignature: (submissionPackageId: string, expectedPackageVersion: number) =>
      request<SubmissionSignatureReceipt>(
        `/api/v1/patron/submission-packages/${encodeURIComponent(submissionPackageId)}/signatures`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: makeId(),
            idempotency_key: makeId(),
            signature_id: makeId(),
            expected_package_version: expectedPackageVersion,
          }),
        },
      ),
    getSubmissionSignature: (signatureId: string) =>
      request<SubmissionSignatureProjection>(
        `/api/v1/patron/submission-signatures/${encodeURIComponent(signatureId)}`,
      ),
    recordSubmissionEvidence: (
      submissionPackageId: string,
      input: {
        evidence_type: "MANUAL_RECEIPT" | "MANUAL_PORTAL_REFERENCE" | "HUMAN_DEPOSIT_ATTEMPT";
        external_reference_hash: string;
        evidence_sha256: string;
        notes_redacted?: string;
      },
    ) =>
      request<SubmissionEvidenceReceipt>(
        `/api/v1/patron/submission-packages/${encodeURIComponent(submissionPackageId)}/evidence`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: makeId(),
            idempotency_key: makeId(),
            evidence_id: makeId(),
            ...input,
          }),
        },
      ),
    getSubmissionEvidence: (submissionPackageId: string) =>
      request<SubmissionEvidenceProjection[]>(
        `/api/v1/patron/submission-packages/${encodeURIComponent(submissionPackageId)}/evidence`,
      ),
    createDraft: (caseId: string) =>
      request<CommandReceipt>(
        `/api/v1/patron/cases/${encodeURIComponent(caseId)}/financial-reports/drafts`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: makeId(),
            idempotency_key: makeId(),
            currency_code: "EUR",
            ruleset_version: 1,
          }),
        },
      ),
    getDraft: (caseId: string, reportId: string) =>
      request<DraftReport>(
        `/api/v1/patron/cases/${encodeURIComponent(caseId)}/financial-reports/${encodeURIComponent(reportId)}/draft`,
      ),
    addLine: (
      caseId: string,
      reportId: string,
      input: {
        category: FinancialCategory;
        label: string;
        quantity_decimal: string;
        unit: string;
        amount_minor: number;
        expected_revision: number;
      },
    ) =>
      request<CommandReceipt>(
        `/api/v1/patron/cases/${encodeURIComponent(caseId)}/financial-reports/${encodeURIComponent(reportId)}/lines`,
        {
          method: "POST",
          body: JSON.stringify({
            command_id: makeId(),
            idempotency_key: makeId(),
            expected_revision: input.expected_revision,
            category: input.category,
            label: input.label,
            quantity_decimal: input.quantity_decimal,
            unit: input.unit,
            amount_minor: input.amount_minor,
          }),
        },
      ),
  };
}
