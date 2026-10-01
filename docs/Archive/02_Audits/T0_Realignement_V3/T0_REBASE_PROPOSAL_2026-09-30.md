# Proposition de réalignement SMART AO — après audits T0

**Statut :** recommandation pour revue propriétaire ; V3 reste candidat.  
**Décision courte :** **oui au pivot stratégique, non à une promotion ou réécriture immédiate.**

## Ce que je recommande

1. **Déplacer le message produit** de « l’IA lit le DCE » vers « SMART AO maîtrise l’engagement de l’Affaire avant et après attribution ». C’est cohérent avec vingt ans de pratique BTP et avec la pression concurrentielle désormais publique.
2. **Garder le DCE comme entrée**, et faire du lien longitudinal la valeur : source/version → applicabilité humaine → obligation/droit/inconnu → impact/hypothèses → décision/condition P3 → offre/contrat attribué → événement réel → action/preuve → REX.
3. **Traiter le graph comme modèle logique**, pas comme choix technique. Le modular monolith, les FK/événements existants et des read models bornés sont le premier chemin ; pas de graph DB, microservices ou nouveau `Engagement Control` module avant code map/mesure.
4. **Construire une seule verticale à la fois :** A « Avant de signer » d’abord; B « Si nous gagnons » ensuite; C « Quelque chose change » après la preuve A/B. Les 104 surfaces restent un contrat de couverture, pas 104 étapes de livraison séquentielles.
5. **Ne pas déplacer Payment maintenant.** Le modèle actuel prouve une prudence et une revue humaines, mais pas encore un settlement structuré. Établir ownership par event/consumer et contrat de projection avant tout MOVE.
6. **Faire du benchmark un gate de qualité**, sans en faire le premier produit. Mesurer la vérité terrain : source/version, applicabilité, omission/faux positif, lien d’impact, abstention UNKNOWN et temps de revue. Comparer avec vendors seulement sur corpus permis/expurgé et sans revendiquer de supériorité sur la base des pages marketing.

## Ce qu’il faut changer dans les documents après décision

Ne pas publier cinq références de même rang. Utiliser une autorité par question :

| Question | Document canonique après promotion |
|---|---|
| Quel produit et quelles limites ? | un seul Product Freeze v3.0, Owner-promu |
| Quelle profondeur/matière métier ? | Master métier comme annexe/référence de détail, sans autorité concurrente |
| Comment l’implémenter ? | un seul Cahier technique v3.0 dérivé, réconcilié avec l’architecture v3.1 |
| Quelles surfaces/parcours ? | catalogue UX v0.3 mis à jour seulement si le contrat change |
| Quel travail maintenant ? | plan global + T0 traceability matrix, synchronisés |

Avant cela, conserver v2.0/v2.1 comme actifs. Le paquet V3 doit corriger d’abord les chemins absents du README, la numérotation/ancres du Master métier et le pied de page technique V2.1 résiduel, puis fournir un vrai delta `KEEP / CHANGE / DEFER / OWNER_REOPEN_REQUIRED` contre les autorités v2.

## Première tranche Deep Core recommandée

Réutiliser la preuve `ContractBaselineDeviationImpact` existante et la preuve `ContractInstrumentVersion`; ne pas ajouter un aggregate simplement nommé `ContractBaseline` sans clarifier les deux baselines métier :

- **avant attribution :** termes et versions du DCE examinés, encore candidats ;
- **après attribution :** marché/avenant signé et version identifiée, autorité contractuelle déclarée par preuve.

Premier parcours vérifiable : un élément contractuel sourcé dans une version DCE → applicabilité déclarée par le Patron → écart ou UNKNOWN → un impact business borné (coût, cash, délai ou capacité, avec hypothèses et source) → condition P3 lisible et arbitrée humainement. Puis tester rectificatif/version, refus, source absente, retry et confidentialité.

Ce parcours comble le vrai gap sans prétendre produire un avocat, un moteur de deadlines ou un ERP. Le basculement après attribution (Vertical B) réutilisera ensuite les versions signées/supersessions déjà présentes; les OS seront un objet C dédié seulement après ce chaînage.

## Arbitrages propriétaires à trancher avant promotion

- Le centre de gravité « système de maîtrise des engagements BTP » est-il accepté comme promesse v3 ?
- Les trois verticales sont-elles bien ordonnées A → B → C, avec A comme seule première preuve produit ?
- Le Parity Core reste-t-il maintenu uniquement lorsqu’il bloque une vente, une tâche Deep Core ou une obligation ?
- Le benchmark externe se limite-t-il initialement aux sources publiques/licenciées, aux données expurgées et aux vendors accessibles sans téléverser de DCE client ?
- Le Master métier v3 est-il un document de profondeur non autoritaire (recommandé) ou une seconde autorité produit ?

Jusqu’à ces réponses, le Product Freeze v2.0 reste l’autorité. Aucun Product Freeze/Index actif n’est modifié par cette proposition.
