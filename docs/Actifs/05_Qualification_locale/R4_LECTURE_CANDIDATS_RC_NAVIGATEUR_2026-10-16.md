# R4h — lecture des valeurs candidates RC et navigateur local — 16 octobre 2026

## Cadrage / plan minimal

AS-IS : R4g2839backend/123ciblés qualifié; candidats déjà présents dans le GET, non affichés. Checkout principal codex/reconcile-smartao-20261009, HEAD30f26934430095632000a1d82519f61dbb4c6411, WIP antérieur conservé. Risques : candidat assimilé à conformité/échéance applicable, source discordante, fuite après changement de contexte, réponses tardives, huit premières exigences seulement affichées.

Insertion : panneau `DceKnowledgePanel`, styles locaux existants et tests; hook/API existants réutilisés, sans changement d'autorisation, de confirmation ou de backend. Toutes les exigences de la projection doivent rester consultables. Champs séparés, date ISO sans conversion de fuseau, UNKNOWN visible, ancres avec version/pièce/extraction/hash et régions octet des valeurs. Pas d'acte métier.

- [x] Reprise Git/docs/Graphify/Serena/Basic Memory; cadrage Superpowers/ECC.
- [x] Consultation catalogue courant OpenDesign et contexte SMART AO existant, Local Codex choisi sans Cloud/BYOK. Transport MCP existant rétabli via daemon7456 sain et URL explicite, découverte sidecar périmée; aucune nouvelle installation. Aucun run/génération/prototype ajouté pour ce changement limité. Système confirmé : direction Owner Cytd PF31-11, composants du panneau actuel conservés; aucune refonte globale revendiquée. Catalogue et référence frontend-design lus via MCP, pas de système Cytd fourni dans le catalogue. Dette visuelle générale du panneau historique distincte de cette tranche.
- [x] Impeccable context exécuté une fois; panneau existant utilisé comme contexte, pas de PRODUCT/DESIGN/.impeccable créés. Références audit/craft-floor lues avant édition.
- [x] Régressions : cinq échecs initiaux observés pour affichage/provenance/identité/neuvième ligne; correction minimale puis45 tests panneau/hook verts. Un échec intermédiaire venait de la fixture partageant une ancre mutable; clonage de fixture corrigé sans relâcher le produit.
- [x] Qualifier le composant et le hook réels via API/session synthétiques, Chromium isolé et Chrome DevTools MCP (pas de Playwright MCP installé). Nominal, UNKNOWN, REVIEW_REQUIRED, source/version discordantes, 409, changements Affaire/session/rôle, retour au contexte et réponses hors ordre; vérifier absence de POST, cookies/token et trafic externe du parcours.
- [x] Audit visuel groupé desktop/mobile, detector Impeccable borné, corrections puis confirmation au plus une passe.
- [x] Suite Web entière, types/lint/build, revue indépendante, Semgrep après tests, diff/secrets; mettre à jour case/journal/unique prochaine étape puis Basic Memory.

A1 non admis, A2 générique HOLD et NO-GO public maintenus. Aucun corpus réel/backend live/VPS/déploiement/push/P3/GO public. Preuves privées `~/.local/share/smartao-proofs/r4h-20261016/`. Aucun commit.

## Résultats observés

### Code et TDD

Le panneau expose les pièces attendues candidates, date ISO citée, heure citée, fuseau explicite ou UNKNOWN, lots cités et applicabilité toujours UNKNOWN. Aucun calcul temporel ou validation de conformité. Les valeurs sont masquées si état UNKNOWN/REVIEW_REQUIRED, source non RC, source/fragment/version discordants, localisation non résolue, DCE non courant/admis/vérifié ou preuve absente. Chaque valeur affichée dispose de son champ/valeur/région octet. La provenance existante reçoit version/pièce/extraction; SHA source et fragment sont conservés. Une lecture de mauvaise Affaire masque tout le panneau; session/rôle et réponses tardives utilisent le hook existant inchangé. Le plafond silencieux de huit lignes a été supprimé.

Preuve initiale : 5 échecs observés/19 verts dans `panel-red.log`; après code et correction d'une fixture partageant son ancre mutable, **45 tests ciblés réussis** (24 panneau +21 hook). Les six refus de source et états critiques sont couverts; aucun bouton de confirmation/autorisation/export ajouté. Aucune modification du backend, contrat API, modèle, migration, dépendance ou règle de droits. La baseline R4g **2 839 backend** n'a pas été rejouée : les9empreintes R4g (backend/API/type) sont toujours identiques, ce n'est pas une nouvelle réussite backend R4h.

### Qualification navigateur synthétique

