# L06 — Répartitions révisées et chiffrage publié — 05/11/2026

Le [plan global](../00_Pilotage_et_audits/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md) reste l’unique statut opérationnel. Ce dossier prolonge la [répartition déclarée](L06_REPARTITION_COUT_PARTAGE_2026-11-05.md) ; il ne change aucune porte ni politique de publication. Qualification synthétique locale, général PARTIAL.

## AS-IS, risques et plan minimal

Le rapport financier natif possède un acte de publication immuable et une révision. Les revues de position citent chaque rapport/révision/état exact ; les affectations sont un registre séparé. Publier passe DRAFT→PUBLISHED et incrémente la révision, ce qui invalide les anciennes revues. Le manque visible était l’absence d’identification complète du rapport source dans la relecture des postes.

Risques : assimiler une affectation à un nouveau coût publié, sommer deux fois, réutiliser une approbation DRAFT, présenter une revue ultérieure comme contenue dans la publication, ou conclure à une couverture. Insertion minimale : ajouter la provenance lisible et la distinction dans Facts du panneau Prix, puis qualifier le parcours HTTP/PostgreSQL existant. Aucun backend applicatif, schéma, migration, DTO, endpoint, droit, compteur, porte ou export changé.

Plan appliqué : vérifier baseline765/Git et autorités ; test UI rouge puis ajout ciblé ; recette native publication/invalidation/nouvelles revues/révision ; refus et historique ; navigateur sur la même Affaire synthétique ; contrôles et miroir. Tests à prouver : publication/retry, sources anciennes refusées, nouvelle revue explicite, budget et reste, rapport JSON inchangé, tenant/rôle et histoire exacte.

## Résultat utilisateur

Prix → Chiffrage sourcé par poste affiche pour chaque coût rattaché le rapport source, sa révision et son état enregistré, ainsi que le montant affecté. Sur une source PUBLISHED, l’avertissement précise que la répartition est distincte des totaux du rapport publié, qu’elle ne les modifie pas et ne prouve pas la couverture. Le même composant expose les références historiques sous leur en-tête HISTORICAL.

Le parcours conserve justification/hypothèses/manques et confirmation humaine natives. Après publication, anciennes revues REVIEW_REQUIRED et montants courants UNKNOWN ; nouvelle sélection de la source exacte et nouveaux actes nécessaires. Après révision d’une affectation, le coût natif et les totaux publiés restent ceux de la publication : les montants affectés ne s’y ajoutent pas. Un rapport PUBLISHED cité n’est pas automatiquement le dernier rapport publié de l’Affaire ni une preuve de prix certain.

## Parcours et preuves natifs

Fichier : `backend/tests/db/test_l06_allocation_publication.py` ; fixtures synthétiques et vrais services/routes de publication, lecture de rapport et revues de position. Un même tenant/Affaire/import/coût suit :

1. Source12000 à révision1/DRAFT ; affectations4500 et6500, avec hypothèse/transport inconnu.
2. Publication humaine native201 puis retry200 même intention ; rapport révision2/PUBLISHED, coût direct12000 inchangé et lecture no-store.
3. Deux anciennes revues invalidées ; montants UNKNOWN et source sans allocation actuelle. Une nouvelle intention qui cite encore la révision1 est refusée409.
4. Nouvelles revues5000 et7000 sur la source PUBLISHED exacte, nouveaux IDs, justifications et consentements ; retries200 sans nouvelle revue. Aucun accord repris.
5. 5001 refusé422 car dépassement avec7000 ; nouvelle revue4000 autorisée. Affecté11000/reste1000 ; couverture/applicabilité UNKNOWN et transport manquant visibles.
6. Historique du premier poste :4000/PUBLISHED,5000/PUBLISHED,4500/DRAFT avec IDs/révisions propres. Les données JSON du rapport publié sont identiques avant/après, sans prétendre à une comparaison des octets HTTP.

Campagne élargie : **112 réussites/66,11s**, dont positions, parcours L06 et85 contraintes d’architecture. Après revue statique, les tests privés sont renforcés pour établir effectivement publication et affectations avant de changer de rôle/tenant : **3 recettes finales/22,70s**, incluant refus des lectures rapport/postes/historique. Les campagnes se recouvrent ; pas de somme de tests distincts annoncée. Avertissement Starlette/httpx existant conservé. Pas de globale backend nouvelle, aucun backend applicatif changé.

