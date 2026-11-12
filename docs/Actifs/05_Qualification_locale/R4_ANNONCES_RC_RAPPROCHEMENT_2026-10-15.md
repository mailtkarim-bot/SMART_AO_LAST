# R4 — Annonces du RC et rapprochement candidat — 15 octobre 2026

## AS-IS
R3 est qualifiée techniquement sur données synthétiques (backend2603/web544+4ignorés). Les observations RC v4 produisent des exigences; leur matérialiseur refuse un kind inconnu. La couverture connaît les pièces admises, anomalies d'archives et déclarations manquantes, mais ne rapproche pas les annonces du RC.

## Risques
Confondre composition du DCE et pièces de remise, propager une négation ou un lot voisin, déclarer une absence d'après un nom/famille, utiliser une extraction ancienne, exposer du texte privé ou changer les exigences/P3 existantes.

## Points d'insertion et conception bornée
Projection candidate distincte dans la lecture DCE existante, sans nouveau registre, migration, commande ni effet métier. Détecteur déterministe local alimenté exclusivement par fragments RC classifiés/courants, hash original et texte vérifiés. Source document/extraction/fragment, offsets UTF8 et locator fermé; pas de nouveau hash/parser ni extrait privé public. Famille et portée lot explicitement citées, négations et contradictions conservées. Pièces de même famille proposées comme rapprochements seulement : présence/applicabilité/criticité UNKNOWN.

## Plan minimal — Superpowers writing-plans/TDD
- [x] Détecteur : table de cas synthétiques positifs/négatifs/ambiguïtés, offsets exacts, listes, lot/négation locaux; rouges puis changement minimal et métriques omissions/faux positifs.
- [x] Lecture SQL/API : sources courantes exclusivement, limites explicites, rapprochement sans nom de fichier ni présence déduite; tests tenant/version/refus/rectificatif/source discordante.
- [x] Panneau existant : candidats et UNKNOWN consultables, mêmes classes/design Owner PF31-11 via OpenDesign Local Codex et Impeccable; pas de nouvel acte humain ou automatique.
- [x] Revue, tests appropriés, types/lint/build/Semgrep, plan/journal et miroir Basic Memory.

A1 non admis,A2 HOLD,NO-GO public. Local synthétique uniquement,aucun corpus réel,VPS,déploiement,push,P3 ou admission automatique. Les versions existantes d'analyse/matérialisation restent inchangées.

## Périmètre de qualification acquis
Détecteur candidat distinct de l'analyse RCv4 et de sa matérialisationv2, toutes deux inchangées. Les références de famille réutilisent le catalogue existant via `document_family_references`, avec alias BPU long pour la lecture candidate uniquement. La classification historique n'est pas réécrite. Composition du DCE, remise, remise non requise, interdiction et ambiguïtés restent des signaux candidats; jamais des faits de présence ou d'absence.

Rattachement lexical local des participes/actions au document : un joint de dilatation et des matériaux fournis ne sont pas des annonces documentaires. Négation non reconnue, futur, rôle offre/candidat, référence normative et portée conditionnelle restent ambigus. Deux signaux opposés ne sont marqués qu'à titre candidat et lorsque leurs lots cités peuvent se recouvrir. Les nombres de lots cités ne qualifient pas les identités/applicabilités du modèle Case.

Lecture SQL : documents RC classifiés, extractions COMPLETED courantes exclusivement, égalités conservatrices via helper DCE existant, hash d'entrée égal à l'original et hash du texte vérifié. Ancres document/extraction/fragment et offsets UTF8, locator fermé. L'en-tête de liste garde une seconde ancre dans le même fragment. Pas de texte, nom, hash ou parser privé nouveau dans le DTO public. Rapprochement par famille seulement : même avec un document candidat, `presence_status`, `applicability`, `criticality` restent UNKNOWN. Pas de déclaration manquante/exigence/acte P3 créé.

Bornes :2000fragments RC,2Mcaractères agrégés,1000candidats;rejet explicite REJECTED_LIMIT sans résultat partiel. La couverture sémantique n'est jamais déduite d'un scan sans candidat.

## Mesures et preuves acquises avant le global final

### Calibration synthétique, pas Golden DCE
Référence figée `backend/tests/fixtures/rc_document_announcements_v1.json`,24textes/25signatures attendues. Signatures= famille,signal lexical, nombres de lots explicitement cités; ce n'est pas une mesure de présence documentaire réelle. Jeu créé par Codex, **pas une annotation humaine indépendante ni un benchmark de généralisation**. L'extracteur reçoit seulement le texte, pas les attendus.

| État | Signatures attendues retrouvées | Omissions | Faux positifs de signature | Présences déclarées connues |
|---|---:|---:|---:|---:|
| Avant correction des six formes manquantes |17|8|0|0|
| Après correction, référence inchangée |25|0|0|0|

Les six formes corrigées couvrent dossier composé de, pièces constitutives, BPU en toutes lettres, remise passive, liste à joindre, absence explicitement annoncée. Les contre-exemples de genre/pluriel, annexe nominale, joint de dilatation, matériaux, rôle offre, négation et futur ont aussi leurs régressions.

