# SMART AO — Plan global de conception et réalisation
## CHECKLIST PILOTÉE v0.1

**Créé le :** 14 septembre 2026  
**Dernière mise à jour :** 24 septembre 2026
**Statut global :** EN COURS  
**Tranche active :** T2 — contrat applicable, baseline et dérogations
**Prochaine étape unique :** implémenter la vue d'audit consolidée de l'export local, sans fusion d'événements.

## 1. Rôle de ce document

Ce document est la feuille de route opérationnelle suivie par Codex jusqu'à la fin du projet. Il relie la conception produit, l'UX, le code, les tests, les validations et la mise en production.

Il ne remplace pas les autorités propriétaires. L'ordre de preuve reste :

1. code vivant et tests exécutés ;
2. décisions propriétaires, ADR et spécifications approuvées ;
3. ce plan de pilotage ;
4. Basic Memory, utilisé pour reprendre le travail et suivre l'état du plan.

Légende :

- `[x]` terminé et prouvé ;
- `[>]` tranche active ;
- `[ ]` à faire ;
- `[-]` conditionnel, non nécessaire dans l'état actuel ;
- `[!]` bloqué par une décision ou une preuve manquante.

Une seule tranche peut porter `[>]`. Une case n'est cochée qu'après production de la preuve annoncée.

## 2. Méthode appliquée à chaque tranche

Chaque expérience et chaque capacité suit le même cycle :

- [ ] relire l'autorité produit et le catalogue concernés ;
- [ ] inspecter le code, les tests, les données et les contrats réellement disponibles ;
- [ ] écrire le résultat métier attendu, les rôles, les états difficiles et les invariants ;
- [ ] choisir la plus petite tranche verticale qui produit une valeur réelle ;
- [ ] coder le front, le backend et la persistance strictement nécessaires ;
- [ ] prouver le chemin réel, les refus de sécurité, les erreurs et l'idempotence applicable ;
- [ ] mettre à jour la documentation active et ce plan ;
- [ ] enregistrer le nouvel état et la prochaine étape dans Basic Memory ;
- [ ] présenter le résultat pour revue propriétaire lorsqu'un arbitrage ou un gel est nécessaire.

Les neuf cases de ce cycle sont évaluées dans chaque tranche ; elles ne sont pas cochées globalement une fois pour toutes.

## 3. Plan de travail du 14 septembre 2026

- [x] Réorganiser la documentation active et désigner les autorités actuelles.
- [x] Établir le programme des sept expériences utilisateur.
- [x] Prouver PAGE-001/PAGE-002 : mot de passe, session limitée et MFA obligatoire.
- [x] Prouver PAGE-003/PAGE-006 : confirmation du contexte et première Affaire idempotente.
- [x] Créer le présent plan global et son suivi persistant.
- [x] Auditer, cadrer et coder PAGE-007 — premier Accueil composé.
- [x] Exécuter les tests ciblés de PAGE-007 et mettre à jour les preuves EXP-01.
- [x] Auditer et prouver l'émission, l'expiration, la réémission et la non-divulgation d'une invitation nominative.
- [x] Coder l'acceptation nominative à usage unique, l'activation d'identité et son enchaînement vers la MFA.
- [x] Exécuter la preuve PostgreSQL de l'acceptation et vérifier le refus métier avant MFA.
- [x] Auditer les contrats et le code de récupération existants, puis fixer la plus petite preuve d'identité, codes de secours et refus de l'email seul.
- [x] Coder la preuve de récupération par mot de passe et code de secours : révocation complète, nouvel enrôlement MFA obligatoire et refus de l'email seul.
- [x] Synchroniser le miroir Basic Memory après la preuve PostgreSQL.
- [x] Terminer la tranche par la mise à jour de cette checklist et du statut Basic Memory.
- [x] Auditer les contrats et le code de changement de contexte, puis fixer la plus petite preuve des rôles Patron, Responsable et Expert sans élévation de droit.
- [x] Auditer puis cadrer la qualification P0/P1, les lots, les échéances et les inconnus explicites dans `SMART_AO_EXP_02_QUALIFICATION_P0_P1_LOTS_ECHEANCES_INCONNUS_AUDIT_CADRAGE_v0.1.md`.
- [x] Coder et tester le statut P0, le périmètre de lots et les inconnus explicitement visibles sur la Fiche Opportunité.
- [x] Auditer puis cadrer la décision de poursuivre ou d’écarter une opportunité sans score opaque dans `SMART_AO_EXP_02_DECISION_POURSUIVRE_ECARTER_AUDIT_CADRAGE_v0.1.md`.
- [x] Implémenter et tester la décision explicite de poursuivre ou d’écarter sans score opaque.
- [x] Compléter la preuve HTTP/PostgreSQL de l’indépendance entre score et décision.

Si la session s'arrête avant la fin de cette liste, la première case non terminée devient automatiquement la prochaine étape de reprise.

## 4. Feuille de route globale

### PHASE 0 — Gouvernance et socle de preuve

- [x] Désigner le cahier produit/métier OWNER_CONSOLIDATED v0.4 comme autorité actuelle.
- [x] Désigner le catalogue écrans/parcours OWNER_CONSOLIDATED v0.3 comme référence UX active.
- [x] Séparer références actives, implémentation active, travaux futurs et archives.
- [x] Réaliser l'audit Phase 0 / Gate 0 du dépôt et de l'architecture v3.1.
- [x] Rendre A0 reproductible et constituer la baseline Golden DCE Development A1.
- [ ] Qualifier le Golden DCE avec droits, anonymisation, double revue et désaccords résolus avant tout usage de gel.
- [ ] Maintenir l'index documentaire et ce plan après chaque tranche.

**Sortie de phase :** une autorité claire, un dépôt mesurable et aucune décision de produit portée par un document historique.

### PHASE 1 — EXP-01 : premier accès et première valeur

- [x] PAGE-001 — connexion et session tenant-scopée.
- [x] PAGE-002 — activation/challenge MFA et interdiction d'accès métier avant validation.
- [x] PAGE-003 — confirmation explicite de l'entreprise et du rôle.
- [-] PAGE-004 — configuration minimale, déclenchée seulement si une donnée réellement obligatoire manque.
- [-] PAGE-005 — profil personnel, déclenché seulement si une préférence nécessaire apparaît.
- [x] PAGE-006 — création réelle et reprise idempotente d'une première Affaire.
- [x] PAGE-007 — premier Accueil composé avec prochaine action, surveillance et événements autorisés.
- [x] Invitation nominative : validité, expiration, réémission et non-divulgation.
- [x] Acceptation nominative à usage unique : consommation PostgreSQL, activation atomique et session `PASSWORD` refusée avant MFA prouvées.
- [x] Récupération assistée : code de secours refusé en step-up ; session fraîche par mot de passe, révocation complète et nouvel enrôlement MFA prouvés sur PostgreSQL.
- [x] Changement de contexte et rôles Patron, Responsable et Expert sans élévation de droit : audit et contrat minimal fixé dans `SMART_AO_EXP_01_CONTEXTE_ROLES_PREUVE_VERTICALE_v0.1.md`.
- [x] Coder la preuve minimale de contexte : rôle technique serveur, profil Responsable ou Expert sans nouveau droit, et refus de toute élévation depuis le navigateur.
- [x] Auditer les contrats et le code de reprise après expiration, réponse inconnue et configuration interrompue, puis fixer la plus petite preuve verticale.
- [x] Coder la preuve de résultat inconnu pour la création d’Affaire : état « à vérifier », rejeu avec les mêmes identifiants et absence de succès présumé — preuve front acquise, sans succès présumé.
- [x] Auditer les contrats et le code de reprise de session après expiration, puis fixer la preuve minimale du dernier état confirmé — snapshot en mémoire, masquage et reprise conditionnelle prouvés.
- [x] Assembler la preuve exécutable EXP-01 et parcourir les états difficiles : suite front complète, sous-ensemble backend, refus, erreurs, reprise et changement de rôle prouvés.
- [x] Présenter la preuve exécutée d'EXP-01 et ses limites pour revue propriétaire dans `SMART_AO_EXP_01_OWNER_REVIEW_v0.1.md`.
- [x] Recueillir les arbitrages propriétaire sur le périmètre et les limites d'EXP-01 : délégation explicite reçue et décisions retenues.
- [x] Revue propriétaire puis `OWNER EXPERIENCE FREEZE` d'EXP-01 : contrat gelé dans `SMART_AO_EXP_01_OWNER_EXPERIENCE_FREEZE_v0.1.md`.
- [x] Rédiger la maquette détaillée et le contrat technique consolidé d'EXP-01.
- [x] Implémenter et tester la première tranche verticale du contrat technique consolidé d'EXP-01 : création manuelle complète, origine non référencée masquée, rejeu idempotent et états inconnus vérifiés côté front.
- [x] Démarrer EXP-02 : auditer les contrats et le code d’ingestion/qualification BOAMP, puis fixer la plus petite preuve verticale dans `SMART_AO_EXP_02_BOAMP_AUDIT_PREUVE_VERTICALE_v0.1.md`.
- [x] Coder et tester le chaînage observation qualifiée → Affaire idempotente, avec fraîcheur de collecte visible côté front/API.
- [x] Exécuter la preuve PostgreSQL de la conversion BOAMP et ses refus sur le conteneur dédié `smart-ao-v8-postgres`.
- [x] Auditer puis cadrer la qualification P0/P1, les lots, les échéances et les inconnus explicites dans `SMART_AO_EXP_02_QUALIFICATION_P0_P1_LOTS_ECHEANCES_INCONNUS_AUDIT_CADRAGE_v0.1.md`.
- [x] Coder et tester la projection P0/P1, le lot `UNKNOWN`, les états d’échéance et les inconnus d’ouverture sur la Fiche Opportunité.

**Sortie de phase :** un nouvel utilisateur autorisé atteint un Accueil utile et reprend son travail en sécurité dans tous les scénarios retenus.

### PHASE 2 — EXP-02 : opportunité vers Affaire

- [ ] Radar et ingestion d'une opportunité avec fraîcheur et provenance.
- [x] Qualification P0/P1, lots, échéances et inconnus explicites — matérialiser la projection sur la Fiche Opportunité.
- [x] Auditer puis cadrer la décision de poursuivre ou d'écarter sans score opaque dans `SMART_AO_EXP_02_DECISION_POURSUIVRE_ECARTER_AUDIT_CADRAGE_v0.1.md`.
- [x] Implémenter et tester la décision explicite de poursuivre ou d'écarter sans score opaque.
- [x] Compléter la preuve HTTP/PostgreSQL de l'indépendance entre score et décision.
- [x] Compléter la preuve de transformation idempotente en Affaire sans doublon ni perte de source.
- [x] Cadrer la panne de source externe et la saisie manuelle maîtrisée dans `SMART_AO_EXP_02_SOURCE_OUTAGE_MANUAL_INTAKE_AUDIT_CADRAGE_v0.1.md`.
- [x] Implémenter et tester le statut de source, la conservation des observations et l'accès à la saisie manuelle.
- [x] Clôturer EXP-02 par la revue des rôles, refus, responsive utile et critères de gel dans `SMART_AO_EXP_02_OWNER_EXPERIENCE_FREEZE_v0.1.md`.
- [x] Rôles, refus, mobile utile, tests verticaux, revue et gel d'expérience.

**Parcours couverts :** PUX-02 et première partie de PUX-03.  
**Sortie de phase :** une opportunité traçable devient une Affaire unique et exploitable.

### PHASE 3 — EXP-03 : importer et comprendre un DCE

- [x] Auditer la réception contrôlée, quarantaine, antivirus, limites et reprise.
- [x] Prouver un flux interrompu et une reprise par nouvelle intention sans réutiliser l'objet rejeté.
- [x] Inventaire des fichiers, versions, formats protégés et éléments illisibles.
- [x] Extraction multiformat avec ancres de source vérifiables.
- [x] Classification et synthèse sans masquer les manques ni les incertitudes.
- [x] Rectificatifs et invalidation ciblée des conclusions dépendantes.
- [x] Panne IA, instruction hostile et poursuite manuelle sûre.
- [x] Rôles, refus, tests Golden DCE, revue et gel d'expérience.

**Dépendances d'architecture activées ici :**

- [ ] A2 — `SourceAnchor` multiformat générique ;
- [ ] A3 — Evidence probatoire générique en préservant les Evidence locales ;
- [ ] A4 — liaison, validation et invalidation transversales additives.

**Parcours couverts :** PUX-03, PUX-04, PUX-05 et PUX-17.  
**Sortie de phase :** un DCE réel devient un ensemble lisible, sourcé, versionné et révisable.

### PHASE 4 — EXP-04 : résoudre les points bloquants

- [ ] Unifier la vue « À résoudre » sans fusionner exigences, inconnues, risques, contradictions et tâches.
- [x] Première projection read-only des exigences DCE, demandes ouvertes et bloqueurs ouverts, avec couverture `PARTIAL`, tenant et affectation conservés.
- [x] Étendre la preuve aux rôles Patron/Responsable/Expert et aux états `REVIEW_REQUIRED`.
- [x] Intégrer les lectures séparées de risques et contradictions sans fusionner leurs cycles ; les inconnus restent dans leur source BOAMP.
- [x] Rattacher les inconnus BOAMP à une Affaire d'origine `OPPORTUNITY` sans perdre leur source ni leur état `UNKNOWN`.
- [x] Propager les attributs réellement portés par les agrégats EXP-04, dont l’échéance de la tâche liée au bloqueur, sans inventer les champs absents.
- [x] Traiter les contributions concurrentes sans « dernier clic gagne ».
- [x] Préparer des questions sourcées sans envoi autonome.
- [x] Conserver les validations métier distinctes de l'achèvement d'une tâche.
- [x] Préparer la revue et le gel d'expérience EXP-04 après preuve des rôles, refus et états difficiles.

**Parcours couverts :** PUX-05, PUX-06, N01 et N04.  
**Sortie de phase :** chaque blocage possède un état exact, une preuve et une action autorisée.

### PHASE 5 — EXP-05 : préparer la réponse et le chiffrage

- [x] Importer les prix et préserver les formats imposés : preview XLSX bornée, batch normalisé et source hashée.
- [x] Rejouer preview et commit après résultat inconnu avec les mêmes identifiants, sans succès présumé côté front.
- [x] Exposer les besoins non couverts déjà enregistrés avec leurs sources et une action de revue Patron-only.
- [x] Projeter côté Patron les hypothèses sourcées, l’absence de contrat de devis, le dernier run de capacité et la prévision de trésorerie sans montant ni feu vert implicite.
- [x] Intégrer cette projection économique dans la surface « Mes affaires / Revue » et vérifier son masquage Collaborateur.
- [x] Auditer les contrats de marge/scénarios et vérifier le calcul entier sur données validées ; les inconnus restent bloquants avant commit.
- [x] Auditer les contrats de moyens, partenaires et groupements, puis fixer la plus petite preuve sourcée sans élargir les droits ni agréger des engagements absents ; moyens réutilisés via les capacités d’entreprise, partenaires/groupements explicitement non démontrés faute de contrat.
- [x] Exposer les brouillons techniques versionnés dans le package collaborateur comme plan de réponse non financier, avec sections, sources et responsable.
- [ ] Calculer marge et taux avec données complètes, sans transformer l'inconnu en zéro.
- [ ] Gérer scénarios, moyens, partenaires et groupements avec provenance.
- [ ] Produire la réponse depuis un plan unique, avec modèles et preuves réemployables, puis séparer revue, transmission et autorisation de dépôt.
- [x] Protéger marge, CV et données sensibles selon rôle, champ et destinataire ; routes financières/entreprise Patron-only, package collaborateur non financier et remise gardée par décision.
- [x] Contrôler P2/P3/P4, conflits, versions, tests verticaux, revue et gel d'expérience ; couverture `PARTIAL` explicitement conservée dans le gel EXP-05.

