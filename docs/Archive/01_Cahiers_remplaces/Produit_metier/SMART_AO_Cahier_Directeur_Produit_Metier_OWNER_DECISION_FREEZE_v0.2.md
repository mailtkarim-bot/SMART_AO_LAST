# SMART AO — Cahier directeur Produit & Métier
## Owner Decision Freeze — Socle v0.2

**Date : 13 septembre 2026**  
**Statut : DÉCISIONS PROPRIÉTAIRE VERROUILLÉES — prêt pour contre-audit Work avant Product Freeze v1.0**  
**Propriétaire produit : Dirigeant SMART AO**  
**Rôle du document : devenir la référence unique de ce que SMART AO doit être avant traduction en cahier technique puis exécution par Codex.**

---

# 0. Mandat propriétaire et règle de décision

Le propriétaire du produit a validé le socle v0.1 et a délégué à l’architecte produit la responsabilité de trancher les choix résiduels selon le meilleur intérêt de SMART AO.

À compter de cette version :

- les propositions DEC-01 à DEC-10 sont **acceptées et figées** ;
- DEC-11 reste figée ;
- OWN-01 à OWN-13 sont **arbitrées dans la présente version** ;
- un choix produit ne doit plus rester ouvert uniquement par prudence abstraite ;
- lorsqu’un sujet dépend d’une qualification juridique, réglementaire ou factuelle externe, le produit adopte un comportement conservateur et le point est envoyé à Work ou à un spécialiste pour validation, sans inventer une conclusion juridique ;
- les choix techniques de bibliothèques, OCR, retrieval, modèles, infrastructure ou frameworks restent hors de ce document tant que le comportement produit peut être figé sans les choisir.

Cette version constitue donc un **Owner Decision Freeze**. Le Product Freeze v1.0 sera prononcé après :
1. le contre-audit Work ;
2. la consolidation des écarts réellement matériels ;
3. la fixation des contrats fonctionnels des 12 écrans structurants.

---

# 0.1 Pourquoi ce document existe

SMART AO dispose déjà de plusieurs documents solides : cahier métier, univers documentaire, benchmark, CCF UX, décisions d’architecture, audit V8 et architecture directrice.

Le problème n’est plus l’absence de réflexion. Le problème est la **dispersion des décisions**.

Ce document crée un nouveau point de départ :

> **le propriétaire doit pouvoir lire un seul document et dire : “oui, c’est exactement le logiciel que je veux vendre à une PME française du BTP”.**

Il ne choisit pas encore les bibliothèques PDF, l’OCR, la base vectorielle, le fournisseur LLM ou l’infrastructure précise. Ces choix appartiendront au **Cahier technique d’exécution**.

En revanche, tout ce qui change ce que l’utilisateur voit, comprend, peut faire, ne peut pas faire, doit valider, peut déléguer, peut prouver, risque de perdre, peut exporter, peut partager ou doit décider appartient au présent cahier.

---

# 1. Hiérarchie documentaire à partir de maintenant

## 1.1 Sources métier à consolider

Le présent socle absorbe sans les supprimer :

1. `SMART_AO_Cahier_des_charges_Metier_v1.0.md`
2. `SMART_AO_Univers_documentaire_metier_v1.0.md`
3. `SMART_AO_CCF_UX_Product_Blueprint_v1.1.md`
4. `SMART_AO_Benchmark_Concurrentiel_UX_Parcours_v1.0.md`
5. `SMART_AO_Registre_Decisions_Architecture_Preliminaires_v0.1.md`

Documents techniques utiles mais non propriétaires du besoin :
6. `SMART_AO_Architecture_Logicielle_v3.1_REFERENCE_DIRECTRICE_PHASE0.md`
7. rapports `phase0_gate0`
8. Golden DCE / A0 / A1
9. architecture v2.3 comme héritage technique lorsque ses critères n’ont pas encore été absorbés.

## 1.2 Futur statut

Après arbitrage complet :

> `SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md`

deviendra la **source normative propriétaire du produit**.

Le cahier technique devra en dériver.  
Le code devra dériver du cahier technique.  
Un ancien comportement V8 ne pourra pas contredire ce document sous prétexte qu’il existe déjà.

---

# 2. Convention de statut des décisions

| Code | Statut | Signification |
|---|---|---|
| **F** | FIGÉ | décision produit/métier considérée comme stable |
| **P** | PROPOSITION À ARBITRER | recommandation à accepter, modifier ou refuser par le propriétaire |
| **W** | À CONTRÔLER PAR WORK | nécessite une revue externe, réglementaire, marché ou usage |
| **T** | À TRADUIRE TECHNIQUEMENT | comportement figé, implémentation laissée au cahier technique |
| **H** | HORS PÉRIMÈTRE INITIAL | volontairement différé |

Aucun `P` critique ne doit subsister au Product Freeze v1.0.

---

# 3. Vision propriétaire

## 3.1 Question fondamentale

SMART AO doit aider le dirigeant à répondre de manière défendable à la question :

> **Cette affaire mérite-t-elle notre effort commercial, pouvons-nous la gagner, la financer, l’exécuter correctement et conserver la marge prévue ?**

**Statut : F**

## 3.2 Promesse produit

SMART AO doit permettre à une PME BTP de :

1. trouver ou recevoir une opportunité ;
2. comprendre exactement ce que le dossier exige ;
3. identifier ce qui manque, se contredit ou reste incertain ;
4. rapprocher les exigences des capacités réelles de l’entreprise ;
5. détecter ce qui modifie prix, délai, trésorerie, capacité ou risque ;
6. décider GO / GO sous conditions / ATTENTE / NO-GO / ABANDON ;
7. organiser les tâches et validations ;
8. produire ou compléter les pièces de réponse ;
9. protéger les engagements et la confidentialité ;
10. préparer et contrôler le paquet de remise ;
11. conserver la preuve de ce qui a réellement été déposé ;
12. transmettre au chantier ce qui a réellement été vendu.

**Statut : F**

## 3.3 Positionnement

