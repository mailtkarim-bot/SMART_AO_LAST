# L04 — actes humains de preuve attendue et risque résiduel — 20 octobre 2026

## AS-IS, risques et insertion

Le lecteur de synthèse revalide déjà la source. Les actes de revue ne sont pas enregistrés. Réutiliser ApplicationCommand/CommandDispatcher/reçus/outbox et la politique Patron existante. Aucun autre registre ne porte ces champs source-liés. Préserver le WIP principal, HEAD30f2693.

Risques : double effet après timeout, première révision concurrente, portée/version remplacée entre lecture et acte, transfert d’un ancien acte, contenu financier libre exposé, confusion déclaration/preuve ou porte. Une déclaration n’est jamais une confirmation de conformité.

## Plan minimal autorisé

1. Commande fermée : états DECLARED/UNKNOWN, texte requis uniquement si DECLARED, raison UNKNOWN et justification humaine ; validation de l’empreinte source et expected_revision. TDD pur.
2. Registre Case append-only0137 : tenant/Affaire/point/source/version/portée/révision/auteur, précédence et contraintes. Premier acte/révision sous verrou Case et source ; reçus idempotents existants ; mise à jour des contrats de tête et migration réversible sans perte silencieuse d’actes. TDD PostgreSQL.
3. POST et lecture de synthèse dans les parcours existants, gardes Patron/MFA et capacités natives de lecture/écriture financière ; JSON de provenance dérivé côté serveur. Ancien acte visible comme à revalider sans contenu transféré si le contexte change.
4. Formulaire Patron explicite, justification/confirmation et intent identique après UNKNOWN ; masquage contexte, 409, double clic, saisie et relecture en Chromium isolé/API synthétique. OpenDesign Local et Impeccable avant UI.
5. Revue, suites adaptées et migration upgrade/contraintes/downgrade/head, lint/types/build/Semgrep, journal/plan/index et miroir local.

Aucune confirmation/porte modifiée ; DPGF non RAG, candidats inactifs, A1 non admis, A2HOLD, NO-GO public. Aucun live/corpus réel/VPS/déploiement/P3/push.

## Qualification locale acquise

Commande `RecordAnalysisAssessment`, POST `/api/v1/cases/{case_id}/analysis-assessments`, registre `case_analysis_assessments` et formulaire Patron intégrés aux projections existantes. Aucun moteur candidat activé, aucune confirmation ni porte modifiée. Aucun événement envoyé au worker cockpit : acte immuable et reçu durable constituent la trace locale.

Le serveur dérive le manifeste source et son SHA-256 : tenant/Affaire, version DCE, portée exacte, point/révision native, document/hash/extraction/fragment et région. Patron, appartenance, capacités natives et MFA récente sont exigés. Les verrous Case, point natif, document et version protègent l’écriture; la révision attendue refuse les actes concurrents. Les reçus existants donnent un seul effet aux retries identiques. Toute source obsolète ou point absent de la version courante produit un conflit 409 après contrôle d’accès à l’Affaire; une Affaire étrangère reste non observable.

Migration `20261020_0137` : clé tenant/id, contraintes de texte/état, prédécesseur exact et révision, triggers refusant UPDATE/DELETE. Upgrade et downgrade vide qualifiés; downgrade avec actes explicitement interdit pour éviter leur perte. Tête runtime et runbook alignés. La barrière C10 reste conservée.

`human_assessment` est la projection typée de référence : auteur, date serveur, révision, justification, prédécesseur et empreinte courante. Un contexte remplacé masque les textes et rend REVIEW_REQUIRED/UNKNOWN; aucun ancien acte concordant n’est ressuscité. Les champs historiques nus `expected_evidence`/`residual_risk` restent UNKNOWN. Une déclaration de preuve attendue n’est ni une preuve reçue/vérifiée ni une évaluation automatique du risque.

