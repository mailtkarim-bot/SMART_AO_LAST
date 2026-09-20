# SMART AO — V0-01 Shell + Catalogue exact des prototypes V0
## OWNER EXECUTION SPEC v0.1

**Date : 13 septembre 2026**  
**Statut : CONTRAT PROPRIÉTAIRE DE PRODUCTION DES PROTOTYPES V0 — V0-01 prêt à maquettage ; V0-02 à V0-16 catalogués et ordonnés.**  
**Autorités supérieures :**
1. `SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_CONSOLIDATED_v0.4.md`
2. `SMART_AO_Catalogue_Ecrans_Parcours_Produit_OWNER_CONSOLIDATED_v0.3.md`
3. `SMART_AO_Prototype_UX_V0_Fondations_OWNER_CONSOLIDATED_v0.2.md`

**Source de recherche absorbée :** `SMART_AO_Prototype_UX_V0_Fondations_WORK_PROPOSAL_v0.1.md`.

---

## 0. Objet du document

Le présent document fait deux choses et uniquement deux choses :

1. il transforme **V0-01 — Shell desktop/laptop** en contrat de maquettage exploitable et validable ;
2. il fixe le **catalogue exact des unités de prototype V0-01 à V0-16**, afin que SMART AO soit matérialisé sans improvisation écran par écran.

Il ne remplace pas les fondations UX v0.2. Il en devient la **spécification d’exécution V0**.

Le mot « prototype » désigne ici une matérialisation visuelle/interactive jetable destinée à valider le produit. Il ne préjuge ni du framework frontend, ni du backend, ni de la structure des composants de production.

### 0.1. Clarification sur le premier écran déjà généré

La maquette visuelle déjà produite et jugée convaincante est conservée comme :

`SMART_AO_CONCEPT_VISUEL_COMPOSITE_01`

Elle sert de **North Star visuelle** pour le ton général : produit B2B premium, lisible, professionnel, BTP, IA intégrée sans domination du chat.

Elle n'est **pas** V0-01 validé. Elle mélange déjà plusieurs contrats : Shell, Vue d'ensemble Affaire, Accueil/Minute Patron, C05, IA contextuelle et états métier. Elle ne peut donc pas servir seule de recette V0-01.

Règle : **on conserve son langage visuel comme hypothèse forte, puis on valide chaque couche séparément.**

---

# PARTIE I — CONTRAT FORMEL V0-01

## 1. Finalité de V0-01

V0-01 doit prouver que SMART AO possède une structure stable dans laquelle tous les futurs écrans peuvent vivre sans perdre :

- l'organisation active ;
- l'Affaire ;
- l'entreprise candidate ;
- le lot ;
- la phase ;
- le tour ;
- l'échéance acheteur ;
- la prochaine porte métier pertinente ;
- les droits de l'utilisateur ;
- le retour au contexte après une interruption.

V0-01 ne cherche pas encore à valider le métier détaillé de C05, C11 ou l'IA. Ces contenus peuvent être utilisés comme **données réalistes de démonstration**, mais le sujet testé est le Shell.

### 1.1. Question de validation

> Un utilisateur peut-il entrer n'importe où dans SMART AO, comprendre immédiatement où il se trouve et ce qu'il peut faire, naviguer dans une Affaire puis revenir à son travail sans perdre son contexte ?

---

## 2. Anatomie normative du Shell

Le Shell comporte quatre couches stables.

### 2.1. Couche S1 — Rail global

Le rail global porte les destinations de responsabilité :

- **Accueil**
- **Opportunités**
- **Affaires**
- **Entreprise**
- **Administration** — séparée visuellement et affichée uniquement selon droits

Règles :

- l'espace actif est identifiable par texte + position + accent visuel ;
- le rail n'affiche aucun menu d'« agents IA » ;
- sur laptop étroit, il peut se réduire mais reste explicite au focus/survol ;
- réduire le rail ne modifie jamais les droits ni le contenu ;
- les compteurs éventuels sont calculés après filtrage des droits ;
- l'identité SMART AO reste visible sans consommer une largeur excessive.

