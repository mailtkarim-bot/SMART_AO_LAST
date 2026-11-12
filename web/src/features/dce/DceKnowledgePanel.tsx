import type { CaseDceReading, KnowledgeSearchResult } from "../../shared/types";

type Props = {
  sourceReadBlocked?: boolean;
  selectedCaseId: string;
  reading: CaseDceReading | null;
  results: KnowledgeSearchResult[];
  query: string;
  loading: boolean;
  searching: boolean;
  onQueryChange: (query: string) => void;
  onLoad: () => void;
  onSearch: () => void;
  onResetSearch: () => void;
};

function formatDate(value: string) {
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? "Date invalide"
    : new Intl.DateTimeFormat("fr-FR", { dateStyle: "medium" }).format(date);
}

function locatorLabel(locator: Record<string, unknown>) {
  const label = locator.label ?? locator.page ?? locator.section;
  return typeof label === "string" ? label : "Localisation source non précisée";
}

const extractionLabels = {
  NOT_STARTED: "Non extraite",
  COMPLETED: "Extraction enregistrée",
  REVIEW_REQUIRED: "À revoir",
  UNSUPPORTED: "Format non pris en charge",
  REJECTED_LIMIT: "Limite d’extraction atteinte",
  FAILED_SAFE: "Extraction refusée",
};

const coverageExceptionLabels = {
  EXCLUDED_COMPRESSION: "Compression non qualifiée, entrée exclue",
  NOT_EXTRACTED: "Membre non extrait et non admis",
  NESTED_ARCHIVE: "Sous-archive inventoriée, contenu non admis",
  DIRECTORY: "Répertoire, sans preuve de complétude",
  EXCLUDED_UNSAFE: "Chemin dangereux exclu",
  EXCLUDED_SYMLINK: "Lien symbolique exclu",
  EXCLUDED_ENCRYPTED: "Contenu chiffré exclu",
  EXCLUDED_LIMIT: "Limite atteinte, contenu exclu",
  UNREADABLE: "Entrée ou ancre illisible, à revoir",
  INVENTORY_LIMIT: "Inventaire interrompu par une limite",
  DECLARED_MISSING: "Absence déclarée, à vérifier",
};

const announcementLabels = {
  PROVIDED_SIGNAL: "Annonce de pièce fournie · à vérifier",
  NOT_PROVIDED_SIGNAL: "Annonce de pièce non fournie · à vérifier",
  SUBMISSION_SIGNAL: "Annonce de pièce à remettre · à vérifier",
  NOT_REQUIRED_SIGNAL: "Remise annoncée non requise · à vérifier",
  PROHIBITED_SUBMISSION_SIGNAL: "Annonce d’interdiction de remise · à vérifier",
  AMBIGUOUS: "Annonce ambiguë · UNKNOWN",
};
const announcementScanLabels = {
  UNKNOWN: "Sources RC non qualifiées pour cette lecture.",
  CANDIDATES_ONLY: "Candidats lexicaux uniquement; présence, applicabilité et criticité non prouvées.",
  REVIEW_REQUIRED: "Source RC incomplète ou discordante; relecture requise.",
  REJECTED_LIMIT: "Limite de lecture RC atteinte; couverture inconnue.",
};

