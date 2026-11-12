# L09 — rapprochement offre/contrat et passation conducteur

## AS-IS et sortie demandée

Le P7 natif conserve un WON par lot, le P5 autorisé exact et ses références techniques, une décision/contexte et les conditions OPEN. Le contrat reste UNKNOWN; le lecteur ne renvoie que la dernière révision par attribution. Les versions de contrat/avenant et leurs remplacements existent dans Pricing; ils ne prouvent pas à eux seuls une signature ni une réception externe. Aucun reçu du dossier par le conducteur n’est enregistré. La projection actuelle copie les libellés de conditions Patron, alors que ces textes peuvent contenir de l’économie privée.

Sortie du parcours : le Patron sélectionne l’offre et la version contractuelle déclarée, publie des points opérationnels sourcés (engagements/exclusions/écarts/conditions/actions/responsables/preuves), puis le Responsable affecté lit la version exacte et accuse sa réception, éventuellement avec manques. Un point critique sans responsable/source/état ne donne jamais une passation complète. P7 et réception du dossier restent distincts d’un OS ou d’une acceptation juridique.

## Risques et invariants

- Fuite d’une marge/hypothèse ou d’un texte privé au travers d’une condition, d’une référence ou d’un document : projection publique fermée, aucun transfert automatique de texte privé. Une condition reste visible par son identité/état; sa formulation opérationnelle est un acte humain explicite.
- Mauvais lot/paquet/version de contrat; remplacement après revue; confusion hash d’enregistrement/hash de fichier : sources exactes et distinctions explicites, UNKNOWN sur tout élément non prouvé.
- Perte de conditions/actions, faux dossier complet : couverture des conditions contrôlée, manques visibles, aucune complétude calculée par simple présence de texte ou reçu.
- Reçu perdu, double clic, concurrence, contexte changé : IDs et corps figés, contrôles serveur tenant/rôle/affectation et révision/hash exacts, append-only et replay.
- Historique réécrit ou source actualisée implicitement : nouvelles révisions; historique/source figée distingués de l’état courant, requalification sans relier automatiquement une autre version.

## Points d’insertion et plan minimal

1. Étendre facultativement RecordCaseHandoverSnapshot et son JSON natif immuable avec une revue opérationnelle fermée. Conserver le payload des anciens appels sans revue. Extraire projection sûre et calcul des manques dans une fonction pure testable; compléter les lecteurs SQL natifs pour options/sources/versions/remplacements, sans nouveau registre de comparaison parallèle.
2. Vérifier le WON courant, l’offre P5 exacte, le lot, la version déclarée et son empreinte, les conditions référencées et les limites de source; publier seulement les champs opérationnels validés. Revalider les fichiers techniques exacts lors de leur lecture; ne considérer un brouillon C10 comme offre vendue que si son entrée et ses octets sont effectivement présents dans le P5 autorisé. Le ZIP natif inspecté contient le document technique principal; la seule présence de métadonnées C10 ne prouve pas l’inclusion des brouillons.
3. Ajouter un reçu opérationnel distinct append-only sur snapshot/révision/vue sûre/hash exacts. Migration0143 statique, FK tenant/Affaire/snapshot, refus de downgrade avec reçus; capacité d’écriture limitée au Responsable explicitement affecté, sans élargir les droits financiers ni modifier P0–P7. Reçu avec manques possible sans déclarer le contenu ou contrat approuvé.
4. Après OpenDesign Local/Impeccable, compléter le panneau existant : sélection et revue structurées Patron, lecture conducteur et reçus/historique, sources/manques, masquage immédiat et retry identique. Aucun JSON à inventer pour ce parcours.
5. Prouver un scénario BTP synthétique accès contraint/transport exclu/contrat déclaré/condition/action et reçu, puis source remplacée et historique. Refus rôle/tenant/Affaire, confidentialité, concurrence, interruptions et migrations. Revue puis suites et scans séquentiels (éviter la saturation RAM de L08), cleanup et suivi/mémoire.

