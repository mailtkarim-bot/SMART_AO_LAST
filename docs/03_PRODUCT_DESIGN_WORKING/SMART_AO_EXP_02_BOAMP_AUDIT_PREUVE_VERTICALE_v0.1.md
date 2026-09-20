# SMART AO — EXP-02 BOAMP : audit et plus petite preuve verticale

**Statut :** AUDITÉ · PREUVE NOMINALE PROUVÉE  
**Date :** 14 septembre 2026  
**Autorité produit/métier :** `SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_CONSOLIDATED_v0.4.md`  
**Référence UX :** `SMART_AO_Catalogue_Ecrans_Parcours_Produit_OWNER_CONSOLIDATED_v0.3.md`

## 1. Décision de tranche

La plus petite preuve verticale d’EXP-02 est :

```text
observation BOAMP persistée
  → lecture patronale tenant-scopée
  → qualification humaine QUALIFIED
  → création d’une Affaire unique
  → même commande rejouée = même Affaire, sans doublon
```

La preuve est limitée à un avis public non expiré, un acteur `PATRON_ADMIN` avec MFA validée et un parcours continu dans l’interface. Le serveur revalide toujours le tenant, le rôle, l’observation et la qualification ; le navigateur ne décide jamais seul qu’une conversion est autorisée.

Cette tranche produit la première valeur d’EXP-02 sans construire le Radar complet. Elle couvre le noyau de `C02 Radar`, `C03 Opportunité` et le lien permanent vers `C04/C05 Affaire`.

## 2. Autorités et attentes métier

Le cahier OWNER v0.4 (§13) impose BOAMP comme source V1, une fraîcheur affichée, une provenance explicable, l’absence de score opaque et une conversion sans doublon. Le catalogue UX v0.3 rattache ces attentes à `OPP-01 Radar BOAMP` et `OPP-03 Fiche Opportunité`.

La conversion ne vaut ni GO/NO-GO, ni réception du DCE, ni prix, ni engagement commercial. `QUALIFIED` signifie seulement que le Patron retient le signal public selon le motif choisi.

## 3. Audit du code vivant

| Étape | Contrat et code observés | Verdict |
|---|---|---|
| Source | `market_watch` fournit `PublicNoticeSearchPort` et `BoampReadOnlySearch`. | Présent ; aucun accès riche BOAMP ne traverse le domaine. |
| Ingestion | `BoampOpportunityIngestionService` normalise les avis, borne pages/résultats/mots-clés, filtre les départements et les échéances passées, déduplique par `source_notice_id` et trie déterministement. | Présent ; le service reste volontairement sans effet de bord. |
| Staging | `scripts/ingest_boamp_opportunities.py` produit `SMART_AO_OPPORTUNITY_INGESTION_REPORT_V1` avec une allowlist publique et un fingerprint recalculable. | Présent ; pas de tenant ni d’identité dans le rapport. |
| Persistence | `BoampObservationRepository` persiste run, observation, lien, score `BOAMP_PUBLIC_V1`, événement et outbox dans une transaction ; les identités et la clé d’idempotence sont externes au rapport. | Présent ; la preuve PostgreSQL dédiée passe hors sandbox. |
| Lecture | `GET /api/v1/patron/boamp-opportunities` retourne une projection fermée, triée et filtrée par tenant, score et échéance. | Présent ; `observed_at` est maintenant publié en UTC. |
| Qualification | `POST /{observation_id}/qualification` accepte seulement les décisions et motifs fermés, exige `PATRON_ADMIN` membre actif et persiste une qualification append-only avec rejeu idempotent. | Présent et protégé. |
| Conversion | `POST /{observation_id}/case` et `BoampCaseCreationService` exigent `PATRON_ADMIN`, rechargent observation et dernière qualification `QUALIFIED`, créent une commande `CreateCase` avec `origin_kind=OPPORTUNITY` et `origin_reference_id`, puis dérivent l’`case_id` de la clé d’idempotence. | Présent côté serveur ; le contrôle de qualification ne dépend pas du navigateur. |
| Interface | `BoampOpportunityPanel`, `useBoampOpportunities` et `api.ts` savent lire et qualifier. | Présent : type/appel API de conversion, bouton après qualification, fraîcheur visible et identifiants conservés pour rejeu. |

## 4. Contrat minimal à coder

### Entrée

- session bearer active, tenant courant et MFA validée ;
- observation visible dans la liste patronale ;
- décision `QUALIFIED` avec motif `RELEVANT_PUBLIC_SIGNAL` ;
- `command_id`, `idempotency_key` et `correlation_id` générés côté client mais conservés pour tout rejeu de la même intention.

### Projection minimale visible

La liste et le détail montrent `source_notice_id`, titre public, collecte (`observed_at`), publication, échéance, départements, types, statut, score et explication. La date de collecte est exposée en UTC depuis `BoampOpportunityObservationRecord.observed_at` et affichée séparément de la date limite. Aucun texte DCE, montant, prix ou marge n’est ajouté.

### Transition nominale

