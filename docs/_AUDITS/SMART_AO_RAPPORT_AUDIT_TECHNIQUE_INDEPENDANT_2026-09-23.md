# SMART AO — RAPPORT D’AUDIT TECHNIQUE INDÉPENDANT

**Projet :** SMART AO  
**Dépôt audité :** `mailtkarim-bot/SMART_AO_LAST`  
**Branche :** `main`  
**Commit de référence :** `374510a033e786884cc5ac0f0c322a12e0b6fc5e`  
**Date de l’audit :** 23 septembre 2026  
**Nature :** audit indépendant READ-ONLY / AUDIT FIRST  
**Périmètre :** architecture, sécurité, dépendances, CI/CD, conteneurisation, isolation tenant, autorisation, MFA, persistance, outbox, soumission, DPGF, exploitation et cohérence avec le Product Freeze.

---

# 1. Objet du rapport

Le présent rapport vise à établir l’état technique réel de SMART AO au commit :

`374510a033e786884cc5ac0f0c322a12e0b6fc5e`

L’objectif n’est pas de produire un jugement général fondé sur une note abstraite, mais d’identifier :

- les défauts effectivement vérifiés ;
- les risques probables restant à démontrer ;
- les limitations assumées par le Product Freeze ;
- les recommandations à accepter ou à rejeter ;
- les corrections minimales nécessaires avant qualification de release ;
- les éléments restant à tester avant déploiement pilote ou production publique.

L’ordre d’autorité documentaire déclaré par le projet est :

1. code et tests effectivement exécutés ;
2. Product Freeze v1.0 ;
3. contrats approuvés ;
4. checklist globale ;
5. mémoire auxiliaire.

**Référence :** `docs/README_DOCUMENTATION.md`

---

# 2. Périmètre et limitations de l’audit

## 2.1 Périmètre vérifié

L’audit a notamment couvert :

- le commit exact actuellement présent sur `main` ;
- les GitHub Actions correspondant à ce commit ;
- `pyproject.toml` ;
- le Dockerfile backend ;
- le `docker-compose.preprod.yml` ;
- la composition root FastAPI ;
- la configuration production ;
- l’autorisation et le contexte acteur ;
- le rate limiting ;
- l’import pricing/DPGF ;
- le stockage des `domain_events` et de l’outbox ;
- le worker de rétention DCE ;
- la soumission et l’export ;
- le Product Freeze actif ;
- le contrat Alembic ;
- les frontières entre bounded contexts.

## 2.2 Limitation d’exécution locale

Le clonage direct du dépôt dans l’environnement d’audit a été empêché par une défaillance de résolution réseau/DNS de l’environnement d’exécution.

En conséquence :

### VÉRIFIÉ

- accès au dépôt via le connecteur GitHub ;
- inspection du code source au SHA exact ;
- inspection des GitHub Actions du SHA exact ;
- observation du build Docker exécuté par GitHub Actions.

### NON REPRODUIT INDÉPENDAMMENT

- installation locale complète dans le sandbox de l’auditeur ;
- exécution indépendante des 1 720 tests annoncés par le rapport précédent ;
- cycle Alembic complet `base → head → downgrade → head`.

Aucune affirmation d’installation locale réussie n’est donc faite dans ce rapport.

---

# 3. Verdict exécutif

## 3.1 Verdict

**Statut actuel : NO-GO RELEASE / GO CORRECTION CIBLÉE.**

Le projet ne nécessite pas une refonte générale.

L’architecture possède déjà plusieurs fondations robustes :

- tenant isolation explicite ;
- contrôle d’autorisation centralisé ;
- données financières Patron-only ;
- MFA / step-up ;
- portée Collaborateur contrôlée ;
- idempotence ;
- command receipts ;
- événements de domaine ;
- outbox ;
- preuves, hash et provenance ;
- décision et dépôt conservés sous autorité humaine ;
- Product Freeze clair ;
- CI structurée ;
- dépendances et images partiellement verrouillées.

En revanche, le commit actuel ne doit pas être qualifié de release prête, principalement pour trois raisons :

1. défaut vérifié de construction Docker lorsque plusieurs extras sont activés ;
2. dépendances vulnérables présentes dans la résolution actuelle ;
3. CI du HEAD actuellement rouge.

