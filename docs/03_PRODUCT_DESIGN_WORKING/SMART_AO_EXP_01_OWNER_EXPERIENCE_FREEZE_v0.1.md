# SMART AO — EXP-01 : OWNER EXPERIENCE FREEZE

**Statut :** OWNER EXPERIENCE FREEZE — approuvé par le propriétaire le 14 septembre 2026  
**Périmètre :** PAGE-001 → PAGE-007, invitation, récupération, contexte/rôles et reprises minimales  
**Autorités :** cahier Produit/Métier OWNER v0.4, catalogue Écrans/Parcours OWNER v0.3, dossier de revue propriétaire et preuves exécutées.

## 1. Décision de gel

Le propriétaire délègue les arbitrages d’EXP-01 à l’agent qui tient le code et approuve les décisions ci-dessous. Elles deviennent la référence d’expérience pour la rédaction du cahier technique d’exécution. Toute évolution ultérieure doit créer une nouvelle décision datée ; elle ne modifie pas silencieusement ce gel.

## 2. Contrat gelé

| Sujet | Décision approuvée | Conséquence immédiate |
|---|---|---|
| PAGE-004 / PAGE-005 | rester conditionnelles jusqu’à l’apparition d’une donnée réellement obligatoire ou d’une préférence nécessaire | aucun formulaire artificiel ni brouillon spéculatif |
| reprise après expiration | masquer immédiatement les projections métier, vider l’état local et conserver seulement le dernier contexte confirmé en mémoire ; rechargement serveur obligatoire après MFA | pas de restauration après fermeture, changement d’appareil ou changement d’identité/tenant/rôle |
| résultat inconnu | afficher « Création à vérifier » et rejouer la même intention avec les mêmes identifiants d’idempotence | aucune confirmation ou navigation avant réponse serveur confirmée |
| rôles | `PATRON_ADMIN` reste l’autorité Patron ; Responsable et Expert restent des profils de `COLLABORATEUR` sans droit supplémentaire | le navigateur ne peut ni choisir ni élever un rôle ou un périmètre |
| durée de session | conserver les durées serveur actuelles (8 h inactivité, 24 h absolues standard, 12 h privilégiées) pour cette tranche | l’écart avec la proposition 30 min / 12 h est reporté à une décision de sécurité dédiée |
| avertissement pré-expiration | ne pas l’ajouter dans EXP-01 | aucune promesse UI avant expiration ; future tranche séparée |
| suite autorisée | rédiger la maquette détaillée et le cahier technique consolidé d’EXP-01 | traduction du contrat gelé vers composants, API, données, tests et observabilité |

## 3. Preuves qui fondent le gel

- **141/141 tests front** sur 31 fichiers ; absence de session, MFA, création, Accueil, expiration, reprise et changement de rôle couverts.
- **31/31 tests backend ciblés** sur les gardes d’accès, la création et les rôles.
- Build TypeScript/Vite, ESLint et `git diff --check` réussis.
- Les preuves PostgreSQL antérieures couvrent invitation, acceptation unique, récupération, profils et idempotence ; leur rerun attend un PostgreSQL accessible.
- La suite backend non-DB complète compte 1 144 succès ; deux assertions ops historiques et deux skips PIL restent hors du gel EXP-01.

## 4. Limites maintenues

Le gel ne prétend pas livrer la persistance de brouillons, la reprise multi-appareil, l’accessibilité complète, la performance de production, la qualification juridique, la qualification Golden DCE ou un pilote utilisateur. Ces sujets restent dans le plan global et ne peuvent pas être déduits du prototype.

## 5. Références d’exécution

- [Dossier de revue propriétaire](SMART_AO_EXP_01_OWNER_REVIEW_v0.1.md)
- [Preuve de reprise et états difficiles](SMART_AO_EXP_01_REPRISE_INTERRUPTION_PREUVE_VERTICALE_v0.1.md)
- [Évaluation technique EXP-01](SMART_AO_EXP_01_Evaluation_Technique_WORK_PROPOSAL_v0.1.md)
- [Parcours et contrats de pages](../_ARCHIVE/work_reviews/SMART_AO_Experience_Utilisateur_Parcours_Pages_WORK_PROPOSAL_v0.1.md)
- [Plan global](SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md)
- [Cahier Produit/Métier OWNER v0.4](../00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md)
- [Catalogue Écrans/Parcours OWNER v0.3](../00_REFERENCE_ACTIVE/SMART_AO_Catalogue_Ecrans_Parcours_Produit_OWNER_CONSOLIDATED_v0.3.md)
