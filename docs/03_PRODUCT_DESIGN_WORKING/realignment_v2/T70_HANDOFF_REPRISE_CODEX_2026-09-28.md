# T70 — Reprise Codex après session Kimi Code (28 septembre 2026)

## État livré et prouvé le 28/09/2026

Branche `feat/ccap-cctp-risk-register-20260831`, poussée sur `origin` (tracking configuré).
Commits du jour (ordre chronologique) :

| Commit | Contenu |
|---|---|
| `6795439` | Backend post-réception : chaîne signal externe → cycle → dispatcher PostgreSQL (pile Codex), actes humains (owner act audit, revue de rejets de collecte), qualification `QualifyPaymentPostReceptionCycle` (Kimi) |
| `f8f8b55` | UI C07 : actes humains rejets partiels, déblocage validation Patron après traitement des rejets, formulaire de qualification coût/cash par cycle (Kimi) |
| `104b4bd` | Journal des tranches du 28/09 + contrat d’activation d’outils dans `AGENTS.md` |
| `ea3d2a6` | Packets et décisions de tranches T54–T69 (owner act audit paiement) |
| `8c948a9` | Clôture journal 28/09 |

## Preuves de gates (à re-vérifier avant d’intégrer quoi que ce soit)

- Backend complet : **1869/1869 tests verts** en 16 min 11 sur `postgresql+psycopg://smart_ao:smart_ao@127.0.0.1:5433/smart_ao_v8_test` (variable `SMART_AO_TEST_DATABASE_URL` explicite ; conteneur `smart_ao_v8-postgres-1`, base `smart_ao_v8_test` recréée ce jour).
- Frontend : **213/213 tests Vitest verts**, `typecheck`, `lint`, `build` verts.
- Ruff : propre sur les fichiers touchés le 28/09 ; erreurs I001/E701/E702 **préexistantes** dans des fichiers backend non commités plus tôt — laissées telles, à traiter si un gate complet l’exige.
- `.codex/`, `.kimi-code/` (install ECC projet), `.serena/` restent **non suivis volontairement**.

## Ce que Kimi Code a fait (pour ne pas re-dérouler)

1. **Acte humain rejets partiels (C07)** : formulaire décision `ACKNOWLEDGED`/`FOLLOW_UP_REQUIRED` + justification, persistance via `RecordPaymentCollectionRejectionReview`, affichage serveur seul, réutilisation des identifiants après échec non confirmé.
2. **Déblocage validation Patron** : C07 ne bloque plus l’approbation si une revue de rejets est persistée (`rejected_count > 0 && !rejectionReview` seul bloque). Aucune garde backend à lever (vérifié dans `payment_unknown_audit_owner_act_handler.py`).
3. **Qualification coût post-réception / hypothèse cash prudentienne** : contrat domaine `PaymentCostQualification`, commande `QualifyPaymentPostReceptionCycle` (idempotente, `PAYMENT_CYCLE_NOT_FOUND` si cycle inconnu ou hors Affaire), route `POST /api/v1/patron/cases/{case_id}/payment-cycles/{cycle_id}/cash-assumptions`, formulaire C07 par cycle. **Le statut du cycle ne change jamais** : qualifier une hypothèse ne crée pas de certitude de cash (garantie métier §27 et §4.11 des cahiers).

## Reprise proposée — prochaine tranche

La chaîne post-réception (signal → cycle → revue → audit → rejets → qualification → validation Patron) est close.
Candidats naturels, par priorité métier :

1. **Obligations post-réception** (cahier technique §4.12 `PostReceptionObligation` : OPR, essais, mise en service, DOE/DIUO, levée de réserves, GPA, maintenance initiale, clôture administrative, libération garanties — chacune avec coût, ressource, échéance, preuve, sanction liée). Nouvel agrégat tenant-scoped, séquence préférée §24.3.
2. **Carte d’Engagement Patron** (T6) : projection uniquement après stabilisation des sources ; aucune logique métier dans le frontend.
3. Poursuite T47–T69 si un packet reste ouvert (tous figés au 28/09).

Contraintes inchangées : sans ouverture publique ; aucune logique métier dans le frontend ; séquence §24.3 ; journal + Basic Memory mis à jour après chaque tranche.

## Vigilance

- La base de test `smart_ao_v8_test` a été **recréée** ce jour (CREATE DATABASE) ; si des données de test locales étaient attendues ailleurs, les recharger.
- Basic Memory n’a pas pu être resynchronisée depuis la session Kimi (MCP indisponible) : resynchroniser la note `SMART AO - Plan global de conception et réalisation` depuis Codex.