SMART AO n’est pas :
- un chatbot documentaire ;
- un générateur générique de mémoire technique ;
- un ERP chantier ;
- un logiciel qui “donne le prix” ;
- un avocat automatique ;
- un outil qui remplace le patron ;
- une simple GED ;
- un score opaque de GO/NO-GO.

SMART AO est :

> **un poste de commandement métier de l’appel d’offres BTP, centré sur l’Affaire, la preuve, la décision humaine et la protection de la marge.**

**Statut : F**

---

# 4. Client initial et périmètre commercial

## 4.1 Client initial

Décision propriétaire :
- cœur de cible commercial : **PME BTP françaises de 10 à 100 personnes** ;
- le produit ne bloque pas les TPE ni les entreprises plus grandes, mais elles ne pilotent pas les choix V1 ;
- validation terrain recherchée avec au moins **un pilote multi-métiers/entreprise générale** et **un pilote entreprise spécialisée technique**, afin de tester à la fois interfaces inter-lots et profondeur métier.

**Statut : F — DEC-01**

## 4.2 Public / privé

Décision propriétaire :
- les marchés publics et privés sont reconnus dans le modèle produit ;
- la **garantie fonctionnelle V1 est prioritairement qualifiée sur la commande publique** ;
- le privé dispose dès V1 d’un parcours minimal natif, sans prétendre à une couverture exhaustive tant qu’un corpus privé n’a pas été qualifié.

**Statut : F — DEC-03**

## 4.3 Cycle vendu

Décision propriétaire :
- opportunité / invitation ;
- analyse ;
- GO/NO-GO ;
- préparation de l’offre ;
- autorisation ;
- remise et preuve ;
- résultat ;
- passation minimale si gagné.

SMART AO s’arrête avant la gestion opérationnelle complète du chantier et ne devient pas un ERP chantier.

**Statut : F — DEC-02**

---

# 5. Les deux piliers du produit

## 5.1 L’Affaire

L’Affaire est le centre opérationnel.

Elle répond à :

> **Que devons-nous comprendre, décider, produire et remettre pour cette consultation précise ?**

Elle contient ou relie : acheteur, objet, lot/périmètre, responsables, versions DCE, échéances, exigences, preuves, inconnus, hypothèses, contradictions, MIRP, risques, prix et facteurs de coût, partenaires, tâches, questions, engagements, documents de réponse, décisions, manifeste, reçu, résultat et passation.

**Statut : F**

## 5.2 La Mémoire Entreprise

La Mémoire Entreprise est le patrimoine privé gouverné de la société.

Elle répond à :

> **Que savons-nous réellement sur notre entreprise, avec quelles preuves, quelle validité, quels droits et quelle possibilité de réemploi ?**

Elle couvre notamment : identité société, établissements, pouvoirs et signataires, assurances, qualifications, certifications, références, CV/compétences, personnel, moyens matériels, méthodes, QSE, partenaires, fournisseurs, sous-traitants, produits/références, modèles, prix internes, données de marge et trésorerie selon droits, historiques et REX.

Une information n’est pas vraie parce qu’un LLM l’a formulée.

**Statut : F**

---

# 6. Cycle métier complet d’une affaire

```text
RADAR / INVITATION
      ↓
OPPORTUNITÉ
      ↓ P0 — CIBLER
QUALIFICATION
      ↓
DCE / INVITATION REÇUE
      ↓ P1 — OUVRIR
AFFAIRE
      ↓
COUVERTURE DU DOSSIER
      ↓
EXIGENCES / PREUVES / INCONNUS / CONTRADICTIONS
      ↓
MIRP / RISQUES / INTERFACES
      ↓ P2
PLAN DE RÉPONSE
      ↓
VISITE / QUESTIONS / DOCUMENTS / PARTENAIRES
      ↓
CHIFFRAGE CONTRÔLÉ / CAPACITÉ / TRÉSORERIE
      ↓ P3
RÉPONSE / MÉMOIRE / ENGAGEMENTS
      ↓ P4
COFFRE / MANIFESTE / VERSION CANDIDATE
      ↓ P5
DÉPÔT HUMAIN + PREUVE
      ↓
CLARIFICATIONS / NÉGOCIATION / RÉSULTAT
      ↓ P6 SI MODIFICATION
GAGNÉ → PASSATION → P7
PERDU → REX
```

**Statut : F sur la structure générale.**

Le sens précis de chaque porte P0–P7 doit être regroupé dans la version v1.0 du présent document.

---

# 7. Modèle d’autorité et séparation Patron / Collaborateur

## 7.1 Patron / dirigeant

Le Patron :
- définit les orientations commerciales ;
- décide GO / GO sous conditions / ATTENTE / NO-GO / ABANDON ;
- contrôle prix, marge, prix plancher, trésorerie et exposition ;
- arbitre les risques ;
- accepte les hypothèses critiques ;
- valide les engagements sensibles ;
- autorise l’offre ;
- autorise la remise ;
- décide les dérogations ;
- gère ou délègue la confidentialité ;
- approuve les engagements financiers, solidarités et expositions sensibles.

Son interface est orientée **décision, exception et arbitrage**.

**Statut : F**

## 7.2 Responsable d’offre / collaborateur

Le collaborateur :
- prend en charge l’affaire ;
- contrôle les pièces ;
- vérifie les règles de consultation ;
- traite les exigences ;
- prépare questions, tâches et consultations ;
- assemble les preuves ;
- coordonne experts et partenaires ;
- prépare les documents ;
- remonte les inconnus ;
- soumet au Patron un dossier prêt à arbitrer.

Par défaut, il ne voit pas : marge, prix d’achat sensibles, prix plancher, scénarios de trésorerie Direction, notes privées Direction, évaluations confidentielles partenaires.

**Statut : F**

## 7.3 Experts internes

Métreur, conducteur, QSE, administratif, DAF, achats ou autre expert :
- accèdent uniquement au périmètre nécessaire ;
- peuvent apporter un avis ;
- peuvent valider un point si habilités ;
- ne gagnent pas automatiquement l’autorité Patron.

