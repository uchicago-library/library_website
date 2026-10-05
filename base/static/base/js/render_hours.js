$(document).ready(function() {
  /*
     * Get libal id for the page.
     */
  function getLibCalId() {
    var libcalid = $('#current-hours').data('libcalid');
    var fallback;
    $.ajax({
      dataType: 'json',
      url: '/json-hours/?fallback=true',
      async: false,
      success: function (data) {
        fallback = data.llid;
      }
    });
    if (libcalid == '') {
      return fallback;
    } 
    return libcalid;
  }
    
  /*
     * Ajax call to libcal. Renders hours in the header. 
     */
  function renderHours(libcalid) {
    $.getJSON('/json-hours/?libcalid='.concat(encodeURIComponent(libcalid)), function(data) {
      var innerJson = JSON.parse(data.all_building_hours);
      var currentLlid = data.llid;
      var html ='';

      // Build the html
      $.each(innerJson, function(keystr){
        var key = JSON.parse(keystr);
        var llid = innerJson[key][0];
        var hours = innerJson[key][1];
        var hlink = innerJson[key][2];
    
        if (llid != currentLlid) {
          html += '<li><a href="' + hlink + '">' + hours + '</a></li>';
        } else {
          // Render the current building hours as selected
          var currentHoursHtml = '<span><strong>Hours:</strong> ' + hours  + '</span>';
          $('#current-hours-target').replaceWith(currentHoursHtml);
        }
      });
    
      // Render the hours dropdown
      $('#hours-dropdown').prepend(html); 
    });
  }
    
  // Render hours html in the header
  renderHours(getLibCalId());
});
