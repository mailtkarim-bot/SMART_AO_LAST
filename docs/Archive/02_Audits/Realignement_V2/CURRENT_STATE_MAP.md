# SMART AO — État réel avant réalignement v2

**24 septembre 2026 · T0, lecture seule du code · base examinée : `374510a`**  
**Statut :** audit de fichiers, non preuve d'exécution des nouvelles recettes v2. Le Product Freeze v1.0 reste l'autorité active.

## AS-IS

| Zone | Éléments vérifiés dans le dépôt | Frontière pour le candidat v2 |
|---|---|---|
| Affaire/DCE | `backend/app/modules/case/`, `backend/app/modules/dce/` ; versions, fragments, exigences, contradictions et impact DCE ; `20260920_0090_dce_contribution_conflicts.py` | Socle de source/version réutilisable. L'impact DCE existant ne prouve pas l'invalidation de tous les futurs objets contractuels. |
| Décision | `decision/infrastructure/models/{decision,risk,risk_requirement}.py`, `decision/application/{finalize,risk}.py` ; contexte gelé, risques CCAP/CCTP, conditions et finalisation Patron | `DecisionRiskRecord` a source, version DCE, locator, traitement. Il n'a pas le contrat de sanction, dérogation, droit ou carte à 12 axes. |
| Prix/capacité | `pricing/infrastructure/models/financial.py`, `pricing/domain/cost_basis.py`, `enterprise/infrastructure/models/enterprise.py`, `optimization/` | Scénarios et capacités existent ; aucun circuit de paiement, assurance-prestation ou coût post-réception dédié repéré. |
| Réponse/remise | `preparation/infrastructure/models/preparation.py`, `submission/infrastructure/models/submission.py` | Brouillons, paquet, autorisation, signatures et preuve de remise existent. Le registre d'engagement mesurable v2 n'est pas démontré. |
| Résultat/P6/P7 | `patron_action/infrastructure/models/{outcome,order,p6,p7,rex}.py` et `application/order.py` | `CaseP7ResultRecord` conserve résultat/source/réserves ; pas de paquet P7 v2 avec droits, sanctions, paiement et acceptation spécialisée. |
| Autorisation | `platform/security/{context,authorization}.py` ; acteur/tenant/MFA et `FINANCIAL_PRIVATE` filtrés côté serveur | Profil Responsable/Expert ne confère pas de droit. Classifications v2 « juridique sensible » et vues Patron/Expert restent à qualifier. |
| Recherche/IA | `knowledge/{domain,application}/retrieval.py` ; scope tenant/Affaire/version/classification et refus financier de requête | Contrat de retrieval existant ; pas de moteur d'applicabilité réglementaire ni calculateur contractuel autoritatif. Le refus par mots-clés ne prouve pas à lui seul l'absence de toute fuite indirecte. |
| UX | `web/src/app/canonicalSpaces.ts` ; C05 `PARTIAL`, C09 et C12 `BACKLOG`, C07/C08/C10/C13 `MATERIALIZED` ; panneaux décision/risques | Couverture de navigation ≠ parcours v2 prouvé. La carte Patron 12 axes et la protection contractuelle P7 n'y sont pas constatées. |
| Infrastructure | `backend/app/bootstrap/application.py`, `backend/alembic/versions/`, `backend/tests/` | Monolithe modulaire, dispatcher/idempotence, PostgreSQL/Alembic. Tête déclarée `20260920_0090` dans `platform/persistence/schema.py`. |

## Méthode et limites

Recherche ciblée des modèles, services, routes, composants, migrations et tests ; lecture des frontières risquées. Les noms conceptuels `REGULATORY_PROFILE`, `CONTRACTUAL_SANCTION`, `RIGHT_PRESERVATION_EVENT`, `PaymentCircuit` et `MeasurableCommitment` ne sont pas trouvés dans `backend/app`, `web/src` ou `backend/alembic`. **Cela établit l'absence de ces contrats nommés dans le code examiné, pas l'absence de toute logique apparentée.** Aucun test v2 ni migration n'a été lancé à ce stade.

Les objets et champs cités sont `VERIFIED` par lecture ; l'absence de capacité v2 complète est `PROBABLE` avant tests de caractérisation ; les points d'insertion ci-dessous sont des `PROPOSAL`.

## Points d'insertion minimaux

Conserver les modules et le dispatcher. Après promotion, caractériser d'abord les lecteurs DCE et les risques existants, puis placer l'applicabilité/règle versionnée derrière une frontière applicative dédiée ; intégrer les nouveaux faits contractuels par migrations additives. Les projections Patron et P7 consommeront ces faits sans devenir leur source de vérité.