### 2.2. Couche S2 — Barre supérieure

La barre supérieure contient :

- organisation active ;
- recherche globale ;
- traitements ;
- notifications/alertes ;
- aide contextuelle ;
- identité utilisateur / rôle courant informatif.

Règles :

- changer d'organisation reconstruit immédiatement les droits et la portée de recherche ;
- la recherche ne montre jamais un extrait interdit ;
- une alerte n'est pas confondue avec un blocage métier ;
- le rôle affiché n'est pas un sélecteur permettant de s'attribuer un pouvoir ;
- l'aide s'ouvre sur le contexte courant lorsque possible.

### 2.3. Couche S3 — Bandeau de contexte Affaire

Présent uniquement à l'intérieur d'une Affaire.

Informations minimales toujours visibles :

- nom court de l'Affaire ;
- entreprise candidate ;
- lot ;
- phase ;
- tour ;
- échéance acheteur et fuseau source ;
- état de porte utile à la décision courante.

Règles :

- le bandeau reste visible pendant le travail ;
- une valeur inconnue est affichée `Non déterminé`, jamais supprimée ;
- changer lot/phase/tour exige un avertissement si un brouillon local ou une action sensible est en cours ;
- le changement de contexte ne doit pas recycler silencieusement le contenu précédent ;
- un lien direct reconstruit ce contexte avant d'afficher le contenu ;
- l'échéance acheteur conserve son fuseau source ; une conversion locale est secondaire.

### 2.4. Couche S4 — Navigation Affaire + zone de travail

Destinations quotidiennes :

- **Vue d'ensemble**
- **Documents**
- **Prix**
- **Réponse**
- **Remise**

Destinations contextuelles :

- Décision
- Partenaires
- Résultat / Passation

Elles sont accessibles depuis les objets qui les appellent et via `Plus dans cette Affaire` ; elles ne deviennent pas des onglets permanents.

La zone de travail suit l'ordre :

1. titre / portée ;
2. message d'état majeur si applicable ;
3. action principale ;
4. filtres ;
5. contenu ;
6. panneau de détail éventuel.

Un seul panneau latéral peut être ouvert. Un travail long bascule en **mode large** au lieu d'empiler des panneaux.

---

## 3. Géométrie et densité de référence

### 3.1. Viewports V0-01

Deux viewports font foi pour V0-01 :

- **Desktop de confort : 1584 × 990 environ** — utilisé pour la North Star et les revues de composition.
- **Laptop de référence : 1366 × 768** — viewport critique de recette.

Le Shell doit rester exploitable à 1366 × 768 sans défilement horizontal de page.

### 3.2. Grille

- grille logique : 12 colonnes dans la zone de travail ;
- liste : 8 à 12 colonnes ;
- panneau : 4 à 5 colonnes quand la largeur le permet ;
- si le panneau devient trop étroit, il remplace temporairement la liste avec un retour explicite ;
- document/comparaison : mode large 12 colonnes.

### 3.3. Spacing prototype

Échelle adoptée pour les prototypes : `4 / 8 / 16 / 24 / 32–48`.

Cette échelle est normative pour la cohérence V0 ; elle ne fige pas la future charte de marque.

---

## 4. États obligatoires de V0-01

Le Shell doit être maquetté dans les situations suivantes :

1. **hors Affaire** — Accueil ou Opportunités ;
2. **dans une Affaire** — contexte complet ;
3. **lien direct profond** — ouverture d'un objet avec contexte reconstruit ;
4. **lot/phase/tour à changer** — avertissement si travail local ;
5. **droit insuffisant** — contenu non révélé ;
6. **session expirée puis reprise** — contexte restauré après réauthentification ;
7. **service/IA dégradé** — Shell utilisable, état ciblé ;
8. **laptop étroit** — rail réduit et panneau adaptatif.

Les états 5–7 peuvent être matérialisés en V0-01 comme variantes de Shell, puis approfondis dans V0-13/V0-14/V0-16.

---

## 5. Interactions V0-01 à rendre visibles

V0-01 n'est pas une image statique unique. Le prototype doit permettre de démontrer :

