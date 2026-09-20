# SMART AO — Catalogue des écrans et parcours produit
## WORK_REVIEW v0.2 — proposition d’organisation de la surface UX complète

**Date : 13 septembre 2026. Statut : proposition non approuvée, avant prototypes.**

Source métier : [OWNER_CONSOLIDATED v0.4](../../docs/00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_CONSOLIDATED_v0.4.md). SHA-256 : `af461cf4782af01575e707d97a724ac1c5d1a5c2229b9ec820010c58a4e05042`.

Base de comparaison : [catalogue v0.1](../../docs/00_REFERENCE_ACTIVE/SMART_AO_Catalogue_Ecrans_Parcours_Produit_v0.1.md). SHA-256 : `f94c8e805040fc1150149ba1252aa89f22cc7cb3c5aae8c7c522a86e9ec29f80`.

Compagnons : [contre-revue et parcours détaillés](01_CONTRE_REVUE_UX.md), [benchmark et sources](02_BENCHMARK_ET_SOURCES.md).

## 0. Portée et précédence

Cette proposition remplace **l’organisation de présentation** du catalogue v0.1 si le propriétaire l’approuve. Elle ne remplace pas le cahier métier v0.4. Les missions, rôles, états obligatoires et niveaux minimaux de fidélité du v0.1 demeurent applicables sauf modification explicite ci-dessous ; aucune réduction de pouvoir de preuve ni extension de droit n’est implicite dans une fusion.

Les 104 identifiants d’origine sont conservés comme contrats de couverture. Le v0.1 compte 83 SCREEN, 10 FLOW, 2 PANEL, 3 STATE, 1 SHELL et 5 RESPONSIVE ; 52 UX-Critical, 43 UX-Primary et 9 UX-Support. Le v0.2 propose **16 espaces canoniques**, une structure transversale **C00** et **5 contrats transversaux nouvellement individualisés N01–N05**. Ce sont des unités de conception de natures différentes : ne pas additionner 104 + 16 + 5 pour annoncer un nombre d’écrans.

Les surfaces regroupées gardent leurs scénarios de validation. La couverture complète V1 demandée par OWN-12 et v0.4-R1 ne se réduit pas aux 12 pivots E01–E12, ni aux 16 espaces ci-dessous. Une réduction de pages n’est pas un gain de développement ou d’usage mesuré.

**Décisions préservées** : cinq espaces principaux ; IA-native non chat-first ; création accompagnée ; MFA interne obligatoire ; délégations explicites ; dépôt humain ; contrôle de chiffrage importé ; mobile compagnon ; réemploi validé ; source/version/autorité avant action. P0–P7 restent les portes métier, UX-Critical/Primary/Support les priorités de prototype, C1/C2/C3 les priorités de la contre-revue, B0/B1/B2 les blocages/risques métier. Ces vocabulaires ne sont pas interchangeables.

Les options qui modifieraient une décision figée sont signalées dans le registre de révision du rapport ; elles ne sont pas incluses silencieusement ici. En particulier : aucune P5 hors ligne, aucun dépôt autonome, aucun chiffrage intégral et aucun téléchargement intégral hors ligne promis.

## 1. Navigation et formats

Premier niveau : **Accueil / Opportunités / Affaires / Entreprise / Administration**. Administration est groupée à part dans la navigation, selon droits, mais demeure un espace identifiable. Recherche, activité, traitements et profil sont des utilitaires de C00.

Dans l’Affaire : **Vue d’ensemble / Documents / Prix / Réponse / Remise**, selon accès. Décision, Partenaires, Résultat/passation sont des destinations contextuelles accessibles par des actions explicites et par le menu Affaire. Visites et Questions acheteur ont des vues nommées depuis la synthèse. Le contexte entreprise candidate/lot/phase/tour demeure visible.

Formats proposés : **vue** = espace de travail avec lien direct ; **onglet** = vue nommée du même espace ; **section** = contenu dans sa page ; **panneau** = inspection/action courte avec retour ; **parcours** = séquence guidée reprenable ; **état** = variante avec action de reprise ; **mode large** = tâche longue en pleine largeur ; **mobile** = variante ciblée. Un panneau peut s’ouvrir en mode large sans créer une nouvelle destination de menu.

Ne pas empiler des panneaux. Au clavier, focus sur le contenu ouvert puis retour à son déclencheur ; sur petit écran, le détail remplace temporairement la liste avec retour explicite. Filtres et position de lecture sont conservés. Un lien direct vérifie les droits comme l’entrée normale.

## 2. Contrat commun C00

Applicable à chaque ligne de ce catalogue, y compris les variantes non critiques :

1. **Contexte et droits** : entreprise/périmètre visibles ; accès vérifié avant contenu, recherche, compteurs, source, réponse IA et export. Admin/Propriétaire/Patron sont distincts. Une préférence d’affichage ne donne aucun pouvoir.
2. **Preuve** : état qualifié, source exacte et version accessibles ; original et dérivé identifiables ; assertion IA et validation humaine distinctes. Source manquante = non vérifiable, pas citation reconstruite.
3. **Actions** : proposer, enregistrer, faire revoir, autoriser, partager et exporter séparés lorsque leur effet diffère. Blocage B0/B1 non levé ne peut pas devenir conforme par acceptation Patron ; risque B2 arbitrable selon R05.
4. **Reprise** : dernier enregistrement confirmé visible ; local distingué ; contributions concurrentes préservées ; résultat non confirmé jamais annoncé réussi. Une fermeture de notification ne ferme pas l’objet métier.
5. **Accessibilité** : clavier, zoom/reflow, libellés, erreurs associées, progression annoncée sans envahissement ; aucune signification fondée uniquement sur couleur ou geste de glisser-déposer.
6. **États** : vide réel, filtre vide, chargement, partiel, refus d’accès, erreur, blocage, revalidation, panne et reprise matérialisés lorsque pertinents. Un refus ne révèle pas un secret. Le détail des 13 états difficiles est dans le rapport ; N01/N02/N05 les rendent testables.
7. **IA** : explication et suggestion contextualisées, génération datée, portée connue ; opération manuelle maintenue pour les fonctions critiques selon état réel. Pas d’exécution d’ordres contenus dans un document ni d’envoi externe autonome.
8. **Temps** : échéance source et fuseau identifiés ; conversion explicite ; conflit de dates sans report automatique. Une heure locale d’appareil ne remplace pas l’échéance de l’acheteur.

**Rôles et priorités de chaque surface** : ils restent ceux de la ligne portant le même identifiant dans le v0.1. Les fusions ne mettent pas en commun leurs droits. Les sous-scénarios critiques identifiés en section 5 reçoivent une recette critique même si leur parent est UX-Primary ou UX-Support.

## 3. Les 16 espaces de travail et leur contrat

