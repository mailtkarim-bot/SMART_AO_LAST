# RC — intentions préfixées et impératifs candidats v9 — 18/10/2026

## AS-IS

V8 opt-in : jeu11 deux intentions omises (lot en tête, formulaire au passif), impératif source non projeté. HEAD30f2693, branche codex/reconcile-smartao-20261009; WIP préservé. Plan global seul statut opérationnel.

## Risques et points d’insertion

Conserver v7/v8 impose une politique v9 et des options explicites par défaut inactives dans les fonctions existantes. Requête originale encodée inchangée. Réutiliser RcSignalAnchor, RcQueryLot et project_rc_conflicts. Risques : perte des offsets UTF8, lot implicitement transféré, impératif cité/conditionnel pris pour obligation certaine, propagation d’un sujet à plusieurs demandes.

## Plan minimal et tests à ajouter

- [x] Rouge puis vert : deux formes de requête, ancres/hash inchangés; ambiguïtés, budget et compatibilité v8.
- [x] Impératif source fermé à sujet unique : joindre/fournir/remettre/présenter un document ou effectuer/réaliser une visite; ancres sujet/directive/lot; refus citation, négation et condition non qualifiée, lot absent/ambigu et segment tronqué.
- [x] Intégration v9, tests typed-rescue, isolation, invalidation, financier, CLI; revue.
- [x] Nouveau jeu12 gelé, E5 CPU/SQL, aucune retouche après mesure; contrôles ciblés et suite appropriée, sécurité, nettoyage.
- [x] Case/journal/prochaine étape/index et Basic Memory.

Aucun moteur actif remplacé, aucune dépendance/migration/UI. UNKNOWN/REVIEW_REQUIRED et sources conservés; DPGF non évaluable,A1nonadmis/A2HOLD/NO-GOpublic. Aucun live/corpus réel/VPS/P3/commit/push/déploiement.

## Implémentation et preuve TDD

Politique `rc-imperative-v9` additive, profil E5 CPU identique sauf identité de politique. `extended_forms=False` et `imperative_sources=False` conservent le comportement antérieur. Les profils v7/v8 et le jeu11 gardent leurs empreintes.

- `rc_query_intent.py` reconnaît un préfixe explicite « Pour le lot …, » ou « : » et le formulaire DC1/DC2 au passif. Les ancres byte UTF8 sont calculées sur la requête brute avec décalage prouvé ; l’encodage reçoit la chaîne originale.
- `rc_candidate_conflicts.py` reconnaît un impératif simple à un seul sujet : document DC1/DC2/mémoire ou visite. Portée lot unique explicite et ancres `SUBJECT/DIRECTIVE/LOT`, hash de source/segment, page et région conservés. Aucun transfert implicite de sujet ou lot.
- `candidate_retrieval.py` ne choisit cette extension que pour v9 ; refus financier avant lecture/parseur/encodeur, intention non couverte refusée avant accès aux sources, rescues typés et revalidation des sources existants réutilisés.
- La CLI exige un gold indépendant des ancres impératives et refuse les ancres supprimées ou déplacées. Ces annotations ne sont pas fournies au service ou à l’encodeur.

26 régressions rouges initiales puis vertes ; un rouge CLI pour la nouvelle preuve, un rouge pour une ancre entièrement supprimée, trois rouges de préambules trouvés par revue indépendante. 35 nouveaux cas application, un CLI et un SQL (37 nouveaux). Le périmètre pur final compte 103 tests réussis. Le premier ciblé incluant SQL compte104 réussites avant les trois tests de préambule.

La contre-revue confirme le refus des préambules négatifs ou illustratifs. La règle est volontairement conservatrice : tout préambule antérieur non blanc non qualifié bloque l’impératif, même bénin. L’absence d’interprétation de préambules, négations ou conditions complexes à distance n’est pas une preuve d’analyse complète.

## Jeux gelés et limites d’annotation

