# Preuve du type et rappel typé candidat — 17 octobre 2026

## AS-IS, risques, plan

V5 couple encore type et valeur d'obligation reconnue : deux sources médicales sous0.85 et une clause conditionnelle rejetées sur jeu6. HEAD30f2693,checkout principal/WIP conservés; index/plan/CT2-083/décision E5 relus.

Insertion minimale : preuve technique de type avec ancre source propre, signal documentaire d'obligation distinct, conditions sourcées et valeur UNKNOWN tant que non prouvée. Politique v6 opt-in, rattrapage typé borné dans la fenêtre50/top_k, seuil dense inchangé. Anciennes politiques inchangées, aucune admission de source ni applicabilité déduite.

Risques : type seul pris pour obligation, citations ou mention secourues, condition perdue, mot de négation omis, portée lot inventée, source étrangère visible dans la preuve.

- [x] Rouge/vert preuve de type indépendante, condition/négation/citation/préfixe source, directive non prouvée, budget et ancres UTF8 exactes.
- [x] Coder preuve, rattrapage typé, trace et qualification CLI; préserver garde financier, scopes et anciens profils.
- [x] Revue indépendante et suite pertinente; geler un jeu7 synthétique nouveau avant mesure sans transmettre le gold aux extracteurs/encodeurs.
- [x] Mesurer E5CPU isolé CPU2/900MiB/600s sans réseau; conserver omissions/faux positifs et UNKNOWN, sans réglage après résultat.
- [x] Vérifier lint/types/diff/secrets/Semgrep; retirer conteneur, mettre à jour plan/case/journal/index et Basic Memory.

Superpowers cadrage/plan/TDD/revue et ECC ai-regression-testing/verification-loop. Aucun moteur actif/API/UI/SQL/dépendance du projet/commit/push/live/corpus réel/VPS/P3/déploiement/GO public. A1nonadmis/A2HOLD.

## Clôture locale — 18 octobre 2026

Qualification locale bornée v6 exécutée, candidat HOLD : preuve du type de visite indépendante de la valeur, rattrapage RC_TYPED_RESCUE borné, conditions/négations/citations et UNKNOWN conservés. 44 tests ajoutés, 342 ciblés/architecture réussis; Ruff, mypy633, diff et15SHA verts. Revue indépendante : condition après point/hors segment corrigée après3rouges; contre-revue135tests verte. Jeu7 gelé21sources/19questions E5CPU sans réseau :10/10positives évaluables complètes@5,0fauxcandidat sur8cas attendus sans candidat,5rescues typés et2génériques,1couple exact. Rappel brut source/région90,91%; seule gate critical_complete fausse pour DPGF refusée avant lecture, admitted=false. p95chaud26,030ms,froid16,305s,RSS878,875MiB,cgroup900MiB sans marge prouvée. Semgrep1.179.0/225règles/9fichiers0finding0erreurJSON+1warningfixpoint;secrets0nouveau nontrié/3checksums publics sans filtre/staging. Conteneur exit0 retiré, aucunPG. Contre-lecture indépendante du rapport final interrompue; comptes principaux revérifiés localement. Aucun réglage après mesure, moteur actif/API/UI/SQL/dépendance projet inchangés, aucun commit/push/live/corpus réel/P3/déploiement/GOpublic;HEAD30f2693/WIP conservés. Suite backend globale et Web non rejouées pour cette tranche.

### Code et contrats

- `rc_candidate_conflicts.py` : `RcSignalAnchor`, preuve VISIT_MEDICAL/VISIT_SITE distincte de la valeur d'obligation, directive CANDIDATE/UNKNOWN, marqueurs conditionnels sourcés. Une simple mention ne constitue pas une obligation; les citations restent refusées.
- `candidate_retrieval.py` : politique opt-in `rc-type-proof-v6`, sélection typée bornée fenêtre50/top_k avec priorité dense, seuil0.85 inchangé; une entrée non sélectionnée porte TOP_K_LIMIT. Revalidation avant toute preuve/trace; garde financier avant lecture/encodage.
- `embedding_profile.py`, `profile-v6.json` : identité additive, profils v1–v5 préservés; aucun branchement au moteur actif.
- `qualify_candidate_retrieval.py` : sérialisation et vérification des preuves, ancres UTF8/hash/lot/source, sélection typée et traces cohérentes.
- Régressions : `test_rc_visit_type_proof.py`, `test_candidate_retrieval.py`, `test_candidate_qualification_cli.py`; fixture `btp_rc_visit_type_heldout_v7.json`.

