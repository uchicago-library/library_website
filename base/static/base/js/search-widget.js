// The main search box (base/includes/bs5/search_widget.html). The tabs are
// Bootstrap's; this does what they don't, replacing the old widget's
// transformer-tabs.js and radiobuttoncontroller.js:
// - keeps the address and the open tab in step: opens the tab named in the
//   address, such as /#tab-3 from the header's "Website Search" link, and
//   writes the open tab to the address without adding to the history, so a
//   reload or that link always lands on the right tab;
// - copies a query typed in one form to the others, so it survives a switch
//   of tab;
// - on the Articles tab, shows the form for the checked radio button.
document.querySelectorAll('#search-widget').forEach((widget) => {
  const openTabInAddress = () => {
    const { hash } = window.location;
    if (!/^#tab-\d+$/.test(hash)) return;
    const trigger = widget.querySelector(`[data-bs-target="${hash}"]`);
    if (trigger) window.bootstrap.Tab.getOrCreateInstance(trigger).show();
  };
  openTabInAddress();
  window.addEventListener('hashchange', openTabInAddress);
  widget.addEventListener('shown.bs.tab', (event) => {
    window.history.replaceState(null, '', event.target.dataset.bsTarget);
  });

  const queries = widget.querySelectorAll('[data-search-widget-query]');
  queries.forEach((input) => {
    input.addEventListener('change', () => {
      queries.forEach((other) => {
        // eslint-disable-next-line no-param-reassign
        other.value = input.value;
      });
    });
  });

  const radios = widget.querySelectorAll('[data-radio-button-controller]');
  const showChecked = () => {
    radios.forEach((radio) => {
      const name = radio.dataset.radioButtonController;
      widget
        .querySelectorAll(`[data-radio-button-content-panel="${name}"]`)
        .forEach((panel) => {
          // eslint-disable-next-line no-param-reassign
          panel.hidden = !radio.checked;
        });
    });
  };
  radios.forEach((radio) => radio.addEventListener('change', showChecked));
  showChecked();
});
