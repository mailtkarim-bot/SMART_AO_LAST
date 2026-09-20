# SMART AO — EXP-01 Évaluation technique
## WORK_PROPOSAL v0.1

**Date : 14 septembre 2026**  
**Statut : OWNER EXPERIENCE FREEZE — prototype exécutable EXP-01 assemblé, états difficiles parcourus et arbitrages approuvés**

## Verdict

Le parcours nominal d'EXP-01 est exécutable en réemployant le socle actuel : une session obtenue par mot de passe reste limitée à PAGE-002, la MFA ouvre PAGE-003, la personne confirme son entreprise et son rôle, PAGE-006 crée une première Affaire, puis PAGE-007 compose son Accueil à partir des projections autorisées. Un rejeu identique retourne la même Affaire sans duplication.

## Réemploi et écarts

| Étape | Socle réutilisable | Écart bloquant pour la preuve |
|---|---|---|
| PAGE-001 Connexion | login tenant-scopé, mot de passe Argon2id, session courte, renouvellement rotatif | le formulaire expose encore `tenant_id` |
| PAGE-002 MFA | enrôlement TOTP, confirmation, step-up, récupération et révocation | **preuve acquise** : écran exclusif avant accès métier et garde serveur commune |
| PAGE-003 Contexte | acteur, entreprise et rôle résolus côté serveur | **preuve acquise** : le serveur retourne l'espace entreprise et le rôle ; leur confirmation précède tout chargement métier |
| PAGE-004 Configuration | aucune donnée supplémentaire n'est requise par le socle pour créer une Affaire | étape sautée dans le parcours nominal ; elle ne sera ajoutée que si un prérequis réel est identifié |
| PAGE-005 Profil | aucune préférence personnelle n'est requise pour créer une Affaire | étape facultative sautée ; aucune donnée de profil artificielle n'est demandée |
| PAGE-006 Première Affaire | création idempotente d'une Affaire déjà disponible | **preuve acquise** : les mêmes identifiants sont conservés après réponse perdue et le rejeu HTTP retourne la même Affaire |
| PAGE-007 Accueil | Affaires autorisées, file d'actions Patron et journal d'affectation | **preuve acquise** : prochaine action, surveillance et événements réels sont composés ; une projection absente produit un état vide explicite |
| Résultat inconnu de création | `CreateCasePanel` conserve les identifiants de commande et l'idempotence serveur | **preuve acquise** : « Création à vérifier », rejeu explicite avec les mêmes identifiants et aucun succès présumé |
| Invitation nominative | identité et membership `INVITED`, capability `membership.manage`, jetons opaques existants | **émission et acceptation prouvées** : collaborateur nommé, validité 7 jours, réémission sans doublon, activation atomique, consommation unique et réponse publique neutre |
| Reprise après expiration | session serveur expirée refusée ; rotation de refresh unique côté client | **preuve acquise** : expiration non récupérable masquée, dernier contexte confirmé gardé en mémoire et restauré seulement pour le même acteur après rechargement confirmé |

## Preuves exécutées

- Front : le chemin connexion → MFA → contexte → création → Accueil, l'absence de rendu métier sans session et la reprise idempotente sont couverts ; **35 tests ciblés** et la suite complète de **141 tests** passent, ainsi que le lint et le build de production.
- Serveur : **28 tests verticaux**, **81 tests d'intégration réalignés** et **373 tests HTTP unitaires** passent.
- Intégration réelle : une session `PASSWORD` reçoit `403 STEP_UP_REQUIRED` ; une session MFA crée l'Affaire en `201`, puis le même payload retourne `200`, le même `case_id` et `replayed: true`.
- Invitation : migration Alembic jusqu'à `20260914_0068`, émission/réémission, consommation unique, expiration et réponse neutre passent sur PostgreSQL isolé. La session créée après mot de passe reste `PASSWORD` sans MFA ; la garde métier renvoie `403 STEP_UP_REQUIRED`. Commande ciblée : `5 passed`.
- Résultat inconnu : une erreur réseau sans statut HTTP laisse le formulaire visible, affiche « Création à vérifier » et rejoue `command_id`, `idempotency_key` et `correlation_id` inchangés ; seules les réponses serveur confirmées vident le formulaire. Les tests front ciblés et le build passent.
- Reprise de session : un `401` suivi d'un refresh refusé efface le jeton et l'acteur, affiche l'expiration sans donnée métier, puis restaure uniquement le snapshot `identity_id`/tenant/rôle/Affaire/navigation du même acteur après confirmation MFA et rechargement ; un changement de rôle invalide le snapshot et vide les projections locales. La preuve front ciblée passe avec **35 tests**, le build et ESLint passent.

## Preuve verticale minimale réalisée

1. ~~après mot de passe, conserver une session limitée à PAGE-002~~ — prouvé ;
2. ~~refuser toute route métier avec `STEP_UP_REQUIRED` tant que `mfa_verified_at` est absent~~ — prouvé ;
3. ~~après confirmation TOTP, ouvrir PAGE-003 puis PAGE-006~~ — prouvé ;
4. ~~créer une Affaire et vérifier le retour idempotent~~ — prouvé ;
5. ~~couvrir cette seconde tranche par un test vertical ciblé~~ — prouvé.
6. ~~masquer une session expirée et reprendre le dernier contexte confirmé après réauthentification~~ — prouvé en mémoire ; persistance de brouillon différée.

