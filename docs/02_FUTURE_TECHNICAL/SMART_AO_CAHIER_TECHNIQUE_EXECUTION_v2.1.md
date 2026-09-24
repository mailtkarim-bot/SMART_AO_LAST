# SMART AO — CAHIER TECHNIQUE D’EXÉCUTION
## v2.1 — Dérivé du MASTER métier v2.0 et du Product Freeze v2.0 actif

**Date :** 24 septembre 2026  
**Statut :** RÉFÉRENCE TECHNIQUE ACTIVE — IMPLÉMENTATION PAR TRANCHES GOUVERNÉES  
**Destination :** Codex / revue architecture / plan de migration / futures PR  
**Dépôt :** `mailtkarim-bot/SMART_AO_LAST`  
**Remplace :** `docs/_ARCHIVE/architecture_ancienne/SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v1.0.md`  
**Référence métier :** `docs/00_REFERENCE_ACTIVE/SMART_AO_CAHIER_DIRECTEUR_METIER_MASTER_v2.0.md`

---



> **AUTORITÉ DE DÉRIVATION v2.1.** Ce cahier technique dérive du `docs/00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v2.0.md`, promu le 24 septembre 2026. Il autorise l'implémentation par tranches verticales gouvernées ; aucune activation silencieuse de comportement juridique, assurantiel ou HSE ne remplace les validations externes requises.

> **RÈGLE CODEX.** L'audit de l'existant et la matrice `KEEP / ADAPT / REPLACE / DELETE / ABSENT` sont produits sous `docs/03_PRODUCT_DESIGN_WORKING/realignment_v2_audit/`. Codex implémente ensuite par tranches verticales. Toute différence entre MASTER métier, Product Freeze v2.0 et le présent document est un défaut de spécification à remonter ; Codex ne choisit pas lui-même quel besoin métier supprimer.

# 0. Mandat, statut et règle de sécurité documentaire

## 0.1 Pourquoi cette version existe

Le cahier technique d’exécution v1.0 traduit correctement les invariants du Product Freeze v1.0 vers un monolithe modulaire tenant-aware : identité, Affaire, DCE, décision, prix, préparation, remise, audit, RAG, idempotence, append-only et sécurité.

Le nouveau `Cahier Directeur Métier Intégral — MASTER v2.0` révèle cependant une profondeur métier supplémentaire qui n’est pas encore explicitement traduite en contrats techniques suffisants :

- profil réglementaire dynamique de l’Affaire ;
- hiérarchie contractuelle et dérogations ;
- pénalités et sanctions contractuelles ;
- préservation des droits, délais et risques de forclusion ;
- ordres de service, modifications et travaux supplémentaires ;
- résiliation, substitution et exécution aux frais et risques ;
- réception, règlement des comptes, décompte général et DGD ;
- assurance : couverture réelle de l’activité et non simple présence d’une attestation ;
- HSE comme contrainte de capacité, délai et coût ;
- engagements environnementaux et sociaux mesurables ;
- circuit réel de paiement ;
- coût post-réception et garanties ;
- autorisations et dépendances tierces ;
- exposition portefeuille multi-Affaires ;
- Carte d’Engagement Patron consolidant les conséquences plutôt qu’un score opaque.

Cette v2.0 constitue la **traduction technique candidate** de cette profondeur.

## 0.2 Règle de précédence pendant la transition

La confrontation MASTER métier v2.0 ↔ Product Freeze v1.0 étant désormais réalisée et le Product Freeze v2.0 promu, la règle active est :

1. le **Product Freeze v2.0** est l’autorité produit officielle du dépôt ;
2. le **Product Freeze v2.0** porte le contrat produit issu de l'audit d'écart ;
3. le présent **Cahier technique v2.1** décrit la traduction technique candidate et le travail d’audit nécessaire ;
4. Codex peut réaliser les inventaires, analyses de dépendances, matrices `KEEP / ADAPT / REPLACE / DELETE`, tests de caractérisation et propositions de migration ;
5. Codex **ne doit pas activer silencieusement un comportement métier nouveau** hors des tranches et gates approuvées ;
6. toute implémentation qui modifie rôles, portes P0–P7, droits, état métier, règle de décision, portée vendue ou comportement visible attend la décision propriétaire correspondante.

Cette séparation est volontaire. Elle évite que le code devienne une autorité de fait avant l’arbitrage produit.

## 0.3 Mandat Codex — READ-ONLY / AUDIT FIRST

Avant la première migration ou création de modèle liée aux nouveaux domaines, Codex doit produire un audit factuel du dépôt.

Le mandat initial est :

```text
READ-ONLY / AUDIT FIRST
1. Cartographier l’existant réel.
2. Localiser modèles, services, ports, événements, routes, projections, tests et migrations concernés.
3. Classer chaque capacité : KEEP / ADAPT / REPLACE / DELETE / ABSENT.
4. Identifier les invariants déjà protégés par tests.
5. Identifier les divergences entre code, Product Freeze v2.0 actif et MASTER métier v2.0.
6. Proposer la plus petite migration cohérente.
7. Ne créer aucun droit, état ou pouvoir implicite.
8. Ne coder qu’après gate propriétaire/technique explicite.
```

### Sorties obligatoires de l’audit

- `CURRENT_STATE_MAP` : modules, tables, migrations, commandes, projections et tests existants ;
- `TRACEABILITY_DELTA` : MASTER métier → contrat technique → existant → écart ;
- `DATA_MIGRATION_IMPACT` ;
- `AUTHORIZATION_IMPACT` ;
- `AI_RAG_IMPACT` ;
- `UX_API_IMPACT` ;
- `TEST_GAP_MAP` ;
- `PR_PLAN` ordonné et réversible ;
- risques et rollback de chaque tranche.

Aucune affirmation « déjà supporté » n’est admise sans preuve dans le code ou les tests.

---

# 1. État technique de référence à préserver

## 1.1 Architecture générale

La direction existante est conservée :

- **frontend :** React 19 + TypeScript + Vite sous `web/` ;
- **backend :** Python + FastAPI sous `backend/app/` ;
- **persistence :** PostgreSQL + SQLAlchemy + Alembic ;
- **jobs :** workers Python existants pour ingestion, export et projections ;
- **documents :** stockage privé référencé par hash et clé interne ;
- **IA/RAG :** retrieval borné par tenant, Affaire, DCE, rôle et classification ;
- **déploiement :** monolithe modulaire sur Docker Compose aujourd’hui, VPS durci ensuite ;
- **modèle d’exploitation cible initial :** instance dédiée par client mais application tenant-aware ;
- **aucun rewrite global**, aucun microservice par anticipation.

## 1.2 Invariants techniques existants à ne pas affaiblir

1. `tenant` résolu côté serveur ; jamais accepté comme autorité venant du navigateur.
2. rôle, membership, affectation, délégation et step-up résolus côté serveur.
3. aucune donnée financière Patron-only dans un contrat Collaborateur.
4. toute conclusion critique revient à une source et une version.
5. les inconnus restent `UNKNOWN`, `PARTIAL` ou `REVIEW_REQUIRED` selon le contrat ; absence de donnée ≠ zéro ≠ conformité.
6. transitions critiques et preuves append-only lorsque l’historique doit être défendable.
7. commandes sensibles idempotentes.
8. résultat externe inconnu n’est jamais converti en succès.
9. document externe = donnée non fiable ; jamais instruction système.
10. LLM = extraction/recherche/proposition ; jamais autorité de décision.
11. calcul financier déterministe ; jamais délégué au LLM.
12. migration additive et réversible autant que le contrat le permet.
13. code et tests décrivent l’état réellement implémenté ; un document ne permet pas de prétendre qu’une capacité existe.

## 1.3 Doctrine de modification

La stratégie reste :

> **greenfield fonctionnel, migration technique sélective.**

Le besoin métier redéfinit ce qui doit être vrai. Le dépôt existant est audité et reçoit pour chaque composant :

- `KEEP` — protège déjà le bon invariant ;
- `ADAPT` — base saine mais contrat insuffisant ;
- `REPLACE` — modèle incompatible avec le besoin ;
- `DELETE` — comportement désormais interdit ou sans propriétaire ;
- `ABSENT` — capacité non implémentée.

Le statut est attribué après lecture du code et des tests, jamais par ressemblance de nom.

---

# 2. Principes architecturaux non négociables v2.0

Les principes v1.0 restent applicables et sont complétés par les suivants.

## 2.1 Métier et preuve

