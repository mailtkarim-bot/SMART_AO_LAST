# SMART AO — exécution G01–G52 — matrice de recette v0.1

**Autorité :** cahier produit/métier OWNER v0.4 et catalogue UX OWNER_CONSOLIDATED v0.3.  
**Périmètre :** recettes métier et adversariales G01–G52, rôles et états difficiles applicables.  
**Date de passe :** 20 septembre 2026.

## Verdict de la première passe

La suite automatisée disponible a été exécutée contre PostgreSQL Docker : **1 651 tests passent, 2 sont ignorés faute de PIL et 50 échouent**. Cette suite est une preuve de non-régression technique ; elle ne suffit pas à déclarer les 52 recettes métier acceptées. Les recettes restent ouvertes tant qu’un scénario complet avec rôle, état initial, action, refus attendu, preuve append-only et état final n’est pas matérialisé.

Le registre machine fermé se trouve dans `backend/app/platform/quality/data/g01_g52.json`. Il est chargé par `backend/app/platform/quality/recipe_catalog.py` et contrôlé par `backend/tests/application/test_recipe_catalog.py` ; chaque ID G01–G52 possède un rôle, un état initial, une action, un refus, une preuve append-only, un état final et un mode d’exécution.

Les corrections réalisées pendant cette passe sont limitées aux régressions bloquantes identifiées : compatibilité de la route Patron avec les fixtures sans service d’outcome, compatibilité des commandes de soumission historiques avec les nouveaux champs de mode, et résultat Collaborateur sans lot pour une Affaire sans périmètre de lots. Les tests ciblés correspondants repassent.

## Seconde passe après corrections

La suite backend complète a été rejouée après correction : **1 701 tests passent, 2 sont ignorés uniquement parce que PIL n’est pas installé**. Le lot critique DCE, soumission, partage et gouvernance passe également avec **311 tests sur 311**. Les contrôles architecture, identité/C14 et exploitation sont verts. Les dix avertissements restants sont des dépréciations Starlette/httpx et 422, sans échec fonctionnel.

## Exécution G01–G09 — 20 septembre 2026

Le premier lot de flux réels DCE a été rejoué contre PostgreSQL Docker avec les suites extraction, classification, upload, staging, analyse, exigences, lecture et routes HTTP. Le résultat est de **105 tests réussis, 5 avertissements, 115,20 s**. La preuve détaillée et la correspondance test/scénario sont dans [`SMART_AO_PHASE9_G01_G09_EXECUTION_PREUVE_v0.1.md`](SMART_AO_PHASE9_G01_G09_EXECUTION_PREUVE_v0.1.md).

Les fixtures métier G01–G09 sont maintenant versionnées dans `backend/app/platform/quality/data/g01_g09_business.json`. Leur rejeu dédié passe **10 tests** (9 unitaires, 1 PostgreSQL), dont un événement `CapabilityGapReported` append-only pour G04. Les scénarios restent ouverts lorsque la preuve humaine ou la résolution métier n’est pas encore persistée.

| Scénarios | Résultat de la passe | Décision |
|---|---|---|
| G01 | PARTIEL — provenance, absence de signal, exigences et lecture prouvées | compléter le blocage P3/P5 sur plan absent |
| G02 | PARTIEL — versions non admises, stale et rejeu prouvés | jouer l’invalidation P5 après rectificatif |
| G03 | PARTIEL — sources conservées sans priorité automatique | jouer la résolution humaine motivée |
| G04 | PREUVE VERTICALE TECHNIQUE — gap levage bloquant, source CCTP et événement append-only | faire la décision économique humaine |
| G05 | PARTIEL — projection XLSX/DOCX et immutabilité prouvées | jouer l’édition dérivée non qualifiée |
| G06 | PARTIEL — illisible/OCR/limites fail-closed prouvés | projeter l’échéance inconnue |
| G07 | PREUVE TECHNIQUE — protégé sans contournement | confirmer le blocage métier dépendant |
| G08 | PARTIEL — limite archive et inventaire borné prouvés | jouer le manifeste partiel et la reprise |
| G09 | PREUVE VERTICALE TECHNIQUE — contenu hostile isolé sans exécution | relier revue et événement append-only |

