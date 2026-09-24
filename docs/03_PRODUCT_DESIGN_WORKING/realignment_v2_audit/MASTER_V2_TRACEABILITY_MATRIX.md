# SMART AO — Traçabilité du candidat Product Freeze v2 vers le code

**24 septembre 2026 · T0 · autorité active : Product Freeze v1.0**  
`COVERED/PARTIAL/MISSING/DEFERRED/EXTERNAL_VALIDATION` comparent la **capacité v2 proposée** au code inspecté ; ils ne déclarent pas une non-conformité à l'autorité v1.0.

**Niveau de preuve de chaque constat :** une classe, un champ, une route ou un statut UX cité dans le dépôt est `VERIFIED` ; une absence déduite de recherches ciblées est `PROBABLE`, à confirmer par test de caractérisation avant PR ; la colonne « Suite » est `PROPOSAL` ; tout comportement v2 reste `TO_TEST`. Le statut du tableau décrit la couverture, pas le niveau de preuve.

| Décision proposée | État code | Preuve ou limite vérifiée | Suite |
|---|---|---|---|
| PF2-01 Protéger les droits dans la promesse | MISSING | Le Product Freeze v1.0 §1 n'a pas cette obligation ; P7 actuel est un résultat append-only simple (`patron_action/.../p7.py`). | Validation propriétaire avant changement de promesse. |
| PF2-02 Carte 12 axes | PARTIAL | Dossier décision Patron et risques existent ; pas de projection 12 axes dans `decision/`, `web/src/features/decision/`. | T6 après stabilisation des sources. |
| PF2-03 Profil/règles réglementaires datées | MISSING | Aucun modèle/route d'applicabilité trouvé dans les zones inspectées. | T1, source/version/date/état et abstention. |
| PF2-04 Contrat de référence/dérogation | PARTIAL | Signaux CCAP/CCTP sourcés (`dce/application/contract_risk_read.py`) ; pas de baseline et override qualifiés. | T2 ; comparer côte à côte règle et clause. |
| PF2-05 Sanctions structurées | PARTIAL | `DecisionRiskRecord` porte un risque sourcé, pas formule/base/plafond/cumul. | T3, aucun calcul sans paramètres validés. |
| PF2-06 Événement de droit | MISSING | Aucun modèle de délai de droit, preuve d'envoi/réception et échéance calculée trouvé. | T3 ; calendrier `UNKNOWN/REVIEW_REQUIRED`. |
| PF2-07 OS/modifications | MISSING | Aucun agrégat de prescription/valorisation OS trouvé. | T4, distinguer ordre, réception, réserve, prix. |
| PF2-08 Réception/comptes/DGD/post-réception | PARTIAL | P7 et REX existent ; la séquence de comptes, conditions DGD et obligations post-réception ne sont pas modélisées comme telles. | T4/T5 ; aucun DGD tacite déduit. |
| PF2-09 Résiliation/substitution | MISSING | Pas de contrat d'exposition de rupture trouvé ; un risque générique ne le couvre pas. | T4, revue humaine. |
| PF2-10 Assurance ↔ prestation | PARTIAL | Pièces et capacités d'entreprise existent ; aucune évaluation de couverture par prestation trouvée. | T5 ; état `NOT_ESTABLISHED` par défaut. |
| PF2-11 HSE ↔ ressource/coût/délai | PARTIAL | Exigences DCE et écarts de capacité existent ; pas de prérequis d'exécution HSE dédié. | T5 ; ne pas confondre pièce détectée et capacité réelle. |
| PF2-12 Engagement mesurable | PARTIAL | Brouillon technique versionné existant ; pas de registre KPI/coût/preuve/responsable/passation. | T5, traçabilité offre → P7. |
| PF2-13 Circuit de paiement | MISSING | Scénarios/prévisions financiers présents ; acteurs, contrôles et rejets de paiement non représentés. | T5 ; séparer délai légal et hypothèse cash. |
| PF2-14 P2/P3/P4/P6/P7 enrichis | PARTIAL | Portes/conditions et P6/P7 existent ; les nouveaux critères ne sont pas dans les contrats actuels. | T6/T7 après faits métiers et tests. |
| PF2-15 Validation externe spécialisée | EXTERNAL_VALIDATION | Les garde-fous de rôle/IA existent, mais expertise juridique, assurance, QSE et corpus ne sont pas des preuves disponibles dans le dépôt. | Attestations datées et bornées, jamais inférées du code. |
| PF2-16 Socle C1 en V1, avancé en V1.x | CONTRADICTED/DEFERRED | Le v1.0 §10 reporte partenaires/groupements structurés et automatisation juridique ; le candidat avance des contrats C1 en V1. | Arbitrage de périmètre propriétaire avant PR. |

**Écart documentaire constaté et corrigé dans le candidat :** le Product Freeze v2 §23 imposait REC‑29 à REC‑45 alors que le cahier technique v2.1 §21.2 s'arrêtait à REC‑40. Les cinq recettes ont été ajoutées au cahier technique candidat le 24 septembre. Leur présence documentaire ne vaut ni implémentation ni validation métier.

**Verdict de cet audit T0 initial :** `READY_WITH_BLOCKERS` pour préparer l'implémentation, sous réserve de la promotion propriétaire, de la caractérisation des absences `PROBABLE` et de la validation des règles sensibles. Aucun `MISSING` C1 n'est réputé résolu par une simple référence à un risque générique.
