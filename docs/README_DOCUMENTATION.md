# Documentation SMART AO

## Point d’entrée

La hiérarchie complète des autorités est tenue dans :

[`00_REFERENCE_ACTIVE/00_INDEX_REFERENCE_ACTIVE.md`](00_REFERENCE_ACTIVE/00_INDEX_REFERENCE_ACTIVE.md)

Les nouveaux livrables produit, métier, UX et techniques sont écrits sous `docs/`. Le répertoire `rapports/` reste un historique de travaux antérieurs et ne reçoit plus les livrables actifs de cette phase.

## Source de vérité produit et métier actuelle

La référence unique pour répondre à la question **« Quel SmartAO voulons-nous construire ? »** est désormais :

[`00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md`](00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md)

En cas de contradiction, le Product Freeze v1.0 prévaut. Le cahier v0.4 est archivé dans `_ARCHIVE/produit_metier/`.

La transition a été approuvée par le propriétaire le 20 septembre 2026.

## Références d'implémentation actives

[`01_IMPLEMENTATION_ACTIVE/`](01_IMPLEMENTATION_ACTIVE/) contient l'architecture v3.1, le mandat Phase 0 et le dossier Gate0, y compris Golden DCE et les éléments A0/A1 lorsqu'ils y sont référencés.

Ces documents décrivent l'état technique, la migration et la qualification existante. Ils ne définissent pas le produit lorsqu'ils contredisent le cahier propriétaire v0.4.

## Conception produit en cours

[`03_PRODUCT_DESIGN_WORKING/`](03_PRODUCT_DESIGN_WORKING/) contient les expériences utilisateur en cours de conception. Un fichier `WORK_PROPOSAL` n'est pas une autorité propriétaire.

Le pilotage global, la tranche active et la checklist maintenue par Codex sont dans :

[`03_PRODUCT_DESIGN_WORKING/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md)

Le cycle de travail est :

```text
expérience métier
→ parcours écrit
→ contenu candidat
→ prototype basse fidélité
→ audit du code et tests ciblés
→ preuve verticale minimale
→ revue
→ OWNER EXPERIENCE FREEZE
→ maquette détaillée
→ contrat technique consolidé
→ tranche verticale implémentée et testée
```

Le gel porte sur une expérience cohérente et ses états, pas sur une page isolée avant tout prototype.

## Cycle suivant

La maquette détaillée et le contrat technique consolidé d'EXP-01 sont désormais rédigés :

- [`03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_01_MAQUETTE_DETAILLEE_OWNER_FREEZE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_01_MAQUETTE_DETAILLEE_OWNER_FREEZE_v0.1.md) décrit les surfaces et états à vérifier ;
- [`02_FUTURE_TECHNICAL/SMART_AO_EXP_01_CAHIER_TECHNIQUE_EXECUTION_v0.1.md`](02_FUTURE_TECHNICAL/SMART_AO_EXP_01_CAHIER_TECHNIQUE_EXECUTION_v0.1.md) mappe ces états vers les composants, API, données, sécurité et tests réellement présents.

`02_FUTURE_TECHNICAL/` contient des contrats d'exécution versionnés ; ils deviennent normatifs pour leur tranche seulement après les preuves et la promotion prévues par le plan global.

## EXP-02 en cours

L’audit BOAMP et la plus petite preuve verticale retenue sont décrits dans :

