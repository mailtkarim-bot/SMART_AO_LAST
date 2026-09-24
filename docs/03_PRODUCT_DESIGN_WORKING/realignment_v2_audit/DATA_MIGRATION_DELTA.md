# SMART AO — Delta de données v2 proposé

**24 septembre 2026 · conception T0, aucune migration écrite ou exécutée**  
Tête existante déclarée : `20260920_0090` (`backend/app/platform/persistence/schema.py`). Les noms ci-dessous sont conceptuels et restent à vérifier contre les conventions SQL/ORM avant toute PR.

| Tranche | Données additives proposées | Contrainte de preuve |
|---|---|---|
| T1 | Profil de faits d'Affaire, règle/version/date d'effet, évaluation d'applicabilité et liens source/version | Tenant, Affaire, version, dates avec fuseau, statut `UNKNOWN_APPLICABILITY`/`FUTURE` ; jamais de backfill « applicable » par défaut. |
| T2 | Baseline contractuelle, référence de règle, clause particulière et évaluation de dérogation | DCE/version/locator et auteur de validation ; conserver chaque ancienne version et la hiérarchie déclarée. |
| T3 | Règle de sanction, paramètres validés, scénario calculé ; événement de préservation des droits, preuve d'envoi et accusé séparés | Unité/monnaie/formule/règle source explicites ; unique `(tenant, command/idempotency)` ; aucun délai certain sans trigger et règle applicables. |
| T4 | Instruction de modification/OS, jalon de réception/règlement, exposition de résiliation | Historique append-only, source, statut et relation à l'Affaire/lot ; pas d'état DGD conclu sans conditions prouvées. |
| T5 | Évaluation assurance, prérequis HSE, engagement mesurable, circuit de paiement, obligation post-réception et dépendance tierce | Classification et accès par objet ; montants Patron-only ; l'absence devient `NOT_ESTABLISHED`, jamais `COVERED` ou zéro. |
| T6–T7 | Lectures dérivées Carte d'Engagement et paquet P7 versionné/accepté | Projections reconstruites depuis les faits ; pas de seconde vérité ; P7 ancien conservé. |

## Séquence sûre à prouver par PR

1. Créer tables/colonnes vides et index tenant + Affaire + version pertinents ; ajouter FK composites tenant-scoped et checks fermés.
2. Déployer code capable de lire l'ancien schéma pendant la transition, puis introduire l'écriture derrière le service/commande existant.
3. Backfill seulement les correspondances prouvables par source/version. Marquer le reste `UNKNOWN` ou `REVIEW_REQUIRED`.
4. Comparer ancien/nouveau sur copie représentative anonymisée ; tester concurrence, idempotence et append-only.
5. Basculer les lectures après validation, puis durcir les contraintes. Un rollback **applicatif** revient au code antérieur sans effacer les faits nouveaux ; un downgrade SQL destructif de preuves ne doit pas être automatisé.

## Bloqueurs

La cardinalité exacte des objets, les champs obligatoires, les index et le backfill ne sont pas encore validés par des données représentatives. Le dossier Golden DCE et la qualification juridique/assurantielle manquent. Cette note est un delta conceptuel, pas un script de migration prêt à lancer.
