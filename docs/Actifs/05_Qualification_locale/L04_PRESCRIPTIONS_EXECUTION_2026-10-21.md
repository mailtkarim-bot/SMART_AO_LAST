# L04 — prescriptions et contraintes d’exécution sourcées —21/10/2026

## AS-IS, risques, insertion et plan

Objectif autorisé : alimenter le dossier L04 et le parcours humain existant avec les faits techniques/logistiques/planning-HSE/paiement/réception omis. Réutiliser observations, matérialisation, provenance, actes et revue12axes. Aucun nouveau contexte, moteur candidat, pouvoir de confirmation ou porte.

Six catégories fermées de signaux à revoir, sans applicabilité ni valeur numérique inférée : TECHNICAL_PRESCRIPTION, LOGISTICS_CONSTRAINT, SCHEDULE_CONSTRAINT, HSE_CONSTRAINT, PAYMENT_TERM_SIGNAL, ACCEPTANCE_TERM_SIGNAL. Axes natifs respectifs TECHNICAL, CONSTRUCTIBILITY, CAPACITY, HSE, CASH, RIGHTS. Les conséquences restent des déclarations humaines distinctes.

Les mots-clés seuls ne prouvent pas une obligation. Limiter les règles à des constructions explicites et familles non financières, conserver citations UTF8/conditions/négations; UNKNOWN sur portée ou lecture non prouvée. Les anciens analyseurs conservent leur validation historique. Migration additive de contraintes fermées, downgrade peuplé refusé, aucun effacement de preuve.

- [x] Développement distinct : tests rouges sur six familles, ambiguïtés, négations/conditions et ancres; aucun réglage sur les anciens holdouts.
- [x] Analyseur version7, contrats/types persistés, migration0139, matérialisation et projection source/lot vers douze axes; aucune confirmation automatique.
- [x] Extraction→matérialisation→traitement humain de tous les points→préparation/revue sur PostgreSQL jetable; source obsolète/isolation/append-only/concurrence et rollback qualifiés.
- [x] Libellés dans le panneau existant après consultation OpenDesign Local; test client et lecture navigateur synthétique. Aucun redesign.
- [x] Nouveau jeu gelé après code, tests appropriés et revue; mise à jour plan/index/matrice/mémoire locale, cleanup. Les anciennes preuves restent historiques.

A1 non admis, A2 HOLD, NO-GO public; DPGF non évaluable par RAG. Aucun live/corpus réel/VPS/déploiement/P3/dépôt externe/commit/push; WIP principal conservé.

## Résultat fonctionnel local

Six types de signaux d’exécution source-only codés (technique, logistique, capacité/planning, HSE, paiement, réception) dans l’analyseur natif v7; contraintes SQL migrées vers0139 avec refus de downgrade peuplé. Les11 faits absents du jeu de développement sont maintenant présents (32/32points historiques et nouveaux), et15/15points du nouveau DCE synthétique gelé sont retrouvés sans point parasite mesuré. Types/axes, source/version/hash/ligne/offsets et portée lot candidate ou UNKNOWN contrôlés; négations/conditions UNSPECIFIED et applicabilité UNKNOWN jusqu’à acte humain. Sur PostgreSQL jetable,15points ont été traités, puis dossier12axes préparé/revu sur SHA exact,17actes uniques vérifiés en navigateur via vraies routes TestClient. Aucun GO métier ni analyse exhaustive déduits.

### Code et limites sémantiques

- Règles natives v7 `DCE_*` bornées aux familles de pièces non financières; anciennes versions1–6 validées selon leurs propres règles. Six types physiques/publics et projection vers TECHNICAL,CONSTRUCTIBILITY,CAPACITY,HSE,CASH,RIGHTS. Chaque point est PENDING_HUMAN_CONFIRMATION et SOURCE_SIGNAL_ONLY; pas d’exécution d’action ou de confirmation implicite.
- Retour ligne conservé dans une clause et offsets UTF8 exacts; exemples/lexiques refusés à l’extraction et en relecture de preuve. Deux défauts P2 relevés par revue indépendante, reproduits par tests rouges, corrigés et contre-vérifiés. Conditions/négations gardées dans l’extrait; obligations et portées ambiguës restent UNSPECIFIED/UNKNOWN. Les nombres «28 jours» et dates de planning ne deviennent ni échéancier, ni effet juridique ou financement calculé.
- Migration139 élargit seulement deux contraintes fermées, conserve les anciennes lignes, et refuse le downgrade contenant de nouveaux signaux. Le test de données historiques descend/revient sans les effacer. Runtime head, modèle et contrat de migration alignés; aucun schéma de production touché.
- Panneau existant : six libellés français « à revoir », localisation native (page, ligne, paragraphe, cellule) seulement lorsqu’elle est prouvée, hashes longs repliés sur mobile. Système visuel Owner/CYTD conservé; OpenDesign Local et Impeccable consultés, aucun prototype supplémentaire ou mode Cloud. La source reste consultable par rôle Patron avec la même politique financière.

### Preuves exécutées

