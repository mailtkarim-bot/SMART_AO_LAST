# L05 — carte d'engagement et décision Patron

## Cadrage et plan minimal

AS-IS : le dossier L04 dispose des douze axes, extraits/ancres, actes de traitement, actions et liens contractuels exacts. La décision native gèle des références et conserve conditions/justification; son écran demande encore des UUID et du JSON, sa lecture n'expose pas les anciens cycles. Les hypothèses d'un traitement ne sont pas un champ distinct.

RISQUES : confondre projection et nouvelle vérité; perdre une hypothèse ou un lien; transférer une décision après rectificatif/nouvel acte; fuite FINANCIAL_PRIVATE; récursion entre conditions et dossier; retry créant un second acte; GO implicite.

POINTS D'INSERTION : projection decision réutilisant le dossier case; registre natif des actes d'analyse et contextes/décisions/conditions existants. Référence optionnelle typée ANALYSIS_ASSESSMENT vers un acte exact (révision et hash source), sans modifier les portes. La reprise du24/10 ajoute une association append-only condition↔acte : les liens contractuels existants ne couvraient pas les points techniques/risques. Les FK portent tenant/Affaire/décision/contexte/condition/acte exact; migration0142 statique avec refus de downgrade non vide.

PLAN :

1. TDD de projection des points et hypothèses explicites; ajouter une hypothèse facultative au traitement existant en préservant les sérialisations historiques sans hypothèse.
2. Valider la référence d'acte courant sans relire récursivement les conditions dérivées; qualifier changement de source/révision/tenant et refus avant décision. Lire carte et historique depuis un snapshot SQL cohérent, avec inconnus/troncatures explicites.
3. Après OpenDesign Local/Impeccable, restituer la carte dans le parcours Patron, fournir des sélections/formulaires structurés pour les actes natifs et conserver les IDs des résultats inconnus. Aucun JSON à inventer dans ce parcours.
4. Prouver une décision humaine motivée et conditionnelle, sources/actes/historique et refus; tests ciblés puis suites appropriées séquentielles, revue et scans. Mettre à jour plan/index/fiche/CSV et Basic Memory après la preuve complète.

TESTS : nominal, hypothèse absente UNKNOWN, sérialisation legacy, déduplication/axes, relations manquantes, source/lot/versions, rectificatif, nouvel acte humain, tenant/rôle/MFA/FINANCIAL_PRIVATE, concurrence/retry/UNKNOWN, historique, aucun prix/porte déduit. Qualification exclusivement synthétique locale; A1 non admis, A2 HOLD, NO-GO public, aucun push.


## Checkpoint du24/10 — codage et preuves intermédiaires

- Projection native Python/API/UI, hypothèses optionnelles legacy-compatibles et référence typée ANALYSIS_ASSESSMENT codées; carte12axes, extraits/sources/lot, actions déclarées/responsables/preuves/risque et liens de condition. Historique paginé par UUID opaque/date, relecture exacte du reçu hors20cycles et décision courante cherchée indépendamment du budget historique.
- Table `decision_condition_assessment_links` append-only, FK inter-Affaires interdites; head attendu0142. La migration préserve les actes existants et refuse de supprimer les nouveaux liens non vides. Aucun binaire ancien/deploiement qualifié.
- Revue/correctifs : source changée au gel409, portée financière contrôlée aux actes et aux reçus idempotents via attestation policy serveur, sources revalidées à résolution, cache invalidé aux frontières/écritures SQL et identités ORM rafraîchies, ancien cycle non proposé comme nouvelle décision; traitement historique complet rendu. Aucun nouveau droit ni règle de porte.
- Preuves intermédiaires :140backend ciblés/52Web+2ignorés avant derniers correctifs;22frontières backend puis33cœur ciblés (recouvrements); quatre tests cache finaux verts; anciens neuf tests de finalisation verts après correction de leur double sans aggregate_type (champ obligatoire du port natif). Web complet intermédiaire649+4ignorés vert; après dernier verrou frère/version,54Web ciblés+2ignorés verts. Pas de PASS global backend L05 encore.
- TDD réels conservés dans les journaux :22/source/capacité de réception, droits retirés/replay, références natives avant acte, session réutilisée, portéeORM, versionDCEdiscordante et contrôles Decision frères pendant UNKNOWN. Erreurs de fixture/import/DSN distinctes, non prises pour bugs produit; journaux initiaux conservés.
- Qualif BTP : une clause CCTP synthétique « maintenir les accès en site occupé; transport exclu de la fourniture », source/version/hash/région; hypothèse humaine de deux rotations et coût/dates encoreUNKNOWN. Ce n’est pas un devis partenaire réel ni une preuve de coût couvert.
- OpenDesign Local : catalogue et contexte existant consultés/reconfirmés le24, aucun Cloud/BYOK. Impeccable context/craft-floor consultés; détecteur final/navigateur/scans/suites finales à exécuter avant clôture.
- Principal HEAD30f2693/WIP préservé. Seul conteneur PG dédié `smartao-l04-acts-pg-20261020`, réseau none/TCPaucun, base `smartao_l05`; chaque runner utilise une DB dédiée et un `SMART_AO_TEST_DATABASE_URL` explicite. ACLUID70 temporaire sur socket privé à retirer à la fin. Aucun commit/push/live/corpus réel/P3/admission/activation/GO public.

