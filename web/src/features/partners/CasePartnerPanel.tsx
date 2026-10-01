import { useRef, useState, type FormEvent } from "react";

import type {
  CasePartnerEvent,
  CasePartnerEventList,
  CasePartnerKind,
  DeclareCasePartnerEngagementInput,
  RecordCasePartnerReceiptInput,
  RecordCasePartnerRequestInput,
} from "../../shared/types";
import type { CasePartnerReadStatus } from "./useCasePartnerEvents";

type Failure = "UNCONFIRMED" | "REJECTED";

type Props = {
  caseId: string;
  caseLabel: string;
  status: CasePartnerReadStatus;
  list: CasePartnerEventList | null;
  onRequest: (input: RecordCasePartnerRequestInput) => Promise<unknown>;
  onReceive: (input: RecordCasePartnerReceiptInput) => Promise<unknown>;
  onDeclareEngagement: (input: DeclareCasePartnerEngagementInput) => Promise<unknown>;
  onRefresh: () => void | Promise<void>;
};

export function CasePartnerPanel({
  caseId,
  caseLabel,
  status,
  list,
  onRequest,
  onReceive,
  onDeclareEngagement,
  onRefresh,
}: Props) {
  const events = list?.events ?? [];
  const partners = [...new Set(events.map((event) => event.partner_id))];
  const latestRevisionByPartner = new Map(
    partners.map((partnerId) => [
      partnerId,
      Math.max(...events.filter((event) => event.partner_id === partnerId).map((event) => event.revision)),
    ]),
  );
  const receivedRequestIds = new Set(
    events.filter((event) => event.event_type === "RECEIVED" && event.related_event_id)
      .map((event) => event.related_event_id),
  );
  const latestReceiptByPartner = new Map(
    partners.map((partnerId) => [
      partnerId,
      events.filter((event) => event.partner_id === partnerId && event.event_type === "RECEIVED")
        .sort((a, b) => b.revision - a.revision)[0]?.event_id,
    ]),
  );
  const engagedReceiptIds = new Set(
    events.filter((event) => event.event_type === "ENGAGEMENT_DECLARED" && event.related_event_id)
      .map((event) => event.related_event_id),
  );

  return (
    <section className="section-block" id="partners-section" aria-label="Partenaires de l’Affaire C09">
      <div className="section-heading">
        <div>
          <span className="section-kicker">C09 · PARTENAIRES</span>
          <h3>Partenaires de l’Affaire</h3>
        </div>
        <span className="count-pill">{partners.length} partenaire(s)</span>
      </div>
      <p>Affaire active : {caseLabel || "UNKNOWN · aucune Affaire sélectionnée"}.</p>
      <p>Demande déclarée ≠ envoi par SmartAO · reçu ≠ engagé · seul un acte Patron séparé déclare l’engagement.</p>
      <p>Ce registre ne calcule pas le prix, la couverture, le cash ou P3, et ne valide pas juridiquement un mandat.</p>
      {status === "NO_CASE" && <p role="status">UNKNOWN · sélectionnez une Affaire pour ouvrir C09.</p>}
      {status === "LOADING" && <p role="status">Chargement des partenaires et des preuves…</p>}
      {status === "FORBIDDEN" && <p role="status">FORBIDDEN · accès à C09 absent pour cette Affaire.</p>}
      {status === "UNAVAILABLE" && <p role="status">UNAVAILABLE · les événements partenaires ne sont pas disponibles.</p>}
      {status === "READY" && list?.can_request && caseId && (
        <PartnerRequestForm caseId={caseId} onSubmit={onRequest} onRefresh={onRefresh} />
      )}
      {status === "READY" && list?.can_receive && caseId && (
        <PartnerReceiptForm
          key={`standalone-${caseId}`}
          caseId={caseId}
          expectedRevision={0}
          onSubmit={onReceive}
          onRefresh={onRefresh}
        />
      )}
      {status === "READY" && events.length === 0 && <p>UNKNOWN · aucune demande ni aucun reçu partenaire n’est enregistré.</p>}
      {status === "READY" && events.map((event) => (
        <PartnerEventCard
          key={event.event_id}
          event={event}
          caseId={caseId}
          latestRevision={latestRevisionByPartner.get(event.partner_id) ?? event.revision}
          canReceive={list?.can_receive ?? false}
          canDeclareEngagement={list?.can_declare_engagement ?? false}
          requestHasReceipt={receivedRequestIds.has(event.event_id)}
          isLatestReceipt={latestReceiptByPartner.get(event.partner_id) === event.event_id}
          isEngaged={engagedReceiptIds.has(event.event_id)}
          onReceive={onReceive}
          onDeclareEngagement={onDeclareEngagement}
          onRefresh={onRefresh}
        />
      ))}
    </section>
  );
}

