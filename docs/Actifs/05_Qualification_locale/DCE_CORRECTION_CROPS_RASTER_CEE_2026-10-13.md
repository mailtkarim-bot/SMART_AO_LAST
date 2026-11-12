# ESSAIS DCE — correction des crops et pertes OCR CEE

## Cadrage de la tranche

**AS-IS :** le checkout principal reste sur `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`, WIP antérieur conservé. Campagne précédente : 70/81 concordances, 20/63 chemins, 43 omissions. T81 est lu `oui|` parce que le crop de qualification inclut le trait vertical de la route voisine. Les autres pertes comprennent des caractères divergents, un pixel d'encre non couvert et des routes non résolues.

**Risques :** corriger I/l/1 par devinette, choisir une recette en fonction du texte attendu, éliminer une négation ou une condition, confondre correction du harness avec intégration produit, réutiliser un hash de crop antérieur. Les pertes ne justifient jamais de lever UNKNOWN.

**Points d'insertion :** évaluateur local et fonction de crop de labels ; le crop défectueux est dans le harness privé, pas dans un caller applicatif. Les lecteurs produits conservent leurs contrats. Les probes OCR servent à déterminer si une modification de lecteur est justifiée avant toute édition produit.

**Plan minimal :** (1) crop synthétique avec glyphes courts et trait de route long : rouge puis correction géométrique et vert ; (2) identité native, relecture indépendante de T81 et sept chemins ; (3) vérifier les pertes restantes sans substitution textuelle ; (4) nouvelle campagne sur les mêmes 17 rasters, diagnostics et contre-exemples ; (5) revue, tests, provenance, plan et miroir.

**Tests :** exclusion d'une route continue d'au moins 18 pixels à l'extrémité d'une boîte de label à 150 DPI, conservation du glyphe court, absence de trait, ambiguïté avec texte au-delà du trait, bounds invalides et région trop grande. Calibration locale explicite, aucun texte attendu dans le crop.

Méthode : Superpowers using-superpowers/systematic-debugging/TDD/cadrage borné, ECC python-testing/verification. Aucun changement visible d'interface, API, migration ou dépendance prévu. A1 non admis, A2 HOLD, NO-GO public ; aucun push/backend live/VPS/déploiement/P3/dépôt externe.

## Journal de preuve initial

- Rouge observé : le crop existant conserve le trait (bord droit 51, attendu avant 43) ; un test échoué et un réussi.
- Correction : trouver le trait axial depuis l'encre raster, puis borner le crop avant le trait. Aucun effacement de pixel ni correction du texte ; les régions et SHA exacts restent enregistrés.
- Vert : cinq tests synthétiques passent, dont limites et ambiguïté. Probes natifs : T81 est relu OUI sur les neuf variantes positives avec crop sans route ; la recette de sonde manuelle sert seulement au diagnostic, la campagne utilise la fonction géométrique générale.
- Identité avec cette fonction : neuf concordances et sept chemins candidats, zéro omission/faux chemin. La sortie correspondant CEE est conservée. Aucun résultat métier promu.
- Probe détecteur min512 sur luminosité0.97 : sept concordances seulement ; augmenter sa résolution ne corrige pas la cause. Probe archivée, non adoptée.

## Requalification finale des 17 rasters

Le crop corrigé et le garde de topologie ont été figés avant le rejeu final. Chaque résultat lie les SHA de l’évaluateur, du helper de crop et du lecteur produit ; l’agrégat vérifie ces hashes, les scopes, UNKNOWN/REVIEW_REQUIRED et admission false. Les premières sorties, dont le faux chemin JPEG, restent archivées dans `initial-campaign/` et ne qualifient pas le correctif.

**Résultat nominal : 2/9 variantes complètes, 70/81 concordances et 30/63 chemins, donc 33 omissions.** T81 est corrigé, mais les autres pertes OCR ne sont pas corrigées. Elles restent bloquées ; la robustesse globale est NON QUALIFIÉE. Le témoin et contraste1.05 retrouvent9/7 ; aucun faux chemin ni affirmation critique interdite observé sur les17cas finaux.

| Variante | Concordances /9 | Chemins candidats | Omissions autorisées | Faux chemins | Refus |
|---|---:|---:|---:|---:|---|
| identity | 9 | 7 | 0 | 0 | — |
| brightness_0.97 | 7 | 2 | 5 | 0 | — |
| brightness_1.03 | 8 | 4 | 3 | 0 | — |
| contrast_0.95 | 8 | 4 | 3 | 0 | — |
| contrast_1.05 | 9 | 7 | 0 | 0 | — |
| blur_035 | 8 | 3 | 4 | 0 | — |
| jpeg_85 | 7 | 1 | 6 | 0 | — |
| resample_0.9 | 7 | 0 | 7 | 0 | — |
| resample_1.1 | 7 | 2 | 5 | 0 | — |
| erase_NON | 8 | 4 | 0 | 0 | — |
| erase_async | 8 | 1 | 0 | 0 | — |
| erase_centre | 8 | 5 | 0 | 0 | — |
| erase_first_head | 9 | 3 | 0 | 0 | — |
| contradict_T89 | 9 | 0 | 1 | 0 | DIAGRAM_BRANCH_AMBIGUOUS |
| blur_15 | 0 | 0 | 7 | 0 | LABEL_CROP_LIMIT |
| contrast_0 | 0 | 0 | 7 | 0 | LABEL_CROP_LIMIT |
| dpi_300_unqualified | 0 | 0 | 7 | 0 | TOPOLOGY_SCALE_UNQUALIFIED |

