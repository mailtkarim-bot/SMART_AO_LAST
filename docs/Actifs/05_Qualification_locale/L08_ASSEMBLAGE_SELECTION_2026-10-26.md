# L08 — document multi-contributions et sélection exacte

## AS-IS

L’assembleur natif `build_response_plan_draft` couvre les contributions de chaque couple exigence/section d’un plan. Le Wizard permet déjà leur saisie. La revue Patron vise un ID/version/hash exact. Le snapshot lit tous les brouillons courants, puis refuse des textes différents : aucun choix explicite ne peut encore atteindre transmission/P5/ZIP/passation. Le graphe existant a été interrogé; les sources actuelles font autorité.

## Risques et points d’insertion

Conserver les reçus/idempotences historiques, la portée tenant/Affaire/package/plan, les sources d’exigence et d’entreprise, les revues exactes et UNKNOWN. Une sélection n’est ni une revue ni une autorisation P5. Réutiliser contrats/commandes de snapshot, handler, lecteur d’origine C10 et Wizard existants; pas de nouveau moteur, registre ou migration prévu.

## Plan minimal et preuves

- [x] Reproduire le refus de sélection explicite; conserver la sérialisation historique sans nouvelle valeur.
- [x] Coder la référence exacte sélectionnée et la figer dans le manifeste; revalider le même choix à la transmission et chez Submission.
- [x] Qualifier un document réunissant plusieurs contributions et un autre brouillon concurrent, avec revue Patron, sources/manques, retries et refus de version/hash/contexte.
- [x] Livrer la sélection lisible dans le Wizard existant, après consultation OpenDesign Local/Impeccable; préserver les intentions UNKNOWN.
- [x] Prouver les octets jusqu’au ZIP et à la passation, exécuter consommateurs/contrôles/revue/scans, nettoyer les ressources puis mettre à jour plan et miroir Basic Memory.

Essais locaux synthétiques uniquement. Aucun commit/push, live, corpus réel, VPS, déploiement, effet P3 réel, dépôt externe ou GO public. A1 non admis, A2 HOLD; DPGF non évaluable par RAG, candidats inactifs. Le plan global garde seul le statut et la prochaine étape.


## Journal en cours

Le contrat a d’abord refusé le nouveau champ (rouge), puis accepte le triplet explicite tout en omettant le champ None pour préserver les anciens hashes de retry. Snapshot, transmission et lecteur C10 Submission utilisent la même sélection; le manifeste du snapshot la fige. Les alternatives non sélectionnées ne deviennent ni revues ni sources du document choisi.

Scénario natif réussi29,22s : corpus de développement copié en dossier temporaire, une deuxième clause ajoutée et son hash recalculé sans modifier le gold; deux contributions sourcées et une alternative concurrente, revue Patron du document choisi, même texte jusqu’au ZIP et conducteur. Puis23tests de consommateurs/contrats réussis54,30s, avec refus ID/version/hash. Deux rouges UI reproduisent les reçus tardifs après changement d’Affaire; les guards réutilisent le scope existant, avec abandon de l’affichage tardif et maintien du même triplet pour UNKNOWN dans son contexte.30tests Wizard passent après correction.

OpenDesign Local : catalogue courant, projet C10 et prototype `plan-reponse-c10.html` consultés; direction existante conservée, aucun nouveau système/palette/Cloud. Impeccable context et craft-floor appliqués au panneau existant. Les suites globales précédentes T01–T03 sont historiques pour ce nouveau code; aucune globale L08 actuelle revendiquée.


## Point de reprise — gel final

La recette native a mis au jour une projection Collaborateur sans hash/plan/contenu. Test HTTP rouge puis getter `read_package_with_verified_drafts`, autorisé par le lecteur de package existant, vérifiant taille100k/hash/UTF8/non-financier; artefact manquant/corrompu rendu avec contenu UNKNOWN, non sélectionnable.27routes puis30tests natifs/API passent; la copie du corpus de développement, ses deux clauses/propositions et l’alternative concurrente ne modifient aucun gold.

