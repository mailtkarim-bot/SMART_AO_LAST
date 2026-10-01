# PUX-07 — Audit et cadrage de la comparaison des offres C08/C09

**Date :** 30 septembre 2026  
**Statut :** cadrage d’exécution locale ; aucune ouverture publique  
**Autorités :** Product Freeze métier v2.0 ; Catalogue écrans/parcours v0.3

## CAPABILITY

Permettre au Patron de consulter dans C08 les montants explicitement déclarés dans les offres reçues des partenaires d’une Affaire, côte à côte avec leur périmètre, exclusions, validité et événement de réception C09/locator déclaré. La comparaison aide une revue humaine ; elle ne calcule pas la couverture d’un besoin, ne sélectionne pas un partenaire, ne déclare aucun engagement et ne fait pas avancer P3.

## AS-IS — code vérifié

- **C09 partenaire :** `CasePartnerEventRecord` conserve le type de partenaire, l’événement `RECEIVED`, un locator texte, la validité, l’état des exclusions et le mandat. Il n’existe ni montant ni référence typée à une version de document C06. Le panneau C09 sépare le reçu et l’acte Patron d’engagement.
- **Pièces C06 :** le stockage/versionnement consulté est rattaché aux documents d’un DCE (`DceDocumentRecord` → `DceVersionRecord`). Aucun registre générique de version de document d’offre partenaire n’a été trouvé. Un devis fournisseur ne doit donc pas être artificiellement traité comme une pièce du DCE acheteur.
- **C08 import :** `PricingImportBatchRecord` accepte `DPGF`, `BPU` ou `EXCEL`, garde l’empreinte SHA-256 et les lignes normalisées. Il ne porte aucun `partner_id`, reçu C09 ou identifiant de version du document source. `PricingImportRowRecord` porte unité, quantité, prix unitaire et total, mais pas de devise.
- **Effet de l’import C08 :** le batch validé est appliqué à un brouillon financier de l’Affaire. Ce chemin ne peut pas être repris tel quel pour comparer des offres : une offre partenaire serait confondue avec les lignes de prix du dossier.
- **Scénarios financiers :** `PricingScenarioRecord` calcule ventes, coûts et marge à partir d’un snapshot financier publié. Le service de lecture/écriture est aujourd’hui limité à `PATRON_ADMIN` et les montants sont classés `FINANCIAL_PRIVATE`.
- **UX :** C08 importe dans le brouillon et présente des scénarios. `PartnerOfferPricesPanel` compare désormais totaux et périmètres par reçu ; il n’existe toujours aucun rapprochement poste par poste. PAR-02 place le comparatif dans C08/C09, avec périmètre constant, exclusions, transport, validité et ajustements à reconfirmer lors d’une révision.

## RISQUES ET CONTRAINTES FIXES

1. **Séparation des données :** aucun montant d’offre, total, indicateur de prix ou existence d’une analyse financière ne doit apparaître dans l’API ou la projection C09 destinée aux Collaborateurs. Les événements partenaire opérationnels ne deviennent pas financiers.
2. **Confidentialité :** le premier parcours de comparaison reste Patron Admin uniquement, conformément aux services financiers actuels. Profil opérationnel, affectation d’Affaire ou droit de lecture C09 n’accordent pas l’accès aux montants. Une extension DAF/délégation exigerait une capacité financière explicite et des tests de non-divulgation.
3. **Provenance :** chaque montant doit référencer l’événement C09 `RECEIVED` exact (tenant/Affaire/partenaire) et reprendre son locator immuable côté serveur ; le client ne peut substituer ni le partenaire ni la source. Ce locator est une référence déclarée, pas une empreinte du fichier. Le code n’offre pas aujourd’hui de version générique de pièce partenaire ; une empreinte de fichier reste `UNKNOWN` tant qu’un chemin de preuve contrôlé ne la fournit pas. Une nouvelle offre crée une nouvelle version financière ; l’ancienne reste historique et ne change pas silencieusement.
4. **Inconnus :** prix absent, devise absente, total absent ou périmètre incertain restent `UNKNOWN`/non renseignés ; jamais zéro. Ne pas convertir de devise, reconstruire un total de lignes, inférer le transport/la TVA, ni déclarer deux périmètres équivalents.
5. **Aucune décision induite :** le comparatif n’est ni un classement, ni une recommandation de choix, ni une preuve d’engagement. L’acte C09 d’engagement reste distinct. Aucun score, coût couvert, marge, P3 ou GO n’est calculé ou modifié.

