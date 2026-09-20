# SMART AO — Catalogue des écrans & parcours produit
## Surface UX complète V1 — v0.1

**Date : 13 septembre 2026**  
**Statut : CATALOGUE UX DE CONSOLIDATION — à valider visuellement avant Product Freeze v1.0**  
**Source normative : `SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_CONSOLIDATED_v0.4.md`**  
**SHA-256 de la copie source utilisée : `af461cf4782af01575e707d97a724ac1c5d1a5c2229b9ec820010c58a4e05042`**

---

# 0. Rôle du document

Ce catalogue transforme le Cahier directeur Produit & Métier en une **surface UX complète et vérifiable**.

Il ne remplace pas le cahier v0.4 : le v0.4 reste la source de vérité sur le métier, l’autorité, la confidentialité, les portes P0–P7, les preuves et le périmètre V1.

Le présent document répond à une autre question :

> **Quels écrans, vues, parcours, panneaux et états l’utilisateur doit-il réellement voir pour que tout ce qui est écrit dans le cahier existe dans le produit ?**

Décision propriétaire : **ne pas limiter le prototypage aux seuls 12 écrans structurants**. Les 12 écrans E01–E12 restent les pivots du produit, mais la validation avant Product Freeze doit porter sur la **surface fonctionnelle V1 complète**, y compris identité, onboarding, Mémoire Entreprise, administration, partage tiers, erreurs, reprise, mode dégradé et mobile.

---

# 1. Doctrine UX

## 1.1 Navigation principale

La navigation de premier niveau reste :

**Accueil / Opportunités / Affaires / Entreprise / Administration-Paramètres**

DCE, MIRP, prix, partenaires, réponse, remise et passation restent des sous-espaces contextuels ; ils ne deviennent pas des applications séparées.

## 1.2 Une seule identité IA

L’utilisateur voit **SMART AO**, pas une collection d’agents. L’IA intervient comme briefing, explication, rapprochement, suggestion, contrôle ou brouillon. Toute fonction critique garde une voie non conversationnelle.

## 1.3 Autorité et confidentialité

Le titre de poste ne donne pas automatiquement un droit. Chaque prototype doit montrer ce que l’utilisateur peut voir, modifier, proposer, valider, partager ou exporter, ainsi que ce qui reste masqué.

## 1.4 États obligatoires

Tout écran critique prévoit lorsque pertinent : **vide / normal / traitement / partiel / non accessible / erreur / bloqué / à revalider / mode dégradé / reprise**.

Un résultat inconnu n’est jamais zéro.  
Un droit insuffisant n’est jamais « aucune donnée ».  
Une opération non confirmée n’est jamais présentée comme réussie.

---

# 2. Convention du catalogue

| Terme | Sens |
|---|---|
| **SCREEN** | Vue navigable principale ou secondaire |
| **FLOW** | Parcours guidé multi-étapes |
| **PANEL** | Panneau, tiroir ou dialogue contextuel |
| **STATE** | État système ou page de reprise |
| **SHELL** | Structure globale de navigation |
| **RESPONSIVE** | Variante mobile d’une surface existante |

Priorités :

| Priorité | Exigence de prototype |
|---|---|
| **UX-Critical** | Haute fidélité fonctionnelle + principaux états + interactions |
| **UX-Primary** | Prototype visuel complet des états principaux |
| **UX-Support** | Fidélité moyenne, contrat visuel et comportement validés |

---

# 3. Résumé quantitatif

Le catalogue v0.1 contient **104 surfaces UX**.

## 3.1 Par type
| Type | Nombre |
|---|---|
| FLOW | 10 |
| PANEL | 2 |
| RESPONSIVE | 5 |
| SCREEN | 83 |
| SHELL | 1 |
| STATE | 3 |

## 3.2 Par priorité
| Priorité | Nombre |
|---|---|
| UX-Critical | 52 |
| UX-Primary | 43 |
| UX-Support | 9 |

## 3.3 Par domaine
| Domaine | Nombre |
|---|---|
| Accueil | 3 |
| Accès | 8 |
| Administration | 11 |
| Affaires | 3 |
| Après remise | 4 |
| Collaboration | 2 |
| DCE & Preuves | 13 |
| Décision & Prix | 7 |
| Entreprise | 12 |
| Global | 5 |
| Mobile | 5 |
| Onboarding | 4 |
| Opportunités | 4 |
| Partage tiers | 4 |
| Partenaires | 2 |
| Remise | 7 |
| Réponse | 7 |
| Système | 3 |

Ces 104 surfaces ne signifient pas 104 routes web indépendantes. Certaines deviendront des onglets, panneaux, dialogues, assistants guidés ou variantes responsive. Le cahier technique pourra composer ces surfaces, mais il ne pourra pas supprimer une capacité UX validée.

---

# 4. Inventaire complet V1

