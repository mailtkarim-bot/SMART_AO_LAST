# SMART_AO V8 — Référentiel des dépendances techniques, logicielles et externes
## WORK PROPOSAL v0.2 — inventaire V8 vérifié + cible candidate non gelée

**Statut :** `WORK_PROPOSAL` — référentiel technique de faisabilité et d’inventaire ; **ne constitue pas encore un Architecture Freeze**  
**Date de cadrage initial :** 17 septembre 2026  
**Date de contre-révision :** 17 septembre 2026  
**Périmètre :** SMART_AO V8 — application BTP d’analyse DCE, décision Go/No-Go, préparation, chiffrage, sécurisation et dépôt  
**Emplacement de travail actuel :** `docs/00_REFERENCE_ACTIVE/DEPENDENCIES_WORKING/SMART_AO_V8_DEPENDANCES_ARCHITECTURE_WORK_PROPOSAL.md`

**Autorités amont :** le Cahier directeur Produit & Métier, le Catalogue UX consolidé, les Fondations UX actives et les futurs contrats d’expériences priment sur le présent document pour toute décision visible, métier, d’autorité, de confidentialité ou de parcours. Le présent référentiel décrit l’existant V8, les contraintes techniques connues et les options candidates ; il ne doit pas transformer une hypothèse technique en décision produit irréversible.

---

## 1. Objet du document

Ce document définit l’inventaire, le rôle, la criticité, le mode d’exécution, les risques et les règles de gouvernance de toutes les dépendances nécessaires à SMART_AO V8.

Il couvre quatre familles distinctes :

1. **dépendances internes** : modules métier, couches applicatives, workers, ports/adaptateurs et dépendances entre composants SMART_AO ;
2. **dépendances logicielles locales** : Python, bibliothèques Python, Node.js, React, PostgreSQL, Docker, Caddy, Nginx, ClamAV, outils de parsing, OCR, RAG, embeddings, etc. ;
3. **dépendances externes réseau** : LLM distant, API INSEE Sirene, BOAMP, SMTP, webhooks, éventuels services de signature, stockage S3 distant, etc. ;
4. **dépendances de développement et d’exploitation** : Git, GitHub, CI/CD, tests, scanners sécurité, sauvegarde, restauration, observabilité et maintenance.

Ce document ne doit pas être compris comme « la liste de tout ce qu’il serait possible d’installer ». Son objectif est au contraire de réduire la surface technique de SMART_AO : toute dépendance doit avoir une mission explicite, un propriétaire, un mode de défaillance connu et, lorsque cela est possible, une solution de remplacement.

### 1.1 Place du document dans la gouvernance actuelle

La séquence de décision est désormais :

```text
Expérience métier
   ↓
Parcours et contenu candidat
   ↓
Prototype / revue propriétaire
   ↓
OWNER EXPERIENCE FREEZE
   ↓
Cahier technique d’exécution
   ↓
Benchmarks + ADR
   ↓
Référentiel des dépendances consolidé
   ↓
ARCHITECTURE FREEZE
   ↓
Plan d’exécution Codex
```

Le présent document accompagne cette conception et permet de détecter tôt les contraintes de faisabilité, de sécurité, de coût et d’exploitation. Il **n’autorise pas** à démarrer une migration technique ou un remplacement de stack avant les gates correspondants.

---

## 2. Règle fondamentale : distinguer l’existant de la cible

SMART_AO ne doit jamais confondre :

- ce qui est **déjà présent et vérifié dans le dépôt V8** ;
- ce qui est **prévu par le code mais désactivé** ;
- ce qui est **recommandé pour la production cible** ;
- ce qui est **encore une décision d’architecture** ;
- ce qui est **futur / optionnel**.

Légende utilisée dans tout le document :

| Code | Signification |
|---|---|
| **V** | Vérifié dans le dépôt SMART_AO_V8 actuel |
| **VD** | Vérifié mais désactivé par défaut / activable par configuration |
| **T** | Cible recommandée **candidate** pour la production ; non gelée tant qu’un ADR/gate ne la promeut pas |
| **D** | Décision d’architecture encore à prendre / benchmark ou ADR requis |
| **F** | Futur / optionnel, à ne pas installer sans besoin démontré |

### 2.1 Lecture à deux axes obligatoire

Pour éviter de confondre « existe dans V8 » et « sera conservé dans la cible », chaque composant important doit être lu selon deux axes :

- **preuve AS-IS** : `V` / `VD` / non vérifié ;
- **décision TO-BE** : `FROZEN`, `CANDIDATE`, `BENCHMARK`, `FUTURE` ou `REJECTED`.

Exemples :

```text
FastAPI        AS-IS : V     TO-BE : CANDIDATE
PostgreSQL     AS-IS : V     TO-BE : CANDIDATE_FORT / ADR
BGE-M3         AS-IS : VD    TO-BE : BENCHMARK
Rust backend   AS-IS : absent TO-BE : option à comparer, aucune migration engagée
```

La présence d’un composant dans V8 ne lui donne donc aucune autorité automatique sur l’architecture finale.

Criticité :

| Niveau | Signification |
|---|---|
| **C0** | SMART_AO ne démarre pas ou ne peut pas assurer son socle sans cette dépendance |
| **C1** | indispensable à une fonction métier centrale ou de sécurité |
| **C2** | fonctionnalité importante mais dégradable / désactivable |
| **C3** | développement, confort, expérimentation ou extension future |

---

## 3. Architecture de travail candidate — non gelée

```text
                         UTILISATEUR ENTREPRISE
                                  │
                                  ▼
                            HTTPS / TLS
                                  │
                                  ▼
                              CADDY
                                  │
                       ┌──────────┴──────────┐
                       ▼                     ▼
             Frontend Web (V8 : React)   Backend principal
             Serveur statique (V8 : Nginx) (V8 : FastAPI/Python)
                                             │
                                             │
                           ┌─────────────────┼──────────────────┐
                           │                 │                  │
                           ▼                 ▼                  ▼
                      PostgreSQL      Workers métier      Quarantaine DCE
                           │                 │                  │
                           │                 │                  ▼
                           │                 │               ClamAV
                           │                 │
                           │         ┌───────┼─────────────┐
                           │         ▼       ▼             ▼
                           │      Parsing   OCR       RAG / Embeddings
                           │      docs      CPU           CPU
                           │         │       │             │
                           └─────────┴───────┴──────┬──────┘
                                                   │
                                                   ▼
                                           Evidence structurée
                                                   │
                                      ┌────────────┴────────────┐
                                      ▼                         ▼
                                Moteur de règles           LLM externe
                                SMART_AO                   via API
                                      │                         │
                                      └────────────┬────────────┘
                                                   ▼
                                        Résultat vérifiable
                                        + sources + alertes
```

Principe : **le LLM ne doit pas être SMART_AO**. Il doit être un moteur externe remplaçable appelé par une couche d’adaptation. Les données, règles métier, décisions, preuves, résultats structurés, droits et états restent sous contrôle de SMART_AO.

### 3.1 Invariants DEC-11 à respecter quelle que soit la stack

La cible technique devra respecter simultanément :

- **un environnement dédié par entreprise cliente** au lancement ;
- **une application tenant-aware** : organisation, rôles, droits, périmètres et délégations restent explicites dans le logiciel ;
- **un code produit unique** et une chaîne de version unique, sans forks permanents par client ;
- provisioning, mise à jour, sauvegarde, restauration et suppression reproductibles ;
- coûts infrastructure et IA attribuables par client ;
- résidence cible France/EEE avec cartographie des services externes ;
- réversibilité prévue dès la conception ;
- aucune confiance implicite accordée au seul fait d’être sur un VPS dédié.

Le `tenant_id` / `organization_id` doit donc être propagé ou dérivé de façon contrôlée dans les données, jobs, index, logs, exports, stockage objet, retrieval et appels IA.

---

# PARTIE I — DÉPENDANCES INTERNES SMART_AO

