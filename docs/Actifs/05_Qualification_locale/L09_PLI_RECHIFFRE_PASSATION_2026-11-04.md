# L09 — pli reconstruit après révision du chiffrage et passation

Qualification locale avec limites ; le plan global est la seule autorité de statut. L09 général reste PARTIAL.

AS-IS : P7 conserve une sélection de pli exacte, une revue opérationnelle et des reçus distincts. Le parcours L08 vient de reconstruire un pli après nouvelle publication de prix, sans ajouter de fichier financier au ZIP. Le contrôle financier final reste Patron-only.

RISQUES : ancienne lecture visible sous reprise DCE incertaine, reçu technique discordant pris pour connu, ancien accord/texte/reçu transmis à un nouveau pli, données financières privées remises au conducteur, réception du dossier confondue avec OS ou conformité.

POINTS D’INSERTION : panneau de passation et appel App, stores d’intention existants, prolongement synthétique de la recette L08 et contrats P7 natifs. Aucun nouveau schéma, moteur, rôle, calcul ou porte.

PLAN MINIMAL :

- [x] Tests rouges de suspension/source-session et reçu discordant ; correction minimale sans perdre les intentions UNKNOWN.
- [x] Prolonger la recette de prix révisés vers une passation/reçu nouveaux, avec refus des anciens hash et inconnus/historique exacts.
- [x] Vérifier les octets du mémoire remis contre le ZIP et l’absence des métadonnées/montants privés dans la vue conducteur.
- [x] Revue, contrôles ciblés/globaux appropriés, rendu, sécurité ; sauvegarde puis plan et miroir relus.

TESTS À AJOUTER : aucune lecture/écriture sous suspension, réponse tardive ignorée, changement de scope relu, identifiants techniques de reçu exacts avant GET, retry identique, sélection du nouveau P5, anciens accords/refus sans effet, nouveau reçu conducteur sans héritage, confidentialité et manques visibles. Réutiliser Markdown ; pas de relance de tranche DOCX.

Checkout principal, branche et HEAD attendus vérifiés ; les 754 empreintes WIP L08 sont identiques avant édition. Preuves privées : `~/.local/share/smartao-proofs/l09-repriced-handover-20261104/`. Aucun checkout supplémentaire, reset/clean/stash, stage, commit, push, live, dépôt externe ou activation.

## Fonction livrée et contrat exact

La passation se suspend pendant la reprise DCE incertaine : aucun dossier, formulaire ou appel de lecture n’est reconduit sous cette vue. Une clé distincte de session/version/disponibilité DCE remonte la lecture, tout en conservant le store d’intention par propriétaire/Affaire. Les réponses tardives de l’ancien scope ne repeuplent pas le nouveau. Une publication UNKNOWN survit à la suspension et repart avec le même corps et les mêmes identifiants.

Le client ne traite un résultat comme reçu qu’après concordance du code, statut, command_id et idempotency_key. Le serveur exposait auparavant seulement statut/code/replayed ; les deux POST P7 renvoient désormais les identifiants **persistés de DispatchResult**, pas un écho de la requête. Le test de replay utilise volontairement un command_id de requête différent de celui du reçu stocké. Un ancien serveur sans ces métadonnées reste UNKNOWN dans le nouveau client ; aucune confirmation n’est inventée. Les commandes, leur hash historique et les permissions sont inchangés.

Les lectures réussies liste/options/historique/exact et les deux POST réussis portent `Cache-Control: no-store`. Les options contractuelles et le téléchargement technique avaient déjà ce contrôle et le conservent. Cette qualification ne garantit pas les en-têtes de toutes les réponses d’erreur.

Neuf fichiers logiciels : `web/src/features/results/CaseHandoverPanel.tsx`, son test, `web/src/app/App.tsx`, `web/src/shared/types.ts`, `backend/app/interfaces/http/routes/case_handover.py`, `backend/app/modules/patron_action/public/handover_contracts.py`, `backend/tests/api/test_handover_receipt_metadata.py`, `backend/tests/db/test_l08_pricing_response_continuity.py`, `backend/tests/db/test_l09_repriced_packet_handover.py`. Le seul complément à la recette L08 est un callback de qualification optionnel aux deux plis ; le cas sans callback est aussi rejoué. Aucun handler métier, calcul, schéma, migration, rôle, solveur ou gate modifié.

## Parcours natif source → passation → reçu

Le parcours de prix L08 est exécuté une fois sur la même Affaire : premier prix importé/publié et premier pli, puis nouveau prix publié et nouveau brouillon/revue/snapshot/transmission/P5/ZIP. Deux callbacks ajoutent une déclaration WON synthétique, une version contractuelle déclarée et une revue opérationnelle attachée au pli exact. P6/P7 et le contrat demeurent déclaratifs ; aucune attribution réelle ou autorité juridique n’est déduite.

Pour chaque génération, un extrait unique est prélevé dans les octets du mémoire du ZIP, avec un locator déclaré. La passation retient package/version/hash, DCE et hash du mémoire exact, avec preuve EXACT_BYTE_MATCH. Le Responsable affecté reçoit uniquement ces octets techniques : comparaison binaire et SHA contre le ZIP, contrôle final financier et ZIP complet refusés403. Les IDs des rapports de prix liés/derniers publiés, pricing_reference, financial_snapshot_id, OFFICIAL_PRICING_VERSION, montants et storage_key sont absents de sa projection.

