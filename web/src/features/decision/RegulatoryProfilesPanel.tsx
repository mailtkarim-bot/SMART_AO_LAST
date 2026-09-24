import type { RegulatoryProfileProjection } from "../../shared/types";

type RegulatoryProfilesPanelProps = {
  caseId: string;
  profiles: RegulatoryProfileProjection[];
  loading: boolean;
  onRefresh: () => void;
};

const statusLabels: Record<RegulatoryProfileProjection["status"], string> = {
  ACTIVE: "Actif",
  FUTURE: "Futur",
  EXPIRED: "Expiré",
  UNKNOWN_APPLICABILITY: "Applicabilité inconnue",
  REVIEW_REQUIRED: "Revue requise",
};

export function RegulatoryProfilesPanel({
  caseId,
  profiles,
  loading,
  onRefresh,
}: RegulatoryProfilesPanelProps) {
  return (
    <section className="section-block decision-section" id="regulatory-profiles-section">
      <div className="section-heading">
        <div>
          <span className="section-kicker">PROFIL RÉGLEMENTAIRE</span>
          <h2>Applicabilité à vérifier</h2>
        </div>
        <button className="secondary-button" type="button" onClick={onRefresh} disabled={!caseId || loading}>
          {loading ? "Chargement…" : "Actualiser"}
        </button>
      </div>
      {!caseId ? (
        <div className="empty-card"><strong>Aucune affaire sélectionnée</strong><p>Sélectionnez une affaire pour lire son profil.</p></div>
      ) : profiles.length === 0 && !loading ? (
        <div className="empty-card"><strong>Aucun profil enregistré</strong><p>L'applicabilité réglementaire n'est pas encore documentée.</p></div>
      ) : (
        <div className="decision-grid">
          {profiles.map((profile) => (
            <article className="detail-panel" key={profile.profile_id}>
              <div className="panel-heading">
                <div>
                  <h3>Profil v{profile.profile_version}</h3>
                  <p>{profile.source_refs.join(" · ")}</p>
                </div>
                <span className={`state-badge state-${profile.status.toLowerCase()}`}>
                  {statusLabels[profile.status]}
                </span>
              </div>
              <dl className="decision-facts">
                {Object.entries(profile.facts).map(([key, value]) => (
                  <div key={key}><dt>{key}</dt><dd>{String(value)}</dd></div>
                ))}
              </dl>
              <p className="panel-empty">Lecture seule : aucune conclusion juridique n'est déduite.</p>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
