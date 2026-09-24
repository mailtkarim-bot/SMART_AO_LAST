# SMART AO — Cahier directeur Produit & Métier
## OWNER FREEZE v2.0 — AUTORITÉ PRODUIT/MÉTIER ACTIVE

**Date :** 24 septembre 2026  
**Statut :** PRODUCT FREEZE v2.0 — PROMU PAR LE PROPRIÉTAIRE LE 24 SEPTEMBRE 2026  
**Remplace :** `../_ARCHIVE/produit_metier/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md`  
**Source métier principale :** `SMART_AO_CAHIER_DIRECTEUR_METIER_MASTER_v2.0.md`  
**Question couverte :** « Quel SmartAO voulons-nous construire et quelles vérités métier doit-il être capable de prouver sans les simplifier ? »

> **RÈGLE D’AUTORITÉ.** Le propriétaire a explicitement promu ce document le 24 septembre 2026. Il est l’autorité produit/métier active. Le Product Freeze v1.0 est historique et archivé. Le cahier technique et le code doivent dériver de ce v2.0 ; aucun comportement historique ne peut le contredire silencieusement.

---

## 0. Objet de la réouverture

Le Product Freeze v1.0 a correctement fixé les fondamentaux : Affaire, Mémoire Entreprise, source/version/preuve, séparation Patron/Collaborateur, P0–P7, confidentialité, dépôt humain, IA non autoritaire, états `UNKNOWN/PARTIAL/REVIEW_REQUIRED`, idempotence et continuité.

Le MASTER métier v2.0 a cependant démontré que plusieurs risques essentiels étaient trop compressés pour constituer des obligations produit explicites : dérogations, sanctions, préservation des droits, ordres de service, règlement des comptes/DGD, résiliation, assurance réelle, HSE capacitaire, engagements mesurables, réglementation applicable et circuit de paiement.

La réouverture v2.0 poursuit un objectif unique :

> **empêcher qu’une simplification produit fasse disparaître un risque métier capable de consommer la marge, la trésorerie ou un droit contractuel de l’entreprise.**

Le v2.0 ne transforme pas SmartAO en ERP chantier, cabinet juridique, logiciel de chiffrage complet ou moteur de conformité automatique.

---

# 1. Vision, promesse et client initial

## 1.1 Question fondamentale — FIGÉE v2.0

SMART AO doit aider le dirigeant à répondre de manière défendable à la question :

> **Cette affaire mérite-t-elle notre effort commercial, pouvons-nous la gagner, la financer, l’exécuter correctement, protéger nos droits et conserver la marge prévue ?**

« Protéger nos droits » signifie que le produit doit rendre visibles, sourcés et transmissibles les événements, délais, formalismes, preuves et décisions qui conditionnent la capacité de l’entreprise à défendre un paiement, une prolongation, une réserve, une réclamation ou une clôture contractuelle. SmartAO ne délivre pas seul un avis juridique.

## 1.2 Positionnement produit — FIGÉ v2.0

SMART AO est :

> **un poste de commandement d’ingénierie DCE et de décision d’engagement pour PME BTP, centré sur l’Affaire, la preuve, l’applicabilité, l’impact chantier, la décision humaine, la protection de la marge et la préservation des droits.**

SMART AO n’est pas : chatbot documentaire, générateur générique de mémoire, ERP chantier, logiciel qui fixe seul le prix, avocat automatique, moteur de conformité universelle, simple GED ou score opaque de GO/NO-GO.

## 1.3 Client initial — HÉRITÉ / MAINTENU

- cœur de cible : PME BTP françaises de 10 à 100 personnes ;
- qualification terrain avec au moins un pilote multi-métiers/entreprise générale et un pilote spécialisé technique ;
- public et privé sont natifs dans le modèle ;
- la promesse V1 est qualifiée d’abord sur la commande publique ;
- le privé reste borné tant qu’un corpus privé diversifié n’a pas été validé.

---

# 2. Doctrine produit non négociable

