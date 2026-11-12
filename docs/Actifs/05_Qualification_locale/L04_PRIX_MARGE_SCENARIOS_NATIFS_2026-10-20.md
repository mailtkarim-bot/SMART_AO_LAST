# L04 — Prix et marge : scénarios natifs — 20 octobre 2026

## AS-IS et cadrage

Le cahier métier M2-116/118 exige une lecture séparée de marge, trésorerie, résistance et hypothèses; M2-044 et CT3.1 Prix imposent provenance, catégories déclarées et confidentialité. Le lecteur natif `SqlAlchemyPricingScenarioReader` qualifie déjà snapshot publié exact, révision et catégories de base; ses transitions append-only portent l’état/révision courant. L’axe PRICE de la synthèse n’exposait aucun scénario. Les sources financières n’ont pas de liaison DCE/lot/hash documentaire : cette applicabilité reste UNKNOWN, sans inventer d’ancre documentaire.

Risques : fuite financière hors contexte; reprise d’un snapshot discordant; assimilation d’un historique chiffré à une analyse complète, à la DPGF par RAG ou à P3. Insertion minimale : composition runtime et contrat de synthèse existants, lecteur natif réutilisé dans la même transaction REPEATABLE READ, rendu PRICE sans commande ni nouvelle capacité. Plan : preuve rouge pure/absence UI, projection fermée, intégration SQL/HTTP, rendu/readback/refus, contrôles et journal. Aucun schéma, dépendance ou moteur modifié.

## Code livré

- `backend/app/modules/case/application/analysis_summary.py` : projection des scénarios de la même Affaire. Révision native et détails exacts conservés; ARCHIVED, source UNKNOWN/révision discordante ou contexte DCE non courant masquent montants, hypothèses, intitulé et provenance détaillée. Applicabilité DCE/lot reste UNKNOWN même pour une base qualifiée.
- `backend/app/modules/pricing/infrastructure/scenario_reader.py` : helper de lecture dans la session appelante; le chemin historique utilise ce même code. La synthèse limite à100 scénarios avec détection101/truncated, ordre date/id déterministe. La qualification native des lignes/source et transitions reste inchangée.
- `backend/app/bootstrap/application.py` : compose uniquement l’axe PRICE, dans le même snapshot de lecture que le DCE. Aucun calcul, écriture, nouvelle confirmation, événement, P3 ou porte.
- `backend/app/modules/case/public/analysis_summary_contracts.py` : contrat typé de scénario, corrélation scénario/révision/Affaire/axe et refus des détails non prouvés. `coverage_scope` demeure celui de la couverture documentaire; les scénarios sont des compléments natifs, pas une extension de sa complétude.
- `backend/app/interfaces/http/routes/case_analysis_summary.py` : garde Patron/tenant/MFA/PRICING_READ/FINANCIAL_PRIVATE existante conservée, ajout de `Cache-Control: no-store` sur le GET financier. Défaut d’en-tête reproduit rouge avant correction.
- `web/src/features/dce/AnalysisPricing.tsx`, `CaseAnalysisSummaryPanel.tsx`, `web/src/shared/types.ts` : lecture vente/coût/marge, réserves/seuils, hypothèses enregistrées et snapshot/révisions. Formateurs financiers existants; montants non représentables restent UNKNOWN. Aucun scénario et source obsolète ont un état UNKNOWN visible. Le garde de contexte masque immédiatement les données; aucune commande métier ajoutée.
- Tests : `backend/tests/application/test_analysis_pricing.py`, ajout dans `backend/tests/db/test_case_analysis_summary_sql.py`, `AnalysisPricing.test.tsx` et ajout Panel.test.tsx.

## Preuves locales synthétiques

Logs et recettes : `~/.local/share/smartao-proofs/l04-price-20261020/`, hors Git.

