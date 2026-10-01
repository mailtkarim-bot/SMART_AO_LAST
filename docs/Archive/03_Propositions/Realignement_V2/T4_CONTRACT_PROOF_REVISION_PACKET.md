# T4 — Révision contrôlée d’une preuve contractuelle

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Résultat de la revue complète

Le socle T2/T3 est stable : persistence tenant-scoped, actes append-only,
projection du dernier état, API Patron et C07 sont couverts par les gates
backend/frontend. La suite complète compte 1 740 tests backend et 188 tests
frontend verts.

## Objectif de T4

Permettre de déposer une nouvelle révision d’une preuve lorsque la revue
humaine demande une clarification ou rejette la représentation, sans modifier
la révision précédente ni effacer son acte de revue.

## Contrat attendu

- une nouvelle révision possède une identité et une source propres ;
- la révision précédente reste consultable ;
- un acte `REJECTED` ou `NEEDS_CLARIFICATION` ne devient jamais `ACCEPTED` par
  simple rejeu ;
- toute nouvelle révision exige une nouvelle revue humaine ;
- une révision inconnue ou étrangère au tenant est refusée neutrement ;
- la projection C07 indique la révision et le dernier acte associés.

## Preuves à produire

Migration ou contrainte additive si nécessaire, tests PostgreSQL de révision,
rejeu et tenant, test API Patron, projection C07, puis suite backend/frontend.

## Limites

Pas de moteur juridique, de recalcul automatique de délai/pénalité, de scoring,
de signature électronique, de pilote client ou d’ouverture publique.

