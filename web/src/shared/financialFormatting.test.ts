import { describe, expect, it } from "vitest";
import { formatBasisPoints, formatMinorMoney } from "./financialFormatting";

describe("exact integer financial presentation", () => {
  it.each([[3299, "32.99"], [-1, "-0.01"], [-9007199254700001, "-90071992547000.01"]])("formats %s basis points exactly", (value, expected) => {
    expect(formatBasisPoints(value)).toBe(expected);
  });
  it.each([[125000, "1250,00€"], [-1, "-0,01€"], [-9007199254700001, "-90071992547000,01€"]])("formats %s centimes exactly", (value, expected) => {
    expect(formatMinorMoney(value).replace(/\s/g, "")).toBe(expected);
  });
  it("keeps unsafe numeric inputs unknown", () => {
    expect(formatMinorMoney(Number.MAX_SAFE_INTEGER + 1)).toBe("UNKNOWN");
    expect(formatBasisPoints(NaN)).toBe("UNKNOWN");
  });
});