**Statut : F**

## 7.4 Administrateur

L’administrateur :
- gère techniquement utilisateurs, rôles et paramètres ;
- ne possède pas automatiquement l’autorisation de lire les marges, RIB, prix confidentiels ou affaires restreintes.

**Statut : F**

## 7.5 Tiers externes

Fournisseur, sous-traitant, cotraitant, conseil :
- ne voit jamais l’Affaire complète par défaut ;
- reçoit un paquet ciblé ;
- accès limité en objet, durée et action ;
- révocation possible pour l’accès futur ;
- le produit explique qu’un fichier déjà téléchargé ne peut pas être “rappelé”.

**Statut : F**

---

# 8. Comptes, organisation et identité utilisateur

Ce bloc n’est pas assez fermé dans les documents précédents. Il devient une priorité propriétaire.

## 8.1 Création initiale de l’entreprise

### Proposition
Lors du provisioning d’un environnement client :
1. SMART AO crée l’organisation ;
2. un premier **Propriétaire** nominatif est créé/invité ;
3. ce Propriétaire active son accès ;
4. il peut inviter d’autres utilisateurs ;
5. il ne peut pas être supprimé tant qu’un autre Propriétaire n’a pas été désigné.

**Statut : P**

## 8.2 Rôles de compte à distinguer des rôles métier

Proposition :
- Propriétaire organisation ;
- Administrateur ;
- Patron / Dirigeant ;
- Responsable d’offre ;
- Expert ;
- Tiers.

Une personne peut cumuler certains rôles selon la taille de l’entreprise.

**Statut : P**

## 8.3 Invitation utilisateur

À arbitrer : invitation par email, durée de validité, acceptation, affectation initiale du rôle, activation MFA, possibilité de domaine email imposé ou non.

**Statut : P / T**

## 8.4 Départ d’un salarié

Le produit doit :
- désactiver immédiatement son accès ;
- ne pas supprimer son historique ;
- réaffecter ses tâches/affaires ;
- conserver les décisions qu’il a réellement prises ;
- invalider ou transférer les délégations futures ;
- révoquer sessions et accès partagés si nécessaire.

**Statut : F sur le résultat, T sur l’implémentation**

---

# 9. Authentification et sécurité utilisateur

## 9.1 Principes produit

- chaque utilisateur dispose de son identité propre ;
- aucun compte partagé recommandé ;
- authentification renforcée pour actions sensibles ;
- sessions expirées sans perte silencieuse de travail ;
- droits appliqués aux écrans, recherches, exports et contextes IA ;
- réauthentification possible pour une action engageante.

**Statut : F**

## 9.2 Décisions à arbitrer

- MFA obligatoire pour Propriétaire/Patron/Administrateur ?
- MFA obligatoire pour tous ?
- passkeys acceptées ?
- SSO entreprise différé ou V1 ?
- durée session ;
- réauthentification avant P5 ;
- récupération de compte ;
- politique d’inactivité ;
- blocage et déblocage ;
- appareils connus ;
- journaux visibles au client.

**Statut : P / W / T**

La sécurité technique concrète sera choisie dans le cahier technique.

---

# 10. Navigation générale

Les espaces de premier niveau sont :

1. **Accueil**
2. **Opportunités**
3. **Affaires**
4. **Entreprise**
5. **Administration / Paramètres**

Risques, exigences, documents, tâches, prix, partenaires, décisions et dépôt ne deviennent pas douze applications séparées.

**Statut : F**

---

# 11. Les 12 écrans structurants à figer

Avant Product Freeze complet, le comportement des écrans suivants doit être validé :

1. Accueil Patron
2. Radar
3. Fiche Opportunité
4. Import DCE
5. Explorateur DCE
6. Synthèse Affaire
7. Registre MIRP
8. Décision GO/NO-GO
9. Prix
10. Réponse
11. Coffre de remise
12. Passation

Pour chacun devront être figés : rôle principal, question métier, informations essentielles, action principale, actions secondaires, état vide, état en traitement, état incomplet, erreur, reprise, confidentialité, preuve/source, mobile éventuel, clavier/accessibilité et comportement IA.

**Statut : F pour la liste ; P pour la spécification finale de chaque écran**

---

# 12. Accueil Patron

L’accueil répond avant tout à :

> **Qu’est-ce qui mérite mon attention aujourd’hui ?**

Il privilégie : échéances menaçantes, décisions ouvertes, blocages critiques, rectificatifs à revalider, visite, questions acheteur, preuve expirante, partenaire non sécurisé, risque de prix ou engagement non couvert.

Trois dimensions synthétiques :
- Temps ;
- Préparation prouvée ;
- Risque.

Le briefing SMART AO n’est pas une génération libre : chaque alerte doit revenir à un état, un événement ou une preuve.

**Statut : F**

---

# 13. Opportunités / Radar

## 13.1 Fonction

Le Radar sert à : rechercher, filtrer, sauvegarder des recherches, suivre, écarter avec motif, expliquer pourquoi une opportunité apparaît et convertir en Affaire.

BOAMP est la première source native prioritaire ; TED la seconde.

**Statut : P — DEC-06 à signer comme décision propriétaire**

## 13.2 Interdictions

- ne pas masquer silencieusement des résultats ;
- ne pas présenter un score opaque de “chance de gagner” ;
- afficher la fraîcheur de la source ;
- si la source est indisponible, ne pas prétendre être à jour.

**Statut : F**

---

# 14. Réception du DCE

## 14.1 Import

L’utilisateur peut fournir : fichier, plusieurs fichiers, dossier, archive, document issu d’un canal autorisé.

Le dossier source reçu est conservé.

**Statut : F**

## 14.2 Première sortie

La première sortie n’est jamais “analyse terminée”.

SMART AO affiche : fichiers reçus, archives, fichiers reconnus, fichiers non lus, fichiers partiellement lus, doublons/versions, rectificatifs, pièces annoncées mais absentes, éléments nécessitant revue.

