# SMART AO — Expériences utilisateur, parcours et contrats de pages
## WORK_PROPOSAL v0.1

**Date : 14 septembre 2026**  
**Statut : DOCUMENT DE TRAVAIL — EXP-01 gelée ; EXP-02 à EXP-07 restent en proposition**  
**Prochaine sortie : première tranche verticale d'implémentation du contrat technique EXP-01**

## 0. Objet

Ce document décrit SMART AO dans l’ordre où les personnes l’utilisent réellement. Il relie les objectifs métier, les parcours, les pages, les états, les droits, les preuves, l’IA, les erreurs et la reprise avant leur traduction en maquettes détaillées puis en spécifications techniques.

Il ne remplace aucune autorité propriétaire :

1. [Cahier directeur Produit & Métier v0.4](../00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_CONSOLIDATED_v0.4.md) — produit et métier ;
2. [Catalogue UX v0.3](../00_REFERENCE_ACTIVE/SMART_AO_Catalogue_Ecrans_Parcours_Produit_OWNER_CONSOLIDATED_v0.3.md) — couverture et parcours ;
3. [Fondations UX v0.3](../00_REFERENCE_ACTIVE/SMART_AO_Prototype_UX_V0_Fondations_OWNER_CONSOLIDATED_v0.3.md) — règles communes de présentation et d’interaction.

Toute contradiction est remontée comme écart. Elle n’est jamais résolue par une invention silencieuse.

## 1. Doctrine de conception

### 1.1 L’expérience est l’unité de travail

Une page n’a de valeur que dans un parcours. Le document est donc organisé par **expériences métier de bout en bout**, puis par pages et états à l’intérieur de ces expériences.

### 1.2 Le contenu est candidat avant d’être gelé

Les statuts autorisés sont :

| Statut | Signification |
|---|---|
| `DRAFT` | cadrage incomplet ; aucune décision |
| `WORK_PROPOSAL` | parcours proposé et vérifiable |
| `CONTENT CANDIDATE` | contenu assez précis pour prototypage |
| `PROTOTYPE CANDIDATE` | parcours manipulable à éprouver |
| `TECHNICAL ASSESSED` | code existant, écarts et tests ciblés identifiés |
| `FEASIBILITY PROVEN` | chemin vertical minimal réellement exécutable et testé |
| `REVIEWED` | constats enregistrés et écarts traités |
| `OWNER EXPERIENCE FREEZE` | contenu, ordre, états et critères explicitement validés par le propriétaire |
| `VISUAL VALIDATED` | maquette détaillée conforme au gel et validée |
| `TECHNICAL READY` | traduction technique finale prête pour l’implémentation complète |
| `IMPLEMENTED` | tranche verticale vérifiée dans le produit |

Le mot `OWNER` n’est jamais attribué automatiquement par l’auteur, la maquette ou le code.

### 1.3 Une maquette n’invente pas

Une maquette peut révéler une lacune et proposer une correction. Elle ne peut ajouter silencieusement un KPI, un bouton, un droit, une action IA, un menu ou une promesse non décrite.

### 1.4 Une expérience n’est pas terminée au chemin heureux

Elle couvre, lorsque pertinent : vide, chargement, traitement, partiel, indisponible, interdit, erreur, bloqué, à revalider, non confirmé, conflit, panne IA, hors ligne et reprise.

## 2. Programme initial des expériences

