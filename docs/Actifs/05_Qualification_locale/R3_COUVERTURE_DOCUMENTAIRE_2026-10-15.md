# R3 — Couverture documentaire dans la lecture DCE — 15 octobre 2026

## AS-IS
La lecture Affaire/DCE expose les exigences et leurs ancres, mais aucune couverture par pièce. Les registres contiennent les pièces admises et des extractions immuables, pas un inventaire exhaustif des archives ni une applicabilité par lot ou une criticité qualifiée.

## Risques
Confondre classification/extraction/analyse complète, recycler une extraction ancienne après refus, exposer noms/texte privés ou données hors tenant/version, inventer la portée lot. Le WIP antérieur est conservé.

## Points d’insertion
Projection existante, adaptateur SQL tenant/version, contrat HTTP déjà autorisé CASE_DCE_READ, panneau lecture existant. Aucun schéma, droit, commande, dépendance ou source d’autorité ajouté.

## Plan minimal
1. Tests rouges des extractions absentes/refusées/incohérentes et de la complétude inconnue.
2. Projection des pièces admises avec dernière extraction conservatrice et compte réel des fragments; refus prioritaire à timestamp égal. Famille fermée, identifiants uniquement, aucun texte/nom/hash privé nouveau.
3. Contrat HTTP additif et présentation réutilisant les classes actuelles. Lot/criticité/inventaire complet et analyse restent UNKNOWN/REVIEW_REQUIRED.
4. Preuves PostgreSQL synthétiques, tests web, lint/types/build, revue et Semgrep, puis plan et miroir mémoire.

## Tests à ajouter
Absence, refus, hash ou nombre de fragments incohérent, succès sans déclaration complète, plus récent et égalité conservatrice, tenant/version, contrat fermé et UI sans couverture/avec pièces non extraites.

## Consultation UI
OpenDesign local : catalogue courant (163 skills, 144 design systems), contexte et deux anciens projets consultés via MCP direct; aucune génération Cloud. Les anciens styles ne prouvent pas CYTD. Autorité : PF31-11 et captures Owner; augmentation de la surface existante sans nouvelle palette, CSS ni refonte. Impeccable context et craft-floor consultés; détection ciblée après édition.

## État
QUALIFIÉ POUR LES PIÈCES ADMISES — R3 globale reste ouverte. A1 non admis, A2 HOLD, NO-GO public.

## Preuves acquises pendant la tranche
- TDD : 9 nouveaux cas backend rouges (méthode absente) puis verts; 2 nouveaux cas panneau rouges puis verts.
- Backend ciblé final : **71/71**, dont PostgreSQL réel : dernier refus plus récent/égalité, incohérence du hash et du nombre réel de fragments, scope tenant/version et confidentialité. Upgrade/downgrade Alembic exécutés par fixture, aucun schéma nouveau. Premier runner HTTP sandbox suspendu puis arrêté; run hors sandbox vert, pas un échec produit.
- Web global : **543 réussis / 4 ignorés**, 66 fichiers; typecheck, lint et build verts. Warning bundle 703,25 kB (>500 kB) conservé.
- Ruff global backend/scripts vert; mypy app **622 sources** vert; format 7 fichiers R3 vert.
- Semgrep **1.179.0**, p/security-audit, **225 règles / 10 fichiers R3**, **0 finding / 0 erreur**; règles téléchargées, analyse locale, résultats non envoyés. Périmètre explicite uniquement, pas audit global du WIP.
- Impeccable detect : aucun constat sur le panneau; pas une preuve d'accessibilité exhaustive ni de conformité CYTD complète.
- Revue Codex indépendante : aucun défaut bloquant confirmé; demande de renforcer hash/fragments sur PostgreSQL traitée par les deux cas supplémentaires verts.
- Chrome DevTools Local, contexte isolé, panneau réel et session de présentation synthétique : douze pièces dépliées et visibles, dont non extraite; analyse complète refusée même READY; couverture historique indisponible masque les anciennes pièces. Largeurs 390 et 1440 sans débordement. Douze requêtes de la dernière navigation uniquement loopback. Pas de Playwright MCP, pas de backend/auth live ni E2E application complet.
- Harnais et assertions : `/home/noor/.local/share/smartao-proofs/r3-20261015/`. Une assertion initiale a été corrigée pour tenir compte du text-transform CSS uppercase et de l'état déplié; aucune correction produit induite.

## Limites maintenues et suite R3
Cette sous-tranche qualifie **les pièces admises**, pas tout R3. La portée de chaque pièce par lot, la criticité, les pièces annoncées absentes et les entrées d'archives exclues ne sont pas établies par ces registres : UNKNOWN explicite, REVIEW_REQUIRED et analysis_complete=false. Aucun nom/texte/clé/hash privé nouveau exposé. Les ancres exactes déjà autorisées restent liées aux exigences. Pas de transfert des preuves CEE, ni admission Golden DCE.

