# SMART_AO V8

SMART_AO V8 est un SaaS web dédié aux entreprises françaises du BTP pour qualifier les appels d'offres, analyser les DCE, préparer les réponses et sécuriser les décisions patronales.

> Le socle durable (**Case**, **Consultation/DceVersion**, **Decision**, sécurité tenant-scoped et outbox) est complété par des parcours métier contrôlés : préparation collaborative, génération technique versionnée, cockpit patron initial, chiffrage confidentiel et paquet de dépôt immutable. Le système ne déclare jamais un dépôt externe réussi sans accusé de réception vérifiable.

## Principes non négociables

- Le patron décide, chiffre, valide et dépose ; le collaborateur prépare et transmet.
- Les prix, marges, devis et données de trésorerie ne traversent jamais les contrats collaborateur.
- Une transaction modifie un aggregate métier propriétaire ; les effets inter-modules passent par événements, outbox et commandes idempotentes.
- Les versions DCE, contextes de décision et résultats validés sont non destructifs.
- Le domaine reste pur : FastAPI, SQLAlchemy, MinIO, workers et LLM restent hors de `domain/`.

## Démarrage local prévu

```bash
cp .env.example .env
make up
make test
```

Le dépôt se démarre localement avec Docker Compose ou les services de développement disponibles. Avant une mise en production, le runbook VPS doit encore être exécuté sur un hôte réel : images digest-pinnées, PostgreSQL, ClamAV/EICAR, Caddy/HTTPS, sauvegarde hors hôte, restauration isolée et supervision.

## Documentation

- [Documentation active](docs/README_DOCUMENTATION.md)
- [Index des références actives](docs/00_REFERENCE_ACTIVE/00_INDEX_REFERENCE_ACTIVE.md)
- [Product Freeze v2.0](docs/00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v2.0.md)
- [Cahier technique d’exécution](docs/02_FUTURE_TECHNICAL/SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v2.1.md)
- [Plan global de conception et réalisation](docs/03_PRODUCT_DESIGN_WORKING/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md)
- [Checklist durable](todo.md)

## Structure

- `backend/app/modules/` : modules métier isolés.
- `backend/app/platform/` : mécanismes transversaux sans métier BTP.
- `backend/app/interfaces/` : interfaces HTTP minces.
- `backend/tests/` : tests de domaine, intégration, architecture, concurrence, sécurité et processus.
- `web/` : frontend React/Vite, organisé par fonctionnalités métier.
- `docs/` : contrats actifs et point de reprise inter-session.