- ouvrir une Affaire depuis le rail ou une liste ;
- changer de destination Affaire ;
- ouvrir un panneau de détail ;
- basculer du panneau au mode large ;
- revenir à la liste avec filtre/position restaurés ;
- ouvrir un lien direct ;
- changer de lot/phase/tour avec avertissement si nécessaire ;
- réduire/ouvrir le rail sur laptop ;
- ouvrir recherche/alertes/aide sans perdre le contexte ;
- expirer la session puis restaurer le contexte après reprise.

---

## 6. Ce que V0-01 ne doit pas valider

V0-01 ne décide pas encore :

- du design final de toutes les cartes métier ;
- de la grammaire complète B0/B1/B2 ;
- de tous les états C05 ;
- de la remise complète C11 ;
- du comportement détaillé de l'IA ;
- du responsive mobile final ;
- de la charte de marque finale ;
- d'un framework ou composant frontend de production.

Toute conclusion sur ces sujets est réservée aux unités V0 suivantes.

---

## 7. Livrables exacts de V0-01

### V0-01-F01 — Shell Affaire / desktop de confort

**Vue :** Affaire active, rail ouvert, barre supérieure, bandeau complet, cinq destinations, contenu neutre réaliste.  
**But :** valider hiérarchie globale et séparation navigation globale / Affaire / action.  
**Données :** scénario École des Pins.  
**Critère :** Affaire, candidate, lot, phase, tour et échéance identifiables en moins de 5 secondes.

### V0-01-F02 — Shell hors Affaire

**Vue :** Accueil ou Opportunités sans bandeau Affaire.  
**But :** vérifier que le Shell ne donne pas l'impression qu'une Affaire est toujours active.  
**Critère :** changement de contexte global compréhensible sans espace vide artificiel.

### V0-01-F03 — Laptop 1366 × 768

**Vue :** même Affaire, rail réduit, densité réaliste, contenu et action principale visibles.  
**But :** recette de densité minimale.  
**Critère :** aucun scroll horizontal de page ; contexte + titre + action + contenu utile restent exploitables.

### V0-01-F04 — Panneau de détail puis mode large

**Vue A :** liste + panneau court.  
**Vue B :** passage en mode large pour lecture/édition substantielle.  
**But :** prouver `liste → détail → travail long → retour`.  
**Critère :** aucun empilement de panneaux ; retour conserve sélection, filtre et position.

### V0-01-F05 — Reprise de contexte / changement sensible

**Board à deux états :**
- ouverture par lien direct ;
- changement de lot/phase/tour avec brouillon local présent.

**But :** valider que le contexte est reconstruit et qu'aucun changement ne détruit silencieusement du travail.  
**Critère :** l'utilisateur sait ce qui sera changé, ce qui sera conservé et comment revenir.

### 7.1. Gate V0-01

V0-01 est **VALIDÉ** uniquement si :

- F01 à F05 existent ;
- les cinq destinations Affaire restent stables ;
- la séparation global/Affaire/action est comprise ;
- le laptop 1366 × 768 passe la recette ;
- le retour au contexte est démontré ;
- aucune information sensible n'est révélée par le Shell ;
- aucune décision de V0-02+ n'a été figée par accident.

---

# PARTIE II — CATALOGUE EXACT DES PROTOTYPES V0-01 À V0-16

## 8. Règle de production

La V0 comporte **16 unités de validation**, dans l'ordre ci-dessous. Une unité n'est pas « un écran » : elle peut contenir plusieurs frames ou une planche d'états.

Les frames obligatoires sont identifiés `V0-XX-FYY`.

Un prototype suivant peut être préparé pendant la revue du précédent, mais il n'est pas déclaré validé si une ambiguïté de preuve, d'autorité ou de reprise du précédent reste ouverte.

Le scénario de données commun demeure une PME BTP fictive, une consultation multilot, RC/CCAP/CCTP/DPGF ou BPU, visite obligatoire, contradiction, page illisible, coût non couvert, devis expiré, GO conditionnel, rectificatif, remise, reçu partiel, un lot gagné et un perdu.

---

