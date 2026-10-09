import { scenarioParameterFields, type usePricingScenarios } from "./usePricingScenarios";
import type { ChangeEvent, Dispatch, SetStateAction } from "react";

import { formatBasisPoints } from "../../shared/financialFormatting";
import type { PricingImportBatchRead, PricingScenario } from "../../shared/types";
import type {
  PricingImportReloadState,
  PricingImportState,
  PricingImportUnknownAction,
} from "./usePricingImport";

type PricingPanelProps = {
  scenarioCreation: ReturnType<typeof usePricingScenarios>["creation"];
  scenarioTransition: ReturnType<typeof usePricingScenarios>["transition"];
  scenarios: PricingScenario[];
  scenariosLoading?: boolean;
  scenariosError?: string | null;
  onRefreshScenarios?: () => void;
  formatMoney: (minor: number, currency?: string) => string;
  selectedCaseId: string;
  reportId: string;
  pricingImportBatchId: string;
  pricingImportBatchRevision: string;
  pricingImportReportRevision: string;
  pricingImportState: PricingImportState;
  pricingImportUnknownAction: PricingImportUnknownAction;
  pricingImportPreview: PricingImportBatchRead | null;
  pricingImportReloadState: PricingImportReloadState;
  pricingImportUploading: boolean;
  pricingImportLoading: boolean;
  pricingImportSubmitting: boolean;
  setPricingImportBatchId: Dispatch<SetStateAction<string>>;
  setPricingImportBatchRevision: Dispatch<SetStateAction<string>>;
  setPricingImportReportRevision: Dispatch<SetStateAction<string>>;
  onPreview: (file: File) => void;
  onRetryPreview: () => void;
  onRetryCommit: () => void;
  onReload: () => void;
  onCommit: () => void;
};

