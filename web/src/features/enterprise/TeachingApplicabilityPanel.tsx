import { useRef, useState, type FormEvent } from "react";

import type {
  CaseTeachingApplicability,
  CaseTeachingApplicabilityDecision,
  CaseTeachingSource,
  RecordCaseTeachingApplicabilityInput,
} from "../../shared/types";
import type { TeachingApplicabilityReadStatus } from "./useCaseTeachingApplicability";

type Failure = "UNCONFIRMED" | "REJECTED";

type Props = {
  targetCaseId: string;
  targetCaseLabel: string;
  readStatus: TeachingApplicabilityReadStatus;
  sources: CaseTeachingSource[] | null;
  applicabilities: CaseTeachingApplicability[] | null;
  onRecord: (input: RecordCaseTeachingApplicabilityInput) => Promise<void>;
  onRefresh: () => void | Promise<void>;
};

export function TeachingApplicabilityPanel({
  targetCaseId,
  targetCaseLabel,
  readStatus,
  sources,
  applicabilities,
  onRecord,
  onRefresh,
}: Props) {
  return (
    <section className="section-block" aria-label="Applicabilité des enseignements C13">
      <div className="section-heading">
        <div>
          <span className="section-kicker">C13 · APPLICABILITÉ</span>
          <h3>Enseignements examinés pour l’Affaire</h3>
        </div>
        <span className="count-pill">{applicabilities?.length ?? "—"} revue(s)</span>
      </div>
      <p>Affaire cible : {targetCaseLabel || "UNKNOWN · aucune Affaire sélectionnée"}.</p>
      <p>Validité de la source et applicabilité à cette Affaire sont deux états distincts.</p>
      <p>Une déclaration Patron ne transfère aucun contenu, ne prolonge pas la validité et ne constitue pas une conclusion juridique.</p>
      {readStatus === "LOADING" && <p role="status">Chargement des sources et revues d’applicabilité…</p>}
      {readStatus === "UNAVAILABLE" && <p role="status">UNAVAILABLE · sources ou revues d’applicabilité non disponibles.</p>}
      {readStatus === "READY" && sources?.length === 0 && <p>UNKNOWN · aucun enseignement source disponible.</p>}
      {readStatus === "READY" && sources?.map((source) => (
        <TeachingSourceReview
          key={`${source.source_interview_id}:${source.source_rex_id}`}
          source={source}
          targetCaseId={targetCaseId}
          onRecord={onRecord}
          onRefresh={onRefresh}
        />
      ))}
      {readStatus === "READY" && applicabilities?.length === 0 && <p>Aucun acte humain d’applicabilité n’est enregistré pour cette Affaire.</p>}
      {readStatus === "READY" && applicabilities?.map((act) => (
        <article key={act.applicability_id} className="detail-panel">
          <h4>{act.source_case_label} · enseignement {act.source_rex_id}</h4>
          <p>{act.decision} · validité lors de la déclaration : {act.source_validity_at_recording} · validité actuelle : {act.source_validity_current}</p>
          <p>Motif : {act.rationale}</p>
          <p>Source cible déclarée : {act.target_source_locator}</p>
          <TeachingSnapshotDetails snapshot={act.source_snapshot} />
        </article>
      ))}
    </section>
  );
}

