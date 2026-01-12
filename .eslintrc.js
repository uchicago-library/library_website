module.exports = {
  root: true,
  parser: '@babel/eslint-parser',
  env: {
    browser: true,
  },
  extends: ['airbnb', 'prettier'],
  plugins: ['prettier'],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    requireConfigFile: false,
    ecmaFeatures: {
      jsx: true,
    },
  },
  rules: {
    'prettier/prettier': 'error',
    'func-names': ['error', 'as-needed'],
    'no-underscore-dangle': ['error', { allow: ['_id'] }],
    'import/no-absolute-path': 'off',
    'react/jsx-filename-extension': [1, { extensions: ['.js', '.jsx'] }],
    'react/function-component-definition': 0,
    'jsx-a11y/label-has-for': 'off',
    'jsx-a11y/anchor-is-valid': [
      'error',
      {
        components: ['Link'],
        specialLink: ['to', 'hrefLeft', 'hrefRight'],
        aspects: ['noHref', 'invalidHref', 'preferButton'],
      },
    ],
  },
  globals: {
    fetch: false,
    document: false,
  },
  overrides: [
    {
      // Legacy jQuery files - relax modern JS requirements
      files: ['**/static/**/js/**/*.js'],
      excludedFiles: [
        '**/static/**/js/index.js', // ES6 React components
        '**/static/**/js/NewsFeed.js', // ES6 React component
        '**/static/**/js/CGIMailForm.js', // ES6 React component
        '**/bundles/**/*.js', // Webpack bundles
      ],
      env: {
        browser: true,
        jquery: true,
      },
      rules: {
        // Disable Prettier for legacy files (use ESLint indentation instead)
        'prettier/prettier': 'off',
        // Basic indentation enforcement (2 spaces to match ES6 code)
        indent: ['error', 2, { SwitchCase: 1 }],

        // Keep these bug-catching rules enabled:
        // - no-undef (catch undefined variables)
        // - no-unused-vars (catch dead code)

        // Relax stylistic/legacy-friendly rules:
        'no-var': 'off',
        'vars-on-top': 'off',
        'prefer-arrow-callback': 'off',
        'func-names': 'off',
        'prefer-template': 'off',
        'object-shorthand': 'off',
        'prefer-destructuring': 'off',
        'no-console': 'off',
        'no-alert': 'off',
        eqeqeq: 'off', // == vs === very common in legacy
        'dot-notation': 'off', // bracket notation is fine
        'no-param-reassign': 'off',
        'no-plusplus': 'off',
        'no-continue': 'off',
        'no-nested-ternary': 'off',
        'no-else-return': 'off',
        'no-lonely-if': 'off',
        'no-unused-expressions': 'off',
        'no-restricted-globals': 'off', // allow 'location' etc
        'no-useless-concat': 'off',
        'no-useless-escape': 'off',
        'no-array-constructor': 'off',
        'consistent-return': 'off',
        strict: 'off',
        'spaced-comment': 'off', // legacy comment formatting
      },
      globals: {
        // jQuery globals
        $: 'readonly',
        jQuery: 'readonly',
      },
    },
  ],
}
