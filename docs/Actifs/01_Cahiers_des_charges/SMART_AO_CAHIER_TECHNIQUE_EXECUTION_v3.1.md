# SMART AO — Cahier technique d'exécution v3.1

**Statut : référence technique active dérivée du Product Freeze v3.1 — 30 septembre 2026.**
Spécification de production future, non certificat de production publique. Le nom v3.1 de ce cahier ne remplace pas l'architecture logicielle v3.1 Phase 0 par une migration globale.


## CONSOLIDATION V3.1 — lecture intégrale et arbitrages de compatibilité

Le cahier actif comprend le cadrage V3.1 et les chapitres détaillés intégrés ci-dessous. **Périmètre cible complet ≠ première livraison ≠ code qualifié.** Les exigences différées restent écrites et applicables à leur future tranche ; les capacités existantes et leurs protections restent maintenues.

| Sujet | Disposition actuelle applicable à tous les chapitres |
|---|---|
| Autorité et références historiques | Freeze v3.1 actif ; mentions v0.4/v1/v2/candidat et anciennes injonctions de promotion dans le contenu intégré sont provenance, pas nouvelle demande d'approbation |
| Priorité de construction | A avant engagement, B passation, C événement/changement ; les anciens T0–T8 et priorités horizontales ne supplantent pas le plan global actif |
| Engagement Control / Payment | Modèle logique transversal ; aucun déplacement de contexte, nouvelle façade ou table de graphe obligatoire sans audit/ADR/consumer et preuve de tranche |
| Règles, sanctions, échéances, DGD et cash | Contrats cibles conservés en détail ; calcul/automatisation soumis aux validations et faits applicables ; UNKNOWN si non établis, aucun effet juridique certain par LLM |
| Assurance, HSE, environnement, MIRP, portefeuille | Exigences conservées et détaillées, pas supprimées ; réalisation/qualification ultérieure explicitement distincte d'une promesse initiale |
| Personnalisation | Exigences PF31-05/M31-06/CT31-05 ajoutées à l'ensemble du périmètre ; profils versionnés et snapshots, sécurité/portes/confidentialité non paramétrables à la baisse |
| Couverture UX | Catalogue et fondations conservés ; les surfaces dérivent de ces contrats, aucun écran déclaré livré par sa présence dans le cahier |
| Observations concurrentielles anciennes | Matériau stratégique daté et non benchmark produit ; pas d'exclusivité ni supériorité déduite |
| Déploiement et preuve | NO-GO public ; toute ancienne validation ou baseline se rapporte à sa date/snapshot, pas au checkout actuel |

**AS-IS :** les précédents cahiers actifs courts perdaient l'accès direct à une partie de la profondeur requise. **Risques :** omission métier, doubles autorités et choix techniques interprétés comme livrés. **Insertion :** intégration des chapitres complets dans les trois cahiers existants avec identifiants uniques et contrôle de couverture. **Plan minimal :** conserver les corps de texte, expliciter les arbitrages ci-dessus, puis vérifier origine, présence, liens, autorité et plan. **Tests :** conservation de chaque ligne non-titre et chaque chapitre, absence de doublon d'ancre, autorité unique ; aucune gate production dans ce bloc documentaire.


## CT31-01 — AS-IS, risques et insertion

**Qualification technique locale du 09/10.** Fermeture demandée par l’Owner avant toute reprise du cahier codable : lint/format globaux verts sur 1180 fichiers, mypy sur 1025 sources, backend final 2193/2193, couverture de l’application 87,92 % (seuil 85,50 % conservé), Web 513/513 et typecheck/lint/build verts. Les avis connus Python et Node sont fermés par mises à jour des locks et bornes directes; audits complets zéro, Semgrep/Bandit/secrets zéro. Les scripts de diagnostic n’infèrent plus une base PostgreSQL locale : benchmark destructif protégé par URL/flag jetable/moteur exact, export OpenAPI en mémoire; HTTP(S) borné sans redirection bearer. Revue ciblée sans finding bloquant. Le [plan actif](../00_Pilotage_et_audits/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md) porte les commandes, preuves, avertissements et checkpoints exacts; cet état ne qualifie ni corpus réel, ni exploitation/VPS, ni GO public. Direction visuelle ultérieure obligatoire : PF31-11 du Product Freeze, design Cytd adapté avec captures et typographies Owner.


Stack conservée : modular monolith Python/FastAPI, React/TypeScript, PostgreSQL/Alembic, ports/adapters existants. Ni Rust ni graph DB ni framework ajouté pour ce réalignement.

Le [code map T0](../../Archive/02_Audits/T0_Realignement_V3/T0_DEEP_CORE_CODE_MAP_2026-09-30.md) établit la couverture au HEAD `1c8ac62` et distingue le WIP local. La preuve `ContractBaselineDeviationImpact` existe déjà dans DCE : ce n'est pas une baseline signée complète. Les documents/versions/locators DCE existent. Contrats/avenants, réception, requalification et paiement existent dans Pricing ; leurs références sont souvent des chaînes. P0–P7 et REX sont réels. Il manque les relations longitudinales complètes et un flux OS dédié.

Risques : reconstruire les mêmes objets ; mélanger DCE et contrat signé ; transformer champs libres en calcul fiable ; migration d'ownership prématurée ; fuite financière par une projection ; profil configurable qui contourne les portes ; statut de tests mal rattaché au snapshot source.

Insertion : garder les écritures dans leur contexte existant et ajouter seulement la relation et projection nécessaires. Decision reste propriétaire de P3 ; Submission du paquet P5 ; DCE des sources/exigences ; Pricing des déclarations économiques actuelles. Un déplacement de Payment ou nouveau contexte Contract Control exige ADR consommateurs/transactions/API/migration/rollback ; aucun MOVE dans la première verticale.

## CT31-02 — Relations source-backed

Avant nouveau schéma, inventorier les modèles DCE document/source/requirement et les instruments contractuels. Réutiliser leurs identifiants. Pour chaque relation transversale ajoutée : tenant_id, case_id, identifiants/version source et cible, nature du lien, auteur, date et justification. Ne pas créer une table générique de graphe avant besoin de requête démontré.

Référence structurée cible : source_type, document_id/document_version_id quand résolus, anchor/locator, hash quand disponible, observed_at ; rule_version_id uniquement si une règle existe. En conserver la provenance : résolue depuis registre, déclarée par humain ou extraite candidate. Une résolution incomplète reste UNKNOWN et conserve la chaîne historique ; jamais de backfill par invention.

Les références doivent être vérifiées dans le même tenant/Affaire avant lecture, écriture ou comptage. Les FK composites tenant/case sont privilégiées lorsque les tables existantes le permettent. Des identifiants UUID seuls ne prouvent pas isolation ou applicabilité. Source immuable et état de revue sont distincts.

## CT31-03 — Première verticale A codable

Audit initial des commandes baseline/review, des instruments, impacts Pricing et conditions Decision ; relever signatures et politiques publiques exactes avant tout ajout. Noms de DTO/endpoints à fixer dans ce contrat de tranche, sans inventer une API déjà existante.

Contrat minimal d'écriture : un lien humain entre preuve baseline/source exacte, applicabilité à l'Affaire/lot et impact déclaré, puis lien vers une condition Patron existante ou créée par son service autorisé. Identifiants command/idempotency et version attendue selon les patterns installés. Le lien ne modifie pas P3 de lui-même.

Impact : axe fermé COST/CASH/SCHEDULE/CAPACITY ; valeur connue ou inconnue explicitement, unité/devise applicable, hypothèses, justification et sources. Réutiliser la représentation numérique installée ; argent exact en unités mineures entières selon le patron existant, ou Decimal/NUMERIC si le contrat le requiert ; jamais float. Ne pas réécrire les calculs entiers déjà validés. Refuser valeur+UNKNOWN contradictoires, unité manquante d'une valeur connue et lien source étrangère. Pas de conversion, addition, classement ou coût couvert dans cette tranche.

Projection C07 de l'engagement : source/version accessible, applicabilité, impact autorisé, condition/acte et historique. C08 conserve les détails financiers ; C09 les identités et reçus partenaires permis. Les relations privées sont filtrées avant pagination/count/projection, pas simplement masquées par CSS.

Le scénario de clôture passe par React → HTTP → PostgreSQL, puis relecture après interruption ; il doit retrouver la condition et la version initiales. Aucun nouveau moteur juridique n'est nécessaire pour livrer cette valeur.

## CT31-04 — Versions, invalidation et temporalité

Relations et revues sont append-only, ou versionnées selon l'aggregate existant ; jamais UPDATE destructif d'un acte. Nouveau DCE, reçu partenaire, avenant ou adoption de profil crée un événement d'obsolescence/revue des liens affectés. La projection distingue fait initial et état courant dérivé, avec référence à l'événement qui explique REVIEW_REQUIRED/SUPERSEDED.

Ordre déterministe par séquence/révision serveur avec identifiant de départage ; filtre tenant/Affaire avant ordre et pagination. Le client ne recalcule pas l'état autoritatif. Optimistic concurrency s'applique aux commandes qui dépendent d'une version observée ; conflit explicite, aucun retry aveugle sur une intention modifiée.

## CT31-05 — Configuration métier versionnée

Première tranche séparée et bornée : profil entreprise contenant vocabulaire, checklist, catégories de vigilance et modèles d'actions/preuves. Réutiliser Enterprise et son authorization ; ajouter un modèle de configuration seulement si aucun contrat équivalent n'existe après audit.

Identité cible extensible : entreprise/tenant, configuration_id si plusieurs profils métier deviennent nécessaires, revision, schema_version, contenu validé, digest canonique, acteur/date, référence prédécesseur. Le socle M0 implémenté utilise l'unique `EnterpriseCompanyRecord` du tenant comme racine implicite du profil, `version_number` et `profile_version_id` pour chaque version ; il n'existe pas de brouillon ou de second profil entreprise en concurrence. `profile_json` V1 est borné aux alias métier (`terminology`) et à 40 contrôles additionnels informatifs (`additional_checks`) sans flag bloquant. Le SHA-256 porte le JSON validé canonique, pas une authenticité juridique.

Chaque adoption d'Affaire est un acte append-only avec numéro de révision, FK vers l'identifiant, le numéro et l'empreinte de version. Le contexte Patron peut ensuite référencer le profil adopté exact : les validateurs contrôlent tenant, Affaire, version et hash. Un historique de décision sans cette référence reste sans configuration démontrée ; il n'est pas complété après coup. A1 devra envoyer la référence explicitement dans le contexte figé.

Cycle : DRAFT → prévisualisation → publication immutable → adoption explicite par nouvelle Affaire ou acte sur Affaire existante. Remplacer/revenir à une version crée un nouvel acte ; publication précédente conservée. Les préférences d'affichage personnelles ne changent pas les règles métier.

M0 livre l'API Patron de publication/liste de versions et d'adoption/relecture Case ; M1 doit livrer l'éditeur et l'aperçu React pour rendre cette personnalisation utilisable sans requête API manuelle. Les contrôles PostgreSQL refusent toute modification/suppression d'une version publiée ou d'un acte d'adoption. Les versions et l'adoption sont tenant-scoped et sérialisées par verrou/numéro attendu.

Résolution contrôlée : socle → pack → entreprise → adaptations Affaire. Allowlist de clés et enums, validation taille/profondeur, références locales tenant-scoped et refus de clé inconnue. Aucun eval, Python/JavaScript/SQL utilisateur, template exécutant du code, URL distante chargée implicitement ou prompt capable d'altérer les politiques.

Invariants non overridables : contrôles sécurité, B0/B1/B2/P0–P7, UNKNOWN, classifications minimales, nécessité de preuve et ordre des portes. La publication refuse une configuration qui veut retirer une exigence obligatoire. Les seuils internes produisent une vigilance, jamais conclusion juridique/GO. L'adoption ne change pas les décisions antérieures ; elle propose revue des objets affectés.

Pas de DSL, moteur de workflows universel, serveur plugins ou duplication source par client. Un JSON validé avec modèles installés et PostgreSQL suffit tant que les besoins restent bornés. Étendre seulement sur un scénario métier vérifié.

## CT31-06 — API, sécurité et UI

S'appuyer sur auth/session/MFA/step-up/policies actuelles. Un droit nouveau doit être explicite et testé ; les profils d'entreprise ne distribuent pas de capabilities. Support et tiers ne deviennent pas Patron. Confidentialité FINANCIAL_PRIVATE/PERSONAL_DATA propagée aux read models, cache, recherche, LLM, exports et logs.

Écriture atomique : registre idempotent et événement/état selon transaction existante ; outbox seulement si side effect externe réel. Rejeu même payload retourne effet confirmé unique ; réutilisation d'une clé pour intention différente refusée. Concurrence de deux révisions testée. Aucun appel fournisseur/LLM dans le domaine.

UI : état chargement/indisponible/vide/UNKNOWN distincts ; succès seulement confirmé serveur ; double clic bloqué ; identifiants de retry conservés par intention et Affaire ; réponse tardive d'ancienne Affaire ignorée. Le changement de case_id purge projections et intentions locales selon les patterns existants. Clavier, focus, messages d'erreur et responsive vérifiés sur le parcours livré.

Les exports contiennent seulement les données autorisées et versions citées ; READY/hash local n'est ni livraison ni reçu externe. Redaction et corpus permis restent requis pour tout usage concurrentiel/IA externe.

## CT31-07 — Échéances/règles : frontière différée

Pas de moteur juridique avant contrat validé. Future computation exige règle/source/version, régime et période d'effet, applicability validée, déclencheur prouvé, calendrier/fuseau et exceptions. Résultat expose inputs, algorithm/rule version et état NOT_COMPUTABLE/provisoire/à revoir/validé selon contrat futur. Le simple ajout d'une date libre ne satisfait pas cette exigence.

Les règles internes personnalisées ne valent pas règle légale. Aucun mécanisme de configuration ne transforme un texte CCAG ou une réponse LLM en règle exécutable approuvée. La qualification externe est version/périmètre/preuve, non un accord générique à tout calcul.

## CT31-08 — Migrations et compatibilité

Migrations additives après audit de la tête réelle. Ne pas déclarer `0121` appliquée parce qu'un fichier existe. Conserver les données historiques ; liens nouveaux optionnels pendant transition, état UNKNOWN explicite. Valider contraintes, upgrade sur données anciennes, réapplication attendue, transaction, rollback/downgrade lorsque contrat autorise, triggers append-only, index et isolation.

Ne pas supprimer champs strings existants avant preuve de résolution et compatibilité consumers. Ne pas renommer endpoints/événements publics silencieusement ; contrat versionné si breaking change. Un downgrade ne peut prétendre conserver des données qu'il efface : documenter archive/restauration et refus si nécessaire.

## CT31-09 — Programme de preuve et rythme des gates

| Bloc | Preuves nécessaires |
|---|---|
| Relation et impact | Domaine nominal/UNKNOWN/invalide ; API permission/tenant ; DB contraintes/append-only/idempotence/concurrence |
| Condition P3 | Relation exacte, refus de promotion induite, relecture des décisions, obsolescence après source nouvelle |
| Configuration | Validation/preview/publication/adoption ; impossibilité override sécurité ; ancien snapshot reproductible ; tenant étranger/import hostile |
| Web | Parcours réel, focus/clavier, résultat inconnu/rejeu, réponses hors ordre et changement d'Affaire |
| Régression | Tests des contextes touchés + architecture/imports + typecheck/lint/build ; complet à la clôture d'un grand bloc ou si changement transversal |

Pas de full gates après chaque libellé ou micro-correction. Tests ciblés pendant le bloc ; gates complètes à une frontière significative. Enregistrer SHA **et empreinte du snapshot local incluant le WIP pertinent**, versions DB/dépendances, commande exacte, pass/fail/skipped, preuve et limites. Un run HEAD ne valide pas le checkout modifié.

Base de test explicitement éphémère et dimensionnée ; URL fournie selon configuration locale, aucun fallback sur DB métier. Ne pas détruire les bases CUA/dev existantes. La suite complète précédente a rencontré DiskFull puis interruption ; aucune baseline backend fraîche verte n'est acquise par ce cahier.

## CT31-10 — Séquence d'exécution

1. Stabiliser le snapshot à qualifier : statut Git, inventaire WIP, migrations/imports et dépendances. Le rapprochement C08 `0121` reste incomplet/non qualifié et doit être caractérisé, sans intégration opportuniste ni suppression.
2. Obtenir baseline appropriée backend/frontend sur ce snapshot ; distinguer code, environnement et interruption.
3. Fermer S0 : réutilisation des sources DCE et références de contexte Decision, résolution tenant/Affaire/version ou UNKNOWN.
4. Livrer M0 : identité/version de configuration publiée et adoption/snapshot minimal avant les nouvelles décisions A1. Les anciens contextes sans configuration restent UNKNOWN, sans backfill arbitraire.
5. Livrer A1 : source/version → applicabilité/impact déclaré → condition Patron existante, projection et HTTP/DB/browser ; puis M1 éditeur/aperçu et même scénario sous deux configurations, sans effets sur sécurité.
6. Fermer B sur contrat attribué/passation ; fermer C sur un événement lié au même engagement. Pas de paiement/settlement ou moteur OS universel en parallèle.
7. Benchmark et revue terrain ; revoir l'hypothèse commerciale avant extension horizontale.

Audit actualisé du checkout : [rapport et matrice](../00_Pilotage_et_audits/V3_1/CHECKOUT_COVERAGE_AUDIT.md). Il précise ce qui existe déjà et les prérequis avant A1, sans prétendre clôturer les limites DB/juridiques.

Le [plan global](../00_Pilotage_et_audits/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md) est l'unique statut opérationnel. La [matrice v3.1](../00_Pilotage_et_audits/SMART_AO_REALIGNEMENT_V3_1_DECISIONS_ET_TRACABILITE_2026-09-30.md) relie exigence, code et preuve manquante. Les chapitres CT2 intègrent tout le cahier technique v2.1 (domaine, persistance, API, IA, sécurité, performance, exploitation et recettes). Les chapitres CT3 intègrent tout le delta technique V3 transmis. Aucun recours aux archives n'est nécessaire pour accéder à cette profondeur ; l'archive est uniquement la preuve de provenance.

## CT31-11 — État vérifié A0/S0/M0 avant A1, au 1er octobre 2026

`20260930_0121` corrige l'import C08, son chargement par Alembic et le runtime ; modèle et migration partagent les contraintes/index PostgreSQL vérifiés. `20260930_0122` ajoute les versions de profil, adoptions Case et le garde append-only de la preuve baseline existante. Le contexte de décision vérifie `BUSINESS_METHOD_PROFILE` (adopté, version/hash exact) et `CONTRACT_BASELINE_IMPACT` (Affaire/tenant/révision exacte, table maintenant protégée append-only). Les références source DCE restent `DCE_REQUIREMENT` et gardent leur chaîne d'ancrage existante. A1 devra imposer une référence au profil adopté lors du gel du nouveau contexte et relier l'impact à une condition Patron précise ; cette obligation n'est pas déjà activée globalement dans l'application.

La migration vide→0122 et 9 tests PostgreSQL C08/M0 ont réussi sur une instance temporaire à volume nul ; aucun schéma de base persistante n'est qualifié. 338 tests backend ciblés, typecheck web et Ruff ciblé sont verts. `alembic check` cible sans delta les tables C08 et profil/adoption. La table baseline garde des différences historiques d'index tenant et de noms de contraintes ; le contrôle global signale aussi d'autres incohérences historiques. L'ensemble des tests backend n'a pas été rejoué. C07, la condition P3 liée à une preuve et l'éditeur M1 restent à implémenter ; NO-GO public maintenu.

### CT31-12 — A1 implémentée localement au 1er octobre 2026

Le code ajoute `20261001_0123_a1_condition_contract_evidence.py`. Les preuves antérieures gardent leur shape historique ; les nouveaux actes A1 stockent l'identifiant/révision d'une exigence DCE confirmée courante et le serveur dérive `source_observation_id` depuis cette exigence applicable à l'Affaire. L'API ne demande pas au navigateur de fournir cette observation. Les références libres restent des localisateurs déclarés par le Patron et ne sont pas promues en authenticité ou conclusion juridique.

Le gel d'un contexte qui référence `CONTRACT_BASELINE_IMPACT` exige un `BUSINESS_METHOD_PROFILE` adopté exact. Une commande Patron distincte peut relier une preuve/révision à une condition `OPEN` d'une décision `CONDITIONAL_GO` finalisée et courante, uniquement si le contexte final sélectionné contient la même exigence DCE confirmée, le même impact/révision et un profil unique/version/hash toujours adopté. Le lien est tenant-scoped, idempotent, append-only en base et lié par FKs composites. Il ne change ni l'issue de décision ni le statut de la condition ; aucun calcul de coût, GO/P3 induit ou conclusion juridique n'est produit. Écriture/lecture relèvent de FINANCIAL_PRIVATE et restent Patron Admin.

C07 affiche le localisateur, baseline, dérogation et impact déclarés en `HUMAN_REVIEW_REQUIRED`, propose un lien seulement vers une condition ouverte et projette l'exigence, la preuve, la révision du contexte et le profil exact. La révision de confirmation DCE est incluse à la lecture pour choisir la source ; son observation sous-jacente reste résolue au serveur.

Preuve au snapshot de travail local (HEAD publié `657b213`, WIP non commité) : test PostgreSQL HTTP A1 avec migration upgrade/downgrade, rejeu d’écriture et de lien, refus révision DCE obsolète/état `UNKNOWN`, absence de profil, refus rôle/tenant, lecture C07, absence de promotion et refus UPDATE append-only ; tests projection DCE **3/3**. Les tests ciblés application/domain/API sont **12/12**, frontend **288/288**, typecheck, lint et build réussis. Le build émet encore un avertissement de chunk JavaScript >500 kB. La suite backend complète et le navigateur CUA ne sont pas qualifiés. Aucun commit/push ; NO-GO public maintenu.

### CT31-13 — M1, aperçu et adoption React du profil métier

C07 propose un éditeur borné du schéma V1 existant : cinq alias métier et jusqu’à 40 contrôles informatifs, chacun limité à clé, libellé et axe fermé. L’aperçu JSON est local et ne vaut pas validation serveur ; la publication utilise l’endpoint immuable M0 et affiche la version/hash retournés. Une version publiée est sélectionnée puis adoptée explicitement à l’Affaire par l’endpoint append-only existant. Le formulaire n'expose ni capability, seuil bloquant, instruction exécutable, permission ou override de règle obligatoire. L’absence d’entreprise, l’indisponibilité et l’absence d’adoption restent visibles.

Lors du gel d'un nouveau contexte C07, l'application injecte le profil courant adopté (ID, version, hash) si le Patron ne l'a pas saisi ; une référence manuelle multiple, obsolète ou discordante est refusée. Pour une baseline A1, absence ou chargement indéterminé de l'adoption bloque le gel. Les contexts déjà gelés ne sont jamais recalculés après une nouvelle adoption.

L’E2E PostgreSQL rejoue le même scénario A1 sur deux Affaires partageant l’exigence DCE : la première adopte v1, la seconde une v2 avec vocabulaire et contrôle informatif distincts. Les deux impacts et conditions sont reliés à leur profil exact ; après l’adoption v2, la décision v1 conserve son contexte, son hash, sa révision et sa condition ouverte. Ce test a exposé une collision de PK des références Decision quand deux contextes réutilisaient la même source DCE : l’identifiant interne est désormais dérivé du `context_id` et de la référence, sans migration ni modification de l’empreinte métier du contexte.

Preuves locales : E2E A1 + projection DCE + persistance version/adoption **8/8 PostgreSQL** ; tests backend ciblés **17/17** ; tests React **293/293**, typecheck/lint/build et Ruff ciblé verts. Aucun full backend, test navigateur CUA, commit ou push. Build : avertissement de chunk principal >500 kB. NO-GO public maintenu.

### CT31-14 — B1, passation P7 vers le Conducteur