1. L’Affaire reste l’unité de décision et de preuve.
2. La Mémoire Entreprise reste le patrimoine privé gouverné de l’entreprise.
3. Toute conclusion critique garde sa source, sa version et son locator/hash lorsque disponible.
4. Une absence de preuve ne devient jamais conformité, zéro, absence de coût ou absence de risque.
5. Une rectification invalide les conclusions dépendantes sans effacer l’historique.
6. Un score ne décide jamais d’une porte P0–P7.
7. Une règle générale n’est jamais appliquée à l’affaire sans preuve d’applicabilité.
8. Une règle contractuelle particulière peut modifier ou neutraliser une règle de référence ; la dérogation doit être visible.
9. Une règle juridique, assurantielle ou HSE incertaine provoque `REVIEW_REQUIRED`, pas une conclusion générée.
10. Les calculs contractuels et financiers critiques sont déterministes, reproductibles et sourcés ; le LLM ne calcule pas l’autorité finale.
11. Le Collaborateur ne reçoit ni marge, ni prix d’achat confidentiel, ni cash Direction, ni notes privées Patron par UI, API, recherche, export, notification ou contexte IA.
12. L’IA observe, extrait, rapproche, explique et propose ; elle ne décide ni GO, ni prix final, ni couverture assurantielle, ni conformité juridique, ni recours, ni dépôt.
13. Les documents externes sont des données non fiables ; leur contenu ne peut élargir droits, outils ou instructions système.
14. Une panne IA ou source conserve un chemin manuel visible.
15. Le dépôt final externe reste humain en V1.
16. SmartAO ne devient pas un ERP chantier ; il doit toutefois représenter assez de conséquences chantier pour sécuriser la décision d’engagement et la passation.

---

# 3. Autorité, rôles et confidentialité

## 3.1 Patron

Le Patron : décide P0–P7 selon habilitation ; contrôle prix, marge, trésorerie et exposition ; accepte les hypothèses critiques ; arbitre dérogations et risques contractuels ; approuve garanties, solidarités et engagements sensibles ; décide les escalades juridiques/assurantielles/DAF/QSE ; autorise P4/P5 et la passation selon politique.

## 3.2 Collaborateur / Responsable

Il prépare, contrôle, documente, consulte, coordonne et remonte les inconnus. Il ne devient jamais Patron par accumulation d’informations ou de tâches. Il peut voir un impact non financier utile à son travail sans recevoir la vérité économique Direction correspondante.

## 3.3 Experts

Métreur, conducteur, QSE, DAF, administratif, achats, juriste, courtier/assureur et autres experts contribuent uniquement dans leur périmètre. Une validation experte et une décision Patron restent deux actes distincts.

## 3.4 Administrateur / Support / Tiers

Administration technique ≠ autorité métier. Le support n’acquiert jamais implicitement l’accès au contenu métier. Un tiers externe reçoit un paquet borné en objet, durée, données et action.

## 3.5 Contrat d’une décision critique

Toute décision critique porte : auteur, rôle, organisation/tenant, Affaire/lot/phase/tour, date, version, faits/preuves consultés, inconnus, conditions, éventuelle expiration, motif et règle de réouverture.

---

# 4. Objets métier de premier rang

Les objets suivants sont désormais normatifs au niveau produit. Le cahier technique choisit leur représentation logicielle exacte ; il ne peut les supprimer par regroupement générique.

## 4.1 Objets historiques maintenus

`Affaire`, `DCE/DocumentVersion`, `Source/SourceAnchor`, `Evidence`, `Requirement`, `Unknown`, `Hypothesis`, `Contradiction`, `Risk`, `Decision`, `Condition`, `Task`, `Partner`, `PricingScenario`, `Commitment`, `CandidatePackage`, `Manifest`, `SubmissionEvidence`, `Result`, `Handover`, `REX`, éléments de Mémoire Entreprise.

## 4.2 Nouveaux contrats produit v2.0

### A. Carte d’Engagement de l’Affaire
Projection Patron centrale, composée de douze axes ; ce n’est ni un score ni une nouvelle source de vérité.

### B. `REGULATORY_PROFILE`
Profil de faits validés permettant de qualifier l’applicabilité de règles versionnées : public/privé, ouvrage, usage, date, montant, site, travaux, acteurs, diagnostics et autres faits nécessaires.

### C. Règle réglementaire vivante
Chaque règle porte source d’autorité, publication, dates d’effet/fin, champ, exceptions, faits requis, statut `ACTIVE/FUTURE/EXPIRED/UNKNOWN_APPLICABILITY/REVIEW_REQUIRED`, validation et date de revue.

### D. Baseline contractuelle et dérogation
Le produit doit représenter la règle de référence réellement incorporée au contrat, sa version, la clause particulière qui la modifie et l’impact métier résultant. Une simple étiquette « CCAG Travaux » ne suffit pas.

