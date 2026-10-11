# Revue du dépôt et livraison GitHub — 11 octobre 2026

## État Git et périmètre

Le checkout principal est `/home/noor/PROJECTS/BTP/SMART_AO_V8`, branche `codex/reconcile-smartao-20261009`. La base de revue est `e48de13b970163f4d6b191439ce19935cb53d697`; 19 fichiers suivis modifiés et 3 fichiers non suivis portent P5/export, la migration de rollback et CT31-39 à CT31-42. Aucun conflit, merge ou rebase en cours n’a été trouvé. Les trois anciens worktrees restent préservés.

Le remote `origin`, confirmé par le connecteur GitHub, est `mailtkarim-bot/SMART_AO_LAST`; le dépôt est public. Le nom local SMART_AO_V8 désigne le produit et le répertoire, pas l’identifiant distant. Le mapping local Basic Memory a été corrigé pour refléter le remote existant.

Après `git fetch origin --prune`, `origin/main` est `657b21362133a2391a43fade319047a65af4169b` et ancêtre de HEAD : 0 commit distant divergent, 9 commits locaux non présents dans main avant cette livraison. La branche de travail n’existait pas encore sur GitHub. Le merge local `8f0b3ad` conserve les parents `d5fe733` et `608a6ea` de l’intégration des gates qualité. Aucune fusion supplémentaire n’est nécessaire pour synchroniser cette base; main et les autres branches ne sont pas modifiés par cette livraison.

Le delta historique vers main est volumineux (538 fichiers au HEAD de reprise). Cette revue inspecte l’histoire Git, ses chemins et contrôles, puis le diff logiciel C10/P5 actuel; elle ne prétend pas être une revue indépendante exhaustive de chacun des fichiers historiques.

## Risques corrigés avec régressions

Les chemins réels `LinkCaseDceVersionHandler` et `RecordDceRequirementConfirmationHandler` pouvaient committer un rectificatif ou retirer une confirmation après revalidation C10, avant commit d’export. Le test historique ne faisait qu’un UPDATE sans changement du package Préparation. Deux régressions rouges ont reproduit ces commits concurrents. Le lecteur Submission verrouille désormais Préparation, puis Affaire/DCE et les exigences/confirmations sélectionnées par le plan, dans l’ordre des writers existants, jusqu’au commit. Les UUID des exigences sont triés, les lectures sont tenant/DCE-scopées et rechargées après attente. Les writers terminent après l’export; l’export suivant est refusé avec le code public expurgé `EXPORT_REJECTED`, sans nouvel audit, événement ou outbox.

L’UI pouvait envoyer deux POST P5 simultanés, puis laisser une réponse ancienne effacer une nouvelle intention UNKNOWN. Une réponse tardive de préparation pouvait également changer la sélection/effacer l’intention, et un GET manifeste tardif pouvait empêcher le retry exact. Les régressions rouges couvrent ces entrelacements. Un seul POST reste maintenant en cours; la libération vérifie l’identité de l’intention, et les projections tardives recontrôlent sélection et intention après leur await. Le retry explicite UNKNOWN garde son corps et ses identifiants. Les GET commencés avant P5 sont invalidés pour ne pas effacer un reçu réussi. Le workspace Remise est désormais remonté à chaque changement de session/tenant/Affaire; un retour tardif ne publie plus de message dans un autre scope et un ZIP tardif ne déclenche plus de téléchargement après démontage. Ces défauts ont des régressions rouges puis vertes; une régression avec consultation présente prouve également l’effacement du message P5 déjà publié au changement de scope authentifié, avant affichage. Aucun ajout visuel, dépendance ou abstraction de domaine.

Ruff a aussi détecté une ligne trop longue dans le downgrade et mypy un alias de variable utilisé comme classe par le test ZipFile. Les deux corrections conservent les mêmes chaînes SQL et le même comportement du test. Le suffixe `.coverage.*` des workers a été ajouté au gitignore après apparition de ces artefacts; aucun artefact de couverture n’est indexé.

## Preuves de ce snapshot