- [`03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_02_BOAMP_AUDIT_PREUVE_VERTICALE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_02_BOAMP_AUDIT_PREUVE_VERTICALE_v0.1.md) — observation publique, qualification humaine, conversion idempotente en Affaire, écarts front et limites.
- [`03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_02_QUALIFICATION_P0_P1_LOTS_ECHEANCES_INCONNUS_AUDIT_CADRAGE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_02_QUALIFICATION_P0_P1_LOTS_ECHEANCES_INCONNUS_AUDIT_CADRAGE_v0.1.md) — états P0/P1, périmètre de lots, états d’échéance et inconnus structurés, avec preuve applicative, front et PostgreSQL.
- [`03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_02_DECISION_POURSUIVRE_ECARTER_AUDIT_CADRAGE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_02_DECISION_POURSUIVRE_ECARTER_AUDIT_CADRAGE_v0.1.md) — séparation entre tri public explicable, actes P0/P1 et décision formelle humaine, avec écarts `ATTENTE`/`ABANDON` déclarés.
- [`03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_02_SOURCE_OUTAGE_MANUAL_INTAKE_AUDIT_CADRAGE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_02_SOURCE_OUTAGE_MANUAL_INTAKE_AUDIT_CADRAGE_v0.1.md) — contrat minimal de panne BOAMP, dernier succès et accès à la saisie manuelle existante.
- [`03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_02_OWNER_EXPERIENCE_FREEZE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_02_OWNER_EXPERIENCE_FREEZE_v0.1.md) — arbitrages, rôles, refus, responsive et preuves gelés pour EXP-02.

Cette tranche est prouvée côté front, HTTP et PostgreSQL : le score est séparé de la décision P0 et ses facteurs sont visibles. La transformation idempotente en Affaire est également prouvée sans doublon ni perte de source. Le statut de panne BOAMP, le dernier succès, l’accès à la saisie manuelle et la revue finale sont implémentés et gelés ; EXP-03 peut commencer.

## EXP-03 clôturée

Les preuves DCE sont suivies dans :

- [`03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_03_DCE_UPLOAD_AUDIT_CADRAGE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_03_DCE_UPLOAD_AUDIT_CADRAGE_v0.1.md) — réception bornée, quarantaine, antivirus, interruption et reprise par nouvelle intention.
- [`03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_03_DCE_EXTRACTION_SOURCE_ANCHORS_PREUVE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_03_DCE_EXTRACTION_SOURCE_ANCHORS_PREUVE_v0.1.md) — extraction PDF/DOCX/XLSX/texte, ancres déterministes et limites.
- [`03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_03_DCE_CLASSIFICATION_SYNTHESE_PREUVE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_03_DCE_CLASSIFICATION_SYNTHESE_PREUVE_v0.1.md) — classification sourcée, readiness partielle et synthèse qui n’efface pas les pièces manquantes.
- [`03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_03_DCE_RECTIFICATION_IMPACT_PREUVE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_03_DCE_RECTIFICATION_IMPACT_PREUVE_v0.1.md) — nouvelle version rectificative, historique `SUPERSEDED` et revue ciblée des conclusions dépendantes.
- [`03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_03_DCE_IA_PANNE_INSTRUCTION_HOSTILE_PREUVE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_03_DCE_IA_PANNE_INSTRUCTION_HOSTILE_PREUVE_v0.1.md) — panne IA visible, instruction hostile isolée en revue humaine et voie manuelle conservée.

L’inventaire `GET /api/v1/dce-versions/{id}/documents` rend l’état de chaque document visible sans divulguer le stockage privé. La lecture Case affiche la readiness de classification et d’analyse ; toute classification autre que `CLASSIFIED` reste explicitement partielle.

EXP-03 est maintenant gelée dans [`03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_03_OWNER_EXPERIENCE_FREEZE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_03_OWNER_EXPERIENCE_FREEZE_v0.1.md). Le harnais Golden est validé, mais son manifeste de dépôt reste vide : aucune qualité de compréhension sur corpus réel n’est revendiquée. La prochaine tranche ouvre EXP-04 sur les points bloquants.

## EXP-04 en cours

Le cadrage et la première preuve de lecture « À résoudre » sont suivis dans [`03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_04_POINTS_BLOQUANTS_SOURCES_ACTIONS_AUDIT_CADRAGE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_04_POINTS_BLOQUANTS_SOURCES_ACTIONS_AUDIT_CADRAGE_v0.1.md). La route read-only `GET /api/v1/cases/{case_id}/resolution` rassemble les exigences DCE à confirmer ou revoir, les demandes d’information encore ouvertes et les bloqueurs de tâche ouverts. Chaque ligne garde son état natif, ses références de source, son responsable connu et son échéance éventuelle ; la couverture reste explicitement `PARTIAL`.

