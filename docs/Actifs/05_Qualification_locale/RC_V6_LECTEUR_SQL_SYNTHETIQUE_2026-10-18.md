# Profil candidat v6 — lecteur DCE SQL synthétique — 18 octobre 2026

## AS-IS et cadrage

HEAD30f2693, branche codex/reconcile-smartao-20261009, WIP conservé. Plan/index et autorités v3.1 relus; CT2-083 impose REVIEW_REQUIRED sans priorité documentaire implicite. V6 est sans factory active, jeu7 E5 mesuré séparément. Tests SQL existants qualifient lecteur/index mais pas leur composition avec v6.

**Risques :** preuve périmée dans le cache, fragments d'extraction incomplète, confusion tenant/Affaire/version, perte de condition après segmentation, DPGF observable. **Insertion :** tests DB candidats réutilisant le seed SQL existant; pas d'API/UI ni activation. **Plan minimal :** cas adverses avec vrai lecteur/transactions PostgreSQL et encodeur déterministe au score0.84, puis suite pertinente, contrôles, revue, nettoyage et miroir Basic Memory. Aucun benchmark E5 inféré de ce test d'intégration.

- [x] Prouver octets/ancres/hash/lot/source exacts, négation et conditions hors segment, retry sans effet.
- [x] Prouver refus des extractions inéligibles, invalidation cache et changement pendant requête.
- [x] Prouver tenant/Affaire/version et rectificatif; garde DPGF avant lecture/encodage.
- [x] Revue et suites ciblées, lint/types/diff/secrets/Semgrep; vérifier tête puis downgrade base jetable.
- [x] Nettoyer uniquement la ressource dédiée, consigner résultats/limites et prochaine tranche au plan/index/BM.

Base dédiée smartao-rc-v6-sql-pg-20261018, port127.0.0.1:55448, tmpfs512MiB sans volume persistant. Aucun accès au PostgreSQL existant5432, backend live/corpus réel/VPS/déploiement/P3/push/GO public. DPGF non évaluable; A1 non admis/A2 HOLD/candidat HOLD.

## Résultats et décision

Qualification locale SQL v6 exécutée :25nouveaux tests,384knowledge/candidat/SQL/architecture réussis en10,44s dont19freshness existants. Trois défauts de provenance reproduits puis corrigés dans le lecteur :hashtexte stocké discordant refusé par erreur générique avant encodage, document appartenant à une autre version et hashentrée différent exclus par jointure exacte. Tests couvrant ancres UTF8/région/hash/lot, condition hors segment et négation, refus extraction incomplète même à date égale, cache chaud, changement pendant requête, rectificatif avec nouveau document, tenant/Affaire/version étrangers peuplés dont même tenant, et DPGF avant lecture. Revue indépendante et contre-revue sans défaut bloquant restant. Ruff backend/scripts,mypy633,format/diff/6SHA verts;Semgrep1.179.0/225règles/3fichiers0finding0erreur,sans warning spécifique;detect-secrets1.5.0 zéro finding. Profil exact v6 et encodeur déterministe0.84;aucune nouvelle mesure E5,aucune relecture blob ni analyse DCE entière. PostgreSQL16jetable tmpfs512MiB/port55448,migrationshead→base par fixtures et Alembic0 final vérifié,conteneur dédié retiré;aucun accès au5432. Aucun changement schéma/API/UI/factory/profil/dépendance,aucun moteur remplacé/commit/push/live/corpus réel/P3/VPS/déploiement/GOpublic. HEAD30f2693/WIP conservés. CandidatHOLD,A1nonadmis/A2HOLD.

### Modification minimale

- `backend/app/modules/knowledge/infrastructure/dce_source.py` : jointure document/extraction sur tenant,ID,version,hash d'entrée; contrôle du SHA256 du texte avant construction des chunks, erreur `DCE_FRAGMENT_INTEGRITY_MISMATCH` sans contenu/ID. Aucun résultat partiel en cas de hashtexte discordant. Une extraction récente incohérente ne fait pas réapparaître l'ancienne. Ce lecteur est partagé avec l'indexation existante : comportement durci pour les données incohérentes; aucune activation du candidat.
- `backend/tests/db/test_candidate_retrieval_sql.py` :25cas nouveaux, profilv6 du dépôt chargé tel quel; vecteurs384dimensions normés,cosinus0.84 pour forcer le secours typé et callbacks de commit SQL pendant requête. Ancres de type/condition comparées aux octets originaux, locator entier comparé, cache/réessai et conservation historique prouvés.
- `backend/tests/db/test_knowledge_source_freshness.py` : helper de seed extrait de la fixture inchangée pour créer deux tenants réellement peuplés; les19tests existants restent verts.

