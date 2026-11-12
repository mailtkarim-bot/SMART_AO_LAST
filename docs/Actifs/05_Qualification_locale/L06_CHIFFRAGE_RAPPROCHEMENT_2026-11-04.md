# L06 — chiffrage sourcé et rapprochement partenaire

Campagne locale qualifiée avec limites ; le statut opérationnel reste dans le plan global. L06 général reste PARTIAL.

AS-IS : import Excel, brouillon financier, positions sourcées et rapprochements humains existent. Les tests natifs couvrent déjà les coûts inconnus, sources remplacées, transport exclu et confidentialité.

RISQUES : une réponse HTTP 5xx peut suivre une écriture réussie ; les identifiants doivent survivre. Les réponses tardives et intentions d’une autre session/Affaire ne doivent pas exposer de données. Un rapprochement humain ne démontre ni comparabilité économique ni prix certain.

POINTS D’INSERTION : hook usePricingImport, appel App, tests du hook ; réutilisation des contrats et parcours backend existants. Aucun changement de schéma ou de porte prévu.

PLAN MINIMAL :

- [x] Prouver les refus/reprises d’import par tests rouges, puis corriger le hook et son appel.
- [x] Qualifier import, positions, sources, hypothèses et rapprochements synthétiques avec les services natifs.
- [x] Consolider les derniers contrôles, sauvegarde et miroir du plan.

TESTS À AJOUTER : HTTP 503 après import, double clic synchrone, GET interdit avant reçu, intention modifiée refusée, réponse ancienne masquée, reprise dans le contexte exact. Les tests natifs doivent laisser visibles unités, transport exclu, manques et offres non comparables.

Preuves locales : `~/.local/share/smartao-proofs/l06-pricing-comparison-20261104/`. Les 743 empreintes WIP L05 sont identiques avant modification ; branche et HEAD attendus vérifiés.

## Fonction livrée et contrats

Le hook d’import conserve vues et intentions par session/propriétaire, Affaire et rapport normalisé. Un HTTP 503 ou une réponse non vérifiable laisse UNKNOWN ; les champs et opérations concurrents sont bloqués, le retry conserve fichier, révisions et identifiants. Aucun GET ne réconcilie une commande sans reçu. Les réponses d’un autre contexte ne sont pas affichées et ne déclenchent pas la relecture de son brouillon. Le commit vérifie reçu, identifiants, agrégats exacts et révisions avant succès. Aucun prix ou champ financier nouveau n’est calculé.

Fichiers logiciels : `web/src/features/pricing/usePricingImport.ts`, son test, le seul appel interne dans `web/src/app/App.tsx`, et `backend/tests/db/test_l06_sourced_costing_path.py`. Aucun JSX, style, backend de production, contrat HTTP, dépendance ou migration changé.

Le nouveau parcours natif importe une feuille synthétique, applique son batch au brouillon puis rejoue sans double effet ; il rattache explicitement le coût déclaré 12000 au poste, conserve transport sans coût et couverture UNKNOWN. Deux devis de la même Affaire sont revus humainement et leurs lignes sourcées « u »/« forfait » restent NEEDS_CLARIFICATION. Ce rapprochement ne démontre pas une correspondance automatique aux postes importés, ni une couverture ou une comparabilité des montants.

## Vérifications

- TDD : trois rouges initiaux (503 preview/commit, double preview), puis rouge preview étrangère, reçu incohérent et clé de rapport non normalisée ; corrections minimales puis 18 tests du hook inclus dans la campagne finale pricing.
- Web global final après gel logiciel : 775 réussites, 4 ignorés, 92 fichiers, 343,89 s ; code de sortie 0. Sources SHA inchangées après le run. Pas de preuve navigateur supplémentaire.
- Web pricing final : 97 réussites, 1 ignoré, 8 fichiers, 40,75 s. Types Web, ESLint et build finaux exécutés ; avertissements existants `setDecisionDossier` et chunk >500 kB.
- Backend ciblé : 61 réussites, 107,96 s ; recette native renforcée rejouée ensuite : 1 réussite, 25,74 s. Ces tests couvrent sources/cellules, coût inconnu, provenance de l’original, histoire/invalidation, transport/exclusions/validité, tenant/rôle/MFA, révisions, idempotence, refus et contraintes append-only. Le resolver d’authentification du parcours intégré est synthétique ; il ne qualifie pas une connexion réelle.
- Premier essai natif : erreur du test (`model_dump` sur dataclass), corrigée par `asdict`. Une fixture Web retournait batch-2 pour une lecture batch-1 ; corrigée sans retirer le nouveau contrôle de contexte. Deux lancements Vitest depuis la mauvaise racine sont des erreurs d’outil, pas des échecs produit. Le premier run global a terminé à 774 réussites, 4 ignorés et le seul rouge de normalisation, car il avait chargé la source avant le dernier correctif ; il n’est pas une preuve du gel final. La tentative de lui envoyer TERM a constaté un processus déjà terminé, sans effet sur les autres processus.
- Mypy application : 708 fichiers verts. Application/tests : 206 diagnostics dans 40 fichiers, 1267 sources, identiques après normalisation des numéros de ligne au relevé L05 ; aucun diagnostic ajouté. Ruff et format du nouveau test vérifiés. Tête Alembic inchangée `20261102_0147` ; fixtures upgrade/downgrade jusqu’à base.
- Semgrep 1.183.0, configuration `p/security-audit`, métriques désactivées : 99 règles sur les 4 fichiers logiciels, 0 finding, 0 erreur ; aucune certification globale ou transmission de résultat. Diff et absence de fichiers inattendus contrôlés sur le delta L06, distinct du WIP antérieur.
- Base jetable propre : 0 table métier, 0 révision Alembic ; conteneur exact `7d3602d2e83aaeaf07a2624d052a1af21ea9f3de0bc5bb3363634d9b76c5ab0b` sans montage persistant arrêté et supprimé. Services préexistants non touchés.

## Limites, reports et outils

Intention conservée en mémoire du hook seulement : un rechargement complet ne constitue pas une reprise durable de fichier. Les projections financières peuvent nécessiter une nouvelle lecture après remplacement de source. La matrice de couverture générale, les conversions d’unités/devises, l’allocation automatique entre lignes et le calcul de coût complet ne sont pas démontrés ; aucun prix certain, sélection automatique ou promotion de porte.

Pas de nouvelle preuve navigateur/authentification réelle, d’accessibilité complète ou de corpus réel. Aucun écran changé : OpenDesign/Impeccable inapplicables à ce correctif interne. Graphify utilisé avant navigation textuelle ; Superpowers cadrage/plan/TDD/revue/vérification et ECC product-capability/verification-loop appliqués. Revue indépendante en lecture seule : normalisation de la clé relevée et corrigée ; vérification des reçus préexistante renforcée. Serena non utilisé faute de navigation sémantique nécessaire ; Context7 sans question de bibliothèque nouvelle ; Jev/Manus sans gain pour ce périmètre borné. Basic Memory conserve le checkpoint d’orientation et reçoit le miroir du plan après consolidation.

Gates, candidats, FINANCIAL_PRIVATE, droits et autorité Patron conservés ; aucun effet externe, signature réelle, dépôt, commit, push ou GO public. Aucun accord ou hypothèse partenaire ne devient un engagement certain.
