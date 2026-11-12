# L07 — capacité datée par Affaire

## Cadrage et plan d'implémentation

AS-IS : le module `optimization` affecte des unités entières, sans période. Son registre de calcul conserve les snapshots et leurs hashes. Le contrat historique ne doit pas être réinterprété comme un calendrier.

RISQUES : double comptage d'une équipe, confusion entre disponibilité absente et nulle, affectation hors période/compétence, mélange tenant/Affaire, réutilisation après rectificatif, résultat pris pour une réservation ou un accord Patron.

POINTS D'INSERTION : adaptateur OR-Tools du module optimization; commandes, registre et projection natifs; API et parcours Affaire existants. Aucun prix, calendrier de jours ouvrés ou engagement déduit.

PLAN MINIMAL :

1. Calcul daté séparé, sources déclarées et ressources nommées/génériques explicites; intervalles journaliers [début, fin exclue), capacité entière constante par disponibilité. Données manquantes UNKNOWN. Aucun fractionnement implicite d'un besoin.
2. Saisie révisionnée append-only et calcul par Affaire avec concurrence, retry, permissions et provenance; invalidation du résultat après changement des entrées ou du contexte DCE.
3. Saisie/relecture dans le parcours existant après consultation OpenDesign Local et Impeccable; qualification navigateur synthétique.
4. Tests, revue et contrôles projet; clôture uniquement après preuve du parcours complet, mise à jour du plan et miroir Basic Memory.

TESTS À AJOUTER : interventions successives/simultanées, disponibilité partielle/nulle/absente, ressources incompatibles ou nommées, limites, déterminisme; source obsolète, tenant/rôle/MFA, retry/concurrence; masquage hors contexte et UNKNOWN navigateur.

## Journal

- 23/10 : checkout principal/HEAD30f2693 et WIP vérifiés; Graphify consulté, instructions projet et chapitres actifs lus. Documentation OR-Tools consultée via Context7 (intervalles optionnels et contrainte cumulative). Premier rouge TDD : module daté absent, erreur de collecte attendue avant implémentation.
- Travail en cours : ce dossier ne qualifie pas encore un parcours utilisable et ne clôture pas L07. Aucun changement de porte, réservation, prix ou moteur candidat autorisé.

## Fonction implémentée et limites du modèle

- `optimization/application/dated_capacity.py` : besoins indivisibles et disponibilités datées, type exact et ressource nommée facultative; OR-Tools CP-SAT installé, cumul des unités sur les périodes et budget solveur5s/1worker. Maximum100besoins et100disponibilités, unités entières≤10000. Les frontières temporelles évitent une expansion non bornée en jours.
- `dated_commands.py` : contrat fermé, sources référence/révision/repère, dates absentes distinctes des dates invalides, capacité nulle distincte d'inconnue, confirmation/justification humaines.
- `optimization/infrastructure/dated_service.py` : snapshots dans `optimization_runs` existant, SHA-256 canonique des entrées, version OR-Tools, contexte DCE/portée, révision optimiste et verrou Affaire. Aucun nouveau schéma : Alembic reste0141. Le dispatcher conserve les reçus/idempotences; les triggers existants refusent UPDATE/DELETE.
- Route Patron `GET/POST /api/v1/patron/cases/{case_id}/capacity`, composition native et panneau Affaire `CapacityPanel.tsx`. Patron/MFA/tenant contrôlés côté serveur; contexte de lecture masqué immédiatement côté client. Intention UNKNOWN conservée en mémoire de l'App, sans stockage navigateur ni changement d'IDs au retry.
- La projection économique globale conserve UNKNOWN pour ce profil : OPTIMAL signifie seulement faisabilité des entrées déclarées. Aucun prix, réservation de ressource, confirmation, porte ou moteur candidat modifié.

Une disponibilité représente une ressource/équipe distincte sur une seule période continue à capacité constante. Les congés, autres chantiers, trajets et autres charges doivent être retranchés explicitement par le déclarant; pas de calendrier ouvré, déplacement, découpage de besoin ou réservation inter-Affaires calculés implicitement. Les diagnostics agrégés signalent des surcharges; leur absence n'explique pas tous les refus de compatibilité/ressource nommée. Les sources sont HUMAN_DECLARED, pas des documents automatiquement admis ni des octets externes revalidés. Une nouvelle saisie est un nouveau snapshot, pas une synchronisation d'un planning externe. L07 complet, dont échéancier cash et portefeuille différé, reste PARTIAL.

## Preuves intermédiaires (historiques)

