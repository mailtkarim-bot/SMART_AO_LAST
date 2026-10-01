# SMART AO — EXP-05 — Réponse et prix — audit/cadrage v0.1

**Statut : PREUVE D’IMPORT PRIX, REPRISE INCONNUE, COUVERTURE ÉCONOMIQUE, PLAN DE RÉPONSE ET AUDIT P2/P3/P4 TESTÉS · COUVERTURE PARTIELLE**  
**Autorité :** cahier produit/métier `OWNER_CONSOLIDATED v0.4`  
**Périmètre :** importer un DPGF/BPU/Excel, garder la provenance, produire un batch relisible et commiter uniquement les lignes validées

## 1. Question métier

Le Patron doit pouvoir reprendre un fichier de prix sans perdre la source, sans transformer une erreur en zéro et sans publier implicitement un montant. Le produit doit montrer ce qui a été reçu, ce qui est validé, ce qui reste à corriger et si le commit a réellement été confirmé.

Cette tranche ne fabrique pas encore la réponse complète ni un score de décision. Elle ferme la preuve minimale de l’import contrôlé et de son rejeu sûr.

L’audit des portes métier et le gel d’expérience sont détaillés dans [`SMART_AO_EXP_05_P2_P3_P4_AUDIT_CADRAGE_v0.1.md`](SMART_AO_EXP_05_P2_P3_P4_AUDIT_CADRAGE_v0.1.md) et [`SMART_AO_EXP_05_OWNER_EXPERIENCE_FREEZE_v0.1.md`](SMART_AO_EXP_05_OWNER_EXPERIENCE_FREEZE_v0.1.md). P2, P3 et P4 restent explicitement `PARTIAL` tant qu’aucune source et commande dédiées ne permettent de prouver leurs décisions séparées.

## 2. Code déjà disponible

| Étape | Code vivant | Garantie observée |
|---|---|---|
| Preview | `backend/app/modules/pricing/application/import_preview.py` | `.xlsx` uniquement, taille et budget bornés, macros refusées, en-têtes/lignes normalisés, décimales et totaux contrôlés, erreurs et troncature visibles |
| Création | `backend/app/modules/pricing/application/import_creation.py` et `import_creation_handler.py` | le serveur rattache l’affaire et le tenant, persiste un batch et ses lignes normalisées dans une transaction, conserve le `source_sha256` et ne stocke pas le fichier brut |
| Lecture | `backend/app/modules/pricing/application/import_read.py` et `patron_pricing_import.py` | le Patron relit le batch par son identifiant et sa révision ; les lignes, états et erreurs restent lisibles |
| Commit | `backend/app/modules/pricing/application/import_service.py` et `import_handler.py` | verrouillage batch/snapshot, refus des erreurs, de la publication concurrente et de la révision obsolète, lignes financières append-only et reçu sans montant |
| Scénarios | `backend/app/modules/pricing/application/scenario_handler.py` | un scénario part seulement d’un snapshot officiel publié et réutilise les helpers de base de coût et de marge |
| Besoins non couverts | `CaseCapabilityGapRecord` et lecture Case | le Patron voit les écarts existants avec leurs références ; le Collaborateur reste limité aux tâches de son affectation |
| Front | `web/src/features/pricing/usePricingImport.ts`, `PricingPanel.tsx`, `infrastructure/api.ts` | upload, lecture et commit Patron ; état confirmé, rejet connu et résultat inconnu avec rejeu des mêmes identifiants |
| Couverture économique | `CaseResolutionIndexProjection.economic_coverage` et `GET /api/v1/cases/{case_id}/resolution` | le Patron voit l’état des hypothèses, de la validité des devis, de la capacité et du financement sans montant ni décision implicite |
| Plan de réponse | `TechnicalResponseDraftRecord`, package collaborateur et `CollaboratorWizardPanel` | versions, sections, sources et responsable sont relus dans un plan unique ; le contenu reste privé et non financier |

## 3. Contrat minimal de la preuve

