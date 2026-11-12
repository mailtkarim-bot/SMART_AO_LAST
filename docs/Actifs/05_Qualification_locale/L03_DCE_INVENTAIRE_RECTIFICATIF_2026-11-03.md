# L03 — réception, inventaire et rectificatif synthétiques

Statut exclusivement dans le plan global ; preuves et limites bornées ci-dessous.

AS-IS : staging/admission et liaison Case existent ; couverture des archives, non-lus et déclarations manquantes existent. Le canal RECTIFICATION n’établit pas de prédécesseur dans l’admission HTTP. Le hook d’ouverture conserve des données non indexées par version/périmètre et relit la fermeture de l’ancienne sélection après rattachement.

RISQUES : présenter V1 comme courante sous V2 ; transférer une extraction, un lot ou un accord ; confondre archive reçue et membres admis ; rejouer une mutation avec de nouveaux IDs après UNKNOWN.

POINTS D’INSERTION : commandes/handler et transport d’admission existants, historique Case/DCE et lecteurs ; hook/panneau d’ouverture. Modèles existants, aucune migration prévue. Ne pas modifier les portes ni les règles d’éligibilité.

PLAN MINIMAL : tests rouges ; acte de rectification explicite avec prédécesseur exact et motif, contrat legacy conservé ; invalidation de fraîcheur sans rattachement automatique ; lecture liée à l’Affaire/version exactes et reprise d’intent ; recette native V1/V2 incluant reçus/exclus/non-lus/manquants et lots UNKNOWN si non établis ; contrôles ciblés, navigateur et revue.

TESTS : prédécesseur/tenant/révision refusés, deux rectificatifs concurrents, retry exact/rollback ; absence de données V1 après changement et réponse tardive ; refus d’extraction courant sans recours à l’ancien succès ; historique et manques non hérités.

## Parcours livré

L’ouverture accepte plusieurs fichiers pour une seule version : hash de chaque binaire puis manifeste canonique, staging/transfert de chaque original et admission atomique du corpus. Aucun membre de ZIP n’est automatiquement admis. Les limites locales sont visibles (100 fichiers, 150 Mo par fichier) ; corpus vide, trop volumineux ou contenant des octets dupliqués est refusé avant tout staging.

Le canal RECTIFICATION dispose désormais d’un acte complet : prédécesseur, révision attendue et motif déclarés, confirmation UI liée au propriétaire, à l’Affaire et à la sélection exacte. Le serveur vérifie Patron administrateur, tenant, consultation, révision, lifecycle et intégrité ; le garde s’exécute avant résolution d’un ancien reçu. La sérialisation retire les trois nouveaux champs lorsqu’ils sont absents : les empreintes des admissions legacy sont conservées. Les anciens enregistrements RECTIFICATION sans relation ne sont pas complétés arbitrairement.

Le prédécesseur devient SUPERSEDED/REVIEW_REQUIRED et les Affaires qui lui sont rattachées passent à revoir, avec révision et événements. Leurs rattachements et sources ne sont pas remplacés silencieusement. Le rattachement de V2 reste un acte distinct ; la révision Case exposée dans la projection fermée sert à son contrôle optimiste. Remplacement et rattachement verrouillent la consultation avant les Affaires et versions pour empêcher un rattachement concurrent d’échapper à l’invalidation.

Les lectures sont indexées par propriétaire/Affaire/version/fraîcheur. Une réponse tardive ne remet pas V1 sous V2. Dès l’envoi, les anciennes projections DCE sont suspendues ; UNKNOWN conserve fichiers, corps et identifiants. La reprise saute les phases déjà reçues et vérifie les reçus exacts avant de continuer. Après rattachement connu mais relecture en échec, le retry ne refait que la relecture. Les motifs, fichiers et canaux d’un autre propriétaire restent masqués. L’effet de lecture automatique App est également bloqué pendant pending/busy, y compris au retour sur une Affaire en UNKNOWN.

## Fichiers concernés

