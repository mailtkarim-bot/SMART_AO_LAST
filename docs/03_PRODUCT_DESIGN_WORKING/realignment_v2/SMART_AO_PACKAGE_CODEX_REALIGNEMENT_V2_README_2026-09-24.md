# SMART AO — PACKAGE CODEX RÉALIGNEMENT v2
## Ordre de lecture et mandat d'exécution

**Date :** 24 septembre 2026  
**But :** empêcher toute perte entre métier, Product Freeze, technique et code.

## Ordre obligatoire

1. `docs/00_REFERENCE_ACTIVE/SMART_AO_CAHIER_DIRECTEUR_METIER_MASTER_v2.0.md`
   - connaissance métier exhaustive ;
   - ne pas transformer chaque détail directement en table ; comprendre d'abord la décision métier.

2. `docs/03_PRODUCT_DESIGN_WORKING/realignment_v2/SMART_AO_AUDIT_MASTER_V2_VS_PRODUCT_FREEZE_V1_2026-09-24.md`
   - explique ce que le Product Freeze v1.0 avait couvert, comprimé ou omis ;
   - sert de justification de réouverture.

3. `docs/00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v2.0.md`
   - contrat produit actif après promotion propriétaire ;
   - autorité produit/métier v2.0.

4. `docs/02_FUTURE_TECHNICAL/SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v2.1.md`
   - traduction technique normative active ;
   - décrit domaines, objets, sécurité, déterminisme, migrations, tests et tranches.

5. `docs/03_PRODUCT_DESIGN_WORKING/realignment_v2/SMART_AO_MANDAT_CODEX_REALIGNEMENT_METIER_v2.0.md`
   - instructions opérationnelles immédiates ;
   - audit T0 terminé ; poursuivre par les tranches approuvées et leurs gates.

6. Références du repo :
   - `docs/00_REFERENCE_ACTIVE/00_INDEX_REFERENCE_ACTIVE.md`
   - catalogue UX actif ;
   - fondations UX actives ;
   - architecture v3.1 ;
   - code/migrations/tests actuels.

## Consigne à Codex

> Tu dois traiter les documents 1 à 5 comme une chaîne de traçabilité, pas comme cinq opinions indépendantes. Le MASTER explique le métier ; le Product Freeze décide ce qui devient contrat produit ; le cahier technique décide comment le logiciel doit porter ce contrat ; le mandat définit la méthode de travail. Le code actuel est une preuve de l'existant, pas une raison pour supprimer une exigence.
>
> Commence en READ-ONLY. Produis les matrices d'écart et le plan de migration demandés. Ne crée aucune nouvelle capacité métier tant que le Product Freeze v2.0 n'est pas explicitement promu. Après promotion, implémente par petites tranches verticales testées, sans rewrite global, sans microservices anticipés et sans règle juridique codée en dur sans source/version/applicabilité.

## Gate propriétaire

Le passage de l'audit à l'implémentation est maintenant autorisé par la promotion propriétaire. Chaque tranche garde ses gates :

- vérifier la portée de la tranche et ses validations externes ;
- approuver l’impact UX requis lorsqu’il existe ;
- accepter la séquence de PR proposée par Codex ;
- maintenir le NO-GO public jusqu’aux gates d’exploitation.

## Résultat attendu

La chaîne cible est :

```text
MASTER MÉTIER v2.0
   ↓
PRODUCT FREEZE v2.0 PROMU
   ↓
CAHIER TECHNIQUE v2.1 PROMU
   ↓
AUDIT CODE RÉEL
   ↓
TRACEABILITY + KEEP/ADAPT/REPLACE/DELETE/ABSENT
   ↓
MIGRATIONS + TESTS + PR VERTICALES
   ↓
CODE QUALIFIÉ
```

Aucune étape ne peut être remplacée par « Codex a compris l'intention ».
