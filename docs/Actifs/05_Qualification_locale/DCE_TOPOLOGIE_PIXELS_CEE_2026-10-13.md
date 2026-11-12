# Essais DCE — topologie extraite des pixels CEE Cadarache — 13 octobre 2026

## Résultat local et périmètre

Source : CEA Cadarache, petits contrats de travaux d’entretien, contrats cadres 2027–2031; `CCTPC.pdf`, CCTP commun à tous les lots, indice 2, référence `DG/CEACAD/DSTG/STL/GTP/CCTP-22-057`, annexe 13, page 42/44. Diagramme inférieur « Variation de vitesse (BAT-TH-112) ». [Identité et origine](DCE_CHEMINS_FLECHES_QUALIFICATION_2026-10-12.md); [référence conditionnelle précédente](DCE_CHEMINS_CONDITIONNELS_CEE_2026-10-13.md).

Source SHA-256 : `263c2dfdea1d010c1b02d6387ab6eef7d8fdab4e1d2fabd32e32ab3bd133ad8d`. Rendu 150 DPI, 1275×1650 pixels : `e2d7b37426d89c8483d9a9260e8dad7d0792c399560b7ac4b17cbf579e788e79`.

L’extracteur reçoit uniquement le raster, son scope, une région de travail, les neuf nœuds textuels OCR connus et les 24 tokens. **Aucune polyligne, relation attendue ou position de jonction de référence n’est fournie à l’extracteur.** La référence des 12 liaisons et 3 jonctions n’est lue par le comparateur qu’après l’extraction. Les régions/noms des nœuds textuels restent fournis : cette tranche ne prouve pas leur découverte autonome.

| Mesure sur cette référence | Résultat |
|---|---|
| Cadres de nœuds détectés dans le raster | 9/9 |
| Liaisons candidates retrouvées | 12/12 |
| Liaisons attendues manquantes ou dupliquées | 0/12 |
| Liaisons candidates supplémentaires par rapport à la référence | 0 |
| Jonctions de référence retrouvées | 3/3 |
| Jonctions supplémentaires | 0 |
| Preuves de contact des routes avec les cadres | 15 chemins de pixels bruts conservés |
| Trait supplémentaire conservé sans raccordement qualifié | 1 UNKNOWN |
| Orientation / interprétation réelle / admission | UNKNOWN / UNKNOWN / NON |

Ces comptes portent sur les 12 relations de référence, pas sur tous les objets du PDF ni sur la complétude d’un DCE. Le trait UNKNOWN, du bandeau supérieur à `y1099`, relie deux extrémités non rattachées; il reste visible dans les 13 observations et n’est pas éliminé pour améliorer les métriques.

## Nœuds et connexions observés

Les trois jonctions sont découvertes sans coordonnées de référence dans les entrées :

| Jonction détectée | Région en pixels | Correspondance du comparateur |
|---|---|---|
| `p-344-1280` | `[344,1280,345,1281]` | reject : variateur déjà présent / asynchrone NON → sortie NON ELIGIBLE |
| `p-676-1222` | `[676,1222,677,1223]` | inlet : moteur neuf / variateur absent → question asynchrone |
| `p-677-1328` | `[677,1328,678,1329]` | split : asynchrone OUI → IE2 et IE3/IE4 |

La comparaison associe ces régions aux ancres gelées de la référence avec une tolérance déclarée de 3 pixels. Les extrémités sont comparées **sans orientation**; le mapping n’est pas réinjecté dans l’extracteur.

Les 12 connexions topologiques candidates conservées sont : existant–variateur; neuf–inlet; variateur–inlet; inlet–asynchrone; variateur–reject; asynchrone–reject; reject–NON ELIGIBLE; asynchrone–split; split–IE2; split–IE3/IE4; IE2–correspondant CEE; IE3/IE4–ELIGIBLE. Les flèches « → » du tableau explicitent la référence documentaire précédente, pas une orientation déduite automatiquement par ce lecteur.

Les questions existant/neuf, variateur déjà présent, asynchrone et classes IE2/IE3/IE4 restent dans les seeds/tokens originaux. Les OUI/NON, y compris T81 `iño` et T89 `Iño`, sont conservés en OCR brut. Leur rattachement et la direction des nouvelles routes restent à qualifier. La sortie « Contacter votre correspondant CEE centre » reste un nœud distinct, sans réduction à une issue binaire d’éligibilité.

## AS-IS, risques, insertion et plan minimal

