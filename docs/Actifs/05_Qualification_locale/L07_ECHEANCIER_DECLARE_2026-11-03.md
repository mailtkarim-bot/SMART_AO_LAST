# L07 — Échéancier de trésorerie déclaré par Affaire — 2–3 novembre 2026

Le plan global reste l’unique statut opérationnel. Parcours exclusivement local synthétique ; aucune liquidité, capacité de financement, échéance juridique, agrégation portefeuille ou porte déduite.

## Résultat et cadrage

Le Patron peut saisir des flux datés et des soldes de départ par devise, avec sources et hypothèses, relire leur cumul déclaré, puis modifier, retirer ou annuler dans une nouvelle révision. L’historique et les actes humains restent conservés. Une source changée rend l’ancienne déclaration REVIEW_REQUIRED et masque ses cumuls courants. Une absence n’est jamais remplacée par zéro.

AS-IS : le CASH existant expose rapports/réserves et un solde déclaré sans échéancier. Les lignes financières n’ont pas de date métier de flux ; les faits de paiement L11 sont des déclarations, pas un calendrier juridique. Aucun registre natif ne porte la déclaration datée révisionnée de ce parcours.

RISQUES : prix de vente pris pour coût, paiement attendu additionné à son encaissement, source étrangère, date déplacée sans relecture, zéro implicite, montant imprécis, double effet après UNKNOWN, historique réécrit.

INSERTION : contexte pricing, autorisation financière Patron existante, dispatcher/reçus natifs, verrou Affaire et garde de version. Un registre append-only de révisions porte le document déclaré ; aucune nouvelle comptabilité, aucun nouveau solveur. UI intégrée au même espace Affaire, composants/styles existants.

PLAN suivi : rouges purs/API/UI → minimum domaine et registre/API → interface confirmée → refus/concurrence/reprise/sources → recette navigateur native locale → régressions/qualité/sécurité et conservation. Autorités PF31-08/09, M31-02/M2-026 axes7/8, CT31-02/04/06/07 et contrat du bilan local.

## Contrat métier

- Période déclarée bornée, jusqu’à 8 devises, 120 flux, 12 références par flux/solde ; aucune conversion. Solde initial signé et zéro explicites, date/montant manquants visibles. L’absence d’une date ou d’un montant dans une devise rend son cumul indisponible.
- Calcul entier exact ; résultats monétaires sérialisés en chaînes décimales pour rester exacts au-delà de la précision entière JavaScript. Les entrées sont des entiers stricts bornés, pas des flottants.
- Le cumul ne porte que sur les flux et hypothèses déclarés. Complétude PARTIAL, solde réel/financement/effet juridique UNKNOWN, même si toutes les cases du formulaire sont remplies. Les montants et dates restent déclaratifs.
- Sources manuelles référencées : aucune authenticité ni lecture binaire présumée. Sources natives facultatives sélectionnées : faits attendus/encaissements L11 ou lignes du dernier rapport publié, avec identifiants et empreintes exacts. Une vente est une entrée, un coût une sortie ; marge et solde agrégé ne deviennent pas un flux.
- Même chaîne paiement attendu/encaissement : double sélection refusée. Montant, devise et sens doivent correspondre à la source sélectionnée. Une date native disponible est reprise et contrôlée ; une autre hypothèse relève d’une déclaration manuelle distincte, pas d’une réécriture du fait.
- Nouvelle source/portée DCE/contrat/rapport : relecture requise ; nouvelle révision motivée et confirmée, aucun consentement transféré. Annulation par nouvelle révision, sans DELETE.
- Patron, PRICING_READ/WRITE et autorisation FINANCIAL_PRIVATE existantes ; MFA native. GET/POST no-store, refus génériques, comparaison tenant/Affaire avant restitution. L’identifiant de révision est tenant-scoped, y compris sa clé primaire, pour éviter une différence observable avec un UUID d’un autre tenant.
- Révision attendue et hash de vue exacts, validation transactionnelle sous verrou CASE ; requêtes concurrentes 201/409. UNKNOWN fige l’intention, les identifiants et le formulaire ; retry strictement identique. Relecture après reçu ou conflit, absence de faux succès sur reçu discordant.

