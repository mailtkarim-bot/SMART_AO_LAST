# C1/C5 — preuve humaine d’exécution d’une action reliée par C4

**Date :** 3 octobre 2026<br>
**Statut :** audit et cadrage ; aucune implémentation C5 dans cette tranche<br>
**Base auditée :** HEAD `9c2a982` et WIP local C2/C3/C4, dont C4 non commité<br>
**Autorités :** Product Freeze PF31-03/04, Master métier M31-05 étapes 4–5, Cahier technique CT31-04/07/15

## AS-IS vérifié

- C1 enregistre une action Patron sous la condition d’une revue d’applicabilité courante `APPLICABLE_TO_HANDOVER`. Sa projection reste `RECORDED` ; le texte, la date déclarée et les `evidence_refs` décrivent l’intention enregistrée, pas une exécution constatée.
- C4 est un acte relationnel distinct qui relie une action C1 exacte à des actes C3 exacts. `LINKED` établit une relation humaine déclarée ; il ne modifie ni C1/C3 ni l’état de l’action.
- `ContractExecutionEvidenceRecord` est un acte tenant/Affaire-scoped voisin. Il impose un type parmi `WORK_RECEPTION`, `RIGHTS_PRESERVATION`, `CONTRACT_EXIT`, un résumé, des références de source et de preuve, et une date éventuelle. Il ne référence pas d’action C1 ni de relation C4 exacte.
- Le lecteur des actes d’exécution expose les références persistées et la version d’instrument applicable ; il ne résout pas ces références en pièce réellement présente et vérifiée. Leur présence en base ne prouve donc pas la récupération d’un document.
- Le cycle `PostReceptionObligationTransition` peut exiger au moins une chaîne `evidence_ref` pour une transition `COMPLETED`. Ce contrôle garantit une référence déclarée non vide, pas l’existence, l’intégrité ni la consultation de la pièce.
- Le reçu P5/manifeste et ses empreintes concernent la soumission. Son contrat distingue déjà l’état technique `NOT_PERFORMED` d’une réception externe ; ce flux n’est pas un registre générique d’exécution d’action après attribution.
- Les références DCE ont des versions/hash documentaires, mais leur stockage et leur portée restent liés au DCE. L’audit n’a pas établi de registre générique de pièces d’exécution post-attribution, tenant/Affaire-scoped, que C5 pourrait prétendre interroger.

## Risques et distinctions métier

Les quatre affirmations ci-dessous sont indépendantes. Aucune ne doit être inférée de la précédente :

1. **Intention** — l’action demandée ou enregistrée en C1, liée aux impacts C3 par C4.
2. **Réalisation déclarée** — une personne dit avoir exécuté tout ou partie de l’action, ou dit ne pas l’avoir exécutée. Cette déclaration reste attribuée à son auteur et à sa date ; ce n’est pas une vérification.
3. **Preuve retrouvée** — une pièce identifiée a effectivement été résolue depuis une source autorisée et son identité/intégrité contrôlée selon le contrat de cette source. Une URL, un chemin, un locator, un hash saisi librement ou un `evidence_ref` non résolu ne sont que des références déclarées.
4. **Confirmation externe** — une réponse ou un accusé de réception externe a été reçu et relié à une source exacte. Une preuve interne de réalisation ne démontre ni transmission, ni réception, ni acceptation par un tiers.

Risques à prévenir : afficher « terminé » après simple déclaration ; convertir absence de pièce en échec ou succès ; assimiler hash déclaré à hash recalculé ; confondre remise/envoi et accusé reçu ; laisser une révision C4 obsolète paraître encore applicable ; mélanger cette preuve à C1/C3/C4 ou écraser leurs actes ; exposer une pièce d’un autre tenant ou contourner `FINANCIAL_PRIVATE`.

## Décision de cadrage proposée — acte C5 distinct

Créer, après validation de ce cadrage dans le plan d’implémentation, un acte humain C5 append-only qui documente l’exécution déclarée d’une action C1 exacte, avec référence obligatoire à l’acte C4 exact ayant relié cette action aux impacts C3. C5 ne réécrit et ne clôt aucun acte antérieur.

Identifiants d’ancrage proposés : `action_id`, `c4_relation_id` (ID de la révision C4 parent), tenant, Affaire et événement dérivés/validés côté serveur. L’acte conserve l’acteur, l’horodatage serveur, le motif et la révision attendue. La référence à C4 doit être contrôlée comme appartenant à la même action, au même événement, à la même Affaire et au même tenant. Une relation C4 devenue `REVIEW_REQUIRED` reste consultable dans son état historique ; C5 ne la rend pas courante par sa seule existence.

Le contenu garde trois champs d’état indépendants et fermés :

