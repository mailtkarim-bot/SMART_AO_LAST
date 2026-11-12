# L08 — cadre acheteur DOCX sourcé

**Qualification locale bornée du 27/10/2026.** Cadre synthétique à régions dédiées; L08 général PARTIAL. Le plan global garde seul le statut opérationnel et la prochaine étape.

## AS-IS

Le C10 actuel assemble un Markdown unique, sélectionné et revu sur son triplet exact. Le stockage des brouillons, leur revue, leur publication et l’export présument UTF-8/Markdown. Les bibliothèques python-docx/lxml sont déjà installées. OnlyOffice DesktopEditors est présent localement avec son convertisseur x2t; aucune installation nouvelle prévue. Graphify consulté avant exploration, Serena activée.

## Risques et conception retenue

Le DOCX rempli est un brouillon natif distinct, lié au Markdown source exact et au cadre DCE exact, puis revu séparément sur ses octets binaires. Pas de conversion d’une revue Markdown en revue DOCX. Format explicite MARKDOWN/DOCX sur brouillon/document publié, défaut MARKDOWN pour l’historique; provenance JSON append-only sur le brouillon DOCX. Aucun nouveau moteur, framework ou porte.

Remplissage des régions dédiées du cadre synthétique : paragraphes et cellules rectangulaires simples, locator structurel et hash XML avant modification. Ne modifier que word/document.xml; garder les autres parties, styles et contenu statique. Ancre changée/ambiguë, fusion/nesting ou contenu actif : refus REVIEW_REQUIRED. Champ dédié sans contribution : UNKNOWN explicite. Provenance source/template/DCE/version/hash, couple exigence/section et offsets du texte source conservés; aucune normalisation de négation/condition.

## Points d’insertion et plan

- [x] Adapter OOXML sûr et preuves de préservation/ancres/refus/UNKNOWN, puis DOCX rendu localement et inspection visuelle.
- [x] Métadonnées format/provenance et migration additive avec contraintes, upgrade, downgrade sans perte et tête unique.
- [x] Acte de remplissage depuis contribution source exacte et cadre DCE possédé; idempotence/OCC/tenant/rôle, revue et invalidation natives.
- [x] Projection/aperçu/téléchargement exacts, sélection DOCX et revue Patron dans les parcours existants; OpenDesign Local/Impeccable avant UI.
- [x] Manifeste/snapshot/P5/ZIP binaires exacts avec compatibilité Markdown; tests natifs et contre-exemples, revue/scans, nettoyage, plan et miroir Basic Memory.

Local synthétique uniquement; aucun corpus réel, live, VPS, déploiement, push, effet P3 réel ou dépôt externe. UNKNOWN, FINANCIAL_PRIVATE, PERSONAL_DATA, MFA, tenant/assignment, append-only et portes préservés. A1 non admis, A2 HOLD, candidats inactifs et NO-GO public. Le plan global garde seul le statut et la prochaine étape.

## Journal de qualification en cours — 27/10/2026

Brouillon DOCX natif distinct du Markdown : création/retry, revue exacte séparée, snapshot, P5 synthétique et ZIP contenant les mêmes octets prouvés sur PostgreSQL jetable. Le développement temporaire ne modifie pas le gold. Six refus de référence/empreinte/région/contribution ne consomment pas la révision; cadre ou source altéré après revue bloque le snapshot. Source des manques et offsets UTF-8 conservés par région, région non remplie UNKNOWN.

123 tests backend ciblés API/architecture/adaptateur réussis; 54 tests wizard réussis. Contre-exemple en-tête Word actif rouge puis corrigé (toutes les parties Word XML contrôlées); correction texte d’un DOCX explicitement refusée après rouge (11 tests adaptateur/correction réussis). TypeScript vert après correction du raccord App et des types de mapping. XML du DOCX réellement extrait du ZIP validé, 8 paragraphes conservés. Rendu OnlyOffice installé, hors réseau, une page; inspection visuelle et recette Chromium natives en cours. Ce journal ne vaut pas clôture : globale backend/Web, revue complète, scans, limites aval et nettoyage restent à vérifier.

Preuves privées : `/home/noor/.local/share/smartao-proofs/l08-docx-20261027/`. Checkout principal, branche `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`; WIP préexistant préservé, aucun commit/push. Deux bases jetables `smartao_docx_dev` (tests) et `smartao_docx_browser` (recette séparée), conteneur dédié `smartao-l04-acts-pg-20261020`/socket privé, à nettoyer après campagne.

## Contre-exemples corrigés et frontière vérifiée

