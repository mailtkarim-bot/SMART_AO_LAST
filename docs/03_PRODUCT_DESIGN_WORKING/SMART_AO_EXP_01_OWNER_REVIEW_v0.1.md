# SMART AO — EXP-01 : dossier de revue propriétaire

**Statut :** REVIEWED — arbitrages approuvés et promus dans l’`OWNER EXPERIENCE FREEZE`  
**Date :** 14 septembre 2026  
**Périmètre :** PAGE-001 → PAGE-007, invitation, récupération, contexte/rôles et reprises minimales  
**Autorités :** cahier Produit/Métier OWNER v0.4, catalogue Écrans/Parcours OWNER v0.3, code et tests vivants.

## 1. Objet de la revue

Ce dossier présente la preuve exécutable d'EXP-01 et les arbitrages approuvés avant le `OWNER EXPERIENCE FREEZE`. Il ne remplace pas le cahier propriétaire ; le gel associé porte les décisions retenues.

## 2. Verdict proposé

**FEASIBILITY PROVEN et arbitrages approuvés par le propriétaire.**

Le prototype permet à un Patron authentifié de franchir la MFA, de confirmer son contexte, de créer une première Affaire sans doublon et d'atteindre un Accueil composé. Il protège aussi les cas d'interruption : aucune réponse perdue n'est transformée en succès, aucune session expirée ne laisse de projection métier visible et un changement d'acteur, de tenant ou de rôle ne réutilise pas l'ancien état.

## 3. Preuves exécutées

| Domaine | Comportement démontré | Évidence |
|---|---|---|
| Accès | absence de session → connexion uniquement ; session `PASSWORD` → MFA uniquement | `web/src/app/App.test.tsx`, garde `STEP_UP_REQUIRED` |
| Contexte | entreprise et rôle projetés par le serveur, confirmation avant chargement métier | `SMART_AO_EXP_01_CONTEXTE_ROLES_PREUVE_VERTICALE_v0.1.md` |
| Première Affaire | création réelle, `command_id`/`idempotency_key`/`correlation_id` conservés au rejeu, aucun doublon | `CreateCasePanel.test.tsx`, tests backend de création |
| Accueil | prochaine action, surveillance et événements composés depuis les projections autorisées | `App.test.tsx` |
| Invitation / récupération | émission, acceptation unique, expiration, non-divulgation, révocation et nouvel enrôlement MFA | preuves PostgreSQL antérieures référencées dans l'évaluation technique |
| Expiration | `401` + refresh refusé → jeton/acteur effacés, données masquées, contexte confirmé gardé seulement en mémoire | `useAuthentication.test.tsx`, `App.test.tsx` |
| Reprise | même acteur après MFA → rechargement obligatoire ; autre rôle → snapshot invalidé et projections vidées | `App.test.tsx` |

## 4. États difficiles parcourus

| État | Décision comportementale proposée | Résultat observé |
|---|---|---|
| réseau interrompu pendant une création | afficher « Création à vérifier » et proposer le rejeu avec les mêmes identifiants | prouvé |
| réponse HTTP connue en erreur | conserver l'erreur connue, sans la requalifier en succès ou en résultat inconnu | prouvé |
| absence normale (`404`) | rester silencieux lorsque la projection facultative est absente | prouvé |
| session expirée | masquer l'espace métier et exiger une nouvelle authentification | prouvé |
| reprise avec le même acteur | restaurer le dernier contexte uniquement après confirmation et reload serveur réussi | prouvé ; reload refusé reste une erreur |
| reprise avec un autre rôle | ne restaurer ni navigation ni Affaire de l'ancien rôle | prouvé |
| espace collaborateur | ne pas afficher les surfaces Patron, opportunités ou dépôt | prouvé |
| MFA ou bearer absents | refuser avant l'exécution du service métier | prouvé par les gardes et tests ciblés |

## 5. Limites à accepter ou à fermer

Ces points ne sont pas masqués par le prototype :

