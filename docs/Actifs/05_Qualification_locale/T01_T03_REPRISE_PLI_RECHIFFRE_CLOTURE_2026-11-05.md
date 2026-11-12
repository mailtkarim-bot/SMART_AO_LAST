# T01–T03 — refus et reprise du pli rechiffré jusqu’à la clôture

Qualification locale avec limites ; le plan global est la seule autorité de statut. Garanties générales T01–T03 restent PARTIAL.

AS-IS : L08–L11 ont raccordé le pli rechiffré, les passations, changements/actions et clôture déclarée. Une recette native de refus/reprise existe sur l’ancien parcours rectifié ; elle doit être rejouée sur ce nouveau runner, sans additionner des preuves indépendantes comme un parcours unique.

RISQUES : réponse perdue prise pour absence d’effet, retry créant un second acte, anciens accords ou sources réemployés, réponse différenciant tenant étranger/inexistant, faits de paiement ou réserves altérés par la reprise.

POINTS D’INSERTION : runners de tests L11 et recette de refus existante ; code de production uniquement sur défaut reproduit, pas d’interface ou nouvelle abstraction produit prévue.

PLAN MINIMAL :

- [x] Raccorder la recette de refus au nouveau parcours de prix/plis/passations/actions/clôture.
- [x] Injecter panne avant service et après commit réel, reconnecter le client et rejouer le corps/IDs exacts ; vérifier unicité, historique et manques.
- [x] Contrôler refus tenant/rôle/auth sans effet, confidentialité et absence de promotion de porte.
- [x] Revue, suites adaptées, types/sécurité/diff ; sauvegarde puis plan et miroir relus.

Tests : 404 générique tenant étranger/inexistant ; 401/403 ; 503 UNKNOWN avant/après effet ; premier effet unique puis replay sans nouvelle ligne/événement/outbox ; ancien dossier/accord non promu ; paiement attendu/encaissement/règlement et réserves inchangés. Aucun rouge artificiel pour un comportement existant correct ; tout bug reproduit recevra un rouge/vert avant correction.

Checkout principal/branche/HEAD vérifiés, 761 empreintes WIP L11 identiques avant édition. Preuves privées : `~/.local/share/smartao-proofs/t01-t03-repriced-recovery-20261105/`. Aucun reset/clean/stash/nouveau checkout/stage/commit/push, live/corpus réel/VPS/déploiement/dépôt ou effet externe.

## Changement et parcours retenu

Trois fichiers de tests uniquement : `backend/tests/db/test_l11_repriced_closure.py` transmet le callback de continuité ; `backend/tests/db/test_transversal_rectified_closure_recovery.py` permet un runner de clôture optionnel ; `backend/tests/db/test_transversal_repriced_closure_recovery.py` raccorde le parcours REPRICED. Le parcours par défaut et ses assertions restent inchangés. Aucun code de production, interface, API, droit, porte, schéma, migration, dépendance ou calcul modifié ; pas de rouge fabriqué pour un comportement existant correct.

Une même Affaire suit les prix importés/publiés, deux plis C10/P5, passations/reçus, changements/actions, puis réceptions/réserves/paiements et requalifications L11. Le callback de reprise utilise cette application et ce dossier exacts ; ce n’est pas une addition de chiffres de campagnes séparées.

## Refus et reprise vérifiés

- Même Patron face à un autre tenant ou identifiant absent : GET/POST404 `NOT_FOUND_OR_FORBIDDEN` identiques ; anonyme401, Responsable/Collaborateur403 sur écriture privée. Aucun nouvel effet de clôture dans ces refus.
- Panne injectée **avant exécution du service réel** : HTTP503 `RESULT_UNKNOWN`, état métier identique. Nouveau client HTTP sur la même application, même corps/IDs :201, un acte exactement égal à act_id, puis replay200 sans nouvel effet.
- Panne injectée **après retour du dispatch réel** :503UNKNOWN malgré l’acte déjà commité. Reconnexion par nouveau TestClient, corps/IDs strictement identiques :200/replayed=true et mêmes command_id/idempotency_key/act_id/result_code. La répétition supplémentaire ne change ni lignes ni compteurs.
- Les anciennes lignes d’actes sont identiques ; réserves/obligations/transitions, cycles et faits financiers restent identiques. L’unique nouvelle ligne est celle de l’acte demandé. Compteurs d’événements/outbox tenant stables aux refus/replays ; le nombre exact de nouvelles émissions au premier succès n’est pas explicitement imposé par cette recette.
- Réserves ouvertes et faits de paiement conservés ; règlement complet, reçu externe et effet juridique UNKNOWN. Un retry connu ne vaut pas accord sur une nouvelle source, réception juridique ou droit acquis.

