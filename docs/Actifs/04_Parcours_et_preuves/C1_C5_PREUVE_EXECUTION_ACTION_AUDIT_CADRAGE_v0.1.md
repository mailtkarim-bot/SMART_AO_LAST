# C1/C5 — preuve humaine d’exécution d’une action reliée par C4

**Date :** 4 octobre 2026<br>
**Statut :** preuve locale C5 de bout en bout (déclaration, source immuable retrouvée, acte de confirmation séparé) ; qualification d’exploitation VPS ouverte<br>
**Base auditée :** HEAD `9c2a982` et WIP local C2/C3/C4, dont C4 non commité<br>
**Autorités :** Product Freeze PF31-03/04, Master métier M31-05 étapes 4–5, Cahier technique CT31-04/07/15

## AS-IS vérifié

- C1 enregistre une action Patron sous la condition d’une revue d’applicabilité courante `APPLICABLE_TO_HANDOVER`. Sa projection reste `RECORDED` ; le texte, la date déclarée et les `evidence_refs` décrivent l’intention enregistrée, pas une exécution constatée.
- C4 est un acte relationnel distinct qui relie une action C1 exacte à des actes C3 exacts. `LINKED` établit une relation humaine déclarée ; il ne modifie ni C1/C3 ni l’état de l’action.
- `ContractExecutionEvidenceRecord` est un acte tenant/Affaire-scoped voisin. Il impose un type parmi `WORK_RECEPTION`, `RIGHTS_PRESERVATION`, `CONTRACT_EXIT`, un résumé, des références de source et de preuve, et une date éventuelle. Il ne référence pas d’action C1 ni de relation C4 exacte.
- Le lecteur des actes d’exécution expose les références persistées et la version d’instrument applicable ; il ne résout pas ces références en pièce réellement présente et vérifiée. Leur présence en base ne prouve donc pas la récupération d’un document.
- Le cycle `PostReceptionObligationTransition` peut exiger au moins une chaîne `evidence_ref` pour une transition `COMPLETED`. Ce contrôle garantit une référence déclarée non vide, pas l’existence, l’intégrité ni la consultation de la pièce.
- Le reçu P5/manifeste et ses empreintes concernent la soumission. Son contrat distingue déjà l’état technique `NOT_PERFORMED` d’une réception externe ; ce flux n’est pas un registre générique d’exécution d’action après attribution.
- Les références DCE ont des versions/hash documentaires, mais leur stockage et leur portée restent liés au DCE. L’audit n’a pas établi de registre générique de pièces d’exécution post-attribution, tenant/Affaire-scoped, que C5 pourrait prétendre interroger.

## Risques et distinctions métier

Les quatre affirmations ci-dessous sont indépendantes. Aucune ne doit être inférée de la précédente :

1. **Intention** — l’action demandée ou enregistrée en C1, liée aux impacts C3 par C4.
2. **Réalisation déclarée** — une personne dit avoir exécuté tout ou partie de l’action, ou dit ne pas l’avoir exécutée. Cette déclaration reste attribuée à son auteur et à sa date ; ce n’est pas une vérification.
3. **Preuve retrouvée** — une pièce identifiée a effectivement été résolue depuis une source autorisée et son identité/intégrité contrôlée selon le contrat de cette source. Une URL, un chemin, un locator, un hash saisi librement ou un `evidence_ref` non résolu ne sont que des références déclarées.
4. **Confirmation externe** — une réponse ou un accusé de réception externe a été reçu et relié à une source exacte. Une preuve interne de réalisation ne démontre ni transmission, ni réception, ni acceptation par un tiers.

Risques à prévenir : afficher « terminé » après simple déclaration ; convertir absence de pièce en échec ou succès ; assimiler hash déclaré à hash recalculé ; confondre remise/envoi et accusé reçu ; laisser une révision C4 obsolète paraître encore applicable ; mélanger cette preuve à C1/C3/C4 ou écraser leurs actes ; exposer une pièce d’un autre tenant ou contourner `FINANCIAL_PRIVATE`.

