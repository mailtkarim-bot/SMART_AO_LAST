# L04 — parcours de préparation et revue — 20 octobre 2026

## AS-IS / risques / insertion / plan minimal

Les actes source-liés existent pour preuves attendues/risque résiduel; pas de traitement complet ni de revue du dossier exact. Réutiliser ces actes et le dispatcher/reçus. Les risques natifs CCAP/CCTP et les revues de documents Preparation ont d'autres contrats : ne pas les détourner en revue12axes ni modifier leurs portes.

Étendre l'acte humain avec un traitement optionnel fermé : axe qualifié humainement, applicabilité motivée, cinq conséquences déclarées ou UNKNOWN motivé, action, responsabilité explicite du Patron, échéance ou UNKNOWN. Anciennes révisions inchangées. Ajouter un registre de revue Case append-only avec deux actes PREPARED puis REVIEWED, douze dispositions d'axes et empreinte du dossier exact; aucune analyse exhaustive/confirmation de conformité déduite. Une révision/source changée impose une nouvelle préparation. L'absence de traitement d'un point empêche la revue, pas la lecture des lacunes.

Plan : TDD contrats; migration0138 et handler/projections; préparation/traitement/revue dans le panneau existant; preuve HTTP/PostgreSQL et navigateur avec les mêmes identifiants/états; source remplacée, tenant/rôle/MFA, UNKNOWN/retry/concurrence et append-only; contrôles puis bilan unique du parcours. Les étapes sont internes au livrable, le marqueur L04 reste actif pendant l'implémentation.

Responsable minimal : le Patron se désigne explicitement comme responsable de préparation; pas de délégation implicite ni changement des assignations natives. Les actions du dossier sont des actions déclarées de préparation, pas des preuves d'exécution. Les axes sans faits nécessitent raison, action et responsable; ils restent UNKNOWN, jamais « sans risque ». Aucun candidat, P3, corpus réel, backend live, push ou GO public.

## Résultat fonctionnel qualifié — 21 octobre 2026

Parcours humain de préparation/revue qualifié localement : traitements source-liés, applicabilité motivée, cinq conséquences déclarées ou UNKNOWN motivé, action/responsable explicite/échéance, preuves attendues et risque résiduel; préparation puis revue des douze axes sur SHA exact, historique protégé après rectificatif. Backend3678 réussites/2avertissements; Web615/4ignorés; navigateur23desktop+23mobile+12historique/invalidation; quatre refus API tenant/financier supplémentaires. PostgreSQL jetable, HTTP réel via TestClient et session synthétique; aucune analyse exhaustive automatique déduite.

### Code et contrats

- Python : `analysis_dossier.py`, `analysis_dossier_handler.py`, `analysis_dossier_reader.py`, modèle `analysis_dossier.py`; extension optionnelle des actes `analysis_assessment.py`, projections/contrats/runtime/routes existants. Aucun moteur ou dépendance ajouté.
- Migration `20261020_0138` : registre immuable de revue et snapshot exact; traitement optionnel des points. Anciennes requêtes sans traitement conservent leur empreinte. Douze axes distincts; REVIEWED exige une préparation du même SHA/dispositions, des traitements courants et une synthèse non tronquée. Verrous NOWAIT et rollback natif sur concurrence.
- Interface existante : saisie/relecture des traitements, préparation puis revue explicite, UNKNOWN/retry identique, masquage hors contexte et historique paginé. Aucun CSS/design system inventé; consultation OpenDesign Local et Impeccable, direction Owner conservée.
- Responsable : désignation explicite du Patron lui-même. Action déclarée de préparation; aucune tâche exécutée ni délégation créée implicitement. Les confirmations, portes et P3 demeurent indépendants.

### Scénario et preuves reproductibles

Preuves privées : `~/.local/share/smartao-proofs/l04-parcours-20261020/`. Manifeste32fichiers : `source-sha256-delivery.json`.

Scénario synthétique BTP : exigence RC « Lot 6 : le DC1 est obligatoire. » matérialisée par les services existants, risque lié, annexe non extraite, rapport financier publié et scénario économique créé par son handler natif. Même Affaire/source/identifiants entre PostgreSQL jetable, routes réelles FastAPI TestClient et navigateur. Pas de serveur backend live; identité/MFA et passerelle navigateur synthétiques, extraction fournie par les helpers de test : aucune qualification Docling/OCR réelle déduite.

