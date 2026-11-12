# Intention RC fermée — candidat v8 — 18 octobre 2026

## AS-IS, risques, points d'insertion, plan minimal

Checkout principal codex/reconcile-smartao-20261009, HEAD30f2693/WIP conservé. Index/plan actifs et autorités v3.1 relus : provenance exacte, UNKNOWN, non-inférence des droits et applicabilité. Jeu10 : paraphrases de questions0/20couples, sources non canoniques0/3, demande multiple0/2. Aucun réglage après mesure des jeux historiques.

Risques : reconnaître un sujet sans comprendre la demande, confondre horaire et obligation, inventer une portée, réécrire la requête avant encodage, changer v7. Réutilisation : RcQueryLot pour la portée et RcSignalAnchor pour les spans exacts. Nouveau RcQueryIntent fermé (sujet/demande/couverture/portée/ancres/hash de requête), sans port ni fournisseur supplémentaire. Politique rc-intent-v8 opt-in; profils1–7 conservés.

- [x] Tests rouges du contrat puis parseur minimal; paraphrases simples, ambiguïtés, requêtes temporelles, budget et ancres UTF8.
- [x] Routage candidat et refus avant source/encodeur pour une intention non couverte; scopes, garde financier, retry, source périmée et compatibilité v7.
- [x] Validation CLI de l'intention et de ses ancres; revue indépendante avant gel.
- [x] Nouveau jeu11 gelé et E5CPU/SQL réel, sans retouche après mesure; source impérative/portée locale/multi-demande restent hors extension.
- [x] Suites pertinentes, lint/types/format/diff/secrets/Semgrep, cleanup, plan/case/journal/index et miroir Basic Memory.

Budgets : CPU2/1200MiB/sansswap/600s, PGCPU1/768MiB/tmpfs512MiB, conteneurs sans réseau et socketUnix seul. Aucun moteur actif/factory/API/UI/schéma/dépendance modifié; v7/v8 non activés, DPGF non évaluable, A1nonadmis/A2HOLD/NO-GOpublic. Pas de corpus réel/backendlive/VPS/P3/déploiement/commit/push.

## Résultat technique et qualification gelée

Intention RC v8 opt-in codée : sujet/demande/portée/couverture fermés, ancres exactes UTF8 et hash de la requête originale; refus avant source/encodeur hors couverture et garde financier avant parseur. V7 conservé, aucun moteur actif remplacé. 507 tests pertinents réussis (50 cas nouveaux), Ruff/format/mypy636/diff verts. Semgrep1.179.0/225 règles/8 fichiers :0finding/0erreurJSON,1avertissement fixpoint de règle boto3 sans appel boto3 dans le périmètre. Baseline secrets :3empreintes publiques précises ajoutées,aucun secret. Jeu11 gelé :16documents/29questions/14annotations;14/18questions positives évaluables complètes contre2/18pourv7,20retours source pertinents/0parasite et0/10cas attendus sans candidat. Clauses :20/25occurrences détectées contexte inclus,14projetées pertinentes,5omissions;11contextes hors sujet,0extra projeté/valeur connue fausse/type connu faux/surcertitude. Quatre besoins incomplets :lot en tête,formulaire au passif,source impérative,demande composée. Deux intentions non reconnues;3gates fausses (critical_complete,evidence_recall_at_5,rc_query_intent_exact),HOLD/admittedfalse. 72ancres requête fournies valides,103occurrences de preuves source vérifiées,16fragmentsSQL;6/6contrôlesSQL vrais. E5CPU/SQL v8 p95chaud33,125ms,froid15,020s,RSS888,793MiB,cgroup938,668MiB sous1200MiB;144statements+12validation. Comparaison v7 source virtuelle et v8SQL descriptive,ne sépare pas coût politique/transport. Aucun réglage après mesure;18SHA code/profils/tests/gold gelés inchangés. PostgreSQL jetable tête0136→base,Alembic0;3conteneurs dédiés retirés,modèles exit0 sansOOM. Aucun backend live/corpus réel/VPS/déploiement/P3/activation/commit/push;HEAD30f2693/WIP conservés. A1nonadmis/A2HOLD/NO-GOpublic.

## Fichiers et preuves reproductibles

- Parseur : `backend/app/modules/knowledge/application/rc_query_intent.py`; intégration : `candidate_retrieval.py`; contrat profil : `domain/embedding_profile.py`.
- Profil : `ops/retrieval-candidate/profile-v8.json`; CLI : `scripts/qualify_candidate_retrieval.py`.
- Régressions : `test_rc_query_intent.py`, `test_rc_intent_retrieval.py`, `test_candidate_qualification_cli.py`, `test_e5_sql_measurement.py`.
- Gold : `backend/tests/fixtures/knowledge/btp_rc_intent_heldout_v11.json`, SHA256 `a54faded6d5cf1eb4c15ed8182070c7dea32eccb1406016e9b8b6c68531b7bfa`.
- Preuves privées : `~/.local/share/smartao-proofs/rc-intent-v8-20261018/` : rouges parser28/service15/CLI2, UTF8, portée et sémantique des ancres; `targeted-final.log`, `ruff.log`, `mypy.log`, `semgrep.json`, `verification.json`, rapports v7/v8 et scores clauses, manifeste18SHA, logs migration/cleanup.

## Invariants, revue et limites

Isolation tenant/Affaire/version et classes privées, refus financier avant lecture/encodage, invalidation après changement de source, retry et requête originale inchangée couverts. Couverture COVERED décrit la reconnaissance de la question, jamais la complétude des sources ou l’applicabilité. Aucune migration ni nouvelle dépendance. Revue indépendante avant gel : deux défauts du validateur corrigés après rouges (ancre sémantiquement mal rattachée et liens non couverts), contre-revue et contrôle des résultats réalisés. Méthode Superpowers cadrage/TDD/revue/vérification et ECC verification-loop; Graphify consulté, aucune édition UI.

La suite backend globale et Web ne sont pas rejouées; preuve synthétique seulement, aucun DCE entier déclaré complet. Les conditions locales et demandes composées ne sont pas qualifiées généralement. Deux formulaires naturels restent non couverts; ne pas régler sur le jeu11 après mesure. Les temps v7 virtuel/v8SQL ne permettent pas d’attribuer un écart au seul parseur. Les douze rasters historiques/28omissions restent hors périmètre.

Prochaine étape : ESSAIS DCE — corriger sur développement les deux formes d’intention encore omises (lot en tête et formulaire au passif), puis projeter les obligations sources impératives simples avec sujet, portée et ancres exactes; conserver les demandes multiples non couvertes en UNKNOWN et requalifier sur un nouveau jeu gelé sans activer le candidat. Conserver v7 et v8; DPGF reste non évaluable. A1 non admis, A2 générique HOLD et NO-GO public maintenus.