---

# 4. Synthèse des findings

| ID | Finding | Statut | Priorité | Verdict |
|---|---|---|---|---|
| BUILD-01 | Les extras Docker se désinstallent mutuellement | VÉRIFIÉ | P0 | Bloquant |
| SEC-DEP-01 | Résolution actuelle contenant des dépendances vulnérables | VÉRIFIÉ | P0 | Bloquant |
| CI-01 | CI du HEAD actuellement en échec | VÉRIFIÉ | P0 release gate | Bloquant |
| API-ERR-01 | Absence de handler global FastAPI | VÉRIFIÉ | P1 | À corriger |
| ARCH-BC-01 | Couplage application → ORM de bounded contexts étrangers | VÉRIFIÉ qualitativement | P1 | À résorber progressivement |
| OPS-OUTBOX-01 | Pas de politique explicite de rétention des outbox terminales | VÉRIFIÉ / conception requise | P1 | À concevoir |
| PRICING-01 | Import DPGF classé systématiquement en `SALES` | VÉRIFIÉ | P2 métier | Limitation fonctionnelle |
| SEC-RATE-01 | Rate limiter process-local | VÉRIFIÉ | P2 actuellement | Acceptable dans la topologie actuelle |
| FE-ROUTER-01 | Pas de routeur frontend structurant standard | VÉRIFIÉ | P2 | Non bloquant pilote |
| OPS-VPS-01 | VPS réel / restauration réelle non qualifiés | VÉRIFIÉ | P0 production publique | Bloquant avant commercialisation publique |
| PROD-SUBMIT-01 | Absence de dépôt automatique | NON-DÉFAUT | — | Conforme au Product Freeze |
| DATA-PURGE-01 | Purger indistinctement `domain_events` | RECOMMANDATION REJETÉE | — | Incompatible avec les invariants actuels |

---

# 5. Finding BUILD-01 — Défaut critique de construction Docker

## Statut

**VÉRIFIÉ.**

## Gravité

**P0 avant pilote utilisant plusieurs extras simultanément.**

## Description

Le Dockerfile backend réalise plusieurs synchronisations successives :

- base ;
- `rag` ;
- `document-advanced` ;
- `object-storage` ;
- `connectors` ;
- `notifications` ;
- `calendar`.

**Référence :** `ops/docker/backend.Dockerfile`

Le problème est structurel : `uv sync` fonctionne avec une synchronisation exacte de la sélection demandée.

Les extras installés lors d’une étape précédente peuvent donc être retirés par l’étape suivante.

Ce comportement n’est pas seulement théorique.

Les logs GitHub Actions du build actuel montrent effectivement :

- installation des dépendances RAG ;
- installation de Docling et dépendances avancées ;
- puis désinstallation massive de ces dépendances lors de l’installation de `object-storage` ;
- puis retraits supplémentaires lors de `connectors`, `notifications` et `calendar`.

Parmi les paquets retirés figurent notamment des composants liés à :

- `docling` ;
- `torch` ;
- `transformers` ;
- `sentence-transformers` ;
- les dépendances CUDA installées transitivement.

## Impact

Une image construite avec plusieurs capacités activées peut :

- réussir son `docker build` ;
- être publiée ;
- démarrer ;
- mais ne plus posséder toutes les capacités demandées.

C’est un défaut dangereux car il peut être silencieux.

La CI construit précisément une image avec plusieurs extras simultanément.

**Référence :** `.github/workflows/ci.yml`

Le build réussi ne constitue donc pas une preuve de présence fonctionnelle de chacun des extras.

## Correction proposée

Construire la liste d’extras désirés puis exécuter **une seule synchronisation exacte** avec l’ensemble de ces extras.

Éviter une correction superficielle consistant uniquement à passer en mode non exact sans justification.

## Tests de régression exigés

L’image “all capabilities” devra au minimum vérifier :

- import `sentence_transformers` ;
- import Docling ;
- import boto3 ;
- import httpx ;
- import aiosmtplib ;
- import icalendar ;
- import des dépendances OCR lorsque l’extra OCR est demandé ;
- `uv pip check` ;
- démarrage application ;
- démarrage des workers concernés.

---

