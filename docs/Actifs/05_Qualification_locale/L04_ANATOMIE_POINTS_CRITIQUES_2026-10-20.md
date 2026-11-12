# L04 — anatomie lisible des points critiques — 20 octobre 2026

## AS-IS / risques / points d’insertion

La synthèse et ses relations natives existent. Le registre des risques porte severity et source_excerpt ; les exigences disposent de bornes source revalidées. Aucun champ structuré expected_evidence ou residual_risk rattaché à ces points n’a été trouvé dans les modèles DCE/Decision/PatronAction ; une preuve reçue ou un traitement MITIGATED n’est pas un risque résiduel mesuré.

Risques : extrait reconstruit ou normalisé, coupure UTF-8, source obsolète exposée, criticité déclarée assimilée à un score calculé, preuve attendue inventée, ancien contenu restauré après changement de contexte.

Insertion : lecteur SQL Case de synthèse, contrat public existant, panneau/hook existants et tests. Aucun schéma, dépendance, droit, confirmation, porte ou moteur modifié.

## Plan minimal et preuves

- [x] Régression rouge SQL et contrat : extrait byte-exact de la région prouvée, criticité native du risque seulement, absence et obsolescence UNKNOWN ; budgets de lecture explicites.
- [x] Projection additive et refus du contenu sans preuve courante ; preuve attendue et risque résiduel UNKNOWN sans inférence.
- [x] Affichage Patron dans le système existant après consultation OpenDesign Local/Impeccable, tests rouges puis verts ; masquage et refus discordants.
- [x] PostgreSQL jetable synthétique, suites appropriées, types/lint/build, revue et Semgrep ; journal/plan/index actualisés après preuves.

A1 non admis, A2 HOLD, NO-GO public ; DPGF non évaluable par RAG, aucun candidat activé. WIP principal conservé, aucun commit/push/live/corpus réel.


## Code livré

- `backend/app/modules/case/application/analysis_summary.py` : `exact_source_excerpt` lit exclusivement la région UTF-8 exacte, refuse les bornes invalides, les caractères coupés et une région dépassant8000octets ; aucune reformulation ou substitution. Preuve attendue et risque résiduel restent des littéraux UNKNOWN dans la projection.
- `backend/app/modules/case/infrastructure/analysis_summary_reader.py` : exigences depuis leurs bornes revalidées, risques depuis l’extrait comparé au fragment actuel. Criticité uniquement issue de `DecisionRiskRecord.severity`, jamais d’un score ou d’un mot-clé ; exigences sans criticité native UNKNOWN. Source périmée/incomplète/discordante : aucun extrait/criticité divulgué.
- `backend/app/modules/case/public/analysis_summary_contracts.py` : champs additifs `source_excerpt`, `source_excerpt_state`, raison UNKNOWN, `severity`, `expected_evidence`, `residual_risk`. Validation état/contenu, longueur UTF-8/région et interdiction de contenu d’anatomie sans source courante. Les défauts UNKNOWN conservent les anciens doubles synthétiques.
- `web/src/shared/types.ts`, `CaseAnalysisSummaryPanel.tsx` et `useCaseAnalysisSummary.ts` : lecture visible Patron, citation littérale avec retours à la ligne conservés, criticité déclarée traduite ; budget dépassé affiché UNKNOWN, champs non enregistrés UNKNOWN. Refus de l’extrait ou criticité sans preuve et de la longueur UTF-8 discordante ; masquage de contexte déjà acquis conservé.
- Tests enrichis : `test_case_analysis_summary_sql.py`, `test_analysis_follow_ups.py`, tests du panneau et du hook. Aucun fichier de confirmations, de porte, de commande, de politique, de migration ou de dépendance modifié.

## Preuves exécutées

