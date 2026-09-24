# SMART AO — Cahier technique d’exécution v1.0

**Statut :** CANDIDAT D’EXÉCUTION ALIGNÉ SUR LE PRODUCT FREEZE v1.0  
**Date :** 20 septembre 2026  
**Autorités :** Product Freeze v1.0, UX Freeze global, architecture v3.1, code et tests exécutés

## 1. Décision de construction

SMART AO reste un modular monolith tenant-aware :

- **frontend :** React 19 + TypeScript + Vite sous `web/` ;
- **backend :** Python + FastAPI sous `backend/app/` ;
- **persistence :** PostgreSQL + SQLAlchemy + Alembic ;
- **jobs :** workers Python existants pour ingestion, export et projections ;
- **documents :** stockage privé référencé par hash et clé interne ;
- **IA/RAG :** retrieval local borné par tenant, Case, DCE et classification ;
- **déploiement :** Docker Compose aujourd’hui, VPS durci ensuite.

Rust, microservices et séparation frontend/backend par réseau interne restent des options futures. Le Product Freeze n’autorise pas un rewrite qui retarderait les preuves métier.

## 2. Modules et responsabilités

| Module | Responsabilité | Source de vérité |
|---|---|---|
| `identity` / `membership` | identité, tenant, membership, propriété, délégation, MFA et sessions | PostgreSQL + événements append-only |
| `case` | Affaire, origine, périmètre, rattachement DCE et projections « À résoudre » | Case records + sources référencées |
| `opportunity` | ingestion BOAMP, observation publique, qualification P0/P1 et inconnues | observation/qualification append-only |
| `dce` | staging, admission, extraction, classification, analyse, exigences et conflits | versions, fragments, exigences et résolutions |
| `decision` | contexte, risques, contradictions, conditions et GO/NO-GO | agrégat Decision + références immuables |
| `pricing` | imports, coûts, scénarios, hypothèses et marges Patron-only | snapshots/scénarios versionnés |
| `preparation` | readiness, documents techniques, brouillons, revue et transmission | package de préparation versionné |
| `submission` | candidate, manifeste, signature, P5, export et preuve humaine | package/hash/evidence append-only |
| `patron_action` | file d’actions, résultats P6/P7, REX, suspension, export et conservation | faits Patron append-only |
| `knowledge` | extraction/retrieval borné et preuves de source | fragments non financiers indexés |
| `audit` / `platform` | commandes, reçus, événements, outbox, sécurité et observabilité | infrastructure transactionnelle |

Chaque module possède ses contrats publics et ne lit les autres modules qu’au travers de ports ou lecteurs dédiés. Les routes HTTP ne contiennent pas de règle métier nouvelle.

## 3. Flux d’une commande

```text
HTTP bearer + CSRF
  → résolution serveur du contexte
  → policy / classification / affectation
  → commande Pydantic extra=forbid
  → CommandDispatcher
  → reçu d’idempotence
  → handler du module
  → transaction PostgreSQL
  → événement append-only + outbox
  → projection / réponse fermée
```

Une commande sensible porte `command_id`, `idempotency_key`, `correlation_id`, tenant, actor et membership résolus côté serveur. Les rejeux retournent le reçu existant ; une clé réutilisée avec un autre contenu est refusée.

## 4. Données et migrations

- toutes les tables métier sont tenant-scoped et portent les contraintes d’intégrité adaptées ;
- les transitions et preuves critiques sont append-only ;
- les migrations Alembic sont linéaires, réversibles lorsque le contrat le permet et vérifiées sur une tête fraîche ;
- les fichiers bruts restent privés, les projections exposent seulement les métadonnées autorisées ;
- les hashes, versions, locators et manifestes sont calculés côté serveur ;
- aucun cache, vecteur, LLM ou frontend ne devient une source de vérité transactionnelle.

La tête de migration actuelle est celle du code exécuté dans le dépôt. Toute nouvelle migration exige un test de contrat, une montée propre et une descente vérifiée lorsque possible.

## 5. Sécurité d’exécution

1. Une session `PASSWORD` ne traverse jamais une route métier sans MFA.
2. Les actions sensibles exigent un step-up récent.
3. Le tenant, le rôle, l’affectation et la délégation sont déterminés par le serveur.
4. Un Collaborateur ne reçoit ni marge, ni coût, ni trésorerie, ni pouvoir Patron.
5. Les erreurs HTTP restent neutres pour les ressources étrangères.
6. Les uploads sont bornés, scannés, privés et fail-closed.
7. Les contenus hostiles restent isolés et ne sont pas exécutés ni envoyés au modèle.
8. Les secrets ne sont pas écrits dans le navigateur, les logs, les événements ou les contrats publics.
9. La reprise après expiration ou résultat inconnu conserve le dernier état confirmé.

