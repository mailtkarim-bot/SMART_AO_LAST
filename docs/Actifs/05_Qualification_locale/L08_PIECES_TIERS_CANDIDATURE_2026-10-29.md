# L08 — pièces tierces de candidature non financières — 29 octobre 2026

Le plan global reste seul statut. Checkout principal `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`;642empreintes WIP comparées à la clôture précédente. Aucun reset/clean/stash, nouveau checkout, stage, commit ou push.

**AS-IS :** les contrats d'entreprise ferment les types à INSURANCE/KBIS/RIB; les annexes C10 acceptent seulement INSURANCE/KBIS, avec droits administratifs explicites et copies figées. Les recettes précédentes prouvent les assurances PDF. Le contrôle final affiche les octets/empreintes mais pas encore la nature, le MIME et une validité explicitement inconnue par pièce.

**RISQUES :** confondre vérification documentaire interne/validité officielle; associer une pièce à la mauvaise société/exigence; perdre les octets ou le format dans le ZIP; relâcher les droits administratifs ou inclure un RIB; réutiliser une pièce expirée, refusée, obsolète ou d'un autre tenant.

**POINTS D'INSERTION :** bibliothèque/upload/verification d'entreprise natifs, propositions et contributions sourcées, sélection d'annexes/snapshot C10 existants, origine Submission/P5/ZIP et contrôle final Python/API/UI. Aucun nouveau type documentaire, droit ou gate. La qualification porte sur KBIS synthétique, déjà admis par les contrats, en PDF/PNG/DOCX; les autres familles restent des manques, pas une extension silencieuse.

**PLAN MINIMAL :**

- [x] Test rouge : nature et format manquants dans le contrôle final; projection enrichie en lecture, validité UNKNOWN distincte du statut interne VALIDATED, aucun manifeste/hash/retry historique modifié.
- [x] Recettes KBIS synthétiques par upload privé natif, inspection MIME réelle et scanner de fixture par SHA, revue humaine native; association à l'exigence, droits existants, sélection justifiée, revue/P5 et mêmes octets ZIP. Ancien parcours assurance et cadres DOCX rejoués.
- [x] Refus : société/exigence/hash étrangers, droit administratif absent, pièce refusée/expirée/altérée, upload incompatible et RIB dans les contrôles existants; omission KBIS visible, nouvelle revue REJECTED invalidant l'export. Source et droits restent tenant-scopés, aucun statut juridique ou signature déduit.
- [x] UI après consultation OpenDesign locale/Impeccable; source/format/UNKNOWN lisibles, preuve navigateur synthétique, ciblés et suite Web réussis, revue indépendante, types/lint/build et Semgrep. La suite backend complète est close avec son reçu d’exit.
- [x] Archiver le WIP et les preuves localement; vérifier le nettoyage, mettre à jour plan/index/registre et relire le miroir Basic Memory. Aucun live, corpus réel, VPS, déploiement, P3 réel, signature réelle, dépôt externe ou GO public.

**TESTS À AJOUTER :** nominal multiformat et bytes exacts, omission visible sans satisfaction présumée, droits/tenant/ownership, idempotence/retry, états invalide/expiré et source altérée. Les actes de test et le scanner restent synthétiques; aucune authenticité officielle ni conformité de candidature n'est prouvée.

Autorités : PF2-073/074, M2-184 et M2-239–242, CT31-40; lecture des chapitres actuels, aucune réécriture des cahiers. Méthode : cadrage/plan/TDD Superpowers, sécurité et vérification ECC. Les anciennes preuves restent datées et ne qualifient pas cette nouvelle tranche.

## Fonction obtenue et correction native

Les pièces KBIS, déjà admises par la bibliothèque et les annexes, sont qualifiées en PDF, PNG et DOCX synthétiques. Aucun nouveau type documentaire, MIME autorisé, droit, porte ou schéma ajouté. Le KBIS DOCX est une annexe copiée à l'identique, pas une reprise du chantier de remplissage des cadres acheteur. L'original, le lien à la société/exigence et la sélection exacte sont conservés dans la chaîne native jusqu'au ZIP.

`FinalControlFile` expose maintenant `document_kind`, `media_type` et `validity=UNKNOWN`. La projection ne modifie pas les manifestes C10/Submission ni leurs hashes. Le panneau réutilise les classes existantes et affiche Nature/Format/Validité UNKNOWN; aucun statut interne VALIDATED ne devient validité officielle, authenticité ou conformité. Les champs nouveaux restent optionnels pour un client lisant une réponse plus ancienne.

La recette native a reproduit `RESPONSE_PLAN_UNKNOWN` après un upload CLEAN et un acte humain VALIDATED réussis. Cause : le registre initial immuable garde PENDING; la bibliothèque lisait déjà le dernier acte append-only, mais plusieurs consommateurs lisaient le statut initial. Le nouveau lecteur partagé d'infrastructure reprend cette même règle : dernière révision corrélée par tenant/document, puis repli sur le registre en l'absence d'acte historique. Bibliothèque, preuves de capacités/propositions, préparation, annexes et Submission utilisent cette lecture courante. Une nouvelle revue REJECTED prime l'ancien VALIDATED et invalide l'usage futur sans réécrire le registre ni ses actes.

