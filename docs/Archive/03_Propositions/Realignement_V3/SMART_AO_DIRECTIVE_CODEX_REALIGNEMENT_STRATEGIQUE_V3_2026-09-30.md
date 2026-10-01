# SMART AO — DIRECTIVE CODEX DE RÉALIGNEMENT STRATÉGIQUE V3
## Pivot immédiat : du logiciel d’analyse DCE vers le système de maîtrise des engagements BTP

**Date : 30 septembre 2026**  
**Statut : CANDIDAT PROPRIÉTAIRE À EXÉCUTER EN MODE AUDIT-FIRST**  
**Destinataire : Codex / équipe d’implémentation SMART AO**  
**Objet : interrompre l’expansion fonctionnelle horizontale, remettre les autorités documentaires en cohérence, auditer le code vivant puis réaligner l’implémentation sur le nouveau Deep Core.**

---

# 0. ORDRE EXÉCUTIF

À compter de la réception du présent paquet, **ne pas démarrer une nouvelle feature de parité IA** avant d’avoir terminé les actions T0 décrites ci-dessous.

La direction produit change de centre de gravité :

> **SMART AO n’est plus piloté comme un “assistant IA de réponse aux appels d’offres”.**
>
> **SMART AO doit devenir un système de maîtrise des engagements BTP : il relie ce que le dossier impose, ce que l’entreprise décide et vend, ce qui se produit réellement, et ce qu’elle doit faire pour protéger sa marge, sa trésorerie, ses délais et ses droits.**

Le DCE reste l’entrée principale. Il n’est plus la frontière du produit.

La chaîne cible devient :

```text
SOURCE / VERSION / PREUVE
        ↓
CLAUSE / EXIGENCE / INCONNU / HYPOTHÈSE
        ↓
APPLICABILITÉ
        ↓
OBLIGATION / DROIT / DÉROGATION / SANCTION
        ↓
IMPACT
coût · cash · délai · ressource · partenaire · assurance · HSE
        ↓
DÉCISION PATRON / CONDITION DE GO
        ↓
ENGAGEMENT VENDU / PAQUET AUTORISÉ
        ↓
ÉVÉNEMENT RÉEL
OS · avenant · changement · paiement · réception · réserve · réclamation
        ↓
ACTION / ÉCHÉANCE / PREUVE
        ↓
DROIT PRÉSERVÉ / EXPOSITION / REVIEW_REQUIRED
        ↓
DGD / CLÔTURE
        ↓
REX VALIDÉ ET RÉUTILISABLE
```

Cette continuité est désormais le **Deep Core**.

---

# 1. POURQUOI LE PIVOT EST OBLIGATOIRE

## 1.1 Constat marché

Les capacités suivantes ne doivent plus être considérées comme différenciantes à elles seules :

- veille d’appels d’offres ;
- résumé DCE ;
- chat/RAG sur DCE ;
- extraction RC/CCAP/CCTP ;
- extraction d’exigences ;
- mémoire technique assistée ;
- DC1/DC2/DC4 et administratif ;
- Go/No-Go simple ou score ;
- provenance document/page ;
- contradictions entre pièces ;
- DPGF/BPU/DQE assisté ;
- base de connaissances entreprise ;
- analyse générique de pénalités ou de risques CCAP.

Elles restent nécessaires pour la parité du produit, mais elles ne doivent plus consommer l’essentiel du temps d’innovation.

## 1.2 Pression sur Contract & Rights

Le marché commence également à revendiquer :

- analyse des dérogations au CCAG ;
- pénalités et garanties ;
- délais de paiement ;
- ordres de service ;
- travaux supplémentaires ;
- réserves/contestation ;
- réception/DGD ;
- mémoire en réclamation.

Conclusion :

> **détecter un objet contractuel n’est plus suffisant. Le moat doit porter sur la continuité causale, la gouvernance, l’applicabilité, la temporalité et la preuve.**

## 1.3 Ce qui reste défendable

Le territoire à renforcer est :

