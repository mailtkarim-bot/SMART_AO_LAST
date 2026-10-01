# SMART AO — Cahier directeur Produit & Métier
## OWNER FREEZE v3.0 — CANDIDAT DE RÉOUVERTURE PROPRIÉTAIRE

**Date : 30 septembre 2026**  
**Statut : CANDIDAT DE RÉOUVERTURE PROPRIÉTAIRE — NE REMPLACE PAS L’AUTORITÉ ACTIVE AVANT PROMOTION EXPLICITE**  
**Question couverte : « Quel SMART AO devons-nous construire maintenant pour rester utile, défendable et différencié face à l’évolution du marché ? »**

---

# 0. RÈGLE DE RÉOUVERTURE

Cette V3 ne nie pas V2. Elle en change le centre de gravité.

V2 avait correctement élargi SMART AO :

- DCE ;
- décision ;
- économie ;
- capacité ;
- contrat/dérogations ;
- sanctions ;
- préservation des droits ;
- OS/modifications ;
- paiement ;
- réception/DGD ;
- assurance/HSE ;
- passation ;
- REX.

V3 ajoute une décision structurante :

> **ces fonctions ne doivent plus être développées comme une collection de registres ou d’analyses. Elles doivent former une chaîne causale gouvernée qui suit l’engagement réel de l’Affaire.**

Le nouveau centre produit est l’**Engagement Control Graph**.

Le mot Graph désigne le réseau de relations métier ; il ne choisit aucune technologie.

---

# 1. QUESTION FONDAMENTALE V3

SMART AO doit permettre au Patron de répondre de manière défendable :

> **Cette affaire mérite-t-elle notre engagement ; que nous fait-elle réellement accepter ; qu’est-ce qui peut consommer notre marge, notre trésorerie, notre capacité ou nos droits ; comment devons-nous l’exécuter ; et que devons-nous faire, prouver ou décider si la réalité change ?**

La question ne s’arrête plus à la remise.

Elle couvre :

```text
opportunité
→ DCE
→ compréhension
→ prix/capacité
→ décision
→ offre
→ autorisation
→ attribution/mise au point
→ passation
→ événement contractuel
→ paiement/réception
→ clôture
→ REX
```

SMART AO n’est pas un ERP chantier. Il conserve uniquement les événements d’exécution nécessaires pour relire, protéger et apprendre l’engagement initial.

---

# 2. CATÉGORIE PRODUIT

## 2.1 Positionnement principal

SMART AO est :

> **un système de maîtrise des engagements BTP pour PME, centré sur l’Affaire, la preuve, l’autorité humaine et la continuité entre DCE, décision, offre, contrat et exécution.**

## 2.2 Ce qu’il n’est pas

SMART AO n’est pas :

- un chatbot de DCE ;
- un générateur générique de mémoire ;
- un logiciel de chiffrage complet ;
- un ERP chantier ;
- un avocat automatique ;
- un moteur de conformité qui rend des conclusions juridiques autonomes ;
- un score Go/No-Go ;
- un portail de dépôt automatique en V1/V3 initial ;
- une base de normes copiées illicitement ;
- un agent autonome qui engage l’entreprise.

## 2.3 Formulation commerciale candidate

> **Avant de signer, SMART AO montre ce que l’Affaire engage. Après attribution, il conserve ce que l’entreprise doit tenir, protéger et prouver.**

Autre formulation :

> **Le DCE dit ce que le marché demande. SMART AO montre ce que cela devient pour votre entreprise — avant et après la signature.**

---

# 3. DOCTRINE DE PARITÉ ET DE DIFFÉRENCIATION

## 3.1 PARITY CORE

Les capacités suivantes restent obligatoires mais ne pilotent plus la différenciation :

- veille ;
- ingestion ;
- OCR/parsing ;
- résumé ;
- recherche ;
- extraction ;
- exigences ;
- contradictions ;
- versioning ;
- provenance ;
- mémoire technique ;
- administratif ;
- prix importé ;
- Go/No-Go de premier niveau ;
- Enterprise Memory.

Règle :

> elles doivent être suffisamment bonnes pour ne pas faire perdre une vente, mais aucune roadmap majeure ne leur est consacrée sans raison mesurée.

