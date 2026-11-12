# Essais DCE — orientation et chemins CEE Cadarache — 13 octobre 2026

**Qualification technique locale acquise; aucune admission ou éligibilité réelle.**

## Cadrage et plan minimal

AS-IS : topologie150DPI qualifiée sans routes attendues,12liaisons/3jonctions/15contacts bruts et1traitUNKNOWN. Pointe terminale et qualificateur OUI/NON existants; assembleur conditionnel précédent guidé par référence.

Risques : direction arbitraire, label affecté à une route voisine, doublepointe, négation perdue, chemin incomplet ou OCR illisible promu, provenance effacée. Insertion minimale : nouveau module applicatif `discovered_diagram.py`, son test `test_discovered_diagram.py`, caller privé local. Aucun writer/API/UI/schéma/dépendance nouvelle.

1. Observer les pointes aux deux extrémités des routes réellement extraites; conserver chaque observation, même UNKNOWN/contradictoire.
2. Qualifier/rattacher OUI/NON avec les scopes/régions et relectures déjà prouvées. Un label de réponse peut produire un sens **candidat de port de question** vers une jonction, selon la convention bornée de ce logigramme; ce n’est pas une pointe inventée ou une règle métier évaluée.
3. Dériver les relations depuis la géométrie/pointes/labels; aucun endpoint, polyligne, direction, label attendu ou chemin de référence injecté dans le qualificateur. Réutiliser l’assembleur existant.
4. Comparer ensuite aux12liaisons et7chemins de référence; mesurer omissions et fauxchemins. Garder IE2→correspondant CEE, les questions amont, UNKNOWN et REVIEW_REQUIRED.
5. TDD rouge→vert, revue indépendante, intégration locale des seuls fichiers concernés, contrôles du projet/Semgrep, plan/index/Basic Memory.

Comportements à prouver : nominal, inconnus, doublepointe, label illisible/concurrent, label d’issue refusé, autretenant/source/version, provenance falsifiée, cycle, limites et déterminisme. Les rôles/nœuds OCR restent fournis; les résultats concernent le document, jamais un moteur réel ou l’éligibilité réglementaire actuelle.

Code/HEAD à qualifier : branche `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`, WIP préservé;33fichiers logiciels hérités figés parSHA. Méthode : Superpowers using-superpowers/brainstorming/writing-plans/TDD/requesting-code-review; ECC verification-loop. Plan dans les emplacements du dépôt, aucun `docs/superpowers` ajouté.

A1 non admis, A2 générique HOLD et NO-GO public maintenus. Aucun backend live, VPS, déploiement, push, P3, dépôt externe ou export métier.

## Résultat source borné

Pièce CEA Cadarache : `CCTPC.pdf`, indice2, référence `DG/CEACAD/DSTG/STL/GTP/CCTP-22-057`, annexe13 page42/44, diagramme inférieur « Variation de vitesse (BAT-TH-112) ». [Origine](DCE_CHEMINS_FLECHES_QUALIFICATION_2026-10-12.md), [topologie](DCE_TOPOLOGIE_PIXELS_CEE_2026-10-13.md).

Source SHA-256 `263c2dfdea1d010c1b02d6387ab6eef7d8fdab4e1d2fabd32e32ab3bd133ad8d`; rendu150DPI SHA-256 `e2d7b37426d89c8483d9a9260e8dad7d0792c399560b7ac4b17cbf579e788e79`. Le caller vérifie ces deux hashes, bloque les accès réseau Python et réexécute le lecteur topologique depuis le PNG. Il observe les pointes aux26extrémités des13routes, sans copier les relations ou directions de référence.

Le qualificateur produit **7directions candidates par pointe unique et5par port de question**, avec1trait isolé UNKNOWN. Les5labels sont qualifiés/rattachés : T81 OUI (brut `iño`, relecture `ouI`), T82 OUI, T84 NON, T87 NON, T89 OUI (brut `Iño`, relecture OUI). Ancres/source/version/SHA/parseur/crop et OCR brut restent dans les observations. Aucune affectation issue des IDs de relations précédentes : seuls les objets OCR qualifiés sans relation ID sont réutilisés.