- TDD : module/contrat/route initialement absents;3rouges de validation typée; régression économique PROVEN→UNKNOWN; dates inversées et422 initial bloquaient le formulaire, reproduits puis corrigés.
-137tests ciblés calculs/anciennes persistances/synthèse/architecture verts;8tests SQL/API finaux, dont deux révisions concurrentes, tenant/rôle/MFA, révision/contexte et append-only. Recouvrement : ne pas additionner ces campagnes.
-6tests UI candidat verts;52tests App/panneau et2ignorés historiques après mise à jour du mock API et libellé de justification spécifique.
- Recette Chromium isolé via Chrome DevTools MCP (aucun Playwright MCP) :11assertions complètes sur fixture neuve. Deux besoins successifs→OPTIMAL/même équipe, chevauchement→INFEASIBLE/4unités pour2disponibles, changement de portée→historique, entrée absente→UNKNOWN. Trois calculs persistés malgré perte de reçu synthétique;POST natifs201/403/200/201/201, premiers3corps identiques et aucunGET entre ces retries. Sans cookie/Authorization/stockage dans le navigateur; réseau loopback uniquement. Backend appelé in-process sur PostgreSQL synthétique via socket privé, aucun backend live.
- Captures mobile390etdesktop1440 inspectées; largeur mobile390pourviewport390 après reprise des styles existants et retour à la ligne des hashes. Sources dans tableaux à défilement horizontal annoncé. Audit WCAG exhaustif et refonte visuelle globale hors preuve.
- OpenDesign Local : catalogue courant et artefact SMART AO existant consultés; conventions incumbent/CYTD conservées, aucun Cloud/BYOK/génération parallèle. Impeccable context/craft-floor/audit ciblé/detect : aucun finding mécanique. Revue indépendante : blocage422 corrigé; contre-revue sans autre blocage concret.
- Ruff/format, mypy663fichiers, types/lint/build Web verts; avertissement bundle>500kB conservé. Semgrep1.179.0/225règles/10fichiers explicitement vérifiés/0finding/0erreur; secrets0.
- Suites Web parallèles historiques non qualifiantes : un mock App absent, puis19échecs sous saturation mémoire/swap; aucune augmentation de délais. Rejeu séquentiel final requis. Première globale backend interrompue volontairement pour figer le dernier traitement HTTP des erreurs incertaines; aucun PASS global final déduit.

Preuves privées : `~/.local/share/smartao-proofs/l07-capacity-20261023/`. Les erreurs historiques de recette sont conservées : contrôle de portée initial identique à la fixture et comptage DOM incluant l'historique masqué; scénario complet rejoué sur fixture neuve après correction. Adaptateur, Chromium et serveur de recette arrêtés. WIP principal préservé, aucun commit/push/live/VPS/déploiement/P3/admission/activation/GO public.


## Gel final achevé et nettoyage

La session97653 est achevée, exit0; ne pas la relancer. Backend complet3887réussites/0ignoré/3avertissements Starlette/Pydantic/1025,59s. Web complet séquentiel644réussites/4ignorés préexistants/76fichiers/134,32s/exit0.33tests L07 finaux verts;16SHA de code gelés et inchangés. Aucun changement de schéma : head Alembic20261023_0141.

Dernier garde : deux rouges HTTP422≠503 reproduits avant correction, puis5cas verts; exécution en cours ou persistance incertaine renvoie503 et conserve le retry identique. Le422 de validation FastAPI préalable autorise la correction seulement avant tout résultat incertain. Le scénario navigateur précède ce dernier changement de classification, couvert séparément par ces tests HTTP et par la régression UI503→422 au retry; aucun nouveau comportement nominal ou style non vérifié déduit.

Semgrep final de la route modifiée :225règles/0finding/0erreur;10fichiers du scan principal tous explicitement vérifiés malgré l’avertissement générique sur les exclusions. Secrets finaux0. Contrats documentaires4/4; lint/types/build et mypy663verts, warning de bundle préexistant conservé.

`cleanup.json` : quatre bases `smartao_l07`, `smartao_l07_global`, `smartao_l07_browser`, `smartao_l07_final` vérifiées Alembic0; seul conteneur dédié arrêté et revenu à son état initial exited. Réseau none/aucunTCP; ACLUID70 retirée, socket700. Chromium, Vite et adaptateur privés arrêtés. Les campagnes intermédiaires restent historiques/non qualifiantes; seuls les journaux finaux soutiennent la clôture locale.

Méthode appliquée : Superpowers using-superpowers/brainstorming/writing-plans/test-driven-development/requesting-code-review/verification-before-completion; ECC product-capability/verification-loop. Graphify consulté avant exploration, Serena activé, Context7 pour OR-Tools; OpenDesign Local et Impeccable pour le panneau existant. Jev/Manus non nécessaires pour cette implémentation locale déterministe; aucune délégation externe ni validation humaine inférée.


## Suite de codage

Le plan global seul porte le statut et la prochaine tranche : L05 — livrer la carte d’engagement d’une Affaire depuis les points critiques du dossier : relier impacts, hypothèses, actions, responsables et preuves à leurs sources, puis qualifier la décision Patron motivée et son historique sans lever de porte implicitement.
L07 général reste PARTIAL; A1 non admis, A2 générique HOLD et NO-GO public maintenus. Aucun live/corpus réel/VPS/déploiement/P3/admission/activation de candidat/commit/push.