| Code / espace | Entrée et première information | Action et continuité | Preuve / droits / état déterminant |
|---|---|---|---|
| **C01 — Accueil** | Connexion ou navigation ; décisions et contributions attendues dans le périmètre | Ouvrir un travail avec contexte puis revenir à la même liste ; événements séparés | Priorité expliquée, condition persistante ; données Direction seulement aux habilités ; aucune urgence cachée par un filtre de nouveautés |
| **C02 — Radar** | Opportunités ; critères et fraîcheur BOAMP | Filtrer, conserver recherche, ouvrir fiche ou saisir invitation | Source/doublon/collecte partielle ; panne visible, saisie manuelle accessible |
| **C03 — Opportunité** | Résultat Radar ou ajout manuel ; entreprise/lot/date et inconnus | Qualifier, préparer P0/P1, ouvrir l’Affaire autorisée et garder le lien | Autorité P0/P1 ; pas de score faisant décision ; cas candidature sans prix |
| **C04 — Portefeuille** | Affaires ; responsable, état, échéance et prochaine porte | Filtrer puis rejoindre l’Affaire ; vues enregistrées selon droits | Aucun agrégat révélant affaire ou marge interdite ; vide réel distinct de filtre vide |
| **C05 — Synthèse Affaire** | Affaire ou retour d’un travail ; prochain obstacle, lot/phase/tour | Vue À résoudre, affectation, questions, visite, activité et préparation décision | Objets typés liés, tâches distinctes des preuves ; condition ouverte maintenue ; statut partiel et rectificatif visibles |
| **C06 — Documents et preuves** | Import, source citée ou navigation ; inventaire et version | Déposer, lire, comparer en mode large, revenir à l’objet d’origine | Reçu/lu/revu/couvert séparés ; quarantaine/illisible/non supporté ; original préservé ; preuve accessible selon droits |
| **C07 — Décision** | Carte d’arbitrage ; porte/périmètre/version, faits et inconnus | Préparer, demander complément, GO/condition/attente/NO-GO/abandon selon porte | Habilitation et motif ; B0/B1/B2 ; preuve de levée ; conflit de deux décisions et supersession tracés |
| **C08 — Prix** | Navigation ou besoin non couvert ; fichier et hypothèses | Rapprocher coûts, comparer scénarios/partenaires, moyens/cash puis préparer P3 | Montants sourcés, inconnus jamais zéro ; total importé à vérifier ; confidentialité économique par champ/agrégat |
| **C09 — Partenaires** | Synthèse ou Prix ; demandes et statut d’engagement | Consulter, recevoir, comparer via C08, demander pièces via partage ciblé | Fournisseur/sous-traitant/cotraitant distincts ; exclusions/validité/mandats ; reçu ≠ engagé |
| **C10 — Réponse** | Plan ; livrables à produire/obtenir/remplir/revoir | Ouvrir travail en mode large, sources latérales, revue puis engagements et P4 | Original/copie, IA/humain ; cadres imposés ; aperçu et export autorisés ; sauvegarde/conflit ; fichier externe qualifié si nécessaire |
| **C11 — Remise** | Candidate ou alerte ; paquet/autorisation/transmission/réception | Préparer → contrôler/autoriser → dépôt externe humain → reçu ; historique et nouvelle candidate | Signature ≠ P5 ≠ dépôt ≠ reçu ; step-up ; manifeste exact ; limites du rapprochement ; nouveau paquet après changement |
| **C12 — Résultat et passation** | Après remise, lot concerné ; preuve d’accord/notification et périmètre | Traiter demande/P6, résultat, passation/P7, réserves et REX | Lot gagné seul transmis ; engagement exact et responsable ; P7 ≠ ordre de service ; enseignement validé avant mémoire |
| **C13 — Entreprise** | Besoin de réemploi ou menu ; revues et utilisations affectées | Revoir élément typé, sélectionner pour l’Affaire, contrôler applicabilité et figer version utilisée | Validité/applicabilité séparées ; droits de réemploi ; Direction isolée ; original sensible distinct du dérivé partageable |
| **C14 — Administration** | Menu habilité ou incident ; accès/sécurité/données et service | Inviter/révoquer, déléguer selon autorité, auditer, support, export/fermeture | Pas d’auto-élévation ni de lecture métier implicite ; support borné ; fermeture bloquée si export/litige non traité |
| **C15 — Accès** | Invitation, connexion, expiration ou récupération | S’identifier, MFA, confirmer organisation, reprendre travail autorisé | Facteurs jamais exposés ; compte compromis suspendable ; dernier Propriétaire récupéré selon preuve organisationnelle |
| **C16 — Paquet tiers** | Invitation de partage ; demande précise et fichiers autorisés | Consulter et déposer une pièce puis voir accusé de réception technique | Identité/durée/périmètre ; expiration/révocation ; upload non fiable jusqu’aux contrôles ; aucune navigation interne Affaire |

### Détails structurants des fusions

**À résoudre (C05)** rassemble des objets, pas des validations. Une exigence possède une source et une satisfaction ; une hypothèse une justification et une échéance ; une contradiction au moins deux sources ; un risque un impact ; une tâche un résultat attendu et un responsable. La même tâche peut aider à lever plusieurs objets, mais « tâche faite » ne ferme aucun de ces objets sans son acte de revue. Filtres « Bloque ma décision », « Bloque le prix », « Bloque la remise », « Mes contributions » ; les registres typés restent retrouvables.

**Documents (C06)** : inventaire d’abord, filtre exceptions et traitement par fichier. DCE-06 garde des couvertures distinctes et leurs dénominateurs ; ne pas mélanger lu/revu/coût couvert/réponse couverte. Visionneuse en panneau pour une preuve courte, mode large pour lecture et comparaison. Une comparaison suggère des impacts ; l’utilisateur confirme ou maintient « non interprété ».

**Prix (C08)** : couverture visible à l’ouverture ; scénarios, moyens et financement sont des vues nommées. Les tableaux importés et les pièces fournisseurs restent traçables. La comparaison C09→C08 ne duplique pas le devis et ne transforme pas un ajustement interne en prix accepté du fournisseur. Un devis révisé rend les anciens ajustements dépendants « à reconfirmer ».

**Réponse (C10)** : un plan réunit sections et pièces à obtenir, avec types d’action différents. Un éditeur de mémoire, un formulaire acheteur et une pièce à demander ne partagent pas artificiellement la même interface d’édition. Le traitement externe autorisé d’un fichier imposé conserve original, version réimportée et revue. Engagements et conformité ont leurs vues nommées ; une barre de progression rédactionnelle ne valide pas P4.

**Remise (C11)** : quatre étapes visuelles ne signifient pas quatre validations équivalentes. P4 courant précède P5 ; signatures requises contrôlées avant P5 ; dépôt humain ensuite ; preuve rapprochée après. Historique par candidate/lot/tour, sans écrasement. La copie de sauvegarde a un état et des preuves distincts. Dépôt hors autorisation peut être consigné sans régulariser le paquet.

**Entreprise (C13)** : accueil de revue puis catalogue typé. Les catégories ENT-02–10 conservent formulaires, sources et règles propres. ENT-11 reste une vue Direction strictement séparée ; ses informations n’apparaissent pas dans un compteur, aperçu, recherche ou briefing non autorisé. La fiche utilisée dans l’Affaire est une version tracée, pas un lien vivant qui réécrirait l’historique.

## 4. Revue individuelle des 104 surfaces

**Lecture** : le nom, le type initial, la priorité et les acteurs sont repris de la ligne exacte du v0.1. L’ID reste stable. « Fusion » conserve la capacité et ses contrôles. « Retrait page » supprime la destination autonome, pas son contenu. « Maintien » ne dispense pas des améliorations C00. Les missions d’origine restent applicables selon la section 2 ; la dernière colonne précise la décision UX individuelle et le risque à tester.

