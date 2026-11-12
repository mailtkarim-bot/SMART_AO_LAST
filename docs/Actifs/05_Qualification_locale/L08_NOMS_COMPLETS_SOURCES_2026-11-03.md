# L08 — Noms complets demandés par l’acheteur — 3 novembre 2026

Le plan global garde seul le statut. Correctif local synthétique ; aucune conformité, validité, complétude de pli ou porte déduite d’une égalité de nom.

## Cadrage et cause

AS-IS : le comparateur de noms sait lire une citation complète, mais la segmentation RC v10 découpe la clause au point du nom (`«Memoire.`). Le contrôle final ne dispose alors pas des octets nécessaires pour comparer `Memoire.pdf` et garde UNKNOWN. Le défaut est en amont du comparateur, pas dans la construction du ZIP.

RISQUES : recomposer une citation tronquée, changer casse/accents, avaler une condition voisine, modifier le sens d’une ancienne analyse, transférer sa confirmation, interpréter l’extension comme demande MIME ou renommer un fichier déjà revu.

INSERTION : segmentation déterministe et validation versionnée dans `analysis.py`, conservation du manifeste de provenance v2 dans le handler, éligibilité technique et lecture des versions dans les lecteurs existants. Aucun nouveau modèle, endpoint, écran ou schéma.

PLAN : reproduire le découpage par tests rouges, préserver seulement les littéraux complets et bornés, garder la validation historique, vérifier analyse→matérialisation→confirmation→paquet/revue/P5/ZIP sur V1/V2, puis régressions, revue et sécurité.

## Comportement livré

- Nouvelle version de provenance **11** de `smart-ao-rc-rules`. Les règles/familles restent celles de v9 ; v11 change uniquement la segmentation des littéraux complets après `doit être nommé`/`doit etre nommé`.
- Guillemets français ou doubles, nom de 1 à 255 caractères sans saut de ligne ; points/extensions et ponctuation interne conservés. Accents, casse et octets ne sont pas normalisés dans le nom demandé.
- Segmentation v5 historique inchangée pour reproduire les observations v1–v10. Les nouveaux runs/observations ont des identifiants distincts ; anciennes analyses et confirmations ne sont pas réécrites. Les dossiers déjà analysés en v10 ne sont pas réparés par un GET : relance d’analyse/matérialisation et actes humains courants restent nécessaires.
- Seuls les points internes au littéral complet sont protégés ; séparations de phrases/listes voisines conservées. Offsets UTF‑8 et texte extrait continuent de provenir des fragments originaux, avec mêmes empreintes/locators.
- Citation coupée, guillemet non fermé, alternative, condition, chemin/motif et limite dépassée restent UNKNOWN/non interprétés. Aucune extension, fermeture de guillemet, portée ou unité devinée. La limite de 1000 octets d’extrait, les bornes du run et les refus de source sont conservés.
- Le comparateur et les noms des ZIP exportés restent inchangés. `Memoire.pdf` donne un écart observé face à `technical-response.md` ; `technical-response.md` donne une égalité observée. Dans les deux cas, conformité et applicabilité restent UNKNOWN.

Ce changement de version du code déterministe ne sélectionne ni n’active un moteur candidat. Aucun registre/provider/feature flag de candidat, admission A1/A2 ou règle de porte n’est modifié. L’acceptation technique de v11 conserve les mêmes prérequis de source, classification, intégrité, manifeste et état courant ; v10 reste lisible selon son ancien contrat.

## Fichiers

- `backend/app/modules/dce/application/analysis.py` : itérateur de limites v11 à mémoire bornée, identité de version et validation historique.
- `backend/app/modules/dce/application/handlers.py` : manifeste de source format2 pour v10/v11, mêmes contrôles transactionnels.
- `backend/app/modules/dce/infrastructure/preparation_readiness.py` et `case_dce_reading_reader.py` : versions v10/v11 et provenance courante, sans relâcher les autres conditions.
- `backend/tests/application/test_buyer_full_name_sources.py` : noms/UTF‑8, UNKNOWN, frontières 255/256, voisinage et identités v10/v11.
- Tests existants de métadonnée de version ajustés à 11 ; assertions de contenu, holdout et corpus inchangés.
- `backend/tests/db/test_l08_full_name_packet.py`, helper intégré et recette de formats : assertions natives de nom complet au lieu de l’ancienne troncature attendue. Variante Markdown rejouée ; tranche DOCX non rouverte.

