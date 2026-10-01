# T2 — Preuve baseline → dérogation → impact

## Décision de périmètre

La première tranche T2 conserve uniquement la chaîne de preuve nécessaire pour
relier un signal contractuel à une référence source, une dérogation éventuelle
et un impact opérationnel. Elle ne déduit ni validité juridique, ni droit, ni
obligation certaine.

## AS-IS audité

Les signaux CCAP/CCTP existants sont déterministes, bornés à des familles
documentaires classifiées et exposent déjà l'observation, la règle, la version,
le fragment et le locator. La lecture Patron est tenant-scoped et en lecture
seule. Aucun contrat existant ne portait les trois maillons ensemble.

## Preuve minimale livrée

`ContractBaselineDeviationImpact` porte :

- l'Affaire et l'observation source ;
- au moins une référence source et une formulation de baseline ;
- une dérogation et un impact facultatifs tant qu'une revue humaine n'a pas
  confirmé la chaîne ;
- un état fermé (`SOURCE_SIGNAL_ONLY`, `HUMAN_REVIEW_REQUIRED`, `CONFIRMED`,
  `UNKNOWN`).

La validation refuse une baseline sans source, un texte vide et un état
`CONFIRMED` sans dérogation et impact. Un signal source seul reste valide sans
inventer de conclusion juridique.

## Preuve exécutée

- 5 tests domaine verts dans
  `backend/tests/domain/dce/test_contract_baseline_deviation_impact.py` ;
- refus des chaînes incomplètes et des sources absentes ;
- conservation explicite du statut `SOURCE_SIGNAL_ONLY`.

## Limites conservées

- pas de migration, endpoint, index persistant ou moteur de règles dans cette
  tranche ;
- pas de calcul de délai, pénalité, couverture ou conformité ;
- l'impact demeure une observation opérationnelle à qualifier par un humain.

