# T18 — Acte append-only de vérification d’export

Le résultat local `MATCH`, `MISMATCH` ou `UNAVAILABLE` devient un acte séparé,
lié à l’export et à l’acteur de vérification. `MATCH` exige le hash calculé ;
`UNAVAILABLE` interdit d’enregistrer un hash absent de la vérification.

Cet acte ne modifie pas la demande, les transitions ou le contenu exporté et
ne prouve aucune réception externe.