1. Une règle juridique ou réglementaire n’est jamais appliquée parce qu’un LLM « la connaît ».
2. Une règle vivante possède une source, une version, une date d’effet, une éventuelle date de fin, un champ d’application et un statut de validation.
3. Une clause du DCE prime sur une règle générique lorsque le contrat l’autorise ou la modifie ; cette relation doit être explicite.
4. Une dérogation n’écrase jamais la règle de référence : les deux restent visibles et reliées.
5. Un délai contractuel calculé conserve la règle, l’événement déclencheur, le timestamp de départ, le calendrier utilisé et la méthode de calcul.
6. Si l’un de ces éléments manque, le système ne fabrique pas d’échéance certaine.
7. Une pénalité extraite n’est pas une dette certaine ; elle est une règle d’exposition à qualifier et simuler.
8. Une attestation d’assurance n’est pas une conclusion de couverture.
9. Une exigence HSE n’est pas « traitée » tant que les moyens, compétences, délais ou preuves nécessaires ne sont pas reliés.
10. Un engagement de mémoire technique devient un objet métier si sa promesse est mesurable ou opposable.

## 2.2 Temps et temporalité

Toute règle susceptible d’évoluer doit être **bitemporelle ou au minimum effective-dated** selon le besoin :

- date de publication ;
- date d’effet ;
- date de fin si connue ;
- date de connaissance/import dans SmartAO ;
- version/supersession.

Une règle future reste future. Une règle expirée ne devient pas applicable à une affaire nouvelle. Une affaire ancienne conserve la règle utilisée au moment de sa décision si le contrat l’exige.

## 2.3 Exactitude financière et contractuelle

- argent : entier en centimes ou `Decimal` contrôlé selon conventions existantes ; **jamais float** ;
- pourcentage : représentation exacte/documentée ;
- durée/délai : unité et convention explicites ;
- fuseau horaire : source explicite ; jamais heure locale implicite du poste ;
- formules contractuelles : parse/normalisation déterministes uniquement lorsqu’elles sont suffisamment établies ; sinon revue humaine ;
- aucune exécution d’expression arbitraire extraite d’un document.

## 2.4 Reproductibilité

Tout résultat critique calculé doit être reproductible à partir de :

`inputs + source_versions + rule_version + algorithm_version + actor/context + timestamp`.

Cette règle vaut notamment pour :

- échéances de préservation des droits ;
- simulations de pénalités ;
- prix révisés/actualisés ;
- cash-flow ;
- exposition portefeuille ;
- couverture d’engagement ;
- applicability d’une règle validée.

---

# 3. Bounded contexts et frontières v2.0

Le monolithe modulaire reste la cible. Les domaines ci-dessous sont **frontières logiques**, pas des microservices.

## 3.1 Contextes existants à conserver / enrichir

### Identity & Access
Identité, tenant, membership, rôles, délégations, MFA, step-up, partage externe, suspension, récupération.

### Opportunity / Radar
Sources amont, opportunités, qualification P0/P1, provenance et inconnus.

### Case / Affaire
Périmètre, lots, phases, tours, acteurs, échéances de référence et projections opérationnelles.

### DCE & Document Intelligence
Admission, versioning, extraction, classification, fragments, locators, rectificatifs, lisibilité et couverture.

### Evidence & Market Understanding
Evidence, SourceAnchor, Requirement, MIRP, Unknown, Hypothesis, Contradiction, RiskSignal, Applicability, CostFactor.

### Enterprise Memory
Faits d’entreprise, preuves, ressources, personnes, partenaires, prix internes, assurances, qualifications, REX.

### Decision & Governance
P0–P7, conditions, motifs, dérogations décisionnelles, invalidation, supersession, autorité humaine.

### Pricing Intelligence
Imports, coût, prix, scénarios, trésorerie, facteurs de coût, couverture DPGF/BPU/DQE.

### Response & Artifacts
Pièces à produire/remplir/obtenir, mémoire, engagements, versions, contrôle et export.

### Submission
Candidate, manifeste, signature, P5, export, dépôt humain et preuve.

### Collaboration & Work
Tâches, revues, notifications, responsables, contributeurs, partage ciblé et reprise.

### Handover & Learning
Contrat vendu, passation P7, engagements, résultats, REX.

### AI Runtime / Guidance
Retrieval, reranking, context policy, outils, structured outputs, citations, abstention, télémétrie.

### Platform
Persistence, outbox, idempotence, jobs, stockage, logs, observabilité, sauvegardes.

## 3.2 Nouveau bounded context logique : Contract & Rights

**Statut : RÉFÉRENCE TECHNIQUE ACTIVE ; les tranches restent soumises à leurs gates d’implémentation.**

Ce domaine est justifié car il possède :

- son propre vocabulaire ;
- des transitions temporelles ;
- des calculs déterministes ;
- des obligations d’audit ;
- des dépendances vers DCE/Evidence sans appartenir au parser ;
- des conséquences sur Decision, Pricing et Handover sans appartenir à ces domaines.

Il regroupe :

- contrat de référence ;
- hiérarchie des pièces ;
- règles incorporées ;
- dérogations ;
- pénalités/sanctions ;
- événements de préservation de droits ;
- OS/modifications/travaux supplémentaires ;
- règlement des comptes / décomptes ;
- réception/garanties ;
- résiliation/substitution/frais et risques ;
- obligations contractuelles d’exécution et de preuve.

### Frontière stricte

`Contract & Rights` :

- **ne rend pas d’avis juridique autonome** ;
- ne détermine pas seul la validité d’une clause ;
- ne remplace pas un juriste/conseil ;
- expose règles, sources, conditions, calculs et incertitudes ;
- ouvre des revues humaines explicites lorsque la qualification dépasse le contrat déterministe.

## 3.3 Regulatory Knowledge — référentiel transversal, pas moteur juridique autonome

Le `RegulatoryProfile` et les règles vivantes peuvent être implémentés comme sous-domaine de Evidence/Knowledge ou module autonome si l’audit justifie la frontière.

Le choix physique est à déterminer **après inventaire** ; le contrat fonctionnel est en revanche figé dans ce candidat :

- rule store versionné ;
- applicability par faits prouvés ;
- source officielle ;
- dates d’effet ;
- exceptions ;
- revue humaine ;
- aucune conclusion réglementaire fondée uniquement sur génération LLM.

---

# 4. Modèle de données conceptuel v2.0

Les noms ci-dessous sont des **noms métier candidats**, pas des classes existantes revendiquées. Codex doit d’abord les mapper aux conventions et modèles du dépôt.

## 4.1 Regulatory Profile

### `RegulatoryProfile`

Portée : une Affaire / lot / option / phase selon besoin.

Attributs conceptuels :

- case/affaire ;
- lot/périmètre ;
- marché public/privé ;
- nature opération ;
- bâtiment / infrastructure / réseau / ouvrage ;
- neuf / existant / rénovation / démolition / maintenance ;
- destination/usage ;
- date(s) déterminantes ;
- année de construction lorsque prouvée ;
- surface/quantité lorsque applicable ;
- site occupé / ERP / site sensible ;
- géographie ;
- montant et seuils utiles ;
- sous-traitance/groupement ;
- substances/risques connus ;
- nombre d’entreprises/intervenants si pertinent ;
- provenance de chaque fait ;
- état de complétude.

Un champ non établi reste inconnu ; aucune valeur par défaut opportuniste.

### `RegulatoryRule`

Attributs conceptuels :

- identifiant stable interne ;
- juridiction ;
- thème ;
- source officielle ;
- référence ;
- version ;
- publication ;
- date d’effet ;
- date de fin éventuelle ;
- scope structuré ;
- exceptions structurées lorsque qualifiées ;
- niveau de validation ;
- propriétaire de revue ;
- dernière revue ;
- prochaine revue ;
- statut `FUTURE / ACTIVE / EXPIRED / SUPERSEDED / REVIEW_REQUIRED`.

### `RuleApplicabilityAssessment`

Relie une règle à une Affaire et conserve :

- faits utilisés ;
- faits manquants ;
- résultat `APPLICABLE / NOT_APPLICABLE / POTENTIALLY_APPLICABLE / REVIEW_REQUIRED / UNKNOWN` ;
- méthode ;
- rule version ;
- evidence ;
- validateur humain si nécessaire ;
- invalidation après changement d’un fait ou de la règle.

## 4.2 Contrat et hiérarchie

### `ContractBaseline`

Décrit le cadre contractuel identifié :

- type d’affaire ;
- documents constituant le contrat proposé ;
- référentiels incorporés lorsqu’ils sont explicitement cités ;
- version de chaque référentiel ;
- ordre de priorité si établi ;
- éléments non établis ;
- état de revue.

### `ContractRuleReference`

Relie une disposition contractuelle générique à sa source/version.

### `ContractDeviation`

Une dérogation ne remplace pas la règle ; elle la **référence**.

Champs :

- règle de référence ;
- clause particulière source ;
- nature de la modification ;
- périmètre ;
- texte/extrait ;
- impacts candidats ;
- certitude ;
- revue métier/juridique ;
- statut ;
- supersession.

### Invariant

Impossible d’avoir une dérogation « active » sans :

- source particulière ;
- règle de référence ou motif `REFERENCE_NOT_ESTABLISHED` ;
- portée ;
- état de revue.

## 4.3 Pénalités et sanctions

