# Audit du checkout contre les cahiers V3.1 intégraux

**Statut : audit de couverture fonctionnelle et dépendances exécuté ; aucune nouvelle fonctionnalité implémentée.**
**Horodatage UTC :** 2026-09-30T23:36:02.599098+00:00  
**HEAD :** `1c8ac62fcddc78d2b156f70df9f0b130910cc918` — branche `feat/ccap-cctp-risk-register-20260831`.  
**Snapshot source :** `396b78e74db0f2ef87c44139e9d349475a80c6f043800de218ee70784f1afb1d` ; 1265 fichiers, dont 64 non suivis dans le périmètre sélectionné. Checkout local modifié, pas équivalent au HEAD distant.

## AS-IS

Le socle n'est pas à reconstruire : identity/MFA, Affaire/DCE, sources/exigences, décisions et conditions, prix/scénarios, dépôt humain, contrat/avenant/réception, post-réception et REX sont réellement représentés. Le checkout contient des ajouts locaux C08/C09 et d'applicabilité REX. Le point faible V3.1 est la connexion entre ces objets et la méthode d'entreprise utilisée à une date donnée, pas leur absence générale.

[Snapshot et inventaire des classes/champs](CHECKOUT_SOURCE_SNAPSHOT.json), [matrice fonctionnelle JSON](FUNCTIONAL_CODE_TEST_MATRIX.json), [CSV](FUNCTIONAL_CODE_TEST_MATRIX.csv) et [index de toutes les sections](SPEC_SECTION_COVERAGE_INDEX.csv) rendent les constats reprenables. Aucun secret/.env/cache ou contenu utilisateur n'est inclus dans le snapshot.

## Méthode et limite de complétude

Les trois CDC complets sont couverts par **899 titres de section indexés**, dont les 854 titres intégrés contrôlés dans le bloc documentaire précédent. Les titres sont rattachés à **45 familles fonctionnelles** avec code, tests repérés, surfaces et écart. Les 152 titres ambigus ou administratifs ont reçu une disposition de périmètre explicite.

Cette couverture n'est **pas** une déclaration que chaque phrase est une exigence atomique testée. Un rapprochement thématique automatisé aide à retrouver les sections ; il ne certifie ni équivalence sémantique ni réalisation. Les familles ont des jugements d'audit, et les critères détaillés se traduisent en tests lors de leur tranche. Les validations juridiques/assurance/HSE et la preuve sur corpus réel restent externes/non acquises. Aucun pourcentage d'achèvement logiciel n'est calculé à partir des titres, fichiers ou tests.

## Constats vérifiés et risques

