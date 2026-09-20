# SMART AO — Architecture logicielle v3.0 — Cadrage directeur initial

**Date : 12 septembre 2026**  
**Statut : DRAFT directeur — base de conception logicielle avant découpage PR Codex**  
**Objet : consolider les référentiels métier, documentaire, UX et les ADR préliminaires dans une architecture logicielle cohérente pour SMART_AO V8.**

## 0. Hiérarchie documentaire de référence

Ordre de priorité pour la conception logicielle :

1. `SMART_AO_Cahier_des_charges_Metier_v1.0`
2. `SMART_AO_Univers_documentaire_metier_v1.0`
3. `SMART_AO_CCF_UX_Product_Blueprint_v1.1`
4. `SMART_AO_Registre_Decisions_Architecture_Preliminaires_v0.1`
5. `SMART_AO_Benchmark_Concurrentiel_UX_Parcours_v1.0`
6. `SMART_AO_Cahier_des_charges_Architecture_Metier_v2.3` — **baseline technique héritée à réconcilier, non norme finale**
7. Code existant SMART_AO V8 — **socle réel à faire évoluer, jamais supposé identique aux documents**

`CCF-UX v1.0` est supersédé par `CCF-UX v1.1` et ne doit plus servir de référence normative.

## 1. Décision de migration documentaire

L’architecture métier/technique v2.3 n’est pas jetée. Elle conserve des décisions techniques fortes :
- V8 est le socle à faire évoluer, pas à réécrire ;
- architecture cible != architecture de construction ;
- chaîne probatoire minimale `Document/Fragment -> SourceAnchor -> Evidence -> Requirement -> validation humaine` ;
- `DceRequirement`, `Decision`, `Pricing/CostBasis`, `enterprise`, `submission`, `patron_action` sont adaptés avant toute suppression ;
- Golden DCE et environnement de tests sont des gates ;
- Agent Orchestrator, Artifact Registry général, reranking, GraphRAG, vision/plans et nouvelles abstractions sont différés tant qu’un besoin mesuré ne les justifie pas.

Mais v2.3 précède le CCF v1.1 et les ADR de déploiement. Elle ne couvre pas suffisamment :
- Radar BOAMP/TED et modèle Opportunité ;
- expérience AI-native / harnais fonctionnel ;
- Mémoire Entreprise comme patrimoine privé gouverné ;
- marchés privés et contrat réellement accepté ;
- collaboration simultanée et partage ciblé ;
- cycle de vie des données et réversibilité ;
- single-tenant dédié + tenant-aware ;
- control plane / data plane ;
- coût IA et coût d’exploitation par client ;
- exigences UX/accessibilité/reprise devenues normatives.

La v3.0 doit donc **absorber v2.3**, pas simplement l’amender à la marge.

## 2. Architecture de produit retenue

SMART_AO est un **modular monolith structuré par bounded contexts**, déployé initialement en **single-tenant dédié par client**, mais conservant `tenant/organization` dans le domaine.

Raisons :
- V8 possède déjà un socle utile ;
- une architecture microservices précoce augmenterait le coût, l’exploitation et les risques de cohérence ;
- les frontières métier doivent être explicites dès maintenant sans imposer des déploiements distribués ;
- certaines fonctions pourront être extraites plus tard si charge, sécurité ou exploitation le justifient.

### 2.1 Bounded contexts cibles

1. **Identity & Access**
   - organisation, utilisateurs, rôles, délégations, sessions, MFA, permissions, partage ciblé.

2. **Opportunity / Radar**
   - sources BOAMP/TED, recherche, profils de veille, déduplication, fraîcheur, suivi, qualification, conversion en Affaire.

3. **Case / Affair**
   - conteneur métier principal, lot/périmètre, cycle P0–P7, responsables, états, jalons.

4. **DCE & Document Intelligence**
   - ingestion, versions, archives, extraction, classification, locators, couverture, rectificatifs.

5. **Evidence & Market Understanding**
   - SourceAnchor, Evidence, Requirements, Unknowns, Hypotheses, Risks, InformationRequirements/MIRP, applicabilité, contradictions.

6. **Enterprise Memory**
   - identité, preuves, assurances, qualifications, personnes, matériel, références, partenaires, méthodes, produits, modèles, prix/achats, données financières et règles internes.
   - provenance, validité, sensibilité, propriétaire, réemploi autorisé.

7. **Decision & Governance**
   - portes P0–P7, décisions nominatives, conditions, dérogations, contextes figés, invalidation après changement.

8. **Pricing Intelligence**
   - facteurs de coût, couverture du besoin, import/export des chiffrages, hypothèses, scénarios, contrôles.
   - ne fixe pas le prix final.

9. **Response & Artifacts**
   - candidature, mémoire, modèles, documents à remplir/générer/obtenir, engagements, validations et versions candidates.
   - pas d’Artifact Registry général tant que les cas réels ne sont pas stabilisés.

10. **Submission**
    - manifeste, version autorisée, signatures, canaux, reçu, rapprochement, preuve de remise.

11. **Collaboration & Work**
    - tâches, commentaires, affectations, contributions, conflits, délégations, notifications, reprises.

12. **Handover & Learning**
    - contrat vendu, engagements, réserves, hypothèses, passation, résultat et REX minimal.

13. **AI Runtime / Guidance**
    - provider port, context builder, policy/permission gate, tool registry, prompt/skill registry, structured outputs, citations, abstention, usage/cost accounting.
    - un seul assistant visible ; aucun Agent Orchestrator général dans la première tranche.

