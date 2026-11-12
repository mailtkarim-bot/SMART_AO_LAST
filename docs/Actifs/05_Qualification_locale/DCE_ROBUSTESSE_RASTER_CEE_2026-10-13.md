# ESSAIS DCE — robustesse des relectures/chemins CEE

## Cadrage et protocole avant exécution

**AS-IS :**source9concordances/7chemins candidats à150DPI,0manquant/0faux sur référence unique;calibration inconnue horscas. **Risques :**réutiliser une preuve OUI/NON d’un autre render,ignorer NON effacé,masquer fauxpositifs avecsimplecompteur,confondre limite de calibration etpanne outil. **Insertion :**campagne locale de qualification,preuves privées etdocuments;aucun codeproduit modifié tantqu’aucun défaut démontré ne l’exige.

**Plan minimal :**définir variantes etgrader avant résultats;générer PNG synthétiques hashés,scope/version spécifiques;relectures OCR fraîches de cadres etlabels;redécouvrir nœuds/routes/directions depuis pixels sans groupes/rôles/polylignes attendus;qualifier chemins aprèsbarrière textuelle;comparer références uniquementaprès,refuser lecteurscope/échelle/ambiguïté. Campagne chaquevariant isolé,réseau bloqué/modèles locaux/budgetmémoire borné. Contrôles de grader par assertions indépendantes.

**Familles positives :**identité,luminosité douce,contraste,flou léger,JPEG,réduction/agrandissement simulés sur grille150DPI. Les variantes qui conservent le texte devraient retrouver9cadres/7chemins;les omissions sont rapportées,une protectionUNKNOWN ne vaut pasrobustesse nominale.

**Familles négatives :**effacementNON/asynchrone/centre,flou prononcé,contraste extrême,annulationpointe/étiquette contradictoire,échelle nonqualifiée. Toute affirmation dechemin passant parunezone critique altérée compte fauxpositif critique. Les chemins nonaffectés peuvent rester candidats. Aucunlabelcopié d’un ancienrender.

**Limite déclarée :**OCR primaire/boîtes issus de la référence,conservés commeintentionsstales sur variantes;la campagne testeleurrevalidation,nerequalifiepasl’extractionprimaire detoutepage. ROI fixe,données dérivées locales;pas corpusGolden,d’éligibilitéréelle,d’analysecomplète,UI/backendlive/VPS/déploiement/push/effetP3/dépôt externe/GOpublic. Sources,correspondantCEE,UNKNOWN etREVIEW_REQUIRED maintenus.

- [x] Manifeste de 17 variantes, parent SHA, scopes/hash et huit assertions sur le grader réel.
- [x] Mesure terminée : robustesse nominale NON QUALIFIÉE, omissions et refus explicites.
- [x] Revue technique indépendante ; diagnostics des relations non assemblées et provenance ajoutés. Aucun faux positif démontré ; aucun correctif produit dans cette tranche.
- [x] 39 hashes logiciel inchangés, 85 tests ciblés, compilation des quatre scripts et contrôles documentaires. Mise à jour du plan et du miroir après revue finale.

Superpowers cadrage/plan/verification et ECC eval-harness/verification-loop. Aucunbenchmark d’agent pass@k revendiqué : métriques déterministes d’OCR/graphes sur interventions raster.


## Résultats du 13 octobre 2026

**Verdict : campagne exécutée, robustesse nominale non qualifiée.** Le témoin avec relectures fraîches des labels ne retrouve que 4/7 chemins. T81 est relu `oui|`, refusé plutôt que corrigé depuis la référence ; les trois chemins du moteur neuf restent absents. Cela ne remplace pas la preuve antérieure à 7/7, fondée sur un autre protocole de crop. La nouvelle campagne révèle une dépendance non robuste à ce protocole.

Sur les neuf variantes conservant l'information : **70/81 concordances textuelles**, **20/63 occurrences de chemins**, **43 omissions**, aucun chemin parasite observé. Aucun des neuf cas atteint simultanément neuf concordances et sept chemins. Les neuf groupes géométriques sont retrouvés dans ces cas : cette mesure ne garantit pas leur texte.

| Variante | Concordances /9 | Chemins candidats | Omissions autorisées par le protocole | Faux chemins | Routes non résolues | Refus |
|---|---:|---:|---:|---:|---:|---|
| identity | 9 | 4 | 3 | 0 | 2 | — |
| brightness_0.97 | 7 | 1 | 6 | 0 | 2 | — |
| brightness_1.03 | 8 | 4 | 3 | 0 | 2 | — |
| contrast_0.95 | 8 | 4 | 3 | 0 | 2 | — |
| contrast_1.05 | 9 | 4 | 3 | 0 | 2 | — |
| blur_035 | 8 | 1 | 6 | 0 | 3 | — |
| jpeg_85 | 7 | 1 | 6 | 0 | 3 | — |
| resample_0.9 | 7 | 0 | 7 | 0 | 4 | — |
| resample_1.1 | 7 | 1 | 6 | 0 | 5 | — |
| erase_NON | 8 | 2 | 2 | 0 | 2 | — |
| erase_async | 8 | 1 | 0 | 0 | 2 | — |
| erase_centre | 8 | 3 | 2 | 0 | 2 | — |
| erase_first_head | 9 | 0 | 3 | 0 | 0 | DIAGRAM_ENTRY_REQUIRED |
| contradict_T89 | 9 | 0 | 1 | 0 | 0 | DIAGRAM_BRANCH_AMBIGUOUS |
| blur_15 | 0 | 0 | 7 | 0 | 0 | DIAGRAM_ENTRY_REQUIRED |
| contrast_0 | 0 | 0 | 7 | 0 | 0 | DISCOVERED_DIAGRAM_LIMIT |
| dpi_300_unqualified | 0 | 0 | 7 | 0 | 0 | TOPOLOGY_SCALE_UNQUALIFIED |

