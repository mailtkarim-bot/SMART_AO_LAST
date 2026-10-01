# SMART AO — EXP-04 — Points bloquants, sources et actions — audit/cadrage v0.1

**Statut : PROJECTION READ-ONLY ÉTENDUE ET TESTÉE · COUVERTURE PARTIELLE**  
**Autorité :** cahier produit/métier OWNER_CONSOLIDATED v0.4  
**Périmètre :** rendre les points de progression visibles sans fusionner exigences, inconnues, contradictions, risques et tâches

## 1. Question métier

Pour une Affaire donnée, l'équipe doit savoir ce qui empêche la prochaine porte, quelle source le prouve, qui peut agir et quelle sortie est autorisée. « À résoudre » est une lecture transversale ; ce n'est pas un nouvel état métier qui écrase les états natifs.

## 2. Code et contrats déjà disponibles

| Famille | Source actuelle | État / action existante |
|---|---|---|
| Exigence DCE | `GET /api/v1/cases/{case_id}/dce-reading` et `DceRequirementRecord` | `PENDING`, `CONFIRMED`, `REVIEW_REQUIRED`, `NOT_APPLICABLE` ; confirmation humaine via `dce.requirement.confirm` |
| Demande d'information | `/api/v1/collaborator/tasks/{task_id}/information-requests` | `OPEN`, `ANSWERED`, `CLOSED`, `CANCELLED` ; réponse versionnée avec source facultative |
| Bloqueur de tâche | `/api/v1/collaborator/tasks/{task_id}/blockers` | `OPEN`, `RESOLVED` ; résolution versionnée et affectation explicite |
| Contradiction / risque | lecteurs et routes décision Patron existants | lecture séparée, aucune clôture générique ; décisions et risques gardent leur propre cycle |
| Inconnu BOAMP | projection Fiche Opportunité | `UNKNOWN` et action suivante visibles avant ouverture d'Affaire |

Le code confirme qu'il existe déjà des preuves de tenant, d'affectation, de version, d'idempotence, d'audit et de masquage financier. Aucun stockage « blocker » universel ne doit être ajouté pour remplacer ces agrégats.

## 3. Écart constaté

Il n'existe pas encore de lecture Case unique qui rassemble les éléments ouverts provenant de ces sources. Les écrans actuels savent lire et traiter leurs objets d'origine, mais une personne doit ouvrir plusieurs surfaces pour répondre à « qu'est-ce qui bloque maintenant ? ». Cette absence ne justifie pas de fusionner les données ni de déduire une priorité opaque.

## 4. Contrat minimal de la preuve

La première projection unifiée sera **read-only**, tenant-scoped et calculée depuis les lecteurs existants. Chaque ligne conservera :

- `item_id` et `item_kind` (`REQUIREMENT`, `INFORMATION_REQUEST`, `TASK_BLOCKER`, `CONTRADICTION`, `RISK`, `UNKNOWN`) ;
- `native_state`, sans conversion silencieuse en « résolu » ;
- `source_refs` vers l'agrégat ou le locator d'origine ;
- `resolution_owner` lorsqu'il est déjà connu ;
- `next_action` limitée à une action existante ou à `REVIEW_REQUIRED` ;
- échéance seulement si la source la porte ; sinon l'absence reste explicite.
- `impact` seulement lorsqu'il est déjà porté par la source ; sinon `null` reste explicite.

La projection ne donnera aucun pouvoir supplémentaire. Les actes restent les commandes natives : confirmer une exigence, répondre à une demande, déclarer/résoudre un bloqueur, revoir un risque ou traiter une contradiction. Il n'y aura pas de `POST /resolve-all`, de score de priorité, de fusion d'historique ni de clôture IA.

## 5. Règles de rôle et confidentialité

- `PATRON_ADMIN` peut voir les éléments autorisés par les lecteurs décisionnels ; marge, trésorerie et notes Direction restent absentes des lignes opérationnelles.
- `COLLABORATEUR` ne voit que les tâches et cas couverts par son affectation et son périmètre ; Responsable et Expert restent des profils opérationnels.
- Toute ressource d'un autre tenant ou hors affectation produit une réponse neutre sans existence révélée.
- L'IA peut proposer une source ou une question, jamais fermer, accepter ou envoyer.
- Une liste vide signifie « aucun élément dans le périmètre lu » ; elle ne signifie pas que l'Affaire est sans risque lorsque la couverture est partielle.

## 6. Cas de preuve retenu

Le premier vertical sera limité à une Affaire avec :

1. une exigence DCE `PENDING` reliée à son locator ;
2. un bloqueur de tâche `OPEN` relié à sa tâche et à son responsable ;
3. une réponse `ANSWERED` qui reste historique et n'efface pas l'exigence ;
4. une lecture par Patron, par Collaborateur affecté et par Collaborateur non affecté ;
5. un autre tenant, un état `REVIEW_REQUIRED` et une échéance absente.

Cette coupe prouvera la valeur de la vue sans inventer encore les contrats complets de contradictions, risques financiers ou décisions P2/P3.

## 7. Limites et décisions

- Les modèles d'inconnus, contradictions et risques restent des sources indépendantes jusqu'à leur propre preuve de lecture.
- Le code actuel ne transporte pas toujours un responsable sur les exigences DCE ; la projection affichera l'absence au lieu d'inventer un nom.
- La priorisation temporelle et la vue mobile viennent après la projection fermée.
- Aucun package ou service externe n'est nécessaire.