### `ContractSanctionRule`

Une entrée représente une règle contractuelle de sanction/pénalité.

Attributs conceptuels :

- déclencheur ;
- catégorie ;
- source et version ;
- scope lot/phase/engagement ;
- unité ;
- montant fixe ou formule normalisée si déterminable ;
- base de calcul ;
- franchise ;
- plafond ;
- exonération/seuil ;
- cumul ;
- prérequis de procédure ;
- cause exonératoire à examiner ;
- dérogation liée ;
- partie responsable ;
- recours partenaire éventuel ;
- statut de modélisation ;
- niveau de confiance ;
- validation humaine.

### Calculs de scénarios

Le moteur de simulation doit produire :

- hypothèses ;
- événements simulés ;
- formule/version ;
- résultat ;
- `MAX_EXPOSURE_UNKNOWN` lorsque l’absence de plafond ou une formule ambiguë interdit une borne défendable.

**Interdit :** interpréter une phrase libre avec `eval`, expression dynamique non contrôlée ou LLM comme calculateur autoritatif.

## 4.4 Préservation des droits

### `RightPreservationEvent`

Objet C1 central.

Champs minimaux :

- type d’événement ;
- affaire/lot/phase ;
- événement déclencheur source ;
- document/version ;
- règle contractuelle applicable ;
- dérogation éventuelle ;
- timestamp de réception/constat ;
- convention de calcul du délai ;
- date/heure limite calculée si établie ;
- fuseau et calendrier ;
- destinataires ;
- canal/forme ;
- contenu minimal attendu ;
- montant/chef de demande lorsque applicable ;
- responsable interne ;
- validateur ;
- preuve d’envoi ;
- preuve de réception ;
- état ;
- conséquence potentielle ;
- `REVIEW_REQUIRED` si qualification juridique nécessaire.

États candidats :

`OPEN → DUE → PREPARED → SENT → ACKNOWLEDGED → CLOSED`

États alternatifs :

`REVIEW_REQUIRED`, `DISPUTED`, `SUPERSEDED`, `EXPIRED`, `UNKNOWN_OUTCOME`.

Les états définitifs devront être alignés sur les conventions existantes après audit.

### Invariants C1

1. aucune échéance certaine sans règle et événement de départ établis ;
2. toute date calculée conserve ses inputs ;
3. changer la version contractuelle invalide les calculs dépendants ;
4. une échéance expirée n’efface pas l’événement ;
5. « envoyé » ≠ « reçu » ;
6. « reçu » ≠ « juridiquement suffisant » ;
7. l’IA ne ferme jamais l’événement ;
8. l’utilisateur qui valide doit être habilité pour le périmètre ;
9. chaque événement critique apparaît dans la passation P7.

## 4.5 OS, modifications et travaux supplémentaires

### `ContractChangeInstruction`

Capture :

- instruction/OS/demande ;
- émetteur ;
- pouvoir de prescription non présumé ;
- source ;
- date ;
- prestation ;
- prix fourni/non fourni ;
- délai fourni/non fourni ;
- impacts identifiés ;
- action de préservation liée ;
- nouveau prix/proposition si validé ;
- statut d’acceptation/exécution ;
- preuves.

Le système ne transforme jamais l’absence de prix en « inclus ».

## 4.6 Règlement des comptes, réception et DGD

### `SettlementMilestone`

Types candidats :

- situation/acompte ;
- projet de décompte ;
- projet de décompte final ;
- décompte général ;
- DGD ;
- réception ;
- réserves ;
- levée de réserves ;
- garantie/libération.

Chaque jalon :

- source ;
- date de réception ;
- montant lorsque autorisé ;
- réserves/écarts ;
- délai de réaction ;
- événements de droits liés ;
- statut ;
- preuve.

## 4.7 Résiliation et substitution

### `TerminationExposure`

Représente l’exposition, pas une décision juridique automatique :

- cause/clause ;
- prérequis ;
- mise en demeure ;
- délai de remède ;
- résiliation potentielle ;
- substitution/exécution aux frais et risques ;
- coût/scénarios ;
- garanties affectées ;
- partenaires affectés ;
- preuves ;
- revue spécialisée.

## 4.8 Assurance

### `InsuranceCoverageAssessment`

Compare une **prestation/activité promise** à une preuve assurantielle.

Champs :

- activité/prestation ;
- ouvrage/technique ;
- période ;
- zone ;
- titulaire ;
- attestation/police source ;
- libellé déclaré ;
- exclusions/réserves visibles ;
- conclusion limitée ;
- validateur courtier/assureur si nécessaire ;
- état.

États métier candidats :

`COVERED`, `PROBABLY_COVERED`, `NOT_ESTABLISHED`, `OUTSIDE_DECLARED_ACTIVITY`, `BROKER_REVIEW_REQUIRED`.

Ces valeurs sont des états de workflow interne, **pas des avis juridiques**.

## 4.9 HSE et prérequis d’exécution

### `ExecutionPrerequisite`

Relie une obligation à :

- compétence ;
- personne/ressource ;
- matériel ;
- autorisation ;
- document ;
- formation/habilitation ;
- délai d’obtention ;
- coût ;
- phase ;
- blocage ;
- preuve ;
- responsable.

Exemples : PPSPS, inspection commune, consignation, AIPR, DT-DICT, RAT, habilitation, accès, autorisation exploitant.

## 4.10 Engagement mesurable

### `MeasurableCommitment`

Un engagement de l’offre ou du contrat devient objet lorsqu’il promet :

- une valeur ;
- un moyen ;
- une fréquence ;
- un délai ;
- une personne ;
- un matériel ;
- un taux ;
- une performance ;
- une obligation de reporting.

Champs :

- texte source ;
- valeur/objectif ;
- unité ;
- méthode de mesure ;
- fréquence ;
- preuve attendue ;
- coût ;
- ressource ;
- responsable ;
- sous-traitants concernés ;
- obligation de cascade ;
- sanction liée ;
- phase ;
- statut de couverture.

Le simple texte du mémoire n’est pas la source de vérité du suivi : la version remise et son hash restent reliés.

## 4.11 Circuit de paiement

### `PaymentCircuit`

Un circuit décrit :

`production → demande/situation → contrôleur/visa → service fait → payeur/plateforme → encaissement`.

Chaque étape :

- acteur ;
- pièce ;
- délai contractuel ;
- motif de rejet/suspension ;
- preuve ;
- dépendance ;
- retenue ;
- statut ;
- hypothèse de cash associée.

Il ne remplace ni Chorus Pro ni la comptabilité.

## 4.12 Obligations post-réception

### `PostReceptionObligation`

- OPR ;
- essais ;
- mise en service ;
- formation ;
- DOE/DIUO ;
- levée de réserves ;
- GPA ;
- maintenance initiale ;
- stock pièces ;
- astreinte ;
- clôture administrative ;
- libération garanties.

Chaque obligation peut porter coût, ressource, échéance, preuve et sanction liée.

## 4.13 Autorisations et dépendances tierces

### `ExternalDependency`

Couvre :

- autorisation voirie/domaine public ;
- coupure ;
- concessionnaire ;
- badge/site sensible ;
- survol/grutage ;
- arrêté circulation ;
- consignation ;
- accès exploitant ;
- autorisation environnementale/projet si explicitement pertinente.

Le moteur de planning peut constater une dépendance non sécurisée ; il ne prétend pas que l’autorisation sera obtenue.

---

# 5. Carte d’Engagement de l’Affaire — projection centrale Patron

## 5.1 Nature

La Carte d’Engagement est une **projection de décision**, pas une nouvelle source de vérité.

Elle agrège des objets autoritatifs depuis leurs contextes et répond aux douze axes :

1. intérêt commercial ;
2. admissibilité/candidature ;
3. périmètre technique ;
4. constructibilité/logistique ;
5. contrat/exposition ;
6. prix/marge ;
7. trésorerie/garanties ;
8. capacité/charge ;
9. partenaires ;
10. HSE/environnement/réglementaire ;
11. obligations documentaires/engagements ;
12. préservation des droits/sortie de contrat.

## 5.2 Interdiction du score opaque

Aucune somme pondérée ne peut produire un GO automatique.

La projection peut afficher :

- nombre d’objets ouverts par criticité ;
- conséquences ;
- conditions de porte ;
- risques acceptés ;
- inconnus ;
- échéances ;
- couverture par preuves ;
- scénarios économiques.

Mais elle ne doit jamais transformer cette information en « 83/100 donc GO ».

## 5.3 Anatomie technique d’une ligne Patron

Chaque ligne de risque/condition doit pouvoir exposer :

- source ;
- version ;
- locator ;
- applicabilité ;
- certitude ;
- impact technique ;
- impact coût ;
- impact délai ;
- impact trésorerie ;
- impact contractuel ;
- responsable ;
- action suivante ;
- échéance ;
- preuve attendue ;
- décision requise ;
- risque résiduel ;
- liens vers objets sources.

