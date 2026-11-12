import { useEffect, useState } from "react";

import type { ApiClient } from "../../infrastructure/api";
import type {
  PartnerOfferLineComparison,
  PartnerOfferLineComparisonList,
  PartnerOfferLineComparisonMember,
} from "../../shared/types";
import { PartnerOfferLineComparisonCommand } from "./PartnerOfferLineComparisonCommand";

type ReadStatus = "LOADING" | "READY" | "FORBIDDEN" | "UNAVAILABLE" | "NO_CASE" | "INACTIVE";

function apiErrorStatus(error: unknown): number | undefined {
  const value = (error as { status?: unknown })?.status;
  return typeof value === "number" ? value : undefined;
}

export function PartnerOfferLineComparisonsPanel({
  api,
  caseId,
  enabled,
}: {
  api: ApiClient;
  caseId: string;
  enabled: boolean;
}) {
  const [status, setStatus] = useState<ReadStatus>(() => !enabled ? "INACTIVE" : caseId ? "LOADING" : "NO_CASE");
  const [list, setList] = useState<PartnerOfferLineComparisonList | null>(null);

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
    void api.listPartnerOfferLineComparisons(caseId).then((result) => {
      if (!active) return;
      if (result.case_id !== caseId || !Array.isArray(result.comparisons)) {
        setStatus("UNAVAILABLE");
        return;
      }
      setList(result);
      setStatus("READY");
    }).catch((error: unknown) => {
      if (!active) return;
      setList(null);
      setStatus(apiErrorStatus(error) === 403 ? "FORBIDDEN" : "UNAVAILABLE");
    });
    return () => { active = false; };
  }, [api, caseId, enabled]);

  const visibleList = enabled && status === "READY" && list?.case_id === caseId ? list : null;
  const latestRevisionByComparison = new Map<string, number>();
  for (const comparison of visibleList?.comparisons ?? []) {
    latestRevisionByComparison.set(
      comparison.comparison_id,
      Math.max(latestRevisionByComparison.get(comparison.comparison_id) ?? 0, comparison.revision),
    );
  }
  if (!enabled) return null;

  return (
    <section className="partner-line-comparisons" aria-label="Rapprochements de lignes C08">
      <div className="partner-line-comparisons-heading">
        <div>
          <h3>Rapprochements de lignes</h3>
          <p>Lecture seule · reçus, décisions Patron et révisions conservés.</p>
        </div>
      </div>

      <PartnerOfferLineComparisonCommand
        api={api}
        caseId={caseId}
        enabled={enabled}
        onComparisonsRead={(result) => {
          if (result.case_id !== caseId) return;
          setList(result);
          setStatus("READY");
        }}
      />

      {status === "NO_CASE" && <p role="status">UNKNOWN · sélectionnez une Affaire.</p>}
      {status === "LOADING" && <p role="status">Chargement des rapprochements…</p>}
      {status === "FORBIDDEN" && <p role="status">FORBIDDEN · lecture privée réservée au Patron habilité.</p>}
      {status === "UNAVAILABLE" && <p role="status">UNAVAILABLE · les rapprochements n’ont pas pu être relus.</p>}
      {visibleList?.comparisons.length === 0 && (
        <p className="partner-line-comparisons-empty">
          Aucun rapprochement de lignes enregistré. Aucune correspondance n’est déduite en l’absence d’un acte Patron.
        </p>
      )}
      {visibleList?.comparisons.map((comparison) => (
        <ComparisonRecord
          key={comparison.record_id}
          comparison={comparison}
          open={
            !comparison.requires_reassessment
            && latestRevisionByComparison.get(comparison.comparison_id) === comparison.revision
          }
        />
      ))}
    </section>
  );
}

function ComparisonRecord({ comparison, open }: { comparison: PartnerOfferLineComparison; open: boolean }) {
  return (
    <details className="partner-line-comparison-record" open={open}>
      <summary>
        <span className="partner-line-comparison-title">
          <strong>{comparison.record_id}</strong>
          <code>{comparison.comparison_id} · révision {comparison.revision}</code>
        </span>
        <span className={comparison.requires_reassessment ? "partner-line-state partner-line-warning" : "partner-line-state"}>
          {comparison.requires_reassessment ? "REVIEW_REQUIRED" : "Enregistrement conservé"}
        </span>
      </summary>

      {comparison.requires_reassessment && (
        <p className="partner-line-stale" role="status">
          REVIEW_REQUIRED · la revue de périmètre ou un reçu a changé depuis cet acte. Historique conservé, sans réécriture.
        </p>
      )}

      <dl className="partner-line-record-meta">
        <div><dt>Revue de périmètre exacte</dt><dd><code>{comparison.scope_review_id} · révision {comparison.scope_review_revision}</code></dd></div>
        <div><dt>Décision de périmètre enregistrée</dt><dd><code>{comparison.scope_review_decision}</code></dd></div>
        <div><dt>Enregistré le</dt><dd><time dateTime={comparison.recorded_at}>{comparison.recorded_at}</time></dd></div>
      </dl>

      {comparison.groups.map((group) => (
        <section className="partner-line-group" key={group.group_id} aria-label={`Groupe ${group.group_id}`}>
          <div className="partner-line-group-heading">
            <h4>{group.group_id}</h4>
            <code>{group.disposition}</code>
          </div>
          <p className="partner-line-rationale">Motif Patron · {group.rationale}</p>
          <div className="partner-line-members">
            {group.members.map((member) => <ComparisonMember key={member.receipt_event_id} member={member} />)}
          </div>
        </section>
      ))}
    </details>
  );
}

function ComparisonMember({ member }: { member: PartnerOfferLineComparisonMember }) {
  return (
    <article className="partner-line-member">
      <div className="partner-line-member-heading">
        <div>
          <h5>{member.partner_label}</h5>
          <span>{partnerKindLabel(member.partner_kind)}</span>
        </div>
        <span className={member.receipt_is_current ? "partner-line-state" : "partner-line-state partner-line-muted"}>
          {member.receipt_is_current ? "Reçu courant" : "Reçu historique"}
        </span>
      </div>

      <dl className="partner-line-source">
        <div><dt>ID exact du reçu</dt><dd><code>{member.receipt_event_id}</code></dd></div>
        <div><dt>Localisateur source déclaré</dt><dd><code>{member.source_locator}</code></dd></div>
      </dl>

      <dl className="partner-line-fields">
        <Field label="Repère de ligne" state={member.line_locator_state} value={member.line_locator} />
        <Field label="Référence article" state={member.item_reference_state} value={member.item_reference} />
        <Field label="Désignation" state={member.designation_state} value={member.designation} />
        <Field label="Unité" state={member.unit_state} value={member.unit} />
        <Field label="Quantité" state={member.quantity_state} value={member.quantity} />
      </dl>
    </article>
  );
}

function Field({ label, state, value }: {
  label: string;
  state: "UNKNOWN" | "DECLARED";
  value: string | null;
}) {
  const displayState = state === "DECLARED" && value === null ? "DECLARED · valeur absente" : state;
  return (
    <div>
      <dt>{label}</dt>
      <dd>
        {state === "DECLARED" && value !== null && <span>{value}</span>}
        <code>{displayState}</code>
      </dd>
    </div>
  );
}

function partnerKindLabel(kind: PartnerOfferLineComparisonMember["partner_kind"]) {
  if (kind === "SUPPLIER") return "Fournisseur";
  if (kind === "SUBCONTRACTOR") return "Sous-traitant";
  return "Cotraitant";
}
