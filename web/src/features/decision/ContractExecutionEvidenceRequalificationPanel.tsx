import type { FormEvent } from "react";
import { useEffect, useState } from "react";
import type {
  ContractExecutionEvidence,
  ContractExecutionEvidenceRequalification,
  ContractInstrumentSupersession,
  ContractInstrumentVersion,
  RecordContractExecutionEvidenceRequalificationInput,
} from "../../shared/types";
import type { ContractExecutionEvidenceReadStatus } from "../pricing/useContractExecutionEvidence";

type Draft = {
  act_id: string;
  supersession_id: string;
  decision: RecordContractExecutionEvidenceRequalificationInput["decision"];
  resulting_contract_instrument_version_id: string;
  rationale: string;
};
const EMPTY_DRAFT: Draft = {
  act_id: "",
  supersession_id: "",
  decision: "RETAINED_AS_DECLARED",
  resulting_contract_instrument_version_id: "",
  rationale: "",
};

function versionLabel(version: ContractInstrumentVersion): string {
  const kind = version.instrument_kind === "SIGNED_CONTRACT" ? "Contrat signé" : "Avenant";
  return `${kind} · ${version.version_reference}`;
}

function decisionLabel(decision: ContractExecutionEvidenceRequalification["decision"]): string {
  switch (decision) {
    case "RETAINED_AS_DECLARED": return "Conservé tel que déclaré";
    case "RELINKED_TO_DECLARED_VERSION": return "Rattaché à une autre version déclarée";
    case "NEEDS_CLARIFICATION": return "Précisions requises";
  }
}

