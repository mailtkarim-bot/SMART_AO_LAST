# T47 — Cycle métier paiement et coût post-réception

**Statut :** prêt à cadrer localement — NO-GO public maintenu

## Objectif

Préparer une capacité métier qui relie les conditions contractuelles de
paiement, les retenues, le solde et les coûts post-réception sans transformer
une clause en encaissement certain.

## Périmètre initial

- circuit contractuel et événements déclencheurs ;
- hypothèses de délai et de cash explicitement marquées ;
- retenues, garanties, solde et coût post-réception ;
- données `FINANCIAL_PRIVATE` tenant-scoped ;
- revue humaine obligatoire pour les inconnus et contradictions.

## Interdits

- aucun calcul juridique automatique ;
- aucun encaissement ou paiement externe ;
- aucune certitude de cash sans preuve ;
- aucune exposition Collaborateur des données financières privées ;
- aucune ouverture publique.

## Preuves attendues

Contrat domaine, migration additive si nécessaire, tests PostgreSQL de tenant/
confidentialité/idempotence, projection Patron C07 et gates complètes.

Contrat initial implémenté : `PaymentPostReceptionCycle` exige une source et
un événement déclencheur, conserve les hypothèses prudentes de cash et les
coûts post-réception sans produire de certitude.