Limites de parcours : aucune commande applicative native de remplacement d’une décision FINALIZED actuellement câblée; la carte ne l’invente pas et signale REVIEW_REQUIRED. Les contrôles détaillés et la résolution native existants restent disponibles, masqués pendant l’intention de carte non réconciliée. Budget de sources/historique explicite, aucun score opaque ni analyse complète déduit.


## Mesure navigateur et gel final du24/10

-17contrôles Chromium isolé via Chrome DevTools MCP réussis sur composants réels/API native in-process/PGsynthétique :12axes, source accès, absence de promotion de transport non matérialisé, saisie hypothèse, gel des inconnus, GO conditionnel explicite, lien restantOPEN, UNKNOWN/MFA/retry, résolution native explicite, révision de source, historique immuable et masquage Collaborateur. Aucun Playwright MCP ni backend live.
- Effets confirmés : une décision, un lien, une transition; zéro rapport financier et Affaire toujoursANALYSIS, outcome toujoursCONDITIONAL_GO. POST lien natifs201/403/200, corps/IDs identiques, aucunGET entre ces retries. Aucun cookie/Authorization/stockage navigateur. Réseau loopback uniquement. Captures390/1440 inspectées; page390px, tableau à défilement horizontal annoncé. WCAG exhaustif non qualifié.
- Limite métier constatée : dans le document synthétique, la phrase séparée sur le transport est lisible mais non matérialisée en exigence. Le point source couvre exactement la phrase accès. Le transport reste explicitement à confirmer/UNKNOWN, présent dans les inconnus du contexte; ni extraction exhaustive ni exclusion de devis partenaire prouvée. Ce manque moteur est conservé hors de la qualification de carte, sans modifier le jeu pour le cacher ni repartir dans L04 par défaut.
- Diagnostics du banc conservés : première fixture encore ancienne, puis sélecteur de label DOM incluant les options de select; pas des échecs du produit. Fixture neuve et scénario complet rejoués après correction. Aucun non-idempotent rejoué à l’aveugle.
- Web final652réussites/4ignorés préexistants/77fichiers/91,85s/exit0; types/lint/build verts. Semgrep1.179.0/225règles/31fichiers0finding0erreur après import type nommé, testsAPI et build revalidés. Premier scan partiel conservé, jamais utilisé comme PASS complet. Impeccable detect=[]; secrets0.
- Globale backend en cours : session26758, base neuve smartao_l05_global, journal privé backend-global-final.log. Ne pas lancer un autre global concurrent; attendre résultat et cleanup avant clôture. Navigateur, Vite et adaptateur de recette arrêtés.
- Transparence du gel :41fichiers dans code-sha256-final.json. Format final des tests et une ligne vide du vérificateur Python (AST identique) normalisés après collecte initiale; import de type TS effacé à runtime pour le parseur Semgrep. Aucun changement de logique de production. Deltas documentés dans format-only-test-delta.json et type-only-import-delta.json; tests concernés à revalider séparément après le global, sans confondre les snapshots.


## Reprise de la globale après contrat runbook

La première globale L05 (backend-global-final.log) a terminé3920réussites/1échec documentaire/1avertissement/1085,24s/exit1. Le seul échec venait du runbook préparatoire sans mention de0142. Le document a été complété, sans aucune opération VPS, puis ses contrats ciblés revalidés. Aucun échec fonctionnel dans cette campagne; ne pas la présenter comme globale verte.