Les trois P2 de revue UI sont corrigés : Maps en mémoire par propriétaire/Affaire/package gardant les intentions/reçus, relectures post-acte et GET manuels protégés par contexte/séquence, conflits409 inconnus conservés. Un refus terminal connu ne libère l’intention qu’après relecture réussie. Les408/429 restent UNKNOWN; quatre rouges supplémentaires avant cette correction. Ancien aperçu/package masqué immédiatement au changement d’Affaire/propriétaire. La sélection du plan enregistré reste distincte de la couverture complète exigée pour créer un nouveau brouillon : aucun assouplissement de ce dernier contrôle.

Chromium isolé via Chrome DevTools MCP :29contrôles qualifiés, API ASGI native en processus et PostgreSQL séparé, SHA affiché recalculé identique au brouillon revu, deux contributions/manques UNKNOWN lisibles, réponse perdue après commit, retour A→B→A puis deuxPOST strictement identiques. DB :un seul snapshot et une seule transmission; le Patron relit le triplet choisi et un seul brouillon dans le manifeste. Desktop1280/mobile390 sans débordement, rôle/session masqués, aucun cookie ni Authorization dans le navigateur, ressources locales uniquement. Les deux appels de sélection de rôle avec valeur interne erronée sont des erreurs de pilote conservées, exclus du verdict; actions corrigées avec libellés observés, assertions positives rejouées.

Nettoyage navigateur natif : DB `smartao_l08_browser` revenue àbase0 après effacement explicite des seules données jetables, puis downgrade; le premier downgrade avait correctement refusé la perte de preuves avant truncate, aucune migration modifiée. Vite et Chromium de recette fermés. `smartao_l08_assembly` reste réservée aux tests. **Seule orchestration actuelle :96096**, `final-selected-consumers.log` puis `backend-global-final.log` si ciblé vert. Premier `backend-global.log` interrompu proprement2572réussites/1057,27s/exit2, non qualifiant. Web historique691/4ignorés; seul `web-global-final.log` qualifie le dernier code.19fichiers logiciels figés dans `source-sha256-final.json`. Attendre verdicts et nettoyage final avant clôture.


## Résultats sur le gel logiciel

Les138tests ciblés finaux passent104,04s/1warning; la suite Web complète finale passe695réussites/4ignorés/85fichiers/196,32s. La correction supplémentaire408/429 a eu quatre rouges avant sa requalification. Types/lint/build Web verts, avec le warning App historique et le chunk volumineux; mypy application/tests garde206diagnostics/40fichiers hors raccord, application692sansdiagnostic.19SHA stables et Ruff13Python passent; Semgrep et secrets ciblés ne signalent aucun finding ni erreur. La globale `backend-global-final.log` reste en cours et ne peut pas être remplacée par ces nombres.


## Bilan final — qualification locale du 27 octobre 2026

La suite backend complète passe **4 011 tests, 1 avertissement Starlette/httpx, 1 586,07 s, exit0** (`backend-global-final.log`). La suite Web finale passe **695 tests, 4 ignorés conditionnels, 85 fichiers, 196,32 s, exit0**. Les138tests ciblés finaux ont passé104,04s avant la globale. Aucun résultat de run interrompu n’est ajouté ou substitué à ces verdicts.

**Résultat utilisateur livré.** L’assembleur existant réunit les contributions par exigence/section, leurs sources et leurs manques. Le Collaborateur peut relire les octets vérifiés de ses brouillons possédés puis choisir un assemblage exact ID/version/SHA. Le snapshot fige ce choix et la transmission ainsi que le lecteur C10/P5 le revalident; la revue Patron de cet assemblage reste obligatoire. Le test de développement utilise deux clauses/propositions distinctes et une alternative non revue : les deux contributions choisies arrivent au ZIP et au conducteur, l’alternative reste exclue. Aucun gold métier n’a été modifié. Sans sélection explicite, la sérialisation et le parcours historiques sont conservés; aucune fusion arbitraire ni nouvelle autorisation implicite.

