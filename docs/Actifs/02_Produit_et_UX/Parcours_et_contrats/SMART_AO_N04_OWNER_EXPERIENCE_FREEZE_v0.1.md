# SMART AO — N04 Owner Experience Freeze v0.1

**État :** gel de la preuve minimale de relève nominative
**Date :** 20 septembre 2026

N04 gèle le parcours de passation comme un acte explicite : un demandeur
autorisé nomme un successeur actif et liste la portée ; le successeur accepte
séparément. Aucun pouvoir n'est implicite et l'historique reste append-only.

| Situation | Résultat |
|---|---|
| successeur absent, inactif ou identique au demandeur | `SUCCESSOR_NOT_ELIGIBLE` ou réponse neutre |
| acceptation par un autre membre | `HANDOVER_SUCCESSOR_REQUIRED` |
| reprise de la même intention | même état, `replayed=true`, aucun doublon |
| dernier Propriétaire suspendu | `NO_ACTIVE_OWNER`, aucune promotion implicite |

La route HTTP ne reçoit jamais un rôle, un tenant ou une capacité depuis le
navigateur. Les identifiants d'affectation sont une portée déclarée, pas une
preuve de transfert : chaque autorisation métier doit rester acceptée par son
service propre.

**Preuve exécutée :** 3 tests HTTP directs N04, 21 tests API web, compilation
Python, typecheck, build, Ruff et `git diff --check`. Les 23 tests PostgreSQL C14 et la tête Alembic `0088`
restent la preuve domaine de la demande et de l'acceptation.

**Prochaine étape :** ouvrir N05 sur la disponibilité terrain locale, en attente et confirmée.
