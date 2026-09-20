# SMART AO — Cahier de conception fonctionnelle, parcours utilisateurs et expérience produit

**Version : 1.1 — 12 septembre 2026**  
**Statut : référence fonctionnelle stabilisée avant architecture logicielle**  
**Nom court : CCF-UX / Product Blueprint**

## 0. Rôle du document

Ce document constitue la couche intermédiaire entre les référentiels métier stabilisés et le futur cahier des charges technique.

Il répond à la question :

> **Comment SMART AO doit-il fonctionner concrètement pour ses utilisateurs, de la découverte d’une opportunité jusqu’au dépôt, puis jusqu’à la passation minimale vers l’exécution, sans devenir lourd ni imposer l’organisation d’un ERP ?**

Il transforme les exigences du **Cahier des charges métier v1.0** et de l’**Univers documentaire métier v1.0** en :

- architecture de l’information visible par l’utilisateur ;
- parcours par rôle ;
- vues et écrans ;
- états, transitions, alertes et verrous de décision ;
- règles d’ergonomie et de confidentialité ;
- interactions avec les sources d’opportunités ;
- principes de production et de contrôle documentaire ;
- critères d’acceptation fonctionnels et UX.

Il ne fixe volontairement **aucune architecture de code, aucun framework, aucune base de données, aucun découpage en microservices, aucun endpoint, aucun schéma ORM et aucun choix de fournisseur IA**. Ces sujets appartiendront au cahier des charges technique.

### 0.1 Sources de conception

Les sources normatives de ce CCF sont :

1. `SMART_AO_Cahier_des_charges_Metier_v1.0.md` ;
2. `SMART_AO_Univers_documentaire_metier_v1.0.md` ;
3. l’ancien `SMART_AO_VISION_METIER_PARCOURS_UTILISATEUR.md`, utilisé comme réservoir d’idées UX à conserver, corriger ou simplifier ;
4. les arbitrages explicites du propriétaire intervenus pendant la conception ;
5. les sources officielles utilisées pour la découverte des opportunités, notamment BOAMP et TED.

En cas de divergence, le cahier métier v1.0 et l’univers documentaire v1.0 priment sur l’ancien document de vision.

### 0.2 Évolutions structurantes de la v1.1

Cette version consolide la v1.0 sans modifier ses fondations métier. Elle ferme les angles morts qui auraient sinon été reportés à l’architecture : marchés privés, collaboration simultanée, reprise après erreur, cycle de vie des données, accessibilité, mesure de la confiance, formation à l’IA et protocole de validation par des professionnels BTP.

La v1.1 retient notamment :

1. SMART AO reste **AI-native dans l’expérience**, sans devenir un chatbot posé à côté du logiciel ;
2. l’utilisateur doit ressentir une **présence métier guidante** : briefing, prochaine action, explication, préparation et reprise de contexte ;
3. le modèle conversationnel agit à l’intérieur d’un **harnais fonctionnel SMART AO** : rôle, droits, contexte d’affaire, preuves, outils, politiques et validations humaines ;
4. l’IA peut être proactive pour signaler et préparer, mais reste bornée pour décider, signer, déposer, modifier une preuve tierce ou exposer une donnée confidentielle ;
5. l’**Affaire** reste le centre opérationnel du travail, tandis que la **Mémoire Entreprise** devient le socle privé et réutilisable des faits, documents, prix, moyens, personnes, références et preuves de la société ;
6. les données de l’entreprise ne deviennent jamais vraies parce qu’un LLM les a formulées : elles doivent provenir d’un document, d’une donnée structurée, d’un tiers ou d’une validation humaine explicite ;
7. la confidentialité patron/collaborateur devient une propriété fonctionnelle de la donnée elle-même, et pas seulement une différence d’écran ;
8. l’onboarding reste progressif : SMART AO doit pouvoir absorber une base existante en masse, proposer son classement et ses métadonnées, puis demander confirmation seulement lorsqu’elle est utile ou critique ;
9. les documents périodiques ou expirables doivent être suivis dans le temps et rapprochés des échéances réelles des affaires ;
10. l’expérience doit rester flexible : taxonomie commune minimale pour la sécurité, catégories et vocabulaire personnalisables pour respecter l’organisation de chaque PME ;
11. le marché privé dispose d’un parcours propre centré sur le contrat proposé, négocié puis accepté ;
12. le travail simultané, le remplacement d’un responsable et les conflits de modification ne doivent jamais faire perdre une contribution ;
13. chaque action engageante, erreur ou interruption possède un résultat visible et une voie de reprise ;
14. l’accessibilité devient une exigence testable dès le premier prototype ;
15. l’entreprise garde une vision compréhensible des accès, partages, conservations, exports et suppressions ;
16. la qualité est mesurée sur des tâches métier et des cas hostiles, pas sur le volume de contenu généré.

La v1.1 ne choisit aucun fournisseur de modèle, aucune API, aucun framework, aucun système de stockage ni aucune architecture d’agents. Elle spécifie le **contrat d’expérience** que la future architecture devra rendre possible.

### 0.3 Décision propriétaire de modèle de service transmise à l’architecture

Après stabilisation de l’expérience produit, le propriétaire a fixé une contrainte de service qui ne modifie pas les écrans mais influence directement la future architecture : **SMART AO sera exploité comme un SaaS avec environnement dédié par entreprise cliente, tout en conservant une application tenant-aware et un code produit unique.**

Cette décision est détaillée dans `SMART_AO_Registre_Decisions_Architecture_Preliminaires_v0.1.md`. Le CCF n’en choisit pas l’implémentation technique ; il transmet seulement les conséquences produit qui doivent rester vraies :

- la confidentialité Direction/Collaborateur ne repose pas sur le simple fait qu’un client soit seul sur son serveur ;
- les rôles, droits, organisations et délégations restent des invariants applicatifs ;
- une PME doit pouvoir exporter ses données et quitter SMART AO sans dépendre d’une base mutualisée opaque ;
- le produit doit rester standardisé : personnalisation par données et règles, pas par forks de code client ;
- la consommation IA et les coûts d’exploitation doivent pouvoir être attribués au client ;
- la cible commerciale initiale privilégie l’hébergement principal en France, avec cartographie explicite des flux externes ;
- aucun message commercial ne doit promettre une résidence ou une absence de transfert que l’architecture réelle ne peut pas démontrer.

---

# 1. Vision fonctionnelle consolidée

SMART AO doit être perçu comme un **poste de commandement métier des affaires BTP**, et non comme un chatbot, un générateur de mémoire technique ou un ERP généraliste.

Sa promesse fonctionnelle est :

> **Trouver les affaires pertinentes, comprendre ce qu’elles exigent, décider si elles méritent d’être poursuivies, organiser la réponse, protéger le prix et les engagements, constituer le bon dossier de remise et transmettre au chantier ce qui a réellement été vendu.**

Le centre de gravité de l’expérience n’est ni le document, ni l’IA, ni un module technique. Le centre opérationnel est **l’Affaire**.

Sous cette expérience existe un second pilier : la **Mémoire Entreprise**, c’est-à-dire le patrimoine privé, daté, validé et gouverné de la société. L’Affaire répond à « que devons-nous faire sur ce marché ? » ; la Mémoire Entreprise répond à « que savons-nous réellement sur notre propre entreprise et avec quelles preuves ? ».

Une affaire relie en permanence deux réalités :

- ce que l’acheteur demande ;
- ce que l’entreprise peut réellement prouver, produire, chiffrer et exécuter.

SMART AO doit rendre visibles les correspondances, les manques, les contradictions, les risques, les actions et les décisions entre ces deux réalités.

---

# 2. Décision fonctionnelle structurante : SMART AO doit aussi trouver les appels d’offres

## 2.1 Distinction essentielle : opportunités publiées vs signaux avant publication

Le cahier métier classe les signaux **avant publication** dans un horizon avancé. Cela reste correct.

En revanche, la **recherche des consultations déjà publiées** devient une fonction visible du produit initial. Un patron ne doit pas nécessairement utiliser un logiciel externe pour trouver un appel d’offres, puis venir seulement dans SMART AO pour l’analyser.

Le CCF distingue donc :

- **Radar des opportunités publiées — cœur visible dès la première expérience produit** ;
- **Intelligence commerciale avant publication — extension ultérieure** : permis, budgets, programmations, contrats sortants, signaux territoriaux, etc.

Ainsi, l’ajout de BOAMP ne remet pas en cause la priorisation métier des signaux amont : il crée une couche de **découverte des avis publiés** en amont immédiat de l’Affaire.

## 2.2 BOAMP comme source native prioritaire

SMART AO doit intégrer le BOAMP comme **source native prioritaire de découverte des marchés publics français**.

Le service officiel permet une interrogation et un filtrage par API, gratuitement et sous licence ouverte 2.0.[^1] L’interface fonctionnelle de SMART AO doit donc être capable de proposer des résultats régulièrement rafraîchis sans demander à l’utilisateur de quitter l’application.

BOAMP ne doit cependant jamais être présenté comme la totalité du marché français : selon les seuils et procédures, certains marchés peuvent être publiés sur d’autres supports. SMART AO doit afficher la provenance de chaque opportunité et ne jamais écrire « tous les appels d’offres français » lorsque la couverture n’est pas démontrée.

## 2.3 TED comme deuxième source publique native

Les avis européens publiés dans TED disposent d’une Search API ouverte destinée à la recherche et à la réutilisation des avis publiés.[^2] TED doit être prévu comme deuxième source publique native pour éviter une vision uniquement nationale des avis de niveau européen.

## 2.4 Sources ultérieures

Le modèle fonctionnel doit permettre d’ajouter ensuite, sans changer l’expérience utilisateur :

- autres sources publiques ou profils acheteurs disposant d’un accès licite ;
- sources spécialisées sous licence ;
- opportunités privées saisies par l’entreprise ;
- invitations reçues par e-mail ou transmises par un client ;
- signaux avant publication ;
- import CRM ou veille tierce.

L’utilisateur ne doit pas avoir à comprendre l’architecture des sources. Il voit **un Radar unique**, avec la source clairement indiquée sur chaque opportunité.

## 2.5 Ce que le Radar doit faire

Le Radar doit permettre au patron ou à un collaborateur autorisé de :

- rechercher des opportunités ;
- enregistrer des recherches ;
- recevoir des alertes ;
- filtrer par métier, lot, localisation, type de marché, acheteur, dates et autres critères disponibles ;
- voir pourquoi une affaire correspond à l’entreprise ;
- écarter une opportunité avec motif ;
- suivre une opportunité sans encore ouvrir une affaire ;
- demander une première qualification ;
- transformer l’opportunité en **Affaire** ;
- conserver la provenance et la date de découverte.

Le classement doit être explicable. SMART AO ne doit pas produire un « score magique de gain ».

## 2.6 Carte d’opportunité minimale

Une carte doit privilégier la lecture en dix secondes :

```text
OBJET : Réhabilitation énergétique — Groupe scolaire X
ACHETEUR : Ville de ...
SOURCE : BOAMP
LIEU : ...
TYPE : Travaux
DATE LIMITE : 03/10/2026 — 12:00
LOT PERTINENT : Lot 04 — CVC
POURQUOI CETTE AFFAIRE RESSORT :
  ✓ métier compatible
  ✓ territoire ciblé
  ✓ référence similaire disponible
  ! délai de réponse court

[Voir]   [Suivre]   [Créer une affaire]   [Écarter]
```

## 2.7 Garde-fous fonctionnels du Radar

- toujours afficher la source et la date ;
- distinguer avis publié, résultat, rectificatif et autre type de publication ;
- ne jamais déduire une probabilité de gain comme un fait ;
- permettre à l’utilisateur de corriger la pertinence ;
- apprendre des motifs d’exclusion sans rendre le système opaque ;
- ne pas exposer de champs de données bruts inutiles ;
- séparer données publiques de la stratégie privée de l’entreprise ;
- ne jamais transformer une absence BOAMP en preuve qu’aucun marché n’existe.

### Décision produit retenue dans ce CCF

> **La recherche d’appels d’offres publiés fait partie de l’expérience initiale SMART AO. BOAMP est la première source native prioritaire ; TED complète la couverture européenne. L’intelligence commerciale avant publication reste un horizon distinct et ultérieur.**

---

# 3. Principes UX non négociables

## 3.1 Une affaire, pas un labyrinthe

L’utilisateur travaille dans une **Affaire**. Les objets internes du logiciel ne doivent pas dicter le menu.

Le menu ne doit donc pas exposer des concepts techniques tels que « Evidence », « Requirement », « Claim Verification », « CostFactor » ou « CanonicalDocument ».

Le langage visible doit rester métier :

- Que demande l’acheteur ?
- Qu’est-ce qui manque ?
- Qu’est-ce qui peut coûter cher ?
- Qui doit agir ?
- Que devons-nous produire ?
- Puis-je continuer ?
- Que dois-je décider ?
- Sommes-nous prêts à déposer ?

## 3.2 Simplicité d’abord, profondeur à la demande

SMART AO doit appliquer une logique de **divulgation progressive** :

- niveau 1 : synthèse et décisions ;
- niveau 2 : détails métier ;
- niveau 3 : preuve, source, version, page, cellule, extrait ;
- niveau 4 : historique et justification détaillée.

Le patron ne doit jamais être obligé de lire 80 alertes pour comprendre qu’il existe trois risques critiques.

## 3.3 Chaque écran doit répondre à une utilité

Chaque vue doit servir au moins l’une des fonctions suivantes :

1. comprendre ;
2. agir ;
3. décider ;
4. vérifier une preuve.

Une vue qui ne sert aucune de ces fonctions doit être supprimée ou intégrée ailleurs.

## 3.4 Toujours une prochaine action claire

L’utilisateur ne doit jamais se demander « et maintenant ? ».

À tout moment, SMART AO doit pouvoir indiquer :

- ce qui est attendu ;
- ce qui est fait ;
- ce qui manque ;
- qui doit agir ;
- la date ;
- l’impact si rien n’est fait.

## 3.5 Pas de faux vert

Une analyse partielle ne doit jamais être présentée comme complète.

Un fichier illisible, une annexe absente, une contradiction ou une preuve expirée doivent empêcher un état « prêt » lorsqu’ils affectent une exigence critique.

## 3.6 La preuve doit rester à un clic

Toute conclusion importante doit offrir **Voir la source**.

Cette action ouvre idéalement un panneau latéral ou une vue partagée, sans faire perdre le contexte de l’affaire.

## 3.7 L’IA doit être perceptible, intégrée et gouvernée

La v0.1 disait que l’IA devait rester discrète. Cette formulation est corrigée. **L’IA ne doit pas être cachée**, car une partie de la valeur de SMART AO tient précisément à sa capacité à comprendre, expliquer, guider et préparer le travail.

En revanche, le produit ne doit toujours pas devenir un écran de chat géant. La bonne doctrine est :

> **L’intelligence est au centre de l’accompagnement, pas au centre de la navigation ni de l’autorité.**

SMART AO doit donc être ressenti comme un **collaborateur numérique métier** qui :

- accueille l’utilisateur avec une synthèse utile ;
- comprend l’affaire sur laquelle il travaille ;
- sait où l’utilisateur se trouve dans le parcours ;
- explique pourquoi un point est important ;
- propose la prochaine action ;
- prépare un travail que l’utilisateur peut contrôler ;
- retrouve la preuve lorsqu’on le lui demande ;
- reformule un problème dans le langage BTP ;
- conserve la continuité d’une session à l’autre ;
- sait dire « je ne peux pas conclure avec les éléments disponibles ».

L’IA n’est donc ni un gadget, ni une mascotte, ni l’autorité métier. Elle est la **couche de guidance intelligente** de l’expérience.

## 3.8 Une expérience guidée plutôt qu’une interface muette

Un écran ne doit pas seulement montrer des données. Lorsque cela apporte une valeur réelle, SMART AO doit pouvoir les interpréter en une courte consigne opérationnelle.

Exemples :

```text
Bonjour. Trois affaires demandent votre attention aujourd’hui.

1. AP-HP — dépôt dans 3 jours : 1 blocage documentaire.
2. Ville de X — un rectificatif modifie le BPU ; le prix doit être revu.
3. Filieris — décision GO économique prête pour vous.

Je vous propose de commencer par AP-HP : le blocage peut rendre l’offre irrecevable.

[Ouvrir AP-HP] [Voir toutes mes priorités]
```

ou, dans une affaire :

```text
J’ai terminé la lecture exploitable du dossier.

• 47 exigences détectées
• 4 C1
• 2 informations importantes pour le prix manquent
• 1 contradiction entre le RC et le CCAP

Je vous propose de sécuriser d’abord la visite obligatoire, puis la donnée géotechnique.

[Traiter les C1] [Voir la contradiction] [Continuer l’analyse]
```

Cette parole doit rester courte, concrète et reliée à des éléments vérifiables. Elle ne doit pas remplir l’écran de commentaires inutiles.

## 3.9 Le harnais fonctionnel SMART AO

Le modèle conversationnel ne reçoit jamais une consigne isolée du type « réponds à l’utilisateur ». Fonctionnellement, il intervient dans un **harnais SMART AO** qui lui fournit le cadre nécessaire.

Avant toute intervention, le système doit pouvoir lui donner, selon le besoin :

```text
QUI EST L’UTILISATEUR ?
  rôle, droits, niveau de confidentialité

OÙ SE TROUVE-T-IL ?
  Accueil / Opportunité / Affaire / Analyse / Réponse / Décision / Remise

SUR QUOI TRAVAILLE-T-IL ?
  entreprise, affaire, lot, version du DCE, phase, porte P0–P7

QUE SAIT-ON ?
  faits sourcés, preuves, données validées, documents disponibles

QUE NE SAIT-ON PAS ?
  inconnus, pièces absentes, contradictions, hypothèses, données expirées

QUE PEUT-IL FAIRE ?
  outils et actions autorisés dans ce contexte

QUE NE PEUT-IL PAS FAIRE ?
  décisions réservées, données interdites, actions nécessitant confirmation

QUEL EST LE BUT IMMÉDIAT ?
  comprendre / agir / produire / vérifier / décider
```

Le futur cahier technique décidera comment ce harnais est implémenté. Le CCF impose seulement qu’il existe fonctionnellement.

## 3.10 Une intelligence outillée, pas une intelligence qui improvise

Lorsque SMART AO doit retrouver une source, contrôler un document, préparer une pièce, rechercher une opportunité ou comparer deux versions, l’IA doit s’appuyer sur des **outils et des données du produit** plutôt que d’improviser une réponse à partir du seul modèle.

La conversation doit donc pouvoir déclencher des capacités bornées telles que :

- ouvrir la source d’une exigence ;
- filtrer les C1 d’une affaire ;
- retrouver une preuve entreprise autorisée ;
- préparer une question acheteur ;
- ouvrir le bon formulaire ou modèle ;
- comparer une nouvelle version du DCE ;
- rechercher les opportunités selon les critères du patron ;
- préparer un brouillon de section du mémoire ;
- demander une validation à une personne habilitée ;
- afficher les inconnus qui empêchent de conclure.

