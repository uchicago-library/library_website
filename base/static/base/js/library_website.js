/*
 * Get libal id for the page.
 DEPRECATED: 
    function getLibCalId() {
        var fallback = '1357';
        var libcalid = $('#current-hours').data('libcalid');
        if (libcalid == '') {
            return fallback;
        } else {
            return libcalid;
        }
    }
*/
function getLibCalId() {
    var libcalid = $('#current-hours').data('libcalid');
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
function renderHours(libcalid){
    json = $.getJSON('/json-hours/?libcalid='.concat(encodeURIComponent(libcalid)), function(data) {
        var innerJson = JSON.parse(data.all_building_hours);
        var currentLlid = data.llid;
        var html ='';
        var currentHoursHtml = '';

        // Build the html
        $.each(innerJson, function(keystr, val){
            var key = JSON.parse(keystr);
            var llid = innerJson[key][0];
            var hours = innerJson[key][1];

            if (llid != currentLlid) {
                html += '<li><a href="#">' + hours + '</a></li>';
            } else {
                // Render the current building hours as selected
                var currentHoursHtml = '<span>' + hours  + '</span>';
                $('#current-hours-target').replaceWith(currentHoursHtml);
            }
        });

        // Render the hours dropdown
        $('#hours-dropdown').prepend(html); 
    });
}

$(document).ready(function(){

    /* 
     * Collection browse pages "Limit to digital materials" button. 
     */

    // hide the submit button if javascript is enabled. 
    $('#checkboxdigital').closest('form').find('input[type="submit"]').hide();
    // when the checkbox is clicked, submit the form automatically. 
    $('#checkboxdigital').change(function() {
        $(this).closest('form').submit();
    });

    /*
     * Lightbox
     */
    $(document).delegate('*[data-toggle="lightbox"]', 'click', function(event) {
        event.preventDefault();
        $(this).ekkoLightbox();
    });

    renderHours(getLibCalId());

});
