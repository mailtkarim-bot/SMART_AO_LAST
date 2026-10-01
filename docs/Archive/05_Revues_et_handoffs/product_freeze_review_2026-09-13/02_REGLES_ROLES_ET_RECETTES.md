# SMART AO — Règles fonctionnelles, rôles et recettes proposés

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

## Références citées

[^1]: [Remettre la réponse et échanger avec l'acheteur](https://entreprendre.service-public.gouv.fr/vosdroits/F32106). Type, date et limites : registre des sources du dossier, entrée 1.
[^2]: [Préparer le dossier de candidature](https://entreprendre.service-public.gouv.fr/vosdroits/F32144). Type, date et limites : registre des sources du dossier, entrée 2.
[^3]: [Préparer le dossier offre](https://entreprendre.service-public.gouv.fr/vosdroits/F32154). Type, date et limites : registre des sources du dossier, entrée 3.
[^4]: [Groupement et sous-traitance](https://entreprendre.service-public.gouv.fr/vosdroits/F32137). Type, date et limites : registre des sources du dossier, entrée 4.
[^5]: [R2151-6](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000037730533). Type, date et limites : registre des sources du dossier, entrée 5.
[^6]: [R2151-4](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000037730539). Type, date et limites : registre des sources du dossier, entrée 6.
[^7]: [Questions-réponses copie de sauvegarde](https://www.economie.gouv.fr/files/files/directions_services/daj/marches_publics/dematerialisation/QR-Copie-sauvegarde.pdf). Type, date et limites : registre des sources du dossier, entrée 7.
[^9]: [Guide pratique des prix, édition 2023](https://www.economie.gouv.fr/daj/publication-de-la-version-2023-du-guide-pratique-de-loecp-le-prix-dans-les-marches-publics). Type, date et limites : registre des sources du dossier, entrée 9.
[^10]: [Obtenir une attestation de vigilance](https://entreprendre.service-public.gouv.fr/vosdroits/F31422). Type, date et limites : registre des sources du dossier, entrée 10.
[^11]: [Obtenir et vérifier une attestation](https://www.urssaf.fr/accueil/attestation-vigilance.html). Type, date et limites : registre des sources du dossier, entrée 11.
[^12]: [Modèle d'attestation décennale](https://entreprendre.service-public.gouv.fr/vosdroits/R44868). Type, date et limites : registre des sources du dossier, entrée 12.
[^13]: [Recourir à la sous-traitance](https://entreprendre.service-public.gouv.fr/vosdroits/F36261). Type, date et limites : registre des sources du dossier, entrée 13.
[^14]: [Considérations environnementales et sociales : nouvelles exigences](https://www.economie.gouv.fr/daj/considerations-environnementales-et-sociales-dans-les-marches-publics-publication-de-fiches-pratiques-pour-repondre-aux-nouvelles-exigences-de-la). Type, date et limites : registre des sources du dossier, entrée 14.
[^15]: [Gérer les habilitations](https://www.cnil.fr/fr/securite-gerer-les-habilitations). Type, date et limites : registre des sources du dossier, entrée 15.
[^16]: [Tracer les opérations](https://www.cnil.fr/fr/securite-tracer-les-operations). Type, date et limites : registre des sources du dossier, entrée 16.
[^17]: [Gérer la sous-traitance](https://www.cnil.fr/fr/securite-gerer-la-sous-traitance). Type, date et limites : registre des sources du dossier, entrée 17.
[^18]: [Durées de conservation](https://www.cnil.fr/fr/passer-laction/les-durees-de-conservation-des-donnees). Type, date et limites : registre des sources du dossier, entrée 18.
[^19]: [Authentification multifacteur et mots de passe](https://messervices.cyber.gouv.fr/guides/recommandations-relatives-lauthentification-multifacteur-et-aux-mots-de-passe). Type, date et limites : registre des sources du dossier, entrée 19.
[^20]: [Questions-réponses sur l'IA générative](https://cnil.fr/fr/les-questions-reponses-de-la-cnil-sur-lutilisation-dun-systeme-dia-generative). Type, date et limites : registre des sources du dossier, entrée 20.
[^21]: [Sécurité d'un système d'IA générative](https://messervices.cyber.gouv.fr/guides/recommandations-de-securite-pour-un-systeme-dia-generative). Type, date et limites : registre des sources du dossier, entrée 21.
[^22]: [RGAA](https://accessibilite.numerique.gouv.fr/). Type, date et limites : registre des sources du dossier, entrée 22.
[^23]: [Gérer les incidents et violations](https://www.cnil.fr/fr/securite-gerer-les-incidents-et-les-violations). Type, date et limites : registre des sources du dossier, entrée 23.
[^24]: [Questions-réponses règlement IA](https://cnil.fr/fr/entree-en-vigueur-du-reglement-europeen-sur-lia-les-premieres-questions-reponses-de-la-cnil). Type, date et limites : registre des sources du dossier, entrée 24.
