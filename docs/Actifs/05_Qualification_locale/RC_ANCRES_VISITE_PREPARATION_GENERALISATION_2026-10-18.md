# RC — contrat d’ancre de visite et préparation de généralisation — 18/10/2026

## AS-IS, risques et périmètre

Checkout principal `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`, WIP conservé. Le dossier v10 précédent a mesuré 6/8 positives et cinq gates fausses ; son écart d’ancre visite opposait `est-elle obligatoire` dans le gold à `obligatoire` dans le moteur. Ces résultats restent historiques et ne sont pas recalculés.

Cette tranche **explicite le contrat existant**, sans changer le parseur, le moteur, la CLI, les profils ou le runtime. Les points d’insertion sont la documentation, les tests de caractérisation et un nouveau gold préparatoire. Risques : maquiller le score historique, réduire une preuve à un indice sémantiquement insuffisant, ou écrire les attentes de généralisation à partir des limites actuelles du parseur. Les attentes sémantiques du nouveau gold sont donc séparées des états techniques et ne sont pas obtenues en appelant le moteur.

## Contrat technique de l’ancre DEMAND

L’ancre de demande est **l’indice lexical capturé par la grammaire reconnue**, pas systématiquement la proposition interrogative entière. Elle atteste la demande reconnue dans la requête ; elle ne prouve ni la réponse, ni une obligation source, ni son applicabilité.

| Forme reconnue | Extrait DEMAND exact | Convention |
|---|---|---|
| La visite de site est-elle obligatoire… | `obligatoire` | adjectif seul, auxiliaire/inversion exclus |
| Est-ce que la visite de chantier est facultative… | `facultative` | ni préambule ni auxiliaire |
| La participation à la visite médicale est-elle imposée ? | `imposée` | le sujet et sa qualification restent dans SUBJECT |
| Faut-il effectuer une visite de site… | `Faut-il effectuer` | interrogatif et action inclus |
| La visite de site doit-elle être effectuée ? | `doit-elle être effectuée` | groupe verbal au passif inclus |
| À quelle heure débute la visite de site… | `À quelle heure` | DATE_TIME reconnu, couverture UNSUPPORTED ; pas une obligation |

Règles communes : octets UTF-8 du texte original, indexation zéro, intervalle `[start_byte,end_byte)`, extrait exact sans normalisation ni expansion, `query_sha256` du texte entier. SUBJECT et LOT ont leurs ancres propres. Le span sémantique d’une proposition complète peut être utile à l’annotation humaine ; il ne doit pas être comparé comme si c’était le même contrat que l’indice DEMAND. Un changement de convention imposerait un nouveau contrat explicite et une requalification, pas la réécriture silencieuse d’un gold mesuré.

Les formes documentées sont communes à l’intention fermée v8 et à ses formes étendues v9/v10. V7 conserve son contrat antérieur ; aucun profil n’est changé. Une requête multiple ou tronquée non reconnue garde UNKNOWN/AMBIGUOUS et n’acquiert pas artificiellement une ancre DEMAND. Une ancre reconnue ne rend pas une demande temporelle couverte. Les conditions **sources** et leurs ancres restent un contrat distinct de celui de la demande **requête**.

Le gold v18 et sa gate `rc_query_intent_valid=false` restent inchangés. Le présent contrat explique l’écart, **il ne transforme pas rétroactivement ce résultat en PASS**. Tout futur banc devra annoncer avant mesure s’il évalue l’indice lexical, la proposition sémantique ou les deux.

## Préparation hors templates simples

Artefact : `backend/tests/fixtures/knowledge/rc_generalization_preparation_v1.json`. Sources synthétiques écrites avant tout appel au moteur : prose de recevabilité, tableau, événement conditionnel, dispense, coordination de pièces, condition tronquée, article à deux sujets, suppression par rectificatif, horaire sans obligation, citation non applicable, mémoire décrit par son contenu. Les questions utilisent négation interrogative, reformulation, référence à un article, deux demandes et absence de lot. Ce n’est pas une permutation des seuls lots ou suffixes du jeu18. Ce n’est toutefois **ni un corpus réel, ni un holdout aveugle statistiquement indépendant**.

Le gold porte la pertinence documentaire pour répondre à la question et les valeurs candidates d’obligation dans les sources, avec UNKNOWN d’applicabilité. Cette pertinence inclut une source qui explique explicitement les limites d’une citation ; elle ne signifie pas preuve d’exigence applicable. Une exigence explicitement présente dans une source multi-sujets peut être REQUIRED dans la vérité sémantique, alors que le moteur doit rester UNKNOWN tant que la couverture n’est pas prouvée. Ne pas remplacer la vérité annotée par la sortie que le parseur sait actuellement fournir.