## Décision de cadrage proposée — acte C5 distinct

Créer, après validation de ce cadrage dans le plan d’implémentation, un acte humain C5 append-only qui documente l’exécution déclarée d’une action C1 exacte, avec référence obligatoire à l’acte C4 exact ayant relié cette action aux impacts C3. C5 ne réécrit et ne clôt aucun acte antérieur.

Identifiants d’ancrage proposés : `action_id`, `c4_relation_id` (ID de la révision C4 parent), tenant, Affaire et événement dérivés/validés côté serveur. L’acte conserve l’acteur, l’horodatage serveur, le motif et la révision attendue. La référence à C4 doit être contrôlée comme appartenant à la même action, au même événement, à la même Affaire et au même tenant. Une relation C4 devenue `REVIEW_REQUIRED` reste consultable dans son état historique ; C5 ne la rend pas courante par sa seule existence.

Le contenu garde trois champs d’état indépendants et fermés :

| Axe | Valeurs de cadrage | Sens et garde |
|---|---|---|
| Réalisation déclarée | `DECLARED_PERFORMED`, `DECLARED_PARTIAL`, `DECLARED_NOT_PERFORMED`, `UNKNOWN` | Déclaration humaine attribuée ; `UNKNOWN` est obligatoire lorsque le déclarant ne peut établir l’état. Ne jamais projeter `COMPLETED` comme fait vérifié. |
| Pièce | `UNKNOWN`, `REFERENCED`, `RETRIEVED` | `REFERENCED` signifie seulement qu’un locator a été déclaré. `RETRIEVED` exige que le serveur retrouve une pièce via une source autorisée et vérifie son identifiant/version/hash conformément au contrat de cette source. Sans intégration probante disponible, rester `UNKNOWN` (ou `REFERENCED` si un locator existe). |
| Confirmation externe | `UNKNOWN`, `NOT_CONFIRMED`, `CONFIRMED` | Un acte distinct de confirmation, sa source exacte et sa date sont nécessaires pour `CONFIRMED`. C5 n’envoie rien et ne sonde aucun tiers. Une pièce interne retrouvée ne suffit pas. |

Le résumé et les références de source restent visibles, mais ne remplacent pas ces états. Les dates sont déclarées ou horodatées comme telles ; aucun délai, effet juridique, paiement, préservation de droit ou réception n’est calculé. Le terme `CONFIRMED` décrit uniquement l’existence d’une confirmation externe sourcée, pas la validité juridique de l’exécution.

## Frontière d’intégration minimale

- **Propriétaire provisoire :** module `pricing`, au voisinage des actes C1–C4 et des actes d’exécution actuels ; l’audit ne justifie pas un nouveau bounded context.
- **Persistance :** migration additive C5 et actes immuables. Éviter d’ajouter des colonnes à C1/C3/C4 ou de transformer leurs listes de références historiques.
- **Écriture :** commande Patron sous la politique existante `FINANCIAL_PRIVATE`, avec idempotence et contrôle de révision. Aucune commande ne déclenche l’action C1, une notification ou une communication externe.
- **Projection :** actes C5 affichés séparément dans C07/C12 ; état de liaison C4 courant/à requalifier projeté séparément des faits déclarés C5. Une nouvelle revue C1/C4 rend le lien signalable comme obsolète sans altérer le dossier C5.
- **Pièce :** avant de permettre `RETRIEVED`, définir une source effectivement exploitable et son adaptateur de vérification. Tant que ce point n’est pas résolu, C5 peut enregistrer la déclaration et une référence, mais ne doit pas prétendre avoir retrouvé la pièce. Ne pas créer un stockage générique dans cette tranche par anticipation.
- **Confirmation :** future commande humaine append-only, uniquement si un flux de confirmation exact est défini. Pas de connecteur externe ni de polling implicite dans C5.

