# T01–T03 — continuité métier sur une même Affaire synthétique

## AS-IS à l’entrée

Les parcours L04–L11 ont des preuves locales séparées. Leurs fixtures créent souvent leur propre Affaire; juxtaposer leurs résultats ne prouve pas la continuité. Le lecteur L04 compose DCE, prix et trésorerie, mais ne reprend pas encore le plan daté L07. Le graphe existant a été consulté; le code et les tests courants restent prioritaires.

## Risques

Ne pas masquer une rupture en injectant des résultats attendus ou en réaffectant des actes historiques à un autre tenant/lot/version. Une fixture technique n’est ni admission Golden DCE ni validation humaine réelle. Préserver droits, finance, MFA, sources, UNKNOWN, append-only, retries et invalidation. Les décisions/attributions nécessaires à l’aval sont des états synthétiques explicitement déclarés, jamais un GO public ni un effet externe.

## Points d’insertion et plan minimal

- [x] Construire un contexte synthétique partagé à partir du corpus multi-pièces/multi-lots existant, extraction et matérialisation actives; garder un seul case_id de L04 à L11 et une seconde Affaire pour le réemploi.
- [x] Reproduire puis corriger les raccords absents entre projections natives, en commençant par la capacité datée L07 dans le dossier L04 et son empreinte de revue.
- [x] Éprouver prix/engagement/réponse/passation/changement/réception-paiement-REX en conservant les sources exactes, conditions et inconnus; ne pas fabriquer de couverture complète.
- [x] Injecter rectificatif, remplacement de source, changement de rôle/session/tenant et réponse tardive; prouver invalidation/historique, refus et absence de second effet.
- [x] Qualifier les parcours concernés, revue, contrôles et scans, nettoyer les ressources dédiées puis mettre à jour plan et mémoire. Toute partie non exécutée reste ouverte.

## Tests à ajouter

Un plan L07 réellement enregistré doit être lisible dans L04 avec son run_id/révision/hash, hypothèses, statut solveur et états de source exacts. Un remplacement change le dossier et invalide sa revue; une portée/DCE discordants ne deviennent jamais applicables. Le reste de la chaîne reprend les mêmes identifiants de sources et d’Affaire, avec refus tenant/rôle/finance/MFA et retries identiques. Les commandes de régression des producteurs et consommateurs sont dans le registre lié.

Le plan global reste l’unique statut et prochaine étape. Local synthétique uniquement; aucun push, VPS, déploiement, corpus réel, activation de candidat ou modification de porte. A1 non admis, A2 HOLD, NO-GO public.

## Journal de travail en cours — 26 octobre

Le corpus existant de8pièces et2lots est extrait/analysé/matérialisé par les services actifs. Les vrais JWT de test et les rôles DB distincts sont utilisés via l’application HTTP complète. Les externalités sont absentes; le scanner de fichiers retourne CLEAN uniquement pour les hashes de classeurs synthétiques explicitement connus. La preuve d’entreprise est un PDF synthétique INSURANCE pour la seule clause assurance lot1 : aucune compétence ni pièce sans rapport ne sont présentées comme qualifiées.

Ruptures rouges corrigées : L07 absent du dossier L04 et de la carte L05; CAPACITY_RUN absent du contrat HTTP/TS et ignoré par le lecteur P5; reclassification RC donnant une réutilisation de clé avec payload différent; préparation bloquée DCE_NOT_READY alors que les entrées courantes sont qualifiées. La projection de préparation vérifie les extractions/fragments/classification/analyse/matérialisation, conserve la déclaration historique sans nouvelle extraction, et n’assimile jamais READY_FOR_ANALYSIS à une analyse complète. Le contexte d’Affaire et son manifeste sont revalidés avant génération. Métadonnées RC10, mêmes règlesv9 et validation historique; SourceFamily/ID de classification font partie de la nouvelle identité canonique.

Preuves intermédiaires réussies :9SQL capacité au premier raccord,11SQL/contrats avec références,14SQL préparation/chaîne,2P5 après remplacement;2tests du nouvel affichage capacité. Le scénario HTTP partagé atteint rédaction/revue C10 native (1/1) avec un seul effet de commit/préparation/draft au retry. Le modèle de droits n’est pas modifié; l’ID serveur confirmé est suivi, pas l’ID proposé dans une commande interne.