| Contrôle | Résultat |
|---|---|
| TDD extraction | 1 rouge helper absent puis vert ; accents, bornes UTF-8 coupées et limites8000/8001 explicitement couverts |
| TDD SQL | 2 rouges champs absents puis verts ; citation exacte risque/exigence, sans criticité inférée |
| TDD Web | 1 rouge affichage puis vert ; 3 rouges réponses discordantes puis verts |
| Backend de la verticale et consommateurs DCE | **115réussites**,1avertissement Starlette/httpx,19,10s ; application/API/lecteur/PostgreSQL synthétique, droits/tenant/rôle/MFA, invalidation et conséquences/conditions conservées |
| Web ciblé | **28réussites** |
| Web global | **586réussites,4ignorés préexistants C08,68fichiers**,50,61s,exit0 |
| Types/lint/build | mypy643sources,types Web,Ruff global,ESLint etbuild Web verts ; format5Python etdiff contrôlés |
| Revue | Indépendante en lecture seule : aucun bug important concret identifié ; ni test DB ni validation humaine déduits de cette revue |
| Sécurité | Semgrep1.179.0,225règles,10fichiers,zérofinding/zéroerreur ; detect-secrets zéro résultat ; Impeccable detect zéro finding |
| Navigateur | Chrome DevTools MCP/Chromium isolé,32contrôles desktop1440×1000 et32mobile390×844 : citation,criticité,UNKNOWN,budget,ancres,changement Affaire/session/rôle,409,réponses discordantes et tardives ; aucun test Playwright revendiqué |

La criticité est une déclaration native ; MITIGATED et ACCEPTED sont tous deux testés sans transformer le traitement en risque résiduel connu. Une preuve de traitement déjà reçue ne devient pas une preuve attendue. Le budget8000octets limite l’affichage, jamais la complétude du DCE. La citation n’est pas une analyse sémantique complète.

OpenDesign Local Codex : catalogue et surface existante relus, système Owner Freeze3.1/Cytd de production conservé, aucune palette/CSS de thème nouvelle, aucun artefact supplémentaire/Cloud/BYOK/crédit. Impeccable context/craft-floor/polish/detect appliqués. Superpowers cadrage/TDD/revue/vérification, ECC API/vérification ; Graphify consulté avant les lectures ciblées. Pas de navigation sémantique : Serena non employé. Jev/Manus sans apport borné supplémentaire sur cette projection déterministe.

## Limites et état réel

La suite backend globale de3641réussites appartient à la tranche relations précédente ; **elle n’a pas été rejouée après cet ajout**. La qualification courante backend porte sur les115tests de la verticale et de ses consommateurs ; aucun PASS global courant déduit. Les avertissements conservés sont Starlette/httpx et le chunk Web >500kB.

L04 métier reste PARTIEL : aucun champ structuré natif de preuve attendue/risque résiduel n’a été trouvé pour ces points, donc UNKNOWN visibles. Aucun contenu n’est inventé depuis la criticité, une action, un état de condition ou une preuve reçue. Une saisie humaine source-liée reste à coder. Pas d’analyse complète, d’évaluation économique RAG ou d’applicabilité certaine déduite.

Recette UI avec vrais panneau/hook/client API, serveur synthétique uniquement ; pas du parcours d’authentification complet App ni d’un backend live. Pas de corpus réel, VPS, déploiement, dépôt externe, P3, GO public, commit ou push. Aucun candidat activé. A1 non admis, A2 HOLD et NO-GO public maintenus.

PostgreSQL16 jetable sans réseau/port publié, tête0136 exercée, retour Alembic0 vérifié puis conteneur dédié retiré. WIP principal préservé, branche `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`. Preuves privées `~/.local/share/smartao-proofs/l04-anatomy-20261020/`,10empreintes sources conservées. Miroir Basic Memory préparé localement, non transmis.

La recette a effectué 28GET synthétiques,sansbearer/cookie ;captures/layout conservés.

Prochaine étape : L04 — implémenter un enregistrement humain révisionné des preuves attendues et du risque résiduel des points critiques, avec source/version/portée exactes, UNKNOWN, append-only, concurrence et contrôles tenant/rôle; qualifier saisie et relecture sans modifier confirmations ni portes. DPGF non évaluable par RAG, aucun moteur candidat activé; A1 non admis, A2 générique HOLD et NO-GO public maintenus.
