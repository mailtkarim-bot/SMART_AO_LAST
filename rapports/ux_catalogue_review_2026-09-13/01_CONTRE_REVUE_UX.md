# SMART AO — Contre-revue créative du catalogue UX v0.1

**13 septembre 2026 — WORK REVIEW, proposition non approuvée.**

Le v0.1 est une bonne base de couverture, mais **pas encore une bonne architecture d’expérience**. Il décrit surtout où ranger les fonctions. Il doit maintenant expliquer comment un entrepreneur termine son travail sans devoir connaître cette classification.

Ma recommandation : conserver les cinq espaces de premier niveau, organiser les 104 surfaces en **16 espaces de travail canoniques**, faire de l’Affaire le point de continuité et orienter l’Accueil vers les décisions ou contributions attendues. Ce nombre ne désigne ni seize pages physiques ni seize prototypes suffisants. Les 104 contrats restent à valider, y compris leurs droits, états difficiles et variantes mobiles.

Le risque principal est de fabriquer une collection de registres honnêtes mais fatigants : exigences, contradictions, MIRP, risques, tâches, couverture, engagements. Le gain potentiel vient de leur présentation coordonnée, sans confondre leurs natures ni leurs pouvoirs de validation.

## Lire les livrables

| Attente | Livrable |
|---|---|
| A verdict, B problèmes, C manques, D fusions, E suppressions, F navigation | Présent rapport, sections A–F |
| G parcours, points de vue, première heure, états difficiles | Présent rapport, sections G et suivantes |
| H benchmark, I inspirations et discipline des sources | [Recherche comparative](02_BENCHMARK_ET_SOURCES.md) |
| J innovations | Présent rapport, section J |
| K catalogue corrigé, revue individuelle des 104 surfaces | [WORK_REVIEW v0.2](SMART_AO_Catalogue_Ecrans_Parcours_Produit_WORK_REVIEW_v0.2.md) |
| L changelog, recettes et ordre de prototypage | Catalogue proposé, sections finales |

Autorité : [cahier propriétaire v0.4](../../docs/00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_CONSOLIDATED_v0.4.md). Base auditée : [catalogue v0.1](../../docs/00_REFERENCE_ACTIVE/SMART_AO_Catalogue_Ecrans_Parcours_Produit_v0.1.md). Les deux originaux restent inchangés. Toute conception ci-dessous est une **PROPOSITION SMART AO** ; les jugements sont des **INFÉRENCES**. Les faits concurrentiels et témoignages sont identifiés dans le benchmark.

## A — Verdict et notes

Échelle de 0 à 10 : jugement documentaire, pas test utilisateur ni classement concurrentiel. 5 = couverture ou cohérence fragile ; 7 = base solide avec écarts importants ; 9 = contrat très abouti, restant à éprouver. Aucune note ne certifie le code existant.

| Dimension | Note | Motif |
|---|---:|---|
| Couverture métier | **8,5** | Cycle complet, tiers, gouvernance et reprise présents ; certaines interactions transversales restent sans contrat visible précis. |
| Cohérence UX | **6,5** | Affaire et portes structurent bien le fond ; raccords entre les registres et retour au travail insuffisamment définis. |
| Simplicité | **4,5** | 83 éléments sont typés SCREEN ; risque de matérialiser un besoin documentaire en page autonome. Ce nombre ne prouve toutefois pas 83 menus. |
| Différenciation | **6,5** | Sources, IA et bibliothèques existent ailleurs ; la continuité preuve/coût/engagement/remise/passation est plus prometteuse. |
| Expérience Patron | **6** | Bon contenu attendu, mais pas encore de contrat précis de file d’exceptions, de priorité et de décision rapide. |
| Expérience Collaborateur | **6** | Responsabilités explicites ; dispersion entre tâches, exigences, pièces manquantes et réponse. |
| IA-native | **7** | Bonne doctrine non conversationnelle ; placements, refus, reprise et coût des suggestions doivent être matérialisés. |
| Sécurité fonctionnelle | **8** | Version, autorité et preuve sont fortes dans le texte ; fusion et personnalisation peuvent réintroduire des fuites si mal conçues. |
| Potentiel commercial | **7,5** | Problèmes utiles au BTP, notamment marge et remise ; volonté de payer, adoption et coût d’entretien non mesurés. |

**Décision recommandée : corriger les contrats C1 ci-dessous, puis prototyper.** Ni abandon du catalogue, ni validation en l’état, ni promesse d’être « le meilleur au monde » sans essais comparatifs.

## B — Carte des problèmes

Les classes C1/C2/C3 concernent cette revue UX. Elles ne changent ni les blocages métier B0/B1/B2 ni les portes P0–P7.

