# L04 — synthèse sourcée des douze axes — 20 octobre 2026

## AS-IS / risques / insertion

Checkout principal codex/reconcile-smartao-20261009, HEAD30f2693, WIP préservé. Lecteur DCE/version/couverture/exigences existant et risques structurés Patron-only. Les prototypes RAG/intention restent inactifs. Risques principaux : exposition des risques privés au lecteur Collaborateur, ancien fragment réutilisé après nouvelle extraction, classement documentaire confondu avec évaluation métier, lot déduit, complétude déduite d’un compteur.

## Plan minimal — Superpowers cadrage/TDD et ECC API/vérification

- [x] Projection fermée dans le contexte Case, sur les registres DCE et risques existants ;12 axes stables,signaux à revoir ou non évalués,jamais « analyse complète ».
- [x] Lecteur SQL revalidant version courante,extraction courante,document/input/hash fragment et origine exacte des risques ;sources non prouvées UNKNOWN sans transfert de preuve.
- [x] GET Case existant étendu par route de synthèse réservée au Patron avec CASE_DCE_READ et DECISION_RISK_READ ;aucune capacité nouvelle,aucune commande/confirmation/porte modifiée. Composition sous snapshot transactionnel de lecture.
- [x] Intégration dans le panneau DCE existant,uniquement Patron ;masquage immédiat Affaire/session/rôle/version,réponses tardives refusées. OpenDesign Local Codex catalogue/système existant et Impeccable avant édition UI.
- [x] Preuves pures/HTTP/PostgreSQL et navigateur synthétique,contrôles et revue ;plan/index mis à jour ; miroir Basic Memory préparé localement, non transmis.

Regroupement initial explicite : types candidature/visite → candidature,contenu/canal/échéance/formats → documents,critères → commercial,signaux contractuels → contrat. Risques structurés CCAP → contrat,CCTP → technique selon la catégorie enregistrée,avec classement documentaire candidat seulement. Aucune affectation par recherche de mots dans une note ou un montant. Les autres axes restent NON_EVALUATED en l’absence de projection source qualifiée. Un axe contenant des signaux reste REVIEW_REQUIRED,même si une confirmation humaine existe ;confirmation ponctuelle ≠ revue exhaustive de l’axe. Ni marge/cash/capacité ni droit juridique ne sont déduits.

Exigences et risques conservent leur identifiant natif,état et preuve exacte ;responsable/action/conséquences non raccordés restent UNKNOWN. Les lots candidats déjà ancrés sont montrés comme candidats,applicabilité UNKNOWN. Budget de sortie explicite,limite signalée sans prétendre à l’exhaustivité. Aucune migration ni nouvelle dépendance.

A1 Golden non admis,A2 HOLD,NO-GO public ;DPGF non évaluable par RAG,aucun moteur candidat activé. Aucun backend live/corpus réel/VPS/P3/déploiement/push.


## Résultat local qualifié — assemblage initial, L04 métier PARTIEL

Le GET `/api/v1/cases/{case_id}/analysis-summary` compose les registres existants sous snapshot REPEATABLE READ. Il exige Patron Admin, appartenance, tenant propriétaire et les capacités CASE_DCE_READ et DECISION_RISK_READ. Aucune permission élargie au Collaborateur. Aucun schéma, dépendance, moteur actif ou confirmation modifié.

Le panneau `CaseAnalysisSummaryPanel` est intégré au parcours DCE Patron existant. Les douze axes ont un statut explicite NON_EVALUATED ou REVIEW_REQUIRED, les pièces non lues restent visibles. Exigences et risques gardent leurs identifiants, confirmations/traitements et sources exactes. Les lots sont candidats et l’applicabilité demeure UNKNOWN. Le regroupement par type de registre/catégorie documentaire n’est pas une évaluation sémantique des douze axes. `analysis_complete` reste faux. Les limites de sortie (200 exigences, 100 risques) et troncatures sont explicites.

La source est revalidée contre document/version applicable/extraction actuelle, hash d’entrée et hash réel du fragment, observation et matérialisation courantes, règle et offsets exacts. Une version remplacée, extraction incomplète, preuve discordante ou contexte non courant retire les détails de preuve courante. Le frontend masque immédiatement au changement Affaire/session/rôle/version, refuse les réponses discordantes et tardives, sans résurrection après un aller-retour de contexte.

### Fichiers et points d’insertion

- Case : `application/analysis_summary.py`, `infrastructure/analysis_summary_reader.py`, `public/analysis_summary_contracts.py` ; route HTTP `case_analysis_summary.py`, bootstrap existant.
- DCE : `application/queries.py`, `infrastructure/case_dce_reading_reader.py` ; validation de provenance partagée avec les projections existantes, contrat HTTP DCE conservé.
- Web : `CaseAnalysisSummaryPanel.tsx`, `useCaseAnalysisSummary.ts`, types/API/App existants ; tests de panneau et de hook.
- Régressions backend : tests application, API et PostgreSQL `test_case_analysis_summary*` et double du lecteur DCE adapté au contrat interne.