## Tests à prouver

Rouges avant comportement : libellé économique interdit dans projection; conservation de l’identité des conditions et des sources; absence de revue UNKNOWN; comparaison humaine et sources exactes; responsable/preuve manquants; version remplacée/hors Affaire; même corps/IDs après UNKNOWN; reçu sur mauvais hash/révision; mauvaise affectation/profil; changement de contexte pendant POST/GET; historique; aucune P6/P7 d’exécution/OS/P3/autorisation P5 automatique. Upgrade/contraintes/downgrade vide/refus non vide/head0143 et anciens parcours.

## Autorités et limites

PF31-04/06, PF2-081, M31-04 et R31-05; CT31-02/04/06 et historique CT31-14/15. Aucun droit acquis, réception externe, signature réelle ou adéquation de toutes les pièces n’est déduit d’une déclaration. Pas de calcul juridique ni d’écart financier automatique. Corpus synthétique local uniquement; aucun VPS/déploiement/push/effet P3/dépôt externe/GO public. A1 non admis, A2 HOLD, DPGF hors RAG et moteurs candidats inchangés. Le plan global reste l’unique statut opérationnel.

## Checkpoint de réalisation — 25/10/2026, qualification en cours

Python/API : publication opérationnelle optionnelle dans le snapshot natif, projection fermée des conditions privées, rapprochement déclaré d’une version contractuelle et preuve d’extrait dans les octets du document P5. Reçu distinct append-only lié à la révision et au hash de la vue; migration locale0143. Invalidation après WON devenu LOST, remplacement contractuel ou fichier altéré; verrouillage des sources décision/contrat lors du reçu. Ces verrous et les revalidations restantes doivent encore être éprouvés.

Interface existante : formulaire Patron avec justification et confirmation, points/action/responsable/preuves, lecture et reçu conducteur, historique et mémoire d’intention en RAM pour les retries identiques; masquage par propriétaire/Affaire. Direction issue du contexte OpenDesign Local C08, sans nouvelle palette; Impeccable consulté avant code.

Preuves intermédiaires : 5 tests purs backend et 3 scénarios PostgreSQL verts; 4 tests Web ciblés verts, TypeScript vert; lint sans erreur avec un avertissement App.tsx. Les suites globales, les négatifs étendus, migrations/concurrence, navigateur et scan L09 ne sont pas encore qualifiés. Ce checkpoint ne clôture pas L09.

Reprise technique : principal `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`, WIP préexistant préservé; aucun commit/push. PostgreSQL jetable `smartao_l09_dev` dans `smartao-l04-acts-pg-20261020`, socket local et ACL UID70 actifs pour la qualification, à nettoyer en fin. Preuves privées : `/home/noor/.local/share/smartao-proofs/l09-handover-20261025/`.

## Parcours codé et frontières de preuve

Le Patron choisit une attribution WON courante et son P5 autorisé exact, puis une version de contrat déclarée ou UNKNOWN. La revue contient des points opérationnels, leur nature/criticité, un extrait et ses localisations, l’écart déclaré, les conditions référencées, l’action, le responsable déclaré et la preuve attendue. Justification et confirmation explicites sont obligatoires dans l’interface; le raccourci historique sans revue a été retiré. L’API ancienne reste compatible, sans ajouter de champ au hash de retry lorsque la revue est absente.

Le lecteur de contexte fige l’empreinte de portée/DCE/décision présentée; la publication la compare sous verrou à l’état courant. Une divergence renvoie409. Un extrait n’est EXACT_BYTE_MATCH que s’il apparaît une seule fois dans les octets du document technique P5, chevauchements compris. Le hash du contrat est celui de son enregistrement déclaré : aucune identité de fichier signé ni autorité juridique n’est inventée. Les brouillons C10 sont exclus de cette preuve s’ils ne sont pas réellement dans le ZIP autorisé; leurs seules métadonnées ne prouvent pas une offre vendue.

