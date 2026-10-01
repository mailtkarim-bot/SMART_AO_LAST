# SMART AO — Phase 9 : matérialisation C00–C16 — audit et preuve v0.1

**État :** inventaire canonique matérialisé, rattachement structurel des surfaces prouvé
**Date :** 20 septembre 2026

Le registre `web/src/app/canonicalSpaces.ts` matérialise les 17 identifiants
canoniques adoptés par le catalogue (`C00` transversal et `C01` à `C16`). Pour
chaque espace il conserve le libellé, la destination de navigation éventuelle,
le statut réel (`MATERIALIZED`, `PARTIAL` ou `BACKLOG`) et les IDs de surfaces
à rattacher. Une entrée `BACKLOG` n'est jamais présentée comme un écran
disponible.

La première cartographie est volontairement honnête : les espaces C01, C02,
C04, C06, C07, C08, C10, C11 et C13 ont déjà une surface web identifiable ;
C00, C03, C05, C14, C15 et C16 restent partiels ; C09 et C12 n'ont pas encore
de surface web dédiée. Les preuves backend existantes ne sont pas converties
en écrans fictifs.

Preuve : le test de registre vérifie les 17 codes, l'unicité, les destinations
valides, l'obligation d'un rattachement de surface et l'égalité exacte des 104
IDs du catalogue. Les tests web globaux,
le typecheck, le lint et le build restent les contrôles de compilation et de
non-régression.
