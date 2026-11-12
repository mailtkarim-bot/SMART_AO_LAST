# L08 — noms et tailles du pli exact — 29 octobre 2026

Le plan global reste seul statut. Checkout principal, branche et HEAD inchangés; 656 empreintes WIP de la tranche précédente vérifiées avant modification. Aucun reset/clean/stash, checkout, stage, commit ou push.

**AS-IS :** le contrôle final porte noms ZIP exacts et tailles d'annexes, mais taille du mémoire UNKNOWN. La lecture Préparation a déjà vérifié ses octets. Les consignes RC courantes et confirmées sont disponibles avec ancres; aucune comparaison de nom/taille n'existe.

**RISQUES :** comparer le nom original au nom exporté, altérer casse/accents dans le nom demandé, confondre Mo et Mio, inventer une portée, ignorer les clauses contradictoires, assimiler une mesure à une conformité.

**POINTS D'INSERTION :** transmettre la longueur des octets déjà vérifiés via la couverture native; comparer en lecture les noms de base exportés et tailles des fichiers documentaires connus. Aucun changement de manifeste, hash, export, gate, droit ou schéma de base.

**PLAN MINIMAL ET TESTS :**

- [x] TDD Python : nom exact sensible à casse/accents, noms sans espace, taille limite inclusive en octets/Mio; absence, taille inconnue, source/lot/confirmation/contradiction et formulation non prise en charge UNKNOWN. Aucun arbitrage de conformité.
- [x] TDD UI dans le contrôle existant : extrait/locator/ancre, demandé/observé, pièces/manques, raison et limites; OpenDesign local et Impeccable avant édition.
- [x] Recette native PostgreSQL synthétique : noms et tailles contre les octets du ZIP, mêmes hash/P5 et aucune écriture GET. Contrôles d'accès et invalidation existants conservés.
- [x] Régressions pertinentes Submission/Préparation, Web, types/lint/build, revue ciblée, Semgrep et diff. Une seule qualification intégrée finale; aucun nouveau sous-chantier ouvert par automatisme.
- [x] Sauvegardes WIP/delta relues, plan/index/registre et miroir Basic Memory relu.

**CONTRAT BORNÉ :** consignes RC confirmées et ancrées du DCE courant; mémoire/KBIS nommés explicitement entre guillemets, noms sans espaces et taille maximale par fichier documentaire connu. Comparaison à l'identique des noms de base ZIP (pas au nom original). Unités octets et Mio (1048576 octets); unité Mo ambiguë, taille agrégée/ZIP compressé, motifs et chemins demandés non interprétés => UNKNOWN. Les métadonnées manifest.json, les fichiers absents de cet inventaire, la portée lot/phase/opérateur et l'exhaustivité restent UNKNOWN. Applicabilité et conformité toujours UNKNOWN. Aucun renommage automatique. Macros/mots de passe/liens/antivirus ne sont pas qualifiés par cette tranche.

Autorités : PF2-074, M2-239–242, CT31-40. Skills : cadrage, plan minimal et TDD Superpowers; ECC security-review/verification-loop; Graphify consulté, Serena activé; OpenDesign local/Impeccable pour extension du panneau existant. L08 général reste PARTIAL.

## Fonction livrée et fichiers

La lecture Préparation transmet `content_byte_size`, longueur des octets sélectionnés déjà vérifiés. `final_control` reprend cette taille seulement si la source est CURRENT; annexes, noms ZIP et SHA restent ceux du paquet existant. `name_size_comparisons` ajoute les consignes source/extrait/locator/ancre/confirmation, cible, nom ou maximum, fichiers observés, état et raison. `buyer_names_sizes_state` indique seulement la présence d'observations. Aucune conformité/applicabilité ni absence de contrainte ne sont inférées; aucune commande ni porte n'est créée.

Nouveau comparateur pur `backend/app/modules/submission/application/buyer_name_size_comparison.py`; intégration dans `submission/application/final_control.py` et `submission/public/final_control_contracts.py`. Taille dans `preparation/public/contracts.py` et `preparation/infrastructure/response_coverage.py`. Ajustement ciblé `buyer_file_comparison.py` : le préfixe « Format de fichier : » n'est pas une demande de MIME; une consigne de nom seul reconnue entière ne doit pas transformer son extension en consigne de format. Une phrase composée non reconnue reste UNKNOWN.

