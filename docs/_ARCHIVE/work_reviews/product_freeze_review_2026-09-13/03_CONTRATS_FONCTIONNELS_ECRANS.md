# SMART AO — Contrats fonctionnels des écrans

## E. Portée et invariants communs

Proposition v0.3 à valider par le propriétaire, à utiliser ensuite pour le prototypage. Les 12 écrans de OWN-12 sont conservés. Ce document ne constitue ni une maquette graphique, ni une spécification d'architecture, ni une recette déjà exécutée. Référence des règles : R01–R16 dans `02_REGLES_ROLES_ET_RECETTES.md` ; référence des essais : G01–G52 du même fichier.

**C00 — applicable à tous les écrans** : l'identité de l'entreprise active et le périmètre sont visibles ; droits appliqués avant recherche/affichage/calcul IA/export, pas seulement au bouton ; aucune donnée d'une autre entreprise. Une information porte son état de preuve et sa version. Une action non aboutie n'est pas présentée comme réussie. Les brouillons confirmés sont récupérables après reconnexion ; un conflit conserve les deux contributions. Une alerte persistante critique ne disparaît pas avec la fermeture d'une notification. Toute décision engageante garde auteur habilité, portée, heure, contexte et motif.

**Accessibilité commune A11Y** : clavier, ordre de focus cohérent, libellés et erreurs associés, annonces de progression non envahissantes, contraste et zoom/reflow, alternative textuelle aux graphiques et au glisser-déposer, absence de dépendance à la couleur. Cible WCAG 2.2 AA avec référentiel français courant et complément explicite ; voir R16.[^22]

**États distincts** : « vide » = absence réelle de donnée dans un périmètre autorisé ; « non accessible » = droits insuffisants sans fuite de contenu ; « partiel » = données disponibles avec exclusions ; « erreur » = échec identifié ; « bloqué » = action interdite et voie de sortie indiquée. Chaque écran expose ces états, sans remplacer un résultat inconnu par zéro.

## E01 — Accueil Patron

| Champ | Contrat |
|---|---|
| Rôles | Patron principal ; vue « Mon travail » du responsable/expert limitée à ses tâches, sans synthèse Direction. |
| Question métier | Quelles décisions ou échéances exigent mon attention aujourd'hui ? |
| Données indispensables | Affaires autorisées, responsables, délais absolus, portes ouvertes, rectificatifs, conditions GO, preuves expirantes, incidents et fraîcheur. |
| Information prioritaire | Échéance menaçante et blocage critique, avant volume d'affaires ou production IA. |
| Action principale | Ouvrir la décision ou le blocage prioritaire dans son contexte exact. |
| Actions secondaires | Filtrer par responsable/période, affecter une action, consulter source, ouvrir suppléance. |
| Décisions autorisées | Prise en charge/affectation ; décision P renvoyée au contrat E08/E11, jamais validation en masse aveugle. |
| Informations masquées | Affaires restreintes hors portée, chiffres Direction de la vue collaborateur ; aucun agrégat permettant leur déduction. |
| Source / preuve | Chaque alerte ouvre l'événement, la pièce/version ou la condition dont elle dépend. |
| État vide | « Aucune Affaire accessible / aucune action dans ce filtre », avec création ou vue sans filtre si autorisée. |
| État normal | Alertes triées avec date source, responsable et prochaine action ; trois dimensions Temps, Préparation prouvée, Risque sans score opaque. |
| Traitement en cours | Dernier état confirmé visible, période de calcul annoncée ; aucune validation créée par le rafraîchissement. |
| Résultat partiel | Liste des sources ou Affaires non actualisées, sans les faire passer pour sans risque. |
| Erreur | Message par bloc indisponible et dernière actualisation ; les autres blocs restent lisibles. |
| Blocage critique | P5 invalide ou absence de décideur affichée avec chemin vers traitement, jamais masquée par filtre personnel par défaut. |
| Reprise | Réactualisation ciblée ; prise en charge conservée, doublons regroupés et aggravations visibles. |
| Action IA | Briefing sourcé des états existants, proposition de priorités ; aucun risque ou fait nouvellement « validé ». |
| IA indisponible | Même liste de faits, échéances et actions, sans briefing rédigé. |
| Mobile | Consultation des alertes et tâches ; décision sensible renvoie vers parcours explicitement pris en charge, pas un bouton aveugle. |
| Accessibilité | A11Y ; alertes en texte, trois dimensions lisibles sans graphique ; pas de compte à rebours seul. |

**Acceptation** : E01-A, un rectificatif invalidant P5 apparaît avec Affaire/lot/version et source ; E01-B, un expert ne peut obtenir ni montant ni nombre d'Affaires interdites ; E01-C, panne IA et email ne retirent aucune alerte factuelle. Recettes G02, G25, G52.

