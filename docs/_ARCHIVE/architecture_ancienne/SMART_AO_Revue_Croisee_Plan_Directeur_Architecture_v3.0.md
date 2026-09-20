# SMART AO — Revue croisée du plan directeur d’architecture logicielle v3.0

**Version : 1.0 — 12 septembre 2026**  
**Statut : rapport de revue avant autorisation de reprise du cœur logiciel**  
**Document examiné : `SMART_AO_Architecture_Logicielle_v3.0_PLAN_DIRECTEUR_FINAL.md`**

---

# 0. Décision proposée

Le plan directeur v3.0 est **validé comme charte d’orientation et comme mandat de Phase 0**.

Il n’est pas encore suffisamment fermé pour autoriser directement les PR-A2 à PR-A4 ni, a fortiori, la construction des tranches B à I. Le bon statut opérationnel est donc :

> **GO pour l’audit Phase 0.**  
> **HOLD sur la transformation du cœur jusqu’à validation du dossier de sortie de Phase 0.**  
> **NO-GO pour un pilote contenant des données client réelles tant que les gates sécurité, données, exploitation et qualité ne sont pas définies et démontrées.**

Ce verdict ne remet pas en cause l’architecture choisie. Il distingue trois niveaux que le document mélange encore :

1. la direction cible, qui est cohérente ;
2. l’autorisation d’auditer et de mesurer V8, qui peut être donnée maintenant ;
3. l’autorisation de modifier le cœur et d’exploiter le produit, qui exige encore des preuves et des décisions.

---

# 1. Périmètre de la revue

La revue confronte le plan directeur avec les sources suivantes :

1. [Cahier des charges métier v1.0](SMART_AO_Cahier_des_charges_Metier_v1.0.md) ;
2. [Univers documentaire métier v1.0](SMART_AO_Univers_documentaire_metier_v1.0.md) ;
3. [CCF UX Product Blueprint v1.1](SMART_AO_CCF_UX_Product_Blueprint_v1.1.md) ;
4. [Registre des décisions d’architecture préliminaires v0.1](SMART_AO_Registre_Decisions_Architecture_Preliminaires_v0.1.md) ;
5. [Benchmark concurrentiel UX et parcours v1.0](SMART_AO_Benchmark_Concurrentiel_UX_Parcours_v1.0.md) ;
6. [Architecture métier et technique v2.3](SMART_AO_Cahier_des_charges_Architecture_Metier_v2.3.docx) ;
7. [Cadrage directeur initial v3.0](SMART_AO_Architecture_Logicielle_v3.0_Cadrage_Directeur_INITIAL.md) ;
8. la structure, les contrats, les migrations et les tests présents dans V8.

Cette revue porte sur la cohérence, la traçabilité, l’exécutabilité et les gates de décision. Elle ne constitue pas encore l’audit exhaustif Phase 0 demandé au chapitre 21 du plan.

---

# 2. Conclusion générale

Le plan directeur a la bonne colonne vertébrale :

- V8 reste le socle ;
- la migration est progressive ;
- le monolithe reste modulaire ;
- la preuve, la version et l’autorité humaine structurent le produit ;
- l’IA travaille dans un harnais contrôlé ;
- l’instance dédiée ne remplace pas les droits applicatifs ;
- le produit reste utilisable lorsque le fournisseur IA est indisponible ;
- le développement commence par une tranche probatoire mesurable ;
- les composants séduisants mais non prouvés sont différés.

Ce sont de bonnes décisions. Elles répondent directement au risque principal de SMART AO : construire un logiciel impressionnant qui résume beaucoup, mais qui ne sait pas prouver qu’il a lu le bon dossier, appliqué la bonne version, protégé la marge et préparé le bon paquet.

Le plan reste toutefois **un plan directeur condensé**, pas encore un contrat de construction complet. Sa faiblesse ne vient pas d’un mauvais choix technologique. Elle vient de l’absence des tables qui relient les décisions métier aux composants, aux propriétaires de données, aux tranches et aux tests.

