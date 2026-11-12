# L09 — pli reconstruit et passation au conducteur — clôture du 30 octobre 2026

**Verdict : continuité locale V1/V2 qualifiée, avec manques et reports. L09 général reste PARTIAL.** Démarrée le29octobre, campagne close le30octobre. Ni attribution/contrat authentifiés, ni complétude ou effet externe déduits.

Le plan reste seul statut. Checkout principal, branche et HEAD inchangés;662 empreintes WIP vérifiées avant modification. Aucun reset/clean/stash, checkout, stage, commit ou push.

**AS-IS :** L08 reconstruit V1/V2 sur une même Affaire; L09 publie une revue offre/contrat et un reçu exact du Responsable. Le parcours combiné n'est pas qualifié; la sélection de P5 semble accepter une version DCE antérieure si son autorisation reste historique.

**RISQUES :** republier V1 sous contexte V2, hériter de textes/conditions/reçus, transmettre un autre document que les octets P5, présenter un contrat déclaré comme authentifié, divulguer des éléments financiers ou masquer les manques du dossier.

**POINTS D'INSERTION :** tests de passation et hooks de recette L08; si reproduit, garde de version source dans sélection/publication natives, sans nouvelle porte ni modification P5/P7. Aucun schéma SQL, nouvelle page ou nouvelle porte.

**PLAN MINIMAL :**

- [x] TDD : P5 V1 ne doit pas être sélectionnable ni republiable sous DCE V2 connu; refus sans effet. Correction minimale si les tests reproduisent le défaut.
- [x] Recette native Markdown/DOCX : passation/reçu V1, rectificatif natif et pli V2, V1 historique et refus de réutilisation, nouvelle revue et nouveau reçu V2. Engagements/extraits exacts, actions/responsables/preuves et manques visibles.
- [x] Relecture Conducteur des octets du mémoire exact contre ZIP; P5/hash/versions et contrôles de confidentialité conservés. Pas de ZIP complet ni données économiques au Conducteur.
- [x] Régressions ciblées DB/API/Web, revue indépendante, types/lint/Semgrep/diff et navigateur sur interface existante si utile. Les globales restent des preuves datées; aucune réattribution automatique.
- [x] Bilan borné, sauvegardes et archives relues; plan/index/registre et miroir Basic Memory actualisés et relus.

Autorités : PF2-081, M2-083, CT31-14. Méthode Superpowers executing-plans/TDD/systematic-debugging et ECC security-review/verification-loop; Graphify consulté et Serena activé. Pas d'OpenDesign/Impeccable tant qu'aucune interface n'est modifiée.

Toutes les déclarations et actes sont synthétiques. P7/reçu ne valent ni OS, acceptation juridique, signature du contrat, conformité du pli ni dépôt externe. Le bilan L08 (42–44 signaux sans réponse dans ses fixtures) et ses reports restent ouverts; aucun accord réel n'est inféré.

## Élargissement nécessaire après les rouges

La recette Markdown est passée avec deux passations/reçus V1/V2. Le DOCX a révélé une rupture de preuve : `unique_excerpt_offsets` cherchait une chaîne UTF-8 dans les octets ZIP compressés. Aucun faux match n'était produit, mais l'extrait restait UNKNOWN malgré sa présence. La correction réutilise le parseur OOXML borné de Préparation, uniquement sur les paragraphes du corps `word/document.xml`. Elle conserve source DOCX/hash/version, hash de partie XML, locator XPath et offsets UTF-8 de paragraphe; les offsets de fichier binaire restent nuls et l'état distinct `EXACT_DOCX_TEXT_MATCH`. Duplications, en-tête seul, paragraphe caché/structure non prise en charge, texte entre paragraphes et package invalide restent UNKNOWN/AMBIGUOUS. Le DOCX fermé n'est ni regénéré autrement, ni réécrit; les anciennes publications ne sont pas promues rétroactivement.

Huit tests purs ajoutés après rouge,15ciblés purs verts à ce stade. Le lecteur existant doit rendre la provenance lisible; catalogue OpenDesign et artefact natif C08 de rapprochement, système `linear-app` consultés en local via SDK/MCP existant après transport de session fermé. Aucun Cloud/BYOK/prototype nouveau; Owner CYTD et styles existants conservés. Impeccable context de la session réutilisé, craft-floor relu avant édition; aucun PRODUCT/DESIGN/hook ajouté.

