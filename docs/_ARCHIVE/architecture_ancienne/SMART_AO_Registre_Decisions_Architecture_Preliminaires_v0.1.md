# SMART AO — Registre des décisions d’architecture préliminaires

**Version : 0.1 — 12 septembre 2026**  
**Statut : décisions propriétaire à transmettre au futur cahier d’architecture**  
**Objet : modèle de service, isolation client, exploitation, coûts IA, résidence des données et cycle de vie d’un environnement client**

---

## 0. Rôle du document

Ce document capture immédiatement les décisions prises avant la rédaction du cahier d’architecture logicielle. Il évite qu’un choix structurant exprimé pendant la conception produit soit perdu ou réinterprété plus tard par le code.

Il ne constitue pas encore le cahier technique complet. Il fixe des **contraintes d’architecture et d’exploitation** que la future architecture devra satisfaire, puis vérifier par une table de traçabilité.

Les choix de technologies restent ouverts : fournisseur VPS/cloud, système de conteneurs, base de données, stockage objet, IaC, orchestration, reverse proxy, solution de sauvegarde, fournisseur LLM et outillage de supervision.

---

# ADR-DEP-001 — Modèle de déploiement client

## Décision

SMART AO sera commercialisé comme un **SaaS opéré par l’éditeur**, mais le modèle de déploiement initial sera **single-tenant dédié par entreprise cliente**.

Chaque entreprise cliente dispose d’un environnement dédié, hébergé en France ou, à défaut après décision explicite, dans l’EEE. L’environnement est exploité, maintenu et mis à jour par SMART AO. Le client accède à l’application par une interface web et ne reçoit pas une installation autonome à maintenir.

La doctrine retenue est :

> **Single-tenant au déploiement ; tenant-aware dans l’application.**

Le logiciel conserve donc une notion d’organisation/tenant, de rôles, de droits, de périmètres et de délégations, même lorsqu’une instance ne sert qu’une seule entreprise.

## Représentation cible

```text
CLIENT A
URL A
  ↓
ENVIRONNEMENT DÉDIÉ A — FRANCE/EEE
Application SMART AO
Base de données A
Stockage documents A
Index/recherche A
Secrets A
Sauvegardes A
Journaux/monitoring A

CLIENT B
URL B
  ↓
ENVIRONNEMENT DÉDIÉ B — FRANCE/EEE
Application SMART AO
Base de données B
Stockage documents B
Index/recherche B
Secrets B
Sauvegardes B
Journaux/monitoring B
```

## Motifs

1. **Confidentialité métier forte** : prix d’achat, marges, trésorerie, documents bancaires, données personnelles, DCE, références, décisions, appréciations partenaires et Mémoire Entreprise ne doivent pas être mélangés avec les données d’une autre PME.
2. **Argument commercial compréhensible** : le patron peut se voir proposer un environnement dédié à son entreprise plutôt qu’une simple promesse abstraite d’isolation logique.
3. **Cycle de vie client plus lisible** : sauvegarde, export, suspension et destruction d’un environnement peuvent être raisonnés client par client.
4. **Réduction du blast radius** : un incident sur une instance ne doit pas devenir automatiquement un incident de données métier pour toutes les entreprises.
5. **Cohérence avec la Mémoire Entreprise** : SMART AO doit être perçu comme un collaborateur à qui l’entreprise confie un patrimoine privé, daté et gouverné.

## Contreparties acceptées

- coût d’infrastructure supérieur à un SaaS multi-tenant mutualisé ;
- davantage d’environnements à maintenir ;
- besoin d’automatiser provisioning, mises à jour, sauvegardes, supervision et restauration ;
- nécessité de connaître le coût réel par client.

Ces coûts sont acceptés comme compromis initial en échange de la confiance, de l’isolation et de la lisibilité commerciale.

## Interdictions

- aucun fork de code métier spécifique à un client sans décision produit formelle ;
- aucune base métier partagée par défaut entre clients ;
- aucune clé secrète commune à tous les environnements si elle peut être évitée ;
- aucun déploiement manuel « artisanal » qui rende chaque client techniquement différent ;
- aucune hypothèse selon laquelle l’absence d’autre client dans l’instance permet de supprimer le modèle d’organisation et de droits.

