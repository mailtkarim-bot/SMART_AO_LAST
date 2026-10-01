# SMART AO — Product Freeze v3.1

**Statut : AUTORITÉ PRODUIT/MÉTIER ACTIVE — 30 septembre 2026.**
**Promotion :** orientation et rédaction déléguées explicitement par le propriétaire à Codex le 30 septembre 2026. Cette promotion documentaire ne vaut ni recette logicielle ni autorisation publique.

La v3.1 consolide les candidats v3.0 transmis et ajoute la personnalisation gouvernée demandée par le propriétaire. Elle remplace la v2.0 comme autorité actuelle. Elle ne prétend pas que ces capacités sont déjà toutes implémentées. Le [Master métier](SMART_AO_CAHIER_DIRECTEUR_METIER_MASTER_v3.1.md) détaille les parcours et recettes ; le [cahier technique](SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v3.1.md) en dérive l'exécution.


## CONSOLIDATION V3.1 — lecture intégrale et arbitrages de compatibilité

Le cahier actif comprend le cadrage V3.1 et les chapitres détaillés intégrés ci-dessous. **Périmètre cible complet ≠ première livraison ≠ code qualifié.** Les exigences différées restent écrites et applicables à leur future tranche ; les capacités existantes et leurs protections restent maintenues.

| Sujet | Disposition actuelle applicable à tous les chapitres |
|---|---|
| Autorité et références historiques | Freeze v3.1 actif ; mentions v0.4/v1/v2/candidat et anciennes injonctions de promotion dans le contenu intégré sont provenance, pas nouvelle demande d'approbation |
| Priorité de construction | A avant engagement, B passation, C événement/changement ; les anciens T0–T8 et priorités horizontales ne supplantent pas le plan global actif |
| Engagement Control / Payment | Modèle logique transversal ; aucun déplacement de contexte, nouvelle façade ou table de graphe obligatoire sans audit/ADR/consumer et preuve de tranche |
| Règles, sanctions, échéances, DGD et cash | Contrats cibles conservés en détail ; calcul/automatisation soumis aux validations et faits applicables ; UNKNOWN si non établis, aucun effet juridique certain par LLM |
| Assurance, HSE, environnement, MIRP, portefeuille | Exigences conservées et détaillées, pas supprimées ; réalisation/qualification ultérieure explicitement distincte d'une promesse initiale |
| Personnalisation | Exigences PF31-05/M31-06/CT31-05 ajoutées à l'ensemble du périmètre ; profils versionnés et snapshots, sécurité/portes/confidentialité non paramétrables à la baisse |
| Couverture UX | Catalogue et fondations conservés ; les surfaces dérivent de ces contrats, aucun écran déclaré livré par sa présence dans le cahier |
| Observations concurrentielles anciennes | Matériau stratégique daté et non benchmark produit ; pas d'exclusivité ni supériorité déduite |
| Déploiement et preuve | NO-GO public ; toute ancienne validation ou baseline se rapporte à sa date/snapshot, pas au checkout actuel |

**AS-IS :** les précédents cahiers actifs courts perdaient l'accès direct à une partie de la profondeur requise. **Risques :** omission métier, doubles autorités et choix techniques interprétés comme livrés. **Insertion :** intégration des chapitres complets dans les trois cahiers existants avec identifiants uniques et contrôle de couverture. **Plan minimal :** conserver les corps de texte, expliciter les arbitrages ci-dessus, puis vérifier origine, présence, liens, autorité et plan. **Tests :** conservation de chaque ligne non-titre et chaque chapitre, absence de doublon d'ancre, autorité unique ; aucune gate production dans ce bloc documentaire.


## PF31-01 — Produit et client

SmartAO est un **système de maîtrise des engagements d'une Affaire BTP** : avant l'offre, comprendre ce qui sera vendu ; après attribution, transmettre ce qui a été accepté ; face à un changement, retrouver les conséquences, actions et preuves à examiner.

Client initial : PME française de travaux, prioritairement 10–100 personnes, marchés publics en premier. Les marchés privés restent modélisables mais ne bénéficient pas d'une promesse juridique ou d'un corpus qualifié implicite. Le premier profil chantier est la réhabilitation en site occupé, avec interfaces de lots et partenaires : choix de concentration, non exclusivité commerciale. Sa pertinence devra être éprouvée sur des dossiers et avec des utilisateurs.

L'Affaire reste l'unité centrale, avec consultations, lots, documents et versions, décisions, partenaires et événements. L'IA aide à préparer et retrouver ; une chaîne manuelle complète doit fonctionner sans LLM.

## PF31-02 — Différenciation à démontrer

La promesse n'est pas « nous seuls analysons les CCAP » ou « les concurrents sont rigides ». Les annonces publiques montrent déjà analyse contractuelle et personnalisation. Notre hypothèse de différence est la **continuité vérifiable de l'engagement**, avec des méthodes d'entreprise configurables et historisées.

Une question concrète doit devenir traitable : « L'accès restreint était connu avant GO ; qu'avons-nous chiffré ou exclu, qui l'a accepté, et que change la nouvelle instruction pour nos prestations, nos partenaires et les preuves à produire ? »

Les douleurs prioritaires sont : limites de prestations mal raccordées aux devis ; conditions de GO perdues lors de la passation ; changements non rapprochés de ce qui a été vendu ; travail réalisé sans preuve exploitable ; paiement attendu confondu avec paiement constaté ; réserves et coûts de sortie oubliés. Leur fréquence et la disposition à payer restent à valider, sans affirmer qu'aucun concurrent ne les traite.

## PF31-03 — Chaîne fonctionnelle obligatoire

```text
Source/version → constat → applicabilité humaine → obligation/droit/inconnu
→ impact déclaré et hypothèses → décision/condition Patron
→ engagement de l'offre et paquet exact → contrat attribué identifié
→ événement réel → revue des conséquences → action/preuve → réception/sortie → REX
```

Chaque lien expose son origine, sa version, son auteur, sa date et sa justification. Un lien non établi est absent ou UNKNOWN ; il n'est pas généré comme vérité par l'IA. DCE candidat, offre déposée et contrat signé sont trois sources distinctes. Un avenant déclaré remplaçant une version entraîne une requalification explicite, jamais une réécriture d'historique.

## PF31-04 — Trois verticales, dans cet ordre

| Verticale | Sortie utilisable | Première borne de livraison |
|---|---|---|
| A — Avant de s'engager | Carte Patron reliant clause, périmètre, coût/cash/délai/capacité et condition P3 | Un engagement critique sourcé, applicability humaine, impact déclaré, condition P3 reliée ; refus/UNKNOWN visibles |
| B — Si nous gagnons | Dossier conducteur de ce qui a été vendu et accepté | Version attribuée, écarts contre offre, conditions reprises, responsables et preuves attendues ; P7 séparé de l'OS |
| C — Quelque chose change | Revue d'une instruction/avenant et de ses conséquences | Événement sourcé, version visée, engagement concerné, impact révisé et action humaine ; aucun droit acquis présumé |

Le premier scénario traverse un dossier local borné : contrainte de site occupé → exclusion/transport d'un partenaire → hypothèse de coût → condition Patron → passation → changement d'accès → action et preuve. Les verticales livrent des parcours React/API/PostgreSQL complets, pas une succession de reçus sans résultat métier.

## PF31-05 — Personnalisation gouvernée

Une entreprise doit pouvoir adapter son vocabulaire, ses listes de contrôle, ses types d'impacts, ses modèles d'actions/preuves, ses seuils internes de vigilance et ses vues. Un pack métier fournit des valeurs de départ ; il ne devient pas une obligation réglementaire par son nom.

