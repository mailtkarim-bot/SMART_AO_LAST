# L08 — chiffrage révisé, réponse sourcée et pli exact

Qualification locale avec limites ; le plan global demeure la seule autorité de statut. L08 général reste PARTIAL.

AS-IS : le mode FULL lie déjà le paquet à un rapport de prix publié ; le manifeste contient OFFICIAL_PRICING_VERSION, sans montant ni fichier financier exporté. C10, revue, snapshot, P5 et ZIP exact existent. Le contrôle final ne rapproche pas cette référence avec le dernier rapport publié.

RISQUES : présenter l’ancien chiffrage comme le dernier, transférer l’accord P5 au paquet reconstruit, assimiler une référence sans fichier à une pièce remise, divulguer des montants privés ou modifier les portes sous couvert de fraîcheur.

POINTS D’INSERTION : projection de contrôle final Submission et interface existante, tests de continuité natifs. Aucun changement de manifeste, hash, export, calcul financier, schéma, droit ou politique P5.

PLAN MINIMAL :

- [x] Prouver le manque de filiation visible par tests rouges backend/UI.
- [x] Ajouter une observation bornée et tenant-scoped de la référence de prix, sans montants ni effet sur les portes ; garder UNKNOWN et candidature seule distincts.
- [x] Qualifier prix importés/publiés V1→réponse C10/pli→nouvelle publication→nouveau pli/P5, sources et manques exacts ; ancien accord non transféré.
- [x] Revue, tests, qualité/sécurité, rendu, sauvegarde WIP puis plan et miroir Basic Memory relus.

TESTS À AJOUTER : référence courante, nouveau rapport publié, référence absente/discordante, candidature seule, lecture interdite/tenant étranger, reconstruction avec nouveau hash/P5, fichier financier absent visible, absence de montant ou de stockage privé dans le contrôle et le ZIP. Réutilisation du parcours Markdown existant ; tranche DOCX déjà close non recommencée.

Checkout principal/branche/HEAD vérifiés ; 749 empreintes WIP L07 identiques avant édition. Preuves locales : `~/.local/share/smartao-proofs/l08-pricing-response-20261104/`. Aucun nouveau checkout, reset/clean/stash, stage, commit, push, live, corpus réel, dépôt externe ou activation de candidat.

## Fonction livrée

Le contrôle final Patron rapproche la référence OFFICIAL_PRICING_VERSION du manifeste exact avec les métadonnées du rapport lié, puis le dernier rapport PUBLISHED de la même Affaire et du même tenant. Il restitue seulement ID/révision, jamais montant, marge ou clé de stockage. CURRENT veut dire « référence du dernier rapport publié lors de la lecture », pas validité économique, applicabilité DCE ou conformité. Une publication différente donne REVIEW_REQUIRED dans cette seule observation ; une référence non vérifiable reste UNKNOWN. CANDIDATURE_ONLY donne NOT_APPLICABLE sans exposer de rapport financier. L’ancienne API sans ce champ est affichée UNKNOWN par le client.

L’observation est strictement en lecture : manifeste/hash, export, registre P5, décision et source C10 restent inchangés. Une publication révisée n’est pas une nouvelle autorisation. L’ancien P5 reste l’acte de l’ancien pli exact, sans accord déduit sur le nouveau chiffrage ; ses contrôles historiques restent ceux des portes natives. Le nouveau candidat doit recevoir son propre P5 exact. Aucune pièce financière n’est automatiquement copiée dans le mémoire ou le ZIP.

Une seconde correction bornée concerne la revue C10 : une note rejetée par la validation de commande produisait un HTTP500 lors de sa conversion. Elle est maintenant refusée 422 avec code générique `PREPARATION_REVIEW_INPUT_INVALID`, sans recopier la saisie, sans dispatch et sans effet. Le validateur FINANCIAL_DATA_FORBIDDEN, l’authentification et les contrôles du service sont conservés.

## Fichiers logiciels

