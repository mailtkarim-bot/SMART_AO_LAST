# RC — cadrage d’intention et abstention — 19 octobre 2026

## AS-IS, risques, périmètre

Branche/HEAD du checkout principal vérifiés :`codex/reconcile-smartao-20261009`/`30f26934430095632000a1d82519f61dbb4c6411`. WIP conservé. Le banc mesuré précédent est une référence immuable :aucun cas, seuil ou expression de ce banc ne sert de corpus de développement ni de test de calibration. Son résultat ne qualifie pas E5 ;il localise un refus avant accès aux sources.

Le travail présent cadre le reconnaisseur futur et prépare ses évaluations. **Aucun reconnaisseur, profil, moteur ou CLI n’est modifié ou activé.** Risques :addition de patrons pour réussir un gold connu, classification de mots sans comprendre la demande, négation transformée en dispense, contexte/lot inventé, confiance de modèle prise pour une preuve, requalification silencieuse d’une abstention en réponse métier.

Les insertions futures restent dans la reconnaissance candidate d’intention et son branchement opt-in ;la projection des sources et ses protections ne sont pas élargies par ce cadrage. Le contrat d’intention fermée actuel est conservé comme référence. Aucun schéma/dépendance/SDK/API/UI nouveau à ce stade.

## Décision de mécanisme — proposition à confirmer

| Option | Apport possible | Limite/coût |
|---|---|---|
| Local compositionnel déterministe — recommandé pour la première tranche |assembler sujet, demande et portée à partir d’indices explicites, sans exiger une seule phrase complète ;aucune dépendance ou exécution distante nouvelle |couverture toujours bornée ;les combinaisons non prouvées doivent s’abstenir ;pas une compréhension générale du français |
| Classifieur sémantique local |évaluer une généralisation au-delà des indices explicites |qualité et calibration inconnues ;profil de reconnaissance distinct à geler ;similarité dense non suffisante comme preuve d’intention |
| Classifieur LLM/Jev borné |proposition structurée parmi des classes fermées |disponibilité/confidentialité/coût/latence à décider ;aucun envoi réel ni pouvoir métier automatique ;validation des ancres et abstention obligatoires |

Le fichier `backend/tests/fixtures/knowledge/rc_intent_recognition_design_contract_v1.json` fixe les enums,priorités,raisons,gates et références de politique de ce cadrage proposé. Il ne constitue pas une nouvelle API.

Question soumise à l’utilisateur sur le mécanisme. Tant qu’elle reste ouverte, le choix local est **une recommandation**, pas une décision approuvée. Le corpus et les obligations d’abstention ci-dessous sont indépendants de ce choix ;aucune implémentation n’est autorisée par une réussite de cadrage.

## Contrat observable proposé

