# L11 — Requalification humaine après invalidation — 02/11/2026

Qualification locale synthétique. Le plan global reste seul statut. L11 général PARTIAL.

## AS-IS, risque et insertion

La clôture refuse déjà les comparaisons invalidées et exige un hash de dossier courant et une confirmation humaine. Le lien direct réserve→réception ne passait cependant pas par ce refus. Une nouvelle réserve pouvait donc reprendre une réception REVIEW_REQUIRED. Le correctif minimal est dans `validate_closure_review`, partagé par les commandes natives de clôture. Aucun nouveau modèle, schéma, endpoint, écran ou mécanisme de requalification concurrent.

La requalification contractuelle historique (migration 0113) reste distincte : ces tests qualifient de nouvelles déclarations de clôture, pas une promotion des anciens actes ni une décision de validité juridique.

## Comportements prouvés

- Réception d'origine absente ou invalidée : nouvelle réserve refusée avec l'erreur existante CLOSURE_COMPARISON_SOURCE_CHANGED_OR_FORBIDDEN.
- Nouvelle réception sourcée V2, nouveaux identifiants et revue sur le hash courant : nouvelle réserve possible avec nouveau consentement explicite.
- Les anciennes revues et leur consentement restent inchangés. La réserve historique COMPLETED invalidée reste ouverte dans la projection ; la nouvelle réserve ne récupère pas sa levée. Aucun acquittement automatique de sortie.
- Confirmation false et hash périmé refusés. UNKNOWN n'est pas converti en preuve, même si une déclaration humaine est enregistrée.

## Fichiers

- `backend/app/modules/pricing/application/case_closure_handler.py` : contrôle partagé de l'origine réception avant acceptation de la revue.
- `backend/tests/application/test_closure_requalification.py` : origine invalide/absente/courante/inconnue, consentement et conflit, historique intact.
- `backend/tests/db/test_operational_change_workflow.py` : extension du parcours existant après révision de passation, refus du lien invalidé, nouvelles déclarations V2 et réserves anciennes/nouvelles encore ouvertes.

## Preuves et limites

Deux rouges attendus observés (absence de refus pour origine absente/invalidée), puis correction minimale. Campagne SQL/application : 34 tests passent en 57,36 s avec avertissement Starlette/httpx existant. Après ajout du test consentement/conflit : 13 tests unitaires passent en 1,18 s. L'assertion supplémentaire de source a d'abord échoué par mauvais nom de champ de test (`source_refs` au lieu de `source_refs_json`), corrigé sans changement produit ; rejeu final : 1 passe, 16 désélectionnés en 16,80 s (`sql-replay.log`). Base dédiée après teardown : zéro table métier et zéro ligne Alembic.

Mypy du handler : 1 source sans diagnostic ; Ruff ciblé et diff whitespace vérifiés. Semgrep 1.183.0, 79 règles, 3 fichiers, zéro finding et zéro erreur (scan final après les tests). Reçus sous `/home/noor/.local/share/smartao-proofs/l11-human-requalification-20261102/`.

Pas de relance des longues suites globales, de la chaîne intégrale DCE/DOCX ni de preuve navigateur pour cette modification backend. Aucun changement UI : OpenDesign/Impeccable non applicables. Graphify consulté ; lectures ciblées suffisantes sans navigation sémantique Serena. Aucun appel de bibliothèque nouveau : Context7 non nécessaire. Aucun Jev, Manus ou agent externe.

Méthode : cadrage borné Superpowers brainstorming, TDD rouge/vert, vérification avant conclusion ; ECC verification-loop et revue sécurité ciblée. Sources déclarées synthétiques : ni authenticité des pièces, ni signature réelle, ni conformité, ni levée juridique déduite. Portes, permissions natives et historique conservés ; aucun dépôt ou effet externe, activation, commit ou push.
