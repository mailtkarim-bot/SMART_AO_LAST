# L11 — réception, réserves et paiement depuis la passation du pli reconstruit

Qualification locale avec limites ; le plan global demeure seul statut. L11 général reste PARTIAL.

AS-IS : dossier de clôture, réceptions/réserves/paiements et invalidation/requalification existent. Le parcours L10 donne deux générations exactes de changements/actions ; sa clôture reste à raccorder. Le panneau n’est pas suspendu sous reprise DCE et sa relecture manuelle ne retire pas tous les consentements si l’empreinte change.

RISQUES : accord sur un ancien dossier repris sur un nouveau, acte/réserve/action liés à la mauvaise passation, paiement attendu confondu avec encaissement, donnée privée au Responsable, UNKNOWN transformé en conformité, prescription ou règlement certain.

POINTS D’INSERTION : wrapper/lecture et sous-arbre de formulaire du panneau, appel App, runners synthétiques L10/L11 ; pas de nouveau schéma/calcul/gate.

PLAN MINIMAL :

- [x] Reproduire suspension absente et ancien consentement conservé après nouveau dossier, y compris formulaires de suivi imbriqués.
- [x] Corriger le remount/scope et les consentements sans perdre les intentions UNKNOWN.
- [x] Raccorder la recette de clôture au parcours du pli rechiffré : sources/actions, réserves, faits de paiement et requalifications exacts, anciens accords historiques.
- [x] Vérifier rôle/tenant/MFA, confidentialité, refus/retry, rendu et sécurité ; sauvegarde puis plan/mémoire relus.

Tests : source incertaine sans lecture/écriture ; anciennes réponses ignorées ; nouveau hash retirant confirmations et notes ; réception/réserve/paiement distincts ; données privées inaccessibles au Responsable ; actions périmées invalidantes et actes nouveaux sans réécriture de l’historique.

Les 759 empreintes WIP L10 sont identiques avant édition, branche/HEAD et checkout principal vérifiés. Preuves privées : `~/.local/share/smartao-proofs/l11-repriced-closure-20261105/`. Aucun reset/clean/stash/nouveau checkout/stage/commit/push, live, corpus réel, dépôt ou effet externe.

## Fonction livrée

Le dossier Patron est masqué et ses lectures/formulaires suspendus pendant la reprise DCE incertaine. Son périmètre de lecture suit la session, version et disponibilité DCE ; le store stable propriétaire/Affaire conserve les intentions UNKNOWN. La relecture explicite « Relire le dossier et ses sources » est maintenant disponible hors intention en attente.

Après lecture d’une nouvelle empreinte, le sous-arbre du dossier entier est remonté : réception, réserve, suivi imbriqué, paiement, sortie/REX/réemploi perdent leurs anciennes confirmations et notes de consentement. Un champ de dossier courant n’est plus injecté dans un acte conservant l’accord de l’ancien dossier. Les déclarations et historiques serveur ne sont pas effacés. La source reste une lecture ponctuelle, pas une garantie de stabilité future.

Six fichiers logiciels : `web/src/features/decision/CaseClosurePanel.tsx`, son test et `web/src/app/App.tsx` ; `backend/tests/db/test_l10_repriced_execution.py`, `backend/tests/db/test_l11_v2_closure.py`, `backend/tests/db/test_l11_repriced_closure.py`. Les deux recettes existantes reçoivent des callbacks/runners optionnels pour le raccordement ; pas de backend de production, calcul, schéma, migration, rôle ou gate modifié. L’accès App reste Patron-only, les chiffres financiers ne passent pas dans la projection Responsable.

## Parcours natif continu

La même Affaire traverse les deux prix importés/publiés, plis exacts, P7/reçus et changements/actions L10, puis la recette L11 existante est rejouée sur ces sources du pli reconstruit. Réception avec réserves déclarée, réserve liée à son acte origine et rapprochement exact de l’action V2 à la réception ; les identifiants/hash de référence sont ceux du dossier relu.

Le paiement attendu et l’encaissement humain sont deux faits distincts avec devise et date déclarées. L’observation de leur paire vaut -40000 unités mineures dans cette recette, jamais solde, encaissement bancaire constaté ou échéance juridique. Réserves et inconnus ne sont pas effacés par ces montants ; règlement complet et effets juridiques restent UNKNOWN.

Un remplacement de source invalide les comparaisons/actes concernés sans modifier leur JSON d’accord historique. Les anciennes empreintes/confirmations sont refusées ; nouvelles réception et réserve exigent de nouveaux IDs, source relue et justification. Les réserves ouvertes restent conservées. La requalification ne devient pas achèvement ou levée d’office. Le scénario vérifie aussi refus Responsable sur les API privées de clôture, rôles/tenant/MFA, refus sans effet, retry exact et registres append-only via ses suites adaptées.

