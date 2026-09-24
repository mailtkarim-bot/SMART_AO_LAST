# SMART AO — Fondations UX du prototype V0
## OWNER_CONSOLIDATED v0.3

**Date : 14 septembre 2026**  
**Révision : v0.3-R1 — gouvernance de conception par expériences métier, prototypes testables et tranches verticales.**  
**Statut : RÉFÉRENCE UX PROPRIÉTAIRE ACTIVE — fondations conservées ; ancienne séquence V0-01 à V0-16 remplacée comme ordre de fabrication par une boucle expérience → prototype → validation → freeze → spécification technique → implémentation.**  
**Autorités supérieures : Cahier directeur Produit & Métier OWNER_CONSOLIDATED v0.4, puis Catalogue UX OWNER_CONSOLIDATED v0.3.**  
**Version remplacée : `SMART_AO_Prototype_UX_V0_Fondations_OWNER_CONSOLIDATED_v0.2.md` — conservée en archive, non active.**

## 0. Objet, portée et règle de lecture

Ce document définit **les fondations propriétaires communes de la conception UX** : comment SMART AO doit se présenter et se comporter dans chaque expérience, prototype et future tranche fonctionnelle. Il couvre les 104 contrats de surface : shell, navigation, densité, langage métier, états, preuve, autorité, confidentialité, assistance IA et adaptation aux écrans.

Le [catalogue UX propriétaire v0.3](SMART_AO_Catalogue_Ecrans_Parcours_Produit_OWNER_CONSOLIDATED_v0.3.md) fait foi pour C00, C01–C16, N01–N05, PUX-01–PUX-19, les huit corrections UX-C1 et les douze innovations I01–I12. Le [cahier produit v0.4](SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v2.0.md) reste supérieur sur le métier, les droits, les portes P0–P7 et l’autorité. Le présent OWNER_CONSOLIDATED v0.3 conserve les décisions UX adoptées en v0.2 et change leur méthode de matérialisation ; toute contradiction se résout en faveur des autorités supérieures.^1

La conception ne part plus d’une succession de frames isolées. Elle part d’une **expérience métier de bout en bout**, décrite par ses acteurs, résultats, pages, données, droits, états, preuves, erreurs et critères de réussite. Le contenu est d’abord candidat, puis prototypé et éprouvé. Le gel propriétaire intervient après cette boucle ; une maquette ne peut ni inventer une capacité ni masquer un état exigé.

Les termes suivants qualifient les propositions :

- **OBSERVÉ** : comportement visible dans une documentation, une capture publique ou une démonstration citée ; cela ne signifie pas qu’un compte client a été testé.
- **AFFIRMATION ÉDITEUR** : promesse du fournisseur, non traitée comme résultat indépendant.
- **RETOUR UTILISATEUR** : témoignage public dont la représentativité, la version et les intérêts ne sont pas établis.
- **INFÉRENCE** : analyse tirée des sources et des contraintes SMART AO.
- **PROPOSITION SMART AO** : règle ou interaction recommandée, encore à éprouver.

La cible est le poste desktop et le laptop 13–14 pouces. La tablette et le mobile compagnon sont conçus dès V0, sans transformer le produit en poste d’étude mobile. Le document ne choisit ni framework, ni bibliothèque, ni architecture technique.

### 0.1 Arbitrage propriétaire et statut des propositions Work

La contre-proposition Work est **adoptée dans sa direction et consolidée** sous les règles suivantes :

| ID | Décision propriétaire | Statut v0.3 |
|---|---|---|
| **PROP-01** | Rail global + barre supérieure + bandeau Affaire collant. | **ADOPTÉ** |
| **PROP-02** | Une action principale par vue/état ; microcopy `verbe + objet + version/portée` pour toute action sensible. | **ADOPTÉ** |
| **PROP-03** | Preuve à un geste ; document complet à deux gestes ; bascule en mode large dès que le panneau devient insuffisant. | **ADOPTÉ** |
| **PROP-04** | Grammaire métier multi-signaux : nature, marqueur/forme, position stable, état textuel, couleur secondaire. | **ADOPTÉ** |
| **PROP-05** | Accueil commun structuré en `À faire maintenant / À surveiller / Événements`, composé selon droits et responsabilités. | **ADOPTÉ** |
| **PROP-06** | C05 « À résoudre » filtrable par conséquence métier : décision, prix, réponse, remise, contributions. | **ADOPTÉ** |
| **PROP-07** | Actualisation IA ciblée sur les changements, avec date, périmètre et possibilité de recalcul autorisé. | **ADOPTÉ** |
| **PROP-08** | Responsive par transformation liste/détail et non par compression du desktop. | **ADOPTÉ** |
| **PROP-09** | Grille, spacing et hiérarchie typographique définis dès V0 pour garantir la cohérence des prototypes. | **ADOPTÉ POUR LE PROTOTYPE** — ne fige pas encore la charte de marque finale. |

**Aucune réouverture propriétaire n’est retenue.** Les cinq espaces globaux, l’autorité humaine, les portes P0–P7, le dépôt final humain en V1, la confidentialité Direction, le mobile compagnon et la frontière avec le chiffrage complet/ERP restent inchangés. Le cache documentaire hors ligne étendu reste une option future à qualifier, pas une capacité V0.

### 0.2 Précédence documentaire

Pour toute décision V0 :

1. `SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v2.0.md` — autorité produit/métier ;
2. `SMART_AO_Catalogue_Ecrans_Parcours_Produit_OWNER_CONSOLIDATED_v0.3.md` — autorité UX de couverture et de parcours ;
3. **le présent `SMART_AO_Prototype_UX_V0_Fondations_OWNER_CONSOLIDATED_v0.3.md`** — autorité de fondations visuelles et interactionnelles ;
4. expériences portant un statut `OWNER EXPERIENCE FREEZE` — contenu et enchaînement propriétaires validés pour leur périmètre ;
5. maquettes/prototypes validés — matérialisation des contrats, sans pouvoir les réécrire silencieusement ;
6. futur cahier technique d’exécution — traduction technique, sans pouvoir modifier silencieusement le produit.

Les versions Work v0.1 et OWNER_CONSOLIDATED v0.2 sont des **sources historiques de recherche, benchmark, arbitrage et raisonnement de conception**. Elles ne font plus foi en cas d’écart avec la présente version.

## A — Principes UX directeurs

Ces principes sont des critères de recette. Une maquette qui les contredit doit être corrigée ou explicitement arbitrée.

### A1. L’utilisateur sait toujours où et pour quoi il agit

Le nom de l’organisation active reste visible dans le shell. Dans une Affaire, le bandeau de contexte affiche toujours : **Affaire, entreprise candidate, lot, phase, tour et échéance de référence**. Une valeur inconnue est écrite « Non déterminé » ; le champ n’est jamais supprimé pour donner une impression de complétude.

**Test V0** : après ouverture directe d’un lien, une personne peut nommer l’Affaire, le lot, la version concernée et l’effet de l’action sans revenir à l’accueil.

### A2. Le produit présente d’abord le travail ou la décision, puis l’historique

L’Accueil ne cherche pas à résumer toute l’entreprise. Il présente ce qui attend l’utilisateur : décision pour une autorité, travail pour un responsable, contribution pour un expert. Les événements récents sont disponibles dans une vue séparée. Le simple fait qu’une information soit nouvelle ne la rend pas prioritaire.

**Test V0** : un Patron trouve l’ensemble des arbitrages urgents en 60 à 90 secondes, explique pourquoi ils lui sont présentés et retrouve leur preuve.

### A3. Chaque ligne opérationnelle répond à six questions

Une ligne utile permet de comprendre : **quoi, de quelle nature, dans quel contexte, pourquoi maintenant, qui agit, et quelle preuve manque ou existe**. Toute liste structurante possède une colonne ou sous-ligne d’action attendue. Les compteurs servent à retrouver les objets ; ils ne remplacent jamais leur qualification.

**Test V0** : en masquant la couleur et les icônes, la ligne reste compréhensible.

### A4. Un objet métier conserve sa nature

Une exigence, une contradiction, un inconnu, une hypothèse, un risque et une tâche peuvent apparaître dans la même file C05. Ils ne partagent pas un statut générique « ouvert/fermé ». La tâche décrit le travail ; l’objet métier décrit ce qui est ou n’est pas établi. « Tâche terminée » n’implique aucune conformité.

**Test V0** : clôturer une tâche liée à une exigence sans joindre ni valider de preuve laisse l’exigence ouverte et explique la suite attendue.

### A5. La preuve est à un geste, la complexité complète à deux

Le premier geste ouvre le panneau de preuve sur l’extrait, la source, la version et la qualification. Le second ouvre le document en mode large à l’emplacement exact. Le panneau ne prétend pas remplacer une lecture longue. Il se ferme en restaurant le filtre, la ligne sélectionnée, la position et le focus.

Ce modèle reprend le bénéfice du « peek » documenté par Linear — inspecter sans perdre la liste — et les précautions de Carbon : si le contenu devient complexe ou exigu, il mérite une vraie vue ou un panneau dédié.^2 ^3

### A6. Une action engageante nomme son objet et son effet

Les boutons « Valider », « Confirmer » et « Terminer » sont interdits lorsqu’ils ne précisent pas l’effet. Utiliser : « Autoriser le paquet v7 », « Marquer cette contribution revue », « Enregistrer la preuve de réception », « Révoquer les futurs accès ». Les actions secondaires ne sont pas visuellement concurrentes avec l’action principale.

**Test V0** : une personne peut prédire l’effet et la réversibilité avant de cliquer.

### A7. Le statut décrit ce qui est établi, pas ce que l’on espère

« Export préparé », « transmission déclarée », « réception prouvée » et « contenu rapproché » sont quatre états possibles. « Traitement en cours » n’est pas « terminé bientôt ». « Résultat non confirmé » n’est ni succès ni échec. La terminologie des transactions asynchrones de Stripe montre l’utilité de statuts séparés plutôt qu’un unique état binaire.^4

**Test V0** : après perte de réponse réseau, le produit explique le dernier état confirmé et interdit une répétition risquée avant vérification.

### A8. La confidentialité commence avant l’affichage

Les droits filtrent les lignes, compteurs, regroupements, suggestions IA, recherches, exports et historiques avant calcul ou composition. Les pages ne montrent pas des cartes vides intitulées « Marge restreinte » à un rôle qui ne doit pas savoir qu’une analyse de marge existe dans ce dossier. Une interface fusionnée ne fusionne aucun droit.

**Test V0** : comparer Patron, Responsable, Métreur, DAF, Admin et tiers sur la même Affaire ; aucune valeur ni déduction sensible ne traverse les différences de vue.

### A9. L’IA se manifeste là où elle a travaillé

SMART AO n’ajoute pas une présence lumineuse générale ni un avatar permanent. Une intervention IA est signalée au niveau exact de la phrase, cellule, ligne ou bloc produit. Le déclencheur « Pourquoi cette suggestion ? » ouvre sources, portée, date et limites. IBM Carbon applique aussi la présence IA au bon niveau — table entière, ligne, colonne ou cellule — plutôt qu’un marquage indifférencié.^5

**Test V0** : distinguer instantanément contenu source, suggestion IA et validation humaine sans connaître la couleur choisie.

### A10. L’erreur explique ce qui reste possible

