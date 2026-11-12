# L04 — livrables techniques et durées — plan et preuve locale

## AS-IS / risques / points d'insertion

Deux omissions reproduites lors de la calibration multi-formats : « Le titulaire doit fournir les plans pour le lot 2 » et « Le délai d'exécution est de 6 semaines pour le lot 7 ». L'analyse nativev7 ne les couvre pas. Les actes humains, la synthèse12axes, la matérialisation et la chaîne multi-formats existent; les réutiliser jusqu'à la revue du dossier.

Risque : faux signal financier/RC, négation ou condition promue en obligation, lecture historique réinterprétée, preuve courante v8 refusée, point sans source/version/lot exacts ou pièce non lue cachée. Aucune conversion de durée ni date de fin calculée. Applicabilité UNKNOWN; analyse_complete reste faux.

Insertion : deux règles fermées dans `dce/application/analysis.py`, nouvelle identité de recette native8 et validation v1–v7 conservée; lecteur DCE accepte les preuves8 avec les mêmes contrôles. Aucune migration, route, UI, dépendance, confirmation, porte ni moteur candidat modifié.

## Plan minimal — exécution inline Superpowers / ECC

- [ ] TDD : deux omissions et variantes simples, ancres UTF8, négations/conditions, familles financières/RC/exemples refusés, validation historique7 et refus d'une preuve nouvelle marquée7.
- [x] Ajouter les deux règles versionnées et la relecture8; vérifier tous les consommateurs et contrats de version sans modifier les recettes historiques.
- [x] Construire un DCE synthétique complet multi-formats depuis le développement32faits, ajouter les deux omissions; conserver une annexe tableau non lue. Qualifier les34points avec ancres exactes et traitements/revue natifs; éprouver rectificatif/invalidation/historique.
- [x] Revue ciblée, suites appropriées, Ruff/mypy/diff/secrets/Semgrep puis résultat daté; une seule tranche active dans le plan, miroir Basic Memory et fermeture des ressources locales.

Les anciens challenges restent intacts; aucune mesure de généralisation indépendante déduite de cette recette de développement. Aucun live/corpus réel/VPS/déploiement/P3/export/dépôt externe/commit/push; A1 non admis, A2 HOLD, NO-GO public. Le plan global reste la seule autorité opérationnelle.


## Résultat fonctionnel local observé

La recette native8 ajoute deux règles de signaux à revoir, dans les types existants TECHNICAL_PRESCRIPTION et SCHEDULE_CONSTRAINT. Les plans, notes de calcul et fiches techniques sont reconnus dans des constructions actives/passives bornées CCTP/CCAP. Les durées explicites d'exécution/travaux sont reconnues dans CCTP/CCAP/PLAN/PLANNING : chiffres ou vocabulaire numérique français borné, unités littérales, délai global, parenthèses numériques conservées. Aucun parseur de quantité, conversion d'unité, comparaison chiffres/lettres ou calcul d'échéance n'est ajouté.

La validation7 et ses règles restent inchangées; les nouvelles règles8 sont refusées si étiquetées7. Les identités des analyses nouvelles incluent8, donc ne rejouent pas silencieusement un résultat7. Le lecteur revalide8 avec les mêmes contrôles document/extraction/fragment/hash/dernière analyse/matérialisation et portéelot. Aucun profil retrievalv8 candidat n'est activé : ce numéro est celui de la recette native DCE.

### TDD et contre-revue

- Quinze cas rouges observés sur les omissions et variantes, puis verts; treize refus/compatibilité déjà verts.
- Revue ciblée : deux formulations usuelles supplémentaires omises (délai global et six(6)) et plans comptables parasite. Trois nouveaux rouges observés, corrigés puis31tests dédiés verts en contre-revue indépendante.
- Suite domaine DCE finale384/384; ciblés services/lecteurs/SQL/parcours126/126. Les ensembles se recouvrent; ne pas additionner comme un total distinct.
- Ruff/format ciblés et mypy650 verts. Suite backend complète en cours sur base neuve smartao_l04_duration_global; ne pas extrapoler le global3730 de la tranche précédente au code8.

### Dossier complet multi-formats de développement

`backend/tests/db/test_l04_fullformats_duration.py` transforme les huit pièces du développement historique32faits en originaux synthétiques PDF (RC), DOCX (CCAP et CCTP), XLSX (planning) et texte (autres pièces). Il ajoute deux faits attendus, avec lots1/2; neuf pièces en incluant une annexe DOCX dont le tableau n'est pas lu. Chaque fichier binaire est haché; la chaîne native extrait/analyse/matérialise réellement les sources. Le gold n'est pas injecté dans les tables de résultats.

