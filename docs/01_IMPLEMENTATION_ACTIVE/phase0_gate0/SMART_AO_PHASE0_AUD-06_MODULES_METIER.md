# SMART AO — AUD-06 — Audit des modules métier exigés

**Date :** 12 septembre 2026  
**Référence :** `feat/ccap-cctp-risk-register-20260831@b6b05b8`  
**Statut :** TERMINÉ  
**Verdict :** capacités réelles à conserver ; ownership cible à clarifier sans déplacement massif

## 1. Synthèse

| Module | Capacité réellement observée | Écart principal v3.1 | Trajectoire |
|---|---|---|---|
| Decision | cycle, contexte figé, risques, traitements, liens exigence, GO/NO-GO | portes P0–P7 et invalidation généralisée | KEEP + EXTEND |
| Pricing | scénarios, import preview/commit, snapshots, publication, cost basis | couverture DPGF/BPU/DQE, trésorerie, engagements | KEEP + REPOSITION |
| Enterprise | société, bibliothèque, versions, vérifications, capacités/proofs | taxonomie mémoire, expiration, droits, partenaires | KEEP + EVOLVE |
| Submission | paquet, exports, preuves locales, callback signature | manifeste autoritatif, reçu/rapprochement multi-canaux | KEEP + ALIGN |
| PatronAction | file d'actions et transitions | questions/inconnus/escalades non unifiés | KEEP |
| Knowledge | recherche locale BGE et contrat benchmark | corpus réel absent, lifecycle dérivé incomplet | KEEP + MEASURE |
| Opportunity | profils, BOAMP, scoring, qualification, création Case | TED, déduplication multi-source, preuve fraîcheur | KEEP + ADAPT |
| MarketWatch | lecteur/service BOAMP | doublon de responsabilité avec Opportunity | MOVE + ADAPT |
| Membership | affectations, tâches, bloqueurs, collaboration | mêle accès, travail et lecteurs métier | KEEP + SPLIT LOGICAL |
| Preparation | paquets, readiness, revues, corrections, drafts, transmissions | ownership Response et dépendances multiples | KEEP + ALIGN |
| Optimization | planification de capacité/OR-Tools | pas de frontière publique ni preuve produit | KEEP + MEASURE/DEFER |

## 2. Decision

Le module est le noyau métier le plus proche de la cible. Il contient cycle de décision, transitions, finalisation, contexte figé, registre de risques, traitements et liens entre risques et exigences confirmées. Des contrats publics existent et les autorisations sont appliquées par services.

À ajouter plus tard : modèle générique P0–P7, conditions/dérogations, relation explicite aux Evidence actives, invalidation après nouvelle version, supersession complète et projection Patron. La cible doit enrichir ce noyau, pas le remplacer.

## 3. Pricing

Le module gère scénarios, import en deux temps, lignes, base de coût, snapshots financiers et publication. Il supporte déjà des contrôles de transition et un confinement des informations financières.

Le besoin métier dépasse ce socle : rapprochement DPGF/BPU/DQE, couverture MIRP, facteurs de coût prouvés, hypothèses économiques, trésorerie, engagements du mémoire et validation humaine du prix final. L'ownership des données financières doit rester dans Pricing ; DCE et Submission en lisent des projections bornées.

## 4. Enterprise

Le module couvre identité société, pièces de bibliothèque, uploads, versions, états de vérification, capacités et liens de preuve. C'est un bon socle de Mémoire Entreprise.

Il manque une taxonomie couvrant pouvoirs, assurances, qualifications, personnes, matériel, références, méthodes/QSE, partenaires, produits, achats, finance et REX. Chaque item devra porter titulaire, validité/revue, sensibilité, autorité de validation, droits et réemploi. Cette extension doit partir des Golden DCE et des validations VAL-03/05/10, pas d'un schéma universel spéculatif.

## 5. Submission

Le module sait construire un paquet, lancer des exports, enregistrer des preuves locales et intégrer un retour de signature. Il dépend des états de Case, Decision, Pricing, Preparation, Enterprise et DCE.

Il ne démontre pas encore la chaîne complète : manifeste exigé/présent, candidate figée, P5, paquet hashé, tentative, envoi, réception, acceptation et reçu tiers rapproché. Une `SubmissionEvidence` actuelle ne doit pas être renommée en Evidence métier générique.

## 6. PatronAction

