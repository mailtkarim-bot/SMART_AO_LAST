# L08 — contributions humaines sourcées et revue exacte

AS-IS : C10 dispose de plans versionnés, preuves entreprise relues par hash, brouillons Markdown immuables, corrections/revue exacte, transmission et manifeste. Le premier brouillon reste une trame sans saisie de contribution par exigence. L08 ne remplace ni ce registre ni ses portes.

RISQUES : texte assimilé à une couverture validée, confusion acheteur/entreprise/humain, source obsolète, fuite financière, mélange Affaire/session, retry avec contenu changé et transfert d'une ancienne revue.

POINTS D'INSERTION : commande/requête CreateTechnicalResponseDraft, assemblage document_content/review et wizard Collaborateur existant. Les contributions facultatives sont figées dans le Markdown canonique hashé du brouillon natif, avec exigence/section, source/version/ancres disponibles et preuves entreprise exactes; aucune nouvelle table ni dépendance. Les anciens appels sans contributions gardent leur trame. La revue continue à porter sur le SHA exact; une rédaction n'est pas une validation ni une couverture démontrée.

PLAN MINIMAL :

1. Contrats et assemblage en TDD : couples exigence/section exacts, doublons/hors-plan refusés, contenu humain et manques séparés, UNKNOWN sans inférence, limites et garde financière existants. Snapshot des sources résolues côté serveur dans le contenu.
2. Raccorder la saisie au wizard existant après OpenDesign Local/Impeccable : champs par exigence, manque explicite si vide, copie figée lors du POST, retry identique, remise à zéro/masquage après changement de contexte.
3. Qualifier HTTP/PostgreSQL synthétique jusqu'au brouillon relu/revu et paquet natif exact, refus/invalidation/historique. Aucun acte P5 ou dépôt automatique. Vérifier le contenu produit, pas seulement le hash.
4. Revue, suites appropriées complètes, types/lint/scan/diff puis mise à jour du plan/index/fiche/CSV et miroir Basic Memory. Ne pas clôturer sur la seule preuve d'un helper.

TESTS À AJOUTER : nominal et contribution partielle/absente; négation/condition conservées; attribution distincte; référence dupliquée/hors-plan; source/hash discordants; version remplacée; rôles/tenant; idempotence/concurrence; UNKNOWN et réponses tardives; aperçu et relecture Patron exacts. Source non lue ou portée absente reste UNKNOWN. Format natif Markdown qualifié uniquement, pas tous les cadres acheteur ni formats/signatures.

Contraintes : checkout principal/WIP conservés, aucun commit/push/live/VPS/corpus réel/P3/GO public; A1 non admis, A2 HOLD, DPGF hors RAG, candidats non activés. Le plan global garde l'unique statut L08.


## Code et preuves intermédiaires

- Contrat ResponseContribution facultatif ajouté à la commande/requête native, couples exigence/section stricts, texte et manque distincts, taille bornée, garde financière et sérialisation historique sans nouveau champ None. Les anciens brouillons restent des trames. Aucun schéma ni dépendance ajouté; head0142 conservé.
- Texte humain et sources acheteur/entreprise figés dans le Markdown hashé : extrait/ancres/révisions/hash et empreinte de portée, preuves exactes du plan. L'absence de portée lot reste UNKNOWN; aucune couverture ni signature déduite. Revalidation au moment de la revue/correction et dans le manifeste C10 consommé en aval par Submission.
- Verrous tenant/Affaire/exigences/documents/version NOWAIT : rouge PostgreSQL sans verrou d'exigence puis vert. Corrections d'une source UNKNOWN ne deviennent pas une preuve via un bool historique; un brouillon manquant peut être enregistré mais ne devient pas révisable sans source actuelle.
- Wizard existant : saisie par exigence, manque explicite si vide, corps figé à l'acte, retry scoped propriétaire/endpoint logique/Affaire/package/DCE/plan; aucune réponse tardive de POST/GET appliquée hors portée, séquencement des relectures. Contextes de saisie masqués immédiatement par clé de portée.
- TDD réels conservés : contrats/assemblage, garde financière, payload legacy, boolfalse/source UNKNOWN, verrou de confirmation, changement de fraîcheur, retry via autre connexion et relecture GET différée. Les premières erreurs de préparation de fixture/import/statut HTTP sont distinctes de ces régressions; elles n'établissent pas de bug produit.
- 19 natifs finaux verts : rédaction DC1/extrait source exact, SHA,201/200 sans doublon, revue Patron motivée, snapshot et manifeste exact, zéro autorisation P5; refus aval après obsolescence. 95 SQL/purs/architecture verts antérieurs recouvrants. Web intermédiaire654/4ignorés puis25ciblés verts après ajustement React conforme à la documentation Context7.
- Revue indépendante ciblée : verrou de confirmation, correction du manque et scopes du retry/GET traités. OpenDesign Local catalogue/contexte C10 relus, choix de raffinement `impeccable-design-polish`; conventions et CSS actuels préservés, aucune palette inventée ni Cloud. Impeccable context/craft-floor consultés, audit final à faire.
- Finale backend session26133 sur base neuve smartao_l08_global; Chromium natif in-process sur smartao_l08_browser, fixture bornée à une exigence de plan sélectionnée (les placeholders historiques du seed ne sont pas un corpus). Aucun backend live/TCP métier, corpus réel, P3, déploiement/push ou admission. Finir navigateur/suites/scans puis remettre les trois bases à Alembic0, arrêter le conteneur dédié et retirer ACLUID70.


