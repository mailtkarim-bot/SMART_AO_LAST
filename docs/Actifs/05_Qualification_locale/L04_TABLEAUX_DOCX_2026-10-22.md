# L04 — prescriptions des tableaux DOCX — plan et preuves

## AS-IS, risques et insertion

Les tableaux DOCX sont refusés en bloc par l'extracteur3. Les locators publics ne connaissent que les paragraphes du corps. L'analyseur natif8 et le parcours humain complet fonctionnent sur34points multi-formats. Réutiliser ces services jusqu'à la revue/rectificatif; aucun nouveau registre, dépendance, migration, porte ou moteur candidat.

Risques : fusion/répétition de cellule, texte imbriqué ou hors corps ignoré, héritage silencieux du lot ou d'une condition, obligation artificiellement certaine, faux localisateur et transfert d'un acte après rectificatif.

## Contrat borné et plan minimal (Superpowers/ECC, exécution inline)

Support : tableaux textuels rectangulaires non fusionnés du corps. Chaque paragraphe conserve tableau/ligne/colonne/paragraphe/partie, ordre documentaire et texte exact; aucune concaténation intercellules. Structures fusionnées/imbriquées/omises/révisionnées/illustrées ou contenu hors corps non parcouru : REVIEW_REQUIRED/FAILED_SAFE, fragments conservés sans admission automatique. Limites ZIP/cellules/paragraphes avant admission.

Les relations entre cellules restent UNKNOWN : pas d'héritage d'en-tête ni de condition, directive des signaux issus de cellules UNSPECIFIED, portée absente UNKNOWN. Recette native9 révisable depuis le locator immuable, avec validation historique8 conservée. Un signal HSE source-only de consignation rend exploitable la prescription négative déjà présente dans l'annexe synthétique.

- [x] TDD extraction/ancres/ordre/limites/refus d'ambiguïté et preuve du contexte cellulaire UNKNOWN; aucun changement production avant rouge observé.
- [x] Extracteur4 et locator docx_table_cell de bout en bout; revalidation native9 dérivée du fragment, refus des preuves table forcées REQUIRED.
- [x] Restitution des coordonnées exactes et du contexte UNKNOWN dans les surfaces existantes, après consultation OpenDesign Local/CYTD et Impeccable; aucune refonte.
- [x] Dossier complet synthétique :34ancienspoints+3prescriptions de cellules, annexe ambiguë non lue, traitements/revue puis rectificatif/historique/isolation; preuves navigateur local si nécessaire pour les nouveaux locators.
- [x] Revue ciblée, suites appropriées, types/lint/build/Semgrep/secrets/diff, suivi et Basic Memory, fermeture des ressources jetables.

Le plan global est l'unique statut. Aucun corpus réel/live/VPS/déploiement/P3/commit/push/admission/activation; A1 non admis/A2 HOLD/NO-GO public. L04 reste PARTIAL, aucune analyse exhaustive déduite.


## Résultat local qualifié

Extracteur déterministe4 : tableaux rectangulaires textuels du corps, dans l'ordre documentaire. Locator `docx_table_cell` : tableau/ligne/colonne/paragraphe/partie positifs, sans renumérotation des cellules vides et sans concaténation de cellules. Fusion, imbrication, omission de grille, suivi de révision, champs, dessins, équations, contenu alternatif ou hors corps non parcouru : REVIEW_REQUIRED/FAILED_SAFE. Une vérification supplémentaire confronte tous les paragraphes Word et leurs textes à ce qui est effectivement parcouru; la comparaison de couverture ne modifie pas le texte émis.

Une forme de locator nouvellement reconnue ne promeut pas une ancienne recette : les ancres de cellule exigent exactement le couple `smart-ao-deterministic`/`4`. La recette native9 revalide le contexte à partir du fragment et refuse une preuve cellulaire étiquetée avec une recette pré9. Les signaux de cellule restent UNSPECIFIED; un lot présent dans une autre cellule n'est pas hérité. Source/version/hash et éventuel lot explicite dans la cellule restent accessibles. La consignation HSE exige un contexte physique; la consignation d'un acompte est refusée comme signal HSE.

