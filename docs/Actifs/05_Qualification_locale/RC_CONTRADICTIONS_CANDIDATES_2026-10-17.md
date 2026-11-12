# Contradictions RC candidates — 17 octobre 2026

## Cadrage et plan d'exécution

AS-IS : politique rectification-signal-v1 limitée aux marqueurs explicites, conflit implicite visite manqué sur le jeu2. HEAD30f2693, checkout principal codex/reconcile-smartao-20261009 avec WIP conservé. CT2-083 impose REVIEW_REQUIRED et aucune priorité contractuelle implicite; les sources opposées doivent rester visibles.

Risques : mélange tenant/Affaire/version/lot, confusion non-obligatoire/interdit, condition ignorée, portée héritée sans preuve, calibration sur jeu tenu à l'écart.

Insertion : module pur de projection de clauses/couples dans knowledge/application et branche candidate explicite rc-opposition-v2. Le profil v1 garde son identité et son comportement; seul un nouveau profil v2 demande cette politique. Sources sélectionnées et revalidées par le service existant. Aucune API, UI, SQL, dépendance ni factory active modifiée.

Périmètre borné : formulations déclaratives de visite obligatoire/facultative, mémoire technique/DC1/DC2/DPGF exigés ou non, variantes autorisées/interdites. Une clause soutient une seule portée lot explicite dans la même phrase; portée absente/multiple, condition, formulation ou négation non reconnue restent UNKNOWN. Aucun héritage de titre/page ni extraction juridique générale. Les textes non couverts restent mesurables, aucune complétude déduite. Rectificatif = signal distinct, jamais priorité.

- [x] Écrire et observer les régressions rouges : polarités, opposition, rectificatif, lot/version/tenant, conditions, régions UTF8/hash.
- [x] Coder projection, couples sourcés, politique v2 opt-in et tests de service/retry/source périmée sans changer le moteur actif.
- [x] Geler un jeu3 synthétique différent du développement avant la première mesure; tracer les attendus hors extracteur/encodeur, exactitude des couples et inconnus.
- [x] Qualifier avec E5CPU réel, encodages existants et budgets CPU2/900MiB/600s; aucune modification de règle après résultats.
- [x] Contre-revue indépendante, suites pertinentes, lint/types/diff/secrets puis Semgrep; finaliser preuves, plan et miroir Basic Memory.

Exécution native suivant Superpowers brainstorming/plan/TDD et ECC ai-regression-testing/verification-loop. Pas de commit/push, aucun corpus réel/live/VPS/déploiement/P3. A1 non admis, A2 générique HOLD, NO-GO public.

## Code et contrats

Nouveau `knowledge/application/rc_candidate_conflicts.py` : preuves de clause immuables, hash source/segment, tenant/Affaire/version, lot, sujet, polarité et région UTF8 exacte; liens OPPOSITION ou RECTIFICATION_OPPOSITION, applicabilité UNKNOWN. Portée manquante/multiple, condition, phrase interrogative/non terminée ou premier fragment d'un segment tronqué : région UNKNOWN visible. Maximum50segments/256clauses. Les conditions amont restent conservativement actives dans le segment; cela peut réduire le rappel, aucune fin de portée devinée.

`candidate_retrieval.py` projette uniquement les hits déjà filtrés puis revalidés, sans élargir les droits. La politique `rc-opposition-v2` est explicite dans `profile-v2.json`; v1 conserve son SHA historique. Les poids/runtime/préfixes/seuil0.85/segmentation ne changent pas. Aucun contrat actif, port public, migration ni dépendance ajouté.

Le CLI conserve clauses/liens/inconnus et mesure couples exacts (deux sources, sujet, lot, version, type), ancres contre les octets de la fixture et présence des UNKNOWN attendus. Le gate UNKNOWN exige au moins une région de la source attendue, pas une couverture exhaustive de ses ambiguïtés. Le gold n'entre ni dans l'encodeur ni dans le projecteur. Les textes hors grammaire restent inconnus; absence de signal n'est pas absence de contradiction.

## TDD, revue et suites

20rouges initiaux puis verts; limite et intégration ajoutées; deux régressions question/phrase tronquée rouges puis vertes. Vérification des deux tests de service contre les modules préchangements, chargés en mémoire sans modifier le checkout : deux échecs attendus (politique v2 absente), puis suite actuelle verte. Les premières erreurs d'import du helper de test ont été corrigées dans le harness, elles ne sont pas des bugs produit.

La revue indépendante reproduit une condition perdue au saut de ligne et dans une région amont tronquée. Quatre régressions rouges ont précédé le correctif; contre-revue49tests verts et aucun nouveau finding. 30tests ajoutés (27projection pure,2service,1scoreur); suite finale **202réussites en1,93s**, incluant knowledge existant et architecture. Ruff globalbackend/scripts et format des fichiers concernés verts; mypy630sources vert. Aucun run global backend/Web ni nouvelle couverture : dernier global2881/3avertissements précède cette tranche. Pas de migration ni besoin de PostgreSQL pour cette politique non branchée.

## Jeu3 gelé et mesure réelle

