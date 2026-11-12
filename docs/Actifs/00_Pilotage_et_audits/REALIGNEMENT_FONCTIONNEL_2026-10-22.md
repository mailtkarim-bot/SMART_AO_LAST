# Réalignement fonctionnel demandé par l’Owner — 22 octobre 2026

## Décision appliquée

Le plan global reste l’unique statut. Cette revue remplace sa direction « nouveau challenge DCE » par la livraison des fonctions métier manquantes. Elle réutilise les11livrables/3garanties et45familles existants; aucun nouveau catalogue de versions de candidats. Une preuve locale de parcours et l’exhaustivité automatique sont deux contrats distincts. L04 reste PARTIAL au niveau du cahier, mais son parcours humain source→traitement→préparation→revue est prouvé localement; la perfection OCR/RAG ne bloque pas tous les autres livrables.

AS-IS : Python/API/UI existent sur les11livrables; matrice et cahiers actifs maintenus. La revue14/10 et matrice19/10 décrivent déjà des manques; la méthode20/10 n’a pas empêché une succession de micro-qualifications. Revue actuelle des contrats/scripts de prix : onglet actif seul, formule masquée par data_only, quantité absente remplacée par1, prévisualisation tronquée à contrôler avant persistance. Présence des fichiers et3809tests verts antérieurs ne prouvent pas l’achèvement des45familles.

RISQUES : coûts/postes omis, quantité inventée, double compte, dépendances de travail artificielles, confusion fonction disponible/couverture automatique. Préserver FINANCIAL_PRIVATE, tenant, append-only, concurrence, MFA, portes et UNKNOWN.

## Carte du produit confrontée au code existant

Références du CSV vérifiées sur le checkout principal/WIP. Le détail chemin/code/tests/surface reste dans le CSV compagnon; les manques ci-dessous sont des hypothèses de travail à confirmer par régression, pas45verdicts de conformité. Toute preuve plus récente des journaux prévaut sur la date19/10. Les reports PF31-09 sont maintenus.

