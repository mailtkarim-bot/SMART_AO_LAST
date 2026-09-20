# SMART AO — QUAL-01 — Golden DCE, bancs, métriques et gouvernance

**Date :** 12 septembre 2026  
**Référence :** `feat/ccap-cctp-risk-register-20260831@b6b05b8`  
**Statut :** BASELINE AUDITÉE — CORPUS EXÉCUTABLE ABSENT  
**Verdict :** squelette technique valide, zéro Golden DCE ; Gate de non-régression impossible aujourd'hui

## 1. État réel du harnais

Le dépôt contient `ops/golden-corpus/README.md`, un `manifest.example.json`, un validateur et des tests. Le validateur réussit et annonce :

```text
valid corpus=smart-ao-anonymized-dce-v1 documents=0
```

Il vérifie notamment la forme du manifeste, les noms de fichiers sûrs, SHA-256, MIME, fragments et labels. Le manifeste n'enregistre toutefois aucun document. Le validateur ne démontre ni présence des fichiers, ni conformité des hashes aux octets, ni extraction, ni évaluation métier bout-en-bout. Les MIME du schéma courant sont limités à PDF, DOCX et XLSX.

Les 17 tests ciblés `test_golden_corpus.py` et `test_knowledge_benchmark.py` passent. Ils qualifient le code du harnais, pas la qualité de SMART AO sur de vrais DCE.

## 2. Corpus DCE externe observé

Chemin inventorié, sans copie ni ingestion :

```text
/home/noor/PROJECTS/BTP/DOCUMENTATION/SMART_AO DOCUMENTATION/DCE Type
```

| Mesure | Valeur |
|---|---:|
| Fichiers | 379 |
| Volume | 726 829 972 octets, environ 693 MiB |
| Profondeur maximale | 5 niveaux |
| Groupes de consultation de premier niveau | 6 |
| PDF | 165 |
| XLS | 152 |
| XLSX | 32 |
| DOC | 13 |
| DB | 9 |
| DOCX | 4 |
| ODT | 2 |
| ZIP | 1 |
| 7Z | 1, dont une archive de 423 004 980 octets, environ 403 MiB |

Cette diversité prouve que le sous-ensemble PDF/DOCX/XLSX ne suffit pas à annoncer une couverture des DCE réels. Elle ne donne pas le droit d'utiliser ces fichiers dans un corpus de test partagé. Les droits, données personnelles, secrets d'affaires et exigences d'anonymisation restent à établir dossier par dossier.

## 3. Décision de gouvernance

Le Golden DCE est un actif produit gouverné, pas un répertoire de fixtures. Chaque cas possède :

- origine, titulaire des droits et autorisation d'usage ;
- niveau de confidentialité et emplacement autorisé ;
- empreinte des octets ;
- famille métier, cadre public/privé, lots, formats et difficulté ;
- version du schéma d'annotation ;
- annotations et identité/rôle des validateurs ;
- désaccords conservés ;
- date de gel et historique de modification ;
- versions parser, règles, modèle, prompt et tool ;
- métriques ventilées et diff de régression.

Les DCE réels restent hors Git. Git conserve le manifeste non sensible, le schéma, le runner, les métriques agrégées et les identifiants opaques. Les chemins absolus locaux ne deviennent jamais un contrat CI.

## 4. Trois bancs séparés

| Banc | But | Contenu | Accès | Usage |
|---|---|---|---|---|
| Development | développer et diagnostiquer | 5 à 8 DCE diversifiés, extraits minimaux autorisés | équipe produit habilitée | itération fréquente |
| Qualification | mesurer sans contamination | cas gelés jamais utilisés pour régler les règles/prompts | cercle restreint, résultats agrégés | décision de release/gate |
| Hostile | éprouver limites et sécurité | archives imbriquées, gros fichiers, formats anciens/protégés, prompt injection, corruption | sécurité/qualité | fail-closed et abstention |

Les valeurs 5 à 8 décrivent un démarrage praticable du banc Development, pas la taille finale. Le cahier métier impose à terme six familles : simple par lot, multi-lots, accord-cadre multi-sites, réhabilitation en site occupé, infrastructure, nombreux rectificatifs, plus un corpus privé dédié et un dossier hostile.

## 5. Strates d'annotation

| Strate | Unité | Champs minimaux | Validateur |
|---|---|---|---|
| inventaire | fichier/membre archive | chemin logique, taille, format, lisibilité, rôle supposé | documentaliste/études |
| extraction | page/paragraphe/cellule | anchor attendu, texte/valeur, statut | annotateur + contrôle format |
| exigence | obligation atomique | texte, portée, phase, criticité, source | expert métier |
| contradiction | paire/groupe de claims | sources opposées, résolution ou inconnu | responsable offre |
| MIRP/prix | besoin d'information | poste, niveau, donnée présente/manquante | métreur du lot |
| candidature | preuve requise | titulaire, validité, applicabilité | administratif/QSE |
| engagement | promesse | formulation, coût, responsable, phase | études + travaux |
| remise | artefact/canal | exigé, présent, hash, étape externe, reçu | responsable offre/signataire |
| sécurité | passage hostile | type d'attaque, comportement interdit, résultat attendu | sécurité |

Le schéma doit permettre `UNKNOWN`, `NOT_APPLICABLE` et désaccord. Forcer un label majoritaire sur un cas réellement ambigu produirait une fausse vérité de référence.

