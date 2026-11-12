# L11 — état source des actions et invalidation des comparaisons — 2 novembre 2026

**Verdict : invalidation source et relecture qualifiées localement. L11 général PARTIAL.** Aucun CURRENT d’action fabriqué sans relecture binaire.

Plan seul statut, checkout principal/branche/HEAD inchangés,670empreintes antérieures conservées. Aucun reset/clean/stash, checkout, stage, commit ou push.

AS-IS : le lecteur forçait toutes les actions à UNKNOWN; les revues de clôture pouvaient donc garder une comparaison apparemment courante après invalidation du point d'origine.
Risques : fabriquer CURRENT sans lire les octets, transférer un consentement, masquer une dépendance périmée, altérer les actes/montants historiques.
Insertion minimale : réutilisation du validateur L10 dans le lecteur de clôture, sans stockage binaire injecté ou porte supplémentaire; relecture des comparaisons capturées, champs dérivés seulement.

- [x] Deux rouges PostgreSQL : DCE à revoir et ancienne action après requalification restaient UNKNOWN. Lire les états L10, conserver UNKNOWN si seuls octets non relus/contrat non lié empêchent la validation, signaler les invalidations avérées REVIEW_REQUIRED.
- [x] Propager les sources manquantes, périmées ou d'empreinte différente aux actes/réserves qui les comparent, y compris dépendances en chaîne. Conserver JSON des revues, identifiants et consentements historiques.
- [x] Qualifier remplacement sans changement DCE, rôle/tenant, paiement déclaré/UNKNOWN, append-only et vues/hash; tests ciblés, revue, types/lint/Semgrep/diff.
- [x] Sauvegardes, nettoyage, plan/index/registre et miroir Basic Memory relu après preuve.

Superpowers TDD/systematic-debugging et ECC verification-loop/security-review. Graphify consulté. Aucun travail UI, aucune nouvelle bibliothèque, migration ou contrat d'écriture. La source courante complète n'est pas démontrée sans relecture binaire : UNKNOWN conservé, aucune réception externe, exécution, paiement bancaire, effet juridique ou GO public.


## Fonction livrée et preuves

Le lecteur de clôture relit les événements/revues du même tenant/Affaire et sélectionne la dernière révision par événement. Une action d'une ancienne revue ou d'une source invalidée est REVIEW_REQUIRED. Le validateur L10 est réutilisé; faute de stockage binaire dans ce chemin, les seuls motifs d'octets non relus/vue non rapprochable/contrat non lié conservent UNKNOWN. Aucune source d'action n'est promue CURRENT par supposition. Le contrat déclaré du changement est vérifié indépendamment : l'absence d'octets ne doit pas masquer son remplacement, même si le contrat sélectionné dans la passation est un autre instrument.

Les comparaisons capturées sont relues contre les références et empreintes actuelles. Source absente, périmée ou différente : contexte de l'acte/réserve à revoir. Propagation jusqu'au point fixe, y compris dépendances en chaîne et origine de réception d'une obligation. Les JSON de revue, identifiants, consentements, transitions et montants historiques restent inchangés. Les faits financiers ne deviennent pas dépendants d'une action sans relation déclarée; aucun solde/paiement externe n'est déduit.

Deux rouges PostgreSQL ont reproduit DCE à revoir et ancienne action après requalification restant UNKNOWN; correctifs puis verts. Un rouge pur a prouvé la propagation aux comparaisons. Le contrat distinct remplacé a ensuite un vrai rouge UNKNOWNvsREVIEW_REQUIRED; les premiers essais avec import de fixture manquant et remplacement non déclaré AMENDMENT sont des erreurs de fixture conservées, pas des bugs produit ni des succès. Aucune contrainte n'a été assouplie.

La revue indépendante a trouvé une cascade manquante (P1) : réserve liée par origin_reception_act_id mais sans comparaison explicite. Rouge dédié puis correction du lien d'origine. Scénario SQL : réception liée à une action, réserve avec levée historiquement déclarée COMPLETED, nouvelle passation de même offre sans changer Case/DCE/contrats. L'acte indépendant reste CURRENT; acte dépendant et réserve deviennent REVIEW_REQUIRED, origin_context_state est actualisé. La déclaration COMPLETED reste dans l'historique mais la réserve revient dans open_obligation_ids; une sortie avec vue fraîche et sans acquittement est refusée OPEN_OBLIGATIONS_REQUIRE_ACKNOWLEDGEMENT. Aucun ancien consentement transféré ou réécrit. Contre-revue statique : P1 corrigé, aucun nouveau point bloquant; aucun test/DB exécuté par le relecteur.

