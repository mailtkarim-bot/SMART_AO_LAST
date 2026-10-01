# SMART AO — EXP-07 : OWNER EXPERIENCE FREEZE

**Statut :** GEL D’EXPÉRIENCE DÉLÉGUÉ · PREUVES EXÉCUTÉES · RÉCEPTION EXTERNE NON PRÉSUMÉE  
**Date :** 20 septembre 2026  
**Autorité :** délégation propriétaire explicite reçue dans le fil Codex  
**Références :** cahier OWNER v0.4, catalogue OWNER_CONSOLIDATED v0.3, contrats EXP-07 résultat, transmission, REX, capitalisation et rétention.

## 1. Périmètre gelé

EXP-07 couvre le cycle de fin d’Affaire et de passation sans réécrire son historique :

```text
résultat par lot WON / LOST / UNKNOWN
  → transmission des seuls lots WON
  → commande ACCEPTED / REJECTED
  → contrôle P6 APPROVED / REJECTED
  → résultat P7 COMPLETED / UNKNOWN / INTERRUPTED
  → REX local ou réemployable selon source et validation
  → suspension / reprise / fermeture
  → demande d’export et conservation de preuve
```

Chaque fait est append-only, tenant-scopé, attribué à son auteur et idempotent. L’état commercial courant n’est jamais utilisé comme preuve de ces actes.

## 2. Arbitrages gelés

| Sujet | Décision |
|---|---|
| Résultat | `WON` exige une source ; `UNKNOWN` exige un motif ; un lot hors périmètre est refusé. |
| Transmission | Seuls les engagements `WON` sont transmis, avec leurs réserves. |
| Commande / P6 / P7 | Ce sont trois faits distincts. P6 exige une commande `ACCEPTED`; P7 exige P6 `APPROVED`. |
| États difficiles | `UNKNOWN` et `INTERRUPTED` restent non conclusifs. Ils ne deviennent ni succès, ni fermeture implicite. |
| REX | Un REX local peut documenter un inconnu. Le réemploi entreprise exige P7 `COMPLETED`, source et validation `APPROVED`. |
| Suspension / fermeture | `CLOSED` exige un P7 `COMPLETED`; une suspension ouverte, notamment `OPEN_LITIGATION`, interdit la fermeture jusqu’à une reprise append-only. |
| Export | `CASE_EXPORT_REQUESTED` prépare une sortie de dossier ; il n’affirme aucun envoi ni réception par un tiers. |
| Conservation | Une preuve conservée porte sa référence interne, sa base et son échéance ; elle ne supprime ni ne transforme les faits antérieurs. |

## 3. Rôles, refus et limites

- les actes EXP-07 sont Patron-only ; les Collaborateurs sont refusés ;
- les contrôles tenant, périmètre de lot, chaîne `WON → ACCEPTED → APPROVED → P7` et idempotence restent côté serveur ;
- un P7 `UNKNOWN` ou `INTERRUPTED` interdit la fermeture ;
- un litige est exprimé par une suspension `OPEN_LITIGATION`, sans registre de litige parallèle inventé ;
- `external_receipt: NOT_PERFORMED` reste l’unique position sur la réception externe tant qu’une preuve contrôlée n’est pas intégrée.

## 4. Critères d’acceptation observables

1. Le Patron distingue clairement résultat, commande, P6, P7 et REX pour chaque lot.
2. Un lot non gagné, une commande refusée ou un P6 refusé ne progresse pas dans la chaîne.
3. Un P7 inconnu peut produire un REX local, jamais une règle de succès ni une fermeture.
4. Une suspension litigieuse bloque la fermeture jusqu’à un acte de reprise explicitement enregistré.
5. Une demande d’export reste une intention auditée ; aucune interface ne l’affiche comme une réception externe.
6. La conservation rend la base et l’échéance de conservation explicites sans effacer les preuves.

## 5. Preuves exécutées

- PostgreSQL ciblé : **9 tests** sur contrat de résultat, lecture Patron, chaîne commande/P6/P7/REX, suspension, fermeture, export et conservation ;
- refus Collaborateur prouvé pour lecture de résultat, commande et demande d’export ;
- tête Alembic contrôlée jusqu’à `20260920_0084` ;
- Ruff, format Ruff, compilation et `git diff --check` passent.

## 6. Limites assumées

Ce gel ne crée pas de connecteur de portail, d’accusé de réception tiers, de livraison automatique, de registre juridique de litige ou de purge physique. Une demande d’export, une conservation interne et une fermeture ne constituent jamais une preuve de réception ou d’exécution par un tiers.

## 7. Effet du gel

EXP-07 est gelée. Toute extension de dépôt, livraison, réception externe, conservation légale automatisée ou contentieux devra apporter sa propre source, ses états d’incertitude, son autorisation et sa preuve verticale.

**Prochaine étape :** ouvrir la phase 8 en cadrant C14 — membres, rôles, délégations, suspension, relève et dernier Propriétaire compromis.