Les effacements de NON, asynchrone et centre n'autorisent aucun chemin touchant le nœud critique altéré. Les branches non affectées peuvent rester candidates. Le critère négatif est conservateur : une affirmation interdite par protocole serait comptée comme faux positif critique, sans établir à elle seule une lecture factuellement fausse. La contradiction OUI remplacé par NON est refusée (`DIAGRAM_BRANCH_AMBIGUOUS`). Pointe effacée, flou fort, contraste nul et échelle 300 déclarée sont également refusés. **Zéro faux chemin et zéro affirmation critique interdite sur ces 17 cas**, sans généralisation statistique.

La sortie « contacter le correspondant CEE » reste candidate dans cinq des neuf variantes positives ; elle est manquante dans les quatre autres et explicitement non restituée. Elle n'est jamais transformée en éligibilité. Les diagnostics privés gardent les relations manquantes/non qualifiées/ambiguës et les nœuds inaccessibles : `unknown_paths=0` ne signifie pas absence d'inconnues quand aucun chemin n'est assemblé.

## Preuves reproductibles et contrôles

Preuves privées : `/home/noor/.local/share/smartao-proofs/dce-structured-projection-20261012/raster-robustness/`. `generate.py`, `evaluate.py`, `grader-selfcheck.py`, `aggregate.py`, manifeste, PNG/crops et résultats hashés sont conservés. `aggregate.json` lie les SHA des scripts, manifeste, baseline, références et des 17 résultats.

SHA-256 de l'agrégat : `f93fa13f29147e1f4b3816c147740af1dbd58b26c1c757794adff8d4d84003ce`.

Commande de reproduction depuis ce dossier : `python3 grader-selfcheck.py`, puis chaque cas avec le Python de `.venv` du checkout principal et `PYTHONPATH=backend` absolu, `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1`, enfin `python3 aggregate.py`. Chaque cas est un processus séparé, avec modèles locaux et appels socket Python refusés. Aucun confinement OS complet n'est revendiqué. Le runtime min384/threads1 est borné pour la machine ; aucun seuil de qualification texte n'a été abaissé.

- Huit assertions exécutent le vrai bloc de signature/mapping et de grading sur nominal, omission, mauvaise étiquette, mauvaise sortie, région critique, destruction et chemins UNKNOWN.
- 85/85 tests existants `test_diagram_ocr_coverage.py`, `test_discovered_diagram.py`, `test_conditional_diagram.py`, sans DB et sans coverage globale : contrôle des refus, provenance et assemblage. Aucun test ajouté, aucun comportement produit modifié.
- Compilation des quatre scripts réussie ; Ruff ciblé F821/F822/F823 (noms indéfinis) réussi. Pas de lint/types/build global relancé pour cette tranche sans code produit modifié. `git diff --check` réussi. Les 39 hashes logiciel de début de tranche sont identiques à la fin : aucune modification applicative, dépendance, schéma ou contrat public. La suite globale 2529/2529 de la tranche précédente n'est pas revendiquée comme relancée ici.
- Revue indépendante : limites du compteur UNKNOWN et du grader initial traitées par diagnostics complets et selfchecks réels. Références ouvertes après extraction ; aucun groupe, rôle, route ou texte attendu injecté dans la découverte.

Semgrep 1.179.0 : 225 règles `p/security-audit` sur les quatre scripts privés, aucune erreur ; un finding `python.lang.security.audit.exec-detected.exec-detected` dans `grader-selfcheck.py:10`. Revu : `exec` exécute exclusivement le bloc du script local contrôlé `evaluate.py` pour éprouver le grader réel, avec fixtures construites en code ; aucune donnée DCE/OCR ni entrée réseau n'est exécutée. Usage accepté pour cette preuve privée, pas un mécanisme produit. Une règle `python.boto3.security.hardcoded-token.hardcoded-token` atteint un fixpoint timeout sur l'évaluateur : scan partiel pour cette règle, jamais une preuve globale de sécurité. L'avertissement de lecture de `.cache/dconf` ne concerne pas les quatre fichiers explicitement scannés. Aucun secret ajouté dans les documents/scripts inspectés.

Revue finale indépendante : 17 résultats relus, zéro divergence des hashes d'artefacts et de scope render ; contre-exemples et refus confirmés. Cette revue technique ne vaut pas validation métier humaine.

## Limites et suite

OCR primaire et boîtes conservés, ROI fixe, raster 150 DPI, modèles communs, neuf perturbations nominales et huit cas négatifs seulement. Cette campagne mesure la revalidation de cette page ; elle ne qualifie ni OCR primaire de toute page, ni analyse exhaustive d'un DCE, ni robustesse générale. Les références servent au grading seulement. Les résultats demeurent candidats, `UNKNOWN`, `REVIEW_REQUIRED`, sans acte humain et sans admission.

Prochaine correction : lecture fraîche T81 et pertes OCR sur perturbations légères, avec régression démontrée avant changement, sans normalisation par devinette et sans relâcher les contre-exemples critiques. A1 non admis, A2 générique HOLD, NO-GO public. WIP local non commité ; aucun push, backend live, corpus supplémentaire, VPS, UI, déploiement, effet P3 ou dépôt externe.
