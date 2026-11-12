# L08 — couverture sourcée de la réponse sélectionnée

## Cadrage et plan de réalisation

Autorité : prochaine étape unique du plan global, PF31-03/07/09, M31-02 et CT31-36–42. Checkout principal, WIP préservé; aucun commit/push, moteur activé ou acte réel.

**AS-IS :** contributions Markdown et régions DOCX exactes existent, ainsi que sélection, revue, snapshot et ZIP. Il manque une confrontation lisible avec toutes les exigences de la lecture DCE native. Les références de preuves entreprise ne prouvent pas leur inclusion dans le ZIP.

**Risques :** compter une alternative non choisie, une contribution source absente du DOCX, une preuve citée comme annexe livrée, une signature ou une applicabilité de lot déduite; masquer les exigences sans réponse; exposer des données financières ou inter-tenant; conserver une lecture après changement de contexte.

**Points d'insertion :** lecture fermée DCE, `response_artifact.py`, reconstruction `buyer_docx_sources.py`, services et routes preparation, panneau de revue/wizard existants. Pas de migration ou dépendance nouvelle prévue. Les contrôles P0–P7 restent indépendants.

**Plan minimal :**

- [x] Écrire et observer les régressions rouges de la projection exhaustive des exigences non financières, sur une seule sélection ID/version/SHA.
- [x] Résoudre les octets et sources courants; confronter les contributions/régions effectivement présentes aux exigences. Exposer liens, manques, lot candidat sourcé et applicabilité/signature UNKNOWN. Les annexes citées restent explicitement non incluses tant qu'aucun manifeste ne le prouve.
- [x] Exposer la lecture aux acteurs déjà autorisés via les services/routes natifs, sans acte métier ni nouveau pouvoir.
- [x] Après consultation OpenDesign Local Codex et Impeccable, raccorder la lecture au choix exact dans le parcours existant, avec refus des réponses tardives et états incomplets visibles.
- [x] Qualifier les parcours synthétiques Markdown/DOCX, ZIP technique exact et refus de reprise de l’ancienne couverture après rectificatif (pli acheteur complet toujours ouvert); vérifier types/lint/build, suites appropriées, Semgrep, diff et absence de secrets.
- [x] Mettre à jour preuves, index, plan et miroir Basic Memory avec les limites mesurées.

**Tests à ajouter :** exigence omise; texte avec manque déclaré; pièce sélectionnée vs alternative; DOCX ne contenant qu'une partie des contributions source; région UNKNOWN; hash/source/version périmés; tenant/rôle/affectation; DCE rectifié; lecture répétée sans écriture; signature UNKNOWN; aucune annexe déduite d'une citation. La présence textuelle est distincte de la conformité et de l'exhaustivité documentaire.

## État des preuves

Orientation seule à ce stade : branche/HEAD conformes au checkpoint exact; les 605 fichiers du manifeste de passation ont le même SHA-256. Aucune nouvelle suite applicative exécutée à ce point. Basic Memory MCP absent de la session; checkpoint exact lu par CLI local dans le projet `smart-ao-v8`. Graphify historique consulté, Serena activée. OpenDesign MCP en cours de diagnostic avant toute édition UI.

## Implémentation et premières preuves

La lecture native `/api/v1/preparation/{package_id}/response-coverage` et sa variante Collaborateur confrontent une seule sélection ID/version/SHA à tous les signaux DCE non financiers de la lecture fermée. Le POST est une lecture sans commande, reçu ni écriture métier. Les autorisations existantes précèdent la résolution; tenant/package, affectation, état DCE, version du plan, octets et sources sont recontrôlés. Réponse privée `Cache-Control: no-store`.

Le résultat distingue `TEXT_PRESENT`, `TEXT_WITH_GAPS`, `MISSING` et `UNKNOWN`. La conformité/couverture, l'applicabilité du lot et la signature restent UNKNOWN. Les lots affichés sont exclusivement des candidats sourcés déjà produits par la lecture native. Un DOCX ne compte que ses régions réellement liées, pas toutes les contributions du Markdown source. Chaque lien expose section, locator, SHA et offsets de la contribution Markdown ou hash de texte de région DOCX. Les preuves entreprise citées gardent ID/SHA/exigence/section; leur inclusion au ZIP reste UNKNOWN. Aucun nouveau mécanisme d'annexe n'est inventé.

Le panneau est raccordé à la pièce choisie du Wizard et à la revue Patron. Il permet le filtre par lot candidat/lot UNKNOWN, montre chaque exigence sans réponse et ses sources; un changement de sélection/propriétaire/API masque la lecture, même après retour au même contexte. Les réponses tardives sont écartées. Réutilisation des classes existantes, simple règle de reflow/hash et cible44px; pas de nouvelle palette ni de refonte globale.

