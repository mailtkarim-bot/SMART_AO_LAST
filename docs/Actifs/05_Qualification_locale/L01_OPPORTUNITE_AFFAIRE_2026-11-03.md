# L01 — Opportunité synthétique → qualification humaine → Affaire — 3 novembre 2026

Le plan global est l’unique statut. Parcours local et synthétique, sans collecte BOAMP live, conversion automatique, probabilité commerciale, effet externe ou promotion de porte.

## Résultat utilisateur

Le Patron consulte un avis rejoué, son score public expliqué, ses captures/hash/version et ses inconnus avant de décider. Il choisit décision et motif P0, confirme cet avis exact, puis confirme séparément l’ouverture avec inconnus. Il retrouve l’Affaire réellement créée ou celle déjà liée à une autre capture du même avis.

Après résultat UNKNOWN, sélection, décision et identifiants sont figés ; seule la même opération peut être rejouée. Un reçu confirmé est suivi d’une lecture, pas d’une nouvelle création. Une réponse tardive d’un ancien propriétaire ne déclenche ni nouvelle écriture ni exposition de sa source.

## Cadrage et causes

AS-IS : ingestion/scoring/persistance, P0 et création normale de Case existent. Trois rouges SQL ont révélé la réutilisation d’une ancienne qualification positive après REJECTED/SNOOZED, et une seconde Affaire pour une nouvelle capture du même avis. Les inconnus structurés n’étaient exposés qu’après ouverture. La qualification frontend régénérait ses identifiants au retry et n’isolait pas les réponses par propriétaire.

RISQUES : décision humaine périmée, doublon entre captures, course qualification/conversion, ancien reçu inutilisable, collision d’identifiant intertenant, origine sans motif exact, réponse perdue assimilée à échec, mauvaise Affaire sélectionnée, données de l’ancien propriétaire visibles.

INSERTION : adaptateur BOAMP autour du handler Case normal, même commande CreateCase et mêmes reçus ; registre de qualification existant, projection et route BOAMP ; hook et panneau existants, lecture des Affaires de l’App. Aucun nouveau contexte, table, dépendance, capability, seuil de score ou schéma de porte.

PLAN : vrais rouges de refus/doublon → validation transactionnelle → qualification/source/reprise natives → UI confirmée et isolée → navigateur local → régressions/qualité/conservation. Autorités PF31-03, M31-01/03/07 et CT31-02/04/06 ; critères L01 du livrable métier.

## Contrats et invariants

- Source = BOAMP + identifiant d’avis dans le tenant ; les captures restent distinctes et immuables. Aucune fusion floue par titre, aucun héritage de P0 d’une capture à l’autre.
- Décisions et conversion partagent un verrou transactionnel de l’avis. Le handler contrôle la dernière décision, toutes catégories comprises, avant tout nouvel effet. Les dates serveur des nouveaux actes sont monotones ; ancien score/motif ne remplace pas une décision plus récente.
- Une Affaire active déjà liée au même avis bloque une conversion de périmètre inconnu. Un périmètre inconnu ne prouve pas la disjonction d’un nouveau périmètre : garde symétrique. Les dimensions connues et distinctes relèvent du contrat de création explicite, pas d’un lot BOAMP inventé.
- Motif P0, identifiant de qualification, observation et empreinte sont figés dans l’origine de la nouvelle Affaire. Le budget de 2000 caractères réserve le suffixe de preuve ; le texte complémentaire est borné. Une justification générique optionnelle None reste acceptée avec preuve serveur.
- Les nouvelles identités de Case incluent tenant/acteur. Les reçus de l’ancienne formule sont reconnus par leur hash canonique et rejoués sans recréer ni réécrire l’Affaire. Un rejet ultérieur n’efface pas un effet déjà confirmé ; l’adhésion courante reste exigée, y compris au replay.
- Inconnus lots/DCE/échéance absente visibles avant P0/P1 et après ouverture, avec source et action à faire. P0 ciblé ne vaut pas éligibilité DCE ou GO ; P1 reste OPEN_WITH_UNKNOWNS.
- Réponses BOAMP privées no-store. Refus/authentification/tenants gardés ; indisponibilité SQL ou reçu perdu → 503 RESULT_UNKNOWN, retry exact. Categorical reason et principal autorisé restent le contrat serveur ; les confirmations UI portent sur l’avis, la décision et les inconnus affichés.
- La projection P1 retrouve aussi l’Affaire d’une autre capture du même avis, sans reprendre sa décision P0. La navigation préfère le nouvel identifiant après lecture confirmée et rejette les réponses d’une ancienne session/propriétaire.

