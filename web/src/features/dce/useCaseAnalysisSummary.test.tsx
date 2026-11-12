import { act, renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { ApiClient } from "../../infrastructure/api";
import { useCaseAnalysisSummary } from "./useCaseAnalysisSummary";
import { analysisFixture } from "./analysisFixture.test-helper";

function deferred<T>() { let resolve!: (value: T)=>void; const promise=new Promise<T>(r=>{resolve=r;}); return {promise,resolve}; }
function setup(getCaseAnalysisSummary=vi.fn().mockResolvedValue(analysisFixture())) {
 const api={getCaseAnalysisSummary} as unknown as ApiClient;
 return {getCaseAnalysisSummary,...renderHook(({caseId,scope,version})=>useCaseAnalysisSummary(api,caseId,scope,version),
  {initialProps:{caseId:"case-a",scope:"tenant/session/patron",version:"version-a" as string|null}})};
}

describe("case analysis summary",()=>{
 it("loads only the matching case/version",async()=>{const h=setup();await act(async()=>{await h.result.current.refresh();});expect(h.result.current.summary?.axes).toHaveLength(12);});
 it.each(["case","session","version","role"])("masks immediately after %s changes",async(field)=>{
  const h=setup();await act(async()=>{await h.result.current.refresh();});
  h.rerender({caseId:field==="case"?"case-b":"case-a",scope:field==="session"?"new-session":field==="role"?"":"tenant/session/patron",version:field==="version"?"version-b":"version-a"});
  expect(h.result.current.summary).toBeNull();
 });
 it("ignores a late response after leaving and returning to the same scope",async()=>{
  const d=deferred<ReturnType<typeof analysisFixture>>();const h=setup(vi.fn().mockReturnValue(d.promise));
  let pending!:Promise<void>;act(()=>{pending=h.result.current.refresh();});
  h.rerender({caseId:"case-b",scope:"tenant/session/patron",version:"version-a"});
  h.rerender({caseId:"case-a",scope:"tenant/session/patron",version:"version-a"});
  await act(async()=>{d.resolve(analysisFixture());await pending;});expect(h.result.current.summary).toBeNull();
 });
 it("refuses a discordant source version and duplicate axes",async()=>{
  const fixture=analysisFixture();fixture.axes[0].code=fixture.axes[1].code;
  const h=setup(vi.fn().mockResolvedValue(fixture));await act(async()=>{await h.result.current.refresh();});
  expect(h.result.current.summary).toBeNull();expect(h.result.current.error).not.toBeNull();
 });
 it("refuses another case or version",async()=>{
  const h=setup(vi.fn().mockResolvedValue({...analysisFixture(),dce_version_id:"other-version"}));
  await act(async()=>{await h.result.current.refresh();});expect(h.result.current.summary).toBeNull();
 });
 it("keeps error payload private and clears old proof while reloading",async()=>{
  const get=vi.fn().mockResolvedValueOnce(analysisFixture()).mockRejectedValueOnce({status:409,detail:"private-debug"});
  const h=setup(get);await act(async()=>{await h.result.current.refresh();});
  await act(async()=>{await h.result.current.refresh();});expect(h.result.current.summary).toBeNull();
  expect(h.result.current.error).not.toContain("private-debug");
 });
 it("does not call API without an authenticated version scope",async()=>{
  const h=setup();h.rerender({caseId:"case-a",scope:"",version:null});await act(async()=>{await h.result.current.refresh();});
  expect(h.getCaseAnalysisSummary).not.toHaveBeenCalled();
 });
});

it.each(["case","session","version","role"])("does not resurrect loaded proof after %s round trip",async(field)=>{
 const h=setup();await act(async()=>{await h.result.current.refresh();});expect(h.result.current.summary).not.toBeNull();
 h.rerender({caseId:field==="case"?"case-b":"case-a",scope:field==="session"?"new-session":field==="role"?"":"tenant/session/patron",version:field==="version"?"version-b":"version-a"});
 h.rerender({caseId:"case-a",scope:"tenant/session/patron",version:"version-a"});
 expect(h.result.current.summary).toBeNull();
});

it.each(["source","endpoint"])("refuses a follow-up with discordant %s proof",async(bad)=>{
 const fixture=analysisFixture();
 fixture.axes[4].items=[{item_id:"risk-a",kind:"RISK",native_type:"CCAP",native_state:"OPEN",title:null,source_state:bad==="source"?"UNKNOWN":"CURRENT_SOURCE",source_anchor:null,start_byte_offset:null,end_byte_offset:null,lot_numbers:[],lot_state:"UNKNOWN",applicability:"UNKNOWN",responsible:null,action:null,consequences:"UNKNOWN",follow_up_state:"RECORDED",follow_ups:[{kind:"ACTION",record_id:"action-a",revision:1,state:"OPEN",relation_id:null,risk_id:bad==="endpoint"?"foreign-risk":"risk-a",requirement_id:null,description:"Private action",consequence:null,responsible_actor_id:null,due_at:null,scope:"EXACT_RECORDED_RELATION"}]}];
 const h=setup(vi.fn().mockResolvedValue(fixture));await act(async()=>{await h.result.current.refresh();});expect(h.result.current.summary).toBeNull();
});

it.each(["region","unproved","severity"])("refuses discordant anatomy %s",async(bad)=>{
 const fixture=analysisFixture();
 fixture.axes[4].items=[{item_id:"risk-a",kind:"RISK",native_type:"CCAP",native_state:"OPEN",title:null,source_state:bad==="region"?"CURRENT_SOURCE":"UNKNOWN",source_anchor:null,start_byte_offset:0,end_byte_offset:1,lot_numbers:[],lot_state:"UNKNOWN",applicability:"UNKNOWN",responsible:null,action:null,consequences:"UNKNOWN",source_excerpt:bad==="severity"?null:"É",source_excerpt_state:bad==="severity"?"UNKNOWN":"EXACT_SOURCE",severity:bad==="severity"?"CRITICAL":"UNKNOWN",expected_evidence:"UNKNOWN",residual_risk:"UNKNOWN"}];
 const h=setup(vi.fn().mockResolvedValue(fixture));await act(async()=>{await h.result.current.refresh();});expect(h.result.current.summary).toBeNull();
});
