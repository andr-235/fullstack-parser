/** @type {import('next').NextConfig} */
const nextConfig = {
  // Экспериментальные функции
  experimental: {
    // Включаем оптимизации для production
    optimizePackageImports: ['lucide-react', '@radix-ui/react-icons'],
  },

  // Настройки изображений
  images: {
    domains: [
      'vk.com',
      'sun9-1.userapi.com',
      'sun9-2.userapi.com',
      'sun9-3.userapi.com',
      'sun9-4.userapi.com',
      'sun9-5.userapi.com',
      'sun9-6.userapi.com',
      'sun9-7.userapi.com',
      'sun9-8.userapi.com',
      'sun9-9.userapi.com',
      'sun9-10.userapi.com',
      'sun9-11.userapi.com',
      'sun9-12.userapi.com',
      'sun9-13.userapi.com',
      'sun9-14.userapi.com',
      'sun9-15.userapi.com',
      'sun9-16.userapi.com',
      'sun9-17.userapi.com',
      'sun9-18.userapi.com',
      'sun9-19.userapi.com',
      'sun9-20.userapi.com',
      'sun9-21.userapi.com',
      'sun9-22.userapi.com',
      'sun9-23.userapi.com',
      'sun9-24.userapi.com',
      'sun9-25.userapi.com',
      'sun9-26.userapi.com',
      'sun9-27.userapi.com',
      'sun9-28.userapi.com',
      'sun9-29.userapi.com',
      'sun9-30.userapi.com',
      'sun9-31.userapi.com',
      'sun9-32.userapi.com',
      'sun9-33.userapi.com',
      'sun9-34.userapi.com',
      'sun9-35.userapi.com',
      'sun9-36.userapi.com',
      'sun9-37.userapi.com',
      'sun9-38.userapi.com',
      'sun9-39.userapi.com',
      'sun9-40.userapi.com',
      'sun9-41.userapi.com',
      'sun9-42.userapi.com',
      'sun9-43.userapi.com',
      'sun9-44.userapi.com',
      'sun9-45.userapi.com',
      'sun9-46.userapi.com',
      'sun9-47.userapi.com',
      'sun9-48.userapi.com',
      'sun9-49.userapi.com',
    ],
    formats: ['image/webp', 'image/avif'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },

  // Настройки webpack
  webpack: (config, { dev, isServer }) => {
    // Настройки для SVG
    config.module.rules.push({
      test: /\.svg$/,
      use: ['@svgr/webpack'],
    })

    // Оптимизации для production
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
          },
        },
      }
    }

    return config
  },

  // Настройки заголовков
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()',
          },
        ],
      },
      {
        source: '/api/(.*)',
        headers: [
          {
            key: 'Access-Control-Allow-Origin',
            value: '*',
          },
          {
            key: 'Access-Control-Allow-Methods',
            value: 'GET, POST, PUT, DELETE, OPTIONS',
          },
          {
            key: 'Access-Control-Allow-Headers',
            value: 'Content-Type, Authorization',
          },
        ],
      },
    ]
  },

  // Настройки редиректов
  async redirects() {
    return [
      {
        source: '/',
        destination: '/dashboard',
        permanent: false,
      },
    ]
  },

  // API проксирование отключено - используем Nginx в Docker
  // Все запросы к API проходят через Nginx reverse proxy
  // async rewrites() {
  //   return []
  // },

  // Настройки TypeScript
  typescript: {
    // Игнорируем ошибки TypeScript при сборке (для production)
    ignoreBuildErrors: process.env.NODE_ENV === 'production',
  },

  // Настройки ESLint
  eslint: {
    // Проверяем ESLint при сборке (только для production)
    ignoreDuringBuilds: process.env.NODE_ENV === 'production',
  },

  // Отключаем статическую генерацию для страниц с ошибками
  staticPageGenerationTimeout: 1000,

  // Отключаем статическую оптимизацию
  trailingSlash: false,

  // Настройки для Docker
  output: 'standalone',
  poweredByHeader: false,
  compress: true,
  generateEtags: false,
}

module.exports = nextConfig
