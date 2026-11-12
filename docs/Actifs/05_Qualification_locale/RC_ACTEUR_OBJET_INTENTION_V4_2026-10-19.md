# Intention candidate v4 — acteur, objet et demande — 19 octobre 2026

## AS-IS / risques / insertion

Checkout principal, HEAD30f2693, WIP conservé. V3 et son adaptateur restent gelés ; l’épreuve contexte/E5/SQL est historique et n’est pas un jeu de réglage. V4 est un module d’application séparé, sans lecture source, encodeur, SQL, HTTP, UI ou acte métier. Aucune nouvelle dépendance.

Risques : confondre auteur de question et acteur métier, enlever une négation/condition, assimiler une attestation à une visite, attribuer un possessif sans référent, perdre une restriction d’objet ou une ancre Unicode. Un rôle lexical n’est ni une identité ni une permission.

## Plan minimal (Superpowers writing-plans / TDD / ECC verification-loop)

- [x] `backend/tests/application/test_rc_actor_intent_v4.py` : observer les régressions rouges avant module ; acteurs nominaux simples, objets et adjectifs bornés, demande/action, lots, contexte possessif et refus.
- [x] `backend/app/modules/knowledge/application/rc_actor_intent_v4.py` : reconnaître une relation acteur/demande/objet complète ; réutiliser les contrats d’intention et les formes v3 sûres sans modifier v3. Les trois composants ont des ancres distinctes. Tout résidu non qualifié reste UNKNOWN.
- [x] CLI d’évaluation séparé et tests : vérifier indépendamment hash/ancres/composantes et absence de promotion, jamais produire les attentes depuis le candidat.
- [x] Geler code et développement avant création/ouverture d’un nouveau challenge indépendant ; mesurer une fois, conserver les échecs sans réglage.
- [x] Revue, suite pure/ciblés, lint/types/scans/diff, plan/index et miroir mémoire autorisé.

Périmètre initial déclaré avant code : préambule neutre infinitif de préparation (pas phrase déclarative anaphorique libre), possessif sa/son exigeant un acteur nominal explicite dans la même question ; acteur candidat/soumissionnaire/titulaire/employeur/opérateur, sujet lexical et action compatibles. Lots numériques du contrat existant seulement, absence UNKNOWN. Demandes multiples ou conditionnelles non qualifiées refusées ; négation d’action non reconnue refusée, négation interrogative éventuellement conservée littéralement. La notion d’obligation réelle reste hors périmètre.

La première proposition indépendante, reçue avant gel du code, est exposée et PREPARATION_ONLY : ni utilisée pour le développement ni présentée comme held-out. Une autre épreuve sera créée après gel. Aucune validation humaine ou admission implicite.

DPGF non évaluable ; A1 non admis, A2 HOLD, NO-GO public. Aucun branchement retrieval, moteur actif, backend live, corpus réel, VPS, P3, déploiement, commit ou push.


## Fichiers et comportement démontré

- `backend/app/modules/knowledge/application/rc_actor_intent_v4.py` : enveloppe immutable séparant acteur lexical, objet nominal complet, demande, action, contexte lié et complément de phase ; intention/lot/SHA issus des contrats existants. Aucun acteur authentifié ou droit n’est dérivé de ces mots.
- `backend/tests/application/test_rc_actor_intent_v4.py` : 45 tests, dont contre-exemples d’autres têtes nominales et accords Unicode.
- `scripts/qualify_rc_actor_intent_v4.py` et `backend/tests/ops/test_rc_actor_intent_v4_qualification.py` : banc fermé et cinq tests ; attentes positives complètes obligatoires, preuve corrompue détectée, composantes distinctes et refus financier.
- `backend/tests/fixtures/knowledge/rc_intent_development_actor_v4.json` : 33 cas de développement, neuf positifs, 33/33 exacts.
- `backend/tests/fixtures/knowledge/rc_actor_intent_independent_challenge_v4.sealed.json` : autre jeu créé par auteur isolé APRÈS gel du code, jamais utilisé pour régler le candidat.

V3 est réutilisée pour ses formes sûres sans la modifier. V4 expose alors l’objet nominal complet et étend la preuve de demande au prédicat interrogatif déjà reconnu. L’action du fallback n’est pas encore exposée : cette limite ressort de l’épreuve et n’est pas corrigée sur son jeu. Les possessifs sa/son des préambules qualifiés sont reliés au seul acteur nominal explicite de la question. Cette relation grammaticale ne prouve ni identité, ownership ou applicabilité métier.

## TDD, revue et gel