- 16 fragments,18questions :13 positives documentaires (dont1citation explicitement non probante),4 exclusions de portée/état et1demande financière non évaluable.
- Une requête sans lot demande cinq sources pertinentes, y compris suppression de l’obligation et caractère non indiqué ; pas seulement les textes que le parseur peut rappeler. Le budget top10 et les rapports@1/@5/@10 sont déclarés, maximum5sources par question, sans opposition automatique entre lots.
- Les sources étrangères ont des identités/version distinctes ; version remplacée non courante et extraction REVIEW_REQUIRED exclues. Une seule version courante par tenant/Affaire est vérifiée statiquement.
- Quatre faits structurés distincts préservent une condition complète, l’horaire déclaré `10 h 30`, une citation historique et son disclaimer actuel. Ils ont chacun source/hash/span UTF-8/extrait ; aucune normalisation ni date/fuseau inventé. `value/kind=UNKNOWN` décrit uniquement l’obligation non établie, pas la disparition de ces faits certains.
- `runtime_expectations=null` : aucun état attendu du parseur n’est inventé à partir d’une attente sémantique. Le mapping vers le banc legacy/fermé reste à spécifier explicitement.
- `held_out=false`, `preparation_only=true`, statut `PREPARED_NOT_RUN`. La CLI existante refuse ce fichier avant de construire l’encodeur ; un test le démontre. Aucun E5, SQL, résultat de rappel ou score de performance n’est revendiqué pour ce gold.

## Mapping préparé, sans adaptateur exécuté

Le protocole JSON fixe six axes pour l’adaptateur futur :

1. Comparer sujet/demande/lot et pertinence documentaire sémantiques indépendamment du vocabulaire courant du parseur. Ne jamais produire une attente COVERED/UNKNOWN en copiant la sortie mesurée.
2. Enregistrer séparément le contrat fermé sujet/demand/coverage. Les demandes sémantiques CONDITION ou MULTIPLE n’ont pas d’équivalent direct dans son enum ; ce sont des limites explicites, pas des obligations simples forcées.
3. Exiger `answer_state=UNKNOWN` partout. `protected_runtime_unknown` ne rend pas les documents non pertinents et n’exige pas leur rappel ; les sources multi-sujets et conditions tronquées ne sont pas promues en preuves typées par ce protocole.
4. Mesurer l’indice lexical DEMAND uniquement pour une forme reconnue ; ne pas comparer un span de proposition sémantique à une ancre lexicale comme s’il s’agissait du même objet.
5. Une citation/disclaimer pertinent ne devient jamais NOT_REQUIRED ni applicable.
6. Rapporter le refus financier séparément et exclure DPGF du dénominateur de rappel.

Le préflight SQL, les champs legacy exacts et l’implémentation de l’adaptateur restent à qualifier. Aucun appel au parseur sur ce gold n’a été effectué. Le gel de préparation concerne les données et le protocole ; le futur gel de mesure devra également fixer code/adaptateur/profil/tests avant toute observation.

## Plan minimal et preuves à produire

1. Caractériser les spans DEMAND de l’existant et les refus multiple/tronqué, sans changement de comportement.
2. Contre-lire le nouveau gold sémantique sans appeler le parseur, vérifier identité/portée/extraits/hash/budgets et conserver les réserves.
3. Vérifier la préparation et son refus par la CLI, lancer la suite sans DB appropriée aux seuls tests/documents, lint/format et scan ciblé ; conserver diff et hashes.
4. Mettre à jour le plan unique et l’index. La suite opérationnelle demeure le mapping, le préflight SQL, le gel et la mesure, sans activation.

TDD rouge/vert de production non applicable ici : aucun comportement de production n’est modifié. Les tests ajoutés caractérisent l’existant et vérifient les données ; aucun rouge artificiel ni qualification des nouvelles questions par le parseur n’est utilisé.

## État de vérification

