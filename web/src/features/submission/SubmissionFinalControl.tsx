import { BuyerNameSizeComparisons } from "./BuyerNameSizeComparisons";
import { BuyerFormatComparisons } from "./BuyerFormatComparisons";
import type { SubmissionFinalControl as Control } from '../../shared/types';

export function SubmissionFinalControl({ report }: { report: Control }) {
  const formats: Record<string, string> = {
    'application/pdf':'PDF', 'image/png':'PNG', 'image/jpeg':'JPEG', 'text/plain':'Texte',
    'text/markdown':'Markdown',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document':'DOCX',
  };
  const missing = report.requirements.filter(r => r.response_state === 'MISSING');
  const partial = report.requirements.filter(r => r.response_state === 'TEXT_WITH_GAPS');
  const pricing = report.pricing_reference;
  return <div className="response-coverage rc-candidate-values" aria-label="Contrôle final du pli exact">
    <h3>Contrôle final du pli exact</h3>
    <p><strong>{report.state === 'REVIEW_REQUIRED' ? 'Sources à revoir' : report.state === 'UNKNOWN' ? 'Contrôle inconnu' : 'Contrôle partiel'}</strong> · Aucune conformité présumée.</p>
    <p>Paquet {report.submission_package_id} · version {report.package_version}</p>
    <p>SHA-256 du manifeste : <code>{report.manifest_sha256}</code></p>
    <p>DCE : {report.dce_version_id} · Sources : {report.source_state}</p>
    <p>{report.files.length} fichier(s) prévu(s) · {missing.length} réponse(s) manquante(s) · {partial.length} réponse(s) avec manques · {report.missing_cited_annexes.length} annexe(s) citée(s) absente(s).</p>
    <p>Inventaire limité aux signaux non financiers connus. Les montants et pièces financières ne sont pas contrôlés ici. Exhaustivité, signatures requises et pouvoirs : UNKNOWN.</p>
    <details><summary>Fichiers du paquet et empreintes</summary>
      <ul>{report.files.map(f => <li key={f.archive_path}>
        <strong>{f.archive_path}</strong> · {f.presence === 'VERIFIED_SOURCE' ? 'Source vérifiée' : 'Présence UNKNOWN'}
        <p>Nature : {f.document_kind ?? 'UNKNOWN'} · Format : {f.media_type ? (formats[f.media_type] ?? f.media_type) : 'UNKNOWN'} · Validité : UNKNOWN</p>
        <p>SHA-256 : <code>{f.sha256}</code></p>
        <p>{f.byte_size == null ? 'Taille UNKNOWN' : `${f.byte_size} octets`} · Signature de cette pièce : UNKNOWN</p>
        {f.requirement_ids.length > 0 && <p>Exigences : {f.requirement_ids.join(', ')}</p>}
      </li>)}</ul>
      {report.entries_without_exported_file.map(kind => <p key={kind}>Référence sans fichier exporté : {kind}</p>)}
    </details>
    <details open={missing.length > 0 || partial.length > 0}>
      <summary>Exigences connues et manques ({report.requirements.length})</summary>
      {report.requirements.length === 0 && <p>Exigences courantes non vérifiées : relire les sources avant de conclure.</p>}
      <ul>{report.requirements.map(r => <li key={r.requirement_id}>
        <strong>{r.response_state === 'MISSING' ? 'Réponse manquante' : r.response_state === 'TEXT_WITH_GAPS' ? 'Réponse avec manques' : r.response_state === 'TEXT_PRESENT' ? 'Texte présent, couverture UNKNOWN' : 'Réponse UNKNOWN'}</strong>
        <p>{r.document_family} · {r.source_locator} · Lots candidats : {r.lot_candidates.join(', ') || 'UNKNOWN'}</p>
        <p>{r.source_excerpt ?? 'Extrait source UNKNOWN'}</p>
        <p>Exigence {r.requirement_id} · Confirmation : {r.confirmation} · Applicabilité : UNKNOWN</p>
        {r.pieces.filter(p => p.missing).map(p => <p key={`${p.section_code}:${p.locator}`}>{p.section_code} : {p.missing}</p>)}
      </li>)}</ul>
      {report.missing_cited_annexes.map(a => <p key={`${a.requirement_id}:${a.document_id}:${a.section_code}`}>Annexe citée à obtenir : {a.document_id} · exigence {a.requirement_id} · SHA-256 {a.sha256}</p>)}
    </details>
    <BuyerFormatComparisons report={report} />
    <BuyerNameSizeComparisons report={report} />
    <h4>Filiation du chiffrage publié</h4>
    <p>{pricing?.state === 'CURRENT' ? 'Référence du dernier chiffrage publié lors de cette lecture.'
      : pricing?.state === 'REVIEW_REQUIRED' ? 'Chiffrage révisé : cette référence est à relire avant toute nouvelle décision humaine.'
      : pricing?.state === 'NOT_APPLICABLE' ? 'Candidature seule : aucune référence de chiffrage attendue.'
      : 'Référence de chiffrage UNKNOWN : aucune continuité financière établie.'}</p>
    {pricing?.referenced && <p>Rapport lié au pli : {pricing.referenced.report_id} · révision {pricing.referenced.revision}</p>}
    {pricing?.latest_published && <p>Dernier rapport publié de l’Affaire : {pricing.latest_published.report_id} · révision {pricing.latest_published.revision}</p>}
    <p>Aucun accord sur le nouveau chiffrage n’est déduit. Une référence n’est pas une pièce financière exportée, ni un prix certain. Les actes P5 restent rattachés au pli exact.</p>
    {pricing?.state === 'REVIEW_REQUIRED' && <p>Pour reprendre : nouveau brouillon sourcé, nouvelle revue Patron, nouveau pli puis acte P5 sur son manifeste exact. Aucun accord précédent n’est repris.</p>}
    <p>Les flux et hypothèses de trésorerie privés ne sont pas repris automatiquement dans la réponse ni dans le pli.</p>
    <h4>Actes humains rattachés au paquet</h4>
    <p>Revues Patron exactes : {report.patron_review_ids.join(', ') || 'UNKNOWN'}</p>
    <p>P5 {report.p5_authorization_status === 'RECORDED' ? `enregistrée : ${report.p5_authorization_id}` : 'non enregistrée'}. P5 ne vaut ni signature ni conformité.</p>
    {report.source_state !== 'CURRENT' && <p>Les actes du registre sont historiques ; leur applicabilité aux sources courantes reste UNKNOWN.</p>}
    <p>Registre de signature : lecture protégée, état UNKNOWN. Aucun fait ni compteur n'est exposé par ce contrôle.</p>
    <p>Validité cryptographique : UNKNOWN · Signature de chaque pièce : UNKNOWN.</p>
    <p>Dépôt externe non effectué.</p>
  </div>;
}
