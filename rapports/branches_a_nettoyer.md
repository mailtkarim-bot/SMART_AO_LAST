# Branches à nettoyer — audit du 30 août 2026

Ce document liste les branches identifiées comme obsolètes ou candidates à suppression après l'analyse de `main` (`16f61b9`).

## Branches locales

| Branche | État | Action recommandée |
|---|---|---|
| `docs/pricing-http-next-lot-28` | Existe encore localement alors que les lots équivalents ont été fusionnés dans `main` via PR #51–#56. | À vérifier, puis supprimer si elle n'est plus nécessaire. |
| `remediation/audit-p0-hardening-20260825` | Marquée `[gone]` : la branche distante a déjà été supprimée. | Supprimer localement. |
| `t3code/8cf1106d` | Branche externe non identifiée (`feat: add CCAP CCTP risk register and reader ports`). | Ne pas supprimer sans confirmation de son propriétaire. |

## Branches distantes déjà fusionnées dans `main`

Ces branches peuvent être supprimées du remote sans risque :

```bash
git push origin --delete chore/collab-evidence-vps-preproduction
git push origin --delete feat/collab-info-blockers-01
git push origin --delete feat/collab-work-task-01
git push origin --delete feat/enterprise-capability-foundation-01
git push origin --delete feat/enterprise-library
git push origin --delete feat/enterprise-library-http
git push origin --delete feat/enterprise-library-upload-verification
git push origin --delete feat/financial-report-draft-lines
git push origin --delete feat/preparation-completeness-01
```

## Branches distantes à vérifier avant suppression

Ces branches ne sont **pas** fusionnées dans `main`. Elles doivent être vérifiées individuellement (contenu utile, PR ouverte, travail en cours) avant toute suppression :

- `origin/arch-001-membership-mutation-service-20260826`
- `origin/audit/consolidated-remediation`
- `origin/docs/manual-preprod-deployment-20260826`
- `origin/docs/pricing-http-next-lot-28`
- `origin/feat/arch001-pricing-case-port-20260827`
- `origin/feat/collaborator-document-kinds-20260827`
- `origin/feat/collaborator-task-workflow-20260827`
- `origin/feat/controlled-dce-ocr-20260826`
- `origin/feat/decision-finalization-cockpit-20260826`
- `origin/feat/interdocument-contradiction-detection-20260826`
- `origin/feat/mfa-enforce-decision-finalization-20260827`
- `origin/feat/mfa-enforce-submission-signature-20260827`
- `origin/feat/mfa-step-up-cockpit-20260827`
- `origin/feat/mfa-totp-cockpit-20260827`
- `origin/feat/patron-preparation-review-cockpit-20260827`
- `origin/feat/preparation-generated-document-access-20260826`
- `origin/ops/preprod-ocr-preflight-20260826`
- `origin/refactor/pricing-hook-robustness-staging-simulation`

## Commandes de nettoyage

```bash
# 1. Supprimer les branches locales obsolètes
git branch -d remediation/audit-p0-hardening-20260825
git branch -d docs/pricing-http-next-lot-28  # si confirmé inutile

# 2. Supprimer les branches distantes déjà fusionnées
git push origin --delete chore/collab-evidence-vps-preproduction feat/collab-info-blockers-01 feat/collab-work-task-01 feat/enterprise-capability-foundation-01 feat/enterprise-library feat/enterprise-library-http feat/enterprise-library-upload-verification feat/financial-report-draft-lines feat/preparation-completeness-01

# 3. Synchroniser les références locales
git fetch --prune
```

## Attention

Ne pas exécuter les suppressions distantes sans vérifier qu'aucune PR ouverte ne pointe encore vers ces branches.
