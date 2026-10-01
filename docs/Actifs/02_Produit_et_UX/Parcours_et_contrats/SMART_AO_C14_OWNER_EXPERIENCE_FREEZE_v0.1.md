# SMART AO — C14 Owner Experience Freeze v0.1

**Statut :** preuve verticale gelée pour revue propriétaire  
**Autorités :** cahier OWNER v0.4 §8 ; catalogue UX OWNER v0.3 C14/C15/N04 ; code et tests PostgreSQL du dépôt.

## Ce qui est désormais prouvé

La gouvernance distingue la propriété organisationnelle du rôle métier Patron. Un Propriétaire courant peut suspendre un membre, désigner ou transférer la propriété, accorder une délégation bornée et préparer une relève. Les actes restent append-only et les sessions d’un membre suspendu sont révoquées.

La relève est nominative : le demandeur liste les affectations concernées, le successeur actif accepte séparément et le rejeu de la même intention ne crée pas de nouvel acte. L’acceptation ne donne aucun rôle implicite et ne réécrit aucune décision passée.

Lorsque le dernier Propriétaire est suspendu, `authority_status()` renvoie `NO_ACTIVE_OWNER`. Aucune ancienne délégation, session de support ou action navigateur ne devient une autorité de remplacement. La récupération R03 exige deux memberships support distincts, une preuve d’autorité et une approbation persistées ; elle désigne ensuite un membre actif sans donner de pouvoir métier au support.

## États et refus obligatoires

| Situation | Résultat |
|---|---|
| Successeur inactif ou identique au demandeur | refus `SUCCESSOR_NOT_ELIGIBLE` |
| Acceptation par un autre membre | refus `HANDOVER_SUCCESSOR_REQUIRED` |
| Dernier Propriétaire suspendu | `NO_ACTIVE_OWNER`, aucune récupération automatique |
| R03 avec un seul support, preuve ou approbation manquante | refus explicite |
| Rejeu d’une demande de relève ou récupération | même résultat, sans doublon |

## Limites gelées

Cette preuve ne fournit pas encore les dix écrans ADM ni le transfert automatique des affectations, signatures, autorisations P5 ou pouvoirs financiers. Ces objets doivent rester explicitement réacceptés dans une tranche ultérieure. Le support n’est jamais un acteur métier.

## Preuve exécutée

- migrations `20260920_0085` à `20260920_0088` ;
- `MembershipGovernanceService` et `ContinuityGovernanceService` ;
- 23 tests PostgreSQL ciblés : propriété, suspension, délégation, relève, `NO_ACTIVE_OWNER`, R03 et idempotence ;
- tête Alembic `20260920_0088`, compilation Python et format Ruff validés.

**Prochaine étape :** ouvrir C15 en auditant MFA, récupération et sessions sensibles après les nouvelles frontières de gouvernance.