export function ContractExecutionEvidenceRequalificationPanel({
  caseId,
  acts,
  versions,
  supersessions,
  requalifications,
  status,
  canManage,
  onRecord,
}: {
  caseId: string;
  acts: ContractExecutionEvidence[];
  versions: ContractInstrumentVersion[];
  supersessions: ContractInstrumentSupersession[];
  requalifications: ContractExecutionEvidenceRequalification[];
  status: ContractExecutionEvidenceReadStatus;
  canManage: boolean;
  onRecord?: (caseId: string, input: RecordContractExecutionEvidenceRequalificationInput) => Promise<void>;
}) {
  const [draft, setDraft] = useState(EMPTY_DRAFT);
  const [draftCaseId, setDraftCaseId] = useState(caseId);
  const [pending, setPending] = useState<{
    caseId: string;
    input: RecordContractExecutionEvidenceRequalificationInput;
  } | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<"VALIDATION" | "UNCONFIRMED" | null>(null);

  useEffect(() => {
    if (draftCaseId !== caseId && (!pending || pending.caseId === caseId)) {
      setDraft(EMPTY_DRAFT);
      setError(null);
      setDraftCaseId(caseId);
    }
  }, [caseId, draftCaseId, pending]);

  const eligibleActs = acts.filter((act) => (
    act.case_id === caseId
    && act.contract_instrument_version_relation === "REVIEW_REQUIRED"
    && act.contract_instrument_version_id !== null
  ));
  const selectedAct = eligibleActs.find((act) => act.act_id === draft.act_id);
  const availableSupersessions = supersessions.filter((item) => (
    item.case_id === caseId
    && item.replaced_contract_instrument_version_id === selectedAct?.contract_instrument_version_id
  ));
  const selectedSupersession = availableSupersessions.find(
    (item) => item.supersession_id === draft.supersession_id,
  );
  const latestRevision = requalifications
    .filter((item) => item.act_id === draft.act_id && item.supersession_id === draft.supersession_id)
    .reduce((latest, item) => Math.max(latest, item.review_revision), 0);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canManage || !onRecord || submitting) return;
    const attempt = pending?.caseId === caseId ? pending : {
      caseId,
      input: {
        command_id: crypto.randomUUID(),
        idempotency_key: crypto.randomUUID(),
        requalification_id: crypto.randomUUID(),
        act_id: draft.act_id,
        supersession_id: draft.supersession_id,
        expected_revision: latestRevision,
        decision: draft.decision,
        resulting_contract_instrument_version_id: (
          draft.decision === "RELINKED_TO_DECLARED_VERSION"
            ? draft.resulting_contract_instrument_version_id || null
            : null
        ),
        rationale: draft.rationale.trim(),
      },
    };
    if (pending && pending.caseId !== caseId) return;
    const { input } = attempt;
    const selectedTarget = versions.some((version) => (
      version.case_id === caseId
      && version.contract_instrument_version_id === input.resulting_contract_instrument_version_id
    ));
    if (!selectedAct || !selectedSupersession || !input.rationale || input.rationale.length > 2000
      || (input.decision === "RELINKED_TO_DECLARED_VERSION" && !selectedTarget)) {
      setError("VALIDATION");
      return;
    }
    setPending(attempt);
    setSubmitting(true);
    setError(null);
    try {
      await onRecord(attempt.caseId, input);
      setDraft(EMPTY_DRAFT);
      setPending(null);
    } catch {
      setError("UNCONFIRMED");
    } finally {
      setSubmitting(false);
    }
  }

  if (pending && pending.caseId !== caseId) return <section className="detail-panel" aria-label="Requalification en attente">
    <p role="status">Un résultat de requalification reste à vérifier pour une autre Affaire.</p>
  </section>;
  if (draftCaseId !== caseId) return <section className="detail-panel" aria-label="Chargement de la requalification">
    <p role="status">Chargement de la revue humaine pour l’Affaire courante…</p>
  </section>;

  const visibleReviews = requalifications.filter((item) => item.case_id === caseId);
  return <section className="detail-panel" aria-label="Revue humaine de requalification contractuelle">
    <h3>Revue humaine des actes liés à une version remplacée</h3>
    <p>Cette décision Patron conserve l’acte d’origine et son signal `REVIEW_REQUIRED`. Elle ne confirme pas l’applicabilité juridique de la version choisie.</p>
    {status === "LOADING" ? <p role="status">Chargement de l’historique des requalifications…</p>
      : status === "UNAVAILABLE" ? <p>UNAVAILABLE · impossible de lire les actes et leurs requalifications.</p>
        : visibleReviews.length === 0 ? <p>UNKNOWN · aucune décision humaine de requalification enregistrée.</p>
          : <ol aria-label="Historique des requalifications humaines">{visibleReviews.map((item) => {
            const trigger = supersessions.find((entry) => entry.supersession_id === item.supersession_id);
            const sourceAct = acts.find((entry) => entry.act_id === item.act_id);
            return <li key={item.requalification_id}>
              <strong>Revue {item.review_revision} · {decisionLabel(item.decision)}</strong>
              <span>Acte conservé : {item.act_summary} · {item.act_kind}</span>
              <span>Déclaration examinée : {trigger?.replacing_version_reference ?? "UNKNOWN"} remplace {trigger?.replaced_version_reference ?? "UNKNOWN"}</span>
              <span>Version déclarée après revue : {item.resulting_version_reference ?? "UNKNOWN"}</span>
              <span>Justification : {item.rationale} · par {item.actor_id} le {item.recorded_at}</span>
              <span>Signal source conservé : REVIEW_REQUIRED · applicabilité juridique non évaluée.</span>
              {sourceAct && <span>Sources de l’acte initial : {sourceAct.source_refs.join(" · ")} · preuves : {sourceAct.evidence_refs.join(" · ")}</span>}
            </li>;
          })}</ol>}
    {canManage && onRecord && status === "READY" && eligibleActs.length > 0 && <form aria-label="Requalifier un acte contractuel" onSubmit={(event) => void submit(event)}>
      <label>Acte à requalifier
        <select required aria-label="Acte à requalifier" value={draft.act_id} disabled={!!pending || submitting} onChange={(event) => setDraft({ ...draft, act_id: event.target.value, supersession_id: "" })}>
          <option value="">Choisir un acte signalé</option>
          {eligibleActs.map((act) => <option key={act.act_id} value={act.act_id}>{act.summary}</option>)}
        </select>
      </label>
      <label>Déclaration de remplacement examinée
        <select required aria-label="Déclaration de remplacement examinée" value={draft.supersession_id} disabled={!draft.act_id || !!pending || submitting} onChange={(event) => setDraft({ ...draft, supersession_id: event.target.value })}>
          <option value="">Choisir la déclaration</option>
          {availableSupersessions.map((item) => <option key={item.supersession_id} value={item.supersession_id}>{item.replacing_version_reference} remplace {item.replaced_version_reference}</option>)}
        </select>
      </label>
      <label>Décision de requalification
        <select aria-label="Décision de requalification" value={draft.decision} disabled={!!pending || submitting} onChange={(event) => setDraft({ ...draft, decision: event.target.value as Draft["decision"], resulting_contract_instrument_version_id: "" })}>
          <option value="RETAINED_AS_DECLARED">Conserver le rattachement déclaré</option>
          <option value="RELINKED_TO_DECLARED_VERSION">Rattacher à une autre version déclarée</option>
          <option value="NEEDS_CLARIFICATION">Précisions requises</option>
        </select>
      </label>
      {draft.decision === "RELINKED_TO_DECLARED_VERSION" && <label>Version déclarée après requalification
        <select required aria-label="Version déclarée après requalification" value={draft.resulting_contract_instrument_version_id} disabled={!!pending || submitting} onChange={(event) => setDraft({ ...draft, resulting_contract_instrument_version_id: event.target.value })}>
          <option value="">Choisir une version</option>
          {versions.filter((version) => version.case_id === caseId).map((version) => <option key={version.contract_instrument_version_id} value={version.contract_instrument_version_id}>{versionLabel(version)}</option>)}
        </select>
      </label>}
      <label>Justification de requalification
        <textarea required maxLength={2000} aria-label="Justification de requalification" value={draft.rationale} disabled={!!pending || submitting} onChange={(event) => setDraft({ ...draft, rationale: event.target.value })} />
      </label>
      <button type="submit" disabled={submitting}>{submitting ? "Enregistrement…" : error === "UNCONFIRMED" && pending ? "Réessayer la requalification" : "Enregistrer la décision humaine"}</button>
      {error === "VALIDATION" && <p role="alert">Sélectionnez l’acte et sa déclaration, puis complétez la version demandée et la justification.</p>}
      {error === "UNCONFIRMED" && <p role="alert">Résultat non confirmé · vérifiez la lecture serveur. Le rejeu reprend les mêmes identifiants.</p>}
    </form>}
    {canManage && status === "READY" && eligibleActs.length === 0 && <p>UNKNOWN · aucun acte lié à une version contractuelle déclarée remplacée n’est à requalifier.</p>}
  </section>;
}
