/** @type {import('postcss').Config} */
module.exports = {
  plugins: {
    '@tailwindcss/postcss': { config: './tailwind.config.js' },
    autoprefixer: {},
  },
}