Fixture `btp_rc_conflicts_heldout_v3.json`, SHA `03f00c6db83139cd7d677330a4ba6866d58c5380d87af329b82197ba7c87264e` :18sources dont11éligibles/7exclues,12questions dont8positives/4sansréponse. Nouveau corpus synthétique après développement, sans mesure préalable; pas de preuve statistique d'indépendance ou de généralisation. Profil `candidate-e5-v1:3533f073f68bcb0b3f5b2a43776719748421095905f867ae9ab7505d5e9a299f`. Douze empreintes figées avant la première mesure. Aucun fichier de code/profil/jeu modifié depuis.

Conteneur non privilégié, code/poids/runtime en lecture seule, réseau désactivé, CPU2/900MiB/swapnul et alarme600s. Une première tentative de lancement a échoué avant tout encodage car runpy ne positionne pas le répertoire des scripts : chemin d'import ajouté au lanceur, traces conservées; aucun réglage du produit ni résultat de test inféré de cette erreur. Mesure suivante terminéeexit0, quatre répétitions stables; état archivé, conteneur dédié retiré, aucun PostgreSQL lancé.

| Mesure / gate | Résultat |
|---|---|
| Couples attendus |3/3retrouvés|
| Couples inattendus pour la requête |2occurrences : lot13 dans visite14, lot31 dans variantes32|
| Rapprochements entre deux lots différents |aucun observé; ces2couples sont valides dans leur propre lot mais hors requête|
| Rappel source@5 |0,875 (moyenne7/8questions positives)|
| Point critique non examiné |j3-dpgf, refus FINANCIAL_SCOPE_REFUSED avant source/encodeur|
| UNKNOWN attendus observés |2/3; DPGF non examinée|
| Cas sans réponse avec candidat |0/4 (garde financier compris)|
| Scope, réponse UNKNOWN, ancres |PASS;29instances vérifiées indépendamment|
| p95chaud / premier appel |22,434ms /17,265s|
| PicRSS / cgroup |891716KiB=870,82MiB /900MiB exact|

Six gates restent faux : rappel seuil0.90, complétude critique, signaux de revue attendus, absence de revues inattendues, précision des couples pour la requête et refus UNKNOWN attendus. **Candidat HOLD/admitted=false**, pas d'admission Golden DCE ni activation. La garde financière est préservée : l'absence DPGF n'est pas présentée comme une lecture négative du parseur. Le jeu3 est maintenant historique; aucune règle/seuil ajusté pour le faire passer. Comparaisons de latence entre jeux non qualifiées;36requêtes chaudes incluent des refus rapides, mémoire proche du plafond sans marge d'exploitation prouvée.

## Sécurité et limites

Semgrep1.179.0,225règles/9fichiers,0finding/0erreurJSON. Un avertissement fixpoint sur python.boto3.security.hardcoded-token au CLI est conservé; pas d'import/appel boto3 dans ce CLI local, aucune attestation de sécurité exhaustive. Règles téléchargées seules après refus réseau sandbox; analyse locale, métriquesoff, aucun upload. JSON extrait du journal car le wrapper osemgrep installé écrit sur stdout. Trois alertes de checksums du profil v2 sont les mêmes révision/empreintes publiques que v1 : triage précis is_secret:false dans .secrets.baseline, aucun filtre/plugin désactivé ni entrée historique modifiée. Contrôle detect-secrets1.5.0 sur copie privée :0nouveau nontrié. Aucun staging; le hook précommit canonique n'est pas annoncé PASS avec une baseline non indexée.

Invariants vérifiés dans ce périmètre : tenant/Affaire/version/classification avant encodage/projection; liens seulement sur même portée prouvée; régions/hash exacts, retry stable, source modifiée refusée, négations conservées et applicabilité UNKNOWN. Tests de permissions/actions métier/MFA/append-only non ajoutés : aucun accès à ces writers. A1nonadmis/A2HOLD/NO-GOpublic inchangés. Corpus réel, analyse DCE complète, UI, persistance SQL segmentée, marge RAM et qualité universelle de contradiction/abstention ne sont pas qualifiés.

Outils réellement utilisés : Graphify (orientation, graphe tronqué donc code vérifié), Serena projet activé, Basic Memory décision relue puis miroir synchronisé; Superpowers cadrage/plan/exécution native/TDD/revue/vérification et ECC ai-regression-testing/verification-loop. Aucune nouvelle question d'API externe : pas de requête Context7 supplémentaire, contrats de l'encodeur inchangés. Jev/Manus non nécessaires à ces règles déterministes et à la revue indépendante; OpenDesign/Impeccable/navigateur non applicables sans UI.

Prochaine étape : ESSAIS DCE — coder une portée lot explicite de requête pour les clauses et couples RC candidats, avec UNKNOWN sur portée absente ou ambiguë; corriger les deux remontées hors lot sur cas de développement, tracer le refus financier DPGF sans modifier les droits, puis qualifier sur un nouveau jeu synthétique gelé sans activer le candidat. A1 non admis, A2 générique HOLD et NO-GO public maintenus.