## Fichiers concernés

- `backend/app/modules/pricing/domain/cash_schedule.py` : déclaration validée et projection pure.
- `backend/app/modules/pricing/public/cash_schedule_contracts.py` : commande fermée, version/hash et consentement.
- `backend/app/modules/pricing/infrastructure/cash_schedule.py` et `models/cash_schedule.py` : sélection native, historique, invalidation, transaction et registre.
- `backend/app/interfaces/http/routes/cash_schedule.py`, bootstrap, métadonnées Alembic et garde runtime : intégration native.
- Migration additive `20261102_0147`, parent `20261027_0146` : FK tenant/Affaire, unicité des révisions, contraintes et trigger UPDATE/DELETE interdit ; downgrade non vide refusé.
- `web/src/features/pricing/CashSchedulePanel.tsx`, `cashScheduleTypes.ts`, client API et espace Affaire : saisie, sources, retrait, confirmation, cumuls, reprise et historique.
- Tests domaine, PostgreSQL/HTTP, composant ; fixture API de `App.test.tsx` adaptée à la nouvelle lecture CASH, sans masquer son erreur réelle.

## Preuves et incidents

Preuves privées : `~/.local/share/smartao-proofs/l07-cash-schedule-20261102/`.

- Quatre rouges purs d’absence, puis quatre verts initiaux ; rouge API route absente ; rouge UI composant absent. Test de date native : 201 au lieu de 422, corrigé. Test de collision d’identifiant intertenant : refus au lieu de création indépendante, corrigé par PK composite.
- Revue indépendante : retrait de flux/solde manquant corrigé après rouge UI ; contre-revue sans P1/P2 identifié. Pas une validation humaine ou une certification.
- Une erreur de fixture MFA a violé la contrainte de session (force MFA avec date absente) : scénario corrigé en session PASSWORD sans MFA. Une erreur de test liée au placement d’un import a été corrigée ; ces incidents ne sont pas des rouges produit.
- Navigateur : CUA a signalé un hôte indisponible ; transport MCP Chrome DevTools Local configuré rétabli avec le paquet 1.12.0 déjà installé, Chromium/Helium headless et contexte isolé. Aucun autre outil installé. Adaptateur synthétique local : jeton de fixture injecté hors navigateur, autorisation/API/dispatcher/PostgreSQL natifs inchangés. Ce n’est pas une session utilisateur live.
- Recette UI → adaptateur → API → PostgreSQL : perte de réponse après écriture (503), formulaire figé, retry 200 avec mêmes command_id/revision_id, puis nouvelle révision 201. Deux lignes finales, cumul −100 puis −150 et ancien historique visible. Aucun faux solde certain.
- Desktop 1280 et mobile 393 : assertions de résultat/historique et absence de débordement ; captures relues. Zéro cookie, localStorage, sessionStorage et ressource externe. Pas Playwright ni audit WCAG global ; perte de réponse injectée, pas une panne DB/TCP réelle.
- OpenDesign Local : catalogue courant, artefact financier existant et système consultés ; styles/composants CYTD Owner conservés ; références longues remises à la ligne sans changement de palette ni feuille CSS. Mode Local uniquement. Impeccable contexte/craft-floor/polish et detector ; correction visuelle bornée aux classes existantes.

### Résultats finaux et portée

