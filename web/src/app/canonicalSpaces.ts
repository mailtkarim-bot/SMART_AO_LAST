import type { NavKey } from "./deepLink";

export type CanonicalSpaceCode = `C${string}`;
export type CanonicalSpaceStatus = "MATERIALIZED" | "PARTIAL" | "BACKLOG";

export type CanonicalSpace = {
  code: CanonicalSpaceCode;
  label: string;
  navKey: NavKey | null;
  status: CanonicalSpaceStatus;
  surfaceIds: readonly string[];
};

/**
 * Canonical product spaces are an inventory, not a promise that every surface
 * is already implemented. Surface-level proof remains tracked in the roadmap.
 */
export const CANONICAL_SPACES = [
  { code: "C00", label: "Transversal", navKey: null, status: "PARTIAL", surfaceIds: ["GLB-01", "GLB-02", "GLB-05", "COL-02", "AUTH-07", "AUTH-08", "SYS-01", "SYS-02", "SYS-03"] },
  { code: "C01", label: "Accueil", navKey: "overview", status: "MATERIALIZED", surfaceIds: ["ONB-02", "ONB-04", "GLB-03", "GLB-04", "HOME-01", "HOME-02", "HOME-03", "MOB-01", "MOB-05"] },
  { code: "C02", label: "Radar", navKey: "opportunities", status: "MATERIALIZED", surfaceIds: ["OPP-01", "OPP-02"] },
  { code: "C03", label: "Opportunité", navKey: "opportunities", status: "PARTIAL", surfaceIds: ["OPP-03", "OPP-04"] },
  { code: "C04", label: "Portefeuille", navKey: "review", status: "MATERIALIZED", surfaceIds: ["AFF-01"] },
  { code: "C05", label: "Synthèse Affaire", navKey: "review", status: "PARTIAL", surfaceIds: ["AFF-02", "AFF-03", "DCE-07", "DCE-08", "DCE-10", "DCE-11", "DCE-12", "DCE-13", "COL-01", "MOB-02", "MOB-03", "MOB-04"] },
  { code: "C06", label: "Documents et preuves", navKey: "dce", status: "MATERIALIZED", surfaceIds: ["DCE-01", "DCE-02", "DCE-03", "DCE-04", "DCE-05", "DCE-06", "DCE-09"] },
  { code: "C07", label: "Décision", navKey: "decision", status: "MATERIALIZED", surfaceIds: ["DEC-01", "DEC-02"] },
  { code: "C08", label: "Prix", navKey: "review", status: "MATERIALIZED", surfaceIds: ["PRI-01", "PRI-02", "PRI-03", "PRI-04", "PRI-05"] },
  { code: "C09", label: "Partenaires", navKey: null, status: "BACKLOG", surfaceIds: ["PAR-01", "PAR-02"] },
  { code: "C10", label: "Réponse", navKey: "preparation", status: "MATERIALIZED", surfaceIds: ["RES-01", "RES-02", "RES-03", "RES-04", "RES-05", "RES-06", "RES-07"] },
  { code: "C11", label: "Remise", navKey: "submission", status: "MATERIALIZED", surfaceIds: ["SUB-01", "SUB-02", "SUB-03", "SUB-04", "SUB-05", "SUB-06", "SUB-07"] },
  { code: "C12", label: "Résultat et passation", navKey: null, status: "BACKLOG", surfaceIds: ["OUT-01", "OUT-02", "OUT-03", "OUT-04"] },
  { code: "C13", label: "Entreprise", navKey: "library", status: "MATERIALIZED", surfaceIds: ["ONB-03", "ENT-01", "ENT-02", "ENT-03", "ENT-04", "ENT-05", "ENT-06", "ENT-07", "ENT-08", "ENT-09", "ENT-10", "ENT-11", "ENT-12"] },
  { code: "C14", label: "Administration", navKey: null, status: "PARTIAL", surfaceIds: ["ADM-01", "ADM-02", "ADM-03", "ADM-04", "ADM-05", "ADM-06", "ADM-07", "ADM-08", "ADM-09", "ADM-10", "ADM-11"] },
  { code: "C15", label: "Accès", navKey: "wizard", status: "PARTIAL", surfaceIds: ["AUTH-01", "AUTH-02", "AUTH-03", "AUTH-04", "AUTH-05", "AUTH-06", "ONB-01"] },
  { code: "C16", label: "Paquet tiers", navKey: null, status: "PARTIAL", surfaceIds: ["SHR-01", "SHR-02", "SHR-03", "SHR-04"] },
] as const satisfies readonly CanonicalSpace[];

export const CATALOG_SURFACE_IDS = [
  "AUTH-01", "AUTH-02", "AUTH-03", "AUTH-04", "AUTH-05", "AUTH-06", "AUTH-07", "AUTH-08",
  "ONB-01", "ONB-02", "ONB-03", "ONB-04",
  "GLB-01", "GLB-02", "GLB-03", "GLB-04", "GLB-05",
  "HOME-01", "HOME-02", "HOME-03",
  "OPP-01", "OPP-02", "OPP-03", "OPP-04",
  "AFF-01", "AFF-02", "AFF-03",
  "DCE-01", "DCE-02", "DCE-03", "DCE-04", "DCE-05", "DCE-06", "DCE-07", "DCE-08", "DCE-09", "DCE-10", "DCE-11", "DCE-12", "DCE-13",
  "DEC-01", "DEC-02",
  "PRI-01", "PRI-02", "PRI-03", "PRI-04", "PRI-05",
  "PAR-01", "PAR-02",
  "COL-01", "COL-02",
  "RES-01", "RES-02", "RES-03", "RES-04", "RES-05", "RES-06", "RES-07",
  "SUB-01", "SUB-02", "SUB-03", "SUB-04", "SUB-05", "SUB-06", "SUB-07",
  "OUT-01", "OUT-02", "OUT-03", "OUT-04",
  "ENT-01", "ENT-02", "ENT-03", "ENT-04", "ENT-05", "ENT-06", "ENT-07", "ENT-08", "ENT-09", "ENT-10", "ENT-11", "ENT-12",
  "SHR-01", "SHR-02", "SHR-03", "SHR-04",
  "ADM-01", "ADM-02", "ADM-03", "ADM-04", "ADM-05", "ADM-06", "ADM-07", "ADM-08", "ADM-09", "ADM-10", "ADM-11",
  "SYS-01", "SYS-02", "SYS-03",
  "MOB-01", "MOB-02", "MOB-03", "MOB-04", "MOB-05",
] as const;

export function getCanonicalSpace(code: CanonicalSpaceCode): CanonicalSpace | undefined {
  return CANONICAL_SPACES.find((space) => space.code === code);
}
