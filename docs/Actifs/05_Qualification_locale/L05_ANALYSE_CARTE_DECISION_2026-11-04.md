# L05 — dossier traité, carte d’engagement et décision Patron

Statut exclusivement dans le plan global ; preuves et limites bornées ci-dessous.

AS-IS : carte12axes, références exactes, création/gel/finalisation et liens de condition existent. Le gel exige une confirmation native DCE distincte du traitement d’analyse ; les références ANALYSIS_ASSESSMENT seules ne suffisent pas. Le cycle natif après changement de DCE existe ; la carte ne propose pas le brouillon après une décision finale à revoir. La lecture de carte n’est pas suspendue par l’incertitude d’admission.

RISQUES : recopier un accord ancien, finaliser sur un contexte remplacé, présenter une condition ouverte comme levée ou effectuer une lecture pendant UNKNOWN.

POINTS D’INSERTION : résolution des versions du contexte natif, carte existante et raccord App. Aucune nouvelle règle de finalisation, porte ou migration ; ne pas inventer une commande de substitution de FINALIZED.

PLAN MINIMAL : rouges sur scénario reçu/traité/gelé et nouveau cycle natif ; raccorder la confirmation native et préserver son refus au gel ; exposer une demande explicite de nouveau brouillon, refus serveur conservés ; suspendre la carte sous admission inconnue ; qualifier décision conditionnelle, lien exact et condition ouverte, motivation nouvelle sous V2, historique/refus/retry.

TESTS : contexte exact, acteur/tenant/MFA/droits, référence remplacée, cycle identique refusé, retry sans doublon, refus/UNKNOWN visibles, aucun accord/condition transféré ni GO automatique.

## Fonction livrée

La confirmation native d’exigence est distincte du traitement d’analyse. La carte expose l’acte existant sur le signal exact (extrait, ID, révision, DCE, document/hash), exige une confirmation explicite et conserve les IDs/corps lors d’un UNKNOWN. Le reçu vérifie type/identifiant de confirmation/révision et la relecture retrouve la référence DCE courante. Une confirmation qui invalide le traitement renvoie au dossier à retraiter ; elle ne vaut ni conformité, ni applicabilité automatique, ni analyse complète. Le lien vers le dossier est raccordé à la navigation App.

Le bouton de gel expose le garde natif déjà présent : exigence DCE confirmée et évaluation sourcée sont nécessaires. Le refus initial422 `DCE_REQUIREMENT_REFERENCE_REQUIRED` a été respecté, pas contourné. Une fois le dossier actualisé, création/gel/finalisation et lien de condition utilisent les services existants, motivations et consentements frais. La condition liée reste OPEN jusqu’à un acte de résolution distinct.

Une décision finale à revoir peut faire l’objet d’une demande explicite de nouveau brouillon, avec confirmation propre ; le serveur vérifie le changement de DCE et peut refuser409. Ce chemin utilise le CreateDecision natif qui marque le contexte ancien à revoir et ouvre un nouveau cycle ; il ne réécrit pas les références, motivations ou conditions finales et n’invente pas une commande de substitution. Aucun garde de finalisation ni porte modifié.

La carte est suspendue avant son Editor/GET pendant pending/busy d’admission ou pendant un intent d’analyse/dossier du même propriétaire/Affaire. Les corps privés restent dans les stores App en mémoire ; le pending de carte conserve son propre retry. Le rapprochement n’invente pas de source, impact, mandat ou preuve.

## Fichiers

Production : `web/src/features/decision/CommitmentCardPanel.tsx`, `commitmentTypes.ts`, `web/src/infrastructure/api.ts`, `web/src/app/App.tsx`. Tests de carte et nouveau `backend/tests/api/test_l05_received_commitment_decision.py`. Aucun backend de production, migration, dépendance, règle de porte ou candidat modifié. Les whitelists/fields de confirmation reprennent le contrat public existant.

## Preuves exécutées

Racine privée : `/home/noor/.local/share/smartao-proofs/l05-analysis-commitment-20261104/`.

