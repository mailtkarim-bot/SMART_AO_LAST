# Revue générale et réorientation — 12 novembre 2026

Le [plan R0–R3](SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md) remplace le journal comme outil de décision. La demande Owner autorise désormais consolidation, commits, intégration et push, mais pas un GO public ou un déploiement implicite.

## Diagnostic

Les dernières sessions L09–L11 ont ajouté des raccordements de recettes et leurs preuves. Les primitives métier étaient déjà présentes ; ces travaux n’ont pas ajouté de parcours applicatif nouveau. La multiplication de compte-rendus et de prochaines micro-étapes a entretenu la progression des preuves sans donner une borne claire d’utilisation. C’est une erreur de pilotage à corriger : les prochaines unités sont des livraisons, pas des variantes de tests.

La version locale contient un ensemble fonctionnel important L01–L11. Elle n’est pas démontrée opérationnelle pour un utilisateur depuis une installation propre. Les sorties avec UNKNOWN protègent les données ; elles ne closent pas les fonctions manquantes. Les blocages structurants restent la pièce de prix publiable, la continuité A1/C3, la reprise durable et la recette produit/exploitation. Les reports Owner sont séparés dans le plan.

## Contrôles du jour

Après fetch, origin/main est ancêtre du HEAD30f2693 :13 commits d’avance, aucun commit distant manquant. Aucun PR ouvert retrouvé par le connecteur. Les worktrees ci-dessous ont des commits déjà intégrés au HEAD, mais leurs modifications locales ne sont pas des commits et ne sont donc pas automatiquement fusionnées. D’autres branches historiques ont des commits non communs : `codex/phase-a0-execution`, `docs/pricing-http-next-lot-28`, `feat/arch001-pricing-scenario-projection-20260830`, `t3code/8cf1106d`. Leur ascendance et leur contenu doivent être classés avant une fusion, sans réintroduire des versions anciennes.

| Worktree/branche secondaire | Fichiers WIP | Variantes différentes du principal |
|---|---:|---:|
| `codex/capacity-input-guard-20261011` | 4 | 2 |
| `codex/dce-analysis-trials-20261011` | 18 | 7 |
| `codex/dce-completeness-trials-20261011` | 22 | 7 |
| `codex/dce-page-coverage-20261012` | 24 | 9 |
| `codex/dce-six-signals-20261012` | 24 | 9 |
| `codex/dce-structured-projection-20261012` | 39 | 9 |
| `codex/p5-contract-audit-20261009` | 0 | 0 |
| `codex/p5-exact-origin-20261009` | 0 | 0 |
| `codex/pdf-coverage-guard-20261011` | 4 | 2 |
| `codex/quality-gates-20261009` | 0 | 0 |

Une archive de tous les WIP de worktrees a été créée avant intégration, avec inventaire sous `.local-proofs/reorientation-20261112/` (hors Git). Les variantes portent notamment sur extraction/analyse DCE, capacité, tests et dépendances. Aucune n’a été supprimée ou silencieusement écrasée.

Ruff global passe. Le formatage avait un seul défaut dans le bootstrap CASH, corrigé sans comportement modifié. Le contrôle CI réel `mypy backend/app backend/tests` rapporte212 diagnostics dans44 fichiers : la vérification antérieure des seuls708 fichiers applicatifs ne suffisait pas à qualifier la CI. Aucune suite backend générale nouvelle n’est revendiquée par cette revue documentaire. Le contrôle de secrets et les résultats Git finaux sont à confirmer dans le relevé de livraison ; un push ou merge non effectué ne sera pas annoncé comme réussi.

## Décision de pilotage

R0 : baseline Git/CI reproductible. R1 : parcours utilisateur complet local, incluant les manques qui empêchent la première promesse. R2 : pilote représentatif autorisé et reprise/restauration. R3 : exploitation explicitement autorisée. Pas de date ferme avant R0 ; fournir alors une estimation mesurée de R1, puis une démonstration, pas un pourcentage arbitraire.

Limiter les lectures au contrat affecté et aux derniers résultats ; regrouper les correctifs ; une campagne globale au jalon pertinent, pas à chaque détail. Une revue ciblée et une passe de correction. Les livrables datés existants restent historiques. Un défaut observé doit être rattaché au jalon actif avec impact utilisateur et critère de sortie, sans créer une nouvelle boucle L01–L11.


**Contrôle de secrets :**450 faux positifs hexadécimaux examinés : champs SHA256 et12 révisions Git de modèles dans36 JSON de fixtures/manifestes. Exceptions enregistrées dans la baseline sans filtre global désactivé ; aucun mot de passe/token identifié parmi ces nouvelles alertes. Les archives privées `.local-proofs/` sont exclues de Git. La baseline complète reste contrôlée par le hook avant publication.


**Vérification avant commit :** scan statique de tous les fichiers source versionnables (mêmes exclusions docs/lock frontend que la CI), comparaison avec la baseline : zéro alerte non triée hors de la baseline elle-même. Le fichier de baseline contient des empreintes de détection et n’est pas une source de credentials ; ses auto-détections ne sont pas ajoutées comme nouvelles exceptions. Le hook direct a dépassé le budget local d’attente ; son passage CI n’est pas revendiqué. Whitespace indexé propre, CRLF CSV et sauts Markdown explicitement reconnus par attributs Git. Les212 diagnostics mypy restent bloquants pour une intégration finale main.
