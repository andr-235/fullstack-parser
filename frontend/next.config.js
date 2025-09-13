/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    optimizePackageImports: ['lucide-react', '@radix-ui/react-icons'],
  },
  images: {
    unoptimized: true,
  },
  webpack: config => {
    config.module.rules.push({
      test: /\.svg$/,
      use: ['@svgr/webpack'],
    })
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': require('path').resolve(__dirname),
    }
    return config
  },
  output: 'standalone',
  trailingSlash: false,
  poweredByHeader: false,
  eslint: {
    ignoreDuringBuilds: true,
  },
}

module.exports = nextConfig
