/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    // Enable if you need server actions
    serverActions: {
      bodySizeLimit: '2mb',
    },
  },
  // Handle CORS for API calls to backend
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
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