Nouvelle globale complète : session86130, base neuve smartao_l05_final, journal privé backend-global-qualified.log. Les41SHA de code finaux sont stables. Attendre le résultat, puis vérifier les quatre bases L05 à Alembic0, arrêter le seul conteneur dédié, retirer ACLUID70/socket700, mettre à jour case/journal/next du plan puis Basic Memory. Aucun autre global concurrent, aucun commit/push.


## Revalidation aval Submission — 24/10

La deuxième globale complète a terminé :3921réussites/2avertissements/1335,91s/exit0 (`backend-global-qualified.log`). La revue des consommateurs avant clôture a ensuite reproduit un défaut fonctionnel distinct : après remplacement de l’acte d’analyse gelé, la porte Submission restaitREADY malgré la projectionREVIEW_REQUIRED. Test rouge PostgreSQL réel conservé dans `submission-source-red.log`; aucun export ni acte P5 exécuté.

Correctif minimal dans le lecteur SQL Submission : les références ANALYSIS_ASSESSMENT exactes sont revalidées par le vérificateur natif déjà utilisé pour décision/résolution. Une preuve périmée projette un contexteSTALE, refusé par la règle de porte existante; aucune mutation de décision, nouveau droit ou règle de porte. Test nominal courant puis acte remplacé,38ciblés verts et89contrats porte/architecture verts, mypy670 vert. Les anciens contextes sans ce type de référence restent compatibles.

Nouvelle globale finale en cours : session22250, base neuve `smartao_l05_gate_global`, journal `backend-global-gate-qualified.log`. Le manifest complémentaire `code-sha256-gate-final.json` couvre43fichiers; les41précédents restent inchangés. Pas de clôture avant résultat, scan final et nettoyage de cette reprise.

Contre-revue ciblée du lecteur aval : aucun défaut concret supplémentaire identifié; les consommateurs préparation/autorisation/export utilisent leur transaction existante et ne reçoivent aucun nouveau contenu financier. Le test neuf démontre le remplacement séquentiel, pas une course concurrente réelle; les tests du verrou/cache natif sont distincts. Semgrep1.179.0,225règles,2fichiers supplémentaires :0finding/0erreur; détection de secrets0. Le code reste gelé pendant la globale.


## Résultat final après revalidation Submission

L05 qualifiée localement : carte native douze axes Python/API/UI, hypothèses humaines optionnelles, actes exacts et liens condition↔preuve append-only0142, décision motivée et historique. Backend final après correctif aval : **3922 passed, 1 warning in 1161.97s (0:19:21)**, journal `backend-global-gate-qualified.log`; Web : 652 réussites et 4 ignorés préexistants,17 contrôles Chromium isolé synthétique via Chrome DevTools MCP. Source remplacée : rouge PostgreSQL réel puis refus Submission par contexteSTALE;38 ciblés / 89 contrats porte-architecture verts (recouvrants), mypy : 670 fichiers. Contrôles tenant/rôle/MFA/FINANCIAL_PRIVATE/replay/UNKNOWN/invalidation; aucune règle de porte ou confirmation modifiée. Semgrep 1.179.0 / 225 règles / 31 fichiers puis 2 supplémentaires :0 finding / 0 erreur; secrets : 0, Impeccable[].43 SHA-256 stables. Bases de la reprise vérifiées Alembic 0, conteneur dédié arrêté/networknone, ACL UID 70 retirée/socket 700; navigateur/Vite/adaptateur déjà clos. Aucun commit/push/live/VPS/corpus réel/P3/admission/activation/GO public.

Limites : L05 général reste PARTIAL; remplacement natif de FINALIZED non câblé, transport séparé non matérialisé UNKNOWN, authenticité des preuves externes et analyse automatique exhaustive non démontrées. Le nouveau test aval prouve le remplacement séquentiel; aucune course concurrente de ce scénario ni WCAG exhaustif revendiqués. A1 non admis / A2 HOLD / NO-GO public; DPGF hors RAG.

Méthode : Superpowers cadrage/plan/TDD/débogage/revue/vérification; ECC product-capability et verification-loop. OpenDesign Local Codex et Impeccable pour la direction/revue UI; Chrome DevTools MCP pour les17 contrôles, aucun Playwright MCP. Graphify consulté, graphe historique complété par le code courant. Les tests/scans locaux ne valent ni validation métier humaine, ni certification de sécurité, ni qualification live.

Suite du plan : L08 — livrer la rédaction et la revue sourcées des contributions de réponse acheteur dans les documents natifs : relier chaque contenu aux exigences et pièces exactes, rendre les manques visibles et qualifier le paquet produit, sans autorisation P5 ni dépôt automatiques.