- PostgreSQL 16 digest-pinné, nouveau conteneur identifié `push-review`, port aléatoire lié à `127.0.0.1`, données en tmpfs, aucun volume ou base existante réutilisé. Les seuls nettoyages visent ce conteneur. URL DB et opt-in jetable explicites.
- Backend ciblé C10/P5/rollback : **58/58**, avec les trois writers PACKAGE/DCE/CONFIRMATION, refus après modification, intégrité et compatibilité legacy. Upgrade/downgrade/ré-upgrade Alembic passent; tête unique `20261010_0136`.
- Backend global final : **2213/2213**, deux avertissements de dépendances, 1130,02 s; upgrade → downgrade base → ré-upgrade réussis. La campagne précédente mesurait **87,96 %** de couverture sur le même code applicatif backend, avec 2212 réussites et un échec documentaire : la case A1 différait de la prochaine étape unique. Cette incohérence a été corrigée, les quatre contrats documentaires ont passé et la suite globale entière a été rejouée avec succès.
- Web global final : **530/530**, **66 fichiers**, aucun ignoré, 99,76 s, mono-worker; preuve C08 HTTP synthétique fournie. Une campagne intermédiaire a échoué sur deux attentes PUX-19/C09 sous charge concurrente backend; le rejeu global sans cette charge passe, sans modification de ces assertions ni hausse des timeouts. Typecheck, ESLint et build passent. Le bundle principal de 700,79 kB garde l’avertissement connu >500 kB; aucune limite de build abaissée.
- Ruff global `backend scripts` et format **1184 fichiers** verts; mypy **1028 sources** vert. Revue indépendante ciblée après corrections : aucun finding restant dans les scénarios examinés; ce n’est pas une preuve exhaustive de tous les writers.
- Hook detect-secrets conforme à la CI : 0 alerte; Bandit backend : 0 finding. Scan supplémentaire docs : 2444 candidats triés en 2434 empreintes d’intégrité, un chemin de fichier, huit URL DB loopback de fixtures et un exemple de champ password; aucune credential réelle identifiée. Les quatre candidats de l’historique non poussé sont les mêmes fixtures déjà triées. Aucun chemin `.env`, clé privée, base ou ZIP n’apparaît dans les commits non poussés.
- Audits de dépendances Python et Node : aucune vulnérabilité connue signalée (pip-audit strict et pnpm audit).
- Semgrep 1.179.0 `p/security-audit`, métriques désactivées : 225 règles, 945 fichiers, 0 finding/0 erreur; cinq analyses de taint atteignent leur limite. Une passe ciblée, incluant explicitement la migration non suivie, examine 16 fichiers avec 0 finding/0 erreur et quatre avertissements de taint. La passe UI finale couvre cinq fichiers, puis les deux fichiers App retouchés sont rescannés : 0 finding/0 erreur, sans avertissement de taint sur cette dernière passe. Les avertissements restent consignés, sans ignore ajouté; ils limitent la complétude du scan. Aucun code ou résultat n’est envoyé vers un service distant.

## Réconciliation documentaire et limites

Le plan garde une seule tranche produit active : GATE A1. CT31-42 demeure une recette navigateur datée, clôturée par l’Owner uniquement dans son périmètre synthétique; elle n’est pas extrapolée aux corrections de concurrence CT31-43. Aucun nouveau parcours navigateur, corpus réel ou backend live n’est qualifié par cette revue.

CT31-41 prouve des écritures legacy émulées et l’inspection statique de `d1f6db8`; l’ancien binaire n’a pas été lancé. La garde GUC/trigger n’est pas une protection contre du SQL arbitraire sous le rôle applicatif. L’ancien binaire reste interdit en exploitation sur une base schema 3.

## Livraison autorisée

Commit logiciel vérifié : `2800bbda398027662a911deb11cdb24f809d6add`. Le commit documentaire qui suit contient la réconciliation du plan, du cahier technique, du runbook et de ce dossier.

L’Owner a explicitement demandé ce push GitHub le 11 octobre. Les changements sont répartis en commits logiciels et documentaires cohérents sur `codex/reconcile-smartao-20261009`, puis publiés avec un push normal et un upstream, sans force-push ni réécriture de l’histoire. La présence du commit distant et la propreté du checkout sont vérifiées après le push; le SHA courant se résout par `git rev-parse origin/codex/reconcile-smartao-20261009`.

La publication du code dans le dépôt GitHub ne vaut pas GO produit. Aucun VPS, déploiement, effet P3, dépôt métier externe ou ouverture publique de l’application. Le workflow CI existant écoute les pushes main, les PR et workflow_dispatch; un simple push de cette branche ne constitue pas une exécution CI GitHub.

**Méthode :** Superpowers using-superpowers, requesting-code-review, systematic-debugging, TDD, finishing-a-development-branch; ECC git-workflow, security-review et verification-loop. Graphify a orienté la revue; GitHub a confirmé le dépôt et les refs; Basic Memory reste miroir. OpenDesign/Impeccable ne sont pas requis pour les corrections du hook sans évolution visuelle.
