# L06 — bordereau multi-feuilles vers brouillon financier — 23 octobre 2026

## Fonction et autorités

Patron habilité : charger un classeur tabulaire compatible, consulter toutes les lignes et leurs sources, relire l’aperçu enregistré puis appliquer une fois les lignes au brouillon de la même Affaire. Ce parcours est une livraison interne à L06; il ne constitue pas un chiffrage complet ni une preuve de coût couvert.

Autorités : PF31-03/06/08/09, M31-03 étapes3–4, M2-026 axes6/9 et M2-027; CT31-02/03/06; famille F18 de la matrice existante. Direction Owner22–23/10 : [réalignement fonctionnel](../00_Pilotage_et_audits/REALIGNEMENT_FONCTIONNEL_2026-10-22.md). Le plan global porte seul statut/prochaine étape.

## AS-IS, risques, insertion, plan exécuté

Avant : aperçu sur l’onglet actif seulement; quantité absente remplacée par1; formules masquées par `data_only`; total fourni invalide susceptible de recalcul; prévisualisation limitée montrée sans contrôle systématique avant persistance. UI : cinq premières lignes seulement. Source de cellule perdue après aperçu. Le parcours financier natif et ses contrôles tenant/Patron/idempotence/révision existaient déjà.

Risques : postes omis, montants faux, origine perdue, aperçu partiel committable, effets doubles, données privées exposées. Insertion : parser/commandes/lecteurs/route/imports pricing existants; colonne JSON nullable par migration0140; panneau de prix existant. Aucune nouvelle dépendance, moteur actif, porte ou droit ajouté.

- [x] Régressions rouges observées : multi-feuilles, quantité/formule, troncature terminale, feuille non reconnue, en-tête ambigu; puis montants fournis invalides, dépassements BigInteger, formules matricielles, prix sous-centime et dimensions XLSX fausses.
- [x] Parser, source persistée, lecture HTTP et application/retry qualifiés sur PostgreSQL synthétique.
- [x] UI : toutes les lignes par pages20, tableau Poste/Source/État, sources et erreurs lisibles; tests rouges puis verts.
- [x] Suite backend globale finale, scans finaux et nettoyage de toutes les bases avant clôture locale.
- [x] Journal/case du plan, index/fiche/CSV et miroir Basic Memory finalisés après résultat final.

## Code et contrats

`pricing/application/import_preview.py` lit toutes les feuilles tabulaires compatibles. Les dimensions déclarées par le producteur sont réinitialisées pour ne pas couper les lignes réelles; budgets explicites32feuilles/10000lignes/256colonnes/100erreurs et limites ZIP/upload antérieures conservées. Feuille non vide non reconnue, structure ambiguë ou limite : refus, jamais promotion silencieuse des autres lignes.

Les formules sont détectées par `cell.data_type`, y compris ArrayFormula/DataTableFormula; aucune représentation d’objet Python n’est une désignation. Les formules ne sont pas exécutées ni leur cache considéré frais. Quantité absente : UNKNOWN/erreur, pas1. Montant fourni invalide : erreur, pas substitution par un calcul. Ligne et somme bornées au BigInteger; longueurs compatibles avec la persistance. XML malformé : refus contrôlé.

Le prix unitaire natif est stocké en unités mineures entières. L’arrondi commercial historique sur une quantité explicitement égale à1 est conservé; les fractions d’unité mineure pour une quantité différente sont refusées plutôt qu’arrondies avant multiplication. Ceci ne qualifie pas les prix unitaires BTP à précision étendue. Aucun devis ou coût couvert déduit de ces montants.

`source_locator` porte feuille, ligne physique et cellules des champs reconnus; le numéro de ligne normalisée est distinct pour éviter les collisions entre feuilles. Le nom de feuille ne devient pas une portée lot. Le SHA du fichier reste privé dans le batch selon le contrat antérieur; aucun nouveau hash exposé par la lecture publique. Les projections historiques sans source restent acceptées et lisibles en UNKNOWN. Le champ optionnel absent ne modifie pas les hashes de retry historiques.

Création : un aperçu tronqué est refusé avant toute persistance. Commit : handlers et verrous/idempotence/révisions existants conservés. Migration `20261022_0140` : colonne nullable, sans backfill; SQLNULL et JSONnull ne prouvent aucune source; downgrade refusé si une vraie provenance serait perdue. Tête runtime et runbook réconciliés, aucune migration live.

Fichiers : parser, commandes, handler de création, projections/lecteur SQL, modèle financier, contrats publics, route native; schéma runtime/migration; tests parseur/API/SQL/migration; types client et PricingPanel. Dix-huit fichiers de code/tests suivis dans les preuves privées.

## Preuves observées — qualification locale clôturée

Racine privée : `~/.local/share/smartao-proofs/realign-metier-20261022/`.

