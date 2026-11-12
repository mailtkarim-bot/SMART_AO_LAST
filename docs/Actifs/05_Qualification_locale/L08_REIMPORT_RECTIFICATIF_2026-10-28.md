# L08 — reconstruction après réimport rectificatif synthétique — 28 octobre 2026

Le plan global reste seul statut opérationnel. Checkout principal/HEAD vérifiés,619empreintes WIP comparées à la clôture précédente; aucun commit/push/nouveau checkout.

**AS-IS :** paquet V1 avec choix d'annexes exacts qualifié. Le dernier test remplaçait seulement une référence de version au registre et prouvait le refus d'anciens actes, sans réimport ni second ZIP positif.

**Risques :** réutilisation d'exigences, sources, propositions, revue ou P5V1; données seulement clonées au registre; contournement d'un gate économique pour obtenir V2; modification de l'historique.

**Insertion :** scénario natif existant de préparation/P5, upload/admission/extraction/classification/matérialisation et liaison DCE existants. Deux passages sur la même Affaire et les mêmes acteurs, nouvelles intentions et sources. Les témoins économiques/capacité/dossier sont relus et révisés par les actes existants; aucune porte assouplie. Toute lacune rencontrée sera corrigée après régression rouge, pas masquée par une mutation SQL de validation.

**Plan minimal :**

- [x] Construire le scénario exigeant deux ZIP exacts sur la même Affaire, avec véritables nouveaux originaux DOCX synthétiques, upload privé borné/inspection réelle, scanner synthétique en allowlist SHA, admission native et extraction/classification/matérialisation actives.
- [x] Observer le rouge et corriger seulement les manques natifs démontrés; nouvelles confirmations, sources de réponse, revues et P5. Les anciens identifiants/hashes sont refusés pour V2 et leurs octets restent inchangés.
- [x] Qualifier nominal/refus/retry/tenant/rôles et absence de transfert d'accord; tests ciblés puis contrôles appropriés, revue et Semgrep après tests.
- [x] Preuves/archives locales, nettoyage, plan/index/registre et miroir Basic Memory, sans activation, live, corpus réel, VPS, déploiement, P3 réel, dépôt externe ou GO public.

Les scanners/acteurs synthétiques ne prouvent pas une analyse antivirus, signature, décision ou dépôt réel. Les cadres acheteur arbitraires et l'exhaustivité restent hors de cette recette bornée.

## Comportement et correction démontrés

Le test initial reproduit un refus produit `DECISION_ALREADY_ACTIVE` après un vrai réimport : la décision finalisée sur V1 restait courante et empêchait de reconstruire le parcours sur V2. Le correctif réutilise la commande native de création de décision. Il verrouille l'Affaire, puis sa décision, et exige une nouvelle version applicable admise et vérifiée ainsi qu'une seule ancienne version identifiable dans le contexte final. Sans ces conditions, le refus existant reste inchangé.

L'ancienne décision reçoit `REVIEW_REQUIRED`/`STALE` avec les deux versions et un événement transactionnel. Son résultat, sa justification, son contexte final et ses conditions restent historiques. Un nouveau cycle démarre `DRAFT`/`UNDECIDED`/`INCOMPLETE`, sans contexte, justification ou condition hérités. Ce nouveau cycle ne donne ni accord Patron, ni P3, ni P5 : les actes natifs doivent être refaits. La nouvelle référence reste la première du reçu pour préserver son contrat HTTP. Aucun schéma, droit ou gate n'est étendu.

Deux intentions de création concurrentes donnent exactement une création et un conflit; le retry de l'intention gagnante rend le même reçu sans second cycle. La création sans changement de DCE reste refusée. Le remplacement, le nouveau cycle et leurs événements utilisent la transaction et les contrôles tenant/rôle existants.

## Recette reproductible et fichiers

`backend/tests/db/test_l08_reimport_packet.py` exerce deux variantes, réponse Markdown et cadre DOCX dédié, chacune sur la même Affaire et les mêmes acteurs pendant les deux générations. Les seules fixtures modifiées sont des copies dans le répertoire temporaire; aucun gold ou corpus réel n'est modifié.

1. Construire V1 par le parcours HTTP natif, avec revue exacte, annexes figées, snapshot, transmission et P5 synthétiques, puis conserver son ZIP.
2. Construire de nouveaux originaux DOCX synthétiques : échéance rectifiée, titres explicites RC/CCAP/CCTP/DPGF et cadre dédié lorsque applicable. Upload borné, inspection MIME réelle, staging/quarantaine et scanner synthétique par allowlist SHA, admission native, extraction, classification, analyse et matérialisation. Aucun clonage SQL d'une version admise ou mutation forcée de son statut.
3. Rattacher V2 par la commande native et son replay. Refuser l'export V1; reconstruire les sources et actes, la revue Patron, les sélections, le snapshot et un P5 propre à V2. Refuser la revue, la réponse, la sélection d'annexes et le hash P5 antérieurs.
4. Vérifier deux décisions/cycles et deux autorisations distinctes, de nouveaux identifiants et hashes de paquets/revues/snapshots, ainsi que des annexes de contenu réellement différent. Le manifeste de chaque ZIP correspond au manifeste enregistré et ses annexes aux copies figées. Les originaux, octets de réponse et annexes V1 restent inchangés.