| ID | Classe | Problème précis / surfaces | Correction et critère de fermeture |
|---|---|---|---|
| UX-C1-01 | Avant prototype | DCE-07/08/12/13 et COL-01 peuvent produire cinq files concurrentes. | Définir une vue « À résoudre » composée d’objets typés. Fermer une tâche laisse l’obligation ouverte tant que sa preuve n’est pas validée. |
| UX-C1-02 | Avant prototype | SUB-01–07 donnent sept destinations à l’opération la plus sensible. | Un espace Remise ; quatre étapes visuelles ; état permanent paquet/autorisation/transmission/réception. Le mot « remis » seul ne suffit jamais. |
| UX-C1-03 | Avant prototype | HOME-01 et GLB-04 ne définissent pas qui voit quoi en priorité. | Séparer décision, contribution et événement ; filtre par habilitation et périmètre avant tout calcul de résumé. Aucun compteur révélant des marges cachées. |
| UX-C1-04 | Avant prototype | La synthèse peut confondre pourcentage de lecture, réponse produite et conformité. | Quatre couvertures distinctes, dénominateurs visibles ; aucun indicateur global vert si un B0/B1 applicable subsiste. |
| UX-C1-05 | Avant prototype | Conflit simultané et issue inconnue figurent en doctrine, sans interaction de résolution assez explicite. | Formaliser N01/N02 dans le catalogue ; conserver contributions et dernier état confirmé ; interdire le succès supposé et le renvoi aveugle. |
| UX-C1-06 | Avant prototype | Les fusions Prix/Entreprise risquent de placer des données Direction dans une vue commune. | Contrats d’accès par champ, agrégat, source, génération et export ; prototype avec rôle sans droit économique. |
| UX-C1-07 | Avant prototype | L’enchaînement onboarding peut imposer toutes les étapes ONB avant première valeur. | Identité et MFA requis ; configuration métier progressive, avec reprise depuis la première Affaire et exemple fictif clairement séparé. |
| UX-C1-08 | Avant prototype | Les vagues placent gouvernance, mobile et panne après les expériences qu’ils conditionnent. | Prototyper des parcours complets avec droits/pannes dès la première vague, puis couvrir toutes les surfaces. Aucun report de la couverture obligatoire. |
| UX-C2-01 | Avant UX Freeze | Navigation Affaire potentiellement surchargée par tous les sous-domaines. | Tester les cinq entrées quotidiennes et les destinations contextuelles proposées ; retrouver visite, partenaire et reçu sans apprendre MIRP. |
| UX-C2-02 | Avant UX Freeze | ENT-01/12 doublonnent la maintenance ; catégories isolées du besoin Affaire. | Un accueil « À tenir à jour » et un catalogue typé ; réemploi contextualisé, snapshot et validité/applicabilité séparés. |
| UX-C2-03 | Avant UX Freeze | PRI-01–05 peuvent devenir un logiciel de chiffrage déguisé. | Import et rapprochement, couverture et scénarios bornés ; mesurer double saisie et compréhension des inconnus. |
| UX-C2-04 | Avant UX Freeze | SHR-01 exige un aperçu exact sans contrat de ses limites. | Rendre N03 testable sur fichiers, métadonnées, commentaires, nom du destinataire et droits réels ; pas de vue administrateur déguisée. |
| UX-C2-05 | Avant UX Freeze | Relève et départ traités par réassignation, sans réception structurée du travail. | N04 : liste des éléments orphelins, nouveau responsable, accusé de reprise ; délégations validées séparément. |
| UX-C2-06 | Avant UX Freeze | Notifications critiques et coût IA classés Support peuvent être sous-testés. | Garder la priorité de base, mais exiger les variantes critiques : canal échoué, seuil atteint, action bloquée et reprise manuelle. |
| UX-C2-07 | Avant UX Freeze | G18 du v0.4 conserve une phrase historique « A02 non encore acceptée ». | Corriger lors de la prochaine édition propriétaire ; appliquer dès maintenant A02/OWN-01 amendée, qui autorisent la suspension immédiate. Ne pas rouvrir cet arbitrage. |
| UX-C2-08 | Avant UX Freeze | Mobile : frontière entre local, consultable et partagé insuffisamment spécifiée. | N05 : disponibilité explicite ; recette réseau intermittent, reconnexion, droit retiré et reprise des captures. |
| UX-C3-01 | Amélioration | Chronologie générique longue. | « Depuis ma dernière revue », avec retour à la liste complète et version de référence visible. |
| UX-C3-02 | Amélioration | Comparaison d’offres partenaires coûteuse à lire. | Mettre d’abord les différences de périmètre et les ajustements à reconfirmer. |
| UX-C3-03 | Amélioration | Valeur de la mémoire peu visible. | Montrer les réemplois acceptés et les affaires qu’une revue débloque, sans gamifier la complétude. |
| UX-C3-04 | Amélioration | Engagements de l’offre éloignés des contraintes chantier. | Vue « promesse → moyen → responsable → réserve », avant et après gain du lot. |

C1 signifie une décision de conception à fermer avant de dessiner le parcours concerné ; le présent rapport apporte une proposition de fermeture, pas l’approbation propriétaire ni sa validation utilisateur.

## C, D, E — Ajouter des contrats, fusionner des expériences, retirer des pages

### Ce qui manque réellement

Je ne recommande pas un nouveau module principal. Cinq contrats visuels explicites manquent à l’inventaire : **N01 conflit de contributions ; N02 résultat d’opération inconnu ; N03 aperçu destinataire ; N04 relève nominative ; N05 disponibilité mobile**. Plusieurs obligations existaient déjà dans le texte : l’ajout porte sur leur visibilité et leur recette, pas sur cinq nouvelles fonctions métiers vendues.

Le parcours Entreprise manque surtout comme parcours bout en bout : ajout, revue, sélection pour une Affaire, contrôle d’applicabilité, snapshot, expiration et actualisation. Il devient **PUX-19**. Le résultat privé, la candidature seule et le lot partiellement gagné sont des variantes des parcours existants, pas trois produits supplémentaires.

### Fusions recommandées

