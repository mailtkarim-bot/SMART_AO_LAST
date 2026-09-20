# SMART AO — EXP-05 — Audit P2/P3/P4, conflits et versions v0.1

**Statut :** AUDIT EXÉCUTÉ · COUVERTURE PARTIELLE ASSUMÉE · AUCUN GO IMPLICITE  
**Date :** 15 septembre 2026  
**Autorité :** cahier produit/métier `OWNER_CONSOLIDATED v0.4` et catalogue `OWNER_CONSOLIDATED v0.3`  
**Références :** [`SMART_AO_EXP_05_REPONSE_PRIX_AUDIT_CADRAGE_v0.1.md`](SMART_AO_EXP_05_REPONSE_PRIX_AUDIT_CADRAGE_v0.1.md), [`SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md`](../00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md)

## 1. Objet de l’audit

Le cahier OWNER R04 définit P2 comme le GO de principe, P3 comme le GO économique et P4 comme l’autorisation de l’offre. L’audit vérifie si ces portes existent comme décisions séparées dans le code vivant, si elles gardent une version et une preuve, et si un état incomplet peut être présenté comme prêt.

Le vocabulaire P2/P3/P4 ne doit pas être confondu avec les niveaux de fidélité visuelle P1/P2/P3 du catalogue UX. Ici, il s’agit de portes métier.

## 2. Matrice de preuve

| Porte | Preuves actuellement réutilisables | Contrôle de version/conflit | Écart réel | Verdict |
|---|---|---|---|---|
| **P2 — GO de principe** | `FreezeDecisionContextHandler` vérifie l’Affaire, les références DCE, les inconnus et les risques avant de geler un contexte de décision. `DecisionContext` conserve un fingerprint et des références immuables. | `expected_revision`, références d’agrégats et fingerprint affiché sont contrôlés ; une décision périmée est refusée. | Aucun champ typé ne porte encore l’éligibilité par phase/lot, la visite, la charge d’étude, les partenaires ou le MIRP. Aucun acte `P2_GO` séparé n’existe. | **PARTIAL / NON AUTORISANT** |
| **P3 — GO économique** | L’import prix garde source, hash, lignes normalisées et révisions. La couverture économique Patron expose hypothèses, devis non démontré, capacité et prévision de trésorerie. Les scénarios partent d’un snapshot publié. | Le commit financier refuse révision obsolète, erreurs et publication concurrente ; les transitions sont append-only. | Aucun acte P3 versionné n’enregistre l’acceptation d’un scénario, d’une marge, d’un prix plancher, d’une capacité ou d’une trésorerie. Les données complètes de marge et de devis restent manquantes. | **PARTIAL / NON AUTORISANT** |
| **P4 — Autoriser l’offre** | Le package de préparation conserve une version de manifeste, un document technique généré, un snapshot financier officiel et `external_submission: NOT_PERFORMED`. Les brouillons techniques sont versionnés et relus par le Patron. | Le package vérifie la révision de préparation, la readiness, le document courant, le snapshot publié et l’intégrité SHA-256 du manifeste. La soumission vérifie ensuite la porte de décision. | Aucun acte P4 distinct ne valide la complétude de réponse, les engagements, le périmètre de lots ou un brouillon `ACCEPTED_CANDIDATE`. Le code prépare le paquet et ne doit pas le présenter comme offre autorisée. | **PARTIAL / NON AUTORISANT** |

## 3. Porte réellement démontrée aujourd’hui

La garde `evaluate_submission_gate` est une garde de préparation/remise en aval. Elle exige une décision `FINALIZED`, un contexte `FROZEN`, un résultat `GO` ou `CONDITIONAL_GO` satisfait, les exigences DCE confirmées et aucune action de risque non résolue. Elle refuse `NO_GO`, les conditions ouvertes, les exigences non confirmées et les incohérences de snapshot.

Cette garde constitue une barrière de sécurité pour préparer ou exporter un paquet. Elle ne prouve pas à elle seule que P2, P3 et P4 ont été décidées séparément. La préparation reste donc fermée par défaut lorsque la décision, le prix officiel, la readiness ou les preuves de capacité ne sont pas disponibles.

## 4. Conflits, versions et résultat inconnu

- Un contexte de décision conserve les références et le fingerprint effectivement affichés ; une modification du contexte ou de la révision provoque un refus.
- Une préparation et un brouillon technique portent une révision attendue ; une écriture concurrente retourne `VERSION_CONFLICT`.
- Un package de remise est immuable par version et son manifeste est vérifié par SHA-256 avant lecture du stockage privé.
- Les réponses et prix gardent des identifiants et des versions distincts ; aucun « dernier clic gagne » ni succès de dépôt externe n’est présumé.
- Il manque encore une règle transversale qui invalide automatiquement un P2/P3/P4 lorsqu’un rectificatif, un prix, une pièce, un engagement ou un lot change. Cette règle est explicitement laissée à une future tranche plutôt que simulée par un booléen global.

## 5. Décision de cadrage

Le code actuel est suffisant pour une preuve de préparation contrôlée et pour empêcher un export lorsque la décision aval n’est pas prête. Il ne justifie pas l’ajout immédiat de trois nouveaux agrégats P2/P3/P4 : les sources métier correspondantes (visite, partenaires, charge, engagement, marge complète) ne sont pas encore modélisées de façon vérifiable.

Le gel d’expérience EXP-05 peut donc être prononcé avec une couverture `PARTIAL` : le produit montre les états connus, les inconnus et les refus, mais ne transforme aucune absence en GO. Une future tranche pourra ajouter une porte typée seulement lorsqu’elle réutilisera des sources et une preuve de version suffisantes.

## 6. Vérifications

- `backend/tests/domain/test_decision_submission_gate.py` couvre les états READY/BLOCKED, les conditions, les risques non résolus et les snapshots invalides.
- `backend/tests/application/test_decision_finalization.py` couvre le contexte gelé, le fingerprint, les exigences DCE et les conflits de révision.
- `backend/tests/application/test_submission_decision_gate.py` couvre le refus avant stockage et la lecture non financière du gate.
- `backend/tests/application/test_submission_package.py` couvre la préparation du manifeste, les versions, la concurrence et l’export Patron-only.

Les résultats exécutés sont consignés dans le plan global et le gel d’expérience. Les limites `PARTIAL` restent opposables jusqu’à l’apparition d’un contrat de source et d’une commande métier explicite pour la porte concernée.

## Prochaine étape

Exécuter la revue verticale EXP-05 sur les états `PARTIAL`, `BLOCKED`, conflit de révision et résultat inconnu, puis consigner le gel d’expérience sans déclarer P2/P3/P4 complets.