| Livrable | CDC métier | Cahier technique | Résultat attendu | Manques et limite du bilan existant |
|---|---|---|---|---|
| T01 | PF31-05/06/07; M31-07 | CT31-06 | Session/MFA/step-up/permissions, refus sans fuite, retry sans double effet. | Rejouer les refus serveur et projections croisées pour chaque verticale ; pas de pentest ou exploitation réelle déduit des tests locaux. |
| L02 | PF31-05; M31-06 | CT31-05 | Bibliothèque de preuves/capacités et profil publié, versionné puis adopté explicitement par une Affaire. | Prouver adéquation/validité des pièces pour chaque exigence et delta d’adoption sur Affaire existante ; une attestation ne prouve pas une couverture réelle. |
| L01 | PF31-03; M31-01; M31-03 | CT31-02/06 | Une opportunité expliquée, qualifiée humainement, reliée à une Affaire et à ses lots. | Prouver le scénario annonce → qualification → ouverture sans doublon, motifs sourcés et données manquantes visibles ; pas de probabilité commerciale inventée. |
| L03 | PF31-03; M31-03 étape 1; M2-029 | CT31-02/04 | Inventaire de la version applicable : reçus, exclus, annoncés manquants, extraits/non extraits, sources consultables. | Qualifier l’inventaire réellement reçu et les portées lot ; ne pas confondre extraction avec analyse complète. Les PDF/raster/tableaux complexes et sources non éligibles conservent leurs limites. |
| L04 | PF31-06; M31-02/03; M2-026/027 | CT31-02/03/06 | Pour chaque axe : constats, exigences, risques, applicable/inconnu, sources, conséquences, responsable, action et preuve attendue. | DCE mixtes PDF/DOCX/XLSX, graphes/raster, rectificatif/reprise de traitement et généralisation au corpus réel non qualifiés; montants/délais/échéancier UNKNOWN sans acte. |
| L05 | PF31-03/06/07/08; M31-02/03; M2-028 | CT31-02/03/06 | Un engagement précis, ses impacts/hypothèses et une condition humaine expliquée, avec portes et inconnus visibles. | Étendre la lecture aux engagements critiques identifiés par L04 ; relier chaque conséquence à sa source, unité, hypothèse et revue. Les impacts déclarés ne deviennent pas des coûts complets calculés. |
| L09 | PF31-04/06; M31-04 | CT31-02/04/06 | Engagements vendus, exclusions, conditions ouvertes, contrat attribué distinct et dossier conducteur sans données privées. | Déclarer les liens/écarts réels au contrat gagné et enrichir le snapshot opérationnel ; recette du conducteur à rejouer sur scénario complet. |
| L11 | PF31-08/09; M31-05/07; M2-026 axe12 | CT31-04/07 | Réserves/obligations/événements de paiement distincts, actions de préservation et enseignements sourcés. | Écarts prévu/réalisé et chaîne de sortie à qualifier. Calcul juridique/calendaire validé, sanctions quantitatives et settlement/DGD structurés restent différés par PF31-09. |
| L10 | PF31-04/08; M31-05 | CT31-02/04/07 | Instruction/OS/avenant relié à l’engagement concerné, delta déclaré et action/preuve suivis dans la chronologie. | Prouver le fil complet sur même Affaire après remplacement de source/contrat ; aucune réception externe ou conséquence juridique déduite d’un acte enregistré. |
| L06 | PF31-08; M31-03 étapes 3–4; M2-026 axes6/9 | CT31-02/03/06 | Prix importés et scénarios, devis exacts, inclusions/exclusions, validité, transport et postes couverts/inconnus. | Relier obligations/coûts et lignes sources, feuilles/cellules, devis/validité et exclusions ; rendre non chiffré/double compte/incomparabilité visibles. DPGF non évaluable dans les essais RAG ne signifie pas absence du module import financier. |
| L07 | PF31-08/09; M31-02; M2-026 axes7/8 | CT31-02/07 | Ressources/périodes/compétences et hypothèses de cash/garanties, séparant prévu, déclaré, inconnu et constaté. | Prouver saisie/source → calcul → lecture des périodes et ressources critiques ; échéancier cash minimum par Affaire et garanties. Portefeuille cash avancé reste explicitement différé. |
| L08 | PF31-03/07/09; M31-02; M2-026 axe11 | CT31-36–42 | Réponse technique/administrative substantielle, pièces acheteur, engagements vendus et paquet exact versionné/hashé. | Produire les contenus répondant à chaque exigence et prouver couverture/format/signature par pièce ; conserver confirmation/MFA/hash et dépôt humain distincts. |
| T02 | PF31-09/10; M31-08/09 | CT31-08/09/10 | Migrations/provenance/export/audit/reprise vérifiables et bilan de limites, avant toute ouverture. | Droits corpus/validation métier, restauration et exploitation réelle restent à qualifier ; ERP et validation marché ne sont pas déduits des adaptateurs. |
| T03 | PF31-06/11; M31-03/04/05 | CT31-06 | Accès compréhensible aux sources, états et actions, clavier/responsive et masquage hors contexte. | Qualifier chaque livrable complet en navigateur, règles de masquage et accessibilité ; utiliser OpenDesign Local Codex/Impeccable avant toute édition visible. |

## Ordre de livraison et points d’insertion

1. **L06 — bordereau→chiffrage traçable** : importer toutes les feuilles tabulaires compatibles, conserver source/feuille/cellules, refuser les formules non qualifiées et toute prévisualisation incomplète; prouver aperçu→persistance→brouillon, relecture, retries et refus. Module pricing existant, pas RAG.
2. **L07 — ressources et trésorerie par Affaire** : saisies datées/hypothèses→calcul déterministe→périodes critiques/raisons UNKNOWN; réutiliser optimization/financial, compléter les données temporelles absentes. Pas de portefeuille avancé ni de zéro par défaut.
3. **L05 — engagement→impact→condition Patron** : relier les conséquences issues des dossiers/prix/capacité aux engagements exacts et aux décisions humaines existantes. Ne pas exiger une analyse automatique exhaustive pour permettre une déclaration sourcée.
4. **L08 — réponse acheteur complète** : contenus substantiels, couverture des exigences et pièces réelles du ZIP; l’intégrité du paquet existant ne suffit pas à prouver son contenu métier. P5 exact/dépôt humain conservés.
5. **L09→L10→L11 — engagement vendu→passation→changement→sortie/REX** : compléter les écarts/actions/preuves dans les parcours natifs, selon les reports juridiques du cahier.

