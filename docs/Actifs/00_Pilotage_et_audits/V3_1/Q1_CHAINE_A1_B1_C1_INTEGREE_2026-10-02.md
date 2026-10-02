# Q1 — recette intégrée A1 → B1 → C1

**Date :** 2 octobre 2026
**Verdict :** recette locale même-Affaire réussie ; validation marché et ouverture publique restent absentes.
**Autorité :** Product Freeze et cahiers V3.1 actifs. Cette pièce mesure le checkout local seulement.

## Ce qui a été rejoué

Le test `backend/tests/db/test_case_handover_http_e2e.py::test_http_c1_keeps_unknown_until_patron_links_change_to_handover_and_records_action` utilise les fixtures synthétiques déjà autorisées et conserve le même `case_id` pendant tout le scénario :

1. A1 confirme la source DCE existante, publie/adopte un profil versionné, crée via API l’impact baseline et sa décision `CONDITIONAL_GO` avec une condition `OPEN`, puis relie exactement source, impact, profil et condition.
2. Le lien d’une seconde preuve A1 `UNKNOWN` est refusé en HTTP 422. Le snapshot B1, créé après l’attribution `WON` sur le paquet P5 autorisé exact, restitue les IDs et révisions de l’exigence, de l’impact et du profil/hash utilisés par la condition.
3. Un événement de changement C1 est créé via HTTP contre le snapshot B1 exact. Avant revue Patron, l’applicabilité reste `UNKNOWN` et l’action est refusée en HTTP 422. Après choix humain de la version contractuelle exacte, le Patron enregistre le delta déclaré puis l’action et sa preuve. L’événement référence le même snapshot B1.

Le test rejoue les commandes A1, B1 et C1 avec les mêmes clés. Les reçus confirment l’idempotence. En fin de parcours, l’issue demeure `CONDITIONAL_GO`, la condition reste `OPEN` et la preuve A1 reste `HUMAN_REVIEW_REQUIRED` ; aucun effet financier, P3 induit, ordre de service ou conclusion juridique n’est produit. Le rôle Collaborateur est refusé et la lecture d’un autre tenant reste neutre.

## Défaut d’intégration corrigé

`DecisionRecord.selected_final_context_id` était renseigné à la finalisation, mais `DecisionContextRecord.is_selected_final` restait faux. Le dossier Patron et la passation B1 recherchaient l’indicateur contextuel et perdaient alors le contexte A1, même si le lien de condition existait. Les lectures utilisent maintenant la FK racine vers le contexte final exact. Le registre de contexte reste append-only ; le correctif ne modifie pas l’historique.

Les violations de frontière architecture ont été corrigées : le handler de liaison A1 et les handlers transactionnels B1/C1 vivent dans des modules `*_handler.py`; les lectures B1 et C1 passent par des ports de l’application et des lecteurs SQLAlchemy sous `infrastructure/`. Les filtres tenant/Affaire restent appliqués dans ces lecteurs avant projection.

## Vérifications

Commande E2E finale ciblée :

```bash
SMART_AO_TEST_DATABASE_URL='postgresql+psycopg://smart_ao:smart_ao@127.0.0.1:5433/smart_ao_test' ./.venv/bin/pytest --import-mode=importlib -q --tb=short backend/tests/db/test_a1_condition_contract_evidence.py backend/tests/db/test_case_handover_http_e2e.py backend/tests/architecture/test_application_infrastructure_boundary.py
```

Résultat après renforcement des rejeux : **5/5 passés**, une dépréciation Starlette/httpx. Les tests ciblés étendus au dossier Patron, head Alembic et contrat ops ont également passé **14/14** avant le dernier renforcement ; les contrats ops + head ont passé **32/32** après mise à jour du runbook.

Gates complètes exécutées sur le checkout local :

```bash
SMART_AO_TEST_DATABASE_URL='postgresql+psycopg://smart_ao:smart_ao@127.0.0.1:5433/smart_ao_test' ./.venv/bin/pytest --import-mode=importlib -q --tb=short
npm --prefix web test -- --run
npm --prefix web run lint
npm --prefix web run build
```

Le backend a passé **2013/2013** (18 min 28, une dépréciation Starlette/httpx) après les corrections de production et d’architecture ; le test C1 intégré a ensuite été renforcé et rejoué dans les 5 tests ciblés ci-dessus. Le frontend a passé **296/296** lors du rejeu isolé, ESLint et build/TypeScript sont verts. Un test PUX-19 a échoué dans un premier lancement concurrent des gates, puis a passé seul ; cette instabilité ponctuelle est conservée comme signal, sans échec reproductible.

Contrôles ciblés : `ruff check` sur tous les fichiers Python modifiés, mypy sur 11 modules d’application/infra, import de `app.bootstrap.application`, test architecture **2/2** et `git diff --check` verts. Le `ruff check .` global échoue sur **327 constats** de l’arbre complet, dont 190 sous `backend/app` et `backend/tests`; les fichiers modifiés dans cette tranche sont propres au contrôle ciblé. Aucun nettoyage global n’a été entrepris.

## Limites

- Fixtures synthétiques de test uniquement : aucun DCE client, entretien métier ou benchmark concurrentiel ajouté.
- Les assertions prouvent une continuité technique dans le modèle local ; elles ne mesurent ni adoption, ni précision métier en exploitation, ni supériorité face à un concurrent.
- Pas de CUA/navigateur, VPS ou préproduction réelle. PostgreSQL de qualification était éphémère, sans volume persistant, et a été arrêté.
- NO-GO public maintenu. Aucun commit ni push.
- Basic Memory n’était pas disponible comme outil MCP dans cette session ; la documentation active porte le checkpoint.

## Reprise de plan

Q1 est clos pour cette qualification locale. Le [plan global](../SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md) ouvre E1 : cartographier les exigences V3.1 restantes contre le code et ses preuves, puis choisir la prochaine verticale à partir du gap réel. Le [rapport du 1er octobre](Q1_QUALIFICATION_FIXTURES_LOCALES_2026-10-01.md) reste disponible comme constat historique pré-intégration.