## 3.2 DEEP CORE

Le Deep Core est constitué de :

1. source/provenance/version ;
2. applicabilité ;
3. obligation/droit/dérogation/sanction ;
4. business impact ;
5. condition de décision ;
6. engagement vendu ;
7. événement réel ;
8. action/échéance ;
9. preuve ;
10. handover ;
11. règlement/clôture ;
12. REX.

## 3.3 DEFERRED

Sont différés :

- agents généralistes multiples ;
- graph DB imposée ;
- microservices ;
- dépôt autonome ;
- ERP chantier ;
- chiffrage natif complet ;
- couverture UX exhaustive comme séquence bloquante avant preuve de valeur ;
- fonctions “wow” sans impact mesuré sur décision, temps, erreur ou marge.

---

# 4. LES INVARIANTS V3

## 4.1 Absence de preuve

> **absence de preuve ≠ conformité ≠ zéro ≠ absence de coût ≠ absence de risque ≠ absence d’obligation ≠ absence de droit.**

## 4.2 Autorité

- l’IA propose ;
- le Collaborateur prépare ;
- l’Expert qualifie son domaine ;
- le Patron arbitre et engage ;
- le système conserve ce qui est établi et ce qui ne l’est pas.

## 4.3 Temporalité

Une règle ou conclusion critique porte :

- source ;
- version ;
- période d’effet ;
- portée ;
- applicability ;
- événement déclencheur ;
- éventuellement deadline ;
- état de validation.

## 4.4 Causalité

Un impact critique ne doit pas être orphelin.

Exemple :

```text
CCAP v4 art. 8.2
→ dérogation
→ pénalité spécifique
→ simulation
→ P3 condition
→ offre autorisée
→ retard réel
→ exposition actualisée
→ décision/action
```

## 4.5 Historique

Une rectification :

- n’efface pas ;
- supersède ou invalide ce qui dépend d’elle ;
- conserve la décision antérieure ;
- explique pourquoi une révision est nécessaire.

## 4.6 Prudence

Les états suivants sont de première classe :

- `UNKNOWN`
- `PARTIAL`
- `REVIEW_REQUIRED`
- `SOURCE_SIGNAL_ONLY`
- `NOT_PERFORMED`
- `NOT_ESTABLISHED`
- `NOT_APPLICABLE`
- `EXPIRED`
- `SUPERSEDED`

Aucun de ces états n’est un succès implicite.

---

# 5. ENGAGEMENT CONTROL GRAPH — MODÈLE CENTRAL

## 5.1 Objectif

Le système doit pouvoir expliquer une Affaire non par une liste de documents, mais par les relations entre ses faits et décisions.

## 5.2 Familles d’objets

### Source & preuve

- Source
- Document
- Version
- SourceReference
- Evidence

### Compréhension

- Requirement
- InformationRequirement / MIRP
- Unknown
- Hypothesis
- Contradiction
- RiskSignal
- ClarificationQuestion

### Applicabilité

- RegulatoryProfile
- RegulatoryRule
- ContractBaseline
- ContractRule
- ContractDeviation
- ApplicabilityAssessment

### Engagement

- Obligation
- Right
- ContractualSanction
- MeasurableCommitment
- ExecutionPrerequisite
- InsuranceCoverageAssessment
- ExternalDependency

### Impact

- CostImpact
- CashImpact
- ScheduleImpact
- CapacityImpact
- PartnerImpact
- HseImpact
- InsuranceImpact
- ContractImpact

### Décision

- Decision
- DecisionCondition
- Gate P0–P7
- HumanReview

### Offre / contrat vendu

- OfferCommitment
- SubmissionPackage
- Manifest
- Authorization
- AwardedScope
- AcceptedClarification

### Exécution contrôlée

- ChangeEvent
- ContractChangeInstruction / OS
- RightPreservationEvent
- SettlementEvent
- PaymentEvent
- ReceptionEvent
- PostReceptionObligation
- TerminationExposure

### Apprentissage

- Outcome
- DeviationObserved
- RexFinding
- ReuseScope

## 5.3 Relation minimale

Chaque objet critique doit pouvoir pointer vers :