La projection est recalculable et ne duplique pas la vérité source.

## 5.4 GO sous conditions

Une condition doit être un objet adressable, et non du texte libre uniquement.

Elle conserve :

- porte ;
- condition ;
- cause ;
- responsable ;
- échéance ;
- preuve de levée ;
- règle de revalidation ;
- conséquences si non levée ;
- décision Patron.

Une condition levée n’efface pas son historique.

---

# 6. Applicabilité et moteur de règles sûr

## 6.1 Deux moteurs à ne pas confondre

### Moteur d’extraction

Peut utiliser IA/RAG pour trouver :

- indices de clauses ;
- références réglementaires ;
- dates ;
- usages ;
- seuils ;
- obligations candidates.

Sortie = **candidat sourcé**, jamais verdict réglementaire final.

### Moteur d’applicabilité

Utilise :

- faits structurés validés ;
- règles validées/versionnées ;
- opérateurs déterministes bornés ;
- exceptions explicitement modélisées ;
- revue humaine lorsque nécessaire.

## 6.2 DSL / règles

S’il existe un langage de règles, il doit être :

- déclaratif ;
- non Turing-complet ;
- sans exécution dynamique arbitraire ;
- versionné ;
- testable ;
- limité à des opérateurs whitelisted ;
- explicable en sortie.

Aucune expression réglementaire extraite d’un DCE ne devient directement exécutable.

## 6.3 Invalidation

Recalcul ciblé si :

- fait du profil change ;
- règle est supersédée ;
- date déterminante change ;
- nouvelle pièce DCE corrige le fait ;
- périmètre lot/option change.

Les anciens résultats restent audités avec leur rule version.

---

# 7. Hiérarchie contractuelle et dérogations

## 7.1 Graphe de contrat

Le système doit pouvoir représenter :

- document ;
- version ;
- nature contractuelle/indicative ;
- ordre de priorité explicite ;
- référence/incorporation ;
- modification/dérogation ;
- réponse acheteur/avenant/mise au point ;
- statut `PROPOSED / SUBMITTED / ACCEPTED / SUPERSEDED` selon contexte.

## 7.2 Règle de conflit

Une contradiction documentaire n’est pas résolue par priorité implicite si l’ordre contractuel n’est pas établi.

Sortie : `REVIEW_REQUIRED`.

## 7.3 Dérogations

Pipeline :

```text
REFERENCE_RULE
   ↓
PARTICULAR_CLAUSE
   ↓
DEVIATION_CANDIDATE
   ↓
HUMAN/DETERMINISTIC QUALIFICATION
   ↓
BUSINESS_IMPACTS
   ↓
P2/P3/P4 CONDITION OR RISK
```

Les impacts peuvent créer des liens vers Pricing, Capacity, Handover ou Right Preservation ; le module Contract ne duplique pas leurs données.

---

# 8. Calculs déterministes critiques

## 8.1 Pénalités

Un calcul doit conserver :

- montant d’assiette ;
- unité ;
- quantité/durée ;
- taux ;
- plafond/franchise ;
- règles de cumul ;
- version ;
- arrondi ;
- résultat.

Si le texte ne permet pas une normalisation fiable : `FORMULA_REVIEW_REQUIRED`.

## 8.2 Prix / actualisation / révision

Pour toute formule qualifiée :

- mois zéro ;
- date de référence ;
- index exact ;
- coefficients ;
- part fixe ;
- source index ;
- périodicité ;
- formule ;
- arrondi ;
- indice manquant ;
- substitution éventuelle ;
- résultat par période.

Le moteur doit comparer la protection client à l’exposition achats/fournisseurs sans conclure que l’une couvre automatiquement l’autre.

## 8.3 Délais de droits

Calcul :

`deadline = function(trigger_timestamp, rule_version, calendar, duration, timezone, exclusions)`

Le résultat conserve tous les inputs.

Éviter de coder « 30 jours » ou « 45 jours » comme constante métier globale.

## 8.4 Cash-flow

Les projections existantes doivent pouvoir intégrer :

- retenues ;
- avance et remboursement ;
- garanties bancaires ;
- situations ;
- délai prudent d’encaissement ;
- paiement sous-traitants ;
- achats ;
- frais bancaires ;
- pénalités scénarisées ;
- coûts post-réception ;
- obligations HSE/environnement ;
- scénarios de modification.

Aucun résultat ne doit être présenté comme prévision certaine.

## 8.5 Exposition portefeuille

Projection Patron-only :

- combinaison d’attributions ;
- cash cumulé ;
- garanties cumulées ;
- équipes/matériels partagés ;
- fournisseurs communs ;
- périodes de pointe ;
- hypothèses de probabilité clairement distinctes des engagements signés.

Une probabilité d’attribution ne devient jamais une prédiction automatique de marché.

---

# 9. Sécurité, droits et classification des nouvelles données

## 9.1 Classifications minimales

Les classifications exactes doivent réutiliser les enums du dépôt lorsqu’ils existent. Conceptuellement, les nouveaux objets nécessitent au moins :

- public/partageable ;
- affaire interne ;
- direction/finance ;
- juridique sensible ;
- données personnelles ;
- sécurité/site sensible.

Codex doit **mapper**, pas multiplier les enums si l’existant permet la règle.

## 9.2 Patron

Patron ou capacité explicitement déléguée :

- P3 ;
- acceptation des risques économiques ;
- seuils de trésorerie ;
- exposition sanctions ;
- solidarité ;
- acceptation de dérogations sensibles ;
- conditions GO ;
- P5 ;
- P6/P7 selon contrat.

## 9.3 Collaborateur

Peut :

- préparer ;
- sourcer ;
- qualifier candidat ;
- demander revue ;
- gérer tâches et preuves ;
- proposer impact.

Ne reçoit pas automatiquement :

- marge ;
- prix d’achat sensible ;
- cash ;
- exposition économique confidentielle ;
- appréciations partenaires Direction ;
- consultation juridique confidentielle hors périmètre.

## 9.4 Experts

QSE, DAF, conducteur, métreur, achats, juriste/conseil : accès limité par périmètre et besoin.

Une validation spécialisée n’élève pas le rôle au Patron.

## 9.5 Administrateur et support

Aucun droit métier implicite.

Les accès exceptionnels suivent les règles existantes : bornés, nominatifs, temporels, journalisés, avec objectif.

## 9.6 IA

Le context builder applique classification + permissions **avant retrieval et avant agrégation**.

Le LLM d’un rôle non financier ne doit pas pouvoir déduire la marge à partir d’agrégats intermédiaires.

---

# 10. Contrats d’application et idempotence

## 10.1 Principe

Les opérations métier passent par les services/commandes applicatifs existants. Les noms concrets ne sont pas imposés avant audit.

Chaque commande sensible porte les identifiants de corrélation/idempotence prévus par l’architecture existante.

## 10.2 Familles de commandes à supporter

Après mapping sur l’existant, l’application doit permettre de :

- enregistrer/corriger un fait réglementaire avec preuve ;
- qualifier l’applicabilité d’une règle ;
- enregistrer une règle contractuelle de référence ;
- qualifier une dérogation ;
- enregistrer/modéliser une pénalité ;
- créer/requalifier un événement de préservation de droits ;
- enregistrer un OS/modification ;
- enregistrer une preuve d’envoi/réception ;
- préparer une analyse assurance ;
- qualifier un prérequis HSE ;
- créer/revoir un engagement mesurable ;
- définir/revoir un circuit de paiement ;
- enregistrer un jalon de règlement/réception ;
- préparer/valider la passation P7.

## 10.3 Rejeu

Un retry après timeout doit :

- retourner le reçu antérieur si la commande est identique ;
- refuser même clé avec payload différent ;
- ne pas créer deux échéances, deux engagements ou deux preuves ;
- conserver `UNKNOWN_OUTCOME` si la confirmation externe manque.

---

# 11. Concurrence et cohérence transactionnelle

## 11.1 Optimistic concurrency

Les objets à forte contention doivent porter une révision ou mécanisme équivalent :

- décision ;
- condition GO ;
- événement de droit ;
- dérogation ;
- sanction ;
- engagement ;
- version de passation.

Une modification basée sur une révision ancienne doit produire un conflit explicite, pas « dernier clic gagne ».

## 11.2 Édition concurrente

Préserver :

- contribution A ;
- contribution B ;
- dernier état confirmé ;
- décision de merge/revue.

L’UX N01/N02 existante reste la doctrine.

## 11.3 Outbox

Les événements métier internes peuvent alimenter projections/notifications via outbox.

L’outbox ne transforme jamais :

- email envoyé supposé ;
- courrier reçu supposé ;
- dépôt reçu supposé ;
- notification réglementaire externe supposée.

Toute externalité conserve un statut de preuve propre.

---

# 12. IA / RAG / règles métier — séparation stricte

## 12.1 Pipeline obligatoire

