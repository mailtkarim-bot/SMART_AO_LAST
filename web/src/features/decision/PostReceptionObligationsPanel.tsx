import type { FormEvent } from "react";
import { useEffect, useState } from "react";
import type { ContractExecutionEvidence, PostReceptionObligation } from "../../shared/types";

const OBLIGATION_TYPES: PostReceptionObligation["obligation_type"][] = [
  "OPR", "TESTS", "COMMISSIONING", "TRAINING", "DOE_DIUO", "RESERVES_LIFTING",
  "GPA", "INITIAL_MAINTENANCE", "SPARE_STOCK", "ON_CALL", "ADMIN_CLOSURE", "GUARANTEE_RELEASE",
];

type Draft = {
  obligation_type: PostReceptionObligation["obligation_type"];
  summary: string;
  source_ref: string;
  origin_reception_act_id: string;
  due_date: string;
  resource_note: string;
  cost_estimate_note: string;
  proof_ref: string;
  sanction_ref: string;
};

const EMPTY_DRAFT: Draft = {
  obligation_type: "DOE_DIUO", summary: "", source_ref: "", origin_reception_act_id: "", due_date: "",
  resource_note: "", cost_estimate_note: "", proof_ref: "", sanction_ref: "",
};

type TransitionAttempt = {
  command_id: string;
  idempotency_key: string;
  transition_id: string;
  expected_revision: number;
  resulting_status: "IN_PROGRESS" | "FOLLOW_UP_REQUIRED" | "UNKNOWN" | "COMPLETED";
  rationale: string;
  evidence_refs: string[];
};

function ObligationCard({
  obligation,
  onTransition,
}: {
  obligation: PostReceptionObligation;
  onTransition?: (obligationId: string, input: Record<string, unknown>) => Promise<void>;
}) {
  const [rationale, setRationale] = useState("Revue Patron de l’obligation");
  const [proofRef, setProofRef] = useState("");
  const [pending, setPending] = useState<TransitionAttempt | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(false);
  const [proofRequired, setProofRequired] = useState(false);

  useEffect(() => {
    if (pending && obligation.revision > pending.expected_revision) {
      setPending(null);
      setError(false);
      setProofRef("");
    }
  }, [obligation.revision, pending]);

  const availableTransitions: TransitionAttempt["resulting_status"][] = obligation.status === "COMPLETED"
    ? []
    : obligation.status === "REVIEW_REQUIRED"
      ? ["IN_PROGRESS", "FOLLOW_UP_REQUIRED", "UNKNOWN", "COMPLETED"]
      : obligation.status === "IN_PROGRESS"
        ? ["FOLLOW_UP_REQUIRED", "UNKNOWN", "COMPLETED"]
        : ["IN_PROGRESS", "FOLLOW_UP_REQUIRED", "UNKNOWN", "COMPLETED"];

  async function transition(resultingStatus: TransitionAttempt["resulting_status"]) {
    if (!onTransition || submitting) return;
    if (pending && pending.resulting_status !== resultingStatus) return;
    if (!pending && resultingStatus === "COMPLETED" && !proofRef.trim()) {
      setProofRequired(true);
      return;
    }
    const attempt = pending ?? {
      command_id: crypto.randomUUID(),
      idempotency_key: crypto.randomUUID(),
      transition_id: crypto.randomUUID(),
      expected_revision: obligation.revision,
      resulting_status: resultingStatus,
      rationale,
      evidence_refs: resultingStatus === "COMPLETED" ? [proofRef.trim()] : [],
    };
    setPending(attempt);
    setSubmitting(true);
    setError(false);
    try {
      await onTransition(obligation.obligation_id, attempt);
    } catch {
      setError(true);
    } finally {
      setSubmitting(false);
    }
  }

  return <article className="detail-panel" key={`${obligation.case_id}:${obligation.obligation_id}`}>
    <div className="panel-heading"><h3>{obligation.obligation_type} · {obligation.summary}</h3><span className="state-badge">{obligation.status}</span></div>
    <p>Sources : {obligation.source_refs.join(" · ")}</p>
    {obligation.obligation_type === "RESERVES_LIFTING" && <p>Acte de réception source : {obligation.origin_reception_act_id
      ? `${obligation.origin_reception_summary ?? "Acte relié"} · ${obligation.origin_reception_outcome}`
      : "UNKNOWN · obligation historique non reliée à un acte de réception"}</p>}
    <p>Échéance : {obligation.due_date ?? "Non renseignée"}</p>
    <p>Ressource : {obligation.resource_note ?? "Non renseignée"}</p>
    <p>Coût estimatif : {obligation.cost_estimate_note ?? "Non renseigné"}</p>
    <p>Preuves disponibles à l’enregistrement : {obligation.fulfillment_proof_refs.join(" · ") || "Aucune"}</p>
    <p>Sanction liée : {obligation.sanction_ref ?? "Non renseignée"}</p>
    {obligation.latest_transition_rationale && <p>Dernière décision Patron : {obligation.latest_transition_rationale}</p>}
    {obligation.status !== "COMPLETED" && onTransition && <div aria-label={`Actions Patron ${obligation.summary}`}>
      <label>Motif de la décision<input aria-label={`Motif ${obligation.summary}`} required value={rationale} disabled={!!pending || submitting} onChange={(event) => setRationale(event.target.value)} /></label>
      <label>Preuve de levée<input aria-label={`Preuve de levée ${obligation.summary}`} value={proofRef} disabled={!!pending || submitting} onChange={(event) => { setProofRef(event.target.value); setProofRequired(false); }} /></label>
      {proofRequired && <p role="alert">Une référence de preuve est obligatoire pour déclarer l’obligation terminée.</p>}
      {availableTransitions.map((target) => <button key={target} type="button" disabled={submitting || (!!pending && pending.resulting_status !== target)} onClick={() => void transition(target)}>
        {error && pending?.resulting_status === target ? "Réessayer" : target === "IN_PROGRESS" ? "Passer en cours" : target === "FOLLOW_UP_REQUIRED" ? "Exiger un suivi" : target === "UNKNOWN" ? "Marquer inconnu" : "Marquer terminée"}
      </button>)}
      {error && <p role="alert">Transition non confirmée · état serveur à relire. Le rejeu conserve les mêmes identifiants.</p>}
    </div>}
    {obligation.status === "COMPLETED" && <p className="panel-empty">Terminé après une décision Patron et une preuve référencée ; aucun achèvement automatique.</p>}
  </article>;
}