### E. `CONTRACTUAL_SANCTION`
Sanction/pénalité avec source, déclencheur, unité, formule, base, franchise, plafond, cumul, procédure, dérogation, exonération potentielle, responsable et scénarios d’exposition.

### F. `RIGHT_PRESERVATION_EVENT`
Événement de préservation d’un droit : trigger, source/version, règle de délai, échéance, destinataire, forme, contenu minimal, preuve d’envoi/réception, responsable, statut et conséquence potentielle.

### G. Modification / ordre de service
Objet représentant prescription, forme, réception, obligation d’exécuter selon cadre, réserves, délai de réaction, prix/provisoire/nouveau, effet planning et preuve.

### H. Règlement des comptes / réception / DGD
Séquence sourcée reliant OPR, réception, réserves, décompte final/général, DGD, garanties et échéances. Le produit n’invente jamais un DGD tacite sans toutes les conditions prouvées.

### I. Exposition de résiliation / substitution
Cas de rupture, remède, mise en demeure, exécution aux frais et risques, marché de substitution, liquidation et conséquences ; sortie = stress de risque, pas avis juridique.

### J. Évaluation assurance/prestation
Lien entre prestation promise, activité déclarée, technique, ouvrage, période, territoire, exclusions et preuve. États minimaux : `COVERED`, `PROBABLY_COVERED`, `NOT_ESTABLISHED`, `OUTSIDE_DECLARED_ACTIVITY`, `BROKER_REVIEW_REQUIRED`.

### K. Prérequis d’exécution
Obligation HSE/technique/autorisation traduite en document, compétence, personne, matériel, délai d’obtention, coût, planning, preuve et responsable.

### L. Engagement mesurable
Promesse sensible de l’offre avec KPI/valeur, méthode de mesure, période, preuve, coût, ressource, responsable, partenaire/cascade, reporting et conséquence potentielle.

### M. Circuit de paiement
Chaîne production → situation → contrôle/service fait → MOA/plateforme/payeur → encaissement, avec documents, rejets/suspensions, dates et hypothèses prudentes.

### N. Obligation post-réception
OPR, essais, mise en service, DOE/DIUO, levée de réserves, GPA, stock, maintenance initiale, astreinte, garantie, clôture et coût associé.

### O. Dépendance tierce
Autorisation, coupure, voirie, concessionnaire, grutage, badge, accès, consignation, autorité externe ou autre condition pouvant rendre le planning impossible.

---

# 5. Cycle P0–P7 — portes maintenues, critères enrichis

Aucune nouvelle porte n’est créée. Les portes restent distinctes et toute condition critique non levée peut rouvrir la porte correspondante.

## P0 — Cibler

Décider si une opportunité mérite une action commerciale. Prendre en compte : métier/zone, horizon, intérêt stratégique, coût d’approche, légalité/éthique de l’intelligence commerciale, données sourcées et inconnus.

## P1 — Ouvrir

Le DCE/invitation est reçu avec périmètre, échéance et source. Une incompatibilité immédiate, pièce critique absente ou impossibilité manifeste reste visible ; un dossier partiellement lisible ne devient pas « analysé ».

## P2 — GO de principe

Examiner au minimum : éligibilité, candidature, capacités, charge d’étude, partenaires essentiels, MIRP initial, profil réglementaire, assurance de principe, constructibilité rédhibitoire, dépendances tierces et régime contractuel applicable.

## P3 — GO économique

Examiner au minimum : marge, cash, garanties/financement, clause de prix/révision, exposition fournisseurs, charge/capacité, pénalités identifiables, risques de résiliation/substitution, HSE/réglementaire coûteux, coût post-réception et scénarios de portefeuille lorsqu’applicables.

## P4 — Autoriser l’offre

Vérifier cohérence prix/technique/planning, documents, preuves, engagements mesurables, ressources promises, assurances sensibles, dérogations acceptées, environnement/social, conditions ouvertes et toute promesse pouvant devenir obligation de chantier.

## P5 — Autoriser le dépôt

Maintenir séparation stricte : candidate → contrôles/signatures → autorisation P5 → export → dépôt humain → preuve externe. Toute modification du paquet après autorisation invalide P5 selon dépendances.

## P6 — Accepter clarification/négociation/mise au point

Toute modification pertinente déclenche revalidation ciblée : prix, marge, cash, capacité, assurance, engagement, pénalité, règle contractuelle, profil réglementaire, partenaire, délai et droits.

## P7 — Lancer l’exécution