## E02 — Radar

| Champ | Contrat |
|---|---|
| Rôles | Commercial, responsable d'offre, Patron et délégataire P0. |
| Question métier | Quelles opportunités publiées dans la source surveillée correspondent à notre recherche ? |
| Données indispensables | Avis BOAMP, référence, acheteur, objet, localisation, lots disponibles, date de publication/modification, délais, URL, critères de filtre et dernière collecte réussie. |
| Information prioritaire | Pertinence explicable et délai utile, avec limites de couverture de la veille. |
| Action principale | Ouvrir une opportunité à qualifier. |
| Actions secondaires | Rechercher, filtrer, sauvegarder recherche, suivre, écarter avec motif, saisir une invitation manuelle. |
| Décisions autorisées | P0 uniquement par habilité ; le classement ne décide pas GO/NO-GO. |
| Informations masquées | Motifs commerciaux restreints et références à Affaires non autorisées. |
| Source / preuve | Avis BOAMP et version/date collectée ; la publication d'un avis n'est pas la réception du DCE. |
| État vide | Aucun résultat pour critères/date/source affichés ; proposer élargissement sans supprimer silencieusement les filtres. |
| État normal | Résultats explicables, lien source, suivi, doublons/avis liés regroupés sans perte de version. |
| Traitement en cours | Recherche/collecte en cours et portée ; résultats déjà acquis conservés. |
| Résultat partiel | Source ou période non couverte ; total connu distinct du total inconnu. |
| Erreur | Panne BOAMP explicite, dernier succès daté, saisie manuelle disponible. |
| Blocage critique | Conversion d'une opportunité annulée ou périmée exige avertissement et confirmation de son état ; pas d'Affaire active créée silencieusement. |
| Reprise | Nouvelle collecte puis rapprochement des références, aucun doublon d'Affaire au double clic. |
| Action IA | Expliquer correspondance métier/territoire, proposer critères ; ne supprime pas un résultat seul. |
| IA indisponible | Recherche par champs et filtres déterminés, consultation de l'avis. |
| Mobile | Liste courte et suivi ; paramétrage approfondi sur poste d'étude. |
| Accessibilité | A11Y ; libellés de filtres, indication de résultats actualisés et navigation clavier. |

**Acceptation** : E02-A, panne affiche date du dernier succès et ne dit pas « à jour » ; E02-B, chaque résultat explique ses critères ; E02-C, répéter conversion ne crée pas deux dossiers. BOAMP seul en V1, TED V1.x.[^25] G26.

## E03 — Fiche Opportunité

| Champ | Contrat |
|---|---|
| Rôles | Commercial/responsable préparent ; Patron ou délégataire P0/P1 décide. |
| Question métier | Devons-nous investir du temps dans cette consultation et sur quels lots ? |
| Données indispensables | Identité candidate, source/invitation, client/acheteur, procédure et phase, lots visés, dates, première éligibilité, responsable, charge d'étude estimée et inconnus. |
| Information prioritaire | Périmètre, date limite, incompatibilité connue, prochaine action. |
| Action principale | Soumettre ou décider l'ouverture P1. |
| Actions secondaires | Joindre invitation, modifier périmètre préparatoire, affecter responsable, suivre, écarter avec motif. |
| Décisions autorisées | Cibler et ouvrir selon habilitation ; aucun GO économique ou engagement commercial externe implicite. |
| Informations masquées | Motifs privés Direction, enveloppes financières ou notes non autorisées. |
| Source / preuve | Avis/invitation et document fixant les dates ; chaque saisie manuelle est attribuée. |
| État vide | Formulaire minimal public/privé avec inconnus permis et exemple anonymisé séparé des dossiers réels. |
| État normal | Qualification et décision courante, prochaine action, lien vers Affaire liée. |
| Traitement en cours | Import de l'invitation ou recherche de doublon, sans création définitive prématurée. |
| Résultat partiel | Acheteur/phase/lot/date manquants identifiés ; dossier préparatoire permis, remise non prête. |
| Erreur | Échec de conversion sans perte de pièces ni fausse confirmation. |
| Blocage critique | Entreprise candidate/périmètre non identifié ou décideur absent interdit la décision dépendante. |
| Reprise | Retrouver la conversion déjà aboutie ou recommencer depuis les données conservées. |
| Action IA | Proposer champs et questions de qualification, à confirmer. |
| IA indisponible | Saisie manuelle et consultation directe des pièces. |
| Mobile | Consultation, note et suivi ; ouverture simple possible si champs et preuve visibles. |
| Accessibilité | A11Y ; aucun champ obligatoire caché, erreurs regroupées et liées. |

