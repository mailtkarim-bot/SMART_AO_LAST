import { readFileSync } from "node:fs";
import { env } from "node:process";

if (!env.SMART_AO_C08_HTTP_PROOF) throw new Error("An explicit local C08 HTTP proof file is required.");
globalThis.__smartAoC08Proof = JSON.parse(readFileSync(env.SMART_AO_C08_HTTP_PROOF, "utf8"));
