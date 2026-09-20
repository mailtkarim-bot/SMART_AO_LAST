# SMART AO — AUD-01 — Carte du dépôt, interfaces et dépendances

**Date :** 12 septembre 2026  
**Référence :** `feat/ccap-cctp-risk-register-20260831@b6b05b8`  
**Statut :** TERMINÉ  
**Verdict :** monolithe modulaire réel, frontières publiques présentes, composition et dépendances encore trop centrales

## 1. Inventaire exécutif

| Mesure | Résultat observé |
|---|---:|
| Fichiers Python dans `backend/app` | 390 |
| Modules métier dans `backend/app/modules` | 13 |
| Fichiers de routes HTTP | 35 |
| Endpoints HTTP détectés | 111 |
| Workers applicatifs | 9 exécutables + `__init__.py` |
| Migrations Alembic | 67 |
| Tables ORM | 102 |
| Fichiers de tests backend | 234 |
| Tests collectés | 1 624 |

Le dépôt est déjà structuré en `public`, `application`, `domain` et `infrastructure` sur les modules les plus mûrs. Il ne justifie pas un rewrite. La trajectoire correcte consiste à renforcer les frontières existantes et à déplacer progressivement les propriétaires.

## 2. Carte de haut niveau

```text
web/                         interface React/Vite
backend/app/api/             routes HTTP et dépendances FastAPI
backend/app/bootstrap/       composition runtime
backend/app/modules/         capacités métier modulaires
backend/app/platform/        sécurité, persistance, événements, stockage
backend/app/workers/         processus asynchrones/one-shot
backend/alembic/             67 migrations
backend/tests/               tests application, intégration, architecture
ops/                         préproduction, corpus Golden et exploitation
scripts/                     contrôles et simulations opérateur
```

## 3. Modules et maturité de frontière

| Module | Fichiers | Couches observées | Interface publique | Diagnostic |
|---|---:|---|---|---|
| `case` | 14 | public/application/domain/infrastructure | contrats de création et lecture | `KEEP + ADAPT`, centre Affaire déjà réel |
| `dce` | 41 | quatre couches | contrats très étendus | `KEEP + ADAPT`; certains contrats financiers/affectation sont mal logés |
| `decision` | 45 | quatre couches | cycle, risques, finalisation | `KEEP + EXTEND` |
| `enterprise` | 19 | public/application/infrastructure | société, bibliothèque, capacités | `KEEP + EVOLVE`; domaine explicite absent |
| `knowledge` | 14 | quatre couches | recherche | `KEEP + MEASURE` |
| `market_watch` | 4 | public/application/infrastructure | avis BOAMP | faible ; chevauche `opportunity` |
| `membership` | 46 | public/application/infrastructure | affectations, tâches, capacités | responsabilité trop large |
| `opportunity` | 19 | quatre couches | veille et BOAMP | `KEEP + ADAPT` |
| `optimization` | 8 | application/infrastructure | aucune couche `public` | capacité isolée, intégration à prouver |
| `patron_action` | 13 | quatre couches | action patron et port | `KEEP` |
| `preparation` | 17 | public/application/infrastructure | paquets, revues, transmissions | `KEEP + ALIGN` vers Response |
| `pricing` | 30 | quatre couches | scénario, import, publication | `KEEP + REPOSITION` |
| `submission` | 23 | public/application/infrastructure | paquet, preuve, signature | `KEEP + ALIGN` |

L'absence d'une couche `domain` n'est pas, seule, une faute. Elle signale ici que le modèle et ses invariants vivent souvent dans les services applicatifs ou les modèles de persistance, ce qui compliquera le déplacement des propriétaires.

## 4. Composition réelle

`backend/app/bootstrap/application.py` est le véritable composition root. Il dépasse 1 200 lignes et construit directement une grande partie des dépôts, services, façades et lecteurs croisés. `backend/app/bootstrap/module_registry.py` et `container.py` sont des coquilles vides ou documentaires ; `production.py` ajoute le câblage de production.

Conséquences :

- l'application reste déployable comme un seul processus, ce qui convient à la cible ;
- les dépendances sont visibles, mais trop concentrées dans une classe/runtime central ;
- plusieurs lecteurs traversent directement les infrastructures des modules ;
- la future séparation doit être incrémentale : contrats publics, événements et projections avant déplacement physique.

## 5. Dépendances directes inter-modules

Le scan AST des imports Python a trouvé les arêtes suivantes :

