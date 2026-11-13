# SMART AO — Plan de livraison vers un usage opérationnel

**Réorganisé le :** 12 novembre 2026, sur demande Owner.
**Statut global :** socle Git intégré et qualifié techniquement ; recette utilisateur complète et exploitation réelle non démontrées.
**Tranche active :** R1 — parcours utilisateur complet local.
**Prochaine étape unique :** R1 — qualifier le parcours utilisateur complet sur le socle figé, corriger ses blocages puis livrer une recette locale reproductible sans console ni SQL.

Ce fichier est l’unique statut opérationnel. L’ancien plan est conservé intégralement dans [l’historique](../../Archive/00_Pilotage/PLAN_GLOBAL_HISTORIQUE_AVANT_RECADRAGE_2026-11-12.md). Les cahiers v3.1 restent les autorités de périmètre et de droits. Les bilans et recettes datés sont des preuves, pas des files de tâches concurrentes.

## Vision et définition de « opérationnel »

Une PME doit pouvoir ouvrir une Affaire depuis une opportunité, adopter son profil entreprise, recevoir et remplacer un DCE, traiter les risques, décider humainement, chiffrer, construire un pli contrôlé, puis retrouver les engagements vendus dans la passation, les changements et la clôture. Les rôles, sources, versions, inconnus et responsabilités doivent rester compréhensibles durant ce parcours.

Trois niveaux, sans les confondre :

| Niveau | Résultat mesurable | Situation actuelle |
|---|---|---|
| Utilisable localement | Installation reproductible sur une machine propre ; un utilisateur suit le parcours sans API manuelle ni manipulation SQL, avec aide minimale | Fonctions et recettes présentes ; cette recette utilisateur complète n’est pas acquise |
| Pilote encadré | Corpus autorisé représentatif, plusieurs utilisateurs/rôles, erreurs et reprises maîtrisées, sauvegarde/restauration démontrée | Non qualifié ; autorisations de corpus et environnement à obtenir à ce jalon |
| Exploitable en production | Installation, sécurité, supervision, sauvegardes restaurables, support et critères métier acceptés par l’Owner | Non démontré ; aucun déploiement ni GO public autorisé par la seule demande de nettoyage Git |

**Disponibilité :** le socle de recette est disponible. L’usage local complet se démontre en R1 ; la date du pilote et de la production reste à établir après les recettes R1/R2. Le premier passage utilisateur R1 doit produire les blocages mesurés et une estimation en fourchette ; aucun délai d’usage n’est déduit des seuls résultats CI.

## État fonctionnel consolidé

Les preuves détaillées sont indexées dans [l’index actif](../00_INDEX_DOCUMENTATION_ACTIVE.md) et la [fiche des livrables](LIVRABLES_METIER_ET_PREUVES_2026-10-19.md). « Présent » ne signifie pas complet, conforme ni prêt pour la production.

| Parcours | Acquis localement | Ce qui reste à démontrer ou compléter |
|---|---|---|
| L01 Opportunité → Affaire | Qualification humaine, motifs/inconnus, prévention de doublons, scénario synthétique | Entrée utilisateur complète ; collecte live hors autorisation actuelle |
| L02 Entreprise → profil → adoption | Pièces sourcées, publication/adoption explicite, états de validité et historique | Configuration compréhensible et données représentatives ; validité externe non certifiée |
| L03 DCE et rectificatif | Inventaire lot/version, reçus/exclus/non lus/manquants, invalidation | Réception simple par l’utilisateur, formats/corpus représentatifs et erreurs opérables |
| L04 Analyse | Douze axes et traitements humains sourcés | Exhaustivité automatique non prouvée ; ne pas relancer OCR/retrieval comme projet autonome sans déficit mesuré |
| L05 Décision | Carte d’engagement et décision Patron, conditions et reprise après DCE changé | Cohérence du parcours complet et intelligibilité des conditions |
| L06 Prix | Import, cellules/unités, rapprochement partenaires, coûts partagés, publication et nouvelles revues | Produit financier destiné à l’acheteur distinct des données internes ; couverture économique complète non présumée |
| L07 Capacité/cash | Capacités datées, flux déclarés, provenance et requalification ; inconnus/historique | Recette intégrée sans expertise technique ; pas de disponibilité garantie ni de trésorerie bancaire |
| L08 Réponse/pli | Rédaction sourcée, annexes, revues, manifeste/P5 exact, reconstruction ; flux privés exclus dans les recettes | Pièce financière exportable à cadrer et coder ; offre complète et conformité/signatures non établies |
| L09 Passation | Sources/engagements/manques, reçus distincts, confidentialité synthétique | Réception métier par un conducteur dans le parcours utilisateur complet |
| L10 Changements | Événements, revues et actions sur sources exactes ; anciens actes à revoir | Source A1 courante absente du parcours couplé : C3 refusé/C4 UNKNOWN ; positif C3 séparé ne ferme pas cette continuité |
| L11 Clôture | Réception/réserves/paiements déclarés, invalidation/requalification, refus et histoire | Une invalidation est simulée par insertion SQL dans la recette ; pas une nouvelle passation humaine validée, ni règlement juridique certain |
| T01–T03 Garanties | Nombreux refus, isolation, idempotence, reprise après réponse perdue, tests locaux | Reprise durable après reload/crash réel, matrice de sécurité consolidée et restauration ; couverture non universelle |