**Acceptation** : E03-A, invitation privée peut créer un dossier sans BOAMP ; E03-B, candidature seule ne réclame pas une offre de prix ; E03-C, NO-GO conserve motif/historique et réouverture explicite. G23, G37.

## E04 — Import DCE

| Champ | Contrat |
|---|---|
| Rôles | Responsable et contributeur autorisé ; tiers via paquet de dépôt limité distinct. |
| Question métier | Qu'avons-nous reçu et quelle part peut réellement être étudiée ? |
| Données indispensables | Origine/date/canal, version reçue, fichiers/archives, formats, tailles, état de contrôle, périmètre lot/phase et profil de prise en charge. |
| Information prioritaire | Pièces non reçues/non lues et anomalies, avant la synthèse générée. |
| Action principale | Importer puis vérifier l'inventaire de réception. |
| Actions secondaires | Fournir complément, relier rectificatif, expliquer doublon, annuler/reprendre traitement, demander copie autorisée. |
| Décisions autorisées | Confirmer inventaire/source/version ; pas certifier conformité globale ou absence de danger par clic. |
| Informations masquées | Pièces hors habilitation et contenu en quarantaine ; tiers ne voit que ses dépôts. |
| Source / preuve | Originaux et provenance conservés ; chaque dérivé est relié à l'original. |
| État vide | Formats/limites affichés avant transfert, sélection fichier accessible sans glisser-déposer. |
| État normal | Inventaire confirmé, reçus/analysables/non lus distincts et prochaines actions. |
| Traitement en cours | Progression par réception/contrôle/lecture, annulation sûre ; aucune mention « analyse terminée » prématurée. |
| Résultat partiel | Pages, feuilles, archives ou pièces non traitées nommées ; autres résultats accessibles. |
| Erreur | Motif exploitable par fichier et état de réception réel ; travail antérieur conservé. |
| Blocage critique | Contenu dangereux isolé ; exigences critiques dépendantes non validables. |
| Reprise | Reprendre éléments en échec sans redoubler les pièces confirmées ; remplacement versionné. |
| Action IA | Classement et suggestions de pièces annoncées absentes, explicitement révisables. |
| IA indisponible | Inventaire, contrôle des fichiers et classement/revue manuels ; extraction IA différée. |
| Mobile | Photos/constats de visite, pas import massif garanti en réseau dégradé. |
| Accessibilité | A11Y ; progression annoncée, sélection alternative, liste textuelle des erreurs. |

**Acceptation** : E04-A, un fichier illisible empêche le libellé « dossier entièrement lu » ; E04-B, archive limitée expose les éléments exclus ; E04-C, document hostile n'exécute aucune action. G01, G05–G09, G29.

## E05 — Explorateur DCE

| Champ | Contrat |
|---|---|
| Rôles | Responsable, chargé d'études, métreur, QSE et autres experts sur périmètre. |
| Question métier | Où se trouve l'information qui fonde cette exigence, et quelle version s'applique ? |
| Données indispensables | Arborescence, versions, lots, type de pièce, couverture de lecture, recherche, extrait localisé et exigences liées. |
| Information prioritaire | Version consultée et limitation de lecture ; alerte si version dépassée. |
| Action principale | Ouvrir une source et créer/contrôler l'exigence reliée. |
| Actions secondaires | Rechercher, comparer versions, annoter, signaler contradiction/manque, télécharger original admis. |
| Décisions autorisées | Validation de lecture/extraction par habilité ; aucune résolution juridique automatique. |
| Informations masquées | Documents, titres, extraits et résultats de recherche interdits par droits. |
| Source / preuve | Page ou feuille/cellule, contexte et fichier exact ; lien indisponible signalé. |
| État vide | Aucun document reçu : lien E04 ; recherche vide distincte de contenu non lu. |
| État normal | Liste et extrait, portée des résultats, accès à la version courante et historique. |
| Traitement en cours | Documents en lecture identifiés, recherche limitée aux contenus disponibles. |
| Résultat partiel | Extrait disponible mais tableau/plan non exploitable ; conclusion interdite sur cette portion. |
| Erreur | Aperçu impossible : original contrôlé téléchargeable si droit, message de limitation. |
| Blocage critique | Source absente ou nouvelle version non revue empêche validation des conclusions dépendantes. |
| Reprise | Réimporter/relocaliser avec contrôle humain, sans remapper silencieusement une citation historique. |
| Action IA | Extraire/expliquer passage, proposer liens et contradictions avec références. |
| IA indisponible | Navigation, recherche disponible hors conversation, annotations et liens manuels. |
| Mobile | Lecture ciblée, photo/annotation ; tableau large accessible sans prétendre remplacer le poste d'étude. |
| Accessibilité | A11Y ; extrait textuel accessible identifié comme dérivé ; alternative à sélection visuelle d'une zone. |

