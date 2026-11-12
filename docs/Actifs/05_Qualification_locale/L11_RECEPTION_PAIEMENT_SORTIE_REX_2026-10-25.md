# L11 — réception, réserves, paiement, sortie et REX

## AS-IS d’entrée — 25 octobre 2026

Les actes WORK_RECEPTION/RIGHTS_PRESERVATION/CONTRACT_EXIT, obligations et transitions, cycles/signaux/revues de paiement et REX/interviews/applicabilité existent. Les cycles ne portent aucun constat d’encaissement structuré. Les obligations n’ont pas de responsable ni preuve attendue structurés. Les actes voisins ne constituent pas un dossier de sortie ; le REX commercial dépend du P7, ce qui ne doit pas être remplacé par un faux P7 pour enregistrer un enseignement d’exécution.

## Risques

Ne pas fusionner réception, levée déclarée, pièce reçue, paiement attendu et encaissement enregistré. Une date libre n’est pas une échéance juridique. Une différence entre deux déclarations ne prouve ni solde, couverture ni droit acquis. Préserver confidentialité financière, tenant/ownership, MFA, append-only, provenance, invalidation et retries. Un nouvel enseignant ou une nouvelle Affaire cible ne doit pas reprendre un REX sans choix humain explicite.

## Points d’insertion et plan minimal

- [x] Étendre les actes et obligations natifs par contexte/suivi facultatif ; comparer les sources exactes dans une projection de dossier d’Affaire. Garder les anciens corps/hashes de retries.
- [x] Ajouter des faits financiers append-only aux cycles natifs : facture déclarée, paiement attendu, encaissement enregistré humainement avec montant/devise/date/source/preuve. Les liens restent explicites ; aucune somme partielle n’est promue en règlement complet.
- [x] Raccorder une sortie déclarée aux points ouverts et comparaisons prévu/réalisé sourcées. Ajouter au REX natif une origine de sortie d’exécution distincte du P7 commercial ; garder interviews figées, expiration et acte humain de réemploi sur l’Affaire cible.
- [x] Livrer le parcours existant enrichi, après OpenDesign Local/Impeccable : sélection de sources, justification/confirmation, responsables/preuves, UNKNOWN et historique, masquage de contexte et retries identiques.
- [x] Qualifier nominal/refus/concurrence/obsolescence/tenants et rôles/migrations sur PostgreSQL jetable, puis navigateur synthétique, revue, suites, scans, nettoyage et suivi/mémoire.

## Tests à prouver

Paiement attendu sans encaissement ; collection sans lien ne produit aucun solde ; devise incompatible/ref étrangère refusée ; reçu/réserve/complétion restent distincts ; source remplacée ou version fausse invalide la revue ; nouveau point ouvert avant sortie bloque une confirmation périmée. Écarts uniquement entre références exactes, UNKNOWN sans preuve. REX d’exécution sans faux P7, snapshot d’interview immuable, cible différente et choix humain, expiration/source/cible obsolètes sans réemploi automatique. Rejet rôle/tenant/MFA/finance, double clic/retry/409, réponse tardive, append-only/upgrade/downgrade vide/refus non vide/head0145.

## Autorités et limites

PF31-08/09, M31-05/07, M2-026 axe12, CT31-04/07 et réalignement métier→code. Calcul juridique/calendaire, sanctions quantitatives et settlement/DGD structurés restent différés. Local synthétique uniquement : aucun VPS/déploiement/push, corpus réel, P3, dépôt externe ou GO public. A1 non admis, A2 HOLD, DPGF hors RAG et moteurs inchangés. Le plan global reste l’unique statut opérationnel.

## Point de travail — noyau et raccord UI en cours

Code Python/API ajouté : contrats fermés, faits financiers natifs append-only, projection sourcée par Affaire, revue des actes/obligations, sortie déclarée avec reconnaissance des obligations ouvertes, origine REX d’exécution distincte du P7 et réemploi humain avec contexte cible. Tête additive locale0145; aucun commit/push. Anciennes commandes sans extension inchangées. La réception déclarée, la levée déclarée, les références de preuves et les effets externes restent distincts.