- En-tête Word actif hors corps : refus étendu aux parties Word XML. En-tête portant des termes financiers : inclus dans la projection textuelle de sécurité, refus FINANCIAL_DATA_FORBIDDEN après rouge; aucune affirmation d’exhaustivité d’un filtre lexical.
- Correction texte d’un DOCX : refus BUYER_DOCX_REFILL_REQUIRED, invitation à corriger les contributions puis remplir/revoir une nouvelle pièce; aucune conversion binaire→Markdown.
- PostgreSQL JSONB réordonne les clés : quatre rouges UI reproduits; comparaison structurelle des valeurs au readback, sans relâcher l’égalité des champs/IDs/hash. Network/409 non terminal/408/429 restent UNKNOWN; un reçu permet seulement le GET exact, sans second POST.
- Consommateur P7 : un rouge a montré le MIME Markdown sur les octets DOCX exacts. Format relu depuis document/manifeste, MIME/extension transmis jusqu’au téléchargement Conducteur; même Affaire synthétique poursuivie jusqu’au REX, sans effet juridique ou réception externe déduits.

137 tests backend ciblés (API ancienne/nouvelle, correction/revue, migration, chaîne DOCX et consommateur P7, architecture) réussis,1 avertissement/109,94s;12 tests adaptateur/correction avec fixtures typées réussis ensuite. Web704 réussites/4 ignorés/88 fichiers/262,67s. Types applicatifs backend696fichiers sans diagnostic; mypy app+tests conserve206diagnostics/40fichiers historiques, cinq diagnostics de la tranche corrigés. TypeScript vert; lint un avertissement App historique, build chunk878,64kB. Semgrep1.182.1,99règles/29fichiers,0finding/0erreur; detect-secrets1.5.0,0finding; Impeccable ciblé0finding. À ce stade du journal, la globale backend était encore en cours; résultat consolidé ci-dessous.

Recette Chrome DevTools MCP/Chromium isolé (aucun Playwright MCP) sur composants réels, ASGI en processus et PostgreSQL jetable séparé : choix du MD exact, inspection des régions source/hash, mapping paragraphe/cellule, UNKNOWN, confirmation explicite, perte de réponse après commit, changement de session et masque, retry strictement identique, readback reçu puis GET seul, download binaire avec SHA recalculé, revue Patron du triplet exact, choix du DOCX puis snapshot/transmission natifs. Compteurs DB : un DOCX, deux révisions de revue, un snapshot, une transmission. Cookies et Authorization absents des requêtes navigateur (acteurs fictifs résolus seulement par l’adaptateur local). Téléchargement intercepté en mémoire pour contrôler bytes/hash/extension sans écrire dans Downloads. Mise en page Patron contrôlée à390px sans débordement; bouton de revue aligné à sa hauteur utile. Les captures ne remplacent pas les assertions/API/compteurs.

**Limites :** cadre synthétique à marqueurs dédiés `[[REPONSE:...]]`, paragraphes/cellules simples uniquement; aucune prise en charge générale des cadres acheteur arbitraires, PDF, signatures, tableaux fusionnés/imbriqués ou documents actifs. Le DOCX rempli ne prouve ni pertinence exhaustive ni couverture du pli complet. Les champs sans contribution restent UNKNOWN; manques déclarés des contributions conservés dans la provenance. Pas de source admise automatiquement, pas de preuve transférée depuis un corpus réel. L08 général reste PARTIAL.

Recette navigateur close :18assertions consolidées dans `browser-qualified-checks.json`, mapping de deux régions, troisième UNKNOWN, deux POST strictement identiques pour un seul DOCX. Le SHA revu en Patron concorde avec le manifeste et le document DOCX publié. Formulaire et lecture Patron à390px sans débordement; aperçu textuel distinct du fichier binaire. L’adaptateur ASGI et Chromium ont été fermés; la base navigateur est revenue àAlembic0. La globale backend utilise l’autre base dédiée. Dépendances réutilisées : python-docx1.2.0/lxml6.1.1 du verrou, aucune installation nouvelle; `uv lock --check --offline` résout les195paquets sans changement. Rendu final du DOCX réellement conservé et empreintes template/DOCX/PDF/provenance dans `artifact-sha256.json`.

## Reprise de la globale après une attente de migration périmée

`backend-global-qualified.log` :2535réussites puis un échec sur `test_case_closure_workflow::test_nonempty_downgrade_is_refused_and_legacy_cycle_survives_roundtrip`,973,18s. Le rollback refusé conserve toute la transaction à0146; le test attendait encore0145. Correction de la fixture : lire la tête avant l’essai et prouver qu’elle est inchangée après refus. Test ciblé vert1/9,32s; aucune modification applicative ou de migration requise. Pour couvrir tous les4027nœuds sans rejouer les2535déjàverts sur le même code gelé, continuation avec le test corrigé puis les1491suivants : `backend-continuation-final.log`. Partition exacte et liste des nœuds dans `backend-suite-partition.json` / `backend-tail-nodeids.json`; pas de clôture tant que cette continuation n’a pas terminé. Un total consolidé ne sera pas présenté comme une exécution monolithique verte.

## Revue finale ciblée du code

