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
     * Search Widget, Catalog search, Begins-With searches.
     */

    // If this script is running (i.e., JavaScript is enabled) add dropdown elements for browses. 
    $('#search_widget_catalog_search').each(function() {
        var select = $(this).find('select[name="type"]');
        select.append('<option value="browse_title">Title begins with</option><option value="browse_journal">Journal begins with</option><option value="browse_lcc">Call Number begins with</option>');
    });

    // Modify browses before the form is submitted.
    $('#search_widget_catalog_search').submit(function() {
        // If the field pulldown's value begins with "browse_"...
        var type = $(this).find('select[name="type"]').val();
        if (type.substring(0, 7) == 'browse_') {
            // Make a new hidden element called "source" for everything after "browse_". 
            $('#search_widget_catalog_search').append('<input name="source" type="hidden" value="' + type.substring(7) + '"/>');
            // Remove the original "type" element.
            $(this).find('select[name="type"]').remove();
            // Change the name of the text input from "lookfor" to "from". 
            $(this).find('input[name="lookfor"]').attr('name', 'from');
            // Change the action of the form so it points to the browse result pages. 
            $(this).attr('action', 'https://catalog.lib.uchicago.edu/vufind/Alphabrowse/Home');
        }
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
