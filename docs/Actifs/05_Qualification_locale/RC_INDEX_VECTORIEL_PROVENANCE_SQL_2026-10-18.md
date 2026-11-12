# Index vectoriel SQL — revalidation de provenance — 18 octobre 2026

## AS-IS, risques, insertion, plan minimal

Checkout principal codex/reconcile-smartao-20261009,HEAD30f2693/WIP conservé. Index/plan actifs et autorités v3.1 relus : source/version/hash/localisateur et UNKNOWN; aucun lien contractuel implicite. Le lecteur SQL a été durci lors de la tranche précédente, mais `SqlAlchemyVectorIndex.search` reconstitue encore ses sorties depuis les copies persistées sans les confronter au lecteur. L'upsert compare seulement textehash/vecteur sur identité déjà présente, pas toute la provenance.

**Risques :** copie divergente, région inventée, document d'une autre version, hash d'entrée invalide, vecteur JSON non numérique ou modèle différent. **Insertion minimale :** réutiliser `SqlAlchemyDceRetrievalSource` pour vérifier la source courante; contrôler les copies et les vecteurs dans l'adaptateur existant, sans nouvelle abstraction ni migration. Préserver contraintes append-only, refus financiers et anciens profils.

- [x] Prouver rouges PostgreSQL synthétiques avant correction : copie/index et chaîne source, upsert, modèle/vecteur.
- [x] Contrôles minimaux avant résultat/écriture, refus génériques sans contenu ni mutation historique.
- [x] Nominal/retry/batch/isolation/fraîcheur et suites pertinentes; revue indépendante.
- [x] Lint/types/format/diff/secrets/Semgrep et hashes; vérifier Alembicbase et retirer le seul conteneur dédié.
- [x] Mettre à jour case/journal/prochaine étape unique/index et miroir Basic Memory.

Base dédiée smartao-rc-vector-sql-pg-20261018,127.0.0.1:55449,tmpfs512MiB; aucune base existante5432 ni backend live/corpus réel. Vecteurs déterministes, aucune mesure E5, aucun contrôle sémantique du vecteur sans réencodage. V6 reste non activé; DPGF non évaluable; A1 non admis/A2 HOLD/NO-GO public.

## Clôture locale et décision

Index vectoriel SQL durci sans remplacement de modèle/factory :revalidation via lecteur DCE réel,comparaison texte/hash/ordinal/locator/classification,contrôle modèle et vecteurs numériques,identité complète au retry et batch transactionnel.29nouveaux SQL/413tests knowledge/candidat/SQL/architecture réussis en14,86s;rouge initial22échecs/3verts puis3rouges numériques/retry corrigés. Revue/contre-revue indépendantes sans défaut bloquant restant. Ruff backend/scripts,mypy633,format/diff/5SHA verts;Semgrep1.179.0/225règles/2fichiers0finding0erreur,detect-secrets1.5.0 zéro finding. PostgreSQL16jetable port55449/tmpfs512MiB,fixtureshead→base,Alembic0 final,conteneur dédié retiré. Vecteurs déterministes :pas de preuve du calcul par modèle ni atomicité entre lectures distinctes,pas de relecture blob ni nouveau benchmark E5/globalbackend/Web. Adaptateur existant durci,aucun schéma/dépendance/API/UI/profil/factory changé,v6nonactivé,DPGFnonévaluable,A1nonadmis/A2HOLD/NO-GOpublic;aucun live/corpus réel/VPS/P3/déploiement/commit/push. HEAD30f2693/WIP conservés.

### Modifications

- `backend/app/modules/knowledge/infrastructure/vector_index.py` : réutilise `SqlAlchemyDceRetrievalSource`, qui valide déjà document/version/hash d'entrée et SHA du fragment. Les lignes indexées sans source courante éligible sont exclues. Toute copie discordante texte/hash/ordinal/localisateur/classification provoque un refus générique avant toute projection de résultat, sans réparation ni suppression. Un vecteur doit être numérique, non booléen, fini, non nul, de longueur/dimension déclarée cohérente; à la recherche sa dimension correspond à celle de la requête. Dépassement numérique JSON transformé en refus contrôlé.
- L'upsert vérifie la source et le vecteur avant écriture, puis toutes les composantes persistées de l'identité avant d'accepter un retry. Le vecteur existant est également validé pour éviter l'égalité Python True==1.0. Divergence d'identité refusée selon le contrat existant, batch entier rollback sur erreur. Aucun nouveau schéma/port/framework/dépendance.
- `backend/tests/db/test_vector_index_provenance_sql.py` :29cas adverses/nominaux avec vraies contraintes et transactions PostgreSQL, réutilise les seeds précédents;aucun code de modèle ni factory actif.

### Preuves exécutées

