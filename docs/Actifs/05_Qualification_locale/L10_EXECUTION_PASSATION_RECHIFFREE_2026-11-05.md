# L10 — changements d’exécution sur la passation du pli reconstruit

Qualification locale avec limites ; le plan global reste seul statut. L10 général demeure PARTIAL.

AS-IS : événements, applicabilité humaine, impacts déclarés, actions et projection opérationnelle existent. L09 a qualifié deux passations exactes après révision de prix ; leur continuité vers L10 reste à rejouer. Le panneau n’a pas encore de suspension de source ou de scope de session explicite.

RISQUES : lecture ou formulaire anciens sous reprise DCE incertaine, action rattachée à une autre passation, anciens accords réemployés, montant privé rendu au conducteur, date/impact déclaré pris pour effet juridique ou engagement certain.

POINTS D’INSERTION : wrapper du panneau et appel App ; callbacks de recettes L09/L10 existantes, sans modification des portes ou handlers sauf défaut reproduit.

PLAN MINIMAL :

- [x] Observer les rouges de suspension Patron/Responsable et de scope de lecture, puis corriger sans perdre les intentions UNKNOWN.
- [x] Prolonger le parcours du pli rechiffré en changements/actions explicites et liaison d’impact UNKNOWN sur la nouvelle passation ; refus des reprises anciennes et de C3 sans liaison courante.
- [x] Vérifier confidentialité, sources, manques, historique, idempotence et régressions adaptées.
- [x] Revue, rendu, sécurité et sauvegarde, puis plan et miroir relus.

TESTS À AJOUTER : aucune lecture/écriture sous suspension pour les deux rôles, réponses tardives annulées après changement de scope, anciennes actions à revoir après nouvelle passation de même DCE, nouveaux actes/reviews/reçus sans héritage, impacts financiers exclus de la projection opérationnelle, effets juridiques UNKNOWN. Réutilisation Markdown ; aucune reprise de tranche DOCX.

Checkout principal, branche et HEAD attendus vérifiés ; les 757 empreintes du WIP L09 sont identiques avant édition. Preuves privées : `~/.local/share/smartao-proofs/l10-repriced-execution-20261105/`. Aucun nouveau checkout/reset/clean/stash/stage/commit/push/live/dépôt ou effet externe.

## Fonction et fichiers

Le wrapper `CaseContractChangePanel` suspend les interfaces Patron et Responsable pendant la reprise DCE incertaine. Il distingue désormais le périmètre stable d’intention (propriétaire/Affaire/rôle) du périmètre de lecture (session/version/disponibilité DCE). Un remount retire l’ancien affichage et les brouillons/confirmations, annule les lectures tardives et conserve les intentions UNKNOWN dans le store existant. Le retour à une source connue n’est pas une nouvelle autorisation.

Six fichiers logiciels : `web/src/features/decision/CaseContractChangePanel.tsx`, son test et `web/src/app/App.tsx` ; `backend/tests/db/test_l09_repriced_packet_handover.py`, `backend/tests/db/test_l10_rectified_changes.py`, `backend/tests/db/test_l10_repriced_execution.py`. Les deux recettes existantes gagnent seulement des callbacks/runners optionnels de qualification ; le défaut et les assertions natives restent conservés. Aucun backend de production, handler, gate, permission, schéma, migration, calcul ou moteur changé.

## Parcours couplé qualifié

Une Affaire suit L08/L09 en Markdown : prix importés/publiés, premier pli et P7/reçu, révision de prix, nouveau brouillon/revue/snapshot/P5/ZIP, nouveau P7/reçu. Chaque passation précise ses octets exacts et les engagements humains. Les deux générations de changements se rattachent ensuite à leur vue P7, à leurs points et au hash exact du pli.

Chaque génération crée un événement sourcé, une relecture d’applicabilité humaine avec delta déclaré, une action publiée et une liaison économique C4 UNKNOWN. Le changement ne devient pas un effet juridique ; les références d’instruction/pièces restent déclarées. La deuxième génération exige des IDs/actes nouveaux et refuse les anciens points, hashes et revues sans ajouter d’événement/outbox. L’ancien événement/action passe REVIEW_REQUIRED ; l’historique conserve ses actes et textes, sans report de responsable ou de preuve attendue dans V2. Les valeurs absentes restent UNKNOWN, pas zéro, date légale ou accord supposé.

La projection Responsable conserve la source de passation, le hash du pli et les engagements publiés ; elle n’inclut pas impact_declarations, financial_snapshot, montants ou storage_key. Lecture privée Patron refusée au Responsable et lecture anonyme refusée. La source est d’un DCE initial de fixture déjà admis/classifié, avec copie de développement du parcours L08 ; ni nouveau réimport DCE ni nouvelle qualification DOCX/OCR dans cette tranche.

## Limite C3 exacte, sans provenance inventée

Le parcours couplé présente `a1_engagements_state=UNKNOWN` et aucune source A1 courante. Il ne démontre donc **pas** une nouvelle déclaration quantitative C3 sur le pli rechiffré. La recette d’origine prouvait une liaison C4 UNKNOWN avec des déclarations C3 vides ; cela n’a pas été présenté comme un impact chiffré.

