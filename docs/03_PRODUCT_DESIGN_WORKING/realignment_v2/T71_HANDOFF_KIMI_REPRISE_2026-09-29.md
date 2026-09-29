# T71 — Handoff Codex après réception structurée (actualisé 29 septembre 2026)

## Où reprendre

Le dépôt est `/home/noor/PROJECTS/BTP/SMART_AO_V8`, branche `feat/ccap-cctp-risk-register-20260831`, HEAD local `f0c27b5`. Le HEAD est identique à `origin/feat/ccap-cctp-risk-register-20260831`, mais **le travail postérieur est présent uniquement dans un arbre local fortement modifié et non commité**. Ne pas nettoyer, réinitialiser, stash, committer ou pousser sans instruction explicite de Noor. Ne pas toucher aux dossiers locaux non suivis `.codex/`, `.kimi-code/` et `.serena/`.

Le plan de réalisation, mis à jour le 29/09, confirme les obligations post-réception, les actes humains sourcés, leur lien DCE, le registre des contrats/avenants, le remplacement contractuel, la requalification et la chronologie C07. La réception structurée 0114 reste validée. PUX-11/C12 est maintenant exercé dans Brave Origin via Chrome DevTools MCP, avec profil isolé. La session Patron a passé le login, TOTP et confirmation de contexte ; C12 a lu les résultats depuis l’API, puis le parcours a persisté WON → commande ACCEPTED → P6 APPROVED → P7 UNKNOWN. Lecture PostgreSQL en fin de test : un résultat, une commande, un P6, un P7 et aucune transmission externe. Le rendu mobile C12 et l’ordre de focus ont été vérifiés ; la capture ciblée est temporaire dans `/tmp/smart-ao-c12-proof-2026-09-29T18-48-30-950Z/10-c12-mobile-p7.png`. Le test de régression empêche maintenant App de lancer des lectures Patron avant MFA et confirmation de contexte. La prochaine tranche est PUX-12 C12→C13 REX : motif connu/inconnu, portée, revue avant réemploi ; aucun apprentissage automatique.

## Preuves enregistrées dans le plan

Pour la réception 0114, PostgreSQL E2E ciblé **2/2**, backend complet **1920/1920**, frontend **237/237** et gates locales passaient. Pour C12/PUX-11, backend complet antérieur **1923/1923** (14 min 50, PostgreSQL dédié 5433, un avertissement Starlette/httpx), et maintenant frontend complet **253/253**, typecheck/lint/build verts. Brave Origin a réellement traversé l’application Vite, l’API et la base `smart_ao_v8_cua` après MFA. Les actes ont été persistés une fois : outcome WON, order ACCEPTED, P6 APPROVED, P7 UNKNOWN. `GET execution-results` répond 200 ; capture clavier mobile et Lighthouse snapshot effectués. Le seed original de Kimi écrivait le facteur TOTP dans l’ancienne table `mfa_factors`, d’où `TOTP_NOT_ENABLED`; le ciphertext existant a été copié vers `mfa_totp_factors` dans la seule base CUA. Le helper temporaire `/tmp/seed_cua.py` a été corrigé pour semer le modèle courant et ne plus imprimer les valeurs sensibles. Le snapshot Lighthouse est à 96/100 en accessibilité et 100/100 en bonnes pratiques ; l’échec de contraste est ailleurs dans l’application, aucun élément C12 n’est signalé. Écart observé sur mobile : le document dépasse la largeur visible d’environ 1 px (`body.scrollWidth`). Le serveur backend local a signalé ClamAV indisponible dans `/healthz/ready`, mais l’authentification et le parcours C12 fonctionnent. Aucun backend modifié, aucun commit/push. Basic Memory reste non joignable dans cette session.

## Invariants

