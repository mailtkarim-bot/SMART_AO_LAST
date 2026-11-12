# L08 — formats et mode de remise acheteur — 29 octobre 2026

Le plan global reste seul statut. Checkout principal `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`;651empreintes WIP vérifiées contre la clôture précédente. Aucun reset/clean/stash, nouveau checkout, stage, commit ou push.

**AS-IS :** le contrôle final connaît le pli ID/version/SHA, ses fichiers/MIME et les exigences non financières connues avec extraits, locators, ancres et confirmation. L'export local est ZIP; il ne prouve ni acceptation acheteur, ni dépôt. Pas de rapprochement structuré entre consigne et format/mode observé.

**RISQUES :** appliquer une consigne à la mauvaise pièce/phase/lot, lire une négation comme obligation, ignorer une contradiction ou une source tronquée, assimiler profil acheteur et format d'archive, transformer concordance technique/P5 en conformité.

**POINTS D'INSERTION :** projection actuelle de couverture Préparation, composition du contrôle final Submission, DTO/API et panneau existants. Comparateur pur et borné, sans nouveau moteur, extraction, classification ou règle de porte. Manifestes, hashes, commandes, idempotence, droits et export restent inchangés.

**CONTRAT BORNÉ :** consignes connues de RC courant, ancrées et confirmées, formulations explicites sur mémoire technique/KBIS et archive ZIP/fichiers individuels. Concordance ou écart sont des observations techniques, jamais une conformité; applicabilité reste UNKNOWN. Une portée non précisée, un lot explicitement extrait sans rattachement fiable, une composition, une négation non reconnue, une contradiction, une source non confirmée/tronquée/périmée ou un canal externe donnent UNKNOWN avec raison visible. Sans lot explicite, comparer le MIME à une phrase ciblée n'établit pas une portée globale ou une applicabilité aux lots. Aucune consigne non extraite n'est inventée; inventaire/exhaustivité et exigences financières restent UNKNOWN.

## Plan minimal et tests à prouver

- [x] TDD : PDF demandé contre Markdown observé, KBIS PDF concordant, ZIP demandé/interdit et fichiers individuels, cible absente; sources et fichiers exacts conservés, aucune porte/autorisation déduite.
- [x] Refus d'inférence : portée inconnue, phrases composées/négatives/tronquées, ancres absentes/mauvais DCE, absence de confirmation, conflit de consignes, source obsolète et canal externe non vérifié.
- [x] Recette native synthétique : mêmes données C10/P5/ZIP, contrôle en lecture sans événement/outbox, droits existants et provenance conservés. Aucun ancien résultat substitué.
- [x] UI après consultation OpenDesign locale/Impeccable, raisons/extraits lisibles, ciblés/Web/navigateur, revue, types/lint/build, Semgrep et diff/empreintes.
- [x] Suites appropriées, nettoyage, sauvegardes locales, plan/index/registre et miroir Basic Memory relu. Aucun commit/push/live/corpus réel/VPS/déploiement/P3 réel/signature/dépôt externe/activation/GO public.

Autorités : PF2-074, M2-239–242 (aucune hypothèse ZIP), CT31-40. La recette ne qualifie pas une plateforme acheteur ni les macros, signatures, mots de passe, tailles ou conformité générale. L08 général reste PARTIAL.

## Fonction livrée en lecture

Le contrôle final rapproche les consignes de la couverture non financière existante et les fichiers du paquet exact, sans relire de corpus externe ni créer une nouvelle extraction/classification. La composition reçoit les mêmes objets vérifiés que le contrôle C10 actuel. Les nouvelles données sont `local_delivery_mode`, `buyer_formats_state` et `format_comparisons`; chaque observation garde exigence, extrait, locator, ancre/hash, confirmation et pièces exactes. Aucun manifeste, hash, commande, rôle, droit ou précondition de P5/export changé.

Les formulations prises en charge sont littérales et ciblées : mémoire technique remis au format PDF/DOCX/PNG, KBIS fourni dans ces formats, pli remis en archive ZIP, ZIP interdit, fichiers individuels. Un préfixe explicite « Format de fichier : » est accepté, dans les signaux déjà reconnus par le pipeline. Les phrases sont normalisées pour accents/espaces/apostrophes, pas interprétées comme instructions d'agent. Les formulations non prises en charge restent UNKNOWN; aucune exhaustivité automatique du DCE n'est revendiquée.