Un état dégradé nomme : **ce qui est affecté, ce qui reste disponible, le dernier état confirmé, l’action sûre et la prochaine mise à jour connue**. Atlassian distingue impact confirmé et avis lorsqu’il ne peut pas garantir qu’un site est sain ; cette honnêteté s’applique au produit, sans recopier son vocabulaire d’exploitation.^6

**Test V0** : pendant une panne IA, Documents, Décision et Remise ne deviennent pas artificiellement inaccessibles s’ils restent réellement utilisables.

### A11. La densité est progressive et stable

La liste montre les attributs nécessaires au tri et à l’action. Le détail apparaît dans un panneau ; les tâches longues passent en mode large. Les lignes ne changent pas de hauteur au gré des statuts. Une table dense reçoit toute la largeur utile ; elle n’est jamais enfermée dans une petite carte, conformément aux recommandations Carbon.^3

**Test V0** : sur 1366 × 768, l’utilisateur voit le contexte, le titre, les filtres actifs, au moins six lignes utiles et l’action principale sans défilement horizontal de page.

### A12. Revenir au travail est une fonctionnalité

Après interruption, le produit restaure l’Affaire, le filtre, la ligne, le panneau et le dernier enregistrement confirmé. Il signale les changements intervenus depuis. Une notification lue ne clôt pas l’objet. Une session expirée masque les données puis reprend le contexte après réauthentification selon droits.

**Test V0** : quitter une contradiction, traiter un document, puis revenir à la même contradiction avec la même position et les nouvelles preuves attachées.

## B — Architecture visuelle

### B1. Le shell général

Le shell est composé de quatre zones stables.

1. **Rail global gauche** : logo compact, Accueil, Opportunités, Affaires, Entreprise ; Administration séparée en partie basse et uniquement selon droits. Le rail peut se réduire en mode icônes sur laptop, mais le nom des destinations apparaît au focus et une préférence permet de le garder ouvert.
2. **Barre supérieure** : organisation active à gauche ; recherche globale au centre ; traitements/notifications, aide et menu utilisateur à droite. Le bouton d’aide ouvre une aide contextuelle au lieu d’une page générique.
3. **Bandeau de contexte Affaire** : uniquement dans une Affaire, sous la barre supérieure ; nom court, entreprise candidate, lot, phase/tour, échéance et état de porte. Il reste collant. Un sélecteur change lot/phase/tour seulement avec avertissement si un brouillon local existe.
4. **Zone de travail** : titre/action, navigation Affaire, contenu principal, panneau latéral éventuel. Un seul panneau latéral est ouvert ; une tâche longue bascule en mode large.

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ SMART AO  Organisation ▾   Rechercher…     Traitements  Alertes  Aide  Noor │
├──────────────┬───────────────────────────────────────────────────────────────┤
│ Accueil      │ [Affaire École des Pins] [Société X] [Lot 2] [Offre] [T1]   │
│ Opportunités │ Échéance acheteur : ven. 16:00 Europe/Paris • P3 sous cond.  │
│ Affaires     ├───────────────────────────────────────────────────────────────┤
│ Entreprise   │ Vue d’ensemble  Documents  Prix  Réponse  Remise              │
│              ├───────────────────────────────────────────────────────────────┤
│              │ Titre de la vue                         Action principale     │
│              │ Filtres actifs / portée                 Action secondaire    │
│              │                                                       ┌─────┐ │
│              │ Liste ou espace de travail                       │Détail│ │
│              │                                                       │preuve│ │
│ Administration                                                     └─────┘ │
└──────────────┴───────────────────────────────────────────────────────────────┘
```

### B2. Navigation globale, navigation Affaire et actions

La navigation globale change d’espace de responsabilité. La navigation Affaire change de mode de travail dans le même dossier. Une action contextuelle agit sur l’objet sélectionné. Elles ont trois emplacements et trois styles distincts : rail, onglets horizontaux, puis boutons ou menu de ligne.

Les destinations contextuelles Décision, Partenaires et Résultat/Passation sont visibles depuis les objets qui les appellent et dans un menu « Plus dans cette Affaire ». Elles ne deviennent pas des onglets permanents à côté des cinq destinations quotidiennes. L’utilisateur peut partager l’URL d’une destination ; l’ouverture directe reconstruit le contexte et revérifie les droits.

### B3. Hiérarchie de page

Chaque vue suit le même ordre : fil de retour si nécessaire ; titre et portée ; message d’état majeur ; action principale ; filtres ; contenu. Les alertes ponctuelles ne repoussent pas constamment la page. Un problème persistant est intégré près de l’objet affecté et résumé dans la zone d’état.

Une vue standard utilise une grille de douze colonnes. La liste occupe huit à douze colonnes ; le panneau de détail quatre à cinq colonnes. Une lecture longue utilise environ sept à huit colonnes de texte, pour éviter les lignes démesurées. Une table comparative ou un document prend les douze colonnes.

### B4. Échelle d’espacement et typographie

Base d’espacement : **4 unités** pour les ajustements internes, **8** entre éléments liés, **16** entre sous-groupes, **24** entre sections, **32–48** pour les séparations de page. Cette échelle guide les maquettes sans imposer une technologie.

Hiérarchie typographique : titre de page, titre de section, titre d’objet, corps, métadonnée, libellé compact. Le corps reste la référence de lecture ; les métadonnées ne deviennent pas minuscules sous prétexte de densité. Les nombres utilisent des chiffres tabulaires dans les colonnes. Les unités, devises et conventions de marge sont explicites. Le gras met en évidence l’action ou le changement, pas chaque libellé.

### B5. Tables, cartes, panneaux, modales et timelines

- **Table** : comparer ou balayer des objets homogènes. En-tête collant, titre explicite, filtres persistants, tri annoncé, colonnes masquables sans masquer l’état ou l’action critique. Une ligne sélectionnée ouvre le panneau ; elle ne devient pas toute entière une action ambiguë.
- **Carte** : unité courte avec une seule action, surtout sur l’Accueil. Pas de grille de douze cartes KPI. Une carte décisionnelle contient le contexte, le changement, l’échéance et la décision attendue.
- **Panneau** : inspecter, expliquer, attacher une preuve ou effectuer une action courte. Pas de panneau dans un panneau. Au-delà d’une lecture ou édition substantielle, passage en mode large.
- **Modale** : interruption brève pour confirmation sensible, conflit immédiat ou conséquence irréversible. La modale nomme l’objet, conserve le focus et propose annulation ; le W3C insiste sur la gestion du focus et la fermeture explicite.^7
- **Timeline** : preuve chronologique, pas navigation principale. Chaque événement montre auteur/système, instant, objet/version et conséquence. Les informations anciennes restent consultables, sans concurrence avec l’état courant.

## C — Accueil commun, trois compositions

### C1. Architecture commune

L’Accueil comporte trois onglets logiques : **À faire maintenant**, **À surveiller**, **Événements**. Le premier s’ouvre par défaut. Le rôle et les responsabilités déterminent les sections à l’intérieur ; l’utilisateur ne choisit pas une fausse identité « mode Patron ». Linear documente une Inbox qui sépare les notifications prioritaires des autres mises à jour ; SMART AO reprend la séparation, tout en gardant les blocages métier indépendants de l’état lu/non lu.^8

Ordre :

1. bandeau de service uniquement si une fonction pertinente est affectée ;
2. décisions ou contributions échues/proches ;
3. blocages qui menacent une remise ;
4. autres travaux affectés ;
5. surveillance sans action immédiate ;
6. événements dans l’onglet dédié.

Le classement est explicable. « Pourquoi ici ? » donne la règle : « P5 attend votre délégation et l’échéance est demain à 16 h ». Aucun score opaque de priorité. L’utilisateur peut reporter une contribution non critique ; une condition de porte ou un B0/B1 ne disparaît pas.

### C2. Composition Patron — La minute Patron

```text
À FAIRE MAINTENANT                                              3 décisions

ÉCOLE DES PINS · Lot 2 · Offre · Tour 1              Demain 11:00
Le devis levage a expiré depuis votre GO économique.
Décision attendue : réexaminer P3 — condition « prix renouvelé » ouverte.
Préparé par Samira · 2 preuves · 1 coût non déterminé
[Examiner et décider]   [Voir les preuves]   [Demander un complément]

GYMNASE MARAIS · Lot 1                              Vendredi 16:00
Le paquet v7 attend votre autorisation P5.
0 B0 · 0 B1 · 2 risques B2 acceptables avec motif
[Examiner le paquet v7]  [Voir les contrôles]
```

La première ligne de chaque carte nomme Affaire/lot/phase/tour. La deuxième explique le changement. La troisième nomme la décision exacte et la porte. La sous-ligne fournit préparateur, preuve et inconnus. Une valeur économique n’apparaît que selon droits ; l’absence de chiffre ne fournit aucun indice de son existence à un rôle non habilité.

### C3. Composition Responsable d’offre

Sections : « Bloque la remise », « À produire ou obtenir », « En attente d’un tiers », « À faire revoir ». Une ligne commence par l’action : « Faire confirmer la date contradictoire », « Obtenir l’attestation de visite », « Faire revoir le cadre DPGF ». Chaque entrée affiche l’objet métier lié et la porte touchée.

L’utilisateur peut grouper par Affaire ou par échéance. Le groupe reste collant ; la position est restaurée au retour. Les préférences modifient l’ordre ou la densité, jamais les droits, les blocages ni la vérité de l’état.

### C4. Composition Expert

Une liste courte « Contributions attendues » : question, contexte autorisé, responsable demandeur, échéance et attendu. L’expert ouvre directement le détail utile, avec source. Il ne voit pas un dashboard amputé de cartes confidentielles. S’il n’a rien à faire : « Aucune contribution ne vous est demandée pour le moment », puis accès aux éléments consultables selon droits.

### C5. Variantes d’Accueil à prototyper

- normal avec plusieurs rôles ;
- aucun travail immédiat ;
- Affaire urgente mais donnée Direction masquée ;
- condition ancienne sans événement récent ;
- panne IA affectant le briefing, sans affecter les documents ;
- filtre personnel qui ne peut masquer un blocage obligatoire ;
- mobile : une décision ou trois actions maximum avant « Tout voir ».

## D — C05 « À résoudre »

### D1. Intention

La vue « À résoudre » répond à : **qu’est-ce qui empêche cette Affaire d’avancer, et quelle est la prochaine action sûre ?** Elle ne remplace pas les registres. Elle compose une file d’objets typés et permet de revenir à leur vue complète.

Barre de filtres : **Tous / Bloque décision / Bloque prix / Bloque réponse / Bloque remise / Mes contributions**. Puis filtres secondaires : nature, responsable, lot, échéance, source manquante, à revalider. Le filtre actif est écrit dans le titre de résultat et partageable sans divulguer d’objets non autorisés.

### D2. Anatomie d’une ligne

```text
┌ EXIGENCE ─ B1 ─ BLOQUE LA REMISE ─────────────────────────── ven. 16:00 ┐
│ Attestation de visite obligatoire                                      │
│ RC §4.2, p.12 · Lot 2 · preuve absente                                 │
│ Action : obtenir l’attestation ou qualifier une dispense prouvée       │
│ Responsable : Lina · tâche T-184 en cours                              │
│ [Ouvrir] [Voir la source] [Affecter]                                   │
└─────────────────────────────────────────────────────────────────────────┘
```

La forme commence par un libellé de nature en toutes lettres. B0/B1/B2 a son propre emplacement, jamais fusionné avec la criticité UX. L’impact « bloque la remise » apparaît comme phrase. Le titre décrit l’objet. La source et sa version suivent. L’action et le responsable terminent la ligne.

### D3. Panneau de détail

Le panneau comprend : état courant et raison ; objet ; sources ; relations ; action attendue ; propriétaire métier ; tâche liée ; activité. Pour une contradiction, deux cartes source symétriques sont visibles simultanément. Pour un inconnu, le champ « Ce qui permettrait de le lever » est obligatoire. Pour un risque, distinguer probabilité qualitative si utilisée, impact, couverture et acceptation éventuelle par l’autorité compétente.

Le bouton « Terminer la tâche » est dans le bloc Tâche. Le bloc Exigence garde son propre contrôle « Faire revoir la preuve ». Après clôture de la tâche : message « Travail déclaré terminé. L’exigence reste à faire revoir par [rôle] ». C’est la matérialisation de UX-C1-01.

### D4. Actions groupées

Autoriser seulement des actions non engageantes et homogènes : affecter plusieurs tâches, changer une échéance interne autorisée, demander une revue. Interdire la validation de masse d’exigences, l’acceptation groupée de risques B2 et la fermeture de contradictions. Carbon montre l’intérêt des actions par lot, mais SMART AO les borne selon la nature des objets.^3

### D5. États de C05

- **Vide réel** : « Aucun objet ne bloque actuellement cette Affaire » et lien vers les registres ; ne pas dire « affaire conforme ».
- **Filtre vide** : rappeler le filtre et proposer « Effacer les filtres » ; ne pas afficher l’illustration d’une réussite.
- **Partiel** : bandeau « 3 documents non lus : cette liste peut être incomplète » et accès aux documents concernés.
- **À revalider** : ancienne conclusion visible, barrée ou atténuée avec texte « établie sur DCE v2 ; v3 reçue » ; action comparer.
- **Droits limités** : les objets autorisés restent visibles ; aucun compteur global ne révèle les objets cachés.
- **IA indisponible** : objets existants utilisables ; suggestions et nouveaux rapprochements qualifiés indisponibles.

## E — C11 Remise

### E1. Principe : quatre états permanents, cinq actes distincts

C11 présente une seule expérience de remise avec quatre étapes persistantes : **Candidate → Contrôles et autorisation → Transmission → Réception**. Les actes restent distincts : signature des pièces, P5, export, geste humain de dépôt et rapprochement du reçu. Aucun composant ne les condense en un bouton « Signer et remettre ».

Les quatre étapes sont toujours visibles en tête. Chaque étape affiche un état textuel, son dernier auteur/instant et l’objet concerné. Une coche n’est utilisée que lorsqu’un fait précis est établi. L’étape active possède un titre et une instruction ; les étapes précédentes restent consultables sans modifier leur trace.

```text
REMISE · École des Pins · Société X · Lot 2 · Offre · T1
Échéance acheteur : ven. 16:00 Europe/Paris (15:00 Africa/Casablanca)

