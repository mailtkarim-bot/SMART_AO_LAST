# SMART AO — EXP-07 : suspension, export, conservation et fermeture

**Statut :** suspension, fermeture, demande d'export et conservation implémentées

## Contrat minimal

Ces actes restent séparés de la commande, du P6, du P7 et du REX :

- `SUSPENDED` bloque le réemploi sans supprimer les faits ;
- `EXPORT_REQUESTED` décrit une intention Patron, jamais une transmission externe réussie ;
- `RETAINED` conserve une preuve selon sa classification et sa durée ;
- `CLOSED` ferme la tranche opérationnelle en conservant les références et les litiges.

Chaque acte porte le tenant, l'Affaire, l'auteur, la cause, l'horodatage, la source, la portée et les identifiants d'idempotence. Aucun acte n'efface ni ne réécrit un résultat antérieur.

## Garde-fous

- un état `UNKNOWN` ou un litige ouvert interdit `CLOSED` ;
- un export n'affirme pas qu'un destinataire externe l'a reçu ;
- une suspension est réversible par un acte explicite et audité ;
- la conservation respecte la classification et les règles de rétention du document source ;
- les Collaborateurs ne suspendent, n'exportent ni ne ferment une Affaire depuis cette surface.

## Preuve réalisée

`CaseDispositionRecord` et la migration `20260920_0083` conservent `SUSPENDED`, `RESUMED` et `CLOSED` comme faits append-only. La fermeture exige un P7 `COMPLETED`, refuse un P7 `UNKNOWN` ou `INTERRUPTED`, ainsi qu'une suspension active pour `OPEN_LITIGATION`. La reprise est elle-même un fait audité ; aucun résultat P7 n'est modifié. Les cinq tests PostgreSQL ciblés prouvent la suspension, la reprise, le refus litigieux, le refus `UNKNOWN`, le rejeu et la tête Alembic.

## Preuve d'export et de conservation

La migration `20260920_0084` ajoute deux registres séparés : `case_export_requests` pour l'intention Patron de préparer un export, et `case_retentions` pour la conservation interne d'une référence de preuve jusqu'à une date donnée. L'événement d'export porte explicitement `external_receipt: NOT_PERFORMED` ; il n'existe aucun statut de livraison ou de réception. La conservation porte une base explicite (`MARKET_RECORD`, `OPEN_LITIGATION` ou `INTERNAL_POLICY`) et une échéance, sans supprimer de preuve.

## Décision de tranche

Le cycle minimal d'archivage est maintenant couvert par des faits distincts, idempotents et Patron-only. La suite doit assembler les parcours de clôture, d'export et de conservation avec les refus de rôle avant le gel d'expérience EXP-07.

**Prochaine étape :** assembler la preuve verticale EXP-07, vérifier les refus Patron et préparer le gel d'expérience.
