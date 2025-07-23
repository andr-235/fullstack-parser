/** @type {import('next').NextConfig} */
const nextConfig = {
  // Экспериментальные функции
  experimental: {
    // Включаем новые функции React 19
    reactCompiler: true,
    // Улучшенная оптимизация изображений
    optimizePackageImports: ['lucide-react', '@radix-ui/react-icons'],
    // Улучшенная обработка CSS
    turbo: {
      rules: {
        '*.svg': {
          loaders: ['@svgr/webpack'],
          as: '*.js',
        },
      },
    },
  },

  // Оптимизация изображений
  images: {
    formats: ['image/webp', 'image/avif'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    minimumCacheTTL: 60,
    dangerouslyAllowSVG: true,
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
  },

  // Оптимизация сборки
  swcMinify: true,
  compress: true,
  poweredByHeader: false,

  // Заголовки безопасности
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
            key: 'Cache-Control',
            value: 'no-store, max-age=0',
          },
        ],
      },
    ]
  },

  // Перенаправления
  async redirects() {
    return [
      {
        source: '/',
        destination: '/dashboard',
        permanent: false,
      },
    ]
  },

  // Переменные окружения
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },

  // Webpack конфигурация
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Оптимизация для production
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
          },
          common: {
            name: 'common',
            minChunks: 2,
            chunks: 'all',
            enforce: true,
          },
        },
      }
    }

    // Обработка SVG
    config.module.rules.push({
      test: /\.svg$/,
      use: ['@svgr/webpack'],
    })

    return config
  },

  // Настройки для разработки
  ...(process.env.NODE_ENV === 'development' && {
    // Включаем подробные логи в разработке
    logging: {
      fetches: {
        fullUrl: true,
      },
    },
  }),

  // Настройки для production
  ...(process.env.NODE_ENV === 'production' && {
    // Оптимизация для production
    output: 'standalone',
    trailingSlash: false,
  }),
}

module.exports = nextConfig