## Preuves à exiger pour l’implémentation C5

| Cas | Preuve attendue |
|---|---|
| Déclaration nominale sans locator/pièce | HTTP/PostgreSQL : déclaration conservée, axe pièce et confirmation `UNKNOWN`, C1 `RECORDED` et C4 inchangés |
| Réalisation partielle, non réalisée et inconnue | états distincts, auteur/date/motif conservés ; aucune projection « terminée » |
| Référence présente, source indisponible ou identité/hash discordant | `REFERENCED`, `UNKNOWN` ou état d’échec de vérification fermé selon contrat ; jamais `RETRIEVED` sur seule saisie du locator/hash |
| Confirmation externe absente | reste `UNKNOWN` même si la réalisation est déclarée et la pièce interne retrouvée |
| Intégrité et permissions | refus action/C4 d’un autre tenant/Affaire/événement, relation C4 incohérente, Collaborateur et rôles non autorisés ; aucune fuite dans erreur/compteur |
| Révision et rejeu | clé idempotente stable, rejeu sans doublon, conflit `expected_revision` refusé ; aucune réécriture d’actes |
| Obsolescence | nouvelle revue C1 ou C4 projetée séparément comme `REVIEW_REQUIRED`; la déclaration C5 et ses sources restent historiques |
| Non-déclenchement | tests prouvant absence d’envoi, notification, exécution de l’action et appel externe |
| Projection | API et UX distinguent intention C1, relation C4, déclaration C5, pièce retrouvée et confirmation externe sans fusion d’historiques |

## Limites et questions techniques ouvertes

1. Le dépôt ne fournit pas encore, selon cet audit, de registre générique résolvant les références de pièces d’exécution post-attribution. Le contrat de source permettant de prouver `RETRIEVED` doit être choisi depuis une source réellement disponible ; aucune source ni fichier ne doit être inventé.
2. Les enums ci-dessus sont un cadrage destiné à la tranche d’implémentation, pas un contrat déjà accepté par le code ni une conclusion juridique.
3. `NOT_CONFIRMED` doit signifier qu’un humain a explicitement déclaré l’absence de confirmation ; l’absence d’enregistrement reste `UNKNOWN`.
4. L’audit est local. Aucun navigateur CUA, service de stockage réel, compte tiers, environnement VPS ou corpus chantier client n’a été utilisé.

**Non-objectifs :** modifier ou recalculer C1/C3/C4 ; marquer C1 terminé ; exécuter l’action ; transmettre ou notifier ; affirmer réception, paiement, conformité ou préservation d’un droit ; calculer une échéance juridique/financière ; promouvoir un état inconnu.

**Au cadrage initial :** aucun code de production, schéma, migration ou acte métier n’avait été modifié. NO-GO public maintenu.

## Implémentation locale C5 — preuve et frontière

**Base d’implémentation :** branche `codex/checkpoint-orca-smartao-20261003`, HEAD de reprise `bb441538b3636d0b29194ea69461b5c7ca0158c7`, WIP local non commité/non poussé. La tête Alembic locale attendue en runtime est `20261003_0130`, migrations additives `0129` (acte) et `0130` (sources), au-dessus de `0128`.

