# SMART AO — Cahier directeur Produit & Métier
## OWNER FREEZE v1.0 — Product Freeze candidat

**Statut :** CANDIDAT POUR APPROBATION PROPRIÉTAIRE  
**Date :** 20 septembre 2026  
**Autorité de transition :** le cahier OWNER_CONSOLIDATED v0.4 reste l’autorité active jusqu’à l’approbation explicite de ce v1.0  
**Question couverte :** « Quel SmartAO voulons-nous construire ? »

## 0. Règle de transition

Ce document consolide les décisions produit/métier du cahier v0.4, du catalogue UX v0.3, des OWNER EXPERIENCE FREEZE et de la preuve G01–G09. Il devient la nouvelle autorité produit/métier uniquement après approbation propriétaire explicite.

Avant cette approbation :

- le v0.4 prévaut en cas de contradiction ;
- ce document est le candidat de Product Freeze v1.0 ;
- les contrats techniques et les preuves existantes restent des références d’implémentation, pas des autorités produit.

Après approbation :

- ce document remplace le v0.4 comme source de vérité produit/métier ;
- le v0.4 passe dans `_ARCHIVE/` avec son historique de décisions ;
- toute modification produit exige une nouvelle version, un motif, un impact et une validation propriétaire.

## 1. Promesse et client initial

SMART AO est un système d’exploitation de réponse aux appels d’offres BTP. Il aide une entreprise à transformer des sources publiques et des dossiers acheteurs en décisions, préparation et remise contrôlées, en conservant les preuves, les inconnus, les contradictions et les responsabilités.

Le client initial est une entreprise BTP qui prépare des candidatures et offres publiques ou privées. Le produit sert d’abord le Patron dirigeant, puis les Responsables, Experts et autres Collaborateurs dans un périmètre assigné.

La valeur n’est pas un score opaque ni un texte généré sans preuve. Elle est la continuité entre source, compréhension, décision, préparation, autorisation, dépôt humain et retour d’expérience.

## 2. Objets métier

### 2.1 Affaire

L’Affaire est l’unité de travail principale. Elle porte un périmètre connu, ses lots, son origine, son cycle, ses versions documentaires, ses décisions, ses tâches et ses preuves.

La création initiale est progressive : elle ne requiert pas une fiche Entreprise complète et reste idempotente. Une réponse réseau inconnue conserve les mêmes identifiants et ne présume aucun succès.

### 2.2 Mémoire Entreprise

La Mémoire Entreprise conserve des capacités, preuves, documents, versions et retours réutilisables. Un élément expiré, non validé, hors périmètre ou contradictoire reste visible dans son état réel.

Un retour d’expérience `CASE_ONLY`, `LOT_PATTERN` ou `ENTERPRISE_PATTERN` ne devient une règle réutilisable qu’avec sa portée, sa source et sa validation exigées.

### 2.3 Source, version et preuve

Toute conclusion importante garde sa source, sa version, son hash ou son locator lorsque ces informations existent. Une rectification invalide uniquement les conclusions qui en dépendent ; elle n’efface ni l’ancienne version ni l’historique.

## 3. Autorité et rôles

| Acteur | Autorité gelée |
|---|---|
| Propriétaire organisationnel | Autorité de continuité de l’organisation ; distincte du rôle Patron. |
| Patron administrateur | Décisions, revue économique, P3/P5, entreprise, partage sensible, dépôt autorisé et validation finale selon capacité. |
| Patron délégué | Capacités explicitement déléguées, bornées par durée, périmètre, affaire et action. |
| Responsable | Collaborateur opérationnel avec affectation et actions assignées ; aucun pouvoir Patron implicite. |
| Expert | Collaborateur opérationnel spécialisé ; même frontière d’autorité, avec périmètre assigné. |
| Support | Peut participer aux procédures de continuité prévues ; ne devient jamais acteur métier par récupération. |
| Tiers externe | Destinataire ou source ; aucune réception, validation ou identité n’est inventée. |

Le serveur résout tenant, identité, membership, rôle, profil, affectation, délégation, MFA et périmètre. Le navigateur ne peut ni les déclarer ni les élever.

## 4. Cycle produit d’une Affaire

```text
observation / demande
  → qualification humaine P0/P1
  → réception et admission du DCE
  → extraction, classification et exigences sourcées
  → P2 / P3 / P4 avec inconnus et risques visibles
  → prix, capacités et réponse technique sous confidentialité
  → candidate et manifeste exact
  → signatures séparées et autorisation P5
  → export local et dépôt humain externe
  → preuve de réception PARTIAL ou UNKNOWN
  → résultat par lot, P6, P7, REX et clôture
```

Les portes P0 à P7 sont distinctes. Une porte non démontrée reste bloquante ou `PARTIAL`; aucune porte n’est franchie par score, absence d’erreur ou convention d’interface.

## 5. Sources, inconnus et contradictions

- une source BOAMP publique peut être observée et triée avec un score explicable, mais sa qualification est humaine ;
- un DCE protégé, illisible, incomplet ou hostile reste dans un état de revue ou de blocage ;
- une contradiction conserve ses deux sources et exige une résolution motivée ;
- une échéance absente reste `UNKNOWN` ;
- une capacité non couverte devient un `CAPABILITY_GAP` avec source et action de revue ;
- un contenu hostile n’est ni exécuté ni transmis à un moteur IA ;
- une panne de source ou d’IA ouvre une voie manuelle visible sans masquer l’échec.