export function PricingPanel({
  scenarioCreation: creation,
  scenarioTransition: transition,
  scenarios,
  scenariosLoading = false,
  scenariosError = null,
  onRefreshScenarios,
  formatMoney,
  selectedCaseId,
  reportId,
  pricingImportBatchId,
  pricingImportBatchRevision,
  pricingImportReportRevision,
  pricingImportState,
  pricingImportUnknownAction,
  pricingImportPreview,
  pricingImportReloadState,
  pricingImportUploading,
  pricingImportLoading,
  pricingImportSubmitting,
  setPricingImportBatchId,
  setPricingImportBatchRevision,
  setPricingImportReportRevision,
  onPreview,
  onRetryPreview,
  onRetryCommit,
  onReload,
  onCommit,
}: PricingPanelProps) {
  return (
    <>
      <div className="section-heading enterprise-pricing-heading">
        <div>
          <span className="section-kicker">SCÉNARIOS PRIVÉS</span>
          <h2>Options de prix</h2>
        </div>
        <span className="count-pill">
          {scenarios.length} scénario{scenarios.length > 1 ? "s" : ""}
        </span>
      </div>
      {scenariosLoading && <p role="status">Chargement des scénarios privés…</p>}
      {scenariosError && <p role="alert">{scenariosError} <button type="button" className="secondary-button" onClick={onRefreshScenarios}>Réessayer les scénarios</button></p>}
      {!scenariosLoading && !scenariosError && scenarios.length === 0 ? (
        <div className="empty-card">
          <strong>Aucun scénario chargé</strong>
          <p>Sélectionnez une affectation patronale pour consulter les scénarios privés autorisés.</p>
        </div>
      ) : (
        <div className="summary-grid">
          {scenarios.slice(0, 4).map((scenario) => {
            const qualified = scenario.source_basis_state === "DECLARED_COMPLETE" && Boolean(scenario.source_snapshot_id) && Number.isSafeInteger(scenario.source_snapshot_revision) && scenario.source_snapshot_revision >= 0 && Boolean(scenario.currency_code);
            const margin = qualified && Number.isSafeInteger(scenario.gross_margin_minor) ? formatMoney(scenario.gross_margin_minor, scenario.currency_code!) : "UNKNOWN";
            const rate = qualified ? formatBasisPoints(scenario.gross_margin_rate_bps) : "UNKNOWN";
            return (
            <div className="summary-card" role="group" aria-label={`Scénario ${scenario.scenario_key}`} key={scenario.scenario_id}>
              <span>
                {scenario.scenario_key} · v{scenario.version}
              </span>
              <strong>{margin}</strong>
              <small>
                Marge {rate === "UNKNOWN" ? rate : `${rate} %`} · {scenario.state}
              </small>
              <small>{scenario.source_snapshot_id ? `Source ${scenario.source_snapshot_id} · révision ${scenario.source_snapshot_revision}` : "Source UNKNOWN"}</small>
              <small>{qualified ? "Base déclarée complète; couverture économique globale non démontrée." : "Base source non qualifiée : UNKNOWN"}</small>
              <div className="form-actions">
                {scenario.state === "DRAFT" && <button type="button" className="secondary-button" disabled={!qualified || !Number.isSafeInteger(scenario.gross_margin_rate_bps) || creation.locked || transition.locked} onClick={() => transition.prepare(scenario.scenario_id, "selection")}>Préparer la sélection</button>}
                {scenario.state !== "ARCHIVED" && <button type="button" className="secondary-button" disabled={creation.locked || transition.locked} onClick={() => transition.prepare(scenario.scenario_id, "archive")}>Préparer l’archive</button>}
              </div>
            </div>
            );
          })}
        </div>
      )}
      {transition.target && <section className="detail-panel scenario-creation" aria-label="Acte humain sur scénario privé">
        <h3>{transition.action === "selection" ? "Sélection humaine" : "Archivage humain"}</h3>
        <p>Scénario visé : <code>{transition.target.scenario_id}</code> · version {transition.target.version} · {transition.target.state}.</p>
        <p>Source : <code>{transition.target.source_snapshot_id ?? "UNKNOWN"}</code> · révision {transition.target.source_snapshot_id && Number.isSafeInteger(transition.target.source_snapshot_revision) && transition.target.source_snapshot_revision >= 0 ? transition.target.source_snapshot_revision : "UNKNOWN"} · {transition.target.currency_code ?? "UNKNOWN"}. Base {transition.target.source_basis_state ?? "UNKNOWN"}.</p>
        <p>{transition.action === "archive" ? "L’archive est terminale; la source et les actes restent historiques." : "Cette sélection ne constitue ni un engagement ni un GO P3."} FINANCIAL_PRIVATE.</p>
        <form onSubmit={(event) => { event.preventDefault(); void transition.submit(); }}>
          <fieldset disabled={transition.locked || transition.readingBack || transition.state === "CONFIRMED"}>
            <label><span>Motif codifié</span><input required minLength={2} maxLength={64} pattern="[A-Z0-9_]{2,64}" value={transition.reason} onChange={(event) => transition.setReason(event.target.value)} aria-describedby="scenario-reason-hint" /></label>
            <p id="scenario-reason-hint">2 à 64 caractères : A–Z, 0–9 ou underscore. Saisissez votre motif explicite.</p>
          </fieldset>
          {["IDLE", "SUBMITTING", "UNKNOWN"].includes(transition.state) && <button type="submit" className="primary-button" disabled={transition.state === "SUBMITTING"}>{transition.state === "UNKNOWN" ? "Réessayer le même acte" : transition.state === "SUBMITTING" ? "Acte en cours…" : transition.action === "selection" ? "Confirmer la sélection" : "Confirmer l’archive"}</button>}
        </form>
        {transition.state === "UNKNOWN" && <p role="status">UNKNOWN · intention figée. Le retry garde la version, le motif et les identifiants exacts.</p>}
        {transition.error && <p role="alert">{transition.error}</p>}
        {["CONFLICT", "REJECTED"].includes(transition.state) && <button type="button" className="secondary-button" disabled={transition.readingBack} onClick={() => void transition.reload()}>Relire avant une nouvelle intention</button>}
        {transition.receipt && <p role="status">Reçu technique : <code>{transition.receipt.scenario_id}</code> · version {transition.receipt.version}. La projection GET est une preuve distincte.</p>}
        {transition.receipt && !transition.projection && <button type="button" className="secondary-button" disabled={transition.readingBack} onClick={() => void transition.readBack()}>Relire l’acte confirmé</button>}
        {transition.projection && <p>Scénario relu : <code>{transition.projection.scenario_id}</code> · version {transition.projection.version} · {transition.projection.state}. Base {transition.projection.source_basis_state ?? "UNKNOWN"}; aucun effet P3.</p>}
      </section>}
      {!transition.target && transition.error && <p role="status">{transition.error}</p>}
      <section className="detail-panel scenario-creation" aria-label="Création humaine de scénario privé">
        <h3>Créer un scénario</h3>
        <p>FINANCIAL_PRIVATE · saisie humaine. Aucun engagement, sélection automatique ou effet P3.</p>
        {creation.source && <p>Source PUBLISHED relue : <code>{creation.source.report_id}</code> · révision {creation.source.aggregate_revision} · {creation.source.currency_code}</p>}
        {creation.sourceReason && <p role="status">{creation.sourceReason}</p>}
        <form onSubmit={(event) => { event.preventDefault(); void creation.submit(); }}>
          <fieldset disabled={Boolean(creation.sourceReason) || creation.locked || creation.state === "CONFIRMED"}>
            <legend>Paramètres et hypothèses explicites</legend>
            <div className="scenario-form-grid">
              <label><span>Nom du scénario</span><input required maxLength={120} value={creation.form.scenario_key} onChange={(event) => creation.setForm({ ...creation.form, scenario_key: event.target.value })} /></label>
              <label><span>Type de scénario</span><select value={creation.form.scenario_type} onChange={(event) => creation.setForm({ ...creation.form, scenario_type: event.target.value as typeof creation.form.scenario_type })}><option value="BASE">BASE</option><option value="PRUDENT">PRUDENT</option><option value="CUSTOM">CUSTOM</option></select></label>
              {scenarioParameterFields.map((field) => <label key={field.key}><span>{field.label}</span><input type="number" required step="1" min={field.min} max={field.max} value={creation.form[field.key]} onChange={(event) => creation.setForm({ ...creation.form, [field.key]: event.target.value })} /></label>)}
            </div>
            <label><span>Hypothèses du Patron</span><textarea required maxLength={2000} value={creation.form.assumptions} onChange={(event) => creation.setForm({ ...creation.form, assumptions: event.target.value })} /></label>
          </fieldset>
          <p>100 points de base = 1 %. Réserves en unités mineures de la devise source; zéro est une valeur déclarée. Le type ne remplit aucune hypothèse.</p>
          {creation.state !== "CONFIRMED" && <button type="submit" className="primary-button" disabled={Boolean(creation.sourceReason) || creation.state === "SUBMITTING" || transition.locked}>{creation.state === "UNKNOWN" ? "Réessayer la même création" : creation.state === "SUBMITTING" ? "Création en cours…" : "Créer ce scénario"}</button>}
        </form>
        {creation.state === "UNKNOWN" && <p role="status">UNKNOWN · résultat serveur inconnu. Paramètres et identité de commande conservés pour le retry.</p>}
        {creation.error && <p role="alert">{creation.error}</p>}
        {creation.receipt && <p role="status">Reçu serveur : <code>{creation.receipt.scenario_id}</code> · version {creation.receipt.version}. La relecture reste distincte.</p>}
        {creation.receipt && !creation.scenario && <button type="button" className="secondary-button" disabled={creation.readingBack} onClick={() => void creation.readBack()}>{creation.readingBack ? "Relecture…" : "Relire le scénario créé"}</button>}
        {creation.scenario && <><p>Scénario relu : <code>{creation.scenario.scenario_id}</code> · version {creation.scenario.version} · {creation.scenario.state}. Source <code>{creation.scenario.source_snapshot_id}</code> · révision {creation.scenario.source_snapshot_revision}.</p><p>Hypothèses enregistrées : {String(creation.scenario.assumptions.note)}</p><button type="button" className="secondary-button" disabled={transition.locked} onClick={creation.reset}>Préparer un autre scénario</button></>}
      </section>
      <div className="detail-panel import-commit-panel">
        <div className="panel-heading">
          <div>
            <h3>Importer dans le brouillon</h3>
            <p>Seules les lignes validées du batch DPGF/BPU/Excel sont appliquées, côté patron.</p>
          </div>
          <span className={`state-badge state-${pricingImportState.toLowerCase()}`}>
            {pricingImportState === "IDLE"
              ? "PRÊT"
              : pricingImportState === "UNKNOWN"
                ? "À VÉRIFIER"
                : pricingImportState}
          </span>
        </div>
        <div className="import-commit-grid">
          <label>
            <span>Fichier DPGF/BPU/Excel</span>
            <input
              type="file"
              accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
              disabled={pricingImportUploading || !selectedCaseId}
              onChange={(event: ChangeEvent<HTMLInputElement>) => {
                const file = event.target.files?.[0];
                if (file) onPreview(file);
                event.target.value = "";
              }}
            />
          </label>
          <button
            className="secondary-button"
            type="button"
            onClick={onReload}
            disabled={pricingImportLoading || !selectedCaseId || !pricingImportBatchId.trim()}
          >
            {pricingImportLoading ? "Lecture…" : "Relire le batch"}
          </button>
          <label>
            <span>Batch d’import validé</span>
            <input
              value={pricingImportBatchId}
              onChange={(event) => setPricingImportBatchId(event.target.value)}
              placeholder="UUID du batch PREVIEWED"
            />
          </label>
          <label>
            <span>Révision du batch</span>
            <input
              type="number"
              min="1"
              step="1"
              value={pricingImportBatchRevision}
              onChange={(event) => setPricingImportBatchRevision(event.target.value)}
            />
          </label>
          <label>
            <span>Révision du brouillon</span>
            <input
              type="number"
              min="0"
              step="1"
              value={pricingImportReportRevision}
              onChange={(event) => setPricingImportReportRevision(event.target.value)}
            />
          </label>
          <button
            className="primary-button"
            type="button"
            onClick={onCommit}
            disabled={
              pricingImportSubmitting ||
              !selectedCaseId ||
              !reportId.trim() ||
              !pricingImportBatchId.trim()
            }
          >
            {pricingImportSubmitting ? "Commit en cours…" : "Commiter les lignes validées"} <span>→</span>
          </button>
        </div>
        {pricingImportPreview && (
          <div className="import-preview-summary">
            <strong>
              {pricingImportPreview.document_kind} · {pricingImportPreview.state} ·{" "}
              {pricingImportPreview.row_count} ligne{pricingImportPreview.row_count > 1 ? "s" : ""}
            </strong>
            <span>
              {pricingImportPreview.valid_row_count} valide
              {pricingImportPreview.valid_row_count > 1 ? "s" : ""}
              {pricingImportPreview.error_count > 0
                ? ` · ${pricingImportPreview.error_count} erreur${pricingImportPreview.error_count > 1 ? "s" : ""}`
                : ""}
            </span>
            {pricingImportPreview.rows.slice(0, 5).map((row) => (
              <div className="import-preview-row" key={row.row_number}>
                <span>
                  #{row.row_number} · {row.designation ?? "Ligne sans désignation"}
                </span>
                <span>{row.errors.length ? row.errors.join(", ") : "Valide"}</span>
              </div>
            ))}
          </div>
        )}
        <small className="invariant-note">
          Le serveur verrouille le batch et le brouillon, refuse les erreurs, applique l’idempotence
          et ne retourne aucun montant dans ce receipt.
        </small>
        {pricingImportUnknownAction && (
          <div className="form-actions">
            <button
              className="secondary-button"
              type="button"
              onClick={pricingImportUnknownAction === "PREVIEW" ? onRetryPreview : onRetryCommit}
              disabled={pricingImportUploading || pricingImportSubmitting}
            >
              {pricingImportUnknownAction === "PREVIEW" ? "Rejouer la preview" : "Rejouer le commit"}
            </button>
            <small className="invariant-note warning">
              Résultat inconnu : aucun succès n’est présumé et le rejeu conserve les mêmes identifiants.
            </small>
          </div>
        )}
        {pricingImportReloadState === "FAILED" && (
          <small className="invariant-note warning">
            Commit confirmé. Rechargez le brouillon pour resynchroniser l’affichage.
          </small>
        )}
      </div>
    </>
  );
}
