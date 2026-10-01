# T2 — Acte de revue humaine de la preuve contractuelle

L'acte de revue est distinct de la preuve `baseline → dérogation → impact`.
Il référence la preuve et sa révision, identifie le relecteur, porte une
décision fermée et impose une justification.

Décisions autorisées :

- `ACCEPTED` — la chaîne est retenue comme représentation opérationnelle ;
- `REJECTED` — la chaîne est refusée ;
- `NEEDS_CLARIFICATION` — la chaîne reste ouverte sans conclusion.

Le contrat refuse une révision nulle et une justification vide. Il ne produit
aucun avis juridique et ne modifie pas la preuve source.

Preuve initiale : 2 tests domaine verts dans
`backend/tests/domain/dce/test_contract_review.py`.

