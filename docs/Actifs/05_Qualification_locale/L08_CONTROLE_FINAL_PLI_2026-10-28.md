# L08 — contrôle final des pièces et signatures du pli exact

Le plan global reste seul statut. Cadrage du 28 octobre 2026, checkout principal `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`; 623 empreintes WIP vérifiées contre la précédente clôture. Aucun reset/clean/stash, nouveau checkout, stage, commit ou push.

**AS-IS :** manifeste exact et ZIP natifs, revues C10/P5 et registre de signature disponibles. Absence d'une lecture consolidée du contrôle final; la signature UI n'est pas une preuve par pièce et sa commande ne fige pas encore toute l'intention de retry.

**Risques :** confondre présence/réponse/conformité, signature du manifeste/signature des pièces, état historique/paquet courant; afficher un accord d'un autre paquet ou tenant; masquer les manques connus sous UNKNOWN; dupliquer un acte après timeout.

**Insertion :** port existant de lecture des sources Préparation, couverture sourcée existante, service et route Submission, signatures natives et panneau Submission existant. Aucun schéma ou gate nouveau. Les lectures restent sans acte; revue, signature demandée et P5 demeurent distincts et humains. Aucun dépôt externe ni fournisseur réel.

**Contrat borné :** contrôler un paquet ID/version/SHA précis, vérifier ses sources, inventorier les fichiers exportables et les références sans octets, rendre les manques connus et leurs sources visibles, afficher les revues/P5 exacts sans contourner le lecteur de signature protégé. Conformité, validité cryptographique, pouvoir du signataire et exhaustivité restent UNKNOWN. Une source obsolète rend le contrôle REVIEW_REQUIRED, sans transporter ses accords à une nouvelle version. Pas de P5 ou signature déduits de la lecture.

## Plan minimal et preuves attendues

- [x] TDD : contrôle natif avec sources/revue/annexes; manques textuels et annexes absentes visibles, fichiers du rapport conformes au ZIP, signature/P5 distincts; refus tenant/rôle et source remplacée, lecture sans effets.
- [x] Lecture métier Préparation → Submission et contrat HTTP typé; compatibilité legacy UNKNOWN. Réutiliser les vérifications d'origine et la couverture existantes, sans matrice parallèle ni ouverture des portes.
- [x] Demande humaine de signature côté client : intention exacte, motif et confirmation, double clic/retry identiques, réponse tardive et mauvais paquet masqués. **Le serveur natif refuse ce flux protégé : aucune signature réussie n'est qualifiée.**
- [x] UI dans le panneau existant, consultation OpenDesign locale et Impeccable, tests Web et assertions navigateur synthétiques bornées. Pas de refonte CYTD, preuve screenshot ou Playwright revendiquée.
- [x] Suites appropriées, revue, lint/types/build, Semgrep après tests, diff/secrets, empreintes et sauvegarde locales; plan/index/registre puis miroir Basic Memory relu, ressources dédiées nettoyées.

Autorités : PF2-074, M2-239–242, CT31-40 et contrôles natifs C10/P5. Les objets arbitraires, contrôles juridiques, signatures réelles, corpus clients et dépôts restent hors de la preuve synthétique.

## Résultat métier et invariants

Le Patron peut ouvrir `GET /api/v1/patron/submission-packages/{id}/final-control` depuis le panneau existant. Le service reprend l'autorisation de lecture du manifeste puis relit l'origine Préparation et ses octets dans la transaction. Préparation reste responsable de la vérification et de la couverture sourcée; aucune seconde matrice n'est construite. Le manifeste et son hash canonique ne changent pas, P5 et l'export ne reçoivent aucune nouvelle porte.

La projection donne les noms et empreintes des fichiers exportables, les annexes et exigences liées, les références du manifeste qui n'ont **pas de fichier exporté**, ainsi que les textes manquants ou incomplets et leurs extraits/ancres/lots candidats. `TEXT_PRESENT` ne devient pas une couverture validée. Les données financières restent hors de cet inventaire; une référence `OFFICIAL_PRICING_VERSION` n'est jamais présentée comme un fichier livré. Ni complétude financière ni conformité du pli ne sont déduites.

`CURRENT` signifie que les sources natives ont été vérifiées à la lecture. Le rapport reste `PARTIAL`. Un rectificatif rend les sources historiques `REVIEW_REQUIRED` et leurs présences `UNKNOWN`; aucune exigence courante n'est remplacée par une ancienne liste. Les revues/P5 sont des références exactes, pas des accords transportables. Un candidat legacy sans origine qualifiée reste `UNKNOWN`. Les lectures n'ajoutent ni événement ni outbox.

### Signature : porte préservée, aucune preuve inventée

