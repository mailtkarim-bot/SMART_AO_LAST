# SMART AO — EXP-03 — Audit et cadrage de l’import DCE

**Date :** 15 septembre 2026  
**Statut :** AUDITÉ · PREUVES UPLOAD ET INVENTAIRE EXÉCUTÉES  
**Autorité :** cahier OWNER produit/métier v0.4, contrat UX OWNER v0.3, code vivant et tests exécutés

## 1. Décision de tranche

La première preuve EXP-03 reste limitée à **un objet DCE préparé, reçu en flux binaire privé, contrôlé puis rendu admissible ou rejeté de façon explicite**. Elle couvre l’interruption du flux, la quarantaine, le type détecté, la taille, le hash et l’antivirus. Elle ne prétend pas encore livrer l’inventaire multi-fichiers, l’extraction, la classification, les ancres multiformat ni un centre de traitements.

Une reprise ne réutilise jamais un objet déjà revendiqué ou rejeté. Après interruption, l’objet courant devient non admissible ; la reprise sûre consiste à préparer une nouvelle intention liée à la même Consultation et à conserver l’historique de la tentative précédente. Cette règle évite de compléter silencieusement un objet dont le contenu ou le résultat est inconnu.

## 2. Audit du flux existant

| Étape | Code vivant | Verdict |
|---|---|---|
| Intention avant octets | `PrepareDceStagingHandler` + `POST /api/v1/dce-staged-objects` | COUVERT |
| Réservation atomique | `ClaimDceStagedObjectUploadHandler` avec verrou DB | COUVERT |
| Réception privée | `LocalQuarantineStorageAdapter` : racine privée, fichier temporaire `.part`, limite, fsync, remplacement sans écrasement | COUVERT |
| Intégrité | taille réelle + SHA-256 calculés pendant le flux | COUVERT |
| Type réel | `PythonMagicContentInspectionAdapter`, indépendant de l’extension et du header | COUVERT |
| Antivirus | `ClamdTcpMalwareScanAdapter`, timeout et verdict `ERROR` fail-closed | COUVERT EN CODE |
| Persistance | `QUARANTINED`, `CLEAN`, `REJECTED`, `EXPIRED`, `CONSUMED` avec contraintes SQL | COUVERT |
| Nettoyage | suppression de la quarantaine après rejet ; suppression physique différée après expiration | COUVERT EN CODE |
| Rejeu de la même intention | reçu d’idempotence et refus d’une seconde revendication | COUVERT |
| Interruption d’un flux réel | rejet durable et absence de fichier partiel à vérifier par test dédié | À PROUVER DANS CETTE TRANCHE |
| Reprise opérateur | nouvelle préparation explicite ; aucun endpoint de reprise implicite | DÉCISION FIXÉE |
| Inventaire par fichier | `GET /api/v1/dce-versions/{id}/documents` relit les originaux admis et la dernière extraction | COUVERT POUR LA PREMIÈRE TRANCHE |
| Traitement multi-fichiers | pas encore de manifest/job public dans ce flux | FUTUR EXP-03 |

## 3. Contrat minimal de résultat

Le endpoint d’upload retourne uniquement `storage_object_id` et `state=CLEAN` lorsque la chaîne complète est confirmée. Il ne retourne ni chemin, bucket, nom de scanner, signature antivirus, ni contenu extrait.

Les erreurs restent neutres côté HTTP (`UPLOAD_REJECTED`) avec un statut adapté. La base conserve le motif opérable (`UPLOAD_LIMIT_EXCEEDED`, `STORAGE_WRITE_FAILED`, `UPLOAD_INTERRUPTED`, `INSPECTION_ERROR`, `MEDIA_TYPE_NOT_ALLOWED`, `SCAN_ERROR`, `MALWARE_DETECTED` ou `BYTE_SIZE_MISMATCH`) et l’objet rejeté ne peut plus être revendiqué.

Les états internes retenus sont :

```text
AWAITING_UPLOAD → UPLOADING → QUARANTINED → CLEAN
                         └──────→ REJECTED
AWAITING_UPLOAD/UPLOADING/QUARANTINED/CLEAN/REJECTED → EXPIRED
CLEAN → CONSUMED
```

`CLEAN` exige les métadonnées de taille, hash, type et scan ; `CONSUMED` exige la version DCE consommatrice ; aucune transition inverse n’est autorisée.

## 4. États difficiles et reprise

- **Flux interrompu avant un octet :** rejet `UPLOAD_INTERRUPTED`, aucune quarantaine persistante.
- **Flux interrompu après des octets :** rejet de la tentative et suppression du fichier temporaire ou final ; le contenu partiel n’est jamais analysable.
- **Dépassement de limite :** rejet `UPLOAD_LIMIT_EXCEEDED`, réponse 413, aucune réutilisation de l’objet.
- **Type interdit ou taille incohérente :** rejet après contrôle, sans scan si le type est interdit.
- **Scanner indisponible ou verdict inconnu :** `SCAN_ERROR`, jamais `CLEAN`.
- **Expiration pendant l’attente :** `EXPIRED`, puis rétention physique traitée par l’outbox.
- **Rejeu après succès, rejet ou revendication :** refus neutre ; pour reprendre, nouvelle intention idempotente.

Le document OWNER E04 exige progression, erreurs par fichier et reprise ; ces garanties s’ajouteront après cette preuve mono-objet, avec un premier cas Golden qui justifie un état de traitement durable. Aucun orchestrateur générique, stockage public ou dépendance nouvelle n’est introduit ici.

## 5. Preuve exécutable

1. préparer une intention non expirée ;
2. revendiquer et envoyer un flux qui lève une exception après un fragment ;
3. vérifier le rejet durable, son motif `STORAGE_WRITE_FAILED` et l’absence de fichier final/partiel ;
4. préparer une nouvelle intention pour la même Consultation ;
5. vérifier que la nouvelle intention reste `AWAITING_UPLOAD` tandis que la première reste `REJECTED` ;
6. vérifier qu’une seconde tentative sur le premier objet reste refusée ;
7. exécuter les refus de taille, type et antivirus déjà présents ;
8. relire l’inventaire d’une version admise et distinguer réception, lecture, format non pris en charge et document protégé sans exposer la quarantaine.

## 6. Vérifications déjà disponibles

Les tests existants couvrent la limite incrémentale, le type interdit sans scan, ClamAV `ERROR`, l’objet vide, la revendication unique, les transitions SQL, l’expiration et la consommation. La preuve ajoutée couvre un flux qui lève une exception après écriture partielle, la suppression du fichier temporaire et la préparation d’une nouvelle intention pour la même Consultation : **19 tests DCE staging/upload passent** sur PostgreSQL.

La première lecture d’inventaire est désormais exposée par API avec quatre états vérifiés (`RECEIVED`, `READ`, `UNSUPPORTED`, `PROTECTED`) et le code `issue_code` conservé. **1 test API PostgreSQL** et **12 tests d’extraction** passent ; un PDF chiffré devient `DOCUMENT_PROTECTED` sans fragment ni ouverture active.

Les tests API couvrent le bearer, le périmètre tenant, la neutralité des refus et l’absence de clé de stockage dans les réponses.

La suite historique `TestClient` peut rester bloquée par l’environnement Starlette/httpx ; les preuves DB dédiées et les tests applicatifs ciblés sont la référence exécutée lorsqu’elle se produit.

## 7. Prochaine étape unique

Passer à l’extraction multiformat avec ancres de source vérifiables.