## 4. Modules métier actuellement présents

Le dépôt contient notamment les modules :

- `case`
- `dce`
- `decision`
- `enterprise`
- `knowledge`
- `market_watch`
- `membership`
- `opportunity`
- `optimization`
- `patron_action`
- `preparation`
- `pricing`
- `submission`

Ces modules sont des dépendances **internes**, mais ils ne doivent pas devenir un graphe d’imports arbitraire.

### Règle de dépendance interne

```text
Domain métier
   ↑ ne dépend de rien d’infrastructure
Application / handlers
   ↓ dépend du domaine + ports
Adapters / platform
   ↓ implémentent les ports
FastAPI / SQLAlchemy / stockage / LLM / SMTP / HTTP
```

Le domaine doit rester pur : pas d’import FastAPI, SQLAlchemy, boto3, SDK LLM, HTTP, SMTP, filesystem ou Docker dans le domaine métier.

### Communication entre modules

Les dépendances inter-modules doivent privilégier :

- événements métier ;
- outbox transactionnelle ;
- commandes idempotentes ;
- process managers ;
- projections ;
- contrats explicites.

À éviter :

- accès direct aux tables d’un autre agrégat ;
- import de repositories privés d’un autre module ;
- mutation de plusieurs agrégats propriétaires dans une même transaction sans contrat explicite ;
- dépendance d’un module métier envers une bibliothèque d’IA.

**Criticité : C0.** Cette discipline réduit le couplage et rend remplaçables les dépendances externes.

---

## 5. Ports d’abstraction à considérer comme obligatoires

Les services externes structurants doivent être cachés derrière des interfaces SMART_AO. Les ports suivants sont recommandés :

| Port interne | Mission | Raison |
|---|---|---|
| `LLMProvider` | génération / raisonnement / extraction structurée complexe | éviter le verrouillage OpenAI ou autre fournisseur |
| `EmbeddingProvider` | calcul des embeddings | permettre modèle local, API ou remplacement du modèle |
| `Reranker` | reclassement de candidats RAG | benchmark et remplacement indépendants |
| `ObjectStorage` | stockage objets S3/MinIO | ne pas coupler le domaine à boto3 |
| `MalwareScanner` | analyse antivirus | ClamAV remplaçable |
| `DocumentExtractor` | PDF/DOCX/XLSX → représentation normalisée | séparer parsing métier et librairie |
| `OCRProvider` | image/scans → texte | RapidOCR/ONNX remplaçable |
| `PublicNoticeProvider` | BOAMP et futures sources | isolation des schémas externes |
| `CompanyRegistryProvider` | Sirene / enrichissement entreprise | isolation INSEE |
| `NotificationProvider` | SMTP / autre canal | éviter couplage au transport |
| `SignatureProvider` | callbacks de signature éventuels | fournisseur non fixé |
| `Clock` / `IdGenerator` | déterminisme des tests | fiabilité des invariants |

Tous les ports ne doivent pas nécessairement devenir des classes abstraites complexes. Le principe est : **un fournisseur externe ne doit jamais devenir une hypothèse irréversible du métier**.

---

# PARTIE II — SOCLE SYSTÈME ET CONTENEURISATION

## 6. Linux / VPS

**Statut : T — C0**

Production envisagée : VPS Linux hébergé en France, un VPS dédié par entreprise cliente.

Le VPS n’a pas besoin de GPU si :

- le LLM génératif principal est externe ;
- les embeddings et petits modèles sont dimensionnés pour CPU ;
- l’OCR est asynchrone et limité en concurrence ;
- les traitements lourds passent par des workers plutôt que par le thread HTTP utilisateur.

### Cible de départ recommandée par entreprise

```text
CPU      : ~8 vCPU à benchmarker
RAM      : 24 Go
Stockage : NVMe/SSD, capacité selon volume DCE + sauvegardes
GPU      : non requis au lancement
Réseau   : sortie HTTPS contrôlée vers services autorisés
```

24 Go n’est pas un engagement de capacité définitif. La validation doit se faire par benchmark avec corpus DCE réel, en particulier pour BGE-M3, Docling et OCR.

---

## 7. Docker Engine et Docker Compose

**Statut : V — C0**

Le dépôt utilise déjà Docker/Compose pour isoler :

- Caddy ;
- frontend ;
- backend ;
- migrations ;
- workers ;
- PostgreSQL ;
- ClamAV.

Le déploiement préproduction utilise des réseaux séparés `edge` et `internal`, ce dernier étant marqué `internal: true`.

### Politique cible

- images de base pinnées par digest SHA256 ;
- `no-new-privileges` ;
- services non exposés sur l’hôte sauf nécessité ;
- backend et frontend exécutés en utilisateur non-root lorsque possible ;
- secrets jamais intégrés dans les images ;
- volumes nommés et sauvegarde explicite ;
- healthchecks obligatoires pour les composants critiques.

Le dépôt applique déjà plusieurs de ces principes.

---

# PARTIE III — RUNTIME BACKEND V8 — PYTHON (BASELINE AS-IS)

## 8. Python

**AS-IS : V — C0. TO-BE : CANDIDATE, non gelé.**

Version déclarée :

```text
Python >= 3.12 et < 3.13
```

L’image backend actuelle est basée sur `python:3.12-slim` et est pinnée par digest.

### 8.1 Règle d’architecture

Python/FastAPI est la **baseline vérifiée de V8**, pas encore une décision irréversible du futur SMART_AO. Le choix du backend final doit faire l’objet d’un ADR après stabilisation des expériences et des exigences non fonctionnelles. Les options à comparer peuvent inclure :

- conservation de Python/FastAPI ;
- migration ciblée de certains composants ;
- backend différent, dont Rust si un gain mesuré de sûreté, performance, coût ou maintenabilité le justifie ;
- architecture hybride.

Aucune réécriture ou migration de langage n’est autorisée par ce document seul.

### Gestion des dépendances Python

**Statut : V — C0**

- `pyproject.toml` = déclaration ;
- `uv.lock` = résolution reproductible ;
- `uv sync --frozen` = installation déterministe ;
- `uv` est utilisé dans l’image de build.

Politique : toute nouvelle dépendance Python doit entrer par `pyproject.toml`, être verrouillée dans `uv.lock`, justifiée, testée et auditée.

---

## 9. Dépendances Python cœur actuellement déclarées

| Dépendance | Plage actuelle | Rôle | Criticité |
|---|---:|---|---|
| FastAPI | `>=0.115,<1.0` | API HTTP | C0 |
| Pydantic | `>=2.10,<3.0` | contrats, validation | C0 |
| pydantic-settings | `>=2.6,<3.0` | configuration | C0 |
| SQLAlchemy | `>=2.0,<3.0` | persistence / ORM infrastructure | C0 |
| Alembic | `>=1.14,<2.0` | migrations DB | C0 |
| psycopg[binary] | `>=3.2,<4.0` | driver PostgreSQL | C0 |
| Uvicorn | `>=0.34,<1.0` | serveur ASGI | C0 |
| argon2-cffi | `>=23.1,<26.0` | hash de mots de passe | C1 sécurité |
| PyJWT | `>=2.10,<3.0` | tokens JWT | C1 sécurité |
| python-magic | `>=0.4.27,<1.0` | détection MIME | C1 upload sécurisé |
| pypdf | `>=6.16.0` | extraction PDF de base | C1 DCE |
| python-docx | `>=1.2.0` | documents Word | C1 DCE |
| openpyxl | `>=3.1.5` | Excel | C1 DCE/chiffrage |
| python-multipart | `>=0.0.20,<1.0` | upload multipart HTTP | C1 |
| OR-Tools | `>=9.14,<10.0` | optimisation / contraintes | C2 selon parcours |
| cryptography | `>=50,<51` | chiffrement / primitives sécurité | C1 |

### Dépendance système Python associée

`python-magic` s’appuie sur **libmagic**. L’image Docker installe déjà `libmagic1`.

