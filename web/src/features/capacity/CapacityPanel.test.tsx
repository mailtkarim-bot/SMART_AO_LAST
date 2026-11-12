import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import type { ApiClient } from "../../infrastructure/api";
import { CapacityPanel, CapacityPendingStore } from "./CapacityPanel";
function data(caseId = "case-a") {
  return {
    case_id: caseId,
    context_sha256: "a".repeat(64),
    revision: 0,
    current: null,
    history: [],
    history_has_more: false,
    state: "UNKNOWN",
    coverage_state: "UNKNOWN",
    reservation_state: "NOT_RESERVED"
  };
}
it("shows missing inputs and requires explicit confirmation before a dated command", async () => {
  const api = {
    getDatedCapacity: vi.fn().mockResolvedValue(data()),
    recordDatedCapacity: vi.fn()
  } as unknown as ApiClient;
  render(<CapacityPanel api={api} enabled caseId="case-a" ownerKey="owner" scopeKey="session" pendingStore={new CapacityPendingStore()} />);
  await screen.findByText("Aucun plan enregistré.");
  expect(screen.getByRole("button", {
    name: "Enregistrer et calculer"
  })).toBeDisabled();
  expect(api.recordDatedCapacity).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole("button", {
    name: "Ajouter un besoin"
  }));
  expect(screen.getByLabelText("Besoin 1 — libellé")).toBeInTheDocument();
});
it("masks the old case immediately and refuses a discordant response", async () => {
  const api = {
    getDatedCapacity: vi.fn().mockResolvedValue(data()),
    recordDatedCapacity: vi.fn()
  } as unknown as ApiClient;
  const store = new CapacityPendingStore();
  const view = render(<CapacityPanel api={api} enabled caseId="case-a" ownerKey="owner" scopeKey="session" pendingStore={store} />);
  await screen.findByText("Aucun plan enregistré.");
  fireEvent.click(screen.getByRole("button", {
    name: "Ajouter un besoin"
  }));
  fireEvent.change(screen.getByLabelText("Besoin 1 — libellé"), {
    target: {
      value: "Privé A"
    }
  });
  view.rerender(<CapacityPanel api={api} enabled caseId="case-b" ownerKey="owner" scopeKey="session" pendingStore={store} />);
  expect(screen.queryByDisplayValue("Privé A")).not.toBeInTheDocument();
  await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("Lecture indisponible"));
});
it("freezes an UNKNOWN intent and retries identical IDs without an intervening GET", async () => {
  const get = vi.fn().mockResolvedValue(data());
  const post = vi.fn().mockRejectedValueOnce(Object.assign(Error("timeout"), {status:503})).mockRejectedValueOnce(Object.assign(Error("validation after timeout"), {status:422}));
  const api = {
    getDatedCapacity: get,
    recordDatedCapacity: post
  } as unknown as ApiClient;
  const store = new CapacityPendingStore();
  render(<CapacityPanel api={api} enabled caseId="case-a" ownerKey="owner" scopeKey="session" pendingStore={store} />);
  await screen.findByText("Aucun plan enregistré.");
  fireEvent.change(screen.getByLabelText("Justification du plan de capacité"), {
    target: {
      value: "Capacité inconnue à instruire"
    }
  });
  fireEvent.click(screen.getByLabelText(/Je confirme ces entrées/));
  fireEvent.click(screen.getByRole("button", {
    name: "Enregistrer et calculer"
  }));
  await screen.findByText(/UNKNOWN — résultat de l’envoi inconnu/);
  const first = post.mock.calls[0][1];
  expect(get).toHaveBeenCalledTimes(1);
  expect(screen.queryByLabelText("Justification")).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", {
    name: "Réessayer le même envoi"
  }));
  await waitFor(() => expect(post).toHaveBeenCalledTimes(2));
  expect(post.mock.calls[1][1]).toEqual(first);
  expect(get).toHaveBeenCalledTimes(1);
});
it("does not expose a plan after losing the Patron context", async () => {
  const api = {
    getDatedCapacity: vi.fn().mockResolvedValue(data()),
    recordDatedCapacity: vi.fn()
  } as unknown as ApiClient;
  const store = new CapacityPendingStore();
  const view = render(<CapacityPanel api={api} enabled caseId="case-a" ownerKey="owner" scopeKey="session" pendingStore={store} />);
  await screen.findByText("Aucun plan enregistré.");
  view.rerender(<CapacityPanel api={api} enabled={false} caseId="case-a" ownerKey="owner" scopeKey="session" pendingStore={store} />);
  expect(screen.queryByRole("region", {
    name: "Planification de capacité"
  })).not.toBeInTheDocument();
});
it("keeps invalid periods editable instead of sending an uncorrectable intent", async () => {
  const api = {
    getDatedCapacity: vi.fn().mockResolvedValue(data()),
    recordDatedCapacity: vi.fn()
  } as unknown as ApiClient;
  render(<CapacityPanel api={api} enabled caseId="case-a" ownerKey="owner" scopeKey="session" pendingStore={new CapacityPendingStore()} />);
  await screen.findByText("Aucun plan enregistré.");
  fireEvent.click(screen.getByRole("button", {
    name: "Ajouter un besoin"
  }));
  for (const [label, value] of [["libellé", "Pose"], ["début inclus", "2026-11-03"], ["fin exclue", "2026-11-01"]]) fireEvent.change(screen.getByLabelText(`Besoin 1 — ${label}`), {
    target: {
      value
    }
  });
  fireEvent.change(screen.getByLabelText("Justification du plan de capacité"), {
    target: {
      value: "Essai"
    }
  });
  fireEvent.click(screen.getByLabelText(/Je confirme ces entrées/));
  fireEvent.click(screen.getByRole("button", {
    name: "Enregistrer et calculer"
  }));
  await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("fin"));
  expect(api.recordDatedCapacity).not.toHaveBeenCalled();
  expect(screen.getByLabelText("Besoin 1 — fin exclue")).toBeInTheDocument();
});
it("restores editing after a certain initial validation rejection", async () => {
  const api = {
    getDatedCapacity: vi.fn().mockResolvedValue(data()),
    recordDatedCapacity: vi.fn().mockRejectedValue(Object.assign(Error("validation"), {
      status: 422
    }))
  } as unknown as ApiClient;
  render(<CapacityPanel api={api} enabled caseId="case-a" ownerKey="owner" scopeKey="session" pendingStore={new CapacityPendingStore()} />);
  await screen.findByText("Aucun plan enregistré.");
  fireEvent.change(screen.getByLabelText("Justification du plan de capacité"), {
    target: {
      value: "Essai"
    }
  });
  fireEvent.click(screen.getByLabelText(/Je confirme ces entrées/));
  fireEvent.click(screen.getByRole("button", {
    name: "Enregistrer et calculer"
  }));
  await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("Saisie refusée"));
  expect(screen.getByLabelText("Justification du plan de capacité")).toBeInTheDocument();
});

