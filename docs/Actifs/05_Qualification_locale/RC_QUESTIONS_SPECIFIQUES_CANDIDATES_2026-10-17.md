# Questions RC spécifiques candidates — 17 octobre 2026

## Cadrage et plan

AS-IS : v4 accepte un score dense>=0.85 malgré l'absence de preuve du qualificatif demandé; jeu5 médical faux candidat0.851169, sans rescue. Checkout principal HEAD30f2693/WIP conservé; index/plan/décision E5/CT2-083 relus.

Risques : mélange médical/chantier, négation/condition perdue, mot isolé pris pour preuve, rappel générique diminué. Correction bornée : politique v5 opt-in, type explicitement ancré dans une question d'obligation de visite médicale ou de chantier/site/locaux; clause exacte du type demandé avant sélection dense. Requêtes ambiguës/non couvertes avec qualificatif restent UNKNOWN. Questions génériques sans qualificatif gardent v4. Grammaire finie, pas de compréhension universelle des questions RC.

- [x] Tests rouges/verts types croisés, source négative, mention/condition non prouvée, portée lot/version et contexte de segment; trace des rejets et garde DPGF avant source/encodeur.
- [x] Coder intent et projection typée v5 facultative, identités v1–v4 inchangées, source/ancres/UNKNOWN et rappel générique conservés.
- [x] Revue indépendante, suite pertinente et gel jeu6 inédit avant mesure; gold indépendant des entrées extracteur/encodeur.
- [x] Mesurer E5CPU isolé sans réseau (CPU2/900MiB/600s), garder faux positifs/omissions sans réglage après résultat.
- [x] Vérifier lint/types/diff/secrets/Semgrep, retirer conteneur de preuve, actualiser plan/case/journal/index et Basic Memory.

Superpowers diagnostic/cadrage/plan/TDD/revue et ECC ai-regression-testing/verification-loop. Aucun moteur actif/API/UI/SQL/dépendance du projet/commit/push/live/corpus réel/VPS/P3/déploiement/GO public. A1nonadmis/A2HOLD.

## Implémentation et portée

`rc_specific_intent.py` fournit une intention NONE/CANDIDATE/UNKNOWN et une ancre de requête UTF8 : grammaire finie des questions d'obligation sur visite médicale ou chantier/site/locaux. Aucun SITE par défaut pour « visite ». Qualificatif ambigu, question horaire ou autre forme non couverte avec qualificatif : UNKNOWN, pas de type choisi par le modèle.

Le projecteur RC accepte facultativement les visites qualifiées (v5 uniquement), avec sujet VISIT_MEDICAL/VISIT_SITE. Les prédicats négatifs sont conservés. Le filtre v5 exige un sujet et une valeur documentaire reconnus dans la même clause et un lot compatible si la requête l'établit. Sans lot de source, une valeur documentaire reconnue reste de portée UNKNOWN; sans lot de requête aucun couple n'est promu. Types/clauses non rattachés sont conservés, hits sélectionnés et trace gardent leurs ancres exactes.

Le seuil dense0.85 est inchangé, rappel générique v4 conservé sur les questions couvertes. Une question spécifique ne reçoit pas de rescue sous seuil. Les clauses conditionnelles non reconnues ne sont pas admises par le filtre : limite mesurée ci-dessous, pas une preuve d'absence. Décisions SPECIFIC_MISMATCH/SPECIFIC_UNPROVEN/SPECIFIC_QUERY_UNKNOWN expliquent les rejets; réponse toujours UNKNOWN.

Revue : une citation de plusieurs phrases pouvait devenir une assertion après un point. Cinq rouges (guillemets français, courbes, ASCII et préfixe de segment) ont précédé le garde de citation. Une apostrophe typographique dans n’est fermait encore à tort une citation ‘…’ : rouge dédié puis traitement des apostrophes entre caractères alphanumériques. Citation fermée puis véritable clause négative reste lue. Contrôle du préfixe source exact dans rescue et projection finale. V1–v4 gardent les anciens modes et leurs identités historiques; aucun moteur actif, API/UI/SQL/dépendance du projet modifié.

## Vérification locale

36tests ajoutés :8intention,27service (dont paramètres sécurité),1CLI. Rouges initiaux17, puis mixité des types dans un fragment, visite non qualifiée, citations et apostrophe observés avant corrections. Un jeu CLI uniquement négatif avait un recallNone : refus de la preuve de rappel plutôt qu'un PASS fictif, couvert par régression. Suite pertinente **298réussites en1,92s**;Ruff backend/scripts,mypy633sources,format etdiff verts. Contre-revue indépendante100tests purs verts et anciens scénarios de citation refusés; pas de validation humaine métier ni de modèle rejoué par le reviewer.

