# Portée lot de requête candidate — 17 octobre 2026

## Cadrage et plan

AS-IS : v2 produit des couples sourcés de même lot/version, mais ne prouve pas le lot demandé; deux occurrences hors lot sur jeu3. Garde financier DPGF avant toute source/encodage. Checkout principal HEAD30f2693, WIP conservé; CT2-083/UNKNOWN et aucun remplacement actif maintenus.

Risques : portée inventée, source masquée, clause ambiguë exclue à tort, refus financier pris pour analyse négative. Insertion : parseur borné de requête et projection contextualisée, politique v3 explicite; v1/v2 et droits inchangés. Pas d'API/UI/SQL/dépendance.

- [x] TDD sur lot explicite et ancre UTF8, absence/multiplicité/plage/négation/condition/identifiant ambigu, deux remontées hors lot, sources brutes et inconnus conservés, retries et refus financier avant source/encodeur.
- [x] Coder le parseur/projection et le profil v3; attribuer les preuves hors portée sans les supprimer. Tracer le refus financier dans la qualification sans modifier le garde ni déclarer DPGF lue.
- [x] Figer un jeu4 synthétique inédit avant mesure; tester couples, portée de requête, inconnus et refus attendus, gold hors extracteur/encodeur.
- [x] Mesurer E5CPU réel hors réseau, CPU2/900MiB/600s; conserver échecs et abstentions, sans réglage sur ce jeu.
- [x] Revue indépendante, suite pertinente, lint/types/diff/secrets/Semgrep, plan/index/journal et Basic Memory synchronisés.

Superpowers cadrage/plan/TDD/revue et ECC ai-regression-testing/verification-loop. Exécution native sur le WIP autorisé; aucun commit/push, live, corpus réel, VPS, P3, déploiement ou GO public. A1 non admis, A2 générique HOLD.

## Implémentation

Nouveau module `knowledge/application/rc_query_scope.py` : lot explicite unique, ancre UTF8 exacte, refus des absences/multiplicités/plages/exclusions/conditions/identifiants non prouvés. Grammaire bornée, pas de compréhension universelle du français. `scope_rc_projection` ne rattache que les clauses et couples du lot prouvé; les régions source de lot inconnu restent UNKNOWN. Si la requête n'a pas de lot prouvé, aucune clause connue ni couple n'est promu. Les preuves reconnues non rattachées sont conservées dans `rc_unscoped_evidence`; tous les hits bruts restent présents. Une recherche sans résultat conserve aussi la portée de requête sans conclure à l'absence d'exigence.

Service candidat : politique `rc-query-lot-v3` choisie par `profile-v3.json`, nouveaux champs query_lot et rc_unscoped_evidence. Identités v1/v2 historiques inchangées; poids/runtime/préfixes/segmentation/seuil inchangés. Le garde financier est exécuté avant parsing/source/encodeur, sans modification de droits ou de son motif d'exception. Aucun branchement actif/API/UI/SQL/dépendance.

CLI : gold indépendant expected_query_lot/expected_query_anchor/expected_refusal, comparaison d'ancre exacte, contrôle des clauses/liens et preuves non rattachées contre les octets source. UNKNOWN de requête reconnu par gold+état+raison, sans inventer de source déclencheuse. `policy_refusal` porte code FINANCIAL_RETRIEVAL_SCOPE_REQUIRED et stage BEFORE_SOURCE_AND_ENCODER; `non_evaluable_queries` conserve tous les refus réels. Les métriques documentaires brutes ne sont pas corrigées pour faire passer un gate : un refus ne prouve aucune lecture ni complétude.

## Régressions et revue

20rouges parseur,5rouges service et1rouge CLI observés avant corrections; régression du gate de revue sur requête ambiguë rouge puis verte. La revue indépendante a trouvé des exclusions/conditions/plages reconnues à tort comme lot4. Six rouges puis trois rouges supplémentaires (ponctuation Unicode et service) ont précédé le correctif. Contre-revue indépendante58/58 verts, aucun nouveau défaut bloquant établi; portée de revue bornée, pas de validation humaine métier.

36tests ajoutés :28parseur,7service,1CLI. Suite pertinente finale **238réussites en1,90s**, incluant knowledge, encodeurs, CLI et architecture; Ruff backend/scripts et format7fichiers verts, mypy631sources vert. Diff sans whitespace. Pas de suite globale backend/Web ni nouvelle couverture : dernière globale2881/3avertissements antérieure aux politiques RCv2/v3; aucun changement DB/API/UI. Aucun PostgreSQL nécessaire ou lancé dans cette tranche.

## Jeu4 gelé / mesure réelle

