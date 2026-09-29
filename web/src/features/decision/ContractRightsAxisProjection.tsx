import type { ContractExecutionActKind, ContractExecutionEvidence, PostReceptionObligation } from "../../shared/types";
import type { ContractExecutionEvidenceReadStatus } from "../pricing/useContractExecutionEvidence";

const RECEPTION_TYPES: PostReceptionObligation["obligation_type"][] = [
  "OPR", "TESTS", "COMMISSIONING", "TRAINING", "DOE_DIUO", "RESERVES_LIFTING",
];
const CONTRACT_EXIT_TYPES: PostReceptionObligation["obligation_type"][] = ["ADMIN_CLOSURE", "GUARANTEE_RELEASE"];
const ACT_LABELS: Record<ContractExecutionActKind, string> = {
  WORK_RECEPTION: "Réception d’ouvrage",
  RIGHTS_PRESERVATION: "Préservation des droits",
  CONTRACT_EXIT: "Sortie contractuelle",
};
const INSTRUMENT_LABELS = { SIGNED_CONTRACT: "Contrat signé", AMENDMENT: "Avenant" } as const;

function ActItems({
  acts,
  status,
}: {
  acts: ContractExecutionEvidence[];
  status: ContractExecutionEvidenceReadStatus;
}) {
  if (status === "LOADING") return <p role="status">Chargement des actes et preuves…</p>;
  if (status === "UNAVAILABLE") return <p>UNAVAILABLE · impossible de lire les actes ; leur absence ne peut pas être établie.</p>;
  if (acts.length === 0) return <p>UNKNOWN · aucun acte enregistré ; cela ne prouve pas son absence.</p>;
  return <ul>{acts.map((act) => <li key={`${act.case_id}:${act.act_id}`}>
    <strong>{act.summary}</strong>
    <span>Acte déclaré par le Patron · portée juridique non évaluée</span>
    <span>Date d’acte déclarée : {act.declared_event_date ?? "UNKNOWN"} · enregistré par {act.actor_id} le {act.recorded_at}</span>
    {act.act_kind === "WORK_RECEPTION" && <span>Réception déclarée : {act.reception_outcome === "UNKNOWN"
      ? "UNKNOWN · acte historique non qualifié"
      : act.reception_outcome === "WITH_RESERVATIONS" ? "avec réserves"
        : act.reception_outcome === "UNDER_RESERVATIONS" ? "sous réserves" : "sans réserves"}</span>}
    <span>Version DCE associée à l’Affaire lors de l’acte : {act.case_dce_version_id_at_recording ?? "UNKNOWN"}</span>
    {act.version_relation === "MATCHES_CASE_CURRENT" && <span>Le lien DCE correspond encore à celui de l’Affaire ; cela ne confirme pas l’applicabilité contractuelle.</span>}
    {act.version_relation === "REVIEW_REQUIRED" && <span>REVIEW_REQUIRED · version DCE remplacée ou lien modifié ; requalification humaine requise.</span>}
    {act.version_relation === "UNKNOWN" && <span>UNKNOWN · aucune version DCE n’était explicitement liée lors de l’acte.</span>}
    {act.contract_instrument_version_relation === "REVIEW_REQUIRED" && <span>REVIEW_REQUIRED · le Patron a déclaré cette version remplacée ; requalification humaine requise, sans conclusion sur l’applicabilité.</span>}
    {act.contract_instrument_version_relation === "UNKNOWN" && <span>UNKNOWN · version contractuelle non reliée ou non établie.</span>}
    <span>Version signée/avenant sourcée : {act.contract_instrument_version
      ? `${INSTRUMENT_LABELS[act.contract_instrument_version.instrument_kind]} · ${act.contract_instrument_version.version_reference} (déclaration Patron, non vérifiée)`
      : "UNKNOWN · aucune version enregistrée ou liée"}</span>
    {act.contract_instrument_version && <>
      <span>Sources de cette version : {act.contract_instrument_version.source_refs.join(" · ")}</span>
      <span>Pièces de cette version : {act.contract_instrument_version.evidence_refs.join(" · ")}</span>
    </>}
    <span>Sources : {act.source_refs.join(" · ")}</span>
    <span>Preuves : {act.evidence_refs.join(" · ")}</span>
  </li>)}</ul>;
}

function ObligationItems({ obligations, loading }: { obligations: PostReceptionObligation[]; loading: boolean }) {
  if (loading) return <p role="status">Chargement des obligations…</p>;
  if (obligations.length === 0) return <p>UNKNOWN · aucune source de cette catégorie n’est enregistrée ; cela ne prouve pas son absence.</p>;
  return <ul>{obligations.map((item) => <li key={`${item.case_id}:${item.obligation_id}`}>
    <strong>{item.obligation_type} · {item.summary}</strong>
    <span>État : {item.status} · date renseignée : {item.due_date ? `${item.due_date} (déclarée, non recalculée)` : "UNKNOWN"}</span>
    <span>Sources : {item.source_refs.join(" · ")}</span>
    {item.obligation_type === "RESERVES_LIFTING" && <span>Acte de réception source : {item.origin_reception_act_id
      ? `${item.origin_reception_summary ?? item.origin_reception_act_id} · ${item.origin_reception_outcome}`
      : "UNKNOWN · obligation non reliée"}</span>}
  </li>)}</ul>;
}

export function ContractRightsAxisProjection({
  obligations,
  obligationsLoading = false,
  acts,
  actsStatus,
}: {
  obligations: PostReceptionObligation[];
  obligationsLoading?: boolean;
  acts: ContractExecutionEvidence[];
  actsStatus: ContractExecutionEvidenceReadStatus;
}) {
  return <section className="detail-panel" aria-label="Carte d’Engagement axe 12 préservation des droits, réception et sortie contractuelle">
    <div className="panel-heading"><div><h3>Carte d’Engagement · Axe 12</h3><p>Préservation des droits, réception et sortie contractuelle</p></div><span className="state-badge">PARTIAL</span></div>
    <p>Les actes sont des déclarations humaines sourcées ; les pièces référencées ne sont pas ouvertes ni validées et leur portée juridique n’est pas qualifiée. Aucun délai, DGD tacite ou forclusion n’est calculé ni conclu.</p>
    {(Object.keys(ACT_LABELS) as ContractExecutionActKind[]).map((kind) => <div key={kind}>
      <h4>{ACT_LABELS[kind]}</h4>
      <ActItems acts={acts.filter((act) => act.act_kind === kind)} status={actsStatus} />
      {kind === "WORK_RECEPTION" && <>
        <h5>Obligations associées à la réception · elles ne prouvent pas sa tenue</h5>
        <ObligationItems obligations={obligations.filter((item) => RECEPTION_TYPES.includes(item.obligation_type))} loading={obligationsLoading} />
      </>}
      {kind === "CONTRACT_EXIT" && <>
        <h5>Tâches de clôture · elles ne valent pas sortie contractuelle acquise</h5>
        <ObligationItems obligations={obligations.filter((item) => CONTRACT_EXIT_TYPES.includes(item.obligation_type))} loading={obligationsLoading} />
      </>}
    </div>)}
  </section>;
}
