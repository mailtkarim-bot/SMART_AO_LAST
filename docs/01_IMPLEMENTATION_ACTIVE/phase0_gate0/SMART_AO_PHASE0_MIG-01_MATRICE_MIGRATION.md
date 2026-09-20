# SMART AO — MIG-01 — Matrice de migration depuis V8

**Date :** 12 septembre 2026  
**Référence :** `feat/ccap-cctp-risk-register-20260831@b6b05b8`  
**Statut :** TERMINÉ  
**Verdict :** migration progressive et additive ; aucune suppression autorisée par l'audit

## 1. Sémantique des décisions

| Décision | Sens |
|---|---|
| `KEEP` | objet/module utile et sémantiquement compatible |
| `ADAPT` | enrichissement compatible, contrat ou données à faire évoluer |
| `MOVE` | responsabilité à déplacer derrière une frontière, sans big bang |
| `CREATE` | objet cible absent et justifié par les exigences |
| `DEFER` | capacité cible différée jusqu'à cas ou métrique |
| `DELETE` | suppression seulement après absence d'usage ou parité prouvée |

**Résultat de Phase 0 : aucune ligne `DELETE`.** L'audit n'a ni preuve d'absence d'usage ni parité suffisante pour supprimer une capacité.

## 2. Modules

| Élément V8 | Décision | Preuve code | Cible | Migration minimale | Gate |
|---|---|---|---|---|---|
| Platform | KEEP + ADAPT | `backend/app/platform/` | Platform | compléter jobs, data lifecycle, ops | A0/pilote |
| bootstrap/runtime | ADAPT | `bootstrap/application.py` central | Platform | documenter puis découpler au fil des cas | A0 puis incréments |
| Case | KEEP + ADAPT | quatre couches, contrats publics | Case / Affair | ajouter lot/porte/version active sans reprendre l'agrégat | post-A |
| DCE | KEEP + ADAPT | 41 fichiers, versions/extractions/exigences | DCE + Evidence | extraire les owners probatoires par contrats | A2–A4 |
| Decision | KEEP + EXTEND | cycle/risques/contexte/finalisation | Decision & Governance | portes, conditions, Evidence, invalidation | post-A |
| Pricing | KEEP + REPOSITION | scénarios/import/snapshots | Pricing Intelligence | owner coût/prix, liens MIRP/Evidence | post-A |
| Enterprise | KEEP + EVOLVE | société/documents/capacités | Enterprise Memory | taxonomie fondée sur cas et lifecycle | post-A |
| Submission | KEEP + ALIGN | package/export/evidence/signature | Submission | manifeste/reçu/états externes | post-A |
| PatronAction | KEEP | action queue/transitions | Collaboration projection | rester projection, ne pas absorber tous les objets | post-A |
| Knowledge | KEEP + MEASURE | BGE/embeddings/benchmark | AI/Knowledge baseline | qualifier avant nouvelle stack | A1/Gate A |
| Opportunity | KEEP + ADAPT | veille/BOAMP/qualification | Opportunity / Radar | owner avis/opportunité | post-A |
| MarketWatch | MOVE + ADAPT | service BOAMP minimal | adapter d'Opportunity | port source puis migration lecteurs | post-A |
| Membership | KEEP + SPLIT LOGICAL | affectations/tâches + lectures cross-module | Identity / Collaboration | séparer contrats/owners avant fichiers | post-A |
| Preparation | KEEP + ALIGN | paquets/revues/drafts/transmissions | Response & Artifacts | owner document réponse/candidate | post-A |
| Optimization | KEEP + MEASURE + DEFER | OR-Tools, pas de public API | capacité interne | comparer à baseline simple | après besoin REC-15 |

## 3. Objets probatoires et DCE

| Objet | Décision | Preuve actuelle | Changement | Compatibilité/rollback | PR |
|---|---|---|---|---|---|
| Consultation | KEEP | agrégat DCE | aucun changement A | tables existantes | — |
| staged object | KEEP | modèles staging/upload | qualifier ops | aucun changement de contrat | A0 |
| `DceVersion` | KEEP + ADAPT | domaine + persistance | référence active/provenance renforcée | colonnes additives | A2/A4 |
| document original | KEEP | version/doc records + storage | attacher anchors | aucune mutation de l'original | A2 |
| extraction | KEEP | runs versionnés | exposer parser/version aux anchors | ancien lecteur conservé | A2 |
| fragment/locator | KEEP | texte/hash/locator JSON | source de backfill | pas de réécriture | A2 |
| classification evidence locale | KEEP DISTINCT | table dédiée | conserver nom et sens | aucun renommage | — |
| observation RC | KEEP + ADAPT | analyse RC | devenir entrée d'Evidence si déterministe | double lecture temporaire | A3 |
| `DceRequirementSource` | KEEP + ADAPT | offsets fragment | relier à anchor/evidence | table historique conservée | A2–A4 |
| `DceRequirement` | KEEP + ADAPT | table/runs/confirmation pending | portée, criticité, Evidence, invalidation | champs optionnels puis obligatoires après backfill | A4 |
| confirmation historique | KEEP | chaîne immuable | relation à contexte/proof si nécessaire | aucun update historique | A4 |
| current confirmation | KEEP | projection courante | reconstruisible | rebuild rollback | A4 |
| impact rectificatif | KEEP + EXTEND | registre conservateur | dépendances Evidence | mode conservateur si graphe incomplet | A4/post-A |
| `SourceAnchor` | CREATE | aucun objet générique | locator typé multiformat | table additive, feature/read switch réversible | A2 |
| `Evidence` générique | CREATE | sens locaux seulement | preuve réutilisable distincte | namespace/table distincte | A3 |
| Requirement→Evidence | CREATE/ADAPT | RequirementSource indirect | liaison explicite | ajout sans supprimer ancienne source | A4 |
| InformationRequirement/MIRP | CREATE + DEFER | concepts dispersés | objet après Golden métier | aucun schéma en A | post-A |
| Unknown | CREATE + DEFER | états d'échec/signaux | objet métier seulement sur cas | aucun schéma en A | post-A |
| Hypothesis | ADAPT/CREATE + DEFER | champs Pricing/Decision | owner probatoire explicite | migration par use-case | post-A |
| Contradiction | ADAPT + DEFER | analyses ciblées | objet sourcé et résolu | conserver sorties actuelles | post-A |
| RiskSignal/CostFactor | ADAPT | DCE risk + Pricing cost | séparer signal/preuve/décision | adapters temporaires | post-A |

