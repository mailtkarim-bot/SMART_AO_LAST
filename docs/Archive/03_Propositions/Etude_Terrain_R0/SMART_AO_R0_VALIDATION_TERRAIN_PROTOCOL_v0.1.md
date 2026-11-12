# SMART AO — protocole R0 de validation terrain

**Statut :** option de recherche future, différée faute de moyens ; ne bloque pas le codage A1
**Date :** 1er octobre 2026
**Autorités produit :** cahiers complets v3.1 dans `docs/Actifs/01_Cahiers_des_charges/`
**Sources d’orientation :** [contre-audit Smart BTP](../../../Actifs/00_Pilotage_et_audits/Veille_concurrentielle_2026-10-01/SMART_AO_COMPETITOR_SMART_BTP_DEEP_DIVE.md), [lecture et verdict](../../../Actifs/00_Pilotage_et_audits/Veille_concurrentielle_2026-10-01/SMART_AO_READ_ME_FIRST.md), [roadmap après recherche](../../../Actifs/00_Pilotage_et_audits/Veille_concurrentielle_2026-10-01/SMART_AO_RECOMMENDED_ROADMAP_AFTER_RESEARCH.md)

> Décision de pilotage du 1er octobre 2026 : les annonces publiques concurrentes sont utilisées comme hypothèses conservatrices. Les entretiens et DCE client ne sont pas un prérequis au code dans la situation actuelle. Ce protocole est conservé pour une validation terrain future.

## But

Vérifier qu’une PME BTP rencontre souvent une douleur de continuité entre l’offre, le contrat attribué, l’événement de chantier et l’action à prouver, qu’un décideur veut la résoudre, et que SMART AO peut réduire la charge face aux outils actuels.

Ce protocole ne certifie pas un marché, une supériorité concurrentielle ou une capacité logicielle complète. Le logiciel existant sert de baseline et de support de démonstration ; aucun développement de fonction élargie n’est autorisé par ce R0.

## Seuil initial de passage

R0 ne passe que si les quatre conditions sont documentées :

1. **Cinq entretiens** auprès de profils acheteur/Patron, études ou métreur, et conducteur, sur au moins deux entreprises lorsque possible.
2. **Trois DCE** utilisables avec autorisation documentée et traitement convenu ; le contenu brut reste hors de GitHub et des dossiers de documentation.
3. **Douleur récurrente :** le même type de tâche ou de rupture est rapporté spontanément par au moins 3 participants sur 5, avec un exemple récent et un coût opérationnel décrit.
4. **Acheteur identifiable :** le rôle qui peut décider du budget est connu et le mode de décision/achat est documenté ; un intérêt poli ou une demande de démonstration ne compte pas comme intention d’achat.

Les critères sont fixés avant les entretiens. Si une condition manque, le statut reste `UNKNOWN` ou `PARTIAL`, et le R0 n’autorise pas l’élargissement fonctionnel. Un pilote payé est une gate ultérieure, pas une conclusion automatique de R0.

## Entretien semi-directif — 35 à 45 minutes

Ne pas commencer par présenter SMART AO. Demander à la personne de raconter une affaire récente où une condition acceptée à l’étude a changé après l’attribution.

1. Quel était le dernier cas concret ? Quelle pièce, version ou décision a déclenché le problème ?
2. Qui a dû retrouver l’information, dans quels outils, et pendant combien de temps ?
3. Qu’est-ce qui a été vendu ou accepté, qu’est-ce qui a réellement changé, et quelle action/preuve a suivi ?
4. Qu’est-ce qui était encore inconnu ou contradictoire ? Comment l’équipe l’a-t-elle signalé ?
5. Quel a été l’effet observé : reprise de travail, coût, délai, partenaire, trésorerie ou droit à préserver ? Séparer fait observé et estimation.
6. À quelle fréquence ce cas se reproduit-il ? Qui supporte le coût et qui décide de payer pour le réduire ?
7. Quel outil ou assemblage d’outils est utilisé aujourd’hui ? Qu’est-ce qui devrait rester dans l’ERP, l’outil de prix ou le logiciel chantier ?
8. Quelle preuve ferait dire que le problème est réellement mieux maîtrisé ?

