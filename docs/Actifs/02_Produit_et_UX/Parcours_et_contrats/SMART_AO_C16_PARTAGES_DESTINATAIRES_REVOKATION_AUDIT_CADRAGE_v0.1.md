# SMART AO — C16 : partages, destinataires, durée et révocation

**Statut :** audit initial exécuté ; preuve verticale à construire  
**Autorités :** cahier OWNER v0.4 §38 et confidentialité ; catalogue UX OWNER v0.3, SHR-01/N03, ADM-06, ADM-10 et G24/G45/G47.

## Constat du code vivant

Le dépôt contient des téléchargements internes de documents et des exports Patron de paquets, mais aucun registre de partage externe générique. Aucune route active ne persiste ensemble l’objet partagé, le destinataire, la finalité, la durée, la version, la classification, la révocation ou la preuve de consultation.

Les briques réutilisables sont déjà présentes :

- contexte serveur tenant-scopé et garde MFA récente pour les opérations sensibles ;
- versions et empreintes de manifestes de soumission ;
- classifications de données et refus des ressources `SECURITY_RESTRICTED`/`FINANCIAL_PRIVATE` hors parcours dédié ;
- états append-only pour export demandé, conservation, suspension et fermeture ;
- téléchargement interne contrôlé par affectation et expiration de document.

Il ne faut pas créer de lien public permanent ni réutiliser un export comme preuve de partage. Le partage doit référencer une version exacte et rester révocable côté serveur.

## Contrat minimal retenu

1. Un partage nomme un objet/version, un destinataire, une finalité, une classification autorisée et une expiration obligatoire.
2. Le destinataire reçoit une invitation ou un jeton opaque à usage borné ; l’URL ne contient aucun contenu ni secret permanent.
3. La révocation est append-only et invalide immédiatement toute nouvelle consultation ; elle ne prétend pas effacer une copie déjà téléchargée.
4. Une nouvelle version de l’objet ne modifie pas silencieusement un partage existant : le partage reste lié à l’empreinte initiale.
5. Un partage sensible exige MFA récente, confirmation explicite et audit du créateur, de la finalité, de la date d’expiration et du résultat.
6. Un objet litigieux, suspendu, expiré ou supprimé est refusé avec un état neutre ; aucun succès de téléchargement n’est présumé après une réponse réseau inconnue.

## Plus petite preuve verticale

Créer un registre tenant-scopé `resource_shares` et ses événements append-only, puis prouver : création d’un partage sur une version exacte, lecture par destinataire autorisé avant expiration, refus après expiration ou révocation, rejeu idempotent et séparation entre demande de partage et téléchargement réel. La conservation de copies locales et les notifications externes restent hors de cette tranche.

**Prochaine étape :** implémenter le registre de partage borné et la lecture révocable sur une version exacte.
