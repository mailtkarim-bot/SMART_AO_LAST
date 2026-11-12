# Rappel RC sans lot explicite — 17 octobre 2026

## AS-IS, risques et plan

Checkout principal codex/reconcile-smartao-20261009, HEAD30f2693, WIP conservé. Index/plan/CT2-083 et décision E5 candidat relus; aucun moteur actif remplacé. Diagnostic CPU réel sur6sources de développement :6segments intégraux, clause négative visite classée3 à0.834708968 sous seuil0.85; variante « Quelles obligations de visite sont prévues ? » met les3sources pertinentes sous seuil (0.840864/0.823844/0.801281). Ce sont des refus de score, pas des pièces absentes ni une segmentation tronquée. Rapport privé diagnostic.json, profil v3, aucun réglage après lecture d'un nouveau jeu tenu à l'écart.

Risques : abaisser un seuil global, rattraper un faux sujet ou une condition tronquée, masquer budget/omissions, inférer un lot, fuiter une source via trace. Plan minimal : politique v4 explicite, seuil dense inchangé; rappel lexical seulement sur grammaire bornée de questions génériques RC sans lot et clauses de même sujet effectivement reconnues. Résultats denses prioritaires puis complément dans top_k; fenêtre diagnostic positive au plus50segments. Motif DENSE_FLOOR/RC_SUBJECT_RESCUE et trace rang/score/seuil/segment/source/hash avant filtrage, sans fait applicable. Portée UNKNOWN et DPGF refusée avant source/encodeur.

- [x] Rouge/vert sur clause négative sous seuil, question générique alternative, faux sujets/questions spécifiques, clauses tronquées, fenêtre/top_k, provenance, confidentialité, source modifiée, retry, UNKNOWN et refus DPGF.
- [x] Coder profil/service/trace/CLI sans branchement actif; v1/v2/v3 conservent leur identité.
- [x] Revue indépendante et suites pertinentes, puis gel jeu5 inédit avec gold hors extracteur/encodeur.
- [x] Mesure CPU2/900MiB/600s sans réseau, quatre répétitions, aucune règle changée après mesure.
- [x] Vérification lint/types/diff/secrets/Semgrep, conteneurs retirés; plan/index/journal et Basic Memory actualisés avec limites.

Superpowers diagnostic/cadrage/plan/TDD/revue et ECC ai-regression-testing/verification-loop; aucune UI/API/SQL/dépendance, pas de corpus réel/live/VPS/P3/déploiement/commit/push. A1nonadmis/A2HOLD/NO-GOpublic.

## Code et comportement

Nouveau module `knowledge/application/rc_recall.py` : grammaire finie des questions génériques visite/pièces prises en charge/variantes, sans lot ni qualificatif spécifique. Supplément lexical seulement si le projecteur RC reconnaît dans le segment une clause du même sujet. Aucun abaissement du seuil dense0.85; le classement dense est conservé puis complété dans top_k, fenêtre de50scores positifs au plus. Ce n'est pas une recherche lexicale universelle ni une preuve d'absence sur les512segments possibles.

Profil `rc-recall-v4` explicite dans profile-v4.json, anciennes identités v1/v2/v3 inchangées. `score_trace` conserve IDs source/segment, régions UTF8/hashes, rang dense, score, seuil et décision DENSE_FLOOR/RC_SUBJECT_RESCUE/TOP_K_LIMIT/BELOW_FLOOR. Le CLI vérifie les octets des segments, les sources autorisées et l'accord exact entre hits et décisions sélectionnées. Aucun vecteur stocké dans la preuve.

La revue a trouvé une condition avant segment oubliée par le rescue. Deux rouges (100/10 et1000/150) ont précédé le correctif : préfixe source exact fourni au projecteur, longueur UTF8 vérifiée contre start_byte, conditions recherchées dans préfixe+texte amont. Le rescue et la projection finale utilisent ce contexte. Contre-revue : à0.8 aucun rescue; à1.0 hits denses conservés mais clause UNKNOWN, aucune assertion. Aucun transfert vers un raster ou une autre version.

Portée de requête et réponse restent UNKNOWN sans lot prouvé; pas de couple promu par le rattrapage générique. Sources filtrées/revalidées avant trace; source modifiée retourne sans hits ni scores. DPGF garde son refus avant source/encodeur. Aucun branchement dans factory active, API/UI, SQL, dépendance du projet ou writer métier.

## Régressions et contrôles

14rouges initiaux et rougeCLI observés avant correction. 24tests ajoutés :11grammaire,12service (sélection/budget/refus/provenance/privé/conditions),1CLItrace. Suite pertinente **262réussites**, rejouée à la reprise en1,80s; Ruff backend/scripts et mypy632sources verts, format fichiers concernés et diff vérifiés. Revue indépendante81/81 ciblés puis contre-exemples de frontière corrigés et rejoués. Pas de globale backend/Web ni couverture nouvelle; dernier backend global2881/3avertissements antérieur aux politiques RC. Aucun PostgreSQL de preuve lancé, DB/API/UI inchangées.

Semgrep1.179.0,225règles/10fichiers,0finding/0erreurJSON;1warningfixpoint sur règle python.boto3.security.hardcoded-token à CLI:50 conservé (aucun import/appel boto3 dans ce CLI). Analyse locale, seules règles téléchargées, métriquesoff, aucun upload. Trois checksums publics identiques au profil v3 classés précisément dans .secrets.baseline; anciens triages/plugins/filtres inchangés. Detect-secrets1.5.0 sur copie privée :0nouveau finding non trié. Aucun staging; hook précommit canonique non annoncé PASS avec baseline non indexée.

