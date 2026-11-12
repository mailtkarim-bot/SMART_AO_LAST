# L08 — annexes sourcées du paquet exact — 28 octobre 2026

Le plan global reste seul statut opérationnel. Travail dans le checkout principal, branche/HEAD confirmés,610fichiers WIP préservés; aucun commit/push, nouveau checkout, moteur activé ou effet réel.

**AS-IS :** réponse choisie/revue et couverture sourcée natives; ZIP = manifeste + réponse technique. Les preuves entreprise sont citées mais non embarquées.

**Risques :** inclusion arbitraire, RIB/FINANCIAL_PRIVATE, source étrangère ou périmée, chemin ZIP injecté, perte de sélection sur retry, ancien binaire ignorant une annexe, confusion inclusion/signature/conformité.

**Insertion et conception bornée :** liste optionnelle exigence/document/SHA dans le snapshot existant; absence de liste garde le hash legacy. Vérifier la citation dans la seule réponse choisie et les preuves natives courantes; seuls INSURANCE/KBIS autorisés (RIB privé refusé). Lecture binaire bornée et source contrôlée, copie privée immuable au snapshot. Métadonnées publiques sans clé de stockage. Liste exacte dans documents/manifeste C10, origine Submission et manifeste P5; export des mêmes octets dans des noms ZIP dérivés du UUID. Le champ documents étendu fait refuser les anciennes lectures C10 strictes plutôt que perdre les annexes. Revalidation aux frontières, historique conservé après rectificatif. Signature/couverture globale UNKNOWN, portes inchangées.

**Plan minimal et preuves :**

- [x] Rouge contrats de sélection/hash legacy et lecture privée bornée; implémenter le minimum.
- [x] Rouge parcours natif avec annexes, sélection/retry/snapshot/transmission/P5/ZIP et refus source/hash/type/droits; implémenter dans les modules existants.
- [x] Après consultation OpenDesign Local Codex et Impeccable, cases de choix exactes, confirmation humaine et intention figée, liste lisible Patron; ne pas changer les portes.
- [x] Rectificatif (invalidation de l’ancien paquet, sans réimport complet) : ancien paquet refusé pour nouvel acte; historique et copie figés; nouvelle réponse/revue/sélection requises. ZIP exhaustif limité aux pièces explicitement sélectionnées, pas conformité acheteur ni signature présumée.
- [x] Tests ciblés puis suites appropriées, types/lint/build, Semgrep/diff/secrets, recette locale synthétique et nettoyage; mettre à jour plan/index/registre et miroir Basic Memory.

Aucune nouvelle dépendance ou migration prévue. Les uploads non natifs, formats non validés, signatures et corpus réels restent hors qualification. Les résultats ne sont pas annoncés avant exécution.


## Fonction livrée et contrats

Le Préparateur retient des références exigence/document/SHA depuis la seule réponse choisie. La justification et la confirmation sont explicites. La liste et la note sont copiées dans l'intention de commande; une perte de réponse, une navigation ou un choix visible différent ne les modifient pas au retry. Aucun nouveau droit n'est accordé : les annexes administratives requièrent la classification `PERSONAL_OR_ADMINISTRATIVE` dans l'affectation; le premier POST de recette sans cette classification est refusé403. RIB/FINANCIAL_PRIVATE est refusé même avec ce droit administratif.

Le snapshot vérifie citation, DCE/plan/exigences, preuves entreprise courantes, statut VALIDATED/CLEAN, type INSURANCE/KBIS, expiration et octets. Copie privée immuable, sans clé de stockage exposée, budget total150000000octets existant. Les liens multiples vers un même document sont groupés dans un fichier, avec leurs exigences explicites. La taille et le SHA sont vérifiés à toutes les relectures; tailles invalides et adaptateurs sans lecture bornée sont refusés. La reprise d'un fichier déjà écrit après rollback vérifie aussi les octets avec cette borne.

Les documents/annexes exacts sont figés dans C10, revalidés à transmission/P5/export puis présents dans le manifeste Submission et le ZIP. Le champ documents C10 étendu fait refuser une ancienne lecture stricte qui n'attendait qu'un document technique. Les commandes sans annexes gardent leur sérialisation et leur hash legacy. Les noms ZIP dérivent des UUID et du MIME validé, jamais d'un chemin fourni par le client. La revue Patron expose la liste, les références et hashes avant P5. La présence d'une pièce ne valide ni sa signature ni sa couverture; ces états restent UNKNOWN.

## Preuves finales

