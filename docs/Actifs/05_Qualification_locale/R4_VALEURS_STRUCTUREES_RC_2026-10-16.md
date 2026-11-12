# R4 — projection structurée candidate des exigences RC — 16 octobre 2026

## Cadrage et plan autorisé

AS-IS : moteur5 et matérialisation qualifiés localement; lecture actuelle sans valeurs structurées. HEAD30f26934430095632000a1d82519f61dbb4c6411 sur checkout principal, WIP conservé. Risques : promotion d'un ancien texte, dates/fuseaux devinés, rectificatif/lot ambigu, fuite de texte ou de données privées, effet humain inventé.

Insertion : nouveau projecteur pur borné, projection/query/DTO HTTP existants et type client non visuel. Aucune migration, dépendance, commande ou édition d'interface. Les structures raster ne sont pas utilisées pour cette projection textuelle; les identifiants SourceAnchor existants sont réutilisés. M2-027/029/035 et CT31-02 : source/version/hash/région et applicabilité inconnue, sans backfill.

- [x] TDD sur lecture SQL absente, puis valeurs, inconnus, refus et ancres exactes.
- [x] Coder les valeurs candidates fermées : pièces attendues, date/heure/fuseau explicitement cités, numéros de lots cités; états CANDIDATE/UNKNOWN distincts, applicabilité toujours UNKNOWN.
- [x] Relier uniquement des observations v5 reproductibles aux sources RC courantes, version/extraction/hash exacts. Refuser les textes obsolètes/non prouvés et les rectificatifs/valeurs concurrents; préserver les exigences historiques.
- [x] Exposer la projection additive dans GET Case DCE existant, sans texte libre, sans changement de confirmation ni effet métier.
- [x] Revue, tests pertinents, global backend, types/lint/scan/diff; cleanup PGjetableR4g, plan/case/journal/index et miroir Basic Memory.

Preuves privées : `/home/noor/.local/share/smartao-proofs/r4g-20261016/`. PostgreSQL jetable local R4g, port55439; aucun backend live/corpus réel/VPS/déploiement/push/P3/admission/GOpublic. A1 non admis,A2HOLD,NO-GOpublic. Superpowers cadrage/TDD et ECC vérification/sécurité; Graphify, Serena activé et Basic Memory pour l'orientation. Pas d'onboarding Serena global ni nouveau framework.

## Contrat implémenté et limites

Le projecteur pur `requirement_values.py` ne lit qu'une clause RC vérifiée (1 000 octets UTF-8 au plus). Les preuves de chaque valeur sont des intervalles d'octets absolus dans le fragment exact; les valeurs ne transportent pas de texte libre. Pièces reconnues : DC1/DC2/DC4/DUME, mémoire technique, acte d'engagement, BPU et DPGF, uniquement avec un signal documentaire requis/optionnel. Cela ne prouve ni présence de pièce ni applicabilité.

Pour une échéance de remise explicitement rattachée au texte : date calendaire numérique complète ou mois français complet, heure HHhMM/HH:MM et UTC/décalage explicite. L'ordre numérique ambigu 04/05 est refusé; année, fuseau et applicabilité absents restent UNKNOWN. Aucun calcul de durée, instant légal ou fuseau français implicite. Les dates de réunion et valeurs dans une URL ne deviennent pas une échéance. Les lots reconnus sont des numéros cités, jamais un rapprochement automatique avec les lots de l'Affaire. Listes partielles, alternatives et plages non reconnues sont refusées.

Le reader réutilise les ancres, l'analyse v5, la matérialisation et l'extraction courantes tenant/version exactes. Il revalide le SHA-256 et le segment UTF-8 de l'observation; l'ancien historique reste lisible sans promouvoir ses valeurs. Une extraction REVIEW_REQUIRED plus récente (ou au même instant) invalide les valeurs antérieures. Les conflits de date/heure/fuseau sur des portées potentiellement communes sont refusés; au-delà de 256 candidats l'absence de comparaison complète reste explicite. Un rectificatif avec plusieurs dates de remise distinctes ne sélectionne pas une nouvelle date arbitraire. Ce garde borné n'est pas un moteur sémantique général de rectification.

Le GET existant expose une propriété additive `structured_candidate`, fermée et validée : cohérence des valeurs/états/preuves, identité d'ancre parent. Aucun nouvel endpoint ni mutation. Confirmation humaine toujours PENDING; aucune écriture de Requirement/Event/Outbox après deux lectures. Le type TypeScript est raccordé; aucun affichage JSX/CSS modifié et aucune qualification navigateur dans cette tranche.

## TDD, revue et preuves intermédiaires