| ID | Constat actuel | Preuve | Conséquence |
|---|---|---|---|
| AUD-01 | WIP rapprochement C08 non importable | Import isolé `app.modules.pricing.infrastructure.models.partner_offer_line_comparison` : **NameError `_source_field_constraints`**. Usage dans la classe ligne140 ; définition après les classes ligne160 | Blocage de collecte des tests DB de cette feature ; réparer avant de la déclarer intégrée |
| AUD-02 | Tête migration en fichiers différente du contrat runtime | `alembic heads` : `20260930_0121`, `EXPECTED_ALEMBIC_HEAD` : `20260930_0120` ; test architecture échoue | Bloque une baseline verte ; aucune conclusion sur la tête réellement appliquée en DB sans lecture DB |
| AUD-03 | Routes/handlers/modèle0121 présents mais non enregistrés | Absence de `line_comparison` dans bootstrap, imports modèles et env Alembic, alors que `scope_review` est enregistré | La présence des fichiers n'est pas exposition HTTP fonctionnelle. Choisir intégration maîtrisée du WIP, sans extension de scope |
| AUD-04 | Conditions Patron et références typées déjà existantes | `DecisionConditionRecord`, `DecisionContextReferenceRecord`, lifecycle/repositories/finalize | Réutiliser : références validées CASE/DCE_VERSION/DCE_REQUIREMENT/DECISION_RISK/PRICING_SCENARIO. Aucun type baseline/contrat/profil métier accepté actuellement |
| AUD-05 | Baseline/contrat/impact ne forment pas une chaîne intégrale | `ContractBaselineDeviationImpactRecord` conserve UUID observation sans FK document et impact libre ; instrument signé possède source refs string | S0 : relation source typée/résolue, UNKNOWN si non résolue, pas de table source en double |
| AUD-06 | Configuration métier versionnée d'Affaire non établie | EnterpriseCompany/CapabilityVersion et WatchProfile ont d'autres responsabilités ; aucun cycle publication/adoption/snapshot métier trouvé dans modèles/commandes/UI inspectés | **M0 doit précéder les nouvelles décisions A1 qui en dépendent**, puis M1 éditeur complet ; ancien historique sans profil reste UNKNOWN |
| AUD-07 | Montants exacts déjà calculés en unités mineures entières | `cost_basis.py`, `scenario.py`, `FinancialReportSnapshotRecord.ruleset_version` | Ne pas imposer Decimal/rewrite aux calculs int existants. Rechercher réutilisation des règles financières ; ruleset_version ≠ profil métier intégral |
| AUD-08 | Capacité possède service OR-Tools et persistence de runs | `CaseCapacityPlanningService`, `OptimizationRunRecord`, tests capacité et projection CaseResolution | Ne pas créer un solveur neuf ; intégration capacité/engagement/portefeuille reste partielle |
| AUD-09 | UI condition/contexte exige du JSON technique | `PatronDecisionPanel.tsx` : `referencesJson`, `conditionsJson`, parse JSON au submit | Backend réutilisable ; formulaire métier guidé et source sélectionnée nécessaires dans A1 pour une preuve utilisable |
| AUD-10 | Payment qualification reste prudente et textuelle | `PaymentPostReceptionCycleRecord.cash_assumption/post_reception_cost_note` ; revue/qualification/collecte réelles | Pas de cash moteur/settlement complet ; ne pas recoder une nouvelle revue équivalente ; pas MOVE hors Pricing sans ADR |
| AUD-11 | Droits/échéances/sanctions : actes/signalements ≠ calcul juridique | Actes RIGHTS_PRESERVATION, sanction_ref, calendrier ICS de dépôt ; pas de règle applicable validée en moteur transversal démontré | Maintenir UNKNOWN/date déclarée ; échéancier juridique, sanctions et DGD différés jusqu'aux validations nécessaires |
| AUD-12 | Historique de docs et WIP restent locaux | Git status et 64 fichiers source non suivis dans snapshot ; trois autorités nouvelles non suivies | Reprise dans un clone HEAD seul incomplète. Pas de reset/clean/stash, ni push automatique |

Ces risques ne constituent pas une découverte de fuite tenant : les protections existent. Les nouveaux liens et configurations doivent prouver qu'ils ne divulguent rien via relation, compteurs, cache, export, logs ou LLM. Aucune preuve DB/security complète fraîche dans cet audit.

## Matrice exigences → code → tests → écarts

Les tests listés dans les artefacts sont **repérés**, pas tous exécutés dans ce bloc. EXISTANT n'implique pas complet/qualifié ; ABSENT_FLUX_CIBLE signifie flux cible non trouvé dans le périmètre inspecté, pas inexistence de toute primitive liée.