Rupture suivante reproduite : ZIP autorisé contenant encore la trame contrôlée plutôt que la contribution acceptée. Publication native immuable des octets revus dans le registre de documents lors du snapshot C10 en cours; anciennes origines divergentes refusées, aucun choix arbitraire entre textes différents. Verdict global, reste de chaîne L09–L11, adverse rectificatif, revue finale, navigateur et scans encore à établir. L’activité ne clôt pas la tranche et ne promeut aucune source réelle.


### Chaîne HTTP native exécutée et contre-exemples

`shared-full-first.log` : quatre tests réussis, un avertissement Starlette/httpx, 52,07 s. La même Affaire couvre DCE huit pièces/deux lots, prix importé, hypothèse de capacité, dossier/revue, engagement, contribution C10 acceptée, P5 exact et ZIP local, attribution déclarée, contrat, document remis au conducteur identique aux octets du ZIP, instruction et action, réception/réserve, levée déclarée, facture/paiement attendu/encaissement partiel, sortie et REX. Une seconde Affaire est créée par le POST natif, puis le réemploi humain explicite est enregistré avec retry sans double effet. Sans DCE cible, son contexte reste UNKNOWN. Le remplacement contractuel entraîne REVIEW_REQUIRED dans passation/actes et réemploi, avec historique conservé. Les rôles de test et la banque/attribution/P3 sont synthétiques : aucun acte réel, livraison acheteur ni effet juridique.

Contre-exemple supplémentaire rouge : génération acceptée après remplacement CONFIRMED→NOT_APPLICABLE d’une confirmation d’exigence. Le manifeste n’avait que les identifiants d’exigences. Il inclut désormais type/directive/outcome et ID/révision exacts de confirmation; requalification en cours. Trois contre-exemples extraction échouée, classification courante absente et tenant étranger passent. Revue indépendante et concurrence de confirmation en cours; aucune clôture globale déduite.


### Revue, concurrence et lecture UI

Revue indépendante bornée : aucun autre P1/P2 concret identifié dans publication/provenance; un P2 de concurrence des confirmations a été reproduit par deux rouges. Le lecteur verrouille désormais exigences et confirmations dans le même ordre que le writer natif, avec refus NOWAIT `VERSION_CONFLICT`. Après libération du verrou, la même commande peut réussir. Dix tests sources/concurrence/chaîne passent (82,63 s, un avertissement); la campagne précédente de18tests avait passé83,51 s. Les nombres ne sont pas additionnés comme des tests distincts.

Chromium isolé via Chrome DevTools MCP, aucun Playwright MCP : treize assertions sur identité/hash, sources/dates, UNKNOWN, masquage hors contexte, absence de cookie et de requête externe. Contrôles de mise en page à390et1280px : SHA long initialement débordant, retour à la ligne corrigé puis absence de débordement vérifiée. UI synthétique du composant de capacité seulement; les actes L04→L11 sont prouvés séparément par HTTP/PostgreSQL. Cela ne constitue pas une recette navigateur intégrale de l’Affaire. OpenDesign Local (contexte/catalogue existant) et Impeccable utilisés sans nouvelle palette ni Cloud; détecteur ciblé sans finding.

Régressions aval :214réussites et trois attentes C10 périmées qui visaient encore l’ancienne trame. Elles vérifient maintenant ID/version/hash du document publié, corruption de ses octets puis ZIP exact. Rejeu en cours avant suite globale. Première Web globale :672réussites,8échecs dans App.test.tsx après timeout,4ignorés. Rejeu exact isolé :47réussites/2ignorés; suite complète àunworker en cours, aucune globale déclarée verte par substitution. Ruff30fichiers/typecheck/build Web et mypy application692fichiers passent; lint Web garde un avertissement App préexistant, chunk principal volumineux. Scan secrets ciblé :0finding, sans exclure les nouveaux fichiers. Semgrep1.182.1 :0finding/35fichiers mais4timeouts sur3fichiers; complément borné en cours, pas PASS complet prématuré.


### Gel final et récupération de publication