L'effacement de la première pointe conserve seulement les trois chemins du moteur neuf, sans toucher les deux nœuds critiques `existing/equipped` ; c'est une restitution partielle admissible au protocole, pas un contournement. La contradiction T89 est refusée comme ambiguë. Flou fort/contraste nul donnent désormais LABEL_CROP_LIMIT : aucun candidat n'est restitué parce que la découverte de nœuds a échoué et les boîtes restantes dépassent la limite du label. Échelle300 reste refusée.

Le correspondant CEE est retrouvé dans identité, luminosité0.97/1.03 et contraste0.95/1.05. Les autres variantes peuvent omettre cette sortie : absence explicite, jamais remplacement par une éligibilité réelle.

## Défaut de topologie révélé et corrigé

Le succès de T81 révèle sur JPEG85 un ancien contournement : le lecteur restitue `new→async` sans la jonction intermédiaire alors qu'une branche arrive à deux pixels de la route verticale, sans contact qualifié. Cette sortie compte comme faux chemin même si la condition métier finale ressemble à une référence. La garde exige maintenant que les proximités perpendiculaires à≤3pixels sans contact démontré rendent la route traversante UNKNOWN ; aucune liaison ou jonction n'est inventée. Les régions non résolues sont conservées et la version de lecteur devient `axial-150dpi-v3`.

Rouge : deux tests gaps2/3 échouent avec PIXEL_TOPOLOGY_CANDIDATE au lieu de UNKNOWN ; vert ensuite. Un troisième test préserve une ligne réellement indépendante à gap4. Le test du petitI adjacent au crop échoue pour44/45 avant le contrôle du bord réel du trait puis passe avec refus explicite. Sept tests privés de crop passent.

Fichiers produit : `backend/app/modules/dce/infrastructure/diagram_topology_reader.py` et `backend/tests/application/test_diagram_topology.py`. Développés dans le worktree du sujet, intégrés au checkout principal seulement après135tests verts et vérification des hashes initiaux. Les37autres fichiers logiciels hérités sont inchangés. L'évaluateur/crop reste une preuve locale privée, pas une nouvelle API ni un lecteur produit déployé.

## Contrôles

- 135/135 tests combinés topologie/nœuds/coverage/assemblage/chemins ; trois nouvelles régressions produit. Sept tests privés de crop ; huit assertions du vrai grader.
- Ruff backend/scripts vert,1207fichiers formatés ; mypy622sources vert ; diffcheck vert.
- Semgrep1.179.0,225règles,2fichiers produit :0finding/0erreur, aucun fixpointtimeout. Contrôle des scripts privés :0finding/0erreur mais une règle boto3 hardcoded-token atteint un fixpointtimeout sur l'évaluateur monoligne ; preuve partielle de sécurité, sans scanSecrets.
- Suite backend complète : **2532/2532**,0échec/0ignoré,29warnings,1616,97s (26min57),408fichiers répartis exhaustivement en102lots disjoints ; couverture totale **88,25%** (lignes91,36%,branches72,54%) et seuil final85,50% maintenu. PostgreSQL tmpfs local explicitement jetable,384MiB,127.0.0.1 ; conteneur supprimé et absence vérifiée dans cleanup-receipt.json. Aucun service live.

## Limites restant ouvertes

Les onze concordances textuelles manquantes et les routes raster encore ambiguës restent UNKNOWN ; aucune substitution I/l/1, aucune négation supprimée, aucun relâchement de couverture. Les probes min512/min736 et lignes seules n'ont pas démontré la correction et ne sont pas adoptées. La promesse d'analyse complète demeure interdite. OCR primaire/boîtes conservés,ROI fixe,traits axiaux/seuils18px/3px/150DPI : qualification locale d'une page uniquement, pas corpusGolden. A1 non admis,A2HOLD,NO-GO public.

La revue finale indépendante vérifie17résultats,5878ancres et70crops de labels reconstruits depuis les pixels : zéro divergence de scope ou de SHA. Les deux cas9/7 ne garantissent pas un graphe entièrement résolu : une route hors des sept chemins reste inconnue sur le témoin. «2/9» mesure seulement la restitution de la référence locale, jamais une analyse complète. Les diffs `topology.diff` et `topology-tests.diff` sont conservés avec versions antérieures dont les SHA correspondent exactement aux hashes de reprise.

Les contrôles techniques de ce correctif sont vérifiés ; la correction des onze occurrences de cadres non concordants et des33omissions reste ouverte. Aucun achèvement de la robustesse ni de l’analyse complète n’est revendiqué. WIP local non commité,aucun push.
