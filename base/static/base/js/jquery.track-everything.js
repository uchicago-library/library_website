/**
 * @fileoverview GA4 Event Tracking Implementation
 * @version 3.0.0
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
 * - event_option
 * - event_indecision_count
 * 
 * `event_category`: Navigation, Main, Sidebar, Floating (Alert banners, feedback button), Main Search Widget, Global Navbar
 * 
 * `event_subcategory`: Recognizable content or function blocks. 
 *      Typically has a conceptual term like: List, Widget, Table, Form, Toolbar
 *      ex: Global Navbar, Footer, Left Sidebar, Right Sidebar, Search Widget, *** Widget, Recent News, News List, Search Results List,
 *      defaults to: .getAttribute('aria-labelledby'), .closest('[id]').getAttribute('id'),
 * 
 * `event_label`: The actual link or button text, image alt text, or aria-label, role of the link. Where links are typically highly dynamic, the role of the link will be preferred
 *      Generic `event_label`: .getAttribute('aria-label'), .textContent, .getAttribute('title'), .getAttribute('alt'), 'Unknown'
 *      VuFind `event_label`: 'Title', 'Author', 'Holding', 'Save Record', 'Unknown'
 *      Guides `event_label`: 'Guide Name', 'Guide Author', 'Guide Subject', 'Guide Link', 'Guide Page Title', 'More Button', 'Unknown'
 * 
 * `click_position` can be based on the index of a `<li>` item, a `<div>` as a ('.newsblock, article'), a row on a table 
 * 
 * `event_option` adds any checkbox or radio button selected to the main link, like search options in the home page search widget
 * 
 * `event_indecision_count` counts how many times a user has clicked on tabs or dropdowns before making a final selection
 * 
 * Features:
 * - Event delegation for efficient event handling
 * - Debounced event processing to prevent excessive API calls (not enabled, was not working)
 * - Automatic detection of event categories based on DOM context
 * - Support for custom data attributes (data-ga-*) overrides
 * - Fallback handling for missing labels, categories, and sub-categories
 * - Position tracking for list items
 * - with specific selectors for .news-wrap, .news-stories, VuFind, and Guides
 * 
 * Usage:
 * Add data-ga-* attributes to track custom parameters:
 * <a href="#" data-ga-category="custom" data-ga-label="My Link">Link</a>
 * Add data-ga-category and data-ga-subcategory to parent elements to set context for child links.
 */