Jeu12 :19 documents/25questions. Le document présenté comme étranger à l’Affaire utilisait la version active de cette Affaire. Dans le schéma réel, les documents appartiennent à une version, et non directement à une Affaire ; cette donnée représentait un document partagé légitimement visible. Le rapport SQL jeu12 est conservé comme diagnostic non qualifiant ; aucune fuite SQL n’est démontrée par cette fixture incohérente.

Le gel corrigé jeu13 change uniquement la version de ce document pour représenter l’exclusion voulue. Questions, gold sémantique et code sont inchangés. Les marqueurs de requête j12 sont conservés. Aucun réglage du moteur après mesure ; manifeste de17fichiers plus SHA du jeu13 et diagnostics archivés.

Sur jeu13, les dix cas nominaux des nouvelles formes sont complets en v9, contre zéro en v8. Le compteur brut donne11/14 questions positives évaluables complètes, rappel source73,33% financier inclus, zéro candidat sur10 questions attendues sans réponse. Trois besoins sont manqués : impératif conditionnel, source multi-sujet et lot écrit « n° ». Toutes les réponses métier restent UNKNOWN.

Le scoreur de clauses donne11/14 occurrences attendues détectées (contexte inclus),10projetées pertinentes,0extra projeté/valeur connue fausse/type connu faux/surcertitude,1contexte horsgold. Ce dernier est la clause DC2 non exigée du lot647 dans la question sans lot : preuve conservée hors projection, applicabilityUNKNOWN. Son omission du gold de cette question est une limite d’annotation, pas une preuve de source hors sujet. Ne pas présenter ce score global comme une mesure exhaustive et indépendante de toutes les omissions.

Cinq gates restent fausses : critical_complete, evidence_recall_at_5, rc_unknown_refusals, review_signals et specific_intent_exact. Cette dernière porte sur la compatibilité legacy de la question horaire : son gold attend NONE alors que le parseur refuse en UNKNOWN, cohérent avec la demande temporelle non couverte ; la gate fermée rc_query_intent_exact est vraie. Le gold gelé n’est pas retouché pour rendre les gates vertes. Une nouvelle qualification devra annoter exhaustivement les questions sans lot et expliciter les attentes des deux contrats d’intention.

## Provenance, isolation et ressources

69 ancres requête,54 occurrences de preuves source et150 occurrences d’ancres impératives confrontées aux octets ;19 fragments SQL, textes/hash/version/page exacts. Les occurrences peuvent répéter une même preuve. Les6contrôles SQL sont vrais : source initiale, changement d’extraction pendant requête, exclusion du fragment périmé, déréférencement de version, absence de source courante, historique préservé.

E5CPU réel épinglé et lecteur SQL : p95 chaud63,527ms, première requête28,383s, RSS863,191MiB et cgroup823,473MiB sous plafond1200MiB ;168statements et12validation,780,455ms de validation. Mesures descriptives sur hôte partagé avec suite globale ; référence v8 source virtuelle et v9SQL ne séparent pas politique et transport. La première requête v8 est refusée avant encodage, ses2,349ms ne sont pas un démarrage modèle.

## Contrôles et preuves

Ruff backend/scripts et mypy636 sources réussis ; format8fichiers et diff whitespace vérifiés. Semgrep1.179.0 :225règles sur8fichiers,0finding/0erreurJSON, aucun avertissement spécifique ; premier téléchargement des règles en timeout, une relance réussie. Détection secrets1.5.0 :15 empreintes publiques (modèle et SHA de sources synthétiques) vérifiées et triées précisément ; anciennes entrées/plugins/filtres de baseline inchangés. Aucun secret ajouté.

Première suite globale interrompue après951réussites/22erreurs d’initialisation et1warning : saturation WAL du tmpfs512MiB et récupération PostgreSQL, pas22assertions produit rouges. Base de tests recréée avec WALmax64MiB/min32MiB et checkpoint30s, même plafond CPU/RAM/tmpfs ; suite complète relancée. Le résultat final est consigné ci-dessous après achèvement.