La priorité n’est donc pas d’ajouter une nouvelle architecture. La priorité est de rendre l’architecture actuelle **traçable, mesurable et autorisable**.

---

# 3. Ce qui doit être conservé sans réouverture

## 3.1 V8 comme base de migration

La règle « aucun rewrite global » est justifiée par l’état réel du dépôt. V8 contient déjà des modules `case`, `dce`, `decision`, `enterprise`, `knowledge`, `market_watch`, `membership`, `opportunity`, `optimization`, `patron_action`, `preparation`, `pricing` et `submission`, ainsi que des mécanismes de sécurité, persistance, événements, outbox, observabilité et stockage.

La migration doit donc partir des contrats actuels, pas des noms idéaux du plan.

## 3.2 Monolithe modulaire

Le choix est cohérent avec le produit et avec le dépôt. Les tests d’architecture existants vérifient déjà plusieurs règles de pureté du domaine, de propriété des modèles et d’interdiction d’importer les détails d’infrastructure d’un autre module.

Le terme « bounded context cible » doit rester une frontière de sens et de responsabilité. Il ne doit pas déclencher automatiquement la création de quatorze nouveaux paquets, bases, files ou services.

## 3.3 Fondation probatoire

La chaîne suivante reste le meilleur premier chantier :

```text
Document / Fragment
        ↓
SourceAnchor
        ↓
Evidence
        ↓
DceRequirement
        ↓
Validation humaine
```

Le dépôt contient déjà `DceExtractionFragment`, `DceRequirement`, les sources d’exigence et les confirmations humaines. Il ne contient pas encore de `SourceAnchor` générique ni d’`Evidence` probatoire générique. La Tranche A cible donc un manque réel sans remplacer les actifs existants.

## 3.4 Single-tenant dédié et tenant-aware

Cette décision est correctement transmise depuis le CCF v1.1 et le registre ADR : un environnement métier dédié par entreprise, un code produit unique et des droits applicatifs conservés.

Elle ne doit pas être réouverte pendant la Phase 0. Les choix d’hébergeur, de stockage, de secrets et de déploiement restent réversibles.

## 3.5 Autorité humaine et dégradation sans IA

Le plan respecte le contrat d’expérience : l’IA extrait, rapproche, explique, recommande et prépare ; une personne habilitée valide et engage. Les fonctions critiques de lecture, preuve, tâche, décision, documents et remise doivent rester disponibles sans conversation et en cas d’indisponibilité du fournisseur IA.

## 3.6 Différer les abstractions non prouvées

Il faut conserver les interdictions de la Tranche A : pas de nouvel orchestrateur général, pas de GraphRAG, pas de reranker sans benchmark, pas de registre d’artefacts général, pas de vision/plans et pas de multiplication des fournisseurs par anticipation.

---

# 4. Écarts bloquants avant modification du cœur

## B01 — Le statut « final » est plus large que l’autorisation réelle

Le chapitre 20 affirme que toutes les conditions de préparation sont remplies. Le chapitre 21 interdit pourtant de construire et demande d’abord un audit du dépôt. La migration elle-même est présentée comme une série d’orientations « à confirmer par audit ».

**Risque :** un agent ou un développeur peut lire « plan final pour démarrage » comme une autorisation de créer les modèles cibles avant la confrontation au code.

**Correction :** donner au document le statut opérationnel suivant :

> **Référence directrice validée. Autorisation limitée à la Phase 0. Toute modification du cœur requiert la validation du Gate 0.**

La Definition of Done doit préciser que la direction est définie, tandis que l’architecture de migration détaillée reste une sortie de Phase 0.

## B02 — La table de traçabilité obligatoire a disparu

Le CCF v1.1 exige une table reliant l’architecture aux objets, actions, invariants, REC‑01 à REC‑28, UX‑01 à UX‑28, droits, validations externes et dossiers de vérification. Le registre ADR exige aussi que chaque décision soit reliée à une réponse technique. Le cadrage initial v3.0 prévoyait cette table avant le premier merge.

Le plan final ne la contient pas et ne la demande plus explicitement parmi les douze livrables de Phase 0.

