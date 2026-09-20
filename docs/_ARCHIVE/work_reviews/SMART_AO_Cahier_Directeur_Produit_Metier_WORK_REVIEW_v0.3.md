# SMART AO — Cahier directeur Produit & Métier
## Work Review — Proposition consolidée v0.3

**Date : 13 septembre 2026**  
**Statut : PROPOSITION DE CONTRE-AUDIT — décisions propriétaire du socle préservées ; compléments à approuver, aucun Product Freeze automatique**  
**Propriétaire produit : Dirigeant SMART AO**  
**Rôle du document : devenir la référence unique de ce que SMART AO doit être avant traduction en cahier technique puis exécution par Codex.**


> **Portée de v0.3.** Copie proposée du socle propriétaire v0.2, consolidée le 13 septembre 2026. Les §§45–47 (DEC-01–11, OWN-01–13 et périmètre) restent intégralement identiques. Les autres passages F restent la doctrine courante ; les harmonisations M01–M08 répercutent les décisions déjà figées, sans les rouvrir. Les §§54–57 sont les compléments de contre-audit : toute exigence nouvelle est **P**, toute qualification non démontrée est **W**, même si sa rédaction emploie « doit ». En cas de conflit, une proposition ne remplace jamais une décision F. L'exception OWN-01 figure comme décision à reconsidérer, non comme amendement accepté.
>
> **Verdict historique : non à la promotion immédiate ; oui sous conditions.** Douze lacunes C1 et huit arbitrages sont à fermer. Le rapport détaillé est [01_RAPPORT_CONTRE_AUDIT](product_freeze_review_2026-09-13/01_RAPPORT_CONTRE_AUDIT.md). Ce Work Review est archivé et est remplacé comme référence produit/métier par le cahier consolidé v0.4. Les contrats et recettes étaient rédigés, non validés par prototype ou essais logiciels à cette étape.
>
> **Lecture.** §§0–53 : socle harmonisé ; §54 : modifications et arbitrages ; §55 : règles R01–R16, profils et recettes G01–G52 ; §56 : contrats E01–E12 et surfaces S01/S02 ; §57 : sources et limites. Les chiffres proposés de session, volumétrie, partage, conservation et reprise ne sont ni des lois ni des F.

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

### Décision confirmée — OWN-01 / OWN-06
Lors du provisioning d’un environnement client :
1. SMART AO crée l’organisation ;
2. un premier **Propriétaire** nominatif est créé/invité ;
3. ce Propriétaire active son accès ;
4. il peut inviter d’autres utilisateurs ;
5. il ne peut pas être supprimé tant qu’un autre Propriétaire n’a pas été désigné.

**Statut : F pour le premier compte selon OWN-01 ; compléments de récupération R03 / A02 proposés**

## 8.2 Rôles de compte à distinguer des rôles métier

Rôles à distinguer conformément à OWN-01/OWN-02 :
- Propriétaire organisation ;
- Administrateur ;
- Patron / Dirigeant ;
- Responsable d’offre ;
- Expert ;
- Tiers.

Une personne peut cumuler certains rôles selon la taille de l’entreprise.

**Statut : F sur la séparation des autorités selon OWN-02 ; matrice détaillée R02 proposée**

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

## 9.2 Décisions figées et paramètres à fermer

Décisions déjà figées : MFA obligatoire pour tous les utilisateurs internes (OWN-03) ; réauthentification pour les actions sensibles énumérées par OWN-04, dont P5 ; SSO entreprise en V1.x (OWN-05).

Restent proposés ou à qualifier : invitations et récupération, durée/inactivité des sessions, moyens d'authentification admis, appareils connus, blocage/déblocage, journaux visibles et procédure du dernier Propriétaire compromis. Voir R02/R03, A02 et recettes G14–G20.

**Statut : F sur OWN-03/04/05 ; P / W sur les paramètres R03 et A02 ; T sur les mécanismes futurs.**

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

BOAMP est la source native prioritaire V1 ; TED est prévu en V1.x conformément à DEC-06.

**Statut : F — DEC-06**

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

**Statut : F — DEC-04 / OWN-07**

## 21.3 Paramètres du minimum V1 à fermer

- contrat détaillé du contrôle importé défini par OWN-07, sans rouvrir sa profondeur ;
- formats et règles de fidélité garantis (R06 / A04), sans sélectionner de logiciel ;
- assiette, libellé et calcul de marge/contribution (R09 / A05) ;
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

Le geste final de dépôt reste humain pendant toute la V1, conformément à DEC-05 et OWN-11. Toute automatisation future exige une décision propriétaire séparée.

**Statut : F — DEC-05 / OWN-11**

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

La profondeur minimale V1 est figée par OWN-08. Les comportements détaillés proposés en R12 doivent être qualifiés à partir d’un corpus privé réel, sans déplacer ce minimum hors V1.

**Statut : F — OWN-08 sur le minimum ; P / W sur les compléments et la qualification**

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

Onboarding accompagné sans inscription publique libre : F — OWN-06. Restent à préciser : responsabilité du provisioning et de la configuration, données minimales de démarrage et contrôle des droits initiaux (R02/R03, S02).

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


---

# 54. Changelog de v0.3 et arbitrages proposés


Les M01–M08 sont des harmonisations éditoriales avec les registres déjà figés, pas de nouvelles décisions métier. M09–M17 ajoutent des exigences proposées P ou qualifications W ; seules les exigences déjà F restent F. La copie consolidée conserve les §§45–47 intégralement.

| ID | Emplacement / problème actuel | Modification proposée | Raison / criticité / source |
|---|---|---|---|
| M01 | En-tête, §§0–2 : socle Owner et statut de copie peu distingués | En-tête WORK REVIEW v0.3, règle de précédence, changelog et A01–A08 ; conserver le mandat original. | Éviter une promotion implicite ; C1 L01 ; LOC-01. |
| M02 | §8.1 « Proposition », P ; §8.2 liste P | Rappeler OWN-01/02/06 figés, séparation compte/métier ; détails de droits en R02/R03 restent P. | Ne pas rouvrir le premier compte ; C1 L01/L02 ; LOC-01. |
| M03 | §9.2 questions MFA/SSO/P5 déjà tranchées | Remplacer par décisions F rappelées et paramètres P restant ouverts. | MFA tous internes, step-up OWN-04, SSO V1.x ; C1 L01/L03 ; LOC-01, 19. |
| M04 | §13.1 « P — DEC-06 à signer » | F DEC-06 : BOAMP V1, TED V1.x ; fraîcheur et repli via R15/E02. | Contradiction interne ; C1 L01 ; LOC-01, 25. |
| M05 | §21.2 P DEC-04 et §21.3 profondeur ouverte | Doctrine F DEC-04/OWN-07 ; remplacer la question de profondeur par paramètres de formats/calcul/capacité/cash R09/A05. | Assiette économique observable ; C1 L01/L06 ; LOC-01, 9. |
| M06 | §25 « P — DEC-05 à confirmer » | F DEC-05/OWN-11, geste final humain toute la V1, automatisation future par décision séparée ; détails R11. | Autorité et preuve distinctes ; C1 L01/L09 ; LOC-01, 1/5/7. |
| M07 | §27 « profondeur V1 doit être arbitrée », P/W | Minimum OWN-08 F ; corpus privé et règles de négociation/commande en qualification W, R12. | Ne pas déplacer le privé hors V1 ; C1 L01/L10 ; LOC-01. |
| M08 | §35 onboarding accompagné ou self-service « à arbitrer » | Accompagné sans inscription libre F OWN-06 ; responsabilités/configuration/données minimales P. | Évite un nouveau parcours commercial ; C1 L01 ; LOC-01. |
| M09 | §§5–8/22/26/32 : objet, délégation et portes incomplètes | Ajouter R01–R05, table P0–P7 et 16 profils, renvois par section dans §54. | Autorité/états/invalidations ; C1 L02–L05 ; LOC-01, 15/23. |
| M10 | §§14–18/23 : fidélité sans qualification, candidature/visites/Q&A partiels | Ajouter R06/R07 et tests G01–G11/G37/G40/G50. | Pas de fausse complétude ou formulaire universel ; C1 L07/L08 ; 1–3/14. |
| M11 | §§5.2/15/36 : Mémoire sans cycle précis de validité | Ajouter R08 et S01 : type, entité, activité, validité, propriétaire, confidentialité et snapshot. | Une assurance à jour peut être inapplicable ; C1 L12 ; 10–12/15. |
| M12 | §§19–21/24 : économie et partenaires | Ajouter R09/R10 et A05, plafonner V1 au minimum §F. | Protéger marge sans logiciel universel ; C1 L06/L08 ; 4/9/13, HYP calcul. |
| M13 | §§25–27/47 fin de cycle | Ajouter R11/R12 : signature, preuve graduée, redépôt, privé, résultat par lot, passation avec réserves. | Pas de réussite externe inventée ; C1 L09/L10 ; 1/4/5/7. |
| M14 | §§7/28–31/37–39 : permissions et gouvernance | Ajouter R13/R14, A06/A07 et S02 : paquet tiers, support, export, clôture, données fournisseurs IA. | Droits transversaux, réversibilité ; C1 L11 ; 15–18/20/21/23/24. |
| M15 | §§9/32–34/39–42 : erreurs et qualification | Ajouter R15/R16, A08 et G : réseau, concurrence, notifications, reprise, accessibilité et protocole pilote. | Les états d'échec font partie du contrat ; C2 sauf effets C1 ; 19/22/23. |
| M16 | §§10–12/49 : écrans sans contrat complet | Ajouter E01–E12 et S01/S02, adoption des critères observable avant gel ; conserver OWN-12. | Ne pas déléguer le produit au prototypeur ; C1 L12 ; LOC-01, 22. |
| M17 | §§41–42/48–49 : justification et validation | Ajouter registre des sources/limites, 52 recettes et conditions de fermeture ; aucune recette déclarée passée. | Distinguer proposition, preuve documentaire et preuve logicielle ; C1 définition / C2 mesures ; H/LOC-01. |

### Registre A01–A08 — décisions demandées pour la future fermeture, pas prises par la revue

| ID | Proposition exacte à accepter/amender | Qui décide / éléments requis | Effet si non tranché |
|---|---|---|---|
| A01 | Adopter harmonisations M01–M08, objet affaire/phase/lot/tour R01, minimum P6/P7 et précédence F sur P. | Propriétaire produit ; exemples candidature seule, privé, gain partiel. | L01/L04/L10 restent ouverts. |
| A02 | Adopter R02/R03, délégations, invitations/sessions/récupération ; amender explicitement OWN-01 selon D ou donner un autre comportement sûr et opérable. Valeurs R03 proposées : invitation 7 jours, inactivité 30 min, session absolue 12 h, step-up lié à action/version 5 min. | Propriétaire + responsable sécurité ; preuve d'autorité client et scénario unique compte compromis. Chiffres HYP, pas exigence ANSSI. | L02/L03 ouverts ; aucune interprétation technique ne règle seule le conflit OWN-01. |
| A03 | Adopter portes R04/R05, B0/B1/B2 et conditions de levée ; définir qui accepte le risque économique dans quel périmètre et les effets d'une modification. | Propriétaire métier, responsables offre/Direction ; revue G02/G10/G30/G51. | L05/L09 ouverts. |
| A04 | Adopter contrat de formats R06, qualification R16 et garantie de volume : proposition PDF texte/scans, DOCX/XLSX qualifiés ; anciens formats conservés avec parcours externe. Hypothèses de test : 500 fichiers, 2 Go/dossier, 200 Mo/fichier, archives 3 niveaux ; mesurer puis accepter/amender avant promesse. | Propriétaire + pilotes ; corpus représentatif, seuils compatibles besoin/coût ; futur cahier technique démontre faisabilité. | L07 ouvert ; aucun « tous formats » vendu. |
| A05 | Adopter calcul R09 : contribution et taux sur vente HT couverte, distinguer taux sur coût ; coût inconnu ≠ zéro ; minimum capacité/trésorerie et décisions sous hypothèse. | Patron/DAF/métreur ; exemple 120/100 et vrai chiffrage pilote. | L06 ouvert ; métrique « marge » non normalisée. |
| A06 | Adopter R13 : autorité par contenu, destinataire vérifié, paquet externe exact révocable ; défaut proposé 7 jours, support exceptionnel 1 h ; partage financier seulement avec autorité adéquate. | Propriétaire + autorité Direction + sécurité ; G24/G45/G46/G52. | L11 ouvert ; les durées sont P, pas règle propriétaire actuelle. |
| A07 | Adopter matrice de finalités/droits/export R14 et faire qualifier durées/contrats/flux. Hypothèses proposées : réversibilité 30 jours, lien export 7 jours, purge sauvegardes ≤90 jours, journaux 12 mois sauf justification. | Propriétaire + spécialiste juridique + responsable de service ; catégories, litiges, prestataires et territoires documentés. | L11 ouvert ; aucune durée universelle ni promesse de résidence déduite. |
| A08 | Adopter contrats d'écrans/états R15/R16 et plan de qualification ; objectifs de reprise proposés perte maximale 1 h / rétablissement 4 h à faire confirmer avant engagement commercial. Faire qualifier accessibilité et usages IA selon cadre applicable. | Propriétaire + responsable service + pilotes ; prototype OWN-12, objectif réaliste et périmètre de preuve. | L12 reste ouvert si contrats/parcours non adoptés ; objectifs commerciaux et mesures encore à qualifier. |

Les dossiers R/E détaillent des comportements recommandés, y compris des valeurs par défaut. **Aucune valeur chiffrée nouvelle n'est une prescription juridique ni une décision F.** Toute acceptation doit identifier l'approbateur, la date, le texte accepté, les amendements et les preuves ; un tableau rempli par l'auditeur ne suffit pas. Pour une règle dépendant d'une qualification juridique, employer explicitement « À valider par spécialiste juridique » jusqu'à conclusion tracée.

## Décision propriétaire à reconsidérer — OWN-01


**Une seule remise en question forte : OWN-01, obligation de conserver au moins un Propriétaire actif.** La décision actuelle reste reproduite intégralement et applicable tant que le propriétaire ne l'a pas amendée.

Cas : l'unique Propriétaire est compromis et aucun second titulaire n'est désigné. Maintenir sa session pour respecter « actif » empêche le retrait immédiat des droits ; le supprimer détruit la continuité d'autorité. La CNIL recommande le retrait des accès devenus inappropriés et une procédure d'incident ; elle ne prescrit pas de conserver un compte compromis actif. L'incompatibilité avec OWN-01 est une **inférence de l'audit**, pas une citation de loi imposant un second Propriétaire.[^15][^23]

**Amendement proposé A02, non adopté :** « Une organisation conserve au moins un Propriétaire nominatif désigné. En fonctionnement normal, au moins un Propriétaire est actif. En cas de compromission ou de perte d'accès de l'unique titulaire, son accès peut être suspendu sans supprimer son identité ni son historique. Les actions réservées restent bloquées jusqu'à récupération ou réattribution par la procédure de preuve d'autorité approuvée ; le support n'acquiert pas pour autant l'autorité métier. » Voir R03/G18/G19. La procédure exceptionnelle doit être déterminée avant le gel, avec éléments de preuve organisationnels vérifiables ; deux intervenants SMART AO ne remplacent pas l'autorité du client.

Les autres tensions ne demandent pas de rouvrir les choix F : le P6/P7 minimal existe déjà au §47, leurs versions approfondies restent V1.x ; S01/S02 matérialisent des espaces et fonctions déjà F, sans remplacer les douze écrans ; la mention d'automatisations de plateformes en V1.x n'autorise pas à elle seule le dépôt autonome : DEC-05 exige une décision séparée pour toute automatisation future du geste final. Pas de proposition de SSO V1, de plateforme mutualisée, d'ERP ou de nouveau moteur de chiffrage.


---

# 55. Règles fonctionnelles, rôles et recettes proposés

## Statut de cette proposition

