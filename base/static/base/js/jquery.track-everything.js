/**
 * @fileoverview GA4 Event Tracking Implementation
 * @version 1.0.0
 * @author [Vitor]
 * @requires jQuery
 * 
 * Script to track user interactions and send events to Google Analytics 4 (GA4)
 * using event delegation for optimal performance.
 * 
 * Schema:
 * - name
 * - event_category
 * - event_subcategory
 * - event_label
 * - click_position
 * 
 * Features:
 * - Event delegation for efficient event handling
 * - Debounced event processing to prevent excessive API calls
 * -- commented out, was not working
 * - Automatic detection of event categories based on DOM context
 * - Support for custom data attributes (data-ga-*)
 * - Fallback handling for missing labels, categories, and sub-categories
 * - Position tracking for list items
 * - with specific selectors for .news-wrap and .news-stories
 * 
 * Usage:
 * Add data-ga-* attributes to track custom parameters:
 * <a href="#" data-ga-category="custom" data-ga-label="My Link">Link</a>
 */

(function () {
    // Configuration constants
    const SELECTORS = {
        GLOBAL_NAV: '#global-navbar',
        WIDGET: '.widget, [id*="widget"]',
        SIDEBAR: '[class^="sidebar"], [id*="sidebar"], .rightside, [role="complementary"]',
        FOOTER: 'footer',
        TAB: '[role="tab"], [data-role="tab"], .spaces-toggle',
        DROPDOWN: '[data-bs-toggle="dropdown"], [data-toggle="dropdown"]',
        CHECKBOX_RADIO: 'input[type="checkbox"], input[type="radio"]',
        BUTTON_A: 'button, a'
    };

    const CATEGORIES = {
        NAVIGATION: 'navigation',
        FOOTER: 'footer',
        WIDGET: 'widget',
        SIDEBAR: 'sidebar',
        MAIN: 'main'
    };

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
            event_category: link.getAttribute('data-ga-category'),
            event_subcategory: link.getAttribute('data-ga-subcategory'),
            event_label: link.getAttribute('data-ga-label') ||
                link.getAttribute('aria-label') ||
                ((() => {
                    // Clone the node to avoid modifying the original DOM
                    const clone = link.cloneNode(true);
                    // Remove visually-hidden elements from the clone
                    clone.querySelectorAll('.visually-hidden, .sr-only, [aria-hidden="true"]').forEach(el => el.remove());
                    // Get and clean the remaining text
                    return clone.textContent.replace(/\s+/g, ' ').trim();
                })()) ||
                link.getAttribute('title') ||
                (link.querySelector('img') ? link.querySelector('img').getAttribute('alt') : '') ||
                'Unknown',
            click_position: null,
        };


        // Determine category, subcategory, based on link context.
        if (!params.event_category || !params.event_subcategory) {
            if (link.closest(SELECTORS.GLOBAL_NAV)) { // main navbar
                params.event_category = params.event_category || CATEGORIES.main;
                const listParent = link.closest('ul, ol');
                params.event_subcategory = params.event_subcategory ||
                    (listParent ? listParent.getAttribute('aria-labelledby') : null) ||
                    params.label || CATEGORIES.main;

            } else if (link.closest(SELECTORS.NAVBAR_RIGHT)) { // shortcuts
                params.event_category = params.event_category || CATEGORIES.SHORTCUTS;
                params.event_subcategory = params.event_subcategory || CATEGORIES.SHORTCUTS;

            } else if (link.closest(SELECTORS.FOOTER)) { // footer
                params.event_category = params.event_category || CATEGORIES.FOOTER;
                const listParent = link.closest('ul, ol');
                params.event_subcategory = params.event_subcategory ||
                    (listParent ? listParent.getAttribute('aria-labelledby') : null) || CATEGORIES.FOOTER;

            } else if (link.closest(SELECTORS.WIDGET)) { // any widget
                params.event_category = params.event_category || CATEGORIES.WIDGET;
                const widgetParent = link.closest(SELECTORS.WIDGET);
                params.event_subcategory = params.event_subcategory ||
                    (widgetParent?.id.includes('widget') ? widgetParent.id : null) || null;

            } else if (link.closest(SELECTORS.SIDEBAR)) { // any sidebar
                params.event_category = params.event_category || CATEGORIES.SIDEBAR;
                const sidebarParent = link.closest(SELECTORS.SIDEBAR);
                params.event_subcategory = params.event_subcategory ||
                    (sidebarParent?.id.includes('sidebar') ? sidebarParent.id : '') ||
                    (sidebarParent?.className.split(' ').find(c => c.includes('sidebar')) || null);

            } else if (window.location.href.indexOf("lib.uchicago.edu/vufind/Search/Results") > -1) { // Catalog Vufind Search results
                params.event_category = params.event_category || "vufind-search-results";
                params.event_subcategory = params.event_subcategory ||
                    link.closest('.action-toolbar') ? 'action-toolbar' :
                    link.closest('.searchtools') ? 'searchtools' :
                        link.closest('.pagination') ? 'pagination' :
                            link.closest('[id]').getAttribute('id');
                params.event_label = link.classList.contains('title') ? 'title' :
                    link.classList.contains('result-author') ? 'author' :
                        link.classList.contains('external') ? 'holding' :
                            link.classList.contains('save-record') ? 'save-record' :
                                params.event_label || 'Unknown';

            } else { // main content
                params.event_category = params.event_category || CATEGORIES.MAIN;
                params.event_subcategory = params.event_subcategory ||
                    link.closest('#navbar-right') ? 'navbar-shortcuts' :
                    link.closest('.action-toolbar') ? 'action-toolbar' :
                        link.closest('.pagination') ? 'pagination' :
                            link.closest('[id]').getAttribute('id');
            }
        }

        // Get link position if in a list
        if (!link.closest(SELECTORS.FOOTER)) {
            if (link.getAttribute('data-ga-position')) {
                params.event_subcategory = params.event_subcategory || 'list';
                params.click_position = parseInt(link.getAttribute('data-ga-position'), 10);
            } else {
                let ancestor = link.closest('li');
                // for any list
                if (ancestor) {
                    params.event_subcategory = params.event_subcategory || 'list';
                    params.click_position = Array.from(ancestor.parentElement.children).indexOf(ancestor) + 1;
                }
                // for the news list on the home page and on the news page
                else if ((ancestor = link.closest('.news-wrap, .news-stories'))) {
                    params.event_subcategory = params.event_subcategory || 'news-list';
                    params.click_position = Array.from(ancestor.children).indexOf(link.closest('.newsblock, article')) + 1;
                }
                // for collex but works for any table actually
                else if ((ancestor = link.closest('tbody'))) {
                    params.event_subcategory = params.event_subcategory || 'table';
                    params.click_position = Array.from(ancestor.children).indexOf(link.closest('tr')) + 1;
                }
            }
        }

        return params;
    }

    // Function to establish the event name
    function getEventName(target) {
        if (!target) return false;

        // Check if event target or direct parent is defined as a tab
        if (target.matches(SELECTORS.TAB) ||
            target.closest(SELECTORS.TAB)) {
            return 'tab';
        }
        // Check if target or direct parent is defined as a toggler
        else if (target.matches(SELECTORS.DROPDOWN) ||
            target.closest(SELECTORS.DROPDOWN)) {
            return 'dropdown';
        }
        // Check if target is an input of type checkbox
        else if (target.matches(SELECTORS.CHECKBOX_RADIO)) {
            return 'checkbox';
        }
        // Check if element is an <a>
        else if (target.matches(SELECTORS.BUTTON_A)) {
            return 'click';
        }
        // return false and do not trigger a GA4 event
        else {
            return false;
        }
    }

    // Function to handle link clicks and send events to GA4.
    function handleLinkClick(event) {
        const target = event.target.closest('a, button, input');
        const eventName = getEventName(target);
        if (!eventName) { return; }

        const ep = getEventParameters(target);
        // DEBUG, leaving it here for the first couple of weeks.
        console.log("Event Name: " + eventName + "\n" + ep.event_category + "\n" + ep.event_subcategory + "\n" + ep.event_label + "\n" + ep.click_position);
        gtag('event', eventName, eventParams);

        // for links that navigate away
        const href = target.getAttribute('href');
        if (href) {
            e.preventDefault(); // delay navigation just slightly
            setTimeout(() => {
                window.location.href = href;
            }, 200); // give GA time to fire
        }
    }

    // Attach a single event listener to the document body using event delegation.
    // document.body.addEventListener('click', debounce(handleLinkClick, 200));
    document.body.addEventListener('click', handleLinkClick, true);
})();