import { caseResolutionItemKinds, type CaseResolution, type CaseResolutionItemKind } from "../../shared/types";

type Props = {
  caseId: string;
  projection: CaseResolution | null;
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
};

const groupLabels: Record<CaseResolutionItemKind, string> = {
  REQUIREMENT: "Exigences",
  INFORMATION_REQUEST: "Demandes d’information",
  TASK_BLOCKER: "Blocages de tâche",
  CONTRADICTION: "Contradictions",
  RISK: "Risques",
  UNKNOWN: "Inconnus",
  CAPABILITY_GAP: "Écarts de capacité",
};

const actions: Record<string, string> = {
  CONFIRM_REQUIREMENT: "Confirmer l’exigence dans son contexte source",
  REVIEW_REQUIREMENT: "Revoir l’exigence dans son contexte source",
  RESPOND_INFORMATION_REQUEST: "Répondre à la demande d’information",
  RESOLVE_TASK_BLOCKER: "Examiner le blocage de la tâche",
  REVIEW_RISK: "Revoir le risque dans son contexte source",
  REVIEW_CONTRADICTION: "Revoir les sources de la contradiction",
  REVIEW_CAPABILITY_GAP: "Revoir l’écart de capacité",
  REVIEW_UNKNOWN: "Revoir l’information inconnue dans sa source",
};

const owners: Record<string, string> = {
  PATRON_ADMIN: "Patron administrateur",
  COLLABORATEUR: "Collaborateur",
  EXTERNAL_PARTY: "Partie externe",
};

function dateLabel(value: string | null) {
  if (!value || Number.isNaN(Date.parse(value))) return "Échéance inconnue";
  return `${new Intl.DateTimeFormat("fr-FR", { dateStyle: "short", timeStyle: "short", timeZone: "UTC" }).format(new Date(value))} UTC`;
}

export function CaseResolutionPanel({ caseId, projection, loading, error, onRefresh }: Props) {
  const current = !loading && !error && projection?.case_id === caseId ? projection : null;
  return (
    <section className="case-resolution" aria-labelledby="case-resolution-title" aria-busy={loading}>
      <div className="case-resolution-heading">
        <div>
          <h2 id="case-resolution-title">À résoudre</h2>
          <p>{current?.work_label || "Points disponibles pour l’affaire sélectionnée"}</p>
        </div>
        <button className="secondary-button" type="button" disabled={!caseId || loading} onClick={onRefresh}>
          {loading ? "Chargement…" : "Actualiser"}
        </button>
      </div>
      {current && <div className="case-resolution-coverage"><strong>Couverture partielle</strong><p>Cette vue réunit les points retournés par les sources disponibles. Les états restent propres à chaque objet; aucune clôture globale n’est déduite.</p></div>}
      {!caseId ? <p className="case-resolution-message">Sélectionnez une affaire pour consulter ses points à résoudre.</p>
        : loading ? <p className="case-resolution-message" role="status">Chargement des points à résoudre…</p>
        : error ? <p className="case-resolution-message" role="alert">{error}</p>
        : !current ? <p className="case-resolution-message">La projection n’est pas disponible pour cette affaire.</p>
        : current.items.length === 0 ? <div className="case-resolution-message"><strong>Aucun point retourné dans le périmètre disponible</strong><p>La couverture reste partielle : cette absence ne vaut ni validation ni clôture de l’affaire.</p></div>
        : <div className="case-resolution-groups">{caseResolutionItemKinds.map((kind) => {
          const items = current.items.filter((item) => item.item_kind === kind);
          if (items.length === 0) return null;
          return <section className="case-resolution-group" key={kind} aria-labelledby={`resolution-${kind}`}>
            <div className="case-resolution-group-heading"><h3 id={`resolution-${kind}`}>{groupLabels[kind]}</h3><span className="count-pill" aria-label={`${items.length} élément${items.length > 1 ? "s" : ""} retourné${items.length > 1 ? "s" : ""}`}>{items.length}</span></div>
            <ul className="case-resolution-items">{items.map((item) => <li key={`${kind}:${item.item_id}`}>
              <div className="case-resolution-item-main"><strong>{actions[item.next_action] || item.next_action}</strong><span className="case-resolution-native-state">{item.native_state}</span><p>{item.impact || "Impact non renseigné"}</p></div>
              <dl className="case-resolution-meta"><div><dt>Responsable</dt><dd>{item.resolution_owner ? owners[item.resolution_owner] || item.resolution_owner : "Responsable inconnu"}</dd></div><div><dt>Échéance</dt><dd>{dateLabel(item.due_at)}</dd></div></dl>
              <details className="case-resolution-sources"><summary>Sources et identifiant</summary><p>Identifiant source : {item.item_id}</p>{item.source_refs.length ? <ul>{item.source_refs.map((ref, index) => <li key={`${index}:${ref}`}>{ref}</li>)}</ul> : <p>Référence de source inconnue.</p>}</details>
            </li>)}</ul>
          </section>;
        })}</div>}
    </section>
  );
}
