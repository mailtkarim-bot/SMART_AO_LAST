# RC — banc sémantique, SQL et mesure gelée — 18/10/2026

## AS-IS et risques

Checkout principal/branche `codex/reconcile-smartao-20261009`, HEAD30f26934430095632000a1d82519f61dbb4c6411/WIP conservés. Le gold préparation16documents/18questions et ses faits sont contre-lus, sans moteur. Les CLI existantes exigent des attentes fermées ; le gold sémantique ne doit pas être converti en prédiction de leurs sorties.

Risques : confondre source pertinente et exigence applicable, certifier une condition, mesurer uniquement les formes reconnues, inclure DPGF au rappel, laisser une fuite dans une projection hors hits, comparer uniquement des ensembles sans ordre ni provenance. UNKNOWN/tenant/Affaire/version/classifications/append-only restent obligatoires. Aucun nouveau port, dépendance, schéma ou branchement du candidat.

## Plan minimal et points d’insertion

- [x] Tests rouges sur un adaptateur `scripts/qualify_rc_semantic.py` : refus du gold de préparation, gold/identités/hashes invalides, rappel manqué visible et abstention sûre, financier séparé, surcertitude et source étrangère refusées ; utiliser des données de développement pour ces essais, sans moteur sur le nouveau gold.
- [x] Implémenter l’adaptateur en réutilisant service candidat/scoreur existants ; ne pas éditer moteur/profils/CLI historiques. Rapporter les sorties fermées sans copier leur état dans le gold.
- [x] Créer un dérivé de mesure additif sans modifier les annotations ; fixer les règles de protection des sources multi-sujets/tronquées/citation avant mesure. SQL jetable : chargement réel et fidélité des fragments, puis upgrade/downgrade/re-upgrade ; tests SQL dédiés et revue technique indépendante.
- [x] Geler données/code/profil/tests avant encodage, exécuter mémoire puis SQL hors réseau ; conserver omissions et gates fausses sans réglage après observation. Contrôle positif d’invalidation séparé de la mesure du gold ; déclarer le nombre réel d’appels encodeur.
- [x] Tests appropriés, lint/types/secrets/Semgrep après tests, comparaison états/ordres/provenance, nettoyage des seuls conteneurs créés, plan/index et reprise.

Les faits de condition/heure/citation/disclaimer seront mesurés comme **couverture documentaire des spans**. Ce n’est pas une évaluation d’extraction structurée ou d’interprétation temporelle. Couverture sémantique et acceptation du parseur seront publiées séparément, même si le rappel est nul.

A1nonadmis/A2génériqueHOLD/NO-GOpublic. V7/v8/v9 conservés,v10nonactivée,DPGFnonévaluable. Aucuncommit/push/reset/clean/stash.

## Adaptation exécutée et gel

L’adaptateur est additif : `scripts/qualify_rc_semantic.py`. Il appelle le service candidat existant avec seulement texte de requête, scope et top10 ; les qrels, valeurs et faits ne sont jamais transmis au moteur. Il réutilise `score_queries`/`region_is_covered`, le seeder et le lecteur SQL existants. Les CLI historiques, le moteur et les profils v7/v8/v9/v10 ne sont pas modifiés.

Le dérivé `backend/tests/fixtures/knowledge/rc_semantic_measurement_v1.json` conserve exactement `documents`, `queries`, `source_facts` et `gold_semantics` de la préparation originale, qui reste non exécutable. Seuls type/flags de mesure et protocole de gel sont ajoutés. Le profil doit correspondre **octet pour octet** au profil v10 canonique et à son SHA déclaré, avant seed/encodage. Les sources protégées sont fixées avant mesure : condition complète, coordination de pièces, condition tronquée, article multi-sujets, horaire sans obligation et citation/disclaimer. Les valeurs d’obligation de ces sources ne peuvent être certifiées par ce banc.

Les budgets portent sur les **hits/segments classés bruts** : cutoff@k avant déduplication des sources. `[A,A,A,A,A,B]` ne compte donc pas B dans recall@5. Les sources, rangs et régions conservent leurs ordres ; modèle, révision, runtime, segmentation et seuil ne changent pas.

### TDD et revue avant observation

- 10 cas rouges initiaux sur adaptateur absent, puis développement vert. Un état de test financier a été corrigé (il ne devait pas contenir d’intention reconnue en cas de refus).
- 3 rouges supplémentaires : fuite dans traces, liens, identifiants de revue ; contrôle étendu à ces surfaces.
- Revue indépendante avant gel :3P2 identifiés (compression des rangs, hashes/spans segments/traces, identité exacte du profil) ;4régressions rouges→vertes. Un P2 complémentaire sur traces/revue en refus financier a reçu son rouge puis correction.
- Un cas rouge supplémentaire prouve l’absence de compteur de lectures ; instrumentation ajoutée sans modifier le service pour rendre visible tout rejet avant lecture/encodage. **18 tests d’adaptateur verts**, plus les consommateurs ciblés.
- Aucune sortie du nouveau gold n’a été consultée pendant ces corrections. Revue et contre-revues statiques ; annotations du gold vérifiées identiques. Le SHA de35fichiers (code/tests/profil/runtime/données/harness) a été enregistré avant mesure. **Aucun réglage ni changement de ce gel après observation.**

