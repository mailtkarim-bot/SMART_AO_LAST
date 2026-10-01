# SMART AO — EXP-06 : OWNER EXPERIENCE FREEZE

**Statut :** GEL D’EXPÉRIENCE DÉLÉGUÉ · PREUVES EXÉCUTÉES · DÉPÔT EXTERNE NON EFFECTUÉ  
**Date :** 19 septembre 2026  
**Autorité :** délégation propriétaire explicite reçue dans le fil Codex  
**Références :** cahier OWNER v0.4, catalogue OWNER_CONSOLIDATED v0.3, [`SMART_AO_EXP_06_VALIDATION_SIGNATURE_DEPOT_RECEPTION_AUDIT_v0.1.md`](SMART_AO_EXP_06_VALIDATION_SIGNATURE_DEPOT_RECEPTION_AUDIT_v0.1.md), [`SMART_AO_EXP_06_RECEPTION_PARTIELLE_MANIFESTE_AUDIT_PREUVE_v0.1.md`](SMART_AO_EXP_06_RECEPTION_PARTIELLE_MANIFESTE_AUDIT_PREUVE_v0.1.md)

## 1. Périmètre gelé

EXP-06 couvre la préparation d'une candidate, son contrôle P5, sa signature éventuelle, son export local et la conservation des faits de remise humaine :

```text
contenu validé
  → package immuable et manifeste exact
  → autorisation P5 avec MFA
  → signature séparée si nécessaire
  → export ZIP déterministe et audité
  → dépôt humain hors SMART AO
  → preuve manuelle liée au hash, PARTIAL ou UNKNOWN
```

Le mode `FULL` peut inclure le snapshot financier publié. Le mode `CANDIDATURE_ONLY` exige une justification et omet le snapshot financier ainsi que l'entrée de pricing. Dans les deux modes, le périmètre `Case.scope_json`, les exclusions et `external_submission: NOT_PERFORMED` restent dans le manifeste exact.

## 2. Arbitrages gelés

| Sujet | Décision |
|---|---|
| Autorité | Le serveur détermine tenant, rôle, MFA, révision, manifeste et porte de décision ; le navigateur ne peut pas élever ses droits. |
| P5 | Patron Admin ou Delegate habilité avec MFA peut autoriser une version et un hash exacts ; l'autorisation est append-only. |
| Candidature seule | Elle est choisie explicitement et sa justification est persistée ; l'absence de prix n'est jamais convertie en zéro. |
| Signature | Une intention de signature est un fait séparé, rattaché au hash du manifeste ; elle ne vaut pas dépôt. |
| Export et sauvegarde | L'export ZIP est déterministe, hashé et audité. La copie de sauvegarde est conservée par l'opérateur ; SMART AO ne la déclare pas comme un dépôt externe. |
| Redépôt | Une nouvelle intention produit une nouvelle version de package ; cette version doit recevoir une nouvelle autorisation P5 avant export. |
| Réception | `MANUAL_RECEIPT` et `MANUAL_PORTAL_REFERENCE` restent `RECEIVED/PARTIAL`; `HUMAN_DEPOSIT_ATTEMPT` reste `UNKNOWN/PARTIAL` tant qu'aucun fait externe contrôlé n'est fourni. |
| Confidentialité | Les clés de stockage, montants et résultats externes sont exclus du manifeste et des projections Patron-only. |

## 3. Rôles, refus et états difficiles

- une session sans MFA est refusée sur les actes sensibles ;
- un Collaborateur, un tenant différent ou une préparation absente reçoit un refus neutre ;
- une révision périmée renvoie `VERSION_CONFLICT` ;
- une candidature seule sans justification renvoie `CANDIDATURE_ONLY_REASON_REQUIRED` ;
- un manifeste altéré renvoie `SUBMISSION_MANIFEST_INTEGRITY_FAILED` ;
- une décision non prête, une préparation bloquée ou un document technique absent empêche le package ;
- un export sans P5 exacte renvoie `SUBMISSION_PACKAGE_NOT_AUTHORIZED` et ne lit pas le stockage privé ;
- une réponse réseau inconnue conserve les identifiants d'intention dans le hook front pour permettre le rejeu ;
- une tentative humaine ne devient jamais une réussite externe implicite.

## 4. Critères d'acceptation observables

1. Le Patron voit le mode, le périmètre, la version, le hash et les exclusions avant P5.
2. Le bouton d'export apparaît seulement après l'autorisation P5 exacte.
3. Le panneau propose explicitement `Paquet complet` ou `Candidature seule` et demande une justification dans le second cas.
4. Les preuves manuelles affichent leur type, leur version, leur hash et leur statut sans révéler de contenu sensible.
5. Une nouvelle version de package n'hérite d'aucune autorisation de la version précédente.
6. Aucun état `UNKNOWN`, `PARTIAL` ou `NOT_PERFORMED` n'est rendu comme dépôt réussi.

## 5. Limites assumées

Ce gel ne crée aucun fournisseur de portail, worker de dépôt, registre de lots ou signataire légal. Le dépôt, la copie de sauvegarde et le contenu d'un reçu restent des actes humains hors système. Le rapprochement complet par lot, fichier remis, tour de portail et accusé contrôlé est donc explicitement hors périmètre et reste `PARTIAL`.

## 6. Preuves exécutées

- PostgreSQL ciblé : **37 tests** `test_submission_package.py` + `test_submission_evidence.py`, dont candidature seule, tentative humaine inconnue et redépôt versionné ;
- Front : **165 tests** sur 31 fichiers passent avec `--pool=threads --maxWorkers=1` ;
- `pnpm --dir web typecheck` et `pnpm --dir web build` passent ;
- Ruff, format Ruff, test du contrat de tête Alembic et `git diff --check` passent.

## 7. Effet du gel

EXP-06 est suffisamment prouvée pour ouvrir EXP-07 sans rouvrir la séparation P5/export/réception, le refus des rôles, la candidature seule, l'idempotence de version ou l'invariant de non-dépôt. Toute extension du dépôt externe devra apporter son propre contrat de source, ses états inconnus, sa preuve de sécurité et sa recette verticale.

**Prochaine étape :** ouvrir EXP-07 sur l'enregistrement du résultat par lot et la passation, en conservant `external_submission: NOT_PERFORMED` tant qu'aucune source de dépôt n'est intégrée.
