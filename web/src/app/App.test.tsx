import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import type {
  AssignedCase,
  CaseExecutionResults,
  CaseInterview,
  CaseResolution,
  DraftReport,
  CommandReceipt,
  ContractBaselineImpact,
  FreezeDecisionContextRequest,
  PatronDecisionDossier,
  PricingScenario,
} from "../shared/types";

const { authSessionGenerationRef, authTenantRef, authAccessTokenRef, authMfaRef, authProfileRef, authRoleRef, authSessionExpiredRef, authSessionRef, overridesRef } = vi.hoisted(() => ({
  authSessionGenerationRef: { current: 1 },
  authTenantRef: { current: "entreprise-test" },
  authAccessTokenRef: { current: "token-test" },
  authMfaRef: { current: true },
  authProfileRef: { current: null as "RESPONSABLE" | "EXPERT" | null },
  authRoleRef: { current: "PATRON_ADMIN" as string },
  authSessionExpiredRef: { current: false },
  authSessionRef: { current: true },
  overridesRef: { current: {} as Record<string, unknown> },
}));

vi.mock("../infrastructure/api", () => ({
  createApiClient: () =>
    new Proxy({ ...overridesRef.current } as Record<string, unknown>, {
      get(target, prop) {
        if (typeof prop === "string" && prop in target) return target[prop];
        return () => Promise.resolve({});
      },
    }) as never,
}));

vi.mock("../features/auth/useAuthentication", () => {
  const defaults: Record<string, unknown> = {
    getEnterpriseCompany: () => Promise.reject(new Error("no company")),
    listAssignedCases: () => Promise.resolve([]),
    listPatronAssignments: () => Promise.resolve({ items: [] }),
    listPatronActions: () => Promise.resolve({ items: [], open_count: 0 }),
    listBoampObservations: () => Promise.resolve({ observations: [] }),
    getCaseDceReading: () => Promise.reject(Object.assign(new Error("missing DCE"), { status: 404 })),
    searchCaseKnowledge: () => Promise.resolve({ case_id: "case-1", query: "", results: [] }),
    listPricingScenarios: () => Promise.resolve([]),
    getCapabilityAssessments: () => Promise.resolve({proposals:[],gaps:[]}),
    getCapabilityCandidates: () => Promise.resolve([]),
    getCaseResolution: (caseId: string) => Promise.resolve({ case_id: caseId, work_label: "Affaire synthétique", coverage: "PARTIAL", items: [], economic_coverage: null }),
    listDecisionRiskRequirementLinks: () => Promise.resolve({ items: [], next_cursor: null }),
    listDceContractRiskSignals: () => Promise.resolve({ case_id: "case-1", items: [] }),
    listRegulatoryProfiles: () => Promise.resolve({ case_id: "case-1", items: [] }),
    crossCctpPricing: () => Promise.resolve({ case_id: "case-1", items: [] }),
    listDocumentContradictions: () => Promise.resolve({ case_id: "case-1", items: [] }),
    reconcileDecisionPricing: () => Promise.resolve({ link_id: "", search: "", items: [] }),
    getDecisionDossier: () => Promise.reject(Object.assign(new Error("missing"), { status: 404 })),
  };
  const api = new Proxy(defaults, {
    get(target, prop) {
      if (typeof prop === "string" && prop in overridesRef.current) return overridesRef.current[prop];
      if (typeof prop === "string" && prop in target) return target[prop];
      return () => Promise.resolve({});
    },
  }) as never;
  return {
    useAuthentication: () => ({
      accessToken: authAccessTokenRef.current,
      sessionGeneration: authSessionGenerationRef.current,
      currentActor: authSessionRef.current ? {
        actor_id: "actor-1",
        identity_id: "identity-1",
        tenant_slug: authTenantRef.current,
        actor_kind: authRoleRef.current,
        operational_profile: authProfileRef.current,
        membership_state: "ACTIVE",
        mfa_verified: authMfaRef.current,
      } : null,
      isRestoring: false,
      sessionExpired: authSessionExpiredRef.current,
      hasSession: authSessionRef.current,
      isAuthenticated: authSessionRef.current && authMfaRef.current,
      api,
      login: vi.fn(),
      refreshActor: vi.fn(),
      logout: vi.fn(),
    }),
  };
});

vi.mock("../features/connection/useBackendReadiness", () => ({
  useBackendReadiness: () => ({
    backendReadiness: {
      status: "ok",
      service: "smart-ao-v8",
      checks: { database: "ok", clamav: "ok" },
    },
    backendReadinessState: "ready",
    checkBackendReadiness: vi.fn(),
  }),
}));

const CASE: AssignedCase = {
  case_id: "case-1",
  work_label: "Extension de collège",
  case_lifecycle: "PREPARATION",
  commercial_stage: "QUALIFICATION",
  dce_availability: "AVAILABLE",
  consultation_id: null,
  applicable_dce_version_id: null,
};
const c08HttpProof = (globalThis as typeof globalThis & { __smartAoC08Proof?: { complete: DraftReport; incomplete: DraftReport; scenarios_complete: PricingScenario[]; scenarios_incomplete: PricingScenario[] } }).__smartAoC08Proof;

function baseOverrides(): Record<string, unknown> {
  return {
    getEnterpriseCompany: () => Promise.reject(new Error("no company")),
    listAssignedCases: () => Promise.resolve([CASE]),
    listPatronAssignments: () => Promise.resolve({ items: [] }),
    listPatronActions: () => Promise.resolve({ items: [], open_count: 0 }),
    listBoampObservations: () => Promise.resolve({ observations: [] }),
    getCaseDceReading: () => Promise.reject(Object.assign(new Error("missing DCE"), { status: 404 })),
    searchCaseKnowledge: () => Promise.resolve({ case_id: "case-1", query: "", results: [] }),
    listPricingScenarios: () => Promise.resolve([]),
    getCaseResolution: (caseId: string) => Promise.resolve({ case_id: caseId, work_label: "Affaire synthétique", coverage: "PARTIAL", items: [], economic_coverage: null }),
    listDecisionRiskRequirementLinks: () => Promise.resolve({ items: [], next_cursor: null }),
    listDceContractRiskSignals: () => Promise.resolve({ case_id: "case-1", items: [] }),
    listRegulatoryProfiles: () => Promise.resolve({ case_id: "case-1", items: [] }),
    crossCctpPricing: () => Promise.resolve({ case_id: "case-1", items: [] }),
    listDocumentContradictions: () => Promise.resolve({ case_id: "case-1", items: [] }),
    reconcileDecisionPricing: () => Promise.resolve({ link_id: "", search: "", items: [] }),
    getDecisionDossier: () =>
      Promise.reject(Object.assign(new Error("ignored"), { status: 404 })),
  };
}

async function renderApp() {
  let view: ReturnType<typeof render> | undefined;
  await act(async () => {
    view = render(<App />);
    await new Promise((resolve) => setTimeout(resolve, 80));
  });
  const confirmation = screen.queryByRole("button", { name: "Confirmer et continuer" });
  if (confirmation) {
    fireEvent.click(confirmation);
    await act(async () => { await new Promise((resolve) => setTimeout(resolve, 80)); });
  }
  return view!;
}

function connect() {
  // The auth hook is connected by the test mock; no bearer-entry flow is allowed.
}

function delayedRejection(error: Error, delayMs: number): Promise<never> {
  return new Promise((_, reject) => {
    setTimeout(() => reject(error), delayMs);
  });
}

