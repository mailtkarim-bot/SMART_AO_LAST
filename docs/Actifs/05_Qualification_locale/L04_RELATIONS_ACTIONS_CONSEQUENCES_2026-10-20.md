# L04 — relations, actions et conséquences — 20 octobre 2026

## AS-IS

Synthèse douze axes existante, sources revalidées et champs d’anatomie UNKNOWN. Registres natifs : actions Patron liées par clés fonctionnelles et références explicites ; liens risque/exigence ; impacts contractuels révisionnés ; conditions liées à une preuve et un contexte décisionnel exacts. Auteur ≠ responsable.

## Risques

Transfert d’une action entre Affaires/versions/lots, preuve remplacée, exigence déconfirmée, décision invalidée, responsable inventé, impact déclaré pris pour coût calculé. Préserver les gardes natifs de lecture, aucune nouvelle autorisation/commande.

## Points d’insertion et plan minimal

1. TDD lecteur des relations dans le snapshot de synthèse : source courante obligatoire, liens exacts, confirmations/révisions actuelles ; refus et bornes explicites.
2. Projection additive `follow_ups` typée, état UNKNOWN si relation absente ou refusée ; conséquences déclarées, rôle/acteur assigné seulement si explicite.
3. Lecture Patron protégée aussi par les capacités natives des registres raccordés ; aucune modification de droits, confirmations, portes, schéma ou dépendance.
4. Panneau existant et preuve UI après consultation OpenDesign Local/Impeccable ; régressions SQL/HTTP/frontend, lint/types/sécurité et suivi.

## Tests à ajouter

Nominal action directe et lien risque/exigence, transition courante, condition/impact/profil/révisions exacts ; source périmée, mauvais tenant/Affaire/référence, exigence déconfirmée, lien absent, décision invalide et borne. UNKNOWN sans assignation ; pas de promotion métier ni mutation à la lecture.

Tranche de raccordement qualifiée localement ; L04 métier reste PARTIEL. A1 non admis, A2 HOLD, NO-GO public. DPGF non évaluable par RAG, aucun candidat activé, aucun live/corpus réel/push.

## Implémentation et preuves ciblées acquises

### Comportement

Le lecteur `case/infrastructure/analysis_follow_up_reader.py` compose dans le snapshot existant les relations natives, sans commande ni écriture métier :

- action directe au risque : même tenant/Affaire, clé fonctionnelle et ensemble de références exacts, dernière transition native ; aucune affectation du créateur comme responsable ;
- action du couple risque/exigence : relation exacte de la version applicable, deux sources courantes et exigence actuellement confirmée ;
- conséquence contractuelle : exigence/révision/observation exactes, dernière preuve de l’observation, référence source exacte ; états UNKNOWN/SUPERSEDED refusés ; conséquence déclarée, pas coût calculé ;
- condition/responsable : condition et relation de preuve exactes, impact/révision, exigence/révision et profil figés, décision GO_NO_GO finalisée conditionnelle CURRENT et contexte FROZEN, même empreinte de portée ; toutes les références du contexte sont revalidées avec le validateur natif ;
- impacts/conditions ne sont projetés sur un risque qu’à travers son lien explicite à l’exigence confirmée. Plusieurs liens natifs restent distincts.

Le contrat de synthèse ajoute `follow_ups` et `follow_up_state`, avec identifiants, révisions, relations, condition/décision/contexte/preuve lorsque présents. Aucun écrasement des registres natifs. Les champs agrégés historiques action/responsable/conséquences restent UNKNOWN : aucune valeur unique n’est inférée d’une liste de relations. L’UI lit la liste typée et affiche le responsable explicitement affecté, l’échéance ou UNKNOWN, les conséquences déclarées et les références consultables. Une relation absente/non prouvée reste UNKNOWN. Aucun lot ni applicabilité déduits d’un texte ou propagés comme certains.

Bornes : 300 liens/actions/preuves/conditions lus par groupe (+1 pour signaler la troncature), 300 relations au plus rendues par élément ; `truncated` visible. Aucune borne n’établit la complétude. Les douze axes restent NON_EVALUATED/REVIEW_REQUIRED et `analysis_complete=false`.

### Droits et garde financier

Le GET de synthèse compose désormais aussi les contrôles natifs PATRON_ACTION_READ, DECISION_FINALIZE (lecture du dossier décisionnel) et PRICING_READ/FINANCIAL_PRIVATE, en plus de CASE_DCE_READ et DECISION_RISK_READ. Aucun rôle/capacité accordé, aucune politique modifiée. Les refus ont lieu avant lecture du dossier. Ce GET échoue fermé si une de ces capacités manque ; il ne fournit pas une synthèse partielle financière à un lecteur moins habilité.

### TDD et revue

- Projection : rouge sur champ de relation absent puis vert ; budget301→300 rouge puis vert.
- SQL actions : un rouge nominal, trois refus verts, puis quatre verts.
- SQL conséquences : un rouge nominal, quatre refus verts, puis verts.
- SQL propagation aux deux extrémités : un rouge nominal et un refus vert, puis deux verts.
- Condition/profil/responsable : rouge sur le parcours PostgreSQL A1 synthétique existant, puis vert.
- Revue : défaut de revalidation partielle du contexte reproduit (révision CASE périmée) puis corrigé ; test de décision invalidée également vert. La portée et le type de décision sont revalidés.
- Web : affichage rouge puis vert ; deux réponses aux preuves discordantes rouges puis vertes ; clés React dupliquées pour deux liens natifs reproduites puis corrigées.
- Contre-revue indépendante en lecture seule : aucun finding important restant après les deux corrections. Elle ne remplace pas les tests DB.

