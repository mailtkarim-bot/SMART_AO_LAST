# Preuve navigateur RC locale

Depuis la racine du dépôt : `node web/browser/rc-candidates/serve.mjs`.
Ouvrir `http://127.0.0.1:5179/browser/rc-candidates/` dans un contexte Chromium **isolé**, sans cookies ni session utilisateur. Cette fixture est séparée de l'entrée de production; elle utilise le panneau, le hook et le client API réels. Tous les états et acteurs sont synthétiques, sans autorité métier. Aucun proxy backend; les méthodes autres que GET sont refusées sur l'API simulée.

Avec Chrome DevTools MCP `evaluate_script`, exécuter :

```js
async () => await (await import('/browser/rc-candidates/checks.mjs')).default()
```

Les 28 assertions doivent réussir : affichage nominal/inconnus/refus, changements d'Affaire/session/rôle, déconnexion, retour sans résurrection, réponses tardives/hors ordre, lectures GET sans bearer/cookie et ressources locales. Une assertion fausse lève une erreur; conserver la sortie JSON et le journal `/__proof`. `SMARTAO_BROWSER_PROOF_LOG` permet d'écrire ce journal local à l'arrêt du serveur. La preuve ne remplace pas les autorisations réelles : le client de production utilise `credentials: include`, l'isolation du profil est indispensable.

Inspecter ensuite les régions source et leurs disclosures au clavier, à390px et1440px, sans débordement. Cette fixture ne qualifie ni le backend live, ni un corpus réel, ni une conformité WCAG complète, ni la refonte visuelle Cytd globale. Aucun POST métier, P3, export ou GO public.