| ID | Surface exacte v0.1 | Type / priorité v0.1 | Acteurs v0.1 (selon habilitations) | Destination | Forme proposée / changement | Contrat conservé ou correction spécifique |
|---|---|---|---|---|---|---|
| AUTH-01 | Connexion | SCREEN / UX-Critical | Tous internes | C15 | Vue, maintien | Identifier l’organisation sans exposer de données ; retour vers le travail après connexion. |
| AUTH-02 | Activation d’invitation | FLOW / UX-Critical | Utilisateur invité | C15 | Parcours simplifié | Entreprise/invitant/rôle annoncés ; expirée, déjà acceptée et mauvais destinataire distincts. |
| AUTH-03 | Enrôlement MFA | FLOW / UX-Critical | Tous internes | C15 | Étape du parcours, fusion | Obligatoire avant accès interne ; aide et récupération accessibles, facteurs secrets jamais affichés dans l’audit. |
| AUTH-04 | Challenge MFA / Step-up | PANEL / UX-Critical | Utilisateur habilité | C00/C11/C15 | Dialogue contextuel, maintien | Nommer l’action et le paquet ; durée de validité selon règle ; MFA initial ne remplace pas P5 step-up. |
| AUTH-05 | Récupération d’accès | FLOW / UX-Critical | Utilisateur / Propriétaire | C15 | Parcours dédié, maintien | Ne pas restaurer par seul email ; anciens facteurs révoqués, preuve et dernier accès maîtrisés. |
| AUTH-06 | Récupération du dernier Propriétaire | FLOW / UX-Critical | Représentant client / support borné | C15/C14 | Parcours exceptionnel | Suspension immédiate possible avant récupération longue ; identité conservée, aucune autorité métier donnée au support. |
| AUTH-07 | Session expirée / reprise | STATE / UX-Critical | Tous internes | C00/C15 | État transversal | Masquer hors session, retrouver brouillon confirmé après reconnexion ; local et conflit distingués. |
| AUTH-08 | Accès refusé / droit insuffisant | STATE / UX-Critical | Tous | C00 | État contextualisé | Demande d’habilitation possible sans révéler le contenu ; pas de faux « aucun résultat ». |
| ONB-01 | Bienvenue / confirmation de l’organisation | FLOW / UX-Primary | Premier Propriétaire | C15 | Étape après activation | Confirmer entreprise et contexte accompagné ; ne pas créer une organisation publique autonome. |
| ONB-02 | Choix du premier chemin | SCREEN / UX-Primary | Propriétaire / Patron | C01 | Section d’entrée, déplacement | Action proposée selon rôle/invitation ; contribution directe pour expert, première Affaire pour responsable. |
| ONB-03 | Profil entreprise minimal | FLOW / UX-Primary | Propriétaire / Administratif | C13/C15 | Parcours progressif | Demander au moment utile, sans rendre facultatifs identité candidate et prérequis de porte. |
| ONB-04 | Checklist de démarrage | SCREEN / UX-Support | Propriétaire / Admin | C01 | Retrait page → section | Reprise des données manquantes ; ne pas bloquer la première valeur par un taux de profil complet. |
| GLB-01 | Shell principal / navigation | SHELL / UX-Critical | Tous internes | C00 | Structure commune, maintien | Cinq espaces, contexte lot/phase/tour, parcours clavier et droits ; pas de menus d’agents IA. |
| GLB-02 | Recherche globale | SCREEN / UX-Primary | Selon droits | C00 | Panneau + résultats en mode large | Résultats par objet autorisé ; filtrer avant extraits/compteurs ; retour à l’objet exact. |
| GLB-03 | Centre de notifications | SCREEN / UX-Primary | Tous internes | C01/C00 | Panneau et vue Événements | Événements séparés des décisions ; lu/reporté ne lève pas un blocage métier. |
| GLB-04 | Mes tâches / Mon travail | SCREEN / UX-Primary | Collaborateurs / experts / Patron | C01 | Fusion avec accueil de rôle | Une contribution référencée, pas une copie de tâche ; prochaine action et date. |
| GLB-05 | Profil / préférences personnelles | SCREEN / UX-Support | Tous internes | C00 | Panneau, simplification | Préférences ordinaires simples ; identité/session/actions sensibles renvoient aux contrôles appropriés. |
| HOME-01 | Accueil Patron | SCREEN / UX-Critical | Patron / dirigeant | C01 | Composition Décisions, refonte | Exception et arbitrage avant indicateurs ; sources/inconnus, droits Direction et autorité réelle. |
| HOME-02 | Accueil Collaborateur / Responsable d’offre | SCREEN / UX-Primary | Responsable d’offre | C01 | Composition Actions, fusion | Travaux affectés et obstacles ; pas de données Direction déduites du résumé. |
| HOME-03 | Accueil Expert | SCREEN / UX-Support | Métreur / QSE / Conducteur / Achats / DAF | C01 | Retrait page dupliquée → vue de rôle | Contribution bornée et demande précise ; possibilité de consulter le contexte autorisé. |
| OPP-01 | Radar BOAMP | SCREEN / UX-Critical | Commercial / Responsable / Patron | C02 | Vue, maintien | Provenance/fraîcheur/doublons ; résultat partiel et panne explicites. |
| OPP-02 | Recherches sauvegardées | SCREEN / UX-Support | Commercial / Responsable | C02 | Retrait page → filtres gérés | Nom, critères, collecte/alerte et désactivation retrouvables depuis le Radar. |
| OPP-03 | Fiche Opportunité | SCREEN / UX-Critical | Commercial / Responsable / Patron | C03 | Vue, maintien | Lots, effort et inconnus ; P0/P1 par habilité ; lien permanent vers Affaire créée. |
| OPP-04 | Créer une opportunité / invitation manuelle | FLOW / UX-Primary | Responsable / Commercial | C03/C02 | Parcours contextuel | Source attribuée, date inconnue, doublon ; public hors Radar ou invitation privée. |
| AFF-01 | Portefeuille des Affaires | SCREEN / UX-Primary | Selon droits | C04 | Vue, maintien | Prochaine porte et responsable ; agrégats bornés aux droits, vues filtrées reprenables. |
| AFF-02 | Synthèse Affaire | SCREEN / UX-Critical | Responsable / Patron / experts adaptés | C05 | Vue, refonte | À résoudre + prochaine action + contexte ; ne pas refaire une GED ou un dashboard de métriques. |
| AFF-03 | Chronologie / journal de l’Affaire | SCREEN / UX-Support | Selon droits | C05 | Retrait page → onglet Activité | Historique immuable, filtres, décisions et versions ; « depuis ma revue » garde accès à l’ancien. |
| DCE-01 | Import DCE | SCREEN / UX-Critical | Responsable / contributeur | C06 | Panneau/parcours intégré | Inventaire reçu confirmé ; progression et échec par fichier ; limites et reprise. |
| DCE-02 | Suivi d’ingestion / traitement | SCREEN / UX-Primary | Responsable / contributeur | C06/C00 | Retrait page → état d’inventaire | Réception, contrôle, lecture distincts ; centre détaillé accessible pour cas longs. |
| DCE-03 | Explorateur DCE | SCREEN / UX-Critical | Études / métreur / QSE / responsable | C06 | Vue, maintien | Pièces et versions ; recherche autorisée ; exceptions visibles sans changer d’application. |
| DCE-04 | Visionneuse document + source | SCREEN / UX-Critical | Selon droits | C06 | Panneau + mode large | Source exacte page/feuille/cellule ; original/dérivé ; source absente ne se remplace pas arbitrairement. |
| DCE-05 | Comparateur de versions / rectificatifs | SCREEN / UX-Critical | Responsable / experts | C06 | Mode large, maintien | Comparaison lisible, impacts confirmés/non interprétés ; validations dépendantes à rouvrir. |
| DCE-06 | Couverture documentaire | SCREEN / UX-Critical | Responsable / Patron | C06/C05 | Retrait page → section + détail | Dénominateurs séparés et accès aux manques ; pas de score unique lu/conforme/prix. |
| DCE-07 | Registre des exigences | SCREEN / UX-Critical | Responsable / experts | C05 | Vue filtrée À résoudre, fusion | Objet exigence conservé, lot/source/criticité et satisfaction ; tâche distincte. |
| DCE-08 | Registre des contradictions | SCREEN / UX-Primary | Responsable / experts / conseil | C05/C06 | Vue filtrée + panneau, fusion | Au moins deux sources, qualification motivée ; comparaison ouvre C06 ; aucun arbitrage automatique. |
| DCE-09 | Pièces manquantes / non lues | SCREEN / UX-Primary | Responsable | C06 | Retrait page → filtre Exceptions | Absence annoncée, protection, illisibilité et format non pris en charge séparés. |
| DCE-10 | Questions à l’acheteur | SCREEN / UX-Primary | Responsable / Patron selon validation | C05 | Vue nommée + panneau | Brouillon/approbation/émission déclarée ou prouvée/réponse ; pas d’envoi IA autonome. |
| DCE-11 | Visite / jalons terrain | SCREEN / UX-Primary | Responsable / conducteur | C05 | Vue nommée + mobile | Obligation, créneau, remplaçant, attestation et dispense prouvée ; lien à blocage P5. |
| DCE-12 | Registre MIRP | SCREEN / UX-Critical | Études / métreur / QSE / Patron | C05 | Vue Inconnus et hypothèses, renommage | Registre métier préservé ; impact, responsable, action et porte dépendante ; pas une liste de notes. |
| DCE-13 | Risques et facteurs de coût | SCREEN / UX-Primary | Responsable / études / métreur / Patron | C05/C08 | Vue filtrée avec lien Prix | Relier contrainte, impact et couverture ; B1/B2 visibles, données économiques protégées. |
| DEC-01 | Décision GO / NO-GO | SCREEN / UX-Critical | Patron / délégataire | C07 | Vue de décision, refonte | Brief versionné, porte réelle, conditions, avis et inconnus ; aucun GO général couvrant P5. |
| DEC-02 | Historique des décisions | SCREEN / UX-Primary | Patron / responsable selon droits | C07/C05 | Retrait page → onglet/panneau | Supersession, auteur, motif et revalidation ; accessible depuis la décision courante. |
| PRI-01 | Workspace Prix | SCREEN / UX-Critical | Métreur / DAF / Patron selon droits | C08 | Vue, maintien | Import identifié, postes et unités ; aucun moteur de métrés complet requis. |
| PRI-02 | Couverture coûts / facteurs non couverts | SCREEN / UX-Critical | Métreur / Responsable / Patron | C08 | Section d’ouverture, fusion | Besoin↔postes plusieurs-à-plusieurs ; coût inconnu visible ; absence jamais zéro. |
| PRI-03 | Capacité / charge critique | SCREEN / UX-Primary | Conducteur / Patron | C08 | Onglet Moyens, fusion | Période/ressource/conflit et hypothèse ; avis conducteur sans exposer marge Direction. |
| PRI-04 | Trésorerie / financement | SCREEN / UX-Primary | DAF / Patron | C08 | Onglet Financement protégé | Pic estimé, hypothèses et financement prouvé/non démontré ; contribution distincte. |
| PRI-05 | Scénarios économiques / hypothèses | SCREEN / UX-Critical | DAF / Patron | C08 | Onglet Scénarios, fusion | Contribution/taux sur vente, scénario défavorable, hypothèses ; pas de total exact trompeur. |
| PAR-01 | Partenaires de l’Affaire | SCREEN / UX-Primary | Responsable / Achats / Patron | C09 | Vue contextuelle, maintien | Consulté/reçu/retenu/engagé/accepté selon type ; pièce et entité responsables. |
| PAR-02 | Comparatif d’offres partenaires | SCREEN / UX-Primary | Achats / Métreur / Patron | C08/C09 | Mode Comparer les offres, déplacement | Périmètre constant, exclusions/transport/validité ; ajustements internes visibles et revus à la révision. |
| COL-01 | Tâches de l’Affaire | SCREEN / UX-Primary | Équipe Affaire | C05 | Vue Mes actions, fusion | Affecter n’est pas déléguer ; tâche achevée ne lève pas une obligation sans preuve. |
| COL-02 | Commentaires / mentions / fil d’activité | PANEL / UX-Support | Équipe autorisée | C00 | Panneau d’objet, maintien | Commentaire distinct du fait validé ; mentions bornées, aucun contexte secret dans notifications. |
| RES-01 | Plan de réponse | SCREEN / UX-Critical | Responsable / équipe | C10 | Vue d’ouverture, maintien | Type de livrable, responsable, critère, phase/lot/tour ; lien vers production réelle. |
| RES-02 | Checklist des livrables | SCREEN / UX-Critical | Responsable / administratif | C10 | Retrait page → plan unifié | Pièce obligatoire, modèle et signature restent visibles ; progression ≠ conformité. |
| RES-03 | Atelier de réponse / mémoire technique | SCREEN / UX-Critical | Responsable / rédacteurs / experts | C10 | Mode large, maintien | Écrire avec sources et mémoire autorisée ; IA proposée ≠ texte validé ; sauvegarde/reprise. |
| RES-04 | Atelier cadres acheteur / formulaires | SCREEN / UX-Primary | Administratif / Responsable | C10 | Mode de travail spécialisé | Original/copie, champs/formules/zones protégées ; voie externe si édition non qualifiée. |
| RES-05 | Documents et preuves externes à obtenir | SCREEN / UX-Primary | Administratif / Responsable | C10 | Retrait page → filtre du plan | Demande/reçu/vérifié/expiré/non applicable ; réception seule n’autorise pas le réemploi. |
| RES-06 | Registre des engagements | SCREEN / UX-Critical | Responsable / Patron / experts | C10/C12 | Onglet + liens Passation | Texte exact, origine, validation, moyens et futur responsable ; pas de promesse créée par génération. |
| RES-07 | Revue de conformité de la réponse | SCREEN / UX-Critical | Responsable / Patron | C10 | Mode Revoir, maintien | B0/B1/B2, critères et revalidation avant P4 ; ne pas tout transférer au dernier contrôle P5. |
| SUB-01 | Coffre de remise | SCREEN / UX-Critical | Responsable / Patron | C11 | Espace Remise, renommage visible | Candidate exacte avec manifeste ; objet Coffre conservé, distinct des brouillons. |
| SUB-02 | Contrôle pré-remise | SCREEN / UX-Critical | Responsable / Patron | C11 | Étape Contrôler, fusion | B0/B1 levés, B2 traités ; version/canal/destinataire/heure ; pas de simple liste cochable arbitrairement. |
| SUB-03 | Signataires / statut de signature | SCREEN / UX-Primary | Administratif / Patron / signataire | C11 | Section contrôles + détail | Par pièce/phase, signataire et preuve ; réimport signé avant P5 ; image ≠ signature valide. |
| SUB-04 | Autorisation P5 | FLOW / UX-Critical | Patron / délégataire P5 | C11 | Parcours sensible, maintien | Paquet exact, droit, step-up et confirmation séparée ; aucun bouton « signer et déposer ». |
| SUB-05 | Export / instructions de dépôt | SCREEN / UX-Critical | Opérateur de dépôt | C11 | Étape Déposer à l’extérieur | Export de la version autorisée, consignes ; copie de sauvegarde séparée ; geste humain V1. |
| SUB-06 | Preuve de remise / reçu | SCREEN / UX-Critical | Opérateur / Responsable / Patron | C11 | Étape Rapprocher le reçu | Déclaration, réception et couverture du contenu distinctes ; incohérence/partiel visibles. |
| SUB-07 | Historique des remises / redépôts | SCREEN / UX-Primary | Responsable / Patron | C11 | Onglet + action nouvelle candidate | Anciennes versions/reçus préservés ; redépôt complet avec nouvelles validations applicables. |
| OUT-01 | Clarification / négociation / nouvelle offre | SCREEN / UX-Primary | Responsable / Patron | C12/C10 | Parcours de modification | P6 selon impact ; retour ciblé P3/P4/P5 ; prolongation de validité = décision, pas édition anodine. |
| OUT-02 | Résultat de l’Affaire | SCREEN / UX-Critical | Responsable / Patron | C12 | Onglet par lot, fusion | Perdu/annoncé/notifié/sans suite ; preuve externe, pas d’Affaire entièrement gagnée par défaut. |
| OUT-03 | Passation | SCREEN / UX-Critical | Patron / Responsable / Conducteur | C12 | Mode de travail, maintien | Engagements, documents, risques, réserves et accusé ; P7 par habilité, pas ordre de service. |
| OUT-04 | REX / clôture de l’Affaire | SCREEN / UX-Primary | Responsable / Patron | C12 | Parcours/panneau, fusion | Motif connu/inconnu, estimé/réalisé ; revue avant mémoire ; pas de suppression des traces. |
| ENT-01 | Accueil Mémoire Entreprise | SCREEN / UX-Critical | Selon droits | C13 | Vue À tenir à jour, renommage | Revues et usages prioritaires ; expirations obligatoires restent visibles ; pas de score de GED. |
| ENT-02 | Identité / établissements | SCREEN / UX-Primary | Propriétaire / Administratif | C13 | Catégorie avec fiche | Entité, SIREN/SIRET, source et applicabilité ; aucune confusion entre établissement et société candidate. |
| ENT-03 | Pouvoirs / signataires | SCREEN / UX-Critical | Propriétaire / Patron / Administratif | C13 | Catégorie protégée | Personne, portée, durée et preuve ; pouvoir de signature distinct du compte et de P5. |
| ENT-04 | Documents administratifs / preuves | SCREEN / UX-Critical | Administratif / QSE | C13 | Catégorie avec fiche | Validité, activité, période, source et prochaine revue ; valide ≠ applicable ici. |
| ENT-05 | Personnel / compétences / habilitations | SCREEN / UX-Primary | Administratif / QSE / responsable autorisé | C13 | Catégorie restreinte | Données minimisées ; compétence/habilitation/disponibilité distinguées ; copie partageable revue. |
| ENT-06 | Moyens matériels | SCREEN / UX-Primary | Responsable / Conducteur | C13 | Catégorie avec fiche | Détenu/loué/envisagé et disponible ; pas d’affectation automatique aux offres. |
| ENT-07 | Références / réalisations | SCREEN / UX-Critical | Commercial / Responsable / Patron | C13 | Catégorie avec fiche | Réalisé réellement, rôle et part, preuve, permission de publication ; réemploi contextuel. |
| ENT-08 | Partenaires / fournisseurs / sous-traitants | SCREEN / UX-Primary | Achats / Administratif / Patron | C13 | Catégorie, maintien du lien C09 | Fiche générale distincte de l’engagement dans une Affaire ; preuves et état propres. |
| ENT-09 | Méthodes / QSE / contenus réutilisables | SCREEN / UX-Primary | Responsables de contenu | C13 | Catégorie avec revue | Version/propriétaire/portée ; suggestion IA ne publie pas une méthode validée. |
| ENT-10 | Modèles / gabarits internes | SCREEN / UX-Support | Responsables / Admin produit client | C13 | Catégorie, simplification | Modèle autorisé/versionné ; cadre acheteur imposé clairement distinct. |
| ENT-11 | Données économiques Direction | SCREEN / UX-Critical | Patron / DAF uniquement | C13 | Vue protégée séparée | Patron/DAF habilités uniquement ; historique/export bornés ; rien dans compteurs ou aperçus communs. |
| ENT-12 | File de revue / expirations | SCREEN / UX-Primary | Propriétaires de contenu | C13 | Retrait page → accueil + filtre | Qui revoit quoi, échéance et Affaires autorisées affectées ; pas d’actualisation rétroactive des snapshots. |
| SHR-01 | Créer un partage externe | FLOW / UX-Critical | Utilisateur autorisé | C00/C05/C09/C10 | Parcours contextuel + N03 | Objet autorisé, paquet, destinataire, finalité, durée ; étape sensible selon contenu ; confirmation explicite. |
| SHR-02 | Gérer / révoquer les partages | SCREEN / UX-Primary | Utilisateur autorisé / sécurité | C05/C14 | Vue Partages + panneau | Lien actif/expiré/révoqué, accès téléchargés ; couper accès futur sans prétendre rappeler fichiers. |
| SHR-03 | Portail destinataire externe | SCREEN / UX-Critical | Tiers | C16 | Vue isolée, maintien | Identité et paquet seulement ; pas d’en-tête global Affaire ni d’accès via liens connexes. |
| SHR-04 | Dépôt tiers externe | SCREEN / UX-Primary | Tiers | C16 | Section/parcours | Reçu technique, progression et contrôles ; pièce reçue non fiable jusqu’à vérification. |
| ADM-01 | Accueil Administration / Gouvernance | SCREEN / UX-Primary | Propriétaire / Admin | C14 | Retrait dashboard → sections/actions | Actions rares et urgences d’accès ; aucun résumé métier sensible automatique. |
| ADM-02 | Utilisateurs | SCREEN / UX-Critical | Propriétaire / Admin | C14 | Onglet Accès, maintien | Invitation/suspension/réactivation ; effets immédiats de révocation et éléments orphelins. |
| ADM-03 | Fiche utilisateur / accès | SCREEN / UX-Critical | Propriétaire / Admin | C14 | Panneau + mode large | Rôles/périmètres/sessions, approbation ; aucune lecture métier induite par l’inspection des accès. |
| ADM-04 | Rôles / délégations | SCREEN / UX-Critical | Propriétaire / autorité compétente | C14 | Onglet Délégations, maintien | Porte, lot, catégorie, durée/plafond ; délégation non transmissible ; autorité qui approuve visible. |
| ADM-05 | Sécurité / MFA / sessions | SCREEN / UX-Critical | Propriétaire / Admin sécurité | C14 | Onglet Sécurité, fusion | Politiques, statut et révocation sans facteur secret ; renvoi récupération AUTH si nécessaire. |
| ADM-06 | Journal d’audit | SCREEN / UX-Critical | Propriétaire / sécurité / auditeur autorisé | C14 | Vue détaillée dédiée | Filtres, preuve et export autorisé ; ne pas fondre le journal d’intégrité dans les commentaires. |
| ADM-07 | Notifications / préférences organisation | SCREEN / UX-Support | Admin / Propriétaire | C14 | Section Service | Canaux/échec/escalade ; préférence ne supprime pas le blocage produit critique. |
| ADM-08 | Gouvernance des données | SCREEN / UX-Critical | Propriétaire / responsable données | C14 | Onglet Données, maintien | Catégories, finalités, calendrier, droits et points W ; pas de délai juridique inventé. |
| ADM-09 | Accès support exceptionnel | SCREEN / UX-Critical | Autorité client / support | C14 | Parcours et vue de session | Autorité correspondante aux données, nominatif, motif/durée par défaut 1 h ; expiration/révocation. |
| ADM-10 | Export / réversibilité / fermeture | FLOW / UX-Critical | Propriétaire + autorités données | C14 | Parcours sensible, maintien | Export vérifié, autorités données, gel/litige/conservation ; arrêt si export interrompu. |
| ADM-11 | Usage IA / coûts / quotas | SCREEN / UX-Support | Propriétaire / Admin | C14 | Section Service + détail | Usage/limites et dépense inhabituelle ; seuils/actions critiques testés, aucune consommation illimitée implicite. |
| SYS-01 | Centre de traitements | SCREEN / UX-Primary | Selon droits | C00/C06 | Retrait page quotidienne → panneau + détail | Traitement au lieu de travail ; vue globale autorisée pour reprise ; annulation sûre et état réel. |
| SYS-02 | Mode dégradé / IA indisponible | STATE / UX-Critical | Tous | C00 | État transversal, maintien | Décrire fonctions affectées/utilisables ; alternative manuelle critique, pas page bloquant tout par défaut. |
| SYS-03 | Incident / reprise de service | SCREEN / UX-Primary | Propriétaire / responsables | C00/C14 | Vue incident contextuelle | Périmètre, dernier état confirmé, prochaine information ; objectifs RPO/RTO non annoncés comme résultats. |
| MOB-01 | Accueil mobile terrain | RESPONSIVE / UX-Primary | Conducteur / Responsable | C01 | Variante mobile, fusion | Prochaine action/visite/alerte et sync ; même identité, pas application parallèle. |
| MOB-02 | Affaire mobile ciblée | RESPONSIVE / UX-Primary | Utilisateur terrain | C05/C06 | Variante ciblée | Échéances, pièces effectivement disponibles, tâches autorisées ; pas poste de prix complet. |
| MOB-03 | Visite mobile | RESPONSIVE / UX-Primary | Conducteur / visiteur autorisé | C05 | Variante de DCE-11 | Checklist, présence/preuve, local/synchronisé ; obligation de visite non masquée par capture faite. |
| MOB-04 | Capture note / photo / justificatif | RESPONSIVE / UX-Primary | Utilisateur terrain | C05/C06 | Action mobile et état N05 | Note/photo/preuve locale, attente, échec, confirmation ; ne pas confondre capture et partage à l’équipe. |
| MOB-05 | Tâches mobile | RESPONSIVE / UX-Primary | Utilisateur terrain | C01/C05 | Variante de Mon travail | Mise à jour bornée et reprise ; hors ligne ne valide aucune porte sensible. |