1. L’intention d’import reçoit trois identifiants (`command_id`, `idempotency_key`, `correlation_id`) générés côté interface.
2. La preview est calculée côté serveur et devient un batch normalisé ; aucun nom de fichier ou contenu brut ne sert d’autorité après la persistance.
3. Une réponse HTTP connue met l’interface à `PREVIEWED`, `COMMITTED` ou `REPLAYED` selon le reçu réel.
4. Une erreur HTTP connue reste une erreur et libère l’intention afin qu’une nouvelle correction puisse être saisie.
5. Une panne réseau, une expiration ou une réponse non décodable est `UNKNOWN`/« À VÉRIFIER » : aucun succès n’est affiché, les identifiants restent en mémoire et le bouton de rejeu renvoie exactement la même intention.
6. Le commit reprend la même règle avec sa révision de batch et de brouillon. Un reçu `replayed=true` confirme le même résultat métier sans nouvelle ligne.

La reprise est limitée à la session de la page : les identifiants sont conservés dans les `useRef` du hook et ne sont pas inventés à chaque clic. La persistance inter-rechargement pourra être traitée avec la tranche de reprise générale si elle devient nécessaire.

## 3 bis. Marge et scénarios

La marge est calculée par `calculate_cost_basis` en unités monétaires mineures et en points de base entiers. Les réserves, seuils, plancher et cible sont validés avant calcul ; le plancher ne peut dépasser la cible. Un scénario est créé uniquement depuis un snapshot financier `PUBLISHED`, conserve sa révision source et reste Patron-only. Ses transitions de sélection ou d’archivage sont append-only et contrôlées par révision.

La complétude est garantie en amont : le preview marque toute ligne incomplète, le commit refuse les erreurs et le snapshot ne persiste que des agrégats numériques validés. Une donnée inconnue ne devient donc pas `0`. Le domaine accepte encore un chiffre d’affaires nul pour maintenir un brouillon calculable ; son taux de marge à `0` ne doit pas être interprété comme une marge démontrée tant qu’un montant de vente positif n’est pas fourni. Le modèle ne porte pas encore un registre séparé de coûts inconnus : cette limite reste visible dans la couverture et bloque une réponse finale.

## 3 ter. Moyens, partenaires et groupements

Le code vivant possède déjà une preuve réutilisable pour les moyens internes : `EnterpriseCapabilityRecord` accepte les types `EQUIPMENT`, `TEAM` et `METHOD`, ses versions sont datées (`valid_from`/`valid_until`) et ses liens pointent vers des documents d’entreprise. Les documents doivent être `VALIDATED` et non expirés pour être retenus dans une proposition de capacité. `CaseCapabilityProposalRecord` rattache ensuite une proposition à une Affaire, une affectation et une exigence ou tâche ; `CaseCapabilityGapRecord` conserve l’écart `BLOCKING`/`IMPORTANT`. Cette chaîne prouve une capacité documentaire à examiner, pas une réservation de charge ni un engagement contractuel.

L’audit ne trouve aucun agrégat actif pour partenaire ou groupement : pas de membre, mandat, mandataire, lot/part, forme de responsabilité, état de consultation/réponse/rétention/acceptation ou engagement signé. La décision `PARTNER_SELECTION` existe dans le schéma générique des décisions, mais aucune commande ou route ne fournit encore les candidats et leurs preuves. La catégorie financière `SUBCONTRACTING` ne porte qu’un montant de coût et ne prouve donc pas l’existence d’un sous-traitant engagé.

La preuve minimale retenue est la réutilisation de la bibliothèque d’entreprise et des propositions de capacité dans le plan de préparation, avec états `CURRENT`, `EXPIRED` ou `UNKNOWN` et références de source. Partenaires, groupements, mandats et parts restent `NOT_DEMONSTRATED` tant qu’un contrat dédié n’est pas approuvé. Aucun collaborateur ne peut déclarer un engagement au nom de l’entreprise ; toute future sélection devra rester une décision Patron, versionnée et sourcée.

