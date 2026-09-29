import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { expect, test, vi } from "vitest";
import type { ContractExecutionEvidence, ContractInstrumentVersion, DeclareContractInstrumentSupersessionInput, RecordContractExecutionEvidenceInput, RecordContractInstrumentVersionInput } from "../../shared/types";
import { ContractExecutionEvidencePanel } from "./ContractExecutionEvidencePanel";
import { ContractInstrumentVersionsPanel } from "./ContractInstrumentVersionsPanel";
import { ContractRightsAxisProjection } from "./ContractRightsAxisProjection";

const event: ContractExecutionEvidence = {
  act_id: "act-1", case_id: "case-1", act_kind: "RIGHTS_PRESERVATION",
  reception_outcome: "UNKNOWN",
  summary: "Réserve envoyée au maître d’ouvrage", source_refs: ["ccap://v3/clause/18"],
  evidence_refs: ["document://courrier/sha256:abc", "document://accuse/sha256:def"],
  declared_event_date: "2026-09-27", case_dce_version_id_at_recording: "dce-v3",
  version_relation: "MATCHES_CASE_CURRENT", contract_instrument_version_id: "contract-version-1",
  contract_instrument_version_relation: "DECLARED",
  contract_instrument_version: {
    contract_instrument_version_id: "contract-version-1", instrument_kind: "SIGNED_CONTRACT",
    version_reference: "MARCHE-SIGNE-2026-04-12", source_refs: ["contract://signed/1"],
    evidence_refs: ["document://signed-contract/sha256:abc"],
  },
  actor_id: "patron-1", recorded_at: "2026-09-28T10:00:00Z",
};

test("projette les actes humains séparément et n’en déduit aucune portée juridique", () => {
  render(<ContractRightsAxisProjection obligations={[]} acts={[event]} actsStatus="READY" />);
  const projection = screen.getByLabelText(/Carte d’Engagement axe 12/);
  expect(projection).toHaveTextContent("Réserve envoyée au maître d’ouvrage");
  expect(projection).toHaveTextContent("ccap://v3/clause/18");
  expect(projection).toHaveTextContent("document://accuse/sha256:def");
  expect(projection).toHaveTextContent("Date d’acte déclarée : 2026-09-27");
  expect(projection).toHaveTextContent("Acte déclaré par le Patron · portée juridique non évaluée");
  expect(projection).toHaveTextContent("Version DCE associée à l’Affaire lors de l’acte : dce-v3");
  expect(projection).toHaveTextContent("cela ne confirme pas l’applicabilité contractuelle");
  expect(projection).toHaveTextContent("Version signée/avenant sourcée : Contrat signé · MARCHE-SIGNE-2026-04-12 (déclaration Patron, non vérifiée)");
  expect(projection).toHaveTextContent("contract://signed/1");
  expect(screen.getAllByText("UNKNOWN · aucun acte enregistré ; cela ne prouve pas son absence.")).toHaveLength(2);
  expect(projection).not.toHaveTextContent("forclusion acquise");
});

test("signale une version DCE remplacée comme nécessitant une requalification humaine", () => {
  render(<ContractRightsAxisProjection obligations={[]} acts={[{ ...event, version_relation: "REVIEW_REQUIRED" }]} actsStatus="READY" />);
  expect(screen.getByText(/REVIEW_REQUIRED · version DCE remplacée ou lien modifié ; requalification humaine requise/)).toBeInTheDocument();
});

test("signale indépendamment l’acte attaché à une version contractuelle déclarée remplacée", () => {
  render(<ContractRightsAxisProjection obligations={[]} acts={[{
    ...event, contract_instrument_version_relation: "REVIEW_REQUIRED",
  }]} actsStatus="READY" />);
  expect(screen.getByText(/REVIEW_REQUIRED · le Patron a déclaré cette version remplacée ; requalification humaine requise/)).toBeInTheDocument();
});

test("conserve UNKNOWN quand la référence d’un contrat signé ou d’un avenant manque", () => {
  render(<ContractRightsAxisProjection obligations={[]} acts={[{
    ...event, contract_instrument_version_id: null, contract_instrument_version: null,
  }]} actsStatus="READY" />);
  expect(screen.getByText("Version signée/avenant sourcée : UNKNOWN · aucune version enregistrée ou liée")).toBeInTheDocument();
});

test("n’affiche pas l’absence d’acte comme UNKNOWN si la source est indisponible", () => {
  render(<ContractRightsAxisProjection obligations={[]} acts={[]} actsStatus="UNAVAILABLE" />);
  expect(screen.getAllByText(/UNAVAILABLE · impossible de lire les actes/i)).toHaveLength(3);
});

