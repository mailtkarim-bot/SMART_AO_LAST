# T1 — Contrat pur `RegulatoryProfile`

**24 septembre 2026 · première tranche v2 après promotion propriétaire**

## User journey

En tant que système, je veux conserver un profil d'applicabilité réglementaire sourcé et versionné pour une Affaire, afin qu'une règle future, expirée ou incertaine reste dans son état réel sans devenir une conclusion juridique automatique.

## RED / GREEN

- RED : `backend/tests/domain/test_regulatory_profile.py` ne pouvait pas importer le contrat absent (`ModuleNotFoundError`).
- GREEN : `backend/app/modules/case/domain/regulatory_profile.py` ajoute le contrat pur, sans FastAPI, ORM, HTTP ou fournisseur externe.
- Checkpoint RED : commit local `667902e`.
- Checkpoint GREEN : commit local `754b530`.

## Garanties

- statut fermé : `ACTIVE`, `FUTURE`, `EXPIRED`, `UNKNOWN_APPLICABILITY`, `REVIEW_REQUIRED` ;
- version strictement positive ;
- faits non vides et références de source non vides ;
- profil `FUTURE` exige une date d'effet ;
- profil `EXPIRED` exige une date de fin ;
- intervalle de dates cohérent ;
- aucun calcul de droit, aucune règle juridique et aucune conclusion d'applicabilité n'est inventée.

## Vérification

- `pytest backend/tests/domain/test_regulatory_profile.py` : **4 passés** ;
- Ruff et format ciblés : **verts** ;
- mypy ciblé : **vert** ;
- couverture ciblée : **91 %**.
- migration `20260924_0091` rejouée sur PostgreSQL Docker éphémère : **1 test de structure passé** ; tête Alembic et downgrade du fixture vérifiés par le harness DB.
- contrat pur + migration : **5 tests passés** dans le rejeu combiné.

## Limites

Cette tranche persiste la structure tenant-scoped mais ne contient pas encore de commande/service/API d'écriture, de registre de règles vivantes ou de calcul juridique. Elle ne modifie aucune porte P0–P7. La prochaine tranche ajoute l'écriture applicative avec idempotence et refus tenant.
