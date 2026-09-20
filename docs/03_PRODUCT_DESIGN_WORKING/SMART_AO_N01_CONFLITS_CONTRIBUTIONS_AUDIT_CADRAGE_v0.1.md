# SMART AO — N01 : conflits de contributions

**Statut :** audit exécuté ; preuve append-only réalisée côté service et PostgreSQL  
**Autorités :** cahier OWNER v0.4 §32 et C00 ; catalogue UX OWNER v0.3, N01, C05/C07/C10 et G16/G51.

## Constat du code vivant

Le socle possède plusieurs protections utiles contre l’écrasement silencieux :

- les agrégats Case, Decision, Entreprise, affectation et préparation portent une révision courante ;
- les commandes sensibles demandent une révision attendue et lèvent une erreur de conflit optimiste lorsque la révision a changé ;
- les changements d’affectation, validations, décisions et réponses sont déjà conservés comme faits séparés ;
- les tests couvrent des rejets de révision périmée et vérifient l’absence d’effet secondaire dans plusieurs modules.

L’écart produit était net : il n’existait pas de registre transversal qui conserve deux contributions concurrentes, les auteurs, la version de départ, les validations touchées, la source et la résolution humaine. Cet écart est maintenant couvert pour le plus petit objet retenu, l’exigence DCE.

## Contrat minimal retenu

1. Une contribution conserve son auteur, son périmètre, sa version de départ, son contenu borné et ses références de source.
2. Une seconde contribution sur une version devenue obsolète crée un conflit append-only ; elle ne remplace jamais la première.
3. La lecture expose les deux propositions et les validations touchées, sans choisir automatiquement la plus récente.
4. Une résolution humaine référence les contributions retenues ou écartées, son motif, son auteur habilité et la nouvelle révision.
5. Tant qu’un conflit critique n’est pas résolu, les portes métier dépendantes restent bloquées ; un échec réseau ou un rejeu ne ferme pas le conflit.

## Plus petite preuve verticale

L’objet retenu est l’exigence DCE. La migration `20260920_0090` et le service `DceContributionConflictService` conservent deux propositions, leurs auteurs, leurs sources et la révision observée. La validation ordinaire est refusée sur conflit ouvert ; une résolution humaine append-only et idempotente lève le blocage. La preuve PostgreSQL est détaillée dans `SMART_AO_N01_OWNER_EXPERIENCE_FREEZE_v0.1.md`.

Les conflits de fichiers locaux, la fusion automatique et une IA qui arbitrerait seule sont hors périmètre.

**Prochaine étape :** ouvrir N02 sur l’issue d’opération inconnue.
