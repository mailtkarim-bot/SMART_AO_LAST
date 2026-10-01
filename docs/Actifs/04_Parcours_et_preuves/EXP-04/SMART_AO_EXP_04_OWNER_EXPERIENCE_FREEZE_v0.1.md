# SMART AO — EXP-04 : OWNER EXPERIENCE FREEZE

**Statut :** GEL D’EXPÉRIENCE DÉLÉGUÉ · PREUVES EXÉCUTÉES · COUVERTURE `PARTIAL` ASSUMÉE  
**Date :** 15 septembre 2026  
**Autorité :** délégation propriétaire explicite reçue dans le fil Codex  
**Références :** cahier OWNER v0.4, catalogue OWNER_CONSOLIDATED v0.3 et cadrage [`SMART_AO_EXP_04_POINTS_BLOQUANTS_SOURCES_ACTIONS_AUDIT_CADRAGE_v0.1.md`](SMART_AO_EXP_04_POINTS_BLOQUANTS_SOURCES_ACTIONS_AUDIT_CADRAGE_v0.1.md)

## 1. Périmètre gelé

EXP-04 couvre une lecture Case « À résoudre » calculée à partir des agrégats existants :

```text
exigence DCE ouverte / demande d'information ouverte / bloqueur ouvert
  → lecture Patron ou Collaborateur selon tenant et affectation
  → risques, contradictions et inconnus BOAMP visibles dans leur périmètre autorisé
  → source, état natif, action et attributs réellement disponibles
```

La vue reste read-only et `coverage=PARTIAL`. Elle ne crée pas un nouvel état métier et ne remplace aucun cycle natif.

## 2. Arbitrages gelés

| Sujet | Décision |
|---|---|
| Autorité | Le serveur détermine tenant, rôle, MFA, capacité et affectation ; aucune valeur de contexte fournie par le navigateur ne fait foi. |
| Patron | `PATRON_ADMIN` peut lire les éléments de son tenant, y compris risques, contradictions et inconnus BOAMP rattachés à une Affaire `OPPORTUNITY`. |
| Responsable / Expert | Ce sont des profils opérationnels de `COLLABORATEUR` ; ils gardent le même périmètre et doivent avoir une affectation active. |
| MFA | Une session `PASSWORD` sans MFA reçoit `403 STEP_UP_REQUIRED` avant toute projection métier. |
| États | `PENDING_HUMAN_CONFIRMATION`, `REVIEW_REQUIRED`, `OPEN` et `UNKNOWN` restent visibles dans leur état natif ; aucune résolution implicite n'est faite. |
| Sources | Chaque ligne conserve ses identifiants et locators ; l'inconnu BOAMP est rattaché par `origin_reference_id` et identité déterministe. |
| Attributs incomplets | `impact`, `resolution_owner` et `due_at` sont propagés uniquement lorsqu'une source les porte. L'échéance d'un bloqueur vient de sa tâche liée ; une absence reste `null`. |
| Concurrence | Les commandes natives gardent `expected_revision` et verrouillent la tâche ; une révision périmée est refusée par `VERSION_CONFLICT`. |
| Questions et validations | Une demande d'information est seulement référencée dans la projection ; aucun envoi autonome. `RecordTaskResult` reste distinct de la validation DCE et l'achèvement exige un résultat admissible. |
| Actions | La lecture propose les commandes existantes (`CONFIRM_REQUIREMENT`, `REVIEW_REQUIREMENT`, `RESPOND_INFORMATION_REQUEST`, `RESOLVE_TASK_BLOCKER`, `REVIEW_RISK`, `REVIEW_CONTRADICTION`) ; aucun `resolve-all`, score ou acte IA n'est ajouté. |

## 3. Refus et états difficiles prouvés

- absence de bearer : `401` ;
- session `PASSWORD` sans MFA : `403 STEP_UP_REQUIRED` ;
- Collaborateur sans affectation active : `403` ;
- tenant ou Affaire inexistante : `404 NOT_FOUND_OR_FORBIDDEN` neutre ;
- Collaborateur : exigences et tâches de son affectation seulement ; risques, contradictions et inconnus Patron-only absents ;
- exigence `REVIEW_REQUIRED`, risque, contradiction ou inconnu `UNKNOWN` : revue explicite sans clôture ;
- résultat de tâche absent ou révision périmée : achèvement/refus contrôlés par les commandes natives ;
- impact, responsable ou échéance absents : `null`, sans déduction.

## 4. Preuves exécutées

- projection applicative : inconnus BOAMP, risques, contradictions, états natifs et échéance de tâche liée ;
- HTTP PostgreSQL : Patron, Collaborateur affecté, Collaborateur non affecté, Affaire inconnue et session sans MFA ;
- concurrence et validation : révision périmée, achèvement sans résultat et état non complétable.

Les preuves ciblées totalisent **7 tests PostgreSQL passés** sur `smart-ao-v8-postgres:5433` après la propagation d'échéance, plus les contrôles mypy, Ruff et `git diff --check`.

## 5. Limites assumées

La projection ne dispose pas encore d'un champ d'impact textuel pour les exigences, risques ou contradictions qui n'en portent pas ; elle laisse donc `null`. Les noms individuels ne sont pas inventés à partir d'un UUID de membership. Une couverture complète, une vue de détail et les contributions multi-utilisateurs restent des extensions séparées.

## 6. Effet du gel

EXP-04 peut avancer sans rouvrir les garanties de tenant, MFA, affectation, provenance, concurrence et séparation des validations. Toute extension doit rester additive, conserver `coverage=PARTIAL` tant que les sources manquent, et être reliée à une nouvelle preuve.

**Prochaine étape :** auditer puis cadrer EXP-05 sur les réponses et prix validables, en réutilisant les contrats de provenance et de rôle déjà prouvés.