**Risque :** une tranche peut être déclarée terminée tout en perdant un blocage métier, une autorité, un cas hostile ou une exigence de confidentialité.

**Correction :** ajouter à Phase 0 un livrable `TRC-01 — Matrice de traçabilité normative` avec au minimum :

| Champ | Contenu attendu |
|---|---|
| Référence | document, section, REC/UX/VAL/ADR |
| Exigence observable | ce qui doit être vrai pour l’utilisateur ou l’exploitation |
| Objet propriétaire | objet métier autoritatif |
| Contexte cible | responsabilité fonctionnelle |
| Module V8 actuel | propriétaire ou lecteur actuel |
| Commande ou événement | effet et frontière de transaction |
| Tranche et PR | moment de traitement |
| Test ou preuve | résultat reproductible attendu |
| Statut | couvert, partiel, absent, différé, bloqué |

## B03 — Les quatorze contextes n’ont pas encore de context map

Le plan nomme les contextes, mais ne définit pas qui possède chaque objet, qui peut l’écrire, qui ne fait que le lire, ni comment les dépendances circulent.

Plusieurs chevauchements doivent être tranchés :

- `CostFactor` apparaît dans Evidence & Market Understanding, alors que Pricing Intelligence porte les facteurs de coût ;
- partenaires et prix/achats sont dans Enterprise Memory, mais interviennent aussi dans Pricing et Handover ;
- délégation et partage apparaissent dans Identity & Access et Collaboration & Work ;
- les engagements relient Response, Pricing, Decision, Submission et Handover ;
- les rectificatifs naissent dans DCE, invalident des preuves et rouvrent des décisions, prix et documents.

**Risque :** création de doubles sources de vérité ou import direct des tables d’un module voisin.

**Correction :** produire une context map avant PR-A2. Chaque objet du dictionnaire fonctionnel du CCF doit avoir un propriétaire d’écriture unique. Les projections de lecture peuvent être dupliquées, mais leur source autoritative doit être nommée.

## B04 — La cible n’est pas encore reliée aux modules V8

Le dépôt possède déjà treize modules métier et une architecture de ports publics. Le plan propose quatorze contextes cibles sans préciser si chacun correspond à un module existant, une capacité interne, un renommage, une fusion ou une projection.

Des capacités prévues pour plus tard existent déjà partiellement : opportunités, veille, knowledge/retrieval, préparation, pricing, soumission et corpus Golden DCE. Elles doivent être mesurées avant d’être reconstruites ou différées.

**Correction :** la matrice V8 → v3 doit couvrir tous les modules et objets, pas seulement les dix orientations du chapitre 15. Chaque ligne reçoit `KEEP`, `ADAPT`, `MOVE`, `CREATE`, `DEFER` ou `DELETE`, avec preuve dans le code et test associé.

## B05 — Phase 0 et PR-A0 se recouvrent

La Phase 0 prévoit l’environnement, les tests et la baseline. PR-A0 prévoit aussi la baseline et l’environnement. Sans frontière explicite, les mêmes travaux peuvent être refaits ou des modifications peuvent commencer pendant un audit annoncé comme préalable.

**Correction :**

- **Phase 0 :** lecture, exécution des commandes existantes, inventaire, mesures, matrice et rapport ; aucune refonte du cœur ;
- **Gate 0 :** approbation du diagnostic, de la traçabilité et du plan des PR ;
- **PR-A0 :** uniquement les corrections approuvées nécessaires pour rendre l’environnement reproductible ;
- **PR-A1 :** harness, manifeste et annotations Golden DCE autorisées ;
- **PR-A2 à A4 :** chaîne probatoire, après validation des deux premières PR.

## B06 — Le Gate A n’a pas de critères de sortie mesurables

Le plan indique la taille du corpus et les familles de bancs, mais ne fixe pas les résultats qui autorisent la suite. Le document v2.3 et les cahiers métier contiennent des critères plus précis qui n’ont pas été repris.

**Correction :** le Gate A doit au minimum démontrer :