- Backend entier : **4044 réussites,2avertissements,2699,40s (44:59),exit0**. Les avertissements sont Starlette/httpx et un alias Pydantic historique. Aucun échec restant dans ce run.
- Web entier : **713 réussites,4ignorés,89fichiers,370,90s,exit0**, un worker. Sept tests de contrat/lecture privée,49tests ciblés de panneau/hook/Wizard et9tests du panneau Submission passent aussi; recouvrements, non additionnés.
- Quatre parcours natifs : **4/4,375,38s**, avec/sans annexes, Markdown/DOCX, sélection exacte, absence de sélection implicite, refus de source/hash/exigence hors citation, habilitation administrative, retry, source C10/P5, même ZIP à répétition et document technique Conducteur. Deux PDF d'assurance synthétiques sont conservés octet pour octet avec le manifeste et la réponse technique.
- Une copie privée altérée fait refuser l'export; restauration de la seule fixture de test puis même ZIP. Le remplacement DCE au registre fait refuser nouvel export et nouveau snapshot depuis les anciens accords. Hash du snapshot et copies précédentes inchangés. Ceci ne qualifie pas un réimport complet de nouvelles pièces puis la reconstruction positive d'un second paquet dans la même Affaire.
- TypeScript, lint/build et Ruff/format ciblés vérifiés. Mypy application698sources sans diagnostic; application/tests :206diagnostics/40fichiers, mêmes identités historiques,0nouvelle dette. Warning lint App historique et chunk principal >500kB conservés; pas de CI entière revendiquée.
- Semgrep1.182.1 `p/security-audit`,99règles/28fichiers :0finding/0erreur; aucun ignore rapporté. Analyse locale, métriques désactivées. Detect-secrets ciblé0. Impeccable ciblé0. Un scan ne prouve pas l'absence de vulnérabilité.
- Chrome DevTools Local : deux cases non précochées, choix exacts à trois champs et SHA64, cibles >=44px, masquage à changement de session, reflow390/1280sans débordement; aucune ressource externe/cookie/token. Composant réel et projection enregistrée depuis la recette native, pas backend live ni Playwright. La justification/confirmation et le corps de retry sont prouvés par les tests du Wizard/hook; ne pas appeler ce montage une recette navigateur native de bout en bout.

## Revue, incidents et limites

Superpowers : using-superpowers, cadrage brainstorming borné, writing-plans, TDD, revue et vérification; ECC verification-loop/security-review. Graphify historique interrogé avant navigation, Serena initialisée/activée; Basic Memory relu/synchronisé en miroir du plan. OpenDesign local : catalogue courant, système Application et artefact C10 consultés; mêmes classes/conventions visuelles, aucun Cloud/BYOK/second MCP. Impeccable context/craft-floor/detect et audit ciblé, aucun init/hook ajouté. Context7 a vérifié le contrat StreamingBody.read(amt)/close de botocore avant réutilisation de la lecture S3 bornée existante; aucun stockage S3 réel appelé. Jev/Manus sans besoin de classification ni investigation distante, GitHub sans action autorisée.

Revue indépendante bornée : un P2 de lecture de copie non bornée a été signalé, reproduit en rouge, corrigé via un port optionnel de lecture bornée et contre-revu sans nouveau défaut concret. Contre-vérification indépendante23tests de stockage passés, puis7tests d'annexes courants verts. Pas approbation humaine ou audit exhaustif du WIP.

Erreurs de qualification conservées : imports manquants dans une fixture, tentative de mutation d'un document entreprise rejetée par son trigger append-only (aucun trigger désactivé; test remplacé par le refus RIB isolé avant lecture), tri d'import et lancement d'une suite DB sans URL explicite (aucune connexion de repli). Les tentatives interrompues/rouges ne sont pas PASS. Le code final est couvert par la globale ci-dessus, aucune preuve antérieure substituée.

Qualification bornée aux preuves entreprise natives; assurances PDF synthétiques prouvées, KBIS et autres MIME supportés non qualifiés sur corpus réel. Pièces arbitraires, signatures, conformité et exhaustivité acheteur restent UNKNOWN. Aucun prix/RIB exporté, moteur candidat ou porte modifié, migration/dépendance ajoutée, commit/push/nouveau checkout, live/corpus réel/VPS/déploiement/P3réel/dépôt externe/GOpublic. L08 général reste PARTIAL.

Preuves privées : `/home/noor/.local/share/smartao-proofs/l08-annex-20261028/`, incluant ZIPs natifs, manifestes, SHA, logs, revue et reçus de nettoyage/mémoire. Le plan est seul statut et prochaine étape.


Nettoyage confirmé : base `smartao_annex_test` à0table métier/0révision puis conteneur jetable propre supprimé sans montage persistant; Vite5197 arrêté et onglet de recette fermé. Miroir Basic Memory écrit avec checksum conditionnel puis relu : prochaine étape et SHA du plan concordants. Les28empreintes logicielles sont stables (20production/8tests); l'assertion d'affichage du manifeste P5 ajoutée après le lancement backend est comprise dans le Web final et ne change aucun code Python. WIP619chemins conservé, delta32fichiers archivé séparément des sauvegardes antérieures. Reçus dans le dossier de preuves, aucun commit/push.