## 6. Contrats frontend

Le frontend consomme des projections et commandes fermées via `web/src/infrastructure/api.ts`. Il ne fabrique jamais :

- l’identité, le rôle, le tenant ou l’affectation ;
- les montants et agrégats financiers ;
- un succès d’export, de dépôt ou de réception ;
- un état `UNKNOWN`, `PARTIAL` ou `REVIEW_REQUIRED` converti en succès ;
- un identifiant d’Affaire avant confirmation serveur.

Les erreurs sont annoncées, les formulaires sont labelisés, les états difficiles restent textuels et les actions sensibles sont masquées ou désactivées selon la politique serveur.

## 7. Contrats d’événements et audit

Chaque événement contient au minimum : tenant, agrégat, révision, type, payload versionné, actor, command, correlation et date. Les payloads ne contiennent ni secret ni contenu financier lorsqu’un contrat non financier suffit.

L’outbox n’affirme jamais la livraison externe. Un statut `NOT_CONFIGURED`, `UNKNOWN` ou `NOT_PERFORMED` reste visible jusqu’à une preuve contrôlée.

## 8. RAG et IA

- l’index ignore les fragments `FINANCIAL_PRIVATE` hors portée Patron ;
- toute recherche est limitée au tenant, à la Case, au DCE et au rôle ;
- les résultats portent score, fragment, version et locator, sans créer d’autorité ;
- l’IA peut proposer extraction, classification ou question, mais une personne habilitée décide ;
- une panne IA bascule vers la lecture et la revue manuelles ;
- une instruction hostile devient une revue requise, jamais une commande.

## 9. Tests de sortie

Chaque tranche doit fournir :

- tests unitaires des invariants de domaine ;
- tests PostgreSQL sur migration, tenant, idempotence et append-only ;
- tests API des rôles, refus neutres et contrats fermés ;
- tests web du parcours, des erreurs, du clavier et du responsive ;
- lint, typecheck, build, format et `git diff --check` ;
- preuve documentaire reliée au plan global et à Basic Memory.

Les résultats inconnus, expirés, protégés, contradictoires, partiels et hostiles sont des cas de sortie obligatoires, pas des exceptions optionnelles.

## 10. Déploiement et exploitation

- images Docker versionnées et non exécutées avec privilèges inutiles ;
- secrets injectés par environnement, jamais dans Git ;
- PostgreSQL sauvegardé et restaurable avant données client ;
- healthcheck séparant API, base, stockage privé, antivirus et outbox ;
- logs structurés sans secrets, avec correlation et code de refus ;
- migrations exécutées avant l’application et tête vérifiée ;
- rollback d’application séparé du rollback de données ;
- aucune activation production avant les gates de sécurité, restauration et non-régression.

## 11. Cartographie vers le Product Freeze

| Exigence produit | Contrat technique |
|---|---|
| preuve avant conclusion | source/version/hash/locator sur les projections et événements |
| séparation Patron/Collaborateur | `AuthorizationPolicy`, `DataClassification`, context resolver et lecteurs filtrés |
| P0–P7 distincts | modules `opportunity`, `decision`, `preparation`, `submission`, `patron_action` |
| inconnu honnête | états `UNKNOWN`, `PARTIAL`, `REVIEW_REQUIRED`, reçus idempotents |
| dépôt humain | export local, `external_submission: NOT_PERFORMED`, preuve manuelle liée au manifeste |
| continuité | sessions, ownership, délégation, handover, suspension et recovery append-only |
| accessibilité | HTML natif, focus visible, rôles ARIA minimaux, reflow et erreurs annoncées |

## 12. Limites et décisions à venir

Ce cahier ne déclare pas la production prête, ne crée pas de Rust, ne choisit pas de fournisseur IA, ne promet pas de connecteur de portail et ne remplace pas les procédures d’exploitation. Les détails de déploiement, observabilité, restauration et qualification de production seront complétés par les tranches Phase 10–11.

## Références

- `docs/00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md`
- `docs/03_PRODUCT_DESIGN_WORKING/SMART_AO_UX_FREEZE_GLOBAL_v0.1.md`
- `docs/01_IMPLEMENTATION_ACTIVE/SMART_AO_Architecture_Logicielle_v3.1_REFERENCE_DIRECTRICE_PHASE0.md`
- `docs/02_FUTURE_TECHNICAL/SMART_AO_EXP_01_CAHIER_TECHNIQUE_EXECUTION_v0.1.md`
- `docs/03_PRODUCT_DESIGN_WORKING/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md`
