# SMART AO — Revue de méthode et priorités — 14 octobre 2026

## Décision de pilotage locale

Revue demandée par l’Owner après l’alerte JOOC. Réorienter les essais vers des résultats métier complets et mesurables. La tranche bordures/raccord CEE est différée, non achevée. Le plan global reste l’autorité unique du statut et de la prochaine étape; ce document motive la réorientation sans modifier les cahiers v3.1.

## AS-IS vérifié

- Checkout principal `/home/noor/PROJECTS/BTP/SMART_AO_V8`, branche `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`. WIP préexistant : 73 entrées Git; aucun nettoyage, commit ou push dans cette revue.
- [PF31-02 à PF31-04](../01_Cahiers_des_charges/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v3.1.md) demandent une différenciation à démontrer et des parcours React/API/PostgreSQL complets. L’hypothèse centrale est la continuité vérifiable de l’engagement; fréquence du besoin et disposition à payer restent à valider.
- [M2-026/027/029](../01_Cahiers_des_charges/SMART_AO_CAHIER_DIRECTEUR_METIER_MASTER_v3.1.md) exigent douze axes métier, conséquences/actions et complétude documentaire explicite. Un inventaire, une extraction ou un signal lexical ne prouvent pas l’analyse complète.
- [Complétude des quatre DCE](../05_Qualification_locale/DCE_COMPLETUDE_ET_OMISSIONS_CRITIQUES_2026-10-12.md) : 1 000 entrées inventoriées; confrontation initiale de 50 points, puis 18 signaux supportés, zéro omission ciblée restante, 19 points sans règle et 13 initialement non éligibles. Ces dénominateurs sont locaux, pas un rappel global. Les qualifications ultérieures des sources doivent être reprises individuellement, sans figer ces exclusions comme état courant.
- Le journal comporte onze tranches récentes explicitant un produit inchangé. Les 39 empreintes applicatives/tests/configuration du checkpoint privé ont été revérifiées identiques. La suite backend 2 544/2 544 avec couverture 88,24 % précède ces travaux; aucune nouvelle suite globale exécutée dans cette revue documentaire.
- [Dernière preuve CEE](../05_Qualification_locale/DCE_SORTIES_NATIVES_ASYNCHRONE_CEE_2026-10-14.md) : labels locaux corroborés, 3/7 supports textuels, aucune route native qualifiée. IE2/T92, douze occurrences altérées et 28 omissions de chemins restent UNKNOWN/REVIEW_REQUIRED. Preuves privées utiles, sans démonstration d’un parcours DCE complet ni intégration générale.
- Surfaces existantes examinées : `backend/app/modules/dce/application/analysis.py` (règles RC), `backend/app/modules/dce/infrastructure/advanced_extraction.py`, `scripts/qualify_dce_completeness.py`, `web/src/features/dce/useDceKnowledge.ts` et `DceKnowledgePanel.tsx`. Le CLI distingue couverture documentaire et sémantique; le panneau expose une lecture/version et des états. Le raccord complet entre campagne privée, API, persistance et résultat utilisateur reste à auditer; la simple présence des fichiers ne le prouve pas.
- [Dépendances qualifiées](../05_Qualification_locale/DCE_ESSAIS_METIER_DEPENDANCES_2026-10-11.md) : capacités Docling/OCR/OR-Tools bornées. OR-Tools n’analyse pas le texte; un essai Docling synthétique ne prouve ni tous les PDF ni son appel automatique dans le pipeline courant.

## Risques et correction de méthode

Le découpage répété en sous-problèmes d’une seule page a remplacé le critère de sortie métier. Une preuve de refus correcte augmente la sécurité, mais n’est pas une livraison utilisateur. Je prends en charge cette dérive de pilotage : le prochain défaut rencontré ne devient plus automatiquement la prochaine tranche.

L’erreur historique de padding RGB supposé blanc montre aussi qu’il faut qualifier le banc d’essai avant une campagne : reconstruction indépendante, couleur réelle, conservation des pixels, provenance et contre-exemples. Deux moteurs concordants peuvent partager une même erreur d’entrée.

