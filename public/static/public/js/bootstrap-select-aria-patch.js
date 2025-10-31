/**
 * Bootstrap Select ARIA Accessibility Patch
 *
 * Adds missing ARIA attributes to Bootstrap Select v1.10.0 to improve accessibility
 * without requiring an upgrade to v1.14.x which breaks custom styling.
 *
 * Fixes:
 * - #891: Button role
 * - #895: aria-controls on button
 * - #896: aria-labelledby on dropdown menu
 * - #897: role="option" on menu items
 * - #898: aria-selected on selected items
 */

(function($) {
  'use strict';

  function patchBootstrapSelectAria() {
    $('.bootstrap-select').each(function() {
      var $selectContainer = $(this);
      var $button = $selectContainer.find('.dropdown-toggle');
      var $dropdownMenu = $selectContainer.find('.dropdown-menu');
      var $menuItems = $dropdownMenu.find('li a');

      // Get or create unique IDs
      var buttonId = $button.attr('id') || 'bs-select-' + Math.floor(Math.random() * 10000);
      var menuId = $dropdownMenu.attr('id') || buttonId + '-menu';

      if (!$button.attr('id')) {
        $button.attr('id', buttonId);
      }
      if (!$dropdownMenu.attr('id')) {
        $dropdownMenu.attr('id', menuId);
      }

      // #895: Add aria-controls to button
      $button.attr('aria-controls', menuId);

      // #896: Add aria-labelledby to dropdown menu
      $dropdownMenu.attr('aria-labelledby', buttonId);

      // #897 & #898: Add role="option" and aria-selected to menu items
      $menuItems.each(function() {
        var $item = $(this);
        var $li = $item.parent();

        // Add role="option" to the anchor
        $item.attr('role', 'option');

        // Add aria-selected based on whether parent li has 'selected' class
        if ($li.hasClass('selected')) {
          $item.attr('aria-selected', 'true');
        } else {
          $item.attr('aria-selected', 'false');
        }
      });
    });
  }

  // Run on DOM ready
  $(document).ready(function() {
    // Initial patch after Bootstrap Select initializes
    setTimeout(patchBootstrapSelectAria, 100);
  });

  // Also patch when dropdown is shown (in case Bootstrap Select rebuilds the menu)
  $(document).on('shown.bs.dropdown', '.bootstrap-select', function() {
    patchBootstrapSelectAria();
  });

  // Patch on change events to update aria-selected
  $(document).on('changed.bs.select', '.selectpicker', function() {
    patchBootstrapSelectAria();
  });

})(jQuery);
