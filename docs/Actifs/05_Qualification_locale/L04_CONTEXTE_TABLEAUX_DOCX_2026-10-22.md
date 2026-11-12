# L04 — contexte sourcé des tableaux DOCX — 22 octobre 2026

## Cadrage et plan minimal

AS-IS : extraction déterministe4, analyse native9 et parcours37points existants. Les cellules sont ancrées séparément; leur texte voisin n’est pas restitué. M2-026/027/029, PF2-084 et contrat technique source/version/hash/locator font autorité.

RISQUES : négation ou condition cachée dans une autre cellule, héritage de lot inventé, contexte tronqué présenté comme complet, réutilisation d’un acte antérieur, fuite tenant/version.

INSERTION : lecteur de synthèse Case, contrat public, empreinte du contexte humain, panneau existant et tests. Pas de migration, dépendance, nouvelle route ni moteur.

Choix : restituer les paragraphes non vides du même tableau/extraction avec texte et ancre propres, sans leur attribuer de rôle sémantique ni d’applicabilité. La première ligne reste une ligne, pas un en-tête implicitement prouvé. Limites : 64 fragments et16000octets par tableau,16tableaux distincts par lecture. Toute preuve discordante ou budget dépassé produit UNKNOWN sans liste partielle.

- [x] Régression rouge : contexte exact des cellules, conditions/négations intactes, aucun héritage; empreinte sensible au contexte, stable hors tableau.
- [x] Projection SQL bornée et contrats; preuve indépendante de chaque fragment courant avant restitution.
- [x] OpenDesign Local Codex/catalogue consulté; UI existante conservée, Impeccable et test de lecture/masquage.
- [x] Traitement/revue/rectificatif sur base jetable, refus et historique; contrôles ECC, suites, Semgrep et revue.
- [x] Mise à jour du plan, index, matrice et miroir Basic Memory après résultats observés.

## Invariants

UNKNOWN/PARTIAL/REVIEW_REQUIRED, tenant/rôle, FINANCIAL_PRIVATE, append-only, MFA, retries et confirmations inchangés. DPGF non évaluable par RAG. A1 non admis, A2 générique HOLD, NO-GO public. Aucun candidat activé, live, corpus réel, VPS, déploiement, P3, commit ou push.

## Code et comportement

`case/infrastructure/analysis_table_context.py` ajoute une projection de lecture sur les fragments immuables du même tenant/extraction/tableau. Chaque texte et ancre doit concorder : identifiant, ordinal, version, document/hash, extraction, coordonnées et SHA du texte. Le cache est réutilisé uniquement si l’ancre complète du point y figure. Pas d’assemblage de clauses ni de reconnaissance sémantique des en-têtes. Les cellules vides ne sont pas inventées. La table extraite ne prouve pas à elle seule la complétude du document.

Le lecteur de synthèse rattache cette projection avant les actes humains. `source_context_digest` inclut le contexte des tableaux, y compris UNKNOWN; l’absence de contexte hors tableau conserve le digest historique. Les traitements antérieurs sur cellules exigent une relecture après cet enrichissement. Les snapshots historiques ne sont pas réécrits. Le contrat public et le type client sont additifs, sans nouveau POST. Dans `CaseAnalysisSummaryPanel`, un détail « Cellules du tableau · contexte à relire » présente chaque texte et référence; la portée reste UNKNOWN. Budget dépassé/preuve discordante : message explicite, aucune liste partielle.

## Preuves observées — clôture locale bornée

Preuves privées : `~/.local/share/smartao-proofs/l04-docx-context-20261022/`. HEAD `30f26934430095632000a1d82519f61dbb4c6411`, principal sale préservé. Dix fichiers code/tests concernés, hashes dans `delivery-sha256.json`.

