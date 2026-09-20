# SMART AO — C14 : délégations, relève et dernier Propriétaire compromis

**Statut :** preuve verticale C14 complète (délégation, relève, `NO_ACTIVE_OWNER`, R03) implémentée et testée  
**Autorités :** cahier OWNER v0.4, §8, OWN-01/02, R02/R03 et G13 ; catalogue UX OWNER v0.3, C14, C15, N04, AUTH-06 et G18.

## Question traitée

Après la séparation entre propriété organisationnelle et rôle Patron, cette tranche précise ce qui doit être prouvé pour :

1. déléguer une capacité nominative, bornée et révocable ;
2. organiser une relève sans transférer automatiquement les pouvoirs ni réécrire l'historique ;
3. maintenir un état honnête lorsque le dernier Propriétaire est compromis ou suspendu.

Le support SMART AO reste un opérateur de procédure et ne devient jamais Propriétaire, Patron, signataire ou détenteur d'une capacité client par défaut.

## Audit du code vivant

### Délégation

Le socle contient déjà une frontière utile mais incomplète :

- `ActorKind.PATRON_DELEGATE` existe ;
- `capabilities_for()` accepte un ensemble `delegated_capabilities` et l'intersecte avec une liste fermée ;
- la liste délégable contient notamment lecture Consultation/DCE, tâches, préparation, finalisation de décision, autorisation de soumission et export sensible ;
- aucune table, migration, commande ou route ne persiste le délégant, le délégataire, la porte P0–P7, le périmètre Case/lot, la durée, le plafond, la révocation, l'approbation ou la preuve de MFA ;
- le résolveur de contexte appelle actuellement `capabilities_for(actor_kind)` sans charger de délégation persistée. Un `PATRON_DELEGATE` réel reçoit donc zéro capacité par cette voie, ce qui est un refus sûr mais ne constitue pas encore une délégation utilisable ;
- les délégations ne peuvent pas être transmises par un navigateur : le rôle, les capacités et le périmètre doivent rester issus de données serveur.

### Relève

Le code possède des briques de réaffectation de Case :

- `CaseAssignmentRecord` porte l'état `ACTIVE`, `SUSPENDED`, `ENDED` ou `EXPIRED`, un périmètre d'actions et de classifications, une fenêtre temporelle et un auteur ;
- `CaseAssignmentChangeEventRecord` conserve les changements de périmètre et d'état avec révisions, motifs et acteur ;
- les services Patron savent créer, suspendre, réactiver, terminer et modifier une affectation ;
- aucune agrégation de relève ne relie encore l'ancien responsable, le successeur, les objets ouverts, les validations attendues, les inconnus, les pièces, la date de prise en charge et l'acceptation du successeur ;
- aucune règle ne transfère automatiquement une délégation, une autorisation P5, une signature ou un pouvoir financier lors d'une réaffectation.

### Dernier Propriétaire compromis

La propriété courante et la suspension sont maintenant persistées : `tenant_owners`, `tenant_owner_changes` et `membership_suspensions` permettent de conserver l'identité, de fermer une projection et de révoquer les sessions. En revanche :

- la méthode `authority_status()` expose explicitement `NO_ACTIVE_OWNER` lorsque le dernier Propriétaire est suspendu ; aucune récupération n'est déclenchée implicitement ;
- la procédure R03 persiste la preuve d'autorité organisationnelle, deux intervenants support distincts, l'approbation, la nouvelle désignation et la clôture de récupération ;
- aucune délégation future n'est invalidée par lecture d'un acte de suspension ou d'une fin de propriété ;
- le support ne possède pas de route de récupération et ne doit pas recevoir de capacité métier implicite.

## Contrat métier à retenir

| Objet | Règle minimale | État difficile |
|---|---|---|
| Délégation | Acte nominatif du propriétaire courant vers un membre actif ; capacités dans la liste fermée ; porte, périmètre et durée obligatoires | `PENDING_APPROVAL`, `ACTIVE`, `EXPIRED`, `REVOKED`, `REFUSED` |
| Délégation sensible | Approbation distincte et MFA récent selon la porte ; aucune auto-délégation ni sous-délégation | approbation absente ou conflit de périmètre = refus explicite |
| Suspension | Toute suspension du délégant, du délégataire ou de la propriété invalide l'usage futur ; l'acte passé reste lisible | session expirée ou délégation échue = accès refusé, sans succès présumé |
| Relève | Acte séparé qui nomme un successeur et liste les objets à reprendre ; le successeur accepte avant d'agir | éléments orphelins, refus du successeur ou périmètre incomplet |
| Dernier Propriétaire compromis | Suspendre immédiatement est permis ; les opérations réservées restent bloquées jusqu'à une nouvelle propriété prouvée | `NO_ACTIVE_OWNER`, aucune récupération automatique |
| Support | Peut enregistrer et faire avancer une procédure R03 approuvée ; ne reçoit aucun rôle client | preuve insuffisante, double contrôle absent ou réattribution non approuvée |

## Invariants de sécurité et de preuve

