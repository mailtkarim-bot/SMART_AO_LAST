# R4 — Continuité des listes RC — 15 octobre 2026

## AS-IS et risques
HEAD30f26934430095632000a1d82519f61dbb4c6411, branche codex/reconcile-smartao-20261009, WIP préservé. Deux omissions connues : en-tête final suivi de CCAP/CCTP dans le fragment suivant. Risques : contexte attribué au mauvais fragment, page vide sautée, extraction/version différente, fausse portée lot ou négation.

## Plan minimal / points d'insertion
- [x] TDD : reproduire les deux omissions et les ruptures, ancres UTF8 exactes.
- [x] Détecteur : reprise bornée de la dernière ligne en-tête sur le début de liste explicite du fragment immédiatement suivant; pas de concaténation persistée ni de contexte injecté à une clause indépendante.
- [x] Reader : même tenant/document/version/extraction, ordinal consécutif et page PDF immédiatement suivante/part1; vérifier les deux hashes. Ancres distinctes publiques document/extraction/fragment/page/octet; état candidat seulement.
- [x] Contrat/panneau : région d'en-tête distinguée de la région de liste dans le style Owner existant, sans nouvel acte métier.
- [x] Tests ciblés puis suites appropriées/types/lint/Semgrep/revue; mettre à jour plan/journal/mémoire selon preuves.

## Refus à prouver
Page sautée, partie interrompue, fragment corrompu, extraction/document étrangers, texte intercalaire, ligne blanche/section/fin de liste, négation/condition ambiguë. Aucun transfert vers une liste située au-delà du fragment suivant : cas restant UNKNOWN à mesurer séparément. Pas d'admission source, de présence/criticité/applicabilité déduite, de nouvelle dépendance ou migration. A1 non admis,A2 HOLD,NO-GOpublic.


## Résultats acquis avant le global final

- TDD : deux omissions reproduites (2rouges/72verts); reprise minimale →74verts. En-tête négatif non reconnu reproduit puis corrigé. Négation locale héritant à tort du positif détectée par revue indépendante :4rouges (`ne faisant pas partie`, `non applicable`, `sans application`, `jamais requis`), puis correction partagée →**83tests purs verts**. Aucun lot affirmé sur une ambiguïté.
- SQL : première fixture de refus tentait des UPDATE interdits, bloqués par append-only; fixtures corrigées par ajouts d'extractions/fragments, aucune contrainte désactivée. Régression nominale rejouée avec la reprise désactivée :1rouge; lecteur corrigé :155tests ciblés SQL/API/reader/détecteur alors verts (173,55s). Refus supplémentaire `previous_part` reproduit rouge puis garde ajoutée; sa qualification finale dépend de la suite globale en cours.
- Web : test d'ancre rouge1/11verts →12/12verts. Global **546réussites/4ignorés**,66fichiers,49,44s. Typecheck/lint/build verts; bundle707,64kB et warning>500kB conservés. Aucun CSS/style/palette/typo changé.
- Ruff backend/scripts vert; mypy624sources vert avant puis après corrections. Impeccable detect :0constat. Semgrep final en cours après correction de revue, pas de PASS anticipé.
- Revue indépendante READ ONLY par la skill Superpowers requesting-code-review, ECC security-review : défaut de négation retenu/corrigé; relecture16combinaisons positif/négatif/réserves, aucun nouveau blocage concret. Ne remplace ni une revue métier humaine ni les tests DB.

## Preuve source et navigateur synthétiques

Répertoire privé horsGit `/home/noor/.local/share/smartao-proofs/r4c-20261015/` : PDF synthétique original conservé, manifeste source/page/fragment/extraction/hash, `harness/reading.json`, `http-evidence.json`, `source-chain-verification.json`, `continuation-metrics.json`, captures/logs et empreintes de code. Relecture réelle du PDF après teardown de la base secondaire :2fragments/locators/hash vérifiés,2annonces CCAP/CCTP reliées à la région de liste page2 et à l'en-tête page1, version/extraction/document exacts. Aucun hash/texte privé ajouté au DTO public. Signal candidat `rule_version=2`; candidats historiques gardent leur identité et version1.

Chaîne réelle extraction→SQL→FastAPI/TestClient sur PG jetable, mais acteur/politique/runtime Case synthétiques explicites : aucune preuve d'auth live ou topologie Case réelle. Capture positive acquise avant la correction de négation; source reparsée et métriques positives rejouées sur code corrigé, sans déduire une preuve de négation de la seule capture positive.

ChromeDevToolsLocal, contexts isolés, composant/CSS réels avec projection API capturée. Deux ancres distinctes visibles, UNKNOWN et analyse complète non démontrée conservés, disparition des candidats après retrait de couverture vérifiée après rendu React. Première lecture synchrone immédiatement après clic donnait `hidden=false` avant rendu; assertion rejouée après deux requestAnimationFrame :true. Largeurs demandées390/1440, réellement mesurées393/1443, sans débordement.12requêtes de la dernière navigation toutesloopback. Harnais arrêté, onglets fermés. Pas dePlaywrightMCP, backend live, auth réelle ou parcours applicatif complet.

## Mesures et limites

