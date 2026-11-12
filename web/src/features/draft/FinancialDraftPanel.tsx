import type { Dispatch, FormEvent, SetStateAction } from "react";

import type { AssignedCase, DraftReport, FinancialCategory, PublishedFinancialReport } from "../../shared/types";
import type { FinancialLineForm, FinancialPublicationState } from "./useFinancialDraft";
import { formatBasisPoints } from "../../shared/financialFormatting";

type SummaryCard = { label: string; value: string; accent: string };

type FinancialDraftPanelProps = {
  scenarioSourceLocked?: boolean;
  cases: AssignedCase[];
  selectedCaseId: string;
  setSelectedCaseId: Dispatch<SetStateAction<string>>;
  reportId: string;
  setReportId: Dispatch<SetStateAction<string>>;
  draft: DraftReport | null;
  publishedReport: PublishedFinancialReport | null;
  publicationState: FinancialPublicationState;
  publicationRevision: number | null;
  publicationExpectedRevision: number | null;
  publicationError: string | null;
  publishedReadError: string | null;
  publicationLocked: boolean;
  publishReport: () => void;
  loadPublishedReport: () => void;
  loadingDraft: boolean;
  lineForm: FinancialLineForm;
  setLineForm: Dispatch<SetStateAction<FinancialLineForm>>;
  summaryCards: SummaryCard[];
  createDraft: () => void;
  loadDraft: () => void;
  submitLine: (event: FormEvent<HTMLFormElement>) => void;
  formatMoney: (minor: number, currency: string) => string;
  formatDate: (value: string) => string;
  categoryLabel: (category: FinancialCategory) => string;
};