La politique native refuse `SECURITY_RESTRICTED` hors flux dédié, y compris au Patron. Les GET/POST de signature restent donc protégés. Le contrôle final **ne consulte pas le registre** : `signature_visibility=RESTRICTED`, projection vide contrainte à zéro élément. Cette liste vide est un masquage constant, jamais le constat qu'aucune signature existe. Le panneau dit « lecture protégée, état UNKNOWN »; aucun fait, fournisseur, identifiant ou compteur de ce registre n'est divulgué.

L'intention de demande côté client fige paquet/version/SHA, motif et identifiants de commande/idempotence/signature après relecture et confirmation humaine. Double clic bloqué, UNKNOWN/408/429 rejoués à l'identique; GET de rapprochement seulement après conflit409, et uniquement si ID/version/hash correspondent. Un refus4xx définitif libère l'intention sans inventer REQUESTED. L'API accepte SHA attendu et motif optionnels; le handler refuse un hash discordant et conserve le motif dans l'événement si un flux autorisé l'atteint. Sérialisation legacy inchangée lorsque ces champs sont absents; preuve indépendante du hash d'idempotence. Un motif blanc est refusé à la frontière HTTP.

Les recettes clientes positives de reçu/retry sont des doubles de transport. Elles ne prouvent **pas** une demande autorisée par la politique native, un appel fournisseur ou une signature. Les actes positifs natifs qualifiés restent les revues C10 et P5 synthétiques du parcours antérieur, relus ici; les demandes de signature natives sont403 sans effet.

## Régressions rouges et revue indépendante

- Première lecture de contrôle absente : `AttributeError`, puis route native404; implémentation minimale et passage positif.
- UI : contrôle absent, envoi de demande sans confirmation, puis tests exacts de double clic/UNKNOWN/mauvais paquet/réponse tardive.
- P1 trouvé en revue : le premier rapport interrogeait le registre malgré sa porte dédiée. Rouge avec un vrai enregistrement synthétique `SIGNED` préexistant dans une fixture DB de lecture; correction supprimant totalement cette lecture, vert. Ce seed historique sert uniquement au contre-exemple de confidentialité et ne constitue pas un acte de signature autorisé.
- P2 trouvé en revue : une réponse de signature A pouvait rester affichée après sélection de B. Rouge A→B différé, setter invalidant la génération et masquant statut/fournisseur/révision, vert. Le retour est vérifié contre l'identifiant encore sélectionné.
- Rapprochement final : rouge sur entrée candidate SHA-B avec couverture C10 vérifiée SHA-A. Garde strict schéma/origine, document généré ID/version, SHA/format du brouillon exact et mêmes entrées d'annexes. Sept divergences qualifiées : SHA, document, version, format, doublon, annexe et schéma. La première globale a été interrompue volontairement après **1605 réussites / 862,59 s / exit2**, non qualifiante. Rejeu ciblé final121vert puis nouvelle globale complète4058verte, sans substitution du run interrompu. Contre-revue statique sans contresens confirmé, distinction version du document généré/version du brouillon préservée.
- Cache P5 : rouge sur changement de paquet laissant un manifeste/P5 précédent observable. Le retour public masque ces données hors paquet exact, tout en gardant le cache interne nécessaire au retry UNKNOWN après retour à la sélection initiale.42tests Web ciblés verts; contre-revue statique sans contresens confirmé.
- Hash de demande discordant et motif blanc : rouges puis verts. Le premier essai du test de hash avait une fixture incomplète; cette erreur de harnais a été corrigée avant de retenir le rouge « DID NOT RAISE ».
- Contre-revue statique : aucun défaut concret nouveau confirmé sur P1/P2. Aucun test/DB exécuté par le relecteur; les preuves de runners sont celles du principal.

Deux invocations de création de tests ont utilisé par erreur un préfixe `web/` depuis `web/`; elles n'ont rien écrit et ne sont pas comptées comme des tests produit. Chemins corrigés et runners rejoués. Aucun fichier préexistant supprimé ou restauré depuis HEAD.

## Vérifications acquises et limites