La projection réutilise les lecteurs DCE et membership existants, filtre les tâches d’un collaborateur par son affectation active et ne fournit aucune clôture générique ni score opaque. Pour le Patron, elle réutilise aussi les lecteurs existants de signaux de risque et de contradictions et les expose avec `REVIEW_REQUIRED`, leurs sources et une action de revue ; ils ne sont pas fusionnés avec les cycles natifs. Pour une Affaire d’origine `OPPORTUNITY`, elle rattache également les inconnus BOAMP par l’observation d’origine, avec une identité déterministe et l’état `UNKNOWN`. Le champ `impact`, comme le responsable et l’échéance, n’est rempli que lorsque la source le fournit ; le responsable du bloqueur vient du bloqueur et son échéance de la tâche liée ; les absences restent explicites. Le gel d’expérience est consigné dans [`03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_04_OWNER_EXPERIENCE_FREEZE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_04_OWNER_EXPERIENCE_FREEZE_v0.1.md).

## EXP-05 gelée avec couverture partielle

L’audit et la preuve de l’import prix sont suivis dans [`03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_05_REPONSE_PRIX_AUDIT_CADRAGE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_05_REPONSE_PRIX_AUDIT_CADRAGE_v0.1.md). Le flux Patron preview → batch normalisé → commit conserve le hash de source, les lignes et les révisions sans stocker le fichier brut ni exposer de montant dans le reçu. Le front affiche maintenant « À VÉRIFIER » lorsqu’une réponse réseau est inconnue et rejoue la même intention avec les mêmes identifiants. La lecture Case Patron expose aussi les besoins non couverts déjà enregistrés, avec leur source et `REVIEW_CAPABILITY_GAP`, sans modifier le périmètre Collaborateur. Elle expose désormais une couverture économique minimale : hypothèses sourcées, absence explicite de contrat de devis, dernier run de capacité et prévision de trésorerie, sans montant ni feu vert implicite ; la surface « Mes affaires / Revue » l’affiche au Patron et la masque au Collaborateur. Les calculs de marge/scénarios sont réutilisés tels quels avec données numériques validées ; la limite des coûts inconnus reste bloquante.

Les moyens internes sont relus via les capacités d’entreprise versionnées et leurs preuves validées. Aucun agrégat actif de partenaires/groupements n’existe encore, donc aucun engagement n’est déduit. Le package collaborateur expose maintenant les brouillons techniques versionnés (sections, sources et responsable) comme plan de réponse unique, sans contenu financier. Le Patron peut relire ces mêmes métadonnées via la route de revue avant d’autoriser une suite ; la réponse complète reste à construire. Les contrôles de confidentialité gardent marge, CV et pièces d’entreprise hors des surfaces Collaborateur ; l’export de remise reste conditionné par la décision et `external_submission: NOT_PERFORMED`.

L’audit des portes métier P2/P3/P4, des conflits et des versions est consigné dans [`03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_05_P2_P3_P4_AUDIT_CADRAGE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_05_P2_P3_P4_AUDIT_CADRAGE_v0.1.md). Les preuves existantes permettent une préparation contrôlée, mais aucune porte P2, P3 ou P4 séparée n’est déclarée complète : les informations manquantes restent `PARTIAL` et bloquantes. Le gel d’expérience correspondant est [`03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_05_OWNER_EXPERIENCE_FREEZE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_05_OWNER_EXPERIENCE_FREEZE_v0.1.md). La prochaine tranche ouvre EXP-06 sur la candidate, l’autorisation P5 et la remise humaine.

## EXP-06 gelée

La candidate et l’autorisation P5 sont décrites dans [`03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_06_CANDIDATE_P5_AUDIT_PREUVE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_06_CANDIDATE_P5_AUDIT_PREUVE_v0.1.md). Le package préparé reste immuable ; une autorisation Patron append-only porte sa version et le hash canonique de son manifeste. Le mode `CANDIDATURE_ONLY` exige une justification et omet le snapshot financier et le pricing. La route Patron-only de prévisualisation expose la version, le hash, les entrées, le mode, le périmètre et les exclusions sans clé de stockage ni montant. L’intention de signature et la preuve de réception manuelle reprennent aussi ce hash exact, sans automatiser le dépôt. `HUMAN_DEPOSIT_ATTEMPT` reste `UNKNOWN` et `PARTIAL`, tandis que le redépôt crée une nouvelle version qui exige une nouvelle P5. L’audit des frontières est consigné dans [`03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_06_VALIDATION_SIGNATURE_DEPOT_RECEPTION_AUDIT_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_06_VALIDATION_SIGNATURE_DEPOT_RECEPTION_AUDIT_v0.1.md), la lecture détaillée dans [`03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_06_RECEPTION_PARTIELLE_MANIFESTE_AUDIT_PREUVE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_06_RECEPTION_PARTIELLE_MANIFESTE_AUDIT_PREUVE_v0.1.md), et le gel final dans [`03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_06_OWNER_EXPERIENCE_FREEZE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_06_OWNER_EXPERIENCE_FREEZE_v0.1.md). Le rapprochement complet et le dépôt externe restent explicitement hors périmètre.

