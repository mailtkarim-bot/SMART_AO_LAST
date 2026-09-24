# SMART AO — CONFRONTATION MASTER MÉTIER v2.0 ↔ PRODUCT FREEZE v1.0
## Audit de couverture, écarts et décision de réouverture propriétaire

**Date :** 24 septembre 2026  
**Statut :** AUDIT DE TRAÇABILITÉ — READ-ONLY / AUCUNE MODIFICATION DU REPO  
**Source métier :** `SMART_AO_CAHIER_DIRECTEUR_METIER_MASTER_CANDIDATE_v2.0_2026-09-24.md`  
**Autorité produit comparée :** `SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md`

## 0. Verdict exécutif

Le Product Freeze v1.0 n'est pas incohérent avec le MASTER métier v2.0, mais il est **insuffisamment expressif pour servir seul de contrat produit à Codex après l'enrichissement métier**.

Le problème principal n'est pas une contradiction frontale. C'est une **perte de profondeur par compression** : plusieurs familles de risques que le MASTER transforme désormais en obligations métier de premier rang sont agrégées dans le v1.0 sous des formulations trop génériques telles que « risques », « capacités », « P7 », « REX » ou « passation ». Cette compression permettrait techniquement à une implémentation d'être conforme au texte du v1.0 tout en n'implémentant pas les mécanismes métier essentiels du MASTER.

**Conclusion : réouverture propriétaire requise.** Le Product Freeze v1.0 doit être remplacé, après validation du propriétaire, par un Product Freeze v2.0 explicitant les nouveaux contrats produit. Le cahier technique ne doit plus être dérivé du v1.0.

### Classification globale

- **COVERED** : doctrine de preuve, source/version, IA non autoritaire, confidentialité Patron/Collaborateur, dépôt humain, idempotence, tenant-awareness, P0–P7, inconnus/contradictions.
- **PARTIAL** : économie, capacité, partenaires, passation, REX, public/privé, obligations documentaires, assurances, HSE, réglementation, prix/révision.
- **MISSING / NON CONTRACTUALISÉ** : Carte d’Engagement à 12 axes, profil réglementaire dynamique, dérogations contractuelles structurées, registre de sanctions, préservation des droits/forclusion, OS et travaux supplémentaires, règlement des comptes/DGD, résiliation/frais et risques, matrice assurance/prestation, HSE → capacité/coût, engagements mesurables environnement/social, circuit réel de paiement, coût post-réception, autorisations tierces, risque portefeuille.
- **NEEDS_EXTERNAL_VALIDATION** : contenu juridique détaillé, assurance, HSE, corpus privé, règles réglementaires vivantes, métriques métier.

## 1. Pourquoi le v1.0 ne suffit plus

Le Product Freeze v1.0 a été conçu pour fixer une architecture de produit sûre : Affaire, Mémoire Entreprise, preuves, P0–P7, confidentialité, dépôt humain, REX et IA sous contrôle. Cette base reste valide.

Le MASTER v2.0 ajoute cependant une nouvelle dimension : **le produit doit désormais protéger la décision d’engagement jusqu'aux droits économiques et contractuels qui conditionnent la rentabilité réelle de l'affaire**.

La question produit évolue de :

> Cette affaire mérite-t-elle notre effort commercial, pouvons-nous la gagner, la financer, l'exécuter correctement et conserver la marge prévue ?

vers :

> **Cette affaire mérite-t-elle notre effort commercial, pouvons-nous la gagner, la financer, l'exécuter correctement, protéger nos droits et conserver la marge prévue ?**

Cette modification n'est pas éditoriale. Elle crée de nouveaux objets, états, preuves, décisions, échéances et obligations de passation.

## 2. Matrice de confrontation