Preuves intermédiaires effectivement exécutées : contrats/application5/5; workflow PostgreSQL synthétique3/3, incluant montants attendus/constatés, retry, append-only, sortie après réserve, REX/interview et réemploi refusé après changement de portée; Web3/3, masquage de contexte et retry identique. Ces comptes ne qualifient pas encore la livraison : code ensuite enrichi, suites/revue finale/navigateur/scan encore à exécuter. Les journaux rouges sont conservés dans le dossier privé `~/.local/share/smartao-proofs/l11-closure-20261025/`.

Revue technique indépendante bornée (aucune validation métier humaine) : contrôle financier explicite PRICING_READ/WRITE ajouté; verrou Case avant writers natifs de cycles/contrats; portée lot REX contrôlée, justification conservée; garde SQL REX d’exécution et refus de perte au downgrade. Invalidation étendue à portée/fraîcheur/lifecycle/contrats, pas seulement au DCE ID. Leurs régressions finales restent à consolider. Les preuves sont des références humaines enregistrées, pas une validation de contenu juridique, bancaire ou de chantier.

## Clôture de la qualification locale — 26 octobre 2026

Le parcours réception → réserve/action/responsable/preuve → suivi humain → facture/paiement attendu/encaissement déclaré → sortie avec écarts sourcés → REX/interview figée → décision humaine sur une autre Affaire est codé dans les registres natifs et le parcours existant. Cette clôture est technique et synthétique; elle n’est ni une validation métier humaine de données réelles, ni une admission Golden DCE, ni un GO public. L11 général reste PARTIAL, les reports PF31-09 sont conservés.

### Code et contrats livrés

- `pricing/application/case_closure.py` : autorisations Patron + PRICING_READ/WRITE et FINANCIAL_PRIVATE, MFA pour les actes; lecteur injecté. `case_closure_handler.py` : écritures transactionnelles et revalidation des références exactes. `infrastructure/case_closure_reader.py` : dossier courant, snapshots/hash, liens/états et invalidation; aucune exception ARCH-001 ajoutée.
- Migration additive `20261025_0145` : faits de paiement append-only liés au cycle/tenant/Affaire exacts; contexte de revue facultatif sur actes et obligations natifs; origine REX d’exécution distincte du P7 commercial et garde SQL. Historiques antérieurs et anciens corps de commandes conservés.
- Les montants sont des entiers positifs déclarés en unités monétaires mineures avec devise/date/sources/preuves. Facture, attente et constat sont distincts. Le seul écart calculé est la différence d’une paire explicite compatible; elle ne vaut jamais solde ni règlement complet. Les références de preuve ne valent pas inspection du document, confirmation bancaire ou validité juridique.
- Réserves : responsable et preuve attendue déclarés ou UNKNOWN; une complétion déclarée reste historique. Si sa source devient obsolète, elle réintègre les points à revoir. Une sortie reconnaît explicitement les points ouverts; elle ne les efface pas et ne change aucune porte.
- Écarts généraux : deux références natives exactes (acte/obligation/fait/action), SHA serveur et snapshots, note humaine. Absence ou ambiguïté demeure UNKNOWN; aucune mesure juridique ou quantitative générale inventée.
- `patron_action/application/execution_rex_handler.py` : enseignement d’exécution sans faux P7, lot prouvé ou UNKNOWN, publication opérationnelle explicite. La justification privée reste hors de l’origine publiée dans l’interview/bibliothèque. Réemploi à décision humaine distincte, source/cible/expiration et contextes revalidés; décisions historiques conservées avec état courant dérivé.
- `interfaces/http/routes/case_closure.py` et bootstrap : lecture privée et huit opérations dans `/api/v1/patron/cases/{case_id}/closure`. Les anciennes routes restent disponibles sans changement de droits. Le vieux panneau REX dirige les enseignements d’exécution vers cette revue dédiée.
- `web/src/features/decision/CaseClosurePanel.tsx`, types/API et App : parcours intégré, sélection exacte des sources, responsable/preuve, justification/confirmation par acte, reçus stricts, relecture après reçu/409. UNKNOWN fige l’intention; un même propriétaire conserve corps et IDs après reconnexion, tandis que le contexte d’affichage change et masque immédiatement l’ancien formulaire. Un refus terminal ne libère qu’après lecture courante; une réponse incertaine ne déclenche aucun nouvel acte.