Ces statuts ne sont pas des acceptations métier : les recettes G01–G09 restent `NON CLOTUREE` jusqu’à l’exécution des décisions humaines et des preuves append-only attendues.

## Échecs regroupés à traiter

| Groupe | Résultat | Action restante |
|---|---|---|
| Routes Patron / soumission | Corrigé : 46 tests ciblés passent | conserver la couverture dans la seconde passe G15/G23/G30–G38 |
| Tâches Collaborateur sans lot | Corrigé : 10 tests ciblés passent | ajouter les scénarios multi-lots et lot hors périmètre |
| Garde de décision soumission | Corrigé par compatibilité de commande | rejouer avec décision `NO_GO`, gate absent et `CANDIDATURE_ONLY` |
| Dette de frontière applicative | 3 violations préexistantes | extraire les ports de `contribution_conflicts.py`, `order.py`, `outcome.py` |
| Contrat exploitation | tests obsolètes sur l’ancien head `20260826_0067` et guide déplacé | réaligner le test et le guide sur `20260920_0090` dans la tranche exploitation |
| Unicité Patron historique | attente de test incompatible avec la propriété organisationnelle C14 | remplacer par la règle propriétaire/Patron actuelle avant gel |

## Ledger G01–G52

Les états ci-dessous sont volontairement `NON CLOTUREE` : la ligne décrit la recette à jouer et rappelle qu’une preuve technique voisine ne vaut pas acceptation métier.

