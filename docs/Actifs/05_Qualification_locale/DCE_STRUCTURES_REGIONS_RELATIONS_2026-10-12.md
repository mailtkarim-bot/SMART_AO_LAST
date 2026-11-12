# Essais DCE — champs, cellules et relations — 12 octobre 2026

## Résultat

Qualification technique locale **PARTIAL / REVIEW_REQUIRED** sur21pages :14annexes raster DCE-03 (30–43),7pages graphiques/tableaux DCE-04 (4,6,13,16,17,18,21). Les régions sont tracées; la complétude structurelle n’est pas démontrée. Aucun statut documentaire levé, A1 non admis, A2 générique HOLD, NO-GO public.

## AS-IS, risques, insertion, plan

AS-IS : texte OCR candidat page/bbox présent, cellules et flèches non qualifiées. Risques : confondre voisinage et relation, perdre NON, associer mauvaise ligne/lot, prendre blanc pour zéro ou exemple pour engagement réel. Insertion : preuves privées réutilisant renders/locators existants, sans code produit/migration/permission modifiés. Plan exécuté : extraction des régions/labels, contours de grille, observations visuelles bornées, référence des relations avec UNKNOWN, vérification des ancres et gardes, documentation/mémoire.

Autorités : M2-026/027/029, PF2-035, CT31-02. Checkout principal `/home/noor/PROJECTS/BTP/SMART_AO_V8`, branche `codex/reconcile-smartao-20261009`, HEAD30f26934430095632000a1d82519f61dbb4c6411. WIP précédent préservé;24fichiers logiciels revérifiés inchangés. Corpus/renders/texte/valeurs/références demeurent hors Git.

## Registre géométrique et référence technique

| Preuve | Résultat | Autorité |
|---|---:|---|
| Pages sources traitées |21|SHA source/render et page physique vérifiés|
| Libellés OCR avec régions |1467|OCR_LABEL_CANDIDATE, pas valeur métier|
| Régions de grille |370|GRID_REGION_CANDIDATE, pas cellules sémantiques confirmées|
| Liens de containment |600|GEOMETRIC_CONTAINMENT_ONLY; semantic_state UNKNOWN|
| Références bornées lues sur source |11|8observations de champs/cellules/nœud,3flèches; technique IA non validée humain|
| Admissions ou levées de revue |0|REVIEW_REQUIRED conservé|

Les régions de grille proviennent des traits horizontaux/verticaux du render; elles peuvent être imbriquées, partielles ou chevauchantes. Aucun row/column/value n’est inventé : UNKNOWN, null et empty_means_zero=false. Les fragments qui coupent les limites sont listés comme chevauchants, sans association automatique.

Chaque enregistrement lie alias/sourceSHA/page physique/renderSHA/coordonnées pixels150DPI/identifiants de labels. Les relations références disposent d’une région couvrant leurs preuves; aucune liaison entre deux documents ou deux versions n’est autorisée par cette campagne. Provenance candidate technique, pas résolution dans une Affaire ou un tenant métier.

Les11références comprennent : champ Société, contrôle amiante, choix4h/24h, colonnes représentants, en-têtes d’un ordre d’exécution exemple, deux associations critère prix/pondération sur tableaux distincts DCE-04, nœud NON ELIGIBLE et trois branches du diagramme DCE-03. Valeurs sélectionnées, états des coches, responsabilité/signature et applicabilité à l’Affaire restent UNKNOWN. Une référence documentaire n’est ni une décision CEE ni une autorisation ou un ordre réel.

## Constats qui empêchent une promotion

- L’OCR sépare NON et ELIGIBLE dans le même nœud. Le fragment ELIGIBLE seul ne peut prouver une issue positive. La référence conserve les deux ancres et la région commune.
- Les branches OUI/NON et les flèches exigent une association au bon nœud; l’ordre des fragments OCR n’est pas l’ordre du graphe. Trois relations visuelles bornées sont référencées, sans prétendre qualifier tous les diagrammes42–43.
- Les critères et pondérations DCE-04 sont dans des tableaux à scopes documentaires distincts; pas de fusion par intitulé. La sélection du lot de l’Affaire demeure UNKNOWN.
- Cellule vide, case non résolue et champ d’exemple ne deviennent ni zéro, ni absent, ni obligation satisfaite. Les informations administratives/financières du corpus restent privées; aucune projection Collaborateur nouvelle.

Le résultat automatique demeure candidat :0cellule sémantique confirmée et0flèche confirmée automatiquement. Les11références fournissent un dossier borné pour mesurer l’implémentation ultérieure, pas un Golden humain ou une couverture exhaustive. Les13points non éligibles et le score50précédent ne sont pas promus.

## Vérifications, méthode et limites

Assertions exécutées : sources/renders exacts, pages21/21, toutes ancres présentes et dans les limites, liens pointant les labels de la même page, valeurs métier UNKNOWN et statuts REVIEW_REQUIRED. Le contrôle de containment a refusé une région trop étroite d’une référence; sa limite a été corrigée sur la source avant conservation.

Tests existants PDF/adaptateurs/comparateur :24/24 réussis. Aucun code produit modifié; pas de TDD correctif, migration ou scan Semgrep de changement produit applicable. Suite globale2301/2301/cov87,99% appartient à la tranche précédente, sur code vérifié inchangé; elle n’est pas rejouée ici.

Méthode : Superpowers using-superpowers/cadrage borné, ECC verification-loop adapté à la preuve, skill PDF et Graphify. Basic Memory miroir. OpenDesign/Impeccable inapplicables sans UI; Jev/Manus non requis, aucune délégation remplaçant la preuve visuelle. Aucune validation humaine métier/Corpus Owner/DPO.

Preuves : `/home/noor/.local/share/smartao-proofs/dce-structure-20261012/` :21registres, summary.json, technical-reference.json, scripts/assertions et détails rendus. Les images et références ne sont pas copiées dans Git.

La prochaine tranche doit transformer ces preuves en projection structurée candidate testable; les négations, scopes, cases ambiguës et relations non résolues doivent garder UNKNOWN. Aucune admission automatique des documents ou décision métier.

Prochaine étape : ESSAIS DCE — implémenter et prouver une projection structurée candidate des champs, cellules et relations sur les 11 références locales, avec négations, portée lot, ancres de région et UNKNOWN préservés, sans admission automatique des sources. A1 non admis, A2 générique HOLD et NO-GO public maintenus.