## EXP-07 en cours

EXP-07 est gelée dans [`03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_07_OWNER_EXPERIENCE_FREEZE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_07_OWNER_EXPERIENCE_FREEZE_v0.1.md). Résultat par lot, transmission, commande/P6/P7, REX, suspension, fermeture, demande d’export et conservation sont append-only et prouvés côté backend. Une demande d’export reste distincte d’une réception externe, qui demeure `NOT_PERFORMED`. La prochaine étape ouvre C14, sur la gouvernance des membres, rôles et délégations.

## C14 prouvée — C15 suivante

Le cadrage [`03_PRODUCT_DESIGN_WORKING/SMART_AO_C14_GOUVERNANCE_MEMBRES_DELEGATIONS_AUDIT_CADRAGE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_C14_GOUVERNANCE_MEMBRES_DELEGATIONS_AUDIT_CADRAGE_v0.1.md) distingue propriété organisationnelle, rôle métier, délégation, suspension et récupération exceptionnelle. La preuve sépare `tenant_owners` de `PATRON_ADMIN`, conserve les suspensions, désignations, transferts et relèves append-only, révoque les sessions suspendues et invalide les délégations futures. Le détail est dans [`03_PRODUCT_DESIGN_WORKING/SMART_AO_C14_DELEGATIONS_RELEVE_DERNIER_PROPRIETAIRE_AUDIT_CADRAGE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_C14_DELEGATIONS_RELEVE_DERNIER_PROPRIETAIRE_AUDIT_CADRAGE_v0.1.md), et le gel dans [`03_PRODUCT_DESIGN_WORKING/SMART_AO_C14_OWNER_EXPERIENCE_FREEZE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_C14_OWNER_EXPERIENCE_FREEZE_v0.1.md). C14 est prouvée ; la prochaine tranche ouvre C15 sur MFA, récupération et sessions sensibles.

## C15 prouvée — C16 suivante

L’audit [`03_PRODUCT_DESIGN_WORKING/SMART_AO_C15_ACCES_MFA_RECUPERATION_SESSIONS_AUDIT_PREUVE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_C15_ACCES_MFA_RECUPERATION_SESSIONS_AUDIT_PREUVE_v0.1.md) et le gel [`03_PRODUCT_DESIGN_WORKING/SMART_AO_C15_OWNER_EXPERIENCE_FREEZE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_C15_OWNER_EXPERIENCE_FREEZE_v0.1.md) confirment la garde MFA avant métier, la fraîcheur du step-up, la récupération avec révocation complète et le refus de l’email ou du code de secours seul. La désactivation volontaire d’un facteur exige désormais une session MFA récente et un TOTP courant. C15 est prouvée ; la prochaine tranche ouvre C16 sur les partages et révocations.

## C16 prouvée — N01 suivante

L’audit [`03_PRODUCT_DESIGN_WORKING/SMART_AO_C16_PARTAGES_DESTINATAIRES_REVOKATION_AUDIT_CADRAGE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_C16_PARTAGES_DESTINATAIRES_REVOKATION_AUDIT_CADRAGE_v0.1.md) et le gel [`03_PRODUCT_DESIGN_WORKING/SMART_AO_C16_OWNER_EXPERIENCE_FREEZE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_C16_OWNER_EXPERIENCE_FREEZE_v0.1.md) fixent et prouvent le registre de partage à version exacte, le destinataire, la finalité, l’expiration, la révocation append-only et la limite après téléchargement. Les routes HTTP publiques restent à exposer ; la prochaine tranche ouvre N01 sur les conflits de contributions.

## N01 prouvée — N02 suivante

