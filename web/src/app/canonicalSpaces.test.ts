import { describe, expect, it } from "vitest";

import { NAV_KEYS } from "./deepLink";
import { CATALOG_SURFACE_IDS, CANONICAL_SPACES, getCanonicalSpace } from "./canonicalSpaces";

describe("canonical product spaces", () => {
  it("materializes every canonical code exactly once", () => {
    expect(CANONICAL_SPACES.map((space) => space.code)).toEqual([
      "C00", "C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08",
      "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16",
    ]);
    const registeredSurfaceIds = CANONICAL_SPACES.flatMap((space) => space.surfaceIds);
    expect(new Set(registeredSurfaceIds).size).toBe(CATALOG_SURFACE_IDS.length);
    expect(new Set(registeredSurfaceIds)).toEqual(new Set(CATALOG_SURFACE_IDS));
  });

  it("keeps navigation and implementation status explicit", () => {
    for (const space of CANONICAL_SPACES) {
      if (space.navKey !== null) expect(NAV_KEYS).toContain(space.navKey);
      expect(["MATERIALIZED", "PARTIAL", "BACKLOG"]).toContain(space.status);
      expect(space.surfaceIds.length).toBeGreaterThan(0);
    }
    expect(getCanonicalSpace("C14")?.status).toBe("PARTIAL");
    expect(getCanonicalSpace("C09")?.status).toBe("BACKLOG");
  });
});