it("suspends source reads and ignores replies during an uncertain DCE replacement", async () => {
  let resolve!: (value: ReturnType<typeof data>) => void;
  const get = vi.fn().mockImplementation(() => new Promise<ReturnType<typeof data>>(done => { resolve = done; }));
  const api = {getDatedCapacity:get} as unknown as ApiClient;
  const props = {api, enabled:true, caseId:"case-a", ownerKey:"owner", scopeKey:"session", pendingStore:new CapacityPendingStore()};
  const {rerender} = render(<CapacityPanel {...props}/>);
  rerender(<CapacityPanel {...props} sourceReadBlocked/>);
  expect(screen.getByRole("status")).toHaveTextContent("Sources en cours de reprise");
  resolve(data());
  await waitFor(() => expect(screen.queryByText("Aucun plan enregistré.")).not.toBeInTheDocument());
  expect(get).toHaveBeenCalledTimes(1);
});

it("clears old inputs and human consent after a changed source context is reread", async () => {
  const get = vi.fn().mockResolvedValueOnce(data()).mockResolvedValue({...data(), context_sha256:"b".repeat(64)});
  const post = vi.fn();
  render(<CapacityPanel api={{getDatedCapacity:get,recordDatedCapacity:post} as unknown as ApiClient} enabled caseId="case-a" ownerKey="owner" scopeKey="session" pendingStore={new CapacityPendingStore()}/>);
  await screen.findByText("Aucun plan enregistré.");
  fireEvent.click(screen.getByRole("button",{name:"Ajouter un besoin"}));
  fireEvent.change(screen.getByLabelText("Justification du plan de capacité"),{target:{value:"Accord ancien contexte."}});
  fireEvent.click(screen.getByLabelText(/Je confirme ces entrées/));
  fireEvent.click(screen.getByRole("button",{name:"Relire le plan"}));
  await waitFor(() => expect(get).toHaveBeenCalledTimes(2));
  await waitFor(() => expect(screen.getByLabelText(/Je confirme ces entrées/)).not.toBeChecked());
  expect(screen.queryByLabelText("Besoin 1 — libellé")).not.toBeInTheDocument();
  expect(screen.getByLabelText("Justification du plan de capacité")).toHaveValue("");
  expect(post).not.toHaveBeenCalled();
});
