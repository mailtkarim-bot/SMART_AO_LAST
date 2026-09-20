# SMART AO — EXP-07 : capitalisation, validité et réemploi

**Statut :** lecture Patron de la capitalisation implémentée ; rétention et gel restent à faire

## Registre des faits réemployables

| Fait | Portée par défaut | Validité | Réemploi autorisé |
|---|---|---|---|
| résultat P7 `COMPLETED` | Case/lot | liée à la source et à sa date | preuve descriptive, après lecture Patron |
| résultat P7 `UNKNOWN` ou `INTERRUPTED` | Case/lot | non concluante | analyse locale, jamais règle de succès |
| REX `CASE_ONLY` | Case | durée et périmètre explicites | même Affaire seulement |
| REX `LOT_PATTERN` | lot | source et applicabilité à vérifier | autre Affaire seulement après validation Patron |
| REX `ENTERPRISE_PATTERN` | entreprise | source, P7 concluante et validation `APPROVED` | réemploi déclaré, révocable |

## Règles

- la source, le lot, la version et l'état au moment du réemploi sont affichés ;
- une preuve expirée, remplacée ou sans portée applicable devient `REVIEW_REQUIRED` ;
- une capitalisation ne modifie jamais le P7 source ;
- le Collaborateur peut exploiter une règle publiée dans son périmètre mais ne la valide pas ;
- les exportations suivent la classification de la source et le droit Patron existant.

## Décision

La lecture Patron des faits REX est maintenant disponible via `GET /api/v1/patron/cases/{case_id}/rex`. Elle reste limitée au tenant, affiche lot, portée, validation, source, motif, observation et suivi, et ne déduit aucune applicabilité automatique. Les règles de suspension, export, conservation et fermeture restent à implémenter avant le gel. Aucun moteur de recherche global ni apprentissage automatique n'est nécessaire pour le gel EXP-07.

Le test PostgreSQL `backend/tests/application/test_case_order_p6.py` vérifie la relecture Patron du REX créé et la tête Alembic ; 3 tests passent.

**Prochaine étape :** cadrer puis implémenter la suspension, l'export, la conservation et la fermeture selon les droits et la rétention.
