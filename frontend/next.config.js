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
  webpack: (config, { isServer }) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': require('path').resolve(__dirname, 'src'),
      // Alias canvas to empty module for browser (pdfjs-dist compatibility)
      canvas: false,
    };

    // Also add to externals to prevent bundling
    config.externals = config.externals || [];
    config.externals.push({
      canvas: 'canvas',
    });

    return config;
  },
  // Use standard page extensions
  pageExtensions: ['tsx', 'ts', 'jsx', 'js'],
}

module.exports = nextConfig