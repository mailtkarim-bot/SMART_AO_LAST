# SMART AO — EXP-06
## Audit des frontières validation → signature → dépôt → réception

**Statut :** AUDIT CODE VIVANT · P5, MANIFESTE, SIGNATURE ET HASH DE RÉCEPTION PROUVÉS · LECTURE STRUCTURÉE AJOUTÉE · RAPPROCHEMENT PARTIEL  
**Date :** 15 septembre 2026  
**Référence métier :** `docs/00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_CONSOLIDATED_v0.4.md` §11 et portes P4/P5.

## 1. Résultat de l’audit

| Frontière | Preuve déjà présente | Écart réel | Verdict |
|---|---|---|---|
| Validation du contenu | `PreparationReadinessRecord`, document technique généré, snapshot financier publié, manifeste versionné et hashé ; lecture Patron-only des entrées et exclusions ; périmètre `Case.scope_json` gelé avec le manifeste | Pas de projection unique indiquant la complétude par lot | **PARTIAL** |
| Autorisation P5 | `SubmissionPackageAuthorizationRecord` append-only, version/hash exacts, Patron Admin/Delegate + MFA, décision de soumission | Les destinataire, canal, signataires, lots et échéance ne sont pas encore des champs contrôlés de l’autorisation | **PROUVÉE SUR LE NOYAU** |
| Signature | Intention de signature liée au `manifest_sha256`, provider fermé, callback HMAC, hash de référence et projection bornée | La demande peut précéder P5, ce qui est compatible avec §11 ; aucune preuve de signature par pièce/lot | **PROUVÉE SUR LE NOYAU** |
| Export | ZIP déterministe avec manifeste et document technique, garde de décision et garde P5, stockage privé lu après les contrôles | L’export est un téléchargement local ; il ne constitue ni dépôt ni réception externe | **PROUVÉE COMME EXPORT** |
| Dépôt humain | Invariant `external_submission: NOT_PERFORMED` et notifications d’export | Aucun clic de portail, envoi automatique ou présomption de succès | **NON EFFECTUÉ PAR CONCEPTION** |
| Réception | `SubmissionEvidenceRecord` append-only, `manifest_sha256`, hashes et notes expurgées, types d’accusé ou référence portail | Aucun rapprochement structuré consultation/lot/tour/fichiers ni état « contenu entièrement rapproché » | **PARTIAL** |

## 2. Décision de conception

Le package immuable et son manifeste restent la candidate de référence. L’autorisation P5 ne change pas son contenu et n’est pas assimilée à une signature légale. La signature externe peut être demandée et reçue séparément, puis un opérateur humain effectue le dépôt hors SMART AO. Seule une preuve manuelle ultérieure peut établir un fait de réception ; elle ne doit pas transformer un reçu incomplet en correspondance complète.

La lecture Patron-only du manifeste exact est prouvée : version, hash, entrées, périmètre d'Affaire et exclusions sont exposés sans clé de stockage ni montant. Le `scope_json` déjà validé par l'agrégat Affaire devient partie du hash de candidate, ce qui empêche de confondre un paquet entre lots ou périmètres. Le mode `CANDIDATURE_ONLY` exige une justification explicite, conserve le périmètre, omet le snapshot financier et toute entrée de pricing, et reste donc contrôlable sans transformer l'absence de prix en zéro. La signature et la preuve de réception copient ce hash côté serveur, sans faire passer un fait manuel pour un dépôt automatique. La lecture structurée des preuves par package expose le hash, la version, le type et l’état `PARTIAL` ; la preuve PostgreSQL passe avec **37 tests** sur les packages et réceptions. L'export du paquet et l'enregistrement de la preuve imposent désormais aussi un step-up MFA ; relire les preuves ne change aucun fait et ne demande pas ce step-up. Une tentative humaine peut maintenant être enregistrée comme `HUMAN_DEPOSIT_ATTEMPT` avec `status: UNKNOWN`, sans créer de succès externe.

## 3. États difficiles conservés

- package absent ou hors tenant → réponse neutre ;
- version attendue différente → `VERSION_CONFLICT` ;
- manifeste altéré → `SUBMISSION_MANIFEST_INTEGRITY_FAILED` ;
- décision non prête → autorisation et export refusés ;
- export sans P5 → `SUBMISSION_PACKAGE_NOT_AUTHORIZED` ;
- signature déjà finalisée → `SIGNATURE_ALREADY_FINALIZED` ;
- résultat externe inconnu → aucun état de succès créé ;
- tentative humaine déclarée → `UNKNOWN`, conservée par hash du manifeste et jamais convertie en succès externe ;
- candidature seule sans justification → `CANDIDATURE_ONLY_REASON_REQUIRED` ; candidature seule justifiée → aucun snapshot financier ni entrée de pricing ;
- reçu sans inventaire complet → preuve conservée sans rapprochement intégral.

## 4. Ce qui est volontairement écarté

Aucun fournisseur de portail, automatisation de dépôt, agrégat de lots ou registre de signataires n’est ajouté sans contrat de source. La tentative humaine est un fait local déclaré, pas une preuve de portail. Une copie de sauvegarde et un redépôt ne sont pas encore des faits persistés : le téléchargement audité fournit une archive à conserver par l'opérateur, tandis qu'un nouveau paquet doit créer une version distincte et réautoriser son manifeste exact. Les champs absents du package actuel restent à construire dans une tranche dédiée ; le manifeste ne doit pas être enrichi avec des valeurs déduites.

## 5. Références de code

- `backend/app/modules/submission/application/service.py` — préparation, P5 et export.
- `backend/app/modules/submission/application/signature_service.py` — intention/callback de signature.
- `backend/app/modules/submission/application/evidence_service.py` — preuve manuelle expurgée.
- `backend/app/modules/submission/infrastructure/models/submission.py` — package, autorisation, signature et evidence.
- `backend/app/interfaces/http/routes/patron_submission.py` — préparation, autorisation et export.
- `backend/app/interfaces/http/routes/patron_submission_signature.py` — signature et callback.
- `backend/app/interfaces/http/routes/patron_submission_evidence.py` — réception manuelle.

## 6. Prochaine preuve

Cadrer la copie de sauvegarde et le redépôt, puis fermer les critères de rôles, d'audit et de gel d'EXP-06.