- L’acte `CaseContractChangeActionExecutionRecord` est séparé des registres C1/C3/C4, tenant/Affaire/événement-scoped et append-only. Il référence l’action C1 et l’identifiant exact du parent C4. La contrainte d’écriture vérifie que le parent C4 appartient à la même action. Idempotence par commande, verrou de l’Affaire et `expected_revision` sont appliqués ; C1 demeure `RECORDED`.
- La route Patron `POST /api/v1/patron/cases/{case_id}/contract-change-events/{event_id}/actions/{action_id}/execution-acts` utilise l’autorisation existante `PATRON_ACTION_WRITE` classée `FINANCIAL_PRIVATE`. La lecture expose l’acte C5 séparément et projette son parent C4 comme `CURRENT`, `REVIEW_REQUIRED` ou `SUPERSEDED` sans modifier l’historique.
- La réalisation humaine accepte `DECLARED_PERFORMED`, `DECLARED_PARTIAL`, `DECLARED_NOT_PERFORMED` et `UNKNOWN`. Sans pièce vérifiée, l’état pièce est `UNKNOWN`; un locator libre reste `REFERENCED`.
- La migration `0130` crée un objet source C5 propre à l’action/C4 exact, identifiant UUID opaque, version immuable 1, clé privée, taille, SHA-256 serveur, MIME détecté et verdict/versions du scanner. Upload borné et ClamAV fail-closed; le contenu devient `CLEAN` seulement après contrôles. Avant qu’un acte C5 soit `RETRIEVED`, le service relit les octets sous tenant/Affaire/événement/action/C4/kind et recalcule la taille et SHA-256. Toute absence, mauvaise portée, lecture impossible ou discordance ferme le chemin positif.
- Le Patron peut ensuite enregistrer un acte distinct `CONFIRMED` référant un objet propre `EXTERNAL_CONFIRMATION` compatible avec l’acte/C4 exact. Cet acte prouve le rattachement et la déclaration datée du Patron; la pièce uploadée ne prouve pas à elle seule l’authenticité d’un tiers. Aucun envoi, polling ou appel tiers n’a lieu. C1 reste `RECORDED`; C1/C3/C4 ne sont pas mutés.

### Preuves exécutées