AS-IS : l’assembleur précédent avait besoin de polylignes fournies. Risques : cadre lu comme route, trait fin dédoublé, remplissage coloré interprété comme réseau, croisement lu comme jonction, gap comblé sans preuve, provenance perdue, extraction hors région.

Insertion : un lecteur local `backend/app/modules/dce/infrastructure/diagram_topology_reader.py` et 30 cas dans `backend/tests/application/test_diagram_topology.py`. PyMuPDF installé est réutilisé; extraction par parcours de pixels en bibliothèque standard, pas d’ajout de package. OpenCV a été examiné via Context7 comme alternative, puis écarté de cette insertion : aucun import ni dépendance supplémentaire. Pas de writer/API, schéma, migration, UI ou branchement automatique dans l’analyse métier.

Plan réalisé : preuves du dépôt et référence gelée → dix tests rouges initiaux → traits/cadres/connectivité → confrontation source → régressions des défauts observés → revue indépendante → correctifs rouges/verts → intégration des deux fichiers → contrôles finaux. Les 31 fichiers logiciels hérités contrôlés sont inchangés dans le checkout principal et le worktree.

Branche `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`; WIP local non commité. Les fichiers intégrés correspondent au worktree relu. Aucun push.

## Algorithme borné et refus

Calibration `axial-150dpi-v1` : PNG de 20 Mo maximum, image de 25 millions de pixels maximum, région de travail d’un million de pixels maximum, gris strictement inférieur à 180, traits axiaux d’au moins 18 pixels et au plus 3 pixels d’épaisseur. Cadres rectangulaires clos recherchés jusqu’à 64 pixels autour des régions OCR; plusieurs cadres possibles ou plusieurs seeds pour un même cadre restent non qualifiés.

Les longs runs horizontaux/verticaux sont regroupés par leur connectivité réelle à quatre voisins. Les cadres qualifiés sont retirés du graphe des routes. Les rectangles de labels OCR ne masquent pas les routes : un rectangle OCR peut déborder sur un trait, sans autoriser sa suppression. Le seuil de gris distingue ici les traits anti-aliasés du remplissage orange; ce réglage ne vaut pas calibration universelle sur tout DCE.

Une intersection exige des pixels communs ou adjacents réellement connectés. Les stubs de quantification d’au plus 2 pixels sont rabattus sur une intersection déjà prouvée; aucun espace blanc entre traits n’est comblé. Les coudes sont conservés dans les routes, les T deviennent candidats, les croisements à quatre branches restent UNKNOWN. Les cycles de traits non résolus restent visibles dans `unresolved_regions`.

Une extrémité proche d’un cadre ne suffit pas : preuve conservée de contact par parcours des pixels bruts, ou preuve de pointe axiale unique à au plus 2 pixels du cadre selon le détecteur déjà qualifié. Cette seconde possibilité est limitée à sa calibration; sur le raster réel les **15 contacts sont tous des parcours de pixels bruts**. L’arrondi de l’axe autorise uniquement un pixel latéral unique, avec parcours réel conservé. Un trait nu séparé du cadre par des rangées blanches n’est pas raccordé.

Bornes : 32 seeds, 128 tokens/liens, 256 traits, 512 composants par orientation, produit des recherches de cadre ≤4096 par seed, 512 points maximum par route. IDs de seeds uniques et namespace `p-` réservé aux sommets pixel. Scope source/version/tenant/rendu exact vérifié; bornes de région entières, minima inclusifs/maxima exclusifs; ancres de sortie confinées dans la région. Hash, PNG corrompu, échelle étrangère, région hors scope ou limites invalides sont refusés.

Le résultat conserve seeds, tokens, cadres, jonctions, chemins, contacts et preuves de pointe éventuelles, scope et hash d’entrée/version du lecteur. Une sélection UNKNOWN ne supprime pas la preuve. Ces candidats ne résolvent pas l’ownership SQL ni les permissions HTTP; le caller doit fournir un contexte autorisé.

## Tests, revue et contrôles

**149 tests ciblés réussis** : 30 topologie, 23 assemblage conditionnel, 39 pointes/labels, 57 projection. Dix rouges initiaux, puis régressions reproduites pour dédoublement des traits, cadre large, masquage OCR destructeur, remplissage, bornes de recherche et provenance.

La revue indépendante a confirmé deux P2 : rattachement fictif par proximité du cadre et troncature d’une région fractionnaire. Tests rouges observés puis verts, incluant trois espacements blancs, contact conservé, confinement de région et arrondi latéral. Seconde revue : deux findings fermés, aucun autre défaut concret confirmé; elle ne remplace pas une validation humaine ou la preuve source.