| ID | Expérience | Résultat métier observable | Statut |
|---|---|---|---|
| **EXP-01** | Premier accès et première valeur | le Patron accède de manière sûre à son entreprise et atteint une première vue utile sans configuration exhaustive | **OWNER EXPERIENCE FREEZE — maquette détaillée et contrat technique consolidé rédigés ; implémentation suivante** |
| **EXP-02** | Opportunité vers Affaire | une opportunité sourcée est qualifiée, décidée et transformée en Affaire sans perte de provenance | **DRAFT** |
| **EXP-03** | Importer et comprendre un DCE | un dossier est admis, traité et synthétisé avec sources, versions, limites et reprise | **DRAFT** |
| **EXP-04** | Résoudre les points bloquants | exigences, inconnues, contradictions, risques et tâches sont traités sans fusion de leurs validations | **DRAFT** |
| **EXP-05** | Préparer la réponse et le chiffrage importé | les réponses et prix importés sont contrôlés, versionnés et validés selon droits | **DRAFT** |
| **EXP-06** | Préparer et remettre l’offre | candidate, contrôles, P5, export, dépôt humain et réception restent des actes distincts et prouvés | **DRAFT** |
| **EXP-07** | Passer, clôturer et capitaliser | le résultat, la passation, le REX et les éléments réemployables sont enregistrés avec portée et validité | **DRAFT** |

## 3. Contrat obligatoire d’une expérience

Chaque expérience doit renseigner les rubriques suivantes :

1. objectif et résultat attendu ;
2. acteurs et responsabilités ;
3. déclencheur et préconditions ;
4. parcours nominal ;
5. embranchements et décisions ;
6. pages et surfaces mobilisées ;
7. contrat détaillé de chaque page ;
8. données, sources, versions et fraîcheur ;
9. droits et confidentialité ;
10. IA contextuelle et voie manuelle ;
11. états difficiles et reprise ;
12. responsive et continuité entre appareils ;
13. preuves et journalisation visibles ;
14. risques produit, métier, UX et technique ;
15. critères d’acceptation et questions de recherche ;
16. matrice de couverture vers les 104 IDs, C00, C01–C16, N01–N05, PUX et G01–G52 ;
17. registre des décisions et arbitrages.

## 4. Contrat obligatoire d’une page

Une page est décrite par :

| Rubrique | Contenu attendu |
|---|---|
| Identité | ID stable, nom, expérience, espace global et contexte Affaire éventuel |
| Finalité | question à laquelle la page répond et résultat permis |
| Entrées | chemins d’arrivée, lien direct, notification, reprise |
| Sorties | prochaines actions, retour, abandon sans perte |
| Structure | rail, barre, bandeau, titre, zones principales, panneau ou modal |
| Contenu | libellés, données, ordre, regroupements, valeurs d’exemple |
| Actions | action principale, secondaires, sensibles, interdictions |
| Droits | visible, masqué, modifiable, validable, exportable, partageable |
| États | normal et états C00 applicables |
| Preuves | source, version, auteur, date, portée, accès au document |
| IA | intervention, source, limite, validation humaine et voie sans IA |
| Responsive | desktop, laptop, tablette, mobile compagnon |
| Accessibilité | clavier, focus, libellés, lecture, contraste et alternatives |
| Recette | critères observables de réussite et d’échec |

## 5. EXP-01 — Premier accès et première valeur

**Statut : OWNER EXPERIENCE FREEZE — synthèse d'expérience ; détails d'exécution dans les artefacts liés**

### 5.1 Objectif

Permettre au Patron/Propriétaire de sécuriser son accès, confirmer son entreprise, compléter uniquement les informations indispensables et atteindre une première valeur concrète dans SMART AO sans devoir configurer toute la Mémoire Entreprise.

### 5.2 Résultat attendu

À la fin de l’expérience :

- l’identité et le MFA obligatoire sont établis ;
- l’entreprise active et le rôle courant sont visibles ;
- la configuration minimale requise est connue et traçable ;
- le Patron peut créer ou rejoindre une première Affaire ;
- l’Accueil présente une action utile réelle, pas une démonstration fictive ;
- aucune donnée Direction n’est exposée à un profil non autorisé ;
- une interruption peut être reprise sans recommencer les étapes confirmées.

### 5.3 Acteurs à couvrir

| Acteur | Position dans EXP-01 |
|---|---|
| Patron / Propriétaire initial | acteur principal et autorité de configuration minimale |
| Propriétaire invité | variante : entreprise existante et droits déjà définis |
| Collaborateur invité | variante de confidentialité ; aucun pouvoir propriétaire implicite |
| Administrateur | assistance et visibilité bornées par les règles d’autorité |
| SMART AO | système, contrôles et assistance IA contextuelle sans décision autonome |

