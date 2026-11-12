# RC — gold et impératifs conditionnels candidats v10 — 18/10/2026

## AS-IS

Checkout principal codex/reconcile-smartao-20261009, HEAD30f2693/WIP conservé. Le plan seul porte le statut. V9 non activé : lot n° et conditionnels omis ; gold sans lot incomplet et attente legacy horaire ambiguë. Trois cahiers actifs : pertinence sourcée distincte de l’applicabilité, UNKNOWN et revue humaine conservés.

## Risques et points d’insertion

Confondre signal conditionnel et obligation certaine, perdre les négations, propager un lot ou un sujet, régler sur le gold historique. Réutiliser project_rc_conflicts, RcSignalAnchor, politique et CLI existants ; option v10 explicite inactive par défaut, v7/v8/v9 préservés. Aucun schéma/dépendance/API/UI/factory modifié.

## Plan minimal et comportements à prouver

- [x] Contre-lecture indépendante du gold sans lot et des contrats legacy/fermé ; correction additive hors historique, pertinence exhaustive des sources indépendamment de la capacité du parseur.
- [x] Rouges/verts sur n°/no et impératifs conditionnels simples avec source/page/région/hash et ancres SUBJECT/DIRECTIVE/LOT/condition ; négation conservée dans la condition, valeur/kind UNKNOWN et REVIEW_REQUIRED ; refus citation, préambule, multi-sujets et condition tronquée.
- [x] Intégration v10 opt-in, CLI exigeant deux attentes explicites et gold de condition indépendant ; intégrité des ancres, isolation, financier, invalidation/retry, compatibilité v7/v8/v9, revue indépendante.
- [x] Nouveau jeu synthétique contre-lu puis gelé ; E5 CPU réel/SQL jetable, sans réglage après mesure ; tests pertinents et suite appropriée, lint/types/format/diff/secrets/Semgrep.
- [x] Nettoyage, case/journal/prochaine étape/index ; miroir Basic Memory tenté mais non synchronisé (refus consigné ci-dessous).

A1nonadmis/A2HOLD/NO-GOpublic ; DPGF non évaluable. Demandes et sources multi-sujets non couvertes UNKNOWN. Aucun live/corpus réel/VPS/P3/déploiement/commit/push.

## Point d’arrêt demandé — nouvelle session

Tranche en cours, non qualifiée. 17rouges puis52tests ciblés verts, Ruff ciblé et mypy636 verts ; CLI des conditions/deux contrats, gold additif, revue code et nouvelle mesure gelée restent à faire. La suite3236 et Semgrep v9 sont antérieurs au WIP v10. Reprise détaillée : [REPRISE_DIRECTE_RC_V10_2026-10-18](../00_Pilotage_et_audits/REPRISE_DIRECTE_RC_V10_2026-10-18.md). Aucun commit/push, DB v10 ou runner actif.

Prochaine étape : ESSAIS DCE — reprendre la v10 locale en cours : matérialiser le gold sans lot contre-lu, expliciter les attentes legacy et intention fermée dans la CLI, valider les ancres conditionnelles UNKNOWN, puis qualifier sur un nouveau jeu gelé sans activer le candidat. Conserver v7/v8/v9, les demandes et sources multi-sujets non couvertes en UNKNOWN et DPGF non évaluable. A1 non admis, A2 générique HOLD et NO-GO public maintenus.

## Reprise exécutée — preuve technique locale, candidat HOLD

### Changement et raison

Reprise vérifiée sur la branche/HEAD demandés, checkout principal et WIP conservés, sans commit/push. Les 52 tests du handoff ont été rejoués avant modification. Le moteur v10 du handoff n’a pas été retouché : le changement de production de cette reprise porte seulement sur `scripts/qualify_candidate_retrieval.py`. La CLI compare maintenant les ancres de condition et valeur/kind au gold indépendant, exige UNKNOWN/UNKNOWN sur un impératif conditionnel, et exige une attente `expected_legacy_intent` distincte de `expected_intent`. Les anciens profils ne demandent pas ce nouveau champ.

Deux défauts ont été observés en rouge : refus d’une condition correctement sourcée UNKNOWN et acceptation de sa falsification REQUIRED/ASSERTION. Deux autres rouges démontrent l’absence du contrat legacy explicite et de sa gate. Huit nouveaux cas CLI passent ensuite, dont ancres absentes/déplacées, gold manquant/déplacé et surcertitude refusée.

### Fichiers et gold