Les trois variantes C10 passent après adaptation des attentes au document réellement publié (62,69 s, un avertissement). Le contrôle corrompt bien ce document et le draft, pas l’ancienne trame devenue historique; ces refus restent sans effet d’export. Revue indépendante du verrouillage : P2 fermé, aucun défaut résiduel concret dans le correctif borné, sans prétendre avoir exécuté les tests.

La première globale backend a été interrompue volontairement (`-15`), non qualifiante : vérification finale du stockage révélant un retry de publication bloqué après écriture du fichier suivie d’un rollback avant reçu. Rouge `publication-retry-red.log` : même commande refusée après interruption synthétique. Correctif : sur FileExistsError, relire les octets immuables et comparer leur SHA-256 attendu, sans réécriture; divergence refusée. Le scénario conserve le même command_id/idempotency_key, éprouve un fichier discordant puis récupère avec les octets exacts avant de continuer L09–L11. Rejeu ciblé puis globale finale enchaînés conditionnellement; attendre les résultats avant clôture.

Web finale àunworker :85fichiers,680réussites,4ignorés,297,97 s; exit0. Mypy application692fichiers sans diagnostic; application/tests : dette historique206diagnostics/40fichiers, aucun nouveau diagnostic après corrections de typage des tests transversaux. Semgrep complément à30s/unworker :0finding/0erreur sur les3fichiers ayant eu des timeouts; le correctif de récupération sera rescanné. Aucun verdict CI global ou sécurité exhaustive.


### Requalification des contrats de version

La globale `backend-global-final.log` a été arrêtée proprement après11échecs et1160réussites (733,26s, exit2), afin d’inspecter les diagnostics. Les11échecs portent tous sur `observation.rule_version == "9"` dans les tests de matérialisation. Le protocole existant lie version d’observation et version d’analyse : la version10 porte désormais l’identité de classification, avec les mêmes règles et le même gold métier. Ces assertions et les assertions de version active de deux modules domaine attendent maintenant10; aucune clause/exigence/source/attente sémantique des challenges n’est modifiée.

Seule orchestration courante : session38422, d’abord `dce-version-contract-final.log`, puis `backend-global-requalified.log` si le ciblé passe. Option pytest`--ff` : exécute TOUS les tests, les anciens échecs en premier; elle ne se substitue pas à la suite entière. Nouveau manifeste38fichiers `code-sha256-requalified.json`; aucun code de production modifié depuis le gel de récupération. Tranche toujours ouverte.


## Environnement et portée de la preuve

PostgreSQL local jetable vérifié : image déjà installée `postgres:16-alpine`, réseau `none`, aucun port publié, mémoire768MiB, unCPU et PGDATA en tmpfs512MiB. Connexion par socket privé, URL explicite et opt-in `SMART_AO_TEST_DISPOSABLE_DATABASE=1`; aucune base métier. Tête de code Alembic0145, sans nouvelle migration. Les tests DB restent reproductibles depuis leurs fixtures synthétiques et les commandes du registre de régression.

Outillage appliqué : Graphify avant exploration, Serena pour navigation sémantique, Basic Memory comme miroir; Superpowers (cadrage borné, diagnostic/TDD, revue) et ECC (module-regression, verification-loop), tests natifs du dépôt, OpenDesign Local Codex et Impeccable pour le composant existant, Chrome DevTools MCP isolé pour ses assertions. Aucune dépendance ni aucun moteur candidat ajoutés/activés. Pas de Jev/Manus : pas de classification déléguée utile ni d’investigation externe nécessaire; pas de nouvelle API/SDK dont le contrat exigeait une recherche documentaire externe.

Les4testsWeb conditionnels sont explicitement ignorés en l’absence de leur artefact C08 HTTP optionnel : aucun ancien artefact n’est injecté pour les faire passer. La recette native transversale couvre séparément les API/SQL de cette Affaire; elle ne remplace pas ces assertions UI particulières. Les tests ne prouvent ni exploitation réelle, ClamAV réel, corpus Golden, couverture automatique exhaustive, conformité juridique, banque ni recette navigateur intégrale.


### Limite multi-contributions explicite