**Acceptation** : E05-A, toute exigence critique ouvre sa version exacte ; E05-B, pas de résultat pour une pièce interdite ; E05-C, même nom de fichier nouveau conserve l'ancien. G03, G06, G52.

## E06 — Synthèse Affaire

| Champ | Contrat |
|---|---|
| Rôles | Responsable principal ; Patron et experts avec vues adaptées. |
| Question métier | Où en est cette réponse, quels obstacles restent et qui agit ? |
| Données indispensables | Périmètre/phase/tour, délais, décideurs, couvertures, visite/questions, tâches, décisions, prix autorisé, rectificatifs, résultat et état de remise. |
| Information prioritaire | Blocage courant et prochaine porte applicable, non un pourcentage global. |
| Action principale | Traiter ou affecter l'obstacle qui empêche l'étape suivante. |
| Actions secondaires | Ouvrir registres, partenaires, échéances, journal, réponse, résultat/REX et passation. |
| Décisions autorisées | Affectation et proposition ; P via contrat dédié, enregistrement du résultat externe selon habilitation. |
| Informations masquées | Montants Direction et notes privées ; état « revue financière requise » ne donne pas le plancher. |
| Source / preuve | Provenance de chaque état, pièces de résultat par lot, journal des changements. |
| État vide | Affaire ouverte avec checklist guidée et informations minimales manquantes. |
| État normal | Lots et phases distincts, chemin de réponse, risques et tâches responsables. |
| Traitement en cours | Analyse ou rapprochement en cours ; état confirmé précédent conservé. |
| Résultat partiel | Réponse prête pour certains lots seulement, ou résultat gagné sur un seul lot. |
| Erreur | Bloc indisponible localisé, actions non dépendantes utilisables. |
| Blocage critique | Pas de responsable/décideur, échéance contradictoire ou porte invalidée empêche progression correspondante. |
| Reprise | Réaffectation ou actualisation ciblée, sans effacer les décisions. |
| Action IA | Synthèse factuelle et suggestion de prochaine action, avec état de preuve. |
| IA indisponible | Tableaux structurés, checklists et actions manuelles. |
| Mobile | Mon travail, visite, notes et statuts de synchronisation ; pas modification économique complexe. |
| Accessibilité | A11Y ; étapes textuelles, lecture par lot, aucun diagramme seul. |

**Acceptation** : E06-A, phase candidature seule suivie d'offre garde deux échéances ; E06-B, résultat partiel ne passe pas toute l'Affaire en gagné ; E06-C, changement responsable conserve toutes les actions ouvertes. G13, G37, G38.

## E07 — Registre MIRP

| Champ | Contrat |
|---|---|
| Rôles | Études, métreur, QSE, responsable ; Patron pour acceptation critique. |
| Question métier | Qu'est-ce qui manque pour défendre notre prix et notre décision ? |
| Données indispensables | Inconnus/contradictions/hypothèses, source, lot, impact coût/délai/capacité, responsable, action, échéance, criticité et porte dépendante. |
| Information prioritaire | Inconnus qui empêchent P3/P5 et contradictions non résolues. |
| Action principale | Traiter un point par preuve, question, visite ou hypothèse bornée soumise. |
| Actions secondaires | Affecter, regrouper doublons avec liens, filtrer, consulter prix, historique et dépendances. |
| Décisions autorisées | Expert valide sa revue ; Patron/délégataire accepte risque/hypothèse critique selon R05. |
| Informations masquées | Montant de provision ou exposition Direction ; avis expert utile sans révélation du scénario global. |
| Source / preuve | Sources opposées pour contradiction ; origine et validateur pour hypothèse ; absence explicitée pour inconnu. |
| État vide | « Aucun point enregistré », jamais « aucun risque » si couverture non terminée. |
| État normal | Chaque ligne possède propriétaire et prochaine action ; état ouvert/traité/accepté sous condition/supersédé. |
| Traitement en cours | Propositions d'analyse distinctes du registre validé. |
| Résultat partiel | Impact connu qualitativement, montant non estimé ; pas de zéro implicite. |
| Erreur | Échec d'analyse/citation ; édition manuelle possible si droits. |
| Blocage critique | Condition dépassée ou source manquante laisse porte concernée bloquée. |
| Reprise | Nouvelle preuve ou décision remplace le traitement courant en gardant l'historique. |
| Action IA | Propose point, impact et question ; aucune clôture ou acceptation autonome. |
| IA indisponible | Création, lien documentaire, affectation et décision manuels. |
| Mobile | Constats et preuves de visite enrichissent les points après synchronisation confirmée. |
| Accessibilité | A11Y ; filtres clavier, criticité en texte, colonnes masquables sans perdre les blocages. |

