/*
 * Get libal id for the page.
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

/*
 * Ajax call to workshops and events feed.
 */
function renderEvents() {
    var feed = $('#events').data('events'); // Already encoded
    var eventsHtml = '';
    if (feed) {
        json = $.getJSON('/json-events/?feed='.concat(feed), function(data) {
            var innerJson = data['events'];
            $.each(innerJson, function(i, v){
                if (v['start_date'] == v['end_date']) {
                    // single-day events.
                    eventsHtml += '<p><a id="event-header" href="' + v['link'] + '">' + v['title'] + '</a><br/><span class="event-date">' + v['start_date'] + '</span> | ' + v['start_time'] + ' - ' + v['end_time'] + '</p>'
                } else {
                    // multi-day events. 
                    eventsHtml += '<p><a id="event-header" href="' + v['link'] + '">' + v['title'] + '</a><br/><span class="event-date">' + v['start_date'] + '</span> | ' + v['start_time'] + ' -<br/>' + '<span class="event-date">' + v['end_date'] + '</span> | ' + v['end_time'] + '</p>'
                }
            });
            $('#events-target').replaceWith(eventsHtml);
        });
    }
}

/*
 * Ajax call to wordpress for news.
 */
function renderNews() {
    var feed = $('#news-target').data('news-feed'); // Already encoded
    var newsHtml = '';
    if (feed) {
        json = $.getJSON('/json-news/?feed='.concat(feed), function(data) {
            var innerJson = data['news'];
            var has_stories = innerJson.length > 0;
            if (has_stories) {
                $('#news-header').removeClass('hidden');
            }
            $.each(innerJson, function(key, val){
                var title = innerJson[key][0];
                var tag = innerJson[key][2];
                var desc = innerJson[key][3];
                var link = innerJson[key][1];
                var css = innerJson[key][4];
                var img = innerJson[key][5];
                newsHtml += '<div class="newsblock col-xs-12 col-sm-6 col-md-3">'
                newsHtml += '<figure class="embed"><div class="figure-wrap">'
                newsHtml += '<a href="' + link + '"><img class="img-responsive" src="' + img + '"></a></div>'
                newsHtml += '<figcaption class="' + css + '">' + tag + '</figcaption></figure>'
                newsHtml += '<a href="' + link + '"><h3>' + title + '</h3></a>'
                newsHtml += '<p>' + desc + '<br><a href="' + link + '">Read more...</a></p>'
                newsHtml += '</div>'
            });
            $('#news-target').replaceWith(newsHtml);
        });
    }
}

/*
 * Ajax call for the Ask a Librarian status icon in the banner.
 */
function renderBannerChatStatus(){
    var askpage = $('#chat-status').data('default-ask-name');
    if (askpage) {
        json = $.getJSON('/chat-status/?name='.concat(askpage), function(data) {
            $('#chat-status').addClass(data.chat_css);
        });
    }
}

/*
 * Ajax calls for the chat statuses listed in the table on Ask
 * a Librarian pages.
 */
function renderAskPageChatStatuses(){
    $('.ask .btn-ask').each(function() {
        var askpage = $(this).data('btn-chat-status');
        var master = $(this);
        if (askpage) {  
            json = $.getJSON('/chat-status/?name='.concat(askpage), function(data) {
                console.log(data.chat_css);
                master.addClass(data.chat_css);
            });
        }
    });
}



/* 
 * validateFormBeforeSubmit
 */

(function($) {
    $.fn.extend({
        validateConfirmField: function() {
            var form = this.parents('form').eq(0);
            var elementName = this.attr('name');
            var elementData = form.serializeArray();
            var e = 0;
            while (e < elementData.length) {
                if (elementData[e].name == elementName)
                    break;
                e++;
            }
            var previousElementName = elementData[e-1].name;
            var previousElement = form.find('*[name=' + previousElementName + ']');
            if (previousElement.val() == this.val())
                return true;
            else
                return false;
        }
    });
    $.fn.extend({
        validateEmailField: function() {
            var re = /^.+@.+\..+$/;
            return re.test(this.val());
        }
    });
    $.fn.extend({
        validateRequiredField: function() {
            if (this.attr('type') == 'radio') {
                var name = this.attr('name');
                if ($('input:radio[name=' + name + ']:checked').size() > 0) 
                    return true;
                else
                    return false;
            } else {
                if (this.val() != '')
                    return true;
                else
                    return false;
            }
        }
    });
    $.fn.extend({
        validateFormBeforeSubmit: function() {
            this.submit(function(e) {
                var errors = new Array();
    
                $(this).find('.validateemail').each(function() {
                    if (!$(this).validateEmailField())
                        errors.push($(this).attr('name') + ' is an invalid email address.');
                });

                $(this).find('.validaterequired, select[name="affiliation"], select[name="proxy_length"], select[name="heard_about"], select[name="researcher_type"], select[name="category"]').each(function(element) {
                    if (!$(this).validateRequiredField())
                        errors.push($(this).attr('name') + ' is required.');
                });

                $(this).find('.validateconfirm').each(function() {
                    if (!$(this).validateConfirmField())
                        errors.push($(this).attr('name') + ' doesn\'t match.');
                });

                if (!$(this).find('.validateatleastone').first().validateRequiredField()) {
                    errors.push($(this).find('.validateatleastone').first().attr('name') + ' is required.');
                }
        
                if (errors.length > 0) {
                    e.preventDefault();
                    alert(errors.join('\n'));
                    return false;
                }
            });
        }
    });
})(jQuery);    

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

    // Render news html
    renderNews();

    // Render hours html in the header
    renderHours(getLibCalId());

    // Render events widget html in the right sidebar
    renderEvents();

    // Apply chat status
    renderBannerChatStatus();

    // Apply chat statuses to table on Ask pages
    renderAskPageChatStatuses();

    /*
     * Lightbox
     */
    $(document).delegate('*[data-toggle="lightbox"]', 'click', function(event) {
        event.preventDefault();
        $(this).ekkoLightbox();
    });

    // Fix # link to website search in searchbox on non-searchbox pages
    $("#web-search").click(function() {
        var wslink = $(this).find('a').attr('href');
        $(location).attr('href', wslink)
    });

    $('form#knowledgetracker').validateFormBeforeSubmit();

    /*
     * Appeal a Fine or Claim a Return Form
     * /borrow/borrowing/appeal.html
     */

    $('#appeal_a_fine_or_claim_a_return_form').validateFormBeforeSubmit();

    /* Before submitting the form, concatenate call no, copy no, and title and place that
       string in the question field. */
    $('#appeal_a_fine_or_claim_a_return_form').submit(function(e) {
        var q = 'FINE APPEAL/CLAIM: ';
        q += $("input[name='04_title']").val() + ', ';
        q += $("input[name='02_call_no']").val() + ', ';
        q += $("input[name='03_copy_no']").val();

        $("input[name='question']").val(q);
    });
});