**Statut : F**

## 14.3 États

- analysable ;
- analysable sous réserves ;
- incomplet pour l’étude ;
- incomplet pour le prix ;
- non analysable sur certains éléments.

“Complet” n’est utilisé que si le périmètre de complétude est prouvé.

**Statut : F**

---

# 15. Univers documentaire

SMART AO ne confond jamais :

1. documents fournis ou référencés par l’acheteur ;
2. documents à remettre par le candidat ;
3. preuves/documents tiers que SMART AO ne peut pas fabriquer ;
4. informations/documents nécessaires à l’étude et au prix.

**Statut : F**

Chaque objet documentaire doit pouvoir porter notamment : source, phase, lot, titulaire, responsable, mode de traitement, modèle imposé, signature, format, nom/emplacement attendu, validité, sensibilité, criticité, conséquence d’absence, prochaine action et preuve de sortie.

**Statut : F**

---

# 16. Fidélité aux documents acheteur

Quand un modèle acheteur est imposé :
- original conservé ;
- travail sur copie/version dérivée ;
- structure et consignes préservées ;
- formules et zones protégées respectées ;
- aucune suppression silencieuse ;
- aucune conversion silencieuse de format ;
- modifications traçables ;
- comparaison possible entre original et produit.

**Statut : F**

Le cahier technique devra démontrer cette fidélité sur DOCX/XLSX et autres formats pris en charge.

---

# 17. Exigences, preuves et source

Une exigence critique doit permettre de répondre à :

- qu’est-ce qui est demandé ?
- par quelle source ?
- quelle version ?
- où exactement ?
- pour quel lot/site/phase ?
- obligatoire ou non ?
- criticité ?
- quel acteur ?
- quelle échéance ?
- quelle conséquence ?
- est-elle prouvée, contradictoire, incertaine ou non supportée ?
- qui l’a validée ?

**Statut : F**

Invariant :

> **aucune conclusion critique sans état de preuve.**

**Statut : F**

---

# 18. Inconnus, contradictions, hypothèses et MIRP

## 18.1 Inconnu

Un inconnu comporte : ce qui manque, pourquoi cela compte, impact possible, responsable, action, échéance et état.

## 18.2 Contradiction

Une contradiction conserve : sources en conflit, versions, périmètre, impact et question/décision nécessaire.

## 18.3 Hypothèse

Une hypothèse n’est jamais présentée comme fait et possède auteur, motif, portée, durée/condition, validateur et impacts.

## 18.4 MIRP

Le MIRP représente l’information nécessaire pour chiffrer ou décider de manière fiable.

Une pièce absente peut entraîner : question, visite, hypothèse bornée, provision, réserve si autorisée, blocage du prix ou NO-GO à décider.

**Statut : F**

---

# 19. Risques métier et facteurs de coût

SMART AO recherche transversalement notamment : installation/logistique, site occupé, études, sécurité, environnement, qualité/réception, géotechnique, amiante/plomb, réseaux, supports existants, interventions de nuit, continuité de service, accès, levage, essais, DOE/DIUO, délais, pénalités, garanties, retenues, paiement, hors-site et obligations spécifiques.

Une prestation présente dans un CCTP mais absente du DPGF ne devient pas automatiquement “hors prix”.

**Statut : F**

---

# 20. Fournisseurs, sous-traitants, cotraitants

Les offres partenaires doivent être comparées à périmètre constant en tenant compte notamment de : postes/quantités, exclusions, variantes, performances/marques, délais, validité prix, transport/levage/stockage, paiement, garanties, disponibilité et conformité administrative/assurantielle.

Le moins-disant apparent n’est pas forcément le coût complet le plus faible.

**Statut : F**

Les solidarités, engagements de groupement et expositions inhabituelles nécessitent décision Patron.

**Statut : F**

---

# 21. Chiffrage, marge, capacité, trésorerie

## 21.1 Doctrine

SMART AO :
- rapproche le besoin et la couverture du chiffrage ;
- signale prestations/facteurs non couverts ;
- permet l’import/export ;
- conserve hypothèses ;
- permet scénarios ;
- protège les informations Direction.

SMART AO ne fixe pas seul le prix final.

**Statut : F**

## 21.2 Orientation actuelle

Le premier produit doit **contrôler et compléter un chiffrage importé**, plutôt que devenir immédiatement un logiciel de chiffrage complet.

**Statut : P — DEC-04**

## 21.3 À arbitrer

- profondeur du chiffrage V1 ;
- fichiers/logiciels de chiffrage visés ;
- calcul de marge ;
- trésorerie minimale ;
- capacité chantier ;
- charge études ;
- prix plancher ;
- scénarios Direction.

---

# 22. GO / NO-GO et portes P0–P7

SMART AO n’attribue pas un score final qui décide à la place du Patron.

Décisions possibles : GO, GO SOUS CONDITIONS, ATTENTE, NO-GO, ABANDON.

Chaque décision engageante conserve : auteur habilité, date/heure, version/contexte, faits et preuves, inconnus, conditions, motif, éventuelle date de revue et supersession.

**Statut : F**

---

# 23. Production de la réponse

SMART AO prépare : candidature, mémoire technique, cadres acheteur, questionnaires, références, CV, organigrammes, tableaux, réponses administratives, documents libres et documents à obtenir auprès d’un tiers.

Chaque document distingue : ce qui vient de l’acheteur, ce qui vient de l’entreprise, ce que l’IA propose, ce que l’humain a validé et ce qui manque.

**Statut : F**

---

# 24. Engagements

Une phrase d’offre qui crée une obligation doit pouvoir devenir un Engagement avec : formulation, source de création, coût/impact, responsable futur, phase, validation et lien vers passation.

L’IA ne doit pas créer silencieusement un engagement contractuel.

**Statut : F**

---

# 25. Coffre, manifeste et remise

Le Coffre est la zone de contrôle final.

Il gère : liste des livrables, versions, formats, signatures, nommage, organisation du pli, blocages, version candidate, autorisation et manifeste.