- **44 ciblés verts** :42tests intention (dont14caractérisations ajoutées) et2tests de préparation/refus CLI. Ils prouvent les spans lexicaux existants, les refus multiple/tronqué, les hashes/régions/faits/portées/budgets et l’absence de chargement d’encodeur par la CLI sur ce fichier. Ils ne prouvent aucun rappel sur les nouvelles questions.
- **2438 tests sans DB réussis,845désélectionnés,1warning** en39,96s. Warning historique Starlette/httpx. La première exécution sandbox est restée bloquée après7cas dans le TestClient/AnyIO ; diagnostic borné30s avec pile conservée, runner identifié interrompu puis terminé, relance hors sandbox bornée180s réussie. Cette interruption n’est pas un PASS ni un échec produit.
- Ruff et format2fichiers verts ; mypy2sources sans erreur ; `git diff --check` vert. Aucun code de production, profil, moteur, CLI, schéma, dépendance ou UI changé. Les preuves précédentes3267backend/90ciblés/5SQL restent historiques : **suite DB non rejouée** pour cette préparation de tests/données/docs.
- Semgrep1.179.0 :225règles/2fichiers de tests,0finding/0erreur. Premier téléchargement de règles bloqué sous sandbox, relance autorisée réussie ; code analysé localement, aucun résultat envoyé. Scan borné, pas audit sécurité de tout le WIP.
- detect-secrets ciblé : hashes SHA256 de provenance uniquement, vérifiés et triés dans les preuves. Ni secret réel ni modification de baseline.
- Contre-lecture indépendante sans moteur : deux P2 corrigés avant gel de préparation (obligation UNKNOWN séparée des faits certains ; citation/disclaimer pertinent sans dispense déduite). Contre-revue sans réserve bloquante sur les corrections. La revue est technique, pas une validation humaine métier.

Fichiers de cette tranche : présente note, `backend/tests/application/test_rc_query_intent.py`, `backend/tests/ops/test_rc_generalization_preparation.py`, `backend/tests/fixtures/knowledge/rc_generalization_preparation_v1.json`, index et plan actifs ; un lien d’addendum dans le dossier v10 historique. Aucune source/prévision métier existante réécrite. Préparation gelée par SHA256 dans les preuves privées `~/.local/share/smartao-proofs/rc-anchor-preparation-20261018/` :état avant, logs ciblés/nonDB/incident, scan/triage, manifeste préparation et conservation WIP.

Méthode appliquée : Superpowers using-superpowers/brainstorming/revue ciblée, ECC verification-loop. Caractérisation de l’existant, pas changement de production nécessitant un rouge TDD. Graphify consulté (graphe ancien sans le WIP), Serena déjà activé dans cette session ; lecture ciblée suffisante sans nouvelle navigation sémantique. Aucun API/SDK nouveau pour Context7, UI pour OpenDesign/Impeccable/navigateur, ou besoin borné de Jev/Manus. Aucun conteneur/base créé.

A1 non admis, A2 générique HOLD, NO-GO public ; v7/v8/v9 conservés, v10 non activée. DPGF non évaluable. Sources multi-sujets et conditions tronquées non couvertes conservées UNKNOWN. Aucun commit/push/reset/clean/stash.

Prochaine étape : ESSAIS DCE — adapter le banc au gold sémantique préparé, valider sa représentabilité SQL, puis geler et mesurer sans réglage après observation; distinguer rappel documentaire, contrat fermé et sécurité. Conserver les sources multi-sujets et conditions tronquées non couvertes en UNKNOWN, v7/v8/v9 et v10 non activée. DPGF non évaluable; A1 non admis, A2 générique HOLD et NO-GO public maintenus.

Miroir Basic Memory : lecture réussie ; écriture refusée par la revue automatique, qui classe la destination comme externe et exige une autorisation explicite pour ce contenu privé (statut/chemins/preuves). **Non synchronisé**, aucune écriture de contournement. Résumé minimal proposé conservé dans les preuves locales pour décision utilisateur. Contrôle final :48tests ciblés+documentaires verts ;4fichiers préexistants modifiés dans le périmètre,aucun fichier de départ manquant,code de production et gel de préparation vérifiés identiques.


Mise à jour du miroir : après autorisation explicite de l’utilisateur, le résumé minimal approuvé a été ajouté dans Basic Memory, projet `smart-ao-v8`, note « SMART AO - Plan global de conception et réalisation ». Relecture confirmée, une seule occurrence ; synchronisation de ce résumé réussie. Le refus antérieur ci-dessus reste historique. Aucun autre contenu envoyé.


## Addendum — banc exécuté, préparation originale conservée

Le [banc sémantique additif](RC_GENERALISATION_BANC_SEMANTIQUE_2026-10-18.md) a validé SQL,gelé et mesuré un dérivé aux annotations identiques. Résultat0/17couvertes avant toute lecture/encodage ;ancienne préparation etmesures v10préservées,candidatHOLD. Voir le nouveau dossier pour les contrôles,incidents etlimites ;plan seul statut courant.