Le Responsable explicitement affecté lit les points publiés et les manques, puis enregistre un reçu de la révision/vue SHA exacte. Le reçu est append-only, distinct de tout OS/P6/P7 d’exécution, signature ou acceptation externe. Les sources Case, décision, analyses gelées, contrat et octets P5 sont revalidées; les sources décision/contrat sont verrouillées lors de l’acte. Une version remplacée ou invalide reste visible comme historique/REVIEW_REQUIRED. Les textes de conditions Patron ne sont jamais copiés implicitement; leur identité/état reste visible, leur formulation publique absente reste UNKNOWN.

Les intentions sont conservées uniquement en RAM dans la portée propriétaire/session/Affaire. UNKNOWN impose le corps et les identifiants d’origine; lecture de rapprochement seulement après reçu ou409. Un changement de contexte masque immédiatement les résultats; aucune persistance de secrets, cookies ou jetons navigateur n’est utilisée dans la recette. Historique des snapshots paginé; au-delà de100reçus, la limite est explicite, sans couverture exhaustive présumée.

| Partie du parcours | Code natif et preuve principale |
|---|---|
| Publication et projection sûre | [Service](../../../backend/app/modules/patron_action/application/case_handover.py), [handler](../../../backend/app/modules/patron_action/application/case_handover_handler.py), [projection](../../../backend/app/modules/patron_action/application/operational_handover.py), [sources SQL](../../../backend/app/modules/patron_action/infrastructure/operational_handover.py) |
| Lecture, comparaison et historique | [Lecteur](../../../backend/app/modules/patron_action/infrastructure/handover_reader.py), [routes](../../../backend/app/interfaces/http/routes/case_handover.py), [contrats](../../../backend/app/modules/patron_action/public/handover_contracts.py) |
| Reçu exact et conservation | [Handler](../../../backend/app/modules/patron_action/application/handover_receipt_handler.py), [modèle](../../../backend/app/modules/patron_action/infrastructure/models/handover_receipt.py), [migration0143](../../../backend/alembic/versions/20261025_0143_case_handover_receipts.py) |
| Parcours existant | [Panneau](../../../web/src/features/results/CaseHandoverPanel.tsx), [formulaire](../../../web/src/features/results/HandoverReviewForm.tsx), [lecture/reçu](../../../web/src/features/results/HandoverSnapshotRead.tsx), [intentions](../../../web/src/features/results/HandoverIntentStore.ts) |
| Régressions | [Workflow SQL/HTTP](../../../backend/tests/db/test_operational_handover_workflow.py), [projection/contrats](../../../backend/tests/application/test_handover_operational_review.py), [Web](../../../web/src/features/results/CaseHandoverPanel.test.tsx) |

## Mise au point et preuves intermédiaires consolidées

Les régressions rouges conservées couvrent : projection de libellé privé, perte lors de double projection, conflit d’idempotence, attribution remplacée, octets altérés, contexte de publication changé, extrait chevauchant, catalogue d’affectation incomplet, limite de reçus silencieuse, frontière d’erreur du lecteur de contexte, ancien raccourci UI sans confirmation et débordement mobile. Le handler de reçu a été replacé dans `application/*_handler.py` après le rouge architectural, sans exception ajoutée au contrôle.

117tests ciblés backend verts, puis reçu hors Affaire1/1 et purs7/7 verts (recouvrements, ne pas additionner). Verrous réels Decision/ContractInstrument vérifiés par une deuxième connexion NOWAIT; UPDATE/DELETE refusés, révision de reçu liée au snapshot, downgrade avec reçu refusé et aller-retour vide0142→0143 conservant le snapshot qualifiés. Les tests étendus vérifient rôle/profil/affectation, MFA/finance révoqués, mauvais hash/révision, contrat remplacé, fichier altéré, WON devenu LOST et replay sans double effet.