```text
INGESTION
  → EXTRACTION
  → RETRIEVAL
  → RERANKING éventuel
  → CANDIDATE FACT / CLAUSE / REQUIREMENT
  → DETERMINISTIC RULES / BUSINESS SERVICES
  → HUMAN REVIEW WHEN REQUIRED
  → DECISION / GENERATION
```

Jamais :

```text
PDF → LLM → "conforme / assuré / délai certain / GO"
```

## 12.2 Extraction contractuelle

Le LLM peut proposer :

- clause candidate ;
- catégorie ;
- paramètres candidats ;
- source/locator ;
- ambiguïtés.

Il ne peut pas :

- inventer un plafond ;
- présumer une dérogation ;
- choisir une version de CCAG sans preuve ;
- conclure qu’une pénalité est inapplicable ;
- rendre un avis assurance ;
- créer une échéance juridique certaine si le trigger manque.

## 12.3 Réglementation

La connaissance générative n’est jamais la base de vérité.

Les règles actives proviennent d’un store validé ; la veille peut proposer une mise à jour mais celle-ci passe par revue, versioning et impact analysis.

## 12.4 Génération documentaire

Un brouillon d’OS/réserve/réclamation/question peut être généré uniquement à partir :

- faits sourcés ;
- paramètres validés ;
- modèle approprié ;
- destinataire sélectionné ;
- version de contrat ;
- mention explicite `DRAFT / REVIEW_REQUIRED`.

Aucun envoi automatique V1 sans décision séparée.

---

# 13. Document intelligence, locators et tableaux

## 13.1 Sources critiques

Les nouveaux domaines augmentent l’importance de :

- CCAP/CCP ;
- AE/projet de marché ;
- RC ;
- CCTP ;
- réponses acheteur ;
- actes de mise au point ;
- bordereaux ;
- plannings ;
- PGC/PPSPS ;
- attestations ;
- devis fournisseurs ;
- courriers/OS ;
- décomptes ;
- PV réception.

## 13.2 Locator

Une alerte contractuelle sans locator précis doit indiquer `SOURCE_LOCATION_PARTIAL` au lieu de simuler une précision inexistante.

## 13.3 Tableurs

Les formules et cellules de prix doivent conserver :

- feuille ;
- cellule/plage ;
- valeur ;
- formule si accessible ;
- type ;
- unité ;
- version du fichier ;
- hash.

Un export/import Excel ne peut pas silencieusement écraser le contexte source.

---

# 14. Rectificatifs et invalidation ciblée

Un nouveau DCE, Q/R, CCAP, DPGF ou planning peut invalider :

- exigence ;
- MIRP ;
- applicability ;
- dérogation ;
- pénalité ;
- délai ;
- prix ;
- cash ;
- assurance ;
- HSE ;
- engagement ;
- condition P2/P3/P4/P5 ;
- paquet de remise.

## 14.1 Graphe de dépendance

Toute conclusion critique doit déclarer ses dépendances suffisamment pour recalculer **les objets touchés**, pas purger toute l’Affaire.

## 14.2 Candidate invalidation

Si une pièce ayant contribué au paquet P5 change :

- candidate précédente reste historique ;
- readiness/P5 peut redevenir invalide ;
- aucun dépôt précédent n’est réécrit ;
- une nouvelle candidate doit être construite et autorisée.

---

# 15. Passation P7 renforcée

La passation devient le moment où l’on transmet le **contrat vendu et le système de protection**, pas seulement les pièces de prix.

## 15.1 Paquet minimal

- version contractuelle acceptée ;
- prix/budget autorisé selon droits ;
- hypothèses ;
- exclusions/réserves ;
- engagements vendus ;
- partenaires retenus ;
- contraintes capacité/logistique ;
- HSE/prérequis ;
- environnement/social ;
- sanctions significatives ;
- dérogations sensibles ;
- OS/change rules ;
- calendrier de préservation des droits ;
- circuit paiement ;
- réception/DGD/garanties ;
- conditions GO non encore closes ;
- points `REVIEW_REQUIRED`.

## 15.2 Acceptation

P7 ne signifie pas « tout est sans risque ».

Il signifie que :

- le paquet est identifiable ;
- les risques sont affectés ;
- les obligations critiques ont un responsable ;
- les droits temporels ont un propriétaire ;
- les inconnus acceptés restent visibles.

---

# 16. Frontend / UX — impacts obligatoires

Le catalogue UX actuel conserve son autorité. Les nouveaux besoins doivent être absorbés sans créer une jungle de routes.

## 16.1 C05 — À résoudre

Ajouter des natures typées pour les nouveaux objets, selon le catalogue après révision propriétaire :

- dérogation ;
- sanction ;
- droit/échéance ;
- assurance à confirmer ;
- prérequis HSE ;
- engagement mesurable ;
- autorisation tierce.

Une tâche fermée ne ferme pas l’objet source.

## 16.2 C07 — Décision

La carte P2/P3/P4 doit pouvoir afficher :

- impacts contractuels ;
- sanctions ;
- risque de forclusion futur ;
- conditions assurance ;
- règles réglementaires applicables ou à revoir ;
- risques résiduels.

## 16.3 C08 — Prix

Intégrer sans exposer au Collaborateur non autorisé :

- coûts HSE ;
- coûts garanties ;
- coûts post-réception ;
- pénalités scénarisées ;
- mismatch révision/fournisseurs ;
- scénarios OS/modification ;
- cash timing paiement.

## 16.4 C10 — Réponse

Tout engagement mesurable du mémoire doit pouvoir être retrouvé et relié à :

- preuve ;
- coût ;
- responsable ;
- sanction éventuelle ;
- passation.

## 16.5 C12 — Résultat et passation

Ajouter une vue/section de **protection du contrat** plutôt qu’une nouvelle destination globale par défaut :

- échéances de droits ;
- OS/modifications ;
- règlement des comptes ;
- réception ;
- garanties ;
- engagements.

## 16.6 HOME Patron / Carte d’Engagement

L’accueil Patron peut afficher les décisions et conditions les plus critiques, mais pas une matrice exhaustive de 12 cartes KPI.

Respecter l’UX existante : décision d’abord, preuve à un geste, complexité à deux.

---

# 17. APIs et projections — règles de contrat

Aucune route concrète n’est imposée dans ce document avant audit du style API existant.

Les contrats publics doivent toutefois respecter :

1. `extra=forbid` ou équivalent strict côté commandes ;
2. réponse fermée ;
3. champs financiers absents du schéma Collaborateur, pas seulement `null` ;
4. permissions appliquées avant agrégation ;
5. source/version/locator sur les conclusions critiques ;
6. ETag/révision ou contrôle de concurrence approprié ;
7. idempotence pour actions sensibles ;
8. codes d’erreur métier stables ;
9. aucun message révélant l’existence d’une ressource d’un autre tenant ;
10. dates ISO 8601 avec timezone explicite ;
11. money/unit explicitement typés ;
12. pagination/filtrage bornés.

## 17.1 Projections

Créer des read models spécialisés si nécessaire plutôt que permettre au frontend de joindre des tables métier.

Exemples conceptuels :

- Carte d’Engagement ;
- calendrier des droits ;
- exposition sanctions ;
- profil réglementaire ;
- couverture des engagements ;
- passation P7.

Ces projections n’acquièrent aucune autorité de mutation.

---

# 18. Migrations et stratégie de données

## 18.1 Règle générale

Migration additive d’abord.

Séquence recommandée :

1. nouvelles structures vides ;
2. contraintes minimales sûres ;
3. code d’écriture derrière feature flag interne si besoin ;
4. backfill à partir de données réellement mappables ;
5. comparaison ancien/nouveau ;
6. bascule lecture ;
7. durcissement des contraintes ;
8. suppression éventuelle bien plus tard, après preuve.

## 18.2 Backfill

Interdit d’inventer :

- applicability ;
- dates de droits ;
- version de CCAG ;
- plafond de pénalités ;
- assurance couverte ;
- état de réception ;
- engagement satisfait.

Les enregistrements historiques insuffisants deviennent `UNKNOWN` / `REVIEW_REQUIRED`.

## 18.3 Réversibilité

Chaque PR de migration documente :

- forward ;
- rollback code ;
- rollback data possible/impossible ;
- données non destructibles ;
- point de restauration ;
- compatibilité version N/N-1 si déploiement progressif.

---

# 19. Observabilité et audit métier

## 19.1 Événements à journaliser

Sans secrets ni contenu excessif :

- création/revue d’une applicability ;
- qualification d’une dérogation ;
- changement d’une règle de sanction ;
- calcul/recalcul d’une échéance ;
- preuve d’envoi/réception ;
- acceptation/rejet d’un risque ;
- changement de couverture assurance ;
- validation d’un engagement ;
- modification de condition GO ;
- construction/acceptation de passation.

## 19.2 Corrélation

Toute opération longue ou multi-module conserve `correlation_id`.

## 19.3 Métriques techniques

