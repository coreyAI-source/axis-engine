import path from "node:path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Trace files from the monorepo root so the build doesn't read unrelated parent folders.
  outputFileTracingRoot: path.join(__dirname, "../../"),
  // The dev-only route badge sat on top of the sidebar's sign-out button.
  devIndicators: { appIsrStatus: false },
};

export default nextConfig;