- ses sources ;
- ses dépendances ;
- ses impacts ;
- son propriétaire ;
- son statut ;
- ses actions ;
- ses décisions ;
- ses versions.

---

# 6. CARTE D’ENGAGEMENT PATRON V3

La Carte d’Engagement reste la projection principale, mais elle devient **causale**.

Elle couvre au minimum :

1. intérêt commercial ;
2. éligibilité/candidature ;
3. technique ;
4. constructibilité/logistique ;
5. contrat/droits ;
6. prix/marge ;
7. cash/garanties ;
8. capacité/charge ;
9. partenaires ;
10. HSE/environnement/réglementaire ;
11. engagements/documentation/remise ;
12. exécution/événements/clôture.

Chaque ligne contient :

```text
objet
source/version
applicabilité
état
fait établi
inconnu
impact coût
impact cash
impact délai
impact capacité
impact droit/contrat
condition de décision
responsable
action
deadline
preuve attendue
décision Patron
risque résiduel
liens causaux
```

Aucun score global ne remplace cette structure.

---

# 7. LES PORTES P0–P7 SONT MAINTENUES

## P0 — Cibler

Décider si l’opportunité mérite une attention.

Ne pas confondre score de pertinence et décision.

## P1 — Ouvrir

Créer une Affaire avec provenance, lots, échéances et inconnus.

## P2 — GO de principe

Question :

> pouvons-nous raisonnablement envisager de répondre ?

Doit examiner :

- périmètre ;
- données critiques disponibles ;
- capacité générale ;
- assurance de principe ;
- profil réglementaire ;
- dépendances ;
- régime contractuel ;
- risques éliminatoires.

## P3 — GO économique / engagement

P3 devient la première grande sortie de la Verticale A.

Doit présenter :

- baseline contractuelle ;
- dérogations ;
- sanctions ;
- rights/obligations critiques ;
- hypothèses ;
- marge ;
- cash ;
- capacité ;
- fournisseurs ;
- HSE ;
- coûts post-réception ;
- conditions de GO ;
- inconnus résiduels.

Décision possible :

- GO ;
- GO sous conditions ;
- ATTENTE ;
- NO-GO ;
- ABANDON.

## P4 — Autoriser l’offre

Contrôler que ce qui est écrit/promis correspond à :

- prix ;
- moyens ;
- calendrier ;
- partenaires ;
- assurances ;
- engagements mesurables ;
- preuves ;
- conditions acceptées.

## P5 — Autoriser le paquet exact

Conserve le contrat V2 :

candidate → manifeste → contrôles → signatures → P5 → export → dépôt humain → preuve.

Toute modification substantielle invalide l’autorisation applicable.

## P6 — Accepter une clarification / négociation / mise au point

Toute modification doit être projetée sur :

- scope ;
- prix ;
- marge ;
- cash ;
- délai ;
- capacité ;
- assurance ;
- obligations ;
- droits ;
- engagements.

## P7 — Lancer l’exécution

P7 devient la sortie principale de la Verticale B.

La passation doit contenir :

- contrat réellement gagné ;
- offre réellement autorisée ;
- mise au point ;
- conditions de GO encore ouvertes ;
- engagements vendus ;
- hypothèses de prix ;
- obligations ;
- droits ;
- sanctions ;
- calendrier de préservation ;
- prérequis HSE ;
- assurance ;
- partenaires ;
- paiement ;
- réception ;
- responsables ;
- preuves attendues.

P7 n’est pas un ordre de service.

---

# 8. VERTICAL A — AVANT DE SIGNER

## 8.1 Objectif

Donner au Patron une lecture économique et contractuelle exploitable avant engagement.

## 8.2 Chaîne

```text
DCE
→ sources actives
→ contract baseline
→ deviations
→ obligations / rights / sanctions
→ applicability
→ impacts
→ hypotheses
→ conditions
→ P3
```

## 8.3 Sortie

La sortie doit pouvoir dire :

- ce qui est certain ;
- ce qui est probable ;
- ce qui manque ;
- ce qui peut coûter ;
- ce qui peut immobiliser du cash ;
- ce qui exige une ressource ;
- ce qui expose un droit ;
- ce que le Patron accepte ;
- sous quelles conditions.

