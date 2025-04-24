/**
* Script to track link clicks and send events to GA4 using event delegation.
*
* This script handles:
* - Event delegation for efficient event handling.
* - Debouncing to prevent excessive event firing.
* - Documentation for clarity and maintainability.
* - Consistent naming conventions.
* - Edge case handling for robustness.
* - Accessibility considerations to avoid conflicts with screen readers.
* - Browser compatibility for wide support.
*/

(function () {
    // Debounce function to limit the rate at which a function can fire.
    function debounce(func, wait) {
        let timeout;
        return function (...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Function to determine event parameters based on link context.
    function getEventParameters(link) {
        const params = {
            event_category: '',
            event_subcategory: '',
            event_label: link.textContent.trim() || link.getAttribute('aria-label') || 'Unknown',
            click_position: link.getAttribute('data-click-position') ? parseInt(link.getAttribute('data-click-position'), 10) : null,
        };

        // Determine category and subcategory based on link context.
        if (link.closest('nav')) {
            params.event_category = 'navigation';
            params.event_subcategory = link.getAttribute('data-ga-subcategory') || 'nav-link';
        } else if (link.closest('.sidebar')) {
            params.event_category = 'sidebar';
            params.event_subcategory = link.getAttribute('data-ga-subcategory') || 'sidebar-link';
        } else if (link.closest('.widget')) {
            params.event_category = 'widget';
            params.event_subcategory = `widget-${link.getAttribute('data-widget-name') || 'unknown'}`;
        } else if (link.closest('main')) {
            params.event_category = 'content';
            params.event_subcategory = link.getAttribute('data-ga-subcategory') || 'content-link';
        } else {
            params.event_category = 'other';
            params.event_subcategory = link.getAttribute('data-ga-subcategory') || 'unknown-link';
        }

        return params;
    }

    // Function to establish the event name
    function getEventName(target) {
        if (!target) return false;

        // Check if event target or direct parent is defined as a tab
        if (target.matches('[role="tab"], [data-role="tab"]') || 
            target.closest('[role="tab"], [data-role="tab"]')) {
            return 'tab';
        }
        // Check if target or direct parent is defined as a toggler
        else if (target.matches('[data-bs-toggle="dropdown"], [data-toggle="dropdown"]') || 
                 target.closest('[data-bs-toggle="dropdown"], [data-toggle="dropdown"]')) {
            return 'dropdown';
        }
        // Check if target is an input of type checkbox
        else if (target.matches('input[type="checkbox"]') ||
                 target.matches('input[type="radio"]') ) {
            return 'checkbox';
        }
        // Check if element is an <a>
        else if (target.matches('a')) {
            return 'click';
        }
        // return false and do not trigger a GA4 event
        else {
            return false;
        }
    }

    // Function to handle link clicks and send events to GA4.
    function handleLinkClick(event) {
        const target = event.target.closest('a');
        const eventName = getEventName(target);
        if (target) {
            const eventParams = getEventParameters(target);
            gtag('event', eventName, eventParams);
        }
    }

    // Attach a single event listener to the document body using event delegation.
    document.body.addEventListener('click', debounce(handleLinkClick, 200));

    // Ensure the script does not interfere with screen readers.
    document.body.setAttribute('aria-live', 'polite');
})();


(function ($) {
    $.fn.track = function (options) {
        // Set defaults
        var defaults = {
            outbound: true,
            debug: false
        };
        var settings = $.extend(defaults, options);

        $.expr[':'].external = function (obj) {
            return !obj.href.match(/^mailto:/) && !obj.href.match(/^tel:/) && !obj.href.match(/^#/) && (obj.hostname.replace(/^www\./i, '') != document.location.hostname.replace(/^www\./i, ''));
        };

        pushEvent = function (params) {
            var gauEventInfo = {
                'hitType': 'event',
                'eventCategory': params['category'],
                'eventAction': params['action']
            };
            if (params['label']) {
                gauEventInfo['eventLabel'] = params['label'];
            }
            if (params['value']) {
                gauEventInfo['eventValue'] = params['value'];
            }
            if (params['nonInteraction']) {
                gauEventInfo['nonInteraction'] = Number(params['nonInteraction']);
            }

            try {
                ga('send', gauEventInfo);
                if (settings.debug) {
                    console.log(gauEventInfo);
                }
            } catch (e) {
                if (settings.debug) {
                    console.log("Google Analytics must be installed and initiated for Track Everything to work");
                }
            }
        }

        // $('body').track() means that this loop will be executed once. 
        return this.each(function () {
            $('*[data-ga-category][data-ga-action][data-ga-label]').each(function () {
                // Skip anything that has been tracked already.
                if ($(this).is('[data-ga-tracked]')) {
                    return;
                }
                // <a> elements. 
                if ($(this).is('a')) {
                    $(this).attr("data-ga-tracked", "on");
                    $(this).on("click.track-everything keypress.track-everything", function (e) {
                        pushEvent({
                            'category': $(this).attr('data-ga-category'),
                            'action': $(this).attr('data-ga-action'),
                            'label': $(this).attr('data-ga-label')
                        });
                    });
                    if (settings.debug) {
                        console.log('Added tracking for:');
                        console.log($(this));
                    }
                }
                // <form> elements.
                if ($(this).is("form")) {
                    $(this).on("submit.track-everything", function (e) {
                        pushEvent({
                            'category': $(this).attr('data-ga-category'),
                            'action': $(this).attr('data-ga-action'),
                            'label': $(this).attr('data-ga-label')
                        });
                    });
                    if (settings.debug) {
                        console.log('Added tracking for:');
                        console.log($(this));
                    }
                }
                // <input type="checkbox">, <input type="radio"> elements.
                if ($(this).is("input[type='checkbox'], input[type='radio']")) {
                    $(this).on("change.track-everything", function (e) {
                        pushEvent({
                            'category': $(this).attr('data-ga-category'),
                            'action': $(this).attr('data-ga-action'),
                            'label': $(this).attr('data-ga-label')
                        });
                    });
                }
            });

            // Outbound links.
            if (settings.outbound) {
                $(this).find("a:external").each(function () {
                    // Skip anything that has been tracked already.
                    if ($(this).is('[data-ga-tracked]')) {
                        return;
                    }
                    $(this).attr("data-ga-tracked", "on");
                    $(this).on("click.track-everything keypress.track-everything", function (e) {
                        pushEvent({
                            'category': $(this).attr('data-ga-category'),
                            'action': $(this).attr('data-ga-action'),
                            'label': $(this).attr('data-ga-label')
                        });
                    });
                    if (settings.debug) {
                        console.log('Added tracking for:');
                        console.log($(this));
                    }
                });
            }

            /* For debugging, check to see if anything with a data-ga-category, data-ga-action,
             * or data-ga-label wasn't tracked. 
             */
            if (settings.debug) {
                $('body').find('[data-ga-category]:not([data-ga-tracked])').each(function () {
                    console.log('Element has a data-ga-category attribute, but was not tracked.');
                    console.log($(this));
                });
                $('body').find('[data-ga-action]:not([data-ga-tracked])').each(function () {
                    console.log('Element has a data-ga-action attribute, but was not tracked.');
                    console.log($(this));
                });
                $('body').find('[data-ga-label]:not([data-ga-tracked])').each(function () {
                    console.log('Element has a data-ga-label attribute, but was not tracked.');
                    console.log($(this));
                });
            }
        });
    };

    $(document).ready(function () {
        // Explore Research Guides
        // View all link. 
        $('#widget-explore-research-guides-view-all').on('click.track-everything keypress.track-everything', function (e) {
            pushEvent({
                'category': 'Guides and Course Support',
                'action': 'click',
                'label': 'View all'
            });
        });
        $('#widget-explore-research-guides-view-all').attr("data-ga-tracked", "on");

        // All other links .
        $('#widget-explore-research-guides a').not('#widget-explore-research-guides-view-all').each(function () {
            $(this).on('click.track-everything keypress.track-everything', function (e) {
                pushEvent({
                    'category': 'Guides and Course Support',
                    'action': 'click',
                    'label': $(this).text()
                });
            });
            $(this).attr("data-ga-tracked", "on");
        });

        // Featured Library Expert
        // View all link. 
        $('#widget-featured-library-expert-view-all').on('click.track-everything keypress.track-everything', function (e) {
            pushEvent({
                'category': 'Featured Library Expert',
                'action': 'click',
                'label': 'View all'
            });
        });
        $('#widget-featured-library-expert-view-all').attr("data-ga-tracked", "on");

        // All other links .
        $('#widget-featured-library-expert a').not('#widget-featured-library-expert-view-all').each(function () {
            $(this).on('click.track-everything keypress.track-everything', function (e) {
                pushEvent({
                    'category': 'Featured Library Expert',
                    'action': 'click',
                    'label': $(this).text()
                });
            });
            $(this).attr("data-ga-tracked", "on");
        });

        // Quick Links
        $('#widget-quicklinks a').each(function () {
            $(this).on('click.track-everything keypress.track-everything', function (e) {
                pushEvent({
                    'category': 'Quicklinks',
                    'action': 'click',
                    'label': $(this).text()
                });
            });
            $(this).attr("data-ga-tracked", "on");
        });

        // Spaces
        $('#widget-spaces a').each(function () {
            $(this).on('click.track-everything keypress.track-everything', function (e) {
                var title = $(this).parents('p').text().split('    ').pop();
                pushEvent({
                    'category': 'Spaces',
                    'action': 'click',
                    'label': title
                });
            });
            $(this).attr("data-ga-tracked", "on");
        });

        // Workshops and Events
        $('#widget-workshops-and-events a').each(function () {
            $(this).on('click.track-everything keypress.track-everything', function (e) {
                pushEvent({
                    'category': 'Workshops and Events',
                    'action': 'click',
                    'label': $(this).text()
                });
            });
            $(this).attr("data-ga-tracked", "on");
        });

        // Social Media
        $('#widget-social-media a').each(function () {
            $(this).on('click.track-everything keypress.track-everything', function (e) {
                pushEvent({
                    'category': 'Social Media',
                    'action': 'click',
                    'label': $(this).text()
                });
            });
            $(this).attr("data-ga-tracked", "on");
        });
    });

    // News
    var interval = setInterval(function () {
        if ($('.newsblock').length == 0) {
            return;
        } else {
            clearInterval(interval);
            // View all link. 
            $('#widget-news-view-all').on('click.track-everything keypress.track-everything', function (e) {
                pushEvent({
                    'category': 'News',
                    'action': 'click',
                    'label': 'View all'
                });
            });
            $('#widget-news-view-all').attr("data-ga-tracked", "on");

            // All other links .
            $('#widget-news a').not('#widget-news-view-all').each(function () {
                $(this).on('click.track-everything keypress.track-everything', function (e) {
                    var title = $(this).parents('.newsblock').find('a').eq(1).text();
                    pushEvent({
                        'category': 'News',
                        'action': 'click',
                        'label': title
                    });
                });
                $(this).attr("data-ga-tracked", "on");
            });
        }
    }, 100);
}(jQuery));