**Acceptation** : E07-A, « hypothèse acceptée » reste différente de « fait prouvé » ; E07-B, condition échue rouvre la porte ; E07-C, ajout pièce déclenche revue des points dépendants. G01–G04, G51.

## E08 — Décision GO/NO-GO

| Champ | Contrat |
|---|---|
| Rôles | Patron/délégataire P2/P3 principalement ; responsable prépare, experts apportent avis. |
| Question métier | Autorisons-nous cette étape, sur quel périmètre et sous quelles conditions ? |
| Données indispensables | Porte, lots/phase/version, faits, inconnus, scénarios autorisés, risques, capacité, trésorerie, conditions et habilitation du décideur. |
| Information prioritaire | Motif décisif et risques non levés, séparés des bénéfices attendus. |
| Action principale | Enregistrer GO, GO sous conditions, ATTENTE, NO-GO ou ABANDON motivé. |
| Actions secondaires | Demander complément, consulter preuves, inviter avis, désigner revue, superséder décision antérieure. |
| Décisions autorisées | Uniquement portes/périmètres délégués ; P5 exige le Coffre exact et son step-up. |
| Informations masquées | Avis Direction et scénarios financiers pour contributeurs non habilités ; résultat communicable séparé du motif privé. |
| Source / preuve | Dossier de décision figé avec sources/version et liste explicite des inconnus acceptés. |
| État vide | Dossier non soumis, informations à rassembler et prochain responsable. |
| État normal | Décision actuelle et historique, conditions, responsables et dates de revue. |
| Traitement en cours | Préparation de synthèse ou enregistrement : attendre confirmation avant statut validé. |
| Résultat partiel | Avis manquant, capacité/trésorerie non démontrée ; arbitrage borné seulement selon R05. |
| Erreur | Échec d'enregistrement : décision non confirmée ; rechercher opération avant répétition. |
| Blocage critique | Délégation expirée, version modifiée ou classe B0/B1 applicable non résolue. |
| Reprise | Rafraîchir dossier puis confirmer nouvelle décision ; pas de recyclage automatique du clic initial. |
| Action IA | Expose arguments sourcés et limites ; aucun score final décisionnaire. |
| IA indisponible | Même dossier structuré et décision humaine possible. |
| Mobile | Consultation ; décision seulement dans un parcours qualifié montrant contexte complet, jamais hors ligne. |
| Accessibilité | A11Y ; choix explicites, récapitulatif de portée, confirmation sans minuterie arbitrairement courte. |

**Acceptation** : E08-A, GO sous conditions exige action/preuve de levée/échéance ; E08-B, deux Patrons concurrents ne s'écrasent pas ; E08-C, rôle administrateur ne permet pas de décider. G15, G17, G39, G51.

## E09 — Prix

| Champ | Contrat |
|---|---|
| Rôles | Métreur/études sur couverture ; achats sur devis autorisés ; DAF/Patron sur scénarios sensibles. |
| Question métier | Le chiffrage couvre-t-il le besoin et quelles hypothèses exposent notre contribution et notre financement ? |
| Données indispensables | Bordereau/version, HT/TTC/monnaie/unités, quantités, postes, hypothèses, facteurs non couverts, devis/validités, variante/tranche, coûts et droits, capacité/trésorerie minimales. |
| Information prioritaire | Besoin non couvert, total non fiable ou hypothèse critique ; montant final seulement dans son périmètre. |
| Action principale | Revoir les écarts du chiffrage importé et soumettre le scénario à P3. |
| Actions secondaires | Importer/exporter, lier postes/exigences, consulter devis, saisir scénario borné, comparer variantes séparément. |
| Décisions autorisées | Expert valide rapprochement/quantité ; DAF revue ; Patron ou délégataire accepte scénario. Aucun prix final IA. |
| Informations masquées | Prix achat sensibles, plancher, marge, trésorerie et provisions Direction selon droits ; prévention des déductions par agrégats. |
| Source / preuve | Cellule/ligne du fichier original, offre fournisseur, source exigence et composition du coût. |
| État vide | Profil de formats accepté et import de chiffrage ; pas de tarif universel suggéré. |
| État normal | Couverture et totaux par lot/scénario, formule des indicateurs explicitée. |
| Traitement en cours | Contrôle/import en cours, aucun remplacement de version active avant confirmation. |
| Résultat partiel | Lignes non reconnues, formule non recalculée, coût inconnu ou trésorerie non démontrée. |
| Erreur | Erreur d'unité/structure, précision et emplacement ; original disponible pour correction externe. |
| Blocage critique | P3/P4 dépendantes non validables en cas de total indéterminé, mauvaise version ou risque non traité. |
| Reprise | Corriger mapping ou fichier externe, réimporter, comparer et réexaminer scénario ; aucun double comptage. |
| Action IA | Suggère correspondances et coûts oubliés, ne fabrique ni devis ni quantités vérifiées. |
| IA indisponible | Saisie/mapping/revue et calculs définis restent accessibles ; rapprochement automatique différé. |
| Mobile | Lecture autorisée de synthèse seulement ; travail complet sur poste d'étude. |
| Accessibilité | A11Y ; en-têtes de tableaux, accès clavier par ligne, unités verbalisées et écarts textuels. |

