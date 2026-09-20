# SMART AO — Univers documentaire métier

**Version de référence : 1.0 — 12 septembre 2026**  
**Statut : référentiel documentaire métier stabilisé**

Ce document décrit les pièces, preuves, informations minimales et décisions documentaires nécessaires à une PME BTP pour étudier et remettre une offre défendable. Il complète le [cahier des charges métier v1.0](/home/noor/PROJECTS/BTP/SMART_AO_V8/rapports/SMART_AO_Cahier_des_charges_Metier_v1.0.md). Il ne constitue ni une architecture informatique ni une liste fermée de documents.

Les affirmations portent l’un des trois statuts suivants : **ÉTABLI** par un texte, une source officielle ou le corpus ; **HYPOTHÈSE MÉTIER** à tester sur des cas réels ; **VALIDATION EXTERNE** lorsqu’un expert, une licence ou un corpus complémentaire est nécessaire.

## 1. Décision métier

SMART AO doit piloter la chaîne documentaire complète d’une affaire BTP. Pour une consultation donnée, il doit pouvoir répondre à cinq questions distinctes :

1. **Le DCE contient-il les informations nécessaires pour comprendre et chiffrer raisonnablement les travaux ?**
2. **Quelles pièces l’entreprise doit-elle remettre, à quelle phase et selon quel modèle ?**
3. **Quelles pièces SMART AO peut-il produire ou préremplir à partir de données validées ?**
4. **Quelles preuves doivent provenir de l’entreprise, d’une autorité ou d’un tiers ?**
5. **Le paquet exact remis à l’acheteur correspond-il à la version autorisée de l’offre ?**

Il n’existe pas de liste nationale fermée des documents à remettre. Le Code de la commande publique définit les documents de la consultation comme l’ensemble des documents fournis par l’acheteur ou auxquels il se réfère pour définir son besoin et la procédure. Le règlement et les autres pièces peuvent imposer des documents supplémentaires permettant d’apprécier l’offre, y compris des échantillons, maquettes ou prototypes.[^1][^2] Une offre qui ne respecte pas les exigences de la consultation, notamment parce qu’elle est incomplète, est irrégulière ; sa régularisation n’est ni automatique ni toujours possible.[^3]

Le modèle métier retenu est donc :

```text
RÉFÉRENTIEL DOCUMENTAIRE STANDARD
        +
DÉCOUVERTE DYNAMIQUE DANS TOUTES LES PIÈCES ET VERSIONS DU DCE
        +
EXIGENCES MINIMALES D’INFORMATION POUR ÉTABLIR LE PRIX
        +
PATRIMOINE DOCUMENTAIRE VALIDÉ DE L’ENTREPRISE ET DE SES PARTENAIRES
        =
REGISTRE DOCUMENTAIRE ET MANIFESTE DE REMISE PROPRES À L’AFFAIRE
```

Le résultat attendu dépasse une checklist. Chaque document devient un objet de décision relié à une source, une phase, un lot, un responsable, un mode d’obtention, une validité et une conséquence s’il manque.

## 2. Périmètre et méthode

Cette étude constitue le référentiel documentaire spécialisé du [cahier des charges métier v1.0](/home/noor/PROJECTS/BTP/SMART_AO_V8/rapports/SMART_AO_Cahier_des_charges_Metier_v1.0.md). Elle ne décrit ni base de données, ni service logiciel, ni choix de modèle d’IA.

Elle repose sur :

- le corpus [DCE Type](/home/noor/PROJECTS/BTP/DOCUMENTATION/SMART_AO%20DOCUMENTATION/DCE%20Type), soit 379 fichiers au niveau des dossiers et 140 fichiers supplémentaires contenus dans une archive ZIP et une archive 7z ;
- l’extraction textuelle de 212 documents PDF, DOC, DOCX, XLSX et ODT ; deux grands plans ont dépassé la limite d’extraction, un plan était sans texte exploitable et un ancien formulaire DOC était vide à l’extraction ;
- l’inventaire des 152 classeurs XLS historiques et des 55 classeurs XLSX supplémentaires contenus dans le BPU AP-HP ;
- une recherche ciblée dans toutes les pièces pour les expressions d’obligation documentaire et les familles de livrables ;
- les sources officielles françaises à jour consultées le **11 septembre 2026** ;
- une veille des éditeurs français et étrangers sur la production et le contrôle des dossiers de réponse.

### 2.1 Résultats mesurés dans le corpus

Les occurrences ci-dessous servent à démontrer la dispersion des exigences. Elles ne représentent pas un nombre de documents obligatoires : un mot peut apparaître dans une pièce fournie, une exigence d’offre ou un livrable d’exécution.

| Famille recherchée | Occurrences | Documents concernés |
|---|---:|---:|
| Formulations « à fournir/joindre/remettre/compléter » | 279 | 52 |
| Mémoire ou cadre de réponse technique | 60 | 24 |
| BPU, DPGF, DQE, décomposition ou sous-détail | 153 | 35 |
| Visite ou attestation de visite | 35 | 10 |
| Planning, calendrier ou phasage | 132 | 35 |
| Échantillon, prototype, maquette ou catalogue | 615 | 58 |
| CV, organigramme, moyens ou qualifications | 199 | 40 |
| Environnement, déchets, réemploi ou PEMD | 486 | 55 |
| Insertion ou heures sociales | 140 | 12 |
| RGPD, données personnelles ou cybersécurité | 13 | 6 |
| Assurance | 52 | 26 |
| Signature | 72 | 24 |
| Amiante, plomb ou diagnostic avant travaux | 3 641 | 66 |
| Géotechnique, sondage ou étude de sol | 961 | 31 |
| Topographie, réseaux ou DT-DICT | 13 | 6 |
| PGC SPS, PPSPS ou coordination SPS | 98 | 29 |
| DOE, DIUO, exécution, calcul ou mise en service | 211 | 34 |

L’analyse a également rencontré des formats anciens, scans, fichiers graphiques lourds, tableurs structurés, fichiers protégés ou susceptibles de contenir des macros, ZIP imbriqué, 7z, bases système inutiles et documents sans couche texte. « Présent » ne signifie donc ni « lisible », ni « exploitable », ni « suffisant pour chiffrer ».

## 3. Les quatre univers documentaires

### 3.1 Documents fournis ou référencés par l’acheteur

Ils décrivent le besoin, le contrat et la procédure : avis, RC, AE ou projet de marché, CCAP/CCP, CCTP et prescriptions communes, plans, détails, BPU/DPGF/DQE vierges, calendriers, diagnostics, études, annexes et réponses aux questions.

SMART AO doit les inventorier, reconnaître leur version, détecter les renvois vers une pièce absente et distinguer :

- pièce contractuelle ou destinée à le devenir ;
- information de consultation ;
- modèle à remplir ;
- donnée indicative ou non contractuelle ;
- pièce remplacée par un rectificatif ;
- référence externe à consulter licitement ;
- document technique incomplet ou illisible.

### 3.2 Documents à remettre par le candidat ou le soumissionnaire

Ils couvrent candidature, offre administrative, prix, technique, environnement, social, annexes et preuves. Leur liste est ouverte et propre à la consultation. Une même famille change de statut selon le DCE : l’acte d’engagement peut être demandé signé avec l’offre, prérempli sans signature, ou transmis uniquement à l’attributaire pressenti. Le planning peut être fourni par l’acheteur, noté dans l’offre ou dû après notification.

### 3.3 Preuves externes que SMART AO ne fabrique pas

Elles proviennent d’une administration, d’un assureur, d’une banque, d’un certificateur, d’un client, d’un fabricant, d’un laboratoire, d’un fournisseur ou d’un partenaire. SMART AO peut les réclamer, contrôler, classer et joindre lorsque le DCE le demande. Il ne peut ni les créer, ni prolonger leur validité, ni modifier leur titulaire ou leur portée.

### 3.4 Documents nécessaires à l’étude ou au prix

Ils permettent à l’entreprise de mesurer quantités, méthode, moyens, interfaces et risques. Ils ne sont pas toujours légalement obligatoires et ne sont pas nécessairement à remettre. Leur absence peut pourtant rendre un prix dangereux : étude de sol, repérage amiante, plans de réseaux, diagnostic de structure, relevé topographique, phasage de site occupé ou données de puissance électrique.

SMART AO doit appliquer une question simple :

> **Peut-on établir un prix fiable et une méthode réalisable sans cette donnée ?**

Si la réponse est non, l’absence produit un blocage de chiffrage, une question à l’acheteur, une hypothèse approuvée par le dirigeant ou un NO-GO.

## 4. Registre des exigences documentaires

Chaque affaire possède un registre unique, alimenté par le référentiel standard puis enrichi par la découverte du DCE. Une entrée représente un document complet, une annexe, un tableau, une preuve, un échantillon matériel ou un livrable attendu.

### 4.1 Fiche métier minimale

| Champ | Question couverte |
|---|---|
| Intitulé normalisé | Quel document ou livrable est attendu ? |
| Intitulé exact acheteur | Comment est-il nommé dans le DCE ? |
| Raison | Candidature, notation, engagement, chiffrage, contrat, exécution ou réception ? |
| Source de l’exigence | Pièce, version, page/section/cellule et extrait exact |
| Autres sources | Exigence répétée, précisée ou contredite ailleurs ? |
| Portée | Consultation, lot, site, bâtiment, phase, tranche, PSE, variante ou groupement |
| Moment requis | Candidature, offre, attributaire pressenti, avant démarrage, exécution, réception/DOE |
| Condition | Toujours, si candidat seul/groupé, si variante, si sous-traitant, si travaux concernés, etc. |
| Émetteur attendu | Entreprise, acheteur, administration, assureur, banque, certificateur, fabricant, partenaire |
| Titulaire | Entreprise, établissement, salarié, matériel, produit, sous-traitant ou cotraitant concerné |
| Mode de traitement | Remplir modèle, générer, récupérer, demander, compléter manuellement, signer, remettre physiquement |
| Données sources | Données d’entreprise, décision, DCE, devis, CV, prix, métrés, preuve tierce |
| Modèle imposé | Fichier et version à préserver |
| Signature | Non, requise, facultative, à l’attribution ou indéterminée |
| Format final | DOCX, XLSX, PDF, XML, support physique, archive ou autre format autorisé |
| Nom et emplacement | Nom exact et position dans le pli/manifeste |
| Validité | Date d’émission, expiration, période couverte et date minimale requise |
| Sensibilité | Public interne, affaire, direction, données personnelles, prix/marge, bancaire |
| Responsable | Producteur, contrôleur, valideur et signataire |
| Échéance interne/externe | Date de disponibilité et date de remise |
| État | Statut normalisé du cycle documentaire |
| Criticité | C1 : élimination, prix ou engagement majeur ; C2 : décision requise ; C3 : information utile |
| Conséquence d’absence | Irrégularité, perte de points, prix incertain, engagement impossible, retard ou autre risque |
| Action suivante | Produire, demander, corriger, questionner, accepter l’hypothèse ou abandonner |
| Preuve de sortie | Version, empreinte, validation, signature et reçu de remise |

### 4.2 États du cycle

```text
DÉTECTÉ → QUALIFIÉ → AFFECTÉ → EN ATTENTE DE DONNÉES → EN PRODUCTION
        → À CONTRÔLER → À VALIDER → À SIGNER → PRÊT
        → INCLUS AU MANIFESTE → REMIS → ACCUSÉ
```

États d’exception : **absent du DCE**, **introuvable en interne**, **illisible**, **incomplet**, **expiré**, **hors portée**, **mauvais titulaire**, **mauvais modèle**, **remplacé**, **contradictoire**, **non applicable**, **dérogation à décider**, **bloqué**.

Un document n’est jamais « valide » uniquement parce qu’un fichier porte le bon nom. La validité combine contenu, titulaire, portée, date, modèle, version, format, signature et contrôle humain.

### 4.3 Vocabulaire commun de référence

| Terme | Définition documentaire retenue |
|---|---|
| Exigence | élément demandé, imposé ou nécessaire, conservé avec formulation source, portée et criticité |
| Preuve | élément vérifiable soutenant une conclusion, une capacité, une conformité ou une remise |
| Engagement | promesse mesurable ou obligation acceptée, reliée au coût, à la phase et au responsable lorsqu’ils existent |
| Phase | candidature, offre, attributaire, préparation, exécution ou réception/DOE |
| Criticité | C1 : élimination, prix ou engagement majeur ; C2 : décision requise ; C3 : information utile |
| Preuve tierce | document émis ou détenu par une autorité, un assureur, un client ou un autre tiers que SMART AO ne fabrique pas |
| Blocage | impossibilité de poursuivre sans preuve, correction ou dérogation nominative |
| Validation | décision humaine nommée autorisant l’usage d’un résultat pour une étape donnée |
| Applicabilité | portée selon l’affaire, l’entreprise, le lot, le site, la phase, l’option, le rôle et le cadre contractuel |
| MIRP | minimum d’informations requises pour établir un prix défendable, qualifié R, C, P1, P2 ou P3 |