| Contrôle | Résultat et portée |
|---|---|
| TDD pur | Import du projecteur absent rouge;2 tests verts : hypothèses/snapshot/révision exacts, absence/étranger, archivage, source et contexte inconnus |
| TDD UI | Absence d’état prix UNKNOWN reproduite rouge;36 tests ciblés verts, dont6 nouveaux scénarios de lecture/masquage |
| SQL/HTTP | Scénario/snapshot réels synthétiques avec catégories natives, révision discordante masquée; route réelle refuse tenant étranger/Collaborateur/capacité absente/MFA absente sans contenu financier; no-store rouge puis vert |
| Régressions backend |65 tests ciblés verts; puis197 tests incluant synthèse/scénarios/transitions/actes humains/ops/architecture verts,1 warning Starlette/httpx,19,57s. Pas de suite backend globale rejouée dans cette tranche |
| Web global |600 réussites,4 ignorés,70 fichiers,34,26s; typecheck/lint/build verts. Warning historique chunk>500kB conservé |
| Navigateur réel |Chrome DevTools MCP, Chromium isolé, API/session synthétiques,14 contrôles desktop1440 +14 mobile390 verts : lecture exacte, hypothèses, UNKNOWN, source obsolète, masquage Affaire/session/rôle, absence cookies/storage et absence overflow global. Pas de Playwright MCP |
| Qualité |Ruff/format, mypy646 sources et diff verts; Impeccable detect:0; secrets:0; Semgrep1.179.0,225 règles/12 fichiers,0finding/0erreur. Règles téléchargées, code/résultats non transmis |

La fixture SQL initiale ne créait pas d’appartenance; elle a été corrigée avec des identifiants d’audit synthétiques, sans changer le produit. Le socket PostgreSQL redémarré nécessitait ses droits locaux; défaut de harness corrigé, non annoncé comme régression produit. Le restart Vite a laissé l’onglet sur une erreur de connexion; navigation locale rétablie avant recette finale. Ces tentatives ne sont pas des passes.

Superpowers : using/brainstorming borné/TDD/revue/vérification; ECC verification-loop; Graphify interrogé avant les recherches manuelles (graphe ancien, code/tests autorité). OpenDesign Local : catalogue et artefact existants consultés, direction Owner/Cytd de production conservée sans CSS/palette nouvelle, aucun Cloud/BYOK/génération. Le MCP local a été retrouvé sur son daemon existant après diagnostic Node/socket; aucune seconde installation. Impeccable context/craft-floor/polish/detect appliqués. Serena non utilisé sans navigation sémantique; Context7 sans question API nouvelle; Jev/Manus sans apport utile à ce raccordement déterministe.

Revue indépendante ciblée : aucun finding concret bloquant sur filtres tenant/Affaire, droits financiers, source/révision, masquage, transaction et contrats/UI; lecture statique sans tests DB supplémentaires ni validation métier humaine.

Nettoyage : base jetable vérifiée Alembic0, conteneur dédié arrêté; onglet isolé et serveur synthétique5191 fermés. Le daemon OpenDesign préexistant a été conservé. Capture desktop relue; l’ergonomie mobile exhaustive reste non qualifiée.

## Limites et statut

Qualification locale de lecture uniquement. L04 reste PARTIAL; les catégories déclarées ne prouvent pas le coût complet BTP, les hypothèses par paramètre ne sont pas automatiquement vérifiées, et aucun scénario n’est déclaré applicable au DCE/lot. Un snapshot financier antérieur reste sa source historique exacte : aucune règle métier de remplacement par un autre snapshot n’est inventée. Pas de backend/auth live, corpus réel, audit WCAG exhaustif, courbe de trésorerie, effet P3, dépôt externe, VPS, déploiement, commit ou push. DPGF non évaluable par RAG; candidats inactifs; A1 non admis, A2 générique HOLD et NO-GO public.

WIP principal conservé sur `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`. Basic Memory externe non synchronisée après refus automatique antérieur; miroir proposé localement. Plan global seule autorité.

Prochaine étape : L04 — raccorder à l’axe Trésorerie et garanties les déclarations financières publiées et réserves déjà enregistrées pour l’Affaire, avec source/révision et hypothèses exactes; laisser UNKNOWN l’échéancier, le pic de financement et toute portée non prouvés, puis qualifier invalidation et confidentialité sans modifier confirmations ni portes. DPGF non évaluable par RAG, aucun moteur candidat activé; A1 non admis, A2 générique HOLD et NO-GO public maintenus.