Consigner les mots de l’interviewé séparément de l’interprétation. Une réponse hypothétique (« je paierais ») n’est pas une commande. Après le récit, montrer au besoin une seule tâche existante SmartAO et noter les incompréhensions, saisies et corrections.

## Tâche comparative sur les mêmes affaires

Avec accord d’usage, sélectionner trois affaires qui couvrent les cas disponibles sans prétendre représenter tous les corps d’état. Pour chacune, exécuter les mêmes tâches avec le processus actuel de l’entreprise puis avec la version locale de SmartAO :

- retrouver la condition économique et sa source/version ;
- distinguer la clause du DCE du contrat attribué ;
- retrouver l’engagement vendu et la condition Patron ;
- retrouver un événement ultérieur et l’action/preuve associée ;
- marquer explicitement ce qui reste inconnu.

Mesurer avant la collecte : temps total, personnes et outils sollicités, interruptions/recherches, erreurs de version, données ressaisies, inconnus préservés et corrections humaines. Ne pas comparer à un concurrent sans accès autorisé à une tâche réelle ; une page publique reste une déclaration éditoriale.

## Autorisation et conservation

- Obtenir l’autorisation d’utiliser chaque DCE et préciser les personnes habilitées, la durée, le périmètre et la suppression attendue.
- Inventorier noms, signatures, coordonnées, prix et autres données sensibles ; ne pas présumer qu’un DCE est anonymisé.
- Garder les originaux et notes nominatives dans l’espace contrôlé convenu avec le propriétaire. Ne pas les copier dans ce dépôt, un ticket public, un prompt externe ou un outil tiers.
- Dans le dépôt, conserver uniquement les identifiants pseudonymes nécessaires, le manifeste expurgé, les localisateurs autorisés et les mesures agrégées validées.
- Si l’autorisation ou la provenance manque, ne pas utiliser le corpus ; inscrire `UNKNOWN` et poursuivre seulement les tâches qui n’en dépendent pas.

Aucune invitation, prise de rendez-vous, collecte auprès d’un client ou partage de fichier ne sera envoyée par Codex dans ce protocole. Le propriétaire du projet organise les entretiens et confirme les autorisations.

## Registre de résultats

Une ligne par participant et par tâche, sans identité personnelle dans Git :

| ID | Rôle/segment pseudonyme | Cas autorisé | Événement et source/version | Pain rapporté | Fréquence déclarée | Charge actuelle observée | Résultat SmartAO observé | Inconnus/corrections | Rôle budgétaire | État de preuve |
|---|---|---|---|---|---|---|---|---|---|---|
| À renseigner | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | `NOT_PERFORMED` | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` |

Ne pas transformer une absence de réponse, un scénario de démonstration ou un témoignage isolé en succès. Documenter aussi les cas où SmartAO ajoute plus de saisie qu’il n’en retire.

## Décision après R0

- **Gate atteinte :** formuler un R1 borné sur le parcours manuel avant d’ajouter de l’automatisation ; conserver A1 comme tranche fonctionnelle candidate et mesurer cinq engagements sur deux rôles.
- **Pain non récurrent ou acheteur absent :** ne pas poursuivre le même périmètre par inertie ; resserrer le segment ou le workflow et refaire une hypothèse mesurable.
- **Corpus non autorisé :** ne pas franchir la gate sur des données improvisées ; le statut corpus demeure bloqué/UNKNOWN.
- **Temps ou corrections défavorables :** corriger la tâche et la friction avant d’ajouter des fonctions.

Le verdict R0 doit rapporter les participants anonymisés, les affaires autorisées, la baseline, les écarts, les limites et une décision de poursuite/pivot. Il ne modifie pas le Product Freeze et ne lève pas le NO-GO public.