## Preuve UI et navigateur

`PricingPositionsPanel.test.tsx` : un rouge sur l’identification PUBLISHED et l’avertissement, puis **12 réussites/4,19s** avec les garanties existantes de source, contexte, relecture et intention UNKNOWN. Production : `PricingPositionsPanel.tsx` seulement, aucun CSS/token nouveau.

Chrome DevTools MCP local headless/isolé, pas Playwright MCP. La recette native ci-dessus prépare la même Affaire ; React du panneau réel→adaptateur loopback→TestClient/API/PostgreSQL enregistre ensuite une revue4500 sur le premier poste après publication. Réponse masquée503 après commit201 ; retry200 strictement identique, première position révision4, deuxième7000 ; affecté11500/reste500 sur12000. Lecture du rapport avant/après depuis le navigateur : mêmes données JSON, révision2. Aucun nouvel acte de publication déclenché par l’affectation.

Lectures1280 et393 : largeur globale égale au viewport, tableau défilant interne explicite, cookies/localStorage/sessionStorage vides et ressources loopback seulement. Capture mobile relue : identifiant long du rapport lisible, état/révision et réserve sur les totaux visibles. Ce n’est pas une recette d’authentification réelle ni une preuve de tout le parcours de publication cliqué dans le navigateur : la publication initiale est exercée par HTTP natif dans le même scénario. Ni crash réseau/DB, ni reprise UNKNOWN après reload, ni WCAG exhaustive déduits.

## Contrôles, périmètre et méthode

Preuves privées : `~/.local/share/smartao-proofs/l06-allocation-publication-20261105/`, baseline765 empreintes relues, copies avant et3 sources gelées. Le backend applicatif reste strictement identique à la tranche précédente ; contrôles de portée et archive à la livraison.

Superpowers using-superpowers/brainstorming borné/TDD et requesting-code-review ; ECC verification-loop. Graphify consulté avant navigation manuelle, Serena activée, Basic Memory miroir. OpenDesign Local : catalogues et artefact C08 existant relus via MCP local ; aucun nouveau prototype ou système visuel, composants/styles de l’interface cible conservés. Impeccable contexte existant et craft-floor, détecteur0. Pas de Context7 nouveau (aucun contrat de bibliothèque modifié), Jev/Manus non nécessaires pour ce périmètre ; aucune publication ou requête GitHub.

La revue a corrigé une limite de preuve : les premiers refus se faisaient sur un DRAFT ; la campagne renforcée les place après publication et affectations, y compris historique. L’égalité JSON est nommée comme telle, pas comme identité octet par octet. Aucun défaut de backend ni changement de publication n’a été inventé pour la recette.

Les portes, UNKNOWN, droits, sources et champs privés sont conservés. Pas de calcul juridique, prix certain, cash certain, couverture complète, source réelle, VPS/déploiement, P3 réel, dépôt externe, candidat activé, commit ou push. A1 non admis/A2 HOLD/NO-GO public.

La nouvelle recette de publication porte le coût DIRECT_COST natif et des positions de classeur reçues en aperçu ; elle ne rejoue pas le commit commercial des ventes dans ce même scénario. Le parcours import/commit garde sa preuve distincte L06 dans la régression ; aucune offre complète ni prix commercial certain n’est déduit de cette publication interne.

## Relevé final

Globale Web : **801 réussites/4 ignorés,93 fichiers/305.78s/exit0**. Mypy application708 sources, types Web, lint ciblé et Ruff verts ; build vert, avertissements App et chunk volumineux existants. Semgrep1.183.0,99 règles/3 fichiers,0 finding/0 erreur, métriques désactivées ; aucun résultat envoyé. Impeccable0 finding. Aucune globale backend actuelle nouvelle :112 régressions et3 recettes renforcées conservent leur périmètre propre.

Trois sources gelées inchangées pendant le navigateur ; aucun backend applicatif changé. Base jetable relue0 table métier/0 révision Alembic ; conteneur/volume et adaptateur/Vite/entrées UI temporaires retirés. Services utilisateur et daemon OpenDesign préexistants préservés. Liens, tranche unique, archive WIP et miroir relus dans `delivery.json` à la livraison. Qualification locale acquise avec ces limites, général PARTIAL ; aucune porte ni GO public déduit.
