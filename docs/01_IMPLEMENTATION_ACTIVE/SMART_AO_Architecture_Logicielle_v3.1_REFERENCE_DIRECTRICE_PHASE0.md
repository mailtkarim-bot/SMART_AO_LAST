# SMART AO — Architecture logicielle et plan de construction

**Version : 3.1 — 12 septembre 2026**  
**Statut : RÉFÉRENCE DIRECTRICE VALIDÉE — AUTORISATION LIMITÉE À LA PHASE 0**  
**Portée : architecture de construction de SMART_AO V8, trajectoire vers l’architecture cible, règles de migration et gates de qualité.**

---

# 0. Objet du document

Ce document devient la **référence directrice de construction logicielle** de SMART AO.

Il ne remplace pas les référentiels métier et fonctionnels. Il les transforme en architecture de logiciel et en ordre de construction. Il doit permettre à Codex de travailler sans réinterpréter les besoins métier, sans réécrire V8 et sans anticiper des abstractions qui n’ont pas encore démontré leur utilité.

La règle de lecture est :

> **Le cahier propriétaire consolidé v0.4 dit ce qui doit être vrai.  
> Architecture v3.1 dit comment organiser le logiciel pour le rendre vrai.  
> Le code V8 dit ce qui existe réellement aujourd’hui et doit être audité avant modification.**

Le v0.4 se trouve dans `docs/00_REFERENCE_ACTIVE/`. Les anciens cahiers métier et CCF cités ci-dessous sont archivés : ils conservent le contexte de cette architecture, mais ne peuvent plus définir ou contredire le produit.

## 0.1 Autorisation opérationnelle

Le présent document valide la direction d’architecture, mais **n’autorise pas encore la transformation du cœur logiciel**.

Décision de gate :

- **GO** : audit et mesures de **Phase 0** ;
- **HOLD** : modification du cœur jusqu’à validation formelle du **Gate 0** ;
- **NO-GO** : pilote avec données client réelles tant que les gates sécurité, données, exploitation et qualité ne sont pas définies et démontrées.

La direction cible est donc stabilisée ; l’architecture de migration détaillée reste une **sortie de Phase 0**.


---

# 1. Corpus normatif et statut des documents

## 1.1 Ordre de référence

1. `docs/00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md` pour le produit et le métier ;
2. présent document `SMART_AO_Architecture_Logicielle_v3.1` pour l'architecture de construction ;
3. code réel `SMART_AO_V8` pour l'état observé ;
4. dossiers `phase0_gate0/` pour les constats, gates et la migration ;
5. documents de `docs/_ARCHIVE/` uniquement comme contexte historique, quand le v0.4 ou les références actives les désignent explicitement.

## 1.2 Documents supersédés ou hérités

### CCF-UX v1.0
**SUPERSEDÉ par CCF-UX v1.1.**

Il reste archivistique mais ne doit plus être donné à Codex comme source normative.

### Architecture métier et technique v2.3
**BASELINE TECHNIQUE HÉRITÉE, absorbée par v3.0.**

Elle reste une source majeure pour :
- la stratégie evidence-first ;
- l’absence de rewrite global ;
- la séparation architecture cible / architecture de construction ;
- SourceAnchor / Evidence / Requirement ;
- Golden DCE ;
- la conservation de Decision, DceRequirement, Pricing/CostBasis, Enterprise, Submission et PatronAction ;
- le benchmark-first pour retrieval/reranking ;
- les gates d’environnement et de non-régression.

En cas de conflit entre v2.3 et les décisions postérieures du CCF v1.1 / ADR préliminaires, **v3.0 tranche**.

À compter de ce document, v2.3 ne doit plus être utilisé seul comme mandat d’exécution.

Les contrats, invariants et critères de v2.3 qui ne sont pas encore repris explicitement dans v3.1 restent applicables comme exigences héritées jusqu’à leur absorption ou leur révocation documentée.

---

# 2. Principes architecturaux non négociables

