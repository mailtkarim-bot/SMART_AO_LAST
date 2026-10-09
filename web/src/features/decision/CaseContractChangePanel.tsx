import { useEffect, useLayoutEffect, useRef, useState, type FormEvent } from "react";
import type { ApiClient } from "../../infrastructure/api";
import type {
  A1EngagementSource,
  CaseContractChangeApplicability,
  CaseContractChangeEvent,
  CaseContractChangeImpactAxis,
  CaseContractChangeKind,
  ContractInstrumentVersion,
  RecordCaseContractChangeActionInput,
  RecordCaseContractChangeActionImpactRelationInput,
  RecordCaseContractChangeActionExecutionInput,
  PrepareCaseContractChangeEvidenceUploadInput,
  RecordCaseContractChangeExternalConfirmationInput,
  RecordCaseContractChangeApplicabilityInput,
  RecordCaseContractChangeEngagementLinkInput,
  RecordCaseContractChangeImpactDeclarationInput,
  RecordCaseContractChangeEventInput,
} from "../../shared/types";

type ReadState = "LOADING" | "READY" | "UNAVAILABLE";
type IntentInput =
  | RecordCaseContractChangeEventInput
  | RecordCaseContractChangeApplicabilityInput
  | RecordCaseContractChangeActionInput
  | RecordCaseContractChangeActionImpactRelationInput
  | RecordCaseContractChangeActionExecutionInput
  | RecordCaseContractChangeExternalConfirmationInput
  | RecordCaseContractChangeEngagementLinkInput
  | RecordCaseContractChangeImpactDeclarationInput;
type PendingIntent = { caseId: string; key: string; input: IntentInput };
type EvidenceUploadIntent = { input: PrepareCaseContractChangeEvidenceUploadInput; file: File };

const CHANGE_KINDS: Array<{ value: CaseContractChangeKind; label: string }> = [
  { value: "ORDER_OF_SERVICE", label: "Ordre de service / instruction" },
  { value: "CHANGE_REQUEST", label: "Demande de changement" },
  { value: "ADDENDUM", label: "Avenant" },
  { value: "SCHEDULE_CHANGE", label: "Changement de calendrier" },
];
const IMPACT_AXES: Array<{ value: CaseContractChangeImpactAxis; label: string }> = [
  { value: "SCOPE", label: "Périmètre" },
  { value: "COST", label: "Coût" },
  { value: "CASH", label: "Cash" },
  { value: "SCHEDULE", label: "Délai" },
  { value: "CAPACITY", label: "Capacité" },
];
const APPLICABILITY_CHOICES: Array<{ value: CaseContractChangeApplicability; label: string }> = [
  { value: "APPLICABLE_TO_HANDOVER", label: "À relier à cette passation" },
  { value: "NOT_APPLICABLE", label: "Non relié à cette passation" },
  { value: "NEEDS_CLARIFICATION", label: "À clarifier" },
];
const ids = () => ({
  command_id: crypto.randomUUID(),
  idempotency_key: crypto.randomUUID(),
  correlation_id: crypto.randomUUID(),
});
const refs = (value: string) => value.split("\n").map((item) => item.trim()).filter(Boolean);
const a1SourceKey = (source: A1EngagementSource) => [
  source.condition_id,
  source.requirement_id,
  source.requirement_revision,
  source.impact_id,
  source.impact_revision,
  source.profile_version_id,
  source.profile_version,
  source.profile_sha256,
].join(":");

