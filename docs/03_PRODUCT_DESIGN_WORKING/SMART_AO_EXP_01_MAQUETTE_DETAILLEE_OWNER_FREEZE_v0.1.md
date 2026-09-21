# SMART AO — EXP-01 : maquette détaillée

**Version :** 0.1  
**Statut :** MAQUETTE DÉTAILLÉE — alignée sur l’OWNER EXPERIENCE FREEZE, validation visuelle terrain à venir  
**Date :** 14 septembre 2026  
**Périmètre :** PAGE-001 → PAGE-007, avec les états d’authentification, de reprise et de création d’Affaire prouvés

## 1. Autorité et objectif

Cette maquette traduit le gel d’expérience EXP-01 en surfaces, états et critères vérifiables. Elle ne remplace ni le cahier Produit/Métier OWNER v0.4, ni le catalogue Écrans/Parcours OWNER v0.3. En cas de contradiction, ces deux autorités et le [gel d’expérience EXP-01](SMART_AO_EXP_01_OWNER_EXPERIENCE_FREEZE_v0.1.md) prévalent.

Le but est de permettre à une personne autorisée de :

1. ouvrir une session tenant-scopée ;
2. valider la MFA avant toute lecture métier ;
3. confirmer l’entreprise et le rôle résolus par le serveur ;
4. créer une première Affaire avec le périmètre connu ;
5. reprendre un état confirmé après expiration sans fausse confirmation.

Les écrans PAGE-004 et PAGE-005 restent conditionnels. Aucun champ n’est ajouté pour remplir artificiellement un onboarding.

## 2. Règles de composition

### 2.1 Ton et information

- Une action primaire par surface ; le libellé décrit son résultat.
- Les états inconnus, expirés, partiels et refusés sont écrits en clair.
- Aucune identité, organisation, rôle ou donnée métier n’est déduite d’un échec d’authentification.
- Les références techniques (UUID, corrélation) restent dans les détails de support et les journaux, jamais comme preuve de succès à l’écran.
- Les notifications décrivent ce qui est confirmé par le serveur, pas ce que l’interface espérait obtenir.

### 2.2 Grille visuelle existante

La maquette réemploie les tokens déjà présents dans `web/src/app/styles.css` :

| Élément | Règle existante à conserver |
|---|---|
| Shell | barre latérale sombre, contenu fluide, largeur maximale 1300 px |
| Surface | cartes blanches bordées, rayon 12–15 px, ombres légères |
| Action primaire | bouton violet `#7187fb`, texte blanc, libellé explicite |
| Action secondaire | bouton neutre, réservé à l’annulation, la fermeture ou une reprise non destructive |
| État positif | vert, toujours accompagné d’un texte |
| Alerte | ambre/rouge, jamais le seul signal de l’état |
| Typographie | titres courts, textes d’aide de 10–13 px, contraste lisible |
| Responsive | 2 colonnes à tablette, 1 colonne à mobile ; navigation horizontale sous 780 px |

Ces valeurs sont des contraintes de continuité visuelle, pas une nouvelle dépendance de design.

### 2.3 Structure de surface

```text
surface
├── en-tête : contexte + titre + état global
├── message : succès, avertissement ou erreur actionnable
├── contenu : une tâche principale et ses informations nécessaires
└── pied : action primaire, action secondaire, aide limitée
```

Chaque formulaire possède un titre associé, un label visible, un état de soumission et un retour `role="status"` ou `role="alert"` selon la gravité.

## 3. États transverses

```text
NO_SESSION
  └─ login confirmé → PASSWORD
PASSWORD
  ├─ mfa_verified=false → MFA_PENDING
  └─ mfa_verified=true  → CONTEXT_PENDING
MFA_PENDING
  └─ TOTP confirmé → CONTEXT_PENDING
CONTEXT_PENDING
  └─ contexte confirmé → READY
READY
  ├─ 401 + refresh refusé → EXPIRED
  └─ action de création sans réponse → CREATE_UNKNOWN
EXPIRED
  └─ reconnexion + MFA + même contexte + rechargement → READY
CREATE_UNKNOWN
  ├─ rejeu avec mêmes identifiants → READY si réponse confirmée
  └─ nouvelle saisie différente → nouvelle intention, après décision explicite
```

Le navigateur ne choisit jamais `actor_kind`, `operational_profile`, tenant ou capacités. Il affiche la projection résolue par le serveur.

## 4. Maquettes par page

### PAGE-001 — connexion tenant-scopée

