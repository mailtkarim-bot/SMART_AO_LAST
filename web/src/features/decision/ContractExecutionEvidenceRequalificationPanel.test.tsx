import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { expect, test, vi } from "vitest";
import type {
  ContractExecutionEvidence,
  ContractInstrumentSupersession,
  ContractInstrumentVersion,
  RecordContractExecutionEvidenceRequalificationInput,
} from "../../shared/types";
import { ContractExecutionEvidenceRequalificationPanel } from "./ContractExecutionEvidenceRequalificationPanel";

const act: ContractExecutionEvidence = {
  act_id: "act-old", case_id: "case-1", act_kind: "RIGHTS_PRESERVATION", summary: "Réserve envoyée",
  reception_outcome: "UNKNOWN",
  source_refs: ["contract://clause/18"], evidence_refs: ["document://courrier/sha256:abc"],
  declared_event_date: "2026-09-28", case_dce_version_id_at_recording: null, version_relation: "UNKNOWN",
  contract_instrument_version_relation: "REVIEW_REQUIRED", contract_instrument_version_id: "signed-v1",
  contract_instrument_version: null, actor_id: "patron-1", recorded_at: "2026-09-28T10:00:00Z",
};
const versions: ContractInstrumentVersion[] = [
  {
    contract_instrument_version_id: "signed-v1", case_id: "case-1", instrument_kind: "SIGNED_CONTRACT",
    version_reference: "MARCHE-SIGNE-1", source_refs: ["contract://signed/1"], evidence_refs: ["document://signed/1"],
    actor_id: "patron-1", recorded_at: "2026-09-28T00:00:00Z",
  },
  {
    contract_instrument_version_id: "amendment-v2", case_id: "case-1", instrument_kind: "AMENDMENT",
    version_reference: "AVENANT-2", source_refs: ["contract://amendment/2"], evidence_refs: ["document://amendment/2"],
    actor_id: "patron-1", recorded_at: "2026-09-29T00:00:00Z",
  },
];
const supersessions: ContractInstrumentSupersession[] = [{
  supersession_id: "supersession-1", case_id: "case-1",
  replacing_contract_instrument_version_id: "amendment-v2", replacing_instrument_kind: "AMENDMENT",
  replacing_version_reference: "AVENANT-2", replaced_contract_instrument_version_id: "signed-v1",
  replaced_instrument_kind: "SIGNED_CONTRACT", replaced_version_reference: "MARCHE-SIGNE-1",
  rationale: "Déclaration Patron précédente", actor_id: "patron-1", recorded_at: "2026-09-29T10:00:00Z",
}];

test("le rejeu reprend la même requalification et laisse la portée juridique explicitement non évaluée", async () => {
  const inputs: RecordContractExecutionEvidenceRequalificationInput[] = [];
  const onRecord = vi.fn(async (_caseId: string, input: RecordContractExecutionEvidenceRequalificationInput) => {
    inputs.push(input);
    if (inputs.length === 1) throw new Error("interrupted");
  });
  render(<ContractExecutionEvidenceRequalificationPanel
    caseId="case-1" acts={[act]} versions={versions} supersessions={supersessions} requalifications={[]}
    status="READY" canManage onRecord={onRecord}
  />);
  fireEvent.change(screen.getByLabelText("Acte à requalifier"), { target: { value: "act-old" } });
  fireEvent.change(screen.getByLabelText("Déclaration de remplacement examinée"), { target: { value: "supersession-1" } });
  fireEvent.change(screen.getByLabelText("Décision de requalification"), { target: { value: "RELINKED_TO_DECLARED_VERSION" } });
  fireEvent.change(screen.getByLabelText("Version déclarée après requalification"), { target: { value: "amendment-v2" } });
  fireEvent.change(screen.getByLabelText("Justification de requalification"), { target: { value: "Référence relue par le Patron à partir de l’avenant." } });
  fireEvent.submit(screen.getByRole("form", { name: "Requalifier un acte contractuel" }));
  expect(await screen.findByText(/résultat non confirmé/i)).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Réessayer la requalification" }));

  await waitFor(() => expect(onRecord).toHaveBeenCalledTimes(2));
  expect(inputs[0]).toEqual(inputs[1]);
  expect(inputs[0]).toMatchObject({
    act_id: "act-old", supersession_id: "supersession-1", expected_revision: 0,
    decision: "RELINKED_TO_DECLARED_VERSION", resulting_contract_instrument_version_id: "amendment-v2",
  });
  expect(screen.getByText(/ne confirme pas l’applicabilité juridique/i)).toBeInTheDocument();
});

test("affiche la requalification comme un acte distinct et garde le signal d’origine", () => {
  render(<ContractExecutionEvidenceRequalificationPanel
    caseId="case-1" acts={[act]} versions={versions} supersessions={supersessions}
    requalifications={[{
      requalification_id: "requal-1", case_id: "case-1", act_id: "act-old",
      act_kind: "RIGHTS_PRESERVATION", act_summary: "Réserve envoyée", supersession_id: "supersession-1",
      review_revision: 1, decision: "RELINKED_TO_DECLARED_VERSION",
      resulting_contract_instrument_version_id: "amendment-v2", resulting_instrument_kind: "AMENDMENT",
      resulting_version_reference: "AVENANT-2", rationale: "Rattachement relu par le Patron",
      actor_id: "patron-1", recorded_at: "2026-09-29T12:00:00Z",
    }]}
    status="READY" canManage={false}
  />);

  expect(screen.getByText(/Revue 1 · Rattaché à une autre version déclarée/)).toBeInTheDocument();
  expect(screen.getByText(/Signal source conservé : REVIEW_REQUIRED/)).toBeInTheDocument();
  expect(screen.getAllByText(/REVIEW_REQUIRED/).length).toBeGreaterThan(0);
  expect(screen.getByText(/ne confirme pas l’applicabilité juridique/i)).toBeInTheDocument();
});
