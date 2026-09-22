# SMART AO — Recette métier locale bornée Phase 11 v0.1

**Date :** 22 septembre 2026  
**Statut :** QUALIFIÉE LOCALEMENT — GO CONDITIONNEL LOCAL  
**Autorité produit/métier :** `docs/00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md`

## Périmètre

Cette recette vérifie les actes métier déjà implémentés sur des fixtures locales et une base PostgreSQL Docker locale. Elle couvre les refus et états difficiles sans utiliser de données client, de fournisseur externe, de VPS ou de dépôt public.

| Bloc | Vérification | Résultat |
|---|---|---|
| G01–G09 | gate P3/P5, version rectificative, contradiction, coût non couvert, édition dérivée, échéance inconnue, fichier protégé, inventaire partiel et contenu hostile | 10 scénarios métier et preuves append-only | 
| P6/P7 | résultat `WON`, commande, contrôle P6, résultat P7, rejeu et capitalisation bornée | couvert par les tests PostgreSQL ciblés |
| Contrats ops | tête Alembic, runbooks, flags OCR/RAG, Product Freeze, sauvegarde et contrats de déploiement | 45 tests ops inclus dans le lot |
| Frontend | authentification, MFA, contexte, Affaire, DCE, décision, préparation, remise et refus | 34 fichiers, 187 tests |

## Exécution reproductible

```bash
SMART_AO_TEST_DATABASE_URL='postgresql+psycopg://smart_ao:dev_password_12345@127.0.0.1:5432/smart_ao_v7_dev' \
  uv run pytest -q \
  backend/tests/application/test_g01_g09_business_fixtures.py \
  backend/tests/application/test_case_outcome_contract.py \
  backend/tests/application/test_case_order_p6.py \
  backend/tests/ops

cd web && pnpm test -- --run
```

## Résultats du 22 septembre 2026

- lot métier G01–G09, P6/P7 et contrats ops : **62 tests passés en 7,94 s** ;
- frontend : **187 tests passés sur 34 fichiers en 12,67 s** ;
- PostgreSQL utilisé localement, aucune écriture dans une base distante ;
- aucun dépôt externe, envoi SMTP/webhook, signature fournisseur ou index RAG permanent exécuté.

## Écarts requalifiés

| Écart | Traitement local | Statut |
|---|---|---|
| typecheck, lint et build frontend | rejoués après la recette | **FERMÉ — vert** |
| tests métier G01–G09 et contrats ops | 62 tests rejoués avec PostgreSQL local | **FERMÉ — vert** |
| recette lecteur d’écran réelle | non simulable honnêtement par les tests structurels | **OUVERT — vérification manuelle requise** |
| Bandit complet | assertions applicatives remplacées par des refus explicites, hash factice marqué comme fixture et scan complet rejoué | **FERMÉ — 0 alerte** |
| Golden DCE réel, droits et anonymisation | aucun corpus client introduit | **OUVERT — attestation propriétaire requise** |
| VPS, domaine, sauvegarde hors site et reprise matérielle | aucun fournisseur disponible | **OUVERT — exploitation future** |
| SMTP, webhook et signature externes | flags désactivés, aucun envoi présumé | **OUVERT — intégration fournisseur future** |
| `detect-secrets` | hook CI rejoué via `uvx` sur les fichiers suivis, baseline mis à jour pour les lignes déplacées | **FERMÉ — vert** |
| scan Trivy sur images | outil absent de l’hôte local | **OUVERT — runner outillé requis** |

## Rejeu de clôture locale — 22 septembre 2026

- `pip-audit .` : aucune vulnérabilité connue ;
- `pnpm audit --prod --registry=https://registry.npmjs.org` : 0 vulnérabilité sur 3 dépendances de production ;
- hook `detect-secrets` CI : vert sur les fichiers suivis avec `.secrets.baseline` mis à jour ;
- Bandit complet sur `backend/app` : 0 alerte ;
- lot backend borné : 62/62 ;
- frontend : 187/187 ; typecheck, lint et build déjà verts.
- rejeu backend complet après corrections : **1 720/1 720 tests passés**, 10 avertissements non bloquants ;
- rejeu frontend complet après corrections : **187/187 tests passés**, typecheck, lint et build verts.
- images locales backend/workers et frontend inspectées : utilisateurs `smartao` et `nginx`, bases d’images digest-pinnées dans les Dockerfiles ; healthcheck frontend présent et healthchecks backend portés par Compose ; configuration Compose exige volontairement les secrets runtime et refuse les placeholders absents.
- constantes FastAPI dépréciées remplacées sur les routes ; suite API rejouée : **540 tests passés**, un seul avertissement provenant de la dépendance Starlette/httpx.
- simulation préproduction locale rejouée après génération dynamique des secrets : HTTPS/DB/schema/ClamAV OK, 20 requêtes, 100 requêtes à concurrence 10 en 1 170 ms (85,47 req/s), redémarrages, incident ClamAV, backup/restauration 127 tables et rotation JWT : **PASS** ; la variation de débit reste un repère local et non un budget VPS.

## Limites et décision

Cette recette prouve une tranche locale bornée. Elle ne vaut pas recette client, pilote, validation Golden DCE réel, test de fournisseur externe, budget VPS, sauvegarde hors site ou décision d’ouverture publique. Les états inconnus restent visibles et les refus ne sont pas convertis en succès.

**Verdict :** `PASS LOCAL BORNÉ` — poursuivre la conception et les corrections localement ; `NO-GO PUBLIC` maintenu.