### 5.4 Parcours candidat

1. **PAGE-001 — Connexion** : identifier le compte et l’entreprise visée sans révéler l’existence d’informations interdites.
2. **PAGE-002 — Activation / MFA** : établir le second facteur et présenter clairement les options de récupération autorisées.
3. **PAGE-003 — Confirmation du contexte** : entreprise, rôle, éventuelle invitation et portée d’accès.
4. **PAGE-004 — Configuration minimale** : informations indispensables seulement ; le reste est différé et expliqué.
5. **PAGE-005 — Profil utilisateur** : identité professionnelle, préférences utiles et limites de modification.
6. **PAGE-006 — Première valeur** : créer une Affaire, rejoindre une Affaire invitée ou reprendre une configuration interrompue.
7. **PAGE-007 — Premier Accueil composé** : prochaine action, points à surveiller et événements selon les droits réels.

Cette liste reste candidate. Elle doit être confrontée aux écrans C15, C01 et C03 du catalogue, au code existant et aux scénarios d’invitation avant gel.

### 5.5 États difficiles obligatoires

- invitation expirée, révoquée ou déjà utilisée ;
- MFA indisponible ou récupération nécessaire ;
- entreprise inconnue sans révélation d’existence ;
- dernier Propriétaire compromis ou suspendu selon la règle propriétaire ;
- configuration enregistrée partiellement ;
- action confirmée côté client mais résultat serveur non confirmé ;
- panne IA sans blocage de l’accès ou de la configuration manuelle ;
- lien direct vers une page devenue interdite ;
- reprise sur un autre appareil ;
- session expirée avant une action sensible.

### 5.6 Risques à traiter avant contenu freeze

| Risque | Preuve attendue avant gel |
|---|---|
| onboarding trop long | le premier résultat utile est atteint sans configuration exhaustive |
| confusion entreprise / Affaire | les deux contextes sont compris sans explication orale |
| pouvoir implicite du titre | les actions visibles correspondent aux droits effectifs |
| perte après interruption | les étapes confirmées sont restaurées et les étapes incertaines signalées |
| accueil vide ou décoratif | une prochaine action réelle est proposée selon la situation |
| MFA vécu comme impasse | récupération, aide et conséquences sont compréhensibles |

### 5.7 État observé du code et portée de l’expérience

Les constats suivants proviennent du code et de ses tests. Ils décrivent l’état actuel ; ils ne sont pas une autorité produit.

| Surface | Observé dans le code | Conséquence pour EXP-01 |
|---|---|---|
| Connexion | Le front demande actuellement email, mot de passe et `tenant_id` technique ; le backend crée une session après mot de passe. | Le contrat UX propose de ne jamais demander cet identifiant technique à une personne. Le futur contrat technique devra résoudre l’organisation sans en divulguer l’existence. |
| Sessions | Jeton d’accès en mémoire, cookie de renouvellement HttpOnly, rotation de session et garde serveur existent. Le front mémorise le dernier contexte confirmé et le masque après expiration. | La reprise minimale est prouvée pour le même acteur après rechargement confirmé ; la persistance de brouillon, l’avertissement pré-expiration et l'alignement des durées restent à concevoir. |
| MFA | Le backend couvre l’enrôlement TOTP, les codes de récupération et le step-up ; le front limite désormais une session `PASSWORD` à PAGE-002. | La garde commune des routes métier impose la MFA avant tout accès interne. |
| Premier Propriétaire | Un service de provisioning et de bootstrap crée un premier Patron nominatif à partir d’un secret à usage unique. | Il n’existe pas encore de parcours produit visible correspondant ; PAGE-002 et PAGE-003 doivent le rendre intelligible sans inscription publique. |
| Invitations et récupération | Le serveur émet une invitation de collaborateur valable 7 jours, conserve uniquement le hash, réémet sans doublon et accepte une invitation sous consommation unique. La récupération exige une session `PASSWORD` récente et un code de secours ; elle révoque sessions, refresh et facteur, puis impose un nouveau TOTP. | Le code de secours est refusé en step-up et le chemin email seul n'existe pas. L'écran visuel de récupération reste à concevoir. |
| Contexte | `/auth/me` retourne l'espace entreprise, le rôle effectif et l'état MFA ; le front exige leur confirmation avant tout chargement métier. | PAGE-003 est exécutable ; le nom légal remplacera le slug lorsque cette donnée deviendra un prérequis qualifié. |
| Première Affaire | PAGE-006 réemploie le formulaire existant et conserve les mêmes identifiants de commande après une réponse perdue. | La création réelle puis son rejeu retournent la même Affaire sans doublon ; une réponse perdue affiche « Création à vérifier » sans succès présumé. |
| Accueil | Le front compose « À faire maintenant », « À surveiller » et les événements d'affectation depuis les projections autorisées existantes. | PAGE-007 possède une première preuve réelle ; la navigation canonique, les notifications et l'Administration restent à consolider. |

