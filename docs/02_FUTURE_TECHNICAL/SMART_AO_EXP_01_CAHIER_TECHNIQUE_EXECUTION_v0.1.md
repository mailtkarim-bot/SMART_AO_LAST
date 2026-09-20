# SMART AO — EXP-01 : cahier technique d’exécution consolidé

**Version :** 0.1  
**Statut :** TRANCHE 1 IMPLÉMENTÉE — création manuelle EXP-01 vérifiée ; origines référencées réservées aux tranches suivantes  
**Date :** 14 septembre 2026  
**Autorité fonctionnelle :** [OWNER EXPERIENCE FREEZE EXP-01](../03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_01_OWNER_EXPERIENCE_FREEZE_v0.1.md)  
**Maquette liée :** [maquette détaillée EXP-01](../03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_01_MAQUETTE_DETAILLEE_OWNER_FREEZE_v0.1.md)

## 1. Objet et décision d’architecture

Ce document transforme le gel d’expérience EXP-01 en contrat implémentable pour le dépôt actuel. Il décrit uniquement les frontières nécessaires au premier accès, à la première Affaire et à la reprise sûre. Il n’introduit ni framework, ni stockage navigateur, ni abstraction parallèle.

L’implémentation de référence est :

- **front :** React/Vite sous `web/` ; état de session et projections en mémoire ; `createApiClient` comme point d’accès HTTP ;
- **API :** FastAPI sous `backend/app/interfaces/http/routes/` ; modèles Pydantic fermés (`extra="forbid"`) ;
- **domaine :** commandes et agrégats sous `backend/app/modules/` ; dispatcher et reçus idempotents sous `backend/app/platform/events/` ;
- **persistance :** PostgreSQL/SQLAlchemy et migrations Alembic ; tenant, identité, membership, sessions, facteurs MFA, Affaires et événements ;
- **transport :** access token Bearer court en mémoire, refresh token rotatif en cookie `HttpOnly`, CSRF double-submit.

La source de vérité reste le code et les tests exécutés. Une divergence avec ce document ouvre une correction ou une décision datée ; elle n’est pas résolue par une valeur par défaut côté navigateur.

## 2. Périmètre contractuel

### Inclus

- connexion par email, mot de passe et tenant sélectionné avant session ;
- session `PASSWORD` limitée jusqu’à MFA ;
- enrôlement TOTP, confirmation, step-up, désactivation et récupération assistée ;
- résolution serveur de l’entreprise, du rôle et du profil opérationnel ;
- confirmation locale du contexte ;
- création manuelle d’une Affaire et rejeu idempotent ;
- Accueil composé par projections autorisées ;
- expiration, rotation refusée, masquage et reprise du dernier état confirmé ;
- invitations nominatives déjà prouvées côté API, sans divulgation d’identité.

### Exclus de cette version

PAGE-004 et PAGE-005 tant qu’une obligation n’est pas démontrée, brouillons persistants, reprise multi-appareil, avertissement pré-expiration, nouvelle politique de durée, synchronisation hors ligne, refonte du tenant ID et extension des parcours EXP-02 à EXP-07.

## 3. Contrats de session et d’accès

### 3.1 États de session

```text
NO_SESSION
  -- POST /auth/login --> PASSWORD
PASSWORD
  -- /auth/me mfa_verified=false --> MFA_PENDING
  -- /auth/me mfa_verified=true  --> CONTEXT_PENDING
MFA_PENDING
  -- /mfa/totp/confirm ou /mfa/step-up --> CONTEXT_PENDING
CONTEXT_PENDING
  -- confirmation locale --> READY
READY
  -- requête 401 + refresh refusé --> EXPIRED
EXPIRED
  -- login + MFA + même contexte + GET /cases/assigned --> READY
```

`useAuthentication.isAuthenticated` vaut vrai uniquement lorsque l’access token et `CurrentActor.mfa_verified` sont présents. `hasSession` peut être vrai pendant l’étape PASSWORD ; aucune route métier ne doit alors être appelée.

### 3.2 Durées et cookies observés