Le modèle doit être capable de dire **ce qu’il a consulté et ce qu’il n’a pas pu vérifier**.

## 3.11 La proactivité doit être utile et interruptible

SMART AO peut prendre l’initiative de signaler :

- un rectificatif ;
- une échéance proche ;
- une nouvelle opportunité très pertinente ;
- une pièce qui expire ;
- une contradiction ;
- une donnée manquante qui bloque le prix ;
- un engagement du mémoire non couvert ;
- une décision patron arrivée à maturité.

Mais toute proactivité doit respecter quatre règles :

1. **pertinence** : ne remonter que ce qui mérite réellement l’attention ;
2. **explicabilité** : dire pourquoi le point est remonté ;
3. **actionnabilité** : proposer une action claire ;
4. **contrôle** : permettre à l’utilisateur de différer, masquer ou modifier le niveau de sollicitation.

SMART AO ne doit pas devenir un collègue bavard.

## 3.12 Un seul assistant visible, plusieurs compétences derrière

Pour l’utilisateur, SMART AO doit parler d’une seule voix. Il n’a pas besoin de choisir entre « agent juridique », « agent DCE », « agent mémoire », « agent prix » ou « agent BOAMP ».

La spécialisation éventuelle des outils, prompts ou agents appartient à l’architecture interne. L’expérience visible reste :

> **« Je travaille avec SMART AO sur cette affaire. »**

Cela réduit la charge cognitive et renforce l’identité du produit.

## 3.13 Le ton du collaborateur numérique

SMART AO doit parler comme un collaborateur BTP expérimenté : précis, court, factuel, orienté action.

Il doit éviter :

- les longues introductions ;
- le jargon IA ;
- les compliments inutiles ;
- les certitudes non prouvées ;
- les formulations juridiques péremptoires ;
- les messages anxiogènes sans conséquence concrète ;
- les dizaines de recommandations de même importance.

Il doit privilégier :

```text
J’ai trouvé une contradiction sur le délai de préparation.
RC v2 : 30 jours.
CCAP v1 : 45 jours.
Je ne peux pas trancher sans règle de priorité confirmée.
Impact : planning et coût d’encadrement.

[Voir les sources] [Préparer une question] [Soumettre au patron]
```

## 3.14 Autorité : ce que l’assistant peut et ne peut pas faire

SMART AO peut **constater, expliquer, préparer, recommander et demander**.

Il ne doit pas, sans autorité humaine explicite :

- décider GO/NO-GO ;
- accepter une hypothèse C1 ;
- fixer le prix final ;
- accepter une marge ;
- signer ;
- déposer ;
- modifier une preuve tierce ;
- envoyer une question engageante ;
- accepter une clause juridique sensible ;
- partager une donnée restreinte ;
- considérer un partenaire comme engagé sans confirmation.

Le produit doit toujours distinguer **« SMART AO propose »** de **« l’entreprise décide »**.

## 3.15 Fournisseur de modèle : décision technique différée

Le propriétaire peut décider ultérieurement de commencer avec un fournisseur de modèle unique afin de réduire la complexité et d’obtenir une expérience cohérente. Cette orientation peut être pertinente.

Le présent CCF ne doit toutefois pas inscrire un nom de fournisseur comme exigence fonctionnelle. Ce qu’il rend obligatoire est le comportement : compréhension du contexte, usage des outils, preuves, confidentialité, abstention, continuité et qualité de guidance.

Le choix du premier modèle et la stratégie éventuelle de remplacement ou de comparaison seront traités dans le cahier technique et dans le protocole d’évaluation.

---

# 4. Architecture de l’information globale

Le nombre d’espaces de premier niveau doit rester faible.

## 4.1 Navigation principale cible

### 1. Accueil

Vue adaptée au rôle : priorités, affaires en cours, décisions, urgences, éléments en attente.

### 2. Opportunités

Radar BOAMP/TED et autres sources ; recherches enregistrées ; opportunités suivies ; affaires à qualifier.

### 3. Affaires

Toutes les consultations réellement travaillées, de l’ouverture jusqu’au résultat et à la passation minimale.

### 4. Entreprise

Cet espace porte la **Mémoire Entreprise** : patrimoine privé de l’entreprise, structuré sans devenir un ERP rigide. Il regroupe identité, documents, preuves, références, personnes, matériels, partenaires, méthodes, modèles, prix et données réutilisables. Les informations sensibles sont cloisonnées selon leurs droits et certaines familles restent réservées à la direction par défaut.

Le patron doit pouvoir y confier progressivement le savoir documentaire de la société afin que SMART AO ne reparte jamais de zéro lorsqu’une nouvelle affaire arrive.

### 5. Administration / Paramètres

Utilisateurs, rôles, règles, préférences, sources, notifications et réglages de l’organisation. Cet espace ne doit pas être présenté comme une destination quotidienne.

## 4.2 Ce qui ne doit pas devenir un espace de premier niveau

Par défaut, les éléments suivants vivent dans l’Affaire ou dans Entreprise :

- risques ;
- exigences ;
- documents ;
- questions ;
- tâches ;
- preuves ;
- prix ;
- partenaires ;
- décisions ;
- dépôt.

L’objectif est de ne pas créer douze modules concurrents.

---

# 5. Les rôles et les expériences

Le produit doit disposer d’un modèle fin de responsabilités, mais l’expérience utilisateur doit rester simple.

## 5.1 Patron / dirigeant

Le patron :

- définit les orientations commerciales ;
- décide GO / GO sous conditions / ATTENTE / NO-GO / ABANDON ;
- contrôle prix, marge, trésorerie et exposition ;
- valide les engagements sensibles ;
- autorise l’offre ;
- autorise le dépôt ;
- décide des dérogations ;
- contrôle les données confidentielles ;
- arbitre les risques résiduels.

Son interface doit être orientée **décision et exception**, pas production quotidienne.

## 5.2 Collaborateur / responsable d’offre

Le collaborateur :

- prend en charge l’affaire ;
- contrôle les pièces ;
- vérifie les règles de consultation ;
- traite les exigences ;
- prépare questions et tâches ;
- assemble les preuves ;
- prépare mémoire et documents ;
- coordonne les contributions ;
- remet au patron un dossier prêt à arbitrer.

Il ne doit pas voir, par défaut, les marges, prix d’achat, prix planchers, scénarios de trésorerie ou notes privées sur les partenaires.

## 5.3 Experts contributifs

Métreur, conducteur, QSE, administratif, DAF, achats ou autre expert ne nécessitent pas chacun un logiciel différent.

Ils interviennent dans l’Affaire via :

- actions assignées ;
- vues filtrées ;
- demandes de validation ;
- commentaires et réponses ;
- accès limité à la donnée nécessaire.

## 5.4 Tiers externes

Fournisseur, sous-traitant, cotraitant ou conseil externe ne doit jamais accéder à l’Affaire complète par défaut.

Les échanges futurs doivent fonctionner par **partage ciblé du strict périmètre nécessaire**.

---

# 6. Les portes de décision comme ossature du parcours

Le cahier métier définit P0 à P7. Elles deviennent des moments visibles du parcours.

| Porte | Moment UX | Question affichée au patron | Effet fonctionnel |
|---|---|---|---|
| P0 — Cibler | Opportunité | Cette opportunité mérite-t-elle une action ? | Suivre, ignorer, qualifier |
| P1 — Ouvrir | DCE reçu | Devons-nous investir du temps dans ce dossier ? | Ouvre réellement l’Affaire |
| P2 — GO de principe | Première analyse | Avons-nous une voie crédible pour répondre ? | Autorise le travail de réponse |
| P3 — GO économique | Étude/prix | Avons-nous intérêt à gagner ce marché ? | Autorise la poursuite économique |
| P4 — Autoriser l’offre | Réponse prête | Prix, documents et engagements sont-ils cohérents ? | Fige la version candidate |
| P5 — Autoriser le dépôt | Coffre de dépôt | Cette version exacte peut-elle être remise ? | Verrouille le paquet autorisé |
| P6 — Mise au point | Après classement | Les modifications restent-elles acceptables ? | Nouvelle version et revalidation |
| P7 — Lancer l’exécution | Marché gagné | L’équipe chantier connaît-elle ce qui a été vendu ? | Clôt la passation |

Une porte ne doit jamais être un simple statut automatique. Elle montre :

- décision ;
- auteur ;
- date ;
- conditions ;
- risques restant ouverts ;
- preuves principales ;
- motifs ;
- prochaine réévaluation éventuelle.

---

# 7. Parcours end-to-end cible

```text
RADAR
  ↓
OPPORTUNITÉ
  ↓ P0
QUALIFICATION
  ↓
DCE / INVITATION REÇUE
  ↓ P1
AFFAIRE OUVERTE
  ↓
COUVERTURE DU DOSSIER
  ↓
ANALYSE / EXIGENCES / MIRP / RISQUES
  ↓ P2
PLAN DE RÉPONSE
  ↓
DOCUMENTS / PARTENAIRES / VISITE / QUESTIONS
  ↓
CHIFFRAGE CONTRÔLÉ + CAPACITÉ + TRÉSORERIE
  ↓ P3
MÉMOIRE + PIÈCES + ENGAGEMENTS
  ↓ P4
COFFRE DE DÉPÔT / MANIFESTE
  ↓ P5
DÉPÔT ET PREUVE
  ↓
CLARIFICATIONS / NÉGOCIATION / RÉSULTAT
  ↓ P6 si modification
GAGNÉ → PASSATION → P7
PERDU → RETOUR D’EXPÉRIENCE
```

---

# 8. Parcours collaborateur guidé

L’ancien parcours en onze étapes est conservé comme principe mais simplifié pour éviter onze écrans indépendants.

Le collaborateur voit une **barre d’étapes** dans l’Affaire :

1. Prise en charge ;
2. Dossier reçu ;
3. Règles de consultation ;
4. Analyse du lot ;
5. Actions terrain / visite / questions ;
6. Candidature et preuves ;
7. Réponse technique et documents ;
8. Contrôle ;
9. Soumission au patron ;
10. Corrections éventuelles ;
11. Préparation de la remise.

Ces étapes sont des **états du parcours**, pas forcément des pages séparées.

À chaque étape, l’interface doit répondre :

> **Où suis-je ? Qu’est-ce qui est attendu maintenant ? Qu’est-ce qui manque ? Qui doit agir ? Puis-je continuer ?**

L’utilisateur doit pouvoir fermer SMART AO et reprendre exactement au dernier point utile.

---

# 9. Cockpit patron

## 9.1 Doctrine

Le patron n’a pas besoin de quinze graphiques. Il doit savoir où intervenir.

L’accueil patron se structure autour de trois dimensions :

- **Temps** : où une échéance ou attente menace-t-elle l’affaire ?
- **Préparation prouvée** : quelles parties sont prêtes, lesquelles ne le sont pas et pourquoi ?
- **Risque** : quelle affaire peut coûter de la marge, du temps ou un problème contractuel ?

## 9.2 Liste vivante des affaires

Chaque ligne ou carte d’affaire affiche :

- acheteur, objet, lot, lieu ;
- responsable interne ;
- prochaine échéance ;
- étape actuelle ;
- état de santé ;
- nombre de blocages critiques ;
- prochaine décision attendue ;
- dernière action importante ;
- trois indicateurs synthétiques Temps / Préparation / Risque, chacun ouvrant les faits qui le composent.

## 9.3 Priorités du jour et briefing SMART AO

L’accueil patron doit commencer par un **briefing intelligent très court**, recalculé à partir des affaires, échéances, nouveaux événements et décisions ouvertes. Il répond d’abord : **« Qu’est-ce qui mérite mon attention aujourd’hui ? »**

Le briefing n’est pas une génération libre. Chaque phrase doit pouvoir être reliée à des événements, états ou preuves du produit.

L’écran ne doit pas afficher tout ce qui existe. Il doit sélectionner les éléments réellement actionnables :

- décision P2/P3/P4/P5 en attente ;
- échéance à moins de X jours ;
- visite à confirmer ;
- question acheteur à envoyer ;
- preuve critique expirante ;
- partenaire non sécurisé ;
- document bloquant ;
- rectificatif non revalidé ;
- prix ou engagement non couvert.

---

# 10. L’Affaire comme poste de travail unique

Une Affaire ne doit pas éclater en une multitude d’écrans.

## 10.1 En-tête permanent

L’en-tête affiche toujours :

- nom de l’affaire ;
- acheteur ;
- lot/périmètre ;
- date limite ;
- état de décision ;
- responsable ;
- version DCE ;
- niveau global de préparation ;
- blocages C1 ;
- action principale suivante ;
- accès contextuel **« Demander à SMART AO »**, qui ouvre l’assistant avec le contexte de l’Affaire déjà chargé.

## 10.2 Cinq vues fonctionnelles principales

### A. Synthèse

Décision, échéances, blocages, risques, progression, questions et prochaines actions.

### B. Analyse

DCE, exigences, preuves, applicabilité, contradictions, MIRP, interfaces et risques.

### C. Réponse

Plan de réponse, candidature, documents, mémoire, partenaires, tâches et engagements.

### D. Décision

GO/NO-GO, capacité, scénarios économiques et éléments réservés selon les droits.

### E. Remise

Manifeste, contrôles finaux, signatures, version autorisée, preuve de dépôt.

Les fonctions plus fines deviennent des onglets secondaires, filtres ou panneaux à l’intérieur de ces cinq vues.

---

# 11. Vue Synthèse d’une Affaire

La synthèse doit donner au patron ou au responsable d’offre une réponse exploitable en moins d’une minute.

```text
AFFAIRE — Centre médical X — Lot 01 Gros œuvre

DÉPÔT : J-6 — 18/09/2026 12:00
DÉCISION : GO SOUS CONDITIONS
VERSION DCE : 4 — Rectificatif du 10/09 intégré

3 BLOQUANTS
• Attestation de visite manquante
• Diagnostic amiante cité mais non fourni sur zone B
• Sous-traitant désamiantage : qualification à confirmer

2 RISQUES ÉCONOMIQUES MAJEURS
• Phasage de nuit non couvert dans le chiffrage
• Devis fournisseur expire avant date probable d’achat

DOCUMENTS : 14/18 validés
QUESTIONS ACHETEUR : 2 ouvertes
PROCHAINE DÉCISION PATRON : GO économique

[Traiter les blocages] [Voir les risques] [Décider]
```

---

# 12. Réception du DCE et couverture du dossier

## 12.1 Import

L’utilisateur peut déposer :

- fichiers individuels ;
- dossiers ;
- archives ;
- documents reçus d’un autre canal autorisé.

L’interface doit conserver le dossier source tel que reçu.

## 12.2 Analyse visible de réception

La première sortie n’est pas « analyse terminée ». C’est une **couverture du dossier** :

- X fichiers reçus ;
- X archives ouvertes ;
- X documents reconnus ;
- X documents illisibles ou partiellement lus ;
- pièces annoncées mais absentes ;
- rectificatifs identifiés ;
- doublons ou versions possibles ;
- pièces nécessitant revue manuelle.

## 12.3 États compréhensibles

Le dossier peut être :

- analysable ;
- analysable sous réserves ;
- incomplet pour l’étude ;
- incomplet pour le prix ;
- non analysable sur certains éléments.

Le terme « complet » doit être réservé à une conclusion prouvée dans le contexte concerné.

---

# 13. Analyse DCE : exigences, preuves et source

## 13.1 Carte d’exigence

Chaque exigence visible doit montrer au minimum :

- formulation métier courte ;
- criticité C1/C2/C3 ;
- portée ;
- phase ;
- statut de preuve ;
- source ;
- responsable ;
- action ;
- conséquence si non traitée.

Exemple :

```text
VISITE OBLIGATOIRE — C1
Lot : 01
Échéance : 12/09/2026
Statut : EN ATTENTE
Responsable : Chargé d’affaires
Conséquence : offre potentiellement irrégulière
Source : RC v3 — §4.2 — p. 8

[Organiser] [Voir la source] [Ajouter preuve]
```

## 13.2 Panneau « Voir la source »

La source doit s’ouvrir sans quitter le contexte :

- document ;
- version ;
- page/zone/cellule ;
- extrait ;
- pièce remplacée ou active ;
- éléments liés.

## 13.3 Statuts d’honnêteté

Il faut séparer l’état de connaissance de la criticité.

Statuts possibles :

- Confirmé ;
- Non vérifié ;
- Inconnu ;
- Manquant ;
- Contradictoire ;
- Expiré ;
- Non applicable ;
- Illisible ;
- À revalider après rectificatif.

Une C1 peut donc être « Confirmée » ou « Manquante » : les deux dimensions ne doivent pas être mélangées dans une couleur unique.

---

# 14. Rectificatifs et changements

Un rectificatif ne doit pas être traité comme « un fichier de plus ».

Lorsqu’une nouvelle version arrive, SMART AO doit afficher une vue d’impact :

```text
RECTIFICATIF N°3 REÇU

14 éléments potentiellement impactés
5 nécessitent une revalidation
2 affectent le prix
1 affecte la date de dépôt
3 documents de réponse sont à rouvrir

[Voir les impacts]
```

L’utilisateur voit :

- nouvelle pièce ;
- pièce remplacée ;
- date ou clause changée ;
- exigences impactées ;
- documents de réponse à reprendre ;
- décisions à reconsidérer ;
- tâches rouvertes.

Aucune conclusion critique dérivée d’une pièce remplacée ne reste silencieusement « validée ».

---

# 15. MIRP et informations nécessaires au prix

L’interface doit distinguer clairement :

- document demandé par l’acheteur ;
- document disponible dans le DCE ;
- information nécessaire pour chiffrer ;
- hypothèse décidée par l’entreprise.

Exemple :

```text
NATURE DU SOL — INFORMATION P1 POUR CHIFFRAGE
Statut : MANQUANT
Pourquoi : terrassement et fondations concernés
Documents recherchés : étude géotechnique / sondages / données de sol
Conséquence : coût fondations non défendable

Actions possibles :
[Préparer une question acheteur]
[Ajouter un document]
[Soumettre une hypothèse au patron]
[Marquer NO-GO]
```

Le produit doit éviter l’erreur « une information = un nom de document universel ».

---

# 16. Visite de site

La visite devient un mini-parcours fonctionnel dans l’Affaire.

## Avant

- date, heure, lieu, contact ;
- obligatoire / facultative / dispense ;
- attestation attendue ;
- checklist selon lot et risques déjà détectés ;
- questions à vérifier sur place.

## Pendant

Une vue mobile ou responsive doit permettre :

- notes ;
- photos ;
- mesures simples ;
- croquis ou pièces jointes ;
- constat lié à une exigence ou un risque ;
- fonctionnement hors confort desktop.

## Après

SMART AO confronte les constats avec le DCE et propose :

- nouveau risque ;
- coût à vérifier ;
- question acheteur ;
- engagement à modifier ;
- preuve à conserver ;
- tâche à créer.

La photo de visite ne remplace jamais une attestation officielle.

---

# 17. Questions à l’acheteur

Les questions doivent être gérées comme des objets de l’Affaire :