L'évaluation et les preuves exécutées sont consignées dans [EXP-01 — Évaluation technique](SMART_AO_EXP_01_Evaluation_Technique_WORK_PROPOSAL_v0.1.md). Le parcours nominal PAGE-001 à PAGE-007, l'invitation nominative, la récupération assistée, le changement de contexte, la reprise de création et la reprise minimale après expiration possèdent une preuve verticale. La persistance des brouillons et les variantes de politique de session restent à produire.

### 5.8 Parcours nominal candidat

```text
environnement provisionné ou invitation nominative
→ PAGE-001 Connexion
→ PAGE-002 Activation ou challenge MFA
→ PAGE-003 Confirmation entreprise et rôle
→ PAGE-004 Configuration minimale, si nécessaire
→ PAGE-005 Profil personnel, si nécessaire
→ PAGE-006 Première valeur : créer, rejoindre ou reprendre une Affaire
→ PAGE-007 Accueil composé et reprise du travail
```

Une étape déjà confirmée est sautée sans être masquée : le résumé du contexte reste accessible. Une interruption revient au dernier état confirmé ; une action dont le résultat est incertain ouvre l’état N02 avant toute répétition.

### 5.9 Couverture du catalogue

| Page | Contrats de couverture principaux | Espaces et règles transversales |
|---|---|---|
| PAGE-001 | AUTH-01, AUTH-07, AUTH-08 | C15, C00, R03, R13, R16 |
| PAGE-002 | AUTH-02 à AUTH-06 | C15, C00, R02, R03, OWN-01, OWN-03, OWN-04 |
| PAGE-003 | ONB-01, AUTH-02, AUTH-08 | C15, C14, R02, R03, R13 |
| PAGE-004 | ONB-03, ONB-04 | C15, C13, C01, R03, R13 |
| PAGE-005 | GLB-05, AUTH-07 | C00, C14, R03, R16 |
| PAGE-006 | ONB-02, OPP-04, AFF-01 | C01, C03, C04, R01, R02 |
| PAGE-007 | C01, HOME-01 à HOME-03, GLB-03 à GLB-05 | C00, R02, R03, R13, R15, R16 |

### 5.10 PAGE-001 — Connexion

**Statut : CONTENT CANDIDATE**  
**Finalité :** permettre à une personne déjà provisionnée ou invitée de demander l’accès sans révéler si un compte, une organisation ou une invitation existe.