| ID | Fonction | Action | État | Écart et bloc |
|---|---|---|---|---|
| F01 | Identité, MFA, recovery et step-up | KEEP | EXISTANT_A_REQUALIFIER | Ne pas réécrire ; rejouer policies de toute route ajoutée. Pas de nouvelle preuve PostgreSQL/security complète dans cet audit. **Bloc :** A0 puis transversal |
| F02 | Membership, propriétaire, délégations et relève | KEEP | EXISTANT_A_REQUALIFIER | Propriété organisationnelle ≠ Patron ; configurations ne peuvent distribuer de capabilities. **Bloc :** Transversal/M0 |
| F03 | Entreprise, bibliothèque, capacités et preuves | ADAPT | EXISTANT_PARTIEL | Company/capability versions existent ; ce n’est pas un profil métier/checklist publié et snapshotté. **Bloc :** M0/M1 |
| F04 | Veille BOAMP, qualification P0/P1 et Affaire idempotente | KEEP | EXISTANT_A_REQUALIFIER | Socle à conserver ; ne pas multiplier sources de veille avant valeur longitudinale. **Bloc :** Régression A0/A1 |
| F05 | Affaire, consultations, lots et DCE applicable | ADAPT | EXISTANT_PARTIEL | Versions DCE disponibles ; contrat signé/version source ne doit pas être déduit du DCE applicable. **Bloc :** S0/A1/B1 |
| F06 | Sources documentaires version/hash/locator | ADAPT | EXISTANT_PARTIEL | Réutiliser DceDocument/SourceStatement/RequirementSource ; refs string contrats/paiement non résolues restent déclarées. Pas de SourceReference universel en double. **Bloc :** S0 |
| F07 | Ingestion, inventaire, extraction/OCR et formats | KEEP | EXISTANT_A_REQUALIFIER | Couverture locale bornée ; pas de garantie tous gros PDF/plans/formats. OCR/Docling artefacts et corpus à vérifier pour une promesse précise. **Bloc :** E1/qualification |
| F08 | RAG, ancrage et frontière financière | KEEP | EXISTANT_BORNE | RAG temporaire/corpus expurgé ; indexation persistante et supériorité non validées par cet audit. **Bloc :** Q1/E1 |
| F09 | RC/exigences/confirmation/contradictions humaines | ADAPT | EXISTANT_PARTIEL | Liens exigence/risque existants ; relier les impacts, engagement vendu et événements ultérieurs. **Bloc :** A1/B1/C1 |
| F10 | Risques et liens risque–exigence | ADAPT | EXISTANT_PARTIEL | Relation typée tenant/version déjà disponible ; ne pas dupliquer un graphe pour le même lien. Manque relation impact/condition/événement. **Bloc :** S0/A1 |
| F11 | Baseline → dérogation → impact et revues | ADAPT | EXISTANT_PARTIEL | baseline_observation_id sans FK à la version de contrat ; impact_statement libre ; revue versionnée existe. Ne pas déclarer la baseline absente ni la confondre avec un contrat signé. **Bloc :** S0/A1 |
| F12 | Applicabilité réglementaire et règles versionnées | ADAPT | PROFIL_EXISTANT_MOTEUR_NON_ETABLI | Profil déclaratif versionné ≠ bibliothèque de règles validées par régime/date. Validation externe et règle calendaire demeurent différées. **Bloc :** S0 puis E1 |
| F13 | Contrat signé/avenant, remplacement et requalification | ADAPT | EXISTANT_PARTIEL | FK instrument et source refs déclarées existent ; raccord à la pièce/hash et au contexte avant-offre reste à établir. **Bloc :** S0/B1/C1 |
| F14 | Droits et preuves humaines de réception/sortie | ADAPT | EXISTANT_PARTIEL | Actes RIGHTS_PRESERVATION/WORK_RECEPTION/CONTRACT_EXIT réels ; aucune conséquence juridique certaine ni moteur de droit acquis prouvés. **Bloc :** C1/E1 |
| F15 | Échéances juridiques déterministes | ABSENT_FLUX_CIBLE | NON_ETABLI | ICS et date déclarée ne constituent pas moteur régime/règle validée/déclencheur/calendrier/exceptions. Aucune échéance légale calculée dans A1. **Bloc :** E1 après validation externe |
| F16 | Sanctions/pénalités cumul/plafond/applicabilité | ABSENT_FLUX_CIBLE | NON_ETABLI | Taxonomie/signal et réserve financière déclarée ≠ moteur de sanctions applicable ; pas de plafond inconnu converti à zéro. **Bloc :** E1 après règles validées |
| F17 | OS/instruction et delta longitudinal | ABSENT_FLUX_CIBLE | RELATIONS_LOCALES_PARTIELLES | Delta DCE et avenants existent ; pas de flux dédié OS → ancien engagement/condition → impact/action/preuve. Pas de moteur universel requis. **Bloc :** C1 après A1/B1 |
| F18 | Prix/brouillon financier/import DPGF/BPU/Excel | KEEP | EXISTANT_A_REQUALIFIER | Import crée des lignes financières ; ne pas l’utiliser pour rapprochement partenaire sans source/receipt, ni comme preuve de coût couvert. **Bloc :** A0/S0 puis A1 |
| F19 | Calcul coût/marge et scénarios exacts | ADAPT | CALCULS_EXISTANTS_RELATIONS_PARTIELLES | Arithmétique en unités mineures existe ; garder ce patron et ne pas imposer Decimal/rewrite. Relation clause → impact déclaré → scénario → condition manque. **Bloc :** A1 |
| F20 | Impacts coût/cash/délai/capacité structurés | ADAPT | PARTIEL_TEXTE_ET_SCENARIOS | Axe/valeur connue/inconnue/unité/hypothèses et relation source-condition transversale non matérialisés ensemble. Déclaration ≠ calcul automatique de couverture. **Bloc :** A1 après S0/M0 |
| F21 | Capacité/ressources/charge | ADAPT | SERVICE_EXISTANT_INTEGRATION_PARTIELLE | Solveur OR-Tools et persistence run existent ; pas calendrier entreprise/portefeuille/conducteur intégré complet prouvé. Ne pas recréer le solveur. **Bloc :** A1 déclaration puis E1 |
| F22 | Portefeuille cash et couverture économique complète | ABSENT_FLUX_CIBLE | PROJECTION_PARTIELLE | Vue liste/couverture et calcul par Affaire ne prouvent pas modèle consolidé besoins cash/financement simultanés. **Bloc :** E1 |
| F23 | Partenaires fournisseur/sous-traitant/cotraitant/mandat | ADAPT | WIP_LOCAL_INTEGRE_A_REQUALIFIER | Module local, migration0118. Reçu/engagement humain existent ; locator/hachage pièce et lien vendu restent à enrichir. **Bloc :** A0/S0/A1 |
| F24 | Offres partenaires prix/validité/périmètre/transport | ADAPT | WIP_LOCAL_INTEGRE_A_REQUALIFIER | Déclarations et revues reçus exacts existent ; aucune somme/effet P3 induit. Pièce partenaire versionnée et hash restent non résolus. **Bloc :** A0/S0/A1 |
| F25 | Rapprochement manuel par poste partenaire | REPARER_AVANT_QUALIFICATION | WIP_BLOQUE | NameError reproduit ; modèle/routes/handlers non enregistrés dans bootstrap/metadata ; UI dédiée non repérée. Pas une feature livrée. **Bloc :** A0 sans extension fonctionnelle |
| F26 | Conditions Patron, contexte figé, P2/P3/P4/P5 | ADAPT | SOCLE_REEL_RELATIONS_MANQUANTES | Conditions/owner/date/preuve et références typées CASE/DCE_VERSION/DCE_REQUIREMENT/DECISION_RISK/PRICING_SCENARIO existent. Baseline/contrat/profil ne font pas partie des types validés actuels. Ajouter liens, pas un nouveau Decision. **Bloc :** S0/M0/A1 |
| F27 | Réponse technique, administratif et engagement vendu | ADAPT | EXISTANT_PARTIEL | Draft/snapshot/génération/proofs existent ; registre d’engagement versionné lié aux impacts/conditions et offre exacte non démontré de bout en bout. **Bloc :** B1 après A1 |
| F28 | MIRP, constructibilité et interfaces de lots | ADAPT | EXIGENCES_RISQUES_PARTIELS | Ni absence de toutes fonctions techniques ni MIRP intégral : exigences/risques sont socle ; contrats interfaces, moyens et constructibilité multi-lots dédiés restent à préciser. **Bloc :** A1 scénario borné puis E1 |
| F29 | Assurance, HSE, environnement et obligations vendues | ADAPT | DOCUMENTS_SIGNAUX_PARTIELS | Certificats et signaux existent ; adéquation assurance/prestation, prérequis ressources et engagements mesurables complets pas démontrés. Validation spécialisée toujours nécessaire. **Bloc :** E1 |
| F30 | Paquet exact, manifeste/hash, signature et dépôt humain | KEEP | EXISTANT_A_REQUALIFIER | Réutiliser P5/manifeste et preuves ; signature/export ≠ reçu externe. Aucun automatisme de dépôt supplémentaire. **Bloc :** Régression B1 |
| F31 | Attribution par lot, P6/P7, commande et passation | ADAPT | EXISTANT_PARTIEL | WON/commande/P6/P7 et C12 existent ; joindre version attribuée, engagement vendu et conditions source. P7 ne vaut pas OS. **Bloc :** B1 |
| F32 | Réception/réserves et obligations post-réception | ADAPT | EXISTANT_PARTIEL | Acte de réception/issue et lien réserve/acte réels ; coûts/échéances souvent déclarés, aucune clôture juridique induite. **Bloc :** C1 puis E1 |
| F33 | Paiement signal externe, qualification/revue/rejets | ADAPT | WORKFLOW_EXISTANT_TEXTE | Qualification texte/revue/collecte/rejets effectivement présents ; pas montant/currency/date attendue/encaissée/compte contractuel structuré. Ne pas refaire les reçus ; pas MOVE avant ADR. **Bloc :** C1 déclaration puis E1 |
| F34 | Settlement/DGD/solde/garanties/forclusion | ABSENT_FLUX_CIBLE | ACTES_PARTIELS | Signal, réception et sortie ne sont pas modèle de règlement des comptes complet ni DGD tacite calculable. **Bloc :** E1 après validation externe |
| F35 | Suspension/fermeture/conservation/export/intégrité | KEEP | EXISTANT_A_REQUALIFIER | Historique d’actes réel ; ne pas multiplier une nouvelle synthèse administrative au lieu du lien métier. READY/hash ≠ réception externe. **Bloc :** Régression C1 |
| F36 | REX/entretien/applicabilité nominative | ADAPT | EXISTANT_ET_WIP_LOCAL | Snapshot entretien et applicabilité humaine réels ; relier écart vécu à engagement/impact/événement, sans apprentissage automatique. **Bloc :** C1/Q1/E1 |
| F37 | Configuration métier/version/adoption/snapshot | ABSENT_FLUX_CIBLE | NON_ETABLI | WatchProfile et CapabilityVersion existent mais ne sont pas configuration métier d’Affaire. Version/config snapshot doit précéder les nouvelles décisions dépendantes. Historique sans config reste UNKNOWN. **Bloc :** M0 AVANT A1 ; M1 éditeur ensuite |
| F38 | Graphe causal/transversal et confidentialité dérivée | ADAPT | FK_LOCALES_PAS_CHAINE_COMPLETE | Réutiliser FK/readers ; filtrage avant count/export/cache/LLM. Pas de graph DB ni module générique avant besoin. **Bloc :** S0/A1/B1/C1 |
| F39 | UX C00–C16/PUX, accessibilité et responsive | ADAPT | SURFACES_PARTIELLES | 285 tests composants verts ne valent pas navigateur/lecteur d’écran. Conditions/références saisies JSON technique : à remplacer par interactions métier dans A1, pas suppression du backend. **Bloc :** A1/M1/B1/C1 puis couverture E1 |
| F40 | Qualification Golden/recettes/benchmark et marché | ADAPT | HARNESS_EXISTANT_PREUVES_BORNEES | Pas de benchmark concurrent client ; corpus et validations doivent être réellement exécutés. 854 chapitres ne constituent pas 854 tests passés. **Bloc :** Q1 |
| F41 | Migrations/runtime et branche locale | REPARER_AVANT_QUALIFICATION | ECHEC_VERIFIE | Script graph0121 ≠ runtime expected0120, test architecture échoue. État DB réellement appliqué non interrogé ; imports0121 incomplets. **Bloc :** A0 |
| F42 | Sécurité IA/tenant/classification/retries/concurrence | KEEP | SOCLE_EXISTANT_NOUVEAUX_LIENS_A_PROUVER | Pas audit offensif complet ; les relations/config nouvelles réclament refus et non-divulgation serveur. Aucune fuite constatée déduite d’un seul champ libre. **Bloc :** Transversal S0/M0/A1 |
| F43 | Exploitation, stockage, sauvegarde/rotation/reprise | KEEP | LOCAL_BORNE_PUBLIC_NON_QUALIFIE | Runbooks locaux réels ; pas de fournisseur VPS ni restauration/hardening hôte réel validés ici. **Bloc :** PROD uniquement après GO adapté |
| F44 | API/DTO/events/ownership et interop ERP | ADAPT | CONTRATS_EXISTANTS_RECONCILIATION_REQUISE | Évolution additive, réutiliser ports existants, pas intégration ERP générique ni changement ownership opportuniste. Config/source nouveaux types à intégrer explicitement. **Bloc :** S0/M0/A1 puis E1 |
| F45 | Gouvernance documentaire et plan de reprise | KEEP | PREUVES_DOCUMENTAIRES | CDC intégraux et plan local ; documents non suivis absents d’un clone HEAD seul. Conflits sémantiques intégrés à résoudre par tranche. **Bloc :** Audit puis toutes tranches |