## Fonction livrée

Deux rouges PostgreSQL ont reproduit l'ancien pli proposé et republié sous un DCE différent connu. La sélection filtre maintenant cette incohérence, et le handler refuse `HANDOVER_OFFER_VERSION_CONFLICT` sous le verrou Case partagé avec l'adoption DCE. L'API409 existante est réutilisée; les acteurs, permissions, P5 et portes P0–P7 restent inchangés. Le cas legacy sans DCE applicable connu conserve son contrat; aucun courant n'est inféré d'une version absente. Une lecture d'options concurrente peut être ancienne; la publication revalide la source dans la transaction.

La seconde correction raccorde les engagements DOCX à leur texte source réel. Les offsets ZIP demeurent nuls; `EXACT_DOCX_TEXT_MATCH` porte locator XPath dans `word/document.xml`, hash de partie XML, hash de texte du paragraphe et plage UTF-8. Le document entier est d'abord vérifié contre le hash du P5. Seuls paragraphes directs du corps et paragraphes directs de cellules de tables simples sont admis; aucun rapprochement entre paragraphes, en-têtes, tables fusionnées/imbriquées ou contrôles de contenu. Tout marquage `vanish/webHidden` direct ou dans styles.xml rend la preuve UNKNOWN, même si un style masqué est inutilisé ou `vanish=false`. C'est un refus conservateur, pas une interprétation de styles ou une certification de rendu.

Une revue indépendante a reproduit deux P2 dans la première version du lecteur DOCX : conteneur complexe et style hérité masqué. Trois nouveaux rouges (contrôle de contenu, style masqué et docDefaults) puis verts ont borné les chemins et styles. Contre-relecture statique : ces deux défauts sont corrigés, aucun nouveau défaut concret confirmé; le relecteur n'a exécuté aucun test. Les anciens snapshots et reçus ne sont pas recalculés ou promus rétroactivement; seules de nouvelles publications explicites créent ces preuves. Les contrôles de reçu n'ont pas changé; les manques critiques imposent toujours un reçu avec manques.

Le lecteur Conducteur affiche le locator, le hash XML et la plage de paragraphe, en précisant qu'il ne s'agit pas d'offsets ZIP. Le test DOM a été rouge avant cette ligne, puis vert. Types nouveaux facultatifs, aucun nouveau style/CSS/palette, aucune nouvelle dépendance ou migration. Contrat seulement déclaré, autorité/file SHA inconnus, P7≠OS conservés.

## Bilan des deux variantes et quatre passations

| Variante | Révision | État source | Preuves de points | Manques explicites | Mémoire remis, octets |
|---|---:|---|---|---:|---:|
| markdown | 1 | CURRENT | 1 EXACT_BYTE_MATCH, 1 UNKNOWN | 6 | 5011 |
| markdown | 2 | CURRENT | 1 EXACT_BYTE_MATCH, 1 UNKNOWN | 8 | 5068 |
| docx | 1 | CURRENT | 1 EXACT_DOCX_TEXT_MATCH, 1 UNKNOWN | 6 | 37017 |
| docx | 2 | CURRENT | 1 EXACT_DOCX_TEXT_MATCH, 1 UNKNOWN | 8 | 37021 |

Chaque variante conserve une Affaire entre ses générations; les variantes correspondent à deux Affaires indépendantes. V1 possède une passation/reçu propres. Après rectificatif, V1 devient REVIEW_REQUIRED puis HISTORICAL après V2; son reçu reste historique. V2 possède un autre snapshot, une autre revue explicite et un autre reçu; l'attribution WON synthétique du même lot est **explicitement** resélectionnée, pas recréée ou authentifiée par le test. Une version contractuelle déclarée distincte est sélectionnée pour chaque publication; cela ne prouve ni remplacement légal ni signature.