Pas de backend global/Web ni nouvelle couverture : dernière globale2881/3avertissements antérieure aux politiques RC candidates; aucun changement DB/API/UI. Aucun PostgreSQL lancé. Semgrep1.179.0/225règles/10fichiers/0finding/0erreurJSON avec1warningfixpoint boto3hardcoded-token sur CLI (aucun appel/import boto3), limites conservées. Règles seules téléchargées, analyse locale, métriquesoff,aucunupload. Detect-secrets1.5.0 :3checksums publics identiques à v4 triés précisément;aucunplugin/filtre/ancienneentrée changé,0nouveau finding nontrié sur copie privée. Baseline canonique non indexée,aucunstaging;hook précommit non annoncé PASS.

## Jeu6 gelé / mesure réelle

Fixture btp_rc_specific_heldout_v6.json :19sources dont12éligibles/7exclues,17questions dont9positives/8cas attendus sans candidat. SHA4d6adb7f94c9fbbacc67b95c6b975f27685d85be507184f7c7727faac6aae541. Profil candidate-e5-v1:40655d6f039642514e8b2179599b227ba10f6989026ee246975d4e0244c6d7e3. Quinze empreintes figées avant mesure,inchangées après;gold hors extracteur/encodeur. Corpus synthétique nouveau après développement, pas une indépendance statistique ou une généralisation métier démontrée.

Même image CPU de preuve sha256:d7c4dcbc6bdbbbd5cc93f13c3d8453cbcc2993c8211d788238bcc67c28141938 et mêmes versions contrôlées que la campagnev4. Conteneur non privilégié sans réseau,CPU2/900MiB/swapnul/alarme600s,code/poids/paquetsreadonly,OMP/MKL/OpenBLAS2. Quatre répétitions stables,sortieexit0 etétat archivé,conteneur retiré;aucunserviceactif touché. Pas de comparaison directe de performance entre jeux.

| Mesure / gate | Résultat |
|---|---|
| Cas attendus sans candidat |0fauxcandidat/8, incluant ambiguïtés/refus; pas une preuve d'absence documentaire|
| Positives évaluables complètes@5 |6/8|
| Rappel documentaire brut@5 et@10 |0,666667, DPGF positive refusée comprise|
| Couple médical lot304 |1opposition exacte retrouvée|
| Rappel générique de référence |3sources par3rescues|
| Sous-seuil médical |6004=.841403,6005=.844465,non secourues|
| Condition médicale |6006=.900782,rejet SPECIFIC_UNPROVEN|
| DPGF/marge |refusées avant source/encodeur,non évaluables|
| Intention/type/portée/trace/ancres |PASS sur ce jeu|
| p95chaud / premier appel |22,769ms /14,921s|
| PicRSS / cgroup |887568KiB=866,77MiB /900MiBexact|

Quatre gates restent faux : evidence_recall_at_5,critical_complete,review_signals,rc_unknown_refusals. Les cas critiques manquants sont question médicale générale6004/6005,condition6006 etDPGF non lue. **Candidat HOLD/admitted=false**, aucun GO/admission/activation. Le refus conditionnel ne montre pas que la visite n'existe pas; il révèle le couplage conservateur entre preuve du type et valeur d'obligation. Jeu6 devenu historique, aucun ajustement de règle/seuil après résultat.

Recomptage indépendant :180entrées de trace source/segment/scope/classification et20contrôles d'ancres vérifiés,recall/fauxcandidats/couple/refus concordants. Pas de nouveau run modèle/runtime indépendant. Les51requêtes chaudes incluent des refus rapides;aucune marge mémoire d'exploitation démontrée sous plafond900MiB.

## Invariants et méthode

Tenant/Affaire/version/confidentialité filtrés avant encodage et trace,source modifiée refusée,retry stable,source/région/hash exacts;pas de mélange de types/lot dans les couples,conditions/citations/UNKNOWN et garde financier conservés. Aucun accès aux writers MFA/P3/append-only,aucun corpus réel/live/VPS/déploiement/commit/push. HEAD30f2693/WIP conservés,A1nonadmis/A2HOLD/NO-GOpublic.

Graphify orientation puis code vérifié (graphe tronqué),Serenaactivé,BasicMemorydécisionrelue/miroir;Superpowersdiagnostic/cadrage/plan/TDD/revue/vérification,ECCai-regression-testing/verification-loop. AucunSDKnouveau,Context7supplémentairenonnécessaire;Jev/Manusnonnécessairesauxrèglesbornées/revue;OpenDesign/Impeccable/navigateurnonapplicablessansUI. Preuvesprivées ~/.local/share/smartao-proofs/rc-specific-20261017/.

Prochaine étape : ESSAIS DCE — coder une preuve du type de visite indépendante de la valeur d’obligation, puis un rattrapage typé borné pour les sources sous seuil ou conditionnelles; conserver négations, citations, conditions et UNKNOWN, et requalifier précision et omissions sur un nouveau jeu synthétique gelé. DPGF reste non évaluable et le moteur actif inchangé. A1 non admis, A2 générique HOLD et NO-GO public maintenus.