Les derniers travaux L09–L11 ont essentiellement raccordé des tests existants. Ils ne doivent plus devenir une nouvelle boucle L01→L11 à chaque précision. Leur valeur est conservée ; leur portée reste bornée.

## Reprise immédiate

Reprendre R1 sur main dans le checkout principal. Référence de recette : `r0-recette-20261112`. Le socle R0 est intégré ; commencer par le parcours utilisateur complet et relever ses blocages, puis corriger ensemble ceux d’une même fonction. Ne pas relancer la boucle L01–L11 de qualifications élémentaires.

## Séquence de codage active V3.1

Une seule file de livraison :

- [x] R0 — socle intégré sur main et figé : `r0-recette-20261112` (`ad2a0b42c5a1768df1f2de7de00e7a9f2af5c83d`).

  Inventorier branches/worktrees/WIP ; conserver les variantes ; exclure archives et état local des commits ; contrôler secrets et dépendances ; consolider, committer et pousser sans force. Vérifier la CI réelle, corriger ses échecs bloquants et figer un SHA. Sortie : principal propre, intégration distante explicitement constatée, commandes reproductibles, preuves liées au SHA. **Clôture R0 :** PR #1 fusionnée ; huit jobs CI verts,4254 tests backend réussis, couverture agrégée89,16 % pour seuil85,50 %. Frontend805 tests réussis/4 ignorés, types/lint/audits et scans des deux images verts. Arbre de main intégré identique à celui testé. Les variantes historiques sont conservées ; principal propre avant le suivi documentaire de clôture.
- [>] R1 — qualifier le parcours utilisateur complet sur le socle figé, corriger ses blocages puis livrer une recette locale reproductible sans console ni SQL.

  Depuis un démarrage propre : Patron + Préparateur + Conducteur, une Affaire de bout en bout, un remplacement de DCE/prix, une perte de réponse et une reprise. Faire l’inventaire des blocages utilisateur, corriger ensemble les blocages d’un même parcours puis rejouer une fois. Inclure la décision sur la pièce de prix publiable et le rattachement A1/C3 si nécessaires à cette première promesse. Sortie : démonstration reproductible sans console/API/SQL manuels, liste courte des limitations acceptées, guide de démarrage exact.
- [ ] **R2 — Pilote représentatif et fiabilité.** Après autorisation du corpus/environnement : jeux représentatifs séparés des jeux de développement, rôles/permissions, gros fichiers et erreurs, reprise durable, données obsolètes, sauvegarde/restauration. Corriger les échecs mesurés ; ne pas optimiser des scores sans lien avec une tâche utilisateur. Sortie : recettes métier signées par l’Owner, échecs critiques fermés et budget d’exploitation mesuré.
- [ ] **R3 — Exploitation encadrée.** Préparer une livraison versionnée et un runbook ; déployer seulement après autorisation explicite. Prouver migrations, restauration, supervision/alertes, authentification, gestion des incidents et droits sur les données. Sortie : décision Owner d’ouverture du pilote/production sur preuves, pas sur le nombre de tests.

**Ordre après chaque livraison :** finir les critères du jalon actif ; fermer ses blocages ; seulement alors activer le jalon suivant. Une sous-tâche terminée ne déplace pas le marqueur. Un besoin découvert devient un défaut rattaché au jalon, avec impact utilisateur et preuve de sortie, pas automatiquement une nouvelle tranche documentaire.

### Preuves R0 et ordre de travail R1

