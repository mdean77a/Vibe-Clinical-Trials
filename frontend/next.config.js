/** @type {import('next').NextConfig} */
const nextConfig = {
  // Configure for monorepo structure
  outputFileTracingRoot: require('path').join(__dirname, '..'),
  experimental: {
    // Enable if you need server actions
    serverActions: {
      bodySizeLimit: '2mb',
    },
  },
  // Exclude test files from build
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': require('path').resolve(__dirname, 'src'),
    };
    return config;
  },
  // Use standard page extensions
  pageExtensions: ['tsx', 'ts', 'jsx', 'js'],
}

module.exports = nextConfig