Le premier essai privé avait omis T87 car sa région OCR dépassait de3pixels le carrier géométrique choisi. Ce résultat5/7reste dans `qualification-initial.json`. Le carrier est maintenant calculé depuis les routes/nœuds/pointes avec marge32pixels, sans label attendu ni référence de chemin. Les règles de rattachement restent celles du qualificateur; aucune règle Iño→OUI codée.

| Entrée | Conditions successives conservées | Issue documentaire |
|---|---|---|
| Existant | Variateur déjà présent OUI | NON ELIGIBLE CEE |
| Existant | Variateur déjà présent NON; asynchrone NON | NON ELIGIBLE CEE |
| Existant | Variateur déjà présent NON; asynchrone OUI; IE2 | Correspondant CEE |
| Existant | Variateur déjà présent NON; asynchrone OUI; IE3 ou IE4 | ELIGIBLE CEE |
| Neuf | OUI de l’entrée; asynchrone NON | NON ELIGIBLE CEE |
| Neuf | OUI de l’entrée; asynchrone OUI; IE2 | Correspondant CEE |
| Neuf | OUI de l’entrée; asynchrone OUI; IE3 ou IE4 | ELIGIBLE CEE |

Comparaison effectuée **après reconstruction** :7chemins attendus/7candidats retrouvés,0manquant/0fauxchemin sur cette référence. Trois issues NON ELIGIBLE, deux ELIGIBLE et deux CONTACT sont des chaînes du document, pas l’éligibilité réelle d’un moteur. Le mapping des3jonctions pixel vers les ancres de référence ne sert qu’à la comparaison; il n’est pas renvoyé au qualificateur. La convention de réponse à une question n’est pas une preuve de pointe cachée : ses cinq directions restent explicitement `QUESTION_PORT_DIRECTION_CANDIDATE`, avec sémantique UNKNOWN.

## Qualification et refus

`discovered_diagram.py` reçoit nœuds/tokens/routes/observations de pointe/labels. Il n’accepte ni relations attendues ni chemins attendus. Les relations sont dérivées depuis les observations, puis transmises à l’assembleur conditionnel existant. Le domaine ne dépend d’aucun SDK; le module applicatif est pur. Le caller privé orchestre les lecteurs d’infrastructure existants; aucun port supplémentaire, endpoint, schema ou writer ajouté.

Les pointes doivent appartenir au scope exact, provenir du détecteur calibré, se trouver dans leur carrier et correspondre à une seule extrémité. Plusieurs pointes distinctes, routes concurrentes ou labels concurrents restent UNKNOWN. Un port de question exige ENTRY/CONDITION, texte techniquement qualifié, au moins un caractère alphanumérique et terminaison `?`; une ponctuation seule ou une classe IE2/IE3/IE4 n’est pas une question booléenne. Le label doit être unique, non détenu par un nœud caption, qualifié par la routine existante et géométriquement rattaché à la route. Les mots d’issue ne deviennent pas des réponses OUI/NON.

Une route UNKNOWN reste dans `decisions` et `unresolved_routes`. Tous ses nœuds connus sont rendus non qualifiés pour l’assemblage; une racine aval ne peut ainsi contourner des conditions amont. Les nœuds source originaux restent dans `source_nodes`. Cette propagation est conservatrice : une route incertaine peut rendre UNKNOWN un chemin dont d’autres segments sont visibles. Aucune direction manquante n’est inventée.

Bornes :32nœuds,128routes/labels,64points par route,8observations de tête par route; identifiants uniques et bornés, points finis et carriers exacts. Source/version/tenant/rendu vérifiés avant résultat. Verdict de label falsifié, version de détecteur non qualifiée, cycle, route hors région ou limites invalides sont refusés. Replay/permutation déterministes; preuves ambiguës et non assignées conservées.

## Tests, revue et contre-épreuve

TDD :10rouges initiaux module absent, puis2rouges de contraintes amont et1rouge de caption `???`, observés avant correctifs. **18nouveaux tests /167ciblés réussis** :18reconstruction,30topologie,23assembleur,39pointes/labels,57projection. Nominal7chemins, ordre/permutation, doublepointe, labels ambigus/illisibles, verdict falsifié, scope étranger, trait inconnu, géométrie non qualifiée, limites, région et cycle couverts.