Code applicatif : `decision/application/lifecycle.py`, `decision/application/ports.py`, `decision/infrastructure/repositories.py`. Tests et raccords : `tests/db/test_l08_reimport_packet.py`, `tests/db/test_transversal_affaire_workflow.py`, `tests/support/transversal_affaire.py`, `tests/application/test_p0_remediation.py`, tous sous `backend/`. La fixture partagée relit les révisions courantes sur le second passage et donne aux sources synthétiques de capacité/assurance des identités nouvelles; son parcours ordinaire reste couvert par la suite globale.

Les erreurs intermédiaires de harnais sont conservées : mauvais appel d'un helper, révisions de fixture périmées, titres de documents insuffisants pour l'admission et collision de nom de capacité. Elles ont été corrigées dans le harnais, sans relâcher classification, unicité ni readiness. Le refus de DCE non prêt n'est pas annoncé comme une réussite. Le rouge produit est conservé séparément dans `smartao-reimport-native3.log`.

## Vérifications acquises avant clôture globale

- Ciblés finaux : `pytest -q backend/tests/db/test_l08_reimport_packet.py`, sur URL/flag jetables explicites, **2 réussites**, 1 avertissement, **317,92 s**, exit 0. Les deux variantes incluent concurrence et replay.
- Web inchangé : **713 réussites, 4 ignorés, 89 fichiers**, 400,74 s; types, lint et build réussis. Avertissements historiques : dépendance de hook dans App.tsx et chunk de 886,39 kB.
- Mypy application : **698 fichiers sans diagnostic**. App/tests : **206 diagnostics dans 40 fichiers**, mêmes identités qu'à la clôture DOCX; cette dette n'est pas présentée comme une CI verte.
- Ruff et format : sept fichiers Python verts; sept empreintes figées identiques avant/après contrôles. Tête Alembic source unique `20261027_0146`, aucune migration dans ce changement.
- Après tests et contrôles : Semgrep **1.182.1**, configuration `p/security-audit`, métriques désactivées, **79 règles / 7 fichiers / 0 finding / 0 erreur**. Aucun résultat envoyé à un service distant. Recherche de secrets sur le delta : zéro candidat.
- Revue indépendante statique bornée : aucun défaut concret résiduel confirmé sur requalification, verrouillage/CAS, historique ou absence de transfert d'accord. Le relecteur n'a pas exécuté de recette DB; la preuve concurrente provient du runner principal.

Preuves privées : `/home/noor/.local/share/smartao-proofs/l08-reimport-20261028/`, dont `qualified-packets.json`, quatre ZIP V1/V2 et leurs manifestes, logs rouges/verts, empreintes et comparaison mypy. Les recettes chevauchantes ne sont pas additionnées au compte de la suite complète.

## Méthode et limites

Superpowers : using-superpowers, brainstorming borné, writing-plans, test-driven-development, systematic-debugging, requesting-code-review. ECC : security-review et verification-loop. Graphify interrogé avant l'exploration, contexte Basic Memory vérifié contre les sources; Serena initialisé sur le projet, sans navigation sémantique supplémentaire nécessaire. Aucun contrat de bibliothèque nouveau : Context7 non sollicité. Jev/Manus non utilisés, car la correction et sa preuve sont locales et bornées.

Aucune édition UI, donc aucun nouveau travail OpenDesign/Impeccable ni preuve navigateur. La suite Web est une régression, pas une recette E2E. Aucun Playwright MCP disponible, aucun Chrome DevTools utilisé pour cette tranche. Aucun S3, antivirus réel, source client, live, VPS, déploiement, P3 réel, dépôt externe, activation de candidat ou GO public. La recette exige des documents explicitement typés; elle ne prouve ni les cadres arbitraires ni une couverture exhaustive. Les signatures et les manques des réponses restent UNKNOWN. L08 général reste PARTIAL.

## Clôture des vérifications et conservation

Suite backend complète finale : **4 046 réussites, 4 avertissements, 3 717,18 s (1 h 01 min 57 s), exit 0**. Commande `SMART_AO_TEST_DISPOSABLE_DATABASE=1 SMART_AO_TEST_DATABASE_URL=<URL PostgreSQL jetable dédiée> ./.venv/bin/pytest -q --tb=short --maxfail=1`. Les avertissements Starlette/httpx et Pydantic alias sont conservés; aucun test ignoré ou ancien résultat substitué. Log `backend-full.log` dans les preuves privées. Aucun fichier logiciel modifié pendant cette campagne.

Base dédiée `smartao_reimport_test` vérifiée à **0 table métier / 0 ligne Alembic** après la suite. Conteneur `smartao-l08-reimport-20261028`, identité vérifiée et sans volume persistant, arrêté et retiré; reçu `cleanup-final.json`. Aucune ressource partagée nettoyée, aucun navigateur ou serveur UI démarré pour cette tranche.

Plan, index et registre de régression actualisés. Le miroir local Basic Memory a été écrit avec contrôle de concurrence puis relu : prochaine étape et SHA du plan final identiques; son reçu est `memory-sync-final.json` dans les preuves privées. Le plan reste seul statut, les anciennes preuves/checkpoints restent historiques. WIP principal préservé; empreintes complètes et delta de cette tranche archivés localement, index Git vide, branche et HEAD inchangés. Aucun commit ou push.

Prochaine étape : L08 — qualifier le contrôle final des pièces et signatures du pli exact, avec manques visibles et actes humains, sans dépôt externe ni conformité présumée.