1. **V8 est le socle de production à faire évoluer. Aucun rewrite global.**
2. **Architecture cible ≠ architecture de construction.**
3. **Modular monolith d’abord**, frontières de domaine strictes ; pas de microservices par anticipation.
4. **Single-tenant au déploiement, tenant-aware dans l’application.**
5. **Un code produit unique**, aucune branche permanente par client.
6. **Affaire = centre opérationnel du produit.**
7. **Mémoire Entreprise = source privée gouvernée des faits propres à l’entreprise.**
8. **Toute conclusion critique doit revenir à une preuve et à une version.**
9. **Toute donnée dérivée doit revenir à sa provenance.**
10. **Toute décision engageante doit revenir à une personne habilitée, un contexte et une version.**
11. **IA centrale dans l’accompagnement, jamais autorité finale.**
12. **AI-native, pas chat-first.**
13. **Conversation ≠ base de vérité.**
14. **Une donnée interdite à un rôle est interdite aussi au contexte du LLM de ce rôle.**
15. **Les fonctions critiques restent utilisables si le fournisseur IA est indisponible.**
16. **Les rectificatifs invalident explicitement les conclusions dépendantes.**
17. **Aucun score global ne masque un blocage critique, un fichier non lu ou une inconnue déterminante.**
18. **Word, Excel, PDF et logiciels de chiffrage sont des voisins à intégrer, pas des habitudes à combattre.**
19. **Chaque traitement long expose état, résultat partiel, échec et reprise.**
20. **Chaque nouvelle abstraction doit être justifiée par un cas réel, un test ou une métrique.**

---

# 3. Style d’architecture retenu

## 3.1 Modular monolith structuré par bounded contexts

SMART AO V8 évolue vers un **monolithe modulaire**.

Les bounded contexts sont des frontières de responsabilité, de modèle, de contrats et de dépendances. Ils ne sont pas automatiquement des services séparés.

Avantages recherchés :
- transactions et cohérence simples ;
- exploitation adaptée à un VPS dédié par client ;
- migration progressive du repo existant ;
- tests plus simples ;
- coûts d’exploitation limités ;
- possibilité d’extraire ultérieurement un contexte si un besoin mesuré l’exige.

## 3.2 Règles de dépendance

- Un contexte ne doit pas importer directement les détails internes d’un autre contexte.
- Les échanges passent par contrats applicatifs, événements métier ou interfaces explicitement exposées.
- La couche UI ne porte aucune règle métier critique.
- `Platform` fournit les capacités techniques mais ne contient aucune règle BTP.
- L’IA appelle des outils/contracts du domaine ; elle ne contourne jamais les services applicatifs.
- Les données de référence d’un contexte ont un propriétaire clair.
- Les duplications de lecture sont autorisées si elles évitent un couplage fort, à condition que la source autoritative soit connue.
- Aucun contexte ne peut modifier silencieusement une donnée autoritative d’un autre contexte.

---

# 4. Bounded contexts cibles

## 4.1 Identity & Access
Organisation/tenant, utilisateurs, rôles, délégations, sessions, MFA, permissions, partage externe ciblé et accès support exceptionnel.

## 4.2 Opportunity / Radar
BOAMP prioritaire, TED ensuite, recherche, filtres, recherches sauvegardées, alertes, provenance, fraîcheur, déduplication, pertinence expliquée, suivi/écart et conversion en Affaire.

## 4.3 Case / Affair
Affaire, lot/périmètre, phase, responsables, échéances, progression P0–P7, liens vers versions DCE et synthèse opérationnelle.

## 4.4 DCE & Document Intelligence
Ingestion, conservation des originaux, archives, versioning, extraction, fragments, locators, classification, couverture de lecture, rectificatifs et comparaison.

## 4.5 Evidence & Market Understanding
SourceAnchor, Evidence, Requirement, InformationRequirement/MIRP, Unknown, Hypothesis, contradiction, applicability, RiskSignal, CostFactor et claims critiques lorsque cette couche sera activée.

## 4.6 Enterprise Memory
Identité, pouvoirs, assurances, qualifications, personnes, matériel, références, méthodes/QSE, partenaires, produits, modèles, prix/achats, finance/trésorerie, règles internes et REX.

Chaque élément porte au minimum : provenance, titulaire/périmètre, validité ou date de revue, sensibilité, validation, droits, historique et conditions de réemploi.

## 4.7 Decision & Governance
Portes P0–P7, décisions nominatives, conditions, dérogations, contextes figés, invalidation après changement, historique/supersession. Le noyau Decision existant est conservé et enrichi.

