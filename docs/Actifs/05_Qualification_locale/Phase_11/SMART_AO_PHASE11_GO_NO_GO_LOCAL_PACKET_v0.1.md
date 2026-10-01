# SMART AO — Dossier GO/NO-GO local Phase 11 v0.1

**Date :** 21 septembre 2026  
**Statut :** DÉCISION PROPRIÉTAIRE REÇUE
**Décision proposée :** `GO CONDITIONNEL LOCAL` / `NO-GO OUVERTURE PUBLIQUE`

**Soumission :** 21 septembre 2026 — la recette locale peut continuer ; aucune ouverture publique n’est autorisée.
**Décision propriétaire :** « J’approuve le GO conditionnel local et je maintiens le NO-GO public. »

## 1. Résultat proposé

SMART AO peut continuer sa recette locale et ses qualifications techniques. L’ouverture publique et la déclaration de production restent interdites tant que les dépendances d’infrastructure et de gouvernance listées ci-dessous ne sont pas fermées.

## 2. Preuves vertes

| Domaine | Preuve |
|---|---|
| Backend | 1 720 tests collectés verts après restauration de l’extra calendrier |
| Frontend | 187 tests sur 34 fichiers |
| Exploitation | 45 tests ops |
| Python | pip-audit sans vulnérabilité connue du projet |
| Frontend | pnpm audit officiel : 0 vulnérabilité production |
| Code | Bandit vert ; syntaxe shell ; diff check |
| Local preprod | PostgreSQL, ClamAV, migrations, backend, frontend, Caddy, workers |
| Résilience | charge bornée, redémarrages, incident ClamAV et récupération |
| Sauvegarde | backup, restauration isolée de 127 tables, tête `20260920_0090` |
| RAG temporaire | ancres 3/3, refus financier, fuite 0, nettoyage mémoire 116 → 0 |

## 3. Bloqueurs NO-GO public

- aucun VPS, domaine public, firewall distant ou supervision externe ;
- aucune sauvegarde hors site ni test de reprise matérielle ;
- Golden DCE réel sans attestation finale de droits, anonymisation, double revue et désaccords ;
- SMTP, webhook et signature externes non testés avec fournisseurs réels ;
- `detect-secrets` absent du poste courant ;
- OCR/Docling/RAG installés mais runtime désactivé et index métier permanent absent ;
- recettes PUX/G01–G52 et intégrations métier encore partielles selon la matrice globale.

## 4. Décision propriétaire attendue

- [x] **GO CONDITIONNEL LOCAL** : poursuivre les recettes, benchmarks, corpus et corrections sans ouvrir au public ;
- [x] **NO-GO PUBLIC MAINTENU** : aucune mise en ligne ni donnée client ; position soumise ;
- [ ] **OUVERTURE PUBLIQUE** : impossible à approuver tant que les bloqueurs ci-dessus ne sont pas fermés.

## 5. Conditions de réouverture publique

1. VPS et domaine provisionnés ;
2. Compose préproduction déployé et smoke HTTPS vert ;
3. backup hors site et restauration vérifiée ;
4. rotation des secrets opérée ;
5. Golden DCE approuvé ;
6. intégrations externes testées ou explicitement désactivées ;
7. recettes métier restantes acceptées ;
8. décision GO/NO-GO propriétaire sur preuves consolidées.