Aucune hypothèse “tout en ZIP”.

**Statut : F**

Le geste final de dépôt reste humain dans le périmètre initial.

**Statut : P — DEC-05 à confirmer**

SMART AO distingue : préparé, tentative, envoyé, réception prouvée et accepté lorsque le tiers le prouve.

Aucune remise n’est déclarée réussie sans preuve externe cohérente.

**Statut : F**

---

# 26. Rectificatifs et versions

Une nouvelle version :
- ne remplace pas silencieusement l’ancienne ;
- déclenche comparaison/impact ;
- rouvre les validations dépendantes ;
- signale ce qui doit être revu ;
- peut invalider prix, engagement, décision ou document candidat.

Une décision historique validée reste historique ; elle ne change pas silencieusement après évolution du modèle ou des règles.

**Statut : F**

---

# 27. Marchés privés

SMART AO doit reconnaître un parcours privé avec notamment : invitation, dossier/demande client, devis/offre, contrat proposé, négociation/mise au point, version acceptée, contradictions commande/devis/contrat, preuve d’envoi et réception.

La profondeur garantie V1 doit être arbitrée à partir d’un corpus privé réel.

**Statut : P / W**

---

# 28. IA visible : une seule identité SMART AO

L’utilisateur ne navigue pas entre plusieurs “agents”.

Une seule identité visible : **SMART AO**.

Elle peut : constater, extraire, rapprocher, expliquer, recommander, préparer, poser une question et préparer une action.

Elle ne peut pas seule : décider GO/NO-GO, accepter une hypothèse critique, fixer prix final/marge, signer, déposer, partager une donnée restreinte, accepter une clause juridique sensible, modifier une preuve tierce ou déclarer un partenaire engagé.

**Statut : F**

---

# 29. IA-native, pas chat-first

Le chat n’est pas le produit.

L’IA apparaît dans : briefing, prochaine action, explication, détection d’écart, préparation de question, préparation de document, contrôle et assistance contextuelle.

Toute fonction critique possède aussi une voie non conversationnelle.

**Statut : F**

---

# 30. Comportement de confiance

Les sorties visibles distinguent au besoin : Extraction, Rapprochement, Inférence, Recommandation, Brouillon, Action préparée.

SMART AO privilégie : preuve directe trouvée, preuves concordantes, source unique à confirmer, inférence à valider, contradiction, aucune preuve exploitable, document non lu/hors périmètre.

Pas de pseudo-pourcentage de confiance sans signification testée.

**Statut : F**

---

# 31. Documents hostiles et prompt injection

Un DCE ou une pièce externe est **une source à analyser, jamais une instruction d’administration**.

Une instruction trouvée dans un document ne peut pas modifier les règles système, élargir les droits, lancer un outil interdit, obtenir des secrets ou accéder à une autre affaire/Mémoire Entreprise.

**Statut : F**

---

# 32. Collaboration

Le produit doit gérer : responsable principal, contributeurs, valideurs, tâches, commentaires, mentions, délégations, absence/congé, conflit de modification et reprise.

Aucune contribution validée ne doit disparaître silencieusement.

**Statut : F**

---

# 33. Notifications et échéances

Chaque échéance critique conserve : nature, date/heure absolue, fuseau/convention source, source/version, canal/lieu, marge de sécurité interne, statut, responsable et dépendances.

Le compte à rebours seul est interdit.

Notifications initiales : centre SMART AO + email critique configurable.

**Statut : F**

---

# 34. Mobile et terrain

Le mobile est un compagnon terrain, pas le poste d’étude principal.

Usage : visite, note, photo, constat, tâche, consultation ciblée.

En connectivité dégradée, distinguer : conservé localement, en attente, synchronisé.

Aucune preuve non synchronisée n’est présentée comme partagée.

**Statut : F**

---

# 35. Onboarding

Premiers chemins possibles :
1. importer un DCE réel ;
2. explorer une démonstration anonymisée ;
3. préparer les preuves essentielles de l’entreprise.

La première valeur ne doit pas exiger le paramétrage intégral de la société.

**Statut : F**

À arbitrer : qui effectue le provisioning, qui configure l’entreprise, onboarding accompagné ou self-service, données minimales obligatoires au premier démarrage.

**Statut : P**

---

# 36. Administration

Administration / Paramètres contient notamment : utilisateurs, rôles, délégations, règles, préférences, sources, notifications, sécurité, gouvernance de données et paramètres organisation.

Ce n’est pas l’espace quotidien du collaborateur.

**Statut : F**

---

# 37. Support

Principe produit :
- pas d’accès humain ordinaire au contenu client ;
- diagnostic technique sans contenu privilégié ;
- accès exceptionnel nominatif si indispensable ;
- durée/périmètre bornés ;
- authentification forte ;
- journalisation ;
- information/encadrement.

**Statut : F sur le résultat, W/T sur qualification juridique et mécanisme**

---

# 38. Données, export et fin de contrat

L’entreprise doit pouvoir obtenir un export exploitable comprenant selon droits : fichiers originaux, métadonnées, décisions, preuves, manifestes, historiques utiles et données structurées réutilisables.

Fin de contrat : qualifier conservation → préparer export → remettre/confirmer → geler nouveaux traitements → délai de réversibilité → supprimer données actives → traiter sauvegardes → révoquer secrets/accès → détruire environnement → conserver preuve légitime de clôture.

**Statut : F**

---

# 39. Modèle de service

Décision déjà prise :

> **SaaS opéré par SMART AO, environnement métier dédié par entreprise cliente, application tenant-aware, code produit unique.**

Conséquences produit : confidentialité non fondée uniquement sur le VPS, rôles/droits toujours présents, un seul produit/version, coûts infra et IA attribuables, réversibilité prévue, exploitation reproductible.

**Statut : F — DEC-11**

---

# 40. Accessibilité

Cible produit : WCAG 2.2 AA, contrôlée avec le référentiel français applicable.

