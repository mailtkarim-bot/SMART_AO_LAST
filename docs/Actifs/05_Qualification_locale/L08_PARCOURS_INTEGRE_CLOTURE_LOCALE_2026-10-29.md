# L08 — parcours intégré et bilan de clôture locale — 29 octobre 2026

**Verdict : campagne intégrée locale CLOSE, avec reports explicites.** Le parcours et ses refus sont démontrés sur deux Affaires synthétiques, chacune en V1/V2; aucune offre complète, conforme ou prête au dépôt n'est démontrée. L08 général reste PARTIAL. Cette clôture technique ne vaut ni accord Owner, ni conformité, ni activation d'une porte.

Le plan global reste seul statut. Checkout principal `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`;660 empreintes WIP vérifiées avant édition. Aucun reset/clean/stash, nouveau checkout, stage, commit ou push.

**AS-IS :** les fonctions de réponse, assemblage/DOCX, annexes, paquet exact, réimport et contrôle final sont qualifiées séparément. Une recette existante reconstruit deux paquets sur la même Affaire, mais elle n'assemble pas encore les observations récentes formats/noms/tailles et KBIS dans la même preuve.

**RISQUES :** additionner des preuves séparées comme un parcours unique, transférer un accord de V1 à V2, comparer aux mauvaises sources/octets, cacher les exigences manquantes ou les limites du moteur, confondre clôture de qualification locale et conformité d'une offre.

**POINTS D'INSERTION :** uniquement les recettes et assertions existantes, avec un point de configuration explicite de la recette de réimport. Pas d'abstraction produit, nouveau flux, schéma, dépendance ou UI à créer. Modifier le code métier seulement sur une rupture reproduite.

**PLAN MINIMAL :**

- [x] Rejouer les variantes Markdown et cadre DOCX dédié : même Affaire, DCE natif synthétique, contributions/couverture/annexes KBIS, revue exacte, snapshot, P5 et ZIP.
- [x] Rapprocher les contrôles et chaque nom/taille/hash aux octets du ZIP; conserver extraits, ancres, manques et UNKNOWN.
- [x] Réimporter un véritable rectificatif synthétique; refuser l'ancien paquet et les anciens actes/hash, reconstruire avec sources/revue/P5 nouveaux, historique intact.
- [x] Relire les quatre archives et les bilans; revue ciblée, régressions pertinentes, types/lint/Semgrep/diff et navigateur si utile sur l'interface existante. Pas de nouvelle UI ni nouveau workflow OpenDesign sans besoin visuel.
- [x] Statuer sur la clôture locale au périmètre prouvé, établir les reports et leurs conséquences, puis actualiser plan/index/registre, sauvegardes et miroir Basic Memory relu.

Autorités : PF2-074, M2-239–242, CT31-40 et contrat L08 de `LIVRABLES_METIER_ET_PREUVES_2026-10-19.md`. Méthode : exécution bornée et revue Superpowers, ECC security-review/verification-loop. Graphify consulté, Serena activé. Qualification d'un comportement existant : un nouveau test de parcours peut réussir d'emblée; le TDD rouge/vert est requis si une correction métier devient nécessaire, sans inventer un échec.

La validité officielle des pièces, les signatures et pouvoirs, le canal acheteur et le dépôt externe ne sont jamais présumés. Macros/mots de passe/liens, exhaustivité/financier et cadres arbitraires restent hors de cette preuve. Les noms coupés à l'extension et unités ambiguës restent UNKNOWN.


## Ruptures de recette reproduites avant qualification finale

La passe exploratoire a été interrompue volontairement à87,10s pour figer les assertions supplémentaires de lignée et de contrôle V1 obsolète; elle ne constitue pas un succès. Le rejeu final a ensuite révélé deux incohérences de fixtures, sans défaut produit confirmé :

