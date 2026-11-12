import type {
  AssignedCase,
  ConsultationProjection,
  DceDocumentInventory,
  DceDocumentProcessingState,
  DceProvenanceChannel,
  DceVersionMetadata,
} from "../../shared/types";

const PROCESSING_STATE_LABELS: Record<DceDocumentProcessingState, string> = {
  RECEIVED: "Reçu",
  READ: "Lu",
  REVIEW_REQUIRED: "Revue humaine requise",
  UNSUPPORTED: "Format non pris en charge",
  LIMIT_REACHED: "Limite atteinte",
  PROTECTED: "Document protégé",
  UNREADABLE: "Illisible",
};

const SOURCE_CHANNEL_OPTIONS: Array<{ value: DceProvenanceChannel; label: string }> = [
  { value: "BUYER_PLATFORM", label: "Plateforme de l'acheteur" },
  { value: "EMAIL", label: "Courriel" },
  { value: "MANUAL_UPLOAD", label: "Téléversement manuel" },
  { value: "RECTIFICATION", label: "Rectification" },
];

type Props = {
  canReplace?: boolean;
  pending?: boolean;
  pendingVersionId?: string;
  pendingPredecessorId?: string;
  pendingPredecessorRevision?: number;
  pendingCorpusHash?: string;
  replacementReason?: string;
  replacementConfirmed?: boolean;
  onReplacementReasonChange?: (value: string) => void;
  onReplacementConfirmedChange?: (value: boolean) => void;
  selectedCase: AssignedCase | undefined;
  consultation: ConsultationProjection | null;
  dceVersionMetadata: DceVersionMetadata | null;
  inventory: DceDocumentInventory | null;
  loading: boolean;
  busy: boolean;
  sourceChannel: DceProvenanceChannel;
  file: File | null;
  files?: File[];
  onFilesChange?: (files: File[]) => void;
  step: "IDLE" | "PREPARING" | "UPLOADING" | "ADMITTING";
  onSourceChannelChange: (channel: DceProvenanceChannel) => void;
  onFileChange: (file: File | null) => void;
  onOpen: () => void;
  onAdmit: () => void;
};

function truncateId(value: string) {
  return value.length > 12 ? `${value.slice(0, 8)}…${value.slice(-4)}` : value;
}

function formatByteSize(byteSize: number) {
  if (byteSize < 1024) return `${byteSize} o`;
  if (byteSize < 1024 * 1024) return `${(byteSize / 1024).toFixed(1)} Ko`;
  return `${(byteSize / (1024 * 1024)).toFixed(1)} Mo`;
}

const STEP_LABELS: Record<Props["step"], string> = {
  IDLE: "",
  PREPARING: "Intention de staging…",
  UPLOADING: "Transfert du flux binaire…",
  ADMITTING: "Admission de la version DCE…",
};

