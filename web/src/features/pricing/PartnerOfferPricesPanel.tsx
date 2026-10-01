import { useEffect, useRef, useState, type FormEvent } from "react";

import type { ApiClient } from "../../infrastructure/api";
import type {
  DeclarePartnerOfferPriceInput,
  PartnerOfferPriceList,
  PartnerOfferPriceView,
} from "../../shared/types";
import { PartnerOfferScopeReviewsPanel } from "./PartnerOfferScopeReviewsPanel";

type ReadStatus = "LOADING" | "READY" | "FORBIDDEN" | "UNAVAILABLE" | "NO_CASE" | "INACTIVE";
type Failure = "UNCONFIRMED" | "REJECTED";
type Pending = { input: DeclarePartnerOfferPriceInput; failure?: Failure; message?: string };

function apiErrorStatus(error: unknown): number | undefined {
  const value = (error as { status?: unknown })?.status;
  return typeof value === "number" ? value : undefined;
}

export function PartnerOfferPricesPanel({
  api,
  caseId,
  enabled,
}: {
  api: ApiClient;
  caseId: string;
  enabled: boolean;
}) {
  const [status, setStatus] = useState<ReadStatus>(() => !enabled ? "INACTIVE" : caseId ? "LOADING" : "NO_CASE");
  const [list, setList] = useState<PartnerOfferPriceList | null>(null);
  const [pendingByReceipt, setPendingByReceipt] = useState<Record<string, Pending>>({});
  const [submittingByReceipt, setSubmittingByReceipt] = useState<Record<string, boolean>>({});
  const [writeMessage, setWriteMessage] = useState<string | null>(null);
  const pendingRef = useRef(new Map<string, Pending>());
  const inFlight = useRef(new Set<string>());
  const [reload, setReload] = useState(0);

  useEffect(() => {
    if (!enabled) {
      setStatus("INACTIVE");
      setList(null);
      return;
    }
    if (!caseId) {
      setStatus("NO_CASE");
      setList(null);
      return;
    }

    let active = true;
    setStatus("LOADING");
    setList(null);
    void api.listPartnerOfferPrices(caseId).then((result) => {
      if (!active) return;
      if (result.case_id !== caseId || !Array.isArray(result.offers)) {
        setStatus("UNAVAILABLE");
        return;
      }
      setList(result);
      setStatus("READY");
      setWriteMessage(null);
    }).catch((error: unknown) => {
      if (!active) return;
      setList(null);
      setStatus(apiErrorStatus(error) === 403 ? "FORBIDDEN" : "UNAVAILABLE");
    });
    return () => { active = false; };
  }, [api, caseId, enabled, reload]);

  async function declare(receiptEventId: string, values: { amount: string; currency: string }) {
    const key = `${caseId}:${receiptEventId}`;
    if (inFlight.current.has(key)) return;
    const existing = pendingRef.current.get(key);
    const input = existing?.input ?? {
      command_id: crypto.randomUUID(),
      idempotency_key: crypto.randomUUID(),
      correlation_id: crypto.randomUUID(),
      declaration_id: crypto.randomUUID(),
      expected_revision: list?.offers.find((offer) => offer.receipt_event_id === receiptEventId)?.declarations.at(-1)?.revision ?? 0,
      amount_as_declared: values.amount.trim(),
      currency_code: values.currency.trim().toUpperCase(),
    };
    const pending = { input };
    pendingRef.current.set(key, pending);
    setPendingByReceipt((current) => {
      const next = { ...current, [key]: pending };
      delete next[`${key}:rejected`];
      return next;
    });
    inFlight.current.add(key);
    setSubmittingByReceipt((current) => ({ ...current, [key]: true }));
    try {
      try {
        await api.declarePartnerOfferPrice(caseId, receiptEventId, input);
      } catch (error) {
        const responseStatus = apiErrorStatus(error);
        if (responseStatus === 409 || responseStatus === undefined || responseStatus >= 500) {
          const unconfirmed: Pending = {
            input,
            failure: "UNCONFIRMED",
            message: "Résultat non confirmé · le rejeu conserve les mêmes identifiants.",
          };
          pendingRef.current.set(key, unconfirmed);
          setPendingByReceipt((current) => ({ ...current, [key]: unconfirmed }));
        } else {
          pendingRef.current.delete(key);
          setPendingByReceipt((current) => {
            const next = { ...current };
            delete next[key];
            return next;
          });
          const rejected: Pending = {
            input,
            failure: "REJECTED",
            message: "Refus confirmé · aucun nouveau prix n’a été enregistré.",
          };
          setPendingByReceipt((current) => ({ ...current, [`${key}:rejected`]: rejected }));
        }
        return;
      }

      pendingRef.current.delete(key);
      setPendingByReceipt((current) => {
        const next = { ...current };
        delete next[key];
        return next;
      });
      setWriteMessage("Déclaration confirmée par le serveur · relecture de la comparaison en cours.");
      const refreshed = await api.listPartnerOfferPrices(caseId);
      if (refreshed.case_id === caseId && Array.isArray(refreshed.offers)) {
        setList(refreshed);
        setStatus("READY");
        setWriteMessage(null);
      } else {
        setList(null);
        setStatus("UNAVAILABLE");
        setWriteMessage("Déclaration confirmée par le serveur · projection à relire.");
      }
    } catch (error) {
      setList(null);
      setStatus("UNAVAILABLE");
      setWriteMessage("Déclaration confirmée par le serveur · projection à relire.");
    } finally {
      inFlight.current.delete(key);
      setSubmittingByReceipt((current) => ({ ...current, [key]: false }));
    }
  }

  const visibleList = status === "READY" && list?.case_id === caseId ? list : null;
  return (
    <section className="detail-panel" aria-label="Comparaison confidentielle des offres partenaires">
      <div className="panel-heading">
        <div>
          <h3>Offres partenaires · comparaison privée</h3>
          <p>Vue côte à côte des valeurs déclarées depuis C09 ; aucune comparabilité de périmètre, couverture, marge ou préférence n’est calculée.</p>
        </div>
        <button type="button" className="secondary-button" onClick={() => setReload((value) => value + 1)} disabled={!enabled || !caseId || status === "LOADING"}>
          {status === "LOADING" ? "Chargement…" : "Actualiser les offres"}
        </button>
      </div>
      {status === "INACTIVE" && <p role="status">Ouvrez C08 pour charger les valeurs financières privées.</p>}
      {status === "NO_CASE" && <p role="status">UNKNOWN · sélectionnez une Affaire.</p>}
      {status === "LOADING" && <p role="status">Chargement des offres reçues…</p>}
      {status === "FORBIDDEN" && <p role="status">FORBIDDEN · lecture financière réservée au Patron habilité.</p>}
      {status === "UNAVAILABLE" && <p role="status">UNAVAILABLE · la comparaison financière n’a pas pu être relue.</p>}
      {writeMessage && <p role="status">{writeMessage}</p>}
      {status === "READY" && visibleList?.offers.length === 0 && <p>UNKNOWN · aucun reçu partenaire dans cette Affaire.</p>}
      {visibleList && <div className="summary-grid partner-offer-grid">{visibleList.offers.map((offer) => {
        const key = `${caseId}:${offer.receipt_event_id}`;
        const pending = pendingByReceipt[key];
        const rejected = pendingByReceipt[`${key}:rejected`];
        return (
          <PartnerOfferCard
            key={offer.receipt_event_id}
            caseId={caseId}
            offer={offer}
            pending={pending}
            rejected={rejected}
            submitting={submittingByReceipt[key] === true}
            onDeclare={(values) => declare(offer.receipt_event_id, values)}
          />
        );
      })}</div>}
      {visibleList && (
        <PartnerOfferScopeReviewsPanel
          api={api}
          caseId={caseId}
          offers={visibleList.offers}
          enabled={enabled}
        />
      )}
    </section>
  );
}