- sujet ;
- source du doute ;
- impact prix/délai/méthode/conformité ;
- urgence ;
- auteur ;
- validation ;
- date limite ;
- statut envoyé/non envoyé ;
- réponse ;
- impacts sur le reste du dossier.

Une question proposée par l’IA reste un brouillon jusqu’à validation.

---

# 18. Production documentaire et « Mon dossier de réponse »

L’Univers documentaire v1.0 devient une expérience centrale de la vue **Réponse**.

## 18.1 Une table des matières vivante

Pour chaque pièce :

- nom exact acheteur ;
- type ;
- phase ;
- lot/site/variante ;
- source d’exigence ;
- mode : remplir / générer / récupérer / demander / signer / support physique ;
- responsable ;
- statut ;
- validation ;
- confidentialité ;
- échéance ;
- blocage éventuel.

## 18.2 Groupes visibles

L’interface peut regrouper sans perdre la source :

- À produire ;
- À remplir sur modèle acheteur ;
- À récupérer dans l’entreprise ;
- À obtenir d’un tiers ;
- À faire signer ;
- À remettre physiquement ;
- Post-attribution à anticiper.

## 18.3 Modes de génération

L’utilisateur doit toujours savoir ce que SMART AO fait réellement :

- prépare un brouillon ;
- préremplit un modèle ;
- contrôle une pièce ;
- demande une action humaine.

Aucun document tiers ne doit sembler « généré » par SMART AO.

---

# 19. Mémoire technique et réponses notées

Le mémoire technique doit être construit autour de la matrice :

**critère → sous-critère → attente → preuve → réponse → engagement → coût → responsable**.

L’utilisateur voit pour chaque section :

- critère et poids lorsqu’il est connu ;
- ce que l’acheteur demande ;
- éléments du DCE pertinents ;
- preuves entreprise disponibles ;
- données manquantes ;
- texte en brouillon ;
- engagements créés ;
- responsable de validation.

Le produit doit signaler les passages génériques, non prouvés ou déconnectés du chantier.

---

# 20. Prix et chiffrage : espace protégé du patron

SMART AO ne vise pas, au premier stade, à remplacer l’outil de chiffrage de l’entreprise.

Son expérience prix doit :

- rapprocher CCTP/plans/exigences des DPGF/BPU/DQE ;
- signaler les prestations non couvertes ;
- contrôler cohérence et totaux ;
- intégrer ou importer les valeurs validées selon les droits ;
- relier risques et engagements au prix ;
- présenter scénarios marge/trésorerie/capacité au patron ;
- protéger toutes les informations sensibles.

Le collaborateur peut voir :

> « Cette exigence n’est pas encore couverte par le chiffrage. »

Il ne doit pas nécessairement voir :

> prix d’achat, marge, coefficient, prix plancher, stratégie de négociation.

---

# 21. GO/NO-GO et bureau de décision patron

Le bureau de décision ne doit pas produire un score unique.

Il regroupe les dimensions :

- stratégique/commerciale ;
- candidature ;
- technique ;
- capacité ;
- partenaires ;
- prix et marge ;
- trésorerie ;
- contractuel ;
- informations inconnues ;
- conditions de poursuite.

Le patron choisit :

- GO ;
- GO sous conditions ;
- ATTENTE ;
- NO-GO ;
- ABANDON.

Chaque condition devient une action suivie.

---

# 22. Mode urgence

Le mode urgence est conservé de l’ancienne vision, mais il devient une **présentation priorisée**, pas une baisse cachée de qualité.

Quand le délai est très court, SMART AO propose :

1. vérifier échéance et canal ;
2. identifier les pièces éliminatoires ;
3. identifier les inconnues qui empêchent un prix défendable ;
4. identifier les signatures/actions externes incompressibles ;
5. produire ce qui peut être préparé immédiatement ;
6. présenter au patron les risques impossibles à lever à temps.

Le statut final doit clairement dire ce qui n’a pas été contrôlé.

---

# 23. Notifications, tâches, alertes, blocages et décisions

Ces cinq notions ne doivent pas être confondues.

## Notification

Information à lire, sans action obligatoire.

## Tâche

Action concrète avec responsable et échéance.

## Alerte

Événement ou risque nécessitant attention.

## Blocage

État empêchant une porte ou une phase de progresser sans correction, preuve ou dérogation nominative.

## Décision

Acte d’une personne habilitée ayant une conséquence métier.

Le système doit éviter les centaines de notifications sans hiérarchie.

---

# 24. Confidentialité fonctionnelle

La confidentialité ne se résume pas à patron/collaborateur. Elle doit être portée par la donnée elle-même et suivie jusqu’à l’assistant conversationnel, aux exports et aux documents générés.

Les catégories doivent au minimum distinguer :

- public/réutilisable ;
- affaire ;
- secret commercial ;
- personnel ;
- bancaire/fiscal/social ;
- achats/prix ;
- direction uniquement.

Le réglage par défaut doit être prudent. Les marges, prix planchers, scénarios de trésorerie, appréciations internes de partenaires et autres secrets stratégiques sont **Direction uniquement** tant qu’une délégation explicite ne les ouvre pas à un autre rôle habilité. Le produit ne doit cependant pas figer « patron seul » comme unique organisation possible : un DAF, métreur ou responsable achats peut recevoir un accès ciblé sans obtenir l’ensemble des secrets de direction.

La confidentialité doit aussi s’appliquer au contexte IA : une donnée que l’utilisateur courant n’a pas le droit de voir ne doit ni être affichée, ni résumée, ni utilisée pour produire une explication qui permettrait de la déduire.

L’interface doit montrer à l’utilisateur lorsqu’une donnée est restreinte sans révéler son contenu.

Exemple collaborateur :

```text
Décision patron requise — justification financière confidentielle
```

et non :

```text
Marge prévue : 2,1 % — prix plancher : 184 000 €
```

Cette règle constitue une **promesse produit visible** : le patron peut confier à SMART AO ses informations stratégiques tout en laissant ses équipes travailler sur la même affaire sans exposition implicite de ces secrets.

---

# 25. Mémoire Entreprise : patrimoine privé, source de vérité et onboarding progressif

## 25.1 Décision fonctionnelle

La **Mémoire Entreprise** devient un pilier du produit. Elle n’est ni un simple dossier de fichiers, ni une base de prix nationale, ni un ERP supplémentaire.

Elle représente le patrimoine que le patron confie à SMART AO afin que le logiciel puisse travailler avec **la réalité propre de l’entreprise** : ses documents, ses personnes, ses moyens, ses références, ses méthodes, ses partenaires, ses prix, ses règles et ses validations.

La règle fonctionnelle est :

> **Quand SMART AO affirme quelque chose sur l’entreprise, il doit pouvoir dire d’où cette information vient, si elle est encore valable, qui peut la voir et qui l’a validée.**

Cette mémoire doit réduire très fortement les inventions et réutilisations erronées. Elle ne permet toutefois jamais de promettre « zéro hallucination » par le seul stockage documentaire : l’assistant reste obligé de citer, vérifier l’applicabilité et s’abstenir lorsque la source est absente, contradictoire, expirée ou hors périmètre.

## 25.2 Deux vérités qui ne doivent jamais être confondues

SMART AO travaille en permanence avec deux univers de référence :

```text
CE QUE L’ACHETEUR DEMANDE
→ DCE, rectificatifs, questions/réponses, pièces contractuelles

CE QUE L’ENTREPRISE PEUT RÉELLEMENT DIRE, PROUVER OU ENGAGER
→ Mémoire Entreprise validée + décisions humaines + preuves de tiers
```

Le DCE reste la source de vérité des exigences de la consultation. La Mémoire Entreprise devient la source privilégiée des faits propres à la société.

L’IA n’est source de vérité d’aucun de ces deux univers.

## 25.3 Hiérarchie de confiance fonctionnelle

Lorsqu’une réponse ou un document est préparé, SMART AO doit raisonner selon l’ordre suivant :

1. **source acheteur ou contractuelle** pour ce que le marché impose ;
2. **preuve entreprise validée** pour ce que l’entreprise affirme sur elle-même ;
3. **preuve tierce en cours de validité** pour ce qu’une banque, un assureur, une administration, un certificateur, un fabricant ou un partenaire atteste ;
4. **décision humaine nominative** pour un choix, une hypothèse, un prix ou un engagement ;
5. **proposition IA** uniquement comme brouillon, rapprochement, hypothèse ou aide à la décision.

Une proposition IA ne remonte jamais silencieusement au niveau « fait entreprise ».

## 25.4 Familles de la Mémoire Entreprise

Le produit doit proposer une structure de départ claire, sans imposer une taxonomie rigide. Les familles minimales sont :

| Famille | Exemples | Sensibilité par défaut |
|---|---|---|
| Identité et juridique | raison sociale, établissements, SIRET, dirigeants, pouvoirs, délégations | affaire / direction selon champ |
| Administratif, fiscal et social | attestations, vigilance, bilans remis, formulaires réutilisables | restreint |
| Assurances | RC, décennale lorsqu’applicable, avenants, attestations spécifiques | restreint |
| Qualifications, certifications et habilitations | QUALIBAT, QUALIFELEC, ISO, MASE, habilitations, formations | affaire / personnel |
| Personnel et compétences | CV, diplômes, expérience, habilitations, disponibilité, rôle | personnel |
| Moyens matériels | engins, véhicules, outillage, logiciels, moyens spécifiques, disponibilité | affaire / secret commercial |
| Références et preuves de savoir-faire | fiches opérations, attestations de bonne exécution, photos autorisées, montants publiables | affaire / secret commercial |
| Méthodes et QSE | procédures, modes opératoires, contrôles, politiques, environnement, sécurité | secret commercial |
| Prix et achats | prix fournisseurs, catalogues, accords, sous-détails, ratios, rendements, conditions | prix/achats restreints |
| Finance et stratégie | marges, prix planchers, trésorerie, coût du financement, seuils de décision | direction uniquement |
| Partenaires | fournisseurs, sous-traitants, cotraitants, documents, spécialités, avis internes | selon donnée |
| Produits et solutions | fiches techniques, FDS, DoP, PV, agréments, systèmes proposés | affaire / fournisseur |
| Modèles de l’entreprise | trames de mémoire, plannings, courriers, tableaux, organigrammes | affaire / secret commercial |
| Retour d’expérience | rendements, aléas, écarts prévu/réel, incidents, leçons validées | direction / métier |

Le patron doit pouvoir ajouter ses propres catégories, tags et vocabulaires. Les invariants de sécurité — source, validité, sensibilité, statut, titulaire, validation — ne sont pas supprimables.

## 25.5 Un document n’est pas seulement un fichier

Chaque pièce importante doit pouvoir porter des métadonnées métier. Selon sa nature :

- type de document ;
- titulaire ou entité concernée ;
- émetteur ;
- date d’émission ;
- date de début de validité ;
- date d’expiration, lorsqu’elle existe réellement ;
- date de prochaine revue ;
- activité, qualification, produit, établissement ou personne couverte ;
- périmètre géographique ou contractuel si pertinent ;
- niveau de confidentialité ;
- propriétaire interne ;
- personne ayant contrôlé ;
- statut de validation ;
- fichier original ;
- version remplacée ;
- commentaires ou limites d’usage.

Le produit ne doit pas inventer une date d’expiration lorsqu’un document n’en possède pas. Il peut proposer une **date de revue interne** distincte d’une durée légale ou contractuelle.

## 25.6 Téléversement guidé : ne pas transformer la fiabilité en corvée

L’idée « remplir tous les champs avant de téléverser » est sûre mais deviendrait vite lourde. Le CCF retient deux chemins complémentaires.

### Chemin A — ajout guidé

Pour un document critique, le patron choisit par exemple **Ajouter une assurance**. SMART AO affiche les champs pertinents, accepte le fichier original, extrait les métadonnées qu’il reconnaît et demande confirmation.

```text
AJOUTER — ATTESTATION D’ASSURANCE

Fichier                [Déposer]
Assureur               [proposé après lecture]
Titulaire              [Entreprise X]
Activités couvertes    [à confirmer]
Valable du             [01/01/2026]
Au                     [31/12/2026]
Périmètre / limites    [à confirmer]
Confidentialité        [Restreint]

[Enregistrer comme brouillon] [Valider la fiche]
```

### Chemin B — dépôt en masse

Le patron doit aussi pouvoir déposer un dossier entier : assurances, qualifications, CV, références, prix, procédures, etc.

SMART AO :

1. inventorie les fichiers ;
2. propose un classement ;
3. extrait les métadonnées possibles ;
4. détecte doublons, versions et expirations apparentes ;
5. marque ce qui exige confirmation ;
6. n’utilise comme preuve forte que ce qui a atteint le statut nécessaire.

Ainsi, la flexibilité n’oblige pas l’entreprise à saisir manuellement des centaines de fiches avant de commencer.

## 25.7 Cycle de vie d’un élément de la Mémoire Entreprise

Les états fonctionnels minimaux sont :

```text
IMPORTÉ
  ↓
À QUALIFIER
  ↓
À VÉRIFIER
  ↓
VALIDÉ / ACTIF
  ↓
EXPIRANT ou À REVOIR
  ↓
EXPIRÉ / REMPLACÉ / ARCHIVÉ
```

États parallèles possibles : **incomplet**, **illisible**, **titulaire à confirmer**, **périmètre incertain**, **restreint**, **non réutilisable**.

Un ancien document ne doit jamais disparaître silencieusement lorsqu’il est remplacé. La version active est claire ; l’historique reste retraçable selon les droits.

## 25.8 Expiration et veille documentaire proactive

SMART AO doit surveiller les données périodiques et documents expirables.

L’alerte ne doit pas se limiter à « expire dans 7 jours ». Elle doit comprendre le contexte d’affaires :

```text
ASSURANCE RC — expire le 31/12/2026

• valide aujourd’hui ;
• valide à la date de dépôt AP-HP ;
• pourrait être expirée avant la date probable d’attribution ;
• utilisée actuellement dans 4 affaires ouvertes.

[Demander le renouvellement] [Voir les affaires concernées]
```

Les horizons d’alerte doivent être configurables ou recommandés par famille : 90 / 60 / 30 / 15 / 7 jours par exemple, sans imposer la même règle à tous les documents.

Une expiration doit créer une **action responsable**, pas seulement une notification.

## 25.9 Les prix ne doivent pas devenir une base rigide imposée par SMART AO

Pour les prix, la Mémoire Entreprise doit respecter la méthode du patron.

SMART AO peut absorber :

- fichiers Excel internes ;
- prix fournisseurs ;
- accords-cadres d’achat ;
- historiques de devis ;
- ratios et rendements ;
- coûts matériels ;
- sous-traitance ;
- frais et règles de calcul validées ;
- références provenant d’un ERP ou outil de chiffrage lorsqu’un échange licite existe.

Il ne doit pas forcer l’entreprise à convertir immédiatement son organisation dans une « base de prix SMART AO » universelle.

Pour toute donnée de prix utilisée, l’interface doit pouvoir montrer : **source, version/date, unité, fournisseur ou origine, conditions, validité, périmètre et niveau de confidentialité**.

## 25.10 Données structurées et documents originaux doivent rester liés

SMART AO peut extraire « CA 2025 = X », « assurance expire le 31 décembre », « salarié Y possède telle habilitation » ou « prix fournisseur = Z ».

Mais la donnée structurée ne doit pas devenir orpheline. L’utilisateur doit pouvoir revenir au document, fichier, saisie ou décision qui la justifie.

Si deux sources se contredisent, SMART AO affiche le conflit ; il ne choisit pas silencieusement la valeur la plus récente ou la plus favorable.

## 25.11 La Mémoire Entreprise comme moteur de production documentaire

Lorsqu’un document de réponse doit être préparé, SMART AO commence par rechercher les éléments autorisés dans la Mémoire Entreprise.

Exemple : cadre de mémoire demandant « Responsable de l’opération ».

```text
SMART AO a trouvé :
• 3 personnes possédant le profil métier requis ;
• 2 disposent d’un CV validé ;
• 1 est déjà engagée sur une autre affaire à la période estimée.

Je ne renseignerai personne tant que l’affectation n’est pas décidée.

[Comparer les profils] [Demander une décision]
```

Exemple : assurance demandée :

```text
Attestation trouvée : RC Pro 2026
Statut : valide aujourd’hui
Activité : correspondance à contrôler pour ce lot
Expiration : 31/12/2026

[Voir l’original] [Valider pour cette affaire]
```

L’IA réutilise donc des **faits contrôlés**, pas des souvenirs conversationnels.

## 25.12 Une mémoire privée pour la décision, pas seulement pour rédiger

La Mémoire Entreprise alimente également :

- GO/NO-GO ;
- contrôle des capacités ;
- choix des références ;
- disponibilité des personnes et moyens ;
- couverture des qualifications ;
- comparaison fournisseurs ;
- scénarios de prix ;
- contrôle des engagements ;
- alertes de documents expirants ;
- passation vers l’exécution ;
- retour d’expérience.

La rédaction n’est qu’un consommateur parmi d’autres.

## 25.13 Sous-espaces fonctionnels et séparation direction/collaborateurs

L’espace **Entreprise** doit montrer des familles lisibles plutôt qu’une arborescence de serveur de fichiers :

```text
MON ENTREPRISE

État de préparation
• 3 documents expirent bientôt
• 2 preuves à vérifier
• 1 délégation à renouveler

[Identité & pouvoirs]
[Assurances & conformité]
[Qualifications]
[Équipe & compétences]
[Moyens & matériel]
[Références]
[Méthodes / QSE]
[Partenaires]
[Produits]
[Modèles]

──────── DIRECTION / ACCÈS RESTREINT ────────
[Prix & achats]
[Finance & trésorerie]
[Stratégie & règles de décision]
[Évaluations internes / REX sensibles]
```

Le collaborateur peut voir qu’une preuve existe ou qu’une décision direction est requise sans obtenir nécessairement le contenu restreint.

## 25.14 Le patron reste propriétaire du partage

Le principe commercial « vos secrets restent chez vous » doit être rendu tangible dans l’interface.

Par défaut :

- les informations stratégiques sont invisibles aux collaborateurs ;
- le patron choisit les délégations ;
- une délégation peut être limitée à une famille, une affaire ou une action ;
- toute réutilisation sensible dans un document candidat est contrôlée ;
- SMART AO ne doit pas révéler indirectement un secret dans une phrase générée.

Le futur cahier technique définira authentification, chiffrement, isolation, journalisation, sessions et autres mécanismes de sécurité. Le CCF impose dès maintenant le **résultat visible et attendu**.

## 25.15 Onboarding : exhaustif à terme, progressif à l’entrée

La vision cible est effectivement que SMART AO connaisse assez bien l’entreprise pour travailler comme un collaborateur de confiance. Cela ne justifie pas un tunnel initial de cinquante formulaires.

Au premier démarrage, SMART AO doit proposer :

```text
PRÉPARER MA MÉMOIRE ENTREPRISE

Vous pouvez commencer tout de suite, ou renforcer progressivement SMART AO.

Priorité recommandée :
1. identité et pouvoirs ;
2. assurances / qualifications ;
3. références et moyens ;
4. équipe ;
5. documents administratifs ;
6. modèles ;
7. prix et données privées de direction.

[Importer un dossier complet]
[Ajouter les essentiels]
[Commencer avec un DCE]
```

