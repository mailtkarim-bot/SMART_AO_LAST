# L06 — Répartition déclarée d’un coût partagé — 05/11/2026

Le [plan global](../00_Pilotage_et_audits/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md) reste l’unique statut opérationnel. Qualification locale synthétique, périmètre général PARTIAL ; aucun GO économique/public.

## Contrat et insertion minimale

AS-IS : les revues natives rattachent des coûts exacts aux positions importées ; un coût réutilisé donne UNKNOWN sans double compte mais sans affectation possible. RISQUES : suraffectation entre positions ou imports, perte d’exactitude au navigateur, transfert après source remplacée, altération du hash d’une ancienne intention. POINTS D’INSERTION : commande/révision/snapshot et lecteur existants, projection monétaire et panneau Prix ; aucune table ni migration nouvelle. PLAN MINIMAL : montant facultatif explicite par référence, budget sous verrou Case/Report, projection du reste, saisie/revue/retry/historique puis tests et contrôles. TESTS : nominal/partiel/limites, réutilisation legacy, dépassement/concurrence, ancienne intention, source remplacée, droits/tenant et parcours natif.

PF31-08/09 et CT31-02/03/06 conservés : les impacts restent déclarés et sourcés, une somme partielle ne prouve pas la couverture. Le Patron utilise les sources de son Affaire ; aucun montant privé n’est projeté au Conducteur ou exporté.

## Parcours livré

Dans Prix → Chiffrage sourcé par poste → Rapprocher ce poste : sélectionner les coûts, renseigner un montant affecté en unités monétaires mineures de la devise source, expliciter les hypothèses et manques dans la justification, vérifier puis confirmer. Une valeur vide reste un rattachement sans répartition ; elle ne devient ni zéro ni affectation automatique. L’écran montre coût source, total affecté et restant non affecté, ou UNKNOWN si la preuve est insuffisante. Les montants individuels figurent aussi dans la relecture et l’historique.

Une affectation explicite est un entier exact positif ou nul, borné au montant source et à l’entier monétaire natif. Aucune conversion, règle de répartition ou équivalence d’unité n’est ajoutée. Le total du poste peut être déclaré tandis que couverture et applicabilité restent UNKNOWN ; transport, exclusions, unités et autres manques restent visibles.

Les dernières revues de toutes les positions et de tous les imports de la même Affaire sont prises en compte, sous verrou Case pour l’écriture et verrou du rapport source. Un dépassement est refusé sans nouvelle revue. Modifier la répartition exige nouvelle intention, révision attendue, motif et confirmation ; une même intention rejouée rend le reçu existant. Même clé avec montant différent : refus natif422, sans nouvelle ligne ; ce n’est pas un409 de révision.

Les anciens rattachements sans montant restent compatibles : leur sérialisation omet le nouveau champ absent, donc l’empreinte sémantique des anciennes intentions est conservée. Ils ne sont pas convertis en affectation. Tant qu’un autre rattachement est non résolu, nouvelle répartition refusée ; retirer/requalifier explicitement ces liens. Une source de rapport révisée n’hérite pas des affectations antérieures. Un contexte Affaire/DCE/import invalidé rend ses références UNKNOWN, sans libération ou reprise automatique ; leur budget reste à requalifier.

Le snapshot et les références relationnelles doivent correspondre, et les empreintes du contexte et des sources doivent être actuelles. Sinon UNKNOWN/refus conservateur. Les revues anciennes et montants historiques demeurent append-only. L’actualisation manuelle efface les saisies non confirmées ; après503 l’intention confirmée reste figée dans le store existant, retry exact uniquement.

## Fichiers et compatibilité

- Python : `application/position_commands.py`, `infrastructure/position_handler.py`, `infrastructure/position_reader.py`, `domain/position_costing.py`, `public/position_contracts.py` dans `backend/app/modules/pricing/`.
- API native de revue par position conservée ; champ facultatif `cost_refs[].allocated_amount_minor` chaîne exacte ; résumé de répartition en lecture des coûts sources. Aucun nouvel endpoint, droit, mécanisme de porte ou effet externe.
- Web : `PricingPositionsPanel.tsx`, ses tests et `shared/types.ts`. Pas de CSS/token/dépendance nouvelle.
- Tests : `backend/tests/db/test_pricing_positions.py` et `backend/tests/domain/pricing/test_position_costing.py`.

## Preuves et contrôles

Preuves privées : `~/.local/share/smartao-proofs/l06-shared-cost-20261105/` ; baseline764 fichiers vérifiée avant édition, copies avant et gels SHA conservés. Aucun résultat ancien substitué.

- Rouge initial domaine : montant explicite4500 restait UNKNOWN ; vert ciblé. Rouge HTTP : champ facultatif absent refusé422 ; implémentation puis campagnes vertes.
- Revue indépendante : contexte invalide encore DECLARED corrigé, puis fusion UI historique écrasant le résumé courant corrigée ; régressions rouges puis vertes. Actualisation sans transfert des saisies et ancienne sérialisation sans champ null également rouges puis vertes.
- Backend final : **117 tests réussis /41,16s**, avertissement Starlette/httpx existant ; comprend positions, domaine, parcours L06 et85 contraintes d’architecture. Concurrence6001+6001 sur12000 : un201/un422 ; somme6001. Révision source puis nouvelle affectation5000 : reste7000, ancienne4500 conservée.
- Web Prix final : **104 réussites /1 ignoré,8 fichiers/49,40s**. Les contrôles UI couvrent montant explicite et retry identique, résumé pendant édition d’un acte existant, abandon des saisies après relecture, droits/contexte et comportements existants.
- Mypy application708 sources vert sur la version finale ; types et lint ciblé Web verts. Dette mypy tests historique non requalifiée.
- Lint global Web : zéro erreur, avertissement App530 dépendance de hook déjà présent. Build : avertissements App/chunk volumineux existants. Aucun remaniement hors périmètre.
- Semgrep1.183.0 : première passe99 règles/9 fichiers,0 finding/0 erreur ; dernière passe des sources finales consignée dans le relevé final. Analyse locale, métriques désactivées, aucun résultat envoyé.