1. La fixture KBIS recréait en V2 une capacité au même nom, rejetée `COMMAND_REJECTED`. `tests/support/third_party.py` utilise désormais son `label_suffix` et ajoute une génération lorsqu'un paquet précédent existe, comme la fixture d'assurance. L'unicité métier reste inchangée; téléversement, inspection, revue et proposition restent natifs.
2. Le premier RC de `complete_dossier` est enregistré sous le nom interne `reglement-consultation.txt`, alors que le générateur du rectificatif connaissait seulement `rc.txt`. Il ajoutait donc à tort un titre CCTP au nouveau DOCX; le classifieur répondait correctement CCTP, et les comparaisons refusaient ce type de source avec `UNSUPPORTED_SOURCE_FAMILY`. Le mapping de titre du seul helper de réimport inclut maintenant ce nom exact; aucun classifieur, règle d'analyse ou ancre n'est modifié. Le rapport V2 refusé est conservé sous diagnostics avant écrasement par le rejeu final.

La revue indépendante statique a confirmé ces deux corrections bornées et n'a identifié aucun défaut résiduel. Elle n'a exécuté aucun test et ne vaut pas validation humaine. Elle a relevé que le parcours HTTP testé refuse Collaborateur/anonyme/ID absent, mais ne crée pas d'authentification JWT réelle d'un second tenant. Un test PostgreSQL séparé sur le service final contrôle le refus du même ID de paquet avec un autre tenant de contexte; sa portée n'est pas assimilée à un E2E JWT/C10 inter-tenant complet.

**Frontière de départ :** V1 utilise une fixture de DCE déjà admis avec classifications déclarées synthétiquement; extraction, analyse, matérialisation et fonctions aval sont exécutées. V2 utilise téléversement/quarantaine/admission, extraction, classification et matérialisation natifs sur de nouveaux DOCX. Ne pas présenter V1 comme qualification du téléversement initial ou de sa classification automatique. Les deux variantes correspondent à deux Affaires indépendantes; chacune garde sa propre identité entre V1 et V2.


## Bilan des quatre générations exactes

Ces nombres désignent des signaux/exigences connus, pas un inventaire exhaustif des pièces à remettre. Chaque génération contient3fichiers documentaires (mémoire, assurance et KBIS), plus le manifeste ZIP. Les deux contributions contiennent volontairement des manques.

| Variante | Version | Signaux connus | Sans réponse | Textes avec manques | Taille mémoire, octets |
|---|---|---:|---:|---:|---:|
| markdown | v1 | 45 | 43 | 2 | 5011 |
| markdown | v2 | 46 | 44 | 2 | 5068 |
| docx | v1 | 44 | 42 | 2 | 37017 |
| docx | v2 | 45 | 43 | 2 | 37021 |

Le contrôle conserve les écarts intentionnels du corpus de développement : PDF demandé contre Markdown exporté, nom KBIS demandé différent du nom UUID exporté, limite d'un octet dépassée et nom de mémoire coupé à l'extension UNKNOWN. Ils ne sont ni renommés, ni masqués, ni transformés en conformité. P5 synthétique enregistrée au registre reste l'acte exact existant; les observations n'en changent pas les préconditions et ne la transforment pas en autorisation de conformité.

Après réimport, V1 reste historique : même ID/hash/P5 enregistré, sources REVIEW_REQUIRED, fichiers de présence UNKNOWN, comparaisons vidées, export422. Un zéro de compteur sur cette projection invalidée signifie « non vérifié », pas absence de manque. V2 utilise d'autres DCE, exigences, décision, package, snapshot, revue, hash et autorisation P5. Ancienne sélection/annexes/hash refusés, absence de P5 V2 refuse l'export; deux créations concurrentes de cycle donnent201/409 et retry du gagnant sans deuxième effet. Sources V1, copies d'annexes et quatre archives relues sont conservées sans réécriture.

## Manques, reports et conséquences

