# SMART AO — EXP-03 : OWNER EXPERIENCE FREEZE

**Statut :** GEL D’EXPÉRIENCE DÉLÉGUÉ · PREUVES EXÉCUTÉES · GOLDEN RÉEL À QUALIFIER  
**Date :** 15 septembre 2026  
**Autorité :** délégation propriétaire explicite reçue dans le fil Codex  
**Références :** cahier OWNER v0.4 et catalogue OWNER_CONSOLIDATED v0.3

## 1. Périmètre gelé

EXP-03 couvre le chemin suivant :

```text
intention d’upload DCE
  → flux borné, quarantaine privée et antivirus fail-closed
  → inventaire par fichier et extraction native sourcée
  → classification partielle et revue humaine des inconnus
  → rectificatif versionné avec impact conservateur
  → lecture manuelle maintenue si l’IA est indisponible
```

La voie manuelle est la voie de continuité normative. L'assistance IA ne conditionne ni l'accès aux sources ni une décision métier.

## 2. Arbitrages gelés

| Sujet | Décision |
|---|---|
| Autorité technique | Le serveur calcule le tenant, les capacités, l'affectation et la version DCE ; un rôle, un tenant ou un chemin de stockage fournis par le navigateur ne font jamais autorité. |
| Patron | `PATRON_ADMIN` peut préparer/lire le DCE et confirmer une exigence selon les capacités serveur ; les données privées restent filtrées par contrat. |
| Responsable / Expert | Ce sont des profils opérationnels de `COLLABORATEUR`. Ils conservent les mêmes capacités de base et doivent avoir une affectation et un périmètre explicites pour lire ou confirmer. |
| Délégation | `PATRON_DELEGATE` ne reçoit que les capacités présentes dans la liste délégable ; toute autre capacité est refusée par défaut. |
| Refus | Absence de bearer : `401`; tenant ou ressource étrangère : `404 NOT_FOUND_OR_FORBIDDEN`; absence d'affectation ou d'action de périmètre : `403` audité. |
| Contenu hostile | Un texte importé ne devient jamais une commande. Les motifs suspects produisent `REVIEW_REQUIRED` et `HOSTILE_INSTRUCTION_REVIEW_REQUIRED`, sans appel externe ni mutation. |
| Panne IA | `503 KNOWLEDGE_RETRIEVAL_UNAVAILABLE` est visible ; la lecture des sources, l'inventaire, les ancres et les confirmations humaines restent disponibles. |
| Complétude | Une pièce absente, protégée, illisible, non classifiée ou à revoir empêche la synthèse d'être présentée comme complète. |
| Rectificatif | Nouvelle version, ancien corpus `SUPERSEDED`, ledger append-only et revue ciblée des dépendances ; aucune conclusion indépendante n'est réécrite. |
| Golden | Le harnais et son manifeste sont qualifiés par tests. Le manifeste de dépôt contient zéro document : aucun rappel, score ou résultat de compréhension réel n'est déclaré. |

## 3. Refus et états difficiles prouvés

- le Patron lit une projection fermée et ne reçoit ni texte intégral, ni chemin privé, ni provenance URL non autorisée ;
- un Collaborateur sans affectation, sans action `case.dce.read` ou hors tenant est refusé, avec audit et réponse neutre ;
- un Collaborateur ne peut pas déclarer une exigence `NOT_APPLICABLE`, acte réservé au Patron ;
- la préparation, l'admission et l'upload DCE utilisent le contexte serveur et refusent l'objet client arbitraire ;
- un PDF protégé, une limite dépassée ou une lecture échouée restent visibles par état, sans fragment présenté comme lu ;
- un rectificatif conserve l'historique et force la revue des dépendances ;
- un texte qui demande d'ignorer les règles, de révéler un secret ou d'envoyer vers une URL reste à revoir ;
- une indisponibilité de récupération vide les résultats et conserve le parcours de lecture manuelle.

## 4. Bancs Golden

Le parser du manifeste et le benchmark de recherche sont exécutables et rejettent les chemins, doublons, champs sensibles, classifications financières et données non anonymisées. `manifest.example.json` est volontairement vide (`documents=0`) : les droits, l'anonymisation, la double revue et les désaccords sur un corpus métier réel restent à établir avant toute utilisation de gel qualité ou de mesure de rappel.

## 5. Preuves et limites

- Autorisation DCE/tenant/affectation : **9 tests API** DCE et **9 tests API** confirmation/lecture passent sur PostgreSQL dédié.
- Capacités, profils Responsable/Expert, projection fermée et risques : **24 tests** passent sur PostgreSQL dédié.
- Harnais Golden : **17 tests** passent ; manifeste exemple validé avec `documents=0`.
- Extraction hostile et native : **13 tests** passent ; knowledge : **30 tests passent, 2 tests image ignorés** faute de `PIL` optionnel.
- Front IA/manuelle : **9 tests** passent ; `npm run typecheck`, `npm run lint`, `npm run build`, Ruff ciblé et `git diff --check` passent.
- La suite historique Starlette/httpx `TestClient` reste limitée par l'environnement et n'est pas déclarée verte.

Les limites assumées sont la détection hostile heuristique, l'absence de corpus Golden réel et l'absence de LLM distant ou d'OCR obligatoire. Ces limites empêchent une promesse de qualité documentaire totale, mais ne bloquent pas la sécurité, la traçabilité et la continuité manuelle prouvées ici.

## 6. Effet du gel

EXP-03 peut avancer vers EXP-04 sans rouvrir ces arbitrages de sécurité et de continuité. Toute extension doit rester additive, versionnée et reliée à une preuve. Le prochain travail produit porte sur les points bloquants et leurs sources ; la qualification Golden réelle demeure une condition de la couverture de non-régression, pas une raison pour masquer l'état actuel.

**Prochaine étape :** ouvrir EXP-04 par l’audit des points bloquants, de leurs sources et des actions autorisées.