**But :** établir une session `PASSWORD` sans exposer l’existence d’un compte ni de privilèges.

```text
┌──────────────────────────────────────────────────────────────┐
│ ACCÈS SMART AO                                               │
│ Connectez-vous                                               │
│ Les données métier restent masquées jusqu’à une session sûre.│
│                                                              │
│ URL API             [____________________________________]   │
│ État du backend     Backend prêt · PostgreSQL : ok           │
│ Email professionnel [____________________________________]   │
│ Tenant ID           [____________________________________]   │
│ Mot de passe        [____________________________________]   │
│                                                              │
│                         [ Se connecter → ]                   │
└──────────────────────────────────────────────────────────────┘
```

| Élément | Contrat de maquette |
|---|---|
| Données visibles | URL API, état de readiness, email, tenant ID, mot de passe |
| Action primaire | `Se connecter` ; contrôle readiness puis `POST /api/v1/auth/login` |
| États | restauration, backend prêt, non prêt, inaccessible, identifiants invalides, session expirée |
| Refus | message neutre ; aucune indication « email connu », rôle ou tenant valide |
| Limite connue | le champ tenant ID est encore nécessaire au contrat actuel ; sa suppression est une décision technique ultérieure, pas une modification silencieuse de cette maquette |
| Critères | aucune projection métier rendue ; mot de passe effacé après réussite ; cookie de refresh non lisible par le JavaScript |

### PAGE-002 — activation ou challenge MFA

**But :** établir `mfa_verified=true` avant d’autoriser une lecture ou une commande métier.

```text
┌──────────────────────────────────────────────────────────────┐
│ ACCÈS SÉCURISÉ                                               │
│ Validez votre second facteur                                 │
│ Aucune donnée métier n’est accessible avant cette validation.│
│                                                              │
│ ACTIVER TOTP                                                 │
│ Associer une application d’authentification                  │
│ URI de provisioning : [masquée/copier]                       │
│ Codes de récupération : à conserver hors de l’application    │
│ Code affiché par l’application [______]                       │
│                 [ Confirmer l’activation ]                   │
│                                                              │
│ ACTION SENSIBLE                                              │
│ Code TOTP de step-up [______]                                 │
│                 [ Valider le step-up ]                       │
│                                                              │
│                 [ Se déconnecter ]                            │
└──────────────────────────────────────────────────────────────┘
```

| Élément | Contrat de maquette |
|---|---|
| Activation | URI de provisioning et codes de récupération affichés une fois ; confirmation par code et `factor_id` |
| Session déjà enrôlée | challenge TOTP ; aucun accès à PAGE-003 avant succès |
| Step-up | réservé aux actions sensibles ; fenêtre signalée comme temporaire |
| Récupération | parcours assisté séparé ; l’email seul ne constitue jamais une preuve |
| Erreurs | code invalide, expiration, rate limit ; conserver le contexte de saisie utile sans révéler le secret |
| Critères | le serveur garde `mfa_verified_at`; le front rappelle `/auth/me` avant d’ouvrir l’espace métier |

### PAGE-003 — confirmation du contexte

**But :** faire confirmer à l’utilisateur l’entreprise et le rôle effectifs avant la première projection métier.

```text
┌──────────────────────────────────────────────────────────────┐
│ VOTRE ESPACE SMART AO                                        │
│ Confirmez votre contexte                                     │
│ Vérifiez l’entreprise et le rôle résolus par le serveur.     │
│                                                              │
│ ENTREPRISE ACTIVE                                            │
│ [ tenant_slug ]                         MFA validée          │
│                                                              │
│ VOTRE RÔLE EFFECTIF                                          │
│ [ Patron administrateur / Responsable / Expert ]             │
│ Vos droits dépendent du rôle et du périmètre autorisé.       │
│                                                              │
│ [ Confirmer et continuer ]       [ Se déconnecter ]           │
└──────────────────────────────────────────────────────────────┘
```

| Élément | Contrat de maquette |
|---|---|
| Source | projection `CurrentActor` issue de `/api/v1/auth/me` |
| Action primaire | confirmer localement le contexte affiché ; aucun rôle envoyé au serveur |
| Reprise | si l’état a expiré, afficher « dernier état confirmé » puis recharger avant de lever le bandeau |
| Refus | un contexte différent invalide le snapshot et ouvre un espace vide à recharger |
| Critères | aucune affaire, action ou compteur avant confirmation ; `PATRON_ADMIN` reste le seul rôle Patron |

