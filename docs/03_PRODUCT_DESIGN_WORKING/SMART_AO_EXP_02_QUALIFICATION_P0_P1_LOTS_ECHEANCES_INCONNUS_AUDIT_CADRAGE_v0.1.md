# SMART AO — EXP-02 : qualification P0/P1, lots, échéances et inconnus

**Statut :** AUDITÉ · CONTRAT IMPLÉMENTÉ · PREUVE VERTICALE PROUVÉE
**Date :** 14 septembre 2026
**Autorité produit/métier :** `SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md`
**Référence UX :** `SMART_AO_Catalogue_Ecrans_Parcours_Produit_OWNER_CONSOLIDATED_v0.3.md`
**Tranche :** EXP-02, après la preuve nominale observation BOAMP → Affaire idempotente

## 1. Décision de cadrage

Le cahier OWNER v0.4 donne le contrat métier minimal des portes P0 et P1 dans R04 :

- **P0 — Cibler :** une opportunité est identifiée ; les critères commerciaux ou les inconnus sont visibles ; le Patron ou son délégataire suit, qualifie ou écarte avec motif.
- **P1 — Ouvrir :** un dossier est reçu ou une phase de candidature est documentée ; les lots, le responsable et l’échéance sont connus ou leur absence est signalée ; le Patron ou son délégataire autorise l’effort d’étude et l’Affaire s’ouvre avec ses manques.

Pour la première preuve BOAMP, ces portes deviennent les états observables suivants :

| Porte | État minimal | Déclencheur dans le code actuel | Sens métier |
|---|---|---|---|
| P0 | `UNREVIEWED`, `TARGETED`, `SNOOZED`, `DISCARDED` | absence ou dernière qualification `QUALIFIED` / `SNOOZED` / `REJECTED` | `TARGETED` signifie « signal retenu pour étude », jamais GO/NO-GO |
| P1 | `NOT_OPEN`, `OPEN_WITH_UNKNOWNS` | absence ou création d’une Affaire depuis l’observation | `OPEN_WITH_UNKNOWNS` autorise l’étude préparatoire, pas le prix, la remise ou un engagement |

La création d’une Affaire depuis une observation `QUALIFIED` est donc l’acte P1 de cette tranche. Elle reste une ouverture préparatoire, puisque BOAMP ne fournit actuellement ni DCE ni périmètre de lot exploitable.

P0/P1 restent des portes métier. Ils ne doivent pas être confondus avec `UX-Critical`/`UX-Primary`/`UX-Support`, C1/C2/C3 ou B0/B1/B2.

## 2. Audit du code vivant

| Sujet | Fait vérifié | Écart à traiter |
|---|---|---|
| Source | `BoampReadOnlySearch` appelle l’API Explore en HTTPS avec une allowlist fermée : `idweb`, `objet`, `dateparution`, `datelimitereponse`, départements, type de marché, état. | Aucun champ de lot, de dossier reçu, de responsable ou de provenance de délai n’est admis. |
| Ingestion | `BoampOpportunityIngestionService` borne les pages, mots-clés et résultats, normalise les dates en UTC, filtre les échéances passées et déduplique par `source_notice_id`. | La normalisation perd le fuseau fourni par la source ; un délai absent est seulement `None`, sans état métier explicite. |
| Persistence | `BoampOpportunityObservationRecord` conserve avis, empreinte, score explicable et `observed_at`. La qualification append-only conserve décision, motif, acteur et identifiants d’idempotence ; l’Affaire garde `OPPORTUNITY` et `origin_reference_id`. | Les états P0/P1, lot, échéance et inconnus restent calculés à la lecture depuis ces faits persistés ; aucune table de projection supplémentaire n’est nécessaire pour cette preuve. |
| Lecture patronale | `PatronBoampObservationProjection` est tenant-scopée et publie la fraîcheur, la dernière qualification, l’état d’Affaire, le périmètre de lots, l’échéance et les inconnus. | Les inconnus d’ouverture ne sont émis qu’après création de l’Affaire ; avant P1, la fiche expose leur absence sans les inventer. |
| P0 | `QUALIFIED`, `SNOOZED` et `REJECTED` sont fermés et validés serveur ; seul `PATRON_ADMIN` peut qualifier aujourd’hui. | Le sens P0 n’est pas visible comme tel dans la réponse ou la fiche après rechargement ; la délégation P0 du v0.4 n’est pas encore implémentée. |
| P1 | `BoampCaseCreationService` exige une qualification `QUALIFIED`, crée une Affaire idempotente `OPPORTUNITY` et utilise `scope_kind=CUSTOM` avec justification de confirmation du DCE et des lots. | L’ouverture P1 n’est pas nommée dans le reçu et les manques ne forment pas encore un registre lisible. |
| Lots | `CreateCaseCommand` sait porter `SINGLE_LOT`, `MULTI_LOT`, `TRANCHE`, `VARIANT` ou `CUSTOM`. | Le chemin BOAMP ne peut pas inventer de lot : l’observation n’en contient aucun et l’Affaire est volontairement `CUSTOM`. |
| Échéances | `response_deadline` est conservée comme instant, affichée séparément de `observed_at`, et les avis déjà expirés sont écartés à l’ingestion. | La projection expose désormais `KNOWN`, `MISSING` ou `EXPIRED`, la source BOAMP et la normalisation UTC ; `CONFLICTING` et le fuseau civil source restent parqués faute de seconde source. |
| Inconnus | C05 et les décisions savent transporter des éléments inconnus ; les bloqueurs de tâche ont un état et un responsable. | L’ouverture BOAMP expose maintenant des inconnus structurés et fermés (`LOT_SCOPE`, `DCE_NOT_RECEIVED`, et `DEADLINE_MISSING` si besoin) sans recréer le registre C05. |
| Panne et fraîcheur | `observed_at`, l’empreinte et le statut de source rendent la collecte observable ; l’adaptateur peut refuser une source. | Le dernier succès et la date de réexamen ne sont pas encore un contrat de Radar ; ce sujet reste distinct de cette tranche. |

