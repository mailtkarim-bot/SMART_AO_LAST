import type { AnalysisCapacityPlan } from '../../shared/types';

type Props = { plans: AnalysisCapacityPlan[]; caseId: string; current: boolean };

export function AnalysisCapacity({ plans, caseId, current }: Props) {
  return (
    <div aria-label="Planifications de capacité enregistrées" style={{ overflowWrap: 'anywhere' }}>
      <p>
        Aucune réservation ni disponibilité réelle n’est déduite de ce calcul.
        Couverture globale : UNKNOWN · Portée lot : UNKNOWN.
      </p>
      {!plans.length && <p>Planification enregistrée : UNKNOWN.</p>}
      <ul>
        {plans.map(plan => {
          const details = plan.details;
          const qualified = current && plan.state === 'RECORDED' && details?.case_id === caseId;
          return (
            <li key={plan.run_id}>
              <p>
                Calcul enregistré {plan.run_id} · Révision {plan.revision} ·
                Empreinte des entrées : {plan.input_sha256}
              </p>
              {qualified && details ? (
                <>
                  <p>
                    Statut du solveur enregistré : {details.status} ·
                    Hypothèse humaine : {details.inputs.justification}
                  </p>
                  <details>
                    <summary>Besoins, disponibilités et sources déclarés</summary>
                    {(['demands', 'supplies'] as const).map(kind => (
                      <div key={kind}>
                        <h3>{kind === 'demands' ? 'Besoins déclarés' : 'Disponibilités déclarées'}</h3>
                        {details.inputs[kind] === null ? <p>UNKNOWN</p> : (
                          <ul>
                            {details.inputs[kind]!.map(row => (
                              <li key={row.id}>
                                {row.label} · {row.resource_type ?? 'Type UNKNOWN'} ·
                                {row.units ?? 'Quantité UNKNOWN'} ·
                                {row.start ?? 'Date UNKNOWN'} → {row.end ?? 'Date UNKNOWN'} (fin exclue).
                                Source : {row.source
                                  ? `${row.source.reference} · révision ${row.source.revision} · ${row.source.locator}`
                                  : 'UNKNOWN'}
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>
                    ))}
                    <p>
                      {details.result.assignments.length} affectation(s) calculée(s) ·
                      {details.result.conflicts.length} conflit(s) ·
                      {details.result.unknown_ids.length} entrée(s) inconnue(s).
                      Ce constat ne vaut pas confirmation de disponibilité.
                    </p>
                  </details>
                </>
              ) : (
                <p>
                  Contexte à revalider : UNKNOWN · {plan.unknown_reason ?? 'Source non prouvée'}.
                  Les hypothèses antérieures restent dans l’historique natif.
                </p>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
