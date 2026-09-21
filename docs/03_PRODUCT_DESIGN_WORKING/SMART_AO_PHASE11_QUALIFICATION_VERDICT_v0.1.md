# SMART AO — Verdict de qualification Phase 11 v0.1

**Date :** 21 septembre 2026  
**Verdict :** `QUALIFIÉ LOCALEMENT — PAS PRÊT POUR PRODUCTION PUBLIQUE`

## Preuves locales

| Domaine | Résultat |
|---|---|
| Backend PostgreSQL | 1 718 tests passent sur la passe complète ; les 2 tests calendrier échoués après installation des extras repassent après restauration de `icalendar`/`tzdata`, soit 1 720 tests collectés verts |
| Frontend | 187 tests passent sur 34 fichiers |
| Exploitation | 45 tests ops passent |
| Python dépendances | `pip-audit` : aucune vulnérabilité connue sur le projet et ses extras installés |
| Frontend dépendances | `pnpm audit` officiel : 0 vulnérabilité de production |
| Code sécurité | Bandit passe sur `backend/app` |
| Stack local | PostgreSQL, ClamAV, migrations, backend, frontend, Caddy et workers ; HTTPS, restauration, rotation, charge et reprise vérifiés |
| DCE | ingestion, quarantaine, extraction, classification, RC, exigences, lecture et limites vérifiées sur PostgreSQL isolé |
| RAG | corpus redacted temporaire, ancres 3/3, refus financier, fuite 0, index mémoire supprimé |

## Limites restantes

- aucun VPS, domaine public, firewall distant, sauvegarde hors site ou reprise matérielle ;
- aucun test SMTP/webhook/signature externe réel ;
- Golden DCE réel : droits, anonymisation, double revue et désaccords restent à qualifier ;
- `detect-secrets` n’est pas disponible dans le poste courant, donc ce contrôle n’est pas revendiqué dans cette passe ;
- OCR/Docling/RAG sont installés et mesurés localement, mais restent désactivés en préproduction ;
- les mesures de performance sont des repères de ce poste et ne sont pas des budgets VPS.

## Décision

SMART AO peut poursuivre la recette locale et les preuves métier. Il ne doit pas être présenté comme déployé en production publique. L’ouverture publique dépend encore d’un environnement VPS, de la recette Golden DCE, des intégrations externes et d’une décision GO/NO-GO propriétaire.