## 5. Ajouts explicites et priorité des variantes

| ID ajouté | Surface / rattachement | Acteurs et données | Action / preuve attendue / recette |
|---|---|---|---|
| **N01** | Conflit de contributions — C00, notamment C05/C07/C10 | Deux auteurs autorisés, version confirmée et contribution concurrente | Comparer et conserver les deux ; proposer résolution, revoir validations touchées. Critique : G16/G51 ; jamais « dernier clic gagne » silencieux. |
| **N02** | Issue d’opération inconnue — C00/C11/C14 | Utilisateur de l’action ; dernier état confirmé, identifiant lisible de tentative | Vérifier l’état avant renvoi ; statut indéterminé maintenu tant que non prouvé. Critique : interrompre autorisation/export/upload ; dépôt externe vérifié par opérateur/preuve, pas par un connecteur imaginaire. |
| **N03** | Aperçu destinataire — SHR-01, C00/C16 | Émetteur habilité ; paquet autorisé, destinataire, durée, droits, données exclues | Prévisualiser ce qui sera accessible et déclarer les limites de simulation ; confirmer ou corriger. Critique : G24/G44/G52. Aucun aperçu avec les droits supérieurs d’un Admin. |
| **N04** | Relève nominative — C05/C14 | Responsable sortant/entrant et autorité habilitée ; tâches, inconnus, validations et échéances | Réaffecter le travail, obtenir prise en charge ; délégations séparées ; accès compromis coupé sans attendre. Critique sur droits, principal sur coordination : G13/G14/G15. |
| **N05** | Disponibilité terrain — C01/C05/C06 mobile | Utilisateur autorisé ; documents disponibles et captures locales/en attente/confirmées | Expliquer disponibilité réelle ; confirmer synchronisation ; avertir perte potentielle locale. Critique : G27 et révocation avant sync. Pas de promesse de dossier complet hors connexion. |