---

# PARTIE IV — TRAITEMENT DOCUMENTAIRE DCE

## 10. Extraction de base

**Statut : V — C1**

Formats actuellement couverts au niveau des dépendances :

```text
PDF   → pypdf
DOCX  → python-docx
XLSX  → openpyxl
MIME  → python-magic/libmagic
```

Cette couche doit fournir une représentation normalisée : pages, paragraphes, tableaux, cellules, métadonnées, origine exacte et offsets/source nécessaires à la citation.

---

## 11. Extraction avancée

**Statut : VD — C2**

Extras Python existants :

- `docling>=2.70,<3.0`
- `pymupdf>=1.24,<2.0`

Activation prévue par :

```text
SMART_AO_INSTALL_DOCUMENT_ADVANCED
SMART_AO_ADVANCED_EXTRACTION_ENABLED
```

### Rôle

À utiliser quand l’extraction simple ne suffit pas :

- PDF complexes ;
- structure de page ;
- tableaux ;
- documents techniques à mise en page riche ;
- extraction plus robuste des blocs.

### Règle

Ne pas faire passer tous les documents par l’extracteur lourd. Pipeline recommandé :

```text
extraction simple
      │
      ├── qualité suffisante → continuer
      │
      └── qualité insuffisante → extraction avancée
```

Cela réduit CPU, RAM et latence.

---

## 12. OCR

**Statut : VD — C2**

Extras existants :

- RapidOCR ;
- ONNX Runtime.

Le compose préproduction prévoit les chemins de modèles ONNX : détection, classification, reconnaissance et dictionnaire de caractères.

### Pipeline cible

```text
PDF / page
   ↓
Détection : texte natif exploitable ?
   ├── oui → pas d’OCR
   └── non → rendu image → OCR CPU
```

**GPU non obligatoire.** ONNX Runtime peut fonctionner sur CPU. La concurrence doit toutefois être bornée afin de protéger les 24 Go du VPS.

### Risques

- pages à très haute résolution ;
- plans et scans bruités ;
- documents énormes ;
- consommation RAM/CPU ;
- OCR faux sur unités, montants, références et clauses contractuelles.

Les valeurs critiques détectées par OCR doivent être accompagnées de provenance et, selon le risque, d’une vérification humaine ou d’un contrôle croisé.

## 12.1 Archives, formats legacy et documents protégés

**Statut : T/D — C1**

Le corpus DCE réel impose de traiter explicitement, au-delà de PDF/DOCX/XLSX :

- DOC et XLS historiques ;
- ODT et formats bureautiques moins fréquents ;
- ZIP et 7z ;
- archives imbriquées ;
- documents protégés ou chiffrés ;
- fichiers avec macros ;
- liens externes ;
- cellules/formules/feuilles masquées ;
- documents sans couche texte ;
- plans lourds ;
- fichiers malformés ou hostiles.

Un port `ArchiveInspector` / `SafeArchiveExtractor` est recommandé. Le moteur exact reste une décision d’architecture.

### Contrat minimal

- taille maximale ;
- nombre maximal de fichiers ;
- profondeur maximale d’archive ;
- protection zip-bomb ;
- protection path traversal / symlink traversal ;
- préservation de l’original ;
- aucun contournement de mot de passe ;
- classification explicite `supporté / partiel / externe / refusé` ;
- aucune conversion silencieuse destructrice ;
- inspection des macros, liens externes, formules et éléments masqués lorsque le risque métier le justifie.

Les anciens DOC/XLS doivent pouvoir être conservés comme originaux même si leur édition fidèle n’est pas qualifiée.

---

# PARTIE V — SÉCURITÉ DES DOCUMENTS

## 13. ClamAV

**Statut : V — C1 sécurité**

Le dépôt exécute déjà `clamav/clamav:1.4_base` pinné par digest.

Mission : scanner les DCE entrants avant qu’ils ne deviennent des documents de confiance.

Architecture :

```text
upload
  ↓
quarantaine privée
  ↓
validation taille / MIME
  ↓
ClamAV
  ├── rejet / isolation
  └── accepté → pipeline documentaire
```

La base de signatures doit pouvoir se mettre à jour via une sortie réseau maîtrisée.

---

## 14. Quarantaine DCE

**Statut : V — C1**

Le dépôt prévoit :

```text
/var/lib/smart_ao/dce-quarantine
```

avec taille maximale configurable et worker de rétention.

La quarantaine n’est pas un stockage documentaire final. Elle doit rester privée, avec rétention et purge déterministes.

---

# PARTIE VI — BASE DE DONNÉES ET PERSISTENCE

## 15. PostgreSQL

**Statut : V — C0**

Version de service actuelle : PostgreSQL 16 Alpine, image pinnée par digest.

PostgreSQL porte :

- données métier ;
- agrégats persistés ;
- états ;
- outbox ;
- idempotence ;
- projections selon les modules ;
- données d’authentification ;
- traces structurées nécessaires au métier.

### Dépendances associées

- SQLAlchemy ;
- psycopg ;
- Alembic.

### Politique

PostgreSQL est la source de vérité transactionnelle. Un moteur vectoriel, un cache ou un LLM ne doit jamais remplacer cette source de vérité.

---

## 16. pgvector : recommandation, pas dépendance actuelle vérifiée

**Statut : D/T — C2**

Le dépôt actuel déclare le modèle d’embedding et les extras RAG, mais **ne déclare pas pgvector comme dépendance actuelle du service PostgreSQL**.

Pour une première architecture RAG, l’option `PostgreSQL + pgvector` mérite d’être privilégiée si les benchmarks sont suffisants, car elle évite d’introduire immédiatement Qdrant, Weaviate, Milvus ou un autre service supplémentaire.

Décision à prendre par benchmark :

```text
Option A : PostgreSQL + pgvector
           + moins d’infrastructure
           + sauvegarde simplifiée

Option B : vector DB dédié
           + fonctions vectorielles avancées / scale
           - service, sauvegarde, sécurité, supervision en plus
```

Ne pas installer un vector DB dédié avant qu’un besoin mesuré ne le justifie.

---

## 17. Redis : non requis actuellement

**Statut : F — C3**

Redis ne figure pas dans le compose actuel et ne doit pas être ajouté par réflexe.

Les workers existants utilisent PostgreSQL/outbox/leases. Tant que cela respecte les objectifs de débit et de latence, cette approche réduit les dépendances opérationnelles.

Redis ne devient justifié que si un besoin explicite apparaît :

- cache avec mesure de hit-rate ;
- file de travaux à haut débit ;
- rate limiting distribué ;
- verrou distribué nécessaire ;
- sessions éphémères nécessitant un store spécialisé.

---

# PARTIE VII — STOCKAGE OBJETS

## 18. API S3 / MinIO

**Statut : VD/T — C2**

Le dépôt contient déjà l’extra `object-storage` basé sur `boto3` et des réglages :

- endpoint S3 ;
- bucket ;
- région ;
- chiffrement SSE `AES256`.

Mais le compose préproduction actuel **ne lance pas un service MinIO**.

Il faut donc décider le mode de production :

### Option recommandée pour l’isolation VPS

```text
MinIO privé dans le VPS
        ou
service S3 compatible hébergé en France/UE
```

Le choix doit être fait selon :

- criticité des documents ;
- politique de sauvegarde ;
- résidence des données ;
- coût ;
- charge opérationnelle ;
- RPO/RTO ;
- capacité à restaurer indépendamment.

Tous les accès doivent passer par le port `ObjectStorage`, jamais par boto3 dans le domaine métier.

---

# PARTIE VIII — RAG, EMBEDDINGS ET RETRIEVAL

## 19. Sentence Transformers

**Statut : VD — C1/C2 selon activation RAG**

L’extra `rag` déclare :

```text
sentence-transformers >=3.0,<6.0
```

Le dépôt configure actuellement par défaut le modèle :