## 4.8 Pricing Intelligence
Facteurs de coût, couverture du besoin, hypothèses économiques, import/export chiffrage, contrôles DPGF/BPU/DQE et scénarios. SMART AO ne fixe pas seul le prix final.

## 4.9 Response & Artifacts
Candidature, mémoire, cadres acheteur, documents à générer/remplir/obtenir, modèles, engagements, versions, revues et exports contrôlés.

## 4.10 Submission
Manifest, version candidate, contrôles, signataire, canal, empreintes, autorisation P5, reçu et rapprochement.

## 4.11 Collaboration & Work
Tâches, commentaires, responsable principal, contributeurs, valideur, conflits, délégation/remplacement, notifications, reprise et partage externe ciblé.

## 4.12 Handover & Learning
Contrat réellement accepté, engagements vendus, réserves, hypothèses, passation, résultat et REX minimal sans devenir un ERP chantier.

## 4.13 AI Runtime / Guidance
Provider port, context builder, policy gate, permission gate, tool registry, prompt/skill registry, structured outputs, citations, abstention, budget de contexte, coût/usage IA et télémétrie.

## 4.14 Platform
Persistence, PostgreSQL, migrations, object storage, events/outbox, idempotence, optimistic concurrency, jobs asynchrones, observability, audit technique, secrets/configuration et sauvegardes.

---

# 5. Architecture de données

## 5.1 Déploiement client
Chaque client possède un Data Plane dédié : application, PostgreSQL, stockage documentaire, index/recherche, secrets, journaux nécessaires, sauvegardes et workers. L’organisation/tenant reste présente dans le domaine.

## 5.2 Base relationnelle
- une base PostgreSQL par environnement client ;
- migrations uniques et versionnées ;
- ownership logique par bounded context ;
- pas de séparation physique prématurée par contexte ;
- JSONB réservé aux extensions contrôlées, métadonnées variables et snapshots.

## 5.3 Fichiers
Les originaux restent des objets source versionnés avec hash, provenance, type, taille, droits et état de lecture.

## 5.4 Recherche / vectoriel
Le moteur V8 actuel sert de baseline s’il est effectivement présent et qualifié.

Ordre d’évaluation : exact/structurel → baseline vectorielle → lexical → hybride → RRF/reranking seulement si gain démontré. GraphRAG n’est pas une dépendance du cœur.

---

# 6. Architecture probatoire

## 6.1 SourceAnchor
Pointeur stable vers la source :
- PDF : page + bounding box/span ;
- DOCX : paragraphe/table/cellule + ordre ;
- XLSX : feuille + cellule/plage ;
- texte : lignes/spans ;
- graphique plus tard : page/image + bounding box.

## 6.2 Evidence
Objet de preuve réutilisable distinct de SourceAnchor. Il porte version documentaire, document, anchor, valeur/extrait observé, type, méthode d’extraction, confiance technique, hash source, parser/version et état de validation si nécessaire.

## 6.3 Requirement
`DceRequirement` n’est pas supprimé dans la première migration. Il évolue pour référencer des Evidence, conserver la compatibilité, exposer criticité/portée/phase/applicabilité, recevoir validation/rejet et être invalidé lorsque sa preuve active change.

## 6.4 InformationRequirement / MIRP
Un besoin d’information pour décider/chiffrer est distinct d’un document à remettre. Relation many-to-many entre besoins et documents/preuves.

---

# 7. Architecture IA et harnais SMART AO

## 7.1 Doctrine
Chaque appel LLM est construit par le harnais avec : identité, rôle, permissions, tenant, Affaire/lot, version DCE, phase/porte, objectif, faits prouvés, inconnus/contradictions, données Entreprise autorisées, outils autorisés, actions interdites, budget, format de sortie et politique d’abstention.

## 7.2 Classes de sortie
Extraction, rapprochement, inférence, recommandation, brouillon, action préparée.

## 7.3 Provider
Un provider réel peut suffire au lancement, derrière un `AIProviderPort`, avec mesure token/coût/latence.

## 7.4 Outils
Le LLM utilise des tools bornés. Il ne modifie pas directement les tables critiques.

