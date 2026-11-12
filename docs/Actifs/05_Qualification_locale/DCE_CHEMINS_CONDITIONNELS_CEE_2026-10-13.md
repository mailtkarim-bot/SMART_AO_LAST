# Essais DCE — chemins conditionnels CEE Cadarache — 13 octobre 2026

## Périmètre et résultat documentaire

Pièce : CEA Cadarache, petits contrats de travaux d’entretien, contrats cadres 2027–2031; `CCTPC.pdf`, CCTP commun à tous les lots, indice 2, référence `DG/CEACAD/DSTG/STL/GTP/CCTP-22-057`, annexe 13, page 42/44. Diagramme inférieur « Variation de vitesse (BAT-TH-112) ». Le [dossier source](DCE_CHEMINS_FLECHES_QUALIFICATION_2026-10-12.md) identifie les archives. Cette qualification concerne le financement CEE documentaire, pas une candidature ou un équipement réel.

Source SHA-256 : `263c2dfdea1d010c1b02d6387ab6eef7d8fdab4e1d2fabd32e32ab3bd133ad8d`. Rendu 150 DPI, 1275×1650 pixels : `e2d7b37426d89c8483d9a9260e8dad7d0792c399560b7ac4b17cbf579e788e79`.

La confrontation guidée par une référence technique Codex retrouve 12 nœuds, 24 tokens OCR, 12 liaisons et 3 jonctions. **Relations manquantes : 0/12 attendues**, non qualifiées : 0/12, ambiguës : 0/12; 7 chemins complets candidats dans cette référence. Ce dénominateur n’est pas une mesure de complétude du PDF, du DCE ou de tous les objets du diagramme.

| Entrée | Conditions documentaires successives | Sortie du document |
|---|---|---|
| Moteur existant | Variateur déjà présent : OUI | NON ELIGIBLE CEE |
| Moteur existant | Variateur déjà présent : NON; asynchrone : NON | NON ELIGIBLE CEE |
| Moteur existant | Variateur déjà présent : NON; asynchrone : OUI; classe IE2 | Contacter votre correspondant CEE centre |
| Moteur existant | Variateur déjà présent : NON; asynchrone : OUI; classe IE3 ou IE4 | ELIGIBLE CEE |
| Moteur neuf | Branche OUI de l’entrée; asynchrone : NON | NON ELIGIBLE CEE |
| Moteur neuf | Branche OUI de l’entrée; asynchrone : OUI; classe IE2 | Contacter votre correspondant CEE centre |
| Moteur neuf | Branche OUI de l’entrée; asynchrone : OUI; classe IE3 ou IE4 | ELIGIBLE CEE |

Les trois jonctions restent des nœuds propres, pas des sorties :

| Jonction | Région en pixels du rendu source | Connexions conservées |
|---|---|---|
| inlet | `[671,1214,685,1231]` | Moteur neuf et variateur absent → question asynchrone |
| reject | `[339,1274,352,1287]` | Variateur déjà présent et asynchrone NON → sortie NON ELIGIBLE |
| split | `[670,1321,684,1335]` | Asynchrone OUI → critères IE2 et IE3/IE4 séparés |

La branche OUI de l’entrée neuve est conservée telle qu’affichée; elle ne devient pas une réponse inventée pour un moteur. IE3/IE4 restent dans un même critère. Trois sorties NON ELIGIBLE, deux ELIGIBLE et deux CONTACT sont des chaînes documentaires, avec **éligibilité réelle UNKNOWN** dans tous les cas.

## AS-IS, risques et insertion minimale

AS-IS : géométrie candidate et pointes/labels de trois références déjà qualifiés; conditions amont en OCR brut. Risques : perdre une condition amont, confondre une jonction avec une tête, omettre NON, réinterpréter IE2 comme une issue binaire, considérer un chemin incomplet ou un OCR illisible comme prouvé.

Insertion : un module applicatif pur `backend/app/modules/dce/application/conditional_diagram.py` et 23 tests dans `backend/tests/application/test_conditional_diagram.py`. Réutilisation de `structure_projection`, `diagram_evidence` et du détecteur pixel existant. Pas de writer/API, migration, dépendance, UI ou changement de l’analyse métier globale. Le composant reçoit un scope autorisé; il ne décide pas les droits HTTP/ownership SQL et n’est pas branché à une admission automatique.

Plan réalisé : référence bornée → observations source → assemblage → contre-exemples TDD → revue indépendante → intégration des deux nouveaux fichiers → vérification finale. Les 27 fichiers logiciels hérités contrôlés par SHA sont inchangés. HEAD `30f26934430095632000a1d82519f61dbb4c6411`, branche `codex/reconcile-smartao-20261009`; WIP local non commité.

## Qualification et provenance

Les polylignes attendues et régions des jonctions sont digitizées dans une référence technique locale avant la classification des pixels. Chaque segment est échantillonné à pas maximal de 1 pixel; support sombre dans un voisinage ±2 pixels, seuil requis 98%, lacune maximale 3 pixels. Les 12 routes observées ont un support de 100% sans lacune dans cette calibration. Les ports de chaque jonction appartiennent à un même composant d’encre à quatre connexions. Les têtes terminales proviennent du détecteur 150 DPI déjà qualifié. **Ce contrôle guidé ne découvre pas encore la topologie seul.**

Les nœuds textuels conservent leurs tokens et régions, avec qualification technique explicite `SOURCE_TEXT_CANDIDATE`; texte sans caractère alphanumérique ou qualification absente reste UNKNOWN. Ce drapeau fourni par le caller n’est pas une vérification linguistique générale. Les branches OUI/NON doivent correspondre aux tokens attendus et être proches de leur route; un embranchement CONDITION sans labels reste UNKNOWN. Jonctions, négations et sorties sont conservées, sans simplification des conditions.