- Recette backend finale étendue, après garde des entrées : **121 réussites**, 1 avertissement, **263,88 s**, exit0. Deux formats et deux générations par Affaire; quatre ZIP/manifestes/rapports finaux enregistrés et relus indépendamment : trois fichiers par ZIP, chaque SHA égal aux octets de l'archive. Contrôle après rectificatif, rôles/absence d'authentification, absence de commande à la lecture, P5 et refus de signature natifs qualifiés. La précédente114/271,00s est historique, pas additionnée.
- Web complet final : **721 réussites, 4 ignorés, 90 fichiers, 249,36 s**, exit0, sur les neuf fichiers Web finaux figés. Types/lint/build finaux verts, warning historique App.tsx:517 et chunk **895,39 kB** (>500 kB). Les campagnes720/277,84s et721/245,33s sont historiques, pas substituées à ce dernier reçu.
- Python : Ruff/format sur17fichiers; mypy application **700 fichiers sans diagnostic**. App/tests : **206 diagnostics dans40fichiers**, mêmes identités que la baseline, aucune CI globale verte revendiquée. Aucun schéma, migration, dépendance ou moteur candidat changé.
- Semgrep **1.182.1**, `p/security-audit`, après ciblés/contrôles et Web complet : **99 règles / 26 fichiers / 0 finding / 0 erreur**, sans exclusion Git, métriques désactivées, aucune publication des résultats. Scan borné de motifs de secrets : aucun candidat; ni ce scan ni Semgrep ne prouvent la sécurité globale.
- 17 fichiers Python figés et identiques pendant la nouvelle globale backend; neuf fichiers Web figés pour leur dernière suite.26empreintes finales suivies. L'ajustement des deux classes UI ne change aucun fichier Python; les campagnes restent distinctes et leur reçu d'exit est requis.

### Navigateur, design et outillage

Chrome DevTools Local : contexte isolé, véritable composant/panneau et hook, CSS du dépôt, projection native synthétique enregistrée. Dernières assertions aux viewports mesurés1282 et393px : manques/UNKNOWN visibles, aucun débordement, demande désactivée avant confirmation, paquet/hash/motif exacts, refus403 sans REQUESTED, fermeture de session masquant avant/après réponse tardive, projection d'un mauvais paquet rejetée, manifeste/P5/export masqués après changement de paquet. Le nouveau bouton mesuré initialement36,19px a été porté à44px via une classe d'actions existante; les deux summaries sont44px. La classe claire de prévisualisation a été remplacée par celle de couverture existante : texte hérité16px, contraste mesuré14,62:1 contre le fond de la recette. Aucun nouveau CSS/token/palette. Aucun cookie/token/stockage local ou trafic externe. API en mémoire simulant le refus natif, **pas recette navigateur sur API métier**, ni Playwright. Les deux captures disque ont été refusées par la validation des racines MCP, y compris dans le dépôt : aucune preuve screenshot ni audit visuel/WCAG complet revendiqués. Preview finale dédiée et onglet arrêtés. Les intentions clientes sont limitées au composant actif; aucune reprise durable de signature autorisée après fermeture de session n'est qualifiée par ces mocks.

OpenDesign : outils de session en erreur « Transport closed »; reconnexion de lecture via **le même MCP local configuré**, son CLI et SDK installés, sans installation ou modification de configuration. Catalogue courant, système `linear-app` et artefact C10 existant `plan-reponse-c10.html` consultés; pas de génération Cloud/Vela/BYOK ni nouvel artefact. L'artefact historique et le catalogue ne remplacent pas les captures CYTD Owner; aucun nouveau token/palette/typo, aucune refonte ni conformité CYTD globale revendiquée. Structure et classes du panneau existant conservées. Impeccable context une fois, référence audit/craft-floor, detector sur trois fichiers UI : zéro constat mécanique; PRODUCT/DESIGN/.impeccable non créés.

Superpowers : using-superpowers, brainstorming borné, writing-plans, test-driven-development et requesting-code-review. ECC : security-review et verification-loop. Graphify interrogé avant exploration; Serena initialisé/activé, aucune navigation sémantique nécessaire. Context7 consulté pour le wrap serializer Pydantic et modèle installé/vérification legacy. Basic Memory lu et point de reprise synchronisé/relu via CLI local (outils MCP Basic Memory non exposés dans la session); le plan reste l'autorité. Jev/Manus non utilisés : correction locale bornée et revue ciblée. Aucune action GitHub ou autre connecteur externe autorisée/exécutée.

Preuves privées : `/home/noor/.local/share/smartao-proofs/l08-final-control-20261028/`, recettes sous `native-packets/`, `qualified-packets.json`, `browser-checks.json`, comparaison mypy, contexte OpenDesign, logs et empreintes. Les campagnes qui se chevauchent ne sont pas additionnées.

Aucun live, corpus réel, VPS, déploiement, P3 réel, signature réelle, dépôt externe, admission/activation de moteur ou GO public. L08 général reste PARTIAL : pièces tierces, cadres arbitraires, contrôles financiers et signatures réelles ne sont pas qualifiés par cette lecture bornée.

## Fichiers de cette tranche

**Application Python et API :**