## Fichiers et intégration

- `backend/app/modules/opportunity/application/boamp_case_creation.py` : préservation des identités/reçus et adaptateur transactionnel BoampAwareCreateCaseHandler ; le handler Case générique n’est pas couplé à BOAMP.
- `boamp_qualification.py`, `infrastructure/boamp_qualification_repository.py` : inconnus en amont, verrou partagé, ordre des actes et lien P1 par avis, tenant filtré.
- Route `patron_boamp_opportunities.py` et bootstrap : erreurs sans faux succès, no-store et branchement du handler ; contrats d’entrée existants conservés.
- `web/src/features/opportunities/useBoampOpportunities.ts` et `BoampOpportunityPanel.tsx` : confirmation, owner scope, mutex, IDs figés, reçu exact et lecture ; `shared/types.ts` permet les IDs explicites de qualification.
- `web/src/app/App.tsx` : préférence de navigation et garde de lecture de contexte. Tests App/hook/panneau couvrent notamment l’ancienne Affaire précédemment sélectionnée.
- `backend/tests/support/boamp_local.py` : source mémoire, ingestion/scoring/persistance REPLAY et authentification JWT natives ; aucun transport externe. Scénarios processus/API/projection et comparaisons d’identité complétés.

## Preuves, reprises et incidents

Preuves privées : `~/.local/share/smartao-proofs/l01-opportunity-case-20261103/`.

- Trois rouges initiaux réels : anciennes décisions positives et nouvelle capture doublonnante. Revue indépendante : suffixe P0 tronqué, chevauchement inconnu asymétrique, puis None permis par le contrat ; rouges ciblés et corrections, historique conservé.
- Autres rouges : cache HTTP sans no-store ; callback d’ancien owner ; fuite d’affichage après refus d’accès ; navigation revenant à l’ancienne Affaire ; reçu légitime de révision 0 refusé par le client. Les contrôles sont corrigés à la frontière commune.
- Une fixture SINGLE_LOT avait une justification réservée au scope CUSTOM, corrigée sans changer le domaine. Les anciennes attentes « inconnus vides avant P1 » ont été remplacées par la présence sourcée des inconnus, conformément au résultat attendu. Les erreurs de chemins CLI/patch n’ont pas été comptées comme bugs produit.
- Natif : source mémoire → ingestion bornée → score expliqué → persistance REPLAY → lecture JWT → motif/qualification P0 → création normale → réponse perdue après commit → reçu rejoué → une seule Case lisible et inconnus préservés. Aucun HTTP BOAMP ni corpus réel.
- Test de legacy : vrai reçu de l’ancien handler/ancien CaseId relu après rejet, puis replay refusé après révocation. Deux conversions de captures concurrentes : une création, un doublon refusé ; P0 de chaque capture reste distinct.
- App ciblée : la lecture peut contenir l’ancienne Affaire en premier ; c’est l’Affaire nouvellement reçue qui est sélectionnée. Le navigateur vérifie aussi son existence dans la collection native des Affaires autorisées.

### Navigateur

Chrome DevTools MCP local déjà installé, headless et contexte isolé ; aucun autre MCP/package installé. Le composant et le hook réels appellent l’API et PostgreSQL via un adaptateur synthétique loopback ; le jeton de fixture est injecté hors navigateur. Actions humaines simulées, pas une session live.

Journal qualifié : GET observations, P0 201, GET observations, création masquée en 503 après son écriture, retry 200 avec mêmes command_id/idempotency_key, puis GET observations/Affaires. Une seule Affaire et lien source exact ; plus de bouton de création pour cet avis, lien d’ouverture existante disponible. Pas de GET entre le 503 et son retry.

