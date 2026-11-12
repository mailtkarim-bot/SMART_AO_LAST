import { useEffect, useState } from 'react';
import type { ApiClient } from '../../infrastructure/api';
import type { OperationalChangeView } from '../../shared/types';
export function OperationalChangeRead({
  api,
  caseId
}: {
  api: ApiClient;
  caseId: string;
}) {
  const [refresh, setRefresh] = useState(0);
  const [rows, setRows] = useState<OperationalChangeView[]>([]),
    [state, setState] = useState('LOADING'),
    [truncated, setTruncated] = useState(false);
  useEffect(() => {
    let active = true;
    void api.listOperationalCaseContractChangeEvents(caseId).then(result => {
      if (!active) return;
      if (result.case_id !== caseId || result.events.some(row => row.case_id !== caseId)) throw Error('CHANGE_CASE_MISMATCH');
      setRows(result.events);
      setTruncated(result.truncated);
      setState('READY');
    }).catch(() => {
      if (active) {
        setRows([]);
        setState('UNAVAILABLE');
      }
    });
    return () => {
      active = false;
    };
  }, [api, caseId, refresh]);
  return <section className="section-block decision-section handover-panel" aria-label="Suivi opérationnel des changements"><h2>Changements et actions transmis</h2><p>Seuls les éléments publiés par le Patron sont visibles. Les impacts financiers et pièces privées restent exclus. Aucun OS exécuté ni effet juridique n’est déduit.</p>
 <button className="secondary-button" type="button" onClick={() => {
      setRows([]);
      setState('LOADING');
      setRefresh(value => value + 1);
    }}>Relire les changements publiés</button>
 {state === 'LOADING' && <p role="status">Lecture des changements…</p>}{state === 'UNAVAILABLE' && <p role="status">UNAVAILABLE · droits ou sources à revoir.</p>}{state === 'READY' && !rows.length && <p>UNKNOWN · aucun changement opérationnel publié.</p>}{truncated && <p>Chronologie tronquée · couverture UNKNOWN.</p>}
 {rows.map(row => <article className="review-card" key={row.event_id}><h3>Lot {row.lot_reference} · {row.summary}</h3><p>{row.source_state} · {row.source_reasons.join(' · ')}</p><p>{row.scope_note}</p>
 <p>Passation source : {(row.current_operational_context ?? row.operational_context).handover_snapshot_id} · révision {(row.current_operational_context ?? row.operational_context).handover_revision ?? 'UNKNOWN'} · Empreinte offre : {(row.current_operational_context ?? row.operational_context).offer_manifest_sha256 ?? 'UNKNOWN'}</p>
 <p>Instruction déclarée : {row.source_refs?.join(', ') || 'UNKNOWN'} · Pièces référencées : {row.evidence_refs?.join(', ') || 'UNKNOWN'}. Références déclarées uniquement, fichiers privés non transmis.</p>
 <h4>Engagements transmis concernés</h4>{(row.current_operational_context ?? row.operational_context).points.map(point => <p key={point.point_id}>{point.kind} · {point.statement} · source {point.point_id}</p>)}
 <h4>Delta déclaré</h4>{row.applicability_history.length ? row.applicability_history.map(review => <p key={review.review_id}>{review.source_state} · {review.decision} · {review.delta_note ?? 'UNKNOWN'}</p>) : <p>UNKNOWN · pas de revue opérationnelle publiée.</p>}
 <h4>Actions et preuves attendues</h4>{row.actions.map(action => <div key={action.action_id}><p>{action.source_state} · {action.summary}</p><p>Responsable déclaré : {action.operational_details.responsible ?? 'UNKNOWN'}</p><p>Preuve attendue : {action.operational_details.expected_evidence ?? 'UNKNOWN'} · date déclarée : {action.due_at ?? 'UNKNOWN'}</p>{row.action_execution_acts.filter(act => act.action_id === action.action_id).map(act => <p key={act.act_id}>{act.declared_state} · {act.declared_summary ?? 'UNKNOWN'} · pièce consultable : UNKNOWN (aucune pièce privée transférée)</p>)}</div>)}
 <details><summary>Chronologie sourcée</summary>{row.operational_timeline.map(item => <p key={item.kind + item.record_id}>{item.recorded_at} · {item.kind} · {item.source_state ?? 'UNKNOWN'} · source {item.record_id}</p>)}</details></article>)}
 </section>;
}