- Rouge initial : contexte absent dans SQL; digest insensible au contexte; UI absente. Puis verts. Revue indépendante : quatre rouges identité/version/ordinal/cache, puis deux rouges d’ancre initiale discordante; égalité complète corrigée. Dix tests unitaires finaux réussis; contre-revue statique sans autre défaut concret.
- Ciblés SQL/API/actes :74réussites. Dossier37points traité/revu, rectificatif de contenu et rectificatif du seul contexte, refus de preuves voisines et budget, confidentialité et historique. Ce run précède la dernière égalité stricte de l’ancre initiale; les dix unitaires et la suite globale finale ci-dessous qualifient le code final.
- Backend global final : **3809réussites,0ignoré,2avertissements historiques,1063,06s,exit0**. Avertissements Starlette/httpx et Pydantic Field.alias conservés; aucun échec. Dixhashes de code/tests inchangés après toutes les suites et la recette navigateur.
- Web global629réussites/4ignorés préexistants;26tests panneau. Types/lint/build client verts, warning de chunk>500kB conservé. Ruff/format7Python, mypy651 verts.
- Semgrep1.179.0 :225règles/10fichiers,0finding/0erreur; détecteur de secrets0; Impeccable `[]`. Ce sont des scans bornés, pas une certification de sécurité/accessibilité.
- Navigateur Chrome DevTools MCP headless/isolé :15assertions réussies,37points saisis/préparés/revus sur le SHA exact. Conditions/négations/lots et ancres distinctes lisibles; refus rôle403 et masquage immédiat après changement Affaire/session/rôle. Desktop1440px et mobile390px sans débordement racine; défilement horizontal existant accessible et textes repliés. Captures inspectées. Aucun test Playwright (MCP absent).
- Rectificatif navigateur :6assertions réussies sur un successeur vide synthétique, ancien contexte masqué, revue REVIEW_REQUIRED et2snapshots HISTORICAL avec leurs3contextes intacts. La réextraction positive de V2 est prouvée séparément en SQL, pas déduite de ce contrôle vide.39POST201/39commandes uniques donnent37traitements+2revues SQL, double clic inclus sans effet double.
- Réseau final :114entrées,113HTTP127.0.0.1:5193 et1image interne dataURI;0origine HTTP externe. Aucune requête navigateur avec cookie/Authorization, aucune donnée de session persistée. Adaptateur UDS600 arrêté proprement/base0, serveur Vite privé et client Chromium isolé arrêtés.
- Diagnostic d’automatisation conservé : le premier sélecteur a confondu texte du point et texte d’une cellule voisine; relance sur base neuve avec sélection de l’extrait direct. Aucun défaut produit déduit. Un conflit de dossier de fixture local a été corrigé avec un nouveau chemin avant cette relance; il ne constitue pas un test produit échoué.

Superpowers : cadrage borné/plan adapté/TDD/revue et vérification. ECC : `verification-loop`. OpenDesign Local Codex : catalogues et artefact existant consultés, direction Owner/CYTD conservée sans nouveau style; Impeccable contexte/craft-floor/detect. Graphify consulté, Serena activée; Basic Memory consultée comme miroir. Pas de Jev/Manus : aucun besoin de classification distante ni de deuxième implémentation.

## Limites ouvertes

Grands tableaux, cellules fusionnées, tableaux imbriqués et contenu DOCX non qualifié restent UNKNOWN/REVIEW_REQUIRED. Les liens sémantiques entre cellules et l’analyse entière d’un DCE réel ne sont pas prouvés. Le corpus37points est un développement connu, pas un challenge indépendant. Aucun branchement des cellules au RAG ni aux comparateurs automatiques.

## Nettoyage et suivi final

Quatrebases dédiées (`smartao_l04_context`, `smartao_l04_context_global`, `smartao_l04_context_browser`, `smartao_l04_context_browser_final`) vérifiées Alembic0 avant arrêt du seul conteneur tmpfs `smartao-l04-acts-pg-20261020`; état exited confirmé. ACLUID70 retirée, socket700 restauré, adaptateur/Vite/Chromium privés arrêtés. `cleanup.json` conserve les compteurs. Aucun schéma ajouté; les migrations existantes jusqu’à0139 et retour base ont été exercés par les fixtures.

Plan : case locale prouvée cochée, journal et unique prochaine étape actualisés; index et fiche livrables reliés. Basic Memory reste un miroir de ce plan. La suite finale remplace le run initial interrompu à144réussites pour intégrer le dernier contrôle; ce run interrompu n’est pas une preuve globale.
