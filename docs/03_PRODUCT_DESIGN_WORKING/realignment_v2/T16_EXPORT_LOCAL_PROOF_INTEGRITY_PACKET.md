# T16 — Intégrité de la preuve locale d’export

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Objectif

Garantir qu’un export marqué `READY` possède une preuve locale vérifiable,
sans prétendre qu’il a été reçu par un système externe.

## Contrat

- référence locale obligatoire pour `READY` ;
- hash ou identifiant de contenu conservé dans l’acte de transition ;
- preuve absente, illisible ou incohérente : état `UNKNOWN` ou `REFUSED` ;
- aucune transition rétroactive ;
- tenant/Affaire et export liés vérifiés côté serveur ;
- C07 affiche l’état de preuve sans exposer le contenu exporté.

## Preuves attendues

Contrat de preuve, tests PostgreSQL de cohérence/hash, API/C07 et gates
backend/frontend complètes.