# 6. Finding SEC-DEP-01 — Vulnérabilités de dépendances

## Statut

**VÉRIFIÉ.**

## Gravité

**P0 release gate.**

## pypdf

Le `pyproject.toml` déclare :

`pypdf>=6.16.0`

et non une version strictement égale à `6.16.0`.

**Référence :** `pyproject.toml`

Cependant, le lock actuellement utilisé résout effectivement :

`pypdf==6.16.0`

La distinction est importante :

- la déclaration autorise une version corrigée ;
- le lock actuel installe une version vulnérable.

SMART AO traite des documents DCE externes et potentiellement hostiles. Une vulnérabilité de consommation excessive de ressources ou de parsing PDF doit donc être considérée dans le threat model produit.

## accelerate

Le graphe de dépendances des extras installe également une version d’`accelerate` signalée par les outils de sécurité de la CI.

## CI

La CI exécute :

1. Ruff ;
2. format ;
3. mypy ;
4. contrôle whitespace ;
5. détection de secrets ;
6. `pip-audit` ;
7. Bandit ;
8. pytest + couverture.

**Référence :** `.github/workflows/ci.yml`

Au HEAD actuel, `pip-audit` échoue.

Les étapes placées après ne constituent donc plus une preuve GitHub complète pour ce SHA.

## Correction proposée

Ne pas modifier seulement la borne de `pyproject.toml`.

Procédure :

1. mettre à jour la résolution ;
2. régénérer `uv.lock` ;
3. vérifier les changements transitifs ;
4. exécuter tests extraction PDF ;
5. ajouter des fixtures adversariales de régression ;
6. exécuter `pip-audit` ;
7. exécuter Bandit ;
8. reconstruire l’image ;
9. exécuter Trivy ;
10. exécuter tous les tests backend.

---

# 7. Finding CI-01 — HEAD non qualifié par CI

## Statut

**VÉRIFIÉ.**

Le workflow CI correspondant au commit de référence est terminé avec :

`conclusion: failure`

## Conséquence

Le commit actuel ne peut pas être désigné comme :

- “CI green” ;
- “qualified build” ;
- “release candidate validée”.

Cela ne signifie pas que le code métier est globalement incorrect.

Cela signifie uniquement que le **SHA actuel ne dispose pas d’une preuve CI complète verte**.

## Proposition

Séparer à terme les gates :

- lint/type/SAST ;
- tests backend ;
- dependency audit ;
- image security ;
- frontend.

Une vulnérabilité doit conserver la CI rouge, mais elle ne devrait pas empêcher l’obtention simultanée d’une preuve sur les tests métier.

---

# 8. Finding API-ERR-01 — Contrat global d’erreurs FastAPI incomplet

## Statut

**VÉRIFIÉ au niveau de la composition root.**

La composition root crée l’instance FastAPI, mais aucun handler global d’exception n’est déclaré dans ce fichier.

**Référence :** `backend/app/bootstrap/application.py`

## Risques

Sans frontière globale cohérente :

- comportement différent entre routes ;
- fuites de détails techniques possibles ;
- format d’erreur instable ;
- mauvaise propagation de certaines erreurs internes ;
- observabilité hétérogène.

## Correction proposée

Créer une frontière d’erreurs globale minimale.

Elle devra gérer explicitement :

- refus d’autorisation ;
- ressource inexistante / anti-enumeration ;
- version conflict ;
- validation ;
- erreur application déterministe ;
- indisponibilité temporaire ;
- exception imprévue.

Le fallback inattendu doit :

- répondre en 500 sûr ;
- ne jamais sérialiser une stack trace ;
- ne jamais exposer de secret ;
- conserver un correlation ID ;
- produire un log structuré serveur.

## Tests

Tests obligatoires :

- 401/403/404 ;
- conflit de version ;
- tenant étranger ;
- exception non prévue ;
- absence de traceback ;
- absence de secret ;
- structure JSON stable ;
- correlation ID.

---

# 9. Finding ARCH-BC-01 — Couplage inter-bounded-context

## Statut

**VÉRIFIÉ qualitativement.**

La couche application du module `submission` importe directement des records ORM appartenant notamment à :

- `case` ;
- `enterprise` ;
- `preparation` ;
- `pricing`.