export function FinancialDraftPanel({
  scenarioSourceLocked = false,
  cases,
  selectedCaseId,
  setSelectedCaseId,
  reportId,
  setReportId,
  draft,
  publishedReport, publicationState, publicationRevision, publicationExpectedRevision, publicationError, publishedReadError, publicationLocked, publishReport, loadPublishedReport,
  loadingDraft,
  lineForm,
  setLineForm,
  summaryCards,
  createDraft,
  loadDraft,
  submitLine,
  formatMoney,
  formatDate,
  categoryLabel,
}: FinancialDraftPanelProps) {
  const report = publishedReport ?? (!publicationLocked ? draft : null);
  const margin = report?.margin_calculation;
  const marginKnown = margin?.state === "CALCULATED" && Number.isSafeInteger(margin.gross_margin_minor);
  const rateKnown = marginKnown && Number.isSafeInteger(margin?.gross_margin_rate_bps);
  return (
    <section className="section-block draft-section" id="draft-section" aria-label="Rapport financier privé">
      <div className="section-heading">
        <div>
          <span className="section-kicker">CHIFFRAGE PRIVÉ</span>
          <h2>{publishedReport ? "Rapport financier publié" : "Brouillon financier"}</h2>
        </div>
        {report && (
          <span className="draft-status">
            <span className="status-dot" /> {report.status} · Révision {report.aggregate_revision}
          </span>
        )}
      </div>
      <div className="draft-toolbar">
        <label>
          <span>Affaire sélectionnée</span>
          <select disabled={scenarioSourceLocked} value={selectedCaseId} onChange={(event) => setSelectedCaseId(event.target.value)}>
            <option value="">Choisir une affaire</option>
            {cases.map((item) => (
              <option key={item.case_id} value={item.case_id}>
                {item.work_label}
              </option>
            ))}
          </select>
        </label>
        <label className="report-input">
          <span>Identifiant du rapport</span>
          <input
            value={reportId}
            onChange={(event) => setReportId(event.target.value)}
            placeholder="UUID du rapport financier"
            disabled={scenarioSourceLocked || loadingDraft || publicationState === "UNKNOWN"}
          />
        </label>
        <div className="draft-actions">
          <button className="secondary-button" onClick={createDraft} disabled={scenarioSourceLocked || loadingDraft || publicationState === "UNKNOWN"} type="button">
            + Nouveau brouillon
          </button>
          <button
            className="primary-button load-button"
            onClick={loadDraft}
            disabled={scenarioSourceLocked || loadingDraft || publicationLocked}
            type="button"
          >
            {loadingDraft ? "Chargement…" : "Lire le brouillon"}
            <span>→</span>
          </button>
          <button type="button" className="secondary-button" onClick={loadPublishedReport} disabled={scenarioSourceLocked || loadingDraft || !reportId.trim()}>
            Relire le rapport publié
          </button>
        </div>
      </div>
      {(draft || publicationState !== "IDLE" || publishedReport || publishedReadError) && (
        <section className="financial-publication" aria-label="Publication humaine du rapport financier">
          <h3>Publication humaine</h3>
          {!report && publicationExpectedRevision !== null && <p>Rapport visé : <code>{reportId} · révision attendue {publicationExpectedRevision}</code></p>}
          {report && <p>Rapport exact : <code>{report.report_id} · révision {report.aggregate_revision}</code></p>}
          {draft && !publicationLocked && <p className="financial-publication-warning">La publication fige ce brouillon. Vérifiez le rapport et sa révision avant de publier; ses lignes ne seront plus modifiables.</p>}
          {publicationState === "PUBLISHING" && <p role="status">Publication en cours… édition bloquée.</p>}
          {publicationState === "CONFIRMED" && <p role="status">Publication confirmée par le serveur · révision {publicationRevision}.</p>}
          {publicationError && <p role="alert">{publicationError}</p>}
          {publishedReadError && <p role="alert">{publishedReadError}</p>}
          {publishedReport && <p role="status">Rapport PUBLISHED relu · lecture seule. Une publication ne vaut pas éligibilité aux scénarios, couverture économique complète ou GO P3.</p>}
          {(draft && !publicationLocked || publicationState === "UNKNOWN" || publicationState === "PUBLISHING") && (
            <button type="button" className="primary-button" disabled={loadingDraft} onClick={publishReport}>
              {publicationState === "PUBLISHING" ? "Publication en cours…" : publicationState === "UNKNOWN" ? "Réessayer la même publication" : "Publier et figer ce rapport"}
            </button>
          )}
        </section>
      )}
      {report ? (
        <>
          <div className="summary-grid">
            {summaryCards.map((card) => (
              <div className={`summary-card ${card.accent}`} key={card.label}>
                <span>{card.label}</span>
                <strong>{card.label === "Marge brute" ? marginKnown && margin?.gross_margin_minor != null ? formatMoney(margin.gross_margin_minor, report.currency_code) : "UNKNOWN" : card.value}</strong>
                <small>
                  {card.label === "Marge brute"
                    ? rateKnown && margin?.gross_margin_rate_bps != null ? `${formatBasisPoints(margin.gross_margin_rate_bps)} % du chiffre d’affaires` : "Taux UNKNOWN"
                    : `Révision ${report.aggregate_revision}`}
                </small>
              </div>
            ))}
          </div>
          <p className="panel-empty">{marginKnown
            ? "Calcul sur les cinq catégories de base explicitement saisies; la couverture économique exhaustive de l’affaire reste non démontrée."
            : margin?.missing_categories.length
              ? `Marge UNKNOWN : postes de base absents (${margin.missing_categories.map(categoryLabel).join(", ")}). Un zéro doit être déclaré explicitement.`
              : "Marge UNKNOWN : aucune base de calcul vérifiée disponible."}</p>
          <div className="draft-panel">
            <div className="panel-heading">
              <div>
                <h3>{publishedReport ? "Lignes du rapport publié" : "Lignes du brouillon"}</h3>
                <p>Les montants restent visibles uniquement dans cet espace patron.</p>
              </div>
              <span className="rule-tag">Règleset v{report.ruleset_version}</span>
            </div>
            <div className="line-table-wrap">
              {publishedReport && report.lines.length === 0 ? (
                <p className="panel-empty">Aucune ligne enregistrée dans ce rapport publié.</p>
              ) : <table>
                <thead>
                  <tr>
                    <th>Catégorie</th>
                    <th>Libellé</th>
                    <th>Quantité</th>
                    <th>Unité</th>
                    <th className="amount-column">Montant</th>
                  </tr>
                </thead>
                <tbody>
                  {report.lines.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="table-empty">
                        Aucune ligne. Ajoutez le premier poste du chiffrage.
                      </td>
                    </tr>
                  ) : (
                    report.lines.map((line) => (
                      <tr key={line.line_id}>
                        <td>
                          <span className="category-badge">{categoryLabel(line.category)}</span>
                        </td>
                        <td>
                          <strong>{line.label}</strong>
                        </td>
                        <td>{line.quantity_decimal}</td>
                        <td>{line.unit}</td>
                        <td className="amount-column">
                          {Number.isSafeInteger(line.amount_minor) ? formatMoney(line.amount_minor, line.currency_code) : "UNKNOWN"}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>}
            </div>
            {draft && !publicationLocked && <form className="add-line-form" onSubmit={submitLine}>
              <div className="form-title">
                <span className="plus-mark">+</span>
                <div>
                  <strong>Ajouter une ligne</strong>
                  <small>La révision courante sera appliquée automatiquement.</small>
                </div>
              </div>
              <label>
                <span>Catégorie</span>
                <select
                  value={lineForm.category}
                  onChange={(event) =>
                    setLineForm({ ...lineForm, category: event.target.value as FinancialCategory })
                  }
                >
                  <option value="SALES">Ventes</option>
                  <option value="DIRECT_COST">Coûts directs</option>
                  <option value="OVERHEAD">Frais généraux</option>
                  <option value="SUBCONTRACTING">Sous-traitance</option>
                  <option value="CONTINGENCY">Aléas</option>
                </select>
              </label>
              <label>
                <span>Libellé</span>
                <input
                  required
                  value={lineForm.label}
                  onChange={(event) => setLineForm({ ...lineForm, label: event.target.value })}
                  placeholder="Ex. étude technique"
                />
              </label>
              <label>
                <span>Quantité</span>
                <input
                  required
                  value={lineForm.quantity_decimal}
                  onChange={(event) =>
                    setLineForm({ ...lineForm, quantity_decimal: event.target.value })
                  }
                />
              </label>
              <label>
                <span>Unité</span>
                <input
                  required
                  value={lineForm.unit}
                  onChange={(event) => setLineForm({ ...lineForm, unit: event.target.value })}
                />
              </label>
              <label>
                <span>Montant (centimes)</span>
                <input
                  required
                  type="number"
                  step="1"
                  value={lineForm.amount_minor}
                  onChange={(event) =>
                    setLineForm({ ...lineForm, amount_minor: event.target.value })
                  }
                  placeholder="125000"
                />
              </label>
              <button className="primary-button add-button" type="submit" disabled={loadingDraft}>
                Ajouter <span>→</span>
              </button>
            </form>}
            <div className="last-updated">
              Dernière lecture serveur : {formatDate(report.calculated_at)} · Aucun cache local du
              montant
            </div>
          </div>
        </>
      ) : (
        <div className="empty-draft">
          <div className="empty-icon">◫</div>
          <div>
            <strong>{publicationState === "UNKNOWN" ? "Publication à vérifier." : publicationState === "CONFIRMED" ? "Publication confirmée · source à relire." : publicationState === "REJECTED" ? "Brouillon à relire après refus." : "Sélectionnez un brouillon pour commencer."}</strong>
            <p>
              {publicationState === "IDLE" ? "La lecture est tenant-scopée et ne montre que les snapshots DRAFT autorisés par le serveur." : "Relisez la source ou rejouez uniquement l’intention indiquée pour vérifier l’état du rapport."}
            </p>
          </div>
        </div>
      )}
    </section>
  );
}
