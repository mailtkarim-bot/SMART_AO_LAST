# Essais locaux DCE — précision métier et dépendances — 11 octobre 2026

## Autorité et périmètre

Les demandes Owner autorisent les essais locaux sur les DCE fournis. Le Master métier v3.1, notamment M2-025 à M2-037 et M31-03/08, fixe les comportements attendus. L'admission Golden DCE reste distincte : droits non établis et validations humaines non réalisées; A1 non admis, A2 générique HOLD, NO-GO public.

Base Git : `30f26934430095632000a1d82519f61dbb4c6411`. Corrections isolées dans `codex/dce-analysis-trials-20261011`; WIP documentaire principal conservé. Corpus, annotations détaillées, textes, modèles et preuves individuelles restent hors Git sous `~/.local/share/smartao-proofs/`.

## AS-IS, risques, insertion et plan minimal

**AS-IS :** 29 faits pilotes confrontés à une seconde lecture technique; absence de validation humaine. Les règles existantes repèrent des mentions dans des fragments : cela ne prouve ni les douze axes métier ni l'exhaustivité d'un dossier. Dépendances présentes mais caches et configuration effective à vérifier.

**Risques :** obligation rendue facultative par une autre phrase; validité des offres omise; classement par fréquence de références; ancien texte réutilisé après une extraction devenue incomplète; page dessinée ou scannée déclarée extraite; capacité inconnue déclarée optimale.

**Insertion :** extracteurs natif/PyMuPDF, classification, analyse RC, validation des observations et service capacité existants. Aucun nouveau framework, migration, contrat financier ou acte humain.

**Plan minimal :** reproduire chaque défaut par un test rouge; corriger le composant partagé; exercer réellement les dépendances sur données synthétiques; vérifier un petit échantillon réel; tests PostgreSQL et suite backend; revue, scans et suivi. FontTools est ajouté pour le cas de fontes CFF effectivement rencontré, avec verrou exact.

## Grille des particularités à qualifier

Cette grille définit les essais suivants; elle ne constitue pas une analyse finale des dossiers. Les pièces et citations exactes sont privées. Les intitulés sont remplacés par des alias.

| Échantillon | Particularités du corpus | Contrôles métier prioritaires | Preuve obtenue / encore absente |
|---|---|---|---|
| DCE-01, rénovation, quatre lots | RC, CCAP, CCTP et réponses modificatives; enveloppe et équipements | Applicabilité par lot/version; raccordements; prescriptions énergétiques; interfaces et réception; prix, délais, trésorerie; accès et site occupé | Six pièces pilotes partagées avec DCE-02, 29 supports textuels retrouvés; portée corrigée sur six faits. Chaîne méthode→moyens→coût→délai et exhaustivité non mesurées |
| DCE-02, deux lots ITE/VMC | RC modifié, questions/réponses et plans à diffusion limitée | Validité des offres; rectificatif et invalidation; interface ITE/VMC; visite; contraintes de plans; preuve de capacité | Défaut de détection de durée de validité reproduit et corrigé; analyse des plans, moyens et conséquences économiques non qualifiée |
| DCE-03, accord-cadre multi-technique | Archives imbriquées, règles communes et pièces propres aux lots | Ne pas appliquer une clause d'un autre lot; HSE/déchets; accès; BPU et commandes; restrictions d'usage | RC sélectionné exercé par les fonctions existantes; lecture croisée des pièces communes/lot et droits de réutilisation non qualifiés |
| DCE-04, restructuration complexe | Archive vérifiée : 443 fichiers, formats PDF/DWG/DOC/XLS et archives imbriquées; 17 lots au total (12 AOO et 5 MAPA) | Inventaire et lisibilité; phasage et interfaces; plans; contraintes ERP; obligations et réception; changements; prix/cash | RC sélectionné classé; contrôle de grande image impose REVIEW_REQUIRED. Aucun résultat complet du dossier, des plans ou des tableaux n'est affirmé |

