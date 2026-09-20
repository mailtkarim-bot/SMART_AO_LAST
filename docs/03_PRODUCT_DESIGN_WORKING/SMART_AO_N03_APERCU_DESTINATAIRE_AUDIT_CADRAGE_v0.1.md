# SMART AO — N03 : aperçu destinataire

**Statut :** audit et preuve verticale réalisés
**Objet :** prévisualisation d'un partage avant toute copie ou remise
**Date :** 20 septembre 2026

## Audit

C16 possédait le registre et la lecture interne d'un partage, mais aucune
frontière HTTP ne permettait au destinataire de voir exactement l'objet auquel
son jeton donne accès. Une route de téléchargement ou une notification
externe aurait élargi la preuve au-delà du contrat.

## Contrat minimal retenu

`POST /api/v1/shared-resources/preview` accepte le destinataire et le jeton
dans le corps de la requête afin de ne pas placer le secret dans l'URL. La
réponse contient uniquement l'identifiant du partage et de la ressource, le
type et l'empreinte SHA-256 de la version exacte, la finalité, la classification
et la fenêtre de validité.

Le jeton et l'identité du destinataire ne sont jamais renvoyés. Un jeton
inconnu, expiré ou révoqué produit la même réponse neutre
`404 SHARE_NOT_AVAILABLE`. La route ne télécharge aucune copie et ne prétend
pas constater une réception externe.

## Preuve

Route : [`shared_resources.py`](../../backend/app/interfaces/http/routes/shared_resources.py)
; service réutilisé : `ResourceSharingService`. Deux tests couvrent la réponse
exacte et la neutralité d'un destinataire non autorisé. La preuve C16 de la
lecture, de l'expiration et de la révocation reste inchangée.

Vérifications N03 : 7 tests backend ciblés passent, dont le contrat de schéma.