Compléments de contre-audit au socle v0.2, destinés à la revue v0.3. **Aucune règle nouvelle de ce fichier n'est une décision propriétaire déjà acceptée.** Les invariants DEC/OWN existants demeurent prioritaires. Les arbitrages A01–A08 sont regroupés dans le rapport principal. R01–R16 désignent les règles proposées, jamais des technologies. Les recettes G01–G52 sont à exécuter sur prototype puis logiciel ; elles ne sont pas déclarées passantes.

## R01 — Affaire, lots, phases et statut

Une Affaire représente la réponse d'une entreprise cliente à une consultation identifiée. Elle contient les lots visés et distingue pièces communes et pièces propres à un lot. Une même pièce commune ne doit pas être dupliquée sans lien de version. Décision, prix, admissibilité, pli et résultat portent le périmètre de lots concerné. Un gain partiel n'est pas un gain de toute l'Affaire.

À l'ouverture : entreprise candidate et établissement, acheteur/client, référence externe ou interne, public/privé, type de procédure déclaré, lots, responsable, échéances et canal de remise. Les champs inconnus sont explicitement inconnus ; l'absence d'un DCE intégral n'interdit pas de créer un dossier préparatoire.

Phases reconnues : candidature, offre initiale, clarification, offre révisée lorsque la procédure l'autorise, attribution/notification, passation, clôture. Un appel d'offres restreint peut demander une candidature seule : ni prix ni mémoire d'offre ne deviennent obligatoires à cette étape.[^1][^2]

Les objets n'utilisent pas un statut global ambigu :

- **Travail** : brouillon, en préparation, en revue, prêt, clos/archivé.
- **Décision** : à décider, GO, GO sous conditions, ATTENTE, NO-GO, ABANDON ; chaque décision garde sa portée et sa validité actuelle.
- **Remise** : non préparée, candidate, autorisée, tentative, transmission déclarée, réception prouvée, rapprochement partiel, incohérence, retard constaté ; l'admission juridique n'en découle pas.
- **Résultat** : inconnu, rejet/notifié perdu, attribution annoncée, marché notifié/accord documenté, sans suite, retiré ; par lot.

Une relance ou un nouveau tour est lié au précédent ; les preuves de remise antérieures restent figées. Le statut « gagné » exige l'identification de la pièce externe qui le motive ; une annonce commerciale ou un appel téléphonique reste à confirmer. La décision d'étudier ne signifie pas autorisation de remettre.

## R02 — Autorité, multi-Patron et séparation des droits

Le rôle métier, le périmètre d'Affaire et le droit d'accès à une catégorie sensible sont distincts. Le Propriétaire gère l'organisation ; sa seule qualité ne lui ouvre pas les marges. À la création, les rôles Patron et Propriétaire sont attribués séparément et explicitement. Le provisioning ne confère au support aucun droit métier.

Un Administrateur peut exécuter une attribution préalablement approuvée, mais ne peut ni s'accorder ni accorder seul un droit Direction, Patron ou d'export complet. La demande identifie bénéficiaire, approbateur habilité, portée, motif, début/fin et éventuel plafond. Celui qui n'a pas pouvoir de déléguer un droit ne peut le créer indirectement en attribuant un rôle. Le retrait d'accès pour incident n'exige pas l'accord de la personne compromise.[^15]

Une PME peut cumuler Propriétaire et Patron sur une même personne, sans imposer artificiellement deux salariés. Le cumul autorisé reste visible dans le journal. Une organisation distingue délégation de décision SMART AO et pouvoir juridique de signer : une délégation d'écran n'est pas un mandat de signature.

Chaque porte possède un décideur actif identifié et, s'il existe, un suppléant désigné. Plusieurs Patrons peuvent décider sur des Affaires différentes. Deux décisions simultanées sur la même porte/version ne s'écrasent pas : la seconde reçoit le nouvel état et doit être confirmée comme décision de remplacement motivée. Aucune unanimité ou quorum implicite n'est introduit.

Délégation : portes autorisées, lots/Affaires, catégories visibles, montant/exposition si applicable, période, délégant et délégataire. Elle n'est pas transmissible par défaut, expire sans renouvellement automatique et ne transfère pas les décisions passées. L'absence du Patron n'élève jamais automatiquement un collaborateur.

## R03 — Identité, invitation, sessions et récupération

Proposition de réglages V1 à approuver dans A02 : invitation nominative à usage unique valable 7 jours ; vérification de l'adresse, acceptation de l'invitation et MFA avant tout accès métier interne ; pas d'obligation de domaine email commun. Une invitation expirée peut être réémise sans ouvrir de compte doublon ni conserver un ancien privilège non revérifié.

Sessions proposées : 30 minutes d'inactivité, durée absolue de 12 heures, avertissement 2 minutes avant expiration lorsque l'écran est actif. Ces valeurs sont des choix de travail, pas des exigences chiffrées attribuées à l'ANSSI. Un enregistrement automatique en arrière-plan ne compte pas comme activité humaine. La réauthentification de OWN-04 est liée à l'action et à la version affichées ; autorisation valable au plus 5 minutes, inutilisable si la cible ou les droits changent.[^19]

Un brouillon n'est marqué « enregistré » qu'après confirmation. L'expiration masque les données ; après authentification du même utilisateur et contrôle des droits, le dernier travail confirmé est restauré, et le travail local restant est proposé avec son statut. Une révocation interdit sa publication. Les données d'un compte ne doivent pas réapparaître sous un autre compte du même appareil.

Récupération normale : moyen de secours préenregistré ou validation par un Propriétaire habilité, vérification d'identité hors de la session suspecte, révocation des sessions et anciens facteurs, nouvel enrôlement MFA, notification aux contacts de sécurité. Aucun mot de passe d'origine n'est envoyé. Le support ne décide pas seul de la qualité de Patron.

Propriétaire unique inaccessible : procédure accompagnée avec vérification des pouvoirs de représentation, deux intervenants SMART AO distincts pour l'exécution sensible, justification et journal consultable par le client après récupération. Un email reçu ou une connaissance de dossier ne suffit pas. Les pièces de vérification sont minimisées et leur conservation définie avant ouverture commerciale. Proposition de preuve A02 : rapprocher la personne et l'entreprise contractante identifiée (dont SIREN), contrôler un justificatif actuel des pouvoirs de représentation ou une délégation vérifiable, puis confirmer par un canal indépendant déjà enregistré ou vérifié auprès d'une source organisationnelle indépendante du compte suspect. La liste des éléments examinés, le résultat et les deux exécutants sont tracés ; si l'identité ou le pouvoir demeure contradictoire, aucune réattribution. Le support transmet le cas au représentant légal/responsable contractuel vérifié. Cette procédure ne crée ni un mandat de signature ni un droit automatique aux marges.

**Décision propriétaire à reconsidérer — OWN-01, exception de sécurité** : conserver un Propriétaire désigné, mais autoriser la suspension de tout accès actif en cas de compromission du dernier compte. La récupération restaure ensuite l'accès. L'invariant actuel « au moins un Propriétaire actif » demeure la décision figée tant que A02 n'est pas arbitré ; G18 décrit l'exception proposée et non une règle déjà adoptée.

## R04 — Portes P0–P7 : contrat minimal

Les noms ci-dessous reprennent les tableaux métier antérieurs LOC-02/03. La portée, les sorties et invalidations sont consolidées ici. Les portes sont des décisions explicites ; elles n'imposent pas huit écrans ou huit réunions. Des validations successives peuvent être réalisées dans une même séance tout en gardant leurs effets et traces distincts.

| Porte | Condition d'entrée / pièces minimales | Qui décide ; résultat observable | Ce qui rouvre ou invalide |
|---|---|---|---|
| P0 Cibler | Opportunité identifiée ; critères commerciaux ou inconnus visibles | Patron ou délégataire P0 : suivre/qualifier/écarter avec motif ; affectation | Modification substantielle de périmètre ou de cible ; réouverture humaine |
| P1 Ouvrir | Dossier reçu ou phase candidature documentée ; lots, responsable et échéance connue ou manquante signalée | Patron ou délégataire P1 : autorise l'effort d'étude ; Affaire ouverte avec manques | Changement d'entreprise candidate, de procédure ou périmètre qui invalide le choix initial |
| P2 GO de principe | Éligibilité par phase/lot, visite, charge d'étude, partenaires et MIRP examinés | Patron/délégataire P2 : GO, condition, attente ou renoncement ; préparation autorisée dans les limites enregistrées | Nouvelle exclusion, visite impossible, partenaire critique retiré, rectificatif touchant le périmètre |
| P3 GO économique | Chiffrage identifié, couverture coûts, marge définie, capacité et trésorerie revues | Patron/délégataire P3 avec droits financiers : accepte scénario et risques économiques | Prix, quantité, validité fournisseur, engagement, trésorerie ou ressource critique modifiés |
| P4 Autoriser l'offre | Réponse de la phase courante, critères, engagements, pièces et contrôles de contenu revus | Patron/délégataire P4 : autorise le contenu et désigne version candidate ; pour candidature seule, P3 non applicable avec motif | Tout contenu engageant/prix/pièce/lot modifié ; nouvelle dépendance critique |
| P5 Autoriser la remise | P4 courant, paquet exact, manifeste, destinataire/canal, signataires et échéance revérifiés | Patron/délégataire P5 + step-up : autorise ce paquet pour ce tour ; opérateur humain remet | Modification d'un fichier, signature, manifeste, destinataire, droits nécessaires ou échéance pertinente |
| P6 Accepter une modification | Demande de clarification/négociation/mise au point identifiée et autorisée dans la procédure | Patron/délégataire P6 : accepte/refuse les impacts ; P3/P4/P5 rejouées selon modifications et nouvel envoi | Nouvelle concession, prix, délai, pièce contractuelle ou condition modifiés |
| P7 Accepter la passation | Lot gagné étayé, version contractuelle identifiée, engagements et risques affectés, destinataire chantier | Patron/délégataire P7 : accepte la passation ; conducteur accuse réception ou formule réserves | Nouvelle pièce contractuelle ou engagement ; nouvelle édition de passation et accusé |

P6 et P7 **minimales** sont nécessaires à DEC-02 et OWN-08. Leur approfondissement reste V1.x. P7 ne constitue ni un ordre de service ni l'autorisation juridique de commencer des travaux. Les événements d'exécution sont enregistrés s'ils existent, sans gestion chantier.

Un NO-GO/ABANDON désactive les tâches futures de réponse après présentation de leur liste, sans supprimer pièces ou historique. Une réouverture est motivée et réévalue les échéances et dépendances. ATTENTE exige responsable, motif et date/événement de réexamen. Une condition GO a un responsable, une preuve de levée, une échéance et la porte qu'elle interdit de franchir tant qu'elle reste ouverte.

## R05 — Blocages, dérogations et invalidation

Trois classes visibles : **B0 intégrité/autorité**, **B1 exigence critique non satisfaite**, **B2 risque économique ou organisationnel arbitrable**. Ne pas confondre ces classes avec la criticité C1/C2/C3 de l'audit, ni les portes P0–P7.

- B0 : droits absents, version divergente de l'autorisation, fichier dangereux, destinataire non identifié, identité non vérifiée, impossibilité d'établir quel paquet est autorisé. Aucune dérogation Patron ne fabrique une preuve ni ne contourne ces barrières.
- B1 : pièce/visite/signature exigée manquante, admissibilité critique inconnue, format imposé non démontré. Revue de la source, correction, réponse de l'acheteur ou qualification spécialisée nécessaire. Une simple acceptation de risque interne ne transforme pas l'offre en conforme.
- B2 : coût estimé, marge faible, surcharge probable, prix fournisseur à renouveler avec alternative explicite. Le Patron peut accepter un risque borné, avec scénario, motif, responsable et expiration. Le prix reste « accepté sous hypothèses », jamais « entièrement prouvé ».

L'autorisation P5 exige la levée des B0 et B1 applicables. Un dépôt réalisé ailleurs malgré ces blocages peut être consigné comme **remise hors autorisation SMART AO**, avec preuve ; il n'est ni effacé ni régularisé rétroactivement. Politique à approuver dans A03.

Une correction crée une nouvelle version ; toutes les validations dépendantes affichent « à revalider ». Les validations non touchées restent utilisables. Si la portée d'un rectificatif n'est pas établie, les autorisations de remise des lots potentiellement touchés sont suspendues jusqu'à revue d'impact. Chaque réouverture expose l'événement source et son auteur. Changer une note interne sans dépendance n'invalide pas artificiellement toute l'offre.

## R06 — Lecture, couverture et fidélité documentaire

Avant import, afficher les limites du profil de service : taille par fichier/dossier, nombre de fichiers, profondeur d'archives, formats admis, formats lus, formats modifiables et formats seulement conservés. Proposition A04 : PDF texte et scan lisible, DOCX et XLSX sans fonctionnalités non prises en charge pour la qualification initiale ; XLS/DOC historiques conservés, avec traitement externe guidé et réimport si la fidélité n'est pas démontrée. Aucun rejet silencieux ni assimilation du format conservé au format éditable.

Fichier protégé : demander une copie lisible autorisée ou proposer revue externe, jamais casser la protection. Archive imbriquée : inventaire, limite atteinte visible, traitement des éléments admis sans prétendre couvrir le reste. Fichier suspect : isolé de toute ouverture active, exclusion des aperçus et de l'IA, identifiant et motif visibles sans exposer le contenu dangereux. L'original logique est conservé conformément à la doctrine, mais sa restitution éventuelle passe par une procédure contrôlée ; il n'est pas téléchargeable comme une pièce ordinaire.

Quatre couvertures distinctes : **fichiers reçus**, **contenu effectivement lu**, **exigences revues**, **réponse/prix couverts**. Chaque compteur indique dénominateur et exclusions. Avoir lu 9 fichiers sur 10 ne prouve pas 90 % de conformité. Les plans non interprétés, normes payantes non accessibles, pages scannées illisibles et pièces simplement citées créent des inconnus localisés.

Source consultable : fichier/version, page ou feuille/cellule, extrait et contexte. Toute ancre devenue indisponible affiche son état ; aucune citation décorative ou référence vers une autre version. Une correction humaine ne remplace pas le document acheteur.

Travail sur Word/Excel : télécharger copie, modifier dans l'outil habituel, réimporter comme version candidate, comparer changements. Contrôler feuilles/lignes/colonnes, formules et résultats disponibles, cellules masquées, liens externes, macros, zones protégées, suivis de modifications, commentaires et dépassement de pages. Une fonctionnalité non vérifiable est nommée ; aucune exécution automatique de contenu actif. Une formule affichée avec résultat ancien n'est pas un total fiable. Le format imposé est rendu tel quel ou déclaré non qualifié : exporter un PDF n'est pas un substitut silencieux à XLS.

## R07 — Éligibilité, candidature, visite, questions et critères

Le responsable d'offre établit une checklist par phase, entité et lot : conditions d'accès, capacités demandées, formes de groupement, interdictions de candidatures multiples lorsqu'applicables, documents à fournir maintenant/ultérieurement, signature, variantes/PSE, tranches et échantillons éventuels. Les seuils et délais généraux ne sont pas codifiés comme vérité universelle de chaque consultation. Le RC et les pièces applicables restent consultables.[^2][^3][^4]

DUME et DC1/DC2/DC4 sont des voies/formulaires à qualifier, pas une liasse toujours cumulative. Une déclaration sur l'honneur demeure un brouillon jusqu'à validation de son auteur habilité. SMART AO ne produit pas une fausse attestation fiscale, sociale, d'assurance ou de visite.

Visite : obligatoire/facultative/incertaine, site/lot, inscription, créneau, participant/remplaçant, preuve demandée, constat terrain et date limite. Une photo ne vaut pas attestation acheteur. L'impossibilité de visite remonte au responsable et au Patron ; une éventuelle dispense doit être prouvée.

Questions : brouillon, approuvé pour émission, émission déclarée, émission prouvée, réponse reçue, impact traité. Destinataire et canal sont contrôlés ; la question ne joint ni marge ni note Direction. Une réponse de l'acheteur est une nouvelle source à rapprocher du dossier, pas une simple conversation. Sans connecteur autorisé, émission humaine et import de preuve. Une date annoncée oralement reste à confirmer.