function PartnerEventCard({
  event,
  caseId,
  latestRevision,
  canReceive,
  canDeclareEngagement,
  requestHasReceipt,
  isLatestReceipt,
  isEngaged,
  onReceive,
  onDeclareEngagement,
  onRefresh,
}: {
  event: CasePartnerEvent;
  caseId: string;
  latestRevision: number;
  canReceive: boolean;
  canDeclareEngagement: boolean;
  requestHasReceipt: boolean;
  isLatestReceipt: boolean;
  isEngaged: boolean;
  onReceive: Props["onReceive"];
  onDeclareEngagement: Props["onDeclareEngagement"];
  onRefresh: Props["onRefresh"];
}) {
  return (
    <article className="detail-panel">
      <h4>{event.partner_label} · {partnerKindLabel(event.partner_kind)} · révision {event.revision}</h4>
      <p>{event.event_type === "REQUESTED" ? "REQUESTED · demande déclarée, non transmise par SmartAO" : event.event_type === "RECEIVED" ? "RECEIVED · preuve reçue" : "ENGAGEMENT_DECLARED · acte humain Patron"}</p>
      <p>Validité actuelle : {event.validity_current} · à l’enregistrement : {event.validity_at_recording}</p>
      <p>Exclusions : {event.exclusions_state}{event.exclusions.length ? ` · ${event.exclusions.join("; ")}` : event.exclusions_state === "DECLARED" ? " · aucune déclarée" : " · inconnues"}</p>
      <p>Mandat : {event.mandate_state}{event.mandate_source_locator ? ` · ${event.mandate_source_locator}` : ""}</p>
      <p>Source : {event.source_locator} · {event.rationale}</p>
      {event.event_type === "REQUESTED" && canReceive && !requestHasReceipt && (
        <PartnerReceiptForm
          key={`requested-${event.event_id}`}
          caseId={caseId}
          expectedRevision={latestRevision}
          requestEventId={event.event_id}
          partnerId={event.partner_id}
          partnerKind={event.partner_kind}
          partnerLabel={event.partner_label}
          onSubmit={onReceive}
          onRefresh={onRefresh}
        />
      )}
      {event.event_type === "RECEIVED" && isLatestReceipt && !isEngaged && canDeclareEngagement && (
        <PartnerEngagementForm
          key={`engagement-${event.event_id}`}
          caseId={caseId}
          expectedRevision={latestRevision}
          receipt={event}
          onSubmit={onDeclareEngagement}
          onRefresh={onRefresh}
        />
      )}
      {event.event_type === "RECEIVED" && isLatestReceipt && !isEngaged && !canDeclareEngagement && (
        <p>Un Patron habilité doit déclarer l’engagement séparément après revue des preuves.</p>
      )}
      {event.event_type === "ENGAGEMENT_DECLARED" && (
        <p role="status">Déclaration humaine conservée; SMART AO n’évalue pas la validité juridique du contrat.</p>
      )}
    </article>
  );
}