### PAGE-004 — configuration minimale conditionnelle

**État :** non rendue dans EXP-01 tant qu’une donnée obligatoire n’est pas démontrée par le code ou le métier.

```text
┌──────────────────────────────────────────────────────────────┐
│ PRÉPARER VOTRE DÉMARRAGE                                     │
│ Une information réellement obligatoire manque.               │
│ [ champ démontré comme obligatoire ]                          │
│ Pourquoi cette information est nécessaire : [ explication ]  │
│ [ Enregistrer et continuer ]   [ Reprendre plus tard ]        │
└──────────────────────────────────────────────────────────────┘
```

Règles : pas de formulaire vide, pas de brouillon local, pas de blocage si le premier résultat utile peut être obtenu sans cette donnée. Toute activation de cette page crée une nouvelle décision datée.

### PAGE-005 — profil personnel conditionnel

**État :** non rendue dans EXP-01 tant qu’une préférence nécessaire n’est pas démontrée.

```text
┌──────────────────────────────────────────────────────────────┐
│ VOTRE PROFIL                                                  │
│ Une préférence utile est nécessaire à cette étape.            │
│ Nom affiché [________________]  Fonction [________________]   │
│ Préférence [_________________]                                │
│ La sécurité et les droits se gèrent dans un parcours séparé.  │
│ [ Enregistrer ]                    [ Continuer ]              │
└──────────────────────────────────────────────────────────────┘
```

Un profil ne modifie jamais un rôle, une capacité ou un périmètre. Les valeurs facultatives restent absentes plutôt que fabriquées.

### PAGE-006 — création de la première Affaire

**But :** enregistrer une Affaire minimale et traçable, sans prétendre connaître le DCE ou le chiffrage.

```text
┌──────────────────────────────────────────────────────────────┐
│ NOUVELLE AFFAIRE                         Commande idempotente │
│ Le périmètre est enregistré avant toute lecture DCE.          │
│                                                              │
│ Titre de l’affaire       [_______________________________]   │
│ Objet et description     [_______________________________]   │
│                          [_______________________________]   │
│ Type de périmètre        [ Lot unique ▾ ]                     │
│ Numéros de lots          [ 01, 02A, 04 ]                      │
│ Référence tranche        [ optionnel ]                        │
│ Référence variante       [ optionnel ]                        │
│ Origine                  [ Création manuelle ▾ ]              │
│ Justification            [ hypothèses / exclusions ]          │
│                                                              │
│                         [ Créer l’affaire → ]                │
│                                                              │
│ État ambigu : Création à vérifier. Vérifier et réessayer      │
│ rejoue la même intention avec les mêmes identifiants.         │
└──────────────────────────────────────────────────────────────┘
```

| Élément | Contrat de maquette |
|---|---|
| Champs requis | titre, objet/description, type de périmètre |
| Champs optionnels | lots, tranche, variante, justification ; origine par défaut `MANUAL` |
| Action | `POST /api/v1/cases` avec `command_id`, `idempotency_key`, `correlation_id` |
| En cours | bouton désactivé, libellé « Vérification en cours… » |
| Succès | message serveur `Affaire créée`, sélection de l’affaire, navigation Revue après refresh confirmé |
| Réponse inconnue | conserver le formulaire et les identifiants ; afficher « Création à vérifier » ; aucun succès ni doublon présumé |
| Conflit/validation | message d’erreur, saisie conservée ; un changement de contenu ouvre une nouvelle intention |
| Critères | une même intention rejouée produit au plus une Affaire ; aucune lecture DCE ou décision dans cette page |

### PAGE-007 — Accueil composé

**But :** montrer uniquement les projections autorisées et l’action la plus utile dans le contexte confirmé.

```text
┌──────────────────────────────────────────────────────────────┐
│ SMART_AO V8 · tenant · rôle              Données confidentielles│
│ [Vue d’ensemble] [Nouvelle affaire] [Préparation] [Revue]    │
│ [DCE/RAG] [Wizard] [Bibliothèque] [Décision] [Dépôt]          │
│                                                              │
│ Bonjour. Voici votre point de reprise.  [ n affaires ]        │
│ ┌──────────────────┬──────────────────┬────────────────────┐ │
│ │ À FAIRE          │ À SURVEILLER     │ ÉVÉNEMENTS RÉCENTS │ │
│ │ action autorisée │ partiel à revoir │ journal autorisé   │ │
│ │ [ Ouvrir → ]     │ source/version   │ statut inchangé    │ │
│ └──────────────────┴──────────────────┴────────────────────┘ │
│                                                              │
│ Mes affaires : cartes filtrées par le serveur                │
│ [ Actualiser ]                                               │
└──────────────────────────────────────────────────────────────┘
```

