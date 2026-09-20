# SMART AO — TRC-01 — Matrice de traçabilité normative

**Date :** 12 septembre 2026  
**Référence :** corpus v1.0/v1.1/ADR v0.1/architecture v3.1 contre `b6b05b8`  
**Statut :** TERMINÉ POUR GATE 0  
**Verdict :** chaque exigence recensée a un owner, une tranche et une preuve cible ; la majorité des recettes métier reste partielle ou différée

## 1. Convention

Les colonnes « commande/événement » décrivent l'effet transactionnel attendu ; un nom entre accents graves existe dans V8, une formulation en français est une cible. `Post-A` signifie que l'ordre sera décidé au Gate A. `Golden` désigne un scénario exécutable avec preuves, pas un test unitaire qui recopie l'implémentation.

## 2. Recettes métier REC-01 à REC-28

| Réf. | Exigence observable | Objet owner | Contexte | Module V8 | Commande/événement | Tranche/PR | Test/preuve | Statut |
|---|---|---|---|---|---|---|---|---|
| REC-01 | inventaire archives et fichier illisible nommé | Document/Version | DCE | dce | admettre/extract terminal | A1 puis Post-A | Golden archive imbriquée, inventaire 100 % | PARTIEL |
| REC-02 | pièce annoncée absente, source et question | Requirement/Unknown | Evidence | dce | matérialiser inconnu | A4/Post-A | Golden RC vs inventaire | PARTIEL |
| REC-03 | rectificatif rouvre exigences/prix/risques/livrables | Version + dépendances | DCE/Evidence | dce/decision/pricing/preparation | `DceVersionSuperseded` + invalidate | A4/Post-A | Golden rectificatif, zéro stale C1 | PARTIEL |
| REC-04 | délais contradictoires restent visibles | Contradiction | Evidence | dce partiel | enregistrer contradiction | Post-A | Golden deux clauses | PARTIEL |
| REC-05 | obligation CCTP avec page/lot/phase/criticité | Requirement/Evidence | Evidence | dce | matérialiser + confirmer | A2–A4/Post-A | Golden CCTP C1, source en un clic | PARTIEL |
| REC-06 | portée limitée PSE/site | Requirement scope | Evidence | dce partiel | confirmer applicabilité | A4/Post-A | Golden multi-site/PSE | PARTIEL |
| REC-07 | attestation expirée/activité mal couverte | Enterprise item | Enterprise | enterprise | valider/expirer capacité | Post-A | Golden candidature | PARTIEL |
| REC-08 | capacité tierce reliée aux engagements/signatures | Partner proof | Enterprise | enterprise partiel | valider preuve tierce | Post-A | Golden groupement | PARTIEL |
| REC-09 | totaux divergents localisés | Price contradiction | Pricing | pricing | importer/comparer/valider | Post-A | Golden DPGF/BPU/DQE | PARTIEL |
| REC-10 | MIRP P1 absent bloque prix prêt | InformationRequirement | Evidence/Pricing | absent | déclarer/résoudre MIRP | Post-A | Golden lot par métier | ABSENT |
| REC-11 | limites amiante visibles dans prix | Evidence + CostFactor | Evidence/Pricing | dce/pricing partiel | lier limite/provision | Post-A | Golden diagnostic limité | ABSENT |
| REC-12 | plan lourd non interprété impose inspection | Extraction/Unknown | DCE/Evidence | dce | extraction `REVIEW_REQUIRED` | A1/Post-A | Golden PDF graphique | PARTIEL |
| REC-13 | fournisseur comparé avec exclusions/validité/délai | Partner quote | Enterprise/Pricing | partiel | enregistrer/comparer devis | Post-A | Golden trois offres | ABSENT |
| REC-14 | protection paiement sous-traitant vérifiée | Partner proof/Risk | Enterprise/Decision | decision/enterprise partiel | créer blocage/escalade | Post-A | validation juriste + Golden privé | ABSENT |
| REC-15 | conflit de ressource daté et scénarios | Capacity assignment | Collaboration | optimization/membership | calculer puis arbitrer | Post-A | Golden portefeuille | PARTIEL |
| REC-16 | pic de trésorerie daté et explicable | Cashflow scenario | Pricing | pricing partiel | publier snapshot | Post-A | Golden recalcul cashflow | ABSENT |
| REC-17 | négociation crée une nouvelle version autorisée | Offer candidate/Decision | Response/Decision | preparation/decision | figer/superséder candidate | Post-A | Golden concession | PARTIEL |
| REC-18 | NF P 03-001 citée/version/droits | Evidence/License | Evidence | absent | référencer contenu licite | Post-A | Golden privé + matrice licence | ABSENT |
| REC-19 | ordre contractuel non établi reste ouvert | Contradiction/Question | Evidence | dce partiel | enregistrer contradiction | Post-A | Golden devis/commande/CGV | PARTIEL |
| REC-20 | retenue 7 % signalée, applicabilité juriste | RiskSignal | Evidence/Decision | decision partiel | signaler/escalader | Post-A | Golden privé validé juriste | PARTIEL |
| REC-21 | promesse reliée charge/responsable/prix | Engagement | Response | preparation/pricing partiel | accepter engagement | Post-A | Golden mémoire↔prix | ABSENT |
| REC-22 | modèle Excel protégé préservé, échec visible | Response document | Response | preparation/pricing import | importer/exporter sans altérer | Post-A | hash/formules/feuilles Golden | ABSENT |
| REC-23 | nouveau dépôt = paquet complet/version/hash/reçu | Manifest/Receipt | Submission | submission | autoriser/envoyer/rapprocher | Post-A | Golden re-dépôt | PARTIEL |
| REC-24 | échantillon physique suivi jusqu'au récépissé | Deliverable/Receipt | Response/Submission | absent | remettre objet/enregistrer reçu | Post-A | Golden non numérique | ABSENT |
| REC-25 | contrat final comparé et passé au chantier | SoldContract/Handover | Handover | absent | accepter contrat/passation | Post-A | Golden mise au point | ABSENT |
| REC-26 | perte : faits séparés des suppositions | REX Evidence/Hypothesis | Handover | opportunity/enterprise partiel | valider REX | Post-A | Golden notification rejet | ABSENT |
| REC-27 | rendement réel contextualisé avant réemploi | REX item | Handover/Enterprise | enterprise partiel | capitaliser après validation | Post-A | Golden prévu/réalisé | ABSENT |
| REC-28 | preuve insuffisante => non établi + escalade | Unknown/AI output | Evidence/AI | états fail-safe, pas runtime IA | s'abstenir/escalader | A1 puis AI | Golden hostile | PARTIEL |