`OBSERVED_MATCH` signifie seulement MIME identique ou ZIP local identique au conditionnement cité; ce n'est ni conformité, ni autorisation, ni acceptation. `OBSERVED_MISMATCH` décrit différence de MIME/conditionnement ou absence de pièce ciblée dans le pli connu. Sans source RC courante/confirmée/ancrée, avec lot candidat non établi, texte tronqué/limité, composition ou portée non déterminée, le résultat reste UNKNOWN avec raison. Les contrôles de canal externe restent UNKNOWN/NOT_PERFORMED. Le registre de signature protégé n'est pas consulté.

### Correction après revue

La revue indépendante a trouvé une vraie omission : une consigne positive pouvait rester concordante alors qu'une seconde source courante disait le contraire sous forme négative non interprétée. Deux rouges ont reproduit positive+negative et positive+composition PDFouDOCX. Le comparateur propage maintenant l'incertitude des consignes non interprétées, courantes, confirmées et ancrées sur le même sujet explicitement mentionné. Il ne transforme pas la négation en obligation. Les consignes reconnues incompatibles sont également conservées et UNKNOWN; aucun arbitrage silencieux. Une source non courante/non confirmée ne peut pas empoisonner une consigne courante.

Contre-revue statique : aucun défaut concret résiduel confirmé dans ce correctif. Aucun test/DB/scan exécuté par le relecteur; les preuves de runners sont celles du principal. La distinction observation de MIME/applicabilité UNKNOWN est explicite, notamment pour les lots.

## Preuves acquises

- Rouges initiaux : champ de projection absent, puis section UI absente. Correctifs minimaux Python/API/UI après échec observé.21tests métier de comparaison +9tests antérieurs du contrôle final : **30 réussites**,0,76s. Pas de test de simple texte source ou de getter ajouté.
- Recette native initiale3/315,06s puis rejeu partagé final **113 réussites, 1 avertissement, 681,44s**, exit0, incluant les trois cas natifs après correction : technique Markdown contre PDF, technique DOCX demandé, KBIS PDF, ZIP demandé/interdit, fichiers individuels. Les deux campagnes se chevauchent; elles ne sont pas additionnées.
- Trois ZIP/manifestes/rapports relus indépendamment : mêmes noms, SHA de chaque fichier égal aux octets ZIP, manifeste égal au registre, mêmes IDs/version/hash attendus. Lecture du contrôle n'ajoute ni événement ni outbox. P5 existant est relu, jamais créé par cette comparaison.
- Web complet : **721 réussites, 4 ignorés, 90 fichiers, 455,61s**, exit0; ciblés42/15,12s, types/lint/build verts. Warning historique App.tsx:517, chunk899,39kB (>500kB). Les trois erreurs de typage applicatif initiales (matches optionnels/set) et l'unique diagnostic de fixture typée ont été corrigés, pas ignorés.
- Mypy application : **702 fichiers sans diagnostic**. App/tests : **206 diagnostics dans40fichiers**, mêmes identités de baseline, aucun nouveau diagnostic; CI entière de typage non qualifiée. Ruff/format sur5Python;9SHA logiciels figés pour les suites finales. Aucune migration/dépendance/CSS/palette ou moteur candidat changé.

## Interface et outillage

Chrome DevTools Local sur le véritable composant/panneau/hook et rapports natifs enregistrés : source/extrait/hash et écart visibles pour ZIP interdit/PDF-Markdown, concordance observée pour ZIP demandé, écart pour fichiers individuels; conformité et applicabilité UNKNOWN et dépôt non effectué lisibles. Viewports mesurés1282/393px sans débordement, texte hérité16px, summaries>=44px; fermeture de session masque la projection. Aucun cookie/token/stockage local ou trafic externe. API de projection simulée, pas API métier live ni Playwright. Aucune capture disque, audit WCAG complet ou refonte CYTD revendiqués; preview et onglet dédiés fermés.