function PartnerRequestForm({
  caseId,
  onSubmit,
  onRefresh,
}: {
  caseId: string;
  onSubmit: Props["onRequest"];
  onRefresh: Props["onRefresh"];
}) {
  const [partnerId, setPartnerId] = useState(() => crypto.randomUUID());
  const [partnerKind, setPartnerKind] = useState<CasePartnerKind>("SUPPLIER");
  const [partnerLabel, setPartnerLabel] = useState("");
  const [sourceLocator, setSourceLocator] = useState("");
  const [rationale, setRationale] = useState("");
  const writer = usePartnerCommand(caseId, onSubmit, onRefresh);
  const prefix = `partner-request-${partnerId}`;

  async function submit(event: FormEvent<HTMLFormElement>) {
    const saved = await writer.submit(event, () => ({
      command_id: crypto.randomUUID(), idempotency_key: crypto.randomUUID(), correlation_id: crypto.randomUUID(),
      event_id: crypto.randomUUID(), partner_id: partnerId, case_id: caseId,
      expected_revision: 0, partner_kind: partnerKind, partner_label: partnerLabel.trim(),
      source_locator: sourceLocator.trim(), rationale: rationale.trim(),
    }));
    if (saved) {
      setPartnerId(crypto.randomUUID());
      setPartnerLabel("");
      setSourceLocator("");
      setRationale("");
    }
  }

  return (
    <form aria-label="Tracer une demande partenaire" onSubmit={(event) => void submit(event)} className="detail-panel">
      <h4>Tracer une demande déclarée</h4>
      <p>La trace ne transmet rien au partenaire.</p>
      <label htmlFor={`${prefix}-kind`}>Type de partenaire</label>
      <select id={`${prefix}-kind`} value={partnerKind} disabled={writer.formDisabled} onChange={(event) => setPartnerKind(event.target.value as CasePartnerKind)}>
        <option value="SUPPLIER">Fournisseur</option><option value="SUBCONTRACTOR">Sous-traitant</option><option value="CO_CONTRACTOR">Cotraitant</option>
      </select>
      <label htmlFor={`${prefix}-label`}>Entité partenaire déclarée</label>
      <input id={`${prefix}-label`} value={partnerLabel} required maxLength={240} disabled={writer.formDisabled} onChange={(event) => setPartnerLabel(event.target.value)} />
      <label htmlFor={`${prefix}-source`}>Source de la demande</label>
      <input id={`${prefix}-source`} value={sourceLocator} required maxLength={500} disabled={writer.formDisabled} onChange={(event) => setSourceLocator(event.target.value)} />
      <label htmlFor={`${prefix}-reason`}>Motif</label>
      <textarea id={`${prefix}-reason`} value={rationale} required maxLength={2000} disabled={writer.formDisabled} onChange={(event) => setRationale(event.target.value)} />
      <button type="submit" disabled={writer.buttonDisabled}>{writer.buttonLabel("Tracer la demande", "Réessayer la demande")}</button>
      {writer.message && <p role="alert">{writer.message}</p>}
    </form>
  );
}