1 CANDIDATE             2 AUTORISATION         3 TRANSMISSION       4 RÉCEPTION
v7 prête                P5 accordée            Déclarée envoyée     Non prouvée
12 fichiers             Karim, jeu. 17:42      ven. 14:51           Reçu attendu
──────────────────────────────────────────────────────────────────────────────
RÉCEPTION NON PROUVÉE
Un opérateur a déclaré le dépôt du paquet v7. Aucun reçu rapprochable n’est joint.
Ce que SMART AO sait : export v7 téléchargé à 14:43 ; déclaration à 14:51.
Ce que SMART AO ne sait pas : réception par la plateforme et contenu accepté.
[Importer un reçu]  [Consigner une vérification]  [Voir le paquet v7]
```

### E2. Candidate

La carte candidate affiche entreprise, lot, phase, tour, version, empreinte/identifiant de manifeste, nombre de fichiers et modifications depuis P4. La liste des pièces présente : nom attendu, fichier exact, version, signature requise, statut, source de l’exigence. Un fichier modifié après P5 n’est jamais substitué silencieusement : le paquet v7 reste autorisé ; la modification crée une candidate v8 à faire revoir selon l’impact.

Action principale : « Examiner les contrôles de la candidate v7 ». Action secondaire : « Voir le manifeste ». La création d’une nouvelle candidate avertit que l’ancienne autorisation ne couvrira pas la nouvelle version.

### E3. Contrôles et P5

Le contrôle présente séparément : **B0 intégrité/autorité**, **B1 conformité critique**, **B2 risque arbitrable**. Les deux premiers n’offrent pas « Accepter quand même ». Un B2 montre scénario, portée, responsable, expiration et espace de motif. La revue utilise une page de vérification avant confirmation ; GOV.UK documente ce pattern pour augmenter la confiance et réduire les erreurs, tout en rappelant que la transaction n’est achevée qu’après confirmation.^9

```text
AUTORISER LE PAQUET v7 — LOT 2 — TOUR 1

Paquet : 12 fichiers · manifeste M-v7 · préparé par Samira à 17:31
P4 : actuelle · accordée par Karim à 17:12
B0 : 0       B1 : 0       B2 : 2 acceptés avec motifs valides
Signatures : 3/3 pièces requises rapprochées
Destinataire/canal : profil acheteur X · plateforme Y
Échéance : ven. 16:00 Europe/Paris

Cette autorisation ne dépose rien et ne signe aucune pièce.
[Autoriser le paquet v7]    [Retourner aux contrôles]
```

Le step-up intervient après lecture de ce récapitulatif et avant l’autorisation. En cas d’expiration, le retour restaure le récapitulatif et signale tout changement intervenu ; une authentification réussie ne valide pas une candidate devenue différente.

### E4. Transmission humaine

Après P5, l’opérateur voit uniquement la candidate autorisée, les consignes de canal, l’échéance source, la conversion horaire et l’action « Télécharger le paquet v7 ». Une sous-ligne rappelle : « Autorisé par Karim à 17:42 ; toute modification crée une nouvelle candidate ».

Le bouton « Déclarer le dépôt effectué » ouvre une confirmation qui demande canal, instant, opérateur et éventuelle pièce disponible. Le résultat est **transmission déclarée**, pas réception. Pour une copie de sauvegarde, canal et preuve restent séparés du dépôt principal.

### E5. Réception et preuve

Le rapprochement compare seulement ce que la preuve externe permet : consultation, entreprise, lot/tour, instant et éventuellement fichiers/tailles/empreintes. Résultats possibles :

- **Réception non prouvée** : déclaration sans preuve externe.
- **Preuve incohérente** : une donnée déterminante ne correspond pas ; différences visibles.
- **Réception du pli prouvée — contenu non entièrement rapprochable** : la plateforme confirme le pli sans inventaire.
- **Réception et contenu rapprochés** : seulement si la preuve fournit les éléments suffisants.

DocuSign distingue le contenu d’une transaction de son certificat et de ses événements. SMART AO adapte cette séparation sans assimiler une enveloppe de signature à un reçu de plateforme d’achat.^10

### E6. N02 pendant la remise

Si l’export, l’enregistrement de P5 ou un upload revient sans confirmation, l’étape affiche « Résultat non confirmé » avec l’identifiant de tentative, l’heure et le dernier état confirmé. Le bouton principal devient « Vérifier le résultat ». « Réessayer » reste absent tant que la répétition peut créer deux effets. Le modèle de cycle de vie documenté par Stripe confirme l’intérêt d’un état de traitement distinct du succès ; SMART AO l’étend aux actions métier sans prétendre reproduire un système de paiement.^4

## F — C00 transformé en règles observables

### F1. Contexte

| Situation | Règle visible | Recette |
|---|---|---|
| Hors Affaire | Organisation active visible ; portée de recherche annoncée | Changer d’organisation efface résultats et reconstruit les droits |
| Dans Affaire | Affaire, candidate, lot, phase, tour, échéance collants | Lien direct et retour d’interruption restituent le même contexte |
| Valeur inconnue | Libellé « Non déterminé » avec action ou source attendue | Jamais un blanc, zéro ou tiret ambigu pour une donnée décisionnelle |
| Plusieurs lots | Lot actif accentué par texte et position ; « Tous les lots » seulement si la vue le supporte | Aucune décision/remise multilot involontaire |

### F2. Droits

Chaque action affiche son exigence d’autorité avant que l’utilisateur commence un long parcours. Un bouton indisponible peut rester visible lorsqu’il enseigne une séparation de responsabilité, avec texte : « Préparation autorisée ; P5 réservée à Karim ou à un délégataire P5 actif ». Il disparaît si son existence révèle une donnée sensible ou une fonction sans rapport avec le rôle.

Un changement de rôle ou une révocation déclenche une réévaluation de la vue. Les éléments devenus interdits sont retirés sans laisser leurs valeurs dans le titre, le cache visuel, le bouton Retour ou l’historique local. La continuité ne justifie jamais une fuite.

### F3. Preuve

Une assertion importante comporte un lien « Source » ou « 2 sources », suivi de la version et de la localisation. La preuve est représentée par une pièce attachée à un fait ou à un acte ; le mot « preuve » n’est pas un badge de qualité universel. Le panneau sépare :

1. **Ce qui est affirmé** ;
2. **Source originale** : document/version/localisation ;
3. **Extrait** ;
4. **Interprétation** : humaine ou IA, auteur/date ;
5. **Validation** : rôle, portée et statut ;
6. **Effets** : exigences, coûts, décisions, réponse ou paquet concernés.

Bluebeam documente des usages différents pour comparer et superposer des pages, avec des précautions d’alignement. SMART AO doit de même montrer l’écart visuel et garder l’interprétation métier séparée.^11

### F4. Actions

Hiérarchie : une action principale par vue ou état, actions secondaires textuelles, autres actions dans un menu nommé. Les actions destructrices ou engageantes ne sont jamais de simples icônes. Les actions de masse sont permises uniquement lorsque la nature et l’effet sont identiques et non engageants.

Microcopy : verbe + objet + version/portée si sensible. Après action, la confirmation dit ce qui a changé et ce qui n’est pas encore accompli : « Paquet v7 autorisé. Aucun dépôt externe n’a été effectué. »

### F5. Reprise

Le bandeau de reprise est local au travail : « Brouillon récupéré, dernier enregistrement confirmé 14:21 » ; « Une autre contribution a été enregistrée pendant votre absence » ; « Votre capture reste sur cet appareil et n’est pas partagée ». Il fournit une action sûre. Les brouillons locaux non confirmés ne sont pas mélangés à l’historique serveur.

### F6. Accessibilité

Tous les états sont nommés en texte. Les icônes possèdent un libellé accessible. L’ordre visuel et l’ordre de focus coïncident. Le panneau reçoit le focus sur son titre, se ferme au clavier et le rend au déclencheur. Les graphiques ont une liste/table équivalente ; les écarts ne dépendent pas d’une superposition de couleurs. Les zones de clic restent confortables sur laptop et tablette. Les mises à jour de progression sont annoncées sans répéter chaque pourcentage.

### F7. Temps et fuseaux

Une échéance externe affiche l’heure source et son fuseau. Une conversion pertinente est secondaire : « ven. 16:00 Europe/Paris — 15:00 Africa/Casablanca ». Les mentions « aujourd’hui » et « demain » accompagnent une date/heure absolue. Un conflit de dates ne produit aucun choix automatique ; les deux sources sont montrées.

### F8. Langage commun des états

| Famille | Libellé principal | Structure de message | Action sûre |
|---|---|---|---|
| Vide réel | Aucun [objet] pour le moment | Ce que couvre ce vide ; éventuelle prochaine étape | Créer/importer seulement si autorisé et utile |
| Filtre vide | Aucun résultat avec ces filtres | Filtres actifs et nombre non révélé hors droits | Effacer les filtres |
| Chargement | Chargement de [objet] | Ne pas suggérer progression mesurée sans signal | Attendre ou quitter sans perte |
| Traitement | Analyse de 7/12 fichiers en cours | Accompli, restant, erreurs séparées | Continuer sur les éléments disponibles |
| Partiel | Résultat partiel | Périmètre traité/non traité et effet | Voir les éléments manquants |
| Indisponible | [Fonction] indisponible | Portée et dernier état confirmé | Utiliser la voie manuelle disponible |
| Interdit | Habilitation requise | Autorité nécessaire sans secret | Demander l’accès ou poursuivre le travail permis |
| Erreur | Action échouée | Ce qui n’a pas changé, cause utile si connue | Corriger ou réessayer si sans risque |
| Bloqué | Action impossible : [raison] | B0/B1, source et objet affecté | Lever le blocage ; aucune dérogation impropre |
| À revalider | Établi sur une version ancienne | Ancienne conclusion et changement déclencheur | Comparer et faire revoir |
| Non confirmé | Résultat de l’action non confirmé | Tentative, dernier état connu, risque de répétition | Vérifier avant répétition |
| IA indisponible | Assistance IA indisponible | Ce qui reste utilisable ; ancienneté du dernier résultat | Travailler manuellement / actualiser plus tard |
| Hors ligne | Vous travaillez avec les éléments disponibles sur cet appareil | Disponible, local, en attente | Reconnecter puis confirmer la synchronisation |
| Reprise | Travail récupéré | Dernier confirmé, local et changements concurrents | Continuer, comparer ou résoudre |

GOV.UK recommande de distinguer un vrai état vide d’une erreur et de garder les statuts de tâches en nombre limité. La V0 applique cette sobriété au langage système, tout en conservant les qualifications métier nécessaires.^12

## G — N01 conflits et N02 résultats indéterminés

### G1. N01 : conserver, comparer, résoudre, puis revalider

Un conflit n’est pas une simple erreur de sauvegarde. SMART AO conserve trois éléments : dernière version confirmée, proposition A et proposition B. La résolution peut retenir A, B ou une nouvelle synthèse. Elle indique l’auteur, le motif et les validations à revoir. GitHub rend visibles les deux côtés d’un conflit et exige une résolution avant intégration ; SMART AO reprend la symétrie, avec une couche supplémentaire de droits et de preuve.^13

```text
CONFLIT DE CONTRIBUTIONS · Exigence EX-042
La version confirmée n’a pas été remplacée.

