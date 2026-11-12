# Essais DCE — complétude et omissions critiques — 12 octobre 2026

## Résultat et autorité

**Qualification globale des quatre DCE : NON DÉMONTRÉE.** L'inventaire et la mesure locale sont exécutés; les pièces non éligibles, les omissions et les portées inconnues restent visibles. Aucun dossier complet, précision normalisée ou conformité métier n'est déclaré.

Autorités : Product Freeze v3.1 PF2-035, Master métier M2-026/027/029 et cahier technique v3.1 (provenance résolue/déclarée/candidate, UNKNOWN sans invention). A1 non admis, A2 générique HOLD, NO-GO public. Les références sont des lectures techniques IA; aucune validation humaine métier, Corpus Owner ou DPO n'est simulée.

Essai commencé le 11 octobre et achevé le 12 après reprise de la coupure. Base Git `30f26934430095632000a1d82519f61dbb4c6411`, branche principale `codex/reconcile-smartao-20261009`; worktree `codex/dce-completeness-trials-20261011`. Les corrections précédentes non commitées sont reprises à hashes identiques, sans reset/clean/stash. Corpus, originaux, snapshots, citations, références et résultats détaillés restent hors Git.

## AS-IS, risques, insertion, plan et tests

**AS-IS :** analyse lexicale des fragments admissibles, sans preuve que toutes les pièces ou les douze axes métier soient couverts. Les 29 faits pilotes couvraient deux dossiers; aucune mesure des omissions à l'échelle des quatre dossiers.

**Risques :** ignorer une sous-archive, perdre un fichier unsupported/timeout, utiliser des octets modifiés sous un ancien hash, mélanger deux dossiers ayant le même hash, confondre mention et valeur exacte, déduire un lot depuis un nom, écraser une preuve achevée.

**Insertion minimale :** deux CLI de qualification, utilisant les extracteur/classificateur/analyseur natifs existants, et deux fichiers de tests ops. Pas de changement supplémentaire des services métier, du schéma, des portes P0–P7 ou d'une interface visible dans cette tranche.

**Plan :** (1) figer les 12 originaux et leurs hashes; (2) inventorier récursivement et exercer le pipeline natif par pièce avec délai borné; (3) constituer la référence technique indépendante supplémentaire; (4) confronter 50 points au registre natif; (5) tests, revue/scans et suite globale; (6) intégration locale, plan et mémoire.

**Tests :** archives imbriquées, doublons et locators distincts, ZipSlip évité, root/snapshot/projection mismatch, mutation concurrente des octets, symlinks, formats et compression unsupported, timeout, REVIEW_REQUIRED, versions par dossier indépendantes de l'ordre/format du manifeste, refus d'écraser le ledger, source/page/quote/kind exacts et isolation de dossier.

## Inventaire réel et extraction

Les 12 originaux téléchargés sont vérifiés par SHA-256 puis copiés en snapshots privés `0400`. Les dossiers de preuve sont `0700`, JSON `0600`. Les entrées ZIP sont stockées par hash, sans utiliser leur nom comme chemin d'extraction. Chaque ligne conserve locator d'origine, hash disponible, version canonique du dossier et statut. Une version est calculée par dossier à partir de la liste triée des noms/hashes originaux; le hash exact du manifeste est conservé séparément.

**1 000 lignes** : 42 conteneurs d'archive, 236 répertoires et **722 fichiers ou archives illisibles**. Ce sont des occurrences physiques; les doublons de contenu restent visibles et réutilisent une projection. Les totaux ne doivent pas être présentés comme autant de documents métier uniques.

| Dossier alias | Lignes | Fichiers/archives illisibles | COMPLETED | REVIEW_REQUIRED | FAILED_SAFE | TIMEOUT | UNSUPPORTED | Archive illisible |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| DCE-01 | 53 | 45 | 17 | 3 | 0 | 0 | 25 | 0 |
| DCE-02 | 167 | 93 | 15 | 18 | 0 | 0 | 60 | 0 |
| DCE-03 | 126 | 34 | 15 | 6 | 12 | 1 | 0 | 0 |
| DCE-04 | 654 | 550 | 185 | 115 | 28 | 34 | 187 | 1 |
| **Total** | **1000** | **722** | **232** | **142** | **40** | **35** | **272** | **1** |

L'archive illisible correspond au faux ZIP HTML déjà diagnostiqué et conservé dans les originaux. L'archive réelle est traitée séparément; le faux fichier ne disparaît pas du suivi.

Les projections natives emploient pypdf/DOCX/XLSX/TXT selon les formats supportés. Classification et analyse ne sont exécutées comme sources admissibles qu'après extraction COMPLETED. Les textes conservés d'une pièce REVIEW_REQUIRED restent utiles au diagnostic et aux comparaisons de source; ils ne deviennent pas une extraction admissible. Aucun OCR/Docling avancé, RAG ou LLM distant n'est automatiquement activé par cet essai.

