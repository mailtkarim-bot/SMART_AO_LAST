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
  selectedCase: AssignedCase | undefined;
  consultation: ConsultationProjection | null;
  dceVersionMetadata: DceVersionMetadata | null;
  inventory: DceDocumentInventory | null;
  loading: boolean;
  busy: boolean;
  sourceChannel: DceProvenanceChannel;
  file: File | null;
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
  selectedCase,
  consultation,
  dceVersionMetadata,
  inventory,
  loading,
  busy,
  sourceChannel,
  file,
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
          disabled={!selectedCase || loading}
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
                Version DCE applicable : {dceVersionId ? truncateId(dceVersionId) : "non liée"}
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
              <div className="dce-meta">
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
              <span>un fichier par admission</span>
            </div>
            <label>
              <span>Canal source</span>
              <select
                value={sourceChannel}
                onChange={(event) => onSourceChannelChange(event.target.value as DceProvenanceChannel)}
                disabled={busy}
              >
                {SOURCE_CHANNEL_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span>Document DCE</span>
              <input
                type="file"
                aria-label="Document DCE"
                onChange={(event) => onFileChange(event.target.files?.[0] ?? null)}
                disabled={busy}
              />
            </label>
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
                disabled={busy || !file || !consultation}
              >
                {busy ? "Transfert…" : "Préparer et admettre le document"}
                <span>→</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