## Ordre corrigé — aucune réécriture globale

1. **A0 — intégration/baseline du WIP** : corriger NameError, caractériser0121, aligner runtime/metadata/route/handler selon contrat ; vérifier upgrade et contraintes sur DB éphémère avant gates. Ne pas inventer la tête DB appliquée. Les correctifs sont prérequis, pas fonctionnalité Deep Core neuve.
2. **S0 — références utilisables** : réutiliser DCE sources et DecisionContextReference ; fixer type/classification/tenant/Affaire/version/locator/hash et UNKNOWN pour contrat/partenaire non résolu. Identifier explicitement les consumers ; pas registre générique redondant.
3. **M0 — configuration minimale versionnée** : publication/adoption/snapshot déterministe de quelques paramètres métier autorisés, socle non overridable. Le profil complet et son UI ne sont pas nécessaires pour enregistrer correctement sa version. Les décisions passées ne reçoivent pas artificiellement le nouveau profil.
4. **A1 — avant engagement** : source/applicabilité/impact déclaré → condition Patron existante → C07, interaction métier au lieu de JSON, preuve React/HTTP/PostgreSQL/rejeu/refus. Les politiques P3 existantes ne changent pas par ajout du lien.
5. **M1 — personnalisation utilisable** : éditeur/preview/adoption, deux profils sur le même scénario, sécurité invariants inchangés. Réutiliser M0, aucun deuxième modèle.
6. **B1 puis C1** : offre/contrat attribué/conditions repris à la passation, puis événement réel lié au même engagement et action/preuve. REX causal s'appuie sur les objets déjà livrés.
7. **Q1/E1/PROD** : corpus/terrain/qualification, périmètre restant des CDC, règles spécialisées et exploitation réelle avec validations correspondantes ; NO-GO public reste fermé.