**Acceptation** : E09-A, exemple 120/100 restitue correctement taux sur vente ; E09-B, coût absent ne vaut pas zéro ; E09-C, même équipe occupée et prix expiré apparaissent dans revue P3. G04, G12, G39–G42, G52.

## E10 — Réponse

| Champ | Contrat |
|---|---|
| Rôles | Responsable, administratif, rédacteur/études, QSE ; valideurs par section et Patron P4. |
| Question métier | Avons-nous répondu à chaque exigence de cette phase sans promesse non maîtrisée ? |
| Données indispensables | Checklist candidature/offre par lot, critères/sous-critères, modèle imposé, pièces à produire/obtenir, versions, faits Entreprise, engagements, responsables et statut de revue. |
| Information prioritaire | Pièce/section critique manquante, preuve expirée, engagement nouveau ou dépassement des contraintes acheteur. |
| Action principale | Compléter puis soumettre la réponse en revue de contenu P4. |
| Actions secondaires | Réemployer version validée, télécharger modèle/copie, réimporter, comparer, affecter section, préparer question/partage ciblé. |
| Décisions autorisées | Validation de section déléguée ; déclarations/engagements et P4 par autorité adaptée. |
| Informations masquées | Notes Direction, coûts/marges et données RH inutiles ; sortie acheteur purgée de commentaires internes non destinés. |
| Source / preuve | Chaque fait critique ouvre preuve entreprise/acheteur ou hypothèse ; toutes les sections signalent leur origine et révision. |
| État vide | Liste exigée par la phase et les lots, pas un mémoire générique déjà présenté comme conforme. |
| État normal | Pièces présentes, applicables, revues et incluses distinguées ; sections reliées aux critères. |
| Traitement en cours | Brouillon IA ou export en préparation clairement séparé du document approuvé. |
| Résultat partiel | Section incomplète ou format non qualifié ; tâches de complément créées avec responsable. |
| Erreur | Génération/réimport échoué, original et dernier brouillon conservés. |
| Blocage critique | Attestation tierce inventée, engagement non accepté ou modèle imposé non respecté interdit P4/P5 dépendantes. |
| Reprise | Modifier copie, réimporter, comparer et refaire seulement revues touchées. |
| Action IA | Brouillon fondé sur sources choisies, zones manquantes visibles ; aucune signature ni affirmation de capacité inventée. |
| IA indisponible | Modèles, rédaction manuelle/externe, réemploi validé, checklist et revue. |
| Mobile | Commentaire ou consultation ciblée ; aucune édition complète Word/Excel garantie. |
| Accessibilité | A11Y ; alternatives au glisser-déposer, revue textuelle des modifications, suivi clavier des sections. |

**Acceptation** : E10-A, promesse « sous 2 heures » exige validation et lien passation ; E10-B, DUME n'impose pas artificiellement une liasse cumulative ; E10-C, réimport ne supprime pas les formules/commentaires sans avertissement. G05, G21, G22, G36, G44, G50.

## E11 — Coffre de remise

