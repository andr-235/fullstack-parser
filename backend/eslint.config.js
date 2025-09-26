const js = require("@eslint/js");
const globals = require("globals");
const { defineConfig } = require("eslint/config");

module.exports = defineConfig([
  { files: ["**/*.{js,mjs,cjs}"], plugins: { js }, extends: ["js/recommended"], languageOptions: { globals: { ...globals.node, ...globals.browser } } },
  { files: ["**/*.js"], languageOptions: { sourceType: "commonjs" } },
]);