Preuves privées : `~/.local/share/smartao-proofs/rc-imperative-v9-20261018/` (rouges/verts, copies avant, manifests, gold/rapports, fragmentsSQL, audit.py/verification.json, scans, logs et états conteneurs). Méthodes Superpowers using-superpowers/cadrage/TDD/revue/vérification et ECC verification-loop. Graphify consulté sans nœud correspondant puis lecture ciblée ; Basic Memory miroir. Pas de navigation sémantique Serena, nouveau contrat fournisseur Context7, Jev/Manus, UI/OpenDesign ou navigateur nécessaires à cette tranche.

## Clôture technique locale bornée

Politique rc-imperative-v9 additive codée : lot en tête, formulaire au passif et impératif simple à sujet/lot explicites, ancres exactes requête et source; v7/v8 et requête brute conservés. 37nouveaux cas,103purs finaux verts; backend global3236réussites/2warnings/814,81s/exit0. Première globale interrompue951réussites/22erreurs initialisation après saturation WAL tmpfs : base recréée/WALborné et suite entièrement rejouée; aucun défaut produit maquillé. Ruff backend/scripts,mypy636,format8,diff verts. Semgrep1.179.0/225règles/8fichiers0finding/0erreurJSON,sanswarning spécifique après une relance de téléchargement; secrets15empreintes publiques exactement triées,baseline historique conservée. Revue indépendante : préambule illustratif/négatif corrigé après3rouges; contre-revue code/gold/métriques réalisée. Jeu12 diagnostic invalide côté SQL (pièce dite autreAffaire mais version partagée), pas preuve de fuite; jeu13 corrige uniquement la version étrangère sans réglagemoteur ni changement questions/attentes. Dix cas nominaux ciblés complets v9 contre0v8; compteur brut11/14positives évaluables,11/14occurrences clause détectées/10projetées. Trois omissions :conditionnel,source multi-sujet,lot n°. Zéro candidat sur10cas attendus sans réponse. Gold sans lot incomplet : clause DC2nonexigé pertinente horsprojection mais comptée horsgold; ne pas revendiquer fauxpositif métier ni score exhaustif. Gold legacy horaireNONE contre refusUNKNOWN :closedintentDATE_TIME/UNSUPPORTED exact,gatelegacyfausse. Cinq gates fausses/HOLD/admittedfalse;6validationsSQL vraies,69ancres requête/54occurrences preuves/150ancres impératives/19fragmentsSQL vérifiés. P95chaud v9SQL63,527ms,première requête28,383s,RSS863,191MiB/cgroup823,473MiB sous1200;168statements+12validation,mesure descriptive hôte partagé. 17SHA gelés et SHAjeu13 conservés. Deux bases jetables head0136→base/Alembic0;5conteneurs de mesure et1de tests retirés (premier PG saturé remplacé auparavant). Aucun nouveau schéma/dépendance/UI/factory/moteur actif,aucun corpus réel/live/VPS/P3/déploiement/commit/push;HEAD30f2693/WIP préservés. A1nonadmis/A2HOLD/NO-GOpublic.

Les deux avertissements globaux sont Starlette/httpx et Pydantic Field.alias. Aucune UI/Web ni qualification live n’a été rejouée ; aucune analyse DCE entière ou admission Golden n’est démontrée. Le candidat reste un outil de lecture sourcée sans effet métier automatique.

Prochaine étape : ESSAIS DCE — compléter indépendamment le gold RC sans lot et les attentes des deux contrats d’intention, puis corriger sur développement les impératifs avec lot « n° » et qualifier les conditions impératives avec ancres et UNKNOWN; requalifier sur un nouveau jeu gelé sans activer le candidat. Conserver v7/v8/v9 et les demandes ou sources multi-sujets non couvertes en UNKNOWN; DPGF reste non évaluable. A1 non admis, A2 générique HOLD et NO-GO public maintenus.
