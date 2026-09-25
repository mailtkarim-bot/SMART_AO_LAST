import type { ExportProofVerification } from "../../shared/types";

export function ExportProofVerificationPanel({ verification }: { verification: ExportProofVerification | null }) {
  if (!verification) return <div className="empty-card"><strong>Aucune vérification locale</strong><p>Le fichier exporté n’a pas encore été vérifié.</p></div>;
  return <article className="detail-panel" aria-label="Vérification locale export"><div className="panel-heading"><h3>Intégrité locale</h3><span className="state-badge">{verification.status}</span></div>{verification.calculated_sha256 && <p>SHA-256 calculé : <code>{verification.calculated_sha256}</code></p>}<p className="panel-empty">Lecture seule : cette vérification ne prouve aucune réception externe.</p></article>;
}