Critères : intitulé, pondération lorsqu'elle existe, sous-critères connus, section de réponse, limite de pages/format, preuve attendue et responsable. Aucune note de jury prédite n'est présentée comme fiable. Les exigences environnementales, sociales et de réemploi sont prises en compte selon le DCE et le régime temporel applicable ; détecter une absence ne permet pas d'affirmer seul l'illégalité du marché.[^14]

## R08 — Mémoire Entreprise et preuves réutilisables

Chaque élément a un propriétaire de contenu, une entité/établissement, une sensibilité, une source, un domaine d'emploi, une période pertinente, un état de vérification et une date de prochaine revue. États : brouillon, à vérifier, réutilisable sur périmètre défini, expiré, retiré, archivé. « Réutilisable » ne signifie pas recevable pour toutes les consultations.

Assurance : contrôler la concordance assuré/activité/technique/périmètre/période, avec réserve explicite si nécessaire. Qualification : spécialité, niveau, établissement, validité et preuve d'équivalence admise si le dossier le prévoit. Vigilance : authenticité vérifiée avec référence/date, prochain contrôle adapté au contrat, et transfert au chantier des échéances postérieures ; SMART AO ne devient pas un service de conformité fournisseur pendant tout le chantier.[^10][^11][^12]

Référence : réalisé/en cours, rôle réel titulaire/cotraitant/sous-traitant, part effectivement réalisée, autorisation d'usage et coordonnées publiables. Personnel : compétences, habilitations et disponibilité utile ; CV minimisé, pas de dossier médical, salaire ou appréciation RH dans les réponses. Matériel : détenu/loué/envisagé, disponibilité et preuve associée. Partenaire : consulté, réponse reçue, retenu en interne, engagement documenté, accepté/agréé lorsque requis ; ne pas confondre ces états.

Le réemploi dans une offre fixe la version de la preuve utilisée. Son expiration ou retrait alerte les offres ouvertes dépendantes ; il ne réécrit pas une offre remise. Le REX n'alimente pas automatiquement la mémoire validée : un responsable confirme vérité, portée, confidentialité et droits. Une référence perdue ne devient jamais un chantier réalisé.

## R09 — Prix, marge, capacité et trésorerie minimales

Le contrat de prix identifie : fichier importé/version, type DPGF/BPU/DQE/devis, monnaie, HT/TTC, unités, quantités, prix unitaires, sous-totaux, formules/arrondis, options/variantes/tranches, validité, exclusions et auteur de revue. La valeur contractuelle de chaque pièce est qualifiée depuis le dossier ; un DQE n'est pas automatiquement une quantité commandée, et un plafond d'accord-cadre n'est pas du chiffre d'affaires garanti.[^9]

Une ligne de besoin peut être couverte par plusieurs postes et réciproquement. Conserver affectation et justification pour éviter doubles comptes et faux « manquants ». Ne pas produire un métré automatique généralisé. Toute quantité non prouvée reste une hypothèse du métreur. Les frais de site occupé, coactivité, levage, déchets, études, essais, DOE, nuit, aléas amiante/plomb et interfaces inter-lots ont un responsable et une couverture ou un inconnu.

Proposition de calcul A05 : **contribution prévisionnelle = prix de vente HT − coût prévisionnel couvert** ; **taux sur vente = contribution / vente HT** ; un taux sur coût, s'il est affiché, porte explicitement son dénominateur. Il ne s'agit pas d'un résultat net comptable. Indiquer si le coût inclut main-d'œuvre, achats, sous-traitance, frais chantier, frais généraux alloués et provisions. Une composante inconnue n'est jamais zéro. Vente nulle : taux non calculable. Exemple de recette : vente 120, coût 100 → contribution 20, taux sur vente 16,67 %, taux sur coût 20 %.

Le collaborateur voit, selon habilitation, prix de vente nécessaire à la réponse et état de couverture. Achats voit les devis de son lot sans obtenir la marge globale. DAF voit les hypothèses financières déléguées. Aucun total, graphique, export ou réponse IA ne permet de déduire les composantes Direction masquées par simple soustraction.

Capacité minimale V1 : périodes et ressources critiques déclarées, autres engagements agrégés autorisés, disponibilité validée et responsable. Exemple : la même équipe CVC promise simultanément à deux chantiers crée un conflit ; aucun planning d'exécution complet n'est demandé.

Trésorerie minimale V1 : échéancier sommaire d'encaissements/décaissements, avances, approvisionnements, retenues/garanties, délais de paiement, variation des prix et besoin maximal estimé de financement. Sources et hypothèses explicites, trésorerie disponible datée, scénario défavorable simple. Aucune connexion bancaire, écriture comptable ni paiement. Une donnée inconnue donne une appréciation « non démontrée » soumise à décision, pas un feu vert.

## R10 — Partenaires, groupements et engagements

V1 conserve une fiche de comparaison manuelle structurée et des pièces : périmètre, exclusions, quantités, taxes, coût complet, délais, validité, capacités et documents. La consultation multi-fournisseurs automatisée est différée. Un devis reçu n'est ni un contrat signé ni une réservation de capacité.

Groupement : mandataire, membres et identités légales, lots/prestations/parts, forme de responsabilité annoncée, mandats et état de candidature de chaque membre. Seuls les documents autorisés sont échangés ; pas de mémoire globale commune ni de marges partagées par défaut. Solidarité et engagements inhabituels sont présentés au Patron avec validation spécialisée si nécessaire.[^4]

Sous-traitant : rang connu/inconnu, prestations, montant, paiement, capacités mobilisées, déclaration et acceptation/agrément selon régime. Garanties et obligations privées sont signalées et adressées à une personne compétente, sans génération d'avis juridique.[^13]

Engagement : texte exact, origine, destinataire, lot, version, auteur, validation, conditions, moyens et coût, responsable futur. La relecture humaine couvre aussi les engagements que l'IA n'a pas repérés. Une promesse « intervention sous 2 heures » ne peut être reprise d'un ancien mémoire sans revue de la capacité réelle. Un élément validé par un expert n'est pas automatiquement accepté par le Patron.

## R11 — Coffre, signature, dépôt humain et preuve

Un paquet candidate est une sélection explicite de fichiers/version par lot, phase et tour, avec liste de pièces et contrôles. Le manifeste porte identité candidate, consultation, périmètre, fichiers et caractéristiques permettant de distinguer leur contenu, signatures associées, horodatage, auteur et autorisation. L'empreinte interne ne prouve pas à elle seule la réception externe.

Séparer décideur interne, personne habilitée à signer et opérateur de dépôt. Contrôler les signatures exigées **par pièce et par phase**. Un login, un clic P5, une image de signature ou la signature d'une archive ne prouve pas automatiquement la signature de chaque pièce requise. La signature externe peut être effectuée humainement puis réimportée avant le contrôle final P5 ; pas de modification du contenu signé.[^1]

Après P5 : paquet exportable exact et consignes de canal ; tentative enregistrée par opérateur ; preuve externe importée. Le rapprochement compare consultation, lot/tour, entreprise, date/heure et, seulement si disponibles, noms, tailles, empreintes ou inventaire externe. Si le reçu ne détaille pas les fichiers, afficher **réception du pli prouvée — contenu non entièrement rapprochable**, avec déclaration opérateur et éléments disponibles. Ne pas exiger une preuve que la plateforme ne produit pas, ni affirmer une correspondance complète sans elle.

En cas de redépôt, alerte « préparer une nouvelle offre complète pour le périmètre concerné » ; nouveau paquet, nouvelles validations pertinentes et nouveau reçu. L'ancien reçu reste rattaché à l'ancien paquet. La règle de la dernière offre reçue dans le délai est documentée, sans assimilation à une admission au fond.[^5]

Copie de sauvegarde : parcours facultatif avec modalités prévues, contenu, date limite, expédition/réception et preuve propres. Elle reste distincte du paquet principal et ne garantit pas un rattrapage. Aucun envoi autonome V1.[^7]

Les limites de nommage, taille, signatures et formats propres au profil acheteur sont saisies ou confirmées avec source. Prévoir un test préalable sur la plateforme lorsque proposé. À l'échéance dépassée, l'application conserve les fichiers et faits ; elle ne fabrique pas un report ni un succès. Le Patron choisit l'escalade et la suite à donner hors prétention de conseil juridique.

## R12 — Résultat, négociation, privé, passation et REX

Toute demande reçue après une remise est classée : précision sans modification engageante, demande de pièce, nouvelle offre, négociation autorisée, mise au point ou événement de résultat. La phase « après classement » des anciens documents ne couvre pas toutes les négociations : le cycle proposé accepte des tours antérieurs à l'attribution, sans autoriser une négociation interdite dans une procédure.

Une variation de prix/délai/prestation/engagement est soumise à P6 minimale, avec retour ciblé P3/P4/P5 pour le nouvel envoi. Une durée de validité de l'offre à prolonger est une décision, pas une simple modification de date.

Privé : invitation, devis/offre, commande et contrat gardent chacun état, version et preuve. Acceptation alléguée, acceptation documentée et accord sur contenu sont distingués. Une commande reçue n'efface pas les réserves du devis. Le régime, les pouvoirs, les conditions de formation de l'accord et les garanties doivent être **à valider par spécialiste juridique** si l'écart engage l'entreprise. Aucun droit automatique de négocier ou de commencer le chantier n'est déduit par le logiciel.

Passation minimale par lot gagné : périmètre effectivement vendu, documents contractuels identifiés et ordre applicable confirmé, prix/budget selon droits, planning contractuel, moyens promis, engagements, hypothèses acceptées, points non résolus, partenaires, risques, questions en suspens, prochaines preuves/échéances. Responsable chantier nominatif et accusé de prise en charge avec réserves possibles. Une réserve critique non affectée interdit de déclarer la passation achevée. Les révisions ultérieures produisent une nouvelle édition.

REX minimal : résultat externe et motif connu/inconnu, retour acheteur, écarts constatés, estimations séparées des réalisations, action d'amélioration et validation avant capitalisation. Aucun calcul de « marge protégée » ne prétend mesurer un résultat réel sans coûts et contrefactuel documentés.

## R13 — Confidentialité, partages, support et IA

Catégories minimales : public autorisé, interne Affaire, restreint métier, Direction, personnel/bancaire restreint. Les droits s'appliquent au contenu mais aussi aux titres, résultats de recherche, compteurs, notifications, exports, historique, liens directs, brouillons et réponses IA. Une source interdite ne doit pas être révélée dans l'explication d'un refus.

Partage externe : destinataire identifié, aperçu exact de son paquet, finalité, expiration, téléchargement/dépôt autorisés et confirmation humaine. Proposition A06 : accès 7 jours au plus par défaut, vérification du destinataire ; documents Direction exclus par défaut. Un paquet de prix d'achat nécessaire peut être autorisé par catégorie ; pas d'interdiction universelle des données financières. Renouvellement et élargissement sont de nouvelles autorisations. Un fichier déposé par un tiers est non fiable jusqu'aux contrôles. Un lien transféré ne doit pas donner accès sans contrôle du destinataire.

Révocation : coupe nouveaux accès et téléchargements ; signale téléchargements antérieurs, n'en promet pas l'effacement. En cas d'erreur de destinataire : suspension immédiate, journal des accès, information du responsable sécurité et traitement d'incident. Une analyse IA déjà lancée perd le droit de publier un résultat devenu interdit.

Support : diagnostic par métadonnées minimales ; contenu inaccessible par défaut. Accès exceptionnel approuvé par l'autorité client correspondant aux données, nominatif, périmètre, motif et expiration ; proposition A06 : 1 heure renouvelable par nouvelle approbation. Accès fortement restreint soumis au step-up OWN-04. Un accord de l'Administrateur seul n'ouvre pas les marges. L'accès cesse à expiration/révocation et sa trace est fournie au client.[^15][^17]

IA : contexte limité à l'utilisateur, entreprise, Affaire et sources autorisées ; aucun apprentissage interclients par défaut. Chaque proposition critique affiche type de sortie, sources/version, limites de lecture et validation attendue. Des documents peuvent contenir de vraies consignes acheteur destinées au candidat, mais jamais des ordres au système de partager des données ou changer les droits. Un passage hostile est signalé ; l'analyse des autres pièces reste possible. Les tests adverses couvrent demandes d'exfiltration et instructions masquées, sans promettre leur détection exhaustive.[^20][^21]

Panne/quota IA : traitement signalé interrompu ou partiel, aucune conclusion verte par défaut ; documents, recherche non conversationnelle, saisie d'exigences, décisions humaines, export, Coffre et remise restent utilisables. Reprise explicite sans doubler ni remplacer les validations. Avant une opération payante inhabituelle : coût estimé ou limite connue, périmètre et autorité budgétaire ; pas de dépense automatique illimitée.

## R14 — Données, export, suspension et fermeture

Matrice de gouvernance obligatoire avant gel : catégories, finalité, responsable, habilitations, base active, archive, déclencheur, durée, justification, bénéficiaire export, traitement des sauvegardes et destruction. Distinguer données métier client, données de gestion du service, pièces personnelles, journaux sécurité et preuves conservées pour litige. Le rôle juridique de SMART AO est qualifié par traitement, pas globalement par son statut SaaS.[^17][^18]

Proposition A07 : fenêtre de réversibilité de 30 jours, lecture/export autorisés après gel des nouvelles analyses ; téléchargement export expirant à 7 jours ; purge des sauvegardes au plus 90 jours après suppression active, hors conservation légalement justifiée et isolée. Ces durées commerciales/organisationnelles sont **à valider par spécialiste juridique** et par capacité de service ; elles ne remplacent pas les durées de conservation par finalité. Proposition journaux sécurité : 12 mois, exceptions documentées ; historique contractuel selon politique distincte.[^16]

Matrice de travail A07 à compléter par les durées légalement/contractuellement qualifiées avant approbation ; elle fixe déjà qui décide et ce qui ne peut pas être purgé indistinctement. Une ligne non qualifiée ne devient jamais une conservation illimitée implicite.

| Catégorie | Finalité / responsable côté client | Accès et export | Déclencheur et règle de fin proposés | Point de qualification |
|---|---|---|---|---|
| DCE, réponses et pièces contractuelles | Répondre puis prouver l'engagement ; responsable offre, puis responsable contractuel | Équipe du périmètre ; export client habilité avec sources/versions | Affaire close : sortie de l'espace de travail actif, revue de conservation ; durée d'archive contractuelle explicite ; fin de service : export et fenêtre 30 jours proposée | Durée par nature de marché, garanties et contentieux : à valider par spécialiste juridique ; pas de durée unique BTP inventée |
| Décisions, manifestes, reçus et engagements | Prouver auteur, périmètre et contenu ; Patron/responsable contractuel | Droits d'Affaire et Direction selon contenu ; export de preuve | Même politique d'archive qualifiée que l'engagement concerné ; événement de litige isole la conservation nécessaire | Suppression d'un compte ne supprime pas la preuve ; revue régulière du motif de maintien |
| Prix d'achat, marge, trésorerie et RIB | Préparer décision/engagement ; DAF/Patron habilité | Direction ou délégation précise ; aucune exportation par simple droit d'administration | Usage actif tant que pertinent ; retirer références bancaires obsolètes de la réutilisation ; conserver uniquement preuves nécessaires selon finalité | Finalités bancaires distinctes du dossier AO ; pas de connexion, paiement ni archive comptable universelle |
| CV, contacts et habilitations du personnel | Démontrer capacités utiles ; propriétaire de contenu administratif/QSE | Données minimisées selon affaire ; accès restreint aux originaux | Départ/retrait : cesser réutilisation immédiatement ; revue et suppression des copies sans finalité ; preuve déjà remise traitée selon politique du dossier | Droit des personnes et preuve contractuelle à concilier ; aucune donnée médicale à collecter pour ce besoin |
| Assurances, qualifications, vigilance, références et matériel | Réutilisation et applicabilité ; propriétaire de chaque catégorie | Administratif/QSE et contributeurs concernés | Expiration/retrait : non réutilisable ; anciennes versions liées aux offres conservées selon politique du dossier ; autres copies purgées après revue | Validité d'une pièce ≠ durée légale de conservation ; contrôle périodique adapté au contrat |
| Journaux de sécurité et accès support | Sécurité et responsabilité ; responsable sécurité/service | Accès limité ; extraits client sans exposer autres personnes/clients | 12 mois proposés, puis suppression ; exception motivée/isolée pour incident en cours ; renouvellement explicite du motif | Recommandation CNIL 6–12 mois, exceptions ; ne pas mesurer la productivité des salariés |
| Pièces de récupération et diagnostic | Vérifier identité/pouvoir et résoudre incident ; sécurité/service | Intervenants nominatifs ; pas d'accès métier supplémentaire | Proposition : pièces justificatives détaillées supprimées 30 jours après résolution ; preuve minimale de contrôle suit journal sécurité ; litige isolé si nécessaire | Durée et preuve proportionnées à faire valider ; éviter de conserver copie d'identité complète si un constat suffit |
| Contrat et données administratives du service SMART AO | Gestion du service ; responsable contractuel SMART AO | Personnel de gestion habilité ; droits des personnes appropriés | Calendrier propre à la finalité et aux obligations du service, distinct de la suppression du dossier client | Rôles responsable de traitement/sous-traitant et durées à qualifier ; pas d'effacement automatique des factures par clôture d'Affaire |