## Vérifications réellement exécutées

| Commande/preuve | Résultat | Limite |
|---|---|---|
| `PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/pytest backend/tests/domain backend/tests/architecture -q -p no:cacheprovider` | **297 passés / 1 échec**, 1.68s ; échec `test_runtime_schema_head_matches_alembic_script_graph` | Erreur de contrat source/runtime, pas erreur environnement ni interruption ; pas suite backend API/DB complète |
| `./.venv/bin/alembic -c backend/alembic.ini heads` | `20260930_0121 (head)` | Lit le graphe des fichiers, pas état DB |
| Import isolé modèle0121 avec Python `-B` et PYTHONPATH backend | **NameError** reproduit | Pas de connexion DB ; ne prouve pas que toutes les autres parties du WIP échouent |
| `pnpm --dir web test` | **285/285**, 52 fichiers, 21.02s | Tests composants/API mocks, pas navigateur réel ni E2E PostgreSQL |
| `pnpm --dir web typecheck` / `pnpm --dir web lint` | **Verts**, sorties de processus code0 | Pas de build ni campagne d'accessibilité réelle dans ce bloc |
| Autorité/conservation/reprise documentaire : pytest ops ciblé | **4/4 verts** ; 45 familles/899 localisateurs et 1 265 empreintes source vérifiés ; diff-check vert | Preuve documentaire et intégrité du snapshot, pas validation métier complète |
| Inventaire AST backend | Aucun SyntaxError détecté | Syntaxe AST ne détecte pas le NameError de résolution au runtime |

