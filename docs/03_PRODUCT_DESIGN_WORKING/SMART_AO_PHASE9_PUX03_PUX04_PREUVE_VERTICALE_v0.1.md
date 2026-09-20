# SMART AO — preuve verticale PUX-03 et PUX-04 v0.1

**Date :** 20 septembre 2026  
**Statut :** PREUVE VERTICALE — parcours DCE privé/manuelle et lecture partielle

## Décision métier

Une Affaire ne déduit jamais une Consultation ou une version DCE depuis son
identifiant. La liste des Affaires expose les références résolues par le
serveur. Si la Consultation manque, l'espace DCE refuse l'admission. Si une
version est admise, vérifiée et rattachée à la même Consultation, le rôle
autorisé peut l'attacher à l'Affaire par une commande idempotente.

Le rattachement met à jour l'Affaire, ferme l'ancien indicateur courant et
ajoute une ligne dans `case_dce_applicability_history`. Le document original
reste conservé par le staging ; l'inventaire et les états de traitement sont
lus séparément de la synthèse.

## Chaîne PUX-03

1. L'Affaire est ouverte avec sa source et ses inconnus.
2. `GET /api/v1/cases/assigned` renvoie `consultation_id` et
   `applicable_dce_version_id` calculés côté serveur.
3. Le panneau DCE résout la Consultation, sa révision, ses lots et ses
   tranches ; l'absence de Consultation bloque l'action.
4. Le flux manuel prépare une intention expirante, envoie un flux binaire
   contrôlé, puis enregistre une version DCE admise.
5. `POST /api/v1/cases/{case_id}/dce-applicability` vérifie le tenant, la
   Consultation commune, l'intégrité `VERIFIED` et le cycle `ADMITTED` avant
   le rattachement.

Les identifiants de Consultation, de stockage et de version ne sont jamais
fabriqués par le navigateur. Une réponse inconnue n'est pas transformée en
succès ; le rejeu repose sur les mêmes identifiants de commande.

## Chaîne PUX-04

Après rattachement, l'espace affiche la version DCE, sa fraîcheur,
l'inventaire par fichier (`GET /api/v1/dce-versions/{id}/documents`), puis la
lecture structurée de l'Affaire (`GET /api/v1/cases/{case_id}/dce-reading`).
Les états `RECEIVED`, `READ`, `REVIEW_REQUIRED`, `UNSUPPORTED`,
`LIMIT_REACHED`, `PROTECTED` et `UNREADABLE` restent distincts, avec leur
`issue_code` lorsqu'il existe. Les ancres de source restent visibles dans les
exigences ; la recherche sourcée n'est pas une décision automatique.

## Preuves exécutées

- `useDceOpening.test.tsx` et `DceOpeningPanel.test.tsx` : **13 tests** passent
  sur la séquence intention → upload → admission → rattachement et le refus
  d'une Affaire sans Consultation ;
- contrat, route, handler, compilation Python, import runtime et Ruff passent ;
- les preuves EXP-03 déjà consignées couvrent staging/upload, admission,
  inventaire, extraction native, lecture partielle et états d'exception ;
- la relance PostgreSQL de ces suites n'a pas été déclarée verte dans cette
  passe : le conteneur répondait `connection is bad` pendant les migrations.

## Limites explicites

Cette preuve ferme le parcours privé/manuelle. Elle ne prétend pas avoir
réalisé un échange externe acheteur, une notification partenaire ou une
qualification Golden réelle.
