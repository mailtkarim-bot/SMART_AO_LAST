import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { useCapabilityAssessments } from "./useCapabilityAssessments";

const stamp = "2026-10-08T09:00:00+00:00";
const response = (caseId = "case-a") => ({ proposals: [{ case_id: caseId, source_evidence_state: "CURRENT" as const, source_evidence_evaluated_at: stamp }], gaps: [] });
describe("documentary assessment reading", () => {
  it("requires a scope and projects only state/date", async () => {
    const api = { getCapabilityAssessments: vi.fn().mockResolvedValue({ ...response(), proposals: [{ ...response().proposals[0], source_locator: "private", justification: "private", proposal_id: "private" }] }) };
    const { result, rerender } = renderHook(({ scope }) => useCapabilityAssessments(api, "case-a", scope), { initialProps: { scope: "" } });
    expect(api.getCapabilityAssessments).not.toHaveBeenCalled();
    rerender({scope:"collaborator-tenant-a"});
    await waitFor(() => expect(result.current.projection).toEqual([{state:"CURRENT", evaluatedAt:stamp}]));
    rerender({scope:""});
    expect(result.current.projection).toBeNull();
  });
  it.each([null, undefined, "", "invalid", "2026-02-30T09:00:00Z", "2026-10-08", "2026-10-08T25:00:00Z"])("preserves UNKNOWN with invalid/missing date %s", async (date) => {
    const api = {getCapabilityAssessments:vi.fn().mockResolvedValue({proposals:[{case_id:"case-a",source_evidence_state:"CURRENT",source_evidence_evaluated_at:date}],gaps:[]})};
    const {result} = renderHook(() => useCapabilityAssessments(api,"case-a","collaborator"));
    await waitFor(() => expect(result.current.projection).toEqual([{state:"UNKNOWN",evaluatedAt:null}]));
  });
  it("keeps historical missing state UNKNOWN and mixed evidence distinct", async () => {
    const api = {getCapabilityAssessments:vi.fn().mockResolvedValue({proposals:[{case_id:"case-a"},...['CURRENT','EXPIRED','UNKNOWN'].map(state=>({case_id:'case-a',source_evidence_state:state,source_evidence_evaluated_at:stamp}))],gaps:[]})};
    const {result} = renderHook(() => useCapabilityAssessments(api,"case-a","collaborator"));
    await waitFor(()=>expect(result.current.projection?.map(row=>row.state)).toEqual(['UNKNOWN','CURRENT','EXPIRED','UNKNOWN']));
  });
  it("ignores late results after case/scope changes", async () => {
    let resolve!: (value: ReturnType<typeof response>) => void;
    const pending = new Promise<ReturnType<typeof response>>(yes=>{resolve=yes;});
    const api={getCapabilityAssessments:vi.fn().mockReturnValueOnce(pending).mockResolvedValueOnce(response('case-b'))};
    const {result,rerender}=renderHook(({caseId,scope})=>useCapabilityAssessments(api,caseId,scope),{initialProps:{caseId:'case-a',scope:'tenant-a'}});
    rerender({caseId:'case-b',scope:'tenant-b'});
    expect(result.current.projection).toBeNull();
    await waitFor(()=>expect(result.current.projection).not.toBeNull());
    await act(async()=>resolve({...response(),proposals:[]}));
    expect(result.current.projection).toHaveLength(1);
  });
  it.each([{proposals:[{case_id:'foreign'}],gaps:[]},{proposals:null,gaps:[]},{proposals:[],gaps:null},{proposals:[{case_id:'case-a',source_evidence_state:'CONFIRMED'}],gaps:[]}])("refuses malformed/foreign readings", async(body)=>{
    const api={getCapabilityAssessments:vi.fn().mockResolvedValue(body)};
    const {result}=renderHook(()=>useCapabilityAssessments(api,'case-a','tenant-a'));
    await waitFor(()=>expect(result.current.error).toBeTruthy());
    expect(result.current.projection).toBeNull();
  });
  it("distinguishes empty results from read failure and retries only GET",async()=>{
    const api={getCapabilityAssessments:vi.fn().mockResolvedValueOnce({proposals:[],gaps:[]}).mockRejectedValueOnce(new Error('unavailable'))};
    const {result}=renderHook(()=>useCapabilityAssessments(api,'case-a','tenant-a'));
    await waitFor(()=>expect(result.current.projection).toEqual([]));
    await act(async()=>result.current.refresh());
    expect(result.current.error).toBeTruthy();expect(result.current.projection).toBeNull();
  });
});
