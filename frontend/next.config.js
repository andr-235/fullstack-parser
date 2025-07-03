/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  
  // Настройки для Docker development
  webpackDevMiddleware: (config) => {
    config.watchOptions = {
      poll: 1000,
      aggregateTimeout: 300,
    }
    return config
  },
  
  // Исправление chunk loading в Docker
  webpack: (config, { isServer, dev }) => {
    if (dev && !isServer) {
      config.optimization = {
        ...config.optimization,
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            default: false,
            vendors: false,
            // Группировка vendor библиотек
            vendor: {
              name: 'vendor',
              chunks: 'all',
              test: /[\\/]node_modules[\\/]/,
              priority: 20
            },
            // Отдельная группа для tanstack
            tanstack: {
              name: 'tanstack',
              chunks: 'all',
              test: /[\\/]node_modules[\\/]@tanstack[\\/]/,
              priority: 30
            }
          }
        }
      }
    }
    return config
  },
  
  images: {
    domains: ['localhost'],
  },
  
  // Настройки для development server
  experimental: {
    forceSwcTransforms: true,
  },
}

module.exports = nextConfig
