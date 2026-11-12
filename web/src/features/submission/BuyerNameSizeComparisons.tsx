import type { SubmissionFinalControl as Control } from '../../shared/types';

const reasons: Record<string, string> = {
  NAME_EQUAL: 'Le nom exporté correspond exactement au nom cité.',
  NAME_DIFFERS: 'Le nom exporté diffère du nom cité, casse et accents compris.',
  NO_WHITESPACE: 'Aucun espace observé dans les noms de fichiers comparés.',
  WHITESPACE_FOUND: 'Un espace est présent dans un nom de fichier comparé.',
  SIZE_WITHIN_LIMIT: 'La taille non compressée est dans la limite citée.',
  SIZE_EXCEEDS_LIMIT: 'La taille non compressée dépasse la limite citée.',
  SIZE_LIMIT_UNKNOWN: 'Limite citée hors plage de comparaison exacte : UNKNOWN.',
  SIZE_UNIT_UNKNOWN: 'Unité de taille ambiguë : conversion en octets UNKNOWN.',
  NAME_PATH_OR_PATTERN_UNKNOWN: 'Chemin ou motif demandé : nom exact UNKNOWN.',
  TARGET_FILE_MISSING: 'La pièce ciblée est absente des fichiers connus du pli exact.',
  TARGET_SCOPE_UNKNOWN: 'La pièce visée ne peut pas être établie.',
  OBSERVED_FILE_UNKNOWN: 'Une taille ou les octets d’un fichier restent UNKNOWN.',
  SOURCE_NOT_CURRENT: 'La source courante ne peut pas être établie.',
  SOURCE_NOT_CONFIRMED: 'Le signal reste à confirmer humainement.',
  SOURCE_ANCHOR_UNKNOWN: 'Ancre ou empreinte source non établie.',
  LOT_SCOPE_UNKNOWN: 'L’applicabilité de la consigne aux lots reste UNKNOWN.',
  UNSUPPORTED_SOURCE_FAMILY: 'Famille de source non prise en charge.',
  TRUNCATED_OR_LIMITED_SOURCE: 'Source tronquée ou limite de lecture : rapprochement UNKNOWN.',
  UNRESOLVED_SCOPED_SOURCE: 'Une autre consigne courante sur cette portée reste ambiguë.',
  CONFLICTING_SOURCE_REQUIREMENTS: 'Noms demandés distincts : arbitrage humain requis.',
  UNSUPPORTED_OR_AMBIGUOUS_SIGNAL: 'Formulation ou portée non prise en charge : lecture humaine requise.',
};
const targets: Record<string, string> = {
  TECHNICAL_RESPONSE: 'Mémoire technique', KBIS: 'KBIS',
  KNOWN_DOCUMENT_FILES: 'Fichiers documentaires connus', UNSPECIFIED: 'Pièce non établie',
};
const states: Record<string, string> = {
  OBSERVED_MATCH: 'Concordance observée', OBSERVED_MISMATCH: 'Écart observé', UNKNOWN: 'Rapprochement UNKNOWN',
};

export function BuyerNameSizeComparisons({ report }: { report: Control }) {
  const rows = report.name_size_comparisons ?? [];
  return <section className="rc-candidate-values" aria-label="Noms et tailles des fichiers">
    <h4>Noms et tailles des fichiers</h4>
    <p>Noms de base dans le ZIP exact, sensibles à la casse et aux accents. Tailles non compressées en octets. Aucun renommage automatique.</p>
    <p>Contrôle limité aux fichiers documentaires connus. Métadonnées manifest.json, taille du ZIP, inventaire exhaustif et contraintes non extraites : UNKNOWN. Une concordance ne prouve pas la conformité acheteur.</p>
    {rows.length === 0 && <p>Consignes de nom ou de taille exploitables : UNKNOWN. Relire les sources avant de conclure.</p>}
    {rows.map(row => <details key={row.requirement_id}>
      <summary>{states[row.state] ?? 'Rapprochement UNKNOWN'} · {targets[row.scope] ?? 'UNKNOWN'} · {row.criterion === 'MAX_BYTES' ? 'Taille' : row.criterion === 'UNKNOWN' ? 'Consigne à relire' : 'Nom'}</summary>
      <blockquote>{row.source_excerpt ?? 'Extrait source UNKNOWN'}</blockquote>
      <p>Source : {row.source_locator} · Confirmation du signal : {row.confirmation}</p>
      <p>Exigence : {row.requirement_id}</p>
      {row.source_anchor && <p>DCE : {String(row.source_anchor.dce_version_id ?? 'UNKNOWN')} · Document : {String(row.source_anchor.dce_document_id ?? 'UNKNOWN')} · SHA-256 source : {String(row.source_anchor.source_sha256 ?? 'UNKNOWN')}</p>}
      {row.requested_name !== null && <p>Nom demandé : {row.requested_name}</p>}
      {row.max_bytes !== null && <p>Taille maximale citée : {row.max_bytes} octets</p>}
      {row.criterion === 'NO_WHITESPACE' && <p>Consigne citée : noms sans espace.</p>}
      <p>{reasons[row.reason_code] ?? 'Raison non établie : lecture humaine requise.'}</p>
      {row.files.length > 0 && <ul>{row.files.map(file => <li key={file.archive_path}>
        <p>Nom exporté : {file.archive_path.split('/').at(-1)} · Taille : {file.byte_size == null ? 'UNKNOWN' : `${file.byte_size} octets`}</p>
        <p>Chemin ZIP : {file.archive_path} · SHA-256 : {file.sha256} · {file.presence === 'VERIFIED_SOURCE' ? 'Source vérifiée' : 'Présence UNKNOWN'}</p>
      </li>)}</ul>}
      <p>Applicabilité : UNKNOWN · Conformité : UNKNOWN.</p>
    </details>)}
  </section>;
}