test("un retry après résultat non confirmé réutilise exactement la même intention idempotente", async () => {
  const inputs: RecordContractExecutionEvidenceInput[] = [];
  const onCreate = vi.fn(async (_caseId: string, input: RecordContractExecutionEvidenceInput) => {
    inputs.push(input);
    if (inputs.length === 1) throw new Error("interrupted");
  });
  render(<ContractExecutionEvidencePanel caseId="case-1" canManage onCreate={onCreate} />);
  fireEvent.change(screen.getByLabelText("Type d’acte déclaré"), { target: { value: "CONTRACT_EXIT" } });
  fireEvent.change(screen.getByLabelText("Description de l’acte"), { target: { value: "Acte communiqué" } });
  fireEvent.change(screen.getByLabelText("Références sources, une par ligne"), { target: { value: "ccap://v3/clause/30" } });
  fireEvent.change(screen.getByLabelText("Références de preuve, une par ligne"), { target: { value: "document://act/sha256:abc" } });
  fireEvent.change(screen.getByLabelText("Date de l’acte déclarée"), { target: { value: "2026-09-28" } });
  const form = screen.getByRole("form", { name: "Enregistrer un acte contractuel sourcé" });
  fireEvent.submit(form);
  await waitFor(() => expect(onCreate).toHaveBeenCalledTimes(1));
  expect(await screen.findByText(/résultat non confirmé/i)).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Réessayer l’enregistrement" }));
  await waitFor(() => expect(onCreate).toHaveBeenCalledTimes(2));
  expect(onCreate.mock.calls[0][0]).toBe("case-1");
  expect(inputs[0]).toEqual(inputs[1]);
  expect(inputs[0]).toMatchObject({
    act_kind: "CONTRACT_EXIT", source_refs: ["ccap://v3/clause/30"],
    evidence_refs: ["document://act/sha256:abc"], declared_event_date: "2026-09-28",
    contract_instrument_version_id: null,
  });
});

test("isole une tentative non confirmée de son Affaire et masque ses détails ailleurs", async () => {
  const onCreate = vi.fn(async () => { throw new Error("interrupted"); });
  const { rerender } = render(<ContractExecutionEvidencePanel caseId="case-1" canManage onCreate={onCreate} />);
  fireEvent.change(screen.getByLabelText("Description de l’acte"), { target: { value: "Réserve privée case 1" } });
  fireEvent.change(screen.getByLabelText("Références sources, une par ligne"), { target: { value: "ccap://case-1" } });
  fireEvent.change(screen.getByLabelText("Références de preuve, une par ligne"), { target: { value: "document://case-1" } });
  fireEvent.change(screen.getByLabelText("Réserves consignées au procès-verbal"), { target: { value: "WITH_RESERVATIONS" } });
  fireEvent.submit(screen.getByRole("form", { name: "Enregistrer un acte contractuel sourcé" }));
  expect(await screen.findByText(/résultat non confirmé/i)).toBeInTheDocument();

  rerender(<ContractExecutionEvidencePanel caseId="case-2" canManage onCreate={onCreate} />);

  expect(screen.getByText(/résultat d’enregistrement reste à vérifier pour une autre Affaire/i)).toBeInTheDocument();
  expect(screen.queryByText("Réserve privée case 1")).not.toBeInTheDocument();
  expect(screen.queryByText("ccap://case-1")).not.toBeInTheDocument();
  expect(onCreate).toHaveBeenCalledTimes(1);
});