## 7.5 Prompt injection documentaire
Tout document externe est data, jamais instruction système. Aucun texte du DCE ne peut élargir permissions, outils ou accès à la Mémoire Entreprise.

---

# 8. Sécurité et confidentialité

L’instance dédiée n’est jamais une mesure de sécurité suffisante seule.

À spécifier et tester : secrets par environnement, moindre privilège, MFA sensible, chiffrement transit/repos selon risque, journaux d’accès, audit métier, patching, supervision, sauvegardes, restauration, rotation/révocation des secrets, séparation dev/test/prod et procédure incident.

Une donnée Direction-only n’apparaît pas à l’écran, dans la recherche, l’export ou le contexte LLM d’un collaborateur.

L’accès support au contenu est exceptionnel, nominatif, limité, journalisé, temporel et contractuellement encadré.

---

# 9. Control Plane / Data Plane

## Data Plane client
DCE, documents, Enterprise Memory, prix/marges, décisions, index, utilisateurs métier, preuves, artefacts et manifestes.

## Control Plane commun — différé mais prévu
Licence, version, santé, état migrations, sauvegardes, consommation/coût, déploiement et métadonnées techniques minimales.

Interdit par défaut : DCE complets, marges, prix, documents bancaires, contenu Mémoire Entreprise et décisions métier détaillées.

---

# 10. Architecture frontend et UX

Navigation principale : Accueil, Opportunités, Affaires, Entreprise, Administration.

Dans l’Affaire : Synthèse, Analyse, Réponse, Décision, Remise.

Principes : divulgation progressive, source à un clic, action principale claire, états explicites, pas de confiance décorative, tableaux denses pour experts, synthèses pour patron, assistant contextuel, accessibilité WCAG 2.2 AA cible et aucune fonction critique dépendante du chat.

Les prototypes UX progressent en parallèle de Tranche A. Les tranches B+ ne figent pas une interface majeure sans validation des parcours critiques.

---

# 11. Intégrations externes

## BOAMP
Adapter derrière un contrat `OpportunitySource`. Le domaine attend source, identifiant externe, publication, fraîcheur, objet, acheteur, dates, type/nature, localisation, lots si disponibles et lien source.

La version précise de l’API, pagination, retry, cache et allowlist sont décidés pendant la tranche Radar.

## TED
Deuxième `OpportunitySource` public sur le même contrat interne lorsque possible.

## ERP/chiffrage
Imports/exports et contrats simples d’abord. Connecteurs bidirectionnels plus tard.

## Email / plateformes
Aucune automatisation de dépôt ou d’envoi engageant sans gate humaine explicite dans la première version.

---

# 12. Asynchronisme, événements et reprise

Traitements longs : ingestion, OCR, extraction, analyse, rectificatif, indexation, génération, import entreprise et Radar.

Chaque traitement long possède job id, état, progression utile, résultat partiel, erreurs isolées, retry contrôlé, idempotence et reprise.

Les workers existants sont refactorés progressivement, pas remplacés en big-bang.

---

# 13. Observabilité

Trois plans séparés :

**Technique** : erreurs, latence, jobs, DB, stockage, disponibilité, sauvegardes.  
**Produit/métier** : fichiers lus/non lus, exigences, faux négatifs critiques, citations, rectificatifs, validations, manifeste, remise.  
**IA/coût** : modèle/version, capacité, tokens/équivalent, coût, latence, tool failures, abstentions, corrections et consommation par client.

---

# 14. Golden DCE et qualité

Golden DCE Development démarre avec environ 5–8 DCE réels diversifiés et 50–100 cas/questions critiques.

Bancs séparés : structure, tableaux, requirements, retrieval, risk/cost, claim fidelity.

Une moyenne élevée ne compense jamais une visite obligatoire manquée, une pièce éliminatoire oubliée, une date fausse, un mauvais lot, une source remplacée ou une fuite de donnée Direction.

Jeux séparés : Development, Qualification gelée, Cas hostiles.

---

# 15. Migration depuis V8

Chaque module/objet reçoit : `KEEP`, `ADAPT`, `MOVE`, `CREATE`, `DEFER` ou `DELETE`.

`DELETE` exige absence d’usage réel ou parité fonctionnelle démontrée.