Fonctions critiques accessibles clavier. La couleur n’est jamais le seul signal. Erreurs explicites. Tableaux et graphiques disposent d’une lecture adaptée.

**Statut : F**

---

# 41. Mesure de qualité produit

SMART AO est évalué sur : compréhension, décision, exigences critiques, exactitude des sources, couverture prix, documents, rectificatifs, confidentialité, collaboration, remise, comportement IA, accessibilité et adoption.

Une moyenne ne masque jamais un échec critique.

**Statut : F**

---

# 42. Golden DCE

Le Golden DCE sert à vérifier le produit, pas à définir le métier à la place du propriétaire.

Jeux distincts : Development, Qualification gelée, Hostile/adversarial.

Les vérités critiques peuvent nécessiter deux revues indépendantes ; les désaccords sont conservés.

**Statut : F**

---

# 43. Ce qui appartient au futur cahier technique, pas au présent document

Ne pas arbitrer ici par préférence technique : bibliothèque PDF, moteur OCR, DOC/DOCX parser, XLS/XLSX parser, XLS historique, ZIP/7z, antivirus/quarantaine, moteur lexical, vector DB, embeddings, reranker, parser tableaux, vision/plans, stockage objet, jobs, fournisseur/modèle LLM, monitoring, sauvegardes, secrets manager, containers/IaC, reverse proxy, framework technique exact.

Le présent cahier fixe cependant **les résultats que ces choix doivent rendre possibles**.

**Statut : T**

---

# 44. Repartir de zéro ou migrer V8

Décision de doctrine proposée :

> **Greenfield fonctionnel, migration technique sélective.**

SMART AO est défini par ce nouveau cahier, pas par V8.

Chaque composant V8 reçoit ensuite : KEEP, ADAPT, REPLACE ou DELETE.

Un test V8 n’a pas autorité sur le métier : conserver s’il protège un invariant valide, adapter si le métier change, supprimer si la fonction disparaît.

Ne pas repartir d’un repo vide sauf preuve que la structure existante empêche la cible.

**Statut : F — doctrine propriétaire confirmée : greenfield fonctionnel, migration technique sélective**

---

# 45. Registre propriétaire — décisions verrouillées

## DEC-01 — Client initial — FIGÉ
**Décision :** cœur de cible PME BTP françaises 10–100 personnes. Les TPE et entreprises plus grandes peuvent être servies si compatibles, mais ne pilotent pas la V1. Validation avec un pilote multi-métiers/entreprise générale et un pilote spécialisé technique.

## DEC-02 — Cycle vendu — FIGÉ
**Décision :** opportunité/invitation → DCE → analyse → décision → réponse → remise/preuve → résultat → passation minimale. Pas d’ERP chantier.

## DEC-03 — Public / privé — FIGÉ
**Décision :** les deux sont natifs dans le modèle. La commande publique est qualifiée en premier ; le privé V1 est volontairement borné tant que son corpus n’est pas suffisamment testé.

## DEC-04 — Chiffrage — FIGÉ
**Décision :** V1 contrôle, rapproche et complète un chiffrage importé. SMART AO détecte les prestations/facteurs non couverts, gère hypothèses/scénarios et expose marge/trésorerie selon droits. Il ne devient pas un logiciel de chiffrage complet et ne fixe pas le prix final.

## DEC-05 — Dépôt — FIGÉ
**Décision :** SMART AO prépare, contrôle, fige le manifeste et autorise. **Le geste final de dépôt reste humain pendant toute la V1.** Toute future automatisation sera une décision séparée.

## DEC-06 — Veille — FIGÉ
**Décision :** BOAMP est la source native de lancement. TED est la deuxième source publique, prévue en V1.x après stabilisation du Radar BOAMP. Les autres sources sont ajoutées selon valeur et droits.

## DEC-07 — Contenus payants — FIGÉ
**Décision :** aucune ingestion ou réutilisation de contenu payant/licencié sans droit démontré. Les droits d’usage font partie des métadonnées du contenu.

## DEC-08 — Juridique — FIGÉ
**Décision :** SMART AO détecte, source, explique, prépare une question ou une escalade. Il ne rend pas seul un avis juridique engageant ; l’expert ou le décideur humain tranche.

## DEC-09 — Données / IA — FIGÉ
**Décision :** sensibilité, minimisation, finalité et droits gouvernent les données. Aucune donnée client n’est réutilisée pour entraîner/améliorer un modèle sans base contractuelle et information/choix explicites. Les secrets Direction ne transitent pas vers un rôle non autorisé, y compris via l’IA.

## DEC-10 — Valeur — FIGÉ
**Décision :** la valeur se mesure notamment par temps gagné, erreurs/oubli évités, NO-GO utiles, marge protégée, meilleure préparation, qualité de remise et qualité de passation.

## DEC-11 — Service — FIGÉ
**Décision :** SaaS opéré par SMART AO, environnement dédié par entreprise cliente, application tenant-aware, code produit unique.

---

# 46. Arbitrages propriétaire OWN-01 à OWN-13 — décisions finales

## OWN-01 — Premier compte — FIGÉ
Le premier compte est un **Propriétaire d’organisation nominatif**, créé/invité lors du provisioning de l’environnement. Il active lui-même son accès. Une organisation doit toujours conserver au moins un Propriétaire actif.

## OWN-02 — Multi-Patron — FIGÉ
Plusieurs utilisateurs peuvent avoir le rôle Patron/Dirigeant.  
En revanche :
- la propriété administrative de l’organisation est distincte du rôle métier Patron ;
- au moins un Propriétaire d’organisation existe ;
- les délégations P0–P7 sont explicites ;
- le transfert de propriété est une action sensible tracée.

## OWN-03 — MFA — FIGÉ
MFA obligatoire pour **tous les utilisateurs internes** de SMART AO.  
Les actions à très fort impact peuvent exiger une authentification renforcée supplémentaire.  
Les tiers externes utilisent un mécanisme d’accès borné adapté à leur paquet partagé.