Les sauvegardes ne sont pas une archive métier consultable : propagation des suppressions selon fenêtre maximale proposée de 90 jours ; après restauration, réappliquer les suppressions et révocations avant réouverture. Un gel pour litige porte catégorie, motif, autorité, date de revue et condition de sortie. Le calendrier accepté est visible par le client avant activation commerciale ; ces tableaux ne remplacent pas cette acceptation.

Exporter selon périmètre et droits : originaux admis, versions, métadonnées, pièces validées, exigences/liens de preuve, décisions, hypothèses, tâches ouvertes, prix autorisés, manifestes et reçus. Fournir index, dictionnaire des données, liste des éléments omis avec motif et vérification d'intégrité. Le destinataire doit pouvoir ouvrir et relier les données sans abonnement actif. Les secrets d'authentification et les données d'autres entreprises ne sont jamais exportés.

Export complet : Propriétaire habilité + autorité de divulgation appropriée aux catégories, step-up et destinataire contrôlé. L'intitulé « complet » ne contourne pas les droits Direction. Un export partiel porte ce nom. Une erreur de création ne doit jamais présenter un fichier tronqué comme complet.

Fermeture : demande habilitée → inventaire et éventuelle conservation légitime → export vérifié/remis, ou renonciation explicite documentée → gel → fenêtre de réversibilité → suppression active → extinction des copies/sous-traitants selon calendrier → preuve de clôture minimale. Aucune suppression globale pendant un export non résolu. L'opposition ou la suppression d'une donnée personnelle requiert examen de la finalité ; ne pas effacer automatiquement une preuve contractuelle à conserver, ni conserver indéfiniment au nom de l'audit.

Suspension de service, impayé, incident ou fin d'abonnement sont distingués : motif, état de lecture/export, contact et calendrier sont visibles. La politique commerciale précise l'accès de réversibilité ; aucune perte silencieuse de dossier à la veille d'une remise.

Informations client : catégories traitées, prestataires/sous-traitants, accès support, pays d'hébergement/traitement/support, finalités, réutilisation IA et changement matériel de flux. Pas de promesse « tout reste en France » fondée sur le seul environnement dédié. Retrait d'un usage IA ne supprime pas rétroactivement les preuves légitimes ; les futurs traitements concernés cessent.

## R15 — Travail simultané, notifications, mobile et incidents

Une modification enregistre son auteur et sa version de départ. Si elle est dépassée : comparaison des deux propositions, maintien des contributions et choix humain ; aucun « dernier enregistrement gagne » silencieux sur un objet validé. Rejouer une action dont la réponse réseau a été perdue vérifie d'abord si elle a abouti, afin d'éviter double décision ou double notification externe.

Échéance : valeur absolue, fuseau source, source/version, lot/phase, canal, responsable et date interne de sécurité. Une date incertaine reste incertaine. Si le RC et l'avis divergent, alerte et confirmation humaine ; aucun report inventé sur la base d'une attente réglementaire.[^6]

Notifications : centre produit comme état consultable ; email critique configurable, sans pièce ni secret, destinataire revérifié. Distinguer préparée, expédition confirmée, échec et prise en charge humaine ; email expédié n'est pas « lu ». Escalade au suppléant puis au Patron selon délai de l'affaire. Une défaillance d'email laisse l'alerte active dans le produit. Les doublons sont regroupés sans masquer une aggravation.

Mobile V1 conserve OWN-10 : visite, photos, notes, constats, tâches, consultation ciblée ; aucune promesse d'édition prix/Coffre hors ligne. Chaque élément porte local/en attente/synchronisé/échec. L'heure de capture et celle de synchronisation sont distinctes. Prévenir avant déconnexion/fermeture qui ferait perdre un brouillon local. Après révocation, aucune synchronisation de contenu autorisée ; une suppression à distance d'un fichier déjà extrait n'est pas garantie.

Incident : périmètre affecté, dernier état confirmé, risque sur l'échéance, fonctions restantes, contact, prochaine information prévue. Après restauration, afficher point de reprise réel et éléments potentiellement perdus ; rapprocher autorisations, partages et preuves externes avant de réafficher un succès. Proposition A08 : hors sinistre de service, tout brouillon indiqué « enregistré » est récupérable après expiration de session ou coupure réseau. Pour un sinistre de service déclaré, objectifs distincts de perte maximale de 1 heure et de rétablissement en 4 heures à confirmer avant engagement commercial ; cette exception doit être exposée dans le contrat de service, sans promettre simultanément une absence absolue de perte. Si non tenables, modifier explicitement la promesse avant lancement, pas le cahier technique seul.

Un registre d'incident permet au responsable client de qualifier les notifications nécessaires ; le support lui transmet les faits sans attendre un rapport complet. La notification à l'autorité relève de la qualification et de la responsabilité applicables, non d'un déclenchement IA automatique.[^23]

## R16 — Accessibilité, limites de service et recette de lancement

Conserver WCAG 2.2 AA ; utiliser RGAA 4.1.2 disponible au jour de l'audit avec contrôle complémentaire des critères WCAG 2.2 non couverts, puis revoir le référentiel lors de son évolution. L'assujettissement légal et les déclarations requises sont **à valider par spécialiste juridique** ; la cible produit volontaire ne dépend pas de cette conclusion.[^22]

Tous les chemins critiques : clavier seul, focus visible et retour correct après dialogue, libellés explicites, erreurs liées aux champs, état annoncé aux aides techniques, alternative au glisser-déposer, tableaux lisibles et statuts non fondés sur la couleur. Les données source inaccessibles gardent leur original ; un extrait accessible est identifié comme dérivé et potentiellement partiel.

Profil de qualification A04 proposé : dossier de 500 fichiers / 2 Go au total, 200 Mo par fichier, profondeur d'archives 3 ; au-delà, fractionnement guidé ou prise en charge accompagnée annoncée avant transfert. Cibles de première information : accusé de prise en charge visible immédiatement après réception confirmée ; statut consultable et annulation/reprise pendant analyse, aucune estimation de fin non fondée. Ces plafonds sont des propositions de promesse V1 à confronter aux deux pilotes, pas des choix d'infrastructure.

Recette : au moins un pilote entreprise générale et un pilote technique conformément à DEC-01 ; parcours candidature seule, offre multi-lots, privé minimal, rectificatif, incident et passation. Les 12 contrats E01–E12 et espaces S01/S02 sont parcourus avec représentants des rôles concernés. Prototype exigé avant gel technique conformément à OWN-12 ; cette mission livre les contrats, pas un prototype réalisé.

Zéro échec accepté sur confidentialité interentreprise/Direction, autorisation de mauvaise version, faux reçu, perte silencieuse et engagement critique non signalé dans les cas de qualification convenus. Mesurer séparément oublis, faux positifs et temps de traitement/revue ; aucun score moyen ne masque ces échecs. Une absence de pièce que l'IA ne repère pas doit pouvoir être découverte et traitée par le parcours manuel. Le protocole ne prouve pas une exhaustivité universelle.

RIA : qualification de SMART AO par fonctions et rôle de fournisseur/déployeur, information de l'utilisateur et formation adaptée. Aucun usage d'évaluation RH ou de décision autonome sur les salariés n'est inclus. Les obligations de transparence et leur portée sont **à valider par spécialiste juridique**, sans ajouter un marquage universel de tous les livrables sans examen.[^24]

## Matrice des 16 points de vue utilisateurs

Chaque ligne désigne un profil métier ; le titre de poste ne crée aucun droit automatique. « Jamais » signifie jamais du seul fait de ce profil ou hors habilitation explicite applicable ; les secrets d'authentification et données d'autres clients restent interdits à tous.

| Profil | Faire / voir | Ne doit jamais voir par défaut | Valider / seulement proposer | Escalade, erreur fréquente et remplacement |
|---|---|---|---|---|
| Patron / dirigeant | Priorités, risques, décisions et données Direction de ses Affaires | Affaires/client tiers ; secrets de connexion ; données RH sans finalité | Décisions P selon attribution ; propose les données dont il n'est pas expert | Risque juridique vers conseil ; confusion GO/P5 ; suppléant explicite, aucun contournement pour urgence |
| Responsable d'offre | Coordonne lots, checklist, sources, questions, candidature et paquet | Marge, plancher, achats sensibles, notes Direction | Valide préparation si habilité ; propose GO et dérogation | Alerte Patron sur retard/bloquant ; oublie un tour/lot ; transfert de dossier avec tâches et accès revus |
| Chargé d'études | Analyse CCTP/plans, exigences et mémoire de son périmètre | Prix d'achat/marges hors mandat, évaluation privée partenaire | Valide revue technique déléguée ; propose interprétation et engagement | Confond inférence/fait ; escalade contradiction au responsable ; remplaçant reçoit sources et inconnus |
| Métreur | Bordereaux, quantités, unités, correspondances et hypothèses | Marge globale et notes Direction sans droit | Valide quantités/rapprochement délégués ; propose prix et aléas | Erreur m²/ml, double compte ou DQE garanti ; remplaçant reprend version et couverture |
| Conducteur de travaux | Visite, faisabilité, moyens, contraintes et passation pertinente | Négociation privée Direction, RH non nécessaire | Valide avis d'exécution ; accuse réception/réserve passation ; ne signe pas P7 sans délégation | Promesse irréalisable → Patron ; autre conducteur désigné avec nouvelle prise en charge |
| Administratif | Identité société, DUME/DC, attestations, signataires autorisés, échéances | Marges, achats, RIB sauf mission explicite | Valide exactitude des champs délégués ; prépare déclarations à signer | Pièce expirée ou mauvais SIRET ; responsable offre/DAF ; liste des renouvellements transférée |
| DAF | Hypothèses coûts/trésorerie, garanties et RIB nécessaires selon droits | Affaires restreintes non attribuées, secrets de connexion | Valide revue financière ; propose P3, sauf délégation expresse | Confusion taux marge/marque, financement inconnu ; suppléance financière bornée |
| Achats | Devis de ses lots, exclusions, validités et comparatif | Offres concurrentes hors lot, marge globale, notes Patron | Valide comparaison déléguée ; propose fournisseur et renouvellement | Prix expiré/transport absent → métreur et Patron ; transfert des demandes non répondues |
| QSE | PGC, contraintes chantier, garanties techniques, preuves environnementales et habilitations nécessaires | Dossiers médicaux, salaires, marges | Valide analyse QSE dans son périmètre ; propose conditions | Promesse environnementale invérifiable ou risque amiante → responsable/Patron ; avis et preuves transmis |
| Responsable commercial | Radar, contacts liés à l'Affaire, calendrier et motifs communicables | Plancher, marge et évaluations Direction par défaut | Prépare P0/P1 ; décide seulement si délégation | Assimile attribution annoncée à contrat → responsable ; portefeuille et relances réaffectés |
| Fournisseur | Paquet reçu, demandes précises et ses propres réponses | Affaire globale, autres devis, marge, pièces d'autres fournisseurs | Confirme son offre sous ses propres pouvoirs ; aucune validation SMART AO interne | Mauvaise unité ou offre incomplète → achats ; nouveau contact doit recevoir nouveau droit |
| Sous-traitant | Prestations confiées, documents nécessaires et sa déclaration à compléter | Prix concurrents, marge titulaire, autres lots sans droit | Fournit preuves et engagement ; ne s'auto-déclare pas agréé | Assurance hors activité, rang inconnu → administratif/Patron ; remplacement de société = nouvelle revue |
| Cotraitant | Périmètre commun autorisé, son lot, mandats pertinents | Coûts/marges internes des autres membres | Valide ses éléments et pouvoirs ; propose changements communs | Mandat incomplet/solidarité → mandataire et Patron ; changement de membre exige revue de procédure |
| Conseil externe | Paquet de questions et pièces explicitement autorisées | Mémoire Entreprise complète, données non nécessaires | Émet un avis ; décision engageante reste interne | Avis sur ancienne version → responsable ; nouveau conseil nécessite nouveau partage |
| Administrateur logiciel client | Invitations, statuts, sécurité et métadonnées de gestion | Contenu sensible du seul fait du rôle, RIB, marges | Exécute droits approuvés ; propose élargissement | Auto-attribution → refus ; collègue administrateur distinct ou récupération contrôlée |
| Support SMART AO | Diagnostic minimal, incident et accès exceptionnel approuvé | Contenu client ordinaire, secrets métier hors mandat, facteurs secrets | Valide constat de service ; ne décide aucune porte ni pouvoir client | Mauvais environnement/périmètre → arrêt et incident ; relève nominative avec nouvelle habilitation |

## G. Recettes métier et cas qui cassent le produit

**Lecture** : situation → action → résultat observable. Toutes les traces contiennent auteur, date/heure, portée et version. Les colonnes précisent le périmètre bloqué, ce qui reste utilisable et la reprise. Priorité **critique** = recette de sécurité/probité de lancement ; **majeure** = parcours métier à qualifier. L'état de couverture se rapporte au socle v0.2, pas au code existant.