- taux d’objets `REVIEW_REQUIRED` ;
- erreurs de parsing de clauses ;
- recalculs après rectificatif ;
- temps de projection ;
- dead letters/outbox ;
- conflits de concurrence ;
- retries idempotents ;
- erreurs d’autorisation ;
- résultats inconnus externes ;
- taux d’abstention IA sur classes critiques.

Ces métriques ne sont pas des KPI marketing sans protocole de mesure métier.

---

# 20. Failure modes et reprise

## 20.1 Panne IA

- documents restent accessibles ;
- règles déterministes continuent ;
- saisie/revue manuelle disponible ;
- aucune conclusion IA ancienne n’est présentée comme fraîche ;
- tâches en attente explicites.

## 20.2 Source réglementaire indisponible

- conserver dernière règle validée avec date ;
- ne pas inventer une mise à jour ;
- afficher stale/review due ;
- nouvelles décisions sensibles peuvent exiger revue humaine.

## 20.3 Import DCE partiel

- ne pas déclencher « dossier complet » ;
- conclusions touchées marquées partielles ;
- Carte d’Engagement signale la couverture de lecture.

## 20.4 Conflit utilisateur

- préserver les contributions ;
- demander arbitrage ;
- jamais écraser silencieusement une décision ou un événement de droit.

## 20.5 Timeout externe

- `UNKNOWN_OUTCOME` ;
- pas de retry aveugle pour action non idempotente ;
- réconciliation avant nouvelle tentative.

---

# 21. Tests — contrats obligatoires

Les tests sont des contrats métier. Tout bug critique reçoit un test de régression.

## 21.1 Test matrix générale

Pour chaque capacité C1 :

- nominal ;
- refus ;
- permission ;
- autre tenant ;
- donnée absente ;
- donnée expirée ;
- version ancienne ;
- rectificatif ;
- retry ;
- idempotence ;
- concurrence ;
- timeout ;
- panne ;
- reprise ;
- résultat inconnu ;
- audit ;
- rollback/migration si applicable.

## 21.2 Recettes métier REC-29 à REC-45

### REC-29 — versions contractuelles différentes

Deux Affaires comparables référencent des versions contractuelles différentes. Le système n’applique pas le même délai par défaut ; chaque conclusion cite sa règle/version.

### REC-30 — dérogation au régime de pénalités

Une clause particulière déroge à la règle de référence. Le plafond générique n’est jamais affiché comme applicable sans qualification.

### REC-31 — OS non valorisé

Instruction supplémentaire sans prix : aucun coût nul/inclus n’est inventé ; action de revue et préservation ouverte.

### REC-32 — décompte / délai de réclamation

La réception d’un décompte crée l’événement de droits uniquement si règle et trigger sont établis ; destinataires et preuve sont conservés.

### REC-33 — exécution aux frais et risques

L’exposition est rendue visible et scénarisable sans conclure automatiquement à la validité juridique de la clause.

### REC-34 — engagement environnemental vendu

Une promesse mesurable du mémoire devient engagement relié au coût, preuve, responsable et passation.

### REC-35 — règle réglementaire par date/usage

Deux projets proches mais avec dates/usages différents n’obtiennent pas la même applicability si le champ de la règle diffère.

### REC-36 — RAT infrastructure

Projet d’infrastructure concerné : le système demande/qualifie l’information sans le confondre avec un autre régime documentaire.

### REC-37 — assurance hors activité déclarée

Attestation présente mais libellé insuffisant : interdiction de conclure `COVERED` sans revue appropriée.

### REC-38 — prérequis HSE sans ressource

Exigence détectée, ressource/compétence absente : P2/P3 reste sous condition ou revue ; aucun « conforme ».

### REC-39 — circuit de facturation public

Une situation de travaux publique conserve son circuit propre ; pas de routage naïf vers le flux B2B standard.

### REC-40 — règle future

Une règle publiée avec date d’effet future reste inactive sur une Affaire antérieure ; aucune alerte bloquante prématurée.

### REC-41 — DGD tacite sous conditions

Le système ne conclut à un DGD tacite que si chaque condition de la règle contractuelle applicable, ses dates déclenchantes et ses preuves de notification sont établies. Sinon, état `REVIEW_REQUIRED` et avis humain.

### REC-42 — pénalités cumulatives

Deux sanctions potentiellement cumulables conservent chacune sa source, sa formule et sa dérogation ; aucune addition ni plafond universel n'est affirmé sans qualification de leur régime commun.

### REC-43 — engagement non chiffré dans le mémoire

Une promesse mesurable de l'offre sans coût, capacité ou responsable ne devient pas un engagement couvert. P4 expose l'écart et demande une décision Patron sourcée.

### REC-44 — trésorerie de portefeuille

Plusieurs gains simultanés confrontent ressources, garanties et pic de trésorerie sans transformer une prévision ou un scénario en financement acquis ; si la fonction portefeuille reste différée, son absence est visible.

### REC-45 — rectificatif modifiant délai ou droit

Un rectificatif touchant une clause temporelle invalide les seules conclusions et échéances dépendantes, conserve l'ancienne version et exige une requalification avant tout affichage de délai certain.

## 21.3 Recettes techniques supplémentaires

### TECH-CR-01 — isolation tenant

Créer deux Affaires mêmes identifiants métier dans tenants distincts. Aucun read model, recherche, IA ou export ne croise les données.

### TECH-CR-02 — fuite financière par projection

Responsable non autorisé appelle toutes les projections Carte d’Engagement. Aucun montant, existence de marge, total, compteur ou inférence financière interdite n’est exposé.

### TECH-CR-03 — retry deadline

Deux retries identiques d’un événement déclencheur créent un seul événement de droits.

### TECH-CR-04 — conflit de règle

Une règle réglementaire est supersédée pendant qu’un utilisateur édite une applicability. Le commit ancien est refusé ou requalifié ; aucune décision basée silencieusement sur une version obsolète.

### TECH-CR-05 — rectificatif DCE

Une nouvelle version du CCAP touche une dérogation et une pénalité. Seuls les objets dépendants sont invalidés ; historique conservé.

### TECH-CR-06 — formule ambiguë

Parser ne peut pas normaliser une formule : aucun chiffre n’est inventé, `FORMULA_REVIEW_REQUIRED`.

### TECH-CR-07 — prompt injection

Un CCAP contient une instruction visant le modèle. Le contenu reste data ; aucun outil ni permission élargi.

### TECH-CR-08 — clôture tâche ≠ clôture droit

Tâche « rédiger réserve » terminée ; événement de droits reste ouvert tant que preuve d’envoi/revue requise manque.

### TECH-CR-09 — envoi ≠ réception

Preuve d’envoi enregistrée sans accusé : état ne devient pas `ACKNOWLEDGED`.

### TECH-CR-10 — rollback

Migration ajoute les nouvelles tables/colonnes ; rollback applicatif n’endommage pas les événements historiques.

---

# 22. Golden DCE / corpus de qualification technique

Le corpus doit intégrer des cas hostiles, pas seulement des PDF propres.

Familles minimales :

- marché travaux public simple ;
- multi-lots avec interfaces ;
- réhabilitation site occupé ;
- hôpital/ERP sensible ;
- infrastructure/VRD/réseaux ;
- maintenance multi-sites/accord-cadre ;
- dossier privé ;
- nombreux rectificatifs ;
- vieux scans/tableurs/archives ;
- marché avec clauses particulières fortes.

Annotations supplémentaires v2.0 :

- règle de référence ;
- dérogation ;
- sanction ;
- trigger/délai ;
- engagement mesurable ;
- HSE/prérequis ;
- assurance à revoir ;
- données MIRP manquantes ;
- conséquences prix/capacité ;
- éléments P7.

Le benchmark mesure séparément extraction, locator, qualification et décision humaine. Un bon résultat final obtenu avec une mauvaise source n’est pas accepté.

---

# 23. Plan de construction proposé après audit

Aucune tranche ne démarre en écriture avant validation de l’audit et du statut produit correspondant.

## T0 — Audit de traçabilité et caractérisation

Objectifs :

- inventaire réel ;
- mapping MASTER → code ;
- tests caractérisation ;
- dette/écarts ;
- plan migration ;
- aucun nouveau comportement visible.

**Gate T0 :** aucune divergence critique non comprise.

## T1 — Fondation preuve/applicabilité

- réutiliser Source/Evidence existants ;
- regulatory profile minimal ;
- rule store versionné ;
- applicability ;
- invalidation ciblée ;
- tests multi-tenant.

**Gate :** aucune règle IA autoritative.

## T2 — Contrat et dérogations

- baseline contractuelle ;
- hiérarchie ;
- dérogations ;
- projections ;
- revue humaine.

## T3 — Sanctions et préservation des droits

- sanctions ;
- simulateur déterministe ;
- RightPreservationEvent ;
- calendrier ;
- idempotence ;
- preuves envoi/réception.

