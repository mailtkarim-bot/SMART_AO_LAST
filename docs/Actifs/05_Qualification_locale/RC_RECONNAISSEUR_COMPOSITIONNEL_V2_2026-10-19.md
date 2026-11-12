# Reconnaisseur RC compositionnel v2 — 19/10/2026

## AS-IS / risques / points d’insertion

Checkout principal codex/reconcile-smartao-20261009/HEAD30f2693, WIP préservé. V1 gelé historique :14/16positives,24/32exacts ;aucun calibrage du code v1 ou de son challenge. Diagnostic indépendant transmis au développeur sous forme de familles seulement :permission de non-production/coréférence locale,nécessité impersonnelle,priorités date/condition/troncature/référence/lot signé,convention spatiale.

V2 sera un module candidat distinct pour conserver les12hashes v1 exacts. La duplication bornée de cette grammaire gelée évite de modifier rétroactivement le code ayant produit la preuve v1. Réutiliser les contrats d’intention/portée/ancre existants ;aucun branchement retrieval,profil actif,API,UI,schéma ou dépendance. Pas de réécriture de requête ou d’inférence de réponse métier.

Risques :négation prise pour dispense,auxiliaire temporel pris pour seconde demande,condition promue,format de lot tronqué,référence inventée,calibration sur nouveau challenge. Convention d’ancre et priorité explicitées avant gel ;ancien challenge non relancé pour régler v2.

## Plan minimal

- [x] Développement nouveau par familles et contre-exemples,rouges vérifiés avant v2.
- [x] Contrat v2 explicite et contre-lecture indépendante du nouveau challenge sans accès code/développement ;textes du challenge non vus par le développeur avant gel.
- [x] V2 minimale,développement vert,sûreté/conventions/régressions et revue.
- [x] Banc v2 reproductible distinct,contrôles et gel avant ouverture indépendante ;aucun réglage après résultat.
- [x] Tests appropriés,scans,diff,statut/plan/index/mémoire autorisée.

A1nonadmis/A2HOLD/NO-GOpublic ;DPGFnonévaluable,v7/v8/v9/v10/v1préservés. Aucun retrieval/E5/SQL/live/corpus réel/VPS/P3/déploiement/commit/push.

## Résultat de qualification — HOLD

V2 d’intention locale codée dans un module et un banc distincts, sans modifier les 12 hashes v1. Les familles non-remise/coréférence locale, nécessité impersonnelle, date avec auxiliaire, conditions, troncature, référence non résolue, lot signé et convention spatiale sont couvertes sur développement nouveau. Convention lexical-cue-v2 et priorités explicitées avant gel. 20/20 cas nouveaux exacts, 32 anciens cas de développement conservés (pas de relecture du challenge v1 pour régler v2), 71 ciblés verts dont 67 application/4 CLI. Régressions rouges vérifiées :19 initiaux, condition interrogative,5 contre-exemples de revue, métadonnées CLI et mesure vide. Revue et contre-revue ont corrigé juxtaposition date/statut et reprise pronominale non prouvée. Développement + contre-exemples ne valent pas généralisation. Nouveau challenge32cas préparé et relu par deux agents distincts sans accès au code/développement/anciens challenges; exposition aux agrégats de la référence documentaire déclarée, aucune indépendance statistique revendiquée. Corrections annotatives avant mesure conservées en révisions privées, puis gel20fichiers avant ouverture consignée. Résultat indépendant :2/16 positives exactes,15/32total exact,UNSUPPORTED4/4,AMBIGUOUS5/5,UNKNOWN3/6,financier1/1. Zéro promotion indue et zéro ancre UTF8 invalide;14écarts aux ancres attendues et3gates fausses (positives,composantes/raisons,ancres exactes),candidatHOLD/admittedfalse. Contre-lecture confirme14omissions positives (9préambules et5compléments circonstanciels rejetés) et3divergences de raison, dont deux limites de convention non-active/insuffisance à expliciter sans réannoter la mesure. Sujet conservé,demande et ancre perdues sur les positives omises. Pas de comparaison de progression v1/v2 sur jeux différents.128appels(32initiaux+96chauds),p95chaud0,063ms intention seule;0lecture source/0encodeur et aucun retrieval/E5/SQL qualifié. Code20hashes inchangé après observation. Suite backend sansDB2585réussites/846désélectionnés/1warning39,82s;Ruff/format4/mypy636/diff verts. Semgrep1.179.0/225règles/4fichiers0finding/0erreurJSON;detect-secrets54signaux de SHA de provenance synthétique triés précisément,aucune baseline/filtre édité. Aucun branchement factory/API/UI,profil actif,schéma,dépendance,live/corpus réel/VPS/P3/déploiement/commit/push. HEAD30f2693/WIP conservés,A1nonadmis/A2HOLD/NO-GOpublic,DPGFnonévaluable.

### Fichiers concernés