- CLI ci-dessus ; `backend/tests/ops/test_candidate_qualification_cli.py` : 8 nouveaux cas.
- `backend/tests/application/test_rc_conditional_v10.py` : 5 cas supplémentaires, tenant/Affaire/version/FINANCIAL_PRIVATE/PERSONAL_DATA exclus avant encodage.
- `backend/tests/db/test_e5_sql_measurement.py` : 1 cas v10 condition sourcée UNKNOWN, retry stable et invalidation du rattachement de version ; aucun contournement append-only.
- `backend/tests/fixtures/knowledge/btp_rc_imperative_gold_correction_v13a.json` : correction additive contre-lue des six sources sans lot et de l’attente horaire. Le jeu13 historique n’est pas modifié, ni ses rapports. Plafond théorique recall@5 :5/6 ; ce correctif historique sans champ legacy explicite n’est pas présenté comme un nouveau banc v10 exécuté.
- `backend/tests/fixtures/knowledge/btp_rc_conditional_heldout_v18.json` : nouveau jeu synthétique, 15 documents/12 questions, 8 positives évaluables, budget top10 et mesures@5/@10, au plus une source attendue par question. Contre-lecture sans moteur :52ancres UTF8/10spans/5hashes. Nouveaux identifiants/lots et suffixes conditionnels, mais mêmes templates : **pas un holdout aveugle ni statistiquement indépendant**. Cette limite est inscrite dans le JSON avant gel.

Les brouillons v14–v17 sont conservés dans les preuves privées `diagnostic-fixtures/`, avec manifeste de déplacement/hash. V14 mesuré en mémoire seulement puis refus SQL (deux versions courantes) ; v15 corrige ce point et deux ancres SUBJECT manquantes mais conserve un statut `FAILED` inexistant ; v16 utilise `FAILED_SAFE`, refusé comme parent d’un fragment ; v17 utilise `REVIEW_REQUIRED` et passe SQL. Les qrels n’ont pas été ajustés pour faire disparaître les omissions ; moteur/profil/seuil/segmentation inchangés. V17 reste une mesure diagnostique réparée après observation. V18 a reçu une contre-lecture puis un préflight SQL réel, upgrade/downgrade/re-upgrade, avant encodage. Aucun réglage après sa mesure.

### Résultats v18 mémoire et SQL

| Contrôle | Résultat | Limite |
|---|---|---|
| Sources attendues/positives complètes | 6/8 ; rappel@5 et@10=75% | omissions `multiple-source` et `truncated-condition` conservées |
| Retours parasites | 0 ; aucun candidat sur les4questions négatives | corpus synthétique minuscule, autres distributions inconnues |
| Conditions simples | 4/4 renvoyées, UNKNOWN/UNKNOWN avec suffixe entier et négation | aucune applicabilité/obligation certaine ni complétude DCE |
| Contrats d’intention | legacy exact et fermé exact vrais | gate validité d’ancre fausse sur visite : gold `est-elle obligatoire`, moteur `obligatoire`; aucun raccourcissement du gold après mesure |
| Ancres impératives | gate vraie ;33ancres requête/15occurrences de preuve/4ancres condition contrôlées | ce décompte ne prouve pas le rappel des clauses omises |
| SQL et référence | états et métriques exactement identiques ;72requêtes SQL mesurées | pas d’atomicité nouvelle entre deux lectures |
| Fraîcheur/invalidation SQL | 6/6 vrais : initial, extraction changée, ancien fragment absent, version déréférencée, absence courante, historique conservé | transactions synthétiques seulement |
| Coût SQL | p95 chaud37,12ms ; première requête14,96s ; RSS943,83MiB | CPU2/mémoire1200MiB, hors réseau ; hôte non réservé, pas une promesse SLO |

Cinq gates fausses : `critical_complete`, `evidence_recall_at_5`, `rc_query_intent_valid`, `rc_unknown_refusals`, `review_signals`. DPGF demeure non évaluable. Aucun candidat admis, branchement factory/API/UI ou changement du moteur actif.

### Vérifications, incidents et limites