**Gate :** REC-29 à REC-33 verts.

## T4 — OS / modifications / règlement des comptes

- change instruction ;
- nouveau prix/hypothèse ;
- règlement ;
- réception ;
- DGD ;
- résiliation exposure.

## T5 — Assurance / HSE / engagements / paiement

- assurance assessment ;
- execution prerequisites ;
- measurable commitments ;
- payment circuit ;
- post-reception obligations.

## T6 — Carte d’Engagement Patron

Projection uniquement après stabilisation des sources.

Aucune logique métier dans le frontend.

## T7 — Passation P7 renforcée

- paquet figé ;
- calendrier de droits ;
- engagements ;
- risques ;
- responsables ;
- acceptation études/travaux.

## T8 — REX et calibration

- prévu/réalisé ;
- sanctions réelles ;
- obligations post-réception ;
- erreurs de préparation ;
- capitalisation contextualisée.

---

# 24. Plan de PR Codex — règles

Chaque PR doit être petite, cohérente et réversible.

## 24.1 Interdits

- PR « refonte métier » massive ;
- migration + refactor global + nouvelle UX dans le même PR ;
- renommage cosmétique de dizaines de modules pendant une migration métier ;
- nouvelle dépendance sans justification ;
- microservice ;
- event sourcing global ajouté par dogme ;
- moteur de règles externe sans benchmark/besoin ;
- vector DB différente uniquement pour « moderniser » ;
- secrets/test fixtures sensibles.

## 24.2 Forme d’une PR

Chaque PR indique :

- besoin métier ;
- invariant ;
- état actuel vérifié ;
- choix technique ;
- alternatives rejetées ;
- schéma/migration ;
- droits ;
- concurrence/idempotence ;
- observabilité ;
- tests ;
- rollback ;
- limites ;
- lien de traçabilité MASTER.

## 24.3 Séquence préférée

1. tests de caractérisation ;
2. contrat domaine ;
3. migration additive ;
4. repository/port ;
5. service applicatif ;
6. policy ;
7. API/projection ;
8. UI ;
9. e2e ;
10. doc/preuve.

---

# 25. Dépendances et choix technologiques

## 25.1 Principe

Le présent cahier n’autorise aucune dépendance nouvelle par défaut.

Pour chaque besoin, priorité :

1. standard library / capacités existantes ;
2. dépendance déjà présente ;
3. petite dépendance mature et justifiée ;
4. composant lourd uniquement avec benchmark et rollback.

## 25.2 Moteur de règles

Avant toute bibliothèque : démontrer que les règles validées ne peuvent pas être exprimées par le domaine existant et des prédicats testables.

## 25.3 Calendriers juridiques

Avant toute lib : inventorier les règles réelles nécessaires. Les jours ouvrés/feriés, fuseaux et conventions ne doivent pas être supposés universels.

## 25.4 Document parsing

Conserver la stratégie benchmark-first de l’architecture v3.1. Les nouveaux besoins de locators/tableaux/plans doivent être mesurés sur corpus.

---

# 26. Critères de performance

Aucun objectif de performance n’autorise une perte de preuve ou de sécurité.

À mesurer :

- ouverture Carte d’Engagement ;
- requêtes contrat/droits ;
- recalcul après rectificatif ;
- pagination sanctions/engagements ;
- recherche sourcée ;
- ingestion gros DCE ;
- génération des projections ;
- jobs de veille/règles.

Le document ne fixe pas de SLA chiffré inventé. Codex doit établir baseline puis objectif avec mesures.

---

# 27. Exploitation, sauvegarde et reprise

Les nouveaux objets font partie des données critiques à sauvegarder :

- règles validées utilisées dans des décisions ;
- versions contractuelles ;
- événements de droits ;
- preuves d’envoi/réception ;
- décisions ;
- passations ;
- événements append-only.

Une restauration doit préserver les liens vers les documents/hash correspondants.

Le runbook préproduction reste l’autorité opérationnelle à compléter séparément ; ce cahier ne le remplace pas.

---

# 28. Confidentialité, RGPD et conservation

## 28.1 Minimisation

Ne stocker que ce qui est nécessaire à la finalité métier.

Les appréciations partenaires/personnes doivent être :

- factuelles ;
- sourcées ;
- restreintes ;
- revues ;
- conservées selon durée justifiée.

## 28.2 Données juridiques/sensibles

Une consultation d’un conseil externe peut être restreinte à un paquet documentaire spécifique.

Ne pas exposer son contenu dans :

- recherche globale non autorisée ;
- embeddings accessibles à d’autres rôles ;
- logs ;
- analytics ;
- prompts génériques.

## 28.3 Suppression

La suppression physique ne doit pas casser l’intégrité d’un audit encore légalement/conventionnellement requis. Toute politique de purge autonome reste soumise aux décisions produit/juridiques dédiées.

---

# 29. Menaces spécifiques et sécurité applicative

## 29.1 Prompt injection réglementaire/contractuelle

DCE, email, devis, norme, courrier et fichier tiers sont non fiables.

## 29.2 Formula injection tableur

Exports CSV/XLSX doivent neutraliser les formules dangereuses selon le format et les conventions d’export retenues.

## 29.3 Archives

ZIP bombs, path traversal, macros, formats protégés : pipeline quarantine/fail-closed existant à maintenir.

## 29.4 SSRF / URLs de sources

Une URL trouvée dans un DCE ne doit pas être fetchée automatiquement par un service privilégié sans politique/allowlist adaptée.

## 29.5 IDOR / tenant

Tout nouvel endpoint de contrat/droits doit passer les mêmes tests d’isolation que le reste du système.

## 29.6 Export sensible

Un export Carte d’Engagement ou passation applique les droits au moment de l’export et indique sa portée ; il ne devient pas un moyen de contourner la classification.

---

# 30. Matrice de traçabilité MASTER métier → technique

| Domaine MASTER métier | Contrat technique v2.0 | Contexte principal | Gate |
|---|---|---|---|
| Carte d’Engagement | projection sourcée, 12 axes, sans score | Case/Decision + read models | T6 |
| Profil réglementaire | profile + rule store + applicability | Evidence/Regulatory | T1 |
| Éligibilité/preuves | Evidence/Enterprise validation | Evidence/Enterprise | existant + adapt |
| MIRP | InformationRequirement + evidence links | Evidence/Pricing | existant + adapt |
| Interfaces/coûts invisibles | Requirement/Risk/CostFactor | Evidence/Pricing | adapt |
| Marge/trésorerie | deterministic scenarios | Pricing | adapt |
| Portefeuille | Patron-only scenario projection | Pricing/Case | T5/T6 |
| Révision de prix | deterministic formula + indexes | Pricing/Contract | T3/T4 |
| Sous-traitance | partner evidence + obligations | Enterprise/Partner | adapt |
| Hiérarchie contractuelle | ContractBaseline | Contract & Rights | T2 |
| Dérogations | ContractDeviation | Contract & Rights | T2 |
| Pénalités | ContractSanctionRule + simulator | Contract/Pricing | T3 |
| Forclusion/droits | RightPreservationEvent | Contract & Rights | T3 |
| OS/modifications | ContractChangeInstruction | Contract & Rights | T4 |
| Résiliation/frais-risques | TerminationExposure | Contract & Rights | T4 |
| Réception/DGD | SettlementMilestone | Contract/Handover | T4/T7 |
| HSE | ExecutionPrerequisite | Evidence/Handover | T5 |
| Assurance | InsuranceCoverageAssessment | Enterprise/Evidence | T5 |
| Environnement/social | MeasurableCommitment | Response/Handover | T5 |
| Paiement | PaymentCircuit | Pricing/Handover | T5 |
| Post-réception | PostReceptionObligation | Handover | T5/T7 |
| Engagements mémoire | MeasurableCommitment + artifact link | Response | adapt/T5 |
| Dépôt | manifest/hash/evidence | Submission | existant |
| BAFO/mise au point | version/supersession + P6 | Decision/Response | adapt |
| Attribution/rejet | result + evidence | Handover/Learning | adapt |
| Passation | frozen handover package | Handover | T7 |
| REX | contextualized observed outcomes | Learning | T8 |
| IA/provenance | retrieval + structured candidates + abstention | AI Runtime | transversal |

---

# 31. Écarts déjà visibles avec le Cahier technique v1.0

Le v1.0 n’est pas faux ; il est **insuffisamment expressif** pour la profondeur v2.0.

## Couvert correctement

- monolithe modulaire ;
- tenant ;
- identity/MFA ;
- DCE ;
- source/version/hash/locator ;
- décision ;
- pricing ;
- préparation/remise ;
- append-only ;
- idempotence ;
- RAG borné ;
- tests ;
- déploiement.

## À étendre

- `decision` doit pouvoir consommer risques/conditions de Contract & Rights sans les posséder ;
- `pricing` doit intégrer les coûts contractuels/HSE/post-réception ;
- `handover` doit transmettre calendrier de droits et règlement des comptes ;
- `enterprise` doit enrichir assurance et partenaires ;
- `evidence` doit porter applicability réglementaire ;
- projections UX doivent intégrer Carte d’Engagement.

