# Essais DCE — projection structurée candidate — 12 octobre 2026

## Résultat et limites

Projection locale en lecture seule implémentée dans le contexte DCE. Elle lie source/version/render/page/régions, conserve texte brut et valeurs UNKNOWN, et produit uniquement des candidats REVIEW_REQUIRED. Aucun endpoint, writer, migration, nouvelle permission ou admission automatique.

Sur21pages, les1467libellés et370régions de cellule sont projetés :187cellules avec texte candidat,183UNKNOWN. Les11références ont leurs ancres source exactes conservées :8supports d’ancres et3relations de flèche explicitement UNKNOWN. Il s’agit de conservation/projection de provenance, **pas11compréhensions sémantiques confirmées**. Aucune confirmation sémantique ou décision métier automatique.

A1 non admis, A2 générique HOLD, NO-GO public. Corpus, références, textes, images et projections réelles restent hors Git. Aucun backend live, VPS, déploiement, push, P3 ou dépôt externe. Aucune validation humaine simulée.

## AS-IS, risques, insertion et plan exécuté

AS-IS : labels/régions de preuve privés sans fonction candidate typée. Risques : perdre NON, transformer voisinage en relation, remplir cellule vide, fusionner lots/versions/tenants, sortie mutable sous ancien hash. Insertion : module pur application DCE, réutilisable par un caller autorisé; aucun couplage fournisseur/HTTP/SQL/LLM.

Plan : TDD synthétique rouge; projection minimale et validations; ambiguïtés rouges corrigées; preuve locale21pages/11références; revue/scans et gates globaux; intégration à hashes identiques, docs et mémoire. Worktree depuis HEAD30f26934430095632000a1d82519f61dbb4c6411 avec overlay explicite24fichiers WIP inchangés; checkout principal `/home/noor/PROJECTS/BTP/SMART_AO_V8`, branche `codex/reconcile-smartao-20261009`.

## Code et contrat

- `backend/app/modules/dce/application/structure_projection.py` : dataclasses gelées et fonction pure `project_candidate_structure`.
- `backend/tests/application/test_dce_structure_projection.py` :29preuves synthétiques, aucun corpus réel en fixture.

Le scope attendu comprend tenant/doc/version/SHA source/SHA render/page/dimensions. Tout anchor étranger ou obsolète est rejeté avant retour de contenu, avec erreur générique. Scope, identifiants, hash, nombres finis et coordonnées strictement dans la page sont contrôlés. Bbox mutables refusées; namespace commun token/cellule sans collision. Limites512régions/page et1000caractères/token; entrées invalides refusées, jamais admises par défaut.

Le hash d’entrée lie le contenu, les régions, les identifiants et la version du projecteur1. Ordre d’entrée des tokens/cellules/diagrammes canonisé; retry identique donne une projection identique. Aucun effet métier produit. Le hash est un identifiant de l’entrée déclarée, pas une preuve de signature ou de propriété documentaire.

NON/NOT et ELIGIBLE/ÉLIGIBLE peuvent être regroupés en candidat négatif lorsque l’adjacence est non ambiguë et, si cellules fournies, avec **un seul conteneur commun**. Plusieurs rattachements ou conteneurs différents gardent UNKNOWN. Textes bruts et token IDs restent conservés; l’absence d’une négation reconnue ne rend jamais un candidat éligible. `business_eligibility=UNKNOWN` reste constant.

Une cellule reçoit du texte candidat seulement si les tokens sont contenus de manière non ambiguë, sans fragment coupant sa région. Cellules imbriquées, conteneurs multiples, vides et chevauchements restent UNKNOWN. Texte brut numérique n’est pas une quantité/pondération/montant normalisé; valeur null, row/column null et value_state UNKNOWN. Les relations de containment restent GEOMETRIC_CONTAINMENT_ONLY et semantic_state UNKNOWN.