## Campagnes exécutées (chevauchements, pas de total additionné)

- Tests SQL/purs complets :30réussites,1warning,58,12s/exit0; inclut requalification/tenant/droits du suivi, clôture/paiements, conservation des données, absence de promotion UNKNOWN et propagation multi-niveaux. Rejeu SQL ciblé avec export avant/après :1/17,13s; ajout du refus de sortie puis rejeu ciblé1/14,41s/exit0. Campagne précédente28/53,65s et tests intermédiaires sont datés, non substitués.
- Chaîne native V2 Markdown jusqu'à réception/réserve/paiements :1réussite/214,45s/exit0 au cours du raccordement, avant dernier resserrement de la cascade d'origine; ne pas l'attribuer silencieusement au dernier code. Le dernier refus/cascade est qualifié par le SQL ciblé et les purs, sans rejouer une chaîne entière sans besoin. DOCX/binaire inchangés non rejoués.
- Source PATRON sécurisée et ancienne réception conservée : test UI rouge car WITH_RESERVATIONS masquait context_state; ajout d'une ligne État source distincte dans SourceRow existant.7Web verts, TypeScript/lint/build exécutés; warning App.tsx:517 antérieur et chunk>500kB, aucun seuil relevé. Aucun nouveau formulaire/route/champ API, style ou palette.
- Mypy703sources applicatives sans diagnostic; app/tests206diagnostics40fichiers/1247sources inchangés, aucune nouvelle dette/ignore. Ruff/check/format3Python verts; Alembic unique20261027_0146 inchangé, aucune migration ajoutée. Fixtures exercent upgrade/head/downgrade et refus non vide/verrous existants.
- Semgrep p/security-audit,5sources,0finding/0erreur (version/règles dans reçu), métriques désactivées, analyse locale; motifs de secrets stricts0candidat. Contrôles bornés, pas certification.
- Chrome DevTools Local : CaseClosurePanel existant avec dossiers SQL synthétiques enregistrés, API de lecture simulée, pas de POST bancaire/métier depuis navigateur. Avant/après même Case/DCE/contrats, hash dossier change, réception WITH_RESERVATIONS et source REVIEW_REQUIRED simultanément visibles; réserve COMPLETED mais à revoir et réouverte visible.1280/393px sans débordement; aucun cookie/token/stockage ou trafic externe. Pas Playwright/API live/certification WCAG.

OpenDesign local catalogue/artefact C08/système linear-app consultés avant édition UI, Owner CYTD/styles hérités préservés; Impeccable contexte de session/craft-floor/detector0, aucun Cloud/BYOK/prototype/hook nouveau. Superpowers TDD/systematic-debugging/executing-plans et ECC security-review/verification-loop; Graphify consulté. Pas de navigation Serena sémantique nécessaire, ni Context7/JeV/Manus pour nouveaux contrats externes inexistants. Basic Memory reste miroir du plan, pas autorité d'état.

## Fichiers et limites

backend/app/modules/pricing/infrastructure/case_closure_reader.py : état des actions et propagation dérivée. backend/tests/db/test_operational_change_workflow.py et nouveau backend/tests/application/test_closure_action_sources.py : régressions source/contrat/réserve/consentement. web/src/features/decision/CaseClosurePanel.tsx et son test : visibilité distincte de l'état source. Présent bilan/plan/index/REGRESSION.md : preuves et suite.

UNKNOWN demeure lorsque seule la relecture binaire permettrait une preuve courante; aucun CURRENT d'action prétendu. CURRENT d'un acte indépendant décrit son contexte référentiel, pas une certification binaire/juridique. La requalification humaine après invalidation et le non-transfert d'anciens montants L11 restent à qualifier plus largement; aucune exécution ou réception externe n'est prouvée. L11 général PARTIAL; réserves/accords ne sont pas effacés, montants déclarés ne deviennent pas paiements bancaires ou solde établi.

Preuves privées ~/.local/share/smartao-proofs/l11-action-sources-20261102/, replacement/before.json et after.json; empreintes WIP/delta relues, base Git vérifiée. Deux bases jetables vides après tests, seul conteneur smartao-l11-sources-20261102 et preview5200 retirés; daemon OpenDesign existant préservé. Plan/index/registre et miroir Basic Memory synchronisés puis relus. Aucun reset/clean/stash, checkout, stage/commit/push/live/corpus réel/VPS/déploiement/P3réel/signature réelle/dépôt externe/notification/exécution réelle/activation/GOpublic.

Prochaine étape : L11 — qualifier la requalification humaine des actes et réserves après invalidation, avec nouvelles sources et consentements explicites, sans réécriture de l’historique ni effet externe.
