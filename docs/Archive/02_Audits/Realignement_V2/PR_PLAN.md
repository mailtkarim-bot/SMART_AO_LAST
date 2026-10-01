# SMART AO — Plan de tranches et gates pour le réalignement v2

**24 septembre 2026 · proposition à soumettre, aucune PR créée**

| Tranche | Résultat vertical minimal | Dépendance et gate |
|---|---|---|
| T0 Caractérisation | Matrices de cet audit, correction des lacunes du cahier candidat, tests de comportement existant | Product Freeze v1.0 actif ; aucune capacité métier v2 codée. Faire revoir le périmètre PF2‑01 à PF2‑16 et la séquence. |
| T1 Applicabilité | Faits d'Affaire, règle datée, évaluation `FUTURE/ACTIVE/UNKNOWN` sourcée et revue | Product Freeze v2 promu ; migration additive, tenant, version ancienne, règle future, rollback applicatif. |
| T2 Contrat | Référence réellement incorporée, clause particulière, dérogation et impact affiché | T1 ; deux versions/hiérarchies, refus d'application générique, décision Patron. |
| T3 Sanctions/droits | Une sanction calculable validée et un événement de droit avec preuve envoi/réception séparée | T2 ; REC‑29–33, 41/42, idempotence, concurrence, formule/délai ambigu, expertise externe. |
| T4 OS/règlement | OS non valorisé, jalon réception/décompte, exposition rupture | T3 ; REC‑31–33/41/45, aucun DGD tacite implicite. |
| T5 Assurance/HSE/engagement/paiement | Un exemple par domaine avec statut honnête, coût/ressource/scope et avis expert | T1–T4 selon objet ; REC‑34–40/43, séparation financière, validations spécialistes. |
| T6 Carte Patron | Projection des 12 axes depuis les faits stabilisés, conditions GO et inconnus | T1–T5 ; aucune logique source dans React, refus Collaborateur/tenant. |
| T7 P7 renforcé | Paquet versionné avec responsabilités, droits, sanctions, paiement et acceptation distincte | T3–T6 ; REC‑45 et TECH‑CR‑08/09 ; ancien résultat P7 préservé. |
| T8 REX | Prévu/réalisé contextualisé, sans règle entreprise automatique | T7 ; portée/source/validation et confidentialité. |

Chaque PR doit joindre : diff relu, migration upgrade/contrainte/downgrade si sûr, plan de rollback code et données, tests ciblés + gates appropriées, preuve de non-régression tenant/MFA/append-only/confidentialité, impact UX et source de règle. Une PR ne doit pas prétendre qualifier une règle juridique par la seule présence de tests automatisés.

**Verdict : `READY_WITH_BLOCKERS` pour la préparation seulement.** REC‑41–45 ont été ajoutées au cahier technique candidat. Restent avant première PR métier : promotion explicite du Product Freeze v2, accord sur la portée V1/V1.x, modalités de validation juridique/assurance/QSE, catalogue UX révisé là où nécessaire et corpus DCE habilité. Le plan lui-même reste révisable après ces décisions.
