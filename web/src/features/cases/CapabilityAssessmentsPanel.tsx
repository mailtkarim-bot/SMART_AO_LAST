import type { DocumentaryAssessment } from "./useCapabilityAssessments";

type Props = {
  caseId: string;
  projection: DocumentaryAssessment[] | null;
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
};

export function CapabilityAssessmentsPanel({ caseId, projection, loading, error, onRefresh }: Props) {
  const current = caseId && !loading && !error ? projection : null;
  return (
    <section className="case-resolution documentary-assessments" aria-labelledby="documentary-assessments-title" aria-busy={loading}>
      <div className="case-resolution-heading">
        <div>
          <h2 id="documentary-assessments-title">Éligibilité documentaire des moyens</h2>
          <p>État documentaire évalué pour cette affaire. Il ne vaut ni disponibilité, ni réservation, ni engagement.</p>
        </div>
        <button className="secondary-button" type="button" disabled={!caseId || loading} onClick={onRefresh}>Actualiser la lecture</button>
      </div>
      {!caseId ? <p className="case-resolution-message">Sélectionnez une affaire pour consulter ses évaluations.</p>
        : loading ? <p className="case-resolution-message" role="status">Chargement des évaluations documentaires…</p>
        : error ? <p className="case-resolution-message" role="alert">{error}</p>
        : !current ? <p className="case-resolution-message">La lecture documentaire n’est pas disponible.</p>
        : current.length === 0 ? <p className="case-resolution-message">Aucune évaluation retournée dans ce périmètre. Cette absence ne vaut pas validation des moyens.</p>
        : <ul className="documentary-assessment-list" aria-label="États documentaires et dates d’évaluation">
          {current.map((row, index) => <li key={index}>
            <strong>{row.state}</strong>
            <div><span className="documentary-assessment-date-label">Évalué le</span> {row.evaluatedAt ? <time dateTime={row.evaluatedAt}>{row.evaluatedAt}</time> : <span>Date inconnue</span>}</div>
          </li>)}
        </ul>}
      <p className="case-resolution-message">CURRENT : documentaire courant à l’évaluation. EXPIRED : documentaire expiré. UNKNOWN : qualification inconnue. Aucune confirmation externe authentifiée n’est déduite.</p>
    </section>
  );
}