Revue indépendante :1P2confirmé (routeUNKNOWN supprimée avant contraintes amont); correctif avec2régressions rouges→vertes, source_nodes conservés. Seconde revue confirme la fermeture sur six cas, sans autre défaut concret. Revue IA distincte d’une validation humaine et de la qualification source locale.

Contre-épreuve source : retirer seulement la relecture T89, garder `Iño` brut et sa provenance source → route correspondante UNKNOWN, nœuds asynchrone/split non qualifiés, **6chemins candidats manquants et0fauxchemin** sur7attendus. Le chemin existant/variateur déjà présent OUI reste candidat; les chemins passant par le nœud incertain ne sont pas promus.

Ruff global vert, format1182fichiers; mypy620sources vert après vérification globale des types. Semgrep1.179.0 `p/security-audit`,225règles configurées,2nouveaux fichiers réellement analysés,0finding/0erreur, métriques désactivées. Bandit nouveau module0finding/0erreur; detect-secrets `--all-files --no-verify`0finding. Scan ciblé, pas audit de sécurité exhaustif. Suite backend globale : **2468/2468 réussis**,0ignoré,couverture **88.13%** (seuil85,50% inchangé),1201.79s,1avertissementStarlette/httpx. Snapshot logiciel figé et contrôlé parSHA; base PostgreSQL tmpfs fraîche, journal/XML hors Git.

La campagne précédente a été interrompue à70%, sans résumé final ni processus restant à la reprise; journal conservé séparément, aucune réussite globale inférée. La campagne de reprise utilise une base PostgreSQL tmpfs fraîche et le même code figé. Aucun test/délai/seuil85,50% abaissé. Le timeout non reproduit de la tranche topologie précédente reste documenté dans son dossier; aucune résolution de cause inventée.

## Provenance et limites maintenues

Preuves privées `/home/noor/.local/share/smartao-proofs/dce-structured-projection-20261012/orientation/` : `prove.py`, `qualification.json`, copie figée SHA, `qualification-initial.json`, `counterprobe-raw-T89.json`, `source-final.log`, `inherited-hashes.json`, `integrated-files.json`, scans/journaux/couverture. Sources réelles hors Git; tests synthétiques.33fichiers hérités inchangés, deux nouveaux fichiers intégrés, aucune perte du WIP.

Les9groupes OCR et leurs rôles restent fournis. La convention des ports de question reste bornée au logigramme étudié, sans calibration universelle. Les sorties ELIGIBLE du document ne constituent ni fait d’éligibilité réelle, ni règle réglementaire actuelle, ni analyse complète. UNKNOWN, REVIEW_REQUIRED, A1 non admis, A2 générique HOLD et NO-GO public maintenus. Aucun acte humain simulé, backend live, corpus externe nouveau, UI, VPS, déploiement, push, P3, dépôt externe ou export métier.

Méthode : Graphify, Basic Memory, Superpowers using-superpowers/brainstorming/writing-plans/TDD/requesting-code-review; ECC verification-loop. APIs des lecteurs installés réutilisées selon leurs preuves précédentes; aucun nouveau contrat de bibliothèque nécessitant Context7. Pas de navigation sémantique supplémentaire ni de Jev/Manus requis pour ce traitement déterministe; OpenDesign/Impeccable et REA inapplicables à cette logique source disponible sans UI.

Prochaine étape : ESSAIS DCE — découvrir et regrouper les nœuds textuels du logigramme CEE de Cadarache depuis OCR/raster sans fournir les neuf groupes ni leurs rôles, puis requalifier les sept chemins et mesurer nœuds, relations et conditions manquants ou parasites; conserver sources, correspondant CEE et UNKNOWN. A1 non admis, A2 générique HOLD et NO-GO public maintenus.

Clôture technique locale : plan/index et miroir Basic Memory actualisés. PostgreSQL tmpfs de la finale retiré après contrôle ID/label/aucun volume/port local et absence confirmée; reçus de la campagne interrompue et finale séparés. `git diff --check` vert; hashes du snapshot logiciel et documents conservés dans `final-gates.json`. Aucun commit/push.
