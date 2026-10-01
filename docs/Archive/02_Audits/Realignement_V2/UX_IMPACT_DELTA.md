# SMART AO — Impact UX du candidat v2

**24 septembre 2026 · proposition, aucune route ou surface créée**  
Référence active : catalogue UX v0.3. Code vérifié : `web/src/app/canonicalSpaces.ts` et panneaux décision/risques.

| Espace | État actuel du code | Impact candidat à arbitrer dans le catalogue |
|---|---|---|
| C01 Accueil Patron | `MATERIALIZED` | Montrer conditions et alertes de la Carte, sans score ni tableau financier pour Collaborateur. |
| C05 « À résoudre » | `PARTIAL` | Ajouter types dérogation, sanction, droit/échéance, assurance, HSE, engagement et dépendance ; fermer une tâche ne ferme pas le fait source. |
| C07 Décision | `MATERIALIZED` avec risques sourcés | Carte 12 axes, portes P2/P3/P4/P6/P7, preuves, conditions, inconnus et décisions distinctes ; l'écriture Patron `POST /api/v1/patron/cases/{case_id}/regulatory-profiles` est rattachée à cette surface sans nouvelle destination. |
| C08 Prix | `MATERIALIZED` | Exposition sanctions, cash, clause de révision, HSE et post-réception en vue Patron seulement. |
| C09 Partenaires | `BACKLOG` | Minimum de preuve fournisseur/ST/assurance et dépendances ; aucune promesse de workflow complet. |
| C10 Réponse | `MATERIALIZED` | Relier promesse mesurable à preuve, coût, capacité et responsable futur. |
| C12 Résultat/passation | `BACKLOG` | Paquet P7 et protection des droits ; distinguer acte enregistré, paquet prêt, acceptation et réception externe. |
| C13 Entreprise | `MATERIALIZED` | Portée des assurances et validations externes, sans transformer une attestation en couverture. |

**Gate UX :** vérifier les 104 identifiants et PUX existants ; réviser le catalogue si une nouvelle surface ou un nouveau comportement contractuel est nécessaire. Tester clavier, focus, annonce des états `UNKNOWN/REVIEW_REQUIRED`, rôles et responsive. L'état `MATERIALIZED` du shell ne constitue pas une preuve de la capacité v2.
