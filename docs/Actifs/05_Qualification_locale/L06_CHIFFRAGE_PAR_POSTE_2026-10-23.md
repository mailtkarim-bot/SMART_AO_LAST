# L06 — chiffrage sourcé par poste — 23 octobre 2026

## Contrat de livraison et plan

**But :** depuis un import financier d’une Affaire, le Patron rattache humainement un poste aux obligations DCE confirmées, aux coûts natifs déjà enregistrés et à une offre partenaire. Il relit les sources/révisions, montants déclarés, unités/devise, exclusions/transport/validité et les postes non chiffrés. Aucun montant d’offre global ni prix de vente importé ne devient un coût par défaut. Couverture économique/applicabilité restent UNKNOWN; aucune porte modifiée.

Autorités : PF31-06/08, M2-026 axes6/9, M2-027, M31-03; CT31-02/03/06. Le plan global reste le seul statut/prochaine étape.

**AS-IS :** imports multi-feuilles/aperçus, lignes financières immuables et offres/prix/revues de périmètre existent. Les rapprochements existants relient plusieurs reçus entre eux; ils ne portent pas le lien poste importé→obligation→coûts. Pas de nouvelle vérité financière : les montants restent lus dans leurs registres, un acte garde leurs références et un snapshot historique.

**RISQUES :** prix de vente pris pour coût, montant global d’un devis affecté arbitrairement, devis expiré/transport exclu, devise/unité confondues, coût réutilisé sur deux postes, source obsolète, fuite tenant/rôle, retry/concurrence, perte d’historique.

**INSERTION :** pricing application/infrastructure/public et route patron existante, bootstrap, panneau Prix existant. Un registre append-only d’actes révisionnés et ses références de coûts sont nécessaires pour cette relation multiple; aucune nouvelle table de montants ni moteur. Deux tables et migration0141, sans backfill, downgrade protégé. Le domaine de projection reste pur.

### Contrat des sources

- Poste : ligne/batch exacts, source feuille/cellules et empreinte opaque de contexte incluant Affaire/version/portée. Le hash brut de l’import reste privé.
- Obligation facultative : identifiant/révision de confirmation et ancre DCE actuelle exacte; absence=UNKNOWN, aucune confirmation induite.
- Coûts : zéro à20lignes financières de coût (jamais SALES), chacune avec révision du rapport exact; quantité/unité/devise lues, pas saisies une seconde fois. Mélange de devises/réutilisation d’une ligne : total non qualifié et limite visible, sans conversion ni allocation inventée.
- Offre facultative : déclaration de prix et reçu courants exacts. Montant global affiché comme tel; pas de coût de poste déduit. Revue de périmètre facultative explicitement sélectionnée pour transport, jamais choisie arbitrairement parmi plusieurs revues.
- Source/revision changée : acte précédent REVIEW_REQUIRED, pas de transfert des montants dans le courant. Historique conservé et consultable en HISTORICAL. Justification et confirmation humaines obligatoires; MFA/FINANCIAL_PRIVATE/tenant/append-only/idempotence/concurrence inchangés.
- Lecture bornée et paginée des postes; limites des listes de sources explicites. Aucune absence de coût assimilée à zéro ou à absence de risque.

### Plan minimal exécuté dans le parcours existant

- [x] Rouge API : route absente et poste non chiffré; domaine : coût absent/vente, devises/unités, exclusions/expiration/réutilisation.
- [x] Modèle/migration141, commande humaine et revalidation transactionnelle; lecture sources/current/history et branchement bootstrap.
- [x] Panneau de chiffrage : choix de sources, justification/confirmation, retry exact UNKNOWN, relecture après reçu/409, masquage et historique. OpenDesign Local/Impeccable avant JSX.
- [x] PostgreSQL/HTTP : plusieurs coûts par poste, source DCE exacte, devis et transport exclus, rectificatif/révisions, refus tenant/rôle/MFA, concurrence/retry et append-only/downgrade.
- [x] Revue indépendante, tests ciblés puis suites/qualité/scan, navigateur synthétique, nettoyage; mise à jour plan/index/fiche et miroir Basic Memory.

## Frontière et limites

Ce parcours relie des déclarations enregistrées; il ne déclare pas le chiffrage complet, l’engagement d’un partenaire ni une couverture de coût. Aucun modèle IA/activation de candidat, corpus réel, backend live, VPS, déploiement, effetP3, admission/GOpublic, commit ou push. A1 non admis/A2HOLD/NO-GOpublic; DPGF horsRAG. Les montants multi-devises ne sont pas agrégés et une unité différente ne devient pas équivalente par normalisation.


## Résultat et preuves finales

Le parcours de rattachement est codé dans le panneau Prix : tous les postes paginés du batch choisi, sources DCE confirmées/coûts/offres sélectionnés explicitement, justification puis confirmation/MFA, reçu et relecture. Source obsolète = REVIEW_REQUIRED sans reprise des montants dans le courant. L’historique rend aussi l’obligation, l’offre, les exclusions et le transport lisibles, pas uniquement le montant.