## 6. Confidentialité et absence de déduction

Les données financières privées comprennent notamment prix, coûts, marge, trésorerie, devis, réserves et capacité économique détaillée. Elles sont Patron-only et ne traversent pas les contrats Collaborateur.

Les surfaces Collaborateur peuvent montrer les exigences, tâches, sources, états et limites de leur affectation, jamais les totaux financiers ou les décisions Patron.

Un score public ne déduit jamais une rentabilité, une capacité financière, une aptitude juridique ou une probabilité de gain. Une absence de donnée ne vaut ni zéro ni conformité. Une capacité prouvée ne vaut pas réservation. Une prévision de trésorerie ne vaut pas financement sécurisé.

## 7. Sécurité, sessions et continuité

- une session `PASSWORD` reste limitée jusqu’à MFA ;
- les opérations sensibles exigent un step-up MFA récent ;
- la récupération exige une preuve d’identité et révoque les sessions et refresh tokens ;
- l’email seul et le code de secours seul ne récupèrent pas l’accès métier ;
- une suspension révoque les sessions et délégations applicables ;
- `NO_ACTIVE_OWNER` bloque honnêtement l’autorité sans récupération implicite ;
- les actes de propriété, suspension, délégation, relève, récupération et partage sont append-only et idempotents.

## 8. Expérience, espaces et parcours

Les espaces canoniques C00–C16 et les 104 surfaces du catalogue restent la carte de navigation. Les actes sensibles sont présentés comme étapes distinctes : préparer, contrôler, autoriser, exporter, déposer humainement et rapprocher une preuve.

Les PUX-01 à PUX-19 restent la liste de parcours de référence. Les parcours non entièrement prouvés gardent leur statut `PARTIAL`; le Product Freeze ne les transforme pas en fonctionnalités terminées.

Le langage gelé privilégie « À vérifier », « À résoudre », « Inconnu », « Revue requise », « Résultat non confirmé » et « Dépôt externe non effectué ». Les termes « validé », « envoyé », « conforme » et « prêt » exigent leur preuve propre.

L’interface doit rester utilisable au clavier, avec focus visible, labels natifs, erreurs annoncées, contraste contrôlé, reflow responsive et absence d’action cachée derrière la couleur seule.

## 9. IA et documents

L’IA est une capacité contextuelle sous preuve, jamais une autorité autonome. Elle peut extraire, classer, rechercher et proposer ; elle ne décide pas seule, ne dépose pas, ne modifie pas l’historique et ne transforme pas une instruction hostile en commande.

Les documents originaux, versions, ancres, fragments, hashes, classifications et exclusions sont conservés selon leur contrat. Un brouillon dérivé porte sa source et son statut de revue.

## 10. Périmètre V1 gelé

### Indispensable

- identité, MFA, récupération et organisation tenant-scoped ;
- Affaire progressive et idempotente ;
- observation BOAMP, qualification humaine P0/P1 et conversion sourcée ;
- réception DCE, admission, extraction, classification, exigences et inconnus ;
- décision GO/NO-GO, risques, contradictions et portes P2–P4 ;
- prix privé, capacités versionnées et couverture économique Patron ;
- réponse technique versionnée, candidate, manifeste et autorisation P5 ;
- export local, dépôt humain et preuve `PARTIAL`/`UNKNOWN` ;
- résultats par lot, P6/P7, REX, suspension, fermeture et conservation ;
- gouvernance C14–C16, partage borné et résolution N01/N02 ;
- accessibilité et responsive des surfaces validées.

### V1.x ou plus tard

- SSO et intégrations externes avancées ;
- connecteurs de portail et réception automatisée ;
- partenaires/groupements avec mandats structurés ;
- écrans d’administration complets ADM-01 à ADM-10 ;
- manifeste Golden DCE réel et évaluation de compréhension sur corpus propriétaire ;
- automatisation juridique, purge physique ou conservation légale autonome.

## 11. Contrat de changement

Une modification qui change un rôle, une porte, un état, une source de vérité, une classification, une séparation d’actes, un refus ou une déduction autorisée exige :

1. une nouvelle version du Product Freeze ou un ADR explicitement relié ;
2. l’impact sur le catalogue, les parcours, les preuves et le code ;
3. des tests de refus, confidentialité, idempotence et résultat inconnu ;
4. une revue propriétaire lorsque le comportement produit change.

Aucune divergence silencieuse entre ce document, le code et les tests n’est acceptée.

## 12. Références de consolidation

- `docs/00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_CONSOLIDATED_v0.4.md`
- `docs/00_REFERENCE_ACTIVE/SMART_AO_Catalogue_Ecrans_Parcours_Produit_OWNER_CONSOLIDATED_v0.3.md`
- `docs/03_PRODUCT_DESIGN_WORKING/SMART_AO_UX_FREEZE_GLOBAL_v0.1.md`
- `docs/03_PRODUCT_DESIGN_WORKING/SMART_AO_G01_G09_OWNER_EXPERIENCE_FREEZE_v0.1.md`
- `docs/03_PRODUCT_DESIGN_WORKING/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md`

## 13. Décision attendue

Le propriétaire doit confirmer que ce candidat v1.0 remplace bien le v0.4 comme source de vérité produit/métier. Jusqu’à cette confirmation, le v0.4 reste prioritaire en cas de contradiction.