- Backend : `modules/submission/application/service.py`, `application/final_control.py`, `public/final_control_contracts.py` et `interfaces/http/routes/preparation.py` sous `backend/app/`.
- Web : `web/src/shared/types.ts` et `web/src/features/submission/SubmissionFinalControl.tsx`.
- Tests : `backend/tests/application/test_submission_pricing_reference.py`, `backend/tests/db/test_l08_pricing_response_continuity.py`, `backend/tests/api/test_preparation_review_input_refusal.py`, `web/src/features/submission/SubmissionPricingReference.test.tsx`.

Dix fichiers logiciels ; aucun schéma, migration, dépendance, moteur, calcul financier ou contrat d’entrée P5 changé. Le champ de sortie est additif ; aucune référence privée nouvelle dans le manifeste ou le ZIP.

## Parcours natif qualifié

Une même Affaire et un même DCE synthétique : import Excel V1, relecture des cellules/feuilles, application unique au brouillon, coût déclaré et publication, préparation/réponse sourcée/annexes, revue, snapshot, transmission, décision conditionnelle et P5 synthétiques, ZIP exact. Les manques et la validité inconnue des pièces restent visibles.

Un nouvel Excel est ensuite importé, commité/rejoué sans double ligne, complété par une hypothèse de coût puis publié dans un nouveau rapport. L’ancien contrôle conserve son rapport lié et son P5, mais distingue le dernier rapport publié. Le même brouillon ne peut pas recevoir une seconde revue (`REVIEW_ALREADY_EXISTS`) : aucun garde assoupli. Une nouvelle réponse non financière et sourcée est créée avec toutes les paires exactes du plan ; nouvelle revue Patron, nouveau snapshot et nouvelle transmission. Le candidat FULL reconstruit référence la nouvelle publication et les nouveaux actes C10. Avant son P5, export refusé ; ancien hash présenté au nouvel acte refusé ; nouveau P5 motivé et retry identique acceptés. ZIP relu, hash du manifest.json égal au registre, entrée de prix liée au nouveau rapport, exigences manquantes et signatures/conformité UNKNOWN conservées.

Le prix publié est une **référence sans fichier exporté**, toujours visible dans `entries_without_exported_file`. La pièce Excel n’est pas dans le ZIP, les montants privés non plus : aucune offre financière complète n’est démontrée. Le Collaborateur du parcours partagé n’accède pas au contrôle final Patron. Les commentaires de revue C10 restent non financiers ; le contexte économique appartient aux surfaces privées autorisées et à l’acte P5 approprié.

Frontière de source : le DCE V1 part d’une fixture déjà admise/classifiée, dans une copie de développement enrichie d’une attestation synthétique et avec hash de manifeste actualisé. Pas de nouveau réimport DCE, d’OCR exhaustif ou de DOCX dans cette tranche ; les preuves précédentes restent datées. Les deux générations de prix utilisent réellement les routes natives d’import/commit/publication. Le resolver d’identité du parcours partagé est synthétique ; aucune nouvelle preuve de login JWT réel de bout en bout n’est revendiquée.

## TDD, revue et essais intermédiaires

Rouges observés : champ de filiation absent dans le service, deux affichages UI absents, TypeError sur `entries: null` avec hash cohérent, et HTTP500 sur note de revue financière interdite. Les deux derniers cas ont été reproduits après revue/investigation, puis corrigés : le refus d’intégrité contrôlé existant demeure propriétaire de la validation structurelle, et la conversion de commande refuse l’entrée invalide avant écriture.

Les échecs de recettes restent distingués des bugs produit : attestation absente de la fixture d’assemblage, marqueur de fixture trop long puis identifiant fonctionnel dupliqué, tentative de re-revue du même brouillon refusée correctement, contributions ne couvrant pas toutes les paires exactes du plan. Ils ont été corrigés dans la copie de développement ou le scénario de test ; aucun corpus de référence ni validateur métier assoupli. La note interdite a aussi révélé le véritable défaut de traduction HTTP500, corrigé et désormais vérifié avec absence de dispatch/écho de montant.

Revue indépendante en lecture seule : défaut d’ordre de validation des entrées du manifeste relevé puis corrigé, contre-revue sans autre finding concret sur les dix fichiers. Nouvelle traduction HTTP examinée : bloc limité au constructeur, service et refus financier inchangés. Une revue statique ne vaut pas validation humaine ou test supplémentaire.

## Vérifications exécutées