1. **Sens distinct de la réponse.** Classer ce que la requête demande, jamais ce qu’un candidat doit réellement faire. « Peut-on se dispenser de X ? » vise OBLIGATION ;il ne démontre pas NOT_REQUIRED. Toute réponse métier reste UNKNOWN.
2. **Classes bornées.** Conserver les sujets existants VISIT/VISIT_SITE/VISIT_MEDICAL/DC1/DC2/MEMOIRE_TECHNIQUE/VARIANTS/UNKNOWN. Une visite générique n’est pas renommée SITE et un type médical n’est pas inféré depuis un contexte de chantier. Un qualificatif de visite inconnu n’est pas supprimé pour forcer une classe générique couverte ;sujetUNKNOWN et abstention tant que ce type n’est pas explicitement spécifié.
3. **Demande unique.** L’étiquette technique historique OBLIGATION recouvre ici une question sur le caractère requis, facultatif, permis ou interdit d’un sujet du catalogue ;elle ne signifie pas une obligation positive établie. Pour VARIANTS, « admise/recevable » vise seulement cette demande de permission, jamais un contrôle juridique autonome de recevabilité de l’offre. Une telle demande reconnue peut être COVERED, sans certifier sa réponse. DATE_TIME et LOCATION peuvent être identifiées mais demeurent UNSUPPORTED dans le premier périmètre de retrieval d’obligation. Toute autre demande reste UNKNOWN/UNSUPPORTED, pas rabattue vers OBLIGATION pour augmenter le rappel.
4. **Un seul sujet et une seule portée explicites.** Plusieurs sujets/demandes/lots, coordination ou alternative ambiguë :AMBIGUOUS, aucune recherche/projection typée. Aucun choix du sujet le plus probable. Absence de lot :scopeUNKNOWN autorisé pour une demande unique ;pas de lot inventé ni d’opposition entre lots. Un lot invalide ou ambigu ne devient pas portée implicite. Le périmètre numérique initial reste1–999 comme le lecteur courant ;autres formats/hors plage ne sont pas normalisés silencieusement.
5. **Provenance requête.** Texte original et SHA256 ;offsets UTF-8 `[start,end)` et extraits exacts, sans paraphrase inventée. Les éléments de sujet/demande/portée doivent être justifiés dans la requête. Une synonymie de sujet doit être déclarée dans une version de règles ou de reconnaissance et conservée avec son indice original. Le contrat lexical existant demeure une référence ;une autre convention de span doit être versionnée, jamais appliquée rétroactivement.
6. **Cohérence compositionnelle.** La cooccurrence d’un nom de pièce et du mot « obligatoire » ne suffit pas :citation, comparaison, hypothèse, phrase tronquée, demande métalinguistique ou texte donnant des instructions au modèle ne deviennent pas une question d’obligation couverte.
7. **Conditions et absence d’information.** Une condition tronquée garde UNKNOWN. Une demande conditionnelle complète reste hors couverture initiale (UNSUPPORTED) ;aucune conclusion d’obligation inconditionnelle. Référence à un échange antérieur, pronom sans antécédent explicite dans la requête, sujet ou sens contradictoire :UNKNOWN/AMBIGUOUS, sans compléter depuis le DCE ou une autre session.
8. **Source distincte de l’intention.** Même reconnue, une question ne rend pas une source multi-sujets/tronquée interprétable. Les règles de protection des sources restent inchangées ;conditions sourcées UNKNOWN, source/case/version/hash/locator conservés et revalidation avant résultat.
9. **Financier et confidentialité.** Refus financier avant appel au reconnaisseur coûteux/retrieval ;DPGF non évaluable. Pas de texte/signal/trace de sources étrangères, privées, obsolètes ou partielles transmis à un classifieur comme moyen de choisir la portée. Aucun appel LLM/fournisseur dans le domaine.
10. **Erreurs d’exécution.** Budget de requête existant, entrée invalide refusée ;timeout/indisponibilité/format invalide/ancres fausses/confiance insuffisante :abstention explicite,aucun fallback qui élargit le périmètre. Retry de lecture identique et aucune écriture métier. Pour un modèle, la confiance seule ne suffit jamais à contourner les refus structurels.

L’enveloppe de provenance future devra identifier le mécanisme et sa version, et distinguer sujet/demande/portée/coverage/reason. Ce n’est pas une modification présente du dataclass public ou un nouveau port générique.

## États, priorités et ancres — règles proposées avant implémentation

Ces règles sont normatives pour le **cadrage proposé** ;elles ne changent pas les contrats v7–v10. Les cibles sont décrites par une intention nullable et une raison d’enveloppe. Les champs sujet/demande/coverage/scope_state sont des chaînes énumérées ;lot est un entier JSON1–999 ou null (jamais chaîne décimale ou booléen),comme le type de portée existant. Les offsets sont des entiers JSON,les extraits des chaînes brutes. Les étiquettes de raison sont proposées pour le futur adaptateur, pas ajoutées aux types publics actuels.

| Sortie | Composantes conservées | Recherche autorisée |
|---|---|---|
| Erreur de budget/entrée |pas d’intention ;INVALID_QUERY_BUDGET |non |
| FINANCIAL_SCOPE_REFUSED |pas d’intention,ancres vides,aucune trace/revue |non |
| UNKNOWN |sujet unique/lot explicitement prouvés peuvent rester ;demandeUNKNOWN si non établie |non |
| AMBIGUOUS |aucun choix parmi sujets/lots concurrents ;demandUNKNOWN ;indices bruts exacts conservables |non |
| UNSUPPORTED |un sujet unique et une demande identifiés ;condition complète ou demande temporelle/spatiale hors périmètre |non |
| COVERED |un sujet,demandOBLIGATION,scopeCANDIDATE explicite ou UNKNOWN sans lot mentionné |seulement comme intention candidate ;source/permissions et applicabilité restent à vérifier |

Ordre déterministe proposé :