## 8.4 Anti-pattern

Interdit :

> “Risque contractuel élevé : 82/100.”

Accepté :

> “Le CCAP v3 déroge au régime de pénalité X. Sur le scénario de retard R, l’exposition calculable est Y. Le plafond applicable n’est pas établi. P3 reste `GO_UNDER_CONDITIONS` jusqu’à revue C-17.”

---

# 9. VERTICAL B — SI NOUS GAGNONS

## 9.1 Objectif

Transformer l’offre gagnée en contrat d’exécution compréhensible.

## 9.2 AwardedScope

Le système doit reconstruire le périmètre réellement gagné à partir de :

- offre autorisée ;
- réponses ;
- négociation ;
- mise au point ;
- notification ;
- lot ;
- documents contractuels ;
- réserves.

## 9.3 Handover

Le chantier reçoit une **fiche d’engagement exécutable**, pas un résumé de l’offre.

Elle distingue :

- engagement contractuel ;
- engagement commercial ;
- hypothèse interne ;
- condition de GO ;
- obligation de preuve ;
- droit à préserver ;
- préférence non contractuelle.

---

# 10. VERTICAL C — QUELQUE CHOSE CHANGE

## 10.1 Événements

Au minimum :

- OS ;
- modification ;
- avenant ;
- instruction ;
- retard tiers ;
- indisponibilité ;
- changement planning ;
- quantité nouvelle ;
- prestation supplémentaire ;
- demande client ;
- réserve ;
- refus ;
- situation/paiement ;
- réception ;
- sinistre/assurance ;
- événement réglementaire pertinent.

## 10.2 Analyse delta

Le système ne doit pas seulement classer l’événement.

Il doit rapprocher :

```text
avant
vs
événement
vs
contrat applicable
vs
offre vendue
vs
conditions de GO
```

Puis calculer/proposer :

- différence de scope ;
- coût ;
- cash ;
- délai ;
- capacité ;
- partenaire ;
- assurance ;
- HSE ;
- droit/obligation ;
- deadline ;
- action ;
- preuve.

## 10.3 Limite juridique

SMART AO ne conclut pas :

> “vous avez juridiquement droit à X.”

Il conclut :

> “cet événement correspond à une situation configurée comme pouvant déclencher le mécanisme X selon les sources suivantes ; revue requise.”

---

# 11. CONTRACT BASELINE & DEVIATIONS

Le produit doit reconstruire le corpus réellement applicable.

Public et privé restent distincts.

Chaque `ContractRule` porte :

- source ;
- version ;
- hiérarchie ;
- portée ;
- effective period ;
- texte/résumé autorisé ;
- qualification ;
- validator.

Une dérogation porte :

- règle de référence ;
- source de dérogation ;
- nature ;
- effet proposé ;
- impact ;
- validation.

Aucune règle CCAG/standard/norme/licence n’est considérée universelle.

---

# 12. RIGHTS & OBLIGATIONS

## 12.1 RightPreservationEvent

Un droit potentiel ou une exigence de préservation porte au minimum :

- trigger ;
- source/version ;
- rule reference ;
- start fact ;
- deadline rule ;
- computed deadline ;
- addressee ;
- required form ;
- required content ;
- evidence of sending/receipt ;
- responsible ;
- status ;
- consequence ;
- review.

## 12.2 Interdiction

Aucun délai juridique n’est codé comme constante universelle simplement parce qu’il est fréquent.

---

# 13. SANCTIONS

Une sanction est un objet distinct d’un risque.

Champs métier :

- family ;
- trigger ;
- basis ;
- formula ;
- unit ;
- grace ;
- cap ;
- threshold ;
- cumulation ;
- derogation ;
- excuse mechanism ;
- dispute mechanism ;
- scenario ;
- source ;
- validation.

Sorties :

- central ;
- stress ;
- maximum contractually derivable si établi ;
- `NOT_ESTABLISHED` sinon.

---

# 14. ÉCONOMIE : PRIX, MARGE, CASH ET PORTFOLIO

SMART AO ne devient pas un logiciel de chiffrage complet.

Il contrôle et enrichit un chiffrage.

La décision économique distingue :