34/34points sont retrouvés une fois chacun, sans point parasite mesuré. Types, source/document/version/hash, citation et page/paragraphe/cellule/ligne sont confrontés aux attentes; lots exacts des deux corrections, applicabilitéUNKNOWN et annexe non lue vérifiés. Les34points sont traités par les handlers humains, dossier12axes préparé puis revu. Le rectificatif passe de6à9semaines, invalide la revue et refuse un ancien traitement; les34points V2 sont traités/revus à nouveau, snapshots V1 intacts. Six révisions de revue au total, aucun effet de retry doublé. Ces tests synthétiques ne constituent pas une validation humaine métier réelle.

Le PDF français a été rendu et inspecté; l'encodage accentué est contrôlé par les citations exactes du test. APIs installées réutilisées; Context7/pypdf consulté, aucune nouvelle dépendance. Les formats Word/Excel sont contrôlés structurellement, aucune recette Office ou navigateur déduite.

## Limites explicites

Le jeu complet dérive d'un développement connu : régression de parcours, pas challenge indépendant ni preuve de rappel sur des DCE arbitraires. Les tableaux DOCX, graphiques et structures non extraites restent non lus/REVIEW_REQUIRED. Les dates et durées calculées, obligations conditionnelles arbitraires, autres formulations et comparaisons de valeurs ne sont pas qualifiées. Les conséquences économiques et l'applicabilité restent des actes distincts. DPGF non évaluable par RAG; A1 non admis/A2 HOLD/NO-GO public. Les portes et les moteurs candidats sont inchangés.


## Qualification finale — 22 octobre 2026

- Backend complet : **3763/3763,0ignoré**,1avertissement Starlette/httpx connu,1003,58secondes. Le runner a terminé pendant l'interruption; log complet et absence de processus vérifiés à la reprise, aucune deuxième suite relancée. Huit hashes code/tests toujours identiques au gel.
- Domaine DCE384/384; ciblés services/SQL/parcours126/126; contre-revue dédiée31/31. Ensembles recouvrants : ne pas additionner pour annoncer un nombre distinct. Contrats documentaires4/4.
- Ruff/format ciblés, mypy650 sans erreur. Semgrep1.179.0,225règles/8fichiers,0finding/0erreur; detect-secrets1.5.0 zéro finding, baseline inchangée. Le scan local ne constitue pas un audit de sécurité exhaustif.
- Deux bases `smartao_l04_duration` et `smartao_l04_duration_global` vérifiées Alembic0 (`cleanup.json`), conteneur dédié arrêté, ACL UID70 révoquée/socket700. Aucune UI ni navigateur de recette démarré; aucune qualification live.
- Plan/index/fiche des livrables/Basic Memory mis à jour; aucune mise en scène de validation Owner réelle. HEAD30f2693/WIP principal conservés, aucun stage/commit/push. L04 global PARTIAL, A1 non admis/A2 HOLD/NO-GO public.

### Fichiers et méthode

Production : `backend/app/modules/dce/application/analysis.py` et `backend/app/modules/dce/infrastructure/case_dce_reading_reader.py`. Régressions : `backend/tests/domain/dce/test_technical_deliverable_duration.py` et `backend/tests/db/test_l04_fullformats_duration.py`; réutilisation paramétrée du parcours rectificatif existant. Trois tests existants attendent désormais la recette courante8; leurs entrées historiques ne sont pas réécrites.

Superpowers using-superpowers, brainstorming borné, writing-plans/executing-plans, systematic-debugging, TDD, requesting-code-review et verification-before-completion; ECC verification-loop. Graphify consulté en premier, graphe historique recoupé au code. Skills formats PDF/DOCX/XLSX et Context7/pypdf pour les originaux; Basic Memory miroir de reprise, plan source unique. Serena non nécessaire sans navigation sémantique; Jev/Manus non utilisés pour ces assertions déterministes. Aucun changement visible d'interface : pas de workflow OpenDesign/Impeccable déclenché, aucune preuve navigateur nouvelle revendiquée.

Prochaine étape : L04 — rendre les prescriptions des tableaux DOCX exploitables dans le dossier complet, avec ancres de cellule exactes et UNKNOWN sur les structures ambiguës, puis qualifier traitement, revue et rectificatif sans modifier les portes ni activer de candidat.