L’audit [`03_PRODUCT_DESIGN_WORKING/SMART_AO_N01_CONFLITS_CONTRIBUTIONS_AUDIT_CADRAGE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_N01_CONFLITS_CONTRIBUTIONS_AUDIT_CADRAGE_v0.1.md) confirme les révisions optimistes déjà présentes, mais fixe le manque restant : conserver deux contributions concurrentes, leurs auteurs et une résolution humaine sans « dernier clic gagne ».

La migration `20260920_0090`, le service de registre et la garde de confirmation
classique réalisent ce contrat. La preuve PostgreSQL est dans
[`03_PRODUCT_DESIGN_WORKING/SMART_AO_N01_OWNER_EXPERIENCE_FREEZE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_N01_OWNER_EXPERIENCE_FREEZE_v0.1.md) : deux propositions sont conservées, le conflit ouvert bloque la validation, puis une résolution append-only et idempotente lève le blocage.

## N02 prouvée — N03 suivante

L’audit et le gel [`SMART_AO_N02_ISSUE_OPERATION_INCONNUE_AUDIT_CADRAGE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_N02_ISSUE_OPERATION_INCONNUE_AUDIT_CADRAGE_v0.1.md) et [`SMART_AO_N02_OWNER_EXPERIENCE_FREEZE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_N02_OWNER_EXPERIENCE_FREEZE_v0.1.md) couvrent l’export Patron interrompu après envoi : l’état `UNKNOWN` est stable, le dernier état confirmé reste affiché et l’action de vérification réutilise le paquet sans présumer d’un succès externe.

## N03 prouvée — N04 suivante

La route [`POST /api/v1/shared-resources/preview`](../backend/app/interfaces/http/routes/shared_resources.py) expose au destinataire la ressource exacte, son empreinte, sa finalité, sa classification et sa fenêtre de validité. Elle ne renvoie ni jeton ni identité et répond `404 SHARE_NOT_AVAILABLE` pour un partage inconnu, expiré ou révoqué. Le gel est dans [`SMART_AO_N03_OWNER_EXPERIENCE_FREEZE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_N03_OWNER_EXPERIENCE_FREEZE_v0.1.md). La prochaine tranche ouvre N04 sur la relève nominative.

## N04 prouvée — N05 suivante

La relève nominative est exposée par [`POST /api/v1/continuity/handovers`](../backend/app/interfaces/http/routes/continuity.py) puis par son acceptation [`POST /api/v1/continuity/handovers/{handover_id}/acceptance`](../backend/app/interfaces/http/routes/continuity.py). Le client web reprend ces deux commandes. Le demandeur, le successeur et le tenant sont résolus depuis le serveur ; la portée est déclarée, l'acceptation est réservée au successeur et le rejeu reste idempotent. Aucun rôle ou pouvoir métier n'est transféré implicitement. Le cadrage et les limites sont dans [`SMART_AO_N04_RELEVE_NOMINATIVE_AUDIT_PREUVE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_N04_RELEVE_NOMINATIVE_AUDIT_PREUVE_v0.1.md) et le gel dans [`SMART_AO_N04_OWNER_EXPERIENCE_FREEZE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_N04_OWNER_EXPERIENCE_FREEZE_v0.1.md). La prochaine tranche ouvre N05 sur la disponibilité terrain locale, en attente et confirmée.

## N05 prouvée — variantes responsive suivantes

Le [`CollaboratorWizardPanel`](../web/src/features/wizard/CollaboratorWizardPanel.tsx) distingue les pièces déjà chargées des captures terrain locales. Une capture affiche `LOCAL`, puis `PENDING` pendant la synchronisation et `CONFIRMED` seulement après le retour serveur. Hors ligne, la synchronisation est refusée sans succès présumé ; aucun secret ni fichier brut n'est écrit dans le stockage navigateur. Le cadrage est dans [`SMART_AO_N05_DISPONIBILITE_TERRAIN_AUDIT_PREUVE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_N05_DISPONIBILITE_TERRAIN_AUDIT_PREUVE_v0.1.md) et le gel dans [`SMART_AO_N05_OWNER_EXPERIENCE_FREEZE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_N05_OWNER_EXPERIENCE_FREEZE_v0.1.md). La prochaine tranche matérialise les variantes responsive utiles sans créer une application parallèle.

## Phase 8 responsive clôturée — Phase 9 suivante

L'audit [`SMART_AO_PHASE8_RESPONSIVE_AUDIT_PREUVE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_PHASE8_RESPONSIVE_AUDIT_PREUVE_v0.1.md) confirme que les mêmes surfaces replient coque, grilles, wizard, workflows et formulaires aux paliers desktop, tablette et mobile. Aucune application parallèle ni capacité supplémentaire n'est introduite. La recette visuelle et d'accessibilité reste volontairement en phase 9.

