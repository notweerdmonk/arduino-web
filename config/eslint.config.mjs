import js from "@eslint/js";
import html from "eslint-plugin-html";
import eslintPluginPrettierRecommended from "eslint-plugin-prettier/recommended";

export default [
  js.configs.recommended,

  {
    files: ["**/*.js", "**/*.mjs"],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "script",
      globals: {
        htmx: "readonly",
        document: "readonly",
        window: "readonly",
        console: "readonly",
        fetch: "readonly",
        setTimeout: "readonly",
        encodeURIComponent: "readonly",
        FormData: "readonly",
        EventSource: "readonly",
      },
    },
    rules: {
      "no-var": "warn",
      "prefer-const": "warn",
      "no-unused-vars": ["warn", { args: "none" }],
    },
  },

  {
    // Tell ESLint to check HTML files for inline JS
    files: ["**/*.html"],
    plugins: { html },
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "script",
      globals: {
        htmx: "readonly",
        document: "readonly",
        window: "readonly",
        console: "readonly",
        fetch: "readonly",
        setTimeout: "readonly",
        encodeURIComponent: "readonly",
        FormData: "readonly",
        EventSource: "readonly",
      },
    },
    rules: {
      "no-unused-vars": "warn",
      "no-console": "off",
    }
  },

  {
    ignores: [
      "**/node_modules/**",
      "**/dist/**",
      "**/dist-standalone/**",
      "**/build/**",
      "**/.nox/**",
      "**/_site/**",
      "**/__pycache__/**",
      "**/.opencode/**",
      "**/*.ts",
      "**/*.tsx",
      "config/eslint.config.mjs",
      "eslint.config.mjs",
      "**/docs/reference/**",
      "**/scratch/**",
      "**/typedoc/**",
      "**/search.js",
    ],
  },
  eslintPluginPrettierRecommended,
];