## SQL réel avant encodage

Préflight et tests :16fragments texte/hash/locator exacts,12sources courantes éligibles, exclusions tenant/Affaire/version remplacée/extraction REVIEW_REQUIRED vérifiées par le lecteur réel. Les quatre faits et17régions sémantiques restent liés aux octets des sources. Le test `backend/tests/db/test_rc_semantic_gold_sql.py` n’appelle ni parseur ni modèle sur le gold.

**6 tests SQL réussis** :ce préflight et5contrôles SQL historiques sur données de développement. Deux bases distinctes, tests et mesure, ont été créées hors réseau sur socket Unix/tmpfs512MiB ; PostgreSQL habituel5432 et services existants non ciblés. Upgrade à la tête unique `20261010_0136`, downgrade→re-upgrade avant mesure ; aucune nouvelle migration.

## Résultat gelé — échec de couverture, abstention conservée

| Axe | Observation mémoire et SQL | Interprétation et limite |
|---|---|---|
| Questions évaluables |17non financières,13positives documentaires,4exclusions | DPGF1cas séparé, non évaluable |
| Rappel documentaire |@1/@5/@10=0 ;0/13positives complètes ;17couples source/question omis | aucune omission effacée par l’abstention |
| Couverture fermée |0/17COVERED ;0/14correspondances sémantiques comparables |3demandes hors enum fermé (multiple/condition), pas forcées en OBLIGATION |
| Retours |aucune source renvoyée,0parasite sur4exclusions | ce n’est pas une précision100% ; aucun retrieval n’a eu lieu |
| Travail effectif du candidat |0lecture source,0batch passage,0passage et0encodage requête | rejet `RC_QUERY_NOT_COVERED` avant SQL/embeddings ; **E5 non évalué sur ce gold** |
| Faits |0/5couples question/fait couverts,4faits uniques | couverture documentaire seulement ; extraction structurée NOT_EVALUATED |
| Sécurité observée |UNKNOWN partout, refus financier exact, ancres requêtes valides, aucune projection protégée promue | gates de source/protection satisfaites sans retrieval ; ne pas en déduire une preuve générale d’isolation du parcours complet |
| Durée des appels rejetés |p95mémoire0,263ms ;p95transportSQLconfiguré0,265ms | ni coût E5 ni latence SQL :0lecture ; ne pas publier comme SLO du retrieval |
| Reproductibilité |états/scores/compteurs mémoire et SQL exactement identiques sur4répétitions | scripts et gold gelés inchangés après mesure |

Le modèle n’est pas mis en cause par cette épreuve : la frontière observée est la grammaire de l’intention fermée, qui bloque toutes ces formulations avant l’accès documentaire. Les mesures précédentes sur d’autres jeux ne sont pas recalculées ; comparer leurs pourcentages directement à ce jeu différent ne démontre pas une régression du moteur.

## Contrôles positifs séparés, incident conservé

Un contrôle synthétique connu a été exécuté **après mesure**, sous un scope explicitement admissible pour la source qui était étrangère au scope du gold. Il n’est ni ajouté aux qrels ni compté dans les résultats ci-dessus. Le runtime E5 CPU hors réseau et le parcours lecteur/service ont effectivement été sollicités dans ces contrôles connus.

Le helper séquentiel historique a produit **5/6vrais** :initial attendu, extraction changée, ancien fragment absent, absence de source courante, fragment historique conservé ; `version_dereferenced=false`. Après avoir invalidé l’unique source du scope, le helper retournait NO_CURRENT_SOURCE avant encode_query ; le callback `unlink` n’a donc pas été exécuté. `no_current_source=true` ne prouve aucune déréférence. Cette limite de protocole a été confirmée par revue statique ; le premier résultat et l’arrêt du harness sont conservés, pas annoncés entièrement verts.

Un **contrôle isolé distinct**, avec gel complémentaire de son script avant exécution, démarre sur une autre source courante vérifiée et déclenche alors la déréférence pendant encode_query. Résultat :`SOURCE_CHANGED`,0hit/0trace,réponseUNKNOWN. Ce contrôle valide la phase manquante sans rejouer ni corriger le gold ou le candidat. Le helper partagé n’a pas été modifié après mesure. Downgrade final de la base de mesure exécuté séparément après ces contrôles.

## Preuves et limites de clôture

Preuves privées :`~/.local/share/smartao-proofs/rc-semantic-qualification-20261018/` :rouges/verts,`freeze.json`,préflight/snapshotSQL,`reference.json`/`sql.json`,`positive-control.json`5/6,`version-control-isolated.json`,`verification-final.json`,logs/argv de chaque phase et contrôles de sécurité.