| Avant | Après | Ce qui reste distinct |
|---|---|---|
| Trois accueils + Mon travail | Accueil commun, composition selon responsabilités | Droits, informations et décisions accessibles ; aucun rôle acquis par changement de vue |
| Exigences, contradictions, MIRP, risques, tâches | Synthèse Affaire avec « À résoudre » et filtres typés | Fait, obligation, hypothèse, contradiction, risque et tâche ne deviennent pas un seul statut |
| Import, ingestion, couverture, manquants | Documents avec panneau d’import, inventaire et exceptions | Réception, lecture, revue des exigences et couverture aval |
| Cinq écrans Prix | Espace Prix : couverture, scénarios, moyens, financement | Contribution Direction, droits du métreur, validation P3 et source des montants |
| Plan, checklist, pièces à obtenir | Plan de réponse unique | Rédiger, obtenir, remplir, faire signer ; responsables et critères propres |
| Sept surfaces Remise | Parcours persistant de quatre étapes | Signer, P5, déposer humainement et rapprocher le reçu |
| Accueil Entreprise + file d’expiration | Accueil orienté revue et usages | Catalogue des catégories, données économiques strictement protégées |
| Résultat, passation, REX | Après remise, ouvert selon lot et statut | Attribution annoncée, notification/accord, passation acceptée et capitalisation validée |

### Suppressions assumées

**Retirer comme pages autonomes** : ONB-04 (checklist d’entrée), OPP-02 (recherches sauvegardées), AFF-03/DEC-02 (historiques), DCE-02/06/09 (suivi et exceptions d’inventaire), RES-02/05 (listes du plan), ENT-12 (file d’entretien), ADM-01 (dashboard généraliste), SYS-01 (centre technique quotidien). Leur contenu devient section, filtre, panneau ou vue secondaire accessible depuis le travail. Les historiques et le centre de traitement conservent un accès détaillé pour les besoins longs.

**Supprimer la duplication d’interface** HOME-03/GLB-04 et les pages mobiles conçues comme une seconde application ; préserver leurs vues de rôle et leurs variantes terrain.

**Ne pas supprimer de capacité obligatoire V1** pour faire baisser un compteur. La revue des 104 lignes conclut à des redondances de présentation, pas à la preuve qu’une exigence métier figée est inutile. Les graphes généraux, le score universel de santé, la page de chat vide à l’entrée et les animations de génération ne sont pas ajoutés.

### Séparations nécessaires

L’analyse comparative de deux documents doit pouvoir occuper une vraie grande vue. Le travail sur un mémoire ou un tableur doit pouvoir quitter le petit panneau. La confirmation P5 ne doit pas partager le même bouton que l’export. Les données Direction restent un périmètre protégé même dans Entreprise. Le portail tiers reste isolé. L’audit et la fermeture ne sont pas des actions perdues dans un menu de commentaires.

## F — Navigation proposée

Les cinq espaces sont suffisamment compréhensibles. Les remplacer par Détecter/Comprendre/Décider/Produire/Remettre ferait éclater une même Affaire ; remplacer Entreprise par Documents ferait perdre l’applicabilité et les responsabilités. **Conserver les cinq concepts**, avec Administration séparée visuellement des quatre destinations quotidiennes et visible selon droits.

```text
Navigation permanente
  Accueil         décisions / actions / événements
  Opportunités    radar / qualification
  Affaires        portefeuille / une Affaire
  Entreprise      à tenir à jour / catalogue réutilisable
  Administration  accès / sécurité / données et service

Dans une Affaire — contexte permanent entreprise, lot, phase, tour
  Vue d’ensemble   prochaine action, à résoudre, décisions, activité
  Documents        inventaire, lecture, preuves, comparaison
  Prix             couverture, scénarios, moyens, financement (selon droits)
  Réponse          plan, production, engagements et revue
  Remise           paquet, contrôles, autorisation, preuve

Destinations contextuelles
  Décision          depuis un besoin d’arbitrage
  Partenaires       depuis la synthèse ou le prix
  Résultat/passation depuis le statut après remise
```

Les destinations contextuelles restent trouvables via un menu Affaire explicitement nommé, pas seulement via une alerte qui peut disparaître. Visites et questions acheteur sont des vues nommées de la synthèse. Partenaires possède sa vue complète quand la liste ou le comparatif l’exige. La barre de contexte n’affiche pas dix onglets à tout le monde ; elle n’altère jamais les droits.

Le DCE constitue la preuve reçue. L’analyse produit des assertions qualifiées. MIRP est un registre métier présenté sous « Inconnus et hypothèses ». Les risques relient ces constats aux impacts. Le prix explique leur couverture. La réponse décrit les engagements. Le coffre fige la candidate ; la remise rapporte ce qui s’est passé à l’extérieur. La passation transmet les engagements retenus. Chaque relation doit pouvoir être suivie dans les deux sens sans recopier les mêmes objets.

### Révisions de décisions figées : registre explicite