---

# ADR-STD-001 — Un seul produit, déployé plusieurs fois

## Décision

SMART AO doit conserver un **code source unique**, un schéma de version commun et une chaîne de livraison industrialisée.

```text
                    SMART AO
                  CODE PRODUIT
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
     Client A       Client B      Client C
     v1.x           v1.x          v1.x
```

La personnalisation client porte sur les données, règles, droits, paramètres, taxonomies autorisées, Mémoire Entreprise, sources et politiques ; elle ne doit pas créer des branches permanentes du logiciel.

## Conséquence

Le futur système de déploiement doit pouvoir :

- créer une nouvelle instance à partir d’un modèle reproductible ;
- connaître la version de chaque instance ;
- mettre à jour un sous-ensemble ou l’ensemble des clients de manière contrôlée ;
- revenir en arrière lorsque la politique de release le permet ;
- vérifier les migrations et recettes avant promotion ;
- identifier les différences de configuration sans comparer manuellement des serveurs.

---

# ADR-OPS-001 — Provisioning et exploitation industrialisés

## Décision

L’ouverture d’un nouveau client doit devenir une procédure automatisable et auditée, et non une suite de commandes Linux manuelles.

Le futur cahier technique devra couvrir au minimum :

```text
NOUVEAU CLIENT
  ↓
Créer l’environnement dédié
  ↓
Créer domaine / certificat
  ↓
Créer identités et secrets propres
  ↓
Déployer la version approuvée de SMART AO
  ↓
Initialiser base et stockage
  ↓
Configurer sauvegardes
  ↓
Configurer supervision et alertes
  ↓
Configurer enveloppe / suivi IA
  ↓
Créer le Patron propriétaire
  ↓
Exécuter les tests d’acceptation de l’instance
  ↓
Remettre l’accès au client
```

Le choix entre Ansible, OpenTofu/Terraform, conteneurs, Kubernetes ou autre reste différé. Le besoin fonctionnel et opérationnel est en revanche obligatoire.

---

# ADR-CP-001 — Séparer plan de contrôle et données métier client

## Décision

La cible pourra comporter un **Control Plane SMART AO** commun, séparé des **Data Planes clients**.

Le Control Plane peut gérer, sous réserve de minimisation :

- identité commerciale du client ;
- licence et offre souscrite ;
- version déployée ;
- santé technique ;
- capacité consommée ;
- état des sauvegardes ;
- métriques d’exploitation ;
- facturation et quotas ;
- opérations de déploiement.

Il ne doit pas devenir un entrepôt central des DCE, prix, marges, documents bancaires ou contenus de la Mémoire Entreprise.

```text
CONTROL PLANE SMART AO
licence · version · santé · coûts · déploiement
             │
     ┌───────┴────────┐
     ▼                ▼
DATA PLANE A      DATA PLANE B
DCE A             DCE B
Prix A            Prix B
Mémoire A         Mémoire B
Décisions A       Décisions B
```

La quantité exacte de métadonnées centralisées sera déterminée par minimisation, sécurité, support et facturation.

---

# ADR-AI-001 — Coûts IA séparés et mesurés par client

## Décision

Les coûts du fournisseur IA sont supportés initialement par l’éditeur SMART AO puis intégrés au modèle commercial du client. Ils ne doivent pas être invisibles dans le coût de revient.

Chaque client doit avoir un suivi distinct :

- consommation IA ;
- coût estimé/réel ;
- période de facturation ;
- limites ou enveloppe contractuelle ;
- usages anormaux ;
- éventuels dépassements ;
- ventilation par grandes capacités si utile et non intrusive.

Lorsque le fournisseur le permet, des projets, clés, budgets ou identifiants séparés par client sont préférables à une clé unique non attribuable.

## Doctrine commerciale provisoire

Le futur pricing pourra distinguer :

