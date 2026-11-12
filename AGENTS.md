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

## Pilotage fonctionnel — décision Owner du 20 octobre 2026

L’unité de livraison est un parcours métier utilisable, défini dans la fiche `docs/Actifs/00_Pilotage_et_audits/LIVRABLES_METIER_ET_PREUVES_2026-10-19.md`; son statut reste exclusivement dans le plan global. Enchaîner code et preuves jusqu’au contrat de sortie du livrable actif. Les axes/champs/adaptateurs sont des sous-tâches internes; ne pas déplacer le marqueur actif après leur seule qualification. Un UNKNOWN protège une donnée, mais ne remplace pas une fonctionnalité attendue. Respecter les reports des cahiers et les décisions/gates humaines existantes.

## Réalignement Owner — 22–23 octobre 2026

Lire également `docs/Actifs/00_Pilotage_et_audits/REALIGNEMENT_FONCTIONNEL_2026-10-22.md`. Les11livrables/3garanties et45familles existants restent le périmètre; le plan global garde seul le statut et l’ordre de travail. Le parcours humain d’analyse localement prouvé ne démontre pas l’exhaustivité automatique, mais cette dernière ne bloque pas tous les autres livrables. Ne pas repartir par défaut dans L04/OCR/intention/retrieval : suivre la fonction métier active du plan, coder ses manques dans les modules natifs jusqu’au résultat utilisateur et à sa preuve. Les challenges restent des sous-chantiers bornés, pas l’unité principale de progression. Rapporter fonctions livrées, fichiers Python/API/UI concernés et limites; ne pas substituer une nouvelle revue ou des nombres de tests au codage.

## Réorientation Owner — 12 novembre 2026

Le plan global R0–R3 remplace la succession de micro-qualifications L01–L11 comme file de travail. Les recettes datées restent des preuves ; une nouvelle variante de test ne justifie pas une nouvelle livraison. Travailler jusqu’au résultat utilisateur du jalon actif, regrouper corrections et vérifications, ne relire que les contrats affectés et ne répéter une suite qu’après changement, échec ou au jalon d’intégration.

La demande Owner du12/11 autorise la consolidation Git, les commits, intégrations et pushes nécessaires. Elle ne vaut pas GO public, déploiement, force-push ou suppression aveugle du WIP. Les variantes historiques doivent être sauvegardées et classées avant retrait ; les archives privées et états d’outils restent hors Git. Signaler séparément une branche de consolidation publiée et une intégration main réellement validée.
