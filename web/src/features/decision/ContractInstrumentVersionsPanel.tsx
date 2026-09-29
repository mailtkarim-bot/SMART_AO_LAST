import type { FormEvent } from "react";
import { useEffect, useState } from "react";
import type {
  ContractInstrumentKind,
  ContractInstrumentSupersession,
  ContractInstrumentVersion,
  DeclareContractInstrumentSupersessionInput,
  RecordContractInstrumentVersionInput,
} from "../../shared/types";
import type { ContractInstrumentVersionReadStatus } from "../pricing/useContractInstrumentVersions";

type VersionDraft = {
  instrument_kind: ContractInstrumentKind;
  version_reference: string;
  source_refs: string;
  evidence_refs: string;
};
type SupersessionDraft = {
  replacing_version_id: string;
  replaced_version_id: string;
  rationale: string;
};
const EMPTY_VERSION_DRAFT: VersionDraft = {
  instrument_kind: "SIGNED_CONTRACT", version_reference: "", source_refs: "", evidence_refs: "",
};
const EMPTY_SUPERSESSION_DRAFT: SupersessionDraft = {
  replacing_version_id: "", replaced_version_id: "", rationale: "",
};

function refsFromLines(value: string): string[] {
  return value.split("\n").map((ref) => ref.trim()).filter(Boolean);
}

function instrumentLabel(kind: ContractInstrumentKind): string {
  return kind === "SIGNED_CONTRACT" ? "Contrat signé" : "Avenant";
}

