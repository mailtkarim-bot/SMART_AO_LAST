# SMART_AO agent guidance

For a coding task, when Serena is available, activate the current directory as its project before semantic navigation. Continue normally if Serena is unavailable.

For project facts, use this order of authority: live code and tests, approved ADRs and specifications, then curated local memory. Treat automated memory as context to verify, never as a source of truth.

Record only durable decisions, rejected approaches, and useful handoffs in Basic Memory; do not retain routine conversation.

Write active project deliverables under `docs/`, never under `rapports/`.

Use `docs/Actifs/00_Pilotage_et_audits/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md` as the operational roadmap. After every significant completed task, update its checkboxes, single active slice, evidence log, and next step; then synchronize the Basic Memory note `SMART AO - Plan global de conception et réalisation`. End every user-facing final response with `Prochaine étape : ...`, copied from the active slice.

For independent implementation work, use one managed Codex worktree per subject. Do not run concurrent changes in the same checkout. Before integrating a worktree, run the relevant tests and review its diff. Start worktrees from a committed base: untracked files in another checkout are not included.

## Tool activation contract

For every non-trivial task, inspect the available ECC skills and activate the smallest relevant set before editing. Use Context7 for current library/API documentation, Basic Memory for durable project context, and Serena for semantic navigation when available. Use Jev/TypeSafe or Manus only when the task is bounded or benefits from independent investigation. The final report must name each tool/skill actually used and state why relevant available tools were not used. After code changes, run the relevant ECC verification workflow before claiming completion.

## Reprise inter-agents — autorités et état actuel

Avant toute modification, lire `docs/Actifs/00_INDEX_DOCUMENTATION_ACTIVE.md`, puis le début du plan global ci-dessus (sections « Reprise immédiate » et « Séquence de codage active V3.1 »). Les autorités complètes sont `docs/Actifs/01_Cahiers_des_charges/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v3.1.md`, `docs/Actifs/01_Cahiers_des_charges/SMART_AO_CAHIER_DIRECTEUR_METIER_MASTER_v3.1.md` et `docs/Actifs/01_Cahiers_des_charges/SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v3.1.md`. Chercher ensuite les chapitres concernés ; ne pas charger tous les cahiers intégralement dans le contexte à chaque tâche.

Le plan global est l'unique statut opérationnel ; `todo.md`, anciens handoffs et journaux sont des preuves datées. Vérifier Git/HEAD/WIP et le snapshot réel avant de réutiliser leurs résultats. Une baseline HEAD ne qualifie pas les fichiers locaux non commités/non suivis. Ne pas reset/clean/stash le travail existant ni créer une reprise depuis HEAD seul en oubliant le WIP. Aucun push et NO-GO public jusqu'à instruction contraire explicite. Basic Memory est un miroir : si indisponible, enregistrer la reprise dans `docs/` et signaler l'absence de synchronisation ; ne pas en faire un blocage au travail local.
