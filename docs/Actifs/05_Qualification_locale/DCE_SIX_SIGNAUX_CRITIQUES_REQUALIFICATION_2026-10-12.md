# Essais DCE — six omissions critiques corrigées — 12 octobre 2026

## Statut et périmètre

Correction locale des six omissions du registre natif RC, avec requalification des 50 supports source/page/type. Cette preuve ne qualifie ni les douze axes métier complets, ni les valeurs normalisées, ni l’applicabilité métier d’un lot.

A1 non admis, A2 générique HOLD, NO-GO public. Les annotations restent des références techniques non validées par les rôles humains. Aucun backend live, corpus importé en base métier, VPS, déploiement, push, effet P3 ou dépôt externe. Corpus, citations et preuves détaillées restent hors Git.

Base `30f26934430095632000a1d82519f61dbb4c6411`; checkout principal `/home/noor/PROJECTS/BTP/SMART_AO_V8`, branche `codex/reconcile-smartao-20261009`. Worktree `codex/dce-six-signals-20261012` depuis cette base avec overlay explicite des 22 fichiers de code/tests/verrou déjà présents; WIP antérieur préservé.

## AS-IS, risques, insertion, plan et tests

**AS-IS :** motifs absents, un premier signal dont la citation ne couvrait pas les autres critères de la même page, et sous-traitance exclue des RC.

**Risques :** relecture v3 modifiée rétroactivement, directive héritée du mauvais lot, parcours masquant le signal RC, coût non borné sur texte externe, promotion des sources REVIEW_REQUIRED.

**Insertion :** analyse déterministe existante, lecteur SQL des risques et tests domaine/application. Aucune migration, dépendance ou interface visible ajoutée.

**Plan minimal exécuté :** régressions synthétiques rouges; règles v4 additives et citations par clause; raccord lecteur RC; reanalyse de fragments natifs immuables COMPLETED; mesure identique des 50 points; contrôles, revue et synchronisation du plan.

## Corrections et résultat des six points

| Dossier | Page physique | Fait critique | Type conservé | Règle v4 |
|---|---:|---|---|---|
| DCE-01 | 13 | Pondération qualité environnementale/sociale | RC_AWARD_CRITERION | AWARD_NAMED_WEIGHTING_V4 |
| DCE-01 | 13 | Pondération prix | RC_AWARD_CRITERION | AWARD_NAMED_WEIGHTING_V4 |
| DCE-03 | 16 | Échéance exprimée dans le corps | RC_SUBMISSION_DEADLINE | SUBMISSION_DEADLINE_BODY_V4 |
| DCE-03 | 6 | Visite de caractère obligatoire | RC_SITE_VISIT | SITE_VISIT_CHARACTER_V4 |
| DCE-03 | 16 | Restriction de sous-traitance | CCAP_SUBCONTRACTING | RC_SOUS_TRAITANCE_V4 |
| DCE-03 | 18 | Critère prix numéroté et pondéré | RC_AWARD_CRITERION | AWARD_NAMED_WEIGHTING_V4 |

La taxonomie historique `CCAP_SUBCONTRACTING` désigne le risque; la famille documentaire reste **RC**, sans reclassification en CCAP. Le lecteur accepte ce type depuis RC seulement; autres risques CCAP/CCTP restent limités à leurs familles. La lecture demeure Patron, tenant-scopée, avec `REVIEW_REQUIRED`; aucune permission Collaborateur ou confirmation humaine créée.

Les nouveaux motifs utilisent toutes leurs occurrences, chacune avec une citation propre à sa clause, offsets UTF-8 vérifiés et limite1000octets. Les règles historiques ne sont pas élargies sous leur ancien identifiant. `ANALYZER_VERSION=4`, identités de commande/analyse/observations déterministes et distinctes du v3; validations v1–v3 conservées. Les 545 observations v3 archivées sont revalidables par le code courant.

## Requalification des 50 points

| État | Avant v3 | Après v4 |
|---|---:|---:|
| SIGNAL_SUPPORTED | 12 | 18 |
| CONFIRMED_SIGNAL_OMISSION | 6 | 0 |
| NO_TARGET_RULE_IN_RC_REGISTER | 19 | 19 |
| SOURCE_NOT_ELIGIBLE | 13 | 13 |

| Dossier | Points | Signaux étayés | Sans règle cible | Sources non éligibles |
|---|---:|---:|---:|---:|
| DCE-01 | 24 | 10 | 14 | 0 |
| DCE-02 | 5 | 3 | 2 | 0 |
| DCE-03 | 10 | 5 | 3 | 2 |
| DCE-04 | 11 | 0 | 0 | 11 |

Les 50 citations sont retrouvées sur leur page physique exacte. Le comparateur exige dossier, SHA-256 source, version racine, page, citation et type attendu; seules les variations de mise en page sont ignorées, pas les chiffres ou la ponctuation. Les neuf sources des 50 références ont leurs octets snapshot SHA-256 revérifiés. Le ledger1000lignes et les statuts d’extraction restent identiques; les417projections antérieures restent intactes. Reanalyse séparée des seules sources COMPLETED, sans OCR supplémentaire ni relèvement de lisibilité.

