# SMART AO — EXP-01 : reprise après interruption, preuve verticale minimale

**Statut :** PROTOTYPE EXÉCUTABLE ASSEMBLÉ — états difficiles parcourus, revue propriétaire suivante  
**Date :** 14 septembre 2026  
**Autorités :** cahier produit/métier OWNER v0.4, catalogue écrans/parcours OWNER v0.3, code et tests vivants.

## 1. Résultat attendu

Une interruption ne transforme jamais une opération en succès supposé. La personne voit le dernier état confirmé et peut vérifier ou rejouer l'intention avec la même clé d'idempotence. Aucune donnée locale n'est présentée comme enregistrée sans confirmation serveur.

## 2. Audit du code existant

| Sujet | État réel | Limite |
|---|---|---|
| Expiration de session | le résolveur serveur refuse la session expirée ; le client tente un rafraîchissement unique puis efface le jeton et l'acteur si celui-ci échoue ; l'interface conserve désormais le dernier contexte confirmé en mémoire | pas de persistance de brouillon, pas d'avertissement avant expiration ; le code applique actuellement 8 h d'inactivité et 24 h de durée absolue (12 h privilégiées), alors que le cahier v0.4 propose 30 min et 12 h |
| Création d'Affaire | la commande contient `command_id`, `idempotency_key` et `correlation_id` ; le serveur rejoue la même création sans doublon ; le front garde ces identifiants après une réponse perdue | le résultat inconnu est maintenant signalé « à vérifier » et rejoué explicitement ; la confirmation serveur reste obligatoire |
| Configuration interrompue | PAGE-004/PAGE-005 sont volontairement absentes : aucune donnée obligatoire n'est aujourd'hui demandée | aucun brouillon ne doit être créé artificiellement pour simuler une reprise |

## 3. Contrat de la première preuve exécutée

La tranche porte uniquement sur la création de première Affaire, où une commande idempotente existe déjà.

1. après un échec réseau ou une réponse non reçue, afficher **« Création à vérifier »**, jamais « Affaire créée » ;
2. conserver le formulaire et les trois identifiants de commande en mémoire ;
3. proposer **« Vérifier et réessayer »**, qui renvoie exactement la même intention ;
4. ne vider le formulaire et ne naviguer vers l'Accueil qu'après une réponse serveur confirmée, y compris une réponse rejouée ;
5. ne pas écrire ce formulaire dans `localStorage`, ne pas créer de table de brouillons et ne pas prétendre restaurer un état après fermeture ou changement d'identité.

La session expirée reste masquée par le garde serveur et entraîne une nouvelle authentification. La mise en conformité des durées, l'avertissement avant expiration et la persistance de brouillons forment une tranche distincte. La première preuve de reprise ne persiste donc aucun contenu : elle restaure uniquement le dernier contexte confirmé en mémoire, après concordance d'identité et rechargement serveur.

## 4. Preuves attendues

- une promesse de création rejetée laisse le formulaire visible et présente l'état « à vérifier » ;
- le rejeu conserve `command_id`, `idempotency_key` et `correlation_id` ;
- une réponse rejouée produit le même effet qu'une réponse créée : Affaire confirmée, formulaire vidé et navigation autorisée ;
- aucune notification de succès n'apparaît avant cette réponse ;
- une session expirée est refusée par le serveur, l'accès métier est masqué et le contexte navigateur est supprimé lorsque le rafraîchissement échoue ; le dernier contexte confirmé reste conservé uniquement en mémoire pour une reprise contrôlée.

## 5. Décisions volontairement différées

- persistance chiffrée et bornée du travail local ;
- persistance de brouillons et reprise après fermeture ou changement d'appareil ;
- avertissement à deux minutes et alignement des paramètres de session sur la décision produit ;
- parcours PAGE-004/PAGE-005, qui ne doivent exister que lorsqu'une donnée réellement obligatoire apparaît.

## 6. Preuve exécutée

La preuve minimale est maintenant codée dans `web/src/features/cases/CreateCasePanel.tsx`.

- une erreur sans statut HTTP (réponse perdue ou réseau interrompu) affiche **« Création à vérifier »** et ne présente aucun succès ;
- le formulaire reste visible et conserve `command_id`, `idempotency_key` et `correlation_id` en mémoire ;
- **« Vérifier et réessayer »** rejoue la même intention avec les mêmes identifiants ;
- une réponse serveur confirmée, y compris `replayed: true`, seule vide le formulaire et permet la navigation ;
- les erreurs HTTP connues restent des erreurs connues et ne sont pas requalifiées en résultat inconnu.

