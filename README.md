# SMART_AO V8

SMART_AO V8 vise la maîtrise des engagements d'une Affaire BTP, de l'étude DCE aux décisions, à la passation et aux événements chantier. Les fonctionnalités attendues et la personnalisation sont décrites dans les cahiers V3.1 ; leur présence dans ces cahiers ne signifie pas qu'elles sont toutes livrées.

> Le socle durable (**Case**, **Consultation/DceVersion**, **Decision**, sécurité tenant-scoped et outbox) est complété par des parcours métier contrôlés : préparation collaborative, génération technique versionnée, cockpit patron initial, chiffrage confidentiel et paquet de dépôt immutable. Le système ne déclare jamais un dépôt externe réussi sans accusé de réception vérifiable.

## Principes non négociables

- Le patron décide, chiffre, valide et dépose ; le collaborateur prépare et transmet.
- Les prix, marges, devis et données de trésorerie ne traversent jamais les contrats collaborateur.
- Une transaction modifie un aggregate métier propriétaire ; les effets inter-modules passent par événements, outbox et commandes idempotentes.
- Les versions DCE, contextes de décision et résultats validés sont non destructifs.
- Le domaine reste pur : FastAPI, SQLAlchemy, MinIO, workers et LLM restent hors de `domain/`.

## Reprendre le codage

Lire `AGENTS.md`, l'index actif et le début du plan global : une seule tranche active, ordre A0 → S0 (sources) → M0 (version de méthode) → A1 → M1 (éditeur) → B → C, critères de fin et limites de preuve. Vérifier `git status` et HEAD avant toute modification ; le checkout contient du travail local non qualifié. Ne pas supposer une suite verte à partir d'un ancien handoff. Aucun push ; NO-GO public maintenu.

## Démarrage local prévu

```bash
cp .env.example .env
make up
make test
```

Le dépôt se démarre localement avec Docker Compose ou les services de développement disponibles. Avant une mise en production, le runbook VPS doit encore être exécuté sur un hôte réel : images digest-pinnées, PostgreSQL, ClamAV/EICAR, Caddy/HTTPS, sauvegarde hors hôte, restauration isolée et supervision.

## Documentation

- [Documentation active](docs/README_DOCUMENTATION.md)
- [Index des références actives](docs/Actifs/00_INDEX_DOCUMENTATION_ACTIVE.md)
- [Product Freeze v3.1 intégral](docs/Actifs/01_Cahiers_des_charges/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v3.1.md)
- [Master métier v3.1 intégral](docs/Actifs/01_Cahiers_des_charges/SMART_AO_CAHIER_DIRECTEUR_METIER_MASTER_v3.1.md)
- [Cahier technique d’exécution](docs/Actifs/01_Cahiers_des_charges/SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v3.1.md)
- [Plan global de conception et réalisation](docs/Actifs/00_Pilotage_et_audits/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md)
- [Checklist technique historique](todo.md) — ne remplace pas le plan global

## Structure

- `backend/app/modules/` : modules métier isolés.
- `backend/app/platform/` : mécanismes transversaux sans métier BTP.
- `backend/app/interfaces/` : interfaces HTTP minces.
- `backend/tests/` : tests de domaine, intégration, architecture, concurrence, sécurité et processus.
- `web/` : frontend React/Vite, organisé par fonctionnalités métier.
- `docs/` : contrats actifs et point de reprise inter-session.