Desktop observé 1280 px ; mobile émulé 393 px, largeur de layout observée 402 px. Sources REPLAY, motif et inconnus visibles, aucun dépassement par rapport au layout mesuré ; pas de promesse pixel par pixel à 393 px. Zéro cookie, localStorage, sessionStorage ou ressource externe dans la page. Captures conservées.

La première tentative a expiré ; une tentative pilotée a ensuite révélé le rejet frontend de la révision 0. Ces essais ne sont pas des succès. La recette corrigée a confirmé le reçu et la navigation desktop ; l’émulation mobile a nécessité une nouvelle lecture du composant, sans POST ni nouvelle création. Les journaux distinguent ces phases. Pas de preuve de survie d’une intention UNKNOWN à un redémarrage navigateur ou applicatif.

## Résultats et limites de qualification

- **132 tests backend ciblés passent/38,76 s**, 1 avertissement Starlette/httpx ; ingestion/scoring, qualification, persistance, refus, legacy, concurrence, origine/inconnus, routes et architecture. Pas de backend global relancé.
- **Web global : 735 réussites/4 ignorés, 92 fichiers, 178,32 s**. Après la correction finale de la borne de révision 0 : **67 ciblés réussis/2 ignorés/31,46 s** sur App, hook et panneau. Les ignorés sont antérieurs ; pas de faux PASS sur la tentative navigateur bloquée.
- Types/build verts ; lint sans nouvelle erreur, avertissement préexistant setDecisionDossier App.tsx:522 et chunk >500 kB conservés. Mypy app **708 sources vertes** ; app/tests **206 diagnostics/40 fichiers/1260 sources**, identités comparées à la baseline : aucun ajout ni retrait.
- Ruff/diff verts, tête Alembic **20261102_0147** inchangée et aucune migration. Semgrep 1.183.0 après tests : 99 règles/17 fichiers/0 finding/0 erreur, métriques désactivées, pas d’envoi de code/résultats. Impeccable detector sans finding ; captures relues, pas de certification sécurité/WCAG.
- Source/Case et journal navigateur natifs sauvegardés, IDs exacts du 503/retry200 comparés ; captures desktop/mobile relues. Première source mémoire et seule persistance d’ingestion REPLAY, aucune collecte externe.

**Frontière locale L01 livrée**, avec les limites ci-dessous. Les counts ne sont pas un achèvement général du produit.

- Pannes injectées au service/adaptateur, pas une panne TCP/PostgreSQL réelle. Le stockage des intentions frontend reste local à la durée de vie de l’App.
- Le contrat générique historique OPPORTUNITY peut contenir une référence externe non vérifiée. Ses références absentes/étrangères ne recopient aucune donnée BOAMP et ont le même comportement ; cette tranche ne transforme pas toutes les origines génériques en sources vérifiées. Le chemin BOAMP natif est, lui, filtré et validé.
- Création initiale BOAMP à scope inconnu : une Affaire active par avis ; séparation/reconciliation ultérieure de lots hors de ce parcours, aucun lot inféré.
- Score public de pertinence, pas chance de gagner, capacité, prix ou droit. Les dates et captures du jeu sont synthétiques ; aucune actualité BOAMP réelle certifiée.
- L01 général reste PARTIAL ; pas de collecte/scheduler live, de dossier entreprise réel, d’effet financier ou de GO.

Méthode : Superpowers using-superpowers, brainstorming borné/plan, TDD, revue et verification-before-completion ; ECC product-capability, security-review et verification-loop. Graphify consulté avant recherches ; OpenDesign Local catalogue/artefact/système relus, conventions CYTD Owner conservées ; Impeccable contexte/craft-floor et audit/detector. Pas de nouvelle bibliothèque/API nécessitant Context7 ; Serena sans navigation sémantique, Jev/Manus sans besoin distinct. Basic Memory miroir du plan.

WIP principal préservé, branche/HEAD inchangés ; aucun reset/clean/stash, checkout secondaire, staging, commit ou push. A1 non admis, A2 HOLD, moteurs candidats/portes inchangés, NO-GO public ; aucun effet externe.