Les tests `CreateCasePanel` et `App` couvrent le message d'incertitude, l'absence de succès présumé et l'égalité des identifiants au rejeu. La suite ciblée passe avec 28 tests et le build TypeScript/Vite passe.

## 7. Preuve exécutée de reprise de session

La reprise minimale est maintenant codée sans nouveau stockage ni dépendance.

- quand une requête métier reçoit `401` et que le rafraîchissement unique échoue, `useAuthentication` efface le jeton et l'acteur puis expose `sessionExpired` ;
- `App` masque immédiatement les données métier et affiche un message générique d'expiration, sans révéler d'Affaire ni de contenu ;
- avant l'expiration, `App` mémorise seulement `identity_id`, `tenant_slug`, `actor_kind`, l'Affaire sélectionnée et la navigation du dernier état confirmé ;
- après reconnexion et MFA, la confirmation de PAGE-003 ne restaure l'Affaire et la navigation que si l'identité, le tenant et le rôle correspondent au snapshot ;
- le bandeau de reprise reste visible jusqu'au succès de `refreshCases`, qui est la preuve de fraîcheur des données ; une erreur de rechargement ne devient jamais une confirmation ;
- une autre identité ou un autre rôle invalide le snapshot et ne récupère aucune donnée de la session précédente.

Les tests front ciblés de cette preuve couvrent l'expiration non récupérable, le masquage, la confirmation du même contexte, l'invalidation après changement de rôle et le maintien du bandeau tant que le rechargement échoue. Ils passent avec 35 tests ciblés ; le build et ESLint passent également.

## 8. Preuve exécutable EXP-01 et états difficiles parcourus

La preuve reproductible est volontairement composée des suites déjà présentes : aucune nouvelle dépendance ni lanceur parallèle n'est ajouté.

```text
cd web
npm test -- --run --maxWorkers=1
npm run build
npm run lint
cd ..
uv run --extra calendar pytest -m 'not db' --no-cov \
  backend/tests/api/test_auth_dependency.py \
  backend/tests/api/test_case_creation_api.py \
  backend/tests/application/test_case_creation.py \
  backend/tests/domain/case/test_case_creation.py \
  backend/tests/security/test_actor_context_authorization.py \
  backend/tests/security/test_totp.py
git diff --check
```

| État difficile | Comportement vérifié | Preuve |
|---|---|---|
| aucune session | seule la connexion est rendue ; aucune Affaire ni action métier n'est visible | `App.test.tsx` |
| session `PASSWORD` sans MFA | écran MFA exclusif ; les routes métier restent refusées par `STEP_UP_REQUIRED` | `App.test.tsx`, garde HTTP et preuves PostgreSQL antérieures |
| `401` puis refresh refusé | jeton et acteur effacés, message générique, données métier masquées | `useAuthentication.test.tsx`, `App.test.tsx` |
| réauthentification du même acteur | contexte confirmé, snapshot repris seulement après rechargement serveur ; échec de reload conservé comme erreur | `App.test.tsx` |
| rôle différent à la reprise | snapshot invalidé, état local vidé, aucune Affaire de l'ancien rôle affichée | `App.test.tsx` |
| création à résultat inconnu | formulaire et identifiants conservés, « Création à vérifier », rejeu identique, aucun succès présumé | `CreateCasePanel.test.tsx`, `App.test.tsx` |
| erreur HTTP connue / absence 404 | erreur connue visible ; absence de dossier 404 silencieuse | `App.test.tsx` |
| espace collaborateur | surfaces Patron, opportunités et dépôt absentes | `App.test.tsx` |
| bearer malformé ou contexte sans MFA | `401`/`403` avant tout service métier | tests API backend ciblés |

Résultats de la session du 14 septembre 2026 : **31 fichiers et 141 tests front passent** ; le sous-ensemble backend EXP-01 passe avec **31 tests** ; build, ESLint et `git diff --check` passent. La suite backend non-DB complète passe à **1 144 tests**, avec **2 échecs historiques ops** (head/schema et guide préproduction déplacé par la réorganisation documentaire) et **2 tests d'extraction ignorés** faute de PIL. Ces quatre résultats ne touchent pas le parcours EXP-01 et restent à traiter dans la qualification d'exploitation.

Les preuves PostgreSQL déjà exécutées pour l'invitation, la récupération, les profils et la création idempotente restent valides ; elles n'ont pas été relancées ici car le conteneur PostgreSQL n'est pas démarré dans l'environnement courant.
