# SMART AO — MANDAT CODEX DE RÉALIGNEMENT MÉTIER v2.0
## Audit d'existant → plan de migration → implémentation contrôlée

**Date :** 24 septembre 2026  
**Statut :** MANDAT ACTIF — AUDIT T0 TERMINÉ ; IMPLÉMENTATION PAR TRANCHES  
**Repo :** `mailtkarim-bot/SMART_AO_LAST`

## 1. Autorités à lire avant toute modification

Dans cet ordre :

1. `docs/00_REFERENCE_ACTIVE/SMART_AO_CAHIER_DIRECTEUR_METIER_MASTER_v2.0.md` — profondeur métier et documentaire ;
2. `docs/00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v2.0.md` — contrat produit actif ;
3. `docs/02_FUTURE_TECHNICAL/SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v2.1.md` — traduction technique ;
4. index/catalogue/fondations UX actifs ;
5. architecture logicielle v3.1 et preuves Phase 0 ;
6. code, migrations et tests actuels — preuve de ce qui existe, jamais autorité pour réduire le métier.

## 2. Mandat actif — audit T0 terminé avant T1

L'audit T0 a été produit dans `docs/03_PRODUCT_DESIGN_WORKING/realignment_v2_audit/`. Toute nouvelle tranche commence par son contrat, son test et son rollback.

Produire :

- `CURRENT_STATE_MAP.md` : modules, tables, modèles, services, routes, projections, workers, événements, tests et UX associés ;
- `MASTER_V2_TRACEABILITY_MATRIX.md` : chaque exigence PF2/Master → `COVERED / PARTIAL / MISSING / CONTRADICTED / DEFERRED / EXTERNAL_VALIDATION` ;
- `KEEP_ADAPT_REPLACE_DELETE_ABSENT.md` : décision par composant actuel ;
- `DATA_MIGRATION_DELTA.md` : nouveaux objets/champs/index/contraintes/backfills, avec rollback ;
- `AUTHORIZATION_DELTA.md` : Patron/Collaborateur/Expert/Admin/Support/Tiers + classifications ;
- `AI_RAG_DELTA.md` : où le LLM intervient, où la logique doit être déterministe, protections prompt-injection ;
- `UX_IMPACT_DELTA.md` : impacts C01/C05/C07/C08/C09/C10/C12/C13 sans inventer de route ;
- `TEST_GAP_MATRIX.md` : recettes REC-29–45 et TECH-CR-* ;
- `PR_PLAN.md` : petites tranches verticales, dépendances, gates, rollback et preuves attendues.

## 3. Règles absolues

1. Pas de rewrite global.
2. Pas de microservice créé par anticipation.
3. Pas de nouvelle règle métier dans une route HTTP ou un composant React.
4. Pas de délai juridique, plafond de pénalité, franchise ou formule codé en dur sans source/version/applicabilité.
5. Pas de LLM comme calculateur ou autorité finale pour deadline, sanction, cash, couverture assurance ou conformité.
6. Pas de donnée financière dans contrats Collaborateur, recherche, RAG, notification, logs ou exports non autorisés.
7. `UNKNOWN`, `PARTIAL`, `REVIEW_REQUIRED`, `FUTURE`, `EXPIRED` restent des états de premier rang.
8. Tâche terminée ≠ exigence satisfaite ≠ droit préservé ≠ preuve reçue.
9. Envoi ≠ réception ; export ≠ dépôt ; dépôt déclaré ≠ reçu vérifié.
10. Toute action sensible est idempotente, tenant-scoped, auditable et soumise aux politiques serveur.
11. Un rectificatif invalide uniquement les dépendances touchées.
12. Une donnée réglementaire ou contractuelle externe est non fiable jusqu'à qualification et ne peut commander le système.
13. Tout calcul financier/contractuel critique doit être reproductible à partir des paramètres/sources versionnés.
14. Toute migration doit être additive ou accompagnée d'un plan de compatibilité et rollback explicite.
15. Aucun ancien test ne justifie de conserver un comportement qui contredit le nouveau contrat produit ; adapter le test après décision explicite.

## 4. Priorité d'implémentation après GO propriétaire

### T0 — caractérisation
Aucun changement métier. Verrouiller état réel et tests.

### T1 — fondations preuve/applicabilité
Profil réglementaire, règles versionnées, applicabilité, graphes de dépendance et invalidation.

### T2 — contrat/dérogations
Baseline contractuelle, références, dérogations, affichage source → impact.

### T3 — sanctions et droits
Pénalités structurées, `RIGHT_PRESERVATION_EVENT`, calendrier et calculs déterministes.

### T4 — modifications et comptes
OS/travaux supplémentaires, réception, décompte/DGD, résiliation/substitution.

### T5 — assurance/HSE/engagements/paiement
Évaluation assurance, prérequis exécution, engagements mesurables, circuit de paiement et post-réception.

### T6 — Carte d'Engagement
Projection Patron 12 axes, conditions GO, aucun score opaque.

### T7 — P7 renforcé
Passation complète avec droits, sanctions, paiement, engagements et responsables.

### T8 — REX
Prévu/réalisé, calibration et capitalisation contextuelle.

## 5. Gate de chaque tranche

Une tranche ne passe pas si :

- tests tenant/confidentialité échouent ;
- une conclusion critique n'a pas de source/version ;
- le rollback n'est pas défini ;
- une nouvelle abstraction n'a pas de cas réel/test ;
- un état inconnu est converti en succès ;
- le frontend peut fabriquer autorité ou valeur financière ;
- une règle réglementaire future bloque prématurément une affaire ;
- un délai contractuel est présenté comme certain sans base sourcée ;
- le RAG voit une donnée interdite au rôle ;
- une migration détruit une preuve historique.

## 6. Sortie attendue de Codex avant première PR fonctionnelle

Codex doit remettre un verdict :

- **READY_FOR_IMPLEMENTATION** : traçabilité complète, migrations/tests/rollback prêts ;
- **READY_WITH_BLOCKERS** : plan valable mais validations externes ou décisions propriétaire manquantes ;
- **NOT_READY** : architecture/existant ne permet pas encore une migration sûre.

Le verdict contient les preuves et les blockers précis. Aucun « tout est bon » sans matrice.

## 7. Définition de terminé

Le travail n'est terminé que lorsque :

- Product Freeze v2.0 promu ;
- cahier technique v2.1 aligné ;
- matrice de traçabilité sans `MISSING` C1 non arbitré ;
- migrations exécutées et testées ;
- recettes métier et sécurité vertes ;
- UX impactée mise à jour et validée ;
- documentation active mise à jour ;
- code et tests correspondent au contrat produit ;
- aucune promesse marketing n'excède la preuve produit.
