# T20 — Revue propriétaire de la vérification d’export

**Statut :** prêt pour revue locale — NO-GO public maintenu

## Objet

Faire vérifier par le Patron que le produit distingue correctement intégrité
locale du fichier et réception externe.

## Décision attendue

- `MATCH` signifie uniquement que le contenu local correspond au hash attendu ;
- `MISMATCH` signifie que la preuve locale ne correspond pas ;
- `UNAVAILABLE` signifie que la vérification ne peut pas être conclue ;
- aucun de ces états ne prouve une réception ou acceptation externe ;
- C07 reste en lecture seule.

## Preuves disponibles

Contrat domaine, persistence tenant-scoped, hash SHA-256, panneau C07,
frontend 191 tests et backend 1 781 tests verts.

