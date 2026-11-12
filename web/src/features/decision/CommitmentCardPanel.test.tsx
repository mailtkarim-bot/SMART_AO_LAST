import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import type { ApiClient } from "../../infrastructure/api";
import { analysisFixture } from "../dce/analysisFixture.test-helper";
import { CommitmentCardPanel, CommitmentPendingStore } from "./CommitmentCardPanel";
function card(caseId = "case-a") {
  return {
    case_id: caseId,
    case_scope_fingerprint: "a".repeat(64),
    dce_version_id: "version-a",
    source_context_state: "CURRENT",
    axes: analysisFixture().axes,
    points: [],
    coverage: null,
    dossier_review: null,
    references: [],
    truncated: false,
    analysis_complete: false,
    gate_effect: "NONE",
    current_decision: null,
    history: [],
    history_has_more: false
  };
}
it("shows twelve axes and never creates a decision from a read", async () => {
  const api = {
    getCommitmentCard: vi.fn().mockResolvedValue(card()),
    createDecision: vi.fn()
  } as unknown as ApiClient;
  render(<CommitmentCardPanel api={api} enabled caseId="case-a" actorId="patron" ownerKey="owner" scopeKey="session" pendingStore={new CommitmentPendingStore()} />);
  await screen.findByText("Aucune décision enregistrée.");
  expect(screen.getByRole("heading", {
    name: "Carte d’engagement de l’Affaire"
  })).toBeInTheDocument();
  expect(screen.getAllByText("NON_EVALUATED")).toHaveLength(12);
  expect(api.createDecision).not.toHaveBeenCalled();
});
it("masks old case facts immediately and refuses discordant reads", async () => {
  const api = {
    getCommitmentCard: vi.fn().mockResolvedValue(card())
  } as unknown as ApiClient;
  const store = new CommitmentPendingStore();
  const view = render(<CommitmentCardPanel api={api} enabled caseId="case-a" actorId="patron" ownerKey="owner" scopeKey="session" pendingStore={store} />);
  await screen.findByText("Aucune décision enregistrée.");
  view.rerender(<CommitmentCardPanel api={api} enabled caseId="case-b" actorId="patron" ownerKey="owner" scopeKey="session" pendingStore={store} />);
  expect(screen.queryByText("Aucune décision enregistrée.")).not.toBeInTheDocument();
  await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("Lecture indisponible"));
});
it("keeps unknown commands frozen with identical IDs and no reconciliation read", async () => {
  const read = vi.fn().mockResolvedValue(card());
  const create = vi.fn().mockRejectedValue(Object.assign(Error("timeout"), {
    status: 503
  }));
  const api = {
    getCommitmentCard: read,
    createDecision: create
  } as unknown as ApiClient;
  render(<CommitmentCardPanel api={api} enabled caseId="case-a" actorId="patron" ownerKey="owner" scopeKey="session" pendingStore={new CommitmentPendingStore()} />);
  await screen.findByText("Aucune décision enregistrée.");
  fireEvent.click(screen.getByRole("button", {
    name: "Créer un brouillon de décision"
  }));
  await screen.findByText(/UNKNOWN — résultat de l’acte inconnu/);
  expect(screen.queryByText("Aucune décision enregistrée.")).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", {
    name: "Réessayer exactement cet acte"
  }));
  await waitFor(() => expect(create).toHaveBeenCalledTimes(2));
  expect(create.mock.calls[0][1]).toEqual(create.mock.calls[1][1]);
  expect(read).toHaveBeenCalledTimes(1);
});
it("never offers an impossible new draft while a current finalized decision exists", async () => {
  const value = {
    ...card(),
    current_decision: {
      decision_id: "d1",
      aggregate_revision: 2,
      cycle_number: 1,
      lifecycle: "FINALIZED",
      outcome: "NO_GO",
      validity: "CURRENT",
      context_status: "FROZEN",
      state: "CURRENT",
      final_justification: "Accès impossible",
      finalized_at: null,
      finalized_by_actor_id: "patron",
      context_id: "ctx",
      context_fingerprint: "b".repeat(64),
      rationale: "Revue",
      unknowns: [],
      references: [],
      assessment_snapshots: [],
      assessment_links: [],
      conditions: [],
      transitions: [],
      truncated: false
    }
  };
  const api = {
    getCommitmentCard: vi.fn().mockResolvedValue(value)
  } as unknown as ApiClient;
  render(<CommitmentCardPanel api={api} enabled caseId="case-a" actorId="patron" ownerKey="owner" scopeKey="session" pendingStore={new CommitmentPendingStore()} />);
  await screen.findByText("Accès impossible", {
    exact: false
  });
  expect(screen.queryByRole("button", {
    name: "Préparer une nouvelle décision"
  })).not.toBeInTheDocument();
});
it("refuses a late response for another DCE version in the same case", async () => {
  const api = {
    getCommitmentCard: vi.fn().mockResolvedValue(card())
  } as unknown as ApiClient;
  render(<CommitmentCardPanel api={api} enabled caseId="case-a" actorId="patron" ownerKey="owner" scopeKey="session" dceVersionId="version-b" pendingStore={new CommitmentPendingStore()} />);
  await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("Lecture indisponible"));
  expect(screen.queryByText("Aucune décision enregistrée.")).not.toBeInTheDocument();
});
it("requires confirmation again after a source reread", async () => {
  const decision = {
    decision_id: "d1",
    aggregate_revision: 0,
    cycle_number: 1,
    lifecycle: "DRAFT",
    outcome: "UNDECIDED",
    validity: "CURRENT",
    context_status: "INCOMPLETE",
    state: "DRAFT",
    final_justification: null,
    finalized_at: null,
    finalized_by_actor_id: null,
    context_id: null,
    context_fingerprint: null,
    rationale: null,
    unknowns: [],
    references: [],
    assessment_snapshots: [],
    assessment_links: [],
    conditions: [],
    transitions: [],
    truncated: false
  };
  const initial = {
    ...card(),
    current_decision: decision,
    references: [{aggregate_type:"DCE_REQUIREMENT",aggregate_id:"req-a",aggregate_revision:1,content_hash:null,reference_role:"CLAUSE"}, {
      aggregate_type: "ANALYSIS_ASSESSMENT",
      aggregate_id: "act-a",
      aggregate_revision: 1,
      content_hash: "a".repeat(64),
      reference_role: "CRITICAL_POINT"
    }]
  };
  const changed = {
    ...initial,
    references: [initial.references[0], {
      ...initial.references[1],
      aggregate_id: "act-b",
      aggregate_revision: 2
    }]
  };
  const api = {
    getCommitmentCard: vi.fn().mockResolvedValueOnce(initial).mockResolvedValue(changed)
  } as unknown as ApiClient;
  render(<CommitmentCardPanel api={api} enabled caseId="case-a" actorId="patron" ownerKey="owner" scopeKey="session" pendingStore={new CommitmentPendingStore()} />);
  await screen.findByText("Présenter ces références à la décision");
  fireEvent.change(screen.getByLabelText("Justification de l’acte sur la carte"), {
    target: {
      value: "Revue de la première lecture"
    }
  });
  fireEvent.click(screen.getByLabelText(/Je confirme l’acte/));
  expect(screen.getByRole("button", {
    name: "Geler ces références pour revue"
  })).not.toBeDisabled();
  fireEvent.click(screen.getByRole("button", {
    name: "Relire la carte et l’historique"
  }));
  await waitFor(() => expect(screen.getByRole("button", {
    name: "Geler ces références pour revue"
  })).toBeDisabled());
});