1. chaîne d’autorité P0–P7 sans score décisionnel opaque ;
2. états prudents `UNKNOWN`, `PARTIAL`, `REVIEW_REQUIRED`, `NOT_PERFORMED` ;
3. séparation Patron/Collaborateur jusque dans les recherches, exports, agrégats et contexte IA ;
4. reconstruction du contrat réellement applicable ;
5. causalité `source → obligation/droit → impact → décision → engagement → événement réel → action → preuve → REX` ;
6. préservation temporelle des droits et obligations ;
7. lien déterministe entre contrat, marge, cash, délai, capacité et exécution ;
8. transmission offre → chantier sans perte des hypothèses/conditions ;
9. apprentissage validé à partir des écarts réels.

---

# 2. RÈGLE DE TRANSITION : PAS DE REWRITE

Le repo vivant est le socle. Ne pas repartir de zéro.

Tout composant existant reçoit l’un des statuts :

- `KEEP` — conforme et réutilisable ;
- `ADAPT` — bon socle, contrat à enrichir ;
- `MOVE` — bonne capacité, mauvais propriétaire de domaine ;
- `REPLACE` — concept incompatible avec V3 ;
- `DELETE` — redondant ou contraire ;
- `ABSENT` — capacité normative non encore matérialisée ;
- `TO_TEST` — présence probable mais non démontrée.

**Interdiction :** créer un nouveau module ou une nouvelle table uniquement parce qu’un nom apparaît dans le cahier V3. D’abord rechercher l’équivalent conceptuel dans le code existant.

---

# 3. T0 — ACTION IMMÉDIATE OBLIGATOIRE

Avant toute nouvelle PR fonctionnelle :

## 3.1 Rejouer la baseline au HEAD exact

Exécuter et enregistrer :

- full backend ;
- full frontend ;
- typecheck ;
- lint ;
- build ;
- migrations sur base fraîche ;
- `git diff --check` ;
- gates sécurité/architecture déjà actives.

Le dernier full run documenté ne doit pas être supposé couvrir les commits postérieurs.

Sortie :
`T0_CURRENT_HEAD_BASELINE.md`

Le document contient :

- SHA exact ;
- commandes exactes ;
- nombres de tests ;
- échecs/skips ;
- environnement ;
- durée informative si disponible ;
- verdict `GREEN / PARTIAL / RED`.

## 3.2 Synchroniser la gouvernance documentaire

Auditer au minimum :

- `docs/Actifs/00_INDEX_DOCUMENTATION_ACTIVE.md`
- Product Freeze actif ;
- cahier technique actif/candidat ;
- architecture v3.1 ;
- catalogue UX ;
- fondations UX ;
- plan global de conception/réalisation ;
- traceability matrix ;
- documents Txx récents.

Produire :
`T0_DOCUMENT_AUTHORITY_DRIFT_AUDIT.md`

Pour chaque document :

| Document | Autorité annoncée | Réalité actuelle | Dérive | Action |
|---|---|---|---|---|
| ... | ... | ... | NONE/MINOR/MAJOR | KEEP/UPDATE/ARCHIVE/PROPOSE |

Ne promouvoir **aucun** nouveau Freeze sans validation propriétaire explicite.

## 3.3 Auditer le code contre le Deep Core

Produire :
`T0_DEEP_CORE_CODE_MAP.md`

Cartographier :

- source/provenance/version ;
- Evidence ;
- Requirement/Unknown/Hypothesis/Contradiction/Risk ;
- Decision P0–P7 ;
- Pricing/cash ;
- Submission/P5/hash/manifest/evidence ;
- Handover/P6/P7 ;
- REX ;
- payment/post-reception ;
- contract baseline/deviation ;
- sanctions ;
- right preservation ;
- OS/change ;
- settlement/DGD ;
- insurance ;
- HSE prerequisites ;
- measurable commitments.

Chaque ligne :

```text
CONCEPT
→ code path(s)
→ tests
→ migration(s)
→ API/UI
→ status KEEP/ADAPT/MOVE/REPLACE/ABSENT/TO_TEST
→ gap
→ risk
```

---

# 4. DOCUMENTS V3 À UTILISER

Le présent paquet contient :

