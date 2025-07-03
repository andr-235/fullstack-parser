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
  
  // Удалена кастомная splitChunks оптимизация!
  webpack: (config, { isServer, dev }) => {
    // Не трогаем splitChunks, чтобы не ломать обработку CSS
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
