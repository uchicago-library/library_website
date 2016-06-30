$(document).ready(function() {
  // a function to show the checked panels, hide all others. 
  function toggle() {
    $("[data-radio-button-controller]").each(function() {
      var panel = $(this).attr('data-radio-button-controller');
      // if the one we're looking at was just checked, show its associated panel. 
      if ($(this).is(':checked')) {
        $('[data-radio-button-content-panel="' + panel + '"]').show();
      // otherwise hide its associated panel. 
      } else {
        $('[data-radio-button-content-panel="' + panel + '"]').hide();
      }
    });
  }

  // toggle panels on page load. 
  toggle();

  // toggle panels when any element with the data-radio-button-controller attribute is changed...
  $("[data-radio-button-controller]").change(function() {
    toggle();
  }); 
});