Deux défauts ont laissé des rouges reproductibles puis des verts : le lecteur de contributions rejetait un brouillon existant contenant seulement un manque (ligne blanche avant le marqueur UNKNOWN); le nouveau calcul confondait tout manque humain commençant par « UNKNOWN — » avec le seul placeholder automatique. Le lecteur partagé accepte uniquement la forme historique exacte; le calcul compare le placeholder complet.

- 56 tests rapides backend réussis (application, contrats API existants, architecture); 28 application/OOXML/architecture réussites également, avec recouvrement, non additionnés.
- 5 parcours natifs réussis en90,39s : contributions, isolation, version exacte, lecture sans effet, invalidation après remplacement DCE synthétique; sélection Markdown/DOCX, revue, P5/ZIP et document Conducteur exacts. Le remplacement de registre synthétique prouve le refus de réutiliser l'ancienne réponse, pas un nouvel import DCE réel.
- Web final figé :709 réussites/4ignorés/89fichiers,168,15s, un worker. Le run initial parallèle a été interrompu sous pression mémoire. Le run intermédiaire sans gel n'est pas substitué au final.
- TypeScript et build vérifiés; chunk883,52kB (>500kB). ESLint :0erreur, avertissement App historique sur `setDecisionDossier`. Ruff/format ciblés verts. Mypy application697sources sans diagnostic; app+tests :206diagnostics/40fichiers, mêmes identités que la baseline, aucune nouvelle dette. Deux assertions explicites de non-None et un nom local distinct dans la fixture de qualification ont rétabli ce contrôle; aucun changement applicatif associé.
- Chrome DevTools Local, contexte isolé :33exigences natives enregistrées,31manquantes/2textes avec manques,2annexes citées, filtres lots1/UNKNOWN et retour intégral, réponse périmée, lecture tardive/session, masque Patron, reflow390/1280sans débordement et bouton44px. Six requêtes de recette, une même sélection exacte, aucun token/cookie/requête externe. Le composant/API client sont réels; le navigateur reçoit une projection synthétique enregistrée depuis le test natif, pas une API métier live. Aucun Playwright MCP utilisé.
- Semgrep1.182.1, `p/security-audit`,99règles/17fichiers :0finding/0erreur. Scan local, métriques désactivées, aucune publication. Detect-secrets ciblé :0. Impeccable mécanique ciblé :0; audit borné lisibilité/reflow/contrôles, pas conformité WCAG globale.

## Incident de recette et vérification restante

La globale backend sur le premier conteneur jetable a rencontré une saturation du tmpfs768MiB : le WAL PostgreSQL par défaut a rempli le stockage, puis PostgreSQL est tombé en récupération/arrêt (`No space left on device`). Les erreurs de connexion en cascade et deux parcours supplémentaires exécutés pendant cette panne ne sont pas des preuves PASS. Logs conservés. Aucun stockage réel touché.

Un conteneur jetable distinct a été créé sur le port local5549, tmpfs1536MiB, WAL64MiB/min32MiB et checkpoint30s, paramètres WAL cohérents avec l'ancienne recette qualifiée. La globale backend est relancée avec arrêt au premier échec; résultat en attente. Aucun verdict global backend nouveau à ce stade.

## Méthode, revue et limites

Skills réellement appliquées : `bm-orient`; Graphify existant historique; Superpowers `using-superpowers`, cadrage `brainstorming` borné, `writing-plans`, `test-driven-development`, `systematic-debugging`, `requesting-code-review`, `verification-before-completion`; ECC `verification-loop` et `security-review`. Serena initialisée/activée. Le reviewer indépendant a transmis le contre-exemple du préfixe UNKNOWN puis sa session a échoué sur une limite d'usage : revue partielle seulement, pas approbation indépendante finale.

OpenDesign local existant rétabli via Node24 et son daemon; catalogue courant des skills/design systems et système Application consultés, artefact C10 `plan-reponse-c10.html` relu. Conservation de l'interface et des tokens présents, sous l'autorité visuelle Owner Cytd; aucune génération supplémentaire, aucun Cloud/compte/crédit/BYOK. Impeccable `context`, `craft-floor`, audit et `detect` consultés/exécutés; aucun init, PRODUCT/DESIGN ou hook ajouté.

Context7 n'a pas été nécessaire pour une nouvelle API de bibliothèque : contrats internes et interfaces installées réutilisés. Jev/Manus sans besoin de classification/délégation distant; GitHub sans action distante autorisée. Le checkpoint Basic Memory exact a été lu par CLI locale, le MCP Basic Memory n'étant pas exposé.

