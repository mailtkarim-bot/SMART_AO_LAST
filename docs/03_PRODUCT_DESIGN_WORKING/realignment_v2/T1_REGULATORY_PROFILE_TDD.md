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
- commande/service d'écriture : rejeu identique retourne le reçu précédent, une Affaire d'un autre tenant est refusée `CASE_NOT_FOUND_OR_FORBIDDEN`, et la preuve PostgreSQL combinée passe **2 tests**.
- route Patron contrôlée `POST /api/v1/patron/cases/{case_id}/regulatory-profiles` : contrat fermé, réponse `201`, refus tenant neutre `404`, **2 tests API directs**.
- lecture Patron `GET /api/v1/patron/cases/{case_id}/regulatory-profiles` : projection fermée, version triée et état `UNKNOWN_APPLICABILITY` conservé, **1 test API direct**.

## Limites

Cette tranche persiste et écrit la structure tenant-scoped via `CommandDispatcher`, et expose une route Patron contrôlée sans registre de règles vivantes ni calcul juridique. Elle ne modifie aucune porte P0–P7.