it("suspend la carte sans GET pendant une incertitude sur ses sources",()=>{
 const read=vi.fn();render(<CommitmentCardPanel api={{getCommitmentCard:read} as unknown as ApiClient} enabled sourceReadBlocked caseId="case-a" actorId="patron" ownerKey="owner" scopeKey="session" pendingStore={new CommitmentPendingStore()}/>);
 expect(read).not.toHaveBeenCalled();expect(screen.getByText(/Carte suspendue/)).toBeVisible();
});

it("demande explicitement un nouveau brouillon sans présumer la requalification",async()=>{
 const value={...card(),current_decision:{decision_id:"old",aggregate_revision:3,cycle_number:1,case_scope_fingerprint:"a".repeat(64),lifecycle:"FINALIZED",outcome:"CONDITIONAL_GO",validity:"CURRENT",context_status:"STALE",state:"REVIEW_REQUIRED",final_justification:"Ancien acte",finalized_at:null,finalized_by_actor_id:"patron",context_id:"old-ctx",context_fingerprint:"b".repeat(64),rationale:"Ancien contexte",unknowns:[],references:[],assessment_snapshots:[],assessment_links:[],conditions:[],transitions:[],truncated:false}};
 const create=vi.fn().mockRejectedValue(Object.assign(new Error("Conflit"),{status:409}));
 const api={getCommitmentCard:vi.fn().mockResolvedValue(value),createDecision:create} as unknown as ApiClient;
 render(<CommitmentCardPanel api={api} enabled caseId="case-a" actorId="patron" ownerKey="owner" scopeKey="session" pendingStore={new CommitmentPendingStore()}/>);
 const button=await screen.findByRole("button",{name:"Demander un nouveau brouillon"});expect(button).toBeDisabled();expect(create).not.toHaveBeenCalled();
 fireEvent.click(screen.getByLabelText(/Je confirme la préparation d’un nouveau brouillon/));fireEvent.click(button);
 await waitFor(()=>expect(create).toHaveBeenCalledTimes(1));await screen.findByText(/refusé pour conflit/);
});