| Preuve | Commande / périmètre | Résultat | Ce que cela établit |
|---|---|---|---|
| RED avant code | `backend/tests/db/test_case_handover_http_e2e.py::test_http_c1_keeps_unknown_until_patron_links_change_to_handover_and_records_action` | Échec attendu : route C5 absente, HTTP 404 | Le nouveau parcours n’existait pas avant l’implémentation |
| HTTP/PostgreSQL | `SMART_AO_TEST_DATABASE_URL='postgresql+psycopg://smart_ao:smart_ao@127.0.0.1:5433/smart_ao_v8_test' ./.venv/bin/pytest -q --tb=short backend/tests/db/test_case_handover_http_e2e.py` | 2/2 sur le scanner de test; le harnais local rejoue aussi ce parcours avec ClamAV réel sur son réseau privé | Migration upgrade/downgrade, verdicts INFECTED/ERROR refusés en HTTP 422 et objets `REJECTED`, MIME/limite, rejeu identique et contenu modifié refusé, relecture/hash et stockage altéré, `UNKNOWN`/`REFERENCED`/`RETRIEVED`, confirmation séparée et type exact, refus rôle/tenant/parent, C1 `RECORDED`, append-only. En mode simulation, CLEAN passe par le vrai adaptateur ClamAV, EICAR reçoit INFECTED et la connexion refusée produit ERROR. |
| Annulation asynchrone C5/quarantaine | `backend/tests/infrastructure/test_quarantine.py::test_local_quarantine_cancellation_removes_partial_file` + `backend/tests/application/test_case_contract_change_evidence_upload.py::test_cancelled_c5_scan_rejects_intent_and_removes_quarantined_object` | **2/2** après RED explicite | L’annulation pendant l’écriture supprime le `.part`; l’annulation du scan supprime les octets C5, persiste `REJECTED` et re-propage l’annulation. Les fichiers ne peuvent pas être retrouvés comme `CLEAN`. |
| Arrêt brutal, récupération et retry C5 | `test_abrupt_process_exit_leaves_expected_recovery_target` + `backend/tests/db/test_case_handover_http_e2e.py::test_http_c1_keeps_unknown_until_patron_links_change_to_handover_and_records_action` | Trois processus SIGKILL; E2E HTTP/PostgreSQL **1/1** avec panne de suppression injectée | `.part` et objet après renommage sont récupérés; les intents expirés deviennent `REJECTED`. L’outbox passe à `RETRY` après l’échec, puis `PUBLISHED` après suppression réussie; le rejeu ne crée pas de nouvel outbox et l’objet `CLEAN` est préservé. |
| Restauration isolée du backup C5 | `backend/tests/ops/test_quarantine_restore.py` + `scripts/simulate_preprod_local.sh` | Helper **3/3**; restauration ops réelle réussie; hash DB↔objet **2/2**; mismatch et traversal nettoyés | La fixture E2E opt-in conserve deux sources `CLEAN` et leurs octets dans un DB/volume jetable; le manifeste DB restauré doit correspondre en nombre aux hashes vérifiés. Une archive objet altérée avec checksum externe recalculé est refusée; le snapshot DB et le volume temporaire anonyme sont supprimés. L’E2E normal conserve le truncate et downgrade. |
| Web | `pnpm --dir web test -- src/features/decision/CaseContractChangePanel.test.tsx` | 300/300 tests du projet | Le test C5 couvre le parent C4 exact, la saisie déclarative et la séquence de préparation/upload navigateur; ce n’est pas une recette CUA |
| Contrats et qualité | typecheck, lint, build, Ruff ciblé, mypy 9 modules, `git diff --check` | verts | Compilation/qualité statique des chemins touchés ; Vite garde un avertissement de chunk >500 kB |
| Contrat tête/ALEMBIC et documentation | `backend/tests/architecture/test_schema_head_contract.py` + `backend/tests/ops/test_product_freeze_authority_contract.py` | 5/5 | Runtime `0130` et autorité Product Freeze actifs alignés; le module E2E prouve upgrade/downgrade sur DB dédiée |
| Suite backend complète | `SMART_AO_TEST_DATABASE_URL=<base PostgreSQL éphémère loopback, conteneur digest-pinné sans volume> ./.venv/bin/pytest --import-mode=importlib -q --tb=short` | **2020/2020**, 19 min 05, 1 avertissement Starlette/httpx | Base de test dédiée temporaire; couvre le code de récupération C5 et le worker; le test E2E avec panne de suppression a été rejoué ensuite ciblément (**1/1**) |
| Semgrep | `SEMGREP_SEND_METRICS=off semgrep scan --config=p/security-audit` sur le périmètre modifié C5/backend/ops/web | Semgrep 1.179.0 : 0 finding, 21 fichiers analysés, 99 règles exécutées | Scan local uniquement ; ne prouve pas la sécurité globale, l’exploitation VPS ni l’authenticité d’une pièce |
| Préflight ops C5 | `SEMGREP_SEND_METRICS=off semgrep scan --config=p/security-audit ops/preflight-checklist.sh backend/tests/ops/test_preprod_ops_contract.py` | Semgrep 1.179.0 : 0 finding, 2 fichiers, 79 règles; contrats ops/autorité **37/37** au contrôle du 4 octobre | Garde du chargement `.env.preprod` en place ; aucun stockage/VPS/ClamAV de préproduction n’a été qualifié |
| ClamAV runtime local | Image Compose `clamav/clamav@sha256:1b6920e8c32cca47ea33b1e2611d9a4740ccc622cf13b30b29f8283d60175e39`, conteneur temporaire sans port publié ni volume persistant | ClamAV **1.4.6**, signatures **28142**, ping `PONG`; fichier synthétique propre `OK`; EICAR de test détecté `Eicar-Test-Signature FOUND`; conteneur arrêté et auto-supprimé | Smoke direct du service réel seulement; ne vérifie pas l’adaptateur HTTP C5 en préproduction ni stockage chiffré. ERROR HTTP est couvert par l’E2E simulé et le test d’adaptateur de connexion du backend |
| Semgrep ops+C5 ERROR | `SEMGREP_SEND_METRICS=off semgrep scan --config=p/security-audit backend/tests/db/test_case_handover_http_e2e.py backend/tests/ops/test_preprod_ops_contract.py ops/preflight-checklist.sh` | Semgrep 1.179.0 : 0 finding, 3 fichiers, 79 règles; scan séparé du script local : 0 finding, 2 fichiers, 79 règles | Scan local des fichiers modifiés dans cette étape |
| Semgrep récupération C5 + quarantaine | `SEMGREP_SEND_METRICS=off semgrep scan --config=p/security-audit` sur les 8 fichiers C5/worker/quarantaine et tests modifiés | Semgrep 1.179.0 : 0 finding, 8 fichiers, 79 règles | Scan ciblé uniquement; aucun finding ne constitue une garantie de sécurité globale |
| Simulation de stack locale | `./scripts/simulate_preprod_local.sh` | Run du 4 octobre : readiness + ClamAV réel CLEAN/INFECTED/ERROR et reprise; E2E normal **2/2**, E2E préservé **2/2**; vrai `ops/backup-preprod.sh` produit le dump, l’archive C5, les volumes Caddy et le manifeste complet, tous hashes vérifiés; vrai `ops/restore-preprod.sh` restaure **171 tables** et vérifie les deux objets C5 `CLEAN` **2/2**. Mismatch avec manifeste externe valide refusé, DB/volume temporaires nettoyés; traversal refusé et DB/volume nettoyés. Deux backups concurrents : le second est refusé avant nettoyage, le `.tmp` du premier et le manifeste précédent restent valides, puis le premier publie son manifeste après déblocage. SIGKILL du backup également refusé par le restore incomplet et récupéré au run suivant par suppression ciblée du `.tmp`. ClamAV 1.4.6/daily 28143. | Simulation sans données client. Pas de preuve de chiffrement au repos ni de VPS. `trap EXIT` ne nettoie pas les ressources du restore après SIGKILL; la récupération est la prochaine tranche locale |

