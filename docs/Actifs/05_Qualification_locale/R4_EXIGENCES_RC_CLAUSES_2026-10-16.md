# R4 — Chaîne des exigences RC par clause — 16 octobre 2026

## Résultat métier visé et statut

**Qualification technique locale acquise : moteur v5 codé et backend complet vert, 2 787 réussites, 3 avertissements, sortie 0.** Une seconde obligation, échéance ou condition dans un même fragment doit parvenir jusqu'aux exigences persistées, avec sa propre citation. Les signaux restent en attente de confirmation humaine; aucune date applicable, obligation juridique certaine ou analyse complète n'est déduite.

Le plan global reste l'autorité du statut. A1 non admis, A2 générique HOLD et NO-GO public maintenus.

## AS-IS / risques / points d'insertion

Reprise principale : branche `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`; 112 entrées WIP conservées, aucun reset/stash/clean, commit ou push. Graphify consulté avant recherche; index et tranche active relus, décisions Basic Memory vérifiées contre le dépôt. M2-027/029/035 imposent source/version/portée/état inconnu; le cahier interdit une fausse échéance certaine. Les analyses historiques sont append-only.

La plupart des règles de l'analyse RC v4 ne retenaient que le premier match d'un fragment. Les fenêtres larges mélangeaient aussi des clauses et la négation « ne doit pas » pouvait devenir REQUIRED_SIGNAL. La matérialisation existante recopiait donc fidèlement un ensemble de signaux incomplet.

**Insertion :** `application/analysis.py` uniquement pour le comportement de production. Réutilisation du service d'extraction, du dispatcher, du handler d'analyse et du materializer existants. Aucun nouveau moteur, framework, champ public, schéma, migration ou interface. Risques examinés : perte d'occurrence, condition séparée, fausse obligation, source tronquée, offsets UTF-8, doublons, coût, validation des anciennes versions et retry.

## Plan minimal et code

- [x] Figer neuf textes synthétiques nouveaux avant changement et reproduire les écarts. Référence `backend/tests/fixtures/rc_requirements_holdout_v1.json`, SHA-256 `63ab8a236fcaa7cf83950e3ce4b67bd25ef2ceacc04954323f543c6cb63c2b4c`, non modifiée après mesure rouge.
- [x] Analyser chaque clause distincte, sans l'ancienne limitation au premier match. Une unité de ce protocole est un signal par type d'exigence et clause explicite; deux mentions du même type dans une même clause ne constituent pas ici deux exigences normalisées.
- [x] Retenir une citation complète de clause avec offsets exacts. Espaces de citation exclus par ajustement des offsets, texte extrait inchangé. Parcours incrémental des délimiteurs et octets; pas de reconstruction quadratique de préfixes ni de liste massive de frontières. Les retours de ligne internes et points entre chiffres restent conservés.
- [x] Condition/négation non résolue : UNSPECIFIED. Si un en-tête conditionnel/négatif finissant par deux-points précède une liste à puces/numérotée, refus FAILED_SAFE / RC_LIST_CONTEXT_UNPROVEN, y compris si le premier item est dans le fragment adjacent de même document/extraction; aucun résultat partiel. Autre document/extraction non contaminé. Aucun lien de portée n'est inventé.
- [x] Clause pertinente de plus de 1 000 octets : REJECTED_LIMIT, sans citation tronquée ni résultat partiel pouvant omettre une condition distante.
- [x] Versionner le nouvel analyseur en 5 et préserver la validation explicite 1–4. Identités d'analyse dépendantes de la version; aucun UPDATE des anciennes preuves. La v5 concerne les nouvelles analyses ou relances explicites; aucune réanalyse automatique de corpus existant ici. Les tests de version courante attendent désormais 5, les tests historiques restent explicites.
- [x] Prouver extraction → analyse → enregistrement → matérialisation sur les neuf textes; refus de contexte/limite, confirmation humaine, sources et retries.
- [x] Backend global final, empreintes et base jetable vérifiés; case/journal/index actualisés. Synchronisation Basic Memory consignée après lecture de contrôle.

## Mesures et preuves

Preuves privées : `/home/noor/.local/share/smartao-proofs/r4f-20261016/`.

| Contrôle | Résultat acquis |
|---|---|
| Première régression pure | 9 échecs attendus, 3 réussites avant code |
| Détecteur RC ciblé final | 62 tests réussis, incluant 23 nouveaux tests |
| Analyse/materializer/workers | 30 tests réussis avant les deux nouveaux refus SQL |
| Materializer final, refus/URL/nominal inclus | 15 tests réussis |
| Référence neuf cas, occurrences par type | 10→15 TP, 5→0 FN, 0 FP |
| Référence exacte type/directive/clause | 1→15 conformes sur15; 14→0 FN et9→0 FP sur ce critère strict |
| Anciennes versions, revue indépendante | 2 520 comparaisons identiques avec le snapshot |
| Types et lint | mypy624 et Ruff backend/scripts verts |
| Semgrep | 1.179.0,225règles,5fichiers,0finding/0erreur; chemins effectifs vérifiés |

