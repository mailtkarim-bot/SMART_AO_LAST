# C1/C3 — impact humain d’un changement sur un engagement A1

**Date :** 3 octobre 2026<br>
**Statut :** C3 implémenté et prouvé localement ; NO-GO public maintenu<br>
**Base auditée :** HEAD `9c2a982` + WIP C2/C3 locaux non commités<br>
**Autorités :** Product Freeze PF31-03/04/08, Master métier M31-05 et M3-030, Cahier technique CT31-03/04/07

## AS-IS vérifié

- C1 conserve l’événement sourcé et son snapshot B1. Il projette aussi l’applicabilité à la passation, le `delta_note` libre associé à cette revue, et les actions humaines.
- C2 ajoute `CaseContractChangeEngagementLinkRecord` : `LINKED` ou `UNKNOWN`, avec les références A1 exactes du snapshot B1 et un historique append-only.
- A1 conserve l’impact initial (`baseline_statement`, `deviation_statement`, `impact_statement`, statut et révisions) dans `ContractBaselineDeviationImpactRecord`. Une nouvelle conséquence postérieure à l’événement ne doit pas écraser ou réviser cet objet : ce serait réécrire l’état de référence avant offre.
- Le `delta_note` C1 n’est pas un impact C3 : il décrit un delta libre attaché à la revue d’applicabilité à la passation. Il ne porte ni l’identifiant C2, ni une source A1 précise, ni un axe d’impact fermé. Le réutiliser ferait perdre la causalité et mélangerait applicability, impact et action.
- Aucun aggregate, endpoint, DTO, projection ou formulaire dédié ne relie actuellement un impact post-C1 à un choix A1 précis en C2.
- Des modèles financiers voisins existent mais ne constituent pas ce contrat : la déclaration de prix partenaire est une donnée de reçu C09 ; `FinancialReportLineRecord` appartient au rapport financier et à ses totaux. C3 ne doit importer aucune ligne dans ce rapport ni détourner la comparaison partenaire.

## Lecture des exigences

M31-05 étape 3 demande une déclaration du delta de périmètre/coût/délai/cash/capacité, en conservant l’impact initial et en créant une révision. PF31-03/08 exige source, version, auteur/date, hypothèses, unité/devise si applicable, revue et état inconnu explicite. Le cahier technique CT31-03 prescrit les axes `COST`, `CASH`, `SCHEDULE`, `CAPACITY`, valeur connue ou inconnue, unités/devise et absence de calcul ou de couverture automatique. CT31-04 exige l’historique append-only et une projection qui explique `REVIEW_REQUIRED` quand une dépendance change.

## Décision de cadrage — plus petite tranche C3

Créer un acte C3 append-only **par événement C1, liaison C2, source A1 sélectionnée et axe d’impact**. Cela permet une première preuve verticale simple et garde chaque effet attaché à son origine sans tableau global ni graphe générique.

L’acte référence l’identifiant exact de la révision C2 `LINKED` et recopie l’identité source sélectionnée validée par le serveur. Il contient :

- axe fermé : `SCOPE`, `COST`, `CASH`, `SCHEDULE` ou `CAPACITY` ;
- référence source A1 exacte : condition, exigence/révision, impact/révision, profil/version/hash, égale à une entrée de `selected_sources_json` C2 ;
- état de l’impact : `DECLARED` ou `UNKNOWN` avec motif obligatoire pour l’inconnu ;
- description humaine, hypothèses, sources et preuve ;
- pour les axes mesurables, état de mesure distinct (`DECLARED` ou `UNKNOWN`) afin qu’un impact qualitatif connu puisse garder une quantité inconnue ; valeur telle que déclarée, unité et devise lorsqu’applicable. Coût/cash réutilisent le format décimal déclaré et la devise contrôlée du flux partenaire, sans réutiliser son reçu ; délai/capacité conservent la quantité décimale et l’unité déclarées ;
- acteur, date serveur, justification, révision attendue, `command_id` et `idempotency_key`.

`SCOPE` reste descriptif. `COST`/`CASH` conservent une valeur déclarée et une devise ; `SCHEDULE`/`CAPACITY` une quantité déclarée et son unité. Ces valeurs sont relues telles qu’entrées. Pas de conversion, somme, total couvert, marge, cashflow, durée juridique ou classement. Zéro explicitement saisi reste différent d’une valeur `UNKNOWN`.

Conditions serveur :

1. le Patron est autorisé sur la même Affaire et son tenant ; le traitement reste `FINANCIAL_PRIVATE` ;
2. C3 exige une révision C2 `LINKED` qui est toujours la liaison courante ; C2 `UNKNOWN` ne permet pas d’attribuer un impact à une source absente ;
3. la source choisie doit être l’une des références exactes dans cette révision C2, vérifiée côté serveur ; les identifiants envoyés par le navigateur ne font pas autorité ;
4. une révision C2 ultérieure conserve les anciens actes C3 mais les projette `REVIEW_REQUIRED` tant qu’un Patron ne les rattache pas à la nouvelle liaison ; aucune réécriture automatique ;
5. la revue d’applicabilité C1 reste séparée : un impact opérationnel peut être déclaré ou laissé `UNKNOWN` sans déclarer que l’instrument s’applique juridiquement ; ce statut est affiché à côté.