Le contexte complet du fragment doit correspondre à son SHA et aux octets du segment/préfixe. Une condition même après un point ou hors segment conserve valeur et nature UNKNOWN. Les ancres conditionnelles sont des marqueurs, pas une interprétation des conditions ni une preuve d'applicabilité. Maximum16marqueurs et256clauses/preuves; la portée conditionnelle complète reste à qualifier. Une condition indépendante peut donc provoquer un UNKNOWN conservateur.

### Preuves reproductibles

Répertoire privé : `~/.local/share/smartao-proofs/rc-type-proof-20261017/`.

- `red.log` :11échecs attendus/1réussite avant implémentation; `budget-red.log`, `cli-red.log` puis `suffix-red.log` (3échecs) précèdent leurs corrections.
- `targeted-final.log` :342réussites en1,95s; Ruff backend/scripts et mypy633sources verts. Les tests couvrent refus, scopes, versions, source modifiée, condition/citation/négation, budgets et ancres; ils ne prouvent pas une lecture DCE entière.
- `code-before-heldout-sha256.txt` :15fichiers gelés avant mesure, revalidés après reprise; aucun réglage sur jeu7. Fixture SHA256 `f48f609009db035d70d8a6dad57f0dbd43d2f60545db55232287f13444c0cc50`.
- `heldout.json`, `heldout-run.log`, `heldout-container-state.json` : exécution CPU réelle,4répétitions stables,255traces; sources14éligibles/7exclues. Deux requêtes non évaluables DPGF/marge; les comptes bruts gardent DPGF manquante.
- Runtime `smartao-rc-cpu-proof:20261017`, image `sha256:d7c4dcbc6bdbbbd5cc93f13c3d8453cbcc2993c8211d788238bcc67c28141938`, CPU2/900MiB/sansswap/600s/networknone, code/poids/paquets readonly. E5small FP32/L2, préfixes query/passage, threads2, segments1000/overlap150; identité exacte dans rapport/profil. Aucun environnement actif modifié.
- `semgrep.json` :0finding/0erreur, avertissement fixpoint règle python.boto3.security.hardcoded-token sur CLI sans appel boto3. Analyse locale, métriques off; pas de preuve exhaustive de sécurité.
- `secrets-result.json` :0nouveau nontrié;3checksums publics identiques au profilv5 ajoutés précisément à la baseline, sans suppression de filtre. Aucun staging ni hook de commit qualifié.

### Décision et limites

HOLD maintenu; A1 non admis/A2 générique HOLD/NO-GO public. Aucun effet métier ni admission de source. Données uniquement synthétiques, faible échantillon; aucune généralisation aux DCE complets. Pas de nouvelle suite globale backend/Web, ni de preuve SQL du nouveau profil; pas de marge mémoire au plafond900MiB. Migrations sans objet (aucun schéma changé). Revue indépendante de code achevée, contre-lecture finale du rapport non achevée; recomptage local10/10,0/8,gates et hash exécuté à la clôture.

Prochaine étape : ESSAIS DCE — qualifier le profil candidat v6 avec le lecteur DCE réel sur PostgreSQL jetable synthétique : fragments et ancres exacts, extraction incomplète, version remplacée, rectificatif et isolation tenant/Affaire; vérifier les preuves typées et l’invalidation sans activer le moteur candidat. DPGF reste non évaluable. A1 non admis, A2 générique HOLD et NO-GO public maintenus.