| Option examinée | Décision concernée | Statut de cette revue |
|---|---|---|
| Supprimer Administration du premier niveau pour n’avoir que quatre espaces | Navigation v0.4 §10 | **PROPOSITION DE RÉVISION NON RETENUE** : faible gain ; garder l’entrée, groupée à part. Aucun changement propriétaire appliqué. |
| Dépôt autonome depuis un bouton « remettre » | DEC-05 / OWN-11 | **PROPOSITION DE RÉVISION REJETÉE** : le besoin immédiat est la clarté de preuve, pas une automatisation hors V1. |
| Chiffrage natif complet et planning chantier | DEC-04 / OWN-07 | **PROPOSITION DE RÉVISION REJETÉE** : doublerait les outils métier avant de prouver l’utilité du contrôle de couverture. |
| Poste d’étude complet mobile / P5 hors réseau | OWN-10 et E11 | **PROPOSITION DE RÉVISION REJETÉE** : compagnon terrain maintenu ; une éventuelle P5 mobile doit être qualifiée, connectée et soumise aux mêmes contrôles. |
| Téléchargement préparatoire de tout un dossier pour consultation hors ligne | Extension possible du périmètre mobile | **OPTION À ARBITRER, NON INCLUSE** : N05 informe de la disponibilité existante, sans promettre un cache intégral. |

Les autres recommandations réorganisent les surfaces dans le périmètre v0.4. Elles restent à approuver comme UX et ne changent pas silencieusement une décision F.

## Points de vue : quinze métiers, aucune attribution automatique de pouvoir

| Personne | En arrivant / action recherchée | Information prioritaire, preuve et erreur à prévenir |
|---|---|---|
| Patron | « Qu’attend-on de moi aujourd’hui ? » → décider ou désigner un délégataire habilité | Porte, périmètre, condition ouverte, délai et exposition autorisée. Brief bref puis preuve ; ne pas exiger la lecture de tous les registres. |
| Responsable d’offre | « Qu’est-ce qui empêche d’avancer ? » → lever/affecter le prochain obstacle | Auteur, échéance, source, porte affectée. La clôture d’une tâche ne valide pas la conformité. |
| Métreur | « Qu’est-ce qui n’est pas dans mon prix ? » → rapprocher besoin et poste | Version du chiffrage, unité, exclusions, coût inconnu. Pas de saisie du devis complet ni zéro implicite. |
| Chargé d’études | « Quelle interprétation doit être vérifiée ? » → lire/comparer puis proposer | Deux sources en conflit et portée ; preuve avant réponse, aucune priorité universelle RC/CCAP inventée. |
| Conducteur | « Que dois-je constater ou prendre en charge ? » → visite ou réserve de passation | Moyen promis, date, lieu et statut de capture. Éviter registres financiers et confusion accusé/P7. |
| Administratif | « Quelle pièce manque à qui ? » → obtenir et vérifier | Entité, type de pièce, phase, validité et signataire. Le dossier reçu d’un tiers ne vaut pas vérification. |
| DAF | « Quel besoin reste non financé ? » → revoir scénario | Hypothèses datées, coût connu/inconnu, pic estimé et preuve de financement ; ne pas confondre contribution et cash. |
| Achats | « Quelle offre est comparable et encore valable ? » → demander complément | Périmètre, exclusion, durée et engagement du partenaire. Le meilleur total apparent peut être incomplet. |
| QSE | « Quelle exigence manque de réponse applicable ? » → qualifier preuve ou contenu | Activité assurée, méthode et critère du marché ; badge à jour ≠ applicable. |
| Commercial | « Que qualifier maintenant ? » → consulter le Radar ou préparer P0/P1 | Source/fraîcheur, lots et effort ; pas de marge Direction révélée par score ou motif. |
| Fournisseur | « Quel prix ou justificatif me demande-t-on ? » → répondre dans le paquet reçu | Périmètre demandé, date, fichiers reçus. Pas de visibilité sur concurrents ni accès à l’Affaire entière. |
| Sous-traitant | « Pour quoi m’engager et avec quelles réserves ? » → fournir offre/pièces | Statut consulté/retenu/engagé et justificatifs ; un upload ne devient pas acceptation contractuelle. |
| Cotraitant | « Quelle pièce et quel pouvoir pour mon entité ? » → contribuer | Lot, rôle dans le groupement, mandat et signature attendus. Ne pas attribuer les preuves à la mauvaise entreprise. |
| Administrateur | « Quel accès faut-il créer ou couper ? » → gérer compte/périmètre | Autorité requise et effets de révocation. Aucun accès métier automatique ni auto-promotion Patron. |
| Support SMART AO | « Quel incident suis-je autorisé à diagnostiquer ? » → intervenir dans le créneau accordé | Client, motif, périmètre et expiration. Aucun tableau métier général ni délégation implicite. |

Jargon à traduire dans les libellés : MIRP → « Inconnus et hypothèses » ; ingestion → « Réception et lecture » ; preflight → « Contrôles avant remise » ; P5 → « Autoriser ce paquet » avec code secondaire ; supersession → « Remplacée par une nouvelle décision ». Conserver les termes techniques dans les détails utiles à l’audit.

## Expérience Patron : une file d’exceptions explicable

En tête : les décisions qui attendent une autorité, les blocages de remise proches de l’échéance, les conditions échues, puis les expositions économiques accessibles. À importance équivalente, l’échéance départage. L’utilisateur doit pouvoir comprendre pourquoi une affaire apparaît ; l’IA ne classe pas seule selon un score opaque.

Chaque ligne dit : **Affaire / lot — ce qui a changé — décision attendue — échéance — obstacle ou hypothèse — responsable préparateur**. Le détail montre les pièces déterminantes et les éléments non établis. L’exposition financière n’apparaît que pour les droits adaptés ; aucune variante « sans chiffres » ne doit révéler indirectement la marge via total et coûts.

