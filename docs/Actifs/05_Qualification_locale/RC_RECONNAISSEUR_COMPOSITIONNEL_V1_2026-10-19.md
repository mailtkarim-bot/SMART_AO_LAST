# Reconnaisseur d’intention compositionnel candidat v1 — 19/10/2026

## AS-IS, risques, points d’insertion

Checkout principal codex/reconcile-smartao-20261009/HEAD30f2693, WIP conservé. Cadrage et développement32cas préparés dans RC_INTENTION_GENERALE_CADRAGE_2026-10-19.md. Le mécanisme local compositionnel est retenu par Codex pour cette tranche technique réversible demandée « avancer » ; ce choix ne constitue ni admission métier, validation humaine des réponses ni activation produit. Le cadrage antérieur reste une proposition historique inchangée.

Insertion : nouveau module application rc_compositional_intent.py, réutilisant RcQueryIntent/RcQueryLot/RcSignalAnchor et garde financière canonique. Aucun port, fournisseur, dépendance, schéma, profil retrieval, factory/API/UI nouveau. V7/v8/v9/v10 préservés. L’appel explicite à recognize_rc_intent est le seul accès au candidat ; aucune lecture DCE ou encodage.

Risques : cooccurrence prise pour demande, ambiguïté et contexte ignorés, faux lot/qualificatif, négation supprimée, calibration sur challenge. Règles versionnées rc-compositional-v1/lexical-cue-v1, provenance brute querySHA et ancres exactes. Sujet et demande sont distincts d’une réponse métier qui reste UNKNOWN.

## Plan minimal et preuves

- [x] Tests rouges32cas développement puis module minimal et32verts ; raisonnement compositionnel et refus explicites, aucune requête du challenge consultée.
- [x] Revue contradictoire indépendante du nouveau code et corrections avec rouges/verts sur contre-exemples de développement.
- [x] Banc d’intention reproductible, répétitions/provenance/confusions/compteurs et tests ; contrôles pertinents.
- [x] Gel code/règles/tests/données/protocole avant ouverture unique du challenge ; qualification d’intention distincte de retrieval/SQL.
- [x] Sécurité, diff, documentation et miroir autorisé ; nouvelle prochaine étape selon preuves.

32développement verts et Ruff/mypy ciblés verts ne qualifient pas une compréhension générale, le retrieval, E5 ou des DCE entiers. Challenge toujours scellé à ce point. A1nonadmis/A2génériqueHOLD/NO-GOpublic, DPGFnonévaluable. Aucun corpus réel/live/VPS/P3/déploiement/commit/push.

## Résultat et limites

Reconnaisseur rc-compositional-v1 isolé codé : composition sujet/demande/portée, préfixe nominal positionnel et résiduel grammatical bornés, ancresUTF8/SHA requête, garde financière canonique, abstention sans lecture de source ni modèle. Aucun moteur actif/profilretrieval/factory/API/UI/schéma/dépendance remplacé. Choix technique local retenu pour prototype réversible selon demande de poursuivre, sans validation métier humaine ni activation. Développement32/32exacts dont16/16positives ;53tests ciblés verts (50application+3banc),rouges32initiaux puis9/7/2contre-exemples de revue et2preuvesCLI. Revue/contre-revues indépendantes ont corrigé cooccurrence, qualificatif ignoré, lot tronqué, négation et autre objet inclus dans un document. Gel12fichiers avant ouverture consignée du challenge ;code inchangé après observation. Challenge32cas :14/16positives exactes,24/32total exact,UNSUPPORTED1/4,AMBIGUOUS4/5,UNKNOWN4/6,financier1/1. Zéro promotion indue et zéro ancre byte invalide ;5écarts aux ancres gold,3gates fausses (composantes,ancres exactes,positives exactes),candidatHOLD/admittedfalse. Les11abstentions structurelles et4demandes hors périmètre ne deviennent pas COVERED ;reconnaissance exacte et refus sûr séparés.128appels de reconnaissance (4passages),0lecture source/0encodeur,latencep95chaude0,064ms descriptive intention seule,pas une preuve E5/retrieval/SQL. Suite backend sansDB finale2514réussites/846désélectionnés/1warning47,20s ;pas de globale incluantDB rejouée. Ruff/format4/mypy635/diff verts ;Semgrep1.179.0/225règles/4fichiers0finding/0erreurJSON,sanswarning spécifique ;detect-secrets4fichiers0signal. Aucun DB/CPUmodèle/corpus réel/live/VPS/P3/déploiement/commit/push ;HEAD30f2693/WIP conservés. A1nonadmis/A2HOLD/NO-GOpublic.

