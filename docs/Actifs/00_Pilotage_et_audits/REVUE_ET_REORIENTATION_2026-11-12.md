# Revue générale et réorientation — 12 novembre 2026

Le [plan R0–R3](SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md) remplace le journal comme outil de décision. La demande Owner autorise désormais consolidation, commits, intégration et push, mais pas un GO public ou un déploiement implicite.

## Diagnostic

Les dernières sessions L09–L11 ont ajouté des raccordements de recettes et leurs preuves. Les primitives métier étaient déjà présentes ; ces travaux n’ont pas ajouté de parcours applicatif nouveau. La multiplication de compte-rendus et de prochaines micro-étapes a entretenu la progression des preuves sans donner une borne claire d’utilisation. C’est une erreur de pilotage à corriger : les prochaines unités sont des livraisons, pas des variantes de tests.

La version locale contient un ensemble fonctionnel important L01–L11. Elle n’est pas démontrée opérationnelle pour un utilisateur depuis une installation propre. Les sorties avec UNKNOWN protègent les données ; elles ne closent pas les fonctions manquantes. Les blocages structurants restent la pièce de prix publiable, la continuité A1/C3, la reprise durable et la recette produit/exploitation. Les reports Owner sont séparés dans le plan.

## Contrôles du jour

Après fetch, origin/main est ancêtre du HEAD30f2693 :13 commits d’avance, aucun commit distant manquant. Aucun PR ouvert retrouvé par le connecteur. Les worktrees ci-dessous ont des commits déjà intégrés au HEAD, mais leurs modifications locales ne sont pas des commits et ne sont donc pas automatiquement fusionnées. D’autres branches historiques ont des commits non communs : `codex/phase-a0-execution`, `docs/pricing-http-next-lot-28`, `feat/arch001-pricing-scenario-projection-20260830`, `t3code/8cf1106d`. Leur ascendance et leur contenu doivent être classés avant une fusion, sans réintroduire des versions anciennes.

| Worktree/branche secondaire | Fichiers WIP | Variantes différentes du principal |
|---|---:|---:|
| `codex/capacity-input-guard-20261011` | 4 | 2 |
| `codex/dce-analysis-trials-20261011` | 18 | 7 |
| `codex/dce-completeness-trials-20261011` | 22 | 7 |
| `codex/dce-page-coverage-20261012` | 24 | 9 |
| `codex/dce-six-signals-20261012` | 24 | 9 |
| `codex/dce-structured-projection-20261012` | 39 | 9 |
| `codex/p5-contract-audit-20261009` | 0 | 0 |
| `codex/p5-exact-origin-20261009` | 0 | 0 |
| `codex/pdf-coverage-guard-20261011` | 4 | 2 |
| `codex/quality-gates-20261009` | 0 | 0 |

Une archive de tous les WIP de worktrees a été créée avant intégration, avec inventaire sous `.local-proofs/reorientation-20261112/` (hors Git). Les variantes portent notamment sur extraction/analyse DCE, capacité, tests et dépendances. Aucune n’a été supprimée ou silencieusement écrasée.

Ruff global passe. Le formatage avait un seul défaut dans le bootstrap CASH, corrigé sans comportement modifié. Le contrôle CI réel `mypy backend/app backend/tests` rapporte212 diagnostics dans44 fichiers : la vérification antérieure des seuls708 fichiers applicatifs ne suffisait pas à qualifier la CI. Aucune suite backend générale nouvelle n’est revendiquée par cette revue documentaire. Le contrôle de secrets et les résultats Git finaux sont à confirmer dans le relevé de livraison ; un push ou merge non effectué ne sera pas annoncé comme réussi.

## Décision de pilotage

R0 : baseline Git/CI reproductible. R1 : parcours utilisateur complet local, incluant les manques qui empêchent la première promesse. R2 : pilote représentatif autorisé et reprise/restauration. R3 : exploitation explicitement autorisée. Pas de date ferme avant R0 ; fournir alors une estimation mesurée de R1, puis une démonstration, pas un pourcentage arbitraire.

Limiter les lectures au contrat affecté et aux derniers résultats ; regrouper les correctifs ; une campagne globale au jalon pertinent, pas à chaque détail. Une revue ciblée et une passe de correction. Les livrables datés existants restent historiques. Un défaut observé doit être rattaché au jalon actif avec impact utilisateur et critère de sortie, sans créer une nouvelle boucle L01–L11.


**Contrôle de secrets :**450 faux positifs hexadécimaux examinés : champs SHA256 et12 révisions Git de modèles dans36 JSON de fixtures/manifestes. Exceptions enregistrées dans la baseline sans filtre global désactivé ; aucun mot de passe/token identifié parmi ces nouvelles alertes. Les archives privées `.local-proofs/` sont exclues de Git. La baseline complète reste contrôlée par le hook avant publication.


