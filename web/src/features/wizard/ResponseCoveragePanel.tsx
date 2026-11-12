import { useLayoutEffect, useRef, useState } from "react";
import type { ApiClient } from "../../infrastructure/api";
import type { ResponseCoverage, SelectedResponseDraft, SelectedResponseAnnex } from "../../shared/types";

const labels = {
  TEXT_PRESENT: "Texte présent, conformité UNKNOWN",
  TEXT_WITH_GAPS: "Texte présent avec manques déclarés",
  MISSING: "Réponse manquante",
  UNKNOWN: "Source ou confirmation UNKNOWN",
};

type Props = {
  api: Pick<ApiClient, "readResponseCoverage">;
  packageId: string;
  selection: SelectedResponseDraft;
  scopeKey: string;
  collaborator?: boolean;
  selectedAnnexes?: SelectedResponseAnnex[];
  onAnnexesChange?: (items:SelectedResponseAnnex[])=>void;
};

export function ResponseCoveragePanel({ api, packageId, selection, scopeKey, collaborator = false, selectedAnnexes=[], onAnnexesChange }: Props) {
  const key = JSON.stringify([scopeKey, packageId, selection.draft_id, selection.version, selection.content_sha256, collaborator]);
  const generation = useRef({ value: 0 });
  const [stored, setStored] = useState<{ key: string; value: ResponseCoverage } | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [lot, setLot] = useState("");
  useLayoutEffect(() => {
    const lifecycle = generation.current;
    lifecycle.value++;
    setStored(null); setError(""); setBusy(false); setLot("");
    return () => { lifecycle.value++; };
  }, [api, key]);
  const report = stored?.key === key ? stored.value : null;
  async function read() {
    const token = ++generation.current.value;
    setBusy(true); setStored(null); setError("");
    try {
      const value = await api.readResponseCoverage(packageId, selection, collaborator);
      if (generation.current.value !== token) return;
      const exact = value.selected_response;
      if (value.package_id !== packageId || exact.draft_id !== selection.draft_id
        || exact.version !== selection.version || exact.content_sha256 !== selection.content_sha256) {
        throw Error("RESPONSE_COVERAGE_CONTEXT_UNKNOWN");
      }
      setStored({ key, value });
    } catch {
      if (generation.current.value === token) setError("Lecture indisponible ou périmée · UNKNOWN. Relisez la version DCE et la pièce choisie.");
    } finally {
      if (generation.current.value === token) setBusy(false);
    }
  }
  function chooseAnnex(annex: SelectedResponseAnnex, checked:boolean) {
    const other=selectedAnnexes.filter(item=>item.document_id!==annex.document_id||item.requirement_id!==annex.requirement_id);
    onAnnexesChange?.(checked?[...other,annex].sort((a,b)=>(a.requirement_id+a.document_id).localeCompare(b.requirement_id+b.document_id)):other);
  }
  const lots = [...new Set(report?.requirements.flatMap(row => row.lot_candidates) ?? [])].sort((a, b) => a - b);
  const rows = report?.requirements.filter(row => !lot || (lot === "UNKNOWN" ? !row.lot_candidates.length : row.lot_candidates.includes(Number(lot)))) ?? [];
  return <section className="response-plan response-coverage" aria-label="Liens de la réponse choisie">
    <h4>Exigences et pièce choisie</h4>
    <p>Seule cette version est confrontée aux signaux non financiers connus du DCE. La présence d’un texte ne prouve pas la conformité ni l’exhaustivité.</p>
    <p>Pièce {selection.draft_id} · v{selection.version} · SHA-256 {selection.content_sha256}</p>
    <button type="button" className="secondary-button" disabled={busy} onClick={() => void read()}>
      {busy ? "Lecture en cours…" : "Vérifier les liens de la pièce choisie"}
    </button>
    {error && <p role="alert">{error}</p>}
    {!report && !error && <p role="status">{busy ? "Lecture en cours · UNKNOWN" : "Lecture non effectuée · UNKNOWN"}</p>}
    {report && <>
      <p>Couverture : UNKNOWN · Signature : UNKNOWN · Annexes incluses : UNKNOWN</p>
      <p>Une preuve citée dans le texte n’est pas une annexe incluse dans le ZIP. Les régions non renseignées et les pièces tierces restent à vérifier.</p>
      <p>DCE {report.dce_version_id} · {report.content_format} · {report.requirements.length} exigence(s) connue(s)</p>
      <label>Filtrer par lot candidat, applicabilité UNKNOWN
        <select value={lot} onChange={event => setLot(event.target.value)}>
          <option value="">Tous les lots connus et inconnus</option>
          {lots.map(value => <option key={value} value={String(value)}>Lot candidat {value}</option>)}
          <option value="UNKNOWN">Lot UNKNOWN</option>
        </select>
      </label>
      {!rows.length && <p>Aucune exigence connue dans ce filtre · exhaustivité UNKNOWN.</p>}
      {rows.map(row => <article key={row.requirement_id} className="review-card">
        <strong>{labels[row.response_state]}</strong>
        <p>Exigence {row.requirement_id} · {row.document_family} · {row.source_locator}</p>
        {row.source_excerpt ? <blockquote>{row.source_excerpt}</blockquote> : <p>Texte source non projeté · UNKNOWN</p>}
        <p>Lot candidat : {row.lot_candidates.join(", ") || "UNKNOWN"} · Applicabilité : UNKNOWN</p>
        <p>Source : {row.source_state} · Confirmation : {row.confirmation}</p>
        {row.pieces.map((piece, index) => <div key={`${piece.locator}/${index}`}>
          <p>{piece.section_code} · {piece.text_present ? "Texte présent" : "Texte absent"} · {piece.locator}</p>
          <p>Manques déclarés : {piece.missing || "UNKNOWN"}</p>
          <small>SHA-256 de la région : {piece.sha256}</small>
        </div>)}
        {!row.pieces.length && <p>Aucune contribution liée dans les octets de cette pièce.</p>}
        {report.cited_annexes.filter(annex => annex.requirement_id === row.requirement_id).map((annex, index) =>
          <div key={`${annex.document_id}/${index}`}><p>Annexe citée {annex.document_id} · SHA-256 {annex.sha256} · Inclusion dans le ZIP : UNKNOWN</p>
          {onAnnexesChange && <label className="capability-proposal-confirm"><input type="checkbox" aria-label={`Retenir cette annexe ${annex.document_id} pour l’exigence ${annex.requirement_id}`} checked={selectedAnnexes.some(item=>item.requirement_id===annex.requirement_id&&item.document_id===annex.document_id&&item.sha256===annex.sha256)}
            onChange={event=>chooseAnnex({requirement_id:annex.requirement_id,document_id:annex.document_id,sha256:annex.sha256},event.target.checked)}/>
            Retenir cette annexe pour le snapshot exact</label>}</div>)}
        <details><summary>Source acheteur exacte</summary><pre className="review-draft-content">{row.source_anchor ? JSON.stringify(row.source_anchor, null, 2) : "UNKNOWN"}</pre></details>
      </article>)}
    </>}
  </section>;
}
