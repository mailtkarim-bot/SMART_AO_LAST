import { useEffect, useLayoutEffect, useCallback, useRef, useState, useSyncExternalStore, type FormEvent } from "react";
import type { ApiClient } from "../../infrastructure/api";
import type { PositionCostSource, PositionHistory, PositionReviewInput, PositionRequirementSource, PositionOfferSource, PositionScopeSource, PricingPosition, PricingPositions } from "../../shared/types";
import { PricingPositionPendingStore, type PositionPending } from "./pricingPositionPending";
import { formatPositionMoney } from "./positionMoney";
type Props = {
  api: ApiClient;
  enabled: boolean;
  caseId: string;
  batchId: string;
  ownerKey: string;
  scopeKey: string;
  pendingStore: PricingPositionPendingStore;
};
type Draft = {
  scope: string;
  row: PricingPosition;
  input: PositionReviewInput;
  confirmed: boolean;
  selected: {
    costs: PositionCostSource[];
    requirement: PositionRequirementSource | null;
    offer: PositionOfferSource | null;
    scope: PositionScopeSource | null;
  };
};
const transportLabels:Record<string,string>={UNKNOWN:"UNKNOWN",INCLUDED:"Inclus",EXCLUDED:"Exclu",SEPARATE:"Chiffré séparément"};
const limitLabels: Record<string, string> = {
  IMPORTED_DCE_ORIGIN_UNKNOWN: "Origine du fichier dans le DCE : UNKNOWN",
  NO_DCE_REQUIREMENT: "Obligation DCE non reliée",
  NO_REGISTERED_COST: "Aucun coût enregistré",
  NO_PARTNER_OFFER: "Offre partenaire non reliée",
  COST_REUSE_REVIEW_REQUIRED: "Coût réutilisé sur plusieurs postes : arbitrage nécessaire",
  CURRENCY_MISMATCH: "Devises différentes : aucun total converti",
  MULTIPLE_COST_BASES_REVIEW_REQUIRED: "Plusieurs bases financières : somme à qualifier",
  IMPORTED_UNIT_UNKNOWN: "Unité importée inconnue",
  UNIT_SCOPE_REVIEW_REQUIRED: "Unités et périmètre à revoir",
  QUANTITY_SCOPE_REVIEW_REQUIRED: "Quantités différentes : périmètre à revoir",
  OFFER_TOTAL_IS_NOT_POSITION_COST: "Le montant global de l’offre ne constitue pas un coût de poste",
  OFFER_CURRENCY_MISMATCH: "Devise de l’offre différente de celle des coûts",
  OFFER_VALIDITY_UNKNOWN: "Validité du devis inconnue",
  OFFER_EXPIRED: "Devis expiré",
  OFFER_EXCLUSIONS_UNKNOWN: "Exclusions de l’offre inconnues",
  OFFER_EXCLUSIONS_PRESENT: "Exclusions déclarées à traiter",
  TRANSPORT_UNKNOWN: "Transport non qualifié",
  TRANSPORT_NOT_INCLUDED: "Transport exclu ou chiffré séparément",
  SOURCE_REVIEW_REQUIRED: "Sources à revalider : REVIEW_REQUIRED",
  COST_TOTAL_OUT_OF_RANGE: "Total hors des limites monétaires",
  PARTNER_SCOPE_REVIEW_REQUIRED: "Revue de périmètre partenaire à clarifier",
  EXCLUSIONS_REVIEW_REQUIRED: "Relecture des exclusions non établie"
};
type PositionFacts = Pick<PricingPosition, "declared_cost_minor" | "currency_code" | "requirement" | "costs" | "offer" | "scope" | "review_id" | "revision" | "state" | "justification">;
function Facts({
  row
}: {
  row: PositionFacts;
}) {
  return <><p>Somme des coûts enregistrés rattachés : {formatPositionMoney(row.declared_cost_minor, row.currency_code)} · Couverture : UNKNOWN</p>{row.requirement && <details><summary>Obligation DCE · révision {row.requirement.revision}</summary><blockquote>{row.requirement.excerpt ?? "Extrait UNKNOWN — consultez la source"}</blockquote><p>Document {row.requirement.source_anchor.dce_document_id} · version {row.requirement.source_anchor.dce_version_id} · région octets {row.requirement.start_byte_offset}–{row.requirement.end_byte_offset}</p></details>}{row.costs.map(cost => <p key={cost.line_id}>{cost.label} · {cost.quantity_decimal} {cost.unit} · {formatPositionMoney(cost.amount_minor, cost.currency_code)} · Rapport source {cost.report_id} · révision {cost.report_revision} · {cost.report_state}{cost.allocated_amount_minor !== undefined && <> · Affecté à ce poste : {formatPositionMoney(cost.allocated_amount_minor, cost.currency_code)}</>}</p>)}{row.costs.some(cost => cost.report_state === "PUBLISHED") && <p>La répartition déclarée est distincte des totaux du rapport publié ; elle ne les modifie pas et ne prouve pas la couverture.</p>}{row.offer && <details><summary>Offre : {row.offer.partner_label} · prix révision {row.offer.revision}</summary><p>Montant global déclaré : {row.offer.amount_as_declared} {row.offer.currency_code} · Validité : {row.offer.valid_until ?? "UNKNOWN"}</p><p>Source déclarée : {row.offer.source_locator} · reçu révision {row.offer.receipt_revision}</p><p>Exclusions : {row.offer.exclusions_state === "UNKNOWN" ? "UNKNOWN" : row.offer.exclusions.length ? row.offer.exclusions.join(" ; ") : "Aucune exclusion déclarée"}</p><p>Transport : {transportLabels[row.scope?.transport_state??"UNKNOWN"]??"UNKNOWN"} · {row.scope?.transport_note ?? "Note UNKNOWN"}</p></details>}{row.review_id && <p>Rapprochement · révision {row.revision} · {row.state === "CURRENT" ? "sources relues" : "à revalider"} · {row.justification ?? "Justification historique à consulter"}</p>}</>;
}
export function PricingPositionsPanel({
  api,
  enabled,
  caseId,
  batchId,
  ownerKey,
  scopeKey,
  pendingStore
}: Props) {
  const snapshot = useSyncExternalStore(pendingStore.subscribe, pendingStore.getSnapshot);
  const prefix = JSON.stringify([ownerKey, caseId, batchId]);
  const ctx = JSON.stringify([prefix, scopeKey]);
  const current = useRef(ctx);
  const sequence = useRef(0);
  const active = useRef(new Set<string>());
  const [loaded, setLoaded] = useState<{
    scope: string;
    value: PricingPositions;
  } | null>(null);
  const [status, setStatus] = useState<"LOADING" | "READY" | "ERROR">("LOADING");
  const [scopedNotice,setScopedNotice]=useState<{scope:string;text:string}|null>(null);
  const notice=scopedNotice?.scope===ctx?scopedNotice.text:"";
  function setNotice(text:string){setScopedNotice({scope:ctx,text});}
  const [offset, setOffset] = useState(0);
  const [search, setSearch] = useState("");
  const queryKey = JSON.stringify([ctx, offset, search]);
  const currentQuery = useRef(queryKey);
  const [searchInput, setSearchInput] = useState("");
  const [draft, setDraft] = useState<Draft | null>(null);
  const [history, setHistory] = useState<{
    scope: string;
    positionId: string;
    data: PositionHistory;
  } | null>(null);
  const [form, setForm] = useState<{
    scope: string;
    positionId: string;
    costs: string[];
    amounts: Record<string,string>;
    requirement: string;
    offer: string;
    review: string;
    why: string;
  } | null>(null);
  const entries = [...snapshot.entries()].filter(([key]) => JSON.parse(key)[0] === prefix);
  const locked = entries.some(([, v]) => v.phase === "UNKNOWN" || v.phase === "SENDING");
  const anyPending = entries.length > 0;
  useLayoutEffect(() => {
    current.current = ctx;
    currentQuery.current = queryKey;
  }, [ctx, queryKey]);
  const valid = useCallback((value: PricingPositions, positionId?: string) => value?.case_id === caseId && value.batch_id === batchId && Array.isArray(value.positions) && value.positions.every(p => p.import_source.batch_id === batchId && p.position_id === p.import_source.position_id) && (!positionId || value.positions[0]?.position_id === positionId), [caseId, batchId]);
  async function load(positionId?: string) {
    if (!enabled || !caseId || !batchId || [...pendingStore.getSnapshot()].some(([key, v]) => JSON.parse(key)[0] === prefix && (v.phase === "UNKNOWN" || v.phase === "SENDING"))) return null;
    const generation = ++sequence.current;
    const scope = ctx;
    const query = queryKey;
    setStatus("LOADING");
    try {
      const value = positionId ? await api.getPricingPosition(caseId, batchId, positionId) : await api.getPricingPositions(caseId, batchId, offset, search);
      if (current.current !== scope || sequence.current !== generation) return null;
      if (!valid(value, positionId)) throw Error("Sources discordantes");
      if (!positionId) {
        if (currentQuery.current !== query) return null;
        setLoaded({
          scope: query,
          value
        });
        setStatus("READY");
      }
      return value;
    } catch {
      if (current.current === scope && sequence.current === generation) {
        setLoaded(null);
        setStatus("ERROR");
      }
      return null;
    }
  }
  useEffect(() => {
    let live = true;
    const scope = ctx;
    const generation = ++sequence.current;
    if (!enabled || !caseId || !batchId) return;
    setStatus("LOADING");
    setLoaded(null);
    setHistory(null);
    if ([...pendingStore.getSnapshot()].some(([key, v]) => JSON.parse(key)[0] === prefix && (v.phase === "UNKNOWN" || v.phase === "SENDING"))) return;
    void api.getPricingPositions(caseId, batchId, offset, search).then(value => {
      if (!live || current.current !== scope || currentQuery.current !== queryKey || sequence.current !== generation) return;
      if (!valid(value)) throw Error("scope");
      setLoaded({
        scope: queryKey,
        value
      });
      setStatus("READY");
    }).catch(() => {
      if (live && current.current === scope && sequence.current === generation) {
        setLoaded(null);
        setStatus("ERROR");
      }
    });
    return () => {
      live = false;
    };
  }, [api, enabled, caseId, batchId, ctx, offset, search, pendingStore, prefix, queryKey, valid]);
  const value = enabled && !locked && status === "READY" && loaded?.scope === queryKey ? loaded.value : null;
  const editing = value && form?.scope === ctx ? value.positions.find(p => p.position_id === form.positionId) : null;
  const review = draft?.scope === ctx ? draft : null;
  async function reconcile(key: string, entry: PositionPending) {
    const value = await load(entry.positionId);
    if (!value || current.current !== ctx) return;
    const row = value.positions[0];
    if (entry.phase === "CONFLICT" || entry.receipt && (row.review_id === entry.intent.record_id && row.revision === entry.receipt.revision || row.revision > entry.receipt.revision)) {
      pendingStore.remove(key);
      setDraft(null);
      setForm(null);
      void load();
      setNotice(entry.phase === "CONFLICT" ? "Conflit relu : préparez une nouvelle révision depuis les sources actuelles." : row.state === "CURRENT" ? "Rapprochement enregistré et relu. Couverture économique : UNKNOWN." : "Acte enregistré; sources à revalider avant toute utilisation.");
    } else {
      pendingStore.put(key, {
        ...entry,
        message: "Relecture discordante ou ancienne : UNKNOWN. Seule une nouvelle relecture est permise."
      });
    }
  }
  async function send(key: string, entry: PositionPending) {
    if (active.current.has(key) || !enabled) return;
    active.current.add(key);
    const wasUnknown = entry.phase === "UNKNOWN";
    pendingStore.put(key, {
      ...entry,
      phase: "SENDING",
      message: "Enregistrement en cours…"
    });
    try {
      const receipt = await api.recordPricingPosition(entry.caseId, entry.batchId, entry.positionId, entry.intent);
      if (receipt.command_id !== entry.intent.command_id || receipt.idempotency_key !== entry.intent.idempotency_key || receipt.record_id !== entry.intent.record_id || receipt.position_id !== entry.positionId || receipt.revision !== entry.intent.expected_revision + 1) {
        pendingStore.put(key, {
          ...entry,
          phase: "UNKNOWN",
          message: "Réponse discordante : UNKNOWN. Intention figée, retry exact uniquement."
        });
        return;
      }
      const acknowledged = {
        ...entry,
        phase: "READ_REQUIRED" as const,
        receipt,
        message: "Reçu obtenu : relecture de l’acte nécessaire."
      };
      pendingStore.put(key, acknowledged);
      if (current.current === ctx) await reconcile(key, acknowledged);
    } catch (error) {
      const code = (error as {
        status?: number;
      })?.status;
      if (code === 409) {
        const conflict = {
          ...entry,
          phase: "CONFLICT" as const,
          message: "409 : relecture nécessaire avant une nouvelle intention."
        };
        pendingStore.put(key, conflict);
        if (current.current === ctx) await reconcile(key, conflict);
      } else if (!wasUnknown && code !== undefined && code >= 400 && code < 500) {
        pendingStore.remove(key);
        if (current.current === ctx) setNotice("Déclaration refusée : vérifiez vos droits/MFA et les sources choisies.");
      } else {
        pendingStore.put(key, {
          ...entry,
          phase: "UNKNOWN",
          message: "Résultat UNKNOWN : l’intention reste figée. Rejouez exactement après rétablissement des droits/MFA si nécessaire."
        });
      }
    } finally {
      active.current.delete(key);
    }
  }
  function prepare(event: FormEvent) {
    event.preventDefault();
    if (!editing || !value || !form || anyPending || !form.why.trim()) return;
    if (form.costs.length > 20) {
      setNotice("Sélectionnez au maximum20coûts par rapprochement.");
      return;
    }
    const knownCosts = [...editing.costs, ...value.sources.costs];
    const unique = [...new Map(knownCosts.map(c => [c.line_id, c])).values()];
    const costs = unique.filter(c => form.costs.includes(c.line_id));
    const req = value.sources.requirements.find(r => r.requirement_id === form.requirement);
    const offer = value.sources.offers.find(o => o.price_id === form.offer);
    const scope = value.sources.scopes.find(s => s.review_id === form.review && s.receipt_event_id === offer?.receipt_event_id);
    if (costs.some(c => form.amounts[c.line_id] && (!/^(0|[1-9][0-9]{0,18})$/.test(form.amounts[c.line_id]) || BigInt(form.amounts[c.line_id]) > BigInt(c.amount_minor)))) {
      setNotice("Le montant affecté doit être un entier positif ou nul, inférieur ou égal au coût source.");
      return;
    }
    const input: PositionReviewInput = {
      command_id: crypto.randomUUID(),
      idempotency_key: crypto.randomUUID(),
      record_id: crypto.randomUUID(),
      expected_revision: editing.revision,
      position_context_sha256: editing.position_context_sha256,
      cost_refs: costs.map(c => ({
        line_id: c.line_id,
        report_revision: c.report_revision,
        ...(form.amounts[c.line_id] ? {allocated_amount_minor:form.amounts[c.line_id]} : {})
      })),
      requirement_id: req?.requirement_id ?? null,
      requirement_revision: req?.revision ?? null,
      offer_price_id: offer?.price_id ?? null,
      offer_price_revision: offer?.revision ?? null,
      scope_review_id: scope?.review_id ?? null,
      justification: form.why.trim(),
      human_confirmed: true
    };
    if (costs.length !== form.costs.length || form.requirement && !req || form.offer && !offer || form.review && !scope) {
      setNotice("Une source sélectionnée n’est plus actuelle : vérifiez les choix avant de préparer.");
      return;
    }
    setDraft({
      scope: ctx,
      row: editing,
      input,
      confirmed: false,
      selected: {
        costs: costs.map(c => ({...c, allocated_amount_minor:form.amounts[c.line_id] || undefined})),
        requirement: req ?? null,
        offer: offer ?? null,
        scope: scope ?? null
      }
    });
  }
  async function showHistory(row: PricingPosition, before?: number) {
    const scope = ctx;
    try {
      const result = await api.getPricingPositionHistory(caseId, batchId, row.position_id, before);
      if (current.current !== scope || result.case_id !== caseId || result.batch_id !== batchId || result.position_id !== row.position_id) return;
      setHistory({
        scope,
        positionId: row.position_id,
        data: result
      });
    } catch {
      if (current.current === scope) setNotice("Historique indisponible : UNKNOWN.");
    }
  }
  if (!enabled) return null;
  return <section className="section-block" aria-label="Chiffrage sourcé par poste"><h2>Chiffrage sourcé par poste</h2><p>Couverture économique : UNKNOWN · Applicabilité : UNKNOWN. Les montants d’offres globaux et les prix importés ne sont pas des coûts de poste.</p>{notice && <p role="status">{notice}</p>}
 {entries.map(([key, entry]) => <div className="detail-panel" key={key}><p role="status">{entry.message}</p><p>Intention : {entry.intent.justification}</p>{entry.phase === "UNKNOWN" ? <button type="button" className="secondary-button" onClick={() => void send(key, entry)}>Rejouer exactement cette intention</button> : entry.phase !== "SENDING" ? <button type="button" className="secondary-button" onClick={() => void reconcile(key, entry)}>Relire uniquement après le reçu ou le conflit</button> : null}</div>)}
 {!caseId || !batchId ? <p>Importez ou choisissez un aperçu financier de l’Affaire pour consulter ses postes.</p> : <><div className="form-actions"><label>Rechercher un coût enregistré<input value={searchInput} disabled={anyPending || !!review} onChange={e => setSearchInput(e.target.value)} maxLength={120} /></label><button type="button" className="secondary-button" disabled={anyPending || !!review} onClick={() => {
          setNotice("");setForm(null);setDraft(null);if (search !== searchInput) setSearch(searchInput);else void load();
        }}>Actualiser les postes et sources</button></div>{!locked && status === "LOADING" && <p role="status">Chargement des postes…</p>}{!locked && status === "ERROR" && <p role="alert">Sources indisponibles ou discordantes : UNKNOWN.</p>}
 {value && <>{Object.values(value.sources_limited).some(Boolean) && <p role="status">Listes de sources limitées ou indisponibles : affinez la recherche et consultez les registres avant toute conclusion.</p>}<p>Le tableau peut défiler horizontalement. Les postes affichés ne constituent pas une couverture complète du chiffrage.</p><div className="line-table-wrap" role="region" aria-label="Postes et coûts — tableau défilant" tabIndex={0}><table><caption>Postes importés, coûts rattachés et limites</caption><thead><tr><th scope="col">Poste et source</th><th scope="col">Coûts et sources enregistrés</th><th scope="col">Limites</th><th scope="col">Revue</th></tr></thead><tbody>{value.positions.map(row => <tr key={row.position_id}><td><strong>{row.import_source.designation ?? "Poste sans désignation"}</strong><p>{row.import_source.source_locator ? `${row.import_source.source_locator.sheet} · ligne ${row.import_source.source_locator.row} · cellules ${Object.values(row.import_source.source_locator.cells).join(", ")}` : "Source de cellule UNKNOWN"}</p><p>{row.import_origin?.state === "MATCHED_BY_HASH" ? `Origine DCE : ${row.import_origin.filename} · version ${row.import_origin.dce_version_id}` : "Origine DCE du fichier : UNKNOWN"}</p><p>{row.import_source.quantity_decimal ?? "UNKNOWN"} {row.import_source.unit ?? "unité UNKNOWN"} · Prix importé : {formatPositionMoney(row.import_source.total_minor, null)}</p></td><td><Facts row={row} /></td><td><ul>{row.limitations.map(reason => <li key={reason}>{limitLabels[reason] ?? "Limite à qualifier"}</li>)}</ul></td><td><button type="button" className="secondary-button" disabled={anyPending || !!review || row.source_state !== "CURRENT_SOURCE"} onClick={() => {
                    setDraft(null);
                    setForm({
                      scope: ctx,
                      positionId: row.position_id,
                      costs: row.state === "CURRENT" ? row.costs.map(c => c.line_id) : [],
                      amounts: Object.fromEntries(row.state === "CURRENT" ? row.costs.filter(c => c.allocated_amount_minor !== undefined).map(c => [c.line_id,c.allocated_amount_minor!]) : []),
                      requirement: row.requirement?.requirement_id ?? "",
                      offer: row.offer?.price_id ?? "",
                      review: row.scope?.review_id ?? "",
                      why: ""
                    });
                  }}>Rapprocher ce poste</button><button type="button" className="secondary-button" disabled={anyPending || !!review} onClick={() => void showHistory(row)}>Historique du poste</button></td></tr>)}</tbody></table></div><nav aria-label="Pagination des postes"><button type="button" className="secondary-button" disabled={anyPending || !!review || value.offset === 0} onClick={() => setOffset(Math.max(0, value.offset - 50))}>Postes précédents</button><button type="button" className="secondary-button" disabled={anyPending || !!review || value.next_offset === null} onClick={() => setOffset(value.next_offset!)}>Postes suivants</button></nav>
 {editing && form && !review && !anyPending && <form className="detail-panel decision-form" aria-label="Préparer un rapprochement de poste" onSubmit={prepare}><h3>Rapprocher : {editing.import_source.designation}</h3><label>Obligation DCE confirmée<select value={form.requirement} onChange={e => setForm({
              ...form,
              requirement: e.target.value
            })}><option value="">Non reliée — UNKNOWN</option>{value.sources.requirements.map(r => <option key={r.requirement_id} value={r.requirement_id}>{r.excerpt ?? r.native_type} · révision {r.revision}</option>)}</select></label><label>Coûts enregistrés à rattacher<select multiple value={form.costs} onChange={e => setForm({
              ...form,
              costs: [...e.target.selectedOptions].map(o => o.value)
            })}>{[...new Map([...editing.costs, ...value.sources.costs].map(c => [c.line_id, c])).values()].map((c: PositionCostSource) => <option key={c.line_id} value={c.line_id}>{c.label} · {c.quantity_decimal} {c.unit} · {formatPositionMoney(c.amount_minor, c.currency_code)} · rapport révision {c.report_revision}</option>)}</select></label>{[...new Map([...editing.costs, ...value.sources.costs].map(c => [c.line_id, c])).values()].filter(c => form.costs.includes(c.line_id)).map(c => <div key={c.line_id}><label>Montant affecté à {c.label} (unités mineures {c.currency_code})<input inputMode="numeric" pattern="0|[1-9][0-9]{0,18}" maxLength={19} value={form.amounts[c.line_id] ?? ""} onChange={e => setForm({...form, amounts:{...form.amounts,[c.line_id]:e.target.value}})} /></label><p>Coût source : {formatPositionMoney(c.amount_minor,c.currency_code)}. Laissez vide pour un rattachement sans répartition ; aucune affectation automatique.</p><p>Déjà affecté : {formatPositionMoney(c.allocation_summary?.allocated_amount_minor ?? null,c.currency_code)} · Restant non affecté : {formatPositionMoney(c.allocation_summary?.remaining_amount_minor ?? null,c.currency_code)}{c.allocation_summary?.unresolved_reference_count ? " · Rattachements à requalifier" : ""}</p></div>)}{!value.sources.costs.length && <p>Aucun coût disponible. Utilisez la saisie financière existante puis actualisez les sources. Aucun zéro ne sera déduit.</p>}<label>Offre partenaire<select value={form.offer} onChange={e => setForm({
              ...form,
              offer: e.target.value,
              review: ""
            })}><option value="">Non reliée — UNKNOWN</option>{value.sources.offers.map(o => <option key={o.price_id} value={o.price_id}>{o.partner_label} · montant global {o.amount_as_declared} {o.currency_code} · prix révision {o.revision}</option>)}</select></label><label>Revue de périmètre et transport<select value={form.review} onChange={e => setForm({
              ...form,
              review: e.target.value
            })}><option value="">Non qualifié — UNKNOWN</option>{value.sources.scopes.filter(s => s.receipt_event_id === value.sources.offers.find(o => o.price_id === form.offer)?.receipt_event_id).map(s => <option key={`${s.review_id}:${s.receipt_event_id}`} value={s.review_id}>Révision {s.revision} · transport {transportLabels[s.transport_state]??"UNKNOWN"} · {s.transport_note ?? "note UNKNOWN"}</option>)}</select></label><label>Justification du rapprochement<textarea value={form.why} onChange={e => setForm({
              ...form,
              why: e.target.value
            })} required maxLength={2000} /></label><p>Précisez les hypothèses de répartition, le périmètre retenu et les manques. Une somme partielle ne prouve pas la couverture.</p><button className="primary-button" type="submit">Vérifier les choix</button></form>}
 {review && !anyPending && <div className="detail-panel"><h3>Vérifier le rapprochement de {review.row.import_source.designation}</h3><p>{review.input.cost_refs.length} coût(s) enregistré(s) sélectionné(s). Aucun montant d’offre n’est affecté automatiquement.</p><p>{review.input.justification}</p><Facts row={{
            ...review.row,
            ...review.selected,
            declared_cost_minor: null,
            currency_code: null,
            review_id: null
          }} /><p>Couverture économique : UNKNOWN · Applicabilité : UNKNOWN · MFA requis pour enregistrer.</p><label><input type="checkbox" checked={review.confirmed} onChange={e => setDraft({
              ...review,
              confirmed: e.target.checked
            })} />Je confirme ce rapprochement humain et ses limites UNKNOWN</label><button type="button" className="primary-button" disabled={!review.confirmed} onClick={() => {
            const key = JSON.stringify([prefix, review.row.position_id]);
            if (pendingStore.getSnapshot().has(key)) return;
            void send(key, {
              caseId,
              batchId,
              positionId: review.row.position_id,
              intent: review.input,
              phase: "SENDING",
              receipt: null,
              message: "Enregistrement en cours…"
            });
          }}>Enregistrer le rapprochement</button><button type="button" className="secondary-button" onClick={() => setDraft(null)}>Modifier les choix</button></div>}
 {history?.scope === ctx && <div className="detail-panel"><h3>Historique du poste</h3>{history.data.entries.map(entry => <details key={entry.record_id}><summary>Révision {entry.revision} · {entry.state === "HISTORICAL" ? "HISTORICAL — état enregistré antérieur" : "preuve inconnue"}</summary><p>{entry.justification ?? "UNKNOWN"} · {entry.created_at}</p>{entry.snapshot && <><p>Source historique : {entry.snapshot.import.source_locator ? `${entry.snapshot.import.source_locator.sheet} · ligne ${entry.snapshot.import.source_locator.row}` : "UNKNOWN"} · import révision {entry.snapshot.import.batch_revision}</p><Facts row={{
                ...entry.snapshot,
                declared_cost_minor: null,
                currency_code: null,
                review_id: null,
                revision: entry.revision,
                state: "REVIEW_REQUIRED",
                justification: entry.justification
              }} /></>}<p>Ces sources historiques ne sont pas transférées au courant.</p></details>)}{history.data.next_before_revision !== null && <button type="button" className="secondary-button" onClick={() => {
            const row = value.positions.find(p => p.position_id === history.positionId);
            if (row) void showHistory(row, history.data.next_before_revision!);
          }}>Révisions précédentes</button>}</div>}
 </>}</>}</section>;
}
