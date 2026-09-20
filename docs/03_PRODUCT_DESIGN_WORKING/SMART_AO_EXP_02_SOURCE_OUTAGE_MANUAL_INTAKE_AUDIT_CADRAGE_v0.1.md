# SMART AO — EXP-02 : panne de source externe et saisie manuelle maîtrisée

**Statut :** AUDITÉ · CONTRAT IMPLÉMENTÉ · PREUVES CIBLÉES  
**Date :** 15 septembre 2026  
**Autorité produit/métier :** `SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_CONSOLIDATED_v0.4.md`  
**Référence UX :** `SMART_AO_Catalogue_Ecrans_Parcours_Produit_OWNER_CONSOLIDATED_v0.3.md`

## 1. Objet et verdict

Le cahier OWNER v0.4 exige que le Radar rende une panne BOAMP visible, affiche la date du dernier succès, n'affirme pas que les données sont à jour et laisse une saisie manuelle disponible. Les observations déjà enregistrées doivent rester consultables ; une panne ne doit ni les effacer ni les transformer en résultat vide réputé fiable.

**Verdict :** le modèle possède déjà les deux briques nécessaires. `boamp_ingestion_runs.completed_at` et `status=RECORDED` permettent de retrouver le dernier succès tenant-scopé ; `CreateCase` accepte déjà une origine `MANUAL` et impose une commande idempotente. Il manque seulement une projection de santé de source dans le flux Radar et un accès explicite à la saisie manuelle lorsque la source n'est pas disponible.

## 2. Audit du code vivant

| Élément | Preuve observée | Conclusion |
|---|---|---|
| Adaptateur BOAMP | `BoampReadOnlySearch` borne la requête, suit une allowlist et lève `BoampRegistryUnavailable` pour réseau, 429, 5xx, statut inattendu ou réponse invalide. | La panne est déjà fail-closed et typée. |
| Ingestion | `BoampOpportunityIngestionService` reste borné, dédupliqué et sans effet de bord ; le script de collecte retourne un code d'erreur sans fabriquer de candidats. | Une erreur ne doit pas être convertie en liste vide. |
| Historique de collecte | `BoampIngestionRunRecord` persiste `status`, `started_at`, `completed_at`, le profil et le volume ; les runs réussis sont `RECORDED`. | Le dernier succès est lisible sans nouvelle table. |
| Observations | `BoampOpportunityObservationRecord` est append-only par empreinte ; les liens de run conservent la source. | Une panne ne supprime ni ne remplace les observations antérieures. |
| Lecture Radar | `GET /api/v1/patron/boamp-opportunities` projette les observations tenant-scopées et la fraîcheur `observed_at`. | Ajouter la santé de source au même contrat garde le dernier état visible. |
| Saisie manuelle | `POST /api/v1/cases` et `CreateCasePanel` acceptent uniquement `origin_kind=MANUAL` dans la tranche actuelle, avec `command_id` et `idempotency_key`. | Réutiliser ce flux ; aucun formulaire parallèle ni nouvelle origine. |

## 3. Contrat minimal retenu

La réponse du Radar porte un bloc fermé `source_status` :

```json
{
  "source": "BOAMP",
  "state": "AVAILABLE | UNAVAILABLE | UNKNOWN",
  "checked_at": "2026-09-15T00:00:00+00:00",
  "last_success_at": "2026-09-14T21:30:00+00:00",
  "retryable": true,
  "manual_entry_available": true
}
```

- `AVAILABLE` signifie que la sonde publique a répondu correctement au moment indiqué ; cela ne promet pas l'exhaustivité de la collecte.
- `UNAVAILABLE` signifie que la sonde a échoué avec `BoampRegistryUnavailable` ou une indisponibilité de connecteur. Les observations antérieures restent visibles.
- `UNKNOWN` signifie qu'aucune sonde n'est configurée ou qu'aucun état fiable n'est disponible. L'interface ne doit pas écrire « à jour ».
- `last_success_at` est le `completed_at` du dernier run `RECORDED` du tenant ; il peut être nul lorsque le tenant n'a jamais réussi une collecte.
- `retryable=true` rend la relance explicite. La relance ne crée ni observation ni Affaire à elle seule.
- `manual_entry_available=true` ouvre le flux `CreateCasePanel` existant et sa provenance `MANUAL`.