**AS-IS :** P5 conserve un paquet immuable et une autorisation \`AUTHORIZED\` liées à une version de manifeste/hash ; l'attribution \`WON\` est un fait séparé par lot ; la lecture C12 des actes résultat/commande/P6/P7 est Patron-only. Aucun lien ne permet d'inférer que le dernier instrument de contrat déclaré correspond à l'offre gagnée.

**Risques :** choisir le mauvais paquet après plusieurs dépôts ; divulguer le snapshot financier via le manifeste ou le ZIP ; confondre P7 avec un ordre de service ; perdre une condition ouverte ; présenter une version signée comme rapprochée sans acte source.

**Insertion minimale :** un acte \`CaseHandoverSnapshot\` append-only relie, sur action Patron, une attribution \`WON\` au paquet P5 autorisé exact du même tenant/Affaire/lot. Le serveur recalcule le hash canonique, vérifie l'autorisation P5 et la présence du lot dans le périmètre de ce paquet, puis capture la version de décision/contexte et toutes ses conditions \`OPEN\`, avec les liens A1 existants. Le rejeu retourne le même acte ; une nouvelle transmission crée une révision. La projection est accessible au Patron et au Collaborateur de profil \`RESPONSABLE\` dont l'affectation serveur autorise \`CASE_DCE_READ\` et \`INTERNAL_OPERATIONAL\`.

La projection expose les identifiants et hash exacts du paquet P5 et du document technique, la source d'attribution, les conditions ouvertes (label, état, échéance déclarée ou inconnue) et les sources A1 liées. Elle n'expose ni manifeste brut, snapshot/prix/marge/cash, ni texte libre P6/P7. Le document `TECHNICAL_RESPONSE` dont l'identifiant/version/hash figurent dans le P5 autorisé est téléchargeable après revalidation des références et du hash ; le ZIP P5 et ses références financières ne sont pas servis au Conducteur. `contract_comparison=UNKNOWN` tant qu'un acte humain ne relie pas l'offre à une version de contrat signé/mise au point ; aucune différence n'est calculée. Le nouvel acte P7 de passation ne crée ni commande, ni P6, ni `CaseP7Result` d'exécution, et n'affirme pas qu'il constitue un ordre de service.

**Preuve locale B1 :** un E2E HTTP/PostgreSQL prépare réellement un paquet, l'autorise P5, enregistre le WON, fige une condition ouverte, rejoue la commande, lit et télécharge par un Responsable affecté le document technique exact vérifié, refuse un Collaborateur sans affectation ou de profil Expert, vérifie le trigger append-only, l'absence d'acte commande/P7 résultat, et l'absence de données du snapshot financier dans la projection et le téléchargement. Vitest du panneau C07 **2/2 ciblés**, suite frontend **295/295**, typecheck/lint/build, Ruff ciblé et `git diff --check` verts ; build avec avertissement de chunk principal >500 kB. Aucune suite backend complète ni CUA navigateur exécutée ; aucune ouverture publique, aucun commit/push.


### CT31-15 — C1, événement contractuel sourcé lié à la passation B1

**AS-IS :** les actes de réception, préservation des droits et sortie contractuelle existent dans Pricing, ainsi que les versions de contrat/avenant et leur remplacement déclaré. Aucun événement OS/changement n'est directement lié au snapshot d'offre/passation B1 ; l'écart offre/contrat du snapshot B1 reste donc UNKNOWN.

**Implémentation locale :** un événement ORDER_OF_SERVICE, CHANGE_REQUEST, ADDENDUM ou SCHEDULE_CHANGE conserve sa source, ses pièces déclarées, sa date/heure reçue déclarée, son périmètre décrit, le snapshot B1 exact et, si connu, la version instrument contractuel exacte. Une version absente reste UNKNOWN. Aucun delta financier, délai juridique, effet d'ordre, mise à jour de P3 ou mutation du snapshot B1 n'est produit.

L'applicabilité au périmètre de la passation est un acte Patron append-only distinct. Sans cet acte, elle reste UNKNOWN. Le Patron peut enregistrer APPLICABLE_TO_HANDOVER, NOT_APPLICABLE ou NEEDS_CLARIFICATION ; ces états décrivent uniquement le lien humain avec cette passation, pas l'applicabilité juridique. L'acte référence la version contractuelle retenue, ses preuves et un delta humain DECLARED ou UNKNOWN. Le delta déclaré est une note revue par le Patron, non un calcul ; l'impact A1 initial reste intact.

Une action Patron append-only et ses références de preuve ne sont acceptées qu'après une revue courante APPLICABLE_TO_HANDOVER. Une date d'action est déclarée par l'acteur ; si elle manque, sa raison reste explicite. L'action est RECORDED, jamais considérée automatiquement comme exécutée, notifiée, payée ou juridiquement suffisante. P7 reste distinct de toute création d'OS.

**Preuve locale C1 :** E2E HTTP/PostgreSQL B1+C1 **2/2** : source et version, lien au snapshot B1, UNKNOWN avant revue, refus d'action avant applicabilité, revue Patron/rejeu, action+preuve/rejeu, refus rôle, lecture étrangère neutre, append-only des trois registres et migration upgrade/downgrade. Vitest C1 **1/1**, suite web **296/296**, typecheck/lint/build et Ruff ciblé verts ; avertissement de chunk principal Vite >500 kB. Suite backend complète et CUA non exécutées ; aucune ouverture publique, aucun commit/push.

### CT31-16 — Qualification Q1 préliminaire au 1er octobre 2026 (historique)

La qualification locale exécute A1 et B1/C1 dans des E2E séparés (**3/3** ciblés). Deux refus liés à UNKNOWN sont observés : lien A1 d’une preuve UNKNOWN et action C1 avant revue Patron (HTTP 422). Chaque tranche restitue ses références et preuves dans sa projection. Ce résultat ne démontre pas encore le transfert de l’identifiant A1 et de sa condition vers le snapshot B1 utilisé par C1 : les fixtures créent des Affaires distinctes. Q1 reste PARTIEL/ACTIVE jusqu’à une recette HTTP/PostgreSQL unique même-Affaire. Suite web **296/296**, lint et build verts ; suite backend complète au snapshot testé **2008/2013**, dont des écarts ciblés ont été corrigés ensuite sans rejouer la suite complète, et une violation de frontière application/infrastructure reste ouverte. Détails, limites et commande exacte dans le [rapport de qualification Q1](../00_Pilotage_et_audits/V3_1/Q1_QUALIFICATION_FIXTURES_LOCALES_2026-10-01.md). Pas de corpus client ni de comparaison concurrentielle ; aucun avantage mesuré, aucune ouverture publique, aucun commit/push.

Ce verdict est historique ; la recette même-Affaire et les gates ultérieures sont consignées dans [CT31-17 ci-dessous](#ct31-17--qualification-intégrée-q1-a1b1c1-au-2-octobre-2026).

### CT31-17 — Qualification intégrée Q1 A1/B1/C1 au 2 octobre 2026

Un seul E2E HTTP/PostgreSQL (`test_http_c1_keeps_unknown_until_patron_links_change_to_handover_and_records_action`) rejoue l’Affaire, son exigence DCE confirmée, le profil adopté, l’impact A1, la condition Patron ouverte, le paquet P5, l’attribution WON, le snapshot B1 et le changement C1. Le snapshot B1 expose les identifiants et révisions exacts DCE/impact et le profil/version/hash ; l’acte C1 référence le même snapshot. L’inconnu A1 refuse une liaison (HTTP 422) et l’action C1 est refusée avant revue d’applicabilité (HTTP 422). Les commandes d’impact/lien, issue/passation, événement C1, revue et action sont rejouées avec les mêmes identifiants ; aucune seconde intention n’apparaît. Après C1, la décision reste `CONDITIONAL_GO`, sa condition `OPEN`, et l’impact A1 `HUMAN_REVIEW_REQUIRED`.

Le scénario a révélé que le lecteur du dossier Patron et le snapshot B1 cherchaient `DecisionContextRecord.is_selected_final`, indicateur resté faux, plutôt que le lien racine `DecisionRecord.selected_final_context_id`. Les deux lectures utilisent maintenant l’identifiant exact du contexte sélectionné. Les modèles ORM ont été sortis des services d’application concernés : handlers transactionnels dédiés et ports/lecteurs avec adaptateurs SQLAlchemy filtrés par tenant/Affaire.

Preuves locales : tests ciblés A1/B1/C1, dossier Patron, tête Alembic et architecture **14/14**, puis recette renforcée **5/5** ; suite backend complète **2013/2013** sur PostgreSQL temporaire (une dépréciation Starlette/httpx). Web **296/296** en exécution isolée ; ESLint, TypeScript/build, Ruff ciblé, mypy sur 11 modules modifiés, import bootstrap et `git diff --check` verts. `ruff check .` reste rouge sur 327 constats de l’ensemble du dépôt, dont 190 sous `backend/app` et `backend/tests` ; les fichiers de cette tranche passent le contrôle ciblé. Aucune validation CUA, corpus client ou comparaison concurrentielle ; aucune conclusion juridique/financière, aucun P3 induit ni ouverture publique. Aucun commit ni push ; NO-GO public maintenu. Rapport détaillé : [qualification Q1 intégrée](../00_Pilotage_et_audits/V3_1/Q1_CHAINE_A1_B1_C1_INTEGREE_2026-10-02.md).


### CT31-18 — C08 : marge de base déclarée en lecture Patron

Les GET existants du brouillon et du rapport financier publié exposent additivement `margin_calculation`, après les contrôles Patron Admin/MFA/tenant/Affaire `FINANCIAL_PRIVATE`, avec `Cache-Control: no-store`. Le `summary` stocké et les lignes humaines `GROSS_MARGIN` restent des déclarations historiques; cette projection ne les réécrit pas et ne constitue pas un backfill.

Le calcul réutilise `calculate_cost_basis` sur les sommes entières `amount_minor` des lignes effectivement présentes pour les cinq entrées requises : `SALES`, `DIRECT_COST`, `OVERHEAD`, `SUBCONTRACTING`, `CONTINGENCY`. Une catégorie absente reste inconnue; une ligne de zéro est une déclaration explicite. Les quantités ne sont pas remultipliées et aucune conversion monétaire n’est introduite. `GROSS_MARGIN` et `FORECAST_CASHFLOW` ne sont pas des entrées de ce calcul. Le périmètre est `DECLARED_BASE_CATEGORIES`; il ne prouve pas la couverture économique exhaustive des coûts, réserves, partenaires ou risques de l’Affaire.

Le DTO fermé porte `state=CALCULATED|UNKNOWN`, `basis`, `missing_categories`, `basis_line_ids`, `total_cost_minor`, `gross_margin_minor`, `gross_margin_rate_bps`, `unknown_reason` et `rate_unknown_reason`. Les trois valeurs calculées sont nulles lorsque les catégories requises sont absentes ou les totaux invalides (`MISSING_BASE_CATEGORY` ou `INVALID_BASE_AMOUNT`). Avec des ventes explicitement nulles, la marge en centimes reste calculable mais le taux est nul au sens JSON (`null`, raison `ZERO_SALES`), jamais un zéro pour cent présumé. Les identifiants des lignes d’entrée appartiennent au rapport autorisé dont l’identifiant et la révision figurent dans la réponse.

La UI Patron affiche `UNKNOWN` en l’absence de cette projection, d’une catégorie source ou d’une représentation entière sûre; elle conserve les zéros explicitement déclarés. Le formatage des centimes et points de base utilise quotient/reste entiers, sans division flottante susceptible de perdre un centième. Une saisie de montant vide ou non représentable exactement est refusée avant l’API. Le rendu Collaborateur et Patron délégué n’expose ni brouillon ni montants.

L’état local du brouillon est lié à l’Affaire et à une génération de session (création/restauration/login/logout/expiration), avec contexte tenant/acteur/rôle; un renouvellement du jeton dans la même session ne change pas cette génération. Les réponses tardives d’un ancien contexte sont ignorées. Les intentions d’écriture inconnues gardent leur command/idempotency/correlation et leur révision originale pendant le retry de la même saisie; une nouvelle saisie est une nouvelle intention. Aucune donnée financière n’est persistée dans le stockage navigateur. Cette projection ne crée aucune décision et ne promeut aucune porte P3.

La recette locale `backend/tests/db/test_c08_margin_http_recipe.py` exige une `SMART_AO_TEST_DATABASE_URL` explicitement dirigée vers PostgreSQL jetable; elle peut exporter les réponses synthétiques dans `SMART_AO_C08_HTTP_PROOF` hors Git en mode `0600`. La même variable passée à Vitest active les tests de passerelle HTTP → React; ces deux tests sont explicitement sautés lorsque le fichier de campagne n’est pas fourni. Ils ne constituent jamais une source client ou live. Les tests backend sont lancés depuis la racine du dépôt, les tests web depuis `web/`.

### CT31-19 — C08 : frontière de lecture des scénarios privés

`PricingScenarioService.list_for_case` conserve le guard Patron Admin et soumet `PRICING_READ` à la politique existante avec classification `FINANCIAL_PRIVATE`, tenant et Affaire avant tout appel au reader. Un refus ne lit aucune projection et la route restitue `403 FORBIDDEN` générique. Le GET autorisé porte `Cache-Control: no-store`; aucune nouvelle fenêtre MFA n’est imposée à cette lecture. Les règles d’authentification et de step-up existantes demeurent applicables.

La qualification locale C08 exige désormais les cinq catégories de CT31-18 avant création d’un scénario depuis le snapshot `PUBLISHED` tenant/Affaire exact. Les sommes par catégorie doivent égaler ses scalaires figés; absence ou discordance reste `SCENARIO_SOURCE_UNKNOWN`. Les ventes source nulles et le taux indéfini après arrondi entier des ventes ajustées refusent une nouvelle création connue (`SCENARIO_RATE_UNKNOWN` pour ce dernier cas). Les helpers entiers et les transitions append-only existants demeurent les seules règles de calcul/cycle de vie.

Le GET ajoute `source_snapshot_id`, `source_basis_state=DECLARED_COMPLETE|UNKNOWN`, `source_basis_reason` et `currency_code` à la révision source enregistrée. Le reader résout le parent publié et ses lignes sous tenant/Affaire; une révision discordante ou un parent non résolu rend identité et devise nulles. Une source exacte peut rester visible même lorsque sa base déclarée est incomplète. Les scalaires historiques du DTO sont conservés pour compatibilité, sans validation rétrospective; l’état de qualification demeure séparé du cycle `DRAFT/SELECTED/ARCHIVED`. Aucun backfill ni réécriture de scénario ou transition.

La UI ne montre montant/taux que pour une base déclarée complète avec source exacte, devise et entiers représentables; sinon `UNKNOWN`. La lecture utilise une clé de génération de session/tenant/Affaire, masque immédiatement l’ancien contexte et ignore ses réponses tardives. Elle conserve un état d’erreur distinct d’une liste vide et propose un retry; seuls les Patron Admin rendent/lisent cette surface. Les deux façades de lecture utilisent le même contrôle `PRICING_READ`/`FINANCIAL_PRIVATE` avant le reader.

La recette PostgreSQL/JWT/HTTP C08 existante couvre création, replay, sélection/archivage et provenance stable, refus de base absente et UNKNOWN historique, tenant/rôle/MFA et absence d’effet P3. Son export synthétique optionnel alimente aussi PricingPanel et App : quatre tests de passerelle React sont explicitement sautés sans fichier fourni. Campagne du 05/10 : 245 backend et 363 web; couverture de 100 % sur qualificateur et reader, sans extrapolation au dépôt entier. L’export est éphémère hors Git et doit être recréé après changement de session. Aucune couverture économique exhaustive, confirmation externe ou ouverture publique n’est déduite.

### CT31-20 — EXP-05 : éligibilité documentaire des moyens proposés

La chaîne existante `EnterpriseDocumentRecord` → `EnterpriseCapabilityProofLinkRecord` → `EnterpriseCapabilityVersionRecord` → `CaseCapabilityProposalRecord` reste append-only. Chaque pièce est identifiée par son ID immuable et son SHA-256; chaque proposition garde les IDs exacts de capacité/version, l’Affaire, l’affectation et son locator déclaré. Une version plus récente ne remplace pas celle proposée. Aucun registre transverse, migration ni backfill.

Le GET Collaborateur `capability-assessments` ajoute par proposition `source_evidence_state=CURRENT|EXPIRED|UNKNOWN` et `source_evidence_evaluated_at`, calculés à la date serveur passée par le service après les autorisations et la vérification d’affectation. `validity_state` demeure la déclaration historique figée, séparée de cette éligibilité de lecture et du cycle natif. Les projections anciennes sans qualification restent `UNKNOWN`/null. Le GET porte `Cache-Control: no-store`.

Le reader résout en batch le tenant, la version exacte et son identité de capacité, le lien `SUPPORTS_CAPABILITY`, le document de la même entreprise et le registre d’upload `CLEAN` de même objet/document/type/SHA-256. Toutes les pièces liées doivent qualifier : absence, incohérence, non-validation, inactivité ou date future → `UNKNOWN`; lorsque la chaîne est qualifiée, une date expirée ou une déclaration documentaire `EXPIRED` → `EXPIRED`; sinon `CURRENT`. Les ensembles mixtes restent conservateurs (`UNKNOWN` prioritaire sur `EXPIRED`). Le délai d’admission de l’upload ne devient pas l’expiration d’un document déjà enregistré.

Les droits et le scope d’affectation existants demeurent applicables. Le Collaborateur reçoit uniquement ces deux nouveaux champs d’état/date, jamais IDs de pièces, hashes, noms de fichiers ou clés de stockage. La comparaison de hashes porte sur les métadonnées persistées; elle ne relit pas le blob, ne réauthentifie pas une pièce et ne prouve pas un scan antivirus actuel. La validation documentaire déclarée ne devient pas une confirmation externe authentifiée, une adéquation technique ou une disponibilité/réservation du moyen. Préparation/remise et P3 restent inchangés; cette projection ne remplace pas leurs gates.

La recette locale `backend/tests/db/test_exp05_capability_evidence_http_recipe.py` utilise uniquement PostgreSQL éphémère explicite, un clock de fixture et des métadonnées synthétiques `CLEAN`/validation déclarée. Elle recalcule le SHA-256 d’octets synthétiques connus, vérifie son lien exact en base et exerce les commandes/lectures HTTP existantes, retries, versions, dates, pièces absentes/mixtes/discordantes, refus tenant/affectation/rôle et append-only. Campagne du 07/10 : 104 tests backend, couverture reader 100 %, sans extrapolation au dépôt entier ni recette visuelle UI.

### CT31-21 — EXP-05 : réconciliation C09/C08 et preuve intégrée à réaliser

| Nature | Code et lecture existants | Ce que cela ne prouve pas |
|---|---|---|
| Consultation déclarée | C09 `REQUESTED`, locator/rationale, révision partenaire | Aucun envoi externe effectué |
| Réponse enregistrée | C09 `RECEIVED`, lien à demande facultatif, validité/exclusions/mandat déclaratifs | Aucune pièce versionnée/hash/authentification externe; locator seul reste preuve physique `UNKNOWN` |
| Valeur et comparaison | C08 prix/devise textuels, revue humaine de périmètre, rapprochement manuel de lignes | Aucun calcul de coût couvert, classement, réservation ou engagement induit |
| Engagement humain | Acte C09 `ENGAGEMENT_DECLARED` séparé, reçu courant exact, mandat reçu avec locator pour cotraitant | Ni validité juridique universelle ni confirmation externe authentifiée |

Les migrations `0118–0121`, handlers, bootstrap et routes sont présents. Les revues/lignes conservent leurs reçus et révisions exacts; remplacement d’un reçu ou d’une revue produit un signal d’obsolescence sans réécriture. `SAME_SCOPE_CONFIRMED` est une décision humaine de comparaison, pas une vérification de fichier. Le montant `SUBCONTRACTING` d’un rapport financier n’établit aucun partenaire engagé. `CO_CONTRACTOR` et son mandat déclaratif ne modélisent pas à eux seuls forme, membres/parts, solidarité et gouvernance d’un groupement; les `group_id` de rapprochement regroupent des postes, pas des personnes morales. Ces expositions métier restent non qualifiées.

**Preuve minimale cadrée, exécutée au 07/10 selon CT31-22 :** reprendre les routes existantes dans `AppRuntime` avec JWT et PostgreSQL synthétique explicite, sur une même Affaire et deux partenaires. Déclarer demande puis réponse, relire IDs/révisions/locators exacts, conserver `UNKNOWN` des dates/pièces/mandats absents; déclarer prix sans valeur calculée; enregistrer revue de périmètre puis lignes rattachées à sa révision exacte, quantités inconnues nulles. Ajouter nouveau reçu et nouvelle revue : historique préservé, flags de réévaluation et refus de nouvelles écritures sur références obsolètes. Déclarer séparément un acte Patron, avec refus du mandat inconnu de cotraitant; il ne devient pas confirmation externe. Pour chaque écriture, replay identique et conflit de révision, puis refus tenant/rôle et neutralité des références. Vérifier en base qu’aucune ligne du brouillon financier, décision/readiness P3, couverture, réservation ou envoi externe n’est produit automatiquement. La préparation de cette recette ne nécessite ni nouveau registre ni corpus réel.

**Écart préalable d’isolation — constat historique, fermé localement par CT31-22 :** le guard global de `DeclarePartnerOfferPriceHandler` vérifie l’UUID de déclaration avant le reçu tenant-scopé. Avec source inconnue identique, UUID de déclaration étranger connu → `409 …ID_REUSED`; UUID absent → `404 NOT_FOUND_OR_FORBIDDEN`. Le probe local démontre l’existence observable, sans lire de montant. Le test suivi `backend/tests/db/test_partner_offer_identity_audit.py` marquait initialement ce pattern `XFAIL`; il exige désormais strictement deux refus neutres, ainsi que succès sur source propre avec ID d’un autre tenant. CT31-22 ajoute le parcours JWT/AppRuntime complet. Les guards C09 et de revue présentaient des motifs analogues, désormais alignés sur le scope retenu selon CT31-22.

Réordonner le guard ne suffit pas pour les écritures utilisant une source propre valide; un filtre tenant seul laisse la contrainte de PK globalement unique. Le contrat d’identités et ses effets sur références/API/historique/contraintes doivent donc être cadrés avant une correction ou migration. Ce finding a ensuite été fermé dans le périmètre C09/C08 par les preuves de CT31-22; il ne qualifie pas l’isolation de tout le dépôt. Campagne d’audit historique : 50 backend passés + 1 XFAIL, 14 web ciblés. Correction et recette qualifiées ensuite selon CT31-22; NO-GO public maintenu.

### CT31-22 — C09/C08 : identité tenant/Affaire et provenance JWT qualifiées localement

Le contrat de stockage des quatre racines `CasePartnerEventRecord`, `PartnerOfferPriceDeclarationRecord`, `PartnerOfferScopeReviewRecord`, `PartnerOfferLineComparisonRecord` est `(tenant_id, case_id, UUID public)`. Les routes comportent déjà l’Affaire : ni UUID, payload, locator, révision ni référence historique n’est transformé. Les IDs internes des enfants restent serveur. Les guards de doublon et de réception/engagement opèrent dans ce même scope; la FK parent C09 et l’index partiel d’engagement incluent aussi l’Affaire. Les lectures et l’identity-map ORM ne fusionnent pas les valeurs répétées entre scopes. Les événements ont des IDs internes serveur, leurs données conservent l’Affaire.

La migration `20261007_0133` ne réécrit aucune ligne. Elle conserve FK composites enfants, uniques de révision et triggers append-only. Sous verrous DDL transactionnels, elle refuse un parent historique inter-Affaire avant changement; le downgrade refuse les UUID répétés entre scopes avant tout DDL et restaure sinon les anciennes contraintes. Aucun effacement ou renumérotation pour permettre un retour arrière. Les tests conservent byte-for-byte les JSON des lignes existantes sur upgrade → downgrade → re-upgrade et vérifient les refus atomiques. Verrous exclusifs et durée/volumétrie réelle restent non qualifiés hors PostgreSQL local jetable.

Le test d’oracle est strict, sans XFAIL : source inconnue → même404 pour UUID étranger connu ou absent. Une source propre valide accepte le même UUID utilisé ailleurs, avec réponse et replay normaux; deux écritures interscopes concurrentes peuvent réussir, une collision dans le même scope ne crée qu’un effet. Le contrat ne desserre ni rôle, membership, affectation, classification privée ni référence parent.

La recette `backend/tests/db/test_partner_c09_c08_http_recipe.py` passe réellement par AppRuntime/JWT et les routes existantes, sur deux tenants et deux Affaires du même tenant avec UUID identiques. Elle sépare demande déclarée, réception, prix textuel, revue humaine, rapprochement de lignes et acte d’engagement humain. Locators/reçus/révisions exacts sont conservés; dates, empreinte de pièce et quantités inconnues restent inconnues. Nouvelle revue à membres identiques et nouveau reçu rendent les lectures anciennes obsolètes sans réécriture; un changement de jeu de reçus requiert une nouvelle comparaison, selon le contrat natif. Un mandat inconnu de cotraitant ne permet pas la déclaration d’engagement. Ni comparaison, prix ou catégorie SUBCONTRACTING ne produisent engagement, coût couvert, réservation ou promotion P3; les actes humains ne deviennent pas des confirmations externes authentifiées.

Campagne du 07/10 : 84 tests backend ciblés élargis, dont 22 d’identités/migrations et deux variantes JWT; 44 web/API ciblés, typecheck/lint/build, Ruff et mypy ciblés verts. Source physique/antivirus/groupement juridique, recette navigateur et suites globales nouvelles restent hors preuve. Aucun code C1/C3/C4 modifié, nouvelle dépendance, corpus réel, VPS ou push; NO-GO public maintenu.

Complément du 08/10 : le transport web typé du POST existant de rapprochement de lignes est raccordé à `/api/v1/patron/cases/{case_id}/partner-offer-line-comparisons`; la commande humaine est désormais intégrée au panneau C08 existant. L’acte utilise une revue `SAME_SCOPE_CONFIRMED` courante et ses reçus exacts, démarre tous les champs en `UNKNOWN`, requiert motif et confirmation explicite, puis vérifie le reçu et la projection GET exacte. Une intention UNKNOWN reste figée au retry; 409 et toute relecture après reçu ne déclenchent que des GET. Tests web ciblés 12/12, suite complète 493/4 ignorés, typecheck/lint/build et Semgrep `p/security-audit` (22 règles/7 fichiers/0 finding) verts. Le navigateur réel n’a pas été qualifié; synthétique local seulement. Aucun calcul, import, réservation, engagement, confirmation externe ou effet P3.

### CT31-23 — C08 : publication humaine interne et relecture privée du même rapport

Le GET du rapport `PUBLISHED` expose additivement `aggregate_revision`, transmis depuis `FinancialReportProjection`/le snapshot existants, sans recalcul ni migration. Le transport web conserve des types distincts `DRAFT`/`PUBLISHED` et le reçu de publication; l’identité de commande et `expected_revision` sont fournis explicitement, sans nouvelle génération implicite au retry. Publication interne d’un snapshot privé : aucun envoi externe ou création de scénario.

Le hook/Panel financiers existants portent le parcours humain : avertissement de gel et rapport/révision exacts, clic de publication, puis GET indépendant du même objet publié. Un reçu n’est accepté qu’avec statut/code, command/idempotency et référence du rapport/révision attendus. Le GET contrôle tenant/Affaire via le serveur, puis côté consommateur l’Affaire, l’ID, l’état `PUBLISHED`, la révision exacte connue et la structure minimale nécessaire au rendu. Une réponse discordante est masquée. Un GET seul d’un rapport publié ne fabrique aucun reçu local de publication.

Résultat POST inconnu (transport/5xx ou conflit d’idempotence ambigu) : conserver la même intention et sa révision; bloquer édition et changement de rapport; retry explicite sans deuxième identité. Refus 400/401/403/404/422 ou `409 VERSION_CONFLICT` : aucun succès présumé, relecture du DRAFT avant nouvelle intention humaine. Une écriture de brouillon non résolue bloque la publication. Après reçu confirmé, une panne de GET ne retire pas la confirmation du reçu; seule la projection demeure indisponible et le bouton de reprise ne fait qu’un GET. Édition des lignes absente pour un `PUBLISHED`.

Données et intentions restent en mémoire et sont liées à la génération de session/contexte privé, Affaire et rapport; aucune persistance économique navigateur. Masquage immédiat au changement de scope, réponses tardives ignorées, double clic protégé avant l’await. Le bloc App demeure réservé au Patron Admin avec session/MFA/contexte existants; aucune nouvelle permission ou fenêtre MFA n’est inventée. La publication n’établit ni base de scénario admissible, ni couverture économique complète, engagement ou GO P3 : une base publiée incomplète conserve `UNKNOWN` et les refus serveur de création de scénario.

Preuves du 07/10 : source backend/transport qualifiés dans la campagne précédente de 45 tests JWT/HTTP/PostgreSQL jetable. Parcours React : web393 réussis/4 ignorés pendant la tranche, contrôles finaux ciblés après libellé/toolbar; typecheck/lint/build et Semgrep ciblé verts. Maquette Local Codex inspectée puis vrai App/hook/CSS exécutés dans Brave isolé, avec auth/API synthétiques uniquement; publication UNKNOWN → même retry → reçu confirmé/GET indisponible → reprise GET seule, source exacte/marge UNKNOWN, keyboard et masquage des rôles constatés. Ce navigateur ne prouve pas une authentification/API live; NO-GO public maintenu. Manifest/captures/fingerprints privés hors Git référencés dans le plan opérationnel.

### CT31-24 — C08 : création humaine privée depuis une source publiée relue

Réutiliser le POST de création et le GET des scénarios, sans route, calcul navigateur, migration ou sélection automatique. Le consommateur admin privé fournit une identité de commande/retry/scénario explicite, sept entiers bornés et une note humaine non vide; les ajustements sont également enregistrés dans les hypothèses. La source PUBLISHED doit être relue dans le même scope/Affaire : ID, révision persistée et devise exacts, base CALCULATED sans catégorie manquante et taux défini; publication seule ≠ éligibilité.

Après résultat inconnu, geler source et saisie et rejouer exactement la même intention; le double clic est bloqué synchroniquement. Refus définitif : aucune confirmation et nouvelle intention explicite après correction. Reçu technique contrôlé contre command/idempotency/scénario/version; aucune confirmation externe impliquée. La relecture GET vérifie source/révision/devise, base, type/clé, hypothèses sans ordre de clés JSONB et réserves/taux persistés. Reçu conservé si projection indisponible/discordante; reprise GET seule. Le scope privé masque immédiatement les données lors d’un changement de tenant/rôle/session/Affaire et ignore les réponses tardives. Identité de retry en mémoire seulement : après rechargement, relire l’historique avant toute nouvelle intention.

Preuves locales datées dans le plan : 412 web passés/4 ignorés, 45 backend JWT/PostgreSQL jetable; Brave desktop/mobile sur auth/API synthétiques, UNKNOWN/retry identique, reçu/relecture distincts, scénario DRAFT sans engagement/P3. Aucun corpus réel/VPS ou qualification serveur live par le navigateur; NO-GO public maintenu.

### CT31-25 — C08 : transitions humaines, scope Affaire et concurrence

Les POST existants `pricing-scenarios/{scenario_id}/selection` et `/archive` reçoivent un corps fermé : command/idempotency/correlation, transition_id, expected_version entier ≥1 et reason_code explicite (2–64 caractères A–Z/0–9/underscore). Le chemin choisit SELECTED/ARCHIVED; le corps ne porte ni tenant, état cible, montant ni source à réécrire. Reçu technique `PRICING_SCENARIO_TRANSITIONED`, ID scénario et version ≥2, événements et replay; il reste distinct de la projection GET et ne constitue pas un GO P3 ou un engagement.

Le service exige Patron admin, droits PRICING_WRITE/FINANCIAL_PRIVATE et MFA résolue par la frontière HTTP; il vérifie l’appartenance immutable tenant/Affaire/scénario via le reader existant **avant** le dispatcher, car un reçu réussi est rejoué sans réexécuter le handler. Le case_id de route est propagé dans le contexte serveur et contrôle aussi la requête transactionnelle. Les modèles de commande et le hash sémantique demeurent inchangés; aucun backfill ou migration. Scénario hors Affaire/tenant ou absent : même NOT_FOUND_OR_FORBIDDEN, y compris si la commande possède déjà un reçu dans son scope légitime.

Toutes les lignes immuables de scénario de l’Affaire sont verrouillées par UUID dans un ordre commun avant examen de la cible. Les lectures des derniers actes vérifient ensuite la version et l’unique sélection active; aucun verrou cible-puis-voisin opposé. Même version concurrente : un gagnant, VERSION_CONFLICT pour l’autre; deux sélections : un gagnant, SCENARIO_ALREADY_SELECTED. L’acte append-only incrémente la version sans modifier source/révision, hypothèses, montants ou ligne originale. ARCHIVED reste terminal; une archive historique ne transforme jamais sa base UNKNOWN en base qualifiée. Ce choix sérialise les scénarios d’une même Affaire et ses lectures/verrous croissent avec leur nombre; charge non benchmarkée.

Les transports web typés réutilisent ces routes : URLs encodées, champs explicitement projetés, identités/version/motif fournis par l’appelant, aucun makeId implicite ni retry automatique. VERSION_CONFLICT et refus métier sont renvoyés au consommateur : relire avant une nouvelle intention; transport inconnu/idempotence ambiguë ≠ refus certain. La UI qualifiée localement sous CT31-26 vérifie reçu et projection séparément, gèle son intention UNKNOWN et préserve les permissions/sources exactes; les boutons sont intégrés au panneau existant.

Qualification locale datée : backend élargi176/176 sur PostgreSQL tmpfs jetable, web414 passés/4 ignorés, transport39/39, gates ciblées et Semgrep0finding. Aucun corpus réel, VPS, recette navigateur nouvelle ou GO public.

### CT31-26 — C08 : UI des actes humains sur le scénario relu

Le hook et panneau C08 existants portent un acte inline distinct de la création. Préparer sélection/archive ne déclenche aucun POST : capturer le scénario, son état/version et les références source/devise telles que relues dans le scope Patron admin. Sélection UI disponible pour DRAFT avec base déclarée complète, source/révision/devise et taux connus; archive pour DRAFT/SELECTED, y compris historique UNKNOWN. ARCHIVED est terminal. Une source absente garde sa révision affichée UNKNOWN; aucun zéro source n’est inventé. Le motif codifié est explicitement saisi, fermé au contrat CT31-25.

La confirmation crée une seule intention/identité, conservée au retry UNKNOWN; source/champs/autres écritures C08 sont bloqués pendant son résultat inconnu ou sa relecture non vérifiée. Le reçu doit correspondre à command/idempotency/scénario, code et version attendue+1. Un reçu discordant laisse UNKNOWN. Le GET vérifie ID/source/révision/devise/version et état; une transition ultérieure autorisée peut être affichée comme état relu, sans effacer le reçu de l’acte antérieur. Panne/discordance GET conserve le reçu et propose GET seul. VERSION_CONFLICT/refus métier ne déclenche aucun retry : GET puis nouvelle préparation humaine depuis la version affichée.

Scope session/tenant/Affaire/rôle perdu : masque immédiat et réponses tardives ignorées. La création/publication humaine existante reste distincte; une sélection n’est ni une réservation, ni un engagement partenaire, ni une confirmation externe ou un GO P3. Aucun nouveau calcul, route, schéma ou backfill. Identités de retry en mémoire seulement : après rechargement/changement de scope, relire l’historique avant une nouvelle intention.

Preuves et limites dans le plan actif : web427/4 ignorés, backend176 indépendant sur PostgreSQL jetable; navigateur réel App avec auth/API synthétiques, UNKNOWN/retry identique, reçu/GET, archive v3, refus de scope, desktop/mobile/clavier. Le navigateur ne qualifie pas l’auth serveur live. NO-GO public maintenu.

### CT31-27 — EXP-05 : consommateur web des évaluations de capacité (qualifié localement le 08/10)

Contrat livré : `GET /api/v1/collaborator/cases/{case_id}/capability-assessments` accepte l’omission de `assignment_id`. Lorsqu’il est fourni, son contrôle exact reste inchangé. Sans lui, le reader existant résout l’unique affectation ACTIVE tenant/membership/Case, dans sa fenêtre temporelle et avec `PREPARATION_CAPABILITY_PROPOSE`. Le service réutilise l’ID résolu interne pour la lecture. L’unicité ouverte ACTIVE/SUSPENDED est garantie par l’index existant; SUSPENDED ne devient pas admissible. Bearer, Collaborateur, MFA, ReBAC/INTERNAL_OPERATIONAL et `Cache-Control: no-store` restent obligatoires. Aucun nouveau champ public, table, migration ou backfill.

AS-IS avant cette tranche : query obligatoire, aucun transport/panneau web; les tâches ne fournissaient pas l’affectation d’une proposition requirement-only. Insertion minimale : même port/reader/service/route, transport GET typé, hook calqué sur `useCaseResolution`, panneau dans la Revue Collaborateur. Risques contrôlés : choix arbitraire d’affectation, fuite privée, réponse tardive et date trompeuse.

Le hook lie session/tenant/rôle/Case, masque immédiatement l’ancien scope et ignore les réponses tardives. Sa projection conservée contient seulement `state` et `evaluatedAt`, jamais justification, locator, ID de proposition/capacité/version/affectation/pièce/upload, hash, filename ou clé storage. Énumération non prise en charge/Case étranger/enveloppe invalide : lecture refusée. État historique absent ou date absente/invalide : UNKNOWN; calendrier impossible et horodatage sans timezone refusés. Les timestamps valides sont affichés tels quels, précision incluse, comme **date d’évaluation**, jamais comme expiration ou fraîcheur garantie. États mixtes, liste vide, chargement et erreur restent distincts.

Le reader de preuve CT31-20 reste inchangé fonctionnellement : version exacte, lien SUPPORTS_CAPABILITY, même société/document/upload/type/SHA et état CLEAN persisté. CURRENT qualifie les métadonnées à l’évaluation; aucune relecture de blob, re-scan antivirus, disponibilité, réservation, adéquation, engagement, confirmation externe authentifiée ou effet P3 n’est déduit. Validity_state historique reste dans le DTO existant; le panneau ne l’assimile pas à une pièce vérifiée.

Preuves : 68 tests backend (route/facade/domaines/HTTP JWT/PostgreSQL/E2E), 449 tests web réussis et 4 facultatifs ignorés, typecheck/lint/build, Ruff/mypy, tête 0133, diff-check. Recette requirement-only sans tâche, compatibilité explicite/case-only, tenant/membership/Case/scope/date/état/rôle/MFA (STEP_UP_REQUIRED conservé), sources valides/expirées/absentes/mixtes et historique. Navigateur réel App avec auth/API **synthétiques** : 375/768/1440 px sans overflow, focus clavier solid, date microsecondes exacte, nul/UNKNOWN, vide/refus sans anciennes lignes, zéro commande métier et zéro erreur console. Local Codex OpenDesign terminé; la proposition confondait expiration et évaluation, corrigée lors de l’intégration. Impeccable : 4 constats préexistants dans le CSS, aucune refonte hors périmètre. Semgrep 1.179.0/p-security-audit : 99 règles/8 fichiers, zéro finding/erreur au retry après timeout initial.

Limites : suite backend globale non rejouée, aucun corpus réel/VPS/source live, pas de qualification axe/lecteur écran/CWV; warning Starlette/httpx et chunk 635,61 kB. Artefacts hors Git : `/home/noor/.local/share/smartao-proofs/exp05-means-20261008/`. Basic Memory absent des outils; reprise durable consignée dans le plan, miroir non synchronisé. A1 en attente, A2 générique HOLD, NO-GO public maintenu.

### CT31-28 — EXP-05 : audit de la proposition humaine de moyens (08/10)

**AS-IS.** POST `capability-proposals` et `capability-gaps` existent sous `/api/v1/collaborator/cases/{case_id}`. Bearer/MFA puis Collaborateur, INTERNAL_OPERATIONAL, action distincte PROPOSE/GAP_REPORT et affectation exacte ACTIVE/fenêtre/scope, contrôlés par la facade puis dans la transaction. DTO extra-forbid, texte borné et refus des données financières; source requirement et/ou task obligatoire. Proposition : capacité/version exactes du tenant, validity_state figé, justification humaine; pièce absente ne devient pas confirmation, le reader CT31-20 garde UNKNOWN. Écart : capacité facultative, pas de version de capacité dans ce contrat; nature/sévérité/motif/recommandation explicites. Il ne faut pas fabriquer un lien de version absent du contrat.

Reçu 201 puis 200/replayed sur retry identique, conflits d’idempotence 409. CommandDispatcher verrouille le reçu; contraintes fonctionnelles tenant-scopées empêchent des doublons persistés. Un doublon séquentiel peut être mappé 409 par le handler; une course SQL IntegrityError est convertie en erreur de persistance générique puis 422. Aucune preuve de concurrence réelle acquise ici; unicité ne prouve pas réponse HTTP stable. Les IDs d’acte calculés par uuid5 depuis command_id seul et leurs PK globales nécessitent aussi une recette de collisions multi-tenant avant exposition d’un formulaire. Ne pas déclarer ces collisions sûres sans preuve.

**Lectures autorisées.** Le GET capability-assessments restitue seulement des actes déjà enregistrés sous l’affectation; ce n’est pas un catalogue de versions disponibles à proposer. Le GET `/api/v1/patron/enterprise/companies/{company_id}/capabilities` est PATRON_ADMIN-only, inclut descriptions/usage_scope/proof_document_ids; aucun contournement, partage de cache ni élargissement de ce DTO au Collaborateur. Les tâches donnent leur source et affectation exactes mais ne couvrent pas requirement-only. Aucun transport/formulaire web trouvé pour les deux POST. Les UUID saisis ou une affectation arbitraire ne constituent pas un sélecteur autorisé.

**Finding démontré.** `_validate_source` filtre une exigence par tenant/id seulement. La tâche est filtrée par tenant/Case/assignment, mais aucune comparaison task.requirement_id/requirement_id n’est effectuée si les deux sont fournis. Sur PostgreSQL tmpfs dédié, clone complet d’une seconde chaîne consultation → DCE → analyse → observation → matérialisation → exigence dans le même tenant. Assertions : consultation et version DCE source diffèrent de celles de l’Affaire. Les deux services créent néanmoins la proposition et l’écart depuis cette exigence; lecture documentaire UNKNOWN. La reproduction montre un défaut de rattachement, pas une confirmation de source ni une preuve HTTP. Aucun fichier applicatif corrigé pendant cet audit; historique et écritures existantes restent inchangés.

**Risques / insertion / plan minimal.** Avant catalogue/formulaire, fermer le validateur partagé pour l’origine exigence/DCE/consultation/Case et la cohérence task/exigence, y compris source absente/obsolète. Réutiliser les parents et pointeurs existants; pas de registre, schéma, migration ou backfill. Les anciens actes restent append-only; un nouveau refus ne répare pas rétroactivement leur provenance. Ensuite qualifier identities/retries/concurrence; cadrer une lecture fermée de candidats dans le scope du Collaborateur avant tout transport UI. La tranche de provenance est corrigée; reste le cadrage identités/retries/concurrence du plan actif. Version sélectionnée explicite, jamais dernière version implicite. Aucun état documentaire CURRENT obligatoire inventé pour transformer une déclaration humaine en preuve vérifiée.

**Tests à ajouter / preuves avant formulaire.** Nominal requirement-only et task-only de la bonne Affaire/version; autre consultation et autre Case du même tenant, autre tenant, DCE applicable absent/rectifié/obsolète; task et requirement discordants, tâche hors affectation. Chaque refus : erreur neutre, zéro acte/événement/outbox et historique intact. Capacité/version discordantes/étrangères, inactive/future/expirée, pièce absente et UNKNOWN séparés de la déclaration. Rôle/MFA/affectation expirée ou suspendue/scope; retry identique après réponse inconnue, même clé autre intention, double clic/deux transactions, collisions d’identités inter-tenant avec source propre valide et source absente. Après reçu : GET seul; perte scope/session : réponse tardive ignorée. Future lecture de candidats : aucun pièce ID/hash/locator/filename/storage key/description sensible, cache privé no-store et choix de version exact; aucun engagement/réservation/disponibilité/confirmation externe authentifiée/P3.

**Preuves réalisées.** 35 tests existants (`test_collab_capability_commands.py`, `test_collaborator_capabilities_routes.py`, `test_collab_capability_facade.py`) passent, warning Starlette/httpx. Reproduction locale des deux services sur une base PostgreSQL explicite, Alembic upgrade tête 0133/downgrade base, conteneur sans volume supprimé. Artefacts/hashes hors Git : `/home/noor/.local/share/smartao-proofs/exp05-means-proposal-audit-20261008/`. Les chiffres 68 backend/449 web de CT31-27 sont une campagne précédente, non extrapolée à ce finding. Suites globales, web, Semgrep et concurrence non exécutés pour cet audit sans modification de code; aucune qualification du formulaire. Graphify consulté, Superpowers using/verification et ECC api-design appliqués. OpenDesign/Impeccable non requis avant direction UI; Basic Memory/Serena non callable, miroir non synchronisé. A1 en attente, A2 générique HOLD, NO-GO public maintenu.

**Correction et qualification du 08/10.** Le validateur partagé des deux POST charge maintenant l’Affaire du tenant, refuse Case inactive ou `dce_freshness != CURRENT`, exige une version applicable non nulle `ADMITTED/VERIFIED`, et vérifie qu’elle appartient à la consultation courante (lien courant; racine historique seulement en absence totale de lien; un historique sans lien courant est refusé). Requirement_id est filtré sur cette version exacte. Avec une tâche, le lecteur exige tenant/Case/affectation exacte et refuse un requirement_id explicite différent de `task.requirement_id`; en task-only, la source de la tâche est validée. Toutes les discordances répondent `NOT_FOUND_OR_FORBIDDEN`, sans écriture receipt/event/outbox ou acte. Pas de schéma, de backfill, de réinterprétation/écriture d’historique. CT31-20 continue à rendre UNKNOWN pour les pièces absentes/incohérentes; l’acte humain ne prouve pas la pièce.

TDD observé : les cinq groupes de régression (autre consultation, task/exigence discordantes, aucun DCE, DCE à revoir, historique sans lien courant) échouent avant le correctif car aucun refus n’est levé, puis passent après. API HTTP : les deux POST renvoient 404 neutre pour source d’une autre consultation, DCE absent/revu, task mismatch et lien consultatif sans courant; aucun acte n’est persisté. Qualification PostgreSQL tête 0133, upgrade/downgrade sur base jetable. Résultats frais : 35 tests app/domain/recipe et 37 tests API/facade/routes, Ruff+mypy, Semgrep 1.179.0/p-security-audit 79 règles/3 fichiers/0 finding. Warning Starlette/httpx.

**Qualification identités/retries/concurrence du 08/10.** L’API dérive `proposal_id`/`gap_id` de `(type, tenant_id résolu du bearer, command_id)` dans le contrat interne; le service recalcule cette identité tenant-scopée avant dispatch. Les deux tenants peuvent employer le même UUID de commande et recevoir deux actes aux UUID distincts. Les reçus génériques et leurs contraintes `(tenant_id, command_id)` / `(tenant_id, actor_id, command_type, idempotency_key)` restent inchangés. Le dispatcher conserve la relecture 200/replay et les refus d’intention discordante; une collision de `command_id` avec une nouvelle clé est désormais rendue 409 sur les POST concernés.

Preuves HTTP/JWT PostgreSQL tmpfs : une source étrangère est refusée 404 sans réserver l’identité; la source valide du tenant homonyme est ensuite acceptée 201. Proposals et gaps : retry identique 200/reçu exact, même clé/autre payload 409. Deux requêtes parallèles même intention → un 201 et un 200, une ligne/acte; même command_id avec clés distinctes → un 201 et un 409, un acte. Rejouées avec deux tenants partageant un command_id : chaque UUID d’acte distinct, aucune collision DB. Tests ciblés app/domain/API/facade/recipe **74/74**. Ruff et mypy propres; Semgrep 1.179.0, 79 règles/7 fichiers/0 finding/erreur. PostgreSQL éphémère explicite, tête 0133 et downgrade base; conteneur tmpfs supprimé. Deux warnings préexistants (Starlette/httpx, Pydantic alias); les suites globales ne sont pas extrapolées. Artefacts/hashes : `/home/noor/.local/share/smartao-proofs/exp05-means-identities-20261008/`.

Avant tout catalogue ou formulaire, cadrer la liste autorisée pour le Collaborateur : l’actuelle lecture entreprise est Patron_ADMIN-only et expose `proof_document_ids`. Aucun droit n’est élargi ici. Basic Memory n’est pas callable; reprise consignée dans le plan et l’index, miroir non synchronisé. A1 en attente, A2 HOLD, NO-GO public maintenu.



### CT31-29 — EXP-05 : décision de portée du sélecteur Collaborateur de moyens (08/10)

**AS-IS vérifié.** Le GET Patron `/api/v1/patron/enterprise/companies/{company_id}/capabilities` appelle `EnterpriseCapabilityService.read_capabilities`; `_authorize` exige `PATRON_ADMIN`, capability `ENTERPRISE_CAPABILITY_READ` et classification `PERSONAL_OR_ADMINISTRATIVE`. Sa projection contient IDs capacité/version, nom/résumé, titre/description, dates, usage_scope et `proof_document_ids`. Elle ne peut pas être raccordée telle quelle au Collaborateur. Le Collaborateur n’a actuellement que `PREPARATION_CAPABILITY_PROPOSE` pour un Case/tenant/affectation, `INTERNAL_OPERATIONAL`; cette permission ne vaut pas lecture du catalogue Patron.

**Projection minimale proposée (non autorisée tant que l’Owner n’a pas tranché).** Route séparée read-only sous l’Affaire Collaborateur, bearer + MFA, membership ACTIVE et résolution serveur de l’unique affectation ACTIVE tenant/membership/Case/fenêtre; tenant, version DCE/applicable consultation et scope contrôlés par le serveur. DTO fermé, `no-store`, sans paramètre `company_id`, `assignment_id` implicite, ou cross-tenant. Allowlist à valider : `capability_kind`, `name`, `version.title`, `version_number`, `valid_from`, `valid_until`, `validity_state` calculé pour l’instant serveur, `source_evidence_state` et `source_evidence_evaluated_at` de la version exacte. `capability_id` et `version_id` ne seraient présents que pour l’intention POST côté transport et jamais affichés/rendus à l’écran. Retirer `summary`, `description`, `usage_scope`, `proof_document_ids`, IDs de pièce/upload, hash, locator, filename, stockage et contenu de justificatif. UNKNOWN/mixte conserve UNKNOWN; expiré ne se transforme pas en réservation ou inéligibilité automatique. Le clic humain choisit une version explicite; aucun POST auto ni effet P3.

**Décision Owner reçue le 08/10/2026.** Le propriétaire a autorisé l’exposition de `name`/`title` au seul GET case-scopé et à l’affectation ACTIVE/MFA, avec IDs capacité/version conservés uniquement au transport. `PERSONAL_OR_ADMINISTRATIVE` reste la classification; aucun droit général Enterprise n’est créé et aucun changement Patron n’est fait. `summary`, `description`, `usage_scope`, `proof_document_ids`, données de pièce/personnelles restent exclus.

**Livraison 08/10.** `GET /api/v1/collaborator/cases/{case_id}/capability-candidates` résout l’affectation côté serveur sur `PREPARATION_CAPABILITY_PROPOSE`, consulte l’unique compagnie tenant et retourne une liste DTO fermée sans query company/assignment. `source_evidence_state/evaluated_at` réutilisent l’évaluation de pièces existante; liens mixtes -> UNKNOWN; absence de compagnie -> liste vide. `validity_state` indépendant de preuve, échéances déclarées conservées. IDs ne figurent pas dans l’UI. Cache no-store. Sélection uniquement locale, réinitialisée au changement Case/session; aucun POST, stockage ou acte.

Preuves : recette backend/API PostgreSQL **75 passed**, tenant/Case/rôle Patron/MFA, contenu JSON exact, absence de champs privés, 14 états pièce, UNKNOWN sans source, liens mixtes sans doublon. Vitest complet **469 passed, 4 skipped**; typecheck, eslint, build, Ruff/mypy verts; Semgrep **99 règles, 14 fichiers, 0 finding**. Artefact Local Codex `/home/noor/.local/share/smartao-proofs/exp05-means-candidates-20261008/`, preview HTTP 200, od lint P0/P1/P2 = 0; detector Impeccable 4 lignes de styles préexistants, aucun finding sur nouveaux fichiers. La surface UI n’a pas été contrôlée dans un vrai navigateur : CUA ne dispose d’aucun navigateur callable.

Limites : tests backend globaux non rejoués. Le chunk front de production dépasse 500kB (640.90 kB); warning build non corrigé, hors scope. Warnings Starlette/httpx et Pydantic Field.alias historiques. Basic Memory non callable; le plan/index portent la reprise, miroir non synchronisé. Aucun corpus réel/VPS, modification C1/C3/C4, migration, push ou déploiement; NO-GO public maintenu. La sous-tranche suivante est l’intégration du formulaire après conception OpenDesign Local Codex et lecture/revue exacte du requirement/task source dans l’Affaire.

### CT31-30 — EXP-05 : préparation du POST humain de proposition de moyens (08/10)

Le POST existant `/api/v1/collaborator/cases/{case_id}/capability-proposals` conserve la capacité et la version exactes (`capability_id`, `capability_version_id`), la source requirement/task validée par le handler contre la version DCE actuellement applicable, et la justification humaine obligatoire. Aucun `source_locator` n’est requis ou fabriqué par le nouveau formulaire; UNKNOWN documentaire reste indépendant de l’acte humain. Le champ `assignment_id` du corps devient facultatif de façon additive : le service réutilise `require_active_assignment` pour résoudre l’affectation unique ACTIVE par tenant, membership, Case, dates et action autorisée; l’ID résolu est injecté uniquement dans la commande serveur avant dispatch. L’ancienne entrée explicite reste prise en charge. Le handler refuse fail-closed une commande interne sans affectation résolue.

Le transport web `proposeCapability` accepte les IDs de commande, idempotence et corrélation générés une fois par l’intention, sérialise le même corps sur retry et n’invente aucune identité. Aucun `assignment_id` ni `source_locator` n’est envoyé par la nouvelle UI. L’API résout l’affectation côté serveur et vérifie le requirement/task sous la version DCE applicable.

**UI locale livrée 08/10.** Le panneau Collaborateur consomme les candidats, le reading DCE keyé à Case/session et les tâches du même Case. Il expose les seules exigences du DCE `CURRENT/ADMITTED/VERIFIED` et les tâches reliées à ces exigences; une source UNKNOWN reste qualifiable comme source sans être promue. Le Collaborateur sélectionne une capacité/version exacte, une seule exigence ou tâche, une justification (1–2 000 caractères) et confirme explicitement. Sélection et préparation n’envoient aucun POST. Le reçu technique exact ou HTTP 409 déclenche uniquement le GET `capability-assessments`; l’échec de cette lecture propose seulement son retry. Les autres refus connus ne lancent pas de GET. Après réponse POST inconnue, champs et IDs sont conservés en mémoire dans le scope Case/session actif, et seul le rejeu de la même intention est permis; aucune nouvelle intention ni GET automatique. Un changement de session/Case masque les anciennes données et perd ce retry en mémoire; un changement de DCE dans le même scope garde visible l’intention UNKNOWN figée. Aucun stockage navigateur, réservation, engagement, confirmation externe ou effet P3.

Preuves : recette HTTP/PostgreSQL tmpfs **21/21**, incluant omission d’`assignment_id`, `requirement_id` sans tâche, refus foreign/absent/obsolète/task mismatch, UNKNOWN sans source, concurrence/rejeu idempotent et zéro `CaseCapabilityProposalRecord` après les seuls GET initiaux. Vitest web complet **485 passés, 4 ignorés**; typecheck, build et ESLint verts; Semgrep 1.179.0 `p/security-audit` **0 finding / 10 fichiers / 99 règles**; `git diff --check` vert. Impeccable detect relève quatre warnings de styles/typographie préexistants dans `styles.css`, aucun sur le nouveau composant. Le build signale un chunk 654.49 kB (>500 kB). Aucun changement backend de production, migration ou dépendance.

OpenDesign Local Codex a produit le prototype et ses notes dans le projet existant; ses 35 tests locaux déclarés sont simulés et ne prouvent pas l’intégration. Le run a renvoyé `entry_missing` et aucune preview, même si le fichier est récupérable. Ni Cloud ni BYOK. Les tests DOM de cette campagne ne prouvent pas les flèches natives, le lecteur d’écran ni le reflow réel; la qualification navigateur locale et ses limites sont consignées ci-dessous. Basic Memory n’est pas callable; plan/index/cahier mis à jour mais miroir non synchronisé. A1 en attente, A2 HOLD, NO-GO public maintenu.

**Qualification navigateur du 08/10/2026 — qualifiée localement sur données synthétiques.** Chromium 141 headless isolé, App Vite `4173` et API in-memory `8765`. Le compte résout `actor_kind=COLLABORATEUR`, MFA validée et contexte confirmé; le sous-profil d’affichage est neutralisé uniquement dans le mock. L’exigence/task du DCE courant sont visibles et la provenance documentaire reste `UNKNOWN`. À 1440×900 et 390×844, aucun débordement horizontal; Tab indique le focus candidat, Space sélectionne requirement et ArrowDown task. Aucun POST avant la confirmation explicite. Le mock enregistre l’effet synthétique puis répond 500 JSON : App `UNKNOWN`, un seul POST, aucun GET d’évaluations additionnel. Le clic Retry explicite rejoue le corps et les command/idempotency/correlation IDs identiques (sans `assignment_id`/`source_locator`), reçoit le 200 puis fait le GET `capability-assessments` seul. Une intention distincte reçoit 409, avec de nouveaux IDs, puis le même GET seul. Le journal synthétique final contient POST 500/200/409 et trois GET d’évaluations (lecture initiale, reçu, conflit); runtime exceptions 0. Une première simulation de fermeture socket sans headers a révélé que Chromium pouvait rejouer la requête sous le niveau Fetch; elle a été exclue de la preuve qualifiée et remplacée dans le mock seulement par le scénario 500 après effet.

Le MCP local a été vérifié directement sur stdio : initialize, `tools/list` (30 outils) et `list_pages` (1 page isolée) réussis. L’alias Codex exposé `mcp__chrome_devtools__list_pages` échoue encore sur `/opt/google/chrome/chrome` absent; le parcours UI a donc été piloté via CDP direct. Aucun cookie/token lu ni trafic externe observé. L’API reste synthétique : cette qualification ne prouve ni le backend live, ni un corpus réel, ni l’atomicité/persistance de production. Les suites applicatives, Semgrep, axe/lecteur d’écran et performance ne sont pas rejoués, car aucun code produit n’a changé. Logout 404 est un comportement du mock consommé par son `finally`, non un défaut produit établi. Captures et rapport : [qualification locale EXP-05](../05_Qualification_locale/EXP-05_QUALIFICATION_NAVIGATEUR_FORMULAIRE_2026-10-08.md); résumé privé mode 0600 `/home/noor/.local/share/smartao-proofs/exp05-browser-20261008/evidence.json`, SHA-256 `e8525fdd0511db7cd1fbc833918c5c8488a2504c12db1ea2409f46cfaafea60f`. A1 attente, A2 HOLD, NO-GO public maintenus.

### CT31-31 — PHASE 5 / EXP-05 : C10 réponse, audit AS-IS et cadrage (08/10)

**Autorités réconciliées.** CT2-125 exige de retrouver les engagements mesurables du mémoire par preuve, coût, responsable, sanction éventuelle et passation. PF2-083 maintient C10 dans la surface existante; PF2-084 interdit à l’IA de signer/déposer ou d’effacer un inconnu. M2-236/321 exigent le contexte, les droits, la validité et l’état de vérification des contenus réutilisés. M2-324 distingue paquet candidat, signature, autorisation, export, tentative humaine et preuve externe. M2-286/287 maintiennent les engagements et le dépôt comme gestes contrôlés.

**AS-IS observé dans le WIP local.** `PreparationPackageRecord` est unique par tenant/Affaire/affectation/version DCE; `PreparationReadinessRecord` évalue exigences/tâches mais n’est pas un plan éditorial exigence→section→preuve. `CreateTechnicalResponseDraftCommand` accepte une liste de codes de section et des UUID `source_refs`; le handler valide le document source du package, mais ne résout pas ces UUID vers des faits/preuves, puis stocke un contenu générique listant seulement les sections et « Sources internes ». L’objet de brouillon est versionné/haché, mais son texte ne constitue pas la réponse prévue.

La revue est append-only et versionne sa décision, mais `PreparationReviewRecord.target_document_id` référence `GeneratedTechnicalDocumentRecord`; elle ne cible pas le `TechnicalResponseDraftRecord`. Le snapshot peut être créé lorsque la readiness n’est pas bloquée et qu’un document généré existe, sans exiger une revue acceptée. Il inclut `documents[:1]` et les métadonnées du dernier brouillon par `draft_id`, sans son hash ni son contenu. La transmission `TRANSMITTED_TO_PATRON` est un acte interne append-only. En aval, `PrepareSubmissionPackageHandler` reconstruit un autre manifeste depuis le dernier document généré, des preuves entreprise validées et, en mode `FULL`, le dernier rapport financier publié; il ne reprend pas l’identité du snapshot transmis ni une revue exacte de brouillon. P5 est néanmoins séparée, Patron/MFA et liée à version/hash du manifeste; l’export contrôle l’autorisation et inscrit `external_submission=NOT_PERFORMED`. L’acte `HUMAN_DEPOSIT_ATTEMPT` reste `UNKNOWN`.

**Lecteurs, UI et preuves existantes.** Les GET préparation exposent readiness, documents générés et métadonnées des brouillons; la lecture Patron des brouillons renvoie ID/version/état/sections/sources sans contenu. `CollaboratorWizardPanel` saisit les sections et UUID de sources; `PreparationReviewPanel` affiche ces métadonnées mais demande la revue par ID/version du document généré. `SubmissionPanel` est un bloc distinct : identifiants/révision saisis, aperçu de manifeste, P5, export et acte de preuve manuelle. Les composants ne relient pas encore un plan, le contenu/hachage du brouillon, sa revue et le snapshot exact. Les tests existants `test_preparation_review.py`, `test_preparation_snapshot_transmission.py`, `test_submission_package.py`, les tests API correspondants et `SubmissionPanel.test.tsx` couvrent des sous-parcours (commandes/restrictions, idempotence/append-only, manifest/P5/export); leur présence n’est pas un résultat de campagne et n’a pas été rejouée pendant cet audit.

**Premier écart local.** Il manque le plan versionné unique qui relie les exigences de la version DCE exacte aux sections de réponse et aux faits/preuves autorisés et réutilisables. Les références libres du brouillon, le texte placeholder et la revue d’un autre objet rompent cette chaîne avant transmission. La décision de cadrage est de prolonger `PreparationPackage` et ses sources existantes; ne pas créer de registre générique, de nouvelle destination UX, de génération automatique d’engagement ou de route externe de dépôt.

**Critères de preuve pour la tranche minimale.**

1. Plan tenant/Affaire/affectation/DCE exact, versionné et relisible; chaque ligne relie exigence et ancre DCE à une section et à des références source résolues. L’absence, l’ambiguïté, l’expiration, le retrait ou l’obsolescence garde `UNKNOWN` et ne devient jamais une preuve utilisable.
2. Fait réutilisable borné par propriétaire, contexte, classification, validité, source/version et hash exacts; ne pas injecter marge, trésorerie, coûts ou données personnelles hors finalité dans un candidat Collaborateur.
3. Brouillon append-only dérivé du plan et des seules références admissibles, avec contenu relisible et hash recalculable. La revue humaine référence le même ID/version/hash; correction ou changement de source produit une nouvelle version et rouvre la revue.
4. Snapshot complet qui refuse l’absence de revue acceptée ou toute discordance de DCE, plan, source, contenu ou révision; manifest hash exact. Transmission reste interne au Patron, idempotente, tenant-scopée et optimistement concurrencée; aucune transmission externe.
5. Préparation P5 distincte portant sur ce snapshot/manifeste exact; MFA, décision et intégrité vérifiées avant export. Export signifie téléchargement seulement. Tentative de dépôt humaine demeure séparée; sans pièce externe relue, état `UNKNOWN` et NO-GO public.
6. Tests PostgreSQL/API synthétiques : nominal complet; source étrangère/absente/expirée/retirée et DCE rectifié; payload financier/personnel interdit; revue sur mauvaise version; snapshot sans revue; reçu de transmission rejoué et conflit; relecture exacte après redémarrage; aucune écriture P3, aucun appel réseau de dépôt, aucune pièce réelle.

**Tranche suivante :** test rouge PostgreSQL/API et contrat de plan versionné adossé au package et à la version DCE, avant création de brouillon. Aucun code ou test n’a été modifié/exécuté pendant cet audit; Basic Memory non callable dans cette tâche, miroir à resynchroniser. Travail local synthétique seulement; NO-GO public maintenu.

### CT31-32 — PHASE 5 / EXP-05 : C10, plan de réponse versionné (08/10)

**Insertion.** La migration `20261008_0134` ajoute `preparation_response_plans`, versions append-only d’un plan logique par `PreparationPackageRecord`; chaque version enregistre le `dce_version_id` exact, le contenu canonique, `plan_sha256` et un hash séparé du manifeste interne de preuves. Le package reste l’ancre tenant/Affaire/affectation. Aucun registre transverse n’est créé.

`POST /api/v1/preparation/{package_id}/response-plans` et `GET` sont case/tenant/affectation scoped. Le plan relie chaque requirement DCE exact à une section fermée et, facultativement, à une proposition de capacité déjà liée à cette exigence/affectation. Le lecteur réutilise les évaluations Enterprise existantes. `UNKNOWN` est écrit si la source manque explicitement, si l’exigence n’est pas confirmée ou si l’état de preuve reste inconnu. `SOURCES_CURRENT` exige exigence confirmée, version proposition/capacité courante et preuves `VALIDATED` dont l’upload enregistré est `CLEAN` à l’évaluation.

**Limite de preuve.** Cette tranche lit les métadonnées existantes du scan, de la vérification humaine et du SHA-256 inscrit; elle ne relit pas le blob et ne recalcule pas son SHA-256. `SOURCES_CURRENT` qualifie donc la cohérence des métadonnées à l’instant serveur, pas les octets encore présents, leur authenticité externe ou leur adéquation factuelle. Le manifeste privé fige les IDs de pièce et hashes enregistrés pour le plan, sans les exposer au Collaborateur. Avant de réutiliser le contenu dans le mémoire, la tranche de génération doit relire la pièce autorisée et recalculer son SHA-256; tout blob indisponible ou discordant conserve `UNKNOWN` et bloque le brouillon.

Les IDs de documents et leurs SHA-256 exacts sont conservés uniquement dans `source_evidence_json` avec `source_evidence_sha256`; la projection Collaborateur ne les renvoie pas et est `no-store`. Le SHA-256 du plan public couvre le lien requirement/section/proposition/version et ses états. Un ID de source fourni mais absent, étranger ou discordant reçoit un 404 neutre; une source expirée reçoit 422; un package dont le DCE a changé ou une révision concurrente reçoit 409. Un plan inconnu ne devient jamais une base de brouillon.

`CreateTechnicalResponseDraft` refuse l’absence de plan et toute dernière version `UNKNOWN`. Avant tout stockage, le handler revérifie la version DCE applicable, les exigences confirmées, la version capacité et l’état/hash exact des preuves; les sections et propositions du POST doivent correspondre au plan. La ligne de brouillon conserve une FK vers le `plan_id/version` exacts. Les brouillons historiques restent lisibles avec ces deux colonnes nulles; les nouvelles commandes doivent référencer un plan current. Le texte de réponse reste encore un placeholder et le Collaborator Wizard ne crée/lit pas encore le plan; sa prochaine tranche intégrera l’UI existante avant le rendu réel du contenu.

**Preuves locales.** TDD : le test API PostgreSQL a échoué avant le contrat/modèle, puis a validé création/relecture, versions, rejeu, hash du plan, snapshot privé exact de preuves, UNKNOWN de l’exigence malgré une preuve documentaire CLEAN, source absente/étrangère/expirée, DCE obsolète, absence de brouillon et garde append-only. La campagne ciblée Préparation/capacités/API/architecture/schema/ops est **94/94**; campagne finale backend complète : **2170 passés, 0 échec**, 2 warnings préexistants (Starlette/httpx, Pydantic `Field.alias`). Migration complète upgrade/downgrade passée jusqu’à la tête `20261008_0134`. Ruff ciblé passe, mypy passe sur 10 fichiers, Semgrep 1.179.0 `p/security-audit` : **79 règles, 15 fichiers, 0 finding**.

**Limites.** Aucun changement web/UI ni navigateur, aucune génération de contenu réel depuis le plan, revue du brouillon, snapshot de transmission, action P5, export ou dépôt n’ont été exécutés. Le draft legacy est désormais fail-closed sans plan `SOURCES_CURRENT`; le formulaire web doit être raccordé avant usage. La vérification d’octets est différée à la génération de contenu. Aucune donnée/corpus réel, VPS, effet P3, déploiement, commit/push ou GO public; NO-GO public maintenu. Basic Memory non callable, miroir non synchronisé.

### CT31-33 — PHASE 5 / EXP-05 : C10, plan de réponse dans le Collaborator Wizard (09/10)

**Insertion locale.** Le plan unique est intégré dans le panneau « Complétude et production » de `CollaboratorWizardPanel`; aucune route, surface C00–C16, migration ni dépendance n’a été ajoutée. Le Wizard réutilise la lecture DCE et les projections Collaborateur existantes pour présenter les exigences, les propositions déjà liées à chaque exigence et les libellés versionnés des candidats autorisés. La sélection exigence → section → proposition est humaine et couvre toutes les exigences de la version DCE courante. Les commandes n’envoient ni affectation ni données financières.

**Plan, preuve et brouillon.** L’écriture et la relecture utilisent uniquement le POST et le GET existants `/{package_id}/response-plans`. L’ID logique du plan est conservé pour ses nouvelles versions, y compris après un changement DCE; plusieurs IDs logiques, une Affaire/package discordants, une lecture DCE non courante ou une exigence source étrangère bloquent la commande. Les IDs de proposition/document, hashes, locators, noms de fichiers et clés de stockage ne sont pas rendus. Les identités command/idempotency/correlation et draft sont créées une fois et gardées identiques après un résultat inconnu. Après un reçu, l’UI n’émet pas un second POST et relit le plan; après conflit, elle relit avant une nouvelle intention. `UNKNOWN`, un état de requête non résolu ou une sélection locale différente de la version relue désactive la création du brouillon.

Le gate du brouillon exige le package/Affaire/version DCE exacts, tous les mappages DCE relus, `SOURCES_CURRENT`, des propositions/version/preuves résolues et courantes, et un document `TECHNICAL_RESPONSE` existant. L’interface n’affiche ni l’ID/version/hash du plan. Le backend reste l’autorité finale et revalide révision package, DCE, propositions et manifeste. Comme indiqué en CT31-32, `SOURCES_CURRENT` qualifie toujours les métadonnées de preuve conservées; cette tranche ne relit aucun blob et ne recalcule aucun SHA-256.

**Preuves synthétiques locales.** Suite Web complète : **502 réussis, 4 ignorés, 66 fichiers**. Avertissement non bloquant du test runner : `Not implemented: navigation to another Document` (jsdom). Les nouveaux tests couvrent le transport GET/POST, les identités stables plan/brouillon au retry, le gate `UNKNOWN`/`SOURCES_CURRENT`, le choix explicite de l’exigence/section/proposition, le masquage des IDs et le réemploi de l’ID logique après changement DCE. Typecheck, ESLint et build passent. Semgrep 1.179.0 `p/security-audit` : **22 règles sur 6 fichiers, 0 finding**. Le lint statique OpenDesign a rendu **0 finding**.

**Limites.** Les routes sont simulées par Vitest; aucune recette backend live/PostgreSQL, aucun corpus réel et aucun blob client n’ont été utilisés. Le prototype OpenDesign a été généré, corrigé et relu côté source. La recette réelle locale du 09/10 utilise Helium 0.19.2.1/Chromium 155, le MCP DevTools existant et son profil temporaire isolé. Le vrai Panel/hook/CSS est relu à 1440×900 et 390×844; API/auth restent synthétiques. Aucun navigateur intégré à l’application hôte n’est nécessaire à ce workflow explicitement demandé par l’Owner. Impeccable retrouve quatre motifs globaux CSS/Inter non introduits par les nouveaux sélecteurs; le build signale un chunk principal de **691,16 kB** au-dessus de 500 kB. Pas de génération réelle de contenu, revue, snapshot, transmission, P5, dépôt, effet P3, déploiement ou ouverture publique; NO-GO public maintenu. Basic Memory non callable, miroir non synchronisé.

**Complément de qualification Helium (09/10).** La recette a révélé un état READING persistant après succès du retry; le test de régression échouait avec READING au lieu de IDLE. Une transition minimale termine la requête après relecture réussie; le statut du plan/source conserve son autorité. Les 65 tests ciblés passent, ainsi que les 502 tests Web (4 ignorés), typecheck/lint/build; Semgrep 1.179.0 ciblé : 22 règles/2 fichiers/0 finding. Souris système, Tab/Entrée, focus visible, desktop/mobile sans débordement et captures inspectées. Double clic sans second POST; retry identique sans assignment_id, reçu suivi de GET seuls, aucune écriture automatique du brouillon; 409 et source partielle restent UNKNOWN/bloquants. Zéro erreur console observée dans les scénarios. Preuve privée `/home/noor/.local/share/smartao-proofs/c10-helium-20261009/evidence.json`, SHA-256 `418c9667492cb776f31996ca8b0c94b7cbbb6858e02ad7b3857758f75a906c54`; les empreintes des sources WIP relues sont incluses. Ces preuves ne qualifient pas HTTP/auth serveur, source réelle ou P3.

### CT31-34 — PHASE 5 / EXP-05 : C10, sources relues et trame de réponse hachée (09/10)

Le brouillon est créé par le POST existant `response-drafts`. Le handler relit le plan le plus récent et en vérifie la version DCE, l’Affaire, l’affectation active, chaque exigence, version de capacité, proposition et manifeste privé. Il recalcule les SHA-256 canoniques du plan/manifeste, puis résout dans le tenant les seuls documents reliés aux propositions exactes, admis `VALIDATED`/`CLEAN`. Pour chaque pièce, le stockage privé est relu en flux; la taille et le SHA-256 des octets sont comparés aux empreintes du registre d’entreprise, de l’upload `CLEAN` et du manifeste. La lecture agrégée est bornée à 150 Mo; toute erreur, pièce absente/altérée/hors scope, scan ou métadonnée non admissible garde `UNKNOWN` et bloque avant écriture et acte. Aucun hash, UUID de pièce, locator, nom de fichier, clé stockage, contenu binaire ou réponse d’extraction n’entre dans le corps collaborateur.

Une trame non financière est assemblée depuis les sections et propositions de la révision exacte : libellé de capacité, titre/version et nombre de pièces relues par exigence, puis emplacement explicite pour la contribution humaine. Elle ne transforme pas un titre ou une pièce en fait métier confirmé. L’objet reste append-only/versionné, le stockage calcule son SHA-256 et la ligne référence le `plan_id`/version exacts par FK déjà existante. Les pièces de preuve sont relues avant l’écriture. Pas de migration, route, dépendance ni effet P3.

**Preuves locales.** TDD rouge puis vert : digest local borné et recalculé; la recette PostgreSQL jetable crée une trame depuis un `CLEAN` synthétique, vérifie le hash du contenu stocké et son rattachement exact. Après modification ou suppression des octets, POST renvoie 422 `RESPONSE_PLAN_UNKNOWN`, sans second brouillon ni incrément de révision. Le contrôle interdit aussi les contenus financiers. Suite ciblée : 28 tests backend réussis, un warning Starlette/httpx; Web complet : 504 réussis, 4 ignorés sur 66 fichiers; typecheck/lint/build, Ruff et mypy ciblés passent. Semgrep 1.179.0 `p/security-audit` : 99 règles/13 fichiers/0 finding.

**Limites et frontière.** Les états `CLEAN`, octets, horodatages et scanner sont synthétiques/préremplis par le test; aucune vraie soumission d’upload ou exécution ClamAV n’est qualifiée. Aucun corpus réel, OCR, backend/auth live, relecture d’un blob client, revue Patron, snapshot, transmission, P5, dépôt ou GO public. Le brouillon ne contient qu’une trame soumise à rédaction et revue humaines. Avertissements inchangés : jsdom `Not implemented: navigation to another Document`; bundle Vite 692,16 kB >500 kB. Basic Memory non callable, miroir non synchronisé; NO-GO public maintenu.

### CT31-35 — PHASE 5 / EXP-05 : C10, revue humaine exacte, versions corrigées et gate de transmission (09/10)

**Contrat.** Une revue C10 est liée par tenant au `draft_id`, `version` et `content_sha256` d’une ligne `TechnicalResponseDraftRecord`; elle continue à garder `target_document_id` pour la compatibilité historique. La migration additive `20261009_0135` ajoute les références de version/hash, une FK composite vers la version de brouillon et une contrainte qui exige le triplet entier ou son absence. Les revues et corrections précédentes restent append-only et aucune ligne historique n’est backfillée.

Le GET Patron `/api/v1/preparation/{package_id}/response-drafts` relit chaque objet depuis le stockage privé, recalcule son SHA-256, refuse les octets absents/altérés, les textes financiers et les contenus supérieurs à **100 ko**, puis expose le contenu exact/hash avec `Cache-Control: no-store` et la révision de package nécessaire à l’intention. Le GET package Collaborateur garde ses projections sans contenu, hash de brouillon, clé ni locateur. Une seule demande de revue C10 est admise par tenant/package/`draft_id`/version/hash; un second identifiant d’intention ne crée pas une seconde revue append-only. Une décision et une correction doivent correspondre à la dernière version du `draft_id`, au hash enregistré et à l’objet dont les octets ont été relus. L’ancienne revue documentaire reste supportée.

Une décision Patron `CORRECTIONS_REQUIRED` permet de soumettre un texte corrigé explicitement humain via l’acte de correction. Avant écriture, l’application vérifie encore le plan C10 courant et relit les sources de ce plan. Elle refuse un contenu corrigé supérieur à **100 ko**, l’écrit sous une nouvelle clé/version immuable du même brouillon, recalcule le hash et append une correction liée à l’ancienne cible ainsi qu’une nouvelle révision `REQUESTED` liée à la version corrigée. Le reçu référence la revue et le nouveau brouillon; l’outbox émet les événements de correction du brouillon, de réouverture de la revue et de correction humaine. Aucun texte ni hash de pièce source n’est déduit d’un locator. Le Patron doit ensuite décider cette nouvelle cible exacte; la correction ne l’accepte jamais automatiquement.

Le snapshot C10 refuse plan absent/non courant, absence de brouillon latest issu du plan courant, revue manquante/multiple/non acceptée/hash divergent, ou stockage du brouillon discordant. Son manifeste conserve brouillon ID/version/hash, plan ID/version et revue ID/révision/état exacts. La transmission interne compare ces mêmes références à leur état courant et relit les octets du brouillon; une nouvelle version ou revue rend le snapshot non transmissible. Les contrôles historiques de readiness et de document gardent leur priorité sur les packages sans plan C10. Le statut `READY` issu de l’acceptation humaine autorise la création du snapshot; aucun dépôt externe, P5 ou effet P3 n’est produit.

**Preuves synthétiques locales.** Recette PostgreSQL/HTTP avec octets et pièces de source synthétiques : GET Patron rejette un objet brouillon altéré (422) puis montre le contenu après restauration; demande hash discordante et second review ID pour la même cible refusés (422); snapshot pending refusé sans nouvel enregistrement; cycle demande → `CORRECTIONS_REQUIRED` → version 2 append-only/hash relu → événements draft/review/correction persistés → nouvelle revue exacte → acceptation → manifeste snapshot exact → transmission interne. Les assertions vérifient que correction et version initiale demeurent présentes, la cible de correction reste v1 et la revue acceptée cible v2; la base et stockage sont jetables. Ciblés backend C10/revue/snapshot/routes **43/43**, dont migration `0135` upgrade/downgrade; UI revue **2/2**; Web complet `pnpm exec vitest run --testTimeout=30000` **505 réussis, 4 ignorés sur 66 fichiers**. Typecheck, ESLint, build, Ruff et mypy ciblés (6 fichiers) passent. Semgrep 1.179.0 `p/security-audit`: **79 règles sur 7 fichiers, 0 finding**.

**Limites.** Les octets, états CLEAN, scanner, acteurs et appels restent synthétiques; aucun fichier client, corpus réel, authentification/backend live, VPS ou confirmation externe n’est qualifié. Le premier run complet Web avec timeout par défaut a expiré trois tests C08/C12/C13 hors de cette tranche; les trois passent isolément à 30 s, puis la suite complète passe avec cette limite explicite. Build : chunk principal **693,78 kB** (>500 kB). Impeccable detect relève quatre motifs déjà présents globalement dans `styles.css`/Inter et aucun nouveau sélecteur. OpenDesign Local Codex était configuré et son daemon actif, mais les appels MCP ont échoué `Transport closed`; aucun prototype visuel n’est présenté comme réalisé. Basic Memory non callable et miroir non synchronisé. NO-GO public maintenu.

#<a id="ct31-36"></a>

## CT31-36 — PHASE 5 / EXP-05 : C10, création de snapshot, transmission et relecture Patron du reçu exact (09/10)

Le Collaborator Wizard expose désormais une action humaine « Créer le snapshot complet » dans le bloc de transmission existant. L’ID est saisi ou généré localement; le POST existant reçoit le `snapshot_id`, la révision package relue et une identité commande/idempotence/correlation stable. Si le résultat HTTP est inconnu, le Wizard garde l’intention et ne régénère aucun identifiant à la reprise; l’erreur HTTP définitive déclenche la relecture du package avant une nouvelle intention. Le reçu POST affiche l’ID, la version agrégat et la commande. Le POST de transmission reste distinct, avec son propre ID et une intention retry stable; le reçu visible inclut snapshot et révision package de transmission. Les commandes serveur appliquent toujours le gate C10 de CT31-35 : plan C10 courant et revue acceptée de chaque ID/version/hash exacts avant snapshot, puis absence de nouvelle version/revue et relecture d’octets avant transmission. Aucune valeur saisie dans le navigateur ne peut contourner ces contrôles.

**Canal Patron / relecture persistée.** Une route GET `/api/v1/preparation/{package_id}/transmissions` est ajoutée à la surface Préparation existante. Elle accepte `PATRON_ADMIN` ou `PATRON_DELEGATE` seulement selon `PREPARATION_REVIEW_DECIDE`, tenant/package-scopés; `Cache-Control: no-store`. Elle ne liste que les snapshots ayant une ligne de transmission `TRANSMITTED_TO_PATRON`. Pour chacun, le lecteur recalcule SHA-256 sur la sérialisation canonique du manifeste et vérifie l’identité snapshot/package/Affaire; il relit les deux reçus durables dans `command_receipts`, vérifie tenant, type/résultat, command ID, idempotency key, aggregate refs et event IDs contre les agrégats transmis. Une absence ou discordance produit `PREPARATION_RECEIPT_UNKNOWN`, sans fabriquer un reçu. La projection contient snapshot ID/version/état/horodatage/manifeste/hash, transmission ID/état/horodatage et les corps exacts des reçus (révisions inclues). La Revue Patron présente un panneau read-only « Snapshots transmis au Patron », manifestes figés et reçus/révisions exacts. Aucun nouveau modèle ni migration; tête Alembic reste `20261009_0135`.

**Preuves locales.** TDD rouge sur GET initialement absent puis vert. Recette PostgreSQL/HTTP C10 : création/acceptation du brouillon v2, snapshot v1 lié au hash/revue exacts, transmission package revision 9; une seconde instance d’application relit le reçu de snapshot (aggregate revision 1), le manifeste et le reçu de transmission identiques. GET Collaborateur=403, GET Patron autre tenant=404, GET `no-store`; tests de routes reçus et corps de POST vérifient identities stables. Backend ciblé **27/27** (C10, handlers snapshot et routes); Web complet `pnpm exec vitest run --testTimeout=30000 --maxWorkers=1` **509 réussis, 4 ignorés sur 66 fichiers**; Wizard/Panel/Revue/API/App ciblés **116 réussis, 2 ignorés**. Typecheck, ESLint et build passent; bundle principal **699,66 kB** (>500 kB). Ruff et mypy ciblés passent; Semgrep 1.179.0 `p/security-audit`, **79 règles sur 3 fichiers/0 finding**.

**Réconciliation technique du 09/10.** Le contrat runtime et le runbook annonçaient encore 0134 malgré le graphe à 0135 : le test schema-head rouge a confirmé la dérive, puis passe après correction. La contrainte C10 du triplet ID/version/hash permettait un hash NULL (un CHECK PostgreSQL accepte UNKNOWN); la migration 0135 encore locale/non publiée et les deux modèles sont corrigés avec `target_content_sha256 IS NOT NULL`. Deux régressions lisent le CHECK réellement migré et vérifient les sept triplets partiels/invalides, tout en acceptant l’historique entièrement NULL et le triplet complet. Rouge observé sur les deux tables avant correction, puis recette C10/schema/ops 47/47. Toute base jetable déjà migrée avec l’ancienne définition 0135 doit être reconstruite pour cette preuve; aucun schéma métier existant n’est modifié. Les appels C10 réutilisent le tenant UUID exact du package autorisé. Le contrôle global et ses limites sont consignés dans le plan, sans nouvelle autorité produit.

**Limites.** Tout l’environnement, les octets, les rôles synthétiques et les reçus de test sont locaux; aucune donnée client, API/auth live, VPS, effet P3, P5, export, portail externe ou GO public. La recette navigateur Helium n’a pas pu démarrer : le bridge DevTools local annonce un binaire Chromium Playwright absent, tandis que le bridge Chrome stable ne trouve pas `/opt/google/chrome/chrome`; le registre MCP Codex mentionne Helium, mais aucun viewport/navigateur n’a été qualifié et aucun screenshot n’est revendiqué. Impeccable retrouve les quatre motifs globaux CSS/Inter antérieurs et aucun nouveau sélecteur. Basic Memory CLI/MCP non callable, miroir non synchronisé; NO-GO public maintenu.

<a id="ct31-37"></a>

## CT31-37 — PHASE 5 / EXP-05 : audit P5 depuis le snapshot C10 transmis exact (09/10)

**Périmètre et snapshot inspecté.** Audit READ-ONLY du code, contrats publics, routes, permissions, modèles et tests au HEAD local `8f0b3ad1ece52f3ff7881a00019465401c79665a`, branche `codex/reconcile-smartao-20261009`, arbre propre; tête Alembic/runtime `20261009_0135`. Aucun code produit, route, migration ou UI modifié. Autorités : PF31-03/04/07/08, PF2-074/084, M2-317/318/324, CT31-35/36. P5 reste un acte humain distinct; `AUTHORIZED` ne signifie ni export déclenché, ni dépôt effectué, ni réception externe authentifiée. PF31-11 impose la direction Cytd pour les évolutions UI ultérieures.

**AS-IS confirmé.**

| Frontière | Contrat vivant / protection | Écart ou limite |
|---|---|---|
| Préparation → Patron | GET `/api/v1/preparation/{package_id}/transmissions` : snapshots transmis, ID/version/hash canonique, brouillon/plan/revue exacts, reçus durables vérifiés, tenant/package, `no-store` | Le lecteur reste disponible; Submission ne le consomme pas |
| Préparer le candidat | POST `/api/v1/patron/preparation/{preparation_package_id}/submission-packages`; `PrepareSubmissionPackageRequest/Command` : ID package, révision, mode et motif candidature; readiness non bloquée, P3 via lecteur Decision, preuves entreprise, version append-only | `PrepareSubmissionPackageHandler.execute` choisit le dernier `GeneratedTechnicalDocumentRecord` et, en FULL, le dernier financier PUBLISHED; aucun snapshot/transmission ni brouillon/revue C10 lu |
| Manifeste Submission | Schema 2, identités préparation/Affaire/DCE, scope, readiness, entrées technique/prix/preuves; SHA-256 serveur, stockage privé/montants exclus, `external_submission=NOT_PERFORMED` | Aucun lien source ID/version/hash vers le snapshot C10 transmis. Le hash du manifeste Submission n’est pas celui du manifeste Préparation |
| P5 | POST `/api/v1/patron/submission-packages/{id}/authorize`; command/idempotency/correlation, authorization_id, version attendue, motif; intégrité canonique serveur, P3 courant, refus version/second acte, autorisation append-only avec hash exact du paquet | Pas de source C10 dans le contrat; pas de hash de lecture client attendu. La preuve existante lie P5 au paquet Submission, pas au snapshot C10 relu |
| Droits effectifs | `SUBMISSION_AUTHORIZE`, tenant, membership ACTIVE, `FINANCIAL_PRIVATE`; autorisation/export exigent MFA récente (politique actuelle 15 minutes) | Bien que certains services/handlers listent PATRON_DELEGATE, la politique FINANCIAL_PRIVATE refuse tout acteur autre que PATRON_ADMIN. Ne pas élargir un droit par cette tranche. GET manifeste et prepare n’ajoutent pas de demande explicite MFA récente |
| Export | GET `/api/v1/patron/submission-packages/{id}/export`; autorisation ID/version/hash exigée, P3 revérifié, ZIP privé `no-store`, audit/events/outbox, aucun dépôt | Lit les octets du document généré legacy; pas de relecture C10 ni recalcul du hash des octets techniques après `storage.read`. Aucun export réseau automatique dans ce code; les workers restent hors audit |
| UI existante | `SubmissionPanel`/`useSubmissionActions`, transport typé; UUID/version saisis, GET aperçu, motif P5, identités stables au rejeu identique | Le handler UI peut envoyer P5 sans imposer l’aperçu exact, les champs restent modifiables après erreur réseau, le reçu met `submissionAuthorized=true` sans GET de rapprochement. La stabilité de l’intention entière/scope et les refus C10 ne sont pas prouvés |

**Premier écart local retenu : origine exacte C10 absente de Submission.** Un snapshot transmis et revu existe dans Préparation, mais le candidat P5 peut être reconstruit avec d’autres références. Ne pas afficher « autorisation du snapshot C10 transmis exact » ni considérer le parcours intégré qualifié. Les deux manifestes ont des natures différentes : conserver un lien d’origine explicite, pas prétendre que leurs hashes sont identiques.

**Points d’insertion et tranche minimale proposée, non implémentée.** Réutiliser la commande/route de préparation Submission, les snapshots/transmissions existants et `manifest_json` pour une origine C10 fermée (ID/version/SHA-256 du snapshot, transmission et références brouillon/plan/revue exactes résolues côté serveur). C10 exige une source transmise vérifiée et courante; absence, étrangeté, hash discordant, nouvelle révision DCE/plan/brouillon/revue ou octets indisponibles maintiennent UNKNOWN/refus avant candidat/acte. Un namespace canonique versionné dans le manifeste peut éviter une nouvelle table; le contrat exact doit être fermé et testé avant code, sans registre générique, backfill ou fausse origine pour l’historique. Les paquets legacy conservent leurs références et protections; leur origine C10 non établie reste UNKNOWN. Adapter ensuite lecture/P5 et bytes exportés sur la même source, sans exposer P5 C10/export comme qualifiés tant que les octets exacts revus ne sont pas maîtrisés. FULL/candidature seule, prix, preuves entreprise, P3, rôles et MFA ne sont pas contournés.

**Tests à ajouter avant la réalisation.**

1. Rouge PostgreSQL/API C10 : préparer sans snapshot transmis exact doit refuser sans nouveau candidat/reçu/action; legacy valide reste compatible.
2. Nominal : source transmise relue, hash recalculé, IDs/révisions/hash de snapshot/brouillon/plan/revue conservés dans le candidat; lecture après nouvelle AppRuntime identique.
3. Refus neutres tenant/package/Affaire, rôle/MFA, source absente ou non transmise, manifest/hash/bytes altérés, DCE/plan/brouillon/revue obsolètes; aucune seconde écriture. Les liens historiques restent lisibles avec UNKNOWN d’éligibilité.
4. Retry identique et concurrence : un candidat/acte par intention; collisions d’identités inter-tenant sur source absente et valide à qualifier, pas seulement filtre tenant. Version/hash de lecture discordants refusés.
5. P5 humain : sélection/relecture et motif explicites, corps complet/IDs gelés après UNKNOWN; reçu/409 puis GET seulement, nouvelle intention après relecture sur conflit, changement Case/session invalide l’intention locale. Source/manifeste exacts, absence d’effet P3 et aucune action/export automatique.
6. Export futur : octets SHA-256 du brouillon revu exact, source courante/autorisation du même candidat; indisponibilité/discordance bloque avant archive. Un téléchargement ne devient jamais dépôt; tentative humaine reste UNKNOWN sans pièce externe vérifiée.

**Preuves rejouées, bornées.** Sur PostgreSQL 16 tmpfs dédié sans volume, URL/flag jetable explicites, 8 fichiers backend (Submission paquet/Decision/evidence/signature, Préparation snapshot/transmission et C10 HTTP/PostgreSQL, routes correspondantes) : **117/117**, 61,59 s, 1 warning Starlette/httpx. Web `SubmissionPanel` et `useSubmissionActions` : **19/19**, 2 fichiers, 6,60 s. Gouvernance/cahiers/schema-head : **5/5**. Ces recettes prouvent les sous-parcours existants et leurs refus/rejeu/append-only; elles ne prouvent pas la liaison C10→P5 absente du code. Les autorisations/ZIP de tests utilisent seulement des rôles et octets synthétiques; aucune action métier réelle, worker SMTP/signature/portail, blob client, corpus réel ou VPS lancé. Aucune recette navigateur, suite globale ou nouveau scan logiciel revendiqué dans cet audit documentaire. NO-GO public maintenu.

## Contrats techniques complets conservés — CT2

Ces chapitres font partie du présent cahier actif : **il n'est pas nécessaire d'ouvrir les archives pour disposer de ce détail**. Les identifiants CT2-xxx donnent des ancres uniques. Les exigences métier/techniques sont conservées ; les titres, dates, mentions de promotion et références de version du texte intégré indiquent sa provenance. Ils ne rétablissent pas une ancienne autorité. Les dispositions de consolidation V3.1 en tête gouvernent les conflits et l'ordre de livraison. « À valider », candidat, validation externe ou report ne signifient jamais capacité livrée.

### Accès aux chapitres intégrés

- [CT2-001 — SMART AO — CAHIER TECHNIQUE D’EXÉCUTION](#ct2-001)
- [CT2-002 — v2.1 — Dérivé du MASTER métier v2.0 et du Product Freeze v2.0 actif](#ct2-002)
- [CT2-003 — 0. Mandat, statut et règle de sécurité documentaire](#ct2-003)
- [CT2-004 — 0.1 Pourquoi cette version existe](#ct2-004)
- [CT2-005 — 0.2 Règle de précédence pendant la transition](#ct2-005)
- [CT2-006 — 0.3 Mandat Codex — READ-ONLY / AUDIT FIRST](#ct2-006)
- [CT2-008 — 1. État technique de référence à préserver](#ct2-008)
- [CT2-009 — 1.1 Architecture générale](#ct2-009)
- [CT2-010 — 1.2 Invariants techniques existants à ne pas affaiblir](#ct2-010)
- [CT2-011 — 1.3 Doctrine de modification](#ct2-011)
- [CT2-012 — 2. Principes architecturaux non négociables v2.0](#ct2-012)
- [CT2-013 — 2.1 Métier et preuve](#ct2-013)
- [CT2-014 — 2.2 Temps et temporalité](#ct2-014)
- [CT2-015 — 2.3 Exactitude financière et contractuelle](#ct2-015)
- [CT2-016 — 2.4 Reproductibilité](#ct2-016)
- [CT2-017 — 3. Bounded contexts et frontières v2.0](#ct2-017)
- [CT2-018 — 3.1 Contextes existants à conserver / enrichir](#ct2-018)
- [CT2-033 — 3.2 Nouveau bounded context logique : Contract & Rights](#ct2-033)
- [CT2-035 — 3.3 Regulatory Knowledge — référentiel transversal, pas moteur juridique autonome](#ct2-035)
- [CT2-036 — 4. Modèle de données conceptuel v2.0](#ct2-036)
- [CT2-037 — 4.1 Regulatory Profile](#ct2-037)
- [CT2-041 — 4.2 Contrat et hiérarchie](#ct2-041)
- [CT2-046 — 4.3 Pénalités et sanctions](#ct2-046)
- [CT2-049 — 4.4 Préservation des droits](#ct2-049)
- [CT2-052 — 4.5 OS, modifications et travaux supplémentaires](#ct2-052)
- [CT2-054 — 4.6 Règlement des comptes, réception et DGD](#ct2-054)
- [CT2-056 — 4.7 Résiliation et substitution](#ct2-056)
- [CT2-058 — 4.8 Assurance](#ct2-058)
- [CT2-060 — 4.9 HSE et prérequis d’exécution](#ct2-060)
- [CT2-062 — 4.10 Engagement mesurable](#ct2-062)
- [CT2-064 — 4.11 Circuit de paiement](#ct2-064)
- [CT2-066 — 4.12 Obligations post-réception](#ct2-066)
- [CT2-068 — 4.13 Autorisations et dépendances tierces](#ct2-068)
- [CT2-070 — 5. Carte d’Engagement de l’Affaire — projection centrale Patron](#ct2-070)
- [CT2-071 — 5.1 Nature](#ct2-071)
- [CT2-072 — 5.2 Interdiction du score opaque](#ct2-072)
- [CT2-073 — 5.3 Anatomie technique d’une ligne Patron](#ct2-073)
- [CT2-074 — 5.4 GO sous conditions](#ct2-074)
- [CT2-075 — 6. Applicabilité et moteur de règles sûr](#ct2-075)
- [CT2-076 — 6.1 Deux moteurs à ne pas confondre](#ct2-076)
- [CT2-079 — 6.2 DSL / règles](#ct2-079)
- [CT2-080 — 6.3 Invalidation](#ct2-080)
- [CT2-081 — 7. Hiérarchie contractuelle et dérogations](#ct2-081)
- [CT2-082 — 7.1 Graphe de contrat](#ct2-082)
- [CT2-083 — 7.2 Règle de conflit](#ct2-083)
- [CT2-084 — 7.3 Dérogations](#ct2-084)
- [CT2-085 — 8. Calculs déterministes critiques](#ct2-085)
- [CT2-086 — 8.1 Pénalités](#ct2-086)
- [CT2-087 — 8.2 Prix / actualisation / révision](#ct2-087)
- [CT2-088 — 8.3 Délais de droits](#ct2-088)
- [CT2-089 — 8.4 Cash-flow](#ct2-089)
- [CT2-090 — 8.5 Exposition portefeuille](#ct2-090)
- [CT2-091 — 9. Sécurité, droits et classification des nouvelles données](#ct2-091)
- [CT2-092 — 9.1 Classifications minimales](#ct2-092)
- [CT2-093 — 9.2 Patron](#ct2-093)
- [CT2-094 — 9.3 Collaborateur](#ct2-094)
- [CT2-095 — 9.4 Experts](#ct2-095)
- [CT2-096 — 9.5 Administrateur et support](#ct2-096)
- [CT2-097 — 9.6 IA](#ct2-097)
- [CT2-098 — 10. Contrats d’application et idempotence](#ct2-098)
- [CT2-099 — 10.1 Principe](#ct2-099)
- [CT2-100 — 10.2 Familles de commandes à supporter](#ct2-100)
- [CT2-101 — 10.3 Rejeu](#ct2-101)
- [CT2-102 — 11. Concurrence et cohérence transactionnelle](#ct2-102)
- [CT2-103 — 11.1 Optimistic concurrency](#ct2-103)
- [CT2-104 — 11.2 Édition concurrente](#ct2-104)
- [CT2-105 — 11.3 Outbox](#ct2-105)
- [CT2-106 — 12. IA / RAG / règles métier — séparation stricte](#ct2-106)
- [CT2-107 — 12.1 Pipeline obligatoire](#ct2-107)
- [CT2-108 — 12.2 Extraction contractuelle](#ct2-108)
- [CT2-109 — 12.3 Réglementation](#ct2-109)
- [CT2-110 — 12.4 Génération documentaire](#ct2-110)
- [CT2-111 — 13. Document intelligence, locators et tableaux](#ct2-111)
- [CT2-112 — 13.1 Sources critiques](#ct2-112)
- [CT2-113 — 13.2 Locator](#ct2-113)
- [CT2-114 — 13.3 Tableurs](#ct2-114)
- [CT2-115 — 14. Rectificatifs et invalidation ciblée](#ct2-115)
- [CT2-116 — 14.1 Graphe de dépendance](#ct2-116)
- [CT2-117 — 14.2 Candidate invalidation](#ct2-117)
- [CT2-118 — 15. Passation P7 renforcée](#ct2-118)
- [CT2-119 — 15.1 Paquet minimal](#ct2-119)
- [CT2-120 — 15.2 Acceptation](#ct2-120)
- [CT2-121 — 16. Frontend / UX — impacts obligatoires](#ct2-121)
- [CT2-122 — 16.1 C05 — À résoudre](#ct2-122)
- [CT2-123 — 16.2 C07 — Décision](#ct2-123)
- [CT2-124 — 16.3 C08 — Prix](#ct2-124)
- [CT2-125 — 16.4 C10 — Réponse](#ct2-125)
- [CT2-126 — 16.5 C12 — Résultat et passation](#ct2-126)
- [CT2-127 — 16.6 HOME Patron / Carte d’Engagement](#ct2-127)
- [CT2-128 — 17. APIs et projections — règles de contrat](#ct2-128)
- [CT2-129 — 17.1 Projections](#ct2-129)
- [CT2-130 — 18. Migrations et stratégie de données](#ct2-130)
- [CT2-131 — 18.1 Règle générale](#ct2-131)
- [CT2-132 — 18.2 Backfill](#ct2-132)
- [CT2-133 — 18.3 Réversibilité](#ct2-133)
- [CT2-134 — 19. Observabilité et audit métier](#ct2-134)
- [CT2-135 — 19.1 Événements à journaliser](#ct2-135)
- [CT2-136 — 19.2 Corrélation](#ct2-136)
- [CT2-137 — 19.3 Métriques techniques](#ct2-137)
- [CT2-138 — 20. Failure modes et reprise](#ct2-138)
- [CT2-139 — 20.1 Panne IA](#ct2-139)
- [CT2-140 — 20.2 Source réglementaire indisponible](#ct2-140)
- [CT2-141 — 20.3 Import DCE partiel](#ct2-141)
- [CT2-142 — 20.4 Conflit utilisateur](#ct2-142)
- [CT2-143 — 20.5 Timeout externe](#ct2-143)
- [CT2-144 — 21. Tests — contrats obligatoires](#ct2-144)
- [CT2-145 — 21.1 Test matrix générale](#ct2-145)
- [CT2-146 — 21.2 Recettes métier REC-29 à REC-45](#ct2-146)
- [CT2-164 — 21.3 Recettes techniques supplémentaires](#ct2-164)
- [CT2-175 — 22. Golden DCE / corpus de qualification technique](#ct2-175)
- [CT2-176 — 23. Plan de construction proposé après audit](#ct2-176)
- [CT2-177 — T0 — Audit de traçabilité et caractérisation](#ct2-177)
- [CT2-178 — T1 — Fondation preuve/applicabilité](#ct2-178)
- [CT2-179 — T2 — Contrat et dérogations](#ct2-179)
- [CT2-180 — T3 — Sanctions et préservation des droits](#ct2-180)
- [CT2-181 — T4 — OS / modifications / règlement des comptes](#ct2-181)
- [CT2-182 — T5 — Assurance / HSE / engagements / paiement](#ct2-182)
- [CT2-183 — T6 — Carte d’Engagement Patron](#ct2-183)
- [CT2-184 — T7 — Passation P7 renforcée](#ct2-184)
- [CT2-185 — T8 — REX et calibration](#ct2-185)
- [CT2-186 — 24. Plan de PR Codex — règles](#ct2-186)
- [CT2-187 — 24.1 Interdits](#ct2-187)
- [CT2-188 — 24.2 Forme d’une PR](#ct2-188)
- [CT2-189 — 24.3 Séquence préférée](#ct2-189)
- [CT2-190 — 25. Dépendances et choix technologiques](#ct2-190)
- [CT2-191 — 25.1 Principe](#ct2-191)
- [CT2-192 — 25.2 Moteur de règles](#ct2-192)
- [CT2-193 — 25.3 Calendriers juridiques](#ct2-193)
- [CT2-194 — 25.4 Document parsing](#ct2-194)
- [CT2-195 — 26. Critères de performance](#ct2-195)
- [CT2-196 — 27. Exploitation, sauvegarde et reprise](#ct2-196)
- [CT2-197 — 28. Confidentialité, RGPD et conservation](#ct2-197)
- [CT2-198 — 28.1 Minimisation](#ct2-198)
- [CT2-199 — 28.2 Données juridiques/sensibles](#ct2-199)
- [CT2-200 — 28.3 Suppression](#ct2-200)
- [CT2-201 — 29. Menaces spécifiques et sécurité applicative](#ct2-201)
- [CT2-202 — 29.1 Prompt injection réglementaire/contractuelle](#ct2-202)
- [CT2-203 — 29.2 Formula injection tableur](#ct2-203)
- [CT2-204 — 29.3 Archives](#ct2-204)
- [CT2-205 — 29.4 SSRF / URLs de sources](#ct2-205)
- [CT2-206 — 29.5 IDOR / tenant](#ct2-206)
- [CT2-207 — 29.6 Export sensible](#ct2-207)
- [CT2-208 — 30. Matrice de traçabilité MASTER métier → technique](#ct2-208)
- [CT2-209 — 31. Écarts déjà visibles avec le Cahier technique v1.0](#ct2-209)
- [CT2-210 — Couvert correctement](#ct2-210)
- [CT2-211 — À étendre](#ct2-211)
- [CT2-212 — Absent ou non explicite](#ct2-212)
- [CT2-213 — 32. Critères d’acceptation avant implémentation C1](#ct2-213)
- [CT2-214 — 33. Critères d’acceptation avant exposition commerciale](#ct2-214)
- [CT2-215 — Pénalités](#ct2-215)
- [CT2-216 — Préservation des droits](#ct2-216)
- [CT2-217 — Assurance](#ct2-217)
- [CT2-218 — Réglementation](#ct2-218)
- [CT2-219 — HSE](#ct2-219)
- [CT2-220 — Carte d’Engagement](#ct2-220)
- [CT2-221 — 34. Rollback stratégique](#ct2-221)
- [CT2-222 — 35. Questions ouvertes / validations externes](#ct2-222)
- [CT2-223 — 36. Instructions de travail à donner à Codex](#ct2-223)
- [CT2-224 — 37. Livrable de sortie attendu de Codex après l’audit](#ct2-224)
- [CT2-225 — 38. Références documentaires](#ct2-225)
- [CT2-226 — Autorités actuelles du dépôt](#ct2-226)
- [CT2-227 — Technique](#ct2-227)
- [CT2-228 — Nouvelles autorités candidates](#ct2-228)
- [CT2-229 — 39. Décision technique proposée](#ct2-229)
- [CT2-230 — 40. Verdict final](#ct2-230)

<!-- BEGIN INTEGRATION-CT2 -->
<a id="ct2-001"></a>
### CT2-001 — SMART AO — CAHIER TECHNIQUE D’EXÉCUTION
<a id="ct2-002"></a>
#### CT2-002 — v2.1 — Dérivé du MASTER métier v2.0 et du Product Freeze v2.0 actif

**Date :** 24 septembre 2026  
**Statut :** RÉFÉRENCE TECHNIQUE ACTIVE — IMPLÉMENTATION PAR TRANCHES GOUVERNÉES  
**Destination :** Codex / revue architecture / plan de migration / futures PR  
**Dépôt :** `mailtkarim-bot/SMART_AO_LAST`  
**Remplace :** `docs/Archive/01_Cahiers_remplaces/Architecture_et_technique/SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v1.0.md`  
**Référence métier :** `docs/Archive/01_Cahiers_remplaces/Produit_metier/SMART_AO_CAHIER_DIRECTEUR_METIER_MASTER_v2.0.md`

---



> **AUTORITÉ DE DÉRIVATION v2.1.** Ce cahier technique dérive du `docs/Archive/01_Cahiers_remplaces/Produit_metier/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v2.0.md`, promu le 24 septembre 2026. Il autorise l'implémentation par tranches verticales gouvernées ; aucune activation silencieuse de comportement juridique, assurantiel ou HSE ne remplace les validations externes requises.

> **RÈGLE CODEX.** L'audit de l'existant et la matrice `KEEP / ADAPT / REPLACE / DELETE / ABSENT` sont produits sous `docs/Archive/02_Audits/Realignement_V2/`. Codex implémente ensuite par tranches verticales. Toute différence entre MASTER métier, Product Freeze v2.0 et le présent document est un défaut de spécification à remonter ; Codex ne choisit pas lui-même quel besoin métier supprimer.

<a id="ct2-003"></a>
### CT2-003 — 0. Mandat, statut et règle de sécurité documentaire

<a id="ct2-004"></a>
#### CT2-004 — 0.1 Pourquoi cette version existe

Le cahier technique d’exécution v1.0 traduit correctement les invariants du Product Freeze v1.0 vers un monolithe modulaire tenant-aware : identité, Affaire, DCE, décision, prix, préparation, remise, audit, RAG, idempotence, append-only et sécurité.

Le nouveau `Cahier Directeur Métier Intégral — MASTER v2.0` révèle cependant une profondeur métier supplémentaire qui n’est pas encore explicitement traduite en contrats techniques suffisants :

- profil réglementaire dynamique de l’Affaire ;
- hiérarchie contractuelle et dérogations ;
- pénalités et sanctions contractuelles ;
- préservation des droits, délais et risques de forclusion ;
- ordres de service, modifications et travaux supplémentaires ;
- résiliation, substitution et exécution aux frais et risques ;
- réception, règlement des comptes, décompte général et DGD ;
- assurance : couverture réelle de l’activité et non simple présence d’une attestation ;
- HSE comme contrainte de capacité, délai et coût ;
- engagements environnementaux et sociaux mesurables ;
- circuit réel de paiement ;
- coût post-réception et garanties ;
- autorisations et dépendances tierces ;
- exposition portefeuille multi-Affaires ;
- Carte d’Engagement Patron consolidant les conséquences plutôt qu’un score opaque.

Cette v2.0 constitue la **traduction technique candidate** de cette profondeur.

<a id="ct2-005"></a>
#### CT2-005 — 0.2 Règle de précédence pendant la transition

La confrontation MASTER métier v2.0 ↔ Product Freeze v1.0 étant désormais réalisée et le Product Freeze v2.0 promu, la règle active est :

1. le **Product Freeze v2.0** est l’autorité produit officielle du dépôt ;
2. le **Product Freeze v2.0** porte le contrat produit issu de l'audit d'écart ;
3. le présent **Cahier technique v2.1** décrit la traduction technique candidate et le travail d’audit nécessaire ;
4. Codex peut réaliser les inventaires, analyses de dépendances, matrices `KEEP / ADAPT / REPLACE / DELETE`, tests de caractérisation et propositions de migration ;
5. Codex **ne doit pas activer silencieusement un comportement métier nouveau** hors des tranches et gates approuvées ;
6. toute implémentation qui modifie rôles, portes P0–P7, droits, état métier, règle de décision, portée vendue ou comportement visible attend la décision propriétaire correspondante.

Cette séparation est volontaire. Elle évite que le code devienne une autorité de fait avant l’arbitrage produit.

<a id="ct2-006"></a>
#### CT2-006 — 0.3 Mandat Codex — READ-ONLY / AUDIT FIRST

Avant la première migration ou création de modèle liée aux nouveaux domaines, Codex doit produire un audit factuel du dépôt.

Le mandat initial est :

```text
READ-ONLY / AUDIT FIRST
1. Cartographier l’existant réel.
2. Localiser modèles, services, ports, événements, routes, projections, tests et migrations concernés.
3. Classer chaque capacité : KEEP / ADAPT / REPLACE / DELETE / ABSENT.
4. Identifier les invariants déjà protégés par tests.
5. Identifier les divergences entre code, Product Freeze v2.0 actif et MASTER métier v2.0.
6. Proposer la plus petite migration cohérente.
7. Ne créer aucun droit, état ou pouvoir implicite.
8. Ne coder qu’après gate propriétaire/technique explicite.
```

<a id="ct2-007"></a>
##### CT2-007 — Sorties obligatoires de l’audit

- `CURRENT_STATE_MAP` : modules, tables, migrations, commandes, projections et tests existants ;
- `TRACEABILITY_DELTA` : MASTER métier → contrat technique → existant → écart ;
- `DATA_MIGRATION_IMPACT` ;
- `AUTHORIZATION_IMPACT` ;
- `AI_RAG_IMPACT` ;
- `UX_API_IMPACT` ;
- `TEST_GAP_MAP` ;
- `PR_PLAN` ordonné et réversible ;
- risques et rollback de chaque tranche.

Aucune affirmation « déjà supporté » n’est admise sans preuve dans le code ou les tests.

---

<a id="ct2-008"></a>
### CT2-008 — 1. État technique de référence à préserver

<a id="ct2-009"></a>
#### CT2-009 — 1.1 Architecture générale

La direction existante est conservée :

- **frontend :** React 19 + TypeScript + Vite sous `web/` ;
- **backend :** Python + FastAPI sous `backend/app/` ;
- **persistence :** PostgreSQL + SQLAlchemy + Alembic ;
- **jobs :** workers Python existants pour ingestion, export et projections ;
- **documents :** stockage privé référencé par hash et clé interne ;
- **IA/RAG :** retrieval borné par tenant, Affaire, DCE, rôle et classification ;
- **déploiement :** monolithe modulaire sur Docker Compose aujourd’hui, VPS durci ensuite ;
- **modèle d’exploitation cible initial :** instance dédiée par client mais application tenant-aware ;
- **aucun rewrite global**, aucun microservice par anticipation.

<a id="ct2-010"></a>
#### CT2-010 — 1.2 Invariants techniques existants à ne pas affaiblir

1. `tenant` résolu côté serveur ; jamais accepté comme autorité venant du navigateur.
2. rôle, membership, affectation, délégation et step-up résolus côté serveur.
3. aucune donnée financière Patron-only dans un contrat Collaborateur.
4. toute conclusion critique revient à une source et une version.
5. les inconnus restent `UNKNOWN`, `PARTIAL` ou `REVIEW_REQUIRED` selon le contrat ; absence de donnée ≠ zéro ≠ conformité.
6. transitions critiques et preuves append-only lorsque l’historique doit être défendable.
7. commandes sensibles idempotentes.
8. résultat externe inconnu n’est jamais converti en succès.
9. document externe = donnée non fiable ; jamais instruction système.
10. LLM = extraction/recherche/proposition ; jamais autorité de décision.
11. calcul financier déterministe ; jamais délégué au LLM.
12. migration additive et réversible autant que le contrat le permet.
13. code et tests décrivent l’état réellement implémenté ; un document ne permet pas de prétendre qu’une capacité existe.

<a id="ct2-011"></a>
#### CT2-011 — 1.3 Doctrine de modification

La stratégie reste :

> **greenfield fonctionnel, migration technique sélective.**

Le besoin métier redéfinit ce qui doit être vrai. Le dépôt existant est audité et reçoit pour chaque composant :

- `KEEP` — protège déjà le bon invariant ;
- `ADAPT` — base saine mais contrat insuffisant ;
- `REPLACE` — modèle incompatible avec le besoin ;
- `DELETE` — comportement désormais interdit ou sans propriétaire ;
- `ABSENT` — capacité non implémentée.

Le statut est attribué après lecture du code et des tests, jamais par ressemblance de nom.

---

<a id="ct2-012"></a>
### CT2-012 — 2. Principes architecturaux non négociables v2.0

Les principes v1.0 restent applicables et sont complétés par les suivants.

<a id="ct2-013"></a>
#### CT2-013 — 2.1 Métier et preuve

1. Une règle juridique ou réglementaire n’est jamais appliquée parce qu’un LLM « la connaît ».
2. Une règle vivante possède une source, une version, une date d’effet, une éventuelle date de fin, un champ d’application et un statut de validation.
3. Une clause du DCE prime sur une règle générique lorsque le contrat l’autorise ou la modifie ; cette relation doit être explicite.
4. Une dérogation n’écrase jamais la règle de référence : les deux restent visibles et reliées.
5. Un délai contractuel calculé conserve la règle, l’événement déclencheur, le timestamp de départ, le calendrier utilisé et la méthode de calcul.
6. Si l’un de ces éléments manque, le système ne fabrique pas d’échéance certaine.
7. Une pénalité extraite n’est pas une dette certaine ; elle est une règle d’exposition à qualifier et simuler.
8. Une attestation d’assurance n’est pas une conclusion de couverture.
9. Une exigence HSE n’est pas « traitée » tant que les moyens, compétences, délais ou preuves nécessaires ne sont pas reliés.
10. Un engagement de mémoire technique devient un objet métier si sa promesse est mesurable ou opposable.

<a id="ct2-014"></a>
#### CT2-014 — 2.2 Temps et temporalité

Toute règle susceptible d’évoluer doit être **bitemporelle ou au minimum effective-dated** selon le besoin :

- date de publication ;
- date d’effet ;
- date de fin si connue ;
- date de connaissance/import dans SmartAO ;
- version/supersession.

Une règle future reste future. Une règle expirée ne devient pas applicable à une affaire nouvelle. Une affaire ancienne conserve la règle utilisée au moment de sa décision si le contrat l’exige.

<a id="ct2-015"></a>
#### CT2-015 — 2.3 Exactitude financière et contractuelle

- argent : entier en centimes ou `Decimal` contrôlé selon conventions existantes ; **jamais float** ;
- pourcentage : représentation exacte/documentée ;
- durée/délai : unité et convention explicites ;
- fuseau horaire : source explicite ; jamais heure locale implicite du poste ;
- formules contractuelles : parse/normalisation déterministes uniquement lorsqu’elles sont suffisamment établies ; sinon revue humaine ;
- aucune exécution d’expression arbitraire extraite d’un document.

<a id="ct2-016"></a>
#### CT2-016 — 2.4 Reproductibilité

Tout résultat critique calculé doit être reproductible à partir de :

`inputs + source_versions + rule_version + algorithm_version + actor/context + timestamp`.

Cette règle vaut notamment pour :

- échéances de préservation des droits ;
- simulations de pénalités ;
- prix révisés/actualisés ;
- cash-flow ;
- exposition portefeuille ;
- couverture d’engagement ;
- applicability d’une règle validée.

---

<a id="ct2-017"></a>
### CT2-017 — 3. Bounded contexts et frontières v2.0

Le monolithe modulaire reste la cible. Les domaines ci-dessous sont **frontières logiques**, pas des microservices.

<a id="ct2-018"></a>
#### CT2-018 — 3.1 Contextes existants à conserver / enrichir

<a id="ct2-019"></a>
##### CT2-019 — Identity & Access
Identité, tenant, membership, rôles, délégations, MFA, step-up, partage externe, suspension, récupération.

<a id="ct2-020"></a>
##### CT2-020 — Opportunity / Radar
Sources amont, opportunités, qualification P0/P1, provenance et inconnus.

<a id="ct2-021"></a>
##### CT2-021 — Case / Affaire
Périmètre, lots, phases, tours, acteurs, échéances de référence et projections opérationnelles.

<a id="ct2-022"></a>
##### CT2-022 — DCE & Document Intelligence
Admission, versioning, extraction, classification, fragments, locators, rectificatifs, lisibilité et couverture.

<a id="ct2-023"></a>
##### CT2-023 — Evidence & Market Understanding
Evidence, SourceAnchor, Requirement, MIRP, Unknown, Hypothesis, Contradiction, RiskSignal, Applicability, CostFactor.

<a id="ct2-024"></a>
##### CT2-024 — Enterprise Memory
Faits d’entreprise, preuves, ressources, personnes, partenaires, prix internes, assurances, qualifications, REX.

<a id="ct2-025"></a>
##### CT2-025 — Decision & Governance
P0–P7, conditions, motifs, dérogations décisionnelles, invalidation, supersession, autorité humaine.

<a id="ct2-026"></a>
##### CT2-026 — Pricing Intelligence
Imports, coût, prix, scénarios, trésorerie, facteurs de coût, couverture DPGF/BPU/DQE.

<a id="ct2-027"></a>
##### CT2-027 — Response & Artifacts
Pièces à produire/remplir/obtenir, mémoire, engagements, versions, contrôle et export.

<a id="ct2-028"></a>
##### CT2-028 — Submission
Candidate, manifeste, signature, P5, export, dépôt humain et preuve.

<a id="ct2-029"></a>
##### CT2-029 — Collaboration & Work
Tâches, revues, notifications, responsables, contributeurs, partage ciblé et reprise.

<a id="ct2-030"></a>
##### CT2-030 — Handover & Learning
Contrat vendu, passation P7, engagements, résultats, REX.

<a id="ct2-031"></a>
##### CT2-031 — AI Runtime / Guidance
Retrieval, reranking, context policy, outils, structured outputs, citations, abstention, télémétrie.

<a id="ct2-032"></a>
##### CT2-032 — Platform
Persistence, outbox, idempotence, jobs, stockage, logs, observabilité, sauvegardes.

<a id="ct2-033"></a>
#### CT2-033 — 3.2 Nouveau bounded context logique : Contract & Rights

**Statut : RÉFÉRENCE TECHNIQUE ACTIVE ; les tranches restent soumises à leurs gates d’implémentation.**

Ce domaine est justifié car il possède :

- son propre vocabulaire ;
- des transitions temporelles ;
- des calculs déterministes ;
- des obligations d’audit ;
- des dépendances vers DCE/Evidence sans appartenir au parser ;
- des conséquences sur Decision, Pricing et Handover sans appartenir à ces domaines.

Il regroupe :

- contrat de référence ;
- hiérarchie des pièces ;
- règles incorporées ;
- dérogations ;
- pénalités/sanctions ;
- événements de préservation de droits ;
- OS/modifications/travaux supplémentaires ;
- règlement des comptes / décomptes ;
- réception/garanties ;
- résiliation/substitution/frais et risques ;
- obligations contractuelles d’exécution et de preuve.

<a id="ct2-034"></a>
##### CT2-034 — Frontière stricte

`Contract & Rights` :

- **ne rend pas d’avis juridique autonome** ;
- ne détermine pas seul la validité d’une clause ;
- ne remplace pas un juriste/conseil ;
- expose règles, sources, conditions, calculs et incertitudes ;
- ouvre des revues humaines explicites lorsque la qualification dépasse le contrat déterministe.

<a id="ct2-035"></a>
#### CT2-035 — 3.3 Regulatory Knowledge — référentiel transversal, pas moteur juridique autonome

Le `RegulatoryProfile` et les règles vivantes peuvent être implémentés comme sous-domaine de Evidence/Knowledge ou module autonome si l’audit justifie la frontière.

Le choix physique est à déterminer **après inventaire** ; le contrat fonctionnel est en revanche figé dans ce candidat :

- rule store versionné ;
- applicability par faits prouvés ;
- source officielle ;
- dates d’effet ;
- exceptions ;
- revue humaine ;
- aucune conclusion réglementaire fondée uniquement sur génération LLM.

---

<a id="ct2-036"></a>
### CT2-036 — 4. Modèle de données conceptuel v2.0

Les noms ci-dessous sont des **noms métier candidats**, pas des classes existantes revendiquées. Codex doit d’abord les mapper aux conventions et modèles du dépôt.

<a id="ct2-037"></a>
#### CT2-037 — 4.1 Regulatory Profile

<a id="ct2-038"></a>
##### CT2-038 — `RegulatoryProfile`

Portée : une Affaire / lot / option / phase selon besoin.

Attributs conceptuels :

- case/affaire ;
- lot/périmètre ;
- marché public/privé ;
- nature opération ;
- bâtiment / infrastructure / réseau / ouvrage ;
- neuf / existant / rénovation / démolition / maintenance ;
- destination/usage ;
- date(s) déterminantes ;
- année de construction lorsque prouvée ;
- surface/quantité lorsque applicable ;
- site occupé / ERP / site sensible ;
- géographie ;
- montant et seuils utiles ;
- sous-traitance/groupement ;
- substances/risques connus ;
- nombre d’entreprises/intervenants si pertinent ;
- provenance de chaque fait ;
- état de complétude.

Un champ non établi reste inconnu ; aucune valeur par défaut opportuniste.

<a id="ct2-039"></a>
##### CT2-039 — `RegulatoryRule`

Attributs conceptuels :

- identifiant stable interne ;
- juridiction ;
- thème ;
- source officielle ;
- référence ;
- version ;
- publication ;
- date d’effet ;
- date de fin éventuelle ;
- scope structuré ;
- exceptions structurées lorsque qualifiées ;
- niveau de validation ;
- propriétaire de revue ;
- dernière revue ;
- prochaine revue ;
- statut `FUTURE / ACTIVE / EXPIRED / SUPERSEDED / REVIEW_REQUIRED`.

<a id="ct2-040"></a>
##### CT2-040 — `RuleApplicabilityAssessment`

Relie une règle à une Affaire et conserve :

- faits utilisés ;
- faits manquants ;
- résultat `APPLICABLE / NOT_APPLICABLE / POTENTIALLY_APPLICABLE / REVIEW_REQUIRED / UNKNOWN` ;
- méthode ;
- rule version ;
- evidence ;
- validateur humain si nécessaire ;
- invalidation après changement d’un fait ou de la règle.

<a id="ct2-041"></a>
#### CT2-041 — 4.2 Contrat et hiérarchie

<a id="ct2-042"></a>
##### CT2-042 — `ContractBaseline`

Décrit le cadre contractuel identifié :

- type d’affaire ;
- documents constituant le contrat proposé ;
- référentiels incorporés lorsqu’ils sont explicitement cités ;
- version de chaque référentiel ;
- ordre de priorité si établi ;
- éléments non établis ;
- état de revue.

<a id="ct2-043"></a>
##### CT2-043 — `ContractRuleReference`

Relie une disposition contractuelle générique à sa source/version.

<a id="ct2-044"></a>
##### CT2-044 — `ContractDeviation`

Une dérogation ne remplace pas la règle ; elle la **référence**.

Champs :

- règle de référence ;
- clause particulière source ;
- nature de la modification ;
- périmètre ;
- texte/extrait ;
- impacts candidats ;
- certitude ;
- revue métier/juridique ;
- statut ;
- supersession.

<a id="ct2-045"></a>
##### CT2-045 — Invariant

Impossible d’avoir une dérogation « active » sans :

- source particulière ;
- règle de référence ou motif `REFERENCE_NOT_ESTABLISHED` ;
- portée ;
- état de revue.

<a id="ct2-046"></a>
#### CT2-046 — 4.3 Pénalités et sanctions

<a id="ct2-047"></a>
##### CT2-047 — `ContractSanctionRule`

Une entrée représente une règle contractuelle de sanction/pénalité.

Attributs conceptuels :

- déclencheur ;
- catégorie ;
- source et version ;
- scope lot/phase/engagement ;
- unité ;
- montant fixe ou formule normalisée si déterminable ;
- base de calcul ;
- franchise ;
- plafond ;
- exonération/seuil ;
- cumul ;
- prérequis de procédure ;
- cause exonératoire à examiner ;
- dérogation liée ;
- partie responsable ;
- recours partenaire éventuel ;
- statut de modélisation ;
- niveau de confiance ;
- validation humaine.

<a id="ct2-048"></a>
##### CT2-048 — Calculs de scénarios

Le moteur de simulation doit produire :

- hypothèses ;
- événements simulés ;
- formule/version ;
- résultat ;
- `MAX_EXPOSURE_UNKNOWN` lorsque l’absence de plafond ou une formule ambiguë interdit une borne défendable.

**Interdit :** interpréter une phrase libre avec `eval`, expression dynamique non contrôlée ou LLM comme calculateur autoritatif.

<a id="ct2-049"></a>
#### CT2-049 — 4.4 Préservation des droits

<a id="ct2-050"></a>
##### CT2-050 — `RightPreservationEvent`

Objet C1 central.

Champs minimaux :

- type d’événement ;
- affaire/lot/phase ;
- événement déclencheur source ;
- document/version ;
- règle contractuelle applicable ;
- dérogation éventuelle ;
- timestamp de réception/constat ;
- convention de calcul du délai ;
- date/heure limite calculée si établie ;
- fuseau et calendrier ;
- destinataires ;
- canal/forme ;
- contenu minimal attendu ;
- montant/chef de demande lorsque applicable ;
- responsable interne ;
- validateur ;
- preuve d’envoi ;
- preuve de réception ;
- état ;
- conséquence potentielle ;
- `REVIEW_REQUIRED` si qualification juridique nécessaire.

États candidats :

`OPEN → DUE → PREPARED → SENT → ACKNOWLEDGED → CLOSED`

États alternatifs :

`REVIEW_REQUIRED`, `DISPUTED`, `SUPERSEDED`, `EXPIRED`, `UNKNOWN_OUTCOME`.

Les états définitifs devront être alignés sur les conventions existantes après audit.

<a id="ct2-051"></a>
##### CT2-051 — Invariants C1

1. aucune échéance certaine sans règle et événement de départ établis ;
2. toute date calculée conserve ses inputs ;
3. changer la version contractuelle invalide les calculs dépendants ;
4. une échéance expirée n’efface pas l’événement ;
5. « envoyé » ≠ « reçu » ;
6. « reçu » ≠ « juridiquement suffisant » ;
7. l’IA ne ferme jamais l’événement ;
8. l’utilisateur qui valide doit être habilité pour le périmètre ;
9. chaque événement critique apparaît dans la passation P7.

<a id="ct2-052"></a>
#### CT2-052 — 4.5 OS, modifications et travaux supplémentaires

<a id="ct2-053"></a>
##### CT2-053 — `ContractChangeInstruction`

Capture :

- instruction/OS/demande ;
- émetteur ;
- pouvoir de prescription non présumé ;
- source ;
- date ;
- prestation ;
- prix fourni/non fourni ;
- délai fourni/non fourni ;
- impacts identifiés ;
- action de préservation liée ;
- nouveau prix/proposition si validé ;
- statut d’acceptation/exécution ;
- preuves.

Le système ne transforme jamais l’absence de prix en « inclus ».

<a id="ct2-054"></a>
#### CT2-054 — 4.6 Règlement des comptes, réception et DGD

<a id="ct2-055"></a>
##### CT2-055 — `SettlementMilestone`

Types candidats :

- situation/acompte ;
- projet de décompte ;
- projet de décompte final ;
- décompte général ;
- DGD ;
- réception ;
- réserves ;
- levée de réserves ;
- garantie/libération.

Chaque jalon :

- source ;
- date de réception ;
- montant lorsque autorisé ;
- réserves/écarts ;
- délai de réaction ;
- événements de droits liés ;
- statut ;
- preuve.

<a id="ct2-056"></a>
#### CT2-056 — 4.7 Résiliation et substitution

<a id="ct2-057"></a>
##### CT2-057 — `TerminationExposure`

Représente l’exposition, pas une décision juridique automatique :

- cause/clause ;
- prérequis ;
- mise en demeure ;
- délai de remède ;
- résiliation potentielle ;
- substitution/exécution aux frais et risques ;
- coût/scénarios ;
- garanties affectées ;
- partenaires affectés ;
- preuves ;
- revue spécialisée.

<a id="ct2-058"></a>
#### CT2-058 — 4.8 Assurance

<a id="ct2-059"></a>
##### CT2-059 — `InsuranceCoverageAssessment`

Compare une **prestation/activité promise** à une preuve assurantielle.

Champs :

- activité/prestation ;
- ouvrage/technique ;
- période ;
- zone ;
- titulaire ;
- attestation/police source ;
- libellé déclaré ;
- exclusions/réserves visibles ;
- conclusion limitée ;
- validateur courtier/assureur si nécessaire ;
- état.

États métier candidats :

`COVERED`, `PROBABLY_COVERED`, `NOT_ESTABLISHED`, `OUTSIDE_DECLARED_ACTIVITY`, `BROKER_REVIEW_REQUIRED`.

Ces valeurs sont des états de workflow interne, **pas des avis juridiques**.

<a id="ct2-060"></a>
#### CT2-060 — 4.9 HSE et prérequis d’exécution

<a id="ct2-061"></a>
##### CT2-061 — `ExecutionPrerequisite`

Relie une obligation à :

- compétence ;
- personne/ressource ;
- matériel ;
- autorisation ;
- document ;
- formation/habilitation ;
- délai d’obtention ;
- coût ;
- phase ;
- blocage ;
- preuve ;
- responsable.

Exemples : PPSPS, inspection commune, consignation, AIPR, DT-DICT, RAT, habilitation, accès, autorisation exploitant.

<a id="ct2-062"></a>
#### CT2-062 — 4.10 Engagement mesurable

<a id="ct2-063"></a>
##### CT2-063 — `MeasurableCommitment`

Un engagement de l’offre ou du contrat devient objet lorsqu’il promet :

- une valeur ;
- un moyen ;
- une fréquence ;
- un délai ;
- une personne ;
- un matériel ;
- un taux ;
- une performance ;
- une obligation de reporting.

Champs :

- texte source ;
- valeur/objectif ;
- unité ;
- méthode de mesure ;
- fréquence ;
- preuve attendue ;
- coût ;
- ressource ;
- responsable ;
- sous-traitants concernés ;
- obligation de cascade ;
- sanction liée ;
- phase ;
- statut de couverture.

Le simple texte du mémoire n’est pas la source de vérité du suivi : la version remise et son hash restent reliés.

<a id="ct2-064"></a>
#### CT2-064 — 4.11 Circuit de paiement

<a id="ct2-065"></a>
##### CT2-065 — `PaymentCircuit`

Un circuit décrit :

`production → demande/situation → contrôleur/visa → service fait → payeur/plateforme → encaissement`.

Chaque étape :

- acteur ;
- pièce ;
- délai contractuel ;
- motif de rejet/suspension ;
- preuve ;
- dépendance ;
- retenue ;
- statut ;
- hypothèse de cash associée.

Il ne remplace ni Chorus Pro ni la comptabilité.

<a id="ct2-066"></a>
#### CT2-066 — 4.12 Obligations post-réception

<a id="ct2-067"></a>
##### CT2-067 — `PostReceptionObligation`

- OPR ;
- essais ;
- mise en service ;
- formation ;
- DOE/DIUO ;
- levée de réserves ;
- GPA ;
- maintenance initiale ;
- stock pièces ;
- astreinte ;
- clôture administrative ;
- libération garanties.

Chaque obligation peut porter coût, ressource, échéance, preuve et sanction liée.

<a id="ct2-068"></a>
#### CT2-068 — 4.13 Autorisations et dépendances tierces

<a id="ct2-069"></a>
##### CT2-069 — `ExternalDependency`

Couvre :

- autorisation voirie/domaine public ;
- coupure ;
- concessionnaire ;
- badge/site sensible ;
- survol/grutage ;
- arrêté circulation ;
- consignation ;
- accès exploitant ;
- autorisation environnementale/projet si explicitement pertinente.

Le moteur de planning peut constater une dépendance non sécurisée ; il ne prétend pas que l’autorisation sera obtenue.

---

<a id="ct2-070"></a>
### CT2-070 — 5. Carte d’Engagement de l’Affaire — projection centrale Patron

<a id="ct2-071"></a>
#### CT2-071 — 5.1 Nature

La Carte d’Engagement est une **projection de décision**, pas une nouvelle source de vérité.

Elle agrège des objets autoritatifs depuis leurs contextes et répond aux douze axes :

1. intérêt commercial ;
2. admissibilité/candidature ;
3. périmètre technique ;
4. constructibilité/logistique ;
5. contrat/exposition ;
6. prix/marge ;
7. trésorerie/garanties ;
8. capacité/charge ;
9. partenaires ;
10. HSE/environnement/réglementaire ;
11. obligations documentaires/engagements ;
12. préservation des droits/sortie de contrat.

<a id="ct2-072"></a>
#### CT2-072 — 5.2 Interdiction du score opaque

Aucune somme pondérée ne peut produire un GO automatique.

La projection peut afficher :

- nombre d’objets ouverts par criticité ;
- conséquences ;
- conditions de porte ;
- risques acceptés ;
- inconnus ;
- échéances ;
- couverture par preuves ;
- scénarios économiques.

Mais elle ne doit jamais transformer cette information en « 83/100 donc GO ».

<a id="ct2-073"></a>
#### CT2-073 — 5.3 Anatomie technique d’une ligne Patron

Chaque ligne de risque/condition doit pouvoir exposer :

- source ;
- version ;
- locator ;
- applicabilité ;
- certitude ;
- impact technique ;
- impact coût ;
- impact délai ;
- impact trésorerie ;
- impact contractuel ;
- responsable ;
- action suivante ;
- échéance ;
- preuve attendue ;
- décision requise ;
- risque résiduel ;
- liens vers objets sources.

La projection est recalculable et ne duplique pas la vérité source.

<a id="ct2-074"></a>
#### CT2-074 — 5.4 GO sous conditions

Une condition doit être un objet adressable, et non du texte libre uniquement.

Elle conserve :

- porte ;
- condition ;
- cause ;
- responsable ;
- échéance ;
- preuve de levée ;
- règle de revalidation ;
- conséquences si non levée ;
- décision Patron.

Une condition levée n’efface pas son historique.

---

<a id="ct2-075"></a>
### CT2-075 — 6. Applicabilité et moteur de règles sûr

<a id="ct2-076"></a>
#### CT2-076 — 6.1 Deux moteurs à ne pas confondre

<a id="ct2-077"></a>
##### CT2-077 — Moteur d’extraction

Peut utiliser IA/RAG pour trouver :

- indices de clauses ;
- références réglementaires ;
- dates ;
- usages ;
- seuils ;
- obligations candidates.

Sortie = **candidat sourcé**, jamais verdict réglementaire final.

<a id="ct2-078"></a>
##### CT2-078 — Moteur d’applicabilité

Utilise :

- faits structurés validés ;
- règles validées/versionnées ;
- opérateurs déterministes bornés ;
- exceptions explicitement modélisées ;
- revue humaine lorsque nécessaire.

<a id="ct2-079"></a>
#### CT2-079 — 6.2 DSL / règles

S’il existe un langage de règles, il doit être :

- déclaratif ;
- non Turing-complet ;
- sans exécution dynamique arbitraire ;
- versionné ;
- testable ;
- limité à des opérateurs whitelisted ;
- explicable en sortie.

Aucune expression réglementaire extraite d’un DCE ne devient directement exécutable.

<a id="ct2-080"></a>
#### CT2-080 — 6.3 Invalidation

Recalcul ciblé si :

- fait du profil change ;
- règle est supersédée ;
- date déterminante change ;
- nouvelle pièce DCE corrige le fait ;
- périmètre lot/option change.

Les anciens résultats restent audités avec leur rule version.

---

<a id="ct2-081"></a>
### CT2-081 — 7. Hiérarchie contractuelle et dérogations

<a id="ct2-082"></a>
#### CT2-082 — 7.1 Graphe de contrat

Le système doit pouvoir représenter :

- document ;
- version ;
- nature contractuelle/indicative ;
- ordre de priorité explicite ;
- référence/incorporation ;
- modification/dérogation ;
- réponse acheteur/avenant/mise au point ;
- statut `PROPOSED / SUBMITTED / ACCEPTED / SUPERSEDED` selon contexte.

<a id="ct2-083"></a>
#### CT2-083 — 7.2 Règle de conflit

Une contradiction documentaire n’est pas résolue par priorité implicite si l’ordre contractuel n’est pas établi.

Sortie : `REVIEW_REQUIRED`.

<a id="ct2-084"></a>
#### CT2-084 — 7.3 Dérogations

Pipeline :

```text
REFERENCE_RULE
   ↓