- `backend-global-final-frozen.log` : **3678 passés**,2avertissements,892,87s,exit0. Couvre les nouveaux contrats/SQL/API et les régressions existantes; pas un audit de conformité métier exhaustive.
- `web-global-final-frozen.log` : **615 passés**,4ignorés,74fichiers; types/lint/build verts. Avertissement historique de taille de bundle conservé.
- `browser-metier-desktop.json`, `browser-metier-mobile-qualified.json` :23contrôles chacun, tous vrais. Exigence et risque traités, source exacte, preuve attendue, responsabilité, instant d’échéance, confidentialité, UNKNOWN après reçu perdu, retry identique puis préparation/revue12axes. Chromium isolé via Chrome DevTools; pas Playwright MCP.
- `browser-metier-rectificatif-history.json` :12contrôles vrais. Successeur DCE lié par handler natif, ancienne revue masquée du courant, historique exact conservé, nouvelles intentions obsolètes409, Collaborateur403, aucune persistance d’identifiants navigateur.
- `final-api-guards.json` : résumé et historique refusent tenant étranger404 et droit financier absent403.
- SQL ciblé :52tests initiaux puis57tests API/SQL/migrations/historique et6tests finaux d’historique. Concurrence, append-only, pagination, snapshot corrompu, phase et downgrade peuplé refusés; upgrade et downgrade vide qualifiés. La suite globale finale inclut ces tests.
- TDD effectif : incompatibilité JSON null/SQL NULL, heure locale, verrou du brouillon financier, empreinte legacy et axe vide déclarable relu reproduits puis corrigés. Les exécutions interrompues restent non qualifiantes, conservées dans les logs.
- Ruff/format18Python, mypy650sources, types/lint/build web, diff et secrets verts. Semgrep1.179.0,225règles,32fichiers,0finding/0erreur; analyse locale, aucun téléversement. Impeccable detector sans finding. Revue indépendante ciblée, aucun finding concret restant; ce n’est pas une validation métier humaine.

### Limites et risques ouverts

L04 reste PARTIAL : la recette prouve le parcours humain sur des faits matérialisés, pas l’alimentation exhaustive de tous les axes par un DCE complet. La couverture des omissions critiques sur un dossier multi-pièces/multi-lots reste à coder/qualifier. Échéancier/pic de financement et calculs approfondis ne sont pas inférés. L’accord textuel ne prouve pas les relations graphiques.

Les intentions en attente vivent en mémoire App seulement : un rechargement complet perd cette reprise UI; les contrôles serveur de révision/idempotence restent actifs. Pas de qualification live, de charge, de pentest ou de WCAG exhaustive. Ancien binaire/downgrade interdit sur base enrichie tant qu’un rollback compatible n’est pas qualifié;0138 refuse le downgrade peuplé. Aucune migration de base réelle.

DPGF non évaluable par RAG; candidats inactifs; UNKNOWN/REVIEW_REQUIRED conservés. A1 non admis, A2 HOLD et NO-GO public. Aucun commit/push/déploiement/VPS/corpus réel/P3/dépôt externe.

Méthode appliquée : Superpowers cadrage borné, plan, TDD, revue et vérification; ECC verification-loop; Graphify, Context7 pour sérialisation Pydantic2.10, OpenDesign Local et Impeccable pour interface existante. Basic Memory externe non synchronisée; proposition locale préparée.

## Fermeture des ressources et cohérence finale

Les deux bases jetables smartao_l04 et smartao_l04_global ont été vérifiées Alembic0; conteneur dédié arrêté, onglet isolé fermé et passerelle Vite arrêtée; ACL temporaire PostgreSQL retirée (répertoire700). SQL final :11réponses réussies/6intentions/6traitements,8réponses/4intentions/4revues, aucun double effet.32SHA source inchangés.47tests de contrats documentaires verts. WIP et HEAD inchangés; aucun commit/push. Preuves : final-sql-consistency.json,cleanup-base0.json,final-api-guards.json.