- `backend/app/modules/knowledge/application/rc_compositional_intent_v2.py` : grammaire candidate versionnée séparément ; aucun appel automatique dans le logiciel actif.
- `scripts/qualify_rc_intent_recognition_v2.py` : banc d’intention seule ; convention publiée, mesure vide refusée, manifest essentiel vérifié avant scellé.
- `backend/tests/application/test_rc_compositional_intent_v2.py` et `backend/tests/ops/test_rc_intent_recognition_qualification_v2.py` : preuves reproductibles.
- Fixtures `rc_intent_development_compositional_v2.json`, `rc_intent_compositional_contract_v2.json`, `rc_intent_independent_challenge_v2.sealed.json`, `rc_intent_independent_qualification_protocol_v2.json` sous `backend/tests/fixtures/knowledge/`.

### Ce que les résultats prouvent et ne prouvent pas

La v2 corrige les familles ciblées sur développement et conserve les refus testés. Elle ne reconnaît pas suffisamment les requêtes naturelles contextualisées du nouveau jeu indépendant. Deux positives exactes et zéro promotion ne compensent pas quatorze omissions. Les motifs de refus peuvent être sûrs sans être les motifs annotés. Une ancre byte valide n’est pas nécessairement l’ancre attendue ; les quatorze différences restent des échecs.

La couverture très bornée provient de la grammaire des préambules et compléments, pas d’une mesure d’embeddings ou de retrieval : aucun n’a été appelé. Ce nouveau jeu étant différent, le résultat2/16 n’est pas un test de régression comparatif avec14/16v1. Les cas de développement conservés servent la non-régression, pas cette comparaison indépendante.

Le challenge v2 est désormais ouvert et historique. Aucun réglage du code ou des annotations après observation ; la prochaine version exigera de nouveaux cas de développement et un nouveau challenge indépendant. Deux raisons NON_ACTIVE_REQUEST/INSUFFICIENT_EVIDENCE diffèrent sur des messages non interrogatifs : limite de convention consignée, résultat non réannoté a posteriori.

### Préparation indépendante et intégrité

Auteur indépendant : contrat/protocole/référence seulement, aucun code/développement/ancien challenge. Second relecteur indépendant : contrat et nouveau gold seulement. Avant mesure,8cas ont reçu des corrections de composantes sujet et10ancres restaurées ; une clarification prospective sur les questions de conditions a corrigé1ancre DEMAND. Aucune correction fondée sur une sortie moteur et aucun texte modifié. Original et révisions conservés hors Git. La règle d’antécédent compatible et les demandes juxtaposées ont été contre-lues sans correction supplémentaire.

SHA final du challenge : `1c87df7aea14435b56bcb3d64dc2245aef5f3bd0390d18058fb509abed11a559`. Les20fichiers du gel et les12fichiers de preuve v1 sont vérifiés. La procédure de scellement sépare les rôles ; elle n’est ni une frontière de sécurité ni une preuve statistique.

### Vérifications et limites opérationnelles

71ciblés et2585sansDB sont verts. 846tests DB non exécutés :aucune suite PostgreSQL globale nouvelle,aucune migration ou mesure réelle de DCE. Ancien backend3301 et v10 SQL restent des preuves historiques distinctes. Scan de sécurité limité aux4nouveaux fichiers Python ;54signaux de hash dans les nouvelles données sont triés en preuve privée,aucun secret identifié dans ce périmètre. Ni audit global du WIP ni garantie d’absence de vulnérabilité revendiqués.

Méthodes Superpowers using-superpowers/cadrage/TDD/revue/vérification et ECC verification-loop. Graphify consulté, sans nœud pour le nouveau candidat ; lecture ciblée. Pas de navigation sémantique Serena,SDK/API nouveau nécessitant Context7,UI nécessitant OpenDesign/Impeccable ou Jev/Manus requis. Les agents d’annotation/revue ne remplacent aucune autorité humaine.

Preuves privées : `~/.local/share/smartao-proofs/rc-compositional-v2-20261019/` : diagnostics généraux, révisions indépendantes, rouges/verts, développement/challenge, gel20fichiers, ouverture, nonDB/scans/triage et état final. La synchronisation Basic Memory reste soumise à l’autorisation explicite demandée après le précédent refus de revue automatique ; résumé local préparé, aucun cas indépendant à transmettre.

Prochaine étape : ESSAIS DCE — coder un traitement candidat des préambules et compléments contextuels sur un développement distinct, avec preuve qu’ils ne portent ni autre sujet/demande, ni négation, condition ou portée; clarifier les raisons d’abstention, puis qualifier une v3 sur un nouveau challenge indépendant. Ne pas régler sur les challenges v1/v2; conserver UNKNOWN, les refus et tous les moteurs inchangés, sans branchement retrieval ni activation. DPGF non évaluable; A1 non admis, A2 générique HOLD et NO-GO public maintenus.