Interface : `web/src/features/submission/BuyerNameSizeComparisons.tsx`, intégration dans `SubmissionFinalControl.tsx`, types `web/src/shared/types.ts`. Extrait, locator, ancre/hash, valeur demandée, nom de base exporté, chemin ZIP, taille, raison et UNKNOWN restent lisibles. Classes existantes, aucune palette/CSS/dépendance nouvelle. OpenDesign : catalogue courant, système `linear-app` et artefact C10 `plan-reponse-c10.html` consultés en local; apparence Owner CYTD conservée. Aucun Cloud/BYOK/prototype supplémentaire ni installation. Impeccable context/craft-floor et detector final zéro constat.

Tests : `backend/tests/application/test_buyer_name_size_comparison.py`, helper `test_buyer_file_comparison.py`, recette étendue `backend/tests/db/test_l08_buyer_format_control.py`, panneau `web/src/features/submission/SubmissionPanel.test.tsx`.

## Régressions reproduites et corrigées

- Rouge initial : comparateur absent; taille du mémoire None contre32 octets attendus. Champs et composition ajoutés après preuve rouge.
- Rouge UI : section « Noms et tailles des fichiers » absente. Première intégration : assertion historique d'écart devenue ambiguë car deux écarts sont désormais affichés; assertion bornée aux deux observations, sans masquer un écart.
- Revue indépendante P2 et rouge natif DOCX :5002 octets Markdown annoncés pour37023 octets DOCX dans le ZIP. `selected_byte_size` est désormais figé à la première lecture du draft exact avant lecture de sa source Markdown; recette DOCX finale verte. La tranche DOCX n'est pas réimplémentée.
- Limite entière trop grande et nom avec espaces contradictoire à une consigne sans espaces : deux rouges puis UNKNOWN explicite. Contre-revue P2 : cette contradiction de nom neutralisait aussi une taille indépendante; rouge dédié puis restriction aux critères de nom.
- Nommage/taille sous préfixe « Format de fichier » neutralisaient une comparaison MIME indépendante. Rouges simples et nom KBIS.pdf, puis exclusion de la seule consigne de nom reconnue entière et sélection après retrait du préfixe. Extension jamais interprétée comme demande MIME; contre-revue statique sans défaut concret résiduel confirmé.

## Preuves finales et portée

- **67 tests purs réussis**,0,81s :37 nouveaux et30 antérieurs, couvrant frontières inclusives, absence de taille, casse/accents, nom sans espaces, sources/ancres/lot, incohérences, Mo/agrégats/motifs/chemins, limite JSON exacte, état obsolète et séparation des aspects.
- **231 tests ciblés réussis, 1 avertissement, 67,18s, exit0** : comparateurs, contrôle final, couverture, paquet/annexes, revue/snapshot, DOCX, contrats source/porte et routes Patron Submission/preuves/signatures. Une passe antérieure229/75,19s est historique et chevauche cette passe, sans addition.
- **3 recettes natives PostgreSQL réussies, 1 avertissement, 232,94s, exit0** : Markdown/PDF/ZIP interdit, DOCX/ZIP demandé et fichiers individuels; origine C10, revue/P5 existants, taille exacte de chaque fichier contre octets ZIP, SHA égaux, nom KBIS divergent, limites1/1048576octets, noms sans espaces et sources coupées UNKNOWN. GET conserve compteur événements/outbox et manifeste/hash. Les assertions de refus et droits sont celles du parcours natif réutilisé; aucune politique assouplie.
- Web complet : **721 réussites, 4 ignorés, 90 fichiers, 340,57s**; ciblés finaux42/11,99s, types/build verts. Lint : seul avertissement historique App.tsx:517; chunk903,61kB (>500kB). Aucun résultat de la tranche précédente substitué. Le dernier libellé de raison a aussi été couvert par rejeu ciblé/build après la passe globale.
- Mypy application : **703 fichiers sans diagnostic**. App/tests : **206 diagnostics dans40 fichiers/1241sources**, identités inchangées contre la clôture précédente. Typage global non déclaré vert. Ruff/check/format9Python verts; tête Alembic inchangée20261027_0146, aucune migration de cette tranche.
- Semgrep **1.182.1, p/security-audit, 99 règles, 13 fichiers,0 finding/0 erreur, exit0**, métriques désactivées, analyse locale; ce scan borné n'est pas une certification de sécurité. Aucun secret détecté par motifs stricts sur les13 fichiers logiciels, preuve bornée.
- Chrome DevTools Local : vrai panneau/renderer/hook sur rapports natifs enregistrés, API de projection simulée seulement. Largeurs observées395/1282px, zéro débordement, summaries>=44px, texte16px, source/hash/noms/tailles/inconnus visibles; session fermée masque la projection, aucun cookie/token/stockage local ou trafic externe. Pas Playwright, dépôt réel, capture disque ou audit WCAG complet. Onglet/preview dédiés fermés.