export function PostReceptionObligationsPanel({
  obligations,
  caseId,
  receptionActs = [],
  onCreate,
  onTransition,
}: {
  obligations: PostReceptionObligation[];
  caseId: string;
  receptionActs?: ContractExecutionEvidence[];
  onCreate?: (input: Record<string, unknown>) => Promise<void>;
  onTransition?: (obligationId: string, input: Record<string, unknown>) => Promise<void>;
}) {
  const [draft, setDraft] = useState(EMPTY_DRAFT);
  const [pending, setPending] = useState<{ ids: { command_id: string; idempotency_key: string; obligation_id: string }; payload: Draft } | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<false | "VALIDATION" | "UNCONFIRMED">(false);
  const eligibleReceptionActs = receptionActs.filter((act) =>
    act.act_kind === "WORK_RECEPTION"
    && (act.reception_outcome === "WITH_RESERVATIONS" || act.reception_outcome === "UNDER_RESERVATIONS")
    && act.case_id === caseId,
  );

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!onCreate || submitting) return;
    if (!pending && (!draft.summary.trim() || !draft.source_ref.trim()
      || (draft.obligation_type === "RESERVES_LIFTING"
        && !eligibleReceptionActs.some((act) => act.act_id === draft.origin_reception_act_id)))) {
      setError("VALIDATION");
      return;
    }
    const attempt = pending ?? {
      ids: { command_id: crypto.randomUUID(), idempotency_key: crypto.randomUUID(), obligation_id: crypto.randomUUID() },
      payload: draft,
    };
    setPending(attempt);
    setSubmitting(true);
    setError(false);
    try {
      await onCreate({
        ...attempt.ids,
        obligation_type: attempt.payload.obligation_type,
        origin_reception_act_id: attempt.payload.obligation_type === "RESERVES_LIFTING" ? attempt.payload.origin_reception_act_id : null,
        summary: attempt.payload.summary,
        source_refs: [attempt.payload.source_ref],
        due_date: attempt.payload.due_date || null,
        resource_note: attempt.payload.resource_note || null,
        cost_estimate_note: attempt.payload.cost_estimate_note || null,
        fulfillment_proof_refs: attempt.payload.proof_ref ? [attempt.payload.proof_ref] : [],
        sanction_ref: attempt.payload.sanction_ref || null,
      });
      setDraft(EMPTY_DRAFT);
      setPending(null);
    } catch {
      setError("UNCONFIRMED");
    } finally {
      setSubmitting(false);
    }
  }

  return <section className="section-block decision-section" aria-label="Obligations post-réception">
    <div className="section-heading"><div><span className="section-kicker">APRÈS RÉCEPTION</span><h2>Obligations à suivre</h2></div></div>
    {onCreate && <form onSubmit={(event) => void submit(event)}>
      <label>Type d’obligation<select aria-label="Type d’obligation" value={draft.obligation_type} disabled={!!pending || submitting} onChange={(event) => setDraft({ ...draft, obligation_type: event.target.value as Draft["obligation_type"] })}>{OBLIGATION_TYPES.map((type) => <option key={type} value={type}>{type}</option>)}</select></label>
      {draft.obligation_type === "RESERVES_LIFTING" && <label>Acte de réception source
        <select aria-label="Acte de réception source" required value={draft.origin_reception_act_id} disabled={!!pending || submitting} onChange={(event) => setDraft({ ...draft, origin_reception_act_id: event.target.value })}>
          <option value="">Choisir une réception déclarée avec/sous réserves</option>
          {eligibleReceptionActs.map((act) => <option key={act.act_id} value={act.act_id}>{act.summary} · {act.reception_outcome}</option>)}
        </select>
      </label>}
      <label>Résumé<input aria-label="Résumé de l’obligation" required value={draft.summary} disabled={!!pending || submitting} onChange={(event) => setDraft({ ...draft, summary: event.target.value })} /></label>
      <label>Source<input aria-label="Source de l’obligation" required value={draft.source_ref} disabled={!!pending || submitting} onChange={(event) => setDraft({ ...draft, source_ref: event.target.value })} /></label>
      <label>Échéance déclarée<input aria-label="Échéance déclarée" type="date" value={draft.due_date} disabled={!!pending || submitting} onChange={(event) => setDraft({ ...draft, due_date: event.target.value })} /></label>
      <label>Ressource<input aria-label="Ressource requise" value={draft.resource_note} disabled={!!pending || submitting} onChange={(event) => setDraft({ ...draft, resource_note: event.target.value })} /></label>
      <label>Coût estimatif<input aria-label="Note de coût estimatif" value={draft.cost_estimate_note} disabled={!!pending || submitting} onChange={(event) => setDraft({ ...draft, cost_estimate_note: event.target.value })} /></label>
      <label>Preuve disponible<input aria-label="Référence de preuve" value={draft.proof_ref} disabled={!!pending || submitting} onChange={(event) => setDraft({ ...draft, proof_ref: event.target.value })} /></label>
      <label>Sanction liée<input aria-label="Référence de sanction" value={draft.sanction_ref} disabled={!!pending || submitting} onChange={(event) => setDraft({ ...draft, sanction_ref: event.target.value })} /></label>
      <button type="submit" disabled={submitting}>{error === "UNCONFIRMED" ? "Réessayer l’enregistrement" : "Enregistrer l’obligation"}</button>
      {error === "VALIDATION" && <p role="alert">Renseignez le résumé, une source, et pour une levée de réserves sélectionnez une réception admissible de cette Affaire.</p>}
      {error === "UNCONFIRMED" && <p role="alert">Résultat non confirmé · réessaie avec la même intention.</p>}
    </form>}
    {obligations.length === 0 ? <p>Aucune obligation post-réception enregistrée.</p> : <div className="decision-grid">{obligations.map((obligation) => <ObligationCard key={`${obligation.case_id}:${obligation.obligation_id}`} obligation={obligation} onTransition={onTransition} />)}</div>}
  </section>;
}