## 3. Contrat minimal retenu pour la prochaine preuve

La prochaine preuve ajoute une projection calculée à partir des faits déjà persistés. Elle ne crée pas de moteur de score, de nouvelle dépendance ou de table générique.

### 3.1 P0

La réponse d’une observation expose la décision la plus récente et son état P0 :

```text
p0 = {
  state: UNREVIEWED | TARGETED | SNOOZED | DISCARDED,
  decision: null | QUALIFIED | SNOOZED | REJECTED,
  reason_code: null | RELEVANT_PUBLIC_SIGNAL | INSUFFICIENT_PUBLIC_DATA
               | NOT_RELEVANT | EXPIRED,
  qualification_id: UUID | null,
  decided_at: instant | null
}
```

`TARGETED` est une qualification humaine de signal public. Il n’autorise pas le chiffrage et ne remplace pas une décision de poursuite, d’attente ou de renoncement ultérieure.

### 3.2 P1

La même projection expose :

```text
p1 = {
  state: NOT_OPEN | OPEN_WITH_UNKNOWNS,
  case_id: UUID | null,
  opened_at: instant | null
}
```

`OPEN_WITH_UNKNOWNS` est le seul état P1 émis depuis BOAMP pendant cette tranche. Un état `READY` n’est pas introduit : il exigerait au minimum un dossier reçu ou une phase de candidature documentée, un périmètre de lot et un responsable vérifiables.

Le transport HTTP aplatit volontairement ces facettes (`p0_state`, `p1_state`, `lot_scope_state`, etc.) pour rester compatible avec le contrat de lecture existant ; les valeurs et leurs contraintes restent celles du présent document.

### 3.3 Périmètre de lots

Le contrat porte un objet fermé, même lorsque la source ne donne aucune valeur :

```text
lot_scope = {
  state: UNKNOWN | IDENTIFIED | CONFLICTING | NOT_APPLICABLE,
  references: string[],
  source: "BOAMP" | null
}
```

Pour toute observation BOAMP actuelle, la sortie est `UNKNOWN`, `references=[]`, `source="BOAMP"`. Le titre, le type de marché ou le département ne peuvent pas produire un numéro de lot par inférence. `IDENTIFIED` ne sera émis qu’après ajout d’un champ source explicitement vérifié ou saisie humaine sourcée.

Le contrat HTTP transporte cette provenance sous `lot_scope_source`.

### 3.4 Échéance

La projection sépare l’état de l’échéance de sa valeur :

```text
deadline = {
  state: KNOWN | MISSING | EXPIRED | CONFLICTING,
  value: instant | null,
  source: "BOAMP" | null,
  source_timezone: string | null,
  normalized_timezone: "UTC" | null
}
```

Règles :