## 9. V0-01 — Shell desktop/laptop

**Contrats :** C00 structure, GLB-01, navigation, contexte Affaire.  
**Livrables :** F01 à F05 définis en Partie I.  
**Sortie :** Shell validé comme conteneur de toutes les unités suivantes.

---

## 10. V0-02 — Système visuel métier / C00

**But :** rendre observable le vocabulaire métier avant de dessiner les flux complexes.

### V0-02-F01 — Planche des natures métier
Fait, Source, Preuve, Exigence, Inconnu, Hypothèse, Contradiction, Risque, Tâche, Décision, Condition.

### V0-02-F02 — Planche B0 / B1 / B2
Ouvert, en revue, levé/accepté lorsque applicable ; compréhension en niveaux de gris.

### V0-02-F03 — Planche IA / validation humaine / obsolète / à revalider
Origine, date, portée, limite, auteur de validation.

### V0-02-F04 — Planche des états système C00
Vide réel, filtre vide, chargement, traitement, partiel, indisponible, interdit, erreur, bloqué, à revalider, non confirmé, IA indisponible, hors ligne, reprise.

### V0-02-F05 — Actions / preuve / échéances / droits
Boutons engageants explicites, panneau preuve, dates/fuseaux, permission visible sans fuite.

**Gate :** chaque état reste compréhensible sans couleur seule ; aucune collision entre UX-Critical, B0/B1/B2 et statut métier.

---

## 11. V0-03 — Accueil commun / Patron

**But :** valider « Patron = décisions/exceptions » et la Minute Patron.

### V0-03-F01 — Patron normal
Trois décisions, une condition, une urgence remise, preuve disponible.

### V0-03-F02 — Patron sans décision immédiate
Aucune décision attendue ; surveillance utile sans remplissage artificiel par KPI.

### V0-03-F03 — Patron avec information économique autorisée + panne IA ciblée
Valeurs Direction visibles car autorisées ; briefing ancien/indisponible mais décisions manuelles accessibles.

**Gate :** toutes les décisions pertinentes du scénario sont trouvées et expliquées en 60–90 secondes.

---

## 12. V0-04 — Accueil Responsable / Expert

**But :** même architecture, compositions différentes sans faux changement de rôle.

### V0-04-F01 — Responsable d'offre
Bloque la remise / À produire / En attente tiers / À faire revoir.

### V0-04-F02 — Expert sollicité
Contribution attendue, question précise, source, demandeur, échéance.

### V0-04-F03 — Expert sans contribution + droits restreints
Aucune carte interdite, aucun compteur révélateur ; accès seulement au contexte autorisé.

**Gate :** l'utilisateur sait ce qui lui est demandé sans parcourir tous les registres.

---

## 13. V0-05 — C05 « À résoudre » normal

**But :** réunir visuellement les objets sans fusionner leur nature.

### V0-05-F01 — File multi-objets
Exigence + contradiction + inconnu + hypothèse + risque + tâche dans la même liste.

### V0-05-F02 — Panneau Exigence + tâche liée
`Terminer la tâche` ne ferme pas l'exigence ; revue de preuve séparée.

### V0-05-F03 — Panneau Contradiction / Inconnu / Risque
Planche de trois panneaux ou états montrant leurs différences structurelles.

**Gate :** Responsable distingue chaque nature sans légende permanente et sans statut générique « ouvert/fermé ».

---

## 14. V0-06 — C05 états difficiles

**But :** prouver que la file reste honnête quand les données ne le sont pas.

### V0-06-F01 — Partiel + filtre vide
Lecture partielle explicite ; filtre vide distinct d'une réussite.

### V0-06-F02 — À revalider + droits limités
Ancienne conclusion liée à DCE v2, v3 reçue ; objets interdits absents sans total révélateur.

### V0-06-F03 — IA indisponible + erreur d'action
Objets existants utilisables ; voie manuelle ; échec d'affectation sans perte.

**Gate :** aucun état difficile n'est rendu par un simple toast ou spinner.

---

## 15. V0-07 — Preuve + C06 comparaison

**But :** matérialiser « preuve à un geste, document à deux » et la comparaison versionnée.