- Backend global **3854réussites,0ignoré,2warningshistoriques,1106,06s,exit0**; Web **638réussites/4ignorés**,75fichiers,45,84s.217ciblés backend dont24domaine/SQL/API,7UI, ensembles recouvrants. Warnings Starlette/httpx et Pydantic alias conservés.
- Mypy659,types/lint/build etRuff/format verts. JSON monétaire chaîne décimale/BigInt pour les grands montants;9007199254740993 exact. Comparaison Decimal des quantités, unités strictes, aucune conversion.
- TDD :3rouges domaine et routeHTTPabsente; sources/quantités/bases et précision monétaire; revue reproduit2rouges mutexBatch et2/2.0, corrigés; architecture2contrôlesverts après déplacement du serviceSQL en infrastructure. RougeUI de message de conflit après changementAffaire corrigé par scope de message. Pas d’ignore de gate ni suppression de test.
- Semgrep1.179.0/225règles/24fichiers0finding0erreur; scanUI final0; secrets0/Impeccable[].24hashes finaux stables, backend inchangé après gel. Pas de certification de sécurité ou WCAG complète.

### Recette navigateur native synthétique

Chrome DevTools MCP, Chromiumheadless isolé (pasPlaywrightMCPdisponible). NativeFastAPITestClient etPostgreSQLjetable, session/API/acteurs synthétiques, aucun backend live ni fichierclient.15assertions : choix/confirmation, UNKNOWN et masquage des faits courants, aucunGET avant reçu/409, refusMFA conservant le corps, retryexact, DCE/ancre/révisions etcoût enregistré15000unitésmineuresEUR distincts du priximporté50000 et offre9999,50; exclusions, transportexclu, devisexpiré etpostesnonchiffrés; nouvelle révision du rapport→stale sans transfert; historiqueDCE/coût/offre/exclusions/transport; rôle403 etmasquage immédiat. TroisPOSTnatifs201/403/200replayed, corps/identités égaux, unacte/uneréférencedecoût; registre financier inchangé par les liens (coûtsdirects17000,ventes0,rapportrev2 avant révision synthétique externe).

Desktop1440 etmobile390 : captures finales inspectées, pas de débordement racine; tableau défilant annoncé/accessible. Une première vérification ne laissait pas React appliquer le formulaire, puis une capture de chargement après restauration de rôle; diagnostics conservés, aucune nouvelle écriture aveugle. Reprise depuis intention préparée et attente de données avant capture finale. Les captures ne prouvent pas tous les cas métiers.

### Sources et limites de qualification

Origine de l’import : référence parhash exact à un document/version DCE déjà ADMITTED/VERIFIED et courant, ouUNKNOWN. Aucun document admis, reclassifié ou ajouté auRAG par ce rapprochement. La disponibilité courante du binaire en stockage n’est pas requalifiée par cette seule correspondance de métadonnées. Le hashbrut d’import reste privé. Les snapshots gardent les anciennes déclarations; ils ne deviennent pas une deuxième vérité financière.

Budget :50postes/page,1000choix parregistre (limites indiquées, recherche descoûts), jusqu’à20coûts/acte. Les chiffres d’un devis sontglobaux/declared; aucun coût de poste dérivé. Les réutilisations de lignes et plusieurs bases/devises rendent la somme nonqualifiée. Les allocationspartagées, FX/unités/prixétendus, devise originale de l’import et couverture économique globale restent ouverts; la sortie locale ne clôt pas toutL06 ni le cahier.

### Nettoyage, Git et suivi

Preuves privées `~/.local/share/smartao-proofs/l06-position-costing-20261023/`. TroisDB `smartao_positions`, `smartao_positions_global`, `smartao_positions_browser` Alembic0 vérifiées; conteneurtmpfs dédié arrêté/exited, ACLUID70 retirée/socket700; SDKChromium,adapterUDS600 etVite privés arrêtés. HEAD30f26934430095632000a1d82519f61dbb4c6411, branchecodex/reconcile-smartao-20261009, WIP principal préservé; aucun stage/commit/push.

Plan : case du parcours local cochée, journal et prochaine fonctionL07; index/fiche/CSV etBasicMemory actualisés. Les45familles/14livrables-garanties sont conservés; le plan garde seul lesstatuts. A1nonadmis/A2HOLD/NO-GOpublic, DPGFhorsRAG, candidatsinactifs; aucunVPS/déploiement/P3/corpus réel/GOpublic.

Méthode : Superpowers cadrage/plan/TDD/revue; ECC product-capability/verification-loop et contraintes de migration; Graphify consulté, Serena activée, BasicMemory miroir, Context7SQLAlchemy/RR vérifié avant l’appel et pattern existant réutilisé. OpenDesignLocal catalogue/artefact existant, systèmeincumbent conservé; Impeccablecontexte/craft-floor/detect et inspection bornée. Pas de Jev/Manus : relations et calculs déterministes, une revue indépendante bornée suffisait.