Les cellules dont le contexte intercellulaire n'est pas qualifié sont exclues de la source retrieval SQL. L'index vectoriel existant les refuse aussi par sa revalidation contre cette source; aucun encodeur/profil/factory candidat activé. Les deux lecteurs de comparaison CCTP/prix et contradiction les excluent avant leurs comparateurs. Ces restrictions de preuve n'ajoutent aucun droit, confirmation, porte ou effetP3.

## TDD, revue et tests

Neuf rouges initiaux (extraction, ancre, limites, certitude de cellule, HSE) puis verts; trois consommateurs automatiques rouges avant refus, un faux HSE financier rouge avant correction, trois preuves de recette historiques rouges avant liaison stricte. La revue indépendante a reproduit une négation cachée dans `customXml` : six nouveaux rouges sur paragraphes/runs enveloppés, smartTag, AlternateContent, symbole et équation, puis correction. Une erreur de type transitoire dans le refactoring de l'itérateur a été détectée par le positif et corrigée avant le gel. Contre-revue finale :24tests dédiés verts, aucun autre blocage établi.

- Backend final complet : **3795/3795,0ignoré**,2warnings historiques Starlette/httpx et Pydantic Field.alias,1208,39secondes. Le runner a terminé pendant l'interruption; log complet et24hashes inchangés vérifiés à la reprise. Aucun test interrompu annoncé vert.
- Domaine/locators/consommateurs :431/431; services/SQL/provenance ciblés149/149; deux scénarios SQL complets de37points. Ensembles recouvrants : ne pas additionner comme un total distinct.
- Web complet : **628réussites/4ignorés**,74fichiers,152,09secondes; ciblé panneau25/25. Les quatre ignorés préexistent et ne constituent pas une preuve.
- Ruff/format21Python, mypy650, typecheck/lint/build web et diff-check verts. Warning de taille de chunk Vite conservé. Aucun schéma nouveau, tête0139 inchangée.
- Semgrep1.179.0,225règles/24fichiers :0finding/0erreur; detect-secrets1.5.0 zérofinding. Scan limité au périmètre modifié, pas audit de sécurité complet du dépôt.

## Parcours complet et provenance

`backend/tests/db/test_l04_docx_tables_pipeline.py` réutilise le développement complet multi-formats :10pièces,34ancienspoints+3prescriptions de cellules =37points retrouvés sans point parasite mesuré. Une annexe volontairement fusionnée reste non lue. Les anciens corpus TXT/challenges restent intacts; les anciens générateurs de cas « non lu » utilisent désormais une fusion réellement non qualifiée plutôt qu'un tableau simple devenu lisible.

Trois cellules sourcées : une prescription sans lot explicite malgré une cellule voisine « Lot2 » (lotUNKNOWN); une prescription avec lot1 explicite mais condition dans la cellule voisine (directiveUNSPECIFIED); une interdiction de travaux sans consignation pour lot2. Chaque point a sa source/version/hash/cellule exacte et une applicabilitéUNKNOWN. Les37points sont traités, le dossier12axes préparé/revu, puis un rectificatif change une prescription et la durée6→9semaines. Reprise des traitements et revue qualifiées; snapshots V1 conservés, ancien point refusé. Il s'agit d'un développement connu, pas d'un gold indépendant ni d'une preuve de rappel sur un DCE arbitraire.

## Qualification navigateur locale synthétique

OpenDesign Local consulté via le MCP existant : catalogue courant et artefact SMART AO lus; direction Owner/CYTD conservée. L'artefact historique n'a pas remplacé les captures Owner; aucun style, palette, police ou layout ajouté. Impeccable context/craft-floor/audit et detect appliqués; détecteur final vide. Aucun init, nouveau PRODUCT/DESIGN ou hook.

Chrome DevTools MCP dans un Chromium headless isolé (Helium), profil distinct et résolution externe bloquée; aucun Playwright MCP disponible. Le panneau/hook/API client de production sont servis par un harnais loopback privé. Les routes FastAPI et handlers réels sont exécutés par TestClient avec PostgreSQL jetable; session, rôle et MFA sont synthétiques, admission/classification des sources préconditions de fixture. Aucun backend live, authentification réelle ou validation métier humaine déduits.