Fixture `btp_rc_query_scope_heldout_v4.json`,18sources dont11éligibles/7exclues,14questions dont10avec sources attendues et4sansréponse. SHA `b5b1a38a911ea066478f81903609d719ea78cc41578ad37de4d5bab22c6ca914`. Profil `candidate-e5-v1:04bdf7f8d98e3274cc0d5c208a3279fa552bca6bbe5267426a3ced37b719a3e1`. Treize empreintes figées avant première mesure, inchangées après. Gold hors encodeur/parseur; nouveau jeu synthétique après développement, pas une indépendance statistique démontrée.

E5CPU réel dans conteneur non privilégié sans réseau, code/poids/runtime en lecture seule, CPU2/900MiB/swapnul/alarme600s. Quatre répétitions stables; finexit0, état archivé puis conteneur dédié retiré. Aucun réglage après lecture des résultats.

| Mesure / gate | Résultat |
|---|---|
| Couples attendus / inattendus |3/3 /0|
| Portée/ancre exacte de requête et projection par lot |PASS sur les requêtes effectivement évaluées|
| UNKNOWN source attendu, revue, absence de revue inattendue |PASS|
| Refus de politique attendus |j4-dpgf etj4-private, exacts et non évaluables|
| Scope source et ancres source, y compris non rattachées |PASS|
| Rappel documentaire brut@5 et@10 |0,833333, inférieur au seuil0,90|
| Cas critiques sans couverture complète@5 |j4-no-scope (2sources manquantes) etj4-dpgf (refus avant lecture)|
| Cas sansréponse avec candidat |0/4, refus financier compris|
| p95chaud / premier appel |23,6147ms /16,9472s|
| PicRSS / cgroup |865852KiB=845,56MiB /900MiBexact|

Deux gates restent faux : evidence_recall_at_5 et critical_complete. La requête générale sans lot ne retrouve qu'une des trois sources attendues; son scope reste correctement UNKNOWN. Le refus DPGF est visible et n'est pas une omission attribuée au parseur ni une preuve d'analyse négative. Les autres requêtes non refusées ne démontrent pas une analyse DCE complète. **Candidat HOLD/admitted=false**, moteur actif inchangé. Jeu4 désormais historique, aucune calibration future sur ses scores. Les42requêtes chaudes incluent refus rapides et petites entrées; latences entre jeux non directement comparables. Piccgroup au plafond : aucune marge mémoire d'exploitation démontrée.

## Sécurité, limites et outils

Semgrep1.179.0,225règles/9fichiers,0finding/0erreurJSON;1warningfixpoint conservé sur la règle boto3 hardcoded-token dans le CLI, qui n'importe ni n'appelle boto3. Analyse locale/règles téléchargées seules/métriquesoff, pas d'upload; aucune sécurité exhaustive attestée. Detect-secrets1.5.0 :3checksums publics du profil v3 identiques à v2 triés is_secret:false, aucun plugin/filtre/ancienne entrée changé. Contrôle sur copie privée de baseline :0nouveau finding non trié. Baseline canonique non indexée, aucun staging; ne pas annoncer le hook précommit PASS.

Invariants vérifiés : filtrage tenant/Affaire/version/confidentialité existant avant projection, sources/hashes/ancres conservés, refus de changement de snapshot, retry stable, aucun lot déduit du ranking, UNKNOWN sans preuve, garde financier avant source/encodeur. Les writers MFA/P3/append-only ne sont pas touchés. A1nonadmis/A2HOLD/NO-GOpublic, aucun corpus réel/live/VPS/déploiement/P3/commit/push. WIP conservé, HEAD30f2693.

Superpowers cadrage/plan/TDD/revue/vérification et ECC ai-regression-testing/verification-loop utilisés; Graphify orientation (graphe tronqué, vérification du code), Serena activé, décision Basic Memory relue et miroir mis à jour. Aucune API externe nouvelle à rechercher dans Context7; encodeur inchangé. Jev/Manus inutiles à ces règles déterministes et à cette revue; OpenDesign/Impeccable/navigateur non applicables sans UI.

Preuves privées : ~/.local/share/smartao-proofs/rc-query-lot-20261017/.

Contre-vérification indépendante du rapport :3paires exactes/0inattendue,24ancres,refus et métriques confirmés sans nouvelle exécution modèle;prochain travail borné au rappel sans lot explicite.

Prochaine étape : ESSAIS DCE — reproduire et corriger sur cas de développement les omissions de retrieval RC des requêtes sans lot explicite, en traçant segmentation, scores et seuil; conserver UNKNOWN sans inférer de portée, puis requalifier sur un nouveau jeu synthétique gelé. DPGF reste non évaluable sous le garde financier; aucun moteur actif remplacé. A1 non admis, A2 générique HOLD et NO-GO public maintenus.