Orientations à confirmer par audit :
- Decision : KEEP + EXTEND
- DceRequirement : KEEP + ADAPT
- extraction/fragments/locators : KEEP
- enterprise : KEEP + EVOLVE
- pricing/CostBasis : KEEP + REPOSITION
- patron_action : KEEP
- submission : KEEP + ALIGN
- preparation : KEEP + REFACTOR later
- knowledge : KEEP + MEASURE
- bootstrap/runtime : découplage progressif

---

# 16. Roadmap de construction v3.1

## 16.1 Phase 0 — Audit en lecture, exécution et mesure

La Phase 0 n’est pas une PR de refonte. Elle consiste à **observer, exécuter les commandes autoritatives, mesurer, cartographier et décider**.

Livrables obligatoires :

1. `AUD-00` — état du checkout, commit de référence et périmètre audité ;
2. `AUD-01` — carte du dépôt, modules, interfaces publiques et dépendances ;
3. `AUD-02` — runtime, processus, workers, stockages et flux externes ;
4. `AUD-03` — PostgreSQL, modèles, migrations, contraintes et données à migrer ;
5. `AUD-04` — commandes de test réelles, suites exécutées, skips et blocages ;
6. `AUD-05` — flux DCE de l’entrée au `DceRequirement` et à la confirmation humaine ;
7. `AUD-06` — état Decision, Pricing, Enterprise, Submission, PatronAction, Knowledge, Opportunity, MarketWatch, Membership, Preparation et Optimization ;
8. `MAP-01` — carte des modules V8 vers contextes v3, avec **propriétaire d’écriture unique**, lecteurs et relations ;
9. `MIG-01` — `KEEP / ADAPT / MOVE / CREATE / DEFER / DELETE` par objet et module, avec preuve dans le code ;
10. `TRC-01` — matrice de traçabilité métier / documentaire / CCF / UX / ADR vers objet propriétaire, contexte, module V8, commande/événement, tranche, PR et test ;
11. `QUAL-01` — baseline Golden DCE, corpus autorisé, bancs, gouvernance et métriques ;
12. `SEC-DATA-01` — écarts sécurité, confidentialité, données, flux, exploitation et support ;
13. `PLAN-A` — plan détaillé PR-A0 à PR-A4, migrations, rollback et gates ;
14. `DEC-GATE` — décisions ouvertes, propriétaire et date limite par gate.

### TRC-01 — structure minimale

| Champ | Contenu |
|---|---|
| Référence | document, section, REC/UX/VAL/ADR |
| Exigence observable | ce qui doit être vrai |
| Objet propriétaire | source autoritative |
| Contexte cible | responsabilité |
| Module V8 actuel | propriétaire/lecteur actuel |
| Commande/événement | effet et frontière transactionnelle |
| Tranche / PR | moment de traitement |
| Test / preuve | résultat reproductible attendu |
| Statut | couvert / partiel / absent / différé / bloqué |

### MAP-01 — règle de propriété

Chaque objet critique du CCF reçoit :

- **un propriétaire d’écriture unique** ;
- zéro ou plusieurs lecteurs autorisés ;
- une frontière de transaction explicite ;
- une règle d’invalidation ;
- une trajectoire depuis V8.

Les projections de lecture peuvent être dupliquées ; la source autoritative doit toujours être nommée.

## 16.2 Gate 0 — Autorisation de modifier le cœur

Le Gate 0 répond obligatoirement à cinq questions :

1. savons-nous exactement ce qui existe et ce qui fonctionne ?
2. chaque objet cible a-t-il un propriétaire et une trajectoire ?
3. chaque exigence critique a-t-elle une tranche et une preuve d’acceptation ?
4. les migrations A0–A4 proposées sont-elles additives, réversibles et compatibles ?
5. le corpus et l’environnement permettent-ils de mesurer les régressions ?

Si une réponse est négative, le Gate 0 produit une action bornée. Il ne déclenche pas de refonte générale.

**Aucune PR-A0 à PR-A4 n’est autorisée avant validation du Gate 0.**

## 16.3 PR-A0 — Environnement reproductible approuvé

PR-A0 ne répète pas la Phase 0. Elle applique uniquement les corrections **approuvées au Gate 0** nécessaires pour rendre l’environnement reproductible :