1. Type/entrée/budget existants (vide,>2000caractères,top_k hors1–50) refusés avant tout travail. Une entrée financière invalide ne contourne pas ce contrôle.
2. Garde financière canonique de `retrieval.py` utilisée par `CandidateRetrievalService.retrieve` :même politique lexicale sur **toute la requête**, y compris requête mixte ou mention citée ;pas d’exception sémantique inventée. Elle refuse avant reconnaisseur coûteux,lecteur,encodeur,index. Référence de fichier/hash et motif exact dans le protocole ;termes actuels à frontières de mot :prix,montant,marge,coût/cout,bpu,dpgf,trésorerie/tresorerie,financement,rentabilité/rentabilite,devis,sans distinction de casse. Ne pas inventer de normalisation ni de pluriel implicite. Les autres formulations financières ne sont pas couvertes par la preuve de ce garde ;aucune interprétation permissive ne doit en autoriser le retrieval. Ce cadrage ne crée pas une politique financière nouvelle.
3. Troncature manifeste :UNKNOWN,raisonTRUNCATED ;aucune reconstruction. Préserver seulement des composantes explicites, pas une demande supposée.
4. Ambiguïté structurelle :AMBIGUOUS ;raisons ordonnées MULTIPLE_LOTS,puisMULTIPLE_SUBJECTS,puisMULTIPLE_DEMANDS. Le comptage porte sur les **demandes sémantiques actives** :deux marqueurs du même statut ne deviennent pas automatiquement deux demandes ;des demandes d’heure et d’obligation restent deux demandes même avec un seul sujet. Les alternatives/coordonnées de lots ne sont pas résolues ;un numéro de lot invalide donneAMBIGUOUS/INVALID_LOT avant les ambiguïtés de nombre.
5. Citation/métalangage/instruction de réponse/référence non résolue ou sujet non identifiable :UNKNOWN. Aucun remplissage depuis le DCE ou une session. Une citation n’est pas traitée comme une demande active simplement parce qu’elle contient un marqueur d’obligation.
6. Une condition complète sur une demande unique identifiable :UNSUPPORTED. Sans sujet/demande identifiés,UNKNOWN. Une date ou un lieu demandé avec sujet unique identifiable :UNSUPPORTED ;un pronom sans référent n’est pas rendu compréhensible par un mot temporel.
7. Sinon,uniquement une question cohérente mono-sujet/mono-demande de la famille technique OBLIGATION peut devenirCOVERED ;toute hésitation restante donneUNKNOWN. Erreur/timeout/sortie invalide après appel éventuel au reconnaisseur :UNKNOWN,aucune recherche.

Une promotion indue est un événement observable :COVERED sur un cas attenduUNKNOWN/AMBIGUOUS/UNSUPPORTED/financier ;appel lecteur/encodeur/index malgré ce refus ;ou projection typée d’une source protégée. Ces événements sont rapportés séparément. Une intention correctement reconnue ne suffit pas à autoriser la projection d’une source.

Convention d’ancres proposée :`lexical-cue-v1`, référence au dossier `RC_ANCRES_VISITE_PREPARATION_GENERALISATION_2026-10-18.md`. Les ancres sont des indices textuels,certainement pas une reformulation. Une sortieCOVERED a exactement1SUBJECT et1DEMAND ;LOT est unique si scopeCANDIDATE. Pas de concaténation de spans discontinus. Si la négation est discontinue,le spanDEMAND continu doit englober les éléments pertinents,sans supprimer la négation ;si ce span ne peut être prouvé,abstention. Les cas à motifs discontinus non spécifiés restent hors première tranche. Pour les refus,des SUBJECT concurrents peuvent être conservés,mais aucuneDEMAND unique n’est certifiée ;pas d’ancreLOT choisie parmi des portées coordonnées.

Critère initial de comparaison :égalité exacte avec les ancres annotées,ordre source `(start,end,signal)`,UTF-8/SHA/extrait valides. Pas d’expansion a posteriori de l’ensemble admissible pour faire réussir une sortie. Si plusieurs segmentations légitimes existent,l’annotation doit les déclarer avant gel dans une nouvelle révision explicite,ou classer le cas comme non spécifié ;ne pas en déduire une équivalence silencieuse. Les composantes sujet/demande/coverage/scope_state/lot sont comparées exactement,même sur les abstentions ;la sûreté d’abstention est aussi rapportée séparément pour distinguer un refus sûr d’une reconnaissance exacte.

