# L11 — Parcours intégré et décision de clôture locale — 02/11/2026

Le plan global est la seule autorité de statut. Qualification exclusivement locale et synthétique ; aucun effet externe ni conformité présumée.

## Cadrage et plan minimal

AS-IS : les recettes L08→L10 produisent le pli rectifié et la passation V2 exacte ; L11 enregistre réception, réserve et faits de paiement. La requalification humaine et l’invalidation ont leurs tests séparés.

RISQUES : accord ou levée hérités, source invalidée réutilisée, nouvelle intention confondue avec retry, sortie assimilée à une conformité ou un paiement acquis.

INSERTION : étendre seulement `backend/tests/db/test_l11_v2_closure.py`, en réutilisant les routes, commandes et projections de clôture. Aucun nouveau modèle, endpoint, écran, migration ou dépendance.

PLAN : éprouver la chaîne native Markdown, renforcer les assertions après revue indépendante, lancer les régressions ciblées et contrôles, expliciter les reports avant de statuer dans le plan. La tranche DOCX close n’est pas rouverte.

PREUVES ATTENDUES : sources et identifiants cohérents sur la même Affaire, ancien état puis invalidation, nouvelles déclarations consenties, refus de rôle/vue périmée/consentement absent, sortie refusée sans acquittement puis acte déclaré avec manques encore ouverts, faits financiers et historique inchangés.

## Portée de l’invalidation

L’entrée DCE rectifiée, la production du pli, les nouvelles revues/P5 et la passation V2 passent par la recette native existante. Le changement supplémentaire de passation qui déclenche la relecture de clôture est injecté dans la fixture SQL par une nouvelle révision de snapshot. Cette partie démontre la réaction au remplacement de source ; elle ne démontre pas une nouvelle publication P7 par le parcours public.

La nouvelle réception et la nouvelle réserve sont des déclarations humaines indépendantes avec sources synthétiques et consentements frais. Elles ne réhabilitent pas l’ancienne comparaison vers une action invalidée. Les manques de responsable/preuve attendue restent visibles et l’ancienne réserve reste à revoir.

## Reports explicites

- Authenticité, signatures, validité des pièces, dépôt, banque et réception externes : non qualifiés.
- Levée juridique des réserves, DGD, solde certain, délais/règles/sanctions : reports PF31-09/CT31-07 ; aucune conclusion automatique.
- Relecture binaire exhaustive des sources d’action et nouvelle publication P7 après l’invalidation injectée : non démontrées par cette recette.
- Variante DOCX et longues suites globales : preuves antérieures datées, pas relancées ni attribuées à cette campagne.
- Réemploi du REX vers une seconde Affaire : recette native dédiée existante ; résultat courant à distinguer de la continuité intégrée.

## Outils et méthode

Superpowers using-superpowers, brainstorming borné, writing-plans, requesting-code-review et verification-before-completion ; ECC verification-loop et revue sécurité. Le changement est une qualification de comportements existants : aucun code de production modifié, donc pas de rouge produit artificiel. Graphify consulté avant exploration. Basic Memory reste miroir du plan. Pas de nouvelle API de bibliothèque : Context7 non requis ; navigation ciblée sans Serena/Jev/Manus. Aucun changement UI : OpenDesign/Impeccable non applicables. Chrome DevTools et Playwright absents du catalogue courant des outils ; aucun nouveau résultat navigateur prétendu.

## Revue et incidents de qualification

Revue read-only indépendante : identités distinctes pour les intentions modifiées, préétat explicite de la réserve CURRENT puis REVIEW_REQUIRED, comparaison exacte des reçus hors marqueur replayed, contenu exact du consentement final et absence de mutation des lignes actes/obligations/faits ajoutés. Contre-revue : aucun défaut bloquant identifié ; ce contrôle statique ne vaut pas exécution DB ni accord humain.

La première recette a exécuté la clôture mais échoué sur le compteur amont de snapshots (troisième snapshot synthétique ajouté à une recette qui en attend deux). Le compteur amont est conservé : la qualification de clôture est appelée après les assertions amont. Un rejeu intermédiaire a été interrompu volontairement après découverte de la fermeture du client HTTP par la recette L08 ; il ne constitue aucune preuve. Le client est recréé sur la même application locale, avec les mêmes services et headers, et fermé par contexte après qualification. Aucun code produit corrigé pour ces incidents de harnais.

La stabilité persistée après replay et GET est vérifiée pour actes, obligations et faits uniquement ; cycles, transitions, événements et outbox sont hors de cette assertion. Aucun résultat de concurrence générale ne doit en être déduit.

## Résultats et décision

Recette intégrée Markdown finale : **1 passe, 1 variante DOCX désélectionnée, 287,48 s, exit 0** (`native-corrected.log`). Sources de la recette gelées par SHA-256 et relues après exécution ; dossiers avant/invalidation/requalification/final et filiation enregistrés dans `native-corrected/markdown/`.

Sur une Affaire unique : deux réserves finales ouvertes, ancienne revue conservée, nouvelle source et nouveau consentement exacts, sortie sans acquittement refusée puis nouvel acte avec acquittement exact. Le replay conserve les reçus et les lignes métier contrôlées. Après lecture finale, ces lignes restent inchangées. Paiement attendu 100000 et encaissement déclaré 60000 : écart −40000, solde UNKNOWN. Effet juridique et reçu externe UNKNOWN ; complétude REVIEW_REQUIRED.

Contrôles indépendants : **13 tests unitaires** passent en 1,09 s, **7 tests Web** passent (fichier CaseClosurePanel, durée totale 3,65 s), mypy applicatif **703 sources sans diagnostic**, mypy ciblé recette 1 source sans diagnostic, Ruff et diff whitespace ciblés. Les tests Web sont des tests de composant ; aucun E2E navigateur nouveau.

Régressions SQL/application : **35 passent en 70,08 s, exit 0**, dont permissions/MFA/tenant, idempotence/concurrence native de paiement, invalidation/réserve/sortie et REX/réemploi dédiés. Ces tests séparés ne sont pas une seconde chaîne intégrée. Avertissement Starlette/httpx existant conservé. Semgrep 1.183.0 après les tests : 1 fichier modifié, 0 finding et 0 erreur ; règles p/security-audit, métriques désactivées, aucune remontée de résultats.

**Décision : campagne locale L11 close avec reports.** Ce périmètre est un parcours synthétique de déclarations et de revue, pas une clôture contractuelle réelle. L11 général reste PARTIAL ; aucune activation, admission, porte, conformité, dépôt, paiement ni GO public ne sont accordés.

Preuves privées : `/home/noor/.local/share/smartao-proofs/l11-integrated-closure-20261102/`. Aucun commit/push, checkout secondaire ou modification du code applicatif/UI/schéma.