L01/L02/L03 et T01/T02/T03 sont des prérequis/garanties vérifiés dans ces scénarios, pas des campagnes horizontales remplaçant le code. L04 reçoit les corrections d’omission nécessaires aux scénarios; les challenges OCR/embeddings deviennent des sous-chantiers bornés, jamais la prochaine tranche principale par défaut.

## Première livraison — import financier complet borné

Entrée : Patron habilité, Affaire/brouillon exacts, classeur synthétique multi-feuilles. Sortie : toutes les lignes reconnues et leurs sources relues puis appliquées une fois au brouillon. Refus explicites pour structure non reconnue, formules non qualifiées, troncature, montant incohérent, source/tenant/rôle/révision discordants. Aucune conclusion de coût couvert ou de marge fiable déduite du seul import.

Plan minimal : régressions rouges sur deux onglets, formules et troncature; parser/contrats/persistance/source; parcours HTTP/PostgreSQL/retry/commit; affichage des sources dans le panneau existant via OpenDesign Local/Impeccable; revue/tests/scan; suivi et Basic Memory. Aucun ajout de dépendance ni activation de candidat.


## Passage L05 → L08 —24/10

Carte d’engagement et décision Patron qualifiées localement, limites conservées dans le plan et le dossier L05. La revue de `preparation/application/document_content.py` constate une trame avec contribution à rédiger : la suite porte sur les contenus humains sourcés, leurs exigences/pièces et leur revue dans les parcours natifs, pas sur un second moteur de paquet. Aucune autorisation P5, couverture complète ou dépôt déduit de la génération. Statut/next : plan seul.


## Passage L08 → L09 —24/10

Contributions humaines par exigence dans les brouillons natifs, sources/manques lisibles, revue et snapshot exacts qualifiés localement. Les cadres acheteur spécifiques et la couverture complète restent PARTIAL; ne pas transformer ce report en campagne horizontale obligatoire avant la fonction suivante. Suite : rapprochement offre vendue/contrat attribué/passation conducteur, selon le plan et les reports PF31-09. Aucun effet juridique ou réception externe déduit.


### Preuve locale L09 —25/10/2026

Parcours natif offre P5/contrat déclaré/revue Patron/passation/reçu Responsable qualifié en Python/API/UI : backend 3964 passed, 1 warning in 1519.68s (0:25:19),Web668/4ignorés,25contrôles Chromium synthétiques. Sources/retraits/refus/UNKNOWN préservés;34SHA stables, migration0143 et cleanup vérifiés. Général PARTIAL : pas de contrat/signature/réception externe/effet juridique ou couverture complète déduits; dette mypy des tests hors L09 ouverte, CI non qualifiée. [Dossier](../05_Qualification_locale/L09_OFFRE_CONTRAT_PASSATION_2026-10-25.md). Le plan global conserve seul statut et suite L10.


### Preuve locale L10 —25/10/2026

Changement/pointsL09/delta/action/responsable/preuveC5exacte, lecturefiltréeResponsable et requalification/historique qualifiés localement : backend 3983 passed, 1 warning in 2342.53s (0:39:02);Web672/4ignorés et10scénarios Chromium/47assertions.31SHAstables,migration0144 etcleanupvérifiés. GénéralPARTIAL : impactsquantifiésC3sur sourcesA1privées, pasd’acteexterne/effetjuridique/complétude déduits. CIentière nonqualifiée(dette206diagnosticsmypytests horsL10). [Dossier](../05_Qualification_locale/L10_CHANGEMENTS_EXECUTION_2026-10-25.md). StatutetsuiteL11uniquementdansleplan.