## 3. Recettes UX-01 à UX-28

| Réf. | Exigence observable | Objet owner | Contexte | Module V8 | Commande/événement | Tranche/PR | Test/preuve | Statut |
|---|---|---|---|---|---|---|---|---|
| UX-01 | avis BOAMP expliqué, source, conversion sans ressaisie | Opportunity | Opportunity | opportunity | qualifier/`CreateCase` | Post-A | prototype + source live | PARTIEL |
| UX-02 | écart avec motif sans perdre la source | Opportunity feedback | Opportunity | opportunity | écarter avec motif | Post-A | test Patron | PARTIEL |
| UX-03 | reprise après interruption avec nouveaux rectificatifs | Work state | Collaboration | membership/dce | reprendre tâche/projeter changements | Post-A | test reprise J+1 | PARTIEL |
| UX-04 | motif financier masqué au collaborateur | Decision + Financial snapshot | Decision/Pricing | decision/pricing/security | décider NO-GO | Post-A | test croisé Patron/collaborateur | PARTIEL |
| UX-05 | nouveau BPU liste revalidations et bloque P5 | Invalidation/Gate | Evidence/Decision | dce/decision | supersede/invalidate | A4/Post-A | Golden rectificatif | PARTIEL |
| UX-06 | J-2 priorise C1/prix et déclare non-vérifié | Criticality/Unknown | Evidence/Case | partiel | activer mode urgence | Post-A | test scénario J-2 | ABSENT |
| UX-07 | exigence ouvre la source sans perte de place | SourceAnchor | Evidence/UI | offsets dce | ouvrir anchor | A2 + UX | test un clic PDF/DOCX/XLSX | ABSENT |
| UX-08 | manifeste respecte fichiers séparés | Manifest | Submission | submission partiel | figer manifeste | Post-A | Golden non-ZIP | PARTIEL |
| UX-09 | conflit d'édition garde deux versions | Object versions/conflict | Collaboration | préparation partielle | détecter/résoudre conflit | Post-A | test concurrence | PARTIEL |
| UX-10 | remplaçant reprend sans secrets non délégués | Delegation/Assignment | Identity/Collaboration | membership/security | remplacer/déléguer | Post-A | test droits J-4 | PARTIEL |
| UX-11 | session expirée conserve ou annonce perte brouillon | Draft/Session | Response/Identity | preparation/security | reprendre session | Post-A | test expiration | PARTIEL |
| UX-12 | 37/40 résultats utilisables, 3 échecs isolés | Job/File status | DCE/Platform | dce/workers | terminer partiellement | A0/A1/Post-A | Golden 40 fichiers | PARTIEL |
| UX-13 | BOAMP/TED rapprochés avec provenance | Notice identity | Opportunity | BOAMP seul | rapprocher sources | Post-A | Golden multi-source | ABSENT |
| UX-14 | source indisponible affiche dernière fraîcheur | Source status | Opportunity | opportunity partiel | enregistrer scan échoué | Post-A | test panne BOAMP | PARTIEL |
| UX-15 | invitation privée crée Affaire sans cadre public imposé | Case framework | Case | case partiel | créer affaire privée | Post-A | Golden privé | PARTIEL |
| UX-16 | commande vs devis contradictoires avant acceptation | Contradiction | Evidence | dce partiel | enregistrer/résoudre | Post-A | Golden privé | PARTIEL |
| UX-17 | sous-traitant insuffisant non confirmé et action assignée | Partner proof/task | Enterprise/Collaboration | enterprise/membership | bloquer/assigner | Post-A | Golden sous-traitant | PARTIEL |
| UX-18 | courriel envoyé sans accusé ≠ réception prouvée | Submission attempt | Submission | submission SMTP | enregistrer tentative | Post-A | test SMTP sans DSN | PARTIEL |
| UX-19 | prompt injection DCE non exécutée et signalée | Security finding | DCE/AI | pas de LLM | scanner/policy deny | A1 + AI | Golden Hostile | ABSENT |
| UX-20 | correction fait choisir portée et montre impacts | Enterprise version | Enterprise | enterprise partiel | corriger/versionner | Post-A | test propagation | PARTIEL |
| UX-21 | panne IA laisse sources/tâches/validations/coffre | Core services | domaines/Platform | pas de dépendance LLM | désactiver provider | AI | test provider down | COUVERT PAR ABSENCE DE PROVIDER, À REVALIDER |
| UX-22 | export puis fermeture : périmètre/calendrier/preuve | Export/Deletion job | Platform | absent | exporter/offboard | avant pilote | exercice offboarding | ABSENT |
| UX-23 | partage révoqué, historique et limite copie | Share grant | Identity | absent | accorder/révoquer | avant partage | test lien externe | ABSENT |
| UX-24 | échéance affiche heure source et locale | Deadline | Case | partiel | enregistrer timezone | Post-A | test changement fuseau/DST | PARTIEL |
| UX-25 | blocage C1 traitable au clavier | Requirement/Task UI | Evidence/Collaboration | web partiel | confirmer/retour liste | UX Gate | test clavier manuel | BLOQUÉ, prototype absent |
| UX-26 | lecteur d'écran reçoit fin d'analyse sans focus déplacé | Job status UI | Platform/UI | web partiel | job completed notification | UX Gate | test lecteur d'écran | BLOQUÉ, non exécuté |
| UX-27 | visite hors réseau puis synchronisation explicite | Field observation | Collaboration | absent | enregistrer local/synchroniser | Post-A | test offline/conflict | ABSENT |
| UX-28 | nouveau modèle/règle ne réécrit pas décisions historiques | Decision snapshot/AI version | Decision/AI | decision snapshot présent | publier version/review | AI Change | Golden avant/après | PARTIEL |

