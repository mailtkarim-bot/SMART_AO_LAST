# L07 — capacités datées et trésorerie déclarée : reprise sourcée

Qualification locale avec limites ; le plan global reste la seule autorité de statut. L07 général demeure PARTIAL.

AS-IS : registres natifs append-only, API et interfaces de capacité datée et trésorerie existent. Les sources remplacées invalident les calculs natifs ; l’interface doit relire ce nouveau contexte et demander un acte humain frais.

RISQUES : données anciennes visibles sous une reprise DCE incertaine, confirmation conservée après nouvelle source, trésorerie sans geste de relecture des sources, montant/capacité prévus présentés comme garantis.

POINTS D’INSERTION : CapacityPanel, CashSchedulePanel et leurs appels App ; réutilisation des services natifs et contrats existants, sans migration ou porte nouvelle.

PLAN MINIMAL :

- [x] Observer les rouges UI : suspension des deux panneaux et retrait du consentement après relecture source.
- [x] Corriger les panneaux avec le style existant confirmé par OpenDesign Local Codex ; permettre la relecture des sources de trésorerie.
- [x] Prouver ensemble capacité/cash V1, remplacement, anciens actes refusés, nouvelle révision humaine et historique conservé.
- [x] Vérifier tests, types, lint, build, revue et sécurité ; sauvegarder le WIP, mettre à jour le plan et son miroir.

TESTS À AJOUTER : absence de lecture/écriture sous suspension, réponse tardive masquée, reprise UNKNOWN exacte, source changée retirant l’ancien consentement, relecture du catalogue et des cumuls, nouveau contexte humain sans transfert des accords. Régressions natives tenant/rôle/MFA, concurrence, idempotence, inconnus et append-only à relancer.

Les 747 empreintes du WIP L06 sont identiques avant édition. Branche et HEAD attendus vérifiés ; aucun nouveau checkout ni opération Git destructive. Preuves locales privées : `~/.local/share/smartao-proofs/l07-capacity-cash-20261104/`.

## Fonction livrée et fichiers

`CapacityPanel` et `CashSchedulePanel` suspendent leurs lectures et formulaires pendant la reprise DCE incertaine. Les stores d’intention existants restent dans App : cette suspension ne fabrique ni nouveau retry ni accord. Leurs clés de lecture suivent également la version et la disponibilité du DCE de l’Affaire.

Une relecture de capacité retire la confirmation ; si l’empreinte du contexte a changé, les anciennes saisies et la justification sont retirées du formulaire. Le calcul/historique natif reste conservé. La trésorerie offre désormais « Relire l’échéancier et ses sources » ; une nouvelle empreinte réinitialise les consentements de déclaration **et d’annulation**. Le lecteur reste déclaratif, sans convertir un flux ou une capacité en garantie.

Les réponses capacité réussies GET/POST, y compris replay, portent `Cache-Control: no-store`. Les refus, autorisations et modèles de calcul restent ceux des services natifs.

Sept fichiers logiciels : `web/src/features/capacity/CapacityPanel.tsx`, son test, `web/src/features/pricing/CashSchedulePanel.tsx`, son test, `web/src/app/App.tsx`, `backend/app/interfaces/http/routes/patron_capacity.py` et `backend/tests/api/test_l07_capacity_cash_rectification.py`. Aucun schéma, migration, dépendance, solveur, calcul financier ou porte modifié.

## Parcours natif commun

La nouvelle recette reçoit de vrais originaux synthétiques via staging/admission/extraction, rattache V1 à une seule Affaire et utilise un JWT Patron frais. Elle enregistre séparément besoins/disponibilité datés et flux de trésorerie, avec sources et justification ; chaque rejeu conserve un effet unique. OPTIMAL reste une proposition, couverture UNKNOWN et ressource non réservée ; le cumul initial déclaré vaut -100 unités mineures.

Un vrai réimport V2 et son rattachement explicite rendent les actes V1 à revoir : plan courant masqué et cumuls courants indisponibles. L’ancien reçu peut être rejoué historiquement sans nouvel effet ; un nouvel acte portant l’ancienne empreinte est refusé 409. Les nouvelles révisions sans confirmation sont refusées 422, puis les actes humains V2 sont enregistrés/rejoués. La quantité de besoin reste inconnue ; montant/date du flux restent inconnus et son cumul n’est pas zéro. Anciennes sources, entrées, justification et actes demeurent dans l’historique.

## Preuves exécutées