PARTICULAR_CLAUSE
   ↓
DEVIATION_CANDIDATE
   ↓
HUMAN/DETERMINISTIC QUALIFICATION
   ↓
BUSINESS_IMPACTS
   ↓
P2/P3/P4 CONDITION OR RISK
```

Les impacts peuvent créer des liens vers Pricing, Capacity, Handover ou Right Preservation ; le module Contract ne duplique pas leurs données.

---

<a id="ct2-085"></a>
### CT2-085 — 8. Calculs déterministes critiques

<a id="ct2-086"></a>
#### CT2-086 — 8.1 Pénalités

Un calcul doit conserver :

- montant d’assiette ;
- unité ;
- quantité/durée ;
- taux ;
- plafond/franchise ;
- règles de cumul ;
- version ;
- arrondi ;
- résultat.

Si le texte ne permet pas une normalisation fiable : `FORMULA_REVIEW_REQUIRED`.

<a id="ct2-087"></a>
#### CT2-087 — 8.2 Prix / actualisation / révision

Pour toute formule qualifiée :

- mois zéro ;
- date de référence ;
- index exact ;
- coefficients ;
- part fixe ;
- source index ;
- périodicité ;
- formule ;
- arrondi ;
- indice manquant ;
- substitution éventuelle ;
- résultat par période.

Le moteur doit comparer la protection client à l’exposition achats/fournisseurs sans conclure que l’une couvre automatiquement l’autre.

<a id="ct2-088"></a>
#### CT2-088 — 8.3 Délais de droits

Calcul :

`deadline = function(trigger_timestamp, rule_version, calendar, duration, timezone, exclusions)`

Le résultat conserve tous les inputs.

Éviter de coder « 30 jours » ou « 45 jours » comme constante métier globale.

<a id="ct2-089"></a>
#### CT2-089 — 8.4 Cash-flow

Les projections existantes doivent pouvoir intégrer :

- retenues ;
- avance et remboursement ;
- garanties bancaires ;
- situations ;
- délai prudent d’encaissement ;
- paiement sous-traitants ;
- achats ;
- frais bancaires ;
- pénalités scénarisées ;
- coûts post-réception ;
- obligations HSE/environnement ;
- scénarios de modification.

Aucun résultat ne doit être présenté comme prévision certaine.

<a id="ct2-090"></a>
#### CT2-090 — 8.5 Exposition portefeuille

Projection Patron-only :

- combinaison d’attributions ;
- cash cumulé ;
- garanties cumulées ;
- équipes/matériels partagés ;
- fournisseurs communs ;
- périodes de pointe ;
- hypothèses de probabilité clairement distinctes des engagements signés.

Une probabilité d’attribution ne devient jamais une prédiction automatique de marché.

---

<a id="ct2-091"></a>
### CT2-091 — 9. Sécurité, droits et classification des nouvelles données

<a id="ct2-092"></a>
#### CT2-092 — 9.1 Classifications minimales

Les classifications exactes doivent réutiliser les enums du dépôt lorsqu’ils existent. Conceptuellement, les nouveaux objets nécessitent au moins :

- public/partageable ;
- affaire interne ;
- direction/finance ;
- juridique sensible ;
- données personnelles ;
- sécurité/site sensible.

Codex doit **mapper**, pas multiplier les enums si l’existant permet la règle.

<a id="ct2-093"></a>
#### CT2-093 — 9.2 Patron

Patron ou capacité explicitement déléguée :

- P3 ;
- acceptation des risques économiques ;
- seuils de trésorerie ;
- exposition sanctions ;
- solidarité ;
- acceptation de dérogations sensibles ;
- conditions GO ;
- P5 ;
- P6/P7 selon contrat.

<a id="ct2-094"></a>
#### CT2-094 — 9.3 Collaborateur

Peut :

- préparer ;
- sourcer ;
- qualifier candidat ;
- demander revue ;
- gérer tâches et preuves ;
- proposer impact.

Ne reçoit pas automatiquement :

- marge ;
- prix d’achat sensible ;
- cash ;
- exposition économique confidentielle ;
- appréciations partenaires Direction ;
- consultation juridique confidentielle hors périmètre.

<a id="ct2-095"></a>
#### CT2-095 — 9.4 Experts

QSE, DAF, conducteur, métreur, achats, juriste/conseil : accès limité par périmètre et besoin.

Une validation spécialisée n’élève pas le rôle au Patron.

<a id="ct2-096"></a>
#### CT2-096 — 9.5 Administrateur et support

Aucun droit métier implicite.

Les accès exceptionnels suivent les règles existantes : bornés, nominatifs, temporels, journalisés, avec objectif.

<a id="ct2-097"></a>
#### CT2-097 — 9.6 IA

Le context builder applique classification + permissions **avant retrieval et avant agrégation**.

Le LLM d’un rôle non financier ne doit pas pouvoir déduire la marge à partir d’agrégats intermédiaires.

---

<a id="ct2-098"></a>
### CT2-098 — 10. Contrats d’application et idempotence

<a id="ct2-099"></a>
#### CT2-099 — 10.1 Principe

Les opérations métier passent par les services/commandes applicatifs existants. Les noms concrets ne sont pas imposés avant audit.

Chaque commande sensible porte les identifiants de corrélation/idempotence prévus par l’architecture existante.

<a id="ct2-100"></a>
#### CT2-100 — 10.2 Familles de commandes à supporter

Après mapping sur l’existant, l’application doit permettre de :

- enregistrer/corriger un fait réglementaire avec preuve ;
- qualifier l’applicabilité d’une règle ;
- enregistrer une règle contractuelle de référence ;
- qualifier une dérogation ;
- enregistrer/modéliser une pénalité ;
- créer/requalifier un événement de préservation de droits ;
- enregistrer un OS/modification ;
- enregistrer une preuve d’envoi/réception ;
- préparer une analyse assurance ;
- qualifier un prérequis HSE ;
- créer/revoir un engagement mesurable ;
- définir/revoir un circuit de paiement ;
- enregistrer un jalon de règlement/réception ;
- préparer/valider la passation P7.

<a id="ct2-101"></a>
#### CT2-101 — 10.3 Rejeu

Un retry après timeout doit :

- retourner le reçu antérieur si la commande est identique ;
- refuser même clé avec payload différent ;
- ne pas créer deux échéances, deux engagements ou deux preuves ;
- conserver `UNKNOWN_OUTCOME` si la confirmation externe manque.

---

<a id="ct2-102"></a>
### CT2-102 — 11. Concurrence et cohérence transactionnelle

<a id="ct2-103"></a>
#### CT2-103 — 11.1 Optimistic concurrency

Les objets à forte contention doivent porter une révision ou mécanisme équivalent :

- décision ;
- condition GO ;
- événement de droit ;
- dérogation ;
- sanction ;
- engagement ;
- version de passation.

Une modification basée sur une révision ancienne doit produire un conflit explicite, pas « dernier clic gagne ».

<a id="ct2-104"></a>
#### CT2-104 — 11.2 Édition concurrente

Préserver :

- contribution A ;
- contribution B ;
- dernier état confirmé ;
- décision de merge/revue.

L’UX N01/N02 existante reste la doctrine.

<a id="ct2-105"></a>
#### CT2-105 — 11.3 Outbox

Les événements métier internes peuvent alimenter projections/notifications via outbox.

L’outbox ne transforme jamais :

- email envoyé supposé ;
- courrier reçu supposé ;
- dépôt reçu supposé ;
- notification réglementaire externe supposée.

Toute externalité conserve un statut de preuve propre.

---

<a id="ct2-106"></a>
### CT2-106 — 12. IA / RAG / règles métier — séparation stricte

<a id="ct2-107"></a>
#### CT2-107 — 12.1 Pipeline obligatoire

```text
INGESTION
  → EXTRACTION
  → RETRIEVAL
  → RERANKING éventuel
  → CANDIDATE FACT / CLAUSE / REQUIREMENT
  → DETERMINISTIC RULES / BUSINESS SERVICES
  → HUMAN REVIEW WHEN REQUIRED
  → DECISION / GENERATION