- Backend ciblé + régressions financières/clôture/architecture : **111 passent, 1 avertissement Starlette/httpx, 43,49 s, exit 0**. Pas de suite backend globale relancée.
- Web global : première passe 727 réussites/1 échec de fixture/4 ignorés ; fixture de lecture CASH ajoutée, App rejouée 47 réussites/2 ignorés ; **globale finale 728 réussites/4 ignorés, 92 fichiers, 286,47 s, exit 0**. Pas d’erreur produit masquée.
- Après les ultimes précisions de portée des anciens rapports CASH et le retour à la ligne des longues références : **19 ciblés Web verts/4,17 s**, types, lint et build verts. Un avertissement préexistant App.tsx sur setDecisionDossier et le chunk >500 kB sont conservés. La globale précède ces deux derniers ajustements d’affichage, le rejeu ciblé les suit.
- Mypy application : **708 sources sans diagnostic**. App/tests : **206 diagnostics/40 fichiers/1256 sources**, identités comparées à la baseline (lignes neutralisées) : aucun ajout ni retrait, aucune suppression de contrôle.
- Ruff/diff whitespace verts. Semgrep **1.183.0, 99 règles, 18 fichiers modifiés, 0 finding, 0 erreur** après les tests ; métriques désactivées, aucune remontée de code/résultats. Impeccable detector sans finding ; captures desktop/mobile relues, pas de certification de sécurité ou d’accessibilité.
- Migration : tête **20261102_0147** unique et garde runtime concordante. Exercice séparé 0146→147→0146→147 sur ancienne Affaire/rapport : forecast préexistant 37 conservé, downgrade vide/re-upgrade vérifiés ; downgrade non vide refusé par la recette. Bases de qualification nettoyées (0 table métier/0 ligne Alembic), base supplémentaire supprimée.
- Présentation complémentaire en lecture seule, distincte du parcours natif : à 393 px, URI de 500 caractères et empreinte de 64 caractères visibles sans coupe/débordement, deux zones effectivement mesurées. Aucun nouvel effet métier dans cette vérification.

**Frontière locale livrée :** saisie/source → calcul déclaré → lecture → retrait/révision/annulation → historique et reprise fonctionnent sur l’Affaire synthétique. L07 général reste PARTIAL ; ce résultat ne démontre pas un cash certain, un calendrier/financement global ou les automatismes reportés.

## Méthode et outils

Superpowers using-superpowers, brainstorming borné, plan, test-driven-development, requesting-code-review et verification-before-completion ; ECC fastapi-patterns, security-review et verification-loop. Graphify consulté avant exploration. OpenDesign Local et Impeccable appliqués avant UI ; contrats des transports et CLI installés vérifiés, aucun nouveau MCP ou package installé. Pas de nouvelle dépendance ni de décision confiée à Jev/Manus. Serena non utilisé sans besoin de navigation sémantique ; Context7 sans question d’API de bibliothèque nouvelle, contrats et schémas locaux réutilisés. Basic Memory reste le miroir du plan.

## Limites et reports

Dates manuelles, sources référencées et hypothèses ne prouvent pas leur authenticité, le droit au paiement ou une disponibilité bancaire. Aucune date n’est calculée depuis CCAG/DGD/clause. Pas de courbe portefeuille ni réservation, comptabilité, moteur légal ou projection automatique des contrats.

Les données manuelles peuvent désigner deux fois le même événement sans identité native ; la déduplication démontrée porte sur les sélections natives, pas sur tout texte libre. La liste native est bornée à 200 faits et 200 lignes du dernier rapport ; historique affiché : 50 dernières révisions, anciens enregistrements conservés. Les limites de liste sont visibles. Pas de conversion de devise ou allocation automatique d’un montant global.

Le navigateur qualifie le composant branché sur l’API native via adaptateur synthétique ; il ne requalifie pas toute la navigation App ni l’authentification réelle. Les refus rôle/tenant/MFA sont prouvés séparément sur l’application et les sessions natives de test.

A1 non admis, A2 HOLD, NO-GO public ; aucun candidat activé, live/corpus réel/VPS/déploiement/P3 réel/dépôt externe/commit/push. Le WIP principal reste préservé.