Le complément enregistre une liaison C1 explicitement UNKNOWN, puis prouve que C3 reste refusé422 `C2_LINKAGE_NOT_CURRENT_OR_LINKED`, avec compteurs d’événements/outbox inchangés et aucune déclaration. Le garde C2 intervient avant toute validation du tuple C3 fourni dans cette tentative négative : ce test ne qualifie pas un tuple de provenance invalide comme source réelle. Ni engagement, profil ou condition A1 valide fabriqué, ni condition rouverte, ni porte assouplie pour faire passer une déclaration.

Les cas C3 positifs et leur invalidation sont rejoués dans **un scénario distinct** de `test_case_handover_http_e2e.py`, avec sa propre chaîne A1 sourcée. Cette preuve n’est pas attribuée au parcours couplé. Rendre un impact quantifié sur ce dernier nécessitera un rattachement A1 courant réellement disponible et un acte Patron ; UNKNOWN protège ce manque sans prouver sa complétude.

## TDD, revue et vérifications

- Web global final : **792 réussites,4 ignorés,93 fichiers,287,25 s,exit0** ; six SHA logiciels inchangés.
- Trois rouges Web observés : suspension des deux rôles absente et absence de deuxième lecture après nouveau scope. Puis huit tests du panneau verts ; ciblés finaux : **10 réussites,3 fichiers,12,17 s** incluant store et consentement existants. Types, lint et build Web verts ; avertissements préexistants `setDecisionDossier` dans App et chunk >500 kB conservés.
- Parcours couplé initial : **1 réussite en114,35 s**. Variante négative C3 : premier échec d’assertion sur le préfixe de code attendu (C3 au lieu du refus C2 réel), corrigé sans changer le produit. Campagne backend finale : **21 réussites en155,56 s**, parcours nouveau, HTTP E2E natifs, workflow opérationnel et upload d’évidence. Contrats opérationnels purs séparés : **6 réussites en2,99 s**. Sources périmées, rôles/tenant/MFA, inconnus, append-only, idempotence, concurrence, impact C3 positif distinct et refus couplé exercés.
- Mypy application708 sources vertes ; application/tests206 diagnostics dans40 fichiers sur1274 sources, identiques à L09 après normalisation des numéros de ligne. Ruff/format des trois fichiers Python vérifiés ; Alembic inchangé `20261102_0147`, fixtures upgrade/downgrade jusqu’à base.
- Revue indépendante en lecture seule : aucune régression concrète identifiée ; limite C3 relevée, puis contre-revue du complément de refus. La revue n’a ni exécuté de tests ni ajouté une validation humaine.
- OpenDesign Local Codex : catalogue/artefact SMART AO existant consultés ; styles existants conservés, référence Linear complémentaire seulement, autorité Owner/CYTD inchangée. Impeccable contexte/craft-floor/harden, detector `[]` ; aucun nouveau prototype ou Cloud.
- Chrome DevTools Local : vrai panneau opérationnel sur projections natives enregistrées aux deux instants, relecture simulée sans écriture. Suspension/reprise et relecture exercées ; captures inspectées à1280/393px, absence de débordement global/cookies/stockage/ressources externes. L’article V2 contient la passation exacte et UNKNOWN sans anciens responsable/preuve ; l’article V1 reste visible à revoir, ce n’est pas un héritage dans V2. Pas de Playwright, nouveau login/écriture UI réels ou audit WCAG complet. Les captures proviennent de la première recette couplée valide ; le complément C1/C3 privé ne modifie pas leur déclaration d’impact publique.
- Semgrep1.183.0, `p/security-audit`, métriques désactivées :99 règles/6 fichiers,0 finding/0 erreur ; analyse locale sans transmission de résultat ni certification globale.
- Six SHA logiciels figés et relus, diff scoped vérifié et scan borné des lignes ajoutées sans secret reconnu. Base jetable :0 table métier/0 révision Alembic ; conteneur exact `211ef163922bfe6a9b3a716dcbbf3d4c622c6f8ae5450b6f7d232b2891007b1a`, sans montage persistant, supprimé. Clients navigateur et preview dédiés fermés ; services préexistants conservés.

## Invariants, limites et suite

Tenant/ownership/permissions, FINANCIAL_PRIVATE, MFA, append-only, idempotence, source/version/hash/locator, UNKNOWN et portes P0–P7 conservés. Aucun prix certain, budget couvert, ordre exécuté, calcul juridique, nouveau droit contractuel ou paiement certain déduit. P7 n’est pas un OS, l’action déclarée n’est pas une exécution extérieure.

Les stores sont en RAM, sans reprise durable après recharge complète. Les changements externes peuvent nécessiter une relecture ; aucune surveillance continue ajoutée. Contrat/attribution/pièces restent déclarés, authenticité et autorité inconnues. C3 non créé dans le parcours sans A1 courant ; C4 UNKNOWN et delta humain ne sont pas un chiffrage. L10 général PARTIAL ; A1nonadmis/A2HOLD/NO-GO public et candidats inchangés. Aucun stage/commit/push, live/corpus réel/VPS/déploiement/dépôt ou effet externe.

Méthode : Superpowers cadrage/plan/TDD/revue/vérification, ECC product-capability/security-review/verification-loop ; Graphify avant recherche, Serena activée, OpenDesign Local Codex, Impeccable, Chrome DevTools Local et Basic Memory. Context7 sans question de bibliothèque nouvelle, Jev/Manus sans gain dans ce périmètre borné. Plan seul statut ; miroir synchronisé après consolidation finale.
