import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import type { CapabilityProposalController, CapabilityProposalDraft, CapabilityProposalSource } from "./useCapabilityProposal";
import type { Candidate } from "./useCapabilityCandidates";

type RequirementOption = { id: string; requirementId: string; label: string; state?: string };

type Props = {
  caseId: string;
  scopeKey: string;
  candidates: Candidate[] | null;
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
  requirements: RequirementOption[];
  dceSourceReady: boolean;
  dceVersionId: string | null;
  proposal: CapabilityProposalController;
};

const kindLabels: Record<Candidate["kind"], string> = {
  QUALIFICATION: "Qualification",
  REFERENCE: "Référence",
  EQUIPMENT: "Équipement",
  TEAM: "Équipe",
  METHOD: "Méthode",
};

const lockedStatuses = new Set(["SUBMITTING", "UNKNOWN", "READING", "RECEIVED", "CONFLICT", "RECEIPT_READ_FAILED", "CONFLICT_READ_FAILED"]);

export function CapabilityCandidatesPanel({ caseId, scopeKey, candidates, loading, error, onRefresh, requirements, dceSourceReady, dceVersionId, proposal }: Props) {
  const [selectedVersionId, setSelectedVersionId] = useState<string | null>(null);
  const [selectedCandidateSnapshot, setSelectedCandidateSnapshot] = useState<Candidate | null>(null);
  const [selectedSourceKey, setSelectedSourceKey] = useState<string | null>(null);
  const [selectedSourceLabel, setSelectedSourceLabel] = useState<string | null>(null);
  const [selectedSourceDceVersionId, setSelectedSourceDceVersionId] = useState<string | null>(null);
  const [justification, setJustification] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [validation, setValidation] = useState<Record<string, string>>({});
  const [formScopeKey, setFormScopeKey] = useState(scopeKey);
  const sameScope = formScopeKey === scopeKey;
  const current = caseId && !loading && !error ? candidates : null;
  const locked = lockedStatuses.has(proposal.status);

  const sources = useMemo(() => {
    const requirementIds = new Set(requirements.map((item) => item.requirementId));
    const requirementSources: CapabilityProposalSource[] = requirements.map((item) => ({
      kind: "REQUIREMENT", id: item.id, requirementId: item.requirementId,
      label: item.label, state: item.state,
    }));
    const taskSources: CapabilityProposalSource[] = proposal.tasks
      .filter((task) => task.requirementId && requirementIds.has(task.requirementId))
      .map((task) => ({ kind: "TASK", id: task.id, requirementId: task.requirementId!, label: task.title }));
    return dceSourceReady ? [...requirementSources, ...taskSources] : [];
  }, [dceSourceReady, proposal.tasks, requirements]);

  const visibleSourceKey = sameScope ? selectedSourceKey : null;
  const selected = sameScope
    ? current?.find((candidate) => candidate.versionId === selectedVersionId)
      ?? (selectedCandidateSnapshot?.versionId === selectedVersionId ? selectedCandidateSnapshot : null)
    : null;
  const source = sources.find((item) => `${item.kind}:${item.id}` === visibleSourceKey) ?? null;
  const visibleSourceLabel = sameScope ? selectedSourceLabel : null;
  const visibleJustification = sameScope ? justification : "";
  const visibleConfirmed = sameScope && confirmed;
  const formReady = sameScope && Boolean(caseId && current && dceSourceReady);
  const formDisabled = locked || !formReady;

  useEffect(() => {
    setFormScopeKey(scopeKey);
    setSelectedVersionId(null);
    setSelectedCandidateSnapshot(null);
    setSelectedSourceKey(null);
    setSelectedSourceLabel(null);
    setSelectedSourceDceVersionId(null);
    setJustification("");
    setConfirmed(false);
    setValidation({});
  }, [caseId, scopeKey]);

  useEffect(() => {
    if (!locked && visibleSourceKey && !sources.some((item) => `${item.kind}:${item.id}` === visibleSourceKey)) {
      setSelectedSourceKey(null);
      setSelectedSourceLabel(null);
      setSelectedSourceDceVersionId(null);
      setConfirmed(false);
      setValidation({});
    }
  }, [locked, visibleSourceKey, sources]);

  function selectVersion(candidate: Candidate) {
    if (locked || !sameScope) return;
    const isSelected = selectedVersionId === candidate.versionId;
    setSelectedVersionId(isSelected ? null : candidate.versionId);
    setSelectedCandidateSnapshot(isSelected ? null : candidate);
    setConfirmed(false);
    setValidation({});
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (formDisabled || !caseId) return;
    const errors: Record<string, string> = {};
    if (!selected) errors.candidate = "Sélectionnez une version exacte.";
    if (!dceSourceReady || !source) errors.source = "Sélectionnez une seule exigence ou tâche du DCE courant.";
    if (!justification.trim() || justification.trim().length > 2000) errors.justification = "Saisissez une justification de 1 à 2 000 caractères.";
    if (!confirmed) errors.confirmation = "Confirmez explicitement cette version, cette source et votre justification.";
    setValidation(errors);
    if (Object.keys(errors).length) {
      if (errors.candidate) document.getElementById("capability-candidate-options")?.focus();
      else if (errors.source) document.getElementById("capability-proposal-source")?.focus();
      else if (errors.justification) document.getElementById("capability-proposal-justification")?.focus();
      else document.getElementById("capability-proposal-confirm")?.focus();
      return;
    }
    if (!selected || !source) return;
    const base = { capability_id: selected.capabilityId, capability_version_id: selected.versionId, justification: justification.trim() };
    const draft: CapabilityProposalDraft = source.kind === "REQUIREMENT"
      ? { ...base, requirement_id: source.requirementId }
      : { ...base, task_id: source.id };
    void proposal.propose(draft);
  }

  function resetProposal() {
    proposal.reset();
    setSelectedVersionId(null);
    setSelectedCandidateSnapshot(null);
    setSelectedSourceKey(null);
    setSelectedSourceLabel(null);
    setSelectedSourceDceVersionId(null);
    setJustification("");
    setConfirmed(false);
    setValidation({});
  }

  const message = {
    IDLE: ["Préparation humaine", "Rien n’est envoyé avant la confirmation explicite."],
    SUBMITTING: ["Envoi de la proposition…", "La version, la source et la justification sont figées pendant l’envoi."],
    UNKNOWN: ["Résultat UNKNOWN", "La réponse ne permet pas de savoir si l’intention a été enregistrée. Réessayez cette même proposition; ses identifiants et son contenu sont conservés."],
    READING: ["Lecture des évaluations…", "Seul le GET des évaluations est en cours. Aucun nouvel envoi."],
    RECEIVED: ["Reçu technique obtenu · lecture actualisée", "La lecture ne vaut pas validation documentaire, disponibilité, réservation ou engagement."],
    CONFLICT: ["HTTP 409 · lecture actualisée, revue humaine requise", "Aucun nouvel envoi automatique. Examinez les évaluations avant de préparer une nouvelle proposition."],
    REJECTED: ["Proposition refusée", proposal.error ?? "Relisez le périmètre et la source DCE."],
    RECEIPT_READ_FAILED: ["Reçu obtenu · lecture UNKNOWN", proposal.error ?? "Réessayez uniquement le GET des évaluations."],
    CONFLICT_READ_FAILED: ["HTTP 409 · lecture UNKNOWN", proposal.error ?? "Réessayez uniquement le GET des évaluations."],
  }[proposal.status];

  return (
    <section className="case-resolution capability-candidates" aria-labelledby="capability-candidates-title" aria-busy={loading}>
      <div className="case-resolution-heading">
        <div>
          <h2 id="capability-candidates-title">Moyens que vous pouvez proposer</h2>
          <p>Choisissez une version pour la consulter dans cette affaire. Cette sélection reste locale et ne crée aucun acte.</p>
        </div>
        <button className="secondary-button" type="button" disabled={!caseId || loading || locked} onClick={onRefresh}>
          {loading ? "Chargement…" : "Actualiser les moyens"}
        </button>
      </div>
      {!caseId ? <p className="case-resolution-message">Sélectionnez une affaire pour consulter les moyens proposés.</p>
        : loading ? <p className="case-resolution-message" role="status">Chargement des moyens proposés…</p>
        : error ? <p className="case-resolution-message" role="alert">{error}</p>
        : !current ? <p className="case-resolution-message">La liste des moyens n’est pas disponible.</p>
        : current.length === 0 ? <p className="case-resolution-message">Aucun moyen enregistré n’est retourné dans ce périmètre. Cette absence ne confirme pas qu’aucun moyen n’existe.</p>
        : <ul className="capability-candidate-list" id="capability-candidate-options" aria-label="Capacités et versions proposées" tabIndex={-1}>
          {current.map((candidate) => {
            const selectedCandidate = sameScope && candidate.versionId === selectedVersionId;
            return <li key={candidate.versionId}>
              <button
                className="capability-candidate-option"
                type="button"
                disabled={locked || !sameScope}
                aria-pressed={selectedCandidate}
                aria-label={`${selectedCandidate ? "Retirer" : "Sélectionner"} ${candidate.name}, version ${candidate.versionNumber}`}
                onClick={() => selectVersion(candidate)}
              >
                <span className="capability-candidate-kind">{kindLabels[candidate.kind]}</span>
                <span className="capability-candidate-title"><strong>{candidate.name}</strong><span>{candidate.title} · Version {candidate.versionNumber}</span></span>
                <span className="capability-candidate-validity">
                  Validité déclarée : {candidate.validityState}<br />
                  {candidate.validityState === "UNKNOWN" ? "Dates de validité inconnues" : `Période : ${candidate.validFrom} — ${candidate.validUntil ?? "sans date de fin"}`}
                </span>
                <span className="capability-candidate-evidence">État documentaire : {candidate.sourceEvidenceState}</span>
                <span className="capability-candidate-date">Évalué le {candidate.evaluatedAt ?? "Date inconnue"}</span>
              </button>
            </li>;
          })}
        </ul>}

      <section className="capability-proposal" aria-labelledby="capability-proposal-title" aria-busy={proposal.status === "SUBMITTING" || proposal.status === "READING"}>
        <h3 id="capability-proposal-title">Préparer une proposition humaine</h3>
        <p>Une version précise, une seule exigence ou tâche du DCE courant et une justification humaine. La preuve documentaire inconnue reste UNKNOWN.</p>
        <div className="capability-proposal-selection" aria-live="polite">
          {selected ? <><strong>{selected.name} · version {selected.versionNumber}</strong><span>{selected.title} · preuve documentaire {selected.sourceEvidenceState}</span></>
            : <span>Sélectionnez la version exacte dans la liste.</span>}
          {validation.candidate && <p className="capability-proposal-error">{validation.candidate}</p>}
        </div>
        <form noValidate onSubmit={submit}>
          <fieldset className="capability-proposal-sources" disabled={formDisabled}>
            <legend>Source DCE applicable · choisissez une seule entrée</legend>
            {!dceSourceReady ? <p className="case-resolution-message">La source du DCE courant n’est pas disponible ou qualifiée pour cette affaire.</p>
              : sources.length === 0 ? <p className="case-resolution-message">Aucune exigence ou tâche applicable n’est disponible dans le DCE courant.</p>
              : <div id="capability-proposal-source" tabIndex={-1}>
                {sources.map((item, index) => {
                  const sourceKey = `${item.kind}:${item.id}`;
                  return <label className="capability-proposal-source" key={sourceKey}>
                    <input
                      type="radio"
                      name={`capability-proposal-source-${caseId}`}
                      value={index}
                      checked={visibleSourceKey === sourceKey}
                      aria-describedby={validation.source ? "capability-source-error" : undefined}
                      onChange={() => { setSelectedSourceKey(sourceKey); setSelectedSourceLabel(item.label); setSelectedSourceDceVersionId(dceVersionId); setConfirmed(false); setValidation({}); }}
                    />
                    <span><strong>{item.kind === "REQUIREMENT" ? "Exigence DCE" : "Tâche DCE"}</strong> · {item.label}{item.state && item.state !== "CONFIRMED" ? ` · état ${item.state}` : ""}</span>
                  </label>;
                })}
              </div>}
          </fieldset>
          {visibleSourceLabel && <p className="capability-proposal-help">Source choisie : {visibleSourceLabel}{selectedSourceDceVersionId && dceVersionId && selectedSourceDceVersionId !== dceVersionId ? " · Le DCE courant a changé; l’intention UNKNOWN reste figée pour son rejeu exact." : ""}</p>}
          {validation.source && <p id="capability-source-error" className="capability-proposal-error" role="alert">{validation.source}</p>}
          {proposal.taskLoading && <p className="case-resolution-message" role="status">Lecture des tâches de cette affaire…</p>}
          {proposal.taskError && <p className="case-resolution-message" role="status">{proposal.taskError} Les exigences DCE disponibles restent sélectionnables.</p>}
          <label className="capability-proposal-field" htmlFor="capability-proposal-justification">
            Justification humaine
            <textarea
              id="capability-proposal-justification"
              rows={4}
              maxLength={2000}
              required
              value={visibleJustification}
              disabled={formDisabled}
              aria-invalid={Boolean(validation.justification)}
              aria-describedby="capability-justification-help capability-justification-error"
              onChange={(event) => { setJustification(event.target.value); setConfirmed(false); setValidation({}); }}
            />
            <span id="capability-justification-help" className="capability-proposal-help">Expliquez le lien entre la version et la source sélectionnées (2 000 caractères maximum).</span>
          </label>
          {validation.justification && <p id="capability-justification-error" className="capability-proposal-error" role="alert">{validation.justification}</p>}
          <label className="capability-proposal-confirm">
            <input
              id="capability-proposal-confirm"
              type="checkbox"
              checked={visibleConfirmed}
              disabled={formDisabled}
              aria-invalid={Boolean(validation.confirmation)}
              aria-describedby="capability-confirm-error"
              onChange={(event) => { setConfirmed(event.target.checked); setValidation({}); }}
            />
            <span>Je confirme explicitement cette version, cette source et ma justification.</span>
          </label>
          {validation.confirmation && <p id="capability-confirm-error" className="capability-proposal-error" role="alert">{validation.confirmation}</p>}
          <div className="capability-proposal-actions">
            <button className="secondary-button capability-proposal-submit" type="submit" disabled={!caseId || formDisabled || !selected}>
              Préparer la proposition
            </button>
            {proposal.status === "UNKNOWN" && <button className="secondary-button" type="button" onClick={() => void proposal.retry()}>Réessayer la même proposition</button>}
            {(proposal.status === "RECEIPT_READ_FAILED" || proposal.status === "CONFLICT_READ_FAILED") && <button className="secondary-button" type="button" onClick={() => void proposal.retryRead()}>Réessayer uniquement la lecture</button>}
            {(proposal.status === "RECEIVED" || proposal.status === "CONFLICT" || proposal.status === "REJECTED") && <button className="secondary-button" type="button" onClick={resetProposal}>Préparer une autre proposition</button>}
          </div>
          {proposal.status !== "IDLE" && <div className={`capability-proposal-status${proposal.status === "REJECTED" ? " error" : ""}`} role={proposal.status === "UNKNOWN" || proposal.status === "REJECTED" ? "alert" : "status"} aria-live="polite">
            <strong>{message[0]}</strong><p>{message[1]}</p>{proposal.error && <p>{proposal.error}</p>}
          </div>}
        </form>
      </section>
      <p className="case-resolution-message">Un état documentaire UNKNOWN demeure inconnu. Aucun état ne confirme la disponibilité, l’adéquation, une réservation, un engagement ou une confirmation externe. NO-GO public maintenu.</p>
    </section>
  );
}