## CONTRAT D’IMPLÉMENTATION MINIMAL

- **Propriétaire des montants :** contexte `pricing` / C08, classé `FINANCIAL_PRIVATE`. C09 conserve seulement l’identité partenaire, son reçu et ses sources opérationnelles.
- **Unité de preuve :** snapshot financier d’offre relié par FK au tenant, à l’Affaire et à l’événement C09 `RECEIVED` exact ; identité et locator de source sont copiés côté serveur depuis cet événement. Conserver acteur, date de saisie et révision. Ne pas inventer de `source_sha256` ni de version C06 pour un locator texte ; la liaison future à une pièce/hash générique est un besoin distinct.
- **Donnée initiale :** montant total tel qu’explicitement porté par la source, devise explicite et courte déclaration de périmètre/inclusions/exclusions. Le total reste optionnel ; son absence produit un état inconnu visible. Les lignes détaillées, rapprochements besoin↔prix et ajustements sont hors de cette première tranche.
- **Lecture :** écran/tableau comparatif dans C08 ; chaque colonne reste attachée à un partenaire et à une version source. Afficher côte à côte les valeurs déclarées et les inconnus, sans total agrégé ni ordre de préférence. La validité et les exclusions sont projetées depuis le reçu C09 référencé, sans duplication mutable.
- **Écriture/version :** saisie Patron explicite, idempotente et tenant/Affaire-scopée. Le handler vérifie que le reçu référencé est bien `RECEIVED` pour cette Affaire et ce partenaire ; la source et le partenaire ne viennent pas du corps client. Un nouvel acte de réception ou une offre révisée produit un nouveau snapshot ; aucune ligne antérieure n’est écrasée. L’ajustement interne n’est pas traité comme un prix fournisseur.
- **Transport/API :** routes financières C08 uniquement. Ne pas ajouter de champs financiers aux contrats C09, à la navigation générale, aux compteurs, notifications, événements accessibles aux Collaborateurs ou exports non financiers.
- **Réutilisation technique :** l’analyse XLSX C08 existante peut être réutilisée seulement comme parseur/preview après vérification du contrat. Son commit dans le brouillon financier ne doit jamais être appelé pour une offre partenaire. Aucun nouveau package n’est justifié.

## HORS PÉRIMÈTRE

- calcul ou validation automatique d’un total, d’une équivalence de périmètre, du coût couvert, de la marge ou du cash ;
- classement, sélection, acceptation, engagement, mandat légal ou mise à jour d’une porte P0–P7 ;
- import PDF/OCR/LLM, conversion de devise, rapprochement DPGF détaillé, TVA/transport implicites ;
- accès Collaborateur, DAF ou délégué financier avant définition et test d’une capacité distincte ;
- ouverture publique ou modification du GO/NO-GO public.

## PREUVES ET LIMITES DE LA PREMIÈRE TRANCHE

- **Prouvé :** le Patron consulte dans C08 chaque reçu partenaire, locator, périmètre déclaré, validité/exclusions et déclarations de total/devise. Prix/devise absents restent `UNKNOWN`; le texte lexical saisi est conservé, sans conversion ni addition.
- **Prouvé :** montant réservé à Patron Admin par `FINANCIAL_PRIVATE`; aucun champ financier dans le contrat C09 ; refus Collaborateur/tenant/Affaire, reçu C09 `RECEIVED` exact, version courante exigée, idempotence et historique append-only ; PostgreSQL rejette aussi reçu ancien, UPDATE et DELETE.
- **Prouvé :** scénario HTTP/API/PostgreSQL et panneau C08 testés ; si résultat d’écriture inconnu, retry reprend les mêmes identifiants. L’API C09 demeure inchangée par les montants.
- **Limite explicite :** le locator vient du reçu C09, mais aucune pièce partenaire générique versionnée/hashée par C06 n’existe dans le modèle audité ; l’empreinte de fichier est affichée `UNKNOWN`. Le locator n’est donc pas présenté comme preuve d’intégrité du fichier.
- **Revue humaine de périmètre livrée :** dans C08, le Patron choisit au moins deux reçus courants et consigne par reçu le périmètre inclus, la relecture explicite des exclusions déclarées et le traitement du transport. Il choisit `SAME_SCOPE_CONFIRMED`, `DIFFERENT_SCOPE` ou `NEEDS_CLARIFICATION` avec un motif. `SAME_SCOPE_CONFIRMED` est refusé si une inclusion, une liste d’exclusions ou le transport est inconnu/non relu. L’acte n’altère ni le reçu ni les exclusions C09.
- **Encore partiel :** aucun rapprochement poste par poste, TVA, frais, coût couvert, marge, classement, engagement ou progression P3 n’est calculé. Une revue `SAME_SCOPE_CONFIRMED` est une décision humaine bornée aux faits déclarés et à leurs locators ; elle n’est ni une preuve d’intégrité de fichier ni une validation du montant.

