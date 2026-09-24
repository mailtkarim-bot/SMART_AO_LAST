# SMART AO — Delta d'autorisation v2

**24 septembre 2026 · proposition T0**  
Code vérifié : `backend/app/platform/security/context.py`, `authorization.py`, `capabilities.py`, services `decision` et `dce`. L'acteur, le tenant, l'affectation et la MFA sont résolus côté serveur.

| Acte/donnée v2 | Acteur proposé | État de preuve et règle avant implémentation |
|---|---|---|
| Faits/sources non financiers sur Affaire | Collaborateur affecté, Expert dans sa portée | Réutiliser scope d'affectation. Aucun accès inter-tenant, même via compteur/erreur. |
| Dérogation, sanction, délai de droit | Contribution experte limitée ; arbitrage Patron/délégation explicite | **Nouveau contrat** : saisie/revue/acceptation distinctes, step-up pour l'acceptation sensible. |
| Marge, cash, exposition financière | Patron administrateur selon politique existante | `FINANCIAL_PRIVATE` interdit au Collaborateur dans `AuthorizationPolicy`. Ne pas élargir à un Expert DAF sans décision produit et politique explicite. |
| Assurance/QSE/juridique sensible | Expert assigné pour avis, Patron pour décision | Classification dédiée ou combinaison des classifications existantes à décider ; `PERSONAL_OR_ADMINISTRATIVE` et `SECURITY_RESTRICTED` ne sont pas synonymes de « juridique ». |
| Carte 12 axes | Patron, éventuellement vue Collaborateur épurée par contrat séparé | Filtrer **avant** agrégation/retrieval. Aucun champ financier, compteur ou statut permettant une inférence dans la réponse non autorisée. |
| Paquet P7 et calendrier des droits | Patron/acteur de passation nominativement habilité | Destinataire, portée, accusé d'acceptation et droit d'éditer doivent être explicitement décidés. |
| Support/tiers | Aucun pouvoir métier implicite | Garder procédures bornées de continuité et partage, sans lecture de contenu par défaut. |

**Tests requis :** autre tenant, rôle inférieur, délégation expirée, MFA absente/périmée, affectation révoquée, objet financier caché dans une projection mixte, recherche/IA/export, refus neutre. Aucun de ces tests spécifiques v2 n'est déclaré vert aujourd'hui.
