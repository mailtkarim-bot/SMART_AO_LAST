/* global document, Event, setTimeout, fetch, performance, location, localStorage, sessionStorage, URL */
// Replay with Chrome DevTools evaluate_script after opening the local fixture.
export default async function qualifyRcCandidates() {
  const checks = [];
  const check = (name, ok) => { checks.push({ name, ok }); if (!ok) throw new Error(name); };
  const tick = () => new Promise(resolve => setTimeout(resolve, 40));
  const visible = () => Boolean(document.querySelector('.rc-candidate-values'));
  const panel = () => document.querySelector('.dce-reading-panel');
  const button = text => Array.from(document.querySelectorAll('button')).find(item => item.textContent === text);
  const select = async (name, value) => {
    const control = document.querySelector(`select[aria-label="${name}"]`);
    control.value = value; control.dispatchEvent(new Event('change', { bubbles: true })); await tick();
  };
  const load = async () => {
    button('Actualiser la lecture').click(); await tick();
    for (let i = 0; i < 100 && button('Lecture…'); i++) await tick();
    if (button('Lecture…')) throw new Error('Synthetic reading did not settle');
  };
  const release = async () => { button('Libérer les réponses retardées').click(); await tick(); await tick(); };
  await select('Affaire synthétique', 'case-A');
  await select('Session synthétique', 'session-A');
  await select('Rôle synthétique', 'PATRON_ADMIN');
  for (const mode of ['nominal', 'unknown', 'review', 'fragment', 'version', 'case', '409', '404']) {
    await select('Réponse synthétique', mode); await load();
    check(`scenario:${mode}`, mode === 'nominal' ? visible() : !visible());
    if (mode === 'unknown') check('UNKNOWN explicite', panel().innerText.includes('Valeurs non prouvées · UNKNOWN'));
    if (mode === 'review') check('REVIEW_REQUIRED explicite', panel().innerText.includes('Valeurs à revoir · REVIEW_REQUIRED'));
  }
  await select('Réponse synthétique', 'nominal');
  for (const [name, other, original] of [
    ['Affaire synthétique', 'case-B', 'case-A'], ['Session synthétique', 'session-B', 'session-A'],
    ['Rôle synthétique', 'COLLABORATEUR', 'PATRON_ADMIN'], ['Session synthétique', '', 'session-A'],
  ]) {
    await load(); check(`baseline:${name}:${other}`, visible());
    await select(name, other); check(`masquage:${name}:${other}`, !visible() && !panel());
    await select(name, original); check(`retour sans résurrection:${name}:${other}`, !panel());
  }
  await select('Réponse synthétique', 'delayed'); button('Actualiser la lecture').click(); await tick();
  await select('Affaire synthétique', 'case-B'); await select('Affaire synthétique', 'case-A');
  await release(); check('réponse tardive après aller-retour ignorée', !panel());
  button('Actualiser la lecture').click(); await tick(); await select('Affaire synthétique', 'case-B');
  await select('Réponse synthétique', 'nominal'); await load();
  check('nouvelle affaire chargée', panel()?.innerText.includes('Dossier synthétique case-B'));
  await release(); check('ancienne réponse hors ordre ignorée', panel()?.innerText.includes('Dossier synthétique case-B') && !panel()?.innerText.includes('DC2'));
  check('cookies et stockage vides', !document.cookie && localStorage.length === 0 && sessionStorage.length === 0);
  const requests = await (await fetch('/__proof')).json();
  check('GET uniquement sans bearer ni cookie', requests.every(item => item.method === 'GET' && !item.authorization && !item.cookie));
  check('ressources du parcours locales', performance.getEntriesByType('resource').every(item => new URL(item.name).origin === location.origin));
  return { checks, requests };
}