**Contexte et récupération.** Les intentions/reçus restent en mémoire par propriétaire/Affaire/package, sans stockage navigateur persistant. Un UNKNOWN survit à A→B→A avec le même corps, IDs et sélection. Les408/429 et409 non qualifiés restent UNKNOWN; un refus terminal connu ne libère l’intention qu’après relecture réussie. Les réponses POST et GET tardives sont ignorées hors contexte; package, aperçu et choix précédents sont masqués dès le changement d’Affaire/propriétaire. La sélection d’un assemblage enregistré n’assimile pas un plan partiel à une couverture complète : le contrôle existant de création du brouillon reste inchangé, les choix non enregistrés ne sont pas inclus.

**Preuves et vérifications.**29contrôles Chrome DevTools MCP dans Chromium isolé, avec l’API native ASGI en processus et un PostgreSQL dédié : SHA du texte affiché recalculé par WebCrypto et concordant avec le texte revu, perte de réponse après commit, deuxPOST strictement identiques, un seul snapshot et une seule transmission comptés en DB, relecture Patron du triplet figé, masquages, aucun cookie/Authorization dans le navigateur, ressources locales et géométrie390/1280sans débordement. Les traces d’appels de pilote incorrects sont conservées comme erreurs d’action non qualifiantes; les contrôles qualifiés ont été rejoués après correction, et ne contiennent aucun échec. Cette recette ne prétend pas être un Playwright MCP, absent de la session, ni une recette live.

Les19empreintes logicielles correspondent au gel. Ruff et format13Python passent, application mypy692fichiers sans diagnostic; app/tests206diagnostics dans40fichiers hors raccord, CI entière non qualifiée. Types/build Web passent, lint0erreur/1warning App hors raccord; chunk866,24kB. Secrets19fichiers0finding. Semgrep1.182.1,99règles utiles/19fichiers,0finding/0erreur; analyse statique bornée, pas preuve de sécurité exhaustive. Impeccable0finding sur le périmètre. Revue indépendante des sélections, getter et corrections UI : aucun P1/P2 concret résiduel identifié; la revue n’a pas exécuté la DB.

**Nettoyage vérifié.** `smartao_l08_assembly` et `smartao_l08_browser` ont chacune zéro ligne Alembic après teardown. Le premier arrêt de l’adaptateur navigateur a correctement rencontré la barrière de perte de preuves faute de truncate; le nettoyage a été corrigé sur la seule base explicitement jetable, avec effacement des données synthétiques avant downgrade, sans modifier les migrations. Conteneur `smartao-l04-acts-pg-20261020` arrêté, ACLUID70 retirée et socket700. Vite, Chromium isolé et adaptateur ASGI de recette fermés; applications étrangères préservées. Tête Alembic de code0145 inchangée, aucune migration nouvelle. HEAD30f26934430095632000a1d82519f61dbb4c6411/branche codex/reconcile-smartao-20261009, checkout principal et WIP conservés sans staging/commit/push.

**Limites et suite.** Document natif Markdown et acteurs/données synthétiques uniquement. La couverture exhaustive et la conformité d’un cadre acheteur particulier ne sont pas démontrées. DOCX/PDF acheteur, signatures et pièces tierces restent ouverts. DPGF non évaluable par RAG, moteurs candidats inactifs, A1 non admis, A2 générique HOLD et NO-GO public. Aucun backend live, corpus réel, VPS, déploiement, dépôt externe ou effet P3 réel. Le plan global porte seul la prochaine tranche DOCX.

**Méthode/outillage.** Superpowers (cadrage borné, TDD, diagnostic, revue) et ECC (module-regression/verification-loop); Graphify interrogé avant exploration, Serena activée, Basic Memory miroir. OpenDesign Local : catalogue/projet C10/prototype existant consultés; Impeccable context/craft-floor/detect et recette Chrome DevTools. Aucun nouveau moteur, framework ou dépendance; aucune API/SDK externe nouvelle à documenter. Pas de Jev/Manus : pas de classification ou investigation externe utile à ce raccord natif.


Plan et miroir Basic Memory synchronisés puis vérifiés par relecture : une seule prochaine étape DOCX, identique. Le plan reste l’unique statut.
