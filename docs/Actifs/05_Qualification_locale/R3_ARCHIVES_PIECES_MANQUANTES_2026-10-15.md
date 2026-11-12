# R3 — Archives et pièces annoncées manquantes — 15 octobre 2026

## AS-IS
Lecture des pièces admises qualifiée; registres `DceDocumentIssueRecord` et `DceMissingDocumentDeclarationRecord` déjà présents. Le script privé d'essais inventorie les ZIP, le service applicatif ne le fait pas. Le staging non consommé est consultation-scoped, sans rattachement sûr à une version.

## Risques
Inventer un rattachement version/lot, promouvoir du contenu exclu dans RAG, confondre déclaration et absence vérifiée, perdre une archive partiellement inventoriée, fuite de noms/texte privés, bombes ZIP et traversées de chemin.

## Points d'insertion
Extraction déterministe, commande système existante et handler transactionnel, anomalies documentaires existantes, projection/contrat de couverture et panneau. Pas de nouveau droit, endpoint, migration ni dépendance. Les archives sont inventoriées, jamais décompressées sur disque ni admises automatiquement; leurs membres restent non extraits.

## Plan minimal et comportements à prouver
1. Tests rouges : ZIP imbriqué, doublons, chemin hostile, lien, chiffrement, corruption, budgets taille/entrées/profondeur, absence de fragments RAG.
2. Produire des métadonnées bornées et des ancres ordinales d'archives, liées à leur extraction exacte/hash original; enregistrer append-only avec la commande système et son replay.
3. Lire ces anomalies seulement pour l'extraction courante et la bonne version; intégrer les déclarations manquantes sans exposer raison/référence libre. Lot/criticité UNKNOWN, preuve de source UNKNOWN si la déclaration n'a pas d'ancre qualifiée.
4. Afficher les blocages dans la couverture existante, tests SQL/API/UI, suites adaptées, lint/types/build/Semgrep/revue, plan et miroir.

OpenDesign catalogue/contexte consultés en Local Codex. Conserver la surface et les classes existantes, autorité PF31-11/captures Owner; pas de nouvelle palette ni refonte. Impeccable craft-floor relu.

## État
CLOSE POUR LA QUALIFICATION TECHNIQUE LOCALE. A1 non admis, A2 HOLD, NO-GO public. Aucun corpus réel, VPS, push, P3 ou dépôt externe.

## Résultat d'implémentation
- ZIP et sous-archives : inventaire privé lié au hash original et à l'extraction `smart-ao-archive-inventory:1`, ancres ordinales (distinguant les doublons de noms), hashes des membres effectivement lus seulement. Chaque membre reste non admis/non extrait; aucun fragment RAG, aucune écriture disque de membre.
- L'extraction, ses anomalies et le reçu restent dans la transaction existante SYSTEM. Les commandes historiques sans inventaire conservent exactement leur sérialisation/hash d'idempotence; les ZIP utilisent une identité d'extracteur distincte, sans réécrire l'historique.
- Réutilisation de `DceDocumentIssueRecord` et `DceMissingDocumentDeclarationRecord`, aucun nouveau schéma/endpoint/droit. Les déclarations manquantes sont projetées comme déclarations, pas comme absences automatiquement vérifiées; leurs références libres ne deviennent pas des ancres qualifiées.
- Lecture tenant/version/extraction courante, contrôle croisé hash original/extraction/ancre. Historique conservé mais non courant. Lot et criticité UNKNOWN, source UNKNOWN en cas de preuve discordante. `analysis_complete=false`, `REVIEW_REQUIRED`, compte critique inconnu.
- Le panneau existant expose les constats et leur provenance structurelle, sans noms/texte/références libres privés. Les compteurs de documents restent ceux des pièces admises; les constats d'archive ne sont pas comptés comme documents admis.

## Bornes et revue de sécurité
16MiB source ZIP, budget de travail/expansion16MiB partagé dans l'arbre, membre8MiB,1000 entrées + au plus une sentinelle, profondeur3, répertoire central1MiB maximum avant allocation ZipInfo. La borne globale facture le maximum entre octets compressés lus et sortie réellement produite; en erreur de décodeur, toute la tentative est facturée faute de sortie observable. STORED et DEFLATE uniquement; autres compressions, chiffrement, liens, chemins hostiles, incohérences taille/CRC, EOCD/locatorZIP64, multi-disques et layouts non pris en charge sont explicitement exclus/illisibles/limités. Ces exclusions gardent le refus de complétude, pas un résultat vide réussi.

Revue indépendante : un P1 a montré que `ZipExtFile.read` peut décompresser avant de tronquer à une taille déclarée mensongère. Il est remplacé par lecture des octets compressés bornés et `zlib.decompressobj(...).decompress(...,budget+1)`, avec fin de flux, taille réelle et CRC contrôlés. Préflight du répertoire avant `ZipFile`; la divergence ZIP64 signalée en relecture statique est refusée explicitement. Régressions rouges observées puis vertes sur les trois méthodes8/12/14, allocation centrale, erreurs de décodeur et locatorZIP64. La relecture statique n'est pas un audit exhaustif ni une preuve de charge réelle.

Contrat de format vérifié sur [PKWARE APPNOTE6.3.10, §4.3.7/12/16](https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT); pas de copie de la spécification dans le dépôt. Bibliothèques standard installées examinées, aucune dépendance ajoutée.

