// Annotation overlay for the /design/ pages: a toggle button plus markers built
// from <template class="ds-annotations-template"> blocks. See the
// Annotations page under Methodology. Styles: design_system/scss/meta/_annotations.scss.
/* global bootstrap */
(function () {
  var COLORS = {
    a11y: 'var(--ucl-violet)',
    behavior: 'var(--ucl-lake)',
    tracking: 'var(--ucl-terracotta)',
    responsive: 'var(--ucl-ivy)',
    info: 'var(--ucl-greystone)'
  };
  var ICONS = {
    a11y: 'fa-universal-access',
    behavior: 'fa-hand-pointer',
    tracking: 'fa-chart-simple',
    responsive: 'fa-mobile-screen',
    info: 'fa-circle-info'
  };

  var STORAGE_KEY = 'ds-annotations-visible';

  var toggleBtn = document.getElementById('dsNotesToggle');
  var templates = document.querySelectorAll('.ds-annotations-template');
  if (!templates.length) {
    if (toggleBtn) toggleBtn.remove();
    return;
  }

  // Restore saved preference (default: visible). localStorage throws when
  // storage is blocked, so fall back to the default.
  var saved = null;
  try { saved = localStorage.getItem(STORAGE_KEY); } catch (e) { /* storage unavailable */ }
  var visible = saved !== 'false';

  var targetMap = {};

  // Group annotations by target selector across all templates
  templates.forEach(function (tpl) {
    var items = tpl.content.children;
    for (var i = 0; i < items.length; i++) {
      var el = items[i];
      var target = el.getAttribute('data-target');
      var category = el.getAttribute('data-category');
      var title = el.getAttribute('data-title');
      var content = el.innerHTML.trim();
      if (!target || !category) continue;
      if (!targetMap[target]) targetMap[target] = [];
      targetMap[target].push({ category: category, title: title, content: content });
    }
  });

  var allPopovers = [];

  Object.keys(targetMap).forEach(function (selector) {
    var targetEl = document.querySelector(selector);
    if (!targetEl) return;

    var annotations = targetMap[selector];

    // Dashed outline — use first annotation's color
    targetEl.classList.add('ds-annotated');
    targetEl.style.setProperty('--ds-annotation-color', COLORS[annotations[0].category] || '#868e96');

    // Ensure target is positioned for the absolute marker group
    if (getComputedStyle(targetEl).position === 'static') {
      targetEl.style.position = 'relative';
    }

    // Create marker group
    var group = document.createElement('span');
    group.className = 'ds-note-group';

    annotations.forEach(function (ann) {
      var marker = document.createElement('span');
      marker.className = 'ds-note ds-note--' + ann.category;
      marker.setAttribute('data-bs-toggle', 'popover');
      marker.setAttribute('data-bs-title', ann.title);
      marker.setAttribute('data-bs-content', ann.content);
      marker.setAttribute('tabindex', '0');
      marker.setAttribute('role', 'button');
      marker.innerHTML = '<i class="fa-solid ' + ICONS[ann.category] + '" aria-hidden="true"></i>';
      group.appendChild(marker);
      allPopovers.push(marker);
    });

    targetEl.appendChild(group);
  });

  // Initialize Bootstrap popovers
  allPopovers.forEach(function (el) {
    // eslint-disable-next-line no-new -- Bootstrap keeps the instance on the element
    new bootstrap.Popover(el, { trigger: 'click', html: true, placement: 'top' });
  });

  // Show toggle and apply saved state
  if (toggleBtn) toggleBtn.removeAttribute('hidden');
  if (!visible) {
    document.body.classList.add('ds-notes-hidden');
    if (toggleBtn) toggleBtn.setAttribute('aria-pressed', 'false');
  }

  // Toggle button
  if (toggleBtn) {
    toggleBtn.addEventListener('click', function () {
      var isPressed = toggleBtn.getAttribute('aria-pressed') === 'true';
      if (isPressed) {
        allPopovers.forEach(function (el) {
          var p = bootstrap.Popover.getInstance(el);
          if (p) p.hide();
        });
      }
      document.body.classList.toggle('ds-notes-hidden', isPressed);
      toggleBtn.setAttribute('aria-pressed', String(!isPressed));
      try { localStorage.setItem(STORAGE_KEY, String(!isPressed)); } catch (e) { /* storage unavailable: the toggle still works for this page */ }
    });
  }

  // Dismiss popover on click outside
  document.addEventListener('click', function (e) {
    allPopovers.forEach(function (el) {
      if (!el.contains(e.target)) {
        var p = bootstrap.Popover.getInstance(el);
        if (p) p.hide();
      }
    });
  });
})();