| ID | Surface | Domaine | Type | Priorité | Rôles principaux | Mission | États / points critiques |
|---|---|---|---|---|---|---|---|
| AUTH-01 | Connexion | Accès | SCREEN | UX-Critical | Tous internes | Authentifier l’utilisateur sans exposer de données métier. | Connexion valide, erreur identifiants, compte suspendu, service indisponible |
| AUTH-02 | Activation d’invitation | Accès | FLOW | UX-Critical | Utilisateur invité | Accepter une invitation nominative, vérifier l’adresse et initialiser le compte. | Invitation valide, expirée, déjà utilisée, rôle/périmètre visibles avant activation |
| AUTH-03 | Enrôlement MFA | Accès | FLOW | UX-Critical | Tous internes | Activer le MFA avant tout accès métier interne. | Enrôlement, moyen de secours, échec, reprise |
| AUTH-04 | Challenge MFA / Step-up | Accès | PANEL | UX-Critical | Utilisateur habilité | Réauthentifier avant P5, export complet, droits sensibles ou fermeture. | Action/version ciblée, délai expiré, cible modifiée, échec |
| AUTH-05 | Récupération d’accès | Accès | FLOW | UX-Critical | Utilisateur / Propriétaire | Récupérer l’accès sans se fonder sur le seul email ni recréer des droits. | Facteur perdu, sessions révoquées, récupération normale, escalade |
| AUTH-06 | Récupération du dernier Propriétaire | Accès | FLOW | UX-Critical | Représentant client / support borné | Traiter l’exception OWN-01 après suspension du dernier Propriétaire compromis. | Preuve d’autorité, refus, double contrôle, journal |
| AUTH-07 | Session expirée / reprise | Accès | STATE | UX-Critical | Tous internes | Masquer les données, réauthentifier et restaurer le dernier travail confirmé. | Brouillon confirmé, local non publié, droits révoqués |
| AUTH-08 | Accès refusé / droit insuffisant | Accès | STATE | UX-Critical | Tous | Expliquer un refus sans révéler l’existence ou le contenu interdit. | Non accessible ≠ vide, demande de droit éventuelle |
| ONB-01 | Bienvenue / confirmation de l’organisation | Onboarding | FLOW | UX-Primary | Premier Propriétaire | Confirmer l’organisation et démarrer sans paramétrage exhaustif. | Entreprise correcte, erreur identité, reprise |
| ONB-02 | Choix du premier chemin | Onboarding | SCREEN | UX-Primary | Propriétaire / Patron | Choisir : importer un DCE, explorer une démo, préparer la Mémoire Entreprise. | Trois parcours, retour possible |
| ONB-03 | Profil entreprise minimal | Onboarding | FLOW | UX-Primary | Propriétaire / Administratif | Saisir seulement les données minimales utiles au premier usage. | Incomplet autorisé, éléments obligatoires explicites |
| ONB-04 | Checklist de démarrage | Onboarding | SCREEN | UX-Support | Propriétaire / Admin | Montrer ce qui reste à configurer sans bloquer la première valeur. | Utilisateurs, MFA, preuves, première Affaire |
| GLB-01 | Shell principal / navigation | Global | SHELL | UX-Critical | Tous internes | Porter les 5 espaces : Accueil, Opportunités, Affaires, Entreprise, Administration. | Organisation active, rôle, recherche, notifications, contexte |
| GLB-02 | Recherche globale | Global | SCREEN | UX-Primary | Selon droits | Retrouver Affaires, documents, exigences, preuves et éléments Entreprise autorisés. | Droits avant résultat, zéro fuite par titre/compteur |
| GLB-03 | Centre de notifications | Global | SCREEN | UX-Primary | Tous internes | Centraliser alertes, échéances, blocages et notifications configurées. | Non lue, prise en charge, regroupement, aggravation |
| GLB-04 | Mes tâches / Mon travail | Global | SCREEN | UX-Primary | Collaborateurs / experts / Patron | Voir les actions dont l’utilisateur est responsable. | Retard, dépendance, délégation, absence, reprise |
| GLB-05 | Profil / préférences personnelles | Global | SCREEN | UX-Support | Tous internes | Gérer profil, préférences non sensibles et facteurs autorisés. | Préférences, sécurité renvoyée vers admin |
| HOME-01 | Accueil Patron | Accueil | SCREEN | UX-Critical | Patron / dirigeant | Répondre : qu’est-ce qui mérite mon attention aujourd’hui ? | Temps, préparation prouvée, risque, rectificatifs, décisions |
| HOME-02 | Accueil Collaborateur / Responsable d’offre | Accueil | SCREEN | UX-Primary | Responsable d’offre | Présenter Affaires, tâches, échéances et obstacles sans données Direction. | Affaires affectées, prochaine action, alertes |
| HOME-03 | Accueil Expert | Accueil | SCREEN | UX-Support | Métreur / QSE / Conducteur / Achats / DAF | Présenter uniquement les contributions et validations attendues dans son périmètre. | Échéances, demandes, contexte borné |
| OPP-01 | Radar BOAMP | Opportunités | SCREEN | UX-Critical | Commercial / Responsable / Patron | Chercher, filtrer et suivre les opportunités avec provenance et fraîcheur. | Panne source, résultat partiel, doublons, critères explicables |
| OPP-02 | Recherches sauvegardées | Opportunités | SCREEN | UX-Support | Commercial / Responsable | Créer, modifier et exécuter des recherches sauvegardées. | Dernière collecte, alerte, désactivation |
| OPP-03 | Fiche Opportunité | Opportunités | SCREEN | UX-Critical | Commercial / Responsable / Patron | Qualifier l’intérêt, les lots et l’effort initial avant ouverture. | P0/P1, inconnus, lot, échéance, source |
| OPP-04 | Créer une opportunité / invitation manuelle | Opportunités | FLOW | UX-Primary | Responsable / Commercial | Créer une opportunité privée ou publique hors Radar. | Source manuelle attribuée, doublon, date inconnue |
| AFF-01 | Portefeuille des Affaires | Affaires | SCREEN | UX-Primary | Selon droits | Lister les Affaires par état, responsable, échéance, lot et prochaine porte. | Filtres, vues enregistrées, confidentialité des agrégats |
| AFF-02 | Synthèse Affaire | Affaires | SCREEN | UX-Critical | Responsable / Patron / experts adaptés | Dire où en est la réponse, ce qui bloque et qui agit. | Phase/tour/lot, couvertures, portes, rectificatifs |
| AFF-03 | Chronologie / journal de l’Affaire | Affaires | SCREEN | UX-Support | Selon droits | Voir événements, versions, décisions, remises et changements de responsables. | Historique immuable, filtres, sources |
| DCE-01 | Import DCE | DCE & Preuves | SCREEN | UX-Critical | Responsable / contributeur | Importer fichiers, dossiers, archives et confirmer l’inventaire reçu. | Limites formats/volumes, progression, erreurs par fichier |
| DCE-02 | Suivi d’ingestion / traitement | DCE & Preuves | SCREEN | UX-Primary | Responsable / contributeur | Suivre réception, contrôle, lecture et reprise sans faux 'terminé'. | Reçu, analysable, non lu, quarantiné, reprise |
| DCE-03 | Explorateur DCE | DCE & Preuves | SCREEN | UX-Critical | Études / métreur / QSE / responsable | Naviguer dans les pièces, versions et extraits sourcés. | Version courante, historique, recherche, portée de lecture |
| DCE-04 | Visionneuse document + source | DCE & Preuves | SCREEN | UX-Critical | Selon droits | Ouvrir le document exact et la localisation probante. | Page/feuille/cellule, extrait, original/dérivé, indisponible |
| DCE-05 | Comparateur de versions / rectificatifs | DCE & Preuves | SCREEN | UX-Critical | Responsable / experts | Comparer versions et comprendre les validations à rouvrir. | Diff, impacts, non interprété, revalidation ciblée |
| DCE-06 | Couverture documentaire | DCE & Preuves | SCREEN | UX-Critical | Responsable / Patron | Distinguer reçu, lu, exigences revues et réponse/prix couverts. | Dénominateurs, exclusions, pièces citées absentes |
| DCE-07 | Registre des exigences | DCE & Preuves | SCREEN | UX-Critical | Responsable / experts | Piloter les obligations avec source, lot, criticité et validation. | Prouvée, incertaine, contradictoire, non supportée |
| DCE-08 | Registre des contradictions | DCE & Preuves | SCREEN | UX-Primary | Responsable / experts / conseil | Conserver les sources en conflit et leur impact sans arbitrage automatique. | Sources opposées, question, avis, résolution |
| DCE-09 | Pièces manquantes / non lues | DCE & Preuves | SCREEN | UX-Primary | Responsable | Rendre visibles les lacunes de réception ou de lecture. | Annoncée absente, protégée, illisible, hors profil |
| DCE-10 | Questions à l’acheteur | DCE & Preuves | SCREEN | UX-Primary | Responsable / Patron selon validation | Préparer, approuver, tracer émission et réponse. | Brouillon, approuvé, émission déclarée/prouvée, impact traité |
| DCE-11 | Visite / jalons terrain | DCE & Preuves | SCREEN | UX-Primary | Responsable / conducteur | Gérer visite obligatoire/facultative, inscription, preuve et constats. | Créneau, remplaçant, attestation, impossibilité, dispense prouvée |
| DCE-12 | Registre MIRP | DCE & Preuves | SCREEN | UX-Critical | Études / métreur / QSE / Patron | Piloter inconnus, hypothèses et contradictions qui empêchent prix/décision. | Action, responsable, impact, porte dépendante |
| DCE-13 | Risques et facteurs de coût | DCE & Preuves | SCREEN | UX-Primary | Responsable / études / métreur / Patron | Relier contraintes techniques/contractuelles aux impacts coût/délai/capacité. | Couvert, inconnu, B1/B2, responsable |
| DEC-01 | Décision GO / NO-GO | Décision & Prix | SCREEN | UX-Critical | Patron / délégataire | Enregistrer GO, GO sous conditions, ATTENTE, NO-GO ou ABANDON. | Périmètre, preuves, inconnus, conditions, step-up si applicable |
| DEC-02 | Historique des décisions | Décision & Prix | SCREEN | UX-Primary | Patron / responsable selon droits | Voir décisions, supersessions, invalidations et motifs. | Ancienne version, revalidation, auteur |
| PRI-01 | Workspace Prix | Décision & Prix | SCREEN | UX-Critical | Métreur / DAF / Patron selon droits | Contrôler le chiffrage importé et sa couverture. | DPGF/BPU/DQE, unités, validité, couverture, droits |
| PRI-02 | Couverture coûts / facteurs non couverts | Décision & Prix | SCREEN | UX-Critical | Métreur / Responsable / Patron | Rapprocher exigences et postes de coût, sans zéro implicite. | Un besoin plusieurs postes, postes multiples, inconnus |
| PRI-03 | Capacité / charge critique | Décision & Prix | SCREEN | UX-Primary | Conducteur / Patron | Tester la disponibilité des ressources critiques sans faire un planning chantier complet. | Périodes, ressources, conflits, responsable |
| PRI-04 | Trésorerie / financement | Décision & Prix | SCREEN | UX-Primary | DAF / Patron | Montrer besoin maximal estimé et hypothèses de cash. | Encaissements, décaissements, retenues, financement non démontré |
| PRI-05 | Scénarios économiques / hypothèses | Décision & Prix | SCREEN | UX-Critical | DAF / Patron | Comparer scénarios autorisés avec contribution, exposition et hypothèses. | Contribution, taux sur vente, coût inconnu, scénario défavorable |
| PAR-01 | Partenaires de l’Affaire | Partenaires | SCREEN | UX-Primary | Responsable / Achats / Patron | Voir fournisseurs, sous-traitants, cotraitants et leur état d’engagement. | Consulté, réponse reçue, retenu, engagé, accepté/agréé |
| PAR-02 | Comparatif d’offres partenaires | Partenaires | SCREEN | UX-Primary | Achats / Métreur / Patron | Comparer à périmètre constant, coût complet et validité. | Exclusions, transport, délai, garanties, conformité |
| COL-01 | Tâches de l’Affaire | Collaboration | SCREEN | UX-Primary | Équipe Affaire | Affecter, suivre et réassigner les tâches sans transfert implicite de pouvoir. | Responsable, échéance, dépendance, absence |
| COL-02 | Commentaires / mentions / fil d’activité | Collaboration | PANEL | UX-Support | Équipe autorisée | Collaborer sans transformer un commentaire en fait validé. | Mention, résolution, lien source, droits |
| RES-01 | Plan de réponse | Réponse | SCREEN | UX-Critical | Responsable / équipe | Structurer ce qui doit être produit pour la phase/lot/tour. | Sections, propriétaire, critères, échéance |
| RES-02 | Checklist des livrables | Réponse | SCREEN | UX-Critical | Responsable / administratif | Piloter chaque pièce à produire/obtenir/remplir/signature. | Obligatoire, modèle imposé, état, responsable |
| RES-03 | Atelier de réponse / mémoire technique | Réponse | SCREEN | UX-Critical | Responsable / rédacteurs / experts | Composer le contenu en distinguant source, entreprise, IA et validation. | Brouillon, proposition IA, validation humaine, limite pages |
| RES-04 | Atelier cadres acheteur / formulaires | Réponse | SCREEN | UX-Primary | Administratif / Responsable | Compléter les cadres imposés sans conversion ou suppression silencieuse. | Original, copie, champs, formules, zones protégées |
| RES-05 | Documents et preuves externes à obtenir | Réponse | SCREEN | UX-Primary | Administratif / Responsable | Suivre attestations, assurances, RIB, visites et pièces tierces nécessaires. | Demandé, reçu, vérifié, expiré, non applicable |
| RES-06 | Registre des engagements | Réponse | SCREEN | UX-Critical | Responsable / Patron / experts | Identifier ce que l’offre promet et son coût/responsable futur. | Origine, texte exact, validation, moyens, passation |
| RES-07 | Revue de conformité de la réponse | Réponse | SCREEN | UX-Critical | Responsable / Patron | Contrôler critères, pièces, engagements et inconnus avant P4. | B0/B1/B2, non couvert, à revalider |
| SUB-01 | Coffre de remise | Remise | SCREEN | UX-Critical | Responsable / Patron | Constituer la version candidate exacte par lot/phase/tour. | Versions, format, nommage, signatures, manifeste |
| SUB-02 | Contrôle pré-remise | Remise | SCREEN | UX-Critical | Responsable / Patron | Afficher ce qui bloque P5 et ce qui est seulement arbitrable. | B0/B1/B2, version, destinataire, échéance |
| SUB-03 | Signataires / statut de signature | Remise | SCREEN | UX-Primary | Administratif / Patron / signataire | Vérifier qui doit signer quoi sans confondre login, image et signature valide. | Pièce/phase, signataire, état, réimport signé |
| SUB-04 | Autorisation P5 | Remise | FLOW | UX-Critical | Patron / délégataire P5 | Autoriser ce paquet exact après step-up. | Manifeste, version, droits, confirmation |
| SUB-05 | Export / instructions de dépôt | Remise | SCREEN | UX-Critical | Opérateur de dépôt | Télécharger le paquet exact et voir canal, échéance, consignes et avertissements. | P5 courant, version exact, redépôt |
| SUB-06 | Preuve de remise / reçu | Remise | SCREEN | UX-Critical | Opérateur / Responsable / Patron | Importer et rapprocher la preuve externe sans inventer le succès. | Transmission déclarée, réception prouvée, contenu partiel/incohérent |
| SUB-07 | Historique des remises / redépôts | Remise | SCREEN | UX-Primary | Responsable / Patron | Conserver chaque paquet, autorisation et reçu sans écrasement. | Tour, lot, reçu, statut, ancienne offre |
| OUT-01 | Clarification / négociation / nouvelle offre | Après remise | SCREEN | UX-Primary | Responsable / Patron | Qualifier une demande post-remise et déclencher P6 si engagement modifié. | Précision, pièce, négociation, mise au point, nouvel envoi |
| OUT-02 | Résultat de l’Affaire | Après remise | SCREEN | UX-Critical | Responsable / Patron | Enregistrer résultat par lot et preuve externe. | Perdu, attribution annoncée, marché notifié, sans suite |
| OUT-03 | Passation | Après remise | SCREEN | UX-Critical | Patron / Responsable / Conducteur | Transmettre ce qui a réellement été vendu avec réserves et accusé. | Périmètre, engagements, risques, documents, destinataire chantier |
| OUT-04 | REX / clôture de l’Affaire | Après remise | SCREEN | UX-Primary | Responsable / Patron | Capitaliser résultat, écarts et amélioration sans transformer hypothèse en vérité. | Motif connu/inconnu, estimation vs réalisé, validation mémoire |
| ENT-01 | Accueil Mémoire Entreprise | Entreprise | SCREEN | UX-Critical | Selon droits | Piloter preuves réutilisables, expirations, complétude et actions. | À vérifier, expiré, retiré, réutilisable |
| ENT-02 | Identité / établissements | Entreprise | SCREEN | UX-Primary | Propriétaire / Administratif | Gérer identité légale et établissements applicables. | SIREN/SIRET, coordonnées, état, source |
| ENT-03 | Pouvoirs / signataires | Entreprise | SCREEN | UX-Critical | Propriétaire / Patron / Administratif | Gérer personnes habilitées et portée des pouvoirs. | Pouvoir, durée, périmètre, preuve |
| ENT-04 | Documents administratifs / preuves | Entreprise | SCREEN | UX-Critical | Administratif / QSE | Gérer attestations, assurances, qualifications, certificats et validités. | Applicabilité, expiration, source, prochaine revue |
| ENT-05 | Personnel / compétences / habilitations | Entreprise | SCREEN | UX-Primary | Administratif / QSE / responsable autorisé | Gérer données minimisées utiles aux offres. | CV, compétence, habilitation, disponibilité, sensibilité |
| ENT-06 | Moyens matériels | Entreprise | SCREEN | UX-Primary | Responsable / Conducteur | Gérer matériel détenu/loué/envisagé et disponibilité. | Preuve, disponibilité, périmètre |
| ENT-07 | Références / réalisations | Entreprise | SCREEN | UX-Critical | Commercial / Responsable / Patron | Gérer références réellement réalisées et droits de réemploi. | Rôle réel, part réalisée, preuve, autorisation publication |
| ENT-08 | Partenaires / fournisseurs / sous-traitants | Entreprise | SCREEN | UX-Primary | Achats / Administratif / Patron | Gérer fiches et preuves des partenaires réutilisables. | Identité, assurance, vigilance, spécialité, état |
| ENT-09 | Méthodes / QSE / contenus réutilisables | Entreprise | SCREEN | UX-Primary | Responsables de contenu | Gérer méthodes, politiques et contenus réutilisables avec validation. | Version, propriétaire, portée, statut |
| ENT-10 | Modèles / gabarits internes | Entreprise | SCREEN | UX-Support | Responsables / Admin produit client | Gérer modèles internes autorisés sans confondre avec modèles acheteur. | Version, portée, propriétaire |
| ENT-11 | Données économiques Direction | Entreprise | SCREEN | UX-Critical | Patron / DAF uniquement | Gérer paramètres économiques internes autorisés sans fuite vers autres rôles. | Sensibilité Direction, historique, export borné |
| ENT-12 | File de revue / expirations | Entreprise | SCREEN | UX-Primary | Propriétaires de contenu | Voir ce qui expire, doit être vérifié ou a été retiré. | Date, impact offres ouvertes, responsable |
| SHR-01 | Créer un partage externe | Partage tiers | FLOW | UX-Critical | Utilisateur autorisé | Préparer un paquet ciblé, destinataire, finalité, durée et droits. | Aperçu exact, données exclues, confirmation |
| SHR-02 | Gérer / révoquer les partages | Partage tiers | SCREEN | UX-Primary | Utilisateur autorisé / sécurité | Voir accès, téléchargements et révoquer les futurs accès. | Actif, expiré, révoqué, incident |
| SHR-03 | Portail destinataire externe | Partage tiers | SCREEN | UX-Critical | Tiers | Consulter uniquement le paquet autorisé sans vue globale de l’Affaire. | Vérification destinataire, expiration, téléchargement |
| SHR-04 | Dépôt tiers externe | Partage tiers | SCREEN | UX-Primary | Tiers | Déposer une réponse ou pièce dans le périmètre autorisé. | Upload non fiable jusqu’aux contrôles, reçu de dépôt |
| ADM-01 | Accueil Administration / Gouvernance | Administration | SCREEN | UX-Primary | Propriétaire / Admin | Voir état utilisateurs, sécurité, droits, données et actions rares. | Alertes, tâches admin, aucun contenu sensible automatique |
| ADM-02 | Utilisateurs | Administration | SCREEN | UX-Critical | Propriétaire / Admin | Inviter, suspendre, réactiver et voir les statuts. | MFA, dernier accès, rôle, périmètre |
| ADM-03 | Fiche utilisateur / accès | Administration | SCREEN | UX-Critical | Propriétaire / Admin | Voir rôles, délégations, périmètres et sessions sans lire le métier interdit. | Demandes, approbations, révocations |
| ADM-04 | Rôles / délégations | Administration | SCREEN | UX-Critical | Propriétaire / autorité compétente | Définir délégations P0–P7, lots, catégories, durée et plafonds. | Expiration, non-transmissible, suppléant |
| ADM-05 | Sécurité / MFA / sessions | Administration | SCREEN | UX-Critical | Propriétaire / Admin sécurité | Gérer politiques de sécurité sans exposer les facteurs secrets. | Session, MFA, step-up, révocation |
| ADM-06 | Journal d’audit | Administration | SCREEN | UX-Critical | Propriétaire / sécurité / auditeur autorisé | Consulter actions sensibles et preuves sans fuite inter-client. | Filtres, export borné, intégrité |
| ADM-07 | Notifications / préférences organisation | Administration | SCREEN | UX-Support | Admin / Propriétaire | Configurer notifications critiques et canaux. | Email, centre produit, échec, escalade |
| ADM-08 | Gouvernance des données | Administration | SCREEN | UX-Critical | Propriétaire / responsable données | Voir catégories, finalités, conservation, droits et exports. | W juridiques, calendrier, catégories |
| ADM-09 | Accès support exceptionnel | Administration | SCREEN | UX-Critical | Autorité client / support | Autoriser un accès nominatif, borné et tracé au strict nécessaire. | Motif, durée par défaut 1h, expiration, révocation |
| ADM-10 | Export / réversibilité / fermeture | Administration | FLOW | UX-Critical | Propriétaire + autorités données | Préparer export vérifié, gel, réversibilité et fermeture sans suppression aveugle. | Export complet/partiel, litige, renonciation, calendrier |
| ADM-11 | Usage IA / coûts / quotas | Administration | SCREEN | UX-Support | Propriétaire / Admin | Rendre l’usage IA et les dépenses inhabituelles visibles et gouvernables. | Consommation, limite, alerte, aucune dépense illimitée |
| SYS-01 | Centre de traitements | Système | SCREEN | UX-Primary | Selon droits | Voir analyses/imports/générations en cours, partielles ou en échec. | Progression, annulation sûre, reprise, coût inhabituel |
| SYS-02 | Mode dégradé / IA indisponible | Système | STATE | UX-Critical | Tous | Expliquer ce qui est indisponible et ce qui reste utilisable. | Documents, décisions, Coffre, export utilisables |
| SYS-03 | Incident / reprise de service | Système | SCREEN | UX-Primary | Propriétaire / responsables | Afficher périmètre affecté, dernier état confirmé et prochaine information. | RPO/RTO objectifs non présentés comme atteints sans preuve |
| MOB-01 | Accueil mobile terrain | Mobile | RESPONSIVE | UX-Primary | Conducteur / Responsable | Accéder aux actions terrain et alertes sans devenir un poste d’étude complet. | Tâches, visites, synchro |
| MOB-02 | Affaire mobile ciblée | Mobile | RESPONSIVE | UX-Primary | Utilisateur terrain | Consulter échéances, pièces clés et actions autorisées. | Données bornées, pas prix complexe |
| MOB-03 | Visite mobile | Mobile | RESPONSIVE | UX-Primary | Conducteur / visiteur autorisé | Gérer checklist, constats, présence et preuve de visite. | Obligatoire/facultative, local/synchronisé |
| MOB-04 | Capture note / photo / justificatif | Mobile | RESPONSIVE | UX-Primary | Utilisateur terrain | Capturer hors réseau et rendre le statut de synchronisation explicite. | Local, en attente, synchronisé, échec |
| MOB-05 | Tâches mobile | Mobile | RESPONSIVE | UX-Primary | Utilisateur terrain | Voir et mettre à jour les tâches compatibles mobile. | Hors ligne borné, reprise |