[CI43328769583](https://github.com/mailtkarim-bot/SMART_AO_LAST/actions/runs/43328769583) : quatre partitions PostgreSQL isolées,4254 tests, union exacte des550 modules, source Git identique, agrégateur fail-closed et seuil global inchangé. Partition la plus longue :23min28 ; le job séquentiel antérieur était interrompu à45min/67 %. Les15 garde-fous de partition et de couverture incluent une preuve CLI complète et les refus UNKNOWN.

R1 commence par une recette depuis un démarrage propre avec les trois rôles, un DCE synthétique, son remplacement et une reprise. Produire une liste finie de défauts avec effet utilisateur et reproduction, puis donner une fourchette d’effort sur ces seuls défauts. Les manques déjà repérés (pièce de prix publiable, continuité A1/C3, reprise durable) se traitent selon leur rôle dans ce parcours, dans les modules natifs. La sortie reste un parcours démontré sans console/API/SQL manuels, avec limitations acceptées ; une nouvelle variante de test ne clôt pas R1.

## Travail restant : catégories non interchangeables

1. **Code à compléter :** publication sûre des éléments financiers destinés à l’acheteur, continuité A1/C3 manquante dans le parcours couplé, reprise durable lorsque l’intention doit survivre à un redémarrage. Examiner les modules existants avant tout nouveau registre.
2. **Qualification produit :** lancement et parcours utilisateur complet, corpus représentatif, erreurs/récupération et exploitation. Les tests HTTP synthétiques ne prouvent pas à eux seuls une bonne utilisabilité.
3. **Entrées et actes humains :** pièces, validités, signatures, responsables, dates, preuves et réserves. Ne pas les inventer pour faire passer la recette.
4. **Reports Owner PF31-09 :** moteur juridique/calendaire, sanctions quantitatives, DGD/règlement structuré, cash portefeuille, assurance/HSE automatisés, MIRP avancé, multimétier/private corpus. Maintenus hors de la première promesse.

## Discipline de temps et de crédits

- Une session commence par le plan, l’inventaire Git et le dernier relevé de preuve ; pas par une relecture intégrale des cahiers ou de tous les journaux. Recherche ciblée, puis lecture des seuls contrats affectés.
- Une livraison = un résultat métier démontrable. Les qualifications élémentaires restent des sous-tâches internes ; ne pas demander « continue » entre elles.
- Avant de coder : au plus un cadrage court indiquant le manque, le point d’insertion, les risques et les assertions. Pas de nouveau plan parallèle si celui-ci suffit.
- Tests ciblés pendant l’implémentation ; régression du périmètre à la fin ; suite globale au jalon d’intégration ou si l’impact la justifie. Pas de répétition sans changement ou échec nouveau.
- Une revue ciblée, corrections regroupées, une vérification finale. Pas de générations/agents redondants pour le même sujet.
- Conserver les preuves brutes localement ; un dossier synthétique par jalon, pas un nouveau document pour chaque petit test. Basic Memory est le miroir du plan et des décisions durables, pas un journal de commandes.
- Rapporter : fonction utilisable gagnée, blocages restants, contrôles réellement exécutés, coût/temps observé si disponible, prochaine action exacte. Ne pas inventer un nombre de tokens ou une estimation de crédits indisponible.
- Arrêter une investigation après deux essais sans information nouvelle : expliciter le blocage et traiter le travail indépendant. Ne jamais retirer un contrôle critique pour économiser des crédits.

## Git, historique et autorités

La demande Owner du12/11 autorise consolidation, commits, intégration et push. Elle remplace l’ancienne interdiction de push pour cette opération. Elle n’autorise ni force-push, ni suppression aveugle des variantes, ni dépôt externe de données réelles, ni GO public du logiciel.

Les anciens worktrees ne sont pas une file parallèle de fonctionnalités : leurs commits sont vérifiés par ascendance, leurs WIP par contenu. Une variante obsolète se conserve comme preuve et se classe explicitement ; elle ne remplace pas silencieusement le code plus récent. Ne pas confondre « branche fusionnée » et « fichiers non commités intégrés ».

Les sauvegardes `.local-proofs/`, corpus privés, secrets, caches et états d’outils restent hors Git. Aucun `git add -A` non inspecté. Le journal antérieur est conservé, les contradictions de statut sont résolues par ce plan daté.

## Relevé de la réorientation du12/11

Début de l’opération : branche `codex/reconcile-smartao-20261009`, HEAD `30f2693`,13 commits d’avance sur origin/main et aucun commit distant manquant. Dix worktrees secondaires étaient présents, dont sept avec WIP divergents. Clôture : PR #1 fusionnée, principal sur main, tag de recette publié ; les dix worktrees secondaires sont propres. Les variantes sont sauvegardées et committées localement, sans réintroduction aveugle des anciens contenus. Les contrôles et limites restent détaillés dans le relevé de revue.

Prochaine étape : R1 — qualifier le parcours utilisateur complet sur le socle figé, corriger ses blocages puis livrer une recette locale reproductible sans console ni SQL.
