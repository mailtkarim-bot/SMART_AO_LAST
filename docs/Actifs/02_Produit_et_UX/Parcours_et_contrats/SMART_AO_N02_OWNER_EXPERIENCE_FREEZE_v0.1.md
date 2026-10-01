# SMART AO — N02 — OWNER EXPERIENCE FREEZE v0.1

**État :** preuve front gelée sur l'export Patron
**Date :** 20 septembre 2026

N02 devient un état stable et quitt-able dès qu'une opération peut avoir
réussi sans confirmation reçue. Sur l'export, l'identifiant du paquet et la
P5 restent visibles, le succès n'est pas présumé et le bouton devient
`Vérifier l’export`. Une erreur HTTP déterminée reste distincte d'une rupture
de communication.

Le backend ne prétend toujours pas avoir effectué le dépôt externe :
`external_submission: NOT_PERFORMED`. La preuve manuelle et son rapprochement
restent les seuls éléments permettant de parler de réception tierce.

La preuve comprend le test de rupture réseau dans
`web/src/features/submission/useSubmissionActions.test.tsx`, les tests
SubmissionPanel, le typecheck et ESLint. La suite front complète passe à 166
tests.
