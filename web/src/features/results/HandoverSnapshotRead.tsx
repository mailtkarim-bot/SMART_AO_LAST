import { useState } from "react";
import type { CaseHandoverSnapshotItem } from "../../shared/types";
export function HandoverSnapshotRead({
  item,
  canReceive,
  disabled,
  onDownload,
  onReceive
}: {
  item: CaseHandoverSnapshotItem;
  canReceive: boolean;
  disabled: boolean;
  onDownload: () => void;
  onReceive: (kind: "RECEIVED" | "RECEIVED_WITH_GAPS", note: string) => void;
}) {
  const [note, setNote] = useState('');
  const [kind, setKind] = useState<'RECEIVED' | 'RECEIVED_WITH_GAPS'>('RECEIVED_WITH_GAPS');
  const [confirmed, setConfirmed] = useState(false);
  const snapshot = item.snapshot;
  const review = snapshot.operational_review;
  return <article className="review-card">
 <h3>Lot {item.lot_reference} · passation v{item.revision}</h3><p>{item.source_state ?? 'UNKNOWN'} · {item.source_reasons?.join(' · ')}</p>
 <p>Offre P5 v{item.package_version} · SHA-256 {item.manifest_sha256}</p><p>Version DCE de l’offre : {snapshot.offer.dce_version_id}</p>
 <button className="secondary-button" type="button" disabled={disabled} onClick={onDownload}>Télécharger l’offre technique exacte</button>
 <p>Rapprochement contrat / offre : {snapshot.contract_comparison.state}</p><p>{snapshot.contract_comparison.reason}</p>
 {snapshot.contract_comparison.instrument_version_id && <p>Version contractuelle déclarée : {snapshot.contract_comparison.instrument_version_id} · empreinte d’enregistrement {snapshot.contract_comparison.record_sha256}. SHA du fichier : {snapshot.contract_comparison.file_sha256 ?? 'UNKNOWN'} · autorité juridique : {snapshot.contract_comparison.authority_state ?? 'UNKNOWN'}.</p>}
 <h4>Conditions non levées</h4>{snapshot.decision.open_conditions.length === 0 ? <p>Conditions : {snapshot.decision.conditions_state === 'KNOWN' ? 'aucune condition ouverte enregistrée' : 'UNKNOWN'}</p> : <ul>{snapshot.decision.open_conditions.map(c => <li key={c.condition_id}>{c.label} · échéance {c.due_at ?? 'UNKNOWN'}<small> · source {c.condition_id} · {c.status}</small></li>)}</ul>}
 <h4>Engagements, exclusions, écarts et actions publiés</h4>
 {review?.points.length ? <dl>{review.points.map(point => <div key={point.point_id}>
 <dt>{point.kind} · {point.criticality}</dt><dd>{point.statement}</dd>
 <dd>Offre : {point.offer_locator ?? 'UNKNOWN'} · extrait {point.offer_excerpt ?? 'UNKNOWN'}</dd>
 <dd>Preuve de l’extrait : {snapshot.offer_point_proofs?.[point.point_id]?.state ?? 'UNKNOWN'}</dd>
 {snapshot.offer_point_proofs?.[point.point_id]?.state === 'EXACT_DOCX_TEXT_MATCH' && <dd>Source DOCX : {snapshot.offer_point_proofs[point.point_id].locator ?? 'UNKNOWN'} · SHA-256 XML : {snapshot.offer_point_proofs[point.point_id].part_sha256 ?? 'UNKNOWN'} · Plage UTF-8 du paragraphe : {snapshot.offer_point_proofs[point.point_id].text_start_byte_offset ?? 'UNKNOWN'}–{snapshot.offer_point_proofs[point.point_id].text_end_byte_offset ?? 'UNKNOWN'}. Ces positions ne sont pas des offsets dans le ZIP.</dd>}
 <dd>Contrat déclaré : {point.contract_locator ?? 'UNKNOWN'} · {point.difference_state} · {point.difference_note ?? 'UNKNOWN'}</dd>
 <dd>Responsable déclaré : {point.responsible ?? 'UNKNOWN'} · action : {point.action ?? 'UNKNOWN'}</dd>
 <dd>Preuve attendue : {point.expected_evidence ?? 'UNKNOWN'} · date déclarée : {point.due_date ?? 'UNKNOWN'}</dd>
 </div>)}</dl> : <p>UNKNOWN · aucune reformulation opérationnelle publiée.</p>}
 <p>Complétude du dossier : {review?.completeness ?? 'PARTIAL'} · aucune complétude déduite.</p>
 {!!review?.missing.length && <details><summary>Relations et preuves manquantes ({review.missing.length})</summary><ul>{review.missing.map((missing, index) => <li key={index}>{missing}</li>)}</ul></details>}
 {review?.published_at && <p>Publication : {review.published_at} · auteur {review.publisher_id} · {review.justification}</p>}
 <p>P7 ≠ ordre de service. Ni réception externe, ni droit acquis ou lancement de travaux déduits.</p>
 <h4>Réceptions opérationnelles du dossier</h4>{item.receipts_truncated&&<p>Historique des reçus tronqué aux 100 derniers · couverture UNKNOWN.</p>}{item.receipts?.length ? <ul>{item.receipts.map(r => <li key={r.receipt_id}>{r.receipt_kind} · {r.scope_state} · {r.created_at} · {r.note}</li>)}</ul> : <p>UNKNOWN · aucun reçu enregistré.</p>}
 {canReceive && item.view_sha256 && item.source_state !== 'HISTORICAL' && <form className="workflow-form" onSubmit={e => {
      e.preventDefault();
      if (confirmed && note.trim()) onReceive(kind, note.trim());
    }}><fieldset disabled={disabled}><legend>Accuser réception de cette version du dossier</legend>
 <p>Vue exacte SHA-256 : {item.view_sha256}. Ce reçu ne valide ni le contrat, ni la complétude, ni un démarrage.</p>
 <label>État du reçu<select value={kind} onChange={e => {
            setKind(e.target.value as typeof kind);
            setConfirmed(false);
          }}><option value="RECEIVED_WITH_GAPS">Reçu avec manques / inconnus</option><option value="RECEIVED" disabled={item.source_state !== 'CURRENT' || !!review?.missing.length}>Reçu sans nouveau manque déclaré</option></select></label>
 <label>Note de réception<textarea required maxLength={2000} value={note} onChange={e => {
            setNote(e.target.value);
            setConfirmed(false);
          }} /></label>
 <label><input type="checkbox" checked={confirmed} onChange={e => setConfirmed(e.target.checked)} />Je confirme la réception opérationnelle de cette version exacte, avec ses inconnus.</label>
 <button className="primary-button" type="submit" disabled={!confirmed || !note.trim()}>Enregistrer le reçu du dossier</button></fieldset></form>}
 </article>;
}