VERSION CONFIRMÉE — 14:18        AUTRE CONTRIBUTION — 14:20
Samira : « visite obligatoire »  Lina : « visite facultative selon lot »
Source : RC v2 §4.2 p.12        Source : CCAP v3 §1.8 p.6

Les deux sources concernent-elles le même lot ? Non établi.
[Comparer les sources] [Préparer une résolution] [Garder pour revue]

Résolution proposée : __________________________________________
Motif et portée : ______________________________________________
Effets : P2 et contrôle de remise à revalider
[Soumettre la résolution à revue]    [Annuler]
```

Le bouton « Marquer résolu » n’existe pas sans contenu final, motif et rôle de revue applicable. Résoudre le conflit de texte ne valide pas automatiquement l’exigence, le risque ou la porte affectée. L’historique conserve les contributions.

### G2. N02 : un état stable, pas un spinner infini

N02 apparaît après un délai ou une rupture de communication lorsque l’effet peut exister. Il remplace l’action principale par « Vérifier le résultat ». Le message contient objet, tentative, heure, dernier état confirmé, portée et danger d’un nouvel essai.

```text
RÉSULTAT NON CONFIRMÉ
SMART AO n’a pas reçu la confirmation de l’export E-784 lancé à 14:42.
Dernier état confirmé : paquet v7 autorisé, aucun export confirmé.
Ne relancez pas tant que la vérification n’est pas terminée : deux exports
pourraient être créés.
[Vérifier le résultat]   [Voir l’historique]   [Quitter sans perdre le suivi]
```

Si la vérification conclut à l’échec : « Export non créé ; vous pouvez réessayer ». Si elle conclut au succès : montrer l’objet exact. Si elle ne conclut pas : conserver N02, proposer une vérification humaine ou support borné. Pour un dépôt externe, SMART AO ne prétend pas interroger une plateforme qu’il ne contrôle pas : l’opérateur et la preuve externe restent nécessaires.

### G3. Matrice N02 par action

| Action | Répétition risquée | Vérification proposée | Issue visible |
|---|---|---|---|
| Autorisation P5 | Deux traces concurrentes / mauvaise version | Historique d’autorisation et manifeste exact | Accordée, non accordée ou conflit N01 |
| Export | Doublon ou confusion de fichiers | Historique et identifiant de l’export | Créé avec version, non créé, non confirmé |
| Upload tiers | Deux pièces ou version ambiguë | Accusé technique et inventaire du paquet | Reçu pour contrôle, échoué, non confirmé |
| Synchronisation mobile | Double capture / perte locale | État local et serveur par capture | Local, en attente, confirmé, conflit |
| Dépôt externe | Nouvelle tentative inutile ou hors délai | Preuve/opérateur, informations disponibles | Déclaré, réception prouvée/partielle, non prouvée |

## H — Confidentialité rendue visible sans révéler le secret

### H1. Matrice de vue V0

La matrice décrit les compositions à prototyper ; les droits réels restent plus fins et proviennent du v0.4.

| Élément | Patron habilité | Responsable | Métreur | DAF habilité | Admin sans rôle métier | Tiers |
|---|---|---|---|---|---|---|
| Décisions/conditions | Selon délégation et périmètre | Prépare, voit ce qui lui est permis | Contribue sur prix | Contribue sur finance | Aucun accès par défaut | Aucun |
| Prix détaillé | Selon droit économique | Seulement portée autorisée | Travail métier autorisé | Selon périmètre | Aucun par qualité d’Admin | Aucun |
| Marge/contribution Direction | Selon droit Direction | Masquée, y compris dans résumé IA | Masquée sauf droit explicite | Visible selon droit | Masquée | Masquée |
| Exigences/documents | Selon Affaire | Selon Affaire | Selon besoin | Selon besoin | Aucun accès métier implicite | Seulement paquet partagé |
| Utilisateurs/sécurité | Pas par titre seul | Profil propre | Profil propre | Profil propre | Administration autorisée | Compte/invitation propres |
| Partage | Selon autorisation | Selon autorisation | Borné | Borné | Gère la gouvernance sans lire le contenu interdit | Paquet, durée et actions autorisées |

### H2. Fuites indirectes et règles

| Vecteur | Fuite possible | Règle V0 |
|---|---|---|
| Compteur | « 3 risques de marge » révèle une analyse Direction | Calculer après filtre de droits ; utiliser une catégorie autorisée ou ne rien afficher |
| Badge | Badge « marge faible » sur une Affaire listée | Aucun statut économique hors rôle ; pas de silhouette de carte interdite |
| Notification | Objet ou montant dans aperçu système/email | Corps minimal borné ; ouverture avec nouveau contrôle d’accès |
| Résumé | Total − coût permet de déduire la marge | Contrôler les combinaisons de valeurs, pas seulement chaque champ |
| Recherche | Extrait d’un document interdit | Filtrer avant index/résultat/extrait ; aucun décompte global |
| IA | Réponse fondée sur contenu anciennement accessible | Droits courants avant récupération et génération ; sortie révoquée non accessible |
| Export | Colonne masquée encore présente dans le fichier | Export reconstruit sur le périmètre autorisé ; aperçu et inventaire avant action |
| Historique | Ancienne version contient une valeur maintenant interdite | Contrôle actuel sur chaque version et événement ; auteur visible sans secret inutile |
| URL/retour | Titre ou extrait reste dans l’interface après révocation | Recalcul de contexte et purge de la vue au changement de droits |

Ideals documente un mode « voir comme un groupe », mais précise que certaines ouvertures/téléchargements restent réalisés avec la vue de l’administrateur. Ce contre-exemple impose à N03 d’annoncer ses limites et de construire l’aperçu depuis le paquet réellement autorisé, jamais depuis une session administrateur.^14

### H3. Microcopy de droit

- Si l’existence peut être révélée : « Vous pouvez préparer les contrôles. L’autorisation P5 exige une délégation P5 active. »
- Si le contenu est sensible : « Certaines informations ne sont pas incluses dans votre périmètre. Les éléments autorisés restent affichés. »
- Pour un tiers : « Vous accédez uniquement au paquet partagé par Société X jusqu’au 18 septembre, 18 h. »
- Pour un Admin : « Administrer les accès ne permet pas de consulter les données métier protégées. »

## I — IA contextuelle

### I1. Cinq présences autorisées

1. **Briefing** : au début d’une Affaire ou d’une décision, limité aux changements et inconnus autorisés depuis la dernière revue.
2. **Explication** : « Pourquoi je vois ceci ? », « Pourquoi ce blocage ? », « D’où vient cette affirmation ? ».
3. **Suggestion** : action, rapprochement ou qualification proposée au niveau de l’objet.
4. **Transformation** : contradiction → brouillon de question ; sources → brouillon de réponse ; changement → liste d’impacts à confirmer.
5. **Contrôle** : recherche de manque ou incohérence, présentée comme résultat partiel et révisable.

Chaque présence a le même cartouche : **Proposé par SMART AO · généré à [heure] · fondé sur [n] sources · périmètre [lot/version]**. Actions : « Voir pourquoi », « Modifier », « Rejeter », « Soumettre à revue ». Une validation humaine remplace le statut de suggestion par une trace de validation ; elle ne maquille pas l’origine du brouillon.

### I2. Le panneau « Pourquoi ? »

```text
POURQUOI CETTE SUGGESTION ?

Suggestion : demander si la visite est obligatoire pour le lot 2.
Fondée sur :
• RC v2 §4.2 p.12 — « visite obligatoire… »
• CCAP v3 §1.8 p.6 — portée différente pour le lot 2
Limite : SMART AO n’a pas établi quelle clause gouverne cette situation.
Effet si confirmé : P2 et contrôle avant remise à revoir.