```text
BAAI/bge-m3
```

avec fichiers locaux uniquement en préproduction (`SMART_AO_BGE_LOCAL_FILES_ONLY=1`).

C’est une bonne propriété de production : le conteneur ne doit pas télécharger silencieusement un modèle nouveau au démarrage.

---

## 20. Modèle d’embedding BGE-M3

**Statut : VD/D — C1 si RAG activé**

Rôle : transformer les segments de DCE en représentations permettant la recherche sémantique.

### Exécution cible

CPU sur VPS au lancement.

Un GPU n’est pas obligatoire. En revanche, il faut mesurer :

- RAM au chargement ;
- RAM par batch ;
- documents/heure ;
- latence d’indexation ;
- qualité sur français BTP ;
- qualité sur termes juridiques, techniques, acronymes, montants et références.

Le modèle ne doit être retenu définitivement qu’après benchmark sur un corpus français BTP.

---

## 21. Chunking / indexation

**Statut : T — C1**

Le chunking est une dépendance algorithmique interne, pas seulement une librairie.

SMART_AO doit conserver avec chaque chunk :

- document source ;
- version DCE ;
- page ;
- section/article ;
- type documentaire ;
- offsets ;
- hash ;
- tenant ;
- droits ;
- méthode/version d’extraction ;
- version du modèle d’embedding.

Un changement d’embedding ou de stratégie de segmentation implique un plan de réindexation versionné.

---

## 22. Retrieval hybride

**Statut : T — C1**

Ne pas dépendre uniquement de la similarité vectorielle.

Pour les DCE, il faut combiner :

```text
recherche lexicale / exacte
+ filtres métier
+ recherche vectorielle
+ règles documentaires
+ reranking
```

Pourquoi : les clauses importantes contiennent souvent des références exactes, articles, montants, dates, marques, numéros de lot, pénalités et termes contractuels qui peuvent être mieux servis par une recherche lexicale ou structurée.

### 22.1 Confidentialité du retrieval

Le retrieval doit garantir qu’un contenu interdit ne contribue jamais à une réponse, un extrait, un compteur, un score, un reranking ou un contexte LLM. La règle de conception est :

```text
tenant + droits + périmètre
        ↓
candidats autorisés
        ↓
retrieval / recherche
        ↓
reranking
        ↓
LLM
```

ou un mécanisme techniquement équivalent prouvé par tests.

Les droits doivent suivre les chunks, les index, les projections et les caches éventuels. Une IA ne bénéficie d’aucune exception aux permissions utilisateur.

---

## 23. Reranker

**Statut : D/T — C2**

Un reranker CPU peut améliorer le classement après une première récupération :

```text
20 000 chunks
     ↓ retrieval initial
50 candidats
     ↓ reranker
10–20 passages
     ↓ LLM
```

Le modèle précis n’est pas arrêté. Il doit être choisi sur benchmark métier.

Un reranker ne doit pas devenir une dépendance obligatoire si son gain de qualité ne compense pas le coût CPU/RAM.

---

# PARTIE IX — LLM EXTERNE

## 24. Principe d’architecture LLM

**Statut : T — C1 pour l’IA complexe**

Le dépôt actuel ne doit pas être considéré comme lié définitivement à un fournisseur LLM. Le LLM cible doit être intégré derrière un port `LLMProvider`.

SMART_AO doit pouvoir remplacer :

```text
OpenAI
   ↕
autre fournisseur compatible
   ↕
serveur GPU privé futur
```

sans réécrire le domaine.

---

## 25. Pourquoi le LLM principal reste externe au lancement

Un VPS CPU 24 Go peut exécuter le reste de SMART_AO. Héberger un gros LLM génératif sur CPU introduirait :

- latence élevée ;
- débit faible ;
- contention mémoire ;
- forte dégradation avec long contexte ;
- exploitation plus complexe.

La cible est donc :

```text
VPS France CPU
   ├── métier
   ├── données
   ├── extraction
   ├── OCR
   ├── embeddings
   ├── retrieval
   └── règles
          │
          └── HTTPS → LLM externe
```

---

## 26. Contrat du `LLMProvider`

Le port doit couvrir au minimum :

- requête structurée ;
- réponse structurée JSON/schema ;
- timeout ;
- retry contrôlé ;
- idempotence logique lorsque possible ;
- estimation/mesure tokens ;
- modèle demandé ;
- raison d’échec normalisée ;
- trace d’appel sans fuite de secret ;
- politique de données envoyées ;
- version du prompt ;
- corrélation avec consultation/version DCE.

Il ne doit pas exposer dans le domaine des objets propres au SDK d’un fournisseur.

---

## 27. Données envoyées au LLM

Principe de minimisation :

```text
DCE complet ✗

passages pertinents + contexte métier nécessaire + schéma attendu ✓
```

Avant chaque flux externe, documenter :

- quelles données quittent le VPS ;
- finalité ;
- fournisseur ;
- région de traitement si disponible ;
- durée de rétention contractuelle ;
- chiffrement en transit ;
- opt-out entraînement / paramètres contractuels lorsque disponibles ;
- données personnelles potentielles ;
- secrets exclus ;
- journal d’audit.

---

## 28. Résilience au fournisseur LLM

Le fonctionnement doit prévoir :

- timeout ;
- 429/rate limiting ;
- 5xx ;
- indisponibilité ;
- réponse non conforme au schéma ;
- refus du modèle ;
- modèle retiré ;
- coût anormal ;
- changement de comportement.

Le système doit pouvoir mettre l’analyse en état `pending/retryable/failed` plutôt que produire silencieusement une réponse incomplète.

Pour les résultats critiques, un LLM indisponible doit dégrader SMART_AO en « analyse IA indisponible » et non en fausse décision métier.

## 28.1 Contenus non fiables et prompt injection

**Statut : T — C1 sécurité**

Tout contenu provenant d’un DCE, PDF, DOC/DOCX, XLS/XLSX, archive, e-mail, texte tiers, pièce jointe ou source externe doit être traité comme **donnée non fiable** et jamais comme instruction système.

```text
CONTENU DOCUMENTAIRE = DATA NON FIABLE
CONTENU DOCUMENTAIRE ≠ POLITIQUE / INSTRUCTION SYSTÈME
```

Un contenu documentaire ne peut pas, par son texte seul :

- changer les droits ;
- modifier une politique système ;
- déclencher un outil ou une intégration ;
- autoriser un export ou partage ;
- envoyer un message ;
- valider une décision ;
- modifier une preuve ;
- déposer un pli ;
- exfiltrer un secret ou une donnée d’un autre périmètre.

Des tests adversariaux doivent couvrir le prompt injection et la contamination de contexte.

---

# PARTIE X — FRONTEND

## 29. Node.js / pnpm

**Statut : V — C0 build frontend**

Image de build actuelle : Node.js 22 Alpine pinnée par digest.

Gestionnaire déclaré :

```text
pnpm 11.21.0
```

Lockfile : `web/pnpm-lock.yaml`.

---

## 30. React / TypeScript / Vite

**Statut : V — C0 frontend**

Dépendances principales actuelles :

- React `19.2.8` ;
- React DOM `19.2.8` ;
- TypeScript `7.0.2` ;
- Vite `8.2.1` ;
- plugin React pour Vite.

Le runtime de production ne nécessite pas Node.js : le frontend compilé est servi comme fichiers statiques par Nginx.

---

## 31. Nginx frontend

**AS-IS : V — C0 frontend production. TO-BE : D/CANDIDATE.**

L’image finale frontend utilise Nginx 1.29 Alpine pinné par digest et un utilisateur `nginx` non-root.

Mission actuelle : servir le bundle statique et fournir le healthcheck du frontend.

Avant Architecture Freeze, comparer explicitement :

- **Option A** : Caddy + Nginx, comme dans V8 ;
- **Option B** : Caddy sert aussi le frontend statique si toutes les fonctions nécessaires sont couvertes.