## Contrôle final en cours et incident de ressources

La campagne Web simultanée a rapporté des délais/échecs alors que RAM et swap étaient saturés (7,6Go/5,8Go); elle a été interrompue et n’est pas qualifiante. Chromium initial a expiré avant preuve complète. Adaptateur arrêté proprement avec Alembic0, Vite et processus de recette arrêtés; aucun résultat de navigateur revendiqué. Les campagnes suivantes sont séquencées : backend complet session26133, puis Web seul, puis navigateur. Ne pas assimiler l’incident à une preuve de défaut produit ni masquer les échecs du runner : le replay doit trancher.

Revue finale ciblée : aucun défaut critique restant identifié après guards de POST/GET tardifs et séquence des relectures. Mypy671 et types/build verts; lint0erreur/1avertissementApp préexistant sur une dépendance d’effet. Neuf SHA backend gelés pendant sa suite;15code/tests au total dans le manifeste privé. Aucun changement de schéma, head0142. Synchronisation Basic Memory à reprendre après son transport interrompu pendant la saturation; le présent dossier et le plan conservent la reprise, aucun statut perdu.

Limites métier : format natif Markdown et snapshot interne qualifiés sur un jeu synthétique borné; pas de remplissage universel de cadres acheteur DOCX/PDF, d’authenticité des preuves externes, de signature obtenue, d’analyse complète ou de dépôt. La validation d’un texte n’efface pas un manque déclaré; ni coût ni engagement contractuel créé automatiquement.


## Dernière frontière de portée

La contre-revue a confirmé qu’un couple contribution hors plan atteignait le lecteur avant le refus. Régression HTTP rouge avec lecteur interdit : `An out-of-plan contribution must not touch source records`. La validation de l’ensemble exact des couples et des doublons est désormais exécutée avant le snapshot SQL; refus RESPONSE_PLAN_MISMATCH sans accès aux références fournies hors plan.95 SQL/purs/architecture verts après le correctif. Aucun oracle inter-Affaires reproduit dynamiquement; le test prouve l’absence de lecture sur cette entrée.

La première globale backend a été interrompue proprement avant ce garde final :2720réussites/1warning/2034,24s, aucune globale verte déduite. Son coût a inclus la saturation précédente. La recette navigateur est reprise seule après cleanup initial : adaptateur natif5104, Vite56759, Chrome DevTools33615/page2; base smartao_l08_browser, aucun global concurrent. Finir puis fermer ces processus, rejouer Web seul, scanner et lancer une nouvelle globale backend sur base neuve. Les logs initiaux sont conservés, pas remplacés par une affirmation de succès.

Basic Memory : le CLI local configuré `basic-memory-codex` (uvloop déjà installé) a permis la relecture exacte de la note; utiliser ce lanceur existant pour la synchronisation finale après l’incident du transport MCP, sans installer un autre serveur.


## Recette native et gel final

