# L04 — Trésorerie et garanties natives — 20 octobre 2026

## AS-IS, risques, insertion et plan

M2-116/117/118 distingue marge, besoin de trésorerie daté, résistance et hypothèses; le cahier technique impose les contrôles financiers avant lecture. Le rapport financier natif est un snapshot publié révisionné avec lignes humaines; les scénarios conservent leurs réserves et hypothèses. Aucun de ces registres ne prouve à lui seul une courbe mensuelle ni un pic de financement. L’axe CASH ne présentait pas ces données.

Risques : zéro implicite à partir d’une valeur par défaut, association au DCE/lot non prouvée, snapshot discordant, somme injustifiée entre scénarios et fuite de données financières. Insertion : composition runtime L04 en REPEATABLE READ, lecteur financier existant partagé dans cette session, contrats additifs et panneau existants. Plan minimal : TDD pur et absence UI; rapprochement des lignes exactes; réserves séparées; SQL/HTTP/invalidation; navigateur synthétique, contrôles et suivi. Pas de schéma, dépendance, calcul métier, commande, confirmation ou porte nouvelle.

## Code et comportement

- `backend/app/modules/case/application/analysis_summary.py` : `project_analysis_cash` conserve rapport/révision et déclare le montant uniquement avec au moins une ligne native FORECAST_CASHFLOW dont la somme exacte concorde avec le snapshot. Zéro explicite accepté; aucune ligne, snapshot non publié, discordance ou contexte DCE non courant donnent UNKNOWN avec détails masqués.
- `backend/app/modules/membership/infrastructure/financial_report_reader.py` : réutilisation du lecteur get via `get_in_session`, liste publiée tenant/Affaire dans la transaction appelante. Ordre publication/id,20 rapports présentés avec détection21/truncated; tous restent des historiques identifiés, aucun n’est arbitrairement promu comme applicable au DCE courant.
- `backend/app/bootstrap/application.py` : CASH compose les rapports et les mêmes projections natives de réserves que PRICE. Pas d’addition entre scénarios, pas de conversion en pic de trésorerie ou obligation contractuelle.
- `backend/app/modules/case/public/analysis_summary_contracts.py` : contrats déclarations/lignes/rapports, identité Affaire/axe et somme exacte; échéancier/pic/portée littéralement UNKNOWN. Détails refusés hors contexte courant.
- `backend/app/interfaces/http/routes/case_analysis_summary.py` : ajoute l’exigence native FINANCIAL_REPORT_READ/FINANCIAL_PRIVATE avant lecture aux gardes existantes Patron/MFA/tenant/PRICING_READ. Aucun droit accordé ou rôle élargi. Cache-Control:no-store conservé.
- `web/src/features/dce/AnalysisCash.tsx`, Panel et shared/types : montants déclarés, lignes exactes, date de calcul/règles/devise, réserves par scénario, hypothèses et source/révision. Masquage immédiat hors Affaire/session/rôle, sur source obsolète ou montant discordant/non représentable. Calendrier de paiement/libération, pic/date/durée, portée et empreinte documentaire restent UNKNOWN. L’absence d’un rapport ou d’une réserve n’est pas présentée comme zéro.

Les hypothèses des rapports ne sont pas inventées à partir du libellé des lignes : les libellés sont des déclarations, les hypothèses de calendrier restent UNKNOWN. Les hypothèses des réserves sont celles enregistrées dans leur scénario. Les rapports/scénarios n’ont pas de preuve native de portée DCE/lot; une source historique exacte ne suffit pas à l’établir.

## Preuves exécutées

Logs privés et recettes : `~/.local/share/smartao-proofs/l04-cash-20261020/` (hors Git).