| Élément | Contrat actuel |
|---|---|
| access token | réponse JSON `expires_in=900` ; valeur conservée en mémoire |
| inactivité | 8 heures, prolongées par le résolveur actif |
| durée absolue | 24 heures standard, 12 heures privilégiées selon le rôle |
| refresh cookie | `smart_ao_refresh`, `Secure`, `HttpOnly`, `SameSite=Lax`, chemin `/api/v1/auth` |
| CSRF cookie | `smart_ao_csrf`, `Secure`, lisible par le front, `SameSite=Strict`, chemin `/` |
| rotation | un refresh accepté remplace le cookie et l’access token ; un rejeu compromet la lignée |

Le front tente au plus une rotation sur un `401` rejouable. Si elle échoue, il vide le jeton et l’acteur et déclenche `sessionExpired`.

## 4. Matrice page → composant → API

| Page | Composant actuel | Appel principal | Résultat exploité |
|---|---|---|---|
| PAGE-001 | `App` / formulaire `connection-page` | `GET /healthz/ready`, `POST /api/v1/auth/login` | `AuthSession` ; cookies posés par l’API |
| PAGE-002 | `MfaPanel` | `POST /api/v1/auth/mfa/totp/enroll`, `/confirm`, `/step-up`, `/disable` | facteur, TOTP, codes de récupération, access token MFA |
| PAGE-002 récupération | parcours sécurisé API | `POST /api/v1/auth/mfa/recovery/start` | réponse 204, cookies invalidés ; nouvel enrôlement requis |
| PAGE-003 | `App` / confirmation de contexte | `GET /api/v1/auth/me` | `CurrentActor` résolu serveur |
| PAGE-004 | conditionnel | aucun endpoint EXP-01 | ne pas rendre sans obligation prouvée |
| PAGE-005 | conditionnel | aucun endpoint EXP-01 | ne pas rendre sans préférence nécessaire prouvée |
| PAGE-006 | `CreateCasePanel` | `POST /api/v1/cases` puis `GET /api/v1/cases/assigned` | reçu `CASE_CREATED`, affaire sélectionnée après refresh |
| PAGE-007 | `App` + panneaux métier existants | `GET /api/v1/cases/assigned` ; pour Patron, actions, affectations, entreprise, BOAMP et décisions selon capacité | projections filtrées par tenant, rôle et affectation |

Les routes de lecture DCE, pricing, décisions et préparation restent des capacités de l’Accueil déjà présentes ; elles ne modifient pas le contrat de création de la première Affaire.

## 5. Contrats HTTP

### 5.1 Authentification

#### `POST /api/v1/auth/login`

Requête fermée :

```json
{
  "email": "operateur@example.test",
  "password": "secret",
  "tenant_id": "uuid"
}
```

Réponse `200` :

```json
{ "access_token": "…", "token_type": "Bearer", "expires_in": 900 }
```

`401 INVALID_CREDENTIALS`, `429 RATE_LIMITED`. Les erreurs restent neutres. Le serveur ne renvoie jamais le refresh token dans le JSON.

#### `POST /api/v1/auth/refresh`

Requiert cookie refresh et en-tête `X-CSRF-Token` correspondant au cookie CSRF. Réponse `200` identique à login ; `401 REFRESH_REJECTED` ou `403 CSRF_REJECTED` ferment la reprise.

#### `GET /api/v1/auth/me`

Requiert Bearer. Réponse fermée :

```json
{
  "actor_id": "uuid",
  "identity_id": "uuid",
  "tenant_slug": "entreprise",
  "actor_kind": "PATRON_ADMIN | PATRON_DELEGATE | COLLABORATEUR",
  "operational_profile": "RESPONSABLE | EXPERT | null",
  "membership_state": "ACTIVE | SUSPENDED | REVOKED",
  "mfa_verified": true
}
```

Le front ne fabrique aucun champ de cette projection et ne peut pas poster un rôle choisi.

### 5.2 MFA et récupération

Toutes les commandes MFA authentifiées requièrent Bearer, session active et CSRF. Les codes sont envoyés dans le corps fermé `{ "code": "…" }`, avec `factor_id` pour la confirmation d’enrôlement.