- [backend/app/interfaces/http/routes/patron_submission.py](../../../backend/app/interfaces/http/routes/patron_submission.py)
- [backend/app/interfaces/http/routes/patron_submission_signature.py](../../../backend/app/interfaces/http/routes/patron_submission_signature.py)
- [backend/app/modules/preparation/application/review.py](../../../backend/app/modules/preparation/application/review.py)
- [backend/app/modules/preparation/infrastructure/submission_source_reader.py](../../../backend/app/modules/preparation/infrastructure/submission_source_reader.py)
- [backend/app/modules/submission/application/ports.py](../../../backend/app/modules/submission/application/ports.py)
- [backend/app/modules/submission/application/service.py](../../../backend/app/modules/submission/application/service.py)
- [backend/app/modules/submission/application/signature_commands.py](../../../backend/app/modules/submission/application/signature_commands.py)
- [backend/app/modules/submission/application/signature_service.py](../../../backend/app/modules/submission/application/signature_service.py)
- [backend/app/modules/submission/public/signature_contracts.py](../../../backend/app/modules/submission/public/signature_contracts.py)
- [backend/app/modules/submission/application/final_control.py](../../../backend/app/modules/submission/application/final_control.py)
- [backend/app/modules/submission/public/final_control_contracts.py](../../../backend/app/modules/submission/public/final_control_contracts.py)

**Interface et client HTTP :**

- [web/src/features/submission/SubmissionPanel.tsx](../../../web/src/features/submission/SubmissionPanel.tsx)
- [web/src/features/submission/useSubmissionActions.ts](../../../web/src/features/submission/useSubmissionActions.ts)
- [web/src/infrastructure/api.ts](../../../web/src/infrastructure/api.ts)
- [web/src/shared/types.ts](../../../web/src/shared/types.ts)
- [web/src/features/submission/SubmissionFinalControl.tsx](../../../web/src/features/submission/SubmissionFinalControl.tsx)

**Tests et fixtures :**

- [backend/tests/application/test_submission_package.py](../../../backend/tests/application/test_submission_package.py)
- [backend/tests/application/test_submission_signature_commands.py](../../../backend/tests/application/test_submission_signature_commands.py)
- [backend/tests/application/test_submission_signature_service.py](../../../backend/tests/application/test_submission_signature_service.py)
- [web/src/features/submission/SubmissionPanel.test.tsx](../../../web/src/features/submission/SubmissionPanel.test.tsx)
- [web/src/features/submission/useSubmissionActions.test.tsx](../../../web/src/features/submission/useSubmissionActions.test.tsx)
- [backend/tests/application/test_submission_final_control.py](../../../backend/tests/application/test_submission_final_control.py)
- [backend/tests/db/test_l08_reimport_packet.py](../../../backend/tests/db/test_l08_reimport_packet.py)
- [backend/tests/support/final_control.py](../../../backend/tests/support/final_control.py)
- [web/src/features/submission/finalControl.testdata.ts](../../../web/src/features/submission/finalControl.testdata.ts)
- [web/src/features/submission/useSubmissionFinalControl.test.tsx](../../../web/src/features/submission/useSubmissionFinalControl.test.tsx)


## Clôture locale du 29 octobre 2026

Suite backend complète finale : **4 058 réussites, 2 avertissements, 2 554,11 s (42 min 34 s), exit0**. Campagne lancée le28/10, terminée sans relance pendant la reprise du29/10. Log `backend-qualified.log` et empreintes dans les preuves privées. Les17fichiers Python sont restés identiques pendant cette campagne; les9Web sont identiques à leur dernière suite721/4ignorés/249,36s. Les avertissements Starlette/httpx et Pydantic alias sont conservés. Aucun ancien run substitué ou total de sous-suites additionné.

Base dédiée vérifiée à **0 table métier / 0 ligne Alembic**, puis conteneur `smartao-l08-final-control-20261028` identifié, sans volume persistant, arrêté et retiré. Aucun autre conteneur touché. Tête Alembic source unique `20261027_0146`, inchangée. Les previews et onglets dédiés sont fermés; aucune capture disque créée.26empreintes finales contrôlées, aucune modification inattendue du WIP initial, index Git vide, même branche/HEAD.

Plan/index/registre actualisés; reçu du miroir local Basic Memory et sauvegardes locales vérifiés avant le compte rendu final. Le plan reste l'unique statut. Le dossier commence le28/10 et se clôt le29/10; son nom daté d'ouverture est conservé. Aucun commit/push ou nouvelle opération live.

Prochaine étape : L08 — qualifier l’inclusion de pièces tierces de candidature non financières, au-delà des assurances, dans le pli exact, avec sources, formats, droits et manques visibles, sans modifier les portes ni présumer leur validité.