22 contrôles Chromium isolés via Chrome DevTools MCP réussis : création d’une contribution DC1 avec manque de signature, masquage immédiat du texte au changement de session, verrouillage UNKNOWN,201→200 avec mêmes corps/IDs et aucun GET entre les retries, relecture exacte du SHA dans le navigateur, demande et décision de revue Patron, sources figées lisibles et octets natifs conservés, snapshot exact puis refus422 après obsolescence. Une exigence courante de plan sélectionnée; les placeholders historiques du seed ne qualifient pas un corpus. Un brouillon/deux révisions de revue/un snapshot/P5zéro; Affaire toujoursANALYSIS. Aucune pièce DC1 réelle ni adéquation sémantique de tous les justificatifs déduite du texte humain ou du hash des preuves reliées.

390/1440px sans débordement racine, captures inspectées. Les captures ont été obtenues par la sortie image en mémoire documentée du MCP puis conservées dans les preuves privées; le transport de fichier MCP sans racines configurées refusait les chemins, aucune racine globale changée. Un profil de fixture sans lecture/readiness a d’abord reçu403 : droits synthétiques de lecture ajoutés, pas de modification de permission produit. Aucun cookie/jeton navigateur,75requêtes loopback; captures PNG et transcript natif conservés. Une note de revue est maintenant accessible par aria-label; le lecteur de contenu gère aussi NULL en UNKNOWN, prouvé par régression rouge/verte.

Web final659réussites/4ignorés/78fichiers/103,12s/exit0;33ciblés verts. Mypy671/types/build etRuff/format verts; lint0erreur/1avertissementApp préexistant, bundle>500kB signalé sans requalification performance. Semgrep1.182.1 (outils locaux mis à jour pendant la session),99règles/19fichiers,0finding/0erreur; secrets0, Impeccable engine0.1.5 detect=[]. Aucun résultat de scan envoyé.19SHA finaux dans code-sha256-final.json.

Navigateur33615 fermé/exit0, adaptateur5104 fermé/exit0 avec base navigateur Alembic0, Vite arrêté. Trois bases antérieures àAlembic0 vérifiées puis cluster jetable redémarré pour une base finale neuve smartao_l08_final. **Globale backend finale session6391 active**, journal backend-global-qualified.log. Ne rien modifier dans le code gelé ni lancer un autre global; attendre résultat etcleanup avant clôture. Décision technique mémorisée localement dans Basic Memory0.24.1 : `smart-ao-v8/codex/decisions/l08-contributions-humaines-et-provenance-native-2026-10-24`, statutopen distinct d’une porte ou validation Owner. Le miroir de plan sera synchronisé après qualification.


## Résultat final et limites

La rédaction et la revue sourcées de contributions sont livrées dans les documents natifs : commande/requête facultative typée, couples exigence/section vérifiés avant lecture de leurs références, contenu humain et manques distincts, sources acheteur/entreprise et portée figées dans le Markdown hashé. La revue, les corrections et le manifeste C10 consommé en aval revalident les sources sous verrous; aucun bool historique ne remplace cette preuve. Payload legacy sans nouveau champ None conservé. Aucun schéma ni dépendance ajouté; head0142 inchangé.

Le wizard conserve le texte/IDs d’une intention et bloque les envois et retours tardifs hors propriétaire/connexion logique/Affaire/package/DCE/plan; UNKNOWN et retry identique. Le lecteur Patron sépare rédaction/manques et sources figées sans modifier les octets; contenu natif et SHA restent consultables. Le contenu non disponible et les références non interprétables restent UNKNOWN.

**Backend final : 3932 passed, 2 warnings in 1193.13s (0:19:53), exit0**, journal `backend-global-qualified.log`. Web final :659 réussites,4 ignorés préexistants,78 fichiers,103,12s.95 SQL/purs/architecture et19 natifs antérieurs recouvrants;33 UI ciblés. Les régressions rouges couvrent source obsolète, verrou de confirmation, correction sur source UNKNOWN, lecture hors plan interdite, retry via autre connexion et GET tardif. Revue indépendante ciblée sans défaut critique restant après correction. Mypy671,types/lint/build/Ruff/format/diff vérifiés; un avertissement App préexistant de dépendance d’effet et un avertissement de taille de bundle restent visibles.

