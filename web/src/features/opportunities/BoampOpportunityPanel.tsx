import type {
  BoampObservation,
  BoampSourceStatus,
  BoampQualificationDecision,
  BoampQualificationForm,
  BoampQualificationReason,
} from "../../shared/types";

type Props = {
  observations: BoampObservation[];
  selectedObservationId: string;
  qualificationForm: BoampQualificationForm;
  loading: boolean;
  qualifying: boolean;
  qualifiedObservationIds: ReadonlySet<string>;
  creatingCase: boolean;
  onRefresh: () => void;
  onSelect: (observationId: string) => void;
  onDecisionChange: (decision: BoampQualificationDecision) => void;
  onReasonChange: (reason: BoampQualificationReason) => void;
  onQualify: () => void;
  onCreateCase: () => void;
  sourceStatus?: BoampSourceStatus | null;
  onManualEntry?: () => void;
};

const decisions: Array<{ value: BoampQualificationDecision; label: string }> = [
  { value: "QUALIFIED", label: "Cibler (P0)" },
  { value: "REJECTED", label: "Écarter" },
  { value: "SNOOZED", label: "Mettre en attente" },
];

const reasons: Array<{ value: BoampQualificationReason; label: string }> = [
  { value: "RELEVANT_PUBLIC_SIGNAL", label: "Signal public pertinent" },
  { value: "NOT_RELEVANT", label: "Hors périmètre" },
  { value: "INSUFFICIENT_PUBLIC_DATA", label: "Données publiques insuffisantes" },
  { value: "EXPIRED", label: "Échéance dépassée" },
];

function formatDate(value: string | null) {
  if (!value) return "Non précisée";
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime())
    ? "Date invalide"
    : new Intl.DateTimeFormat("fr-FR", { dateStyle: "medium" }).format(parsed);
}

function p0Label(state: BoampObservation["p0_state"]) {
  return {
    UNREVIEWED: "Non revu",
    TARGETED: "Ciblée",
    SNOOZED: "En attente",
    DISCARDED: "Écartée",
  }[state];
}

function p1Label(state: BoampObservation["p1_state"]) {
  return state === "OPEN_WITH_UNKNOWNS" ? "Ouverte avec inconnues" : "Non ouverte";
}

function deadlineLabel(state: BoampObservation["deadline_state"]) {
  return {
    KNOWN: "Connue",
    MISSING: "Absente",
    EXPIRED: "Dépassée",
    CONFLICTING: "Contradictoire",
  }[state];
}

function lotLabel(item: BoampObservation) {
  if (item.lot_scope_state === "IDENTIFIED") {
    return item.lot_references.join(", ") || "Référence manquante";
  }
  if (item.lot_scope_state === "CONFLICTING") return "À vérifier : sources contradictoires";
  if (item.lot_scope_state === "NOT_APPLICABLE") return "Non applicable";
  return "À confirmer";
}

function selectedItem(observations: BoampObservation[], selectedId: string) {
  return observations.find((item) => item.observation_id === selectedId) ?? null;
}

function sourceStateLabel(state: BoampSourceStatus["state"]) {
  return {
    AVAILABLE: "Source joignable",
    UNAVAILABLE: "Source indisponible",
    UNKNOWN: "État de source inconnu",
  }[state];
}

type ScoreFactor = {
  code: string;
  points: number;
  matched: boolean;
  explanation: string;
};

function scoreFactors(explanation: BoampObservation["score_explanation"]): ScoreFactor[] {
  const factors = explanation.factors;
  if (!Array.isArray(factors)) return [];
  return factors.filter((factor): factor is ScoreFactor => {
    if (typeof factor !== "object" || factor === null) return false;
    const value = factor as Record<string, unknown>;
    return (
      typeof value.code === "string" &&
      typeof value.points === "number" &&
      typeof value.matched === "boolean" &&
      typeof value.explanation === "string"
    );
  });
}