| Rubrique | Contrat candidat |
|---|---|
| Entrées | lien d’invitation, retour après expiration de session, ouverture directe de SMART AO, accès refusé à une page protégée |
| Structure | marque SMART AO ; titre « Accéder à votre espace » ; court rappel de la confidentialité ; formulaire ; lien « Besoin d’aide pour accéder à votre compte ? » |
| Contenu | adresse professionnelle ; mot de passe ; message neutre sur les accès organisés par invitation ou provisioning ; aucun identifiant interne d’organisation affiché ou demandé |
| Action principale | `Continuer` |
| Actions secondaires | ouvrir l’aide à la récupération ; revenir à l’invitation si le parcours vient d’un lien nominatif |
| Sortie normale | PAGE-002 ; le contexte d’entreprise n’est confirmé qu’après les contrôles nécessaires |
| Droits | aucune donnée métier, aucun titre d’Affaire, aucun compteur ni indice d’existence avant authentification complète |
| États | attente ; refus neutre ; limitation temporaire ; session expirée ; indisponibilité de service ; retour à la destination autorisée après succès |
| Preuve | événement d’accès et motif technique minimal ; jamais mot de passe, facteur secret ou contenu métier |
| IA | aucune intervention IA |
| Responsive et accessibilité | champ email avec aide de saisie ; mot de passe masqué par défaut avec contrôle explicite ; clavier complet ; erreurs liées aux champs ; aucune information transmise uniquement par couleur |

**Microcopies candidates :**

- refus : « Les informations saisies ne permettent pas d’accéder à cet espace. Vérifiez-les ou utilisez la récupération d’accès. »
- session expirée : « Votre session a expiré. Reconnectez-vous pour reprendre le dernier travail confirmé. »
- accès direct interdit : « Cette page nécessite une connexion. Après vérification de vos droits, vous reviendrez à l’emplacement autorisé. »

**Règle de conception :** le champ `tenant_id` observé dans le front actuel est un détail technique. Il ne doit pas apparaître dans la cible produit. Cette proposition n’autorise pas une inscription libre.

### 5.11 PAGE-002 — Activation, MFA ou récupération

**Statut : CONTENT CANDIDATE**  
**Finalité :** établir ou vérifier le second facteur avant tout accès métier interne, puis permettre une récupération réellement sécurisée sans transformer le support en décideur métier.

| Variante | Contenu et action |
|---|---|
| Première activation | rappeler l’entreprise et l’adresse masquée ; expliquer pourquoi le MFA est requis ; proposer l’enrôlement ; afficher les codes de récupération une seule fois avec confirmation de conservation ; demander la preuve TOTP avant de continuer |
| Utilisateur déjà enrôlé | demander le code MFA ; annoncer seulement l’action « accéder à SMART AO » ; ne pas révéler d’Affaire ou de droit avant validation |
| Code de récupération | expliquer qu’un code est à usage unique ; après succès, imposer le nouvel enrôlement avant l’accès métier |
| Invitation expirée ou révoquée | indiquer que le lien ne peut plus être utilisé ; proposer de demander une nouvelle invitation sans révéler de privilège antérieur |
| Récupération normale | expliquer le parcours : moyen de secours ou validation par Propriétaire habilité, révocation des anciens facteurs, nouvel enrôlement et notification de sécurité |
| Dernier Propriétaire inaccessible | écran exceptionnel accompagné ; collecte de demande sans donner de droit ; aucune promesse de récupération ni visibilité de données |

L’action principale est contextualisée : `Activer le MFA`, `Vérifier et continuer`, `Utiliser un code de récupération` ou `Demander une nouvelle invitation`. Le retour ne détruit jamais une activation confirmée.

**Interdictions :** pas de secret MFA dans un journal, pas de restauration par seul email, pas de chemin de support donnant accès au contenu, pas de confusion entre MFA initial et step-up d’une action sensible.

**Contrat backend actuellement codé :** `POST /api/v1/invitations/accept` reçoit le jeton et le mot de passe, active l’identité et le membership dans une transaction, puis renvoie `204` sans identité. La page de saisie reste à produire ; la preuve runtime PostgreSQL et la transition vers l’enrôlement MFA sont acquises côté serveur.

### 5.12 PAGE-003 — Confirmation de l’entreprise et du rôle

**Statut : CONTENT CANDIDATE**  
**Finalité :** rendre lisibles l’organisation, le rôle effectif et la portée d’accès avant le premier travail.

