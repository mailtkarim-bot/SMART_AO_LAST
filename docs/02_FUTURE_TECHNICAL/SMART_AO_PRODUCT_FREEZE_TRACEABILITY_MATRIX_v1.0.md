# SMART AO — Matrice de traçabilité Product Freeze v1.0

**Statut :** matrice d’exécution initiale  
**Date :** 20 septembre 2026  
**Référence :** `SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md`

Cette matrice relie les décisions gelées aux points d’implémentation déjà présents. `PROUVÉ` signifie qu’un test ou une preuve ciblée existe ; `PARTIAL` conserve explicitement un travail restant.

| Exigence gelée | Code principal | Tests/preuves | Migration/donnée | Exploitation | État |
|---|---|---|---|---|---|
| Affaire progressive et idempotente | `case_creation.py`, `case/application/handlers.py` | `test_consultation_authenticated_api.py`, PUX-01 | `cases`, reçus de commande | logs `command_id`/correlation | PROUVÉ |
| MFA avant métier | `dependencies/auth.py`, `authentication.py`, `MfaPanel.tsx` | tests auth/MFA, App | sessions, facteurs, recovery | révocation et step-up | PROUVÉ |
| Tenant/rôle/affectation serveur | `security/context.py`, `authorization.py`, `case_assigned.py` | actor policy, collaborator boundary | membership/assignments | audit refus neutre | PROUVÉ |
| Propriété et continuité | `membership` governance services | C14/C15 tests PostgreSQL | migrations `0085–0088` | `NO_ACTIVE_OWNER`, R03 | PROUVÉ |
| Sources BOAMP et P0/P1 | `opportunity/boamp_qualification.py` | qualification and G01–G09 tests | observations/qualifications | panne source/manual intake | PROUVÉ |
| DCE staging/admission | `dce/application/upload.py`, handlers | DCE staging/upload suites | DCE staging/version tables | antivirus fail-closed | PROUVÉ |
| Extraction sourcée | `dce/application/extraction.py` | PDF/DOCX/XLSX/protected tests | extraction fragments | storage private/hash | PROUVÉ |
| Classification et inconnues | `dce/application/classification.py`, requirements | classification/requirements tests | readiness/requirements | `PARTIAL` visible | PROUVÉ |
| Contradictions et résolution humaine | `contribution_conflicts.py` | N01/G03 PostgreSQL tests | migrations `0090` | resolution reason retained | PROUVÉ |
| Décision GO/NO-GO | `decision/application/finalize.py` | decision/gate suites | decisions/contexts/conditions | Patron audit | PROUVÉ |
| Confidentialité financière | `DataClassification`, Patron facades | financial boundary suites | financial snapshots private | no amounts Collaborateur | PROUVÉ |
| Prix et capacités | `pricing`, `enterprise`, `optimization` | pricing/capacity tests | snapshots/scenarios/runs | no reservation inference | PARTIAL portes P2/P3/P4 |
| Réponse technique | `preparation/application/review.py` | draft/review tests | generated docs/reviews | source/hash/version | PROUVÉ sur noyau |
| Candidate et manifeste | `submission/application/service.py` | package/P5/evidence suites | migrations `0071–0075` | manifest integrity | PROUVÉ |
| Signature/P5/export | submission routes/services | signature/export tests | manifest hash records | external `NOT_PERFORMED` | PROUVÉ |
| Résultat par lot/P6/P7 | `patron_action/application/order.py`/`outcome.py` | EXP-07 suites | migrations `0076–0084` | UNKNOWN/INTERRUPTED | PROUVÉ |
| REX et capitalisation | `patron_action/application/rex.py` | REX/capitalisation tests | append-only REX | scopes bounded | PROUVÉ |
| Accessibilité et responsive | `web/src/app/App.tsx`, `styles.css` | 187 web tests, build/lint | n/a | manual reader/zoom pending | PROUVÉ structurel |
| IA/RAG borné | `knowledge/application/retrieval.py` | retrieval/security tests | embeddings non financiers | provider outage/manual | PROUVÉ noyau |
| Observabilité et outbox | `platform/events`, audit records | command/outbox/security tests | domain events/outbox | correlation/retry status | PROUVÉ noyau |

## Gaps explicites

- les portes P2/P3/P4 restent `PARTIAL` tant que leurs preuves et responsables ne sont pas séparés ;
- les parcours PUX partiels et la recette lecteur d’écran réelle restent à fermer ;
- la restauration, l’observabilité de production, la rotation opérationnelle des secrets et le cahier d’exploitation détaillé restent Phase 10/11 ;
- aucun gap ne peut être fermé par un statut UI ou un score.

## Règle de maintenance

Toute nouvelle exigence du Product Freeze doit ajouter une ligne avec un chemin de code, un test, une donnée/migration et une procédure d’exploitation. Une ligne sans preuve reste `PARTIAL`.
