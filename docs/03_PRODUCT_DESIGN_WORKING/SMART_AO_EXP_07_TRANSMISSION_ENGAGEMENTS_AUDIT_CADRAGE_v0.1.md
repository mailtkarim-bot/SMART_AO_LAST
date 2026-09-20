# SMART AO — EXP-07 : transmission des engagements — audit et cadrage

**Statut :** résultat, transmission `WON`, commande, contrôle P6 et P7 implémentés · REX et gel restent à faire

## Constat du code vivant

Le flux `PreparationSnapshot` / `PreparationTransmission` transmet aujourd’hui une préparation technique non financière du Collaborateur au Patron. Il crée une action de revue Patron, mais ne porte ni résultat d’attribution, ni lot gagné, ni réserve d’exécution.

Les états `CaseRecord.commercial_stage = OUTCOME_KNOWN` et `AWARDED` existent, mais ils ne remplacent pas les commandes append-only qui relient une source, un lot, une preuve et des réserves. Les réutiliser directement comme preuve de transmission ferait perdre la distinction entre état courant et fait historique.

## Contrat minimal à ajouter dans la prochaine preuve

Un acte Patron-only append-only devra enregistrer, pour chaque lot :

- `lot_reference` vérifié contre le périmètre de l’Affaire ;
- `outcome` parmi `WON`, `LOST`, `UNKNOWN` ;
- `source_locator` obligatoire sauf pour `UNKNOWN`, qui doit porter un motif ;
- `reservations` structurées et non financières par défaut ;
- `recorded_at`, auteur, commande et identifiants d’idempotence.

`WON` seul pourra alimenter une transmission d’engagement. `LOST` et `UNKNOWN` resteront visibles mais ne produiront aucun engagement transmis. Une nouvelle déclaration append-only corrigera la précédente sans réécrire l’historique.

## Refus et invariants

- Collaborateur, autre tenant ou absence de capacité Patron : refus neutre ;
- lot hors périmètre : refus ;
- `WON` sans source : refus ;
- `UNKNOWN` sans motif : refus ;
- rejeu avec mêmes identifiants : même acte, pas de doublon ;
- aucune transmission d’engagement depuis `PreparationTransmission` seule ;
- attribution, commande, P6 et P7 restent des états distincts.

## Décision de cadrage

Le contrat `RecordCaseOutcome` et la table `case_outcomes` sont maintenant séparés du flux de préparation. La lecture Patron expose chaque déclaration et ses réserves. La transmission append-only `CaseOutcomeTransmissionRecord` et `TransmitWonOutcome` ne relaient que `WON`, recopient les réserves et rejouent le même fait sans doublon ; `LOST` et `UNKNOWN` sont refusés. Les Collaborateurs sont refusés. Le flux de préparation reste inchangé.

Les commandes, lectures et transmissions passent par la politique d’autorisation Patron existante. La tête Alembic attendue est maintenant `20260919_0081`. La preuve PostgreSQL commande → P6 → P7 passe avec deux scénarios ciblés ; la validation HTTP complète et le REX restent à exécuter avant gel EXP-07.

**Prochaine étape :** produire le retour d’expérience P7 avec motif connu ou inconnu, puis préparer le gel EXP-07.
