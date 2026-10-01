# SMART AO — EXP-01 : contexte et rôles, preuve verticale minimale

**Statut :** PREUVE POSTGRESQL ACQUISE  
**Date :** 14 septembre 2026  
**Autorités :** cahier produit/métier OWNER v0.4, catalogue écrans/parcours OWNER v0.3, code et tests vivants.

## 1. Décision de conception

Un rôle métier, un périmètre d'Affaire et un droit sensible restent trois faits distincts. Le navigateur ne choisit aucun de ces faits : il reçoit uniquement la projection calculée par le serveur depuis la session active, l'adhésion active et les affectations actives.

La classe technique existante `TenantMembership.role` demeure la seule source d'autorisation :

| Présentation produit | Classe technique | Effet d'autorisation |
|---|---|---|
| Patron | `PATRON_ADMIN` | capacités Patron existantes ; aucune déduction depuis le statut de propriétaire |
| Responsable | `COLLABORATEUR` + profil opérationnel `RESPONSABLE` | aucun droit supplémentaire ; les données d'Affaire restent bornées par l'affectation |
| Expert | `COLLABORATEUR` + profil opérationnel `EXPERT` | aucun droit supplémentaire ; les données d'Affaire restent bornées par l'affectation |

Le profil opérationnel sert à présenter le parcours et les tâches. Il ne peut ni produire une capacité, ni étendre une affectation, ni rendre visible une donnée financière ou sensible. Un Responsable et un Expert sans affectation active n'accèdent à aucune donnée d'Affaire.

`PATRON_DELEGATE` est exclu de cette première preuve. Le code prévoit une liste fermée de capacités déléguables, mais le résolveur de contexte ne charge encore aucune délégation persistée. Le présenter comme Patron ou l'utiliser pour une porte métier avant cette persistance créerait un droit sans preuve.

## 2. Contexte actif et changement d'organisation

La session actuelle est déjà attachée à une seule identité, une seule adhésion et une seule organisation. Le changement d'organisation n'est donc pas une mutation locale de PAGE-003 : ce bouton ne peut confirmer qu'un affichage et ne modifie aucune autorisation.

La première preuve ne crée pas encore de bascule multi-organisation. Elle expose et utilise le contexte serveur de la session active. Une future bascule devra créer une nouvelle session pour une adhésion active choisie côté serveur, après authentification ou réauthentification adaptée ; elle ne pourra jamais accepter un `tenant_id`, un rôle ou des capacités comme autorité fournie par le navigateur.

## 3. Contrat de la première preuve à coder

Le plus petit ajout est un profil opérationnel serveur, limité à une adhésion `COLLABORATEUR`, et projeté dans le contexte déjà authentifié :

1. persister `RESPONSABLE` ou `EXPERT` sur l'adhésion ; les adhésions existantes peuvent rester sans profil jusqu'à leur attribution explicite ;
2. exposer le profil seulement avec le contexte courant authentifié ;
3. conserver le calcul actuel des capacités et des périmètres exactement inchangé ;
4. afficher Patron depuis `PATRON_ADMIN`, Responsable ou Expert depuis ce profil, sans contrôle client ;
5. refuser une valeur de profil incompatible, une adhésion inactive et toute tentative de créer ou modifier le profil via une API d'authentification publique.

Les attributions de profils et les délégations Patron restent hors de cette preuve : elles exigent le circuit approuvé, traçable, borné et révocable de R02.

## 4. Preuves attendues

- Patron : le contexte projeté affiche Patron et les contrôles Patron restent calculés côté serveur.
- Responsable et Expert : le même rôle technique `COLLABORATEUR` produit la présentation attendue, avec des capacités identiques et sans données d'Affaire hors affectation.
- Refus : un champ de rôle ou de profil envoyé par le navigateur ne modifie ni le contexte, ni les capacités, ni les affectations ; une session inactive ou une adhésion inactive est refusée.
- Régression : le parcours PAGE-003 peut confirmer le contexte affiché, mais ne peut jamais modifier l'autorité résolue.

## 5. Preuve exécutée

La migration `20260914_0070` stocke le profil opérationnel sous contrainte PostgreSQL. Le résolveur de contexte le projette depuis l'adhésion active et `/api/v1/auth/me` le retourne au navigateur. Le front l'affiche sans en déduire d'autorisation.

La preuve isolée couvre Patron sans profil, Responsable, Expert, l'absence d'effet d'un paramètre `operational_profile` envoyé au navigateur, les capacités et périmètres inchangés, et le refus PostgreSQL d'un profil Expert sur `PATRON_DELEGATE`.

## 6. Résultat de l'audit

Le code dispose de `PATRON_ADMIN`, `PATRON_DELEGATE` et `COLLABORATEUR`, de capacités calculées côté serveur et d'affectations d'Affaire. Il ne dispose ni de profils persistés Responsable/Expert, ni d'un endpoint de bascule d'organisation sûr. La séparation ci-dessus conserve ces garde-fous et donne une tranche verticale vérifiable sans inventer une nouvelle hiérarchie de droits.