### V0-07-F01 — Panneau preuve
Assertion, source, extrait, interprétation, validation, effets.

### V0-07-F02 — Document en mode large à l'emplacement exact
Retour au contexte d'origine préservé.

### V0-07-F03 — Comparaison DCE v2 / v3
Deux versions, différences visibles, impacts `confirmé / à interpréter / non établi`.

**Gate :** l'utilisateur peut vérifier sans confondre écart documentaire et impact métier.

---

## 16. V0-08 — N01 conflit de contributions

**But :** aucun `dernier clic gagne` silencieux.

### V0-08-F01 — Conflit détecté
Version confirmée + contribution A + contribution B préservées.

### V0-08-F02 — Résolution et revalidation
Retenir A / B / composer ; motif ; portée ; validations dépendantes rouvertes.

**Gate :** aucune contribution perdue ; résoudre le texte ne valide pas automatiquement l'objet métier.

---

## 17. V0-09 — N02 résultat non confirmé

**But :** rendre sûr un résultat asynchrone ambigu.

### V0-09-F01 — Autorisation P5 non confirmée
Dernier état connu, tentative, vérification avant répétition.

### V0-09-F02 — Export non confirmé
Action principale `Vérifier le résultat`; pas de réessai dangereux.

### V0-09-F03 — Upload tiers non confirmé + résolution
Board montrant issue `succès exact / échec sûr / toujours indéterminé`.

**Gate :** l'utilisateur n'interprète jamais N02 comme succès ou échec sans preuve.

---

## 18. V0-10 — C11 Candidate

**But :** figer l'objet exact qui pourra être autorisé.

### V0-10-F01 — Candidate prête
Manifeste, fichiers, versions, signatures, source de chaque exigence.

### V0-10-F02 — Candidate incomplète / signature ou pièce manquante
B0/B1 visible ; aucune fausse readiness.

### V0-10-F03 — Candidate v8 après modification de v7
Ancienne P5 reste liée à v7 ; v8 doit être revue selon impact.

**Gate :** l'utilisateur peut nommer quel paquet exact est en cours et quelle autorisation le couvre.

---

## 19. V0-11 — C11 Contrôles / P5

**But :** rendre impossible la confusion entre contrôle, signature, autorisation et dépôt.

### V0-11-F01 — Contrôles B0/B1/B2
Trois classes séparées ; B0/B1 sans `Accepter quand même`.

### V0-11-F02 — B2 arbitrable
Scénario, motif, responsable, échéance/expiration.

### V0-11-F03 — Page de vérification + step-up
Paquet exact, manifeste, signatures, destinataire/canal, échéance ; texte `Cette autorisation ne dépose rien`.

### V0-11-F04 — Retour après step-up avec v8 apparue
Réauthentification réussie mais candidate différente ; autorisation suspendue jusqu'à nouvelle revue.

**Gate :** aucun participant n'assimile P5 à une signature ou à un dépôt.

---

## 20. V0-12 — C11 Transmission / Réception

**But :** séparer ce que l'opérateur a fait de ce que la plateforme externe prouve.

### V0-12-F01 — Instructions de dépôt humain
Candidate autorisée, canal, échéance, export exact, avertissement sur modification.

### V0-12-F02 — Transmission déclarée, aucun reçu
État `Réception non prouvée`.

### V0-12-F03 — Reçu incohérent / reçu partiel
Board comparatif des deux issues.

### V0-12-F04 — Réception et contenu rapprochés + historique/redépôt
Seulement lorsque la preuve le permet ; accès à l'historique et nouvelle candidate.

**Gate :** `envoyé`, `reçu`, `contenu rapproché` ne sont jamais synonymes.

---

## 21. V0-13 — Confidentialité croisée

**But :** tester la même vérité métier sous plusieurs permissions sans fuite directe ou indirecte.

### V0-13-F01 — Matrice Accueil / C05 par rôle
Patron, Responsable, Métreur, DAF, Admin, tiers ; mêmes faits, compositions différentes.

