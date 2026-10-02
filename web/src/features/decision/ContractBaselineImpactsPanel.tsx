import { useState } from "react";
import type {
  CaseDceReading,
  ContractBaselineImpact,
  ContractProofReview,
  RecordContractBaselineImpactInput,
} from "../../shared/types";

type Requirement = CaseDceReading["requirements"][number];
type PendingRecord = RecordContractBaselineImpactInput;

export function ContractBaselineImpactsPanel({
  caseId,
  items,
  reviews,
  requirements,
  loading,
  canManage,
  onRefresh,
  onRecord,
}: {
  caseId: string;
  items: ContractBaselineImpact[];
  reviews: ContractProofReview[];
  requirements: Requirement[];
  loading: boolean;
  canManage: boolean;
  onRefresh: () => void;
  onRecord: (input: RecordContractBaselineImpactInput) => Promise<boolean>;
}) {
  const confirmed = requirements.filter(
    (item) => item.confirmation_outcome === "CONFIRMED" && item.confirmation_revision !== null,
  );
  const [requirementId, setRequirementId] = useState("");
  const selectedRequirementId = confirmed.some((item) => item.requirement_id === requirementId)
    ? requirementId
    : confirmed[0]?.requirement_id ?? "";
  const [locator, setLocator] = useState("");
  const [baseline, setBaseline] = useState("");
  const [deviation, setDeviation] = useState("");
  const [impact, setImpact] = useState("");
  const [pending, setPending] = useState<PendingRecord | null>(null);
  const [saving, setSaving] = useState(false);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const requirement = confirmed.find((item) => item.requirement_id === selectedRequirementId);
    if (!requirement || requirement.confirmation_revision === null || !locator.trim() || !baseline.trim() || !impact.trim()) return;
    const request = pending ?? {
      command_id: crypto.randomUUID(),
      idempotency_key: crypto.randomUUID(),
      correlation_id: crypto.randomUUID(),
      proof_id: crypto.randomUUID(),
      dce_requirement_id: requirement.requirement_id,
      dce_requirement_revision: requirement.confirmation_revision,
      baseline_source_refs: [locator.trim(), `DCE_REQUIREMENT:${requirement.requirement_id}@${requirement.confirmation_revision}`],
      baseline_statement: baseline.trim(),
      deviation_statement: deviation.trim() || undefined,
      impact_statement: impact.trim(),
    };
    setPending(request);
    setSaving(true);
    try {
      if (await onRecord(request)) {
        setPending(null);
        setLocator("");
        setBaseline("");
        setDeviation("");
        setImpact("");
      }
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="section-block decision-section" id="contract-baseline-impacts-section">
      <div className="section-heading">
        <div><span className="section-kicker">PREUVE CONTRACTUELLE</span><h2>Baseline → dérogation → impact</h2></div>
        <button className="secondary-button" type="button" onClick={onRefresh} disabled={!caseId || loading}>{loading ? "Chargement…" : "Actualiser"}</button>
      </div>
      {canManage && (
        <form className="detail-panel decision-form" onSubmit={(event) => void submit(event)} aria-label="Déclarer un impact contractuel">
          <h3>Déclarer un impact à examiner</h3>
          {confirmed.length === 0 ? <p className="panel-empty">Aucune exigence DCE confirmée et versionnée. La déclaration reste indisponible tant que la source n’est pas confirmée.</p> : <>
            <label>Exigence DCE confirmée
              <select value={selectedRequirementId} onChange={(event) => { setRequirementId(event.target.value); setPending(null); }} required>
                {confirmed.map((item) => <option key={item.requirement_id} value={item.requirement_id}>{item.requirement_type} · {item.source_locator_label} · v{item.confirmation_revision}</option>)}
              </select>
            </label>
            <label>Localisateur exact de la source baseline<input value={locator} onChange={(event) => { setLocator(event.target.value); setPending(null); }} maxLength={500} required placeholder="Document · article · page ou repère" /></label>
            <label>Baseline déclarée<textarea value={baseline} onChange={(event) => { setBaseline(event.target.value); setPending(null); }} maxLength={4000} required /></label>
            <label>Dérogation observée, si établie<textarea value={deviation} onChange={(event) => { setDeviation(event.target.value); setPending(null); }} maxLength={4000} /></label>
            <label>Impact déclaré, sans calcul automatique<textarea value={impact} onChange={(event) => { setImpact(event.target.value); setPending(null); }} maxLength={4000} required /></label>
            <button className="primary-button" type="submit" disabled={saving || !caseId}>{saving ? "Enregistrement…" : "Enregistrer pour revue humaine"}</button>
          </>}
          <p className="panel-empty">État initial : HUMAN_REVIEW_REQUIRED. Aucun coût couvert, GO/P3 ni conclusion juridique n’est calculé.</p>
        </form>
      )}
      {!caseId ? <div className="empty-card"><strong>Aucune affaire sélectionnée</strong><p>Sélectionnez une affaire pour consulter la preuve.</p></div> : items.length === 0 && !loading ? <div className="empty-card"><strong>Aucune preuve enregistrée</strong><p>Les signaux contractuels restent à qualifier.</p></div> : <div className="decision-grid">{items.map((item) => <article className="detail-panel" key={item.proof_id}><div className="panel-heading"><div><h3>Preuve v{item.proof_revision}</h3><p>{item.baseline_source_refs.join(" · ")}</p></div><span className={`state-badge state-${item.status.toLowerCase()}`}>{item.status}</span></div><dl className="decision-facts"><div><dt>Baseline</dt><dd>{item.baseline_statement}</dd></div><div><dt>Dérogation</dt><dd>{item.deviation_statement ?? "Non renseignée"}</dd></div><div><dt>Impact</dt><dd>{item.impact_statement ?? "Non renseigné"}</dd></div></dl><p className="panel-empty">Lecture seule : aucune conclusion juridique n’est déduite.</p></article>)}</div>}
      {reviews.length > 0 && <div className="decision-grid">{reviews.map((review) => <article className="detail-panel" key={review.review_id}><div className="panel-heading"><h3>Revue v{review.reviewed_revision}</h3><span className="state-badge">{review.decision}</span></div><p>{review.rationale}</p><p className="panel-empty">Acte humain conservé en lecture seule.</p></article>)}</div>}
    </section>
  );
}