function sourceCard(){
 const point={item_id:"req-a",kind:"REQUIREMENT",native_type:"CANDIDATURE_DOCUMENT",native_state:"PENDING_HUMAN_CONFIRMATION",native_revision:0,title:"Signal source",source_state:"CURRENT_SOURCE",source_anchor:{dce_version_id:"version-a",dce_document_id:"doc-a",extraction_id:"ext-a",source_sha256:"a".repeat(64),fragment_sha256:"b".repeat(64),locator_state:"RESOLVED",locator:{kind:"pdf_page",coordinates:{page:1}}},source_context_sha256:"c".repeat(64),source_excerpt:"Signal exact",source_excerpt_state:"EXACT_SOURCE",start_byte_offset:0,end_byte_offset:12,lot_state:"UNKNOWN",lot_numbers:[],human_assessment:null,follow_ups:[],follow_up_state:"UNKNOWN"};
 const value={...card(),points:[{point_key:"req-a",axes:["CANDIDATURE"],point,hypotheses:null,relations_state:"UNKNOWN",condition_links:[]}]};
 return value;
}

it("raccorde une confirmation native explicite sans présumer l’analyse ni la conformité",async()=>{
 const value=sourceCard();
 const confirm=vi.fn(async(_id,input)=>({status:"SUCCEEDED",command_id:input.command_id,idempotency_key:input.idempotency_key,result_code:"DCE_REQUIREMENT_CONFIRMED",aggregate_refs:[{aggregate_type:"DCE_REQUIREMENT_CONFIRMATION",aggregate_id:input.confirmation_id,aggregate_revision:1}],event_ids:[],replayed:false}));
 const api={getCommitmentCard:vi.fn().mockResolvedValue(value),confirmDceRequirement:confirm} as unknown as ApiClient;
 render(<CommitmentCardPanel api={api} enabled caseId="case-a" actorId="patron" ownerKey="owner" scopeKey="session" pendingStore={new CommitmentPendingStore()}/>);
 const button=await screen.findByRole("button",{name:"Confirmer le signal source"});expect(button).toBeDisabled();expect(confirm).not.toHaveBeenCalled();
 fireEvent.click(screen.getByLabelText(/Je confirme avoir relu ce signal/));fireEvent.click(button);await waitFor(()=>expect(confirm).toHaveBeenCalledTimes(1));
 expect(confirm.mock.calls[0][0]).toBe("req-a");expect(confirm.mock.calls[0][1]).toMatchObject({outcome:"CONFIRMED",reason_code:"SOURCE_REVIEWED",expected_confirmation_revision:0});
});


it("identifie chaque confirmation et confirme seulement le second signal choisi",async()=>{
 const value=sourceCard();value.points.push({...value.points[0],point_key:"req-b",point:{...value.points[0].point,item_id:"req-b",source_excerpt:"Second signal exact"}});
 const confirm=vi.fn().mockRejectedValue(new Error("UNKNOWN"));const api={getCommitmentCard:vi.fn().mockResolvedValue(value),confirmDceRequirement:confirm} as unknown as ApiClient;
 render(<CommitmentCardPanel api={api} enabled caseId="case-a" actorId="patron" ownerKey="owner" scopeKey="session" pendingStore={new CommitmentPendingStore()}/>);
 const second=await screen.findByRole("region",{name:"Confirmation du signal req-b"});expect(within(second).getByText("Second signal exact")).toBeVisible();
 fireEvent.click(within(second).getByLabelText(/Je confirme avoir relu/));fireEvent.click(within(second).getByRole("button",{name:"Confirmer le signal source"}));await waitFor(()=>expect(confirm).toHaveBeenCalledOnce());expect(confirm.mock.calls[0][0]).toBe("req-b");
});

it("reprend la confirmation UNKNOWN avec son corps exact avant toute relecture",async()=>{
 let done=false;const value=sourceCard();
 const read=vi.fn(async()=>done?{...value,references:[{aggregate_type:"DCE_REQUIREMENT",aggregate_id:"req-a",aggregate_revision:1,content_hash:null,reference_role:"CLAUSE"}]}:value);
 const confirm=vi.fn().mockRejectedValueOnce(new Error("UNKNOWN")).mockImplementationOnce(async(_id,input)=>{done=true;return{status:"SUCCEEDED",command_id:input.command_id,idempotency_key:input.idempotency_key,result_code:"DCE_REQUIREMENT_CONFIRMED",aggregate_refs:[{aggregate_type:"DCE_REQUIREMENT_CONFIRMATION",aggregate_id:input.confirmation_id,aggregate_revision:1}],event_ids:[],replayed:true};});
 const api={getCommitmentCard:read,confirmDceRequirement:confirm} as unknown as ApiClient;render(<CommitmentCardPanel api={api} enabled caseId="case-a" actorId="patron" ownerKey="owner" scopeKey="session" pendingStore={new CommitmentPendingStore()}/>);
 await screen.findByRole("button",{name:"Confirmer le signal source"});fireEvent.click(screen.getByLabelText(/Je confirme avoir relu/));fireEvent.click(screen.getByRole("button",{name:"Confirmer le signal source"}));await screen.findByText(/UNKNOWN — résultat/);expect(read).toHaveBeenCalledTimes(1);
 fireEvent.click(screen.getByRole("button",{name:"Réessayer exactement cet acte"}));await waitFor(()=>expect(read).toHaveBeenCalledTimes(2));expect(confirm.mock.calls[1]).toEqual(confirm.mock.calls[0]);
});
