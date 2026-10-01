# SMART AO — EXP-07 : retour d'expérience et capitalisation

**Statut :** preuve REX append-only implémentée ; capitalisation et gel restent à faire

## Contrat minimal

Le retour d'expérience est un fait séparé de l'attribution, de la commande, du P6 et du P7. Il peut être attaché à un résultat P7 `COMPLETED`, `UNKNOWN` ou `INTERRUPTED`, mais il ne transforme jamais un état inconnu en succès.

Chaque entrée porte :

- l'Affaire et le lot concernés ;
- le P7 source et son état au moment de la saisie ;
- un motif fermé `KNOWN` ou `UNKNOWN` ;
- une observation courte, une conséquence et une action de suivi ;
- l'auteur Patron, la date, la source éventuelle et les réserves ;
- une portée de réemploi explicite : `CASE_ONLY`, `LOT_PATTERN` ou `ENTERPRISE_PATTERN`.

## Garde-fous

- aucune écriture ne réécrit un résultat, une commande, un P6 ou un P7 ;
- une capitalisation `ENTERPRISE_PATTERN` exige une source et une validation Patron distincte ;
- un motif `UNKNOWN` reste visible et non réemployable comme règle ;
- un Collaborateur ne publie pas une règle d'entreprise depuis une observation locale ;
- la rétention et l'export suivent les mêmes classifications et droits que la source.

## Décision de tranche

Le registre REX dédié est maintenant minimal : `RecordCaseRexCommand` crée un fait Patron-only lié à un P7, refuse une portée d'entreprise sans source/validation ou depuis un P7 non concluant, puis reste rejouable via le dispatcher. Aucun moteur de recommandation ni score de réemploi n'est nécessaire pour cette preuve.

## Preuve exécutée

La migration `20260919_0082` crée `case_rex`. La commande conserve lot, motif, portée, validation, observation, conséquence, suivi et source. Un REX `CASE_ONLY` peut documenter un P7 `UNKNOWN`; `ENTERPRISE_PATTERN` exige un P7 `COMPLETED`, une source et `APPROVED`. La route Patron est `/api/v1/patron/case-p7/{p7_result_id}/rex`.

Le test PostgreSQL `backend/tests/application/test_case_order_p6.py` vérifie la chaîne complète, le rejeu sans doublon et le refus d'une capitalisation d'entreprise depuis un P7 inconnu ; avec le contrôle de tête, 3 tests passent.

**Prochaine étape :** capitaliser les modèles et preuves avec validité, portée, applicabilité et droits de réemploi, puis préparer le gel EXP-07.