1. tous les fichiers et membres d’archives du jeu Gate A sont inventoriés ;
2. tout fichier non lu reste visible et empêche un statut complet lorsqu’il peut porter une exigence critique ;
3. toute exigence C1 détectée ouvre la bonne pièce, la bonne version et le bon emplacement ;
4. le LLM ne fabrique aucune citation libre ; la citation est reconstruite côté serveur ;
5. validation et rejet humains sont persistants, nominatifs et audités ;
6. un rectificatif rouvre les preuves et conclusions réellement dépendantes ;
7. aucun accès inter-tenant n’est possible ;
8. un échec sur quelques fichiers laisse les résultats indépendants utilisables ;
9. les suites PostgreSQL et OCR pertinentes sont réellement exécutées ou explicitement bloquantes ;
10. toute régression critique est visible avant merge.

Les seuils de rappel et de précision seront calibrés après baseline. Sur les cas déclarés bloquants et annotés, une exigence C1 manquée ne peut pas être compensée par une moyenne globale.

## B07 — L’ordre B à I est présenté comme fixé trop tôt

Le cadrage initial précisait que l’ordre B à I devait être ajusté après l’audit réel. Cette réserve a disparu du plan final.

Or la priorité métier P0 couvre une offre complète : ingestion, analyse, risques, prix, décision, production, paquet final, preuve de remise et passation minimale. Une succession entièrement horizontale jusqu’à la Tranche I retarderait la première preuve de valeur de bout en bout.

**Correction :** conserver A comme fondation obligatoire, puis traiter B à I comme un backlog de capacités à ordonner au Gate A. Après A, chaque incrément devrait traverser le minimum de contextes nécessaire pour produire un résultat patron observable, plutôt que terminer un contexte entier avant de toucher le suivant.

---

# 5. Écarts à fermer avant pilote avec données réelles

## P01 — Sécurité, confidentialité et menace documentaire

Le chapitre 8 énumère des sujets « à spécifier et tester ». Cette formulation est correcte pour un plan de cadrage, mais insuffisante pour un cahier technique exécutable.

Le dossier de sécurité doit préciser :

- actifs, frontières de confiance et menaces ;
- authentification, sessions, MFA et délégations ;
- matrice des capacités par rôle, affaire, objet et sensibilité ;
- isolation dans les requêtes, recherches, index, exports, journaux et contextes LLM ;
- quarantaine, antivirus, bombes d’archives, chemins traversants, macros, formules, liens et contenus actifs ;
- egress réseau et ressources distantes interdites lors du traitement documentaire ;
- journalisation sans fuite de prix, marges, pièces privées ou secrets ;
- accès support exceptionnel, limité dans le temps et audité ;
- gestion, rotation et révocation des secrets ;
- réponse à incident et preuve de restauration.

V8 contient déjà des contrats et contrôles sur plusieurs de ces sujets. Phase 0 doit les classer `KEEP` ou `ADAPT` avant toute nouvelle solution.

## P02 — Cycle de vie des données et fin de contrat

Le CCF et le registre ADR exigent export, gel des nouveaux traitements, révocation des accès, suppression active, traitement annoncé des sauvegardes et preuve de clôture. Le plan final n’en donne pas encore l’architecture.

Un dossier `DATA-OPS-01` doit définir :

- catégories et propriétaires de données ;
- finalités, sensibilité, rétention et suppression ;
- emplacement de la base, des fichiers, index, journaux et sauvegardes ;
- format et portée de l’export client ;
- effacement des index, caches et artefacts dérivés ;
- calendrier de purge des sauvegardes ;
- données minimales conservées comme preuve légitime de clôture ;
- flux vers fournisseurs IA et autres sous-traitants ;
- données autorisées dans le Control Plane.

## P03 — Résidence et support depuis le Maroc

Le registre ADR demande explicitement de décrire comment l’accès support depuis le Maroc est empêché, autorisé, limité, tracé et encadré. Le plan final mentionne seulement un accès support exceptionnel.