| Rubrique | Contrat candidat |
|---|---|
| Structure | titre « Votre espace SMART AO » ; carte entreprise ; carte rôle et périmètre ; explication courte de la différence entre rôle métier, propriété de l’organisation et droits sensibles |
| Contenu | nom de l’entreprise, personne invitante lorsque applicable, rôle proposé, état de l’invitation, date d’expiration si encore pertinente, périmètre résumé ; aucune donnée Direction ou liste de personnes non nécessaire |
| Action principale | `Confirmer et continuer` |
| Actions secondaires | `Ce contexte n’est pas le bon` ; `Demander de l’aide` |
| Sorties | PAGE-004 si une donnée minimale manque ; PAGE-005 ou PAGE-006 si le contexte est complet |
| États | invitation déjà acceptée ; rôle retiré entre lien et confirmation ; entreprise désactivée ; droit insuffisant ; résultat de confirmation non confirmé N02 |
| Preuve | auteur de l’invitation ou du provisioning, date, portée et état ; aucune révélation d’autres délégations |
| IA | aucune intervention nécessaire |

La page rend visible le cumul éventuellement autorisé « Propriétaire d’organisation » et « Patron », sans prétendre que l’un donne automatiquement les droits de l’autre.

### 5.13 PAGE-004 — Configuration minimale de l’entreprise

**Statut : CONTENT CANDIDATE**  
**Finalité :** recueillir uniquement ce qui est nécessaire pour commencer une première Affaire ou répondre à un prérequis d’identité ; reporter le reste dans une checklist reprise depuis C01.

| Rubrique | Contrat candidat |
|---|---|
| Structure | progression explicite « Étape nécessaire pour démarrer » ; liste courte des données demandées ; bloc « Vous pourrez compléter le reste plus tard » ; accès à l’aide accompagnée |
| Données admises | données d’identité d’entreprise déjà connues ou nécessaires au premier usage, selon le mode de provisioning ; aucune collecte de Mémoire Entreprise, prix, personnel ou document réutilisable pour franchir cette étape |
| Action principale | `Enregistrer et continuer vers ma première Affaire` |
| Actions secondaires | `Enregistrer et reprendre plus tard`, seulement si les champs restants ne sont pas un prérequis réel ; ouvrir l’aide accompagnée |
| États | donnée invalide expliquée par champ ; enregistrement en cours ; dernier état confirmé ; résultat non confirmé ; interruption et reprise ; fonction de service indisponible avec données saisies conservées localement comme non confirmées |
| Preuve | auteur, date, version confirmée et source du renseignement si importé ; aucune promesse d’exactitude non contrôlée |
| IA | aide à expliquer un champ seulement ; aucune déduction de données d’entreprise ni publication autonome |

La liste exacte des champs est volontairement laissée à la vérification des données existantes et des obligations qualifiées. La page ne crée pas silencieusement une exigence de SIREN, de marque ou de profil complet.

### 5.14 PAGE-005 — Profil personnel et préférences utiles

**Statut : CONTENT CANDIDATE**  
**Finalité :** permettre à la personne de vérifier ses informations professionnelles visibles et de régler les préférences ordinaires sans mélanger identité, droits et sécurité.

| Rubrique | Contrat candidat |
|---|---|
| Structure | section identité ; section préférences ; section sécurité qui renvoie vers le parcours dédié ; résumé du rôle sans mécanisme d’élévation |
| Contenu | nom affiché, fonction professionnelle, langue et préférences de notification ordinaires ; l’avatar éventuel est décoratif et facultatif ; email et identité vérifiée sont distingués des préférences |
| Action principale | `Continuer vers ma première Affaire` ou `Ouvrir mon Accueil` selon l’état d’EXP-01 |
| Actions secondaires | modifier une préférence ordinaire ; consulter les sessions et la sécurité sur un parcours dédié |
| Interdictions | aucune modification de rôle, délégation, droit Direction, MFA ou propriété depuis cette page sans le parcours et l’autorité propres |
| États | profil incomplet non bloquant ; sauvegarde non confirmée ; session expirée ; champ non modifiable expliqué ; droit retiré entre affichage et sauvegarde |
| Accessibilité | libellés explicites ; préférences regroupées par effet ; confirmation textuelle après sauvegarde |