- Backend **72 réussis /106,43 s** : nouveau parcours reçu, workflow/liens, snapshots/cache/portes de soumission, projection et routes natives. Nouveau parcours seul : **1 réussi /11,87 s** avant élargissement. Il reçoit réellement V1, confirme les signaux, traite/revoit le dossier, lit la carte12axes, crée/gèle/finalise sous condition, lie l’évaluation exacte et rejoue sans doublon. La condition reste OPEN, gate_effect=NONE et analysis_complete=False. V2 est un vrai rectificatif, avec confirmations/traitements/revues nouveaux, contexte ancien REVIEW_REQUIRED, nouveau cycle UNDECIDED sans condition héritée, puis NO_GO motivé. Historique/motivation/lien et ancienne condition OPEN conservés ; tentative d’un cycle sur même DCE refusée409.
- Frontend ciblé **11 réussis /2,09 s**, dont lecture sans décision automatique, cache/cas discordant, UNKNOWN stable, refus/requalification explicite, confirmation native et choix de la deuxième exigence exacte, retry avant GET. Rouges observés avant code pour suspension, demande de brouillon, confirmation et défaut d’identification de plusieurs signaux. La revue a trouvé cette ambiguïté : les sections affichent maintenant les sources/IDs explicites. L’ancienne fixture de gel ne listait pas l’exigence native pourtant nécessaire au serveur ; elle est alignée avec ce contrat, sans retirer les assertions de renouvellement de consentement.
- Navigateur : composants/client API de production, Chrome DevTools MCP isolé/headless, API/TestClient et PostgreSQL réels de fixture. Dossier traité confirmé préparé côté fixture ; création201 masquée503 puis retry200 avec corps/IDs identiques, aucun GET entre UNKNOWN et reçu ; gel, décision conditionnelle motivée, lien exact sans levée de condition ; réception V2 pilotée par le harnais via routes natives, demande de nouveau brouillon, nouveau gel et NO_GO distinct. Relecture/SQL final : deux cycles, ancien lien et condition OPEN, nouveau NO_GO ; aucun effet de porte. Le nouveau geste de confirmation est couvert par tests UI/protocole et API native, pas revendiqué comme nouveau parcours navigateur d’analyse amont déjà qualifié L04.
- Captures bureau1280 et mobile émulé393 inspectées ; table horizontalement défilante, contexte/historique/décision présents dans le DOM, aucun débordement de document. Les captures de viewport montrent principalement l’entrée de carte ; elles ne remplacent pas les assertions d’actes. Cookies/localStorage/sessionStorage vides, ressources de page externes absentes ; aucune garantie globale de trafic OS.
- Mypy app/tests : **206 diagnostics /40 fichiers /1266 sources**, identités normalisées identiques à L04, aucune nouvelle dette ;708 sources applicatives sans erreur. Types/lint/build vérifiés ; avertissements historiques setDecisionDossier et chunk>500kB. Ruff ciblé vert. Le global Web final et le scan final sont consignés après leur résultat.

## Limites, garanties et méthode

L05 général PARTIAL. Nouvelle réception à un point natif par version, autres axes non évalués ; pas d’exhaustivité automatique, coût/transport certain, authenticité de preuve externe, obligation juridique ou conformité déduite. La confirmation native ne remplace pas le traitement actualisé ; ses dépendances peuvent nécessiter des actes neufs.

Le nouveau brouillon est seulement demandé : même DCE ou contexte non éligible reste refusé par le serveur. La reprise qualifiée concerne le changement de DCE couvert par le service existant, pas toutes substitutions possibles de FINALIZED ou de portée. Les intents vivent en RAM et ne sont pas annoncés récupérables après reload/session perdue. Les lectures discordantes restent UNKNOWN/READ_REQUIRED. Aucune quantification automatique ou levée de condition par le lien.

Scanner/session MFA de fixture, traitements techniques et dossier amont pilotés localement ; aucune preuve de ClamAV réel, worker déployé ou authentification UI complète. Aucun Playwright MCP disponible. Les services native/gardes financiers/MFA n’ont pas été abaissés. La décision sous conditions est synthétique locale, aucun P3 réel ni dépôt externe. A1 non admis, A2 HOLD, B0/B1/B2/P0–P7 et NO-GO public conservés. Aucun live, corpus réel, VPS, commit, push ou effet externe.

Superpowers using-superpowers/brainstorming/writing-plans/TDD/requesting-code-review et ECC product-capability/verification-loop appliqués. Revue indépendante statique, aucune validation humaine déduite. OpenDesign Local : catalogue courant, artefact C08 et système consultés ; identité UI conservée. Impeccable craft-floor et détecteur borné sur la carte : aucun constat. Graphify avant navigation manuelle ; Basic Memory miroir du plan. Serena sans navigation sémantique, Context7 sans nouvelle bibliothèque/API externe à inférer, Jev/Manus/GitHub non nécessaires au travail local vérifiable.

Les deux bases propres sont revenues à0 table métier/0 version Alembic ; le seul conteneur `d8212625083042958af4815aef09a5953b7e8caa82726ac183f1f10c16dec106` (Mounts=[]) a été arrêté/supprimé. Preview/navigateurs propres fermés, services utilisateur préservés.

## Vérification finale du04/11

**92 fichiers Web réussis, 768 tests réussis /4 ignorés, 259,59 s** sur les six empreintes de code figées. Backend72/106,43s et carte11/2,09s précités. Semgrep1.183.0, `p/security-audit`, métriques désactivées, `--no-git-ignore` : **99 règles sur6 fichiers, 0 finding, 0 erreur** ; aucun envoi de résultats, pas de certification sécurité. Impeccable : aucun constat sur la carte. Types/lint/build/format ciblés et `git diff --check` verts ; revue du delta contre les copies WIP, aucun motif de secret ajouté détecté. Les diagnostics mypy206/40 sont identiques à L04.

La première hypothèse de manque sur la résolution ANALYSIS_ASSESSMENT seule n’a pas été retenue : le gel natif exige aussi une exigence DCE confirmée. Ce refus a été conservé, puis le scénario corrigé a prouvé le nouveau cycle déjà implémenté. Aucun backend ni garde n’a été modifié pour faire réussir la recette.