La deuxième passation utilise un nouvel acte, de nouveaux points et un nouveau reçu ; l’ancien hash est refusé409. L’ancienne passation et ses reçus deviennent HISTORICAL sans modification des lignes historiques. Les libellés « Responsable déclaré V1 » et « Preuve attendue V1 » ne sont pas recopiés : responsable et preuve attendue manquent explicitement en V2. Copie du hash de vue du premier reçu refusée409, réception complète refusée422 en présence des manques ; seul un nouveau RECEIVED_WITH_GAPS confirmé est enregistré et rejoué sans double effet. Réception du dossier, contrat, lancement et ordre de service restent distincts.

## TDD et essais intermédiaires

- Quatre rouges Web observés : suspension absente, scope non relu, deux identifiants techniques discordants acceptés. Treize tests du panneau passent après correction ; un test complémentaire prouve la reprise identique après suspension UNKNOWN.
- Le typecheck a révélé le contrat HTTP incomplet de reçu : les identifiants n’étaient pas émis. Six rouges API ont ensuite reproduit les deux réponses sans métadonnées et les quatre lectures sans no-store ; six verts après correction. Le premier essai natif a aussi reproduit l’absence de no-store sur lecture exacte ; le scénario complet passe après correction.
- Une annotation de dictionnaire mixte manquait dans le test HTTP, ajoutant un diagnostic mypy ; elle est corrigée, la dette finale est identique à la baseline. Un lancement Vitest depuis la mauvaise racine est une erreur d’outil, non un échec produit.
- Revue indépendante en lecture seule, puis contre-revue du complément contrat/cache : aucun autre finding concret. Les métadonnées viennent du reçu stocké, le service et les gates restent inchangés. La revue n’a pas exécuté de tests et ne vaut pas accord humain.

## Vérifications

- Web global final sur gel : **789 réussites,4 ignorés,93 fichiers,276,77 s,exit0**. Neuf SHA logiciels inchangés après la suite.
- Web ciblé final : **30 réussites,5 fichiers,17,19 s** ; résultats, store d’intention, formulaires, reprise/source et reçus. Types Web, lint et build verts ; avertissements existants App `setDecisionDossier` et chunk >500 kB conservés.
- Native couplée isolée : **1 réussite en69,18 s**, deux plis/passations/reçus sur une Affaire ; contrats HTTP isolés finaux : **6 réussites**. Campagne backend élargie : **44 réussites en174,66 s**, enveloppes HTTP, revue opérationnelle, workflow, HTTP E2E local existant, L08 sans callback et L09 couplé. Elle couvre droits/tenant/MFA, contexte, sources altérées, concurrence, append-only, historique, idempotence et refus.
- Mypy application708 sources vertes ; application/tests206 diagnostics dans40 fichiers sur1273 sources, identiques à L08 après normalisation des numéros de ligne. Ruff et format des cinq fichiers Python vérifiés ; Alembic inchangé `20261102_0147`, fixtures upgrade/downgrade jusqu’à base.
- Chrome DevTools Local : vrai panneau sur projections natives enregistrées aux deux instants, API de relecture simulée, sans nouvelle écriture métier navigateur. Suspension/reprise et relecture exercées ; captures inspectées à1280/393px, sans débordement global, cookies/stockages vides et ressources externes absentes. Assertions DOM sur manques/UNKNOWN, reçu avec réserves et absence des anciens libellés. Les captures de tête ne montrent pas tous les détails sous la ligne de flottaison. Aucun test Playwright, de login navigateur réel ou d’accessibilité complète ; l’HTTP E2E backend reste une preuve distincte.
- OpenDesign Local Codex : catalogue courant et artefact SMART AO C08 existant consultés ; styles du dépôt conservés, référence Linear seulement complémentaire et autorité Owner/CYTD inchangée. Impeccable contexte/craft-floor/harden et detector `[]` ; aucun nouveau prototype ou génération Cloud.
- Semgrep1.183.0, `p/security-audit`, métriques désactivées :99 règles/9 fichiers,0 finding/0 erreur ; code analysé localement, aucun résultat transmis, sans certification globale.
- Neuf SHA logiciels figés et relus ; diff du delta vérifié et scan borné des lignes ajoutées sans secret reconnu. Base jetable :0 table métier/0 révision Alembic, conteneur exact `a9ea09e462ce095e696076d5fb72dd69b512d6a85e4e7359a3c954dc5256c15b` sans montage persistant supprimé ; clients navigateur et preview dédiés fermés, services préexistants conservés.

## Limites et invariants

La qualification reprend la frontière L08 : DCE initial de fixture déjà admis/classifié, copie de développement, imports et publications de prix natifs ; aucun nouveau DOCX/OCR/réimport DCE ou corpus réel. Le contrat signé est seulement une version déclarée, sans autorité ou authenticité de fichier prouvée. Aucun dossier complet, prix/cash certain, OS, conformité ou réception juridique n’est inféré ; L09 général PARTIAL.

Les stores d’intention sont en RAM, sans reprise durable après rechargement complet. La source externe modifiée peut nécessiter une relecture ; pas de surveillance continue. Les seuls changements backend portent sur métadonnées/en-têtes de réponses, sans nouvel effet métier, champ privé conducteur ou promotion de porte. FINANCIAL_PRIVATE, permissions, sources/versions/hash/locator, UNKNOWN, append-only et P0–P7 conservés. A1nonadmis/A2HOLD, candidats et NO-GO public inchangés ; aucun commit/push/live/VPS/déploiement/dépôt ou effet externe.

Méthode appliquée : Superpowers cadrage, plan, TDD, revue et vérification ; ECC product-capability, security-review et verification-loop ; Graphify avant exploration, Serena activée/navigation symbolique, OpenDesign Local Codex, Impeccable, Chrome DevTools Local et Basic Memory. Context7 non sollicité sans question de bibliothèque nouvelle ; Jev/Manus sans gain sur ce périmètre borné. Plan seul statut ; miroir synchronisé et relu après consolidation finale.