| ID / priorité / couverture v0.2 | Situation → action → résultat observable attendu | Acteur, blocage / utilisable, reprise et trace |
|---|---|---|
| G01 critique / partiel §14 | DCE annonce un plan absent → importer → liste « pièce annoncée absente », couverture de prix non prouvée | Responsable offre ; P3/P5 dépendantes bloquées, autres pièces lisibles ; obtenir plan ou traiter risque selon R05 ; référence annonce et nouvelle version |
| G02 critique / partiel §26 | Rectificatif à H−3 après P5 → l'ajouter → paquet précédent marqué à revalider, impacts visibles | Responsable + Patron ; nouvelle remise autorisée bloquée, historique disponible ; comparer et rejouer portes touchées ; chaîne d'invalidation |
| G03 critique / partiel §18 | RC et CCAP divergent sur pénalité → comparer → deux sources conservées, pas de priorité automatique universelle | Responsable/conseil ; validation critique bloquée, rédaction non concernée possible ; réponse/qualification motivée ; sources et avis |
| G04 majeure / partiel §19 | CCTP impose levage absent DPGF → rapprocher → facteur de coût sans couverture | Métreur/achats ; P3 à revoir, étude possible ; chiffrage ou hypothèse bornée Patron ; lien besoin/poste |
| G05 critique / incomplet §16 | Acheteur impose XLS historique → importer → conservation distincte de l'édition non qualifiée | Métreur ; promesse de fidélité et P5 si fichier requis non validé bloquées ; traitement externe autorisé puis comparaison ; original/dérivé |
| G06 critique / partiel §14 | Scan dont page délai illisible → analyser → page signalée non lue, aucune date inventée | Responsable ; échéance et remise non validables, pages lisibles utilisables ; demander copie/lecture humaine prouvée ; page et décision |
| G07 majeure / incomplet §14 | Fichier protégé → ouvrir → limitation explicite sans contournement | Déposant ; seul traitement dépendant bloqué ; copie autorisée ou revue externe ; motif et version de remplacement |
| G08 critique / incomplet §14 | Archive dépasse profondeur/volume admis → importer → limite et éléments non traités visibles | Déposant ; éléments risqués isolés, autres reçus conservés ; fractionner puis reprendre ; inventaire des deux imports |
| G09 critique / incomplet §14/31 | Pièce contient contenu actif dangereux → demander aperçu → aucun contenu exécuté ni transmis à l'IA | Responsable + sécurité ; pièce isolée, Affaire restante disponible ; remplacement contrôlé ; événement de quarantaine sans secret |
| G10 critique / partiel §33 | Visite obligatoire échue sans attestation → préparer remise → blocage avec source et responsable | Responsable ; P5 bloquée, dossier conservé ; preuve/dispense réelle ou abandon ; pas de fausse attestation |
| G11 critique / partiel §33 | Date avis et RC diffèrent → proposer nouveau délai → état conflit et ancienne échéance visible | Responsable ; aucun report automatique, tâches conservées ; confirmation source acheteur ; historique des dates |
| G12 majeure / partiel §20 | Prix fournisseur expire avant validité d'offre → contrôler → alerte datée et impact scénario | Achats/Patron ; P3 réexaminée, autre préparation possible ; renouveler/substituer/risque borné ; offre et arbitrage |
| G13 majeure / partiel §32 | Responsable absent J−2 → réaffecter → suppléant voit tâches, inconnus, validations attendues | Patron/administratif habilité ; pas de perte, pas de transfert automatique de pouvoir ; acceptation relève ; ancien/nouveau responsable |
| G14 critique / partiel §8.4 | Salarié part avec session active → désactiver → accès, partage futur et publication IA refusés | Admin habilité ; autres utilisateurs continuent ; réaffecter sans supprimer décisions historiques ; révocation et tâches orphelines |
| G15 critique / partiel §7 | Patron absent sans délégation → collaborateur clique P5 → refus explicite, aucun pouvoir acquis | Responsable ; P5 bloquée, préparation/export brouillon autorisé selon droits ; délégataire existant ou récupération légitime ; tentative tracée |
| G16 critique / partiel §32 | Deux personnes modifient même exigence → enregistrer → conflit visible et deux contributions conservées | Contributeurs ; validation de version divergente bloquée, lecture disponible ; choix/revue ; propositions et résolution |
| G17 critique / incomplet §7.4 | Admin se donne rôle Patron puis exporte marge → action → élévation refusée sans approbation habilitée | Admin/Propriétaire ; mutation bloquée, administration ordinaire disponible ; demande à autorité compétente ; approbation/refus |
| G18 critique / contradiction OWN-01 proposée | Seul Propriétaire compromis → suspendre → tous ses accès cessent malgré absence d'autre actif | Support sécurité ; dépend de l'exception A02 non encore acceptée ; récupération pouvoirs contrôlée, aucune auto-P5 ; preuve incident et restauration |
| G19 critique / incomplet §9 | MFA perdu → demander récupération → aucun accès fondé sur seul email ; nouveaux facteurs après contrôle | Utilisateur/Propriétaire ou support exceptionnel ; compte bloqué, collègues actifs ; révocation anciens facteurs ; journal sans secrets |
| G20 critique / partiel §9 | Session expire pendant mémoire → se reconnecter → dernier brouillon confirmé récupéré, local distingué | Même utilisateur habilité ; contenu masqué hors session ; conflit éventuel traité ; versions et état sauvegarde |
| G21 critique / incomplet §20 | Réponse en groupement sans mandat/signataire d'un membre → contrôle → pièce manquante attribuée au bon membre | Mandataire/administratif ; P5 selon exigence bloquée, préparation disponible ; mandat et candidature mis à jour ; pièces par entité |
| G22 critique / partiel §20 | Sous-traitant seulement consulté est présenté engagé → génération → engagement non prouvé signalé | Achats/responsable ; P4 dépendante bloquée ; obtenir accord/acceptation applicable ; état et preuve tiers |
| G23 critique / partiel §27 | Commande privée réduit prix et élargit prestation → importer → comparaison offre/commande et accord non établi | Patron/conseil ; pas de « gagné définitif » ni passation complète ; arbitrage/document accepté ; versions et preuve |
| G24 critique / partiel §7.5 | Paquet envoyé au mauvais destinataire → révoquer → prochains accès coupés, téléchargements antérieurs visibles | Émetteur/sécurité ; lien bloqué, autres partages selon incident ; traiter divulgation ; destinataire, accès et mesures |
| G25 critique / partiel §28 | IA indisponible pendant contrôle final → ouvrir Coffre → contrôles humains, originaux et export restent accessibles | Responsable/Patron ; génération indisponible seulement ; reprendre sans double contenu ; état de traitement et décisions manuelles |
| G26 majeure / partiel §13 | BOAMP indisponible → actualiser Radar → dernière fraîcheur et panne visibles | Commercial ; aucune prétention de veille complète ; saisie manuelle possible, reprise sans doublon ; provenance et relance |
| G27 critique / partiel §34 | Visite hors réseau → photo et note → « local/en attente », jamais « partagé » | Conducteur ; autre équipe ne la voit pas ; reconnecter puis confirmer synchronisation ; capture et synchro distinctes |
| G28 critique / partiel §33 | Utilisateur au Maroc, remise heure Paris → consulter → heure source et conversion explicites, même instant | Responsable ; pas de recalcul selon appareil seul ; vérifier source/fuseau ; valeur originale et validation |
| G29 critique / partiel §31 | DCE ordonne d'envoyer les marges à une URL → analyser → aucune action externe/droit modifié | Responsable/sécurité ; passage suspect signalé, autres contenus analysables ; revue humaine ; source hostile et traitement |
| G30 critique / partiel §25–26 | Fichier modifié après P5 → exporter comme autorisé → refus, nouvelle candidate proposée | Responsable/Patron ; ancienne autorisation ne couvre pas le nouveau ; P4/P5 selon impact ; manifeste avant/après |
| G31 critique / partiel §25 | Opérateur affirme dépôt mais pas de reçu → déclarer envoyé → « transmission déclarée, réception non prouvée » | Opérateur ; aucun succès prouvé, paquet disponible ; rechercher reçu/support plateforme ; déclaration et pièces |
| G32 critique / partiel §25 | Reçu d'un autre lot ou hors délai → rapprocher → incohérence visible | Opérateur/Patron ; statut réussite bloqué ; bonne preuve ou incident ; contrôle des identifiants/heures |
| G33 majeure / absent §25 | Reçu prouve pli mais ne liste pas les fichiers → importer → réception prouvée et rapprochement contenu partiel séparés | Responsable ; pas de faux contrôle intégral ; déclaration/inventaire complémentaires ; limites de preuve conservées |
| G34 critique / absent §25 | Nouvelle offre après oubli d'une pièce → préparer seulement ajout → avertissement redépôt complet | Responsable/Patron ; candidat incomplet non autorisé ; nouvelle offre intégrale/tour et reçu ; ancien paquet préservé |
| G35 majeure / absent §25 | Copie de sauvegarde préparée → enregistrer → état propre, aucun remplacement automatique du dépôt principal | Opérateur ; conditions de canal/délai contrôlées ; compléter preuve ; manifeste et reçu séparés |
| G36 critique / partiel §24 | Marché gagné promet intervention sous 2 h mais passation omet engagement → clore → blocage | Conducteur/Patron ; autres pièces disponibles ; affecter moyens/risque et accuser prise en charge ; engagement relié à P7 |
| G37 critique / absent §6 | Procédure candidature seule sans prix → préparer paquet → candidature possible sans chiffrage exigé artificiellement | Administratif/responsable ; P3 non applicable motivée, P4/P5 de phase requises ; invitation offre ouvre phase suivante ; décisions par phase |
| G38 critique / incomplet §5 | Deux lots remis, un seul gagné → résultat → seul lot gagné part en passation | Responsable ; pas de prix/engagement fusionné ; notifier autre résultat ensuite ; preuves par lot |
| G39 critique / incomplet §21 | Vente 120, coûts 100 puis coût inconnu → calculer → 20 et 16,67 % sur vente, puis indicateur incomplet | DAF ; feu vert automatique interdit ; compléter/borner hypothèse ; composition du coût et formule |
| G40 critique / incomplet §21 | Somme Excel repose sur valeur non recalculée/ligne masquée → importer → total à vérifier | Métreur ; P3/P4 si critique bloquées ; recalcul externe et comparaison ; fichier original et résultat vérifié |
| G41 majeure / incomplet §21 | Même équipe engagée sur deux périodes incompatibles → P3 → conflit de disponibilité | Conducteur/Patron ; capacité non démontrée, autres études disponibles ; alternative/preuve/arbitrage ; source de disponibilité |
| G42 critique / incomplet §21 | Approvisionnement à payer avant premier acompte, trésorerie absente → synthèse → financement non démontré | DAF/Patron ; pas de feu vert financier ; hypothèses d'échéancier et financement revus ; scénario daté |
| G43 critique / incomplet §5.2 | Assurance courante mais activité non couverte → réemployer → ne passe pas « applicable » | Administratif/QSE ; validation dépendante bloquée ; assureur/équivalence pertinente ; pièce, périmètre et avis |
| G44 critique / partiel §5.2 | CV contient salaire/donnée de santé → joindre à réponse → avertissement et version minimisée à revoir | Administratif habilité ; partage sensible bloqué ; dérivé autorisé ; original restreint et validation |
| G45 critique / incomplet §38 | Propriétaire sans droit Direction lance export complet → demande → périmètre et approbation Direction exigés | Propriétaire/Patron ; export sensible bloqué, export autorisé possible ; nouvelle autorisation ; contenu et bénéficiaire |
| G46 critique / incomplet §37 | Support autorisé une heure consulte après échéance → accès → refus | Support/client ; diagnostic minimal possible ; nouvelle demande justifiée ; journal d'accès/expiration |
| G47 critique / incomplet §38 | Fermeture avec export interrompu ou litige → supprimer → état bloqué et motif visible | Propriétaire/responsable données ; récupération/export possible selon droits ; résoudre export/conservation ; calendrier et certificat final |
| G48 critique / incomplet §38 | Restauration réintroduirait utilisateur révoqué ou donnée supprimée → reprendre → contrôle avant réouverture | Exploitation ; accès affectés suspendus, données sûres selon état ; réappliquer révocations/purge légitime ; rapport de reprise |
| G49 critique / partiel §40 | Utilisateur au clavier autorise une version → parcours → preuve, avertissement et confirmation accessibles | Patron ; aucun geste souris obligatoire ; correction focus/libellé ; compte rendu de recette accessible |
| G50 majeure / incomplet §19 | RC impose critère environnemental et mémoire générique → contrôler → critère sans réponse/preuve signalé | QSE/responsable ; P4 selon criticité bloquée ; réponse spécifique et preuve ; source/version, aucune note prédite |
| G51 critique / incomplet §22 | GO sous condition échue ou deux Patrons décident simultanément → P5 → condition ouverte/conflit bloque | Patron/délégataire ; préparations conservées ; levée prouvée ou remplacement motivé ; décisions historisées |
| G52 critique / partiel §7/28 | Collaborateur demande à l'IA marge via total/coûts ou consulte ancienne réponse après révocation → lecture → aucune divulgation directe ou déductible par les sorties fournies | Responsable sécurité ; fonctions autorisées continuent ; ajuster droits ou corriger dérivé ; refus sans exposer le secret |


---

# 56. Contrats fonctionnels proposés

## E. Portée et invariants communs

Proposition v0.3 à valider par le propriétaire, à utiliser ensuite pour le prototypage. Les 12 écrans de OWN-12 sont conservés. Ce document ne constitue ni une maquette graphique, ni une spécification d'architecture, ni une recette déjà exécutée. Référence des règles : R01–R16 dans `02_REGLES_ROLES_ET_RECETTES.md` ; référence des essais : G01–G52 du même fichier.

**C00 — applicable à tous les écrans** : l'identité de l'entreprise active et le périmètre sont visibles ; droits appliqués avant recherche/affichage/calcul IA/export, pas seulement au bouton ; aucune donnée d'une autre entreprise. Une information porte son état de preuve et sa version. Une action non aboutie n'est pas présentée comme réussie. Les brouillons confirmés sont récupérables après reconnexion ; un conflit conserve les deux contributions. Une alerte persistante critique ne disparaît pas avec la fermeture d'une notification. Toute décision engageante garde auteur habilité, portée, heure, contexte et motif.

**Accessibilité commune A11Y** : clavier, ordre de focus cohérent, libellés et erreurs associés, annonces de progression non envahissantes, contraste et zoom/reflow, alternative textuelle aux graphiques et au glisser-déposer, absence de dépendance à la couleur. Cible WCAG 2.2 AA avec référentiel français courant et complément explicite ; voir R16.[^22]

**États distincts** : « vide » = absence réelle de donnée dans un périmètre autorisé ; « non accessible » = droits insuffisants sans fuite de contenu ; « partiel » = données disponibles avec exclusions ; « erreur » = échec identifié ; « bloqué » = action interdite et voie de sortie indiquée. Chaque écran expose ces états, sans remplacer un résultat inconnu par zéro.

## E01 — Accueil Patron

| Champ | Contrat |
|---|---|
| Rôles | Patron principal ; vue « Mon travail » du responsable/expert limitée à ses tâches, sans synthèse Direction. |
| Question métier | Quelles décisions ou échéances exigent mon attention aujourd'hui ? |
| Données indispensables | Affaires autorisées, responsables, délais absolus, portes ouvertes, rectificatifs, conditions GO, preuves expirantes, incidents et fraîcheur. |
| Information prioritaire | Échéance menaçante et blocage critique, avant volume d'affaires ou production IA. |
| Action principale | Ouvrir la décision ou le blocage prioritaire dans son contexte exact. |
| Actions secondaires | Filtrer par responsable/période, affecter une action, consulter source, ouvrir suppléance. |
| Décisions autorisées | Prise en charge/affectation ; décision P renvoyée au contrat E08/E11, jamais validation en masse aveugle. |
| Informations masquées | Affaires restreintes hors portée, chiffres Direction de la vue collaborateur ; aucun agrégat permettant leur déduction. |
| Source / preuve | Chaque alerte ouvre l'événement, la pièce/version ou la condition dont elle dépend. |
| État vide | « Aucune Affaire accessible / aucune action dans ce filtre », avec création ou vue sans filtre si autorisée. |
| État normal | Alertes triées avec date source, responsable et prochaine action ; trois dimensions Temps, Préparation prouvée, Risque sans score opaque. |
| Traitement en cours | Dernier état confirmé visible, période de calcul annoncée ; aucune validation créée par le rafraîchissement. |
| Résultat partiel | Liste des sources ou Affaires non actualisées, sans les faire passer pour sans risque. |
| Erreur | Message par bloc indisponible et dernière actualisation ; les autres blocs restent lisibles. |
| Blocage critique | P5 invalide ou absence de décideur affichée avec chemin vers traitement, jamais masquée par filtre personnel par défaut. |
| Reprise | Réactualisation ciblée ; prise en charge conservée, doublons regroupés et aggravations visibles. |
| Action IA | Briefing sourcé des états existants, proposition de priorités ; aucun risque ou fait nouvellement « validé ». |
| IA indisponible | Même liste de faits, échéances et actions, sans briefing rédigé. |
| Mobile | Consultation des alertes et tâches ; décision sensible renvoie vers parcours explicitement pris en charge, pas un bouton aveugle. |
| Accessibilité | A11Y ; alertes en texte, trois dimensions lisibles sans graphique ; pas de compte à rebours seul. |

**Acceptation** : E01-A, un rectificatif invalidant P5 apparaît avec Affaire/lot/version et source ; E01-B, un expert ne peut obtenir ni montant ni nombre d'Affaires interdites ; E01-C, panne IA et email ne retirent aucune alerte factuelle. Recettes G02, G25, G52.

## E02 — Radar

