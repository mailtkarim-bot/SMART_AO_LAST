# L07 — Chiffrage publié relu et flux datés déclarés — 05/11/2026

Le [plan global](../00_Pilotage_et_audits/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md) garde seul le statut. Ce dossier prolonge la [continuité L06](L06_REPARTITIONS_CHIFFRAGE_PUBLIE_2026-11-05.md). Qualification locale synthétique, général PARTIAL ; aucune banque, date juridique ou trésorerie certaine.

## AS-IS, risques et plan minimal

Le socle CASH natif sait sélectionner une ligne du dernier rapport PUBLISHED de l’Affaire, conserve son empreinte, refuse les doubles emplois et invalide les cumuls après changement de source. Il manquait une provenance lisible rapport/révision/état, enregistrée avec chaque nouvel acte plutôt que reconstruite au fil de la lecture.

Risques : copier une date du chiffrage comme échéance, confondre coût/affectation/flux, compter deux fois, transférer une ancienne déclaration au nouveau rapport, ou enrichir rétroactivement une histoire UNKNOWN. Insertion minimale : catalogue natif et snapshot JSON existants, types et panneau CASH ; aucun nouveau registre, endpoint, droit, calcul ou schéma. Plan appliqué : sources vérifiées puis rouges/verts de provenance, recette publiée→flux→remplacement→nouvel acte, revue, tests/contrôles et navigateur. Tests : dates/solde absents, refus consentement/doublon/source étrangère-obsolète, retry, projections/histoire exactes et distinction des sources UI.

## Fonction livrée

L’échéancier affiche le rapport publié proposé avec son ID/révision/état ; il rappelle que date de flux et solde initial restent des déclarations humaines. Une sélection native ne fabrique pas la date d’une ligne financière (`declared_date=null`). Hypothèses et justification sont saisies et confirmées dans les formes existantes.

Chaque nouveau snapshot conserve `source_details` pour les seuls éléments natifs sélectionnés depuis le catalogue autorisé ; la référence `financial_report` fournit ID/révision/état. Les empreintes existantes (`sources`) restent celles des enregistrements natifs ; les calculs du domaine sont inchangés. Une ancienne déclaration sans ces détails montre la version UNKNOWN, sans backfill à partir du rapport proposé aujourd’hui. Sources enregistrées et proposées sont distinctes dans l’écran et l’historique.

Après remplacement du rapport publié, les anciennes déclarations et leurs hypothèses restent enregistrées ; état REVIEW_REQUIRED, cumuls courants retirés. L’ancienne source est refusée ; un nouveau choix, de nouvelles valeurs/dates hypothétiques, justification et confirmation humaines permettent un nouvel acte. Le retry identique retrouve le reçu ; aucun flux ou paiement extérieur n’est exécuté.

## Recette native

`backend/tests/db/test_l07_published_cost_cash.py` utilise la même Affaire synthétique que le chiffrage publié et relu L06, via vrais services/routes et PostgreSQL jetable.

1. Rapport initial PUBLISHED révision2, coût12000 ; ses répartitions restent distinctes du montant du flux. Le catalogue financier ne fournit aucune date de paiement.
2. Déclaration de flux12000 sans date ni solde initial : cumul UNKNOWN. Une source répétée deux fois et l’absence de consentement sont refusées422. Premier acte201/retry200 ; provenance exacte enregistrée.
3. Nouvelle date15 novembre déclarée explicitement ; absence de solde initial toujours UNKNOWN.
4. Nouveau brouillon financier natif, coût16000 et publication native dans la même Affaire. Ancienne déclaration REVIEW_REQUIRED, contenu intact et cumuls retirés ; ancienne source refusée404.
5. Nouvelles source/date20 novembre/solde1000 hypothétiques et confirmation : déclaration3, cumul déclaré−15000 et historique3. Rapport initial12000 intact, version/source d’origine conservées dans son histoire.
6. Collaborateur puis Patron d’un autre tenant réel synthétique : lectures et écritures refusées sans ID de rapport ni montant retourné ; retour au Patron initial, révision3 inchangée.

Un premier renforcement employait un tenant UUID inexistant pour l’écriture : refus422 de création du reçu technique, pas le refus métier attendu. Cette campagne1 échec/96 réussites n’est pas qualifiante. Le harnais a été corrigé avec tenant/identité/adhésion réels synthétiques et MFA frais, ainsi que de nouvelles intentions de refus ; aucune règle produit n’a été assouplie.

Campagne finale : **97 réussites/78,79s**, comprenant recette, workflow CASH, domaine CASH, capacité/CASH après rectificatif et85 contraintes d’architecture. Rejeu unitaire après correction de l’acteur :1/23,08s. Avertissement Starlette/httpx existant. Ces campagnes se recouvrent ; aucune somme de tests distincts ou nouvelle globale backend annoncée.

## UI, défaut découvert et preuve navigateur

