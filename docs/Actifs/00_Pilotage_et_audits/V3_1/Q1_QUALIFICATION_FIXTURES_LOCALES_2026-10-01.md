# Q1 — qualification des fixtures locales A1 → B1 → C1

**Date :** 1 octobre 2026
**État :** PARTIEL — la chaîne continue sur une même Affaire n’est pas démontrée
**Périmètre :** fixtures synthétiques déjà présentes dans le dépôt ; aucun DCE client ajouté, aucune comparaison concurrentielle exécutée, aucune ouverture publique.

**Historique :** ce diagnostic partiel du 1er octobre a été complété par la [qualification intégrée même-Affaire du 2 octobre](Q1_CHAINE_A1_B1_C1_INTEGREE_2026-10-02.md). Utiliser le rapport du 2 octobre pour l’état actuel de Q1.

## Verdict

Les preuves locales montrent que les composants A1, B1 et C1 savent conserver et relire leurs objets et preuves respectifs, et refusent certains passages lorsque la source ou l’applicabilité reste inconnue. Elles ne qualifient pas encore le scénario Q1 complet : les E2E A1 et B1/C1 créent des Affaires distinctes. Le test C1 utilise un snapshot B1 mais n’y attache pas la condition et la preuve A1 ; la continuité des mêmes identifiants source, impact et condition jusqu’à C1 reste donc **UNKNOWN / non prouvée**.

Q1 ne peut pas être clôturé ni servir à revendiquer une différence concurrentielle. Le prochain test doit créer la preuve A1, capturer ses liens dans B1 sur la même Affaire, puis rattacher un événement C1 à ce snapshot exact.

## Résultats reproductibles

Commande ciblée exécutée sur PostgreSQL temporaire `127.0.0.1:5433` :

```bash
SMART_AO_TEST_DATABASE_URL='postgresql+psycopg://smart_ao:smart_ao@127.0.0.1:5433/smart_ao_test' ./.venv/bin/pytest -q --tb=short backend/tests/db/test_a1_condition_contract_evidence.py backend/tests/db/test_case_handover_http_e2e.py
```

Résultat : **3/3 tests verts**, une dépréciation Starlette/httpx. Ils comprennent A1 source→impact→condition et deux scénarios B1/C1. Le test C1 vérifie également l’upgrade/downgrade de migration, l’idempotence, le refus de rôle, la lecture étrangère neutre et les trois registres append-only.

| Mesure sur les tests existants | Résultat observé | Limite |
|---|---|---|
| Refus explicitement liés à UNKNOWN | **2** : liaison d’une preuve A1 dont l’état est `UNKNOWN` (HTTP 422) ; action C1 avant revue d’applicabilité humaine (HTTP 422) | Ces refus sont observés dans des scénarios/fixtures séparés. |
| Autres refus A1 | révision de source DCE périmée (409), profil adopté manquant (422), rôle non autorisé (403), tenant étranger (404) | Le test prouve ces contrôles pour A1 uniquement. |
| Autres refus B1/C1 | Collaborateur non affecté ou profil Expert refusé (403), Collaborateur refusé sur C1 (403) ; lecture C1 par tenant étranger retourne une liste vide (200) | Aucun résultat de refus n’est interprété comme une preuve de continuité A1→C1. |
| Rejeu | impact A1, lien A1, passation B1, revue C1 et action C1 rejoués sans duplicata dans leurs tests respectifs | Le rejeu transversal depuis un même command_id n’est pas attendu ; les actes restent des intentions différentes. |
| Preuves relues | A1 expose l’observation DCE et le lien exact exigence/révision → impact/révision → profil adopté/hash → condition ; B1 relit le manifeste et le SHA-256 du document technique et vérifie le téléchargement ; C1 relit l’événement, ses références source/pièce, la version contractuelle choisie, la revue et les références de preuve de l’action | La présence de la preuve A1 dans le snapshot B1 du scénario C1 n’est pas démontrée. |

Commandes de vérification web :

```bash
npm --prefix web test -- --run src/features/decision/CaseContractChangePanel.test.tsx
npm --prefix web test -- --run
npm --prefix web run lint
npm --prefix web run build
```

Résultats : C1 ciblé **1/1**, suite web **296/296**, ESLint et build (TypeScript inclus) verts. Vite conserve son avertissement de chunk principal supérieur à 500 kB.

## Gates backend et écarts connus

Une collecte Pytest normale échoue avant exécution car deux tests distincts portent le nom `test_partner_offer_line_comparison.py`. `--import-mode=importlib` permet de collecter les **2 013 tests**. La première tentative dans le sandbox échoue à ouvrir le PostgreSQL local ; avec l’accès autorisé au service de test local, la suite complète termine à **2 008 passés / 5 échoués / 1 avertissement**.

Les cinq échecs rapportés :

- deux tests de `test_patron_decision_dossier.py` dont les mocks n’attendaient pas la nouvelle lecture des liens de preuve ; leurs mocks ont été adaptés ensuite, mais la suite ciblée correspondante reste à rejouer ;
- le contrat de tête runtime Alembic encore à `20260930_0122` alors que la branche locale contient `20261001_0125` ; la constante runtime a été avancée à `0125`, à confirmer par le test ciblé ;
- le garde d’architecture signale des imports ORM directs dans `decision/application/lifecycle.py`, `patron_action/application/case_handover.py` et `pricing/application/case_contract_change.py` ; ce point reste ouvert et aucun contournement par exception n’a été ajouté ;
- le test d’autorité du plan attendait l’ancien libellé Q1 ; le plan et son unique marqueur actif ont été alignés sur le trou de preuve réel, à confirmer par le test ops.

La suite complète n’a pas été rejouée après ces corrections. Le résultat **2 008/2 013** décrit donc le snapshot juste avant leur application, et ne constitue pas une gate verte pour le checkout actuel.

Après cette suite, les corrections minimales ont été contrôlées séparément : dossier Patron **4/4**, contrat ops + tête Alembic **5/5**, diff-check propre. Le test de frontière d’architecture a été rejoué et reste **1 échec** avec les trois violations listées ci-dessus. Cela ne remplace pas une nouvelle suite backend complète.

## Limites maintenues

- Fixtures déterministes de test seulement : pas de corpus client, de résultats utilisateurs, ni de comparaison aux concurrents.
- Aucun chiffre de précision métier ou avantage produit mesuré ; les nombres ci-dessus comptent des assertions exécutées dans les tests locaux.
- Pas de preuve navigateur CUA dans cette qualification.
- Pas de P3 induit, de calcul juridique, de coût/cash calculé, d’effet d’ordre de service ou d’ouverture publique.
- Aucun commit ni push.

## Reprise

Créer une recette E2E intégrée sur une Affaire : A1 confirmé et relié à la condition Patron → snapshot B1 qui expose les références A1 exactes → événement C1 lié à ce snapshot. Ajouter au moins une branche adversariale où le lien reste `UNKNOWN` et l’action est refusée ; vérifier les identifiants et preuves récupérés via les lectures HTTP. Corriger ensuite les trois violations de frontière architecture, rejouer les tests touchés, puis les gates complètes.