Avant pilote, il faut une cartographie des flux France/EEE/hors EEE et une procédure d’accès support fondée sur l’architecture et les contrats réels. Aucun message commercial sur la résidence ne doit précéder cette preuve.

## P04 — Exploitation d’un parc d’instances dédiées

Le modèle dédié n’est viable que si les opérations sont reproductibles. Le plan doit transformer les quinze questions du registre ADR en preuves d’exploitation : provisioning, inventaire de version, migration, sauvegarde, restauration isolée, déploiement progressif, rollback, supervision, alerte, rotation des secrets, export et destruction.

Les choix d’outil peuvent rester ouverts. Les résultats attendus et les moments de décision doivent être fermés.

## P05 — Exigences non fonctionnelles

Le plan ne fixe pas encore les enveloppes qui influencent réellement l’architecture :

- taille et nombre de fichiers d’un DCE ;
- profondeur et volume maximal des archives ;
- formats garantis, partiels et refusés ;
- nombre d’affaires et utilisateurs actifs par PME ;
- concurrence sur un objet ;
- durée utile des analyses et comportement en reprise ;
- capacité de stockage et croissance des versions ;
- disponibilité, RPO et RTO ;
- budget de coût par instance et par analyse IA ;
- navigateurs, terminaux, zoom, clavier et lecteur d’écran ;
- connectivité dégradée sur le terrain.

Ces valeurs ne doivent pas être inventées. Phase 0 collecte les mesures existantes ; les pilotes fixent les premières enveloppes contractuelles.

## P06 — Gouvernance du Golden DCE

V8 contient déjà un manifeste Golden DCE et un validateur, mais l’exemple est volontairement vide et aucun DCE réel n’est stocké dans Git. C’est une bonne base, pas encore un corpus de qualification.

Le dossier Golden DCE doit préciser :

- droit d’utilisation, confidentialité et anonymisation de chaque dossier ;
- stockage hors Git des pièces réelles ;
- hash et version du manifeste ;
- schéma d’annotation par banc ;
- validateur métier de chaque vérité attendue ;
- gestion des désaccords entre experts ;
- séparation Development, Qualification gelée et Cas hostiles ;
- prévention des fuites entre jeu de développement et jeu de qualification ;
- métriques par criticité, format, corps d’état et type d’affaire ;
- version du parser, du modèle, du prompt et des règles pour chaque résultat.

Les sept dossiers identifiés dans l’univers documentaire constituent le point de départ naturel. Leur inclusion réelle dépend des droits et de l’anonymisation.

## P07 — Gouvernance des changements IA

Le plan décrit le harnais mais pas encore la procédure de changement. Avant pilote, chaque évolution de modèle, prompt, outil, règle ou parser doit :

1. recevoir une version ;
2. être évaluée sur les bancs concernés ;
3. produire un comparatif des régressions critiques ;
4. conserver les résultats historiques avec leur contexte ;
5. prévoir rollback ou désactivation ;
6. ne jamais réinterpréter silencieusement une décision historique validée.

## P08 — Gates UX et accessibilité

Le plan demande douze prototypes, mais ne définit pas leur sortie. Pour chaque écran : rôle cible, affaire réelle, action principale, état vide, état partiel, erreur, reprise, confidentialité, source, clavier, lecteur d’écran et décision d’acceptation doivent être enregistrés.

Les écrans concernés sont : Accueil Patron, Radar, fiche Opportunité, import DCE, explorateur DCE, synthèse Affaire, registre MIRP, GO/NO-GO, Prix, Réponse, Coffre et Passation.

---

# 6. Confrontation aux exigences métier P0

