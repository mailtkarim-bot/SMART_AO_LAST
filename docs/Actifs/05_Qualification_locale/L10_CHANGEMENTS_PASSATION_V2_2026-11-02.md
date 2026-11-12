# L10 — changements rattachés à la passation V2 exacte — 2 novembre 2026

**Verdict : rattachement local qualifié avec manques et limites. L10 général reste PARTIAL.** Aucun changement de porte, calcul économique ou effet externe.

Le plan global reste seul statut. Checkout principal `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`;665 empreintes WIP antérieures vérifiées avant édition. Aucun reset/clean/stash, checkout, stage, commit ou push.

**AS-IS :** L09 qualifie le pli/passation V1→rectificatif→V2. L10 possède événement, contexte exact de points L09, applicabilité/delta déclaré, actions, relations d'impact et projection Responsable. La chaîne combinée avec cette passation V2 n'a pas été qualifiée.

**RISQUES :** hériter d'une applicabilité/action ou d'un impact V1, rattacher un point d'une autre passation, perdre la source originelle, exposer des montants ou pièces privées, assimiler delta/acte déclaré à exécution ou droit acquis.

**POINTS D'INSERTION :** recettes et callback facultatif de qualification L09. Aucun nouveau registre, abstraction produit, schéma SQL ou UI à créer. Corriger le code métier seulement si une rupture est reproduite, en TDD.

**PLAN MINIMAL :**

- [x] Qualifier deux variantes Markdown/DOCX sur la même Affaire V1/V2 par variante : événement/revue/action V1, rectificatif natif, V1 à revoir, nouveaux événements et actes explicitement liés aux points et hash V2.
- [x] Refuser passation/hash/point V1 et transfert d'applicabilité entre empreintes d'offres distinctes, sans effet métier. Refuser une action avant revue courante et une suite sur action V1 périmée.
- [x] Conserver delta opérationnel DECLARED, impacts économiques UNKNOWN sans faux identifiants A1 ni chiffrage inféré; responsables/preuves/dates non renseignés restent visibles, aucun héritage.
- [x] Vérifier historique, retries identiques, concurrence/droits/tenant/finance par recettes pertinentes, projection Responsable et navigateur si utile; revue, types/lint/Semgrep/diff.
- [x] Bilan borné, sauvegardes relues, plan/index/registre et miroir Basic Memory synchronisés puis relus.

