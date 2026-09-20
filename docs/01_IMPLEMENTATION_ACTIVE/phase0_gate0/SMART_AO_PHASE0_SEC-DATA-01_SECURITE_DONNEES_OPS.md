# SMART AO — SEC-DATA-01 — Sécurité, données, exploitation et support

**Date :** 12 septembre 2026  
**Référence :** `feat/ccap-cctp-risk-register-20260831@b6b05b8`  
**Statut :** AUDIT TERMINÉ — DOSSIERS PRÉ-PILOTE OUVERTS  
**Verdict :** contrôles applicatifs sérieux ; cycle de vie, flux fournisseurs et exploitation dédiée non démontrés

## 1. Position de gate

Les contrôles déjà présents justifient de poursuivre sur V8. Ils ne justifient pas un pilote avec données client réelles. Le pilote reste **NO-GO** jusqu'à preuve des dossiers SEC-OPS-01, DATA-OPS-01, DATA-FLOW-01, OPS-DEDICATED-01 et NFR-01 demandés par la v3.1.

## 2. Contrôles observés

| Domaine | Contrôle dans V8 | Qualification |
|---|---|---|
| autorisation | policy deny-by-default, tenant, membership active, capacités serveur | COUVERT EN CODE |
| portée Affaire | ReBAC et résolution côté serveur | COUVERT EN CODE |
| données financières | vues privées Patron et réponses bornées | PARTIEL, tests ciblés présents |
| authentification | JWT/rotation, cookies sécurisés, CSRF, Argon2id | COUVERT EN CODE |
| MFA | TOTP et step-up | COUVERT EN CODE |
| abus | rate limiting | COUVERT EN CODE |
| URL externes | politique HTTPS/anti-SSRF | COUVERT EN CODE |
| réponses sensibles | neutral 404, `no-cache`, headers sécurité | COUVERT EN CODE |
| audit | événements/acteurs avec minimisation prévue | PARTIEL |
| ingestion | quarantaine, taille/MIME/hash, ClamAV fail-closed | COUVERT EN CODE, LIVE BLOQUÉ |
| isolation | tenant dans les modèles + cible instance dédiée | PARTIEL, deux instances non testées |
| secrets | configuration par environnement | PARTIEL, rotation/manager non prouvés |
| sauvegarde | intention opératoire | ABSENT comme exercice de restauration |

## 3. Registre des risques prioritaires

| ID | Risque | Gravité | Preuve actuelle | Manque | Fermeture |
|---|---|---|---|---|---|
| SEC-01 | archive/PDF hostile sature ou contourne l'analyse | critique | limites et états fail-safe | banc Hostile réel, archives imbriquées, EICAR | A1 + SEC-OPS avant pilote |
| SEC-02 | prompt injection documentaire élargit outils/données | critique | doctrine documentaire, aucun runtime LLM | policy gate et test hostile bout-en-bout | avant IA sur données réelles |
| SEC-03 | fuite cross-tenant ou cross-rôle | critique | tenant/policies/ReBAC | tests d'isolation sur deux instances et exports/recherche | A0 puis pilote |
| SEC-04 | accès support depuis le Maroc non borné | critique | aucune procédure JIT complète | approbation, MFA, durée, moindre privilège, journal, contrat | avant pilote |
| SEC-05 | sauvegarde incomplète ou non restaurable | critique | aucune restauration observée | DB + documents + index + secrets, RPO/RTO | avant pilote |
| DATA-01 | suppression laisse embeddings, logs ou backups | élevée | rétention DCE partielle | catalogue et exécuteur de purge transversal | avant offboarding/pilote |
| DATA-02 | fournisseur traite hors région autorisée | critique | provider final non choisi | registre flux/région/DPA/SCC | avant premier flux réel |
| DATA-03 | DCE Golden sans droit ou insuffisamment anonymisé | critique | corpus externe seulement inventorié | ledger droits/anonymisation | A1 |
| DATA-04 | logs contiennent texte DCE, prix ou identité | élevée | minimisation partielle | schéma de logs et tests de redaction | avant pilote |
| OPS-01 | variante permanente par client | élevée | un code source, compose | pipeline multi-instance/digests/versions | avant 2e instance |
| OPS-02 | migration bloque/corrompt une base client | critique | Alembic offline | rehearsal base peuplée, sauveg/rollback | A0/A2–A4 |
| OPS-03 | worker one-shot n'est pas repris après crash | élevée | outbox/inbox partiels | supervision, claim/retry/poison | Gate A/post-A |
| OPS-04 | certificat, image ou OS obsolète | élevée | digests Caddy/Postgres/ClamAV | inventaire, patch SLA, scan images | avant pilote |
| OPS-05 | incident sans détection ni réponse | élevée | logs/healthchecks | alertes, runbook, notification, exercices | avant pilote |