Limites configurées : 20 secondes par projection native en processus enfant, 128 MiB par pièce, 2 GiB de volume décompressé, profondeur 8 et 10 000 entrées pour le traitement. **L'inventaire ZIP est synchrone; les métadonnées des entrées refusées sont conservées et ne sont pas bornées en nombre par la limite de traitement.** Cet essai ne qualifie pas la résistance générale aux archives hostiles ou un SLA. Les hashes restent inconnus pour une entrée refusée sans lecture; aucune valeur n'est inventée.

## Référence et mesure des points critiques

Référence locale : 29 faits réconciliés pilotes + **21 points supplémentaires** issus d'une seconde lecture bornée de trois PDF pour DCE-03/04. Ces trois hashes ont été vérifiés sur les originaux; 21 citations ont été revérifiées sur leur page physique avec pypdf 6.20.0. Le périmètre DCE-04 supplémentaire couvre le RC; il ne représente pas le CCAP/CCTP ni l'ensemble des travaux.

Le RC DCE-04 page 4 distingue **17 lots : 12 AOO et 5 MAPA**. «12 lots» désignait le périmètre AOO seulement. Page12 : PSE à chiffrage obligatoire pour le lot14. Le précédent dossier a été précisé; aucune sélection de lot ou assimilation des procédures n'est faite.

La mesure exige **dossier + hash des octets + page physique + texte cité + type de signal**. Une projection dont le SHA ne correspond pas est non éligible. La comparaison des glyphes ignore les espaces de mise en page après NFKC/casefold et normalisation des apostrophes; elle conserve chiffres et ponctuation. Une négation supplémentaire n'est pas supprimée. Cela ne prouve pas l'extraction d'une date, unité, valeur normalisée ou portée juridique.

**50/50 supports textuels retrouvés.** Résultat du registre natif testé :

| Dossier | Points | Signal étayé | Omission du signal étayé | Sans règle cible dans ce registre | Source non éligible |
|---|---:|---:|---:|---:|---:|
| DCE-01 | 24 | 8 | 2 | 14 | 0 |
| DCE-02 | 5 | 3 | 0 | 2 | 0 |
| DCE-03 | 10 | 1 | 4 | 3 | 2 |
| DCE-04 | 11 | 0 | 0 | 0 | 11 |
| **Total** | **50** | **12** | **6** | **19** | **13** |

Les six omissions portent sur les poids RSE/prix DCE-01, puis échéance de dépôt, visite obligatoire, sous-traitance classifiée et pondération prix DCE-03. «Omission» signifie ici absence de signal du type attendu étayé par la citation sur la page de référence; ce n'est pas une mesure de rappel global du logiciel ou de justesse d'une valeur normalisée.

Les 19 points sans règle cible ne sont pas déclarés inexistants dans tous les autres modules du produit : ils ne sont pas couverts par le registre RC/CCAP/CCTP exercé. Les 13 points non éligibles ne sont comptés ni comme réussites ni comme omissions du parseur admissible. Tous restent dans le ledger. Les premières comparaisons trop strictes aux espaces de mise en page sont conservées dans la preuve v001; la mesure corrigée est v002.

## Lot/version et anatomie métier

La version locale de chaque dossier est résolue et hachée. **Applicabilité au lot sélectionné : UNKNOWN.** Il n'y a ni Case métier importée ni sélection humaine de lot; les noms de fichiers et mentions d'autres lots ne sont pas transformés en affectation. Les portées explicitement lues dans le RC/STP restent dans la référence comme observations techniques, distinctes de l'applicabilité à une affaire.

Pour M2-026, aucun des douze axes n'est déclaré intégralement qualifié. La grille par dossier du [dossier précédent](DCE_ESSAIS_METIER_DEPENDANCES_2026-10-11.md) reste la liste des contrôles attendus. Pour M2-027, source/version/hash/locator sont audités; conséquences techniques/prix/délai/cash/contrat, responsables, actions, échéances opérationnelles, preuves de levée, décisions humaines et risques résiduels ne sont pas déduits d'une mention. **Précision des valeurs normalisées : NOT_MEASURED.**

La visibilité des pièces non extraites est livrée dans ce registre de qualification local et le bilan; une intégration de ces informations dans l'API/écran Patron n'est pas qualifiée par cette tranche. Le compteur des exigences affichées actuellement ne prouve pas une couverture exhaustive du dossier.

## Fichiers et reproduction

- `scripts/qualify_dce_completeness.py` : snapshots, ZIP/sous-ZIP, refus visibles, native pipeline et version par dossier.
- `scripts/measure_dce_critical_omissions.py` : confrontation source/page/citation/type, SHA contrôlé et états explicites.
- `backend/tests/ops/test_dce_completeness_qualification.py` et `test_dce_critical_omissions_qualification.py` : régressions reproductibles sur octets synthétiques.
- Présent dossier, index et plan actifs; précision Montpellier du dossier précédent.

Depuis la racine, avec manifeste/référence privés :

