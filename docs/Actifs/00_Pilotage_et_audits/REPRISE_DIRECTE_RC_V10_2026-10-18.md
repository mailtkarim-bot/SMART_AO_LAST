# Reprise directe — RC v10 en cours — 18 octobre 2026

> Instantané historique du 18/10. Pour reprendre le travail actuel, lire la [passation L08 du 27/10](REPRISE_DIRECTE_L08_COUVERTURE_2026-10-27.md) et le plan global; les étapes RC ci-dessous ne sont pas la prochaine tranche active.

## Lire et reprendre ici

Checkout principal **`/home/noor/PROJECTS/BTP/SMART_AO_V8`**, branche `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`. Le WIP important est conservé, avec de nombreux fichiers non suivis. **HEAD seul ne contient pas ce travail.** Utiliser ce checkout directement ; ne pas ouvrir un ancien worktree, reset/clean/stash ou stage global. Aucun commit/push de cette session.

1. Vérifier `git status --short`, branche et HEAD, puis lire `AGENTS.md`, l’index actif, l’en-tête du plan et sa seule ligne active. Le plan est l’unique statut opérationnel ; Basic Memory est son miroir.
2. Lire `docs/Actifs/05_Qualification_locale/RC_CONDITIONS_GOLD_V10_2026-10-18.md`, puis les fichiers précis ci-dessous et les tests. Les chapitres RC des trois cahiers v3.1 restent l’autorité métier/provenance/UNKNOWN.
3. Rejouer les 52 tests ci-dessous. Reprendre les étapes restantes, sans refaire v9 ni déclarer v10 qualifiée.

## État du code au point d’arrêt

La demande de changement de session a interrompu une tranche **en cours**, pas clôturée.

| Fichier | État réel |
|---|---|
| `backend/app/modules/knowledge/application/rc_candidate_conflicts.py` | `_CONDITIONAL_IMPERATIVE` ajouté, option `conditional_imperatives=False`. V10 reconnaît n°/no et suffixes conditionnels bornés ; sujet/directive/lot prouvés mais valeur/kind UNKNOWN sur condition, ancre du suffixe entier, négation brute conservée. V10 exige la phrase complète comme contexte, un seul sujet et une seule mention de lot. |
| `backend/app/modules/knowledge/application/candidate_retrieval.py` | Politique `rc-conditional-v10` intégrée aux trois projections (sélection, rescue, projection finale) et à l’intention v9 étendue ; activation des conditions uniquement pour v10. Source revalidée et retries inchangés. |
| `backend/app/modules/knowledge/domain/embedding_profile.py` | Nouvelle politique admise dans le contrat candidat. |
| `ops/retrieval-candidate/profile-v10.json` | Profil opt-in additif ; modèle/runtime/segmentation/seuil E5 inchangés. Aucun branchement au moteur actif/factory/API/UI. |
| `scripts/qualify_candidate_retrieval.py` | V10 ajouté aux gates/branches v9, **travail incomplet** : le validateur impératif exige encore REQUIRED/ASSERTION, donc doit être étendu avec tests rouges pour UNKNOWN conditionnel et gold indépendant des conditions. L’attente explicite des deux contrats d’intention n’est pas encore implémentée. |
| `backend/tests/application/test_rc_conditional_v10.py` | 17 nouveaux cas : numérotation, conditions/ancres/négation brute, refus ambiguïtés/multi-sujets/préambule/citation, revue/retry/invalidation. |
| `backend/app/modules/knowledge/application/rc_query_intent.py` | Inchangé par cette tranche ; v10 réutilise les formes étendues v9. |

Les profils v7/v8/v9 et le jeu13 historique sont inchangés. Aucun historique mesuré n’a été corrigé en place. Pas de nouveau gold matérialisé, pas de nouveau gel ni mesure E5/SQL v10.

## Gold contre-lu indépendamment, à matérialiser de façon additive