- Backend : `dce/application/{commands.py,handlers.py,queries.py}`, `case/application/link_dce_version_handler.py`, `dce/infrastructure/case_assigned_reader.py`, `dce/public/contracts.py`, routes `case_assigned.py` et `dce_versions.py`.
- Frontend : `features/dce/{useDceOpening.ts,DceOpeningPanel.tsx,DceKnowledgePanel.tsx}`, `app/{App.tsx,styles.css}`, `shared/types.ts`, `infrastructure/api.ts` et leurs tests.
- Preuves : nouveaux tests `test_l03_rectification_concurrency.py`, `test_l03_dce_inventory_rectification.py`, `test_rectification_contract.py`, helper `tests/support/l03_dce.py` ; tests d’admission et projection Case ajustés. La projection reste fermée : seule la révision technique est ajoutée ; les champs privés restent exclus.

Aucune dépendance ni migration ajoutée ; tête147 conservée. Les portes, candidats et règles de confidentialité ne sont pas modifiés.

## Preuves exécutées

Racine privée locale : `/home/noor/.local/share/smartao-proofs/l03-dce-inventory-20261103/`.

- **239 tests backend réussis / 56,18 s**, admission, concurrence, HTTP authentifié, Case/lectures, archives, extraction/upload, domaine et architecture. La première campagne238/1 révélait l’ancienne whitelist de projection Case, ensuite explicitement étendue à la révision et revérifiée.
- **74 tests DCE ciblés réussis / 3,78 s**, dont corpus multiple, limites/doublons, confirmation, sources suspendues, propriétaire, réponses tardives, reçus discordants et reprise en lecture. Une régression App complémentaire reproduit le GET automatique avant reçu ; le rejeu Web global final est consigné ci-dessous après sa fin.
- Rouges observés : triade d’admission absente, inventaire V1 conservé sous V2, nouvel intent après UNKNOWN, absence de confirmation/sélection multiple, reçus discordants acceptés, relecture échouée masquée, motif privé exposé au changement de propriétaire, source ancienne restituée pendant UNKNOWN et effet App de lecture non bloqué. Le test de concurrence à deux sessions a reproduit une Affaire CURRENT rattachée à un prédécesseur SUPERSEDED, puis a été observé vert sous verrou commun.
- Les erreurs de montage de fixtures (corpus identique, tentative de modifier un staging CLEAN, acteur différent lors d’un replay, parenthèse de test) sont distinctes des rouges produit. Les gardes SQL n’ont pas été abaissés pour les contourner. Un argument de révision introduit par erreur dans AuthorizationResource a été détecté par mypy/HTTP et retiré ; la révision reste uniquement dans le DTO de projection.
- Recette HTTP native : trois originaux V1 (PDF, ZIP, PNG non lu), lots déclarés2/7, archive non admise et entrée dangereuse exclue, manque CCAP déclaré ; nouveau corpus V2 PDF/ZIP, prédécesseur exact, autres Affaires à revoir, rattachement V2 explicite, manque AE distinct. Documents/constats V1 non hérités, sources historiques conservées ; refus tenant étranger404 et Collaborateur403, y compris sur reçu existant. Hashs binaires et corpus sont ceux des octets effectivement transférés.
- Navigateur : composants et client API de production, Chrome DevTools MCP local isolé/headless, API/TestClient et PostgreSQL réels de fixture via pont HTTP local. Deux fichiers sélectionnés, motif et confirmation, admission native201 masquée503, champs effectivement désactivés et aucune source CURRENT restituée ; retry200 avec corps strictement identique, aucun GET entre UNKNOWN et reçu, puis rattachement et relecture V2. SQL final : deux versions, l’autre Affaire demeure sur V1/REVIEW_REQUIRED. Les originaux V1 sont absents de l’inventaire V2 ; exclusions, AE et analyse complète non démontrée restent visibles.
- Captures finales inspectées en bureau et mobile : largeur1280 puis393, aucun débordement, cookies/localStorage/sessionStorage vides, aucune ressource de page externe observée. Ce constat ne garantit pas tout trafic OS. Une tentative antérieure a expiré avec le pont de qualification et fini en502 après nettoyage de sa base : elle reste non concluante. Une assertion vérifiant `input.disabled` au lieu de l’état effectif `:disabled` du fieldset a été corrigée ; le parcours final est un nouveau rejeu complet sur base vide.
- Python : Ruff/format ciblés ; mypy app/tests206 diagnostics dans40 fichiers sur1264 sources, identités normalisées identiques à la preuve L02 (aucune nouvelle dette). Types/lint/build Web vérifiés ; avertissements préexistants setDecisionDossier et chunk>500kB. Aucun backend complet revendiqué.