describe("App readiness integration", () => {
  beforeEach(() => {
    window.localStorage.clear();
    authRoleRef.current = "PATRON_ADMIN";
    authProfileRef.current = null;
    authMfaRef.current = true;
    authSessionExpiredRef.current = false;
    authSessionRef.current = true;
    authAccessTokenRef.current = "token-test";
    authSessionGenerationRef.current = 1;
    authTenantRef.current = "entreprise-test";
    overridesRef.current = {};
  });

  it("clears the submission manifest when the authenticated tenant changes", async () => {
    const hash = "d".repeat(64);
    overridesRef.current = {
      ...baseOverrides(),
      getSubmissionPackageManifest: () => Promise.resolve({ submission_package_id: "package-private", package_version: 1, state: "PRET_CONTROLE", manifest_sha256: hash, manifest: {}, authorization_status: "NOT_AUTHORIZED", external_submission: "NOT_PERFORMED" }),
    };
    const view = await renderApp();
    fireEvent.change(screen.getByLabelText("Identifiant du paquet"), { target: { value: "package-private" } });
    fireEvent.click(screen.getByRole("button", { name: /Prévisualiser le manifeste/ }));
    expect(await screen.findByText(new RegExp(hash))).toBeVisible();
    authTenantRef.current = "entreprise-autre";
    authSessionGenerationRef.current += 1;
    await act(async () => { view.rerender(<App />); });
    expect(screen.queryByText(new RegExp(hash))).not.toBeInTheDocument();
    expect(screen.getByLabelText("Identifiant du paquet")).toHaveValue("");
  });

  it("does not publish a late P5 error into a different tenant session", async () => {
    let failAuthorization: ((error: Error) => void) | undefined;
    const authorize = vi.fn().mockImplementation(() => new Promise((_resolve, reject) => { failAuthorization = reject; }));
    overridesRef.current = {
      ...baseOverrides(),
      authorizeSubmissionPackage: authorize,
      getSubmissionPackageManifest: () => Promise.resolve({ submission_package_id: "package-private", package_version: 1, state: "PRET_CONTROLE", manifest_sha256: "d".repeat(64), manifest: {}, authorization_status: "NOT_AUTHORIZED", external_submission: "NOT_PERFORMED" }),
    };
    const view = await renderApp();
    fireEvent.change(screen.getByLabelText("Identifiant du paquet"), { target: { value: "package-private" } });
    fireEvent.click(screen.getByRole("button", { name: /Prévisualiser le manifeste/ }));
    await screen.findByText(new RegExp("d".repeat(64)));
    fireEvent.click(screen.getByRole("button", { name: /Autoriser la remise humaine/ }));
    expect(authorize).toHaveBeenCalledOnce();
    authTenantRef.current = "entreprise-autre";
    authSessionGenerationRef.current += 1;
    await act(async () => { view.rerender(<App />); });
    await act(async () => { failAuthorization?.(new Error("PRIVATE_RESPONSE_FROM_PREVIOUS_TENANT")); });
    expect(screen.queryByText("PRIVATE_RESPONSE_FROM_PREVIOUS_TENANT")).not.toBeInTheDocument();
    expect(screen.getByLabelText("Identifiant du paquet")).toHaveValue("");
  });

  it("clears an already published P5 message when the authenticated scope changes", async () => {
    const marker = "PRIVATE_STORED_FOR_PREVIOUS_TENANT";
    overridesRef.current = {
      ...baseOverrides(),
      listAssignedCases: () => Promise.resolve([{ ...CASE, consultation_id: "consultation-1" }]),
      getConsultation: () => new Promise(() => {}),
      authorizeSubmissionPackage: vi.fn().mockRejectedValue(new Error(marker)),
      getSubmissionPackageManifest: () => Promise.resolve({ submission_package_id: "package-private", package_version: 1, state: "PRET_CONTROLE", manifest_sha256: "d".repeat(64), manifest: {}, authorization_status: "NOT_AUTHORIZED", external_submission: "NOT_PERFORMED" }),
    };
    const view = await renderApp();
    fireEvent.change(screen.getByLabelText("Identifiant du paquet"), { target: { value: "package-private" } });
    fireEvent.click(screen.getByRole("button", { name: /Prévisualiser le manifeste/ }));
    await screen.findByText(new RegExp("d".repeat(64)));
    fireEvent.click(screen.getByRole("button", { name: /Autoriser la remise humaine/ }));
    expect(await screen.findByText(marker)).toBeVisible();
    authTenantRef.current = "entreprise-autre";
    authSessionGenerationRef.current += 1;
    await act(async () => { view.rerender(<App />); });
    expect(screen.queryByText(marker)).not.toBeInTheDocument();
  });

  it("affiche l’état backend et les dépendances dans la configuration API", async () => {
    await renderApp();

    const sessionButton = screen.getByRole("button", { name: /Session/ });
    fireEvent.click(sessionButton);

    const dialog = screen.getByRole("dialog", { name: "Connexion au backend" });
    expect(dialog).toBeVisible();
    expect(dialog).toHaveAttribute("aria-describedby", "connection-modal-description");
    expect(
      within(dialog).getByRole("button", { name: "Fermer la configuration de connexion" }),
    ).toBeVisible();
    const readiness = within(dialog).getByRole("status");
    expect(readiness).toHaveTextContent("Backend prêt");
    expect(readiness).toHaveTextContent("PostgreSQL : ok");
    expect(readiness).toHaveTextContent("ClamAV : ok");

    fireEvent.keyDown(document, { key: "Escape" });
    expect(screen.queryByRole("dialog", { name: "Connexion au backend" })).toBeNull();
    await waitFor(() => expect(document.activeElement).toBe(sessionButton));
  });

  it("expose C12 résultat/passation dans la navigation Patron", async () => {
    await renderApp();
    expect(screen.getByRole("button", { name: /Résultat et passation/ })).toBeVisible();
  });

  it("affiche les points À résoudre de l'affaire dans la revue existante", async () => {
    Object.defineProperty(HTMLElement.prototype, "scrollIntoView", { configurable: true, value: vi.fn() });
    const projection: CaseResolution = {
      case_id: CASE.case_id,
      work_label: CASE.work_label,
      coverage: "PARTIAL",
      items: [{ item_id: "unknown-1", item_kind: "UNKNOWN", native_state: "UNKNOWN", source_refs: ["fixture://notice/1"], resolution_owner: null, next_action: "REVIEW_UNKNOWN", due_at: null, impact: "Périmètre à vérifier" }],
      economic_coverage: null,
    };
    const getCaseResolution = vi.fn().mockResolvedValue(projection);
    overridesRef.current = { ...baseOverrides(), getCaseResolution };
    await renderApp();
    fireEvent.click(screen.getByRole("button", { name: /Revue/ }));

    const panel = await screen.findByRole("region", { name: "À résoudre" });
    expect(within(panel).getByText("Couverture partielle")).toBeVisible();
    expect(within(panel).getByText("UNKNOWN")).toBeVisible();
    expect(within(panel).getByText("Périmètre à vérifier")).toBeVisible();
    expect(getCaseResolution).toHaveBeenCalledWith(CASE.case_id);
  });

  it("lit les évaluations documentaires de l’Affaire Collaborateur sans identifiant privé", async () => {
    authRoleRef.current = "COLLABORATEUR";
    const getCapabilityAssessments = vi.fn().mockResolvedValue({proposals:[{case_id:CASE.case_id,source_evidence_state:"CURRENT",source_evidence_evaluated_at:"2026-10-08T09:00:00Z",source_locator:"PRIVATE_LOCATOR",proposal_id:"PRIVATE_ID"}],gaps:[]});
    overridesRef.current = {...baseOverrides(),getCapabilityAssessments};
    await renderApp();
    const panel = await screen.findByRole("region", {name:"Éligibilité documentaire des moyens"});
    await waitFor(()=>expect(within(panel).getByText("CURRENT")).toBeVisible());
    expect(getCapabilityAssessments).toHaveBeenCalledWith(CASE.case_id);
    expect(panel.textContent).not.toMatch(/PRIVATE_LOCATOR|PRIVATE_ID/);
  });

  it.each(["PATRON_ADMIN","PATRON_DELEGATE","MFA_PENDING"])("ne lit pas les évaluations documentaires pour %s",async(context)=>{
    authRoleRef.current = context === "MFA_PENDING" ? "COLLABORATEUR" : context;
    if(context === "MFA_PENDING") authMfaRef.current = false;
    const getCapabilityAssessments = vi.fn();
    overridesRef.current = {...baseOverrides(),getCapabilityAssessments};
    await renderApp();
    expect(getCapabilityAssessments).not.toHaveBeenCalled();
    expect(screen.queryByRole("region", {name:"Éligibilité documentaire des moyens"})).toBeNull();
  });

  it("rend les candidats de moyens en lecture sans exposer leurs UUID", async () => {
    authRoleRef.current = "COLLABORATEUR";
    const getCapabilityCandidates = vi.fn().mockResolvedValue([{
      capability_id: "PRIVATE_CAPABILITY_ID", capability_kind: "EQUIPMENT", name: "Levage synthétique",
      version_id: "PRIVATE_VERSION_ID", version_number: 2, title: "Version chantier",
      valid_from: "2026-10-01T00:00:00Z", valid_until: null, validity_state: "CURRENT",
      source_evidence_state: "UNKNOWN", evaluated_at: "2026-10-08T09:00:00Z",
      proof_document_ids: ["PRIVATE_PROOF_ID"], summary: "PRIVATE SUMMARY",
    }]);
    const createProposal = vi.fn();
    overridesRef.current = { ...baseOverrides(), getCapabilityCandidates, proposeCapability: createProposal };
    await renderApp();
    const panel = await screen.findByRole("region", { name: "Moyens que vous pouvez proposer" });
    expect(within(panel).getByText("Levage synthétique")).toBeVisible();
    expect(within(panel).getByText(/État documentaire : UNKNOWN/)).toBeVisible();
    expect(panel.textContent).not.toMatch(/PRIVATE_CAPABILITY_ID|PRIVATE_VERSION_ID|PRIVATE_PROOF_ID|PRIVATE SUMMARY/);
    expect(getCapabilityCandidates).toHaveBeenCalledWith(CASE.case_id);
    expect(createProposal).not.toHaveBeenCalled();
  });

  it.each(["PATRON_ADMIN", "PATRON_DELEGATE", "MFA_PENDING"])("does not read collaborator candidates for %s", async (context) => {
    authRoleRef.current = context === "MFA_PENDING" ? "COLLABORATEUR" : context;
    if (context === "MFA_PENDING") authMfaRef.current = false;
    const getCapabilityCandidates = vi.fn();
    overridesRef.current = { ...baseOverrides(), getCapabilityCandidates };
    await renderApp();
    expect(getCapabilityCandidates).not.toHaveBeenCalled();
    expect(screen.queryByRole("region", { name: "Moyens que vous pouvez proposer" })).toBeNull();
  });

  it("affiche la projection Collaborateur sans couverture économique privée", async () => {
    authRoleRef.current = "COLLABORATEUR";
    authProfileRef.current = "RESPONSABLE";
    const economic = { state: "UNKNOWN" as const, source_refs: [], note: "PRIVATE ECONOMIC NOTE" };
    const getCaseResolution = vi.fn().mockResolvedValue({
      case_id: CASE.case_id, work_label: CASE.work_label, coverage: "PARTIAL",
      items: [{ item_id: "blocker-1", item_kind: "TASK_BLOCKER", native_state: "OPEN", source_refs: ["fixture://task/assigned"], resolution_owner: "COLLABORATEUR", next_action: "RESOLVE_TASK_BLOCKER", due_at: null, impact: null }],
      economic_coverage: { assumptions: economic, quote_validity: economic, capacity: economic, financing: economic },
    } satisfies CaseResolution);
    overridesRef.current = { ...baseOverrides(), getCaseResolution };
    await renderApp();
    const panel = await screen.findByRole("region", { name: "À résoudre" });
    expect(within(panel).getByRole("heading", { name: "Blocages de tâche" })).toBeVisible();
    expect(screen.queryByText("PRIVATE ECONOMIC NOTE")).toBeNull();
    expect(screen.queryByLabelText("Couverture économique de l’affaire")).toBeNull();
  });

  it.each(["PATRON_DELEGATE", "MFA_PENDING"])("ne lit pas À résoudre pour le contexte refusé %s", async (context) => {
    if (context === "MFA_PENDING") authMfaRef.current = false;
    else authRoleRef.current = context;
    const getCaseResolution = vi.fn();
    overridesRef.current = { ...baseOverrides(), getCaseResolution };
    await renderApp();
    expect(getCaseResolution).not.toHaveBeenCalled();
    expect(screen.queryByRole("region", { name: "À résoudre" })).toBeNull();
  });

  it("ignore une réponse Patron tardive après passage au contexte Collaborateur", async () => {
    let resolvePatron!: (value: CaseResolution) => void;
    const patronPending = new Promise<CaseResolution>((resolve) => { resolvePatron = resolve; });
    const collaborator: CaseResolution = { case_id: CASE.case_id, work_label: CASE.work_label, coverage: "PARTIAL", economic_coverage: null, items: [{ item_id: "task-1", item_kind: "TASK_BLOCKER", native_state: "OPEN", source_refs: [], resolution_owner: null, next_action: "RESOLVE_TASK_BLOCKER", due_at: null, impact: null }] };
    const getCaseResolution = vi.fn().mockReturnValueOnce(patronPending).mockResolvedValue(collaborator);
    overridesRef.current = { ...baseOverrides(), getCaseResolution };
    const view = await renderApp();
    authRoleRef.current = "COLLABORATEUR";
    authProfileRef.current = "RESPONSABLE";
    view.rerender(<App />);
    const panel = await screen.findByRole("region", { name: "À résoudre" });
    await waitFor(() => expect(within(panel).getByRole("heading", { name: "Blocages de tâche" })).toBeVisible());
    await act(async () => resolvePatron({ ...collaborator, items: [{ ...collaborator.items[0], item_kind: "RISK", impact: "CONFIDENTIAL PATRON ITEM" }] }));
    expect(within(panel).queryByText("CONFIDENTIAL PATRON ITEM")).toBeNull();
    expect(within(panel).queryByRole("heading", { name: "Risques" })).toBeNull();
  });

  it("invalide la lecture lors du remplacement de session pour le même acteur", async () => {
    let resolveOldSession!: (value: CaseResolution) => void;
    const pending = new Promise<CaseResolution>((resolve) => { resolveOldSession = resolve; });
    const current: CaseResolution = { case_id: CASE.case_id, work_label: CASE.work_label, coverage: "PARTIAL", economic_coverage: null, items: [{ item_id: "current-1", item_kind: "UNKNOWN", native_state: "UNKNOWN", source_refs: [], resolution_owner: null, next_action: "REVIEW_UNKNOWN", due_at: null, impact: "CURRENT SESSION ITEM" }] };
    const getCaseResolution = vi.fn().mockReturnValueOnce(pending).mockResolvedValue(current);
    overridesRef.current = { ...baseOverrides(), getCaseResolution };
    const view = await renderApp();
    authAccessTokenRef.current = "token-test-replacement";
    authSessionGenerationRef.current++;
    view.rerender(<App />);
    await waitFor(() => expect(getCaseResolution).toHaveBeenCalledTimes(2));
    await act(async () => resolveOldSession({ ...current, items: [{ ...current.items[0], impact: "OLD SESSION ITEM" }] }));
    const panel = screen.getByRole("region", { name: "À résoudre" });
    expect(within(panel).getByText("CURRENT SESSION ITEM")).toBeVisible();
    expect(within(panel).queryByText("OLD SESSION ITEM")).toBeNull();
  });

  it.skipIf(!c08HttpProof?.scenarios_complete)("relit la provenance PostgreSQL/HTTP dans l’application Patron puis la masque au changement de rôle", async () => {
    const scenarios = c08HttpProof!.scenarios_complete;
    const sourceCase = { ...CASE, case_id: scenarios[0].case_id };
    const listPricingScenarios = vi.fn().mockResolvedValue(scenarios);
    overridesRef.current = { ...baseOverrides(), listAssignedCases: () => Promise.resolve([sourceCase]), listPricingScenarios };
    const view = await renderApp();
    expect(await screen.findByText(`Source ${scenarios[0].source_snapshot_id} · révision 6`)).toBeInTheDocument();
    expect(screen.getByText("Marge 32.99 % · DRAFT")).toBeInTheDocument();
    expect(listPricingScenarios).toHaveBeenCalledWith(sourceCase.case_id);
    authRoleRef.current = "COLLABORATEUR";
    view.rerender(<App />);
    expect(screen.queryByRole("heading", { name: "Options de prix" })).toBeNull();
    expect(screen.queryByText(`Source ${scenarios[0].source_snapshot_id} · révision 6`)).toBeNull();
  });

  it.each(["COLLABORATEUR", "PATRON_DELEGATE"])("ne lit ni ne rend les scénarios privés pour %s", async (role) => {
    authRoleRef.current = role;
    const listPricingScenarios = vi.fn();
    overridesRef.current = { ...baseOverrides(), listPricingScenarios };
    await renderApp();
    expect(screen.queryByRole("heading", { name: "Options de prix" })).toBeNull();
    expect(listPricingScenarios).not.toHaveBeenCalled();
  });

  it.each(["COLLABORATEUR", "PATRON_DELEGATE"])("ne lit ni n’expose les rapprochements privés pour %s", async (role) => {
    authRoleRef.current = role;
    const listPartnerOfferLineComparisons = vi.fn();
    overridesRef.current = { ...baseOverrides(), listPartnerOfferLineComparisons };
    await renderApp();

    expect(screen.queryByRole("region", { name: "Rapprochements de lignes C08" })).toBeNull();
    expect(listPartnerOfferLineComparisons).not.toHaveBeenCalled();
  });

  it("ignore le scénario tardif d’une ancienne génération de session", async () => {
    let resolveOld!: (value: PricingScenario[]) => void;
    const old = new Promise<PricingScenario[]>((resolve) => { resolveOld = resolve; });
    const current: PricingScenario = { scenario_id: "local-synthetic", case_id: CASE.case_id, scenario_key: "CURRENT SCENARIO", scenario_type: "BASE", version: 1, state: "DRAFT", assumptions: {}, sales_total_minor: 100, total_cost_minor: 0, gross_margin_minor: 100, gross_margin_rate_bps: 10000, source_snapshot_id: "synthetic-source", source_snapshot_revision: 1, source_basis_state: "DECLARED_COMPLETE", source_basis_reason: null, currency_code: "EUR" };
    const listPricingScenarios = vi.fn().mockReturnValueOnce(old).mockResolvedValueOnce([current]);
    overridesRef.current = { ...baseOverrides(), listPricingScenarios };
    const view = await renderApp();
    authSessionGenerationRef.current++;
    view.rerender(<App />);
    await waitFor(() => expect(listPricingScenarios).toHaveBeenCalledTimes(2));
    await act(async () => resolveOld([{ ...current, scenario_key: "OLD SCENARIO" }]));
    expect(await screen.findByText("CURRENT SCENARIO · v1")).toBeInTheDocument();
    expect(screen.queryByText("OLD SCENARIO · v1")).toBeNull();
  });

  it.each(["COLLABORATEUR", "PATRON_DELEGATE"])("masque le brouillon FINANCIAL_PRIVATE pour %s", async (role) => {
    authRoleRef.current = role;
    const getDraft = vi.fn();
    overridesRef.current = { ...baseOverrides(), getDraft };
    await renderApp();
    expect(screen.queryByRole("heading", { name: "Brouillon financier" })).toBeNull();
    expect(getDraft).not.toHaveBeenCalled();
  });

  it("publie humainement le rapport exact puis masque la source publiée au changement de rôle", async () => {
    const report: DraftReport = { report_id: "browser-source", case_id: CASE.case_id, status: "DRAFT", aggregate_revision: 2, currency_code: "EUR", calculated_at: "2026-10-07T10:00:00Z", ruleset_version: 1, lines: [], summary: { sales_total_minor: 0, direct_cost_total_minor: 0, overhead_total_minor: 0, subcontracting_total_minor: 0, contingency_total_minor: 0, gross_margin_minor: 0, gross_margin_rate_bps: 0, forecast_cashflow_minor: 0 } };
    const publishFinancialReport = vi.fn().mockImplementation(async (_case, reportId, input) => ({ status: "SUCCEEDED", command_id: input.command_id, idempotency_key: input.idempotency_key, result_code: "FINANCIAL_REPORT_PUBLISHED", aggregate_refs: [{ aggregate_type: "FinancialReportSnapshot", aggregate_id: reportId, aggregate_revision: 3 }], event_ids: ["synthetic-event"], replayed: false }));
    const getPublishedFinancialReport = vi.fn().mockResolvedValue({ ...report, status: "PUBLISHED", aggregate_revision: 3, margin_calculation: { state: "UNKNOWN", basis: "DECLARED_BASE_CATEGORIES", missing_categories: ["SALES"], basis_line_ids: [], total_cost_minor: null, gross_margin_minor: null, gross_margin_rate_bps: null, unknown_reason: "MISSING_BASE_CATEGORY", rate_unknown_reason: null } });
    overridesRef.current = { ...baseOverrides(), getDraft: vi.fn().mockResolvedValue(report), publishFinancialReport, getPublishedFinancialReport };
    const view = await renderApp();
    fireEvent.change(screen.getByLabelText("Identifiant du rapport"), { target: { value: report.report_id } });
    fireEvent.click(screen.getByRole("button", { name: /Lire le brouillon/ }));
    const publishButton = await screen.findByRole("button", { name: "Publier et figer ce rapport" });
    expect(publishFinancialReport).not.toHaveBeenCalled();
    fireEvent.click(publishButton);
    expect(await screen.findByText("browser-source · révision 3")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Rapport financier publié" })).toBeInTheDocument();
    expect(publishFinancialReport).toHaveBeenCalledOnce();
    expect(getPublishedFinancialReport).toHaveBeenCalledWith(CASE.case_id, report.report_id);
    authRoleRef.current = "COLLABORATEUR";
    view.rerender(<App />);
    expect(screen.queryByText("browser-source · révision 3")).toBeNull();
    expect(screen.queryByRole("heading", { name: "Rapport financier publié" })).toBeNull();
  });

  it("conserve une écriture C08 en cours lors du renouvellement de jeton de la même session", async () => {
    let acknowledge!: (value: CommandReceipt) => void;
    const createDraft = vi.fn().mockReturnValue(new Promise<CommandReceipt>((resolve) => { acknowledge = resolve; }));
    const getDraft = vi.fn().mockResolvedValue({ report_id: "report-1", case_id: CASE.case_id, status: "DRAFT", aggregate_revision: 0, currency_code: "EUR", calculated_at: "2026-10-05T10:00:00Z", ruleset_version: 1, lines: [], summary: { sales_total_minor: 0, direct_cost_total_minor: 0, overhead_total_minor: 0, subcontracting_total_minor: 0, contingency_total_minor: 0, gross_margin_minor: 0, gross_margin_rate_bps: 0, forecast_cashflow_minor: 0 } } satisfies DraftReport);
    overridesRef.current = { ...baseOverrides(), createDraft, getDraft };
    const view = await renderApp();
    fireEvent.click(screen.getByRole("button", { name: /Nouveau brouillon/ }));
    authAccessTokenRef.current = "token-test-renewed";
    view.rerender(<App />);
    await act(async () => acknowledge({ status: "SUCCEEDED", command_id: "fixture-command", idempotency_key: "fixture-intent", result_code: "FINANCIAL_REPORT_DRAFT_CREATED", aggregate_refs: [{ aggregate_type: "FinancialReportSnapshot", aggregate_id: "report-1", aggregate_revision: 0 }], event_ids: [], replayed: false }));
    await waitFor(() => expect(getDraft).toHaveBeenCalledWith(CASE.case_id, "report-1"));
    expect(screen.getByText("DRAFT · Révision 0")).toBeVisible();
  });

  it.skipIf(!c08HttpProof)("projette les réponses HTTP/PostgreSQL synthétiques incomplète puis complète dans C08 Patron", async () => {
    const incomplete = c08HttpProof!.incomplete;
    const complete = c08HttpProof!.complete;
    const getDraft = vi.fn().mockResolvedValueOnce(incomplete).mockResolvedValueOnce(complete);
    overridesRef.current = { ...baseOverrides(), listAssignedCases: () => Promise.resolve([{ ...CASE, case_id: complete.case_id, work_label: "Affaire C08 synthétique" }]), getDraft };
    await renderApp();
    fireEvent.change(screen.getByLabelText("Identifiant du rapport"), { target: { value: complete.report_id } });
    fireEvent.click(screen.getByRole("button", { name: /Lire le brouillon/ }));
    await screen.findByText("Taux UNKNOWN");
    expect(screen.getByText(/postes de base absents/)).toBeVisible();
    fireEvent.click(screen.getByRole("button", { name: /Lire le brouillon/ }));
    expect(await screen.findByText("32.99 % du chiffre d’affaires")).toBeVisible();
    expect(screen.getByText(/330,00/)).toBeVisible();
    expect(getDraft).toHaveBeenCalledWith(complete.case_id, complete.report_id);
    expect(screen.queryByText("Taux UNKNOWN")).toBeNull();
  });

  it("place la revue d’entretien PUX-19 dans C13 et distingue USABLE d’EXPIRED", async () => {
    Object.defineProperty(HTMLElement.prototype, "scrollIntoView", { configurable: true, value: vi.fn() });
    const interviews: CaseInterview[] = [
      { interview_id: "usable-1", case_id: "case-1", held_on: "2026-09-29", source_locator: "fixture://interview/usable", rationale: "Entretien à réutiliser sous conditions", expires_on: "2026-10-01", snapshot: { rex: [{ rex_id: "rex-1", lot_reference: "01", motif: "UNKNOWN", scope: "CASE_ONLY", validation: "PENDING" }] }, status: "USABLE", created_at: "2026-09-29T10:00:00Z" },
      { interview_id: "expired-1", case_id: "case-1", held_on: "2026-03-01", source_locator: "fixture://interview/expired", rationale: "Entretien arrivé à expiration", expires_on: "2026-03-02", snapshot: { rex: [] }, status: "EXPIRED", created_at: "2026-03-01T10:00:00Z" },
    ];
    overridesRef.current = {
      ...baseOverrides(),
      listCaseInterviews: vi.fn(async () => ({ case_id: "case-1", interviews })),
      listCaseTeachingSources: vi.fn(async () => ({
        case_id: "case-1",
        sources: [{
          source_case_id: "source-case-1",
          source_case_label: "Affaire source",
          source_interview_id: "interview-source-1",
          source_rex_id: "rex-source-1",
          held_on: "2026-09-29",
          source_locator: "entretien://source/1",
          interview_rationale: "Revue d’enseignement",
          expires_on: "2026-10-01",
          source_validity: "USABLE",
          snapshot: { rex_id: "rex-source-1", lot_reference: "01", motif: "KNOWN", scope: "ENTERPRISE_PATTERN", validation: "APPROVED", observation: "Coordination à vérifier", consequence: "Risque de retard", follow_up: "Contrôle au démarrage", source_locator: "dce://source/4" },
          can_assess: true,
          block_reason: null,
        }],
      })),
      listCaseTeachingApplicabilities: vi.fn(async () => ({ case_id: "case-1", applicabilities: [] })),
    };
    await renderApp();

    fireEvent.click(screen.getByRole("button", { name: /Entreprise/ }));
    expect(await screen.findByRole("heading", { name: "Entretien du 2026-09-29" })).toBeVisible();
    expect(screen.getByText(/USABLE · réemploi sous conditions jusqu’au 2026-10-01/)).toBeVisible();
    expect(screen.getByText(/EXPIRED · réemploi à réinterroger/)).toBeVisible();
    expect(screen.getByText(/Snapshot à date : 1 enseignement capturé/)).toBeVisible();
    expect(await screen.findByText(/Coordination à vérifier/)).toBeVisible();
    expect(screen.getByText(/Validité : USABLE · portée : ENTERPRISE_PATTERN · revue source : APPROVED/)).toBeVisible();
    expect(screen.getByText(/ne transfère aucun contenu, ne prolonge pas la validité/)).toBeVisible();

    const c12 = screen.getByRole("region", { name: "Résultats et passation C12" });
    expect(within(c12).queryByText(/Entretien du 2026-09-29/)).toBeNull();
  });

  it("charge C09 seulement à l’ouverture et distingue un reçu d’un engagement Patron", async () => {
    const listPartnerOfferPrices = vi.fn();
    const listCasePartnerEvents = vi.fn(async () => ({
      case_id: "case-1",
      can_request: true,
      can_receive: true,
      can_declare_engagement: false,
      events: [{
        event_id: "partner-receipt-1",
        partner_id: "partner-1",
        case_id: "case-1",
        revision: 1,
        event_type: "RECEIVED" as const,
        partner_kind: "SUBCONTRACTOR" as const,
        partner_label: "Électricité déclarée",
        related_event_id: null,
        source_locator: "offer://received/lot-01",
        rationale: "Offre reçue, revue à poursuivre.",
        valid_until: null,
        validity_at_recording: "UNKNOWN" as const,
        validity_current: "UNKNOWN" as const,
        exclusions_state: "UNKNOWN" as const,
        exclusions: [],
        mandate_state: "NOT_APPLICABLE" as const,
        mandate_source_locator: null,
        actor_id: "actor-1",
        recorded_at: "2026-09-30T12:00:00Z",
      }],
    }));
    overridesRef.current = { ...baseOverrides(), listCasePartnerEvents, listPartnerOfferPrices };
    await renderApp();
    expect(listCasePartnerEvents).not.toHaveBeenCalled();

    fireEvent.click(screen.getByRole("button", { name: /Partenaires C09/ }));

    await waitFor(() => expect(listCasePartnerEvents).toHaveBeenCalledWith("case-1"), { timeout: 10000 });
    expect(await screen.findByText(/RECEIVED · preuve reçue/)).toBeVisible();
    expect(screen.getByText(/Mandat : NOT_APPLICABLE/)).toBeVisible();
    expect(screen.getByText(/reçu ≠ engagé/)).toBeVisible();
    expect(listCasePartnerEvents).toHaveBeenCalledWith("case-1");
    expect(listPartnerOfferPrices).not.toHaveBeenCalled();
    expect(screen.queryByText(/ENGAGEMENT_DECLARED · acte humain Patron/)).toBeNull();
  });

  it("attend MFA et confirmation du contexte avant de lire les résultats C12", async () => {
    window.location.hash = "case=case-1&section=results";
    authMfaRef.current = false;
    const listCaseExecutionResults = vi.fn(async () => ({
      case_id: "case-1",
      lot_references: ["01"],
      results: [],
    } satisfies CaseExecutionResults));
    overridesRef.current = { ...baseOverrides(), listCaseExecutionResults };

    let view: ReturnType<typeof render> | undefined;
    await act(async () => {
      view = render(<App />);
      await new Promise((resolve) => setTimeout(resolve, 80));
    });
    expect(screen.getByRole("heading", { name: "Validez votre second facteur" })).toBeVisible();
    expect(listCaseExecutionResults).not.toHaveBeenCalled();

    authMfaRef.current = true;
    await act(async () => {
      view!.rerender(<App />);
      await new Promise((resolve) => setTimeout(resolve, 80));
    });
    expect(screen.getByRole("heading", { name: "Confirmez votre contexte" })).toBeVisible();
    expect(listCaseExecutionResults).not.toHaveBeenCalled();

    fireEvent.click(screen.getByRole("button", { name: "Confirmer et continuer" }));
    await waitFor(() => expect(listCaseExecutionResults).toHaveBeenCalledWith("case-1"));
    window.location.hash = "";
  });

  it("exécute le parcours C12 résultat par lot → commande → P6 → P7 depuis l’application", async () => {
    Object.defineProperty(HTMLElement.prototype, "scrollIntoView", { configurable: true, value: vi.fn() });
    const now = "2026-09-29T12:00:00Z";
    let data: CaseExecutionResults = { case_id: "case-1", lot_references: ["01"], results: [] };
    const receipt = { status: "SUCCEEDED", result_code: "RECORDED", aggregate_refs: [], event_ids: [], replayed: false };
    overridesRef.current = {
      ...baseOverrides(),
      listCaseExecutionResults: vi.fn(async () => data),
      recordCaseOutcome: vi.fn(async (input: Record<string, unknown>) => {
        data = { ...data, results: [{
          outcome_id: String(input.outcome_id), lot_reference: String(input.lot_reference), outcome: "WON",
          source_locator: String(input.source_locator), reservations: [], unknown_reason: null,
          actor_id: "patron-1", recorded_at: now, transmission: null, order: null, p6: null, p7: null,
        }] };
        return receipt;
      }),
      recordCaseOrder: vi.fn(async (input: Record<string, unknown>) => {
        data = { ...data, results: data.results.map((item) => ({
          ...item,
          order: { order_id: String(input.order_id), outcome_id: String(input.outcome_id), decision: "ACCEPTED",
            source_locator: item.source_locator ?? "", reservations: [], rationale: String(input.rationale), actor_id: "patron-1", recorded_at: now },
        })) };
        return receipt;
      }),
      recordCaseP6Control: vi.fn(async (_orderId: string, input: Record<string, unknown>) => {
        data = { ...data, results: data.results.map((item) => ({
          ...item,
          p6: { p6_control_id: String(input.p6_control_id), order_id: String(input.order_id), decision: "APPROVED",
            reservations: [], rationale: String(input.rationale), actor_id: "patron-1", recorded_at: now },
        })) };
        return receipt;
      }),
      recordCaseP7Result: vi.fn(async (_p6Id: string, input: Record<string, unknown>) => {
        data = { ...data, results: data.results.map((item) => ({
          ...item,
          p7: { p7_result_id: String(input.p7_result_id), p6_control_id: String(input.p6_control_id), result: "UNKNOWN",
            source_locator: null, reason: String(input.reason), reservations: [], actor_id: "patron-1", recorded_at: now },
        })) };
        return receipt;
      }),
    };

    await renderApp();
    fireEvent.click(screen.getByRole("button", { name: /Résultat et passation/ }));
    await screen.findByRole("heading", { name: "Résultat par lot · P6 · P7 · REX" });
    fireEvent.change(screen.getByLabelText("Lot concerné"), { target: { value: "01" } });
    fireEvent.change(screen.getByLabelText("Résultat déclaré du lot"), { target: { value: "WON" } });
    fireEvent.change(screen.getByLabelText("Référence de preuve du résultat"), { target: { value: "notification://lot-01" } });
    fireEvent.click(screen.getByRole("button", { name: "Enregistrer le résultat par lot" }));
    await screen.findByText(/Attribution déclarée \(WON\)/);

    fireEvent.change(screen.getByLabelText("Décision Patron sur la commande"), { target: { value: "ACCEPTED" } });
    fireEvent.change(screen.getByLabelText("Motif de la commande"), { target: { value: "Commande rapprochée" } });
    fireEvent.click(screen.getByRole("button", { name: "Enregistrer la décision sur la commande" }));
    await screen.findByRole("heading", { name: "Décision sur la commande · ACCEPTED" });

    fireEvent.change(screen.getByLabelText("Décision Patron P6"), { target: { value: "APPROVED" } });
    fireEvent.change(screen.getByLabelText("Motif P6"), { target: { value: "Clarifications vérifiées" } });
    fireEvent.click(screen.getByRole("button", { name: "Enregistrer la décision P6" }));
    await screen.findByRole("heading", { name: "Contrôle P6 · APPROVED" });

    fireEvent.change(screen.getByLabelText("Résultat P7"), { target: { value: "UNKNOWN" } });
    fireEvent.change(screen.getByLabelText("Motif du résultat P7"), { target: { value: "Retour d’exécution en attente" } });
    fireEvent.click(screen.getByRole("button", { name: "Enregistrer le résultat P7" }));
    await screen.findByRole("heading", { name: "Résultat P7 · UNKNOWN" });
    expect(screen.getByText(/P7 ne vaut pas ordre de service/)).toBeInTheDocument();
  });

  it("limite une session mot de passe à l’étape MFA", async () => {
    authMfaRef.current = false;
    await renderApp();

    expect(screen.getByRole("heading", { name: "Validez votre second facteur" })).toBeVisible();
    expect(screen.queryByText("Actions à traiter")).toBeNull();
  });

  it("ne rend aucune donnée métier sans session", async () => {
    authSessionRef.current = false;
    overridesRef.current = baseOverrides();
    await renderApp();

    expect(screen.getByRole("heading", { name: "Connectez-vous" })).toBeVisible();
    expect(screen.queryByText("Extension de collège")).toBeNull();
    expect(screen.queryByText("À FAIRE MAINTENANT")).toBeNull();
  });

  it("masque les données puis reprend le dernier état confirmé après expiration", async () => {
    overridesRef.current = baseOverrides();
    const view = await renderApp();
    expect(screen.getByRole("heading", { name: "Accueil" })).toBeVisible();

    authSessionExpiredRef.current = true;
    authSessionRef.current = false;
    view.rerender(<App />);

    expect(await screen.findByText(/Votre session a expiré/)).toBeVisible();
    expect(screen.queryByText("Extension de collège")).toBeNull();

    authSessionExpiredRef.current = false;
    authSessionRef.current = true;
    overridesRef.current = {
      ...baseOverrides(),
      listAssignedCases: () => delayedRejection(new Error("rechargement indisponible"), 30),
    };
    view.rerender(<App />);

    expect(await screen.findByRole("heading", { name: "Confirmez votre contexte" })).toBeVisible();
    expect(screen.getByText(/Reprise du dernier état confirmé en cours/)).toBeVisible();
    fireEvent.click(screen.getByRole("button", { name: "Confirmer et continuer" }));

    expect(await screen.findByText(/aucune donnée nouvelle n’est considérée comme confirmée/)).toBeVisible();
    expect(await screen.findByText("rechargement indisponible")).toBeVisible();
  });

  it("n’utilise pas le snapshot si le rôle change avant la reprise", async () => {
    overridesRef.current = baseOverrides();
    const view = await renderApp();
    expect(screen.getByRole("heading", { name: "Accueil" })).toBeVisible();

    authSessionExpiredRef.current = true;
    authSessionRef.current = false;
    view.rerender(<App />);

    expect(await screen.findByText(/Votre session a expiré/)).toBeVisible();

    authSessionExpiredRef.current = false;
    authSessionRef.current = true;
    authRoleRef.current = "COLLABORATEUR";
    authProfileRef.current = "EXPERT";
    overridesRef.current = { ...baseOverrides(), listAssignedCases: () => Promise.resolve([]) };
    view.rerender(<App />);

    expect(await screen.findByRole("heading", { name: "Confirmez votre contexte" })).toBeVisible();
    fireEvent.click(screen.getByRole("button", { name: "Confirmer et continuer" }));

    expect(await screen.findByRole("heading", { name: "Accueil" })).toBeVisible();
    expect(screen.queryByText("Extension de collège")).toBeNull();
    expect(screen.queryByText(/Reprise du dernier état confirmé en cours/)).toBeNull();
  });

  it("confirme le contexte serveur avant d’afficher la première Affaire", async () => {
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Confirmez votre contexte" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "entreprise-test" })).toBeVisible();
    expect(screen.queryByRole("heading", { name: "Créer une affaire" })).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "Confirmer et continuer" }));

    expect(await screen.findByRole("heading", { name: "Créer une affaire" })).toBeVisible();
  });

  it("garde la première valeur disponible sans imposer la fiche entreprise complète", async () => {
    overridesRef.current = {
      ...baseOverrides(),
      listAssignedCases: () => Promise.resolve([]),
      getEnterpriseCompany: () => Promise.reject(new Error("no company")),
    };
    await renderApp();

    expect(await screen.findByRole("heading", { name: "Créer une affaire" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "Créer la fiche entreprise" })).toBeVisible();
    expect(screen.getByText(/Les compléments viendront au moment utile/)).toBeVisible();
  });

  it("crée une première Affaire puis ouvre le premier Accueil composé", async () => {
    const createCase = vi.fn().mockResolvedValue({
      status: "SUCCEEDED",
      command_id: "command-1",
      idempotency_key: "idempotency-1",
      result_code: "CASE_CREATED",
      case_id: "case-1",
      version: 0,
      event_ids: ["event-1"],
      navigation: "CASE_OVERVIEW",
      replayed: false,
    });
    const listAssignedCases = vi.fn()
      .mockResolvedValueOnce([])
      .mockResolvedValue([CASE]);
    overridesRef.current = { ...baseOverrides(), createCase, listAssignedCases };
    await renderApp();

    fireEvent.change(screen.getByLabelText("Titre de l’affaire"), { target: { value: "Première Affaire" } });
    fireEvent.change(screen.getByLabelText("Objet et description"), { target: { value: "Travaux de réhabilitation" } });
    fireEvent.click(screen.getByRole("button", { name: /Créer l’affaire/ }));

    await waitFor(() => expect(createCase).toHaveBeenCalledOnce());
    expect(createCase).toHaveBeenCalledWith(expect.objectContaining({
      title: "Première Affaire",
      idempotency_key: expect.any(String),
    }));
    expect(await screen.findByRole("heading", { name: "Reprendre Extension de collège" })).toBeVisible();
    expect(screen.getByText("À SURVEILLER")).toBeVisible();
    expect(screen.getByText("ÉVÉNEMENTS RÉCENTS")).toBeVisible();
    expect(screen.getByText("Aucun événement d’affectation autorisé n’est disponible.")).toBeVisible();
  });

  it("conserve l’identifiant idempotent quand la création échoue avant la reprise", async () => {
    const createCase = vi.fn()
      .mockRejectedValueOnce(new Error("Réponse perdue"))
      .mockResolvedValueOnce({
        status: "SUCCEEDED",
        command_id: "command-1",
        idempotency_key: "idempotency-1",
        result_code: "CASE_CREATED",
        case_id: "case-1",
        version: 0,
        event_ids: ["event-1"],
        navigation: "CASE_OVERVIEW",
        replayed: true,
      });
    overridesRef.current = {
      ...baseOverrides(),
      listAssignedCases: () => Promise.resolve([]),
      createCase,
    };
    await renderApp();
    fireEvent.change(screen.getByLabelText("Titre de l’affaire"), { target: { value: "Première Affaire" } });
    fireEvent.change(screen.getByLabelText("Objet et description"), { target: { value: "Travaux" } });

    fireEvent.click(screen.getByRole("button", { name: /Créer l’affaire/ }));
    expect(await screen.findByText("Réponse perdue")).toBeVisible();
    fireEvent.click(screen.getByRole("button", { name: /Vérifier et réessayer/ }));

    await waitFor(() => expect(createCase).toHaveBeenCalledTimes(2));
    expect(createCase.mock.calls[1]?.[0].command_id).toBe(createCase.mock.calls[0]?.[0].command_id);
    expect(createCase.mock.calls[1]?.[0].idempotency_key).toBe(createCase.mock.calls[0]?.[0].idempotency_key);
  });
});