[Ouvrir les deux sources]  [Préparer la question]  [Rejeter la suggestion]
```

Microsoft HAX recommande d’expliquer pourquoi le système s’est comporté ainsi, tout en avertissant qu’une explication peut augmenter la confiance et créer un biais d’automatisation. SMART AO montre donc également la limite et l’action de vérification.^15

### I3. Patterns déconseillés

- chatbot vide comme page d’accueil ;
- halo ou dégradé IA sur toute la page ;
- score unique « confiance 87 % » sans définition et calibration métier ;
- bouton « Optimiser » sans sortie prévisible ;
- suggestion déjà cochée dans une liste de conformité ;
- source masquée derrière un texte généré ;
- reformulation qui change une obligation ;
- régénération globale automatique à chaque ouverture ;
- auto-envoi de question, partage ou dépôt ;
- réponse à une demande interdite par une phrase qui confirme indirectement le secret.

### I4. Reprise, coût et panne

Le briefing indique sa date et le périmètre traité. Si des pièces ont changé : « 2 changements depuis ce bref » et action « Actualiser sur ces changements ». Le dernier bref reste visible comme ancien, jamais mis à jour silencieusement. Cette actualisation ciblée limite le bruit, le délai et l’usage IA ; aucune économie chiffrée n’est prétendue sans mesure.

Pendant une panne, les contenus déjà validés, sources, registres, décisions et coffre restent utilisables selon leur état réel. Le cartouche devient : « Assistance IA indisponible — dernier résultat généré hier à 18:12 sur DCE v2 ». Les suggestions non terminées ne sont ni publiées ni relancées automatiquement si leur résultat est inconnu.

## J — Responsive et continuité multi-écran

### J1. Grand écran

Rail global ouvert, liste 7–8 colonnes et panneau 4–5 colonnes. En comparaison documentaire, mode large avec deux documents et une colonne d’impacts repliable. Les éléments supplémentaires servent à rapprocher information et preuve, pas à ajouter des KPI.

### J2. Laptop 13–14 pouces

Cas de référence V0. Rail réductible ; bandeau Affaire sur une ligne principale et une ligne de contexte ; navigation Affaire défilable horizontalement au clavier sans masquer l’onglet actif. Liste 60–65 % et panneau 35–40 %. Quand le panneau devient trop étroit, il remplace la liste et propose un retour explicite. Les tableaux conservent colonnes objet, état, action, échéance ; les métadonnées secondaires se replient dans la ligne.

### J3. Tablette

Rail remplacé par un menu de navigation explicite. Liste puis détail plein écran, avec titre de retour contenant le filtre. Les actions principales restent en bas ou en haut de manière stable selon le parcours, sans couvrir les contenus. Signature/P5 peuvent être consultées ; leur exécution n’est disponible que si le parcours sensible est qualifié et connecté selon le catalogue.

### J4. Mobile compagnon

Accueil : prochaine visite, captures à synchroniser, contributions urgentes. Dans l’Affaire : échéance, pièces clés effectivement disponibles, À résoudre autorisé, tâches et capture. Une preuve courte s’ouvre en plein écran. La navigation Affaire complète devient une liste de destinations, pas cinq onglets compressés.

Volontairement indisponibles ou fortement bornés : chiffrage détaillé, comparaison multi-colonnes, édition longue du mémoire, administration complexe, export complet, résolution élaborée de conflit et P5 hors ligne. Le produit explique : « Cette action nécessite la version desktop » ou « Connectez-vous pour autoriser ce paquet ».

Procore documente que le travail hors connexion dépend des éléments disponibles localement et que les modifications attendent la synchronisation ; Dalux met les tâches récentes et la préparation hors ligne au premier plan. SMART AO retient la disponibilité explicite et les états local/en attente/confirmé, sans promettre un cache intégral.^16 ^17

### J5. Ce qui disparaît, se replie ou change de forme

| Élément | Laptop | Tablette | Mobile |
|---|---|---|---|
| Rail global | Ouvert ou réduit | Menu | Menu compact |
| Bandeau Affaire | Deux lignes max | Résumé + développer | Affaire/lot/échéance ; détail plein écran |
| Liste + panneau | Côte à côte si lisible | Alternés | Alternés |
| Tables comparatives | Pleine largeur | Colonnes essentielles + détail | Résumé et consultation ; comparaison complète desktop |
| Preuve | Panneau puis mode large | Vue pleine | Vue pleine, source exacte |
| Actions secondaires | Textes/menu | Menu nommé | Menu nommé, pas icônes seules |
| IA | Cartouche local | Cartouche local | Explication/suggestion courte ; édition longue desktop |
| Remise | Parcours complet connecté | Consultation et actions qualifiées | État/urgence/preuve ; pas P5 hors ligne |

## K — Système visuel métier

### K1. Grammaire avant palette

Chaque objet combine cinq signaux : **nom de nature**, **forme ou marqueur**, **position stable**, **état textuel**, **couleur secondaire**. La couleur n’est jamais le seul signal. Les icônes ne servent pas à inventer vingt pictogrammes métier : elles soutiennent un petit vocabulaire récurrent et restent accompagnées d’un texte dans les décisions, risques et preuves.

| Nature | Marqueur et position | Libellé / hiérarchie | États propres | Action habituelle |
|---|---|---|---|---|
| Fait | Trait plein vertical, zone « Établi » | « Fait » puis assertion et date de référence | établi, obsolète, à revalider | Voir source |
| Source | Icône document, lien souligné | Type, titre court, version, localisation | disponible, absente, illisible, remplacée | Ouvrir au passage exact |
| Preuve | Attache carrée au fait ou à l’acte | « Preuve de… » et limite démontrée | suffisante, partielle, incohérente, retirée | Examiner / rapprocher |
| Exigence | Barre gauche double, libellé EXIGENCE | Formulation puis lot/source/criticité | satisfaite, non satisfaite, inconnue, non applicable | Faire revoir la preuve |
| Inconnu | Losange vide + « INCONNU » | Question non résolue | ouvert, en recherche, levé | Définir ce qui le lèvera |
| Hypothèse | Losange hachuré + « HYPOTHÈSE » | Proposition, auteur, justification, expiration | proposée, acceptée dans une portée, expirée, réfutée | Examiner / accepter si autorisé |
| Contradiction | Deux traits convergents | Deux affirmations symétriques et leurs sources | ouverte, qualification demandée, résolue, rouverte | Comparer / préparer une résolution |
| Risque | Triangle + classe B si applicable | Événement, impact, couverture et responsable | ouvert, réduit, accepté B2, réalisé | Traiter / arbitrer |
| Tâche | Case carrée | Verbe, résultat attendu, responsable, échéance | à faire, en cours, terminée, annulée | Commencer / terminer |
| Décision | Sceau circulaire | Porte, décision, autorité, périmètre, motif | préparée, accordée, conditionnelle, remplacée, à revalider | Examiner / décider |
| Condition | Crochet relié à la décision | Texte, responsable, échéance, preuve de levée | ouverte, levée, échue, annulée | Lever / réexaminer |
| B0 | Octogone + « B0 » | Intégrité/autorité : pourquoi l’action est impossible | ouvert, levé | Corriger ; aucune dérogation |
| B1 | Rectangle renforcé + « B1 » | Exigence critique non satisfaite | ouvert, en revue, levé | Obtenir/revoir preuve |
| B2 | Triangle + « B2 » | Risque borné, scénario et portée | ouvert, accepté, expiré, levé | Arbitrer avec motif |
| Proposition IA | Étincelle discrète au niveau produit | « Proposé par SMART AO », sources/date/limite | nouvelle, modifiée, rejetée, soumise à revue | Voir pourquoi / modifier |
| Validation humaine | Initiales + date dans zone « Revu par » | Rôle, portée, version | valide, remplacée, à revalider | Voir la trace |
| Obsolète | Bandeau « Ancienne information » | ancienne version et successeur | remplacée | Ouvrir la version actuelle |
| À revalider | Marqueur de réouverture + phrase causale | « Établi sur v2 ; v3 reçue » | attente revue, revue | Comparer / faire revoir |

### K2. Couleur

Palette fonctionnelle limitée : neutres pour structure ; bleu ou accent principal pour action/lien ; ambre pour attention ou non-confirmation ; rouge sombre pour blocage/danger ; vert sombre pour fait positif établi ; violet discret pour intervention IA. Le prototype en niveaux de gris doit rester utilisable. Un B1 levé ne devient pas une carte verte dominante : il passe en texte neutre « Levé », pour laisser l’attention aux éléments actifs.

### K3. Badges et statuts

Un badge tient sur une expression courte et répond à une dimension précise : nature, blocage ou état. Maximum recommandé dans une ligne standard : un marqueur de nature, un état déterminant et une échéance ; les autres attributs passent en métadonnées. Les badges « urgent », « critique », « risque » ne sont pas empilés sans expliquer la cause.

Exemples acceptés : « B1 · bloque la remise », « À revalider · DCE v3 », « Réception non prouvée ». Exemples interdits : « Important », « Succès », « IA 92 % », « À traiter » sans action ou raison.

### K4. Échéances

L’échéance est un texte absolu, renforcé par une proximité lisible : « ven. 18 sept., 16:00 Europe/Paris · dans 2 j ». Une date échue utilise le mot « Échue ». La couleur accentue, mais le texte porte le sens. Les échéances internes et acheteur sont identifiées ; la première ne masque pas la seconde.

### K5. Preuve et citation dans le flux

Une citation courte apparaît sous l’assertion avec titre/version/localisation. Au survol ou focus : aperçu non essentiel ; au clic : panneau accessible. Une source remplacée reste visible avec son statut et un lien vers la version courante. Aucune citation générée n’est inventée pour combler une localisation absente.

### K6. Progression

Utiliser une progression seulement quand le périmètre est connu : « 7 fichiers analysés sur 12 ». Si le dénominateur peut changer, écrire l’activité et les éléments trouvés sans faux pourcentage. Les quatre couvertures adoptées — réception, lecture, revue d’exigences, couverture aval — ont leurs propres libellés et dénominateurs. Aucun anneau global ne les moyenne.

## L — Benchmark ciblé

La sélection privilégie dix réponses UX directement utiles à V0. Les observations proviennent des documentations publiques ; ce n’est ni un classement global ni une déclaration que tous les écrans du produit sont supérieurs.

| Problème V0 / référence | OBSERVÉ ou RETOUR | Limite observée ou inférée | PROPOSITION SMART AO |
|---|---|---|---|
| Priorité et retour au contexte — **Linear Inbox/Peek** | OBSERVÉ : Inbox distingue Priority/Other et ouvre un objet dans une vue adaptée ; Peek inspecte un objet depuis des listes.^2 ^8 | Une notification reportée ou lue peut être confondue avec le problème métier si les deux états sont couplés. | C01 sépare décisions/actions/événements ; panneau de détail puis retour exact. Un blocage persiste indépendamment de la notification. |
| Données denses — **IBM Carbon** | OBSERVÉ : tables triables, lignes extensibles, actions ligne/lot, largeur généreuse ; le détail trop complexe passe à une vraie vue. Présence IA marquée au niveau concerné.^3 ^5 | Une table n’est pas un tableur et les actions par lot peuvent être dangereuses. | Tables pour balayage, mode large pour comparaison/édition ; aucune validation métier de masse ; marque IA sur la cellule/phrase exacte. |
| Transactions longues — **GOV.UK** | OBSERVÉ : liste de tâches pour parcours repris sur plusieurs sessions, nombre de statuts limité, vérification avant confirmation.^9 ^12 | « Tâche terminée » reste déclaratif et ne prouve pas la conformité d’un dossier. | C11 utilise des étapes reprenables mais conserve les preuves et actes séparés ; C05 ne ferme jamais l’exigence depuis la tâche. |
| Comparaison documentaire — **Bluebeam** | OBSERVÉ : comparaison et superposition répondent à des usages différents ; l’alignement influe sur la lecture.^11 | L’écart visuel n’explique pas son impact métier et peut être trompeur sur scans/plans mal alignés. | Deux versions en mode large, localisation synchronisée, puis impacts proposés/confirmés distincts. |
| Travail attribué — **Responsive** | OBSERVÉ : question affectée, recommandation, activité et passage à la suivante ; auteur et revue séparés.^18 | Un travail déclaré revu peut encore être incomplet par rapport à une porte SMART AO. | Liste → production → preuve → revue ; auteur, relecteur et autorité de porte visibles et distincts. |
| Aperçu des droits — **Ideals** | OBSERVÉ : « View As » inspecte permissions et arborescence ; l’aide déclare des limites quand l’ouverture/téléchargement reste dans la vue de l’Admin.^14 | Un aperçu peut rassurer à tort s’il ne simule pas réellement le destinataire. | N03 est construit depuis le paquet autorisé et affiche ses limites ; pas d’usurpation ou de lecture Admin. |
| Cycle asynchrone — **Stripe** | OBSERVÉ : le cycle documente plusieurs états avant traitement et succès.^4 | Un statut de paiement ne se transpose pas juridiquement à la remise d’une offre. | N02 devient un état stable avec dernier confirmé et vérification ; vocabulaire propre à l’AO, aucune répétition aveugle. |
| Preuve transactionnelle — **DocuSign** | OBSERVÉ : certificat et données de transaction gardent des événements séparés du document.^10 | Signature achevée, dépôt sur profil acheteur et admission sont trois choses différentes. | C11 sépare signature, P5, export, transmission et réception ; journal lié au manifeste exact. |
| Conflit — **GitHub** | OBSERVÉ : les deux variantes d’un changement concurrent sont visibles avant résolution.^13 | Le choix de texte ne suffit pas à valider une obligation ou une décision métier. | N01 conserve A/B/version confirmée, puis résolution, motif et revalidation ciblée. |
| Panne ciblée — **Atlassian System Health** | OBSERVÉ : distinction impact confirmé/advisory et statuts investigation, cause identifiée, surveillance, résolution.^6 | Une taxonomie d’incident d’exploitation peut surcharger l’utilisateur métier. | Dans chaque vue : portée affectée, dernier confirmé, fonctions encore utilisables, prochaine action ; détail incident secondaire. |
| Mobile hors ligne — **Procore/Dalux** | OBSERVÉ : disponibilité locale bornée et synchronisation différée ; accueil centré sur tâches récentes et préparation hors ligne.^16 ^17 | Le cache peut être incomplet ou obsolète ; une tâche récente peut masquer une obligation critique. | N05 par fichier/capture ; mobile priorise visite/échéance/blocage avant récence ; aucun dossier intégral implicite. |
| Entretien de la connaissance — **Notion/Loopio** | OBSERVÉ : pages vérifiées avec propriétaire/expiration ; cycles de revue à différentes granularités.^19 ^20 | Une validation générale ne prouve pas l’applicabilité au lot ou à l’entité. | Passeport de réemploi : validité, portée, applicabilité Affaire et snapshot séparés. |
| Comparatif prix — **BuildingConnected** | OBSERVÉ : colonnes par entreprise, lignes de périmètre, ajustements/notes ; anciens ajustements peuvent suivre une proposition révisée.^21 | Un ajustement repris peut devenir faux ; des RETOURS UTILISATEURS signalent de la double saisie et un maintien d’Excel, sans mesure représentative.^22 | C08 montre périmètre/exclusions avant total ; ajustements d’une version précédente passent « à reconfirmer » ; import/export préservés. |

## M — Anti-patterns à interdire dans V0

| Anti-pattern | Pourquoi il échoue dans SMART AO | Remplacement |
|---|---|---|
| Dashboard de graphiques en page d’accueil | Retarde la décision, masque les exceptions et peut divulguer des agrégats | File d’actions/décisions explicable, événements séparés |
| Score global de santé ou de GO | Moyenne des dimensions incompatibles ; suggère une autorité automatique | Faits, inconnus, B0/B1/B2, conditions et preuves séparés |
| Navigation à dix onglets dans l’Affaire | Traite les registres comme applications et surcharge le Patron | Cinq destinations quotidiennes + contextuelles retrouvables |
| Tableau dans une petite carte | Tronque la comparaison et multiplie les scrolls | Table pleine largeur ou liste/détail |
| Tout ouvrir dans une modale | Perd le contexte, empile les couches, dégrade clavier/mobile | Panneau unique pour court ; mode large pour travail substantiel |
| Action principale « Valider » | Objet, pouvoir et effet ambigus | Verbe + objet + version/portée |
| Vert global « dossier prêt » | Peut cacher B0/B1 ou couverture partielle | « 0 B0, 0 B1 ; 2 B2 traités » avec portée et date |
| Tâche terminée = conformité | Confond effort et preuve | Revue de preuve indépendante de la tâche |
| « Envoyé » = reçu | Confond action locale, transport et preuve externe | Transmission déclarée, réception prouvée, contenu rapproché |
| Dernier enregistrement gagne | Perte de contribution et validation sur mauvaise version | N01 A/B/version confirmée et résolution tracée |
| Spinner après action ambiguë | N’explique ni succès ni possibilité de quitter/réessayer | N02 avec dernier confirmé, vérification et reprise |
| IA en panneau permanent | Réduit l’espace, attire l’attention et transforme tout en dialogue | IA au niveau du travail, explicable à la demande |
| Badge « confiance IA » isolé | Peut augmenter la confiance sans exposer les limites | Sources, couverture, ancienneté, limite et action de vérification |
| Pages vides pour données interdites | Révèle l’existence et la structure du secret | Composition recalculée selon droits |
| Responsive par simple compression | Rend tables et onglets illisibles | Transformation liste/détail et fonctions volontairement bornées |
| Timeline comme outil principal | La récence supplante la priorité métier | État courant et action d’abord ; timeline comme preuve secondaire |

## N — Wireframes textuels structurants

Les wireframes décrivent le contenu et le comportement. Ils ne figent ni marque, ni palette finale.

### N1. Shell + Vue d’ensemble Affaire

```text
[RAIL GLOBAL] [BARRE ORG/RECHERCHE/ALERTES/AIDE/UTILISATEUR]
              [CONTEXTE AFFAIRE · candidate · lot · phase/tour · échéance]
              [Vue d’ensemble | Documents | Prix | Réponse | Remise | Plus ▾]

              ÉCOLE DES PINS — VUE D’ENSEMBLE       [Préparer décision P3]
              Analyse partielle : 3 pièces non lues        [Voir les pièces]

              PROCHAINE ACTION
              Faire renouveler le devis levage — Samira — demain 11:00

              À RÉSOUDRE (6)                         ACTIVITÉ DE L’AFFAIRE
              B1 Attestation visite absente          Rectificatif v3 reçu
              Inconnu Coût du levage                  P2 à revalider
              Contradiction Date RC / avis            [Voir toute l’activité]
              [Ouvrir À résoudre]

              PORTES ET CONDITIONS
              P2 à revalider · P3 sous condition · P4 non préparée