**Décision de portée :** le contrat L10 existant exige même attribution/lot/**empreinte d'offre** pour requalifier un événement. Le P5 V2 étant différent, ce test conserve le refus `HANDOVER_REQUALIFICATION_SCOPE_MISMATCH` : nouveau changement V2 explicitement saisi, aucun relâchement de porte ou transfert automatique. Les événements/actions V1 gardent leur origine. Les sources d'événement sont des références déclarées synthétiques, pas des pièces externes retrouvées.

Autorités : PF31-04/08, M31-05, CT31-15; aucun OS exécuté, effet juridique, notification, P3 réel ou dépôt externe. Superpowers executing-plans/TDD si correction nécessaire; ECC security-review/verification-loop. Graphify consulté avant exploration, Serena activé. Aucun nouveau contrat de bibliothèque; pas d'OpenDesign/Impeccable sans édition visible de l'interface.

## Parcours livré et résultats

Sur deux Affaires synthétiques indépendantes (une variante Markdown, une DOCX), chaque Affaire suit DCE/P5/passation V1, événement/revue/action V1, rectificatif natif et pli/passation V2, puis un **nouvel événement**, une nouvelle revue et une nouvelle action V2. Les options et refus L09 restent natifs. Les deux callbacks de recette ne remplacent aucun service, politique, stockage ou transaction.

Le rapprochement conserve snapshot/révision/vue SHA/empreinte d'offre et points L09 exacts, références d'instruction et pièces déclarées, delta opérationnel DECLARED et actes révisés. La passation, le hash ou le point V1 ne sont pas substitués à V2; un hash V1 sur snapshot/points/instrument V2 autrement valides est refusé isolément409 `OPERATIONAL_CHANGE_SOURCE_CONFLICT`. Les refus ne créent ni événement domaine ni outbox. Une action avant revue courante est refusée422; une nouvelle action sur l'événement V1 périmé est refusée409.

Le refus de requalification entre offres d'empreintes différentes (`HANDOVER_REQUALIFICATION_SCOPE_MISMATCH`,422) est conservé. L'événement/action V1 gardent leur origine et deviennent REVIEW_REQUIRED. La nouvelle saisie V2 n'hérite ni de la revue, ni de l'action, ni du responsable ou de la preuve attendue V1. Les rôles, sources, publication explicite et contrats existants n'ont pas été modifiés pour faire passer la recette. Deux événements, deux revues et deux actions par Affaire sont vérifiés; les retries identiques retournent le reçu sans second effet.

## Bilan des quatre générations

| Variante | Génération | Delta opérationnel | Conséquence économique | Responsable / preuve attendue de l'action | Origine et suite |
|---|---|---|---|---|---|
| Markdown | V1 | DECLARED | UNKNOWN, aucune déclaration C3 | Explicitement renseignés V1 | Conservée; REVIEW_REQUIRED après V2 |
| Markdown | V2 | DECLARED | UNKNOWN, aucune déclaration C3 | UNKNOWN / UNKNOWN, pas copiés de V1 | Nouveau snapshot, point, événement, revue, action |
| DOCX | V1 | DECLARED | UNKNOWN, aucune déclaration C3 | Explicitement renseignés V1 | Conservée; REVIEW_REQUIRED après V2 |
| DOCX | V2 | DECLARED | UNKNOWN, aucune déclaration C3 | UNKNOWN / UNKNOWN, pas copiés de V1 | Nouveau snapshot, point, événement, revue, action |

Les identifiants et hashes exacts sont dans `qualified-changes.json`, et les projections/intentions dans `changes/{markdown,docx}/v{1,2}/`. Les sources P5/passation sont conservées dans `l08-origin/` et `l09-origin/`. Les dates reçues sont déclarées, pas des échéances juridiques calculées; les actions sont enregistrées, pas exécutées ou notifiées.

Une relation C4 UNKNOWN est réellement enregistrée par API pour chaque nouvelle action; ses `declaration_ids` restent vides et les `impact_declarations` sont absentes. Cela démontre l'absence de fabrication de C3/A1 et de montant déduit d'un point L09. **Cela ne démontre pas le non-transfert d'un montant V1 préexistant**, puisqu'aucun montant n'est introduit dans cette chaîne. Les impacts chiffrés restent privés et ne sont pas exposés au Responsable. Le test pur existant de projection exclut des valeurs économiques et références binaires synthétiques; il ne remplace pas une recette native de chiffrage héritée.

## Correction visible et compatibilité

Le lecteur Responsable affichait points/delta/actions, mais pas la version exacte de passation ni l'empreinte d'offre. Deux tests UI rouges ont précédé l'ajout de deux lignes au composant existant : source P7/révision/hash issus du contexte courant préféré à l'origine, puis références d'instruction et pièces **déclarées**. Aucun accès binaire ou téléchargement privé ajouté. Les champs de type facultatifs préservent les anciennes réponses; valeurs absentes UNKNOWN, jamais `undefined`. La confirmation/publication humaine et les autorisations restent celles des API existantes.

OpenDesign de session absent après redémarrage : l'ancien script pointait vers une session bootstrap indisponible alors que le daemon local existait déjà. La connexion MCP/SDK locale a été restaurée avec son URL locale vérifiée; aucun processus global installé, configuration modifiée, daemon arrêté ou basculement Cloud/BYOK. Catalogue courant, artefact de rapprochement C08 et système `linear-app` consultés; Owner CYTD et styles existants conservés, aucune palette/CSS/nouvelle page. Impeccable contexte de session/craft-floor puis detector final0; aucun PRODUCT/DESIGN/hook ajouté.

## Vérifications exécutées

- Recette native initiale **2réussites,1avertissement,131,71s,exit0**. Après ajout du refus isolé du hash ancien, recette finale **2réussites,1avertissement,138,31s,exit0**. Ces campagnes se recouvrent, elles ne sont pas additionnées. Aucun échec produit à corriger dans le backend : qualification d'un comportement existant, sans rouge artificiel.
- Régressions L10 **19réussites,1avertissement,15,96s,exit0** : sources/requalification/actions, uploads privés natifs, droits/rôles, véritable second tenant synthétique côté service, verrou des sources, append-only et refus de downgrade non vide; projection fermée. Cette couverture inter-tenant séparée n'est pas attribuée à la nouvelle chaîne V1/V2 ni appelée E2E JWT multi-tenant complet.
- UI : deux rouges de provenance absente, puis **7réussites/2,64s/exit0** avec test d'`evidence_refs`, contexte courant et anciennes réponses; première passe5tests de panneau sans le nouveau lecteur est historique. Types/lint/build exécutés :0erreur TS, warning App.tsx:517 préexistant et chunk904,74kB (>500kB), aucun seuil relevé. Globales backend/Web non rejouées pour ce changement borné; la campagne L09 reste datée, non réattribuée.
- Mypy application703sources sans diagnostic; app/tests206diagnostics40fichiers/1245sources, identités inchangées contre la clôture L09. Aucun ignore ni nouvelle dette. Ruff/check/format2Python verts, tête Alembic20261027_0146 inchangée, aucune migration ajoutée.
- Semgrep version/règles effectives dans le reçu, `p/security-audit`,5fichiers/0finding/0erreur/exit0, métriques désactivées et analyse locale; motifs stricts de secrets0candidat. Ce sont des contrôles bornés, pas une certification de sécurité.
- Revue indépendante statique Graphify/ECC : aucun défaut bloquant constaté; a demandé le refus de hash isolé, l'assertion des références de pièces et la limite C3 ci-dessus, tous intégrés. Aucun fichier modifié ou test/DB exécuté par le relecteur; aucun accord humain inféré.
- Chrome DevTools Local : composant existant **CaseContractChangePanel/OperationalChangeRead** en lecture Responsable, projections publiques natives enregistrées via API simulée. V1 puis V2 affichent état ancien REVIEW_REQUIRED et nouvel état CURRENT, P7/hash/références exactes, delta déclaré et manques UNKNOWN non hérités.1280/393px sans débordement, corps14px hérité. Zéro cookie/token/stockage ou destination externe; aucun POST dans le harnais navigateur. Pas Playwright, API métier live ou audit WCAG complet; actes/privilèges prouvés par les recettes HTTP séparées.

Les erreurs de chemin du script temporaire OpenDesign et son bootstrap fermé sont des erreurs d'intégration d'outil, pas des échecs produit ni tests PASS. La connexion locale corrigée a abouti avant écriture UI; aucun contournement graphique improvisé.

## Fichiers et frontières

- `backend/tests/db/test_l10_rectified_changes.py` : nouvelle qualification native et refus isolés.
- `backend/tests/db/test_l09_rectified_handover.py` : callback facultatif après chaque passation qualifiée; comportement antérieur inchangé sans callback.
- `web/src/features/decision/OperationalChangeRead.tsx`, `web/src/shared/types.ts` : deux lignes de provenance et types facultatifs de données déjà publiées.
- `web/src/features/decision/OperationalChangeRead.test.tsx` : provenance V2, pièces déclarées, UNKNOWN et compatibilité.
- Présent bilan, plan, index et REGRESSION.md : preuve et prochaine étape, pas nouveau registre de statut.

Aucun code applicatif backend, contrat d'écriture, route, droit, porte P0–P7, règle de requalification, schéma SQL ou calcul d'impact modifié. La continuité est locale et synthétique : référence n'est pas pièce retrouvée, impact UNKNOWN n'est pas zéro, reçu n'est pas exécution, publication ne déclassifie pas les binaires. Le contrôle financier et le non-transfert d'un montant économique existant, la réception externe, la classification juridique et l'exécution effective restent hors de cette preuve. Les manques L08/L09 (réponses, responsabilité/preuves, signature/contrat authentifiés) restent ouverts; L10 général PARTIAL.

## Conservation et suite

Preuves privées `~/.local/share/smartao-proofs/l10-v2-changes-20261102/`;665fichiers WIP précédents préservés, archives complètes/delta relues par SHA et base Git d'origine vérifiée. Deux bases dédiées vides (0table métier/0révision), seul conteneur `smartao-l10-v2-20261102` et preview5200 retirés sans volume persistant. Le daemon OpenDesign déjà existant est préservé. Plan/index/registre et miroir Basic Memory synchronisés puis relus.

Méthode/outils : Superpowers using-superpowers/executing-plans, TDD de la correction UI et revue; ECC security-review/verification-loop. Graphify consulté et Serena activé. OpenDesign local/Impeccable avant UI; Chrome DevTools Local et Basic Memory local. Context7 non nécessaire : aucun nouveau contrat de bibliothèque ou API externe; Jev/Manus sans gain pour cette recette bornée. Aucun connecteur de publication utilisé.

Aucun reset/clean/stash, nouveau checkout, stage/commit/push, live/corpus réel/VPS/déploiement/P3réel/signature réelle/dépôt externe/notification/exécution réelle/moteur candidat activé/GOpublic. Continuité L10 qualifiée avec ces limites, général PARTIAL.

Prochaine étape : L11 — qualifier la continuité entre les changements et actions V2 et le dossier de réception, réserves et paiement, avec sources et manques exacts, sans héritage implicite ni effet externe.