Le point d'engagement a une source exacte dans le mémoire; un point de condition conserve ses sources/responsabilités/preuves non prouvées UNKNOWN. La revue V2 laisse volontairement responsable et preuve attendue absents; les valeurs V1 ne sont pas héritées. `RECEIVED` est refusé422, ancien hash/vue409, nouvelle publication sur l'ancien P5 sous DCE V2 refusée409 sans événement/outbox. Le reçu `RECEIVED_WITH_GAPS` est créé et rejoué sans second effet; deux snapshots et deux reçus par Affaire sont vérifiés. Le téléchargement natif du Responsable est byte-identique au membre technique de son ZIP, pas au ZIP entier.

Les6/8manques comprennent responsabilité, locator d'offre, action, preuve attendue, extrait non prouvé et locator contractuel de la condition; V2 ajoute les deux manques délibérés sur l'engagement. Aucune ligne critique n'est réputée complète par présence d'un reçu. Les42–44signaux laissés sans réponse dans le corpus L08 et tous ses reports ne sont pas levés par cette qualification L09.

## Preuves exécutées et leurs limites

- Rouge de source V1/V2 : **2échecs attendus/6,30s**, ancien choix et publication201. Après garde : **27tests opérationnels réussis/20,35s**.
- Campagne de régression après ajout DOCX : **49réussites,1avertissement,127,99s,exit0** : P7 HTTP exact/append-only/confidentialité, reçus, vues, tamper, contrat, services et premières preuves DOCX. **85tests d'architecture réussis/7,12s**.
- Les derniers refus DOCX de contre-revue sont vérifiés par **18tests purs réussis/2,13s** (11nouveaux et7existants). Ces nombres recouvrent une partie des campagnes précédentes; pas de total additionné.
- Recette intégrée : **2variantes réussies,1avertissement,479,96s,exit0**. Après les trois rouges de contre-revue, **DOCX seul rejoué sur code final :1réussite/196,84s/exit0**. Le résultat initial n'est pas attribué silencieusement au code resserré. Les quatre mémoires finaux sont relus indépendamment contre les ZIP et proofs; Markdown garde son chemin byte-identique, DOCX a une qualification native finale et une vérification XML indépendante.
- Premier rejeu de fixture422 : `correlation_id` non admis par la requête de version contractuelle. Seule la requête de test a été corrigée, aucun schéma API assoupli. Rouge DOCX initial `UNKNOWN != EXACT_BYTE_MATCH` conservé avant correction. Les échecs et reçus de chaque campagne restent privés, aucun run incomplet compté PASS.
- Web ciblé : **11réussites/8,67s**, puis globale **722réussites,4ignorés,90fichiers/343,07s,exit0**. Types/lint/build exécutés, seul warning App.tsx:517 préexistant et chunk904,16kB (>500kB); aucun seuil relevé. L'avertissement jsdom de navigation n'est pas présenté comme test navigateur.
- Mypy application703sources vertes; app/tests206diagnostics40fichiers/1244sources, identités inchangées contre le snapshot antérieur. Aucun ignore ajouté; les trois premiers diagnostics de test (clé point_id nullable) puis annotation de liste ont été corrigés. Typage global de CI non qualifié.
- Ruff/check/format8Python verts; Alembic unique20261027_0146 inchangé, pas de migration ajoutée. Fixtures sur PostgreSQL jetable exercent upgrade/downgrade et rollback; après tests les deux bases ont0table métier/0révision.
- Semgrep1.182.1 `p/security-audit`,99règles/11fichiers/0finding/0erreur, métriques désactivées, analyse locale. Motifs stricts de secrets11sources :0candidat; ce sont des contrôles bornés, pas une certification.

## Relecture navigateur et indépendance des preuves

Chrome DevTools Local, contexte isolé : renderer **HandoverSnapshotRead** existant, rapports et binaires sauvegardés des API natives, pas backend live. Séquence Markdown V1→historique→V2, puis DOCX V2; empreintes, états, manques/non-héritage et locator XML lisibles. Viewports1280/393px sans débordement, corps14px hérité; pas de refonte ni audit WCAG complet. Téléchargement du binaire enregistré vérifié par SHA côté navigateur. Aucun POST de publication/reçu dans ce harnais : ces actes sont prouvés séparément par les tests HTTP natifs. Zéro cookie/token/stockage local ou destination externe, onglet/preview dédiés fermés. Pas Playwright ni capture disque revendiqués.