14. **Platform**
    - persistence, events/outbox, idempotence, optimistic concurrency, object storage, audit, observability, background jobs, configuration.

## 3. Déploiement initial

### 3.1 Doctrine
**Single-tenant au déploiement ; tenant-aware dans l’application.**

Chaque client possède un environnement métier dédié :
- application ;
- PostgreSQL ;
- stockage documentaire ;
- index/recherche ;
- secrets ;
- sauvegardes ;
- journaux/monitoring.

Le logiciel, les migrations et la chaîne de release restent uniques.

### 3.2 Control Plane
Un Control Plane commun est autorisé uniquement pour :
- licence ;
- version ;
- santé ;
- quotas/coûts ;
- sauvegardes ;
- déploiement ;
- métadonnées d’exploitation minimales.

Il ne centralise pas les DCE, prix, marges, Mémoire Entreprise ou décisions métier.

## 4. Architecture IA

SMART_AO est **AI-native mais pas chat-first**.

Le LLM n’est jamais appelé avec une simple conversation brute. Chaque appel passe par un harnais composé de :
- identité et droits de l’utilisateur ;
- affaire/lot/version/porte active ;
- données autorisées ;
- preuves et sources ;
- inconnus/contradictions ;
- outils autorisés ;
- politique d’action ;
- objectif immédiat ;
- schéma de sortie attendu.

### 4.1 Règles
- faits critiques : source exigée ;
- donnée entreprise : provenance validée exigée ;
- données interdites au rôle : absentes du contexte LLM ;
- document externe hostile : traité comme donnée, jamais comme instruction système ;
- action engageante : confirmation humaine ;
- proposition conversationnelle != état métier ;
- correction humaine : portée explicite et invalidation contrôlée ;
- indisponibilité LLM : navigation, preuves, décisions, documents et Coffre restent utilisables.

### 4.2 Fournisseur
Première implémentation : **un provider peut suffire**, derrière un port/provider adapter stable.  
Ne pas construire plusieurs intégrations seulement pour anticiper une portabilité future.

## 5. Données et invariants

Objets transversaux minimaux :
`Opportunity`, `Case`, `DceVersion`, `Document`, `ExtractionFragment`, `SourceAnchor`, `Evidence`, `Requirement`, `InformationRequirement`, `Unknown`, `Hypothesis`, `Risk`, `Task`, `Question`, `Commitment`, `Decision`, `EnterpriseItem`, `ResponseDocument`, `SubmissionManifest`, `Receipt`, `Share`.

Invariants :
- toute donnée dérivée revient à sa provenance ;
- toute décision revient à une personne, une autorité et une version ;
- tout droit s’applique aux recherches, exports et contextes IA ;
- tout changement critique invalide les validations dépendantes ;
- toute opération externe distingue préparation, tentative, envoi, réception et acceptation ;
- toute remise autorisée est liée à un manifeste immuable ;
- aucune version remplacée n’est utilisée comme active ;
- aucun statut « prêt » ne masque un C1 inconnu/illisible/contradictoire ;
- aucune conversation brute n’est source de vérité métier.

## 6. Première tranche de construction Codex — à conserver

La première tranche evidence-first de v2.3 reste valide, avec une adaptation : elle devient **Tranche A — Fondation probatoire**, et non l’architecture complète du produit.

### Tranche A
1. stabiliser l’environnement de tests réel (PostgreSQL, OCR si nécessaire) ;
2. Golden DCE Development versionné ;
3. SourceAnchor compatible avec fragments/locators V8 ;
4. Evidence distinct de SourceAnchor ;
5. adapter DceRequirement sans suppression ;
6. validation/rejet humain persistants et audités ;
7. invalidation ciblée après rectificatif ;
8. tests isolation tenant, provenance, reconstruction de citation et non-régression.

### STOP GATE
Après cette tranche, Codex s’arrête. Aucune extension majeure n’est engagée avant revue.

## 7. Tranches suivantes proposées

- **Tranche B — Affaire + couverture DCE + UX source**
- **Tranche C — Mémoire Entreprise minimale gouvernée**
- **Tranche D — Radar BOAMP puis TED**
- **Tranche E — MIRP / inconnus / risques / décisions P0–P3**
- **Tranche F — Réponse documentaire et engagements**
- **Tranche G — Coffre / manifeste / reçu**
- **Tranche H — Guidance IA contextuelle**
- **Tranche I — Pricing intelligence / partenaires / passation**

L’ordre précis B–I sera ajusté après audit réel du repo et dépendances existantes.

## 8. Travail requis avant premier merge

Avant d’autoriser Codex à modifier le cœur :
1. audit du repo V8 courant ;
2. cartographie `existant -> bounded context v3` ;
3. matrice KEEP / ADAPT / MOVE / CREATE / DEFER / DELETE ;
4. vérification de l’environnement de tests ;
5. inventaire des migrations et schémas de données ;
6. repérage des écarts entre code réel et Architecture v2.3 ;
7. plan de PR de la Tranche A ;
8. table de traçabilité vers les exigences métier/CCF/ADR.

## 9. Doctrine de migration

> **Ne pas supprimer le produit actuel. Changer progressivement son centre de gravité.**

Pas de rewrite global. Pas de big-bang. Pas de microservices par anticipation. Pas de nouvel agent général avant les fondations probatoires. Toute abstraction nouvelle doit être justifiée par une tranche réelle, un test ou une métrique.