1. `SMART_AO_CAHIER_DIRECTEUR_PRODUIT_METIER_V3_CANDIDATE_2026-09-30.md`
2. `SMART_AO_CAHIER_TECHNIQUE_EXECUTION_V3_CANDIDATE_2026-09-30.md`
3. `SMART_AO_DIRECTIVE_CODEX_REALIGNEMENT_STRATEGIQUE_V3_2026-09-30.md`
4. `SMART_AO_PACKAGE_REALIGNEMENT_V3_README_2026-09-30.md`

Pendant la transition :

- les autorités actuellement promues dans GitHub restent juridiquement/documentairement actives ;
- V3 est la cible candidate à confronter au code ;
- Codex prépare les patches documentaires ;
- le propriétaire valide la promotion ;
- seulement ensuite les références actives sont basculées.

---

# 5. NOUVELLE SEGMENTATION PRODUIT

## 5.1 PARITY CORE — nécessaire, investissement borné

Maintenir au niveau attendu du marché :

- Radar/veille ;
- ingestion DCE ;
- parsing/OCR ;
- synthèse ;
- exigences ;
- provenance ;
- contradictions ;
- versions ;
- mémoire technique ;
- administratif ;
- import chiffrage ;
- Go/No-Go de premier niveau ;
- mémoire entreprise.

Règle :

> **pas de projet autonome d’innovation sur une feature de parité sans preuve qu’elle bloque le Deep Core, une vente ou une obligation réglementaire.**

## 5.2 SMARTAO DEEP CORE — priorité absolue

Le développement doit prioriser :

- Engagement Control Graph ;
- Contract Baseline / Deviation ;
- droits et obligations temporels ;
- sanctions ;
- impact business déterministe ;
- conditions de GO ;
- engagements vendus ;
- OS/modifications/événements ;
- paiement/règlement/post-réception ;
- P7/handover renforcé ;
- REX causal ;
- Carte d’Engagement Patron.

## 5.3 DEFERRED

Mettre en attente sauf nécessité démontrée :

- multiplication de dashboards ;
- nouveaux agents généralistes ;
- automatisation autonome du dépôt ;
- remplacement complet du logiciel de chiffrage ;
- ERP chantier ;
- graph database par principe ;
- microservices par anticipation ;
- refonte totale UI ;
- 104 surfaces traitées comme objectif de construction séquentiel indépendant de la valeur.

Les 104 surfaces restent un **contrat de couverture**, pas une obligation de fabriquer 104 pages avant validation marché.

---

# 6. NOUVEAU NOYAU : ENGAGEMENT CONTROL GRAPH

## 6.1 Principe

Le terme “Graph” décrit une relation métier. Il **n’impose pas** une base graphe.

Le système doit pouvoir relier explicitement :

- source ;
- clause ;
- exigence ;
- fait ;
- inconnu ;
- hypothèse ;
- contradiction ;
- règle applicable ;
- dérogation ;
- obligation ;
- droit ;
- sanction ;
- coût ;
- cash ;
- délai ;
- capacité ;
- assurance ;
- HSE ;
- partenaire ;
- décision ;
- condition ;
- engagement vendu ;
- événement réel ;
- action ;
- échéance ;
- preuve ;
- règlement/réception ;
- REX.

## 6.2 Invariant causal

Toute conséquence critique doit pouvoir répondre :

1. **d’où vient-elle ?**
2. **pourquoi s’applique-t-elle ?**
3. **qu’est-ce qu’elle change ?**
4. **qui doit décider/agire ?**
5. **avant quand ?**
6. **quelle preuve manque/existe ?**
7. **qu’est-ce qui se passe si rien n’est fait ?**

## 6.3 Invalidation

Un changement de source/version/règle :

- n’efface pas l’historique ;
- invalide seulement les conclusions dépendantes ;
- place les dérivés affectés dans un état explicite ;
- déclenche une réévaluation bornée ;
- ne convertit jamais automatiquement un inconnu en succès.

---

# 7. TROIS VERTICALES PRIORITAIRES

## VERTICAL A — AVANT DE SIGNER

Entrée :
DCE + mémoire entreprise + partenaires + prix importé.

Chaîne :

```text
Contract Baseline
→ Deviations
→ Obligations / Sanctions / Rights
→ Business Impact
→ Conditions
→ P3
```

Question Patron :

> **“Qu’est-ce qui, dans ce marché, peut consommer ma marge, ma trésorerie, mon planning ou mes droits — et qu’est-ce qui n’est pas encore établi ?”**