### Tentatives et limites explicites

Globale backend interrompue volontairement sous pression mémoire :7 réussites puis KeyboardInterrupt/exit2, non qualifiante. Globale Web interrompue/exit130 après deux échecs App sous forte pression mémoire/swap ; les deux mêmes tests passent isolément2/50 non sélectionnés/7,18s. Une cause environnementale est plausible, pas prouvée par le seul rejeu. Ces tentatives ne deviennent pas PASS. Les campagnes ciblées et le nouveau relevé global éventuel gardent leur portée propre.

Deux essais du harnais d’invalidation étaient invalides (clé ORM puis tentative d’UPDATE d’import append-only) ; ni preuve rouge métier ni contournement des protections. Le test correct change le scope Affaire comme les tests existants : ancien total DECLARED avant correction, UNKNOWN ensuite. Une attente409 sur changement de payload était incorrecte : le contrat natif refuse422 ; l’assertion a été alignée sans changer le routeur.

Navigateur : Chrome DevTools MCP local headless/isolé, pas Playwright MCP. Harnais temporaire React→adaptateur loopback→TestClient HTTP/PostgreSQL synthétique, aucun cookie/token ou stockage navigateur. CORS du harnais corrigé, puis attentes DOM et relecture d’un acte après réponse perdue explicitées ; aucune écriture rejouée à l’aveugle, GET de réconciliation avant reprise. Le premier chemin a effectivement enregistré4500/retry200 puis6500 ; source12000, affecté11000, restant1000, UNKNOWN conservé. Desktop1280/mobile393 sans débordement global et sans ressource externe. Les sources finales sont rejouées dans une nouvelle Affaire synthétique avant livraison ; voir relevé final. Aucun parcours d’authentification réel, panne réseau/DB, reload d’intention UNKNOWN ou restauration après crash démontré.

## Méthode et frontières

Superpowers : using-superpowers, brainstorming borné, TDD, systematic-debugging, requesting-code-review et vérification avant clôture. ECC verification-loop adapté aux commandes du projet. Graphify consulté avant navigation textuelle ; Serena activée ; Context7 et version installée pour Field/exclude_if ; Basic Memory miroir. OpenDesign Local consulté via MCP existant, catalogues et contexte C08 de rapprochement financier relus ; interaction/surfaces existantes conservées, aucune ancienne palette imposée contre les références Owner. Impeccable context/craft-floor/audit/detect ; conformité CYTD globale et accessibilité exhaustive non revendiquées. Jev/Manus/GitHub non nécessaires à cette implémentation locale, aucune publication.

Pas de migration ; tête0147 et garde-fous append-only conservés. Pas de réécriture du coût source, des ventes ou du chiffrage publié ; ces affectations ne deviennent pas un prix publié. Pas de fournisseur, live, corpus réel, VPS, P3 réel, dépôt externe, activation de candidat, commit ou push. A1 non admis/A2 HOLD/NO-GO public.

## Relevé final

Globale Web finale : **800 réussites /4 ignorés,93 fichiers/255,84s/exit0** (`web-global-qualified.log`). Backend :117/41,16s/exit0 puis8 purs/0,36s après seul tri d’import de test ; pas de globale backend actuelle qualifiante. Types Python708, types Web et lint ciblé verts ; Ruff final vert, diff sans whitespace. Semgrep final99 règles/4 fichiers0 finding/0 erreur, en complément des9 fichiers initiaux ; les tests Web ne font pas partie du scan sensible. Impeccable final0 finding. Le build final et sa portée sont consignés dans `build-qualified.log` ; avertissements App/chunk conservés.

Rejeu natif sur **nouvelle Affaire synthétique**, fichiers applicatifs gelés : React→HTTP→PostgreSQL, POST503 masqué après201 réellement commis, retry200 même payload/identifiants puis secondPOST201. Deux positions révision1, affectations4500/6500, total11000/reste1000 vérifiés sur la source12000. Lectures1280/393 : largeur globale égale au viewport, cookies/localStorage/sessionStorage vides et ressources loopback uniquement ; captures et requêtes conservées. Pas d’authentification réelle/Playwright ni preuve de WCAG exhaustive ; la console signale des champs sans id/name (labels implicites présents), avertissement de formulaire conservé. Les premiers essais non concluants restent séparés, y compris attente DOM et défaut UI corrigé. Le gel final ne diffère du gel natif que par un tri d’import dans un test pur, rejoué8/8 ; aucun octet applicatif modifié après le rejeu natif.

Les trois bases jetables ont été relues :0 table métier/0 révision Alembic, table Alembic absente pour la base de globale interrompue. Le premier contrôle de cleanup supposait cette table toujours présente et a échoué ; vérification corrigée sur le volume exact, identifié par événement Docker lié au seul conteneur de tranche. Conteneurs/volume et entrées UI/adaptateur/Vite temporaires retirés ; daemon OpenDesign préexistant préservé. WIP, delta, archive et miroir sont vérifiés dans `delivery.json` à la livraison.

Qualification locale acquise **avec ces limites**, général PARTIAL. La prochaine tranche est uniquement désignée dans le plan ; aucune porte ni autorisation aval acquise.