Rouge source : métadonnées financières absentes du catalogue/snapshot ; rouge UI : absence de distinction lisible entre rapport enregistré et nouveau proposé ; vert après ajout ciblé. La compatibilité legacy sans métadonnées est testée UNKNOWN. Types/montants restent natifs, aucun changement de calcul ou conversion.

La première recette navigateur prouvait les montants et le retry, mais la relecture visuelle révélait6 éditeurs dupliqués sur mobile. Cause : même `key={version}` pour les deux frères éditeur et annulation. Régression rouge sur relectures répétées, correction minimale par préfixes de clés distincts `declaration:`/`cancellation:`. Le store des intentions ne change pas ; les consentements restent retirés après nouveau contexte. Ancienne capture conservée comme preuve du défaut, pas qualification finale UI. Contre-revue initiale des sources sans blocage ; dernier correctif revu par Codex, la seconde sollicitation de l’agent étant indisponible pour quota, sans résultat de revue inventé.

**9 tests UI finaux/3,29s** couvrent provenance ancienne/nouvelle, legacy UNKNOWN, reprise/consentements et unicité des formulaires après trois relectures. Navigateur final sur nouvelle Affaire et sources gelées : Chrome DevTools MCP headless/isolé, React réel→adaptateur loopback→TestClient/API/PostgreSQL. La recette native prépare les publications ; le navigateur saisit ensuite une nouvelle hypothèse de date21 novembre, justification et confirmation. POST201 commis mais réponse masquée503 ; retry200 exactement identique, déclaration4. Cumul−15000 déclaré, source native sans date, données anciennes toujours historiques ; solde réel/financement UNKNOWN.

Desktop1280/mobile393 : largeur globale égale au viewport, un seul éditeur et une seule annulation, cookies/localStorage/sessionStorage vides et ressources loopback uniquement. La capture corrigée passe de11002 à2880px de hauteur mobile ; la première preuve monétaire n’a pas été présentée comme preuve d’absence de doublon. Authentification réelle, panne réseau/DB, redémarrage/reload UNKNOWN, clavier/WCAG exhaustifs non qualifiés.

## Fichiers et limites

- Backend : `backend/app/modules/pricing/infrastructure/cash_schedule.py` (catalogue et détails du snapshot) et nouvelle recette SQL.
- Web : `CashSchedulePanel.tsx`, `cashScheduleTypes.ts` et tests. Pas de CSS global, dépendance ou migration nouvelle ; tête0147 conservée, garde-fous append-only existants vérifiés par le workflow.
- Preuves privées : `~/.local/share/smartao-proofs/l07-published-cash-20261105/` ; baseline767 empreintes vérifiées, copies avant, gel5 sources, erreurs/tentatives et revue conservés.

La recette financière porte des coûts publiés et des positions de prix reçues ; elle ne constitue pas une nouvelle preuve de ventes commerciales complètes commises dans ce même scénario. Origine DCE du montage synthétique UNKNOWN conservée. Catalogue borné200 lignes/faits, lignes financières au-delà de9×10¹⁵ unités mineures non proposées ; aucune exhaustivité, conversion, validité externe ou couverture complète déduite. Les dates/solde sont des hypothèses citées, pas un calendrier juridique ou compte bancaire. Aucun portefeuille.

Méthode : Superpowers using-superpowers/brainstorming/TDD/systematic-debugging et revue ciblée ; ECC verification-loop. Graphify consulté avant navigation manuelle, Serena activée, Basic Memory miroir. OpenDesign Local : catalogue et contexte C08 relus pour conserver la surface financière ; Impeccable contexte/craft-floor/détecteur et inspection native. Aucune nouvelle direction visuelle ni promesse de conformité CYTD globale. Context7 non nécessaire : pas de nouveau contrat de bibliothèque ; Jev/Manus/GitHub non nécessaires, aucune publication externe.

A1 non admis, A2 HOLD et NO-GO public. Aucun candidat activé, porte changée, source réelle, VPS/déploiement, P3 réel, dépôt externe, exécution de paiement, commit ou push.

## Relevé final

Globale Web finale : **804 réussites/4 ignorés,93 fichiers/287.57s/exit0**. Backend final97/78,79s/exit0 ; UI9/3,29s. Mypy application708 sources, types Web/lint ciblé/Ruff/build verts ; avertissement de build sur gros chunk conservé. Semgrep1.183.0 :99 règles/5 fichiers initiaux puis2 fichiers UI corrigés,0 finding/0 erreur, métriques désactivées ; aucun résultat envoyé. Impeccable final0 finding. Pas de nouvelle globale backend.

Les5 sources gelées sont identiques pendant le navigateur final. Base jetable relue0 table métier/0 révision Alembic ; conteneur/volume, adaptateur/Vite et fichiers d’entrée UI temporaires retirés ; services utilisateur et daemon OpenDesign préexistants préservés. Liens, tranche unique, empreintes WIP, archive et miroir vérifiés dans `delivery.json`. Qualification locale acquise avec ces limites ; général PARTIAL et NO-GO public maintenus.