| Domaine MASTER v2.0 | Product Freeze v1.0 | Statut | Écart matériel | Décision v2.0 |
|---|---|---|---|---|
| Affaire, lots, versions, preuves | §§2,4,5 | COVERED | bon socle | conserver et enrichir |
| Mémoire Entreprise | §2.2 | COVERED | manque portée des validations externes | enrichir sans changer doctrine |
| P0–P7 | §4 | COVERED/PARTIAL | portes présentes, contenu trop synthétique | maintenir P0–P7, enrichir critères P2/P3/P4/P6/P7 |
| Carte d’Engagement 12 axes | absent | MISSING | pas de sortie Patron globale structurée | créer comme projection centrale, jamais score opaque |
| Profil réglementaire dynamique | absent | MISSING | réglementation non modélisée par applicabilité/version | créer `REGULATORY_PROFILE` produit |
| MIRP | indirect | PARTIAL | n'est pas contractuellement visible dans le freeze | rendre explicite dans P2/P3 |
| Constructibilité / logistique | « risques » | PARTIAL | trop générique | exiger traduction prescription → moyens/coût/délai |
| Interfaces lots / coûts invisibles | « risques » | PARTIAL | matrice non garantie | rendre obligatoire pour affaires applicables |
| Marge / cash / scénarios | §10 « couverture économique » | PARTIAL | cash et stress non définis | figer marge, cash, résistance, portefeuille |
| Clause de prix / révision | absent explicite | PARTIAL | pas de contrat produit sur formule/index/mismatch | ajouter audit prix déterministe |
| Capacité réelle | §10 capacités | PARTIAL | pas de charge/calendrier/ressource nommée | enrichir P2/P3 |
| Fournisseurs/ST/GME | V1.x partenaires structurés | PARTIAL / DEFERRED | profondeur métier v1.0 historique perdue | réintroduire socle V1, structuration avancée V1.x |
| Public/privé | §1 | PARTIAL | distinction existe mais hiérarchie contrat non explicitée | figer reconstruction du contrat applicable |
| Règle → dérogation → impact | absent | MISSING C1 | risque majeur de fausse règle générale | créer objet/décision produit |
| Pénalités/sanctions | « risques » | MISSING C1 | aucune fiche déclencheur/formule/plafond/cumul | créer registre contractuel |
| Préservation droits / forclusion | absent | MISSING C1 | peut faire perdre créance/droit | créer calendrier et événement de droit |
| OS/modifications/travaux sup. | absent | MISSING C1 | pas de contrat sur réaction/valorisation | créer suivi structuré |
| Résiliation/frais et risques | absent | MISSING C1 | exposition de rupture non visible | ajouter stress de rupture |
| Réception/DGD | P7/REX génériques | MISSING/PARTIAL C1 | séquence règlement des comptes absente | ajouter chaîne réception → DGD |
| Assurance réelle | Mémoire Entreprise « capacités » | PARTIAL C1 | attestation ≠ couverture prestation | ajouter évaluation de couverture + revue courtier |
| HSE → capacité/coût | « risques » | PARTIAL C1 | document détecté sans impact opérationnel | ajouter prérequis d’exécution |
| Environnement/social mesurable | absent | MISSING C1 | promesse mémoire non convertie en KPI/coût/preuve | ajouter engagement mesurable |
| PEMD/REP/traçabilité | absent explicite | PARTIAL | contexte documentaire existe ailleurs | rendre dépendant profil réglementaire + engagement |
| Circuit réel paiement | « trésorerie » implicite | PARTIAL C1 | délai légal ≠ encaissement réel | ajouter graphe de paiement |
| Engagements de l’offre | préparation/réponse | PARTIAL | registre pas exigé explicitement | rendre obligatoire avant P4/P7 |
| Dépôt exact / preuve | §§4,8,10 | COVERED | bon | préserver strictement |
| BAFO/mise au point | P6 | PARTIAL | impacts à recalculer non détaillés | figer revalidation multi-axes |
| Passation renforcée | P7 | PARTIAL C1 | ne garantit pas droits/pénalités/paiement | enrichir paquet P7 obligatoire |
| REX droits/OS/pénalités | §10 | PARTIAL | REX trop générique | étendre taxonomy REX |
| IA / abstention | §§5,9 | COVERED | bon | préserver |
| Éthique concurrence | absent | MISSING C2 | risque comportemental | ajouter alerte/escalade, pas qualification juridique |
| Packs sectoriels | absent | MISSING C2 | différenciation métier différée | V1.x |
| Autorisations tierces | absent | MISSING C2 | planning irréaliste possible | registre dépendances |
| Normes/licences | §9 partiel | PARTIAL | licences pas garanties | expliciter |
| Règles futures datées | absent | MISSING C1 | risque d'appliquer prématurément une loi | états ACTIVE/FUTURE/EXPIRED/REVIEW_REQUIRED |