### V0-13-F02 — Matrice C08 Prix / C11 Remise
Marge/contribution Direction, coûts, autorité P5, opérateur de dépôt ; aucun pouvoir acquis par affichage.

### V0-13-F03 — Vecteurs indirects
Recherche, notification, résumé IA, export, historique, URL/retour : exemples `autorisé / supprimé / reformulé sans fuite`.

**Gate :** six profils internes et le tiers ne voient ni ne déduisent de donnée hors périmètre.

---

## 22. V0-14 — IA contextuelle

**But :** démontrer AI-native sans chat-first.

### V0-14-F01 — Briefing + `Pourquoi ?`
Bref daté, périmètre, sources, limites, raison de priorité.

### V0-14-F02 — Suggestion / transformation
Contradiction → brouillon de question ; modification/rejet/soumission à revue.

### V0-14-F03 — Panne IA / résultat ancien
Voie manuelle maintenue ; dernier résultat daté ; aucune relance automatique si issue inconnue.

**Gate :** contenu source, proposition IA et validation humaine sont distinguables sans couleur seule.

---

## 23. V0-15 — Responsive / mobile compagnon

**But :** transformer l'interface plutôt que miniaturiser le desktop.

### V0-15-F01 — Laptop étroit
Rail réduit, liste/panneau adaptés, colonnes essentielles maintenues.

### V0-15-F02 — Tablette liste → détail
Liste plein écran puis détail avec retour explicite et filtre conservé.

### V0-15-F03 — Mobile visite hors ligne + captures N05
Disponible sur appareil / local / en attente / confirmé ; P5 hors ligne indisponible et expliqué.

**Gate :** aucune fonction complexe n'est compressée en version illisible ; disponibilité hors ligne est explicite.

---

## 24. V0-16 — Parcours de fondation bout en bout

**But :** vérifier que les fondations tiennent ensemble avant d'ouvrir la macro-vague V1.

### V0-16-F01 — Entrée et sécurité
Invitation/connexion → MFA → organisation confirmée → arrivée dans le bon contexte.

### V0-16-F02 — Première valeur
C01 → C03 → C06 → C05 : première Affaire, import, lecture partielle, première exception sourcée, première action.

### V0-16-F03 — Interruption, panne et reprise
Session expirée ou panne IA pendant le parcours ; dernier confirmé visible ; reprise sans perte ni double action.

**Gate :** le parcours C15 → C01 → C03 → C06 → C05 fonctionne avec identité, droits, première valeur, panne et reprise.

---

# PARTIE III — INVENTAIRE, NOMMAGE ET VALIDATION

## 25. Inventaire quantifié

Le catalogue impose :

| Unité | Frames/boards obligatoires |
|---|---:|
| V0-01 | 5 |
| V0-02 | 5 |
| V0-03 | 3 |
| V0-04 | 3 |
| V0-05 | 3 |
| V0-06 | 3 |
| V0-07 | 3 |
| V0-08 | 2 |
| V0-09 | 3 |
| V0-10 | 3 |
| V0-11 | 4 |
| V0-12 | 4 |
| V0-13 | 3 |
| V0-14 | 3 |
| V0-15 | 3 |
| V0-16 | 3 |
| **TOTAL MINIMUM** | **53** |

`53` ne signifie pas 53 routes ou 53 écrans de production. Il s'agit de **53 unités visuelles minimales de validation**, certaines étant des boards multi-états.

Une même maquette peut couvrir plusieurs variantes uniquement si chaque comportement reste identifiable et testable. Toute fusion destinée seulement à faire baisser le compteur est interdite.

---

## 26. Convention de nommage

Chaque fichier visuel ou prototype suit :

`SMART_AO_<V0-XX>_<FYY>_<nom-court>_<revision>`

Exemples :

- `SMART_AO_V0-01_F01_Shell_Affaire_r01.png`
- `SMART_AO_V0-05_F02_Exigence_Tache_r01.png`
- `SMART_AO_V0-11_F03_P5_Check_StepUp_r01.png`

Une révision visuelle augmente `r01 → r02`.  
Une modification du contrat de l'unité augmente la version du présent document ; elle n'est pas cachée dans le nom d'une image.