| Contrôle | Résultat et portée |
|---|---|
| TDD | Projecteur absent rouge puis2 tests purs verts : zéro déclaré/source/révision/ligne exacts, manque/discordance/DRAFT/DCE obsolète/étranger; absence d’état CASH visible rouge puis vert |
| SQL/HTTP réels synthétiques | Rapport publié/lignes/révision/réserves natifs; disparition des détails après REVIEW_REQUIRED, exclusion du DRAFT; refus tenant étranger/Collaborateur/PRICING_READ/FINANCIAL_REPORT_READ/MFA absents sans contenu financier; no-store préservé |
| Backend ciblé et régressions |208 réussites,1 warning Starlette/httpx,49,65s : synthèse, rapports/lignes natifs, scénarios/transitions, actes humains, purs, architecture et contrats ops. Pas de backend global entier rejoué dans cette tranche |
| Web global |610 réussites,4 ignorés,71 fichiers,39,29s; types/lint/build verts. Warning historique chunk>500kB conservé |
| Navigateur |Chrome DevTools MCP, Chromium isolé, API/session synthétiques :15 contrôles desktop1440 +15 mobile390 verts. Déclaration/lignes/source/révision/hypothèses/réserves exactes, UNKNOWN échéancier/pic/portée, absence distincte de zéro, masquage Affaire/session/rôle, source obsolète, aucun cookie/storage/overflow global. Aucun Playwright MCP |
| Qualité/sécurité |Ruff et format7 fichiers verts; mypy646 sources vert; diff vert; Impeccable detect0; secrets0; Semgrep1.179.0,225règles/12fichiers,0finding/0erreur. Règles téléchargées seulement, code/résultats non transmis |
| Revue indépendante |Aucun défaut confirmé sur filtres, permissions, somme exacte, transaction, invalidation, réserves séparées et UNKNOWN. Revue statique sans tests DB supplémentaires ni validation humaine métier |

La remise du socket en mode777 a été refusée par la revue automatique; elle n’a pas été exécutée. UID PostgreSQL70 vérifié sur l’image locale, puis ACL limitée à cet utilisateur accordée pour la base jetable. Le sandbox ne supportait pas setfacl; l’opération limitée a été exécutée après revue avec droits adaptés. Aucun élargissement global ni migration live.

Méthode : Superpowers using/brainstorming borné/plan/TDD/revue/vérification et ECC verification-loop; Graphify consulté d’abord (graphe ancien, code/tests autorité). OpenDesign Local : artefact existant relu avant UI, catalogue et direction Owner/Cytd confirmés dans la session, pas de CSS/palette nouvelle ni Cloud/BYOK. Impeccable craft-floor/polish/detect et contexte de session réutilisés, pas d’init ni hooks. Serena non utilisé sans navigation sémantique; Context7 sans question API nouvelle; Jev/Manus sans gain sur ce raccordement déterministe.

Nettoyage : PostgreSQL jetable vérifié Alembic0 puis arrêté; ACL temporaire UID70 révoquée et répertoire de nouveau privé. Onglet isolé et serveur synthétique5191 fermés; daemon OpenDesign préexistant conservé.11 requêtes navigateur synthétiques, toutes GET, sans cookies/authorization; capture desktop relue.47contrats documentaires finaux verts; une seule tranche active concordante.

## Statut et limites

Lecture locale qualifiée, L04 demeure PARTIAL. Aucun échéancier mensuel, pic/financement, capacité financière disponible ou preuve d’applicabilité DCE/lot déduit. Le rapport publié n’est pas une preuve de liquidité ni une validation des hypothèses. Pas de backend/auth live, corpus réel, audit WCAG exhaustif, moteur candidat activé, RAG DPGF, effet P3, dépôt externe, VPS, déploiement, commit ou push. A1 non admis, A2 générique HOLD et NO-GO public maintenus.

WIP principal conservé, branche `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`. Le plan global reste l’unique statut opérationnel. Basic Memory externe non synchronisée après refus automatique antérieur; proposition locale conservée.

Prochaine étape : L04 — raccorder à l’axe Capacité et ressources les exécutions de planification natives déjà enregistrées pour l’Affaire, avec révision, hash des entrées, hypothèses et statut solveur exacts; afficher UNKNOWN les sources, disponibilités ou portées non prouvées et qualifier invalidation/tenant/rôle sans lancer de solveur ni modifier confirmations ou portes. DPGF non évaluable par RAG, aucun moteur candidat activé; A1 non admis, A2 générique HOLD et NO-GO public maintenus.