```

Jamais :

```text
PDF → LLM → "conforme / assuré / délai certain / GO"
```

<a id="ct2-108"></a>
#### CT2-108 — 12.2 Extraction contractuelle

Le LLM peut proposer :

- clause candidate ;
- catégorie ;
- paramètres candidats ;
- source/locator ;
- ambiguïtés.

Il ne peut pas :

- inventer un plafond ;
- présumer une dérogation ;
- choisir une version de CCAG sans preuve ;
- conclure qu’une pénalité est inapplicable ;
- rendre un avis assurance ;
- créer une échéance juridique certaine si le trigger manque.

<a id="ct2-109"></a>
#### CT2-109 — 12.3 Réglementation

La connaissance générative n’est jamais la base de vérité.

Les règles actives proviennent d’un store validé ; la veille peut proposer une mise à jour mais celle-ci passe par revue, versioning et impact analysis.

<a id="ct2-110"></a>
#### CT2-110 — 12.4 Génération documentaire

Un brouillon d’OS/réserve/réclamation/question peut être généré uniquement à partir :

- faits sourcés ;
- paramètres validés ;
- modèle approprié ;
- destinataire sélectionné ;
- version de contrat ;
- mention explicite `DRAFT / REVIEW_REQUIRED`.

Aucun envoi automatique V1 sans décision séparée.

---

<a id="ct2-111"></a>
### CT2-111 — 13. Document intelligence, locators et tableaux

<a id="ct2-112"></a>
#### CT2-112 — 13.1 Sources critiques

Les nouveaux domaines augmentent l’importance de :

- CCAP/CCP ;
- AE/projet de marché ;
- RC ;
- CCTP ;
- réponses acheteur ;
- actes de mise au point ;
- bordereaux ;
- plannings ;
- PGC/PPSPS ;
- attestations ;
- devis fournisseurs ;
- courriers/OS ;
- décomptes ;
- PV réception.

<a id="ct2-113"></a>
#### CT2-113 — 13.2 Locator

Une alerte contractuelle sans locator précis doit indiquer `SOURCE_LOCATION_PARTIAL` au lieu de simuler une précision inexistante.

<a id="ct2-114"></a>
#### CT2-114 — 13.3 Tableurs

Les formules et cellules de prix doivent conserver :

- feuille ;
- cellule/plage ;
- valeur ;
- formule si accessible ;
- type ;
- unité ;
- version du fichier ;
- hash.

Un export/import Excel ne peut pas silencieusement écraser le contexte source.

---

<a id="ct2-115"></a>
### CT2-115 — 14. Rectificatifs et invalidation ciblée

Un nouveau DCE, Q/R, CCAP, DPGF ou planning peut invalider :

- exigence ;
- MIRP ;
- applicability ;
- dérogation ;
- pénalité ;
- délai ;
- prix ;
- cash ;
- assurance ;
- HSE ;
- engagement ;
- condition P2/P3/P4/P5 ;
- paquet de remise.

<a id="ct2-116"></a>
#### CT2-116 — 14.1 Graphe de dépendance

Toute conclusion critique doit déclarer ses dépendances suffisamment pour recalculer **les objets touchés**, pas purger toute l’Affaire.

<a id="ct2-117"></a>
#### CT2-117 — 14.2 Candidate invalidation

Si une pièce ayant contribué au paquet P5 change :

- candidate précédente reste historique ;
- readiness/P5 peut redevenir invalide ;
- aucun dépôt précédent n’est réécrit ;
- une nouvelle candidate doit être construite et autorisée.

---

<a id="ct2-118"></a>
### CT2-118 — 15. Passation P7 renforcée

La passation devient le moment où l’on transmet le **contrat vendu et le système de protection**, pas seulement les pièces de prix.

<a id="ct2-119"></a>
#### CT2-119 — 15.1 Paquet minimal

- version contractuelle acceptée ;
- prix/budget autorisé selon droits ;
- hypothèses ;
- exclusions/réserves ;
- engagements vendus ;
- partenaires retenus ;
- contraintes capacité/logistique ;
- HSE/prérequis ;
- environnement/social ;
- sanctions significatives ;
- dérogations sensibles ;
- OS/change rules ;
- calendrier de préservation des droits ;
- circuit paiement ;
- réception/DGD/garanties ;
- conditions GO non encore closes ;
- points `REVIEW_REQUIRED`.

<a id="ct2-120"></a>
#### CT2-120 — 15.2 Acceptation

P7 ne signifie pas « tout est sans risque ».

Il signifie que :

- le paquet est identifiable ;
- les risques sont affectés ;
- les obligations critiques ont un responsable ;
- les droits temporels ont un propriétaire ;
- les inconnus acceptés restent visibles.

---

<a id="ct2-121"></a>
### CT2-121 — 16. Frontend / UX — impacts obligatoires

Le catalogue UX actuel conserve son autorité. Les nouveaux besoins doivent être absorbés sans créer une jungle de routes.

<a id="ct2-122"></a>
#### CT2-122 — 16.1 C05 — À résoudre

Ajouter des natures typées pour les nouveaux objets, selon le catalogue après révision propriétaire :

- dérogation ;
- sanction ;
- droit/échéance ;
- assurance à confirmer ;
- prérequis HSE ;
- engagement mesurable ;
- autorisation tierce.

Une tâche fermée ne ferme pas l’objet source.

<a id="ct2-123"></a>
#### CT2-123 — 16.2 C07 — Décision

La carte P2/P3/P4 doit pouvoir afficher :

- impacts contractuels ;
- sanctions ;
- risque de forclusion futur ;
- conditions assurance ;
- règles réglementaires applicables ou à revoir ;
- risques résiduels.

<a id="ct2-124"></a>
#### CT2-124 — 16.3 C08 — Prix

Intégrer sans exposer au Collaborateur non autorisé :

- coûts HSE ;
- coûts garanties ;
- coûts post-réception ;
- pénalités scénarisées ;
- mismatch révision/fournisseurs ;
- scénarios OS/modification ;
- cash timing paiement.

<a id="ct2-125"></a>
#### CT2-125 — 16.4 C10 — Réponse

Tout engagement mesurable du mémoire doit pouvoir être retrouvé et relié à :

- preuve ;
- coût ;
- responsable ;
- sanction éventuelle ;
- passation.

<a id="ct2-126"></a>
#### CT2-126 — 16.5 C12 — Résultat et passation

Ajouter une vue/section de **protection du contrat** plutôt qu’une nouvelle destination globale par défaut :

- échéances de droits ;
- OS/modifications ;
- règlement des comptes ;
- réception ;
- garanties ;
- engagements.

<a id="ct2-127"></a>
#### CT2-127 — 16.6 HOME Patron / Carte d’Engagement

L’accueil Patron peut afficher les décisions et conditions les plus critiques, mais pas une matrice exhaustive de 12 cartes KPI.

Respecter l’UX existante : décision d’abord, preuve à un geste, complexité à deux.

---

<a id="ct2-128"></a>
### CT2-128 — 17. APIs et projections — règles de contrat

Aucune route concrète n’est imposée dans ce document avant audit du style API existant.

Les contrats publics doivent toutefois respecter :

1. `extra=forbid` ou équivalent strict côté commandes ;
2. réponse fermée ;
3. champs financiers absents du schéma Collaborateur, pas seulement `null` ;
4. permissions appliquées avant agrégation ;
5. source/version/locator sur les conclusions critiques ;
6. ETag/révision ou contrôle de concurrence approprié ;
7. idempotence pour actions sensibles ;
8. codes d’erreur métier stables ;
9. aucun message révélant l’existence d’une ressource d’un autre tenant ;
10. dates ISO 8601 avec timezone explicite ;
11. money/unit explicitement typés ;
12. pagination/filtrage bornés.

<a id="ct2-129"></a>
#### CT2-129 — 17.1 Projections

Créer des read models spécialisés si nécessaire plutôt que permettre au frontend de joindre des tables métier.

Exemples conceptuels :

- Carte d’Engagement ;
- calendrier des droits ;
- exposition sanctions ;
- profil réglementaire ;
- couverture des engagements ;
- passation P7.

Ces projections n’acquièrent aucune autorité de mutation.

---

<a id="ct2-130"></a>
### CT2-130 — 18. Migrations et stratégie de données

<a id="ct2-131"></a>
#### CT2-131 — 18.1 Règle générale

Migration additive d’abord.

Séquence recommandée :

1. nouvelles structures vides ;
2. contraintes minimales sûres ;
3. code d’écriture derrière feature flag interne si besoin ;
4. backfill à partir de données réellement mappables ;
5. comparaison ancien/nouveau ;
6. bascule lecture ;
7. durcissement des contraintes ;
8. suppression éventuelle bien plus tard, après preuve.

<a id="ct2-132"></a>
#### CT2-132 — 18.2 Backfill

Interdit d’inventer :

- applicability ;
- dates de droits ;
- version de CCAG ;
- plafond de pénalités ;
- assurance couverte ;
- état de réception ;
- engagement satisfait.

Les enregistrements historiques insuffisants deviennent `UNKNOWN` / `REVIEW_REQUIRED`.

<a id="ct2-133"></a>
#### CT2-133 — 18.3 Réversibilité

Chaque PR de migration documente :

- forward ;
- rollback code ;
- rollback data possible/impossible ;
- données non destructibles ;
- point de restauration ;
- compatibilité version N/N-1 si déploiement progressif.

---

<a id="ct2-134"></a>
### CT2-134 — 19. Observabilité et audit métier

<a id="ct2-135"></a>
#### CT2-135 — 19.1 Événements à journaliser

Sans secrets ni contenu excessif :

- création/revue d’une applicability ;
- qualification d’une dérogation ;
- changement d’une règle de sanction ;
- calcul/recalcul d’une échéance ;
- preuve d’envoi/réception ;
- acceptation/rejet d’un risque ;
- changement de couverture assurance ;
- validation d’un engagement ;
- modification de condition GO ;
- construction/acceptation de passation.

<a id="ct2-136"></a>
#### CT2-136 — 19.2 Corrélation

Toute opération longue ou multi-module conserve `correlation_id`.

<a id="ct2-137"></a>
#### CT2-137 — 19.3 Métriques techniques

- taux d’objets `REVIEW_REQUIRED` ;
- erreurs de parsing de clauses ;
- recalculs après rectificatif ;
- temps de projection ;
- dead letters/outbox ;
- conflits de concurrence ;
- retries idempotents ;
- erreurs d’autorisation ;
- résultats inconnus externes ;
- taux d’abstention IA sur classes critiques.

Ces métriques ne sont pas des KPI marketing sans protocole de mesure métier.

---

<a id="ct2-138"></a>
### CT2-138 — 20. Failure modes et reprise

<a id="ct2-139"></a>
#### CT2-139 — 20.1 Panne IA

- documents restent accessibles ;
- règles déterministes continuent ;
- saisie/revue manuelle disponible ;
- aucune conclusion IA ancienne n’est présentée comme fraîche ;
- tâches en attente explicites.

<a id="ct2-140"></a>
#### CT2-140 — 20.2 Source réglementaire indisponible

- conserver dernière règle validée avec date ;
- ne pas inventer une mise à jour ;
- afficher stale/review due ;
- nouvelles décisions sensibles peuvent exiger revue humaine.

<a id="ct2-141"></a>
#### CT2-141 — 20.3 Import DCE partiel

- ne pas déclencher « dossier complet » ;
- conclusions touchées marquées partielles ;
- Carte d’Engagement signale la couverture de lecture.

<a id="ct2-142"></a>
#### CT2-142 — 20.4 Conflit utilisateur

- préserver les contributions ;
- demander arbitrage ;
- jamais écraser silencieusement une décision ou un événement de droit.

<a id="ct2-143"></a>
#### CT2-143 — 20.5 Timeout externe

- `UNKNOWN_OUTCOME` ;
- pas de retry aveugle pour action non idempotente ;
- réconciliation avant nouvelle tentative.

---

<a id="ct2-144"></a>
### CT2-144 — 21. Tests — contrats obligatoires

Les tests sont des contrats métier. Tout bug critique reçoit un test de régression.

<a id="ct2-145"></a>
#### CT2-145 — 21.1 Test matrix générale

Pour chaque capacité C1 :

- nominal ;
- refus ;
- permission ;
- autre tenant ;
- donnée absente ;
- donnée expirée ;
- version ancienne ;
- rectificatif ;
- retry ;
- idempotence ;
- concurrence ;
- timeout ;
- panne ;
- reprise ;
- résultat inconnu ;
- audit ;
- rollback/migration si applicable.

<a id="ct2-146"></a>
#### CT2-146 — 21.2 Recettes métier REC-29 à REC-45

<a id="ct2-147"></a>
##### CT2-147 — REC-29 — versions contractuelles différentes

Deux Affaires comparables référencent des versions contractuelles différentes. Le système n’applique pas le même délai par défaut ; chaque conclusion cite sa règle/version.

<a id="ct2-148"></a>
##### CT2-148 — REC-30 — dérogation au régime de pénalités

Une clause particulière déroge à la règle de référence. Le plafond générique n’est jamais affiché comme applicable sans qualification.

<a id="ct2-149"></a>
##### CT2-149 — REC-31 — OS non valorisé

Instruction supplémentaire sans prix : aucun coût nul/inclus n’est inventé ; action de revue et préservation ouverte.

<a id="ct2-150"></a>
##### CT2-150 — REC-32 — décompte / délai de réclamation

La réception d’un décompte crée l’événement de droits uniquement si règle et trigger sont établis ; destinataires et preuve sont conservés.

<a id="ct2-151"></a>
##### CT2-151 — REC-33 — exécution aux frais et risques

L’exposition est rendue visible et scénarisable sans conclure automatiquement à la validité juridique de la clause.

<a id="ct2-152"></a>
##### CT2-152 — REC-34 — engagement environnemental vendu

Une promesse mesurable du mémoire devient engagement relié au coût, preuve, responsable et passation.

<a id="ct2-153"></a>
##### CT2-153 — REC-35 — règle réglementaire par date/usage

Deux projets proches mais avec dates/usages différents n’obtiennent pas la même applicability si le champ de la règle diffère.

<a id="ct2-154"></a>
##### CT2-154 — REC-36 — RAT infrastructure

Projet d’infrastructure concerné : le système demande/qualifie l’information sans le confondre avec un autre régime documentaire.

<a id="ct2-155"></a>
##### CT2-155 — REC-37 — assurance hors activité déclarée

Attestation présente mais libellé insuffisant : interdiction de conclure `COVERED` sans revue appropriée.

<a id="ct2-156"></a>
##### CT2-156 — REC-38 — prérequis HSE sans ressource

Exigence détectée, ressource/compétence absente : P2/P3 reste sous condition ou revue ; aucun « conforme ».

<a id="ct2-157"></a>
##### CT2-157 — REC-39 — circuit de facturation public

Une situation de travaux publique conserve son circuit propre ; pas de routage naïf vers le flux B2B standard.

<a id="ct2-158"></a>
##### CT2-158 — REC-40 — règle future

Une règle publiée avec date d’effet future reste inactive sur une Affaire antérieure ; aucune alerte bloquante prématurée.

<a id="ct2-159"></a>
##### CT2-159 — REC-41 — DGD tacite sous conditions

Le système ne conclut à un DGD tacite que si chaque condition de la règle contractuelle applicable, ses dates déclenchantes et ses preuves de notification sont établies. Sinon, état `REVIEW_REQUIRED` et avis humain.

<a id="ct2-160"></a>
##### CT2-160 — REC-42 — pénalités cumulatives

Deux sanctions potentiellement cumulables conservent chacune sa source, sa formule et sa dérogation ; aucune addition ni plafond universel n'est affirmé sans qualification de leur régime commun.

<a id="ct2-161"></a>
##### CT2-161 — REC-43 — engagement non chiffré dans le mémoire

Une promesse mesurable de l'offre sans coût, capacité ou responsable ne devient pas un engagement couvert. P4 expose l'écart et demande une décision Patron sourcée.

<a id="ct2-162"></a>
##### CT2-162 — REC-44 — trésorerie de portefeuille

Plusieurs gains simultanés confrontent ressources, garanties et pic de trésorerie sans transformer une prévision ou un scénario en financement acquis ; si la fonction portefeuille reste différée, son absence est visible.

<a id="ct2-163"></a>
##### CT2-163 — REC-45 — rectificatif modifiant délai ou droit

Un rectificatif touchant une clause temporelle invalide les seules conclusions et échéances dépendantes, conserve l'ancienne version et exige une requalification avant tout affichage de délai certain.

<a id="ct2-164"></a>
#### CT2-164 — 21.3 Recettes techniques supplémentaires

<a id="ct2-165"></a>
##### CT2-165 — TECH-CR-01 — isolation tenant

Créer deux Affaires mêmes identifiants métier dans tenants distincts. Aucun read model, recherche, IA ou export ne croise les données.

<a id="ct2-166"></a>
##### CT2-166 — TECH-CR-02 — fuite financière par projection

Responsable non autorisé appelle toutes les projections Carte d’Engagement. Aucun montant, existence de marge, total, compteur ou inférence financière interdite n’est exposé.

<a id="ct2-167"></a>
##### CT2-167 — TECH-CR-03 — retry deadline

Deux retries identiques d’un événement déclencheur créent un seul événement de droits.

<a id="ct2-168"></a>
##### CT2-168 — TECH-CR-04 — conflit de règle

Une règle réglementaire est supersédée pendant qu’un utilisateur édite une applicability. Le commit ancien est refusé ou requalifié ; aucune décision basée silencieusement sur une version obsolète.

<a id="ct2-169"></a>
##### CT2-169 — TECH-CR-05 — rectificatif DCE

Une nouvelle version du CCAP touche une dérogation et une pénalité. Seuls les objets dépendants sont invalidés ; historique conservé.

<a id="ct2-170"></a>
##### CT2-170 — TECH-CR-06 — formule ambiguë

Parser ne peut pas normaliser une formule : aucun chiffre n’est inventé, `FORMULA_REVIEW_REQUIRED`.

<a id="ct2-171"></a>
##### CT2-171 — TECH-CR-07 — prompt injection

Un CCAP contient une instruction visant le modèle. Le contenu reste data ; aucun outil ni permission élargi.

<a id="ct2-172"></a>
##### CT2-172 — TECH-CR-08 — clôture tâche ≠ clôture droit

Tâche « rédiger réserve » terminée ; événement de droits reste ouvert tant que preuve d’envoi/revue requise manque.

<a id="ct2-173"></a>
##### CT2-173 — TECH-CR-09 — envoi ≠ réception

Preuve d’envoi enregistrée sans accusé : état ne devient pas `ACKNOWLEDGED`.

<a id="ct2-174"></a>
##### CT2-174 — TECH-CR-10 — rollback

Migration ajoute les nouvelles tables/colonnes ; rollback applicatif n’endommage pas les événements historiques.

---

<a id="ct2-175"></a>
### CT2-175 — 22. Golden DCE / corpus de qualification technique

Le corpus doit intégrer des cas hostiles, pas seulement des PDF propres.

Familles minimales :

- marché travaux public simple ;
- multi-lots avec interfaces ;
- réhabilitation site occupé ;
- hôpital/ERP sensible ;
- infrastructure/VRD/réseaux ;
- maintenance multi-sites/accord-cadre ;
- dossier privé ;
- nombreux rectificatifs ;
- vieux scans/tableurs/archives ;
- marché avec clauses particulières fortes.

Annotations supplémentaires v2.0 :

- règle de référence ;
- dérogation ;
- sanction ;
- trigger/délai ;
- engagement mesurable ;
- HSE/prérequis ;
- assurance à revoir ;
- données MIRP manquantes ;
- conséquences prix/capacité ;
- éléments P7.

Le benchmark mesure séparément extraction, locator, qualification et décision humaine. Un bon résultat final obtenu avec une mauvaise source n’est pas accepté.

---

<a id="ct2-176"></a>
### CT2-176 — 23. Plan de construction proposé après audit

Aucune tranche ne démarre en écriture avant validation de l’audit et du statut produit correspondant.

<a id="ct2-177"></a>
#### CT2-177 — T0 — Audit de traçabilité et caractérisation

Objectifs :

- inventaire réel ;
- mapping MASTER → code ;
- tests caractérisation ;
- dette/écarts ;
- plan migration ;
- aucun nouveau comportement visible.

**Gate T0 :** aucune divergence critique non comprise.

<a id="ct2-178"></a>
#### CT2-178 — T1 — Fondation preuve/applicabilité

- réutiliser Source/Evidence existants ;
- regulatory profile minimal ;
- rule store versionné ;
- applicability ;
- invalidation ciblée ;
- tests multi-tenant.

**Gate :** aucune règle IA autoritative.

<a id="ct2-179"></a>
#### CT2-179 — T2 — Contrat et dérogations

- baseline contractuelle ;
- hiérarchie ;
- dérogations ;
- projections ;
- revue humaine.

<a id="ct2-180"></a>
#### CT2-180 — T3 — Sanctions et préservation des droits

- sanctions ;
- simulateur déterministe ;
- RightPreservationEvent ;
- calendrier ;
- idempotence ;
- preuves envoi/réception.

**Gate :** REC-29 à REC-33 verts.

<a id="ct2-181"></a>
#### CT2-181 — T4 — OS / modifications / règlement des comptes

- change instruction ;
- nouveau prix/hypothèse ;
- règlement ;
- réception ;
- DGD ;
- résiliation exposure.

<a id="ct2-182"></a>
#### CT2-182 — T5 — Assurance / HSE / engagements / paiement

- assurance assessment ;
- execution prerequisites ;
- measurable commitments ;
- payment circuit ;
- post-reception obligations.

<a id="ct2-183"></a>
#### CT2-183 — T6 — Carte d’Engagement Patron

Projection uniquement après stabilisation des sources.

Aucune logique métier dans le frontend.

<a id="ct2-184"></a>
#### CT2-184 — T7 — Passation P7 renforcée

- paquet figé ;
- calendrier de droits ;
- engagements ;
- risques ;
- responsables ;
- acceptation études/travaux.

<a id="ct2-185"></a>
#### CT2-185 — T8 — REX et calibration

- prévu/réalisé ;
- sanctions réelles ;
- obligations post-réception ;
- erreurs de préparation ;
- capitalisation contextualisée.

---

<a id="ct2-186"></a>
### CT2-186 — 24. Plan de PR Codex — règles

Chaque PR doit être petite, cohérente et réversible.

<a id="ct2-187"></a>
#### CT2-187 — 24.1 Interdits

- PR « refonte métier » massive ;
- migration + refactor global + nouvelle UX dans le même PR ;
- renommage cosmétique de dizaines de modules pendant une migration métier ;
- nouvelle dépendance sans justification ;
- microservice ;
- event sourcing global ajouté par dogme ;
- moteur de règles externe sans benchmark/besoin ;
- vector DB différente uniquement pour « moderniser » ;
- secrets/test fixtures sensibles.

<a id="ct2-188"></a>
#### CT2-188 — 24.2 Forme d’une PR

Chaque PR indique :

- besoin métier ;
- invariant ;
- état actuel vérifié ;
- choix technique ;
- alternatives rejetées ;
- schéma/migration ;
- droits ;
- concurrence/idempotence ;
- observabilité ;
- tests ;
- rollback ;
- limites ;
- lien de traçabilité MASTER.

<a id="ct2-189"></a>
#### CT2-189 — 24.3 Séquence préférée

1. tests de caractérisation ;
2. contrat domaine ;
3. migration additive ;
4. repository/port ;
5. service applicatif ;
6. policy ;
7. API/projection ;
8. UI ;
9. e2e ;
10. doc/preuve.

---

<a id="ct2-190"></a>
### CT2-190 — 25. Dépendances et choix technologiques

<a id="ct2-191"></a>
#### CT2-191 — 25.1 Principe

Le présent cahier n’autorise aucune dépendance nouvelle par défaut.

Pour chaque besoin, priorité :

1. standard library / capacités existantes ;
2. dépendance déjà présente ;
3. petite dépendance mature et justifiée ;
4. composant lourd uniquement avec benchmark et rollback.

<a id="ct2-192"></a>
#### CT2-192 — 25.2 Moteur de règles

Avant toute bibliothèque : démontrer que les règles validées ne peuvent pas être exprimées par le domaine existant et des prédicats testables.

<a id="ct2-193"></a>
#### CT2-193 — 25.3 Calendriers juridiques

Avant toute lib : inventorier les règles réelles nécessaires. Les jours ouvrés/feriés, fuseaux et conventions ne doivent pas être supposés universels.

<a id="ct2-194"></a>
#### CT2-194 — 25.4 Document parsing

Conserver la stratégie benchmark-first de l’architecture v3.1. Les nouveaux besoins de locators/tableaux/plans doivent être mesurés sur corpus.

---

<a id="ct2-195"></a>
### CT2-195 — 26. Critères de performance

Aucun objectif de performance n’autorise une perte de preuve ou de sécurité.

À mesurer :

- ouverture Carte d’Engagement ;
- requêtes contrat/droits ;
- recalcul après rectificatif ;
- pagination sanctions/engagements ;
- recherche sourcée ;
- ingestion gros DCE ;
- génération des projections ;
- jobs de veille/règles.

Le document ne fixe pas de SLA chiffré inventé. Codex doit établir baseline puis objectif avec mesures.

---

<a id="ct2-196"></a>
### CT2-196 — 27. Exploitation, sauvegarde et reprise

Les nouveaux objets font partie des données critiques à sauvegarder :

- règles validées utilisées dans des décisions ;
- versions contractuelles ;
- événements de droits ;
- preuves d’envoi/réception ;
- décisions ;
- passations ;
- événements append-only.

Une restauration doit préserver les liens vers les documents/hash correspondants.

Le runbook préproduction reste l’autorité opérationnelle à compléter séparément ; ce cahier ne le remplace pas.

---

<a id="ct2-197"></a>
### CT2-197 — 28. Confidentialité, RGPD et conservation

<a id="ct2-198"></a>
#### CT2-198 — 28.1 Minimisation

Ne stocker que ce qui est nécessaire à la finalité métier.

Les appréciations partenaires/personnes doivent être :

- factuelles ;
- sourcées ;
- restreintes ;
- revues ;
- conservées selon durée justifiée.

<a id="ct2-199"></a>
#### CT2-199 — 28.2 Données juridiques/sensibles

Une consultation d’un conseil externe peut être restreinte à un paquet documentaire spécifique.

Ne pas exposer son contenu dans :

- recherche globale non autorisée ;
- embeddings accessibles à d’autres rôles ;
- logs ;
- analytics ;
- prompts génériques.

<a id="ct2-200"></a>
#### CT2-200 — 28.3 Suppression

La suppression physique ne doit pas casser l’intégrité d’un audit encore légalement/conventionnellement requis. Toute politique de purge autonome reste soumise aux décisions produit/juridiques dédiées.

---

<a id="ct2-201"></a>
### CT2-201 — 29. Menaces spécifiques et sécurité applicative

<a id="ct2-202"></a>
#### CT2-202 — 29.1 Prompt injection réglementaire/contractuelle

DCE, email, devis, norme, courrier et fichier tiers sont non fiables.

<a id="ct2-203"></a>
#### CT2-203 — 29.2 Formula injection tableur

Exports CSV/XLSX doivent neutraliser les formules dangereuses selon le format et les conventions d’export retenues.

<a id="ct2-204"></a>
#### CT2-204 — 29.3 Archives

ZIP bombs, path traversal, macros, formats protégés : pipeline quarantine/fail-closed existant à maintenir.

<a id="ct2-205"></a>
#### CT2-205 — 29.4 SSRF / URLs de sources

Une URL trouvée dans un DCE ne doit pas être fetchée automatiquement par un service privilégié sans politique/allowlist adaptée.

<a id="ct2-206"></a>
#### CT2-206 — 29.5 IDOR / tenant

Tout nouvel endpoint de contrat/droits doit passer les mêmes tests d’isolation que le reste du système.

<a id="ct2-207"></a>
#### CT2-207 — 29.6 Export sensible

Un export Carte d’Engagement ou passation applique les droits au moment de l’export et indique sa portée ; il ne devient pas un moyen de contourner la classification.

---

<a id="ct2-208"></a>
### CT2-208 — 30. Matrice de traçabilité MASTER métier → technique

| Domaine MASTER métier | Contrat technique v2.0 | Contexte principal | Gate |
|---|---|---|---|
| Carte d’Engagement | projection sourcée, 12 axes, sans score | Case/Decision + read models | T6 |
| Profil réglementaire | profile + rule store + applicability | Evidence/Regulatory | T1 |
| Éligibilité/preuves | Evidence/Enterprise validation | Evidence/Enterprise | existant + adapt |
| MIRP | InformationRequirement + evidence links | Evidence/Pricing | existant + adapt |
| Interfaces/coûts invisibles | Requirement/Risk/CostFactor | Evidence/Pricing | adapt |
| Marge/trésorerie | deterministic scenarios | Pricing | adapt |
| Portefeuille | Patron-only scenario projection | Pricing/Case | T5/T6 |
| Révision de prix | deterministic formula + indexes | Pricing/Contract | T3/T4 |
| Sous-traitance | partner evidence + obligations | Enterprise/Partner | adapt |
| Hiérarchie contractuelle | ContractBaseline | Contract & Rights | T2 |
| Dérogations | ContractDeviation | Contract & Rights | T2 |
| Pénalités | ContractSanctionRule + simulator | Contract/Pricing | T3 |
| Forclusion/droits | RightPreservationEvent | Contract & Rights | T3 |
| OS/modifications | ContractChangeInstruction | Contract & Rights | T4 |
| Résiliation/frais-risques | TerminationExposure | Contract & Rights | T4 |
| Réception/DGD | SettlementMilestone | Contract/Handover | T4/T7 |
| HSE | ExecutionPrerequisite | Evidence/Handover | T5 |
| Assurance | InsuranceCoverageAssessment | Enterprise/Evidence | T5 |
| Environnement/social | MeasurableCommitment | Response/Handover | T5 |
| Paiement | PaymentCircuit | Pricing/Handover | T5 |
| Post-réception | PostReceptionObligation | Handover | T5/T7 |
| Engagements mémoire | MeasurableCommitment + artifact link | Response | adapt/T5 |
| Dépôt | manifest/hash/evidence | Submission | existant |
| BAFO/mise au point | version/supersession + P6 | Decision/Response | adapt |
| Attribution/rejet | result + evidence | Handover/Learning | adapt |
| Passation | frozen handover package | Handover | T7 |
| REX | contextualized observed outcomes | Learning | T8 |
| IA/provenance | retrieval + structured candidates + abstention | AI Runtime | transversal |

---

<a id="ct2-209"></a>
### CT2-209 — 31. Écarts déjà visibles avec le Cahier technique v1.0

Le v1.0 n’est pas faux ; il est **insuffisamment expressif** pour la profondeur v2.0.

<a id="ct2-210"></a>
#### CT2-210 — Couvert correctement

- monolithe modulaire ;
- tenant ;
- identity/MFA ;
- DCE ;
- source/version/hash/locator ;
- décision ;
- pricing ;
- préparation/remise ;
- append-only ;
- idempotence ;
- RAG borné ;
- tests ;
- déploiement.

<a id="ct2-211"></a>
#### CT2-211 — À étendre

- `decision` doit pouvoir consommer risques/conditions de Contract & Rights sans les posséder ;
- `pricing` doit intégrer les coûts contractuels/HSE/post-réception ;
- `handover` doit transmettre calendrier de droits et règlement des comptes ;
- `enterprise` doit enrichir assurance et partenaires ;
- `evidence` doit porter applicability réglementaire ;
- projections UX doivent intégrer Carte d’Engagement.

<a id="ct2-212"></a>
#### CT2-212 — Absent ou non explicite

- rule store réglementaire ;
- baseline/dérogation contractuelle ;
- penalty rule model ;
- rights preservation ;
- OS/change instruction ;
- DGD/settlement milestones ;
- termination exposure ;
- insurance coverage assessment ;
- execution prerequisites HSE ;
- measurable commitments ;
- payment circuit ;
- post-reception obligations.

---

<a id="ct2-213"></a>
### CT2-213 — 32. Critères d’acceptation avant implémentation C1

Le développement C1 ne commence que si :

1. MASTER métier v2.0 est arbitré ou les sections autorisées sont explicitement identifiées ;
2. Product Freeze est mis à jour ou un ADR produit relié autorise le delta ;
3. audit T0 terminé ;
4. modèle existant mappé ;
5. aucune duplication d’autorité non résolue ;
6. droits/tenants définis ;
7. stratégie migration définie ;
8. Golden DCE contient des cas représentatifs ;
9. validations externes nécessaires identifiées ;
10. rollback documenté.

---

<a id="ct2-214"></a>
### CT2-214 — 33. Critères d’acceptation avant exposition commerciale

Une fonction n’est pas commercialisable parce qu’elle existe en UI.

<a id="ct2-215"></a>
#### CT2-215 — Pénalités

Nécessite corpus annoté, précision/recall, calcul reproductible, faux positifs mesurés, revue juridique des cas sensibles.

<a id="ct2-216"></a>
#### CT2-216 — Préservation des droits

Nécessite versions contractuelles testées, calendriers/destinataires, timezones, cas de forclusion, preuve d’envoi/réception et revue juriste commande publique/construction.

<a id="ct2-217"></a>
#### CT2-217 — Assurance

Nécessite validation courtier/assureur des états et wording.

<a id="ct2-218"></a>
#### CT2-218 — Réglementation

Nécessite workflow de veille, date d’effet, supersession, applicability et absence d’activation prématurée.

<a id="ct2-219"></a>
#### CT2-219 — HSE

Nécessite validation QSE et cas réels.

<a id="ct2-220"></a>
#### CT2-220 — Carte d’Engagement

Nécessite tests utilisateurs Patron et absence de fuite financière.

---

<a id="ct2-221"></a>
### CT2-221 — 34. Rollback stratégique

Si une nouvelle couche s’avère insuffisamment fiable :

- conserver les données source ;
- désactiver la projection/automatisation ;
- revenir à `REVIEW_REQUIRED` + workflow manuel ;
- ne jamais effacer l’historique pour masquer une régression ;
- maintenir la possibilité de produire la réponse/déposer selon le flux V1 lorsque la fonction nouvelle n’est pas indispensable.

Le fallback manuel fait partie du design, pas d’un plan de secours improvisé.

---

<a id="ct2-222"></a>
### CT2-222 — 35. Questions ouvertes / validations externes

Les décisions suivantes ne doivent pas être tranchées par Codex seul :

- sémantique finale des règles CCAG/privé ;
- couverture du corpus privé ;
- wording assurance ;
- règles HSE par corps d’état ;
- MIRP métier ;
- délais/formalismes à encoder comme règles validées ;
- politique de conservation juridique ;
- source et licence des normes/DTU ;
- modalités d’intégration réglementaire automatisée ;
- seuils de risque économique propres à chaque entreprise.

Codex peut préparer les structures et tests, pas créer l’autorité métier manquante.

---

<a id="ct2-223"></a>
### CT2-223 — 36. Instructions de travail à donner à Codex

```text
MISSION
Mettre SMART_AO en capacité de refléter le Cahier Directeur Métier MASTER v2.0,
sans rewrite, sans invention et sans transformer le code en autorité produit.