## 4. Validations externes VAL-01 à VAL-12

| Réf. | Sortie attendue | Objet owner | Contexte | Module V8 | Commande/événement | Échéance/tranche | Preuve | Statut |
|---|---|---|---|---|---|---|---|---|
| VAL-01 | règles commande publique datées | RuleSet | Evidence | absent | publier rule version | avant service + veille | juriste + registre | BLOQUÉ EXTERNE |
| VAL-02 | matrice marchés privés + 15 DCE | RuleSet/Golden | Evidence/Quality | absent | publier validation | avant promesse privé | juriste construction | BLOQUÉ EXTERNE |
| VAL-03 | MIRP par corps d'état | InformationRequirement catalog | Evidence/Pricing | absent | valider catalogue | avant contrôle prix garanti | experts métiers | BLOQUÉ EXTERNE |
| VAL-04 | modèle marge-trésorerie | Pricing model | Pricing | pricing partiel | versionner modèle | avant GO financier | DAF + affaires réelles | BLOQUÉ EXTERNE |
| VAL-05 | règles assurance/qualification/diagnostic | RuleSet | Enterprise/Evidence | partiel | publier orientation | avant blocages auto | assureur/QSE | BLOQUÉ EXTERNE |
| VAL-06 | protocole preuve de remise par canal | Submission protocol | Submission | partiel | valider canal | avant automatisation | essais plateformes | BLOQUÉ EXTERNE |
| VAL-07 | taux lecture formats anciens/protégés/plans | Parser benchmark | DCE/Quality | partiel | exécuter banc | avant annonce formats | Golden réel | BLOQUÉ A1 |
| VAL-08 | rappel/précision/désaccord/abstention IA | AI benchmark | AI/Quality | harness vide | exécuter banc gelé | avant engagement qualité | deux experts | BLOQUÉ A1/EXTERNE |
| VAL-09 | fiches concurrentes vérifiées | Market benchmark | Product | rapport documentaire | valider essais | avant positionnement final | essais/contrats | PARTIEL |
| VAL-10 | matrice licences permises | License grant | Enterprise/Evidence | absent | valider droit | avant contenu payant | éditeurs/conseil PI | BLOQUÉ EXTERNE |
| VAL-11 | politique RGPD/fournisseurs/risques | Data processing register | Platform | partiel | approuver traitement | avant données réelles | DPO/RSSI/DPA | BLOQUÉ EXTERNE |
| VAL-12 | bilan valeur PME/passation | Product outcome | Handover/Product | absent | clôturer pilote | pilotes/trimestriel | avant/après validé | DIFFÉRÉ PILOTE |