## Preuves acquises avant la suite finale
- TDD :5cas initiaux rouges→verts;2cas bornes/ordinal bool rouges→verts;compatibilité hashlegacy rouge→verte;budget erreur rouge→vert;4cas décompression/allocation rouges→verts;locatorZIP64 rouge→vert. **16 tests purs inventaire**, **66 avec reader** verts.
- PostgreSQL extraction/lecture/routes ciblées : **98/98**,1warningStarlette,avant les derniers durcissements ZIP. Preuves finales nouvelles transaction/retry/historique/hash/source : **4/4**,10,33s,base secondaire isolée.
- Web global final : **544 réussis,4 ignorés,66 fichiers**,53,88s avec2workers. Premier run non borné :288réussis et21erreurs de démarrage de workers sous pression mémoire; ces21 fichiers n'étaient pas exécutés, pas21régressions produit. Aucun test/timeout modifié, concurrence du runner bornée pour la relance verte.
- Typecheck/lint/build verts; warning bundle>500kB conservé. Ruffglobal vert,mypyapp623sources vert,Impeccable0constat.
- ChromeDevToolsLocal, contexte isolé, composant réel avec props synthétiques : deux constats visibles, archive exclue et déclaration CCAP avec sourceUNKNOWN, détails ouverts/fermés au clavier,390/1440sansdébordement, constats retirés lors d'une lecture sans couverture.12requêtes de la dernière navigation uniquementloopback. Pas dePlaywrightMCP ni E2Eauth/API/backendlive. Harnais arrêté, onglet fermé; preuves horsGit `/home/noor/.local/share/smartao-proofs/r3b-20261015/`.
- Premier run backendglobal interrompu volontairement à224réussites pour intégrer le gardeZIP64 issu de revue; ce run n'est pas qualifié. Nouveau run global final en cours après l'ensemble des corrections, aucun PASS anticipé.

## Limites
Résultat synthétique local, pas inventaire exhaustif d'un DCE réel. ZIP64/multi-disques/compressions exclues et autres formats restent inconnus. Détection automatique des annonces dans RC, rapprochement présence/absence par lot, criticité métier et qualification des références libres non livrés par cette sous-tranche; UNKNOWN reste explicite. Aucun staging non consommé arbitrairement attribué à une version, aucune admission de membre, Golden DCE, effetP3, corpus réel, VPS, déploiement ou push. Capacité CPU/RAM sur corpus réel et licences déjà ouvertes demeurent non qualifiées.

## Fichiers et méthode
Production : `application/archive_inventory.py`, `commands.py`, `extraction.py`, `handlers.py`, `queries.py`; `infrastructure/case_dce_reading_reader.py`, `public/contracts.py`; `web/src/shared/types.ts`, `web/src/features/dce/DceKnowledgePanel.tsx`. Tests : `domain/dce/test_archive_inventory.py`, `application/test_dce_archive_coverage.py`, doubles reader existants et panneau.test.tsx. Documentation : présent dossier, index et plan.
Superpowers brainstorming/TDD et revue indépendante; ECC api-design/verification-loop et security-review dans la revue. Graphify consulté, Serena activée, mémoire lue comme miroir; OpenDesign Local Codex/catalogue courant et Impeccable, sans refonte ni nouvelle palette. Jev/Manus non nécessaires à cette projection déterministe et aux tests locaux; aucune décision humaine remplacée par un agent.

## Clôture technique locale — résultats finaux
- **Backend global2603/2603**,aucunignoré,exit0,**1362,04s(22min42)**;2warningsStarlette/httpx etPydanticField.alias(export_id). Tous les tests nouvellement ajoutés étaient collectés dans ce run final;les66purs et4SQL sont aussi verts séparément.
- **Web544réussites/4ignorés,66fichiers** avec2workers;typecheck/lint/build final verts,bundle704,83kB(avis>500kB). Aucun timeout/assertion modifié.
- Ruffglobalbackend/scripts,mypyapp623,format etdiffcheck verts;secrets ciblés sansnouvellealerte. Semgrep**1.179.0,p/security-audit,225règles/13fichiers,0finding/0erreur**;nouveauparseureffectivementscanné,aucunrésultatenvoyé;pasd'auditglobalexhaustif.
- Revue indépendante et ses points traités : lecture bornée/comptage réel/préflight central, puis refus explicite du locatorZIP64. Régressions rouges→vertes et relecture statique;pas de certification de sécurité ni qualification CPU/RAM sur corpus réel.
- Selfchecks reproductibles supplémentaires horsGit : `duplicate_entry_check.py` (deuxnomsidentiques,ancres/hashsdistincts,0fragmentRAG) et `api_exception_check.py` (HTTP200,exceptions sérialisées,source/lot/criticitéUNKNOWN,analyse_complete=false,aucuneréférenceprivée).
- Les13empreintescode qualifiées restentidentiques. Les deuxbasesjetables revenuesàAlembicbase(0ligne dansalembic_version),seulconteneur`smartao-r3b-proof-20261015`labelr3b-20261015arrêté/auto-supprimé;harnaisarrêté/ongletfermé. Aucunservice live touché.
- Index,case/journal/prochaineétape duplan actualisés;miroirBasicMemoryàsynchroniser. WIPpréservé,aucuncommit/push,déploiement,VPS,effetP3,corpus réel,admission ouGOpublic. Les étapesR3sontclosespourlecture/refuslocaux;inventaire exhaustifréel etanalyses complètes ne sontpasqualifiés.

Les sondes de dépassement de décompression sont bornées à un octet supplémentaire par tentative;les valeurs de budget sont des bornes techniques locales,pas un profil optimal qualifié sur DCE réels.

Prochaine étape unique : R4 — qualifier les annonces de pièces du RC et leur rapprochement avec l’inventaire courant par version/lot : ancres source/page exactes, négations et contradictions, omissions et faux positifs mesurés; conserver UNKNOWN sans déduire absence ou criticité du seul nom. A1 non admis, A2 générique HOLD et NO-GO public maintenus.

Miroir Basic Memory synchronisé après clôture, relu avec prochaine étape R4 exacte et résultats2603/2603. Le plan du dépôt reste l'autorité.