La suite backend globale est en cours sur la première base jetable; les deux cas SQL supplémentaires ajoutés après sa collecte sont qualifiés séparément dans les 71 ciblés. Aucun PASS global anticipé. WIP local non commité; aucun push, déploiement, VPS, corpus réel, modèle téléchargé ou effet P3.

## Insertion suivante — repérage read-only pendant le run global
Graphify consulté puis code actuel vérifié : `DceStagedObjectRecord` porte consultation/scan/rejet, mais ne rattache une version DCE qu'à l'état CONSUMED. Une entrée rejetée ou en attente ne doit donc pas être arbitrairement affectée à toute version de la consultation. `DceDocumentAdmissionInput` référence seulement document_id/storage_object_id CLEAN. L'inventaire existant dans `dce_versions.py` utilise DCE_PREPARE et expose des métadonnées que CASE_DCE_READ ne doit pas hériter. La prochaine tranche doit qualifier le rattachement exact et la provenance avant de compléter l'inventaire; ne pas élargir les droits ou assimiler staging consultation et dossier courant. Ce repérage ne prouve pas l'exhaustivité du dépôt ni l'existence d'un inventaire d'archives persistant.

## Fichiers modifiés par cette sous-tranche
- `backend/app/modules/dce/application/queries.py` : projection additive de couverture.
- `backend/app/modules/dce/infrastructure/case_dce_reading_reader.py` : lecture SQL tenant/version conservatrice.
- `backend/app/modules/dce/public/contracts.py` et `backend/app/interfaces/http/routes/case_dce_reading.py` : contrat HTTP fermé, optionnel pour lectures historiques.
- `web/src/shared/types.ts` et `web/src/features/dce/DceKnowledgePanel.tsx` : types et consultation de toutes les pièces connues; classes existantes, aucun CSS ajouté.
- `backend/tests/infrastructure/test_case_dce_reading_reader.py`, `backend/tests/application/test_case_dce_reading_projection.py`, `backend/tests/api/test_case_dce_reading_routes.py`, `web/src/features/dce/DceKnowledgePanel.test.tsx` : régressions et preuves synthétiques.
- Présent dossier, index documentaire et plan global : suivi de la sous-tranche et prochaine étape unique. Les autres fichiers WIP sont antérieurs et non attribués à R3.

## Méthode et portée des outils
Superpowers brainstorming/writing-plans/TDD et requesting-code-review : cadrage borné, rouge avant code, revue indépendante. ECC api-design et verification-loop : contrat additif et contrôles du projet. Graphify : orientation graphe avant recherches; graphe ancien, code vivant prioritaire. Serena activée pour le projet, sans revendication de preuve sémantique nouvelle. Context7 : contrat Vite du harnais consulté. OpenDesign Local Codex et Impeccable : consultation de direction et détection ciblée, pas refonte ni certification visuelle. Jev/Manus non utilisés : aucune classification externe nécessaire à cette projection déterministe, pas de décision métier déléguée. Basic Memory reste miroir du plan, à synchroniser après les résultats finaux.

## Résultat final — clôture de la sous-tranche pièces admises
- Backend global : **2581/2581 réussis**, aucun ignoré, **1286,91 s (21 min 26 s)**, exit 0. Quatre warnings : Starlette/httpx et Pydantic Field.alias (limit, authorization, request), pas des échecs.
- Les deux cas SQL supplémentaires ajoutés après collecte globale passent dans les **71/71 ciblés**; aucun code produit modifié depuis le run global. La suite complète n'a pas été relancée uniquement pour ajouter ces deux tests.
- Web **543 réussis / 4 ignorés**, 66 fichiers; types/lint/build verts. Ruff global, mypy622, format7, secrets ciblés et diff-check verts; Semgrep225règles/10fichiers0finding0erreur.
- Empreintes des dix fichiers de code qualifiés relues identiques. Preuves finales et logs : `/home/noor/.local/share/smartao-proofs/r3-20261015/`.
- Les deux bases sont revenues à Alembic base (0 ligne dans alembic_version), puis seul conteneur `smartao-r3-proof-20261015` (label r3-20261015) arrêté/auto-supprimé; harnais navigateur arrêté et onglet isolé fermé. Aucun service live touché.
- Aucune modification de schéma/dépendance/droit, aucun commit/push, aucune admission ou preuve d'analyse complète. WIP antérieur conservé.

Prochaine étape unique : R3 — auditer puis intégrer à la couverture les entrées d’archives exclues et les pièces annoncées manquantes, avec version/lot et criticité sourcés ou UNKNOWN; prouver les refus de complétude. A1 non admis, A2 générique HOLD et NO-GO public maintenus.
