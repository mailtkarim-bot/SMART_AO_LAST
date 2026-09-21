# SMART AO — Paquet de revue propriétaire du corpus DCE redacted v0.1

**Date :** 21 septembre 2026  
**Statut :** EN ATTENTE DE VALIDATION PROPRIÉTAIRE  
**Source :** `DCE Type/CENTRALE GROUPE ELEC`  
**Copie de travail :** `/tmp/smartao-dce-corpus-work/redacted`

## Objet de la validation

Valider que la copie `redacted` peut servir à une qualification RAG locale non financière, sans index permanent avant cette validation.

## Périmètre

- 10 PDF : RC, CCAP, CCTC, six CCTP et planning ;
- 30 320 lignes extraites de la source ;
- 687 lignes redacted par remplacement ou suppression déterministe ;
- motifs email, téléphone, code postal et adresse absents de la copie redacted ;
- BGE one-shot vérifié sur 10 fragments : vecteurs de dimension 1 024, sans écriture DB ;
- originaux inchangés et hors Git.

## Exclusions

BPU, DPGF, données financières, montants, facturation, actes d’engagement, DC1/DC2, rapports amiante, RICT, G2PRO, pièces graphiques et fichiers non classés restent hors périmètre.

## Limites connues

La redaction automatique ne prouve pas l’absence de toute identité implicite. Les noms d’établissement et de site sont remplacés, mais une revue humaine doit confirmer les organisations, lieux, dates sensibles, références de marché et droits de réutilisation. La qualification RAG prévue ne doit indexer que des fragments `PUBLIC` ou `INTERNAL_OPERATIONAL` après ce contrôle.

## Qualification prévue après validation

1. Relire le manifeste et les 10 hashes ;
2. confirmer la classification non financière ;
3. construire un index temporaire BGE en mémoire ou dans une base jetable ;
4. exécuter des requêtes techniques attendues avec ancres ;
5. vérifier l’absence de fragments exclus ;
6. supprimer l’index et les artefacts temporaires ;
7. publier uniquement les métriques et les limites.

## Décision propriétaire

- [ ] **APPROUVÉ** pour qualification RAG locale non financière ;
- [ ] **REFUSÉ** ou corrections demandées.

Aucune indexation permanente ni activation préproduction ne doit être faite avant cette décision.