Implémentation prix : migration additive `20260930_0119`; lecture/écriture `GET/POST /api/v1/patron/cases/{case_id}/partner-offer-prices...`; table `partner_offer_price_declarations`; le texte du total et le code devise sont conservés tels que saisis. Pas de somme recalculée.

Implémentation revue : migration additive `20260930_0120`; tables `partner_offer_scope_reviews` et `partner_offer_scope_review_offers`, FK composites tenant/Affaire/reçu C09 exact, déclencheurs PostgreSQL append-only et contrôle différé du nombre/membership des reçus courants. `GET/POST /api/v1/patron/cases/{case_id}/partner-offer-scope-reviews`, Patron Admin/`FINANCIAL_PRIVATE`, projection C08 sans montant. Les révisions gardent la même comparaison et le même ensemble de reçus ; un reçu remplacé marque l’historique `REVIEW_REQUIRED` sans le réécrire. L’empreinte partenaire reste `UNKNOWN`.

Vérification de la tranche revue : tests backend C08/C09 ciblés **62/62**, avec PostgreSQL jetable en tmpfs, incluant migration, décision inconnue, validation des exclusions relues, isolation inter-tenant, idempotence, révision append-only, reçu obsolète, API C09 et contrat ops ; avertissement Starlette/httpx. Frontend ciblé C08/API **37/37**, typecheck, lint et build verts ; Ruff/mypy ciblés propres ; tête Alembic unique `20260930_0120`. Le build affiche un chunk principal de **519,66 kB** (>500 kB). La suite complète backend et frontend n’a pas été rejouée pour cette tranche. Pas de commit ni push. Basic Memory n’était pas exposé comme outil dans cette session ; synchronisation non confirmée.

## AUDIT ET CADRAGE — RAPPROCHEMENT HUMAIN PAR POSTE SOURCE

**Autorités consultées :** Product Freeze métier v2.0 §9.3, §11 et règles de confidentialité ; catalogue C08 §PRI-01/PRI-02 et PAR-02 ; cahier directeur métier master v2.0 §R09 et §11 « Offres partenaires ». Le catalogue demande une comparaison tracée des offres partenaires ; R09 prévoit une relation besoin↔plusieurs postes et plusieurs-à-plusieurs sans métré généralisé, et interdit de convertir un silence ou une quantité inconnue en couverture.

### AS-IS vérifié

- C09 porte un événement `RECEIVED` append-only avec tenant, Affaire, partenaire, locator textuel, exclusions, validité et mandat. Il n’enregistre ni pièce binaire ni locator par ligne ; le hash de la pièce partenaire reste `UNKNOWN`.
- C08 `PartnerOfferPriceDeclarationRecord` conserve seulement un total textuel, une devise déclarée, le reçu C09 exact, acteur et révision. La revue de périmètre `20260930_0120` conserve la décision humaine par reçu, l’inclusion, la relecture des exclusions et le transport. Aucun des deux objets ne possède de ligne partenaire.
- L’import C08 sait lire code/désignation/unité/quantité/prix unitaire/total à partir de la feuille active XLSX. Il conserve l’empreinte et le numéro de ligne du classeur normalisé, mais pas le binaire; il ne porte ni `partner_id`, ni reçu C09, ni locator source partenaire. Son commit applique ses lignes comme `SALES` au brouillon financier. Le brancher directement sur le comparatif partenaire confondrait cadre acheteur et devis partenaire, et pourrait créer un effet financier indu.
- Le panneau C08 actuel compare les totaux déclarés et le périmètre par reçu ; il n’importe ni n’associe des lignes, et ne calcule pas de couverture.