---

# 5. Correspondance avec les 12 écrans structurants

| Contrat | Pivot du catalogue | Surfaces complémentaires majeures |
|---|---|---|
| E01 Accueil Patron | HOME-01 | GLB-03, GLB-04, DEC-02, SYS-02 |
| E02 Radar | OPP-01 | OPP-02, OPP-04, SYS-01 |
| E03 Fiche Opportunité | OPP-03 | OPP-04, AFF-01 |
| E04 Import DCE | DCE-01 | DCE-02, DCE-06, SYS-01 |
| E05 Explorateur DCE | DCE-03 | DCE-04, DCE-05, DCE-07, DCE-08, DCE-09 |
| E06 Synthèse Affaire | AFF-02 | AFF-03, COL-01, PAR-01 |
| E07 Registre MIRP | DCE-12 | DCE-08, DCE-13, DCE-10, DCE-11 |
| E08 Décision GO/NO-GO | DEC-01 | DEC-02, PRI-03, PRI-04, PRI-05 |
| E09 Prix | PRI-01 | PRI-02, PRI-03, PRI-04, PRI-05, PAR-02 |
| E10 Réponse | RES-03 | RES-01, RES-02, RES-04, RES-05, RES-06, RES-07 |
| E11 Coffre | SUB-01 | SUB-02, SUB-03, SUB-04, SUB-05, SUB-06, SUB-07 |
| E12 Passation | OUT-03 | OUT-02, OUT-04, RES-06 |