Si l’utilisateur commence avec un DCE, SMART AO doit pouvoir dire au bon moment :

> « Cette consultation exige une assurance dont je ne dispose pas encore. Ajoutez-la maintenant ou marquez-la à obtenir. »

La complétude se construit donc **au fil des usages**, mais les manques critiques ne sont jamais masqués.

## 25.16 Flexibilité sans chaos

SMART AO doit s’adapter aux habitudes de l’entreprise : noms de fichiers, familles de prix, vocabulaire, procédures, modèles, rôles et circuits de validation.

En revanche, certaines notions restent communes car elles sécurisent le produit :

- provenance ;
- titulaire ;
- version ;
- validité / revue ;
- sensibilité ;
- statut de validation ;
- applicabilité ;
- propriétaire ;
- historique.

La personnalisation doit porter sur la manière de travailler, pas supprimer les garde-fous de preuve.

## 25.17 Critères d’acceptation fonctionnels

La Mémoire Entreprise est acceptable si :

- un patron peut importer un dossier documentaire sans tout ressaisir ;
- SMART AO propose un classement et des métadonnées mais distingue clairement « proposé » de « validé » ;
- chaque document critique possède un titulaire, une portée, un statut et une règle de fraîcheur adaptée ;
- les éléments expirables créent des actions avant échéance ;
- une donnée extraite permet d’ouvrir sa source ;
- une preuve expirée n’est pas utilisée silencieusement comme preuve valide ;
- les prix restent liés à leurs sources et conditions ;
- un collaborateur ne peut ni voir ni déduire les informations réservées à la direction ;
- l’assistant ne peut pas utiliser dans sa réponse une donnée à laquelle l’utilisateur courant n’a pas accès ;
- les catégories de l’entreprise peuvent être enrichies sans casser les invariants de sécurité ;
- un document remplacé conserve son historique ;
- une information absente déclenche « je ne l’ai pas » ou une action, jamais une invention.

---

# 26. Coffre de dépôt et manifeste de remise

Le terme **Coffre de dépôt** est conservé de l’ancienne vision.

Il représente la zone finale, séparée du travail quotidien.

## 26.1 Avant autorisation

Le Coffre vérifie :

- toutes les exigences bloquantes ;
- modèles acheteur ;
- versions ;
- pièces obsolètes ;
- cohérence AE/BPU/DQE/DPGF ;
- engagements techniques ;
- signatures/pouvoirs ;
- formats, tailles, noms et sécurité des fichiers ;
- absence de données internes confidentielles ;
- objets physiques ;
- manifeste exact.

## 26.2 Aucune hypothèse ZIP

La sortie peut être :

- fichiers individuels ;
- dossiers ;
- archive ;
- natif + PDF ;
- dépôt physique ;
- combinaison de plusieurs canaux.

L’interface doit reproduire la règle propre à la consultation.

## 26.3 Version autorisée

Lorsque le patron autorise le dépôt :

- la version devient clairement identifiée ;
- les changements ultérieurs doivent la rendre de nouveau « à valider » ;
- le manifeste et l’empreinte sont conservés ;
- le reçu après dépôt est rapproché de la version autorisée.

---

# 27. Après dépôt, résultat et passation minimale

## Après dépôt

SMART AO suit :

- reçu ;
- demandes de précision ;
- négociation ;
- prolongation de validité ;
- nouvelle offre ;
- résultat.

## Si perdu

- fait vs hypothèse ;
- notes ;
- motifs disponibles ;
- attributaire/montant lorsque publiés ;
- enseignement validé.

## Si gagné

SMART AO crée un **dossier de passation minimal** :

- contrat final/version gouvernante ;
- prix et hypothèses pertinentes ;
- engagements du mémoire ;
- risques acceptés ;
- partenaires ;
- questions/réponses ;
- planning vendu ;
- livrables futurs ;
- points de vigilance.

Le produit ne devient pas pour autant un ERP chantier.

---

# 28. Expérience mobile / terrain

SMART AO reste d’abord un outil desktop pour l’étude de DCE.

Le mobile doit cibler les usages où il apporte une valeur claire :

- visite de site ;
- photos et constats ;
- actions urgentes ;
- validations simples ;
- consultation de synthèse ;
- réception d’alertes critiques.

Il ne faut pas chercher à reproduire l’intégralité du bureau d’études sur téléphone.

---

# 29. Performance perçue et fluidité

Même avant les choix techniques, le CCF impose des attentes visibles :

- l’utilisateur peut commencer à travailler avant la fin d’analyses longues ;
- les étapes d’analyse affichent leur progression et leurs limites ;
- aucun écran principal ne dépend d’un long chargement sans information ;
- les recherches, filtres et ouvertures de source doivent sembler immédiats dans les cas normaux ;
- une tâche longue doit être reprise sans perte de contexte ;
- les résultats partiels sont identifiés comme partiels.

La vitesse perçue fait partie de la confiance produit.

---

# 30. Design system fonctionnel

Le design visuel détaillé viendra ensuite, mais les conventions doivent être stables.

## 30.1 Ne pas utiliser une seule couleur pour tout

Trois dimensions doivent être distinguées :

1. criticité : C1/C2/C3 ;
2. état de connaissance : confirmé/manquant/contradictoire/etc. ;
3. état d’action : à faire/en attente/validé/bloqué.

## 30.2 Composants fonctionnels récurrents

- carte Affaire ;
- carte Opportunité ;
- carte Exigence ;
- carte Risque ;
- carte Document ;
- carte Décision ;
- panneau Source ;
- timeline Version/Rectificatif ;
- barre de progression du parcours ;
- panneau « prochaine action » ;
- bannière de blocage ;
- manifeste de remise.

---

# 31. Wireframes textuels prioritaires

## 31.1 Accueil Patron

```text
SMART AO                                      [Entreprise X] [Patron]

PRIORITÉS AUJOURD’HUI
1. [C1] Filieris — visite obligatoire non confirmée — J-6
2. [P3] Ville Y — GO économique à décider
3. [C1] AP-HP — 4 lignes BPU non renseignées — J-3

MES AFFAIRES
-----------------------------------------------------------------
Affaire          Échéance     Étape          Préparation              Risque
Filieris lot 01  J-6          Réponse        14/18 pièces validées    ÉLEVÉ
AP-HP lot 11A    J-3          Coffre         1 blocage restant        MOYEN
RN12 lot X       J-12         Analyse        3 inconnus de prix       ÉLEVÉ
-----------------------------------------------------------------

[Opportunités nouvelles : 12] [Décisions en attente : 3]
```

## 31.2 Radar Opportunités

```text
OPPORTUNITÉS
[Recherche] [Métier] [Zone] [Acheteur] [Date] [Source] [Filtres]

Recherches enregistrées :
• CVC — Île-de-France — 0 à 2 M€
• Réhabilitation hospitalière — France Nord

-------------------------------------------------------------
Ville de X — Réhabilitation groupe scolaire
Source : BOAMP                  Dépôt : 03/10/2026
Lot : CVC                       Lieu : ...
Pourquoi proposé : métier + territoire + référence similaire
Alerte : délai de réponse court
[Voir] [Suivre] [Créer une affaire] [Écarter]
-------------------------------------------------------------
```

## 31.3 Analyse Affaire

```text
FILIERIS — LOT 01                               DÉPÔT J-6
[Synthèse] [Analyse] [Réponse] [Décision] [Remise]

ANALYSE
Filtres : [C1] [Prix] [Documents] [Technique] [Contradictions]

C1  Visite obligatoire                 EN ATTENTE
    RC v3 §4.2 p.8                     [Voir source]
    Responsable : Karim                [Traiter]

C1  Diagnostic amiante zone B          MANQUANT
    CCTP p.42 renvoie au DAT           [Voir source]
    Impact : prix + méthode             [Question acheteur]

C2  Pénalité retard 200 €/jour         CONFIRMÉ
    CCAP v2 §13                        [Voir source]
```

## 31.4 Coffre de dépôt

```text
COFFRE DE DÉPÔT — VERSION CANDIDATE V7

Pièces requises             18
Validées                     14
À obtenir                     2
En attente de décision        1
Bloquantes                    1

BLOCAGE
• Attestation de visite absente

Contrôles :
✓ DPGF/BPU/AE cohérents
✓ modèles acheteur préservés
✓ aucune pièce obsolète
! signature à vérifier
✓ données internes sensibles absentes

STATUT : DÉPÔT NON AUTORISÉ
[Voir manifeste] [Traiter blocages] [Demander autorisation patron]
```

---

# 32. Recettes fonctionnelles et UX

Le CCF reprend le catalogue REC-01 à REC-28 comme base, mais ajoute des critères d’expérience.

Une recette fonctionnelle n’est réussie que si :

- l’utilisateur comprend ce qui se passe sans connaître l’architecture ;
- la source est accessible ;
- le responsable est identifiable ;
- le blocage ou la décision est explicite ;
- aucune donnée confidentielle n’apparaît au mauvais rôle ;
- la prochaine action est claire ;
- un statut « prêt » n’est jamais obtenu par omission d’une pièce non lue.

## 32.1 Recettes UX prioritaires supplémentaires

### UX-01 — Opportunité BOAMP

Une annonce pertinente arrive : l’utilisateur la voit dans le Radar, comprend pourquoi elle apparaît, peut consulter la source et la transformer en Affaire sans ressaisie importante.

### UX-02 — Opportunité non pertinente

Le patron écarte une annonce avec motif. Le motif améliore les tris futurs mais n’empêche jamais de retrouver la source.

### UX-03 — Collaborateur repris après interruption

Un collaborateur quitte une Affaire pendant l’analyse puis revient le lendemain : il retrouve l’étape, les actions ouvertes, le dernier élément contrôlé et les nouveaux rectificatifs éventuels.

### UX-04 — Confidentialité patron

Le patron refuse une affaire pour raison financière. Le collaborateur voit « décision NO-GO — raison détaillée réservée direction » sans voir marge, prix plancher ou trésorerie.

### UX-05 — Rectificatif

Un nouveau BPU arrive. L’utilisateur ne doit pas chercher ce qui a changé : SMART AO lui présente les éléments à revalider et empêche P5 tant que les contrôles critiques ne sont pas repris.

### UX-06 — Mode urgence

Une affaire arrive à J-2. L’interface priorise les risques éliminatoires et les inconnues de prix, tout en marquant explicitement ce qui ne sera pas vérifié à temps.

### UX-07 — Source

Depuis une exigence critique, l’utilisateur atteint la bonne source en un clic sans perdre sa place dans l’Affaire.

### UX-08 — Manifeste non-ZIP

Une consultation exige plusieurs fichiers séparés : le Coffre reproduit cette règle et ne propose pas par défaut une archive unique.

---

# 33. Arbitrages produit intégrés ou à confirmer

## 33.1 Arbitrages fonctionnels retenus dans cette v1.0

1. **Affaire = centre de l’expérience.**
2. **Patron et collaborateur ont des expériences distinctes.**
3. **La recherche d’opportunités publiées est incluse dans le produit visible initial.**
4. **BOAMP = première source native prioritaire ; TED = deuxième source publique native.**
5. **Les signaux avant publication restent une extension distincte.**
6. **L’interface n’est pas un chatbot.**
7. **Le parcours collaborateur est guidé, mais ses étapes ne deviennent pas onze pages isolées.**
8. **Cockpit patron centré sur Temps / Préparation prouvée / Risque.**
9. **Voir la source est un invariant.**
10. **Le Coffre de dépôt est la zone de validation finale ; aucune hypothèse ZIP.**
11. **Le mobile est un compagnon terrain, pas le poste d’étude principal.**
12. **SMART AO accompagne la passation vers chantier sans devenir un ERP complet.**

## 33.2 Décisions métier encore ouvertes et impact UX

Les DEC-01 à DEC-10 du cahier métier restent juridiquement et produitement ouvertes tant que le propriétaire ne les a pas formellement arbitrées.

Le CCF adopte néanmoins des orientations provisoires compatibles avec leurs recommandations :

- cible initiale PME BTP ;
- public garanti d’abord, privé reconnu mais couverture qualifiée ;
- contrôle du chiffrage avant remplacement d’un ERP de devis ;
- dépôt humain assisté avant automatisation ;
- sources ouvertes ciblées avant agrégation exhaustive ;
- validation humaine des sujets juridiques sensibles ;
- mesure de valeur par temps, erreurs évitées, risque et marge protégée.

---

# 34. Place du BOAMP dans la future architecture technique — frontière du présent document

Le CCF décide **ce que l’utilisateur doit obtenir** :

- source BOAMP intégrée au Radar ;
- recherche/filtrage ;
- rafraîchissement régulier ;
- lien vers l’annonce ;
- déduplication visible ;
- conversion en Affaire ;
- recherches sauvegardées et alertes ;
- provenance conservée.

Le CCF ne décide pas encore :

- version exacte de l’Explore API ;
- endpoint final ;
- mapping de champs ;
- cache ;
- pagination ;
- fréquence technique de synchronisation ;
- stratégie de stockage ;
- rate limits ;
- retry ;
- adaptateur ;
- contrat de données interne.

Ces points appartiendront au cahier technique, après vérification de la documentation actuelle de l’API et de ses conditions d’usage.

Cette séparation est volontaire : le produit dépend du service rendu « rechercher des marchés BOAMP », pas d’une version particulière de l’API.

---

# 35. Critères de réussite du CCF avant passage à l’architecture technique

Le CCF pourra être considéré comme stabilisé lorsqu’il permet de répondre sans ambiguïté à ces questions :

1. Quels sont les espaces visibles du produit ?
2. Que voit le patron ?
3. Que voit le collaborateur ?
4. Comment une opportunité devient-elle une Affaire ?
5. Comment BOAMP/TED apparaissent-ils dans le produit ?
6. Comment une Affaire progresse-t-elle de P0 à P7 ?
7. Quels sont les cinq écrans/vues réellement centraux ?
8. Comment l’utilisateur voit-il une exigence et sa preuve ?
9. Comment l’outil affiche-t-il un inconnu ou un blocage ?
10. Comment les documents sont-ils produits, obtenus, contrôlés et validés ?
11. Comment le patron garde-t-il le contrôle des prix et de la confidentialité ?
12. Comment un rectificatif rouvre-t-il ce qui doit l’être ?
13. Comment le Coffre prouve-t-il la version autorisée et la remise ?
14. Comment la passation vers l’exécution évite-t-elle la perte des engagements ?
15. Quels parcours seront prototypés et testés avant codage ?

---

# 36. Modèle d’interaction conversationnelle intégré

La conversation n’est pas un module autonome. C’est une **capacité transversale** accessible dans les endroits où elle réduit réellement l’effort utilisateur.

## 36.1 Trois formes d’apparition

### A. Briefing

SMART AO prend l’initiative pour résumer ce qui mérite l’attention.

### B. Guidance contextuelle

Une petite zone intégrée à l’écran explique l’état actuel et propose une prochaine action.

### C. Conversation à la demande

Le bouton **« Demander à SMART AO »** ouvre un panneau latéral. Le contexte est déjà connu : l’utilisateur ne doit pas recopier le nom de l’affaire ou réexpliquer le problème.

## 36.2 Questions suggérées selon l’écran

Sur une Opportunité :

- « Pourquoi cette affaire correspond-elle à mon entreprise ? »
- « Qu’est-ce qui peut nous disqualifier rapidement ? »
- « Quelles références internes sont proches ? »

Sur l’Analyse :

- « Montre-moi uniquement ce qui peut affecter le prix. »
- « Qu’est-ce qui reste non vérifié ? »
- « D’où vient cette exigence ? »
- « Y a-t-il des contradictions entre RC, CCAP et CCTP ? »

Sur la Réponse :

- « Qu’est-ce qui manque pour finir le mémoire ? »
- « Quels engagements avons-nous ajoutés ? »
- « Prépare un brouillon pour ce sous-critère avec uniquement nos preuves validées. »

Sur la Décision :

- « Résume ce qui justifie encore un GO sous conditions. »
- « Quelles hypothèses peuvent dégrader la marge ? »
- « Qu’est-ce qui dépend encore d’un tiers ? »

Sur la Remise :

- « Pourquoi le dépôt est-il bloqué ? »
- « Quels fichiers doivent encore être signés ? »
- « Qu’est-ce qui a changé depuis la version autorisée précédente ? »

## 36.3 Réponse orientée action

Par défaut, une réponse SMART AO doit être structurée en trois couches :

1. **réponse courte** ;
2. **raison / preuve essentielle** ;
3. **actions possibles**.

Exemple :

```text
Le prix n’est pas encore sécurisable.

Deux raisons :
• l’étude géotechnique citée au CCTP est absente ;
• le devis de fondations spéciales expire avant la date probable de commande.

[Voir les preuves] [Préparer une question acheteur]
[Demander une actualisation fournisseur] [Soumettre au patron]
```

## 36.4 Mémoire conversationnelle visible et contrôlable

SMART AO peut reprendre le contexte d’une affaire d’une session à l’autre, mais l’utilisateur doit comprendre ce qui constitue la mémoire de travail : décisions validées, documents, commentaires, tâches, preuves et préférences autorisées.

Une phrase prononcée dans une conversation ne doit pas devenir silencieusement une vérité métier. Pour influencer une décision, un document ou un engagement, elle doit être convertie en donnée, hypothèse, commentaire ou décision avec auteur et statut explicites.

---

# 37. Spécification détaillée — Accueil Patron

## 37.1 Objectif

Permettre au dirigeant de savoir en moins de trente secondes :

- où il doit intervenir ;
- ce qui risque une échéance ;
- quels dossiers ne sont pas fiables ;
- quelles décisions attendent son autorité ;
- quelles nouvelles opportunités méritent un regard.

## 37.2 Hiérarchie visuelle

1. **Briefing SMART AO du jour** — 3 à 5 points maximum ;
2. **Décisions à prendre** ;
3. **Affaires sous tension** ;
4. **Affaires en cours** ;
5. **Nouvelles opportunités pertinentes** ;
6. détails et indicateurs secondaires.

## 37.3 Action primaire

L’action primaire n’est pas « Voir le tableau de bord ». Elle est **ouvrir le point prioritaire**.

## 37.4 Assistant

SMART AO peut dire :

```text
Aujourd’hui, je vous recommande de traiter d’abord AP-HP.
Le dépôt est dans 3 jours et l’attestation de visite manque encore.

Ensuite, Ville de X est prête pour votre décision P3.

[Ouvrir AP-HP] [Voir P3 Ville de X]
```

Chaque recommandation doit être justifiée par l’état de l’outil.

## 37.5 État vide

Pour une nouvelle entreprise :

```text
Bienvenue dans SMART AO.

Trois façons de commencer :
1. rechercher vos premiers appels d’offres ;
2. importer un DCE que vous avez déjà reçu ;
3. préparer votre Mémoire Entreprise en important vos documents existants.

[Rechercher des marchés] [Importer un DCE] [Préparer mon entreprise]
```

