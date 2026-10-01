# SMART AO — N04 : relève nominative — audit et preuve v0.1

**État :** preuve verticale minimale implémentée
**Date :** 20 septembre 2026

## Contrat retenu

Une relève désigne explicitement un successeur actif et une liste d'objets à
reprendre. Le demandeur et le successeur sont résolus depuis la session
serveur ; aucun rôle, pouvoir financier, signature, autorisation P5 ou
délégation n'est transféré automatiquement.

Les deux actes restent séparés : la demande est `REQUESTED`, puis le
successeur accepte nominativement et l'état devient `ACCEPTED`. Le rejeu de la
même intention conserve le même résultat sans nouvel enregistrement.

## Surface HTTP minimale

- `POST /api/v1/continuity/handovers` demande la relève avec le successeur,
  les identifiants d'affectations, un motif et une clé d'idempotence ;
- `POST /api/v1/continuity/handovers/{handover_id}/acceptance` permet au seul
  successeur de prendre en charge la relève ;
- l'identité, le tenant et les droits viennent du Bearer résolu côté serveur ;
- une cible absente reste une réponse neutre `404 NOT_FOUND_OR_FORBIDDEN` ;
  une cible inactive, une portée vide ou un motif vide sont refusés.

La réponse contient seulement l'identifiant de l'acte, son état et le marqueur
de rejeu. Elle ne fabrique aucune affectation et ne réécrit aucun historique.

## Preuve

`ContinuityGovernanceService` conserve `tenant_handovers` et
`tenant_handover_events`. Les tests C14 prouvent la demande, l'acceptation par
le bon successeur, le refus implicite des autres acteurs, `NO_ACTIVE_OWNER`,
R03 et l'idempotence. Les tests HTTP N04 vérifient la résolution serveur de
l'acteur, les réponses de création et la neutralité d'un objet absent. Le
client web expose aussi les deux commandes avec identifiants idempotents ; 21
tests API web, le typecheck et le build passent.

La connexion PostgreSQL de validation n'était pas disponible lors de cette
exécution (`127.0.0.1:5433`) ; les tests HTTP directs, Ruff, compilation et
`git diff --check` passent. La preuve PostgreSQL C14 reste la référence déjà
exécutée lorsque la base est disponible.

## Limites gelées

La projection détaillée des tâches, inconnus, validations et échéances reste
une tranche ultérieure. La relève ne vaut pas validation métier et ne déclenche
aucune notification ou transmission externe.