**Référence :** `backend/app/modules/submission/application/service.py`

Le chiffre exact de dépendances inter-modules annoncé dans un audit précédent n’a pas été reproduit exhaustivement dans cette passe.

Il ne doit donc pas être considéré comme vérifié ici.

## Risque

Ce couplage :

- fragilise les bounded contexts ;
- accroît le rayon d’impact d’une migration ;
- facilite les dépendances circulaires ;
- rend les tests plus coûteux ;
- mêle lecture métier et persistance étrangère.

## Correction

Pas de rewrite.

Introduire progressivement :

- Readers ;
- Ports ;
- DTO/projections ;
- contrats applicatifs stables.

Priorité aux modules les plus centraux :

1. submission ;
2. decision ;
3. preparation ;
4. pricing.

Chaque suppression d’import ORM inter-module devra être accompagnée d’un test d’architecture.

---

# 10. Finding OPS-OUTBOX-01 — Rétention de l’outbox

## Statut

**VÉRIFIÉ comme besoin d’exploitation.**

`DomainEventRecord` et `OutboxMessageRecord` sont deux objets distincts.

L’outbox référence le domaine event avec une FK tenant-scoped et `RESTRICT`.

**Référence :** `backend/app/platform/persistence/models.py`

Le worker de rétention DCE traite son sujet fonctionnel mais ne constitue pas une politique globale de rétention de l’outbox.

**Référence :** `backend/app/workers/dce_retention.py`

## Point important

Il serait incorrect de transformer ce finding en :

> “supprimer périodiquement les domain events”.

SMART AO utilise les événements, les preuves, les versions et l’historique comme éléments de traçabilité.

Une purge générique des `domain_events` serait incompatible avec cette doctrine.

## Proposition

Séparer deux politiques :

### Outbox technique

Les états terminaux :

- `PUBLISHED` ;
- `FAILED` ;
- `NOT_CONFIGURED`

peuvent faire l’objet d’une stratégie de :

- rétention limitée ;
- archivage ;
- métriques ;
- purge contrôlée après délai.

### Domain events

Conserver les invariants :

- append-only ;
- provenance ;
- audit ;
- causation ;
- correlation.

Si le volume devient problématique :

- partitionnement PostgreSQL ;
- archivage immutable ;
- cold storage ;
- politique de conservation contractualisée.

---

# 11. Finding PRICING-01 — Classification DPGF trop simplifiée

## Statut

**VÉRIFIÉ.**

Le handler de commit pricing crée les lignes avec :

`category="SALES"`

et augmente `sales_total_minor`.

**Référence :** `backend/app/modules/pricing/application/import_handler.py`

## Conséquence

Le système ne différencie actuellement pas automatiquement :

- matériaux ;
- main-d’œuvre ;
- engins ;
- sous-traitance ;
- fournitures ;
- frais généraux ;
- autres catégories métier.

## Gravité

P2 métier.

Ce comportement ne compromet pas directement la sécurité du logiciel mais limite la richesse de l’analyse économique.

## Recommandation

Ne pas demander au LLM d’inventer une catégorie.

Construire un mapper déterministe capable de retourner notamment :

- catégorie vérifiée ;
- `UNKNOWN` ;
- `REVIEW_REQUIRED`.

Chaque classification devra conserver :

- source ;
- ligne ;
- colonne ;
- version du fichier ;
- règle ou méthode utilisée.

---

# 12. Finding SEC-RATE-01 — Rate limiter local au processus

## Statut

**VÉRIFIÉ.**

Le code indique explicitement que le rate limiter est process-local.

**Référence :** `backend/app/platform/security/rate_limit.py`

## Reclassement

Ce point n’est pas considéré comme P0 dans la topologie actuelle.

Le Dockerfile exécute Uvicorn sans option multi-worker.

**Référence :** `ops/docker/backend.Dockerfile`

Le déploiement actuel correspond donc à un processus API par conteneur.

Avec le modèle de déploiement “un VPS dédié par entreprise”, ce comportement peut être accepté tant que :

- une seule instance backend authentifie les utilisateurs ;
- aucun load balancing multi-réplique n’est mis en place.

## Condition de réouverture

Le finding devient P1/P0 sécurité avant :

