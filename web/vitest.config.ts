import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";
import { loadEnv } from "vite";

const withC08HttpProof = Boolean(loadEnv("test", ".", "SMART_AO_C08_HTTP_PROOF").SMART_AO_C08_HTTP_PROOF);

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts", ...(withC08HttpProof ? ["./src/test/c08-http-proof.setup.mjs"] : [])],
    include: ["src/**/*.test.{ts,tsx}"],
    globals: true,
    // Keep component tests reliable on shared/CPU-constrained runners.
    testTimeout: 15_000,
    hookTimeout: 15_000,
  },
});