Exemple fictif : « École des Pins, lot 2 — devis levage expiré — P3 à réexaminer — décision nécessaire avant jeudi 11 h — renouvellement demandé à Samira ». Actions : lire le bref, demander complément, décider dans la limite de son pouvoir. Pas de bouton général « tout valider ». Si aucun arbitrage n’attend le Patron : le dire, et laisser les alertes de surveillance distinctes.

Mesure proposée : en 90 secondes, un dirigeant identifie les décisions urgentes et les explique sans ouvrir dix pages. Cible de test, aucun résultat acquis. Observer aussi les faux négatifs : une affaire dangereuse doit être repérée même si elle n’est pas la plus récente.

## G — Parcours optimisés

### Première heure : première valeur après l’identité, pas après une GED complète

L’onboarding demeure accompagné, conformément à OWN-06 ; aucune inscription publique autonome ajoutée. L’invitation nomme l’entreprise, l’invitant et le rôle prévu. Après activation et MFA, confirmer l’organisation et les accès ; ne demander que les données nécessaires à l’action suivante. Le responsable peut ouvrir une première Affaire avec les lacunes clairement signalées. Un expert invité arrive directement sur sa contribution autorisée.

Un exemple fictif peut illustrer une contradiction et sa preuve, mais doit porter « démonstration » partout et ne jamais polluer les références de l’entreprise. La Mémoire Entreprise se complète depuis la première pièce réellement utile. L’identité de l’entreprise candidate et les pouvoirs nécessaires ne sont pas facultatifs : différer les champs de confort ne permet pas de franchir une porte sans ses prérequis.

Les durées suivantes sont des **objectifs d’étude**, pas des promesses : premiers accès/MFA pendant l’accompagnement ; première valeur sur une preuve dans les 15 minutes suivant l’accès ; première action attribuée pendant la première heure. Chronométrer séparément les attentes d’analyse pour ne pas maquiller un traitement lent en réussite UX.

### Dix-neuf parcours et leurs critères de sortie

| Parcours | Enchaînement proposé | Arrêt / retour nécessaire et réussite à observer |
|---|---|---|
| **PUX-01 — Entrée** | Invitation → activation/MFA → organisation confirmée → première action/Affaire ; enrichissement Entreprise progressif | Invitation invalide, compte déjà présent et récupération accessibles. L’utilisateur explique la valeur avant la fin de l’accompagnement. |
| **PUX-02 — BOAMP vers Affaire** | Radar → fiche avec source/lots → P0/P1 par habilité → Affaire liée | Dossier/phase de candidature documentés selon R04 ; provenance et fraîcheur conservées ; doublon signalé ; pas de création d’Affaire par simple consultation. |
| **PUX-03 — Invitation privée/manuelle** | Ajouter source reçue → qualification → P1 → Documents/Synthèse | Dates inconnues explicites ; pas de formulaire public imposé ; accord privé distingué de l’offre. |
| **PUX-04 — DCE vers compréhension** | Import dans Documents → inventaire confirmé → lecture partielle visible → première exception sourcée → affectation depuis Synthèse | Une pièce manquante n’interdit pas de lire les autres. Le responsable distingue reçu, lu, revu et couvert. |
| **PUX-05 — Rectificatif** | Ajouter version → comparer → confirmer impacts → retrouver validations à rouvrir → reprendre le travail affecté | Ancien paquet et décision préservés ; aucune revalidation générale silencieuse ni maintien automatique d’un ajustement devenu douteux. |
| **PUX-06 — GO/NO-GO** | Synthèse → bref de décision/P2 → coûts et moyens pertinents → décision avec conditions → file de suivi | Distinguer P2 et P3. Inconnus, B0/B1/B2 et délégation visibles ; conditions avec responsable et échéance. |
| **PUX-07 — Protection du prix** | Chiffrage importé → anomalies/rapprochements → périmètre non couvert → scénario/moyens/cash → P3 | Source du coût consultable ; total incomplet signalé ; aucun moteur complet de métrés ajouté. |
| **PUX-08 — Réponse** | Plan unique → sélectionner livrable → produire/obtenir/remplir → revue → engagements → conformité/P4 | Auteur distinct du valideur ; cadres imposés conservés ; réemploi revu pour cette Affaire. Candidature seule : P3 non applicable avec motif. |
| **PUX-09 — Remise** | Paquet candidat → signatures/contrôles → P5 avec step-up → export exact → geste humain externe → rapprochement du reçu | Quatre étapes visuelles, plusieurs contrôles distincts. Pas de réussite complète sans preuve suffisante. Reçu partiel expliqué sans exiger un inventaire que la plateforme ne fournit pas. |
| **PUX-10 — Redépôt** | Remise précédente → nouvelle candidate complète → revue des changements/P4/P5 selon impacts → nouveau dépôt humain/reçu | Aucun ajout isolé présenté comme nouvelle offre complète ; précédent conservé. |
| **PUX-11 — Résultat/passation** | Résultat par lot → preuve accord/notification → engagements/moyens → réserves du conducteur → P7 et accusé → REX | Un lot perdu ne part pas au chantier ; P7 n’est pas un ordre de service ; réserve ne disparaît pas à la clôture. |
| **PUX-12 — Perte/REX** | Résultat avec source → motif connu ou inconnu → enseignement proposé → revue Entreprise | Pas de motif inventé ni propagation automatique d’une hypothèse dans la mémoire. |
| **PUX-13 — Tiers** | Sélection depuis objet/Affaire → paquet/destinataire/durée → aperçu N03 → contrôle/confirmation → portail → upload contrôlé → gestion/révocation | Le tiers sait quoi faire et voit son accusé ; accès ouvert ≠ email reçu. Révoquer ne rappelle pas les téléchargements. |
| **PUX-14 — Départ salarié** | Suspendre/révoquer → inventorier objets orphelins → N04 relève → confirmer habilitations distinctes | Couper l’accès avant une longue passation ; conserver auteur et décisions historiques ; aucune transmission automatique des pouvoirs. |
| **PUX-15 — Dernier Propriétaire compromis** | Suspension immédiate → incident/récupération d’autorité → nouveau facteur/accès contrôlé → revue des accès | OWN-01 amendée appliquée ; le support ne s’attribue aucun pouvoir métier et le seul email ne restaure pas le compte. |
| **PUX-16 — Réversibilité/fermeture** | Périmètre des données → autorités requises → export et vérification → gel/conservation → fermeture selon règles | Export interrompu/litige bloque la suppression concernée ; l’autorité organisationnelle ne donne pas accès aux secrets Direction. |
| **PUX-17 — IA indisponible** | Bandeau local/global selon portée → dernier résultat daté → travail manuel → reprise surveillée | Documents, décisions, coffre et export utilisables selon droits et état réel ; pas de double génération publiée à la reprise. |
| **PUX-18 — Terrain** | Action/visite → disponibilité N05 → capture locale → attente → confirmation de synchronisation → revue utile à l’Affaire | Aucune photo locale annoncée partagée ; ne pas demander un GO économique depuis une simple notification terrain. |
| **PUX-19 — Entreprise, ajouté** | Besoin Affaire ou file d’entretien → élément/document → revue de validité → applicabilité au lot → copie de référence → usage → alerte de changement | Une assurance valide mais hors activité est refusée ; une mise à jour ne remplace pas rétroactivement la preuve utilisée dans une offre. |