| ID | Espaces | Cas à exécuter | État |
|---|---|---|---|
| G01 | C06/C05/C08 | Plan annoncé absent, couverture dépendante non prouvée | NON CLOTUREE |
| G02 | C06/C07/C11 | Rectificatif après P5, ancienne autorisation non valable pour nouveau paquet | NON CLOTUREE |
| G03 | C05/C06 | RC/CCAP contradictoires, deux sources et résolution motivée | NON CLOTUREE |
| G04 | C08 | Besoin levage sans poste, coût non couvert | NON CLOTUREE |
| G05 | C06/C10/C11 | XLS imposé conservé, édition non qualifiée signalée | NON CLOTUREE |
| G06 | C06/C05 | Page illisible, échéance non inventée | NON CLOTUREE |
| G07 | C06 | Fichier protégé, pas de contournement | NON CLOTUREE |
| G08 | C06/C00 | Archive hors limite, inventaire partiel et reprise | NON CLOTUREE |
| G09 | C06/C14 | Contenu dangereux isolé sans exécution ni envoi IA | NON CLOTUREE |
| G10 | C05/C11 | Visite exigée sans preuve, blocage applicable | NON CLOTUREE |
| G11 | C03/C05 | Conflit de dates, pas de report automatique | NON CLOTUREE |
| G12 | C09/C08/C07 | Devis expiré, hypothèse et P3 réexaminées | NON CLOTUREE |
| G13 | C05/C14/N04 | Releveur voit travail attendu sans pouvoir automatique | NON CLOTUREE |
| G14 | C14/C00/N04 | Révocation immédiate, partage futur et publication refusés | NON CLOTUREE |
| G15 | C07/C11/C14 | P5 refusée sans délégation, préparation permise selon droits | NON CLOTUREE |
| G16 | C05/C10/N01 | Deux contributions conservées, validation divergente bloquée | NON CLOTUREE |
| G17 | C14/C13 | Auto-élévation Admin refusée sans autorité compétente | NON CLOTUREE |
| G18 | C14/C15 | Suspension du dernier Propriétaire compromis possible ; récupération encadrée | NON CLOTUREE |
| G19 | C15 | Récupération MFA non fondée sur seul email | NON CLOTUREE |
| G20 | C10/C15/N01 | Reconnexion, brouillon confirmé et local distingués | NON CLOTUREE |
| G21 | C09/C10/C11/C13 | Mandat/signature par membre du groupement | NON CLOTUREE |
| G22 | C09/C10 | Partenaire consulté ne devient pas engagé par génération | NON CLOTUREE |
| G23 | C12/C06/C07 | Commande privée différente, accord non établi et P6 | NON CLOTUREE |
| G24 | N03/C16/C14 | Révocation coupe le futur, fichiers téléchargés non rappelés | NON CLOTUREE |
| G25 | C00/C11/N02 | Panne IA, contrôles humains et export conservés selon état réel | NON CLOTUREE |
| G26 | C02 | Panne BOAMP, fraîcheur explicite et saisie manuelle | NON CLOTUREE |
| G27 | C05/N05 | Capture locale non annoncée partagée | NON CLOTUREE |
| G28 | C00/C11 | Heure source Paris et conversion Maroc représentent le même instant | NON CLOTUREE |
| G29 | C06/C00 | Instruction hostile dans DCE n’envoie aucune marge ni ne change les droits | NON CLOTUREE |
| G30 | C11 | Paquet modifié non exporté comme ancien paquet autorisé | NON CLOTUREE |
| G31 | C11/N02 | Transmission déclarée sans réception prouvée | NON CLOTUREE |
| G32 | C11 | Reçu mauvais lot/hors délai signalé incohérent | NON CLOTUREE |
| G33 | C11 | Pli reçu, contenu non intégralement rapprochable | NON CLOTUREE |
| G34 | C11 | Redépôt complet, nouvelle candidate et reçu | NON CLOTUREE |
| G35 | C11 | Copie de sauvegarde distincte, pas remplacement automatique | NON CLOTUREE |
| G36 | C10/C12 | Engagement promis non omis de la passation | NON CLOTUREE |
| G37 | C03/C10/C11 | Candidature seule, P3 non applicable avec motif | NON CLOTUREE |
| G38 | C12 | Un seul lot gagné transmis, pas de fusion de prix/engagements | NON CLOTUREE |
| G39 | C08 | Vente 120/coûts 100 : 20 et 16,67 %, puis incomplet si coût inconnu | NON CLOTUREE |
| G40 | C08/C06 | Total Excel non recalculé/ligne masquée à vérifier | NON CLOTUREE |
| G41 | C08 | Conflit de ressource/période, capacité non démontrée | NON CLOTUREE |
| G42 | C08/C07 | Financement manquant visible malgré marge estimée positive | NON CLOTUREE |
| G43 | C13/C10 | Assurance valide hors activité non applicable | NON CLOTUREE |
| G44 | C13/C10/N03 | CV sensible, version minimisée et revue avant partage | NON CLOTUREE |
| G45 | C14/C13 | Export Direction requiert autorité correspondante | NON CLOTUREE |
| G46 | C14 | Support après expiration refusé | NON CLOTUREE |
| G47 | C14/N02 | Export interrompu/litige bloque fermeture concernée | NON CLOTUREE |
| G48 | C14/C00 | Restauration vérifie révocations/purge avant réouverture | NON CLOTUREE |
| G49 | C00/C07/C11 | Preuve et autorisation réalisables au clavier | NON CLOTUREE |
| G50 | C05/C10/C13 | Critère environnemental sans réponse pertinente signalé | NON CLOTUREE |
| G51 | C07/C11/N01 | Condition échue ou décisions concurrentes bloquent validation | NON CLOTUREE |
| G52 | C00/C01/C08/C13/C16 | Aucune divulgation de marge directe, déduite ou via ancienne sortie révoquée | NON CLOTUREE |

## Limites assumées

La qualification Golden DCE réelle, les plateformes externes, les essais d’accessibilité avec clavier/lecteur d’écran et la validation propriétaire ne peuvent pas être déduits de la suite automatisée. Aucune de ces limites ne doit être masquée par un statut `PASS` technique.

**Prochaine tranche :** relier les preuves G01–G09 aux actes métier encore manquants : résolution humaine G03, décision P3/P5 G01/G02, édition dérivée G05 et revue propriétaire G04/G06.