Deux annonces omises dans le contre-exemple figé précédent :**2omissions→0**,0fauxpositif de signature,0présence déclarée connue. Calibration précédente inchangée24textes/25signatures :25retrouvées,0omission,0FP,0présenceconnue; SHAfixture `fcbe18289ff04cf9aeb4f147af5bbd7b631e1335de1f453a01933d8a41a2605b`. Jeu de calibration Codex, pas benchmark indépendant ou Golden DCE.

Qualification limitée à un en-tête final explicite, liste initiale explicite, fragments consécutifs et pages PDF immédiatement successives, partie suivante1 et partie précédente connue. Une page vide sautée, ordinal interrompu, type de locator discordant, hash invalide, contexte remplacé/ancienne extraction ou rupture textuelle refuse la reprise. Les deux ancres ont le même document/extraction/version; la région d'en-tête garde son propre fragment/locator/offset.

**Restent non qualifiés :** listes prolongées au-delà du fragment suivant, parties d'une même page, tableaux/colonnes/en-têtes répétés et continuité sémantique sans délimitation explicite. La provenance technique ne prouve pas l'applicabilité métier; UNKNOWN/REVIEW_REQUIRED et refus de complétude restent. Aucun corpus réel, admission A1, effet P3, déploiement, VPS, push ou GO public.

## Suite globale finale

Premier global volontairement interrompu pour corriger la négation :718réussites observées/1warning,265,78s,exit2;**pas un PASS global**. Nouveau global complet en cours sur code corrigé; résultat à consigner uniquement à sa sortie. Aucun schéma, migration, permission, commande, dépendance ni état de qualification humaine modifié.

## Méthodes

Superpowers using-superpowers/brainstorming/writing-plans/TDD/systematic-debugging/revue; ECC verification-loop/security-review. Graphify consulté avant navigation (graphe ancien, orientation seulement); pas de navigation sémantique supplémentaire nécessitant Serena. OpenDesign MCP local existant consulté (catalogue courant skills/plugins) après rétablissement de l'accès loopback; PF31-11/Owner conservé, pas de génération Cloud/BYOK. Impeccable context/craft-floor/clarify/detect pour l'ancre dans la surface existante. Jev/Manus inutiles pour cette correction déterministe bornée; aucune validation humaine simulée.


### Correction du lancement du global
Le deuxième global a été interrompu après880réussites et1erreur de teardown (`test_rc_subcontracting_is_recorded_and_read_with_exact_family_and_tenant`,475,07s,exit2). Cause vérifiée dans `backend/tests/conftest.py` : `SMART_AO_TEST_DISPOSABLE_DATABASE=1` manquait au lancement; les données n'étaient donc pas purgées avant le downgrade0066, lequel refuse correctement l'ancienne taxonomie incompatible. Aucun test métier n'a échoué dans cette exécution partielle; l'erreur de teardown reste une erreur réelle de suite et n'est pas effacée. Base primaire vérifiée revenue à base par les teardowns suivants, tabletenantsabsente et0versionAlembic. Tentative de TRUNCATE devenue inutile refusée sur table absente; appel CLI Alembic sans URLconfigurée échoué avantconnexion, aucune modification de schéma live. Le runner utilise désormais explicitement les deux variables DATABASE_URL et DISPOSABLE_DATABASE, sur conteneur/port/labeljetablesvérifiés. Test et teardown concernés à requalifier puis nouveau global complet, sans changement produit.

Le test et son teardown concernés passent avec la configuration correcte :1/1,6,71s,exit0. Global courant : `/tmp/smartao-r4c-backend-qualified.log`,session55440;DISPOSABLE_DATABASE=1,PRESERVE_C5_RESTORE_FIXTURE=0,URLjetableexplicitementfourni. Ne pas relancer un runner concurrent sur cette base.


## Résultat final — qualification technique locale bornée

Global avec configuration jetable correcte : **2703 tests réussis,1warningStarlette/httpx,1354,83s,exit0**. Aucun test ignoré dans cette suite backend. Le test de teardown précédemment en erreur passe également dans le global; aucune contrainte ou migration assouplie. Journal `smartao-r4c-backend-qualified.log` conservé avec les anciennes exécutions partielles. Les9SHA-256 code/tests correspondent exactement au manifeste final.

Les deux bases ont été vérifiées à Alembic base (0ligne), puis seul le conteneur identifié `smartao-r4c-proof-20261015`/label`r4c-20261015` a été arrêté et retiré. Aucun service live touché. Plan/case/index/journal actualisés avec une seule tranche active. HEAD30f26934430095632000a1d82519f61dbb4c6411 et branche inchangés;WIP non commité,aucunpush.

Qualification acquise uniquement pour la reprise explicitement délimitée entre pages immédiatement successives et pour ses refus. Aucune analyse complète de DCE réel ou validation humaine A1 ne peut être déduite.

Prochaine étape : R4 — qualifier les listes RC réparties entre parties d’une même page ou prolongées sur plus de deux pages, avec chaîne d’ancres et refus des ruptures; mesurer les omissions restantes sans transfert implicite de contexte. Préserver UNKNOWN, A1 non admis, A2 générique HOLD et NO-GO public.

Miroir Basic Memory smart-ao-v8 synchronisé puis relu :2703/2703,portée bornée et prochaine étape exacte vérifiés. Le plan demeure la seule autorité de statut.
