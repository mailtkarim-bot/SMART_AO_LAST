# L09 — Passation du pli reconstruit et flux privés — 11 novembre 2026

Le [plan global](../00_Pilotage_et_audits/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md) est l’unique statut. Qualification locale synthétique ; général PARTIAL, aucun GO public.

## Périmètre

AS-IS : les parcours L08 et L09 existaient séparément. RISQUES : transfert d’un reçu ou d’un responsable V1, fuite des hypothèses financières ou assimilation de la passation à un ordre de service. INSERTION : callbacks optionnels dans les recettes existantes et une recette couplée ; aucun code applicatif, interface, droit, schéma ou porte modifié. TESTS : deux générations de pli/passation, sources et octets exacts, reçus et retries, refus et recherche des valeurs privées.

La recette crée les flux CASH synthétiques avant et après remplacement du rapport publié, reconstruit le pli avec une nouvelle revue et un nouveau P5, puis établit deux passations et reçus conducteur distincts. Les hash de manifeste, IDs de snapshot, source documentaire et octets du mémoire sont vérifiés. La V1 devient historique ; V2 conserve les manques de responsable et de preuve, et refuse une réception complète. Un ancien hash de vue et un ancien hash de pli sont refusés. Les champs financiers privés et références des rapports ne figurent pas dans la vue opérationnelle ; marqueurs et identifiants des flux privés, ainsi que le solde sentinelle, sont absents des vues, reçus et octets des documents conducteur exercés. Le Collaborateur est refusé sur le registre CASH et les contrôles/exports Patron.

## Résultats et limites

- Recette couplée : **1 réussite / 72,58 s** sur PostgreSQL jetable synthétique ; données et reçus restent locaux.
- Régressions des recettes L08 et L09 autonomes : **2 réussites / 162,84 s**, campagne recouvrant la recette couplée ; avertissement Starlette/httpx existant.
- Mypy application : 708 fichiers, aucun diagnostic ; Ruff sur les trois tests et `git diff --check` propres. Semgrep 1.183.0 : 79 règles sur trois fichiers, aucun finding ni erreur ; métriques désactivées. Le connecteur Basic Memory était indisponible ; le miroir a été synchronisé et relu par la CLI locale.
- Aucune nouvelle interface, aucun code de production, aucune migration, aucune dette de porte modifiée. Pas de TDD de comportement applicatif : le changement porte sur un raccordement de harnais de qualification.
- Le contrat est créé entre les deux phases : l’invalidation de l’ancien CASH dans cette recette peut donc aussi provenir du changement de contexte contractuel. L’effet isolé d’une publication financière est couvert séparément par L07 ; il n’est pas attribué au seul prix ici.
- Les vérifications de confidentialité portent sur les registres, identifiants et sentinelles synthétiques exercés, non sur une détection universelle de fuite en texte libre. Pas de navigateur, d’authentification réelle, d’effet externe, d’ordre de service, de dépôt ou de conformité présumée.

Preuves locales : sauvegarde WIP et journaux sous `~/.local/share/smartao-proofs/l09-private-cash-handover-20261111/` lorsque la livraison les a scellés ; voir `delivery.json` pour les résultats et limites effectivement vérifiés. Superpowers pour la méthode, ECC pour la vérification ; Graphify pour l’orientation et Basic Memory comme miroir. Context7, OpenDesign et Impeccable non requis : aucun nouveau contrat de bibliothèque ou changement visible ; Jev/Manus/GitHub non utilisés pour cette recette locale. DOCX non rouvert. A1 non admis/A2 HOLD/NO-GO public ; aucun candidat moteur activé, commit ou push.