Codex a relu l’adaptateur OOXML, l’extraction des contributions et la reconstruction de provenance, le handler transactionnel, les raccords de revue/publication/Submission/export, le format consommé en passation, les intentions UI et les contrôles de téléchargement/readback. Comparaison à la sauvegarde WIP précédente pour dix fichiers partagés (873lignes de diff dans la preuve privée), sans reconstruire depuis HEAD ni supprimer le WIP préexistant. La contre-lecture indépendante n’a produit qu’un constat d’en-tête actif avant interruption; constat corrigé et testé. Elle ne vaut pas revue indépendante complète.

Contrôles : bornes ZIP/XML et relations externes, ancre avant remplissage, conservation des parties statiques, source MD/plan/revue/template exacts reconstruits avant acte, contexte tenant/package existant, séparation Collaborateur/Patron, OCC de package et reçu idempotent, SHA binaire et format explicite, état UNKNOWN sur lecture discordante, branches Markdown historiques. Aucun nouveau port, framework, dépendance, exception ARCH-001 ou permission ajouté. `buyer_docx_handler.py` suit la règle de placement ORM; pas de refonte des autres bounded contexts.

Les scans ciblés ne prouvent pas une sécurité exhaustive, et le filtre lexical de confidentialité n’est pas un classifieur général de données personnelles ou économiques. Les règles de sources, droits et gates natives restent les autorités. Aucune revue IA ne remplace un acte humain réel; les actes de recette utilisent des acteurs fictifs.

## Livrable métier et code

| Exigence active | Code | Résultat et frontière de preuve |
|---|---|---|
| PF31-03/07/09, M31-02 : réponse acheteur dans une pièce native | `preparation/application/buyer_docx_handler.py`, `infrastructure/buyer_docx.py` | Cadre synthétique rempli depuis les seules contributions sélectionnées, contenu statique conservé; pas de cadre arbitraire présumé compatible. |
| M2-026 axe11 : sources et manques visibles | `buyer_docx_sources.py`, `response_artifact.py`, `BuyerDocxForm.tsx` | Ancre de paragraphe/cellule, hash de région avant remplissage, source/plan/version/lot existants, offsets et manques conservés; sans contribution UNKNOWN. |
| CT31-36–42 : revue et paquet exacts | `review.py`, `transmission.py`, `submission_source_reader.py`, `submission/application/service.py` | Revue du DOCX distincte du MD; sélection figée, revalidation et mêmes octets au ZIP sous P5 natif synthétique. |
| Continuité L08→L09 | `patron_action/application/case_handover.py`, route téléchargement, `CaseHandoverPanel.tsx` | Document Conducteur exact, MIME/extension DOCX; aucune réception externe ni conséquence juridique déduite. |

La lecture des sources existantes conserve leur portée enregistrée; aucun lot, délai, prix, droit, couverture ou signature n’est inféré de la présence d’un texte dans le DOCX. Les points métier et confirmations restent dans leurs registres natifs.

## Résultat final et nettoyage

Tous les4027nœuds de la suite backend ont réussi :2535dans le premier segment sur code applicatif gelé, puis1492dans la continuation corrigée (1525,04s,exit0). Le premier segment s’était arrêté sur l’attente historique de tête0145 : cette attente a été corrigée et requalifiée, aucune logique de production modifiée entre segments. Ce résultat consolidé en deux segments n’est pas un run monolithique vert. Les deux avertissements de la continuation sont la dépréciation Starlette/httpx et un alias Pydantic `export_id` sans effet dans un type de test; pas de succès implicite déduit de ces avertissements. Partition exacte sauvegardée avec les logs et la liste des nœuds.

Web704réussites/4ignorés/88fichiers/262,67s,137ciblés backend et12unitaires typés. Ruff/format26Python verts,TypeScript/build verts,lint unwarning App historique etchunk878,64kB. Mypyapplication696fichiers sans diagnostic;mypyapplication+tests206diagnostics/40fichiers, comparaison àbaseline :0nouvelle identité de diagnostic. Pas de CI totalement verte annoncée. Semgrep99règles/29fichiers,0finding/0erreur;detect-secrets0;Impeccable ciblé0. Aucun scan n’est une preuve exhaustive de sécurité.

Après la campagne, les deux bases `smartao_docx_dev` et `smartao_docx_browser` ont0table métier/0révision Alembic. Le conteneur dédié est arrêté; ACLUID70retirée et socket700. Vite5199,Chromiumisolé,transportMCP etadaptateurASGI clos. Source logicielle suivie :42fichiers, pas de changement applicatif pendant les segments. Sauvegarde finale WIP ciblée etmanifestes SHA privés dans le dossier de preuves; aucune opération Git destructive,stage,commit oupush. A1 non admis,A2 HOLD,DPGF non évaluable parRAG,moteurs candidats inactifs etNO-GOpublic maintenus.