### RISQUES

Une jointure automatique par code, libellé, unité ou quantité pourrait relier deux prestations différentes ; normaliser unité, libellé ou quantité masquerait l’écart déclaré ; utiliser un numéro de ligne sans son locator et le reçu source rendrait la provenance ambiguë. Réutiliser le commit de l’import créerait des lignes de vente dans le rapport financier. Toute nouvelle vue doit rester `FINANCIAL_PRIVATE` et Patron Admin au premier incrément ; les données de prix et les actes financiers restent absents de C09.

### CONTRAT MINIMAL CADRÉ POUR L’IMPLÉMENTATION

- Ajouter dans le contexte `pricing` un acte C08 tenant/Affaire-scopé de **rapprochement manuel**, rattaché à une révision exacte d’une revue de périmètre C08 et à au moins deux reçus C09 `RECEIVED` courants appartenant à des partenaires distincts. Le serveur copie partenaire, reçu et locator C09 ; le client ne peut fournir leur identité de substitution.
- Un groupe de rapprochement est créé par l’utilisateur, jamais par similarité automatique. Chaque membre conserve le reçu exact, un localisateur de ligne déclaré par l’humain (feuille/ligne, page/repère, ou `UNKNOWN`), puis séparément les états `UNKNOWN`/`DECLARED` pour référence/code article, désignation, unité et quantité. Valeurs déclarées stockées en texte source sans conversion, arrondi, normalisation ni calcul ; l’absence demeure `UNKNOWN`.
- Chaque groupe porte une qualification humaine fermée `LINKED_BY_PATRON`, `DISTINCT_POSITIONS` ou `NEEDS_CLARIFICATION`, avec motif obligatoire. `LINKED_BY_PATRON` signifie uniquement que le Patron a relié ces positions pour les examiner ensemble ; cela ne confirme ni équivalence technique, ni couverture d’un besoin, ni prix comparable. Les inconnus par membre restent affichés même si un groupe est relié.
- Les actes sont idempotents, append-only et révisables avec révision attendue. Chaque révision garde les mêmes reçus et identifiants de ligne ; remplacer un reçu ou réviser la revue de périmètre rend les groupes dépendants `REVIEW_REQUIRED` en projection, sans réécriture. C09 reste inchangé.
- La projection C08 présente les membres côte à côte avec leurs valeurs brutes, locators, auteur/date, décision humaine, état de source et inconnus. Aucun champ de montant, devise, prix unitaire, quantité recalculée, agrégat, classement, coût couvert, marge, engagement ni porte P3 n’est introduit dans cet acte.

### POINTS D’INSERTION ET PLAN MINIMAL

1. Domaine/commande sous `backend/app/modules/pricing`, tables additives dédiées au rapprochement et aux membres, FK composites tenant/Affaire/reçu/revue exacte, contraintes de statut et déclencheurs append-only.
2. Routes Patron C08 `GET/POST`, autorisation réutilisant la politique `FINANCIAL_PRIVATE`, `PartnerOfferPricesPanel` étendu par un formulaire de saisie manuelle par reçu et une liste de groupes/historique. Ne pas détourner `PricingImportService` ni son commit.
3. Tests domaine/API/PostgreSQL : liste partielle/inconnue, reçus étrangers ou remplacés, membre dupliqué, revue source absente/obsolète, conflit de révision, retry idempotent, update/delete refusés, refus Collaborateur et absence de champs monétaires. Tests frontend : aucun groupe créé sans acte du Patron, inconnus lisibles, locators visibles, révision historique conservée et aucun coût/GO déduit.

**Handoff :** contrat prêt pour implémentation directe comme prochaine tranche C08. Aucune dépendance ou clarification propriétaire n’est nécessaire pour ce périmètre borné. PUX-07 demeure `PARTIAL` ; hash générique partenaire, import fiable de pièce source, rapprochement des besoins/coûts, calcul de couverture et P3 restent en dehors de ce bloc.