14assertions de parcours vraies :37points traités dans les formulaires, préparation puis revue sur SHA exact, confirmations explicites, premier double-clic sans doublon, trois locators cellulaires et contexteUNKNOWN visibles, annexe non lue, analysis_complete=false, refus natif Collaborateur403 et masquage immédiat des actions privées. Les39POST réussis portent39identifiants de commande distincts; SQL confirme37évaluations et2revues de dossier. Le contrôle synthétique de remplacement de version est distinct de ces39actes.

Sur1440px : trois libellés comparés exactement aux coordonnées API, actes courants, pas de débordement racine. Sur390px : la table640px conserve son défilement horizontal existant et annoncé; texte repliable, références accessibles et aucun débordement de page. Une première assertion de harnais exigeant toutes les colonnes visibles sans défilement était incompatible avec ce contrat existant; diagnostic conservé, aucun CSS modifié pour la masquer. Ce contrôle n'est pas une certification d'accessibilité ou de lisibilité exhaustive.

Le contrôle navigateur de rectificatif lie une version synthétique vide afin de prouver l'invalidation : anciennes cellules masquées, revueREVIEW_REQUIRED,2snapshotsHISTORICAL de37points conservés. Le parcours positif V2 réextrait/traité/revu est prouvé par SQL, pas par ce contrôle navigateur vide.115entrées réseau observées :114HTTP vers127.0.0.1:5192 et1ressource data interne; aucun cookie/Authorization navigateur. Captures desktop/mobile inspectées; elles illustrent les assertions, sans les remplacer.

## Fermeture, fichiers et limites

Preuves privées : `/home/noor/.local/share/smartao-proofs/l04-docx-tables-20261022/` (logs, schemas MCP, sources synthétiques, screenshots, traces natives, `browser-evidence-summary.json`, `native-effect-counts.json`, hashes). Les24fichiers de code/tests qualifiés restent identiques après les suites et le navigateur.

Trois bases `smartao_l04_tables`, `smartao_l04_tables_global`, `smartao_l04_tables_browser` vérifiées Alembic0; adaptateur fermé proprement, Vite dédié arrêté, onglet et client Chromium fermés, conteneur dédié arrêté, ACLUID70 retirée/socket700. Aucun serveur live touché, aucun stage/commit/push; WIP principal et HEAD30f2693 conservés.

Production : extraction/analysis/handlers/locators et contrats/lecteurs DCE; éligibilité source knowledge et deux lecteurs decision CCTP/prix; type client et Source() du panneau existant. Tests nouveaux : `test_docx_tables.py`, `test_docx_cell_consumers.py`, `test_l04_docx_tables_pipeline.py`; fixtures/refus/version courante ajustés sans réécrire les entrées historiques.

Superpowers using-superpowers, cadrage borné/brainstorming, plan/TDD, systematic-debugging, revue/contre-revue et verification-before-completion; ECC verification-loop. Graphify d'abord (graphe historique recoupé au code), Context7 python-docx et skills formats; OpenDesign Local/Impeccable pour le texte d'interface, Chrome DevTools pour le navigateur. Serena non nécessaire sans navigation sémantique; Jev/Manus non utilisés pour ces assertions déterministes. Plan source unique, Basic Memory miroir.

Les relations entre cellules restent UNKNOWN, les structures complexes refusées, les confirmations/portes inchangées. Les tests ne prouvent ni un DCE réel complet, ni la validation humaine du corpus, ni le reload après reçuUNKNOWN, ni une qualification live. DPGF non évaluable par RAG; A1 non admis/A2 HOLD/NO-GO public. L04 global PARTIAL.

Prochaine étape : L04 — coder et qualifier la restitution sourcée des en-têtes de lot, conditions et négations des tableaux DOCX, puis requalifier traitement, revue et rectificatif sans héritage implicite, modification des portes ou activation de candidat.
