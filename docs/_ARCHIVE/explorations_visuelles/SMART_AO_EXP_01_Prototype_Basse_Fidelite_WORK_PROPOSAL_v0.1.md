# SMART AO — EXP-01 Prototype basse fidélité
## WORK_PROPOSAL v0.1

**Date : 14 septembre 2026**  
**Statut : PROTOTYPE CANDIDATE — textuel, non visuel, non normatif**  
**Référence de contenu :** [EXP-01 — Expériences utilisateur, parcours et contrats de pages](../work_reviews/SMART_AO_Experience_Utilisateur_Parcours_Pages_WORK_PROPOSAL_v0.1.md)

## Objet

Ce prototype vérifie l’enchaînement de `PAGE-001` à `PAGE-007` avant toute maquette détaillée. Il ne fixe ni la charte graphique, ni les dimensions, ni les composants techniques. Chaque libellé et comportement doit rester cohérent avec le contrat EXP-01 ; une divergence est un écart à corriger ou à arbitrer.

## Parcours à manipuler

```text
Premier Propriétaire provisionné
PAGE-001 → PAGE-002 activation MFA → PAGE-003 contexte
→ PAGE-004 minimum entreprise → PAGE-005 profil
→ PAGE-006 première Affaire → PAGE-007 Accueil

Utilisateur invité
PAGE-001 depuis lien → PAGE-002 challenge MFA → PAGE-003 contexte
→ PAGE-006 ou PAGE-007 selon son périmètre

Reprise
session expirée → PAGE-001 → PAGE-002 → retour au dernier état confirmé
```

## PAGE-001 — Connexion

```text
┌─────────────────────────────────────────────────────────────┐
│  SMART AO                                                     │
│                                                               │
│  Accéder à votre espace                                       │
│  Votre accès est organisé par votre entreprise ou invitation. │
│                                                               │
│  Adresse professionnelle                                      │
│  [________________________________________________________]   │
│                                                               │
│  Mot de passe                                                 │
│  [________________________________________________________]   │
│                                                               │
│  [ Continuer ]                                                │
│                                                               │
│  Besoin d’aide pour accéder à votre compte ?                  │
└─────────────────────────────────────────────────────────────┘
```

Le prototype doit vérifier que personne ne cherche un champ « Tenant ID », ne croit pouvoir créer librement une organisation, et comprend que l’aide ne révèle pas l’existence d’un compte.

## PAGE-002 — Activation ou vérification MFA

```text
┌─────────────────────────────────────────────────────────────┐
│  SMART AO · Sécuriser votre accès                             │
│                                                               │
│  Votre accès interne exige une vérification en deux étapes.   │
│                                                               │
│  Première activation                                          │
│  1. Associez votre application d’authentification.            │
│  2. Conservez vos codes de récupération hors de SMART AO.     │
│  3. Saisissez le code affiché.                                │
│                                                               │
│  Code de vérification                                         │
│  [______]                                                     │
│                                                               │
│  [ Vérifier et continuer ]                                    │
│                                                               │
│  Utiliser un code de récupération                             │
│  Demander de l’aide pour récupérer l’accès                    │
└─────────────────────────────────────────────────────────────┘
```

Variante utilisateur déjà enrôlé : remplacer le bloc d’activation par « Saisissez le code de votre application ». Variante invitation expirée : ne pas afficher l’entreprise, le rôle ou le privilège précédent ; proposer seulement une nouvelle invitation.

## PAGE-003 — Confirmer le contexte

```text
┌─────────────────────────────────────────────────────────────┐
│  SMART AO · Votre espace                                      │
│                                                               │
│  Vous allez accéder à                                         │
│  [ Entreprise active ]                                        │
│                                                               │
│  Votre rôle effectif                                          │
│  [ Propriétaire d’organisation ]                              │
│  [ Patron ]                                                   │
│                                                               │
│  Vos droits sont déterminés par votre rôle, votre périmètre   │
│  et vos autorisations. Ils peuvent être distincts.            │
│                                                               │
│  [ Confirmer et continuer ]                                   │
│  Ce contexte n’est pas le bon                                 │
└─────────────────────────────────────────────────────────────┘
```

Le prototype vérifie que le cumul Propriétaire/Patron est compris sans laisser croire qu’il donne accès aux données Direction ou à toutes les décisions.

## PAGE-004 — Configuration minimale

```text
┌─────────────────────────────────────────────────────────────┐
│  SMART AO · Préparer votre démarrage                          │
│                                                               │
│  Quelques informations sont nécessaires avant votre première  │
│  Affaire. Le reste pourra être complété quand il sera utile.  │
│                                                               │
│  Informations d’entreprise nécessaires                        │
│  [________________________________________________________]   │
│  [________________________________________________________]   │
│                                                               │
│  [ Enregistrer et continuer vers ma première Affaire ]        │
│  Enregistrer et reprendre plus tard                           │
│                                                               │
│  Besoin d’un accompagnement ?                                 │
└─────────────────────────────────────────────────────────────┘
```

