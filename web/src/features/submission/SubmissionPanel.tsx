import { SubmissionFinalControl } from "./SubmissionFinalControl";
import type { SubmissionFinalControl as FinalControl } from "../../shared/types";
import type { Dispatch, SetStateAction } from "react";
import { useSubmissionActions } from "./useSubmissionActions";
import type {
  SubmissionEvidenceProjection,
  SubmissionMode,
  SubmissionPackageManifestProjection,
} from "../../shared/types";

export function SubmissionWorkspace({ api, setMessage }: {
  api: Parameters<typeof useSubmissionActions>[0];
  setMessage: Parameters<typeof useSubmissionActions>[1];
}) {
  const actions = useSubmissionActions(api, setMessage);
  return <SubmissionPanel
    {...actions}
    onPrepare={() => void actions.prepareSubmissionPackage()}
    onAuthorize={() => void actions.authorizeSubmissionPackage()}
    onLoadManifest={() => void actions.loadSubmissionPackageManifest()}
    onLoadEvidence={() => void actions.loadSubmissionEvidence()}
    onRequestSignature={() => void actions.requestSignature()}
    onLoadSignature={() => void actions.loadSignature()}
    onLoadFinalControl={() => void actions.loadFinalControl()}
    onExport={() => void actions.exportSubmissionPackage()}
    onRecordEvidence={() => void actions.recordSubmissionEvidence()}
  />;
}

export type SubmissionEvidenceForm = {
  evidence_type: "MANUAL_RECEIPT" | "MANUAL_PORTAL_REFERENCE" | "HUMAN_DEPOSIT_ATTEMPT";
  external_reference_hash: string;
  evidence_sha256: string;
  notes_redacted: string;
};

type SubmissionPanelProps = {
  finalControl: FinalControl | null;
  onLoadFinalControl: () => void;
  signatureConfirmed: boolean;
  setSignatureConfirmed: Dispatch<SetStateAction<boolean>>;
  signatureRationale: string;
  setSignatureRationale: Dispatch<SetStateAction<string>>;
  signatureBusy: boolean;
  signatureIntent: { packageId: string; version: number; metadata: { expected_manifest_sha256: string } } | null;
  preparationPackageId: string;
  preparationRevision: string;
  submissionPackageId: string;
  submissionPackageVersion: string;
  submissionAuthorizationRationale: string;
  submissionMode: SubmissionMode;
  candidatureOnlyReason: string;
  submissionAuthorized: boolean;
  submissionManifest: SubmissionPackageManifestProjection | null;
  submissionEvidence: SubmissionEvidenceProjection[];
  submissionExported: boolean;
  submissionExportState: "IDLE" | "EXPORTED" | "UNKNOWN";
  signatureId: string;
  signaturePackageVersion: string;
  signatureStatus: "REQUESTED" | "SIGNED" | "REJECTED" | null;
  signatureProvider: string;
  signatureRevision: number | null;
  evidenceForm: SubmissionEvidenceForm;
  setPreparationPackageId: Dispatch<SetStateAction<string>>;
  setPreparationRevision: Dispatch<SetStateAction<string>>;
  setSubmissionPackageId: Dispatch<SetStateAction<string>>;
  setSubmissionPackageVersion: Dispatch<SetStateAction<string>>;
  setSubmissionAuthorizationRationale: Dispatch<SetStateAction<string>>;
  setSubmissionMode: Dispatch<SetStateAction<SubmissionMode>>;
  setCandidatureOnlyReason: Dispatch<SetStateAction<string>>;
  setSignatureId: Dispatch<SetStateAction<string>>;
  setSignaturePackageVersion: Dispatch<SetStateAction<string>>;
  setEvidenceForm: Dispatch<SetStateAction<SubmissionEvidenceForm>>;
  onPrepare: () => void;
  onAuthorize: () => void;
  onLoadManifest: () => void;
  onLoadEvidence: () => void;
  onRequestSignature: () => void;
  onLoadSignature: () => void;
  onExport: () => void;
  onRecordEvidence: () => void;
};