- `uvicorn --workers > 1` ;
- plusieurs conteneurs backend ;
- Kubernetes ;
- autoscaling ;
- load balancer multi-réplique.

À ce moment, un store distribué ou une autre solution partagée sera nécessaire.

---

# 13. Vérification des invariants d’autorisation

La policy centrale présente une conception globalement robuste.

Elle vérifie notamment :

- égalité de `tenant_id` ;
- membership actif ;
- présence de capability ;
- restrictions des classifications sensibles ;
- `FINANCIAL_PRIVATE` réservé au `PATRON_ADMIN` ;
- scope de Case obligatoire pour Collaborateur ;
- allowed actions ;
- allowed classifications ;
- délégation bornée ;
- MFA récent lorsque requis.

**Référence :** `backend/app/platform/security/authorization.py`

Le `ActorContext` conserve des faits serveur immuables portant notamment :

- identité ;
- tenant ;
- membership ;
- actor kind ;
- session ;
- MFA ;
- assignment scopes ;
- delegated cases ;
- correlation ID.

La fenêtre de step-up MFA par défaut est de quinze minutes.

**Référence :** `backend/app/platform/security/context.py`

## Verdict

**VÉRIFIÉ : la policy centrale respecte les invariants attendus.**

En revanche, l’expression :

> “hermétisme financier absolu”

serait prématurée sans audit exhaustif de toutes les routes, readers et services.

Le statut correct est :

**SOCLE D’AUTORISATION ROBUSTE — CONTOURNEMENTS À AUDITER EXHAUSTIVEMENT.**

---

# 14. Soumission et autorité humaine

Le module de soumission est cohérent avec le Product Freeze.

Le service gère un package prêt pour une soumission humaine et vérifie notamment :

- Patron ;
- MFA ;
- hash du manifeste ;
- decision gate ;
- autorisation portant sur la version exacte du package.

Le contrat indique explicitement :

`external_submission = "NOT_PERFORMED"`.

**Référence :** `backend/app/modules/submission/application/service.py`

Le Product Freeze définit lui-même :

`export local → dépôt humain externe → preuve de réception PARTIAL ou UNKNOWN`

et classe les connecteurs automatisés de portail en V1.x ou ultérieur.

**Référence :** `docs/00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md`

## Conclusion

L’absence de dépôt automatique n’est **pas** un défaut du V1 actuel.

L’implémenter comme simple “correction” serait une violation de la source d’autorité produit.

Toute automatisation du dépôt doit passer par :

- une évolution Product Freeze ;
- une analyse sécurité ;
- une analyse juridique ;
- une conception d’idempotence ;
- une gestion des résultats `UNKNOWN/PARTIAL` ;
- une preuve de réception ;
- une autorité humaine explicite.

---

# 15. Données, preuves et événements

Le modèle actuel conserve correctement plusieurs éléments nécessaires à l’explicabilité :

- aggregate type ;
- aggregate ID ;
- revision ;
- event type ;
- payload version ;
- actor ;
- command ;
- correlation ;
- causation ;
- timestamp.

**Référence :** `backend/app/platform/persistence/models.py`

Cette orientation est cohérente avec les principes SmartAO :

- source ;
- version ;
- locator ;
- hash ;
- append-only ;
- preuves ;
- auditabilité ;
- réversibilité des conclusions sans suppression de l’histoire.

Elle doit être préservée.

---

# 16. Migrations et contrat de schéma

Le runtime déclare :

`EXPECTED_ALEMBIC_HEAD = "20260920_0090"`

**Référence :** `backend/app/platform/persistence/schema.py`

C’est une bonne pratique : le runtime possède une référence explicite au head de migration attendu.

## Statut

**CONTRAT VÉRIFIÉ DANS LE CODE.**

Le cycle complet de migration n’a pas été reproduit indépendamment pendant cette passe.

Avant qualification production, exécuter sur PostgreSQL réel :

1. base vierge ;
2. upgrade head ;
3. smoke tests ;
4. downgrade contrôlé lorsque supporté ;
5. nouvel upgrade ;
6. validation contraintes/index/FK ;
7. test backup/restauration.

---

# 17. Product Freeze et doctrine IA

