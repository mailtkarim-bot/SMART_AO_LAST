# SMART_AO_V8 — bilan final post-fusion

**Date : 25 août 2026**  
**Dépôt :** [mailtkarim-bot/SMART_AO_V8](https://github.com/mailtkarim-bot/SMART_AO_V8)  
**Branche finale :** `main`  
**Dernier commit connu :** `7cdb4af docs: reconcile post-fusion delivery status`

## Conclusion exécutive

Le plan post-fusion a été exécuté par lots. Les chantiers codables ont été implémentés, testés, poussés dans des pull requests dédiées, puis fusionnés dans `main`. La CI GitHub finale a exécuté les jobs backend PostgreSQL, frontend et sécurité des images avec succès. Le run main `32865071807` a validé **1 487 tests backend**, une couverture totale de **88,92 %** contre un seuil de **85,50 %**, ainsi que les artefacts de couverture et de scans d’images.

Cette clôture concerne le **code, les contrats, les tests et les validations CI disponibles**. Elle ne transforme pas les recettes dépendantes d’un VPS, de secrets réels, de comptes fournisseurs, d’un corpus documentaire autorisé ou d’une validation métier/juridique en preuves qui n’ont pas été exécutées.

## Lots livrés et fusionnés

| PR | Commit de fusion observé | Lot | Contenu principal | Preuve |
|---:|---|---|---|---|
| #51 | `60eff13` | MFA/TOTP | Facteur TOTP chiffré Fernet, enrôlement/confirmation/step-up/désactivation, anti-rejeu, recovery codes hashés, CSRF, rate limits, audit, migration `0062`, configuration production explicite | CI PR et run main `32856034458` verts |
| #52 | `a4467b0` | CreateCase | Formulaire cockpit, contrats TypeScript, client API, génération d’identifiants idempotents, navigation et tests Vitest | PR validée avant fusion ; le run push main associé a été annulé mais la validation PR a été exécutée |
| #53 | `614406f` | outbox/cockpit_projection | Contrat fermé de payload, isolation tenant, leases, retry borné, états `FAILED`/`NOT_CONFIGURED`, métriques Prometheus à cardinalité bornée, service Compose profilé | Run main `32860218599` vert |
| #54 | `e9ece0d` | sécurité des imports pricing | Contrôle libmagic, scan ClamAV `INSTREAM` sur réseau privé, refus signature/malware/indisponibilité scanner, injection production | Run main `32861846821` vert |
| #55 | `6149f76` | BOAMP→Case | Conversion seulement après qualification humaine `QUALIFIED`, filtrage tenant, capability `CASE_CREATE`, idempotence dispatcher et maintien du DCE comme étape obligatoire | Run main `32863425564` vert |
| #56 | `26ae18f` | Golden Corpus et documents BTP | Manifeste fermé, validateur CLI, cross-match de documents enterprise, enveloppes DC1/DC2/DC4 non contractuelles | Run main `32865071807` vert |
| #57 | `7cdb4af` | documentation opérationnelle | Réconciliation de `todo.md`, preuves CI et séparation des recettes externes | CI PR verte |

## Validation locale finale

La suite backend hors base de données a produit **1 022 tests passés** et **465 tests DB désélectionnés**. Les avertissements restants sont ceux de dépendances de test déjà signalés par l’environnement, notamment la dépréciation de l’intégration `httpx` de Starlette ; ils n’ont pas provoqué d’échec.

La suite frontend a produit **24 fichiers de tests passés et 103 tests passés**. Les étapes `typecheck`, `lint`, `vitest` et `vite build` sont vertes. Le build a généré les artefacts frontend attendus.

Le contrôle isolé de mypy sur les modules récemment modifiés est vert. Une exécution mypy globale historique du dépôt continue de signaler des erreurs dans des zones non couvertes par le sous-ensemble CI ; ces diagnostics ne correspondent pas aux fichiers ajoutés dans les lots post-fusion. Le job CI officiel, qui applique le périmètre de type-check du dépôt, est vert.

## Validation CI finale

Le run [GitHub Actions 32865071807](https://github.com/mailtkarim-bot/SMART_AO_V8/actions/runs/32865071807) est vert. Son job backend a exécuté les migrations et tests PostgreSQL dans les conteneurs de CI, puis a produit le résumé suivant :

| Contrôle | Résultat |
|---|---:|
| Tests backend | 1 487 passés |
| Couverture totale | 88,92 % |
| Seuil requis | 85,50 % |
| Job backend | Succès |
| Job frontend | Succès |
| Job image-security | Succès |
| Artefact couverture | [Disponible dans le run](https://github.com/mailtkarim-bot/SMART_AO_V8/actions/runs/32865071807/artifacts/9570107091) |

Les scans Trivy et le scan de secrets CI sont donc passés sur l’état final fusionné. Après la fusion de la documentation dans `7cdb4af`, le run post-fusion [32867442866](https://github.com/mailtkarim-bot/SMART_AO_V8/actions/runs/32867442866) a également terminé avec succès sur les trois jobs. Une annotation GitHub signale seulement la dépréciation future de certaines actions ciblant Node.js 20 et de CodeQL v3 ; ce ne sont pas des échecs de sécurité ou de fonctionnalité du dépôt.

## Ce que le code garantit désormais

Le parcours MFA est borné et auditable. La clé Fernet est exigée lorsque MFA est activé en production ; aucune clé exploitable n’est ajoutée au dépôt. Les opérations sensibles demandent une session et une protection CSRF cohérentes avec l’authentification navigateur, tandis que les vérifications TOTP sont limitées par débit et protégées contre le rejeu.

Le parcours CreateCase est disponible dans le cockpit et conserve les identifiants de commande et d’idempotence. La conversion BOAMP ne contourne pas la qualification humaine : une observation non qualifiée ou qualifiée avec une décision autre que `QUALIFIED` est refusée. Les données reprises dans la Case sont des métadonnées publiques, et le texte généré rappelle que le DCE doit encore être reçu et contrôlé.

Les imports pricing ne se fient plus seulement à l’extension ou au `Content-Type` HTTP. Le code vérifie la signature libmagic, les limites XLSX existantes et un verdict ClamAV privé. Une panne du scanner ne devient pas un succès silencieux.

Le worker cockpit_projection possède un contrat fermé et des états opérationnels observables. Sans adaptateur de projection durable configuré, il expose ou persiste l’état `NOT_CONFIGURED` plutôt que de déclarer une publication fictive. Les métriques excluent les identifiants tenant et métier afin de garder une cardinalité bornée.

Le manifeste Golden Corpus et les enveloppes DC1/DC2/DC4 sont volontairement non contractuels. Le générateur ne déduit pas une conformité juridique à partir de données manquantes ; il produit des blocages et des placeholders explicites.

## Validations qui restent externes

| Validation | État réel | Préparation livrée |
|---|---|---|
| ClamAV/EICAR sur VPS ou préproduction | À exécuter | Adaptateur TCP privé, timeout, verdicts et test de comportement ; aucune fausse preuve EICAR |
| HTTPS public, Caddy et certificats réels | À exécuter | Configuration et redaction durcies ; recette DNS/certificat/réseau non exécutée |
| Backup/restauration hors hôte | À exécuter | Scripts et contrats renforcés ; pas de restauration opérée sur un stockage externe |
| S3, SMTP, bus, signature et comptes fournisseurs | À exécuter | Contrats, états `NOT_CONFIGURED`, workers et erreurs fail-closed ; secrets réels absents |
| Golden Corpus DCE réel | À fournir puis exécuter | `ops/golden-corpus/manifest.example.json`, validateur et runbook ; le manifeste exemple contient zéro document |
| Métriques OCR/précision/rappel | À exécuter | Harness structurel ; aucune métrique inventée |
| Profilage N+1 submission/préparation | À exécuter | À mesurer sous PostgreSQL de préproduction avant optimisation ciblée |
| Validation finale DC1/DC2/DC4 et droits métier | À exécuter | Enveloppes déterministes non contractuelles et cross-match contrôlé |
| Clé MFA de production | À injecter hors Git | Flag et exigence de clé documentés dans `.env.example` et `ops/.env.preprod.example` |

## Commandes de reprise

```bash
gh repo clone mailtkarim-bot/SMART_AO_V8
cd SMART_AO_V8
git switch main
git pull --ff-only origin main
```

Pour valider le manifeste structurel :

```bash
cd backend
uv run python -m app.platform.quality.golden_corpus ../ops/golden-corpus/manifest.example.json
```

Pour relancer les contrôles frontend :

```bash
cd web
pnpm typecheck
pnpm lint
pnpm test -- --run
pnpm build
```

Pour la recette ClamAV réelle, utiliser exclusivement un environnement préproduction contrôlé avec le service ClamAV privé du Compose, injecter les variables depuis un gestionnaire de secrets, exécuter un fichier EICAR de test autorisé, puis vérifier à la fois le rejet HTTP, l’audit et l’absence de création de batch pricing. Cette commande opérée n’a pas été exécutée dans le sandbox courant.

## Références GitHub

- [1] [Dépôt SMART_AO_V8](https://github.com/mailtkarim-bot/SMART_AO_V8)
- [2] [Run CI final main 32865071807](https://github.com/mailtkarim-bot/SMART_AO_V8/actions/runs/32865071807)
- [3] [Artefact couverture final](https://github.com/mailtkarim-bot/SMART_AO_V8/actions/runs/32865071807/artifacts/9570107091)
- [4] [PR #51 — MFA/TOTP](https://github.com/mailtkarim-bot/SMART_AO_V8/pull/51)
- [5] [PR #52 — CreateCase](https://github.com/mailtkarim-bot/SMART_AO_V8/pull/52)
- [6] [PR #53 — cockpit_projection](https://github.com/mailtkarim-bot/SMART_AO_V8/pull/53)
- [7] [PR #54 — ClamAV/libmagic pricing](https://github.com/mailtkarim-bot/SMART_AO_V8/pull/54)
- [8] [PR #55 — BOAMP→Case](https://github.com/mailtkarim-bot/SMART_AO_V8/pull/55)
- [9] [PR #56 — Golden Corpus/BTP](https://github.com/mailtkarim-bot/SMART_AO_V8/pull/56)
- [10] [PR #57 — réconciliation todo](https://github.com/mailtkarim-bot/SMART_AO_V8/pull/57)
