module.exports = {
  extends: ['stylelint-config-standard-scss'],
  plugins: ['stylelint-prettier'],
  rules: {
    'prettier/prettier': true,
    'no-duplicate-selectors': true,
    'color-hex-length': 'short',
    'selector-no-qualifying-type': null,
    'selector-class-pattern': null,
    'selector-id-pattern': null,
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
    'color-function-alias-notation': null,
  },
  overrides: [
    {
      // Design system sources, compiled with Dart Sass rather than libsass.
      files: ['design_system/scss/**/*.scss'],
      rules: {
        // The /design/ token docs parse these comment markers (//!, /// and
        // bare // paragraph breaks). See design_system/README.md.
        'scss/double-slash-comment-whitespace-inside': null,
        'scss/comment-no-empty': null,
        'scss/double-slash-comment-empty-line-before': null,
        'comment-empty-line-before': null,
        // Plain-CSS rule. SCSS allows @include before @import, which
        // main.scss relies on for Bootstrap's banner.
        'no-invalid-position-at-import-rule': null,
        // Font names keep their real casing; the token docs display them.
        'value-keyword-case': [
          'lower',
          { ignoreProperties: ['/font-family/'] },
        ],
      },
    },
  ],
}