Revue technique indépendante par l’agent `review_rc_v9`, sans appel du moteur, modèle, DB ou édition. Son historique de conversation ne sera pas nécessaire si le tableau ci-dessous est suivi.

Pour la question `j12-missing-lot` du jeu13, six sources sont pertinentes même si l’extracteur ne sait pas les rappeler :

| Source suffixe UUID | Annotation | Lot | Valeur / kind | Span bytes UTF8 |
|---|---|---:|---|---|
| `2f47` | `c3` | 643 | REQUIRED / ASSERTION | `[0,31)` |
| `2f4b` | `c7` | 647 | NOT_REQUIRED / NEGATION | `[0,34)` |
| `2f4f` | nouvelle `c11` | 651 | UNKNOWN / UNKNOWN — interdiction de fournir, pas simple NOT_REQUIRED | `[0,32)` |
| `2f50` | `c12` | 652 | UNKNOWN / UNKNOWN — condition | `[0,35)` |
| `2f51` | `c13-DC2` | 653 | REQUIRED / ASSERTION — DC2 seul pertinent dans la coordination | `[0,35)` |
| `2f57` | `c19` | 659 | REQUIRED / ASSERTION — lot n° | `[0,37)` |

Exclure exemple non applicable2f4d, tenant étranger2f52, Affaire/version étrangères2f53, version remplacée2f54, extraction incomplète2f55 et autres sujets. Scope requête UNKNOWN, revue requise ; ces preuves ne deviennent pas applicables et ne créent pas une opposition entre lots.

**Six sources attendues dépassent top5** : ne pas corriger le moteur pour rendre artificiellement recall@5 complet. Expliciter le plafond5/6 et mesurer aussi@10, ou concevoir un nouveau jeu dont les budgets sont déclarés avant gel. Ne pas effacer cette distinction du rapport.

Pour `j12-hour` : legacy `expected_visit_subject="UNKNOWN"`, `expected_visit_anchor=null`; intention fermée `VISIT_SITE / DATE_TIME / UNSUPPORTED`. Ancres `[0,15)` demande, `[27,41)` sujet, `[50,57)` lot. Distinguer explicitement les deux attentes dans le nouveau banc ; ne pas dériver le gold de la sortie du moteur.

## Preuves exécutées et limites

- 17 cas rouges avant code : `~/.local/share/smartao-proofs/rc-conditional-v10-20261018/red.log`.
- Reprise vérifiée : **52 tests passent** (17v10 +35v9), `handoff-tests.log`.
- Ruff ciblé final vert : `handoff-ruff-final.log`. Deux défauts de style trouvés au contrôle ont été corrigés (imports et découpage de chaîne regex, sans changement de comportement).
- Mypy **636 sources**, zéro erreur : `handoff-mypy.log`.
- `git diff --check` vérifié.
- Dernière suite backend globale : **3236 réussites/2warnings sur v9**, antérieure au WIP v10. Elle **ne qualifie pas v10**. Dernier Semgrep v9 :0 finding / 0 erreur ; aucun scan v10 encore exécuté.
- Pas encore de tests CLI conditionnelle/deux contrats, tests SQL v10, revue du nouveau code, nouveau jeu gelé, mesure CPU/SQL, suite appropriée finale ou Semgrep v10.
- Aucun runner pytest/benchmark ni conteneur v10 actif à la préparation de cette reprise. Les bases/conteneurs v9 avaient été retirés. Aucune DB v10 créée.

Commande de revalidation pure depuis le checkout principal :

```bash
.venv/bin/pytest -q backend/tests/application/test_rc_conditional_v10.py backend/tests/application/test_rc_imperative_v9.py
```

Pour une future DB : PostgreSQL jetable explicite via SMART_AO_TEST_DATABASE_URL, données synthétiques uniquement ; l’environnement v9 qualifié utilisait réseau absent/socket Unix, tmpfs512MiB et WALmax64MiB/min32MiB/checkpoint30s pour éviter la saturation des migrations répétées. Ne pas utiliser le PostgreSQL local5432. Les recettes et états exacts sont dans les preuves v9 et `scripts/qualify_candidate_sql.py`.