---

## 27. Statut d'une frame

Chaque frame possède un statut parmi :

- `DRAFT` — première matérialisation ;
- `REVIEW` — soumise à revue propriétaire ;
- `CHANGES` — correction demandée ;
- `APPROVED_FOR_V0` — valide pour la recette V0 ;
- `SUPERSEDED` — remplacée mais conservée pour historique.

Aucune frame `APPROVED_FOR_V0` ne signifie que l'UX globale est gelée.

---

## 28. Fiche de revue obligatoire par frame

Chaque revue doit répondre à :

1. **Compréhension** — que pense l'utilisateur qu'il regarde ?
2. **Contexte** — Affaire/lot/phase/tour/version sont-ils clairs ?
3. **Action** — quelle est l'action principale et son effet ?
4. **Preuve** — que sait-on réellement et où est la source ?
5. **Autorité** — qui peut faire quoi ?
6. **Inconnu** — qu'est-ce qui n'est pas établi ?
7. **Reprise** — que se passe-t-il après interruption/retour ?
8. **Confidentialité** — une donnée ou son existence fuit-elle indirectement ?
9. **Accessibilité** — le sens survit-il sans couleur seule et au clavier ?
10. **Densité** — est-ce encore lisible sur le viewport prévu ?

---

## 29. Règles de correction

Une correction de prototype peut :

- déplacer une information ;
- simplifier un libellé ;
- changer un composant ;
- regrouper visuellement des contenus ;
- changer la hiérarchie ;
- modifier la densité ;
- changer un pattern d'interaction.

Elle ne peut pas, sans arbitrage documentaire :

- supprimer une exigence métier ;
- élargir un droit ;
- fusionner preuve et interprétation ;
- transformer B0/B1 en risque acceptable ;
- automatiser P5 ou le dépôt ;
- cacher un inconnu ;
- considérer `tâche terminée = conformité` ;
- considérer `transmis = reçu` ;
- transformer le mobile en poste d'étude complet.

---

## 30. Ordre d'exécution à partir de maintenant

La prochaine production visuelle est :

> **V0-01-F01 — Shell Affaire / desktop de confort**

Elle doit reprendre la force visuelle de `SMART_AO_CONCEPT_VISUEL_COMPOSITE_01`, mais retirer tout ce qui empêcherait de juger séparément le Shell.

Après validation de F01 :

`F02 → F03 → F04 → F05 → Gate V0-01 → V0-02`.

On ne régénère donc plus une « belle vue d'ensemble » indifférenciée. Chaque image suivante possède un identifiant, un contrat et un critère de validation.

---

## 31. Condition de sortie globale de V0

La V0 est considérée prête à passer à la macro-vague **V1 — Première valeur / onboarding** uniquement lorsque :

- les 16 unités V0 ont été parcourues ;
- les 53 unités visuelles minimales ont un statut final exploitable ou une fusion explicitement justifiée ;
- V0-01 à V0-16 ont franchi leur gate ;
- le Patron identifie les décisions pertinentes en 60–90 secondes dans le scénario ;
- le Responsable distingue tâche, exigence, inconnu, contradiction et risque ;
- P5 n'est jamais compris comme signature ou dépôt ;
- transmission n'est jamais comprise comme réception ;
- N01 ne perd aucune contribution ;
- N02 n'entraîne pas de répétition dangereuse ;
- aucune fuite de droit n'est détectée dans les variantes testées ;
- la navigation clavier et le retour au contexte sont matérialisés ;
- le laptop 1366 × 768 reste exploitable ;
- le mobile expose clairement `disponible / local / en attente / confirmé` ;
- la panne IA ne bloque pas artificiellement les opérations manuelles critiques.

À ce moment seulement, la séquence suivante devient :

`V1 Première valeur/onboarding → V2 Comprendre/décider → V3 Produire/remettre → V4 Transmettre/entretenir → V5 Gouvernance/fermeture → V6 Recette transversale`.

---

**Fin — SMART AO V0-01 Shell + Catalogue exact des prototypes V0 — OWNER EXECUTION SPEC v0.1**