Web final :666réussites/4ignorés/80fichiers,246,02s,exit0; ciblés8/8 et build/TypeScript verts. Premier run global interrompu avec exit130 pour retirer le raccourci UI, conservé comme campagne non qualifiante. Lint :0erreur,1avertissement App.tsx sur la dépendance d’un effet antérieur. Bundle principal832,95kB (>500kB), aucun seuil relevé. Application Python : mypy675fichiers sans diagnostic. Contrôle étendu app/tests :207diagnostics dans41fichiers de tests hors périmètre L09; aucun des33fichiers sources/tests du périmètre n’a de diagnostic. Cette dette reste ouverte; aucune CI entièrement verte n’en est déduite.

Chromium isolé via Chrome DevTools MCP :25contrôles consignés, API native en processus/TestClient et PostgreSQL jetable, identités synthétiques. Publication avec reçu perdu après commit, isolation de session, replay identique, Responsable et reçu avec manques, changement d’Affaire, octets P5 SHA exacts, invalidation après affichage/409, reçu devenu historique et absence de nouvel effet P5. Aucun cookie/Authorization envoyé par le navigateur, stockages vides et aucune requête HTTP externe. Vue desktop/mobile inspectée; débordement initial471px pour390px corrigé avec styles natifs, lecture finale390/390. Pas Playwright, backend live, authentification réelle ou certification d’accessibilité. Après ces preuves, le raccourci UI sans revue a été retiré et le refus hors Affaire du lecteur de contexte a été normalisé. Régressions jsdom/SQL puis suites globales qualifient ces deltas; les autres chemins navigateur conservent leur portée de preuve.

OpenDesign Local Codex : catalogue courant et contexte natif C08 de comparaison de lignes consultés avant code; aucune nouvelle palette ni bascule Cloud/BYOK. Impeccable CLI4.0.0 (skill4.3.1) : composants sans finding; inclusion de la feuille CSS globale produit4signaux antérieurs sur les bordures d’autres composants, hors lignes ajoutées. Triés, sans refonte incidente ni affirmation de conformité visuelle complète. Superpowers : cadrage borné, plan, TDD, diagnostic, revue et vérification; ECC product-capability/vérification. Graphify consulté avant recherche manuelle, Serena activée; Jev/Manus non nécessaires pour ces contrats déterministes.

La suite backend globale neuve et les scans finaux restent en cours à ce point du journal. Ne pas clôturer L09 ni transférer les résultats L08. Les33hashes sources/tests sont conservés dans `source-hashes-before-global.json`; la validation finale doit vérifier leur stabilité. Aucun commit/push, source réelle, VPS, déploiement, P3, activation de candidat, admission A1/A2 ou GO public.


### Campagne backend globale en cours — complément de reprise

Un échec est apparu vers63% de la première campagne; diagnostic détaillé attendu à sa fin, aucune clôture autorisée sur ce résultat. Conserver le log et son code de sortie, reproduire puis corriger la cause avant qualification finale. Le cache pytest des anciens échecs date d’avant la campagne et n’est pas son diagnostic.

Ruff a aussi demandé un retour ligne sur le CHECK `receipt_kind` de la migration0143. Seul cet espace SQL a changé pendant la campagne : AST avec chaînes normalisées identique, ancien fichier et hashes conservés dans `migration-before-format.py` et `migration-whitespace-delta.json`.32autres fichiers sont strictement inchangés. Rejouer le scénario migration/reçu après la campagne, mettre le delta à qualificationPASSED, puis vérifier le manifeste final33fichiers. Ne pas remplacer le manifeste initial ni prétendre que les33fichiers ont tous été identiques au lancement de la globale.


### Cause de la première campagne rouge et relance

Campagne initiale interrompue pour diagnostic :2690réussites/1échec/2warnings/1796,22s/exit2. L’échec de `test_assessment_links_are_append_only_and_nonempty_downgrade_is_refused` vient uniquement de l’assertion L05 attendue0142 au lieu de la tête0143. Le refus de perte d’historique a bien eu lieu et la transaction de downgrade a conservé la tête courante. L’attente est maintenant reliée à EXPECTED_ALEMBIC_HEAD; aucune assertion de protection n’a été retirée. Le double de contexte de ce même test est typé explicitement, sans changement de comportement.