Contre-exemples : trait interrompu entre deux cadres → une liaison attendue manquante, aucun faux lien complet, deux fragments UNKNOWN; gap à une intersection → aucune jonction inventée; lignes parallèles proches distinctes; croisement quatre branches UNKNOWN; cadre isolé jamais promu en route; cycle visible non résolu; grille dense refusée par limite. Replay déterministe et scope étranger vérifiés.

Contrôles déjà acquis : Ruff global vert, format1180fichiers, mypy619sources; `git diff --check` vert. Semgrep1.179.0, `p/security-audit`, 225règles configurées, deux fichiers nouveaux réellement scannés,0finding/0erreur, métriques désactivées; Bandit nouveau module0finding/0erreur; detect-secrets `--all-files --no-verify`0finding. Ce scan ciblé ne constitue pas un audit de sécurité exhaustif. Suite backend complète : **2450/2450 réussis**, 0 ignoré, couverture **88.11%** (seuil85,50% inchangé), 1307.40s, 2 avertissements Starlette/Pydantic. Campagne depuis le checkout principal avec PostgreSQL tmpfs frais; journal/XML conservés hors Git.

La première campagne globale n’est pas qualifiante : 2449 réussites et 1 échec dans `test_nested_duplicates_unsupported_and_determinism`, 1854,79s, cov88,10%, 2warnings. La première lecture a dépassé la limite de120s d’un worker; ses deux alias sont restés TIMEOUT_UNEXTRACTED, puis la seconde lecture a terminé. Aucun timeout caché ou transformé en COMPLETED. Test isolé sans couverture1,78s, puis avec instrumentation enfant pytest-cov6.3 installée17,29s :1/1 dans chaque diagnostic. Cause précise du dépassement non reproduite; charge transitoire/instrumentation reste une hypothèse, pas un bug confirmé. Aucun changement du code, des tests, des délais ou du seuil85,50%; seconde campagne complète sur PostgreSQL tmpfs frais terminée :2450/2450,cov88,11%,1307,40s,2warnings. Le délai initial reste un incident non reproduit; sa cause précise n’est pas déclarée résolue par un changement de code. Logs/coverage initiaux et diagnostic conservés séparément.

## Preuves, statut et limites

Preuves privées hors Git : `/home/noor/.local/share/smartao-proofs/dce-structured-projection-20261012/topology/` : `prove.py` bloquant les accès réseau Python, `qualification-initial.json` non qualifiante, `qualification.json` final et copie figée nommée par son SHA, `source-final.log`, `inherited-hashes.json`, `integrated-files.json`, journaux/couverture/scans. La référence antérieure est conservée; son SHA est enregistré dans la comparaison. Aucune source réelle dans les fixtures Git.

**A1 non admis, A2 générique HOLD, NO-GO public.** Sémantique et directions UNKNOWN, REVIEW_REQUIRED, `admission_granted=False`. Pas d’éligibilité réelle, règle réglementaire actuelle, analyse complète, admission Golden ou acte humain simulé. Aucun backend live, corpus externe nouveau, UI, VPS, déploiement, push, P3, dépôt externe ou export métier. Les textes/rôles/regroupements des neuf seeds sont encore fournis; les traits courts, obliques, autres échelles/couleurs et topologies génériques ne sont pas qualifiés.

Méthode : Superpowers using-superpowers/brainstorming/TDD/requesting-code-review/systematic-debugging; ECC verification-loop; Graphify, activation Serena, Context7 pour l’alternative OpenCV et le fonctionnement pytest-cov6.3 installé, Basic Memory miroir. OpenDesign/Impeccable inapplicables sans interface; Jev/Manus non requis pour ce parcours déterministe.

Prochaine étape : ESSAIS DCE — qualifier l’orientation et le rattachement OUI/NON des routes CEE découvertes dans les pixels, puis reconstruire les sept chemins conditionnels de Cadarache sans injecter les relations de référence; comparer omissions et faux chemins, conserver la sortie correspondant CEE, les sources et UNKNOWN. A1 non admis, A2 générique HOLD et NO-GO public maintenus.

Clôture technique locale : plan et index actualisés, miroir Basic Memory synchronisé; PostgreSQL tmpfs de la finale retiré après contrôle ID/label/aucun volume/port local et absence confirmée. Reçus de nettoyage des deux campagnes conservés séparément. Le timeout initial demeure dans les preuves; aucune cause précise ou garantie de latence universelle n’est inférée de la reprise verte.