## Runtime de qualification rétabli localement

Le diagnostic initial avait utilisé smartao-r2-proof:20261014. À la reprise, cette image n'était plus dans le cache local; tentative sans mesure archivée launch-image-error.log. Le runtime de mesure a été reconstitué sans modifier les paquets actifs : base publique Python3.12-slim épinglée sha256:876416ecde9aca2bcc90e1fb0c7a9500bbf749f5788b70f82d4c5a5c2357f8b4 du Dockerfile du dépôt, libstdc++6/libgomp1 installés dans la seule image de preuve. Image réelle sha256:d7c4dcbc6bdbbbd5cc93f13c3d8453cbcc2993c8211d788238bcc67c28141938; libc6=2.41-12+deb13u3,libgomp1/libstdc++6=14.2.0-19. Dockerfile et buildlog conservés horsGit, aucune image poussée.

Packages Python existants montés en lecture seule après le répertoire TorchCPU dans PYTHONPATH; versions vérifiées par l'encodeur (ST5.7.0,Transformers5.15.1,tokenizers0.22.2,numpy2.5.2,safetensors0.8.0,Torch2.13.0+cpu/torchvision0.28.0+cpu). OMP/MKL/OpenBLAS2threads. Les manifestes identifient les roues CPU, pas chaque binaire installé de la machine. Pas de comparaison de performance causale avec le runtime précédent.

Conteneur non privilégié, sans réseau, code/poids/runtime en lecture seule, CPU2/900MiB/swapnul/alarme600s. Mesure terminéeexit0, état archivé, conteneur dédié retiré. Image de preuve locale conservée pour reproduction; aucun service actif touché. Inventaire Docker en lecture seule : conteneur Qdrant existant affiché unhealthy, cause non investiguée hors périmètre et service non sollicité; cette preuve d'index mémoire ne qualifie pas Qdrant.

## Jeu5 gelé et résultat

Fixture btp_rc_recall_heldout_v5.json, SHA84e588558e7e4fff7702e1b0a493032ff964e078633ff55bb22637fad7eae244 :18sources(11éligibles/7exclues),14questions(10positives/4sansréponse). Profil candidate-e5-v1:254b197e86357304d5620155c8bf301aa3946aa34e019f2aa4a1f40fe9c33660. Quatorze empreintes figées avant mesure et revérifiées après reprise; code/profil/jeu inchangés depuis. Gold hors encodeur/parseur; petit corpus synthétique, aucune indépendance statistique générale revendiquée.

| Mesure / gate | Résultat |
|---|---|
| Rappel brut source/evidence@5 |0,90|
| Couverture des requêtes positives évaluables |9/9complètes@5|
| Occurrences de rescue sélectionnées |4 :visite1,obligations2,variantes1|
| Point critique non évalué |DPGF, garde financier avant lecture|
| Refus de politique exacts |DPGF et marge privée|
| Faux candidat sur cas sans réponse |1/4 :visite médicale, sélection dense,0rescue|
| Revue inattendue |visite médicale|
| Portée/UNKNOWN/ancres/source_scope/trace |PASS sur ce jeu|
| p95chaud / premier appel |23,875ms /14,594s|
| PicRSS / cgroup |904512KiB=883,31MiB /900MiBexact|

Trois gates faux : critical_complete,abstention,unexpected_review_signals. **Candidat HOLD/admitted=false**, moteur actif inchangé. Le rappel documenté n'est pas une analyse complète des DCE; le refus DPGF n'est pas transformé en lecture réussie. Le cas médical est un candidat dense hors sujet, pas un élargissement du rescue lexical; il reste à corriger sur des cas de développement distincts. Quatre répétitions stables;42requêtes chaudes incluent refus rapides. Pic mémoire au plafond, aucune marge d'exploitation démontrée. Jeu5 désormais historique : aucune règle/seuil modifié après résultat.

## Invariants et méthode

Tenant/Affaire/version/confidentialité avant encodage/trace; snapshots source/profil incohérents refusés, retry stable, ancrage source/segment/hash exact, conditions amont conservées, UNKNOWN sans inférence de lot ni fait applicable. Aucun accès aux writers MFA/P3/append-only, aucun corpus réel/live/VPS/déploiement/commit/push/GOpublic. HEAD30f2693/WIP conservés; A1nonadmis/A2HOLD.

Graphify orientation puis code vérifié (graphe tronqué), Serena activé, décision Basic Memory relue puis miroir; Superpowers diagnostic/cadrage/plan/TDD/revue/vérification et ECC ai-regression-testing/verification-loop. Aucun SDK nouveau, Context7 non sollicité en plus; Jev/Manus inutiles à ces règles bornées et revue indépendante; OpenDesign/Impeccable/navigateur non applicables sans UI.

Preuves privées ~/.local/share/smartao-proofs/rc-recall-20261017/.

Recomptage indépendant :14/14SHA,132traces/31sélections,4rescues exacts,9/9positives évaluables,refus/UNKNOWN etancres confirmés. Visitemédicale :score0.851169 dense,aucunrescue. Runtimeetperformancesnonreproduitsindépendamment;aucunOOM signalé dansétatarchivé.

Prochaine étape : ESSAIS DCE — reproduire et corriger sur cas de développement les faux rappels denses des questions RC spécifiques, dont visite médicale versus visite de chantier; préserver le rappel générique v4, l’abstention et UNKNOWN, puis qualifier précision et omissions sur un nouveau jeu synthétique gelé. DPGF reste non évaluable et le moteur actif inchangé. A1 non admis, A2 générique HOLD et NO-GO public maintenus.
