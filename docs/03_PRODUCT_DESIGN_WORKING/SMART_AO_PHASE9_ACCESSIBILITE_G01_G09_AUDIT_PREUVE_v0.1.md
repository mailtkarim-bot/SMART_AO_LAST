# SMART AO — Audit accessibilité G01–G09

**Date :** 20 septembre 2026  
**Statut :** audit code et preuve automatisée  
**Référence :** WCAG 2.2 AA, surfaces G01–G09 et shell React partagé

## Résultat

Le shell et les panneaux utilisés par G01–G09 passent les contrôles techniques ciblés : navigation native au clavier, focus visible, fermeture clavier de la boîte de connexion, annonces d’erreur, libellés de formulaires et reflow responsive. Aucun gestionnaire `onClick` n’est attaché à un `div` ou à un `span`.

## Corrections réalisées

- le focus clavier utilise un anneau `:focus-visible` de contraste élevé ; les champs n’annulent plus le focus natif ;
- la boîte de connexion possède un nom, une description, un bouton de fermeture nommé, une fermeture `Escape`, un focus initial et un piège de focus `Tab` ; le focus revient au déclencheur ;
- les erreurs globales utilisent `role="alert"`, les confirmations et états de progression restent `role="status"`, et les glyphes décoratifs sont masqués aux lecteurs d’écran ;
- les textes gris des surfaces claires ont été assombris pour atteindre le contraste normal requis ; les statuts d’avertissement et les badges utilisent des teintes plus foncées ;
- les boutons et champs restent des éléments HTML natifs, avec des cibles supérieures au minimum de 24 px ;
- les grilles existantes replient leurs colonnes à 900, 780, 650, 560 et 480 px sans supprimer de commande ni de contenu.

## Vérifications exécutées

- `pnpm lint` : vert ;
- `pnpm typecheck` : vert ;
- `pnpm test` : **187 tests réussis sur 187** ;
- `pnpm build` : vert ;
- `src/app/App.test.tsx` : **13 tests réussis**, dont ouverture accessible de la boîte de connexion, description du dialogue, fermeture `Escape`, retour du focus et annonce `role="alert"` ;
- recherche statique : aucun `onClick` sur `div`/`span`, aucun `outline: none`, anneau `:focus-visible` présent.

## Limite assumée

Cette tranche est une preuve automatisée et structurelle. Une recette manuelle avec lecteur d’écran réel et zoom navigateur reste utile avant le gel UX global ; elle ne doit pas être confondue avec un test unitaire.

## Références

- `web/src/app/App.tsx`
- `web/src/app/App.test.tsx`
- `web/src/app/styles.css`
- `docs/03_PRODUCT_DESIGN_WORKING/SMART_AO_PHASE9_G01_G09_ACTES_METIER_PREUVE_v0.1.md`
