/** @type {import('next').NextConfig} */
const nextConfig = {
  // Экспериментальные функции
  experimental: {
    // Оптимизация бандла
    optimizePackageImports: [
      '@radix-ui/react-dialog',
      '@radix-ui/react-select',
      '@radix-ui/react-tabs',
      '@radix-ui/react-checkbox',
      'lucide-react',
      'date-fns',
    ],
    // Улучшенная производительность
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
    domains: ['vk.com', 'sun9-*.userapi.com'],
    formats: ['image/webp', 'image/avif'],
  },

  // Webpack конфигурация
  webpack: (config, { dev, isServer }) => {
    // Оптимизация для продакшена
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          // Отдельный чанк для React
          react: {
            test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
            name: 'react',
            chunks: 'all',
            priority: 40,
          },
          // Отдельный чанк для UI библиотек
          ui: {
            test: /[\\/]node_modules[\\/](@radix-ui|lucide-react)[\\/]/,
            name: 'ui',
            chunks: 'all',
            priority: 30,
          },
          // Отдельный чанк для утилит
          utils: {
            test: /[\\/]node_modules[\\/](date-fns|clsx|tailwind-merge)[\\/]/,
            name: 'utils',
            chunks: 'all',
            priority: 20,
          },
          // Отдельный чанк для остальных зависимостей
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendor',
            chunks: 'all',
            priority: 10,
          },
        },
      }
    }

    return config
  },

  // Компрессия
  compress: true,

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
}

module.exports = nextConfig
