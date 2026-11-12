import { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { createApiClient } from "../infrastructure/api";
import { useDceKnowledge } from "../features/dce/useDceKnowledge";
import { DceKnowledgePanel } from "../features/dce/DceKnowledgePanel";
import "../app/styles.css";

function Fixture() {
  const [caseId, setCaseId] = useState("case-A");
  const [session, setSession] = useState("session-A");
  const [role, setRole] = useState("PATRON_ADMIN");
  const [scenario, setScenario] = useState("nominal");
  const [message, setMessage] = useState<{ tone: "success" | "error" | "warning"; text: string } | null>(null);
  const api = useMemo(() => createApiClient(`/synthetic/${scenario}`, ""), [scenario]);
  const dce = useDceKnowledge(api, setMessage, caseId, session ? JSON.stringify(["synthetic-tenant", session, role]) : "");
  return <main>
    <h1>Qualification RC · données synthétiques</h1>
    <p>Aucun compte, cookie, token ni backend réel. Les sélecteurs ci-dessous pilotent uniquement la preuve locale.</p>
    <label>Affaire <select aria-label="Affaire synthétique" value={caseId} onChange={e => setCaseId(e.target.value)}><option>case-A</option><option>case-B</option><option value="">Aucune</option></select></label>
    <label>Session <select aria-label="Session synthétique" value={session} onChange={e => setSession(e.target.value)}><option>session-A</option><option>session-B</option><option value="">Déconnectée</option></select></label>
    <label>Rôle <select aria-label="Rôle synthétique" value={role} onChange={e => setRole(e.target.value)}><option>PATRON_ADMIN</option><option>COLLABORATEUR</option></select></label>
    <label>Réponse <select aria-label="Réponse synthétique" value={scenario} onChange={e => setScenario(e.target.value)}>{["nominal", "unknown", "review", "fragment", "version", "case", "409", "404", "delayed"].map(value => <option key={value}>{value}</option>)}</select></label>
    <button type="button" onClick={() => void fetch("/__release")}>Libérer les réponses retardées</button>
    {message && <p role="status">{message.text}</p>}
    <DceKnowledgePanel selectedCaseId={caseId} reading={dce.reading} results={dce.results} query={dce.query} loading={dce.loading} searching={dce.searching} onQueryChange={dce.setQuery} onLoad={() => void dce.loadReading()} onSearch={() => void dce.searchKnowledge()} onResetSearch={dce.resetSearch} />
  </main>;
}
createRoot(document.getElementById("root")!).render(<Fixture />);