## 5. ADR préliminaires

| Réf. | Exigence observable | Objet owner | Contexte | Module V8 | Commande/événement | Tranche | Test/preuve | Statut |
|---|---|---|---|---|---|---|---|---|
| ADR-DEP-001 | Data Plane dédié par client | Deployment | Platform | compose preprod | provisionner instance | avant pilote | deux instances isolées | PARTIEL |
| ADR-STD-001 | un code produit, versions identifiables | Release | Platform | Git/images | déployer release | A0/pilote | même digest/config distincte | PARTIEL |
| ADR-OPS-001 | provisioning/exploitation industrialisés | Instance | Platform | scripts/compose | créer/mettre à jour | avant 2e instance | exercice reproductible | PARTIEL |
| ADR-CP-001 | Control Plane sans données métier client | Control metadata | Platform | absent | enregistrer état parc | plusieurs instances | test interdit données | DIFFÉRÉ |
| ADR-AI-001 | coûts IA séparés et mesurés par client | AI usage | AI/Platform | absent | enregistrer usage | avant IA réelle | facture↔tenant | ABSENT |
| ADR-FIN-001 | coût de revient/marge SaaS client | Service cost | Control/Finance | absent | consolider coût | avant offre commerciale | bilan client | DIFFÉRÉ |
| ADR-SEC-001 | défense en profondeur malgré instance dédiée | Security controls | Identity/Platform | contrôles présents | autoriser/refuser | avant pilote | pentest/gates | PARTIEL |
| ADR-DATA-001 | résidence France/EEE et support Maroc borné | Data flow/access grant | Platform/Identity | absent comme registre | accorder support JIT | avant pilote | DATA-FLOW + logs | ABSENT |
| ADR-CONTRACT-001 | DPA/SCC/sous-traitants | Contract register | Governance | absent | approuver provider | contrat pilote | documents signés | ABSENT |
| ADR-OFF-001 | export et destruction environnement | Off Job | Platform | absent | offboard instance | avant pilote | exercice + preuve | ABSENT |
| ADR-SALES-001 | promesses commerciales limitées aux preuves | Claim catalog | Governance | documentaire | approuver claim | avant commercialisation | revue claim↔preuve | PARTIEL |
| ADR-EVOL-001 | multi-tenant seulement si besoin démontré | Deployment decision | Platform | tenant-aware/dédié | décider évolution | besoin économique | ADR nouvelle | COUVERT COMME CONTRAINTE |

## 6. Critères d'acceptation métier du chapitre 26

