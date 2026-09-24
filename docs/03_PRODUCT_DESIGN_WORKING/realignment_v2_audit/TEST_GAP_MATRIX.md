# SMART AO — Écarts de recettes v2

**24 septembre 2026 · T0, inventaire de couverture · aucune recette v2 exécutée**  
Des tests d'Affaire/DCE/risque/P7 existent, mais aucune recette ci-dessous n'est réputée couverte par analogie de nom.

| Recettes | État | Preuve à construire après promotion |
|---|---|---|
| REC‑29/30 | MISSING | Deux versions contractuelles ; dérogation pénalité ; règle, clause et impact visibles, calcul sans plafond générique. |
| REC‑31/32/33 | MISSING | OS sans prix ; décompte et événement de droit ; rupture/substitution sans conclusion juridique automatique. |
| REC‑34/35/36 | MISSING | Engagement environnemental vendu et traçable ; applicabilité date/usage ; cas RAT infrastructure avec revue. |
| REC‑37/38/39/40 | MISSING | Assurance hors activité déclarée ; HSE sans ressource ; circuit de facturation public ; règle future non bloquante. |
| REC‑41/42/43/44/45 | MISSING dans le code ; ajoutées au cahier technique candidat §21.2 le 24 septembre | DGD tacite sous conditions ; pénalités cumulatives ; engagement non chiffré ; cash portefeuille ; rectificatif touchant délai/droit. |
| TECH‑CR‑01/02 | PARTIAL comme socle, MISSING pour v2 | Tenant et absence de fuite par la nouvelle Carte, API, recherche, export et IA. |
| TECH‑CR‑03/04/05 | MISSING | Retry droit sans doublon, règle supersédée pendant édition, invalidation ciblée après rectificatif. |
| TECH‑CR‑06/07 | PARTIAL comme socle, MISSING pour v2 | Formule ambiguë sans chiffre ; injection CCAP sans élévation de rôle/outils. |
| TECH‑CR‑08/09/10 | MISSING | Tâche ≠ droit préservé ; envoi ≠ accusé ; rollback code/données sans perte de preuve. |

Pour chaque recette : nominal/refus, tenant étranger, rôle, source/version, `UNKNOWN/PARTIAL/REVIEW_REQUIRED`, retry, concurrence et preuve append-only quand applicable. Le résultat attendu doit être lié à une règle/validation externe pour les cas juridiques, assurance et HSE.

**Preuves existantes à réutiliser, sans les surclasser :** `backend/tests/application/test_decision_risk.py`, `test_case_order_p6.py`, `test_dce_contract_risk_read.py`, `backend/tests/security/test_dce_contribution_conflicts.py` et tests de sécurité de partage/retrieval. Ces tests caractérisent le socle v1, pas les REC v2.
