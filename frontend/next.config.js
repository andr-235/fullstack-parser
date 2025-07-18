/** @type {import('next').NextConfig} */
const isCI = !!process.env.CI || !!process.env.DOCKER

const nextConfig = {
  // В CI / Docker включаем сборку standalone, локально — нет (избегаем ошибок symlink на Windows)
  ...(isCI ? { output: 'standalone' } : {}),

  // Настройки only for dev — переносим в функцию webpack
  webpack: (config, { dev }) => {
    if (dev) {
      config.watchOptions = {
        poll: 1000,
        aggregateTimeout: 300,
      }
    }
    return config
  },

  images: {
    domains: ['localhost', 'parser.mysite.ru'],
  },

  experimental: {
    forceSwcTransforms: true,
  },
}

module.exports = nextConfig
