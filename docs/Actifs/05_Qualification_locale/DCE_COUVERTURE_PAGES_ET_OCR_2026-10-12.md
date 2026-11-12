# Essais DCE — couverture page par page — 12 octobre 2026

## Résultat

**Qualification exécutée; extraction complète NON DÉMONTRÉE.** Deux PDF : CCTP commun DCE-03 (44 pages), RC DCE-04 (21 pages). Toutes les65pages sont rendues et traitées par OCR local, sans promotion de leurs statuts.

Les13supports pilotes sont retrouvés exactement dans le texte natif sur leur page physique;9citations sont aussi reproduites exactement par OCR. Quatre écarts OCR : formulation du délai24h, ponctuation du délai de réponse, confusion chiffre0/lettreo dans le délai de modification et les heures d’insertion. Un écart typographique n’est pas une erreur de valeur; les confusions numériques sont un risque matériel. Le texte natif exact n’est pas remplacé par l’OCR.

**A1 non admis; A2 générique HOLD; NO-GO public.** Aucun backend live, import métier, VPS, déploiement, push, P3 ou dépôt externe. Aucun acte humain simulé. Corpus, citations, images, champs administratifs et résultats OCR restent hors Git.

## AS-IS, risques, insertion, plan

- AS-IS : deux sources natives `REVIEW_REQUIRED/PDF_LARGE_IMAGE_REVIEW_REQUIRED`,13points exclus de l’analyse admissible.
- Risques : prendre un en-tête pour tout le contenu; confondre surface cumulée et grande image isolée; changer une valeur exacte par OCR; prendre du texte de logigramme pour ses relations ou un formulaire exemple pour un engagement réel.
- Insertion : adaptateurs et comparateur existants, scripts de preuve privés; aucun code produit, dépendance, migration ou configuration modifié.
- Plan exécuté : SHA des sources; inventaire/rendus des65pages; inspection des mises en page et annexes; OCR local borné; relecture hashes/pages/bbox; requalification13points puis mesure50inchangée; tests existants et calibration synthétique réelle; plan/mémoire.

Checkout principal `/home/noor/PROJECTS/BTP/SMART_AO_V8`, branche `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`. Worktree exploratoire `codex/dce-page-coverage-20261012` :24fichiers WIP hérités à hashes identiques, aucune correction intégrée. L’hypothèse initiale d’un saut OCR sur page avec en-tête est réfutée par le code et la calibration : l’adaptateur PDF rend déjà toutes les pages. La condition de grande image du natif reste conservative et inchangée.

## Preuve page par page

| Source | Pages | Traitement | Éligibilité |
|---|---:|---|---|
| DCE-03, CCTP commun |44|44renders et44projections OCR candidats avec page physique/hash/région|REVIEW_REQUIRED maintenu|
| DCE-04, RC |21|21renders et21projections OCR candidats avec page physique/hash/région|REVIEW_REQUIRED maintenu|

4202fragments OCR candidats, environ489,82s de traitement cumulé. RapidOCR3.9.2/ONNXRuntime1.29.0/PyMuPDF1.28.2, modèles installés explicitement désignés et hachés; dictionnaire issu des métadonnées du modèle installé. Modèles réellement exécutés, aucun faux moteur pour les documents réels.

Chaque page a : alias, SHA-256 PDF, numéro physique, SHA-256 du render150DPI, fragments et boîtes pixels bornées, état REVIEW_REQUIRED. L’OCR est appliqué à l’image complète de chaque page; sa page-image locale1 est conservée séparément du numéro physique PDF, relié par le render déterministe vérifié. Ce lien de preuve privée ne devient pas une source métier automatiquement admise.

Limites appliquées :200pages/document,25millions pixels/page,250millions pixels/document; traitement total limité900s. CPU threads1, réseau interdit par sandbox et hook socket, modèles locaux seulement, télémétrie/offline activés pour la preuve; flags produit OCR/Docling inchangés.