- marge ;
- cash ;
- capacité ;
- coût du risque ;
- coût post-réception ;
- garanties ;
- financement ;
- exposition portefeuille.

Tout impact contractuel structuré peut produire une projection économique.

Une projection ne remplace pas le fait source.

---

# 15. PAYMENT / SETTLEMENT / RECEPTION

Le paiement n’est pas une certitude issue d’une date contractuelle.

Le système modélise :

```text
prestation
→ situation/décompte
→ justificatifs
→ contrôle
→ validation/service fait
→ facture/plateforme
→ éventuel rejet/suspension
→ paiement attendu
→ paiement constaté
→ écart
```

Séparer :

- délai théorique ;
- date prudente ;
- date réelle ;
- source ;
- acteur ;
- preuve.

Réception, réserves, GPA, DOE/DIUO, DGD, garanties et clôture économique sont reliés, mais conservent leur nature.

---

# 16. ASSURANCE / HSE / ENVIRONNEMENT

## Assurance

Une attestation ≠ couverture.

États :

- `COVERED`
- `PROBABLY_COVERED`
- `NOT_ESTABLISHED`
- `OUTSIDE_DECLARED_ACTIVITY`
- `BROKER_REVIEW_REQUIRED`

## HSE

Transformer :

> obligation HSE

en :

> compétence + habilitation + matériel + délai + coût + preuve + disponibilité.

## Environnement/social

Tout engagement mesurable doit relier :

- source ;
- KPI ;
- valeur promise ;
- méthode ;
- fréquence ;
- preuve ;
- coût ;
- responsable ;
- partenaire ;
- sanction éventuelle.

---

# 17. ENTERPRISE MEMORY

La Mémoire Entreprise reste stratégique, mais ne doit pas devenir un simple RAG.

Chaque élément réutilisable porte :

- provenance ;
- scope ;
- validité ;
- sensitivity ;
- holder ;
- validator ;
- use history ;
- conditions de réemploi.

Le système distingue :

- fait entreprise ;
- préférence ;
- preuve tierce ;
- retour d’expérience ;
- règle interne ;
- hypothèse.

---

# 18. REX CAUSAL

Le REX ne doit pas se limiter à “gagné/perdu”.

Après clôture, comparer :

```text
ce que nous pensions
vs
ce que nous avons vendu
vs
ce qui s’est produit
vs
ce qui a coûté
vs
ce qui a protégé/perdu du temps ou des droits
```

Exemples de REX :

- hypothèse fournisseur invalidée ;
- clause sous-évaluée ;
- sanction réellement appliquée ;
- OS rentable/non rentable ;
- délai de paiement réel vs prudent ;
- ressource manquante ;
- engagement commercial trop ambitieux ;
- faux positif SmartAO ;
- risque manqué ;
- question acheteur qui aurait dû être posée.

Le REX n’est réutilisable qu’avec validation et portée.

---

# 19. UX V3

## 19.1 Les 104 surfaces restent un contrat de couverture

Elles ne sont plus une roadmap séquentielle qui bloque la validation métier.

## 19.2 Surfaces prioritaires V3

Priorité de prototypage :

1. Carte d’Engagement Patron ;
2. Vue Contract Baseline / Deviations ;
3. Vue Rights & Deadlines ;
4. Vue Impact causal ;
5. P3 GO sous conditions ;
6. P7 Handover ;
7. Change Event / OS ;
8. Settlement / Payment / Reception ;
9. REX causal.

## 19.3 “Une preuve à un geste”

Conserver la règle UX : source/locator/version visibles rapidement.

## 19.4 Navigation

Ne pas créer un menu par objet du Deep Core.

Les objets s’intègrent dans l’Affaire et ses vues.

---

# 20. CONFIDENTIALITÉ

Patron-only par défaut :

- prix d’achat ;
- coûts internes ;
- marge ;
- cash ;
- financement ;
- garanties sensibles ;
- notes Direction ;
- arbitrages confidentiels.

Un Collaborateur ne peut pas déduire une donnée Direction via :

- compteur ;
- recherche ;
- suggestion IA ;
- export ;
- notification ;
- audit ;
- cache ;
- endpoint agrégé.

---

# 21. IA ET OUTILS

L’IA est une couche de compréhension.