- **3267 tests backend réussis**, zéro ignoré/échec, 1064,59s, PostgreSQL jetable explicite. Deux warnings : dépréciation Starlette/httpx et alias Pydantic sans effet dans une recette EXP05. Les résultats3236v9 ne sont pas utilisés comme preuve v10.
- **90 ciblés purs/CLI** verts ; **5 SQL** verts. Les premiers essais SQL étaient des erreurs de sandbox, puis deux défauts du nouveau test (déballage du tuple helper et tentative UPDATE refusée append-only) corrigés dans le test, sans modifier le produit. La première sélection élargie sans URL DB avait334verts/8erreurs de fixture : elle n’est pas annoncée verte ; la campagne globale avec DB ci-dessus couvre ces tests.
- Ruff/format ciblés7fichiers verts ; mypy app+3scripts **636sources**, zéro erreur ; `git diff --check` vert. Pas de nouveau schéma ou dépendance ; tête Alembic unique `20261010_0136`, migrations exercées uniquement sur bases jetables.
- Semgrep1.179.0 :225règles/7fichiers,0finding/0erreur. Premier téléchargement échoué sous sandbox, relance autorisée réussie ; résultats analysés localement, pas d’envoi distant. Aucun scan de sécurité de tout le WIP revendiqué.
- detect-secrets ciblé : seuls hashes SHA256 de provenance, vérifiés contre les sources synthétiques et triés dans les preuves ; baseline non modifiée. Ce contrôle n’est pas une preuve d’absence absolue de secrets.
- Revue technique indépendante sans édition : gold/corrections/source/CLI, puis nouveau jeu avant moteur. Elle a corrigé sa conclusion initiale trop forte sur la représentabilité SQL ; le préflight réel la remplace comme preuve. Pas d’approbation métier humaine déduite.
- Deux PostgreSQL créés pour cette reprise, réseau absent/socket Unix/tmpfs512MiB, retirés après tests et downgrade ; aucun service existant ni PostgreSQL5432 ciblé.

Preuves privées : `/home/noor/.local/share/smartao-proofs/rc-v10-resume-20261018/` — rouges/verts CLI, `backend-global.log`, `pure-final.log`, `sql-tests-corrected.log`, manifests `freeze-v18.json` et `diagnostic-artifact-map.json`, rapports `v18-v10-reference.json`/`v18-v10-sql.json`, `verification-final.json`, scans et triages. Profils v7/v8/v9 et jeux historiques10/11/13 comparés octet pour octet à la sauvegarde de reprise : identiques. Le gel est vérifié inchangé, y compris les brouillons archivés.

Méthode réellement utilisée : Superpowers using-superpowers/cadrage brainstorming/TDD/diagnostic/revue ; plan de reprise existant conservé, ECC verification-loop pour lint/types/tests/sécurité/diff. Graphify consulté, graphe ancien insuffisant pour le WIP ; Serena initialisé/activé sans onboarding ni navigation sémantique supplémentaire ; Basic Memory miroir du plan. Aucun nouvel usage d’API/bibliothèque nécessitant Context7, aucune UI nécessitant OpenDesign/Impeccable ou navigateur, aucune classification bornée nécessitant Jev, aucune investigation large nécessitant Manus.

### Décision et suite

**Épreuve technique locale exécutée ; v10 non admise/HOLD.** Les deux omissions et la convention d’ancre visite demeurent ouvertes, les sources/requêtes multi-sujets non couvertes restent UNKNOWN. Aucun corpus réel, live, déploiement, P3 ou GO public. A1nonadmis/A2génériqueHOLD/NO-GOpublic maintenus.

Prochaine étape : ESSAIS DCE — expliciter le contrat d’ancre de demande de visite, puis préparer une qualification RC hors templates connus; conserver les sources multi-sujets et conditions tronquées non couvertes en UNKNOWN, v7/v8/v9 et le candidat v10 non activé. DPGF non évaluable; A1 non admis, A2 générique HOLD et NO-GO public maintenus.

Miroir Basic Memory : lecture du projet/note réussie, mais écriture finale refusée par le contrôle automatique d’autorisation (`MCP tool call requires approval, but approval policy is never`). **Non synchronisé**, aucun contournement via fichiers ; le plan local et ce dossier conservent la reprise complète. Contrat documentaire final :4/4verts. Comparaison à l’archive de reprise :aucun fichier manquant, seulement8fichiers préexistants modifiés dans le périmètre autorisé ; tout autre fichier de cette sauvegarde est identique.


## Addendum — contrat expliqué, aucune requalification historique

Le [contrat lexical de demande de visite](RC_ANCRES_VISITE_PREPARATION_GENERALISATION_2026-10-18.md) explicite le span adjectival sans auxiliaire, avec14caractérisations de l’existant. Aucun parseur/profil ni résultat de jeu18 modifié ; sa gate false reste false. Le gold sémantique de généralisation est préparé séparément et non exécuté ; plan seul statut courant.