- TDD exécuté : module initial absent puis stub →10comportements rouges/4verts;8contre-exemples supplémentaires rouges→verts;4SQL rouges→verts;1conflit rouge→vert;5P2 de revue rouges→verts;6cas de matrice rouges→verts;contre-exemples BTP/genre rouges→verts. **66tests purs de détection** et **116avec le reader** verts.
- Ciblés backend lecture/classification/API/SQL et nouveaux cas : **156/156**,1warningStarlette,47,68s. Dont8SQL source/page, refus récent/hashparent/hashtexte, limites et absence d'exigence/déclaration créée.
- Web final : **545réussites/4ignorés,66fichiers**,51,41s avec2workers;typecheck/lint/build verts. Ruffglobalbackend/scripts et mypyapp624sources verts;Impeccable0constat. Warning bundle>500kB conservé.
- Revue indépendante : deux P2 de polarité/attribution aux familles ont été reproduits puis corrigés. Relecture finale statique bornée provenance/identités/tenant/UTF8/budgets/sans effets : aucun nouveau blocage constaté. Pas de preuve humaine ni de généralisation induite.
- Semgrep**1.179.0,p/security-audit,225règles/11fichiers,0finding/0erreur**;analyse locale et résultats non envoyés. Secrets ciblés et diffcheck verts.

### Chaîne source consultable et navigateur local
Harnais horsGit `/home/noor/.local/share/smartao-proofs/r4-20261015/` : `source-manifest.json`, PDF synthétique original copié byte-exact, hashes/locators des2fragments, projection `harness/reading.json` et `source-chain-verification.json`. Hash de l'original et hashes/locators des fragments relus après capture,3candidats HTTP reliés à ces sources. Les hashes restent dans le manifeste privé, pas le DTO public.

FastAPI/TestClient réel et SQL/PostgreSQL jetable, mais acteur/politique/runtime Case synthétiques et tenant/case alignés explicitement. **Cela ne qualifie pas l'auth live, la topologie Case ni une affectation réelle.** Un premier appel du double de politique avait une signature incompatible; harnais corrigé, base secondaire revenue à base, preuve rejouée. Captures provisoires avant persistance du manifeste conservées séparément et remplacées pour la qualification par la capture finale liée au manifeste.

ChromeDevToolsLocal isolé, composant réel avec cette projection capturée :3candidats/pages1et2/signauxopposés/UNKNOWN visibles,390et1440sansdébordement, ouverture/fermeture au clavier, candidats retirés sans couverture.13requêtes de dernière navigation uniquementloopback. Harnais arrêté et onglet fermé. Pas dePlaywrightMCP, backendlive ni parcours applicatif/auth complet.

## Limite reproduite hors calibration — R4 reste ouverte
Le détecteur lit chaque fragment séparément. Contre-exemple synthétique : fragment1=en-tête «Le DCE comprend les pièces suivantes :»,fragment2=liste CCAP/CCTP. **0candidat en lecture fragmentaire contre2dans le texte continu : deux omissions connues.** `cross-fragment-limit.json` conserve ce constat. La relation entre fragments/pages et les en-têtes répétés doit être qualifiée avant de transporter un contexte; aucune concaténation ou attribution silencieuse n'est ajoutée ici.

La première sous-tranche R4 qualifie les candidats dans un même fragment et leur exposition/source, **pas R4 entière ni une analyse complète de DCE**. Generalisation, tableaux, clauses imbriquées, contexte site/phase, corpus réel et performance au pire cas non qualifiés. Présence/applicabilité/criticité restent UNKNOWN;A1nonadmis,A2HOLD,NO-GOpublic.

## Fichiers et méthodes
Production : `application/document_announcements.py`, helper ajouté à `application/classification.py`, DTO `application/queries.py`, `infrastructure/case_dce_reading_reader.py`, `public/contracts.py`, `web/src/shared/types.ts` et `web/src/features/dce/DceKnowledgePanel.tsx`. Tests : nouveaux `domain/dce/test_document_announcements.py`, `application/test_dce_document_announcements.py`,fixtureJSON, doubles reader et panneau.test.tsx. Aucun schéma, commande, droit, dépendance ou analyse historique modifié.
Superpowers brainstorming/writing-plans/TDD/revue, ECC api-design/verification-loop/sécurité par la revue, Graphify, Serena activée; OpenDesign Local Codex/catalogue et Impeccable réutilisés pour la surface existante, aucun style inventé/refonte. Jev/Manus non nécessaires à ce socle déterministe; comparaison de moteurs et validation humaine ne sont pas déduites des tests.

Suite backend globale finale en cours;aucun PASS global anticipé. WIPpréservé,aucuncommit/push/VPS/déploiement/P3/corpusréel/admission.


## Résultat final du 15/10/2026 — première sous-tranche qualifiée localement

La suite backend globale finale a exécuté **2677 tests réussis, 2 warnings, 1469,15s**. Warnings : dépréciation Starlette/httpx et alias Pydantic `limit` sans effet dans son contexte existant; aucune erreur de test. Journal final conservé dans le répertoire privé de preuves. Les12SHA-256 code/fixture correspondent exactement au manifeste de qualification. Les deux bases jetables ont été vérifiées à Alembic base (0ligne), puis seul le conteneur identifié `smartao-r4-proof-20261015`/label `r4-20261015` a été arrêté et retiré automatiquement.

Plan/index/journal mis à jour : première sous-tranche R4 qualifiée pour les candidats dans un même fragment; R4 reste ouverte sur les deux omissions entre fragments. HEAD `30f26934430095632000a1d82519f61dbb4c6411`, branche `codex/reconcile-smartao-20261009`, WIP local préservé et non commité. Aucun push, backend live, corpus réel, VPS, déploiement, effet P3 ou GO public.

Prochaine étape : R4 — qualifier la continuité des en-têtes de listes RC entre fragments/pages consécutifs, avec ancres distinctes, version/extraction exactes et refus des ruptures; corriger les deux omissions reproduites sans transférer un contexte non prouvé. Préserver UNKNOWN, A1 non admis, A2 générique HOLD et NO-GO public.

Miroir Basic Memory `smart-ao-v8` synchronisé puis relu : résultat global2677/2677, deux omissions connues et prochaine étape exacte vérifiés. Le plan reste la seule autorité de statut.
