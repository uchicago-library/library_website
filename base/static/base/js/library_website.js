/*
 * Decode url parameters.
 */
function urldecode(str) {
   return decodeURIComponent((str+'').replace(/\+/g, '%20'));
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
                    eventsHtml += '<p><a class="event-header" href="' + v['link'] + '">' + v['title'] + '</a><br/><span class="event-date">' + v['start_date'] + '</span> | ' + v['start_time'] + ' - ' + v['end_time'] + '</p>'
                } else {
                    // multi-day events. 
                    eventsHtml += '<p><a class="event-header" href="' + v['link'] + '">' + v['title'] + '</a><br/><span class="event-date">' + v['start_date'] + '</span> | ' + v['start_time'] + ' -<br/>' + '<span class="event-date">' + v['end_date'] + '</span> | ' + v['end_time'] + '</p>'
                }
            });
            $('#events-target').replaceWith(eventsHtml);
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

    /* Prepopulate the Checkout UChicago Feedback form*/
    $.urlParam = function(name) {
        var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
        if (results==null) {
            return null;
        }
        else {
            return results[1] || 0;
        }
    }
    var name = urldecode($.urlParam('name'));
    var email = urldecode($.urlParam('email'));

    if (name != 'null' && email != 'null') {
        $("#knowledgetracker input:text[name='name']").each(function(){
            $(this).val(name);
        });
        $("#knowledgetracker input:text[name='email'], #knowledgetracker input:text[name='email confirmed']").each(function(){
            $(this).val(email);
        });
    }
});