Le module offre une file d'actions dirigeant et des transitions. Il est réutilisé par Decision, Preparation et Submission. Sa responsabilité correspond à une projection de travail/autorité, pas à une source de vérité pour toutes les décisions.

Il doit rester un mécanisme compact. Les futurs inconnus, hypothèses, questions et dérogations appartiendront à leurs contextes propriétaires, avec PatronAction comme lecteur/projection si une action dirigeant est requise.

## 7. Knowledge

Le module implémente une recherche locale, des embeddings BGE et un contrat de benchmark. Les tests ciblés passent, mais le corpus de benchmark contient zéro document réel. Les embeddings utilisent du texte copié et des vecteurs JSONB.

Avant toute nouvelle pile retrieval : mesurer exact/structurel puis baseline vectorielle sur A1 ; enregistrer version de modèle, jeu, métriques et régressions ; assurer purge et invalidation. Hybride, RRF, reranker et GraphRAG restent différés jusqu'à gain prouvé.

## 8. Opportunity et MarketWatch

Opportunity possède profils de veille, ingestion BOAMP, scoring, qualification et conversion en Affaire. MarketWatch expose un service/adaptateur BOAMP plus petit. Cette double responsabilité crée une frontière instable.

La trajectoire minimale consiste à faire d'Opportunity le propriétaire des opportunités et de MarketWatch un provider/adapter derrière un port de source, puis à absorber progressivement son usage. Aucun fichier ne doit être supprimé avant parité et tests. TED sera un second adapter, après Gate A.

## 9. Membership

Le module porte affectations, tâches, bloqueurs, travail et capacités, tandis que la sécurité Platform porte déjà identités, rôles, sessions et MFA. Membership lit directement Case, DCE, Enterprise et Pricing.

La cible exige deux responsabilités : `Identity & Access` pour habilitations et délégations ; `Collaboration & Work` pour affectations, tâches, remplacements et blocages. Le split doit d'abord être logique dans les contrats/owners ; un déplacement physique immédiat produirait trop de changements.

## 10. Preparation

Preparation couvre paquets de préparation, readiness, documents, revues, corrections, brouillons, snapshots et transmissions. Il représente une grande partie de `Response & Artifacts` et dépend de plusieurs lecteurs transversaux.

Les documents réponse doivent avoir Preparation/Response comme propriétaire d'écriture. Submission ne doit recevoir qu'une candidate validée et immuable. Les actions Patron et les tâches Membership restent des projections/commandes vers leurs propriétaires respectifs.

## 11. Optimization

Le module fournit une planification de capacité fondée sur OR-Tools et des runs persistés. Il n'a pas de couche publique et l'audit n'a pas trouvé de preuve produit bout-en-bout ni de corpus de décisions réelles.

Il est conservé, mais son extension est différée. Le besoin REC-15 doit d'abord être satisfait par une visibilité simple des conflits datés et un arbitrage humain ; l'optimiseur n'est utile que s'il améliore une métrique face à cette baseline.

## 12. Risques transversaux

1. Des contrats financiers et d'affectation sont exposés depuis `dce/public/contracts.py`, ce qui brouille le propriétaire.
2. Submission concentre de nombreuses lectures ; ses dépendances doivent devenir des snapshots explicites.
3. Membership traverse trop de modules et doit cesser d'être un agrégateur métier général.
4. MarketWatch et Opportunity se chevauchent sur BOAMP.
5. Optimization et Knowledge peuvent pousser à l'abstraction avant preuve ; leur gate est métrique.

## 13. Ordre recommandé

1. A0/A1 rendent les tests et cas réels mesurables.
2. A2–A4 ajoutent le noyau probatoire.
3. Gate A choisit un premier incrément vertical Patron.
4. Les frontières sont resserrées seulement dans les modules réellement touchés par cet incrément.
5. Toute suppression attend la parité fonctionnelle et la migration des lecteurs.

## 14. Preuves

- `backend/app/modules/decision/`
- `backend/app/modules/pricing/`
- `backend/app/modules/enterprise/`
- `backend/app/modules/submission/`
- `backend/app/modules/patron_action/`
- `backend/app/modules/knowledge/`
- `backend/app/modules/opportunity/`
- `backend/app/modules/market_watch/`
- `backend/app/modules/membership/`
- `backend/app/modules/preparation/`
- `backend/app/modules/optimization/`
- [MAP-01](./SMART_AO_PHASE0_MAP-01_CONTEXT_MAP.md)
