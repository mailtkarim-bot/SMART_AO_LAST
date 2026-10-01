# SMART AO — G01–G09 OWNER EXPERIENCE FREEZE v0.1

**Statut :** OWNER EXPERIENCE FREEZE — VALIDÉ PAR LE PROPRIÉTAIRE  
**Date :** 20 septembre 2026  
**Autorité :** validation explicite « Je valide G01–G09 »  
**Références :** cahier OWNER produit/métier v0.4, catalogue UX OWNER v0.3

## Périmètre gelé

Le gel porte sur les scénarios G01–G09, leurs rôles, leurs états difficiles, leurs refus et leurs preuves :

```text
source publique ou DCE
  → lecture/extraction sourcée
  → qualification et inconnues visibles
  → revue humaine ou décision Patron explicite
  → acte append-only conservé
```

Les neuf scénarios sont reliés à des actes métier réels dans `g01_g09_business.json`. Le gel ne crée aucune autorisation implicite et ne remplace pas le Product Freeze v1.0.

## Décisions d’expérience gelées

| Scénario | Expérience gelée | Refus et limite |
|---|---|---|
| G01 | Le gate P3/P5 montre la dépendance non démontrée et la prochaine preuve attendue. | `DEPENDENCY_UNPROVEN` n’est ni un rejet définitif ni un feu vert. |
| G02 | Un rectificatif rend visible la revalidation du paquet et de P5. | Une ancienne autorisation ne couvre jamais une nouvelle version. |
| G03 | Les sources contradictoires restent côte à côte ; la résolution humaine porte une raison. | Aucune priorité automatique ; aucune source supprimée. |
| G04 | Le gap de capacité/coût est présenté comme blocage à revoir par le Patron. | Aucun montant ni hypothèse n’est inventé. |
| G05 | L’édition dérivée est versionnée, sourcée et présentée comme brouillon. | Brouillon ≠ réponse validée ≠ dépôt. |
| G06 | Une échéance illisible reste `UNKNOWN` avec action de confirmation. | Aucune date n’est déduite. |
| G07 | Le fichier protégé est signalé sans contournement. | Aucun déchiffrement ni contenu fabriqué. |
| G08 | L’inventaire d’archive reste partiel mais reprend les éléments non traités. | Partiel ≠ complet. |
| G09 | Le contenu hostile est isolé et soumis à revue humaine. | Aucune exécution ni transmission IA. |

## Rôles et confidentialité

- Le Patron garde les décisions P3/P5, les revues économiques et les surfaces financières.
- Le Collaborateur voit uniquement les objets assignés et les projections non financières autorisées.
- Les inconnus, contradictions, risques, gaps et refus ne donnent aucun pouvoir de validation.
- Les scores BOAMP restent des signaux publics explicables ; ils ne déduisent ni marge, ni capacité financière, ni probabilité de succès.

## Critères d’acceptation gelés

1. Une source, une version et un état sont visibles avant toute conclusion.
2. Toute contradiction ou inconnue propose une revue, jamais une conclusion silencieuse.
3. Chaque acte métier est rejouable ou explicitement non conclusif.
4. Les données financières et le pouvoir Patron ne traversent pas les contrats Collaborateur.
5. Les états `UNKNOWN`, `REVIEW_REQUIRED`, `PARTIAL` et `DEPENDENCY_UNPROVEN` restent lisibles dans l’interface.
6. Le clavier, le lecteur d’écran, le focus, les erreurs et le responsive suivent le gel d’accessibilité existant.

## Preuves et limites

- liaison métier : `SMART_AO_PHASE9_G01_G09_ACTES_METIER_PREUVE_v0.1.md` ;
- confidentialité et déductions : `SMART_AO_PHASE9_G01_G09_CONFIDENTIALITE_DEDUCTIONS_AUDIT_PREUVE_v0.1.md` ;
- accessibilité : `SMART_AO_PHASE9_ACCESSIBILITE_G01_G09_AUDIT_PREUVE_v0.1.md` ;
- validation propriétaire : `SMART_AO_PHASE9_G01_G09_OWNER_REVIEW_PACKET_v0.1.md` ;
- tests : 10 fixtures PostgreSQL, 29 frontières API PostgreSQL, 31 contrôles architecture/sécurité et 187 tests web.

Les parcours PUX non couverts par une preuve complète restent `PARTIAL` dans le catalogue et devront être fermés dans une tranche dédiée. Ce gel ne les transforme pas en fonctionnalités acceptées.

## Effet du gel

G01–G09 ne peuvent plus changer de rôle, d’état, de refus, de confidentialité ou de sémantique sans nouvelle version et nouvel arbitrage propriétaire. Le futur Product Freeze v1.0 pourra remplacer ce gel, mais ne peut pas le contredire silencieusement.
