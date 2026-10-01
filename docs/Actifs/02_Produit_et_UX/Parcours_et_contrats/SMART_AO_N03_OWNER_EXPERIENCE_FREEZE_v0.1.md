# SMART AO — N03 — OWNER EXPERIENCE FREEZE v0.1

**État :** aperçu destinataire gelé côté HTTP
**Date :** 20 septembre 2026

Le destinataire voit l'objet exact partagé, sa finalité, sa classification, son
empreinte de version et sa fenêtre de validité. Le secret d'accès et
l'identifiant nominatif ne sont pas renvoyés. Un partage indisponible est
indistinguable d'un jeton inexistant.

La route ne fait aucune copie et ne confirme aucune réception tierce. La
révocation ou l'expiration reste effective côté serveur, car la prévisualisation
réutilise la lecture bornée de C16.

La preuve comprend les deux tests de route N03, les tests PostgreSQL C16/N01 et
le contrôle de tête Alembic.