P7 exige une passation formelle comprenant le contrat vendu et les mécanismes nécessaires pour protéger son économie : conditions du GO, risques résiduels, engagements, partenaires, pénalités, paiement, assurances, HSE, documents post-attribution et calendrier de préservation des droits. **P7 n’est pas un ordre de service ni une autorisation juridique de démarrer les travaux.**

---

# 6. Carte d’Engagement de l’Affaire — sortie Patron centrale

La Carte d’Engagement doit permettre au Patron de comprendre en quelques minutes non seulement « faut-il y aller ? » mais « si j’y vais, comment dois-je y aller ? ».

## 6.1 Douze axes obligatoires

1. intérêt commercial ;
2. éligibilité/candidature ;
3. périmètre technique ;
4. constructibilité/logistique ;
5. contrat et exposition ;
6. prix/marge/sensibilité ;
7. trésorerie/garanties/financement ;
8. capacité/charge/ressources ;
9. fournisseurs/sous-traitants/cotraitants ;
10. HSE/environnement/réglementation ;
11. obligations documentaires/engagements de l’offre ;
12. préservation des droits/réception/sortie du contrat.

## 6.2 Anatomie d’une ligne

Chaque point important doit pouvoir exposer : fait/source, version, locator, applicabilité, certitude/inconnu, conséquences technique/coût/délai/cash/contrat, responsable, action, échéance, preuve attendue, décision requise et risque résiduel.

## 6.3 Interdiction du score opaque

La Carte peut agréger et filtrer, mais elle ne réduit jamais la décision à une note globale. Un C1/B0/B1 critique ou un inconnu déterminant reste visible même si les autres axes sont favorables.

## 6.4 GO sous conditions

Chaque condition a propriétaire, échéance, preuve de levée, porte d’origine, criticité et règle de réouverture. « Acceptée par le Patron » ne transforme pas une impossibilité réglementaire ou un défaut de preuve non arbitrable en conformité.

---

# 7. DCE, documents, preuves et rectificatifs

- inventorier archives, sous-archives et fichiers ;
- distinguer reçu, lisible, extrait, revu et couvert ;
- conserver original, hash, version, parser/méthode et locator ;
- signaler pièce annoncée mais absente ;
- conserver documents non supportés/illisibles comme trous de couverture ;
- conserver deux sources en contradiction ;
- une réponse acheteur ou un rectificatif crée une nouvelle version et une analyse d’impact ;
- invalider seulement les conclusions dépendantes ;
- un rectificatif touchant prix, délai, engagement, règle contractuelle ou paquet peut rouvrir P3/P4/P5/P7 ;
- aucun contenu externe n’est exécuté comme instruction.

---

# 8. Applicabilité réglementaire et veille

SmartAO doit distinguer :

1. **fait d’affaire** : donnée sourcée sur le projet ;
2. **règle versionnée** : texte/référence et dates ;
3. **évaluation d’applicabilité** : pourquoi la règle semble applicable/non applicable/incertaine ;
4. **impact métier** : document, coût, délai, compétence, décision ;
5. **validation humaine** lorsque requise.

Une règle future reste `FUTURE`. Une règle expirée ne s’applique pas aux nouvelles affaires sauf raison sourcée. Une source réglementaire indisponible ne produit pas une conclusion à partir d’un cache non daté sans signalement.

Le moteur de règles n'est pas un avocat automatisé. Les sujets juridiques, assurance, HSE et privés sensibles peuvent exiger validation externe avant blocage automatique ou promesse commerciale.

---

# 9. Analyse technique, MIRP, constructibilité et interfaces

## 9.1 Traduction chantier

Pour une prescription importante, le produit doit pouvoir relier :

`exigence → méthode → moyens → interfaces → séquence → contraintes → coût → délai → preuve → responsable`.

## 9.2 MIRP

La complétude du DCE et la complétude nécessaire à un prix défendable sont distinctes. Une information peut être non obligatoire au pli tout en étant critique pour le prix. Les MIRP par corps d’état doivent conserver source, statut, hypothèse, question acheteur et décision Patron.

## 9.3 Interfaces

Le produit doit pouvoir représenter les prestations transversales et limites de lots : inclusion/exclusion/coordination/à confirmer, source CCTP/plan/prix et impact. Le silence d’une DPGF ne crée pas automatiquement une exclusion.

## 9.4 Constructibilité

Accès, stockage, base vie, circulation, levage, ouvrages provisoires, protections, coupures, horaires, phasage, site occupé, séchage/cure, essais, mise en service, remise en état et autorisations tierces peuvent influencer GO, prix et délai.

