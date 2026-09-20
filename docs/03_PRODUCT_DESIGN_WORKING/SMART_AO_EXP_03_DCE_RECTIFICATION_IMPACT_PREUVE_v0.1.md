# SMART AO — EXP-03 — Rectificatifs et impact ciblé — preuve verticale v0.1

**Statut : PREUVE VERTICALE EXÉCUTÉE · IMPACT CONSERVATEUR**  
**Autorité :** cahier produit/métier OWNER_CONSOLIDATED v0.4  
**Périmètre :** version rectificative, chaîne de provenance et invalidation ciblée des conclusions dépendantes

## Décision de tranche

Un rectificatif crée une nouvelle version DCE. Le corpus admis, les documents, les classifications et les exigences de la version précédente restent historisés. La version précédente devient `SUPERSEDED`, et seules les conclusions rattachées à cette version sont placées en revue ; aucune conclusion indépendante n’est réécrite ni supprimée.

Le code existant fournit cette preuve avec `DceVersion` et `CaseDceImpactService`. Aucun remplacement destructif, registre parallèle ou transition automatique vers une décision métier n’est ajouté.

## Contrat prouvé

1. `DceVersion.register` refuse le remplacement du corpus admis : un rectificatif porte un nouvel identifiant, un nouveau hash et une source de supersession obligatoire.
2. `mark_superseded_by` conserve la version précédente dans l’état `SUPERSEDED`, avec son lien vers le successeur et sa date ; elle reste lisible et auditable.
3. Le service d’impact exige la même Consultation, le Case encore attaché au prédécesseur, un successeur `ADMITTED` et `VERIFIED`, et une chaîne `predecessor_dce_version_id` cohérente. Les tenants sont vérifiés à chaque lecture.
4. Le manifeste d’impact inclut le Case, les deux versions et les exigences matérialisées. L’identité de run est déterministe et le rejeu retourne le run existant.
5. Le ledger append-only produit :
   - `DCE_VERSION_REPLACED` en `REVIEW_REQUIRED` ;
   - une ligne `PREVIOUS_REQUIREMENT_REQUIRES_REVIEW` pour chaque exigence issue du prédécesseur ;
   - une ligne `SUCCESSOR_REQUIREMENT_CANDIDATE` en `PENDING_HUMAN_REVIEW` pour chaque exigence du successeur.
6. Une version sans signal matérialisé donne `VERSION_HAS_NO_MATERIALIZED_SIGNAL` en revue. L’absence de signal ne vaut pas validation.
7. La lecture Case conserve la version applicable et sa readiness ; la recherche knowledge exclut les fragments d’une version `SUPERSEDED`. Les décisions, risques et confirmations ne sont pas mutés par le calcul d’impact.

## Limites assumées

- Cette tranche prépare un registre de revue ; elle ne valide pas automatiquement les exigences du successeur et ne clôt pas les tâches humaines.
- La propagation vers une vue unifiée « À résoudre » reste une tranche EXP-04.
- Les liens A2/A3/A4 génériques et les invalidations transversales au-delà du Case DCE sont différés jusqu’à une preuve métier dédiée.

## Vérification exécutée

- `backend/tests/application/test_case_dce_impact.py` : **3 tests passés** contre PostgreSQL Docker dédié.
- Cas couverts : chaîne et manifeste obligatoires, compteurs et projection fermés, acteur système, run append-only, états de revue, conservation des exigences précédentes et rejeu idempotent.
- `backend/tests/domain/dce/test_dce_version.py` et `backend/tests/application/test_knowledge_retrieval.py` : **12 tests passés** ; version superseded auditable et retrieval filtré vérifiés.
- La lecture Case a déjà une couverture dédiée de la version `SUPERSEDED` et de la projection tenant-scoped.

## Fichiers de preuve

- `backend/app/modules/dce/domain/dce_version.py`
- `backend/app/modules/dce/application/impact.py`
- `backend/app/modules/dce/application/handlers.py`
- `backend/app/modules/dce/infrastructure/models/case_dce_impact.py`
- `backend/app/modules/knowledge/infrastructure/dce_source.py`
- `backend/tests/application/test_case_dce_impact.py`
- `backend/tests/domain/dce/test_dce_version.py`
- `backend/tests/application/test_knowledge_retrieval.py`

## Étape suivante

Auditer la panne IA, les instructions hostiles et la poursuite manuelle sûre sans masquer l’échec ni envoyer d’action autonome.