Le vérificateur natif verrouille la racine du document; la relecture des preuves la verrouille en SHARE dans la transaction consommatrice. La recette concurrente observe effectivement un writer en attente de verrou PostgreSQL : la lecture actuelle termine CURRENT avant le rejet, puis le rejet est enregistré et les lectures/export suivants refusent sa source. Aucun accord n'est créé par une lecture; le registre initial reste PENDING, les revues et snapshots historiques sont conservés.

## Preuves acquises

- Recettes KBIS : **4 réussites, 1 avertissement, 211,77 s**, exit0. PDF/PNG/DOCX inclus et PDF volontairement omis. La sélection omise laisse deux fichiers au ZIP et une annexe citée à obtenir; les sélections incluses ont trois fichiers. Validité, signature et conformité restent UNKNOWN dans tous les cas.
- Régressions partagées finales : **123 réussites, 1 avertissement, 799,99 s**, exit0 : bibliothèque/upload/revue, capacités/propositions, préparation, revue/snapshot/transmission, Submission, annexes, assemblage assurance, cadre DOCX existant et KBIS. Les campagnes se chevauchent et ne sont pas additionnées.
- Upload/refus : vrai inspecteur MIME, scanner synthétique par allowlist SHA; contenu textuel incompatible refusé422, mauvaise société404, upload et revue rejoués sans second acte. Avant scope administratif explicite, la sélection d'annexes est403. Mauvais IDs/exigences/hash sont422; copie figée altérée refuse l'export puis mêmes octets après restauration de la seule fixture.
- Après une lecture simulée à+2h, la source KBIS expirée devient REVIEW_REQUIRED et les présences UNKNOWN. Après revue humaine native REJECTED, l'ancien export est422, le contrôle REVIEW_REQUIRED; les copies figées restent intactes. Le test d'expiration modifie uniquement l'horloge de la route de lecture dans une fixture, pas les dates du registre ou une porte d'authentification.
- Web complet : **721 réussites, 4 ignorés, 90 fichiers, 384,10 s**, exit0; ciblés42/15,13s. Types et lint verts, avertissement historique App.tsx:517; build vert, chunk895,75kB (>500kB).
- Mypy application : **701 fichiers sans diagnostic**. App/tests :206diagnostics/40fichiers, mêmes identités de baseline; aucune CI de typage entière verte revendiquée. Ruff/format sur17Python, diff whitespace vert.
- Semgrep1.182.1, `p/security-audit`, après ciblés et contrôles : **99 règles/20fichiers/0finding/0erreur**, métriques off, sans exclusion Git, aucune publication. Les17Python et3Web sont figés pour les campagnes finales; suite backend entière close sur ces empreintes.

Deux premiers échecs du harnais ne sont pas des défauts produit : la revue documentaire retourne200, pas201, et le `version_id` de capacité est dans le reçu de l'agrégat parent. Un ancien double de test Submission a reçu la valeur de la nouvelle requête de statut courant; ses refus société/PENDING/expiration n'ont pas été retirés. Le rouge produit retenu est celui du brouillon422 RESPONSE_PLAN_UNKNOWN après revue native réussie; logs conservés.

## Revue, interface et limites

Revue indépendante statique : aucun finding concret confirmé sur latest tenant/document, priorité REJECTED, repli legacy, sérialisation des vérifications et consommateurs, métadonnées sans mutation des manifestes. Le relecteur n'a exécuté ni DB, ni test, ni scan; concurrence et refus sont prouvés par les runners du principal.

Chrome DevTools Local, véritable panneau/hook et CSS du dépôt sur rapports natifs enregistrés : PDF/PNG/DOCX, paquet/hash exacts, nature KBIS, format lisible et validité UNKNOWN. Omission visible sans prétendre que le document est inclus. Viewports mesurés1282/393px sans débordement, texte hérité16px et summaries44px; fermeture de session masque la projection. Aucun cookie/token/stockage local ou trafic externe. Il s'agit d'une API de projection simulée, pas d'une session sur API métier ni de Playwright. Pas de capture disque ou d'audit WCAG/visuel global revendiqué; preview et onglet dédiés arrêtés.

OpenDesign : consultation du catalogue courant, du système `linear-app` et de l'artefact C10 existant via le CLI MCP local configuré et son SDK installé; aucune installation, modification de configuration, génération Cloud/Vela/BYOK ou nouvel artefact. L'Owner CYTD reste l'autorité d'apparence; aucun nouveau CSS/token/palette/typo ou refonte globale dans cette tranche. Impeccable context une fois, audit/craft-floor consultés et detector final : zéro constat; PRODUCT/DESIGN/.impeccable non créés.

