# SMART AO — Contre-audit métier, produit et fonctionnel

**Revue du 13 septembre 2026 — proposition, non Product Freeze.**

Socle examiné : `docs/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_DECISION_FREEZE_v0.2.md`, 1 339 lignes, lu intégralement. Les instructions de mission viennent de la demande jointe ; les décisions F du cahier sont le référentiel produit examiné. Le cahier original n'est pas modifié. Aucun choix d'architecture, aucune installation, aucun développement du nouveau cœur n'est autorisé par cette revue.

Lecture du dossier : ce rapport contient A/B/C/D/F/I et la synthèse H ; [règles, rôles et recettes](02_REGLES_ROLES_ET_RECETTES.md) contient les compléments R01–R16, les 16 profils et G01–G52 ; [contrats d'écrans](03_CONTRATS_FONCTIONNELS_ECRANS.md) contient E ; [sources et limites](04_SOURCES_ET_PREUVES.md) contient H détaillé. La copie [WORK_REVIEW v0.3](../SMART_AO_Cahier_Directeur_Produit_Metier_WORK_REVIEW_v0.3.md) rassemble le socle, le changelog, les arbitrages et les compléments. Ce dossier est archivé et ne concurrence pas le cahier consolidé v0.4, source active produit/métier.

## A. Verdict exécutif

**NON en l'état pour une promotion immédiate ; OUI SOUS CONDITIONS après fermeture des C1 ci-dessous.** La cible, la proposition de valeur, les deux piliers, le cycle vendu, l'autorité humaine, le contrôle du chiffrage importé et le dépôt humain sont suffisamment déterminés. Les onze DEC et treize OWN constituent une base exploitable. Le problème restant est le comportement précis dans les situations engageantes, pas la recherche d'un autre produit.

Aujourd'hui deux équipes pourraient respecter les mêmes phrases et livrer des comportements incompatibles : un administrateur pourrait s'attribuer le droit de voir une marge, un Patron pourrait lever une pièce obligatoire manquante par simple GO, un reçu sans inventaire pourrait être présenté comme preuve de chaque fichier, un prix importé pourrait afficher une « marge » sur une assiette différente, ou un compte compromis rester actif parce qu'il est l'unique Propriétaire. Ce sont des lacunes de décision produit, à fermer avant de les confier à un cahier technique.

Les vrais bloqueurs sont : autorité et récupération d'accès ; phase/lot/version et portes ; fidélité documentaire et limites garanties ; candidature, signature et preuve de remise ; définition économique minimale ; données d'entreprise applicables ; partage et données en fin de contrat ; contrats des écrans et parcours de qualification. **Douze C1** les regroupent sans multiplier un ticket par symptôme. Les compléments de cette revue donnent une solution proposée pour chacun ; les rédiger ne prouve pas leur acceptation ni leur fonctionnement.

La séquence de fermeture recommandée est : (1) propriétaire arbitre A01–A08 et traite L01–L12 ; (2) corrections documentaires et contrats adoptés avec traçabilité, exemples métier revus ; (3) qualifications juridiques critiques documentées ou comportement conservateur explicitement accepté ; (4) propriétaire décide de la promotion en Product Freeze. Le prototype testable est requis avant le gel technique complet selon OWN-12, et non ajouté par cet audit comme condition formelle supplémentaire au Product Freeze. La confrontation aux deux pilotes reste nécessaire pour qualifier la promesse de lancement. A2 demeure HOLD ; la reprise du code ne fait pas partie de cette livraison.

**Ce que la revue ne démontre pas :** aptitude réelle d'un moteur à préserver des fichiers imposés, accessibilité effective, disponibilité de service, conformité juridique globale, performances ou qualité IA sur un corpus indépendant, satisfaction de pilotes. Ce dossier donne les résultats observables à obtenir. Les recettes G sont écrites, non exécutées contre un logiciel ; aucun prototype utilisateur n'a été fabriqué.

## B. Matrice de couverture intégrale

« SOLIDE » signifie suffisamment clair à son niveau de décision, pas implémenté ou certifié. « CONTRADICTOIRE » peut signaler un statut ancien qui contredit le registre final ; le registre propriétaire demeure prioritaire. Une exigence partielle n'est pas classée ABSENT pour amplifier artificiellement le diagnostic.

| § | Domaine | État | Constat et fermeture attendue |
|---|---|---|---|
| 0 | Mandat et décisions | SOLIDE | Ne pas déléguer l'autorité au rédacteur ; expliciter la portée de v0.3, M01. |
| 0.1 | Fin de dispersion documentaire | À RENFORCER | Ajouter une règle de précédence entre F, compléments P et anciens documents ; L01. |
| 1 | Hiérarchie et futur gel | À RENFORCER | Une seule version applicable et journal des acceptations ; A01. |
| 2 | Statuts F/P/W/T/H | CONTRADICTOIRE | Des P restent sur des décisions OWN/DEC figées ; M02–M08. |
| 3 | Vision, promesse, limites | SOLIDE | Entrepreneur, preuve et marge ; ne pas convertir « gagner » en promesse de résultat. |
| 4 | Cible, public/privé, cycle | SOLIDE | Deux pilotes restent à observer ; phase candidature et privé minimal à spécifier, R01/R12. |
| 5 | Affaire et Mémoire Entreprise | INCOMPLET | Identités, périmètre de validité et snapshots de réutilisation manquent ; R01/R08. |
| 6 | Cycle P0–P7 | INCOMPLET | Entrées, sauts non applicables, lots et réouvertures ; R01/R04. |
| 7 | Patron, collaborateurs, experts, admin, tiers | INCOMPLET | Cumul n'est pas autorisation ; délégation et approbation des droits sensibles ; R02. |
| 8 | Premier compte, invitations, départs | CONTRADICTOIRE | Provisioning déjà figé ; récupération/invitation non fermées ; R02/R03. |
| 9 | Authentification | CONTRADICTOIRE | MFA tous, step-up et SSO sont tranchés ; sessions/récupération restent P, A02. |
| 10 | Cinq espaces | SOLIDE | Entreprise et Administration accueillent S01/S02 ; pas de nouvelle navigation de principe. |
| 11 | Douze écrans | INCOMPLET | Liste ≠ contrat ; E01–E12 et surfaces de soutien S01/S02. |
| 12 | Accueil Patron | À RENFORCER | Préparation mesurée, secret agrégé, fraîcheur, état partiel ; E01. |
| 13 | BOAMP/TED | CONTRADICTOIRE | DEC-06 signé ; TED V1.x et panne/retard visibles ; M04/E02. |
| 14 | Réception DCE | À RENFORCER | Inventaire distinct de lecture, limites et reprise ; R06/E04. |
| 15 | Univers documentaire | À RENFORCER | Documents multi-entités, phase, rôle et origine ; R01/R08. |
| 16 | Fidélité acheteur | INCOMPLET | Promesse sans matrice de formats/round-trip ; R06/A04. |
| 17 | Exigences et preuve | À RENFORCER | Caractère obligatoire/applicable, propriétaire et date de contrôle ; R07. |
| 18 | Inconnus/MIRP | À RENFORCER | Levée prouvée, expiration d'hypothèse et dépendance à porte ; R05. |
| 19 | Risques et coûts oubliés | À RENFORCER | Relier couverture/absence/prix au lieu de totaliser des alertes ; R09. |
| 20 | Fournisseurs et groupements | INCOMPLET | Consulté ≠ engagé ; mandat, rang, périmètre, validité ; R10. |
| 21 | Prix/marge/capacité/trésorerie | CONTRADICTOIRE | Doctrine déjà F ; calculs et minimum promis indéfinis ; R09/A05. |
| 22 | Décisions et portes | INCOMPLET | Autorité, effet, blocage non dérogeable, réouverture ; R04/R05. |
| 23 | Réponse/candidature | INCOMPLET | Candidature seule, alternatives de formulaires, critères, signature ; R07/R11. |
| 24 | Engagements | À RENFORCER | Périmètre, auteur, coût et acceptation chantier obligatoires ; R10/R12. |
| 25 | Coffre et remise | CONTRADICTOIRE | Dépôt humain déjà F ; niveaux de preuve et redépôt à fermer ; R11. |
| 26 | Rectificatifs et versions | À RENFORCER | Invalidation ciblée, impact inconnu conservateur, historique intact ; R05. |
| 27 | Privé | CONTRADICTOIRE | Minimum OWN-08 déjà F, qualification terrain encore W ; R12. |
| 28 | Identité IA unique | SOLIDE | Ne confère aucune autorité ni droit supplémentaire. |
| 29 | IA-native, non chat-first | SOLIDE | Détailler panne/quota et opérations manuelles par écran ; R13/E. |
| 30 | Confiance | À RENFORCER | Abstention opérationnelle et preuves insuffisantes visibles ; R05/R06. |
| 31 | Document hostile | À RENFORCER | Instruction documentaire n'accorde jamais un droit ni une action ; G09/G29/G52. |
| 32 | Collaboration | INCOMPLET | Concurrence, réaffectation, absence et délégation expirée ; R02/R15. |
| 33 | Notifications/échéances | À RENFORCER | Source et fuseau ; envoyé ≠ lu ; escalade sans fuite ; R15. |
| 34 | Mobile | À RENFORCER | Local/en attente/synchronisé, conflit et révocation ; R15/E. |
| 35 | Onboarding | CONTRADICTOIRE | Accompagné déjà F ; données initiales et responsabilité restent à préciser ; M08. |
| 36 | Administration | INCOMPLET | Pas d'auto-attribution Direction ; administration ≠ décision métier ; S02. |
| 37 | Support | INCOMPLET | Qui autorise quel contenu, durée et trace ; R13/A06. |
| 38 | Données/export/fin | INCOMPLET | Finalités, catégories, délais, sauvegardes, litige et export vérifié ; R14/A07. |
| 39 | Service dédié | SOLIDE | Ne démontre pas résidence, absence de transfert ou reprise ; R14/R15. |
| 40 | Accessibilité | À RENFORCER | RGAA courant + cible WCAG 2.2, états et pièces de preuve ; R16. |
| 41 | Mesure qualité/valeur | À RENFORCER | Dénominateurs et baseline manuelle ; aucun gain de marge inventé ; R06/R12. |
| 42 | Golden DCE | À RENFORCER | Jeux distincts et résultats hostiles par cas ; R16/G01–G52. |
| 43 | Technique ultérieure | SOLIDE | Aucune technologie ajoutée par la revue. |
| 44 | Greenfield/V8 | SOLIDE | Migration sélective sans relancer des fonctions non approuvées. |
| 45 | DEC-01–11 | SOLIDE | Tous conservés verbatim ; aligner les chapitres antérieurs. |
| 46 | OWN-01–13 | À RENFORCER | Un seul réexamen fort : compte unique compromis, D/A02. Aucun changement silencieux. |
| 47 | V1/V1.x/plus tard | À RENFORCER | Minimum P6/P7 présent V1, approfondissement V1.x ; automatisation ne change pas le dépôt humain. |
| 48 | Mandat Work | SOLIDE | Exécuté par le présent dossier, sans pouvoir d'approbation propriétaire. |
| 49 | Critères de gel | À RENFORCER | Fermer L01–L12, nommer approbateur et preuve ; ne pas confondre document et qualification. |
| 50 | Traduction technique | SOLIDE | Après décision explicite de gel et prototype requis. |
| 51 | Gouvernance après gel | SOLIDE | Journal de changements produit applicable également aux décisions nouvelles. |
| 52 | Chantier A1/A2 | SOLIDE | La revue documentaire est A1 ; elle ne lève pas A2 HOLD. |
| 53 | Résumé propriétaire | À RENFORCER | Accompagner du verdict présent sans remplacer la vision. |

**Absences ciblées au sein de domaines présents :** protocole observable de récupération de l'unique Propriétaire ; formule et assiette de marge ; matrice de formats réellement garantis ; grille de conservation par finalité ; niveau de preuve d'un reçu non détaillé. Elles alimentent L03/L06/L07/L09/L11, plutôt que cinq nouveaux domaines fictifs.

**À SIMPLIFIER :** éviter de multiplier les GO, portails et scores pour combler ces absences. Une seule décision datée par porte/périmètre, un registre commun de points à lever, une comparaison minimale de devis et une passation issue des engagements existants suffisent en V1. Le §47 doit être lu selon ces limites, pas comme une invitation à un ERP.

## C. Lacunes classées et exigences précises

### C1 — douze fermetures nécessaires au Product Freeze

| ID / priorité | Problème réel, utilisateur et situation | Conséquence | Exigence proposée et preuve de fermeture |
|---|---|---|---|
| L01 — C1 | Le responsable produit lit « DEC-05 à confirmer » alors que DEC-05/OWN-11 sont F. | Deux versions du périmètre, décisions inutilement rouvertes ou codées différemment. | Harmoniser les statuts §§8/9/13/21/25/27/35 ; confirmer précédence et registre d'acceptation A01. Vérification textuelle M01–M08. |
| L02 — C1 | Administrateur invité pour gérer les comptes ; il peut se donner un rôle DAF ou déléguer P5. Patron absent et plusieurs dirigeants concurrents. | Fuite de marge ou engagement sans autorité. | R02 : autorité compte/métier/périmètre distincte, approbateur légitime des droits sensibles, délégation nominative limitée, pas de retransmission implicite, conflit de décisions visible. Recettes G13–G17/G51. |
| L03 — C1 | Unique Propriétaire compromis ; utilisateur perd son second facteur ; session expire à J-1. | Choix impossible entre conserver l'attaquant et violer OWN-01 ; support invente une autorité ; travail perdu. | R03/A02 : récupération prouvée, suspension et réattribution tracées, sauvegarde avant expiration ; traiter explicitement l'exception D. G18–G20. |
| L04 — C1 | Responsable d'offre répond seulement à la candidature, à deux lots et à plusieurs tours. | Prix demandé trop tôt, offre d'un lot utilisée pour l'autre, porte globale faussement verte. | R01/R04 : phase/lot/tour/version ; état de travail distinct de décision/remise/résultat ; non-applicabilité motivée des portes. G37/G38, E03/E06/E08. |
| L05 — C1 | Patron accepte le risque d'une visite obligatoire absente ; un rectificatif suit son P5. | Un GO interne masquerait une condition non remplie ou autoriserait une version différente. | R05/A03 : B0/B1/B2, exigences non levées par acceptation de risque seule, dérogation bornée, invalidation ciblée et conservatrice si impact inconnu. G02/G03/G10/G30/G51. |
| L06 — C1 | Métreur importe 120 de vente et 100 de coûts ; DAF compare « 20 % » à un plancher calculé sur vente. Équipe déjà mobilisée ailleurs. | Décision de marge fausse ; coût absent converti en zéro ; engagement impossible ou trésorerie inconnue déclarée acceptable. | R09/A05 : assiette explicite, couverture et hypothèses, unités/scénarios ; minimum de charge/capacité/cash sans comptabilité. G04/G39–G42, E09. |
| L07 — C1 | Chargé d'études reçoit XLS protégé, PDF scanné et XLSX avec lignes masquées/formules. | Document conservé confondu avec document lu ; total ou format contractuel altéré. | R06/A04 : conserver/lire/éditer distincts, formats et tailles qualifiés, contrôle aller-retour, parcours manuel explicite ; échec visible sans faux « complet ». G05–G09/G40, E04/E10. |
| L08 — C1 | Administratif prépare candidature ; cotraitant n'a pas donné mandat ; visite exigée ; question acheteur sans réponse. | Pièces cumulées à tort, signature au mauvais nom, exigence non satisfaite. | R07/R10 : exigences conditionnelles selon procédure/phase/personne/lot, DUME et formulaires appropriés, pouvoir et signature distincts, preuve visite/Q&A. G10/G21/G37. Sources 1–4. |
| L09 — C1 | Opérateur joint un reçu sans liste de fichiers, oublie un lot, ou redépose uniquement une pièce corrigée. | « Remise réussie » et complétude prouvée à tort ; perte d'offre. | R11 : manifeste exact, P5 lié à version, niveaux de preuve et incohérences, nouvelle remise complète et nouveau reçu, copie de sauvegarde séparée. G30–G35. Sources 1/5/7. |
| L10 — C1 | Conducteur reçoit l'affaire gagnée avec un engagement levage non budgété ; négociation ou commande privée change le périmètre. | Rupture entre promesse vendue et lancement ; faux accord contractuel. | R12 : résultat par lot, versions négociées, écart commande/offre visible, transfert accepté avec réserves et responsables, P7 distinct d'un ordre de service. G23/G36/G38, E12. |
| L11 — C1 | Propriétaire sans droit Direction demande export intégral ; départ client en litige ; support regarde un DCE contenant prix d'achat. | Export déborde les droits, suppression sans recours, rétention indéfinie ou support omniscient. | R13/R14/A06/A07 : autorisation par contenu, paquet vérifié, fin de contrat graduée, conservation par finalité, flux/sous-traitants documentés. G24/G45–G48/G52. Sources 15–18/20/23. |
| L12 — C1 | Administratif réutilise une assurance à jour mais hors activité ; utilisateur ne sait pas où corriger une fiche Entreprise ou un droit. Les douze écrans restent des titres. | Dossier présent mais inapplicable ; fonctions V1 sans parcours ; futures décisions laissées au développeur. | R08, E01–E12, S01/S02 : validité et applicabilité distinctes, propriétaire de donnée, snapshots ; tous états et acceptations ; prototype et qualification conformément à OWN-12. G43/G44/G49. Sources 10–12/22. |

La criticité C1 porte sur l'existence et l'acceptation du contrat produit. Les tests d'implémentation et de charge se feront ensuite ; un prototype ne peut démontrer une sécurité effective du service. Les promesses commerciales de formats/disponibilité ne doivent cependant pas être présentées comme acquises avant qualification.

### C2 — importants, sans refaire le produit ni bloquer la définition du cœur

| ID | Situation / utilisateur / conséquence | Complément précis ; échéance et source |
|---|---|---|
| L13 — C2 | QSE réutilise un mémoire générique environnement ; critère/condition du DCE non traité. | R07 : ligne par exigence applicable, engagement mesurable/propriétaire/preuve ; contrôler les nouvelles dispositions avec spécialiste. Base de suivi V1, bibliothèque spécialisée V1.x. Source 14 ; G50. |
| L14 — C2 | Responsable à J-2 pense qu'un email « envoyé » a été lu. | R15 : échéance sourcée/fuseau, statut de notification distinct, relais nominatif ; aucune fuite en objet email. Minimum V1, réglages avancés V1.x. G13/G28. |
| L15 — C2 | Conducteur note sur mobile hors réseau ; révocation avant reconnexion. | R15 : états local/en attente/synchronisé, conflit et refus de synchronisation explicites ; valider appareils/parcours pilote. Aucun offline complet ajouté. G27. |
| L16 — C2 | Patron achète une promesse de temps gagné calculée sans baseline. | R12/R16 : temps déclaré avant/après à tâche comparable, couverture sur dénominateur explicite, incidents et abstentions visibles ; pas de marge « sauvée » estimée comme revenu. DEC-10, HYP. |
| L17 — C2 | Responsable achats compare deux devis de périmètres différents. | R10 : périmètre, unités, exclusions, validité, statut ; comparaison manuelle V1. Portail automatisé seulement après preuve de fréquence. Sources 4/13, HYP pour interface. |
| L18 — C2 | Panne BOAMP ou IA ; utilisateur confond panne et absence d'opportunité/risque. | Fraîcheur visible, reprise et saisie/import manuels, fonctions critiques utilisables sans IA. E02 et R13/R15 ; G25/G26. Source 25 pour limites service, HYP pour comportement. |
| L19 — C2 | Équipe support restaure une sauvegarde ; accès révoqué ou demande de suppression ressuscite. | R15/A08 : point de reprise, réconciliation droits/suppressions, état d'incident visible et information client. Les objectifs chiffrés sont à valider avant engagement commercial. G48 ; source 23. |
| L20 — C2 | Commercial marque « gagné » sans notification et REX IA s'incorpore en connaissance validée. | R12/R08 : résultat déclaré/proouvé, motif sourcé, REX humain avant réutilisation. V1 minimal ; analyses portefeuille V1.x. HYP, DEC-02/10. |

### C3 — améliorations différables

| ID | Besoin et conséquence si absent | Proposition et limite |
|---|---|---|
| L21 — C3 | Acheteur répète des tableaux de comparaison ; temps manuel supplémentaire. | Gabarits de consultation V1.x après pilote ; ne justifie pas un portail fournisseur complet. |
| L22 — C3 | Direction compare ses motifs de perte entre affaires ; apprentissage moins rapide. | Analyse de REX consolidée V1.x, seulement sur données validées et suffisamment nombreuses. |
| L23 — C3 | Expert veut personnaliser ses alertes ; bruit restant. | Préférences et regroupements d'alertes après mesure, sans désactiver silencieusement un blocage. |
| L24 — C3 | Commercial veut davantage de sources de veille. | TED V1.x selon DEC-06 ; connecteurs suivants selon contrats/droits et opportunités utiles, pas selon le nombre d'intégrations. |

## D. Décision propriétaire à reconsidérer — motif et preuves

**Une seule remise en question forte : OWN-01, obligation de conserver au moins un Propriétaire actif.** La décision actuelle reste reproduite intégralement et applicable tant que le propriétaire ne l'a pas amendée.

Cas : l'unique Propriétaire est compromis et aucun second titulaire n'est désigné. Maintenir sa session pour respecter « actif » empêche le retrait immédiat des droits ; le supprimer détruit la continuité d'autorité. La CNIL recommande le retrait des accès devenus inappropriés et une procédure d'incident ; elle ne prescrit pas de conserver un compte compromis actif. L'incompatibilité avec OWN-01 est une **inférence de l'audit**, pas une citation de loi imposant un second Propriétaire.[^15][^23]

**Amendement proposé A02, non adopté :** « Une organisation conserve au moins un Propriétaire nominatif désigné. En fonctionnement normal, au moins un Propriétaire est actif. En cas de compromission ou de perte d'accès de l'unique titulaire, son accès peut être suspendu sans supprimer son identité ni son historique. Les actions réservées restent bloquées jusqu'à récupération ou réattribution par la procédure de preuve d'autorité approuvée ; le support n'acquiert pas pour autant l'autorité métier. » Voir R03/G18/G19. La procédure exceptionnelle doit être déterminée avant le gel, avec éléments de preuve organisationnels vérifiables ; deux intervenants SMART AO ne remplacent pas l'autorité du client.

Les autres tensions ne demandent pas de rouvrir les choix F : le P6/P7 minimal existe déjà au §47, leurs versions approfondies restent V1.x ; S01/S02 matérialisent des espaces et fonctions déjà F, sans remplacer les douze écrans ; la mention d'automatisations de plateformes en V1.x n'autorise pas à elle seule le dépôt autonome : DEC-05 exige une décision séparée pour toute automatisation future du geste final. Pas de proposition de SSO V1, de plateforme mutualisée, d'ERP ou de nouveau moteur de chiffrage.

## E. Contrats des écrans et examen des 16 profils

Les [contrats E01–E12](03_CONTRATS_FONCTIONNELS_ECRANS.md) donnent pour chacun les vingt dimensions demandées et les critères d'acceptation. Ils sont utilisables pour le prototypage ; ils ne valent pas validation utilisateur. Les 16 profils demandés ont chacun une ligne « peut faire / voit / ne voit pas / valide ou propose / escalade / erreur et remplacement » dans le [dossier R](02_REGLES_ROLES_ET_RECETTES.md).

Les douze écrans couvrent le travail d'Affaire, pas l'ensemble du SaaS. **S01 Entreprise/Mémoire** est nécessaire pour maintenir assurance, références, personnel, matériel, prix et leur périmètre. **S02 Organisation/accès/données/support** est nécessaire pour invitations, délégations, récupération, partage, export et clôture. Ils prennent place dans les cinq espaces du §10. Ajouter un écran séparé pour chaque visite, question, engagement, notification ou résultat serait prématuré : ces objets ont un parcours dans Synthèse/Réponse/Passation et des panneaux contextuels.

## F. Périmètre V1 proposé, sans déplacement silencieux des F

Fréquences et complexités sont des **estimations qualitatives de l'audit**, à éprouver chez les deux pilotes, pas une enquête de marché ni un chiffrage projet. « Chaque affaire » décrit la nature du flux, pas un taux observé. Base = attente fonctionnelle probable ; Diff. = différenciation potentielle à démontrer. Le coût cité est une complexité relative, sans choix de technologie.

| Fonction / classement | Valeur et fréquence présumée | Risque / différenciation | Dépendances / complexité | Besoin pilotes et limite |
|---|---|---|---|---|
| Identité/MFA/rôles/récupération — V1 indispensable | Accès sûr quotidien | Risque critique ; base | A02, R02/R03 ; forte | Deux pilotes ; aucune identité partagée. |
| Délégations/absence — V1 indispensable | Décider malgré absence ponctuelle | Engagement non autorisé ; Diff. | Périmètres/portes ; moyenne | Simuler absence, pas gestion RH. |
| BOAMP + saisie manuelle — V1 indispensable | Détection récurrente | Fraîcheur/ratés ; base | Conditions de service, E02 ; moyenne | Corpus réel ; aucune promesse de tout le marché. |
| TED — V1.x utile différable | Marchés européens selon cible | Couverture supplémentaire | DEC-06 ; moyenne | Mesurer affaires utiles, hors lancement. |
| Opportunité/Affaire/lot/phase — V1 indispensable | Structure chaque dossier | Confusion périmètre ; base | R01 ; moyenne | Public candidature/offre et privé minimal. |
| Import/inventaire/source/version — V1 indispensable | Chaque DCE | Fausse complétude ; Diff. | Formats A04 ; forte | Cas hostiles avant promesse de couverture. |
| Lecture PDF/scans et formats qualifiés — V1 indispensable selon contrat A04 | Quotidien probable | Omission/altération ; base | R06 ; forte | Limites prouvées, parcours manuel assumé. |
| Édition universelle de tout ancien format — plus tard, prématurée | Occasionnelle variable | Complexité très forte | Corpus montrant besoin | Original conservé + travail externe V1 ; pas promesse universelle. |
| Exigences/critères/visite/Q&A/MIRP — V1 indispensable minimal | Chaque dossier, visite variable | Irrégularité/oubli ; Diff. | Source/phase ; moyenne | Questions envoyées humainement, pas connecteur universel. |
| Mémoire Entreprise administrative — V1 indispensable | Réutilisation récurrente | Pièce expirée/inapplicable ; base | S01/R08 ; moyenne | Entité/activité/date, pas GED généraliste. |
| Personnel/matériel/références minimaux — V1 indispensable | Offre et passation | Promesse non tenable ; Diff. | Droits/propriétaire ; moyenne | Disponibilité déclarée utile ; pas paie ni BIM. |
| Prix importé/rapprochement/couverture — V1 indispensable | Chaque offre chiffrée | Coût oublié ; Diff. | R06/R09/A05 ; forte | Import réel, formules et écarts visibles. |
| Contribution/marge et scénarios minimum — V1 indispensable | Décision économique | Fausse assiette/confidentialité ; Diff. | Coûts couverts ; moyenne | Choisir le libellé exact, jamais résultat comptable implicite. |
| Capacité/trésorerie minimales — V1 indispensable | Chaque décision, profondeur variable | Engagement inexécutable/non financé | R09/A05 ; moyenne | Ressources critiques + flux/hypothèses ; inconnu possible et escaladé. |
| Planification/cash approfondis — V1.x utile différable | Selon volume portefeuille | Risque d'ERP | Données fiables ; forte | Après besoin démontré, pas comptabilité/bancaire automatique. |
| Devis partenaires/groupement/sous-traitance — V1 indispensable minimal | Variable selon lots | Engagement non sécurisé ; Diff. | R10 ; moyenne | Tableau + pièces/statuts ; pas place de marché. |
| Portail fournisseur/consultations automatisées — V1.x utile différable | Fréquence à mesurer | Extension de surface produit | Consentements et contrats ; forte | Seulement friction démontrée ; OWN-09 préservé. |
| Portes/GO/conditions — V1 indispensable | Chaque affaire | Autorité/marge ; Diff. | R02/R04/R05 ; forte | Pas d'auto-GO ni score remplaçant décision. |
| Réponse/candidature/mémoire/cadres — V1 indispensable | Chaque soumission | Pièce/format/engagement faux ; base+Diff. | R06/R07/R08 ; forte | Critères tracés, humain maître de la réponse. |
| Engagements reliés au coût/passation — V1 indispensable | Chaque promesse engageante | Marge d'exécution ; Diff. | R09/R12 ; moyenne | Source/auteur/responsable, pas gestion chantier. |
| Coffre/manifeste/P5/preuve/redépôt — V1 indispensable | Chaque remise | Perte de candidature ; Diff. | R11 ; forte | Acte final humain, formats selon acheteur. |
| Dépôt autonome — plus tard, décision séparée | Gain hypothétique | Engagement externe critique | Nouvelle décision propriétaire | Exclu V1 ; aucune activation future, y compris en V1.x, sans décision séparée selon DEC-05. |
| Tiers ciblés/révocation — V1 indispensable minimal | Selon sous-traitance/conseil | Fuite irréversible après téléchargement | R13/A06 ; moyenne | Paquet exact, durée, destinataire ; pas espace omniscient. |
| IA assistante + mode manuel — V1 indispensable | Répétitif variable | Hallucination/coût/fuite ; base | Sources/droits ; forte | Abstention et panne testées, aucune dépendance à une conversation unique. |
| Mobile compagnon — V1 indispensable | Visites et consultation terrain | Perte photo/note ; base | R15 ; moyenne | Périmètre OWN-10, pas chiffrage mobile complet. |
| Résultat/REX/passation P6/P7 minimum — V1 indispensable | Affaires finies/gagnées | Rupture de cycle ; Diff. | Versions/engagements ; moyenne | Résultat par lot, réserves et accusé interne conducteur. |
| Négociation/P6P7/REX analytiques approfondis — V1.x différable | Selon activité | Dilution du cœur | Minimum V1 fiable ; forte | Pas suppression du minimum pour simplifier. |
| Export/clôture/support/accessibilité — V1 indispensable | Rare mais décisif | Perte/secret/exclusion ; base | A06/A07, S02 ; forte | Parcours observables dès pilotes, pas dette « après MVP ». |
| SSO — V1.x utile différable | Selon taille client | Simplifie comptes | OWN-05 ; moyenne | MFA interne V1 reste requis. |
| ERP, comptabilité, paie, CRM généraliste, BIM complet — hors produit | Besoins réels hors cœur | Dispersion majeure | Multiples métiers ; très forte | Référencer/importer/exporter si besoin, ne pas reconstruire. |

**Retrait de complexité proposé :** pas de score unique de conformité, de note IA de risque prétendant décider, de garantie générale « DCE complet », de synchronisation automatique de tous les systèmes partenaires, ni de formulaires obligatoires identiques à toutes les phases. À l'inverse, droits, reprise, preuve, format et accessibilité ne sont pas des options à retirer pour raccourcir V1.

## G. Recettes métier nouvelles

Les **52 recettes G01–G52**, dans le dossier R, couvrent les cas fournis par le propriétaire et des trous supplémentaires : candidature sans offre, gain partiel par lot, reçu partiel, marge sur mauvaise assiette, assurance hors activité, export par propriétaire sans droit Direction et restauration après révocation. Chaque ligne indique situation, action, résultat observable, acteur, blocage, fonctions restantes, reprise et trace. Elles devront être rejouées sur prototypes pour le parcours, puis sur logiciel pour les garanties effectives. Aucune n'est déclarée passée aujourd'hui.

Priorité pilote : G02/G10/G18/G30–G34/G37/G39/G43/G45/G48/G49/G52, puis tous les autres scénarios pertinents au périmètre garanti. Les scénarios non couverts doivent produire une limite commerciale explicite, pas disparaître du corpus. Un résultat moyen satisfaisant ne compense pas une fuite de marge ou une remise faussement prouvée.

## H. Recherche externe et contre-benchmark

### Ce que les sources françaises changent concrètement

Les sources DILA distinguent candidature et offre, présentent les pièces selon procédure et expliquent le redépôt ; le produit doit donc porter une phase et des exigences conditionnelles, pas une checklist universelle. La dernière offre reçue dans les délais et les règles de remise rendent nécessaire un nouveau paquet complet, une nouvelle autorisation de version si nécessaire et une nouvelle preuve. Une signature n'est pas requise uniformément sur tous les documents à toute phase ; pouvoir interne, signataire et opérateur de dépôt sont trois qualités distinctes.[^1][^2][^3][^5]

Le groupement et la sous-traitance imposent de décrire qui porte quelles prestations, capacités, responsabilités et pouvoirs ; « partenaire » seul ne suffit pas. La vigilance et les assurances montrent qu'une pièce présente et datée ne prouve ni authenticité, ni validité à l'échéance, ni applicabilité à l'activité. Les règles et cas exacts restent attachés au contrat et à la procédure.[^4][^10][^12][^13]

Le régime des CCAG repose sur la référence applicable et les dérogations ; SMART AO ne doit pas injecter un CCAG par défaut pour inventer des obligations. Les dispositions environnementales et sociales évoluées en 2026 justifient des exigences extraites et qualifiées dans chaque DCE, avec engagements vérifiables, plutôt qu'un paragraphe générique de mémoire. **À valider par spécialiste juridique** pour l'applicabilité à la consultation.[^8][^14]

La CNIL conduit à séparer habilitation, journal, durée de conservation, contrat de sous-traitance et flux ; le SaaS dédié ne répond pas à lui seul à ces questions. Les durées suggérées par l'audit sont des hypothèses contractuelles et non des durées légales universelles. RGAA 4.1.2 est le référentiel français affiché lors de la recherche ; la cible WCAG 2.2 AA du cahier reste conservée avec ses compléments. L'assujettissement légal exact et la qualification des usages sous le règlement IA sont **à valider par spécialiste juridique**.[^15][^16][^17][^18][^22][^24]

### Contre-benchmark : déclarations d'éditeurs, non preuves d'efficacité

| Éditeur / périmètre documentaire | Ce qu'il présente publiquement | Attente ou irritant à examiner | Réponse SMART AO proposée / limite de preuve |
|---|---|---|---|
| Spigao — veille, DCE, études/prix | Veille et outils autour des dossiers et du chiffrage/Excel.[^26] | Rechercher puis retraiter manuellement les quantitatifs est un point de friction plausible. | R06/R09 : import exploitable et fidélité source ; ne pas copier un moteur de chiffrage complet. Pas de test d'import effectué chez l'éditeur. |
| Libel — candidature, mémoire, dématérialisation | Préparation de dossiers, pièces, rappels et assistance à la réponse.[^27][^31] | Réutiliser l'administratif et suivre les échéances paraît une attente de base ; usage réel à confirmer. | R07/R08/R11 : applicabilité des pièces et preuve de version ; ne pas se contenter d'un stockage de documents. Gain de temps marketing non repris. |
| Tenderbolt — analyse DCE/GO-NO-GO | Analyse assistée, identification d'exigences et aide à la décision.[^28] | Une synthèse IA seule devient peu différenciante ; fatigue face aux alertes non actionnables, hypothèse à tester. | MIRP relié à source/coût/acteur/porte ; abstention et revue humaine. Aucun taux d'exactitude comparatif démontré. |
| Saqara — entreprises et consultations | Gestion de consultations, lots, échanges et documents.[^29] | La continuité documentaire et la coordination privées méritent un vrai cas pilote. | R10/R12 : parcours privé et partenaires minimaux ; pas de plateforme complète d'achats. Pas de conclusion sur la qualité de son expérience réelle. |
| Once For All — conformité documentaire | Collecte/suivi de documents et échéances.[^30] | Les pièces administratives ne sont pas un simple coffre statique. | S01 : expiration + applicabilité + entité + snapshot ; connecteur seulement après preuve de besoin et droits. Aucun remplacement d'un contrôle juridique spécialisé. |

La présence de ces fonctions sur plusieurs pages est un **signal de marché**, insuffisant pour affirmer qu'elles sont exigées par toutes les PME. Aucun forum ou avis utilisateur n'est transformé en preuve dans cette revue. Les irritants ci-dessus sont HYP, faute d'entretiens ; ils deviennent des questions du pilote.

**Attentes de base à garantir :** récupération/saisie d'opportunité, pièces réutilisables, recherche/source/version, échéances, réponse adaptée et collaboration. **Différenciation défendable à tester :** chaîne continue exigence → coût couvert ou inconnu → décision humaine → version remise prouvée → engagement transmis au chantier, avec secret Direction préservé. Cette chaîne est un choix de positionnement, pas une exclusivité concurrentielle démontrée.

**Innovations à ne pas poursuivre sans preuve :** agents autonomes de soumission, score de conformité opaque, génération massive de mémoires génériques, catalogue de connecteurs sans usage, simulation exhaustive chantier. Le critère est la décision entrepreneur plus fiable, pas le nombre de fonctions visibles.

### Questions de qualification terrain encore nécessaires

Chez le pilote généraliste et le pilote spécialisé : observer un dossier récemment remis, un rejet ou abandon, un devis fournisseur périmé et une passation réelle ; comparer les fichiers originaux et finaux ; identifier qui voit réellement achat/marge, qui signe et qui dépose ; relever la preuve disponible et les causes de reprise ; mesurer les temps sans les reconstruire de mémoire comme une certitude. Inclure au moins un cas privé selon OWN-08, une candidature seule et un gain partiel par lot. Ces observations n'ont pas encore eu lieu ; elles peuvent corriger les hypothèses A04/A05 sans réinventer la vision.

## I. Modifications proposées, localisées et traçables

Les M01–M08 sont des harmonisations éditoriales avec les registres déjà figés, pas de nouvelles décisions métier. M09–M17 ajoutent des exigences proposées P ou qualifications W ; seules les exigences déjà F restent F. La copie consolidée conserve les §§45–47 intégralement.

| ID | Emplacement / problème actuel | Modification proposée | Raison / criticité / source |
|---|---|---|---|
| M01 | En-tête, §§0–2 : socle Owner et statut de copie peu distingués | En-tête WORK REVIEW v0.3, règle de précédence, changelog et A01–A08 ; conserver le mandat original. | Éviter une promotion implicite ; C1 L01 ; LOC-01. |
| M02 | §8.1 « Proposition », P ; §8.2 liste P | Rappeler OWN-01/02/06 figés, séparation compte/métier ; détails de droits en R02/R03 restent P. | Ne pas rouvrir le premier compte ; C1 L01/L02 ; LOC-01. |
| M03 | §9.2 questions MFA/SSO/P5 déjà tranchées | Remplacer par décisions F rappelées et paramètres P restant ouverts. | MFA tous internes, step-up OWN-04, SSO V1.x ; C1 L01/L03 ; LOC-01, 19. |
| M04 | §13.1 « P — DEC-06 à signer » | F DEC-06 : BOAMP V1, TED V1.x ; fraîcheur et repli via R15/E02. | Contradiction interne ; C1 L01 ; LOC-01, 25. |
| M05 | §21.2 P DEC-04 et §21.3 profondeur ouverte | Doctrine F DEC-04/OWN-07 ; remplacer la question de profondeur par paramètres de formats/calcul/capacité/cash R09/A05. | Assiette économique observable ; C1 L01/L06 ; LOC-01, 9. |
| M06 | §25 « P — DEC-05 à confirmer » | F DEC-05/OWN-11, geste final humain toute la V1, automatisation future par décision séparée ; détails R11. | Autorité et preuve distinctes ; C1 L01/L09 ; LOC-01, 1/5/7. |
| M07 | §27 « profondeur V1 doit être arbitrée », P/W | Minimum OWN-08 F ; corpus privé et règles de négociation/commande en qualification W, R12. | Ne pas déplacer le privé hors V1 ; C1 L01/L10 ; LOC-01. |
| M08 | §35 onboarding accompagné ou self-service « à arbitrer » | Accompagné sans inscription libre F OWN-06 ; responsabilités/configuration/données minimales P. | Évite un nouveau parcours commercial ; C1 L01 ; LOC-01. |
| M09 | §§5–8/22/26/32 : objet, délégation et portes incomplètes | Ajouter R01–R05, table P0–P7 et 16 profils, renvois par section dans §54. | Autorité/états/invalidations ; C1 L02–L05 ; LOC-01, 15/23. |
| M10 | §§14–18/23 : fidélité sans qualification, candidature/visites/Q&A partiels | Ajouter R06/R07 et tests G01–G11/G37/G40/G50. | Pas de fausse complétude ou formulaire universel ; C1 L07/L08 ; 1–3/14. |
| M11 | §§5.2/15/36 : Mémoire sans cycle précis de validité | Ajouter R08 et S01 : type, entité, activité, validité, propriétaire, confidentialité et snapshot. | Une assurance à jour peut être inapplicable ; C1 L12 ; 10–12/15. |
| M12 | §§19–21/24 : économie et partenaires | Ajouter R09/R10 et A05, plafonner V1 au minimum §F. | Protéger marge sans logiciel universel ; C1 L06/L08 ; 4/9/13, HYP calcul. |
| M13 | §§25–27/47 fin de cycle | Ajouter R11/R12 : signature, preuve graduée, redépôt, privé, résultat par lot, passation avec réserves. | Pas de réussite externe inventée ; C1 L09/L10 ; 1/4/5/7. |
| M14 | §§7/28–31/37–39 : permissions et gouvernance | Ajouter R13/R14, A06/A07 et S02 : paquet tiers, support, export, clôture, données fournisseurs IA. | Droits transversaux, réversibilité ; C1 L11 ; 15–18/20/21/23/24. |
| M15 | §§9/32–34/39–42 : erreurs et qualification | Ajouter R15/R16, A08 et G : réseau, concurrence, notifications, reprise, accessibilité et protocole pilote. | Les états d'échec font partie du contrat ; C2 sauf effets C1 ; 19/22/23. |
| M16 | §§10–12/49 : écrans sans contrat complet | Ajouter E01–E12 et S01/S02, adoption des critères observable avant gel ; conserver OWN-12. | Ne pas déléguer le produit au prototypeur ; C1 L12 ; LOC-01, 22. |
| M17 | §§41–42/48–49 : justification et validation | Ajouter registre des sources/limites, 52 recettes et conditions de fermeture ; aucune recette déclarée passée. | Distinguer proposition, preuve documentaire et preuve logicielle ; C1 définition / C2 mesures ; H/LOC-01. |

### Registre A01–A08 — décisions demandées pour la future fermeture, pas prises par la revue

| ID | Proposition exacte à accepter/amender | Qui décide / éléments requis | Effet si non tranché |
|---|---|---|---|
| A01 | Adopter harmonisations M01–M08, objet affaire/phase/lot/tour R01, minimum P6/P7 et précédence F sur P. | Propriétaire produit ; exemples candidature seule, privé, gain partiel. | L01/L04/L10 restent ouverts. |
| A02 | Adopter R02/R03, délégations, invitations/sessions/récupération ; amender explicitement OWN-01 selon D ou donner un autre comportement sûr et opérable. Valeurs R03 proposées : invitation 7 jours, inactivité 30 min, session absolue 12 h, step-up lié à action/version 5 min. | Propriétaire + responsable sécurité ; preuve d'autorité client et scénario unique compte compromis. Chiffres HYP, pas exigence ANSSI. | L02/L03 ouverts ; aucune interprétation technique ne règle seule le conflit OWN-01. |
| A03 | Adopter portes R04/R05, B0/B1/B2 et conditions de levée ; définir qui accepte le risque économique dans quel périmètre et les effets d'une modification. | Propriétaire métier, responsables offre/Direction ; revue G02/G10/G30/G51. | L05/L09 ouverts. |
| A04 | Adopter contrat de formats R06, qualification R16 et garantie de volume : proposition PDF texte/scans, DOCX/XLSX qualifiés ; anciens formats conservés avec parcours externe. Hypothèses de test : 500 fichiers, 2 Go/dossier, 200 Mo/fichier, archives 3 niveaux ; mesurer puis accepter/amender avant promesse. | Propriétaire + pilotes ; corpus représentatif, seuils compatibles besoin/coût ; futur cahier technique démontre faisabilité. | L07 ouvert ; aucun « tous formats » vendu. |
| A05 | Adopter calcul R09 : contribution et taux sur vente HT couverte, distinguer taux sur coût ; coût inconnu ≠ zéro ; minimum capacité/trésorerie et décisions sous hypothèse. | Patron/DAF/métreur ; exemple 120/100 et vrai chiffrage pilote. | L06 ouvert ; métrique « marge » non normalisée. |
| A06 | Adopter R13 : autorité par contenu, destinataire vérifié, paquet externe exact révocable ; défaut proposé 7 jours, support exceptionnel 1 h ; partage financier seulement avec autorité adéquate. | Propriétaire + autorité Direction + sécurité ; G24/G45/G46/G52. | L11 ouvert ; les durées sont P, pas règle propriétaire actuelle. |
| A07 | Adopter matrice de finalités/droits/export R14 et faire qualifier durées/contrats/flux. Hypothèses proposées : réversibilité 30 jours, lien export 7 jours, purge sauvegardes ≤90 jours, journaux 12 mois sauf justification. | Propriétaire + spécialiste juridique + responsable de service ; catégories, litiges, prestataires et territoires documentés. | L11 ouvert ; aucune durée universelle ni promesse de résidence déduite. |
| A08 | Adopter contrats d'écrans/états R15/R16 et plan de qualification ; objectifs de reprise proposés perte maximale 1 h / rétablissement 4 h à faire confirmer avant engagement commercial. Faire qualifier accessibilité et usages IA selon cadre applicable. | Propriétaire + responsable service + pilotes ; prototype OWN-12, objectif réaliste et périmètre de preuve. | L12 reste ouvert si contrats/parcours non adoptés ; objectifs commerciaux et mesures encore à qualifier. |

Les dossiers R/E détaillent des comportements recommandés, y compris des valeurs par défaut. **Aucune valeur chiffrée nouvelle n'est une prescription juridique ni une décision F.** Toute acceptation doit identifier l'approbateur, la date, le texte accepté, les amendements et les preuves ; un tableau rempli par l'auditeur ne suffit pas. Pour une règle dépendant d'une qualification juridique, employer explicitement « À valider par spécialiste juridique » jusqu'à conclusion tracée.

## J. Copie consolidée et limite de son autorité

La v0.3 conserve le texte des décisions DEC-01–11, OWN-01–13 et du périmètre §47. Elle corrige les statuts anciens, puis ajoute un changelog, les arbitrages, les règles, rôles, recettes, contrats et sources. L'amendement OWN-01 reste une proposition identifiable ; il ne remplace pas la phrase propriétaire. Les nouvelles annexes sont P/W selon leur nature, même lorsqu'elles utilisent le langage normatif « doit » pour décrire le comportement proposé.

Le prochain acte utile est une revue propriétaire des huit arbitrages et douze C1 sur des exemples, suivie du prototype prévu. Le livrable de cette mission est prêt à cette revue ; il n'est ni une acceptation des propositions, ni une preuve de conformité, ni une autorisation de développement du nouveau cœur.

## Références citées

[^1]: [Remettre la réponse et échanger avec l'acheteur](https://entreprendre.service-public.gouv.fr/vosdroits/F32106). Type, date et limites : registre des sources du dossier, entrée 1.
[^2]: [Préparer le dossier de candidature](https://entreprendre.service-public.gouv.fr/vosdroits/F32144). Type, date et limites : registre des sources du dossier, entrée 2.
[^3]: [Préparer le dossier offre](https://entreprendre.service-public.gouv.fr/vosdroits/F32154). Type, date et limites : registre des sources du dossier, entrée 3.
[^4]: [Groupement et sous-traitance](https://entreprendre.service-public.gouv.fr/vosdroits/F32137). Type, date et limites : registre des sources du dossier, entrée 4.
[^5]: [R2151-6](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000037730533). Type, date et limites : registre des sources du dossier, entrée 5.
[^8]: [Cahiers des clauses administratives générales et techniques](https://www.economie.gouv.fr/daj/commande-publique/reglementation-de-la-commande-publique/cahiers-des-clauses-administratives). Type, date et limites : registre des sources du dossier, entrée 8.
[^10]: [Obtenir une attestation de vigilance](https://entreprendre.service-public.gouv.fr/vosdroits/F31422). Type, date et limites : registre des sources du dossier, entrée 10.
[^12]: [Modèle d'attestation décennale](https://entreprendre.service-public.gouv.fr/vosdroits/R44868). Type, date et limites : registre des sources du dossier, entrée 12.
[^13]: [Recourir à la sous-traitance](https://entreprendre.service-public.gouv.fr/vosdroits/F36261). Type, date et limites : registre des sources du dossier, entrée 13.
[^14]: [Considérations environnementales et sociales : nouvelles exigences](https://www.economie.gouv.fr/daj/considerations-environnementales-et-sociales-dans-les-marches-publics-publication-de-fiches-pratiques-pour-repondre-aux-nouvelles-exigences-de-la). Type, date et limites : registre des sources du dossier, entrée 14.
[^15]: [Gérer les habilitations](https://www.cnil.fr/fr/securite-gerer-les-habilitations). Type, date et limites : registre des sources du dossier, entrée 15.
[^16]: [Tracer les opérations](https://www.cnil.fr/fr/securite-tracer-les-operations). Type, date et limites : registre des sources du dossier, entrée 16.
[^17]: [Gérer la sous-traitance](https://www.cnil.fr/fr/securite-gerer-la-sous-traitance). Type, date et limites : registre des sources du dossier, entrée 17.
[^18]: [Durées de conservation](https://www.cnil.fr/fr/passer-laction/les-durees-de-conservation-des-donnees). Type, date et limites : registre des sources du dossier, entrée 18.
[^22]: [RGAA](https://accessibilite.numerique.gouv.fr/). Type, date et limites : registre des sources du dossier, entrée 22.
[^23]: [Gérer les incidents et violations](https://www.cnil.fr/fr/securite-gerer-les-incidents-et-les-violations). Type, date et limites : registre des sources du dossier, entrée 23.
[^24]: [Questions-réponses règlement IA](https://cnil.fr/fr/entree-en-vigueur-du-reglement-europeen-sur-lia-les-premieres-questions-reponses-de-la-cnil). Type, date et limites : registre des sources du dossier, entrée 24.
[^26]: [Présentation du produit](https://www.spigao.com/). Type, date et limites : registre des sources du dossier, entrée 26.
[^27]: [Logiciel de réponse et mémoire technique](https://www.libel.fr/logiciel-reponse-appel-offres-memoire-technique/). Type, date et limites : registre des sources du dossier, entrée 27.
[^28]: [Analyse d'appel d'offres et GO/NO-GO](https://www.tenderbolt.ai/fr/features/analysis). Type, date et limites : registre des sources du dossier, entrée 28.
[^29]: [Solutions pour entreprises du bâtiment](https://saqara.com/logiciel/entreprise-batiment). Type, date et limites : registre des sources du dossier, entrée 29.
[^30]: [Conformité documentaire](https://onceforall.fr/solutions/conformite/). Type, date et limites : registre des sources du dossier, entrée 30.
[^31]: [Dématérialisation mode d'emploi](https://www.libel.fr/dematerialisation-candidature-appel-offres/). Type, date et limites : registre des sources du dossier, entrée 31.