PHASE 1 — READ ONLY
- lire Product Freeze v2.0 actif, MASTER métier v2.0 et présent Cahier technique v2.1,
  architecture v3.1, catalogue UX, fondations UX et plan global ;
- inventorier le code et les migrations ;
- produire la matrice KEEP/ADAPT/REPLACE/DELETE/ABSENT ;
- produire les écarts et risques ;
- identifier les tests existants ;
- ne modifier aucun cœur métier.

PHASE 2 — PLAN
- proposer la plus petite migration cohérente ;
- séparer domaines, projections et UI ;
- détailler droits, données, idempotence, concurrence, observabilité et rollback ;
- découper en PR indépendantes ;
- chaque PR doit avoir ses tests et critères d’acceptation.

PHASE 3 — IMPLEMENTATION
Uniquement après autorisation propriétaire/technique :
- additive first ;
- tests avant refactor critique ;
- un bug = test de régression ;
- aucun état UNKNOWN/PARTIAL/REVIEW_REQUIRED converti en succès ;
- aucune donnée financière dans un contrat Collaborateur ;
- aucune règle réglementaire ou juridique créée par LLM ;
- aucune suppression historique silencieuse ;
- aucun secret dans Git/log/test/prompt.

STOP CONDITIONS
- contradiction entre MASTER et Product Freeze non arbitrée ;
- migration destructive sans rollback ;
- règle métier non sourcée ;
- état de permission ambigu ;
- absence de preuve pour une conclusion critique ;
- besoin de nouvelle dépendance structurante non benchmarkée.
```

---

<a id="ct2-224"></a>
### CT2-224 — 37. Livrable de sortie attendu de Codex après l’audit

Codex doit produire un rapport structuré :

```text
1. EXECUTIVE VERDICT
2. CURRENT STATE VERIFIED
3. MASTER v2 TRACEABILITY
4. MISSING DOMAIN CONTRACTS
5. DATA MODEL DELTA
6. AUTHORIZATION DELTA
7. AI/RAG DELTA
8. FRONTEND/API DELTA
9. MIGRATION PLAN
10. TEST PLAN
11. OBSERVABILITY PLAN
12. SECURITY REVIEW
13. PR SEQUENCE
14. ROLLBACK
15. BLOCKERS / OWNER DECISIONS
```

Pour chaque constat :

`VERIFIED / PROBABLE / HYPOTHESIS / PROPOSAL / TO_TEST`.

---

<a id="ct2-225"></a>
### CT2-225 — 38. Références documentaires

<a id="ct2-226"></a>
#### CT2-226 — Autorités actuelles du dépôt

- `docs/Archive/01_Cahiers_remplaces/Produit_metier/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v2.0.md`
- `docs/Actifs/02_Produit_et_UX/SMART_AO_Catalogue_Ecrans_Parcours_Produit_OWNER_CONSOLIDATED_v0.3.md`
- `docs/Actifs/02_Produit_et_UX/SMART_AO_Prototype_UX_V0_Fondations_OWNER_CONSOLIDATED_v0.3.md`
- `docs/Actifs/03_Architecture_et_implementation/SMART_AO_Architecture_Logicielle_v3.1_REFERENCE_DIRECTRICE_PHASE0.md`

<a id="ct2-227"></a>
#### CT2-227 — Technique

- `docs/Archive/01_Cahiers_remplaces/Architecture_et_technique/SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v2.1.md` — baseline remplacée par le présent candidat une fois accepté ;
- `docs/Archive/02_Audits/Realignement_V2/MASTER_V2_TRACEABILITY_MATRIX.md` — traçabilité initiale v2 ;
- `docs/Actifs/06_Dependances_et_exploitation/SMART_AO_PREPRODUCTION_VPS_RUNBOOK_v0.1.md` — exploitation, non remplacé ;
- `docs/Actifs/04_Parcours_et_preuves/EXP-01/SMART_AO_EXP_01_CAHIER_TECHNIQUE_EXECUTION_v0.1.md` — tranche spécifique, non remplacée globalement.

<a id="ct2-228"></a>
#### CT2-228 — Nouvelles autorités candidates

- `docs/Archive/01_Cahiers_remplaces/Produit_metier/SMART_AO_CAHIER_DIRECTEUR_METIER_MASTER_v2.0.md` — profondeur métier ;
- `docs/Archive/01_Cahiers_remplaces/Produit_metier/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v2.0.md` — contrat produit actif ;

---

<a id="ct2-229"></a>
### CT2-229 — 39. Décision technique proposée

**DÉCISION APPLIQUÉE :** ce document est la référence `SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v2.1.md` après promotion du Product Freeze v2.0.

Il ne remplace pas l’architecture v3.1 ; il la **spécifie davantage** à partir du nouveau métier.

Il ne remplace pas le catalogue UX ; il expose les nouveaux contrats que le catalogue devra absorber.

Il ne remplace pas le Product Freeze ; il dépend de sa mise à jour.

Il ne donne pas à Codex le droit d’inventer les règles métier manquantes.

La cible reste :

> **un logiciel où chaque conclusion importante peut revenir à sa source, chaque risque à sa conséquence, chaque décision à son autorité, chaque calcul à ses hypothèses, chaque échéance à sa règle, et chaque engagement au contrat réellement vendu.**

---

<a id="ct2-230"></a>
### CT2-230 — 40. Verdict final

Le cahier technique v1.0 était adapté à un SmartAO centré sur DCE, décision, prix, réponse et remise.

Le MASTER métier v2.0 transforme la profondeur attendue : SmartAO doit maintenant être capable de représenter et sécuriser non seulement **ce que l’entreprise répond**, mais **ce qu’elle accepte, ce qu’elle devra exécuter, ce qu’elle devra prouver, les droits qu’elle devra préserver et la façon dont la marge peut se dégrader après attribution**.

La réponse technique n’est pas un rewrite. Elle est l’ajout discipliné de contrats de domaine, de temporalité, d’applicabilité et de preuve au monolithe modulaire existant.

La règle de construction reste :

> **audit réel → petite migration cohérente → tests contractuels → preuve → seulement ensuite extension.**

**Fin — SMART AO Cahier technique d’exécution v2.1 — 24 septembre 2026.**
<!-- END INTEGRATION-CT2 -->


## Contrats techniques détaillés du réalignement — CT3

Ces chapitres font partie du présent cahier actif : **il n'est pas nécessaire d'ouvrir les archives pour disposer de ce détail**. Les identifiants CT3-xxx donnent des ancres uniques. Les exigences métier/techniques sont conservées ; les titres, dates, mentions de promotion et références de version du texte intégré indiquent sa provenance. Ils ne rétablissent pas une ancienne autorité. Les dispositions de consolidation V3.1 en tête gouvernent les conflits et l'ordre de livraison. « À valider », candidat, validation externe ou report ne signifient jamais capacité livrée.

### Accès aux chapitres intégrés

- [CT3-001 — SMART AO — CAHIER TECHNIQUE D’EXÉCUTION INTÉGRAL](#ct3-001)
- [CT3-002 — MASTER CANDIDATE v3.0 — Engagement Control Architecture + héritage technique V2.1](#ct3-002)
- [CT3-003 — PARTIE I — DELTA TECHNIQUE V3](#ct3-003)
- [CT3-004 — SMART AO — CAHIER TECHNIQUE D’EXÉCUTION](#ct3-004)
- [CT3-005 — V3.0 CANDIDATE — Engagement Control Architecture](#ct3-005)
- [CT3-006 — 0. MANDAT](#ct3-006)
- [CT3-007 — 1. BASELINE TECHNIQUE À PRÉSERVER](#ct3-007)
- [CT3-008 — 2. PROBLÈME D’ARCHITECTURE V3](#ct3-008)
- [CT3-009 — 3. ENGAGEMENT CONTROL — LOGICAL BOUNDED CONTEXT](#ct3-009)
- [CT3-010 — 3.1 Statut](#ct3-010)
- [CT3-013 — 3.2 Interdiction](#ct3-013)
- [CT3-014 — 4. ENGAGEMENT CONTROL GRAPH — MODÈLE TECHNIQUE](#ct3-014)
- [CT3-015 — 4.1 Pas d’obligation de graph DB](#ct3-015)
- [CT3-016 — 4.2 Types de relation](#ct3-016)
- [CT3-017 — 4.3 Stable IDs](#ct3-017)
- [CT3-018 — 5. SOURCE REFERENCE V3](#ct3-018)
- [CT3-019 — 5.1 Objectif](#ct3-019)
- [CT3-020 — 5.2 Compatibilité](#ct3-020)
- [CT3-021 — 6. APPLICABILITY ENGINE](#ct3-021)
- [CT3-022 — 6.1 Deux étapes](#ct3-022)
- [CT3-023 — 6.2 Rule version](#ct3-023)
- [CT3-024 — 6.3 Rule status](#ct3-024)
- [CT3-025 — 7. CONTRACT BASELINE](#ct3-025)
- [CT3-026 — 7.1 Aggregate](#ct3-026)
- [CT3-027 — 7.2 Baseline snapshot](#ct3-027)
- [CT3-028 — 8. CONTRACT DEVIATION](#ct3-028)
- [CT3-029 — 9. OBLIGATION & RIGHT](#ct3-029)
- [CT3-030 — 9.1 Obligation](#ct3-030)
- [CT3-031 — 9.2 Right](#ct3-031)
- [CT3-032 — 10. DEADLINE ENGINE](#ct3-032)
- [CT3-033 — 10.1 Principe](#ct3-033)
- [CT3-034 — 10.2 États](#ct3-034)
- [CT3-035 — 11. SANCTION ENGINE](#ct3-035)
- [CT3-036 — 12. BUSINESS IMPACT MODEL](#ct3-036)
- [CT3-037 — 12.1 Objet](#ct3-037)
- [CT3-038 — 12.2 Financial privacy](#ct3-038)
- [CT3-039 — 13. DECISION CONDITION](#ct3-039)
- [CT3-040 — 14. EVENT MODEL — VERTICAL C](#ct3-040)
- [CT3-041 — 15. CHANGE / OS](#ct3-041)
- [CT3-042 — 16. SETTLEMENT / PAYMENT / RECEPTION](#ct3-042)
- [CT3-043 — 16.1 Ownership](#ct3-043)
- [CT3-044 — 16.2 Migration](#ct3-044)
- [CT3-045 — 16.3 Reception](#ct3-045)
- [CT3-046 — 17. P7 HANDOVER MODEL](#ct3-046)
- [CT3-047 — 18. REX CAUSAL MODEL](#ct3-047)
- [CT3-048 — 19. READ MODELS V3](#ct3-048)
- [CT3-049 — 19.1 Patron Engagement Map](#ct3-049)
- [CT3-050 — 19.2 Contract Baseline View](#ct3-050)
- [CT3-051 — 19.3 Rights Calendar](#ct3-051)
- [CT3-052 — 19.4 Change Impact View](#ct3-052)
- [CT3-053 — 19.5 Handover View](#ct3-053)
- [CT3-054 — 20. API](#ct3-054)
- [CT3-055 — 21. FRONTEND](#ct3-055)
- [CT3-056 — 21.1 Principe](#ct3-056)
- [CT3-057 — 21.2 Progressive disclosure](#ct3-057)
- [CT3-058 — 21.3 Confidentialité](#ct3-058)
- [CT3-059 — 22. AI RUNTIME V3](#ct3-059)
- [CT3-060 — 22.1 Structured extraction](#ct3-060)
- [CT3-061 — 22.2 Link proposal](#ct3-061)
- [CT3-062 — 22.3 Abstention](#ct3-062)
- [CT3-063 — 23. BENCHMARK HARNESS](#ct3-063)
- [CT3-064 — 24. TESTS ADVERSARIAUX V3](#ct3-064)
- [CT3-080 — 25. MIGRATIONS](#ct3-080)
- [CT3-081 — 26. CONCURRENCY](#ct3-081)
- [CT3-082 — 27. OBSERVABILITY](#ct3-082)
- [CT3-083 — 28. SECURITY](#ct3-083)
- [CT3-084 — 29. DEPLOYMENT](#ct3-084)
- [CT3-085 — 30. T0 AUDIT OUTPUT](#ct3-085)
- [CT3-086 — 31. ROADMAP TECHNIQUE V3](#ct3-086)
- [CT3-087 — T0 — Rebaseline & documentation](#ct3-087)
- [CT3-088 — T1 — Traceability foundation](#ct3-088)
- [CT3-089 — T2 — Vertical A baseline](#ct3-089)
- [CT3-090 — T3 — Vertical A impact](#ct3-090)
- [CT3-091 — T4 — Vertical B](#ct3-091)
- [CT3-092 — T5 — Vertical C](#ct3-092)
- [CT3-093 — T6 — Settlement](#ct3-093)
- [CT3-094 — T7 — Benchmark](#ct3-094)
- [CT3-095 — T8 — Consolidation](#ct3-095)
- [CT3-096 — 32. DOCUMENTATION À METTRE À JOUR](#ct3-096)
- [CT3-103 — 33. ACCEPTANCE T0](#ct3-103)
- [CT3-104 — 34. ACCEPTANCE VERTICAL A](#ct3-104)
- [CT3-105 — 35. ACCEPTANCE VERTICAL B](#ct3-105)
- [CT3-106 — 36. ACCEPTANCE VERTICAL C](#ct3-106)
- [CT3-107 — 37. NON-OBJECTIFS](#ct3-107)
- [CT3-108 — 38. RÈGLE FINALE DE CONCEPTION](#ct3-108)

<!-- BEGIN INTEGRATION-CT3 -->
<a id="ct3-001"></a>
### CT3-001 — SMART AO — CAHIER TECHNIQUE D’EXÉCUTION INTÉGRAL
<a id="ct3-002"></a>
#### CT3-002 — MASTER CANDIDATE v3.0 — Engagement Control Architecture + héritage technique V2.1

**Date : 30 septembre 2026**  
**Statut : CANDIDAT TECHNIQUE — AUDIT-FIRST**  
**Règle : la PARTIE I V3 prévaut sur les choix de priorité et d’ownership candidats ; la PARTIE II conserve l’intégralité des contrats techniques V2.1 qui ne sont pas explicitement supersédés.**

---

<a id="ct3-003"></a>
### CT3-003 — PARTIE I — DELTA TECHNIQUE V3

<a id="ct3-004"></a>
### CT3-004 — SMART AO — CAHIER TECHNIQUE D’EXÉCUTION
<a id="ct3-005"></a>
#### CT3-005 — V3.0 CANDIDATE — Engagement Control Architecture

**Date : 30 septembre 2026**  
**Statut : CANDIDAT TECHNIQUE — AUDIT DU CODE VIVANT OBLIGATOIRE AVANT IMPLÉMENTATION**  
**Dérive de : Cahier Directeur Produit & Métier V3.0 candidat**  
**Doctrine : migration sélective du monolithe modulaire existant, aucune réécriture globale.**

---

<a id="ct3-006"></a>
### CT3-006 — 0. MANDAT

Ce cahier traduit techniquement la nouvelle orientation V3.

Il ne donne pas l’autorisation de :

- promouvoir V3 comme autorité ;
- supprimer des contrats existants ;
- déplacer un bounded context sans audit ;
- créer une graph database ;
- créer des microservices ;
- casser les API/UX validées.

Avant implémentation : exécuter T0 de la Directive Codex V3.

---

<a id="ct3-007"></a>
### CT3-007 — 1. BASELINE TECHNIQUE À PRÉSERVER

Architecture retenue :

- frontend React + TypeScript ;
- backend Python + FastAPI ;
- PostgreSQL + SQLAlchemy + Alembic ;
- modular monolith ;
- tenant-aware ;
- VPS dédié possible par client ;
- events/outbox/idempotence ;
- stockage documentaire privé ;
- IA derrière ports/policies ;
- fonctions critiques utilisables sans IA.

Invariants :

- tenant résolu serveur ;
- rôle/membership/délégation résolus serveur ;
- MFA/step-up ;
- Patron/Collaborateur ;
- erreurs neutres cross-tenant ;
- append-only lorsque l’historique est un fait métier ;
- résultats externes non présumés ;
- source/version/hash/locator ;
- commandes idempotentes ;
- migrations contrôlées ;
- secrets hors Git/logs/payloads publics.

---

<a id="ct3-008"></a>
### CT3-008 — 2. PROBLÈME D’ARCHITECTURE V3

V2 a introduit de nombreux objets métier spécialisés.

Le risque V3 est double :

1. **fragmentation** — objets profonds dispersés entre DCE, Decision, Pricing, PatronAction, Submission et futurs modules ;
2. **duplication** — créer un nouveau “Contract & Rights” qui recode ce qui existe déjà.

La solution n’est pas “tout déplacer”.

La solution est :

> **auditer les ownerships, standardiser les relations causales et introduire un modèle d’engagement transversal sans casser les agrégats existants.**

---

<a id="ct3-009"></a>
### CT3-009 — 3. ENGAGEMENT CONTROL — LOGICAL BOUNDED CONTEXT

<a id="ct3-010"></a>
#### CT3-010 — 3.1 Statut

`Engagement Control` est d’abord un **bounded context logique candidat**.

Après T0, deux implémentations sont possibles :

<a id="ct3-011"></a>
##### CT3-011 — Option A — nouveau module cohésif

`backend/app/modules/engagement_control/`

Choisir seulement si les concepts Contract/Right/Change/Settlement n’ont pas de propriétaire cohérent existant.

<a id="ct3-012"></a>
##### CT3-012 — Option B — ownership distribué + contrats transversaux

Conserver les écritures dans les modules existants, et exposer des ports/projections Engagement.

Choisir si le coût de déplacement est supérieur au gain.

T0 doit recommander A ou B avec preuves.

<a id="ct3-013"></a>
#### CT3-013 — 3.2 Interdiction

Ne pas créer un module “engagement_control” vide qui devient une façade couplée à tout.

---

<a id="ct3-014"></a>
### CT3-014 — 4. ENGAGEMENT CONTROL GRAPH — MODÈLE TECHNIQUE

<a id="ct3-015"></a>
#### CT3-015 — 4.1 Pas d’obligation de graph DB

Première implémentation : PostgreSQL relationnel.

Une graph database ne peut être adoptée qu’après benchmark sur :

- complexité requêtes ;
- latence ;
- maintenabilité ;
- isolation tenant ;
- migrations ;
- sauvegarde ;
- coût opérationnel.

<a id="ct3-016"></a>
#### CT3-016 — 4.2 Types de relation

Introduire une représentation typée des relations, sans EAV générique incontrôlé.

Candidate :

```python
class EngagementRelationType(str, Enum):
    DERIVED_FROM = "DERIVED_FROM"
    APPLIES_TO = "APPLIES_TO"
    DEVIATES_FROM = "DEVIATES_FROM"
    IMPACTS = "IMPACTS"
    CONDITIONS = "CONDITIONS"
    SATISFIES = "SATISFIES"
    TRIGGERS = "TRIGGERS"
    SUPERSEDES = "SUPERSEDES"
    INVALIDATES = "INVALIDATES"
    EVIDENCED_BY = "EVIDENCED_BY"
    ASSIGNED_TO = "ASSIGNED_TO"
    HANDS_OVER_TO = "HANDS_OVER_TO"
    LEARNS_FROM = "LEARNS_FROM"
