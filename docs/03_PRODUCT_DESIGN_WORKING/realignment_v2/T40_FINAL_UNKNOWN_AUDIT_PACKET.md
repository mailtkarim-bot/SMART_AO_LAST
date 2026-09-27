# T40 — Audit consolidé final des inconnus

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Objectif

Fournir une vue finale de contrôle des inconnus, blocages et provenances avant
la prochaine revue globale, sans transformer cet audit en décision automatique.

## Contrat

- tous les états difficiles sont comptés et détaillés ;
- chaque entrée pointe vers sa provenance source ;
- tenant/export filtrés avant agrégation ;
- aucune mutation, suppression ou conclusion juridique ;
- `UNKNOWN` reste inconnu et `BLOCKED` reste bloqué ;
- lecture Patron uniquement.

## Preuves attendues

Projection d’audit, tests de comptage/tenant/provenance, C07, puis gates
complètes backend/frontend.

Implémentation initiale : `FinalUnknownAudit` compte uniquement les états
difficiles et conserve chaque entrée avec sa provenance.