Pour **chacun** des quatre DCE, les douze axes M2-026 doivent être traités séparément : intérêt commercial, candidature, technique, constructibilité/logistique, contrat, prix/marge, trésorerie/garanties, capacité, partenaires, HSE/environnement/réglementation, obligations documentaires/engagements, droits/réception/sortie. Un axe non testé reste non testé. Une donnée entreprise absente reste UNKNOWN.

### Couverture à mesurer par axe et par dossier

Toutes les cellules ci-dessous sont des **contrôles attendus**, pas des résultats admis. Les conséquences doivent être reliées aux pièces effectivement applicables; les informations entreprise absentes restent UNKNOWN.

| Axe M2-026 | DCE-01 | DCE-02 | DCE-03 | DCE-04 |
|---|---|---|---|---|
| Intérêt commercial | Sélection des quatre lots et adéquation aux moyens | Deux lots et capacité de coordination | Périmètre d'accord-cadre et commandes | Sélection des 17 lots au total (12 AOO et 5 MAPA) et interfaces |
| Candidature | Conditions RC par lot et preuves à date | RC modifié et pièces candidature | Règles communes versus lot choisi | Candidature, groupement et pièces par lot |
| Technique | Enveloppe/équipements et prescriptions énergétiques | ITE/VMC et raccords | Pièces techniques communes et spécifiques | Plans, prescriptions et compatibilité des lots |
| Constructibilité/logistique | Accès, site occupé à confirmer, séquencement | Interfaces façade/ventilation et visite | Accès site et contraintes d'intervention | Phasage, coactivité et maintien des usages |
| Contrat | CCAP, réponses et portée lot | CCAP et rectificatifs | Hiérarchie commune/lot, bons de commande | CCAP, interfaces et responsabilités |
| Prix/marge | DPGF par lot, exclusions et prestations liées | DPGF ITE/VMC et interfaces | BPU, unités et périmètre commande | DPGF/BPU, variantes et travaux connexes |
| Trésorerie/garanties | Avance, paiement, retenue et statut entreprise | Clauses CCAP et conditions entreprise | Déclenchement commande/paiement et garanties | Phasage financier, paiement et garanties |
| Capacité | Besoins/moyens et disponibilités réelles | Coordination et équipes ITE/VMC | Capacité sur commandes simultanées | Charge multi-lots et calendrier partagé |
| Partenaires | Périmètre exact et dépendances lot | Interfaces et engagements partenaires | Lot, commande et sous-traitance | Interfaces, groupements et sous-traitants |
| HSE/environnement/réglementation | Risques site et justificatifs énergétiques | Risques chantier et insertion à vérifier | Accès/HSE/déchets selon pièces applicables | Contraintes ERP, coactivité et prescriptions |
| Obligations/engagements | Visite, mémoire, essais et preuve de réception | Validité, visite et réponses modificatives | Pièces/visite communes ou lot-spécifiques | Livrables, essais, DOE et coordinations |
| Droits/réception/sortie | Usage des pièces, réception et réserves | Plans à diffusion limitée et réception | Restrictions RC et conditions de sortie | Formats non lus, droits, réception et maintenance |

Le repérage lexical actuel est un premier maillon. Ni le calcul de marge, ni la faisabilité d'un phasage, ni une conformité réglementaire, ni l'absence de travaux connexes ne peuvent être déduits du seul nombre de mentions détectées. Pour admettre un essai complet, mesurer chaque cellule contre une référence locale avec désaccords conservés et aucune pièce critique ignorée.

Chaque point critique doit conserver source/version/hash/locator, applicabilité lot/périmètre, état connu/inconnu, conséquences, responsable, action, échéance, preuve attendue et décision humaine. La présence d'une pièce n'est pas une preuve de conformité. Le statut COMPLETED de l'analyse lexicale décrit les fragments sélectionnés, pas la complétude métier du DCE : l'inventaire des pièces non éligibles demeure une limite ouverte à rendre explicite avant toute qualification de dossier complet.