```text
ABONNEMENT SMART AO
+ environnement dédié
+ maintenance / sauvegardes / exploitation
+ enveloppe IA incluse
+ dépassement ou extension d’usage éventuel
```

L’unité vendue au client ne doit pas nécessairement être le « token ». Elle pourra devenir une unité commerciale plus lisible après observation réelle des usages : capacité mensuelle, volume documentaire, analyses incluses, crédits d’usage ou forfait adapté.

**Interdiction provisoire :** ne pas promettre « IA illimitée » à prix fixe avant de connaître la distribution réelle des consommations et son impact sur la marge SaaS.

---

# ADR-FIN-001 — Coût de revient et marge SaaS par client

## Décision

SMART AO doit pouvoir connaître le coût complet de chaque environnement client afin de protéger sa propre rentabilité.

Le futur pilotage éditeur devra pouvoir rapprocher au minimum :

- hébergement ;
- stockage ;
- sauvegardes ;
- trafic et services techniques ;
- IA/LLM ;
- services externes payants ;
- support exceptionnel ;
- licence facturée ;
- marge brute SaaS estimée.

Les données de coût éditeur ne sont pas exposées au client sauf règle commerciale explicite.

---

# ADR-SEC-001 — Défense en profondeur malgré l’instance dédiée

## Décision

L’instance dédiée ne sera jamais considérée comme une mesure de sécurité suffisante à elle seule.

La future architecture devra spécifier au minimum :

- secrets distincts par environnement lorsque possible ;
- principe du moindre privilège ;
- rôles et droits applicatifs ;
- authentification renforcée pour actions sensibles ;
- chiffrement des flux ;
- chiffrement au repos selon les risques et services retenus ;
- sauvegardes isolées et testées ;
- capacité de restauration démontrée ;
- gestion des correctifs ;
- supervision ;
- journalisation des actions sensibles ;
- traçabilité des accès de support ;
- séparation des environnements de développement, test et production ;
- politique de rotation/révocation des secrets ;
- traitement et notification des incidents.

La CNIL rappelle que la sous-traitance doit être encadrée contractuellement et recommande notamment garanties de sécurité, chiffrement selon la sensibilité, chiffrement des transmissions, traçabilité, habilitations, authentification et conditions de restitution/destruction en fin de contrat.[^1]

---

# ADR-DATA-001 — Résidence France/EEE et accès depuis le Maroc

## Décision de cible

Pour la clientèle française initiale, SMART AO vise :

> **hébergement principal des données métier client en France ; à défaut, décision explicite pour une localisation dans l’EEE.**

Cette cible concerne notamment : base de données, documents, index/recherche, sauvegardes et journaux contenant des données client, sous réserve de l’analyse de chaque fournisseur.

## Limite importante

SMART AO ne doit pas promettre commercialement « aucune donnée ne quitte la France » tant qu’une cartographie complète n’a pas vérifié :

- fournisseur IA et région de traitement ;
- sauvegardes ;
- supervision ;
- messagerie ;
- support ;
- CDN ;
- services tiers ;
- accès d’administration ;
- sous-traitants ultérieurs.

## Administration depuis le Maroc

Le fondateur/exploitant travaillant depuis le Maroc, l’accès distant à des données personnelles ou à des contenus client depuis le Maroc doit être traité comme un **sujet de transfert international et de gouvernance des accès à qualifier juridiquement**, et non comme un détail d’exploitation.

Le Maroc n’apparaît pas, à la date de cette décision, dans la liste publiée par la Commission européenne des juridictions reconnues adéquates au titre du RGPD.[^2] En l’absence d’adéquation, le chapitre V du RGPD prévoit des garanties appropriées pour les transferts vers un pays tiers, notamment selon les cas les clauses contractuelles types dédiées aux transferts internationaux.[^3][^4]

## Orientation produit et exploitation

La cible est donc :

- aucun accès humain ordinaire au contenu client lorsque l’exploitation technique peut s’en passer ;
- accès support exceptionnel, nominatif, limité dans le temps et au périmètre nécessaire ;
- authentification forte ;
- journalisation ;
- information/encadrement contractuel approprié ;
- mécanismes de support privilégiant diagnostics techniques, métadonnées et consentement explicite avant accès au contenu ;
- possibilité future de support sans accès aux données métier lorsque techniquement réaliste.

