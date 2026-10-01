# SMART AO — EXP-02 : décision de poursuivre ou d’écarter sans score opaque

**Statut :** AUDITÉ · CONTRAT IMPLÉMENTÉ · PREUVE FRONT/HTTP/POSTGRESQL  
**Date :** 15 septembre 2026  
**Autorité produit/métier :** `SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v2.0.md`
**Référence UX :** `SMART_AO_Catalogue_Ecrans_Parcours_Produit_OWNER_CONSOLIDATED_v0.3.md`

## 1. Objet et verdict

Cette tranche vérifie comment SMART AO doit permettre de poursuivre ou d’écarter une opportunité sans transformer un classement automatique en décision métier.

**Verdict : aucune nouvelle table de score ni aucun seuil GO/NO-GO n’est nécessaire.** Le code possède déjà les deux actes humains du début du parcours : la qualification P0 et l’ouverture P1 d’une Affaire. Le score BOAMP reste un signal public explicable pour le tri. La décision formelle GO/NO-GO réutilise ensuite l’agrégat `Decision` existant, contre un contexte gelé et une justification humaine.

Le cahier OWNER v0.4 exige cinq résultats possibles pour une décision engageante : **GO, GO SOUS CONDITIONS, ATTENTE, NO-GO, ABANDON**. Le domaine actuellement codé accepte seulement `GO`, `CONDITIONAL_GO` et `NO_GO`. Cet écart est déclaré et ne doit pas être masqué par un renommage ou une conversion silencieuse.

## 2. Autorité métier relue

Les règles applicables sont les suivantes :

- le Radar explique pourquoi une opportunité apparaît et permet de l’écarter avec un motif ;
- SMART AO ne présente pas un score opaque de chance de gagner ;
- P0 **Cibler** rend visibles les critères commerciaux ou les inconnus et permet de suivre, qualifier ou écarter ;
- P1 **Ouvrir** autorise l’effort d’étude et ouvre l’Affaire avec ses manques ;
- P2 porte la décision de principe après examen du périmètre, de la charge, des partenaires et du MIRP ;
- une décision engageante conserve l’auteur habilité, la date, la version/contexte, les faits, les preuves, les inconnus, les conditions, le motif, la revue éventuelle et la supersession ;
- une ATTENTE exige un responsable, un motif et une date ou un événement de réexamen ; un NO-GO/ABANDON conserve le motif et l’historique.

Références : sections 13.1, 13.2, 22, R04, R05 et E08 du cahier OWNER v0.4.

## 3. Audit du code vivant

| Élément | Preuve dans le dépôt | Conclusion |
|---|---|---|
| Score BOAMP | `BoampOpportunityScoringService` produit `BOAMP_PUBLIC_V1`, quatre facteurs publics bornés et une empreinte d’explication. | Explicable, déterministe et sans donnée financière ; il ne doit pas décider. |
| Filtre de liste | `GET /api/v1/patron/boamp-opportunities` accepte `min_score`. | Filtre de lecture seulement ; il ne crée, ne qualifie et ne clôt aucune opportunité. L’interface ne l’utilise pas comme seuil métier. |
| Qualification P0 | `BoampQualificationCommand` ferme les couples décision/motif et persiste une ligne append-only avec acteur, motif, score et version instantanés. | Déjà suffisant pour `TARGETED`, `DISCARDED` et `SNOOZED`, indépendamment du score. |
| Projection P0/P1 | `PatronBoampObservationService` projette P0, P1, échéance, lots et inconnus depuis les faits tenant-scopés. | La décision reste lisible après rechargement ; aucune transition n’est déduite du classement. |
| Ouverture P1 | `BoampCaseCreationService` exige `QUALIFIED`, crée une Affaire `OPPORTUNITY` idempotente et conserve les manques. | « Poursuivre l’étude » est un acte humain P1, pas un GO économique. |
| Décision formelle | `Decision`, `CreateDecision`, `FreezeDecisionContext` et `FinalizeGoNoGoDecision` exigent une Affaire, un contexte vérifié, une justification et une habilitation patronale. | Réutiliser cet agrégat ; ne pas inventer un second registre. |
| Front actuel | `BoampOpportunityPanel` affiche le nombre `/100`, la mention non décisionnaire, les facteurs lisibles et la décision P0 courante. Le bouton d’ouverture exige `P0=TARGETED`. | La preuve front couvre l’indépendance entre score, décision et ouverture ; le endpoint HTTP confirme `401` sans bearer et `200` avec score élevé mais `P0=UNREVIEWED`. |

## 4. Contrat minimal retenu

Le parcours distingue trois portées qui ne doivent pas être fusionnées :

| Portée | États | Sens | Autorité |
|---|---|---|---|
| **P0 — Cibler** | `UNREVIEWED`, `TARGETED`, `SNOOZED`, `DISCARDED` | Signal public à examiner, à suivre, à attendre ou à écarter avec motif. `TARGETED` signifie « poursuivre la qualification », jamais GO. | Qualification humaine append-only |
| **P1 — Ouvrir** | `NOT_OPEN`, `OPEN_WITH_UNKNOWNS` | Effort d’étude autorisé ou non. L’ouverture ne prouve ni réception du DCE, ni conformité, ni prix. | Création idempotente d’Affaire |
| **P2 — Décider** | `UNDECIDED`, `GO`, `CONDITIONAL_GO`, `NO_GO` actuellement | Décision engageante sur une Affaire après contexte gelé. `ATTENTE` et `ABANDON` restent à ajouter explicitement pour couvrir le contrat OWNER complet. | Agrégat `Decision` |