Les régions de diagramme donnent DIAGRAM_EDGE UNKNOWN avec endpoints vides : l’ordre OCR ne peut fournir un chemin ou une direction. La page et la version séparent les tableaux; lot_applicability reste UNKNOWN, même lorsque le document contient un intitulé de lot.

## Preuve locale indépendante des annotations

La projection est exécutée à partir des labels/grilles précédemment extraits sur21pages, sans utiliser les valeurs ou relations annotées comme entrées. Les11références sont comparées ensuite. PDF source et render150DPI rehachés, dimensions/page vérifiées; chaque région de référence contient les ancres résultantes vérifiées. Permutation d’entrée rejouée à projection strictement identique; tous les candidats conservent REVIEW_REQUIRED, aucune admission ou valeur métier.

Les identifiants tenant/document/version du caller de preuve sont synthétiques et dérivés du manifeste privé; ils ne sont pas des objets métier résolus. La fonction ne résout pas l’ownership ou le droit d’accès seule : son caller doit fournir un contexte source autorisé et vérifié. Il n’existe dans cette tranche aucune route publique ou lecture SQL exposant ces candidats. Les tests de mismatch prouvent le refus de région hors scope, pas une nouvelle qualification d’authentification live.

Les13points non éligibles restent exclus; aucune analyse ou matérialisation des exigences ne les promeut. La sortie candidate n’est pas automatiquement intégrée au parcours utilisateur ou à un writer métier.

## Tests, revue et sécurité

TDD :17rouges initiaux (module absent),3rouges géométrie/ambiguïtés/limite,1rouge immutabilité puis2rouges de revue (conteneurs multiples/entier extrême), corrigés;29tests verts. Nominal, NON ambigu, cellules vides/coupées, tenant/doc/version/page/hash étrangers, NaN/bbox hors limites, scope invalide, collisions, taille, coordonnées mutables, version/rendu et retry/permutation couverts.

Revue indépendante : sorties mutables et négation multi-conteneurs corrigées; aucun finding bloquant supplémentaire. Borne512contient les boucles quadratiques, aucune sémantique ni endpoint de flèche inventé.

Ruff global/format1194fichiers et mypy1036sources verts. Semgrep1.179.0/p-security-audit225règles,2fichiers,0finding/0erreur, métriques désactivées; fichiers non suivis explicitement analysés. Detect-secrets0finding; Bandit moyen/haut0finding. Aucun résultat transmis.

**Suite backend complète : 2330/2330 réussis, couverture 88.03%**, seuil85,50% inchangé, PostgreSQL local jetable tmpfs. Journal complet `backend-global.log`, couverture `coverage.xml`. Aucun test global partiel présenté PASS.

Méthode : Superpowers using-superpowers/cadrage borné/TDD/requesting-code-review/verification-before-completion; ECC verification-loop. Graphify/Serena pour contexte, Basic Memory miroir. Jev/Manus non requis pour cette transformation déterministe; OpenDesign/Impeccable inapplicables sans changement UI. Pas d’exercice dépendance distante ou de validation humaine.

Preuves privées : `/home/noor/.local/share/smartao-proofs/dce-structured-projection-20261012/`, projections21pages, qualification11points, hashes, sources/régions revalidées, rouges/verts, scans/revue et journaux. Aucun de ces payloads privés n’est ajouté à Git.

Prochaine étape : ESSAIS DCE — extraire et qualifier les chemins de flèche et leurs étiquettes OUI/NON sur les trois relations de référence du logigramme DCE-03, avec ancres de région et refus des ambiguïtés; conserver UNKNOWN et REVIEW_REQUIRED tant que la relation n’est pas prouvée. A1 non admis, A2 générique HOLD et NO-GO public maintenus.

Clôture checkout principal : les hashes des2fichiers intégrés sont identiques au snapshot complet,34tests du checkout principal passent,5contrats documentaires ont été inclus dans ce total; liens rapport/index, une seule tranche active, diff-check et miroir Basic Memory relus. WIP non commité; aucun push. Base PostgreSQL tmpfs de ce test supprimée après vérification du reçu d’isolation.