Régressions :2/2vertes (L05 refus non vide, L09 refus non vide/aller-retour vide) après le retour ligne SQL équivalent. Ancien log/manifeste archivés sous `initial-red-*`; nouvelle base `smartao_l09_final2`, session84918,34sources/tests figés. Mypy app/tests final206diagnostics/40fichiers hors périmètre, application675sans diagnostic. La globale finale est en cours, pas PASS. Le script privé finalize_docs.py exige exit0/scans/cleanup et les34hashes identiques à son lancement avant clôture.


## Clôture locale consolidée —25/10/2026

Backend final : **3964 passed, 1 warning in 1519.68s (0:25:19)**, exit0, base `smartao_l09_final` neuve, --import-mode=importlib. Web final668/4ignorés et25contrôles navigateur synthétiques; détails et deltas ci-dessus. Aucun résultat interrompu/rouge n’est promu. Mypy application675 sans diagnostic, app/tests206diagnostics/40fichiers hors L09 : CI entière non qualifiée. Couverture CI non remesurée.

Semgrep1.182.1 p/security-audit : 34fichiers analysés,0finding/0erreur; exclusions et statistiques dans `semgrep-qualified.json`, règles téléchargées uniquement, analyse locale, métriques/versioncheck désactivés, aucun résultat envoyé. Secrets34fichiers :0signal restant, baseline copiée dans le dossier privé pour préserver le WIP non indexé, original strictement inchangé; --no-verify/cores1. Impeccable composants0signal,4signaux de CSS antérieure hors lignes L09 triés; aucune correction incidente du design system.

34SHA sources/tests finaux vérifiés après les suites/scans;Python inchangé depuis la globale backend; les2fichiers Web409 ont leurs régressions et leur globale finale. Un retour ligne du CHECK SQL0143 a été imposé par Ruff pendant la première campagne rouge : AST et SQL normalisés identiques, aller-retour migration/reçu rejoué après la globale; delta et original archivés, aucune logique de migration modifiée; diff vérifié et aucune modification de cahier Owner. Bases jetables dev/browser/finale vérifiées àAlembic0; conteneur dédié arrêté/networknone/aucun port, ACLUID70 retirée/socket700. Navigateur, Vite et adaptateur arrêtés. Branche codex/reconcile-smartao-20261009, HEAD30f26934430095632000a1d82519f61dbb4c6411 et WIP intégral conservés; aucun commit/push.

L09 général PARTIAL : preuve opérationnelle humaine, aucune signature/réception externe/validité juridique ou analyse exhaustive déduite. Les portes et droits financiers ne sont pas modifiés; nouvelle capacité de reçu attribuable explicitement, jamais octroyée automatiquement. A1 non admis/A2 HOLD/NO-GO public, DPGF hors RAG, candidats inchangés.

Un dernier cas de retry a été corrigé après la globale backend :409 COMMAND_IN_PROGRESS ou sans détail reste UNKNOWN, contrairement aux sept conflits terminaux explicitement reconnus. Deux rouges puis dix ciblés verts, contre-revue sans défaut identifié, build/types/lint et globale Web668/4ignorés/94.10s/exit0 qualifient ce delta. Seuls CaseHandoverPanel.tsx et son test ont changé; tous les fichiers Python restent identiques à la globale3964. Semgrep99règles/34fichiers et secrets34fichiers repassent à0finding/0erreur. Les quatre tests Web ignorés dépendent des fixtures HTTP/PostgreSQL C08 non chargées; ils ne qualifient pas L09.

Le plan seul porte la clôture bornée et la suite : L10 — livrer le suivi des changements en exécution sur la même Affaire : relier instruction, OS ou avenant aux engagements transmis, conserver le delta déclaré, les actions, responsables et preuves dans la chronologie, puis qualifier remplacement de source/contrat et refus tenant/rôle sans déduire réception externe ni effet juridique.