export function CaseContractChangePanel({
  api,
  caseId,
  versions,
}: {
  api: ApiClient;
  caseId: string;
  versions: ContractInstrumentVersion[];
}) {
  const [events, setEvents] = useState<CaseContractChangeEvent[]>([]);
  const [handovers, setHandovers] = useState<Array<{
    snapshot_id: string; lot_reference: string; package_version: number; manifest_sha256: string;
  }>>([]);
  const [state, setState] = useState<ReadState>("LOADING");
  const [pending, setPending] = useState<PendingIntent | null>(null);
  const [submitting, setSubmitting] = useState<string | null>(null);
  const [failure, setFailure] = useState<{ key: string; kind: "UNCONFIRMED" | "REJECTED" } | null>(null);
  const [message, setMessage] = useState("");
  const [handoverId, setHandoverId] = useState("");
  const [changeKind, setChangeKind] = useState<CaseContractChangeKind>("ORDER_OF_SERVICE");
  const [declaredVersionId, setDeclaredVersionId] = useState("");
  const [issuer, setIssuer] = useState("");
  const [summary, setSummary] = useState("");
  const [scopeNote, setScopeNote] = useState("");
  const [sourceRefs, setSourceRefs] = useState("");
  const [evidenceRefs, setEvidenceRefs] = useState("");
  const [receivedAt, setReceivedAt] = useState(() => new Date().toISOString().slice(0, 16));
  const [reviewDrafts, setReviewDrafts] = useState<Record<string, {
    versionId: string; decision: CaseContractChangeApplicability; deltaState: "UNKNOWN" | "DECLARED";
    deltaNote: string; rationale: string; evidenceRefs: string;
  }>>({});
  const [actionDrafts, setActionDrafts] = useState<Record<string, {
    summary: string; evidenceRefs: string; dueAt: string; noDueReason: string;
  }>>({});
  const [engagementDrafts, setEngagementDrafts] = useState<Record<string, {
    state: "LINKED" | "UNKNOWN"; selectedKeys: string[]; rationale: string; unknownReason: string;
  }>>({});
  const [impactDrafts, setImpactDrafts] = useState<Record<string, {
    sourceKey: string; axis: CaseContractChangeImpactAxis; impactState: "DECLARED" | "UNKNOWN";
    impactSummary: string; impactUnknownReason: string;
    measurementState: "DECLARED" | "UNKNOWN"; value: string; currency: string; unit: string;
    measurementUnknownReason: string; assumptions: string; sourceRefs: string; evidenceRefs: string;
    rationale: string;
  }>>({});
  const [actionImpactDrafts, setActionImpactDrafts] = useState<Record<string, {
    state: "LINKED" | "UNKNOWN" | "NOT_APPLICABLE";
    declarationIds: string[]; rationale: string; reason: string;
  }>>({});
  const [executionDrafts, setExecutionDrafts] = useState<Record<string, {
    state: RecordCaseContractChangeActionExecutionInput["declared_state"];
    summary: string; unknownReason: string; evidenceRefs: string;
    evidenceObjectIds: string[];
    confirmation: "UNKNOWN" | "NOT_CONFIRMED"; confirmationNote: string;
  }>>({});
  const [executionEvidenceFiles, setExecutionEvidenceFiles] = useState<Record<string, File | null>>({});
  const [executionUploadIntents, setExecutionUploadIntents] = useState<Record<string, EvidenceUploadIntent>>({});
  const [externalConfirmationDrafts, setExternalConfirmationDrafts] = useState<Record<string, {
    evidenceObjectId: string; receivedAt: string; externalParty: string; rationale: string;
  }>>({});
  const [externalConfirmationFiles, setExternalConfirmationFiles] = useState<Record<string, File | null>>({});
  const [externalConfirmationUploadIntents, setExternalConfirmationUploadIntents] = useState<Record<string, {
    upload: EvidenceUploadIntent; confirmation: RecordCaseContractChangeExternalConfirmationInput;
  }>>({});
  const activeCaseId = useRef(caseId);

  useLayoutEffect(() => {
    activeCaseId.current = caseId;
    return () => { activeCaseId.current = ""; };
  }, [caseId]);

  async function refresh(targetCaseId = caseId) {
    const [eventResult, handoverResult] = await Promise.all([
      api.listCaseContractChangeEvents(targetCaseId),
      api.listCaseHandoverSnapshots(targetCaseId),
    ]);
    if (activeCaseId.current !== targetCaseId
      || eventResult.case_id !== targetCaseId
      || handoverResult.case_id !== targetCaseId) return;
    setEvents(eventResult.events);
    setHandovers(handoverResult.items);
    setState("READY");
  }

  useEffect(() => {
    setEvents([]);
    setHandovers([]);
    setPending(null);
    setSubmitting(null);
    setFailure(null);
    setMessage("");
    setHandoverId("");
    setReviewDrafts({});
    setActionDrafts({});
    setEngagementDrafts({});
    setImpactDrafts({});
    setActionImpactDrafts({});
    setExecutionDrafts({});
    setExecutionEvidenceFiles({});
    setExecutionUploadIntents({});
    setExternalConfirmationDrafts({});
    setExternalConfirmationFiles({});
    setExternalConfirmationUploadIntents({});
    let active = true;
    setState("LOADING");
    void refresh(caseId).catch(() => {
      if (active) setState("UNAVAILABLE");
    });
    return () => {
      active = false;
      activeCaseId.current = "";
    };
    // Both reads are keyed to the active, confirmed Case.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [api, caseId]);

  async function submit<T extends IntentInput>(
    key: string,
    create: () => T,
    send: (input: T) => Promise<unknown>,
  ) {
    if (pending && (pending.caseId !== caseId || pending.key !== key)) return;
    const existing = pending?.caseId === caseId && pending.key === key ? pending.input as T : null;
    const input = existing ?? create();
    if (!existing) setPending({ caseId, key, input });
    setSubmitting(key);
    setFailure(null);
    setMessage("");
    try {
      await send(input);
      if (activeCaseId.current !== caseId) return;
      await refresh();
      setPending(null);
      setMessage("Act Patron enregistré et relu depuis le serveur.");
    } catch (error) {
      if (activeCaseId.current !== caseId) return;
      const status = (error as { status?: number })?.status;
      if (status !== undefined && status >= 400 && status < 500) {
        setPending(null);
        setFailure({ key, kind: "REJECTED" });
      } else {
        setFailure({ key, kind: "UNCONFIRMED" });
      }
    } finally {
      if (activeCaseId.current === caseId) setSubmitting(null);
    }
  }

  function recordEvent(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!handoverId || !summary.trim() || !scopeNote.trim() || !receivedAt) return;
    const sourceRefsList = refs(sourceRefs);
    const evidenceRefsList = refs(evidenceRefs);
    if (!sourceRefsList.length || !evidenceRefsList.length) return;
    void submit(
      "event",
      () => ({
        ...ids(),
        event_id: crypto.randomUUID(),
        handover_snapshot_id: handoverId,
        change_kind: changeKind,
        contract_instrument_version_id: declaredVersionId || null,
        issuer: issuer.trim() || null,
        summary: summary.trim(),
        scope_note: scopeNote.trim(),
        source_refs: sourceRefsList,
        evidence_refs: evidenceRefsList,
        declared_received_at: new Date(receivedAt).toISOString(),
      }),
      (input) => api.recordCaseContractChangeEvent(caseId, input),
    );
  }

  function recordApplicability(event: CaseContractChangeEvent) {
    const draft = reviewDrafts[event.event_id];
    const versionId = event.declared_instrument?.contract_instrument_version_id ?? draft?.versionId;
    if (!versionId || !draft?.rationale.trim() || !refs(draft.evidenceRefs).length
      || (draft.deltaState === "DECLARED" && !draft.deltaNote.trim())) return;
    void submit(
      "review:" + event.event_id,
      () => ({
        ...ids(),
        review_id: crypto.randomUUID(),
        handover_snapshot_id: event.handover_snapshot_id,
        contract_instrument_version_id: versionId,
        expected_revision: event.applicability_history.length,
        decision: draft.decision,
        delta_state: draft.deltaState,
        delta_note: draft.deltaState === "DECLARED" ? draft.deltaNote.trim() : null,
        rationale: draft.rationale.trim(),
        evidence_refs: refs(draft.evidenceRefs),
      }),
      (input) => api.recordCaseContractChangeApplicability(caseId, event.event_id, input),
    );
  }

  function recordAction(event: CaseContractChangeEvent) {
    const draft = actionDrafts[event.event_id];
    const latestReview = event.applicability_history.at(-1);
    if (!latestReview || latestReview.decision !== "APPLICABLE_TO_HANDOVER"
      || !draft?.summary.trim() || !refs(draft.evidenceRefs).length
      || (!draft.dueAt && !draft.noDueReason.trim())) return;
    void submit(
      "action:" + event.event_id,
      () => ({
        ...ids(),
        action_id: crypto.randomUUID(),
        applicability_review_id: latestReview.review_id,
        expected_revision: event.actions.length,
        action_summary: draft.summary.trim(),
        evidence_refs: refs(draft.evidenceRefs),
        due_at: draft.dueAt ? new Date(draft.dueAt).toISOString() : null,
        due_date_absence_reason: draft.dueAt ? null : draft.noDueReason.trim(),
      }),
      (input) => api.recordCaseContractChangeAction(caseId, event.event_id, input),
    );
  }

  function recordEngagementLink(event: CaseContractChangeEvent) {
    const draft = engagementDrafts[event.event_id];
    if (!draft?.rationale.trim()) return;
    const selectedSources = event.a1_engagements.filter((source) =>
      draft.selectedKeys.includes(a1SourceKey(source))
    );
    if (draft.state === "LINKED" && !selectedSources.length) return;
    if (draft.state === "UNKNOWN" && !draft.unknownReason.trim()) return;
    void submit(
      "engagement-link:" + event.event_id,
      () => ({
        ...ids(),
        linkage_id: crypto.randomUUID(),
        expected_revision: event.engagement_linkage_history.length,
        state: draft.state,
        selected_sources: selectedSources,
        rationale: draft.rationale.trim(),
        unknown_reason: draft.state === "UNKNOWN" ? draft.unknownReason.trim() : null,
      }),
      (input) => api.recordCaseContractChangeEngagementLink(caseId, event.event_id, input),
    );
  }

  function recordImpactDeclaration(event: CaseContractChangeEvent) {
    const draft = impactDrafts[event.event_id];
    const linkage = event.engagement_linkage_history.at(-1);
    const source = linkage?.selected_sources.find(
      (item) => a1SourceKey(item) === draft?.sourceKey
    );
    if (!draft || !linkage || linkage.state !== "LINKED" || !source || !draft.rationale.trim()) {
      return;
    }
    if (draft.impactState === "DECLARED" && !draft.impactSummary.trim()) return;
    if (draft.impactState === "UNKNOWN" && !draft.impactUnknownReason.trim()) return;
    if (draft.impactState === "DECLARED" && !refs(draft.sourceRefs).length) return;
    if (draft.impactState === "DECLARED" && !refs(draft.evidenceRefs).length) return;
    if (draft.axis !== "SCOPE" && draft.impactState === "DECLARED") {
      if (draft.measurementState === "UNKNOWN" && !draft.measurementUnknownReason.trim()) return;
      if (draft.measurementState === "DECLARED" && !draft.value.trim()) return;
      if (draft.axis === "COST" || draft.axis === "CASH") {
        if (draft.measurementState === "DECLARED" && !draft.currency.trim()) return;
      } else if (draft.measurementState === "DECLARED" && !draft.unit.trim()) return;
    }
    const impactKey = "impact:" + event.event_id;
    const priorRevisionCount = event.impact_declarations.filter((item) =>
      item.linkage_id === linkage.linkage_id
      && item.axis === draft.axis
      && a1SourceKey(item.source) === a1SourceKey(source)
    ).length;
    void submit(
      impactKey,
      () => ({
        ...ids(),
        declaration_id: crypto.randomUUID(),
        linkage_id: linkage.linkage_id,
        source,
        expected_revision: priorRevisionCount,
        axis: draft.axis,
        impact_state: draft.impactState,
        impact_summary: draft.impactState === "DECLARED" ? draft.impactSummary.trim() : null,
        impact_unknown_reason: draft.impactState === "UNKNOWN" ? draft.impactUnknownReason.trim() : null,
        measurement_state: draft.axis === "SCOPE"
          ? "NOT_APPLICABLE" as const
          : draft.impactState === "UNKNOWN" ? "UNKNOWN" as const : draft.measurementState,
        value_as_declared: draft.impactState === "DECLARED"
          && draft.measurementState === "DECLARED" && draft.axis !== "SCOPE"
          ? draft.value.trim() : null,
        currency_code: draft.impactState === "DECLARED"
          && draft.measurementState === "DECLARED"
          && (draft.axis === "COST" || draft.axis === "CASH") ? draft.currency.trim() : null,
        unit: draft.impactState === "DECLARED"
          && draft.measurementState === "DECLARED"
          && (draft.axis === "SCHEDULE" || draft.axis === "CAPACITY") ? draft.unit.trim() : null,
        measurement_unknown_reason: draft.impactState === "DECLARED"
          && draft.measurementState === "UNKNOWN" && draft.axis !== "SCOPE"
          ? draft.measurementUnknownReason.trim() : null,
        assumptions: refs(draft.assumptions),
        source_refs: refs(draft.sourceRefs),
        evidence_refs: draft.impactState === "DECLARED" ? refs(draft.evidenceRefs) : [],
        rationale: draft.rationale.trim(),
      }),
      (input) => api.recordCaseContractChangeImpactDeclaration(caseId, event.event_id, input),
    );
  }

  function recordActionImpactRelation(event: CaseContractChangeEvent, actionId: string) {
    const draft = actionImpactDrafts[actionId];
    const latestReview = event.applicability_history.at(-1);
    const selected = event.impact_declarations.filter((item) =>
      draft?.declarationIds.includes(item.declaration_id) && item.linkage_state === "CURRENT"
    );
    if (!draft || !latestReview || latestReview.decision !== "APPLICABLE_TO_HANDOVER"
      || !draft.rationale.trim()) return;
    if (draft.state === "LINKED" && !selected.length) return;
    if (draft.state !== "LINKED" && !draft.reason.trim()) return;
    const key = "c4:" + actionId;
    void submit(
      key,
      () => ({
        ...ids(),
        relation_id: crypto.randomUUID(),
        expected_revision: event.action_impact_relations.filter(
          (item) => item.action_id === actionId
        ).length,
        state: draft.state,
        declaration_ids: draft.state === "LINKED"
          ? selected.map((item) => item.declaration_id) : [],
        rationale: draft.rationale.trim(),
        unknown_reason: draft.state === "LINKED" ? null : draft.reason.trim(),
      }),
      (input) => api.recordCaseContractChangeActionImpactRelation(
        caseId, event.event_id, actionId, input
      ),
    );
  }

  function recordActionExecution(event: CaseContractChangeEvent, actionId: string) {
    const draft = executionDrafts[actionId];
    const c4 = event.action_impact_relations.filter((item) => item.action_id === actionId).at(-1);
    if (!draft || !c4) return;
    const key = "c5:" + actionId;
    const selectedFile = executionEvidenceFiles[actionId] ?? null;
    let uploadIntent = executionUploadIntents[actionId];
    if (selectedFile && (!uploadIntent
      || uploadIntent.input.c4_relation_id !== c4.relation_id
      || uploadIntent.file.name !== selectedFile.name
      || uploadIntent.file.size !== selectedFile.size
      || uploadIntent.file.lastModified !== selectedFile.lastModified)) {
      uploadIntent = {
        input: {
          ...ids(),
          evidence_object_id: crypto.randomUUID(),
          c4_relation_id: c4.relation_id,
          evidence_kind: "EXECUTION_EVIDENCE",
          expected_byte_size: selectedFile.size,
        },
        file: selectedFile,
      };
      setExecutionUploadIntents((current) => ({ ...current, [actionId]: uploadIntent! }));
    }
    const evidenceObjectIds = [...new Set([
      ...draft.evidenceObjectIds,
      ...(uploadIntent ? [uploadIntent.input.evidence_object_id] : []),
    ])];
    void submit(
      key,
      () => ({
        ...ids(),
        act_id: crypto.randomUUID(),
        c4_relation_id: c4.relation_id,
        expected_revision: event.action_execution_acts.filter((item) => item.action_id === actionId).length,
        declared_state: draft.state,
        declared_summary: draft.state === "UNKNOWN" ? null : draft.summary.trim(),
        unknown_reason: draft.state === "UNKNOWN" ? draft.unknownReason.trim() : null,
        evidence_refs: refs(draft.evidenceRefs),
        evidence_object_ids: evidenceObjectIds,
        external_confirmation_state: draft.confirmation,
        external_confirmation_note: draft.confirmation === "NOT_CONFIRMED"
          ? draft.confirmationNote.trim() : null,
      }),
      async (input) => {
        if (uploadIntent) {
          try {
            await api.prepareCaseContractChangeEvidenceUpload(
              caseId, event.event_id, actionId, uploadIntent.input
            );
            await api.uploadCaseContractChangeEvidence(
              caseId,
              event.event_id,
              actionId,
              uploadIntent.input.evidence_object_id,
              uploadIntent.input.idempotency_key,
              uploadIntent.file,
            );
          } catch (error) {
            const status = (error as { status?: number })?.status;
            if (status !== undefined && status >= 400 && status < 500 && status !== 401) {
              setExecutionUploadIntents((current) => {
                const next = { ...current };
                delete next[actionId];
                return next;
              });
            }
            throw error;
          }
        }
        await api.recordCaseContractChangeActionExecution(caseId, event.event_id, actionId, input);
        setExecutionUploadIntents((current) => {
          const next = { ...current };
          delete next[actionId];
          return next;
        });
        setExecutionEvidenceFiles((current) => ({ ...current, [actionId]: null }));
      },
    );
  }

  function recordExternalConfirmation(
    event: CaseContractChangeEvent,
    act: CaseContractChangeEvent["action_execution_acts"][number],
  ) {
    const draft = externalConfirmationDrafts[act.act_id];
    if (!draft?.rationale.trim() || !draft.receivedAt) return;
    const key = "c5-confirmation:" + act.act_id;
    const selectedFile = externalConfirmationFiles[act.act_id] ?? null;
    let pendingUpload = externalConfirmationUploadIntents[act.act_id];
    let confirmation: RecordCaseContractChangeExternalConfirmationInput;
    if (selectedFile && (!pendingUpload
      || pendingUpload.upload.input.c4_relation_id !== act.c4_relation_id
      || pendingUpload.upload.file.name !== selectedFile.name
      || pendingUpload.upload.file.size !== selectedFile.size
      || pendingUpload.upload.file.lastModified !== selectedFile.lastModified)) {
      const upload: EvidenceUploadIntent = {
        input: {
          ...ids(),
          evidence_object_id: crypto.randomUUID(),
          c4_relation_id: act.c4_relation_id,
          evidence_kind: "EXTERNAL_CONFIRMATION",
          expected_byte_size: selectedFile.size,
        },
        file: selectedFile,
      };
      confirmation = {
        ...ids(),
        confirmation_id: crypto.randomUUID(),
        c4_relation_id: act.c4_relation_id,
        evidence_object_id: upload.input.evidence_object_id,
        expected_revision: act.external_confirmation_acts.length,
        received_at: new Date(draft.receivedAt).toISOString(),
        external_party: draft.externalParty.trim() || null,
        rationale: draft.rationale.trim(),
      };
      pendingUpload = { upload, confirmation };
      setExternalConfirmationUploadIntents((current) => ({ ...current, [act.act_id]: pendingUpload! }));
    } else if (pendingUpload) {
      confirmation = pendingUpload.confirmation;
    } else {
      const source = event.evidence_objects.find((item) =>
        item.evidence_object_id === draft.evidenceObjectId
        && item.action_id === act.action_id
        && item.c4_relation_id === act.c4_relation_id
        && item.evidence_kind === "EXTERNAL_CONFIRMATION"
        && item.state === "CLEAN"
      );
      if (!source) return;
      confirmation = {
        ...ids(),
        confirmation_id: crypto.randomUUID(),
        c4_relation_id: act.c4_relation_id,
        evidence_object_id: source.evidence_object_id,
        expected_revision: act.external_confirmation_acts.length,
        received_at: new Date(draft.receivedAt).toISOString(),
        external_party: draft.externalParty.trim() || null,
        rationale: draft.rationale.trim(),
      };
    }
    void submit(
      key,
      () => confirmation,
      async (input) => {
        if (pendingUpload) {
          try {
            await api.prepareCaseContractChangeEvidenceUpload(
              caseId, event.event_id, act.action_id, pendingUpload.upload.input
            );
            await api.uploadCaseContractChangeEvidence(
              caseId,
              event.event_id,
              act.action_id,
              pendingUpload.upload.input.evidence_object_id,
              pendingUpload.upload.input.idempotency_key,
              pendingUpload.upload.file,
            );
          } catch (error) {
            const status = (error as { status?: number })?.status;
            if (status !== undefined && status >= 400 && status < 500 && status !== 401) {
              setExternalConfirmationUploadIntents((current) => {
                const next = { ...current };
                delete next[act.act_id];
                return next;
              });
            }
            throw error;
          }
        }
        await api.recordCaseContractChangeExternalConfirmation(
          caseId, event.event_id, act.action_id, act.act_id, input
        );
        setExternalConfirmationUploadIntents((current) => {
          const next = { ...current };
          delete next[act.act_id];
          return next;
        });
        setExternalConfirmationFiles((current) => ({ ...current, [act.act_id]: null }));
      },
    );
  }

  const blocked = !!pending;
  return (
    <section className="section-block decision-section" aria-label="Événements contractuels C1">
      <div className="section-heading"><div><span className="section-kicker">VERTICALE C · C1</span><h2>Changement contractuel lié à la passation</h2></div></div>
      <p>Événement, version, applicabilité humaine, action et preuve restent des actes séparés. Aucun delta de coût/délai/cash ni effet juridique n’est calculé automatiquement.</p>
      {state === "LOADING" && <p role="status">Lecture des événements contractuels…</p>}
      {state === "UNAVAILABLE" && <p role="status">UNAVAILABLE · aucune projection confirmée n’est affichée.</p>}
      {state === "READY" && events.length === 0 && <p>UNKNOWN · aucun événement contractuel n’est relié à une passation B1.</p>}
      {events.map((event) => {
        const review = reviewDrafts[event.event_id] ?? {
          versionId: "",
          decision: "NEEDS_CLARIFICATION" as const,
          deltaState: "UNKNOWN" as const,
          deltaNote: "",
          rationale: "",
          evidenceRefs: "",
        };
        const action = actionDrafts[event.event_id] ?? {
          summary: "",
          evidenceRefs: "",
          dueAt: "",
          noDueReason: "",
        };
        const latestReview = event.applicability_history.at(-1);
        const engagement = engagementDrafts[event.event_id] ?? {
          state: "UNKNOWN" as const,
          selectedKeys: [],
          rationale: "",
          unknownReason: "",
        };
        const currentLinkage = event.engagement_linkage_history.at(-1);
        const impactDraft = impactDrafts[event.event_id] ?? {
          sourceKey: currentLinkage?.selected_sources[0]
            ? a1SourceKey(currentLinkage.selected_sources[0]) : "",
          axis: "COST" as const,
          impactState: "UNKNOWN" as const,
          impactSummary: "",
          impactUnknownReason: "",
          measurementState: "UNKNOWN" as const,
          value: "",
          currency: "EUR",
          unit: "",
          measurementUnknownReason: "",
          assumptions: "",
          sourceRefs: event.source_refs.join("\n"),
          evidenceRefs: "",
          rationale: "",
        };
        return <article className="detail-panel" key={event.event_id}>
          <h3>{CHANGE_KINDS.find((kind) => kind.value === event.change_kind)?.label ?? event.change_kind} · lot {event.lot_reference}</h3>
          <p>Passation B1 : paquet P5 v{event.offer_package_version} · SHA-256 {event.offer_manifest_sha256}</p>
          <p>Événement reçu : {event.declared_received_at} · source : {event.source_refs.join(" · ")}</p>
          <p>Émetteur déclaré : {event.issuer ?? "UNKNOWN"} · preuves : {event.evidence_refs.join(" · ")}</p>
          <p>{event.summary} · périmètre déclaré : {event.scope_note}</p>
          <p>Version contrat déclarée : {event.declared_instrument
            ? event.declared_instrument.instrument_kind + " · " + event.declared_instrument.version_reference
            : "UNKNOWN · aucun lien versionnel déclaré"}.</p>
          <p>Applicabilité à cette passation : {event.applicability_state}. Ce statut ne constitue pas une conclusion juridique.</p>
          <section aria-label={"Engagements A1 concernés " + event.event_id}>
            <h4>Engagements A1 figés dans la passation B1</h4>
            {event.a1_engagements_state === "UNKNOWN" || event.a1_engagements.length === 0
              ? <p>UNKNOWN · aucun engagement A1 sourcé n’est présent dans ce snapshot B1.</p>
              : <ul>{event.a1_engagements.map((source) => <li key={a1SourceKey(source)}>
                Condition {source.condition_id} · exigence {source.requirement_id} r{source.requirement_revision} · impact {source.impact_id} r{source.impact_revision} · profil {source.profile_version} · SHA-256 {source.profile_sha256}
              </li>)}</ul>}
            <p>Lien humain avec cet événement : {event.engagement_linkage_state}. Il ne modifie ni A1, ni le snapshot B1, ni l’événement C1.</p>
            {event.engagement_linkage_history.map((item) => <p key={item.linkage_id}>
              Acte Patron r{item.revision} : {item.state} · {item.rationale}{item.unknown_reason ? " · Motif UNKNOWN : " + item.unknown_reason : ""} · sources sélectionnées : {item.selected_sources.length}
            </p>)}
            <form onSubmit={(formEvent) => { formEvent.preventDefault(); recordEngagementLink(event); }}>
              <label>État du rapprochement A1/C1
                <select aria-label={"État du lien A1/C1 " + event.event_id} value={engagement.state} disabled={blocked} onChange={(formEvent) => setEngagementDrafts((current) => ({ ...current, [event.event_id]: { ...engagement, state: formEvent.target.value as "LINKED" | "UNKNOWN" } }))}>
                  <option value="UNKNOWN">UNKNOWN · aucun engagement sélectionné</option>
                  <option value="LINKED">Engagements sélectionnés par le Patron</option>
                </select>
              </label>
              {engagement.state === "LINKED" && event.a1_engagements.map((source) => {
                const key = a1SourceKey(source);
                return <label key={key}>
                  <input type="checkbox" aria-label={"Sélectionner la condition A1 " + source.condition_id} checked={engagement.selectedKeys.includes(key)} disabled={blocked} onChange={(formEvent) => setEngagementDrafts((current) => ({
                    ...current,
                    [event.event_id]: {
                      ...engagement,
                      selectedKeys: formEvent.target.checked
                        ? [...engagement.selectedKeys, key]
                        : engagement.selectedKeys.filter((selected) => selected !== key),
                    },
                  }))} />
                  Sélectionner condition {source.condition_id} · impact {source.impact_id} r{source.impact_revision}
                </label>;
              })}
              {engagement.state === "UNKNOWN" && <label>Motif explicite de l’inconnu<input required maxLength={1000} value={engagement.unknownReason} disabled={blocked} onChange={(formEvent) => setEngagementDrafts((current) => ({ ...current, [event.event_id]: { ...engagement, unknownReason: formEvent.target.value } }))} /></label>}
              <label>Justification Patron<textarea required maxLength={2000} value={engagement.rationale} disabled={blocked} onChange={(formEvent) => setEngagementDrafts((current) => ({ ...current, [event.event_id]: { ...engagement, rationale: formEvent.target.value } }))} /></label>
              <button type="submit" disabled={blocked || (engagement.state === "LINKED" && (!event.a1_engagements.length || !engagement.selectedKeys.length))}>
                {submitting === "engagement-link:" + event.event_id ? "Enregistrement…" : failure?.key === "engagement-link:" + event.event_id && failure.kind === "UNCONFIRMED" ? "Réessayer le même lien" : "Enregistrer le lien Patron A1/C1"}
              </button>
            </form>
          </section>
          <section aria-label={"Impacts déclarés C3 " + event.event_id}>
            <h4>Impact humain du changement sur l’engagement A1</h4>
            {event.impact_declarations.length === 0
              && <p>UNKNOWN · aucun impact post-événement n’est encore déclaré sur une source A1.</p>}
            {event.impact_declarations.map((item) => <p key={item.declaration_id}>
              C3 r{item.revision} · {IMPACT_AXES.find((axis) => axis.value === item.axis)?.label ?? item.axis} · {item.impact_state}
              {item.impact_summary ? " · " + item.impact_summary : ""}
              {item.impact_unknown_reason ? " · Motif : " + item.impact_unknown_reason : ""}
              {item.measurement_state === "DECLARED"
                ? " · Valeur déclarée " + item.value_as_declared + " " + (item.currency_code ?? item.unit)
                : item.measurement_state === "UNKNOWN" ? " · Mesure UNKNOWN : " + (item.measurement_unknown_reason ?? item.impact_unknown_reason) : ""}
              {item.linkage_state === "REVIEW_REQUIRED" ? " · REVIEW_REQUIRED — liaison C2 remplacée" : ""}
            </p>)}
            {!currentLinkage || currentLinkage.state !== "LINKED"
              ? <p>UNKNOWN · une liaison C2 `LINKED` est requise avant d’attribuer l’impact à une source A1.</p>
              : <form onSubmit={(formEvent) => { formEvent.preventDefault(); recordImpactDeclaration(event); }}>
                <label>Source A1 liée en C2
                  <select aria-label={"Source A1 de l’impact C3 " + event.event_id} value={impactDraft.sourceKey} disabled={blocked} onChange={(formEvent) => setImpactDrafts((current) => ({ ...current, [event.event_id]: { ...impactDraft, sourceKey: formEvent.target.value } }))}>
                    {currentLinkage.selected_sources.map((source) => <option key={a1SourceKey(source)} value={a1SourceKey(source)}>
                      Condition {source.condition_id} · impact {source.impact_id} r{source.impact_revision}
                    </option>)}
                  </select>
                </label>
                <label>Axe d’impact déclaré
                  <select aria-label={"Axe d’impact C3 " + event.event_id} value={impactDraft.axis} disabled={blocked} onChange={(formEvent) => {
                    const axis = formEvent.target.value as CaseContractChangeImpactAxis;
                    setImpactDrafts((current) => ({ ...current, [event.event_id]: {
                      ...impactDraft,
                      axis,
                      measurementState: "UNKNOWN",
                    } }));
                  }}>
                    {IMPACT_AXES.map((axis) => <option key={axis.value} value={axis.value}>{axis.label}</option>)}
                  </select>
                </label>
                <label>État de l’impact
                  <select aria-label={"État de l’impact C3 " + event.event_id} value={impactDraft.impactState} disabled={blocked} onChange={(formEvent) => setImpactDrafts((current) => ({ ...current, [event.event_id]: { ...impactDraft, impactState: formEvent.target.value as "DECLARED" | "UNKNOWN" } }))}>
                    <option value="UNKNOWN">UNKNOWN · effet non établi</option>
                    <option value="DECLARED">Impact déclaré par le Patron</option>
                  </select>
                </label>
                {impactDraft.impactState === "DECLARED" && <label>Description de l’impact déclaré<textarea required maxLength={2000} value={impactDraft.impactSummary} disabled={blocked} onChange={(formEvent) => setImpactDrafts((current) => ({ ...current, [event.event_id]: { ...impactDraft, impactSummary: formEvent.target.value } }))} /></label>}
                {impactDraft.impactState === "UNKNOWN" && <label>Motif de l’impact inconnu<input required maxLength={1000} value={impactDraft.impactUnknownReason} disabled={blocked} onChange={(formEvent) => setImpactDrafts((current) => ({ ...current, [event.event_id]: { ...impactDraft, impactUnknownReason: formEvent.target.value } }))} /></label>}
                {impactDraft.axis !== "SCOPE" && impactDraft.impactState === "DECLARED" && <label>État de la mesure
                  <select aria-label={"État de la mesure C3 " + event.event_id} value={impactDraft.measurementState} disabled={blocked} onChange={(formEvent) => setImpactDrafts((current) => ({ ...current, [event.event_id]: { ...impactDraft, measurementState: formEvent.target.value as "DECLARED" | "UNKNOWN" } }))}>
                    <option value="UNKNOWN">UNKNOWN · quantité non confirmée</option>
                    <option value="DECLARED">Valeur déclarée par le Patron</option>
                  </select>
                </label>}
                {impactDraft.axis !== "SCOPE" && impactDraft.impactState === "DECLARED" && impactDraft.measurementState === "DECLARED" && <>
                  <label>Valeur déclarée, sans calcul<input required maxLength={80} value={impactDraft.value} disabled={blocked} onChange={(formEvent) => setImpactDrafts((current) => ({ ...current, [event.event_id]: { ...impactDraft, value: formEvent.target.value } }))} /></label>
                  {(impactDraft.axis === "COST" || impactDraft.axis === "CASH")
                    ? <label>Devise déclarée<input required maxLength={3} pattern="[A-Z]{3}" value={impactDraft.currency} disabled={blocked} onChange={(formEvent) => setImpactDrafts((current) => ({ ...current, [event.event_id]: { ...impactDraft, currency: formEvent.target.value.toUpperCase() } }))} /></label>
                    : <label>Unité déclarée<input required maxLength={32} value={impactDraft.unit} disabled={blocked} onChange={(formEvent) => setImpactDrafts((current) => ({ ...current, [event.event_id]: { ...impactDraft, unit: formEvent.target.value } }))} /></label>}
                </>}
                {impactDraft.axis !== "SCOPE" && impactDraft.impactState === "DECLARED" && impactDraft.measurementState === "UNKNOWN" && <label>Motif de mesure inconnue<input required maxLength={1000} value={impactDraft.measurementUnknownReason} disabled={blocked} onChange={(formEvent) => setImpactDrafts((current) => ({ ...current, [event.event_id]: { ...impactDraft, measurementUnknownReason: formEvent.target.value } }))} /></label>}
                <label>Hypothèses, une par ligne<textarea value={impactDraft.assumptions} disabled={blocked} onChange={(formEvent) => setImpactDrafts((current) => ({ ...current, [event.event_id]: { ...impactDraft, assumptions: formEvent.target.value } }))} /></label>
                <label>Sources de l’impact, une par ligne<textarea required value={impactDraft.sourceRefs} disabled={blocked} onChange={(formEvent) => setImpactDrafts((current) => ({ ...current, [event.event_id]: { ...impactDraft, sourceRefs: formEvent.target.value } }))} /></label>
                {impactDraft.impactState === "DECLARED" && <label>Preuves, une par ligne<textarea required value={impactDraft.evidenceRefs} disabled={blocked} onChange={(formEvent) => setImpactDrafts((current) => ({ ...current, [event.event_id]: { ...impactDraft, evidenceRefs: formEvent.target.value } }))} /></label>}
                <label>Justification Patron C3<textarea required maxLength={2000} value={impactDraft.rationale} disabled={blocked} onChange={(formEvent) => setImpactDrafts((current) => ({ ...current, [event.event_id]: { ...impactDraft, rationale: formEvent.target.value } }))} /></label>
                <button type="submit" disabled={blocked || !currentLinkage.selected_sources.length}>
                  {submitting === "impact:" + event.event_id ? "Enregistrement…" : failure?.key === "impact:" + event.event_id && failure.kind === "UNCONFIRMED" ? "Réessayer le même impact" : "Enregistrer l’impact Patron C3"}
                </button>
                <p>Les valeurs restent déclarées ; elles ne modifient ni A1, ni la passation B1, ni l’événement C1 et ne sont pas calculées.</p>
              </form>}
          </section>
          {event.applicability_history.map((item) => <p key={item.review_id}>
            Revue Patron r{item.revision} : {item.decision} · version déclarée {item.contract_instrument?.version_reference ?? item.contract_instrument_version_id} · delta {item.delta_state}{item.delta_note ? " · " + item.delta_note : ""} · {item.rationale} · preuves : {item.evidence_refs.join(" · ")}
          </p>)}
          {event.applicability_state !== "APPLICABLE_TO_HANDOVER" && <form onSubmit={(formEvent) => { formEvent.preventDefault(); recordApplicability(event); }}>
            <label>{event.applicability_history.length ? "Réviser le lien humain vers la version contrat" : "Version contrat retenue par le Patron"}
              <select required aria-label={"Version contrat retenue " + event.event_id} value={review.versionId} disabled={blocked || !!event.declared_instrument} onChange={(formEvent) => setReviewDrafts((current) => ({ ...current, [event.event_id]: { ...review, versionId: formEvent.target.value } }))}>
                <option value="">Choisir une version déclarée, ou conserver UNKNOWN</option>
                {versions.map((version) => <option key={version.contract_instrument_version_id} value={version.contract_instrument_version_id}>{version.instrument_kind} · {version.version_reference}</option>)}
              </select>
            </label>
            <label>Décision humaine sur le lien
              <select aria-label={"Décision d’applicabilité " + event.event_id} value={review.decision} disabled={blocked} onChange={(formEvent) => setReviewDrafts((current) => ({ ...current, [event.event_id]: { ...review, decision: formEvent.target.value as CaseContractChangeApplicability } }))}>
                {APPLICABILITY_CHOICES.map((choice) => <option key={choice.value} value={choice.value}>{choice.label}</option>)}
              </select>
            </label>
            <label>État du delta déclaré
              <select aria-label={"État du delta " + event.event_id} value={review.deltaState} disabled={blocked} onChange={(formEvent) => setReviewDrafts((current) => ({ ...current, [event.event_id]: { ...review, deltaState: formEvent.target.value as "UNKNOWN" | "DECLARED" } }))}>
                <option value="UNKNOWN">UNKNOWN · aucun delta évalué</option>
                <option value="DECLARED">Delta déclaré par le Patron</option>
              </select>
            </label>
            {review.deltaState === "DECLARED" && <label>Delta résumé déclaré (aucun calcul automatique)<textarea required maxLength={2000} value={review.deltaNote} disabled={blocked} onChange={(formEvent) => setReviewDrafts((current) => ({ ...current, [event.event_id]: { ...review, deltaNote: formEvent.target.value } }))} /></label>}
            <label>Justification de revue<textarea required maxLength={2000} value={review.rationale} disabled={blocked} onChange={(formEvent) => setReviewDrafts((current) => ({ ...current, [event.event_id]: { ...review, rationale: formEvent.target.value } }))} /></label>
            <label>Sources/preuves de la décision, une par ligne<textarea required value={review.evidenceRefs} disabled={blocked} onChange={(formEvent) => setReviewDrafts((current) => ({ ...current, [event.event_id]: { ...review, evidenceRefs: formEvent.target.value } }))} /></label>
            <button type="submit" disabled={blocked || !versions.length}>{submitting === "review:" + event.event_id ? "Enregistrement…" : failure?.key === "review:" + event.event_id && failure.kind === "UNCONFIRMED" ? "Réessayer la même revue" : "Enregistrer la revue Patron"}</button>
          </form>}
          {event.applicability_state === "APPLICABLE_TO_HANDOVER" && latestReview && <form onSubmit={(formEvent) => { formEvent.preventDefault(); recordAction(event); }}>
            <h4>Action et preuve Patron</h4>
            <label>Action déclarée<textarea required maxLength={2000} value={action.summary} disabled={blocked} onChange={(formEvent) => setActionDrafts((current) => ({ ...current, [event.event_id]: { ...action, summary: formEvent.target.value } }))} /></label>
            <label>Sources/preuves liées à l’action, une par ligne<textarea required value={action.evidenceRefs} disabled={blocked} onChange={(formEvent) => setActionDrafts((current) => ({ ...current, [event.event_id]: { ...action, evidenceRefs: formEvent.target.value } }))} /></label>
            <label>Date d’action déclarée (facultative, non calculée)<input type="datetime-local" value={action.dueAt} disabled={blocked} onChange={(formEvent) => setActionDrafts((current) => ({ ...current, [event.event_id]: { ...action, dueAt: formEvent.target.value } }))} /></label>
            {!action.dueAt && <label>Motif d’échéance inconnue<input required value={action.noDueReason} disabled={blocked} onChange={(formEvent) => setActionDrafts((current) => ({ ...current, [event.event_id]: { ...action, noDueReason: formEvent.target.value } }))} /></label>}
            <button type="submit" disabled={blocked}>{submitting === "action:" + event.event_id ? "Enregistrement…" : failure?.key === "action:" + event.event_id && failure.kind === "UNCONFIRMED" ? "Réessayer la même action" : "Enregistrer l’action et la preuve"}</button>
          </form>}
          {event.actions.map((item) => <p key={item.action_id}>Action r{item.revision} · {item.state} · {item.summary} · preuves : {item.evidence_refs.join(" · ")} · échéance : {item.due_at ?? item.due_date_absence_reason}</p>)}
          <section aria-label={"Déclarations d’exécution C5 " + event.event_id}>
            <h4>Exécution déclarée C5</h4>
            {event.evidence_objects.map((source) => <p key={source.evidence_object_id}>
              Source C5 {source.evidence_kind} · {source.state} · action {source.action_id} · C4 {source.c4_relation_id}
              {source.sha256 ? " · SHA-256 " + source.sha256 : ""}
              {source.media_type ? " · " + source.media_type : ""}
            </p>)}
            {event.action_execution_acts.map((act) => {
              const confirmationDraft = externalConfirmationDrafts[act.act_id] ?? {
                evidenceObjectId: event.evidence_objects.find((source) =>
                  source.action_id === act.action_id
                  && source.c4_relation_id === act.c4_relation_id
                  && source.evidence_kind === "EXTERNAL_CONFIRMATION"
                  && source.state === "CLEAN"
                )?.evidence_object_id ?? "",
                receivedAt: new Date().toISOString().slice(0, 16),
                externalParty: "",
                rationale: "",
              };
              return <div key={act.act_id}>
                <p>
                  C5 r{act.revision} · {act.declared_state} · pièce {act.evidence_state}
                  {act.evidence_refs.length ? " · références déclarées : " + act.evidence_refs.join(" · ") : " · aucune pièce déclarée"}
                  {" · confirmation externe " + act.external_confirmation_state + " · C4 " + act.c4_projection_state}
                  {act.declared_summary ? " · " + act.declared_summary : " · " + act.unknown_reason}
                </p>
                {act.evidence_objects.map((source) => <p key={source.evidence_object_id}>
                  Pièce retrouvée C5 v{source.version} · {source.sha256} · {source.media_type} · {source.actual_byte_size} octets
                </p>)}
                {act.external_confirmation_acts.map((confirmation) => <p key={confirmation.confirmation_id}>
                  Confirmation externe append-only r{confirmation.revision} · reçue le {confirmation.received_at}
                  {confirmation.external_party ? " · " + confirmation.external_party : ""}
                  {" · pièce " + confirmation.evidence_sha256 + " · " + confirmation.rationale}
                </p>)}
                {act.external_confirmation_state !== "CONFIRMED" && <form onSubmit={(formEvent) => {
                  formEvent.preventDefault(); recordExternalConfirmation(event, act);
                }}>
                  <h5>Enregistrer une confirmation externe reçue</h5>
                  <label>Pièce externe assainie déjà déposée
                    <select aria-label={"Pièce externe C5 " + act.act_id} value={confirmationDraft.evidenceObjectId} disabled={blocked} onChange={(formEvent) => setExternalConfirmationDrafts((current) => ({
                      ...current,
                      [act.act_id]: { ...confirmationDraft, evidenceObjectId: formEvent.target.value },
                    }))}>
                      <option value="">Choisir un accusé externe ou joindre un fichier</option>
                      {event.evidence_objects.filter((source) => source.action_id === act.action_id
                        && source.c4_relation_id === act.c4_relation_id
                        && source.evidence_kind === "EXTERNAL_CONFIRMATION"
                        && source.state === "CLEAN").map((source) => <option key={source.evidence_object_id} value={source.evidence_object_id}>
                        {source.evidence_object_id} · SHA-256 {source.sha256}
                      </option>)}
                    </select>
                  </label>
                  <label>Ou joindre la confirmation externe reçue
                    <input type="file" accept=".pdf,.doc,.docx,.xls,.xlsx,.ods,.odt,.zip,.jpg,.jpeg,.png,.tif,.tiff"
                      disabled={blocked} onChange={(formEvent) => setExternalConfirmationFiles((current) => ({
                        ...current, [act.act_id]: formEvent.target.files?.[0] ?? null,
                      }))} />
                  </label>
                  <label>Date de réception déclarée<input type="datetime-local" required value={confirmationDraft.receivedAt} disabled={blocked} onChange={(formEvent) => setExternalConfirmationDrafts((current) => ({
                    ...current, [act.act_id]: { ...confirmationDraft, receivedAt: formEvent.target.value },
                  }))} /></label>
                  <label>Émetteur externe déclaré<input maxLength={240} value={confirmationDraft.externalParty} disabled={blocked} onChange={(formEvent) => setExternalConfirmationDrafts((current) => ({
                    ...current, [act.act_id]: { ...confirmationDraft, externalParty: formEvent.target.value },
                  }))} /></label>
                  <label>Justification Patron<textarea required maxLength={2000} value={confirmationDraft.rationale} disabled={blocked} onChange={(formEvent) => setExternalConfirmationDrafts((current) => ({
                    ...current, [act.act_id]: { ...confirmationDraft, rationale: formEvent.target.value },
                  }))} /></label>
                  <button type="submit" disabled={blocked
                    || (!confirmationDraft.evidenceObjectId && !externalConfirmationFiles[act.act_id])
                    || !confirmationDraft.rationale.trim()}>
                    {submitting === "c5-confirmation:" + act.act_id ? "Vérification et enregistrement…" : "Enregistrer l’acte de confirmation externe"}
                  </button>
                </form>}
              </div>;
            })}
            {event.actions.map((item) => {
              const draft = executionDrafts[item.action_id] ?? {
                state: "UNKNOWN" as const, summary: "", unknownReason: "", evidenceRefs: "",
                evidenceObjectIds: [],
                confirmation: "UNKNOWN" as const, confirmationNote: "",
              };
              const currentC4 = event.action_impact_relations
                .filter((relation) => relation.action_id === item.action_id).at(-1);
              const hasC4 = !!currentC4;
              const key = "c5:" + item.action_id;
              return <form key={item.action_id} onSubmit={(formEvent) => {
                formEvent.preventDefault(); recordActionExecution(event, item.action_id);
              }}>
                <p>Action C1 {item.action_id} · état C1 {item.state}. C5 enregistre une déclaration, sans clôturer l’action.</p>
                <label>Réalisation déclarée
                  <select aria-label={"Réalisation déclarée C5 " + item.action_id} value={draft.state} disabled={blocked || !hasC4} onChange={(formEvent) => setExecutionDrafts((current) => ({
                    ...current, [item.action_id]: { ...draft, state: formEvent.target.value as typeof draft.state },
                  }))}>
                    <option value="UNKNOWN">UNKNOWN · état non établi</option>
                    <option value="DECLARED_PERFORMED">Réalisation déclarée</option>
                    <option value="DECLARED_PARTIAL">Réalisation partielle déclarée</option>
                    <option value="DECLARED_NOT_PERFORMED">Non réalisée, déclaration humaine</option>
                  </select>
                </label>
                {draft.state === "UNKNOWN"
                  ? <label>Motif UNKNOWN<input required maxLength={1000} value={draft.unknownReason} disabled={blocked || !hasC4} onChange={(formEvent) => setExecutionDrafts((current) => ({ ...current, [item.action_id]: { ...draft, unknownReason: formEvent.target.value } }))} /></label>
                  : <label>Résumé de la déclaration<textarea required maxLength={2000} value={draft.summary} disabled={blocked || !hasC4} onChange={(formEvent) => setExecutionDrafts((current) => ({ ...current, [item.action_id]: { ...draft, summary: formEvent.target.value } }))} /></label>}
                <label>Références de pièce déclarées (une par ligne, non vérifiées)<textarea value={draft.evidenceRefs} disabled={blocked || !hasC4} onChange={(formEvent) => setExecutionDrafts((current) => ({ ...current, [item.action_id]: { ...draft, evidenceRefs: formEvent.target.value } }))} /></label>
                {currentC4 && event.evidence_objects.filter((source) => source.action_id === item.action_id
                  && source.c4_relation_id === currentC4.relation_id
                  && source.evidence_kind === "EXECUTION_EVIDENCE"
                  && source.state === "CLEAN").map((source) => <label key={source.evidence_object_id}>
                    <input type="checkbox" aria-label={"Sélectionner la pièce C5 " + source.evidence_object_id}
                      checked={draft.evidenceObjectIds.includes(source.evidence_object_id)} disabled={blocked}
                      onChange={(formEvent) => setExecutionDrafts((current) => ({
                        ...current,
                        [item.action_id]: { ...draft, evidenceObjectIds: formEvent.target.checked
                          ? [...draft.evidenceObjectIds, source.evidence_object_id]
                          : draft.evidenceObjectIds.filter((id) => id !== source.evidence_object_id) },
                      }))} />
                    Pièce assainie · {source.media_type} · {source.sha256}
                  </label>)}
                <label>Ou joindre une nouvelle pièce d’exécution
                  <input type="file" accept=".pdf,.doc,.docx,.xls,.xlsx,.ods,.odt,.zip,.jpg,.jpeg,.png,.tif,.tiff"
                    disabled={blocked || !hasC4} onChange={(formEvent) => setExecutionEvidenceFiles((current) => ({
                      ...current, [item.action_id]: formEvent.target.files?.[0] ?? null,
                    }))} />
                </label>
                <label>Confirmation externe
                  <select aria-label={"Confirmation externe C5 " + item.action_id} value={draft.confirmation} disabled={blocked || !hasC4} onChange={(formEvent) => setExecutionDrafts((current) => ({ ...current, [item.action_id]: { ...draft, confirmation: formEvent.target.value as typeof draft.confirmation } }))}>
                    <option value="UNKNOWN">UNKNOWN · aucune source externe vérifiée</option>
                    <option value="NOT_CONFIRMED">Absence de confirmation déclarée</option>
                  </select>
                </label>
                {draft.confirmation === "NOT_CONFIRMED" && <label>Motif de l’absence de confirmation<input required maxLength={1000} value={draft.confirmationNote} disabled={blocked || !hasC4} onChange={(formEvent) => setExecutionDrafts((current) => ({ ...current, [item.action_id]: { ...draft, confirmationNote: formEvent.target.value } }))} /></label>}
                <button type="submit" disabled={blocked || !hasC4 || (draft.state === "UNKNOWN" ? !draft.unknownReason.trim() : !draft.summary.trim()) || (draft.confirmation === "NOT_CONFIRMED" && !draft.confirmationNote.trim())}>
                  {submitting === key ? "Enregistrement…" : failure?.key === key && failure.kind === "UNCONFIRMED" ? "Réessayer la même déclaration" : "Enregistrer l’acte C5"}
                </button>
              </form>;
            })}
            <p>Une référence seule ne prouve pas qu’une pièce a été retrouvée. Un upload devient RETRIEVED uniquement après relecture et recalcul SHA-256 ; la confirmation externe se consigne dans un acte séparé. Aucune action, notification ou transmission n’est déclenchée.</p>
          </section>
          <section aria-label={"Liaisons C4 actions et impacts " + event.event_id}>
            <h4>Lier une action Patron aux impacts déclarés</h4>
            {event.action_impact_relations.map((item) => <p key={item.relation_id}>
              C4 r{item.revision} · action {item.action_id} · {item.state} · impacts C3 : {item.declaration_ids.join(", ") || "aucun"} · projection {item.projection_state} · {item.rationale}
              {item.unknown_reason ? " · motif : " + item.unknown_reason : ""}
            </p>)}
            {event.actions.map((item) => {
              const draft = actionImpactDrafts[item.action_id] ?? {
                state: "LINKED" as const, declarationIds: [], rationale: "", reason: "",
              };
              const latestReviewIsCurrent = latestReview?.decision === "APPLICABLE_TO_HANDOVER"
                && item.applicability_review_id === latestReview.review_id;
              return <form key={item.action_id} onSubmit={(formEvent) => {
                formEvent.preventDefault();
                recordActionImpactRelation(event, item.action_id);
              }}>
                <p>Action {item.action_id} · état {item.state} (la relation C4 ne change pas cet état).</p>
                <label>État de la liaison C4
                  <select aria-label={"État C4 " + item.action_id} value={draft.state} disabled={blocked || !latestReviewIsCurrent} onChange={(formEvent) => setActionImpactDrafts((current) => ({
                    ...current,
                    [item.action_id]: { ...draft, state: formEvent.target.value as typeof draft.state },
                  }))}>
                    <option value="LINKED">Relier à des impacts C3</option>
                    <option value="UNKNOWN">UNKNOWN · lien non établi</option>
                    <option value="NOT_APPLICABLE">Sans objet pour cette action</option>
                  </select>
                </label>
                {draft.state === "LINKED" && event.impact_declarations
                  .filter((declaration) => declaration.linkage_state === "CURRENT")
                  .map((declaration) => <label key={declaration.declaration_id}>
                    <input type="checkbox" aria-label={"Sélectionner l’impact C3 " + declaration.declaration_id}
                      checked={draft.declarationIds.includes(declaration.declaration_id)} disabled={blocked || !latestReviewIsCurrent}
                      onChange={(formEvent) => setActionImpactDrafts((current) => ({
                        ...current,
                        [item.action_id]: { ...draft, declarationIds: formEvent.target.checked
                          ? [...draft.declarationIds, declaration.declaration_id]
                          : draft.declarationIds.filter((id) => id !== declaration.declaration_id) },
                      }))} />
                    C3 {declaration.declaration_id} · {declaration.axis} · {declaration.impact_state}
                  </label>)}
                {draft.state !== "LINKED" && <label>Motif UNKNOWN / sans objet<input required maxLength={1000} value={draft.reason} disabled={blocked || !latestReviewIsCurrent} onChange={(formEvent) => setActionImpactDrafts((current) => ({ ...current, [item.action_id]: { ...draft, reason: formEvent.target.value } }))} /></label>}
                <label>Justification Patron C4<textarea required maxLength={2000} value={draft.rationale} disabled={blocked || !latestReviewIsCurrent} onChange={(formEvent) => setActionImpactDrafts((current) => ({ ...current, [item.action_id]: { ...draft, rationale: formEvent.target.value } }))} /></label>
                <button type="submit" disabled={blocked || !latestReviewIsCurrent
                  || (draft.state === "LINKED" && !draft.declarationIds.some((id) =>
                    event.impact_declarations.some((declaration) => declaration.declaration_id === id && declaration.linkage_state === "CURRENT")))
                  || (draft.state !== "LINKED" && !draft.reason.trim())}>
                  {submitting === "c4:" + item.action_id ? "Enregistrement…" : failure?.key === "c4:" + item.action_id && failure.kind === "UNCONFIRMED" ? "Réessayer la même liaison" : "Enregistrer la liaison Patron C4"}
                </button>
              </form>;
            })}
            {event.actions.length === 0 && <p>Une action C1 `RECORDED` doit exister avant de créer une liaison C4.</p>}
            <p>C4 relie une déclaration à l’action ; il ne prouve ni son exécution ni sa clôture et ne crée aucune action automatiquement.</p>
          </section>
        </article>;
      })}
      {message && <p role="status">{message}</p>}
      {failure && <p role="alert">{failure.kind === "UNCONFIRMED" ? "Résultat non confirmé · le rejeu conserve les mêmes identifiants." : "Refus confirmé par le serveur ; aucune nouvelle révision n’a été créée."}</p>}
      {state === "READY" && <form aria-label="Enregistrer un événement contractuel sourcé" onSubmit={recordEvent}>
        <h3>Enregistrer un événement contractuel</h3>
        <label>Passation P7 de départ
          <select required aria-label="Passation de départ" value={handoverId} disabled={blocked} onChange={(formEvent) => setHandoverId(formEvent.target.value)}>
            <option value="">Choisir la passation gagnée</option>
            {handovers.map((handover) => <option key={handover.snapshot_id} value={handover.snapshot_id}>Lot {handover.lot_reference} · P5 v{handover.package_version} · {handover.manifest_sha256.slice(0, 12)}</option>)}
          </select>
        </label>
        <label>Type d’événement
          <select aria-label="Type d’événement contractuel" value={changeKind} disabled={blocked} onChange={(formEvent) => setChangeKind(formEvent.target.value as CaseContractChangeKind)}>
            {CHANGE_KINDS.map((kind) => <option key={kind.value} value={kind.value}>{kind.label}</option>)}
          </select>
        </label>
        <label>Version contractuelle déclarée (facultatif)
          <select aria-label="Version contractuelle déclarée" value={declaredVersionId} disabled={blocked} onChange={(formEvent) => setDeclaredVersionId(formEvent.target.value)}>
            <option value="">UNKNOWN · version non établie</option>
            {versions.map((version) => <option key={version.contract_instrument_version_id} value={version.contract_instrument_version_id}>{version.instrument_kind} · {version.version_reference}</option>)}
          </select>
        </label>
        <label>Émetteur déclaré<input maxLength={240} value={issuer} disabled={blocked} onChange={(formEvent) => setIssuer(formEvent.target.value)} /></label>
        <label>Résumé déclaré<input required maxLength={2000} value={summary} disabled={blocked} onChange={(formEvent) => setSummary(formEvent.target.value)} /></label>
        <label>Périmètre/delta décrit, sans calcul automatique<textarea required maxLength={2000} value={scopeNote} disabled={blocked} onChange={(formEvent) => setScopeNote(formEvent.target.value)} /></label>
        <label>Références source, une par ligne<textarea required value={sourceRefs} disabled={blocked} onChange={(formEvent) => setSourceRefs(formEvent.target.value)} /></label>
        <label>Preuves de réception/événement, une par ligne<textarea required value={evidenceRefs} disabled={blocked} onChange={(formEvent) => setEvidenceRefs(formEvent.target.value)} /></label>
        <label>Date/heure de réception déclarée<input required type="datetime-local" value={receivedAt} disabled={blocked} onChange={(formEvent) => setReceivedAt(formEvent.target.value)} /></label>
        <button type="submit" disabled={blocked || !handovers.length}>{submitting === "event" ? "Enregistrement…" : failure?.key === "event" && failure.kind === "UNCONFIRMED" ? "Réessayer le même événement" : "Enregistrer l’événement sourcé"}</button>
      </form>}
    </section>
  );
}