La confidentialité opérationnelle amont est exercée par les assertions P7/L10 réutilisées : mémoire technique exact, données financières/montants/stockage exclus, contrôle financier et ZIP complet refusés au Responsable. Cela ne démontre pas une couverture exhaustive de toutes les projections ou canaux de clôture.

## Vérifications exécutées

- Parcours natif isolé : **1 réussite en45,53 s**. Campagne finale : **14 réussites en136,63 s**, retry policy, dispatcher, workflow clôture et reprise du parcours REPRICED. Avant le rerun correct, les tests du dispatcher avaient été lancés sans SMART_AO_TEST_DATABASE_URL :3 tests purs réussis/5 erreurs de configuration, aucun test DB qualifié ; refus de fixture conservé dans `dispatcher-setup-error.log`. Rerun avec base explicite dédiée, en série après la première recette, réussi. Ne pas présenter ces erreurs de configuration comme des défauts produit.
- Web ciblé : **33 réussites,3 fichiers,5,92 s**, panneaux de clôture/passation/changements couvrant intentions UNKNOWN et reprise exacte, scope et consentement. Types Web verts. Pas de nouveau global Web, lint/build ou navigateur : aucune source frontend/production modifiée ; la preuve globale L11 datée796/4ignorés/exit0 n’est pas réattribuée à cette tranche.
- Mypy application708 sources vertes ; application/tests206 diagnostics dans40 fichiers sur1276 sources, identiques à L11 après normalisation des numéros de ligne. Ruff et format des trois fichiers Python verts ; Alembic inchangé `20261102_0147`, fixtures upgrade/downgrade jusqu’à base.
- Revue indépendante en lecture seule : pas de défaut bloquant dans les trois fichiers, transmission des callbacks vérifiée ; limites d’injection/reconnexion et de compteurs/visibilité reprises ici. Aucun test ou accord humain additionnel fourni par la revue.
- Semgrep1.183.0, `p/security-audit`, métriques désactivées :79 règles/3 fichiers,0 finding/0 erreur ; analyse locale sans transmission de résultat, pas certification globale. Trois SHA figés et relus, diff scoped vérifié, scan borné des lignes ajoutées sans secret reconnu.
- Base jetable :0 table métier/0 révision Alembic, conteneur exact `844dfac46314f342e3230d25de7e29acf5924e438c58127c0badaf2b79f6c2f9` sans montage persistant supprimé ; aucun serveur navigateur ou preview créé, services préexistants conservés.

## Limites, reports et invariants

L’injection ne tue pas une transaction durant commit, ne coupe pas TCP/PostgreSQL, ne redémarre ni application ni machine. La reconnexion crée un client neuf sur la même application locale, sans prouver une reprise d’intention UI après fermeture/rechargement ; les stores UI restent en RAM. Aucun nouveau navigateur intégré, réseau concurrent, chaos multi-processus, sauvegarde/restauration de production ou test de charge.

Frontières amont conservées : DCE de fixture/copie de développement, contrat déclaré/autorité inconnue, pas de nouveau DOCX/OCR/réimport ; C3 non créé dans le parcours sans A1 courant, C4 UNKNOWN pas un montant. Les faits de paiement restent déclarés, aucune conformité ou exhaustivité déduite ; garanties générales PARTIAL.

Tenant/ownership/permissions, FINANCIAL_PRIVATE, MFA, source/version/hash/locator, append-only, idempotence et UNKNOWN maintenus ; B0/B1/B2/P0–P7, A1nonadmis/A2HOLD/NO-GO public et candidats inchangés. Aucun stage/commit/push/live/corpus réel/VPS/déploiement/dépôt ou effet externe.

Méthode : Superpowers cadrage/plan/exécution/revue/vérification, ECC security-review/verification-loop ; Graphify avant recherche, Serena activée, Basic Memory miroir du plan. Pas de TDD rouge/vert produit, puisqu’aucun défaut ni changement de comportement produit constaté. OpenDesign/Impeccable inapplicables sans interface modifiée ; Chrome/Playwright non utilisés, pas de nouvelle preuve navigateur. Context7 sans question de bibliothèque nouvelle ; Jev/Manus sans gain sur ce périmètre borné. Statut exclusif dans le plan global, miroir synchronisé après consolidation finale.