## Limites et reports

L03 général reste PARTIAL. Les lots2/7 sont déclarés dans la consultation/portée de fixture ; l’applicabilité de chaque pièce et la criticité restent UNKNOWN. La recette ne prouve ni l’exhaustivité d’un DCE réel, ni sa validité officielle, ni OCR/raster/tableaux complexes. Les membres d’archives non admis ne deviennent pas des pièces analysées. Une extraction n’est pas une analyse complète. Les déclarations manquantes ont une source non qualifiée explicitement UNKNOWN.

La fixture emploie l’inspection MIME native mais un scanner synthétique CLEAN ; aucune preuve ClamAV réel. Les extracteurs natifs sont pilotés localement après admission dans le pont de qualification : aucune livraison de worker déployé ou exploitation réelle n’est déduite. La preuve navigateur concerne les composants intégrés, pas l’authentification humaine complète de l’application ; aucun Playwright MCP disponible. Les périodes UNKNOWN sont qualifiées dans les vues DCE, pas comme gel universel de tous les écrans métier.

Les intents restent en mémoire de la vue, sans reprise garantie après reload/unmount/changement de session. Le retry d’une admission ou relecture est qualifié ; une interruption du PUT binaire peut rester bloquée/refusée et n’est pas annoncée récupérable automatiquement. Une Affaire sans consultation liée conserve son refus visible ; aucun lien amont L01→consultation n’est inventé. Les profils, décisions et accords historiques ne sont pas transférés au corpus nouveau.

Superpowers using-superpowers/brainstorming/writing-plans/TDD/systematic-debugging/requesting-code-review et ECC product-capability/verification-loop appliqués. Revue indépendante serveur : course trouvée et corrigée, garde avant reçu vérifiée ; revue UI : appel automatique trouvé et corrigé. Revues statiques, pas validations humaines. OpenDesign Local : catalogue courant, artefact C08 et système consultés, conventions existantes conservées ; Impeccable context/polish/craft-floor et contrôle borné. Graphify interrogé avant recherche manuelle. Serena non requis pour ces lectures sans navigation sémantique ; aucune nouvelle API externe à inférer via Context7 ; Jev/Manus/GitHub non employés, travail local borné. Basic Memory reste le miroir du plan, pas l’autorité.

A1 non admis, A2 HOLD, B0/B1/B2/P0–P7 et NO-GO public conservés. Aucun live, corpus réel, VPS, dépôt externe, commit, push ou effet externe. Bases propres `l03_dce` et `l03_browser` revenues à0 table métier/0 version Alembic, seul conteneur propre arrêté/supprimé ; preview et navigateurs de qualification fermés, services utilisateur préservés.

## Vérification finale

**92 fichiers Web réussis, 757 tests réussis / 4 ignorés, 226,34 s**, sur les sources figées incluant le garde de lecture automatique App ; types, ESLint et build finaux verts (avertissements historiques précités). Backend final239/56,18s inchangé. Format Python et `git diff --check` verts.

Semgrep1.183.0, configuration `p/security-audit`, métriques désactivées, `--no-git-ignore` : **99 règles exécutées sur25 chemins, 0 finding, 0 erreur**. Analyse locale, aucun envoi de résultats ; pas une certification sécurité. Impeccable : quatre avertissements sur les règles CSS antérieures lignes2/154/216/389, aucun sur les nouvelles règles de retour à la ligne ; pas de refonte hors périmètre.

Le dernier garde App ne fait pas partie du harnais navigateur de composants ; sa régression rouge a été observée et le global Web final le couvre. Les composants, le client API et le parcours natif qualifiés par le navigateur sont inchangés. Le delta est relu contre les copies du WIP, non contre HEAD seul ; aucun motif de secret ajouté détecté.