## Contrat minimal PAGE-007 réalisé

- l'entreprise active et le rôle effectif restent visibles ;
- « À faire maintenant » choisit une action Patron autorisée, sinon l'Affaire courante, sinon la création d'une première Affaire pour un Patron ;
- « À surveiller » ne montre que d'autres actions projetées ou un état DCE réellement disponible ;
- « Événements récents » utilise le journal d'affectation existant et déclare clairement son absence ;
- lire un événement ne ferme aucune action métier ;
- les chargements restent tenant-scopés et soumis à la MFA par les gardes serveur existantes.
- sans session, seul le formulaire de connexion est rendu et tout état métier local reste masqué.

La consolidation de la navigation en cinq espaces canoniques, les notifications et l'Administration complète restent hors de cette preuve minimale : aucune surface active ne permet encore de les rendre réelles sans inventer un écran.

La suite front complète dépasse ponctuellement son délai lorsqu'elle utilise tous les workers disponibles sur cette machine. Les tests passent ensemble avec un worker : **141/141**. La suite backend non-DB complète passe à **1 144 tests** ; deux assertions ops historiques restent rouges (ancien head de schéma et guide préproduction déplacé), et deux tests d'extraction sont ignorés faute de PIL. Ces écarts sont hors du périmètre EXP-01.

## Contrat minimal d'invitation et d'acceptation réalisé

- seule une session active disposant de `membership.manage` et d'une MFA récente peut émettre ou réémettre ;
- la première preuve invite uniquement un `COLLABORATEUR`, afin de ne créer aucun privilège Patron ou Propriétaire implicite ;
- l'adresse est normalisée et reliée à une identité unique et à un membership `INVITED` ;
- le jeton aléatoire n'est retourné qu'à l'émission ou à la réémission ; seul son SHA-256 est conservé ;
- la validité par défaut est de 7 jours conformément au cahier v0.4 ;
- réémettre remplace le jeton du même enregistrement et ne crée ni identité ni membership supplémentaire ;
- le contrôle public ne renvoie aucun nom, email, tenant, rôle ou périmètre ; un jeton expiré, ancien ou inconnu produit exactement `404 INVITATION_UNAVAILABLE`.
- `POST /api/v1/invitations/accept` reçoit le jeton et un mot de passe, consomme l'invitation sous verrou et ne renvoie aucun corps ni détail d'identité (`204`).
- l'acceptation exige une invitation courante d'un membership `COLLABORATEUR` dans un tenant actif ; elle marque `accepted_at`, passe l'identité à `ACTIVE`, vérifie l'adresse et active le membership dans la même transaction.
- une identité en attente reçoit un credential Argon2id ; une identité déjà active conserve son credential et doit le vérifier ; aucune route ne remplace un mot de passe existant silencieusement.
- une seconde acceptation et la vérification d'un jeton consommé restent indistinguables d'un jeton indisponible ; aucune session métier n'est créée par l'acceptation.
- les routes métier continuent d'exiger `mfa_verified_at` via la garde commune ; la session PASSWORD issue après activation ne suffit donc pas pour accéder au métier.

La preuve runtime de consommation unique, de l'expiration et de la session `PASSWORD` avant MFA est acquise. Le contrat ne crée volontairement aucune session métier et s'appuie sur la garde MFA existante pour interdire l'accès avant enrôlement et confirmation. Le contrat contexte/rôles fixe désormais Patron comme autorité serveur et Responsable/Expert comme profils sans droits supplémentaires ; leur projection serveur et les refus d'élévation sont prouvés.

La récupération assistée est prouvée dans [EXP-01 — Récupération assistée](SMART_AO_EXP_01_RECUPERATION_ASSISTEE_PREUVE_VERTICALE_v0.1.md) : le code de secours est refusé en step-up, une session `PASSWORD` fraîche plus ce code révoquent sessions et refresh, désactivent le facteur puis imposent le nouvel enrôlement MFA.

## Décision de passage

Le parcours nominal PAGE-001 à PAGE-007, l'invitation nominative, la récupération assistée, les profils Responsable/Expert, la réponse inconnue de création et la reprise minimale de session passent à `FEASIBILITY PROVEN`. Les profils sont projetés par le serveur, sans capacité ni périmètre supplémentaire, et leur contrainte PostgreSQL est prouvée. La reprise est limitée à un snapshot en mémoire du même acteur ; la persistance de brouillons, l'avertissement pré-expiration et l'alignement des durées restent différés. Le prototype exécutable et la matrice des états difficiles sont assemblés dans [EXP-01 — reprise après interruption](SMART_AO_EXP_01_REPRISE_INTERRUPTION_PREUVE_VERTICALE_v0.1.md). Les arbitrages délégués par le propriétaire sont consignés dans [OWNER EXPERIENCE FREEZE EXP-01](SMART_AO_EXP_01_OWNER_EXPERIENCE_FREEZE_v0.1.md). La [maquette détaillée](SMART_AO_EXP_01_MAQUETTE_DETAILLEE_OWNER_FREEZE_v0.1.md) et le [contrat technique consolidé](../02_FUTURE_TECHNICAL/SMART_AO_EXP_01_CAHIER_TECHNIQUE_EXECUTION_v0.1.md) sont rédigés ; la première tranche d'implémentation, limitée à l'origine manuelle réellement complète, est vérifiée par 142 tests front, build et lint. Les origines référencées restent réservées à EXP-02.
