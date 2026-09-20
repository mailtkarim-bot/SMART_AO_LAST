# SMART AO — EXP-02 : OWNER EXPERIENCE FREEZE

**Statut :** GEL D’EXPÉRIENCE DÉLÉGUÉ · PREUVES EXÉCUTÉES  
**Date :** 15 septembre 2026  
**Autorité :** délégation propriétaire explicite reçue dans le fil Codex  
**Références :** cahier OWNER v0.4 et catalogue OWNER_CONSOLIDATED v0.3

## 1. Périmètre gelé

EXP-02 couvre le chemin suivant :

```text
source BOAMP publique
  → observation conservée et fraîcheur visible
  → qualification humaine P0/P1
  → décision indépendante du score public
  → Affaire unique avec provenance conservée
```

Une panne de source laisse les observations précédentes visibles, affiche le dernier succès connu et ouvre la saisie manuelle existante. Elle ne fabrique pas une liste vide réputée fiable et ne certifie jamais l'exhaustivité de BOAMP.

## 2. Arbitrages gelés

| Sujet | Décision |
|---|---|
| Autorité P0/P1 | `PATRON_ADMIN` et capacités serveur existantes ; Responsable/Expert restent des profils opérationnels sans élévation ni accès Radar depuis le navigateur. |
| Score | `BOAMP_PUBLIC_V1` sert au tri et expose ses facteurs ; il ne déclenche aucune qualification, ouverture ou décision. |
| Panne | `BoampRegistryUnavailable` est mappé vers `source_status.state=UNAVAILABLE` ; la dernière collecte `RECORDED` reste datée. |
| État inconnu | `UNKNOWN` est explicite lorsque la sonde n'est pas configurée ; aucune mention « à jour ». |
| Saisie manuelle | Le formulaire et `POST /api/v1/cases` existants restent l'unique voie ; `origin_kind=MANUAL`, auteur et identifiants idempotents sont conservés. |
| Idempotence | Même clé = même reçu ; nouvelle clé sur la même observation = `DUPLICATE_FUNCTIONAL_IDENTITY`, sans second dossier ni second événement. |
| Responsive | Le Radar passe en une colonne sous 900px ; le détail, le score et les actions s'empilent sous 560px. |

## 3. Preuves et limites

- PostgreSQL dédié : **7 tests** ciblés, dont la lecture tenant-scopée du dernier succès.
- Backend non-DB : **3 tests** de statut source (`AVAILABLE`, `UNAVAILABLE`, `UNKNOWN`) ; les contrats BOAMP existants restent verts.
- Front ciblé : **6 tests** du panneau, dont panne, dernier succès, relance et saisie manuelle.
- Suite front complète : **148 tests** ; build, lint et typecheck passent après la tranche.
- Ruff ciblé et `git diff --check` passent.
- La suite historique `TestClient` reste bloquée au premier appel par l'environnement Starlette/httpx ; elle n'est pas déclarée verte. Le chemin HTTP réel avait déjà été sondé sous Uvicorn pour les invariants d'authentification et de projection.

## 4. Hors périmètre gelé

- Les états formels `ATTENTE` et `ABANDON` restent une extension distincte de l'agrégat `Decision`.
- La collecte planifiée et la persistance d'un run restent des opérations bornées séparées de la lecture Radar.
- Les lots identifiés, l'import DCE et les expériences EXP-03+ restent dans leurs tranches dédiées.

## 5. Effet du gel

Le code et les documents actifs peuvent avancer vers EXP-03 sans rouvrir ces arbitrages. Toute divergence future doit être une décision versionnée et reliée à une preuve ; elle ne peut pas changer silencieusement le comportement du Radar ou de la création manuelle.

**Prochaine étape :** ouvrir EXP-03 par l’audit de réception contrôlée, quarantaine, antivirus et reprise d’un DCE.