describe("App error visibility", () => {
  beforeEach(() => {
    window.localStorage.clear();
    authRoleRef.current = "PATRON_ADMIN";
    authSessionExpiredRef.current = false;
    authMfaRef.current = true;
    authSessionRef.current = true;
    overridesRef.current = {};
  });

  it("ne rend pas les surfaces patronales dans l’espace collaborateur", async () => {
    authRoleRef.current = "COLLABORATEUR";
    authProfileRef.current = "EXPERT";
    await renderApp();

    expect(screen.getByText("ESPACE COLLABORATEUR")).toBeVisible();
    expect(screen.getAllByText("Expert")).not.toHaveLength(0);
    expect(screen.queryByText("Actions à traiter")).toBeNull();
    expect(screen.queryByText("Opportunités BOAMP")).toBeNull();
    expect(screen.queryByText("Dépôt")).toBeNull();
    expect(screen.queryByRole("button", { name: /Résultat et passation/ })).toBeNull();
    expect(screen.queryByText("Ventes")).toBeNull();
  });

  it("affiche une erreur visible quand le chargement des scénarios de chiffrage échoue", async () => {
    overridesRef.current = {
      ...baseOverrides(),
      listPricingScenarios: () =>
        delayedRejection(new Error("Scénarios indisponibles"), 30),
    };
    await renderApp();
    connect();

    expect(
      await screen.findByText(/Les scénarios privés sont indisponibles/, {}, { timeout: 3000 }),
    ).toBeVisible();
    expect(screen.getByRole("alert")).toHaveTextContent("Les scénarios privés sont indisponibles");
  });

  it("affiche une erreur visible quand le dossier de décision échoue hors 404", async () => {
    overridesRef.current = {
      ...baseOverrides(),
      getDecisionDossier: () =>
        delayedRejection(new Error("Dossier momentanément indisponible"), 30),
    };
    await renderApp();
    connect();

    expect(
      await screen.findByText("Dossier momentanément indisponible", {}, { timeout: 3000 }),
    ).toBeVisible();
  });

  it("reste silencieux quand l’absence de dossier de décision répond 404", async () => {
    overridesRef.current = {
      ...baseOverrides(),
      getDecisionDossier: () =>
        delayedRejection(
          Object.assign(new Error("ne doit jamais apparaître"), { status: 404 }),
          50,
        ),
    };
    await renderApp();
    connect();

    expect(
      await screen.findByRole(
        "heading",
        { name: "Extension de collège" },
        { timeout: 3000 },
      ),
    ).toBeVisible();
    await new Promise((resolve) => setTimeout(resolve, 150));
    expect(screen.queryByText("ne doit jamais apparaître")).toBeNull();
  });

  it("relie depuis C07 l’impact au Patron et conserve le contrat de retry exact", async () => {
    Object.defineProperty(HTMLElement.prototype, "scrollIntoView", {
      configurable: true,
      value: vi.fn(),
    });
    const impact: ContractBaselineImpact = {
      proof_id: "proof-1",
      case_id: "case-1",
      baseline_observation_id: "observation-1",
      dce_requirement_id: "requirement-1",
      dce_requirement_revision: 2,
      proof_revision: 1,
      baseline_source_refs: ["CCAP · article 4 · page 12"],
      baseline_statement: "Délai de paiement déclaré.",
      deviation_statement: null,
      impact_statement: "Effet à examiner, non calculé.",
      status: "HUMAN_REVIEW_REQUIRED",
    };
    const dossier: PatronDecisionDossier = {
      decision_id: "decision-1",
      aggregate_revision: 4,
      case_id: "case-1",
      decision_type: "GO_NO_GO",
      lifecycle: "FINALIZED",
      outcome: "CONDITIONAL_GO",
      validity: "CURRENT",
      context_status: "FROZEN",
      final_justification: "Décision conditionnelle Patron.",
      known: [],
      unknowns: [],
      risks: [],
      conditions: [{ condition_id: "condition-1", label: "Vérifier l’impact", status: "OPEN", due_at: null, failure_consequence: "Réexamen Patron" }],
      sources: [
        { aggregate_type: "DCE_REQUIREMENT", aggregate_id: "requirement-1", aggregate_revision: 2, role: "REQUIREMENT" },
        { aggregate_type: "CONTRACT_BASELINE_IMPACT", aggregate_id: "proof-1", aggregate_revision: 1, role: "IMPACT" },
        { aggregate_type: "BUSINESS_METHOD_PROFILE", aggregate_id: "profile-1", aggregate_revision: 1, role: "ADOPTED_METHOD" },
      ],
      contract_evidence_links: [],
      context_fingerprint: "a".repeat(64),
    };
    const link = vi.fn(async () => ({ status: "SUCCEEDED" }));
    overridesRef.current = {
      ...baseOverrides(),
      listContractBaselineImpacts: async () => ({ case_id: "case-1", items: [impact] }),
      getDecisionDossier: async () => dossier,
      linkDecisionConditionContractEvidence: link,
    };
    await renderApp();
    fireEvent.click(screen.getByRole("button", { name: /Décision/ }));
    fireEvent.click(await screen.findByRole("button", { name: "Relier l’impact v1 à cette condition" }));
    await waitFor(() => expect(link).toHaveBeenCalledOnce());
    const [caseId, decisionId, conditionId, input] = link.mock.calls[0] as unknown as [string, string, string, Record<string, unknown>];
    expect([caseId, decisionId, conditionId]).toEqual(["case-1", "decision-1", "condition-1"]);
    expect(input).toMatchObject({ contract_impact_id: "proof-1", proof_revision: 1, expected_decision_revision: 4 });
  });

  it("ajoute au contexte A1 le profil versionné actuellement adopté", async () => {
    Object.defineProperty(HTMLElement.prototype, "scrollIntoView", {
      configurable: true,
      value: vi.fn(),
    });
    const company = {
      company_id: "company-1", aggregate_revision: 1, legal_name: "Entreprise test",
      trade_name: null, siren: "123456789", siret: "12345678900012", vat_number: "FR123456789",
      address_line1: "1 rue test", postal_code: "75000", city: "Paris", country_code: "FR", documents: [],
    };
    const adoption = {
      adoption_id: "adoption-1", case_id: "case-1", adoption_revision: 3,
      profile_version_id: "profile-2", profile_version: 2, profile_content_sha256: "b".repeat(64),
    };
    const decision: PatronDecisionDossier = {
      decision_id: "decision-draft", aggregate_revision: 0, case_id: "case-1",
      decision_type: "GO_NO_GO", lifecycle: "DRAFT", outcome: "UNDECIDED", validity: "CURRENT",
      context_status: "INCOMPLETE", final_justification: null, known: [], unknowns: [], risks: [],
      conditions: [], sources: [], contract_evidence_links: [], context_fingerprint: null,
    };
    const freeze = vi.fn(async (
      _caseId: string,
      _decisionId: string,
      _input: FreezeDecisionContextRequest,
    ) => ({ result_code: "DECISION_CONTEXT_FROZEN" }));
    overridesRef.current = {
      ...baseOverrides(),
      getEnterpriseCompany: async () => company,
      listEnterpriseCapabilities: async () => ({ capabilities: [] }),
      listBusinessMethodProfileVersions: async () => ({ company_id: "company-1", versions: [] }),
      getBusinessMethodProfileAdoption: async () => adoption,
      getDecisionDossier: async () => decision,
      freezeDecisionContext: freeze,
    };
    await renderApp();
    fireEvent.click(screen.getByRole("button", { name: /Décision/ }));
    await screen.findByText("Profil métier versionné");
    fireEvent.change(screen.getByLabelText("Identifiant du contexte"), { target: { value: "context-1" } });
    fireEvent.change(screen.getByLabelText("Justification"), { target: { value: "Décision à instruire" } });
    fireEvent.change(screen.getByLabelText("Références JSON vérifiables"), { target: { value: JSON.stringify([
      { aggregate_type: "CASE", aggregate_id: "case-1", aggregate_revision: 1, reference_role: "SUBJECT" },
      { aggregate_type: "DCE_REQUIREMENT", aggregate_id: "requirement-1", aggregate_revision: 2, reference_role: "REQUIREMENT" },
      { aggregate_type: "CONTRACT_BASELINE_IMPACT", aggregate_id: "proof-1", aggregate_revision: 1, reference_role: "DECLARED_IMPACT" },
    ]) } });
    fireEvent.click(screen.getByRole("button", { name: "Geler le contexte" }));
    await waitFor(() => expect(freeze).toHaveBeenCalledOnce());
    const input = freeze.mock.calls[0][2];
    expect(input.references).toContainEqual({
      aggregate_type: "BUSINESS_METHOD_PROFILE",
      aggregate_id: "profile-2",
      aggregate_revision: 2,
      content_hash: "b".repeat(64),
      reference_role: "ADOPTED_METHOD",
    });
  });
});