Les premières invocations trop larges sans URL DB ont rencontré des erreurs de fixture, conservées et non qualifiées comme bugs produit ni succès; reprise ciblée sur DB explicitement jetable et son flag. Les rouges natifs successifs sur nom partiel, DOCX et propagation d'incertitude sont conservés, aucune suite interrompue comptée PASS. Le CLI Semgrep a été résolu après chemin de venv absent; seul scan du CLI réellement installé retenu.

## Limite réelle de l'extraction des noms

Le moteur DCE existant découpe actuellement certains noms au point d'extension : la consigne synthétique « Le mémoire technique doit être nommé «Memoire.pdf». » devient un extrait acheteur arrêté à «Memoire.». Le contrôle **ne reconstitue pas** le nom manquant; cette ligne et les observations de nom affectées restent UNKNOWN avec raison. Les noms exacts avec extension/casse/accents sont prouvés sur source intacte par tests purs; la recette native prouve le nom explicite sans extension «KBIS», la règle sans espaces et cette limite de source coupée. Aucune prise en charge native générale des noms avec extension n'est revendiquée. Ni analyseur, version de moteur, candidat, ancre ou corpus de référence ne sont modifiés pour contourner cette limite.

Le mot Mo reste ambigu sans convention explicite; seules unités octets/Mio sont comparées. Taille totale ou compressée, manifest.json, autres pièces absentes de l'inventaire, règles non extraites, macros/mots de passe/liens/antivirus, contraintes financières, validité et signatures restent UNKNOWN/non qualifiés. Les fixtures acheteur nomment volontairement des fichiers autrement que l'export actuel : l'écart reste visible, sans renommer automatiquement des octets déjà revus/autorisés.

## Conservation et clôture locale

Les13 fichiers logiciels sont figés; WIP principal antérieur préservé. Preuves et archives complètes/delta sous `~/.local/share/smartao-proofs/l08-names-sizes-20261029/`, avec lecture indépendante noms/tailles/SHA des trois ZIP et empreintes des archives relues. Deux bases synthétiques dédiées vides après tests (0table métier/0révision); seul conteneur `smartao-l08-names-sizes-20261029` retiré, aucun volume persistant; preview5200/port5554 et onglet dédiés fermés. Plan/index/registre actualisés et miroir Basic Memory synchronisé puis relu.

Méthode Superpowers : cadrage borné, plan minimal, TDD, revue indépendante; ECC security-review et verification-loop. Graphify consulté avant exploration, Serena activé. Context7 non nécessaire : aucun nouveau contrat de bibliothèque, réemploi des patterns du dépôt; Jev/Manus sans gain sur ce contrôle local borné. Basic Memory reste un miroir. Aucun connecteur de publication utilisé.

Aucun reset/clean/stash, nouveau checkout, stage/commit/push, live/corpus réel/VPS/déploiement/P3réel/signature réelle/dépôt externe/activation/GOpublic. L08 général PARTIAL : ce contrôle documentaire ne vaut pas conformité et ses reports sont explicites.

Prochaine étape : L08 — qualifier le parcours intégré du DCE synthétique au pli exact et à sa reprise après rectificatif, puis statuer sur la clôture locale avec manques et reports explicites, sans modifier les portes ni effectuer de dépôt externe.