### Résultats effectivement exécutés

| Contrôle | Résultat | Portée et limites |
|---|---|---|
| Backend complet sur PostgreSQL jetable explicite | **3993 réussites, 0 échec, 0 ignoré**, 1122,01 s, exit0 | Deux avertissements : Starlette/httpx déprécié et alias Pydantic d’une autre recette. Campagne interrompue précédente non comptée comme verte. |
| Backend/API/architecture ciblés | **101/101** | Nominal, refus tenant/rôle/finance/MFA, provenance, cycle modifié, sources/cible obsolètes, retry, verrou réel, append-only, migration vide aller-retour et refus downgrade non vide, ancien cycle préservé. Régression de typage de fixture corrigée puis 5/5 application rejoués. |
| Web complet final | **678 réussites, 4 ignorés**, 84 fichiers, 131,61 s, exit0 | Quatre recettes C08 déjà conditionnelles, non qualifiées par cette tranche. Tests jsdom, pas une preuve de navigateur. |
| Navigateur natif local synthétique | **24 assertions finales + reflow à390px**, desktop1280/mobile390 inspectés | Chrome DevTools MCP, Chromium isolé; pas de Playwright MCP disponible. API FastAPI en processus via TestClient et socket privé, PostgreSQL jetable; aucune session réelle ni backend live. |
| Retry de l’encaissement après reçu perdu et reconnexion | **201 natif puis200 replay**, corps strictement identiques, un seul constat | Vérification indépendante du transcript; trois faits financiers, deux actes réception/sortie, une réserve/transition, un REX/interview/réemploi, zéro autorisation P5. |
| Ruff/format et types application | PASS; mypy app **689 fichiers** | Deux alignements d’imports et formatage sans changement métier; annotation de fixture seule ensuite. |
| Mypy app/tests | **206 diagnostics /40 fichiers**, hors L11 | Dette globale historique maintenue, aucune qualification CI complète ou couverture revendiquée. Le diagnostic nouveau de fixture L11 a été corrigé. |
| Web types/lint/build | PASS, lint sans erreur | Avertissement App préexistant de dépendance d’effet; bundle principal860,05kB (>500kB). Pas de refonte visuelle CYTD qualifiée. |
| Sécurité | Semgrep1.182.1, p/security-audit,99 règles/39 fichiers, **0 finding/0 erreur**; secrets1.5.0/39 fichiers, **0 candidat** | Métriques désactivées, analyse locale; ne prouve pas l’absence de toute vulnérabilité. Impeccable : aucun signal mécanique sur les cibles. |
| Revue indépendante | Aucun P1/P2 restant dans le périmètre final relu | Revue technique IA, pas acte Owner/métier/DPO. |

### Preuves, nettoyage et limites

Dossier privé `~/.local/share/smartao-proofs/l11-closure-20261025/` : journaux rouges/verts, campagnes finales et codes de sortie, transcripts natifs, preuve du retry exact, captures finales, scans, manifeste SHA-256 des39 fichiers source/test et état de nettoyage. Les erreurs de harnais (contexte JS après redémarrage Vite, attente asynchrone de bibliothèque, parseur de transcript) ont été diagnostiquées sans rejouer aveuglément les écritures; seuls les contrôles finals réussis sont comptés.

Les trois bases dédiées `smartao_l11_dev`, `smartao_l11_browser`, `smartao_l11_final` ont chacune zéro ligne Alembic avant arrêt. Seul le conteneur tmpfs dédié a été arrêté (exit0, réseau none, aucun port); ACL temporaire UID70 retirée, socket700. Pont/Vite/Chromium isolés fermés; services et navigateurs utilisateur inchangés. Aucun stage/commit/push, corpus réel, VPS, déploiement, P3, dépôt externe, banque réelle ou GO public.

A1 reste non admis, A2 générique HOLD, DPGF hors RAG, candidats inactifs. Calcul juridique/calendaire validé, sanctions quantitatives et settlement/DGD structurés demeurent différés. Le plan global reste l’unique statut; Basic Memory en est le miroir.