| Réf. | Exigence observable | Owner/contexte | Tranche | Preuve cible | Statut |
|---|---|---|---|---|---|
| ACC-01 Complétude | 100 % fichiers et entrées inventoriés | DCE | A1/Post-A | Golden par archive | PARTIEL |
| ACC-02 Traçabilité | 100 % C1/chiffres/engagements ouvrent source | Evidence | A2–A4/Post-A | couverture anchors | ABSENT |
| ACC-03 Portée | lot/site/phase/option corrigibles sans altérer texte | Evidence | A4/Post-A | revue expert | PARTIEL |
| ACC-04 Rectificatif | liste complète des objets potentiellement touchés | DCE/Evidence | A4/Post-A | Golden diff | PARTIEL |
| ACC-05 Contradiction | aucune valeur choisie silencieusement | Evidence | Post-A | Golden contradictions | PARTIEL |
| ACC-06 Candidature | preuve/action/blocage nominatif par obligation | Enterprise/Response | Post-A | Golden candidature | PARTIEL |
| ACC-07 Couverture prix | prestation reliée ligne/inclusion/question/risque | Pricing | Post-A | Golden lot | ABSENT |
| ACC-08 Trésorerie | pic/date/hypothèses recalculables | Pricing | Post-A | scénario cashflow | ABSENT |
| ACC-09 Capacité | double promesse alerte explicable | Collaboration | Post-A | scénario portefeuille | PARTIEL |
| ACC-10 Partenaires | exclusions/validité/délai conservés | Enterprise/Pricing | Post-A | comparatif Golden | ABSENT |
| ACC-11 Engagements | promesse mesurable assignée et passée au chantier | Response/Handover | Post-A | Golden offre/passation | ABSENT |
| ACC-12 Offre finale | paquet bit-à-bit rapproché du reçu | Submission | Post-A | hashes + reçu | PARTIEL |
| ACC-13 IA | preuve insuffisante => non établi | AI/Evidence | A1/AI | Hostile benchmark | PARTIEL |
| ACC-14 Passation | prix/hypothèses/risques/engagements accessibles | Handover | Post-A | test conducteur | ABSENT |
| ACC-15 REX | écart contextualisé/validé/confiance | Handover/Enterprise | Post-A | pilote clôturé | ABSENT |

## 7. Invariants CCF §62.3

| Réf. | Invariant | Owner/contexte | Tranche | Preuve | Statut |
|---|---|---|---|---|---|
| INV-01 | toute donnée dérivée revient à sa provenance | Evidence | A2–A4 | FK + Golden | PARTIEL |
| INV-02 | toute autorisation revient à personne et version | Decision | Post-A | audit immuable | PARTIEL |
| INV-03 | droits identiques dans recherche/export/IA | Identity | avant pilote/AI | tests croisés | PARTIEL |
| INV-04 | modification critique invalide dépendances | Evidence/Decision | A4/Post-A | Golden rectificatif | PARTIEL |
| INV-05 | fonction IA critique a une voie non conversationnelle | domaines/UI | AI | provider-off tests | COUVERT ACTUEL, À REVALIDER |
| INV-06 | traitement long expose état/partiel/reprise | Platform | A0/Post-A | crash/retry Golden | PARTIEL |
| INV-07 | opération externe sépare préparation/tentative/envoi/réception/acceptation | Submission | Post-A | tests par canal | PARTIEL |
| INV-08 | Affaire exportable avec dossier d'audit | Case/Platform | avant pilote | export vérifié | ABSENT |

## 8. Couverture et décision

Cette matrice ne transforme pas les `PARTIEL` en promesse. Elle garantit que chaque exigence a désormais un endroit où être traitée et une preuve attendue. Les exigences C1 liées à l'inventaire, aux sources et aux rectificatifs forment le premier sous-ensemble A1–A4. Les fonctions prix, candidature, remise et passation restent des incréments verticaux après Gate A.

**Question Gate 0 n° 3 — chaque exigence critique a-t-elle un test/preuve et une tranche ? `OUI DANS LA MATRICE`, `NON DANS LE PRODUIT ACTUEL`.** La trajectoire est complète, mais les preuves Golden, externes et pilote manquent. Cela justifie A0/A1 avant A2–A4.

## 9. Sources

- `rapports/SMART_AO_Cahier_des_charges_Metier_v1.0.md` §§26–30
- `rapports/SMART_AO_CCF_UX_Product_Blueprint_v1.1.md` §§32, 60–64
- `rapports/SMART_AO_Registre_Decisions_Architecture_Preliminaires_v0.1.md`
- `rapports/SMART_AO_Architecture_Logicielle_v3.1_REFERENCE_DIRECTRICE_PHASE0.md`
- [QUAL-01](./SMART_AO_PHASE0_QUAL-01_GOLDEN_DCE.md)
- [PLAN-A](./SMART_AO_PHASE0_PLAN-A_PR-A0_A4.md)
