# L08 — Reprise après remplacement du chiffrage, flux privés exclus — 05/11/2026

Le [plan global](../00_Pilotage_et_audits/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md) garde seul le statut. Ce dossier prolonge [L07](L07_CHIFFRAGE_PUBLIE_FLUX_DATES_2026-11-05.md) et la [reconstruction L08 après révision](L08_CHIFFRAGE_REVISE_PLI_EXACT_2026-11-04.md). Qualification synthétique locale, général PARTIAL ; aucun GO public.

## AS-IS, risques et plan minimal

Le parcours natif sait déjà importer/commettre/publier un nouveau chiffrage puis construire une réponse, une revue Patron, un snapshot/transmission, un nouveau pli et son P5 exact. La filiation financière du contrôle est descriptive : elle ne modifie pas les portes ni les octets d’un ancien pli. Manque de preuve retenu : présence de déclarations de flux privées pendant la reconstruction, invalidation de leur source et absence de ces données dans les sorties. Complément visible : expliciter la reprise humaine et l’absence de copie automatique des flux.

Risques : reprendre un accord ou un ancien hash, mélanger registre de trésorerie et réponse acheteur, afficher une référence comme fichier financier exporté ou conformité. Insertion minimale : callback de recette pour créer les données privées avant le nouveau brouillon, test couplé et deux paragraphes dans le contrôle existant. Aucun backend applicatif, calcul, droit, endpoint, contrat de commande, schéma ou porte modifié. Plan : vérifier baseline769/Git/autorités ; rouge UI→texte ciblé ; chaîne native et refus ; contrôle de tous les membres ZIP et JSON frais ; navigateur/contrôles/mémoire/backup.

## Résultat utilisateur et portée

Sur une référence REVIEW_REQUIRED, le contrôle indique le parcours nouveau brouillon sourcé → nouvelle revue Patron → nouveau pli → P5 sur son manifeste exact. Aucun accord précédent repris. Il précise que les flux/hypothèses privés ne sont pas repris automatiquement. Les liens de rapports, manques, signature/conformité UNKNOWN et référence de prix sans fichier exporté restent visibles.

Ce texte n’ajoute aucun blocage. Un ancien P5 reste l’acte enregistré sur son ancien pli exact ; la référence au nouveau chiffrage ne lui transfère pas cet accord. Le nouveau pli n’a pas de P5 avant un acte propre, et l’ancien hash est refusé pour l’autoriser. Une déclaration de trésorerie ultérieure ne change pas ses fichiers exportés.

## Recette native couplée

`backend/tests/db/test_l08_private_cash_rebuild.py` prolonge la recette native existante ; un callback optionnel de tests seulement est placé immédiatement après publication du chiffrage remplacé et avant le nouveau brouillon. Les callbacks de passation existants gardent leur comportement par défaut.

1. DCE synthétique multi-lots, réponse/annexe non financière, revue et pli initial exact déjà autorisé. Une déclaration CASH sourcée sur son rapport est créée, avec marqueur privé unique, IDs de flux/révision et solde sentinelle314159265 ; export et contrôle relu n’exposent rien de cela.
2. Nouveau classeur révisé reçu/commis puis coût17000 déclaré et nouvelle publication. Ancien contrôle : référence REVIEW_REQUIRED, manifeste/P5 d’origine inchangés. Ancien CASH : source REVIEW_REQUIRED, déclaration intacte et cumul retiré.
3. Nouvelle déclaration CASH sur la source financière exacte, nouveaux IDs et consentement, avant le brouillon/réponse reconstruits. Les manques de validité réelle restent UNKNOWN ; la note financière à recopier est refusée422 par le parcours existant.
4. Nouveau brouillon, nouvelle revue Patron, snapshot/transmission, pli FULL distinct. Nouveau manifeste, nouvelle référence de rapport, ancien P5 absent. Export avant nouveau P5 refusé422 ; ancien hash refusé422 ; nouvel acte P5 propre puis retry200 identique.
5. Tous les membres ZIP lus : marqueurs/IDs privés et314159265 absents ; `financial_amounts` exclu, aucun registre CASH ajouté. Le classeur interne révisé n’est pas exporté. Manifeste vérifié par SHA, référence officielle sans fichier financier toujours visible, réponses manquantes et conformité/signatures UNKNOWN.
6. Une troisième déclaration privée est enregistrée après autorisation. Nouvelle lecture HTTP du contrôle et export : données privées absentes du JSON comme des membres ZIP, manifeste inchangé et **ZIP byte-identique** à celui autorisé avant cette dernière déclaration. Cela ne signifie pas égalité de tous les octets HTTP du contrôle.

Trois révisions CASH1/2/3, deux plis et deux ensembles de revues/P5 distincts sont vérifiés. Les contrôles sont en lecture no-store ; le Collaborateur est refusé sur CASH et contrôle final. Aucun accord, aucune donnée financière privée et aucune conformité ne sont déduits d’une simple référence.