**Parcours couverts :** PUX-06, PUX-07, PUX-08 et PUX-19.  
**Sortie de phase :** réponse et prix sont versionnés et contrôlables dans les limites documentées ; P2/P3/P4 restent `PARTIAL` tant que leurs sources et commandes dédiées ne sont pas prouvées.

### PHASE 6 — EXP-06 : préparer et remettre l'offre

- [x] Constituer une candidate persistante et contrôlable ; package immuable, manifeste hashé et autorisation P5 append-only prouvés dans `SMART_AO_EXP_06_CANDIDATE_P5_AUDIT_PREUVE_v0.1.md`.
- [x] Séparer validation du contenu, autorisation P5, signature, export, dépôt humain et réception ; export et réception restent des actes humains, distincts et audités.
- [x] Imposer un step-up MFA aux actes sensibles : P5, export et enregistrement d'une preuve de réception.
- [x] Gérer candidature seule, lots, copie de sauvegarde, redépôt et paquet modifié ; candidature seule justifiée, export déterministe audité, tentative humaine `UNKNOWN` et redépôt par nouvelle version sont prouvés, la copie de sauvegarde reste explicitement un acte opérateur hors système.
- [x] Traiter le rapprochement partiel sans fausse confirmation : lecture par package/version/hash, état `PARTIAL` et statut externe négatif prouvés sur PostgreSQL.
- [x] Prévisualiser exactement le paquet partagé et ses exclusions.
- [x] Rôles, refus, audit, tests verticaux, revue et gel d'expérience dans `SMART_AO_EXP_06_OWNER_EXPERIENCE_FREEZE_v0.1.md`.

**Parcours couverts :** PUX-08, PUX-09, PUX-10, PUX-13, N02 et N03.  
**Sortie de phase :** le bon paquet est autorisé, exporté, prêt pour le dépôt humain et rapproché de la preuve réellement disponible sans présumer du portail externe.

### PHASE 7 — EXP-07 : passer, clôturer et capitaliser

- [x] Auditer les contrats de résultat par lot et fixer la plus petite preuve de clôture sans réécrire l'historique ; preuve additive dans `SMART_AO_EXP_07_RESULTAT_LOT_AUDIT_PREUVE_v0.1.md`, migration `20260919_0076`, lot explicite ou déduit mono-lot, inconnus et refus conservés.
- [x] Implémenter le contrat append-only de résultat par lot et sa preuve Patron-only ; migration `20260919_0077`, rôle Patron, lot contrôlé, source/motif et états `WON`/`LOST`/`UNKNOWN` prouvés au contrat.
- [x] Ajouter la lecture Patron des résultats par lot, avec sources, états, motifs et réserves ; refus Collaborateur prouvé.
- [x] Persister et rejouer la transmission des seuls engagements réellement gagnés, avec réserves ; migration `20260919_0078`, refus des états non gagnés et transmission idempotente prouvés.
- [x] Distinguer attribution, commande, P6 et P7 dans `SMART_AO_EXP_07_ATTRIBUTION_COMMANDE_P6_P7_AUDIT_CADRAGE_v0.1.md` sans réutiliser le stage courant comme preuve.
- [x] Implémenter la commande append-only issue de `WON`, puis son contrôle P6 ; migrations `20260919_0079`/`0080`, routes Patron, invariants WON/lot/ACCEPTED, rejeu idempotent et refus P6 prouvés par 2 tests PostgreSQL.
- [x] Distinguer attribution, commande, P6 et P7.
- [x] Auditer puis implémenter le résultat P7, y compris l’état `UNKNOWN` et l’interruption ; migration `20260919_0081`, P6 `APPROVED` obligatoire, source obligatoire pour `COMPLETED`, motif obligatoire pour `UNKNOWN`/`INTERRUPTED`, rejeu idempotent prouvé.
- [x] Cadrer le retour d'expérience P7 avec motif connu ou inconnu, portée de réemploi et garde de validation dans `SMART_AO_EXP_07_REX_CAPITALISATION_AUDIT_CADRAGE_v0.1.md`.
- [x] Implémenter l'entrée REX append-only liée à P7, avec portée et validation explicites ; migration `20260919_0082`, route Patron, chaîne P7 `UNKNOWN` → REX local, refus de portée entreprise non sourcée et rejeu idempotent prouvés.
- [x] Cadrer la capitalisation des modèles et preuves avec validité, portée, applicabilité et droits de réemploi dans `SMART_AO_EXP_07_CAPITALISATION_VALIDITE_AUDIT_CADRAGE_v0.1.md`.
- [x] Implémenter la lecture Patron de la capitalisation avec portée et validité visibles ; route `GET /api/v1/patron/cases/{case_id}/rex`, tenant-scoping et 3 tests PostgreSQL passent.
- [x] Cadrer la suspension, l'export, la conservation et la fermeture dans `SMART_AO_EXP_07_RETENTION_SUSPENSION_EXPORT_AUDIT_CADRAGE_v0.1.md`.
- [x] Implémenter la suspension et la fermeture append-only ; migration `20260920_0083`, acte Patron `SUSPENDED`/`RESUMED`/`CLOSED`, refus P7 `UNKNOWN`/`INTERRUPTED` ou litige ouvert et rejeu idempotent prouvés par 5 tests PostgreSQL.
- [x] Implémenter la demande d'export et la conservation append-only ; migration `20260920_0084`, actes Patron séparés `CASE_EXPORT_REQUESTED` et `CASE_RETENTION_RECORDED`, réception externe `NOT_PERFORMED`, rejet Collaborateur et rejeu idempotent prouvés par 6 tests PostgreSQL.
- [x] Assembler la preuve verticale EXP-07, vérifier les refus Patron et préparer le gel d'expérience ; 9 tests PostgreSQL ciblés et la tête Alembic passent.
- [x] Produire le retour d'expérience avec motif connu ou inconnu.
- [x] Capitaliser modèles et preuves avec validité, portée, applicabilité et droits de réemploi.
- [x] Suspendre, exporter, conserver et fermer selon litiges et règles de rétention.
- [x] Rôles, refus, tests verticaux, revue et gel d'expérience dans `SMART_AO_EXP_07_OWNER_EXPERIENCE_FREEZE_v0.1.md`.

**Parcours couverts :** PUX-11, PUX-12, PUX-16 et PUX-19.  
**Sortie de phase :** l'Affaire terminée transmet ses engagements et enrichit l'entreprise sans réécrire l'historique.

### PHASE 8 — Gouvernance, administration et mobilité complètes

- [x] Cadrer C14 dans `SMART_AO_C14_GOUVERNANCE_MEMBRES_DELEGATIONS_AUDIT_CADRAGE_v0.1.md` : inventaire du socle, écarts OWN-01/02/R02/R03 et invariants de propriété, délégation, suspension et relève.
- [x] Implémenter la propriété organisationnelle distincte du rôle Patron et la suspension immédiate append-only d’un membre, avec blocage de session.
- [x] Implémenter la désignation et le transfert append-only d’un Propriétaire organisationnel, sans auto-élévation ni récupération support.
- [x] Auditer puis cadrer les délégations nominatives bornées, la relève et le dernier Propriétaire compromis dans `SMART_AO_C14_DELEGATIONS_RELEVE_DERNIER_PROPRIETAIRE_AUDIT_CADRAGE_v0.1.md`.
- [x] Implémenter la délégation nominative bornée, sa résolution serveur, sa révocation et son invalidation à la suspension.
- [x] Implémenter la relève nominative, l’acceptation du successeur et l’état `NO_ACTIVE_OWNER` sans récupération automatique.
- [x] Implémenter R03 avec deux supports distincts, preuve d’autorité, approbation et nouvelle désignation sans pouvoir métier support.
- [x] Assembler la preuve verticale C14 et le gel d’expérience dans `SMART_AO_C14_OWNER_EXPERIENCE_FREEZE_v0.1.md`.
- [x] Auditer C15 : MFA, récupération et sessions sensibles après les nouvelles frontières de gouvernance dans `SMART_AO_C15_ACCES_MFA_RECUPERATION_SESSIONS_AUDIT_PREUVE_v0.1.md`.
- [x] Durcir la désactivation MFA : session active, MFA récente et TOTP courant ; code de récupération refusé.
- [x] Assembler la preuve verticale C15 sur les routes sensibles, la reprise après expiration et les refus de récupération dans `SMART_AO_C15_OWNER_EXPERIENCE_FREEZE_v0.1.md`.
- [x] Auditer puis cadrer C16 dans `SMART_AO_C16_PARTAGES_DESTINATAIRES_REVOKATION_AUDIT_CADRAGE_v0.1.md`.
- [x] Implémenter le registre de partage borné et la lecture révocable sur une version exacte.
- [x] Assembler le gel d’expérience C16 dans `SMART_AO_C16_OWNER_EXPERIENCE_FREEZE_v0.1.md`.
- [x] Auditer puis cadrer N01 dans `SMART_AO_N01_CONFLITS_CONTRIBUTIONS_AUDIT_CADRAGE_v0.1.md`.
- [x] N01 — coder le registre de contributions concurrentes et sa résolution append-only ; migration `20260920_0090`, auteurs/sources/révisions conservés, validation bloquée sur conflit ouvert et résolution idempotente prouvée dans `SMART_AO_N01_OWNER_EXPERIENCE_FREEZE_v0.1.md`.
- [x] N01 — conflits de contributions.
- [x] N02 — issue d'opération inconnue ; audit et gel dans `SMART_AO_N02_ISSUE_OPERATION_INCONNUE_AUDIT_CADRAGE_v0.1.md` et `SMART_AO_N02_OWNER_EXPERIENCE_FREEZE_v0.1.md`, export réseau ambigu conservé en `UNKNOWN` côté front sans succès présumé.
- [x] N03 — aperçu destinataire ; route `POST /api/v1/shared-resources/preview`, réponse versionnée sans secret ni identité, neutralité `404 SHARE_NOT_AVAILABLE` et preuve dans `SMART_AO_N03_OWNER_EXPERIENCE_FREEZE_v0.1.md`.
- [x] N04 — relève nominative ; route de demande et d’acceptation, identité résolue côté serveur, idempotence et refus neutres dans `SMART_AO_N04_OWNER_EXPERIENCE_FREEZE_v0.1.md`.
- [x] N05 — disponibilité terrain locale, en attente et confirmée ; états `LOCAL`/`PENDING`/`CONFIRMED`, avertissement de perte et refus hors ligne dans `SMART_AO_N05_OWNER_EXPERIENCE_FREEZE_v0.1.md`.
- [x] Variantes desktop, tablette et mobile utiles sans application parallèle ; audit dans `SMART_AO_PHASE8_RESPONSIVE_AUDIT_PREUVE_v0.1.md`.

**Sortie de phase :** les cas rares d'administration, d'incident et de terrain respectent les mêmes preuves et droits que les parcours principaux.

### PHASE 9 — Couverture produit totale et UX Freeze

- [x] Matérialiser les 16 espaces canoniques C00 à C16 applicables ; registre `web/src/app/canonicalSpaces.ts` et audit `SMART_AO_PHASE9_C00_C16_MATERIALISATION_AUDIT_PREUVE_v0.1.md`.
- [x] Rattacher et vérifier individuellement les 104 surfaces du catalogue ; registre exhaustif et test d'égalité dans `web/src/app/canonicalSpaces.ts` et `SMART_AO_PHASE9_104_SURFACES_AUDIT_CADRAGE_v0.1.md`.
- [x] Fermer PUX-01 : première valeur accessible sans fiche Entreprise complète ; test d’onboarding progressif dans `web/src/app/App.test.tsx`.
- [x] Fermer PUX-03 et PUX-04 sur le flux DCE privé/manuelle, le rattachement serveur Affaire → Consultation/DCE, l’inventaire et la lecture partielle ; preuve dans `SMART_AO_PHASE9_PUX03_PUX04_PREUVE_VERTICALE_v0.1.md`.
- [x] Exécuter G01 à G52 avec les rôles et états difficiles applicables ; G01–G09 sont reliés à leurs actes métier réels (gate P3/P5, contrôle P5, résolution DCE, revue Patron, édition dérivée et inconnus) dans `backend/app/platform/quality/data/g01_g09_business.json` et `SMART_AO_PHASE9_G01_G09_ACTES_METIER_PREUVE_v0.1.md` ; la matrice complète reste dans `SMART_AO_PHASE9_G01_G52_EXECUTION_MATRIX_v0.1.md`.
- [x] Vérifier clavier, lecteur d'écran, contrastes, focus, erreurs et responsive ; audit structurel et preuve dans `SMART_AO_PHASE9_ACCESSIBILITE_G01_G09_AUDIT_PREUVE_v0.1.md`.
- [x] Vérifier l'absence de fuite de marge, de pouvoir induit et de déduction interdite ; audit et preuves dans `SMART_AO_PHASE9_G01_G09_CONFIDENTIALITE_DEDUCTIONS_AUDIT_PREUVE_v0.1.md`.
- [x] Auditer et corriger les défauts ; aucun défaut bloquant n’a été trouvé dans les audits accessibilité et confidentialité.
- [x] Recueillir la validation propriétaire sur les surfaces G01–G09 à partir du paquet de revue `SMART_AO_PHASE9_G01_G09_OWNER_REVIEW_PACKET_v0.1.md` ; confirmation explicite reçue : « Je valide G01–G09 ».
- [x] Produire les `OWNER EXPERIENCE FREEZE` puis l'UX Freeze global ; G01–G09 dans `SMART_AO_G01_G09_OWNER_EXPERIENCE_FREEZE_v0.1.md`, synthèse globale dans `SMART_AO_UX_FREEZE_GLOBAL_v0.1.md`.

**Sortie de phase :** toutes les surfaces, variantes et recettes disposent d'une preuve ; aucun écran secondaire ne reste implicite.

### PHASE 10 — Product Freeze et cahier technique d'exécution

- [x] Consolider les décisions d'expérience validées dans le Product Freeze v1.0 `docs/00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v2.0.md`.
- [x] Approuver et promouvoir le Product Freeze v1.0 comme nouvelle autorité produit/métier ; v0.4 archivé dans `_ARCHIVE/produit_metier/`.
- [x] Écrire le cahier technique d'exécution : architecture cible, modules, données, API, événements et sécurité dans `docs/02_FUTURE_TECHNICAL/SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v2.1.md`.
- [x] Cartographier les exigences v1 vers code, test, migration, observabilité et procédure d'exploitation ; la traçabilité v2 est dans `docs/03_PRODUCT_DESIGN_WORKING/realignment_v2_audit/MASTER_V2_TRACEABILITY_MATRIX.md`.
- [x] Interdire toute divergence silencieuse entre le Product Freeze v1.0 et l'implémentation ; contrat documentaire dans `backend/tests/ops/test_product_freeze_authority_contract.py`.

**Sortie de phase :** une vérité produit v1.0 et une vérité technique exécutable remplacent les documents de transition.

### T0 — Réouverture produit v2 candidate (24 septembre 2026)