Le [tableau de cohérence du cahier métier](/home/noor/PROJECTS/BTP/SMART_AO_V8/rapports/SMART_AO_Cahier_des_charges_Metier_v1.0.md#29-cohérence-avec-lunivers-documentaire-métier-v10) conclut à une divergence mineure sur la criticité, désormais levée par cette définition. Les doublons restants sont utiles : ici la notion est portée par une pièce ; dans le cahier métier elle sert une décision d’entreprise.

## 5. Classification commune produire–remplir–récupérer–demander

| Code métier | Signification | Exemple | Limite de SMART AO |
|---|---|---|---|
| ACHETEUR_FOURNI | Pièce mise à disposition ou référencée | CCTP, plans, diagnostic | Inventorier, lire, signaler manque/illisibilité |
| ACHETEUR_ATTENDU | Donnée nécessaire qui devrait venir du projet | repérage amiante applicable, plans existants | Demander ou faire approuver une hypothèse ; ne pas fabriquer |
| REMPLIR_MODÈLE | Modèle acheteur à conserver | CRT, DPGF, questionnaire | Remplir sans altérer structure, formules ni consignes |
| GÉNÉRER | Aucun modèle imposé | mémoire libre, note méthodologique | Produire depuis sources validées |
| GÉNÉRER_SOUS_VALIDATION | Le contenu dépend d’une décision | planning engagé, taux de réemploi | Préparer puis bloquer jusqu’à validation responsable |
| BIBLIOTHÈQUE_ENTREPRISE | Preuve ou contenu réutilisable | référence, CV, assurance | Sélectionner la version applicable ; ne pas transformer |
| DOCUMENT_TIERS | Preuve à obtenir | fiscal, social, banque, fabricant | Relancer et vérifier ; génération interdite |
| PARTENAIRE | Pièce d’un cotraitant/sous-traitant | DC4, capacité, assurance | Conserver titulaire et responsabilité propres |
| MANUEL | Saisie ou geste non automatisable de manière sûre | déclaration spécifique, échantillon | Guider, tracer et contrôler |
| SIGNER | Signature d’une personne habilitée | AE si requis, DC4 selon stade | Préparer et vérifier pouvoir ; ne pas signer sans autorité |
| SUPPORT_PHYSIQUE | Remise hors plateforme | échantillon, prototype | Organiser étiquetage, lieu, délai et récépissé |
| POST_ATTRIBUTION | Document non remis avec l’offre mais à anticiper | PPSPS, plans EXE, DOE | Chiffrer et transmettre à l’exécution |

Un même document peut cumuler plusieurs codes. Un CRT est **REMPLIR_MODÈLE**, **GÉNÉRER_SOUS_VALIDATION** et éventuellement **SIGNER**. Une attestation d’assurance est **DOCUMENT_TIERS** et **BIBLIOTHÈQUE_ENTREPRISE**.

## 6. Catalogue documentaire métier extensible

Le catalogue décrit les familles connues. Il ne remplace jamais la lecture dynamique du DCE.

### 6.1 Pièces fournies par l’acheteur ou le maître d’ouvrage

| Famille | Contenu possible | Contrôles SMART AO |
|---|---|---|
| Publicité et procédure | avis, invitation, RC, calendrier, questions-réponses, rectificatifs | cohérence objet/lot/date, version, visite, canal, formats, critères et pièces attendues |
| Engagement et contrat | AE/ATTRI1, projet de marché, CCAP/CCP, CCAG cité, annexes, clauses RGPD | hiérarchie, signature, dérogations, données à compléter, pièces à joindre ou accepter |
| Technique | CCTP, CCTC, spécifications, programmes, notices, fiches de site | périmètre, performances, interfaces, livrables offre/exécution, normes citées |
| Prix | BPU, DPGF, DQE/DE, bordereaux, simulations, affaires fictives, catalogues | modèle original, cellules autorisées, formules, totalité des lignes, scénarios et formats |
| Graphique et numérique | plans, coupes, détails, synoptiques, DWG/DXF, IFC/BIM, SIG, photos | inventaire des feuilles, indices, échelles, repères, liens vers exigences et quantités |
| Calendrier et logistique | planning directeur, phasage, plan d’installation, contraintes d’accès | jalons, site occupé, coupures, coactivité, heures autorisées, emprises |
| Sol et existants | topographie, bornage, géotechnique, sondages, structure, réseaux, recollement | zone couverte, date, limites, hypothèses, investigations complémentaires |
| Risques sanitaires | amiante, plomb, radon, pollution, agents biologiques, diagnostics divers | périmètre réellement investigué, parties inaccessibles, date, travaux concernés |
| Sécurité et contrôle | PGC/PGCSPS, RICT, rapports de bureau de contrôle, SSI, incendie | prescriptions, avis suspendus/défavorables, documents à produire et coûts induits |
| Environnement | étude d’impact, autorisations, PEMD, données déchets/terres, acoustique, hydraulique | seuil/applicabilité, mesures compensatoires, filières, suivi et livrables |
| Exploitation | procédures du site, hygiène, sûreté, continuité, permis de travail, consignation | contraintes par site, habilitations, délais d’accès, astreinte et interlocuteurs |
| Annexes de réponse | trame mémoire/CRT, questionnaires, fiches CV/matériel, tableau références | obligation, notation, modèle, nombre par lot, limites de pages et justificatifs |

L’article R. 2132-1 exige des informations assez précises pour permettre aux opérateurs de déterminer la nature et l’étendue du besoin et de décider de participer.[^1] Cette exigence juridique ne permet pas au logiciel de conclure automatiquement qu’une donnée technique particulière doit toujours exister ; elle justifie de signaler ce qui empêche une décision ou un prix raisonnable.

### 6.2 Candidature et capacité

L’arrêté du 22 mars 2019 encadre les renseignements et documents que l’acheteur peut demander pour apprécier les capacités économiques, financières, techniques et professionnelles.[^4] Les formulaires DAJ sont des modèles actualisés, mais le DCE détermine ce qui est exigé dans la procédure.[^5]

| Document ou information | Phase habituelle | Mode | Points de contrôle |
|---|---|---|---|
| DUME | candidature | remplir service ou fichier fourni | entreprise/membre, exclusions, capacités, lots, réutilisation et date |
| DC1 | candidature | préremplir modèle DAJ/acheteur | candidat, membres, lots, mandataire, habilitations, déclaration |
| DC2 | candidature, un par opérateur | préremplir + joindre preuves | identité, SIRET, forme, pouvoirs, CA, effectifs, capacité et annexes |
| DC4 | offre, attribution ou exécution selon cas | remplir modèle applicable | sous-traitant, prestations, montant, paiement, signature et agrément |
| Déclaration sur l’honneur | candidature ou attributaire selon texte/DCE | modèle acheteur ou rédaction contrôlée | texte exact, périmètre, signataire et date |
| Pouvoir du signataire | candidature/offre/attribution | bibliothèque ou tiers interne | personne, société, délégation, limites, durée et chaîne de pouvoir |
| Extrait d’immatriculation / identifiant | selon DCE et attribution | source officielle ou donnée vérifiable | établissement, statut, actualité ; ne pas imposer une durée universelle |
| Jugement de redressement | candidature si concerné | document juridictionnel | capacité à poursuivre l’activité pendant l’exécution |
| Chiffres d’affaires | candidature | DC2/tableau acheteur/comptes | exercices disponibles, global/domaine, unité et entité concernée |
| Bilans ou extraits | candidature si demandé et applicable | document comptable validé | années, confidentialité, entité et cohérence avec CA |
| Déclaration ou attestation bancaire | si demandé | tiers bancaire | objet, date, titulaire, formulation demandée |
| Assurance des risques professionnels | candidature/attribution | tiers assureur | activité, garanties, plafond, zone, période, exclusions |
| Références de travaux | candidature/offre | tableau acheteur ou fiche | objet comparable, montant, date, destinataire, rôle exact, autorisation d’usage |
| Attestation de bonne exécution | si demandée | tiers client/MOE | titulaire, prestation, dates, montant, résultat et signature |
| Effectifs et encadrement | candidature/offre | cadre acheteur | années, catégories, intérim/salariés, cohérence avec moyens proposés |
| CV, titres et diplômes | capacité ou offre | modèle acheteur/bibliothèque | consentement, actualité, rôle, disponibilité, anonymisation si permise |
| Qualifications/certifications | capacité/offre | organisme tiers | code exact, niveau, établissement titulaire, validité et équivalence admise |
| Moyens matériels | capacité/offre | tableau/texte | propriété/location, disponibilité, caractéristiques et affectation réelle |
| Qualité/environnement | capacité/offre | certificats ou moyens équivalents | périmètre, organisme, version, équivalence et application au lot |
| Chaîne d’approvisionnement | capacité/offre | déclaration/preuve partenaire | source, délai, dépendance, stock et engagement du tiers |
| Capacité d’un tiers | candidature | engagement écrit + preuves du tiers | ressources réellement mises à disposition et durée |
| Pièces de chaque cotraitant | candidature | propre à chaque membre | aucune fusion abusive des titulaires, pouvoirs et capacités |

Les renseignements autorisés incluent notamment chiffre d’affaires, banques ou assurance, bilans, travaux exécutés, effectifs, techniciens, moyens, qualité, environnement, chaîne d’approvisionnement, échantillons et certificats.[^4] SMART AO doit comparer l’exigence réelle à cette base et signaler une demande atypique pour examen, sans rendre un avis juridique automatique.

### 6.3 Offre administrative et contractuelle

| Document | Variantes rencontrées | Comportement attendu |
|---|---|---|
| Acte d’engagement / ATTRI1 | joint au DCE, demandé complété, signé avec l’offre ou seulement à l’attribution | suivre exclusivement le RC et les rectificatifs ; vérifier prix, lots, membres, compte et signataire |
| Acceptation CCAP/CCTP | simple adhésion par l’offre ou pièces datées/signées à remettre | ne jamais joindre par habitude ; respecter la liste exacte |
| Attestation de visite | obligatoire, facultative, dispense conditionnelle, une par site | contrôler identité, date, lot, représentant, preuve ou motif de dispense |
| Déclaration de sous-traitance | sous-traitant présenté, envisagé ou ajouté après attribution | relier DC4, offre du sous-traitant, capacité, paiement et validations |
| Engagement insertion | formulaire, volume d’heures, méthode ou organisme facilitateur | cohérence heures–planning–prix–personnel et lot applicable |
| Engagement environnemental | questionnaire, charte, SOGED/SOPRE, taux ou indicateurs | transformer chaque réponse notée en engagement chiffré et transmissible |
| Annexe RGPD/cybersécurité | clauses à compléter, questionnaire, mesures et sous-traitants | validation par responsable compétent ; aucune promesse générique non vérifiée |
| RIB/IBAN | parfois offre, souvent attribution/facturation | document restreint, titulaire cohérent avec candidat et compte contractuel |
| Variante/PSE/tranche | acte, annexe et prix séparés | manifeste et contrôles propres à chaque combinaison |
| Dérogation/réserve autorisée | tableau imposé ou note | décision nominative, impact prix/notation/recevabilité et formulation contrôlée |

La signature n’est pas présumée. Dans le corpus, l’AP-HP impose une signature électronique de l’AE dans l’offre, alors que Filieris l’encourage au dépôt puis l’exige à l’attribution. Le service public rappelle que la réponse comporte candidature et offre et que les règles de dépôt viennent du profil et des documents de la consultation.[^6]

### 6.4 Documents financiers

| Famille | Fonction | Contrôles métier |
|---|---|---|
| BPU | prix unitaires contractuels | toutes lignes attendues, unité, prix, décimales, cohérence avec mémoire et fournisseurs |
| DQE/DE | simulation avec quantités estimées | formule de calcul, postes BPU, quantités non modifiées, total et caractère contractuel ou non |
| DPGF | décomposition d’un prix global forfaitaire | couverture du CCTP, quantités indicatives, cellules vides, sous-totaux et total AE |
| Sous-détail de prix | justification d’un prix ou poste | déboursé, rendement, frais, cohérence et confidentialité |
| Bordereau de remise/coefficient | application à catalogue ou base | périmètre de la remise, version du tarif, date et formule |
| Catalogue/tarif | référence des produits/prix | version, articles couverts, évolution et licence d’usage |
| Affaire fictive/panier-type | simulation de commandes | scénario, quantités, rattachement BPU et formule de notation |
| Prix de variante/PSE/tranche | prix alternatif ou optionnel | autonomie économique, impacts communs, validité et total correspondant |
| Cadre de coût environnemental | coût carbone/cycle de vie ou données transport | méthode imposée, preuves et absence de double comptage |

Service Public distingue notamment BPU et DPGF et rappelle que l’offre financière doit être établie à partir des cadres de la consultation.[^7] Dans le corpus GHUC, chaque site et chaque corps d’état possède un BPU et une affaire fictive ; cette volumétrie interdit de traiter le prix comme un seul tableur annexe.

SMART AO doit préserver : noms des feuilles, ordre des lignes, formules, protections, cellules fusionnées, listes de validation, unités, formats numériques, colonnes cachées, liens, commentaires et éventuelles macros autorisées. Il ne renseigne que les cellules identifiées comme saisissables. Toute conversion susceptible d’altérer le calcul produit une copie de travail et conserve l’original intact.

### 6.5 Offre technique et mémoire

La page officielle de préparation de l’offre cite offre technique, offre financière et autres pièces comme planning, catalogue, échantillon, maquette ou prototype ; l’absence d’une pièce demandée peut rendre l’offre irrégulière.[^2]

| Famille | Livrables possibles |
|---|---|
| Compréhension | note de compréhension, enjeux, contraintes, risques, interfaces et propositions |
| Organisation | organigramme, rôles, gouvernance, contacts, délégations et continuité |
| Moyens humains | effectifs, CV, compétences, habilitations, disponibilité, astreinte |
| Moyens matériels | parc, outillage, véhicules, logiciels, stocks, moyens provisoires |
| Méthodes | modes opératoires, procédures, séquences, contrôles, rendements et interfaces |
| Planning | calendrier, phasage, jalons, chemin critique, approvisionnements, études et visas |
| Site occupé | accès, zonage, confinement, nuisances, continuité, communication, hygiène et sûreté |
| Qualité | SOPAQ/PAQ, autocontrôles, points d’arrêt, traçabilité, non-conformités |
| Sécurité | analyse des risques, organisation, prévention, urgence, consignations, SPS |
| Environnement | déchets, réemploi, filières, transports, énergie, carbone, produits et nuisances |
| Social | insertion, apprentissage, égalité, emploi local et suivi des engagements |
| Produits | fiches, performances, équivalences, certificats, échantillons et provenance |
| Études | EXE, synthèse, BIM, calculs, visas, relevés et processus de modification |
| Essais/réception | essais, mise en service, formation, OPR, réserves, DOE/DIUO et maintenance |
| SAV/garanties | délais d’intervention, pièces, interlocuteur, maintenance et reporting |

La production part de la matrice **critère → sous-critère → attente → preuve → réponse → engagement → coût → responsable**. Le cadre acheteur prévaut sur un mémoire libre. Les limites de pages, tailles, renvois autorisés et annexes comptées doivent être contrôlés.

### 6.6 Annexes spécifiques et objets inhabituels

Le moteur de découverte recherche dans toutes les pièces et rectificatifs : « à fournir », « à joindre », « à compléter », « remet », « produit », « obligatoirement », « cadre », « attestation », « fiche », « planning », « certificat », « échantillon », « sous-détail » et formulations équivalentes.

Il doit pouvoir découvrir :

- fiches CV, fiches références et tableaux de moyens ;
- liste nominative d’intervenants ou qualifications individuelles ;
- liste de matériels, flotte et taux de véhicules propres ;
- questionnaire environnemental, SOGED/SOPRE-SED ou bilan carbone ;
- questionnaire RGPD, sécurité, hébergement ou plan d’assurance sécurité ;
- tableau de produits, origine, COV, FDES/PEP, contenu recyclé ou recyclabilité ;
- engagement de délai, astreinte, continuité ou stock de secours ;
- cadre de planning, planning détaillé ou note de phasage ;
- tableau insertion, heures, métiers et suivi ;
- attestation de visite ou formulaire de dispense ;
- certificat, autorisation, agrément, accréditation ou équivalence ;
- démonstration, maquette, prototype, échantillon ou dépôt physique ;
- fichier de simulation, affaire fictive, scénario de commande ou catalogue remisé ;
- déclaration d’absence de conflit d’intérêts ou engagement éthique ;
- lettre de confidentialité, accord de traitement des données ou annexe cyber ;
- fichiers natifs BIM, plans, vidéos, photographies ou démonstrateurs.

Le registre conserve l’expression exacte et ne classe « facultatif » qu’avec une preuve. « Invité à fournir », « peut joindre » et « devra produire » n’ont pas la même conséquence.

### 6.7 Marchés privés : reconstruire le dossier contractuel

**Statut : ÉTABLI pour les principes légaux cités ; VALIDATION EXTERNE pour la fréquence et les usages documentaires.** Le corpus local examiné ne permet pas encore de mesurer les pratiques privées. Le catalogue ci-dessous est donc un cadre de découverte, jamais une checklist universelle.

Dans un marché privé, la première question n’est pas « où est le RC ? », mais « quelles pièces forment l’accord et dans quel ordre ? ». Les contrats légalement formés obligent les parties ; devis, bon de commande, marché, cahier particulier, conditions générales, plans, planning, compte rendu ou offre négociée ne peuvent être hiérarchisés par leur seul nom.[^35]

| Famille | Pièces possibles à découvrir | Ce que SMART AO doit établir | Si non établi |
|---|---|---|---|
| Consultation | lettre ou courriel de consultation, règlement privé, liste de pièces, calendrier, questions/réponses | périmètre demandé, date, modalités et règles librement fixées | demander confirmation au donneur d’ordre |
| Besoin technique | cahier technique, descriptif, plans, diagnostics, quantitatifs, planning, contraintes de site | version, lot, limites de prestation et informations MIRP | question, hypothèse validée ou impossibilité de prix |
| Offre de l’entreprise | devis, DPGF/BPU, mémoire, réserves, exclusions, variantes, validité, planning | contenu exact proposé et conditions du prix | bloquer l’acceptation finale |
| Formation du contrat | marché signé, devis accepté, bon/lettre de commande, notification, mise au point | date d’acceptation, parties, montant, version et pouvoir du signataire | validation contractuelle |
| Clauses | conditions particulières, CGA/CGV, norme citée, annexes assurance/RGPD/cyber, charte chantier | ordre de priorité, clauses incorporées et accès licite | contradiction ou document inaccessible |
| Prix et trésorerie | avance/acompte, situations, validation, délai, révision/indexation, retenue, caution, garantie de paiement | échéancier, conditions et coût financier | validation DAF/juriste |
| Sous-traitance | sous-traité, acceptation, agrément des conditions de paiement, caution ou délégation, attestations | chaîne contractuelle et protection de paiement | blocage avant engagement ou démarrage |
| Modifications | courriels acceptés, avenants, commandes complémentaires, comptes rendus, ordres écrits | qui a demandé, qui a accepté, prix/délai et version du contrat | travaux supplémentaires non sécurisés |
| Réception et clôture | demande de réception, procès-verbal, réserves, levées, décompte, solde, DOE | départ des délais, sommes retenues et obligations restantes | dossier de clôture incomplet |

La NF P 03-001 n’est pas applicable à un marché privé par sa seule existence : elle doit être citée dans les pièces contractuelles et sa version doit être identifiée.[^36] Son contenu reste soumis aux droits d’accès et d’usage.

Lorsqu’une retenue de garantie contractuelle entre dans le champ de la loi du 16 juillet 1971, le contrôle documentaire doit rechercher le taux, la consignation, la caution de substitution, la réception, une éventuelle opposition motivée et la date de libération. La loi plafonne la retenue à 5 % et rend nulles les stipulations qui font échec à ses protections.[^37]

Le dossier doit aussi rechercher la garantie de paiement due à l’entrepreneur dans les situations couvertes par l’article 1799-1 du code civil. Le seuil réglementaire est de 12 000 € HT après déduction des arrhes et acomptes payés à la conclusion ; le type de financement et les exceptions doivent être qualifiés avant de conclure à l’existence d’une caution ou d’un droit de suspension.[^40][^41]

La sous-traitance impose une vigilance distincte : acceptation du sous-traitant, agrément des conditions de paiement et garantie par caution ou délégation dans les situations prévues. La loi de 1975 couvre des obligations applicables aux marchés privés comme publics.[^38] SMART AO détecte et prépare le dossier ; un juriste tranche les conséquences d’une irrégularité.

Le guide 2026 du Médiateur des entreprises ajoute des leviers contractuels concrets autour des délais, soldes, garanties, délégations de paiement, cautionnements et index BT/TP.[^39] Ils doivent être extraits comme paramètres de l’affaire et non appliqués comme valeurs par défaut.

## 7. Matrice réglementaire et procédurale publique

| Sujet | Règle utile au candidat | Décision documentaire SMART AO | Source |
|---|---|---|---|
| Définition du DCE | ensemble des documents fournis ou référencés ; information assez précise pour comprendre le besoin | inventorier fichiers et références externes ; signaler ce qui manque à la décision | Code R. 2132-1[^1] |
| Capacité | liste encadrée de renseignements économiques, techniques et professionnels | référentiel de preuves possibles, toujours filtré par le RC | Arrêté du 22 mars 2019[^4] |
| Formulaires | DC1, DC2, DC4 et notices maintenus par la DAJ | partir de la version officielle applicable ou du modèle imposé | DAJ[^5] |
| DUME | moyen de candidature déclarative accepté selon le cadre européen | importer/préremplir sans exiger simultanément une modalité exclusive contraire au RC | DUME/Service Public[^8] |
| Preuves d’exclusion | l’acheteur peut ne demander les justificatifs qu’au candidat pressenti ; défaut dans le délai peut éliminer | distinguer candidature initiale et dossier attributaire ; anticiper sans joindre inutilement | Code R. 2144-1 à R. 2144-9[^9] |
| Documents d’offre | l’acheteur peut exiger tout document permettant d’apprécier l’offre et certains objets matériels | découverte ouverte, logistique séparée pour supports physiques | Code R. 2151-15 et R. 2151-16[^10] |
| Offre irrégulière | offre non conforme ou incomplète ; régularisation possible seulement dans certaines conditions | absence bloquante selon exigence ; ne jamais compter sur une régularisation | Code L. 2152-2 et R. 2152-2[^3] |
| Transmission | plateforme, formats et exceptions définis par le cadre et le DCE | produire un manifeste propre au canal, pas un ZIP systématique | Service Public et arrêté copie de sauvegarde[^6][^11] |
| Signature | modalités électroniques encadrées ; moment et pièces viennent de la consultation | statut par document et signataire habilité, sans signature par défaut | Arrêté signature électronique[^12] |
| Nouveau dépôt | une offre modifiée avant échéance doit être redéposée complète selon les règles du profil | reconstituer le paquet entier et archiver les deux empreintes | Service Public[^6] |
| Échantillons | peuvent être requis et suivre une remise non dématérialisée | gérer support, étiquette, lieu, heure et récépissé séparément | Code/Service Public[^2][^10] |
| Sous-traitance | déclaration et agrément des conditions de paiement selon le stade | DC4, pièces du tiers, signatures et montants reliés au lot | DAJ DC4[^5] |

Les formulaires officiels ne forment pas une liste de remise automatique. La notice DC1 elle-même invite à vérifier les exigences de la consultation.[^13]

## 8. Documents externes, validité et interdiction de génération

| Document | Émetteur/titulaire | Validité à contrôler | Sensibilité | Si absent |
|---|---|---|---|---|
| Attestation fiscale | administration fiscale / entreprise | situation et date prévues, souvent dossier attributaire | fiscale | obtenir via espace officiel ; ne pas réécrire |
| Attestation de vigilance | Urssaf / entreprise | authenticité ; contrôle à la conclusion puis tous les six mois pour contrats concernés | sociale | demander et vérifier le code d’authenticité[^14] |
| Assurance RC professionnelle | assureur / entreprise ou établissement | période, activités, plafonds, exclusions, territoire | contractuelle | demander avenant/attestation adaptée ou bloquer |
| Assurance décennale | assureur / entreprise | obligation selon travaux, activité déclarée, chantier, période d’ouverture et géographie | contractuelle | validation spécialiste ; aucune affirmation universelle[^15] |
| Attestation bancaire/caution/GAPD | banque/garant / entreprise | objet, plafond, date, bénéficiaire et texte | bancaire | demande au tiers avec délai d’obtention |
| Qualification QUALIBAT | organisme / établissement | code/niveau et certificat annuel ; qualification attribuée pour durée limitée avec suivi | commerciale | vérifier annuaire/certificat et équivalence admise[^16] |
| QUALIFELEC, FNTP, MASE ou autre | organisme / entité | catégorie exacte, périmètre, date et établissement | commerciale | traiter selon exigence et moyens équivalents permis |
| ISO/accréditation | certificateur / périmètre certifié | norme, version, sites, activités et expiration | qualité | ne pas étendre à une filiale ou activité non couverte |
| Attestation de bonne exécution | client/MOE / opérateur ayant exécuté | opération, rôle, date, montant et signataire | commerciale | demander au client ou utiliser une autre preuve admise |
| Diplôme/titre/habilitation | organisme / personne | personne, niveau, domaine et éventuel recyclage | personnelle | affecter une autre personne ou renouveler |
| AIPR/CACES/habilitation électrique | organisme/employeur / personne | catégorie, poste, date et autorisation interne associée | personnelle | incapacité de promettre la ressource concernée |
| Attestation amiante/formation | organisme / entreprise ou personne | sous-section, activité, personne, processus et date | santé-sécurité | examen spécialisé et blocage de la méthode concernée |
| Certificat fabricant/agrément poseur | fabricant / entreprise ou personne | produit, système, territoire et durée | commerciale | demander au fabricant ou proposer solution conforme |
| Déclaration de performances/CE | fabricant / produit | référence exacte, version, norme harmonisée, caractéristiques | produit | pièce fournisseur ; génération interdite |
| FDES/PEP/EPD | programme/fabricant / produit | produit, configurateur, unité fonctionnelle, période et vérification | produit | ne pas substituer un produit voisin |
| Fiche technique/FDS | fabricant / produit | référence, révision et composition | produit/santé | obtenir la version exacte et contrôler la solution offerte |
| PV feu/acoustique/essai | laboratoire/organisme / système testé | montage, dimensions, support, domaine d’application | technique | équivalence à valider ; ne pas résumer au seul classement |
| Pièces sous-traitant/cotraitant | sources propres / partenaire | mêmes contrôles, titulaire conservé | confidentielle | relance, alternative ou modification du montage |
| RIB | banque / titulaire du compte | cohérence titulaire/IBAN et circuit sécurisé | bancaire critique | obtenir par canal fiable et contrôler anti-fraude |

L’attestation fiscale sert à prouver la régularité auprès du Trésor ; l’attestation de vigilance est présentée pour les contrats concernés à partir de 5 000 € HT et renouvelée tous les six mois pendant l’exécution.[^14][^17] Les qualifications QUALIBAT ont une durée limitée et un suivi annuel ; le certificat en cours, plutôt qu’une date théorique, fait foi pour le dossier.[^16]

Pour chaque preuve, SMART AO conserve **émetteur, titulaire, identifiant vérifiable, date, expiration, périmètre, document original et contrôle effectué**. Une date de validité ne suffit pas si l’activité, le produit, la personne ou le lot ne correspond pas.

## 9. Bibliothèque des pièces réellement rencontrées dans le corpus

### 9.1 AP-HP Sorbonne Université — entretien et modernisation multi-sites

Le dossier associe un RC, un AE, un CCAP, un CCTP multi-corps d’état, un cadre de mémoire technique, un cadre de présentation de candidature et une archive de prix contenant 55 classeurs XLSX, un XLS et une liste de fiches techniques à fournir.

Pièces et particularités observées :

- un mémoire par lot selon la trame acheteur ;
- organigramme nominatif, liste des sous-traitants, CV détaillés et expériences hospitalières ;
- organisation en périodes sensibles, astreinte, sites multiples et moyens minimums ;
- méthodologie, produits, fiches techniques et performance environnementale ;
- cadre XLSX de capacité : chiffres d’affaires, effectifs, qualifications et références ;
- BPU distincts par lot et parfois par site ;
- liste autonome de fiches techniques obligatoires pour le lot faux plafonds ;
- AE signé électroniquement avec l’offre selon ce RC ;
- distinction entre documents obligatoires, documents nécessaires à l’évaluation et documents souhaités.

**Enseignement :** l’exigence « fiche technique » peut être décrite dans un document niché à l’intérieur de l’archive de prix, pas seulement dans le RC.

### 9.2 Groupement hospitalier universitaire de Champagne — accord-cadre d’entretien

Le dossier comprend notamment DC1, DC2, ATTRI1, BPU, affaires fictives, CRT, questionnaires environnementaux, données financières antérieures, aide au dépôt, règles de copie de sauvegarde, référents amiante et annexe Chorus.

Les 152 classeurs XLS/XLSX visibles au niveau du corpus déclinent de nombreux corps d’état et sites : VRD, gros œuvre, couverture-étanchéité, menuiseries, carrelage, peinture, occultation, marquage, haute tension, CFO, CFA, GTC, CVC, plomberie, fluides médicaux et désamiantage. Chaque famille peut comporter le bordereau et une affaire fictive.

Le CRT exige notamment moyens matériels, moyens humains, CV, pilotage multi-sites, interventions en établissement occupé et prise en compte de l’amiante. Le questionnaire environnemental exige des réponses concrètes sur tri, filières, BSD/BSDA, produits, mobilité, nuisances, poussières, certifications et formation.

**Enseignement :** une « réponse technique » est un ensemble de cadres notés qui créent des engagements d’exécution. Leur contenu doit alimenter le registre des engagements et le dossier de passation.

### 9.3 Centre médical Filieris — réhabilitation et mise aux normes

Le RC distingue clairement :

- contenu du DCE : ATTRI1, DPGF, CRT, CCTP par lot et commun, CCAP, planning, plans et RICT ;
- candidature selon documents nationaux ou DUME ;
- offre : ATTRI1, DPGF intégralement complétée en Excel, CRT, mémoire complémentaire éventuel, attestation ou dispense de visite et RIB ;
- attributaire pressenti : justificatifs, certificats sociaux/fiscaux, pièces du Code du travail, assurance et signature requise.

**Enseignement :** phase, format et signature sont trois attributs indépendants. Un document présent mais au mauvais format ou au mauvais stade ne satisfait pas l’exigence.

### 9.4 Centrale de groupes électrogènes et sécurisation électrique

Le DCE annonce : RC, CCAP, AE/DPGF, CCTC et CCTP, pièces graphiques, rapports amiante, planning prévisionnel, attestation de visite, annexe RGPD, RICT et études G2 PRO. L’offre demande notamment AE/DPGF, pièces contractuelles datées/signées, planning, attestation de visite, mémoire technique et annexe RGPD.

Les annexes techniques couvrent électricité, groupes électrogènes, gros œuvre/VRD, étanchéité, bardage-serrurerie et peinture. L’annexe RGPD contient des engagements sur finalités, sous-traitants, sécurité, violations, transferts, durée, audits et, selon les traitements, hébergement de données de santé.

**Enseignement :** une annexe apparemment administrative peut contenir des obligations techniques, organisationnelles et économiques qui exigent un contrôle expert avant signature.

### 9.5 Réhabilitation du bâtiment d’hôtellerie du cercle mixte de la Gendarmerie de Dijon

Le RC cite DPGF par lot, mémoire technique, note méthodologique, mémoire environnemental, fiches techniques, planning détaillé et plusieurs documents fournis : plans, PGCSPS, RICT, diagnostic structurel, amiante et autres diagnostics. La visite, l’insertion selon le lot, les variantes et l’absence de certaines pièces ont des règles propres.

Les CCTP électricité et CVC imposent le remplissage du fichier Excel DPGF joint. Les documents d’exécution détaillent ensuite plans, notes, matériels, visas, essais et DOE.

**Enseignement :** SMART AO doit distinguer la pièce remise avec l’offre du livrable futur décrit dans le même CCTP, tout en chiffrant dès l’offre le coût du futur livrable.

### 9.6 RN12 — déviation d’Ernée, terrassements, assainissement, chaussées et équipements

L’archive 7z ajoute 83 fichiers : AE base et variante, CCAP, CCTP en nombreux fascicules, BPU, détail estimatif XLSX, cadres SOPAQ et SOPRE-SED, note d’enjeu sécurité et continuité, dossier d’autorisation environnementale, étude d’impact, incidence IOTA, documents hydrauliques, chaussées, topographie, diagnostic amiante-plomb et un grand ensemble de plans. Trois notes additives modifient le dossier.

Le RC prévoit candidature, documents de l’attributaire, offre de base et variante, valeur environnementale, formats admis et absence de macros. L’archive contient pourtant deux fichiers XLSM : cette contradiction de format est précisément le type de point à qualifier au niveau de chaque fichier et de sa destination.

**Enseignement :** la complétude d’un dossier d’infrastructure exige un manifeste hiérarchique, la lecture des notes additives et une couverture croisée des données terrain, environnement, géométrie, prix, qualité et sécurité.

### 9.7 Typologie consolidée des annexes du corpus

| Type rencontré | Exemples réels | Action SMART AO |
|---|---|---|
| Cadre administratif | DC1, DC2, DC4, ATTRI1, cadre capacité | préremplir, contrôler par entité/lot, signer si requis |
| Cadre technique | mémoire imposé, CRT, note méthodologique | remplir dans l’original, couvrir chaque item et preuve |
| Cadre environnemental | CQE, mémoire, SOPRE-SED | répondre, rattacher coûts et engagements |
| Cadre prix | BPU, DPGF, DE/DQE, affaire fictive | remplir cellules autorisées, contrôler formules/totaux |
| Visite | attestation ou dispense | obtenir, vérifier lot/site/date et joindre à la bonne phase |
| Référence/amiante | référents, compétences, modes opératoires | sélectionner personnes valides et documents applicables |
| Données personnelles/cyber | annexe RGPD | qualifier obligations, faire valider et signer |
| Facturation | SIRET/Chorus/comptables assignataires | transmettre à l’attribution/exécution, accès restreint |
| Diagnostics | amiante, plomb, structure, géotechnique, RICT | vérifier zone/date/limites et relier aux postes risqués |
| Plans et données | PDF, DWG annoncés, topo, hydraulique, réseaux | inventaire par feuille/indice et contrôle de lisibilité |
| Exécution future | planning, EXE, calculs, PAQ, PPSPS, DOE | chiffrer, planifier et passer au chantier |

## 10. Niveaux d’exigence pour les informations de prix

Chaque donnée nécessaire au chiffrage reçoit un niveau :

| Niveau | Définition | Effet par défaut |
|---|---|---|
| R — réglementairement requise | un texte impose le document dans les conditions remplies | demander la pièce et validation spécialisée ; blocage si les travaux exposés ne peuvent commencer légalement |
| C — contractuellement requise | le DCE impose sa remise, son utilisation ou un livrable | respecter exactement la clause ; question si pièce annoncée absente |
| P1 — indispensable au prix | absence empêchant une quantité, une méthode ou un risque raisonnablement maîtrisé | blocage prix ou hypothèse exceptionnelle approuvée par le patron |
| P2 — fortement recommandée | prix possible mais exposition importante ou réserve nécessaire | question acheteur, scénario prudent et provision |
| P3 — utile | améliore la précision sans modifier normalement la décision | information et tâche non bloquante |

Le niveau est conditionnel. Une topographie peut être P1 pour des terrassements et P3 pour une peinture intérieure. Un repérage amiante devient R lorsqu’il entre dans le champ réglementaire des travaux concernés ; ailleurs, il peut être non applicable.

## 11. Matrice des exigences minimales d’information pour établir le prix

### 11.1 Tous travaux

| Document ou donnée | Condition d’applicabilité | Niveau habituel | Risque d’absence | Action SMART AO |
|---|---|---|---|---|
| Périmètre et limites de prestation | toujours | P1/C | oubli, doublon ou interface non chiffrée | croiser CCTP, plans et prix ; matrice inclus/exclu/tiers |
| Plans et dimensions utiles | ouvrages quantifiables ou interfaces géométriques | P1 | quantité et méthode impossibles à fiabiliser | demander plan/relevé ou faire accepter métrés provisoires |
| Quantités/cadre de prix | prix forfaitaire ou unitaire selon DCE | C/P1 | total incohérent ou exposition quantité | conserver cadre, signaler quantité indicative et contrôler toutes lignes |
| État de l’existant | rénovation, raccordement, dépose | P1/P2 | découverte, reprise et arrêt de chantier | plans/relevé/visite/diagnostic ; hypothèses par zone |
| Conditions d’accès et logistique | accès limité, site occupé ou urbain | P1/P2 | moyens, temps improductif et autorisations oubliés | qualifier accès, stockage, levage, horaires et domaine public |
| Planning et phasage | délai imposé, coactivité, sites multiples | P1/C | surcharge, travail décalé, approvisionnement impossible | modéliser jalons, coupures, visas, interfaces et marges |
| Prescriptions communes | marché multi-lots | C/P1 | frais communs et obligations transversales oubliés | appliquer à chaque lot concerné et chiffrer |
| Répartition des études/essais/DOE | travaux nécessitant études ou réception technique | C/P1 | coût futur non inclus | registre des livrables post-attribution et charge associée |
| Visite et questions-réponses | selon RC | C/P2 | irrecevabilité ou hypothèse non mise à jour | suivre preuve, compte rendu interne et réponses tardives |

### 11.2 Terrassement et VRD

| Information | Condition | Niveau | Conséquence possible | Action |
|---|---|---|---|---|
| Levé topographique, altimétrie, emprises | terrassement, nivellement, réseaux | P1 | volumes, pentes et implantation non fiables | demander fichier exploitable, indice, système de coordonnées |
| Étude géotechnique et sondages | comportement du sol influençant méthode/portance | P1 ; R seulement dans champs légaux précis | engins, traitement, talus, portance, évacuation ou apport mal estimés | vérifier mission, zone, profondeur, limites et scénarios |
| Hydrogéologie/nappe | excavation, pompage, ouvrage enterré | P1/P2 | rabattement, blindage, rejet et délai | demander niveau saisonnier, débits, autorisations et exutoire |
| Plans/réponses réseaux | travaux à proximité de réseaux | R/C/P1 selon stade | casse, arrêt, sondages et protection | vérifier DT, récépissés, classe de précision et investigations complémentaires[^18] |
| Pollution sols/terres | site ancien, suspicion ou évacuation | P1/P2 | filière et coût d’évacuation majeurs | demander diagnostics/analytiques, volumes, statut et filières |
| Bilan déblais-remblais | terrassement important | P1 | transport, dépôt, emprunt et carbone | contrôler volumes, foisonnement, réemploi et distances |
| Hydraulique/assainissement | réseaux, bassins, traversées | P1 | dimensions, pompage, exutoires et autorisations | demander données de calcul, profils, niveaux et contraintes |
| Circulation et signalisation | voirie circulée | P1/C | phasage, balisage et rendement | plans de circulation, arrêtés, maintien trafic et horaires |

La réglementation anti-endommagement distingue documents du responsable de projet, DT, investigations, marquage-piquetage et DICT ; SMART AO doit déterminer le stade et les responsabilités, pas demander indistinctement une DICT finalisée dès l’offre.[^18]

### 11.3 Fondations, gros œuvre et structure

| Information | Condition | Niveau | Conséquence possible | Action |
|---|---|---|---|---|
| Géotechnique de conception | fondations/interaction sol-structure | P1 ; R pour certains contrats et zones argileuses définis au CCH | type de fondation, profondeur, blindage et aléas | vérifier que l’étude concerne l’implantation et le projet réels[^19] |
| Descente de charges et hypothèses | reprise/extension/fondation | P1 | sous-dimensionnement ou étude supplémentaire | demander données structure et distinguer calcul offre/EXE |
| Diagnostic structure | réhabilitation, percements, changement de charge | P1/P2 | renforcement et méthode inconnus | vérifier zones sondées, matériaux, pathologies et limites |
| Plans coffrage/ferraillage/existant | quantité ou interface structurelle | P1/C | métrés et connexions non fiables | rattacher chaque plan à l’ouvrage et à son indice |
| Relevés et tolérances | raccordement à existant | P1/P2 | préfabrication/reprises | visite technique, scan/relevé ou provision validée |
| RICT/avis contrôle | ouvrage soumis à contrôle ou DCE le fournissant | C/P2 | prescriptions/avis suspendus non chiffrés | extraire avis par lot et réponse attendue |
| Amiante/plomb avant percements/déposes | matériaux/ouvrages susceptibles d’être affectés | R si champ rempli | exposition, arrêt et surcoût | contrôler périmètre du repérage et parties inaccessibles[^20] |

La réglementation géotechnique liée au retrait-gonflement des argiles concerne des situations définies, notamment certains terrains et bâtiments ; elle ne rend pas une G2 universellement obligatoire dans tous les marchés BTP.[^19]

### 11.4 Réhabilitation, démolition et désamiantage

| Information | Condition | Niveau | Risque | Action |
|---|---|---|---|---|
| Plans/relevés de l’existant | toute transformation | P1 | quantités et interfaces inconnues | demander, visiter, relever et marquer les zones non vérifiées |
| Repérage amiante avant travaux | opération susceptible d’affecter matériaux concernés | R | santé, arrêt, méthode et déchets | exiger rapport adapté à la nature et au périmètre des travaux ; lire réserves/parties inaccessibles[^20] |
| Diagnostic plomb/autres polluants | bâtiments/ouvrages et travaux concernés | R ou P1/P2 selon régime | protection, déchets, mode opératoire | déclencher règle conditionnelle et validation QSE |
| Diagnostic structure | déconstruction, ouverture ou reprise | P1 | effondrement, étaiement et séquence | demander stabilité, sondages et méthodologie |
| PEMD | démolition/rénovation significative entrant dans le champ | R | gisements, réemploi, filières et traçabilité ignorés | vérifier seuils/usage, diagnostic avant marché et récolement futur[^21] |
| Inventaire des réseaux actifs | site occupé ou déconstruction partielle | P1 | coupure et danger | plans, consignation, repérage et maintien de service |
| Phasage/occupation | maintien d’activité | P1/C | protections, nettoyage, nuisances et rendement | zones, horaires, déménagements, itinéraires et remises en service |
| Filières et traçabilité | déchets dangereux, amiante, terres | R/C/P1 | prix d’évacuation et non-conformité | volumes, codes, filières, BSD/BSDA et Trackdéchets[^22] |

Pour les ouvrages de génie civil, infrastructures et réseaux, l’arrêté du 4 juin 2024 précise le repérage amiante avant certaines opérations et le traitement des parties techniquement inaccessibles.[^20] SMART AO ne doit jamais traduire « rapport présent » par « totalité du périmètre investiguée ».

### 11.5 Enveloppe, étanchéité et façades

| Information | Condition | Niveau | Risque | Action |
|---|---|---|---|---|
| Relevés façades/toitures et supports | rénovation ou raccords | P1 | surfaces, accessoires et reprises | plans + visite/relevé, état des supports |
| Complexes existants et diagnostics | dépose, recouvrement, percement | P1/R selon substances | épaisseur, fixation, amiante et déchets | identifier chaque couche et périmètre diagnostiqué |
| Performances thermique/acoustique/feu | exigence programme/réglementation applicable | C/P1 | solution non conforme | valeur cible, méthode de preuve et système complet |
| Vent/neige/exposition | façade, couverture, éléments rapportés | P1/P2 | dimensionnement et fixation | données site et notes futures à chiffrer |
| Accès, échafaudage, nacelle, levage | hauteur/site occupé | P1 | installation, autorisation et rendement | emprises, portance, occupation domaine, protections |
| Échantillons, teintes et prototypes | exigés/notés/visés | C/P2 | coût, délai et approbation | registre physique, quantité, destinataire et récépissé |

### 11.6 Électricité, SSI, GTC et groupes électrogènes

| Information | Condition | Niveau | Risque | Action |
|---|---|---|---|---|
| Schéma unifilaire et architecture existante | modification/raccordement | P1 | quantité, compatibilité et coupure | indice, source, départs, réserves et zones |
| Bilan de puissance et régimes | alimentation/extension | P1 | dimensionnement et abonnement | charges, simultanéité, secours, court-circuit, sélectivité |
| Relevés tableaux/câbles/cheminements | rénovation | P1 | métrés et raccordement | visite, photos autorisées, plans et hypothèses |
| Stratégie de coupure/continuité | hôpital, industrie, site occupé | P1/C | moyens temporaires et travail de nuit | fenêtres, groupes provisoires, consignation, essais |
| SSI et interfaces | travaux affectant sécurité incendie | P1 | incompatibilité, essais et coordination | catégorie, scénario, zones, coordonnateur SSI et réception |
| Protocoles GTC/CFA | intégration numérique | P1/P2 | licences, passerelles et programmation | liste points, protocoles, marques existantes, accès et cyber |
| Terre, foudre, CEM | installations concernées | P1/P2 | protections/mesures non chiffrées | études existantes, mesures et essais attendus |
| Habilitations et qualifications | personnel promis | C/P1 | incapacité à intervenir | vérifier personnes, niveaux, disponibilité et recyclages |

### 11.7 CVC, plomberie, fluides et équipements techniques

| Information | Condition | Niveau | Risque | Action |
|---|---|---|---|---|
| Bilans thermiques/aérauliques/hydrauliques | conception ou remplacement fonctionnel | P1 | puissance, débit et performance inconnus | obtenir calculs/hypothèses et responsabilités d’étude |
| Plans/synoptiques/réseaux existants | raccordement/rénovation | P1 | longueurs, diamètres, arrêts et accessoires | plans + relevé, zones non accessibles |
| Régimes, qualité d’eau/air et données fluides | raccordement/process/hôpital | P1 | matériaux, traitement et essais | valeurs source et critères d’acceptation |
| Locaux techniques, accès et manutention | remplacement équipement | P1 | démontage, levage, grutage, renfort | relevés, chemin d’accès, masses et moyens provisoires |
| Continuité et fenêtres d’arrêt | site occupé | P1/C | by-pass, production provisoire, nuits | scénario de bascule, autorisations et essais |
| Régulation/GTC | intégration | P1/P2 | programmation et compatibilité | marque, version, points, licences, protocoles |
| Acoustique/vibrations | locaux sensibles ou limites | C/P1/P2 | supports, pièges, écrans et mesures | objectifs, points de mesure et état initial |
| Mise en service/commissionnement | systèmes techniques | C/P1 | charge d’essais et documents | protocoles, organismes, durée, formation et DOE |

### 11.8 Second œuvre et aménagement

| Information | Condition | Niveau | Risque | Action |
|---|---|---|---|---|
| Plans, carnets de détails et tableaux de finitions | quantités/produits par local | P1 | mélange de gammes, surfaces ou accessoires | rattacher local–ouvrage–finition–ligne prix |
| État/humidité/planéité des supports | rénovation et finitions | P1/P2 | préparation et reprise | diagnostic/visite, tolérances et responsabilités |
| Exigences feu, acoustique, hygiène, COV | ERP, santé, locaux spécifiques | C/P1 | système non conforme | preuve du système complet, pas du produit seul |
| Échantillons et nuanciers | choix esthétique ou exigence | C/P2 | temps, quantités et validation | organiser remise et conserver décision |
| Mobilier/équipements/interfaces | agencement | P1 | raccords, réservations, quincaillerie | plans, nomenclature, fourniture/pose et tolérances |
| Site occupé/protections/nettoyage | rénovation en activité | P1 | rendement et moyens oubliés | phasage, horaires, poussière, stockage et repli quotidien |

### 11.9 Opérations multi-sites et accords-cadres

| Information | Condition | Niveau | Risque | Action |
|---|---|---|---|---|
| Liste et typologie des sites | multi-sites | P1 | déplacement, accès et astreinte | profil par site et règle commune/locale |
| Historique ou affaires fictives | accord-cadre | P2/C | mauvais panier économique | simuler mix réaliste sans le présenter comme volume garanti |
| Minimum/maximum et nombre d’attributaires | accord-cadre | C/P1 | capacité maximale ou chiffre incertain | dissocier exposition maximale et revenu probable |
| Délais de chiffrage/intervention | bons/marchés subséquents | C/P1 | encadrement et astreinte sous-estimés | charge administrative, équipes de secours et distance |
| Règles de remise en concurrence | multi-attributaire | C/P1 | coût de réponses futures | modéliser documents et effort par marché subséquent |

## 12. Documents après attribution à anticiper dans le prix

| Phase | Documents possibles | Règle métier |
|---|---|---|
| Mise au point/notification | AE signé, pièces fiscales/sociales, assurances, RIB, DC4, garanties | préparer le dossier attributaire sans le joindre prématurément |
| Préparation | planning détaillé, PPSPS, plan de prévention, PAQ, plan environnement/SOGED, procédures, demandes d’agrément | chiffrer charge, délais, contributeurs et validations |
| Études d’exécution | relevés, plans EXE, notes de calcul, synthèse/BIM, fiches techniques, échantillons | identifier qui produit, qui vise et le nombre d’itérations prévu |
| Réseaux et autorisations | DICT, arrêtés, occupation domaine, consignations, permis de feu/travail | distinguer responsabilité entreprise/maître d’ouvrage/exploitant |
| Approvisionnements | dossiers fournisseurs, conformité produits, provenance, certificats, traçabilité | rattacher au produit réellement chiffré |
| Travaux | contrôles, essais, fiches autocontrôle, rapports, constats, photos, BSD/BSDA | prévoir effort documentaire continu et preuve de l’engagement |
| Mise en service | protocoles, mesures, réglages, commissions, formation, notices | vérifier critères d’acceptation et présence des organismes |
| Réception | DOE, plans de récolement, DIUO, notices, garanties, PV, dossier maintenance | établir la liste dès l’offre, formats et délais contractuels |
| Clôture | levée de réserves, récolement PEMD, traçabilité déchets, dossiers finaux | transmettre au chantier les obligations et retenues liées |

Lorsque le CCAG Travaux est expressément applicable, son article 29 prévoit notamment plans d’exécution, notes de calcul, études de détail, relevés et transmission d’éléments pour le DIUO ; les documents particuliers répartissent les responsabilités et peuvent déroger.[^23] Le PGC est établi dans les situations de coordination prévues et le PPSPS est produit par l’entreprise dans les cas applicables.[^24][^25]

Un document dû après attribution n’est pas automatiquement un document d’offre. Il devient toutefois une **obligation à budgéter**, un besoin de ressource, une échéance future et un élément de passation.

## 13. Contrôle de complétude du DCE avant chiffrage

Le contrôle se déroule en six passages.

### 13.1 Inventaire technique

- compter fichiers, dossiers et entrées d’archives ;
- reconnaître type réel, extension, taille, mot de passe, corruption et doublon ;
- détecter archives imbriquées, macros, liens externes et pièces sans texte exploitable ;
- établir une empreinte de chaque original ;
- conserver les noms et arborescences d’origine.

Sortie : **présent et lisible**, **présent mais partiellement lisible**, **présent non exploité**, **corrompu/protégé**, **référence sans fichier**.

### 13.2 Inventaire annoncé contre inventaire reçu

SMART AO compare les sommaires et listes de pièces du RC, AE, CCAP, CCTP et éventuel bordereau de téléchargement à l’inventaire réel. Une différence peut être : pièce manquante, nom différent, version inattendue, pièce supplémentaire, doublon ou annexe annoncée seulement par renvoi.

### 13.3 Découverte des exigences de remise

Toutes les formulations d’obligation sont extraites avec leur phrase complète, puis rapprochées des critères de notation, formats, signatures, lots et phases. Le logiciel distingue :

- obligation ferme ;
- exigence conditionnelle ;
- document seulement souhaité ou valorisant ;
- pièce fournie pour information ;
- livrable postérieur ;
- formulation ambiguë à valider.

### 13.4 Analyse des données minimales pour le prix

À partir des corps d’état, ouvrages, travaux et contraintes détectés, SMART AO applique la matrice MIRP. Il ne signale pas toutes les études imaginables ; il explique le lien causal :

> « Terrassement sous nappe identifié, mais aucun niveau de nappe ou débit exploitable n’a été trouvé. Le pompage, le blindage et le rejet ne peuvent pas être chiffrés de manière fiable. »

### 13.5 Contradictions et limites

La présence d’un rapport ne clôt pas le besoin si :

- il ne couvre pas le bâtiment, la zone, la profondeur ou les matériaux touchés ;
- il est antérieur à une modification du projet ;
- ses annexes, sondages ou plans manquent ;
- il annonce des investigations complémentaires ;
- une autre pièce présente une donnée différente ;
- il est seulement indicatif ou explicitement non contractuel.

### 13.6 Décision de préparation

| État | Signification | Autorisation |
|---|---|---|
| PRÊT À ÉTUDIER | pièces critiques présentes, lisibles et applicables | étude détaillée autorisée |
| PRÊT SOUS CONDITIONS | manques couverts par hypothèses bornées ou questions en cours | étude autorisée, prix final bloqué selon criticité |
| INSUFFISANT | données P1 manquantes ou périmètre non maîtrisé | chiffrage fiable non autorisé |
| NON ANALYSABLE | fichier critique illisible, protégé ou absent | action technique/acheteur obligatoire |
| NO-GO À DÉCIDER | l’incertitude résiduelle dépasse le seuil accepté | décision du dirigeant |

Une absence produit l’une des actions suivantes : information, tâche interne, demande de pièce, question à l’acheteur, visite/relevé, consultation d’un expert, hypothèse de chiffrage, provision, réserve si autorisée, blocage du prix ou NO-GO.

## 14. Règles de traitement des modèles propriétaires

### 14.1 Principe de fidélité

Lorsque l’acheteur fournit un modèle, le fichier original est l’autorité de forme. SMART AO travaille sur une copie identifiée et :

- conserve structure, titres, ordre, feuilles, lignes, colonnes, formules et consignes ;
- respecte cellules ou zones prévues pour le candidat ;
- ne supprime aucun texte acheteur sans décision explicite et preuve que cela est permis ;
- ne déverrouille pas une protection pour contourner une restriction ;
- ne convertit pas silencieusement un DOCX/XLSX en PDF ou inversement ;
- préserve les métadonnées ou macros nécessaires lorsque le format est autorisé ;
- signale tout élément externe, lien cassé ou fonction non recalculée ;
- compare le fichier produit avec l’original et liste les modifications.

Spigao documente le retour des prix dans les pièces originales DPGF, DQE ou BPU fournies par le maître d’ouvrage, y compris en PDF, Excel ou Word.[^26] Cette fonction est une attente de marché. SMART AO doit l’étendre aux cadres techniques et administratifs avec un contrôle de fidélité explicable.

### 14.2 Document libre

En l’absence de trame, SMART AO peut générer un document selon la charte de l’entreprise. Il doit néanmoins respecter plan de réponse, critères, limite de pages, annexes et formats du RC. Aucun modèle interne ne prévaut sur une consigne acheteur.

### 14.3 Formulaire tiers ou portail

Pour un DUME en ligne, un formulaire de plateforme, une signature ou une preuve officielle, SMART AO prépare les données et guide le responsable. Il conserve l’accusé ou l’export obtenu. Il n’affirme pas avoir rempli un portail sans preuve du résultat.

### 14.4 Objets physiques

Pour échantillon, prototype ou maquette, le registre ajoute : quantité, référence, dimensions, conditionnement, étiquette, destinataire, lieu, créneau, transporteur, récépissé, retour et coût. Le manifeste distingue remise électronique et remise physique.

## 15. Patrimoine documentaire de l’entreprise

### 15.1 Données stables mais contrôlées

- raison sociale, forme, SIREN/SIRET, adresse et établissements ;
- dirigeants, fonctions et coordonnées professionnelles ;
- identifiants de facturation et informations générales ;
- charte graphique et descriptions institutionnelles validées ;
- métiers et zones d’intervention.

Un changement d’établissement, de dirigeant ou de structure invalide les contenus dérivés concernés.

### 15.2 Données périodiques ou expirables

- chiffres d’affaires, bilans et effectifs par année ;
- assurances ;
- qualifications et certifications ;
- attestations fiscales/sociales et vigilance ;
- pouvoirs et délégations ;
- habilitations, formations et visites médicales selon usage ;
- parc matériel, contrôles et locations ;
- tarifs, accords fournisseurs et fiches produits ;
- CV et disponibilités ;
- politiques, objectifs et indicateurs QSE.

Chaque donnée possède un propriétaire interne, une date de revue et une règle de renouvellement. « Document récent » ne remplace pas une date vérifiée.

### 15.3 Contenus réutilisables avec contexte

- références d’opérations et attestations ;
- méthodes, procédures, contrôles et exemples ;
- photographies avec droits et autorisation client ;
- ratios, rendements et retours de chantier ;
- partenaires et fournisseurs approuvés ;
- engagements environnementaux mesurés ;
- modèles de planning, organigramme et dossiers de passation.

La réutilisation est interdite si elle change l’entreprise qui a réalisé la référence, attribue une compétence à une personne indisponible, promet un matériel non réservé ou présente un résultat non mesuré comme acquis.

### 15.4 Confidentialité et exclusion des sorties candidat

| Classe | Exemples | Règle |
|---|---|---|
| Direction uniquement | marge, prix plancher, trésorerie, note partenaire, risque contentieux | jamais injecté dans un livrable sans décision du dirigeant |
| Prix/achats restreints | prix fournisseur, coefficients, sous-détails | accès études/DAF ; export seulement si demandé et autorisé |
| Bancaire/fiscal/social | RIB, bilans, attestations, masse salariale | accès minimal et remise seulement à la phase utile |
| Personnel | CV, diplômes, habilitations, coordonnées | finalité, minimisation, autorisation et durée adaptées |
| Secret commercial | méthodes, partenaires, références sensibles | marquage, accès affaire et contrôle avant partage |
| Public réutilisable | présentation validée, certifications publiques | version et périmètre toujours contrôlés |

La base de connaissance destinée à la rédaction doit être séparée des données de décision économique. Une instruction de génération ne doit jamais permettre à un mémoire technique de récupérer une marge ou une appréciation interne.

## 16. Constitution du dossier final et manifeste de remise

### 16.1 Le manifeste

Le manifeste est la vérité opérationnelle de la remise. Il contient, pour chaque élément :

- identifiant d’exigence et source DCE ;
- phase et enveloppe logique ;
- lot, variante, PSE, tranche et opérateur ;
- nom exact du fichier ou objet physique ;
- format, taille et empreinte ;
- version documentaire et statut de validation ;
- signature requise, signataire et résultat de vérification ;
- emplacement : fichier individuel, répertoire, archive autorisée, plateforme ou adresse physique ;
- date/heure limite et heure interne de sécurité ;
- preuve de transmission ou récépissé.

La sortie de contrôle doit être lisible par le patron :

```text
VERSION D’OFFRE V7 — LOT 11A
Pièces requises : 18
Présentes et validées : 14
À obtenir : 2
En attente de décision : 1
Bloquantes : 1
Pièces physiques : 0
Statut : DÉPÔT NON AUTORISÉ
```

### 16.2 Aucune hypothèse ZIP

Le dossier final peut exiger : fichiers individuels, dossiers virtuels, PDF et fichier natif simultanés, archive ZIP, absence d’archive, support physique, signature de certains fichiers ou signature seulement à l’attribution. Le RC RN12 accepte certains formats et ZIP mais exclut les macros ; le dossier Centrale exige au contraire l’insertion individuelle des pièces clairement nommées. Le manifeste applique la règle propre à l’affaire.

### 16.3 Contrôles avant autorisation

1. toutes les exigences bloquantes de la version sont satisfaites ;
2. le modèle acheteur et le format demandé sont conservés ;
3. aucun fichier obsolète ou remplacé n’est inclus ;
4. les totaux AE, BPU, DQE et DPGF concordent ;
5. les engagements techniques concordent avec prix, planning et partenaires ;
6. signatures et pouvoirs sont corrects pour cette phase ;
7. noms, tailles, macros, mots de passe, liens et antivirus sont contrôlés ;
8. données confidentielles internes et commentaires de travail sont absents ;
9. les objets physiques ont leur propre preuve ;
10. l’empreinte du paquet autorisé est conservée.

### 16.4 Après transmission

Le reçu du profil acheteur est rapproché du manifeste et de l’empreinte. Un reçu sans correspondance avec le paquet autorisé ne vaut pas succès métier. Si un nouveau dépôt est nécessaire avant échéance, SMART AO reconstruit un paquet complet ; le service public précise qu’une nouvelle offre complète remplace la précédente selon les règles applicables.[^6]

## 17. Blocages et décisions humaines

| Situation | Blocage par défaut | Décideur |
|---|---|---|
| Pièce d’offre explicitement obligatoire absente | dépôt | responsable d’offre puis signataire |
| Modèle acheteur altéré hors zones autorisées | dépôt | responsable d’offre |
| Preuve tierce inventée, modifiée ou mauvais titulaire | dépôt | administratif/dirigeant |
| Attestation expirée à la date utile | phase concernée | administratif/organisme émetteur |
| Document P1 absent pour le prix | validation du prix | chargé d’études + dirigeant |
| Contradiction non résolue affectant prix/périmètre | prix et dépôt | expert + dirigeant |
| Signature requise sans pouvoir valable | dépôt/attribution | dirigeant/juridique |
| Fichier critique illisible ou protégé | analyse/remplissage | responsable d’offre/acheteur |
| Question acheteur sans réponse avant remise | selon impact | dirigeant accepte hypothèse ou NO-GO |
| Engagement technique sans donnée, coût ou responsable | validation offre | responsable technique/dirigeant |
| Donnée confidentielle détectée dans une sortie | export | propriétaire de la donnée |

SMART AO peut recommander une action, jamais lever seul un blocage C1. Toute dérogation conserve auteur, date, raison, conséquence et durée.

## 18. Veille concurrentielle documentaire

### 18.1 Fonctions observées

| Acteur | Fonctions documentaires publiées | Niveau de preuve de cette étude | Limite non établie |
|---|---|---|---|
| Spigao | enveloppe administrative préremplie, DC1/DC2/ATTRI1, DCI, mémoire, retour des prix dans DPGF/DQE/BPU originaux | documenté par pages et parcours éditeur[^26][^27] | complétude dynamique de toutes annexes et MIRP par corps d’état non démontrées |
| Tenderbolt | analyse DCE, matrices, questionnaires, cadres Word/Excel, RFQ/BPU reliés aux catalogues | documenté sur pages fonctionnelles éditeur[^28] | fidélité aux modèles et preuve de paquet final non testées indépendamment |
| Wanao/Sendao | DCE, rectificatifs, bibliothèque administrative, organisation, signature et dépôt | documenté par pages et démonstration éditeur[^29] | documents nécessaires au chiffrage et portée technique non établis |
| Libel | formulaires officiels, espace numérique, mises à jour d’attestations, échéances et réponse électronique | documenté par centre d’aide public[^30] | production technique BTP et analyse de données manquantes non établies |
| Doaken | DPGF, mémoire, DC1/DC2/DC4, base documentaire, expiration et contrôles avant export | revendiqué sur page commerciale publique[^31] | produit, précision, couverture et résultats non vérifiés indépendamment |
| BâtiOffre | coffre documentaire, expiration, mémoire, formulaires et ZIP/checklist | revendiqué sur page commerciale publique[^32] | qualité, exactitude juridique et respect de paquets non-ZIP non vérifiés |
| Titulis | report dans Word acheteur, prix dans Excel, documents administratifs et livrables BTP | revendiqué sur page commerciale publique[^33] | profondeur de découverte et préservation des fichiers non testées |
| Avalanch | extraction PDF/Word/Excel, questionnaires, mémoire et documents réglementaires | revendiqué sur page commerciale publique[^34] | spécialisation BTP, exactitude et portée des preuves non établies |

Les revendications commerciales ne sont pas des essais. Aucun de ces outils n’a été soumis dans cette étude au corpus de 379 fichiers, aux 152 anciens XLS, au ZIP AP-HP ou au 7z RN12.

### 18.2 Fonctions devenues standard

- bibliothèque de pièces administratives ;
- alertes d’expiration ;
- préremplissage DC1/DC2/DC4 ;
- mémoire technique assisté ;
- extraction ou remplissage de DPGF/BPU ;
- checklist avant export ;
- gestion basique des versions et rectificatifs ;
- export d’un dossier de réponse.

### 18.3 Espaces de différenciation documentaire

| Espace | Différence SMART AO |
|---|---|
| Registre unifié | relie chaque document à sa source, phase, portée, mode, validité et conséquence |
| Quatre univers | ne confond pas pièce acheteur, pièce de remise, preuve tierce et donnée nécessaire au prix |
| MIRP par corps d’état | détecte une donnée absente susceptible de rendre le prix dangereux |
| Preuve d’applicabilité | explique pourquoi une géotechnique, un RAT, un PGC ou un PEMD est attendu dans ce cas précis |
| Fidélité au modèle | compare le fichier rempli à l’original et explique chaque modification |
| Phase dynamique | sait qu’un même document peut être offre, attribution ou exécution selon le RC |
| Manifeste multi-canal | gère fichiers individuels, natifs, PDF, archives et objets physiques sans imposer ZIP |
| Engagement futur | transforme les livrables après attribution en coûts, charge et passation chantier |
| Abstention | affiche illisible, absent et non établi au lieu d’un faux statut complet |

## 19. Priorisation métier

### P0 — Indispensable au premier produit documentaire

- inventaire de tous fichiers et archives avec détection d’illisibilité ;
- registre des exigences avec source exacte, phase, lot, criticité et état ;
- découverte des obligations dans RC, CCAP/CCP, CCTP, annexes, prix, rectificatifs et Q/R ;
- distinction acheteur fourni / à remettre / tiers / nécessaire au prix / post-attribution ;
- remplissage fidèle des DOCX/XLSX acheteur et conservation de l’original ;
- candidature de base, bibliothèque entreprise, validité et titulaire ;
- BPU/DPGF/DQE avec contrôle cellules, formules et totaux ;
- mémoire/CRT relié aux critères, preuves et engagements ;
- contrôle de complétude DCE et premier MIRP multi-métiers ;
- manifeste exact, signature, version, empreinte et preuve de dépôt ;
- blocages, dérogations nominatives, confidentialité et abstention IA.

### P1 — Important après validation du socle

- profondeur MIRP par corps d’état et type d’ouvrage ;
- documents des sous-traitants/cotraitants et capacités tierces ;
- qualification réglementaire assistée des diagnostics conditionnels ;
- bibliothèques produits, FDES/PEP, PV et équivalences ;
- supports physiques, échantillons et prototypes ;
- dossiers attributaire et pré-démarrage ;
- passation structurée des livrables futurs vers l’exécution ;
- import/export avec GED, ERP/chiffrage et plateformes de conformité.

### P2 — Spécialisations avancées

- lecture métier approfondie DWG/IFC/SIG et métrés graphiques ;
- remplissage robuste des formats anciens, macros autorisées et formulaires propriétaires complexes ;
- contrôles spécialisés hospitalier, industrie, infrastructure, désamiantage et fluides médicaux ;
- intégration directe DUME, signature, profils acheteurs et services de preuves ;
- connaissance documentaire issue du retour réel de chantier.

Le modèle complet est défini dès maintenant. La réalisation commence par ce qui empêche une élimination, une erreur de prix ou un dépôt du mauvais dossier.

## 20. Critères d’acceptation métier

| Test | Résultat exigé |
|---|---|
| Inventaire | 100 % des fichiers et membres d’archives comptés ; toute impossibilité de lecture visible |
| Liste annoncée/reçue | chaque pièce annoncée est présente, manquante ou justifiée par un renvoi |
| Découverte | chaque pièce explicitement demandée dans les dossiers tests apparaît dans le registre avec sa source |
| Phase | offre, attributaire, pré-démarrage, exécution et DOE restent séparés |
| Portée | lot/site/variante/tranche correctement affectés ou marqués à confirmer |
| Modèle Word | titres, trame et consignes acheteur préservés ; ajouts identifiables |
| Modèle Excel | aucune formule, protection, feuille, ordre ou cellule non autorisée altérée silencieusement |
| Preuve tierce | aucune attestation ou certification fabriquée ; titulaire, périmètre et date contrôlés |
| Prix | tous postes attendus renseignés ou bloquants ; totaux entre pièces rapprochés |
| MIRP | l’absence d’une donnée P1 produit une explication causale et empêche un prix « prêt » sans dérogation |
| Diagnostic | la zone couverte et les limites d’investigation sont prises en compte, pas seulement le titre du rapport |
| Engagement | tout livrable post-attribution promis possède coût/charge, responsable et phase |
| Confidentialité | aucune marge, prix d’achat ou appréciation interne ne sort sans autorisation |
| Manifeste | nombre requis, présents, à obtenir, à décider et bloquants exact pour la version |
| Remise | l’empreinte des fichiers accusés correspond au paquet autorisé |
| Abstention | un fichier non lu ne peut contribuer à un statut « dossier complet » |

### 20.1 Dossiers de validation minimaux

1. AP-HP : mémoire par lot, cadre capacité et BPU ZIP avec liste de fiches techniques cachée dans l’archive ;
2. GHUC : 152 tableurs, affaire fictive, CRT, CQE, multi-sites et amiante ;
3. Filieris : phases offre/attribution, DPGF Excel, visite/dispense et RIB ;
4. Centrale : annexe RGPD, G2 PRO, RICT, amiante, plans et signature ;
5. Gendarmerie : multi-lots, méthode, environnement, planning, insertion et diagnostics ;
6. RN12 : 7z, notes additives, base/variante, SOPAQ/SOPRE, études environnementales, topo et plans lourds ;
7. cas artificiel hostile : pièce obligatoire citée uniquement dans un CCTP, modèle protégé, diagnostic hors périmètre, signature contradictoire et rectificatif tardif.

### 20.2 Recettes documentaires de clôture

Le [catalogue complet des recettes métier REC-01 à REC-28](/home/noor/PROJECTS/BTP/SMART_AO_V8/rapports/SMART_AO_Cahier_des_charges_Metier_v1.0.md#30-catalogue-de-recettes-métier) est la référence d’acceptation commune. Pour l’univers documentaire, les preuves minimales sont :

| Famille | Recettes de référence | Preuve attendue |
|---|---|---|
| Inventaire et versions | REC-01 à REC-04 | inventaire, source, version et liste d’impacts |
| Exigences et portée | REC-05 à REC-08 | extrait exact, applicabilité, titulaire et phase |
| Prix et MIRP | REC-09 à REC-13 | rapprochement, manque causal, décision et validateur |
| Privé et sous-traitance | REC-14, REC-18 à REC-20 | chaîne contractuelle, clause, source légale et arbitrage |
| Engagements et modèles | REC-21, REC-22 | engagement chiffré ou décidé ; original préservé |
| Remise et transmission | REC-23 à REC-25 | manifeste, empreinte, reçu et contrat final transmis |
| REX et abstention | REC-26 à REC-28 | fait séparé de l’hypothèse et absence d’invention |

## 21. Décisions de périmètre du propriétaire

Les dix arbitrages qui engagent le produit sont tenus dans le [registre DEC-01 à DEC-10 du cahier métier](/home/noor/PROJECTS/BTP/SMART_AO_V8/rapports/SMART_AO_Cahier_des_charges_Metier_v1.0.md). Ils restent ouverts jusqu’à décision du propriétaire.

Le présent référentiel en déduit quatre arbitrages documentaires à rendre lors de ces décisions : profondeur initiale du catalogue par corps d’état ; formats dont le traitement est garanti ; lieu et responsabilité de la bibliothèque entreprise ; licences permettant d’exploiter normes, bases produits et bases de prix. Aucun choix technique n’est arrêté dans ce document.

## 22. Backlog de validation externe

Le [registre VAL-01 à VAL-12 du cahier métier](/home/noor/PROJECTS/BTP/SMART_AO_V8/rapports/SMART_AO_Cahier_des_charges_Metier_v1.0.md#28-registre-de-validation-externe) constitue le backlog commun. Les cinq validations documentaires prioritaires sont :

| Priorité | Objet | Sortie exigée avant clôture de la ligne |
|---|---|---|
| 1 | corpus privé représentatif | au moins 15 dossiers anonymisés couvrant direct B2B, entreprise générale/sous-traitance, promotion/VEFA, maintenance et client protégé, avec avenants et clôture lorsque disponibles |
| 2 | MIRP multi-métiers | revue contradictoire par métreurs et conducteurs GO/réhabilitation, VRD, électricité, CVC-plomberie et second œuvre |
| 3 | formats difficiles | mesure sur XLS historiques, classeurs protégés, macros, PDF graphiques lourds, DWG/IFC ; limites publiées |
| 4 | règles conditionnelles | matrices validées assurance, amiante, géotechnique, SPS, PEMD, accessibilité et preuves de fin de travaux |
| 5 | licences et validités | droits d’usage et règles de fraîcheur contractualisés source par source |

Les constats suivants restent visibles : la preuve concurrentielle provient surtout des éditeurs ; les durées de validité ne sont pas généralisables ; deux plans lourds du corpus ont dépassé le temps d’extraction et un autre ne contenait pas de texte exploitable. Ils empêchent une promesse absolue de couverture, mais ne rouvrent pas l’exploration générale.

## 23. Conclusion

Le produit documentaire de SMART AO doit être défini comme un **système de complétude prouvée**. Il ne promet pas de connaître à l’avance tous les documents possibles. Il combine un catalogue extensible, une lecture dynamique de chaque DCE, les informations minimales nécessaires au prix et les preuves réelles de l’entreprise.

Le test décisif est atteint lorsqu’un patron peut charger un dossier inconnu et obtenir une réponse défendable :

> **Voici ce que l’acheteur a fourni, ce qui manque pour chiffrer, ce que vous devez remettre, ce que SMART AO peut remplir, ce qui doit venir d’un tiers, qui doit décider ou signer, et la preuve exacte que le paquet final est complet pour cette version.**

La recherche documentaire générale est close avec cette v1.0. Les inconnues restantes sont des lignes de validation identifiées ; elles seront levées par corpus, expert ou recette, et non par une nouvelle collecte indifférenciée.

## Sources

[^1]: Légifrance, [Code de la commande publique, article R. 2132-1 — définition et précision des documents de la consultation](https://www.legifrance.gouv.fr/jorf/article_jo/JORFARTI000037698313), version consultée le 11 septembre 2026.
[^2]: Service Public Entreprendre, [Répondre au marché : préparer le dossier offre](https://entreprendre.service-public.gouv.fr/vosdroits/F32154), mis à jour en 2026, consulté le 11 septembre 2026.
[^3]: Légifrance, [Code de la commande publique — offre irrégulière, articles L. 2152-2 et R. 2152-2](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000037730501/2026-04-22), version consultée le 11 septembre 2026.
[^4]: Légifrance, [Arrêté du 22 mars 2019 fixant la liste des renseignements et documents pouvant être demandés aux candidats](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000038318577/2026-02-09), version consultée le 11 septembre 2026.
[^5]: Direction des affaires juridiques, [Les formulaires de déclaration du candidat](https://www.economie.gouv.fr/daj/les-formulaires-de-declaration-du-candidat), versions DC1, DC2 et DC4 consultées le 11 septembre 2026.
[^6]: Service Public Entreprendre, [Remettre la réponse à un marché public et échanger avec l’acheteur](https://entreprendre.service-public.fr/vosdroits/F32106), version consultée le 11 septembre 2026.
[^7]: Service Public Entreprendre, [Préparer l’offre — présentation de l’offre financière](https://entreprendre.service-public.gouv.fr/vosdroits/F32154), consulté le 11 septembre 2026.
[^8]: Service Public Entreprendre, [Utiliser le service Document unique de marché européen](https://entreprendre.service-public.fr/vosdroits/R44043) ; DAJ, [Document unique de marché européen](https://www.economie.gouv.fr/daj/document-unique-de-marche-europeen-dume), consultés le 11 septembre 2026.
[^9]: Légifrance, [Code de la commande publique, examen des candidatures, articles R. 2144-1 à R. 2144-9](https://www.legifrance.gouv.fr/codes/id/LEGISCTA000037730577), version consultée le 11 septembre 2026.
[^10]: Légifrance, [Code de la commande publique, informations et documents à produire dans l’offre, articles R. 2151-12 à R. 2151-16](https://www.legifrance.gouv.fr/jorf/id/JORFSCTA000037696948), version consultée le 11 septembre 2026.
[^11]: Légifrance, [Arrêté du 22 mars 2019 sur la mise à disposition des documents et la copie de sauvegarde, article 2](https://www.legifrance.gouv.fr/loda/article_lc/LEGIARTI000047480156), version consultée le 11 septembre 2026.
[^12]: Légifrance, [Arrêté du 22 mars 2019 relatif à la signature électronique des contrats de la commande publique](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000038318621/), version consultée le 11 septembre 2026.
[^13]: DAJ, [Notice explicative du formulaire DC1](https://www.economie.gouv.fr/files/files/directions_services/daj/marches_publics/formulaires/DC/dc1.pdf?v=1588857792), consultée le 11 septembre 2026.
[^14]: Urssaf, [Obtenir et vérifier une attestation de vigilance](https://www.urssaf.fr/accueil/attestation-vigilance.html), mise à jour du 17 avril 2025, consultée le 11 septembre 2026.
[^15]: Service Public Entreprendre, [Garantie décennale et responsabilité professionnelle — exemple d’un métier du bâtiment](https://entreprendre.service-public.fr/vosdroits/F39038), consulté le 11 septembre 2026. Cette source illustre la nécessité de qualifier l’activité et ne constitue pas une règle uniforme pour tous les travaux.
[^16]: QUALIBAT, [Processus de qualification](https://www.qualibat.com/processus-qualification), durée, suivi annuel et renouvellement consultés le 11 septembre 2026.
[^17]: Service Public Entreprendre, [Attestation de régularité fiscale](https://entreprendre.service-public.fr/vosdroits/R14636), vérifiée le 3 février 2026, consultée le 11 septembre 2026.
[^18]: INERIS, [Guide d’application de la réglementation relative aux travaux à proximité des réseaux](https://www.reseaux-et-canalisations.ineris.fr/gu-presentation/userfile?path=%2Ffichiers%2Ftextes_reglementaires%2FGUIDE_LIVRET1v1_20220905.pdf) et [formulaires pratiques, marquage-piquetage](https://www.reseaux-et-canalisations.ineris.fr/gu-presentation/userfile?path=%2Ffichiers%2FGuides_techniques%2FFascicule3-Formulairesetautresdocumentspratiques-dcembre2016-version1-2017-04-14.pdf), consultés le 11 septembre 2026.
[^19]: Légifrance, [Code de la construction et de l’habitation, risques liés aux sols argileux, articles L. 132-4 à L. 132-9](https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006074096/LEGISCTA000041565555/2025-12-05) et [articles R. 132-3 à R. 132-8](https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006074096/LEGISCTA000043818703/2026-04-28/), versions consultées le 11 septembre 2026.
[^20]: Légifrance, [Arrêté du 4 juin 2024 relatif au repérage de l’amiante avant certaines opérations sur ouvrages de génie civil, infrastructures et réseaux](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000049834826/2024-09-24) ; INRS, [Amiante : réglementation](https://www.inrs.fr/risques/amiante/reglementation.html), consultés le 11 septembre 2026.
[^21]: Ministère de la Transition écologique, [Diagnostic produits, équipements, matériaux et déchets — PEMD](https://www.ecologie.gouv.fr/politiques-publiques/diagnostic-produits-equipements-materiaux-dechets-pemd), consulté le 11 septembre 2026.
[^22]: Ministère de la Transition écologique, [Traçabilité des déchets, terres excavées et sédiments](https://www.ecologie.gouv.fr/politiques-publiques/tracabilite-dechets-terres-excavees-sediments), consulté le 11 septembre 2026.
[^23]: Légifrance, [CCAG Travaux 2021, article 29 — études d’exécution](https://www.legifrance.gouv.fr/loda/article_lc/LEGIARTI000043315638), version consultée le 11 septembre 2026.
[^24]: Légifrance, [Code du travail, article L. 4532-8 — plan général de coordination SPS](https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072050/LEGISCTA000006189736/2026-06-23), version consultée le 11 septembre 2026.
[^25]: Légifrance, [Code du travail, coordination des opérations de bâtiment et génie civil, articles R. 4532-1 à R. 4532-98](https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072050/LEGISCTA000018491754/2026-02-21/), version consultée le 11 septembre 2026.
[^26]: Spigao, [Étapes de fabrication du dossier d’appel d’offres](https://www.spigao.com/blog/les-etapes-de-fabrication-du-dossier-dappel-doffres-spigao/), page éditeur consultée le 11 septembre 2026.
[^27]: Spigao, [Plateforme de gestion des appels d’offres BTP](https://www.spigao.com/) et [plaquette produit](https://www.spigao.com/wp-content/uploads/2022/09/Plaquette-SPIGAO.pdf), fonctions revendiquées/documentées par l’éditeur, consultées le 11 septembre 2026.
[^28]: Tenderbolt, [Analyse des consultations](https://www.tenderbolt.ai/fr/features/analysis) et [réponse aux bordereaux/RFQ](https://www.tenderbolt.ai/fr/features/rfq), pages éditeur consultées le 11 septembre 2026.
[^29]: Wanao, [Prévisualisation, recherche et analyse du DCE](https://wanao.com/nos-solutions/logiciel-de-gestion-des-appels-doffres-publics/dce-previsualisation-recherches-et-analyse/) et [Sendao, réponse dématérialisée](https://wanao.com/nos-solutions/reponse-dematerialisee-aux-marches-publics/), pages éditeur consultées le 11 septembre 2026.
[^30]: Libel, [Aide du logiciel de gestion des réponses aux appels d’offres publics](https://www.libel.fr/aide-GC/Bienvenue.html), centre d’aide public consulté le 11 septembre 2026.
[^31]: Doaken, [Logiciel de réponse aux appels d’offres](https://doaken.fr/), revendications commerciales consultées le 11 septembre 2026.
[^32]: BâtiOffre, [Copilote de réponse aux appels d’offres BTP](https://batioffre.fr/), revendications commerciales consultées le 11 septembre 2026.
[^33]: Titulis, [Dossier d’appel d’offres et remplissage des fichiers acheteur](https://titulis.fr/), revendications commerciales consultées le 11 septembre 2026.
[^34]: Avalanch, [Logiciel de réponse aux appels d’offres](https://avalanch.io/), revendications commerciales consultées le 11 septembre 2026.

[^35]: Légifrance, [Code civil, article 1103 — force obligatoire du contrat](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000032040777/2026-04-27), version en vigueur consultée le 12 septembre 2026.
[^36]: Fédération française du bâtiment, [Présentation de la révision 2026 de la NF P 03-001](https://www.ffbatiment.fr/pdf/%7BDAA5C1B6-E28A-45E1-A207-086C49E5DEA2%7D), consultée le 12 septembre 2026.
[^37]: Légifrance, [Loi n° 71-584 du 16 juillet 1971 relative aux retenues de garantie dans les marchés de travaux](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000687670), version en vigueur consultée le 12 septembre 2026.
[^38]: Légifrance, [Loi n° 75-1334 du 31 décembre 1975 relative à la sous-traitance](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000889241/2021-02-22), version consultée le 12 septembre 2026.
[^39]: Médiateur des entreprises, [Guide pratique pour améliorer la trésorerie dans les marchés privés de travaux](https://www.economie.gouv.fr/mediateur-des-entreprises/guide-pratique-ameliorer-la-tresorerie-dans-les-marches-prives-de-travaux), publié le 7 juillet 2026.
[^40]: Légifrance, [Code civil, article 1799-1 — garantie de paiement de l’entrepreneur](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000027645885/2024-09-01), version en vigueur consultée le 12 septembre 2026.
[^41]: Légifrance, [Décret n° 99-658 du 30 juillet 1999 fixant le seuil de garantie de paiement](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000578018/2024-04-21), version en vigueur consultée le 12 septembre 2026.

### Sources locales du corpus

- [AP-HP Sorbonne Université — dossier APHPSU26-023](/home/noor/PROJECTS/BTP/DOCUMENTATION/SMART_AO%20DOCUMENTATION/DCE%20Type/APHPSU26-023_MTE_DCE), consulté le 11 septembre 2026.
- [Accord-cadre travaux d’entretien GHUC](/home/noor/PROJECTS/BTP/DOCUMENTATION/SMART_AO%20DOCUMENTATION/DCE%20Type/02-DCE%20demat%20AC-Trx), consulté le 11 septembre 2026.
- [Centre médical Filieris](/home/noor/PROJECTS/BTP/DOCUMENTATION/SMART_AO%20DOCUMENTATION/DCE%20Type/CENTRE%20M%C3%89DICAL%20FILIERIS), consulté le 11 septembre 2026.
- [Centrale de groupes électrogènes et sécurisation électrique](/home/noor/PROJECTS/BTP/DOCUMENTATION/SMART_AO%20DOCUMENTATION/DCE%20Type/CENTRALE%20GROUPE%20ELEC), consulté le 11 septembre 2026.
- [Réhabilitation du bâtiment d’hôtellerie de la Gendarmerie de Dijon](/home/noor/PROJECTS/BTP/DOCUMENTATION/SMART_AO%20DOCUMENTATION/DCE%20Type/R%C3%A9habilitation%20b%C3%A2timent%20h%C3%B4tellerie%20cercle%20mixte%20Gendarmerie%20de%20Dijon), consulté le 11 septembre 2026.
- [RN12 — marché TACES](/home/noor/PROJECTS/BTP/DOCUMENTATION/SMART_AO%20DOCUMENTATION/DCE%20Type/VRD%20), consulté le 11 septembre 2026.
