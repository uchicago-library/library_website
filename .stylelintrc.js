module.exports = {
  extends: ['stylelint-config-standard-scss'],
  plugins: ['stylelint-prettier'],
  rules: {
    'prettier/prettier': true,
    indentation: null,
    'string-quotes': null,
    'no-duplicate-selectors': true,
    'color-hex-length': 'short',
    'selector-no-qualifying-type': null,
    'selector-class-pattern': null,
    'selector-id-pattern': null,
    'scss/at-import-partial-extension': null,
    'scss/dollar-variable-pattern': null,
    'scss/no-global-function-names': null,
    'scss/percent-placeholder-pattern': null,
    'declaration-block-no-redundant-longhand-properties': null,
    'no-descending-specificity': null,
    'rule-empty-line-before': null,

    // Disabled because libsass doesn't support CSS Level 4 syntax.
    // These rules enforce modern notation like rgb(0 0 0 / 33%) and (width <= 986px)
    // which libsass cannot compile. Use legacy syntax instead: rgba(0, 0, 0, 0.33)
    // and (max-width: 986px).
    'color-function-notation': null,
    'alpha-value-notation': null,
    'media-feature-range-notation': null,
  },
}
