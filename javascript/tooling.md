# JavaScript Tooling

## Required Tools

| Tool | Purpose | Config |
|------|---------|--------|
| **ESLint** | Linting | `.eslintrc.cjs` |
| **Prettier** | Formatting | `prettier.config.cjs` |
| **Jest** | Testing | `jest.config.cjs` |

## ESLint Config (Flat Config, ESLint 9+)

```javascript
// eslint.config.mjs
import js from '@eslint/js';
import globals from 'globals';

export default [
  js.configs.recommended,
  {
    languageOptions: {
      ecmaVersion: 2024,
      sourceType: 'module',
      globals: { ...globals.node },
    },
    rules: {
      'no-var': 'error',
      'prefer-const': 'error',
      'no-console': 'warn',
      'no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      'eqeqeq': ['error', 'always'],
      'no-eval': 'error',
      'no-implied-eval': 'error',
      'max-len': ['error', { code: 100, ignoreUrls: true }],
      'max-params': ['error', 4],
      'no-throw-literal': 'error',
    },
  },
];
```

## Prettier Config

```javascript
// prettier.config.cjs
module.exports = {
  semi: true,
  singleQuote: true,
  trailingComma: 'all',
  printWidth: 100,
  tabWidth: 2,
  arrowParens: 'always',
};
```

## package.json Scripts

```json
{
  "scripts": {
    "lint": "eslint src tests",
    "lint:fix": "eslint src tests --fix",
    "format": "prettier --write src tests",
    "format:check": "prettier --check src tests",
    "test": "jest",
    "test:coverage": "jest --coverage",
    "test:watch": "jest --watch",
    "typecheck": "tsc --noEmit"
  }
}
```