## Phase 9 ouverte — espaces C00–C16 matérialisés

Le registre [`canonicalSpaces.ts`](../web/src/app/canonicalSpaces.ts) conserve les 17 codes adoptés par le catalogue : C00 transversal et C01 à C16. Chaque espace porte son statut réel, sa destination éventuelle et les IDs de surfaces à vérifier. Les espaces partiels ou `BACKLOG` restent visibles comme tels ; aucune surface backend n'est transformée en écran fictif. L'audit est dans [`SMART_AO_PHASE9_C00_C16_MATERIALISATION_AUDIT_PREUVE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_PHASE9_C00_C16_MATERIALISATION_AUDIT_PREUVE_v0.1.md). La couverture structurelle des 104 surfaces est prouvée par égalité exacte des IDs ; la tranche active est maintenant la recette PUX-01 à PUX-19.

## Archives

`_ARCHIVE/` conserve les documents remplacés, leurs raisonnements et leurs preuves. Ils restent consultables, mais ne sont pas des références actives :

- `produit_metier/` : cahiers métier et versions antérieures du cahier propriétaire ;
- `ux_ccf/` : CCF UX et benchmark ;
- `architecture_ancienne/` : cadrages, plans et registres d'architecture remplacés ;
- `audits/` : documents de revue anciens ;
- `work_reviews/` : contre-audit Work v0.3 et son dossier de preuves.
- `explorations_visuelles/` : images, essais et prototypes non normatifs remplacés.

Cette organisation archive sans détruire. Un document actif doit renvoyer vers cette hiérarchie, et non réintroduire une source historique comme autorité produit.

### Phase 9 ouverte — couverture C00–C16 et surfaces catalogue

Le registre [`web/src/app/canonicalSpaces.ts`](../web/src/app/canonicalSpaces.ts)
matérialise les 17 espaces canoniques C00–C16 et rattache exactement les 104
surfaces non-PUX du catalogue. Les statuts restent honnêtes :
`MATERIALIZED`, `PARTIAL` ou `BACKLOG` ; l'inventaire ne vaut pas recette
comportementale. La preuve structurelle est décrite dans
[`SMART_AO_PHASE9_104_SURFACES_AUDIT_CADRAGE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_PHASE9_104_SURFACES_AUDIT_CADRAGE_v0.1.md).

L’audit [`SMART_AO_PHASE9_PUX_01_19_EXECUTION_AUDIT_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_PHASE9_PUX_01_19_EXECUTION_AUDIT_v0.1.md)
sépare les preuves verticales des parcours réellement complets. PUX-01 est
désormais prouvé sur sa première valeur progressive ; PUX-03/04 disposent de
la preuve dédiée [`SMART_AO_PHASE9_PUX03_PUX04_PREUVE_VERTICALE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_PHASE9_PUX03_PUX04_PREUVE_VERTICALE_v0.1.md).
L’audit ne déclare aucun dépôt externe, partenaire, interface ADM,
qualification Golden ou marge finale sans preuve correspondante.

La première passe automatisée G01–G52 et ses limites sont consignées dans
[`SMART_AO_PHASE9_G01_G52_EXECUTION_MATRIX_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_PHASE9_G01_G52_EXECUTION_MATRIX_v0.1.md).
Elle distingue les tests techniques passants des recettes métier qui restent à
clôturer. Après correction des régressions, la seconde passe backend est verte
avec 1 701 tests passants et 2 skips PIL ; les recettes métier restent à jouer
scénario par scénario.
La première exécution réelle G01–G09 est détaillée dans
[`SMART_AO_PHASE9_G01_G09_EXECUTION_PREUVE_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_PHASE9_G01_G09_EXECUTION_PREUVE_v0.1.md) :
105 tests passent contre PostgreSQL Docker, mais les statuts restent partiels
ou techniques tant que les décisions métier et preuves append-only dédiées ne
sont pas jouées.
Le registre machine fermé des 52 scénarios est `backend/app/platform/quality/data/g01_g52.json`.
Les fixtures métier exécutables G01–G09 et leur parseur sont
`backend/app/platform/quality/data/g01_g09_business.json` et
`backend/app/platform/quality/business_fixtures.py`; leur rejeu est couvert par
`backend/tests/application/test_g01_g09_business_fixtures.py`.