OpenDesign : catalogue courant, système `linear-app` et artefact C10 existant consultés via CLI MCP local/SDK installé, aucune installation/configuration/Cloud/Vela/BYOK ou génération nouvelle. L'Owner CYTD reste l'autorité d'apparence; classes existantes conservées sans nouveaux tokens/styles. Impeccable context une fois, craft-floor, detector final zéro constat; aucun PRODUCT/DESIGN/.impeccable créé.

Superpowers : using-superpowers, brainstorming borné, writing-plans, test-driven-development, systematic-debugging et requesting-code-review. ECC : security-review et verification-loop. Graphify consulté avant exploration; Serena initialisé/activé sans navigation sémantique supplémentaire nécessaire. Basic Memory lu localement via CLI (MCP non exposé). Context7 non nécessaire : aucune API de bibliothèque nouvelle, patterns Pydantic existants et comparaison standard Python; Jev/Manus non utiles à cette correction/revue locale. Aucun connecteur de publication utilisé.

Preuves privées : `/home/noor/.local/share/smartao-proofs/l08-buyer-formats-20261029/`, sous `native-packets/`, `qualified-packets.json`, `browser-qualified.json`, logs rouges/verts, comparaisons de types et empreintes. Les consignes non extraites, les autres formulations/familles/phases/lot, contraintes financières, tailles/macros/mots de passe/signatures et acceptation d'un portail restent non qualifiés. Aucune conformité du pli déduite; L08 général PARTIAL.

## Fichiers concernés

**Application Python/API :**

- [backend/app/modules/submission/application/buyer_file_comparison.py](../../../backend/app/modules/submission/application/buyer_file_comparison.py)
- [backend/app/modules/submission/application/final_control.py](../../../backend/app/modules/submission/application/final_control.py)
- [backend/app/modules/submission/public/final_control_contracts.py](../../../backend/app/modules/submission/public/final_control_contracts.py)

**Interface et types :**

- [web/src/shared/types.ts](../../../web/src/shared/types.ts)
- [web/src/features/submission/BuyerFormatComparisons.tsx](../../../web/src/features/submission/BuyerFormatComparisons.tsx)
- [web/src/features/submission/SubmissionFinalControl.tsx](../../../web/src/features/submission/SubmissionFinalControl.tsx)

**Tests et fixtures :**

- [web/src/features/submission/SubmissionPanel.test.tsx](../../../web/src/features/submission/SubmissionPanel.test.tsx)
- [backend/tests/application/test_buyer_file_comparison.py](../../../backend/tests/application/test_buyer_file_comparison.py)
- [backend/tests/db/test_l08_buyer_format_control.py](../../../backend/tests/db/test_l08_buyer_format_control.py)


## Clôture et limites de validation

Backend complet : **4087 réussites, 2 avertissements, 3916,02s** (journal intégral conservé). Le handle de processus a expiré après compaction; son code de sortie n’a pas pu être relu, le résumé final pytest est la preuve directe. Aucune suite interrompue ni résultat attendu compté comme réussite. Les deux avertissements concernent Starlette/httpx et un alias Pydantic préexistants. Alembic reste `20261027_0146`; aucune migration nouvelle. Base jetable vide après tests (0 table métier/0 révision), conteneur exact retiré sans volume persistant; ports5554/5200 fermés. Neuf empreintes logiciels revalidées. Sauvegarde WIP complète et delta relus par SHA, plan/index/registre actualisés; miroir Basic Memory synchronisé et relu.

Le TDD et la revue Superpowers, la vérification/revue sécurité ECC, Ruff, types et Semgrep sont bornés aux preuves décrites. Les 206 diagnostics préexistants app/tests, quatre tests Web ignorés et avertissements lint/chunk restent ouverts. Chrome DevTools Local ne constitue pas une preuve Playwright, de dépôt, de validité de signature ou de conformité acheteur. Aucun effet externe ni accord humain transféré.

Prochaine étape : L08 — qualifier le contrôle sourcé des noms et tailles des fichiers du pli exact, avec limites et manques visibles, sans modifier les portes ni présumer leur conformité.