Ces cinq contrats individualisent des besoins déjà évoqués dans le v0.1/v0.4. Ils complètent l’inventaire testable sans étendre les pouvoirs ni le périmètre commercial. N02 détaille particulièrement une interaction insuffisamment dessinée : une opération peut avoir réussi côté service sans que l’utilisateur en ait reçu la confirmation.

**Variantes rehaussées, sans déclasser le reste** : GLB-05 pour toute modification sensible ou reprise de session ; ADM-07 pour un canal critique échoué ; ADM-11 pour quota/limite bloquante et reprise ; MOB-04/05 pour perte de capture, révocation ou conflit ; HOME-03 dès qu’un expert doit fournir une validation déterminante. Leur priorité de catalogue d’origine reste lisible, mais leur scénario critique ne peut être traité comme simple décoration Support.

## 6. Parcours : couverture conservée et complément Entreprise

Le détail des actions, arrêts et réussites figure dans la section G du [rapport](01_CONTRE_REVUE_UX.md). La matrice ci-dessous fixe les rattachements de cette version.

| Parcours | Espaces / contrats | Point de contrôle déterminant |
|---|---|---|
| PUX-01 | C15 → C01/C13 → C03/C05 | Identité/MFA puis première valeur ; configuration progressive, création accompagnée |
| PUX-02 | C02 → C03 → C05 | P0/P1, lots, provenance et liaison sans doublon |
| PUX-03 | C03 → C06/C05 | Invitation privée/manuelle, phase et inconnus explicites |
| PUX-04 | C06 → C05 | Inventaire, lecture partielle, première exception sourcée |
| PUX-05 | C06 → C05/C07/C08/C10/C11 | Rectificatif et chaîne d’invalidation ciblée |
| PUX-06 | C05 → C07 avec C08 | P2/P3 distinctes, conditions et autorité |
| PUX-07 | C08 avec C09 → C07 | Couverture, hypothèses, capacité/cash et P3 |
| PUX-08 | C10 avec C13 → C07/C11 | Revue/engagements/P4, modèles et preuves |
| PUX-09 | C11 avec C15 | P5/step-up, dépôt humain et reçu limité à sa preuve |
| PUX-10 | C11 → C10/C07 → C11 | Nouvelle candidate complète et nouvelle preuve |
| PUX-11 | C12 avec C10 | Résultat par lot, engagement, réserve et P7 |
| PUX-12 | C12 → C13 | Motif connu/inconnu, enseignement revu |
| PUX-13 | C05/C09/C10 → N03 → C16 | Partage ciblé, upload contrôlé, révocation future |
| PUX-14 | C14 → N04/C05 | Suspension avant relève, historique et pouvoirs distincts |
| PUX-15 | C14/C15 | Dernier Propriétaire compromis, suspension et récupération prouvée |
| PUX-16 | C14/N02 | Export vérifié, gel/litige/conservation et fermeture |
| PUX-17 | C00 et espace concerné/N02 | Panne IA, manuel, reprise sans double publication |
| PUX-18 | C01/C05/C06/N05 | Terrain local/en attente/confirmé |
| **PUX-19 — ajouté** | C13 → C10/C05 → C13 | Entretien → revue → applicabilité Affaire → snapshot → expiration/actualisation |