Répertoire privé `~/.local/share/smartao-proofs/rc-vector-sql-20261018/`.

- `red.log` :22échecs/3réussites avant correctif. Ce ne sont pas22défauts indépendants : certains refus d'upsert existaient mais ne couvraient pas uniformément la provenance/message attendu.
- `green-first.log` :69réussites/1échec numérique; `edge-red.log` :3échecs/26réussites avant correction OverflowError et booléen persisté au retry. Aucun échec d'infrastructure ou de construction de seed confondu avec un défaut produit.
- `targeted-final.log` :413réussites en14,86s.29nouveaux SQL + précédents modules SQLv6/fraîcheur,knowledge/retrieval/worker/benchmark,projecteurs RC,candidat/encodeur/CLI et architecture. Commande `.venv/bin/pytest --import-mode=importlib -q --tb=short` avec `SMART_AO_TEST_DISPOSABLE_DATABASE=1` et `SMART_AO_TEST_DATABASE_URL` ciblant exclusivement127.0.0.1:55449/smartao_vector_sql. DSN synthétique horsGit.
- Nominal/réessai exact,erreurs texte/hash/localisateur/ordinal/classification,hashentrée/document autreversion/hashfragment,vecteurs booléen/chaîne/null/objet/zéro/nombreextrême/dimension,modèle discordant,rollback batch,tenant/Affaire/version étrangers peuplés et même tenant prouvés. Les19tests fraîcheur existants gardent refus d'extraction incomplète/remplacement/versioncourante. Les25tests SQLv6 restent verts.
- `ruff.log` :lint globalbackend/scripts; `mypy.log` :633sources;format2fichiers et `git diff --check` verts. `code-sha256.txt` :5fichiers dont lecteur/candidat/profil inchangés. `scoped.diff` compare le changement à l'étatWIP initial, pas seulement HEAD.
- `semgrep.json`/`.log` :1.179.0,225règlessecurity-audit,2paths explicitement scannés dont nouveau fichier non suivi,0finding/0erreur et aucun warning spécifique; métriques off,analyse locale,aucun upload des résultats. Scan limité à ces2fichiers, non exhaustif. `secrets.json` :1.5.0,0finding;baseline/filtrage/staging inchangés.
- `database-isolation.txt` :PostgreSQL16image `sha256:57c72fd2a128e416c7fcc499958864df5301e940bca0a56f58fddf30ffc07777`,Mounts=[],tmpfs512MiB;fixtures upgradehead/downgradebase; `alembic-final.txt`=0. Aucun accès au5432;conteneur smartao-rc-vector-sql-pg-20261018 arrêté/retiré uniquement.
- Revue puis contre-revue en lecture seule, sans édition ou exécution indépendante; chiffres de tests issus du runner principal.

### Limites et risques restant ouverts

Aucune preuve qu'un vecteur numérique valide a réellement été calculé par le modèle déclaré : pas de réencodage ni hash attesté externe. Les métadonnées SQL sont vérifiées, aucun blob/PDF relu. Les lectures index/source sont distinctes; revalidation après lecture des lignes, sans preuve d'atomicité face à un changement ultérieur concurrent. Aucune conclusion de complétude ou d'éligibilité DCE réelle.

La contrainte historique tenant/fragment/modèle reste inchangée et n'autorise qu'une Affaire persistée : la tentative pour une seconde Affaire est explicitement refusée, sans mutation/réemploi du reçu de la première. Le support multicase du même fragment n'est pas ajouté. Les appels supplémentaires au lecteur SQL, dont ceux à l'upsert par fragment, n'ont pas de budget de performance qualifié; ne pas inférer les temps E5 isolés comme temps SQL boutenbout.

Aucune nouvelle suite globale backend/Web ni couverture exhaustive,migration ou test multithread. Permissions/MFA/API/UI non modifiées et non requalifiées;FINANCIAL_PRIVATE et DPGF restent sous gardes existantes. Pas d'activation de v6, ni admission de source.

Méthode : Superpowers using-superpowers,cadrage borné,writing-plans intégré au dossier,TDD,systematic-debugging,requesting-code-review,verification-before-completion;ECC verification-loop. Graphify consulté,Serena activé,BasicMemory miroir;Context7 sans objet (aucune nouvelle API),Jev/Manus non nécessaires,OpenDesign/Impeccable sans objet (aucun visuel).

Prochaine étape : ESSAIS DCE — mesurer ensemble le profil v6, E5 CPU réel et le lecteur DCE SQL sur un nouveau jeu BTP synthétique gelé : fidélité des ancres, précision/omissions, abstention, invalidation et budgets RAM/temps; comparer aux preuves séparées sans régler sur le jeu ni activer le candidat. DPGF reste non évaluable. A1 non admis, A2 générique HOLD et NO-GO public maintenus.