---

# 10. Économie, prix, cash et capacité

## 10.1 Quatre vues économiques

- marge ;
- pic de trésorerie/date/durée/causes ;
- résistance aux scénarios ;
- valeur attendue/coût d’opportunité, sans transformer une probabilité en vérité.

## 10.2 Prix et révision

Le produit distingue prix ferme/actualisable/révisable, mois/date de référence, index/formule, part fixe, périodicité, exclusions et substitutions lorsque sourcées. Il compare protection contractuelle et exposition achats réelle. Aucun index générique ne vaut couverture.

## 10.3 Capacité

Comparer carnet signé, affaires probables, réponses en cours, ressources, études, encadrement, compétences rares, matériel, congés, maintenance, déplacement et partenaires réellement disponibles. Une ressource nommée dans l’offre est traitée comme engagement potentiel.

## 10.4 Portefeuille

Lorsque activé, le produit doit pouvoir tester plusieurs gains simultanés pour cash, garanties, ressources et dépendances communes. Cette capacité peut être V1.x si le socle V1 garantit au moins l’analyse affaire isolée et les dépendances explicites.

---

# 11. Partenaires, sous-traitance et groupements

Le socle V1 doit au minimum conserver et comparer périmètre, exclusions, prix, validité, délais, garanties, conformité, assurance et disponibilité des partenaires utilisés au chiffrage ou à l'offre.

Sous-traitance : prestation/montant, déclaration/acceptation/agrément selon cadre, paiement direct/garantie lorsque pertinent, vigilance, assurance, dépendance et solution de remplacement.

Groupement : forme, mandat, répartition, solidarité, responsabilités et exposition. Une solidarité inhabituelle exige décision Patron.

La structuration avancée de mandats, portails partenaires et connecteurs peut rester V1.x ; l'exposition métier ne peut pas être supprimée de V1 pour cette raison.

---

# 12. Contrat applicable, dérogations et exposition

## 12.1 Reconstruire le contrat

Public : procédure, CCAG réellement visé/version, CCTG/fascicules cités, CCAP/CCP, AE, pièces de prix, calendrier, réponses/mise au point/avenants selon valeur.

Privé : parties, offre/devis, commande/marché, conditions particulières/générales, plans, planning, échanges acceptés, normes incorporées, sous-traitance, garanties, réception et ordre des pièces.

## 12.2 Dérogations

Chaîne obligatoire :

`REFERENCE_RULE → CONTRACT_REFERENCE → PARTICULAR_OVERRIDE → APPLICABILITY → BUSINESS_IMPACT → HUMAN_DECISION`.

Le produit doit pouvoir montrer côte à côte la règle de référence et la clause particulière qui la modifie.

## 12.3 Pénalités et sanctions

Pour chaque sanction : source, déclencheur, unité, formule, base, franchise, plafond, cumul, contradictoire/mise en demeure, dérogation, éventuelle cause exonératoire, responsable, recours partenaire, scénario central/stress et inconnus.

**Interdit :** coder un plafond, une franchise, un délai ou une exonération comme vérité universelle parce qu'un CCAG particulier les prévoit.

## 12.4 Préservation des droits

Pour chaque événement : source/version, trigger, deadline calculée à partir de la règle applicable, destinataires, forme, contenu requis, responsable, preuves d'envoi/réception, statut et conséquence potentielle. Aucune deadline sensible n'est affichée comme certaine sans source et base de calcul.

## 12.5 OS / modifications / travaux supplémentaires

Le produit doit rendre visibles pouvoir de prescription, forme, réception, réserves, délai de réaction, valorisation/prix nouveaux, impact délai, preuve et conséquences. Il ne réduit pas tout changement à « avenant possible ».

## 12.6 Résiliation / substitution

Le produit expose conditions identifiées, remède, mise en demeure, frais et risques, substitution/liquidation et impact financier potentiel. Il ne qualifie pas seul la validité juridique de la clause.

## 12.7 Réception / règlement / DGD

Le produit représente la séquence applicable et ses preuves. Un DGD tacite ou une forclusion ne peut être affirmé que si chaque condition requise est établie ; sinon `REVIEW_REQUIRED`.

---

# 13. Assurance, HSE, environnement et obligations mesurables

## 13.1 Assurance

Une attestation présente ne suffit pas. Le produit compare la prestation/technique promise avec la portée déclarée et conserve les états d'incertitude. Les cas ambigus ou sensibles escaladent vers courtier/assureur.

