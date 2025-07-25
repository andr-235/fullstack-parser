/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './hooks/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx,mdx}',
    './providers/**/*.{js,ts,jsx,tsx,mdx}',
    './store/**/*.{js,ts,jsx,tsx,mdx}',
    './types/**/*.{js,ts,jsx,tsx,mdx}',
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    './features/**/*.{js,ts,jsx,tsx,mdx}',
    './shared/**/*.{js,ts,jsx,tsx,mdx}',
    './entities/**/*.{js,ts,jsx,tsx,mdx}',
    './widgets/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: ['class'],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'sans-serif'],
      },
      fontSize: {
        'xs-compact': ['0.7rem', { lineHeight: '1rem' }],
        'sm-compact': ['0.8rem', { lineHeight: '1.2rem' }],
        'base-compact': ['0.875rem', { lineHeight: '1.4rem' }],
        'lg-compact': ['1rem', { lineHeight: '1.5rem' }],
        'xl-compact': ['1.125rem', { lineHeight: '1.6rem' }],
        '2xl-compact': ['1.25rem', { lineHeight: '1.7rem' }],
        '3xl-compact': ['1.5rem', { lineHeight: '1.8rem' }],
        '4xl-compact': ['1.75rem', { lineHeight: '2rem' }],
        // Еще более компактные размеры
        'xs-tiny': ['0.65rem', { lineHeight: '0.9rem' }],
        'sm-tiny': ['0.75rem', { lineHeight: '1.1rem' }],
        'base-tiny': ['0.8rem', { lineHeight: '1.3rem' }],
        'lg-tiny': ['0.9rem', { lineHeight: '1.4rem' }],
        'xl-tiny': ['1rem', { lineHeight: '1.5rem' }],
        '2xl-tiny': ['1.125rem', { lineHeight: '1.6rem' }],
        '3xl-tiny': ['1.25rem', { lineHeight: '1.7rem' }],
      },
      spacing: {
        '0.5-compact': '0.125rem',
        '1-compact': '0.25rem',
        '1.5-compact': '0.375rem',
        '2-compact': '0.5rem',
        '2.5-compact': '0.625rem',
        '3-compact': '0.75rem',
        '3.5-compact': '0.875rem',
        '4-compact': '1rem',
        '5-compact': '1.25rem',
        '6-compact': '1.5rem',
        // Еще более компактные отступы
        '0.5-tiny': '0.1rem',
        '1-tiny': '0.2rem',
        '1.5-tiny': '0.3rem',
        '2-tiny': '0.4rem',
        '2.5-tiny': '0.5rem',
        '3-tiny': '0.6rem',
        '3.5-tiny': '0.7rem',
        '4-tiny': '0.8rem',
        '5-tiny': '1rem',
        '6-tiny': '1.2rem',
      },
    },
  },
  plugins: [],
}