### Fichiers

- `backend/app/modules/knowledge/application/rc_compositional_intent.py` : reconnaisseur d’intention candidat explicite, hors moteur actif.
- `scripts/qualify_rc_intent_recognition.py` : mesure d’intention seule,4passages,groupes/gates distincts ;refuse le scellé sans manifest de gel et vérifie les4fichiers essentiels ainsi que tous les hashes déclarés.
- `backend/tests/application/test_rc_compositional_intent.py` :32développement +18contre-exemples indépendants.
- `backend/tests/ops/test_rc_intent_recognition_qualification.py` : rappel positif distinct d’abstention,échec d’ancres distinct d’intégrité byte,barrière scellé et manifest essentiel.

### Lecture des preuves

Les ancres physiquement exactes ne satisfont pas automatiquement la convention annotée :les5différences gold restent des échecs. Les14positives exactes ne compensent ni les2omissions ni les mauvaises composantes des abstentions. Le seuil indépendant100% n’est pas atteint. L’intégrité financière prouvée porte sur la garde lexicale existante,pas sur toute formulation financière possible.

Le mécanisme reste une grammaire locale finie, pas une compréhension générale du français. Les contrôles positionnels et le vocabulaire grammatical sont versionnés dans le code ;la sûreté universelle n’est pas démontrée. La qualification de stage1 n’autorise aucune projection ou recherche. Les source_guards/runtime_guards de la préparation sont des exigences futures, pas des scénarios SQL/timeout exécutés ici.

Challenge v1 désormais ouvert/historique :ne pas retoucher ce candidat,ce gold ou ses seuils pour rendre le rapport vert. La prochaine itération exige une nouvelle version et un nouveau challenge indépendant ;les corrections passent par de nouveaux cas de développement.

Preuves privées `~/.local/share/smartao-proofs/rc-compositional-20261019/` :rouges/verts,développement/challenge,manifest12fichiers,consignationd’ouverture,nonDBfinal,lint/types/scans. Méthode Superpowers using-superpowers/brainstorming/TDD/revue/vérification,ECC verification-loop. Graphify consulté avant lecture ciblée,graphe ancien insuffisant pour ce nouveau WIP. Pas de navigation sémantique Serena,aucun SDK nouveau nécessitant Context7,aucune UI pour OpenDesign/Impeccable et aucun Jev/Manus requis. Le choix se limite à ce candidat technique réversible ;pas de décision métier/Owner inférée.

Miroir Basic Memory :résumé minimal prêt en preuve privée,autorisation explicite demandée après le refus de revue automatique antérieur (destination considérée externe). Aucun texte du challenge à transmettre. En attente,le plan et ce dossier locaux sont à jour.

Prochaine étape : ESSAIS DCE — reproduire sur développement les deux omissions positives et les divergences de composantes/ancres du reconnaisseur compositionnel v1, puis préparer une v2 et un nouveau challenge indépendant sans régler sur le challenge v1 désormais historique. Préserver les refus, les portées et UNKNOWN; aucun branchement au retrieval ni activation avant preuve. V7/v8/v9 et v10 non activée, DPGF non évaluable; A1 non admis, A2 générique HOLD et NO-GO public maintenus.