## 13.2 HSE / prérequis d'exécution

Chaque exigence applicable doit pouvoir être transformée en compétence/personne/matériel/document/délai/coût/planning/preuve. Une obligation connue mais ressource absente peut maintenir P2/P3/P4 en `REVIEW_REQUIRED`.

## 13.3 Environnement et social

Une promesse mesurable de mémoire ou condition d'exécution devient un engagement structuré, pas du texte libre oublié après dépôt : KPI, valeur, méthode, preuve, coût, responsable, partenaire, reporting et conséquence.

## 13.4 Déchets / PEMD / REP

Lorsqu'applicable : diagnostic, inventaire, réemploi, flux, tri, opérateur, transport, exutoire, coût, prise en charge, traçabilité et preuve finale. Les règles évolutives restent versionnées.

---

# 14. Production de l'offre et registre des engagements

Tout élément offrant un résultat, moyen, fréquence, délai, personne, matériel, marque, performance, stock, réunion, intervention, méthode, KPI environnement/social, outil ou reporting doit pouvoir devenir un **engagement** relié au texte offert, à la demande source, au coût, au planning, à la preuve de capacité et au responsable futur.

Un engagement critique non chiffré, non prouvé ou incompatible avec la capacité peut bloquer P4 ou exiger dérogation Patron lorsque le risque est arbitrable.

Les documents à produire, remplir, récupérer ou demander restent gérés selon l'Univers documentaire : titulaire, validité, modèle, signature, format, portée, sensibilité, échéance, conséquence et preuve de sortie.

---

# 15. Remise, dépôt et preuve

Le contrat v1.0 est conservé et renforcé :

- candidate exacte et immutable après autorisation sauf nouvelle version ;
- manifeste exhaustif ;
- signatures et P5 distincts ;
- export distinct du dépôt ;
- dépôt externe final humain en V1 ;
- preuve externe rapprochée du paquet/hash ;
- résultats `UNKNOWN/PARTIAL/NOT_PERFORMED` jamais convertis en succès ;
- une preuve de dépôt du mauvais paquet est un incident critique.

---

# 16. Paiement, trésorerie d'exécution et post-réception

## 16.1 Circuit de paiement

Le produit doit pouvoir représenter les acteurs et pièces qui conditionnent l'encaissement, et distinguer délai contractuel/légal de l'hypothèse prudente utilisée dans le cash-flow.

## 16.2 Post-réception

Les coûts de OPR, essais, mise en service, formation, DOE/DIUO, corrections, réserves, GPA, pièces de rechange, astreintes, garanties et clôture peuvent être intégrés au prix/marge avant GO lorsque matériels.

La marge estimée à la réception ne doit pas être présentée comme marge finale si des obligations significatives persistent.

---

# 17. Clarification, négociation, résultat et passation

## 17.1 P6

Chaque clarification, régularisation, négociation, BAFO, prolongation ou mise au point crée ou référence une nouvelle version et déclenche une analyse d'impact ciblée.

## 17.2 Attribution / rejet

Le dossier conserve notification, date, lots, classement/notes/motifs lorsqu'ils sont disponibles, attributaire/montant communicable, anomalies, délais et décisions de suivi. Toute décision contentieuse reste humaine/professionnelle.

## 17.3 P7 / dossier de passation obligatoire

Le chantier reçoit :

- contrat et hiérarchie ;
- offre finale/budget/hypothèses ;
- exclusions/réserves/interfaces ;
- engagements vendus ;
- partenaires ;
- planning ;
- garanties ;
- pénalités et sanctions ;
- assurance et prérequis HSE ;
- obligations environnement/social ;
- documents post-attribution ;
- conditions du GO ;
- circuit de paiement ;
- `RIGHT_PRESERVATION_EVENT` et échéances ;
- risques résiduels et responsables.

La passation doit être acceptée par les rôles prévus. Une ligne critique sans responsable, source ou état empêche de prétendre « passation complète ».

---

# 18. Retour d'expérience

Le REX rapproche prévu/réalisé : prix, heures, rendements, achats, partenaires, délai, cash, pénalités, révision, réserves, garanties, réclamations, marge et satisfaction.

Il capture aussi : droits préservés/perdus, OS/modifications, dérogations coûteuses, engagements difficiles, faux positifs réglementaires/HSE/assurance et coûts post-réception sous-estimés.

Aucun REX ne devient règle d'entreprise sans portée, contexte et validation.

---

# 19. UX et surfaces — impact du v2.0