## Tests et revue

UI : rouge sur parcours humain/limite privée absents, puis **15 réussites/3,66s** (filiation et panneau Submission). Recette couplée initiale **1/43,69s**, puis renforcée après revue **1/42,97s**. La revue statique a fait chercher314159265 aussi dans le JSON et imposer une relecture fraîche après le dernier CASH, plutôt que réutiliser le contrôle antérieur ; ces corrections sont intégrées.

Régressions : **95 réussites/51,94s**, comprenant recette L08 originale, contrôle final applicatif et85 contraintes d’architecture. Première invocation de régression : fichier cherché à tort sous api/ plutôt que application/, sortie4 et aucun test ; erreur de chemin corrigée, pas un échec produit. Campagnes recouvrantes, aucun total additionné ni nouvelle globale backend revendiquée. Avertissement Starlette/httpx existant.

## Navigateur et confidentialité

Chrome DevTools MCP headless/isolé, pas Playwright MCP. La chaîne native complète est exécutée en HTTP/TestClient/PostgreSQL dans une nouvelle Affaire ; l’interface réelle lit ensuite, via ApiClient et adaptateur loopback qui conserve les jetons synthétiques hors navigateur, les contrôles vivants de l’ancien et du nouveau pli. Ancien : référence à revoir et instructions de reprise ; nouveau : manifeste/actes distincts, référence courante et aucun accord implicite. Lecture après dernière révision privée, aucune donnée CASH affichée. L’adaptateur vérifie aussi l’absence des marqueurs privés avant de renvoyer le JSON.

Desktop1280/mobile393 sans débordement global, cookies/localStorage/sessionStorage vides, ressources loopback uniquement. Capture mobile relue : manques nombreux, états UNKNOWN et filiation visibles. La publication/reconstruction/P5 sont exercés par HTTP natif, pas tous cliqués dans ce navigateur ; ce n’est pas une preuve d’auth réelle, reprise après crash, accessibilité exhaustive ou dépôt externe.

## Fichiers, méthode et limites

Production : `web/src/features/submission/SubmissionFinalControl.tsx` seulement, deux paragraphes sans changement de style global ni de porte. Tests : `SubmissionPricingReference.test.tsx`, recette `test_l08_pricing_response_continuity.py` (callback optionnel) et nouveau `test_l08_private_cash_rebuild.py`. Aucun backend applicatif changé, aucune migration ni nouvelle dépendance ; tête0147.

Superpowers using-superpowers/brainstorming/TDD et requesting-code-review ; ECC verification-loop. Graphify puis navigation ciblée, Serena activée, Basic Memory miroir. OpenDesign Local : catalogue et contexte financier existant relus, aucune nouvelle génération/direction ; Impeccable contexte/craft-floor/détecteur. Context7 non nécessaire pour ces contrats existants ; Jev/Manus/GitHub non nécessaires, aucune action externe.

Preuves privées `~/.local/share/smartao-proofs/l08-published-cash-packet-20261105/` : baseline769 empreintes, copies avant, gel4 fichiers, recettes/captures/ZIP et contrôles relus. La tranche DOCX n’est pas rouverte : cette chaîne native utilise la réponse Markdown et les pièces synthétiques existantes. La preuve d’absence porte sur les registres/champs/sentinelles connus ; aucune détection universelle de fuite en texte libre, formulaire arbitraire ou corpus réel. Aucune offre acheteur complète : fichier financier non inclus et manques persistants.

Pas de cash certain, validité externe, signature vérifiée, moteur candidat activé, porte promue, live, corpus réel, VPS/déploiement, P3 réel, dépôt externe, commit ou push. A1 non admis/A2 HOLD/NO-GO public.

## Relevé final

Globale Web finale : **805 réussites/4 ignorés,93 fichiers/179.96s/exit0** ;15 UI ciblés. Backend95 régressions/51,94s puis1 recette renforcée/42,97s, avec campagnes recouvrantes ; le dernier ajustement de capture JSON du contrôle relu est aussi exercé dans la chaîne native du navigateur sur sources gelées. Mypy application708 sources, types Web/lint/Ruff/build verts, avertissements App/chunk existants ; Impeccable0. Semgrep1.183.0 :4 fichiers initiaux,99 règles combinées Python/JS puis1 test Python final,0 finding/0 erreur, métriques désactivées ; aucun résultat envoyé. Pas de nouvelle globale backend.

Les4 sources gelées sont restées identiques durant la preuve native finale. Les deux rapports relus par l’UI ont des manifestes/revues/P5 distincts ; les trois révisions CASH demeurent privées. Base jetable relue0 table métier/0 révision Alembic ; conteneur/volume, adaptateur/Vite et entrées UI temporaires retirés. Sources, liens, marqueur unique, archive WIP et miroir vérifiés dans `delivery.json` à la livraison. Qualification locale acquise avec ces limites ; général PARTIAL, aucun transfert d’accord ni GO public.
