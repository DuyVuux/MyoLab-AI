/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // ASSUMPTION: No external image domains needed for prototype (all synthetic/local)
  images: {
    unoptimized: true,
  },
  // Suppress hydration warnings from browser extensions
  experimental: {
    // Enable typed routes in future
  },
};

module.exports = nextConfig;