## 4. Autres objets métier

| Objet | Décision | Owner cible | Preuve V8 | Suite |
|---|---|---|---|---|
| décision/contexte figé | KEEP + EXTEND | Decision | modèles et contrats présents | P0–P7, supersession |
| risque/traitement | KEEP + EXTEND | Decision | registre et transitions | relier Evidence/invalidation |
| scénario prix | KEEP | Pricing | présent | couverture besoin |
| import prix | KEEP + ADAPT | Pricing | preview/commit | formats Golden |
| snapshot/publication | KEEP | Pricing | présent | conserver confidentialité |
| élément Entreprise | KEEP + EVOLVE | Enterprise | présent partiellement | validité/droits/réemploi |
| capacité/preuve tierce | KEEP + ADAPT | Enterprise | capacités/proof links | partenaire/engagement |
| document réponse | KEEP + ALIGN | Response | Preparation | provenance, validation, engagement |
| candidate offre | ADAPT | Response | Preparation/Submission | figer avant dépôt |
| manifeste | ADAPT | Submission | paquet partiel | exigé/présent/version/hash/canal |
| SubmissionEvidence locale | KEEP DISTINCT | Submission | table et service | rapprocher au reçu, ne pas fusionner |
| reçu tiers | ADAPT/CREATE | Submission | preuve partielle | états envoi/réception/acceptation |
| tâche/affectation | KEEP + MOVE LOGICAL | Collaboration | Membership | contrats ciblés |
| action patron | KEEP | Collaboration projection | PatronAction | source dans contexte demandeur |
| contrat vendu/passation/REX | CREATE + DEFER | Handover | fragments dispersés | incrément après A |
| appel IA/prompt/tool | CREATE + DEFER | AI Runtime | absent | après noyau probatoire |
| Control Plane | DEFER | Platform control | absent | avant plusieurs instances |

## 5. Ordre et dépendances

```text
A0 reproductibilité
  └── A1 Golden Development
        └── A2 SourceAnchor
              └── A3 Evidence
                    └── A4 Requirement + validation/invalidation
                          └── Gate A
                                └── incréments verticaux B–I réordonnés
```

A2 dépend d'un corpus et de locators mesurables. A3 dépend d'anchors stables. A4 dépend d'une Evidence distincte et d'un plan de compatibilité. Inverser cet ordre contraindrait le système à inventer des références ou à réécrire deux fois les modèles.

## 6. Stratégie expand/contract

1. **Expand** : ajouter tables/colonnes/index nullable et contrats versionnés.
2. **Backfill** : reprendre seulement les données dont la provenance est démontrée ; produire un rapport des inconnues.
3. **Dual read** : garder le chemin historique et comparer les projections sur Golden.
4. **Switch** : activer le nouveau lecteur après Gate de parité.
5. **Contract** : aucune suppression dans A2–A4 ; une PR ultérieure séparée exigera preuve d'absence d'usage.

Le rollback applicatif doit pouvoir ignorer les nouvelles tables. Une migration de rollback ne doit pas supprimer des données nouvellement collectées ; elle désactive le chemin et conserve le schéma jusqu'à décision.

## 7. Conditions interdisant le déplacement

- corpus Golden vide ;
- test backend suspendu ou baseline globale rouge ;
- colonne cible non backfillée avec rapport d'écarts ;
- consommateur direct non recensé ;
- Evidence locale confondue avec la preuve générique ;
- perte de l'acteur, de la version ou de l'historique ;
- absence de rollback du lecteur.

## 8. Réponse Gate 0

**Question 4 — A0–A4 sont-elles additives, réversibles et compatibles ? `OUI COMME PLAN`, `NON DÉMONTRÉ EN EXÉCUTION`.** Le plan interdit la contraction dans A2–A4 et conserve les lecteurs actuels. La preuve sur PostgreSQL peuplé appartient à A0 puis aux tests de migration de chaque PR.

## 9. Preuves

- [AUD-03](./SMART_AO_PHASE0_AUD-03_DB_MIGRATIONS.md)
- [AUD-05](./SMART_AO_PHASE0_AUD-05_FLUX_DCE.md)
- [MAP-01](./SMART_AO_PHASE0_MAP-01_CONTEXT_MAP.md)
- [PLAN-A](./SMART_AO_PHASE0_PLAN-A_PR-A0_A4.md)