export function DceOpeningPanel({
  canReplace = false, pending = false, pendingVersionId, pendingPredecessorId, pendingPredecessorRevision, pendingCorpusHash, replacementReason = "", replacementConfirmed = false,
  onReplacementReasonChange, onReplacementConfirmedChange,
  selectedCase,
  consultation,
  dceVersionMetadata,
  inventory,
  loading,
  busy,
  sourceChannel,
  file,
  files, onFilesChange,
  step,
  onSourceChannelChange,
  onFileChange,
  onOpen,
  onAdmit,
}: Props) {
  const consultationId = selectedCase?.consultation_id ?? null;
  const dceVersionId = selectedCase?.applicable_dce_version_id ?? null;
  return (
    <section className="section-block dce-opening-section" id="dce-opening-section">
      <div className="section-heading">
        <div>
          <span className="section-kicker">OUVERTURE DCE · PUX-03/PUX-04</span>
          <h2>Espace DCE</h2>
        </div>
        <button
          className="secondary-button compact-button"
          type="button"
          onClick={onOpen}
          disabled={!selectedCase || loading || pending || busy}
        >
          {loading ? "Ouverture…" : "Ouvrir / actualiser l'espace"}
        </button>
      </div>
      <p className="section-note">
        Affaire courante : {selectedCase ? selectedCase.work_label : "aucune affaire sélectionnée"}.
        Les références consultation et version DCE proviennent exclusivement du serveur.
      </p>
      {!selectedCase ? (
        <div className="empty-card">
          <strong>Sélectionnez une affaire</strong>
          <p>L'espace DCE s'ouvre depuis les références serveur de l'affaire choisie.</p>
        </div>
      ) : !consultationId ? (
        <div className="empty-card">
          <strong>Affaire sans consultation liée</strong>
          <p>
            Cette affaire n'expose aucune consultation côté serveur : la consultation et la version
            DCE applicables ne peuvent pas être déterminées. Aucune action d'admission n'est
            possible depuis ce poste.
          </p>
        </div>
      ) : (
        <div className="dce-opening-layout">
          <div className="detail-panel">
            <div className="subheading">
              <span className="section-kicker">RÉFÉRENCES SERVEUR</span>
            </div>
            <div className="dce-meta">
              <span>Consultation : {truncateId(consultationId)}</span>
              <span>
                {pending ? "Dernière version rattachée (à requalifier)" : "Version DCE applicable"} : {dceVersionId ? truncateId(dceVersionId) : "non liée"}
              </span>
            </div>
          </div>

          {loading && !consultation ? (
            <div className="empty-card">
              <strong>Ouverture de l'espace DCE</strong>
              <p>Le serveur résout la projection Consultation et l'inventaire de la version applicable.</p>
            </div>
          ) : consultation ? (
            <div className="detail-panel">
              <div className="dce-reading-heading">
                <div>
                  <span className="section-kicker">CONSULTATION</span>
                  <h3>{consultation.object_label}</h3>
                </div>
                <span className="state-badge state-monitor">{consultation.lifecycle}</span>
              </div>
              <div className="dce-meta">
                <span>Acheteur : {consultation.buyer_legal_name}</span>
                <span>Lieu : {consultation.location_label}</span>
                <span>Référence : {consultation.external_reference}</span>
                <span>Freshness : {consultation.freshness}</span>
                <span>Révision : {consultation.aggregate_revision}</span>
                <span>Lots : {consultation.lots.length > 0 ? consultation.lots.join(", ") : "—"}</span>
                <span>Tranches : {consultation.tranches.length > 0 ? consultation.tranches.join(", ") : "—"}</span>
              </div>
            </div>
          ) : (
            <div className="empty-card">
              <strong>Espace DCE non ouvert</strong>
              <p>Ouvrez l'espace pour résoudre la Consultation et la version DCE applicable depuis le serveur.</p>
            </div>
          )}

          {dceVersionMetadata && (
            <div className="detail-panel">
              <div className="subheading">
                <span className="section-kicker">VERSION DCE APPLICABLE</span>
                <span>{dceVersionMetadata.lifecycle}</span>
              </div>
              {dceVersionMetadata.lifecycle !== "ADMITTED" && <p role="status">Version historique ou retirée : aucune source de cette version ne doit être tenue pour courante.</p>}
              <div className="dce-meta">
                <span>Prédécesseur : {dceVersionMetadata.predecessor_dce_version_id ?? "aucun remplacement démontré"}</span>
                <span>Intégrité : {dceVersionMetadata.integrity}</span>
                <span>Classification : {dceVersionMetadata.classification_readiness}</span>
                <span>Analyse : {dceVersionMetadata.analysis_readiness}</span>
              </div>
            </div>
          )}

          {inventory && (
            <div className="detail-panel">
              <div className="subheading">
                <span className="section-kicker">INVENTAIRE DES DOCUMENTS</span>
                <span>{inventory.items.length} document{inventory.items.length > 1 ? "s" : ""}</span>
              </div>
              {inventory.items.length === 0 ? (
                <p className="muted-copy">Aucun document dans la version DCE applicable.</p>
              ) : (
                <div className="line-table-wrap">
                  <table>
                    <thead>
                      <tr>
                      <th>Document</th>
                      <th>Type</th>
                      <th>Taille</th>
                      <th>Source</th>
                      <th>État de traitement</th>
                      <th>Code d'exception</th>
                    </tr>
                  </thead>
                  <tbody>
                    {inventory.items.map((item) => (
                      <tr key={item.document_id}>
                        <td>{item.original_filename}</td>
                        <td>{item.media_type}</td>
                        <td>{formatByteSize(item.byte_size)}</td>
                        <td>{item.received_from}</td>
                        <td>{PROCESSING_STATE_LABELS[item.processing_state]}</td>
                        <td>{item.issue_code ?? "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          <div className="detail-panel">
            <div className="subheading">
              <span className="section-kicker">ADMISSION D'UN DOCUMENT DCE</span>
              <span>un corpus explicite par admission</span>
            </div>
            <label>
              <span>Canal source</span>
              <select
                value={sourceChannel}
                onChange={(event) => onSourceChannelChange(event.target.value as DceProvenanceChannel)}
                disabled={busy || pending}
              >
                {SOURCE_CHANNEL_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value} disabled={option.value === "RECTIFICATION" && (!canReplace || !dceVersionMetadata || dceVersionMetadata.lifecycle !== "ADMITTED")}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span>Document DCE</span>
              <input
                type="file"
                multiple
                aria-label="Document DCE"
                onChange={(event) => onFilesChange ? onFilesChange(Array.from(event.target.files ?? [])) : onFileChange(event.target.files?.[0] ?? null)}
                disabled={busy || pending}
              />
            </label>
            {sourceChannel === "RECTIFICATION" && <fieldset disabled={busy || pending}>
              <legend>Remplacement explicite</legend>
              <p>Prédécesseur : {pendingPredecessorId ?? dceVersionMetadata?.id ?? "UNKNOWN"} · révision {pendingPredecessorRevision ?? dceVersionMetadata?.aggregate_revision ?? "UNKNOWN"}. Les pièces absentes et les accords ne sont pas repris automatiquement.</p>
              <label>Motif du rectificatif<input maxLength={2000} value={replacementReason} onChange={event => onReplacementReasonChange?.(event.target.value)} /></label>
              <label><input type="checkbox" checked={replacementConfirmed} onChange={event => onReplacementConfirmedChange?.(event.target.checked)} />Je confirme le remplacement de cette version exacte et le rattachement à cette Affaire.</label>
              {!canReplace && <p>Acte de remplacement réservé au Patron administrateur.</p>}
            </fieldset>}
            {pending && <div className="dce-meta"><span>Version de l’acte : {pendingVersionId ?? "UNKNOWN"}</span><span>Prédécesseur de l’acte : {pendingPredecessorId ?? "aucun remplacement"}</span><span>SHA-256 du corpus de l’acte : {pendingCorpusHash ?? "UNKNOWN"}</span></div>}
            {pending && <p role="status">Acte en attente de résolution : fichiers, prédécesseur et identifiants conservés. Réessayez le même acte ; aucun nouvel accord n’est déduit.</p>}
            <p className="muted-copy">Limites locales : 100 fichiers, 150 Mo par fichier. Le serveur contrôle les formats, droits et limites ; aucune pièce d’une ancienne version n’est ajoutée automatiquement.</p>
            {files && files.length > 1 && <ul>{files.map((source, index) => <li key={index}>{source.name} · {formatByteSize(source.size)}</li>)}</ul>}
            {file ? <p className="muted-copy">Fichier sélectionné : {file.name}</p> : null}
            {step !== "IDLE" ? (
              <p className="muted-copy" role="status">
                {STEP_LABELS[step]}
              </p>
            ) : null}
            <div className="knowledge-actions">
              <button
                className="primary-button"
                type="button"
                onClick={onAdmit}
                disabled={busy || (!pending && (!file || !consultation || (sourceChannel === "RECTIFICATION" && (!canReplace || !replacementConfirmed || !replacementReason.trim()))))}
              >
                {busy ? "Transfert…" : pending ? "Réessayer le même acte" : "Préparer et admettre le document"}
                <span>→</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