Le catalogue C00–C16 et les 104 contrats de couverture restent la carte de navigation de référence jusqu'à sa révision. Le v2.0 **n'autorise pas Codex à inventer de nouvelles routes ou de nouveaux écrans sans mise à jour UX**.

Les nouveaux contrats doivent d'abord être matérialisés dans les surfaces existantes lorsque cohérent :

- C05 « À résoudre » : dérogations, sanctions, droits, prérequis et conditions ;
- C07 Décision : Carte d'Engagement, P2/P3/P4/P6/P7 et décisions ;
- C08 Prix : exposition pénalités, cash, prix/révision, coûts HSE/post-réception ;
- C09 Partenaires : assurance, vigilance, réserves, dépendances ;
- C10 Réponse : engagements mesurables ;
- C12 Résultat/passation : DGD, droits, réception, passation renforcée ;
- C13 Entreprise : assurances/capacités/règles validées ;
- C01 Accueil Patron : décisions de la Carte d'Engagement.

Toute modification qui change la structure C00–C16, les 104 contrats ou PUX exige une nouvelle version du catalogue UX.

---

# 20. IA, provenance et abstention

L'IA peut : extraire, classer, rechercher, rapprocher, suggérer des impacts et préparer des questions/brouillons.

L'IA ne peut seule : appliquer définitivement une règle juridique, déclarer une couverture d'assurance, calculer une échéance sans règle sourcée, franchir une porte, accepter une dérogation, fixer le prix, décider un recours, signer, déposer ou effacer un inconnu.

Pour les calculs déterministes de délai, sanction, formule de prix et cash : les paramètres peuvent être extraits/proposés par IA, mais le calcul final est effectué par logique déterministe versionnée à partir de paramètres validés.

---

# 21. Périmètre V1 v2.0

## 21.1 Indispensable V1

- identité/MFA/tenant/délégations et confidentialité existantes ;
- Affaire, DCE, versions, preuves, exigences, inconnus, contradictions ;
- MIRP et interfaces critiques ;
- P0–P7 et conditions ;
- couverture économique Patron : prix, marge, cash, capacités ;
- registre des engagements ;
- profil réglementaire minimal avec règles versionnées nécessaires aux pilotes ;
- reconstruction contractuelle minimale et dérogations critiques ;
- sanctions/pénalités critiques ;
- événements de préservation des droits nécessaires à la passation ;
- OS/modification et règlement des comptes au niveau nécessaire pour P7 ;
- assurance de principe avec abstention/escalade ;
- HSE/prérequis critiques ;
- engagement environnement/social mesurable lorsqu'exigé par le DCE ;
- candidate/manifeste/P5/export/dépôt humain/preuve ;
- P6 et P7 renforcé ;
- REX minimal ;
- Carte d'Engagement Patron ;
- tests de sécurité, tenant, confidentialité, unknown/partial et non-régression métier.

## 21.2 V1.x / qualification ultérieure

- packs sectoriels complets ;
- portefeuille multi-affaires avancé ;
- automatisation/connecteurs de portails ;
- partenaires/groupements avec mandats complexes et workflows externes ;
- corpus privé exhaustif ;
- contrôle réglementaire spécialisé multi-domaines au-delà des pilotes ;
- administration avancée ;
- automatisation juridique autonome — **non prévue tant que la doctrine produit reste inchangée**.

## 21.3 Hors promesse sans qualification

- « conformité juridique garantie » ;
- « toutes les pénalités détectées » ;
- « aucune hallucination » ;
- « couverture assurance certifiée » ;
- « aucun droit ne sera perdu » ;
- « rentabilité garantie » ;
- « toutes les normes/DTU disponibles » ;
- « dépôt automatique fiable ».

---

# 22. Validations externes obligatoires

Avant blocage automatique ou promesse publique sur les sujets concernés :

- juriste commande publique ;
- juriste construction privée + corpus privé ;
- DAF BTP ;
- courtier/assureur construction ;
- QSE / spécialiste amiante et autres sujets sensibles ;
- métreurs/conducteurs par corps d'état pour MIRP ;
- essais réels de dépôt ;
- banc formats/plans ;
- corpus Golden DCE annoté ;
- accessibilité/RGPD/sécurité lorsque la promesse l'exige.

Une validation externe doit avoir date, périmètre, version de règle et preuve ; elle n'est pas remplacée par une opinion de LLM.

---

# 23. Recettes métier obligatoires du v2.0

