# L02 — bibliothèque, profil et adoption explicite

Qualification locale synthétique ; statut exclusivement dans le plan global.

## Cadrage et plan minimal

AS-IS : bibliothèque privée tenant-scopée, upload enregistré avec hash, vérifications humaines versionnées ; profil de méthode V1 borné au vocabulaire et contrôles informatifs ; publication immuable et adoption par Affaire append-only. La publication ne copie pas les pièces et ne vaut pas adoption.

RISQUES : confondre présence, vérification humaine et validité officielle ; masquer une échéance absente ; perdre les anciennes adoptions dans une projection limitée au courant ; transférer une configuration ou une pièce implicitement.

POINTS D’INSERTION : lecteur et contrat de bibliothèque, projection/historique et route du profil, panneaux et client React existants. Aucun nouveau moteur, dépendance ou schéma de profil ; aucune migration prévue.

PLAN MINIMAL : prouver les manques avant code ; exposer la provenance et les limites de validité ; rendre l’historique d’adoption relisible ; qualifier publication distincte de l’adoption, retour explicite à une ancienne version et conservation des sources ; vérifier les refus et contrôles ciblés.

TESTS À AJOUTER : historique 1→2→1 et retry sans doublon ; refus tenant/Collaborateur ; pièce sans échéance et pièce expirée sans validation présumée ; provenance exacte ; parcours HTTP synthétique et composants existants.

## Résultats

Les résultats bornés sont consignés ci-dessous. Le plan seul porte la tranche active ; aucune conformité ou promotion de porte déduite.

## Fonction livrée et surfaces

- Bibliothèque Patron : identifiant immuable de pièce et SHA-256 relus dans le même tenant ; aucun storage key, nom de fichier interne, command_id ou idempotency_key ajouté à cette projection. Le champ d’empreinte est optionnel pour les projections historiques ; absence = UNKNOWN. Le test de non-exposition historique a été ajusté volontairement pour ce seul champ, désormais nécessaire à la provenance visible.
- Échéance absente/ininterprétable : UNKNOWN ; échéance déclarée dépassée : EXPIRED, séparée du verdict humain PENDING/VALIDATED/REJECTED. Comparaison à l’ouverture de la vue, explicitement annoncée. Une date future ne devient pas une validité officielle.
- Historique `GET /api/v1/patron/cases/{case_id}/business-method-profile/adoptions` : actes existants ordonnés par révision, profil ID/version/hash exacts, refus neutre tenant étranger et accès Patron. La lecture courante conserve sa requête bornée antérieure.
- Interface du profil : avant/après relisibles, confirmation liée à l’Affaire/révision/version/hash, liste des actes ; retour à v1 après v2 = nouvel acte r3, sans réécriture de r1/r2. Le profil V1 reste borné au vocabulaire et aux contrôles informatifs ; ni pièces ni droits ne sont copiés automatiquement.
- Reprise du hook : intent conservé par propriétaire/entreprise ou Affaire, mutex synchrone contre double clic, reçu incomplet conservé UNKNOWN, pas de nouvel intent ni GET de réconciliation pendant l’incertitude ; retry exact et bouton de reprise après aller-retour de périmètre. Les réponses tardives d’un autre périmètre ne sont pas projetées.
- Lisibilité mobile : références complètes et JSON reviennent à la ligne ; le premier contrôle visuel avait montré des hash coupés malgré une largeur mesurée sans débordement, corrigés puis revus.

Fichiers applicatifs : `backend/app/modules/enterprise/{application/business_method_profile_handler.py,application/enterprise_library.py,infrastructure/library_reader.py,public/enterprise_contracts.py}`, routes `patron_business_method_profiles.py` et `patron_enterprise_library.py` ; `web/src/features/enterprise/{BusinessMethodProfilePanel.tsx,EnterpriseLibraryPanel.tsx,useBusinessMethodProfile.ts}`, `web/src/infrastructure/api.ts`, `web/src/shared/types.ts`, `web/src/app/{App.tsx,styles.css}`. Aucun changement de dépendance, migration ou schéma du profil.

## Preuves exécutées

Racine locale privée : `/home/noor/.local/share/smartao-proofs/l02-library-profile-20261103/`.