| Besoin métier P0 | Réponse du plan | Diagnostic |
|---|---|---|
| Inventaire, versions, rectificatifs | DCE & Document Intelligence, A puis B | direction correcte ; gate incomplet |
| Exigences, sources, contradictions | Evidence & Market Understanding, A puis B/E | fondation correcte ; propriétaire à clarifier |
| Candidature et preuves entreprise | Enterprise Memory, C/F | couvert en cible ; périmètre MVP à préciser |
| Analyse technique et couverture DPGF | Pricing, E/I | trop tardif si I signifie premier traitement réel |
| Risques, hypothèses, engagements | Evidence, Decision, Response, E/F | couvert ; transactions et responsabilités manquent |
| GO/NO-GO, marge, trésorerie, capacité | Decision, Pricing, E/I | actifs V8 à auditer ; incrément vertical nécessaire |
| Production contrôlée | Response, F | couvert en cible ; fidélité DOCX/XLSX non spécifiée |
| Manifeste, autorisation, remise | Submission, G | direction correcte ; preuve externe et modes d’échec à détailler |
| Rôles, confidentialité, audit | Identity, Collaboration, Platform | principes corrects ; matrice exécutable absente |
| Passation minimale | Handover, I | couverte mais trop tardive pour valider la promesse P0 |

La roadmap n’a pas besoin de construire tout P0 en profondeur dès le début. Elle doit néanmoins prévoir rapidement un **fil vertical pilotable** : un DCE versionné, une exigence critique sourcée, une décision humaine, une pièce de réponse contrôlée, un manifeste, une preuve de remise simulée et une passation minimale.

---

# 7. Context map minimale à produire en Phase 0

La table suivante ne remplace pas l’audit du code. Elle fixe les questions de propriété à résoudre.

| Objet | Propriétaire cible pressenti | Lecteurs principaux | Point à trancher |
|---|---|---|---|
| Opportunity | Opportunity / Radar | Case, AI Guidance | déduplication BOAMP/TED et conversion |
| Case | Case / Affair | tous les contextes d’affaire | porte courante ou projection des décisions |
| DceVersion, Document, Fragment | DCE & Document Intelligence | Evidence, Response, AI | version active et couverture de lecture |
| SourceAnchor | DCE ou Evidence | tous les consommateurs de preuve | propriétaire technique unique |
| Evidence | Evidence & Market Understanding | Decision, Pricing, Response, AI | distinction preuve DCE, entreprise et remise |
| Requirement | Evidence & Market Understanding | Case, Pricing, Response, Submission | compatibilité avec `DceRequirement` |
| Unknown, Hypothesis, Risk | Evidence ou Decision | Pricing, Response, Work | lieu d’écriture et invalidation |
| InformationRequirement / MIRP | Evidence ou Pricing | Work, Decision | besoin de prix vs exigence documentaire |
| Task, Question | Collaboration & Work | Case, Evidence, Response | preuve de fin et réponses externes |
| Commitment | Response & Artifacts | Pricing, Decision, Handover | autorité de validation et coût associé |
| Decision | Decision & Governance | Case, Submission, Handover | contexte figé et supersession |
| EnterpriseItem | Enterprise Memory | Evidence, Pricing, Response, AI | validité, sensibilité et portée d’usage |
| ResponseDocument | Response & Artifacts | Submission | original acheteur, dérivé et version candidate |
| SubmissionManifest | Submission | Decision, Handover | immutabilité après autorisation |
| Receipt | Submission | Handover | différence envoi, réception et acceptation |
| Share | Identity ou Collaboration | tous les contextes | révocation et copie déjà téléchargée |

Le principe à préserver est simple : **un propriétaire d’écriture, plusieurs lecteurs autorisés, aucune table critique partagée comme raccourci**.

---

# 8. Plan de travail recommandé

## Étape 1 — Stabiliser le corpus documentaire

1. conserver v3.0 comme référence directrice ;
2. changer son statut pour limiter l’autorisation à Phase 0 ;
3. classer v2.3 comme héritage applicable tant que ses critères n’ont pas été repris ;
4. archiver CCF v1.0 comme supersédé ;
5. enregistrer le corpus actif dans Git avec une carte documentaire et des hashes si nécessaire ;
6. retirer les fichiers de verrou bureautique du corpus livré.

Constat de cette revue : les nouveaux rapports apparaissent actuellement non suivis dans le checkout. Avant la reprise de code, le corpus normatif doit avoir un commit de référence afin que chaque PR puisse citer une version exacte.

## Étape 2 — Exécuter la Phase 0 en lecture et mesure

