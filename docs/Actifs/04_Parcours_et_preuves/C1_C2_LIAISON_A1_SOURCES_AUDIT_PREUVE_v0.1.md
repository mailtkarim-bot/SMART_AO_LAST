# C1/C2 — liaison Patron entre changement et engagements A1

**Date :** 3 octobre 2026<br>
**Statut :** preuve locale complète au checkout de travail, NO-GO public maintenu<br>
**Base de code :** HEAD `9c2a982` plus les changements C2 locaux non commités<br>
**Autorités :** Product Freeze v3.1 PF31-03/04/08, Master métier M31-05, Cahier technique CT2-119

## AS-IS avant C2

- B1 fige les liens d’engagement A1 dans `snapshot.decision.condition_sources` : condition, exigence/révision, impact/révision, profil/version/hash.
- C1 rattache un événement contractuel à son snapshot B1, puis enregistre séparément une revue d’applicabilité et une action humaine.
- La lecture C1 exposait l’événement et le snapshot, mais pas les références A1 figées à consulter ou à sélectionner pour cet événement. Aucun lien humain direct C1→A1 n’était conservé.

## Décision de cadrage

C2 réutilise uniquement les références A1 déjà présentes dans le snapshot B1 lié à l’événement C1. Le Patron consulte ces références et enregistre une révision append-only par événement :

- `LINKED` exige une ou plusieurs références sélectionnées, strictement égales aux références A1 de ce snapshot ;
- `UNKNOWN` exige une justification, ne sélectionne aucune source et demeure visible dans l’historique ;
- une correction crée une nouvelle révision avec `expected_revision` ; un rejeu conserve le même acte et ne crée pas une nouvelle ligne.

La liaison conserve l’identité des références de condition/preuve (IDs, révisions, version/hash de profil) sans relire ni recalculer A1. L’acte ne change ni l’événement C1, ni le snapshot B1, ni la décision/condition/impact A1.

## Risques contrôlés

- référence forgée, altérée ou issue d’un autre snapshot : refus serveur ;
- fuite entre Affaires/tenants ou vers un Collaborateur : filtrage tenant/Affaire et politique Patron `FINANCIAL_PRIVATE` ;
- double clic/interruption : command ID et idempotency key stables au retry ;
- réécriture ou suppression d’un acte : contraintes et trigger PostgreSQL append-only ;
- conclusion abusive : aucun effet juridique, calcul de coût/cash/délai, changement P3/P7 ou action automatique.

## Points d’insertion

- Migration additive `20261003_0126_case_contract_change_engagement_links.py`.
- La FK composite PostgreSQL lie chaque acte à l’événement et au snapshot B1 exact portés par ce C1.
- Handler de commande C1 existant, registre des modèles SQLAlchemy et lecteur tenant-scoped existant.
- API Patron `POST /api/v1/patron/cases/{case_id}/contract-change-events/{event_id}/engagement-links` ; lecture incluse dans la projection C1 existante.
- `CaseContractChangePanel` : lecture du snapshot A1, sélection Patron, historique et état inconnu.

## Preuves

| Garantie | Cible | Résultat |
|---|---|---|
| Parcours HTTP/PostgreSQL même Affaire A1→B1→C1→C2 | `backend/tests/db/test_case_handover_http_e2e.py::test_http_c1_keeps_unknown_until_patron_links_change_to_handover_and_records_action` | 1/1 PASS |
| `UNKNOWN` motivé, puis sélection exacte C2 et historique ordonné | même test | PASS |
| Rejeu d’UNKNOWN et de LINKED sans nouvel acte | même test | PASS |
| Référence modifiée non présente dans B1 refusée | même test | HTTP 422 `A1_SOURCE_NOT_IN_HANDOVER_SNAPSHOT` |
| Collaborateur refusé, autre tenant sans lecture et écriture refusée | même test | 403 / lecture neutre / 422 |
| UPDATE et DELETE C2 refusés ; A1 reste `CONDITIONAL_GO`, condition `OPEN`, impact `HUMAN_REVIEW_REQUIRED` | même test | PASS |
| UI C2 de consultation et sélection | `web/src/features/decision/CaseContractChangePanel.test.tsx` | 2/2 PASS |
| Backend complet PostgreSQL | `SMART_AO_TEST_DATABASE_URL=...smart_ao_v8_test ./.venv/bin/pytest --import-mode=importlib -q --tb=short` | 2013/2013 PASS, 16 min 44 s |
| Frontend complet, typecheck, lint et build | scripts `web` | 297/297 ; typecheck/lint/build PASS |
| Contrats d’architecture/schema/ops | quatre tests ciblés | 38/38 PASS |
| Ruff ciblé et mypy ciblé | fichiers C2 | PASS |
| Alembic | fixture PostgreSQL du test C2 | upgrade head et downgrade base exécutés |

Le full backend a précédé le dernier durcissement de FK composite ; le test E2E C2 avec upgrade/downgrade PostgreSQL et les contrats architecture/schema/ops ont été rejoués après ce changement et passent.

Le seul avertissement de test est la dépréciation Starlette/httpx. Le build signale également le chunk principal au-dessus de 500 kB. Ces avertissements ne sont pas causés par le contrat métier C2.

## Limites et suite

Cette preuve établit le comportement local sur fixtures déterministes, pas une validation utilisateur, un audit externe, un navigateur CUA ni une mise en production. Le WIP C2 n’est ni commité ni poussé ; la branche distante reste au dernier commit antérieur `9c2a982`. Basic Memory n’était pas accessible dans cette session. Aucune ouverture publique n’est autorisée.

**Tranche suivante :** auditer si les actions/preuves C1 existantes doivent être rattachées à une déclaration C3 exacte, sans fusionner les actes ni déclencher une action automatiquement.