Il ne faut pas imposer un long paramétrage initial. L’utilisateur peut travailler immédiatement, mais SMART AO doit rendre visible le niveau de préparation de la Mémoire Entreprise et demander les éléments manquants au moment où ils deviennent nécessaires.

## 37.6 État d’erreur ou données partielles

Si certaines analyses ou sources sont indisponibles, le briefing doit le dire explicitement et ne pas transformer cette absence en « aucune priorité ».

## 37.7 Critères d’acceptation

- pas plus de cinq priorités au premier niveau ;
- toute priorité possède une raison et une action ;
- aucune donnée financière réservée n’est visible à un rôle non autorisé ;
- le briefing reste utile même si l’IA conversationnelle est temporairement indisponible : les priorités structurées restent accessibles.

---

# 38. Spécification détaillée — Radar Opportunités

## 38.1 Objectif

Faire de SMART AO le point d’entrée naturel pour **trouver puis qualifier** une consultation publiée, sans prétendre couvrir immédiatement toute l’intelligence commerciale française.

## 38.2 Structure

Colonne ou barre de filtres :

- recherche libre ;
- métier / famille de travaux ;
- zone ;
- acheteur ;
- type de procédure ou marché lorsqu’il est disponible ;
- date limite ;
- source ;
- montant lorsqu’il est publié ;
- recherches enregistrées.

Zone principale : cartes ou liste compacte d’opportunités.

Panneau secondaire : **Pourquoi SMART AO me la montre ?**

## 38.3 Actions

Action primaire : **Créer une affaire**.

Actions secondaires : Voir, Suivre, Écarter, Ajouter une note, Ouvrir la source.

## 38.4 Assistant

Le modèle peut transformer des préférences exprimées naturellement en recherche guidée :

```text
« Cherche-moi les marchés de rénovation électrique en Île-de-France,
plutôt entre 200 k€ et 2 M€, avec au moins trois semaines pour répondre. »
```

SMART AO doit reformuler les critères appliqués avant d’enregistrer une veille :

```text
J’ai compris :
• travaux électriques / rénovation
• Île-de-France
• 200 k€ à 2 M€ lorsque le montant est publié
• délai de réponse ≥ 21 jours

[Appliquer] [Modifier]
```

Le modèle ne doit jamais inventer un filtre non disponible dans la source ; il doit signaler les critères impossibles à vérifier.

## 38.5 Déduplication visible

Si un même marché provient de plusieurs sources, l’utilisateur doit voir une opportunité consolidée avec plusieurs provenances, sans perdre les liens originaux.

## 38.6 États vides

Aucun résultat ne doit devenir « aucun marché existe ». Le message doit être :

> « Aucun résultat dans les sources et critères actuellement interrogés. »

Le produit propose ensuite d’élargir les filtres.

## 38.7 Critères d’acceptation

- source et fraîcheur visibles ;
- explication de pertinence consultable ;
- transformation en Affaire sans ressaisie des données déjà connues ;
- motif d’exclusion enregistré mais réversible ;
- absence de « probabilité de gain » présentée comme vérité.

---

# 39. Spécification détaillée — Fiche Opportunité

## 39.1 Objectif

Permettre une décision P0/P1 rapide avant d’engager une analyse lourde.

## 39.2 Premier écran

Doit montrer : objet, acheteur, source, dates, lieu, lots, procédure connue, documents accessibles, première compatibilité avec l’entreprise, points d’attention et provenance.

## 39.3 Bloc SMART AO

```text
Pourquoi regarder cette affaire ?
✓ lot compatible avec votre activité
✓ deux références internes proches
! réponse dans 16 jours
? montant non publié

Ce que je ne peux pas encore établir :
• charge réelle de l’étude
• contraintes techniques du DCE non encore téléchargé

[Créer une affaire et récupérer le DCE]
```

## 39.4 Action décisionnelle

P0 peut conclure : suivre / ouvrir / écarter.

Écarter doit proposer des motifs simples : hors métier, hors zone, délai trop court, client non ciblé, charge indisponible, autre.

## 39.5 Critères d’acceptation

L’utilisateur doit pouvoir décider sans être forcé de lire les données brutes de la source.

---

# 40. Spécification détaillée — Synthèse Affaire

## 40.1 Objectif

Transformer un dossier complexe en **situation de travail actuelle**.

## 40.2 Hiérarchie

1. décision actuelle et prochaine porte ;
2. échéance ;
3. blocages C1 ;
4. inconnus importants ;
5. risques prix/capacité ;
6. documents ;
7. actions ;
8. historique récent.

## 40.3 Briefing d’affaire

À chaque retour significatif, SMART AO peut résumer ce qui a changé depuis la dernière visite :

```text
Depuis votre dernière ouverture :
• le rectificatif n°2 a été ajouté ;
• la date de dépôt est repoussée de 4 jours ;
• 3 exigences doivent être revalidées ;
• le BPU a changé sur 12 lignes.

Je n’ai pas modifié votre décision GO.
Elle doit être revue si l’impact prix est confirmé.

[Voir les impacts]
```

## 40.4 Commande naturelle contextualisée

L’utilisateur peut demander :

> « Montre-moi seulement ce qui peut empêcher le dépôt. »

La vue doit alors appliquer un filtre explicite et réversible ; l’assistant ne doit pas cacher silencieusement les autres données.

## 40.5 Critères d’acceptation

- un dirigeant comprend l’état de l’affaire en moins d’une minute ;
- les changements depuis la dernière session sont séparés de l’état global ;
- chaque blocage ouvre son action ;
- aucune synthèse ne masque un inconnu C1.

---

# 41. Spécification détaillée — Analyse / Exigence / Source

## 41.1 Objectif

Permettre à un professionnel de passer de **« SMART AO me dit quelque chose »** à **« je peux le vérifier »** sans perdre le fil.

## 41.2 Disposition cible desktop

```text
┌─────────────────────────┬──────────────────────────────────┐
│ Liste / filtres         │ Détail de l’exigence            │
│ C1 / prix / document    │                                  │
│ technique / contradiction│ Statut, portée, conséquence      │
│                         │ Action / responsable             │
│                         │                                  │
│                         │ [Voir la source]                 │
└─────────────────────────┴──────────────────────────────────┘
                                  ↓
                    panneau source latéral / partagé
```

## 41.3 Assistant

Le modèle peut expliquer une clause en langage opérationnel, mais doit séparer :

- texte source ;
- interprétation SMART AO ;
- conséquence possible ;
- décision requise.

Exemple :

```text
Le CCAP impose une retenue de garantie de 5 %.

Ce que cela signifie pour l’étude :
une partie des encaissements restera immobilisée jusqu’aux conditions de libération prévues au contrat.

Je peux l’ajouter au scénario de trésorerie, mais le montant final dépend du prix et du calendrier validés par le patron.

[Voir la clause] [Ajouter au contrôle financier]
```

## 41.4 Correction humaine

Un expert doit pouvoir corriger l’applicabilité ou la qualification sans modifier le texte source. La correction devient une validation traçable.

## 41.5 Critères d’acceptation

- source à un clic ;
- interprétation clairement distincte du texte ;
- correction humaine possible ;
- filtres C1/prix/document/technique/contradiction ;
- pas de perte de contexte à l’ouverture de la pièce.

---

# 42. Spécification détaillée — Dossier documentaire / Réponse

## 42.1 Objectif

Montrer exactement **ce que l’entreprise doit produire, remplir, récupérer, obtenir, signer ou remettre**.

## 42.2 Vue par défaut

La vue doit privilégier l’action, pas la taxonomie documentaire.

```text
À FAIRE AVANT DÉPÔT

À produire                         3
À remplir sur modèle acheteur      4
À obtenir d’un tiers               2
À signer                           1
À remettre physiquement            0
Bloquants                          2
```

## 42.3 Fiche document

Chaque document affiche :

- intitulé exact ;
- raison ;
- source ;
- phase ;
- lot/site/variante ;
- mode de traitement ;
- données nécessaires ;
- responsable ;
- validité ;
- signature ;
- statut ;
- prochaine action.

## 42.4 Assistant de production

Lorsqu’un modèle acheteur est imposé :

```text
Ce fichier doit être rempli sans modifier sa structure.
J’ai identifié 18 zones de saisie :
• 11 peuvent être préremplies avec des données validées ;
• 4 demandent une contribution technique ;
• 3 créent un engagement et nécessitent validation.

[Préremplir les 11 champs sûrs] [Voir les 7 champs à traiter]
```

Pour un mémoire libre :

```text
Je peux préparer cette section à partir de :
• 2 références validées ;
• 1 procédure QSE ;
• 3 exigences du CCTP.

Il manque encore la composition exacte de l’équipe.
Je laisserai ce point explicitement à compléter.

[Préparer le brouillon]
```

## 42.5 Critères d’acceptation

- distinction claire générer/remplir/récupérer/tiers/signature ;
- aucun document tiers généré ;
- original acheteur conservé ;
- engagements signalés avant validation ;
- statut documentaire compréhensible sans ouvrir les métadonnées complètes.

---

# 43. Spécification détaillée — Bureau de décision Patron

## 43.1 Objectif

Préparer une décision de dirigeant sans la transformer en score automatique.

## 43.2 Structure

Le bureau de décision présente des **dimensions**, chacune avec faits, inconnus et conditions :

- attractivité / stratégie ;
- éligibilité ;
- technique ;
- capacité ;
- partenaires ;
- couverture du prix ;
- marge ;
- trésorerie ;
- contrat ;
- engagement et délai.

## 43.3 Résumé SMART AO

```text
Je considère l’affaire prête pour une décision P3.

Points favorables
• capacité technique démontrée
• 3 références comparables
• partenaire critique confirmé

Points défavorables
• pic de trésorerie supérieur à votre seuil interne dans le scénario de paiement tardif
• prix fournisseur principal valable seulement 20 jours

Inconnus
• date de démarrage non confirmée

Je ne recommande pas un GO automatique.
La décision dépend du niveau d’exposition financière que vous acceptez.

[Comparer les scénarios] [Voir les preuves] [Décider]
```

Le vocabulaire « je considère » doit toujours signifier une **préparation de décision**, jamais une décision engageante.

## 43.4 Action de décision

GO / GO sous conditions / ATTENTE / NO-GO / ABANDON.

Toute condition est convertie en objet suivi avec responsable, échéance et critère de levée.

## 43.5 Critères d’acceptation

- aucun score global opaque ;
- faits/inconnus/hypothèses séparés ;
- données confidentielles protégées ;
- décision nominative et justifiée ;
- conditions suivies après la décision.

---

# 44. Spécification détaillée — Coffre de dépôt

## 44.1 Objectif

Faire du dernier contrôle un **rituel de confiance**, pas un bouton d’export.

## 44.2 Hiérarchie

1. statut autorisé/non autorisé ;
2. blocages ;
3. manifeste ;
4. contrôles de cohérence ;
5. signatures ;
6. version ;
7. canal de remise ;
8. marge temporelle ;
9. validation patron.

## 44.3 Assistant

```text
Le dépôt n’est pas encore autorisable.

Il reste 2 points :
1. l’attestation de visite est absente ;
2. la signature de l’AE doit être vérifiée pour cette phase.

Tout le reste du manifeste est prêt.

[Traiter l’attestation] [Vérifier la signature] [Voir le manifeste]
```

Une fois prêt :

```text
La version V7 est prête pour validation patron.
18/18 pièces requises sont présentes et contrôlées.
Aucun document remplacé ni donnée interne restreinte n’a été détecté.

La remise reste une action humaine.

[Examiner la version V7] [Autoriser le dépôt]
```

## 44.4 Après remise

Le reçu est rapproché du manifeste. L’assistant peut expliquer les écarts éventuels, mais ne doit jamais déclarer « dépôt réussi » si la preuve n’est pas cohérente.

## 44.5 Critères d’acceptation

- aucune hypothèse ZIP ;
- version exacte visible ;
- changement après autorisation = nouvelle validation ;
- reçu rapproché du paquet ;
- geste final humain sauf future décision explicite contraire.

---

# 45. États conversationnels, erreurs et abstention

L’assistant doit disposer d’un vocabulaire d’incertitude stable.

## 45.1 Quand l’IA ne dispose pas de preuve

```text
Je ne peux pas établir ce point avec les documents actuellement disponibles.
```

## 45.2 Quand un outil n’a pas pu lire un document

```text
Je n’ai pas pu exploiter ce fichier.
Je ne l’utilise donc pas pour conclure que le dossier est complet.

[Ouvrir le fichier] [Affecter une revue manuelle]
```

## 45.3 Quand les sources se contredisent

```text
Deux sources actives donnent des informations incompatibles.
Je conserve les deux valeurs et je ne choisis pas silencieusement.
```

## 45.4 Quand une action dépasse son autorité

```text
Je peux préparer la décision, mais seul le patron peut l’autoriser.
```

## 45.5 Quand une donnée est confidentielle

```text
Une information utile existe, mais votre rôle ne permet pas d’en afficher le détail.
```

Le ton de l’abstention doit rester utile : dire ce qui manque et comment avancer.

---

# 46. Microcopie et personnalité produit

SMART AO doit avoir une identité reconnaissable sans tomber dans l’anthropomorphisme excessif.

## 46.1 Principes

- parler en français professionnel BTP ;
- utiliser « je » avec parcimonie lorsqu’il clarifie l’action de l’assistant ;
- préférer « J’ai identifié… » à « Je pense que… » lorsque la preuve existe ;
- préférer « Je ne peux pas établir… » à une approximation ;
- parler de **l’entreprise** ou du **patron** pour les décisions ;
- ne jamais dire « j’ai décidé », « j’ai accepté » ou « j’ai déposé » pour une action humaine ;
- éviter le ton robotique comme le ton familier excessif.

## 46.2 Vocabulaire recommandé

```text
J’ai identifié…
Je vous propose de…
Ce point reste à confirmer…
Cette information vient de…
Cette exigence concerne…
Je ne peux pas conclure parce que…
Voici ce qui a changé…
Voici ce qui bloque…
Voici ce qui mérite votre décision…
```

## 46.3 Vocabulaire à éviter

```text
Tout est bon.
Aucun risque.
Vous allez gagner.
Cette clause est illégale.
Le dossier est complet.  [si la preuve est incomplète]
J’ai décidé de…
J’ai signé…
J’ai soumis l’offre…
```

---

# 47. Wireframes de référence

## 47.1 Accueil Patron — version guidée

```text
┌────────────────────────────────────────────────────────────────────┐
│ SMART AO                                      Entreprise X  Patron │
├────────────────────────────────────────────────────────────────────┤
│ BONJOUR — CE QUI MÉRITE VOTRE ATTENTION AUJOURD’HUI               │
│                                                                    │
│ 1  AP-HP — J-3 — attestation de visite manquante                  │
│ 2  Ville de X — décision P3 prête                                 │
│ 3  Filieris — nouveau rectificatif, impact BPU                    │
│                                                                    │
│ [Commencer par AP-HP]      [Voir toutes les priorités]             │
├────────────────────────────────────────────────────────────────────┤
│ DÉCISIONS À PRENDRE (2)           AFFAIRES SOUS TENSION (3)       │
│ • Ville X — P3                    • AP-HP — blocage C1             │
│ • RN12 — P2                       • Filieris — rectificatif        │
├────────────────────────────────────────────────────────────────────┤
│ MES AFFAIRES                                                       │
│ AP-HP       J-3   Remise     Fiabilité haute   Risque moyen        │
│ Filieris    J-6   Réponse    Fiabilité moyenne Risque élevé        │
│ RN12        J-12  Analyse    Fiabilité moyenne Risque élevé        │
├────────────────────────────────────────────────────────────────────┤
│ 12 nouvelles opportunités pertinentes        [Ouvrir le Radar]     │
└────────────────────────────────────────────────────────────────────┘
```

## 47.2 Affaire — assistant contextuel

```text
┌────────────────────────────────────────────────────────────────────┐
│ FILIERIS — LOT 01               J-6       GO SOUS CONDITIONS      │
│ Synthèse | Analyse | Réponse | Décision | Remise    [Demander à AO]│
├────────────────────────────────────────────────────────────────────┤
│ SMART AO                                                          │
│ Depuis hier : 1 réponse acheteur reçue. Elle lève une inconnue     │
│ sur le phasage mais crée un impact de prix à vérifier.             │
│ [Voir l’impact]                                                    │
├────────────────────────────────────────────────────────────────────┤
│ 3 BLOQUANTS          2 RISQUES PRIX         14/18 DOCUMENTS       │
│ ...                                                                │
└────────────────────────────────────────────────────────────────────┘
```

## 47.3 Panneau « Demander à SMART AO »

```text
┌──────────────────────────────┐
│ SMART AO — contexte FILIERIS │
├──────────────────────────────┤
│ Que voulez-vous vérifier ?   │
│                              │
│ Suggestions                  │
│ • Ce qui bloque le dépôt     │
│ • Les risques qui coûtent    │
│ • Ce qui reste non vérifié   │
│ • Les changements récents    │
│                              │
│ > _________________________  │
│                              │
│ Réponse courte               │
│ Preuves principales          │
│ Actions proposées            │
└──────────────────────────────┘
```

## 47.4 Mémoire Entreprise — vue Patron

```text
┌────────────────────────────────────────────────────────────────────┐
│ MON ENTREPRISE                                  Patron / Direction │
├────────────────────────────────────────────────────────────────────┤
│ SMART AO                                                          │
│ Votre base est exploitable. Trois éléments méritent une action :  │
│ • assurance RC : expire dans 19 jours ;                           │
│ • habilitation électrique de M. X : à revoir ;                    │
│ • tarif fournisseur Y : validité dépassée.                        │
│ [Traiter les 3 points]                                             │
├────────────────────────────────────────────────────────────────────┤
│ PRÉPARATION                                                        │
│ Identité ✓  Assurances !  Qualifications ✓  Équipe ✓  Références ✓│
├────────────────────────────────────────────────────────────────────┤
│ PATRIMOINE                                                         │
│ [Administratif] [Équipe] [Matériel] [Références] [Méthodes]       │
│ [Partenaires] [Produits] [Modèles]                                 │
│                                                                    │
│ ─────────────── DIRECTION UNIQUEMENT ───────────────────────────   │
│ [Prix & achats] [Finance] [Règles de marge] [REX sensibles]       │
├────────────────────────────────────────────────────────────────────┤
│ [Importer un dossier] [Ajouter un document] [Voir les expirations]│
└────────────────────────────────────────────────────────────────────┘
```

---

# 48. Critères d’acceptation spécifiques à l’expérience IA

Une expérience IA SMART AO n’est acceptable que si les tests suivants réussissent :

