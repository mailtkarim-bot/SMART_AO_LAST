import type { SubmissionFinalControl as Control } from '../../shared/types';

const reasons: Record<string,string> = {
  MIME_EQUAL:'Le MIME de la pièce correspond au format cité.',
  MIME_DIFFERS:'Le MIME de la pièce diffère du format cité.',
  TARGET_FILE_MISSING:'La pièce ciblée est absente des fichiers du pli exact.',
  OBSERVED_FILE_UNKNOWN:'Le format ou les octets de la pièce ne sont pas vérifiés.',
  SOURCE_NOT_CURRENT:'La source courante ne peut pas être établie.',
  SOURCE_NOT_CONFIRMED:'Le signal source reste à confirmer humainement.',
  SOURCE_ANCHOR_UNKNOWN:'L’ancre ou l’empreinte de la source ne permet pas ce rapprochement.',
  UNSUPPORTED_SOURCE_FAMILY:'La famille de source n’est pas prise en charge par ce rapprochement.',
  LOT_SCOPE_UNKNOWN:'L’applicabilité de la consigne aux lots n’est pas établie.',
  TARGET_SCOPE_UNKNOWN:'Portée de la demande non établie : aucune pièce n’est choisie par inférence.',
  TRUNCATED_OR_LIMITED_SOURCE:'Source tronquée ou limite de lecture : rapprochement UNKNOWN.',
  UNSUPPORTED_OR_AMBIGUOUS_SIGNAL:'Formulation non prise en charge ou ambiguë : lecture humaine requise.',
  EXTERNAL_CHANNEL_NOT_VERIFIED:'Le canal acheteur n’est pas vérifié par un export local.',
  LOCAL_ZIP_ONLY:'ZIP local observé ; remise et acceptation externes non vérifiées.',
  LOCAL_ZIP_DIFFERS:'L’export ZIP local diffère du conditionnement cité.',
  UNRESOLVED_SCOPED_SOURCE:'Une autre consigne courante sur cette portée reste ambiguë : rapprochement UNKNOWN.',
  CONFLICTING_SOURCE_REQUIREMENTS:'Consignes distinctes : priorité ou cumul non établis.',
};
const targets:Record<string,string>={TECHNICAL_RESPONSE:'Mémoire technique',KBIS:'KBIS',DELIVERY:'Conditionnement',UNSPECIFIED:'Pièce non établie'};
const wanted:Record<string,string>={ZIP:'Archive ZIP',NO_ZIP:'ZIP interdit',INDIVIDUAL_FILES:'Fichiers individuels',UNKNOWN:'UNKNOWN'};
const states:Record<string,string>={OBSERVED_MATCH:'Concordance observée',OBSERVED_MISMATCH:'Écart observé',UNKNOWN:'Rapprochement UNKNOWN'};

export function BuyerFormatComparisons({report}:{report:Control}) {
  const rows=report.format_comparisons??[];
  return <section className="rc-candidate-values" aria-label="Formats demandés et pli exact">
    <h4>Formats demandés et pli exact</h4>
    <p>Export local observé : {report.local_delivery_mode==='LOCAL_ZIP'?'ZIP':'UNKNOWN'}. Dépôt externe non effectué.</p>
    <p>Ces observations portent sur les formats et le conditionnement connus. Elles ne prouvent ni l’applicabilité d’une consigne, ni l’acceptation acheteur, ni la conformité. Portée juridique : UNKNOWN.</p>
    {rows.length===0&&<p>Consignes exploitables : UNKNOWN. L’absence de signal connu ne prouve pas l’absence d’exigence.</p>}
    {rows.map(row=><details key={row.requirement_id}>
      <summary>{states[row.state]??'Rapprochement UNKNOWN'} · {targets[row.scope]??'UNKNOWN'} · {wanted[row.requested]??row.requested}</summary>
      <blockquote>{row.source_excerpt??'Extrait source UNKNOWN'}</blockquote>
      <p>Source : {row.source_locator} · Confirmation du signal : {row.confirmation}</p>
      <p>Exigence : {row.requirement_id}</p>
      {row.source_anchor&&<p>DCE : {String(row.source_anchor.dce_version_id??'UNKNOWN')} · Document : {String(row.source_anchor.dce_document_id??'UNKNOWN')} · SHA-256 source : {String(row.source_anchor.source_sha256??'UNKNOWN')}</p>}
      <p>{reasons[row.reason_code]??'Raison non établie : lecture humaine requise.'}</p>
      {row.files.length>0&&<ul>{row.files.map(file=><li key={file.archive_path}>{file.archive_path} · MIME : {file.media_type??'UNKNOWN'} · SHA-256 : {file.sha256}</li>)}</ul>}
      <p>Applicabilité : UNKNOWN · Conformité : UNKNOWN.</p>
    </details>)}
  </section>;
}
