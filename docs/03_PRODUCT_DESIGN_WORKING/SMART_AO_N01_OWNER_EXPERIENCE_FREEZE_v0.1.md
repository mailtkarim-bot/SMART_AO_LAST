# SMART AO — N01 — OWNER EXPERIENCE FREEZE v0.1

**Objet :** contributions concurrentes sur une exigence DCE et résolution humaine
**État :** prouvé côté PostgreSQL, service et garde de validation
**Date :** 20 septembre 2026

## Décision gelée

Une proposition humaine ne remplace jamais silencieusement celle d'un autre
acteur. Chaque contribution conserve son auteur, sa source, son empreinte, la
révision observée et l'horodatage. Deux propositions différentes pour la même
exigence et la même révision ouvrent un conflit durable.

La validation ordinaire est refusée tant qu'une résolution append-only n'a pas
désigné l'une des contributions. La résolution conserve son auteur, son motif,
la contribution retenue et ses identifiants de commande. Elle ne supprime ni ne
réécrit les propositions concurrentes.

## Contrat réalisé

- `dce_requirement_contributions` conserve les propositions concurrentes et
  rend la répétition idempotente par auteur et clé d'idempotence ;
- `dce_requirement_conflicts` ouvre au plus un conflit par exigence et révision
  observée ;
- `dce_requirement_conflict_resolutions` ferme le conflit par l'existence d'un
  acte append-only, avec sélection contrôlée d'une des deux contributions ;
- l'absence de résolution lève `DCE_REQUIREMENT_CONFLICT_OPEN` avant toute
  confirmation classique ;
- un acteur `SYSTEM` ou une adhésion non active ne peut pas produire ni résoudre
  une contribution.

La source est un locator métier libre et l'empreinte est une SHA-256 fournie
par le producteur de la contribution. Aucun texte de source n'est réécrit et
aucune décision n'est déduite du dernier enregistrement reçu.

## Preuve

La migration `20260920_0090` est appliquée par le schéma runtime. Les deux
tests PostgreSQL de
[`test_dce_contribution_conflicts.py`](../../backend/tests/security/test_dce_contribution_conflicts.py)
prouvent :

1. deux propositions différentes sont retenues, le conflit bloque la
   validation, puis une résolution le ferme ;
2. le rejeu d'une même intention restitue la contribution existante sans en
   créer une nouvelle.

La suite consolidée C15/C16/N01 totalise `58 passed`.

## Limites assumées

La tranche prouve le registre et la garde de persistance. Une route HTTP et une
surface front dédiées pourront exposer la comparaison et l'acte de résolution
après un contrat de présentation ; aucune résolution n'est envoyée
automatiquement et aucune intégration externe n'est présumée.