- commandes autoritatives ;
- PostgreSQL réel ;
- OCR réellement requis ;
- dépendances ;
- suites qui doivent s’exécuter ;
- classification des skips/non-started ;
- état migrations ;
- documentation de bootstrap.

## 16.4 PR-A1 — Golden DCE Development exécutable

PR-A1 porte uniquement :

- manifeste ;
- harness/runner ;
- schéma d’annotations ;
- stockage autorisé hors Git des pièces réelles si nécessaire ;
- hashes/versions ;
- premiers cas critiques ;
- séparation Development / Qualification / Hostile ;
- baseline mesurée.

## 16.5 Tranche A — Fondation probatoire

Après A0 et A1 :

### PR-A2 — SourceAnchor
Contrat générique au-dessus des locators/fragments existants ; aucune substitution destructive.

### PR-A3 — Evidence
Objet probatoire distinct, source-bound, versionné, avec reconstruction serveur des citations.

### PR-A4 — DceRequirement + validation
Liaison Evidence, validation/rejet humain, audit, rectificatif/invalidation et non-régression.

Interdictions A0–A4 :

- nouvel Agent Orchestrator général ;
- HTML obligatoire au cœur ;
- nouvelle stack retrieval généralisée sans benchmark ;
- reranker sans preuve de gain ;
- GraphRAG ;
- Artifact Registry général ;
- vision/plans ;
- nouveau Decision engine ;
- multiplication des providers ;
- microservices ;
- migration DB destructive sans gate dédié.

## 16.6 Gate A — critères mesurables de sortie

Le Gate A doit démontrer au minimum :

1. tous les fichiers et membres d’archives du jeu Gate A sont inventoriés ;
2. tout fichier non lu reste visible et empêche un statut « complet » s’il peut porter une exigence critique ;
3. toute exigence C1 détectée ouvre la **bonne pièce, bonne version et bon emplacement** ;
4. aucune citation critique n’est fabriquée librement par le LLM : elle est reconstruite côté serveur ;
5. validation et rejet humains sont persistants, nominatifs et audités ;
6. un rectificatif rouvre les preuves et conclusions réellement dépendantes ;
7. aucun accès inter-tenant n’est possible ;
8. un échec sur quelques fichiers laisse les résultats indépendants utilisables ;
9. les suites PostgreSQL/OCR pertinentes s’exécutent réellement ou sont classées bloquantes ;
10. toute régression critique est visible avant merge.

Les seuils de rappel/précision sont calibrés après baseline. **Une C1 manquée ne peut jamais être compensée par une moyenne globale.**

## 16.7 Backlog B–I — ordre provisoire

Les capacités suivantes restent dans la cible, mais **leur ordre n’est pas figé avant le Gate A** :

- expérience Affaire / source ;
- Mémoire Entreprise ;
- Radar BOAMP/TED ;
- MIRP / risques / décisions ;
- réponse documentaire / engagements ;
- Coffre / manifeste / reçu ;
- guidance IA ;
- pricing avancé / partenaires / privé / passation.

Après Gate A, la roadmap doit privilégier des **incréments verticaux pilotables** produisant un résultat Patron observable plutôt qu’une succession horizontale de contextes terminés isolément.

Premier fil vertical à viser rapidement après A :

```text
DCE versionné
→ exigence critique sourcée
→ décision humaine
→ pièce de réponse contrôlée
→ manifeste
→ preuve de remise simulée
→ passation minimale
```

---

# 17. Dossiers obligatoires avant pilote réel

Ces dossiers peuvent être préparés pendant Phase 0, mais doivent être fermés avant tout pilote avec données client réelles.

## 17.1 SEC-OPS-01 — Sécurité et menace documentaire

Doit couvrir :

- actifs et frontières de confiance ;
- authentification, sessions, MFA, délégations ;
- matrice de capacités par rôle/affaire/objet/sensibilité ;
- isolation dans requêtes, recherche, index, exports, journaux et contexte LLM ;
- quarantaine et traitement des fichiers ;
- antivirus/antimalware si retenu ;
- bombes d’archives, zip slip/path traversal ;
- macros, formules, liens et contenu actif ;
- egress réseau et ressources distantes ;
- logs sans fuite de secrets/prix/marges ;
- accès support exceptionnel ;
- secrets, rotation/révocation ;
- incident response ;
- preuve de restauration.

