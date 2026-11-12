# C08 — Commande humaine de rapprochement des lignes

**Date :** 8 octobre 2026
**État :** intégrée et testée localement sur données synthétiques; aucune recette serveur live ni GO public.

## AS-IS et points d’insertion

Le POST existant `POST /api/v1/patron/cases/{case_id}/partner-offer-line-comparisons` conserve déjà l’acte append-only, l’isolation tenant/Affaire, le contrôle `PATRON_ADMIN`/`FINANCIAL_PRIVATE`, la revue `SAME_SCOPE_CONFIRMED` courante, le jeu exact des reçus encore actuels, l’optimistic concurrency et l’idempotence. Le web ne consommait auparavant que le GET read-only.

Le transport web typé `recordPartnerOfferLineComparison` réutilise ce POST et ne génère ni identité ni retry métier. Le formulaire est intégré au panneau C08 de la Revue Patron, avec `PartnerOfferLineComparisonCommand` et son modèle/formulaire dédiés. Aucune route, migration, dépendance ou écriture backend nouvelle.

## Comportement prouvé

- La commande ne s’ouvre qu’à partir d’une revue exacte `SAME_SCOPE_CONFIRMED` actuelle, dont tous les reçus sont actuels. Revue obsolète/non confirmée ou reçu historique : préparation bloquée et `REVIEW_REQUIRED` explicite.
- Chaque groupe reprend exactement les reçus de la revue; chaque champ — repère, référence, désignation, unité, quantité — commence à `UNKNOWN`/`null` et ne devient `DECLARED` qu’après saisie. Motif humain et confirmation explicite requis avant POST.
- Après résultat transport inconnu, le corps et les identités restent figés; seul le retry identique est offert. Après reçu 201/200, le reçu est contrôlé et un GET des revues et rapprochements relit la projection exacte. Un 409 interdit le retry POST et déclenche ces seuls GET; une nouvelle intention exige une action humaine après lecture.
- La réponse technique reste distincte de la projection GET. Si le reçu, la révision, la revue, les reçus ou les champs ne concordent pas, aucun succès n’est affiché; le reçu demeure consultable et l’état reste `UNKNOWN`/`REVIEW_REQUIRED` avec relecture GET seule.
- Le flux ne calcule ni montant, coût couvert, classement, disponibilité, réservation ou engagement partenaire; aucune confirmation externe, décision juridique ou promotion P3 n’est produite.

## Vérifications locales

- TDD du transport POST lors de la tranche précédente : rouge sur méthode absente, puis vert; `api.test.ts` 43/43.
- Tests du panneau et de la commande : 12/12, incluant confirmation préalable, dix champs `UNKNOWN`, sources/reçus exacts, refus de revue obsolète, retry identique après UNKNOWN, 409 sans second POST, relecture GET seule, reçu préservé quand le GET échoue et discordance non promue.
- Suite web complète : 493 réussis, 4 ignorés sur 66 fichiers. Typecheck, ESLint et build réussis.
- Semgrep 1.179.0 `p/security-audit` : 22 règles sur 7 fichiers, 0 finding. Impeccable detect retourne 4 avertissements historiques dans `styles.css` (lignes 154, 216, 381 et police Inter); aucun nouveau constat sur les sélecteurs ajoutés.
- Le prototype OpenDesign Local Codex est disponible [dans la preview locale](http://127.0.0.1:7456/api/projects/smart-ao-c08-line-comparisons/raw/index.html); ses tests synthétiques passent 26/26. Aucun navigateur Chromium n’était installé à l’emplacement configuré, et l’export image exige le runtime desktop : la recette visuelle navigateur n’a donc pas été exécutée.

## Limites

Les données et réponses de la recette sont synthétiques et testent la couche web; elles ne qualifient pas une API/DB live, un reçu externe authentifié, une pièce source vérifiée ni un groupement juridique. Le build conserve l’avertissement Vite sur le chunk principal de 676,03 kB (>500 kB). Aucun effet P3/GO public n’est déduit; A1 reste en attente, A2 générique HOLD et NO-GO public maintenu.