## Absent ou non explicite

- rule store réglementaire ;
- baseline/dérogation contractuelle ;
- penalty rule model ;
- rights preservation ;
- OS/change instruction ;
- DGD/settlement milestones ;
- termination exposure ;
- insurance coverage assessment ;
- execution prerequisites HSE ;
- measurable commitments ;
- payment circuit ;
- post-reception obligations.

---

# 32. Critères d’acceptation avant implémentation C1

Le développement C1 ne commence que si :

1. MASTER métier v2.0 est arbitré ou les sections autorisées sont explicitement identifiées ;
2. Product Freeze est mis à jour ou un ADR produit relié autorise le delta ;
3. audit T0 terminé ;
4. modèle existant mappé ;
5. aucune duplication d’autorité non résolue ;
6. droits/tenants définis ;
7. stratégie migration définie ;
8. Golden DCE contient des cas représentatifs ;
9. validations externes nécessaires identifiées ;
10. rollback documenté.

---

# 33. Critères d’acceptation avant exposition commerciale

Une fonction n’est pas commercialisable parce qu’elle existe en UI.

## Pénalités

Nécessite corpus annoté, précision/recall, calcul reproductible, faux positifs mesurés, revue juridique des cas sensibles.

## Préservation des droits

Nécessite versions contractuelles testées, calendriers/destinataires, timezones, cas de forclusion, preuve d’envoi/réception et revue juriste commande publique/construction.

## Assurance

Nécessite validation courtier/assureur des états et wording.

## Réglementation

Nécessite workflow de veille, date d’effet, supersession, applicability et absence d’activation prématurée.

## HSE

Nécessite validation QSE et cas réels.

## Carte d’Engagement

Nécessite tests utilisateurs Patron et absence de fuite financière.

---

# 34. Rollback stratégique

Si une nouvelle couche s’avère insuffisamment fiable :

- conserver les données source ;
- désactiver la projection/automatisation ;
- revenir à `REVIEW_REQUIRED` + workflow manuel ;
- ne jamais effacer l’historique pour masquer une régression ;
- maintenir la possibilité de produire la réponse/déposer selon le flux V1 lorsque la fonction nouvelle n’est pas indispensable.

Le fallback manuel fait partie du design, pas d’un plan de secours improvisé.

---

# 35. Questions ouvertes / validations externes

Les décisions suivantes ne doivent pas être tranchées par Codex seul :

- sémantique finale des règles CCAG/privé ;
- couverture du corpus privé ;
- wording assurance ;
- règles HSE par corps d’état ;
- MIRP métier ;
- délais/formalismes à encoder comme règles validées ;
- politique de conservation juridique ;
- source et licence des normes/DTU ;
- modalités d’intégration réglementaire automatisée ;
- seuils de risque économique propres à chaque entreprise.

Codex peut préparer les structures et tests, pas créer l’autorité métier manquante.

---

# 36. Instructions de travail à donner à Codex

```text
MISSION
Mettre SMART_AO en capacité de refléter le Cahier Directeur Métier MASTER v2.0,
sans rewrite, sans invention et sans transformer le code en autorité produit.

PHASE 1 — READ ONLY
- lire Product Freeze v2.0 actif, MASTER métier v2.0 et présent Cahier technique v2.1,
  architecture v3.1, catalogue UX, fondations UX et plan global ;
- inventorier le code et les migrations ;
- produire la matrice KEEP/ADAPT/REPLACE/DELETE/ABSENT ;
- produire les écarts et risques ;
- identifier les tests existants ;
- ne modifier aucun cœur métier.

PHASE 2 — PLAN
- proposer la plus petite migration cohérente ;
- séparer domaines, projections et UI ;
- détailler droits, données, idempotence, concurrence, observabilité et rollback ;
- découper en PR indépendantes ;
- chaque PR doit avoir ses tests et critères d’acceptation.

PHASE 3 — IMPLEMENTATION
Uniquement après autorisation propriétaire/technique :
- additive first ;
- tests avant refactor critique ;
- un bug = test de régression ;
- aucun état UNKNOWN/PARTIAL/REVIEW_REQUIRED converti en succès ;
- aucune donnée financière dans un contrat Collaborateur ;
- aucune règle réglementaire ou juridique créée par LLM ;
- aucune suppression historique silencieuse ;
- aucun secret dans Git/log/test/prompt.

STOP CONDITIONS
- contradiction entre MASTER et Product Freeze non arbitrée ;
- migration destructive sans rollback ;
- règle métier non sourcée ;
- état de permission ambigu ;
- absence de preuve pour une conclusion critique ;
- besoin de nouvelle dépendance structurante non benchmarkée.
```

---

# 37. Livrable de sortie attendu de Codex après l’audit

Codex doit produire un rapport structuré :

```text
1. EXECUTIVE VERDICT
2. CURRENT STATE VERIFIED
3. MASTER v2 TRACEABILITY
4. MISSING DOMAIN CONTRACTS
5. DATA MODEL DELTA
6. AUTHORIZATION DELTA
7. AI/RAG DELTA
8. FRONTEND/API DELTA
9. MIGRATION PLAN
10. TEST PLAN
11. OBSERVABILITY PLAN
12. SECURITY REVIEW
13. PR SEQUENCE
14. ROLLBACK
15. BLOCKERS / OWNER DECISIONS
```

Pour chaque constat :

`VERIFIED / PROBABLE / HYPOTHESIS / PROPOSAL / TO_TEST`.

---

# 38. Références documentaires

## Autorités actuelles du dépôt

- `docs/00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v2.0.md`
- `docs/00_REFERENCE_ACTIVE/SMART_AO_Catalogue_Ecrans_Parcours_Produit_OWNER_CONSOLIDATED_v0.3.md`
- `docs/00_REFERENCE_ACTIVE/SMART_AO_Prototype_UX_V0_Fondations_OWNER_CONSOLIDATED_v0.3.md`
- `docs/01_IMPLEMENTATION_ACTIVE/SMART_AO_Architecture_Logicielle_v3.1_REFERENCE_DIRECTRICE_PHASE0.md`

## Technique

- `docs/02_FUTURE_TECHNICAL/SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v2.1.md` — baseline remplacée par le présent candidat une fois accepté ;
- `docs/03_PRODUCT_DESIGN_WORKING/realignment_v2_audit/MASTER_V2_TRACEABILITY_MATRIX.md` — traçabilité initiale v2 ;
- `docs/02_FUTURE_TECHNICAL/SMART_AO_PREPRODUCTION_VPS_RUNBOOK_v0.1.md` — exploitation, non remplacé ;
- `docs/02_FUTURE_TECHNICAL/SMART_AO_EXP_01_CAHIER_TECHNIQUE_EXECUTION_v0.1.md` — tranche spécifique, non remplacée globalement.

## Nouvelles autorités candidates

- `docs/00_REFERENCE_ACTIVE/SMART_AO_CAHIER_DIRECTEUR_METIER_MASTER_v2.0.md` — profondeur métier ;
- `docs/00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v2.0.md` — contrat produit actif ;

---

# 39. Décision technique proposée

**DÉCISION APPLIQUÉE :** ce document est la référence `SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v2.1.md` après promotion du Product Freeze v2.0.

Il ne remplace pas l’architecture v3.1 ; il la **spécifie davantage** à partir du nouveau métier.

Il ne remplace pas le catalogue UX ; il expose les nouveaux contrats que le catalogue devra absorber.

Il ne remplace pas le Product Freeze ; il dépend de sa mise à jour.

Il ne donne pas à Codex le droit d’inventer les règles métier manquantes.

La cible reste :

> **un logiciel où chaque conclusion importante peut revenir à sa source, chaque risque à sa conséquence, chaque décision à son autorité, chaque calcul à ses hypothèses, chaque échéance à sa règle, et chaque engagement au contrat réellement vendu.**

---

# 40. Verdict final

Le cahier technique v1.0 était adapté à un SmartAO centré sur DCE, décision, prix, réponse et remise.

Le MASTER métier v2.0 transforme la profondeur attendue : SmartAO doit maintenant être capable de représenter et sécuriser non seulement **ce que l’entreprise répond**, mais **ce qu’elle accepte, ce qu’elle devra exécuter, ce qu’elle devra prouver, les droits qu’elle devra préserver et la façon dont la marge peut se dégrader après attribution**.

La réponse technique n’est pas un rewrite. Elle est l’ajout discipliné de contrats de domaine, de temporalité, d’applicabilité et de preuve au monolithe modulaire existant.

La règle de construction reste :

> **audit réel → petite migration cohérente → tests contractuels → preuve → seulement ensuite extension.**

**Fin — SMART AO Cahier technique d’exécution v2.1 — 24 septembre 2026.**