### Preuves et reproduction

Répertoire privé `~/.local/share/smartao-proofs/rc-v6-sql-20261018/` :

- `initial.log` : erreur d'import du test corrigée, aucune exécution produit; `qualification-first.log` :14verts/6échecs de construction de données, contrainteSQL interdisant les fragments sous FAILED_SAFE/UNSUPPORTED/REJECTED_LIMIT. Seeds corrigés; REVIEW_REQUIRED conserve un fragment réellement stocké.
- `hash-red.log` :1défaut produit/20verts; `refusal-red.log` :refus d'intégrité attendu non levé; `chain-red.log` :3défauts produit de provenance et3NameError du test corrigés séparément,18verts. Ne pas confondre les erreurs du banc avec des défauts du logiciel.
- `sql-green.log` :43tests verts avant dernier complément; `targeted-final.log` :384réussites en10,44s. Suite :2modules DB SQL/fraîcheur, candidat/projecteurs RC/retrieval/knowledge/worker/benchmark,encodeur/vectorindex,CLI et architecture.
- Commande DB avec variables `SMART_AO_TEST_DATABASE_URL` désignant exclusivement127.0.0.1:55448/smartao_v6_sql et `SMART_AO_TEST_DISPOSABLE_DATABASE=1`, `.venv/bin/pytest --import-mode=importlib -q --tb=short` sur ces modules. Aucun secret réel utilisé; DSN synthétique horsGit.
- `ruff.log`, `mypy.log` :lint globalbackend/scripts et types633sources;3fichiers formatés, `git diff --check` vert. `semgrep.json`/`.log` :225règlessecurity-audit,3paths explicitement listés dont le nouveau fichier non suivi,0finding/0erreur; métriques off,analyse locale sans upload des résultats. Scan limité à ces fichiers, pas un audit exhaustif.
- `secrets.json` :detect-secrets1.5.0,0finding sur3fichiers,baseline/filtrage non modifiés. `code-sha256.txt` :6fichiers vérifiés, inclut code/profil candidats inchangés.
- `database-isolation.txt` :image PostgreSQL `sha256:57c72fd2a128e416c7fcc499958864df5301e940bca0a56f58fddf30ffc07777`,Mounts=[],tmpfs512MiB; migrations inchangées,fixtures upgradehead/downgradebase,tablealembic_version vide vérifiée après suite. Conteneur dédié arrêté et retiré.

### Limites et risque restant

Cette passe démontre le contrat SQL→service candidat avec vecteurs déterministes; le benchmark E5 réel jeu7 reste une preuve séparée, sans nouvelle mesure mémoire/latence. Le hash d'entrée est comparé aux métadonnées SQL : ni blob ni PDF relu. Aucun statut de complétude DCE ou admission produit n'en découle. Pas de nouvelle suite globale backend/Web,ni couverture exhaustive ni scénario multithread; les changements committés pendant encode_query éprouvent des instants contrôlés. Les permissions/MFA/API/UI demeurent inchangées et ne sont pas requalifiées par ces tests de composition.

L'index vectoriel SQL possède sa propre lecture : sa cohérence document/version/hash et texte/vecteur persistés n'est pas qualifiée par le seul durcissement du reader. Cette frontière distincte motive la prochaine tranche, sans affirmer une exploitation réelle ni modifier un moteur actif ici.

Méthode : Superpowers using-superpowers,cadrage borné,plan,TDD sur3défauts,systematic-debugging,requesting-code-review,verification-before-completion;ECC verification-loop;Graphify consulté,Serena initialisé/activé,BasicMemory miroir. Context7 sans objet (aucuneAPI de bibliothèque nouvelle),Jev/Manus non nécessaires,OpenDesign/Impeccable sans objet (aucun changement visuel).

Prochaine étape : ESSAIS DCE — qualifier et renforcer la revalidation de provenance de l’index vectoriel SQL existant (document/version/hash d’entrée, fragment et vecteur stockés), avec contre-exemples PostgreSQL synthétiques et refus des preuves discordantes; conserver le profil v6 non activé et DPGF non évaluable. A1 non admis, A2 générique HOLD et NO-GO public maintenus.