function RcCandidateValues({ requirement, reading }: {
  requirement: CaseDceReading["requirements"][number];
  reading: CaseDceReading;
}) {
  const candidate = requirement.structured_candidate;
  const anchor = requirement.source_anchor;
  if (!candidate || candidate.state !== "CANDIDATES_ONLY") {
    return <p className="muted-copy">{candidate?.state === "REVIEW_REQUIRED" ? "Valeurs à revoir · REVIEW_REQUIRED" : "Valeurs non prouvées · UNKNOWN"}</p>;
  }
  const declared = [
    ...(candidate.document_state === "CANDIDATE" ? candidate.documents.map(value => ["DOCUMENT", value]) : []),
    ...(candidate.date_state === "CANDIDATE" && candidate.date_iso ? [["DATE", candidate.date_iso]] : []),
    ...(candidate.time_state === "CANDIDATE" && candidate.time_local ? [["TIME", candidate.time_local]] : []),
    ...(candidate.timezone_state === "CANDIDATE" && candidate.timezone ? [["TIMEZONE", candidate.timezone]] : []),
    ...(candidate.lot_state === "CANDIDATE" ? candidate.lot_numbers.map(value => ["LOT", String(value)]) : []),
  ];
  const sourced = candidate.projector_version === "1" && reading.dce_freshness === "CURRENT" &&
    reading.availability === "AVAILABLE" && reading.dce.lifecycle === "ADMITTED" && reading.dce.integrity === "VERIFIED" &&
    requirement.document_family === "RC" && anchor?.locator_state === "RESOLVED" && anchor.locator !== null &&
    anchor.dce_version_id === reading.dce.dce_version_id && anchor.source_anchor_id === candidate.source_fragment_id &&
    declared.length > 0 && declared.every(([field, value]) => candidate.evidence.some(proof =>
      proof.field === field && proof.value === value && Number.isInteger(proof.start_byte_offset) &&
      Number.isInteger(proof.end_byte_offset) && proof.start_byte_offset >= 0 && proof.end_byte_offset > proof.start_byte_offset));
  if (!sourced) return <p className="muted-copy">Valeurs non prouvées · UNKNOWN</p>;
  return (
    <section className="rc-candidate-values" aria-label="Valeurs candidates du RC">
      <p className="muted-copy">Valeurs citées candidates · à vérifier dans la source. Aucune conformité ni échéance applicable déduite.</p>
      <dl>
        <div><dt>Pièces attendues candidates</dt><dd>{candidate.document_state === "CANDIDATE" ? candidate.documents.join(", ") : "UNKNOWN"}</dd></div>
        <div><dt>Date de remise citée</dt><dd>{candidate.date_state === "CANDIDATE" ? candidate.date_iso : "UNKNOWN"}</dd></div>
        <div><dt>Heure citée</dt><dd>{candidate.time_state === "CANDIDATE" ? candidate.time_local : "UNKNOWN"}</dd></div>
        <div><dt>Fuseau</dt><dd>Fuseau : {candidate.timezone_state === "CANDIDATE" ? candidate.timezone : "UNKNOWN"}</dd></div>
        <div><dt>Lots cités</dt><dd>{candidate.lot_state === "CANDIDATE" ? candidate.lot_numbers.join(", ") : "UNKNOWN"}</dd></div>
        <div><dt>Applicabilité</dt><dd>Applicabilité : UNKNOWN</dd></div>
      </dl>
      <details className="dce-source-anchor">
        <summary>Régions des valeurs candidates · {requirement.source_locator_label}</summary>
        <ul>{candidate.evidence.filter(proof => declared.some(([field, value]) => proof.field === field && proof.value === value)).map((proof, i) => (
          <li key={i}>{proof.field} · {proof.value} · octets {proof.start_byte_offset}–{proof.end_byte_offset}</li>
        ))}</ul>
      </details>
    </section>
  );
}

