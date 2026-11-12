# Adaptateur contexte v3 → retrieval candidat / SQL synthétique — 19/10/2026

## AS-IS, risques et insertion

Checkout principal `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`, WIP préexistant conservé. V3 avait une qualification d’intention bornée (32/32), sans retrieval. Le service candidat existant interprète sa propre requête et participe aux preuves historiques : le modifier ou lui transmettre une requête réécrite invaliderait ces preuves.

L’insertion retenue est une composition expérimentale distincte. Aucun moteur actif, factory, API, UI, schéma, dépendance ou droit n’est modifié. Les 28 fichiers gelés v3 et sept fichiers de service/profils préservés sont vérifiés par SHA-256.

## Plan minimal et preuves

- [x] Régression rouge : 17 tests initiaux échouent sur le module absent avant implémentation.
- [x] Adaptateur séparé conservant requête brute, intentions, ancres UTF8 et preuves de contexte ; 24 tests unitaires finaux réussis.
- [x] PostgreSQL jetable synthétique : 17 tests réussis, provenance exacte, refus, invalidation, isolation et rectificatif.
- [x] Backend global : **3543 réussites, 3 avertissements, 778,60 s, exit0** ; 47 contrats documentaires/ops verts. Ruff backend/scripts, format trois fichiers, mypy 637 fichiers, diff sans erreur. Semgrep 1.179.0 : 225 règles, trois fichiers Python, aucun finding/erreur JSON. detect-secrets : trois identifiants publics modèle/manifestes triés exactement, baseline inchangée. Base finale Alembic0 vérifiée puis conteneur dédié arrêté et retiré.

## Code et contrat

- `backend/app/modules/knowledge/application/context_candidate_retrieval.py` : reconnaissance v3, composition du transport existant et projection typée existante, enveloppe d’identité distincte.
- `ops/retrieval-candidate/profile-context-transport-v1.json` : modèle/runtime/segmentation épinglés identiques au profil v1 ; plancher zéro destiné uniquement à l’énumération.
- `backend/tests/application/test_context_candidate_retrieval.py` et `backend/tests/db/test_context_candidate_retrieval_sql.py` : régressions reproductibles.

La requête brute arrive inchangée à l’encodeur. La vue grammaticale du reconnaisseur reste interne. L’ID de l’adaptateur engage le profil de transport, le reconnaisseur v3, la convention d’ancres, la politique source v10, le seuil de sélection 0,85 et la fenêtre de 50 segments. Le plancher zéro n’est pas un seuil d’acceptation : chaque hit exige une preuve typée sujet/directive/lot ; sous 0,85, son retour est tracé `RC_TYPED_RESCUE`. Au-dessus, il est tracé `DENSE_FLOOR` après le même contrôle typé.

Chaque requête a sa capture et son index éphémères. Les sources étrangères, privées ou personnelles sont filtrées avant encodage. Les métadonnées visibles sont copiées. Le transport revalide après encodage ; l’adaptateur relit après projection. Toute discordance vide hits, traces et preuves sources avec `SOURCE_CHANGED`/`REVIEW_REQUIRED`. L’intention et ses ancres de requête restent consultables. Le résultat reste `UNKNOWN`, sans effet métier.

## Ce que les tests prouvent

**24 tests unitaires :** requête/contextes/ancres et identité, preuves typées positives/négatives, score dense et rescue, refus lot/sujet/source tronquée ou coordonnée, garde financière avant lecture, requêtes non couvertes, confidentialité avant encodage, invalidation pendant encodage ou projection, lot/condition inconnus, concurrence entre deux Affaires sans état partagé, limites d’entrée et identité du profil.

**17 tests PostgreSQL :** fragments/version/hash/page/région et extraits aux offsets exacts ; trois lectures SELECT sans écriture durant le retrieval nominal ; rejet des extractions REVIEW_REQUIRED/FAILED_SAFE/UNSUPPORTED/REJECTED_LIMIT ; scopes étrangers tenant/Affaire/version peuplés mais inobservables ; hash fragment discordant et extraction/document discordants refusés sans retour à un prédécesseur ; requête financière ou non couverte refusée avant SQL ; changement durant encodage/projection effaçant les preuves ; invalidation de l’ancienne version après rectificatif ; nouvelle Affaire ne récupérant aucune preuve de l’ancienne. Les fragments historiques restent stockés.

La revue indépendante n’a pas identifié de finding important après examen et exécution des 24 tests unitaires. Elle ne remplace pas une validation humaine métier.

## Limites conservées

1. Fenêtre de transport de 50 segments à score positif : aucun engagement d’exhaustivité, une contradiction peut être hors fenêtre. Budget de source : 128 fragments.
2. Réencodage des passages à chaque requête ; coût CPU/RAM et qualité d’E5 réel non mesurés ici. Encodeur déterministe dans les tests.
3. Trois lectures distinctes, aucune transaction atomique ou autorisation d’acte métier prouvée.
4. Le lecteur SQL existant classe ses sorties `INTERNAL_OPERATIONAL`. Les tests SQL ne qualifient donc pas une classification documentaire réelle financière/personnelle. Les objets classifiés des tests unitaires et la garde financière sont refusés ; DPGF reste non évaluable, sans élargissement de droits.
5. Fidélité à l’extraction stockée et concordance des métadonnées document/extraction, sans relecture du blob ni preuve de complétude d’extraction ou de DCE.
6. Aucun test HTTP d’ownership/MFA, index vectoriel SQL stocké, navigateur ou politique de production n’est revendiqué par cette tranche.

A1 non admis, A2 générique HOLD, NO-GO public. Aucun branchement actif, corpus réel, backend live, VPS, P3, déploiement, commit ou push.

## Preuves privées et méthode

`~/.local/share/smartao-proofs/rc-context-retrieval-20261019/` : rouge initial, unitaires, SQL, suite globale, lint/types, scans, hashes préservés et clôture. PostgreSQL dédié sans réseau ni port publié, stockage tmpfs ; URL synthétique explicite et flag jetable. Aucun secret réel dans les fixtures.

Graphify interrogé avant exploration ciblée ; Superpowers cadrage borné/TDD/revue/vérification et ECC verification-loop. Pas de nouvelle API nécessitant Context7, de navigation sémantique nécessitant Serena, ni d’UI nécessitant OpenDesign/Impeccable. Jev/Manus non nécessaires à cette composition bornée.

Basic Memory : résumé technique minimal préparé localement ; transmission suspendue en attendant la réponse à la demande d’autorisation déjà présentée après rejet automatique de l’envoi. Le plan du dépôt demeure la source opérationnelle.

## Suite exacte

Prochaine étape : ESSAIS DCE — mesurer ensemble l’intention v3, l’adaptateur expérimental, E5 CPU réel et le lecteur DCE SQL sur un nouveau jeu BTP synthétique gelé indépendant : précision et omissions par clause, fidélité des ancres/contextes, abstention, invalidation et budgets RAM/temps; ne pas régler sur ce jeu ni activer le candidat. DPGF non évaluable; UNKNOWN préservé, A1 non admis, A2 générique HOLD et NO-GO public maintenus.