Mesure prévue :4passages même ordre,1initial et3chauds,p95 par rang supérieur `ceil(.95*n)` sur tous les appels chauds,refus compris. Rapporter séparément durée des réponses refusées,lecture/reconnaissance/encodage/retrieval réellement effectués,initialisation et taille des groupes. Trois décisions répétées identiques et compteurs de travail sont attendus ;pas de revendication de performance retrieval lorsqu’il n’est pas appelé.

Exposition du challenge :consultation de ses textes par le développeur,diagnostic d’une sortie ou correction d’une annotation compte comme ouverture. Les validations automatiques de hash/structure/offsets et de non-chevauchement, sans exposer les textes au contexte d’implémentation, ne sont pas une consultation de contenu ;elles ne doivent jamais imprimer les cas sur échec. Avant mesure,une ambiguïté de contrat peut conduire à révision d’annotation indépendante,avec ancien fichier/hash conservé et **aucun candidat ni sortie consultés**. Après ouverture pour qualification,toute adaptation du candidat exige nouvelle version et nouveau challenge ;l’ancien devient historique, jamais recalibré en place. Le scellé est une discipline de séparation des rôles, pas une frontière de sécurité ni une preuve statistique.

## Développement distinct et plan minimal

- [x] Matérialiser un corpus de **développement** nouveau, annoté sans appeler un moteur ;couvrir reformulations mono-sujet et couples contradictoires, négation interrogative, demande temporelle/spatiale, coordination, citations, conditions, lot manquant/invalide et financier.
- [x] Relire contrat et données indépendamment ;les exemples et étiquettes sont des cibles proposées, pas des sorties mesurées. Vérifier UTF-8/hash/séparation des corpus.
- [x] Préparer un challenge indépendant à partir du seul contrat d’abstention, sans lecture du développement, du reconnaisseur ou du gold mesuré. Le garder scellé procéduralement jusqu’au gel du candidat ;pas une frontière de sécurité ni une indépendance statistique garantie.
- [x] Fixer métriques et gates avant implémentation ;valider structure/tests/documentation et geler la préparation. Choix du mécanisme et éventuelle implémentation restent distincts de la mesure.

## Nouvelle qualification — protocole avant observation

Deux étages :d’abord intention seule sur données synthétiques, puis retrieval/SQL avec sources et protections inchangées, quand le candidat est prêt. Aucun score de l’étage1 ne qualifie l’étage2. Les faits et obligations sources demeurent dans leur contrat propre.

- Rapport par famille, confusion sujet/demande/lot, couverture et abstention. Ne pas compter une abstention comme une reconnaissance correcte d’un positif.
- Gates strictes :0promotion des négatifs/ambiguïtés/protégés ;0fausse ancre ;0portée inventée ;0effet métier/fuite ;financier refusé,UNKNOWN métier partout ;répétitions identiques et refus d’erreur sûrs.
- Gate de couverture proposée avant test :au moins90% des16cas de développement annotés COVERED (donc au moins15/16),100% des12refus structurels UNKNOWN/AMBIGUOUS et du refus financier. Les3demandes UNSUPPORTED sont évaluées séparément sur leur identification correcte et absence de retrieval, sans les compter dans la couverture OBLIGATION. Ce seuil local n’est ni une garantie générale ni un droit d’activer le candidat. Le seuil90% de développement ne se transfère pas au challenge :gate indépendante proposée100% des positives ciblées et100% des refus/unsupported/financier,avec0promotion/0fausseancre/0portéeinventée. Le challenge indépendant publiera tous les échecs et dénominateurs, sans compensation d’un faux positif par du rappel.
- Toute calibration (règles/prototypes/prompt/seuils) utilise seulement développement. Gel code/profil/données/tests/règles avant ouverture du challenge. Après observation,aucun réglage en place :nouvelle version et nouveau challenge si une modification est nécessaire.
- La latence du reconnaisseur et celle du retrieval seront séparées ;les compteurs de lectures/encodeur/interpréteur seront publiés. Budget initial candidat :p95 de l’appel complet ≤1500ms, limite interactive déclarée par le banc actuel ;temps du reconnaisseur et du retrieval publiés séparément. Un rejet avant lecture ne devient pas une preuve de latence retrieval. Pas d’augmentation silencieuse de ce budget. Un service externe exige un choix de confidentialité/budget avant branchement.