37 régressions initiales rouges avant module, puis vertes. Revue indépendante : tête « formulaire visite médicale » et accord après tabulation/espace insécable reproduits par six rouges, corrigés et contre-revus. Seconde passe : demande attributive tronquée et gold positif incomplet reproduits puis corrigés. 50 ciblés finaux verts ; contre-revue indépendante les a également exécutés sans nouveau finding important.

Gel code/développement :31 fichiers à16:16:22UTC. Nouveau gold créé ensuite sans accès au code/dev/anciens jeux, scellé à16:18:03UTC :24 cas,12 positifs/12 refus. Son contenu n’a pas été montré à l’intégrateur avant la première mesure : copie des octets et contrôle SHA sans décodage, puis manifeste de mesure32 fichiers et événement d’ouverture. Aucun réglage après résultat. L’indépendance de l’auteur est une séparation de contexte d’agent déclarée, pas une seconde validation humaine. La première proposition exposée n’a pas servi au développement ni à la mesure.

## Résultat indépendant — candidat HOLD

| Mesure | Résultat |
|---|---|
| Cas exacts | **17/24** |
| Intentions positives complètes | **5/12** |
| Positifs classés COVERED | **6/12** : un de ces six manque la preuve d’action du fallback |
| Omissions positives | Six refus conservateurs ; préambules possessifs non couverts, objets qualifiés attributifs et variation de verbe |
| Refus / promotions | **12/12 respectés ; zéro promotion** |
| Ancres retournées | Zéro ancre invalide ; cela ne signifie pas couverture des ancres manquantes |
| Temps | 96 appels intention seuls, p95 chaud0,135ms ; aucun temps de retrieval, source ou modèle mesuré |

Le cas reconnu mais incomplet demande une visite avec « faut-il effectuer » : sujet/demande/objet sont prouvés, action séparée absente. Il n’est pas crédité comme succès complet. Les six refus positifs ne sont ni des réponses exactes ni un faux positif ; ils restent des omissions. Les 33/33 du développement ne compensent pas ces échecs indépendants.

Aucune preuve de pertinence documentaire, extraction de DCE ou analyse complète n’est apportée. Les compteurs source_reads/encoder_calls du rapport sont déclaratifs : l’absence de lecteur/encodeur est établie par le périmètre du module et sa revue, pas par une instrumentation exhaustive d’un backend actif.

## Contrôles de clôture

- Backend sans DB : **2742 réussites,864 désélectionnés,un avertissement,39,16s,exit0**. Pas de nouvelle suite globale PostgreSQL ni migration : module pur, aucune infrastructure modifiée.
- Ruff backend/scripts,format4,mypy639 et diff sans erreur. Semgrep1.179.0 :225 règles sur quatre Python,zéro finding/erreur JSON. detect-secrets1.5.0 :57 signaux de SHA de questions synthétiques comparés exactement aux textes,baseline/filtres inchangés.
- 32 empreintes de mesure et653 empreintes historiques de la tranche précédente conservées ; aucun changement aux anciens candidats/profils/jeux/services.
- Revue des rapports : comptes, citations littérales et hashes recoupés,aucun écart de gold corrigé après mesure.
- Aucun moteur actif,factory,API,UI,SQL,schéma,dépendance,backend live,corpus réel,VPS,P3,déploiement,commit ou push. HEAD30f2693/WIP préservés.

Méthode : Graphify interrogé avant exploration ciblée ; Superpowers cadrage/plan/TDD/revue/vérification et ECC verification-loop. Pas de nouvelle API nécessitant Context7,ni navigation sémantique nécessitant Serena,ni UI nécessitant OpenDesign/Impeccable. Pas de besoin de Jev/Manus sur cette reconnaissance locale déterministe. Basic Memory : résumé local proposé,transmission toujours suspendue à l’autorisation déjà demandée après rejet automatique ; plan du dépôt seul statut.

Preuves privées : `~/.local/share/smartao-proofs/rc-actor-v4-20261019/` (rouges,mesure,manifestes,tests,scans,revues et clôture). A1 non admis,A2 générique HOLD,NO-GO public maintenus.

Prochaine étape : ESSAIS DCE — coder une révision d’intention séparée sur développement distinct pour les preuves d’action du fallback, les objets qualifiés attributifs et les contextes possessifs, avec refus des changements de sens non prouvés; qualifier sur un nouveau jeu indépendant gelé, sans régler sur les challenges v4/contexte-E5-SQL ni brancher le retrieval. DPGF non évaluable; UNKNOWN préservé, A1 non admis, A2 générique HOLD et NO-GO public maintenus.