Frontière conservée : le DCE initial est une fixture admise/classifiée et copie de développement du parcours amont, les contrats et sources sont déclarés, les prix suivent les routes natives ; aucun nouveau DOCX/OCR/réimport DCE ou corpus réel. La limite L10 reste entière : pas de C3 quantitatif sur ce parcours sans source A1 courante, C4 UNKNOWN ne devient pas montant par la clôture.

## TDD, revue et preuves

- Web global final sur gel : **796 réussites,4 ignorés,93 fichiers,274,80 s,exit0**. Six SHA logiciels inchangés. Premier run distinct : même bilan de réussites en285,09 s mais retour de processus143 ; il n’est pas qualifié exit0. La passe finale a été relancée en session TTY et son retour0 a été relu.
- Quatre rouges Web observés : suspension absente, ancienne confirmation cochée en réception **et dans le suivi de réserve imbriqué** après nouvelle empreinte, relecture explicite absente. Onze tests du panneau verts après correction ; ciblés finaux : **12 réussites,2 fichiers,7,73 s**, avec le contrat de confirmation existant. Les contrôles de résultat/IDs exacts et UNKNOWN du panneau préexistaient et restent exécutés.
- Recette native raccordée : **1 réussite en150,24 s**. Backend final : **19 réussites en149,99 s**, contrats clôture/source d’actions/requalification, workflow et parcours du pli rechiffré. Réception, réserves, faits de paiement, invalidation/source remplacée, absence de transfert d’accord, confidentialité, MFA/tenant/rôles, concurrence, idempotence, append-only et barrière de downgrade exercés.
- Types Web/lint/build verts ; avertissements existants App `setDecisionDossier` et chunk >500 kB. Mypy application708 sources vertes ; application/tests206 diagnostics dans40 fichiers sur1275 sources, identiques à L10 après normalisation des numéros de ligne. Ruff des trois fichiers Python vérifié ; Alembic inchangé `20261102_0147`, fixtures upgrade/downgrade jusqu’à base.
- Revue indépendante en lecture seule : pas de finding concret ; réinitialisation de tout le sous-arbre, conservation de pending et accès Patron vérifiés statiquement. La revue n’a ni exécuté de tests ni validé les actes d’un humain réel.
- OpenDesign Local Codex : catalogue et artefact SMART AO existant consultés ; composants/styles existants conservés, référence Linear complémentaire seulement, autorité Owner/CYTD inchangée. Impeccable contexte/craft-floor/harden puis detector `[]`, pas de prototype supplémentaire ou Cloud.
- Chrome DevTools Local : vrai panneau sur projections natives privées synthétiques enregistrées, API simulée de relecture sans écriture. Justification/confirmation préparées, empreinte invalidée présentée puis vraie relecture du panneau : anciennes confirmations/notes absentes ; suspension masque les formulaires ; dossier requalifié réouvert et trois onglets contrôlés. Six captures inspectées à1280/393px, sans débordement global/cookies/stockage/ressources externes, cases de consentement non cochées. Les montants visibles sont des données synthétiques de la vue **Patron** ; ils ne constituent pas une vue conducteur. Pas Playwright, nouveau login/écriture API navigateur réels ou audit WCAG complet.
- Semgrep1.183.0, `p/security-audit`, métriques désactivées :99 règles/6 fichiers,0 finding/0 erreur ; analyse locale sans transmission de résultat ni certification globale. Scan borné des lignes ajoutées sans secret reconnu, six SHA logiciels figés et relus, diff scoped vérifié.
- Base jetable :0 table métier/0 révision Alembic ; conteneur exact `69f12d8a56cd9e316c9dab0f825497291fefec75ae94a19a2963a008519dc92b`, sans montage persistant, supprimé. Preview et clients navigateur dédiés fermés, services préexistants conservés.

## Limites, reports et invariants

Un accord sur une ancienne empreinte ne vaut pas accord courant. Les actes/réserves restent déclarés, authenticité et autorité des pièces non établies ; aucun paiement certain, solde global, réception juridique, droit acquis ou extinction contractuelle automatique déduit. Le dossier garde REVIEW_REQUIRED et UNKNOWN même après les gestes de recette ; L11 général PARTIAL.

Stores en RAM sans reprise durable après recharge complète ; une modification externe peut nécessiter une relecture, pas de surveillance continue ajoutée. Pas de nouveau calcul juridique/calendaire, conversion de devises, agrégation portefeuille ou comptabilité. FINANCIAL_PRIVATE, permissions, source/version/hash/locator, idempotence, append-only, MFA et P0–P7 préservés ; A1nonadmis/A2HOLD/NO-GO public et candidats inchangés. Aucun stage/commit/push/live/corpus réel/VPS/déploiement/dépôt ou effet externe.

Méthode : Superpowers cadrage/plan/TDD/revue/vérification, ECC product-capability/security-review/verification-loop ; Graphify avant recherche, Serena activée, OpenDesign Local Codex, Impeccable, Chrome DevTools Local et Basic Memory. Context7 sans question de bibliothèque nouvelle, Jev/Manus sans gain dans ce périmètre borné. Plan seul statut ; miroir synchronisé et relu après consolidation finale.