La première recette couvre une source A1 et un axe par acte ; les autres sources/axes sont obtenus par des actes séparés et visibles. L’extension à une saisie groupée ne fait pas partie de C3. L’intégration d’un impact dans P3, un calcul économique ou une décision contractuelle automatique restent différés.

## Implémentation C3 livrée

- Migration additive `20261003_0127_case_contract_change_impact_declarations.py` ; runtime Alembic aligné sur `20261003_0127`.
- `CaseContractChangeImpactDeclarationRecord` conserve un acte append-only par source C2 et axe. Ses FK désignent séparément C1 et C2 ; un trigger vérifie leur correspondance, le C2 courant `LINKED` et la source A1 exacte, sans ajouter de contrainte au schéma C2.
- Le handler Patron vérifie le C2 courant `LINKED` et l’appartenance exacte de la source A1 ; un trigger PostgreSQL applique aussi cette garde à l’insertion directe.
- La projection C1 expose l’historique et marque `REVIEW_REQUIRED` lorsque C2 est remplacé. Le formulaire Patron C07/C12 conserve impacts/mesures UNKNOWN et affiche les valeurs saisies sans calcul.
- Les enregistrements/snapshots A1/B1/C1/C2 ne sont pas modifiés ; seule la projection de lecture C1 ajoute l’historique C3. Les actes C3 restent append-only lors d’une nouvelle liaison C2.

## Points d’insertion, sans doublon

- Aggregate/commande append-only dans le bounded context `pricing` existant qui possède déjà C1/C2 ; aucune nouvelle couche « Contract Control » n’est créée.
- Persistance C3 distincte de `case_contract_change_applicabilities`, `case_contract_change_actions` et `contract_baseline_deviation_impacts`.
- FK tenant/Affaire vers l’événement C1 et FK tenant vers l’acte C2 ; le trigger valide la relation event/case et la source au moment de l’insertion.
- Écriture dans le routeur Patron C1 existant, lecture C3 dans la projection d’événement ; `CaseContractChangePanel` étendu en lecture/écriture Patron, avec historique et reprise idempotente.
- Axes/valeurs/unknown suivent des contrats validés existants : chaînes décimales déclaratives et devise contrôlée pour la valeur monétaire, quantité décimale déclarée et unité pour délai/capacité. Ne pas réutiliser la ligne d’un rapport financier calculé.

## Preuves locales exécutées

| Garantie | Preuve exécutée | Résultat |
|---|---|
| Parcours HTTP/PostgreSQL A1→B1→C1→C2→C3 | `test_case_handover_http_e2e.py` | 1/1 PASS |
| Zéro, UNKNOWN d’impact et UNKNOWN de mesure | zéro `0.00 EUR` restitué ; mesure inconnue séparée de l’impact déclaré | PASS |
| C2 UNKNOWN/obsolète et source forgée | API refuse ; trigger PostgreSQL refuse une source JSON non sélectionnée | PASS |
| Rejeu, révision et concurrence | rejeu sans doublon ; `expected_revision` obsolète refusé | PASS |
| Permission/tenant | Collaborateur refusé ; tenant étranger neutre en lecture et écriture refusée | PASS |
| Append-only/séparation | UPDATE/DELETE C3 refusés ; A1/B1/C1/C2 inchangés ; action C1, revue C1, C2 et C3 restent distincts | PASS |
| Obsolescence C2 | C2 révisé après C3 ; anciens actes conservés et projetés `REVIEW_REQUIRED` | PASS |
| Frontend C07/C12 | C3 source/axe, UNKNOWN, valeur et preuves testés dans `CaseContractChangePanel.test.tsx` | 3 tests du composant PASS |
| Backend complet PostgreSQL | `pytest --import-mode=importlib -q --tb=short` sur `smart_ao_v8_test` | 2013/2013 PASS, 17 min 16 s |
| Frontend complet, typecheck, lint et build | scripts `web` | 298/298 ; typecheck/lint/build PASS |
| Contrats architecture/schema/ops, qualité | quatre suites ciblées ; Ruff et mypy ciblés | 38/38, Ruff/mypy PASS |
| Alembic | fixture PostgreSQL du C3 E2E | upgrade head et downgrade base PASS |

## Non-objectifs et limites

Aucun calcul d’application juridique, pénalité, échéance, coût couvert, coût total, marge, cash certain ou P3. Aucun impact ne modifie l’issue A1, la condition, l’impact initial, le snapshot B1, l’événement C1 ou sa revue/action. Aucun montant de partenaire n’est assimilé à un coût d’entreprise. La preuve restera locale sur fixtures ; CUA, revue utilisateur, données client, validation juridique et ouverture publique demeurent non qualifiées.

**Tranche suivante cadrée :** implémenter C4 selon `C1_C4_ACTION_IMPACT_LIAISON_AUDIT_CADRAGE_v0.1.md`, sans mutation des actions C1 ou déclarations C3 ni déclenchement automatique.