## 4. Carte des données

| Catégorie | Exemples | Stockages observés | Sensibilité | Owner | Règle à prouver |
|---|---|---|---|---|---|
| identité | nom, email, rôle, MFA | PostgreSQL sécurité | personnel | Identity | minimisation, conservation, droits |
| entreprise | assurances, finance, références | PostgreSQL + documents | confidentiel à très sensible | Enterprise | validité, rôle, réemploi |
| DCE | pièces, plans, clauses, courriers | objets + DB + fragments | contractuel/confidentiel | DCE | droits, hash, rétention |
| prix | déboursés, marge, cashflow | PostgreSQL/exports | direction | Pricing | Patron-only et traces bornées |
| décision | motif, conditions, dérogation | PostgreSQL/audit | confidentiel | Decision | immutabilité/supersession |
| réponse | mémoires, cadres, pièces | stockage/DB/exports | confidentiel | Response | versions et destinataires |
| remise | manifeste, paquet, reçu | stockage/DB/logs externes | engageant | Submission | rapprochement/hash |
| dérivés | fragments, embeddings, résumés | PostgreSQL/index/logs | hérite de la source | contexte producteur | provenance + purge |
| opérations | logs, métriques, sauvegardes | hôte/backup | variable | Platform | redaction, accès, durée |

La sensibilité doit se propager aux fragments, index, caches, exports, prompts et traces. Une donnée interdite au rôle ne doit jamais entrer dans le contexte du modèle pour ce rôle.

## 5. Flux par frontière géographique et fournisseur

| Flux potentiel | Données | Destination/région | Base/contrat | État | Décision avant activation |
|---|---|---|---|---|---|
| navigateur ↔ VPS | sessions, DCE, décisions | à choisir France/EEE | contrat client | non déployé | hébergeur/région/TLS |
| VPS ↔ stockage objet | originaux/exports | provider non choisi | DPA | optionnel | chiffrement/région/rétention |
| VPS ↔ BOAMP | avis publics | France | source publique | adapter présent | quotas/fraîcheur |
| VPS ↔ TED | avis publics | UE | source publique | absent | second adapter |
| VPS ↔ INSEE | identité entreprise | France | conditions API | optionnel | champs/quotas/logs |
| VPS ↔ LLM | contexte DCE/Entreprise autorisé | provider non choisi | DPA/SCC éventuelles | absent | région, no-training, rétention, clés |
| VPS ↔ SMTP/webhook/signature | paquets/métadonnées | provider/client | contrat spécifique | code présent | canal, reçu, secret, retry |
| support Maroc ↔ Data Plane | métadonnées ou contenu selon incident | accès transfrontalier | autorisation/contrat | procédure absente | JIT, approbation, MFA, journal, écran/donnée bornés |
| backups | DB/objets/index | emplacement à choisir | DPA | non prouvé | région, chiffrement, restauration, destruction |

Un flux n'est autorisé que si les champs exacts, but, base, région, durée, sous-traitant, chiffrement et mécanisme de retrait sont enregistrés.