**Vérification avant commit :** scan statique de tous les fichiers source versionnables (mêmes exclusions docs/lock frontend que la CI), comparaison avec la baseline : zéro alerte non triée hors de la baseline elle-même. Le fichier de baseline contient des empreintes de détection et n’est pas une source de credentials ; ses auto-détections ne sont pas ajoutées comme nouvelles exceptions. Le hook direct a dépassé le budget local d’attente ; son passage CI n’est pas revendiqué. Whitespace indexé propre, CRLF CSV et sauts Markdown explicitement reconnus par attributs Git. Les212 diagnostics mypy restent bloquants pour une intégration finale main.


## R0 — intégration et contrôles effectifs

Le socle `c2474dd` et le correctif `0179552` sont publiés sur `codex/reconcile-smartao-20261009`. La [PR #1](https://github.com/mailtkarim-bot/SMART_AO_LAST/pull/1) cible main ; elle n’est pas encore fusionnée. Les constats de push bloqué ci-dessus sont historiques et ont été levés par l’instruction Owner renouvelée de publication R0.

Le contrôle mypy complet passe sur1282 fichiers, Ruff et format passent. Les595 tests ciblés passent. La campagne PostgreSQL complète atteint89,16 % de couverture (seuil85,50 % conservé), avec4236 réussites et3 échecs en9151 s. Les trois échecs ont été reproduits avant correction : le plan ne respectait plus son contrat de marqueur unique, le runbook citait une ancienne tête Alembic, et une attente DOCX gardait UNKNOWN malgré des noms complets explicites sans espaces. Corrections documentaires et attente de test seulement, comparateur métier inchangé ;50 tests des modules concernés et37 tests noms/tailles repassent. Ce relevé ne transforme pas cette campagne globale en succès total.

CI GitHub43257881486 : types/lint/format/secrets verts ; jobs bloqués sur les audits Python, npm et image. Audit Python initial :71 avis/5 paquets ; correctifs verrouillés pour certifi, filelock, setuptools, pypdf6.21.4, Pillow13 avec Docling2.150 compatible. Audit du nouveau verrouillage : aucun avis connu. Image : uv0.12.1 également signalé ; passage au correctif0.13.4 vérifié dans les métadonnées PyPI.

Frontend avant correction des dépendances :805 tests passent,4 ignorés, build et types verts ; avertissement de dépendance React Hook préexistant dans App.tsx et taille de bundle à traiter si impact utilisateur mesuré. Audit npm initial :18 avis ; mises à jour ciblées de Vite/Vitest, ESLint/jsdom et Zod. Minimatch11.0.1 remplace10 seulement sous les deux parents ESLint : les appels installés utilisent Minimatch.match, pas les API retirées ([changelog officiel](https://github.com/isaacs/minimatch/blob/v11.0.1/changelog.md)). Vérifier le même inventaire de fichiers/diagnostics ESLint puis les tests/build ; retirer ces overrides lorsque les parents adoptent la version corrigée. Aucun avis n’est ignoré pour obtenir une CI verte.

Semgrep1.185.0 :79 règles de security-audit sur44 tests modifiés, zéro finding/erreur ; Bandit applicatif sans finding bloquant. Ces analyses statiques ne démontrent ni absence universelle de vulnérabilité ni recette utilisateur.

Branches historiques : trois branches documentaires restent conservées avec leurs anciens chemins. `codex/phase-a0-execution` contient en plus un banc golden DCE de830 lignes absent du socle actuel ; conservé pour examen R2, non réintroduit dans R0 sans besoin de recette. Les dix worktrees sont conservés, leurs sept WIP sauvegardés et committés localement. Pas de suppression, reset, clean, stash ni force-push.


Audit npm après correctifs : zéro avis connu (323 dépendances, outils compris). ESLint conserve exactement231 fichiers et les mêmes compteurs de diagnostics avant/après minimatch. Audit Python du verrouillage corrigé : zéro avis connu. Le scan Semgrep global a exécuté117 règles sur1641 fichiers suivis : une alerte `python.lang.security.use-defused-xml.use-defused-xml` à `pricing/application/import_preview.py:6`, triée comme faux positif sur import de l’exception ParseError, sans appel au parseur XML standard dans ce module. Quatre timeouts de règles sur trois fichiers UI sont repris séparément ; les fichiers ignorés et deux fichiers >1 Mo ne sont pas couverts par ce scan. Aucun résultat Semgrep global exhaustif n’est présumé.


Régressions avec dépendances corrigées :75 tests documentaires hors DB passent ;15 setups ont d’abord refusé une variable de base absente (erreur de commande, pas une régression produit), puis les15 tests PostgreSQL passent après fourniture explicite de la base jetable. Frontend corrigé :93 fichiers/805 tests passent,4 ignorés, build vert. Semgrep sur les trois fichiers repris : zéro finding/erreur avec un worker et timeout30 s.

Une régression de contrat Docker supplémentaire a été observée rouge : `pnpm-workspace.yaml` absent des entrées copiées avant l’installation figée. Le Dockerfile frontend le copie désormais avec les deux manifestes existants ; les contrats ops et mypy sont revérifiés avant publication. Le job frontend CI43309678081 est vert. Son pipeline est remplacé par le SHA incluant ce correctif d’image ; les résultats backend/image doivent être confirmés sur ce dernier SHA.


Scan image du SHA66b1be6 (CI43310478840) : les avis HIGH/CRITICAL initiaux sont résolus. Restent Mako1.4.1, pip26.1.2 et rustls0.23.45 embarqué deux fois dans les outils uv/uvx, en MEDIUM/LOW. L’action Trivy épinglée retire le filtre de sévérités pour SARIF par défaut ([code officiel de l’action](https://github.com/aquasecurity/trivy-action/blob/ed142fd0673e97e23eac54620cfb913e5ce36c25/entrypoint.sh#L69)) ; cette portée n’est pas réduite. Correctifs : Mako1.4.2 dans uv.lock, pip26.2.0 et uv0.13.8 dans l’image ; le Cargo.lock officiel de uv0.13.8 embarque rustls0.23.46. Une nouvelle CI reste nécessaire, aucun vert d’image n’est présumé.


Le scan image suivant (CI43312244128) isole des copies vendoriées dans pip26.2 : certifi2026.6.17, msgpack1.1.2, urllib3 2.7.0 et setuptools70.3.0. Elles ne sont pas remplacées par la mise à jour du verrou applicatif. Les roues officielles pip26.2 et pip courant26.3 ont été inspectées ; ce dernier embarque encore setuptools70.3.0. Le runtime applicatif et les commandes ops ne dépendent pas de pip ; les exigences runtime exportées ne contiennent pas pip. L’image le désinstalle donc après uv sync avec `/usr/local/bin/python` explicitement (le Python du virtualenv est alors prioritaire dans PATH), puis un auto-contrôle de build prouve son absence. Sur l’image Python exacte, sans réseau ni volume, le contrôle est rouge avant retrait et vert après. Les47 contrats ops/Alembic passent. Msgpack de l’outillage dev est également verrouillé au correctif1.2.3. Aucun fichier du scanner ni aucune alerte n’est exclu.


## Timeout CI et retour court sans retrait de tests

Sur2219766, CI43314585181 : frontend et scans des deux images verts. Le backend est annulé par sa limite de45 min, après67 % des tests sans assertion en échec affichée ; cela n’est pas une réussite de suite. La fin du segment collecté comprend les parcours intégrés L04/L08, longs à exécuter.

Le script existant de diagnostic gère maintenant quatre partitions déterministes de modules complets. Chaque job dispose de son runner et de son service PostgreSQL ; aucun partage de base. Les contrôles statiques/secrets/audits restent effectués une fois. L’agrégateur backend refuse un job non réussi, une partition manquante/dupliquée, une donnée vide, un code pytest non nul ou un commit absent/différent. Il valide l’inventaire exact des modules puis combine les données coverage.py ; le rapport final conserve le seuil du pyproject85,50 %. Le seuil n’est pas appliqué aux fragments individuels, qui ne constituent pas une qualification globale.

TDD :12 tests rouges initiaux, puis15 garde-fous verts incluant identités UNKNOWN refusées, combinaison réelle100 % et refus d’une couverture incomplète, plus exercice CLI intégral sur un dépôt synthétique temporaire. Total ciblé62 verts. Collecte effective :4254 identifiants pytest =1217+926+1087+1024, union exacte sans omission/doublon ;550 modules répartis138/138/137/137. Types1284 fichiers, Ruff/format verts ; Semgrep79 règles sur script/tests/workflow, zéro finding/erreur. Actions download-artifact v4.3.0 épinglée au commit officiel vérifié ; artefacts séparés par partition, pas d’écrasement. La CI réelle du nouveau SHA doit encore confirmer l’ensemble et sa durée.


CI43324913879 du8287ffc : qualité/backend, frontend et images verts. Partitions1 et2 vertes ; partition3 termine1019 réussites/5 échecs en17min51 : le simulateur des extras du Dockerfile remplaçait seulement les commandes via PATH et essayait donc d’appeler `/usr/local/bin/python` de l’hôte. Le Dockerfile réel et ses scans passent. Le simulateur redirige maintenant ce chemin absolu vers son Python temporaire, avec citation shell stricte ; aucun installateur hôte n’est exécuté. Les cinq cas en échec et les autres contrats passent :68 tests ciblés, puis2 contrats d’architecture de l’image ;70 réussites distinctes au total. C’était un consommateur omis de la passe ciblée précédente, désormais inclus avec toutes les références au Dockerfile. La partition0 du run précédent est encore en cours ; aucune couverture globale verte n’est revendiquée par ces résultats partiels.
