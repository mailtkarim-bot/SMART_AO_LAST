# T24 — Relève opérationnelle de l’export local

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Objectif

Permettre à un responsable Patron de reprendre un export local à partir de sa
chronologie complète, sans modifier les actes techniques ou propriétaires.

## Contrat

- afficher demande, transitions, vérifications et acte propriétaire séparés ;
- afficher le dernier état confirmé et les inconnus restants ;
- conserver les références locales et hashes sans exposer le contenu exporté ;
- aucune mutation depuis la vue de relève ;
- aucune réception externe présumée ;
- tenant/Affaire/export filtrés côté serveur.

## Preuves attendues

Projection C07 dédiée, tests de rôle Patron, tenant et états difficiles,
frontend, puis gates complètes backend/frontend.

