import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    // Use the TypeScript compiler API instead of spawning the CLI.
    useTypeScriptCli: false,
  },
};

export default nextConfig;