Formulaire explicite : état DECLARED/UNKNOWN, raison de l’inconnu, justification et confirmation. Double clic bloqué; après UNKNOWN, les champs restent gelés et seul le même intent est rejoué. Un refus MFA lors d’un retry ne résout pas l’incertitude précédente. GET de réconciliation seulement après reçu concordant ou 409. Le magasin App conserve l’intent lors d’une navigation et le masque hors propriétaire/Affaire/rôle. **Limite : un rechargement complet du navigateur détruit ce magasin mémoire; aucune reprise durable navigateur n’est qualifiée.** Les protections serveur d’idempotence et de révision demeurent.

## Preuves exécutées et périmètre

Preuves privées : `~/.local/share/smartao-proofs/l04-acts-20261020/` (hors Git).

- TDD : modules absents, MFA expirée, verrou natif, perte de l’intent au remontage, refus MFA après UNKNOWN et disparition du point après rectificatif reproduits avant correction. Dernière régression : NOT_FOUND_OR_FORBIDDEN au lieu de STALE_SOURCE_CONTEXT; correction minimale puis **13 tests SQL verts** (`version-conflict-green.log`, 7,70 s).
- Backend global : **3 663 réussites**, 2 avertissements, 836,45 s, exit0 (`backend-global-final.log`). Cette mesure précède la dernière correction 404→409; **la suite entière n’a pas été relancée après cette ligne**, couverte ensuite par les 13 tests SQL. Le premier global interrompu à 2 346 n’est pas qualifiant. Les erreurs intermédiaires d’accès au socket sandbox ne sont pas des régressions produit.
- Gate précédent : 51 tests ciblés SQL/synthèse/C10/purs; suite Web finale **593 réussites, 4 ignorés**, 69 fichiers (`web-global-delivery.log`); types/lint/build verts, avertissement historique de taille de chunk conservé.
- Navigateur **Chrome DevTools**, Chromium isolé et API/session synthétiques : **24 contrôles desktop + 24 mobile** (`browser-*-acts-delivery.json`). Saisie, relecture auteur/date/justification/UNKNOWN, double clic, changement de contexte/rôle, 409, reçu discordant, timeout simulé et retries identiques vérifiés. Aucun Playwright MCP utilisé. La première simulation de perte par fermeture transport était réessayée automatiquement par Chromium; le simulateur a été corrigé par une réponse503 après persistance synthétique, puis recette rejouée.
- Revue ciblée indépendante : verrou natif et conservation du pending corrigés après preuves rouges; pas de validation humaine métier déduite. Superpowers (cadrage/plan/TDD/revue/vérification), ECC (migrations/API/vérification), Graphify, OpenDesign Local (système existant) et Impeccable appliqués. Aucun Cloud/BYOK, nouvelle dépendance ou refonte visuelle.

Contrôles finaux : Ruff/diff verts; 47 contrats documentaires verts; Semgrep1.179.0, 225 règles sur23 fichiers, 0finding/0erreur, sans upload de code/résultats. Manifestes SHA-256 privés conservés. Vue mobile contrôlée : tableau interne défilant horizontalement, pas de certification d’ergonomie mobile exhaustive. Onglet et serveur synthétiques arrêtés; base jetable vérifiée Alembic0 puis conteneur arrêté. Aucun autre conteneur ou état de travail touché.

## Limites et suite

L04 demeure PARTIAL : cette tranche qualifie l’enregistrement humain local de deux champs, pas l’analyse exhaustive des douze axes. Pas de backend/authentification live, corpus réel, preuve économique par RAG, audit WCAG exhaustif, export, P3, VPS, déploiement, commit ou push. UNKNOWN et régions/champs absents restent visibles. A1 non admis, A2 générique HOLD et NO-GO public maintenus.

Le miroir Basic Memory n’a pas été transmis : l’autorisation automatique avait refusé l’écriture externe. Proposition conservée localement; le plan est l’autorité de reprise.

Prochaine étape : L04 — raccorder à l’axe Prix et marge les scénarios économiques natifs déjà enregistrés pour l’Affaire, avec révision, hypothèses et provenance exactes; afficher les absences ou obsolescences en UNKNOWN et qualifier tenant/rôle/FINANCIAL_PRIVATE sans utiliser le RAG pour la DPGF ni modifier confirmations ou portes. DPGF non évaluable par RAG, aucun moteur candidat activé; A1 non admis, A2 générique HOLD et NO-GO public maintenus.