La qualification juridique exacte — responsable, sous-traitant, sous-traitants ultérieurs, transfert, garanties et documentation — sera validée avec un professionnel compétent avant commercialisation.

---

# ADR-CONTRACT-001 — Cadre contractuel de sous-traitance et fournisseurs

## Décision

Le modèle SaaS devra disposer d’un cadre contractuel décrivant au minimum :

- rôle des parties pour les données personnelles ;
- objet, durée et finalité du traitement ;
- catégories de données et personnes concernées ;
- confidentialité ;
- mesures de sécurité ;
- sous-traitants ultérieurs ;
- localisation et transferts ;
- assistance et incidents ;
- audit/garanties ;
- restitution/export ;
- suppression/destruction en fin de contrat.

La CNIL rappelle que l’article 28 du RGPD impose un contrat spécifique entre responsable de traitement et sous-traitant, et publie des clauses types pouvant servir de support ; ces clauses de sous-traitance ne remplacent pas, le cas échéant, les clauses dédiées aux transferts internationaux.[^5]

---

# ADR-OFF-001 — Fin de contrat et destruction d’un environnement

## Décision

La fin de contrat doit être conçue dès le départ.

Le parcours cible est :

```text
Demande / fin de contrat
  ↓
Qualifier obligations de conservation
  ↓
Préparer export exploitable
  ↓
Remettre l’export / confirmer réception
  ↓
Geler les nouveaux traitements
  ↓
Appliquer délai contractuel de réversibilité
  ↓
Supprimer données actives
  ↓
Traiter sauvegardes selon politique annoncée
  ↓
Révoquer secrets et accès
  ↓
Détruire l’environnement dédié
  ↓
Conserver la preuve de clôture autorisée
```

L’export doit viser, selon les droits et formats : fichiers originaux, métadonnées, décisions, manifestes, preuves, historiques utiles et données structurées réutilisables.

Aucune promesse de suppression instantanée des sauvegardes ne doit être faite si l’architecture réelle ne permet pas de la prouver.

---

# ADR-SALES-001 — Formulation commerciale autorisée

## Décision

Le modèle dédié devient un argument commercial, mais la communication doit rester techniquement et juridiquement exacte.

### Formulations compatibles avec la cible

- « Votre environnement SMART AO est dédié à votre entreprise. »
- « Vos données métier ne partagent pas la même base opérationnelle qu’un autre client dans le modèle Business Dedicated. »
- « L’hébergement principal est prévu en France, sous réserve des flux externes explicitement documentés. »
- « SMART AO sépare vos données métier, vos droits et votre consommation d’usage. »

### Formulations interdites sans démonstration

- « Vos données ne quittent jamais la France. »
- « Aucune personne ne peut accéder à vos données. »
- « Sécurité absolue. »
- « Zéro fuite possible. »
- « IA illimitée. »
- « Suppression instantanée de toutes les sauvegardes. »

---

# ADR-EVOL-001 — Évolution éventuelle vers du multi-tenant

## Décision

Le multi-tenant mutualisé n’est pas le modèle de départ.

Il peut être réévalué plus tard si :

- un segment d’entrée de gamme exige un coût d’infrastructure beaucoup plus faible ;
- l’isolation logique et les tests de sécurité atteignent le niveau requis ;
- la réversibilité et la suppression peuvent être démontrées ;
- le coût d’exploitation du modèle dédié devient un frein commercial mesuré ;
- la décision ne dégrade pas la promesse de confidentialité du produit principal.

Une segmentation future pourrait exister sans être décidée aujourd’hui :

```text
SMART AO ESSENTIAL   → éventuellement mutualisé
SMART AO BUSINESS    → environnement dédié
SMART AO ENTERPRISE  → environnement dédié + exigences spécifiques
```

Aucune de ces offres n’est figée par le présent document.

---

# 10. Critères d’acceptation à remettre au futur cahier technique