La réponse à une concurrence visible n’est pas une nouvelle architecture. [JOOC](https://www.jooc.ai/) présente une promesse de synthèse DCE rapide et de réponses personnalisées. Ce sont des affirmations publiques : application non testée, aucune comparaison sur les mêmes dossiers. Ni le volume de notre cahier ni le nombre de tests ne démontrent une supériorité commerciale.

## Points d’insertion

Réutiliser les contrats DCE, extraction, analyse, lecture Affaire et preuves existants. Avant toute modification produit, tracer leurs appels, tests et états sur un dossier complet; séparer résultat en production locale, prototype privé, attendu métier et capacité non démontrée. Aucun framework, modèle ou moteur supplémentaire décidé par cette revue.

## Plan minimal et critères de sortie

| Ordre | Travail | Preuve de sortie |
|---|---|---|
| 1 | Baseline DCE-01 sur le parcours existant | Identité dossier/lot/version/hash, inventaire complet et limites; étapes réellement exécutées et résultats consultables; matrice des douze axes et journal des lacunes avec source exacte; temps/coût/ressources mesurés ou NON MESURÉ explicite |
| 2 | Prioriser les lacunes critiques et corriger le mécanisme commun | Source et conséquence métier de chaque omission; test de régression rouge puis vert; raccord au parcours existant et régression sur les autres DCE applicables, aucun correctif au seul texte attendu |
| 3 | Rejouer les quatre dossiers avec un protocole stable | Omissions, faux positifs, sources, portée lot/version, pièces/pages non lues et états inconnus comparables; résultat utile par axe, sans fabriquer un taux global à partir de seuls points ciblés |
| 4 | Qualifier la tranche utilisateur avant engagement PF31-04 A | Le Patron peut consulter constat sourcé, portée, conséquences connues/inconnues et action/condition humaine. Parcours testé avec session/API synthétiques; toute évolution UI suit OpenDesign Local Codex et Impeccable |

Le premier livrable est un diagnostic reproductible du parcours réellement disponible, pas une fiche déclarée complète à partir des attentes. Séparer les faits de référence des entrées de l’extracteur pour éviter une validation circulaire. Pour chaque axe : résultat étayé, NON APPLICABLE avec justification humaine prévue, ou UNKNOWN avec cause et action. Les hypothèses financières restent des hypothèses et FINANCIAL_PRIVATE.

### Règle de sortie des cas difficiles

- Une lacune critique doit rester visible avec source/page/région/hash, conditions et chemins affectés, preuve manquante et action attendue. Elle interdit toute déclaration de complétude et toute conclusion qui en dépend.
- Après deux protocoles techniques distincts et bornés sans preuve suffisante, consigner l’exception et poursuivre les autres résultats démontrables. Reprise approfondie seulement pour un faux positif dangereux, une lacune récurrente sur plusieurs dossiers, ou un besoin central identifié par la matrice métier. Ce budget organise l’effort; il ne lève jamais UNKNOWN.
- La sortie correspondant CEE et le refus du raccord asynchrone restent conservés. Aucun transfert des preuves natives vers les rasters altérés. Les 28 omissions ne disparaissent pas parce que la tranche change.
- Chaque tranche indique résultat utilisateur attendu, dénominateurs, seuil de refus, preuve de sortie et risque résiduel avant d’être lancée. Un seul prochain travail actif. Une synthèse par résultat cohérent, preuves détaillées en annexes, journal append-only préservé.

## Tests et contrôles à prévoir lors des changements produit

TDD et tests du contexte concerné; extraction partielle/inaccessible, négation, portée lot/version, rectificatif, source obsolète, refus des conclusions non prouvées et absence de fuite tenant. Pour toute action métier : permissions, MFA, intention exacte, UNKNOWN, retry/idempotence et concurrence selon le contrat existant. Contrôles globaux avant livraison cohérente ou changement transversal, contrôles ciblés pendant l’itération; aucun seuil de sécurité abaissé. Tests puis scan Semgrep adapté aux fichiers modifiés.

Cette revue ne modifie que pilotage/index. Vérification documentaire : unicité de la tranche active, liens locaux du nouveau dossier, concordance de la prochaine étape avec le miroir et diff sans whitespace. Aucun test produit, navigateur ou scan de code nouveau ne peut être déduit de cette revue.

## Limites maintenues

A1 non admis, A2 générique HOLD et NO-GO public. Pas de validation humaine inventée ni d’admission Golden automatique. Travail local sur corpus d’essai déjà disponible, sans backend live, VPS, déploiement, push, effet P3, dépôt externe, contact concurrent ni téléversement de DCE. La qualité sur tous les DCE, l’usage réel et la disposition à payer restent non démontrés.

## Réorientation ultérieure — revue globale du même jour

À la demande Owner de revoir le logiciel entier, la [revue globale](REVUE_GLOBALE_METIER_CODE_CONCEPTION_2026-10-14.md) et le plan actif remplacent l’ordre de priorité proposé plus haut : R0 contexte de recherche, R1 fraîcheur des sources et R2 composition des extras avant comparaison des moteurs. Les constats et preuves de ce document restent datés, sans nouvelle qualification implicite.