Le snapshot refuse plusieurs contenus revus différents : il ne sélectionne ni ne fusionne arbitrairement une réponse. Contre-exemple isolé `test_preparation_publication_choice.py` :1réussite en1,37s, aucun write stockage ni ajout DB; dépendances de lecture bornées simulées, sans prétendre à une seconde preuve HTTP. Il a été ajouté pendant la globale, après sa collecte : il est exécuté séparément et n’est pas ajouté artificiellement au nombre de réussites de cette campagne. Aucun code de production n’a changé. Le manifeste complémentaire `code-sha256-with-choice.json` couvre39fichiers.

La composition d’un document unique à partir de plusieurs contributions, avec sélection explicite et revue Patron de l’assemblage exact, reste un manque métier de L08. La preuve transversale ne démontre qu’une réponse revue unique, dont les octets sont conservés jusqu’au ZIP et au conducteur. Aucun pli acheteur complet ni couverture exhaustive n’est prétendu.


## Bilan de qualification locale — 26 octobre 2026

La suite backend complète termine avec **4005réussites,1avertissement Starlette/httpx,3148,25s,exit0** (`backend-global-requalified.log`). Elle inclut les contre-exemples de provenance, les versions historiques, le rectificatif concurrent, les refus tenant/rôle/MFA, les retries et l’append-only des modules concernés. Le contre-exemple isolé ajouté après collecte passe séparément1/1 : les deux nombres ne sont pas fusionnés pour prétendre à un unique run4006. Web complète :680réussites,4ignorés conditionnels,85fichiers,297,97s,exit0. Les campagnes interrompues/en échec restent historiques et ne sont jamais qualifiantes.

Résultat métier : un plan de capacité natif est visible dans le dossier et sélectionnable par référence exacte dans l’engagement; son remplacement invalide P5. Le lecteur de préparation vérifie les entrées courantes extraction/classification/analyse/matérialisation sans déduire l’exhaustivité; confirmation et révision appartiennent au manifeste, avec verrouillage contre les writers natifs. Une contribution C10 acceptée est publiée de façon immuable : même texte/SHA dans le ZIP autorisé puis le document conducteur. Un rollback après écriture du fichier permet le retry identique si les octets correspondent; une divergence reste refusée. Instructions/actions, réception/réserve, paiement attendu et encaissement partiel, sortie et réemploi explicite du REX conservent la même Affaire et leurs sources. Le remplacement contractuel impose une revue et conserve l’historique.

Contrôles finaux :39empreintes de code stables, Ruff et format35Python verts, application mypy692sansdiagnostic, types/build Web verts, lint0erreur/1warning hors raccord, secrets39fichiers0finding. Semgrep1.182.1 :99règles utiles sur39fichiers cumulés,0finding; quatre timeouts initiaux résolus par compléments bornés30s/unworker,0erreur résiduelle. Contre-revues indépendantes du verrouillage et de la récupération sans défaut concret identifié; ces revues n’ont pas exécuté la DB. L’application/tests garde206diagnostics mypy dans40fichiers hors raccord, CI non qualifiée; chunk principal862,12kB. Aucun seuil de couverture de tests n’est revendiqué.

Nettoyage observé après exit0 : `smartao_transversal_dev` a zéro ligne Alembic, seule base du préfixe de cette recette; conteneur dédié `smartao-l04-acts-pg-20261020` arrêté (`exited`). ACL UID70 retirée et socket restauré700. Vite et les deux transports MCP de recette terminés; aucun worker Vitest de recette restant. Les navigateurs et applications étrangers n’ont pas été touchés.39SHA correspondent toujours au gel; HEAD30f26934430095632000a1d82519f61dbb4c6411 et index sans staging, aucun commit/push.

Cette qualification est locale et synthétique. Garanties T01–T03 et livrables généraux restent PARTIAL : aucun corpus Golden admis, A2 générique HOLD, DPGF non évaluable par RAG, moteurs candidats inactifs et NO-GO public. Plusieurs textes revus différents exigent encore une composition/sélection explicite et une revue de l’assemblage; aucune fusion arbitraire n’est livrée. Les formulaires acheteur DOCX/PDF, signatures et recette navigateur intégrale restent ouverts. Le plan global porte seul la prochaine étape L08.


Synchronisation Basic Memory vérifiée par relecture : même prochaine étape L08 que le plan global. Aucun statut alternatif créé.
