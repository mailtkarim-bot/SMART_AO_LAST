# SMART AO — C14 : gouvernance des membres, rôles et délégations

**Statut :** preuve verticale C14 complète implémentée et testée  
**Autorités :** cahier OWNER v0.4, §8, OWN-01/02, R02/R03 ; catalogue UX OWNER v0.3, C14 et ADM-01 à ADM-10.

## Constat du code vivant

Le socle de sécurité possède déjà des éléments utiles :

- `TenantMembershipRecord` relie une identité à un tenant avec les états `INVITED`, `ACTIVE`, `SUSPENDED`, `REVOKED` et `EXPIRED` ;
- une session ou un refresh est refusé quand le membership devient inactif ;
- l’invitation nominative, l’activation et la MFA existent ;
- les capacités sont calculées côté serveur ; un Collaborateur ne peut pas s’octroyer un rôle par le navigateur ;
- les affectations d’Affaire se suspendent, se réactivent et se terminent déjà avec journal.

Le socle ne couvre pas encore la gouvernance C14 :

- `PATRON_ADMIN` confond aujourd’hui l’autorité métier Patron et la propriété organisationnelle ;
- l’index `ux_memberships__active_patron` impose au plus un Patron Admin actif, contraire à OWN-02 qui autorise plusieurs Patrons ;
- l’invitation crée uniquement un `COLLABORATEUR` ; aucun flux n’attribue explicitement Administrateur, Patron ou Propriétaire ;
- `PATRON_DELEGATE` existe dans le vocabulaire, mais aucun registre persistant ne porte délégant, délégataire, porte P0–P7, périmètre, durée, plafond, révocation ou approbation ;
- aucune propriété organisationnelle, aucun transfert, aucune protection du dernier Propriétaire et aucune récupération R03 n’existent ;
- suspendre directement une ligne membership bloque bien l’accès, mais il n’existe pas encore d’acte Patron gouverné qui révoque les sessions, délégations et accès partagés liés.

## Contrat métier minimal

Les concepts suivants restent séparés :

| Concept | Rôle |
|---|---|
| Propriétaire organisation | Autorité administrative nominative, distincte du Patron métier ; au moins un est désigné. |
| Rôle métier | Patron, Responsable, Expert, tiers : il ne crée pas de propriété organisationnelle. |
| Délégation | Autorisation explicite, non transmissible, bornée par porte, périmètre, durée et éventuellement plafond. |
| Suspension | Coupe l’accès sans supprimer identité, décisions ni historique. |
| Relève | Réaffecte les éléments actifs par actes distincts ; elle ne réécrit pas les décisions passées. |
| Récupération du dernier Propriétaire | Procédure exceptionnelle fondée sur une preuve organisationnelle ; le support n’acquiert aucun pouvoir métier. |

## Invariants à imposer

1. Une organisation conserve au moins un Propriétaire nominatif désigné, même si son accès est suspendu pour compromission.
2. Le dernier Propriétaire peut être suspendu immédiatement en cas d’incident ; les actes réservés restent alors bloqués.
3. Un transfert de propriété, une élévation de rôle ou une délégation sensible est un fait append-only, motivé et audité.
4. Une délégation expire sans renouvellement implicite, n’est pas transmissible et ne modifie pas les décisions passées.
5. La suspension révoque les sessions actives et invalide les délégations futures ; l’historique demeure.
6. L’Administrateur ne peut pas se donner un pouvoir Direction, Patron ou financier qu’il ne possède pas.
7. La récupération du dernier Propriétaire exige une preuve d’autorité organisationnelle, deux intervenants support distincts et un journal consultable après récupération.

## Preuve implémentée

La première preuve C14 est maintenant portée par les migrations `20260920_0085`/`20260920_0086` et le service `MembershipGovernanceService` :

- `tenant_owners` désigne nominativement le Propriétaire d'organisation ; plusieurs `PATRON_ADMIN` actifs sont désormais possibles sans leur donner cette propriété ;
- le bootstrap du premier Patron crée simultanément le premier Propriétaire ;
- `membership_suspensions` conserve l'acte append-only, son motif, sa justification, sa corrélation et son identifiant d'idempotence ;
- seul un Propriétaire désigné peut suspendre un membre ; un Patron non désigné est refusé ;
- la suspension passe le membership à `SUSPENDED` et révoque, dans la même transaction, toutes ses sessions actives en incrémentant leur version de jeton ;
- le rejeu de la même intention ne crée ni second acte ni seconde révocation ; le dernier Propriétaire peut être suspendu en cas de compromission, conformément à OWN-02.
- `tenant_owner_changes` conserve chaque désignation ou transfert avec l’acteur, le membre précédent, le nouveau membre, le motif et l’identifiant d’idempotence ; la projection `tenant_owners` conserve les propriétaires courants sans supprimer les actes passés ;
- une désignation n’altère jamais le rôle métier de la cible ; un transfert termine seulement la projection de l’ancien propriétaire et exige que la nouvelle cible soit déjà membre active ;
- un Patron non propriétaire ne peut ni désigner ni transférer une propriété ; aucun rôle n’est ajouté depuis le navigateur et le support n’est pas un chemin d’élévation.

La preuve PostgreSQL couvre la séparation Patron/Propriétaire, la révocation de session, l'acte conservé et l'idempotence. La délégation, la relève nominative, `NO_ACTIVE_OWNER` et R03 sont prouvés dans `SMART_AO_C14_DELEGATIONS_RELEVE_DERNIER_PROPRIETAIRE_AUDIT_CADRAGE_v0.1.md` et `ContinuityGovernanceService`.

## Décision de tranche

La preuve C14 sépare **propriété organisationnelle** et `PATRON_ADMIN`, enregistre la suspension immédiate d’un propriétaire ou membre comme un acte append-only qui coupe les sessions, puis ferme la continuité minimale : relève nominative acceptée par le successeur, état `NO_ACTIVE_OWNER` et récupération R03 à double contrôle. Elle ne matérialise pas encore l’interface complète ADM-01 à ADM-10 ni l’orchestration automatique des affectations.

**Prochaine étape :** ouvrir C15 en auditant MFA, récupération et sessions sensibles après les nouvelles frontières de gouvernance.