### Résultats actuellement qualifiés

- Backend ciblé : **36 réussites**, dont PostgreSQL/HTTP réel synthétique ; refus individuel de chacune des cinq capacités inclus dans le contrôle HTTP SQL final.
- Web ciblé final : **24 réussites**.
- Web global final : **582 réussites, 4 ignorés préexistants C08, 68 fichiers**, 56,71 s, exit0.
- mypy : **643 sources** ; Ruff global, format des9Python concernés, types/lint/build Web et diff verts. Avertissement de chunk Web >500kB conservé.
- Semgrep1.179.0 : **225 règles/14 fichiers, zéro finding/zéro erreur**. Analyse locale, métriques désactivées. detect-secrets14fichiers : zéro résultat. Aucun scan ne constitue une preuve exhaustive de sécurité.
- Navigateur : **25 contrôles desktop1440×1000 et25mobile390×844**, vrais panneau/hook/clientAPI, Chrome DevTools MCP/Chromium isolé, API entièrement synthétique. 24GET sous `/synthetic/`, aucun bearer/cookie ; aucun backend live. Affichage action/conséquence/condition/responsable, UNKNOWN, sources, changement Affaire/session/rôle, réponses discordantes/409 et tardives qualifiés. Mobile390 sans débordement de page, tableau explicitement défilant/focusable. Captures desktop/mobile conservées. Serveur Vite et page dédiés arrêtés après preuve.
- OpenDesign : catalogue courant/artefact existant consultés localement, système production Owner Freeze3.1/Cytd confirmé ; aucune génération Cloud/BYOK, palette ou CSS nouvelle. Runtime Node24 installé réutilisé pour SQLite natif. Impeccable context/craft-floor/polish et detect : zéro finding. Aucun init/hook/PRODUCT/DESIGN créé.

Contrats documentaires : 47 tests réussis.

Suite backend globale finale : **3641 réussites, 1 avertissements, 935.09 s, exit0**. L’avertissement Starlette/httpx reste visible. Preuves privées : `~/.local/share/smartao-proofs/l04-links-20261020/`, manifeste14fichiers `source-sha256.json`, journal `backend-global-final.log`. Un premier global interrompu après21réussites est non qualifiant.

### Limites conservées

L04 métier reste partiel : pas de conséquence technique/prix/délai/cash calculée par nature, pas d’applicabilité métier ou de risque résiduel déduit de ces relations, pas d’assignation implicite. La condition OPEN/SATISFIED/FAILED/WAIVED est restituée comme état natif, jamais comme preuve automatique d’une action réalisée ou d’une porte levée. La vérification navigateur porte sur la composition UI/API synthétique, pas l’authentification entière d’App, un backend live ou une conformité accessibilité exhaustive. Aucun test Playwright revendiqué.

Méthode : Superpowers cadrage borné/plan/TDD/revue/vérification, ECC API et vérification ; Graphify consulté. Pas de navigation sémantique, Serena non requis ; Jev/Manus sans besoin borné supplémentaire ici. Aucun schéma/dépendance/moteur actif modifié ; aucun staging/commit/push.

## Commandes de vérification ciblée

Depuis le checkout principal, avec `SMART_AO_TEST_DATABASE_URL` renseignée explicitement vers une base jetable et `SMART_AO_TEST_DISPOSABLE_DATABASE=1` :

```bash
.venv/bin/pytest -q backend/tests/db/test_case_analysis_summary_sql.py backend/tests/db/test_a1_condition_contract_evidence.py backend/tests/application/test_analysis_follow_ups.py backend/tests/application/test_case_analysis_summary.py backend/tests/api/test_case_analysis_summary_routes.py
.venv/bin/ruff check backend scripts
.venv/bin/mypy backend/app
```

Depuis `web/` :

```bash
npm test -- --run src/features/dce/useCaseAnalysisSummary.test.tsx src/features/dce/CaseAnalysisSummaryPanel.test.tsx
npm run typecheck
npm run lint
npm run build
```

Les recettes navigateur rejouables et journaux complets sont dans le dossier de preuves privé indiqué plus haut. Leur serveur synthétique refuse les routes `/api/` ordinaires et ne contient aucun proxy vers un backend live.

Contrôle de non-activation : les32empreintes du gel candidat v4 `rc-actor-v4-20261019/measurement-freeze.json` sont inchangées. Cette preuve ne s’étend pas aux anciens manifestes contenant les fichiers DCE volontairement modifiés par L04.


## Clôture locale

14empreintes sources inchangées après qualification. Base PostgreSQL jetable vérifiée Alembic0 et conteneur dédié retiré. Aucun schéma ou migration ajouté. WIP principal préservé,branche codex/reconcile-smartao-20261009,HEAD30f26934430095632000a1d82519f61dbb4c6411. Aucunstaging/commit/push. Plan/index/matrice actualisés ; miroir Basic Memory préparé localement seulement,non transmis.

Prochaine étape : L04 — restituer dans la synthèse le fait/extrait source exact, la criticité, les preuves attendues et le risque résiduel déjà enregistrés pour chaque point critique; qualifier ancres, invalidation et lecture Patron, avec UNKNOWN sur les champs absents sans inférer une analyse complète ni modifier confirmations ou portes. DPGF non évaluable par RAG, aucun moteur candidat activé; A1 non admis, A2 générique HOLD et NO-GO public maintenus.