| Test | Résultat attendu |
|---|---|
| Briefing | Les priorités citées existent réellement et ouvrent les bons objets métier |
| Contexte | L’utilisateur n’a pas à réexpliquer l’affaire active lors d’une question contextuelle |
| Preuve | Toute affirmation critique de l’assistant permet d’ouvrir la source ou indique qu’aucune preuve suffisante n’existe |
| Confidentialité | L’assistant ne révèle jamais une donnée hors des droits du rôle courant |
| Mémoire Entreprise | Un fait propre à l’entreprise utilisé par l’assistant renvoie à une donnée validée, une preuve ou une décision explicite |
| Expiration | Une preuve expirée ou bientôt expirée est distinguée d’une preuve active et rapprochée des échéances des affaires |
| Source interne | Une donnée structurée extraite d’un document permet d’ouvrir l’original et sa version |
| Autorité | Une proposition de l’assistant ne devient jamais une décision humaine par simple formulation conversationnelle |
| Outils | Lorsqu’une réponse dépend d’une donnée du produit, l’assistant utilise la donnée/outillage prévu ou s’abstient |
| Rectificatif | Après changement de version, l’assistant ne continue pas à présenter une ancienne conclusion critique comme validée |
| Abstention | Un document illisible, absent ou non couvert produit un inconnu explicite, pas une réponse plausible |
| Continuité | Une session reprise restitue actions, décisions et changements depuis la dernière ouverture sans transformer les conversations brutes en vérités métier |
| Charge cognitive | L’assistant ne remonte pas plus de priorités que l’utilisateur ne peut raisonnablement traiter ; le reste reste accessible sans être imposé |
| Réversibilité | Un filtre ou tri créé en langage naturel reste visible et modifiable sous forme de critères structurés |
| Dégradation | Si le modèle conversationnel est indisponible, les fonctions critiques de preuve, décision, documents et remise restent utilisables |

---

# 49. Décisions fonctionnelles consolidées en v1.0

La v1.0 retient les décisions suivantes pour le futur prototype :

1. **SMART AO est AI-native, pas chat-first.**
2. **L’assistant est une couche transversale de guidance**, visible sur l’Accueil et dans l’Affaire.
3. **Une seule identité conversationnelle SMART AO** est exposée à l’utilisateur, même si plusieurs compétences ou outils existent en interne.
4. **Le modèle agit dans un harnais fonctionnel** composé du rôle, des droits, du contexte, des preuves, des outils et des règles de validation.
5. **La proactivité est limitée aux éléments pertinents, explicables et actionnables.**
6. **L’IA prépare ; l’humain engage.**
7. **Le choix du fournisseur de modèle reste technique et évalué**, même si une première implémentation peut volontairement commencer avec un fournisseur unique.
8. **La recherche des avis publiés reste native** dans le Radar ; l’IA peut transformer une intention commerciale en critères de recherche explicites.
9. **Affaire reste le centre opérationnel du produit** ; l’assistant ne crée pas un second univers parallèle.
10. **La Mémoire Entreprise devient le socle privé des faits propres à la société** : documents, preuves, moyens, personnes, prix, références, méthodes et règles validées.
11. **La conversation ne devient jamais une base de vérité implicite** : toute information qui engage le workflow doit être matérialisée comme fait, hypothèse, action, décision, preuve ou engagement.
12. **La confidentialité est portée par la donnée et le contexte IA**, pas seulement par les écrans.
13. **L’onboarding est progressif mais la préparation est prouvée** : import en masse possible, métadonnées proposées, validation nécessaire avant usage critique.
14. **Les expirations sont proactives et contextualisées aux affaires**, pas de simples rappels calendaires.
15. **La personnalisation n’impose pas une base de prix ou une taxonomie rigide** ; elle conserve toutefois provenance, validité, sensibilité, validation et historique comme invariants.

---

# 50. Audit croisé final et angles morts fermés

La v0.3 décrivait correctement la vision, les rôles, les cinq vues de l’Affaire, le Radar, la Mémoire Entreprise, le Coffre et l’assistant. La confrontation avec les cahiers métier v1.0, l’univers documentaire v1.0 et les référentiels actuels fait néanmoins apparaître des zones que l’architecture ne doit pas résoudre seule.[^23][^24]

| Domaine | Acquis de la v0.3 | Risque encore présent | Réponse de la v1.0 |
|---|---|---|---|
| Marchés privés | opportunité privée reconnue | parcours pensé surtout avec le vocabulaire du public | dossier contractuel privé, négociation, paiement et sous-traitance explicités |
| Collaboration | rôles et tâches définis | modification simultanée, absence, remplacement et désaccord non traités | règles de propriété, concurrence, délégation et passation |
| Confiance | preuve à un clic et abstention | « fiabilité » trop globale et pourcentages potentiellement trompeurs | préparation factuelle, couverture décomposée et classes de sortie IA |
| Erreurs | états illisible/inconnu | perte de connexion, session expirée, action partielle et retour arrière incomplets | reprise, confirmation, annulation et journal métier |
| Données | confidentialité par rôle | durée, sortie du client, suppression et usage secondaire peu visibles | cycle de vie, export, archivage, effacement et transparence d’accès |
| Accessibilité | simplicité et mobile évoqués | absence de cible testable clavier, lecteur d’écran, zoom et statuts | contrat d’accessibilité WCAG 2.2 AA et méthode RGAA en vigueur |
| IA | harnais et autorité humaine | nature des sorties, portée des corrections et évolution du comportement incomplètes | grammaire extraction/inférence/recommandation et apprentissage contrôlé |
| Mesure | recettes qualitatives | absence de seuils et protocole d’observation | tableau de mesures, corpus, rôles et conditions de réussite |
| Passage à l’architecture | frontières techniques posées | objets et effets fonctionnels dispersés | dictionnaire d’objets, commandes critiques et invariants de handoff |

### 50.1 Ce que la concurrence confirme, sans dicter le produit

Le benchmark dédié [SMART AO — Benchmark concurrentiel UX et parcours v1.0](SMART_AO_Benchmark_Concurrentiel_UX_Parcours_v1.0.md) compare vingt-deux solutions ou familles de solutions françaises et internationales sur la chaîne complète : veille, DCE, décision, prix, réponse, collaboration, remise et passation. Il distingue systématiquement parcours observable, fonction illustrée et promesse commerciale.

Les offres publiques confirment que l’analyse DCE, le GO/NO-GO, la base de connaissances, la rédaction, la traçabilité de source, les tâches et la collaboration deviennent des attentes de marché. Tenderbolt revendique ces fonctions dans un flux unifié ; Spigao relie détection, DCE, chiffrage et outils BTP.[^20][^21] Libel et Wanao installent les métaphores du dossier, de la grille de suivi et du dernier kilomètre ; Loopio et Responsive montrent la maturité des bibliothèques gouvernées, de l’affectation et des matrices d’exigences ; Procore et BuildingConnected démontrent la force de la comparaison côte à côte et de la continuité vers le contrat. Ces constats proviennent des éditeurs et ne démontrent ni leur qualité sur le corpus SMART AO ni leurs taux d’erreur.

La différenciation fonctionnelle de SMART AO ne peut donc pas reposer sur « résumer avec l’IA ». Elle repose sur la couverture prouvée du dossier, l’applicabilité, les rectificatifs, les MIRP, le prix et la trésorerie, les décisions nominatives, la confidentialité direction, le contrat réellement accepté et la passation vers l’exécution.

### 50.2 Doctrine d’interface issue du benchmark

SMART AO conserve les conventions déjà comprises par les patrons et les équipes BTP : liste d’affaires filtrable, vue maître–détail, arborescence de dossiers, aperçu PDF, tableau proche d’Excel, checklist, glisser-déposer, commentaires, historique et exports Word/Excel/PDF. Son empreinte ne consiste pas à déplacer arbitrairement les commandes, mais à ajouter à chaque convention une maîtrise nouvelle : source, version active, inconnu, contradiction, responsabilité, condition de décision et preuve d’achèvement.

Douze écrans doivent être prototypés et testés avant que l’architecture d’interface soit figée : Accueil Patron, Radar, fiche opportunité, import DCE, explorateur DCE, synthèse Affaire, registre MIRP, décision GO/NO-GO, Prix, Réponse, Coffre de remise et Passation. Le benchmark donne pour chacun la convention dominante et la question de compréhension à valider.

La règle de clôture est simple : **si une décision change ce que l’utilisateur voit, comprend, autorise, perd ou peut prouver, elle appartient à ce CCF**. Le futur cahier technique choisira comment rendre ce résultat possible.

---

# 51. Contrat d’expérience SMART AO

Le contrat d’expérience est la promesse stable faite à toute PME cliente. Il s’applique quels que soient le terminal, le fournisseur IA, le format du DCE ou la source de l’opportunité.

## 51.1 Les dix invariants

1. **Aucune conclusion critique sans état de preuve.**
2. **Aucune progression silencieuse lorsqu’un élément C1 reste inconnu, illisible ou contradictoire.**
3. **Aucune décision engageante attribuée à l’IA.**
4. **Aucune donnée restreinte révélée directement ou indirectement à un rôle non autorisé.**
5. **Aucune version remplacée utilisée comme si elle était active.**
6. **Aucune action irréversible sans conséquence annoncée et confirmation adaptée.**
7. **Aucune modification humaine perdue à cause d’un traitement automatique ou d’un conflit simultané.**
8. **Aucun statut global trompeur lorsque son dénominateur est incomplet.**
9. **Aucune remise déclarée réussie sans preuve externe cohérente.**
10. **Aucune dépendance au dialogue IA pour accomplir une fonction critique.**

## 51.2 La préparation ne se résume pas à un pourcentage

Un pourcentage peut être montré uniquement si son dénominateur est stable, explicite et consultable. « 80 % prêt » est interdit si des fichiers restent non lus, si un rectificatif n’est pas intégré ou si la liste des pièces exigées n’est pas établie.

La synthèse privilégie des faits :

```text
14/18 pièces exigées sont validées.
2 pièces sont à obtenir.
1 décision patron bloque l’autorisation.
1 fichier n’a pas pu être lu.
3 informations P1 manquent pour défendre le prix.
```

Les états globaux autorisés sont : **préparation non établie**, **non prêt**, **prêt sous conditions**, **prêt pour validation**, **autorisé** et **remis avec preuve**. Chaque état ouvre son détail.

## 51.3 Une action primaire, des issues secondaires

Chaque vue indique une action principale correspondant au prochain obstacle réel. Les actions secondaires restent accessibles sans concurrencer la priorité. En cas de désaccord ou d’incertitude, l’interface propose toujours une issue sûre : différer, demander, ouvrir la source, affecter un expert ou soumettre une décision.

Les recommandations françaises de conception rappellent qu’un service numérique doit permettre l’erreur, la contestation, la transparence et les tests avec des utilisateurs représentatifs.[^3] SMART AO applique cette doctrine aux décisions économiques et contractuelles de la PME.

## 51.4 Service blueprint du cycle de l’affaire

| Étape | Expérience visible | Travail préparé par SMART AO | Dépendance externe | Preuve de sortie |
|---|---|---|---|---|
| Découvrir | opportunité et raison de sa présence | agréger, dédupliquer, filtrer, dater | BOAMP, TED, invitation, saisie | source et fraîcheur |
| Qualifier | premiers motifs pour agir ou écarter | rapprocher métier, territoire, délai et références | données de l’entreprise | décision P0 |
| Recevoir | couverture du dossier et limites | inventorier, ouvrir archives, reconnaître versions | fichiers et liens reçus | inventaire horodaté |
| Comprendre | exigences, inconnus, risques et MIRP | extraire, relier, confronter et signaler | expert métier si ambigu | registre sourcé |
| Décider | faits, scénarios et conditions | préparer la décision sans la prendre | patron, DAF, travaux | décision et conditions |
| Produire | dossier de réponse vivant | préremplir, rédiger, contrôler, affecter | tiers, signataires, modèles | pièces validées |
| Autoriser | version candidate et écarts | rapprocher prix, engagements et documents | patron/signataire | P4 puis P5 |
| Remettre | canal, progression et résultat | préparer le paquet et rapprocher le reçu | profil acheteur, courriel, remise physique | manifeste + reçu |
| Négocier | changements et concessions | comparer les versions et recalculer les impacts | acheteur/client | P6 et accord final |
| Transmettre | contrat vendu et points de vigilance | assembler la passation | conducteur et équipe chantier | P7 |
| Apprendre | prévu/réel et cause validée | proposer un REX contextualisé | données d’exécution | connaissance réutilisable |

---

# 52. Parcours fonctionnel des marchés privés

Le privé n’est pas une variante du public sans RC. Le contrat se construit souvent à partir de plusieurs échanges dont l’ordre et la portée doivent être établis. Les contrats légalement formés obligent les parties ; le produit doit donc rendre visible ce qui a été proposé, réservé, accepté et modifié.[^25]

## 52.1 Entrées possibles

Une affaire privée peut commencer par :

- une invitation ou un dossier reçu par courriel ;
- un lien vers une plateforme privée ;
- un dossier transmis par une entreprise générale ;
- un devis demandé à la suite d’une visite ou d’une relation existante ;
- un contrat-cadre et un nouveau bon de commande ;
- une consultation d’un promoteur, d’une foncière, d’un syndic ou d’un industriel ;
- une saisie manuelle par le patron.

L’utilisateur choisit ou confirme le **cadre présumé** : direct professionnel, sous-traitance, promotion/VEFA, copropriété/particulier, maintenance/accord-cadre ou autre. Le mot « présumé » reste visible jusqu’à validation.

## 52.2 Dossier contractuel privé

La vue Analyse ajoute un sous-ensemble **Contrat proposé** :

| Question | Éléments rapprochés | Résultat visible |
|---|---|---|
| Qui contracte ? | sociétés, établissements, signataires, pouvoirs | parties confirmées ou incohérence |
| Sur quoi ? | devis, DPGF/BPU, descriptifs, plans, exclusions | périmètre inclus, exclu ou ambigu |
| Selon quelles pièces ? | marché, commande, CGA/CGV, clauses, norme citée | hiérarchie déclarée, prouvée ou à négocier |
| À quel prix ? | offre initiale, remises, variantes, négociation | prix par version et conditions |
| Dans quel délai ? | planning, ordre de démarrage, phasage, validité | jalons et inconnus contractuels |
| Comment être payé ? | avance, situations, validation, échéance, retenue, garantie | courbe et protections à vérifier |
| Avec quels tiers ? | sous-traitants, cotraitants, fournisseurs critiques | engagement et protection documentaire |
| Comment clôturer ? | réception, réserves, DOE, décompte, solde | obligations et preuves futures |

## 52.3 Négociation et formation de l’accord

Chaque envoi ou réception susceptible de modifier l’affaire porte un statut : **proposition**, **contre-proposition**, **réserve**, **accepté**, **refusé**, **sans effet établi** ou **à qualifier**. Un courriel n’est jamais promu automatiquement au rang de clause acceptée.

La vue de mise au point doit répondre :

```text
CE QUI A CHANGÉ DEPUIS NOTRE OFFRE V3
• prix : remise de 1,5 % demandée, non acceptée ;
• délai : démarrage avancé de 14 jours, impact capacité non validé ;
• paiement : validation des situations modifiée ;
• technique : prestation de rebouchage ajoutée, coût non couvert.

STATUT : ACCORD NON PRÊT À SIGNER
```

## 52.4 Trésorerie et protections

Le produit signale les clauses et pièces relatives aux acomptes, délais, validation des situations, retenues, cautionnements, délégations et garanties. La retenue privée couverte par la loi de 1971 est plafonnée à 5 % et suit un mécanisme de consignation ou de caution ; l’article 1799-1 du code civil prévoit, sous conditions et exceptions, une garantie de paiement au-dessus du seuil réglementaire.[^26][^27]

SMART AO n’affiche jamais « clause illégale ». Il affiche : texte trouvé, règle de référence, champ d’application à confirmer, montant exposé, personne à consulter et effet sur la décision.

## 52.5 Sous-traitance privée

Avant qu’un sous-traitant soit considéré comme sécurisé, la vue Partenaire vérifie au minimum : identité, périmètre, prix, acceptation, agrément des conditions de paiement, assurance, qualification, caution ou délégation lorsque requise, validité de l’offre et date de mobilisation. La loi de 1975 rend ces sujets documentaires déterminants dans les marchés privés comme publics.[^28]

L’absence d’une protection attendue bloque le statut « partenaire confirmé ». Le patron peut poursuivre l’étude, mais le produit conserve une condition nominative avant le démarrage ou l’engagement contractuel.

## 52.6 Remise et passation privées

Le canal peut être un courriel, une plateforme, un lien documentaire, une remise physique ou une combinaison. Le Coffre conserve : destinataire, adresse ou espace, objet du message, pièces exactes, version, date/heure, accusé ou réponse, et limites de la preuve. Une copie dans « éléments envoyés » prouve un envoi, pas nécessairement une réception ou une acceptation. Pour le public, le produit respecte le canal et la règle de nouveau dépôt définis par la consultation au lieu de les déduire de l’usage habituel.[^19]

En cas de gain, la passation transmet le **contrat accepté**, pas seulement le dernier devis produit. Toute réserve non reprise dans l’accord final est signalée comme potentiellement perdue et soumise au responsable contractuel.

---

# 53. Collaboration, responsabilité et travail simultané

Le produit doit aider une petite équipe sans reproduire la lourdeur d’un outil de gestion de projet généraliste.

## 53.1 Propriété de l’action

Chaque objet nécessitant un travail possède au plus un responsable principal, avec contributeurs et valideur distincts. « Toute l’équipe » n’est pas un responsable. Une délégation indique auteur, bénéficiaire, périmètre, début, fin et possibilité de révocation.

## 53.2 Commentaire, correction, validation et décision

Ces actes ne doivent pas être confondus :

| Acte | Effet |
|---|---|
| Commenter | apporte un contexte sans changer l’état officiel |
| Corriger | propose ou applique une nouvelle valeur avec historique |
| Valider | autorise l’usage de la valeur pour une phase donnée |
| Décider | engage l’entreprise dans la limite de l’autorité du décideur |
| Déroger | accepte explicitement un risque ou un manque pour une porte donnée |

Un « pouce levé », un message libre ou l’absence d’objection ne remplace jamais une validation formelle.

## 53.3 Modifications simultanées

Lorsque deux personnes travaillent sur le même objet :

- la présence de l’autre est visible sans exposer inutilement son activité ;
- une section en cours de modification indique son auteur ;
- aucun enregistrement ne doit écraser silencieusement une modification plus récente ;
- le conflit montre les deux versions, leurs auteurs et leurs dates ;
- la résolution exige un choix ou une fusion contrôlée ;
- toute validation antérieure est rouverte si la substance validée change.

Pour les modèles Word ou Excel imposés, SMART AO doit éviter de promettre une édition simultanée qu’il ne peut garantir. Il peut réserver le document à un éditeur, gérer les contributions par section ou imposer une réconciliation explicite.

## 53.4 Absence, remplacement et urgence

Un responsable absent peut être remplacé sans perdre le contexte. La passation affiche : objectif, dernière action, sources consultées, points ouverts, décisions déjà prises, échéance et niveau d’accès. Le remplaçant ne reçoit pas automatiquement les secrets que détenait le titulaire précédent.

Si une échéance approche et qu’une tâche C1 n’a plus de responsable disponible, l’escalade est adressée au rôle de secours défini par l’entreprise. Elle ne repose pas sur une personne unique codée en dur.

## 53.5 Partage externe ciblé