La suppression de Nginx n’est pas un objectif en soi ; elle n’est justifiée que si elle réduit réellement la surface d’exploitation sans perte fonctionnelle.

---

# PARTIE XI — EDGE, TLS ET RÉSEAU

## 32. Caddy

**Statut : V — C0 production web**

Le compose préproduction utilise Caddy 2.10 Alpine pinné par digest.

Mission :

- ports 80/443 ;
- TLS ;
- reverse proxy ;
- point d’entrée public ;
- routage frontend/backend ;
- logs edge.

Les composants PostgreSQL, ClamAV et backend ne doivent pas être publiés directement sur Internet.

---

## 33. DNS

**Statut : T — C0**

Dépendance externe opérationnelle : fournisseur DNS du domaine client/SmartAO.

Doit être documenté dans le runbook :

- enregistrement ;
- changement d’IP VPS ;
- TTL ;
- DNSSEC si retenu ;
- procédure de reprise.

---

# PARTIE XII — AUTHENTIFICATION ET CRYPTOGRAPHIE

## 34. JWT

**Statut : V — C1 sécurité**

Implémenté via PyJWT avec :

- clé de signature injectée ;
- issuer ;
- audience ;
- key id / clés de vérification ;
- rotation prévue par script ops.

Une clé de développement ne doit jamais être réutilisée en production.

---

## 35. Hash de mot de passe

**Statut : V — C1**

Argon2 via `argon2-cffi`.

Les paramètres de coût doivent être benchmarkés sur le VPS afin de résister aux attaques sans rendre les connexions indisponibles.

---

## 36. MFA / TOTP

**Statut : V/VD — C1**

Le dépôt prévoit :

- activation MFA ;
- secret TOTP chiffré ;
- clé Fernet injectée ;
- issuer configuré.

La clé de chiffrement TOTP doit être sauvegardée de façon sécurisée : perdre cette clé rend les secrets chiffrés inutilisables.

## 36.1 Sessions, révocation et step-up

**Statut : T/D — C1 sécurité**

Le choix JWT/TOTP ne suffit pas à définir un modèle de session. Le mécanisme cible doit rendre exécutables les règles produit déjà fixées :

- inactivité : **30 minutes par défaut** ;
- durée absolue : **12 heures par défaut** ;
- avertissement avant expiration lorsque l’écran est actif ;
- step-up lié à **l’action et à la version**, utilisable au plus **5 minutes** ;
- invalidation du step-up si cible, droits ou version changent ;
- révocation immédiate des sessions/facteurs compromis ;
- récupération normale et exceptionnelle ;
- gestion du dernier Propriétaire compromis ;
- conservation du contexte utile après réauthentification sans contourner les droits.

Un ADR doit décider : session server-side ou hybride, access token, refresh/rotation éventuelle, révocation, stockage des sessions, corrélation d’audit et récupération MFA.

## 36.2 Support exceptionnel / break-glass

**Statut : T/D — C1 sécurité**

Le support SMART AO n’acquiert jamais automatiquement les droits métier du client. L’accès au contenu doit être exceptionnel, nommé, borné et traçable.

Contrat minimal :

- métadonnées minimales par défaut ;
- opérateur SMART AO identifié ;
- demande/approbation explicite ;
- scope précis ;
- durée limitée et expiration automatique ;
- journalisation ;
- révocation ;
- données Direction séparées ;
- impossibilité pour le support de devenir Patron, Propriétaire métier ou signataire.

---

# PARTIE XIII — CONNECTEURS EXTERNES

## 37. INSEE Sirene

**Statut : VD — C2**

Le dépôt prévoit un enrichissement **read-only** vers l’API Sirene de l’INSEE via token injecté à l’exécution.

Règles :

- timeout court ;
- allowlist de données utiles ;
- cache éventuel uniquement si juridiquement/techniquement pertinent ;
- panne INSEE ne bloque pas le cœur DCE ;
- aucun secret dans le dépôt.

---

## 38. BOAMP

**Statut : VD — C2**

Recherche d’avis publics BOAMP, désactivée par défaut.

Le connecteur doit rester un adaptateur externe et normaliser les résultats vers un contrat interne SMART_AO.

---

## 39. HTTP générique

**Statut : VD — C2**

L’extra `connectors` déclare `httpx`.

Il peut servir aux connecteurs externes, mais chaque intégration doit définir :

- domaine/URL autorisé ;
- méthode ;
- auth ;
- timeout ;
- retry ;
- limites de taille ;
- données autorisées ;
- journalisation sans secrets.

---

## 40. SMTP

**Statut : VD — C2**

Extra : `aiosmtplib`.

Le dépôt prévoit des notifications d’état et un worker SMTP.

Règle actuelle saine : les notifications ne doivent pas transporter silencieusement des documents ou montants sensibles si la fonctionnalité n’a pas été explicitement conçue pour cela.

En production, le fournisseur SMTP devient une dépendance externe à inventorier (hébergeur, quotas, TLS, réputation, SPF/DKIM/DMARC selon le domaine utilisé).

---

## 41. Webhooks / portail de dépôt

**Statut : VD/D — C2**

Le compose prévoit un worker `submission-export-webhook` avec URL et secret injectés.

Règles :

- HMAC/signature ;
- anti-replay si nécessaire ;
- timeout ;
- retry via outbox ;
- idempotence ;
- ne jamais déclarer un dépôt externe réussi sans accusé vérifiable.

---

## 42. Fournisseur de signature

**Statut : D — C2**

Le dépôt prévoit `SMART_AO_SIGNATURE_PROVIDER` et un secret de callback, mais aucun fournisseur ne doit être considéré comme engagé tant qu’un choix produit, juridique et contractuel n’est pas fait.

---

## 43. Calendrier ICS

**Statut : VD — C3**

Extra `icalendar`. L’approche actuelle est un export ICS local, sans synchronisation distante obligatoire. C’est une bonne manière de garder cette fonction faiblement couplée.

---

## 44. Event bus externe

**Statut : VD/F — C3**

Un worker optionnel `opportunity-event-bus` existe sous profile `external-bus`.

Il ne doit être activé que si un cas d’intégration concret justifie l’ajout d’un service externe. L’outbox PostgreSQL reste la base de fiabilité interne.

---

# PARTIE XIV — WORKERS ET ASYNCHRONISME

## 45. Workers présents dans le déploiement

Le compose préproduction contient notamment :

- `dce-retention-worker` ;
- `dce-rc-analysis-runner` ;
- `dce-requirements-runner` ;
- `submission-export-webhook-worker` ;
- `submission-export-smtp-worker` ;
- `opportunity-event-bus-worker` optionnel ;
- `cockpit-projection-worker` optionnel.

Cette stratégie montre qu’un broker externe n’est pas nécessaire aujourd’hui.

### Politique cible

Les traitements longs doivent quitter le chemin HTTP :

```text
requête utilisateur
      ↓
commande persistée / état
      ↓
worker
      ↓
résultat versionné
      ↓
UI / notification
```

OCR, extraction avancée, indexation RAG et gros appels LLM doivent suivre le même principe.

### 45.1 N02 — résultat d’opération inconnu

Les opérations à effet externe doivent modéliser explicitement le cas où l’effet peut avoir eu lieu sans confirmation reçue.

Contrat recommandé :

```text
OperationAttempt
- attempt_id
- object_id / object_version
- requested_at
- idempotency_key
- last_confirmed_state
- external_reference
- outcome = confirmed_success | confirmed_failure | unknown
```

En état `unknown` :

- ne pas relancer automatiquement une opération à effet ;
- vérifier l’état avant retry ;
- préserver la dernière vérité confirmée ;
- rendre l’incertitude visible à l’UX ;
- journaliser la résolution.

Cette règle concerne notamment P5, exports, uploads tiers, webhooks, synchronisation terrain et toute future automatisation de remise.

---

# PARTIE XV — OUTILS DE DÉVELOPPEMENT ET QUALITÉ

