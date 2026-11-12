# Préparation locale de l’échantillon DCE — 11 octobre 2026

L’Owner a fourni les DCE téléchargés sur PLACE et demandé à Codex de travailler sur leur inspection locale. Cette instruction autorise la préparation locale; elle ne constitue pas une qualification des droits de réutilisation, une admission Golden DCE, une seconde revue ou un GO public.

## Résultats observés

- DCE-01 : archive valide, 23 fichiers, dont 4 CCTP, 4 DPGF XLSX, CCAP, RC, plans et deux registres de questions-réponses. Échantillon pilote retenu : pièces administratives et réponses, sans plans du site.
- DCE-02 : archive valide, 40 fichiers, règlement explicitement modifié, CCTP/DPGF de deux lots et questions-réponses. Le carnet de plans est soumis à une attestation de confidentialité : hors premier échantillon.
- DCE-03 : archive valide, 4 entrées dont 3 ZIP imbriqués également vérifiés. Clause limitant l’utilisation/transmission des informations à la réponse à la consultation repérée dans le RC : REVIEW_REQUIRED, pas d’admission au corpus d’essai.
- DCE-04 : le premier fichier fourni avec extension ZIP est une page HTML de formulaire, conservée sans modification. Le véritable paquet a été récupéré via le parcours anonyme officiel : 735 720 957 octets, 523 entrées, CRC valide et SHA-256 enregistré. La nouvelle archive vérifiée est placée à côté des fichiers fournis; pas encore d’annotation sur ce dossier.

La correspondance entre alias et fichiers source est conservée exclusivement dans l’inventaire local privé. Aucun PDF, tableur, plan, archive, extrait ou annotation du corpus n’est ajouté au dépôt Git.

## Annotation primaire pilote

29 faits : 24 sur DCE-01, 5 sur DCE-02, issus de six PDF. Ils couvrent RC, CCAP, exigences techniques et questions-réponses. Chaque fait porte le locator exact, le SHA-256 du PDF, la page physique indexée à partir de 1, l’extrait support et la valeur attendue. Les contrôles ont vérifié les 29 ancrages textuels et la somme 100 % des critères pondérés du premier RC. Les dates restent celles écrites dans les sources locales, sans supposer leur actualité future.

`annotations_primaires_brouillon.json` demeure PRIMARY_DRAFT_NOT_GOLDEN/REVIEW_REQUIRED. `annotation_secondaire_vierge.json` est une grille sans réponses pour une lecture indépendante; ce modèle ne vaut pas une seconde annotation. La collecte est locale et privée, pas un benchmark applicatif. Les quatre DPGF XLSX du premier dossier sont analysées structurellement (deux feuilles chacune, 164/120/135/168 lignes XML); aucune qualification des formules/prix ni comparabilité inter-lots n’est déduite. Les 20 PDF uniques extraits représentent 414 pages physiques; cela ne signifie pas une revue exhaustive de toutes ces pages.

## Preuves et contrôles

Dossier privé : `/home/noor/.local/share/smartao-proofs/a1-dce-preparation-20261011/` (répertoire 0700, fichiers de contenu 0600). Inventaire des archives avec SHA-256 et CRC, inventaire des pièces imbriquées, copies minimales et textes extraits, annotation primaire, grille secondaire et vérification JSON. Les fichiers originaux sont conservés intacts. Aucun compte ou cookie du navigateur utilisateur n’est utilisé; la récupération emploie une session HTTP anonyme indépendante.

Précontrôles du dépôt : checkout principal propre à `30f2693` avant documentation, branche `codex/reconcile-smartao-20261009`. Aucun code applicatif, migration ou dépendance du projet ne change. Les suites backend/Web précédentes ne sont pas présentées comme une qualification de ces DCE réels. Pas de nouveau test applicatif, OCR, import en base ni backend live.

Méthode : skill PDF (lecture locale Poppler), ECC living-docs-governance pour le statut et Superpowers using-superpowers pour la discipline d’entrée. Pas de génération UI ni OpenDesign; pas de nouveau graphe sur le corpus ou d’envoi à un outil distant de classification.

## Suite

Confronter l’annotation pilote à une seconde lecture indépendante, puis traiter les désaccords. Qualifier séparément droits et anonymisation avant admission Golden DCE. A1 reste non admis; A2 HOLD et NO-GO public maintenus.


## Suite exécutée le 11 octobre

La [contre-lecture technique et expurgation](A1_REVUE_TECHNIQUE_INDEPENDANTE_ET_EXPURGATION_2026-10-11.md) est réalisée après cette préparation : 29 valeurs concordantes, six précisions de portée et six copies textuelles de revue contrôlées. Elle ne vaut pas seconde annotation métier humaine. Les lectures originales sont conservées, une version réconciliée distincte est créée; le plan porte la prochaine étape humaine et l’admission reste NON ACCORDÉE.
