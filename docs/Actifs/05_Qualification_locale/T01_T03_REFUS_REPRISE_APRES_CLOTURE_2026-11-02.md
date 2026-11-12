# T01–T03 — Refus et reprise après rectificatif et clôture — 02/11/2026

Le plan global conserve seul le statut. Périmètre exclusivement local synthétique ; aucun effet externe ni GO public.

## AS-IS, risques et plan minimal

La recette intégrée L11 produit sur une Affaire le pli rectifié, la passation V2, les changements, les nouvelles déclarations de clôture et une sortie avec deux réserves encore ouvertes. Elle prouve le replay nominal ; elle ne distingue pas une indisponibilité avant écriture d’une perte de réponse après commit.

Risques : divulguer une existence étrangère par une erreur, confondre un UNKNOWN avec un échec sans effet, doubler l’effet lors du retry, réécrire l’historique lors du premier effet réussi ou transférer un accord ancien.

Insertion minimale : callback optionnel de qualification en fin de recette `backend/tests/db/test_l11_v2_closure.py` ; nouveau scénario `backend/tests/db/test_transversal_rectified_closure_recovery.py`. Aucun code applicatif, UI, droit, porte, modèle, migration ou dépendance modifié.

Plan : réutiliser la chaîne Markdown et l’application exacte ; éprouver les refus avant tout nouvel effet ; injecter deux indisponibilités au service applicatif ; reconnecter un client et rejouer le même corps/IDs ; comparer état durable, faits financiers et manques ; exécuter revue, tests et contrôles avant bilan.

Autorités : PF31-08 (déclarations distinctes), M31-07/R31-07–08 (retry inconnu, isolation), CT31-04 (invalidation/historique).

## Contrats vérifiés par le scénario

- Même Patron authentifié face à une Affaire d’un autre tenant ou un identifiant inexistant : GET et POST retournent le même 404 générique, sans source ni compteur.
- Absence d’authentification : 401 ; Collaborateur : 403 ; aucun nouvel effet de clôture.
- Indisponibilité avant appel du service réel : 503 RESULT_UNKNOWN, état métier identique ; retry avec corps et IDs identiques crée un acte puis replay sans nouvel effet.
- Indisponibilité après retour du dispatch réel : 503 RESULT_UNKNOWN alors que l’acte est enregistré ; reconnexion sur la même application et retry identique retourne le reçu avec replayed=true.
- L’unique acte ajouté correspond exactement à act_id. Tous les actes antérieurs, réserves, faits, cycles et transitions restent identiques après le premier effet réussi, puis les retries. Les compteurs d’événements/outbox du tenant ne croissent pas lors des retries.
- Réserves toujours ouvertes et montants historiques inchangés ; solde, effet juridique et reçu externe UNKNOWN. Aucun acquittement ni droit nouveau déduit d’une reprise réussie.

## Limites à conserver

Les pannes sont injectées au niveau de `CaseClosureService.record`, avant délégation ou après commit ; elles ne simulent pas une panne TCP/PostgreSQL, une transaction tuée pendant commit ou un redémarrage applicatif. La reconnexion crée un client HTTP sur la même application locale. Événements/outbox : comparaison des compteurs tenant, pas du contenu ni de leur livraison. Les lignes métier sont comparées dans le tenant/Affaire ; les données de l’autre tenant ne sont jamais renvoyées par HTTP.

L’invalidation supplémentaire de passation reste injectée SQL dans la recette L11, sans nouvelle publication P7 publique démontrée. Les nouvelles sources sont déclarées synthétiques, non authentifiées. Variante DOCX, corpus réel, navigateur intégré, concurrence réseau et longues suites globales : non relancés. Aucune exhaustivité ni conformité juridique/technique déduite.

## Revue et incidents de harnais

Revue read-only indépendante : renforcer le contrôle du premier effet, pas seulement celui des retries. Assertion ajoutée sur les anciennes lignes intactes et l’unique nouvel act_id ; contre-revue sans nouveau défaut P1/P2 identifié. Ceci ne remplace ni DB ni accord humain.

Deux lancements interrompus volontairement (18,78 s puis 90,56 s) : correction de la largeur du marqueur de fixture et ajout des assertions demandées par la revue. Ils ne sont ni des tests réussis ni des échecs produit. Un diagnostic mypy de liste non annotée a été corrigé. Les résultats retenus sont ceux du rejeu final gelé par SHA-256.

## Méthode et outils

Superpowers using-superpowers, brainstorming borné, writing-plans, requesting-code-review et verification-before-completion ; ECC verification-loop et security-review ciblés. Qualification d’un comportement existant : aucun rouge produit artificiel ni code de production modifié. Graphify interrogé avant exploration ; Basic Memory miroir du plan. Pas de nouvelle API de bibliothèque : Context7 non requis ; pas de besoin de navigation sémantique Serena, Jev ou Manus. Aucun changement UI : OpenDesign/Impeccable non applicables ; tests du composant existant, pas de nouveau résultat navigateur/Playwright.

## Résultats

Rejeu intégré Markdown final : **1 test passe en 206,86 s, exit 0**, avertissement Starlette/httpx existant. `native-reviewed/recovery.json` conserve les deux reçus : première reprise 201/replayed=false, seconde 200/replayed=true ; `final.json` conserve le dossier après reprise. Les hashes des sources testées ont été relus après exécution.

Régressions SQL/application : **18 passent en 13,17 s**, dont HTTP/rôle/tenant/MFA, concurrence native de paiement, refus de downgrade non vide, historique et REX/réemploi dédiés. Les **13 unitaires** initiaux en 1,03 s sont inclus dans cette campagne de 18, pas des tests supplémentaires.

Composant Web existant : **7 passent**, durée totale 5,85 s, dont gel UNKNOWN et retry identique ; pas une preuve navigateur ni une connexion E2E composant→API. Mypy app **703 sources vertes**, deux fichiers de recette verts ; Ruff ciblé et diff whitespace vérifiés. Semgrep 1.183.0 après tests : 2 fichiers, 79 règles p/security-audit, 0 finding et 0 erreur. Métriques désactivées ; aucun résultat envoyé à un service distant.

**Décision : qualification locale bornée des refus et de la reprise acquise ; T01–T03 général reste PARTIAL.** Les garanties globales, le redémarrage, les pannes réelles et le navigateur restent non démontrés. Deux réserves restent ouvertes, solde UNKNOWN ; aucune activation, porte, conformité, livraison d’outbox, dépôt, effet externe ou GO public déduit.

Reçus privés et sources gelées : `/home/noor/.local/share/smartao-proofs/t01-t03-recovery-20261102/`. Aucun reset/clean/stash, nouveau checkout, staging, commit ou push.