La projection de santé n'expose ni URL interne, ni exception, ni secret. Une recherche source qui échoue ne renvoie pas `observations=[]` comme si aucun avis n'existait.

## 4. Parcours vertical

1. Le Patron ouvre ou actualise le Radar.
2. Le serveur lit les observations conservées et sonde BOAMP avec une requête publique bornée.
3. Le serveur retourne les observations conservées plus `source_status` ; il conserve `last_success_at` même lorsque la sonde échoue.
4. L'interface affiche l'état, la date de contrôle et, en panne, la date du dernier succès sans mention « à jour ».
5. Le Patron peut **Relancer** ; le rejeu reste une lecture bornée.
6. Le Patron peut **Saisie manuelle**, qui ouvre le formulaire d'Affaire existant. Le serveur conserve `origin_kind=MANUAL`, l'auteur et les identifiants idempotents.
7. Une réponse inconnue de création manuelle conserve le formulaire et rejoue la même commande ; aucun succès n'est annoncé sans reçu.

## 5. Invariants et limites

- Une panne BOAMP ne supprime, n'écrase ni ne déclasse les observations déjà persistées.
- `last_success_at` provient d'un run réellement `RECORDED`, jamais d'une tentative commencée ou d'une réponse vide.
- Un état `UNAVAILABLE` ou `UNKNOWN` ne se transforme pas en « aucun résultat » et ne certifie pas la fraîcheur.
- La relance est une lecture ; la collecte/persistance reste une opération séparée et bornée.
- La saisie manuelle utilise le flux Case existant, sans identifiant d'affaire saisi par l'utilisateur et sans nouvelle table.
- L'origine `MANUAL` ne réclame pas de référence externe ; l'interface conserve la justification saisie et le serveur journalise l'acteur.
- Le score BOAMP, la qualification P0/P1 et la conversion idempotente restent inchangés par la panne.
- La sonde de disponibilité ne prouve ni l'exhaustivité BOAMP, ni l'absence d'avis, ni la conformité d'une Affaire.

## 6. Plus petite preuve implémentée

1. Sonde réussie : `state=AVAILABLE`, `checked_at` présent et `last_success_at` issu du dernier run `RECORDED`.
2. Sonde en panne : `state=UNAVAILABLE`, anciennes observations inchangées et dernier succès visible ou nul ; aucune liste vide fabriquée.
3. Sonde non configurée : `state=UNKNOWN`, aucune prétention de fraîcheur.
4. Le panneau affiche la panne et propose **Relancer** et **Saisie manuelle**.
5. La saisie manuelle continue d'utiliser `POST /api/v1/cases` avec `origin_kind=MANUAL`, puis le rejeu conserve les mêmes identifiants.

La projection est maintenant codée dans le contrat fermé `BoampObservationListResponse.source_status`, la lecture du dernier succès est tenant-scopée dans `BoampQualificationRepository.last_successful_ingestion_at`, et le panneau réutilise `CreateCasePanel` pour l'entrée manuelle.

## 7. Critères de sortie

- Contrat Pydantic fermé et états `AVAILABLE`, `UNAVAILABLE` et `UNKNOWN` vérifiés par 3 tests ciblés.
- Dernier succès vérifié par requête PostgreSQL tenant-scopée ; la suite EXP-02 dédiée passe à 7 tests.
- Le test de projection conserve les observations antérieures et n'en fabrique pas une liste vide pendant une panne.
- Le test front affiche panne, dernier succès, relance et saisie manuelle ; le panneau ciblé passe à 6 tests et la suite complète à 148 tests.
- Le flux manuel reste `MANUAL` et idempotent via le contrat `CreateCase` déjà testé.
- `typecheck`, `lint`, build, Ruff ciblé et `git diff --check` passent.

## 8. Décision de tranche

Le code existant couvre la persistance et la création manuelle ; la tranche ajoute seulement la projection de santé de source et son accès UX. Une table de monitoring, un scheduler, une nouvelle dépendance ou une collecte automatique dans la route ne sont pas nécessaires à cette preuve.

**Prochaine étape :** clôturer EXP-02 par la revue des rôles, refus, responsive utile et critères de gel.