| Élément | État démontré / manque | Conséquence et suite |
|---|---|---|
| Parcours de réponse et de reconstruction exact | Contributions/assemblage, sources, choix/revue, snapshots/P5/ZIP et reprise V2 prouvés | Campagne de qualification locale close; code produit inchangé |
| Complétude de la réponse acheteur |42–44 signaux connus sans réponse et2textes avec manques par génération, volontairement laissés dans la fixture | Aucun pli complet ou exigence critique satisfaite par défaut; préparation/revue humaine nécessaires pour une offre réelle |
| Formulaire et formats acheteur | Cadre DOCX dédié uniquement; Markdown diffère du PDF demandé, nom KBIS différent | Pas de conversion/renommage ou approbation implicites; cadres arbitraires/PDF restent reportés |
| Noms avec extension et unités | Extrait «Memoire.» incomplet, Mo et agrégats non interprétés | UNKNOWN; aucune reconstitution ou correction d'ancre/moteur dans cette tâche |
| Ensemble du pli |3fichiers documentaires exportés, références financières et signaux non exhaustifs | Ni manifeste exhaustif de remise ni contrôles financiers/AE/BPU/DQE/DPGF prouvés ici; confidentialité conservée |
| Pièces et signatures | KBIS/assurance synthétiques téléversés/inspectés/revus; validité officielle UNKNOWN; signature protégée et POST natifs403 | Aucun registre officiel/antivirus réel, signature cryptographique/pouvoir ou validité juridique admis |
| Autres contrôles de remise | Macros, mots de passe, liens, supports physiques, canal/portail et reçu externes non qualifiés | Pas de dépôt externe, plateforme ou conformité présumés |
| Isolation et droits | Refus natifs Collaborateur/anonyme/ID absent, service PostgreSQL autre tenant de contexte refusé | Ne vaut pas E2E JWT/C10 complet avec utilisateur d'un second tenant |
| Typage global et diffusion |206 diagnostics de tests préexistants, aucun nouveau; pas de déploiement | CI de typage entière non qualifiée; WIP local, NO-GO public maintenu |

Le critère général « aucune exigence critique sans réponse ou refus explicite » d'une offre complète **n'est pas démontré par cette fixture volontairement incomplète**. La clôture porte sur la campagne du parcours et la visibilité de ses manques, pas sur la satisfaction générale de L08 ni sur le dossier d'un acheteur réel. Les reports restent dans ce bilan et le plan; ils ne bloquent pas par inférence tout autre livrable local déjà cadré.

## Preuves exécutées sur ce snapshot

- Nouvelle recette intégrée : **2 tests réussis,1avertissement,230,13s,exit0**, deux variantes et quatre générations exactes. Réimport réel, nouvelles sources/actes, refus de transfert/concurrence/retry/historique et octets contrôlés par les recettes natives réutilisées.
- Régressions application/API ciblées : **208 réussites,23désélectionnées par `-m 'not db'`,1avertissement,18,28s,exit0**. Les23tests DB ne sont pas comptés PASS. Preuve séparée PostgreSQL : **1réussite/11,16s/exit0** pour lecture de paquet tenant-scoped, signature protégée et absence de création d'acte par GET.
- Web Submission : **42 réussites/13,23s/exit0**. Aucun code Python applicatif/API/UI, CSS, dépendance, contrat public, schéma de manifeste, algorithme d’empreinte, règle de porte ou schéma de données modifié dans cette tâche; pas de rejeu automatique des longues suites globales. La globale précédente reste une preuve datée, non réattribuée à cette tâche.
- Mypy application :703fichiers sans diagnostic. App/tests :206diagnostics40fichiers/1242sources, identités inchangées contre la clôture noms/tailles. Ruff/check/format3fichiers Python verts; tête Alembic20261027_0146 inchangée. La fixture exerce upgrade/head/downgrade sur bases jetables; aucune migration ajoutée.
- Semgrep1.182.1,`p/security-audit`, métriques désactivées,3fichiers de tests,0finding/0erreur/exit0; nombre de règles effectivement exécutées dans le reçu. Scan de secrets par motifs stricts0candidat, limité aux3sources de tests; pas de certification de sécurité.
- Chrome DevTools Local : véritable panneau/hook sur rapports natifs enregistrés, API de lecture simulée. Séquence Markdown V1→V1 obsolète→V2 puis DOCX V2; IDs/hash/P5/revues distincts, avertissement historique et manques/UNKNOWN visibles, fermeture de session masque la projection. Viewports CDP1280/393px sans débordement, cibles>=44px, texte16px. Zéro cookie/token/stockage local ou destination externe. Redimensionnement de fenêtre refusé, puis émulation CDP et sélection fraîche qualifiées; pas de PASS mobile sur l'appel refusé. Pas Playwright, API métier live, capture disque ou audit WCAG complet.
- Revue indépendante statique Graphify/ECC : aucun défaut produit confirmé, corrections de fixtures relues et limite tenant explicitée. Les preuves de tests proviennent du principal; aucun accord humain n'est attribué au relecteur.