| Élément | Contrat de maquette |
|---|---|
| Vue principale | prochaine action, surveillance, événements récents |
| Source minimale | `GET /api/v1/cases/assigned` puis projections autorisées selon le rôle |
| Patron | navigation d’administration et création visibles seulement pour `PATRON_ADMIN`/`PATRON_DELEGATE` selon les capacités réellement résolues |
| Collaborateur | uniquement les surfaces et affaires de ses affectations actives ; Responsable/Expert ne gagnent aucun droit par le libellé |
| État vide | explication concrète et action adaptée, sans urgence inventée |
| Expiration | vider les projections, masquer l’Accueil et revenir à PAGE-001 ; ne pas laisser une ancienne carte visible |
| Critères | aucun compteur, secret financier, décision ou action hors périmètre n’est rendu |

## 5. Responsive, clavier et lecteur d’écran

- À 1100 px, les grilles passent de trois à deux colonnes ; à 780 px, le shell devient une navigation horizontale ; à 480–640 px, les cartes passent en une colonne.
- Le focus clavier suit l’ordre visuel : titre, champs, message d’état, action primaire, action secondaire.
- Les boutons ont un nom accessible indépendant de l’icône `→` ou `↻`.
- Toute erreur est reliée au champ ou au formulaire par un texte visible ; la couleur seule ne porte jamais l’état.
- Les données confidentielles restent masquées lorsque le shell n’est pas `READY`, y compris sur mobile.

## 6. Scénarios d’acceptation EXP-01

| ID | Parcours | Preuve attendue |
|---|---|---|
| UX-01 | mot de passe sans MFA | PAGE-002 uniquement ; aucun appel métier |
| UX-02 | MFA confirmée | PAGE-003 affiche tenant et rôle serveur |
| UX-03 | même contexte confirmé | PAGE-007 charge les affaires autorisées |
| UX-04 | Responsable/Expert | aucune action Patron et aucune élévation locale |
| UX-05 | création nominale | une Affaire, réponse `CASE_CREATED`, refresh visible |
| UX-06 | réponse inconnue | formulaire conservé, identifiants inchangés, pas de succès présumé |
| UX-07 | expiration | projections vidées, reconnexion puis MFA/contexte exigés |
| UX-08 | autre rôle après expiration | snapshot invalidé, aucune Affaire précédente restaurée automatiquement |
| UX-09 | MFA récupération | email seul refusé, code de secours et nouvel enrôlement requis selon le parcours sécurisé |

## 7. Hors périmètre et critères de promotion

Restent hors de cette maquette : persistance de brouillons, reprise multi-appareil, avertissement pré-expiration, nouvelles pages d’administration, refonte du champ tenant ID, pilote utilisateur et validation complète WCAG.

La maquette est promouvable vers une implémentation de tranche lorsque les critères UX-01 à UX-08 sont rejouables avec le contrat technique consolidé, les états d’erreur visibles et un test de non-divulgation. Toute nouvelle surface ou dépendance doit être ajoutée par décision explicite.

## 8. Références

- [OWNER EXPERIENCE FREEZE EXP-01](SMART_AO_EXP_01_OWNER_EXPERIENCE_FREEZE_v0.1.md)
- [Prototype basse fidélité EXP-01](SMART_AO_EXP_01_Prototype_Basse_Fidelite_WORK_PROPOSAL_v0.1.md)
- [Parcours et contrats de pages](../_ARCHIVE/work_reviews/SMART_AO_Experience_Utilisateur_Parcours_Pages_WORK_PROPOSAL_v0.1.md)
- [Évaluation technique EXP-01](SMART_AO_EXP_01_Evaluation_Technique_WORK_PROPOSAL_v0.1.md)
- [Cahier Produit/Métier OWNER v0.4](../00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md)
- [Catalogue Écrans/Parcours OWNER v0.3](../00_REFERENCE_ACTIVE/SMART_AO_Catalogue_Ecrans_Parcours_Produit_OWNER_CONSOLIDATED_v0.3.md)
- `web/src/app/App.tsx`
- `web/src/features/auth/MfaPanel.tsx`
- `web/src/features/cases/CreateCasePanel.tsx`
- `web/src/app/styles.css`