Ces neuf textes étaient nouveaux par rapport aux calibrations précédentes et ont été figés avant modification. Après leur utilisation en TDD, ils constituent un jeu de régression : aucune généralisation hors échantillon indépendante n’est démontrée. Ces métriques ne sont ni un benchmark DCE réel, ni une vérité Golden humaine. « FP exact » signifie que type/directive/citation ne correspondent pas au triplet attendu; ce n'est pas nécessairement une famille documentaire inventée. Lots, dates et rectificatif sont conservés dans les clauses; ils ne sont pas normalisés ni arbitrés automatiquement.

La chaîne SQL vérifie pour chaque clause attendue : observation version5, exigence persistée reliée à cette observation, fenêtre UTF-8 exacte, hash du fragment, PENDING_HUMAN_CONFIRMATION et SOURCE_SIGNAL_ONLY. Le retry est rejoué sans deuxième effet. Un tenant étranger est refusé avant matérialisation. Les analyses FAILED_SAFE/REJECTED_LIMIT ne produisent aucune obligation partielle et ne peuvent être matérialisées.

La première passe SQL a produit 9 échecs/17réussites : la normalisation des espaces de citation par la commande rendait les offsets discordants. Les offsets ont été corrigés au calcul, sans modification du contrat de commande ni des octets extraits. Journaux rouges conservés. La revue indépendante a trouvé les conditions « lorsque / sous condition / à moins que » et le contexte introductif des listes enveloppées ou séparées; régressions rouges puis vertes, garde étendu jusqu'au même document/extraction. Relecture finale indépendante : 59purs verts, cas signalés corrigés, pas de DB/Semgrep revendiqué par ce relecteur.

## Limites explicites

- Le garde liste est borné aux en-têtes finissant par deux-points immédiatement suivis de la liste, éventuellement entre fragments adjacents. Une négation indépendante ne bloque plus une liste nominale. Autres relations, en-têtes implicites et reconnaissance linguistique exhaustive ne sont pas qualifiés; une directive portée seulement par un en-tête ne devient pas une obligation confirmée.
- Une clause n'est pas une analyse grammaticale générale. Abréviations, tableaux, relations inter-documents et portée sémantique complexe restent non qualifiés. Aucune complétude d'exigences de DCE entier déduite.
- Une mention ancienne d'une échéance dans un rectificatif reste une mention distincte, jamais une date courante certaine. Les protections version/extraction/tenant existantes restent en place; le texte V1/V2 de la référence ne remplace pas une qualification réelle de rectificatif.
- Aucun nouveau champ normalisé de date, heure, fuseau, document attendu ou lot applicable; aucune obligation confirmée, tâche humaine, P3, dépôt ou GO automatique.
- Frontend/DTO inchangés : aucune preuve navigateur ou nouvelle qualification UI; OpenDesign/Impeccable non applicables. Jev/Manus et Context7 non nécessaires à cette correction déterministe sur les contrats installés; pas de navigation sémantique Serena. Superpowers cadrage/TDD/debug/revue/vérification et ECC verification-loop/security-review appliqués; Graphify et Basic Memory utilisés.

## Reprise de la vérification globale

Code gelé : six empreintes dans `code-sha256-verified.txt` (production, tests et référence). Seul runner global : session **20563**, journal `backend-global-verified.log`. PostgreSQL jetable R4f, `127.0.0.1:55439`, conteneur `smartao-r4f-proof-20261016`, label `smartao.proof=r4f-20261016`, flags DISPOSABLE=1/PRESERVE_C5=0. Aucun runner DB concurrent; ne pas déclarer PASS avant sortie du runner. Aucun service live, corpus réel, VPS, déploiement, push ou effet P3.

### Correction finale de conservation des URL

Une vérification a reproduit une citation du canal acheteur coupée à `https://plateforme.`. Un test rouge puis correction du découpage protège les URL HTTP(S), leurs points et paramètres, sans lecture réseau ni modification des octets source. Le même découpage est utilisé pour la validation v5; versions1–4 inchangées. Le premier helper copiait inutilement le token à chaque point : budget2secondes dépassé sur400000répétitions, puis cache de la borne du token et test vert. Relecture indépendante :61pursverts,2520comparaisonshistoriquesidentiques,URL multiples/query/pointvirgulepréservés;0,100s pour400000 répétitions et0,194s pour800000,mesureslocalesnoncertificationgénérale. Chaîne SQL finale y comprisURL :**14tests réussis,17,65s**.