### 5.15 PAGE-006 — Première valeur : créer, rejoindre ou reprendre une Affaire

**Statut : CONTENT CANDIDATE**  
**Finalité :** faire arriver le Patron à une première valeur concrète sans le forcer à configurer une bibliothèque complète ou à inventer des données.

| Situation | Proposition de contenu et action |
|---|---|
| Première Affaire manuelle | expliquer que le périmètre est enregistré avant toute lecture de DCE, chiffrage ou décision ; demander titre, objet, périmètre, lots si connus, origine et justification ; `Créer l’Affaire` |
| Opportunité existante | afficher une opportunité autorisée, sa source, sa fraîcheur et ses inconnues ; `Ouvrir et qualifier l’opportunité` plutôt que créer un doublon |
| Invitation à une Affaire | afficher le nom autorisé, le rôle et le périmètre ; `Rejoindre l’Affaire` ; conserver l’invitation comme preuve |
| Configuration interrompue | indiquer ce qui est confirmé et ce qui reste à faire ; `Reprendre la configuration` |
| Aucune action disponible | état vide réel : « Votre accès est actif, mais aucune Affaire ne vous est encore attribuée. » ; proposer la demande ou l’aide adaptée sans fausse urgence |

L’action principale dépend du contexte, mais reste unique. Une création réussie ouvre le contexte de l’Affaire créée avec son origine et son périmètre ; un résultat non confirmé n’autorise pas une seconde création avant vérification.

**Observé dans le code :** le formulaire actuel couvre déjà titre, objet, type de périmètre, lots, tranche, variante, origine et justification, avec commande idempotente. La présentation cible doit conserver cette sécurité, tout en supprimant les choix non nécessaires selon le contexte de première valeur.

### 5.16 PAGE-007 — Premier Accueil composé

**Statut : CONTENT CANDIDATE**  
**Finalité :** faire comprendre immédiatement où l’on se trouve, ce qui compte maintenant et quelle action utile est possible, selon les droits effectifs.

| Zone | Contenu candidat |
|---|---|
| Barre supérieure | entreprise active, rôle affiché, accès aux notifications, état de session et profil ; aucune donnée sensible exposée par un compteur ou un libellé |
| Navigation | cinq espaces canoniques : Accueil, Opportunités, Affaires, Entreprise, Administration ; les destinations non accessibles sont absentes ou expliquées sans révéler leur contenu |
| À faire maintenant | décisions, contributions ou prérequis réellement ouverts et autorisés ; une condition ancienne reste visible ; action principale contextualisée |
| À surveiller | échéances, informations partielles, éléments à revalider ou risques autorisés ; chaque ligne dit pourquoi elle apparaît et mène à sa preuve |
| Événements | informations récentes séparées des décisions ; lire ou reporter un événement ne ferme jamais un blocage métier |
| Checklist progressive | uniquement les compléments d’entreprise utiles au prochain travail ; aucune note de complétude décorative ni sanction du profil incomplet |
| État vide | proposer une première Affaire, une opportunité, une invitation ou une action de demande selon le rôle ; ne jamais afficher un tableau de bord fictif |

**États obligatoires :** chargement localisé sans masquer les zones déjà disponibles ; données partielles avec cause et portée ; droit insuffisant sans fuite ; panne IA laissant les actions manuelles accessibles ; lien direct vers objet retiré ; session expirée avec retour au dernier état confirmé ; N01 conflit et N02 résultat non confirmé quand ils concernent une action visible.

### 5.17 Matrice rôles × informations × actions