| Champ | Contrat |
|---|---|
| Rôles | Commercial, responsable d'offre, Patron et délégataire P0. |
| Question métier | Quelles opportunités publiées dans la source surveillée correspondent à notre recherche ? |
| Données indispensables | Avis BOAMP, référence, acheteur, objet, localisation, lots disponibles, date de publication/modification, délais, URL, critères de filtre et dernière collecte réussie. |
| Information prioritaire | Pertinence explicable et délai utile, avec limites de couverture de la veille. |
| Action principale | Ouvrir une opportunité à qualifier. |
| Actions secondaires | Rechercher, filtrer, sauvegarder recherche, suivre, écarter avec motif, saisir une invitation manuelle. |
| Décisions autorisées | P0 uniquement par habilité ; le classement ne décide pas GO/NO-GO. |
| Informations masquées | Motifs commerciaux restreints et références à Affaires non autorisées. |
| Source / preuve | Avis BOAMP et version/date collectée ; la publication d'un avis n'est pas la réception du DCE. |
| État vide | Aucun résultat pour critères/date/source affichés ; proposer élargissement sans supprimer silencieusement les filtres. |
| État normal | Résultats explicables, lien source, suivi, doublons/avis liés regroupés sans perte de version. |
| Traitement en cours | Recherche/collecte en cours et portée ; résultats déjà acquis conservés. |
| Résultat partiel | Source ou période non couverte ; total connu distinct du total inconnu. |
| Erreur | Panne BOAMP explicite, dernier succès daté, saisie manuelle disponible. |
| Blocage critique | Conversion d'une opportunité annulée ou périmée exige avertissement et confirmation de son état ; pas d'Affaire active créée silencieusement. |
| Reprise | Nouvelle collecte puis rapprochement des références, aucun doublon d'Affaire au double clic. |
| Action IA | Expliquer correspondance métier/territoire, proposer critères ; ne supprime pas un résultat seul. |
| IA indisponible | Recherche par champs et filtres déterminés, consultation de l'avis. |
| Mobile | Liste courte et suivi ; paramétrage approfondi sur poste d'étude. |
| Accessibilité | A11Y ; libellés de filtres, indication de résultats actualisés et navigation clavier. |

**Acceptation** : E02-A, panne affiche date du dernier succès et ne dit pas « à jour » ; E02-B, chaque résultat explique ses critères ; E02-C, répéter conversion ne crée pas deux dossiers. BOAMP seul en V1, TED V1.x.[^25] G26.

## E03 — Fiche Opportunité

| Champ | Contrat |
|---|---|
| Rôles | Commercial/responsable préparent ; Patron ou délégataire P0/P1 décide. |
| Question métier | Devons-nous investir du temps dans cette consultation et sur quels lots ? |
| Données indispensables | Identité candidate, source/invitation, client/acheteur, procédure et phase, lots visés, dates, première éligibilité, responsable, charge d'étude estimée et inconnus. |
| Information prioritaire | Périmètre, date limite, incompatibilité connue, prochaine action. |
| Action principale | Soumettre ou décider l'ouverture P1. |
| Actions secondaires | Joindre invitation, modifier périmètre préparatoire, affecter responsable, suivre, écarter avec motif. |
| Décisions autorisées | Cibler et ouvrir selon habilitation ; aucun GO économique ou engagement commercial externe implicite. |
| Informations masquées | Motifs privés Direction, enveloppes financières ou notes non autorisées. |
| Source / preuve | Avis/invitation et document fixant les dates ; chaque saisie manuelle est attribuée. |
| État vide | Formulaire minimal public/privé avec inconnus permis et exemple anonymisé séparé des dossiers réels. |
| État normal | Qualification et décision courante, prochaine action, lien vers Affaire liée. |
| Traitement en cours | Import de l'invitation ou recherche de doublon, sans création définitive prématurée. |
| Résultat partiel | Acheteur/phase/lot/date manquants identifiés ; dossier préparatoire permis, remise non prête. |
| Erreur | Échec de conversion sans perte de pièces ni fausse confirmation. |
| Blocage critique | Entreprise candidate/périmètre non identifié ou décideur absent interdit la décision dépendante. |
| Reprise | Retrouver la conversion déjà aboutie ou recommencer depuis les données conservées. |
| Action IA | Proposer champs et questions de qualification, à confirmer. |
| IA indisponible | Saisie manuelle et consultation directe des pièces. |
| Mobile | Consultation, note et suivi ; ouverture simple possible si champs et preuve visibles. |
| Accessibilité | A11Y ; aucun champ obligatoire caché, erreurs regroupées et liées. |

**Acceptation** : E03-A, invitation privée peut créer un dossier sans BOAMP ; E03-B, candidature seule ne réclame pas une offre de prix ; E03-C, NO-GO conserve motif/historique et réouverture explicite. G23, G37.

## E04 — Import DCE

| Champ | Contrat |
|---|---|
| Rôles | Responsable et contributeur autorisé ; tiers via paquet de dépôt limité distinct. |
| Question métier | Qu'avons-nous reçu et quelle part peut réellement être étudiée ? |
| Données indispensables | Origine/date/canal, version reçue, fichiers/archives, formats, tailles, état de contrôle, périmètre lot/phase et profil de prise en charge. |
| Information prioritaire | Pièces non reçues/non lues et anomalies, avant la synthèse générée. |
| Action principale | Importer puis vérifier l'inventaire de réception. |
| Actions secondaires | Fournir complément, relier rectificatif, expliquer doublon, annuler/reprendre traitement, demander copie autorisée. |
| Décisions autorisées | Confirmer inventaire/source/version ; pas certifier conformité globale ou absence de danger par clic. |
| Informations masquées | Pièces hors habilitation et contenu en quarantaine ; tiers ne voit que ses dépôts. |
| Source / preuve | Originaux et provenance conservés ; chaque dérivé est relié à l'original. |
| État vide | Formats/limites affichés avant transfert, sélection fichier accessible sans glisser-déposer. |
| État normal | Inventaire confirmé, reçus/analysables/non lus distincts et prochaines actions. |
| Traitement en cours | Progression par réception/contrôle/lecture, annulation sûre ; aucune mention « analyse terminée » prématurée. |
| Résultat partiel | Pages, feuilles, archives ou pièces non traitées nommées ; autres résultats accessibles. |
| Erreur | Motif exploitable par fichier et état de réception réel ; travail antérieur conservé. |
| Blocage critique | Contenu dangereux isolé ; exigences critiques dépendantes non validables. |
| Reprise | Reprendre éléments en échec sans redoubler les pièces confirmées ; remplacement versionné. |
| Action IA | Classement et suggestions de pièces annoncées absentes, explicitement révisables. |
| IA indisponible | Inventaire, contrôle des fichiers et classement/revue manuels ; extraction IA différée. |
| Mobile | Photos/constats de visite, pas import massif garanti en réseau dégradé. |
| Accessibilité | A11Y ; progression annoncée, sélection alternative, liste textuelle des erreurs. |

**Acceptation** : E04-A, un fichier illisible empêche le libellé « dossier entièrement lu » ; E04-B, archive limitée expose les éléments exclus ; E04-C, document hostile n'exécute aucune action. G01, G05–G09, G29.

## E05 — Explorateur DCE

| Champ | Contrat |
|---|---|
| Rôles | Responsable, chargé d'études, métreur, QSE et autres experts sur périmètre. |
| Question métier | Où se trouve l'information qui fonde cette exigence, et quelle version s'applique ? |
| Données indispensables | Arborescence, versions, lots, type de pièce, couverture de lecture, recherche, extrait localisé et exigences liées. |
| Information prioritaire | Version consultée et limitation de lecture ; alerte si version dépassée. |
| Action principale | Ouvrir une source et créer/contrôler l'exigence reliée. |
| Actions secondaires | Rechercher, comparer versions, annoter, signaler contradiction/manque, télécharger original admis. |
| Décisions autorisées | Validation de lecture/extraction par habilité ; aucune résolution juridique automatique. |
| Informations masquées | Documents, titres, extraits et résultats de recherche interdits par droits. |
| Source / preuve | Page ou feuille/cellule, contexte et fichier exact ; lien indisponible signalé. |
| État vide | Aucun document reçu : lien E04 ; recherche vide distincte de contenu non lu. |
| État normal | Liste et extrait, portée des résultats, accès à la version courante et historique. |
| Traitement en cours | Documents en lecture identifiés, recherche limitée aux contenus disponibles. |
| Résultat partiel | Extrait disponible mais tableau/plan non exploitable ; conclusion interdite sur cette portion. |
| Erreur | Aperçu impossible : original contrôlé téléchargeable si droit, message de limitation. |
| Blocage critique | Source absente ou nouvelle version non revue empêche validation des conclusions dépendantes. |
| Reprise | Réimporter/relocaliser avec contrôle humain, sans remapper silencieusement une citation historique. |
| Action IA | Extraire/expliquer passage, proposer liens et contradictions avec références. |
| IA indisponible | Navigation, recherche disponible hors conversation, annotations et liens manuels. |
| Mobile | Lecture ciblée, photo/annotation ; tableau large accessible sans prétendre remplacer le poste d'étude. |
| Accessibilité | A11Y ; extrait textuel accessible identifié comme dérivé ; alternative à sélection visuelle d'une zone. |

**Acceptation** : E05-A, toute exigence critique ouvre sa version exacte ; E05-B, pas de résultat pour une pièce interdite ; E05-C, même nom de fichier nouveau conserve l'ancien. G03, G06, G52.

## E06 — Synthèse Affaire

| Champ | Contrat |
|---|---|
| Rôles | Responsable principal ; Patron et experts avec vues adaptées. |
| Question métier | Où en est cette réponse, quels obstacles restent et qui agit ? |
| Données indispensables | Périmètre/phase/tour, délais, décideurs, couvertures, visite/questions, tâches, décisions, prix autorisé, rectificatifs, résultat et état de remise. |
| Information prioritaire | Blocage courant et prochaine porte applicable, non un pourcentage global. |
| Action principale | Traiter ou affecter l'obstacle qui empêche l'étape suivante. |
| Actions secondaires | Ouvrir registres, partenaires, échéances, journal, réponse, résultat/REX et passation. |
| Décisions autorisées | Affectation et proposition ; P via contrat dédié, enregistrement du résultat externe selon habilitation. |
| Informations masquées | Montants Direction et notes privées ; état « revue financière requise » ne donne pas le plancher. |
| Source / preuve | Provenance de chaque état, pièces de résultat par lot, journal des changements. |
| État vide | Affaire ouverte avec checklist guidée et informations minimales manquantes. |
| État normal | Lots et phases distincts, chemin de réponse, risques et tâches responsables. |
| Traitement en cours | Analyse ou rapprochement en cours ; état confirmé précédent conservé. |
| Résultat partiel | Réponse prête pour certains lots seulement, ou résultat gagné sur un seul lot. |
| Erreur | Bloc indisponible localisé, actions non dépendantes utilisables. |
| Blocage critique | Pas de responsable/décideur, échéance contradictoire ou porte invalidée empêche progression correspondante. |
| Reprise | Réaffectation ou actualisation ciblée, sans effacer les décisions. |
| Action IA | Synthèse factuelle et suggestion de prochaine action, avec état de preuve. |
| IA indisponible | Tableaux structurés, checklists et actions manuelles. |
| Mobile | Mon travail, visite, notes et statuts de synchronisation ; pas modification économique complexe. |
| Accessibilité | A11Y ; étapes textuelles, lecture par lot, aucun diagramme seul. |

**Acceptation** : E06-A, phase candidature seule suivie d'offre garde deux échéances ; E06-B, résultat partiel ne passe pas toute l'Affaire en gagné ; E06-C, changement responsable conserve toutes les actions ouvertes. G13, G37, G38.

## E07 — Registre MIRP

| Champ | Contrat |
|---|---|
| Rôles | Études, métreur, QSE, responsable ; Patron pour acceptation critique. |
| Question métier | Qu'est-ce qui manque pour défendre notre prix et notre décision ? |
| Données indispensables | Inconnus/contradictions/hypothèses, source, lot, impact coût/délai/capacité, responsable, action, échéance, criticité et porte dépendante. |
| Information prioritaire | Inconnus qui empêchent P3/P5 et contradictions non résolues. |
| Action principale | Traiter un point par preuve, question, visite ou hypothèse bornée soumise. |
| Actions secondaires | Affecter, regrouper doublons avec liens, filtrer, consulter prix, historique et dépendances. |
| Décisions autorisées | Expert valide sa revue ; Patron/délégataire accepte risque/hypothèse critique selon R05. |
| Informations masquées | Montant de provision ou exposition Direction ; avis expert utile sans révélation du scénario global. |
| Source / preuve | Sources opposées pour contradiction ; origine et validateur pour hypothèse ; absence explicitée pour inconnu. |
| État vide | « Aucun point enregistré », jamais « aucun risque » si couverture non terminée. |
| État normal | Chaque ligne possède propriétaire et prochaine action ; état ouvert/traité/accepté sous condition/supersédé. |
| Traitement en cours | Propositions d'analyse distinctes du registre validé. |
| Résultat partiel | Impact connu qualitativement, montant non estimé ; pas de zéro implicite. |
| Erreur | Échec d'analyse/citation ; édition manuelle possible si droits. |
| Blocage critique | Condition dépassée ou source manquante laisse porte concernée bloquée. |
| Reprise | Nouvelle preuve ou décision remplace le traitement courant en gardant l'historique. |
| Action IA | Propose point, impact et question ; aucune clôture ou acceptation autonome. |
| IA indisponible | Création, lien documentaire, affectation et décision manuels. |
| Mobile | Constats et preuves de visite enrichissent les points après synchronisation confirmée. |
| Accessibilité | A11Y ; filtres clavier, criticité en texte, colonnes masquables sans perdre les blocages. |

**Acceptation** : E07-A, « hypothèse acceptée » reste différente de « fait prouvé » ; E07-B, condition échue rouvre la porte ; E07-C, ajout pièce déclenche revue des points dépendants. G01–G04, G51.

## E08 — Décision GO/NO-GO

| Champ | Contrat |
|---|---|
| Rôles | Patron/délégataire P2/P3 principalement ; responsable prépare, experts apportent avis. |
| Question métier | Autorisons-nous cette étape, sur quel périmètre et sous quelles conditions ? |
| Données indispensables | Porte, lots/phase/version, faits, inconnus, scénarios autorisés, risques, capacité, trésorerie, conditions et habilitation du décideur. |
| Information prioritaire | Motif décisif et risques non levés, séparés des bénéfices attendus. |
| Action principale | Enregistrer GO, GO sous conditions, ATTENTE, NO-GO ou ABANDON motivé. |
| Actions secondaires | Demander complément, consulter preuves, inviter avis, désigner revue, superséder décision antérieure. |
| Décisions autorisées | Uniquement portes/périmètres délégués ; P5 exige le Coffre exact et son step-up. |
| Informations masquées | Avis Direction et scénarios financiers pour contributeurs non habilités ; résultat communicable séparé du motif privé. |
| Source / preuve | Dossier de décision figé avec sources/version et liste explicite des inconnus acceptés. |
| État vide | Dossier non soumis, informations à rassembler et prochain responsable. |
| État normal | Décision actuelle et historique, conditions, responsables et dates de revue. |
| Traitement en cours | Préparation de synthèse ou enregistrement : attendre confirmation avant statut validé. |
| Résultat partiel | Avis manquant, capacité/trésorerie non démontrée ; arbitrage borné seulement selon R05. |
| Erreur | Échec d'enregistrement : décision non confirmée ; rechercher opération avant répétition. |
| Blocage critique | Délégation expirée, version modifiée ou classe B0/B1 applicable non résolue. |
| Reprise | Rafraîchir dossier puis confirmer nouvelle décision ; pas de recyclage automatique du clic initial. |
| Action IA | Expose arguments sourcés et limites ; aucun score final décisionnaire. |
| IA indisponible | Même dossier structuré et décision humaine possible. |
| Mobile | Consultation ; décision seulement dans un parcours qualifié montrant contexte complet, jamais hors ligne. |
| Accessibilité | A11Y ; choix explicites, récapitulatif de portée, confirmation sans minuterie arbitrairement courte. |