Les recettes historiques restent applicables. Ajouter au minimum :

- REC-29 versions CCAG différentes ;
- REC-30 dérogation au régime de pénalités ;
- REC-31 OS non valorisé ;
- REC-32 décompte / délai de réclamation ;
- REC-33 exécution aux frais et risques ;
- REC-34 engagement environnemental vendu ;
- REC-35 applicabilité réglementaire date/usage ;
- REC-36 RAT infrastructure ;
- REC-37 assurance hors activité déclarée ;
- REC-38 prérequis HSE sans ressource ;
- REC-39 circuit de facturation public ;
- REC-40 règle future ;
- REC-41 DGD tacite uniquement si conditions prouvées ;
- REC-42 pénalités cumulatives ;
- REC-43 engagement mémoire non chiffré ;
- REC-44 portefeuille cash ;
- REC-45 rectificatif modifiant un délai/droit.

Chaque recette échoue si le bon résultat est obtenu sans preuve consultable, avec fuite de confidentialité ou par conclusion non sourcée.

---

# 24. Critères de qualification métier

Mesurer séparément :

- rappel des exigences critiques ;
- précision/faux positifs ;
- source/locator ;
- préservation des inconnus ;
- contradictions ;
- dérogations ;
- sanctions/pénalités ;
- conditions GO ;
- droits/échéances contractuelles ;
- couverture du prix et cash ;
- capacité ;
- séparation Patron/Collaborateur/tenant ;
- engagement offre → passation ;
- candidate autorisée → preuve de dépôt ;
- compréhension du dossier P7 par le conducteur.

**Zéro tolérance** sur : fuite financière inter-rôles/tenant, mauvaise version autorisée, faux reçu, conclusion juridique inventée, délai contractuel affiché comme certain sans source, engagement critique silencieusement perdu.

---

# 25. Contrat de changement et traçabilité

Toute modification qui change rôle, porte, état, source de vérité, classification, déduction autorisée, engagement, preuve attendue, objet métier ou périmètre vendu exige :

1. nouvelle version du Product Freeze ou ADR relié ;
2. impact catalogue UX/parcours ;
3. impact cahier technique, migrations et API ;
4. tests de refus, confidentialité, idempotence, inconnus et régression métier ;
5. revue propriétaire.

Une technologie peut changer sans rouvrir le Product Freeze si elle respecte exactement ces contrats.

Aucune spécification technique, maquette, migration ou code ne peut créer silencieusement un nouveau droit ou réduire une exigence du présent document.

---

# 26. Règle de dérivation vers Codex

Après promotion propriétaire :

```text
MASTER MÉTIER v2.0
      ↓ couverture sémantique contrôlée
PRODUCT FREEZE v2.0
      ↓ contrats techniques
CAHIER TECHNIQUE D'EXÉCUTION v2.1
      ↓ audit du code réel
MATRICE KEEP / ADAPT / REPLACE / DELETE / ABSENT
      ↓ migrations + plan de PR
CODE + TESTS + PREUVES
```

Codex doit commencer par un audit READ-ONLY du code actuel. Il n'est pas autorisé à créer les nouvelles tables, routes ou surfaces avant d'avoir produit la cartographie d'existant, le delta, les migrations proposées, les tests de refus et le rollback.

Le code et les tests sont la preuve de ce qui est effectivement implémenté ; ils ne redéfinissent jamais le métier.

---

# 27. Références normatives après promotion

1. `SMART_AO_CAHIER_DIRECTEUR_METIER_MASTER_v2.0.md` — source de profondeur métier et documentaire ;
2. présent `SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v2.0.md` — autorité produit/métier ;
3. catalogue UX actif, à réviser uniquement pour les impacts de surface nécessaires ;
4. fondations UX actives ;
5. `SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v2.1.md` — traduction technique ;
6. architecture logicielle active + ADR de delta si nécessaire ;
7. code/tests/migrations — état effectivement implémenté.

Le MASTER n'est pas une seconde autorité contradictoire : il conserve la profondeur et sert de source de traçabilité ; le Freeze v2.0 décide ce qui devient contrat produit codable.

---

# 28. Promotion

**État actuel : PROMU.**

Le propriétaire a confirmé la promotion du Product Freeze v2.0. Le v1.0 est historique, l'index des références actives est réaligné et le cahier technique v2.1 dérive désormais de cette autorité. Codex peut passer de l'audit à l'implémentation uniquement selon les gates approuvés, les validations externes prévues et les tranches T1–T8.