Première globale interrompue pour cette correction :**689réussites,1avertissement,281,82s**,nonqualifiante;archive`backend-interrupted-url.log`. **Seule passe finale en cours :82508,backend-global-qualified-final.log**. Référence9casinchangée15/15;6empreintes renouveléesaprèsgel,aucunPASSglobalanticipé.

### Refus précis et gel effectivement final

Le garde de coexistence condition/liste était trop large : négation indépendante puis liste nominale refusée. Rouge puis remplacement par `_unproven_list_context_v5` : en-tête source de clause terminant par deux-points, suite immédiate à puces/numérotée, ou début du fragment d’ordinal adjacent même document/extraction. Ordre des fragments inversé, autre extraction/document et lignes enveloppées/vides vérifiés par revue indépendante. **62pursverts,15materializerSQLverts(19,57s)**;casindépendantCOMPLETED,casconditionnelsrefusés. Référence15/15inchangée. Le précédent garde trop large est une étape intermédiaire, pas le comportement livré.

Passe précédente179réussites/1avertissement/172,10s interrompue pour ce refus nominal;archive`backend-interrupted-list-refusal.log`,nonqualifiante. **Seul global courant :session20563,journal backend-global-verified.log**,6empreintes code-sha256-verified.txt. Ruff/mypy624verts,revuefinalesansfindingdanslepérimètre;les2520comparaisonslegacyprécédentesconcernentdescheminsinchangésparlegardev5. AucunPASSglobalanticipé.

## Fichiers du delta et contrôle de périmètre

- `backend/app/modules/dce/application/analysis.py` : comportement v5, validation historique conservée;97lignes ajoutées/24retirées par rapport au snapshot exact de reprise, pas au HEAD contenant du WIP antérieur.
- `backend/tests/domain/dce/test_rc_requirement_clauses.py` : nouvelles preuves et contre-exemples.
- `backend/tests/fixtures/rc_requirements_holdout_v1.json` : neuf textes figés, SHA inchangé.
- `backend/tests/domain/dce/test_rc_critical_signal_coverage.py` : attentes de version courante5, assertions des anciennes règles préservées.
- `backend/tests/application/test_dce_rc_analysis.py` : attente de version courante5 pour le signal persistant.
- `backend/tests/application/test_dce_requirements.py` : neuf parcours et refus/URL/nominal supplémentaires.

Plan/index/dossier servent au suivi. Aucun fichier de dépendances, de migrations ou d’interface modifié; aucun nettoyage du WIP préexistant. Le patch de production exact est conservé dans les preuves privées.

## Résultat final — 16 octobre 2026

**2 787 tests backend réussis, 3 avertissements, 1 466,99 s (24 min 26 s), sortie 0.** Les62tests RC purs et15tests de matérialisation sont inclus dans cette suite sur le code final; aucun test backend ignoré. Trois avertissements : dépréciation Starlette/httpx et deux occurrences de l’alias Pydantic `authorization` sans effet dans le contexte de génération de schéma des tests d’UUID tenant/retry EXP-05. Ils sont conservés hors du correctif RC, sans masquer un échec.

Les6empreintes finales sont inchangées. Ruff backend/scripts, mypy624, git diff --check et Semgrepfinal1.179.0/p-security-audit/225règles5fichiers0finding0erreur sont verts; lescheminseffectivementscannés sont vérifiés. Revue indépendante décrite ci-dessus, aucunevalidationhumaineGoldendéduite. Le scan ne certifie pas l’absence de vulnérabilité. Les deux passes interrompues sont archivées et non qualifiantes; seul `backend-global-verified.log` établit le global.

Base jetableR4f : label exact relu, Alembicbase vérifié à zéro ligne après suite, puis seul `smartao-r4f-proof-20261016` arrêté/retiré. Aucun service live touché. Branche/HEAD inchangés, WIP préservé, aucun commit ni push. Pas de dépendance/migration/DTO/frontend changé; suite Web/navigateur non rejoués dans cette tranche.

Les clauses sont maintenant distinctes jusqu’aux exigences persistées avec leurs citations et leurs états pending/source-signal. Les valeurs de date/heure, pièces et lot applicable ne sont pas encore des champs normalisés prouvés : c’est la prochaine insertion. Aucun DCE réel entier déclaré complet, aucune admission A1, A2 reste HOLD et NO-GO public maintenu.

Plan, case, journal et index finalisés avec une seule tranche active. Basic Memory `smart-ao-v8` synchronisé puis relu : résultat2787, retrait du conteneur et prochaine étape exacte concordants. Le plan reste l’autorité opérationnelle.

Prochaine étape : R4 — intégrer une projection structurée candidate des pièces attendues, échéances et portées lot aux exigences RC sourcées, avec UNKNOWN sur toute valeur ou applicabilité non prouvée et refus des rectificatifs ambigus; qualifier sa lecture sans effet métier automatique. A1 non admis, A2 générique HOLD et NO-GO public maintenus.