## 7. Traçabilité des contrats E/S et G01–G52

| Contrat propriétaire | Espaces de réalisation proposés |
|---|---|
| E01 Accueil Patron | C01 et C00 |
| E02 Radar | C02 |
| E03 Opportunité | C03 |
| E04 Import DCE | C06 |
| E05 Explorateur DCE | C06 avec C05 |
| E06 Synthèse Affaire | C05 |
| E07 MIRP | C05, vue Inconnus et hypothèses |
| E08 GO/NO-GO | C07 |
| E09 Prix | C08 |
| E10 Réponse | C10 |
| E11 Coffre/remise | C11 |
| E12 Passation | C12 |
| S01 Entreprise | C13 |
| S02 Accès/gouvernance | C14/C15/C16 et C00 |

Les recettes ci-dessous sont **rattachées, non exécutées**. Leur texte attendu reste celui du v0.4. Pour G18, l’annotation historique « A02 non encore acceptée » est obsolète face à A02/OWN-01 amendée ; le test applique la suspension autorisée, sans demander un nouvel arbitrage.

| Recette | Espace / état à matérialiser | Invariant à vérifier |
|---|---|---|
| G01 | C06/C05/C08 | Plan annoncé absent, couverture dépendante non prouvée |
| G02 | C06/C07/C11 | Rectificatif après P5, ancienne autorisation non valable pour nouveau paquet |
| G03 | C05/C06 | RC/CCAP contradictoires, deux sources et résolution motivée |
| G04 | C08 | Besoin levage sans poste, coût non couvert |
| G05 | C06/C10/C11 | XLS imposé conservé, édition non qualifiée signalée |
| G06 | C06/C05 | Page illisible, échéance non inventée |
| G07 | C06 | Fichier protégé, pas de contournement |
| G08 | C06/C00 | Archive hors limite, inventaire partiel et reprise |
| G09 | C06/C14 | Contenu dangereux isolé sans exécution ni envoi IA |
| G10 | C05/C11 | Visite exigée sans preuve, blocage applicable |
| G11 | C03/C05 | Conflit de dates, pas de report automatique |
| G12 | C09/C08/C07 | Devis expiré, hypothèse et P3 réexaminées |
| G13 | C05/C14/N04 | Releveur voit travail attendu sans pouvoir automatique |
| G14 | C14/C00/N04 | Révocation immédiate, partage futur et publication refusés |
| G15 | C07/C11/C14 | P5 refusée sans délégation, préparation permise selon droits |
| G16 | C05/C10/N01 | Deux contributions conservées, validation divergente bloquée |
| G17 | C14/C13 | Auto-élévation Admin refusée sans autorité compétente |
| G18 | C14/C15 | Suspension du dernier Propriétaire compromis possible ; récupération encadrée |
| G19 | C15 | Récupération MFA non fondée sur seul email |
| G20 | C10/C15/N01 | Reconnexion, brouillon confirmé et local distingués |
| G21 | C09/C10/C11/C13 | Mandat/signature par membre du groupement |
| G22 | C09/C10 | Partenaire consulté ne devient pas engagé par génération |
| G23 | C12/C06/C07 | Commande privée différente, accord non établi et P6 |
| G24 | N03/C16/C14 | Révocation coupe le futur, fichiers téléchargés non rappelés |
| G25 | C00/C11/N02 | Panne IA, contrôles humains et export conservés selon état réel |
| G26 | C02 | Panne BOAMP, fraîcheur explicite et saisie manuelle |
| G27 | C05/N05 | Capture locale non annoncée partagée |
| G28 | C00/C11 | Heure source Paris et conversion Maroc représentent le même instant |
| G29 | C06/C00 | Instruction hostile dans DCE n’envoie aucune marge ni ne change les droits |
| G30 | C11 | Paquet modifié non exporté comme ancien paquet autorisé |
| G31 | C11/N02 | Transmission déclarée sans réception prouvée |
| G32 | C11 | Reçu mauvais lot/hors délai signalé incohérent |
| G33 | C11 | Pli reçu, contenu non intégralement rapprochable |
| G34 | C11 | Redépôt complet, nouvelle candidate et reçu |
| G35 | C11 | Copie de sauvegarde distincte, pas remplacement automatique |
| G36 | C10/C12 | Engagement promis non omis de la passation |
| G37 | C03/C10/C11 | Candidature seule, P3 non applicable avec motif |
| G38 | C12 | Un seul lot gagné transmis, pas de fusion de prix/engagements |
| G39 | C08 | Vente 120/coûts 100 : 20 et 16,67 %, puis incomplet si coût inconnu |
| G40 | C08/C06 | Total Excel non recalculé/ligne masquée à vérifier |
| G41 | C08 | Conflit de ressource/période, capacité non démontrée |
| G42 | C08/C07 | Financement manquant visible malgré marge estimée positive |
| G43 | C13/C10 | Assurance valide hors activité non applicable |
| G44 | C13/C10/N03 | CV sensible, version minimisée et revue avant partage |
| G45 | C14/C13 | Export Direction requiert autorité correspondante |
| G46 | C14 | Support après expiration refusé |
| G47 | C14/N02 | Export interrompu/litige bloque fermeture concernée |
| G48 | C14/C00 | Restauration vérifie révocations/purge avant réouverture |
| G49 | C00/C07/C11 | Preuve et autorisation réalisables au clavier |
| G50 | C05/C10/C13 | Critère environnemental sans réponse pertinente signalé |
| G51 | C07/C11/N01 | Condition échue ou décisions concurrentes bloquent validation |
| G52 | C00/C01/C08/C13/C16 | Aucune divulgation de marge directe, déduite ou via ancienne sortie révoquée |