S01 Mémoire Entreprise est matérialisée par **ENT-01 à ENT-12**.  
S02 Organisation / Accès / Gouvernance est matérialisée par **AUTH-01 à AUTH-08**, **ADM-01 à ADM-11** et l’onboarding.

---

# 6. Parcours bout-en-bout à prototyper

| ID | Parcours | Chaîne principale | Validation recherchée |
|---|---|---|---|
| PUX-01 | Première mise en service | AUTH-02 → AUTH-03 → ONB-01 → ONB-02 → ONB-03 → ONB-04 → HOME-01 | Première valeur sans paramétrage exhaustif |
| PUX-02 | BOAMP vers Affaire | HOME-01 → OPP-01 → OPP-03 → P0 → P1 → AFF-02 | Provenance, lots, échéance, décision d’ouvrir |
| PUX-03 | Invitation privée | OPP-04 → OPP-03 → P1 → DCE-01 → AFF-02 | Aucune dépendance obligatoire au Radar |
| PUX-04 | DCE reçu et analyse | DCE-01 → DCE-02 → DCE-06 → DCE-03 → DCE-07/12/13 → AFF-02 | Reçu ≠ lu ≠ compris ≠ couvert |
| PUX-05 | Rectificatif | DCE-05 → impacts → à revalider → écrans dépendants | Invalidation ciblée, pas globale |
| PUX-06 | GO/NO-GO | AFF-02 → DCE-12 → PRI-01/03/04/05 → DEC-01 → DEC-02 | Décision humaine avec inconnus et preuves |
| PUX-07 | Prix | PRI-01 → PRI-02 → PRI-03 → PRI-04 → PRI-05 → P3 | Couverture, contribution, capacité, cash |
| PUX-08 | Préparer la réponse | RES-01 → RES-02 → RES-03/04/05 → RES-06 → RES-07 → P4 | Acheteur / entreprise / IA / validation séparés |
| PUX-09 | Autoriser et remettre | SUB-01 → SUB-02 → SUB-03 → AUTH-04 → SUB-04 → SUB-05 → dépôt humain → SUB-06 | P5 ≠ signature ≠ preuve de dépôt |
| PUX-10 | Redépôt | SUB-07 → nouvelle candidate → P4/P5 concernés → SUB-05/06 | Ancien paquet jamais recyclé silencieusement |
| PUX-11 | Résultat et passation | OUT-02 → lot gagné → OUT-03 → réserves → OUT-04 | Résultat par lot et engagements transmis |
| PUX-12 | Perdu / REX | OUT-02 → OUT-04 → ENT si capitalisation validée | REX non injecté automatiquement dans la mémoire |
| PUX-13 | Partage tiers | SHR-01 → aperçu → step-up si sensible → SHR-03/04 → SHR-02 | Destinataire, contenu, durée, révocation |
| PUX-14 | Départ collaborateur | ADM-02 → suspension → réaffectation → historique conservé | Retirer accès sans effacer l’histoire |
| PUX-15 | Dernier Propriétaire compromis | incident → AUTH-06 → suspension → preuve d’autorité → réattribution | OWN-01 sans pouvoir automatique du support |
| PUX-16 | Fin de contrat | ADM-10 → inventaire → export → gel → réversibilité → suppression → preuve | Pas de suppression aveugle |
| PUX-17 | Panne IA | SYS-02 superposé aux parcours | Fonctions critiques toujours utilisables |
| PUX-18 | Terrain hors réseau | MOB-01 → MOB-03/04 → en attente → synchronisation | Non synchronisé ≠ partagé |