## Dépendances réellement exercées

| Composant installé/verrouillé | Exercice réel local | Limite |
|---|---|---|
| OR-Tools 9.15.6755 | CP-SAT : OPTIMAL nominal, INFEASIBLE, timeout UNKNOWN sans affectation | Ce n'est pas un analyseur de texte; intégration entreprise/calendrier complète absente |
| Docling 2.137.0 | Adaptateur réel, une page synthétique, COMPLETED, 16,492 s; modèles officiels préparés et hachés; conversion hors ligne | Pic mémoire environ 1,49 GiB; locators lignes, pas provenance page/bbox; tableaux/scans réels non qualifiés |
| PyMuPDF 1.28.2 | Adaptateur réel, une page synthétique avec page/bloc/bbox, COMPLETED | Couverture et layout complexes non démontrés par une page |
| RapidOCR 3.9.2 / ONNXRuntime 1.29.0 | Modèles installés et dictionnaire embarqué exact : texte synthétique retrouvé; REVIEW_REQUIRED | Sans chemins explicites : FAILED_SAFE/OCR_MODELS_REQUIRED; pas de validation humaine de l'OCR |
| pypdf 6.20.0 + FontTools 4.66.1 | RC à fontes CFF : 52 avertissements avant, zéro après ajout isolé | Absence d'avertissement ne prouve pas fidélité universelle du texte |

Les flags optionnels restent désactivés par défaut. Les chemins de modèles sont propres aux essais; aucun fichier `.env` global modifié. Docling n'est pas invoqué automatiquement par le chemin PDF composite PyMuPDF/OCR. BGE-M3/RAG et services distants ne sont pas qualifiés ici.

Les anciennes affirmations de présence de caches dans la décision Phase 11 du 21 septembre sont historiques : les caches globaux recherchés étaient absents le 11 octobre. Les modèles officiels nécessaires ont été préparés dans le dossier privé d'essai, avec commits immuables et SHA-256, sans transfert du corpus.

**Précision du 11/10, seconde tranche :** le RC DCE-04 page4 énumère 17 lots : 12 AOO et5 MAPA; «12 lots» désigne le seul périmètre AOO. Page12, lot14 : PSE «Lasure sur support béton», chiffrage obligatoire. Ces faits ont été revérifiés sur les originaux hachés et la page physique; ce sont des observations techniques locales, sans choix de lot ni validation humaine.

## Corrections et preuves

- Analyse RC version 3 : clause pertinente, obligation/facultatif/conditionnel distincts; délai de dépôt et durée de validité reconnus. Revalidation des versions historiques 1/2 conservée. La négation de « requis/exigé » est protégée après quatre régressions rouges; 25 tests ciblés RC verts.
- Extraction PDF et PyMuPDF version 2 : page comportant contenu graphique sans texte et grande image directe derrière un en-tête imposent REVIEW_REQUIRED; texte/locator conservés. Une petite image de logo et une vraie page blanche restent admises. Les images dans Form et les significations vectorielles restent une limite déclarée.
- Classification version 2 : titre explicite prioritaire, suffixe accepté, références ultérieures sans effet; titres adjacents contradictoires exigent une revue. Service et handlers classification/RC sélectionnent les mêmes extractions courantes : un nouveau REVIEW_REQUIRED, même au timestamp égal, interdit le recours au texte historique. Deux tests PostgreSQL rouges et un successor RC rouge, puis 25 tests PostgreSQL verts. Régression de suffixe/liste : deux tests rouges puis sept verts.
- Capacité : demandes/offres absentes (`None`) donnent UNKNOWN; ensembles explicitement vides restent connus. Snapshot et retry distinguent ces états; test PostgreSQL sans effet métier.
- Première passe ciblée sans DB après les corrections de titre : **58/58**. PostgreSQL ciblé extraction/analyse/capacité : **35/35**; classification avant dernier correctif de chargement : **9/9**. Ces chiffres ne remplacent pas la suite entière finale.