`qualified-handovers.json` conserve snapshots/révisions/P5/DCE/hash/reçus/manques exacts. `passations/{markdown,docx}/v{1,2}/` conserve vues, publications, intentions de reçu et mémoires; historique V1 dans v2/history.json. `l08-origin/` garde les quatre paquets d'origine. Une vérification indépendante par python-docx résout chaque XPath DOCX, extrait le paragraphe et compare plage/hash de texte et hash XML; aucune confusion entre offsets texte et binaire. Une tentative de relecture pendant le rejeu a rencontré un mélange V1 renouvelée/V2 encore ancienne; ce StopIteration d'orchestration n'est ni bug produit ni résultat PASS, et toutes les preuves finales ont été relues après fin du runner.

## Fichiers et décisions conservées

Application : `patron_action/application/case_handover_handler.py`, `infrastructure/handover_reader.py` (source DCE); `infrastructure/operational_handover.py` (adaptateur de preuve DOCX bornée réutilisant le parseur de Préparation), `application/operational_handover.py` (preuve connue distincte, complétude toujours PARTIAL/REVIEW_REQUIRED). Aucun ancien objet ni acte modifié.

Interface : `web/src/features/results/HandoverSnapshotRead.tsx`, `web/src/shared/types.ts` et test `CaseHandoverPanel.test.tsx`. Tests backend : `test_operational_handover_workflow.py`, `test_l08_integrated_packet.py` (callback facultatif de qualification seulement), nouveau `test_l09_rectified_handover.py`, nouveau `test_handover_docx_excerpt.py`. Les hooks de recettes ne remplacent aucun service/politique natif.

La preuve XML est un texte localisé dans un corps vérifié, pas une interprétation d'engagement ou de contrat. Structures hors support, styles masqués (même inutilisés), texte absent/ambigu et contraintes juridiques restent UNKNOWN; aucune garantie sur la visibilité de tous les rendus arbitraires ni sur les cadres acheteur arbitraires. Autorités contractuelles, pièces financières/budgets, acceptations, OS, signatures et effets externes restent hors de cette preuve. Le reçu est opérationnel et synthétique. Les scopes tenant/rôle/affectation, confidentialité FINANCIAL_PRIVATE et append-only existants restent obligatoires; les refus et l'histoire ne valent pas qualification JWT multi-tenant complète ou recette de production.

Méthode : Superpowers executing-plans/TDD/systematic-debugging/revue, ECC security-review/verification-loop. Graphify consulté avant exploration, Serena activé; OpenDesign local (catalogue, artefact C08 existant, système `linear-app`) et Impeccable (contexte de session, craft-floor, detector0) pour la seule ligne UI ajoutée. Transport OpenDesign de session fermé, rétabli via CLI/SDK MCP local existant, sans installation/Cloud/BYOK. Context7 non nécessaire : aucun nouveau contrat de bibliothèque, parseur du dépôt réutilisé; Jev/Manus sans gain pour ces contrôles bornés. Revue indépendante uniquement statique, jamais une approbation humaine.

## Conservation et suite

Dossier privé `~/.local/share/smartao-proofs/l09-rectified-handover-20261029/` (identifiant de démarrage du29, preuves finales du30).662fichiers WIP antérieurs préservés; archives complètes/delta relues par SHA, base Git d'origine vérifiée. Deux bases dédiées vides, seul conteneur `smartao-l09-rectified-20261029` retiré sans volume persistant; ports5554/5200 fermés. Index/registre/plan actualisés, miroir Basic Memory synchronisé puis relu.

Aucun reset/clean/stash, nouveau checkout, stage/commit/push/live/corpus réel/VPS/déploiement/P3réel/signature réelle/dépôt externe/moteur candidat activé/GOpublic. L09 local qualifié avec manques, L09 général PARTIAL. Le rattachement aval L10 doit sélectionner explicitement la nouvelle passation; aucun transfert implicite des événements/décisions/accords antérieurs n'est déduit.

Prochaine étape : L10 — qualifier le rattachement des changements d’exécution à la passation V2 exacte, avec sources, impacts, actions et manques visibles, sans héritage implicite ni effet externe.