1. Une délégation est non transmissible, tenant-scopée, limitée à des capacités fermées, à une ou plusieurs portes explicitement listées, à un périmètre et à une échéance.
2. Le délégataire ne peut pas désigner, modifier, prolonger ou transmettre sa propre délégation.
3. Une révocation, une suspension de membership, une suspension de propriété ou l'expiration coupe l'usage futur sans supprimer l'acte ni les décisions prises avant sa fin.
4. Une relève ne réécrit aucune décision, signature, soumission ou preuve passée ; elle crée des affectations et des attentes nouvelles, acceptées par le successeur.
5. Aucun rôle `PATRON_ADMIN`, `PATRON_DELEGATE` ou capacité financière n'est écrit à partir d'un payload navigateur.
6. S'il n'existe aucun Propriétaire actif, les actions réservées renvoient un état explicite de blocage ; elles ne sont pas exécutées par le support ni par une délégation ancienne.
7. Une récupération R03 exige une preuve organisationnelle conservée, deux intervenants support distincts, une approbation, une nouvelle désignation nominative et un journal append-only.

## Plus petite preuve verticale retenue

La preuve ne construit pas encore l'interface complète ADM-01 à ADM-10. Elle doit :

1. persister une délégation nominative `ACTIVE` avec délégant propriétaire, délégataire membre actif, capacités fermées, porte, périmètre, expiration, motif et idempotence ;
2. charger cette délégation dans le contexte serveur du `PATRON_DELEGATE` et refuser toute capacité hors liste ;
3. refuser l'auto-délégation, la sous-délégation, la cible suspendue, le périmètre vide et l'expiration dépassée ;
4. révoquer l'usage futur lors d'une suspension du délégataire et conserver les deux actes ;
5. persister une relève nominative, son acceptation à usage unique et son périmètre d'affectations sans mutation implicite des droits ;
6. exposer `NO_ACTIVE_OWNER` après suspension du dernier Propriétaire ;
7. exécuter R03 uniquement avec deux acteurs support distincts, preuve d'autorité et approbation persistées.

## Preuve implémentée

La migration `20260920_0087`, `MembershipGovernanceService` et `AuthenticationContextResolver` couvrent maintenant cette tranche :

- `tenant_delegations` conserve une délégation nominative tenant-scopée avec capacités fermées, portes, Cases, fenêtre, motif et idempotence ;
- `tenant_delegation_events` conserve séparément les actes `GRANTED` et `REVOKED` ;
- seul un Propriétaire organisationnel courant peut accorder ou révoquer ; la cible doit être une membership active `PATRON_DELEGATE` ;
- le contexte serveur charge uniquement les délégations actives et non expirées, intersecte les capacités avec la liste fermée et expose les Cases autorisées ;
- l'autorisation refuse un Case hors périmètre délégué ; aucune capacité n'est lue depuis un payload navigateur ;
- l'auto-délégation, la sous-délégation, la cible suspendue, le périmètre vide, la fenêtre invalide et les capacités non délégables sont refusés ;
- la suspension du délégant ou du délégataire clôture les délégations futures et écrit les événements de révocation dans la même transaction.

La preuve C14 est maintenant complète pour la frontière gouvernance/continuité ; les interfaces ADM et l'orchestration des affectations restent hors périmètre.

## Preuve de relève et de récupération implémentée

Les migrations `20260920_0088`, `ContinuityGovernanceService` et les tests PostgreSQL couvrent la suite minimale :

- `tenant_handovers` conserve le demandeur, le successeur, les objets à reprendre, l'état et l'idempotence ; `tenant_handover_events` conserve la demande et l'acceptation séparément ;
- seul le Propriétaire courant peut demander la relève ; seul le successeur actif peut l'accepter ; l'acceptation ne modifie ni rôle ni décisions passées et son rejeu est idempotent ;
- `authority_status()` renvoie `NO_ACTIVE_OWNER` quand la projection courante ne comporte plus de Propriétaire dont le membership est actif ; aucune délégation ancienne n'est promue ;
- `tenant_recoveries` conserve preuve d'autorité, approbation, deux supports distincts, cible et clôture ; R03 désigne ensuite nominativement un membre actif et n'accorde aucun rôle métier au support ; le rejeu est idempotent.

## Décisions et limites

- Le registre de délégation sera append-only pour les actes de création, modification bornée, révocation et expiration ; une projection courante peut être dérivée, mais aucun acte historique ne sera réécrit.
- La propriété organisationnelle reste la condition d'approbation de la délégation sensible ; le rôle métier Patron ne suffit pas à lui seul.
- La relève ne sera pas implémentée par une mutation globale des affectations existantes : elle produira des actes de reprise et des affectations nouvelles, avec acceptation.
- Le support reste limité à l'acte R03 prouvé ; l'interface complète, les notifications et le transfert automatique d'affectations sont reportés.

**Prochaine étape :** ouvrir C15 en auditant MFA, récupération et sessions sensibles après les nouvelles frontières de gouvernance.
