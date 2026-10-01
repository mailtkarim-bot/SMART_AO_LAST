# SMART AO — EXP-05 : OWNER EXPERIENCE FREEZE

**Statut :** GEL D’EXPÉRIENCE DÉLÉGUÉ · PREUVES EXÉCUTÉES · COUVERTURE P2/P3/P4 `PARTIAL`  
**Date :** 15 septembre 2026  
**Autorité :** délégation propriétaire explicite reçue dans le fil Codex  
**Références :** cahier OWNER v0.4, catalogue OWNER_CONSOLIDATED v0.3, [`SMART_AO_EXP_05_REPONSE_PRIX_AUDIT_CADRAGE_v0.1.md`](SMART_AO_EXP_05_REPONSE_PRIX_AUDIT_CADRAGE_v0.1.md) et [`SMART_AO_EXP_05_P2_P3_P4_AUDIT_CADRAGE_v0.1.md`](SMART_AO_EXP_05_P2_P3_P4_AUDIT_CADRAGE_v0.1.md)

## 1. Périmètre gelé

EXP-05 couvre la préparation contrôlée de la réponse et du prix :

```text
source prix reçue
  → preview et batch normalisé
  → commit financier validé et versionné
  → couverture économique Patron, inconnus et capacités sourcées
  → plan de réponse technique versionné
  → revue Patron et paquet préparé sans dépôt externe
```

Le produit reste explicite sur ce qui est connu, inconnu, bloqué ou à vérifier. Aucun montant n’est ajouté aux contrats Collaborateur et aucun dépôt n’est déclaré réussi.

## 2. Arbitrages gelés

| Sujet | Décision |
|---|---|
| Autorité | Le serveur détermine tenant, rôle, affectation, révision et classification ; le navigateur ne fournit pas une autorité de décision. |
| Prix | Preview, commit et scénarios réutilisent les agrégats existants ; source, hash, révision et erreurs restent visibles. |
| Reprise | Un résultat réseau inconnu reste `UNKNOWN`/« À VÉRIFIER » et se rejoue avec les mêmes identifiants ; aucune réussite n’est présumée. |
| Couverture économique | Hypothèses, devis non démontré, capacité et prévision de trésorerie sont des états sourcés ; ils n’autorisent ni financement sécurisé, ni réservation, ni feu vert implicite. |
| Moyens | Les capacités internes versionnées et leurs preuves validées peuvent être relues ; une pièce expirée ou non validée bloque l’utilisation. |
| Partenaires/groupements | Aucun engagement, mandat, lot/share ou composition n’est inventé tant qu’un contrat dédié n’existe pas. |
| Plan de réponse | Le Collaborateur crée un brouillon technique non financier avec sections, sources et rôle ; le Patron relit les métadonnées versionnées. |
| P2/P3/P4 | Les portes sont contrôlées comme `PARTIAL` et non autorisantes : leurs informations manquantes restent visibles au lieu d’être remplacées par un GO. |
| Remise | Le package conserve manifeste, versions et `external_submission: NOT_PERFORMED` ; l’export exige la garde de décision et reste Patron-only. |

## 3. États et refus prouvés

- import confirmé, rejeté ou `UNKNOWN` après panne réseau ;
- batch ou préparation à révision périmée : `VERSION_CONFLICT` ;
- scénario sans snapshot officiel publié : refus ;
- couverture économique absente ou incomplète : `NOT_DEMONSTRATED`, jamais zéro ;
- capacité expirée, preuve absente ou non validée : refus avant paquet ;
- brouillon technique contenant un terme financier : refus serveur ;
- Collaborateur : package assigné et données non financières seulement ;
- Patron/Patron Delegate : lecture des brouillons et des états selon autorisation ;
- décision `NO_GO`, conditions ouvertes, risques non résolus ou exigences DCE non confirmées : préparation/export bloqués ;
- manifeste altéré ou document privé indisponible : export refusé, aucun succès externe annoncé.

## 4. P2/P3/P4 et fidélité d’expérience

La revue affiche les éléments nécessaires à une décision future, mais ne simule pas de commande inexistante :

| Porte | Surface visible | Sortie actuelle |
|---|---|---|
| P2 | contexte de décision, références, inconnus, risques et limites de moyens/partenaires | `PARTIAL`, revue requise |
| P3 | couverture économique Patron, snapshot/prix versionnés, hypothèses et états de capacité/trésorerie | `PARTIAL`, aucune acceptation économique enregistrée |
| P4 | plan de réponse, brouillons versionnés, readiness, documents générés et paquet candidat | `PARTIAL`, aucune autorisation d’offre distincte |

Les conflits de contexte et de révision sont refusés côté serveur. Une nouvelle version de pièce, de prix, de lot ou d’engagement doit provoquer une future réévaluation ; aucune invalidation globale fictive n’est introduite dans ce gel.

## 5. Critères d’acceptation observables

1. Le Patron voit la provenance et l’état de chaque couverture économique sans montant dans cette surface.
2. Le Collaborateur peut créer et relire son plan de réponse sans accéder à la marge, aux CV ou aux pièces privées.
3. Le Patron peut relire les mêmes métadonnées avant la revue et distinguer brouillon, revue et paquet préparé.
4. Une erreur connue permet une correction ; un résultat inconnu conserve l’intention et propose le rejeu identique.
5. Une révision obsolète, une décision non prête ou une preuve expirée est bloquée avec un code explicite.
6. Aucun état `PARTIAL`, `UNKNOWN` ou `BLOCKED` n’est rendu comme GO, offre autorisée ou remise effectuée.

## 6. Limites assumées

Ce gel ne couvre pas la complétude de la réponse, les engagements contractuels, les partenaires/groupements, le calcul complet de marge, une réservation de capacité, l’invalidation automatique par rectificatif ou un dépôt externe. Ces sujets exigent des contrats et des preuves séparés. Les portes P2/P3/P4 restent donc explicitement partielles.

## 7. Preuves exécutées

- pricing et reprise : 121 tests PostgreSQL dédiés, front complet 154 tests, typecheck, lint et build ;
- préparation, revue et plans de réponse : 42 tests PostgreSQL ciblés ;
- confidentialité, remise et garde de décision : 46 tests PostgreSQL ciblés ;
- revue P2/P3/P4 : tests domaine de la garde, finalisation, gate non financier et package de soumission ;
- Ruff ciblé, mypy ciblé et `git diff --check` passent.

## 8. Effet du gel

EXP-05 peut avancer vers la prochaine tranche sans rouvrir la provenance, la reprise, la séparation Patron/Collaborateur, les contrôles de révision ni le refus de dépôt implicite. Toute extension P2/P3/P4 doit apporter une commande métier explicite, une source vérifiable, une version, une preuve de conflit et une recette verticale.

**Prochaine étape :** ouvrir EXP-06 sur la candidate, le manifeste, l’autorisation P5 et la remise humaine, en réutilisant les garde-fous EXP-05.