Les quatre ZIP ont été relus indépendamment : noms égaux à l'inventaire documentaire plus manifest.json, manifeste canonique égal au hash du contrôle, SHA et taille de chaque fichier égaux aux octets. `qualified-packets.json` et `native-packets/{markdown,docx}/lineage.json` conservent les identifiants exacts. `stale-v1-after-rectificatif.json` conserve le refus courant sans effacer les actes historiques. Les deux échecs de fixtures et la passe exploratoire interrompue restent des preuves négatives, jamais comptées en succès.

## Fichiers concernés et conservation

- `backend/tests/db/test_l08_integrated_packet.py` : nouveau parcours de qualification, assertions sur contrôles, archives et lignée.
- `backend/tests/db/test_l08_reimport_packet.py` : configuration explicite optionnelle du workflow, capture du contrôle/du refus V1 et titre exact de la fixture RC.
- `backend/tests/support/third_party.py` : suffixe de génération de la capacité KBIS, sans changement de contrat produit.
- Présent dossier, index, REGRESSION.md et plan : preuve, bilan, reports et prochaine étape; aucun catalogue parallèle de statut.

Preuves privées : `~/.local/share/smartao-proofs/l08-integrated-20261029/`. Les660 fichiers WIP antérieurs sont préservés; archives complètes/delta relues par SHA et base Git d'origine vérifiée. Deux bases dédiées vides après tests (0table métier/0révision), seul conteneur `smartao-l08-integrated-20261029` retiré sans volume persistant; preview5200 et onglet dédiés fermés. Plan/index/registre actualisés, miroir Basic Memory synchronisé puis relu.

Méthode/outils : Superpowers using-superpowers/executing-plans, TDD sur les deux corrections de fixtures après échec natif, revue finale; ECC security-review/verification-loop, et code-review-and-quality par le relecteur. Graphify consulté avant exploration, Serena activé, Basic Memory miroir local. Aucune API/bibliothèque nouvelle à documenter par Context7; Jev/Manus sans gain pour cette recette bornée. OpenDesign/Impeccable inapplicables : aucun changement visible d'interface ni direction graphique; seul le renderer existant est relu dans un harnais isolé. Aucun connecteur de publication utilisé.

Aucun reset/clean/stash, nouveau checkout, stage/commit/push, corpus réel/live/VPS/déploiement/P3réel/signature réelle/dépôt externe/moteur candidat activé/GOpublic. L08 général PARTIAL conservé; continuité vers L09 seulement au périmètre synthétique et avec ces manques.

Prochaine étape : L09 — qualifier la continuité entre le pli reconstruit après rectificatif et la passation au conducteur, avec sources, engagements et manques exacts, sans héritage implicite ni effet externe.
