import { useEffect, useLayoutEffect, useRef, useState } from "react";
import type { ApiClient } from "../../infrastructure/api";
import type {
  CaseHandoverOfferOption,
  CaseHandoverSnapshotItem,
  RecordCaseHandoverInput,
} from "../../shared/types";

type ReadState = "LOADING" | "READY" | "UNAVAILABLE";
type Failure = "UNCONFIRMED" | "REJECTED";
const commandIds = () => ({
  command_id: crypto.randomUUID(),
  idempotency_key: crypto.randomUUID(),
  correlation_id: crypto.randomUUID(),
});

function offerLabel(option: CaseHandoverOfferOption) {
  return "Lot " + option.lot_reference + " · paquet P5 v" + option.package_version
    + " · " + option.manifest_sha256.slice(0, 12);
}

export function CaseHandoverPanel({
  api,
  caseId,
  canManage,
}: {
  api: ApiClient;
  caseId: string;
  canManage: boolean;
}) {
  const [items, setItems] = useState<CaseHandoverSnapshotItem[]>([]);
  const [options, setOptions] = useState<CaseHandoverOfferOption[]>([]);
  const [readState, setReadState] = useState<ReadState>("LOADING");
  const [optionsLoaded, setOptionsLoaded] = useState(false);
  const [selected, setSelected] = useState("");
  const [pending, setPending] = useState<{ caseId: string; selected: string; input: RecordCaseHandoverInput } | null>(null);
  const [failure, setFailure] = useState<{ key: string; kind: Failure } | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [downloadingSnapshot, setDownloadingSnapshot] = useState<string | null>(null);
  const [message, setMessage] = useState("");
  const activeCaseId = useRef(caseId);
  useLayoutEffect(() => {
    activeCaseId.current = caseId;
    return () => {
      activeCaseId.current = "";
    };
  }, [caseId]);

  async function refresh(targetCaseId = caseId) {
    if (!targetCaseId) {
      setItems([]);
      setOptions([]);
      setReadState("UNAVAILABLE");
      setOptionsLoaded(true);
      return;
    }
    setReadState((current) => (current === "READY" ? current : "LOADING"));
    try {
      const snapshots = await api.listCaseHandoverSnapshots(targetCaseId);
      if (activeCaseId.current !== targetCaseId) return;
      if (snapshots.case_id !== targetCaseId) throw new Error("Case mismatch");
      setItems(snapshots.items);
      setReadState("READY");
    } catch {
      if (activeCaseId.current !== targetCaseId) return;
      setReadState("UNAVAILABLE");
    }
    if (canManage) {
      try {
        const offerOptions = await api.listCaseHandoverOfferOptions(targetCaseId);
        if (activeCaseId.current !== targetCaseId) return;
        if (offerOptions.case_id !== targetCaseId) throw new Error("Case mismatch");
        setOptions(offerOptions.items);
      } catch {
        if (activeCaseId.current !== targetCaseId) return;
        setOptions([]);
      }
      setOptionsLoaded(true);
    }
  }

  useEffect(() => {
    setItems([]);
    setOptions([]);
    setSelected("");
    setPending(null);
    setFailure(null);
    setSubmitting(false);
    setDownloadingSnapshot(null);
    setMessage("");
    setOptionsLoaded(!canManage);
    void refresh(caseId);
    // Refresh is intentionally scoped to the confirmed Case and actor surface.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [caseId, canManage]);

  const selectedOption = options.find(
    (option) => option.outcome_id + ":" + option.submission_package_id === selected,
  );
  const activeKey = selectedOption
    ? selectedOption.outcome_id + ":" + selectedOption.submission_package_id
    : "";

  async function transmit() {
    if (!canManage || !selectedOption || submitting) return;
    const submittedCaseId = caseId;
    const input = pending?.caseId === caseId && pending.selected === selected
      ? pending.input
      : {
          ...commandIds(),
          snapshot_id: crypto.randomUUID(),
          outcome_id: selectedOption.outcome_id,
          submission_package_id: selectedOption.submission_package_id,
        };
    if (!pending || pending.caseId !== caseId || pending.selected !== selected) {
      setPending({ caseId, selected, input });
    }
    setSubmitting(true);
    setFailure(null);
    setMessage("");
    try {
      const result = await api.recordCaseHandover(submittedCaseId, input);
      if (activeCaseId.current !== submittedCaseId) return;
      await refresh(submittedCaseId);
      setPending(null);
      setMessage(result.replayed
        ? "Rejeu confirmé : la même passation est conservée."
        : "Passation P7 enregistrée et disponible au Conducteur affecté.");
    } catch (error) {
      if (activeCaseId.current !== submittedCaseId) return;
      const status = (error as { status?: number })?.status;
      if (status !== undefined && status >= 400 && status < 500) {
        setPending(null);
        setFailure({ key: activeKey, kind: "REJECTED" });
      } else {
        setFailure({ key: activeKey, kind: "UNCONFIRMED" });
      }
    } finally {
      if (activeCaseId.current === submittedCaseId) setSubmitting(false);
    }
  }

  async function downloadOffer(snapshotId: string) {
    if (downloadingSnapshot) return;
    setDownloadingSnapshot(snapshotId);
    try {
      const blob = await api.downloadCaseHandoverOffer(caseId, snapshotId);
      if (activeCaseId.current !== caseId) return;
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "offre-technique.md";
      anchor.click();
      URL.revokeObjectURL(url);
    } catch {
      if (activeCaseId.current === caseId) {
        setMessage("Téléchargement indisponible · vérifiez les droits Conducteur et l’intégrité du P5.");
      }
    } finally {
      if (activeCaseId.current === caseId) setDownloadingSnapshot(null);
    }
  }

  return (
    <section className="section-block decision-section" aria-label="Passation P7 au Conducteur">
      <div className="section-heading">
        <div><span className="section-kicker">VERTICALE B · P7</span><h2>Passation au Conducteur</h2></div>
      </div>
      <p>P7 conserve l’offre attribuée, ses références et les conditions ouvertes. Cette passation ne crée pas un ordre de service.</p>
      <p>Les données financières privées et le contenu financier du paquet P5 ne sont pas inclus. La lecture est réservée au Patron et au Responsable affecté à l’Affaire.</p>
      {canManage && <>
        <label>Offre gagnée exacte à transmettre
          <select aria-label="Offre gagnée exacte à transmettre" value={selected} disabled={!optionsLoaded || submitting || !!pending} onChange={(event) => { setSelected(event.target.value); setFailure(null); }}>
            <option value="">Choisir une attribution WON et son paquet P5 autorisé</option>
            {options.map((option) => <option key={option.outcome_id + ":" + option.submission_package_id} value={option.outcome_id + ":" + option.submission_package_id}>{offerLabel(option)}</option>)}
          </select>
        </label>
        {optionsLoaded && options.length === 0 && <p>UNKNOWN · aucune offre P5 autorisée reliée à une attribution WON de cette Affaire.</p>}
        <button type="button" disabled={!selectedOption || submitting || (!!pending && (pending.caseId !== caseId || pending.selected !== selected))} onClick={() => void transmit()}>
          {submitting ? "Transmission…" : failure?.key === activeKey && failure.kind === "UNCONFIRMED" ? "Réessayer la même passation" : "Transmettre au Conducteur"}
        </button>
        {failure?.key === activeKey && <p role="alert">{failure.kind === "REJECTED" ? "Refus confirmé par le serveur ; aucune nouvelle passation n’a été enregistrée." : "Résultat non confirmé · le rejeu réutilise les mêmes identifiants."}</p>}
        {message && <p role="status">{message}</p>}
      </>}
      {readState === "LOADING" && <p>Lecture serveur de la passation…</p>}
      {readState === "UNAVAILABLE" && <p role="status">UNAVAILABLE · aucune passation confirmée n’est affichée. Vérifiez l’affectation Responsable si vous êtes Conducteur.</p>}
      {readState === "READY" && items.length === 0 && <p>UNKNOWN · aucune passation P7 n’a encore été enregistrée.</p>}
      {readState === "READY" && items.map((item) => {
        const snapshot = item.snapshot;
        return <article className="detail-panel" key={item.snapshot_id}>
          <h3>Lot {item.lot_reference} · passation P7 révision {item.revision}</h3>
          <p>Source d’attribution : {snapshot.award.source_locator ?? "UNKNOWN · aucune référence"}</p>
          <p>Offre P5 exacte : version {snapshot.offer.package_version} · SHA-256 {snapshot.offer.manifest_sha256}</p>
          <p>Document technique : {snapshot.offer.technical_document_id} · v{snapshot.offer.technical_document_version} · SHA-256 {snapshot.offer.technical_document_sha256}</p>
          {snapshot.offer.technical_document_kind === "TECHNICAL_RESPONSE" && <button type="button" disabled={!!downloadingSnapshot} onClick={() => void downloadOffer(item.snapshot_id)}>{downloadingSnapshot === item.snapshot_id ? "Téléchargement…" : "Télécharger l’offre technique exacte"}</button>}
          <p>Contenu financier : non inclus. P7 ≠ ordre de service.</p>
          <p>Rapprochement contrat / offre : {snapshot.contract_comparison.state} · {snapshot.contract_comparison.reason}</p>
          {snapshot.decision.conditions_state === "UNKNOWN"
            ? <p>UNKNOWN · état des conditions de décision indisponible au moment de la passation.</p>
            : snapshot.decision.open_conditions.length === 0
              ? <p>Aucune condition de GO n’était ouverte dans le contexte décisionnel figé.</p>
              : <div><h4>Conditions ouvertes au moment de la passation</h4><ul>{snapshot.decision.open_conditions.map((condition) => <li key={condition.condition_id}>{condition.label}{condition.due_at ? " · échéance déclarée : " + condition.due_at : " · échéance UNKNOWN"}</li>)}</ul></div>}
          <p>Sources contractuelles reliées : {snapshot.decision.condition_sources.length}</p>
          <small>Snapshot {item.snapshot_id} · enregistré le {item.created_at}</small>
        </article>;
      })}
    </section>
  );
}
