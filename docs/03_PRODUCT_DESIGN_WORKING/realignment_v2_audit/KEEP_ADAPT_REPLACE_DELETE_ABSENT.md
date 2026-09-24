# SMART AO — Décision sur l'existant pour le candidat v2

**24 septembre 2026 · propositions de T0, aucune suppression décidée**

| Composant actuel | Décision | Motif et garde |
|---|---|---|
| Affaire, DCE, versions, fragments, exigence, conflits | KEEP + ADAPT | Conserver les preuves. Étendre les liens d'impact aux nouveaux faits uniquement après tests de rectificatif ciblé. |
| Dispatcher, reçus d'idempotence, outbox, `AuthorizationPolicy` | KEEP | Réutiliser les contrôles transactionnels et les refus neutres. Aucune seconde infrastructure de commandes. |
| `DecisionRiskRecord` et signaux CCAP/CCTP | KEEP + ADAPT | Garder les risques existants ; ajouter des contrats distincts pour sanction, dérogation et événement de droit. Ne pas renommer `risk` en sanction. |
| Scénarios de prix, rapports, capacités d'entreprise | KEEP + ADAPT | Sources utiles pour la carte et le cash ; ne pas les présenter comme financement, couverture d'assurance ou réservation. |
| Brouillon, paquet, manifeste, P5 et preuves de remise | KEEP + ADAPT | Conserver les séparations d'actes. Relier les engagements mesurables au paquet/version. |
| Résultat par lot, P6, P7 et REX | KEEP + ADAPT | P7 actuel conserve une preuve d'acte ; il faudra un paquet/acceptation de passation, sans modifier l'ancien résultat. |
| C05/C07/C08/C10/C13 et shell React | KEEP + ADAPT | Ajouter les états/sources requis sans inventer des droits côté navigateur. |
| C09/C12 | ABSENT comme parcours complets | `canonicalSpaces.ts` les marque `BACKLOG`; concevoir leur minimum après révision UX. |
| Profil/règle réglementaire, baseline, sanction calculable, droit, OS, DGD, paiement, engagement KPI | ABSENT comme contrats dédiés | Aucun équivalent démontré dans modèles/services/migrations inspectés. Concevoir par tranches, avec expertise externe si nécessaire. |
| Suppression/rewrite de modules historiques | DELETE : AUCUN | Aucun composant actuel n'est prouvé dangereux ou remplaçable globalement par ce seul audit. |

`REPLACE` reste **non décidé** : une migration destructive exigerait des données représentatives, une comparaison de comportement et un rollback démontré. La stratégie proposée est additive dans le monolithe modulaire existant.