La fonction est une confrontation sourcée des signaux connus, pas une preuve d'exhaustivité du DCE ou de conformité du pli. Les annexes ne sont pas sélectionnées/embarquées par cette évolution; les cadres arbitraires/PDF/signatures et le ZIP acheteur complet restent ouverts. Aucun moteur candidat, porte P0–P7, dépôt humain, schéma/migration ou dépendance modifié. L08 général reste PARTIAL, A1 non admis/A2 HOLD/NO-GO public; aucun commit/push/live/corpus réel/VPS/déploiement/P3réel/dépôt externe.

## Extraits lisibles — complément du 28 octobre 2026

La confrontation affiche aussi l'extrait acheteur, pour éviter une liste d'UUID sans sens métier. Le raccord réutilise `contribution_source_snapshots` : confirmation/source courantes, bornes UTF-8, hash du fragment et garde de confidentialité existants. Aucun nouveau parseur ou privilège. Une projection indisponible reste « Texte source non projeté · UNKNOWN ».

Rouges vérifiés : API `KeyError: source_excerpt`, et assertion UI sur le texte absent. Après implémentation :5parcours natifs verts/74,87s,6tests du panneau verts, puis globale Web710réussites/4ignorés/89fichiers/196,72s. Types, lint/build et Impeccable ciblé vérifiés; chunk883,67kB. La première globale backend complète s'est achevée4035/2avertissements/1293,98s, avant ce dernier raccord; elle n'est pas substituée à la globale du code final relancée ensuite.

Recette Chrome DevTools Local mise à jour :33exigences/31extraits lisibles/2extraits UNKNOWN,31réponses manquantes/2textes avec manques, sources et annexes citées conservées; filtres, rejet tardif après changement de session et source périmée, reflow390/1280sans débordement, aucune ressource externe/cookie. Cinq requêtes du même triplet exact sans bearer/cookie. Les31extraits enregistrés repassent le garde `contains_forbidden_text`; aucune famille DPGF/BPU dans la projection. Les deux captures actualisées ont bloqué côté outil et n'ont pas été obtenues malgré une tentative corrigée; les assertions DOM ont réussi et l'onglet a finalement été fermé. Les captures précédentes restent historiques, avant ce raccord.


## Résultat final du code figé — 28 octobre 2026

Backend complet : **4035 réussites,3 avertissements,1568,20s (26:08),exit0**, sur le code final incluant les extraits lisibles. Web complet : **710 réussites,4ignorés,89fichiers,196,72s,exit0**, un worker. Les17empreintes logicielles sont identiques avant/après ces suites. Les avertissements backend sont Starlette/httpx et les alias Pydantic `case_id`/`authorization`; ils ne sont pas masqués. Les deux bases `smartao_coverage_test` et `smartao_coverage_delta` sont revenues à0table métier et0révision Alembic. Tête source unique0146 inchangée. Aucun verdict CI/exploitation ou conformité du pli complet n'est déduit.

Mypy final :697sources applicatives sans diagnostic; application/tests206diagnostics/40fichiers, mêmes identités que la baseline,0nouvelle dette. Ruff/format ciblés, TypeScript, ESLint/build final vérifiés; seul avertissement App historique, chunk883,67kB. Semgrep final1.182.1/99règles/17fichiers/0finding/0erreur; aucune exclusion rapportée, analyse locale et métriques désactivées. Detect-secrets ciblé0; Impeccable ciblé0. Les résultats antérieurs/interrompus ne sont pas ajoutés au décompte final.

Le plan est mis à jour en gardant L08 comme seule tranche active. La suite concerne la sélection/inclusion effective des annexes et la qualification du pli après rectificatif; ce dossier ne prétend pas livrer ces fonctions. Le ZIP technique exact et son document Conducteur sont qualifiés dans les parcours natifs, pas un ZIP acheteur exhaustif ou signé.

Preuves privées et delta de travail : `/home/noor/.local/share/smartao-proofs/l08-coverage-20261027/`. Les reçus finaux de nettoyage et de synchronisation Basic Memory sont enregistrés dans ce dossier; le plan reste l'autorité de statut. Aucun commit/push ou nouveau checkout.


Nettoyage final confirmé : deux bases à0table métier/0révision puis suppression des deux conteneurs jetables créés ici, sans montage persistant; serveur Vite5198 arrêté et onglet de recette fermé. Le daemon OpenDesign local rétabli reste disponible comme outil. Miroir Basic Memory mis à jour par écriture conditionnelle sur checksum puis relu; prochaine étape et SHA du plan concordants. Le premier refus `NOTE_PATH_CONFLICT` n'a rien écrit; le dossier relatif `codex/SMART_AO_V8` a permis la mise à jour du même permalink, sans note dupliquée. Reçus `cleanup-final.json` et `memory-sync-final.json` dans le dossier de preuves. Les archives initiales605fichiers restent intactes; le delta courant est archivé séparément. Aucun commit/push.