function PartnerReceiptForm({
  caseId,
  expectedRevision,
  requestEventId = null,
  partnerId: existingPartnerId,
  partnerKind: existingPartnerKind,
  partnerLabel: existingPartnerLabel,
  onSubmit,
  onRefresh,
}: {
  caseId: string;
  expectedRevision: number;
  requestEventId?: string | null;
  partnerId?: string;
  partnerKind?: CasePartnerKind;
  partnerLabel?: string;
  onSubmit: Props["onReceive"];
  onRefresh: Props["onRefresh"];
}) {
  const [partnerId, setPartnerId] = useState(() => existingPartnerId ?? crypto.randomUUID());
  const [partnerKind, setPartnerKind] = useState<CasePartnerKind>(existingPartnerKind ?? "SUPPLIER");
  const [partnerLabel, setPartnerLabel] = useState(existingPartnerLabel ?? "");
  const [sourceLocator, setSourceLocator] = useState("");
  const [rationale, setRationale] = useState("");
  const [validUntil, setValidUntil] = useState("");
  const [exclusionsState, setExclusionsState] = useState<"UNKNOWN" | "DECLARED">("UNKNOWN");
  const [exclusionsText, setExclusionsText] = useState("");
  const [mandateState, setMandateState] = useState<"NOT_APPLICABLE" | "UNKNOWN" | "REQUESTED" | "RECEIVED" | "REVIEW_REQUIRED">("UNKNOWN");
  const [mandateSource, setMandateSource] = useState("");
  const writer = usePartnerCommand(caseId, onSubmit, onRefresh);
  const prefix = `partner-receipt-${requestEventId ?? partnerId}`;
  const fixedPartner = !!existingPartnerId;

  async function submit(event: FormEvent<HTMLFormElement>) {
    const saved = await writer.submit(event, () => ({
      command_id: crypto.randomUUID(), idempotency_key: crypto.randomUUID(), correlation_id: crypto.randomUUID(),
      event_id: crypto.randomUUID(), partner_id: partnerId, case_id: caseId, expected_revision: expectedRevision,
      request_event_id: requestEventId, partner_kind: partnerKind, partner_label: partnerLabel.trim(),
      source_locator: sourceLocator.trim(), rationale: rationale.trim(), valid_until: validUntil || null,
      exclusions_state: exclusionsState, exclusions: exclusionsText.split("\n").map((item) => item.trim()).filter(Boolean),
      mandate_state: mandateState, mandate_source_locator: mandateSource.trim() || null,
    }));
    if (saved && !fixedPartner) {
      setPartnerId(crypto.randomUUID());
      setPartnerLabel("");
      setSourceLocator("");
      setRationale("");
      setValidUntil("");
      setExclusionsText("");
      setMandateSource("");
    }
  }

  return (
    <form aria-label={requestEventId ? `Enregistrer le reçu ${partnerLabel}` : "Enregistrer une offre reçue non sollicitée"} onSubmit={(event) => void submit(event)} className="detail-panel">
      <h4>{requestEventId ? "Enregistrer la réception" : "Enregistrer une offre reçue sans demande suivie"}</h4>
      {!fixedPartner && <>
        <label htmlFor={`${prefix}-kind`}>Type de partenaire</label>
        <select id={`${prefix}-kind`} value={partnerKind} disabled={writer.formDisabled} onChange={(event) => setPartnerKind(event.target.value as CasePartnerKind)}>
          <option value="SUPPLIER">Fournisseur</option><option value="SUBCONTRACTOR">Sous-traitant</option><option value="CO_CONTRACTOR">Cotraitant</option>
        </select>
        <label htmlFor={`${prefix}-label`}>Entité partenaire déclarée</label>
        <input id={`${prefix}-label`} value={partnerLabel} required maxLength={240} disabled={writer.formDisabled} onChange={(event) => setPartnerLabel(event.target.value)} />
      </>}
      <label htmlFor={`${prefix}-source`}>Source du reçu</label>
      <input id={`${prefix}-source`} value={sourceLocator} required maxLength={500} disabled={writer.formDisabled} onChange={(event) => setSourceLocator(event.target.value)} />
      <label htmlFor={`${prefix}-reason`}>Motif / périmètre reçu</label>
      <textarea id={`${prefix}-reason`} value={rationale} required maxLength={2000} disabled={writer.formDisabled} onChange={(event) => setRationale(event.target.value)} />
      <p>Ne saisissez pas de montant ici ; les montants d’offre se déclarent séparément dans C08, réservé au Patron.</p>
      <label htmlFor={`${prefix}-validity`}>Valable jusqu’au (laisser vide si inconnu)</label>
      <input id={`${prefix}-validity`} type="date" value={validUntil} disabled={writer.formDisabled} onChange={(event) => setValidUntil(event.target.value)} />
      <label htmlFor={`${prefix}-exclusion-state`}>État des exclusions</label>
      <select id={`${prefix}-exclusion-state`} value={exclusionsState} disabled={writer.formDisabled} onChange={(event) => setExclusionsState(event.target.value as "UNKNOWN" | "DECLARED")}>
        <option value="UNKNOWN">Inconnues</option><option value="DECLARED">Déclarées</option>
      </select>
      {exclusionsState === "DECLARED" && <>
        <label htmlFor={`${prefix}-exclusions`}>Exclusions déclarées (une par ligne, vide = aucune)</label>
        <textarea id={`${prefix}-exclusions`} value={exclusionsText} maxLength={4000} disabled={writer.formDisabled} onChange={(event) => setExclusionsText(event.target.value)} />
      </>}
      <label htmlFor={`${prefix}-mandate`}>État du mandat</label>
      <select id={`${prefix}-mandate`} value={mandateState} disabled={writer.formDisabled} onChange={(event) => setMandateState(event.target.value as typeof mandateState)}>
        {partnerKind !== "CO_CONTRACTOR" && <option value="NOT_APPLICABLE">Non applicable déclaré</option>}
        <option value="UNKNOWN">Inconnu</option>
        {partnerKind === "CO_CONTRACTOR" && <>
          <option value="REQUESTED">Demandé</option><option value="RECEIVED">Reçu</option><option value="REVIEW_REQUIRED">À revoir</option>
        </>}
      </select>
      {mandateState === "RECEIVED" && <>
        <label htmlFor={`${prefix}-mandate-source`}>Source du mandat reçu</label>
        <input id={`${prefix}-mandate-source`} value={mandateSource} required maxLength={500} disabled={writer.formDisabled} onChange={(event) => setMandateSource(event.target.value)} />
      </>}
      <button type="submit" disabled={writer.buttonDisabled}>{writer.buttonLabel("Enregistrer le reçu", "Réessayer le reçu")}</button>
      {writer.message && <p role="alert">{writer.message}</p>}
    </form>
  );
}

