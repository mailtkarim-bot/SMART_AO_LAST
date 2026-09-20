# SMART AO — Runbook préproduction VPS v0.1

**Statut :** prêt pour provisionnement VPS  
**Date :** 20 septembre 2026  
**Prérequis :** Product Freeze v1.0, cahier technique v1.0, Docker Compose préproduction

## 1. Dimensionnement minimal

- 4 vCPU dédiés ou burstables ;
- 8 Go RAM minimum, 16 Go recommandés avec extraction/ClamAV ;
- 80 Go SSD pour l’application, PostgreSQL et quarantaine ;
- volume séparé pour sauvegardes, idéalement hors VPS ;
- Ubuntu LTS récent, Docker Engine et plugin Compose ;
- DNS public, certificats Caddy, pare-feu SSH administré + HTTP/HTTPS uniquement.

Le VPS de préproduction ne doit contenir aucune donnée client réelle avant validation du smoke test, de la sauvegarde et de la restauration.

## 2. Installation et configuration

```bash
git clone git@github.com:mailtkarim-bot/SMART_AO_LAST.git /opt/smart-ao
cd /opt/smart-ao
cp ops/.env.preprod.example ops/.env.preprod
chmod 600 ops/.env.preprod
${EDITOR:-vi} ops/.env.preprod
```

Renseigner uniquement sur le VPS : domaine, URL PostgreSQL, identifiants PostgreSQL, clés JWT aléatoires, paramètres SMTP/webhook si activés. Aucun secret ne doit être commit ou copié dans le dépôt.

## 3. Premier déploiement contrôlé

```bash
ops/deploy-preprod.sh config
SMART_AO_ALLOW_EMPTY_BACKUP=1 ops/deploy-preprod.sh deploy
ops/deploy-preprod.sh healthcheck
```

Le premier déploiement est accepté seulement si PostgreSQL et ClamAV sont `healthy`, l’API live/ready répond, Caddy sert HTTPS et aucun port interne n’est publié.

## 4. Sauvegarde

```bash
ops/deploy-preprod.sh backup
```

La sauvegarde produit le dump PostgreSQL compressé, les volumes privés nécessaires et un manifeste SHA-256 avec permissions restreintes. Copier ensuite le répertoire de sauvegarde vers un stockage hors VPS.

## 5. Restauration vérifiée

```bash
ops/deploy-preprod.sh restore /var/backups/smart-ao/smart_ao_<timestamp>.sql.gz
```

Le script restaure dans une base temporaire isolée, vérifie les tables de durabilité, la tête Alembic et le trigger append-only, puis supprime la base temporaire. Il ne remplace jamais la base active.

La preuve locale déjà exécutée a restauré 127 tables, la tête `20260920_0090` et le trigger append-only ; la preuve VPS reste à exécuter.

## 6. Rotation JWT

```bash
cp ops/.env.preprod ops/.env.preprod.before-rotation
chmod 600 ops/.env.preprod.before-rotation
SMART_AO_CONFIRM_ROTATE=YES \
SMART_AO_NEW_JWT_SIGNING_KEY="$(openssl rand -base64 48)" \
ops/rotate-jwt-key-preprod.sh
ops/deploy-preprod.sh healthcheck
```

La rotation se déroule dans une fenêtre de maintenance : elle invalide les sessions signées avec l’ancienne clé dans cette version, puis exige une reconnexion. Détruire la copie temporaire après vérification et conserver la nouvelle valeur uniquement dans le gestionnaire de secrets ou le fichier VPS `0600`.

## 7. Contrôles après restauration/rotation

- login + MFA et step-up ;
- création idempotente d’une Affaire de test ;
- lecture DCE protégée et refus Collaborateur/tenant étranger ;
- upload EICAR uniquement en préproduction dédiée, puis rejet ClamAV ;
- vérification `external_submission: NOT_PERFORMED` ;
- vérification des logs sans secret, mot de passe, token, marge ou contenu DCE ;
- nouveau backup après rotation.

## 8. Rollback et incident

Arrêter la mise en production si healthcheck, migration, backup ou restauration échoue. Revenir à l’image précédente seulement après sauvegarde et vérification de compatibilité de schéma. Une migration destructive, une clé compromise ou une restauration non vérifiée bloque l’ouverture client.

## 9. Limite actuelle

Ce runbook est prêt, mais aucun VPS, domaine, secret préproduction ou backup réel n’est encore disponible dans le poste local. La restauration et la rotation réelles restent donc une opération à exécuter sur l’infrastructure provisionnée.