export function DceKnowledgePanel({
  selectedCaseId,
  sourceReadBlocked = false,
  reading: suppliedReading,
  results: suppliedResults,
  query,
  loading,
  searching,
  onQueryChange,
  onLoad,
  onSearch,
  onResetSearch,
}: Props) {
  const reading = !sourceReadBlocked && suppliedReading?.case_id === selectedCaseId ? suppliedReading : null;
  const results = sourceReadBlocked ? [] : suppliedResults;
  return (
    <section className="section-block dce-knowledge-section" id="dce-knowledge-section">
      <div className="section-heading">
        <div>
          <span className="section-kicker">LECTURE DCE · RAG SOURCÉ</span>
          <h2>Comprendre le dossier</h2>
        </div>
        <button className="secondary-button compact-button" type="button" onClick={onLoad} disabled={sourceReadBlocked || !selectedCaseId || loading}>
          {loading ? "Lecture…" : "Actualiser la lecture"}
        </button>
      </div>
      <p className="section-note">Les résultats indiquent une source et un emplacement ; ils ne constituent pas une décision automatique.</p>
      {sourceReadBlocked ? <p role="status">Admission DCE en cours ou UNKNOWN : anciennes sources suspendues ; réessayez le même acte avant toute nouvelle lecture.</p> : !selectedCaseId ? (
        <div className="empty-card"><strong>Sélectionnez une affaire</strong><p>La lecture DCE et la recherche knowledge restent limitées à l’affaire choisie.</p></div>
      ) : !reading && loading ? (
        <div className="empty-card"><strong>Lecture DCE en cours</strong><p>Le serveur prépare une projection minimale tenant-scoped.</p></div>
      ) : !reading ? (
        <div className="empty-card"><strong>Lecture DCE indisponible</strong><p>La projection n’est pas encore disponible pour cette affaire, ou nécessite une recette backend.</p></div>
      ) : (
        <div className="dce-knowledge-layout">
          <div className="dce-reading-panel">
            <div className="dce-reading-heading"><div><span className="section-kicker">PROJECTION DCE</span><h3>{reading.work_label}</h3></div><span className="state-badge state-monitor">{reading.dce_freshness}</span></div>
            <div className="dce-meta"><span>{reading.dce.lifecycle}</span><span>Version {reading.dce.dce_version_id}</span><span>Reçu le {formatDate(reading.dce.source_received_at)}</span></div>
            <div className="dce-readiness" role="status">
              <div><span>Classification</span><strong>{reading.dce.classification_readiness}</strong></div>
              <div><span>Analyse</span><strong>{reading.dce.analysis_readiness}</strong></div>
              {reading.dce.classification_readiness !== "CLASSIFIED" && (
                <p>La synthèse reste partielle : les pièces non classifiées ou à revoir restent visibles.</p>
              )}
            </div>
            <div className="requirement-list">
              <h3>Couverture documentaire</h3>
              {!reading.coverage ? (
                <p className="muted-copy">Couverture documentaire non disponible</p>
              ) : (
                <>
                  <strong>Analyse complète non démontrée</strong>
                  <p className="section-note">Inventaire limité aux pièces admises dans cette version. Les archives et pièces annoncées manquantes restent à vérifier. Criticité et applicabilité par lot inconnues.</p>
                  <p>{reading.coverage.total_documents} pièces connues · {reading.coverage.completed_extractions} extractions enregistrées · {reading.coverage.unread_documents} pièces sans extraction prouvée</p>
                  <details>
                    <summary>Consulter les {reading.coverage.total_documents} pièces connues</summary>
                    {reading.coverage.documents.length === 0 && <p>Aucune pièce admise recensée; couverture inconnue.</p>}
                    {reading.coverage.documents.map((document) => (
                      <div className="requirement-row" key={document.document_id}>
                        <div>
                          <strong>Pièce {document.document_id}</strong>
                          <span>{document.document_family === "SOURCE_UNCLASSIFIED" ? "Famille inconnue" : document.document_family}</span>
                          {document.extraction_id && <small>Extraction {document.extraction_id}</small>}
                        </div>
                        <span className="state-badge state-monitor">{extractionLabels[document.extraction_status] ?? "État inconnu"}</span>
                      </div>
                    ))}
                  </details>
                  {(reading.coverage.exceptions?.length ?? 0) > 0 && (
                    <details>
                      <summary>Archives et pièces annoncées · {reading.coverage.exceptions?.length} constats à revoir</summary>
                      {reading.coverage.exceptions?.map((item) => (
                        <div className="requirement-row" key={item.observation_id}>
                          <div>
                            <strong>{item.kind === "DECLARED_MISSING"
                              ? `Pièce annoncée manquante · ${item.document_family === "SOURCE_UNCLASSIFIED" ? "famille inconnue" : item.document_family}`
                              : `Entrée d’archive ${item.entry_path.length ? item.entry_path.join(" › ") : "non localisée"}`}</strong>
                            <span>{coverageExceptionLabels[item.state] ?? "État inconnu"}</span>
                            <small>{item.source_state === "RESOLVED" ? "Ancre structurelle reliée, sans preuve d’analyse" : "Source non qualifiée · UNKNOWN"}</small>
                            {item.document_id && <small>Pièce {item.document_id} · extraction {item.extraction_id ?? "UNKNOWN"}</small>}
                            <small>Constat {item.observation_id} · lot et criticité UNKNOWN</small>
                          </div>
                        </div>
                      ))}
                    </details>
                  )}
                  <div>
                    <h3>Annonces de pièces du RC · candidats</h3>
                    <p className="section-note">{announcementScanLabels[reading.coverage.announcement_scan_state ?? "UNKNOWN"]}</p>
                    <p className="muted-copy">Un nom ou une famille correspondante ne suffit pas à prouver une présence ou une absence.</p>
                    {(reading.coverage.announcements?.length ?? 0) === 0 ? (
                      <p>Aucun candidat restitué dans cette lecture; ce résultat ne prouve pas l’absence d’annonce.</p>
                    ) : (
                      <details>
                        <summary>Consulter les {reading.coverage.announcements?.length} annonces candidates</summary>
                        {reading.coverage.announcements?.map((item) => (
                          <div className="requirement-row" key={item.candidate_id}>
                            <div>
                              <strong>{item.document_family} · annonce candidate</strong>
                              <span>{announcementLabels[item.claim] ?? "Annonce inconnue · UNKNOWN"}</span>
                              <small>{item.source_locator_label}</small>
                              <small>{item.lot_numbers.length ? `Lots explicitement cités : ${item.lot_numbers.join(", ")}` : "Portée lot non résolue · UNKNOWN"}</small>
                              {item.conflict_state === "CONFLICTING_CANDIDATES" && <strong>Signaux opposés à confronter</strong>}
                              <small>Rapprochement exact non prouvé · UNKNOWN</small>
                              <small>{item.family_candidate_document_ids.length} pièce(s) candidate(s) par famille; présence, applicabilité et criticité UNKNOWN</small>
                              <small>Pièce source {item.source_document_id} · extraction {item.source_extraction_id}</small>
                              <small>Fragment {item.source_fragment_id} · octets {item.start_byte_offset}–{item.end_byte_offset} · localisation {item.source_locator_state}</small>
                              {item.context_start_byte_offset !== null && <small>{item.context_fragment_id && item.context_fragment_id !== item.source_fragment_id ? `En-tête lié · ${item.context_locator_label ?? "localisation UNKNOWN"} · fragment ${item.context_fragment_id}` : "En-tête lié dans le même fragment"} · octets {item.context_start_byte_offset}–{item.context_end_byte_offset}</small>}
                              {!!item.anchor_chain?.length && <div>
                                <small>Chaîne de provenance · {item.anchor_chain.length} régions</small>
                                {item.anchor_chain.map((anchor) => <small key={`${anchor.fragment_id}:${anchor.kind}:${anchor.start_byte_offset}:${anchor.end_byte_offset}`}>
                                  {{ HEADING: "En-tête", BRIDGE: "Continuité", SOURCE: "Annonce" }[anchor.kind]} · {anchor.locator_label} · partie {anchor.part} · fragment {anchor.fragment_id} · octets {anchor.start_byte_offset}–{anchor.end_byte_offset}
                                </small>)}
                              </div>}
                            </div>
                          </div>
                        ))}
                      </details>
                    )}
                  </div>
                </>
              )}
            </div>
            <div className="dce-counter-grid">
              <div><strong>{reading.counters.total}</strong><span>Exigences</span></div>
              <div><strong>{reading.counters.pending_human_confirmation}</strong><span>À confirmer</span></div>
              <div><strong>{reading.counters.confirmed}</strong><span>Confirmées</span></div>
              <div><strong>{reading.counters.review_required}</strong><span>À revoir</span></div>
            </div>
            <div className="requirement-list">
              <div className="subheading"><span className="section-kicker">EXIGENCES STRUCTURÉES</span><span>{reading.requirements.length} affichées</span></div>
              {reading.requirements.length === 0 ? <p className="muted-copy">Aucune exigence structurée dans cette projection.</p> : reading.requirements.map((requirement) => (
                <div className="requirement-row rc-requirement-row" key={requirement.requirement_id}>
                  <div>
                    <strong>{requirement.requirement_type}</strong>
                    <span>{requirement.document_family} · {requirement.source_locator_label}</span>
                    <RcCandidateValues requirement={requirement} reading={reading} />
                    <details className="dce-source-anchor">
                      <summary>Provenance de la source · {requirement.source_anchor?.locator_state ?? "UNKNOWN"}</summary>
                      {requirement.source_anchor ? (
                        <div>
                          <small>Version {requirement.source_anchor.dce_version_id} · pièce {requirement.source_anchor.dce_document_id} · extraction {requirement.source_anchor.extraction_id}</small>
                          <small>Ancre {requirement.source_anchor.source_anchor_id} · fragment {requirement.source_anchor.fragment_ordinal}</small>
                          {requirement.source_anchor.locator ? (
                            <small>Type de localisation : {requirement.source_anchor.locator.kind}</small>
                          ) : (
                            <strong>Localisation source non résolue</strong>
                          )}
                          <small>Extracteur {requirement.source_anchor.extractor_id} · v{requirement.source_anchor.extractor_version}</small>
                          <small>SHA-256 source <code>{requirement.source_anchor.source_sha256}</code></small>
                          <small>SHA-256 fragment <code>{requirement.source_anchor.fragment_sha256}</code></small>
                        </div>
                      ) : (
                        <small>UNKNOWN · ancre de fragment non disponible</small>
                      )}
                    </details>
                  </div>
                  <span className={`state-badge ${requirement.confirmation_outcome === "CONFIRMED" ? "state-success" : "state-warning"}`}>{requirement.confirmation_outcome}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="knowledge-search-panel">
            <div><span className="section-kicker">RECHERCHE SOURCÉE</span><h3>Interroger le DCE</h3></div>
            <label><span>Question ou terme</span><input value={query} onChange={(event) => onQueryChange(event.target.value)} maxLength={500} placeholder="ex. délai d’exécution" /></label>
            <div className="knowledge-actions"><button className="primary-button" type="button" onClick={onSearch} disabled={searching}>{searching ? "Recherche…" : "Rechercher"}<span>→</span></button><button className="secondary-button" type="button" onClick={onResetSearch} disabled={!query && results.length === 0}>Effacer</button></div>
            <div className="knowledge-results" aria-live="polite">
              {results.length === 0 ? <p className="muted-copy">Les résultats avec score et localisation source apparaîtront ici.</p> : results.map((result) => <article className="knowledge-result" key={result.source_fragment_id}><div className="knowledge-result-top"><strong>{Math.round(result.score * 100)}%</strong><span>{result.embedding_model}</span></div><p>{locatorLabel(result.locator)}</p><small>Fragment source {result.source_fragment_id}</small></article>)}
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