Ne pas utiliser le nombre de clics comme unique mesure. Mesurer les changements de contexte, les erreurs d’interprétation, le retour après interruption et l’aide nécessaire. Une étape de vérification utile peut ajouter un clic tout en évitant une mauvaise remise.

## Mémoire Entreprise : entretenir ce qui sert

ENT-01 devient « À tenir à jour », avec trois entrées : éléments utilisés dans une affaire proche, documents expirant, contenus à revoir. ENT-02–10 restent des catégories du même catalogue, avec formulaires adaptés. Pas de fiche universelle qui demanderait les mêmes champs à un matériel, une assurance et une méthode.

Chaque élément sépare **source/propriétaire**, **validité propre**, **portée**, **revue**, **utilisations dans les Affaires**. À la sélection : préciser l’entité candidate, l’activité, la période, le lot et le droit de réemploi pertinent. L’étiquette « applicable ici » est une conclusion de revue contextualisée. Conserver la version effectivement utilisée et signaler les Affaires ouvertes affectées par une expiration ou un retrait.

L’intérêt pour l’utilisateur n’est pas « votre profil est complet à 86 % », mais « la revue de cette assurance débloque deux dossiers où vous intervenez », sous réserve que ces dossiers soient autorisés. L’entretien porte sur les usages utiles, sans rendre invisibles les autres échéances obligatoires. Les données économiques ENT-11 demeurent un compartiment Direction.

## Prix : montrer la perte possible sans réinventer le chiffrage

L’ouverture de Prix montre le fichier importé et sa version, la part de coût non couverte, les hypothèses acceptées ou à confirmer, puis les moyens/cash pertinents. Un graphique d’exposition n’est utile que si les montants sont comparables et les inconnus lisibles. Si le montant est inconnu, écrire « non estimé » ; ne pas dessiner une barre de longueur zéro.

Exemple de recette v0.4 : vente 120, coûts 100 → contribution 20 et taux sur vente 16,67 %. Ajouter un besoin de levage non chiffré rend l’indicateur incomplet. Il ne permet pas d’affirmer que la contribution reste 20. Le financement peut manquer même si la contribution estimée est positive ; la capacité peut manquer malgré une trésorerie disponible. Ces trois diagnostics restent séparés.

Comparer les partenaires dans le même contexte de prix : pièce d’origine, périmètre, exclusions, date de validité, compléments estimés et validation de comparaison. L’outil aide à détecter ce qui manque ; il n’exige pas que le métreur abandonne son outil habituel. Les témoignages à l’origine de cette prudence sont documentés dans le [benchmark](02_BENCHMARK_ET_SOURCES.md).

## Remise : quatre étapes, aucune ambiguïté de preuve

1. **Préparer le paquet** : candidate exacte par entreprise/lot/phase/tour, pièces, manifeste et signatures nécessaires.
2. **Contrôler et autoriser** : P4 courant, B0/B1 applicables levés, risques B2 traités, destinataire/canal/heure, habilitation et step-up P5. Le bouton dit « Autoriser le paquet [version] ».
3. **Déposer à l’extérieur** : exporter cette version, afficher consignes et échéance source/conversion ; l’opérateur agit humainement. Une déclaration de transmission reste une déclaration.
4. **Rapprocher le reçu** : consultation/lot/tour/entreprise/date ; contenu seulement selon données disponibles. Afficher réception non prouvée, incohérente ou prouvée avec rapprochement partiel/complet.

