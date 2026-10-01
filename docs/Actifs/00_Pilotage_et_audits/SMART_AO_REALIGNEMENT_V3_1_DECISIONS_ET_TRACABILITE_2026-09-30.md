# Réalignement v3.1 — décisions, veille et traçabilité

**Date : 30 septembre 2026. Statut : décisions de conception déléguées, spécifications actives ; capacités non toutes livrées.**

## D31-01 — Pourquoi v3.1

Le propriétaire demande explicitement à Codex de produire les nouvelles autorités métier/technique, de prendre le lead et de ne plus attendre de documents. Cette délégation autorise la promotion documentaire ; elle ne signifie pas validation juridique, recette terrain ou ouverture publique. v3.1 distingue cette consolidation et la personnalisation ajoutée des candidats v3.0 transmis. Le Product Freeze v3.1 est la seule autorité produit actuelle.

Les trois autorités v2 sont archivées à contenu identique. Les cinq candidats restent dans `docs/Archive/` comme provenance de proposition, jamais une seconde liste de documents à suivre. Leurs chemins inexistants et doublons n'ont pas été recopiés dans les autorités nouvelles. Les anciens audits T0 restent des constats datés ; leur attente d'approbation est levée par la présente délégation, pas leurs limites de tests.

## D31-02 — Veille et corrections stratégiques

Sources primaires consultées le 30 septembre 2026 ; annonces publiques, aucun compte client ou benchmark vendor exécuté.