- Lecture structurée absente reproduite par test SQL avant implémentation. Régressions pures de valeurs/ancres/refus ensuite ajoutées. Des premiers appels TestClient sous restriction de boucle ont été interrompus sans assertion : ils ne constituent pas des tests rouges produit. L'exécution locale autorisée sur base jetable a ensuite terminé.
- Première passe ciblée : 117 réussites. Revue indépendante Codex, lecture sans mutation/DB, reproductions via analyse v5 : `lots n°2 à n°5`, `lots 2,3-5`, `lots 2/3` étaient tronqués; `10h30-11h30`, `10:30-11:30`, `10h30+11h30` choisissaient la première borne. **6 échecs attendus observés** (`review-red.log`), correction des gardes partagés puis **43 tests purs verts**. Les contre-exemples ne normalisent ni portée ni heure.
- Après correction : **123 tests ciblés réussis**, 1 avertissement Starlette/httpx, 21,56s (`targeted-reviewed.log`). Périmètre : projecteur pur, lecture application SQL, reader infrastructure et API existante; refus tenant étranger, hash/offset/observation incompatibles, fraîcheur/extraction, rectificatifs/conflits, valeurs absentes, répétition sans écriture, sérialisation fermée. L'authentification/policy du test HTTP reste synthétique; aucune qualification live.
- Web entier : **547 réussites, 4 ignorés, 66 fichiers, 91,40s** (`web-global.log`), code client inchangé après cette mesure. Typage Python625 fichiers, typage client, lint et build verts; chunk Vite >500kB existant. Aucun changement de schéma, dépendance ou migration.
- Backend global initial volontairement interrompu après **1 411 réussites**, 630,36s, pour intégrer la revue; cette campagne ne qualifie pas la suite entière. Suite finale relancée après les corrections, session98908, `backend-global.log`. Ne pas confondre la baseline précédente2787 avec une réussite de cette tranche.

La revue assistée Jev n'a produit aucun avis utilisable (permission puis absence de fournisseur configuré); aucun secret/profil/fournisseur ajouté. L'avis indépendant Codex reste technique, pas une validation métier humaine. Superpowers : cadrage, TDD, revue et vérification; ECC : vérification/sécurité. Graphify/Serena/Basic Memory utilisés pour l'orientation. Context7 non nécessaire : aucune question de bibliothèque ni nouvelle API tierce. OpenDesign/Impeccable réservés au prochain affichage visible.

Contre-revue indépendante après correction : 43 tests purs exécutés, aucun nouveau constat sur les deux corrections; SQL/HTTP non rejoués par le reviewer (123 ciblés exécutés par Codex intégrateur). Semgrep1.179.0 : 225 règles/9 fichiers, 0 finding/0 erreur JSON, deux avertissements de fixpoint sur la règle `python.boto3.security.hardcoded-token.hardcoded-token` (projecteur et reader); cette limite reste ouverte, pas de preuve de sécurité exhaustive. Chargement des règles autorisé après échec de téléchargement sous restriction; aucune donnée envoyée. Detect-secrets avec baseline du dépôt : 9 fichiers, exit0. Diff whitespace vert.

## Fichiers de la tranche R4g

- Application : `backend/app/modules/dce/application/requirement_values.py` (pur), `queries.py` (projection additive).
- Lecture : `backend/app/modules/dce/infrastructure/case_dce_reading_reader.py` (source exacte/courante, conflits, refus).
- Contrats : `backend/app/modules/dce/public/contracts.py`, `backend/app/interfaces/http/routes/case_dce_reading.py`, `web/src/shared/types.ts` (sans affichage).
- Régressions : `backend/tests/domain/dce/test_rc_requirement_values.py`, `backend/tests/application/test_rc_structured_reading.py`, `backend/tests/api/test_case_dce_reading_routes.py`.
- Suivi : présent dossier, index actif et plan global. Les autres différences Git précèdent cette tranche; elles ne sont pas nettoyées, indexées ou attribuées à R4g. Le snapshot `reader-before.py` privé distingue les ajouts de cette tranche dans le reader déjà modifié.

## Clôture technique locale

La suite backend finale termine avec **2 839 réussites, 2 avertissements, aucun échec, exit0, 1 566,10s (26min06)**. Les avertissements sont Starlette/httpx et Pydantic Field.alias; aucune couverture nouvelle mesurée (`--no-cov`). Log `backend-global.log`, distinct du lancement interrompu. Les neuf empreintes `code-sha256.txt` concordent après la suite; Ruff global backend/scripts, mypy625 et diff whitespace verts. Les quatre nouveaux fichiers Git sont le projecteur, ses deux suites de tests et ce dossier; aucun autre fichier inattendu introduit par R4g. Le WIP antérieur est conservé, HEAD30f26934430095632000a1d82519f61dbb4c6411 inchangé, aucun commit/push.

PostgreSQL jetable : nom/label R4g vérifiés, `SELECT count(*) FROM alembic_version` retourne0 après la suite; seul `smartao-r4g-proof-20261016` est arrêté pour suppression automatique. Pas de backend live, corpus réel, VPS, déploiement, modification de schéma, effet P3, export ou admission. Cette qualification synthétique ne prouve ni extraction universelle ni complétude du DCE. A1 non admis, A2 générique HOLD et NO-GO public maintenus.

**Prochaine étape :** R4 — afficher les valeurs candidates RC dans le panneau DCE existant et qualifier leur lecture en navigateur local synthétique, avec sources, UNKNOWN et masquage immédiat hors contexte, sans modifier les confirmations ni produire d’effet métier automatique; utiliser OpenDesign Local Codex et Impeccable. A1 non admis, A2 générique HOLD et NO-GO public maintenus.