---

# 7. Parcours par rôle

## Patron

Fil principal :  
`HOME-01 → AFF-02 → DEC-01 / PRI-05 / RES-07 / SUB-02 → autorisation`

Le Patron doit pouvoir arbitrer par exception sans parcourir toute la mécanique documentaire.

## Responsable d’offre

Fil principal :  
`HOME-02 → AFF-01 → AFF-02 → DCE-06/07/12 → RES-01/02/03 → SUB-01`

Il prépare et prouve ; il ne gagne pas automatiquement l’accès Direction ni l’autorité Patron.

## Expert

Fil principal :  
`HOME-03 ou GLB-04 → écran expert concerné → validation/revue → retour tâche`

L’expert intervient dans son périmètre sans devoir reconstruire l’Affaire entière.

## Administrateur

Fil principal :  
`ADM-01 → ADM-02/03/04/05/06/08/09/10`

Administrer ne confère aucun droit métier automatique.

## Tiers

Fil principal :  
`SHR-03 → consultation limitée / SHR-04 dépôt → fin d’accès`

Aucune vue globale de l’Affaire.

---

# 8. Matrice de fidélité des prototypes

## Niveau A — UX-Critical

Prototype haute fidélité fonctionnelle :
- données réalistes fictives ;
- parcours complet ;
- Patron et Collaborateur ;
- états normal / partiel / bloqué / erreur ;
- action IA et mode sans IA ;
- interactions principales ;
- source/preuve accessible ;
- confirmation sensible lorsque requise.