(function () {
    console.log('loading jquery.track-everything.js');




    // Configuration constants
    const SELECTORS = {
        GLOBAL_NAV: '#global-navbar',
        NAVBAR_RIGHT: '#navbar-right',
        WIDGET: '.widget, [id*="widget"]',
        SEARCH_WIDGET: '#search-widget',
        SIDEBAR: '[class^="sidebar"], [id*="sidebar"], .rightside, [role="complementary"], ul.nav.nav-pills.nav-stacked',
        FOOTER: 'footer',
        TAB: '[role="tab"], [data-role="tab"], .spaces-toggle',
        DROPDOWN: '[data-bs-toggle="dropdown"], [data-toggle="dropdown"]',
        CHECKBOX_RADIO: 'input[type="checkbox"], input[type="radio"]',
        BUTTON_A: 'button, a'
    };

    const CATEGORIES = {
        NAVIGATION: 'Navigation',
        FOOTER: 'Footer',
        SIDEBAR: 'Sidebar',
        MAIN: 'Main',
        SHORTCUTS: 'Navbar Shortcuts',
        VUFIND_RESULTS: 'VuFind Results',
        VUFIND_RECORD: 'VuFind Record',
        WIDGET: 'Widget',
    };

    const LOCATIONS = {
        LIB: 'catalog.lib.uchicago.edu/vufind/Search/Results',
        VUFIND: 'catalog.lib.uchicago.edu/vufind/',
        VUFIND_RESULTS: 'catalog.lib.uchicago.edu/vufind/Search/Results',
        VUFIND_RECORD: 'catalog.lib.uchicago.edu/vufind/Record/',
        GUIDES_SEARCH: 'guides.lib.uchicago.edu/srch.php',
        GUIDES: 'guides.lib.uchicago.edu',
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





    /*
     * applyHtmlProperties
     * Apply attributes (or data-*) to elements based on a list of rules.
     * - Each rule: { location, selector, attribute, value, valueFn, childSelector, useFirstHeading, onlyIfMissing, apply }
     * - apply: 'each' (default) or 'first' to only apply to the first matched element
     * - useFirstHeading: boolean or { levels: [1,2,3] } - finds the first heading inside the matched element (h1/h2/h3 by default)
     * - valueFn receives ( $mainMatchedElement, $targetElement ) and should return a string value
     */
    function applyHtmlProperties(rules) {
        if (!Array.isArray(rules)) { return; }

        function getFirstHeadingTextWithin($elem, levels, $child) {
            // Defensive: ensure $elem is present and is a jQuery object with content
            if (!$elem || !$elem.length) { return ''; }
            // Default heading preference: skip h1 (will never target h1), prefer h2,h3,h4
            levels = Array.isArray(levels) && levels.length ? levels : [2, 3, 4];
            for (var i = 0; i < levels.length; i++) {
                var lvl = levels[i];
                var $h = $elem.find('h' + lvl).first();
                if ($h.length) {
                    return $h.text().trim();
                }
            }
            return '';
        }

        rules.forEach(function (rule) {
            if (!rule || !rule.selector || !rule.attribute) { return; }

            if (rule.location && window.location.href.indexOf(rule.location) === -1) { return; }

            var $items = $(rule.selector);
            if (!$items.length) { return; }

            // If rule.apply === 'first', only use the first matched element
            if (rule.apply === 'first' || rule.childSelector) {
                $items = $items.first();
            }
            // Determine the actual target to set attribute on: 
            //      either the main matched element or it's children
            if (rule.childSelector) {
                var $children = $items.find(rule.childSelector);
                if ($children.length) {
                    $items = $children;
                } else { return; }
            }

            console.log('applyHtmlProperties found', $items.length, 'items for selector', rule.selector);

            $items.each(function () {
                console.log('applyHtmlProperties processing', rule.selector, 'for attribute', rule.attribute);

                var $target = $(this); // the element matched by selector (the "main" element)
                // Defensive: ensure $target is present
                if (!$target || !$target.length) { return; }
                // Skip if attribute already exists and onlyIfMissing is true
                if (rule.onlyIfMissing && typeof $target.attr(rule.attribute) !== 'undefined') {
                    return;
                }

                // Find heading inside the main matched element if requested (explicitly inside the main, not child)
                var headingText = '';
                if (rule.useFirstHeading) {
                    if (typeof rule.useFirstHeading === 'object' && Array.isArray(rule.useFirstHeading.levels)) {
                        headingText = getFirstHeadingTextWithin($items, rule.useFirstHeading.levels);
                    } else {
                        headingText = getFirstHeadingTextWithin($items);
                    }
                }


                // Compute value
                var val = '';
                try {
                    if (rule.valueFn && typeof rule.valueFn === 'function') {
                        // Give both the main matched element and the final target element to the value function
                        val = rule.valueFn($items, $target) || '';
                    } else if (rule.useFirstHeading) {
                        val = headingText || '';
                    } else if (typeof rule.value !== 'undefined') {
                        val = rule.value;
                    } else {
                        // nothing to set
                        return;
                    }
                } catch (e) {
                    console.warn('applyHtmlProperties valueFn error for selector', rule.selector, e);
                    return;
                }

                // Set attribute (support data-* via attr so it appears in DOM)
                try {
                    $target.attr(rule.attribute, val);
                    console.log('applyHtmlProperties set', rule.attribute, 'for', rule.selector, 'to:', val);
                } catch (e) {
                    console.warn('applyHtmlProperties failed to set attribute', rule.attribute, 'for', rule.selector, e);
                }
            });
        });
    }
    // Example rules for applyHtmlProperties - fill these in as needed
    var htmlPropertyRules = [
        {
            location: LOCATIONS.LIB,
            selector: '#widget-featured-library-expert',
            childSelector: 'a',
            attribute: 'data-ga-label',
            value: "Expert's Subjects",
        },
        {
            location: LOCATIONS.VUFIND_RECORD,
            selector: '.media-body table tr td a',
            attribute: 'data-ga-label',
            valueFn: function ($items, $target) {
                return $($target).closest('tr').find('th').text().trim();
            },
        },
    ];
    // Example rules for applyHtmlProperties - fill these in as needed
    var ExampleHtmlPropertyRules = [
        // 1) Set a data attribute on each .record-header using the first heading inside the record header
        {
            selector: '.record .record-header',
            attribute: 'data-first-heading',
            useFirstHeading: true,
            apply: 'each'
        },
        // 2) Set the label for the main home page widgets.
        {
            selector: '#widget-featured-library-expert',
            childSelector: 'a',
            attribute: 'data-test-label',
            valueFn: function ($items, $target) {
                var mainClassAttr = $items.attr('class') || '';
                var mainClass = '';
                if (mainClassAttr) {
                    var classes = mainClassAttr.split(/\s+/).filter(function (c) { return c; });
                    if (classes.length) {
                        mainClass = classes.reduce(function (a, b) { return a.length >= b.length ? a : b; }, '');
                    }
                }
                if (!mainClass) {
                    mainClass = $target.text().trim();
                }
                return mainClass;
            },
            apply: 'each'
        },
        // 3) Example: derive a role value from a class on the target element (assumes class like 'role-admin' => 'admin')
        {
            selector: '.some-role-element',
            attribute: 'role',
            valueFn: function ($items, $target) {
                var classes = ($target.attr('class') || '').split(/\s+/);
                for (var i = 0; i < classes.length; i++) {
                    var m = classes[i].match(/^role-(.+)$/);
                    if (m) { return m[1]; }
                }
                return '';
            },
            onlyIfMissing: true,
            apply: 'each'
        }
    ];

    // Apply the example rules now on page load
    applyHtmlProperties(htmlPropertyRules);
    console.log('ran htmlPropertyRules');








    // Function to determine event parameters based on link context. ----- Big logic work-horse -----
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
            click_position: link.getAttribute('data-ga-position') || null,
            event_option: link.getAttribute('data-ga-event-option') || null,
            event_indecision_count: link.getAttribute('data-ga-indecision-count') || null,
        };

        // Look for Category and Subcategory in parent elements
        // This will handle most cases
        if (!params.event_category && link.closest('[data-ga-category]')) {
            params.event_category = link.closest('[data-ga-category]').getAttribute('data-ga-category');
        }
        if (!params.event_subcategory && link.closest('[data-ga-subcategory]')) {
            params.event_subcategory = link.closest('[data-ga-subcategory]').getAttribute('data-ga-subcategory');
        }

        if (!params.event_indecision_count && link.closest('[data-ga-indecision-count]')) {
            params.event_indecision_count = link.closest('[data-ga-indecision-count]').getAttribute('data-ga-indecision-count') || null;
        }

        // Determine category, subcategory, based on link context.
        if (!params.event_category || !params.event_subcategory) {
            // A lot of links will have this established in the HTML and will not get in here.
            // But might be of help if changes are made to the HTML without proper labeling,
            // or for websites where this script is reused.
            // main navbar
            if (link.closest(SELECTORS.GLOBAL_NAV)) {
                params.event_category = params.event_category || CATEGORIES.NAVIGATION;
                const listParent = link.closest('ul, ol');
                params.event_subcategory = params.event_subcategory ||
                    (listParent ? listParent.getAttribute('aria-labelledby') : null) ||
                    params.event_label || CATEGORIES.NAVIGATION;
            }
            // shortcuts
            else if (link.closest(SELECTORS.NAVBAR_RIGHT)) {
                params.event_category = params.event_category || CATEGORIES.NAVIGATION;
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
                params.event_category = params.event_category || CATEGORIES.MAIN;
                const widgetParent = link.closest(SELECTORS.WIDGET);
                params.event_subcategory = params.event_subcategory ||
                    (widgetParent && widgetParent.id && widgetParent.id.includes('widget') ? widgetParent.id : null) || CATEGORIES.WIDGET;
            }
            // any sidebar
            else if (link.closest(SELECTORS.SIDEBAR)) {
                params.event_category = params.event_category || CATEGORIES.SIDEBAR;
                const sidebarParent = link.closest(SELECTORS.SIDEBAR);
                params.event_subcategory = params.event_subcategory ||
                    (sidebarParent && sidebarParent.id && sidebarParent.id.includes('sidebar') ? sidebarParent.id : '') ||
                    (sidebarParent && sidebarParent.className && sidebarParent.className.split(' ').find(function (c) { return c.includes('sidebar'); }) || "Sidebar Widget");
            }
            // Catalog VuFind Search results
            else if (window.location.href.indexOf(LOCATIONS.VUFIND) > -1) {
                params.event_category = params.event_category ||
                    link.closest('header, .breadcrumbs') ? CATEGORIES.NAVIGATION :
                    link.closest('footer') ? CATEGORIES.FOOTER :
                        link.closest('.sidebar') ? CATEGORIES.SIDEBAR :
                            link.closest('.main') ? CATEGORIES.MAIN :
                                "VuFind";

                // Catalog VuFind Search results
                if (window.location.href.indexOf(LOCATIONS.VUFIND_RESULTS) > -1) {
                    params.event_subcategory = params.event_subcategory ||
                        link.closest('.top-navbar, .navbar-header, .navbar-collapse') ? 'Header Navbar' :
                        link.closest('.search.container.navbar') ? 'Search Operations' :
                            link.closest('.record-list.search-results-solr') ? 'Search Results List' :
                                link.closest('.facet-group') ? link.closest('.facet-group').getAttribute('data-title') :
                                    link.closest('.action-toolbar') ? 'Action Toolbar' :
                                        link.closest('.searchtools') ? 'Search Toolbar' :
                                            link.closest('.pagination') ? 'Pagination' :
                                                link.closest('.search-sort') ? 'Sort Filter' :
                                                    link.closest('[id]').getAttribute('id') || "VuFind Results Widget";
                    params.event_label = link.classList.contains('title') ? 'Title' :
                        link.classList.contains('result-author') ? 'Author' :
                            link.classList.contains('external') ? 'Holding' :
                                link.classList.contains('save-record') ? 'Save Record' :
                                    params.event_label || 'Unknown';

                }
                // Catalog VuFind Record
                else if (window.location.href.indexOf(LOCATIONS.VUFIND_RECORD) > -1) {
                    params.event_subcategory = params.event_subcategory ||
                        link.closest('.top-navbar, .navbar-header, .navbar-collapse') ? 'Header Navbar' :
                        link.closest('.search.container.navbar') ? 'Search Operations' :
                            link.closest('.breadcrumbs') ? 'Breadcrumbs' :
                                link.closest('#bookplates') ? "Bookplates" :
                                    link.closest('.media-left') ? "Record Media" :
                                        link.closest('.savedLists') ? "Record Saved in Lists" :
                                            link.closest('.media-body, .bibToggle') ? "Record Metadata" :
                                                link.closest('.related__title, .record-tab.similar, .tab-pane.similar-tab') ? 'Record Similar Items' :
                                                    link.closest('.record-tab.holdings, .tab-pane.holdings-tab') ? 'Record Holdings' :
                                                        link.closest('.record-tab.description, .tab-pane.description-tab') ? 'Record Description' :
                                                            link.closest('.record-tab.toc, .tab-pane.toc-tab') ? 'Record Table of Contents' :
                                                                link.closest('.record-tab.details, .tab-pane.details-tab') ? 'Record Staff View' :
                                                                    link.closest('.action-toolbar') ? 'Action Toolbar' :
                                                                        link.closest('[id]').getAttribute('id') || "VuFind Record Widget";
                    params.event_label = link.closest('.savedLists') ? 'Record Saved in List' :
                        link.closest('.bibToggle') ? 'More Details' : // How did VSCode knew to predict the value 'More Details' here?.
                            link.classList.contains('title') ? 'Title' :
                                link.classList.contains('result-author') ? 'Author' :
                                    link.classList.contains('external') ? 'Holding' :
                                        link.classList.contains('save-record') ? 'Save Record' :
                                            params.event_label || 'Unknown';

                }
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
            // default - probably main content
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
                // Catalog VuFind Search results
                else if (window.location.href.indexOf(LOCATIONS.VUFIND_RESULTS) > -1) {
                    let ancestor = link.closest('[data-record-number]');
                    if (ancestor) {
                        params.click_position = ancestor.getAttribute('data-record-number');
                    }
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

        // Force to global nav dropdowns t
        if (target.matches(SELECTORS.DROPDOWN) &&
            target.closest(SELECTORS.GLOBAL_NAV)) {
            return 'tab';
        }
        // Check if event target or direct parent is defined as a tab
        else if (target.matches(SELECTORS.TAB) ||
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

    function count_indecision(ep, eventName, target) {
        // Function to count indecision clicks on tabs and dropdowns
        // --- indecision count logic ---
        if (eventName === 'tab') {
            const component = target.closest('[data-ga-category]');
            if (component) {
                let count = parseInt(component.getAttribute('data-ga-indecision-count') || '0', 10) + 1;
                if (isNaN(count)) count = 1;
                component.setAttribute('data-ga-indecision-count', count);
            }
        }
    }





    function all_log(ep, eventName) {
        // DEBUG, leaving it here for the first couple of weeks.
        function pad(label, width = 25) {
            return (label + ':').padEnd(width, ' ');
        }
        console.log(
            pad('eventName') + eventName + '\n' +
            pad('event_category') + ep.event_category + '\n' +
            pad('event_subcategory') + ep.event_subcategory + '\n' +
            pad('event_label') + ep.event_label + '\n' +
            pad('click_position') + ep.click_position + '\n' +
            pad('event_option') + (ep.event_option || '') + '\n' +
            pad('event_indecision_count') + (ep.event_indecision_count || '')
        );

    }

    function defer_link_click(eventName, event, href, isNewTab) {
        // for links that navigate away
        // const isNewTab = target.target === '_blank' || event.ctrlKey || event.metaKey || event.shiftKey || isMiddleClick; // UNTESTED
        // const isNewTab = event.target === '_blank' || isMiddleClick;
        if (href && !isNewTab && !(eventName === 'tab' && href && href.startsWith('#'))) {
            event.preventDefault(); // delay navigation just slightly
            setTimeout(() => {
                window.location.href = href;
            }, 200); // give GA time to fire
        }
    }

    function handleCheckboxChange(target, searchWidget) {
        const searchButtons = searchWidget.querySelectorAll('button.btn-search[type="submit"][data-ga-subcategory="' + target.getAttribute('data-ga-subcategory') + '"]');
        if (searchButtons.length) {
            searchButtons.forEach((searchButton) => {
                let optionText = target.getAttribute('data-ga-label');
                let currentOption = searchButton.getAttribute('data-ga-event-option') || '';
                if (target.checked) {
                    // Add option
                    if (currentOption) {
                        if (!currentOption.split('; ').includes(optionText)) {
                            currentOption += '; ' + optionText;
                        }
                    } else {
                        currentOption = optionText;
                    }
                } else {
                    // Remove option
                    currentOption = currentOption.split('; ').filter(opt => opt !== optionText).join('; ');
                }
                searchButton.setAttribute('data-ga-event-option', currentOption);
            });
        }
    }

    function handleRadioChange(target, searchWidget) {
        const searchButtons = searchWidget.querySelectorAll('button.btn-search[type="submit"][data-ga-subcategory="' + target.getAttribute('data-ga-subcategory') + '"]');
        if (searchButtons.length) {
            searchButtons.forEach((searchButton) => {
                let optionText = target.getAttribute('data-ga-label');
                let currentOption = searchButton.getAttribute('data-ga-event-option') || '';
                let optionsArr = currentOption ? currentOption.split('; ') : [];
                // Remove any previous rad:... entry
                optionsArr = optionsArr.filter(opt => !opt.startsWith('radio:'));
                if (target.checked) {
                    optionsArr.push('radio:' + optionText);
                }
                currentOption = optionsArr.join('; ');
                searchButton.setAttribute('data-ga-event-option', currentOption);
            });
        }
    }

    function handleSelectPickerChange(target, searchWidget) {
        const searchButton = searchWidget.querySelector('button[type="submit"].btn-search');
        if (searchButton) {
            let selectedValue = target.value.trim();
            let currentOption = searchButton.getAttribute('data-ga-event-option') || '';
            let optionsArr = currentOption ? currentOption.split('; ') : [];
            // Remove any previous type:... entry
            optionsArr = optionsArr.filter(opt => !opt.startsWith('type:'));
            if (selectedValue !== 'AllFields') {
                optionsArr.push('type:' + selectedValue);
            }
            currentOption = optionsArr.join('; ');
            searchButton.setAttribute('data-ga-event-option', currentOption);
        }
    }




    // Function to handle link clicks and send events to GA4. ----- MAIN FUNCTION -----
    function handleLinkClick(event, isMiddleClick = false) {
        const target = event.target.closest('a, button, input');
        const eventName = getEventName(target);
        if (!eventName) { return; }

        const ep = getEventParameters(target);

        count_indecision(ep, eventName, target);

        all_log(ep, eventName); // for debugging

        gtag('event', eventName, ep);

        defer_link_click(eventName, event, target.getAttribute('href'), target.target === '_blank' || isMiddleClick);
    }

    // Function to add option changes (checkboxes, radio buttons, select pickers) in the search widget to the main search button.
    function handleOptionChange(e) {
        const target = e.target;
        const searchWidget = target.closest(SELECTORS.SEARCH_WIDGET);
        if (!searchWidget) return;
        if (target.matches('input[type="checkbox"]')) {
            handleCheckboxChange(target, searchWidget);
        } else if (target.matches('input[type="radio"]')) {
            handleRadioChange(target, searchWidget);
        } else if (target.matches('[role="tabpanel"][data-ga-subcategory="tab-catalog"] select.selectpicker.btn-searchtype')) {
            handleSelectPickerChange(target, searchWidget);
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        // Attach a single event listener to the document body using event delegation.
        // document.body.addEventListener('click', debounce(handleLinkClick, 200));

        document.body.addEventListener('click', handleLinkClick, true);

        // Handle middle-clicks (auxclick) for links and buttons.
        document.body.addEventListener('auxclick', function (e) {
            if (e.button === 1) {
                handleLinkClick(e, true);
            }
        }, true);

        // Add options to the search widget search button on change.
        document.body.addEventListener('change', handleOptionChange, true);
    });
})();