| Source | Observation étayée | Conséquence de conception |
|---|---|---|
| [Smart BTP : OS](https://www.smartbtp.ai/ordre-de-service-marche-public-btp), [CGU](https://www.smartbtp.ai/terms) | Contenu public sur OS et risques ; périmètre contractuel présenté dans les CGU plus resserré | Distinguer documentation éditoriale et fonction testée ; ne pas revendiquer exclusivité contractuelle |
| [TenderCrunch](https://tendercrunch.com/) | Extraction contractuelle confrontée aux critères propres de l'entreprise | Critères personnalisés seuls insuffisants pour se différencier |
| [KALAO : démarche](https://www.kalao-solution.fr/comment-ca-marche), [positionnement](https://www.kalao-solution.fr/) | Adaptation aux fichiers, trames et méthodes ; essai sur dossier réel annoncé | La rigidité de tous les concurrents est une hypothèse réfutée par leurs annonces ; se distinguer par adoption versionnée et chaîne longitudinale vérifiable |
| [FFB : délais cachés](https://www.ffbatiment.fr/revues-guides/ba/21-decembre-2025/marches-stop-aux-delais-de-paiement-caches) | Allongement des règlements signalé comme fragilisant la trésorerie | Modéliser le chemin des pièces/événements et inconnus de cash ; ce constat ne prouve pas une demande pour SmartAO |
| [Veille T0 élargie](../../Archive/02_Audits/T0_Realignement_V3/T0_COMPETITIVE_REAUDIT_2026-09-30.md) | TenderStrike, Spigao, Specgen, Bryte et autres : sources éditeurs et limites détaillées | Maintenir ingestion/analyse comme socle, éviter la course horizontale et les promesses de supériorité non testées |

Une nouvelle tentative d'ouverture de la page Bryte cabinets-conseil a échoué : ne pas en tirer une nouvelle preuve de personnalisation. Les comparaisons précédentes restent datées et soumises à leurs limites.

**Choix :** continuité source → condition acceptée → engagement vendu → changement réel → action/preuve, plus personnalisation métier reproductible. **Hypothèse non démontrée :** cette combinaison justifie un achat face aux concurrents. Valider sur terrain/corpus avant extension. Aucun suivi hebdomadaire autonome n'a été installé.

## D31-03 — Concentration et personnalisation

Premier profil de travail : réhabilitation en site occupé, interfaces et partenaires. Raisons : scénario transverse qui exploite C07/C08/C09 existants et révèle exclusions/logistique/passation/changement, sans reconstruire ERP ou métré. Risque : segment trop étroit ou contraintes différentes par métier ; entretiens et dossier réel conditionnent l'élargissement.

Alternative rejetée : multiplier immédiatement les packs pour tous corps d'état. Alternative rejetée : plateforme no-code avec scripts clients ; trop coûteuse à sécuriser et maintenir seul. Retenir un profil entreprise borné, publié et snapshotté, puis élargir à partir d'un besoin observé. Les invariants ne sont pas configurables.

## D31-04 — Traçabilité normative et état réel

| Exigence | Spécification | Réutilisation actuelle | État / preuve manquante |
|---|---|---|---|
| PF31-01/02 : positionnement et douleur | M31-01/08 | Affaire, DCE, acteurs | Décision de conception ; besoin utilisateur/paiement non validé |
| PF31-03 : chaîne causale | M31-02, CT31-02 | DCE sources, baseline/review, instruments et événements | PARTIAL : lien exact version/impact/condition/événement non fermé |
| PF31-04 A | M31-03, CT31-03 | DCE baseline ; Pricing ; Decision P3 ; C07/C08/C09 | À coder/qualifier dans le premier bloc après baseline |
| PF31-04 B | M31-04 | Submission P5 ; résultats P6/P7 et contrat instrumenté | PARTIAL : engagement vendu et condition repris explicitement |
| PF31-04 C | M31-05 | Avenant/remplacement/requalification/réception | PARTIAL : événement OS dédié et relation longitudinale manquent |
| PF31-05 : personnalisation | M31-06, CT31-05 | Enterprise/permissions, préférences UI éventuelles | À auditer : aucun moteur de profil versionné démontré dans T0 |
| PF31-06/07 : confidentialité/portes | CT31-04/06/09 | Security/policies, idempotence, append-only, P0–P7 | KEEP ; rejouer régressions des nouvelles relations, ne pas prétendre checkout complet vert |
| PF31-08 : impacts prudents | CT31-03/07 | PaymentCycle/obligations textuels, scénarios Pricing | ADAPT pour déclarations structurées ; moteur cash/juridique différé |
| PF31-09 : héritage | Freeze v2 archivé §9–18, §23 REC-29–45 | MIRP/HSE/assurance/capacité/settlement selon carte existante | Conservation des exigences, priorisation/report explicites ; aucune réalisation déduite |
| PF31-10 : qualification | M31-07/08, CT31-09 | G01–G52/Golden harness et tests locaux | Recettes nouvelles et benchmark vendor non exécutés |

Le détail KEEP/ADAPT/MOVE/ABSENT est dans la [carte de code T0](../../Archive/02_Audits/T0_Realignement_V3/T0_DEEP_CORE_CODE_MAP_2026-09-30.md). Aucune baseline n'a été déclarée absente par simple recherche GitHub : `ContractBaselineDeviationImpact` existe, avec un contrat plus limité que la cible. Aucun changement de bounded context n'est décidé par un nom commercial.

## D31-05 — Baseline et travail suspendu

HEAD local vérifié : `1c8ac62fcddc78d2b156f70df9f0b130910cc918`, branche `feat/ccap-cctp-risk-register-20260831`, checkout modifié et fichiers non suivis. Les changements partenaires/prix/REX et le WIP rapprochement C08 ne font pas partie du HEAD.

[Baseline T0](../../Archive/02_Audits/T0_Realignement_V3/T0_CURRENT_HEAD_BASELINE_2026-09-30.md) : frontend exact HEAD 258/258, typecheck/lint/build verts ; backend première tentative 1795 passés/135 erreurs avec DiskFull, deuxième interrompue après 140 passés. Ces résultats ne qualifient ni le WIP ni une nouvelle version produit. Pas de nouvelle suite backend complète dans le présent bloc documentaire.

Migration locale `20260930_0121_partner_offer_line_comparisons.py` et consommateurs : WIP à caractériser, pas migration certifiée appliquée ni feature fermée. Ne pas supprimer/réinitialiser le checkout. Ne pas intégrer ce travail par opportunité dans le réalignement.

## D31-06 — Ordre de reprise

Lire index → Freeze v3.1 → Master métier v3.1 → cahier technique v3.1 → plan global → carte T0 et baseline. Puis état Git/snapshot réel, audit du WIP et baseline appropriée. Premier bloc fonctionnel : source/version → applicabilité/impact déclaré → condition Patron → projection C07 → HTTP/PostgreSQL/navigateur, refus/UNKNOWN/rejeu compris. Profil métier versionné ensuite ; B puis C après A.

Pas de GitHub/push dans ce mandat. NO-GO public maintenu. Basic Memory indisponible par MCP dans cette session : la documentation locale porte la reprise, sans prétendre à une synchronisation réussie.

## D31-07 — Correction de complétude demandée par le propriétaire

La première consolidation V3.1 était trop courte pour servir de cahier intégral. Le propriétaire demande explicitement tout le contenu sous les yeux des agents, sans recours aux archives. Les trois cahiers actifs sont enrichis en place : tout le corps Freeze v2, tout le Master métier v2, tout le cahier technique v2.1, et les deltas V3 complets avant leur partie héritée déjà incluse. Personnalisation V3.1 et arbitrages actuels restent en tête. Aucun raccourcissement des détails reportés n'est une suppression d'exigence.

La conservation vérifiable est **textuelle**, avec titres transformés uniquement pour donner des identifiants uniques ; ce n'est pas une preuve d'absence de toute contradiction sémantique. Les différences connues (autorité, priorité, ownership, règles juridiques, validation externe, commercialisation) sont traitées par la table de consolidation en tête de chaque cahier. Tout conflit supplémentaire découvert pendant une tranche doit être documenté, jamais résolu par omission silencieuse.

Manifest `SMART_AO_CDC_INTEGRAL_V3_1_COVERAGE_2026-09-30.json` : cinq sources, 9 241 lignes intégrées, 854 chapitres. Test compare chaque ligne et titre retenus avec les sources et contrôle leur empreinte ; les frontières V3 éliminent uniquement la seconde copie du même héritage v2, qui est intégré depuis l'autorité v2 promue. Le contenu complet est donc localement accessible dans les cahiers actifs. L'ancien checkpoint reste un constat immuable avant cette correction.

## D31-08 — Audit checkout et ordre des dépendances

Le [rapport](V3_1/CHECKOUT_COVERAGE_AUDIT.md) et la matrice détaillent 45 familles et indexent 899 titres de section. Les références/conditions Decision et calculs financiers entiers existent déjà : les enrichir, pas les remplacer. La configuration métier publiée et son snapshot doivent précéder les nouveaux contextes qui en dépendent : A0 → S0 → M0 → A1 → M1 → B1 → C1. M0 est le socle version/adoption, M1 son éditeur utilisable ; aucun deuxième système.

Constats reproduits : import modèle C08 NameError ; tête fichiers Alembic0121 versus runtime0120, test architecture rouge. L'audit ne corrige pas ces fichiers production. Domaine/architecture297 passés/1 échec ; frontend285/285. Full backend PostgreSQL reste non qualifié. La couverture des titres est un index de périmètre, jamais preuve atomique de chaque exigence ou validation externe. Les CDC complets sont conservés ; arbitrages monétaires/ordre de livraison sont explicités dans le cadrage technique dérivé.


## D31-09 — Clôture ciblée A0/S0/M0 et ordre A1 (1 octobre 2026)

A0 est clos pour les blocs touchés : C08 imports et route/model wiring, tête supportée 0122, upgrade de migration complète sur base éphémère et tests PostgreSQL ciblés. La tête locale n’est pas une qualification de toute la suite backend. S0 valide des références tenant/Affaire vers DCE Requirement, preuve baseline exacte par révision et profil de méthode adopté/hash ; l’historique de strings non résolues reste UNKNOWN. M0 publie une configuration entreprise V1 bornée, append-only/hachée et explicitement adoptée par Affaire ; Decision peut la vérifier lors du gel de contexte. L'éditeur UI M1 est encore absent.

Résultats : 9 tests DB ciblés M0/C08 verts ; 338 tests domaine/architecture/ops/API ciblés verts ; typecheck et Ruff verts. Le contrôle Alembic ne trouve pas d'écart nouveau dans les tables C08/profil/adoption. Il reste des écarts de métadonnées historiques ailleurs, dont index/noms de contraintes de la baseline ancienne. Le NO-GO public est maintenu ; rien n’est commité ou poussé. Le snapshot A0/M0 est local et inclut les fichiers non suivis listés dans `V3_1/A0_M0_SOURCE_SNAPSHOT_2026-10-01.json`.

A1 est la prochaine tranche : prouver dans C07 le lien entre une exigence DCE et la preuve baseline, un impact déclaré et une condition Patron, avec le profil exact cité. M1 UI vient après A1. A1 garde UNKNOWN/refus/rejeu, pas de promotion P3 ni conclusion juridique automatique.
