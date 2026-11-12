# A1 — contre-lecture technique, portée et expurgation — 11 octobre 2026

## Verdict et périmètre

**Admission Golden DCE : NON ACCORDÉE. A2 HOLD; NO-GO public.** La confrontation technique demandée est réalisée. La seconde lecture a un contexte Codex distinct sans historique ni réponses primaires, mais ne représente pas l’Expert métier 2 humain. Le protocole actif [QUAL-01, rôles et arbitrage](../03_Architecture_et_implementation/phase0_gate0/SMART_AO_PHASE0_QUAL-01_GOLDEN_DCE.md#6-rôles-et-arbitrage) distingue Expert métier 1, Expert métier 2, Adjudicator, Corpus Owner et Security/DPO. Leurs actes restent non exécutés.

La demande Owner autorise l’inspection et la préparation privées du corpus fourni. Aucune autorisation tierce de réutilisation Golden n’a été inventée à partir du téléchargement public.

## Confrontation des 29 faits

- Six PDF identifiés par hashes, fournis avec questions et valeurs vierges au lecteur technique à contexte neuf; extraction locale fraîche, aucun accès déclaré aux annotations primaires.
- 29 valeurs concordantes, aucun désaccord de valeur. Le lecteur d’intégration a vérifié les six hashes et les 29 citations/pages, ainsi que les deux ancrages supplémentaires critiques.
- Six clarifications de portée conservées : accès aux raccordements sans dispense générale de compteurs; taux général/exception conditionnelle; seuils CEE distingués des prescriptions d’ouvrage; consigne à confirmer avant mise en service.
- Les observations documentaires ne prouvent ni réalisation des travaux, ni statut réel du titulaire, ni confirmation du réglage, ni actualité future.

Les lectures originales sont figées dans des copies JSON hashées en lecture seule. `reconciliation_v001.json` conserve valeurs primaires/secondaires et décisions techniques; `annotations_reconciliees_v002.json` ajoute le contexte avec `HUMAN_REVIEW_REQUIRED`, sans réécrire la version primaire. L’indépendance est une isolation de contexte avec instructions, pas une frontière de confinement ni une validation humaine.

## Expurgation technique limitée

Six PDF de revue sont reconstruits uniquement à partir de 29 champs, extraits minimaux, aliases et références de pages. Aucun original, plan ou image n’est incorporé. Ce sont des **copies textuelles de revue**, pas des PDF DCE originaux ni un benchmark de leur mise en page.

Contrôles : 29 valeurs présentes après réextraction, absence de pièces jointes/images/liens/annotations, métadonnées auteur/XMP vidées, absence d’actions JavaScript/Launch, zéro correspondance des motifs e-mail/téléphone/URL/chemins locaux/cas nommés. Contrôle visuel d’une page Unicode et contrôle de débordement des 29 pages. Huit nouveaux fichiers de lecture ont été restreints à 0600; ils étaient déjà contenus dans un répertoire privé 0700. Les snapshots gelés restent 0400. Aucun fichier original modifié.

**Limites :** les dates et faits contractuels restent présents, donc un rapprochement contextuel demeure possible. Pas de revue exhaustive NER/DPO. L’absence de motifs détectés n’équivaut pas à une certification d’anonymisation complète.

## Droits : qualification du dossier de preuves

Le ledger privé de droits identifie, avec hashes/pages, la clause de discrétion du CCAP du premier cas, la confidentialité du carnet de plans du second et la limitation d’usage du troisième. Les plans restent hors échantillon. Le quatrième n’est pas admis ni annoté dans ce pilote.

Les [CGU PLACE, propriété intellectuelle](https://www.marches-publics.gouv.fr/app.php/entreprise/footer/conditions-utilisation) mentionnent une protection des contenus et une autorisation écrite. Leur consultation ne fournit pas à elle seule un acte de réutilisation applicable au corpus. Les observations ne constituent pas une interprétation juridique de l’applicabilité des clauses.

`rights_evidence_review_v001.json` porte **NOT_ESTABLISHED**, sans signature Corpus Owner ni Security/DPO. `admission_status_v003.json` porte **NOT_GRANTED**. Le dossier `REVUE_HUMAINE_A1.md` est prêt avec périmètre, preuves et actes à compléter; aucune identité ou décision humaine préremplie.

## Vérification et reprise

Preuves privées hors Git : `/home/noor/.local/share/smartao-proofs/a1-dce-preparation-20261011/`. Sous-dossiers `secondary-blind-technical`, `freeze`, `review-redacted-v002`; copies, annotations et ledgers ne sont pas indexés dans Git.

Contrôles des helpers : compilation Python, assertions de hashes/citations/valeurs et vie privée. Semgrep 1.179.0 `p/security-audit`, métriques off : 2 helpers, 0 finding, 0 erreur, aucun avertissement de taint. Code applicatif/migrations/dépendances inchangés; suites backend/Web non rejouées, ni OCR, import métier, navigateur, VPS, déploiement ou push. Les contrats documentaires du dépôt et `git diff --check` sont vérifiés séparément.

Le validateur Golden présent est v1 et vérifie la structure et les hashes. Il ne constitue pas une décision de droits ou d’admission; les outils v2 cités par d’anciens handoffs ne sont pas présents et ne sont pas recréés pour cette tranche.

Méthode : Superpowers using-superpowers, dispatching-parallel-agents et verification-before-completion; ECC security-review, verification-loop et living-docs-governance; PDF/Poppler et PyMuPDF installé, API vérifiée via Context7. Graphify a orienté les sources de gouvernance. Aucune interface modifiée, donc aucun workflow OpenDesign/Impeccable; aucun outil de classification externe ne reçoit le corpus.

## Prochaine étape

Faire valider le dossier par les rôles humains métier, Corpus Owner et Security/DPO, avec décisions de réutilisation/anonymisation traçables, puis décider l’admission. Les actes manquants sont affichés dans le ledger, pas remplacés par les accords techniques IA.