La dernière suite backend complète fiable au HEAD n'est pas rétablie : les runs antérieurs DiskFull/interrompu restent historiques. La présence de tests DB/E2E ne prouve pas leur passage actuel. Aucun test de performance ou benchmark concurrent ajouté.

## Invariants et conservation

Audit du code en lecture seule : aucun fichier production, migration ou test métier corrigé. Les seules modifications de dépôt autorisées par ce bloc sont les livrables d'audit, le plan et les dispositions documentaires nécessaires. Tenant/roles/MFA/FINANCIAL_PRIVATE/append-only/idempotence/P0–P7/UNKNOWN restent les contrats à préserver et à tester pendant l'implémentation. Aucune action externe, aucun push, aucune suppression du WIP.

Outils : ECC production-audit (preuves locales), méthode de navigation codebase-onboarding, Serena pour symboles, ripgrep/AST/Git et tests locaux. Context7 non nécessaire : pas d'API de bibliothèque nouvelle. Jev/Manus non nécessaires pour cet audit local, aucune donnée envoyée à un agent externe. Basic Memory MCP absent ; fichiers locaux sont la reprise, pas un miroir prétendu synchronisé.

## Reprise

Lire ce rapport et la matrice, puis la ligne active du plan global. Vérifier le digest du snapshot avant de réutiliser ces résultats. Si un fichier source a changé, actualiser la preuve concernée au lieu de déclarer l'ancien run valide. Après A0/S0/M0, la première verticale A1 devient codable sans fabriquer des doubles d'objets déjà présents.