## VERTICAL B — SI JE GAGNE

Entrée :
offre autorisée + résultat gagné + contrat/mise au point.

Chaîne :

```text
P5 package
→ awarded perimeter
→ accepted deviations
→ conditions of GO
→ sold commitments
→ execution prerequisites
→ rights/obligations calendar
→ P7 handover
```

Question chantier :

> **“Qu’avons-nous réellement vendu et accepté, que devons-nous tenir, prouver et protéger ?”**

## VERTICAL C — QUELQUE CHOSE CHANGE

Entrée :
OS / avenant / événement / instruction / retard / situation / réception.

Chaîne :

```text
Event
→ applicable baseline
→ delta
→ scope/cost/time/cash impact
→ right/obligation triggered
→ deadline
→ action
→ evidence
→ human review
```

Question :

> **“Qu’est-ce que cet événement change, combien, avant quand, et quelle action sûre protège notre position ?”**

---

# 8. BENCHMARK CONCURRENTIEL COMME GATE PRODUIT

Le benchmark devient une exigence de qualification.

Sur des DCE autorisés/anonymisés comparables, tester SMART AO contre :

- Smart BTP ;
- TenderCrunch ;
- TenderStrike ;
- un assistant généraliste puissant ;
- autre concurrent pertinent au moment du test.

Ne pas mesurer la beauté du résumé.

Mesurer :

- exigence critique manquée ;
- clause critique manquée ;
- fausse alerte critique ;
- source exacte ;
- version exacte ;
- applicabilité ;
- lien vers coût/délai/cash/capacité ;
- détection d’un droit/obligation déclenché ;
- échéance correcte ;
- abstention correcte ;
- temps de revue humaine ;
- décision Patron explicable ;
- conservation du lien avant-offre → événement réel.

Aucune revendication marketing comparative n’est autorisée sans protocole, corpus, date, version et résultats conservés.

---

# 9. RÈGLES D’IA

L’IA peut :

- extraire ;
- classer ;
- rapprocher ;
- proposer un lien causal ;
- proposer une question ;
- préparer un brouillon ;
- expliquer une source ;
- suggérer une action à revoir.

L’IA ne peut jamais seule :

- déclarer une règle applicable ;
- calculer un délai juridique comme vérité sans règle versionnée ;
- déclarer une couverture assurantielle ;
- conclure à un droit acquis/perdu ;
- autoriser P3/P4/P5/P6/P7 ;
- fixer le prix final ;
- déposer ;
- transformer `UNKNOWN/PARTIAL/REVIEW_REQUIRED` en succès.

Les calculs de dates, montants, scénarios et statuts critiques doivent être déterministes une fois les faits/règles validés.

---

# 10. SOURCE REFERENCES — DETTE À TRAITER

Les nouvelles capacités ne doivent pas multiplier les références textuelles libres.

Cible :

```text
SourceReference
- tenant_id
- document_id / external_source_id
- document_version_id
- anchor_id / locator
- page / section / cell / article si disponible
- content_hash
- source_kind
- observed_at
- parser/version si dérivé
```

Les anciennes chaînes de provenance restent compatibles pendant migration, mais toute nouvelle tranche Deep Core doit préférer une référence typée ou un adaptateur vers le modèle de preuve existant.

---

# 11. OWNERSHIP DE DOMAINE — AUDIT AVANT DÉPLACEMENT

Le cycle paiement/post-réception existe actuellement dans Pricing.

Ne pas le déplacer immédiatement.

Auditer d’abord :

- sa responsabilité métier ;
- ses dépendances ;
- ses projections ;
- ses tests ;
- ses consumers.

Cible conceptuelle :

```text
Contract / Engagement Control
        ↓
Settlement / Payment event
        ↓
Pricing & Cash projection
```

Si l’audit confirme que Pricing devient un “god context”, proposer un déplacement progressif `MOVE`, additive migration, adaptateurs de compatibilité et rollback.

---

# 12. PRÉSERVATION DE L’EXISTANT

Ne pas affaiblir :