Le Product Freeze actif définit correctement que :

- l’IA n’est pas une autorité autonome ;
- elle peut extraire, classer, rechercher et proposer ;
- elle ne décide pas seule ;
- elle ne dépose pas ;
- elle ne modifie pas l’historique ;
- les contenus hostiles ne sont pas transformés en instructions ;
- les conclusions importantes doivent conserver leur source/version/hash/locator.

**Référence :** `docs/00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md`

Ce contrat doit rester invariant lors des futures intégrations LLM/RAG.

---

# 18. Ce que l’audit précédent avait correctement identifié

Plusieurs observations du précédent audit sont confirmées :

- vulnérabilités dépendances ;
- absence de handler global FastAPI ;
- couplage inter-modules ;
- rate limiter process-local ;
- simplification DPGF ;
- nécessité d’une politique d’exploitation de l’outbox ;
- absence actuelle de qualification VPS réelle.

Son rapport était donc techniquement utile.

---

# 19. Points à corriger par rapport à l’audit précédent

## 19.1 Bug Docker non identifié

Le défaut de synchronisation successive des extras n’avait pas été relevé.

Il constitue pourtant un finding critique car l’image peut perdre silencieusement les fonctionnalités qu’elle prétend embarquer.

## 19.2 Dépôt automatique

Le considérer comme un manque du V1 est incorrect.

Le Product Freeze exige actuellement un dépôt humain externe.

## 19.3 Purge des domain events

La croissance des tables doit être traitée, mais une purge indistincte des événements de domaine est incompatible avec la doctrine actuelle de provenance et d’historique.

## 19.4 Rate limiting

Le risque multi-réplique est réel, mais sa gravité doit être alignée sur la topologie actuelle.

Dans le déploiement mono-processus actuel, il ne justifie pas l’introduction immédiate d’un Redis uniquement pour ce besoin.

---

# 20. Plan de correction recommandé

## Lot P0-A — Build et supply chain

### BUILD-01

Réparer la sélection des extras Docker.

### SEC-DEP-01

Mettre à jour le lock et supprimer les vulnérabilités connues.

### CI-01

Obtenir une CI entièrement verte sur un nouveau SHA.

### Critères d’acceptation

- image multi-extras réellement fonctionnelle ;
- `uv pip check` vert ;
- `pip-audit` vert ;
- Trivy sans HIGH/CRITICAL corrigibles ;
- Bandit vert ;
- tests backend verts ;
- tests frontend verts ;
- couverture ≥ seuil contractuel ;
- aucun secret détecté.

---

# 21. Lot P1 — Fiabilité et architecture

## API-ERR-01

Ajouter un mapping global et sûr des erreurs.

## ARCH-BC-01

Réduire progressivement les imports ORM inter-bounded-context.

## OPS-OUTBOX-01

Définir une stratégie de rétention technique de l’outbox sans détruire la provenance métier.

## Critères d’acceptation

- erreurs structurées ;
- correlation ID ;
- absence de fuite ;
- tests anti-enumeration ;
- tests tenant ;
- tests architecture ;
- mesure du volume outbox ;
- documentation de la politique de conservation.

---

# 22. Lot P2 — Produit et évolutivité

## PRICING-01

Introduire une taxonomie DPGF plus riche avec `UNKNOWN/REVIEW_REQUIRED`.

## SEC-RATE-01

Préparer une stratégie partagée uniquement lors du passage à plusieurs workers/réplicas.

## FE-ROUTER-01

Introduire un routeur frontend lorsque le nombre de surfaces et parcours justifie son coût.

---

# 23. Qualification VPS avant production publique

Avant commercialisation publique, une qualification sur VPS réel en France doit démontrer :

- installation depuis zéro ;
- migration base ;
- démarrage ;
- TLS ;
- Caddy ;
- PostgreSQL ;
- ClamAV ;
- volumes ;
- backup ;
- restauration ;
- rotation secrets ;
- redémarrage ;
- saturation disque ;
- arrêt PostgreSQL ;
- indisponibilité réseau ;
- rollback ;
- monitoring ;
- journaux ;
- absence de secrets dans les logs ;
- reprise workers/outbox ;
- comportement DCE corrompu ou hostile ;
- scénarios MFA ;
- tenant isolation ;
- récupération.