- Service de référence initial : 1 réussite après le rouge. Campagne intermédiaire source/recette : 5 réussites en111,10 s après correction du scénario.
- Backend final : **109 réussites en108,91 s**, sur référence financière, contrôle final, paquet/préparation/P5/export, contrats de source, décision et parcours natif révisé. Routes de revue et régression HTTP : **29 réussites en7,35 s**. Nouveau prix d’une autre Affaire ignoré ; candidature seule sans référence exposée ; malformed-manifest refusé ; contrôles tenant/rôle/MFA/idempotence et append-only des suites natives conservés.
- Web global final sur gel : **784 réussites,4 ignorés,93 fichiers,209,31 s,exit0**. Dix SHA logiciels inchangés après la suite.
- Web ciblé final : **46 réussites en9,47 s**, quatre fichiers Submission. États chiffrage révisé/courant/candidature seule/ancienne réponse UNKNOWN séparés de P5 et de la conformité ; hooks de contrôle, signatures et intentions existants exécutés.
- Types Web, lint et build verts. Mypy application708 fichiers verts ; application/tests206 diagnostics dans40 fichiers sur1271 sources, identiques à L07 après normalisation des numéros de ligne. Ruff/format des sept fichiers Python verts ; Alembic inchangé `20261102_0147`, fixtures upgrade/downgrade jusqu’à base.
- Semgrep1.183.0, `p/security-audit`, métriques désactivées :99 règles sur10 fichiers,0 finding/0 erreur, sans transmission de résultat. Detector Impeccable `[]` ; scan borné des lignes ajoutées sans secret reconnu. Ni l’un ni l’autre ne certifie la sécurité globale.
- Chrome DevTools Local : composant réel sur projections natives enregistrées, relecture simulée sans écriture métier ; ancienne référence REVIEW_REQUIRED et nouvelle référence CURRENT avec P5 distinct observées à1280/393px. Quatre captures inspectées, pas de débordement global, cookies/stockages vides, aucune ressource externe. Un premier essai attendait un texte dans un détail replié ; le harnais ouvre le détail avant assertion, sans changement produit. Pas Playwright, pas nouvelle preuve d’écriture UI/P5 ou d’authentification réelle, pas audit WCAG complet.
- OpenDesign Local Codex : catalogue courant/artefact SMART AO existant consultés, styles et composants du dépôt conservés ; référence Linear complémentaire seulement, autorité Owner/CYTD inchangée. Impeccable contexte/craft-floor/harden puis detector ; aucune génération Cloud ou nouveau prototype nécessaire à cet ajout borné.
- Dix SHA logiciels figés et relus. Base jetable propre :0 table métier/0 révision Alembic ; conteneur exact `6e998c7554def4c61c6accf28c369b23169d9202ba09fff576dd99e2d2288bc4`, sans montage persistant, supprimé. Clients navigateur et preview dédiés fermés, services préexistants conservés.

## Invariants et limites

Tenant/Affaire/PUBLISHED bornent les deux lectures. La garde Patron/FINANCIAL_PRIVATE et le no-store du contrôle final restent existants ; aucune nouvelle permission. Les IDs/révisions ne deviennent pas montants, prix fiables, source externe authentifiée ou preuve de remise. Actualité financière et actualité C10 restent deux observations distinctes, sans promotion de porte.

Une nouvelle publication externe peut nécessiter une relecture ; pas de surveillance continue ajoutée. Les intentions UI restent en RAM. Les garanties de prix/validité, complétude documentaire et financière, signatures et dépôt restent UNKNOWN ou non effectués ; L08 général PARTIAL. Aucun candidat activé, P3 réel, GO public, commit, push, live, corpus réel, VPS, déploiement ou effet externe.

Méthode : Superpowers cadrage/plan/TDD/debugging/revue/vérification ; ECC product-capability, security-review et verification-loop ; Graphify avant recherche, Serena activée/navigation symbolique, OpenDesign Local Codex, Impeccable, Chrome DevTools Local et Basic Memory. Context7 sans question de bibliothèque nouvelle ; Jev/Manus sans gain sur ce périmètre borné. Le miroir Basic Memory est synchronisé après consolidation finale du plan.