test("refuse localement plus de 32 références sans créer une intention serveur", async () => {
  const onCreate = vi.fn(async () => undefined);
  render(<ContractExecutionEvidencePanel caseId="case-1" canManage onCreate={onCreate} />);
  fireEvent.change(screen.getByLabelText("Description de l’acte"), { target: { value: "PV" } });
  fireEvent.change(screen.getByLabelText("Références sources, une par ligne"), {
    target: { value: Array.from({ length: 33 }, (_, index) => `ccap://clause/${index}`).join("\n") },
  });
  fireEvent.change(screen.getByLabelText("Références de preuve, une par ligne"), { target: { value: "document://pv" } });
  fireEvent.submit(screen.getByRole("form", { name: "Enregistrer un acte contractuel sourcé" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("1 à 32 sources/preuves par liste");
  expect(screen.getByRole("button", { name: "Enregistrer l’acte" })).toBeEnabled();
  expect(onCreate).not.toHaveBeenCalled();
});

test("lie l’acte à une version de contrat signée ou d’avenant sourcée, distincte du DCE", async () => {
  const inputs: RecordContractExecutionEvidenceInput[] = [];
  const onCreate = vi.fn(async (_caseId: string, input: RecordContractExecutionEvidenceInput) => { inputs.push(input); });
  const version: ContractInstrumentVersion = {
    contract_instrument_version_id: "version-2", case_id: "case-1", instrument_kind: "AMENDMENT",
    version_reference: "AVENANT-2-SIGNE", source_refs: ["contract://amendment/2"],
    evidence_refs: ["document://amendment/2"], actor_id: "patron-1", recorded_at: "2026-09-29T00:00:00Z",
  };
  render(<ContractExecutionEvidencePanel caseId="case-1" canManage instrumentVersions={[version]} onCreate={onCreate} />);
  fireEvent.change(screen.getByLabelText("Type d’acte déclaré"), { target: { value: "RIGHTS_PRESERVATION" } });
  fireEvent.change(screen.getByLabelText("Description de l’acte"), { target: { value: "Réserve adressée" } });
  fireEvent.change(screen.getByLabelText("Références sources, une par ligne"), { target: { value: "ccap://clause/18" } });
  fireEvent.change(screen.getByLabelText("Références de preuve, une par ligne"), { target: { value: "document://courrier/sha256:abc" } });
  fireEvent.change(screen.getByLabelText("Version du contrat signé ou de l’avenant"), { target: { value: "version-2" } });
  fireEvent.submit(screen.getByRole("form", { name: "Enregistrer un acte contractuel sourcé" }));

  await waitFor(() => expect(inputs).toHaveLength(1));
  expect(inputs[0].contract_instrument_version_id).toBe("version-2");
});

test("une version contractuelle est enregistrée avec sources et preuves et reste déclarative", async () => {
  const inputs: RecordContractInstrumentVersionInput[] = [];
  const onCreate = vi.fn(async (_caseId: string, input: RecordContractInstrumentVersionInput) => { inputs.push(input); });
  render(<ContractInstrumentVersionsPanel caseId="case-1" versions={[]} supersessions={[]} status="READY" canManage onCreate={onCreate} />);
  fireEvent.change(screen.getByLabelText("Référence exacte de version"), { target: { value: "AVENANT-3-SIGNE" } });
  fireEvent.change(screen.getByLabelText("Sources d’identification, une par ligne"), { target: { value: "contract://amendment/3" } });
  fireEvent.change(screen.getByLabelText("Pièces justificatives, une par ligne"), { target: { value: "document://amendment/3" } });
  fireEvent.change(screen.getByLabelText("Type de version contractuelle à déclarer"), { target: { value: "AMENDMENT" } });
  fireEvent.submit(screen.getByRole("form", { name: "Déclarer une version contractuelle sourcée" }));

  await waitFor(() => expect(inputs).toHaveLength(1));
  expect(inputs[0]).toMatchObject({
    instrument_kind: "AMENDMENT", version_reference: "AVENANT-3-SIGNE",
    source_refs: ["contract://amendment/3"], evidence_refs: ["document://amendment/3"],
  });
  expect(screen.getByText(/authenticité, leur ordre juridique et leur applicabilité ne sont pas vérifiés/)).toBeInTheDocument();
});

test("le Patron peut déclarer qu’un avenant remplace une version enregistrée", async () => {
  const inputs: DeclareContractInstrumentSupersessionInput[] = [];
  const original: ContractInstrumentVersion = {
    contract_instrument_version_id: "signed-1", case_id: "case-1", instrument_kind: "SIGNED_CONTRACT",
    version_reference: "MARCHE-SIGNE-2026", source_refs: ["contract://signed/1"],
    evidence_refs: ["document://signed/1"], actor_id: "patron-1", recorded_at: "2026-09-29T00:00:00Z",
  };
  const amendment: ContractInstrumentVersion = {
    contract_instrument_version_id: "amendment-1", case_id: "case-1", instrument_kind: "AMENDMENT",
    version_reference: "AVENANT-1", source_refs: ["contract://amendment/1"],
    evidence_refs: ["document://amendment/1"], actor_id: "patron-1", recorded_at: "2026-09-29T00:00:00Z",
  };
  const onDeclare = vi.fn(async (_caseId: string, input: DeclareContractInstrumentSupersessionInput) => { inputs.push(input); });
  render(<ContractInstrumentVersionsPanel caseId="case-1" versions={[original, amendment]} supersessions={[]} status="READY" canManage onDeclareSupersession={onDeclare} />);
  fireEvent.change(screen.getByLabelText("Avenant déclaré comme remplaçant"), { target: { value: "amendment-1" } });
  fireEvent.change(screen.getByLabelText("Version remplacée par cet avenant"), { target: { value: "signed-1" } });
  fireEvent.change(screen.getByLabelText("Justification de la déclaration"), { target: { value: "Le Patron rattache les deux versions selon la pièce reçue." } });
  fireEvent.submit(screen.getByRole("form", { name: "Déclarer un remplacement contractuel" }));

  await waitFor(() => expect(inputs).toHaveLength(1));
  expect(inputs[0]).toMatchObject({
    replacing_contract_instrument_version_id: "amendment-1",
    replaced_contract_instrument_version_id: "signed-1",
    rationale: "Le Patron rattache les deux versions selon la pièce reçue.",
  });
});