Le scoreur contrôle aussi les sources dans les liens, traces et identifiants de revue ; les segments sont reliés au texte/hash et les ancres aux octets source/requête. Cela ne remplace ni l’évaluation d’extraction structurée, ni l’atomicité entre lectures, ni une recette live/authentification/MFA/permissions. Petit corpus synthétique diversifié hors templates simples, pas holdout aveugle ou statistiquement indépendant. Aucun appel financier au service de recherche n’est admis ; DPGF n’entre pas au rappel.

Tests globaux et nettoyage final à consigner ci-dessous. Candidat **HOLD/non activé** ; aucun acte métier, admission A1, déploiement ou GO public. Revue Superpowers/TDD et ECC verification-loop ; Graphify consulté (graphe ancien), Serena déjà activé dans la session. Pas de nouvelle API/SDK à documenter via Context7, d’UI pour OpenDesign/Impeccable/navigateur, ni besoin de Jev/Manus pour ce banc borné.


## Clôture technique locale et limites de preuve

- **3301tests backend réussis**,0ignoré,2warnings,1328,22s ;PostgreSQL jetable explicite. Warnings historiques Starlette/httpx et alias Pydantic dans une recette Collaborateur. La collecte de ce run précédait le dernier cas de compteur sans travail ; ce cas est inclus dans les **152ciblés finaux verts**, dont18cas d’adaptateur. Collecte finale3302cas :aucun cas nouveau laissé sans exécution, mais ne pas présenter3302comme le compteur de la campagne globale.
- **6tests SQL verts** (fidélité du nouveau gold et5contrôles développement),4contrats documentaires verts avant actualisation du plan ;contrôle documentaire final rejoué après actualisation. La source unique du contrôle positif séquentiel5/6 reste une limite distincte de ces tests.
- Ruff/format3fichiers verts ;mypy app+4scripts **637sources**,0erreur ;mypy3fichiers adapter/tests vert ;`git diff --check` vert. Aucun code métier, profil, dépendance, schéma, API ou UI modifié.
- Semgrep1.179.0 **225règles/3fichiers**,0finding/0erreur. Téléchargement initial bloqué sous sandbox ;première revue automatique de relance expirée,unique retry borné120s autorisé et réussi. Pas de résultat de sécurité annoncé pendant l’indisponibilité ;analyse locale seulement,aucun résultat envoyé.
- detect-secrets :36signaux de hashes SHA256 synthétiques de provenance, tous triés par ligne/usage ;baseline inchangée. Ce scan ciblé n’est pas une garantie globale d’absence de secrets.
- Les deux bases créées pour cette tranche ont été ramenées à Alembic base puis retirées ;la base de tests avait0ligne dans `alembic_version` après la suite. Aucun service existant ciblé.
- Relecture du gel35fichiers inchangé,états/scores/compteurs mémoire=SQL,texte/hash/locator des16fragments SQL vérifiés. Tous les fichiers WIP présents au départ étaient identiques avant les mises à jour documentaires ;le contrôle final de périmètre est consigné dans les preuves.

**Épreuve exécutée ; généralisation insuffisante, candidat HOLD/non activé.** Les tableaux de sécurité vrais dans cette mesure ne qualifient pas le parcours retrieval complet puisqu’il n’a pas été sollicité. A1nonadmis/A2génériqueHOLD/NO-GOpublic. Aucune activation/déploiement/commit/push. L’étape suivante doit partir d’un corpus de développement distinct et d’un contrat d’abstention explicite ;ne pas régler les expressions ou le modèle sur ce gold mesuré.

Prochaine étape : ESSAIS DCE — cadrer sur un corpus de développement distinct une reconnaissance d’intention plus générale et son contrat d’abstention, puis préparer une nouvelle qualification indépendante; ne pas régler sur le gold sémantique mesuré. Conserver les demandes multiples et les sources multi-sujets ou tronquées non couvertes en UNKNOWN, v7/v8/v9 et v10 non activée. DPGF non évaluable; A1 non admis, A2 générique HOLD et NO-GO public maintenus.


Clôture du 19 octobre 2026 :miroir Basic Memory synchronisé et relu,une seule occurrence du résumé de mesure. Conservation finale :35hashes du gel inchangés,annotations préparation/mesure identiques,aucun fichier WIP de départ manquant ;seuls3documents préexistants de pilotage ont été modifiés. Branche/HEAD conservés,sanscommit/push.


## Addendum — cadrage suivant proposé

Le [cadrage d’intention du19/10](RC_INTENTION_GENERALE_CADRAGE_2026-10-19.md) prépare développement distinct etchallengeindépendant scellé,sansmoteur ;choixmécanismeencoreouvert. Aucun exemple,score ou fichier de ce banc mesuré n’a été corrigé pour ce cadrage. Planseulstatutcourant.