- Développement : huit pièces synthétiques texte UTF8,32points attendus dont11nouveaux; qualification source/axe/type/lot et contradictions sans ajout de faux point sur ce jeu. Aucun fait n’a été injecté dans les registres de résultats : extraction, analyse, matérialisation et lecture natives ont été exécutées.
- Nouveau jeu gelé après le code : huit pièces texte, lots5/9 et15points attendus dont12signaux d’exécution; quinze détectés, aucun point parasite mesuré. Source/document/version/hash/ligne contrôlés. Portées explicites candidates; portée d’une négation, d’une condition ou d’une phrase mêlant deux lots laissée UNKNOWN. Ce jeu est synthétique et rédigé par le même agent : indépendance humaine/statistique non revendiquée.
- SQL ciblé :7tests sur les deux dossiers, traitement humain de chaque point, préparation/revue exacte, retry idempotent, refus downgrade peuplé et roundtrip historique. Gate élargi :30tests avec gardes C10, migrations et registre L04. Suite backend finale : **3725 passés/2avertissements/852,59s/exit0**. Le résultat ne valide pas tous les CDC ni une base réelle.
- Web : **626passés/4ignorés/74fichiers** sur runner séquentiel borné; 23tests du panneau ciblés, types/lint/build verts. L’exécution parallèle initiale a eu des timeouts sans qualification; les assertions et seuils sont restés identiques pour la suite verte. Avertissement historique de taille de bundle conservé.
- Navigateur isolé Chrome DevTools MCP, vraie API TestClient synthétique et PostgreSQL jetable sur les mêmes identifiants :12contrôles du parcours complet,15saisies/2actes de dossier, cinq contrôles mobiles à390px, puis vérification de15localisations «ligne» et du refus Collaborateur403. Même SHA avant/après revue, EMPTY/UNKNOWN visibles,0débordement de page. `browser-sql-consistency.json` relie15POST/15lignes et2POST/2lignes; aucun cookie/bearer navigateur. C’est une simulation de geste humain, pas une validation métier humaine.
- Ruff, format, mypy650sources, git diff --check et Impeccable détecteur vérifiés. Semgrep1.179.0/225règles/18fichiers, dont les2fichiers UI rescannés après le dernier changement :0finding/0erreur. Détecteur de secrets :8SHA256 publics des pièces synthétiques triés,0résultat non trié. Une revue de code indépendante ne remplace pas le jugement métier.

Preuves privées : `~/.local/share/smartao-proofs/l04-execution-20261021/` (source/holdout gelés, tests rouges et verts, rapports SQL, logs des suites, transcriptions API et navigateur, revue/scan). Le premier essai web parallèle, les échecs de mise en route du connecteur visuel et les preuves intermédiaires ne sont pas des résultats produit; la qualification citée ici utilise les runs finaux détaillés.

### Restes ouverts

L04 global reste PARTIAL. Les expressions au-delà de ces règles lexicales, les tableaux/graphes/raster, PDF/DOCX/XLSX mixtes, rectificatifs et historique croisé de ce nouveau parcours restent à éprouver. Les pièces complètes du DCE réel et leur droits/anonymisation ne sont pas admis au Golden DCE. Aucun calcul de coût/délai/risque ou applicabilité réelle n’est déduit des citations. Une source non lue reste non lue; une condition sans preuve reste UNKNOWN. Le rollback de l’ancien binaire sur ces nouveaux types n’est pas qualifié : downgrade peuplé refusé.

DPGF non évaluable par RAG, profils candidats inactifs, A1 non admis, A2 HOLD, NO-GO public. Aucun backend live, corpus réel, VPS, déploiement, P3, dépôt externe, commit ou push. WIP principal et HEAD conservés. Basic Memory externe non synchronisée; miroir local préparé. Ressources de recette fermées et bases jetables vérifiées Alembic0 ci-dessous.

Prochaine étape : L04 — qualifier le dossier d’analyse sur un DCE synthétique multi-formats et son rectificatif : préserver pièces non lues, points source/version/lot, reprises de traitement, historique et revue Patron, puis corriger les ruptures sans admission ni activation de candidat.

### Fermeture et méthode

Les bases smartao_l04 et smartao_l04_browser ont été vérifiées Alembic0 après les suites. Le seul conteneur PostgreSQL dédié a été arrêté et son ACL UID70 retirée (répertoire socket700). Adaptateur Unix arrêté proprement, onglet Chrome isolé fermé, passerelle navigateur et serveur Vite arrêtés. Aucun objet réel ni secret utilisé. Les27hashes source/test/fixture finaux restent identiques après gel de livraison. `git diff --check` et contrats documentaires47/47 verts; HEAD30f2693/WIP conservés.

Skills et outils : Superpowers using-superpowers, cadrage borné, plan, TDD et revue/vérification; ECC database-migrations et verification-loop. Graphify consulté en premier (graphe historique, code courant autoritaire). OpenDesign Local consulté sur catalogue courant et artefact SMART AO, système Owner/CYTD confirmé; Impeccable context/craft-floor/detect utilisé, détecteur final vide. Chrome DevTools MCP isolé, aucun Playwright MCP disponible. Serena non requis faute de navigation sémantique; Jev/Manus non sollicités pour ces tests déterministes. Aucun changement de bibliothèque/API nécessitant une recherche externe : CLI/options interrogés sur les installations locales. Miroir Basic Memory privé non transmis; plan source unique du statut.