### Statut et limites restantes

La frontière locale livrée est la **capture humaine append-only, la vérification d’intégrité d’un objet C5 reçu et la restauration vérifiée en volume temporaire**; elle ne prouve ni l’exécution physique de l’action ni l’authenticité d’une confirmation externe. Une référence non résolue reste `REFERENCED`; une absence reste `UNKNOWN`. L’accès à un stockage objet réel, CUA, VPS, comptes tiers et corpus client n’a pas été utilisé. Aucun commit, push ou déploiement n’a eu lieu. Basic Memory n’était pas exposé dans cette session; le plan global et le présent dossier portent le statut courant.

## Décision de source — qualification locale du substrat

### Candidats observés

| Candidat | Preuve présente dans le dépôt | Décision pour C5 |
|---|---|---|
| `DceStagedObjectRecord` + `DceUploadService` | UUID objet, taille, SHA-256 calculé pendant l’upload, MIME détecté par signature, verdict ClamAV et état CLEAN ; clés privées. Les objets sont reliés à une Consultation et consommés par une version DCE. | Écarter comme registre C5 : périmètre métier pré-attribution et absence de lien action/C4 post-attribution. Réutiliser ses ports/adapters d’upload seulement. |
| `EnterpriseDocumentUploadRecord` / `EnterpriseDocumentRecord` | Upload privé, hash calculé, MIME et antivirus ; acte de vérification Patron. | Écarter comme source générique C5 : types fermés `INSURANCE`, `KBIS`, `RIB`, racine société sans action/Affaire. |
| `ContractExecutionEvidenceRecord` | Acte append-only et tenant/Affaire-scoped avec dates et références. | Écarter comme preuve retrouvée : les références ne sont pas résolues en octets ni hash recalculés et le type ne référence pas le C4 exact. |
| `S3PrivateObjectStorage` | Adaptateur privé avec `IfNoneMatch`, métadonnée SHA-256, SSE `AES256` par défaut et lecture bornée ; les tests utilisent un client simulé. | Ne pas qualifier comme source actuellement disponible : `.env.example` désactive l’intégration, aucun endpoint/bucket réel n’est configuré ici et le bootstrap ne l’utilise que pour les documents générés/lectures DCE. |