**Chromium isolé via Chrome DevTools MCP :22 contrôles**, composants réels/API in-process/PG synthétique. Une exigence courante sélectionnée, rédaction DC1 et manque de signature; huit contrôles saisie/UNKNOWN/retry/scope, relecture et décision Patron explicites, SHA exact recalculé dans le navigateur, snapshot natif exact puis refus422 après source devenue obsolète. Effets :un brouillon/deux révisions de revue/un snapshot/zéro P5, Affaire toujoursANALYSIS.201→200 sur le brouillon après reçu perdu, corps/IDs identiques, aucun GET entre les retries; aucun cookie/token navigateur, réseau loopback uniquement.390/1440px sans débordement racine, captures inspectées. Identité des preuves ≠ adéquation de tous les livrables.

Semgrep 1.182.1,99 règles/19 fichiers :0 finding/0 erreur; aucun résultat envoyé à un service. Secrets0, Impeccable engine0.1.5 detect=[].19 SHA finaux stables; conteneur dédié arrêté après vérification Alembic0, ACLUID70 retirée/socket700; navigateur/Vite/adaptateur clos. Les trois bases antérieures avaient été vérifiées Alembic0 avant redémarrage du cluster jetable, puis la base finale a été contrôlée de même. Aucun commit/push/live/VPS/corpus réel/P3/admission/activation/GO public.

Limites : L08 général reste PARTIAL. Cette preuve porte sur contributions humaines dans un brouillon Markdown et snapshot internes; aucun pli acheteur complet, cadre DOCX/PDF universel, signature obtenue, pièce tierce adéquate ou couverture exhaustive déduits. Aucun export ZIP/P5 réalisé dans cette recette nouvelle; les preuves C10 antérieures gardent leur périmètre. Un texte validé ne devient pas une preuve de fourniture de chaque pièce. A1 non admis/A2HOLD/NO-GO public; DPGF hors RAG et moteurs candidats inchangés. WCAG exhaustif et qualification live non exécutés.

Les campagnes interrompues restent documentées : Web avec délais/échecs pendant saturation RAM+swap, Chromium initial non qualifié, backend initial interrompu proprement à2720réussites avant le dernier garde. Seules les finales séquentielles ci-dessus fondent cette clôture locale.

Méthode : Superpowers cadrage/plan/TDD/débogage/revue/vérification, ECC product-capability et verification-loop; Graphify historique consulté puis code courant, Serena activé. OpenDesign Local catalogue/contexte C10 et conventions existantes, Impeccable context/craft-floor/polish/detect; Context7 React19.2.8. Basic Memory local via lanceur uvloop configuré, version0.24.1. Jev/Manus non utilisés : aucune classification ou enquête externe nécessaire pour ce parcours déterministe local. Aucun Playwright MCP, Chrome DevTools MCP utilisé. Pas de certification de sécurité ni d’accessibilité exhaustive.

Suite exacte du plan : L09 — livrer le rapprochement sourcé de l’offre vendue avec le contrat attribué et le dossier de passation au conducteur : conserver engagements, exclusions, écarts, conditions et actions, avec inconnus et confidentialité explicites, sans déduire réception externe ni effet juridique.


## L08 — 25/10 — complément de récupération du reçu tardif qualifié

Régression rouge : après POST en vol A→B, réponse ignorée puis retour A, SUBMITTING empêchait le retry. Une métadonnée incertaine reste désormais attachée à la portée d’origine; le retour dans cette portée restitue UNKNOWN et permet le même acte, sans nouveau corps ni identifiant. Le marqueur est masqué ailleurs et retiré pendant le nouvel envoi.34ciblés, types/lint/build et Web complet660réussites/4ignorés/78fichiers/248,50s/exit0; contre-revue sans nouveau défaut concret.

Correctif limité à deux fichiers Web; les neuf Python restent identiques à la globale backend3932/2warnings/1193,13s/exit0. Les22contrôles Chromium du parcours natif restent une preuve bornée de leurs chemins; la nouvelle course différée est qualifiée par test de promesse. Semgrep1.182.1/22règles/2fichiers supplémentaires0finding0erreur, secrets0. Delta et19SHA finaux conservés; aucune nouvelle base ni action métier exécutée pour ce complément. Cleanup précédent toujours valable. A1nonadmis/A2HOLD/NO-GO public, DPGFhorsRAG, candidats inchangés. Aucun commit/push/live/VPS/P3/GOpublic.

Statut final et suite : plan du dépôt seul.