| Route | Succès | Refus à préserver |
|---|---:|---|
| `POST /mfa/totp/enroll` | `200` avec `factor_id`, `otpauth_uri`, `recovery_codes`, `expires_at` | `401`, `403`, `409`, `429` |
| `POST /mfa/totp/confirm` | `200` access token MFA | `422` code invalide, `403` CSRF |
| `POST /mfa/totp/step-up` | `200` access token step-up + `used_recovery_code` | code de secours non accepté par ce chemin |
| `POST /mfa/recovery/start` | `204`, cookies d’authentification supprimés | email seul absent du contrat ; code invalide `422` |
| `POST /mfa/totp/disable` | `204` après code TOTP | `422` code invalide |

Après récupération, toutes les sessions et le facteur compromis sont révoqués ; l’utilisateur doit repasser par mot de passe puis enrôler un nouveau facteur avant l’accès métier.

### 5.3 Création d’Affaire

#### Requête `POST /api/v1/cases`

Le front normalise les champs puis conserve les trois UUID dans `pendingCommand` tant qu’un succès n’est pas confirmé. Pour la tranche EXP-01, le panneau expose uniquement `MANUAL`, car les origines `OPPORTUNITY`, `IMPORT` et `CLIENT_REQUEST` exigent une `origin_reference_id` que seule une sélection de source métier pourra fournir. L’API garde ces variantes pour les tranches suivantes.

Le corps de la commande est :

```json
{
  "command_id": "uuid",
  "idempotency_key": "uuid",
  "correlation_id": "uuid",
  "title": "Réhabilitation énergétique du groupe scolaire",
  "object_description": "Périmètre connu et limites actuelles",
  "scope_kind": "SINGLE_LOT | MULTI_LOT | TRANCHE | VARIANT | CUSTOM",
  "lot_numbers": ["01", "02A"],
  "tranche_reference": "optionnel",
  "variant_reference": "optionnel",
  "scope_justification": "hypothèses ou exclusions",
  "origin_kind": "MANUAL"
}
```

Le serveur interdit les champs supplémentaires et valide les longueurs. Les règles de domaine actuelles imposent notamment : origine manuelle sans référence, référence pour une origine non manuelle et cohérence consultation/révision lorsqu’une consultation est fournie.

#### Réponse

Création initiale : `201`.

Rejeu avec la même clé : `200` et `replayed=true`.

```json
{
  "status": "SUCCEEDED",
  "command_id": "uuid",
  "idempotency_key": "uuid",
  "result_code": "CASE_CREATED",
  "case_id": "uuid",
  "version": 0,
  "event_ids": ["uuid"],
  "navigation": "CASE_OVERVIEW",
  "replayed": false
}
```

Le `case_id` est déterminé côté serveur à partir de la clé d’idempotence et du tenant ; il n’est jamais saisi par l’utilisateur. `409 IDEMPOTENCY_CONFLICT` couvre une réutilisation incompatible ou une commande en cours. Les erreurs de domaine sont `409` pour identité fonctionnelle/version et `422` pour validation métier.

#### Sémantique de réponse inconnue

Une absence de réponse HTTP, timeout ou interruption après émission de la requête est `CREATE_UNKNOWN` côté UI :

1. conserver la saisie et les UUID ;
2. afficher « Création à vérifier » ;
3. au clic « Vérifier et réessayer », rejouer exactement le même corps ;
4. n’afficher le succès et ne naviguer qu’après une réponse `200/201` valide.

Une saisie modifiée produit une nouvelle intention et de nouveaux UUID. Aucun `GET` approximatif ne doit être interprété comme preuve de succès.

### 5.4 Collection d’Affaires et Accueil

`GET /api/v1/cases/assigned` renvoie une liste fermée de :

```json
{
  "case_id": "uuid",
  "work_label": "Affaire visible",
  "case_lifecycle": "ACTIVE",
  "commercial_stage": "…",
  "dce_availability": "AVAILABLE | …"
}
```

Le serveur part d’un candidat tenant-scopé puis applique la politique d’autorisation pour `CASE_DCE_READ`. Le front ne filtre pas un résultat interdit pour le rendre visible ; il ne rend que la liste reçue.

## 6. Invariants de sécurité et de cohérence