### Source C5 implémentée et qualification d’exploitation restante

Le registre dédié C5 est implémenté sur le pipeline privé existant : `LocalQuarantineStorageAdapter`, détection MIME par signature et `ClamdTcpMalwareScanAdapter`. La clé est créée côté serveur sous un préfixe C5 non exposé; l’identité publique est un UUID d’objet opaque, version 1 immuable. L’objet lie tenant, Affaire, événement, action C1 et relation C4 exacte. Le SHA-256 est calculé côté serveur à l’ingestion; les octets sont relus de manière tenant-scopée et taille/hash recalculés avant `RETRIEVED`. Tout verdict autre que CLEAN ou toute indisponibilité refuse l’admission.

Une confirmation externe sera un acte Patron append-only séparé, attaché à un objet C5 de type `EXTERNAL_CONFIRMATION`, avec date de réception déclarée et source exacte. La pièce seule ne prouvera pas l’authenticité externe ; elle prouvera que l’acteur a relié cet objet et cette déclaration à la confirmation. Aucun envoi, polling ou appel tiers ne sera fait.

**Qualification du substrat :** `./.venv/bin/pytest -q --tb=short backend/tests/infrastructure/test_quarantine.py backend/tests/infrastructure/test_object_storage.py` — **20/20** lors de la qualification précédente. Ces tests couvrent permissions locales 0700/0600, collision sans écrasement, traversal, limite, SHA, lecture bornée, MIME, verdicts ClamAV CLEAN/INFECTED/ERROR et contrats S3 simulés. L’E2E C5 courant prouve maintenant la liaison action/C4 et les comportements HTTP/PostgreSQL du registre dédié.

**Limite de stockage :** le pipeline local prouve une racine privée et des permissions POSIX, pas un chiffrement au repos. La source est qualifiée pour la tranche locale/no-go ; elle ne constitue pas une qualification d’exploitation VPS. Pour toute qualification de déploiement, confirmer le stockage chiffré approuvé avant d’y conserver des pièces chantier.

**Qualification préproduction — contrôle local du 3 octobre 2026 :** aucune configuration ou stack préproduction réelle n’est disponible dans ce checkout. `ops/.env.preprod` est absent; les seuls services SMART_AO actifs vus dans le contexte Docker sont le PostgreSQL de test `smart_ao_v8` (5433), sans backend, Caddy ni ClamAV préproduction. `docker compose ... ps` ne peut pas être évalué sans les variables requises. Le Compose décrit bien ClamAV avec image digest-pinnée, healthcheck, réseau interne et dépendance backend à son état healthy; ce sont des contrats statiques. Un smoke ClamAV direct avec image digest-pinnée en conteneur temporaire confirme le ping, verdict CLEAN et détection EICAR, sans port publié ni volume persistant; la simulation Compose locale complète confirme ensuite la readiness et la récupération après panne. Le stockage objet S3 est désactivé dans l’exemple. Le volume local de quarantaine et les archives backup ne prouvent pas le chiffrement au repos. `backend/tests/ops/test_preprod_ops_contract.py` passe **33/33**. Le préflight échoue désormais explicitement sur le fichier `ops/.env.preprod` absent après avoir ajouté ce garde; ce refus est attendu et fermé. Aucun VPS ou contenu des volumes préexistants n’a été inspecté.

**Prochaine étape consignée au plan :** tuer `ops/restore-preprod.sh` par SIGKILL après création de sa base et de son volume temporaires; établir une récupération idempotente strictement bornée aux ressources du run interrompu. Chiffrement au repos et préproduction réelle restent non qualifiés; aucun VPS n’est demandé, NO-GO public maintenu.

**NO-GO public maintenu.**
