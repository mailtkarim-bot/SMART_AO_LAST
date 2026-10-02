import { useMemo, useState } from "react";
import type {
  BusinessMethodProfileAxis,
  BusinessMethodProfileTerm,
} from "../../shared/types";
import { useBusinessMethodProfile } from "./useBusinessMethodProfile";

type ProfileManager = ReturnType<typeof useBusinessMethodProfile>;

const TERMS: Array<{ key: BusinessMethodProfileTerm; label: string }> = [
  { key: "affair", label: "Affaire" },
  { key: "lot", label: "Lot" },
  { key: "owner", label: "Patron" },
  { key: "collaborator", label: "Collaborateur" },
  { key: "evidence", label: "Preuve" },
];
const AXES: BusinessMethodProfileAxis[] = [
  "CONTRACT", "COST", "CASH", "SCHEDULE", "CAPACITY", "PARTNER", "DOCUMENT",
];

export function BusinessMethodProfilePanel({
  companyId,
  caseId,
  canManage,
  manager,
}: {
  companyId: string;
  caseId: string;
  canManage: boolean;
  manager: ProfileManager;
}) {
  const [terminology, setTerminology] = useState<Partial<Record<BusinessMethodProfileTerm, string>>>({});
  const [checks, setChecks] = useState<Array<{ key: string; label: string; axis: BusinessMethodProfileAxis }>>([]);
  const [formError, setFormError] = useState<string | null>(null);
  const selectedVersion = manager.versions.find(
    (item) => item.profile_version_id === manager.selectedVersionId,
  ) ?? null;
  const draft = useMemo(() => ({
    schema_version: 1 as const,
    terminology: Object.fromEntries(
      Object.entries(terminology)
        .map(([key, value]) => [key, value?.trim() ?? ""])
        .filter(([, value]) => value.length > 0),
    ) as Partial<Record<BusinessMethodProfileTerm, string>>,
    additional_checks: checks
      .filter((item) => item.key.trim() || item.label.trim())
      .map((item) => ({ ...item, key: item.key.trim(), label: item.label.trim() })),
  }), [checks, terminology]);
  const adoptedVersionMatchesSelection = Boolean(
    manager.adoption && selectedVersion &&
    manager.adoption.profile_version_id === selectedVersion.profile_version_id &&
    manager.adoption.profile_version === selectedVersion.version &&
    manager.adoption.profile_content_sha256 === selectedVersion.content_sha256,
  );

  function validateDraft(): boolean {
    const incomplete = draft.additional_checks.find((item) =>
      !item.key || !/^[a-z][a-z0-9_]+$/.test(item.key) || !item.label || item.label.length > 160,
    );
    if (incomplete) {
      setFormError("Chaque contrôle doit avoir une clé (lettres minuscules, chiffres, _), un libellé et un axe.");
      return false;
    }
    if (new Set(draft.additional_checks.map((item) => item.key)).size !== draft.additional_checks.length) {
      setFormError("Les clés de contrôle doivent être uniques.");
      return false;
    }
    if (draft.additional_checks.length > 40) {
      setFormError("Le profil accepte au maximum 40 contrôles informatifs.");
      return false;
    }
    setFormError(null);
    return true;
  }

  async function submitPublish(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canManage || !companyId || !validateDraft()) return;
    if (await manager.publish(draft)) {
      setTerminology({});
      setChecks([]);
    }
  }

  async function submitAdoption() {
    if (!canManage || !caseId || !selectedVersion) return;
    await manager.adopt(selectedVersion);
  }

  return (
    <section className="section-block decision-section" id="business-method-profile-section">
      <div className="section-heading">
        <div>
          <span className="section-kicker">C07 · MÉTHODE ENTREPRISE</span>
          <h2>Profil métier versionné</h2>
        </div>
        <button className="secondary-button" type="button" onClick={manager.refresh} disabled={manager.status === "LOADING"}>
          {manager.status === "LOADING" ? "Chargement…" : "Actualiser"}
        </button>
      </div>
      {!canManage ? <p className="panel-empty">Lecture et modification réservées au Patron administrateur.</p> : !companyId ? (
        <div className="empty-card"><strong>Fiche entreprise requise</strong><p>Créez la fiche entreprise avant de publier une méthode.</p></div>
      ) : !caseId ? (
        <div className="empty-card"><strong>Aucune Affaire sélectionnée</strong><p>Sélectionnez une Affaire pour consulter ou adopter un profil.</p></div>
      ) : manager.status === "UNAVAILABLE" ? (
        <div className="empty-card"><strong>Profils métier indisponibles</strong><p>La configuration actuelle de l’Affaire reste inchangée.</p></div>
      ) : (
        <div className="decision-grid">
          <article className="detail-panel">
            <div className="panel-heading"><div><h3>Version adoptée pour cette Affaire</h3><p>Une adoption ultérieure ne réécrit pas le contexte des décisions déjà figées.</p></div></div>
            {manager.adoption ? (
              <dl className="decision-facts">
                <div><dt>Version</dt><dd>v{manager.adoption.profile_version} · adoption {manager.adoption.adoption_revision}</dd></div>
                <div><dt>Identifiant</dt><dd>{manager.adoption.profile_version_id}</dd></div>
                <div><dt>SHA-256</dt><dd>{manager.adoption.profile_content_sha256}</dd></div>
              </dl>
            ) : <p className="panel-empty">Aucun profil n’est adopté. L’ancienneté des contextes existants n’est pas complétée rétroactivement.</p>}
          </article>

          <article className="detail-panel">
            <div className="panel-heading"><div><h3>Versions publiées</h3><p>Les versions sont immuables. L’adoption est un acte distinct, propre à l’Affaire.</p></div></div>
            {manager.versions.length === 0 ? <p className="panel-empty">Aucune version publiée.</p> : <>
              <label>Version à prévisualiser ou adopter
                <select value={manager.selectedVersionId} onChange={(event) => manager.setSelectedVersionId(event.target.value)}>
                  {manager.versions.map((version) => <option key={version.profile_version_id} value={version.profile_version_id}>v{version.version} · {version.content_sha256.slice(0, 12)}…</option>)}
                </select>
              </label>
              {selectedVersion && <>
                <pre className="decision-json" aria-label="Aperçu de la version publiée">{JSON.stringify(selectedVersion.profile, null, 2)}</pre>
                <button className="secondary-button" type="button" onClick={() => void submitAdoption()} disabled={manager.adopting || adoptedVersionMatchesSelection}>
                  {manager.adopting ? "Adoption…" : adoptedVersionMatchesSelection ? "Version déjà adoptée" : `Adopter v${selectedVersion.version} pour l’Affaire`}
                </button>
              </>}
            </>}
          </article>

          <form className="detail-panel decision-form" onSubmit={(event) => void submitPublish(event)} aria-label="Publier une nouvelle version de profil métier">
            <div className="panel-heading"><div><h3>Préparer une nouvelle version</h3><p>Aperçu local avant publication serveur. Les contrôles supplémentaires sont informatifs.</p></div></div>
            {TERMS.map(({ key, label }) => <label key={key}>{`Vocabulaire · ${label}`}
              <input maxLength={80} value={terminology[key] ?? ""} onChange={(event) => setTerminology((current) => ({ ...current, [key]: event.target.value }))} />
            </label>)}
            <div><strong>Contrôles de méthode informatifs</strong>
              {checks.map((item, index) => <div className="decision-form condition-form" key={`${index}-${item.key}`}>
                <label>Clé<input value={item.key} maxLength={64} onChange={(event) => setChecks((current) => current.map((check, row) => row === index ? { ...check, key: event.target.value } : check))} placeholder="site_access" /></label>
                <label>Libellé<input value={item.label} maxLength={160} onChange={(event) => setChecks((current) => current.map((check, row) => row === index ? { ...check, label: event.target.value } : check))} /></label>
                <label>Axe<select value={item.axis} onChange={(event) => setChecks((current) => current.map((check, row) => row === index ? { ...check, axis: event.target.value as BusinessMethodProfileAxis } : check))}>{AXES.map((axis) => <option key={axis} value={axis}>{axis}</option>)}</select></label>
                <button className="secondary-button" type="button" onClick={() => setChecks((current) => current.filter((_, row) => row !== index))}>Retirer</button>
              </div>)}
              <button className="secondary-button" type="button" onClick={() => setChecks((current) => current.length < 40 ? [...current, { key: "", label: "", axis: "CONTRACT" }] : current)} disabled={checks.length >= 40}>Ajouter un contrôle informatif</button>
            </div>
            <details><summary>Aperçu local du profil à publier</summary><pre className="decision-json" aria-label="Aperçu JSON local du profil">{JSON.stringify(draft, null, 2)}</pre></details>
            {formError && <p className="form-error" role="alert">{formError}</p>}
            <p className="panel-empty">Le serveur revalide le profil. Cette configuration ne change ni les permissions, ni les contrôles obligatoires, ni une décision déjà prise.</p>
            <button className="primary-button" type="submit" disabled={manager.publishing || manager.status !== "AVAILABLE"}>{manager.publishing ? "Publication…" : `Publier la version v${(manager.versions.at(-1)?.version ?? 0) + 1}`}</button>
          </form>
        </div>
      )}
    </section>
  );
}