Livrables obligatoires :

1. `AUD-00` — état du checkout, commit de référence et périmètre audité ;
2. `AUD-01` — carte du dépôt, modules, interfaces publiques et dépendances ;
3. `AUD-02` — runtime, processus, workers, stockages et flux externes ;
4. `AUD-03` — PostgreSQL, modèles, migrations, contraintes et données à migrer ;
5. `AUD-04` — commandes de test réelles, suites exécutées, skips et blocages ;
6. `AUD-05` — flux DCE de l’entrée au `DceRequirement` et à la confirmation ;
7. `AUD-06` — état Decision, Pricing, Enterprise, Submission, PatronAction, Knowledge, Opportunity, MarketWatch, Membership, Preparation et Optimization ;
8. `MAP-01` — modules V8 vers contextes v3 ;
9. `MIG-01` — KEEP/ADAPT/MOVE/CREATE/DEFER/DELETE par objet et module ;
10. `TRC-01` — traçabilité métier/CCF/UX/ADR vers architecture, tranche et test ;
11. `QUAL-01` — baseline Golden DCE, corpus autorisé, bancs et métriques ;
12. `SEC-DATA-01` — écarts sécurité, confidentialité, données et exploitation ;
13. `PLAN-A` — plan détaillé PR-A0 à PR-A4, migrations, rollback et gates ;
14. `DEC-GATE` — décisions ouvertes avec propriétaire et date limite par gate.

## Étape 3 — Tenir le Gate 0

Le Gate 0 répond à cinq questions :

1. savons-nous exactement ce qui existe et ce qui fonctionne ?
2. chaque objet cible a-t-il un propriétaire et une trajectoire ?
3. chaque exigence critique a-t-elle une tranche et une preuve d’acceptation ?
4. les migrations A0–A4 sont-elles additives, réversibles et compatibles ?
5. le corpus et l’environnement permettent-ils de mesurer les régressions ?

Si une réponse est non, le gate produit une action bornée. Il ne déclenche pas une refonte générale.

## Étape 4 — Exécuter A0 puis A1

PR-A0 corrige seulement l’environnement reproductible approuvé. PR-A1 rend le Golden DCE Development exécutable avec des données autorisées et des annotations versionnées.

Ces deux PR donnent la baseline avant toute modification de la représentation probatoire.

## Étape 5 — Exécuter A2 à A4

- A2 introduit `SourceAnchor` au-dessus des locators existants ;
- A3 introduit `Evidence` sans confondre les preuves DCE, entreprise ou remise ;
- A4 relie `DceRequirement` aux preuves et fiabilise validation, rejet et invalidation.

Chaque PR doit être petite, additive et accompagnée du minimum de tests qui prouve le nouveau contrat.

## Étape 6 — Tenir le Gate A et recalculer la roadmap

Le Gate A compare les résultats à la baseline. Il décide ensuite quelle capacité apporte le prochain résultat métier démontrable : expérience source, tableau, FieldUnderstanding, MIRP, document de réponse, coffre, retrieval ou autre manque mesuré.

La décision ne doit pas être prise aujourd’hui à la place des données de Phase 0 et de Tranche A.

---

# 9. Décisions ouvertes et date limite recommandée

| Décision | Peut rester ouverte pendant Phase 0 | Doit être fermée avant |
|---|---:|---|
| Hébergeur, VPS/VM/PaaS | oui | pilote réel |
| Conteneurs et IaC | oui | deuxième instance reproductible |
| PostgreSQL managé ou non | oui | pilote réel et RPO/RTO |
| Stockage objet | oui | ingestion de données réelles |
| Recherche/vectoriel final | oui | adoption d’une nouvelle baseline retrieval |
| Fournisseur et région LLM | oui | premier traitement de données réelles |
| RPO, RTO, sauvegarde et restauration | mesure pendant Phase 0 | pilote réel |
| Secrets, support et accès Maroc | conception pendant Phase 0 | pilote réel |
| DPA, SCC et sous-traitants | oui | contrat pilote et données réelles |
| Control Plane | oui | exploitation de plusieurs instances |
| Quotas et tarification | oui | offre commerciale |
| Connecteurs ERP bidirectionnels | oui | besoin pilote prouvé |
| Dépôt automatisé | oui | recette par plateforme et décision responsabilité |
| Multi-tenant mutualisé | oui | segment et besoin économique démontrés |