## 46. Outils Python de développement

**Statut : V — C3 développement**

| Outil | Rôle |
|---|---|
| pytest | tests |
| pytest-cov | couverture |
| Ruff | lint/qualité |
| Bandit | sécurité statique Python |
| detect-secrets | détection de secrets |
| pip-audit | vulnérabilités dépendances Python |
| mypy | typage statique |
| httpx | tests/API et connecteurs dev |

Le seuil de couverture déclaré est actuellement de **85,50 %** avec couverture de branches.

---

## 47. Outils frontend de développement

**Statut : V — C3**

- ESLint ;
- Vitest ;
- Testing Library ;
- jsdom ;
- TypeScript typecheck ;
- Vite build.

Tous les changements frontend doivent passer au minimum build, typecheck, lint et tests pertinents.

---

## 48. Git / GitHub

**Statut : V/T — C1 chaîne de livraison**

Dépendances de développement :

- Git pour l’historique et les revues ;
- GitHub pour dépôt distant, PR et automatisation si maintenu comme forge principale.

Le serveur de production ne doit pas dépendre d’un accès GitHub permanent pour servir les utilisateurs. Le déploiement doit pouvoir fonctionner à partir d’artefacts/images approuvés.

---

# PARTIE XVI — SAUVEGARDE ET RESTAURATION

## 49. Sauvegardes

**Statut : V partiel / T — C0 exploitation**

Le dépôt contient déjà des scripts de backup et restore préproduction.

En production, sauvegarder séparément :

1. PostgreSQL ;
2. objets/documents ;
3. secrets nécessaires à la restauration, par canal séparé ;
4. configuration déployée ;
5. modèles locaux versionnés ou leur référence reproductible ;
6. métadonnées RAG si elles ne sont pas reproductibles rapidement.

### Règle absolue

Une sauvegarde non restaurée en test n’est pas une sauvegarde prouvée.

Prévoir :

- sauvegarde hors VPS ;
- chiffrement ;
- rétention ;
- contrôle d’intégrité ;
- restauration isolée périodique ;
- RPO et RTO contractuellement définis.

Pour chaque classe d’actif, maintenir une matrice :

```text
objet | RPO | RTO | backup | restore test | chiffrement | rétention | purge | preuve
```

Au minimum : PostgreSQL, documents/objets, manifestes/reçus, secrets et clés nécessaires à la restauration, configuration, index non rapidement reproductibles et journaux indispensables à la clôture.

---

# PARTIE XVII — OBSERVABILITÉ

## 50. Logs

**Statut : V partiel — C1**

Le compose configure des logs Docker `json-file` avec rotation.

À standardiser :

- correlation ID ;
- tenant ID non sensible ;
- consultation/case ID ;
- worker/job ID ;
- type d’événement ;
- latence ;
- résultat ;
- cause normalisée ;
- jamais de secret, token, DCE complet ou mot de passe.

---

## 51. Métriques / tracing / error tracking

**Statut : D/T — C2**

Ne pas installer Grafana, Prometheus, Loki, Sentry et OpenTelemetry tous ensemble par défaut.

Décider selon la phase :

### Minimum lancement

- healthchecks ;
- logs structurés ;
- alertes disque/RAM/CPU ;
- état backup ;
- erreurs applicatives ;
- disponibilité HTTP.

### Extension

Prometheus/Grafana, OpenTelemetry, Sentry ou stack équivalente uniquement si le besoin d’investigation l’exige.

### 51.1 Événements métier critiques à rendre observables

Sans exposer de secrets métier, la plateforme doit pouvoir détecter et corréler au minimum :

- import échoué / fichier quarantiné ;
- extraction ou OCR partiel ;
- analyse IA indisponible/échouée ;
- revalidation requise après changement de source/version ;
- P5 et step-up associé ;
- export et partage externe ;
- accès support exceptionnel ;
- opération N02 / résultat inconnu ;
- backup/restore ;
- saturation disque/RAM ;
- purge/rétention ;
- récupération du Propriétaire.

---

# PARTIE XVIII — DÉPENDANCES NON RECOMMANDÉES PAR DÉFAUT

## 52. Ce que SMART_AO ne doit pas installer « parce que c’est populaire »

| Composant | Position actuelle |
|---|---|
| Redis | non requis tant que PostgreSQL/outbox suffit |
| Qdrant/Weaviate/Milvus | ne pas ajouter avant benchmark pgvector / besoin prouvé |
| Kubernetes | excessif pour un VPS dédié par entreprise au lancement |
| gros LLM local CPU | non recommandé pour la génération principale |
| GPU par client | non requis dans l’architecture cible initiale |
| Kafka | excessif sans débit justifiant son coût opérationnel |
| Elastic/OpenSearch | ne pas ajouter tant que PostgreSQL/recherche existante suffit |
| plusieurs fournisseurs OCR simultanés | éviter ; un port, une implémentation active, benchmarks |
| plusieurs moteurs d’embedding actifs | éviter ; versionner et benchmarker |

Le principe d’architecture est **sobriété de dépendances**.

---

# PARTIE XIX — BUDGET RESSOURCES D’UN VPS 24 Go

## 53. Budget indicatif

Ce tableau est un budget de conception, pas une mesure contractuelle.

| Composant | RAM typique à prévoir | Nature |
|---|---:|---|
| Linux + Docker | ~1–2 Go | permanent |
| PostgreSQL | ~2–5 Go selon tuning | permanent |
| backend FastAPI + workers légers | ~1–3 Go | permanent/variable |
| ClamAV | ~1–3 Go | permanent |
| Caddy + Nginx | <1 Go | permanent |
| embedding BGE-M3 | plusieurs Go selon runtime/dtype | chargé à la demande ou worker dédié |
| OCR ONNX | ~1–3+ Go selon modèles/batch | transitoire |
| Docling/extraction avancée | variable, potentiellement plusieurs Go | transitoire |
| réserve OS / pics / filesystem cache | 4–6 Go souhaitables | sécurité |

### Conséquence

24 Go est une cible crédible **si la concurrence des jobs lourds est contrôlée**.

Ne pas charger simultanément sans limite :

- plusieurs OCR ;
- plusieurs extractions avancées ;
- plusieurs embeddings de gros DCE ;
- gros reranking ;
- scans antivirus massifs.

Utiliser des files/leases et limites de concurrence.

### 53.1 Gate économique par client

Le sizing n’est pas uniquement un problème de performance. Avant le gel de production, mesurer :

```text
coût VPS
+ sauvegarde hors site
+ stockage
+ trafic
+ SMTP / services externes
+ LLM
+ supervision
+ exploitation / support
= coût réel mensuel par client
```

Le dimensionnement final doit rester compatible avec le modèle économique des PME BTP ciblées.

---

# PARTIE XX — MATRICE SYNTHÉTIQUE DES DÉPENDANCES

## 54. Socle obligatoire

| Dépendance | Statut | C | GPU | Internet runtime | Remplaçable |
|---|---|---:|---|---|---|
| Linux VPS | T | C0 | non | réseau général | oui |
| Docker/Compose | V | C0 | non | non après images | oui, coûteux |
| Python 3.12 | V | C0 | non | non | évolution planifiée |
| FastAPI/Uvicorn | V | C0 | non | non | oui, coûteux |
| PostgreSQL 16 | V | C0 | non | non | théoriquement, très coûteux |
| SQLAlchemy/Alembic/psycopg | V | C0 | non | non | oui |
| React/TypeScript/Vite | V | C0 | non | build seulement | oui, coûteux |
| Nginx | V | C0 | non | non | oui |
| Caddy | V | C0 | non | ACME/DNS selon TLS | oui |
| ClamAV | V | C1 | non | mises à jour signatures | oui |

## 55. Mission DCE / IA