```

Comportement : le clic sur une ligne ouvre le panneau ; « Documents » conserve le contexte. Les chiffres économiques n’apparaissent que selon droits. « Analyse partielle » mène aux pièces non lues, jamais à un faux bouton « terminer l’analyse ».

### N2. Accueil Patron

```text
ACCUEIL                                            [À faire] [À surveiller] [Événements]
Bonjour Karim. 3 décisions attendent votre autorité.

À DÉCIDER AVANT DEMAIN
┌ Affaire / lot / phase / tour                           Échéance ┐
│ Ce qui a changé                                                  │
│ Décision exacte et porte · condition ou blocage                  │
│ Préparé par · preuves · inconnus autorisés                       │
│ [Examiner et décider] [Voir les preuves] [Demander complément]   │
└───────────────────────────────────────────────────────────────────┘

À DÉLÉGUER OU RÉAFFECTER
Responsable absent J−2 · 4 objets attendent une prise en charge
[Préparer la relève] [Voir les objets]
```

Variante sans action : « Aucune décision ne vous attend. Deux affaires approchent de leur échéance sans nouvel arbitrage. » Le produit ne remplit pas l’espace par des graphiques.

### N3. C05 À résoudre, liste/détail/preuve

```text
À RÉSOUDRE                  [Décision] [Prix] [Réponse] [Remise] [Mes contributions]
[Nature ▾] [Responsable ▾] [Lot 2] [À revalider ☐] [Rechercher dans cette vue]

LISTE 8 colonnes                              PANNEAU 4 colonnes
> EXIGENCE · B1 · remise                      EXIGENCE EX-042
  Attestation visite absente                  État : non satisfaite
  RC v2 §4.2 p.12 · Lina · ven. 16:00         Impact : bloque P5

  INCONNU · prix                              SOURCE
  Coût du levage non déterminé                RC v2 §4.2, page 12
  Métreur · demain 11:00                      « …visite obligatoire… »

  CONTRADICTION · décision                    TRAVAIL LIÉ
  Date avis ≠ RC                              T-184 · Lina · en cours
                                              [Terminer la tâche]
                                              La revue restera nécessaire.
                                              [Faire revoir la preuve]
```

### N4. C11 Remise

```text
[Candidate v7 prête] — [P5 accordée] — [Transmission déclarée] — [Réception non prouvée]

RÉCEPTION NON PROUVÉE                                     [Importer un reçu]
Dernier état confirmé et limites de connaissance

PAQUET AUTORISÉ                JOURNAL
12 fichiers · M-v7             14:43 export créé
P4 actuelle                    14:51 dépôt déclaré par Lina
0 B0 · 0 B1 · 2 B2 traités     — aucune preuve externe —
3/3 signatures rapprochées

[Voir le paquet v7] [Consigner une vérification] [Historique des remises]
```

### N5. Panneau de preuve

```text
PREUVE DE L’EXIGENCE EX-042                                      [Fermer]
Assertion : une attestation de visite est requise pour le lot 2.

SOURCE ORIGINALE
RC · version 2 reçue le 14 sept. · §4.2 · page 12     [Ouvrir dans Documents]
[extrait court avec passage mis en évidence]

INTERPRÉTATION
Proposée par SMART AO à 10:14 · portée lue : RC v2, lot 2
Limite : le CCAP v3 contient une clause de portée différente.
[Voir pourquoi] [Comparer avec CCAP v3]

VALIDATION
Non revue · rôle attendu : Responsable d’offre / conseil selon besoin
[Soumettre à revue]
```

### N6. N01 conflit

```text
CONFLIT — rien n’a été écrasé
Version confirmée 14:18 | contribution Samira 14:19 | contribution Lina 14:20

[PROPOSITION A + source]      [PROPOSITION B + source]
[Retenir A] [Composer]        [Retenir B]

Résolution proposée + motif + portée
Effets à revalider : P2, exigence EX-042, contrôle Remise
[Soumettre à revue] [Conserver ouvert]
```

### N7. N02 résultat non confirmé

```text
RÉSULTAT NON CONFIRMÉ · Export E-784 · lancé à 14:42
Dernier état confirmé : paquet v7 autorisé, aucun export confirmé.
Pourquoi ne pas réessayer : un second fichier pourrait être créé.
[Vérifier le résultat] [Voir l’historique] [Quitter sans perdre le suivi]
```

### N8. Panne IA locale

```text
ASSISTANCE IA INDISPONIBLE POUR L’ANALYSE DE DOCUMENTS
Les originaux, preuves déjà enregistrées, décisions et Remise restent disponibles.
Dernier briefing : hier 18:12 · DCE v2 · désormais ancien (v3 reçue)
[Continuer sans IA] [Voir les documents] [État du service]
```

### N9. Mobile visite

```text
ÉCOLE DES PINS · Lot 2                         Hors ligne
Visite aujourd’hui 10:30 · présence obligatoire

À FAIRE SUR PLACE
□ Confirmer accès grue
□ Photographier zone de stockage
□ Obtenir attestation de présence

DISPONIBLE SUR CET APPAREIL
Plan masse v2 · RC v2 §visite                 [Ouvrir]