Les DEC‑01 à DEC‑10 métier restent ouvertes tant que le propriétaire ne les a pas arbitrées. Le développement peut utiliser leurs orientations recommandées uniquement si la solution reste réversible et si l’hypothèse est visible dans `DEC-GATE`.

---

# 10. Preuves observées dans V8 pendant cette revue

La présente revue a effectué un contrôle limité du dépôt afin de vérifier les hypothèses du plan :

- 13 modules métier sont présents sous `backend/app/modules` ;
- 67 fichiers sont présents dans l’historique de migrations Alembic ;
- 234 fichiers `test_*.py` sont présents et l’environnement du dépôt collecte 1 624 tests ;
- un backend FastAPI/SQLAlchemy/PostgreSQL et un frontend React/Vite sont déclarés ;
- des tests d’architecture existent pour les frontières de domaine, d’application, d’infrastructure et de propriété des modèles ;
- **75 tests d’architecture ont été exécutés avec succès** via l’environnement `uv` du dépôt ;
- un contrat Golden DCE et un manifeste vide validable existent déjà sous `ops/golden-corpus` ;
- `DceRequirement`, les sources d’exigence et la confirmation humaine existent ;
- aucun contrat générique `SourceAnchor` ni objet probatoire générique `Evidence` n’a été identifié dans le cœur DCE ;
- des usages du mot evidence existent dans des sens locaux, notamment classification documentaire et preuve de soumission ; ils ne doivent pas être renommés ou fusionnés sans audit sémantique.

Le premier lancement direct de `pytest` a échoué à cause d’un environnement Python global incompatible. La commande du dépôt `uv run --extra calendar pytest ...` a ensuite exécuté correctement la suite. Ce résultat confirme l’intérêt de PR-A0 : les commandes autoritatives doivent être uniques et explicites.

---

# 11. Amendements minimaux au plan directeur

Le plan v3.0 n’a pas besoin d’être réécrit. Un amendement court suffit avant Phase 0 :

1. remplacer le statut par « référence directrice validée, autorisation Phase 0 uniquement » ;
2. ajouter `TRC-01` aux livrables du chapitre 21 ;
3. ajouter `MAP-01` avec propriétaire d’écriture et relations entre contextes ;
4. distinguer Phase 0, Gate 0, PR-A0 et PR-A1 ;
5. rendre l’ordre B–I provisoire jusqu’au Gate A ;
6. ajouter les critères mesurables du Gate A ;
7. classer les décisions ouvertes par date limite ;
8. ajouter les dossiers `SEC-DATA-01`, `QUAL-01` et NFR avant pilote ;
9. préciser que v2.3 reste applicable pour ses contrats et critères non encore repris ;
10. enregistrer le corpus normatif dans un commit de référence.

Ce sont les corrections minimales qui rendent le plan exécutable sans l’alourdir avec des choix techniques prématurés.

---

# 12. Verdict final

Le plan directeur v3.0 mérite d’être conservé. Sa direction est sérieuse, prudente et adaptée à SMART AO. Il protège le projet contre les deux erreurs les plus coûteuses : réécrire V8 et construire une architecture IA plus vite que la preuve métier.

Il faut maintenant éviter l’erreur inverse : appeler « architecture finale » un document qui ne relie pas encore chaque exigence à un propriétaire, une migration et un test.

La prochaine action correcte est donc :

> **figer le corpus documentaire, appliquer les dix amendements minimaux, puis lancer l’audit Phase 0 sans modification du cœur.**

À l’issue de cette Phase 0, le propriétaire reçoit un dossier de décision concret. C’est ce dossier, et non la seule qualité rédactionnelle du plan, qui autorisera PR-A0 à PR-A4.