```

Ce type n’est pas automatiquement une table unique universelle.

Préférer :

- foreign keys métiers explicites pour relations structurantes ;
- relation table pour liens secondaires/transversaux ;
- projection read model pour navigation.

<a id="ct3-017"></a>
#### CT3-017 — 4.3 Stable IDs

Toute relation persistée référence des IDs stables, tenant-scoped.

Pas de join par titre de document ou label UI.

---

<a id="ct3-018"></a>
### CT3-018 — 5. SOURCE REFERENCE V3

<a id="ct3-019"></a>
#### CT3-019 — 5.1 Objectif

Supprimer progressivement les références critiques sous forme de chaînes libres.

Cible conceptuelle :

```python
SourceReference:
    id
    tenant_id
    source_kind
    document_id
    document_version_id
    anchor_id
    locator_kind
    page
    section
    sheet
    cell_range
    external_uri
    content_hash
    observed_at
    extractor_name
    extractor_version
```

Tous les champs ne sont pas requis simultanément.

<a id="ct3-020"></a>
#### CT3-020 — 5.2 Compatibilité

Créer un adaptateur :

```text
legacy string ref
→ ParsedLegacySourceRef
→ SourceReference when resolvable
→ REVIEW_REQUIRED if ambiguous
```

Ne pas réécrire l’historique silencieusement.

---

<a id="ct3-021"></a>
### CT3-021 — 6. APPLICABILITY ENGINE

<a id="ct3-022"></a>
#### CT3-022 — 6.1 Deux étapes

```text
Extraction
→ candidate facts/rules
```

puis :

```text
Validated facts + rule version
→ deterministic applicability evaluation
```

Le LLM ne décide pas l’applicabilité finale.

<a id="ct3-023"></a>
#### CT3-023 — 6.2 Rule version

Une règle porte :

- `rule_id`
- `version`
- `source_ref`
- `effective_from`
- `effective_to`
- `scope`
- `conditions`
- `exceptions`
- `status`
- `validation_state`.

<a id="ct3-024"></a>
#### CT3-024 — 6.3 Rule status

- `FUTURE`
- `ACTIVE`
- `EXPIRED`
- `REVIEW_REQUIRED`
- `DISABLED`.

Une règle FUTURE ne produit pas d’obligation active.

---

<a id="ct3-025"></a>
### CT3-025 — 7. CONTRACT BASELINE

<a id="ct3-026"></a>
#### CT3-026 — 7.1 Aggregate

Candidate :

```python
ContractBaseline:
    id
    tenant_id
    case_id
    lot_id
    baseline_version
    status
    established_at
    established_by