## 6. Rôles et arbitrage

| Rôle | Responsabilité |
|---|---|
| Corpus Owner | droits, classification, admission/retrait des cas |
| Quality Owner | schéma, runner, gel, versions et rapport de gate |
| Expert métier 1 | annotation primaire dans son corps d'état |
| Expert métier 2 | annotation indépendante des cas critiques |
| Adjudicator | tranche un désaccord ou le conserve comme ambiguïté |
| Security/DPO | données personnelles, secrets, hostile et règles de conservation |
| Release Owner | accepte ou refuse une régression documentée |

Une même personne peut cumuler des rôles dans la PME de démarrage, mais les actes et leurs dates restent distincts.

## 7. Métriques obligatoires

| Mesure | Définition | Ventilation | Gate critique |
|---|---|---|---|
| inventory recall | éléments inventoriés / éléments attendus | archive, format, taille | **100 %** du jeu Gate A |
| readable coverage | éléments interprétés / inventoriés | format/métier | aucun non-lu silencieux |
| C1 requirement recall | C1 retrouvées / C1 annotées | type/lot/format | **100 %** sur jeu accepté |
| anchor validity | anchors ouvrant l'emplacement attendu | format/parser | **100 %** C1/chiffres/engagements |
| precision | sorties correctes / sorties produites | criticité/type | seuil étalonné A1 |
| contradiction recall | contradictions critiques détectées | document/type | zéro omission critique acceptée |
| stale-valid count | conclusions encore valides après source remplacée | objet | **0** critique |
| silent failure count | fichier/étape échouée présentée comme réussie | pipeline | **0** |
| unauthorized disclosure | donnée révélée à un rôle interdit | rôle/canal | **0** |
| abstention correctness | cas insuffisants rendus `non établi` | classe IA/règle | seuil étalonné, zéro invention engageante |
| regression delta | différence à la baseline gelée | version parser/modèle/règle | diff explicite, décision nommée |
| latency/resource | durée, mémoire, CPU par dossier/fichier | taille/format | enveloppe NFR à fixer |

Une moyenne globale ne peut pas masquer un échec C1. Les intervalles et seuils de précision seront fixés après observation du corpus ; Phase 0 ne les invente pas.

## 8. Manifeste v2 minimal proposé

Le manifeste doit référencer, sans contenir les documents :

```text
corpus_id, corpus_version, bank, case_id
rights_record_id, anonymization_status, sensitivity
object_id, sha256, bytes, mime, logical_path
document_family, trade, procurement_framework, difficulty_tags
annotation_schema_version, annotation_object_id, annotator_roles
expected_inventory, expected_failures, criticality
parser/rule/model/prompt/tool versions
```

Le validateur v2 vérifiera aussi : unicité des identifiants, séparation des bancs, hash d'un objet accessible via adapter de stockage, absence de chemin absolu, présence d'une décision de droits, schéma d'annotation et impossibilité pour la CI standard de lire Qualification.

## 9. Sélection initiale à partir des 379 fichiers

PR-A1 ne doit pas importer tout le corpus. La sélection commence par les six groupes et choisit les plus petits ensembles couvrant :

1. PDF texte natif et PDF graphique/scanné ;
2. DOCX et XLSX modernes ;
3. XLS/DOC anciens comme cas `UNSUPPORTED` attendu tant qu'aucun parser sûr n'existe ;
4. archive et sous-arborescence ;
5. multi-lots et rectificatif ;
6. au moins trois familles métier, dont gros œuvre, électricité et CVC si les droits le permettent ;
7. un cas privé seulement après VAL-02/droits ;
8. un cas Hostile synthétique pour injection documentaire, bombe d'archive contrôlée et corruption.

La sélection doit être enregistrée dans un ledger, avec motif d'inclusion et lacunes restantes.

## 10. Gates A1 et A

### Sortie PR-A1

- droits prouvés pour chaque cas Development ;
- stockage hors Git reproductible ;
- manifeste et objets réconciliés par hash ;
- schéma d'annotation versionné ;
- runner exécutable depuis une commande documentée ;
- premiers cas C1 doublement annotés ;
- rapport baseline généré ;
- Development, Qualification et Hostile techniquement séparés.

### Sortie Gate A

- 100 % des fichiers/membres du jeu Gate A inventoriés ;
- zéro échec silencieux ;
- C1 sourcées par anchors valides ;
- changement de source visible et invalidation critique démontrée ;
- résultat par format, métier, type et criticité ;
- rollback A2–A4 testé sur base représentative.

## 11. Réponse Gate 0

**Question 5 — l'environnement et le Golden DCE permettent-ils de mesurer les régressions ? `NON`.** Action bornée : autoriser A0, puis A1. A2 ne démarre qu'après sortie A1 vérifiable.

## 12. Preuves

- `ops/golden-corpus/README.md`
- `ops/golden-corpus/manifest.example.json`
- `backend/tests/application/test_golden_corpus.py`
- `backend/tests/application/test_knowledge_benchmark.py`
- [AUD-04](./SMART_AO_PHASE0_AUD-04_TESTS_ENVIRONNEMENT.md)
- [PLAN-A](./SMART_AO_PHASE0_PLAN-A_PR-A0_A4.md)