| Champ | Contrat |
|---|---|
| Rôles | Responsable assemble ; Patron/délégataire P5 autorise ; signataire et opérateur humains identifiés. |
| Question métier | Ce paquet exact est-il autorisé, puis quelle réception pouvons-nous réellement prouver ? |
| Données indispensables | Phase/tour/lots, pièces/version, manifeste, contrôles, P4, signatures/pouvoirs, destinataire/canal, échéance, opérateur, tentative et preuve externe. |
| Information prioritaire | Divergence de version ou blocage, puis délai et état exact de réception. |
| Action principale | Avant remise : autoriser P5 avec step-up ; après geste humain : importer et rapprocher le reçu. |
| Actions secondaires | Ouvrir preuve, exporter paquet exact, consignes plateforme, préparer copie de sauvegarde, nouvelle candidate/redépôt, traiter incohérence. |
| Décisions autorisées | P5 sur paquet exact ; rapprochement humain documenté ; aucune admission juridique ni dépôt autonome. |
| Informations masquées | Tous les éléments Direction non inclus intentionnellement ; opérateur voit le paquet qu'il doit remettre sans tout le contexte financier. |
| Source / preuve | RC/consignes, mandat, pièces signées, manifeste interne et reçu externe distincts. |
| État vide | Aucune candidate ; checklist et retour vers réponse, sans bouton d'autorisation actif. |
| État normal | Candidate/autorisation/tentatives/réception clairement séparées ; historique immuable. |
| Traitement en cours | Assemblage/export/rapprochement ; aucune réussite tant qu'opération non confirmée. |
| Résultat partiel | Reçu pli cohérent mais contenu non rapprochable intégralement, avec limite visible. |
| Erreur | Fichier export incomplet, signature non vérifiée, reçu illisible ou mauvaise consultation ; motif ciblé. |
| Blocage critique | Paquet modifié, mauvaise habilitation, pièce critique absente, canal inconnu ou date incohérente selon R05. |
| Reprise | Nouvelle candidate et autorisation si changement ; collecte de reçu ; incident tracé si remise hors autorisation. |
| Action IA | Aide à lire consignes/reçu et signaler écart ; aucun clic de dépôt, signature ou preuve créée. |
| IA indisponible | Contrôles, revue du manifeste, autorisation humaine, export et rapprochement manuel disponibles. |
| Mobile | Consultation et ajout de preuve simple ; P5 seulement si parcours sensible qualifié, jamais hors ligne. |
| Accessibilité | A11Y ; liste des fichiers lisible, confirmation avec version/destinataire, authentification accessible. |

**Acceptation** : E11-A, modifier un octet/fichier après autorisation invalide l'autorisation de ce nouveau paquet ; E11-B, reçu sans inventaire ne produit pas « contenu intégral vérifié » ; E11-C, redépôt propose paquet complet et nouveau reçu ; E11-D, P5 n'est jamais nommé signature légale. G30–G35.

## E12 — Passation

| Champ | Contrat |
|---|---|
| Rôles | Responsable d'offre prépare ; conducteur prend en charge ; Patron/délégataire P7 accepte ; experts ciblés. |
| Question métier | Le chantier reçoit-il exactement le périmètre vendu, ses engagements et les risques encore ouverts ? |
| Données indispensables | Lot gagné, preuve de résultat/accord, version contractuelle, engagements, planning contractuel, moyens, partenaires, budget autorisé, risques et échéances de preuves. |
| Information prioritaire | Engagement sans responsable, écart contrat/offre ou réserve de prise en charge. |
| Action principale | Soumettre puis accepter la passation avec accusé du destinataire. |
| Actions secondaires | Consulter preuve, affecter risque, noter réserve, exporter dossier chantier, réviser passation, préparer REX. |
| Décisions autorisées | Conducteur accuse réception avec réserves ; Patron/délégataire P7 clôt selon conditions ; aucune émission d'ordre de service implicite. |
| Informations masquées | Notes privées de négociation, marge et RIB sans habilitation ; budget chantier autorisé présenté séparément. |
| Source / preuve | Offre remise, accord/notification, modifications acceptées P6 et pièces de passation versionnées. |
| État vide | Aucun lot gagné prouvé ou aucun dossier assemblé ; indique ce qui manque sans créer chantier fictif. |
| État normal | Engagements affectés, responsables et accusés ; liens aux pièces contractuelles et risques. |
| Traitement en cours | Assemblage du dossier, ancienne édition clairement identifiée. |
| Résultat partiel | Un lot transmis, autre en attente ; réserves et pièces manquantes explicites. |
| Erreur | Export incomplet ou référence inaccessible ; aucune clôture silencieuse. |
| Blocage critique | Engagement non repris/non affecté, version contractuelle contradictoire ou destinataire absent empêche clôture. |
| Reprise | Compléter, arbitrer, créer nouvelle édition et nouvel accusé des changements. |
| Action IA | Préparer synthèse du vendu et comparer offre/contrat, toujours revue. |
| IA indisponible | Assemblage manuel à partir du registre et des documents, accusé et P7 possibles. |
| Mobile | Consultation ciblée terrain, notes et réserves ; état de synchronisation explicite. |
| Accessibilité | A11Y ; checklist textuelle, documents dérivés accessibles et réserve saisissable au clavier. |