Les paramètres métier publiés sont versionnés et rattachés à l'Affaire par un snapshot immuable. Une nouvelle version ne modifie pas silencieusement une décision passée ; son adoption par une Affaire en cours exige aperçu des différences et acte explicite. Les préférences purement visuelles peuvent changer sans changer la configuration métier.

**Non personnalisables :** isolation tenant, permissions minimales, MFA/step-up applicables, confidentialité, append-only, idempotence, invariants B0/B1/B2 et P0–P7, état UNKNOWN, nécessité de preuve et séparation déclaration/conclusion juridique. Aucune configuration ne donne un pouvoir de Patron à un Collaborateur, ne masque un blocage obligatoire ou ne déclenche un GO.

Première capacité : un petit profil entreprise versionné de checklist/termes/actions, éditable par le Patron habilité et prévisualisable sur une Affaire. Pas de constructeur universel de workflows, code utilisateur, fork par client ou moteur générique de règles en première livraison.

## PF31-06 — Carte d'Engagement et rôles

Les douze axes restent couverts : intérêt commercial ; candidature ; technique ; constructibilité/logistique ; contrat ; prix/marge ; cash/garanties ; capacité ; partenaires ; HSE/environnement/réglementation ; obligations documentaires/engagements vendus ; droits/réception/sortie.

Chaque point critique montre fait/source, version/localisateur, applicabilité, connu/inconnu, conséquence, responsable, action, date déclarée ou non calculable, preuve et décision. Aucun score global ne remplace cette lecture.

Patron : arbitrages économiques et actes autorisés par la politique serveur. Collaborateur/Responsable : préparation et exécution dans ses droits existants. Expert : avis sourcé, pas pouvoir induit. Propriété organisationnelle et rôle Patron restent distincts. Support : aucune récupération ou consultation privée implicite.

FINANCIAL_PRIVATE et PERSONAL_DATA sont protégés jusque dans compteurs, relations, recherche, RAG, exports, erreurs et logs. Une conséquence privée ne doit pas être déduite depuis une projection publique du graphe.

## PF31-07 — Portes et états conservés

P0 cibler ; P1 ouvrir ; P2 GO de principe ; P3 GO économique ; P4 autoriser l'offre ; P5 autoriser le paquet exact ; P6 accepter une clarification/négociation/mise au point ; P7 lancer l'exécution selon les contrats existants. Aucun profil configurable ne contourne une porte.

P5 reste lié au manifeste/hash et à la version exacte autorisée. Dépôt humain, reçu externe et résultat inconnu restent distincts. P7 n'est pas un ordre de service. B0/B1/B2 conservent leurs définitions et contrôles existants ; aucun renommage ou assouplissement n'est autorisé ici.

UNKNOWN, PARTIAL, REVIEW_REQUIRED, SUPERSEDED et indisponibilité restent visibles. Un retry conserve la même intention ; succès affiché uniquement après réponse ou relecture serveur confirmée. Nouvel événement et correction sont append-only.

## PF31-08 — Économie et droits

Impacts coût, cash, délai et capacité sont d'abord **déclarations sourcées**, avec unités, devise si applicable, hypothèses, périmètre et niveau de revue. Une somme partielle ne devient pas coût couvert. Un devis partenaire ne prouve ni engagement, ni comparabilité, ni couverture du prix. Aucun classement automatique ni promotion P3.

Situation/facture, réception d'une pièce, paiement attendu et encaissement constaté sont des faits distincts. Cash prévu n'est pas cash certain. Réception avec/sous/sans réserves, levée, DGD et sortie contractuelle ne sont pas fusionnés.

Une échéance juridique ne peut être calculée qu'avec régime applicable, règle versionnée validée pour son périmètre, fait déclencheur et données calendaires nécessaires. Sinon : date déclarée clairement identifiée ou NOT_COMPUTABLE/UNKNOWN. Aucune application universelle d'un délai CCAG, aucun calcul automatique de forclusion/DGD tacite, aucune conclusion juridique par LLM.

## PF31-09 — Périmètre et reports explicites

| Politique | Contenu |
|---|---|
| Maintenir le socle | Identité/entreprise, DCE/OCR/provenance, exigences/contradictions, prix importés, production d'offre, dépôt humain, P0–P7 et REX existants ; corriger les blocages sans course horizontale |
| Investir maintenant | Relations source/version → engagement/impact/condition ; passation et événement réel ; personnalisation métier versionnée ; preuves de bout en bout |
| Différer sans supprimer l'exigence | Moteur juridique/calendaire validé, sanctions quantitatives, règlement/DGD structuré, cash portefeuille, assurance/HSE automatisés, MIRP avancé, extension multi-métiers/private corpus |
| Hors première promesse | ERP/comptabilité/paie, métré universel, plateforme no-code, dépôt autonome, scraping privé, graph DB, rewrite Rust et microservices |

Les exigences et recettes v2 sont **intégralement intégrées ci-dessous dans les chapitres PF2**, notamment le détail des §9–18 et REC-29–45. La copie archivée sert uniquement à la provenance. Elles n'ont pas une seconde autorité : la présente politique de priorité/report prévaut. Les recettes historiques G01–G52 restent des contraintes de régression applicables ; elles ne sont pas toutes revendiquées exécutées au checkout actuel.

Le catalogue UX v0.3 et ses 104 identifiants restent la carte de couverture. Ils ne forcent pas 104 nouvelles livraisons avant validation d'une verticale. Les surfaces C07/C08/C09/C12/C13 existantes sont réutilisées ; toute nouvelle surface de personnalisation est dérivée par contrat UX avant implémentation.

## PF31-10 — Qualification et évolution

Une verticale ferme seulement avec chemin web → API → PostgreSQL, refus rôle/tenant, rejeu/interruption, données obsolètes, preuve consultable et absence de fuite. Les critères quantifiés et le protocole du Master métier sont obligatoires avant promesse de supériorité. La configuration et le corpus utilisés font partie de la preuve.

Veille concurrentielle avant chaque grande phase, sans automatisation hebdomadaire prétendue installée. Différenciation commerciale encore hypothétique : entretiens de terrain et benchmark comparatif autorisé restent à faire. Hébergement/VPS, production publique et validations externes non réalisées restent ouverts. **NO-GO public maintenu.**

Le propriétaire délègue les arbitrages de conception courants ; ils sont documentés avec limites. Cela ne permet pas d'inventer une validation client/juriste, une preuve de test ou une décision Patron dans les données métier. Toute évolution des droits, invariants ou promesses réclame une révision explicite de ce Freeze et les preuves correspondantes.


## Contrats produit complets conservés — PF2

Ces chapitres font partie du présent cahier actif : **il n'est pas nécessaire d'ouvrir les archives pour disposer de ce détail**. Les identifiants PF2-xxx donnent des ancres uniques. Les exigences métier/techniques sont conservées ; les titres, dates, mentions de promotion et références de version du texte intégré indiquent sa provenance. Ils ne rétablissent pas une ancienne autorité. Les dispositions de consolidation V3.1 en tête gouvernent les conflits et l'ordre de livraison. « À valider », candidat, validation externe ou report ne signifient jamais capacité livrée.

### Accès aux chapitres intégrés

