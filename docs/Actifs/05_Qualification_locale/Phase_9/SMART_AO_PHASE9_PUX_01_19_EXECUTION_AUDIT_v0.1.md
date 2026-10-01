# SMART AO — Phase 9 : audit d’exécution PUX-01 à PUX-19 v0.1

**État :** audit bout-en-bout exécuté sur les preuves disponibles ; parcours complets restant partiels identifiés  
**Date :** 20 septembre 2026

« Exécuter un PUX » signifie faire passer un dossier métier par toutes les
étapes de son parcours, avec ses rôles, pièces, validations, refus, états
inconnus et preuves. Les tests unitaires d’un composant ne suffisent pas à
déclarer un parcours terminé. Cette passe consolide les preuves déjà exécutées
et vérifie que chaque PUX possède une frontière explicite.

| PUX | Parcours métier | État après audit | Preuve disponible / limite principale |
|---|---|---|---|
| PUX-01 | identité → première valeur | PREUVE VERTICALE | EXP-01 prouve MFA, contexte, première Affaire et Accueil ; un test confirme que la fiche Entreprise reste progressive et ne bloque pas la première valeur |
| PUX-02 | radar → qualification → Affaire | PREUVE VERTICALE | EXP-02 prouve fraîcheur, P0/P1, décision indépendante du score et idempotence |
| PUX-03 | opportunité → DCE privé/manuelle | PREUVE VERTICALE | preuve dédiée `SMART_AO_PHASE9_PUX03_PUX04_PREUVE_VERTICALE_v0.1.md` : références serveur, staging privé, upload rejouable, admission et rattachement append-only à l'Affaire |
| PUX-04 | inventaire → lecture partielle → exception sourcée | PREUVE VERTICALE | inventaire de la version applicable avec les sept états de traitement et `issue_code` visible, complété par la lecture partielle (`DceKnowledgePanel`) ; la qualification Golden réelle reste externe |
| PUX-05 | rectificatif → invalidation ciblée | PREUVE VERTICALE | versionnement, impact conservateur et conflits N01 prouvés ; recette multi-surface à faire |
| PUX-06 | points bloquants → décision P2/P3 | PARTIEL | projection, rôles et refus prouvés ; P2/P3 restent `PARTIAL` |
| PUX-07 | prix → couverture → capacité/cash | PARTIEL | import, provenance et inconnus prouvés ; marge complète et partenaires restent non démontrés |
| PUX-08 | réponse → revue → P4 | PARTIEL | plan technique, revue et garde de décision prouvés ; réponse complète et P4 restent `PARTIAL` |
| PUX-09 | P5 → signature → dépôt humain | PARTIEL | candidate, P5, MFA et export prouvés ; dépôt externe non effectué |
| PUX-10 | nouvelle candidate → nouvelle preuve | PARTIEL | redépôt versionné et nouvelle autorisation prouvés ; réception externe non intégrée |
| PUX-11 | résultat par lot → commande → P7 | PREUVE VERTICALE | chaîne WON/commande/P6/P7, inconnus, reprise et idempotence prouvés côté serveur |
| PUX-12 | résultat → REX → enseignement | PREUVE VERTICALE | REX local, portée, validité et lecture Patron prouvés ; capitalisation UI à faire |
| PUX-13 | partage ciblé → aperçu → paquet tiers | PARTIEL | partage versionné, révocation et aperçu N03 prouvés ; upload/notification tiers absents |
| PUX-14 | suspension → relève → pouvoirs distincts | PREUVE VERTICALE | C14 et N04 prouvent suspension, relève et acceptation nominative ; interfaces ADM restent absentes |
| PUX-15 | dernier Propriétaire compromis | PREUVE VERTICALE | `NO_ACTIVE_OWNER`, R03 à double contrôle et MFA prouvés ; parcours visuel à faire |
| PUX-16 | export → litige/conservation → fermeture | PREUVE VERTICALE | N02 et EXP-07 prouvent UNKNOWN, export, conservation, suspension et fermeture refusée |
| PUX-17 | panne IA → manuel → reprise | PREUVE VERTICALE | voie manuelle, `REVIEW_REQUIRED` et reprise sans double publication prouvées |
| PUX-18 | terrain local → attente → confirmé | PREUVE VERTICALE | N05 prouve `LOCAL`, `PENDING`, `CONFIRMED` et refus hors ligne |
| PUX-19 | entretien → réemploi → applicabilité | PARTIEL | capacités d’entreprise et REX existent ; entretien lié à l’Affaire, snapshot et expiration restent à assembler |

## Vérifications exécutées

- registre canonique : C00–C16 et 104 surfaces rattachés exactement ;
- web : 170 tests sur 32 fichiers, typecheck, ESLint et build Vite passent ;
- preuves backend ciblées : les suites documentées dans les freezes EXP-01 à
  EXP-07, C14–C16 et N01–N05 restent les références exécutées ;
- la suite backend non-DB globale a été lancée mais n’a pas fourni de résultat
  exploitable dans cet environnement après les premiers tests ; elle n’est
  donc pas déclarée verte ;
- aucune réception externe, qualification Golden réelle, interface ADM
  complète, marge finale, partenaire ou parcours PUX complet n’est déclaré par
  inférence.

## Décision de sortie

La phase ne peut pas être cochée « PUX-01–19 terminés » : onze parcours ont une
preuve verticale exploitable, huit restent partiels au niveau du parcours
complet ou d’une dépendance explicitement absente. PUX-03/04 ont été fermés le
20/09/2026 : l'Espace DCE prouve l'ouverture depuis les références serveur
(`consultation_id` / `applicable_dce_version_id`), l'upload binaire privé
rejouable, l'admission d'une version avec `corpus_hash` canonique et la relecture
de l'inventaire avec ses états et `issue_code` ; aucun identifiant n'est fabriqué
par le navigateur. La qualification Golden réelle reste externe.