## 6. Procédure support cible minimale

1. ticket client identifie incident, Data Plane et données nécessaires ;
2. accès approuvé par une personne habilitée du client ou règle contractuelle d'urgence ;
3. identité support forte, MFA et appareil géré ;
4. jeton JIT limité à une instance, des actions et une durée ;
5. lecture privilégiée ; export/téléchargement interdits par défaut ;
6. session journalisée sans copier les secrets métier dans les logs ;
7. révocation automatique, compte rendu et revue ;
8. mécanisme d'accès exceptionnel testé et contractualisé, avec localisation documentée.

Aucun compte partagé ni accès permanent au parc client ne satisfait cette cible.

## 7. Cycle de vie et offboarding

Le dossier DATA-OPS-01 devra relier chaque catégorie à : création, duplication, dérivation, export, archivage, durée, legal hold, suppression, preuve de suppression et persistance en backup.

Un offboarding accepté démontre :

- export compréhensible de l'Affaire et des pièces ;
- liste de ce qui est inclus/exclu ;
- arrêt des flux et révocation des accès ;
- purge DB, objets, index, caches et files ;
- expiration/destruction des sauvegardes selon calendrier ;
- preuve finale sans exposer le contenu supprimé.

## 8. Exploitation d'instances dédiées

Avant la deuxième instance, OPS-DEDICATED-01 doit prouver :

- même code/image et configuration séparée ;
- inventaire instance → client → version → migrations ;
- secrets par instance ;
- déploiement progressif et rollback ;
- supervision, quotas et coûts par client ;
- sauvegarde/restauration isolée ;
- impossibilité de brancher une base ou un stockage d'un autre client ;
- aucun document métier dans un éventuel Control Plane.

## 9. NFR à mesurer

Phase 0 ne fixe pas de chiffres arbitraires. PR-A0/A1 doivent produire les distributions nécessaires pour décider :

- taille/nombre/profondeur d'archives ;
- temps et mémoire par format ;
- concurrence uploads/jobs/utilisateurs ;
- délai d'affichage d'un résultat partiel ;
- durée de migration et rollback ;
- RPO/RTO et durée de restauration ;
- coût stockage/extraction/IA par dossier ;
- disponibilité et fraîcheur des sources ;
- délai de révocation d'accès support/partage.

Les seules tolérances déjà normatives sont zéro fuite non autorisée, zéro échec silencieux critique et inventaire complet du jeu accepté.

## 10. Gates avant pilote réel

| Dossier | Sortie requise | Owner proposé |
|---|---|---|
| SEC-OPS-01 | threat model, banc hostile, scan images, incidents | Security Owner |
| DATA-OPS-01 | catalogue, rétention, export, purge et offboarding | DPO/Data Owner |
| DATA-FLOW-01 | flux/régions/providers/DPA/SCC/sous-traitants | DPO + juridique |
| OPS-DEDICATED-01 | provisioning, inventaire, upgrade, rollback | Ops Owner |
| NFR-01 | enveloppes mesurées et seuils acceptés | Product + Tech Owner |
| QUAL-01 | corpus gelé, droits et résultats | Quality Owner |
| AI-CHANGE-01 | version/diff/rollback IA | AI/Quality Owner |
| UX-GATE-01 | 12 écrans, accessibilité et confidentialité | Product/UX Owner |

## 11. Preuves

- `backend/app/platform/security/`
- `backend/app/modules/dce/infrastructure/quarantine.py`
- `backend/app/modules/dce/application/upload.py`
- `backend/app/platform/storage/`
- `ops/docker-compose.preprod.yml`
- `ops/`
- [AUD-02](./SMART_AO_PHASE0_AUD-02_RUNTIME_FLUX.md)
- [QUAL-01](./SMART_AO_PHASE0_QUAL-01_GOLDEN_DCE.md)
- [DEC-GATE](./SMART_AO_PHASE0_DEC-GATE_DECISIONS.md)