1. Toute route métier passe par `resolve_bearer_context`; une session sans `mfa_verified_at` obtient `403 STEP_UP_REQUIRED`.
2. Les routes d’authentification utilisent leur résolveur dédié pour permettre l’enrôlement et la récupération avant MFA.
3. Tenant, identité, membership, rôle, profil, capacités et affectations sont résolus côté serveur.
4. `PATRON_ADMIN` est la seule autorité Patron ; `RESPONSABLE` et `EXPERT` sont des profils de `COLLABORATEUR`.
5. Aucune valeur fournie par le navigateur ne peut élever un rôle, une capacité, un tenant ou une affectation.
6. Les projections locales (`cases`, actions, scénarios, dossier de décision, affaire sélectionnée) sont vidées dès `sessionExpired`.
7. Le snapshot de reprise ne contient que `identityId`, `tenantSlug`, `actorKind`, `caseId` et navigation ; il reste en mémoire.
8. La reprise exige même identité, tenant et rôle, puis MFA, confirmation du contexte et refresh serveur réussi.
9. Les secrets TOTP, mots de passe et refresh tokens ne sont jamais écrits dans les journaux ou dans le stockage navigateur.
10. Une erreur ou un résultat inconnu ne constitue jamais une commande métier confirmée.

## 7. Observabilité minimale

Chaque commande métier transporte `command_id`, `idempotency_key` et `correlation_id`. Le serveur journalise l’événement d’audit avec tenant, identité, session, résultat et code de raison ; aucun secret ni contenu de mot de passe/TOTP n’est journalisé.

Le front peut afficher un UUID de corrélation uniquement dans un détail de support. Les messages utilisateurs restent neutres et orientés action. Les métriques minimales sont : login accepté/refusé, refresh accepté/refusé, MFA accepté/refusé, création initiale/rejouée/conflit, expiration et reprise confirmée.

## 8. Tests et preuve de sortie

### Tests obligatoires pour la tranche d’exécution

- front : absence de session, MFA manquante, confirmation de contexte, création nominale, réponse inconnue et rejeu, expiration, reprise même acteur, invalidation d’un autre rôle ;
- backend ciblé : gardes Bearer/MFA, `/auth/me`, création `201/200`, conflit d’idempotence, isolation tenant et capacités Patron/collaborateur ;
- PostgreSQL : migration à jour, consommation unique des invitations, récupération/révocation et idempotence de création ;
- qualité : build TypeScript/Vite, ESLint, `git diff --check`.

### Critères de sortie

La tranche est terminée lorsque :

1. les contrats ci-dessus sont couverts par des tests exécutables ;
2. un premier login autorisé atteint PAGE-007 après MFA et contexte ;
3. une Affaire réelle est créée, relue et rejouée sans doublon ;
4. les états inconnus et expirés ne montrent aucune donnée périmée ;
5. les refus MFA, tenant, rôle et idempotence sont observés ;
6. le plan global et Basic Memory pointent vers les commandes et résultats réellement exécutés.

## 9. Limites et décisions différées

Le contrat ne fixe pas la suppression du tenant ID, les durées alternatives proposées dans les travaux UX, l’avertissement avant expiration, la persistance d’un brouillon, le multi-device, une application mobile ou l’automatisation du dépôt. Ces sujets demandent une décision séparée et ne doivent pas être introduits pendant l’implémentation EXP-01.

## 10. Références de code et de pilotage

- `web/src/app/App.tsx`
- `web/src/features/auth/useAuthentication.ts`
- `web/src/features/auth/MfaPanel.tsx`
- `web/src/features/cases/CreateCasePanel.tsx`
- `web/src/infrastructure/api.ts`
- `web/src/shared/types.ts`
- `backend/app/interfaces/http/dependencies/auth.py`
- `backend/app/interfaces/http/routes/authentication.py`
- `backend/app/interfaces/http/routes/case_creation.py`
- `backend/app/interfaces/http/routes/case_assigned.py`
- `backend/app/modules/case/public/contracts.py`
- `backend/app/modules/case/application/handlers.py`
- [Plan global](../03_PRODUCT_DESIGN_WORKING/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md)
- [Maquette détaillée](../03_PRODUCT_DESIGN_WORKING/SMART_AO_EXP_01_MAQUETTE_DETAILLEE_OWNER_FREEZE_v0.1.md)