- TDD : quatre rouges UI initiaux (suspension des deux panneaux, capacité relue, geste de relecture cash), puis rouge consentement d’annulation signalé par revue. Le premier essai natif a reproduit l’absence de no-store sur GET capacité, corrigée avant le succès natif. Un sélecteur Web devenu ambigu entre déclaration et annulation a été borné au formulaire ; aucun contrôle métier retiré.
- Web global final sur gel logiciel : 780 réussites, 4 ignorés, 92 fichiers, 397,46 s, exit0. Sept SHA logiciels recontrôlés après la suite.
- Web ciblé final : 25 réussites, 4 fichiers, 7,40 s, couvrant panneaux et projections d’analyse capacité/cash. Les tests existants de retry UNKNOWN, droits, réponses tardives et formulaires restent exécutés.
- Recette native commune : 1 réussite, 22,42 s. Campagne backend élargie finale : 44 réussites, 87,63 s ; calculs/commandes/erreurs HTTP, capacité révisionnée et cash couvrent tenant étranger, Collaborateur, MFA, concurrence, idempotence, append-only, sources remplacées et montants/dates inconnus.
- Types Web, lint et build exécutés ; seuls avertissements préexistants `setDecisionDossier` dans App et chunk >500 kB. Mypy application : 708 fichiers verts ; application/tests : 206 diagnostics dans 40 fichiers sur 1268 sources, identiques aux diagnostics L06 après normalisation des numéros de ligne. Ruff et format des deux fichiers Python verts ; tête Alembic inchangée `20261102_0147`, fixtures upgrade/downgrade jusqu’à base.
- Semgrep 1.183.0, `p/security-audit`, métriques désactivées : 99 règles, 7 fichiers, 0 finding, 0 erreur. Analyse locale, aucun résultat transmis ; pas de certification globale. Scan borné des lignes ajoutées : aucun secret reconnu. Diff du seul delta L07 relu, sept SHA logiciels figés et recontrôlés.
- Impeccable detector : `[]`. OpenDesign Local Codex : catalogue courant et artefact SMART AO C08 existant consultés ; composants/styles du dépôt conservés, système Linear uniquement référence complémentaire, autorité Owner/CYTD inchangée. Aucun nouveau prototype ou style inventé.
- Chrome DevTools Local installé : vrais composants sur projections natives V1/V2 enregistrées, API **simulée en lecture**, suspension/reprise et relecture exercées. Captures capacité puis cash inspectées à 1280 et 393 px : pas de débordement global, manques et historiques présents, cases de consentement cash non cochées, cookies/stockages vides et aucune ressource externe. La table capacité utilise son défilement horizontal existant ; ce contrôle ne démontre pas tous les gestes tactiles ou WCAG.
- Limites de harnais conservées : attente initiale d’un texte absent (« Quantité »), puis chargement JSON de fixture restant en attente ; corrigés en attendant un état réel et en intégrant la projection au module privé. Une tentative de diagnostic avait un argument de script non sérialisable ; aucune de ces erreurs d’outil n’est un échec produit ou une preuve navigateur. Le run final porte `L07_BROWSER_PASS` ; aucune mutation métier effectuée par ce navigateur de relecture.
- Base jetable : zéro table métier et zéro révision Alembic, conteneur exact `e8fcb4d6bf2059cd33b0dcaf4ed90fda065b02a395845a68a9d8042a16506c25`, sans montage persistant, arrêté/supprimé. Clients navigateur et preview dédiée fermés ; services préexistants conservés.

## Invariants, limites et reports

FINANCIAL_PRIVATE, droits Patron/Collaborateur, MFA, tenant scope, optimistic concurrency, identifiants de replay, append-only, sources et UNKNOWN restent préservés. Le no-store ajouté concerne les réponses capacité réussies ; aucune nouvelle prétention de cache global des erreurs.

Sources de planning et soldes/flux manuels restent des références déclarées : leur authenticité et leur validité externe ne sont pas démontrées. Le scanner de fixture est synthétique. Le remplacement DCE est réellement éprouvé ; la détection continue de changements externes n’est pas ajoutée. Une source externe peut nécessiter un geste de relecture. Les stores d’intention sont locaux en RAM, sans reprise durable après rechargement complet.

Pas de capacité garantie/réservation, financement ou cash certain, calcul juridique, conversion de devise ou agrégation portefeuille. Aucun lien automatique capacité→coût/flux ajouté. Les règles de coûts/charges inter-Affaires demeurent déclaratives ; les moteurs/calendriers reportés restent reportés. Aucun candidat activé, gate promu, effet externe, dépôt, commit, push ou GO public.

Outils réellement appliqués : Graphify avant exploration ; Serena initialisée/activée et navigation symbolique ; Superpowers cadrage, plan, TDD, revue indépendante en lecture seule et vérification ; ECC product-capability et verification-loop ; OpenDesign Local Codex, Impeccable et Chrome DevTools Local. Pas de Playwright MCP disponible, ni preuve Playwright. Context7 non sollicité faute de question de bibliothèque nouvelle ; Jev/Manus sans gain sur ce périmètre borné. Basic Memory reste le miroir du plan, synchronisé après consolidation finale.
