/* global EventsFeed */

/*
 * Decode url parameters.
 */
function urldecode(str) {
  return decodeURIComponent((str + '').replace(/\+/g, '%20'));
}

/*
 * Workshops and events widget. Fetches the page's LiveWhale JSON feed
 * and lists its events, parsed by EventsFeed (events_feed.js).
 */
var EVENTS_FEED_TIMEOUT_MS = 5000;

function eventDateLine(parent, date, time, suffix) {
  var dateSpan = document.createElement('span');
  dateSpan.className = 'event-date';
  dateSpan.textContent = date;
  parent.appendChild(dateSpan);
  if (time) {
    parent.appendChild(document.createTextNode(' | ' + time + suffix));
  }
}

function eventParagraph(event) {
  var p = document.createElement('p');
  var a = document.createElement('a');
  a.className = 'event-header';
  if (EventsFeed.isSafeLink(event.link)) {
    a.setAttribute('href', event.link);
  }
  a.textContent = event.title;
  p.appendChild(a);
  p.appendChild(document.createElement('br'));

  if (event.multiDay) {
    eventDateLine(p, event.startDate, event.startTime, ' -');
    p.appendChild(document.createElement('br'));
    eventDateLine(p, event.endDate, event.endTime, '');
  } else {
    eventDateLine(
      p,
      event.startDate,
      event.startTime,
      event.endTime ? ' - ' + event.endTime : ''
    );
  }
  return p;
}

function renderEvents() {
  var container = document.getElementById('events');
  var target = document.getElementById('events-target');
  var feed = container ? container.getAttribute('data-events-feed') : '';
  if (!feed || !target) {
    return;
  }

  EventsFeed.loadEvents(fetch, feed, new Date(), EVENTS_FEED_TIMEOUT_MS)
    .then(function (events) {
      var fragment = document.createDocumentFragment();
      if (events.length) {
        events.forEach(function (event) {
          fragment.appendChild(eventParagraph(event));
        });
      } else {
        var empty = document.createElement('p');
        empty.textContent = 'There are no upcoming events.';
        fragment.appendChild(empty);
      }
      target.replaceWith(fragment);
    });
}

/*
 * Ajax call for the Ask a Librarian status icon in the banner.
 */
function renderBannerChatStatus() {
  var askpage = $('#chat-status').data('default-ask-name');
  if (askpage) {
    $.getJSON('/chat-status/?name='.concat(askpage), function (data) {
      $('#chat-status').addClass(data.chat_css);
    });
  }
}

/*
 * Ajax calls for the chat statuses listed in the table on Ask
 * a Librarian pages.
 */
function renderAskPageChatStatuses() {
  $('.ask .btn-ask').each(function () {
    var askpage = $(this).data('btn-chat-status');
    var master = $(this);
    if (askpage) {
      $.getJSON('/chat-status/?name='.concat(askpage), function (data) {
        console.log(data.chat_css);
        master.addClass(data.chat_css);
      });
    }
  });
}



/* 
 * validateFormBeforeSubmit
 */

(function ($) {
  $.fn.extend({
    validateConfirmField: function () {
      var form = this.parents('form').eq(0);
      var elementName = this.attr('name');
      var elementData = form.serializeArray();
      var e = 0;
      while (e < elementData.length) {
        if (elementData[e].name == elementName)
          break;
        e++;
      }
      var previousElementName = elementData[e - 1].name;
      var previousElement = form.find('*[name=' + previousElementName + ']');
      if (previousElement.val() == this.val())
        return true;
      else
        return false;
    }
  });
  $.fn.extend({
    validateEmailField: function () {
      var re = /^.+@.+\..+$/;
      return re.test(this.val());
    }
  });
  $.fn.extend({
    validateRequiredField: function () {
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
    validateFormBeforeSubmit: function () {
      this.submit(function (e) {
        var errors = new Array();

        $(this).find('.validateemail').each(function () {
          if (!$(this).validateEmailField())
            errors.push($(this).attr('name') + ' is an invalid email address.');
        });

        $(this).find('.validaterequired, select[name="affiliation"], select[name="proxy_length"], select[name="heard_about"], select[name="researcher_type"], select[name="category"]').each(function () {
          if (!$(this).validateRequiredField())
            errors.push($(this).attr('name') + ' is required.');
        });

        $(this).find('.validateconfirm').each(function () {
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

$(document).ready(function () {

  /* 
     * Collection browse pages "Limit to digital materials" button. 
     */

  // hide the submit button if javascript is enabled. 
  $('#checkboxdigital').closest('form').find('input[type="submit"]').hide();
  // when the checkbox is clicked, submit the form automatically. 
  $('#checkboxdigital').change(function () {
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
  $(document).delegate('*[data-toggle="lightbox"]', 'click', function (event) {
    event.preventDefault();
    $(this).ekkoLightbox({
      onShown: function () {
        console.log('onShown fired');
        // Focus the close button for accessibility
        var closeButton = this.modal.find('.close');
        if (closeButton.length) {
          closeButton.focus();
        }
      }
    });
  });

  // Fix # link to website search in searchbox on non-searchbox pages
  $("#web-search").click(function () {
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
  $('#appeal_a_fine_or_claim_a_return_form').submit(function () {
    var q = 'FINE APPEAL/CLAIM: ';
    q += $("input[name='04_title']").val() + ', ';
    q += $("input[name='02_call_no']").val() + ', ';
    q += $("input[name='03_copy_no']").val();

    $("input[name='question']").val(q);
  });

  /* Prepopulate the Checkout UChicago Feedback form*/
  $.urlParam = function (name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results == null) {
      return null;
    }
    else {
      return results[1] || 0;
    }
  }
  var name = urldecode($.urlParam('name'));
  var email = urldecode($.urlParam('email'));

  if (name != 'null' && email != 'null') {
    $("#knowledgetracker input:text[name='name']").each(function () {
      $(this).val(name);
    });
    $("#knowledgetracker input:text[name='email'], #knowledgetracker input:text[name='email confirmed']").each(function () {
      $(this).val(email);
    });
  }
});
