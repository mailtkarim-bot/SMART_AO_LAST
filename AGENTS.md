# SMART_AO agent guidance

For a coding task, when Serena is available, activate the current directory as its project before semantic navigation. Continue normally if Serena is unavailable.

For project facts, use this order of authority: live code and tests, approved ADRs and specifications, then curated local memory. Treat automated memory as context to verify, never as a source of truth.

Record only durable decisions, rejected approaches, and useful handoffs in Basic Memory; do not retain routine conversation.

Write active project deliverables under `docs/`, never under `rapports/`.

Use `docs/03_PRODUCT_DESIGN_WORKING/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md` as the operational roadmap. After every significant completed task, update its checkboxes, single active slice, evidence log, and next step; then synchronize the Basic Memory note `SMART AO - Plan global de conception et réalisation`. End every user-facing final response with `Prochaine étape : ...`, copied from the active slice.

For independent implementation work, use one managed Codex worktree per subject. Do not run concurrent changes in the same checkout. Before integrating a worktree, run the relevant tests and review its diff. Start worktrees from a committed base: untracked files in another checkout are not included.