### Preuves exécutées

Preuves privées : `~/.local/share/smartao-proofs/l04-20261020/`. Manifeste `source-sha256.json` : 19 fichiers source/tests. HEAD inchangé `30f26934430095632000a1d82519f61dbb4c6411`, WIP préexistant préservé ; aucun staging, commit ou push.

| Contrôle | Résultat et portée |
|---|---|
| TDD | 2 rouges projection, 4 rouges route ; revue : 6 rouges provenance/contexte corrigés ; 4 rouges aller-retour contexte corrigés |
| Backend ciblé | 78 réussites, dont 22 nouveaux tests L04 : 2 projection, 4 API, 16 PostgreSQL |
| Backend global | 3 628 réussites, 2 avertissements, 802,33 s, exit0 |
| Web ciblé final | 20 réussites |
| Web global final | 578 réussites, 4 ignorés préexistants C08, 68 fichiers, 80,28 s, exit0 |
| Types et qualité | mypy 642 sources ; types Web, lint backend/Web, build Web et format des 11 Python concernés verts |
| Navigateur synthétique | Chrome DevTools MCP, 21 contrôles sur desktop 1440×1000 et 21 sur mobile 390×844 ; tabulation et défilement horizontal clavier natifs prouvés, sans débordement de page |
| Réseau de recette | 38 GET sous `/synthetic/`, aucun bearer/cookie, aucun backend live ; stockage navigateur vide |
| Semgrep final | 1.179.0, 225 règles, 19 fichiers, zéro finding et zéro erreur ; analyse locale, métriques désactivées |
| Autorités documentaires | 4 tests réussis ; plan : une seule tranche active |
| Secrets | detect-secrets sur les 19 fichiers : zéro résultat |
| Revue ciblée | Défauts de provenance et cache corrigés ; contre-revue sans finding important restant |

Les erreurs initiales d’unicité des fixtures SQL et une course du script navigateur ont été corrigées dans le banc ; elles ne sont pas des défauts produit. Les avertissements backend concernent Starlette/httpx et les métadonnées d’alias Pydantic ; le build Web signale un chunk supérieur à 500 kB.

OpenDesign consulté en Local Codex : catalogue et contexte de l’artefact existant, autorité Owner Freeze v3.1/Cytd et classes production conservées. Aucun Cloud/BYOK/crédit ni nouveau système visuel. Impeccable context, craft-floor et polish consultés ; detect : zéro finding. Aucune nouvelle CSS. Méthode Superpowers cadrage/plan/TDD/debugging/revue/vérification, ECC API et vérification ; Graphify consulté avant navigation ciblée.

PostgreSQL 16 jetable synthétique sans réseau/port publié, tête 0136 exercée par la suite, retour Alembic zéro vérifié puis conteneur dédié retiré. Serveur Vite et client navigateur dédiés arrêtés. Le daemon OpenDesign préexistant est conservé.

### Limites et risques ouverts

Cette recette teste le vrai panneau, son hook et client API contre une API synthétique. Elle ne prouve ni backend live ni parcours d’authentification complet dans App, ni accessibilité exhaustive. Le snapshot de lecture n’est pas une autorisation atomique d’acte métier. La divulgation des ancres ne constitue pas une ouverture du document original.

Les responsables/actions/conséquences non raccordés restent UNKNOWN ; cela ne signifie pas qu’ils sont absents des registres natifs. Les autres axes ne sont pas évalués automatiquement, la complétude de l’analyse métier et des extractions n’est pas acquise. L04 reste partiel ; les pièces non lues, UNKNOWN et REVIEW_REQUIRED restent visibles. Aucun transfert de preuve aux rasters ou corpus historiques, aucune activation des candidats RC/RAG. DPGF non évaluable par RAG. A1 non admis, A2 générique HOLD, NO-GO public maintenus. Aucun corpus réel, VPS, déploiement, P3 ou dépôt externe.

Basic Memory : proposition locale préparée, transmission non exécutée ; le plan reste l’unique autorité de statut.

Prochaine étape : L04 — raccorder les exigences et risques sourcés aux actions, responsables et conséquences déjà enregistrés, avec preuves et portées exactes; rendre visibles les relations manquantes en UNKNOWN, qualifier invalidation et refus tenant/rôle dans la synthèse existante sans modifier confirmations ni portes. DPGF non évaluable par RAG, aucun moteur candidat activé; A1 non admis, A2 générique HOLD et NO-GO public maintenus.