- [x] Recevoir les six documents de réalignement, les vérifier en lecture seule puis les promouvoir sous les emplacements actifs prévus.
- [x] Comparer les exigences PF2-01 à PF2-16 aux modèles, services, routes, migrations, tests et surfaces existants ; neuf livrables d'audit sous `docs/03_PRODUCT_DESIGN_WORKING/realignment_v2_audit/`.
- [x] Corriger dans le cahier technique **candidat** l'omission de REC-41 à REC-45 exigées par le Product Freeze v2 candidat.
- [x] Soumettre le paquet d'audit et les arbitrages PF2-01 à PF2-16 au propriétaire ; promotion explicite du Product Freeze v2.0 reçue le 24 septembre 2026.
- [x] Lancer T1 par le contrat pur `RegulatoryProfile` : états d'applicabilité, sources, version et dates testés ; preuve dans `realignment_v2/T1_REGULATORY_PROFILE_TDD.md`.
- [x] Ajouter la persistance tenant-scoped de `RegulatoryProfile` par migration additive et test PostgreSQL, sans moteur juridique automatique : migration `20260924_0091`, structure fermée et rollback du harness DB vérifiés.
- [x] Ajouter la commande/service d'écriture `RegulatoryProfile`, avec idempotence, refus tenant et test PostgreSQL, sans moteur juridique automatique : rejeu reçu et `CASE_NOT_FOUND_OR_FORBIDDEN` vérifiés.
- [x] Décider puis implémenter l'exposition HTTP Patron contrôlée de `RegulatoryProfile`, après contrat UX et test API : `POST /api/v1/patron/cases/{case_id}/regulatory-profiles`, 2 tests API directs, réponse fermée et refus tenant neutre.
- [x] Ajouter la lecture Patron de `RegulatoryProfile` dans C07/C05, avec filtrage tenant et états inchangés : `GET /api/v1/patron/cases/{case_id}/regulatory-profiles`, projection fermée et 1 test API direct.
- [x] Rejouer les gates backend ciblées et vérifier l'intégration du bootstrap avant d'ajouter le composant UX C07 : Ruff, format, mypy 697/697, bootstrap import et tests ciblés verts.
- [x] Ajouter le composant UX C07 de lecture seule du profil réglementaire, sans mutation ni conclusion juridique automatique.

**État :** `READY_WITH_BLOCKERS` pour l'implémentation ; aucun nouveau comportement v2 n'est encore codé, aucune règle juridique/assurantielle/HSE n'est déclarée validée. Le GO conditionnel local et le NO-GO public restent en vigueur.

### PHASE 11 — Qualification de production

- [x] Suites unitaires, intégration PostgreSQL, contrats, end-to-end et non-régression Golden ; 1 717 tests backend passent, 2 tests PIL sont ignorés faute de dépendance optionnelle.
- [x] Vérifier la sécurité de production, les secrets, les dépendances et les uploads hostiles ; audit dans `SMART_AO_PHASE11_PRODUCTION_SECURITY_AUDIT_v0.1.md`.
- [x] Exécuter une preuve isolée de restauration PostgreSQL et de rotation JWT avec environnement éphémère ; 127 tables, tête `20260920_0090`, trigger append-only et rotation atomique vérifiés.
- [ ] Exécuter la restauration et la rotation sur l’environnement VPS de préproduction réel ; aucun VPS disponible, preuve reportée.
- [x] Fiabilité locale : idempotence, concurrence, reprise, files de travail et opérations d’issue inconnue couvertes par les 1 720 tests backend et la simulation locale ; limites VPS conservées.
- [x] Performance locale bornée : 100 requêtes à concurrence 10 en 480 ms, soit 208,33 req/s sur ce poste ; aucun budget VPS ou coût IA déduit.
- [x] Exploitation locale : logs de smoke, métriques de charge, readiness, panne/récupération ClamAV, sauvegarde/restauration et rotation éphémère vérifiés ; supervision distante hors périmètre.
- [x] Migration additive répétée sur une base locale jetable et rollback vérifié : deux `upgrade head`, `downgrade -1`, puis remontée à `20260920_0090`, 127 tables conservées.
- [ ] Préproduction, recette métier, pilote encadré et correction des écarts ; recette locale bornée qualifiée, préproduction réelle et pilote restant hors périmètre.

**Sortie de phase :** les critères de production sont mesurés sur un environnement représentatif et les risques résiduels sont acceptés explicitement.

### PHASE 12 — Mise en production et stabilisation

- [ ] Décision GO/NO-GO propriétaire sur preuves consolidées.
- [ ] Déploiement contrôlé et vérifications post-déploiement.
- [ ] Surveillance renforcée, support de lancement et procédure de retour arrière.
- [ ] Recette réelle du premier cycle complet autorisé.
- [ ] Correction des incidents et clôture de la période de stabilisation.
- [ ] Publication du bilan, des limites connues et de la prochaine feuille de route.

**Sortie de projet :** SMART AO exécute les sept expériences validées, couvre les contrats propriétaires et fonctionne en production avec sécurité, preuves, exploitation et reprise démontrées.

## 5. Tableau de pilotage

| Ordre | Tranche | Statut | Preuve de sortie | Prochaine dépendance |
|---:|---|---|---|---|
| 0 | Gouvernance documentaire | TERMINÉE | autorités et arborescence actives | maintien continu |
| 1A | EXP-01 PAGE-001/002 | TERMINÉE | MFA obligatoire front + serveur | PAGE-003/006 |
| 1B | EXP-01 PAGE-003/006 | TERMINÉE | première Affaire créée et rejouée sans doublon | PAGE-007 |
| 1C | EXP-01 PAGE-007 | TERMINÉE | Accueil réel, 35 tests ciblés et suite front 141/141 | invitation nominative |
| 1D | EXP-01 variantes + preuve assemblée | TERMINÉE | résultat inconnu, reprise minimale, invalidation de rôle et états difficiles parcourus ; 141 tests front + 31 backend ciblés | maquette détaillée et contrat technique consolidé |
| 1E | EXP-01 maquette + contrat technique | TERMINÉE | maquette détaillée, matrice composants/API, invariants et critères de sortie rédigés | tranche verticale création manuelle |
| 1F | EXP-01 tranche verticale implémentée | TERMINÉE | origine manuelle seule exposée, rejeu idempotent et états inconnus couverts ; 142 tests front, build et lint | EXP-02 audit BOAMP |
| 2 | EXP-02 | TERMINÉE | observation qualifiée → Affaire idempotente ; projection P0/P1, lots `UNKNOWN`, échéances et inconnus d’ouverture prouvés côté front, backend et PostgreSQL ; décision P0 explicite, facteurs du score visibles, indépendance score → décision et transformation sans doublon vérifiées ; statut de source, dernier succès, accès manuel et responsive gelés | audit de réception contrôlée DCE |
| 3 | EXP-03 + A2/A3/A4 | TERMINÉE | réception, inventaire, extraction native sourcée, classification partielle, impact rectificatif conservateur, voie manuelle IA, rôles/refus et gel d'expérience prouvés ; corpus Golden réel explicitement à qualifier | EXP-04 |
| 4 | EXP-04 | TERMINÉE | points bloquants sourcés, états natifs, actions autorisées et limites `PARTIAL` | EXP-05 |
| 5 | EXP-05 | TERMINÉE (PARTIAL) | réponse et prix contrôlables dans les limites gelées | EXP-06 |
| 6 | EXP-06 | TERMINÉE | candidate, manifeste, P5, signature, candidature seule justifiée, tentative humaine `UNKNOWN`, export audité et redépôt versionné prouvés ; limites de copie de sauvegarde et de dépôt externe gelées dans `SMART_AO_EXP_06_OWNER_EXPERIENCE_FREEZE_v0.1.md` | EXP-07 |
| 7 | EXP-07 | TERMINÉE | résultat par lot, transmission WON, commande/P6/P7, REX, suspension, fermeture, export demandé et conservation append-only ; limites de réception externe et contentieux gelées dans `SMART_AO_EXP_07_OWNER_EXPERIENCE_FREEZE_v0.1.md` | gouvernance complète |
| 8–9 | Gouvernance + couverture totale | À FAIRE | 104 surfaces, 19 PUX, 52 recettes | freezes globaux |
| 10 | Product Freeze + cahier technique | À FAIRE | deux autorités finales | qualification |
| 11–12 | Qualification + production | À FAIRE | pilote, GO et stabilisation | exploitation continue |

## 6. Journal d'avancement

