// Application configuration
export const config = {
  api: {
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    timeout: 10000,
  },
  app: {
    name: 'My App',
    description:
      'A modern web application built with Next.js and FSD architecture',
    version: '1.0.0',
  },
} as const

// Legacy export for backward compatibility
export const APP_CONFIG = config.app