| Dépendance | Statut | C | GPU | Internet runtime | Remplaçable |
|---|---|---:|---|---|---|
| pypdf | V | C1 | non | non | oui |
| python-docx | V | C1 | non | non | oui |
| openpyxl | V | C1 | non | non | oui |
| Docling | VD | C2 | non obligatoire | modèle/cache selon préparation | oui |
| PyMuPDF | VD | C2 | non | non | oui |
| RapidOCR + ONNX | VD | C2 | non | non si modèles locaux | oui |
| sentence-transformers | VD | C1/2 | non | non si modèle local | oui |
| BGE-M3 | VD/D | C1/2 | non | non si préchargé | oui |
| pgvector | D/T | C2 | non | non | oui |
| reranker | D/T | C2 | non | non si local | oui |
| LLM externe | T | C1 | GPU chez fournisseur | oui | **doit l’être** |

## 56. Services externes

| Service | Statut | Blocage du cœur ? | Données sortantes |
|---|---|---|---|
| INSEE Sirene | VD | non | requête entreprise limitée |
| BOAMP | VD | non | critères de recherche |
| SMTP | VD | non | métadonnées notification autorisées |
| Webhook dépôt | VD/D | dépend du parcours dépôt | payload explicitement contrôlé |
| Signature externe | D | dépend du parcours | à définir |
| S3 distant | D/T | selon choix stockage | documents si activé |
| LLM | T | oui pour fonctions IA avancées | contexte DCE minimisé |

### 56.1 Fiche obligatoire pour chaque dépendance externe

Pour chaque service externe actif, documenter :

- propriétaire/fournisseur ;
- finalité ;
- URL/domaines autorisés ;
- données envoyées et reçues ;
- authentification ;
- timeout ;
- retry et idempotence ;
- région/résidence ;
- politique de rétention ;
- DPA/contrat applicable ;
- quota ;
- coût ;
- fallback ;
- criticité métier ;
- procédure de sortie/migration si le fournisseur disparaît.

---

# PARTIE XXI — GOUVERNANCE DES DÉPENDANCES

## 57. Conditions d’acceptation d’une nouvelle dépendance

Aucune dépendance ne doit être ajoutée avant d’avoir répondu à :

1. Quel problème exact résout-elle ?
2. Ce problème existe-t-il réellement aujourd’hui ?
3. Une dépendance déjà présente sait-elle le faire ?
4. La stdlib / PostgreSQL / Docker / navigateur sait-il le faire ?
5. Quel est son coût RAM/CPU/disque ?
6. Appelle-t-elle Internet ?
7. Quelles données reçoit-elle ?
8. Quelle licence ?
9. Quelle maturité et quel rythme de maintenance ?
10. Quelle surface CVE/supply-chain ajoute-t-elle ?
11. Comment la tester ?
12. Comment la désactiver ?
13. Comment migrer si le projet disparaît ?
14. Quel composant possède son adaptation ?
15. Son installation est-elle reproductible ?

Si ces réponses ne sont pas documentées, la dépendance n’entre pas dans le socle.

---

## 58. Pinning / reproductibilité

SMART_AO applique ou doit appliquer :

- `uv.lock` figé ;
- `pnpm-lock.yaml` figé ;
- images Docker par digest pour production ;
- modèles ML identifiés par version/hash ;
- migrations Alembic versionnées ;
- configuration déclarative ;
- versions des prompts et schémas IA ;
- migrations de données reproductibles.

---

## 59. Sécurité supply-chain

Déjà présents dans les dépendances dev :

- Bandit ;
- detect-secrets ;
- pip-audit.

À prévoir dans la chaîne CI/CD :

- audit npm/pnpm ;
- scan des images conteneur ;
- SBOM (CycloneDX ou SPDX) ;
- vérification des licences ;
- revue des mises à jour de digest ;
- politique de secrets ;
- dépendances directes minimisées.

Outils exacts à choisir ultérieurement ; ne pas multiplier les scanners sans politique de traitement des alertes.

Compléments à formaliser :

- provenance des images ;
- politique de mise à jour des digests ;
- fenêtre de patch critique ;
- procédure EOL ;
- licences et hashes des modèles ML ;
- hashes des artefacts téléchargés ;
- interdiction des téléchargements dynamiques non contrôlés en production.

---

## 60. Matrice de sortie réseau

La production doit maintenir une allowlist conceptuelle des sorties :

```text
Caddy          → ACME si certificats automatiques
ClamAV         → signatures antivirus
Backend        → LLM choisi
Backend        → INSEE si activé
Backend        → BOAMP si activé
SMTP worker    → serveur SMTP si activé
Webhook worker → portail externe configuré
Object storage → endpoint S3 si distant
```

PostgreSQL ne nécessite aucune sortie Internet.

Le worker OCR local et les embeddings locaux ne doivent pas télécharger de modèles dynamiquement en production.

---

# PARTIE XXII — STRATÉGIE DE DÉPLOIEMENT PAR ENTREPRISE

## 61. Un VPS dédié par entreprise

Le modèle envisagé apporte :

- isolation forte ;
- capacité connue par client ;
- restauration client par client ;
- logs séparés ;
- secrets séparés ;
- données séparées ;
- réduction du risque de fuite cross-tenant infrastructurelle.

Il implique en contrepartie :

- automatisation du provisioning ;
- mise à jour de plusieurs instances ;
- gestion de versions ;
- monitoring de flotte ;
- sauvegardes par instance ;
- coûts linéaires.

Le futur outil de déploiement doit traiter la pile comme un **template immuable versionné**, pas comme des VPS configurés manuellement au fil du temps.

### 61.1 Control Plane minimal / Data Plane client

La flotte d’instances nécessite à terme un Control Plane minimal, distinct du Data Plane métier de chaque client.

Le Control Plane peut gérer :

- inventaire des instances ;
- version déployée ;
- health ;
- état des sauvegardes ;
- usage/quota ;
- orchestration des mises à jour ;
- rotation des secrets ;
- provisioning / deprovisioning.

Il ne doit pas centraliser par commodité : DCE, prix, marges, preuves, documents client ou données Direction. Le Data Plane dédié reste l’autorité métier de l’entreprise cliente.

---

## 62. Dépendances par phase

### Phase A — socle de production

Conserver :

```text
Linux
Docker Compose
Caddy
Nginx
React
Backend V8 : FastAPI / Python 3.12 (baseline à réévaluer par ADR)
PostgreSQL
ClamAV
parsers de base
workers/outbox
backup/restore
```

### Phase B — analyse DCE renforcée

Activer selon benchmarks :

```text
Docling / PyMuPDF
RapidOCR / ONNX
sentence-transformers
BGE-M3 ou alternative benchmarkée
index vectoriel retenu
reranker retenu
LLMProvider externe
```

### Phase C — intégrations

Activer uniquement selon contrat/client :

```text
INSEE
BOAMP
SMTP
S3/MinIO
signature
webhooks dépôt
calendar
external event bus
```

### Phase D — scale

Évaluer seulement lorsqu’une limite est mesurée :

```text
Redis
vector DB dédié
queue/broker spécialisé
cluster GPU
orchestration plus lourde
observabilité distribuée
```

---

# PARTIE XXIII — DÉCISIONS ENCORE OUVERTES

## 63. ADR à produire

Les décisions suivantes devraient avoir un ADR distinct avant production :