## Travail restant, dans cet ordre

1. Matérialiser la correction de gold historique dans un artefact additif avec les six sources et les attentes des deux contrats ; conserver jeu13 et rapports historiques.
2. Tests rouges CLI : condition UNKNOWN avec ancres source et gold de condition indépendant, ancre manquante/déplacée/surcertitude refusée ; attentes legacy/fermé explicites. Corriger le minimum ; ne pas passer le gold au moteur.
3. Renforcer tests v10 pertinents (tenant/Affaire/version/private/financier, source changée, conditions et multi-sujets), SQL synthétique et revue indépendante ciblée.
4. Concevoir et contre-lire un nouveau gold sans utiliser le moteur, vérifier sa représentabilité SQL (pièces étrangères = version réellement distincte), geler code/profil/tests/gold, mesurer E5 CPU/SQL avec budgets/provenance/invalidation, sans réglage après mesure.
5. Contrôles du projet, sécurité après tests, nettoyage DB/containeurs, puis case/journal/prochaine étape/index et miroir Basic Memory.

## Conservation Git et sauvegarde

Preuves de cette tranche : `~/.local/share/smartao-proofs/rc-conditional-v10-20261018/` (copies avant, profils/historique préservés, rouges/verts et contrôles). Sauvegarde privée de tous les fichiers modifiés/non suivis non ignorés, état Git et manifestes : `~/.local/share/smartao-proofs/handoff-rc-v10-20261018/`. Le chemin exact de l’archive et son SHA sont enregistrés dans `backup-summary.json` et `SHA256SUMS`. L’archive est une copie de secours locale, pas un livrable ni un commit. Vérifier avant toute restauration ; la reprise normale utilise les fichiers déjà présents dans ce checkout.

A1nonadmis/A2génériqueHOLD/NO-GOpublic, DPGF non évaluable. Préserver tenant/Affaire/permissions/MFA/FINANCIAL_PRIVATE/PERSONAL_DATA, append-only/idempotence/provenance et UNKNOWN/REVIEW_REQUIRED. Aucun live/corpus réel/VPS/P3/déploiement/push/GOpublic.

Prochaine étape : ESSAIS DCE — reprendre la v10 locale en cours : matérialiser le gold sans lot contre-lu, expliciter les attentes legacy et intention fermée dans la CLI, valider les ancres conditionnelles UNKNOWN, puis qualifier sur un nouveau jeu gelé sans activer le candidat. Conserver v7/v8/v9, les demandes et sources multi-sujets non couvertes en UNKNOWN et DPGF non évaluable. A1 non admis, A2 générique HOLD et NO-GO public maintenus.


## Addendum de reprise exécutée — état ultérieur

Le point d’arrêt ci-dessus est historique et conservé. La reprise a exécuté les étapes CLI/gold/gel/SQL/contrôles :3267backend/90ciblés/5SQL verts ;v18 6/8positives et5gatesfausses,v10toujoursHOLD/nonactivée. Voir le [dossier v10 complété](../05_Qualification_locale/RC_CONDITIONS_GOLD_V10_2026-10-18.md) et le plan unique pour le statut courant. Preuves privées `~/.local/share/smartao-proofs/rc-v10-resume-20261018/`, dont brouillons14–17 archivés, gels, erreurs conservées et audit final ; bases jetables retirées,aucuncommit/push.

Prochaine étape : ESSAIS DCE — expliciter le contrat d’ancre de demande de visite, puis préparer une qualification RC hors templates connus; conserver les sources multi-sujets et conditions tronquées non couvertes en UNKNOWN, v7/v8/v9 et le candidat v10 non activé. DPGF non évaluable; A1 non admis, A2 générique HOLD et NO-GO public maintenus.