## Preuves

Dossier privé : `~/.local/share/smartao-proofs/l08-full-names-20261103/`.

- Après correction d’une catégorie erronée dans le test, **3 vrais rouges** montrent les citations arrêtées avant l’extension ; 4 cas ambigus restent UNKNOWN. Correction minimale puis 65 purs initiaux verts.
- Revue indépendante : pas de défaut P1/P2 identifié, 8 purs exécutés séparément. Les bornes 255/256 et le guillemet non fermé traversant une clause ont ensuite été ajoutés. **477 purs passent/5,64 s**, couvrant domaine DCE, comparateurs et régression source. Rejeu ciblé final : **11 passent/1,18 s** après simple clarification de variable.
- **Deux recettes natives PostgreSQL/HTTP passent/207,63 s**, avec nouvelle analyse et confirmation des sources : nom différent et nom égal, chacun sur paquet V1 puis paquet V2 après réimport rectificatif. Quatre ZIP, sources/DCE/ancres, revues/P5/manifeste/empreintes et contenu exact relus. V1 obsolète reste REVIEW_REQUIRED, comparaisons vidées et export refusé ; aucun accord/P5 V1 transféré.
- Les preuves des deux cas ont été préservées par identifiant d’Affaire distinct (`native-cases/`), car l’export standard utilise le même sous-répertoire Markdown. Le script de conservation et les quatre empreintes de ZIP sont archivés avec `native-summary.json`.
- **197 régressions passent/55,18 s** : analyse, matérialisation, lecture tenant, ancres, contrôle final et architecture. Deux assertions de métadonnée codées en dur à 10 ont d’abord échoué, puis ont été mises à 11 ; les corpus et attentes de clauses n’ont pas changé.
- Rendu Submission existant : **10 tests Web passent/2,44 s**. Pas de changement de composant ni de nouvelle recette navigateur attribuée à cette correction.
- Mypy app : **708 sources sans diagnostic**. App/tests : **206 diagnostics/40 fichiers/1258 sources**, identités comparées à la clôture L07 : aucun ajout ni retrait, aucune suppression de garde.
- Ruff et diff whitespace verts ; tête Alembic **20261102_0147** inchangée, aucune migration. Semgrep **1.183.0, 99 règles, 12 fichiers, 0 finding, 0 erreur, exit 0** après les tests ; analyse locale et métriques désactivées, pas d’envoi de code/résultats. Base dédiée nettoyée : 0 table métier et 0 ligne Alembic avant suppression du conteneur éphémère.

## Limites et clôture

Pas de reconstruction entre fragments, de réparation de citation coupée ni de traitement des formes de nomination non reconnues par le comparateur actuel. Les consignes de Mo/agrégats/conditions ambiguës, autres familles de pièces et signatures restent avec leurs limites. Les anciennes preuves DOCX restent datées et ne sont pas revendiquées rejouées ; son assertion native attend désormais le nom complet pour les futurs passages.

La correction qualifie l’observation source du nom, pas le renommage de pièces, la satisfaction de toutes les consignes acheteur ou la remise externe. Le pli synthétique conserve ses autres manques. L08 général reste PARTIAL.

Méthode : Superpowers using-superpowers, systematic-debugging, test-driven-development, requesting-code-review et verification-before-completion ; ECC verification-loop et revue sécurité. Graphify consulté avant exploration ; Basic Memory miroir du plan. Aucun changement UI : OpenDesign/Impeccable non applicables. Pas de nouvelle API de bibliothèque nécessitant Context7, de navigation sémantique Serena ni de tâche Jev/Manus pertinente.

A1 non admis, A2 HOLD, NO-GO public, droits/UNKNOWN/portes maintenus. Aucun candidat activé, corpus réel ou gold modifié, live, VPS, déploiement, P3 réel, dépôt externe, commit ou push.