- tenant scoping ;
- MFA/step-up ;
- rôle serveur ;
- Patron/Collaborateur ;
- idempotence ;
- append-only quand l’historique compte ;
- neutralité des erreurs cross-tenant ;
- exactitude du manifeste P5 ;
- hashes/provenance ;
- dépôt humain ;
- résultats externes `UNKNOWN/PARTIAL/NOT_PERFORMED` ;
- invalidation ciblée ;
- REX validé avant réemploi ;
- fonctionnement critique sans IA.

---

# 13. PLAN DE PR APRÈS T0

Aucune PR fonctionnelle avant validation du paquet T0.

Puis proposer, pas exécuter silencieusement :

### PR-A — Traceability foundations
Typed source references, causal links, migration additive, compatibility.

### PR-B — Vertical A / baseline
Contract baseline + rule/deviation + applicability + Patron projection.

### PR-C — Vertical A / impacts
Sanctions/obligations/rights → business impacts → P3 conditions.

### PR-D — Vertical B
Awarded contract + sold commitments + rights/obligation calendar + P7.

### PR-E — Vertical C
Change event/OS → delta → impacts → deadline/action/evidence.

### PR-F — Settlement
Payment/settlement/reception/DGD projection + prudent cash.

### PR-G — Benchmark harness
Golden DCE / adversarial recipes / comparative metrics.

Chaque PR doit être réversible, bornée et prouvée.

---

# 14. DEFINITION OF DONE POUR CHAQUE TRANCHE

Une tranche n’est pas terminée parce qu’un endpoint existe.

Elle doit démontrer :

1. autorité documentaire ;
2. use case métier ;
3. modèle et invariants ;
4. migration ;
5. permissions ;
6. idempotence/concurrence ;
7. source/provenance ;
8. états difficiles ;
9. API fermée ;
10. front utile si nécessaire ;
11. tests domaine ;
12. tests PostgreSQL ;
13. tests API ;
14. tests refus/tenant ;
15. régression ;
16. rollback ;
17. documentation ;
18. preuve exploitable par le propriétaire.

---

# 15. SORTIE ATTENDUE DE CODEX AVANT TOUTE MODIFICATION DE CŒUR

Répondre avec un paquet contenant :

- `T0_CURRENT_HEAD_BASELINE.md`
- `T0_DOCUMENT_AUTHORITY_DRIFT_AUDIT.md`
- `T0_DEEP_CORE_CODE_MAP.md`
- `T0_KEEP_ADAPT_MOVE_REPLACE_ABSENT.md`
- `T0_V3_DATA_DELTA.md`
- `T0_V3_AUTHORIZATION_DELTA.md`
- `T0_V3_API_UX_DELTA.md`
- `T0_V3_TEST_GAP_MATRIX.md`
- `T0_V3_MIGRATION_AND_PR_PLAN.md`
- proposition de patch documentaire, sans promotion non autorisée.

Pour chaque affirmation, utiliser :

- `VERIFIED`
- `PROBABLE`
- `HYPOTHESIS`
- `PROPOSAL`
- `TO_TEST`

---

# 16. INTERDICTIONS

Codex ne doit pas :

- réécrire SMART AO ;
- supprimer un historique utile ;
- considérer une note libre comme preuve structurée si une décision critique en dépend ;
- copier une règle juridique en constante globale ;
- inventer un deadline universel ;
- conclure à une assurance couverte ;
- créer un score global “risque” qui écrase les objets ;
- créer une base graphe sans benchmark ;
- créer des microservices sans besoin mesuré ;
- ouvrir la production publique ;
- promouvoir V3 comme autorité sans validation propriétaire ;
- dériver une capacité produit d’un concurrent ;
- copier du contenu propriétaire/licencié non autorisé ;
- considérer les claims marketing concurrents comme preuve de fonctionnement.

---

# 17. VERDICT DE TRANSITION

Le projet ne change pas de métier.

Il précise son métier.

Ancienne lecture dominante :

> analyser un appel d’offres et préparer une réponse fiable.

Nouvelle lecture :

> **maîtriser l’engagement d’une affaire BTP de la première source jusqu’à la clôture, en conservant les liens entre contrat, décision, argent, exécution, preuve et droits.**

C’est cette direction que le code, la documentation, les tests et les benchmarks doivent désormais matérialiser.