export function SubmissionPanel({
  finalControl, onLoadFinalControl, signatureConfirmed, setSignatureConfirmed,
  signatureRationale, setSignatureRationale, signatureBusy, signatureIntent,
  preparationPackageId,
  preparationRevision,
  submissionPackageId,
  submissionPackageVersion,
  submissionAuthorizationRationale,
  submissionMode,
  candidatureOnlyReason,
  submissionAuthorized,
  submissionManifest,
  submissionEvidence,
  submissionExported,
  submissionExportState,
  signatureId,
  signaturePackageVersion,
  signatureStatus,
  signatureProvider,
  signatureRevision,
  evidenceForm,
  setPreparationPackageId,
  setPreparationRevision,
  setSubmissionPackageId,
  setSubmissionPackageVersion,
  setSubmissionAuthorizationRationale,
  setSubmissionMode,
  setCandidatureOnlyReason,
  setSignatureId,
  setSignaturePackageVersion,
  setEvidenceForm,
  onPrepare,
  onAuthorize,
  onLoadManifest,
  onLoadEvidence,
  onRequestSignature,
  onLoadSignature,
  onExport,
  onRecordEvidence,
}: SubmissionPanelProps) {
  return (
    <section className="section-block submission-section" id="submission-section">
      <div className="section-heading">
        <div>
          <span className="section-kicker">PRÉPARATION &amp; DÉPÔT</span>
          <h2>Contrôler le paquet et conserver la preuve</h2>
        </div>
        <span className="secure-pill">
          <span className="status-dot" />Dépôt externe non effectué
        </span>
      </div>
      <div className="response-plan-actions">
      <button className="secondary-button" type="button" onClick={onLoadFinalControl}
        disabled={!submissionPackageId.trim() || signatureIntent !== null || signatureBusy}>
        Contrôler les pièces du paquet exact
      </button>
      </div>
      {finalControl?.submission_package_id === submissionPackageId.trim() && <SubmissionFinalControl report={finalControl} />}
      <div className="submission-grid">
        <div className="detail-panel">
          <div className="panel-heading">
            <div>
              <h3>Préparer le paquet</h3>
              <p>La préparation est une commande patronale révisée et idempotente.</p>
            </div>
          </div>
          <label>
            <span>Identifiant de préparation</span>
            <input
              value={preparationPackageId}
              onChange={(event) => setPreparationPackageId(event.target.value)}
              placeholder="UUID du package de préparation"
            />
          </label>
          <label>
            <span>Révision attendue</span>
            <input
              type="number"
              min="1"
              step="1"
              value={preparationRevision}
              onChange={(event) => setPreparationRevision(event.target.value)}
            />
          </label>
          <label>
            <span>Mode de remise</span>
            <select
              aria-label="Mode de remise"
              value={submissionMode}
              onChange={(event) => setSubmissionMode(event.target.value as SubmissionMode)}
            >
              <option value="FULL">Paquet complet</option>
              <option value="CANDIDATURE_ONLY">Candidature seule</option>
            </select>
          </label>
          {submissionMode === "CANDIDATURE_ONLY" && (
            <label>
              <span>Justification de la candidature seule</span>
              <textarea
                aria-label="Justification de la candidature seule"
                rows={2}
                maxLength={1000}
                value={candidatureOnlyReason}
                onChange={(event) => setCandidatureOnlyReason(event.target.value)}
                placeholder="Éléments financiers non disponibles ou hors périmètre"
              />
            </label>
          )}
          <button className="primary-button" type="button" onClick={onPrepare}>
            Préparer le paquet <span>→</span>
          </button>
          {submissionPackageId && (
            <>
              <button className="secondary-button" type="button" onClick={onLoadManifest}>
                Prévisualiser le manifeste <span>⌁</span>
              </button>
              {submissionManifest && (
                <div className="manifest-preview" aria-label="Prévisualisation du manifeste">
                  <strong>Manifeste exact · v{submissionManifest.package_version}</strong>
                  <span>SHA-256 : {submissionManifest.manifest_sha256}</span>
                  <span>
                    {Array.isArray(submissionManifest.manifest.entries)
                      ? `${submissionManifest.manifest.entries.length} entrée(s) partagée(s)`
                      : "Entrées non exposées"}
                    {" · "}{submissionManifest.authorization_status === "AUTHORIZED" ? "P5 autorisée" : "P5 à autoriser"}
                  </span>
                  {typeof submissionManifest.manifest.scope === "object" && submissionManifest.manifest.scope !== null && (
                    <small>Périmètre gelé : {JSON.stringify(submissionManifest.manifest.scope)}</small>
                  )}
                  {typeof submissionManifest.manifest.submission_mode === "string" && (
                    <small>Mode : {submissionManifest.manifest.submission_mode}</small>
                  )}
                  {Array.isArray(submissionManifest.manifest.entries) && submissionManifest.manifest.entries.filter((item):item is Record<string,unknown>=>typeof item==="object"&&item!==null&&(item as Record<string,unknown>).kind==="SOURCE_ANNEX").map((item,index)=><div key={index}><strong>Annexe incluse dans le paquet exact : {String(item.archive_path)}</strong><p>Document {String(item.document_id)} · SHA-256 {String(item.sha256)}</p><p>Exigences : {Array.isArray(item.requirement_ids)?item.requirement_ids.join(", "):"UNKNOWN"} · Signature : UNKNOWN</p></div>)}
                  <small>
                    Exclus : {Array.isArray(submissionManifest.manifest.exclusions)
                      ? submissionManifest.manifest.exclusions.join(", ")
                      : "stockage privé, montants et succès externe"}.
                  </small>
                </div>
              )}
              <div className="panel-heading">
                <div>
                  <h3>Autorisation P5</h3>
                  <p>Le Patron autorise la version exacte du manifeste avant toute remise.</p>
                </div>
              </div>
              <label>
                <span>Version du paquet</span>
                <input
                  type="number"
                  min="1"
                  step="1"
                  value={submissionPackageVersion}
                  onChange={(event) => setSubmissionPackageVersion(event.target.value)}
                />
              </label>
              <label>
                <span>Justification de contrôle</span>
                <textarea
                  rows={2}
                  maxLength={2000}
                  value={submissionAuthorizationRationale}
                  onChange={(event) => setSubmissionAuthorizationRationale(event.target.value)}
                />
              </label>
              <button className="primary-button" type="button" onClick={onAuthorize}>
                Autoriser la remise humaine <span>→</span>
              </button>
              {submissionAuthorized && (
                <>
                  <span className="rule-tag">P5 autorisée</span>
                  <button className="secondary-button" type="button" onClick={onExport}>
                    {submissionExportState === "UNKNOWN" ? "Vérifier l’export" : "Exporter le dossier ZIP"} <span>{submissionExportState === "UNKNOWN" ? "↻" : "↓"}</span>
                  </button>
                  {submissionExported && <span className="rule-tag">Export audité</span>}
                  {submissionExportState === "UNKNOWN" && (
                    <p className="form-status" role="status">
                      Export non confirmé : dernier état confirmé « paquet autorisé ». Vérifiez avant de relancer.
                    </p>
                  )}
                </>
              )}
              <small className="invariant-note">
                Invariant serveur : <strong>external_submission: NOT_PERFORMED</strong>.
              </small>
            </>
          )}
        </div>
        <div className="detail-panel">
          <div className="panel-heading">
            <div>
              <h3>Preuve manuelle</h3>
              <p>Le registre conserve seulement des références et des hashes redigés.</p>
            </div>
          </div>
          <label>
            <span>Identifiant du paquet</span>
            <input
              value={submissionPackageId}
              onChange={(event) => setSubmissionPackageId(event.target.value)}
              placeholder="UUID du paquet de dépôt"
            />
          </label>
          <label>
            <span>Type de preuve</span>
            <select
              value={evidenceForm.evidence_type}
              onChange={(event) =>
                setEvidenceForm({
                  ...evidenceForm,
                  evidence_type: event.target.value as SubmissionEvidenceForm["evidence_type"],
                })
              }
            >
              <option value="MANUAL_RECEIPT">Accusé manuel</option>
              <option value="MANUAL_PORTAL_REFERENCE">Référence portail manuelle</option>
              <option value="HUMAN_DEPOSIT_ATTEMPT">Tentative humaine — résultat inconnu</option>
            </select>
          </label>
          <label>
            <span>Hash de référence externe</span>
            <input
              pattern="[0-9a-f]{64}"
              required
              value={evidenceForm.external_reference_hash}
              onChange={(event) =>
                setEvidenceForm({ ...evidenceForm, external_reference_hash: event.target.value })
              }
              placeholder="64 caractères hexadécimaux"
            />
          </label>
          <label>
            <span>SHA-256 de la preuve</span>
            <input
              pattern="[0-9a-f]{64}"
              required
              value={evidenceForm.evidence_sha256}
              onChange={(event) =>
                setEvidenceForm({ ...evidenceForm, evidence_sha256: event.target.value })
              }
              placeholder="64 caractères hexadécimaux"
            />
          </label>
          <label>
            <span>Notes expurgées</span>
            <textarea
              rows={2}
              maxLength={1000}
              value={evidenceForm.notes_redacted}
              onChange={(event) =>
                setEvidenceForm({ ...evidenceForm, notes_redacted: event.target.value })
              }
              placeholder="Aucune donnée sensible"
            />
          </label>
          <button className="primary-button" type="button" onClick={onRecordEvidence}>
            Enregistrer la preuve <span>→</span>
          </button>
          <button className="secondary-button" type="button" onClick={onLoadEvidence}>
            Relire les preuves <span>↻</span>
          </button>
          {submissionEvidence.length > 0 && (
            <div className="manifest-preview" aria-label="Preuves de réception">
              {submissionEvidence.map((evidence) => (
                <div key={evidence.evidence_id}>
                  <strong>{evidence.status === "UNKNOWN" ? "Tentative inconnue" : "Réception partielle"} · v{evidence.package_version}</strong>
                  <span>{evidence.evidence_type} · SHA-256 manifeste : {evidence.manifest_sha256}</span>
                  <small>Rapprochement incomplet · external_submission: NOT_PERFORMED.</small>
                </div>
              ))}
            </div>
          )}
          <small className="invariant-note">
            Invariant serveur : <strong>external_submission: NOT_PERFORMED</strong>.
          </small>
        </div>
        <div className="detail-panel signature-panel">
          <div className="panel-heading">
            <div>
              <h3>Signature électronique</h3>
              <p>Demande humaine distincte de P5. La signature et sa validité ne sont jamais présumées.</p>
            </div>
          </div>
          <label>
            <span>Révision attendue du paquet</span>
            <input
              type="number"
              min="1"
              step="1"
              value={signaturePackageVersion}
              onChange={(event) => setSignaturePackageVersion(event.target.value)}
            />
          </label>
          <label>
            <span>Identifiant de signature</span>
            <input
              value={signatureId}
              onChange={(event) => setSignatureId(event.target.value)}
              placeholder="UUID de la signature"
            />
          </label>
          <div className="signature-status" aria-live="polite">
            <span>État</span>
            <strong>{signatureStatus ?? "NON_DEMANDÉE"}</strong>
            {signatureProvider && <small>Provider : {signatureProvider}</small>}
            {signatureRevision !== null && <small>Révision signature : {signatureRevision}</small>}
          </div>
          <label>
            <span>Motif de la demande de signature</span>
            <textarea value={signatureRationale} maxLength={2000} rows={2}
              disabled={signatureIntent !== null || signatureBusy}
              onChange={event => setSignatureRationale(event.target.value)} />
          </label>
          <label>
            <input type="checkbox" checked={signatureConfirmed}
              disabled={signatureIntent !== null || signatureBusy}
              onChange={event => setSignatureConfirmed(event.target.checked)} />
            Je confirme la demande pour le paquet exact contrôlé, sans présumer la validité de la signature.
          </label>
          {signatureIntent && <p role="status">Demande figée pour {signatureIntent.packageId} · version {signatureIntent.version} · SHA-256 {signatureIntent.metadata.expected_manifest_sha256}. Reprenez la même demande si son résultat est inconnu.</p>}
          <button className="primary-button" type="button" onClick={onRequestSignature}
            disabled={signatureBusy || (signatureIntent === null && !signatureConfirmed)}>

            {signatureBusy ? "Demande en cours" : signatureIntent ? "Reprendre la même demande" : "Demander la signature"} <span>→</span>
          </button>
          <button className="secondary-button" type="button" onClick={onLoadSignature} disabled={signatureIntent !== null || signatureBusy}>
            Recharger l’état <span>↻</span>
          </button>
          <small className="invariant-note">
            Invariant serveur : <strong>external_submission: NOT_PERFORMED</strong>.
          </small>
        </div>
      </div>
    </section>
  );
}