Superpowers : using-superpowers, brainstorming borné, writing-plans, test-driven-development, systematic-debugging, requesting-code-review. ECC : security-review et verification-loop. Graphify consulté avant recherches, Serena initialisé/activé, Context7 pour la corrélation SQLAlchemy, Basic Memory lu localement (CLI, MCP non exposé). Jev/Manus non nécessaires à la correction et à la revue locale bornée; aucun connecteur de publication utilisé.

Preuves privées : `/home/noor/.local/share/smartao-proofs/l08-third-party-20261029/`, dont quatre ZIP/manifestes/rapports/historiques sous `native-packets/`, `qualified-packets.json`, `browser-qualified.json`, logs et empreintes. L'antivirus, les acteurs et documents sont synthétiques; aucune authenticité de KBIS, validité officielle, lecture de registre public, signature réelle ou conformité de candidature prouvée. Les autres familles documentaires et formats restent non qualifiés; RIB reste exclu des annexes. L08 général reste PARTIAL, aucun moteur candidat activé ni GO public.

## Fichiers concernés

**Application Python et API :**

- [backend/app/modules/enterprise/application/enterprise_capability.py](../../../backend/app/modules/enterprise/application/enterprise_capability.py)
- [backend/app/modules/enterprise/application/enterprise_upload.py](../../../backend/app/modules/enterprise/application/enterprise_upload.py)
- [backend/app/modules/enterprise/infrastructure/library_reader.py](../../../backend/app/modules/enterprise/infrastructure/library_reader.py)
- [backend/app/modules/membership/infrastructure/collab_capability_reader.py](../../../backend/app/modules/membership/infrastructure/collab_capability_reader.py)
- [backend/app/modules/preparation/application/review.py](../../../backend/app/modules/preparation/application/review.py)
- [backend/app/modules/preparation/application/service.py](../../../backend/app/modules/preparation/application/service.py)
- [backend/app/modules/submission/application/service.py](../../../backend/app/modules/submission/application/service.py)
- [backend/app/modules/enterprise/infrastructure/document_verification.py](../../../backend/app/modules/enterprise/infrastructure/document_verification.py)
- [backend/app/modules/preparation/infrastructure/annexes.py](../../../backend/app/modules/preparation/infrastructure/annexes.py)
- [backend/app/modules/submission/application/final_control.py](../../../backend/app/modules/submission/application/final_control.py)
- [backend/app/modules/submission/public/final_control_contracts.py](../../../backend/app/modules/submission/public/final_control_contracts.py)

**Interface et types :**

- [web/src/shared/types.ts](../../../web/src/shared/types.ts)
- [web/src/features/submission/SubmissionFinalControl.tsx](../../../web/src/features/submission/SubmissionFinalControl.tsx)

**Tests et fixtures :**

- [backend/tests/application/test_submission_package.py](../../../backend/tests/application/test_submission_package.py)
- [web/src/features/submission/SubmissionPanel.test.tsx](../../../web/src/features/submission/SubmissionPanel.test.tsx)
- [backend/tests/application/test_submission_final_control.py](../../../backend/tests/application/test_submission_final_control.py)
- [backend/tests/db/test_l08_third_party_packet.py](../../../backend/tests/db/test_l08_third_party_packet.py)
- [backend/tests/db/test_transversal_affaire_workflow.py](../../../backend/tests/db/test_transversal_affaire_workflow.py)
- [backend/tests/support/third_party.py](../../../backend/tests/support/third_party.py)
- [backend/tests/support/third_party_concurrency.py](../../../backend/tests/support/third_party_concurrency.py)


## Clôture locale du 29 octobre 2026

Suite backend complète finale : **4 063 réussites, 3 avertissements, 3 752,56 s (1 h 02 min 32 s), exit0**. Même campagne conservée pendant les reprises utilisateur, aucune relance. Les20fichiers logiciels sont restés identiques; aucun résultat ciblé ajouté au total global. Avertissements Starlette/httpx et Pydantic alias historiques conservés. Log `backend-full.log` dans les preuves privées.

Base dédiée `smartao_third_party_test` vérifiée à **0 table métier / 0 ligne Alembic**, conteneur `smartao-l08-third-party-20261029` identifié et sans volume persistant arrêté/retiré. Aucun autre conteneur touché. Tête Alembic source unique `20261027_0146`, inchangée. Preview5199 et onglet dédiés fermés. Aucune modification hors périmètre du WIP initial642; index Git vide, même branche/HEAD.

Plan, index et registre actualisés. Le miroir local Basic Memory et les sauvegardes complètes/delta sont relus avant le compte rendu final; le plan reste seul statut. Les détails et reçus sont dans les preuves privées. Aucun commit, push ou opération live.

Prochaine étape : L08 — qualifier le rapprochement sourcé des formats et du mode de remise demandés par l’acheteur avec les pièces du pli exact, sans modifier les portes ni présumer leur conformité.