Contrôles globaux déjà exécutés : Ruff/check et format **1187 fichiers**, mypy **1031 sources**, Bandit niveau medium/high sans finding, secrets sur fichiers suivis et trois nouveaux tests sans alerte; audit export de toutes les extras verrouillé/hashed : aucune vulnérabilité connue. Semgrep **1.179.0**, `p/security-audit`, métriques désactivées : **225 règles / 16 fichiers / 0 finding / 0 erreur**, puis dernière correction RC **2 fichiers / 0 finding**; scan local, sans envoi des résultats. Ces scans ne prouvent pas absence de vulnérabilité.

**Vérification finale acquise.** Backend complet, PostgreSQL 16 jetable explicite sur tmpfs : **2265/2265**, zéro ignoré, **1182,35 s (19 min 42)**, **87,96 %** de couverture statements/branches, seuil **85,50 %** conservé; 31537 statements, 5954 branches. Deux warnings non bloquants (Starlette/httpx et alias Pydantic) conservés. Les campagnes interrompues pour intégrer les findings ne sont pas annoncées réussies.

Intégration locale dans le checkout principal `codex/reconcile-smartao-20261009` : hashes identiques sur les **18 fichiers** source/tests/config du patch testé; WIP documentaire préexistant conservé. Aucun commit/push. La suite entière a été exécutée sur le worktree isolé avant intégration; elle n'est pas rejouée inutilement sur les mêmes octets. Les tests d'autorité documentaire et de tête schema ont passé **5/5** sur le principal; contrôles finaux d'import, lint/types et whitespace après intégration. Les suites PostgreSQL exercent migrations/contraintes existantes; aucune migration nouvelle. Logs, couverture JSON, patch et manifestes privés conservés dans `~/.local/share/smartao-proofs/dce-analysis-trials-20261011/`.

## Fichiers concernés

- `backend/app/modules/dce/application/{analysis,classification,extraction,handlers}.py` : versionnement, clauses, sélection des sources et validation canonique.
- `backend/app/modules/dce/infrastructure/advanced_extraction.py` : même barrière de couverture PDF et version PyMuPDF.
- `backend/app/modules/optimization/application/{capacity_planning,run_service}.py` : absence/ensemble vide, snapshot et hash.
- `backend/tests/domain/dce/test_{rc_directive_precision,document_title_precision,pdf_content_coverage}.py` : nouvelles preuves de régression.
- Tests application `test_advanced_extraction.py`, `test_capacity_planning.py`, `test_capacity_run_service.py`, `test_dce_document_classification.py`, `test_dce_rc_analysis.py`; test DB `test_capacity_run_persistence.py`.
- `pyproject.toml`, `uv.lock` : seul FontTools ajouté; versions préexistantes conservées.
- Index actif, plan global, référentiel dépendances et présent dossier : preuves, limites, couverture attendue et reprise; cahiers produit/métier intégraux conservés.

## Invariants et limites

Conservation des historiques, versions, hashes, locators, tenant et retries; aucune promotion UNKNOWN/OCR en certitude métier. Aucun P3, acte Patron, export métier, backend live, VPS, déploiement, push ou GO public. Les probes réels utilisent les fonctions de production en lecture locale, sans import dans une base métier. Les analyses diagnostiques de fragments REVIEW_REQUIRED ne sont pas éligibles à la persistance comme extraction complète.

Méthode appliquée : Graphify, Superpowers systematic-debugging/TDD/requesting-code-review/verification-before-completion, ECC python-testing/verification-loop/security-review; PDF pour les sources. OpenDesign/Impeccable inapplicables sans modification UI; Jev/Manus non requis pour les régressions déterministes.