| Source | Cible | Imports directs |
|---|---|---:|
| `dce` | `case` | 6 |
| `decision` | `case` | 5 |
| `decision` | `dce` | 9 |
| `decision` | `patron_action` | 1 |
| `decision` | `pricing` | 3 |
| `knowledge` | `case` | 1 |
| `knowledge` | `dce` | 1 |
| `membership` | `case` | 8 |
| `membership` | `dce` | 12 |
| `membership` | `enterprise` | 2 |
| `membership` | `pricing` | 5 |
| `opportunity` | `case` | 1 |
| `opportunity` | `market_watch` | 1 |
| `preparation` | `dce` | 3 |
| `preparation` | `enterprise` | 1 |
| `preparation` | `membership` | 5 |
| `preparation` | `patron_action` | 1 |
| `pricing` | `case` | 2 |
| `submission` | `case` | 1 |
| `submission` | `dce` | 2 |
| `submission` | `decision` | 5 |
| `submission` | `enterprise` | 1 |
| `submission` | `patron_action` | 1 |
| `submission` | `preparation` | 1 |
| `submission` | `pricing` | 1 |

Ces nombres mesurent des déclarations d'import, pas le volume d'appels ni leur danger. Ils révèlent cependant les nœuds de couplage : `dce`, `case`, `membership`, `decision` et `submission`.

## 6. Frontières contrôlées

La suite `backend/tests/architecture` passe avec 75 tests. Elle interdit plusieurs dérives et maintient une liste de **21 exceptions connues application → infrastructure**. Le test demande que la liste rétrécisse et n'augmente pas.

Ce résultat signifie :

- l'architecture actuelle possède des règles exécutables ;
- la dette est recensée et contenue ;
- la cible v3.1 « aucune dépendance interne directe » n'est pas encore atteinte ;
- une PR de déplacement massif serait plus risquée que l'extraction progressive de contrats.

## 7. Interfaces publiques observées

| Module | Contrats publics utiles à préserver |
|---|---|
| `case` | création d'Affaire, lecteurs/projections |
| `dce` | versions, lectures, exigences, confirmation, risques contractuels |
| `decision` | cycle de décision, risques, liens risque-exigence, finalisation |
| `enterprise` | société, bibliothèque documentaire, capacités |
| `knowledge` | recherche/retrieval |
| `market_watch` | lecture d'avis |
| `membership` | affectations, travail, capacités |
| `opportunity` | profils de veille, BOAMP, qualification |
| `patron_action` | actions à arbitrer |
| `preparation` | paquet, revue, transmission |
| `pricing` | scénarios, import, snapshots/publication |
| `submission` | paquet, preuves de remise, signature |

`optimization` ne possède pas de frontière publique formalisée. Ce module ne doit pas être élargi avant qu'un cas produit et un benchmark établissent son utilité.

## 8. Écarts structurants et action bornée

| Écart | Risque | Traitement proposé |
|---|---|---|
| composition root géant | modifications transversales fragiles | documenter en A0, extraire seulement lors d'un changement réel |
| 21 exceptions de couche | couplage aux détails SQL | ne pas en ajouter ; réduire par les PR verticales |
| `dce/public/contracts.py` porte des notions voisines | ownership confus | déprécation additive après MAP-01, jamais renommage massif |
| `membership` agrège identité et travail | règles de droits et workflow mêlées | séparation logique Identity/Collaboration avant déplacement |
| `market_watch` chevauche `opportunity` | double propriétaire BOAMP | conserver adaptateur, rendre Opportunity propriétaire |
| `optimization` sans contrat public | dépendance difficile à stabiliser | mesurer et différer son exposition |

## 9. Conclusion

Le monolithe modulaire est une base adaptée à v3.1. Le travail à venir ne consiste pas à reconstruire le produit, mais à rendre les propriétaires et contrats explicites. MAP-01 nomme ces propriétaires ; MIG-01 décrit leur trajectoire.

## 10. Preuves

- `backend/app/bootstrap/application.py`
- `backend/app/bootstrap/module_registry.py`
- `backend/app/modules/`
- `backend/app/api/routes/`
- `backend/tests/architecture/test_application_infrastructure_boundary.py`
- [MAP-01 — Context map](./SMART_AO_PHASE0_MAP-01_CONTEXT_MAP.md)
- [MIG-01 — Matrice de migration](./SMART_AO_PHASE0_MIG-01_MATRICE_MIGRATION.md)