- [PF2-001 — SMART AO — Cahier directeur Produit & Métier](#pf2-001)
- [PF2-002 — OWNER FREEZE v2.0 — AUTORITÉ PRODUIT/MÉTIER ACTIVE](#pf2-002)
- [PF2-003 — 0. Objet de la réouverture](#pf2-003)
- [PF2-004 — 1. Vision, promesse et client initial](#pf2-004)
- [PF2-005 — 1.1 Question fondamentale — FIGÉE v2.0](#pf2-005)
- [PF2-006 — 1.2 Positionnement produit — FIGÉ v2.0](#pf2-006)
- [PF2-007 — 1.3 Client initial — HÉRITÉ / MAINTENU](#pf2-007)
- [PF2-008 — 2. Doctrine produit non négociable](#pf2-008)
- [PF2-009 — 3. Autorité, rôles et confidentialité](#pf2-009)
- [PF2-010 — 3.1 Patron](#pf2-010)
- [PF2-011 — 3.2 Collaborateur / Responsable](#pf2-011)
- [PF2-012 — 3.3 Experts](#pf2-012)
- [PF2-013 — 3.4 Administrateur / Support / Tiers](#pf2-013)
- [PF2-014 — 3.5 Contrat d’une décision critique](#pf2-014)
- [PF2-015 — 4. Objets métier de premier rang](#pf2-015)
- [PF2-016 — 4.1 Objets historiques maintenus](#pf2-016)
- [PF2-017 — 4.2 Nouveaux contrats produit v2.0](#pf2-017)
- [PF2-033 — 5. Cycle P0–P7 — portes maintenues, critères enrichis](#pf2-033)
- [PF2-034 — P0 — Cibler](#pf2-034)
- [PF2-035 — P1 — Ouvrir](#pf2-035)
- [PF2-036 — P2 — GO de principe](#pf2-036)
- [PF2-037 — P3 — GO économique](#pf2-037)
- [PF2-038 — P4 — Autoriser l’offre](#pf2-038)
- [PF2-039 — P5 — Autoriser le dépôt](#pf2-039)
- [PF2-040 — P6 — Accepter clarification/négociation/mise au point](#pf2-040)
- [PF2-041 — P7 — Lancer l’exécution](#pf2-041)
- [PF2-042 — 6. Carte d’Engagement de l’Affaire — sortie Patron centrale](#pf2-042)
- [PF2-043 — 6.1 Douze axes obligatoires](#pf2-043)
- [PF2-044 — 6.2 Anatomie d’une ligne](#pf2-044)
- [PF2-045 — 6.3 Interdiction du score opaque](#pf2-045)
- [PF2-046 — 6.4 GO sous conditions](#pf2-046)
- [PF2-047 — 7. DCE, documents, preuves et rectificatifs](#pf2-047)
- [PF2-048 — 8. Applicabilité réglementaire et veille](#pf2-048)
- [PF2-049 — 9. Analyse technique, MIRP, constructibilité et interfaces](#pf2-049)
- [PF2-050 — 9.1 Traduction chantier](#pf2-050)
- [PF2-051 — 9.2 MIRP](#pf2-051)
- [PF2-052 — 9.3 Interfaces](#pf2-052)
- [PF2-053 — 9.4 Constructibilité](#pf2-053)
- [PF2-054 — 10. Économie, prix, cash et capacité](#pf2-054)
- [PF2-055 — 10.1 Quatre vues économiques](#pf2-055)
- [PF2-056 — 10.2 Prix et révision](#pf2-056)
- [PF2-057 — 10.3 Capacité](#pf2-057)
- [PF2-058 — 10.4 Portefeuille](#pf2-058)
- [PF2-059 — 11. Partenaires, sous-traitance et groupements](#pf2-059)
- [PF2-060 — 12. Contrat applicable, dérogations et exposition](#pf2-060)
- [PF2-061 — 12.1 Reconstruire le contrat](#pf2-061)
- [PF2-062 — 12.2 Dérogations](#pf2-062)
- [PF2-063 — 12.3 Pénalités et sanctions](#pf2-063)
- [PF2-064 — 12.4 Préservation des droits](#pf2-064)
- [PF2-065 — 12.5 OS / modifications / travaux supplémentaires](#pf2-065)
- [PF2-066 — 12.6 Résiliation / substitution](#pf2-066)
- [PF2-067 — 12.7 Réception / règlement / DGD](#pf2-067)
- [PF2-068 — 13. Assurance, HSE, environnement et obligations mesurables](#pf2-068)
- [PF2-069 — 13.1 Assurance](#pf2-069)
- [PF2-070 — 13.2 HSE / prérequis d'exécution](#pf2-070)
- [PF2-071 — 13.3 Environnement et social](#pf2-071)
- [PF2-072 — 13.4 Déchets / PEMD / REP](#pf2-072)
- [PF2-073 — 14. Production de l'offre et registre des engagements](#pf2-073)
- [PF2-074 — 15. Remise, dépôt et preuve](#pf2-074)
- [PF2-075 — 16. Paiement, trésorerie d'exécution et post-réception](#pf2-075)
- [PF2-076 — 16.1 Circuit de paiement](#pf2-076)
- [PF2-077 — 16.2 Post-réception](#pf2-077)
- [PF2-078 — 17. Clarification, négociation, résultat et passation](#pf2-078)
- [PF2-079 — 17.1 P6](#pf2-079)
- [PF2-080 — 17.2 Attribution / rejet](#pf2-080)
- [PF2-081 — 17.3 P7 / dossier de passation obligatoire](#pf2-081)
- [PF2-082 — 18. Retour d'expérience](#pf2-082)
- [PF2-083 — 19. UX et surfaces — impact du v2.0](#pf2-083)
- [PF2-084 — 20. IA, provenance et abstention](#pf2-084)
- [PF2-085 — 21. Périmètre V1 v2.0](#pf2-085)
- [PF2-086 — 21.1 Indispensable V1](#pf2-086)
- [PF2-087 — 21.2 V1.x / qualification ultérieure](#pf2-087)
- [PF2-088 — 21.3 Hors promesse sans qualification](#pf2-088)
- [PF2-089 — 22. Validations externes obligatoires](#pf2-089)
- [PF2-090 — 23. Recettes métier obligatoires du v2.0](#pf2-090)
- [PF2-091 — 24. Critères de qualification métier](#pf2-091)
- [PF2-092 — 25. Contrat de changement et traçabilité](#pf2-092)
- [PF2-093 — 26. Règle de dérivation vers Codex](#pf2-093)
- [PF2-094 — 27. Références normatives après promotion](#pf2-094)
- [PF2-095 — 28. Promotion](#pf2-095)

<!-- BEGIN INTEGRATION-PF2 -->
<a id="pf2-001"></a>
### PF2-001 — SMART AO — Cahier directeur Produit & Métier
<a id="pf2-002"></a>
#### PF2-002 — OWNER FREEZE v2.0 — AUTORITÉ PRODUIT/MÉTIER ACTIVE

**Date :** 24 septembre 2026  
**Statut :** PRODUCT FREEZE v2.0 — PROMU PAR LE PROPRIÉTAIRE LE 24 SEPTEMBRE 2026  
**Remplace :** `../_ARCHIVE/produit_metier/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md`  
**Source métier principale :** `SMART_AO_CAHIER_DIRECTEUR_METIER_MASTER_v2.0.md`  
**Question couverte :** « Quel SmartAO voulons-nous construire et quelles vérités métier doit-il être capable de prouver sans les simplifier ? »

> **RÈGLE D’AUTORITÉ.** Le propriétaire a explicitement promu ce document le 24 septembre 2026. Il est l’autorité produit/métier active. Le Product Freeze v1.0 est historique et archivé. Le cahier technique et le code doivent dériver de ce v2.0 ; aucun comportement historique ne peut le contredire silencieusement.

---

<a id="pf2-003"></a>
#### PF2-003 — 0. Objet de la réouverture

Le Product Freeze v1.0 a correctement fixé les fondamentaux : Affaire, Mémoire Entreprise, source/version/preuve, séparation Patron/Collaborateur, P0–P7, confidentialité, dépôt humain, IA non autoritaire, états `UNKNOWN/PARTIAL/REVIEW_REQUIRED`, idempotence et continuité.

Le MASTER métier v2.0 a cependant démontré que plusieurs risques essentiels étaient trop compressés pour constituer des obligations produit explicites : dérogations, sanctions, préservation des droits, ordres de service, règlement des comptes/DGD, résiliation, assurance réelle, HSE capacitaire, engagements mesurables, réglementation applicable et circuit de paiement.

La réouverture v2.0 poursuit un objectif unique :

> **empêcher qu’une simplification produit fasse disparaître un risque métier capable de consommer la marge, la trésorerie ou un droit contractuel de l’entreprise.**

Le v2.0 ne transforme pas SmartAO en ERP chantier, cabinet juridique, logiciel de chiffrage complet ou moteur de conformité automatique.

---

<a id="pf2-004"></a>
### PF2-004 — 1. Vision, promesse et client initial

<a id="pf2-005"></a>
#### PF2-005 — 1.1 Question fondamentale — FIGÉE v2.0

SMART AO doit aider le dirigeant à répondre de manière défendable à la question :

> **Cette affaire mérite-t-elle notre effort commercial, pouvons-nous la gagner, la financer, l’exécuter correctement, protéger nos droits et conserver la marge prévue ?**

« Protéger nos droits » signifie que le produit doit rendre visibles, sourcés et transmissibles les événements, délais, formalismes, preuves et décisions qui conditionnent la capacité de l’entreprise à défendre un paiement, une prolongation, une réserve, une réclamation ou une clôture contractuelle. SmartAO ne délivre pas seul un avis juridique.

<a id="pf2-006"></a>
#### PF2-006 — 1.2 Positionnement produit — FIGÉ v2.0

SMART AO est :

> **un poste de commandement d’ingénierie DCE et de décision d’engagement pour PME BTP, centré sur l’Affaire, la preuve, l’applicabilité, l’impact chantier, la décision humaine, la protection de la marge et la préservation des droits.**

SMART AO n’est pas : chatbot documentaire, générateur générique de mémoire, ERP chantier, logiciel qui fixe seul le prix, avocat automatique, moteur de conformité universelle, simple GED ou score opaque de GO/NO-GO.

<a id="pf2-007"></a>
#### PF2-007 — 1.3 Client initial — HÉRITÉ / MAINTENU

- cœur de cible : PME BTP françaises de 10 à 100 personnes ;
- qualification terrain avec au moins un pilote multi-métiers/entreprise générale et un pilote spécialisé technique ;
- public et privé sont natifs dans le modèle ;
- la promesse V1 est qualifiée d’abord sur la commande publique ;
- le privé reste borné tant qu’un corpus privé diversifié n’a pas été validé.

---

<a id="pf2-008"></a>
### PF2-008 — 2. Doctrine produit non négociable

1. L’Affaire reste l’unité de décision et de preuve.
2. La Mémoire Entreprise reste le patrimoine privé gouverné de l’entreprise.
3. Toute conclusion critique garde sa source, sa version et son locator/hash lorsque disponible.
4. Une absence de preuve ne devient jamais conformité, zéro, absence de coût ou absence de risque.
5. Une rectification invalide les conclusions dépendantes sans effacer l’historique.
6. Un score ne décide jamais d’une porte P0–P7.
7. Une règle générale n’est jamais appliquée à l’affaire sans preuve d’applicabilité.
8. Une règle contractuelle particulière peut modifier ou neutraliser une règle de référence ; la dérogation doit être visible.
9. Une règle juridique, assurantielle ou HSE incertaine provoque `REVIEW_REQUIRED`, pas une conclusion générée.
10. Les calculs contractuels et financiers critiques sont déterministes, reproductibles et sourcés ; le LLM ne calcule pas l’autorité finale.
11. Le Collaborateur ne reçoit ni marge, ni prix d’achat confidentiel, ni cash Direction, ni notes privées Patron par UI, API, recherche, export, notification ou contexte IA.
12. L’IA observe, extrait, rapproche, explique et propose ; elle ne décide ni GO, ni prix final, ni couverture assurantielle, ni conformité juridique, ni recours, ni dépôt.
13. Les documents externes sont des données non fiables ; leur contenu ne peut élargir droits, outils ou instructions système.
14. Une panne IA ou source conserve un chemin manuel visible.
15. Le dépôt final externe reste humain en V1.
16. SmartAO ne devient pas un ERP chantier ; il doit toutefois représenter assez de conséquences chantier pour sécuriser la décision d’engagement et la passation.

---

<a id="pf2-009"></a>
### PF2-009 — 3. Autorité, rôles et confidentialité

<a id="pf2-010"></a>
#### PF2-010 — 3.1 Patron

Le Patron : décide P0–P7 selon habilitation ; contrôle prix, marge, trésorerie et exposition ; accepte les hypothèses critiques ; arbitre dérogations et risques contractuels ; approuve garanties, solidarités et engagements sensibles ; décide les escalades juridiques/assurantielles/DAF/QSE ; autorise P4/P5 et la passation selon politique.

<a id="pf2-011"></a>
#### PF2-011 — 3.2 Collaborateur / Responsable

Il prépare, contrôle, documente, consulte, coordonne et remonte les inconnus. Il ne devient jamais Patron par accumulation d’informations ou de tâches. Il peut voir un impact non financier utile à son travail sans recevoir la vérité économique Direction correspondante.

<a id="pf2-012"></a>
#### PF2-012 — 3.3 Experts

Métreur, conducteur, QSE, DAF, administratif, achats, juriste, courtier/assureur et autres experts contribuent uniquement dans leur périmètre. Une validation experte et une décision Patron restent deux actes distincts.

<a id="pf2-013"></a>
#### PF2-013 — 3.4 Administrateur / Support / Tiers

Administration technique ≠ autorité métier. Le support n’acquiert jamais implicitement l’accès au contenu métier. Un tiers externe reçoit un paquet borné en objet, durée, données et action.

<a id="pf2-014"></a>
#### PF2-014 — 3.5 Contrat d’une décision critique

Toute décision critique porte : auteur, rôle, organisation/tenant, Affaire/lot/phase/tour, date, version, faits/preuves consultés, inconnus, conditions, éventuelle expiration, motif et règle de réouverture.

---

<a id="pf2-015"></a>
### PF2-015 — 4. Objets métier de premier rang

Les objets suivants sont désormais normatifs au niveau produit. Le cahier technique choisit leur représentation logicielle exacte ; il ne peut les supprimer par regroupement générique.

<a id="pf2-016"></a>
#### PF2-016 — 4.1 Objets historiques maintenus

`Affaire`, `DCE/DocumentVersion`, `Source/SourceAnchor`, `Evidence`, `Requirement`, `Unknown`, `Hypothesis`, `Contradiction`, `Risk`, `Decision`, `Condition`, `Task`, `Partner`, `PricingScenario`, `Commitment`, `CandidatePackage`, `Manifest`, `SubmissionEvidence`, `Result`, `Handover`, `REX`, éléments de Mémoire Entreprise.

<a id="pf2-017"></a>
#### PF2-017 — 4.2 Nouveaux contrats produit v2.0

<a id="pf2-018"></a>
##### PF2-018 — A. Carte d’Engagement de l’Affaire
Projection Patron centrale, composée de douze axes ; ce n’est ni un score ni une nouvelle source de vérité.

<a id="pf2-019"></a>
##### PF2-019 — B. `REGULATORY_PROFILE`
Profil de faits validés permettant de qualifier l’applicabilité de règles versionnées : public/privé, ouvrage, usage, date, montant, site, travaux, acteurs, diagnostics et autres faits nécessaires.

<a id="pf2-020"></a>
##### PF2-020 — C. Règle réglementaire vivante
Chaque règle porte source d’autorité, publication, dates d’effet/fin, champ, exceptions, faits requis, statut `ACTIVE/FUTURE/EXPIRED/UNKNOWN_APPLICABILITY/REVIEW_REQUIRED`, validation et date de revue.

<a id="pf2-021"></a>
##### PF2-021 — D. Baseline contractuelle et dérogation
Le produit doit représenter la règle de référence réellement incorporée au contrat, sa version, la clause particulière qui la modifie et l’impact métier résultant. Une simple étiquette « CCAG Travaux » ne suffit pas.

<a id="pf2-022"></a>
##### PF2-022 — E. `CONTRACTUAL_SANCTION`
Sanction/pénalité avec source, déclencheur, unité, formule, base, franchise, plafond, cumul, procédure, dérogation, exonération potentielle, responsable et scénarios d’exposition.

<a id="pf2-023"></a>
##### PF2-023 — F. `RIGHT_PRESERVATION_EVENT`
Événement de préservation d’un droit : trigger, source/version, règle de délai, échéance, destinataire, forme, contenu minimal, preuve d’envoi/réception, responsable, statut et conséquence potentielle.

<a id="pf2-024"></a>
##### PF2-024 — G. Modification / ordre de service
Objet représentant prescription, forme, réception, obligation d’exécuter selon cadre, réserves, délai de réaction, prix/provisoire/nouveau, effet planning et preuve.

<a id="pf2-025"></a>
##### PF2-025 — H. Règlement des comptes / réception / DGD
Séquence sourcée reliant OPR, réception, réserves, décompte final/général, DGD, garanties et échéances. Le produit n’invente jamais un DGD tacite sans toutes les conditions prouvées.

<a id="pf2-026"></a>
##### PF2-026 — I. Exposition de résiliation / substitution
Cas de rupture, remède, mise en demeure, exécution aux frais et risques, marché de substitution, liquidation et conséquences ; sortie = stress de risque, pas avis juridique.

<a id="pf2-027"></a>
##### PF2-027 — J. Évaluation assurance/prestation
Lien entre prestation promise, activité déclarée, technique, ouvrage, période, territoire, exclusions et preuve. États minimaux : `COVERED`, `PROBABLY_COVERED`, `NOT_ESTABLISHED`, `OUTSIDE_DECLARED_ACTIVITY`, `BROKER_REVIEW_REQUIRED`.

<a id="pf2-028"></a>
##### PF2-028 — K. Prérequis d’exécution
Obligation HSE/technique/autorisation traduite en document, compétence, personne, matériel, délai d’obtention, coût, planning, preuve et responsable.

<a id="pf2-029"></a>
##### PF2-029 — L. Engagement mesurable
Promesse sensible de l’offre avec KPI/valeur, méthode de mesure, période, preuve, coût, ressource, responsable, partenaire/cascade, reporting et conséquence potentielle.

<a id="pf2-030"></a>
##### PF2-030 — M. Circuit de paiement
Chaîne production → situation → contrôle/service fait → MOA/plateforme/payeur → encaissement, avec documents, rejets/suspensions, dates et hypothèses prudentes.

<a id="pf2-031"></a>
##### PF2-031 — N. Obligation post-réception
OPR, essais, mise en service, DOE/DIUO, levée de réserves, GPA, stock, maintenance initiale, astreinte, garantie, clôture et coût associé.

<a id="pf2-032"></a>
##### PF2-032 — O. Dépendance tierce
Autorisation, coupure, voirie, concessionnaire, grutage, badge, accès, consignation, autorité externe ou autre condition pouvant rendre le planning impossible.

---

<a id="pf2-033"></a>
### PF2-033 — 5. Cycle P0–P7 — portes maintenues, critères enrichis

Aucune nouvelle porte n’est créée. Les portes restent distinctes et toute condition critique non levée peut rouvrir la porte correspondante.

<a id="pf2-034"></a>
#### PF2-034 — P0 — Cibler

Décider si une opportunité mérite une action commerciale. Prendre en compte : métier/zone, horizon, intérêt stratégique, coût d’approche, légalité/éthique de l’intelligence commerciale, données sourcées et inconnus.

<a id="pf2-035"></a>
#### PF2-035 — P1 — Ouvrir

Le DCE/invitation est reçu avec périmètre, échéance et source. Une incompatibilité immédiate, pièce critique absente ou impossibilité manifeste reste visible ; un dossier partiellement lisible ne devient pas « analysé ».

<a id="pf2-036"></a>
#### PF2-036 — P2 — GO de principe

Examiner au minimum : éligibilité, candidature, capacités, charge d’étude, partenaires essentiels, MIRP initial, profil réglementaire, assurance de principe, constructibilité rédhibitoire, dépendances tierces et régime contractuel applicable.

<a id="pf2-037"></a>
#### PF2-037 — P3 — GO économique

Examiner au minimum : marge, cash, garanties/financement, clause de prix/révision, exposition fournisseurs, charge/capacité, pénalités identifiables, risques de résiliation/substitution, HSE/réglementaire coûteux, coût post-réception et scénarios de portefeuille lorsqu’applicables.

<a id="pf2-038"></a>
#### PF2-038 — P4 — Autoriser l’offre

Vérifier cohérence prix/technique/planning, documents, preuves, engagements mesurables, ressources promises, assurances sensibles, dérogations acceptées, environnement/social, conditions ouvertes et toute promesse pouvant devenir obligation de chantier.

<a id="pf2-039"></a>
#### PF2-039 — P5 — Autoriser le dépôt

Maintenir séparation stricte : candidate → contrôles/signatures → autorisation P5 → export → dépôt humain → preuve externe. Toute modification du paquet après autorisation invalide P5 selon dépendances.

<a id="pf2-040"></a>
#### PF2-040 — P6 — Accepter clarification/négociation/mise au point

Toute modification pertinente déclenche revalidation ciblée : prix, marge, cash, capacité, assurance, engagement, pénalité, règle contractuelle, profil réglementaire, partenaire, délai et droits.

<a id="pf2-041"></a>
#### PF2-041 — P7 — Lancer l’exécution

P7 exige une passation formelle comprenant le contrat vendu et les mécanismes nécessaires pour protéger son économie : conditions du GO, risques résiduels, engagements, partenaires, pénalités, paiement, assurances, HSE, documents post-attribution et calendrier de préservation des droits. **P7 n’est pas un ordre de service ni une autorisation juridique de démarrer les travaux.**

---

<a id="pf2-042"></a>
### PF2-042 — 6. Carte d’Engagement de l’Affaire — sortie Patron centrale

La Carte d’Engagement doit permettre au Patron de comprendre en quelques minutes non seulement « faut-il y aller ? » mais « si j’y vais, comment dois-je y aller ? ».

<a id="pf2-043"></a>
#### PF2-043 — 6.1 Douze axes obligatoires

1. intérêt commercial ;
2. éligibilité/candidature ;
3. périmètre technique ;
4. constructibilité/logistique ;
5. contrat et exposition ;
6. prix/marge/sensibilité ;
7. trésorerie/garanties/financement ;
8. capacité/charge/ressources ;
9. fournisseurs/sous-traitants/cotraitants ;
10. HSE/environnement/réglementation ;
11. obligations documentaires/engagements de l’offre ;
12. préservation des droits/réception/sortie du contrat.

<a id="pf2-044"></a>
#### PF2-044 — 6.2 Anatomie d’une ligne

Chaque point important doit pouvoir exposer : fait/source, version, locator, applicabilité, certitude/inconnu, conséquences technique/coût/délai/cash/contrat, responsable, action, échéance, preuve attendue, décision requise et risque résiduel.

<a id="pf2-045"></a>
#### PF2-045 — 6.3 Interdiction du score opaque

La Carte peut agréger et filtrer, mais elle ne réduit jamais la décision à une note globale. Un C1/B0/B1 critique ou un inconnu déterminant reste visible même si les autres axes sont favorables.

<a id="pf2-046"></a>
#### PF2-046 — 6.4 GO sous conditions

Chaque condition a propriétaire, échéance, preuve de levée, porte d’origine, criticité et règle de réouverture. « Acceptée par le Patron » ne transforme pas une impossibilité réglementaire ou un défaut de preuve non arbitrable en conformité.

---

<a id="pf2-047"></a>
### PF2-047 — 7. DCE, documents, preuves et rectificatifs

- inventorier archives, sous-archives et fichiers ;
- distinguer reçu, lisible, extrait, revu et couvert ;
- conserver original, hash, version, parser/méthode et locator ;
- signaler pièce annoncée mais absente ;
- conserver documents non supportés/illisibles comme trous de couverture ;
- conserver deux sources en contradiction ;
- une réponse acheteur ou un rectificatif crée une nouvelle version et une analyse d’impact ;
- invalider seulement les conclusions dépendantes ;
- un rectificatif touchant prix, délai, engagement, règle contractuelle ou paquet peut rouvrir P3/P4/P5/P7 ;
- aucun contenu externe n’est exécuté comme instruction.

---

<a id="pf2-048"></a>
### PF2-048 — 8. Applicabilité réglementaire et veille

SmartAO doit distinguer :

1. **fait d’affaire** : donnée sourcée sur le projet ;
2. **règle versionnée** : texte/référence et dates ;
3. **évaluation d’applicabilité** : pourquoi la règle semble applicable/non applicable/incertaine ;
4. **impact métier** : document, coût, délai, compétence, décision ;
5. **validation humaine** lorsque requise.

Une règle future reste `FUTURE`. Une règle expirée ne s’applique pas aux nouvelles affaires sauf raison sourcée. Une source réglementaire indisponible ne produit pas une conclusion à partir d’un cache non daté sans signalement.

Le moteur de règles n'est pas un avocat automatisé. Les sujets juridiques, assurance, HSE et privés sensibles peuvent exiger validation externe avant blocage automatique ou promesse commerciale.

---

<a id="pf2-049"></a>
### PF2-049 — 9. Analyse technique, MIRP, constructibilité et interfaces

<a id="pf2-050"></a>
#### PF2-050 — 9.1 Traduction chantier

Pour une prescription importante, le produit doit pouvoir relier :

`exigence → méthode → moyens → interfaces → séquence → contraintes → coût → délai → preuve → responsable`.

<a id="pf2-051"></a>
#### PF2-051 — 9.2 MIRP

La complétude du DCE et la complétude nécessaire à un prix défendable sont distinctes. Une information peut être non obligatoire au pli tout en étant critique pour le prix. Les MIRP par corps d’état doivent conserver source, statut, hypothèse, question acheteur et décision Patron.

<a id="pf2-052"></a>
#### PF2-052 — 9.3 Interfaces

Le produit doit pouvoir représenter les prestations transversales et limites de lots : inclusion/exclusion/coordination/à confirmer, source CCTP/plan/prix et impact. Le silence d’une DPGF ne crée pas automatiquement une exclusion.

<a id="pf2-053"></a>
#### PF2-053 — 9.4 Constructibilité

Accès, stockage, base vie, circulation, levage, ouvrages provisoires, protections, coupures, horaires, phasage, site occupé, séchage/cure, essais, mise en service, remise en état et autorisations tierces peuvent influencer GO, prix et délai.

---

<a id="pf2-054"></a>
### PF2-054 — 10. Économie, prix, cash et capacité

<a id="pf2-055"></a>
#### PF2-055 — 10.1 Quatre vues économiques

- marge ;
- pic de trésorerie/date/durée/causes ;
- résistance aux scénarios ;
- valeur attendue/coût d’opportunité, sans transformer une probabilité en vérité.

<a id="pf2-056"></a>
#### PF2-056 — 10.2 Prix et révision

Le produit distingue prix ferme/actualisable/révisable, mois/date de référence, index/formule, part fixe, périodicité, exclusions et substitutions lorsque sourcées. Il compare protection contractuelle et exposition achats réelle. Aucun index générique ne vaut couverture.

<a id="pf2-057"></a>
#### PF2-057 — 10.3 Capacité

Comparer carnet signé, affaires probables, réponses en cours, ressources, études, encadrement, compétences rares, matériel, congés, maintenance, déplacement et partenaires réellement disponibles. Une ressource nommée dans l’offre est traitée comme engagement potentiel.

<a id="pf2-058"></a>
#### PF2-058 — 10.4 Portefeuille

Lorsque activé, le produit doit pouvoir tester plusieurs gains simultanés pour cash, garanties, ressources et dépendances communes. Cette capacité peut être V1.x si le socle V1 garantit au moins l’analyse affaire isolée et les dépendances explicites.

---

<a id="pf2-059"></a>
### PF2-059 — 11. Partenaires, sous-traitance et groupements

Le socle V1 doit au minimum conserver et comparer périmètre, exclusions, prix, validité, délais, garanties, conformité, assurance et disponibilité des partenaires utilisés au chiffrage ou à l'offre.

Sous-traitance : prestation/montant, déclaration/acceptation/agrément selon cadre, paiement direct/garantie lorsque pertinent, vigilance, assurance, dépendance et solution de remplacement.

Groupement : forme, mandat, répartition, solidarité, responsabilités et exposition. Une solidarité inhabituelle exige décision Patron.

La structuration avancée de mandats, portails partenaires et connecteurs peut rester V1.x ; l'exposition métier ne peut pas être supprimée de V1 pour cette raison.

---

<a id="pf2-060"></a>
### PF2-060 — 12. Contrat applicable, dérogations et exposition

<a id="pf2-061"></a>
#### PF2-061 — 12.1 Reconstruire le contrat

Public : procédure, CCAG réellement visé/version, CCTG/fascicules cités, CCAP/CCP, AE, pièces de prix, calendrier, réponses/mise au point/avenants selon valeur.

Privé : parties, offre/devis, commande/marché, conditions particulières/générales, plans, planning, échanges acceptés, normes incorporées, sous-traitance, garanties, réception et ordre des pièces.

<a id="pf2-062"></a>
#### PF2-062 — 12.2 Dérogations

Chaîne obligatoire :

`REFERENCE_RULE → CONTRACT_REFERENCE → PARTICULAR_OVERRIDE → APPLICABILITY → BUSINESS_IMPACT → HUMAN_DECISION`.

Le produit doit pouvoir montrer côte à côte la règle de référence et la clause particulière qui la modifie.

<a id="pf2-063"></a>
#### PF2-063 — 12.3 Pénalités et sanctions

Pour chaque sanction : source, déclencheur, unité, formule, base, franchise, plafond, cumul, contradictoire/mise en demeure, dérogation, éventuelle cause exonératoire, responsable, recours partenaire, scénario central/stress et inconnus.

**Interdit :** coder un plafond, une franchise, un délai ou une exonération comme vérité universelle parce qu'un CCAG particulier les prévoit.

<a id="pf2-064"></a>
#### PF2-064 — 12.4 Préservation des droits

Pour chaque événement : source/version, trigger, deadline calculée à partir de la règle applicable, destinataires, forme, contenu requis, responsable, preuves d'envoi/réception, statut et conséquence potentielle. Aucune deadline sensible n'est affichée comme certaine sans source et base de calcul.

<a id="pf2-065"></a>
#### PF2-065 — 12.5 OS / modifications / travaux supplémentaires

Le produit doit rendre visibles pouvoir de prescription, forme, réception, réserves, délai de réaction, valorisation/prix nouveaux, impact délai, preuve et conséquences. Il ne réduit pas tout changement à « avenant possible ».

<a id="pf2-066"></a>
#### PF2-066 — 12.6 Résiliation / substitution

Le produit expose conditions identifiées, remède, mise en demeure, frais et risques, substitution/liquidation et impact financier potentiel. Il ne qualifie pas seul la validité juridique de la clause.

<a id="pf2-067"></a>
#### PF2-067 — 12.7 Réception / règlement / DGD

Le produit représente la séquence applicable et ses preuves. Un DGD tacite ou une forclusion ne peut être affirmé que si chaque condition requise est établie ; sinon `REVIEW_REQUIRED`.

---

<a id="pf2-068"></a>
### PF2-068 — 13. Assurance, HSE, environnement et obligations mesurables

<a id="pf2-069"></a>
#### PF2-069 — 13.1 Assurance

Une attestation présente ne suffit pas. Le produit compare la prestation/technique promise avec la portée déclarée et conserve les états d'incertitude. Les cas ambigus ou sensibles escaladent vers courtier/assureur.

<a id="pf2-070"></a>
#### PF2-070 — 13.2 HSE / prérequis d'exécution

Chaque exigence applicable doit pouvoir être transformée en compétence/personne/matériel/document/délai/coût/planning/preuve. Une obligation connue mais ressource absente peut maintenir P2/P3/P4 en `REVIEW_REQUIRED`.

<a id="pf2-071"></a>
#### PF2-071 — 13.3 Environnement et social

Une promesse mesurable de mémoire ou condition d'exécution devient un engagement structuré, pas du texte libre oublié après dépôt : KPI, valeur, méthode, preuve, coût, responsable, partenaire, reporting et conséquence.

<a id="pf2-072"></a>
#### PF2-072 — 13.4 Déchets / PEMD / REP

Lorsqu'applicable : diagnostic, inventaire, réemploi, flux, tri, opérateur, transport, exutoire, coût, prise en charge, traçabilité et preuve finale. Les règles évolutives restent versionnées.

---

<a id="pf2-073"></a>
### PF2-073 — 14. Production de l'offre et registre des engagements

Tout élément offrant un résultat, moyen, fréquence, délai, personne, matériel, marque, performance, stock, réunion, intervention, méthode, KPI environnement/social, outil ou reporting doit pouvoir devenir un **engagement** relié au texte offert, à la demande source, au coût, au planning, à la preuve de capacité et au responsable futur.

Un engagement critique non chiffré, non prouvé ou incompatible avec la capacité peut bloquer P4 ou exiger dérogation Patron lorsque le risque est arbitrable.

Les documents à produire, remplir, récupérer ou demander restent gérés selon l'Univers documentaire : titulaire, validité, modèle, signature, format, portée, sensibilité, échéance, conséquence et preuve de sortie.

---

<a id="pf2-074"></a>
### PF2-074 — 15. Remise, dépôt et preuve

Le contrat v1.0 est conservé et renforcé :

- candidate exacte et immutable après autorisation sauf nouvelle version ;
- manifeste exhaustif ;
- signatures et P5 distincts ;
- export distinct du dépôt ;
- dépôt externe final humain en V1 ;
- preuve externe rapprochée du paquet/hash ;
- résultats `UNKNOWN/PARTIAL/NOT_PERFORMED` jamais convertis en succès ;
- une preuve de dépôt du mauvais paquet est un incident critique.

---

<a id="pf2-075"></a>
### PF2-075 — 16. Paiement, trésorerie d'exécution et post-réception

<a id="pf2-076"></a>
#### PF2-076 — 16.1 Circuit de paiement

Le produit doit pouvoir représenter les acteurs et pièces qui conditionnent l'encaissement, et distinguer délai contractuel/légal de l'hypothèse prudente utilisée dans le cash-flow.

<a id="pf2-077"></a>
#### PF2-077 — 16.2 Post-réception

Les coûts de OPR, essais, mise en service, formation, DOE/DIUO, corrections, réserves, GPA, pièces de rechange, astreintes, garanties et clôture peuvent être intégrés au prix/marge avant GO lorsque matériels.

La marge estimée à la réception ne doit pas être présentée comme marge finale si des obligations significatives persistent.

---

<a id="pf2-078"></a>
### PF2-078 — 17. Clarification, négociation, résultat et passation

<a id="pf2-079"></a>
#### PF2-079 — 17.1 P6

Chaque clarification, régularisation, négociation, BAFO, prolongation ou mise au point crée ou référence une nouvelle version et déclenche une analyse d'impact ciblée.

<a id="pf2-080"></a>
#### PF2-080 — 17.2 Attribution / rejet

Le dossier conserve notification, date, lots, classement/notes/motifs lorsqu'ils sont disponibles, attributaire/montant communicable, anomalies, délais et décisions de suivi. Toute décision contentieuse reste humaine/professionnelle.

<a id="pf2-081"></a>
#### PF2-081 — 17.3 P7 / dossier de passation obligatoire

Le chantier reçoit :

- contrat et hiérarchie ;
- offre finale/budget/hypothèses ;
- exclusions/réserves/interfaces ;
- engagements vendus ;
- partenaires ;
- planning ;
- garanties ;
- pénalités et sanctions ;
- assurance et prérequis HSE ;
- obligations environnement/social ;
- documents post-attribution ;
- conditions du GO ;
- circuit de paiement ;
- `RIGHT_PRESERVATION_EVENT` et échéances ;
- risques résiduels et responsables.

La passation doit être acceptée par les rôles prévus. Une ligne critique sans responsable, source ou état empêche de prétendre « passation complète ».

---

<a id="pf2-082"></a>
### PF2-082 — 18. Retour d'expérience

Le REX rapproche prévu/réalisé : prix, heures, rendements, achats, partenaires, délai, cash, pénalités, révision, réserves, garanties, réclamations, marge et satisfaction.

Il capture aussi : droits préservés/perdus, OS/modifications, dérogations coûteuses, engagements difficiles, faux positifs réglementaires/HSE/assurance et coûts post-réception sous-estimés.

Aucun REX ne devient règle d'entreprise sans portée, contexte et validation.

---

<a id="pf2-083"></a>
### PF2-083 — 19. UX et surfaces — impact du v2.0

Le catalogue C00–C16 et les 104 contrats de couverture restent la carte de navigation de référence jusqu'à sa révision. Le v2.0 **n'autorise pas Codex à inventer de nouvelles routes ou de nouveaux écrans sans mise à jour UX**.

Les nouveaux contrats doivent d'abord être matérialisés dans les surfaces existantes lorsque cohérent :

- C05 « À résoudre » : dérogations, sanctions, droits, prérequis et conditions ;
- C07 Décision : Carte d'Engagement, P2/P3/P4/P6/P7 et décisions ;
- C08 Prix : exposition pénalités, cash, prix/révision, coûts HSE/post-réception ;
- C09 Partenaires : assurance, vigilance, réserves, dépendances ;
- C10 Réponse : engagements mesurables ;
- C12 Résultat/passation : DGD, droits, réception, passation renforcée ;
- C13 Entreprise : assurances/capacités/règles validées ;
- C01 Accueil Patron : décisions de la Carte d'Engagement.

Toute modification qui change la structure C00–C16, les 104 contrats ou PUX exige une nouvelle version du catalogue UX.

---

<a id="pf2-084"></a>
### PF2-084 — 20. IA, provenance et abstention

L'IA peut : extraire, classer, rechercher, rapprocher, suggérer des impacts et préparer des questions/brouillons.

L'IA ne peut seule : appliquer définitivement une règle juridique, déclarer une couverture d'assurance, calculer une échéance sans règle sourcée, franchir une porte, accepter une dérogation, fixer le prix, décider un recours, signer, déposer ou effacer un inconnu.

Pour les calculs déterministes de délai, sanction, formule de prix et cash : les paramètres peuvent être extraits/proposés par IA, mais le calcul final est effectué par logique déterministe versionnée à partir de paramètres validés.

---

<a id="pf2-085"></a>
### PF2-085 — 21. Périmètre V1 v2.0

<a id="pf2-086"></a>
#### PF2-086 — 21.1 Indispensable V1

- identité/MFA/tenant/délégations et confidentialité existantes ;
- Affaire, DCE, versions, preuves, exigences, inconnus, contradictions ;
- MIRP et interfaces critiques ;
- P0–P7 et conditions ;
- couverture économique Patron : prix, marge, cash, capacités ;
- registre des engagements ;
- profil réglementaire minimal avec règles versionnées nécessaires aux pilotes ;
- reconstruction contractuelle minimale et dérogations critiques ;
- sanctions/pénalités critiques ;
- événements de préservation des droits nécessaires à la passation ;
- OS/modification et règlement des comptes au niveau nécessaire pour P7 ;
- assurance de principe avec abstention/escalade ;
- HSE/prérequis critiques ;
- engagement environnement/social mesurable lorsqu'exigé par le DCE ;
- candidate/manifeste/P5/export/dépôt humain/preuve ;
- P6 et P7 renforcé ;
- REX minimal ;
- Carte d'Engagement Patron ;
- tests de sécurité, tenant, confidentialité, unknown/partial et non-régression métier.

<a id="pf2-087"></a>
#### PF2-087 — 21.2 V1.x / qualification ultérieure

- packs sectoriels complets ;
- portefeuille multi-affaires avancé ;
- automatisation/connecteurs de portails ;
- partenaires/groupements avec mandats complexes et workflows externes ;
- corpus privé exhaustif ;
- contrôle réglementaire spécialisé multi-domaines au-delà des pilotes ;
- administration avancée ;
- automatisation juridique autonome — **non prévue tant que la doctrine produit reste inchangée**.

<a id="pf2-088"></a>
#### PF2-088 — 21.3 Hors promesse sans qualification

- « conformité juridique garantie » ;
- « toutes les pénalités détectées » ;
- « aucune hallucination » ;
- « couverture assurance certifiée » ;
- « aucun droit ne sera perdu » ;
- « rentabilité garantie » ;
- « toutes les normes/DTU disponibles » ;
- « dépôt automatique fiable ».

---

<a id="pf2-089"></a>
### PF2-089 — 22. Validations externes obligatoires

Avant blocage automatique ou promesse publique sur les sujets concernés :

- juriste commande publique ;
- juriste construction privée + corpus privé ;
- DAF BTP ;
- courtier/assureur construction ;
- QSE / spécialiste amiante et autres sujets sensibles ;
- métreurs/conducteurs par corps d'état pour MIRP ;
- essais réels de dépôt ;
- banc formats/plans ;
- corpus Golden DCE annoté ;
- accessibilité/RGPD/sécurité lorsque la promesse l'exige.

Une validation externe doit avoir date, périmètre, version de règle et preuve ; elle n'est pas remplacée par une opinion de LLM.

---

<a id="pf2-090"></a>
### PF2-090 — 23. Recettes métier obligatoires du v2.0

Les recettes historiques restent applicables. Ajouter au minimum :

- REC-29 versions CCAG différentes ;
- REC-30 dérogation au régime de pénalités ;
- REC-31 OS non valorisé ;
- REC-32 décompte / délai de réclamation ;
- REC-33 exécution aux frais et risques ;
- REC-34 engagement environnemental vendu ;
- REC-35 applicabilité réglementaire date/usage ;
- REC-36 RAT infrastructure ;
- REC-37 assurance hors activité déclarée ;
- REC-38 prérequis HSE sans ressource ;
- REC-39 circuit de facturation public ;
- REC-40 règle future ;
- REC-41 DGD tacite uniquement si conditions prouvées ;
- REC-42 pénalités cumulatives ;
- REC-43 engagement mémoire non chiffré ;
- REC-44 portefeuille cash ;
- REC-45 rectificatif modifiant un délai/droit.

Chaque recette échoue si le bon résultat est obtenu sans preuve consultable, avec fuite de confidentialité ou par conclusion non sourcée.

---

<a id="pf2-091"></a>
### PF2-091 — 24. Critères de qualification métier

Mesurer séparément :

- rappel des exigences critiques ;
- précision/faux positifs ;
- source/locator ;
- préservation des inconnus ;
- contradictions ;
- dérogations ;
- sanctions/pénalités ;
- conditions GO ;
- droits/échéances contractuelles ;
- couverture du prix et cash ;
- capacité ;
- séparation Patron/Collaborateur/tenant ;
- engagement offre → passation ;
- candidate autorisée → preuve de dépôt ;
- compréhension du dossier P7 par le conducteur.

**Zéro tolérance** sur : fuite financière inter-rôles/tenant, mauvaise version autorisée, faux reçu, conclusion juridique inventée, délai contractuel affiché comme certain sans source, engagement critique silencieusement perdu.

---

<a id="pf2-092"></a>
### PF2-092 — 25. Contrat de changement et traçabilité

Toute modification qui change rôle, porte, état, source de vérité, classification, déduction autorisée, engagement, preuve attendue, objet métier ou périmètre vendu exige :

1. nouvelle version du Product Freeze ou ADR relié ;
2. impact catalogue UX/parcours ;
3. impact cahier technique, migrations et API ;
4. tests de refus, confidentialité, idempotence, inconnus et régression métier ;
5. revue propriétaire.

Une technologie peut changer sans rouvrir le Product Freeze si elle respecte exactement ces contrats.

Aucune spécification technique, maquette, migration ou code ne peut créer silencieusement un nouveau droit ou réduire une exigence du présent document.

---

<a id="pf2-093"></a>
### PF2-093 — 26. Règle de dérivation vers Codex

Après promotion propriétaire :

```text
MASTER MÉTIER v2.0
      ↓ couverture sémantique contrôlée
PRODUCT FREEZE v2.0
      ↓ contrats techniques
CAHIER TECHNIQUE D'EXÉCUTION v2.1
      ↓ audit du code réel
MATRICE KEEP / ADAPT / REPLACE / DELETE / ABSENT
      ↓ migrations + plan de PR
CODE + TESTS + PREUVES
```

Codex doit commencer par un audit READ-ONLY du code actuel. Il n'est pas autorisé à créer les nouvelles tables, routes ou surfaces avant d'avoir produit la cartographie d'existant, le delta, les migrations proposées, les tests de refus et le rollback.

Le code et les tests sont la preuve de ce qui est effectivement implémenté ; ils ne redéfinissent jamais le métier.

---

<a id="pf2-094"></a>
### PF2-094 — 27. Références normatives après promotion

1. `SMART_AO_CAHIER_DIRECTEUR_METIER_MASTER_v2.0.md` — source de profondeur métier et documentaire ;
2. présent `SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v2.0.md` — autorité produit/métier ;
3. catalogue UX actif, à réviser uniquement pour les impacts de surface nécessaires ;
4. fondations UX actives ;
5. `SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v2.1.md` — traduction technique ;
6. architecture logicielle active + ADR de delta si nécessaire ;
7. code/tests/migrations — état effectivement implémenté.

Le MASTER n'est pas une seconde autorité contradictoire : il conserve la profondeur et sert de source de traçabilité ; le Freeze v2.0 décide ce qui devient contrat produit codable.

---

<a id="pf2-095"></a>
### PF2-095 — 28. Promotion

**État actuel : PROMU.**

Le propriétaire a confirmé la promotion du Product Freeze v2.0. Le v1.0 est historique, l'index des références actives est réaligné et le cahier technique v2.1 dérive désormais de cette autorité. Codex peut passer de l'audit à l'implémentation uniquement selon les gates approuvés, les validations externes prévues et les tranches T1–T8.
<!-- END INTEGRATION-PF2 -->