Le résumé permanent indique séparément **paquet**, **autorisation**, **transmission**, **preuve de réception**. Un changement après P5 ouvre une nouvelle candidate et invalide l’usage de l’autorisation pour cette version. Une preuve d’un dépôt effectué malgré blocage peut être enregistrée comme remise hors autorisation SMART AO, conformément à R05 ; elle ne régularise pas rétroactivement P5.

Les signatures obtenues extérieurement sont réimportées avant le contrôle final. Aucun clic de validation n’est nommé signature légale. Un reçu sans inventaire peut prouver la réception du pli sans prouver tous les fichiers. Préserver également la copie de sauvegarde comme canal/objet distinct lorsque pertinente, sans la présenter comme un remplacement automatique du dépôt principal.

## IA : rendre service dans l’action

Conserver « IA-native, pas chat-first ». À l’ouverture d’une Affaire : bref daté, portée lue, changements et inconnus. Sur un problème : « Expliquer », « Comparer », « Préparer une question » ou « Proposer une réponse ». Dans Réponse : proposition différenciée du contenu validé. Dans Prix : proposition de rapprochement avec coût/source, jamais invention d’un montant manquant.

Chaque suggestion doit montrer la matière utilisée, sa version, sa limite et l’action humaine attendue. L’acceptation ne doit pas franchir une porte sans l’autorité correspondante. Les contenus des documents ne peuvent pas ordonner un envoi externe ou un élargissement de droits. L’assistance conversationnelle reste utile pour demander une explication approfondie ; elle n’est pas le seul moyen d’atteindre un contrôle critique.

Ne pas régénérer un briefing intégral à chaque retour sur la page. **Proposition d’économie d’usage IA** : reprendre le dernier bref qualifié, montrer son ancienneté et proposer une actualisation ciblée sur les changements autorisés. Ce n’est ni un choix technique de cache ni un pourcentage d’économie de tokens démontré. Les quotas, limites et échecs restent visibles ; la reprise ne doit pas facturer ou publier deux fois une action ambiguë sans contrôle.

## États difficiles : contrats de langage et de reprise

Les exemples sont des libellés proposés. L’état doit apparaître au lieu de travail ; une page système seule ne suffit pas.

| État | Ce qui est montré | Action sûre / ce qui reste possible |
|---|---|---|
| IA indisponible | « Analyse indisponible. Dernière analyse confirmée : … » avec portée | Lire les originaux et travailler manuellement ; relancer explicitement sans écraser une décision récente. |
| BOAMP indisponible | Dernière collecte, source affectée, fraîcheur | Consulter l’existant qualifié de non actualisé ; saisir une invitation manuellement. |
| Document illisible | Fichier/page concernés ; aucune extraction présentée comme complète | Lire les autres éléments ; obtenir copie ou preuve de lecture humaine. |
| DCE partiellement analysé | Inventaire reçu/lu/non lu avec dénominateur | Prioriser les pièces critiques ; aucune date de remise inventée. |
| Rectificatif non traité | Nouvelle version reçue, impacts non confirmés, portes à examiner | Comparer ; ne pas réutiliser aveuglément les anciennes validations. |
| Conflit de modification | Version enregistrée et contribution concurrente, auteurs/heures | N01 : préserver les deux, choisir/proposer une résolution puis faire revoir les décisions affectées. |
| Session expirée | Contenu protégé masqué, dernier enregistrement confirmé identifié après reconnexion | Restaurer le brouillon autorisé ; distinguer les changements locaux ; traiter un conflit éventuel. |
| Source absente | Assertion marquée non vérifiable, pièce/localisation manquante | Chercher la bonne source ; ne pas substituer une citation approchante sans le dire. |
| Droit insuffisant | « Cette action nécessite une habilitation » sans contenu sensible | Préparer le travail autorisé ou demander à l’autorité compétente ; ne pas prétendre que le dossier est vide. |
| Remise sans reçu | « Transmission déclarée — réception non prouvée » | Rechercher/importer preuve ; conserver paquet et déclaration ; aucun badge global de succès. |
| Reçu incohérent | Différences de lot/tour/entreprise/instant explicitées | Rectifier la preuve ou déclarer incident, sans fabriquer une réussite. |
| Synchronisation en attente | Local / en attente / confirmé, par capture | Réessayer lorsque possible ; conserver le local selon sécurité ; prévenir avant toute action qui le perdrait. |
| Issue d’opération inconnue | « Résultat non confirmé » et dernier état connu | N02 : vérifier état/historique avant une nouvelle tentative. Pour dépôt externe, demander la preuve/opérateur ; aucun contrôle distant inventé. |

À ajouter aux essais normaux : vide réel, filtre sans résultat, données non accessibles et erreur de chargement doivent avoir quatre messages différents. Lecture clavier, zoom et retour au contexte sont nécessaires sur les variantes critiques ; rouge/vert seuls ne suffisent pas.

## J — Douze innovations proposées, avec décision de périmètre

Ces idées sont des propositions de conception, pas des inventions dont l’unicité mondiale serait prouvée. V1 signifie amélioration à prototyper dans le contrat existant ; exploration signifie ne pas l’ajouter au gel sans preuve de valeur.