## 3. Risques si Codex continue sur v1.0 seul

1. **Faux sentiment de conformité** : un champ générique `risk` pourrait satisfaire le texte sans couvrir les pénalités, dérogations ou délais de droit.
2. **P7 sous-dimensionné** : le conducteur pourrait recevoir l'offre vendue mais pas les échéances permettant de préserver les créances et réserves.
3. **Réglementation non versionnée** : une règle future pourrait être appliquée trop tôt ou une règle expirée rester active.
4. **Assurance trompeuse** : présence d'une attestation interprétée comme couverture de la prestation.
5. **HSE documentaire** : PPSPS/habilitation détectés mais aucun coût, ressource ni blocage de démarrage.
6. **Engagements mémoire non exécutables** : une promesse environnementale/sociale peut rester du texte sans KPI, responsable ni coût.
7. **Trésorerie simplifiée** : calcul économique sans circuit réel de validation/paiement.
8. **Pénalités codées en dur** : plafonds/délais génériques au lieu du contrat applicable.
9. **DGD/forclusion ignorés** : perte de droit non représentée dans les objets métier.
10. **Marketing plus avancé que le produit** : promesse d'« ingénierie DCE » sans couche contractuelle réellement implémentée.

## 4. Décisions de réouverture propriétaire proposées

- **PF2-01 — Question fondamentale** : ajouter explicitement « protéger nos droits ».
- **PF2-02 — Carte d’Engagement** : adopter la carte à 12 axes comme sortie Patron de référence.
- **PF2-03 — Profil réglementaire** : adopter règles vivantes versionnées et applicabilité contextuelle.
- **PF2-04 — Contrat applicable** : exiger reconstruction référence → dérogation → impact.
- **PF2-05 — Sanctions** : adopter registre structuré des pénalités/sanctions.
- **PF2-06 — Droits** : adopter `RIGHT_PRESERVATION_EVENT` et calendrier P7.
- **PF2-07 — Modifications** : adopter OS/travaux supplémentaires/prix nouveaux comme domaine suivi.
- **PF2-08 — Clôture contractuelle** : réception, comptes, DGD, garanties et coût post-réception.
- **PF2-09 — Rupture** : exposer résiliation/substitution/frais et risques sans avis juridique automatisé.
- **PF2-10 — Assurance** : distinguer preuve d'assurance et couverture de la prestation.
- **PF2-11 — HSE** : convertir obligation en prérequis/capacité/coût/délai/preuve.
- **PF2-12 — Engagements mesurables** : tout engagement sensible de l'offre devient objet suivi.
- **PF2-13 — Paiement** : représenter circuit contractuel et hypothèse prudente de cash.
- **PF2-14 — P2/P3/P4/P6/P7** : enrichir les conditions de porte sans créer de nouvelles portes.
- **PF2-15 — Validation externe** : interdire les automatismes juridiques/assurantiels/HSE non qualifiés.
- **PF2-16 — V1/V1.x** : intégrer le socle contractuel C1 dans V1 ; garder packs sectoriels et profondeur avancée en V1.x.

## 5. Ce qui ne doit PAS changer

- pas de rewrite global ;
- pas de nouveau score opaque ;
- pas de décision juridique autonome ;
- pas de dépôt final autonome en V1 ;
- pas d'élargissement des droits Collaborateur ;
- pas de fuite financière dans UI, recherche, export ou contexte LLM ;
- pas de franchissement automatique P0–P7 ;
- pas de vérité issue du frontend, du cache, du vecteur ou du LLM ;
- pas de suppression destructive d'une ancienne version ou d'une ancienne décision.

## 6. Verdict de promotion

**RECOMMANDATION :** produire et faire valider `SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v2.0_CANDIDATE.md`, puis dériver le cahier technique v2.1 de cette version. Le v1.0 reste l'autorité active tant que le propriétaire n'a pas explicitement promu v2.0.

Cette promotion n'est pas une refonte du produit. Elle rend explicite, testable et codable la profondeur métier que le v1.0 avait trop comprimée.