Les tools du domaine restent bornés.

Le contexte IA doit connaître :

- tenant ;
- rôle ;
- affaire/lot ;
- phase ;
- versions ;
- sources autorisées ;
- faits ;
- inconnus ;
- décisions ;
- actions interdites.

Le document externe reste data, jamais instruction système.

---

# 22. BENCHMARK V3

Le benchmark concurrentiel est désormais un gate.

## Corpus

Au minimum 3 dossiers réels autorisés/anonymisés pour la première campagne, puis Golden DCE élargi.

## Comparateurs

- SMART AO ;
- concurrents directs pertinents ;
- assistant généraliste.

## Mesures

- critical requirement recall ;
- critical contractual issue recall ;
- false critical alert rate ;
- source locator accuracy ;
- applicability accuracy ;
- causal impact linkage ;
- right/obligation trigger recall ;
- deadline correctness ;
- unknown preservation ;
- human review time ;
- Patron decision usefulness ;
- version invalidation correctness.

Aucune déclaration “meilleur” n’est autorisée sur la seule base du benchmark interne.

---

# 23. SCOPE V3 INITIAL

## MUST

- tout V2 déjà prouvé et compatible ;
- Engagement Control relations ;
- typed provenance ;
- Vertical A ;
- Vertical B ;
- Vertical C minimale ;
- rights/deadlines ;
- impacts déterministes ;
- P3/P7 renforcés ;
- payment/settlement prudent ;
- benchmark harness ;
- Golden DCE qualifié.

## SHOULD

- portfolio exposure ;
- partner cascades ;
- advanced post-reception ;
- regulatory overlays spécialisés.

## LATER

- connecteurs portails ;
- automation dépôt ;
- full native estimating ;
- ERP chantier ;
- advanced agent orchestration ;
- graph database si gain prouvé ;
- SSO avancé.

---

# 24. INDICATEURS PRODUIT

Ne pas piloter uniquement avec :

- nombre de features ;
- nombre de surfaces ;
- nombre de tests.

Piloter avec :

- risque critique détecté ;
- risque critique manqué ;
- temps économisé ;
- temps de revue ;
- nombre d’inconnus correctement préservés ;
- conditions P3 explicites ;
- conditions réouvertes après changement ;
- engagements correctement passés au chantier ;
- événements correctement reliés ;
- délais critiques protégés ;
- écarts cash/prix expliqués ;
- REX réutilisable.

---

# 25. CRITÈRE DE SUCCÈS V3

SMART AO réussit si, sur une Affaire réelle, un Patron peut répondre rapidement :

1. Pourquoi avons-nous décidé d’y aller ?
2. Qu’avons-nous considéré comme vrai ?
3. Qu’est-ce qui était encore inconnu ?
4. Qu’avons-nous promis ?
5. Qu’avons-nous accepté contractuellement ?
6. Qu’est-ce qui peut nous coûter ?
7. Quels droits/obligations sont temporels ?
8. Que devons-nous surveiller ?
9. Qu’est-ce qu’un nouvel événement change ?
10. Quelle preuve soutient chaque conclusion ?
11. Que transmettons-nous au chantier ?
12. Qu’avons-nous appris pour la prochaine affaire ?

---

# 26. RÈGLE DE PROMOTION

Cette V3 est candidate.

Avant promotion :

1. audit code T0 ;
2. comparaison avec Product Freeze actif ;
3. analyse des incompatibilités ;
4. impact UX ;
5. impact technique ;
6. impact tests/migrations ;
7. validation propriétaire.

Après promotion :

- l’index actif pointe sur V3 ;
- le cahier technique V3 devient sa traduction ;
- le plan global est recalé ;
- toute contradiction avec un ancien document est résolue par archivage/versionning explicite.

---

# 27. FORMULE DIRECTRICE

La formule à préserver dans toutes les décisions futures est :

> **Source → Applicabilité → Engagement → Impact → Décision → Événement → Action → Preuve → Apprentissage.**

Elle complète la formule historique :

> Source → Exigence → Impact → Décision → Preuve.

V3 ne détruit donc pas le produit antérieur.

Elle l’étend dans le temps jusqu’à la réalité de l’Affaire.