Le contrat d’une action humaine contient au minimum :

1. l’état choisi et un motif non vide ;
2. l’acteur habilité, l’horodatage, le tenant et les identifiants de commande/idempotence ;
3. les faits et références affichés, les inconnus visibles et, pour un GO conditionnel, chaque condition avec responsable, preuve attendue, échéance ou raison d’absence et conséquence d’échec ;
4. la version du score et son instantané comme contexte explicatif, jamais comme résultat calculé ;
5. la possibilité de relire la dernière décision et son historique sans écraser les décisions précédentes.

## 5. Invariants anti-score opaque

- Un score de 10 et un score de 100 ne changent aucun état P0/P1 sans commande humaine validée.
- Une qualification `QUALIFIED`, `REJECTED` ou `SNOOZED` est refusée si son motif n’est pas compatible ; le navigateur ne peut pas fabriquer l’état.
- Le score, sa version, ses facteurs et la fraîcheur de collecte sont présentés comme **pertinence publique pour le tri — non décisionnaire**.
- `min_score` est un filtre de lecture facultatif. Il ne doit jamais être interprété comme « seuil de poursuite » ou « seuil d’écartement ».
- Une opportunité écartée reste visible dans son historique avec le motif ; un résultat absent, inconnu ou expiré n’est pas converti silencieusement en NO-GO.
- L’ouverture P1 ne déclenche aucune finalisation `Decision`. Une décision P2 exige une Affaire, un contexte gelé, les références vérifiées et une justification humaine.
- Un contexte devenu obsolète est refusé ; une nouvelle décision est créée ou une décision antérieure est supersédée explicitement.
- `ATTENTE` et `ABANDON` ne sont pas simulés par `SNOOZED` ou `NO_GO` : leur ajout sera une extension de contrat séparée, avec responsable/réexamen pour ATTENTE et historique conservé pour ABANDON.

## 6. Traduction UX minimale

La fiche d’opportunité doit montrer, dans cet ordre :

1. fraîcheur et source publique ;
2. état P0 et motif de la dernière qualification ;
3. score et version, avec les facteurs développables et la mention non décisionnaire ;
4. état P1, échéance, lots et inconnues ;
5. l’action humaine disponible : **Cibler**, **Mettre en attente**, **Écarter avec motif**, puis **Ouvrir l’Affaire pour étude** lorsque P0 est `TARGETED`.

Le bouton ne doit jamais s’appeler « accepter le score », « GO automatique » ou équivalent. La décision formelle se fait dans le dossier de décision de l’Affaire, avec récapitulatif du contexte et confirmation explicite.

## 7. Plus petite preuve verticale implémentée

La prochaine preuve est volontairement limitée à l’indépendance entre score et décision :

1. une observation non qualifiée reste `P0=UNREVIEWED` quel que soit son score ;
2. la même observation qualifiée `QUALIFIED` devient `P0=TARGETED` avec motif et score instantané persistés ;
3. une observation qualifiée `REJECTED` devient `P0=DISCARDED` avec motif, même avec un score maximal ;
4. une observation `TARGETED` convertie ouvre `P1=OPEN_WITH_UNKNOWNS` sans créer de décision P2 ; le rejeu reste idempotent ;
5. lorsqu’un dossier de décision existe, seule une commande humaine contre le fingerprint affiché peut produire `GO`, `CONDITIONAL_GO` ou `NO_GO` ; un changement de score ou de filtre ne peut pas finaliser la décision.

La preuve front et applicative est maintenant implémentée : les facteurs sont affichés, la décision P0 est nommée explicitement et un état `UNREVIEWED` ne permet pas d’ouvrir une Affaire même si un état optimiste local contient l’identifiant. Le endpoint HTTP exécuté sous Uvicorn confirme le refus `401` sans bearer et la lecture `200` d’un score élevé sans décision P0 ; les 5 tests PostgreSQL confirment la qualification, l’immutabilité du signal, la création/rejeu d’Affaire et la relecture de projection. La suite historique `TestClient` reste bloquée par l’environnement Starlette/httpx, sans remettre en cause le chemin HTTP réel.

## 8. Gaps et travaux volontairement parqués

- ajouter explicitement `ATTENTE` et `ABANDON` au contrat formel après vérification des transitions, de la persistance et des tests de soumission ;
- traiter la délégation P0/P1, actuellement limitée au `PATRON_ADMIN` dans la preuve ;
- couvrir le dossier reçu, le DCE, les lots identifiés et la décision P2 complète après EXP-03.

Ces points ne justifient pas une table de score ou une décision automatique intermédiaire.

## 9. Décision de tranche

Le classement BOAMP reste une aide de tri expliquée. **La poursuite et l’écartement sont des actes humains P0/P1 ; le GO/NO-GO est un acte P2 séparé.** Les garde-fous et la visibilité des facteurs sont implémentés sans modifier le modèle métier par une abstraction parallèle. Il reste à exécuter la preuve HTTP/PostgreSQL complète et à traiter séparément `ATTENTE`/`ABANDON`.

**Prochaine étape :** clôturer EXP-02 par la revue des rôles, refus, responsive utile et critères de gel.
