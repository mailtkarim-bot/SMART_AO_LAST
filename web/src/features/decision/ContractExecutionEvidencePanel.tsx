import type { FormEvent } from "react";
import { useEffect, useState } from "react";
import type { ContractExecutionActKind, ContractInstrumentVersion, RecordContractExecutionEvidenceInput } from "../../shared/types";
import type { ContractReceptionOutcome } from "../../shared/types";

type Draft = {
  act_kind: ContractExecutionActKind;
  reception_outcome: ContractReceptionOutcome | "";
  summary: string;
  source_refs: string;
  evidence_refs: string;
  declared_event_date: string;
  contract_instrument_version_id: string;
};

const EMPTY_DRAFT: Draft = {
  act_kind: "WORK_RECEPTION", reception_outcome: "", summary: "", source_refs: "", evidence_refs: "", declared_event_date: "",
  contract_instrument_version_id: "",
};

function refsFromLines(value: string): string[] {
  return value.split("\n").map((ref) => ref.trim()).filter(Boolean);
}

export function ContractExecutionEvidencePanel({
  caseId,
  canManage,
  instrumentVersions = [],
  onCreate,
}: {
  caseId: string;
  canManage: boolean;
  instrumentVersions?: ContractInstrumentVersion[];
  onCreate?: (caseId: string, input: RecordContractExecutionEvidenceInput) => Promise<void>;
}) {
  const [draft, setDraft] = useState(EMPTY_DRAFT);
  const [draftCaseId, setDraftCaseId] = useState(caseId);
  const [pending, setPending] = useState<{ caseId: string; input: RecordContractExecutionEvidenceInput } | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<"VALIDATION" | "UNCONFIRMED" | null>(null);

  useEffect(() => {
    if (draftCaseId !== caseId && (!pending || pending.caseId === caseId)) {
      setDraft(EMPTY_DRAFT);
      setError(null);
      setDraftCaseId(caseId);
    }
  }, [caseId, draftCaseId, pending]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canManage || !onCreate || submitting) return;
    const attempt = pending?.caseId === caseId ? pending : {
      caseId,
      input: {
      command_id: crypto.randomUUID(),
      idempotency_key: crypto.randomUUID(),
      act_id: crypto.randomUUID(),
      act_kind: draft.act_kind,
      reception_outcome: draft.act_kind === "WORK_RECEPTION" ? draft.reception_outcome || null : null,
      summary: draft.summary.trim(),
      source_refs: refsFromLines(draft.source_refs),
      evidence_refs: refsFromLines(draft.evidence_refs),
      declared_event_date: draft.declared_event_date || null,
      contract_instrument_version_id: draft.contract_instrument_version_id || null,
      },
    };
    if (pending && pending.caseId !== caseId) return;
    const input = attempt.input;
    const refs = [...input.source_refs, ...input.evidence_refs];
    const selectedInstrumentVersion = instrumentVersions.some(
      (version) => version.contract_instrument_version_id === input.contract_instrument_version_id
        && version.case_id === caseId,
    );
    if (!input.summary || input.summary.length > 2000 || input.source_refs.length === 0
      || input.evidence_refs.length === 0 || input.source_refs.length > 32 || input.evidence_refs.length > 32
      || refs.some((ref) => !ref || ref.length > 1000)
      || (!pending && input.contract_instrument_version_id !== null && !selectedInstrumentVersion)
      || (input.act_kind === "WORK_RECEPTION" && !input.reception_outcome)) {
      setError("VALIDATION");
      return;
    }
    setPending(attempt);
    setSubmitting(true);
    setError(null);
    try {
      await onCreate(attempt.caseId, input);
      setDraft({ ...EMPTY_DRAFT, contract_instrument_version_id: draft.contract_instrument_version_id });
      setPending(null);
    } catch {
      setError("UNCONFIRMED");
    } finally {
      setSubmitting(false);
    }
  }

  if (!canManage || !onCreate) return null;
  if (pending && pending.caseId !== caseId) return <section className="detail-panel" aria-label="Acte contractuel en attente">
    <p role="status">Un résultat d’enregistrement reste à vérifier pour une autre Affaire. Revenez à cette Affaire pour relire ou rejouer la même demande.</p>
  </section>;
  if (draftCaseId !== caseId) return <section className="detail-panel" aria-label="Chargement du formulaire d’acte contractuel">
    <p role="status">Chargement du formulaire d’acte pour l’Affaire courante…</p>
  </section>;
  return <section className="detail-panel" aria-label="Acte humain de réception, préservation des droits ou sortie contractuelle">
    <h3>Enregistrer un acte humain sourcé</h3>
    <p>L’enregistrement conserve la déclaration, ses pièces et sa date éventuelle. Il n’évalue pas sa portée juridique et ne calcule aucune échéance.</p>
    <form aria-label="Enregistrer un acte contractuel sourcé" onSubmit={(event) => void submit(event)}>
      <label>Type d’acte déclaré
        <select required aria-label="Type d’acte déclaré" value={draft.act_kind} disabled={!!pending || submitting} onChange={(event) => setDraft({ ...draft, act_kind: event.target.value as ContractExecutionActKind })}>
          <option value="WORK_RECEPTION">Réception d’ouvrage</option>
          <option value="RIGHTS_PRESERVATION">Préservation des droits</option>
          <option value="CONTRACT_EXIT">Sortie contractuelle</option>
        </select>
      </label>
      {draft.act_kind === "WORK_RECEPTION" && <label>Réserves consignées au procès-verbal
        <select required aria-label="Réserves consignées au procès-verbal" value={draft.reception_outcome} disabled={!!pending || submitting} onChange={(event) => setDraft({ ...draft, reception_outcome: event.target.value as Draft["reception_outcome"] })}>
          <option value="">Choisir l’état déclaré</option>
          <option value="WITH_RESERVATIONS">Avec réserves</option>
          <option value="UNDER_RESERVATIONS">Sous réserves</option>
          <option value="WITHOUT_RESERVATIONS">Sans réserves</option>
        </select>
      </label>}
      <label>Description de l’acte
        <textarea required maxLength={2000} aria-label="Description de l’acte" value={draft.summary} disabled={!!pending || submitting} onChange={(event) => setDraft({ ...draft, summary: event.target.value })} />
      </label>
      <label>Références sources, une par ligne
        <textarea required maxLength={32031} aria-label="Références sources, une par ligne" value={draft.source_refs} disabled={!!pending || submitting} onChange={(event) => setDraft({ ...draft, source_refs: event.target.value })} />
      </label>
      <label>Références de preuve, une par ligne
        <textarea required maxLength={32031} aria-label="Références de preuve, une par ligne" value={draft.evidence_refs} disabled={!!pending || submitting} onChange={(event) => setDraft({ ...draft, evidence_refs: event.target.value })} />
      </label>
      <label>Date de l’acte déclarée
        <input type="date" aria-label="Date de l’acte déclarée" value={draft.declared_event_date} disabled={!!pending || submitting} onChange={(event) => setDraft({ ...draft, declared_event_date: event.target.value })} />
      </label>
      <label>Version du contrat signé ou de l’avenant
        <select aria-label="Version du contrat signé ou de l’avenant" value={draft.contract_instrument_version_id} disabled={!!pending || submitting} onChange={(event) => setDraft({ ...draft, contract_instrument_version_id: event.target.value })}>
          <option value="">UNKNOWN · aucune version enregistrée/sélectionnée</option>
          {instrumentVersions.map((version) => <option key={version.contract_instrument_version_id} value={version.contract_instrument_version_id}>
            {version.instrument_kind === "SIGNED_CONTRACT" ? "Contrat signé" : "Avenant"} · {version.version_reference}
          </option>)}
        </select>
      </label>
      <button type="submit" disabled={submitting}>{submitting ? "Enregistrement…" : error === "UNCONFIRMED" && pending ? "Réessayer l’enregistrement" : "Enregistrer l’acte"}</button>
      {error === "VALIDATION" && <p role="alert">Vérifiez les références : 1 à 32 sources/preuves par liste ; choisissez aussi l’état de réserves pour une réception.</p>}
      {error === "UNCONFIRMED" && <p role="alert">Résultat non confirmé · vérifiez la lecture serveur. Le rejeu conserve les mêmes identifiants.</p>}
    </form>
  </section>;
}