```

Contenu via références :

- clauses/sources ;
- hierarchy ;
- applicable general texts ;
- particular terms ;
- accepted clarifications ;
- mise au point ;
- award notification.

<a id="ct3-027"></a>
#### CT3-027 — 7.2 Baseline snapshot

P3/P4/P5/P6/P7 doivent référencer un baseline snapshot/version.

Une décision n’est pas liée à “le contrat actuel” abstraitement.

---

<a id="ct3-028"></a>
### CT3-028 — 8. CONTRACT DEVIATION

Candidate fields :

```text
id
baseline_id
reference_rule_ref
deviation_source_ref
deviation_kind
scope
proposed_effect
validation_state
business_impact_state
created_at
superseded_by
```

Aucun `proposed_effect` IA n’est une conclusion validée.

---

<a id="ct3-029"></a>
### CT3-029 — 9. OBLIGATION & RIGHT

Éviter un méga objet “risk”.

<a id="ct3-030"></a>
#### CT3-030 — 9.1 Obligation

```text
source
applicability
holder
beneficiary/addressee
trigger
due rule
required act
required proof
failure consequence
status
```

<a id="ct3-031"></a>
#### CT3-031 — 9.2 Right

```text
source
applicability
trigger
preservation rule
deadline rule
addressee
form
required evidence
status
review
```

---

<a id="ct3-032"></a>
### CT3-032 — 10. DEADLINE ENGINE

<a id="ct3-033"></a>
#### CT3-033 — 10.1 Principe

Pas de deadline “magique”.

Une deadline est :

```text
start fact
+ validated rule
+ calendar policy
+ exceptions
= computed deadline
```

Conserver :

- règle utilisée ;
- inputs ;
- computation version ;
- timezone ;
- holiday/calendar source si utilisé ;
- output ;
- validation.

<a id="ct3-034"></a>
#### CT3-034 — 10.2 États

- `NOT_COMPUTABLE`
- `PROVISIONAL`
- `COMPUTED_REVIEW_REQUIRED`
- `VALIDATED`
- `EXPIRED`
- `SUPERSEDED`.

---

<a id="ct3-035"></a>
### CT3-035 — 11. SANCTION ENGINE

Les montants sont déterministes si la règle est établie.

Entrées :

- trigger ;
- dates ;
- units ;
- basis ;
- amount/base ;
- grace ;
- cap ;
- exemption ;
- cumulation.

Sorties :

- `scenario_central`
- `scenario_stress`
- `max_established`
- `not_established_fields`.

Ne jamais fabriquer un plafond absent.

---

<a id="ct3-036"></a>
### CT3-036 — 12. BUSINESS IMPACT MODEL

<a id="ct3-037"></a>
#### CT3-037 — 12.1 Objet

Une même source peut produire plusieurs impacts.

Candidate :

```text
BusinessImpact
- impact_type
- source_object_ref
- case_id
- amount / duration / capacity unit
- min
- central
- max
- confidence_state
- assumption_refs
- validation_state
- scenario_id
```

Types :

- COST
- CASH
- SCHEDULE
- CAPACITY
- PARTNER
- HSE
- INSURANCE
- CONTRACT
- QUALITY
- POST_RECEPTION.

<a id="ct3-038"></a>
#### CT3-038 — 12.2 Financial privacy

COST/CASH restent Patron-only selon politiques V2.

Les modules non autorisés peuvent connaître :

> “impact économique nécessite revue”

sans montant.

---

<a id="ct3-039"></a>
### CT3-039 — 13. DECISION CONDITION

Les conditions de GO deviennent des objets persistants.

```text
DecisionCondition
- decision_id
- condition_type
- statement
- linked_object_refs
- due_at
- responsible
- evidence_expected
- state
- satisfied_by
- reopened_by
```

États :

- OPEN
- SATISFIED
- WAIVED_BY_AUTHORITY
- EXPIRED
- REOPENED
- SUPERSEDED.

Une condition satisfaite n’est pas supprimée.

---

<a id="ct3-040"></a>
### CT3-040 — 14. EVENT MODEL — VERTICAL C

Créer un concept d’événement métier entrant sans réécrire les événements techniques.

Exemples :

- ORDER_OF_SERVICE
- CHANGE_REQUEST
- ADDENDUM
- SCHEDULE_CHANGE
- PAYMENT_EVENT
- RECEPTION
- RESERVATION
- THIRD_PARTY_DELAY
- INSURANCE_EVENT.

L’événement :

- a une source ;
- a une date ;
- a un acteur/émetteur ;
- a un scope ;
- ne porte pas automatiquement un impact.

Pipeline :

```text
event
→ classify
→ link baseline
→ compute delta candidates
→ human/validated rules
→ impacts
→ actions/deadlines
```

---

<a id="ct3-041"></a>
### CT3-041 — 15. CHANGE / OS

Candidate :

```text
ContractChangeInstruction
- id
- case_id
- event_id
- source_ref
- issuer
- received_at
- scope_delta
- price_status
- time_status
- authority_status
- execution_status
- reservation_required_state
- linked_right_events
```

Ne pas conclure “OS valide/invalide” sans revue compétente.

---

<a id="ct3-042"></a>
### CT3-042 — 16. SETTLEMENT / PAYMENT / RECEPTION

<a id="ct3-043"></a>
#### CT3-043 — 16.1 Ownership

Auditer le `PaymentPostReceptionCycle` existant.

À préserver :

- tenant/Affaire ;
- source obligatoire ;
- prudence ;
- états fermés ;
- idempotence ;
- event.

À enrichir progressivement :

```text
payment_event_type
period
amount_claimed
amount_approved
amount_paid
theoretical_due_at
prudent_cash_at
actual_paid_at
retention
guarantee
rejection_reason
suspension_reason
supporting_documents
source_refs
```

Les champs financiers sont sensibles.

<a id="ct3-044"></a>
#### CT3-044 — 16.2 Migration

Ne pas casser les records existants.

Migration additive + backfill uniquement des champs établis.

<a id="ct3-045"></a>
#### CT3-045 — 16.3 Reception

ReceptionEvent distinct de PaymentEvent.

Liaison :

```text
Reception
→ reservations
→ post-reception obligations
→ settlement/DGD
→ guarantee release
```

---

<a id="ct3-046"></a>
### CT3-046 — 17. P7 HANDOVER MODEL

Créer une projection versionnée, pas forcément une table agrégat unique.

Contenu :

- awarded scope ;
- baseline version ;
- commitments ;
- decision conditions ;
- obligations ;
- rights/deadlines ;
- sanctions ;
- insurance ;
- HSE prerequisites ;
- partners ;
- payment assumptions ;
- reception obligations ;
- open unknowns.

P7 doit conserver le snapshot transmis.

---

<a id="ct3-047"></a>
### CT3-047 — 18. REX CAUSAL MODEL

Candidate :

```text
RexFinding
- source_case_id
- category
- expected_ref
- actual_ref
- variance
- consequence
- root_cause_human
- evidence_refs
- reuse_scope
- validation_state
```

Catégories :

- REQUIREMENT_MISSED
- FALSE_ALERT
- COST_VARIANCE
- CASH_VARIANCE
- SCHEDULE_VARIANCE
- CONTRACT_RIGHT
- SANCTION
- PARTNER
- HSE
- INSURANCE
- COMMITMENT
- PAYMENT
- POST_RECEPTION.

Réemploi impossible sans validation.

---

<a id="ct3-048"></a>
### CT3-048 — 19. READ MODELS V3

Construire des projections read-only au-dessus des agrégats.

<a id="ct3-049"></a>
#### CT3-049 — 19.1 Patron Engagement Map

Read model filtré par droits.

<a id="ct3-050"></a>
#### CT3-050 — 19.2 Contract Baseline View

Sources + deviations + validation.

<a id="ct3-051"></a>
#### CT3-051 — 19.3 Rights Calendar

Tri par deadline, state, responsible.

<a id="ct3-052"></a>
#### CT3-052 — 19.4 Change Impact View

Event → delta → impacts → actions.

<a id="ct3-053"></a>
#### CT3-053 — 19.5 Handover View

Snapshot P7.

Éviter les endpoints qui reconstituent des règles métier dans la route HTTP.

---

<a id="ct3-054"></a>
### CT3-054 — 20. API

Commandes candidates :

```text
EstablishContractBaseline
RecordContractDeviation
ValidateApplicability
RecordObligation
RecordRightPreservationEvent
Compute/ReviewDeadline
RecordBusinessImpact
AttachDecisionCondition
RecordContractChangeEvent
ReviewChangeImpact
RecordSettlementEvent
ValidateP7Handover
RecordCausalRex
```

Les noms sont candidats. Réutiliser commandes existantes si équivalentes.

Command contracts :

- `extra=forbid` ;
- IDs fournis explicitement ;
- idempotency ;
- context serveur ;
- validation syntaxique ≠ validation métier.

---

<a id="ct3-055"></a>
### CT3-055 — 21. FRONTEND

<a id="ct3-056"></a>
#### CT3-056 — 21.1 Principe

Le frontend ne calcule pas :

- deadline contractuelle ;
- pénalité ;
- marge ;
- statut juridique ;
- applicability.

Il affiche une projection serveur avec :

- source ;
- état ;
- formule/raison ;
- inconnus.

<a id="ct3-057"></a>
#### CT3-057 — 21.2 Progressive disclosure

Vue Patron :

1. obstacle/impact ;
2. raison ;
3. preuve ;
4. détails calcul ;
5. historique.

<a id="ct3-058"></a>
#### CT3-058 — 21.3 Confidentialité

Ne jamais agréger avant permissions.

---

<a id="ct3-059"></a>
### CT3-059 — 22. AI RUNTIME V3

<a id="ct3-060"></a>
#### CT3-060 — 22.1 Structured extraction

Toute sortie IA critique utilise schéma fermé :

```text
candidate_type
source_refs
observed_text
normalized_candidate
confidence
uncertainties
```

<a id="ct3-061"></a>
#### CT3-061 — 22.2 Link proposal

L’IA peut proposer :

> clause → potential obligation

mais stocker :

`PROPOSED_LINK`

jusqu’à validation/règle déterministe.

<a id="ct3-062"></a>
#### CT3-062 — 22.3 Abstention

Si source insuffisante :

`UNKNOWN` ou `REVIEW_REQUIRED`.

---

<a id="ct3-063"></a>
### CT3-063 — 23. BENCHMARK HARNESS

Créer un harnais reproductible.

Dataset item :

```text
case_id
corpus_version
expected_critical_findings
expected_unknowns
expected_sources
expected_applicability
expected_impacts
expected_right_triggers
reviewer_1
reviewer_2
disagreement_resolution
```

Metrics :

- recall ;
- precision ;
- source accuracy ;
- applicability ;
- impact linkage ;
- deadline correctness ;
- unknown preservation ;
- review time.

Comparer des exports structurés, pas seulement du texte libre.

---

<a id="ct3-064"></a>
### CT3-064 — 24. TESTS ADVERSARIAUX V3

Au minimum :

<a id="ct3-065"></a>
##### CT3-065 — REC-V3-01
Dérogation détectée mais règle de référence inconnue → `REVIEW_REQUIRED`, pas d’effet juridique affirmé.

<a id="ct3-066"></a>
##### CT3-066 — REC-V3-02
Pénalité sans plafond trouvé → ne jamais introduire un cap par défaut.

<a id="ct3-067"></a>
##### CT3-067 — REC-V3-03
OS reçu avec prix non établi → événement enregistré ; impact coût `UNKNOWN`; right event candidat ; aucune créance affirmée.

<a id="ct3-068"></a>
##### CT3-068 — REC-V3-04
Rectificatif modifie clause source → invalidate seulement dépendances.

<a id="ct3-069"></a>
##### CT3-069 — REC-V3-05
P3 GO sous condition fournisseur → offre gagnée puis devis expiré → condition rouverte/P7 visible.

<a id="ct3-070"></a>
##### CT3-070 — REC-V3-06
Collaborateur demande impact cash via recherche/IA → aucun montant ni inférence sensible.

<a id="ct3-071"></a>
##### CT3-071 — REC-V3-07
Deadline rule FUTURE/non applicable → aucune deadline active.

<a id="ct3-072"></a>
##### CT3-072 — REC-V3-08
Payment contract date ≠ cash date → deux faits distincts.

<a id="ct3-073"></a>
##### CT3-073 — REC-V3-09
Reception with reservations → clôture économique non considérée terminée.

<a id="ct3-074"></a>
##### CT3-074 — REC-V3-10
Rex sur P7 UNKNOWN → ne peut devenir `ENTERPRISE_PATTERN` validé.

<a id="ct3-075"></a>
##### CT3-075 — REC-V3-11
Same event replay → idempotent, no duplicate rights/actions.

<a id="ct3-076"></a>
##### CT3-076 — REC-V3-12
Cross-tenant source ID → neutral refusal.

<a id="ct3-077"></a>
##### CT3-077 — REC-V3-13
LLM prompt injection dans CCAP → aucune élévation outils/droits.

<a id="ct3-078"></a>
##### CT3-078 — REC-V3-14
Legacy string source cannot resolve → keep history + REVIEW_REQUIRED, no fabricated locator.

<a id="ct3-079"></a>
##### CT3-079 — REC-V3-15
Competitor benchmark missing ground truth → no marketing conclusion.

---

<a id="ct3-080"></a>
### CT3-080 — 25. MIGRATIONS

Règles :

- additive first ;
- aucune suppression avant lecture de compatibilité ;
- indices tenant/case/status/deadline ;
- FK tenant-aware ;
- check constraints fermées ;
- data backfill explicite ;
- rollback application séparé du rollback donnée.

Les objets V3 doivent avoir un `schema_version` ou migrations explicites de payload quand événements versionnés.

---

<a id="ct3-081"></a>
### CT3-081 — 26. CONCURRENCY

Risques :

- deux revues d’applicabilité ;
- deux décisions ;
- deux événements de même source ;
- update après supersession.

Utiliser :

- optimistic revision ;
- uniqueness tenant+business key ;
- idempotency keys ;
- conflict status explicite.

Ne jamais “last write wins” sur décision critique.

---

<a id="ct3-082"></a>
### CT3-082 — 27. OBSERVABILITY

Logs structurés sans contenu sensible.

Tracer :

- command_id ;
- correlation_id ;
- case_id ;
- aggregate ;
- result_code ;
- policy refusal ;
- computation version.

Metrics :

- unknown rate ;
- review queue ;
- invalidations ;
- deadline jobs ;
- benchmark metrics ;
- latency extraction vs deterministic evaluation.

---

<a id="ct3-083"></a>
### CT3-083 — 28. SECURITY

Threats V3 :

- prompt injection documents ;
- poisoned source ;
- forged locator ;
- cross-tenant relationship ;
- IDOR on graph edge ;
- leak financial impact via aggregation ;
- malicious export ;
- deadline tampering ;
- rule version substitution.

Ajouter tests spécifiques.

---

<a id="ct3-084"></a>
### CT3-084 — 29. DEPLOYMENT

Aucune nouvelle infra n’est nécessaire pour démarrer V3.

Conserver Docker/PostgreSQL.

Jobs candidats :

- targeted invalidation ;
- deadline evaluation ;
- benchmark batch ;
- document processing.

Pas de worker distribué complexe sans besoin.

---

<a id="ct3-085"></a>
### CT3-085 — 30. T0 AUDIT OUTPUT

Avant code :

1. HEAD baseline ;
2. document authority drift ;
3. code map ;
4. data model map ;
5. duplicate concept map ;
6. source ref debt ;
7. payment ownership audit ;
8. P3/P7 gap ;
9. UX gap ;
10. test gap.

Verdict par capability :

`KEEP / ADAPT / MOVE / REPLACE / ABSENT / TO_TEST`.

---

<a id="ct3-086"></a>
### CT3-086 — 31. ROADMAP TECHNIQUE V3

<a id="ct3-087"></a>
#### CT3-087 — T0 — Rebaseline & documentation
Aucun comportement produit nouveau.

<a id="ct3-088"></a>
#### CT3-088 — T1 — Traceability foundation
Typed source refs / causal link contract / compatibility.

<a id="ct3-089"></a>
#### CT3-089 — T2 — Vertical A baseline
Contract baseline + deviation + applicability.

<a id="ct3-090"></a>
#### CT3-090 — T3 — Vertical A impact
Obligations/rights/sanctions → impacts → decision conditions/P3.

<a id="ct3-091"></a>
#### CT3-091 — T4 — Vertical B
Awarded scope + sold commitments + P7 handover.

<a id="ct3-092"></a>
#### CT3-092 — T5 — Vertical C
Change event/OS + delta + actions/deadlines.

<a id="ct3-093"></a>
#### CT3-093 — T6 — Settlement
Payment/reception/post-reception/DGD + prudent cash.

<a id="ct3-094"></a>
#### CT3-094 — T7 — Benchmark
Golden DCE and comparative/adversarial harness.

<a id="ct3-095"></a>
#### CT3-095 — T8 — Consolidation
Remove duplication, optimize UX, qualify pilot.

Chaque tranche nécessite revue propriétaire si comportement produit change.

---

<a id="ct3-096"></a>
### CT3-096 — 32. DOCUMENTATION À METTRE À JOUR

Codex prépare des patches pour :

<a id="ct3-097"></a>
##### CT3-097 — Autorité
`docs/Actifs/00_INDEX_DOCUMENTATION_ACTIVE.md`

<a id="ct3-098"></a>
##### CT3-098 — Produit
nouveau Product/Metier V3 après validation.

<a id="ct3-099"></a>
##### CT3-099 — Technique
`docs/Archive/03_Propositions/Realignement_V3/SMART_AO_CAHIER_TECHNIQUE_EXECUTION_MASTER_CANDIDATE_v3.0_2026-09-30.md`

<a id="ct3-100"></a>
##### CT3-100 — Plan
`docs/Actifs/00_Pilotage_et_audits/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md`

Mettre à jour :

- date réelle ;
- tranche active réelle ;
- prochaine étape ;
- phase V3 ;
- ancien workstream ;
- baseline tests.

<a id="ct3-101"></a>
##### CT3-101 — Traceability
mettre à jour/créer une matrice V3 :

```text
Requirement V3
→ Product Freeze section
→ Technical contract
→ Code path
→ Migration
→ Tests
→ UI
→ Status
```

<a id="ct3-102"></a>
##### CT3-102 — Architecture
ne modifier architecture v3.1 que si T0 prouve une décision architecturale réelle.

---

<a id="ct3-103"></a>
### CT3-103 — 33. ACCEPTANCE T0

T0 est terminé seulement si :

- HEAD exact green ou écarts expliqués ;
- autorités documentaires listées ;
- aucun Product Freeze promu sans propriétaire ;
- chaque objet Deep Core possède un statut code ;
- duplications identifiées ;
- source refs évaluées ;
- paiement ownership évalué ;
- PR plan borné ;
- rollback décrit ;
- aucune nouvelle feature de parité commencée.

---

<a id="ct3-104"></a>
### CT3-104 — 34. ACCEPTANCE VERTICAL A

Sur un dossier réel de test :

- baseline explicable ;
- deviations sourcées ;
- sanctions distinctes ;
- right/obligation distincts ;
- impacts reliés ;
- UNKNOWN préservés ;
- P3 conditions persistées ;
- Patron peut expliquer le GO ;
- Collaborateur ne voit pas finance privée ;
- rectificatif invalide correctement.

---

<a id="ct3-105"></a>
### CT3-105 — 35. ACCEPTANCE VERTICAL B

- awarded scope exact ;
- P5 package relié ;
- mise au point reliée ;
- P3/P4 conditions reprises ;
- commitments classifiés ;
- rights/deadlines transmis ;
- P7 snapshot versionné ;
- chantier voit ce qui est attendu sans accès Direction indu.

---

<a id="ct3-106"></a>
### CT3-106 — 36. ACCEPTANCE VERTICAL C

- event sourcé ;
- baseline version correcte ;
- delta ;
- impact ;
- deadline/action si calculable ;
- proof expectation ;
- review state ;
- no legal overclaim ;
- idempotent replay ;
- audit history.

---

<a id="ct3-107"></a>
### CT3-107 — 37. NON-OBJECTIFS

V3 ne cherche pas à :

- remplacer juriste, conducteur, DAF, assureur ;
- automatiser une réclamation contentieuse complète ;
- piloter le chantier au quotidien ;
- gérer planning chantier complet ;
- devenir comptabilité ;
- devenir assurance management system ;
- garantir zéro erreur IA.

---

<a id="ct3-108"></a>
### CT3-108 — 38. RÈGLE FINALE DE CONCEPTION

Avant d’ajouter toute nouvelle capacité, demander :

> **Cette fonction renforce-t-elle la continuité entre source, engagement, impact, décision, événement réel, action et preuve ?**

Si non :

- parité nécessaire ? → implémentation minimale ;
- vente bloquée ? → traiter ;
- conformité/sécurité ? → traiter ;
- sinon → différer.

La roadmap V3 est une roadmap de profondeur causale, pas une course au nombre de features.


---
<!-- END INTEGRATION-CT3 -->
