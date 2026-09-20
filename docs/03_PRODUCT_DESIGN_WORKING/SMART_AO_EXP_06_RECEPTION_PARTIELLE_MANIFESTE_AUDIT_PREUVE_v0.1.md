# SMART AO — EXP-06
## Lecture structurée de la réception humaine

**Statut :** PREUVE POSTGRESQL ACQUISE · RAPPROCHEMENT PARTIEL ASSUMÉ
**Date :** 19 septembre 2026
**Autorité produit/métier :** `docs/00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md`

## But

Permettre au Patron de relire les preuves de réception attachées à un package sans confondre une saisie manuelle avec un dépôt automatique ou un rapprochement complet.

## Contrat minimal

La route `GET /api/v1/patron/submission-packages/{submission_package_id}/evidence` est Patron-only et tenant-scoped. Elle renvoie, pour chaque preuve :

- l’identifiant de preuve et le package ;
- la version du package ;
- le `manifest_sha256` copié lors de la saisie ;
    - le type `MANUAL_RECEIPT`, `MANUAL_PORTAL_REFERENCE` ou `HUMAN_DEPOSIT_ATTEMPT` ;
    - l’état `RECEIVED` ou `UNKNOWN` pour une tentative dont le résultat externe est indéterminé ;
- le statut de rapprochement `PARTIAL` ;
- l’invariant `external_submission: NOT_PERFORMED`.

Le service vérifie à la lecture que le hash conservé sur la preuve correspond encore au hash du package. Une divergence est refusée par `SUBMISSION_EVIDENCE_MANIFEST_MISMATCH`. Aucun numéro de lot, contenu de portail ou accusé complet n’est inventé.

## Parcours interface

Le panneau « Preuve manuelle » propose « Relire les preuves ». Chaque résultat affiche la version, le type, le hash du manifeste et « Réception partielle ». Le statut externe reste visible et négatif.

## Vérification

- La suite PostgreSQL `test_submission_package.py` + `test_submission_evidence.py` passe : **37 tests**. Elle vérifie la lecture sans preuve, la preuve liée au bon hash, le refus d'une divergence de hash, l'append-only, la tentative humaine `UNKNOWN`, le paquet `CANDIDATURE_ONLY` avec justification obligatoire et le redépôt comme nouvelle version nécessitant une nouvelle autorisation.
- Ruff, format Ruff et `git diff --check` passent sur les fichiers de cette tranche.
- PostgreSQL Compose du projet est accessible sur `127.0.0.1:5433` pour cette preuve locale ; ce port reste un état machine local, non une hypothèse de déploiement.

## Limites retenues

Le statut `PARTIAL` est volontairement terminal pour cette tranche. Une tentative humaine reste `UNKNOWN` tant qu'aucun fait externe contrôlé ne permet d'aller plus loin. Un rapprochement complet exigerait un contrat de lots, de fichiers remis, de tour de dépôt et de contenu de reçu fourni par une source externe. Aucun fournisseur ni automatisation de portail n’est ajouté ici.

## Prochaine preuve

Cadrer la copie de sauvegarde et le redépôt ; aucun état de conservation ou de nouveau dépôt ne doit être inféré du seul téléchargement local.