## Niveau B — UX-Primary

Prototype visuel complet :
- navigation ;
- contenu ;
- action principale ;
- principaux états ;
- liens avec les écrans critiques.

## Niveau C — UX-Support

Contrat visuel :
- structure ;
- champs/actions essentiels ;
- état principal ;
- place dans le parcours.

---

# 9. Ordre de production des prototypes

| Vague | Contenu |
|---|---|
| **0** | Shell, navigation, langage visuel, badges de preuve, états, tables, panneaux, confirmations sensibles |
| **1** | AUTH-01 à AUTH-08, ONB-01 à ONB-04, HOME-01/02/03 |
| **2** | OPP-01 à OPP-04, AFF-01/02 |
| **3** | DCE-01 à DCE-13, AFF-03 |
| **4** | DEC-01/02, PRI-01 à PRI-05, PAR-01/02, COL-01/02 |
| **5** | RES-01 à RES-07, SUB-01 à SUB-07 |
| **6** | OUT-01 à OUT-04 |
| **7** | ENT-01 à ENT-12 |
| **8** | ADM-01 à ADM-11, SHR-01 à SHR-04 |
| **9** | SYS-01 à SYS-03, MOB-01 à MOB-05 |

---

# 10. Scénario fictif commun aux prototypes

Pour éviter des maquettes abstraites, toutes les vagues utiliseront un même scénario fictif cohérent :