| Profil | Voit dans EXP-01 | Peut faire | Ne déduit jamais |
|---|---|---|---|
| Premier Propriétaire / Patron | son entreprise, son rôle effectif, sa configuration requise et les Affaires qu’il peut ouvrir | activer MFA, confirmer le contexte, configurer le minimum, créer une première Affaire selon son autorité | marges, droits Direction ou délégations non attribués explicitement |
| Propriétaire invité | son invitation, son périmètre et les actions autorisées | activer MFA, accepter, reprendre le travail autorisé | identité ou droits détaillés des autres membres |
| Collaborateur invité | son entreprise, son rôle et sa portée de contribution | activer MFA, accepter, ouvrir ses travaux autorisés | données Direction, liste intégrale d’Affaires, administration ou pouvoir Patron |
| Administrateur | les métadonnées d’accès nécessaires à sa tâche | accompagner un parcours autorisé, appliquer une attribution approuvée | contenu métier, prix, marges ou droit de s’élever lui-même |
| Support SMART AO | métadonnées minimales seulement, après l’autorisation exigée | diagnostiquer dans son périmètre, appliquer la procédure de récupération à plusieurs intervenants | pouvoir métier, contenu ou réattribution sur simple demande |

### 5.18 Conditions de passage à un prototype basse fidélité

EXP-01 peut passer en `PROTOTYPE CANDIDATE` quand les éléments suivants sont vérifiés :

- les variantes premier Propriétaire, utilisateur invité, collaborateur invité et récupération sont représentées ;
- aucun écran ne demande un identifiant technique d’organisation ;
- le MFA précède tout accès métier interne ;
- les retours session, droits insuffisants et résultat non confirmé sont parcourables ;
- PAGE-006 mène à une première valeur réelle ;
- PAGE-007 sépare décisions, surveillance et événements ;
- les écarts avec le code sont étiquetés pour le futur contrat technique ;
- aucune règle produit v0.4 ou v0.3 n’est modifiée.

### 5.19 Décisions propriétaire à solliciter seulement si nécessaire

**Aucune réouverture propriétaire n’est demandée à ce stade.** Les points encore ouverts sont des précisions de contenu, de données disponibles et de faisabilité à résoudre dans la suite de l’analyse. Si une telle précision devait modifier OWN-01 à OWN-13, R01 à R16, le catalogue v0.3 ou une porte P0–P7, elle sera présentée séparément comme `PROPOSITION DE RÉOUVERTURE PROPRIÉTAIRE`.

## 6. Registre des arbitrages

| ID | Sujet | Statut |
|---|---|---|
| EXP-GOV-01 | Concevoir par expérience complète plutôt que par frame isolée | **APPLIQUÉ PAR FONDATIONS UX v0.3** |
| EXP-GOV-02 | Utiliser `CONTENT CANDIDATE` avant le prototype | **APPLIQUÉ PAR FONDATIONS UX v0.3** |
| EXP-GOV-03 | Déclarer `OWNER EXPERIENCE FREEZE` après prototype et revue | **APPLIQUÉ PAR FONDATIONS UX v0.3** |
| EXP-GOV-04 | Faire intervenir métier, UX, technique, sécurité et accessibilité avant gel | **APPLIQUÉ PAR FONDATIONS UX v0.3** |
| EXP-GOV-05 | Prouver une tranche verticale minimale avant gel, puis traduire l’expérience gelée en implémentation complète | **MÉTHODE ADOPTÉE ; EXP-01 EN ÉVALUATION TECHNIQUE** |

## 7. Limites actuelles

Aucune page de ce document ne remplace le gel dédié. Le parcours nominal PAGE-001 à PAGE-007, l'invitation nominative, la récupération assistée, le changement de contexte, la reprise de création et la reprise minimale après expiration possèdent une preuve verticale et sont maintenant traduits dans la [maquette détaillée EXP-01](SMART_AO_EXP_01_MAQUETTE_DETAILLEE_OWNER_FREEZE_v0.1.md) et le [contrat technique consolidé](../02_FUTURE_TECHNICAL/SMART_AO_EXP_01_CAHIER_TECHNIQUE_EXECUTION_v0.1.md). La persistance des brouillons, les tests avec des utilisateurs représentatifs et les variantes hors EXP-01 restent à réaliser. Le présent document organise le travail ; il ne constitue pas le Product Freeze global.
