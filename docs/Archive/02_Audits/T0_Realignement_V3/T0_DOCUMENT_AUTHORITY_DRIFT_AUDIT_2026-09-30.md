# T0 — Audit de dérive des autorités documentaires

**Date :** 30 septembre 2026  
**Verdict :** V3 est un candidat local non promu. L’autorité produit reste le Product Freeze v2.0 tant qu’une décision propriétaire explicite n’a pas basculé l’index.

| Document / surface | Autorité actuelle ou statut | Écart observé | Action recommandée |
|---|---|---|---|
| `docs/Actifs/00_INDEX_DOCUMENTATION_ACTIVE.md` | Index en vigueur, daté du 24/09 ; il désigne Product Freeze v2.0, catalogue v0.3, fondations UX v0.3, architecture v3.1 et Cahier technique v2.1. | Il ne référence pas V3, ce qui est cohérent avec son statut candidat. | `KEEP` jusqu’à une décision propriétaire ; ne pas mettre V3 dans les références actives sans promotion. |
| Product Freeze v2.0 | Contrat produit actuellement promu ; client initial PME BTP françaises de 10–100, commande publique prioritaire, privé borné au corpus. | Le pivot V3 modifie le positionnement et le centre de gravité. | `KEEP` en autorité ; établir un delta et les arbitrages avant remplacement. |
| Catalogue UX v0.3 + fondations UX v0.3 | Références de couverture et d’interaction actuellement actives. Le catalogue porte 104 identifiants/surfaces et PUX-01–19. | V3 propose d’en faire une couverture, pas un ordre de construction. Cette distinction doit être explicite dans la future version. | `KEEP` ; prioriser les parcours sans supprimer les contrats de couverture. |
| Cahier directeur métier MASTER v2.0 et Cahier technique v2.1 | Références dérivées selon l’index v2.0. | V3 ajoute temporalité et causalité, mais ne doit pas réécrire silencieusement les règles, portes et invariants déjà approuvés. | `KEEP` jusqu’au diff de promotion ; résoudre chaque règle via `KEEP / CHANGE / DEFER / OWNER_REOPEN_REQUIRED`. |
| Architecture logicielle v3.1 | Référence directrice limitée à sa portée de construction/gates, pas une autorité métier. | Elle impose modular monolith/no rewrite ; V3 est compatible et indique elle-même un bounded context logique. | `KEEP` ; ne pas faire évoluer l’architecture avant le code map et les gates correspondantes. |
| Plan global v0.1 | Présent localement comme modification non committée ; le HEAD contient l’étape PUX-19, tandis que le working tree a avancé vers C08/PUX-07 et le rapprochement ligne partenaire. | Décalage entre le plan publié dans Git et le plan local, plus la nouvelle suspension T0. | `UPDATE` le plan local pour faire de T0 la tranche d’orientation; conserver PUX-07 comme WIP en attente et ne pas effacer ses changements. |
| Paquet V3 — directive, cahiers candidat et README | Fichiers présents dans `docs/Archive/`, tous non suivis dans le checkout au moment de l’audit ; absents des références actives. | Statut candidat explicitement correct ; le README cite deux noms courts absents du dossier (les fichiers présents sont OWNER_FREEZE/MASTER_CANDIDATE), et numérote deux rubriques « 4 ». | `PROPOSE` : corriger les chemins et l’ordre de lecture avant promotion, sans changer l’index actif. |
| Product Freeze OWNER FREEZE v3.0 candidate | Candidat de réouverture propriétaire ; annonce elle-même qu’il ne remplace pas l’autorité active avant promotion. | Pivot stratégique pertinent ; le scope `MUST` A/B/C + typed provenance + benchmark peut recréer une portée trop large si les verticales ne sont pas séquencées. | `PROPOSE` : valider le pivot, mais phaser A → B → C et conserver une liste explicite de décisions owner. |
| Cahier technique MASTER candidate v3.0 | Candidat audit-first, conserve le delta V3 et le texte V2.1. | Plusieurs headings réapparaissent dans la partie héritée ; le pied de page final dit encore « Cahier technique v2.1 — 24 septembre ». | `UPDATE` avant promotion : normaliser la partie héritée, ancres et pied de page; préciser V2.1 comme référence archivée intégrée, non comme verdict V3. |
| Cahier métier MASTER candidate v3.0 | Candidat qui réunit nouvelle partie V3 et profondeur V2.0. | La partie métier V2 est reprise avec numéros/titres de sections déjà présents; les ancres Markdown dupliquées compliquent citations et traçabilité. | `UPDATE` avant promotion : séparer le delta normatif V3, les annexes/source métier et une table de correspondance; une seule section numérotée par autorité. |

## Règle de promotion proposée

1. Le propriétaire décide `ACCEPTER / AMENDER / REFUSER / DIFFÉRER` la stratégie V3 et choisit les invariants/limites de V1.
2. Après acceptation, publier un diff d’autorité V2→V3 : règles conservées, modifiées, différées, retirées et nouvelles.
3. Promouvoir un Product Freeze V3 unique dans `00_REFERENCE_ACTIVE`, puis dériver le cahier technique et la matrice de traçabilité.
4. Mettre à jour l’index, la roadmap et l’archive dans le même lot documentaire, sans retirer l’historique.
5. Aucun code ou nouveau statut juridique ne prend autorité depuis les documents candidats seuls.

Le point faible actuel n’est pas le manque d’un nouveau cahier : c’est le risque de donner simultanément une autorité à V2 actif, V3 candidat, aux masters et à une roadmap locale non committée. Le nouveau cahier doit réduire cette ambiguïté, pas ajouter un cinquième document faisant foi.