Les mécanismes V8 existants sont audités avant création de nouveaux contrôles.

## 17.2 DATA-OPS-01 — Cycle de vie et réversibilité

Doit définir :

- catégories et propriétaires de données ;
- finalité, sensibilité, rétention, suppression ;
- localisation DB/fichiers/index/logs/backups ;
- export client ;
- purge des dérivés/index/caches ;
- purge des sauvegardes ;
- preuve minimale de clôture ;
- flux vers IA/sous-traitants ;
- données autorisées dans le Control Plane.

## 17.3 DATA-FLOW-01 — France/EEE / Maroc / fournisseurs

Cartographie des flux et procédure d’accès support :

- empêché par défaut ;
- autorisé explicitement ;
- durée limitée ;
- périmètre limité ;
- MFA ;
- journalisation ;
- justification ;
- révocation ;
- encadrement contractuel.

## 17.4 OPS-DEDICATED-01 — Parc d’instances dédiées

Preuves attendues :

- provisioning ;
- inventaire versions ;
- migrations ;
- sauvegarde ;
- restauration isolée ;
- déploiement progressif ;
- rollback ;
- supervision ;
- alertes ;
- rotation secrets ;
- export ;
- destruction.

Les outils restent ouverts ; les résultats sont obligatoires.

## 17.5 NFR-01 — Enveloppes non fonctionnelles

Phase 0 mesure ; les pilotes permettent de fixer :

- tailles/nombres de fichiers ;
- profondeur/volume archives ;
- formats garantis/partiels/refusés ;
- affaires/utilisateurs actifs ;
- concurrence sur objet ;
- durée et reprise des analyses ;
- stockage/croissance versions ;
- disponibilité ;
- RPO/RTO ;
- budget infrastructure/IA ;
- navigateurs/terminaux ;
- clavier/lecteur d’écran ;
- connectivité dégradée.

Aucune valeur n’est inventée avant mesure.

## 17.6 QUAL-01 — Gouvernance Golden DCE

Obligatoire :

- droits d’usage ;
- anonymisation ;
- stockage hors Git des DCE réels ;
- hash/manifeste ;
- schéma annotations ;
- validateur métier ;
- désaccords experts ;
- séparation Development / Qualification / Hostile ;
- prévention des fuites de jeu ;
- métriques par criticité/format/métier/type ;
- versions parser/modèle/prompt/règles.

## 17.7 AI-CHANGE-01 — Gouvernance des changements IA

Toute évolution de modèle, prompt, outil, parser ou règle :

1. reçoit une version ;
2. passe les bancs concernés ;
3. produit un diff de régressions critiques ;
4. conserve son contexte historique ;
5. possède rollback/désactivation ;
6. ne réinterprète jamais silencieusement une décision historique validée.

## 17.8 UX-GATE-01 — Prototypes et accessibilité

Pour chacun des 12 écrans :

- rôle cible ;
- scénario réel ;
- action principale ;
- vide ;
- partiel ;
- erreur ;
- reprise ;
- confidentialité ;
- accès source ;
- clavier ;
- lecteur d’écran ;
- décision d’acceptation.

---

# 18. Décisions ouvertes et date limite de fermeture

| Décision | Peut rester ouverte en Phase 0 | Fermeture au plus tard |
|---|---:|---|
| Hébergeur / VPS / VM / PaaS | oui | pilote réel |
| Conteneurs / IaC | oui | deuxième instance reproductible |
| PostgreSQL managé ou non | oui | pilote réel + RPO/RTO |
| Stockage objet | oui | ingestion données réelles |
| Retrieval/vectoriel final | oui | adoption nouvelle baseline |
| Fournisseur/région LLM | oui | premier traitement de données réelles |
| RPO/RTO/backups | mesure | pilote réel |
| Secrets/support/accès Maroc | conception | pilote réel |
| DPA/SCC/sous-traitants | oui | contrat pilote |
| Control Plane | oui | plusieurs instances |
| Quotas/tarification | oui | offre commerciale |
| ERP bidirectionnel | oui | besoin pilote prouvé |
| Dépôt automatisé | oui | recette plateforme + responsabilité |
| Multi-tenant mutualisé | oui | besoin économique démontré |

