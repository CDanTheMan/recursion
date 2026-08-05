/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // No ESLint dependency is installed; skip the lint pass so `next build` is
  // self-contained. Type checking still runs.
  eslint: {
    ignoreDuringBuilds: true
  }
};

export default nextConfig;
