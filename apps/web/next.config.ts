import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // The dev-only route badge sat on top of the sidebar's sign-out button.
  devIndicators: { appIsrStatus: false },
};

export default nextConfig;