A1 non admis,A2 génériqueHOLD,NO-GOpublic ;v7/v8/v9 préservés,v10nonactivée,DPGFnonévaluable. Aucuncommit/push/reset/clean/stash ni nouvelle dépendance.


## Préparation matérialisée — aucune qualification exécutée

- Développement :`backend/tests/fixtures/knowledge/rc_intent_development_design_v1.json`,32cibles prospectives,16COVERED/3UNSUPPORTED/5AMBIGUOUS/7UNKNOWN/1refusfinancier ;3protections de source et5situations d’erreur d’exécution proposées. Ce sont des annotations, pas des reconnaissances réussies. Aucun candidat ne les a reçues.
- Contrat machine lisible :`rc_intent_recognition_design_contract_v1.json` dans le même dossier,étatPROPOSED_PENDING_OWNER_CHOICE,mécanismechoisi=null. Il fixe les classes/raisons/priorités/types,référence la garde financière réelle par hash et conserve les gates proposées.
- Qualification d’intention seule :`rc_intent_independent_qualification_protocol_v1.json`. Ce protocole fixe avant observation100%des16positives ciblées,4UNSUPPORTED correctement identifiées sans recherche,11abstentions structurelles et1financier ;0promotion/0fausseancre/0portéeinventée. Ce n’est pas le seuil15/16de développement. Le futur retrieval/SQL nécessitera une qualification distincte ;ce challenge ne le qualifie pas.
- Challenge scellé :`rc_intent_independent_challenge_v1.sealed.json`,32propositions,16COVERED/4UNSUPPORTED/5AMBIGUOUS/6UNKNOWN/1financier ;au moins2positives par sujet,2positives avec portée explicite,14positives sans portée. Couverture des formats de lot limitée, pas validation générale de tous les lots.

### Séparation et contre-lectures

Un relecteur de spécification, démarré sans historique de session, a proposé les contre-tests à partir du seul contrat et de sa référence lexicale. Il n’a pas lu le développement, le code reconnaisseur, les golds mesurés ni leurs sorties. La référence autorisée contenait des agrégats historiques :cette exposition est déclarée, donc aucune indépendance statistique/aveugle n’est revendiquée. Un second relecteur indépendant n’a vu que contrat et challenge pour vérifier annotations et spans. Le coordinateur n’a pas reçu les textes/identifiants des cas :copie brute et vérifications statiques sans affichage de contenu seulement.

Les versions provisoires originales et leurs hashes sont conservés en preuves privées. Avant tout candidat,les revues ont clarifié les états/priorités/conventions et corrigé une intention et11ancres de la première proposition ;8contre-tests ont complété les familles,puis2ont complété la portée positive. Une dernière validation a révélé deux valeurs de lot représentées comme chaînes décimales :le contrat a explicité entier JSON|null,et seuls ces2types ont été corrigés,sans changement de texte/ancres. L’erreur regroupait type/bornes sous un message générique ;la cause réelle était le type,les valeurs numériques étaient déjà dans la plage. Aucun ajustement depuis une sortie de candidat n’a eu lieu. Contre-revues sans défaut bloquant d’annotation restant.

Le scellé final et le développement sont disjoints par texte canonique,même après remplacement des numéros de lots. Cette vérification ne démontre pas une indépendance sémantique ou statistique. Le fichier resteheld_out=false et aucune CLI de mesure existante ne peut l’utiliser par erreur :refus avant encodeur vérifié. Toute consultation diagnostique ultérieure doit être consignée comme exposition et le futur candidat doit être gelé avant son ouverture.

### Vérifications de cette tranche