Fixture rejouable : `web/browser/rc-candidates/serve.mjs`, `index.html`, `checks.mjs`, README et `web/src/test/rcCandidatesBrowser.tsx`. Elle importe les composants/hook/client API réels et la CSS de production; configFile:false, aucun proxy backend, /api/* refusé, routes synthétiques GET seulement. CSP restreint les ressources au serveur local. Le profil Chrome DevTools Local utilise Chromium Helium `--isolated`; un contexte isolé propre R4h est créé sans connexion utilisateur. Aucun Playwright MCP dans cette session; cette preuve n'est pas un test Playwright.

**28 assertions navigateur réussies**, puis **28 réussies au rejeu depuis le script versionné**. Scénarios : nominal, UNKNOWN, REVIEW_REQUIRED, fragment/version/Affaire discordants, 404/409, changements Affaire/session/rôle et déconnexion, retour sans résurrection, réponse retardée après aller-retour, réponse ancienne arrivant après la nouvelle Affaire. Journal cumulé **35 lectures API synthétiques**, toutesGET et sans Authorization/Cookie; ressources du parcours de même origine, cookie/localStorage/sessionStorage vides. Le client réel conserve credentials:include : absence de cookies prouvée sur ce profil isolé, pas garantie générale ni preuve des autorisations serveur. Les erreurs console404/409 sont les refus synthétiques attendus, pas des défauts produit.

Mesures finales : **390×844 et1440×1000**, aucun débordement horizontal; `.rc-requirement-row` calculégrid et largeur des valeurs égale à celle de la ligne. Le premier contrôle mobile a révélé la compression par le badge; correction locale en une colonne, puis spécificité du sélecteur renforcée après mesure démontrant l'écrasement par la règle héritée. Les captures intermédiaires ne sont pas des confirmations. Captures/mesures finales `r4h-*-confirmation.png/json`; ouverture des régions au clavier Entrée vérifiée, cible44px. Inspection groupée desktop/mobile suivie de correction et contrôle borné; pas de boucle de polish ouverte.

### Impeccable et limites visuelles

Détecteur exécuté une fois : **4 constats préexistants**, aucun dans les nouveaux sélecteurs/JSX. Trois bordures d'accent ailleurs dans la CSS, police Inter globale. Ces dettes sont hors du delta; aucun renommage/refactoring ou changement de palette global introduit. Le panneau historique n'est donc pas revendiqué conforme à la refonte Cytd complète PF31-11. La consultation OpenDesign a confirmé l'autorité Owner et la réutilisation des composants pour ce changement limité; elle n'est ni une génération Local Codex ni une preuve d'un nouveau prototype. Aucun appel Cloud/BYOK.

Audit technique limité au delta : sémantique dl/section/details et clavier vérifiés, pas de dépendance/animation ajoutée, héritage du thème actuel; responsive mesuré. Scores bornés : accessibilité3/4 (pas d'audit WCAG exhaustif), performance3/4 (pas de benchmark très grand DCE), responsive3/4, thème2/4 (dette globale), intégrité3/4 =14/20. Ces scores ne certifient ni l'ensemble de l'application ni la direction visuelle cible.

### Vérification finale

Suite Web complète finale **558 réussites,4ignorés,66fichiers,91,02s,exit0** (`web-global-final.log`). Une première campagne propre à l'intégrateur est sortie143 sans résumé : non qualifiante. La revue indépendante a aussi exécuté558/4ignorés sans finding substantiel; cette preuve séparée ne remplace pas le log final de l'intégrateur. Typage client, lint et build verts; avertissement Vite de chunk>500kB et message jsdom de navigation conservés. Aucun test ignoré ajouté dans cette tranche.

Semgrep **1.179.0,225règles/7fichiers,0finding/0erreur JSON**, métriquesoff, aucune remontée distante; couverture JS/TS et règles multilang, CSS/HTML sans analyse sémantique complète, limites génériques du scanner conservées. Detect-secrets avec baseline :7fichiers,exit0. Diff whitespace et7SHA verts. Les fichiers déjà modifiés ne doivent pas être attribués intégralement à R4h : snapshot panneau privé pour isoler le delta. Revue indépendante sans modification : source/valeurs, hook, fixture sans proxy et absence d'effets examinés; aucun backend/DB/navigateur/Semgrep exécuté par le reviewer.

Superpowers cadrage/TDD/revue/vérification, ECC vérification/sécurité, OpenDesign et Impeccable utilisés. Graphify a orienté la lecture (~700tokens, graphe tronqué); code/tests actuels font autorité. Serena activé; Basic Memory utilisé comme miroir. Context7 Vite consulté pour createServer/configFile:false/middleware. Jev/Manus non nécessaires à cette évolution bornée, pas de fournisseur externe ajouté. Aucun VPS/corpus réel/backend live/P3/export/déploiement/commit/push/admission/GOpublic. WIP préexistant conservé.

## Clôture et reprise

Le serveur synthétique5179 et l’onglet isolé dédiés sont arrêtés; le journal final35GET sans bearer/cookie est écrit puis relu. Le daemon OpenDesign préexistant7456 est conservé; le démarrage temporaire17456 est arrêté, aucun second MCP installé. Plan/case/journal/index actualisés, Basic Memory synchronisé après le plan. HEAD30f26934430095632000a1d82519f61dbb4c6411 inchangé, WIP conservé, aucun commit/push.

Prochaine étape : ESSAIS DCE — qualifier séparément le retrieval et les embeddings sur un jeu BTP synthétique : tracer segmentation/index/sources, fixer budgets et seuils, comparer référence lexicale, BGE-M3 et multilingual-e5-small avec leurs prétraitements exacts; mesurer pertinence, omissions, RAM et temps sans fuite tenant ni source obsolète. Aucun remplacement avant preuve. A1 non admis, A2 générique HOLD et NO-GO public maintenus.
