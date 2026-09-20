# SMART AO — Audit confidentialité et déductions G01–G09

**Date :** 20 septembre 2026  
**Statut :** audit exécuté, aucun défaut bloquant constaté  
**Périmètre :** marge, pouvoir métier, score public, RAG et états inconnus

## Verdict

Les surfaces G01–G09 ne publient pas de marge, de coût, de trésorerie, de prix ou de pouvoir administratif à un Collaborateur. Les projections ne transforment pas un score public, une capacité, une absence de donnée ou un fichier hostile en décision métier. Les contrôles existants sont réutilisés ; aucun nouveau registre ni calcul implicite n’est nécessaire.

## Contrôles vérifiés

| Risque | Garde observée | Preuve |
|---|---|---|
| Fuite de marge/coût | `DataClassification.FINANCIAL_PRIVATE`, façades Patron-only, champs financiers absents des contrats Collaborateur | `test_decision_financial_boundary`, `test_actor_context_authorization`, `test_collaborator_work_tasks_api`, `test_collaborator_info_blockers_routes` |
| Pouvoir induit | catalogue de capacités Collaborateur sans décision/soumission financière ; ABAC refuse une capacité financière forgée | `test_capability_policy`, `test_authenticated_context_capabilities` |
| Déduction BOAMP | score limité aux signaux publics et explicables ; aucune aptitude financière déduite | `boamp_scoring.py`, `test_boamp_qualification.py`, routes opportunités Patron |
| RAG financier | `InMemoryVectorIndex` ignore `FINANCIAL_PRIVATE` et la recherche reste case/DCE-scoped | `test_knowledge_retrieval.py`, `test_case_dce_reading_routes.py` |
| Projection « À résoudre » | `economic_coverage` est construite uniquement pour `membership_id is None`, donc Patron ; le Collaborateur reçoit `null` | `test_case_resolution_api.py`, `test_case_resolution_index.py` |
| Inconnus et absence de preuve | deadline absente, capacité inconnue, contradiction et contenu hostile restent visibles dans leur état source ; aucun succès n’est déduit | fixtures G01–G09 et tests ciblés associés |

## Vérification exécutée

- 31 tests d’architecture/sécurité non base passent ;
- 29 tests API de frontières passent contre PostgreSQL Docker, avec 3 avertissements Starlette/httpx ;
- 9 tests unitaires G01–G09 passent hors base ;
- la suite web complète reste verte à 187/187, avec typecheck, lint et build déjà vérifiés dans l’audit accessibilité.

## Décision

Aucune modification de comportement n’est introduite dans cette tranche : les garde-fous sont déjà au bon niveau et les ajouter une seconde fois créerait deux autorités de confidentialité. La preuve est documentaire et testée ; toute nouvelle surface financière devra réutiliser les façades Patron et la classification existantes.

## Limites

La recette propriétaire doit encore vérifier visuellement qu’aucun texte d’interface ne suggère une acceptation implicite. L’audit automatisé ne remplace pas cette revue, mais aucune fuite ou élévation n’est observée dans les contrats et flux couverts.

## Références

- `backend/app/modules/case/infrastructure/resolution_reader.py`
- `backend/app/modules/knowledge/application/retrieval.py`
- `backend/app/modules/opportunity/application/boamp_scoring.py`
- `backend/tests/architecture/test_decision_financial_boundary.py`
- `backend/tests/security/test_capability_policy.py`
- `backend/tests/api/test_case_resolution_api.py`
- `docs/03_PRODUCT_DESIGN_WORKING/SMART_AO_PHASE9_ACCESSIBILITE_G01_G09_AUDIT_PREUVE_v0.1.md`