- **5tests statiques réussis** :identités/hash/spans/types/raisons/budgets/références,frontière entre intention et protections source,absence de réutilisation exacte des requêtes mesurées (numéros neutralisés),intégrité du scellé/protocole,barrière CLI avant encodeur. Les messages d’échec du challenge restent génériques et ne révèlent pas ses cas.
- **2461tests sans DB réussis,846désélectionnés,1warning** en44,95s ;warning historique Starlette/httpx. Exécution bornée hors sandbox en raison du blocage TestClient/AnyIO déjà établi lors des tranches précédentes. Aucun nouveau blocage/test en échec sur cette campagne.
- Ruff/format et mypy1fichier verts ;`git diff --check` vert. Aucun code de production,dépendance,profil,schéma,API,UI ou service nouveau. TDD comportemental non applicable :pas de reconnaisseur implémenté ni modifié ;les tests vérifient les données et le protocole.
- Semgrep1.179.0 :225règles/1fichier de tests,0finding/0erreur. Premier téléchargement bloqué sous sandbox,relance autorisée bornée120s réussie ;analyse locale,pas d’envoi des résultats. Scan limité,aucun audit de tout le WIP revendiqué.
- detect-secrets :73signaux SHA256 de provenance synthétique,triés par champ/ligne ;baseline inchangée,pas une garantie globale d’absence de secrets.
- Ancien gel mesuré35fichiers vérifié identique. Les nouvelles données/contrat/protocole/tests sont gelés comme **préparation**,pas comme candidat ni mesure. Aucun appel de reconnaissance,model/embedding ou SQL sur ces cas ;aucune base créée. Les chiffres3301backend/152ciblés/6SQL de la tranche précédente restent historiques.

Preuves privées :`~/.local/share/smartao-proofs/rc-intent-framing-20261019/` — état de départ,revues et parents d’annotation,scellé et métainfo (ne pas consulter le contenu avant gel du candidat),manifest `preparation-freeze.json`,logs statiques/nonDB/types/scan/triage et conservation finale. L’autorité opérationnelle demeure le plan actif,les annotations sont proposées et ne valent pas validation métier humaine.

### Direction proposée et décision restante

Le mécanisme n’est pas choisi à la place du propriétaire. Recommandation :première tranche locale compositionnelle,déterministe,versionnée,opt-in,avec validation stricte des slots/ancres et refus avant toute recherche. Alternative locale sémantique ou LLM/Jev encore possible après arbitrage de calibration/confidentialité/coût. La question de préférence a été posée,aucune réponse reçue à la clôture de cette préparation ;aucune option préselectionnée dans l’UI n’est traitée comme accord.

Cette préparation est livrée pour revue. Avant implémentation,choisir le mécanisme et valider le cadrage proposé ;le choix seul n’est pas une approbation implicite d’un futur patch ou d’une activation. A1nonadmis/A2génériqueHOLD/NO-GOpublic,v7/v8/v9préservés,v10nonactivée,DPGFnonévaluable,UNKNOWNprotégé.

Méthode utilisée :Superpowers using-superpowers/brainstorming/revue,Matt Pocock grilling pour le choix ouvert,ECC eval-harness pour les critères avant implémentation et verification-loop pour les contrôles. Graphify consulté,graphe ancien insuffisant pour le WIP ;Serena déjà activé dans la session,sans besoin de navigation sémantique nouvelle. Aucun SDK/API nouveau pour Context7,UI pour OpenDesign/Impeccable,navigateur ou serviceJev/Manus appelé. Le skill contract-first lu n’a pas été appliqué :pas de frontière à consommateurs indépendants ni de nouveau schéma d’API.

Prochaine étape : ESSAIS DCE — choisir le mécanisme de reconnaissance et valider le cadrage proposé, puis établir le plan d’implémentation d’un candidat distinct opt-in sur le développement seul; ne pas ouvrir le challenge scellé avant le gel du candidat ni régler sur le gold mesuré. Conserver les demandes multiples et les sources multi-sujets ou tronquées non couvertes en UNKNOWN, v7/v8/v9 et v10 non activée. DPGF non évaluable; A1 non admis, A2 générique HOLD et NO-GO public maintenus.

Miroir Basic Memory :lecture réussie,mais ajout du nouveau résumé refusé par auto-review ;l’accord précédent portait sur un résumé antérieur et ne couvre pas explicitement ce nouveau contenu privé vers la destination considérée externe. **Ce cadrage n’est pas synchronisé.** Aucun contournement ;résumé minimal proposé conservé localement pour approbation,sans texte des cas scellés. Le plan et ce dossier restent à jour.

## Suite du cadrage — prototype isolé mesuré le19/10/2026

Préparation ci-dessus conservée comme historique. Le choix local compositionnel technique et la qualification aprèsgel sont consignés dans [RC_RECONNAISSEUR_COMPOSITIONNEL_V1_2026-10-19](RC_RECONNAISSEUR_COMPOSITIONNEL_V1_2026-10-19.md). Le challengev1 est désormais ouvert et historique ;aucune calibration du candidat après observation. CandidatHOLD et aucune activation/validation métier/Owner déduite. Le plan du dépôt seul fixe la prochaine étape.