1. une valeur présente est affichée comme instant absolu normalisé UTC ; cette normalisation ne prétend pas conserver le fuseau civil d’origine ;
2. une valeur absente est `MISSING`, jamais une date estimée ;
3. une divergence entre avis, RC ou DCE devient `CONFLICTING` et interdit tout report automatique ;
4. un avis historique déjà dépassé peut être lu comme `EXPIRED`, mais l’ingestion courante continue de l’écarter ;
5. responsable, canal, phase/lot et date interne de sécurité deviennent obligatoires quand une échéance de dossier est créée dans C05 ; ils ne sont pas inventés dans l’observation BOAMP.

### 3.5 Inconnus explicites

Une ouverture BOAMP doit au minimum rendre visibles les inconnus qu’elle crée. Le premier contrat reste petit et réutilisable :

```text
unknown = {
  code: LOT_SCOPE | DCE_NOT_RECEIVED | DEADLINE_MISSING | DEADLINE_CONFLICT,
  missing: string,
  why_it_matters: string,
  possible_impact: string,
  responsible: string | null,
  next_action: string,
  due_at: instant | null,
  state: OPEN,
  source_ref: string
}
```

Pour le chemin BOAMP nominal, `LOT_SCOPE` et `DCE_NOT_RECEIVED` sont ouverts à la création de l’Affaire. `DEADLINE_MISSING` est ajouté seulement si `response_deadline` est absente ; `DEADLINE_CONFLICT` sera ajouté lorsque plusieurs sources seront ingérées. Une échéance inconnue porte `due_at=null` explicitement et une action de clarification ; elle n’est pas masquée par une date technique.

La résolution complète (`IN_PROGRESS`, `RESOLVED`, invalidation par rectificatif) appartient au registre C05/À résoudre. Cette tranche ne duplique pas ce registre ; elle expose les inconnus de départ et leur rattachement à la source BOAMP.

## 4. Règles d’autorité et de sécurité

- Le serveur reste l’autorité de P0 et P1 ; le navigateur ne transforme jamais une observation en `TARGETED` ou `OPEN_WITH_UNKNOWNS` sans reçu serveur.
- La liste et la fiche restent tenant-scopées, avec `PATRON_ADMIN` comme seul décideur effectivement disponible dans cette preuve. La délégation P0/P1 est reportée jusqu’à l’implémentation de ses capacités explicites.
- Le score `BOAMP_PUBLIC_V1` sert au tri et à l’explication uniquement. Il n’établit ni P0, ni P1, ni probabilité de gain.
- L’ouverture P1 ne vaut ni DCE reçu, ni conformité, ni GO de principe P2, ni prix, ni autorisation de remise.
- Un lot absent, une échéance absente ou une source contradictoire restent visibles dans la fiche et dans l’Affaire ; aucune valeur par défaut n’est présentée comme un fait.
- La provenance conserve `source_notice_id`, l’empreinte et `observed_at`. Une Affaire créée garde le lien `OPPORTUNITY` vers l’observation.
- Les décisions successives restent append-only. Une nouvelle qualification ou un rectificatif ne réécrit pas l’historique ; la projection indique la dernière décision et sa date.

## 5. Échéancier de la preuve verticale

| Ordre | Lot de travail | Sortie attendue | Échéance de tranche |
|---:|---|---|---|
| 1 | Projection P0 | dernière qualification et état `UNREVIEWED/TARGETED/SNOOZED/DISCARDED` visibles après rechargement | même tranche EXP-02 |
| 2 | Périmètre de lots | `UNKNOWN` visible, aucune référence inventée, `CUSTOM` conservé pour la Case BOAMP | même tranche EXP-02 |
| 3 | Échéance | état `KNOWN` ou `MISSING`, instant UTC séparé de la collecte, aucun report automatique | même tranche EXP-02 |
| 4 | Inconnus de départ | `LOT_SCOPE` et `DCE_NOT_RECEIVED` visibles après ouverture ; action et responsable explicites ou absence signalée | même tranche EXP-02 |
| 5 | Preuve | tests contrat/API, front, refus et PostgreSQL ; rejeu de création inchangé | fin de la tranche avant EXP-03 |

Ces échéances sont des critères de sortie de développement, pas des dates métier inventées pour un avis BOAMP.

## 6. Tests de sortie prévus