| Idée / problème | Valeur et fonctionnement | Risque | Validation proposée / pilote |
|---|---|---|---|
| **1. La minute Patron** — arbitrage noyé | Bref par décision : changement, portée, inconnus, condition et autorité ; preuve accessible immédiatement. | Simplification qui masque un B1 ; hiérarchie opaque. | 5 dirigeants, trois affaires urgentes ; repérer tous les blocages déterminants. **V1, C01/C07.** |
| **2. À résoudre, sans doublons** — six registres dispersés | Une ligne par objet avec liens vers obligations/tâches/impacts ; filtres par porte ou rôle. | Tout réduire à une tâche générique. | Faire fermer une tâche sans preuve et vérifier que l’exigence reste ouverte. **V1, C05.** |
| **3. Diff de décision** — rectificatif difficile à interpréter | Comparer ce qui fondait le GO avec ce qui est connu maintenant, puis lister les validations dépendantes. | Inférence IA présentée comme impact certain. | Rectificatif après P4 et après P5 ; distinguer impact confirmé/non interprété. **V1, C06/C07.** |
| **4. Facture de l’inconnu** — risque de marge abstrait | Liste des besoins sans poste, des devis expirés et des hypothèses ; montant seulement s’il est estimé et sourcé. | Double compte ou fausse précision. | Métreur/DAF sur levage absent, transport exclu et quantité incertaine. **V1, C08.** |
| **5. Question prête à envoyer** — blocage qui traîne | Depuis une contradiction, proposer un brouillon neutre avec les deux sources et l’impact attendu. | Envoi autonome ou dévoilement de stratégie. | Responsable et conseil relisent ; émission humaine séparée et tracée. **V1, C05.** |
| **6. Passeport de réemploi** — bibliothèque trompeuse | Résumé source/version/validité/portée/accord d’usage pour l’élément sélectionné dans l’Affaire. | Badge unique trop rassurant. | Assurance à jour hors activité et référence partiellement réalisée. **V1, C13/C10.** |
| **7. Bon paquet, bonne preuve** — confusion avant remise | Résumé fixe des quatre états : candidate, autorisation, transmission, réception. | L’utilisateur ne comprend pas un reçu partiel. | Opérateur explique un reçu sans inventaire sans conclure « tout est vérifié ». **V1, C11.** |
| **8. Promesse transmise au chantier** — contenu commercial oublié | Chaque engagement majeur relie formulation, coût/moyens, responsable et réserve de prise en charge. | Glissement vers gestion chantier complète. | Conducteur retrouve une intervention promise sous 2 h et émet une réserve. **V1, C12.** |
| **9. Reprise à J−2** — absence d’un responsable | Relève nominative montrant conditions, validations, pièces et questions orphelines. | Hériter de pouvoirs sans autorisation. | Suppléant reprend le travail mais ne peut pas signer P5 sans délégation. **V1, N04.** |
| **10. Ce qui a changé pour moi** — trop d’événements | Vue dérivée depuis la dernière revue confirmée, limitée aux objets autorisés qui demandent une action. | Masquer un problème ancien encore ouvert. | Garder une condition échue visible même sans nouvel événement. **V1, C01/C05.** |
| **11. Préparer ma visite** — information manquante sur place | Avant départ : pièces disponibles, obligations de présence, preuves attendues et captures non synchronisées. | Promesse de dossier intégral hors ligne. | Mode avion puis reconnexion ; pas de cache global inclus implicitement. **V1 pour disponibilité, N05 ; préchargement étendu à arbitrer.** |
| **12. Une revue Entreprise qui débloque du travail** — entretien sans intérêt visible | Montrer les Affaires autorisées qui utilisent une preuve à revoir ; proposer l’ordre des revues. | Compteurs révélant des dossiers confidentiels. | Administratif limité à deux affaires ne voit aucun indice des autres. **V1, C13.** |

Explorations volontairement écartées du périmètre immédiat : graphe global des dépendances comme accueil, prédiction de chance de gagner, notation concurrentielle automatique, simulation complète de trésorerie/planning, agent de dépôt autonome. Une liste de dépendances utile précède un graphe ; un scénario borné précède un simulateur.

## Plan de validation de la proposition

Recruter au minimum, comme plan et non comme étude déjà réalisée : cinq PME aux pratiques différentes ; faire participer dirigeants, responsables d’offre et métreurs, puis les autres rôles sur leurs passages critiques. Comparer le v0.1 matérialisé simplement et la proposition sur les mêmes tâches, en alternant l’ordre pour réduire l’effet d’apprentissage.

Mesures : décision ou objet trouvé, mauvaise interprétation, erreur de version/droit, besoin d’aide, reprise après interruption, temps jusqu’à première valeur, travail ressaisi. Critères éliminatoires : autorisation erronée, fuite de données, reçu présenté à tort comme complet, perte de contribution ou disparition d’un blocage critique. Une erreur de sécurité impose correction et nouvelle recette ; une petite moyenne de temps ne la compense pas.

Cas principal fictif : AO public multilot avec RC/CCAP contradictoires, plan annoncé absent, visite obligatoire, chiffrage incomplet, fournisseur expiré, GO sous condition, rectificatif après validation, reçu partiel, un lot gagné et un perdu. Variantes : candidature seule ; offre privée suivie d’une commande modifiée ; absence du Patron ; départ salarié ; panne IA ; support expiré ; terrain hors réseau. Couvrir également les petites affaires sans incident pour éviter d’optimiser uniquement un parcours catastrophe.

Le [catalogue v0.2 proposé](SMART_AO_Catalogue_Ecrans_Parcours_Produit_WORK_REVIEW_v0.2.md) relie les 104 surfaces, les 19 parcours et G01–G52 aux futures recettes. **Aucun prototype, test utilisateur, UX Freeze ou Product Freeze n’est déclaré réalisé par ce rapport.**
