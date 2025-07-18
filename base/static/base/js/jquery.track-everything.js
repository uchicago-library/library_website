/**
 * @fileoverview GA4 Event Tracking Implementation
 * @version 2.0.1
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
 * `event_category`: 'Navigation', 'Footer', 'Widget', 'Sidebar', 'Main', 'VuFind Results'
 * 
 * `event_subcategory`: 'List', 'News List', 'Table', .getAttribute('aria-labelledby'), 'Footer', 'Main', sidebarParent.id, sidebar className, widgetParent.id, 'Navbar Shortcuts', 'Action Toolbar', 'Searchtools', 'Pagination', .getAttribute('id'), 'Search Form', 'Center Column', 'Right Column'
 * 
 * Generic `event_label`: .getAttribute('aria-label'), .textContent, .getAttribute('title'), .getAttribute('alt'), 'Unknown'
 * VuFind `event_label`: 'Title', 'Author', 'Holding', 'Save Record', 'Unknown'
 * Guides `event_label`: 'Guide Name', 'Guide Author', 'Guide Subject', 'Guide Link', 'Guide Page Title', 'More Button', 'Unknown'
 * 
 * `click_position` can be based on the index of a `<li>` item, a `<div>` as a ('.newsblock, article'), a row on a table 
 * 
 * Features:
 * - Event delegation for efficient event handling
 * - Debounced event processing to prevent excessive API calls
 * -- commented out, was not working
 * - Automatic detection of event categories based on DOM context
 * - Support for custom data attributes (data-ga-*) overrides
 * - Fallback handling for missing labels, categories, and sub-categories
 * - Position tracking for list items
 * - with specific selectors for .news-wrap, .news-stories, VuFind, and Guides
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
        SIDEBAR: '[class^="sidebar"], [id*="sidebar"], .rightside, [role="complementary"], ul.nav.nav-pills.nav-stacked',
        FOOTER: 'footer',
        TAB: '[role="tab"], [data-role="tab"], .spaces-toggle',
        DROPDOWN: '[data-bs-toggle="dropdown"], [data-toggle="dropdown"]',
        CHECKBOX_RADIO: 'input[type="checkbox"], input[type="radio"]',
        BUTTON_A: 'button, a'
    };

    const LOCATIONS = {
        VUFIND: 'lib.uchicago.edu/vufind/Search/Results',
        GUIDES: 'guides.lib.uchicago.edu',
        GUIDES_SEARCH: 'guides.lib.uchicago.edu/srch.php',
    };

    const CATEGORIES = {
        NAVIGATION: 'Navigation',
        FOOTER: 'Footer',
        WIDGET: 'Widget',
        SIDEBAR: 'Sidebar',
        MAIN: 'Main',
        SHORTCUTS: 'Navbar Shortcuts',
        VUFIND_RESULTS: 'VuFind Results',
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
            // main navbar
            if (link.closest(SELECTORS.GLOBAL_NAV)) {
                params.event_category = params.event_category || CATEGORIES.MAIN;
                const listParent = link.closest('ul, ol');
                params.event_subcategory = params.event_subcategory ||
                    (listParent ? listParent.getAttribute('aria-labelledby') : null) ||
                    params.event_label || CATEGORIES.MAIN;

            }
            // shortcuts
            else if (link.closest(SELECTORS.NAVBAR_RIGHT)) {
                params.event_category = params.event_category || CATEGORIES.SHORTCUTS;
                params.event_subcategory = params.event_subcategory || CATEGORIES.SHORTCUTS;

            }
            // footer
            else if (link.closest(SELECTORS.FOOTER)) {
                params.event_category = params.event_category || CATEGORIES.FOOTER;
                const listParent = link.closest('ul, ol');
                params.event_subcategory = params.event_subcategory ||
                    (listParent ? listParent.getAttribute('aria-labelledby') : null) || CATEGORIES.FOOTER;

            }
            // any widget
            else if (link.closest(SELECTORS.WIDGET)) {
                params.event_category = params.event_category || CATEGORIES.WIDGET;
                const widgetParent = link.closest(SELECTORS.WIDGET);
                params.event_subcategory = params.event_subcategory ||
                    (widgetParent?.id.includes('widget') ? widgetParent.id : null) || null;

            }
            // any sidebar
            else if (link.closest(SELECTORS.SIDEBAR)) {
                params.event_category = params.event_category || CATEGORIES.SIDEBAR;
                const sidebarParent = link.closest(SELECTORS.SIDEBAR);
                params.event_subcategory = params.event_subcategory ||
                    (sidebarParent?.id.includes('sidebar') ? sidebarParent.id : '') ||
                    (sidebarParent?.className.split(' ').find(c => c.includes('sidebar')) || null);

            }
            // Catalog Vufind Search results
            else if (window.location.href.indexOf(LOCATIONS.VUFIND) > -1) {
                params.event_category = params.event_category || CATEGORIES.VUFIND_RESULTS;
                params.event_subcategory = params.event_subcategory ||
                    link.closest('.action-toolbar') ? 'Action Toolbar' :
                    link.closest('.searchtools') ? 'Searchtools' :
                        link.closest('.pagination') ? 'Pagination' :
                            link.closest('[id]').getAttribute('id');
                params.event_label = link.classList.contains('title') ? 'Title' :
                    link.classList.contains('result-author') ? 'Author' :
                        link.classList.contains('external') ? 'Holding' :
                            link.classList.contains('save-record') ? 'Save Record' :
                                params.event_label || 'Unknown';

            }
            // Guides
            else if (window.location.href.indexOf(LOCATIONS.GUIDES) > -1) {
                params.event_category = params.event_category || CATEGORIES.MAIN;
                params.event_subcategory = params.event_subcategory ||
                    link.closest('#s-lg-guide-search-form') ? 'Search Form' :
                    link.closest('#s-lg-col-1') ? 'Center Column' :
                        link.closest('#s-lg-col-2') ? 'Right Column' :
                            link.closest('#navbar-right') ? CATEGORIES.SHORTCUTS :
                                link.closest('.pagination') ? 'Pagination' : CATEGORIES.MAIN;
                params.event_label = link.closest('.s-srch-result-guide') ? 'Guide Name' :
                    link.closest('.s-srch-result-author') ? 'Guide Author' :
                        link.closest('.s-srch-result-subjects') ? 'Guide Subject' :
                            link.closest('.s-srch-result-url') ? 'Guide Link' :
                                link.closest('.s-srch-result-title') ? 'Guide Page Title' :
                                    link.closest('.s-lg-label-more') ? 'More Button' : params.event_label || 'Unknown';

            }
            // main content
            else {
                params.event_category = params.event_category || CATEGORIES.MAIN;
                params.event_subcategory = params.event_subcategory ||
                    link.closest('#navbar-right') ? CATEGORIES.SHORTCUTS :
                    link.closest('.action-toolbar') ? 'Action Toolbar' :
                        link.closest('.pagination') ? 'Pagination' :
                            link.closest('[id]').getAttribute('id') || CATEGORIES.MAIN;
            }
        }

        // Get link position if in a list
        if (!link.closest(SELECTORS.FOOTER)) {
            if (link.getAttribute('data-ga-position')) {
                params.event_subcategory = params.event_subcategory || 'List';
                params.click_position = parseInt(link.getAttribute('data-ga-position'), 10);
            } else {
                let ancestor = link.closest('li');

                // For any <ul> or <ol> list
                if (ancestor) {
                    params.event_subcategory = params.event_subcategory || 'List';
                    params.click_position = Array.from(ancestor.parentElement.children).indexOf(ancestor) + 1;
                }
                // Guides
                else if (window.location.href.indexOf(LOCATIONS.GUIDES_SEARCH) > -1) {
                    let ancestor = link.closest('.s-srch-results');
                    let item = link.closest('.s-srch-result');
                    if (ancestor && item && !link.closest('.pagination')) {
                        params.click_position = Array.from(ancestor.children).indexOf(item) + 1;
                    }
                }
                // for the news list on the home page and on the news page
                else if ((ancestor = link.closest('.news-wrap, .news-stories'))) {
                    params.event_subcategory = params.event_subcategory || 'News List';
                    params.click_position = Array.from(ancestor.children).indexOf(link.closest('.newsblock, article')) + 1;
                }
                // for collex but works for any table actually
                else if ((ancestor = link.closest('tbody'))) {
                    params.event_subcategory = params.event_subcategory || 'Table';
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
    function handleLinkClick(event, isMiddleClick = false) {
        const target = event.target.closest('a, button, input');
        const eventName = getEventName(target);
        if (!eventName) { return; }

        const ep = getEventParameters(target);
        // DEBUG, leaving it here for the first couple of weeks.
        console.log("Event Name: " + eventName + "\n" + ep.event_category + "\n" + ep.event_subcategory + "\n" + ep.event_label + "\n" + ep.click_position);
        gtag('event', eventName, ep);

        // for links that navigate away
        const href = target.getAttribute('href');
        // const isNewTab = target.target === '_blank' || event.ctrlKey || event.metaKey || event.shiftKey || isMiddleClick; // UNTESTED
        const isNewTab = target.target === '_blank' || isMiddleClick;
        if (href && !isNewTab && !(eventName === 'tab' && href && href.startsWith('#'))) {
            event.preventDefault(); // delay navigation just slightly
            setTimeout(() => {
                window.location.href = href;
            }, 200); // give GA time to fire
        }
    }

    document.addEventListener('DOMContentLoaded', function () {

        // Attach a single event listener to the document body using event delegation.
        // document.body.addEventListener('click', debounce(handleLinkClick, 200));

        document.body.addEventListener('click', handleLinkClick, true);
        // Handle middle-clicks (auxclick) for links and buttons.
        document.body.addEventListener('auxclick', function (e) {
            if (e.button == 1) {
                handleLinkClick(e, true);
            }
        }, true);
    });
})();