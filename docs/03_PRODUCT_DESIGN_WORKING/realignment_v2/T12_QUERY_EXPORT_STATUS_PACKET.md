# T12 — Lecture Patron de l’état d’export

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Objectif

Permettre au Patron de relire les demandes d’export locales et leur état réel,
sans présumer qu’un fichier a été reçu par un système externe.

## Contrat

- lecture tenant-scoped et bornée ;
- états `REQUESTED`, `READY`, `UNKNOWN`, `REFUSED` conservés ;
- ordre par création décroissante ;
- aucune transition implicite vers `READY` ;
- historique append-only et absence de reçu explicitement visible ;
- aucun contenu de preuve, financier ou personnel réexposé.

## Preuves attendues

Projection API fermée, tests tenant/pagination/états, test C07 et gates
backend/frontend complètes.