T81 brut `iño`, relecture candidate `ouI` normalisée OUI; T89 brut `Iño` conservé avec sa relecture OUI déjà acquise. OCR local sur crop droit 450 DPI, `use_cls=False` dans le caller privé uniquement; aucun changement du mode OCR global. Source, rendu, crop, région, parseur et versions sont conservés. Le résultat contient les observations validées et les références attendues, y compris quand des observations contradictoires rendent une liaison ambiguë; le hash seul ne remplace pas la preuve.

Les six conditions source sont conservées exactement : « J’installe un variateur de vitesse sur un moteur déjà existant? », « J’installe un variateur de vitesse sur un moteur neuf? », « Le moteur existant est déjà équipé d’un variateur de vitesse? », « Moteur asynchrone? », « Le moteur est de classe IE2 » et « Le moteur est de classe IE3 ou IE4 ». Les apostrophes ASCII du texte OCR restent inchangées dans les données privées; cette liste est une présentation typographique.

Les limites d’entrée sont bornées (32 nœuds, 64 références, 128 observations/tokens/chemins, 64 points par route); scope source/version/tenant/rendu exact exigé. Cycles, entrée recevant un arc amont, doubles labels concurrents, région hors scope et provenance falsifiée sont refusés. `semantic_state=UNKNOWN`, `REVIEW_REQUIRED` et `admission_granted=False` demeurent obligatoires.

## Tests et revue

TDD : 13 rouges initiaux, puis régressions de provenance/ordre/UNKNOWN, refus de labels distants, entrée recevant une condition et double OUI. La revue indépendante a confirmé trois P2 : bifurcation sans labels, texte « ??? » accepté, provenance régionale perdue en cas d’ambiguïté. Quatre rouges supplémentaires ont été observés avant correction; ces cas et l’absence de qualification textuelle passent désormais. Seconde revue : trois findings fermés, aucun autre défaut concret confirmé.

**119 tests ciblés réussis** : 23 assemblage, 39 pointes/labels, 57 projection. Ils prouvent les sept chemins nominaux, les sorties CONTACT distinctes, UNKNOWN dépendant des liaisons absentes/ambiguës, maintien des négations et sources, limites, scope, cycles et déterminisme. Contrepreuve sur les données source : retirer e4 (jonction d’entrée → asynchrone) expose 1/12 relation manquante et rend six chemins UNKNOWN, sans réparer ou ignorer l’amont.

Vérification finale : suite backend complète **2420/2420 réussis**, 0 ignoré, couverture **88.08%** (seuil85,50% inchangé), 1235.30s, 4 avertissements Starlette/httpx et Pydantic Field.alias (`case_id`, `task_id`, `request`); Ruff global vert, format 1178 fichiers, mypy 618 sources. Semgrep 1.179.0, `p/security-audit`, 225 règles configurées, deux nouveaux fichiers effectivement analysés, 0 finding/0 erreur, métriques désactivées. Detect-secrets `--all-files --no-verify` : 0 finding; Bandit sur le nouveau module : 0 finding/0 erreur. Le scan est ciblé et ne constitue pas un audit de sécurité exhaustif.

## Preuves et limites

Preuves privées hors Git : `/home/noor/.local/share/smartao-proofs/dce-structured-projection-20261012/conditional/` : `prove.py`, `reference.json` historique conservé, `reference-v2.json` avec contrat textuel explicite, `qualification.json`, journaux, couverture et scans. Le caller bloque les accès réseau Python et utilise les modèles OCR installés. Les sources réelles ne sont pas copiées dans les fixtures Git. Qualification commencée le 12/10 UTC et document daté du 13/10 selon Africa/Casablanca.

A1 non admis, A2 générique HOLD, NO-GO public. Aucun moteur réel évalué, règle réglementaire actuelle vérifiée, acte humain simulé, complétude DCE, admission Golden ou levée de REVIEW_REQUIRED. Aucun backend live, UI, VPS, déploiement, push, P3, dépôt externe ou export métier. La découverte autonome des jonctions/routes reste à qualifier; la preuve actuelle est conditionnée par la référence et la calibration.

Méthode : Superpowers using-superpowers/brainstorming/TDD/requesting-code-review, ECC verification-loop; Graphify et Basic Memory. API installée PyMuPDF/RapidOCR réutilisée selon la qualification précédente; pas de nouveau contrat nécessitant une autre recherche Context7. OpenDesign/Impeccable inapplicables sans interface; Jev/Manus non requis pour l’assemblage déterministe. Revue IA distincte d’une validation humaine.

Prochaine étape : ESSAIS DCE — extraire la topologie candidate du logigramme CEE « Variation de vitesse » de Cadarache depuis les pixels sans fournir ses polylignes attendues, puis comparer aux 12 liaisons et 3 jonctions de référence; mesurer omissions et faux raccordements avec contre-exemples synthétiques, provenance et UNKNOWN conservés. A1 non admis, A2 générique HOLD et NO-GO public maintenus.

PostgreSQL tmpfs dédié retiré après vérification ID/label/aucun volume/port local; retrait confirmé par inspection et inventaire des IDs. Reçu `conditional/cleanup-receipt.json` hors Git. Les hashes du code intégré et de la preuve figée sont enregistrés dans `conditional/final-gates.json`, `integrated-files.json` et `proof-hashes.json`.

Plan et index mis à jour; miroir Basic Memory smart-ao-v8 synchronisé puis relu avec prochaine étape exacte. Une seule tranche active; `git diff --check` vert.