- PAGE-004 et PAGE-005 restent conditionnelles ; aucune donnée obligatoire ou préférence artificielle n'est inventée.
- Le snapshot de reprise est en mémoire uniquement. La fermeture de l'onglet, le changement d'appareil et les brouillons persistants restent hors périmètre.
- Les durées actuellement appliquées par le serveur sont 8 h d'inactivité, 24 h absolues standard et 12 h privilégiées ; l'alignement avec la proposition produit 30 min / 12 h n'est pas décidé ici.
- L'avertissement avant expiration n'est pas implémenté.
- Les preuves PostgreSQL invitation/récupération/profils/idempotence sont acquises dans les tranches précédentes mais non rejouées dans cette session, faute de conteneur PostgreSQL accessible.
- La suite backend non-DB complète compte 1 144 succès, deux assertions ops historiques liées à la réorganisation documentaire et deux tests d'extraction ignorés faute de PIL ; ces écarts ne touchent pas EXP-01.
- La preuve ne vaut ni qualification d'accessibilité complète, ni engagement de performance, ni certification juridique, ni validation de pilote.

## 6. Arbitrages demandés au propriétaire

| Décision | Proposition à valider | État |
|---|---|---|
| périmètre EXP-01 | conserver PAGE-004/PAGE-005 hors parcours jusqu'à l'identification d'un prérequis réel | APPROUVÉ |
| reprise après expiration | accepter le snapshot en mémoire, le masquage immédiat et le reload obligatoire | APPROUVÉ |
| résultat inconnu | accepter « à vérifier » + rejeu idempotent comme seul comportement de création interrompue | APPROUVÉ |
| rôles | confirmer Patron comme autorité et Responsable/Expert comme profils collaborateur sans droit supplémentaire | APPROUVÉ |
| limites de session | conserver les durées actuelles et traiter l'avertissement dans une décision dédiée | APPROUVÉ |
| passage suivant | autoriser la rédaction du `OWNER EXPERIENCE FREEZE` puis du cahier technique d'exécution | APPROUVÉ |

## 7. Commandes de reproduction

Depuis la racine du dépôt :

```text
cd web
npm test -- --run --maxWorkers=1
npm run build
npm run lint
cd ..
uv run --extra calendar pytest -m 'not db' --no-cov \
  backend/tests/api/test_auth_dependency.py \
  backend/tests/api/test_case_creation_api.py \
  backend/tests/application/test_case_creation.py \
  backend/tests/domain/case/test_case_creation.py \
  backend/tests/security/test_actor_context_authorization.py \
  backend/tests/security/test_totp.py
git diff --check
```

Résultats du 14 septembre 2026 : **141/141 tests front**, **31/31 tests backend ciblés**, build TypeScript/Vite, ESLint et `git diff --check` réussis.

## 8. Références

- [Évaluation technique EXP-01](SMART_AO_EXP_01_Evaluation_Technique_WORK_PROPOSAL_v0.1.md)
- [Preuve de reprise et états difficiles](SMART_AO_EXP_01_REPRISE_INTERRUPTION_PREUVE_VERTICALE_v0.1.md)
- [Preuve contexte et rôles](SMART_AO_EXP_01_CONTEXTE_ROLES_PREUVE_VERTICALE_v0.1.md)
- [Parcours et contrats de pages](../_ARCHIVE/work_reviews/SMART_AO_Experience_Utilisateur_Parcours_Pages_WORK_PROPOSAL_v0.1.md)
- [Plan global de conception et réalisation](SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md)
- [Cahier Produit/Métier OWNER v0.4](../00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md)
- [Catalogue Écrans/Parcours OWNER v0.3](../00_REFERENCE_ACTIVE/SMART_AO_Catalogue_Ecrans_Parcours_Produit_OWNER_CONSOLIDATED_v0.3.md)
- [OWNER EXPERIENCE FREEZE EXP-01](SMART_AO_EXP_01_OWNER_EXPERIENCE_FREEZE_v0.1.md)