- projection sans qualification : `P0=UNREVIEWED`, `P1=NOT_OPEN`, lots `UNKNOWN` ;
- qualification `QUALIFIED` : `P0=TARGETED`, motif et identifiant visibles après rechargement ;
- qualification `SNOOZED` ou `REJECTED` : état correspondant, aucune ouverture P1 ;
- création depuis `QUALIFIED` : `P1=OPEN_WITH_UNKNOWNS`, `case_id` et inconnus de départ présents ;
- observation sans échéance : `deadline=MISSING` et inconnue dédiée, sans date calculée ;
- échéance passée stockée : état `EXPIRED`, sans conversion automatique ;
- aucune donnée de titre, département ou type de marché ne crée un lot ;
- hors tenant, mauvais rôle, absence de qualification, conflit d’idempotence et rejeu restent refusés comme dans la preuve nominale ;
- premier envoi et rejeu de création conservent la même Affaire, la même provenance et les mêmes inconnus ;
- réponse publique fermée : les nouveaux champs sont bornés et aucun champ interne n’est exposé.

## 7. Inconnus explicitement parqués

1. **Schéma BOAMP des lots :** aucun champ autorisé n’a encore été identifié dans l’adaptateur actuel ; toute extension doit être fondée sur une réponse source vérifiée et des tests de compatibilité.
2. **Fuseau civil source :** l’instant est normalisé UTC, mais le fuseau transmis par BOAMP n’est pas conservé ; ne pas afficher « fuseau source confirmé » avant de le persister.
3. **Conflit de dates :** le modèle ne lit qu’une source BOAMP dans cette preuve ; le rapprochement avis/RC/DCE appartient à l’ingestion documentaire d’EXP-03.
4. **Responsable P1 et délégation :** le chemin actuel est Patron-only ; l’affectation nominative et les capacités P0/P1 déléguées restent à cadrer avec C14.
5. **Dernier succès de source :** l’indisponibilité BOAMP et la saisie manuelle sont traitées dans une tranche Radar dédiée ; `observed_at` ne doit pas être présenté comme une garantie d’actualité.
6. **Registre C05 complet :** ce document amorce les inconnus de l’ouverture ; leur résolution, invalidation et vue « À résoudre » ne sont pas recréées ici.

## 8. Critère de clôture du cadrage

Le cadrage est considéré terminé lorsque la fiche Opportunité peut répondre, sans inférence silencieuse, à quatre questions :

1. **P0 :** le signal est-il non revu, ciblé, en attente ou écarté, par quelle décision et quel motif ?
2. **P1 :** l’Affaire est-elle encore fermée ou ouverte avec quels manques ?
3. **Lots et échéance :** que sait-on réellement du périmètre et de la date limite, avec quelle provenance et quelle incertitude ?
4. **Inconnus :** que manque-t-il, pourquoi, avec quel impact, quelle action, quel responsable et quelle échéance connue ou explicitement absente ?

La preuve nominale EXP-02 reste acquise et inchangée ; cette tranche rend ses limites métier visibles avant d’élargir le Radar ou d’ouvrir EXP-03.

## 9. Preuve exécutée et limites

- projection applicative : états P0/P1, lots `UNKNOWN`, échéances `KNOWN/MISSING/EXPIRED`, provenance et inconnus d’ouverture structurés ;
- front ciblé : affichage P0/P1, lot, échéance, inconnues après ouverture et masquage de la conversion déjà ouverte ; **10 tests passés** ;
- backend ciblé : projection sans qualification, qualification + Affaire, échéance absente et contrôles de rôle ; **5 tests passés** ;
- PostgreSQL dédié `smart-ao-v8-postgres:5433` : qualification, création/rejeu d’Affaire et relecture de projection ; **4 tests passés** ;
- TypeScript, ESLint, build Vite et Ruff sur les fichiers touchés : passés ;
- la sous-suite historique HTTP avec `TestClient` reste non exploitable dans ce checkout : elle se bloque pendant le premier test ; un endpoint réel sous Uvicorn a toutefois confirmé `401` sans bearer et `200` avec `P0=UNREVIEWED` malgré un score élevé ;
- les lots identifiés, les dates contradictoires, le fuseau civil BOAMP, la délégation P0/P1 et le registre C05 restent parqués conformément au cadrage.

## 10. Étape suivante

Le détail de cette décision est cadré dans [`SMART_AO_EXP_02_DECISION_POURSUIVRE_ECARTER_AUDIT_CADRAGE_v0.1.md`](SMART_AO_EXP_02_DECISION_POURSUIVRE_ECARTER_AUDIT_CADRAGE_v0.1.md). Le score reste un tri explicable ; `TARGETED`, `DISCARDED`, `SNOOZED` et l’ouverture P1 sont les actes humains disponibles avant la décision formelle d’Affaire.

La prochaine tranche complète la preuve de transformation idempotente en Affaire sans doublon ni perte de source.