- PME BTP française fictive ;
- Patron, Responsable d’offre, Métreur, QSE, DAF, Conducteur ;
- consultation publique multi-lots ;
- RC, CCAP, CCTP, DPGF/BPU, annexes et rectificatif ;
- visite obligatoire ;
- contradiction documentaire ;
- page illisible ;
- facteur de coût non couvert ;
- fournisseur dont le prix expire ;
- GO sous condition ;
- rectificatif après P4 ;
- paquet de remise ;
- reçu externe partiellement détaillé ;
- un lot gagné et un lot perdu ;
- passation avec engagement critique.

Le scénario reste un support UX fictif/anonymisé et ne devient pas une vérité Golden DCE.

---

# 11. Critères de validation d’une surface

Une surface est **UX-VALIDÉE** lorsque le propriétaire peut répondre oui aux questions suivantes :

1. Je comprends immédiatement où je suis et dans quelle entreprise/Affaire.
2. Je sais ce qui mérite mon attention.
3. L’action principale est évidente.
4. Je distingue prouvé / inconnu / partiel / bloqué.
5. Je peux revenir à la source lorsque nécessaire.
6. Je distingue proposition SMART AO et validation humaine.
7. Patron, Collaborateur, Expert, Admin et Tiers respectent les frontières prévues.
8. Une erreur ou panne IA ne crée ni succès fictif ni perte silencieuse.
9. Je sais comment reprendre.
10. L’écran ne promet rien que le cahier v0.4 n’autorise.

