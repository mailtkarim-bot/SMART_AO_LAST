# SMART AO — Architecture logicielle et plan de construction

**Version : 3.0 — 12 septembre 2026**  
**Statut : PLAN DIRECTEUR FINAL POUR DÉMARRAGE DE L’ARCHITECTURE ET DE LA REPRISE CODEX**  
**Portée : architecture de construction de SMART_AO V8, trajectoire vers l’architecture cible, règles de migration et gates de qualité.**

---

# 0. Objet du document

Ce document devient la **référence directrice de construction logicielle** de SMART AO.

Il ne remplace pas les référentiels métier et fonctionnels. Il les transforme en architecture de logiciel et en ordre de construction. Il doit permettre à Codex de travailler sans réinterpréter les besoins métier, sans réécrire V8 et sans anticiper des abstractions qui n’ont pas encore démontré leur utilité.

La règle de lecture est :

> **Métier et CCF disent ce qui doit être vrai.  
> Architecture v3.0 dit comment organiser le logiciel pour le rendre vrai.  
> Le code V8 dit ce qui existe réellement aujourd’hui et doit être audité avant modification.**

---

# 1. Corpus normatif et statut des documents

## 1.1 Ordre de référence

1. `SMART_AO_Cahier_des_charges_Metier_v1.0`
2. `SMART_AO_Univers_documentaire_metier_v1.0`
3. `SMART_AO_CCF_UX_Product_Blueprint_v1.1`
4. `SMART_AO_Registre_Decisions_Architecture_Preliminaires_v0.1`
5. `SMART_AO_Benchmark_Concurrentiel_UX_Parcours_v1.0`
6. présent document `SMART_AO_Architecture_Logicielle_v3.0`
7. code réel `SMART_AO_V8`

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

# 16. Roadmap de construction v3.0

## Phase 0 — Audit / baseline / environnement
Livrables : architecture réelle du repo, dépendances, migrations, tests, flux DCE, matrice V8→bounded contexts, KEEP/ADAPT/MOVE/CREATE/DEFER/DELETE, dettes bloquantes, baseline Golden DCE et plan PR Tranche A.

**Gate : aucune refonte cœur avant approbation de l’audit.**

## Tranche A — Fondation probatoire
`Document/Fragment -> SourceAnchor -> Evidence -> DceRequirement -> validation humaine`

Construire : environnement tests, Golden DCE, SourceAnchor, Evidence, adaptation DceRequirement, validation/rejet humain, invalidation rectificatif, reconstruction citation serveur et tests tenant/version/provenance.

Ne pas construire : nouvel Agent Orchestrator, HTML obligatoire, nouvelle stack retrieval générale, reranker, GraphRAG, Artifact Registry général, vision/plans, nouveau Decision engine, multiples providers.

**STOP GATE A obligatoire.**

## Tranche B — Affaire / couverture DCE / expérience source
Synthèse Affaire, couverture réception, fichiers lus/non lus, version active, exigences critiques, accès source, inconnus, rectificatif simple et reprise partielle.

## Tranche C — Mémoire Entreprise minimale
Import, classification proposée, provenance, titulaire, validité, sensibilité, validation, expiration, rôles, Direction-only et réutilisation contrôlée.

## Tranche D — Radar Opportunités
BOAMP d’abord : recherche, filtres, veille, fraîcheur, provenance, explication du match, suivi/écart et conversion Affaire. TED ensuite.

## Tranche E — MIRP / risques / décision P0–P3
InformationRequirements, MIRP, Unknown/Hypothesis, risques, facteurs coût, tâches/questions, décisions P0–P3 et GO sous conditions.

## Tranche F — Réponse documentaire / engagements
DocumentRequirement, documents externes, modèles acheteur, brouillons, mémoire, références, engagements, validation et version de réponse.

## Tranche G — Coffre / manifeste / remise
Manifest, version candidate, contrôles, P4/P5, signataire, canaux, empreintes, reçu et rapprochement.