L’architecture proposée ne pourra être approuvée que si elle répond explicitement aux questions suivantes :

1. comment une entreprise cliente est-elle isolée des autres au niveau infrastructure et application ?
2. comment l’organisation/tenant reste-t-elle un invariant du domaine ?
3. comment une nouvelle instance est-elle créée de manière reproductible ?
4. comment connaît-on sa version, son état et ses migrations ?
5. comment sauvegarde-t-on et restaure-t-on une instance client ?
6. comment sépare-t-on les secrets ?
7. comment mesure-t-on les coûts IA et infrastructure par client ?
8. quelles données sont centralisées dans le Control Plane et lesquelles y sont interdites ?
9. où résident base, documents, index, journaux et sauvegardes ?
10. quels flux sortent de France/EEE et pourquoi ?
11. comment l’accès support depuis le Maroc est-il empêché, autorisé, limité, tracé et contractuellement encadré ?
12. comment un client exporte-t-il ses données ?
13. comment une instance est-elle détruite et comment la politique de sauvegarde est-elle appliquée ?
14. quelles fonctions critiques continuent à marcher si le fournisseur IA est indisponible ?
15. comment une mise à jour est-elle déployée sur plusieurs instances sans créer des variantes client permanentes ?

---

# 11. Décisions encore ouvertes

Le présent document fixe le **modèle de service cible**, pas son implémentation.

Restent à décider dans le cahier technique :

- fournisseur(s) d’hébergement et région(s) ;
- VPS simple, VM managée, PaaS, cluster ou autre unité de déploiement ;
- conteneurisation ;
- méthode IaC / configuration ;
- stratégie de domaine et certificats ;
- PostgreSQL managé ou auto-hébergé ;
- stockage documentaire ;
- moteur de recherche/vectoriel ;
- sauvegardes, RPO, RTO et tests de restauration ;
- monitoring et alerting ;
- WAF / reverse proxy / protection réseau ;
- gestion des secrets ;
- fournisseur IA et région de traitement ;
- séparation des clés/projets IA ;
- modèle exact de quotas ;
- procédure support ;
- DPA, SCC éventuelles et registre des sous-traitants ;
- stratégie de mise à jour progressive et rollback ;
- éventuel Control Plane central.

---

# 12. Position dans la documentation SMART AO

Ce registre devient une **entrée obligatoire** du futur cahier d’architecture logicielle, au même titre que :

1. `SMART_AO_Cahier_des_charges_Metier_v1.0.md` ;
2. `SMART_AO_Univers_documentaire_metier_v1.0.md` ;
3. `SMART_AO_CCF_UX_Product_Blueprint_v1.1.md` ;
4. `SMART_AO_Benchmark_Concurrentiel_UX_Parcours_v1.0.md` ;
5. le présent `SMART_AO_Registre_Decisions_Architecture_Preliminaires_v0.1.md`.

Le cahier technique devra transformer ces décisions en architecture concrète et produire une table de traçabilité montrant où chacune est satisfaite.

---

## Sources externes de cadrage

[^1]: CNIL, « Sécurité : Gérer la sous-traitance », 14 mars 2024, https://www.cnil.fr/fr/securite-gerer-la-sous-traitance
[^2]: Commission européenne, « Data protection adequacy for non-EU countries », liste consultée le 12 septembre 2026, https://commission.europa.eu/law/law-topic/data-protection/international-dimension-data-protection/adequacy-decisions_en
[^3]: CNIL, RGPD — Chapitre V, « Transferts de données à caractère personnel vers des pays tiers ou à des organisations internationales », https://www.cnil.fr/fr/reglement-europeen-protection-donnees/chapitre5
[^4]: Commission européenne, « Standard Contractual Clauses (SCC) », https://commission.europa.eu/law/law-topic/data-protection/international-dimension-data-protection/standard-contractual-clauses-scc
[^5]: CNIL, « Clauses contractuelles types entre responsable de traitement et sous-traitant », https://www.cnil.fr/fr/clauses-contractuelles-types-entre-responsable-de-traitement-et-sous-traitant