DCE-03 : formulaires et logigrammes des annexes30–43. Des pages raster ont seulement un en-tête/titre natif; l’OCR retrouve des libellés supplémentaires, notamment contrôle amiante du CRI33, ordre de service35, audit41 et critères/mentions des logigrammes42–43. Les boîtes/coches, cellules, liens entre branches et règles d’éligibilité ne sont pas qualifiés par cette récupération de texte. Les exemples administratifs ne deviennent pas des faits du chantier.

DCE-04 : plusieurs petites images, surface cumulée au seuil sur page4 (environ25,1%); absence de grande image isolée ne vaut pas absence d’images. Les tableaux de notation16–18, graphismes et textes natifs sont visibles dans la revue locale. Une preview et un OCR ne prouvent pas toutes les cellules/relations. Aucun relèvement automatique du statut.

## Requalification et conservation

| Mesure | Résultat |
|---|---:|
| Pages OCR avec texte candidat |65/65|
| Renders/SHA/pages/bbox revérifiés |65/65|
| Citations natives exactes des13points |13/13|
| Citations OCR identiques, comparateur strict existant |9/13|
| Points promus/admis |0|
| SOURCE_NOT_ELIGIBLE conservés |13/13|

La mesure des50points est rejouée sans override de source :18SIGNAL_SUPPORTED,19NO_TARGET_RULE_IN_RC_REGISTER,13SOURCE_NOT_ELIGIBLE,0omission ciblée du registre admissible. Identité complète avec la mesure v4 précédente vérifiée; aucun comparateur assoupli, aucun ledger ou projection antérieur écrasé. Les13points possèdent une requalification distincte avec source/page/render, support natif/OCR et `document_eligibility=NOT_GRANTED`. Valeurs normalisées, structure sémantique et applicabilité lot demeurent non qualifiées/UNKNOWN.

## Contrôles et limites

-17tests existants couverture PDF/adaptateurs réussis,0,95s; gardes image/blank page/texte non extrait et REVIEW_REQUIRED inchangés.
-Calibration **réelle** PDF synthétique texte natif+image : les deux textes sont reconnus, page1 exacte, statut REVIEW_REQUIRED. Aucune régression à corriger constatée dans ce parcours.
-Assertions de preuve :65renders déterministes, pages exhaustives, régions dans limites, sources immuables,13citations natives, absence de promotion et50résultats identiques.
-Aucun code logiciel modifié : TDD correctif/Semgrep non applicables à ce livrable documentaire. Suite globale2301/2301,couverture87,99% est celle de la tranche précédente, sur le même code vérifié inchangé; pas relancée ici. Aucun nouveau GO déduit.
-Méthode : Superpowers using-superpowers/brainstorming borné/systematic-debugging, ECC verification-loop adapté à la qualification, skill PDF; Graphify, Context7 pour les images réellement affichées, Basic Memory miroir. Serena sémantique/Jev/Manus/OpenDesign non nécessaires pour cette revue locale sans code ni UI.

Preuves privées : `/home/noor/.local/share/smartao-proofs/dce-page-coverage-20261012/` :65JSON de pages, deux ledgers OCR, hashes modèles, inventaires et sheets, `page-qualification-ledger.json`, `thirteen-point-requalification.json`, mesure50inchangée, calibration et journaux. Le contenu privé n’est pas recopié ici.

La barrière utile est conservée : un document comportant des obligations dans une image ou une structure non qualifiée ne devient pas analysé parce que ses citations pilotes sont lisibles. La prochaine preuve doit qualifier les champs/cellules/relations et conserver les inconnus.

Prochaine étape : ESSAIS DCE — qualifier les champs, cellules et relations des annexes raster des pages 30–43 de DCE-03 et des graphiques de DCE-04, avec ancres de région et UNKNOWN explicites, avant toute levée de REVIEW_REQUIRED. A1 non admis, A2 générique HOLD et NO-GO public maintenus.

Clôture documentaire :5tests d’autorité/head réussis après mise à jour, liens du rapport/index vérifiés, diff-check vert; plan et miroir Basic Memory relus avec prochaine étape exacte. Aucun fichier logiciel ni modèle modifié, aucun commit/push.