## Tranche H — Guidance IA avancée
Briefing, guidance contextuelle, panneau SMART AO, tools bornés, Evidence Packs, recommandations, brouillons, actions préparées, coût client, correction portée et traçabilité des changements de modèle/règle.

## Tranche I — Économie, partenaires, privé et passation
Pricing readiness avancé, fournisseurs/sous-traitants, capacité, trésorerie, contrat privé, négociation, P6/P7, passation et REX.

---

# 17. Ordre des PR pour la Tranche A

## PR-A0 — Baseline et environnement
Commandes, PostgreSQL réel, OCR requis, skipped/non-started, migrations, rapport baseline.

## PR-A1 — Golden DCE Development
Format annotations, 5–8 DCE, cas critiques, runner, rapport baseline.

## PR-A2 — SourceAnchor
Contrat, locators par format, adaptateurs depuis fragments V8, tests reconstruction.

## PR-A3 — Evidence
Modèle distinct, persistence, lien SourceAnchor/version, server citation reconstruction, tests isolation.

## PR-A4 — DceRequirement + validation
Liaison Evidence, aucune migration destructive, validation/rejet, audit, rectificatif/invalidation, tests non-régression.

## Gate A
Codex s’arrête et remet rapport, métriques, changements schéma, régressions, dette nouvelle et proposition pour B.

---

# 18. Prototypes UX et développement

Le prototypage des 12 écrans prioritaires se fait en parallèle de Phase 0/Tranche A.

Avant une tranche B+ : prototype basse fidélité, scénario réel, rôle cible, comportement IA si pertinent, erreurs/reprise, confidentialité et accessibilité de base.

---

# 19. Décisions encore ouvertes

À ne pas figer irréversiblement : fournisseur VPS/cloud, VPS/VM/PaaS, conteneurs, IaC, reverse proxy/WAF, PostgreSQL managé ou non, stockage objet, moteur recherche/vectoriel final, RPO/RTO, outil secrets, fournisseur LLM/région, projets/keys LLM, Control Plane réel, stratégie support, DPA/SCC, quotas commerciaux, connecteurs ERP, dépôt automatisé futur et multi-tenant éventuel.

DEC-01 à DEC-10 restent réversibles selon le CCF. DEC-11 est une contrainte de construction actuelle.

---

# 20. Definition of Done du plan

Le plan est prêt lorsque : corpus normatif ordonné, CCF v1.0 archivé, v1.1 actif, v2.3 reclassé baseline, bounded contexts définis, règles de dépendance définies, single-tenant/tenant-aware défini, provenance définie, harnais IA défini, sécurité définie, Golden DCE défini, migration définie, phases/gates définies et mandat Phase 0/A défini.

**Ces conditions sont remplies par le présent document.**

---

# 21. Mandat immédiat pour Codex

Codex ne doit pas encore « construire SmartAO v3 ».

Sa première mission est :

> **Auditer le repo SMART_AO V8 actuel contre Architecture v3.0, puis proposer la matrice de migration et le plan détaillé PR-A0 à PR-A4 sans modifier le cœur métier avant revue.**

Livrables :
1. carte repo/modules ;
2. architecture runtime actuelle ;
3. DB/migrations ;
4. tests/environnement ;
5. flux DCE actuel ;
6. état SourceAnchor/Evidence/Requirement ;
7. état Decision/Pricing/Enterprise/Submission/PatronAction/Knowledge ;
8. mapping bounded contexts v3 ;
9. KEEP/ADAPT/MOVE/CREATE/DEFER/DELETE ;
10. risques de migration ;
11. plan PR-A0..A4 ;
12. questions réellement bloquantes.

Interdictions : pas de rewrite, suppression massive, migration destructive, Agent Orchestrator, nouvelle stack retrieval, microservices, GraphRAG, changement fournisseur IA, chantier frontend général ou PR fonctionnelle hors audit/tests sans validation.

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