CAPTURES
2 locales · 1 en attente · 4 confirmées       [Capturer]
```

## O — Variantes obligatoires de la V0

Chaque première vue structurante doit être dessinée au moins dans les variantes suivantes. Une variante peut être combinée pour limiter le nombre de maquettes, si chaque comportement reste visible et testable.

| Variante | Accueil | C05 | C11 | Preuve/IA | Mobile |
|---|---|---|---|---|---|
| Normal | Plusieurs actions autorisées | Objets typés et panneau | Candidate puis parcours complet | Source et validation | Visite connectée |
| Vide réel | Aucune décision/contribution | Aucun objet bloquant, sans conclure conforme | Aucune candidate avec prochain prérequis | Pas de source attachée = non vérifiable | Aucune action terrain |
| Filtre vide | Critères personnels sans résultat | Filtres rappelés | Historique filtré vide | Recherche source vide | Filtre tâches vide |
| Partiel | Brief limité par pièces non lues | Liste potentiellement incomplète | Contrôles incomplets | Extraction partielle | Document non disponible localement |
| Erreur | Une section échoue, autres utilisables | Affectation échouée sans perte | Reçu illisible ou upload échoué | Source indisponible | Capture échouée, local préservé |
| Droits limités | Collaborateur sans données Direction | Objets autorisés seulement, aucun total global | Opérateur sans P5 / Patron sans action opérateur | Source interdite sans extrait | Fonction absente ou expliquée |
| À revalider | Décision réapparaît après changement | Objet établi sur v2, v3 reçue | Candidate modifiée après P5 | Ancienne suggestion datée | Document local ancien |
| Non confirmé | Action d’affectation ambiguë | Mise à jour en vérification | P5/export/dépôt ambigu N02 | Génération issue inconnue | Sync en attente |
| IA indisponible | Liste métier disponible, brief ancien | Registres disponibles | Contrôles humains maintenus | Cartouche indisponible et voie manuelle | Aucune relance intrusive |
| Conflit | Deux décisions/contributions | N01 complet | Autorisations concurrentes bloquées | Deux interprétations préservées | Résolution reportée sur desktop si complexe |

## P — Décisions et statut

### P1. Application directe des décisions déjà propriétaires

| ID | Application dans V0 | Statut |
|---|---|---|
| APP-01 | Cinq espaces globaux et cinq destinations quotidiennes de l’Affaire | **Applique v0.3** |
| APP-02 | Accueil commun composé par responsabilités ; décisions/contributions/événements séparés | **Applique UX-C1-03 / I01** |
| APP-03 | C05 rassemble visuellement les objets typés sans fusionner leurs validations | **Applique UX-C1-01 / I02** |
| APP-04 | C11 en quatre étapes persistantes, actes de signature/P5/export/dépôt/reçu distincts | **Applique UX-C1-02 / I07** |
| APP-05 | Réception/lecture/revue/couverture aval séparées avec dénominateurs | **Applique UX-C1-04** |
| APP-06 | N01/N02 avec contributions préservées et dernier état confirmé | **Applique UX-C1-05** |
| APP-07 | Filtrage de confidentialité avant agrégation, recherche, IA et export | **Applique UX-C1-06** |
| APP-08 | Configuration progressive après identité/MFA ; première valeur dans une Affaire | **Applique UX-C1-07** |
| APP-09 | États difficiles présents dès la première vague | **Applique UX-C1-08** |
| APP-10 | IA contextuelle, source/version/limite, aucune décision ou action externe autonome | **Applique v0.3 et v0.4** |
| APP-11 | Desktop principal, mobile compagnon, P5 jamais hors ligne | **Applique v0.3 et OWN-10** |

### P2. Améliorations adoptées dans le cadre propriétaire

| ID | Décision adoptée | Valeur attendue | Garde-fou / point à éprouver | Statut |
|---|---|---|---|---|
| PROP-01 | Rail global + barre supérieure + bandeau Affaire collant | Contexte stable malgré navigation profonde | Hauteur consommée sur laptop ; tester bandeau sur une/deux lignes | **ADOPTÉ** |
| PROP-02 | Une action principale et microcopy verbe+objet+version | Réduction des clics ambigus | Libellés longs ; privilégier compréhension à compacité seule | **ADOPTÉ** |
| PROP-03 | Preuve à un geste, document à deux | Vérification rapide sans perdre la liste | Panneau trop étroit ; bascule vers mode large | **ADOPTÉ** |
| PROP-04 | Grammaire métier à cinq signaux | Compréhension sans dépendance couleur | Éviter une surcharge de marqueurs ; tester reconnaissance | **ADOPTÉ** |
| PROP-05 | Onglets Accueil À faire/À surveiller/Événements | Sépare priorité, surveillance et récence | Une condition ancienne reste visible hors simple récence | **ADOPTÉ** |
| PROP-06 | Filtres C05 par conséquence métier | Répond à « qu’est-ce qui bloque ? » | Multi-étiquetage explicite lorsqu’un objet touche plusieurs portes | **ADOPTÉ** |
| PROP-07 | Actualisation IA ciblée sur les changements | Moins de bruit, délai et usage | Périmètre et ancienneté visibles ; recalcul complet autorisé accessible | **ADOPTÉ** |
| PROP-08 | Transformation responsive liste/détail | Conserve la lisibilité sans miniature de desktop | Prototyper navigation arrière, focus et restauration du contexte | **ADOPTÉ** |
| PROP-09 | Échelle d’espacement et grille définies dès V0 | Cohérence entre prototypes | Normatif pour prototypes, **non définitif pour la marque graphique** | **ADOPTÉ POUR V0** |

### P3. Réouverture propriétaire — DÉCISION

**AUCUNE RÉOUVERTURE.** La recherche ne fournit pas de preuve assez forte pour rouvrir les cinq espaces, le dépôt final humain V1, l’autorité humaine, la confidentialité Direction, le mobile compagnon, les portes P0–P7 ou la frontière chiffrage/ERP. Les limites observées renforcent au contraire ces garde-fous.

L’éventualité d’un cache documentaire hors ligne étendu reste une idée de vague future déjà identifiée, pas une décision V0. Elle nécessiterait preuve terrain, définition de sécurité/obsolescence et arbitrage propriétaire avant intégration.

## Q — Gouvernance de conception par expériences

### Q1. Unité de conception

L’unité de travail est une **expérience métier complète**, jamais une page isolée. Une expérience peut traverser plusieurs pages, panneaux, états, appareils et acteurs. Elle doit produire un résultat métier observable et conserver la continuité des droits, preuves, versions et reprises.

Chaque expérience contient au minimum :

1. identifiant, objectif et résultat attendu ;
2. acteurs principaux, contributeurs et profils sans droit ;
3. déclencheur, préconditions et fin observable ;
4. parcours nominal et embranchements ;
5. inventaire des pages et surfaces du catalogue couvertes ;
6. contenu candidat de chaque page ;
7. données nécessaires, sources, versions et fraîcheur ;
8. droits de lecture, action, validation, export et partage ;
9. états C00 et contrats N01–N05 applicables ;
10. rôle exact de l’IA, voie manuelle et comportement en panne ;
11. erreurs, résultats non confirmés, reprise et absence de perte ;
12. critères de réussite métier, UX, accessibilité, sécurité et traçabilité.

### Q2. Cycle obligatoire d’une expérience

| Étape | Sortie | Statut | Porte de passage |
|---|---|---|---|
| **1 — Cadrage** | objectif, acteurs, scénario réel, risques et références | `DRAFT` | le résultat métier et les décisions propriétaires sont identifiés |
| **2 — Parcours écrit** | enchaînement de bout en bout, embranchements et états | `WORK_PROPOSAL` | aucune rupture de rôle, droit, preuve ou reprise connue |
| **3 — Contenu candidat** | pages, informations, actions, messages et variantes | `CONTENT CANDIDATE` | chaque élément est rattaché à un besoin ou une règle |
| **4 — Prototype basse fidélité** | parcours manipulable, sans recherche de finition graphique | `PROTOTYPE CANDIDATE` | les hypothèses les plus risquées peuvent être testées |
| **5 — Audit technique ciblé** | capacités existantes, écarts, risques et tests ciblés | `TECHNICAL ASSESSED` | chaque page est reliée au code réel ou à un manque explicite |
| **6 — Preuve verticale** | chemin minimal interface + droits + backend + données + test | `FEASIBILITY PROVEN` | le parcours critique fonctionne réellement sans architecture spéculative |
| **7 — Revue** | constats propriétaire, métier, UX, technique, sécurité et accessibilité | `REVIEWED` | les écarts sont corrigés ou soumis à arbitrage explicite |
| **8 — Gel de l’expérience** | contenu, ordre, états et critères acceptés | `OWNER EXPERIENCE FREEZE` | décision explicite du propriétaire ; faisabilité déjà prouvée |
| **9 — Maquette détaillée** | représentation visuelle conforme au gel | `VISUAL CANDIDATE` puis `VISUAL VALIDATED` | cohérence, lisibilité, responsive et cas dégradés vérifiés |
| **10 — Contrat technique final** | domaine, interfaces, données, sécurité, tests et exploitation | `TECHNICAL READY` | détail d’exécution complet et traçabilité vers l’expérience prouvée |
| **11 — Tranche verticale complète** | expérience implémentée, sécurisée, observable et testée | `IMPLEMENTED` | définition de fini satisfaite et démonstration bout en bout |

Une correction issue du prototype ou de la preuve technique revient à l’étape appropriée. Un `OWNER EXPERIENCE FREEZE` peut être révisé, mais seulement avec une version, un motif, les impacts et un nouvel arbitrage. Il ne transforme ni une hypothèse non testée en vérité utilisateur, ni une maquette en preuve de faisabilité.

### Q3. Ordre initial des expériences

1. **EXP-01 — Premier accès et première valeur** : connexion, MFA, entreprise minimale, profil Patron, première Affaire et premier Accueil utile.
2. **EXP-02 — Créer ou importer une opportunité** : provenance, qualification, décision de poursuite et transformation en Affaire.
3. **EXP-03 — Importer et comprendre un DCE** : dépôt, traitement, état partiel, résultat non confirmé, synthèse et preuve.
4. **EXP-04 — Résoudre les points bloquants** : C05, contributions, contradictions, questions, impacts et revalidation.
5. **EXP-05 — Préparer une réponse et son chiffrage importé** : production, contrôle, versions, confidentialité et validations.
6. **EXP-06 — Préparer et remettre l’offre** : candidate, contrôles, P5, export, dépôt humain, reçu et reprise.
7. **EXP-07 — Passer, clôturer et capitaliser** : passation, résultat, REX, mémoire validée et règles de réemploi.

L’ordre peut changer si une expérience porte un risque produit, métier, juridique ou technique plus élevé. Toute modification est consignée dans le document d’expériences ; elle ne modifie pas silencieusement les décisions du cahier v0.4.

### Q4. Réemploi de l’ancien plan V0-01 à V0-16

Les seize éléments de la v0.2 restent un **registre de couverture** : shell, système visuel, Accueils, C05, preuve, N01, N02, C11, confidentialité, IA et responsive doivent toujours être matérialisés. Ils ne commandent plus l’ordre de fabrication et sont répartis dans les expériences EXP-01 à EXP-07.

### Q5. Critères de sortie des fondations UX

- le Patron identifie toutes les décisions pertinentes du scénario test en 60–90 secondes et justifie chacune avec une preuve ;
- le Responsable distingue tâche, exigence, inconnue, contradiction et risque sans légende permanente ;
- aucun participant n’assimile P5 à une signature ou un dépôt, ni « transmission déclarée » à « réception prouvée » ;
- les utilisateurs expliquent le dernier état confirmé de N02 et ne relancent pas une action à risque ;
- un conflit N01 ne perd aucune contribution et les validations touchées restent à revalider ;
- six profils internes et le tiers ne voient ni ne déduisent d’informations hors périmètre dans les surfaces testées ;
- le parcours clavier couvre navigation, panneau, preuve, confirmation sensible et retour ;
- le laptop de référence reste exploitable sans défilement horizontal de page ;
- le mobile expose clairement disponible/local/en attente/confirmé et refuse la P5 hors ligne ;
- la panne IA laisse les opérations manuelles critiques disponibles selon leur état réel.

Ces critères sont des conditions de recette future, pas des résultats déjà obtenus. La couverture finale reste l’intégralité des 104 IDs, PUX-01–19 et G01–G52 ; le document d’expériences maintient la matrice de traçabilité correspondante.

## À garder pour une vague future

- Préchargement sélectif d’un dossier terrain, après étude sécurité/obsolescence et preuve du besoin.
- Vue de dépendances graphique si les utilisateurs ne réussissent pas avec la liste relationnelle ; conserver une alternative textuelle.
- Comparaison multi-affaires de motifs de perte, seulement à partir de REX validés et sans exposition inter-périmètre.
- Raccourcis clavier avancés après stabilisation du vocabulaire et des parcours fréquents.
- Préférences de densité enregistrées par utilisateur ; jamais au prix des états obligatoires.
- Aide guidée contextuelle fondée sur l’objet courant, après mesure des demandes d’assistance.

## Sources

1. SMART AO. [Catalogue des écrans et parcours produit OWNER_CONSOLIDATED v0.3](../../docs/00_REFERENCE_ACTIVE/SMART_AO_Catalogue_Ecrans_Parcours_Produit_OWNER_CONSOLIDATED_v0.3.md), et [Cahier directeur Produit & Métier OWNER_CONSOLIDATED v0.4](../../docs/00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v2.0.md). 13 septembre 2026. Sources propriétaires locales.
2. Linear. [Peek preview](https://linear.app/docs/peek). Documentation publique consultée le 13 septembre 2026.
3. IBM Carbon Design System. [Data table — Usage](https://carbondesignsystem.com/components/data-table/usage/). Documentation publique consultée le 13 septembre 2026.
4. Stripe. [How PaymentIntents and SetupIntents work](https://docs.stripe.com/payments/paymentintents/lifecycle). Documentation publique consultée le 13 septembre 2026.
5. IBM Carbon Design System. [Data table — AI presence](https://carbondesignsystem.com/components/data-table/usage/#ai-presence). Documentation publique consultée le 13 septembre 2026.
6. Atlassian. [What is System Health?](https://support.atlassian.com/migration/docs/what-is-system-health/). Documentation publique consultée le 13 septembre 2026.
7. W3C Web Accessibility Initiative. [ARIA Authoring Practices Guide — Dialog Modal Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/). Consulté le 13 septembre 2026.
8. Linear. [Inbox](https://linear.app/docs/inbox) et [Priority inbox](https://linear.app/changelog/2026-09-03-priority-inbox). Documentation et changelog public du 3 septembre 2026, consultés le 13 septembre 2026.
9. GOV.UK Design System. [Check answers](https://design-system.service.gov.uk/patterns/check-answers/). Documentation publique consultée le 13 septembre 2026.
10. Docusign. [Use of Transaction Data](https://www.docusign.com/trust/security/transaction-data-use). Documentation publique consultée le 13 septembre 2026.
11. Bluebeam. [Compare Documents vs. Overlay Pages](https://support.bluebeam.com/revu/features/compare-documents-vs-overlay-pages.html) et [Align PDFs with Overlay Pages](https://support.bluebeam.com/revu/features/align-pdfs-with-overlay-pages.html). Documentation publique consultée le 13 septembre 2026.
12. GOV.UK Design System. [Complete multiple tasks](https://design-system.service.gov.uk/patterns/complete-multiple-tasks/). Documentation publique consultée le 13 septembre 2026.
13. GitHub Docs. [Resolving a merge conflict on GitHub](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/resolving-a-merge-conflict-on-github). Documentation publique consultée le 13 septembre 2026.
14. Ideals. [Viewing Documents as Another Group](https://helpcenter.idealsvdr.com/en/articles/7733389-viewing-documents-as-another-group). Mis à jour le 28 janvier 2026 selon la page ; consulté le 13 septembre 2026.
15. Microsoft HAX Toolkit. [Make clear why the system did what it did](https://www.microsoft.com/en-us/haxtoolkit/guideline/make-clear-why-the-system-did-what-it-did/) et [Guidelines for Human-AI Interaction](https://www.microsoft.com/en-us/haxtoolkit/ai-guidelines/). Consultés le 13 septembre 2026.
16. Procore. [Can I use Procore’s mobile application offline?](https://en-ca.support.procore.com/faq/can-i-use-procores-mobile-application-offline). Documentation publique consultée le 13 septembre 2026.
17. Dalux. [How to use the Dalux mobile app](https://support.dalux.com/hc/en-us/articles/4405944987026-How-to-use-the-Dalux-mobile-app). Documentation publique consultée le 13 septembre 2026.
18. Responsive. [Responding to your assigned questions](https://help.responsive.io/en-US/responsive/article/hCw6QF43-responding-to-your-assigned-questions) et [Proposal Builder review process overview](https://help.responsive.io/en-US/responsive/article/2IXqwYWx-proposal-builder-review-process-overview). Documentation publique consultée le 13 septembre 2026.
19. Notion. [Wikis and verified pages](https://www.notion.com/help/wikis-and-verified-pages). Documentation publique consultée le 13 septembre 2026.
20. Loopio. [What is a Library Review?](https://support.loopio.com/hc/en-us/articles/360026171134-What-is-a-Library-Review). Documentation publique, mise à jour affichée du 27 mars 2024 ; consultée le 13 septembre 2026.
21. Autodesk BuildingConnected. [Bid Leveling Overview](https://support.buildingconnected.com/hc/en-us/articles/47949854611219-Bid-Leveling-Overview) et [What happens to plugs if a proposal is revised?](https://support.buildingconnected.com/hc/en-us/articles/360036998594-What-happens-to-plugs-if-a-proposal-is-revised). Pages mises à jour le 6 janvier 2026 ; consultées le 13 septembre 2026.
22. Reddit, r/estimators. [Talk to me about your love of bid leveling](https://www.reddit.com/r/estimators/comments/1jk85xd/talk_to_me_about_your_love_of_bid_leveling_gc/) et [Building Connected Pro — Ideal Bid form structure](https://www.reddit.com/r/estimators/comments/1popo9g/building_connected_pro_ideal_bid_form_structure/). Retours utilisateurs non vérifiés, consultés le 13 septembre 2026 ; ils ne constituent pas une mesure représentative.

## Limites de la consolidation et statut de validation

Les sources publiques permettent d’étudier des interactions et leurs garde-fous ; elles ne prouvent pas les taux d’adoption, la performance, l’accessibilité complète ni l’adéquation aux PME françaises du BTP. Aucun compte concurrent authentifié, aucun test utilisateur SMART AO, aucun prototype visuel et aucune recette G01–G52 n’ont été exécutés dans cette mission. Les exemples d’affaires, personnes, heures et versions sont fictifs.

Les propositions PROP-01–PROP-09 restent **arbitrées et adoptées**. La prochaine sortie est `EXP-01 — Premier accès et première valeur`, sous statut `WORK_PROPOSAL`. Le Product Freeze et l’UX Freeze restent non déclarés : seules les fondations et la méthode de conception sont consolidées.


---

## R — Registre propriétaire de statut V0 v0.3

| Élément | Statut |
|---|---|
| WORK_PROPOSAL v0.1 | **ABSORBÉ / ARCHIVE DE CONCEPTION** |
| OWNER_CONSOLIDATED v0.2 | **REMPLACÉE / ARCHIVE DE CONCEPTION** |
| OWNER_CONSOLIDATED v0.3 | **RÉFÉRENCE ACTIVE DES FONDATIONS UX** |
| A1–A12 principes UX | **ADOPTÉS COMME CRITÈRES DE RECETTE V0** |
| B Shell / architecture visuelle | **ADOPTÉ POUR PROTOTYPAGE** |
| C Accueil / Minute Patron | **ADOPTÉ POUR PROTOTYPAGE** |
| D C05 « À résoudre » | **ADOPTÉ POUR PROTOTYPAGE** |
| E C11 Remise | **ADOPTÉ POUR PROTOTYPAGE** |
| F C00 règles observables | **ADOPTÉ** |
| G N01 / N02 | **ADOPTÉ** |
| H Confidentialité UX | **ADOPTÉ** |
| I IA contextuelle | **ADOPTÉ** |
| J Responsive / mobile compagnon | **ADOPTÉ POUR PROTOTYPAGE** |
| K Système visuel métier | **ADOPTÉ POUR PROTOTYPAGE** |
| L Benchmark | **PREUVE DE RECHERCHE — NON NORMATIF EN SOI** |
| M Anti-patterns | **INTERDICTIONS V0 ADOPTÉES** |
| N Wireframes textuels | **BASE DIRECTE DES MAQUETTES** |
| O Variantes obligatoires | **À MATÉRIALISER DANS LES PROTOTYPES** |
| PROP-01 à PROP-08 | **ADOPTÉES** |
| PROP-09 | **ADOPTÉE POUR COHÉRENCE V0 ; CHARTE DE MARQUE NON FIGÉE** |
| Réouverture propriétaire | **AUCUNE** |
| V0-01 à V0-16 | **REGISTRE DE COUVERTURE CONSERVÉ — PLUS UN ORDRE DE FABRICATION** |
| EXP-01 à EXP-07 | **ORDRE INITIAL DE CONCEPTION PAR EXPÉRIENCES** |
| Gel page isolée avant prototype | **INTERDIT COMME MÉTHODE PAR DÉFAUT** |
| `OWNER EXPERIENCE FREEZE` | **APRÈS PROTOTYPE ET REVUE, PAR EXPÉRIENCE COHÉRENTE** |
| UX Freeze | **NON ATTEINT** |
| Product Freeze v1.0 | **NON ATTEINT** |
| A2 SourceAnchor | **HOLD** |

### R1. Règle de modification

Toute modification ultérieure d’une fondation V0 doit être classée comme :

- **correction de maquette sans changement de contrat** ;
- **révision UX v0.3.x** si le comportement change sans toucher au métier ;
- **proposition de réouverture propriétaire** si elle touche une décision du Catalogue UX v0.3 ou du Cahier Produit & Métier v0.4.

Aucune maquette, aucun outil de prototypage et aucun futur cahier technique ne peut modifier silencieusement les droits, les preuves, les portes, la distinction P5/dépôt/réception, ou la confidentialité Direction.

### R2. Prochaine sortie attendue

La prochaine sortie est **EXP-01 — Premier accès et première valeur**, rédigée dans le document de travail des expériences. Elle doit relier C15, C01, C03, le shell B1–B5, C00, les droits et les états difficiles avant toute maquette détaillée.

---

**Fin — SMART AO — Fondations UX du prototype V0 — OWNER_CONSOLIDATED v0.3**