1. Le Patron sélectionne une observation et enregistre `QUALIFIED`.
2. Après le reçu de qualification, l’action **Créer une Affaire** devient disponible pour cette observation dans la même session.
3. L’interface envoie `POST /api/v1/patron/boamp-opportunities/{observation_id}/case` avec les trois identifiants.
4. Le reçu expose `case_id`, `version`, `event_ids`, `replayed`, `command_id` et `idempotency_key`.
5. L’Affaire est rechargée dans le portefeuille et reste reliée à l’observation par `business_origin=OPPORTUNITY` et `origin_reference_id`.

### Rejeu et erreurs

- même payload et même `idempotency_key` : réponse `200`, `replayed=true`, même `case_id` et mêmes événements ;
- même observation avec une nouvelle `idempotency_key` : refus `409 DUPLICATE_FUNCTIONAL_IDENTITY`, aucune seconde Affaire ni nouvel événement ;
- clé réutilisée avec une autre intention : `409`, aucune nouvelle Affaire ;
- observation absente/hors tenant : `404` neutre ;
- qualification absente ou non `QUALIFIED` : `422 BOAMP_QUALIFICATION_REQUIRED` ;
- échec réseau ou réponse inconnue : l’interface conserve l’intention et propose le rejeu avec les mêmes identifiants, sans annoncer le succès avant un reçu.

## 5. Invariants et limites

- la qualification et la conversion restent deux actes humains distincts ;
- le score sert au tri et à l’explication, jamais à une décision automatique ;
- le serveur revalide tenant, rôle, observation et qualification à chaque conversion ;
- aucun droit de Responsable/Expert ou élévation depuis le navigateur n’est introduit ;
- la source publique et sa référence restent attachées à l’Affaire créée ;
- les lots, P0/P1, DCE, recherche sauvegardée, TED, panne BOAMP avec dernier succès et conversion d’un avis expiré restent hors de cette preuve ;
- le conteneur `smart-ao-v8-postgres` est disponible sur `127.0.0.1:5433` hors sandbox ; les tests DB doivent donc être lancés dans ce contexte d’exécution.

## 6. Critères de sortie de la tranche

La tranche nominale est considérée prouvée :

1. lecture tenant-scopée et projection sans champs internes ;
2. qualification `QUALIFIED` puis bouton de conversion visible uniquement après son reçu ;
3. envoi de la commande de création avec les identifiants fournis ;
4. bouton de conversion disponible uniquement après `QUALIFIED` ;
5. date de collecte visible et distincte de la date limite publique ;
6. résultat inconnu conservé et rejeu avec les mêmes identifiants, sans succès présumé ;
7. nouvelle clé sur la même observation refusée sans doublon et avec la référence BOAMP conservée.

Les tests PostgreSQL démontrent aussi la sortie complète : création `201`, rejeu `200/replayed=true`, provenance persistée, aucun doublon et refus serveur sans qualification, mauvais rôle, hors tenant ou clé en conflit.

## 7. Preuves exécutées pendant l’audit

- Front BOAMP après implémentation : **25 tests passés** (`useBoampOpportunities`, `BoampOpportunityPanel`, transport API), avec `typecheck`, `lint` et `build` passés.
- Backend applicatif et scripts non-DB : **15 tests passés** (ingestion, qualification, scoring, staging/persistence/lecture), plus `ruff` passé sur les fichiers touchés.
- Backend EXP-02 avec PostgreSQL dédié : **6 tests passés** pour qualification, immutabilité du signal, création/rejeu idempotent, refus de doublon et relecture P0/P1 sur `smart-ao-v8-postgres:5433`.
- Endpoint HTTP exécuté sous Uvicorn hors sandbox : **401** sans bearer, puis **200** avec score `100` et `P0=UNREVIEWED` ; la suite TestClient reste bloquée par l’incompatibilité d’environnement Starlette/httpx.
- `git diff --check` passe. Un avertissement Starlette/httpx reste sans impact fonctionnel.

## 8. Étape suivante

La projection P0/P1, le périmètre de lots, les états d’échéance et les inconnus d’ouverture sont désormais prouvés dans [`SMART_AO_EXP_02_QUALIFICATION_P0_P1_LOTS_ECHEANCES_INCONNUS_AUDIT_CADRAGE_v0.1.md`](SMART_AO_EXP_02_QUALIFICATION_P0_P1_LOTS_ECHEANCES_INCONNUS_AUDIT_CADRAGE_v0.1.md), sans modifier la preuve nominale. Le contrat de décision est cadré dans [`SMART_AO_EXP_02_DECISION_POURSUIVRE_ECARTER_AUDIT_CADRAGE_v0.1.md`](SMART_AO_EXP_02_DECISION_POURSUIVRE_ECARTER_AUDIT_CADRAGE_v0.1.md). La panne BOAMP, la saisie manuelle et la revue finale sont gelées dans [`SMART_AO_EXP_02_OWNER_EXPERIENCE_FREEZE_v0.1.md`](SMART_AO_EXP_02_OWNER_EXPERIENCE_FREEZE_v0.1.md) ; EXP-03 peut commencer.
