# SMART AO — EXP-07 : résultat par lot — audit et preuve minimale

**Statut :** preuve verticale minimale implémentée · revue propriétaire à venir  
**Périmètre :** clôturer une tâche opérationnelle sans transformer une absence de résultat en succès.

## Contrat minimal retenu

Le résultat reste un enregistrement append-only de `CollaboratorTaskResultRecord`. Il porte désormais `lot_reference`, contrôlé contre `CaseRecord.scope_json`. Pour une affaire mono-lot, le lot est déduit de façon déterministe ; pour une affaire multi-lots, le lot doit être fourni explicitement et appartenir au périmètre connu.

La clôture exige un résultat portant un lot. Les résultats historiques sans lot ne sont pas réécrits et ne suffisent pas à clôturer une nouvelle tâche. `RECORDED`, `NOT_APPLICABLE` et `UNABLE_TO_COMPLETE` restent distincts ; aucun d’eux ne signifie attribution, commande, P6 ou P7.

## États difficiles et refus

- lot absent sur périmètre multi-lots : `LOT_REFERENCE_REQUIRED` ;
- lot hors périmètre : `LOT_NOT_IN_CASE_SCOPE` ;
- résultat absent : `EVIDENCE_OF_COMPLETION_REQUIRED` ;
- tâche déjà terminale, révision périmée, affectation inactive ou rôle insuffisant : refus existants conservés ;
- rejeu : les identifiants de commande/idempotence existants restent la preuve d’un même acte, sans nouveau succès présumé.

## Limites

Cette tranche ne crée pas encore le registre d’attribution, la commande, P6/P7, la passation patronale ni la capitalisation. Le résultat prouve seulement ce qui a été fait ou non fait pour un lot, avec sa source optionnelle et son historique.

## Preuve technique

- migration additive `20260919_0076` ;
- validation Pydantic, route HTTP et handler réutilisant les contrôles tenant/affectation ;
- clôture refusée sans résultat portant un lot ;
- aucune modification des lignes historiques.

**Prochaine étape :** transmettre uniquement les engagements réellement gagnés, avec réserves.