Un tiers reçoit seulement un paquet explicite : question, documents nécessaires, réponse attendue, échéance et droit de téléchargement ou dépôt. Avant partage, l’utilisateur voit les destinataires et toutes les pièces. Après partage, il peut révoquer l’accès futur ; le produit précise qu’une copie déjà téléchargée ne peut pas être rappelée.

## 53.6 Matrice d’autorité par défaut

| Action | Patron | Responsable d’offre | Expert/DAF/administratif | Administrateur | Tiers |
|---|---|---|---|---|---|
| Voir le DCE de l’Affaire | oui | oui | périmètre affecté | non par fonction | paquet partagé |
| Voir marge et prix plancher | oui | non | DAF/métreur si délégué | non par fonction | non |
| Corriger une exigence | oui | oui | proposer/corriger sur périmètre | non | non |
| Valider un point technique | si compétent ou délégué | selon délégation | expert désigné | non | avis seulement |
| Décider P0 à P7 | oui ou délégataire défini | préparation | avis | non | non |
| Autoriser la remise | signataire habilité | préparation | contrôle spécialisé | non | non |
| Gérer utilisateurs et droits | propriétaire/délégataire | non | non | oui, sans accès métier automatique | non |
| Partager à l’extérieur | selon politique | si autorisé | non par défaut | paramètre la politique | reçoit seulement |

L’administration technique ne donne pas automatiquement accès aux marges, documents bancaires ou affaires. Toute assistance exceptionnelle nécessitant un accès est bornée, annoncée et journalisée.

---

# 54. Erreurs, réversibilité et reprise

La confiance se construit surtout lorsque quelque chose se passe mal.

## 54.1 Brouillon et enregistrement

- une saisie longue est enregistrée comme brouillon sans la valider ;
- l’utilisateur voit l’heure du dernier enregistrement confirmé ;
- une fermeture ou session expirante avertit si une donnée n’est pas enregistrée ;
- le retour à une version antérieure ne supprime pas l’historique ;
- un traitement IA ne remplace pas une correction humaine sans comparaison visible.

## 54.2 Actions à conséquence

Avant une suppression, un remplacement de pièce active, une validation, une dérogation, une autorisation d’offre ou un partage externe, SMART AO affiche : objet concerné, conséquence, personnes ou documents touchés et possibilité de retour arrière.

La confirmation est proportionnée. Une tâche banale ne nécessite pas une fenêtre bloquante ; une autorisation P5 ou une suppression définitive exige une formulation claire et une action non ambiguë.

## 54.3 Matrice de reprise

| Incident | Message utile | Ce qui reste utilisable | Reprise attendue |
|---|---|---|---|
| connexion interrompue | « Connexion perdue, votre brouillon local est conservé » si cela est vrai | consultation locale disponible | synchroniser ou résoudre le conflit |
| session expirée | raison et état de sauvegarde | aucun secret affiché | se réauthentifier puis reprendre au même point |
| analyse longue échouée | fichiers traités et non traités | résultats confirmés séparés | relancer seulement le périmètre échoué |
| fichier rejeté | nom, raison compréhensible et limite | autres fichiers poursuivent | corriger ou affecter revue manuelle |
| document supprimé de la source | donnée dérivée marquée orpheline | historique selon droits | restaurer, remplacer ou invalider |
| rectificatif reçu pendant validation | validation suspendue | ancienne version consultable | analyser l’impact puis revalider |
| source externe indisponible | dernière fraîcheur connue | affaires existantes | ne pas présenter le Radar comme à jour |
| modèle IA indisponible | fonctions IA signalées indisponibles | preuves, tâches, décisions, documents et Coffre | reprendre sans perte quand le service revient |

## 54.4 Confirmation d’une transaction

Après une action engageante, une page ou un état persistant donne : résultat, référence, date/heure, auteur, version, ce qui va se passer ensuite et moyen de conserver la preuve. Ce principe, recommandé pour les transactions numériques, évite qu’un simple toast éphémère porte la seule confirmation d’une remise ou décision.[^18]

---

# 55. Confiance et interaction avec l’intelligence artificielle

Les recherches sur l’interaction humain–IA recommandent d’expliquer ce que le système sait faire, de permettre une correction efficace, de montrer pourquoi il agit, de limiter son initiative en cas de doute et de notifier les changements de comportement.[^8] Le NIST considère la confabulation comme un risque normal des systèmes génératifs et recommande de la traiter par l’évaluation, la documentation et des mesures adaptées au contexte.[^7] La CNIL recommande de partir d’usages concrets plutôt que d’introduire une IA générative sans finalité précise.[^11]

## 55.1 Six classes de sortie visibles

| Classe | Formulation autorisée | Preuve attendue | Autorité |
|---|---|---|---|
| Extraction | « Le RC indique… » | emplacement source exact | aucune décision |
| Rapprochement | « Ces deux passages traitent du même délai » | deux sources consultables | à confirmer si critique |
| Inférence | « Cela peut affecter le planning parce que… » | faits + raisonnement métier court | hypothèse visible |
| Recommandation | « Je propose de poser cette question » | objectif, risques et alternatives | humain décide |
| Brouillon | « Projet de réponse » | sources utilisées et données manquantes | relecture obligatoire |
| Action préparée | « Prêt à envoyer/valider » | objet exact, destinataire et effet | confirmation habilitée |

Une réponse peut combiner plusieurs classes, mais chaque partie critique doit rester identifiable. SMART AO ne montre pas une « pensée interne » détaillée ; il montre les faits, les règles utiles, les limites et le chemin vérifiable vers le résultat.

## 55.2 Couverture de preuve, pas confiance décorative

Un indice numérique de confiance IA n’est pas affiché s’il ne possède pas une interprétation testée. Les libellés admis sont factuels :

- **preuve directe trouvée** ;
- **preuves concordantes** ;
- **source unique à confirmer** ;
- **inférence à valider** ;
- **source contradictoire** ;
- **aucune preuve exploitable** ;
- **document non lu ou hors périmètre**.

## 55.3 Correction et portée

Lorsqu’un utilisateur corrige l’IA, il choisit la portée : cette phrase, cette exigence, cette affaire, ce modèle documentaire ou la Mémoire Entreprise. Une correction locale ne devient jamais une règle globale par défaut.

Le produit montre ce que la correction va invalider : brouillon, synthèse, engagement, décision ou document. Les contenus concernés repassent à l’état « à vérifier » ; l’ancienne valeur reste dans l’historique.

## 55.4 Documents hostiles ou trompeurs

Un DCE, une pièce jointe ou un texte externe est une **source à analyser**, jamais une instruction d’administration adressée à SMART AO. Si un document contient des ordres visant l’assistant, demande d’ignorer les règles, extraction de secrets ou lien suspect, le produit :

1. n’exécute pas l’ordre ;
2. poursuit l’analyse documentaire dans un cadre borné ;
3. marque le passage suspect ;
4. n’expose aucune donnée d’une autre affaire ou de la Mémoire Entreprise ;
5. demande une revue humaine si le passage affecte le contenu métier.

L’ANSSI recommande une posture de prudence et une analyse de risques pour l’intégration de l’IA générative.[^16] Ce besoin doit être visible dans l’expérience avant de devenir une mesure technique.

## 55.5 Évolution du comportement

Une amélioration du modèle, des règles ou du catalogue peut modifier les résultats. Pour toute évolution matérielle, l’utilisateur voit : date, capacités touchées, éventuel besoin de revalidation et moyen de signaler une régression. Une conclusion déjà validée ne change pas silencieusement parce qu’un modèle a été mis à jour.

## 55.6 Transparence et culture IA

L’identité SMART AO rend évident quand une personne interagit avec une IA et quand un contenu a été préparé par elle. Cette transparence rejoint l’article 50 du règlement européen sur l’IA.[^10] L’entreprise doit également pouvoir former ses utilisateurs selon leur rôle, leur expérience et le contexte d’usage, conformément à l’exigence de culture IA de l’article 4.[^9]

---

# 56. Accessibilité et conditions réelles d’usage

L’accessibilité est une exigence de qualité dès la conception. La cible produit est **WCAG 2.2 niveau AA**, contrôlée avec la méthode RGAA 4.1.2 tant qu’elle est la version française publiée ; la future RGAA 5 fera l’objet d’une veille sans retarder les travaux actuels.[^5][^6]

Cette cible produit ne préjuge pas du champ exact des obligations légales de chaque client. Elle évite de bâtir une interface inutilisable par un patron, un métreur ou un administratif ayant une limitation visuelle, motrice, cognitive ou temporaire.

## 56.1 Exigences observables

- toutes les actions sont utilisables au clavier dans un ordre logique ;
- le focus reste visible et n’est pas masqué par un panneau ou une modale ;
- le zoom texte à 200 % et le réajustement n’empêchent pas une tâche critique ;
- la couleur n’est jamais le seul porteur de criticité, état ou action ;
- chaque icône possède un nom accessible et un libellé compréhensible ;
- les statuts d’analyse et messages asynchrones sont annoncés aux technologies d’assistance ;
- tableaux, filtres et pièces jointes ont une alternative navigable ;
- le glisser-déposer possède une alternative par sélection de fichiers ;
- les zones tactiles ont une taille suffisante et ne reposent pas sur des gestes fins ;
- les erreurs sont résumées, localisées et expliquent comment se corriger ;
- l’authentification accepte les gestionnaires de mots de passe et le collage des codes lorsque la sécurité le permet ;
- une limite de temps avertit, permet de prolonger et protège le brouillon ;
- les graphiques de marge ou trésorerie possèdent une lecture textuelle équivalente ;
- l’accès « Demander à SMART AO » reste placé de manière cohérente.

WCAG 2.2 ajoute notamment des exigences sur le focus non masqué, la taille minimale des cibles, l’aide cohérente, la saisie redondante et l’authentification accessible.[^5] Les recommandations DesignGouv insistent également sur les formulaires testés avec des utilisateurs, les erreurs explicites et l’interdiction de transmettre une information par la seule couleur.[^4]

## 56.2 Documents sources inaccessibles

SMART AO ne peut pas rendre rétroactivement accessible chaque PDF ou tableur reçu. Il doit toutefois fournir, lorsque possible : texte extrait, structure, zoom, recherche, navigation page par page et description de l’état de lecture. Si la conversion perd une information, l’original et la limite restent visibles.

## 56.3 Terrain et connectivité dégradée

Pendant une visite, l’utilisateur doit pouvoir capturer notes, photos et constats lorsque le réseau est instable. L’interface distingue **conservé sur l’appareil**, **en attente de synchronisation** et **synchronisé**. Une photo non synchronisée ne peut pas être présentée comme une preuve partagée avec l’équipe.

---

# 57. Cycle de vie des données et confiance du client

La Mémoire Entreprise contient des secrets commerciaux, des données personnelles, des prix et des documents tiers. L’expérience doit rendre les règles de traitement visibles sans transformer chaque écran en notice juridique.

## 57.1 Finalité et minimisation

Lorsqu’une donnée est demandée, SMART AO indique son usage et son caractère nécessaire ou facultatif. Les données de localisation, carnets d’adresses ou documents sans lien avec l’affaire ne sont pas collectés « au cas où ». La CNIL recommande de limiter données et journaux à ce qui est nécessaire, d’organiser l’exercice des droits et d’associer une durée à chaque catégorie.[^13][^22]

## 57.2 Tableau de gouvernance de l’entreprise

Le patron ou l’administrateur habilité peut voir :

- catégories détenues ;
- finalités ;
- niveaux de sensibilité ;
- personnes et rôles ayant accès ;
- partages externes actifs ;
- durées ou critères de conservation ;
- éléments à archiver ou effacer ;
- opérations sensibles récentes ;
- fournisseurs externes impliqués selon le service choisi ;
- règle d’utilisation ou non des données pour améliorer un modèle.

La qualification juridique du fournisseur IA dépend de la configuration et doit être analysée au cas par cas ; le CCF exige donc une information claire sur le rôle des prestataires et leurs usages, sans présumer une qualification unique.[^12]

## 57.3 Sortie, export et suppression

Avant la fin du contrat SMART AO, l’entreprise peut obtenir un export exploitable de ses fichiers originaux, métadonnées, décisions, historiques utiles, manifestes et preuves. L’export indique ce qui ne peut pas être transféré pour des raisons de droits, de format ou de sécurité.

La suppression suit un parcours explicite : périmètre, conséquences, obligations de conservation ou contentieux, date d’effet, éléments archivés, sauvegardes concernées et preuve finale. Les données personnelles suivent un cycle base active, archivage intermédiaire et suppression/anonymisation selon la finalité et les obligations applicables.[^14]

## 57.4 Journal métier visible

Les opérations de création, consultation sensible, partage, modification, validation, autorisation, export et suppression sont traçables avec auteur, date/heure, nature et objet. Le journal ne duplique pas le contenu sensible. La CNIL recommande une telle traçabilité et une durée de conservation justifiée pour les journaux.[^15]

L’utilisateur habilité peut distinguer : action humaine, traitement automatique, proposition IA et intervention d’assistance. Un administrateur ne peut pas réécrire l’historique d’une décision comme si elle avait été prise par un autre utilisateur.

## 57.5 Authentification proportionnée

Les actions sensibles — administration, partage externe, export complet, modification de droits et autorisation de dépôt — peuvent exiger une authentification renforcée selon l’analyse de risque. L’ANSSI recommande de privilégier l’authentification multifacteur et d’adapter sa robustesse au contexte.[^17]

---

# 58. Temps, échéances et notifications

Dans un appel d’offres, une erreur d’heure peut annuler plusieurs semaines de travail. Le temps devient donc un objet métier prouvé.

## 58.1 Fiche d’échéance

Chaque échéance critique conserve :

- nature : question, visite, candidature, dépôt, validité, renouvellement, attribution ou autre ;
- date et heure exactes ;
- fuseau ou convention de la source ;
- source, version et emplacement ;
- canal ou lieu ;
- marge de sécurité interne distincte ;
- auteur de la confirmation ;
- statut : détectée, à confirmer, confirmée, modifiée, dépassée ;
- affaires, documents et actions dépendants.

L’affichage combine date absolue et compte à rebours : **« 3 octobre 2026 à 12:00, heure indiquée par la plateforme — J-6 »**. Le compte à rebours seul est interdit.

## 58.2 Rectification d’une date

Une nouvelle date ne remplace pas silencieusement l’ancienne. L’utilisateur voit le changement, sa source et les actions recalculées. Toute autorisation fondée sur le délai antérieur est requalifiée si le changement touche capacité, prix, validité fournisseur ou calendrier de remise.

## 58.3 Budget d’attention

Les notifications sont regroupées par événement et affaire. Un même rectificatif ne crée pas dix alertes indépendantes. L’utilisateur peut différer une alerte avec une date de retour ; masquer définitivement une alerte C1 requiert un motif ou une règle d’organisation.

Les canaux initiaux sont : centre de notifications dans SMART AO et courrier électronique pour les événements critiques configurés. Le contenu du courriel reste minimal lorsqu’il concerne une affaire restreinte ; il conduit vers l’application après authentification.

---

# 59. Onboarding, aide, culture IA et adoption

Une PME ne doit pas comprendre tout SMART AO avant sa première affaire. Elle doit comprendre les limites au moment où elles comptent.

## 59.1 Première valeur

Le démarrage propose trois chemins : importer un DCE réel, explorer un dossier de démonstration anonymisé ou préparer les preuves essentielles de l’entreprise. Le dossier de démonstration est clairement séparé des données réelles et peut être réinitialisé.

La première session doit permettre d’obtenir une sortie utile sans paramétrage exhaustif : inventaire du dossier, échéance détectée, premiers inconnus et prochaine action. Aucun objectif arbitraire en minutes n’est fixé avant test avec des professionnels.

## 59.2 Aide dans le contexte

L’aide explique d’abord l’action courante, puis propose la doctrine complète. Elle utilise les mots du BTP et des exemples issus du type d’affaire. Une définition de C1, MIRP, preuve tierce ou dérogation s’ouvre sans quitter la tâche.

## 59.3 Formation par rôle

| Rôle | Compétence minimale |
|---|---|
| Patron | portes P0–P7, risques, secrets, dérogations, limites IA |
| Responsable d’offre | versions, exigences, preuves, documents et Coffre |
| Métreur/expert | MIRP, hypothèses, interfaces et validation technique |
| Administratif | titulaires, validités, phases et preuves tierces |
| DAF | scénarios, paramètres, exposition et confidentialité |
| Administrateur | utilisateurs, droits, partages, conservation et incidents |

Chaque personne doit savoir que l’IA peut se tromper, comment ouvrir une preuve, corriger une proposition et signaler un incident. Cette formation constitue une réponse opérationnelle à l’exigence européenne de culture IA.[^9]

## 59.4 Assistance humaine

L’utilisateur peut signaler un résultat erroné, une fuite potentielle, un document impossible à traiter ou une remise en difficulté. La demande de support inclut, avec accord, les références techniques nécessaires sans joindre automatiquement tout le DCE ou les secrets de l’affaire.

---

# 60. Mesure de la qualité produit

SMART AO est évalué sur la protection du travail et de la marge, pas sur le nombre de textes générés.

## 60.1 Tableau de mesure

| Dimension | Mesure | Échec critique |
|---|---|---|
| Compréhension | l’utilisateur explique correctement état, cause et prochaine action | il croit le dossier complet malgré un fichier non lu |
| Décision | temps et étapes pour atteindre une décision défendable | un score masque un inconnu déterminant |
| Exigences | rappel et précision sur jeu annoté, avec résultat par criticité | une C1 prouvée du corpus est absente sans signal |
| Sources | taux d’affirmations critiques ouvrant la bonne preuve | source erronée ou version remplacée |
| Prix | prestations/exigences sans couverture correctement signalées | prix déclaré prêt malgré une MIRP P1 non traitée |
| Documents | pièces, modèles, signatures et phases correctement classés | preuve tierce fabriquée ou mauvais modèle remis |
| Rectificatifs | impacts retrouvés et validations rouvertes | conclusion critique obsolète maintenue valide |
| Confidentialité | tests croisés de rôles et exports | toute révélation non autorisée |
| Collaboration | reprise après absence/conflit sans perte | modification validée écrasée silencieusement |
| Remise | paquet autorisé rapproché du reçu | faux message de succès ou mauvaise version |
| IA | abstention, correction et portée sur cas hostiles | invention engageante non signalée |
| Accessibilité | audit automatisé et manuel + tâches clavier/lecteur d’écran | tâche critique impossible sans souris ou par la seule couleur |
| Adoption | taux de tâches terminées et raisons d’abandon | utilisateur obligé de contourner SMART AO pour une action cœur |

Les seuils quantitatifs seront fixés après constitution du jeu de référence. Les résultats doivent toujours être ventilés par type de dossier, format, corps d’état, rôle et criticité afin qu’une moyenne ne masque pas un échec dangereux.

## 60.2 Protocole de recherche utilisateur

Le protocole minimal réunit des dirigeants, responsables d’offres, métreurs, administratifs et conducteurs issus de PME de tailles et métiers différents. Les tests utilisent des tâches réalistes et des données anonymisées : découverte, première décision, rectificatif, prix, production, autorisation, remise, passation et marché privé.