| ADR | Décision |
|---|---|
| DEP-ADR-001 | Fournisseur(s) LLM et contrat `LLMProvider` |
| DEP-ADR-002 | Stockage vectoriel : pgvector ou moteur dédié |
| DEP-ADR-003 | Modèle d’embedding français/BTP après benchmark |
| DEP-ADR-004 | Reranker et seuil de gain minimal |
| DEP-ADR-005 | Stratégie OCR et critères de déclenchement |
| DEP-ADR-006 | Object storage : MinIO local vs S3 externalisé |
| DEP-ADR-007 | Observabilité minimale et stack éventuelle |
| DEP-ADR-008 | SMTP/fournisseur notification |
| DEP-ADR-009 | Signature électronique si intégrée |
| DEP-ADR-010 | Hébergeur VPS, sizing et politique de montée en charge |
| DEP-ADR-011 | RPO/RTO + stockage de sauvegarde hors site |
| DEP-ADR-012 | Politique données envoyées au LLM / résidence / rétention |
| DEP-ADR-013 | Backend final : conserver Python/FastAPI, autre stack ou hybride |
| DEP-ADR-014 | Sessions, refresh éventuel, révocation, MFA recovery et step-up |
| DEP-ADR-015 | Safe archives / formats legacy DOC-XLS / documents protégés |
| DEP-ADR-016 | Prompt injection / isolation des tools et contenus non fiables |
| DEP-ADR-017 | Control Plane vs Data Plane et données autorisées au Control Plane |
| DEP-ADR-018 | Support exceptionnel / break-glass |
| DEP-ADR-019 | Caddy + Nginx vs Caddy seul pour le frontend statique |
| DEP-ADR-020 | Enforcement tenant/RBAC dans retrieval, RAG, caches et IA |
| DEP-ADR-021 | Secrets/KMS, rotation, sauvegarde et restauration des clés |
| DEP-ADR-022 | Budget de coût cible par instance / infra + IA + exploitation |

---

# PARTIE XXIV — TESTS D’ACCEPTATION DE L’ARCHITECTURE

## 64. Benchmark VPS obligatoire avant gel production

Sur un VPS équivalent cible, mesurer au minimum :

- démarrage complet ;
- RAM idle ;
- RAM pic ;
- CPU moyen/pic ;
- import d’un petit DCE ;
- import d’un DCE moyen ;
- gros DCE ;
- PDF texte ;
- PDF scan ;
- DOCX ;
- XLSX ;
- scan ClamAV ;
- extraction simple ;
- extraction avancée ;
- OCR ;
- embedding ;
- indexation ;
- retrieval ;
- reranking ;
- appel LLM ;
- concurrence de 2/5/10 analyses selon profil client ;
- backup ;
- restore ;
- redémarrage après panne ;
- saturation disque ;
- archives ZIP/7z imbriquées et protections anti-zip-bomb ;
- XLS/XLSX volumineux avec formules/feuilles masquées ;
- expiration/révocation de session et step-up ;
- opération N02 / résultat externe inconnu ;
- indisponibilité LLM ;
- indisponibilité INSEE/BOAMP/SMTP ;
- coût mensuel estimé par profil client.

Les limites de concurrence des workers doivent être dérivées de ces mesures, pas d’intuitions.

---

# PARTIE XXV — POSITION D’ARCHITECTURE RETENUE À CE STADE

## 65. Position de travail corrigée — non gelée

SMART_AO ne doit pas devenir une collection de microservices et de bases spécialisées avant d’en avoir besoin.

La cible de travail est :

```text
1 environnement dédié / entreprise au lancement
        │
        ├── déploiement reproductible
        ├── application tenant-aware
        ├── code produit unique
        ├── modular monolith privilégié
        ├── PostgreSQL autoritatif
        ├── stockage documents derrière ObjectStorage
        ├── pipeline DCE sécurisé + quarantaine
        ├── workers idempotents / outbox
        ├── OCR / extraction / embeddings selon benchmark
        ├── retrieval hybride avec droits appliqués
        ├── LLM derrière LLMProvider
        ├── auth/session/MFA/step-up
        ├── audit / backup / restore
        └── egress contrôlé
```

À ce stade, les **implémentations exactes** suivantes restent ouvertes ou soumises à benchmark/ADR :

- backend final : maintien Python/FastAPI, autre stack ou hybride ;
- vector store ;
- modèle d’embedding ;
- reranker ;
- object storage ;
- Caddy + Nginx ou simplification ;
- observabilité ;
- fournisseurs externes ;
- secrets manager / KMS ;
- Control Plane ;
- sizing VPS final.

Règles toujours valides :

- **pas de GPU obligatoire** au lancement ;
- **pas de Redis obligatoire** ;
- **pas de Kubernetes** ;
- **pas de Kafka** ;
- **pas de vector DB séparé sans benchmark** ;
- **pas de gros LLM génératif local sur CPU** ;
- **pas de téléchargement de modèles ML non contrôlé en production** ;
- **pas de migration de langage/framework sans ADR et bénéfice mesuré**.

Cette position maximise la sobriété tout en laissant l’Architecture Freeze décider des implémentations finales à partir des expériences validées et des mesures réelles.

---

# ANNEXE A — INVENTAIRE VÉRIFIÉ DU DÉPÔT AU 17/09/2026

**Contre-vérification du 17/09/2026 :** les éléments structurants ci-dessous ont été recroisés en lecture seule avec le dépôt GitHub `mailtkarim-bot/SMART_AO_V8`, notamment `pyproject.toml`, `web/package.json`, `ops/docker-compose.preprod.yml`, `ops/docker/backend.Dockerfile` et `ops/docker/frontend.Dockerfile`. Cette vérification confirme l’AS-IS du dépôt, pas sa promotion automatique en cible finale.

## A.1 Fichiers de dépendances et infrastructure

- `pyproject.toml`
- `uv.lock`
- `web/package.json`
- `web/pnpm-lock.yaml`
- `docker-compose.yml`
- `ops/docker-compose.preprod.yml`
- `ops/docker/backend.Dockerfile`
- `ops/docker/frontend.Dockerfile`
- `ops/Caddyfile`
- `ops/nginx/...`
- `.env.example`
- `ops/.env.preprod.example`
- `alembic.ini`
- `backend/alembic/...`
- `Makefile`
- `ruff.toml`
- `.secrets.baseline`

## A.2 Images vérifiées dans les manifests consultés

- `python:3.12-slim` — pinnée SHA256 ;
- `node:22-alpine` — pinnée SHA256 ;
- `nginx:1.29-alpine` — pinnée SHA256 ;
- `postgres:16-alpine` — pinnée SHA256 ;
- `clamav/clamav:1.4_base` — pinnée SHA256 ;
- `caddy:2.10-alpine` — pinnée SHA256.

Les digests exacts restent la source de vérité dans les Dockerfiles/Compose et ne doivent pas être recopiés manuellement dans ce référentiel à chaque mise à jour.

---

# ANNEXE B — RÈGLE DE MAINTENANCE DU PRÉSENT DOCUMENT

Ce référentiel doit être mis à jour lorsque :

- une dépendance directe est ajoutée/supprimée ;
- un service Docker est ajouté/supprimé ;
- un modèle ML change ;
- un fournisseur externe est ajouté ;
- un flux de données sortant est introduit ;
- une base de données supplémentaire apparaît ;
- une nouvelle classe de documents est supportée ;
- un secret/configuration critique apparaît ;
- une dépendance devient EOL ;
- un ADR modifie une décision listée ci-dessus ;
- un OWNER EXPERIENCE FREEZE introduit une nouvelle exigence technique ;
- une décision produit modifie les droits, l’isolation, les flux externes ou la réversibilité.

Une PR qui modifie `pyproject.toml`, `web/package.json`, Dockerfiles, Compose, connecteurs externes ou les ports de dépendances doit vérifier si ce document doit être modifié.

---

## Conclusion

Le vrai actif de SMART_AO n’est pas son nombre de dépendances. C’est sa capacité à **orchestrer un petit nombre de composants bien maîtrisés**, avec preuve, isolation, autorisations, reprise et fallback, pour transformer des DCE complexes en décisions métier fiables.

La dépendance la plus dangereuse est celle dont le produit ne sait plus se passer sans la connaître explicitement. Le présent document doit empêcher cette situation.

À ce stade, ce référentiel est une **base technique majeure mais non gelée**. Il doit accompagner la conception des expériences, puis être consolidé après le Cahier technique, les ADR et les benchmarks. Sa promotion vers `docs/reference/` interviendra seulement à l’Architecture Freeze.