export function ContractInstrumentVersionsPanel({
  caseId,
  versions,
  supersessions,
  status,
  canManage,
  onCreate,
  onDeclareSupersession,
}: {
  caseId: string;
  versions: ContractInstrumentVersion[];
  supersessions: ContractInstrumentSupersession[];
  status: ContractInstrumentVersionReadStatus;
  canManage: boolean;
  onCreate?: (caseId: string, input: RecordContractInstrumentVersionInput) => Promise<void>;
  onDeclareSupersession?: (caseId: string, input: DeclareContractInstrumentSupersessionInput) => Promise<void>;
}) {
  const [versionDraft, setVersionDraft] = useState(EMPTY_VERSION_DRAFT);
  const [supersessionDraft, setSupersessionDraft] = useState(EMPTY_SUPERSESSION_DRAFT);
  const [draftCaseId, setDraftCaseId] = useState(caseId);
  const [versionPending, setVersionPending] = useState<{ caseId: string; input: RecordContractInstrumentVersionInput } | null>(null);
  const [supersessionPending, setSupersessionPending] = useState<{ caseId: string; input: DeclareContractInstrumentSupersessionInput } | null>(null);
  const [versionSubmitting, setVersionSubmitting] = useState(false);
  const [supersessionSubmitting, setSupersessionSubmitting] = useState(false);
  const [versionError, setVersionError] = useState<"VALIDATION" | "UNCONFIRMED" | null>(null);
  const [supersessionError, setSupersessionError] = useState<"VALIDATION" | "UNCONFIRMED" | null>(null);

  useEffect(() => {
    const pendingForOtherCase = (versionPending && versionPending.caseId !== caseId)
      || (supersessionPending && supersessionPending.caseId !== caseId);
    if (draftCaseId !== caseId && !pendingForOtherCase) {
      setVersionDraft(EMPTY_VERSION_DRAFT);
      setSupersessionDraft(EMPTY_SUPERSESSION_DRAFT);
      setVersionError(null);
      setSupersessionError(null);
      setDraftCaseId(caseId);
    }
  }, [caseId, draftCaseId, versionPending, supersessionPending]);

  async function submitVersion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canManage || !onCreate || versionSubmitting) return;
    const attempt = versionPending?.caseId === caseId ? versionPending : {
      caseId,
      input: {
        command_id: crypto.randomUUID(),
        idempotency_key: crypto.randomUUID(),
        contract_instrument_version_id: crypto.randomUUID(),
        instrument_kind: versionDraft.instrument_kind,
        version_reference: versionDraft.version_reference.trim(),
        source_refs: refsFromLines(versionDraft.source_refs),
        evidence_refs: refsFromLines(versionDraft.evidence_refs),
      },
    };
    if (versionPending && versionPending.caseId !== caseId) return;
    const { input } = attempt;
    const refs = [...input.source_refs, ...input.evidence_refs];
    if (!input.version_reference || input.version_reference.length > 500
      || input.source_refs.length === 0 || input.evidence_refs.length === 0
      || input.source_refs.length > 32 || input.evidence_refs.length > 32
      || refs.some((ref) => !ref || ref.length > 1000)) {
      setVersionError("VALIDATION");
      return;
    }
    setVersionPending(attempt);
    setVersionSubmitting(true);
    setVersionError(null);
    try {
      await onCreate(attempt.caseId, input);
      setVersionDraft(EMPTY_VERSION_DRAFT);
      setVersionPending(null);
    } catch {
      setVersionError("UNCONFIRMED");
    } finally {
      setVersionSubmitting(false);
    }
  }

  async function submitSupersession(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canManage || !onDeclareSupersession || supersessionSubmitting) return;
    const attempt = supersessionPending?.caseId === caseId ? supersessionPending : {
      caseId,
      input: {
        command_id: crypto.randomUUID(),
        idempotency_key: crypto.randomUUID(),
        supersession_id: crypto.randomUUID(),
        replacing_contract_instrument_version_id: supersessionDraft.replacing_version_id,
        replaced_contract_instrument_version_id: supersessionDraft.replaced_version_id,
        rationale: supersessionDraft.rationale.trim(),
      },
    };
    if (supersessionPending && supersessionPending.caseId !== caseId) return;
    const { input } = attempt;
    if (!input.replacing_contract_instrument_version_id
      || !input.replaced_contract_instrument_version_id
      || input.replacing_contract_instrument_version_id === input.replaced_contract_instrument_version_id
      || !input.rationale || input.rationale.length > 2000) {
      setSupersessionError("VALIDATION");
      return;
    }
    setSupersessionPending(attempt);
    setSupersessionSubmitting(true);
    setSupersessionError(null);
    try {
      await onDeclareSupersession(attempt.caseId, input);
      setSupersessionDraft(EMPTY_SUPERSESSION_DRAFT);
      setSupersessionPending(null);
    } catch {
      setSupersessionError("UNCONFIRMED");
    } finally {
      setSupersessionSubmitting(false);
    }
  }

  if ((versionPending && versionPending.caseId !== caseId)
    || (supersessionPending && supersessionPending.caseId !== caseId)) {
    return <section className="detail-panel" aria-label="Déclaration contractuelle en attente">
      <p role="status">Un résultat d’enregistrement contractuel reste à vérifier pour une autre Affaire.</p>
    </section>;
  }
  if (draftCaseId !== caseId) return <section className="detail-panel" aria-label="Chargement du formulaire contractuel">
    <p role="status">Chargement du formulaire contractuel pour l’Affaire courante…</p>
  </section>;

  const amendments = versions.filter((version) => version.instrument_kind === "AMENDMENT");
  return <section className="detail-panel" aria-label="Versions sourcées de contrat signé et d’avenant">
    <h3>Versions du contrat signé et des avenants</h3>
    <p>Ces versions sont des références déclarées par le Patron avec leurs pièces ; leur authenticité, leur ordre juridique et leur applicabilité ne sont pas vérifiés.</p>
    {status === "LOADING" ? <p role="status">Chargement des versions contractuelles déclarées…</p>
      : status === "UNAVAILABLE" ? <p>UNAVAILABLE · impossible de lire les versions et déclarations de remplacement.</p>
        : versions.length === 0 ? <p>UNKNOWN · aucune version de contrat ou d’avenant n’est enregistrée ; cela ne prouve pas son absence.</p>
          : <ul aria-label="Versions contractuelles déclarées">{versions.map((version) => <li key={version.contract_instrument_version_id}>
            <strong>{instrumentLabel(version.instrument_kind)} · {version.version_reference}</strong>
            <span>Sources : {version.source_refs.join(" · ")}</span>
            <span>Pièces : {version.evidence_refs.join(" · ")}</span>
          </li>)}</ul>}
    {status === "READY" && supersessions.length > 0 && <ul aria-label="Déclarations de remplacement d’avenant">{supersessions.map((declaration) => <li key={declaration.supersession_id}>
      <strong>Déclaration Patron : {declaration.replacing_instrument_kind === "AMENDMENT" ? "Avenant" : "Contrat signé"} · {declaration.replacing_version_reference} remplace {declaration.replaced_instrument_kind === "SIGNED_CONTRACT" ? "le contrat signé" : "l’avenant"} · {declaration.replaced_version_reference}</strong>
      <span>Justification : {declaration.rationale} · déclaré par {declaration.actor_id} le {declaration.recorded_at}</span>
      <span>Cette déclaration ne qualifie pas l’applicabilité juridique.</span>
    </li>)}</ul>}
    {status === "READY" && supersessions.length === 0 && <p>UNKNOWN · aucune déclaration de remplacement d’avenant enregistrée.</p>}
    {canManage && onCreate && <form aria-label="Déclarer une version contractuelle sourcée" onSubmit={(event) => void submitVersion(event)}>
      <label>Type de version
        <select aria-label="Type de version contractuelle à déclarer" value={versionDraft.instrument_kind} disabled={!!versionPending || versionSubmitting} onChange={(event) => setVersionDraft({ ...versionDraft, instrument_kind: event.target.value as ContractInstrumentKind })}>
          <option value="SIGNED_CONTRACT">Contrat signé</option>
          <option value="AMENDMENT">Avenant</option>
        </select>
      </label>
      <label>Référence exacte de version
        <input required maxLength={500} aria-label="Référence exacte de version" value={versionDraft.version_reference} disabled={!!versionPending || versionSubmitting} onChange={(event) => setVersionDraft({ ...versionDraft, version_reference: event.target.value })} />
      </label>
      <label>Sources d’identification, une par ligne
        <textarea required maxLength={32031} aria-label="Sources d’identification, une par ligne" value={versionDraft.source_refs} disabled={!!versionPending || versionSubmitting} onChange={(event) => setVersionDraft({ ...versionDraft, source_refs: event.target.value })} />
      </label>
      <label>Pièces justificatives, une par ligne
        <textarea required maxLength={32031} aria-label="Pièces justificatives, une par ligne" value={versionDraft.evidence_refs} disabled={!!versionPending || versionSubmitting} onChange={(event) => setVersionDraft({ ...versionDraft, evidence_refs: event.target.value })} />
      </label>
      <button type="submit" disabled={versionSubmitting}>{versionSubmitting ? "Enregistrement…" : "Enregistrer la version sourcée"}</button>
      {versionError === "VALIDATION" && <p role="alert">Une référence et 1 à 32 sources et preuves (1 000 caractères maximum chacune) sont requises.</p>}
      {versionError === "UNCONFIRMED" && <p role="alert">Résultat non confirmé · vérifiez la lecture serveur. Le rejeu réutilise les mêmes identifiants.</p>}
    </form>}
    {canManage && onDeclareSupersession && status === "READY" && amendments.length > 0 && versions.length > 1 && <form aria-label="Déclarer un remplacement contractuel" onSubmit={(event) => void submitSupersession(event)}>
      <h4>Déclarer qu’un avenant remplace une version</h4>
      <p>Déclaration du Patron uniquement : les actes rattachés à la version remplacée demanderont une requalification humaine. Aucune applicabilité juridique n’est déduite.</p>
      <label>Avenant déclaré comme remplaçant
        <select required aria-label="Avenant déclaré comme remplaçant" value={supersessionDraft.replacing_version_id} disabled={!!supersessionPending || supersessionSubmitting} onChange={(event) => setSupersessionDraft({ ...supersessionDraft, replacing_version_id: event.target.value })}>
          <option value="">Choisir un avenant</option>
          {amendments.map((version) => <option key={version.contract_instrument_version_id} value={version.contract_instrument_version_id}>{version.version_reference}</option>)}
        </select>
      </label>
      <label>Version remplacée par cet avenant
        <select required aria-label="Version remplacée par cet avenant" value={supersessionDraft.replaced_version_id} disabled={!!supersessionPending || supersessionSubmitting} onChange={(event) => setSupersessionDraft({ ...supersessionDraft, replaced_version_id: event.target.value })}>
          <option value="">Choisir une version existante</option>
          {versions.filter((version) => version.contract_instrument_version_id !== supersessionDraft.replacing_version_id).map((version) => <option key={version.contract_instrument_version_id} value={version.contract_instrument_version_id}>{instrumentLabel(version.instrument_kind)} · {version.version_reference}</option>)}
        </select>
      </label>
      <label>Justification de la déclaration
        <textarea required maxLength={2000} aria-label="Justification de la déclaration" value={supersessionDraft.rationale} disabled={!!supersessionPending || supersessionSubmitting} onChange={(event) => setSupersessionDraft({ ...supersessionDraft, rationale: event.target.value })} />
      </label>
      <button type="submit" disabled={supersessionSubmitting}>{supersessionSubmitting ? "Enregistrement…" : supersessionError === "UNCONFIRMED" && supersessionPending ? "Réessayer la déclaration" : "Déclarer le remplacement"}</button>
      {supersessionError === "VALIDATION" && <p role="alert">Sélectionnez deux versions distinctes et fournissez une justification (2 000 caractères maximum).</p>}
      {supersessionError === "UNCONFIRMED" && <p role="alert">Résultat non confirmé · vérifiez la lecture serveur. Le rejeu réutilise les mêmes identifiants.</p>}
    </form>}
  </section>;
}
