import { useEffect, useRef, useState, useSyncExternalStore } from "react";
import type { ApiClient } from "../../infrastructure/api";
import type { CapacityInput, CapacityProjection, CapacityReceipt, CapacityRow, CapacityRun } from "./types";
type Pending = {
  intent: CapacityInput;
  phase: "SENDING" | "UNKNOWN" | "READ_REQUIRED" | "CONFLICT";
  receipt: CapacityReceipt | null;
};
/** Private intents live only for the lifetime of the App, including context switches. */
export class CapacityPendingStore {
  private snapshot: ReadonlyMap<string, Pending> = new Map();
  private listeners = new Set<() => void>();
  getSnapshot = () => this.snapshot;
  subscribe = (fn: () => void) => {
    this.listeners.add(fn);
    return () => {
      this.listeners.delete(fn);
    };
  };
  put(key: string, value: Pending) {
    const old = this.snapshot.get(key);
    if (old && JSON.stringify(old.intent) !== JSON.stringify(value.intent)) throw Error("CAPACITY_INTENT_CONFLICT");
    const next = new Map(this.snapshot);
    next.set(key, structuredClone(value));
    this.snapshot = next;
    this.listeners.forEach(fn => fn());
  }
  remove(key: string) {
    const next = new Map(this.snapshot);
    next.delete(key);
    this.snapshot = next;
    this.listeners.forEach(fn => fn());
  }
}
type Props = {
  sourceReadBlocked?: boolean;
  api: ApiClient;
  enabled: boolean;
  caseId: string;
  ownerKey: string;
  scopeKey: string;
  pendingStore: CapacityPendingStore;
};
type EditRow = {
  id: string;
  label: string;
  kind: string;
  units: string;
  start: string;
  end: string;
  reference: string;
  revision: string;
  locator: string;
  named: string;
};
function empty(): EditRow {
  return {
    id: crypto.randomUUID(),
    label: "",
    kind: "",
    units: "",
    start: "",
    end: "",
    reference: "",
    revision: "",
    locator: "",
    named: ""
  };
}
function fromRow(row: CapacityRow): EditRow {
  return {
    id: row.id,
    label: row.label,
    kind: row.resource_type ?? "",
    units: row.units === null ? "" : String(row.units),
    start: row.start ?? "",
    end: row.end ?? "",
    reference: row.source?.reference ?? "",
    revision: row.source?.revision ?? "",
    locator: row.source?.locator ?? "",
    named: row.named_supply_id ?? ""
  };
}
function toRow(row: EditRow, demand: boolean): CapacityRow {
  if (!row.label.trim()) throw Error("Le libellé ne peut pas être vide.");
  const source = [row.reference, row.revision, row.locator].every(value => !value.trim()) ? null : {
    reference: row.reference.trim(),
    revision: row.revision.trim(),
    locator: row.locator.trim()
  };
  if (source && (!source.reference || !source.revision || !source.locator)) throw Error("Complétez les trois champs de source ou laissez-les inconnus.");
  if (Boolean(row.start) !== Boolean(row.end)) throw Error("Renseignez les deux dates ou laissez la période inconnue.");
  if (row.start && row.end && row.end <= row.start) throw Error("La fin exclue doit être postérieure au début.");
  const units = row.units.trim() === "" ? null : Number(row.units);
  if (units !== null && (!Number.isSafeInteger(units) || units < (demand ? 1 : 0) || units > 10000)) throw Error("Les unités doivent être des entiers dans les limites indiquées.");
  return {
    id: row.id,
    label: row.label.trim(),
    resource_type: row.kind.trim() || null,
    units,
    start: row.start || null,
    end: row.end || null,
    source,
    ...(demand ? {
      named_supply_id: row.named || null
    } : {})
  };
}
export function CapacityPanel(props: Props) {
  if (!props.enabled || !props.caseId) return null;
  if (props.sourceReadBlocked) return <section className="section-block scenario-creation" aria-label="Planification de capacité"><h2>Capacité datée de l’Affaire</h2><p role="status">Sources en cours de reprise : plan suspendu jusqu’à la relecture du DCE. Aucun accord reconduit.</p></section>;
  return <CapacityEditor key={JSON.stringify([props.ownerKey, props.scopeKey, props.caseId])} {...props} />;
}
function CapacityEditor({
  api,
  caseId,
  ownerKey,
  pendingStore
}: Props) {
  const key = JSON.stringify([ownerKey, caseId]);
  const pending = useSyncExternalStore(pendingStore.subscribe, pendingStore.getSnapshot).get(key);
  const [data, setData] = useState<CapacityProjection | null>(null);
  const [error, setError] = useState("");
  const [validationError, setValidationError] = useState("");
  const [loaded, setLoaded] = useState(false);
  const [refresh, setRefresh] = useState(0);
  const [demands, setDemands] = useState<EditRow[]>([]);
  const [supplies, setSupplies] = useState<EditRow[]>([]);
  const [demandsKnown, setDemandsKnown] = useState(false);
  const [suppliesKnown, setSuppliesKnown] = useState(false);
  const [why, setWhy] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const sourceContext = useRef<string | null>(null);
  useEffect(() => {
    if (pending?.phase === "UNKNOWN" || pending?.phase === "SENDING") return;
    let alive = true;
    api.getDatedCapacity(caseId).then(value => {
      if (!alive) return;
      if (value.case_id !== caseId || !Number.isSafeInteger(value.revision) || !Array.isArray(value.history)) throw Error("Projection discordante");
      if (pending?.receipt) {
        const runs = [value.current, ...value.history];
        if (!runs.some(run => run?.run_id === pending.receipt?.run_id && run?.revision === pending.receipt?.revision)) throw Error("Relecture du reçu non prouvée");
      }
      setConfirmed(false);
      if (sourceContext.current !== null && sourceContext.current !== value.context_sha256) {
        setDemands([]);
        setSupplies([]);
        setDemandsKnown(false);
        setSuppliesKnown(false);
        setWhy("");
      }
      sourceContext.current = value.context_sha256;
      setData(value);
      setLoaded(true);
      setError("");
      if (pending) pendingStore.remove(key);
    }).catch(() => {
      if (alive) {
        setLoaded(true);
        setData(null);
        setError("Lecture indisponible : réessayez la lecture.");
      }
    });
    return () => {
      alive = false;
    };
  }, [api, caseId, key, pending, pendingStore, refresh]);
  async function send(intent: CapacityInput) {
    const previous = pendingStore.getSnapshot().get(key);
    if (previous?.phase === "SENDING") return;
    pendingStore.put(key, {
      intent,
      phase: "SENDING",
      receipt: null
    });
    try {
      const receipt = await api.recordDatedCapacity(caseId, intent);
      if (receipt.run_id !== intent.run_id || receipt.command_id !== intent.command_id || receipt.idempotency_key !== intent.idempotency_key || receipt.revision !== intent.expected_revision + 1) throw Error("Reçu discordant");
      pendingStore.put(key, {
        intent,
        phase: "READ_REQUIRED",
        receipt
      });
    } catch (failure) {
      const status = (failure as {
        status?: number;
      }).status;
      if (status === 422 && !previous) {
        pendingStore.remove(key);
        setValidationError("Saisie refusée sans enregistrement : vérifiez les champs puis confirmez à nouveau.");
        return;
      }
      pendingStore.put(key, {
        intent,
        phase: status === 409 ? "CONFLICT" : "UNKNOWN",
        receipt: null
      });
    }
  }
  function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!data || pending || !confirmed) return;
    setValidationError("");
    try {
      const intent: CapacityInput = {
        command_id: crypto.randomUUID(),
        idempotency_key: crypto.randomUUID(),
        run_id: crypto.randomUUID(),
        expected_revision: data.revision,
        context_sha256: data.context_sha256,
        demands: demandsKnown ? demands.map(row => toRow(row, true)) : null,
        supplies: suppliesKnown ? supplies.map(row => toRow(row, false)) : null,
        justification: why.trim(),
        human_confirmed: true
      };
      setConfirmed(false);
      void send(intent);
    } catch (failure) {
      setValidationError((failure as Error).message);
    }
  }
  function rows(title: string, items: EditRow[], setRows: (rows: EditRow[]) => void, demand: boolean) {
    return <>
    <h3>{title}</h3>
    {items.map((row, index) => <fieldset key={row.id}><legend>{demand ? "Besoin" : "Disponibilité"} {index + 1}</legend>
      {([['label', 'libellé'], ['kind', 'type de ressource'], ['units', 'unités'], ['start', 'début inclus'], ['end', 'fin exclue'], ['reference', 'source'], ['revision', 'révision source'], ['locator', 'repère source']] as const).map(([field, label]) => <label key={field}>{label}<input aria-label={`${demand ? "Besoin" : "Disponibilité"} ${index + 1} — ${label}`} type={field === "start" || field === "end" ? "date" : field === "units" ? "number" : "text"} min={field === "units" ? demand ? 1 : 0 : undefined} max={field === "units" ? 10000 : undefined} step={field === "units" ? 1 : undefined} required={field === "label"} maxLength={field === "label" ? 200 : field === "kind" ? 100 : 500} value={row[field]} onChange={e => {
            setConfirmed(false);
            setRows(items.map(item => item.id === row.id ? {
              ...item,
              [field]: e.target.value
            } : item));
          }} /></label>)}
      {demand && <label>Ressource nommée<select aria-label={`Besoin ${index + 1} — ressource nommée`} value={row.named} onChange={e => {
            setConfirmed(false);
            setRows(items.map(item => item.id === row.id ? {
              ...item,
              named: e.target.value
            } : item));
          }}><option value="">Générique, remplaçable</option>{supplies.map(supply => <option key={supply.id} value={supply.id}>{supply.label || supply.id}</option>)}{row.named && !supplies.some(s => s.id === row.named) && <option value={row.named}>Ressource absente — conflit à revoir</option>}</select></label>}
      <button className="secondary-button" type="button" onClick={() => {
          setConfirmed(false);
          setRows(items.filter(item => item.id !== row.id));
        }}>Retirer {demand ? "le besoin" : "la disponibilité"} {index + 1}</button>
    </fieldset>)}
    <button className="secondary-button" type="button" disabled={items.length >= 100} onClick={() => {
        setConfirmed(false);
        setRows([...items, empty()]);
        if (demand) setDemandsKnown(true);else setSuppliesKnown(true);
      }}>Ajouter {demand ? "un besoin" : "une disponibilité"}</button>
  </>;
  }
  return <section className="section-block scenario-creation" aria-label="Planification de capacité">
    <h2>Capacité datée de l’Affaire</h2>
    <p>Proposition à partir de sources déclarées. Dates : début inclus, fin exclue. Une disponibilité représente une ressource ou équipe distincte, à capacité constante sur sa période. Aucune réservation, aucun prix ni porte déduits. Couverture globale : UNKNOWN.</p>
    {pending ? <div role="status"><p>{pending.phase === "UNKNOWN" ? "UNKNOWN — résultat de l’envoi inconnu. Les données et identifiants sont figés." : pending.phase === "SENDING" ? "Enregistrement en cours…" : "Relecture du calcul nécessaire."}</p>{pending.phase === "UNKNOWN" && <button className="secondary-button" onClick={() => void send(pending.intent)}>Réessayer le même envoi</button>}{(pending.phase === "READ_REQUIRED" || pending.phase === "CONFLICT") && <button className="secondary-button" onClick={() => setRefresh(n => n + 1)}>Réessayer la lecture</button>}</div> : <>
      {!loaded && <p role="status">Lecture du plan…</p>}
      {data && <><p>Révision {data.revision} — {data.state}</p>{data.current ? <Plan run={data.current} /> : <p>{data.state === "REVIEW_REQUIRED" ? "Plan à revoir après changement du contexte. Historique conservé." : "Aucun plan enregistré."}</p>}
      {data.current && <button className="secondary-button" type="button" onClick={() => {
          const input = data.current!.inputs;
          setDemands((input.demands ?? []).map(fromRow));
          setSupplies((input.supplies ?? []).map(fromRow));
          setDemandsKnown(input.demands !== null);
          setSuppliesKnown(input.supplies !== null);
          setConfirmed(false);
        }}>Reprendre les entrées du plan courant</button>}
      <form onSubmit={submit}><p>Champs absents : UNKNOWN. Types de ressource comparés exactement. Besoins indivisibles, sans changement d’équipe sur leur période. Les charges des autres Affaires, congés et déplacements doivent être inclus dans les disponibilités déclarées ; ils ne sont pas importés automatiquement.</p>
        <label><input type="checkbox" checked={demandsKnown} onChange={e => {
              setConfirmed(false);
              setDemandsKnown(e.target.checked);
            }} />Liste des besoins renseignée (vide = aucun besoin déclaré)</label>
        {demandsKnown && rows("Besoins", demands, setDemands, true)}{!demandsKnown && <button className="secondary-button" type="button" onClick={() => {
            setDemandsKnown(true);
            setDemands([empty()]);
            setConfirmed(false);
          }}>Ajouter un besoin</button>}
        <label><input type="checkbox" checked={suppliesKnown} onChange={e => {
              setConfirmed(false);
              setSuppliesKnown(e.target.checked);
            }} />Liste des disponibilités renseignée (vide = aucune disponibilité déclarée)</label>
        {suppliesKnown && rows("Disponibilités", supplies, setSupplies, false)}{!suppliesKnown && <button className="secondary-button" type="button" onClick={() => {
            setSuppliesKnown(true);
            setSupplies([empty()]);
            setConfirmed(false);
          }}>Ajouter une disponibilité</button>}
        <label>Justification du plan de capacité<input required maxLength={2000} value={why} onChange={e => {
              setConfirmed(false);
              setWhy(e.target.value);
            }} /></label>
        <label><input type="checkbox" checked={confirmed} onChange={e => setConfirmed(e.target.checked)} />Je confirme ces entrées et le calcul proposé pour cette Affaire. MFA requise.</label>
        <button className="primary-button" type="submit" disabled={!confirmed || !why.trim()}>Enregistrer et calculer</button>
      </form>
      {data.history.length > 0 && <details><summary>Historique des calculs</summary>{data.history.map(run => <Plan key={run.run_id} run={run} />)}{data.history_has_more && <p>Historique limité aux vingt derniers calculs.</p>}</details>}
      </>}
    </>}
    {error && <p role="alert">{error}</p>}
    {validationError && <p role="alert">{validationError}</p>}
    {!pending && <button className="secondary-button" type="button" onClick={() => setRefresh(n => n + 1)}>Relire le plan</button>}
  </section>;
}
function Plan({
  run
}: {
  run: CapacityRun;
}) {
  const demands = run.inputs.demands ?? [],
    supplies = run.inputs.supplies ?? [];
  return <div className="detail-panel"><h3>Calcul {run.revision} — {run.status} — {run.state}</h3><p>Source déclarée humainement — {run.inputs.justification}</p>
    {run.status === "INFEASIBLE" && <p>Affectation complète impossible avec ces entrées. Les besoins non affectés doivent être revus ; les diagnostics agrégés ne décrivent pas nécessairement toutes les causes.</p>}
    {run.status === "UNKNOWN" && <p>UNKNOWN — données ou résultat insuffisants. Aucune affectation présumée.</p>}
    <div className="line-table-wrap" tabIndex={0} role="region" aria-label={`Besoins et affectations du calcul ${run.revision}, défilement horizontal`}><table><thead><tr><th>Besoin</th><th>Type / unités</th><th>Période</th><th>Source / révision / repère</th><th>Affectation proposée</th></tr></thead><tbody>{demands.map(row => <tr key={row.id}><td>{row.label}</td><td>{row.resource_type ?? "UNKNOWN"} / {row.units ?? "UNKNOWN"}</td><td>{row.start ?? "UNKNOWN"} → {row.end ?? "UNKNOWN"}</td><td>{row.source ? `${row.source.reference} / ${row.source.revision} / ${row.source.locator}` : "UNKNOWN"}</td><td>{supplies.find(s => s.id === run.result.assignments.find(a => a.demand_id === row.id)?.supply_id)?.label ?? "Non affecté / UNKNOWN"}</td></tr>)}</tbody></table></div>
    <details className="case-resolution-sources"><summary>Disponibilités et provenance</summary>{run.inputs.supplies === null ? <p>UNKNOWN</p> : supplies.length === 0 ? <p>Aucune disponibilité déclarée.</p> : <ul>{supplies.map(row => <li key={row.id}>{row.label} — {row.resource_type ?? "UNKNOWN"} / {row.units ?? "UNKNOWN"} — {row.start ?? "UNKNOWN"} → {row.end ?? "UNKNOWN"} — {row.source ? `${row.source.reference} / ${row.source.revision} / ${row.source.locator}` : "source UNKNOWN"}</li>)}</ul>}<p>Empreinte des entrées : {run.input_sha256}</p></details>
    {run.result.conflicts.length > 0 && <ul aria-label="Diagnostics de surcharge">{run.result.conflicts.map((conflict, index) => <li key={index}>{conflict.period.start} → {conflict.period.end} — {conflict.resource_type} : besoin {conflict.required_units}, disponible {conflict.available_units}.</li>)}</ul>}
  </div>;
}
