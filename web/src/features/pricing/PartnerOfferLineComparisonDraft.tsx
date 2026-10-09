import type { FormEvent } from "react";

import type { PartnerOfferScopeReviewList } from "../../shared/types";
import { fields, type Draft, type GroupDraft } from "./partnerOfferLineComparisonModel";

export function PartnerOfferLineComparisonDraft({
  draft,
  scopeList,
  error,
  saving,
  onGroupUpdate,
  onAddGroup,
  onRemoveGroup,
  onCancel,
  onPrepare,
  onBack,
  onConfirmChange,
  onConfirm,
}: {
  draft: Draft | null;
  scopeList: PartnerOfferScopeReviewList | null;
  error?: string;
  saving: boolean;
  onGroupUpdate: (index: number, update: (group: GroupDraft) => GroupDraft) => void;
  onAddGroup: () => void;
  onRemoveGroup: (index: number) => void;
  onCancel: () => void;
  onPrepare: (event: FormEvent<HTMLFormElement>) => void;
  onBack: () => void;
  onConfirmChange: (confirmed: boolean) => void;
  onConfirm: () => void;
}) {
  if (!draft) return null;

  if (draft.stage === "REVIEW") {
    return (
      <div className="partner-line-command-review">
        <h4>Vérifier les déclarations</h4>
        <p>Revue {draft.scopeReviewId} · révision {draft.scopeReviewRevision} · comparaison {draft.comparisonId}.</p>
        <p>Les groupes, motifs et champs UNKNOWN/DECLARED seront enregistrés comme déclaration humaine; aucune couverture, préférence, valeur financière, disponibilité, réservation, engagement ou statut juridique ne sera calculé.</p>
        {draft.groups.map((group, groupIndex) => (
          <section className="partner-line-command-review-group" key={group.group_id}>
            <h5>Groupe {groupIndex + 1} · {group.disposition}</h5>
            <p>Motif humain · {group.rationale}</p>
            <ul>
              {group.members.map((member) => (
                <li key={member.receipt_event_id}>
                  <code>{member.receipt_event_id}</code>
                  {fields.map(({ key, label }) => (
                    <span key={key}> · {label}: {member.fields[key].state === "UNKNOWN" ? "UNKNOWN" : member.fields[key].value}</span>
                  ))}
                </li>
              ))}
            </ul>
          </section>
        ))}
        <label className="partner-line-confirm-label">
          <input type="checkbox" checked={draft.confirmed} onChange={(event) => onConfirmChange(event.target.checked)} />
          J’ai relu les groupes, les motifs et les reçus exacts; je confirme cette déclaration humaine.
        </label>
        <div className="partner-line-command-actions">
          <button type="button" className="secondary-button" disabled={saving} onClick={onBack}>Modifier le brouillon</button>
          <button type="button" disabled={!draft.confirmed || saving} onClick={onConfirm}>
            {saving ? "Enregistrement…" : "Confirmer et enregistrer"}
          </button>
        </div>
        {error && <p role="alert">{error}</p>}
      </div>
    );
  }

  return (
    <form className="partner-line-command-form" aria-label="Préparer le rapprochement" onSubmit={onPrepare}>
      <div className="partner-line-command-source">
        <strong>Revue exacte</strong>
        <code>{draft.scopeReviewId} · révision {draft.scopeReviewRevision}</code>
        <span>SAME_SCOPE_CONFIRMED · localisateur déclaré ≠ pièce vérifiée</span>
      </div>
      {draft.groups.map((group, groupIndex) => (
        <fieldset className="partner-line-command-group" key={group.group_id}>
          <legend>Groupe {groupIndex + 1} · {group.members.length} reçus exacts</legend>
          <label htmlFor={`line-disposition-${group.group_id}`}>Disposition humaine</label>
          <select
            id={`line-disposition-${group.group_id}`}
            value={group.disposition}
            onChange={(event) => onGroupUpdate(groupIndex, (current) => ({
              ...current,
              disposition: event.target.value as GroupDraft["disposition"],
            }))}
          >
            <option value="LINKED_BY_PATRON">LINKED_BY_PATRON</option>
            <option value="DISTINCT_POSITIONS">DISTINCT_POSITIONS</option>
            <option value="NEEDS_CLARIFICATION">NEEDS_CLARIFICATION</option>
          </select>
          <label htmlFor={`line-rationale-${group.group_id}`}>Motif humain · obligatoire</label>
          <textarea
            id={`line-rationale-${group.group_id}`}
            required
            maxLength={2_000}
            value={group.rationale}
            onChange={(event) => onGroupUpdate(groupIndex, (current) => ({ ...current, rationale: event.target.value }))}
          />
          <p className="small muted">Chaque groupe doit reprendre tous les reçus de cette revue. Une disposition ne vérifie pas une équivalence.</p>
          {group.members.map((member, memberIndex) => {
            const source = scopeList?.reviews.find((review) => review.review_id === draft.scopeReviewId)
              ?.offers.find((offer) => offer.receipt_event_id === member.receipt_event_id);
            return (
              <div className="partner-line-command-member" key={member.receipt_event_id}>
                <div className="partner-line-command-source">
                  <strong>{source?.partner_label ?? "Partenaire"}</strong>
                  <code>{member.receipt_event_id}</code>
                  <span>Localisateur déclaré · {source?.source_locator ?? "UNKNOWN"}</span>
                </div>
                {fields.map(({ key, label, maxLength }) => {
                  const field = member.fields[key];
                  const fieldId = `line-${group.group_id}-${memberIndex}-${key}`;
                  return (
                    <div className="partner-line-command-field" key={key}>
                      <label htmlFor={`${fieldId}-state`}>{label}</label>
                      <select
                        id={`${fieldId}-state`}
                        aria-label={`État ${label} · ${source?.partner_label ?? member.receipt_event_id}`}
                        value={field.state}
                        onChange={(event) => onGroupUpdate(groupIndex, (current) => ({
                          ...current,
                          members: current.members.map((currentMember) => currentMember.receipt_event_id !== member.receipt_event_id
                            ? currentMember
                            : {
                              ...currentMember,
                              fields: {
                                ...currentMember.fields,
                                [key]: { state: event.target.value as typeof field.state, value: event.target.value === "UNKNOWN" ? null : "" },
                              },
                            }),
                        }))}
                      >
                        <option value="UNKNOWN">UNKNOWN</option>
                        <option value="DECLARED">DECLARED</option>
                      </select>
                      {field.state === "UNKNOWN" ? (
                        <code className="partner-line-unknown-field">UNKNOWN · null</code>
                      ) : (
                        <input
                          id={fieldId}
                          aria-label={`Valeur déclarée · ${label} · ${source?.partner_label ?? member.receipt_event_id}`}
                          type="text"
                          required
                          maxLength={maxLength}
                          value={field.value ?? ""}
                          onChange={(event) => onGroupUpdate(groupIndex, (current) => ({
                            ...current,
                            members: current.members.map((currentMember) => currentMember.receipt_event_id !== member.receipt_event_id
                              ? currentMember
                              : { ...currentMember, fields: { ...currentMember.fields, [key]: { state: "DECLARED", value: event.target.value } } }),
                          }))}
                        />
                      )}
                    </div>
                  );
                })}
                {draft.groups.length > 1 && (
                  <button type="button" className="secondary-button" onClick={() => onRemoveGroup(groupIndex)}>
                    Retirer le groupe {groupIndex + 1}
                  </button>
                )}
              </div>
            );
          })}
        </fieldset>
      ))}
      <div className="partner-line-command-actions">
        <button type="button" className="secondary-button" disabled={draft.groups.length >= 8} onClick={onAddGroup}>Ajouter un groupe</button>
        <button type="button" className="secondary-button" onClick={onCancel}>Abandonner le brouillon</button>
        <button type="submit">Vérifier les déclarations</button>
      </div>
      {error && <p role="alert">{error}</p>}
    </form>
  );
}