Les libellés définitifs de champ ne sont pas encore figés. Le prototype vérifie surtout que les informations différées n’empêchent pas le premier résultat utile.

## PAGE-005 — Profil personnel

```text
┌─────────────────────────────────────────────────────────────┐
│  SMART AO · Votre profil                                      │
│                                                               │
│  Identité professionnelle                                     │
│  Nom affiché [___________________________________________]   │
│  Fonction   [___________________________________________]   │
│                                                               │
│  Préférences utiles                                            │
│  Langue      [ Français ▾ ]                                   │
│  Notifications ordinaires [ Gérer ]                            │
│                                                               │
│  Sécurité et accès [ Ouvrir le parcours dédié ]               │
│                                                               │
│  [ Continuer vers ma première Affaire ]                        │
└─────────────────────────────────────────────────────────────┘
```

Le prototype vérifie que la sécurité, les droits et les préférences ne sont pas confondus. Le réglage d’un profil ne doit pas être perçu comme une modification de rôle.

## PAGE-006 — Première valeur

```text
┌─────────────────────────────────────────────────────────────┐
│  SMART AO · Commencer avec une première Affaire               │
│                                                               │
│  Quelle est votre prochaine action ?                          │
│                                                               │
│  [ Créer une Affaire ]                                        │
│    Vous connaissez déjà un projet ou une demande client.      │
│                                                               │
│  [ Ouvrir une opportunité ]                                   │
│    Une opportunité autorisée est déjà disponible.             │
│                                                               │
│  [ Rejoindre une Affaire ]                                    │
│    Une invitation ou une affectation vous attend.             │
│                                                               │
│  Aucune action disponible ? Demander l’accès adapté.          │
└─────────────────────────────────────────────────────────────┘
```

Après « Créer une Affaire », le formulaire s’ouvre avec le minimum contextuel : titre, objet, type de périmètre, lots connus, origine et justification. Les informations non connues restent explicitement inconnues ; la page ne fabrique pas un dossier artificiellement complet.

## PAGE-007 — Premier Accueil

```text
┌─────────────────────────────────────────────────────────────┐
│ SMART AO · Entreprise active · Rôle effectif · Notifications  │
├─────────────────────────────────────────────────────────────┤
│ Accueil  Opportunités  Affaires  Entreprise  Administration   │
├─────────────────────────────────────────────────────────────┤
│ Bonjour. Voici ce qui demande votre attention maintenant.     │
│                                                               │
│ À FAIRE MAINTENANT                                            │
│ [ Action autorisée ]  Pourquoi maintenant ?  [ Ouvrir ]        │
│                                                               │
│ À SURVEILLER                                                  │
│ [ Élément partiel / à revalider ] Source · version · date     │
│                                                               │
│ ÉVÉNEMENTS                                                     │
│ [ Événement récent ]  Lu/reporté ne modifie pas son statut.   │
│                                                               │
│ PROCHAINES ÉTAPES                                              │
│ [ Créer une Affaire ] [ Compléter plus tard ]                  │
└─────────────────────────────────────────────────────────────┘
```

L’état vide remplace les trois blocs par une explication claire et une action adaptée. L’Accueil ne montre jamais une urgence, un compteur ou une donnée à laquelle la personne n’a pas droit.

## Scénarios de vérification avant revue

| Scénario | Résultat attendu |
|---|---|
| Premier Propriétaire | comprend pourquoi le MFA précède l’accès ; atteint la création d’Affaire sans compléter la Mémoire Entreprise |
| Collaborateur invité | comprend son rôle et son périmètre sans voir d’information d’administration ou de Direction |
| Invitation expirée | sait demander une réémission sans savoir si le privilège précédent existe encore |
| Session expirée | se reconnecte puis revient à son dernier état confirmé ; aucun brouillon incertain n’est annoncé comme enregistré |
| Création d’Affaire ambiguë | vérifie l’état avant de recommencer ; aucune seconde Affaire n’est créée par réflexe |
| Panne IA | poursuit l’accès, la configuration et les actions manuelles sans promesse de résultat IA |

## Sortie attendue

Le prototype peut être présenté à la revue propriétaire dès que chaque scénario est parcourable. À cette étape, il devra être corrigé, puis EXP-01 pourra éventuellement recevoir le statut `OWNER EXPERIENCE FREEZE`. Les images détaillées viennent seulement après ce gel.