## 3 quater. Confidentialité par rôle et destinataire

L’audit des surfaces confirme que les montants, scénarios et rapports financiers passent par des routes Patron-only et par des contrats de classification financière. La bibliothèque d’entreprise et ses pièces de CV/capacité sont également Patron-only ; le Collaborateur ne reçoit que les propositions et écarts rattachés à son affectation, avec état et source. Le package de préparation Collaborateur ne renvoie ni `storage_key`, ni hash de contenu, ni montant ; le Patron relit seulement les métadonnées de brouillon avant la revue. L’export de remise reste Patron-only, exige une décision de soumission valide et conserve `external_submission: NOT_PERFORMED`.

Cette séparation est une garde serveur, pas une simple règle d’affichage. Les tests de préparation, revue, remise et frontières financières vérifient les rôles, les classifications, l’absence de champs financiers dans les contrats non financiers et le refus d’un contenu financier dans un brouillon technique. Aucune donnée n’est copiée vers `rapports/`.

## 4. Rôles, confidentialité et provenance

- Les routes d’import et de scénarios sont Patron-only côté serveur ; masquer le bouton ne constitue pas une autorisation.
- Le batch garde l’affaire, le type de document, la révision, les lignes normalisées et le hash SHA-256 de la source.
- Le fichier brut n’est pas conservé par cette preuve ; la lecture métier se fait depuis le batch et ses lignes.
- Les erreurs de ligne, la troncature et les totaux sont visibles avant commit. Une donnée absente ou invalide n’est jamais remplacée par `0`.
- Le reçu de commit ne contient ni montant ni désignation : l’interface recharge le brouillon autorisé séparément.
- Les calculs de marge restent des helpers de domaine testés et ne sont pas remplacés par un score opaque.

## 5. États difficiles parcourus

| Situation | État visible | Sortie autorisée |
|---|---|---|
| fichier valide | `PREVIEWED` | relire ou commiter les lignes validées |
| lignes invalides / budget dépassé | `PREVIEWED` avec `truncated` ou erreurs | corriger ou fractionner ; commit refusé si une erreur subsiste |
| preview déjà reçue | `PREVIEWED` avec `replayed=true` | même batch, aucune duplication |
| commit confirmé | `COMMITTED` | recharger le brouillon |
| commit déjà reçu | `REPLAYED` | même résultat, aucune nouvelle ligne |
| réponse preview inconnue | `UNKNOWN` / « À VÉRIFIER » | rejeu avec les mêmes identifiants, sans succès présumé |
| réponse commit inconnue | `UNKNOWN` / « À VÉRIFIER » | rejeu avec les mêmes identifiants et les mêmes révisions |
| autre tenant ou rôle non autorisé | erreur HTTP neutre | aucune existence ni donnée financière révélée |

## 6. Preuve exécutée

Le hook front transmet désormais les identifiants à l’API multipart et au commit. Il conserve le fichier et la commande en attente uniquement lorsque la réponse est inconnue ; une erreur HTTP connue est libérée. `PricingPanel` expose l’état « À VÉRIFIER » et un bouton adapté (« Rejouer la preview » ou « Rejouer le commit »).

La lecture Case réutilise également les `CaseCapabilityGapRecord` existants pour ajouter au périmètre Patron les besoins non couverts. Chaque ligne garde `capability-gap`, l’exigence ou la tâche source lorsqu’elle existe, l’état de sévérité et l’action `REVIEW_CAPABILITY_GAP`. Aucun responsable, échéance ou impact n’est inventé lorsqu’il n’est pas porté par la source ; le Collaborateur ne reçoit pas ces lignes Patron-only.