Les 13 références non éligibles sont exactement les mêmes. Les19points sans règle cible ne sont ni « compris » par ce registre ni déclarés absents de tous les autres modules. `normalized_value_accuracy=NOT_MEASURED`, `whole_dce_analysis_claim=false`, `human_validation=NOT_PERFORMED`. Une mesure de six omissions corrigées sur cet échantillon ne prouve pas le rappel global du logiciel.

## Preuves et vérification

- TDD initial : sept rouges (six supports et version4), puis verts; sources non classifiées toujours sans nouveau risque.
- Revue : obligation de seconde visite proche initialement qualifiée facultative, rouge→vert dans les deux ordres; boucle de citation rescannant tout le fragment, rouge100044→vert<=1002 caractères scannés.
- Lecteur PostgreSQL : rouge0signal→vert1signal RC; famille exacte, replay sans effet additionnel, tenant étranger vide.
- Ciblés :146tests réussis avant la dernière borne de scan;39domaine réussis après cette borne. La suite finale globale couvre le snapshot exact ci-dessus.
- Ruff global et format1192fichiers; mypy1034sources; `git diff --check` verts.
- Semgrep1.179.0, `p/security-audit`,225règles/4fichiers/0finding/0erreur, métriques désactivées; première tentative sans accès réseau non exécutée, scan final effectué après téléchargement des seules règles. Detect-secrets0finding; Bandit moyen/haut0finding. Aucun résultat envoyé.
- Revue indépendante finale : P1/P2 corrigés, aucun finding restant dans le delta;100assertions de fenêtres/offsets identiques et2000occurrences de bornage3,239s→0,074s. Revue technique, pas validation humaine.

**Suite backend complète avec couverture : 2301/2301 réussis, couverture 87.99 %, seuil CI85,50 % respecté.** Deux départs ont été volontairement interrompus pour intégrer les constats de revue; leurs22/138tests partiels ne sont pas une qualification globale. Le run final terminé utilise PostgreSQL local tmpfs et le seuil85,50% inchangé. Durée1318,63s (21min58); résultat consigné dans `backend-global-qualified.log` et `coverage-qualified.xml`. Deux avertissements historiques : dépréciation Starlette/httpx et attribut Pydantic Field.alias sans effet; aucun test échoué.

Preuves privées : `/home/noor/.local/share/smartao-proofs/dce-six-signals-20261012/`, score `critical-measurement-50-v4-qualified.json`, intégrité/revue/journaux/hashes séparés. SHA-256 du score : `4bf5283db8e3433463af9b183d72f9a1bcea8c13d9b1fd97711f8a20a4713696`.

Méthode : Superpowers using-superpowers/brainstorming borné/systematic-debugging/writing-plans/TDD/requesting-code-review/verification-before-completion; ECC verification-loop. Graphify et Serena pour orientation, Basic Memory pour miroir. Jev/Manus non requis pour quatre règles déterministes; OpenDesign/Impeccable inapplicables, aucune modification UI. Aucun nouvel exercice Docling/OR-tools dans cette tranche; leurs qualifications antérieures ne prouvent pas la couverture des pièces exclues.

## Limites et suite

La lisibilité des pièces critiques DCE-03/04, l’applicabilité métier par lot, les valeurs normalisées et la couverture exhaustive restent à qualifier. Aucun contrat P0–P7, FINANCIAL_PRIVATE, MFA ou effet métier de dépôt modifié; les essais synthétiques ne constituent aucun GO produit.

Fichiers du delta :

- `backend/app/modules/dce/application/analysis.py` : quatre motifs additifs v4 et fenêtres par clause bornées.
- `backend/app/modules/dce/infrastructure/contract_risk_reader.py` : sous-traitance RC visible dans le lecteur existant avec famille réelle.
- `backend/tests/application/test_dce_rc_analysis.py` : persistence/lecture/replay/tenant RC sur PostgreSQL.
- `backend/tests/domain/dce/test_rc_critical_signal_coverage.py` : supports, versions, sources inconnues, directives opposées et borne de scan.

Prochaine étape : ESSAIS DCE — qualifier l’extraction complète des deux PDF critiques non éligibles de DCE-03/04 par une preuve locale page par page, puis requalifier les 13 points exclus sans lever REVIEW_REQUIRED sans preuve. A1 non admis, A2 générique HOLD et NO-GO public maintenus.

## Clôture de l’intégration locale

Checkout principal :152tests ciblés/documentaires réussis en21,46s après intégration, hashes du delta identiques au worktree qualifié; Ruff/format/mypy/diff-check revérifiés. Plan :case de correction cochée, journal append-only enrichi, une seule prochaine tranche. Basic Memory synchronisé via édition explicite puis relu, prochaine étape exacte vérifiée. Le CLI overwrite a refusé le conflit sans mutation; l’édition MCP conserve le corps historique et fusionne les seuls champs courants. PostgreSQL tmpfs de cet essai supprimé après contrôle identifiant/nom/label/mounts; aucun autre conteneur supprimé. WIP non commité, aucun push.