Pour chaque séance : scénario identique, observation des hésitations, résultat obtenu, erreur, temps, besoin d’aide, compréhension de la preuve et confiance déclarée. Une phrase « j’aime bien » ne remplace pas la réussite de la tâche. DesignGouv recommande de tester avant de développer avec des utilisateurs représentatifs et de piloter par l’impact.[^3]

## 60.3 Validation de l’IA

Les sorties IA sont testées sur un jeu gelé et annoté indépendamment par au moins deux professionnels lorsque l’enjeu le justifie. Les désaccords d’experts sont conservés. Un changement de modèle ou de règle repasse les recettes critiques ; le NIST recommande une démarche structurée de test, évaluation, vérification et validation des systèmes d’IA.[^7]

---

# 61. Recettes UX complémentaires de la v1.0

Ces recettes complètent UX-01 à UX-08 et REC-01 à REC-28.

| ID | Scénario | Résultat observable exigé |
|---|---|---|
| UX-09 | Deux collaborateurs corrigent la même exigence | les deux versions sont conservées, le conflit est visible, aucune correction n’est perdue |
| UX-10 | Le responsable d’offre part en congé à J-4 | le remplaçant reprend sources, actions et décisions sans recevoir les secrets non délégués |
| UX-11 | Session expirée pendant une rédaction | après authentification, le brouillon et le contexte sont récupérés ou la perte est explicitement annoncée |
| UX-12 | L’analyse échoue sur 3 fichiers sur 40 | 37 résultats restent utilisables ; les 3 échecs et leurs impacts sont isolés |
| UX-13 | TED et BOAMP publient des avis apparentés | provenance et rapprochement visibles ; l’utilisateur décide s’il s’agit de la même opportunité |
| UX-14 | La source BOAMP est indisponible | dernière date de rafraîchissement visible ; aucune promesse d’exhaustivité ou fraîcheur |
| UX-15 | Invitation privée reçue par courriel | création d’une affaire sans vocabulaire public imposé ; contrat proposé à reconstruire |
| UX-16 | Commande privée contredit le devis | contradictions, versions et décision de mise au point visibles avant acceptation |
| UX-17 | Sous-traitant sans garantie documentaire suffisante | partenaire non confirmé et condition de poursuite adressée au bon responsable |
| UX-18 | Courriel de remise privée sans accusé | état « envoyé, réception non prouvée » et action de suivi |
| UX-19 | DCE contient une instruction destinée à détourner l’IA | instruction non exécutée, passage signalé, aucune donnée interne exposée |
| UX-20 | L’utilisateur corrige un fait entreprise | choix de portée, impacts et revalidations visibles avant propagation |
| UX-21 | Le fournisseur IA est indisponible | navigation, sources, tâches, validations et Coffre restent utilisables |
| UX-22 | Patron exporte puis ferme son compte | périmètre exporté, exclusions, calendrier de suppression et preuve finale compréhensibles |
| UX-23 | Partage externe envoyé au mauvais contact puis révoqué | accès futur coupé, historique conservé, limite sur copie téléchargée expliquée |
| UX-24 | Dépôt à 12:00 avec utilisateur dans un autre fuseau | heure source et heure locale distinguées, aucune conversion silencieuse |
| UX-25 | Utilisateur clavier traite un blocage C1 | source, action, validation et retour à la liste réalisables sans souris |
| UX-26 | Lecteur d’écran reçoit la fin d’une analyse | statut annoncé sans déplacement de focus inattendu, résultats accessibles |
| UX-27 | Visite sans réseau | constats indiqués comme locaux puis en attente et enfin synchronisés |
| UX-28 | Modèle ou règles changent après validation | anciennes décisions restent figées ; éléments nécessitant une nouvelle revue clairement listés |

Une recette échoue si le résultat correct dépend d’une explication orale de l’équipe produit. Le vocabulaire, la preuve et la prochaine action doivent suffire dans l’interface.

---

# 62. Dictionnaire fonctionnel remis à l’architecture

## 62.1 Objets métier minimaux

| Objet | Question à laquelle il répond | États ou propriétés indispensables |
|---|---|---|
| Opportunité | mérite-t-elle une action ? | source, fraîcheur, pertinence expliquée, suivi/écart |
| Affaire | quel travail et quelle décision poursuivons-nous ? | cadre, lot, responsable, porte, échéances, version active |
| Version documentaire | avec quel dossier travaillons-nous ? | reçu, actif, remplacé, comparaison, couverture de lecture |
| Exigence | que demande ou impose la source ? | formulation, source, portée, phase, criticité, état de connaissance |
| Preuve | sur quoi repose la conclusion ? | origine, titulaire, version, validité, droits, applicabilité |
| Inconnu | qu’est-ce qui empêche de conclure ? | cause, impact, action, responsable, échéance |
| Hypothèse | quelle valeur choisit temporairement l’entreprise ? | auteur, motif, portée, durée, validateur, impacts |
| Risque | que peut-il arriver et avec quel effet ? | cause, conséquence, exposition, traitement, propriétaire |
| Tâche | qui doit faire quoi et quand ? | responsable, échéance, dépendances, preuve de fin |
| Question | que faut-il demander à un tiers ? | source, brouillon, validation, envoi, réponse, impacts |
| Engagement | que promet l’offre ou le contrat ? | formulation, coût, responsable, phase, source de création |
| Décision | qui autorise quoi ? | porte, auteur habilité, date, motif, conditions, preuves |
| Document réponse | que doit-on produire ou obtenir ? | modèle, mode, version, statut, validation, confidentialité |
| Élément Entreprise | que savons-nous sur la société ? | source, titulaire, validité, sensibilité, validation, réemploi |
| Manifeste | que contient exactement la remise ? | exigé, présent, version, format, empreinte, canal |
| Reçu | que prouve le tiers ? | canal, date/heure, référence, paquet rapproché, limites |
| Partage | qui peut voir quoi et jusqu’à quand ? | destinataire, périmètre, droits, expiration, révocation |

## 62.2 Actions critiques et effets

| Action | Conditions fonctionnelles | Effet obligatoire |
|---|---|---|
| Créer une Affaire | opportunité ou invitation identifiée | provenance conservée, aucun GO implicite |
| Activer une nouvelle version DCE | comparaison disponible ou limites déclarées | anciennes conclusions touchées rouvertes |
| Valider une preuve | personne habilitée, portée et source visibles | usage autorisé seulement pour la portée validée |
| Accepter une hypothèse | impact et alternatives visibles | auteur, motif, durée et objets affectés conservés |
| Décider GO sous conditions | conditions nommées et responsables | actions suivies ; porte suivante limitée par les conditions |
| Autoriser l’offre | prix, documents et engagements rapprochés | version candidate figée |
| Autoriser le dépôt | manifeste, blocages et signataire contrôlés | paquet exact figé ; toute modification révoque l’état prêt |
| Enregistrer le reçu | preuve externe disponible | rapprochement au manifeste, écart visible |
| Partager à un tiers | destinataire et périmètre revus | journal, expiration et révocation disponibles |
| Archiver ou supprimer | conséquences et conservation qualifiées | état traçable, aucune disparition silencieuse |

## 62.3 Invariants de passage

La future architecture doit pouvoir démontrer, par ses interfaces et ses tests, que :

- toute donnée dérivée revient à sa provenance ;
- toute autorisation revient à une personne et une version ;
- tout droit s’applique aussi aux recherches, exports et réponses IA ;
- toute modification critique invalide les validations dépendantes ;
- toute fonction IA critique possède une voie non conversationnelle ;
- tout traitement long expose état, résultat partiel et reprise ;
- toute opération externe distingue préparation, tentative, envoi, réception et acceptation ;
- toute affaire peut être exportée avec un dossier d’audit compréhensible.

---

# 63. Décisions à verrouiller au démarrage de l’architecture

Les DEC-01 à DEC-11 restent la propriété du dirigeant. L’architecture peut démarrer avec les orientations recommandées, mais elle ne doit pas transformer une hypothèse en décision irréversible.

| Décision | Orientation fonctionnelle de travail | Impact si elle change |
|---|---|---|
| DEC-01 Client initial | PME BTP 10–100 personnes, pilote mono-métier et pilote multi-métiers | rôles, onboarding, profondeur et vocabulaire |
| DEC-02 Cycle vendu | DCE → dépôt + GO/NO-GO et passation minimale | navigation, états et frontière avec chantier |
| DEC-03 Public/privé | reconnaissance des deux ; garantie public avant corpus privé validé | règles, parcours, sources et recettes |
| DEC-04 Chiffrage | contrôle et complément d’un chiffrage importé | échanges, droits et profondeur prix |
| DEC-05 Dépôt | préparation, autorisation et preuve ; geste final humain | autorité, canal et responsabilité |
| DEC-06 Veille | BOAMP/TED puis sources ciblées | Radar, couverture et modèle économique |
| DEC-07 Contenus payants | usage seulement avec droit prouvé | accès, références et limitations |
| DEC-08 Juridique | détecter, sourcer, préparer ; expert décide | microcopie, escalade et responsabilité |
| DEC-09 Données/IA | niveaux de sensibilité et options adaptées | isolation, fournisseurs, contrats et coûts |
| DEC-10 Valeur | temps + erreurs + NO-GO + marge protégée + passation | instrumentation et suivi après affaire |
| DEC-11 Modèle de service et isolation | SaaS opéré par SMART AO, environnement dédié par entreprise cliente, application tenant-aware et code unique | infrastructure, coûts, support, sécurité, réversibilité et conformité |

La v1.1 fixe aussi cinq orientations fonctionnelles nécessaires :

1. interface française initiale, avec conservation de la langue originale des sources ;
2. dates absolues avec fuseau/convention source et marge interne séparée ;
3. cible WCAG 2.2 AA, contrôlée selon le référentiel français applicable ;
4. capture terrain tolérant une connectivité dégradée, sans promettre l’édition hors ligne de toute l’Affaire ;
5. aucune réutilisation des données client pour entraîner ou améliorer un modèle sans base contractuelle et information explicite.

### 63.1 Contraintes DEC-11 déjà figées

Le détail technique reste ouvert, mais l’architecture devra respecter les décisions suivantes :

- **single-tenant dédié au déploiement initial** : un environnement métier dédié par entreprise cliente ;
- **tenant-aware dans le logiciel** : organisation, rôles, droits, périmètres et délégations restent présents ;
- **un seul SMART AO** : même code produit et même chaîne de version, sans forks permanents par client ;
- **industrialisation obligatoire** : création, mise à jour, sauvegarde, supervision et suppression d’une instance doivent être reproductibles ;
- **coûts attribuables** : infrastructure et usage IA doivent être mesurables par client ;
- **séparation Control Plane / Data Plane à étudier** : les données métier client ne doivent pas être centralisées par commodité ;
- **résidence cible France/EEE** avec cartographie des services externes et accès de support ;
- **réversibilité prévue dès la conception** : export, délai de sortie, révocation des secrets, suppression et traitement des sauvegardes ;
- **aucune confiance implicite dans le VPS dédié** : chiffrement, habilitations, MFA, journaux, sauvegardes et restauration restent nécessaires.

Ces contraintes sont normées dans `SMART_AO_Registre_Decisions_Architecture_Preliminaires_v0.1.md`, qui devient une entrée du cahier technique.

---

# 64. Critères de passage à l’architecture logicielle

Le CCF est prêt à être transformé en architecture lorsque le dossier d’entrée contient :

- les trois référentiels fonctionnels/métier v1.0/v1.1 comme références ordonnées ;
- `SMART_AO_Registre_Decisions_Architecture_Preliminaires_v0.1.md` comme registre de contraintes de service et d’exploitation ;
- les orientations DEC de travail et la liste des arbitrages encore réversibles ;
- le dictionnaire des objets et des actions critiques ;
- les portes P0–P7 et leurs autorités ;
- les matrices de droits patron/collaborateur/expert/administrateur/tiers ;
- les scénarios REC-01 à REC-28 et UX-01 à UX-28 ;
- les jeux de dossiers retenus pour la vérification ;
- les exigences de preuve, version, confidentialité, accessibilité et reprise ;
- les limites fonctionnelles du premier périmètre ;
- le registre des validations externes toujours ouvertes.

L’architecture devra produire une table de traçabilité reliant chaque composant futur à ces exigences. Elle ne pourra supprimer un blocage, une validation ou une preuve pour simplifier le code sans décision métier explicite.

---

# 65. Conclusion v1.1

SMART AO ne doit pas ressembler à un logiciel traditionnel auquel on aurait ajouté un bouton « IA ».

Il doit ressembler à un **poste de travail métier vivant et défendable** : les écrans structurent le travail, l’intelligence prépare et explique, les preuves permettent de vérifier, les erreurs peuvent être reprises, les secrets restent sous contrôle et les personnes habilitées décident.

L’expérience cible peut se résumer ainsi :

> **SMART AO me montre où j’en suis, ce qui est prouvé, ce qui manque et ce qui a changé. Il prépare le travail sans décider à ma place, protège ce que mon entreprise lui confie et me permet de défendre chaque offre, chaque risque et chaque remise.**

Cette v1.1 clôt la conception fonctionnelle générale et transmet désormais explicitement le modèle de service dédié au futur cahier d’architecture. Les étapes suivantes sont l’architecture logicielle, les prototypes des parcours critiques et les validations REC/UX sur les dossiers réels. Une nouvelle fonction ne doit être ajoutée au CCF que si un test utilisateur, une évolution réglementaire ou un cas métier réel révèle un manque.

---

## Sources

[^1]: data.gouv.fr / DILA, [API Bulletin officiel des annonces des marchés publics — BOAMP](https://www.data.gouv.fr/dataservices/api-bulletin-officiel-des-annonces-des-marches-publics-boamp), accès et caractéristiques consultés le 12 septembre 2026.
[^2]: Office des publications de l’Union européenne, [TED Search API](https://docs.ted.europa.eu/api/latest/search.html), documentation v3 consultée le 12 septembre 2026.
[^3]: Direction interministérielle du numérique, [Concevoir un service public numérique de qualité](https://design.numerique.gouv.fr/bien-concevoir/), consulté le 12 septembre 2026.
[^4]: Direction interministérielle du numérique, [Bonnes pratiques pour les formulaires](https://design.numerique.gouv.fr/outils/checklist-forms/), consulté le 12 septembre 2026.
[^5]: W3C Web Accessibility Initiative, [WCAG 2 Overview et WCAG 2.2](https://www.w3.org/WAI/standards-guidelines/wcag/), version consultée le 12 septembre 2026.
[^6]: Direction interministérielle du numérique, [Référentiel général d’amélioration de l’accessibilité — RGAA 4.1.2](https://accessibilite.numerique.gouv.fr/), consulté le 12 septembre 2026 ; la version 5 est annoncée pour fin 2026.
[^7]: National Institute of Standards and Technology, [Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile, NIST AI 600-1](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf), juillet 2024.
[^8]: Saleema Amershi et al., [Guidelines for Human-AI Interaction](https://www.microsoft.com/en-us/research/wp-content/uploads/2019/01/Guidelines-for-Human-AI-Interaction-camera-ready.pdf), CHI 2019.
[^9]: Commission européenne, [AI Act Service Desk — Article 4, AI literacy](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-4), texte officiel de référence consulté le 12 septembre 2026.
[^10]: Commission européenne, [AI Act Service Desk — Article 50, obligations de transparence](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50), consulté le 12 septembre 2026.
[^11]: CNIL, [Comment déployer une IA générative ?](https://www.cnil.fr/fr/comment-deployer-une-ia-generative-la-cnil-apporte-de-premieres-precisions), 18 juillet 2024.
[^12]: CNIL, [Déterminer la qualification juridique des fournisseurs de systèmes d’IA](https://www.cnil.fr/fr/determiner-la-qualification-juridique-des-fournisseurs-de-systemes-dia), consulté le 12 septembre 2026.
[^13]: CNIL, [Minimiser les données collectées](https://www.cnil.fr/fr/minimiser-les-donnees-collectees), consulté le 12 septembre 2026.
[^14]: CNIL, [Les durées de conservation des données](https://cnil.fr/fr/passer-laction/les-durees-de-conservation-des-donnees), mise à jour du 2 avril 2026.
[^15]: CNIL, [Sécurité : tracer les opérations](https://www.cnil.fr/fr/securite-tracer-les-operations), consulté le 12 septembre 2026.
[^16]: ANSSI, [Recommandations de sécurité pour un système d’IA générative](https://messervices.cyber.gouv.fr/guides/recommandations-de-securite-pour-un-systeme-dia-generative), avril 2024.
[^17]: ANSSI, [Recommandations relatives à l’authentification multifacteur et aux mots de passe](https://messervices.cyber.gouv.fr/guides/recommandations-relatives-lauthentification-multifacteur-et-aux-mots-de-passe), consulté le 12 septembre 2026.
[^18]: GOV.UK Design System, [Confirmation pages](https://design-system.service.gov.uk/patterns/confirmation-pages/), consulté le 12 septembre 2026.
[^19]: Service Public Entreprendre, [Remettre la réponse à un marché public et échanger avec l’acheteur](https://entreprendre.service-public.fr/vosdroits/F32106), version consultée le 12 septembre 2026.
[^20]: Tenderbolt, [Analyse d’appel d’offres et GO/NO-GO](https://www.tenderbolt.ai/fr/features/analysis) et [mémoire technique](https://www.tenderbolt.ai/fr/features/proposal), fonctions revendiquées par l’éditeur, consultées le 12 septembre 2026.
[^21]: Spigao, [Gestion des appels d’offres BTP](https://www.spigao.com/), fonctions revendiquées par l’éditeur, consultées le 12 septembre 2026.
[^22]: CNIL, [Les six grands principes du RGPD](https://www.cnil.fr/fr/comprendre-le-rgpd/les-six-grands-principes-du-rgpd), consulté le 12 septembre 2026.
[^23]: SMART AO, [Cahier des charges métier v1.0](/home/noor/PROJECTS/BTP/SMART_AO_V8/rapports/SMART_AO_Cahier_des_charges_Metier_v1.0.md), 12 septembre 2026.
[^24]: SMART AO, [Univers documentaire métier v1.0](/home/noor/PROJECTS/BTP/SMART_AO_V8/rapports/SMART_AO_Univers_documentaire_metier_v1.0.md), 12 septembre 2026.
[^25]: Légifrance, [Code civil, article 1103 — force obligatoire du contrat](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000032040777/2026-04-27), consulté le 12 septembre 2026.
[^26]: Légifrance, [Loi n° 71-584 du 16 juillet 1971 relative aux retenues de garantie](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000687670), version en vigueur consultée le 12 septembre 2026.
[^27]: Légifrance, [Code civil, article 1799-1 — garantie de paiement de l’entrepreneur](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000027645885/2024-09-01) et [décret n° 99-658 fixant le seuil](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000578018/2024-04-21), consultés le 12 septembre 2026.
[^28]: Légifrance, [Loi n° 75-1334 du 31 décembre 1975 relative à la sous-traitance](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000889241/2021-02-22), consultée le 12 septembre 2026.