La même lecture expose maintenant `economic_coverage`, uniquement au Patron. Les hypothèses sont `PROVEN` si un scénario non archivé porte un `assumptions_json` non vide, avec la révision du snapshot dans la référence. La validité de devis reste `NOT_DEMONSTRATED` tant qu’aucun agrégat de devis n’existe : une expiration de document d’entreprise ne devient pas une expiration de devis. La capacité reprend le dernier `OptimizationRunRecord` (`PROVEN`, `INFEASIBLE` ou `UNKNOWN`) et rappelle qu’un run n’est pas une réservation. Le financement est `FORECAST_PRESENT` seulement si un snapshot publié possède une ligne `FORECAST_CASHFLOW`; cette prévision ne prouve pas un financement sécurisé. Les absences restent `NOT_DEMONSTRATED`, sans zéro ni feu vert. La surface « Mes affaires / Revue » charge cette lecture avec la même autorisation et affiche les quatre états sans montant.

Le package collaborateur relit également les `TechnicalResponseDraftRecord` déjà créés pour son affectation. La projection conserve la version, l’état, les sections, les références de source et le rôle responsable ; elle n’expose ni contenu de stockage privé ni donnée financière. `CollaboratorWizardPanel` affiche ce plan à côté de la readiness et des documents générés. Le même panneau peut créer un nouveau brouillon depuis un document généré, des sections et des références saisies ; l’API génère les identifiants de commande et d’idempotence, puis le serveur revalide l’affectation, la révision et l’absence de termes financiers. Une route Patron-only relit les mêmes métadonnées avant la revue. Cette preuve de plan unique ne confond toujours pas brouillon, revue Patron et autorisation P4.

Vérifications réellement exécutées :

- suite front Vitest : **154 tests passés dans 31 fichiers** ; elle couvre preview, commit, rejeu, résultat inconnu, reload, projection et création du plan de réponse ;
- `pnpm typecheck` : **passe** ;
- `pnpm lint` : **passe** ;
- `pnpm build` : **passe** ;
- `git diff --check` : **passe** ;
- suites backend pricing avec PostgreSQL dédié `127.0.0.1:5433` : **121 tests passés**, preview, création, lecture, commit, registre, scénarios, routes et domaine ;
- projection Case des besoins non couverts : **4 tests PostgreSQL ciblés passent**, dont l’isolation Patron/Collaborateur et la conservation des références d’exigence ;
- projection économique Patron : **3 tests applicatifs et 2 tests API PostgreSQL ciblés passent**, avec hypothèses, run de capacité, prévision de trésorerie, absence de contrat de devis et masquage Collaborateur ;
- plan de réponse : **42 tests PostgreSQL préparation/revue/routes ciblés passent**, avec lecture Collaborateur et Patron-only des brouillons, création idempotente et refus financier ;
- confidentialité et remise : **46 tests PostgreSQL préparation/revue/remise/frontières financières passent**, avec séparation des rôles, refus des champs financiers et décision de soumission opposable ;
- affichage de la couverture dans la revue front : **31 fichiers, 152 tests**, typecheck, lint et build passent ; le client appelle la route Case et ne rend la couverture qu’au Patron ;
- Ruff et mypy ciblés backend déjà exécutés sur la base EXP-04 : **passent**.

## 7. Limites explicites

- Cette tranche ne couvre pas encore la complétude de la réponse, la gestion des partenaires/groupements ni une réservation de capacité ou un financement contractuel.
- La projection économique est une lecture de couverture : elle ne calcule pas de total, ne crée pas de devis et ne remplace pas les agrégats financiers ou optimisation.
- Le front ne conserve les identifiants que pendant la durée de vie de la page ; aucun stockage navigateur n’est introduit sans preuve de besoin.
- Le commit dépend toujours d’un brouillon financier existant et de ses révisions attendues.
- Les scénarios supposent un snapshot officiel publié ; ils ne valident pas à eux seuls une offre finale ni un dépôt.
- Les besoins non couverts sont maintenant lisibles dans « À résoudre », mais aucune correspondance automatique entre poste de prix et exigence n’est acceptée comme couverture tant qu’elle n’est pas vérifiée.

## Étape suivante

Contrôler P2/P3/P4, les conflits et les versions, puis exécuter la revue verticale et le gel d’expérience EXP-05.