- Rouges observés : absence d’historique, absence de SHA dans la projection, absence de confirmation, échéance inconnue/expirée invisible, nouvel intent après UNKNOWN, reprise impossible après aller-retour de périmètre. Les tests des nouveaux comportements ont ensuite été observés verts.
- Backend final : **79 réussis / 187,10 s**, modules profil/persistance/domaines, bibliothèque, upload privé, handlers d’upload, capacités et routes. L’API native traverse bibliothèque → publications v1/v2 → adoptions 1→2→1, replay sans doublon, historique et refus du tenant étranger. L’append-only est exercé en SQL. Avertissement Starlette/httpx préexistant.
- Web ciblé final : **12 réussis / 6,74 s**, panneaux et hook ; confirmation, UNKNOWN, mutex, absence de GET avant résolution, IDs identiques et aller-retour de périmètre. Trois scénarios App/C07 ayant échoué dans une première campagne chargée sont repassés **3/3 / 12,72 s** sans changement de leur logique.
- La première recette API a rencontré une erreur de fixture (marqueur produisant plus de 64 caractères), corrigée avant réussite ; ce n’était pas un rouge produit. La première campagne globale Web a été interrompue après échecs/timeouts : elle ne vaut pas PASS. Résultat du rejeu global final ajouté ci-dessous quand disponible.
- Navigateur final : Chrome DevTools MCP installé, contexte isolé headless, composants React réels et API/TestClient/PostgreSQL natifs via pont HTTP local ; aucun Playwright MCP disponible. Publication v1, réponse d’adoption native 201 masquée en 503, sélecteur/actualisation bloqués, retry natif 200 avec mêmes command_id/idempotency_key, publication v2 sans adoption implicite, adoption explicite v2 puis retour explicite v1. SQL final : **3 actes, versions [1,2,1]**, bibliothèque identique avant/après. Deux pièces synthétiques et leur hash binaire réel ; scanner et inspection de fixture, pas de vrai ClamAV ni de validité officielle démontrés.
- Captures finales inspectées : bureau 1280 px et mobile émulé 393 px, références lisibles, aucune largeur excédentaire ; UNKNOWN/EXPIRED présents, cookies/localStorage/sessionStorage vides, ressources de page externes absentes. Ce constat ne garantit pas l’absence de tout trafic du système. Les premiers appels navigateur (timeout de navigation, clic programmatique non concluant, option sélectionnée par valeur au lieu du texte attendu par l’outil) restent des erreurs d’outillage documentées ; aucune mutation n’a été rejouée sans relire l’état natif. Le parcours final a été rejoué sur une nouvelle base synthétique vide.
- Contrôles : Ruff et format ciblés verts ; mypy applicatif **708 fichiers sans erreur** ; mypy app/tests **206 diagnostics dans 40 fichiers / 1260 fichiers analysés**, identités normalisées identiques à la preuve L01 finale, aucune nouvelle dette ; types, ESLint et build Web verts (avertissements préexistants setDecisionDossier et chunk >500 kB).
- Semgrep **1.183.0**, configuration `p/security-audit`, métriques désactivées, `--no-git-ignore` : **99 règles exécutées, 21 chemins analysés, 0 finding, 0 erreur** ; analyse locale, pas d’envoi de résultats. Ne vaut pas certification sécurité.
- OpenDesign Local : catalogue courant, artefact C08 existant et système consultés ; conventions de l’interface en place conservées. Impeccable context/polish/craft-floor et detector : quatre avertissements dans le CSS préexistant (lignes 2/154/216/389), aucun sur les nouvelles règles de retour à la ligne ; pas de refonte hors périmètre. Revue indépendante lecture seule : P1 UNKNOWN identifié puis corrigé, aucun autre blocage relevé ; limite mémoire React confirmée.

## Invariants et limites

Général L02 PARTIAL : la recette bornée ne démontre pas l’adéquation de toute pièce à chaque exigence ni une assurance/HSE, validité officielle ou conformité. Les pièces restent des sources de bibliothèque ; adopter une méthode n’en fait pas des preuves de candidature ou des annexes du pli. Les anciens contextes C07 ne sont ni complétés ni recalculés. Le scénario A1 complet historique à deux profils n’a pas été rejoué dans cette tranche.

Les intents UNKNOWN ne survivent pas à un rechargement complet/unmount : aucune persistance navigateur ajoutée. La reprise exercée concerne la vue montée et ses aller-retours. L’échéance affichée est une observation à l’ouverture, pas une horloge juridique. L’historique d’adoption est une liste intégrale, sans pagination nouvelle ; sa volumétrie longue n’est pas qualifiée.

Isolation tenant, rôle Patron, append-only, identifiants et hash exacts, UNKNOWN et séparation des actes conservés. Aucun candidat activé ; A1 non admis, A2 HOLD, portes B0/B1/B2/P0–P7 et NO-GO public inchangés. Aucun live, corpus réel, VPS, dépôt externe, commit, push ou effet externe.

Méthode : Superpowers using-superpowers/brainstorming/writing-plans/TDD/requesting-code-review/verification-before-completion ; ECC product-capability et verification-loop. Graphify interrogé avant navigation manuelle ; Basic Memory miroir du plan. Serena non requis pour ces lectures ciblées sans navigation sémantique ; Context7 non requis, aucun nouveau contrat de bibliothèque externe à inférer ; Jev/Manus non utilisés, travail borné déjà vérifiable par code/tests/revue. GitHub et connecteurs externes non utilisés, travail strictement local.

Les deux bases propres `l02_library` et `l02_browser` ont fini à **0 table métier / 0 version Alembic**, puis le seul conteneur `827f749351dc19b20fa05a0829dfdb8a3c37534745ee4a6ac25128760c39f657` (Mounts=[]) a été arrêté/supprimé ; preview et navigateurs de qualification fermés. Services utilisateur préservés.

## Vérification finale du 03/11

Rejeu Web global final, seul après fermeture des ressources de qualification : **92 fichiers réussis, 740 tests réussis / 4 ignorés, 250,80 s**. Les campagnes précédentes interrompues/échouées restent distinctes ; elles ne sont pas transformées en PASS. Les 21 empreintes de fichiers logiciels sont restées exactes pendant cette vérification. `git diff --check` et revue du delta contre WIP préservé effectués ; aucun motif de secret ajouté détecté dans ce delta.

La recette locale demandée est consignée avec les limites ci-dessus ; le plan seul porte le statut et la suite.