function TeachingSourceReview({
  source,
  targetCaseId,
  onRecord,
  onRefresh,
}: {
  source: CaseTeachingSource;
  targetCaseId: string;
  onRecord: Props["onRecord"];
  onRefresh: Props["onRefresh"];
}) {
  const [decision, setDecision] = useState<CaseTeachingApplicabilityDecision>("REVIEW_REQUIRED");
  const [rationale, setRationale] = useState("");
  const [targetSource, setTargetSource] = useState("");
  const [pending, setPending] = useState<RecordCaseTeachingApplicabilityInput | null>(null);
  const pendingRef = useRef<RecordCaseTeachingApplicabilityInput | null>(null);
  const submittingRef = useRef(false);
  const [submitting, setSubmitting] = useState(false);
  const [failure, setFailure] = useState<Failure | null>(null);
  const targetChangedDuringRetry = pending !== null && pending.target_case_id !== targetCaseId;
  const formId = `teaching-${source.source_interview_id}-${source.source_rex_id}`;

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!source.can_assess || !targetCaseId || submittingRef.current || targetChangedDuringRetry) return;
    const input = pendingRef.current ?? {
      command_id: crypto.randomUUID(),
      idempotency_key: crypto.randomUUID(),
      correlation_id: crypto.randomUUID(),
      applicability_id: crypto.randomUUID(),
      target_case_id: targetCaseId,
      source_case_id: source.source_case_id,
      source_interview_id: source.source_interview_id,
      source_rex_id: source.source_rex_id,
      decision,
      rationale: rationale.trim(),
      target_source_locator: targetSource.trim(),
    };
    if (!pendingRef.current) {
      pendingRef.current = input;
      setPending(input);
    }
    submittingRef.current = true;
    setSubmitting(true);
    setFailure(null);
    try {
      await onRecord(input);
      await onRefresh();
      pendingRef.current = null;
      setPending(null);
      setRationale("");
      setTargetSource("");
      setDecision("REVIEW_REQUIRED");
    } catch (error) {
      const statusCode = (error as { status?: number })?.status;
      if (statusCode === 409) {
        setFailure("UNCONFIRMED");
      } else if (statusCode !== undefined && statusCode >= 400 && statusCode < 500) {
        pendingRef.current = null;
        setPending(null);
        setFailure("REJECTED");
      } else {
        setFailure("UNCONFIRMED");
      }
    } finally {
      submittingRef.current = false;
      setSubmitting(false);
    }
  }

  return (
    <article className="detail-panel">
      <h4>{source.source_case_label} · entretien du {source.held_on}</h4>
      <p>Source d’entretien : {source.source_locator}</p>
      <p>Validité : {source.source_validity} · portée : {String(source.snapshot.scope)} · revue source : {String(source.snapshot.validation)}</p>
      <TeachingSnapshotDetails snapshot={source.snapshot} />
      {source.source_validity === "EXPIRED" && <p role="status">EXPIRED · cette revue ne renouvelle pas la validité de la source.</p>}
      {!source.can_assess && <p role="status">{source.block_reason ?? "SOURCE_NOT_AVAILABLE_FOR_APPLICABILITY"} · aucune déclaration d’applicabilité positive n’est ouverte.</p>}
      {source.can_assess && (
        <form aria-label={`Revoir ${source.source_rex_id} pour ${targetCaseId}`} onSubmit={(event) => void submit(event)}>
          <label htmlFor={`${formId}-decision`}>Décision humaine d’applicabilité</label>
          <select
            id={`${formId}-decision`}
            value={decision}
            disabled={submitting || pending !== null}
            onChange={(event) => setDecision(event.target.value as CaseTeachingApplicabilityDecision)}
          >
            <option value="REVIEW_REQUIRED">À examiner</option>
            <option value="APPLICABLE">Applicable à cette Affaire</option>
            <option value="NOT_APPLICABLE">Non applicable à cette Affaire</option>
          </select>
          <label htmlFor={`${formId}-rationale`}>Motif de la revue</label>
          <textarea
            id={`${formId}-rationale`}
            required
            maxLength={2000}
            value={rationale}
            disabled={submitting || pending !== null}
            onChange={(event) => setRationale(event.target.value)}
          />
          <label htmlFor={`${formId}-source`}>Source consultée sur l’Affaire cible</label>
          <input
            id={`${formId}-source`}
            required
            maxLength={500}
            value={targetSource}
            disabled={submitting || pending !== null}
            onChange={(event) => setTargetSource(event.target.value)}
          />
          <button type="submit" disabled={submitting || targetChangedDuringRetry}>
            {submitting ? "Enregistrement…" : failure === "UNCONFIRMED" ? "Réessayer la revue" : "Enregistrer la revue"}
          </button>
          {targetChangedDuringRetry && <p role="alert">Résultat non confirmé pour l’Affaire {pending?.target_case_id} · revenez à cette Affaire pour rejouer les mêmes identifiants.</p>}
          {failure === "UNCONFIRMED" && !targetChangedDuringRetry && <p role="alert">Résultat non confirmé · le rejeu conserve les mêmes identifiants.</p>}
          {failure === "REJECTED" && <p role="alert">Refus confirmé · aucun acte n’a été enregistré.</p>}
        </form>
      )}
    </article>
  );
}

function TeachingSnapshotDetails({ snapshot }: { snapshot: CaseTeachingSource["snapshot"] }) {
  return (
    <div>
      <p>Lot source : {snapshot.lot_reference} · motif : {snapshot.motif} · validation source : {snapshot.validation}</p>
      <p>Observation : {snapshot.observation ?? "UNKNOWN · détail absent du snapshot source"}</p>
      <p>Conséquence : {snapshot.consequence ?? "UNKNOWN · détail absent du snapshot source"}</p>
      <p>Suivi : {snapshot.follow_up ?? "UNKNOWN · détail absent du snapshot source"}</p>
      <p>Preuve source : {snapshot.source_locator ?? "UNKNOWN · aucune référence dans le snapshot"}</p>
    </div>
  );
}
