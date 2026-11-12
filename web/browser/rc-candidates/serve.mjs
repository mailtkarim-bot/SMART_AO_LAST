// Local synthetic fixture only; never proxies any API to a backend.
import { createServer } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";
import console from "node:console";
import { writeFile } from "node:fs/promises";
import process from "node:process";

const requests = [];
let pending = [];
function fixture(caseId, scenario) {
  const fragment = "synthetic-fragment";
  const candidate = {
    projector_version: "1", state: "CANDIDATES_ONLY", reason_code: "SOURCE_VALUES_CANDIDATE", source_fragment_id: fragment,
    documents: [scenario === "delayed" ? "DC2" : "DC1"], document_state: "CANDIDATE",
    date_iso: "2034-11-21", date_state: "CANDIDATE", time_local: "10:30", time_state: "CANDIDATE", timezone: null, timezone_state: "UNKNOWN", lot_numbers: [2], lot_state: "CANDIDATE", applicability: "UNKNOWN",
    evidence: [
      { field: "DOCUMENT", value: scenario === "delayed" ? "DC2" : "DC1", start_byte_offset: 7, end_byte_offset: 10 },
      { field: "DATE", value: "2034-11-21", start_byte_offset: 20, end_byte_offset: 30 },
      { field: "TIME", value: "10:30", start_byte_offset: 34, end_byte_offset: 39 },
      { field: "LOT", value: "2", start_byte_offset: 49, end_byte_offset: 50 },
    ],
  };
  if (scenario === "unknown" || scenario === "review") {
    candidate.state = scenario === "unknown" ? "UNKNOWN" : "REVIEW_REQUIRED";
    candidate.documents = []; candidate.document_state = "UNKNOWN"; candidate.date_iso = candidate.time_local = null;
    candidate.date_state = candidate.time_state = "UNKNOWN"; candidate.lot_numbers = []; candidate.lot_state = "UNKNOWN"; candidate.evidence = [];
  }
  if (scenario === "fragment") candidate.source_fragment_id = "discordant-fragment";
  const anchor = { source_anchor_id: fragment, dce_version_id: scenario === "version" ? "old-version" : "synthetic-version", dce_document_id: "synthetic-document", extraction_id: "synthetic-extraction", fragment_ordinal: 1, source_sha256: "a".repeat(64), extractor_id: "synthetic-local", extractor_version: "1", fragment_sha256: "b".repeat(64), locator_state: "RESOLVED", locator: { kind: "pdf_page", coordinates: { page: 12, part: 1 } } };
  return { case_id: scenario === "case" ? "other-case" : caseId, work_label: `Dossier synthétique ${caseId}`, case_lifecycle: "PREPARATION", commercial_stage: "QUALIFICATION", dce_freshness: "CURRENT", availability: "AVAILABLE", dce: { dce_version_id: "synthetic-version", lifecycle: "ADMITTED", integrity: "VERIFIED", classification_readiness: "READY", analysis_readiness: "READY", source_received_at: "2026-10-16T10:00:00Z" }, counters: { total: 1, pending_human_confirmation: 1, confirmed: 0, review_required: 0, not_applicable: 0 }, requirements: [{ requirement_id: "synthetic-requirement", confirmation_revision: null, requirement_type: "CANDIDATURE_DOCUMENT", directive_signal: "REQUIRED_SIGNAL", confirmation_outcome: "PENDING_HUMAN_CONFIRMATION", uncertainty_status: "UNKNOWN", document_family: "RC", source_locator_label: "RC · page 12", source_anchor: anchor, structured_candidate: candidate }] };
}
const server = await createServer({
  configFile: false, root: fileURLToPath(new URL("../../", import.meta.url)),
  plugins: [react(), { name: "synthetic-rc-api", configureServer(server) {
    server.middlewares.use((req, res, next) => {
      const url = new URL(req.url, "http://127.0.0.1");
      res.setHeader("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self' ws://127.0.0.1:5179; img-src 'self' data:; font-src 'self'");
      if (url.pathname === "/__proof") { res.setHeader("Content-Type", "application/json"); res.end(JSON.stringify(requests)); return; }
      if (url.pathname === "/__release") { const batch = pending; pending = []; batch.forEach(send => send()); res.end("released"); return; }
      if (!url.pathname.startsWith("/synthetic/")) {
        if (url.pathname.startsWith("/api/")) { res.statusCode = 503; res.end("NO_LIVE_BACKEND"); return; }
        next(); return;
      }
      requests.push({ method: req.method, path: url.pathname, authorization: Boolean(req.headers.authorization), cookie: Boolean(req.headers.cookie) });
      res.setHeader("Content-Type", "application/json");
      if (req.method !== "GET") { res.statusCode = 405; res.end('{"detail":"READ_ONLY_SYNTHETIC"}'); return; }
      const match = /^\/synthetic\/([^/]+)\/api\/v1\/cases\/([^/]+)\/dce-reading$/.exec(url.pathname);
      if (!match) { res.statusCode = 404; res.end('{"detail":"SYNTHETIC_ROUTE_ABSENT"}'); return; }
      const [, scenario, caseId] = match;
      if (["409", "404"].includes(scenario)) { res.statusCode = Number(scenario); res.end('{"detail":"SYNTHETIC_CONFLICT_OR_ABSENCE"}'); return; }
      const send = () => res.end(JSON.stringify(fixture(caseId, scenario)));
      if (scenario === "delayed") pending.push(send); else send();
    });
  } }], server: { host: "127.0.0.1", port: 5179, strictPort: true },
});
await server.listen();
console.log("Synthetic RC fixture: http://127.0.0.1:5179/browser/rc-candidates/");
async function close() {
  if (process.env.SMARTAO_BROWSER_PROOF_LOG) await writeFile(process.env.SMARTAO_BROWSER_PROOF_LOG, JSON.stringify(requests, null, 2));
  await server.close(); process.exit(0);
}
process.on("SIGINT", close); process.on("SIGTERM", close);