Tant que cette qualification n’existe pas :

**NO-GO production publique.**

Cela ne signifie pas NO-GO développement ou préproduction.

---

# 24. Ordre impératif recommandé à Codex

1. Auditer le Dockerfile et ajouter un test de reproduction de BUILD-01.
2. Corriger BUILD-01 avec le plus petit changement possible.
3. Mettre à jour les dépendances vulnérables et le lock.
4. Exécuter la totalité des tests.
5. Refaire `pip-audit`, Bandit et Trivy.
6. Obtenir une CI verte.
7. Ajouter le handler global d’erreurs.
8. Écrire ses tests de refus et de non-fuite.
9. Concevoir la politique outbox.
10. Traiter progressivement les frontières ORM.
11. Reporter les évolutions DPGF et frontend hors du gate P0.
12. Ne pas automatiser le dépôt externe sans nouvelle décision Product Freeze.

---

# 25. Rollback

Toutes les corrections P0 doivent rester :

- atomiques ;
- réversibles ;
- limitées au problème traité.

Pour les dépendances :

- conserver l’ancien `uv.lock` dans l’historique Git ;
- ne pas mélanger refactoring et upgrade dépendances.

Pour Docker :

- une modification du mécanisme d’extras uniquement ;
- pas de restructuration globale de la chaîne de build au même commit.

Pour les erreurs FastAPI :

- introduire la frontière globale sans changer les contrats métier internes.

---

# 26. Verdict final

SMART AO n’est pas dans un état nécessitant une reconstruction générale.

Le socle présente déjà plusieurs caractéristiques compatibles avec un logiciel professionnel :

- architecture modulaire ;
- PostgreSQL et migrations explicites ;
- idempotence ;
- commandes durables ;
- outbox ;
- événements de domaine ;
- isolation tenant ;
- permissions et ReBAC ;
- données financières protégées ;
- MFA et step-up ;
- provenance ;
- décision humaine ;
- dépôt humain ;
- états `UNKNOWN/PARTIAL` ;
- documentation gouvernée.

Le problème principal du commit actuel est plus précis :

**la preuve de release n’est pas fiable tant que le build Docker multi-extras est incorrect, que les vulnérabilités de dépendances persistent et que la CI du SHA n’est pas entièrement verte.**

Le plan recommandé est donc :

**CORRIGER → TESTER → REQUALIFIER → DÉPLOYER EN PRÉPRODUCTION → QUALIFIER LE VPS RÉEL.**

Pas de rewrite.

Pas de nouvelle infrastructure inutile.

Pas d’automatisation de dépôt hors Product Freeze.

Pas de purge aveugle des preuves.

Pas de classification métier inventée par l’IA.

Chaque bug corrigé doit produire son test de régression, et chaque nouvelle preuve de qualification doit être attachée au SHA exact concerné.

---

# 27. Statut de sortie

**Commit audité :** `374510a033e786884cc5ac0f0c322a12e0b6fc5e`

**Verdict développement :** GO  
**Verdict corrections ciblées :** GO  
**Verdict release du SHA actuel :** NO-GO  
**Verdict pilote après P0 + CI verte :** À REQUALIFIER  
**Verdict production publique :** NO-GO tant que le VPS réel, la restauration et les scénarios opérationnels ne sont pas qualifiés.

**Priorité immédiate : BUILD-01 → SEC-DEP-01 → CI-01.**

---

# 28. Références principales du dépôt

- `.github/workflows/ci.yml`
- `pyproject.toml`
- `uv.lock`
- `ops/docker/backend.Dockerfile`
- `ops/docker-compose.preprod.yml`
- `backend/app/bootstrap/application.py`
- `backend/app/bootstrap/production.py`
- `backend/app/platform/security/authorization.py`
- `backend/app/platform/security/context.py`
- `backend/app/platform/security/rate_limit.py`
- `backend/app/platform/persistence/models.py`
- `backend/app/platform/persistence/schema.py`
- `backend/app/workers/dce_retention.py`
- `backend/app/modules/pricing/application/import_handler.py`
- `backend/app/modules/submission/application/service.py`
- `docs/README_DOCUMENTATION.md`
- `docs/00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md`