```bash
PYTHONPATH=backend .venv/bin/python scripts/qualify_dce_completeness.py \
  --manifest /chemin/prive/originals-manifest.json \
  --output-dir /chemin/prive/nouveau-run --per-document-timeout 20
PYTHONPATH=backend .venv/bin/python scripts/measure_dce_critical_omissions.py \
  --ledger /chemin/prive/nouveau-run/ledger.json \
  --reference /chemin/prive/critical-reference-50.json \
  --output-file /chemin/prive/nouvelle-mesure.json
```

Un ledger achevé et une mesure existante ne sont pas écrasés; choisir un nouveau run. Aucun chemin, citation ou donnée réelle d'exemple n'est ajouté au dépôt. Preuves détaillées sous `~/.local/share/smartao-proofs/dce-completeness-trials-20261011/` : manifestes, ledger, projections, référence indépendante, métrique v002, logs TDD/scans et hashes du code testé.

## Vérification

Régressions rouges puis **21 tests ciblés verts**. Ruff/check et format global1191 fichiers, mypy1033 sources verts. Revue indépendante : mismatch SHA du scorer confirmé et corrigé; compression ZIP non supportée vérifiée par contre-épreuve, le refus existant était déjà correct. Protections supplémentaires de comparaison et de conservation des preuves vérifiées; aucun résultat de revue IA n'est une approbation humaine.

**Suite backend entière finale : 2286/2286**, zéro ignoré, **777,36 s (12min57)**, un warning Starlette/httpx; PostgreSQL jetable explicite. Cette passe finale est sans couverture. La campagne globale précédente avec couverture a mesuré **87,95 %**, seuil85,50 % atteint, et **2283 réussites/3 échecs** de tests nominaux dépassant20s sous instrumentation, en2693,52s. Ce run n'est pas annoncé PASS. Les21 tests de qualification corrigés passent ensuite sous couverture en135,82s. Le budget120s concerne seulement les tests nominaux; les tests de timeout court explicite et le défaut20s des essais réels sont inchangés. Le diagnostic ciblé de couverture utilise un seuil nul pour son périmètre réduit; le seuil du projet85,50 % n'a pas été modifié. La suite globale avec couverture n'a pas été rejouée après cet ajustement de fixture.

pytest-cov installé6.3.0 instrumente les processus enfants par fichier.pth et variablesCOV_CORE; source installée et documentation Context7 vérifiées. La fixture de cache corrompu simule une reprise inachevée, séparément du refus d'écraser un ledger achevé. Logs rouges, campagnes interrompues et variantes de mesure sont conservés.

Contrôles : Ruff/check et format1191 fichiers, mypy1033 sources; Semgrep1.179.0 `p/security-audit`,225 règles/4 fichiers/0 finding/0 erreur, métriques désactivées; secrets et Bandit niveau medium/high sans finding sur les nouveaux fichiers. Contrat documentaire/schema5/5. Aucun package, schéma ou source métier supplémentaire modifié; migrations existantes exercées par les suites DB. Intégration principale à hashes identiques sur4 fichiers; WIP préexistant conservé. Travail non commité, aucun push.

**Risque CI distinct :** la campagne instrumentée a duré44min53, proche du budgetbackend45min avant les autres contrôles du job. Le temps CI et un run global instrumenté corrigé restent à qualifier avant livraison. L'essai présent ne baisse aucun seuil ni assertion.

Méthode appliquée : Graphify, Serena activation, Superpowers brainstorming/TDD/dispatching-parallel-agents/requesting-code-review/verification, ECC verification-loop et PDF. OpenDesign/Impeccable inapplicables sans UI visible; Jev/Manus non nécessaires aux comparaisons déterministes. Les CLI utilisent les fonctions existantes et la bibliothèque standard; aucune dépendance nouvelle ou hypothèse d'API fournisseur.

## Invariants et décision

Corpus et données financières/personnelles hors Git, contrôles locaux de provenance et séparation de dossier, archives et refus conservés, aucune promotion UNKNOWN/REVIEW_REQUIRED en certitude. Aucun service métier, tenant/permission, MFA, step-up, effet P3, règle P5, export ou dépôt externe n'est modifié. Les invariant DB/métier sont vérifiés par la suite appropriée, pas par un acte sur un vrai dossier.

**Pas d'admission Golden ou GO public.** Prochaine correction technique : les six omissions de signaux étayés, avec revalidation sur les 50 points et maintien des pièces non éligibles. Les tâches d'applicabilité lot/version, douze axes et lecture des formats/timeout restent ouvertes.

## Suite datée — correction des six signaux

La mesure v3 ci-dessus demeure une preuve historique. La [requalification v4 des 50 points](DCE_SIX_SIGNAUX_CRITIQUES_REQUALIFICATION_2026-10-12.md) corrige les six omissions :18 signaux étayés,0 omission ciblée,19 sans règle cible,13 sources non éligibles inchangées. Aucun dossier complet ou admission Golden déclaré.
