import { useState, type FormEvent } from "react";
import type { HandoverContractOption, HandoverConditionOption, HandoverOperationalPoint, HandoverOperationalReview } from "../../shared/types";
const kinds = [['ENGAGEMENT', 'Engagement'], ['EXCLUSION', 'Exclusion'], ['CONDITION', 'Condition du GO'], ['INTERFACE', 'Interface'], ['PARTNER', 'Partenaire'], ['PLANNING', 'Planning'], ['GUARANTEE', 'Garantie'], ['PENALTY', 'Sanction déclarée'], ['PAYMENT', 'Circuit de paiement'], ['HSE', 'HSE'], ['POST_AWARD_DOCUMENT', 'Document à obtenir'], ['RESIDUAL_RISK', 'Risque résiduel'], ['RIGHT_PRESERVATION', 'Préservation des droits']];
const emptyPoint = (): HandoverOperationalPoint => ({
  point_id: crypto.randomUUID(),
  kind: 'ENGAGEMENT',
  statement: '',
  offer_excerpt: null,
  offer_locator: null,
  contract_locator: null,
  difference_state: 'UNKNOWN',
  difference_note: null,
  responsible: null,
  action: null,
  expected_evidence: null,
  due_date: null,
  criticality: 'UNKNOWN',
  condition_id: null
});
export function HandoverReviewForm({
  contracts,
  conditions,
  expectedRevision,
  offerSha,
  sourceContextSha,
  disabled,
  onSubmit
}: {
  contracts: HandoverContractOption[];
  conditions: HandoverConditionOption[];
  expectedRevision: number;
  offerSha: string;
  sourceContextSha: string;
  disabled: boolean;
  onSubmit: (review: HandoverOperationalReview) => void;
}) {
  const [contractId, setContractId] = useState('');
  const [why, setWhy] = useState('');
  const [confirmed, setConfirmed] = useState(false);
  const [points, setPoints] = useState<HandoverOperationalPoint[]>(() => [emptyPoint()]);
  const contract = contracts.find(c => c.instrument_version_id === contractId);
  function change(index: number, patch: Partial<HandoverOperationalPoint>) {
    setConfirmed(false);
    setPoints(current => current.map((p, i) => i === index ? {
      ...p,
      ...patch
    } : p));
  }
  const ready = why.trim() && confirmed && points.every(p => p.statement.trim() && (p.difference_state === 'UNKNOWN' || contract && p.offer_locator && p.contract_locator) && (p.difference_state !== 'DECLARED_DIFFERENCE' || p.difference_note));
  function submit(event: FormEvent) {
    event.preventDefault();
    if (!ready || disabled) return;
    onSubmit({
      expected_source_context_sha256: sourceContextSha,
      expected_handover_revision: expectedRevision,
      expected_offer_manifest_sha256: offerSha,
      contract_instrument_version_id: contract?.instrument_version_id ?? null,
      expected_contract_record_sha256: contract?.record_sha256 ?? null,
      justification: why.trim(),
      human_confirmed: true,
      points: structuredClone(points)
    });
  }
  return <form className="workflow-form" onSubmit={submit}>
 <h3>Rapprochement opérationnel de l’offre et du contrat</h3><p>Publiez uniquement ce que le Conducteur peut lire. Aucune marge ou hypothèse économique privée. Les références de contrat sont déclarées; leur sélection ne prouve pas une signature ni un effet juridique.</p>
 <fieldset disabled={disabled}><legend>Sources de la revue</legend><p>Contexte Affaire/décision exact : {sourceContextSha}</p>
 <label>Version contractuelle déclarée<select value={contractId} onChange={e => {
          setContractId(e.target.value);
          setConfirmed(false);
          setPoints(current => current.map(p => ({
            ...p,
            difference_state: 'UNKNOWN'
          })));
        }}><option value="">Version non reliée · UNKNOWN</option>{contracts.map(c => <option key={c.instrument_version_id} value={c.instrument_version_id} disabled={c.state === 'SUPERSEDED'}>{c.version_reference} · {c.instrument_kind} · {c.state}</option>)}</select></label>
 <p>Empreinte de l’enregistrement contractuel : {contract?.record_sha256 ?? 'UNKNOWN'}. SHA du fichier signé et autorité juridique : UNKNOWN.</p>
 {points.map((point, index) => <fieldset key={point.point_id}><legend>Point opérationnel {index + 1}</legend>
 <label>Nature du point {index + 1}<select value={point.kind} onChange={e => change(index, {
            kind: e.target.value,
            condition_id: null
          })}>{kinds.map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></label>
 <label>Point opérationnel {index + 1}<textarea required maxLength={2000} rows={3} value={point.statement} onChange={e => change(index, {
            statement: e.target.value
          })} /></label>
 {point.kind === 'CONDITION' && <label>Condition privée à reformuler pour le Conducteur {index + 1}<select value={point.condition_id ?? ''} onChange={e => change(index, {
            condition_id: e.target.value || null
          })}><option value="">Condition non reliée · UNKNOWN</option>{conditions.map(c => <option key={c.condition_id} value={c.condition_id}>{c.private_label} · {c.status}</option>)}</select></label>}
 <label>Extrait exact de l’offre {index + 1}<textarea rows={2} maxLength={4000} value={point.offer_excerpt ?? ''} onChange={e => change(index, {
            offer_excerpt: e.target.value || null
          })} /></label>
 <label>Localisation dans l’offre {index + 1}<input maxLength={500} value={point.offer_locator ?? ''} onChange={e => change(index, {
            offer_locator: e.target.value || null
          })} /></label>
 <label>Localisation dans le contrat déclaré {index + 1}<input maxLength={500} value={point.contract_locator ?? ''} onChange={e => change(index, {
            contract_locator: e.target.value || null
          })} /></label>
 <label>Écart déclaré {index + 1}<select value={point.difference_state} onChange={e => change(index, {
            difference_state: e.target.value as HandoverOperationalPoint['difference_state']
          })}><option value="UNKNOWN">Non évalué · UNKNOWN</option><option value="DECLARED_EQUIVALENT" disabled={!contract}>Équivalence déclarée</option><option value="DECLARED_DIFFERENCE" disabled={!contract}>Écart déclaré</option></select></label>
 <label>Explication de l’écart {index + 1}<textarea rows={2} maxLength={2000} value={point.difference_note ?? ''} onChange={e => change(index, {
            difference_note: e.target.value || null
          })} /></label>
 <label>Responsable déclaré {index + 1}<input maxLength={300} value={point.responsible ?? ''} onChange={e => change(index, {
            responsible: e.target.value || null
          })} /></label>
 <label>Action à mener {index + 1}<textarea rows={2} maxLength={2000} value={point.action ?? ''} onChange={e => change(index, {
            action: e.target.value || null
          })} /></label>
 <label>Preuve attendue {index + 1}<input maxLength={2000} value={point.expected_evidence ?? ''} onChange={e => change(index, {
            expected_evidence: e.target.value || null
          })} /></label>
 <label>Date déclarée {index + 1}<input type="date" value={point.due_date ?? ''} onChange={e => change(index, {
            due_date: e.target.value || null
          })} /></label>
 <label>Criticité {index + 1}<select value={point.criticality} onChange={e => change(index, {
            criticality: e.target.value as HandoverOperationalPoint['criticality']
          })}><option value="UNKNOWN">UNKNOWN</option><option value="IMPORTANT">Important</option><option value="CRITICAL">Critique</option></select></label>
 <button className="secondary-button" type="button" disabled={points.length === 1} onClick={() => {
          setPoints(current => current.filter((_, i) => i !== index));
          setConfirmed(false);
        }}>Retirer ce point</button>
 </fieldset>)}
 <button className="secondary-button" type="button" disabled={points.length >= 64} onClick={() => {
        setPoints(current => [...current, emptyPoint()]);
        setConfirmed(false);
      }}>Ajouter un point opérationnel</button>
 <label>Justification de la revue<textarea required maxLength={2000} value={why} onChange={e => {
          setWhy(e.target.value);
          setConfirmed(false);
        }} /></label>
 <label><input type="checkbox" checked={confirmed} onChange={e => setConfirmed(e.target.checked)} />Je confirme la publication opérationnelle de ces éléments et de leurs inconnus au Conducteur.</label>
 </fieldset><button className="primary-button" type="submit" disabled={disabled || !ready}>Publier la revue et transmettre</button>
 <p>Une ligne critique sans source, responsable, action ou preuve reste PARTIAL. La réception du dossier ne vaudra ni complétude ni ordre de service.</p>
 </form>;
}