## 8. Ordre de prototypage corrigé : parcours complets, puis couverture totale

La séquence ci-dessous remplace les vagues strictement par domaine. Elle n’autorise pas une livraison limitée aux premières vagues. Les sous-scénarios critiques apparaissent dès que la fonction dont ils dépendent est dessinée.

| Vague | Travail et surfaces | Sortie attendue |
|---|---|---|
| **V0 — Contrats C1** | C00, navigation, À résoudre, Remise, confidentialité, N01/N02 | Décisions de structure explicites ; pas de maquette ambiguë de GO/P5/reçu |
| **V1 — Première valeur et travail réel** | C15 → C01 → C03/C06/C05 ; premier réemploi C13 ; identité/permissions et panne | PUX-01/03/04, versions desktop/mobile utiles, refus et reprise inclus |
| **V2 — Comprendre et décider** | C02/C04/C05/C06/C07/C08/C09 ; rectificatif et rôles multiples | PUX-02/05/06/07 ; comparer preuves et hypothèses sans divulgation |
| **V3 — Produire et remettre** | C10/C11, signature externe, P5, tiers C16/N03 | PUX-08/09/10/13, candidature seule, reçu partiel et dépôt hors autorisation tracé |
| **V4 — Transmettre et entretenir** | C12/C13, groupement et commande privée ; N04/N05 | PUX-11/12/18/19, passation réservée et entretien lié aux affaires |
| **V5 — Gouvernance complète et fermeture** | C14/C15, incidents, perte d’accès, export ; variantes restantes des 104 IDs | PUX-14/15/16/17 ; aucune surface Support ou secondaire omise |
| **V6 — Recette transversale complète** | Tous IDs, E/S, G01–G52, 19 PUX et variantes | Preuves de validation propriétaire, défauts corrigés ; aucun UX Freeze automatique |