- L’avenant et le contrat signé sont des versions déclarées par le Patron avec référence, sources et pièces ; cette déclaration ne vérifie ni signature, ni authenticité, ni applicabilité juridique.
- Le registre reste tenant-scoped, limité à l’Affaire, idempotent et append-only ; l’historique n’est jamais réécrit.
- Le lien avenant → version remplacée est un acte append-only séparé du registre d’identification de version ; il capture la justification, l’acteur et la date.
- Une absence de version ou de preuve reste `UNKNOWN`. Un avenant déclaré remplaçant une version signale les actes concernés à requalifier (`REVIEW_REQUIRED`) sans les modifier ; le signal du lien contractuel reste séparé de la relation DCE.
- Les décisions humaines de requalification `RETAINED_AS_DECLARED`, `RELINKED_TO_DECLARED_VERSION` et `NEEDS_CLARIFICATION` sont append-only et révisionnées par acte/déclaration. Elles ne modifient pas l’acte source et ne font pas disparaître le signal `REVIEW_REQUIRED`.
- La chronologie renvoie les événements `EXECUTION_EVIDENCE`, `INSTRUMENT_SUPERSESSION`, `EVIDENCE_REQUALIFICATION` séparément ; ordre serveur par révision/date/type/id. `SUPERSEDED` est explicitement une déclaration Patron non vérifiée.
- Les nouvelles réceptions exigent `WITH_RESERVATIONS`, `UNDER_RESERVATIONS` ou `WITHOUT_RESERVATIONS` ; seuls les deux premiers résultats permettent de sourcer une nouvelle levée. La base impose le lien tenant/Affaire par clé étrangère composite.
- Les champs ajoutés restent nullable pour garder les actes et obligations préexistants intacts ; leur absence est projetée `UNKNOWN`. Aucun backfill, échéance juridique, DGD/forclusion, paiement, ni clôture automatique n’est introduit.
- Le prochain axe codable garde les catégories produit `WITH_RESERVATIONS`, `UNDER_RESERVATIONS`, `WITHOUT_RESERVATIONS` et `UNKNOWN` distinctes. Le Product Freeze ne fixe pas ici de statut `REFUSED` validé : ne pas l’inventer sans source produit supplémentaire.
- Aucune échéance, conséquence ou conclusion juridique n’est calculée automatiquement. Le NO-GO public demeure.
- Aucun push GitHub. La synchronisation Basic Memory n’était pas disponible : aucun serveur MCP Basic Memory n’est exposé et aucun CLI `basic-memory`/`bm` n’est installé dans cette session.

## Ordre de lecture minimal

1. `AGENTS.md` et `docs/03_PRODUCT_DESIGN_WORKING/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md` (autorité de reprise opérationnelle).
2. `docs/00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v2.0.md` (autorité produit/métier).
3. `docs/03_PRODUCT_DESIGN_WORKING/realignment_v2/T70_HANDOFF_REPRISE_CODEX_2026-09-28.md` uniquement pour le contexte paiement de la veille ; il précède les tranches du 29/09.
4. Les migrations `20260929_0110` à `20260929_0114`, les modèles/handlers `contract_execution_evidence` et `post_reception_obligation`, leurs tests API/PostgreSQL et les composants C07 correspondants.

## Instruction de reprise

Commencer par `git status --short --branch` et `git diff --stat` : l’arbre garde les précédents changements Kimi/Codex non commités. PUX-11/C12 est validé localement ; ne rejouer aucune écriture dans `smart_ao_v8_cua`, qui contient déjà le cycle unique WON → ACCEPTED → APPROVED → UNKNOWN. Prochaine tranche : auditer les contrats vivants `RecordCaseRex` et GET REX, puis implémenter PUX-12 C12→C13 en lecture/écriture Patron, avec motif connu/inconnu, portée explicite et revue avant réemploi mémoire. Ne jamais apprendre automatiquement ni écraser l’historique. Maintenir `P7 ≠ ordre de service`, NO-GO public, aucun commit ou push sans demande explicite. Captures QA actuelles dans `/tmp/smart-ao-c12-proof-2026-09-29T18-48-30-950Z/` (artefacts fragiles, non suivis par Git).