## 8. Première preuve implémentée

La route `GET /api/v1/cases/{case_id}/resolution` expose une projection fermée avec `coverage=PARTIAL`. Elle réutilise `SqlAlchemyCaseDceReadingReader` pour les exigences DCE et lit les registres membership existants pour les demandes d'information `OPEN` et les bloqueurs `OPEN`. Une réponse `ANSWERED` n'est pas transformée en blocage ouvert et reste consultable dans le workflow historique de sa tâche.

Les collaborateurs ne voient que les tâches rattachées à leur affectation active ; le Patron lit les tâches de son tenant. L'autorisation reste celle du serveur (`WORK_TASK_READ` pour un collaborateur, `CASE_DCE_READ` pour un Patron) et une autre tenant ou une Affaire inexistante répond de façon neutre. Les lignes ne contiennent ni description de tâche, ni texte de réponse, ni données financières.

## 9. Rôles et états difficiles parcourus

La preuve HTTP couvre les trois situations utiles de cette coupe : un Collaborateur affecté obtient l'index, un Patron du même tenant obtient l'index complet de son tenant, et un Collaborateur actif sans affectation reçoit `403` sans projection. La preuve applicative force une exigence à `REVIEW_REQUIRED` et vérifie que l'action suivante devient `REVIEW_REQUIREMENT` sans la convertir en résolution. Responsable et Expert restent les profils opérationnels déjà portés par `COLLABORATEUR` ; aucune capacité supplémentaire n'est créée par cette lecture.

## 10. Risques et contradictions conservés séparément

Pour un Patron, la projection réutilise les lecteurs déjà présents des signaux de risque CCAP/CCTP et des contradictions déterministes CCTP–DPGF/BPU. Ils deviennent respectivement `RISK` et `CONTRADICTION`, gardent `REVIEW_REQUIRED`, leurs identifiants et leurs localisations, et proposent seulement `REVIEW_RISK` ou `REVIEW_CONTRADICTION`. Aucun de ces éléments n'est visible dans le périmètre d'un Collaborateur, et aucune décision de traitement n'est déclenchée par la lecture. Les inconnus BOAMP restent dans leur projection d'opportunité jusqu'à une preuve de rattachement Case dédiée.

## 11. Inconnus BOAMP rattachés à l'Affaire

Pour une Affaire d'origine `OPPORTUNITY`, la projection relit l'observation BOAMP référencée par `CaseRecord.origin_reference_id` et reprend les inconnus déjà calculés par le flux de qualification. Chaque code devient une ligne `UNKNOWN` avec une identité déterministe, l'observation et l'avis BOAMP comme sources, l'état `UNKNOWN`, l'impact textuel existant et l'action textuelle existante. La lecture ne crée ni résolution implicite ni échéance inventée ; une Affaire manuelle ne reçoit aucune ligne BOAMP.

## 12. Contrat explicite des attributs incomplets

Le contrat ajoute `impact` comme champ nullable. Il est renseigné uniquement lorsqu'une source fournit déjà un impact textuel ; il reste `null` pour les exigences, demandes, risques ou contradictions qui ne transportent pas cet attribut dans leur projection actuelle. `resolution_owner` et `due_at` suivent la même règle : le responsable du bloqueur vient du bloqueur lui-même, et son `due_at` vient de la tâche liée ; une valeur absente reste absente. Cette forme permet de relier les attributs sans transformer une absence de preuve en information métier.

## 13. Concurrence, questions et validations

Les contributions concurrentes restent protégées par la révision attendue et le verrouillage de la tâche (`with_for_update`) : une seconde commande avec une révision périmée reçoit `VERSION_CONFLICT` et ne peut pas écraser le premier état. Les demandes d'information sont des commandes explicites du workflow Collaborateur ; la projection les référence par tâche et demande, sans envoyer de question ni déclencher d'action autonome. Enfin, `RecordTaskResult` reste un résultat opérationnel append-only distinct de la confirmation DCE et de l'achèvement : une tâche ne peut être complétée sans résultat admissible, et un résultat n'est jamais interprété comme une validation métier.

## Vérification exécutée

- Projection Case : **3 tests applicatifs + 2 tests API PostgreSQL** passent, dont les signaux `RISK`/`CONTRADICTION`, les inconnus BOAMP rattachés, la propagation de `impact` et l'échéance de la tâche liée au bloqueur.
- Concurrence et séparation des validations : **3 tests PostgreSQL ciblés** passent pour les révisions périmées, le refus d'achèvement sans résultat et les états non complétables.
- Contrats de commande et route workflow Collaborateur : **3 tests commande + 3 tests architecture** passent.
- Workflow PostgreSQL demandes/bloqueurs et API de tâche : **9 tests passent** sur le conteneur dédié.
- Autorisation DCE, tenant, affectation, projection et risques : **24 tests passent** sur PostgreSQL dédié.
- Harnais Golden : **17 tests passent**, manifeste exemple valide mais vide (`documents=0`).

## Étape suivante

Le gel d'expérience est consigné dans [`SMART_AO_EXP_04_OWNER_EXPERIENCE_FREEZE_v0.1.md`](SMART_AO_EXP_04_OWNER_EXPERIENCE_FREEZE_v0.1.md). La tranche suivante peut auditer EXP-05 sur les réponses et prix validables sans rouvrir les garanties EXP-04.