Chaque surface garde le niveau minimal du v0.1 : critique détaillée et interactive lorsque nécessaire ; principale complète ; support fonctionnelle. Prototyper un système de composants partagé évite de redessiner cent quatre structures, mais ne remplace pas la validation des combinaisons de rôles/états.

## 9. L — Changelog motivé

| Changement | Avant | Après | Pourquoi / valeur attendue | Risque et garde-fou |
|---|---|---|---|---|
| CH01 — Destinations | Inventaire de 104 surfaces, dont 83 SCREEN | 16 espaces canoniques et rattachement individuel | Réduire l’apprentissage et les changements de contexte | Ne pas annoncer 16 prototypes suffisants ; maintenir toutes les recettes |
| CH02 — Accueil | HOME-01/02/03 et GLB-04 séparés | Accueil commun avec compositions par responsabilités | Patron par exceptions ; expert directement sur contribution | Ne jamais confondre vue et rôle/droit |
| CH03 — À résoudre | Registres DCE et tâches dispersés | Vues coordonnées dans C05 | Une action à partir d’un problème sourcé | Garder objets/états typés ; tâche ≠ exigence validée |
| CH04 — Documents | Import/suivi/manquants/couverture autonomes | Inventaire, panneaux, filtres et mode large dans C06 | Travailler malgré réception ou lecture partielle | Ne pas masquer les manques critiques ni les dénominateurs |
| CH05 — Prix | Cinq espaces PRI | Couverture et vues scénarios/moyens/financement | Montrer les besoins non financés/non chiffrés sans double saisie | Confidentialité par champ et inconnus explicites |
| CH06 — Partenaires | Comparatif à part du Prix | Contexte commun C08/C09, source conservée | Comparer le périmètre réel et revoir ajustements | Aucun ajustement interne présenté comme offre fournisseur |
| CH07 — Réponse | Plan/checklist/documents externes séparés | Plan unique et modes de production spécialisés | Réduire les allers-retours du responsable | Pas d’éditeur universel forcé ; validation de contenu distincte |
| CH08 — Remise | SUB-01–07 présentés comme surfaces successives | Quatre étapes visuelles, candidate persistante | Comprendre exactement ce qui est autorisé et prouvé | Ne pas fusionner P5/signature/export/dépôt/reçu |
| CH09 — Entreprise | Douze pages potentielles | Accueil de revue, catégories typées, Direction isolée | Donner un motif concret d’entretien et de réemploi | Validité ≠ applicabilité ; snapshot conservé |
| CH10 — Historiques | AFF-03/DEC-02/SUB-07 dispersés | Historique depuis l’objet et activité d’Affaire | Revenir à la version qui explique une décision | Accès permanent, immutabilité et filtres autorisés |
| CH11 — Après remise | Résultat/passation/REX séparés | C12 par lot avec étapes et réserves | Transmettre ce qui a réellement été vendu | Pas de lot perdu transmis ni P7 assimilée à un ordre de service |
| CH12 — Administration | Dashboard et écrans nombreux | C14 en vues métier d’administration | Trouver les rares actions sans exposition de données inutiles | Audit/fermeture gardent leur profondeur ; aucun pouvoir métier automatique |
| CH13 — Système | Centre de traitement quotidien autonome | États au lieu de travail, détail accessible | Comprendre l’impact et poursuivre le travail possible | Une simple notification ne suffit pas pour l’incident persistant |
| CH14 — Onboarding | Parcours ONB successifs avant accueil | Identité forte puis configuration au besoin | Première valeur sans dossier administratif complet | Ne pas différer les prérequis réels des portes |
| CH15 — Mobile | Cinq surfaces pouvant former une application parallèle | Variantes C01/C05/C06 et disponibilité N05 | Même repères, compagnon utile en déplacement | Pas de prix complet ni autorisation sensible hors réseau |
| CH16 — Contrats manquants | Conflit/issue inconnue/aperçu/relève/disponibilité implicites | N01–N05 individualisés | Reprises et frontières de confiance testables | Aucun nouveau module ni promesse technique implicite |
| CH17 — Parcours Entreprise | Pas de PUX dédié | PUX-19 entretien/réemploi/applicabilité | Valider le second pilier comme parcours complet | Pas de mise à jour rétroactive des preuves des offres |
| CH18 — Prototypage | Vagues surtout par domaine, erreurs/gouvernance tardives | Parcours complets incluant états critiques puis couverture totale | Détecter tôt les ambiguïtés d’autorité et de preuve | Ne pas arrêter la validation aux premiers parcours |
| CH19 — Terminologie | MIRP/ingestion/preflight/P5 en intitulé principal | Inconnus et hypothèses/Réception et lecture/Contrôles/Autoriser ce paquet | Compréhension métier sans formation au catalogue | Conserver codes/règles dans le détail d’audit |
| CH20 — IA contextuelle | Doctrine générale | Brief/suggestion/action/revue avec source et ancienneté | Aider dans le travail, actualiser uniquement ce qui est utile | Coût et confiance non mesurés ; pas de décision ni envoi autonome |

## 10. Conditions d’adoption

Avant prototype : arbitrer les huit C1 du rapport avec les propositions présentes. Avant UX Freeze : matérialiser toutes les surfaces et variantes applicables, exécuter les parcours et G01–G52, vérifier l’absence de fuite/pouvoir induit, corriger les défauts et recueillir la validation propriétaire. Les points W juridiques et de service restent ceux du v0.4 ; ce catalogue n’en annonce aucune clôture.

La validation documentaire de ce livrable vérifie la couverture des identifiants, les rattachements et l’intégrité des originaux. **Elle n’est ni une recette de code, ni un test d’ergonomie, ni une homologation de sécurité.**