DEC-01 à DEC-10 restent des hypothèses de travail réversibles et doivent apparaître dans `DEC-GATE`. DEC-11 reste une contrainte de construction active.

---

# 19. Prototypes UX et développement

Le prototypage peut progresser pendant Phase 0 et A0/A1.

Il ne bloque pas la fondation probatoire mais peut modifier les contrats applicatifs des incréments post-A.

Aucune interface majeure B+ n’est figée sans :

- scénario réel ;
- rôle ;
- erreurs/reprise ;
- confidentialité ;
- accessibilité ;
- source/preuve ;
- acceptation enregistrée.

---

# 20. Definition of Done de la référence directrice

La **direction architecturale** est définie lorsque le corpus, les principes, les contextes, le déploiement, la preuve, le harnais IA, la stratégie de migration et les gates sont documentés.

**Cette condition est remplie.**

En revanche, l’autorisation de transformation du cœur n’est **pas** incluse dans cette Definition of Done.

Elle nécessite :

- sortie complète de Phase 0 ;
- TRC-01 ;
- MAP-01 ;
- MIG-01 ;
- QUAL-01 ;
- SEC-DATA-01 ;
- PLAN-A ;
- validation Gate 0.

---

# 21. Mandat immédiat pour Codex — Phase 0 uniquement

## 21.1 Mission

> **Auditer le repo SMART_AO V8 actuel contre Architecture v3.1, sans modification du cœur, puis remettre le dossier de Gate 0.**

## 21.2 Livrables

Codex remet exactement :

- `AUD-00`
- `AUD-01`
- `AUD-02`
- `AUD-03`
- `AUD-04`
- `AUD-05`
- `AUD-06`
- `MAP-01`
- `MIG-01`
- `TRC-01`
- `QUAL-01`
- `SEC-DATA-01`
- `PLAN-A`
- `DEC-GATE`

## 21.3 Autorisé

- lire ;
- rechercher ;
- exécuter les commandes documentées du repo ;
- exécuter tests ;
- inspecter schémas/migrations ;
- mesurer ;
- comparer ;
- produire rapports ;
- proposer patchs/PR sans les appliquer au cœur.

## 21.4 Interdit pendant Phase 0

- rewrite ;
- changement structurel du cœur ;
- migration destructive ;
- renommage massif ;
- nouvel Agent Orchestrator ;
- nouvelle stack retrieval ;
- GraphRAG ;
- microservices ;
- nouveau provider ;
- chantier frontend général ;
- suppression de composants ;
- PR-A2/A3/A4 ;
- modification métier non nécessaire à une mesure explicitement autorisée.

## 21.5 Gate

Codex **s’arrête** après le dossier Phase 0.

Aucune transformation du cœur ne commence avant décision explicite du propriétaire au Gate 0.

---

# 22. Doctrine finale

> **Ne supprime pas le produit actuel. Change progressivement son centre de gravité.**

```text
OPPORTUNITÉ
    ↓
AFFAIRE
    ↓
DCE VERSIONNÉ
    ↓
SOURCEANCHOR
    ↓
EVIDENCE
    ↓
EXIGENCE / INFORMATION NÉCESSAIRE / RISQUE
    ↓
MÉMOIRE ENTREPRISE
    ↓
ACTION / RÉPONSE / PRIX
    ↓
DÉCISION HUMAINE
    ↓
MANIFESTE / REMISE
    ↓
CONTRAT VENDU / PASSATION
```

Transversalement :

```text
IDENTITÉ + DROITS + PREUVES + OUTILS + POLITIQUES
                       ↓
                HARNAIS SMART AO
                       ↓
                      LLM
                       ↓
     EXTRAIRE / EXPLIQUER / PROPOSER / PRÉPARER
                       ↓
          L’HUMAIN VALIDE ET ENGAGE
```

SMART AO doit pouvoir devenir très intelligent sans que sa fiabilité repose sur la confiance dans un modèle. La preuve, les droits, les versions, l’autorité humaine et la reprise sont le squelette ; l’IA est l’intelligence qui travaille à l’intérieur de ce squelette.