**Acceptation** : E08-A, GO sous conditions exige action/preuve de levée/échéance ; E08-B, deux Patrons concurrents ne s'écrasent pas ; E08-C, rôle administrateur ne permet pas de décider. G15, G17, G39, G51.

## E09 — Prix

| Champ | Contrat |
|---|---|
| Rôles | Métreur/études sur couverture ; achats sur devis autorisés ; DAF/Patron sur scénarios sensibles. |
| Question métier | Le chiffrage couvre-t-il le besoin et quelles hypothèses exposent notre contribution et notre financement ? |
| Données indispensables | Bordereau/version, HT/TTC/monnaie/unités, quantités, postes, hypothèses, facteurs non couverts, devis/validités, variante/tranche, coûts et droits, capacité/trésorerie minimales. |
| Information prioritaire | Besoin non couvert, total non fiable ou hypothèse critique ; montant final seulement dans son périmètre. |
| Action principale | Revoir les écarts du chiffrage importé et soumettre le scénario à P3. |
| Actions secondaires | Importer/exporter, lier postes/exigences, consulter devis, saisir scénario borné, comparer variantes séparément. |
| Décisions autorisées | Expert valide rapprochement/quantité ; DAF revue ; Patron ou délégataire accepte scénario. Aucun prix final IA. |
| Informations masquées | Prix achat sensibles, plancher, marge, trésorerie et provisions Direction selon droits ; prévention des déductions par agrégats. |
| Source / preuve | Cellule/ligne du fichier original, offre fournisseur, source exigence et composition du coût. |
| État vide | Profil de formats accepté et import de chiffrage ; pas de tarif universel suggéré. |
| État normal | Couverture et totaux par lot/scénario, formule des indicateurs explicitée. |
| Traitement en cours | Contrôle/import en cours, aucun remplacement de version active avant confirmation. |
| Résultat partiel | Lignes non reconnues, formule non recalculée, coût inconnu ou trésorerie non démontrée. |
| Erreur | Erreur d'unité/structure, précision et emplacement ; original disponible pour correction externe. |
| Blocage critique | P3/P4 dépendantes non validables en cas de total indéterminé, mauvaise version ou risque non traité. |
| Reprise | Corriger mapping ou fichier externe, réimporter, comparer et réexaminer scénario ; aucun double comptage. |
| Action IA | Suggère correspondances et coûts oubliés, ne fabrique ni devis ni quantités vérifiées. |
| IA indisponible | Saisie/mapping/revue et calculs définis restent accessibles ; rapprochement automatique différé. |
| Mobile | Lecture autorisée de synthèse seulement ; travail complet sur poste d'étude. |
| Accessibilité | A11Y ; en-têtes de tableaux, accès clavier par ligne, unités verbalisées et écarts textuels. |

**Acceptation** : E09-A, exemple 120/100 restitue correctement taux sur vente ; E09-B, coût absent ne vaut pas zéro ; E09-C, même équipe occupée et prix expiré apparaissent dans revue P3. G04, G12, G39–G42, G52.

## E10 — Réponse

| Champ | Contrat |
|---|---|
| Rôles | Responsable, administratif, rédacteur/études, QSE ; valideurs par section et Patron P4. |
| Question métier | Avons-nous répondu à chaque exigence de cette phase sans promesse non maîtrisée ? |
| Données indispensables | Checklist candidature/offre par lot, critères/sous-critères, modèle imposé, pièces à produire/obtenir, versions, faits Entreprise, engagements, responsables et statut de revue. |
| Information prioritaire | Pièce/section critique manquante, preuve expirée, engagement nouveau ou dépassement des contraintes acheteur. |
| Action principale | Compléter puis soumettre la réponse en revue de contenu P4. |
| Actions secondaires | Réemployer version validée, télécharger modèle/copie, réimporter, comparer, affecter section, préparer question/partage ciblé. |
| Décisions autorisées | Validation de section déléguée ; déclarations/engagements et P4 par autorité adaptée. |
| Informations masquées | Notes Direction, coûts/marges et données RH inutiles ; sortie acheteur purgée de commentaires internes non destinés. |
| Source / preuve | Chaque fait critique ouvre preuve entreprise/acheteur ou hypothèse ; toutes les sections signalent leur origine et révision. |
| État vide | Liste exigée par la phase et les lots, pas un mémoire générique déjà présenté comme conforme. |
| État normal | Pièces présentes, applicables, revues et incluses distinguées ; sections reliées aux critères. |
| Traitement en cours | Brouillon IA ou export en préparation clairement séparé du document approuvé. |
| Résultat partiel | Section incomplète ou format non qualifié ; tâches de complément créées avec responsable. |
| Erreur | Génération/réimport échoué, original et dernier brouillon conservés. |
| Blocage critique | Attestation tierce inventée, engagement non accepté ou modèle imposé non respecté interdit P4/P5 dépendantes. |
| Reprise | Modifier copie, réimporter, comparer et refaire seulement revues touchées. |
| Action IA | Brouillon fondé sur sources choisies, zones manquantes visibles ; aucune signature ni affirmation de capacité inventée. |
| IA indisponible | Modèles, rédaction manuelle/externe, réemploi validé, checklist et revue. |
| Mobile | Commentaire ou consultation ciblée ; aucune édition complète Word/Excel garantie. |
| Accessibilité | A11Y ; alternatives au glisser-déposer, revue textuelle des modifications, suivi clavier des sections. |

**Acceptation** : E10-A, promesse « sous 2 heures » exige validation et lien passation ; E10-B, DUME n'impose pas artificiellement une liasse cumulative ; E10-C, réimport ne supprime pas les formules/commentaires sans avertissement. G05, G21, G22, G36, G44, G50.

## E11 — Coffre de remise

| Champ | Contrat |
|---|---|
| Rôles | Responsable assemble ; Patron/délégataire P5 autorise ; signataire et opérateur humains identifiés. |
| Question métier | Ce paquet exact est-il autorisé, puis quelle réception pouvons-nous réellement prouver ? |
| Données indispensables | Phase/tour/lots, pièces/version, manifeste, contrôles, P4, signatures/pouvoirs, destinataire/canal, échéance, opérateur, tentative et preuve externe. |
| Information prioritaire | Divergence de version ou blocage, puis délai et état exact de réception. |
| Action principale | Avant remise : autoriser P5 avec step-up ; après geste humain : importer et rapprocher le reçu. |
| Actions secondaires | Ouvrir preuve, exporter paquet exact, consignes plateforme, préparer copie de sauvegarde, nouvelle candidate/redépôt, traiter incohérence. |
| Décisions autorisées | P5 sur paquet exact ; rapprochement humain documenté ; aucune admission juridique ni dépôt autonome. |
| Informations masquées | Tous les éléments Direction non inclus intentionnellement ; opérateur voit le paquet qu'il doit remettre sans tout le contexte financier. |
| Source / preuve | RC/consignes, mandat, pièces signées, manifeste interne et reçu externe distincts. |
| État vide | Aucune candidate ; checklist et retour vers réponse, sans bouton d'autorisation actif. |
| État normal | Candidate/autorisation/tentatives/réception clairement séparées ; historique immuable. |
| Traitement en cours | Assemblage/export/rapprochement ; aucune réussite tant qu'opération non confirmée. |
| Résultat partiel | Reçu pli cohérent mais contenu non rapprochable intégralement, avec limite visible. |
| Erreur | Fichier export incomplet, signature non vérifiée, reçu illisible ou mauvaise consultation ; motif ciblé. |
| Blocage critique | Paquet modifié, mauvaise habilitation, pièce critique absente, canal inconnu ou date incohérente selon R05. |
| Reprise | Nouvelle candidate et autorisation si changement ; collecte de reçu ; incident tracé si remise hors autorisation. |
| Action IA | Aide à lire consignes/reçu et signaler écart ; aucun clic de dépôt, signature ou preuve créée. |
| IA indisponible | Contrôles, revue du manifeste, autorisation humaine, export et rapprochement manuel disponibles. |
| Mobile | Consultation et ajout de preuve simple ; P5 seulement si parcours sensible qualifié, jamais hors ligne. |
| Accessibilité | A11Y ; liste des fichiers lisible, confirmation avec version/destinataire, authentification accessible. |

**Acceptation** : E11-A, modifier un octet/fichier après autorisation invalide l'autorisation de ce nouveau paquet ; E11-B, reçu sans inventaire ne produit pas « contenu intégral vérifié » ; E11-C, redépôt propose paquet complet et nouveau reçu ; E11-D, P5 n'est jamais nommé signature légale. G30–G35.

## E12 — Passation

| Champ | Contrat |
|---|---|
| Rôles | Responsable d'offre prépare ; conducteur prend en charge ; Patron/délégataire P7 accepte ; experts ciblés. |
| Question métier | Le chantier reçoit-il exactement le périmètre vendu, ses engagements et les risques encore ouverts ? |
| Données indispensables | Lot gagné, preuve de résultat/accord, version contractuelle, engagements, planning contractuel, moyens, partenaires, budget autorisé, risques et échéances de preuves. |
| Information prioritaire | Engagement sans responsable, écart contrat/offre ou réserve de prise en charge. |
| Action principale | Soumettre puis accepter la passation avec accusé du destinataire. |
| Actions secondaires | Consulter preuve, affecter risque, noter réserve, exporter dossier chantier, réviser passation, préparer REX. |
| Décisions autorisées | Conducteur accuse réception avec réserves ; Patron/délégataire P7 clôt selon conditions ; aucune émission d'ordre de service implicite. |
| Informations masquées | Notes privées de négociation, marge et RIB sans habilitation ; budget chantier autorisé présenté séparément. |
| Source / preuve | Offre remise, accord/notification, modifications acceptées P6 et pièces de passation versionnées. |
| État vide | Aucun lot gagné prouvé ou aucun dossier assemblé ; indique ce qui manque sans créer chantier fictif. |
| État normal | Engagements affectés, responsables et accusés ; liens aux pièces contractuelles et risques. |
| Traitement en cours | Assemblage du dossier, ancienne édition clairement identifiée. |
| Résultat partiel | Un lot transmis, autre en attente ; réserves et pièces manquantes explicites. |
| Erreur | Export incomplet ou référence inaccessible ; aucune clôture silencieuse. |
| Blocage critique | Engagement non repris/non affecté, version contractuelle contradictoire ou destinataire absent empêche clôture. |
| Reprise | Compléter, arbitrer, créer nouvelle édition et nouvel accusé des changements. |
| Action IA | Préparer synthèse du vendu et comparer offre/contrat, toujours revue. |
| IA indisponible | Assemblage manuel à partir du registre et des documents, accusé et P7 possibles. |
| Mobile | Consultation ciblée terrain, notes et réserves ; état de synchronisation explicite. |
| Accessibilité | A11Y ; checklist textuelle, documents dérivés accessibles et réserve saisissable au clavier. |

**Acceptation** : E12-A, engagement validé repris ou exclusion justifiée et arbitrée ; E12-B, lot perdu absent du périmètre gagné ; E12-C, nouvelle pièce contractuelle rouvre les éléments concernés ; E12-D, aucune clôture ne vaut ordre de démarrage des travaux. G23, G36, G38.

## Les 12 écrans suffisent-ils ?

**Pour le cycle d'une Affaire : oui, avec Résultat/REX dans E06 et Visite/Questions dans E06/E07/E10. Pour tout le SaaS vendu : non.** La Mémoire Entreprise et l'Administration sont déjà des espaces figés §10 ; leurs parcours critiques ne sont pourtant pas couverts par les douze contrats. Les contractualiser ne rajoute pas deux applications ni ne remplace OWN-12.

### S01 — Entreprise / Mémoire Entreprise

Question : quelles preuves pouvons-nous réutiliser, pour quelle société et jusqu'à quand ? Rôles : administratif/propriétaire de contenu, QSE, achats, DAF selon catégorie. Action principale : vérifier/publier une version réutilisable ; secondaires : demander renouvellement, voir Affaires dépendantes, retirer, exporter selon droit. Données : identité/établissement, validité, applicabilité, preuve, propriétaire et sensibilité. Un administrateur de compte n'a pas lecture des documents sensibles.

États : vide = kit minimal identité/assurances/références ; normal = preuves réutilisables par portée ; traitement = import contrôlé ; partiel = validité connue mais applicabilité non vérifiée ; erreur = pièce non lisible ; blocage = pièce expirée/inadaptée pour une exigence ; reprise = nouvelle version et revue des offres ouvertes dépendantes. IA propose métadonnées uniquement ; sans IA, saisie/revue restent disponibles. Mobile : consultation/ajout ciblé, pas dossier RH. A11Y s'applique.

Preuves : fichier/version, organisme, référence de vérification et lieu exact si extraction. Validation : propriétaire de contenu habilité ; dérogation sensible selon R05. Acceptation S01-A : une assurance hors activité ne devient pas applicable par sa date ; S01-B : retirer un CV alerte les offres ouvertes sans modifier les plis historiques ; S01-C : mémoire de démonstration isolée des faits réels. G43–G44.

### S02 — Organisation / Accès / Gouvernance et support

Question : qui peut agir, avec quels droits, et comment garder ou récupérer les données de l'entreprise ? Rôles : Propriétaire et Administrateur pour gestion ; autorité Direction pour droits sensibles ; support exceptionnel séparé. Action principale selon contexte : traiter invitation/délégation/incidence d'accès ; opérations rares guidées pour export, transfert ou fermeture. Données : utilisateurs/statuts, portées, MFA sans secrets, sessions, délégations, responsables, accès support, politique de conservation et demandes de sortie.

États : vide = activation premier compte/MFA ; normal = droits et expirations visibles ; traitement = invitation/export/récupération ; partiel = utilisateur invité non activé ou export limité ; erreur = invitation refusée/export échoué ; blocage = transfert sans successeur, accès sans pouvoir ou fermeture avec export non résolu ; reprise = réémission, procédure de récupération, approbation sensible ou nouveau transfert. Aucun état ne donne accès au contenu en raison du rôle administratif.

Sources/preuves : approbations, identité vérifiée, événements d'accès, manifeste d'export et calendrier de purge. IA facultative pour expliquer les règles à partir de données autorisées ; aucune attribution/récupération/fermeture autonome. Sans IA, parcours identique. Mobile : sécurité personnelle et lecture d'état, opérations complexes sur parcours dédié accessible ; aucun contournement MFA. A11Y couvre aussi les erreurs d'authentification et moyens de secours.

Acceptation S02-A : admin ne s'attribue pas les marges ; S02-B : départ coupe sessions et délégations sans effacer décisions ; S02-C : export complet respecte catégories ; S02-D : révocation support effective ; S02-E : récupération du dernier Propriétaire suit l'arbitrage A02. G14, G17–G20, G24, G45–G48.

Les formulaires connexion/MFA/récupération et le paquet tiers sont des parcours de support de S02/R03/R13, non des nouveaux écrans métier de premier niveau. Leur recette reste obligatoire.


---

# 57. Sources et preuves du contre-audit

## H. Registre de recherche

Recherche arrêtée au 13 septembre 2026. Les dates indiquées sont celles des publications lorsqu'elles sont identifiables, non celles des simples indexations. Une page accessible ne démontre ni la conformité d'un logiciel ni son comportement en production. Les exigences proposées par l'audit sont des choix produit, sauf lorsqu'un texte applicable est explicitement cité.

**OFF** : source officielle. **ED** : affirmation ou documentation publique d'éditeur, sans essai indépendant. **LOC** : document propriétaire local. **HYP** : hypothèse ou recommandation de l'audit. Aucun entretien, démonstration commerciale ou test utilisateur réel n'a été effectué. Aucun gain concurrentiel chiffré n'est repris comme fait établi.