| Date | Tranche clôturée | Preuve | Étape suivante |
|---|---|---|---|
| 14/09/2026 | Documentation active réorganisée | index et README actifs | cadrer les expériences |
| 14/09/2026 | PAGE-001/PAGE-002 | MFA obligatoire et tests ciblés | PAGE-003 → PAGE-006 |
| 14/09/2026 | PAGE-003 → PAGE-006 | création réelle et rejeu idempotent | PAGE-007 |
| 14/09/2026 | Plan global v0.1 | checklist dépôt + mémoire persistante | auditer PAGE-007 |
| 14/09/2026 | PAGE-007 | Accueil composé, garde sans session, front 141/141, lint et build | invitation nominative |
| 14/09/2026 | Invitation nominative | migration PostgreSQL, jeton haché, 7 jours, réémission sans doublon et réponse neutre ; 3 tests ciblés + 23 non-régressions | acceptation nominative à usage unique |
| 14/09/2026 | Contrat d'acceptation nominative | endpoint 204 sans identité, consommation `accepted_at`, activation identité/membership et mot de passe Argon2id ; ruff, mypy, collecte et diff validés | preuve PostgreSQL puis MFA avant accès métier |
| 14/09/2026 | Acceptation nominative PostgreSQL | migration Alembic jusqu'à `20260914_0068`, acceptation unique, expiration, réponse neutre, session `PASSWORD` sans MFA et garde `STEP_UP_REQUIRED` ; 5 tests ciblés passent | récupération assistée |
| 14/09/2026 | Audit récupération assistée | 13 tests PostgreSQL MFA existants ; codes hachés et à usage unique, mais step-up direct sans révocation ni nouvel enrôlement | coder la preuve de récupération contrôlée |
| 14/09/2026 | Récupération assistée PostgreSQL | code refusé en step-up ; session `PASSWORD` < 5 min + code révoquent sessions, refresh et facteur ; audit, reconnexion et nouvel enrôlement prouvés ; 7 tests ciblés, ruff et mypy passent | changement de contexte et rôles |
| 14/09/2026 | Contrat contexte et rôles | `PATRON_ADMIN` reste l'autorité ; Responsable/Expert deviennent des profils opérationnels de `COLLABORATEUR`, sans capacité ni périmètre supplémentaire ; aucune bascule d'organisation locale | preuve serveur des profils et des refus |
| 14/09/2026 | Profils contexte/rôles PostgreSQL | migration `20260914_0070`, projection `/auth/me`, UI, capacités et affectations inchangées ; 7 tests PostgreSQL, 14 tests front, build, ruff et mypy passent | reprise après interruption et état inconnu |
| 14/09/2026 | Contrat reprise et interruption | session expirée déjà refusée, création idempotente déjà rejouable ; état UI « à vérifier » absent et choisi comme première preuve | coder le rejeu explicite sans succès présumé |
| 14/09/2026 | Résultat inconnu de création | `CreateCasePanel` conserve le formulaire et les trois identifiants, affiche « à vérifier », rejoue la même intention et n'autorise le succès qu'après confirmation ; 28 tests front ciblés et build passent | reprise de session après expiration |
| 14/09/2026 | Reprise de session après expiration | `sessionExpired` efface le jeton et l'acteur ; `App` masque les données, conserve `identity_id`/tenant/rôle/Affaire/navigation en mémoire et restaure seulement le même contexte après MFA ; 35 tests front ciblés, build, ESLint et `git diff --check` passent | assembler la preuve exécutable EXP-01 |
| 14/09/2026 | Prototype exécutable EXP-01 et états difficiles | 31 fichiers front, 141 tests front, 31 tests backend ciblés, refus MFA/bearer, résultat inconnu, expiration, reprise même acteur, invalidation de rôle et erreurs UI parcourus ; build et lint passent. La suite backend non-DB complète compte 1 144 succès, 2 assertions ops historiques et 2 skips PIL hors périmètre | revue propriétaire puis `OWNER EXPERIENCE FREEZE` |
| 14/09/2026 | Dossier de revue propriétaire EXP-01 | `SMART_AO_EXP_01_OWNER_REVIEW_v0.1.md` rassemble le verdict, les preuves, les états difficiles et les limites ; les six arbitrages sont ensuite approuvés par délégation explicite | OWNER EXPERIENCE FREEZE |
| 14/09/2026 | OWNER EXPERIENCE FREEZE EXP-01 | délégation propriétaire reçue ; six arbitrages approuvés et consignés dans `SMART_AO_EXP_01_OWNER_EXPERIENCE_FREEZE_v0.1.md` | maquette détaillée et contrat technique consolidé |
| 14/09/2026 | Maquette détaillée + contrat technique EXP-01 | `SMART_AO_EXP_01_MAQUETTE_DETAILLEE_OWNER_FREEZE_v0.1.md` et `02_FUTURE_TECHNICAL/SMART_AO_EXP_01_CAHIER_TECHNIQUE_EXECUTION_v0.1.md` rédigés à partir du code, des tests et du gel OWNER ; limites et critères de sortie explicités | première tranche verticale d'implémentation |
| 14/09/2026 | Première tranche verticale EXP-01 | incohérence origine corrigée : le panneau n'expose plus les origines sans `origin_reference_id` ; 142 tests front, build, lint et `git diff --check` passent | EXP-02 : audit ingestion/qualification BOAMP |
| 14/09/2026 | Audit et preuve minimale EXP-02 | `SMART_AO_EXP_02_BOAMP_AUDIT_PREUVE_VERTICALE_v0.1.md` fixe le chaînage observation publique → qualification `QUALIFIED` → Affaire unique, avec provenance, idempotence et fraîcheur `observed_at` à exposer ; 22 tests front, 10 tests applicatifs backend et 5 tests scripts passent ; PostgreSQL reste indisponible | coder et tester le chaînage front/API |
| 14/09/2026 | Chaînage EXP-02 front/API | `observed_at` exposé et visible, bouton de conversion après `QUALIFIED`, commande API idempotente et identifiants conservés après résultat inconnu ; 25 tests front, typecheck, lint, build, 15 tests backend/scripts non-DB et ruff passent ; route HTTP et PostgreSQL non validés car l’environnement reste indisponible | preuve PostgreSQL de la conversion et des refus |
| 14/09/2026 | Preuve nominale EXP-02 PostgreSQL | conteneur dédié `smart-ao-v8-postgres` accessible hors sandbox ; 19 tests backend passent pour ingestion, projection fraîcheur, qualification, route HTTP, création `201`, rejeu `200/replayed=true`, provenance et refus ; suite EXP-02 complète 25 tests front + 15 backend/scripts non-DB + 19 backend PostgreSQL | qualification P0/P1, lots, échéances et inconnus explicites |
| 14/09/2026 | Audit et cadrage P0/P1, lots, échéances et inconnus | `SMART_AO_EXP_02_QUALIFICATION_P0_P1_LOTS_ECHEANCES_INCONNUS_AUDIT_CADRAGE_v0.1.md` fixe les états P0/P1, le lot `UNKNOWN` sans inférence, les états d’échéance et le contrat minimal d’inconnus ; aucun code modifié dans cette sous-tranche | coder et tester le statut P0, le périmètre de lots et les inconnus sur la Fiche Opportunité |
| 14/09/2026 | Projection P0/P1, lots, échéances et inconnus | serveur : projection calculée depuis qualification et Affaire, `lot_scope_source=BOAMP`, échéances `KNOWN/MISSING/EXPIRED`, inconnus structurés seulement après ouverture ; front : badges et fiche P1 ; 10 tests front, 5 tests applicatifs, 4 tests PostgreSQL, typecheck, lint, build et Ruff passent ; suite HTTP TestClient toujours bloquée au premier test | auditer puis cadrer la décision de poursuivre ou d’écarter sans score opaque |
| 15/09/2026 | Audit et cadrage de la décision sans score opaque | `SMART_AO_EXP_02_DECISION_POURSUIVRE_ECARTER_AUDIT_CADRAGE_v0.1.md` distingue le score public explicable, les actes P0/P1 et la décision P2 humaine ; aucune table ni transition automatique ajoutée ; l’écart `ATTENTE`/`ABANDON` du domaine actuel est déclaré | implémenter et tester la décision explicite de poursuivre ou d’écarter sans score opaque |
| 15/09/2026 | Implémentation de la décision explicite sans score opaque | le panneau BOAMP affiche la mention non décisionnaire, les facteurs publics et la décision P0 ; l’ouverture d’Affaire exige `P0=TARGETED` ; 11 tests front et 9 tests backend applicatifs passent ; typecheck, lint, build, Ruff et `git diff --check` passent | compléter la preuve HTTP/PostgreSQL de l’indépendance entre score et décision |
| 15/09/2026 | Preuve HTTP/PostgreSQL de l’indépendance score → décision | Uvicorn hors sandbox : `401` sans bearer puis `200` avec score `100` et `P0=UNREVIEWED` ; PostgreSQL dédié : 5 tests passent pour qualification, immutabilité du signal, création/rejeu idempotent et relecture P0/P1 ; TestClient reste bloqué par l’environnement Starlette/httpx | compléter la preuve de transformation idempotente en Affaire sans doublon ni perte de source |
| 15/09/2026 | Preuve de transformation idempotente en Affaire | PostgreSQL dédié : 6 tests passent ; même clé rejouée avec même `case_id`/événements, nouvelle clé sur la même observation refusée `DUPLICATE_FUNCTIONAL_IDENTITY`, une seule Affaire et un seul événement, `business_origin=OPPORTUNITY` et `origin_reference_id` conservés | cadrer la panne de source externe et la saisie manuelle maîtrisée |
| 15/09/2026 | Audit et cadrage panne BOAMP / saisie manuelle | `SMART_AO_EXP_02_SOURCE_OUTAGE_MANUAL_INTAKE_AUDIT_CADRAGE_v0.1.md` confirme `BoampRegistryUnavailable`, le dernier succès réutilisable depuis `boamp_ingestion_runs` et le flux `CreateCase` `MANUAL` ; aucune table ni dépendance nouvelle | implémenter et tester le statut de source, la conservation des observations et l'accès à la saisie manuelle |
| 15/09/2026 | Statut de source, conservation et saisie manuelle | `source_status` fermé dans le contrat Radar ; `AVAILABLE/UNAVAILABLE/UNKNOWN` couverts, dernier `RECORDED` vérifié par PostgreSQL, observations conservées pendant panne, relance et saisie manuelle visibles ; 7 tests PostgreSQL, 3 tests backend ciblés, 6 tests front ciblés, typecheck, lint, build et Ruff passent | revue finale des rôles, refus, responsive utile et gel EXP-02 |
| 15/09/2026 | Gel d'expérience EXP-02 | `SMART_AO_EXP_02_OWNER_EXPERIENCE_FREEZE_v0.1.md` consigne les arbitrages délégués, les refus Patron/Responsable/Expert, le responsive et les preuves ; suite front 148 tests, 7 tests PostgreSQL, build, lint, typecheck, Ruff et `git diff --check` passent | auditer la réception contrôlée, quarantaine, antivirus et reprise d'un DCE |
| 15/09/2026 | Audit et preuve EXP-03 réception/reprise | `SMART_AO_EXP_03_DCE_UPLOAD_AUDIT_CADRAGE_v0.1.md` fixe le contrat mono-objet ; un flux interrompu après écriture partielle est rejeté, le fichier partiel est supprimé et une nouvelle intention pour la même Consultation reste possible ; 19 tests PostgreSQL DCE passent | inventorier les fichiers, versions, formats protégés et éléments illisibles |
| 15/09/2026 | Inventaire DCE par fichier | endpoint `GET /api/v1/dce-versions/{id}/documents` ; états `RECEIVED`, `READ`, `UNSUPPORTED`, `PROTECTED` et erreurs de lecture exposés sans stockage privé ; PDF protégé détecté sans extraction ; 1 test API PostgreSQL, 12 tests extraction, Ruff, typecheck, lint, build et `git diff --check` passent | extraire les formats admis avec des ancres de source vérifiables |
| 15/09/2026 | Extraction native et ancres de source | `SMART_AO_EXP_03_DCE_EXTRACTION_SOURCE_ANCHORS_PREUVE_v0.1.md` fixe PDF/DOCX/XLSX/texte, OCR optionnel, limites et rejeu déterministe ; 12 tests d’extraction passent sur PostgreSQL dédié, dont PDF protégé sans fragment | projeter la classification et la synthèse sans masquer les manques ni les incertitudes |
| 15/09/2026 | Classification et synthèse DCE | `SMART_AO_EXP_03_DCE_CLASSIFICATION_SYNTHESE_PREUVE_v0.1.md` confirme les règles déterministes, preuves sourcées, états `NOT_EXTRACTED`/`UNCLASSIFIED`/`REVIEW_REQUIRED`, readiness partielle et message UI explicite ; 9 tests PostgreSQL et 4 tests front passent | auditer les rectificatifs DCE et invalider uniquement les conclusions dépendantes de la version remplacée, sans effacer l’historique |
| 15/09/2026 | Rectificatifs et impact ciblé | `SMART_AO_EXP_03_DCE_RECTIFICATION_IMPACT_PREUVE_v0.1.md` confirme le nouvel objet rectificatif, la version précédente `SUPERSEDED`, le ledger append-only et la revue ciblée des exigences dépendantes ; 3 tests PostgreSQL impact et 12 tests domaine/retrieval passent | auditer la panne IA, les instructions hostiles et la poursuite manuelle sûre sans masquer l’échec ni envoyer d’action autonome |
| 15/09/2026 | Panne IA, instruction hostile et voie manuelle | `SMART_AO_EXP_03_DCE_IA_PANNE_INSTRUCTION_HOSTILE_PREUVE_v0.1.md` confirme l'absence d'action autonome, le refus explicite d'un texte hostile (`HOSTILE_INSTRUCTION_REVIEW_REQUIRED`) et la continuité de lecture manuelle ; extraction 13 tests, knowledge 30 passés + 2 skips PIL, front 9 tests | auditer les rôles et refus DCE, parcourir les scénarios Golden DCE, puis préparer la revue et le gel d’expérience EXP-03 |
| 15/09/2026 | Rôles, refus, Golden et gel EXP-03 | `SMART_AO_EXP_03_OWNER_EXPERIENCE_FREEZE_v0.1.md` fixe Patron/Responsable/Expert, refus tenant/affectation, non-exécution du contenu hostile, voie manuelle et limites du manifeste Golden vide ; 9 + 9 tests API DCE, 24 tests sécurité/projection, 17 tests Golden, 13 extraction, 30 knowledge (+2 skips PIL), 9 front passent | auditer les points bloquants, leurs sources, leurs responsables et les actions autorisées sans fusionner les états |
| 15/09/2026 | Première projection EXP-04 « À résoudre » | `GET /api/v1/cases/{case_id}/resolution` ; exigences DCE ouvertes, demandes `OPEN` et bloqueurs `OPEN`, sources/états/actions conservés, filtrage d'affectation et refus neutre ; 1 test applicatif + 1 test API PostgreSQL passent | étendre aux rôles Patron/Responsable/Expert et aux lectures séparées risque/contradiction/inconnu |
| 15/09/2026 | Rôles et `REVIEW_REQUIRED` EXP-04 | Collaborateur affecté, Patron du tenant et Collaborateur non affecté vérifiés ; `REVIEW_REQUIRED` reste ouvert avec action `REVIEW_REQUIREMENT` ; 2 tests applicatifs + 1 test API PostgreSQL passent | intégrer les lectures séparées de risques, contradictions et inconnus |
| 15/09/2026 | Risques et contradictions EXP-04 | la projection Patron réutilise les lecteurs CCAP/CCTP et CCTP–DPGF/BPU ; `RISK` et `CONTRADICTION` gardent `REVIEW_REQUIRED`, leurs sources et une action de revue ; les collaborateurs restent filtrés ; 2 tests applicatifs + 1 test API PostgreSQL, Ruff et `git diff --check` passent | rattacher les inconnus BOAMP à une Affaire `OPPORTUNITY` |
| 15/09/2026 | Inconnus BOAMP rattachés EXP-04 | une Affaire `OPPORTUNITY` relit les inconnus calculés depuis l’observation d’origine ; `UNKNOWN`, source BOAMP, action et identité déterministe sont conservés ; une Affaire manuelle reste sans ligne BOAMP ; 3 tests applicatifs + 2 tests API PostgreSQL, mypy, Ruff et `git diff --check` passent | relier sources, impacts, responsables et échéances réellement portés |
| 15/09/2026 | Attributs incomplets EXP-04 | le contrat ajoute `impact` nullable, propage l’échéance de la tâche liée au bloqueur et laisse les attributs absents explicites ; 3 tests applicatifs + 2 tests API PostgreSQL, mypy, Ruff et `git diff --check` passent | préparer la revue et le gel d’expérience EXP-04 |
| 15/09/2026 | Concurrence, questions et validations EXP-04 | révisions périmées refusées, questions seulement référencées sans envoi autonome et achèvement séparé du résultat métier ; 3 tests PostgreSQL ciblés passent | préparer la revue et le gel d’expérience EXP-04 |
| 15/09/2026 | Gel d'expérience EXP-04 | `SMART_AO_EXP_04_OWNER_EXPERIENCE_FREEZE_v0.1.md` fixe les rôles, refus MFA/tenant/affectation, états difficiles, provenance, concurrence et limites `PARTIAL` ; 7 tests PostgreSQL ciblés, mypy, Ruff et `git diff --check` passent | auditer les contrats et le code de réponse/prix existants |
| 15/09/2026 | Audit et preuve import prix EXP-05 | `SMART_AO_EXP_05_REPONSE_PRIX_AUDIT_CADRAGE_v0.1.md` confirme preview → batch normalisé → commit, provenance SHA-256, validations bornées et Patron-only ; front : état « À VÉRIFIER » et rejeu des mêmes identifiants pour preview/commit ; la lecture Case Patron expose les besoins non couverts existants avec leurs sources ; 152 tests front, 121 tests backend PostgreSQL pricing, 4 tests PostgreSQL de résolution, typecheck, lint, build et `git diff --check` passent | auditer hypothèses, devis expirés, capacité et financement |
| 15/09/2026 | Projection économique Patron EXP-05 | `CaseResolutionIndexProjection.economic_coverage` expose hypothèses, validité de devis non démontrée, dernier run de capacité et prévision de trésorerie publiée ; aucun montant ni financement sécurisé n’est déduit ; 3 tests applicatifs + 2 tests API PostgreSQL ciblés, Ruff, mypy et `git diff --check` passent | intégrer la projection dans la surface « Prix / À résoudre » |
| 15/09/2026 | Affichage couverture économique EXP-05 | la surface « Mes affaires / Revue » charge la route Case, affiche les quatre états au Patron et garde `economic_coverage: null` pour le Collaborateur ; 31 fichiers / 152 tests front, typecheck, lint et build passent | auditer marge et scénarios avec données complètes |
| 15/09/2026 | Audit marge et scénarios EXP-05 | `calculate_cost_basis` et `calculate_pricing_scenario_amounts` réutilisent les unités mineures et les points de base ; snapshot publié obligatoire, transitions append-only, import incomplet refusé avant commit ; tests domaine/application/routes existants passent, aucun nouveau registre ajouté | auditer moyens, partenaires et groupements |
| 15/09/2026 | Audit moyens, partenaires et groupements + plan de réponse EXP-05 | capacités `EQUIPMENT`/`TEAM`/`METHOD` versionnées et preuves `VALIDATED` réutilisées ; aucun agrégat partenaire/groupement actif, mandat ou engagement inventé ; `TechnicalResponseDraftRecord` relu et créé côté Collaborateur puis relu Patron-only avec sections, sources et rôle ; 42 tests préparation/revue/routes PostgreSQL, 154 tests front, typecheck, lint, build, Ruff, mypy ciblé et `git diff --check` passent | produire la réponse depuis un plan unique et séparer revue, transmission et autorisation de dépôt |
| 15/09/2026 | Confidentialité EXP-05 par rôle et destinataire | routes financières, bibliothèque entreprise, préparation et remise vérifiées ; contenu et montants absents des contrats non financiers, décision de soumission exigée et dépôt externe explicitement non effectué ; 46 tests PostgreSQL préparation/revue/remise/frontières financières passent | contrôler P2/P3/P4, conflits, versions, revue et gel d’expérience |
| 15/09/2026 | Audit P2/P3/P4, conflits et versions EXP-05 | `SMART_AO_EXP_05_P2_P3_P4_AUDIT_CADRAGE_v0.1.md` confirme les preuves réutilisables et les écarts réels : P2, P3 et P4 restent `PARTIAL` et non autorisants ; fingerprint, révisions, manifestes et garde de soumission sont contrôlés ; 26 tests domaine décision/gate et 65 tests PostgreSQL préparation/remise passent | exécuter la revue verticale EXP-05 et consigner le gel d’expérience |
| 15/09/2026 | Gel d’expérience EXP-05 | `SMART_AO_EXP_05_OWNER_EXPERIENCE_FREEZE_v0.1.md` fixe la provenance, la reprise, la confidentialité, les états `PARTIAL` et les refus ; aucune porte métier n’est déclarée complète et aucun dépôt externe n’est simulé | ouvrir EXP-06 sur la candidate, le manifeste, l’autorisation P5 et la remise humaine |
| 15/09/2026 | Candidate et autorisation P5 EXP-06 | `SubmissionPackageAuthorizationRecord` append-only, version et manifeste exacts, Patron Admin/Delegate avec MFA, porte de décision et export refusé sans autorisation ; lecture Patron-only du manifeste avec entrées/exclusions ; 30 tests PostgreSQL package, 71 préparation/revue/remise, 30 décision/evidence/signature, 160 tests front, typecheck, lint, build, Ruff, mypy ciblé et `git diff --check` passent ; TestClient HTTP reste bloqué par l’environnement | lier signature et preuve de réception au hash exact |
| 15/09/2026 | Signature et preuve de réception liées au manifeste EXP-06 | intentions de signature et preuves manuelles copient le `manifest_sha256` du package ; migration `20260915_0072`/`0073` ; 17 tests signature, 4 tests provider, 33 tests PostgreSQL evidence/package, statique et typecheck passent ; TestClient HTTP reste bloqué par l’environnement | cadrer le rapprochement structuré de réception humaine |
| 15/09/2026 | Lecture structurée des réceptions EXP-06 | route Patron-only `GET /api/v1/patron/submission-packages/{id}/evidence`, projection version/hash/type/`PARTIAL`, UI de relecture et API front ; 163 tests front, typecheck, lint, build, Ruff, format, mypy et `git diff --check` passent ; tentative locale PostgreSQL relancée le 15/09 puis interrompue par `psycopg.OperationalError` pendant la connexion/Alembic (3 erreurs avant exécution des tests) ; miroir Basic Memory non resynchronisé, écriture refusée par la limite hebdomadaire | exécuter la preuve PostgreSQL de lecture et vérifier l’absence de succès externe implicite |
| 19/09/2026 | Réception inconnue, candidature seule et redépôt EXP-06 | `HUMAN_DEPOSIT_ATTEMPT` est append-only avec `UNKNOWN`; `CANDIDATURE_ONLY` exige une justification et omet snapshot/pricing; mode exposé dans API, hook et panneau React; un redépôt crée une nouvelle version et exige une nouvelle autorisation ; 37 tests PostgreSQL package/evidence, 18 tests front ciblés, typecheck, build, Ruff, format, schema-head et `git diff --check` passent | cadrer copie de sauvegarde puis fermer rôles, audit et gel EXP-06 |
| 19/09/2026 | Gel d'expérience EXP-06 | `SMART_AO_EXP_06_OWNER_EXPERIENCE_FREEZE_v0.1.md` gèle P5, candidature seule, export, tentative `UNKNOWN`, redépôt versionné, rôles/refus et limites de copie opérateur ; 37 tests PostgreSQL ciblés, 165 tests front, typecheck, build, Ruff, format, schema-head et `git diff --check` passent | auditer le résultat par lot et la passation EXP-07 |
| 19/09/2026 | Commande et contrôle P6 EXP-07 | `RecordCaseOrder` et `RecordCaseP6Control` sont append-only ; la commande n'accepte qu'un résultat `WON` dans le lot du Case, P6 exige `ACCEPTED`, les réserves et la source restent visibles, et les rejeux ne créent aucun doublon ; migrations `20260919_0079`/`0080`, routes Patron et 2 tests PostgreSQL passent sur le service isolé ; les contraintes de noms et timestamps manquants des tables EXP-07 existantes ont été corrigées | auditer puis implémenter P7 avec `UNKNOWN` et interruption |
| 19/09/2026 | Résultat P7 EXP-07 | `RecordCaseP7Result` est append-only après P6 `APPROVED`, avec états `COMPLETED`/`UNKNOWN`/`INTERRUPTED`, source ou motif imposé selon l'état, réserves conservées et rejeu idempotent ; migration `20260919_0081`, 2 scénarios PostgreSQL et tête Alembic passent | produire le REX P7 et préparer le gel EXP-07 |
| 19/09/2026 | Audit REX et capitalisation EXP-07 | `SMART_AO_EXP_07_REX_CAPITALISATION_AUDIT_CADRAGE_v0.1.md` sépare le retour d'expérience des faits P7, impose une portée de réemploi et refuse la transformation d'un `UNKNOWN` en règle ; aucun registre REX n'existait dans le code vivant | implémenter l'entrée REX append-only liée à P7 |
| 19/09/2026 | REX append-only EXP-07 | `RecordCaseRex` lie un REX Patron à P7, conserve motif/portée/validation/source, autorise le local sur `UNKNOWN` et refuse `ENTERPRISE_PATTERN` sans P7 `COMPLETED`, source et validation `APPROVED` ; migration `20260919_0082`, 2 scénarios PostgreSQL et tête Alembic passent | capitaliser modèles/preuves puis préparer le gel EXP-07 |
| 19/09/2026 | Capitalisation EXP-07 | `SMART_AO_EXP_07_CAPITALISATION_VALIDITE_AUDIT_CADRAGE_v0.1.md` fixe les portées `CASE_ONLY`/`LOT_PATTERN`/`ENTERPRISE_PATTERN`, la validité, la révision et les droits de réemploi sans moteur global ; la prochaine preuve est une lecture Patron avec portée visible | implémenter la lecture Patron de la capitalisation |
| 19/09/2026 | Lecture Patron de la capitalisation EXP-07 | `GET /api/v1/patron/cases/{case_id}/rex` relit les REX du tenant avec lot, portée, validation, source, motif et suivi ; 3 tests PostgreSQL et la tête Alembic passent | cadrer suspension, export, conservation et fermeture |
| 19/09/2026 | Audit suspension/rétention EXP-07 | `SMART_AO_EXP_07_RETENTION_SUSPENSION_EXPORT_AUDIT_CADRAGE_v0.1.md` sépare suspension, export, conservation et fermeture, interdit la fermeture sur `UNKNOWN` ou litige ouvert et conserve `NOT_PERFORMED` pour l'externe | implémenter suspension et fermeture append-only |
| 20/09/2026 | Suspension et fermeture EXP-07 | `CaseDispositionRecord` conserve les actes Patron `SUSPENDED`/`RESUMED`/`CLOSED` sans mutation de résultat ; `CLOSED` exige un P7 `COMPLETED`, refuse tout P7 `UNKNOWN`/`INTERRUPTED` et une suspension `OPEN_LITIGATION`, puis se rejoue par idempotence ; migration `20260920_0083` et 5 tests PostgreSQL passent | implémenter demande d'export et conservation append-only |
| 20/09/2026 | Export demandé et conservation EXP-07 | `CaseExportRequestRecord` et `CaseRetentionRecord` séparent l'intention d'export de la conservation d'une preuve ; aucun champ ni événement ne prétend à une réception externe, qui reste `NOT_PERFORMED` ; migration `20260920_0084` et 6 tests PostgreSQL passent | assembler la preuve verticale et préparer le gel EXP-07 |
| 20/09/2026 | Gel d'expérience EXP-07 | `SMART_AO_EXP_07_OWNER_EXPERIENCE_FREEZE_v0.1.md` gèle les résultats par lot, la passation, P6/P7, REX, capitalisation, suspension, fermeture, export demandé et conservation ; 9 tests PostgreSQL ciblés, tête Alembic, Ruff, format, compilation et `git diff --check` passent | ouvrir C14 gouvernance et délégations |
| 20/09/2026 | Cadrage C14 gouvernance | `SMART_AO_C14_GOUVERNANCE_MEMBRES_DELEGATIONS_AUDIT_CADRAGE_v0.1.md` confirme le socle membership/session existant et isole les écarts : propriété organisationnelle absente, `PATRON_ADMIN` confondu, délégations non persistées et dernier Propriétaire non protégé | séparer propriété et Patron, puis prouver suspension membre/session |
| 20/09/2026 | Propriété et suspension C14 | `TenantOwnerRecord` sépare la propriété organisationnelle de `PATRON_ADMIN`; `MembershipSuspensionRecord` conserve l'acte idempotent et révoque les sessions actives dans la même transaction. Dix tests PostgreSQL, la tête Alembic, Ruff et la compilation passent. | désigner et transférer un Propriétaire sans auto-élévation |
| 20/09/2026 | Désignation et transfert C14 | `TenantOwnerChangeRecord` conserve les actes `DESIGNATED`/`TRANSFERRED`; `TenantOwnerRecord` garde la projection courante avec fin append-only de l’ancien propriétaire. Douze tests PostgreSQL, la tête Alembic, Ruff et la compilation passent. | auditer et cadrer les délégations bornées, la relève et le dernier Propriétaire compromis |
| 20/09/2026 | Audit et cadrage délégations / relève / dernier Propriétaire | `SMART_AO_C14_DELEGATIONS_RELEVE_DERNIER_PROPRIETAIRE_AUDIT_CADRAGE_v0.1.md` confirme que la liste de capacités délégables existe mais qu’aucun registre ni chargement serveur n’est encore présent ; la relève dispose d’affectations append-only mais pas d’un acte de reprise ; R03 reste sans procédure de preuve et de double contrôle. | implémenter la délégation bornée et sa résolution serveur |
| 20/09/2026 | Délégation nominative C14 | `TenantDelegationRecord` et `TenantDelegationEventRecord` bornent capacités, portes, Cases et durée ; le contexte serveur résout les délégations actives ; suspension et révocation conservent les actes. Vingt-et-un tests PostgreSQL ciblés, tête Alembic, Ruff, compilation et `git diff --check` passent. | implémenter la relève, l’acceptation et `NO_ACTIVE_OWNER` |
| 20/09/2026 | Relève nominative et `NO_ACTIVE_OWNER` C14 | `TenantHandoverRecord`/`TenantHandoverEventRecord` conservent la demande, le successeur, le périmètre et l’acceptation idempotente ; `authority_status()` bloque honnêtement l’absence de Propriétaire actif sans récupération implicite. Vingt-trois tests PostgreSQL ciblés passent. | implémenter R03 à double contrôle |
| 20/09/2026 | R03 et gel d’expérience C14 | `TenantRecoveryRecord` conserve preuve d’autorité, approbation et deux supports distincts ; la récupération désigne un membre actif sans rôle métier support. Migration `20260920_0088`, 23 tests PostgreSQL, compilation et Ruff passent ; gel dans `SMART_AO_C14_OWNER_EXPERIENCE_FREEZE_v0.1.md`. | ouvrir C15 sur MFA, récupération et sessions sensibles |
| 20/09/2026 | Audit et durcissement C15 | `SMART_AO_C15_ACCES_MFA_RECUPERATION_SESSIONS_AUDIT_PREUVE_v0.1.md` confirme la garde MFA, la récupération avec révocation complète et corrige la désactivation par code de secours ; 19 tests PostgreSQL ciblés, Ruff et compilation passent. | assembler la preuve verticale C15 |
| 20/09/2026 | Gel d’expérience C15 | `SMART_AO_C15_OWNER_EXPERIENCE_FREEZE_v0.1.md` couvre session limitée, MFA initiale, step-up récent, récupération, désactivation et états difficiles ; 19 tests PostgreSQL/authentification et 12 tests de politique passent. | ouvrir C16 sur les partages et révocations |
| 20/09/2026 | Audit C16 partages | `SMART_AO_C16_PARTAGES_DESTINATAIRES_REVOKATION_AUDIT_CADRAGE_v0.1.md` constate l’absence de registre externe et fixe la version exacte, l’expiration, la révocation append-only, le destinataire et le refus des états inconnus. | implémenter le registre de partage borné |
| 20/09/2026 | Preuve et gel C16 | `TenantResourceShareRecord`/`TenantResourceShareEventRecord` et `ResourceSharingService` prouvent création, lecture, expiration, révocation et idempotence sur une empreinte exacte ; migration `20260920_0089`, 3 tests C16 et suite consolidée de 56 tests passent ; gel dans `SMART_AO_C16_OWNER_EXPERIENCE_FREEZE_v0.1.md`. | ouvrir N01 sur les conflits de contributions |
| 20/09/2026 | Audit N01 conflits | `SMART_AO_N01_CONFLITS_CONTRIBUTIONS_AUDIT_CADRAGE_v0.1.md` constate les révisions optimistes existantes mais l’absence d’un registre métier conservant deux contributions et une résolution humaine. | choisir l’objet DCE versionné minimal |
| 20/09/2026 | Preuve N01 contributions concurrentes | migration `20260920_0090`, `DceContributionConflictService` et garde du handler DCE conservent deux auteurs/sources/révisions, bloquent la validation sur conflit ouvert et enregistrent une résolution append-only idempotente ; 2 tests N01 et suite consolidée C15/C16/N01 de 58 tests passent ; gel dans `SMART_AO_N01_OWNER_EXPERIENCE_FREEZE_v0.1.md` | ouvrir N02 sur l’issue d’opération inconnue |
| 20/09/2026 | Preuve N02 issue d’opération inconnue | audit et gel `SMART_AO_N02_*`, `submissionExportState` front avec `UNKNOWN` sur rupture réseau, dernier état confirmé conservé et action « Vérifier l’export » ; 166 tests front, typecheck et ESLint passent | ouvrir N03 sur l’aperçu destinataire |
| 20/09/2026 | Preuve N03 aperçu destinataire | route `POST /api/v1/shared-resources/preview` réutilisant C16, version/finalité/classification/expiration exposées sans jeton ni identité ; `404 SHARE_NOT_AVAILABLE` neutre ; 7 tests backend ciblés passent | ouvrir N04 sur la relève nominative |
| 20/09/2026 | Preuve N04 relève nominative | routes `POST /api/v1/continuity/handovers` et `/acceptance` réutilisant `ContinuityGovernanceService`, acteur/tenant résolus côté serveur, portée déclarée, acceptation du seul successeur et rejeu idempotent ; client web ajouté ; 3 tests HTTP directs, 21 tests API web, typecheck, build, Ruff, compilation et `git diff --check` passent ; PostgreSQL indisponible sur `127.0.0.1:5433`, preuve C14 existante conservée | ouvrir N05 sur la disponibilité terrain locale, en attente et confirmée |
| 20/09/2026 | Preuve N05 disponibilité terrain | `CollaboratorWizardPanel` distingue pièces chargées et capture `LOCAL`/`PENDING`/`CONFIRMED`, avertit la perte locale, refuse la synchronisation hors ligne et ne persiste aucun secret navigateur ; 7 tests panneau, 21 tests API web, typecheck, lint et build passent | matérialiser les variantes responsive utiles sans créer une application parallèle |
| 20/09/2026 | Audit responsive Phase 8 | les breakpoints existants replient coque, grilles, wizard, workflows et formulaires sans application parallèle ; 168 tests web, typecheck, lint et build passent ; recette visuelle/accessibilité reportée à la phase 9 | matérialiser les 16 espaces canoniques C00 à C16 applicables |
| 20/09/2026 | Matérialisation C00–C16 Phase 9 | registre canonique de 17 identifiants, destinations, statuts réels et surfaces rattachées ; C09/C12 restent `BACKLOG`, aucun écran fictif déclaré ; test de registre, typecheck, lint et build web passent | rattacher et vérifier individuellement les 104 surfaces du catalogue |
| 20/09/2026 | Couverture structurelle des 104 surfaces | égalité exacte entre les 104 IDs du catalogue et les rattachements C00–C16 ; aucun ID manquant, dupliqué ou inventé ; test ciblé, typecheck, lint et build web passent | exécuter PUX-01 à PUX-19 de bout en bout |
| 20/09/2026 | Audit d’exécution PUX-01–PUX-19 | chaque parcours possède une preuve ou une limite explicite ; 11 preuves verticales exploitables, 8 parcours encore partiels ; 170 tests web, typecheck, lint et build passent | fermer PUX-01, puis PUX-03 et PUX-04 |
| 20/09/2026 | PUX-01 première valeur progressive | test App prouvant MFA/contexte puis création de première Affaire sans fiche Entreprise complète ; test ciblé passe | exposer le lien serveur Affaire → Consultation/DCE avant PUX-03/04 |
| 20/09/2026 | PUX-03/PUX-04 fermeture verticale DCE | références `consultation_id` / `applicable_dce_version_id` exposées par le serveur ; route d’attachement admise/vérifiée append-only ; `useDceOpening` + `DceOpeningPanel` couvrent staging → upload binaire privé → admission → rattachement, inventaire avec `processing_state`/`issue_code` et lecture partielle ; 13 tests front ciblés, suite web 187/187, Ruff, compilation, import runtime et `git diff --check` passent ; 31 tests backend DCE passent avec PostgreSQL Docker | exécuter G01 à G52 avec les rôles et états difficiles applicables |
| 20/09/2026 | Première passe G01–G52 | suite backend complète : 1 651 tests passés, 2 skips PIL, 50 échecs ; les échecs se regroupent en fixtures de routes/soumission, résultat Collaborateur sans lot, dette d’architecture et contrats d’exploitation obsolètes ; matrice détaillée dans `SMART_AO_PHASE9_G01_G52_EXECUTION_MATRIX_v0.1.md` | corriger les régressions bloquantes puis rejouer les recettes critiques |
| 20/09/2026 | Seconde passe G01–G52 après corrections | 1 701 tests backend passés, 2 skips PIL ; lot critique DCE/soumission/partage/gouvernance : 311 tests passés ; architecture, identité/C14 et contrats d’exploitation réalignés ; Ruff et `git diff --check` passent | matérialiser les scénarios métier critiques G01–G52 |
| 20/09/2026 | Scénarios G01–G52 matérialisés | registre structuré de 52 scénarios avec espace canonique, rôle, état initial, action, refus attendu, preuve append-only, état final et mode d’exécution ; parseur fermé et 4 tests de contrat verts | exécuter les scénarios critiques G01–G52 sur leurs flux réels, en commençant par G01–G09 |
| 20/09/2026 | Première exécution réelle G01–G09 | PostgreSQL Docker : 105 tests DCE/extraction/classification/staging/analyse/exigences/lecture/routes passent, 5 avertissements, 115,20 s ; G01/G02/G03/G05/G06/G08 restent partiels, G07/G09 ont une preuve technique, G04 n’est pas exécuté ; détail dans `SMART_AO_PHASE9_G01_G09_EXECUTION_PREUVE_v0.1.md` | compléter les fixtures métier G01–G09 et leurs preuves append-only |
| 20/09/2026 | Fixtures métier et rejeu des refus G01–G09 | catalogue `g01_g09_business.json`, parseur fermé, 9 tests unitaires et 1 test PostgreSQL passent ; gate P3/P5, conflit de version, contradiction `REVIEW_REQUIRED`, gap levage avec événement append-only, provenance XLSX, échéance absente, fichier protégé, limite archive et contenu hostile rejoués | relier les preuves aux actes métier encore manquants : résolution humaine G03, décision P3/P5 G01/G02, édition dérivée G05 et revue propriétaire G04/G06 |
| 20/09/2026 | Actes métier G01–G09 reliés | chaque fixture porte `business_act` et `act_proof` ; gate P3/P5, contrôle P5, résolution humaine DCE, gap et inconnue Patron, brouillon dérivé et refus DCE sont reliés à des handlers/projections réels ; suite fixture 10 tests, G03 2 tests PostgreSQL isolés, G05/G02/G06 ciblés verts ; preuve `SMART_AO_PHASE9_G01_G09_ACTES_METIER_PREUVE_v0.1.md` | vérifier clavier, lecteur d’écran, contrastes, focus, erreurs et responsive |
| 20/09/2026 | Audit accessibilité G01–G09 | focus `:focus-visible`, dialogue fermé par `Escape` avec retour du focus, alertes d’erreur, libellés natifs, cibles interactives et reflow responsive ; 187 tests web, typecheck, lint et build passent ; preuve `SMART_AO_PHASE9_ACCESSIBILITE_G01_G09_AUDIT_PREUVE_v0.1.md` | vérifier l’absence de fuite de marge, de pouvoir induit et de déduction interdite |
| 20/09/2026 | Audit confidentialité et déductions G01–G09 | 31 tests architecture/sécurité non base, 29 tests API de frontières PostgreSQL et 9 tests G01–G09 verts ; marge/coût absents des surfaces Collaborateur, `economic_coverage` Patron-only, RAG financier exclu, scores BOAMP non financiers ; preuve `SMART_AO_PHASE9_G01_G09_CONFIDENTIALITE_DEDUCTIONS_AUDIT_PREUVE_v0.1.md` | corriger les défauts puis recueillir la validation propriétaire |
| 20/09/2026 | Paquet de revue propriétaire G01–G09 | aucun défaut bloquant trouvé ; les neuf scénarios, limites, rôles, refus et critères de sortie sont regroupés dans `SMART_AO_PHASE9_G01_G09_OWNER_REVIEW_PACKET_v0.1.md` ; validation métier encore explicitement en attente | recueillir la validation propriétaire sur G01–G09 |
| 20/09/2026 | Validation propriétaire G01–G09 | confirmation explicite reçue : « Je valide G01–G09 » ; le paquet de revue est passé à `VALIDÉ PAR LE PROPRIÉTAIRE` et les neuf lignes sont marquées `VALIDÉ` | produire les `OWNER EXPERIENCE FREEZE` puis l’UX Freeze global |
| 20/09/2026 | OWNER EXPERIENCE FREEZE et UX Freeze global | gel G01–G09 validé, règles communes consolidées pour C00–C16, 104 surfaces, PUX et freezes EXP/N déjà existants ; limites `PARTIAL`, recette lecteur d’écran et Product Freeze restent explicites ; preuves dans `SMART_AO_G01_G09_OWNER_EXPERIENCE_FREEZE_v0.1.md` et `SMART_AO_UX_FREEZE_GLOBAL_v0.1.md` | consolider les décisions d’expérience validées dans le Product Freeze v1.0 |
| 20/09/2026 | Product Freeze v1.0 promu | cahier v0.4, catalogue UX, freezes d’expérience, G01–G09 validés et contraintes de confidentialité/IA/accessibilité consolidés ; v0.4 archivé, v1.0 devient l’autorité active | écrire le cahier technique d’exécution |
| 20/09/2026 | Promotion de l’autorité produit/métier | approbation explicite reçue : « Je promeus le Product Freeze v1.0 et j’archive le v0.4 » ; index, README et références actives réalignés ; dépôt publié sur SMART_AO_LAST | écrire le cahier technique d’exécution |
| 20/09/2026 | Cahier technique d’exécution v1.0 candidat | modular monolith FastAPI/React/PostgreSQL, commandes idempotentes, sécurité, données, événements, IA/RAG, exploitation et tests consolidés sans rewrite Rust ; document `SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v2.1.md` | cartographier chaque exigence gelée vers code, test, migration, observabilité et procédure d’exploitation |
| 20/09/2026 | Matrice de traçabilité Product Freeze | exigences v1.0 reliées à code, tests, migrations, exploitation et gaps explicites dans la matrice archivée ; la matrice v2 T0 est dans `realignment_v2_audit/MASTER_V2_TRACEABILITY_MATRIX.md` | interdire toute divergence silencieuse entre le Product Freeze actif et l’implémentation |
| 20/09/2026 | Contrat anti-divergence Product Freeze | tests d’architecture vérifiant l’unicité du v1.0 actif, l’archivage du v0.4 et la présence de la matrice de traçabilité ; 2 tests passent | exécuter les suites de qualification de production |
| 20/09/2026 | Qualification backend complète | PostgreSQL Docker : 1 717 tests passés, 2 skips PIL, 10 avertissements Starlette/httpx ou alias HTTP non fonctionnels ; la tête de suite reste verte | vérifier la sécurité de production, les secrets, les dépendances, les uploads hostiles, l’audit et la restauration |
| 20/09/2026 | Audit sécurité production | `pip-audit .`, Bandit, detect-secrets, audit pnpm officiel, frontières tenant/MFA/finance, uploads hostiles et contrat Product Freeze vérifiés ; restauration et rotation de secrets restent à exécuter en préproduction ; preuve `SMART_AO_PHASE11_PRODUCTION_SECURITY_AUDIT_v0.1.md` | exécuter la restauration réelle d’une sauvegarde PostgreSQL et la rotation opérationnelle des secrets |
| 20/09/2026 | Preuve locale restauration/rotation | base source isolée migrée puis restaurée dans une base temporaire : 127 tables, tête `20260920_0090`, trigger append-only ; rotation JWT atomique simulée avec fichier 0600 éphémère ; preuve dans `SMART_AO_PHASE11_PRODUCTION_SECURITY_AUDIT_v0.1.md` | exécuter la restauration et la rotation sur le VPS de préproduction réel |
| 20/09/2026 | Runbook préproduction VPS | dimensionnement, installation, secrets, déploiement, backup, restauration, rotation JWT, smoke tests et rollback décrits dans `docs/02_FUTURE_TECHNICAL/SMART_AO_PREPRODUCTION_VPS_RUNBOOK_v0.1.md` ; infrastructure réelle encore absente | provisionner le VPS de préproduction puis exécuter le runbook |
| 20/09/2026 | Contrats d’exploitation préproduction | 45 tests `backend/tests/ops` passent ; scripts shell, Compose digest-pinné, réseau privé, healthchecks, allowlists de secrets, wrappers one-shot, backup/restore et rotation contrôlés | provisionner le VPS de préproduction puis exécuter le runbook |
| 21/09/2026 | Simulation locale complète du stack | registre npm vérifié depuis l’hôte et Docker ; build frontend complet, migration Alembic `20260920_0090`, PostgreSQL, ClamAV, backend, frontend, Caddy et trois workers démarrés ; HTTPS local via Caddy retourne `200` avec `database=ok`, `schema=ok`, `clamav=ok` ; port 80 occupé isolé par override éphémère `18080/18443` ; correction minimale du PID Nginx non-root dans `ops/docker/frontend.Dockerfile` ; 45 tests ops, syntaxe shell et `git diff --check` passent | provisionner le VPS de préproduction puis exécuter le runbook |
| 21/09/2026 | Décision d’avancer sans VPS | aucun fournisseur, CLI cloud, domaine, secret préproduction ou hôte SSH n’est disponible ; la préproduction locale Docker couvre déjà PostgreSQL, ClamAV, migrations, backend, frontend, Caddy, workers, sauvegarde/restauration et rotation simulée ; DNS public, firewall distant, stockage hors site et reprise matérielle restent différés | industrialiser la simulation locale reproductible, puis rejouer restauration, rotation et smoke tests |
| 21/09/2026 | Harness local préproduction reproductible | `scripts/simulate_preprod_local.sh` crée un environnement éphémère, remplace les ports Caddy occupés, construit et démarre le stack complet, attend HTTPS/DB/schema/ClamAV, exécute 20 puis 100 requêtes concurrentes, redémarre backend/frontend/PostgreSQL et les trois workers, provoque une panne ClamAV puis vérifie son retour, sauvegarde PostgreSQL, restaure dans une base isolée, vérifie 127 tables et la tête `20260920_0090`, simule la rotation JWT en fichier `0600`, puis nettoie ; exécution réussie à 151,52 req/s sur ce poste | mesurer les parcours métier lourds sur un corpus DCE local borné, sans extrapoler les résultats au VPS |
| 21/09/2026 | Benchmark DCE local borné | `scripts/benchmark_dce_local.py` mesure trois itérations de texte UTF-8 (20 000 lignes), DOCX (2 000 paragraphes) et XLSX (12 000 cellules) ; tous les formats passent `COMPLETED` ; médianes locales 105,881 ms / 75,915 ms / 182,319 ms ; limites explicites dans `SMART_AO_PHASE11_LOCAL_DCE_BENCHMARK_v0.1.md` | mesurer l’ingestion, la quarantaine et la persistance DCE sur un corpus local borné, sans extrapoler les résultats au VPS |
| 21/09/2026 | Qualification pipeline DCE local | PostgreSQL Docker isolé et migrations fraîches ; ingestion/quarantaine 36 tests en 22,73 s, extraction/classification 22 tests en 25,12 s, exigences/persistance 18 tests en 22,06 s ; total 76 tests passés ; preuve `SMART_AO_PHASE11_LOCAL_DCE_PIPELINE_QUALIFICATION_v0.1.md` ; OCR, RAG, Docling, analyse RC lourde et corpus PDF volumineux restent hors périmètre | mesurer l’analyse RC, les exigences lourdes et la lecture DCE sur un corpus local borné, sans extrapoler les résultats au VPS |
| 21/09/2026 | Parcours DCE lourds local borné | PostgreSQL Docker isolé : analyse RC, exigences lourdes et lecture DCE passent 68 tests en 24,54 s ; sources, règles, tenant-scope, atomicité, limites et rejeux vérifiés ; preuve `SMART_AO_PHASE11_LOCAL_DCE_HEAVY_PATHS_BENCHMARK_v0.1.md` ; OCR, Docling, RAG et gros PDF restent hors périmètre | qualifier les limites OCR, Docling, RAG et gros PDF sur des fixtures locales explicitement bornées, sans extrapoler les résultats au VPS |
| 21/09/2026 | Limites OCR/Docling/RAG/gros PDF | 38 tests passent, 2 tests OCR sont ignorés faute de PIL ; `docling`, RapidOCR, ONNX Runtime, sentence-transformers et PyMuPDF sont absents de `.venv` ; les limites natives PDF/DOCX/texte, archives et projection OCR `REVIEW_REQUIRED` passent ; smoke advanced `NOT_CONFIGURED` explicitement ; preuve `SMART_AO_PHASE11_LOCAL_OPTIONAL_DCE_LIMITS_v0.1.md` | décider l’activation éventuelle des dépendances OCR/Docling/RAG, puis mesurer uniquement celles qui sont installées et approuvées localement |
| 21/09/2026 | Installation contrôlée des dépendances optionnelles | extras `document-ocr`, `document-advanced` et `rag` installés depuis `uv.lock` ; smoke PyMuPDF/Docling, imports RapidOCR, sentence-transformers et Torch CPU vérifiés ; snapshot `BAAI/bge-m3` téléchargé et cache local vérifié ; flags runtime toujours à `0` ; décision `SMART_AO_PHASE11_OPTIONAL_DEPENDENCIES_DECISION_v0.1.md` mise à jour | mesurer OCR/RapidOCR et Docling sur des fixtures locales approuvées, puis vérifier un embedding BGE isolé sans indexation métier |
| 21/09/2026 | Mesure optionnelle sur fixture locale | PyMuPDF `COMPLETED` en 9,2 ms sur 2 fragments ; Docling importable mais `NOT_CONFIGURED` faute d’artefacts modèles et DNS Hugging Face ; RapidOCR `OCR_MODELS_REQUIRED` sans chemins locaux ; cache BGE présent mais embedding CPU non forcé sous contrainte mémoire ; aucune indexation métier | provisionner les artefacts de modèles Docling/RapidOCR et mesurer un embedding BGE dans une fenêtre mémoire dédiée, sans indexation métier |
| 21/09/2026 | Mesure des artefacts et embedding isolé | Docling offline `COMPLETED` en 6 361,68 ms / 61 caractères, RapidOCR `REVIEW_REQUIRED` en 2 818,22 ms / 1 fragment, BGE offline dimension 1 024 en environ 4 435 ms ; aucun index ni accès DB métier | préparer un corpus DCE non financier et qualifier une indexation RAG one-shot, sans données métier réelles |
| 21/09/2026 | Source DCE candidate inventoriée | dossier `DCE Type` : 379 fichiers, 35 financiers, 16 sensibles, 236 non classés, 9 fichiers système ; premier paquet technique `CENTRALE GROUPE ELEC` de 10 PDF RC/CCAP/CCTC/CCTP/planning, hashes calculés, originaux non copiés ni indexés ; preuve `SMART_AO_PHASE11_DCE_SOURCE_INVENTORY_v0.1.md` | revoir les droits/anonymisation du paquet, puis créer une copie de travail non financière hors Git |
| 21/09/2026 | Copie de travail DCE filtrée | 10 PDF copiés hors Git, 30 320 lignes extraites, 567 lignes retirées par motifs financiers/identitaires/secrets, 19 178 lignes techniques conservées ; noms d’établissement, sites, codes postaux et adresses restent visibles, donc statut `REVIEW_REQUIRED` et aucune indexation ; preuve `SMART_AO_PHASE11_DCE_WORKING_COPY_SCREENING_v0.1.md` | revoir manuellement l’anonymisation et les droits avant toute indexation BGE/RAG |
| 21/09/2026 | Copie redacted et embedding BGE one-shot | seconde passe : 687 lignes redacted, motifs email/téléphone/code postal/adresse absents ; 10 fragments encodés offline en 18 390,81 ms, dimension 1 024, zéro écriture DB ; statut toujours `REVIEW_REQUIRED` avant index permanent | faire approuver la copie redacted puis qualifier l’indexation RAG one-shot non financière |
| 21/09/2026 | Paquet de revue propriétaire corpus DCE | paquet `SMART_AO_PHASE11_DCE_CORPUS_OWNER_REVIEW_PACKET_v0.1.md` produit avec périmètre, exclusions, hashes, limites, critères de requêtes et décision `APPROUVÉ/REFUSÉ` ; index permanent toujours interdit | obtenir la validation propriétaire du paquet redacted |
| 21/09/2026 | Qualification RAG one-shot redacted | 116 fragments redacted, 3 requêtes, vecteurs dimension 1 024, 181 556,10 ms, zéro écriture DB et aucun index persistant ; échéance → RC et planning → planning ; prescriptions communes → résultat CCTP/CCAP, donc retrieval `PARTIAL` | corriger le retrieval des prescriptions communes et rejouer la qualification RAG temporaire |
| 21/09/2026 | Correction retrieval source-aware | `scripts/qualify_redacted_rag.py` préfixe uniquement le titre de source dans l’entrée d’embedding ; rejoue 116 fragments et 3 requêtes en 201 814,11 ms ; RC, CCTC et Planning sont tous retrouvés dans le top 3 ; aucun index ni écrit DB | auditer les ancres et les refus du retrieval RAG temporaire avant toute indexation persistante |
| 21/09/2026 | Audit ancres/refus RAG temporaire | ancres source-aware 3/3 ; tests existants couvrent tenant/Case/version/classification et exclusion `FINANCIAL_PRIVATE` ; index permanent absent ; refus financier explicite à la frontière applicative reste à fermer ; preuve `SMART_AO_PHASE11_DCE_RAG_ANCHOR_REFUSAL_AUDIT_v0.1.md` | fermer le refus financier explicite à la frontière applicative avant toute indexation RAG persistante |
| 21/09/2026 | Refus financier explicite RAG | `RagRetrievalService` refuse une requête financière hors scope privé avec `FinancialRetrievalQueryRejected/FINANCIAL_RETRIEVAL_SCOPE_REQUIRED` ; 2 tests de contrat, suite knowledge 7/7 et ops 45/45 passent ; aucune indexation persistante | rejouer le corpus redacted via le service RAG avec refus financier, puis supprimer l’index jetable |
| 21/09/2026 | Rejeu via le vrai service RAG | 116 fragments redacted indexés en mémoire, RC/CCTC/Planning retrouvés dans le top 3 ; requête financière refusée `FINANCIAL_RETRIEVAL_SCOPE_REQUIRED` ; 215 732,69 ms, zéro écriture DB, index détruit à la fin ; script `scripts/qualify_redacted_rag_service.py` | auditer la réponse RAG, les ancres et la suppression de l’index jetable |
| 21/09/2026 | Audit final RAG temporaire | 3/3 ancres attendues, locators complets, 0 marqueur financier dans les réponses, refus financier `REFUSED`, 116 entrées mémoire puis 0 après nettoyage ; aucun index persistant ; preuve `SMART_AO_PHASE11_DCE_RAG_ANCHOR_REFUSAL_AUDIT_v0.1.md` | publier le verdict RAG local et conserver l’indexation persistante désactivée jusqu’à la décision d’exploitation |
| 21/09/2026 | Verdict RAG local publié | `SMART_AO_PHASE11_LOCAL_RAG_VERDICT_v0.1.md` classe le RAG `QUALIFIÉ POUR EXPÉRIMENTATION LOCALE — PAS DE PRODUCTION` ; flags runtime restent à `0`, aucun index permanent, corpus et limites explicités | qualifier les critères Phase 11 restants et documenter les limites avant tout déploiement public |
| 21/09/2026 | Suite backend complète après extras | 1 718 tests passent sur la passe complète ; 2 échecs initiaux dus à `icalendar` retiré par la synchronisation uv ; extra calendrier restauré et 2/2 tests ciblés passent ; couverture effective verte sur 1 720 tests collectés ; 10 avertissements non fonctionnels | qualifier les critères Phase 11 restants et documenter les limites avant tout déploiement public |
| 21/09/2026 | Verdict qualification Phase 11 | backend 1 720 tests collectés verts, frontend 187/187, ops 45/45, pip-audit sans vulnérabilité, pnpm audit officiel 0, Bandit vert, stack local/restauration/rotation/RAG temporaire vérifiés ; verdict `QUALIFIÉ LOCALEMENT — PAS PRÊT POUR PRODUCTION PUBLIQUE` dans `SMART_AO_PHASE11_QUALIFICATION_VERDICT_v0.1.md` ; VPS, Golden DCE réel, intégrations externes et detect-secrets indisponible restent des limites | préparer le dossier GO/NO-GO local et maintenir les limites VPS/Golden DCE avant toute ouverture publique |
| 21/09/2026 | Dossier GO/NO-GO local | paquet `SMART_AO_PHASE11_GO_NO_GO_LOCAL_PACKET_v0.1.md` produit ; preuves vertes, bloqueurs NO-GO public, conditions de réouverture et décision propriétaire attendue explicités ; proposition `GO CONDITIONNEL LOCAL / NO-GO PUBLIC` | soumettre le dossier GO/NO-GO local à la décision propriétaire |
| 21/09/2026 | Soumission GO/NO-GO au propriétaire | dossier soumis avec `NO-GO PUBLIC MAINTENU` coché et `GO CONDITIONNEL LOCAL` laissé en attente ; aucune ouverture ni donnée client autorisée | recueillir la décision propriétaire sur le GO conditionnel local |
| 21/09/2026 | Décision propriétaire GO conditionnel local | approbation explicite reçue : « J’approuve le GO conditionnel local et je maintiens le NO-GO public » ; conception, code et qualification locale autorisés ; VPS et ouverture publique reportés à la phase d’exploitation | poursuivre la conception et la qualification locale des parcours restants, sans ouverture publique |
| 22/09/2026 | Reprise des gates backend après audit | Ruff, format et mypy passent sur 688 fichiers ; erreurs de production et contrats de test corrigées ; la suite complète a donné 1 719 réussites et un seul échec de typage de faux policy, corrigé puis rejoué avec succès ; PostgreSQL Docker local utilisé | rejouer la suite backend complète après correction du dernier contrat de test |
| 22/09/2026 | Rejeu backend complet après correction | PostgreSQL Docker local, tête Alembic appliquée automatiquement ; `uv run pytest backend/tests -q` : **1 720 tests passés**, 10 avertissements non bloquants, 658,55 s ; aucun échec backend | poursuivre la qualification locale des critères Phase 11 restants, sans ouverture publique |
| 22/09/2026 | Simulation préproduction locale bornée | contexte Docker réduit de plus d'1 Go à 1,565 Mo via `.dockerignore` ; build frontend/backend, HTTPS readiness `database/schema/clamav=ok`, 20 requêtes concurrentes, 100 requêtes à concurrence 10 en 480 ms (208,33 req/s), redémarrages backend/frontend/PostgreSQL et workers, panne/récupération ClamAV, sauvegarde, restauration isolée de 127 tables à `20260920_0090` et rotation JWT mode 600 : **PASS** ; aucune extrapolation VPS | qualifier localement la migration additive répétée et le rollback contrôlé |
| 22/09/2026 | Migration additive répétée et rollback local | base PostgreSQL temporaire dédiée ; `upgrade head` initial et répété idempotents (`20260920_0090`, 127 tables), `downgrade -1` vers `20260920_0089`, puis `upgrade head` restauré avec la même tête et le même nombre de tables ; base supprimée après preuve | préparer la recette métier locale bornée, sans pilote public ni ouverture publique |
| 22/09/2026 | Recette métier locale bornée | paquet `SMART_AO_PHASE11_RECETTE_METIER_LOCALE_BORNEE_v0.1.md` ; G01–G09, P6/P7 et contrats ops : 62 tests verts ; frontend : 187/187 tests verts sur 34 fichiers ; aucune donnée client ni intégration externe ; verdict `PASS LOCAL BORNÉ`, `NO-GO PUBLIC` maintenu | traiter les écarts de recette locale bornée et maintenir le NO-GO public |
| 22/09/2026 | Requalification des écarts de recette | typecheck, lint et build frontend rejoués avec succès ; écarts restants classés sans faux succès : lecteur d’écran réel, Golden DCE/droits, VPS et reprise matérielle, fournisseurs externes, detect-secrets/Trivy nécessitent un environnement ou une attestation absente localement | poursuivre les corrections et preuves locales sans fermer artificiellement les limites externes |
| 22/09/2026 | Corrections locales et rejeu sécurité | assertions applicatives remplacées par des refus explicites, hash factice reconnu comme fixture ; `pip-audit` sans vulnérabilité connue, `pnpm audit` officiel à 0 vulnérabilité, Bandit complet à 0 alerte ; tests ciblés invariants 10/10 verts ; limites externes inchangées | poursuivre les corrections et preuves locales sans fermer artificiellement les limites externes |
| 22/09/2026 | Rejeu complet après corrections locales | backend `1 720/1 720` tests verts avec PostgreSQL Docker local, 10 avertissements non bloquants ; frontend `187/187`, typecheck, lint et build verts ; hook `detect-secrets` CI vert avec baseline réaligné ; Trivy et limites externes restent ouverts | poursuivre les corrections et preuves locales sans fermer artificiellement les limites externes |
| 22/09/2026 | Revue statique des images locales | images backend/workers et frontend inspectées en utilisateurs non-root (`smartao`, `nginx`) ; bases digest-pinnées vérifiées ; healthcheck frontend dans l’image, healthchecks backend dans Compose ; Compose refuse correctement une configuration sans secrets runtime | poursuivre les corrections et preuves locales sans fermer artificiellement les limites externes |
| 22/09/2026 | Réduction des avertissements API | constantes `HTTP_422_UNPROCESSABLE_ENTITY` remplacées par `HTTP_422_UNPROCESSABLE_CONTENT` ; Ruff, format et mypy verts ; suite API **540/540** verte ; seul avertissement restant issu de Starlette/httpx, hors code projet | poursuivre les corrections et preuves locales sans fermer artificiellement les limites externes |
| 22/09/2026 | Simulation locale après génération dynamique des secrets | stack éphémère reconstruite avec secrets aléatoires, smoke HTTPS/DB/schema/ClamAV vert, charge bornée 100/concurrence 10 en 1 170 ms (85,47 req/s), redémarrages, panne/récupération ClamAV, backup/restauration 127 tables et rotation JWT : **PASS** ; mesure locale non extrapolée au VPS | poursuivre les corrections et preuves locales sans fermer artificiellement les limites externes |
| 22/09/2026 | Réalignement documentaire du README | quatre liens historiques supprimés remplacés par documentation active, index de références, Product Freeze v1.0, cahier technique et plan global ; vérification automatique : 6 liens locaux, 0 manquant | poursuivre les corrections et preuves locales sans fermer artificiellement les limites externes |
| 24/09/2026 | Promotion Product Freeze v2 et réalignement documentaire | six documents déplacés depuis `_Update`, v1.0 et l'ancienne matrice archivés, index/README/cahier technique/test d'autorité réalignés ; audit T0 et REC-41–45 intégrés ; 2/2 tests d'autorité ciblés verts, aucune migration ni capacité v2 codée | lancer T1 par la première capacité v2 caractérisée ; maintenir le NO-GO public |
| 24/09/2026 | T1 contrat pur RegulatoryProfile | RED `ModuleNotFoundError` puis GREEN ; 4 tests, Ruff/format/mypy ciblés verts, couverture ciblée 91 % ; aucun ORM, endpoint, fournisseur ou calcul juridique ajouté | ajouter la persistance tenant-scoped de `RegulatoryProfile` par migration additive et test PostgreSQL |
| 24/09/2026 | T1 persistance RegulatoryProfile | modèle SQLAlchemy tenant-scoped, migration additive `20260924_0091`, checks fermés, FK composites Affaire/tenant, index version et test PostgreSQL sur base éphémère : 5 tests combinés verts | ajouter la commande/service d'écriture `RegulatoryProfile`, avec idempotence, refus tenant et test PostgreSQL |
| 24/09/2026 | T1 commande/service RegulatoryProfile | capability Patron dédiée, service d'autorisation, handler via dispatcher, rejeu idempotent et refus d'une Affaire d'un autre tenant ; PostgreSQL : 2 tests métier verts, Ruff/mypy ciblés verts ; aucun endpoint HTTP ni moteur juridique | décider puis implémenter l'exposition HTTP Patron contrôlée de `RegulatoryProfile`, après contrat UX et test API |
| 24/09/2026 | T1 route Patron RegulatoryProfile | `POST /api/v1/patron/cases/{case_id}/regulatory-profiles` rattaché à C07 sans nouvelle destination ; contrat fermé, 201 nominal et 404 `CASE_NOT_FOUND_OR_FORBIDDEN` prouvés par 2 tests API directs ; aucun calcul juridique | ajouter la lecture Patron de `RegulatoryProfile` dans C07/C05, avec filtrage tenant et états inchangés |
| 24/09/2026 | T1 lecture Patron RegulatoryProfile | `GET /api/v1/patron/cases/{case_id}/regulatory-profiles` renvoie les versions et conserve `UNKNOWN_APPLICABILITY` ; filtrage tenant porté par le service ; suite API ciblée 3/3, Ruff et mypy verts | rejouer les gates backend ciblées et vérifier l'intégration du bootstrap avant d'ajouter le composant UX C07 |
| 24/09/2026 | Gates backend et bootstrap RegulatoryProfile | Ruff vert, format 697 fichiers, mypy **697/697** sans erreur, suite domaine/API/autorité **9 tests verts**, imports bootstrap/route vérifiés ; aucun composant UX ni calcul juridique ajouté | ajouter le composant UX C07 pour lire les états sans les modifier |
| 24/09/2026 | UX C07 RegulatoryProfile | hook/API GET, panneau de lecture Patron intégré à C07, état `UNKNOWN_APPLICABILITY` conservé et aucune action de mutation affichée ; frontend **188/188 tests**, typecheck et lint verts | rejouer la suite complète backend après l'ajout UX puis préparer la tranche suivante |
| 24/09/2026 | Correction des gates après intégration T1 | dette application/infrastructure isolée dans le handler, tête attendue mise à `20260924_0091`, architecture/schema tests ciblés verts ; API RegulatoryProfile 3/3 verts | rejouer la suite complète backend sur PostgreSQL éphémère |
| 24/09/2026 | Suite backend complète après UX et T1 | PostgreSQL éphémère : **1 727 tests verts**, 2 contrats ops corrigés pour la tête `20260924_0091`, puis suite ciblée ops **31/31** verte ; un avertissement Starlette/httpx reste externe au code | préparer la tranche suivante après validation du contrat produit et des gates |
| 24/09/2026 | Clôture T1 RegulatoryProfile | suite complète backend `1 727` tests verts sur PostgreSQL éphémère ; contrats ops réalignés sur `20260924_0091`, preuve API/UX RegulatoryProfile et bootstrap validés ; T1 sans moteur juridique terminé | auditer les signaux contractuels existants et fixer la plus petite preuve baseline → dérogation → impact |
| 24/09/2026 | T2 preuve baseline → dérogation → impact | audit des signaux CCAP/CCTP existants ; contrat domaine `ContractBaselineDeviationImpact` ajouté avec source obligatoire, dérogation/impact facultatifs et états fermés ; 5 tests domaine verts ; aucune inférence juridique automatique | persister tenant-scoped la preuve baseline → dérogation → impact avec idempotence et refus tenant |
| 24/09/2026 | Rejeu backend complet après preuve T2 | PostgreSQL éphémère isolé, suite `backend/tests` : **1 734 tests passés**, 1 avertissement Starlette/httpx externe ; conteneur supprimé après exécution, aucune base persistante touchée | persister tenant-scoped la preuve baseline → dérogation → impact avec idempotence et refus tenant |
| 24/09/2026 | T2 persistance baseline → dérogation → impact | migration additive `20260924_0092`, table tenant-scoped append-only, unicité fonctionnelle par Affaire/observation/révision, handler via dispatcher avec rejeu idempotent et refus `CASE_NOT_FOUND_OR_FORBIDDEN` ; upgrade → downgrade → upgrade Alembic validé sur PostgreSQL éphémère | ajouter l'exposition Patron contrôlée de la preuve baseline → dérogation → impact après contrat UX et test API |
| 24/09/2026 | T2 exposition Patron contrôlée | contrat fermé `ContractBaselineImpactPageResponse`, route GET tenant-scoped en lecture seule, états et ancres conservés ; test API direct et domaine **6/6 verts** ; aucune mutation depuis l'UX | préparer le composant UX C07 de consultation de la preuve baseline → dérogation → impact |
| 24/09/2026 | T2 composant UX C07 | types/API, hook de lecture et panneau C07 ajoutés ; baseline, dérogation, impact, sources et statut affichés sans action de mutation ; frontend **188/188 tests**, typecheck vert, lint sans erreur avec 1 avertissement de dépendance Hook | rejouer les gates backend/frontend après l'intégration UX C07 de la preuve contractuelle |
| 24/09/2026 | Gates backend/frontend après UX C07 | backend ciblé **34/34 tests verts** après réalignement de la tête `20260924_0092` ; frontend **188/188**, typecheck et lint verts sans erreur ni avertissement ; aucune ouverture publique | préparer la revue propriétaire locale de la preuve baseline → dérogation → impact, sans ouverture publique |
| 24/09/2026 | Paquet de revue propriétaire T2 | `T2_OWNER_REVIEW_BASELINE_DEROGATION_IMPACT.md` produit avec preuve, invariants, limites et décision locale demandée ; NO-GO public maintenu | attendre la décision propriétaire locale sur la preuve baseline → dérogation → impact, sans ouverture publique |
| 24/09/2026 | Décision propriétaire locale T2 | représentation `source → baseline → dérogation → impact → revue humaine` approuvée ; limites juridiques, externes et NO-GO public maintenus | cadrer l'acte de revue humaine de la preuve contractuelle, avec décision explicite et sans moteur juridique automatique |
| 24/09/2026 | Contrat d'acte de revue humaine T2 | `ContractProofReview` ajouté : relecteur, décision fermée, révision et justification obligatoires ; 2 tests domaine verts ; aucune conclusion juridique ni mutation de la preuve | persister l'acte de revue humaine tenant-scoped, append-only et idempotent |
| 24/09/2026 | Persistance de l'acte de revue humaine T2 | migration `20260924_0093`, modèle tenant-scoped append-only et handler dispatcher ajoutés ; Ruff/imports verts ; validation PostgreSQL dédiée encore à exécuter | exécuter la migration `20260924_0093` et les tests PostgreSQL de l'acte de revue humaine |
| 24/09/2026 | Validation PostgreSQL de l'acte de revue humaine | migration `20260924_0093` validée par upgrade → downgrade → upgrade sur PostgreSQL éphémère ; contrats domaine et preuve T2 **8/8 tests verts** ; aucune base persistante touchée | exposer la lecture Patron de l'acte de revue humaine dans C07, sans mutation ni conclusion juridique |
| 24/09/2026 | Revue humaine intégrée à C07 | types/API, hook de lecture et projection de décision/rationale ajoutés ; frontend **188/188 tests**, typecheck et lint verts ; aucune mutation UX | rejouer les gates backend/frontend après intégration de la revue humaine dans C07 |
| 24/09/2026 | Gates finales après revue humaine C07 | backend ciblé **42/42 tests verts** après réalignement de la tête `20260924_0093` ; frontend **188/188**, typecheck et lint verts ; NO-GO public maintenu | préparer la tranche suivante de revue contractuelle locale, sans ouverture publique |
| 24/09/2026 | Suite backend complète après revue humaine | PostgreSQL éphémère : **1 738 tests verts**, 1 avertissement Starlette/httpx externe ; conteneur supprimé après exécution, aucune base persistante touchée | préparer la tranche suivante de revue contractuelle locale, sans ouverture publique |
| 24/09/2026 | Paquet T3 cycle de vie de revue contractuelle | `T3_CONTRACT_REVIEW_LIFECYCLE_PACKET.md` produit avec périmètre, critères d'acceptation, refus et limites ; NO-GO public maintenu | implémenter le cycle de vie append-only de la revue contractuelle, avec projection du dernier état confirmé |
| 24/09/2026 | T3 cycle append-only et projection | historique conservé via `list_for_case`, projection `latest_for_case` ajoutée par preuve/révision, route Patron `/contract-proof-reviews/latest` exposée en lecture seule ; Ruff, compilation et 8 tests domaine verts | ajouter les tests PostgreSQL de rejeu, révision et projection du dernier état de revue |
| 24/09/2026 | Tests PostgreSQL du cycle de revue | table `contract_proof_reviews` vérifiée sur PostgreSQL éphémère (tenant, unicité preuve/révision, décisions fermées) ; projection déterministe historique → dernier état ; **2/2 tests verts** | rejouer la suite backend/frontend complète après fermeture des tests de cycle de revue |
| 24/09/2026 | Rejeu complet après cycle de revue | backend PostgreSQL éphémère **1 740 tests verts**, 1 avertissement Starlette/httpx externe ; frontend **188/188**, typecheck, lint et build verts ; conteneur supprimé, NO-GO public maintenu | préparer la prochaine tranche contractuelle locale après revue des résultats complets, sans ouverture publique |
| 24/09/2026 | Paquet T4 révision contrôlée | `T4_CONTRACT_PROOF_REVISION_PACKET.md` produit avec contrat, refus, projection et preuves attendues ; aucun changement produit public | implémenter la révision contrôlée d'une preuve contractuelle, sans mutation de l'historique |
| 24/09/2026 | T4 révision contrôlée append-only | handler exige la révision précédente pour `n > 1`, crée une nouvelle identité sans mutation, et conserve la contrainte tenant/Affaire/observation ; 3 tests de contrat de commande verts | ajouter la preuve PostgreSQL de la révision 2, du refus de révision manquante et de l'idempotence |
| 24/09/2026 | Preuve PostgreSQL de révision contrôlée | deux révisions append-only et une revue de révision 2 insérées ; contrainte de rejeu/unicité vérifiée ; projection déterministe ; **3/3 tests PostgreSQL verts** | rejouer les gates complètes après preuve PostgreSQL de la révision contrôlée |
| 25/09/2026 | Gates complètes après révision contrôlée | backend PostgreSQL éphémère **1 744 tests verts**, 1 avertissement Starlette/httpx externe ; frontend **188/188**, typecheck, lint et build verts ; conteneur supprimé, NO-GO public maintenu | préparer la prochaine tranche contractuelle locale, sans ouverture publique |
| 25/09/2026 | Paquet T5 invalidation après rectificatif | `T5_CONTRACT_PROOF_INVALIDATION_PACKET.md` produit avec supersession, nouvel acte de revue, projection C07 et refus tenant ; aucun changement public | implémenter l'invalidation contrôlée après rectificatif, sans suppression de l'historique |
| 25/09/2026 | Migration T5 `SUPERSEDED` validée | `20260925_0094` validée sur PostgreSQL éphémère : upgrade, contrainte `SUPERSEDED`, downgrade et upgrade à nouveau ; base supprimée après preuve | ajouter les tests de projection `SUPERSEDED` et de nouvelle revue après rectificatif |
| 25/09/2026 | Tests de projection `SUPERSEDED` | contrat de commande `SUPERSEDED` et séparation révision ancienne/nouvelle ajoutés ; tests domaine verts ; tests DB nécessitent la variable PostgreSQL éphémère dédiée avant clôture | rejouer les tests `SUPERSEDED` avec PostgreSQL explicitement ciblé, puis fermer T5 |
| 25/09/2026 | Clôture T5 `SUPERSEDED` | PostgreSQL explicitement ciblé : projection, révision et nouvelle revue **8/8 tests verts** ; migration `0094` déjà validée upgrade/downgrade/upgrade ; historique append-only et NO-GO public maintenus | préparer la tranche suivante après clôture T5, sans ouverture publique |
| 25/09/2026 | Paquet T6 chronologie C07 | `T6_CONTRACT_PROOF_TIMELINE_PACKET.md` produit avec ordre déterministe, états historiques, sources et preuves attendues ; NO-GO public maintenu | implémenter la chronologie C07 des preuves et revues, sans fusion silencieuse |
| 25/09/2026 | Projection backend chronologie C07 | service `timeline_for_case` et route Patron `/contract-proof-timeline` ajoutés en lecture seule ; ordre révision/date déterministe, états historiques conservés ; Ruff et compilation verts | ajouter les tests API/frontend de la chronologie C07, sans mutation |
| 25/09/2026 | Tests API/frontend chronologie C07 | API timeline Patron **1/1 vert**, C07 **189 tests verts**, typecheck et lint verts ; `SUPERSEDED` reste visible et aucune action de mutation n'est exposée | rejouer les gates complètes après la chronologie C07 |
| 25/09/2026 | Gates complètes après chronologie C07 | suite backend complète : **1 745 tests verts**, 2 assertions ops obsolètes corrigées pour `20260925_0094`, puis gate ops **33/33** verte ; frontend **189/189**, typecheck, lint et build verts ; avertissement Starlette/httpx externe | préparer la tranche suivante après clôture des gates C07, sans ouverture publique |
| 25/09/2026 | Paquet T7 revue propriétaire chronologie C07 | `T7_OWNER_REVIEW_TIMELINE_PACKET.md` produit avec preuves, limites et décision locale demandée ; NO-GO public maintenu | recueillir la revue propriétaire locale de la chronologie C07, sans ouverture publique |
| 25/09/2026 | Validation propriétaire chronologie C07 | approbation explicite reçue : conservation de `SUPERSEDED`, `REJECTED`, `NEEDS_CLARIFICATION`, lecture seule, aucune conclusion juridique et NO-GO public maintenu | préparer la tranche suivante de consultation contractuelle locale, sans ouverture publique |
| 25/09/2026 | Paquet T8 consultation filtrée | `T8_CONTRACT_TIMELINE_QUERY_PACKET.md` produit avec filtres, pagination, invariants tenant et preuves attendues ; aucun élargissement public | implémenter la consultation filtrée tenant-scoped de la chronologie contractuelle |
| 25/09/2026 | Consultation filtrée chronologie T8 | service et route Patron acceptent révision, état, limite et offset bornés, avec filtrage avant pagination ; lecture seule et tenant-scoped conservés ; Ruff/compilation à rejouer | ajouter les tests PostgreSQL/API des filtres et de la pagination de chronologie |
| 25/09/2026 | Tests filtres/pagination chronologie T8 | API filtrée et projection ordre/pagination : **6 tests ciblés verts** ; états historiques et lecture seule conservés | rejouer les gates complètes après consultation filtrée de la chronologie |
| 25/09/2026 | Gates complètes après consultation filtrée | backend PostgreSQL éphémère **1 749 tests verts**, 1 avertissement Starlette/httpx externe ; frontend **189/189**, typecheck, lint et build verts ; conteneur supprimé, NO-GO public maintenu | préparer la tranche suivante après clôture des gates de consultation filtrée, sans ouverture publique |
| 25/09/2026 | Paquet T9 reçu de consultation | `T9_CONTRACT_QUERY_RECEIPT_PACKET.md` produit avec contrat append-only, filtres normalisés, idempotence et refus tenant ; aucun changement public | implémenter le reçu append-only de consultation contractuelle, sans mutation des preuves |
| 25/09/2026 | Persistance T9 du reçu de consultation | modèle tenant-scoped et migration `20260925_0095` ajoutés ; limites `limit/offset` contraintes ; PostgreSQL ciblé **6/6 tests verts** avec historique de revue conservé | ajouter la commande idempotente et le refus tenant du reçu de consultation |
| 25/09/2026 | Tests commande/reçu T9 | idempotence d'identité, tenant/Affaire et bornes `limit` vérifiés sur PostgreSQL éphémère ; **4/4 tests verts** | rejouer les gates complètes après validation du reçu de consultation |
| 25/09/2026 | Gates complètes après reçu de consultation | backend complet **1 751 tests verts**, 2 assertions ops réalignées sur `20260925_0095`, gate ops **33/33** verte ; frontend **189/189**, typecheck, lint et build verts ; NO-GO public maintenu | préparer la tranche suivante après clôture des gates du reçu de consultation, sans ouverture publique |
| 25/09/2026 | Paquet T10 lecture reçus | `T10_QUERY_RECEIPT_READ_PACKET.md` produit avec projection Patron, tenant, pagination et limites ; aucun élargissement public | implémenter la lecture Patron tenant-scoped des reçus de consultation |
| 25/09/2026 | Lecture Patron T10 des reçus | service et route GET tenant-scoped ajoutés, ordre décroissant et pagination bornée ; lecture seule, sans contenu de preuve ; Ruff/compilation verts | ajouter les tests API/PostgreSQL de lecture des reçus, tenant et pagination |
| 25/09/2026 | Tests lecture reçus T10 | projection API des filtres/pagination et contrats de bornes : **3/3 tests ciblés verts** ; tenant et lecture seule conservés | rejouer les gates complètes après lecture Patron des reçus |
| 25/09/2026 | Gates complètes après lecture reçus T10 | backend PostgreSQL éphémère **1 754 tests verts**, 1 avertissement Starlette/httpx externe ; frontend **189/189**, typecheck, lint et build verts ; NO-GO public maintenu | préparer la tranche suivante après clôture des gates T10, sans ouverture publique |
| 25/09/2026 | Paquet T11 export local des reçus | `T11_QUERY_RECEIPT_EXPORT_PACKET.md` produit avec états fermés, idempotence, tenant et absence de réception externe présumée | implémenter la demande d'export local des reçus, sans présumer de réception externe |
| 25/09/2026 | Demande d'export T11 | migration `20260925_0096`, modèle tenant-scoped append-only et commande `RequestContractQueryExport` ajoutés ; état initial `REQUESTED`, refus tenant et rejeu idempotent via dispatcher ; Ruff vert | ajouter les tests PostgreSQL de la demande d'export, de l'idempotence et des états fermés |
| 25/09/2026 | Tests export local T11 | schéma tenant/états fermés et contrat de commande validés sur PostgreSQL éphémère ; **3/3 tests verts** ; aucune réception externe présumée | rejouer les gates complètes après validation de l'export local |
| 25/09/2026 | Gates complètes après export local | backend complet **1 755 tests verts**, 2 assertions ops réalignées sur `20260925_0096`, gate ops **33/33** verte ; frontend **189/189**, typecheck, lint et build verts ; NO-GO public maintenu | préparer la tranche suivante après clôture des gates d'export local, sans ouverture publique |
| 25/09/2026 | Paquet T12 état d'export | `T12_QUERY_EXPORT_STATUS_PACKET.md` produit avec projection Patron, états fermés, tenant et absence de réception externe présumée | implémenter la lecture Patron tenant-scoped de l'état d'export |
| 25/09/2026 | Lecture Patron T12 de l'état d'export | service et route GET tenant-scoped ajoutés, ordre décroissant et pagination bornée ; états conservés sans transition implicite ; Ruff/compilation verts | ajouter les tests API/PostgreSQL de l'état d'export, tenant et pagination |
| 25/09/2026 | Tests état d'export T12 | projection API `UNKNOWN`, filtres et pagination conservés ; contrainte PostgreSQL des états fermés vérifiée ; **3/3 tests verts** | rejouer les gates complètes après validation de la lecture d'état d'export |
| 25/09/2026 | Gates complètes après lecture état d'export | backend PostgreSQL éphémère **1 759 tests verts**, 1 avertissement Starlette/httpx externe ; frontend **189/189**, typecheck, lint et build verts ; NO-GO public maintenu | préparer la tranche suivante après clôture des gates T12, sans ouverture publique |
| 25/09/2026 | Paquet T13 transitions export | `T13_QUERY_EXPORT_TRANSITIONS_PACKET.md` produit avec états fermés, preuve locale READY, UNKNOWN conservé et refus tenant/ordre | implémenter les transitions append-only de l'export local, sans réception externe présumée |
| 25/09/2026 | Transitions export T13 | migration `20260925_0097`, modèle append-only et commande de transition ajoutés ; `READY` exige une preuve locale, `UNKNOWN` reste inconnu, état précédent contrôlé ; Ruff vert | ajouter les tests PostgreSQL des transitions d'export, de l'ordre et de la preuve READY |
| 25/09/2026 | Tests transitions export T13 | états fermés, ordre et référence locale `READY` vérifiés sur PostgreSQL éphémère ; **6/6 tests verts** ; aucune réception externe présumée | rejouer les gates complètes après validation des transitions d'export |
| 25/09/2026 | Gates complètes après transitions export | backend complet **1 763 tests verts**, 2 assertions ops réalignées sur `20260925_0097`, gate ops **33/33** verte ; frontend **189/189**, typecheck, lint et build verts ; NO-GO public maintenu | préparer la tranche suivante après clôture des gates T13, sans ouverture publique |
| 25/09/2026 | Paquet T14 audit export consolidé | `T14_QUERY_EXPORT_AUDIT_PACKET.md` produit avec demande, transitions, état courant, preuve locale et invariants tenant ; aucun élargissement public | implémenter la vue d'audit consolidée de l'export local, sans fusion d'événements |

## 7. Règle de mise à jour

Après chaque tâche significative, Codex doit :

1. cocher la tâche prouvée et retirer son marqueur `[>]` ;
2. placer `[>]` sur une seule prochaine tranche ;
3. ajouter une ligne au journal avec la preuve réellement exécutée ;
4. mettre à jour le statut miroir dans Basic Memory ;
5. terminer son message utilisateur par `Prochaine étape : ...` en reprenant la tranche active de ce document.

En cas d'écart entre ce document et Basic Memory, le présent fichier dans le dépôt fait foi ; Basic Memory sert à l'orientation et doit être resynchronisée immédiatement.