---

# 12. Critères de fermeture du catalogue

Le catalogue pourra passer en **UX FREEZE v1.0** lorsque :

- toutes les capacités V1 du cahier v0.4 sont reliées à au moins une surface ;
- aucun écran orphelin sans besoin métier n’existe ;
- les 18 parcours PUX sont traversables ;
- les rôles principaux sont testés visuellement ;
- confidentialité, erreur, blocage, reprise et IA indisponible sont matérialisés ;
- toutes les surfaces UX-Critical sont validées ;
- les UX-Primary sont validées au minimum en fidélité fonctionnelle ;
- les recettes G01–G52 sont mappées aux écrans/parcours ;
- aucun écart C1 n’est renvoyé à Codex.

Le résultat sera alors intégré au :

> `SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md`

---

# 13. Ce que le catalogue ne décide pas

Ce document ne choisit ni framework frontend, ni design system technique, ni parser, OCR, moteur vectoriel, embeddings, LLM ou infrastructure.

Il fixe **ce que la technologie devra rendre visible, fiable, sécurisé et utilisable**.

---

# 14. Décision immédiate

Le présent `v0.1` devient le **registre UX de travail**.

A2 SourceAnchor reste HOLD.

Le prochain livrable sera la **Vague 0 — shell et langage visuel**, puis la **Vague 1 — accès, onboarding et accueils**. Chaque vague sera soumise à validation propriétaire avant la suivante, tout en maintenant la cohérence avec l’ensemble du catalogue.

---

**Fin — Catalogue des écrans & parcours produit v0.1**