## OWN-04 — Réauthentification — FIGÉ
Réauthentification/step-up obligatoire avant :
- autorisation P5/remise ;
- transfert de propriété ;
- modification de droits sensibles ;
- export complet ;
- suppression/destruction d’organisation ;
- partage exceptionnel de données fortement restreintes.

## OWN-05 — SSO — FIGÉ
Le SSO n’est **pas un prérequis de lancement V1**. Il est prévu en V1.x pour les clients qui le justifient. La V1 doit cependant éviter toute architecture d’identité qui rendrait son ajout coûteux ou destructif.

## OWN-06 — Onboarding — FIGÉ
Deux niveaux :
1. **onboarding accompagné** par SMART AO pour les premiers clients et pilotes ;
2. parcours produit guidé permettant progressivement un onboarding autonome.

Pas d’inscription libre grand public non contrôlée au lancement.

## OWN-07 — Profondeur Prix V1 — FIGÉ
V1 :
- importe un chiffrage depuis des formats convenus ;
- rapproche prix et exigences ;
- signale postes/facteurs non couverts ;
- gère hypothèses/scénarios ;
- calcule/présente les indicateurs autorisés de marge/exposition ;
- aide à préparer la décision Patron.

V1 ne fait pas :
- métré automatique généralisé ;
- bibliothèque tarifaire universelle ;
- chiffrage complet natif remplaçant le logiciel métier ;
- fixation autonome du prix final.

## OWN-08 — Marché privé V1 — FIGÉ
V1 prend en charge :
- invitation privée ;
- création manuelle d’une Affaire ;
- import du dossier ;
- analyse documentaire ;
- GO/NO-GO ;
- réponse ;
- preuve d’envoi/réception lorsqu’elle existe ;
- contradiction devis/commande/contrat visible.

La négociation contractuelle avancée et les cas privés très spécialisés sont V1.x après constitution d’un corpus privé.

## OWN-09 — Tiers externes V1 — FIGÉ
V1 inclut un **partage externe minimal et ciblé** :
- paquet limité ;
- lien ou accès expirant ;
- droits téléchargement/dépôt bornés ;
- journalisation ;
- révocation future ;
- aucune vue globale de l’Affaire.

Un portail partenaire riche, conversationnel ou multi-projets est V1.x.

## OWN-10 — Mobile V1 — FIGÉ
V1 mobile = **compagnon terrain responsive**, pas poste d’étude :
- consultation ciblée ;
- visite ;
- notes ;
- photos ;
- constats ;
- tâches/checklists ;
- état local/en attente/synchronisé.

Pas d’édition complète de l’Affaire sur mobile comme exigence V1.

## OWN-11 — Dépôt — FIGÉ
Le geste final de dépôt reste humain pour toute la V1. SMART AO peut préparer, contrôler, guider et rapprocher le reçu, mais ne se substitue pas au signataire/opérateur.

## OWN-12 — Frontend — FIGÉ
Les **12 écrans structurants** doivent disposer d’un contrat fonctionnel et d’un prototype testable avant le gel technique complet.  
Le gel exigé porte d’abord sur :
- question métier ;
- contenu ;
- action principale ;
- états ;
- droits ;
- erreurs/reprise ;
- preuve/source ;
- comportement IA.

Le pixel-perfect n’est pas une condition préalable au backend, mais le parcours ne doit pas être improvisé par Codex.

## OWN-13 — Greenfield fonctionnel / V8 — FIGÉ
Doctrine officielle :

> **SMART AO est un nouveau produit défini par le cahier propriétaire. V8 est un réservoir de composants, tests et comportements à réemployer sélectivement.**

Chaque composant V8 est évalué `KEEP / ADAPT / REPLACE / DELETE`.  
Aucun comportement historique ne prime sur le présent cahier.

---

# 47. Périmètre V1 / V1.x / plus tard — décision propriétaire

## V1 — indispensable

### Identité, sécurité et organisation
- organisation ;
- Propriétaire ;
- utilisateurs ;
- rôles/délégations ;
- MFA ;
- réauthentification sensible ;
- confidentialité Patron/Collaborateur ;
- audit.

### Opportunités
- Radar BOAMP ;
- recherches/filtres ;
- suivi ;
- provenance/fraîcheur ;
- conversion en Affaire ;
- création manuelle d’Affaire publique ou privée.

### Affaire / DCE
- import fichiers/dossiers/archives ;
- originaux conservés ;
- versioning/rectificatifs ;
- couverture de lecture ;
- exigences ;
- source/preuve ;
- inconnus ;
- contradictions ;
- MIRP ;
- risques ;
- facteurs de coût.

### Mémoire Entreprise minimale
- identité ;
- preuves administratives ;
- assurances/qualifications ;
- références ;
- personnes/moyens ;
- partenaires ;
- documents réutilisables ;
- validité/sensibilité/droits.

### Décision et prix
- P0–P5 nécessaires à la remise ;
- GO / GO sous conditions / ATTENTE / NO-GO / ABANDON ;
- contrôle d’un chiffrage importé ;
- couverture coûts ;
- scénarios autorisés ;
- information de marge/trésorerie selon droits ;
- décision finale humaine.

### Réponse
- candidature ;
- mémoire ;
- modèles acheteur ;
- documents à produire/obtenir ;
- engagements ;
- validation ;
- fidélité des formats pris en charge.

### Remise
- Coffre ;
- version candidate ;
- manifeste ;
- contrôles ;
- signataire ;
- autorisation ;
- geste final humain ;
- reçu/preuve ;
- rapprochement.

### Collaboration / tiers
- tâches ;
- responsables ;
- validations ;
- commentaires ;
- remplacement/délégation ;
- partage externe minimal ciblé et expirant.

### IA
- briefing/contextual guidance ;
- extraction/explication/recommandation/brouillon ;
- sources ;
- abstention ;
- permissions ;
- coût/usage mesuré ;
- fonctionnement critique sans IA.

### Mobile / terrain
- compagnon responsive ;
- visite/notes/photos/constats/tâches ;
- synchronisation explicite.

