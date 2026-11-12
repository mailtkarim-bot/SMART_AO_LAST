import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { useCapabilityCandidates } from "./useCapabilityCandidates";

const stamp = "2026-10-08T09:00:00.123456Z";
const candidates = [{
  capability_id: "private-capability-id", capability_kind: "EQUIPMENT" as const,
  name: "Levage synthétique", version_id: "private-version-id", version_number: 2,
  title: "Version chantier synthétique", valid_from: "2026-10-01T00:00:00Z",
  valid_until: null, validity_state: "CURRENT" as const,
  source_evidence_state: "CURRENT" as const, evaluated_at: stamp,
  proof_document_ids: ["private-proof-id"], summary: "private summary",
}];
function deferred<T>() { let resolve!: (value:T)=>void; const promise=new Promise<T>(yes=>{resolve=yes;}); return {promise,resolve}; }
describe("useCapabilityCandidates",()=>{
  it("reads only inside a collaborator scope and keeps transport IDs out of the display projection",async()=>{
    const api={getCapabilityCandidates:vi.fn().mockResolvedValue(candidates)};
    const {result,rerender}=renderHook(({scope})=>useCapabilityCandidates(api,"case-a",scope),{initialProps:{scope:""}});
    expect(api.getCapabilityCandidates).not.toHaveBeenCalled();
    rerender({scope:"tenant-a:collaborator"});
    await waitFor(()=>expect(result.current.candidates).toHaveLength(1));
    expect(result.current.candidates?.[0]).toEqual({
      capabilityId:"private-capability-id",kind:"EQUIPMENT",name:"Levage synthétique",
      versionId:"private-version-id",versionNumber:2,title:"Version chantier synthétique",
      validFrom:"2026-10-01T00:00:00Z",validUntil:null,validityState:"CURRENT",
      sourceEvidenceState:"CURRENT",evaluatedAt:stamp,
    });
    rerender({scope:""});expect(result.current.candidates).toBeNull();
    expect(api.getCapabilityCandidates).toHaveBeenCalledWith("case-a");
  });
  it.each([null,"","not-a-date","2026-02-30T09:00:00Z"])("keeps evidence UNKNOWN for missing/invalid evaluated_at %s",async evaluated_at=>{
    const api={getCapabilityCandidates:vi.fn().mockResolvedValue([{...candidates[0],evaluated_at}])};
    const {result}=renderHook(()=>useCapabilityCandidates(api,"case-a","collaborator"));
    await waitFor(()=>expect(result.current.candidates?.[0]).toMatchObject({sourceEvidenceState:"UNKNOWN",evaluatedAt:null}));
  });
  it.each(["2026-02-30T09:00:00Z", "2026-10-08", "invalid"])("keeps a candidate but marks malformed validity dates UNKNOWN: %s",async invalidDate=>{
    const api={getCapabilityCandidates:vi.fn().mockResolvedValue([{...candidates[0],valid_from:invalidDate}])};
    const {result}=renderHook(()=>useCapabilityCandidates(api,"case-a","collaborator"));
    await waitFor(()=>expect(result.current.candidates?.[0]).toMatchObject({validityState:"UNKNOWN",validFrom:null,validUntil:null,sourceEvidenceState:"CURRENT"}));
  });
  it("masks an old Case response immediately and ignores it after a scope switch",async()=>{
    const old=deferred<typeof candidates>();const api={getCapabilityCandidates:vi.fn().mockReturnValueOnce(old.promise).mockResolvedValueOnce(candidates)};
    const {result,rerender}=renderHook(({caseId,scope})=>useCapabilityCandidates(api,caseId,scope),{initialProps:{caseId:"case-a",scope:"tenant-a"}});
    rerender({caseId:"case-b",scope:"tenant-b"});expect(result.current.candidates).toBeNull();
    await waitFor(()=>expect(result.current.candidates).toHaveLength(1));
    await act(async()=>old.resolve([]));expect(result.current.candidates).toHaveLength(1);
  });
  it.each([
    [{...candidates[0],capability_kind:"UNSUPPORTED"}],
    [{...candidates[0],validity_state:"UNKNOWN"}],
    [{...candidates[0],evaluated_at:"2026-10-08"}],
  ])("rejects malformed candidate contracts",async body=>{
    const api={getCapabilityCandidates:vi.fn().mockResolvedValue(body)};
    const {result}=renderHook(()=>useCapabilityCandidates(api,"case-a","collaborator"));
    await waitFor(()=>expect(result.current.error).toBeTruthy());expect(result.current.candidates).toBeNull();
  });
});