export function BoampOpportunityPanel({
  observations,
  selectedObservationId,
  qualificationForm,
  loading,
  qualifying,
  qualifiedObservationIds,
  creatingCase,
  onRefresh,
  onSelect,
  onDecisionChange,
  onReasonChange,
  onQualify,
  onCreateCase,
  sourceStatus = null,
  onManualEntry,
}: Props) {
  const selected = selectedItem(observations, selectedObservationId);
  const selectedScoreFactors = selected ? scoreFactors(selected.score_explanation) : [];

  return (
    <section className="section-block boamp-section" id="boamp-section">
      <div className="section-heading">
        <div>
          <span className="section-kicker">VEILLE PUBLIQUE</span>
          <h2>Opportunités BOAMP</h2>
        </div>
        <div className="section-actions">
          <span className="count-pill">{observations.length} visible{observations.length > 1 ? "s" : ""}</span>
          <button className="secondary-button compact-button" type="button" onClick={onRefresh} disabled={loading}>
            {loading ? "Chargement…" : "Actualiser"}
          </button>
        </div>
      </div>
      <p className="section-note">Lecture patronale de signaux publics. Aucune donnée financière ni conversion automatique en affaire.</p>
      {sourceStatus && (
        <div className="empty-card boamp-source-status" aria-live="polite">
          <span className="section-kicker">ÉTAT DE LA SOURCE</span>
          <strong>{sourceStateLabel(sourceStatus.state)}</strong>
          {sourceStatus.state === "UNAVAILABLE" ? (
            <p>
              Aucune nouvelle collecte n’est confirmée. Dernier succès : {sourceStatus.last_success_at ? formatDate(sourceStatus.last_success_at) : "jamais"}.
            </p>
          ) : sourceStatus.state === "UNKNOWN" ? (
            <p>La disponibilité BOAMP n’est pas confirmée ; aucune mention « à jour » n’est affichée.</p>
          ) : (
            <p>Contrôle effectué le {formatDate(sourceStatus.checked_at)}. La date de collecte de chaque avis reste affichée séparément.</p>
          )}
          <div className="section-actions">
            {sourceStatus.retryable && (
              <button className="secondary-button compact-button" type="button" onClick={onRefresh} disabled={loading}>
                {loading ? "Relance…" : "Relancer"}
              </button>
            )}
            {sourceStatus.manual_entry_available && onManualEntry && (
              <button className="secondary-button compact-button" type="button" onClick={onManualEntry}>
                Saisie manuelle
              </button>
            )}
          </div>
        </div>
      )}
      {observations.length === 0 ? (
        <div className="empty-card">
          <strong>Aucune opportunité BOAMP disponible</strong>
          <p>Les observations ingérées et autorisées apparaîtront ici, dans le périmètre du tenant courant.</p>
        </div>
      ) : (
        <div className="boamp-layout">
          <div className="boamp-list" aria-label="Opportunités BOAMP">
            {observations.map((item) => (
              <button
                className={`boamp-item ${item.observation_id === selectedObservationId ? "selected" : ""}`}
                key={item.observation_id}
                type="button"
                onClick={() => onSelect(item.observation_id)}
              >
                <span className="boamp-item-top">
                  <span className="state-badge state-monitor">P0 {p0Label(item.p0_state)}</span>
                  <span className="boamp-deadline">{formatDate(item.response_deadline)}</span>
                </span>
                <strong>{item.title ?? "Titre non communiqué"}</strong>
                <span>{item.department_codes.join(", ") || "Département non précisé"}</span>
              </button>
            ))}
          </div>
          <div className="boamp-detail">
            {selected ? (
              <>
                <div className="boamp-detail-heading">
                  <div>
                    <span className="section-kicker">OBSERVATION PUBLIQUE</span>
                    <h3>{selected.title ?? "Titre non communiqué"}</h3>
                    <div className="boamp-state-row" aria-label="Portes métier">
                      <span className="state-badge state-monitor">P0 {p0Label(selected.p0_state)}</span>
                      <span className="state-badge state-monitor">P1 {p1Label(selected.p1_state)}</span>
                    </div>
                  </div>
                  <div className="boamp-score-block">
                    <span className="score-emphasis">{selected.score}<small>/100</small></span>
                    <span className="boamp-score-note">Pertinence publique · tri uniquement · {selected.score_version}</span>
                  </div>
                </div>
                {selectedScoreFactors.length > 0 && (
                  <details className="boamp-score-details">
                    <summary>Pourquoi ce classement ?</summary>
                    <ul>
                      {selectedScoreFactors.map((factor) => (
                        <li key={factor.code}>
                          <span>{factor.explanation}</span>
                          <strong>{factor.matched ? `+${factor.points}` : "0"} pts</strong>
                        </li>
                      ))}
                    </ul>
                  </details>
                )}
                <dl className="boamp-facts">
                  <div><dt>Avis source</dt><dd>{selected.source_notice_id}</dd></div>
                  <div><dt>Collectée</dt><dd>{formatDate(selected.observed_at)}</dd></div>
                  <div><dt>Publication</dt><dd>{formatDate(selected.publication_date)}</dd></div>
                  <div><dt>Réponse avant</dt><dd>{formatDate(selected.response_deadline)}</dd></div>
                  <div><dt>État échéance</dt><dd>{deadlineLabel(selected.deadline_state)}</dd></div>
                  <div><dt>Départements</dt><dd>{selected.department_codes.join(", ") || "Non précisés"}</dd></div>
                  <div><dt>Types de marché</dt><dd>{selected.market_types.join(", ") || "Non précisés"}</dd></div>
                  <div><dt>Périmètre de lots</dt><dd>{lotLabel(selected)}</dd></div>
                  <div><dt>Statut public</dt><dd>{selected.source_status ?? "Non précisé"}</dd></div>
                  <div><dt>Décision P0</dt><dd>{selected.p0_decision ?? "Aucune décision"}</dd></div>
                  <div><dt>Motif P0</dt><dd>{selected.p0_reason_code ?? "Non applicable"}</dd></div>
                </dl>
                {selected.unknowns.length > 0 && (
                  <div className="boamp-unknowns" aria-label="Inconnues de l’opportunité">
                    <span className="section-kicker">INCONNUES À LEVER</span>
                    <ul>
                      {selected.unknowns.map((unknown) => (
                        <li key={unknown.code}>
                          <strong>{unknown.missing}</strong>
                          <span>{unknown.next_action}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                <div className="boamp-qualification">
                  <div><span className="section-kicker">DÉCISION HUMAINE P0</span><h3>Décider du suivi</h3></div>
                  <label><span>Décision</span><select value={qualificationForm.decision} onChange={(event) => onDecisionChange(event.target.value as BoampQualificationDecision)}>{decisions.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}</select></label>
                  <label><span>Motif</span><select value={qualificationForm.reason_code} onChange={(event) => onReasonChange(event.target.value as BoampQualificationReason)}>{reasons.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}</select></label>
                  <button className="primary-button" type="button" onClick={onQualify} disabled={qualifying}>{qualifying ? "Enregistrement…" : "Enregistrer la décision P0"}<span>→</span></button>
                  {qualifiedObservationIds.has(selected.observation_id) && selected.p0_state === "TARGETED" && selected.p1_state === "NOT_OPEN" && (
                    <button className="secondary-button" type="button" onClick={onCreateCase} disabled={creatingCase}>
                      {creatingCase ? "Création…" : "Créer une affaire"}<span>→</span>
                    </button>
                  )}
                </div>
              </>
            ) : (
              <div className="empty-card"><strong>Sélectionnez une observation</strong><p>La projection détaillée et la qualification humaine resteront limitées au tenant courant.</p></div>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