### Fin de cycle
- résultat ;
- REX minimal ;
- passation minimale ;
- export ;
- suppression/réversibilité.

## V1.x — après stabilisation de V1

- TED ;
- SSO ;
- portail tiers enrichi ;
- consultations fournisseurs/sous-traitants avancées ;
- marché privé contractuel avancé ;
- capacité/charge/trésorerie approfondies ;
- connecteurs ERP/chiffrage bidirectionnels ;
- mobile enrichi ;
- P6/P7 approfondies ;
- automatisations de plateformes lorsque responsabilité et preuve sont maîtrisées.

## Plus tard / uniquement si preuve de valeur

- ERP chantier complet : hors stratégie par défaut ;
- dépôt autonome généralisé : décision séparée ;
- GraphRAG : uniquement après benchmark ;
- orchestrateur agentique général : seulement si tools/contrats sont stables ;
- vision/plans avancée : selon corpus et ROI ;
- multi-tenant mutualisé : seulement si décision économique future.

**Statut : F**

---

# 48. Mandat futur de Work

Work ne doit pas “concevoir SmartAO à notre place”.

## Mission 1 — Contre-audit métier

Pour chaque bloc : couvert, insuffisamment couvert, absent, contradictoire, inutile/complexifiant.

Points de vue : dirigeant PME BTP, responsable d’offre, métreur, conducteur, administratif, DAF/achats, QSE, sous-traitant/fournisseur, exploitation/support.

## Mission 2 — Recherche ciblée

Vérifier uniquement les sujets qui nécessitent une preuve externe : pratiques PME françaises, parcours AO public/privé, sécurité compte/authentification SaaS, RGPD/support/export, accessibilité, comportement des solutions concurrentes, pratiques de remise, obligations réglementaires matérialisant une exigence produit.

## Interdiction

Dans cette mission, Work ne choisit pas l’architecture logicielle, les librairies, la stack OCR/RAG, le provider LLM ou la base vectorielle.

---

# 49. Critères du Product Freeze v1.0

Le produit est gelé lorsque :

1. DEC-01 à DEC-11 sont figées ;
2. OWN-01 à OWN-13 sont figées ;
3. les 12 écrans ont un contrat fonctionnel ;
4. Patron/Collaborateur/Expert/Admin/Tiers sont fermés ;
5. cycle complet public est validé ;
6. profondeur du privé V1 est décidée ;
7. profondeur du prix V1 est décidée ;
8. compte/onboarding/authentification sont décidés ;
9. dépôt et responsabilité sont décidés ;
10. périmètre V1/V1.x est décidé ;
11. Work a rendu sa revue contradictoire ;
12. les écarts Work ont été arbitrés ;
13. aucune question critique “produit” n’est renvoyée au cahier technique.

Lorsque le contre-audit Work et les 12 contrats d’écran auront été consolidés sans écart critique non arbitré :

> **PRODUCT FREEZE v1.0**

---

# 50. Traduction après Product Freeze

```text
CAHIER DIRECTEUR PRODUIT & MÉTIER v1.0
              ↓
      CAHIER TECHNIQUE
              ↓
MATRICE DÉPENDANCES / BENCHMARKS
              ↓
    ARCHITECTURE EXÉCUTOIRE
              ↓
        PLAN DE PR CODEX
              ↓
             CODE
```

Le futur cahier technique choisira ou benchmarkera : parsers, OCR, locators, SourceAnchor, Evidence, retrieval, embeddings, LLM, stockage, jobs, infra, sécurité technique, génération documentaire et observabilité.

Mais il n’aura pas le droit de redéfinir silencieusement le produit.

---

# 51. Règle de gouvernance après gel

Après `Product Freeze v1.0`, toute modification qui change rôle, autorité, confidentialité, parcours, comportement visible, règle de décision, preuve attendue, engagement, document remis ou périmètre vendu nécessite une **décision propriétaire explicite** et une mise à jour versionnée du cahier.

Une technologie peut évoluer sans rouvrir le Product Freeze si le contrat produit reste inchangé.

---

# 52. Décision immédiate de chantier

Le propriétaire a validé le socle et délégué les choix résiduels ; la présente v0.2 ferme les arbitrages produit.

À partir de maintenant :

- A1 Golden DCE peut être finalisé ;
- **A2 SourceAnchor reste HOLD** jusqu’au contre-audit Work et au Product Freeze v1.0 ;
- Work doit maintenant intervenir comme contre-auditeur, pas comme concepteur principal ;
- les 12 contrats d’écran doivent être consolidés en parallèle ;
- Codex ne transforme pas le cœur produit avant le signal de reprise issu du Product Freeze ;
- aucune ancienne règle V8 ne peut rouvrir une décision propriétaire figée.

---

# 53. Résumé propriétaire en une page

SMART AO doit permettre à un dirigeant de PME BTP de savoir :

> **Est-ce une bonne affaire pour mon entreprise ? Qu’est-ce que l’acheteur exige réellement ? Qu’est-ce qui manque ? Qu’est-ce qui peut me coûter de la marge ? Est-ce que mon équipe est prête ? Qu’est-ce que nous promettons ? Qu’est-ce qui a été validé ? Qu’allons-nous réellement déposer ? Et que transmettons-nous au chantier si nous gagnons ?**

Le collaborateur prépare et prouve.  
Les experts contribuent sur leur périmètre.  
Le Patron arbitre et engage.  
L’administrateur administre sans devenir automatiquement lecteur des secrets métier.  
Les tiers n’accèdent qu’au strict nécessaire.  
L’IA observe, explique, propose et prépare.  
Elle ne décide jamais à la place de l’entreprise.

Le centre du logiciel est l’Affaire.  
Le socle privé est la Mémoire Entreprise.  
La confiance vient des sources, versions, preuves, droits, validations et reçus.

Le produit doit rester utilisable même si l’IA est indisponible.

**Le but n’est pas de générer plus de texte. Le but est de faire prendre de meilleures décisions, éviter les oublis coûteux, protéger la marge et remettre le bon dossier.**