- **103 tests financiers/API finaux réussis** (`financial-final-green.log`), dont17cas parseur et deux scénarios de migration. Aperçu→persistance→relecture→brouillon, retry sans double effet, refus financiers et compatibilité des anciennes projections couverts. Les118ciblés antérieurs incluaient d’autres contrats, sont recouvrants et ne s’additionnent pas à ces103.
- **Backend global final3830réussites/0ignoré/1warninghistorique/1117,36s/exit0** (`backend-global-final.log`). Avertissement Starlette/httpx conservé. Dix-huit hashes de code/tests stables après cette suite; aucun comportement modifié depuis son gel.
- Web global631réussites/4ignorés préexistants;74fichiers,39,80s. Types/lint/build et mypy651 verts, warning chunk>500kB conservé.
- Revue indépendante : quantité par défaut, effacement d’un montant invalide, bornes, XML différé et formules non textuelles reproduits/corrigés. Contre-revue sans autre défaut bloquant identifié dans ce différentiel. Ce n’est pas une validation métier humaine ni un audit exhaustif de tout pricing.
- Un premier global a signalé neuf régressions API sur d’anciennes projections sans `source_locator` (3817réussites/9échecs); elles sont corrigées par enrichissement optionnel UNKNOWN et les tests API concernés passent dans les103. Runs intermédiaires interrompus pour intégrer les gardes non qualifiants. Le global final3830/3830 ci-dessus remplace ces campagnes non qualifiantes.
- Deux tris d’imports après un premier lancement ont conservé l’AST normalisé; `lint-only-ast.json`. Aucun comportement backend changé après le dernier gel de18hashes.

### Navigateur local synthétique

Chrome DevTools MCP headless/isolé, routes natives via FastAPI TestClient, PostgreSQL jetable et API/session synthétiques. Pas de backend live, cookie/token utilisateur ou trafic externe. Playwright MCP absent; aucune preuve Playwright revendiquée.

Classeur de25postes/deux feuilles : toutes les positions sont affichées et accessibles; sources relues après persistance et commit. Brouillon final :25lignes,61000centimes,révision1. Onze assertions réussies, refus Collaborateur403 et masquage des données financières au changement de rôle. Desktop1440/mobile390 sans débordement racine; tableau défilant annoncé et accessible au clavier. Captures inspectées, sans certification WCAG exhaustive.

Le reçu de commit a été coupé après écriture. Chromium a automatiquement rejoué la même requête : native201 puis200/replayed, mêmes command_id/idempotency_key, aucun doublon. L’affichage UNKNOWN n’a donc pas été observé dans ce scénario; il reste couvert séparément par les tests existants du hook. Ce contrôle n’est pas présenté comme une preuve navigateur UNKNOWN.

Diagnostics conservés : un contrôle n’attendait pas le rendu React après pagination; un autre supposait l’ordre des clés JSONB des cellules. Assertions corrigées, état réconcilié avant reprise, aucun second upload/commit aveugle. La reprise finale a confirmé les effets SQL exacts. Capture réseau finale :28HTTPloopback, aucune origine externe observée; journal API navigateur sans cookie/Authorization.

Ces preuves navigateur concernent des prix en centimes entiers. Les derniers gardes de précision/dimensions et la compatibilité HTTP sont prouvés par les tests finaux ci-dessus; aucune généralisation à tout classeur ou toute devise.

### Sécurité et méthode

Semgrep1.179.0,225règles/18fichiers : une alerte `use-defused-xml` triée. Elle vise l’import de la classe d’exception ParseError, pas un appel de parser XML de ce module. Le parsing est délégué à openpyxl; environnement vérifié DEFUSEDXML=True/iterparse defusedxml. Aucune suppression de règle ni transmission des résultats; ce constat ne qualifie pas toute image/runtime de déploiement. Scan final réalisé après gel :18fichiers/1alerte triée/0erreur, aucune suppression. Secrets0 et Impeccable[] finaux. Les dernières modifications ne nécessitent aucune nouvelle dépendance.

Superpowers : cadrage/TDD/revue; ECC `product-capability`, `database-migrations`, `verification-loop`. Graphify consulté, Serena déjà activée sur le principal; Context7 et API installée openpyxl vérifiés. OpenDesign Local : catalogue/contexte existants, composants et style du panneau conservés; Impeccable contexte/craft-floor/detect et inspection bornée. Aucun besoin de Jev/Manus ou de modèle de retrieval pour ce parser financier déterministe.

## Limites et suite métier

L06 complet reste ouvert : lien obligations↔postes↔offres, coûts manquants/doubles comptes, exclusions/transport/validité, couverture et devise doivent être consolidés dans le chiffrage. Le fichier binaire original n’est toujours pas stocké par ce module d’import : hash et localisateurs ne donnent pas un téléchargement de l’original; son lien au registre DCE reste à construire. Aucun format acheteur arbitraire, prix étendu, formule Excel générale ou cas numérique non canonique exhaustivement qualifié. Une BPU sans quantité n’est pas automatiquement applicable au brouillon de ventes.

Conserver A1 non admis, A2 générique HOLD, NO-GOpublic, UNKNOWN, FINANCIAL_PRIVATE, append-only, tenant/rôle, MFA, confirmations et portes. DPGF hors RAG; aucun candidat activé, corpus réel, VPS, déploiement, effetP3, commit ou push.

## Nettoyage et suivi final

Troisbases dédiées `smartao_realign_pricing`, `smartao_realign_global`, `smartao_realign_browser` vérifiées Alembic0; conteneur tmpfs `smartao-l04-acts-pg-20261020` arrêté/exited, ACLUID70 retirée/socket700. Browser/Vite/adapter privés arrêtés. Compteurs et états conservés dans `cleanup-final.json`.

Case du sous-parcours import cochée dans le plan, prochain résultat métier de chiffrage actif; index/fiche/CSV/AGENTS et miroir Basic Memory synchronisés.45familles/14livrables et garanties,265chemins courants valides,12références périmées corrigées. Principal HEAD30f26934430095632000a1d82519f61dbb4c6411/WIP préservés; aucun stage/commit/push. Le plan conserve seul la prochaine étape exacte; L06 complet reste PARTIAL.