function PartnerOfferCard({
  caseId,
  offer,
  pending,
  rejected,
  submitting,
  onDeclare,
}: {
  caseId: string;
  offer: PartnerOfferPriceView;
  pending?: Pending;
  rejected?: Pending;
  submitting: boolean;
  onDeclare: (values: { amount: string; currency: string }) => Promise<void>;
}) {
  const latest = offer.declarations.at(-1);
  const lockedInput = pending?.input;
  const [amount, setAmount] = useState(latest?.amount_as_declared ?? "");
  const [currency, setCurrency] = useState(latest?.currency_code ?? "");
  const canRetryUnknown = pending?.failure === "UNCONFIRMED";
  const inputLocked = !!lockedInput;
  const changed = amount.trim() !== (latest?.amount_as_declared ?? "")
    || currency.trim().toUpperCase() !== (latest?.currency_code ?? "");
  const prefix = `offer-price-${caseId}-${offer.receipt_event_id}`;

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onDeclare({
      amount: lockedInput?.amount_as_declared ?? amount,
      currency: lockedInput?.currency_code ?? currency,
    });
  }

  return (
    <article className="detail-panel">
      <h4>{offer.partner_label} · {partnerKindLabel(offer.partner_kind)} · reçu v{offer.partner_revision}{offer.is_latest_receipt ? " · courant" : " · historique"}</h4>
      <p>Source reçue : {offer.source_locator}</p>
      <p>Empreinte de la pièce : UNKNOWN · seul le locator déclaré dans C09 est conservé.</p>
      <p>Périmètre déclaré : {offer.source_rationale} · comparabilité : UNKNOWN</p>
      <p>Validité : {offer.validity_current}{offer.valid_until ? ` · jusqu’au ${offer.valid_until}` : ""} · exclusions : {offer.exclusions_state}{offer.exclusions.length ? ` · ${offer.exclusions.join("; ")}` : ""}</p>
      {offer.price_state === "UNKNOWN" ? (
        <p role="status">UNKNOWN · aucun montant déclaré pour ce reçu.</p>
      ) : (
        <div>
          {offer.declarations.map((declaration) => (
            <p key={declaration.declaration_id}>
              Révision {declaration.revision} : {declaration.amount_as_declared} {declaration.currency_code} · déclarée {declaration.created_at}
            </p>
          ))}
        </div>
      )}
      {offer.is_latest_receipt && (
        <form aria-label={`Déclarer le total de ${offer.partner_label}`} onSubmit={(event) => void submit(event)}>
          <label htmlFor={`${prefix}-amount`}>Total exactement déclaré par la source</label>
          <input
            id={`${prefix}-amount`}
            type="text"
            inputMode="decimal"
            required
            maxLength={80}
            value={lockedInput?.amount_as_declared ?? amount}
            disabled={inputLocked || submitting}
            onChange={(event) => setAmount(event.target.value)}
          />
          <small>Format sans séparateur de milliers, par exemple 1234,50. La valeur reste telle que déclarée.</small>
          <label htmlFor={`${prefix}-currency`}>Code devise source (3 lettres)</label>
          <input
            id={`${prefix}-currency`}
            type="text"
            autoCapitalize="characters"
            required
            minLength={3}
            maxLength={3}
            value={lockedInput?.currency_code ?? currency}
            disabled={inputLocked || submitting}
            onChange={(event) => setCurrency(event.target.value.toUpperCase())}
          />
          <button type="submit" disabled={submitting || (inputLocked && !canRetryUnknown) || (!changed && offer.price_state === "DECLARED")}>
            {submitting ? "Enregistrement…" : canRetryUnknown ? "Réessayer la déclaration" : latest ? "Déclarer une nouvelle révision" : "Déclarer le total source"}
          </button>
          {pending?.message && <p role="alert">{pending.message}</p>}
          {rejected?.message && <p role="alert">{rejected.message}</p>}
        </form>
      )}
      {!offer.is_latest_receipt && <p>Historique conservé ; une nouvelle déclaration se rattache au reçu courant.</p>}
      <p>La valeur est une déclaration financière Patron. Aucun coût couvert, classement, engagement ou GO P3 n’en est déduit.</p>
    </article>
  );
}

function partnerKindLabel(kind: PartnerOfferPriceView["partner_kind"]) {
  if (kind === "SUPPLIER") return "Fournisseur";
  if (kind === "SUBCONTRACTOR") return "Sous-traitant";
  return "Cotraitant";
}
