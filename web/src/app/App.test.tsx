import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import type { AssignedCase } from "../shared/types";

const { authMfaRef, authProfileRef, authRoleRef, authSessionExpiredRef, authSessionRef, overridesRef } = vi.hoisted(() => ({
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

vi.mock("../features/auth/useAuthentication", () => ({
  useAuthentication: () => ({
    accessToken: "token-test",
    currentActor: authSessionRef.current ? {
      actor_id: "actor-1",
      identity_id: "identity-1",
      tenant_slug: "entreprise-test",
      actor_kind: authRoleRef.current,
      operational_profile: authProfileRef.current,
      membership_state: "ACTIVE",
      mfa_verified: authMfaRef.current,
    } : null,
    isRestoring: false,
    sessionExpired: authSessionExpiredRef.current,
    hasSession: authSessionRef.current,
    isAuthenticated: authSessionRef.current && authMfaRef.current,
    api: new Proxy(
      {
        getEnterpriseCompany: () => Promise.reject(new Error("no company")),
        listAssignedCases: () => Promise.resolve([]),
        listPatronAssignments: () => Promise.resolve({ items: [] }),
        listPatronActions: () => Promise.resolve({ items: [], open_count: 0 }),
        listBoampObservations: () => Promise.resolve({ observations: [] }),
        getCaseDceReading: () => Promise.reject(Object.assign(new Error("missing DCE"), { status: 404 })),
        searchCaseKnowledge: () => Promise.resolve({ case_id: "case-1", query: "", results: [] }),
        listPricingScenarios: () => Promise.resolve([]),
        listDecisionRiskRequirementLinks: () => Promise.resolve({ items: [], next_cursor: null }),
        listDceContractRiskSignals: () => Promise.resolve({ case_id: "case-1", items: [] }),
        crossCctpPricing: () => Promise.resolve({ case_id: "case-1", items: [] }),
        listDocumentContradictions: () => Promise.resolve({ case_id: "case-1", items: [] }),
        reconcileDecisionPricing: () => Promise.resolve({ link_id: "", search: "", items: [] }),
        getDecisionDossier: () => Promise.reject(Object.assign(new Error("missing"), { status: 404 })),
        ...overridesRef.current,
      } as Record<string, unknown>,
      {
      get(target, prop) {
        if (typeof prop === "string" && prop in target) return target[prop];
        return () => Promise.resolve({});
      },
    }) as never,
    login: vi.fn(),
    refreshActor: vi.fn(),
    logout: vi.fn(),
  }),
}));

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
    listDecisionRiskRequirementLinks: () => Promise.resolve({ items: [], next_cursor: null }),
    listDceContractRiskSignals: () => Promise.resolve({ case_id: "case-1", items: [] }),
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
    overridesRef.current = {};
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
      await screen.findByText("Scénarios indisponibles", {}, { timeout: 3000 }),
    ).toBeVisible();
    expect(screen.getByRole("alert")).toHaveTextContent("Scénarios indisponibles");
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
});