**Prochaine étape :** corriger les blocages vérifiés du WIP C08 et de la tête Alembic, qualifier le snapshot local, puis établir les références source et le socle minimal de configuration versionnée avant A1, sans ouverture publique.


## Clôture A0 / S0 / M0 — 2026-10-01

Le snapshot de code actuel est 4f1d37dbc102f7b08d175acdf283547c54d77f4cd24e99f11abc220337649e4f sur HEAD `1c8ac62fcddc78d2b156f70df9f0b130910cc918`. Le C08 line comparison est importable et enregistré dans Alembic/bootstrap ; son index passe sous la limite PostgreSQL et le test de suppression cible désormais la clé présente sur le modèle. Le runtime et le graphe de migration sont à `20260930_0122`.

S0 réutilise les ancrages DCE et les références génériques Decision existants : le contexte peut maintenant vérifier un `CONTRACT_BASELINE_IMPACT` exact par révision et un `BUSINESS_METHOD_PROFILE` exact par version/hash **adopté à cette Affaire**. La table baseline a un garde append-only. Les anciennes `source_refs_json` strings demeurent historiques et UNKNOWN tant qu'elles ne sont pas résolues.

M0 est livré en backend : version entreprise à profil borné (vocabulaire et checks informatifs), canonical JSON SHA-256, publication idempotente et révision optimiste, adoption append-only par Affaire, lecture Patron, FK tenant-scoped, hash/version vérifiés dans le contexte de décision. `required`, scripts, règles libres, override des portes ou automatismes sont refusés/non présents. L'éditeur UX, aperçu visuel et adoption depuis écran restent M1 ; l'éditeur complet n'a pas été livré.

Preuves du bloc : migration complète depuis base sur PostgreSQL temporaire vers 0122 ; 9 tests DB C08/M0 (révisions, rejeu, isolation, append-only, hash/références) verts ; 338 tests domaine/architecture/ops/API ciblés verts ; typecheck front et Ruff ciblé verts. **L'ensemble du backend n'a pas été rejoué.** `alembic check` ne détecte aucun écart sur les nouvelles tables profil/adoption ni sur C08 ; il relève encore le tenant-index et les noms de contraintes historiques de la table baseline, ainsi que d’autres dérives dans le schéma préexistant. La migration 0122 ajoute seulement son garde append-only ; aucun nettoyage global du schéma n’est revendiqué.

A1 est maintenant le seul prochain bloc : lier une exigence/source DCE et la preuve baseline à un impact déclaré, à une condition Patron précise et à C07 ; l'écran doit inclure la référence adoptée exact du profil. Tests API/PostgreSQL/navigation avec UNKNOWN, refus, rejeu ; aucune promotion P3 implicite. Le NO-GO public reste maintenu. Le code local reste non commité et non poussé.