function PartnerEngagementForm({
  caseId,
  expectedRevision,
  receipt,
  onSubmit,
  onRefresh,
}: {
  caseId: string;
  expectedRevision: number;
  receipt: CasePartnerEvent;
  onSubmit: Props["onDeclareEngagement"];
  onRefresh: Props["onRefresh"];
}) {
  const [sourceLocator, setSourceLocator] = useState("");
  const [rationale, setRationale] = useState("");
  const writer = usePartnerCommand(caseId, onSubmit, onRefresh);
  const prefix = `partner-engagement-${receipt.event_id}`;
  const mandateReady = receipt.partner_kind !== "CO_CONTRACTOR"
    || (receipt.mandate_state === "RECEIVED" && !!receipt.mandate_source_locator);

  async function submit(event: FormEvent<HTMLFormElement>) {
    const saved = await writer.submit(event, () => ({
      command_id: crypto.randomUUID(), idempotency_key: crypto.randomUUID(), correlation_id: crypto.randomUUID(),
      event_id: crypto.randomUUID(), partner_id: receipt.partner_id, case_id: caseId,
      expected_revision: expectedRevision, receipt_event_id: receipt.event_id,
      source_locator: sourceLocator.trim(), rationale: rationale.trim(),
    }));
    if (saved) {
      setSourceLocator("");
      setRationale("");
    }
  }

  return (
    <div>
      {!mandateReady && <p role="status">Mandat cotraitant non reçu/sourcé · déclaration d’engagement fermée.</p>}
      <form aria-label={`Déclarer l’engagement de ${receipt.partner_label}`} onSubmit={(event) => void submit(event)} className="detail-panel">
        <h4>Acte Patron séparé : déclarer l’engagement</h4>
        <label htmlFor={`${prefix}-source`}>Source de l’engagement</label>
        <input id={`${prefix}-source`} value={sourceLocator} required maxLength={500} disabled={writer.formDisabled || !mandateReady} onChange={(event) => setSourceLocator(event.target.value)} />
        <label htmlFor={`${prefix}-rationale`}>Motif de la déclaration</label>
        <textarea id={`${prefix}-rationale`} value={rationale} required maxLength={2000} disabled={writer.formDisabled || !mandateReady} onChange={(event) => setRationale(event.target.value)} />
        <button type="submit" disabled={writer.buttonDisabled || !mandateReady}>{writer.buttonLabel("Déclarer l’engagement Patron", "Réessayer la déclaration")}</button>
        {writer.message && <p role="alert">{writer.message}</p>}
        <p>La déclaration n’est ni une validation juridique ni un GO P3.</p>
      </form>
    </div>
  );
}

function usePartnerCommand<T extends { case_id: string }>(
  caseId: string,
  write: (input: T) => Promise<unknown>,
  refresh: Props["onRefresh"],
) {
  const [pending, setPending] = useState<T | null>(null);
  const pendingRef = useRef<T | null>(null);
  const submittingRef = useRef(false);
  const [submitting, setSubmitting] = useState(false);
  const [failure, setFailure] = useState<Failure | null>(null);
  const wrongCase = pending !== null && pending.case_id !== caseId;
  const formDisabled = submitting || pending !== null;
  const buttonDisabled = submitting || wrongCase;

  async function submit(event: FormEvent<HTMLFormElement>, create: () => T): Promise<boolean> {
    event.preventDefault();
    if (submittingRef.current || wrongCase) return false;
    const input = pendingRef.current ?? create();
    if (!pendingRef.current) {
      pendingRef.current = input;
      setPending(input);
    }
    submittingRef.current = true;
    setSubmitting(true);
    setFailure(null);
    try {
      await write(input);
      await refresh();
      pendingRef.current = null;
      setPending(null);
      return true;
    } catch (error) {
      const status = (error as { status?: number })?.status;
      if (status === 409 || status === undefined || status >= 500) {
        setFailure("UNCONFIRMED");
      } else {
        pendingRef.current = null;
        setPending(null);
        setFailure("REJECTED");
      }
      return false;
    } finally {
      submittingRef.current = false;
      setSubmitting(false);
    }
  }

  function buttonLabel(create: string, retry: string) {
    if (submitting) return "Enregistrement…";
    if (failure === "UNCONFIRMED" && pending) return retry;
    if (failure === "REJECTED") return "Corriger et réessayer";
    return create;
  }

  const message = wrongCase
    ? `Résultat non confirmé pour l’Affaire ${pending?.case_id} · revenez à cette Affaire pour rejouer les mêmes identifiants.`
    : failure === "UNCONFIRMED"
      ? "Résultat non confirmé · le rejeu conserve les mêmes identifiants."
      : failure === "REJECTED"
        ? "Refus confirmé · aucun événement n’a été enregistré."
        : null;
  return { submit, formDisabled, buttonDisabled, buttonLabel, message };
}

function partnerKindLabel(kind: CasePartnerEvent["partner_kind"]) {
  if (kind === "SUPPLIER") return "Fournisseur";
  if (kind === "SUBCONTRACTOR") return "Sous-traitant";
  return "Cotraitant";
}
