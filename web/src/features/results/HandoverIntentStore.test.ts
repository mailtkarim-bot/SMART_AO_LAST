import { expect, test } from "vitest";
import { HandoverIntentStore } from "./HandoverIntentStore";
test("retains an exact uncertain intent only in its original scope", () => {
  const store = new HandoverIntentStore();
  const intent = {
    kind: "PUBLISH" as const,
    caseId: "case-a",
    selected: "won:p5",
    input: {
      command_id: "a",
      idempotency_key: "b",
      correlation_id: "c",
      snapshot_id: "s",
      outcome_id: "won",
      submission_package_id: "p5"
    }
  };
  store.put("owner-a/case-a", {
    intent,
    phase: "UNKNOWN"
  });
  expect(store.getSnapshot().get("owner-b/case-a")).toBeUndefined();
  expect(store.getSnapshot().get("owner-a/case-a")?.intent).toEqual(intent);
  expect(() => store.put("owner-a/case-a", {
    intent: {
      ...intent,
      input: {
        ...intent.input,
        command_id: "other"
      }
    },
    phase: "UNKNOWN"
  })).toThrow();
});