| Axe | Valeurs de cadrage | Sens et garde |
|---|---|---|
| Réalisation déclarée | `DECLARED_PERFORMED`, `DECLARED_PARTIAL`, `DECLARED_NOT_PERFORMED`, `UNKNOWN` | Déclaration humaine attribuée ; `UNKNOWN` est obligatoire lorsque le déclarant ne peut établir l’état. Ne jamais projeter `COMPLETED` comme fait vérifié. |
| Pièce | `UNKNOWN`, `REFERENCED`, `RETRIEVED` | `REFERENCED` signifie seulement qu’un locator a été déclaré. `RETRIEVED` exige que le serveur retrouve une pièce via une source autorisée et vérifie son identifiant/version/hash conformément au contrat de cette source. Sans intégration probante disponible, rester `UNKNOWN` (ou `REFERENCED` si un locator existe). |
| Confirmation externe | `UNKNOWN`, `NOT_CONFIRMED`, `CONFIRMED` | Un acte distinct de confirmation, sa source exacte et sa date sont nécessaires pour `CONFIRMED`. C5 n’envoie rien et ne sonde aucun tiers. Une pièce interne retrouvée ne suffit pas. |

Le résumé et les références de source restent visibles, mais ne remplacent pas ces états. Les dates sont déclarées ou horodatées comme telles ; aucun délai, effet juridique, paiement, préservation de droit ou réception n’est calculé. Le terme `CONFIRMED` décrit uniquement l’existence d’une confirmation externe sourcée, pas la validité juridique de l’exécution.

## Frontière d’intégration minimale

- **Propriétaire provisoire :** module `pricing`, au voisinage des actes C1–C4 et des actes d’exécution actuels ; l’audit ne justifie pas un nouveau bounded context.
- **Persistance :** migration additive C5 et actes immuables. Éviter d’ajouter des colonnes à C1/C3/C4 ou de transformer leurs listes de références historiques.
- **Écriture :** commande Patron sous la politique existante `FINANCIAL_PRIVATE`, avec idempotence et contrôle de révision. Aucune commande ne déclenche l’action C1, une notification ou une communication externe.
- **Projection :** actes C5 affichés séparément dans C07/C12 ; état de liaison C4 courant/à requalifier projeté séparément des faits déclarés C5. Une nouvelle revue C1/C4 rend le lien signalable comme obsolète sans altérer le dossier C5.
- **Pièce :** avant de permettre `RETRIEVED`, définir une source effectivement exploitable et son adaptateur de vérification. Tant que ce point n’est pas résolu, C5 peut enregistrer la déclaration et une référence, mais ne doit pas prétendre avoir retrouvé la pièce. Ne pas créer un stockage générique dans cette tranche par anticipation.
- **Confirmation :** future commande humaine append-only, uniquement si un flux de confirmation exact est défini. Pas de connecteur externe ni de polling implicite dans C5.

## Preuves à exiger pour l’implémentation C5

| Cas | Preuve attendue |
|---|---|
| Déclaration nominale sans locator/pièce | HTTP/PostgreSQL : déclaration conservée, axe pièce et confirmation `UNKNOWN`, C1 `RECORDED` et C4 inchangés |
| Réalisation partielle, non réalisée et inconnue | états distincts, auteur/date/motif conservés ; aucune projection « terminée » |
| Référence présente, source indisponible ou identité/hash discordant | `REFERENCED`, `UNKNOWN` ou état d’échec de vérification fermé selon contrat ; jamais `RETRIEVED` sur seule saisie du locator/hash |
| Confirmation externe absente | reste `UNKNOWN` même si la réalisation est déclarée et la pièce interne retrouvée |
| Intégrité et permissions | refus action/C4 d’un autre tenant/Affaire/événement, relation C4 incohérente, Collaborateur et rôles non autorisés ; aucune fuite dans erreur/compteur |
| Révision et rejeu | clé idempotente stable, rejeu sans doublon, conflit `expected_revision` refusé ; aucune réécriture d’actes |
| Obsolescence | nouvelle revue C1 ou C4 projetée séparément comme `REVIEW_REQUIRED`; la déclaration C5 et ses sources restent historiques |
| Non-déclenchement | tests prouvant absence d’envoi, notification, exécution de l’action et appel externe |
| Projection | API et UX distinguent intention C1, relation C4, déclaration C5, pièce retrouvée et confirmation externe sans fusion d’historiques |

## Limites et questions techniques ouvertes

1. Le dépôt ne fournit pas encore, selon cet audit, de registre générique résolvant les références de pièces d’exécution post-attribution. Le contrat de source permettant de prouver `RETRIEVED` doit être choisi depuis une source réellement disponible ; aucune source ni fichier ne doit être inventé.
2. Les enums ci-dessus sont un cadrage destiné à la tranche d’implémentation, pas un contrat déjà accepté par le code ni une conclusion juridique.
3. `NOT_CONFIRMED` doit signifier qu’un humain a explicitement déclaré l’absence de confirmation ; l’absence d’enregistrement reste `UNKNOWN`.
4. L’audit est local. Aucun navigateur CUA, service de stockage réel, compte tiers, environnement VPS ou corpus chantier client n’a été utilisé.

**Non-objectifs :** modifier ou recalculer C1/C3/C4 ; marquer C1 terminé ; exécuter l’action ; transmettre ou notifier ; affirmer réception, paiement, conformité ou préservation d’un droit ; calculer une échéance juridique/financière ; promouvoir un état inconnu.

**NO-GO public maintenu.** Aucun code de production, schéma, migration ou acte métier n’a été modifié pour ce cadrage.