**Acceptation** : E12-A, engagement validé repris ou exclusion justifiée et arbitrée ; E12-B, lot perdu absent du périmètre gagné ; E12-C, nouvelle pièce contractuelle rouvre les éléments concernés ; E12-D, aucune clôture ne vaut ordre de démarrage des travaux. G23, G36, G38.

## Les 12 écrans suffisent-ils ?

**Pour le cycle d'une Affaire : oui, avec Résultat/REX dans E06 et Visite/Questions dans E06/E07/E10. Pour tout le SaaS vendu : non.** La Mémoire Entreprise et l'Administration sont déjà des espaces figés §10 ; leurs parcours critiques ne sont pourtant pas couverts par les douze contrats. Les contractualiser ne rajoute pas deux applications ni ne remplace OWN-12.

### S01 — Entreprise / Mémoire Entreprise

Question : quelles preuves pouvons-nous réutiliser, pour quelle société et jusqu'à quand ? Rôles : administratif/propriétaire de contenu, QSE, achats, DAF selon catégorie. Action principale : vérifier/publier une version réutilisable ; secondaires : demander renouvellement, voir Affaires dépendantes, retirer, exporter selon droit. Données : identité/établissement, validité, applicabilité, preuve, propriétaire et sensibilité. Un administrateur de compte n'a pas lecture des documents sensibles.

États : vide = kit minimal identité/assurances/références ; normal = preuves réutilisables par portée ; traitement = import contrôlé ; partiel = validité connue mais applicabilité non vérifiée ; erreur = pièce non lisible ; blocage = pièce expirée/inadaptée pour une exigence ; reprise = nouvelle version et revue des offres ouvertes dépendantes. IA propose métadonnées uniquement ; sans IA, saisie/revue restent disponibles. Mobile : consultation/ajout ciblé, pas dossier RH. A11Y s'applique.

Preuves : fichier/version, organisme, référence de vérification et lieu exact si extraction. Validation : propriétaire de contenu habilité ; dérogation sensible selon R05. Acceptation S01-A : une assurance hors activité ne devient pas applicable par sa date ; S01-B : retirer un CV alerte les offres ouvertes sans modifier les plis historiques ; S01-C : mémoire de démonstration isolée des faits réels. G43–G44.

### S02 — Organisation / Accès / Gouvernance et support

Question : qui peut agir, avec quels droits, et comment garder ou récupérer les données de l'entreprise ? Rôles : Propriétaire et Administrateur pour gestion ; autorité Direction pour droits sensibles ; support exceptionnel séparé. Action principale selon contexte : traiter invitation/délégation/incidence d'accès ; opérations rares guidées pour export, transfert ou fermeture. Données : utilisateurs/statuts, portées, MFA sans secrets, sessions, délégations, responsables, accès support, politique de conservation et demandes de sortie.

États : vide = activation premier compte/MFA ; normal = droits et expirations visibles ; traitement = invitation/export/récupération ; partiel = utilisateur invité non activé ou export limité ; erreur = invitation refusée/export échoué ; blocage = transfert sans successeur, accès sans pouvoir ou fermeture avec export non résolu ; reprise = réémission, procédure de récupération, approbation sensible ou nouveau transfert. Aucun état ne donne accès au contenu en raison du rôle administratif.

Sources/preuves : approbations, identité vérifiée, événements d'accès, manifeste d'export et calendrier de purge. IA facultative pour expliquer les règles à partir de données autorisées ; aucune attribution/récupération/fermeture autonome. Sans IA, parcours identique. Mobile : sécurité personnelle et lecture d'état, opérations complexes sur parcours dédié accessible ; aucun contournement MFA. A11Y couvre aussi les erreurs d'authentification et moyens de secours.

Acceptation S02-A : admin ne s'attribue pas les marges ; S02-B : départ coupe sessions et délégations sans effacer décisions ; S02-C : export complet respecte catégories ; S02-D : révocation support effective ; S02-E : récupération du dernier Propriétaire suit l'arbitrage A02. G14, G17–G20, G24, G45–G48.

Les formulaires connexion/MFA/récupération et le paquet tiers sont des parcours de support de S02/R03/R13, non des nouveaux écrans métier de premier niveau. Leur recette reste obligatoire.

## Références citées

[^22]: [RGAA](https://accessibilite.numerique.gouv.fr/). Type, date et limites : registre des sources du dossier, entrée 22.
[^25]: [CGU du site et service d'alerte](https://www.boamp.fr/telechargements/cms/fichiers/CGU_site_boamp.fr_et_service_d_alerte_BOAMP_2024-10-21.pdf). Type, date et limites : registre des sources du dossier, entrée 25.
