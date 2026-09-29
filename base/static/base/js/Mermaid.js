/**
 * Client init for Mermaid StreamField diagrams.
 * Expects global mermaid from base/js/vendor/mermaid.min.js (pinned via npm).
 */
(function () {
  function showFriendlyError(el, source) {
    el.classList.remove('mermaid');
    el.removeAttribute('aria-label');
    while (el.firstChild) {
      el.removeChild(el.firstChild);
    }

    var msg = document.createElement('div');
    msg.className = 'mermaid-error';
    msg.setAttribute('role', 'alert');
    msg.textContent =
      'This diagram could not be displayed due to invalid Mermaid syntax. The source is shown below.';

    var pre = document.createElement('pre');
    pre.className = 'mermaid-source-fallback';
    pre.textContent = source;

    var parent = el.parentNode;
    if (parent) {
      parent.insertBefore(msg, el);
      parent.insertBefore(pre, el);
      parent.removeChild(el);
    } else {
      el.appendChild(msg);
      el.appendChild(pre);
    }
  }

  async function renderDiagrams() {
    if (typeof mermaid === 'undefined') {
      return;
    }

    var nodes = Array.prototype.slice.call(
      document.querySelectorAll('pre.mermaid')
    );
    if (!nodes.length) {
      return;
    }

    mermaid.initialize({
      startOnLoad: false,
      securityLevel: 'strict',
      htmlLabels: false,
      theme: 'default',
    });

    for (var i = 0; i < nodes.length; i += 1) {
      var el = nodes[i];
      var source = (el.textContent || '').trim();
      if (!source) {
        continue;
      }

      try {
        await mermaid.parse(source);
        await mermaid.run({ nodes: [el] });
      } catch (err) {
        showFriendlyError(el, source);
      }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderDiagrams);
  } else {
    renderDiagrams();
  }
})();