| N° | Type / éditeur | Source, date publiée ou vérifiée | Fait exploitable et limite |
|---|---|---|---|
| 1 | OFF — DILA / Service Public | [Remettre la réponse et échanger avec l'acheteur](https://entreprendre.service-public.gouv.fr/vosdroits/F32106), vérifié 01/04/2026 | Distingue candidature/offre, remise, redépôt complet, copie de sauvegarde et signature. Ne remplace pas les règles de la consultation. |
| 2 | OFF — DILA | [Préparer le dossier de candidature](https://entreprendre.service-public.gouv.fr/vosdroits/F32144), page consultée | DUME et formulaires de candidature, capacités et pièces. Ne justifie pas de rendre chaque document obligatoire dès toute candidature. |
| 3 | OFF — DILA | [Préparer le dossier offre](https://entreprendre.service-public.gouv.fr/vosdroits/F32154), page consultée | Offre adaptée aux documents de consultation, critères et pièces demandées. |
| 4 | OFF — DILA | [Groupement et sous-traitance](https://entreprendre.service-public.gouv.fr/vosdroits/F32137), vérifié 01/01/2025 | Mandataire, cotraitants, formes de groupement et déclaration de sous-traitance ; les capacités et signatures restent attachées aux personnes concernées. |
| 5 | OFF — Légifrance, accès partiel | [R2151-6](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000037730533) | Dernière offre reçue dans le délai ; texte retrouvé dans l'index officiel, ouverture directe refusée. Corroboration indépendante du moteur de recherche par la page DILA n°1 ouverte. Contrôle du texte consolidé requis pour qualification juridique finale. |
| 6 | OFF — Légifrance, accès partiel | [R2151-4](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000037730539) | Prolongation des délais dans les cas prévus, dont modifications importantes. Texte indexé, ouverture directe refusée ; ne pas déduire automatiquement une nouvelle date. À valider par spécialiste juridique. |
| 7 | OFF — DAJ | [Questions-réponses copie de sauvegarde](https://www.economie.gouv.fr/files/files/directions_services/daj/marches_publics/dematerialisation/QR-Copie-sauvegarde.pdf), document relatif à l'évolution de 2023 | Modalités de copie de sauvegarde, notamment électronique ; ce n'est ni un dépôt principal ni une garantie d'admission. PDF ouvert, 3 pages. |
| 8 | OFF — DAJ | [Cahiers des clauses administratives générales et techniques](https://www.economie.gouv.fr/daj/commande-publique/reglementation-de-la-commande-publique/cahiers-des-clauses-administratives), page consultée | Un CCAG s'applique par référence expresse ; dérogations possibles. Les archives de CCAG 1976/2009 n'ont pas été utilisées comme droit courant. |
| 9 | OFF — DAJ / OECP | [Guide pratique des prix, édition 2023](https://www.economie.gouv.fr/daj/publication-de-la-version-2023-du-guide-pratique-de-loecp-le-prix-dans-les-marches-publics), publication 2023 | Cadre de conseil sur le prix et ses évolutions ; aucune formule contractuelle universelle déduite. Page de présentation consultée, pas d'audit intégral du guide. |
| 10 | OFF — DILA | [Obtenir une attestation de vigilance](https://entreprendre.service-public.gouv.fr/vosdroits/F31422), vérifié 06/07/2026 | Seuil de 5 000 € HT apprécié sur le contrat et renouvellement semestriel ; authentification de la pièce à distinguer de sa simple présence. |
| 11 | OFF — Urssaf, accès partiel | [Obtenir et vérifier une attestation](https://www.urssaf.fr/accueil/attestation-vigilance.html), mise à jour 17/04/2025 | Même principe de vigilance ; contenu indexé, accès direct en erreur 502. Recommandation fondée aussi sur n°10 ouvert. |
| 12 | OFF — DILA | [Modèle d'attestation décennale](https://entreprendre.service-public.gouv.fr/vosdroits/R44868), page consultée | Distingue période, activité et périmètre de garantie. Le modèle individuel illustre les champs ; il ne qualifie pas toutes les assurances d'une PME ni tous les ouvrages. |
| 13 | OFF — DILA | [Recourir à la sous-traitance](https://entreprendre.service-public.gouv.fr/vosdroits/F36261), page consultée | Repères pour le contrat, les obligations et protections de sous-traitance. Qualification public/privé et rang à faire pour chaque cas. |
| 14 | OFF — DAJ | [Considérations environnementales et sociales : nouvelles exigences](https://www.economie.gouv.fr/daj/considerations-environnementales-et-sociales-dans-les-marches-publics-publication-de-fiches-pratiques-pour-repondre-aux-nouvelles-exigences-de-la), publication 2026 | Échéance du 22/08/2026 : contrôle des critères et conditions d'exécution selon le régime applicable. Ne pas traiter toutes les obligations sociales comme universelles. |
| 15 | OFF — CNIL | [Gérer les habilitations](https://www.cnil.fr/fr/securite-gerer-les-habilitations), 13/03/2024 | Moindre privilège, validation et revue des droits, retrait lors du départ ou changement de fonction. |
| 16 | OFF — CNIL | [Tracer les opérations](https://www.cnil.fr/fr/securite-tracer-les-operations), 14/03/2024 | Journaux proportionnés et protégés ; recommandation usuelle de six mois à un an avec exceptions justifiées. Pas de conservation illimitée ni de détournement vers la mesure du temps de travail. |
| 17 | OFF — CNIL | [Gérer la sous-traitance](https://www.cnil.fr/fr/securite-gerer-la-sous-traitance), 14/03/2024 | Contrat, chaîne de sous-traitance, restitution/destruction et flux géographiques ; hébergement dédié ne suffit pas. |
| 18 | OFF — CNIL | [Durées de conservation](https://www.cnil.fr/fr/passer-laction/les-durees-de-conservation-des-donnees), page consultée | Durées définies selon finalités et distinction base active / archivage ; pas de durée unique pour tous les dossiers. |
| 19 | OFF — ANSSI | [Authentification multifacteur et mots de passe](https://messervices.cyber.gouv.fr/guides/recommandations-relatives-lauthentification-multifacteur-et-aux-mots-de-passe), 08/10/2021 | Robustesse adaptée au risque ; page de présentation consultée. Les durées et règles précises proposées dans R03 sont des choix de l'audit, non des prescriptions chiffrées attribuées à l'ANSSI. |
| 20 | OFF — CNIL | [Questions-réponses sur l'IA générative](https://cnil.fr/fr/les-questions-reponses-de-la-cnil-sur-lutilisation-dun-systeme-dia-generative), 18/07/2024 | Hallucinations, vérification, usages encadrés, garanties fournisseur et transferts. |
| 21 | OFF — ANSSI | [Sécurité d'un système d'IA générative](https://messervices.cyber.gouv.fr/guides/recommandations-de-securite-pour-un-systeme-dia-generative), page consultée | Source de cadrage des risques de systèmes IA ; la prévention des actions issues d'un DCE est une exigence produit dérivée, pas une promesse d'invulnérabilité. |
| 22 | OFF — DINUM | [RGAA](https://accessibilite.numerique.gouv.fr/), version affichée 4.1.2 | RGAA 5 annoncé pour fin 2026 ; conserver la cible WCAG 2.2 AA et expliciter les compléments au référentiel courant. Assujettissement légal du SaaS B2B à qualifier séparément. |
| 23 | OFF — CNIL | [Gérer les incidents et violations](https://www.cnil.fr/fr/securite-gerer-les-incidents-et-les-violations), 14/03/2024 | Organisation, réaction, documentation et information en cas d'incident. |
| 24 | OFF — CNIL | [Questions-réponses règlement IA](https://cnil.fr/fr/entree-en-vigueur-du-reglement-europeen-sur-lia-les-premieres-questions-reponses-de-la-cnil), mise à jour affichée 17/08/2026 | Qualification par usage et obligations de transparence à examiner. Le rapport ne classe pas juridiquement SMART AO et ne transforme pas un calendrier général en obligation universelle. |
| 25 | OFF — DILA / BOAMP | [CGU du site et service d'alerte](https://www.boamp.fr/telechargements/cms/fichiers/CGU_site_boamp.fr_et_service_d_alerte_BOAMP_2024-10-21.pdf), 21/10/2024 | Recherche d'avis et alertes ; ne démontre ni accès exhaustif aux DCE ni surveillance universelle des profils acheteurs. PDF ouvert, 4 pages. |
| 26 | ED — Spigao | [Présentation du produit](https://www.spigao.com/), sans date | Annonce veille, import de bordereaux, travail avec Excel/logiciels de devis et mémoire technique. Capacités annoncées, non testées. |
| 27 | ED — Libel | [Logiciel de réponse et mémoire technique](https://www.libel.fr/logiciel-reponse-appel-offres-memoire-technique/), sans date | Annonce candidature, modèles, DUME, documents, rappels et chiffrage bureautique. Aucun taux de succès repris. |
| 28 | ED — Tenderbolt | [Analyse d'appel d'offres et GO/NO-GO](https://www.tenderbolt.ai/fr/features/analysis), sans date | Annonce extraction et grille de qualification personnalisable. Ni l'exhaustivité ni la justesse des analyses ne sont démontrées. |
| 29 | ED — Saqara | [Solutions pour entreprises du bâtiment](https://saqara.com/logiciel/entreprise-batiment), sans date | Annonce lots, DPGF, nouvelles pièces, historique des réponses et échanges privés. |
| 30 | ED — Once For All | [Conformité documentaire](https://onceforall.fr/solutions/conformite/), sans date | Annonce collecte, contrôle, relances et alertes avant expiration. Ne prouve pas une qualification juridique de tous les documents. |
| 31 | ED — Libel, documentation d'usage | [Dématérialisation mode d'emploi](https://www.libel.fr/dematerialisation-candidature-appel-offres/), sans date, illustrations anciennes | Décrit assemblage et export puis accès au profil acheteur. Utilisé seulement comme convention bureautique, pas comme guide réglementaire actuel. |

## Preuves locales

- **LOC-01** : `docs/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_DECISION_FREEZE_v0.2.md`, 1 339 lignes, 6 650 mots ; lecture intégrale par sections ; SHA-256 `74603d872754ec70f317d25cd5b7940a0e420638b91df859dddcd0a50308b6f9`.
- **LOC-02** : `docs/SMART_AO_Cahier_des_charges_Metier_v1.0.md`, tableau des portes P0–P7, lignes 110–117, consulté comme antécédent ; pas comme remplacement du socle propriétaire.
- **LOC-03** : `docs/SMART_AO_CCF_UX_Product_Blueprint_v1.1.md`, §6 et tableau P0–P7, lignes 571–578, consultés ; passages et titres ciblés de collaboration, données et parcours privés repérés. Audit non exhaustif de ce document antérieur.
- **LOC-04** : `docs/SMART_AO_Benchmark_Concurrentiel_UX_Parcours_v1.0.md`, panel, analyses ciblées et protocole de validation consultés. Les affirmations retenues dans ce contre-audit ont été recoupées avec les pages éditeurs ci-dessus.

## Limites de preuve et recherche non concluante

L'accès direct à deux articles Légifrance, à la page Urssaf, à un avis rectificatif BOAMP et à la FAQ de démonstration Klekoon a échoué. Leurs extraits ne sont pas présentés comme une lecture intégrale. Le guide actuel complet de PLACE n'a pas été obtenu : le comportement exact de chaque profil acheteur doit être vérifié sur les consultations pilotes. Aucun délai de réception propre à Klekoon n'est généralisé.

TED est différé conformément à DEC-06 : aucun benchmark de son connecteur ni de ses formats n'est nécessaire au gel V1. Les forums et témoignages ne sont pas indispensables aux conclusions retenues ; aucun récit utilisateur n'a été inventé. Les fréquences des irritants dans le rapport sont des hypothèses qualitatives à vérifier avec les deux pilotes, et non une enquête représentative.

Les sources juridiques servent à définir des alertes et parcours conservateurs. Les conclusions exigeant une qualification sont marquées **« À valider par spécialiste juridique »**, en particulier droit de signature, régimes contractuels, conservation, transferts, qualification RIA et assujettissement à l'accessibilité.


# Références citées dans la consolidation

[^1]: [Remettre la réponse et échanger avec l'acheteur](https://entreprendre.service-public.gouv.fr/vosdroits/F32106). Type, date et limites : §57, entrée 1.
[^2]: [Préparer le dossier de candidature](https://entreprendre.service-public.gouv.fr/vosdroits/F32144). Type, date et limites : §57, entrée 2.
[^3]: [Préparer le dossier offre](https://entreprendre.service-public.gouv.fr/vosdroits/F32154). Type, date et limites : §57, entrée 3.
[^4]: [Groupement et sous-traitance](https://entreprendre.service-public.gouv.fr/vosdroits/F32137). Type, date et limites : §57, entrée 4.
[^5]: [R2151-6](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000037730533). Type, date et limites : §57, entrée 5.
[^6]: [R2151-4](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000037730539). Type, date et limites : §57, entrée 6.
[^7]: [Questions-réponses copie de sauvegarde](https://www.economie.gouv.fr/files/files/directions_services/daj/marches_publics/dematerialisation/QR-Copie-sauvegarde.pdf). Type, date et limites : §57, entrée 7.
[^9]: [Guide pratique des prix, édition 2023](https://www.economie.gouv.fr/daj/publication-de-la-version-2023-du-guide-pratique-de-loecp-le-prix-dans-les-marches-publics). Type, date et limites : §57, entrée 9.
[^10]: [Obtenir une attestation de vigilance](https://entreprendre.service-public.gouv.fr/vosdroits/F31422). Type, date et limites : §57, entrée 10.
[^11]: [Obtenir et vérifier une attestation](https://www.urssaf.fr/accueil/attestation-vigilance.html). Type, date et limites : §57, entrée 11.
[^12]: [Modèle d'attestation décennale](https://entreprendre.service-public.gouv.fr/vosdroits/R44868). Type, date et limites : §57, entrée 12.
[^13]: [Recourir à la sous-traitance](https://entreprendre.service-public.gouv.fr/vosdroits/F36261). Type, date et limites : §57, entrée 13.
[^14]: [Considérations environnementales et sociales : nouvelles exigences](https://www.economie.gouv.fr/daj/considerations-environnementales-et-sociales-dans-les-marches-publics-publication-de-fiches-pratiques-pour-repondre-aux-nouvelles-exigences-de-la). Type, date et limites : §57, entrée 14.
[^15]: [Gérer les habilitations](https://www.cnil.fr/fr/securite-gerer-les-habilitations). Type, date et limites : §57, entrée 15.
[^16]: [Tracer les opérations](https://www.cnil.fr/fr/securite-tracer-les-operations). Type, date et limites : §57, entrée 16.
[^17]: [Gérer la sous-traitance](https://www.cnil.fr/fr/securite-gerer-la-sous-traitance). Type, date et limites : §57, entrée 17.
[^18]: [Durées de conservation](https://www.cnil.fr/fr/passer-laction/les-durees-de-conservation-des-donnees). Type, date et limites : §57, entrée 18.
[^19]: [Authentification multifacteur et mots de passe](https://messervices.cyber.gouv.fr/guides/recommandations-relatives-lauthentification-multifacteur-et-aux-mots-de-passe). Type, date et limites : §57, entrée 19.
[^20]: [Questions-réponses sur l'IA générative](https://cnil.fr/fr/les-questions-reponses-de-la-cnil-sur-lutilisation-dun-systeme-dia-generative). Type, date et limites : §57, entrée 20.
[^21]: [Sécurité d'un système d'IA générative](https://messervices.cyber.gouv.fr/guides/recommandations-de-securite-pour-un-systeme-dia-generative). Type, date et limites : §57, entrée 21.
[^22]: [RGAA](https://accessibilite.numerique.gouv.fr/). Type, date et limites : §57, entrée 22.
[^23]: [Gérer les incidents et violations](https://www.cnil.fr/fr/securite-gerer-les-incidents-et-les-violations). Type, date et limites : §57, entrée 23.
[^24]: [Questions-réponses règlement IA](https://cnil.fr/fr/entree-en-vigueur-du-reglement-europeen-sur-lia-les-premieres-questions-reponses-de-la-cnil). Type, date et limites : §57, entrée 24.
[^25]: [CGU du site et service d'alerte](https://www.boamp.fr/telechargements/cms/fichiers/CGU_site_boamp.fr_et_service_d_alerte_BOAMP_2024-10-21.pdf). Type, date et limites : §57, entrée 25.
