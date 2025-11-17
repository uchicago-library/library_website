/**
 * @fileoverview GA4 Event Tracking Implementation
 * @version 4.7.052
 * @author [Vitor]
 * @requires jQuery
 * 
 * Script to track user interactions and send events to Google Analytics 4 (GA4)
 * using event delegation for optimal performance.
 * 
 * More information here:  https://github.com/uchicago-library/library_website/wiki/Custom-Event-labeling
 */
(function () {
    // 
    // # Section 1: Configuration constants
    //
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
        NAVBAR: 'Global Navbar',
        SEARCH_WIDGET: 'Main Search Widget',
        SHORTCUTS: 'Navbar Shortcuts',
        VUFIND_RESULTS: 'VuFind Results',
        VUFIND_RECORD: 'VuFind Record',
        WIDGET: 'Widget',
    };

    const LOCATIONS = {
        LIB: 'lib.uchicago.edu',
        VUFIND: '.lib.uchicago.edu/vufind',
        VUFIND_RESULTS: '.lib.uchicago.edu/vufind/Search/Results',
        VUFIND_RECORD: '.lib.uchicago.edu/vufind/Record',
        GUIDES: 'guides.lib.uchicago.edu',
        GUIDES_SEARCH: 'guides.lib.uchicago.edu/srch.php',
    };

    const ignoreDeferUrls = [
        "rooms.lib.uchicago.edu/appointments-auth/prepare",
    ];

    // Rules for applyHtmlProperties
    const htmlPropertyRules = [
        {
            location: LOCATIONS.LIB,
            selector: '#widget-featured-library-expert',
            childSelector: 'a',
            attribute: 'data-ga-label',
            value: "Expert's Subjects",
        },
        {
            location: LOCATIONS.VUFIND,
            selector: '.myresearch-menu.account-menu',
            attribute: 'data-ga-subcategory',
            value: "Your Account Menu",
        },
        {
            location: LOCATIONS.VUFIND_RECORD,
            selector: '.media-body table tr td a',
            attribute: 'data-ga-label',
            valueFn: function ($items, $target) {
                return $($target).closest('tr').find('th').text().trim();
            },
        },
        {
            location: LOCATIONS.VUFIND_RECORD,
            selector: '.media-body table tr td a',
            attribute: 'data-ga-subcategory',
            value: 'Record Metadata',
        },
    ];

    // 
    // # Section 2: Populate HTML properties based on rules
    // for key screens that are hard to temper with templates.
    //
    /*
     * applyHtmlProperties
     * Apply attributes (or data-*) to elements based on a list of rules.
     * - Each rule: { location, selector, attribute, value, valueFn, childSelector, useFirstHeading, overrideIfExists, apply }
     * - overrideIfExists: if true and element already has the attribute, will override existing attribute value
     * - apply: 'each' (default) or 'first' to only apply to the first matched element
     * - useFirstHeading: boolean or { levels: [1,2,3] } - finds the first heading inside the matched element (h1/h2/h3 by default)
     * - valueFn receives ( <$items: element or array of elements found by $selector>, <$target: specific element during iteration over $items> ) and should return a string value
     */
    function applyHtmlProperties(rules) {
        if (!Array.isArray(rules) || !rules.length) {
            console.warn('applyHtmlProperties: no rules provided');
            return;
        }

        function getFirstHeadingTextWithin($elem, levels, $child) {
            // Defensive: ensure $elem is present and is a jQuery object with content
            if (!$elem || !$elem.length) { return ''; }
            // Default heading preference: skip h1 (will never target h1), prefer h2,h3,h4
            // h1 will most likely never be meaningful as a parameter for an event
            //     because that information is already in the page title/path.
            levels = Array.isArray(levels) && levels.length ? levels : [2, 3, 4];
            for (let i = 0; i < levels.length; i++) {
                let lvl = levels[i];
                let $h = $elem.find('h' + lvl).first();
                if ($h.length) {
                    return $h.text().trim();
                }
            }
            return '';
        }

        rules.forEach(function (rule) {
            if (!rule || !rule.selector || !rule.attribute) { return; }

            if (rule.location && !window.location.href.includes(rule.location)) { return; }

            let $items = $(rule.selector);
            if (!$items.length) { return; }

            // If rule.apply === 'first', only use the first matched element
            if (rule.apply === 'first' || rule.childSelector) {
                $items = $items.first();
            }
            // Determine the actual target to set attribute on: 
            //      either the main matched element or it's children
            if (rule.childSelector) {
                let $children = $items.find(rule.childSelector);
                if ($children.length) {
                    $items = $children;
                } else { return; }
            }

            $items.each(function () {

                let $target = $(this); // the element matched by selector (the "main" element)
                // Defensive: ensure $target is present
                if (!$target || !$target.length) { return; }
                // Skip if attribute already exists and overrideIfExists is untrue
                if (typeof $target.attr(rule.attribute) !== 'undefined' || rule.overrideIfExists) {
                    return;
                }

                // Find heading inside the main matched element if requested (explicitly inside the main, not child)
                let headingText = '';
                if (rule.useFirstHeading) {
                    if (typeof rule.useFirstHeading === 'object' && Array.isArray(rule.useFirstHeading.levels)) {
                        headingText = getFirstHeadingTextWithin($items, rule.useFirstHeading.levels);
                    } else {
                        headingText = getFirstHeadingTextWithin($items);
                    }
                }


                // Compute value
                let val = '';
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
                } catch (e) {
                    console.warn('applyHtmlProperties failed to set attribute', rule.attribute, 'for', rule.selector, e);
                }
            });
        });

        return;
    }

    // 
    // # Section 3: Log all click events to GA4
    //

    // Manipulate data and debug
    const helpers = {
        addOptionToSearchButton: {
            checkbox(target, searchWidget) {
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
            },
            radio(target, searchWidget) {
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
            },
            select(target, searchWidget) {
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
        },
        count_indecision(ep, eventName, target) {
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
        },
        all_log(ep, eventName = '', someText = '') {
            // DEBUG, leaving it here for the first couple of weeks.
            function pad(label, width = 25) {
                return (label + ':').padEnd(width, ' ');
            }
            console.log(
                someText + '\n' +
                pad('eventName') + eventName + '\n' +
                pad('event_category') + ep.event_category + '\n' +
                pad('event_subcategory') + ep.event_subcategory + '\n' +
                pad('event_label') + ep.event_label + '\n' +
                pad('click_position') + ep.click_position + '\n' +
                pad('event_option') + (ep.event_option || '') + '\n' +
                pad('event_indecision_count') + (ep.event_indecision_count || '')
            );

        }
    };

    // Functions to determine event parameters based on link context. ----- Big logic work-horse -----
    const getEventDetails = {
        getParametersForSpecialCases(link, params) {
            // A lot of links will have this established in the HTML and will not get in here.
            // But might be of help if changes are made to the HTML without proper labeling,
            // or for websites where this script is reused.

            // Catalog VuFind Search results
            if (window.location.href.includes(LOCATIONS.VUFIND)) {
                params.event_category = params.event_category || (
                    link.closest('header, .breadcrumbs') ? CATEGORIES.NAVIGATION :
                        link.closest('footer') ? CATEGORIES.FOOTER :
                            link.closest('.sidebar') ? CATEGORIES.SIDEBAR :
                                link.closest('.main') ? CATEGORIES.MAIN :
                                    link.closest('.pager, .pagination') ? CATEGORIES.NAVIGATION :
                                        "VuFind");

                // Catalog VuFind Search results
                if (window.location.href.includes(LOCATIONS.VUFIND_RESULTS)) {
                    params.event_subcategory = params.event_subcategory || (
                        link.closest('.record-list.search-results-solr') ? 'Search Results List' :
                            link.closest('.facet-group') ? 'Facet: ' + link.closest('.facet-group').getAttribute('data-title') :
                                link.closest('[id^="side-panel"]') ? link.closest('[id^="side-panel"]').getAttribute('id') :
                                    link.closest('.action-toolbar') ? 'Action Toolbar' :
                                        link.closest('.searchtools') ? 'Search Toolbar' :
                                            link.closest('.pagination') ? 'Pagination' :
                                                link.closest('.search-sort') ? 'Sort Filter' :
                                                    "");
                    params.event_label = link.getAttribute('data-ga-label') || (
                        link.classList.contains('title') ? 'Title' :
                            link.closest('.result-author') ? 'Author' :
                                link.closest('.eLink.external') ? 'Online Access' :
                                    link.closest('.save-record') ? 'Save Record' :
                                        link.closest('.record-cover-link') ? 'Record Cover' :
                                            params.event_label || 'VuFind Results Link');

                }
                // Catalog VuFind Record
                else if (window.location.href.includes(LOCATIONS.VUFIND_RECORD)) {
                    params.event_subcategory = params.event_subcategory || (
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
                                                                link.closest('.pager') ? 'Pagination' :
                                                                    "");
                    params.event_label = link.getAttribute('data-ga-label') || (
                        link.closest('.savedLists') ? 'Record Saved in List' :
                            link.closest('.bibToggle') ? 'More Details' : // How did VSCode knew to predict the value 'More Details' here?.
                                link.classList.contains('title') ? 'Title' :
                                    link.classList.contains('result-author') ? 'Author' :
                                        link.classList.contains('save-record') ? 'Save Record' :
                                            link.closest('[href*="/Alphabrowse/"]') ? 'Call Number' :
                                                link.closest('.maplookup') ? 'Map Lookup' :
                                                    link.closest('.eLink') ? 'Online Access' :
                                                        params.event_label || 'VuFind Record Link');
                }
                // My Account
                else if (link.closest('.template-dir-myresearch')) {
                    params.event_label = link.closest('[href*="source=author"]') ? 'Author' :
                        link.closest('.title') ? 'Title' :
                            link.closest('.record-cover-link') ? 'Record Cover' :
                                params.event_label;
                }
                // Fallback for all VuFind Screens.
                params.event_subcategory = params.event_subcategory || (
                    link.closest('.search.container.navbar') ? 'Search Operations' :
                        link.closest('.breadcrumbs') ? 'Breadcrumbs' :
                            link.closest('.top-navbar, .navbar-header, .navbar-collapse') ? 'Header Navbar' :
                                link.closest('[id]') ? 'id:' + link.closest('[id]').getAttribute('id') : "VuFind Component"
                );

            }
            // Guides
            else if (window.location.href.includes(LOCATIONS.GUIDES)) {
                params.event_category = params.event_category || CATEGORIES.MAIN;
                params.event_subcategory = params.event_subcategory || (
                    link.closest('.pagination') ? 'Pagination' : CATEGORIES.MAIN
                );
                params.event_label = link.closest('.s-srch-result-guide') ? 'Guide Name' :
                    link.closest('.s-srch-result-author') ? 'Guide Author' :
                        link.closest('.s-srch-result-subjects') ? 'Guide Subject' :
                            link.closest('.s-srch-result-url') ? 'Guide Link' :
                                link.closest('.s-srch-result-title') ? 'Guide Page Title' :
                                    link.closest('.s-lg-label-more') ? 'More Button' : params.event_label || 'Unknown';

            }

            // default for basic cases where HTML was not set
            // main navbar
            else if (link.closest(SELECTORS.GLOBAL_NAV)) {
                params.event_category = params.event_category || CATEGORIES.NAVBAR;
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
            // search widget
            else if (link.closest(SELECTORS.SEARCH_WIDGET)) {
                params.event_category = params.event_category || CATEGORIES.SEARCH_WIDGET;
                const widgetParent = link.closest(SELECTORS.SEARCH_WIDGET);
                params.event_subcategory = params.event_subcategory ||
                    (widgetParent && widgetParent.id && widgetParent.id.includes('widget') ? widgetParent.id : null) || CATEGORIES.SEARCH_WIDGET;
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

            // default - catch all for everything else
            else {
                params.event_category = params.event_category || CATEGORIES.MAIN;
                params.event_subcategory = params.event_subcategory || (
                    link.closest('.action-toolbar') ? 'Action Toolbar' :
                        link.closest('.pagination') ? 'Pagination' :
                            'id:' + link.closest('[id]').getAttribute('id') || CATEGORIES.MAIN
                );
            }
            return params;
        },
        getPositionInList(link, params) {
            if (!link.closest(SELECTORS.FOOTER)) {
                let ancestor = link.closest('li');

                // For any <ul> or <ol> list
                if (ancestor) {
                    params.event_subcategory = params.event_subcategory || 'List';
                    params.click_position = Array.from(ancestor.parentElement.children).indexOf(ancestor) + 1;
                }
                // Catalog VuFind Search results
                else if (window.location.href.includes(LOCATIONS.VUFIND_RESULTS)) {
                    params.event_subcategory = params.event_subcategory || 'VuFind Search Results';
                    let ancestor = link.closest('[data-record-number]');
                    if (ancestor) {
                        params.click_position = ancestor.getAttribute('data-record-number');
                    }
                }
                // Guides Search results
                else if (window.location.href.includes(LOCATIONS.GUIDES_SEARCH)) {
                    params.event_subcategory = params.event_subcategory || 'Guides Search Results';
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
            return params;
        },
        parameters(link) {

            let params = {
                event_category: link.closest('[data-ga-category]') ?
                    link.closest('[data-ga-category]').getAttribute('data-ga-category') : null,
                event_subcategory: link.closest('[data-ga-subcategory]') ?
                    link.closest('[data-ga-subcategory]').getAttribute('data-ga-subcategory') : null,
                event_label: link.getAttribute('data-ga-label') ||
                    link.getAttribute('aria-label') ||
                    link.getAttribute('title') ||
                    ((() => {
                        // Clone the node to avoid modifying the original DOM
                        const clone = link.cloneNode(true);
                        // Remove visually-hidden elements from the clone
                        clone.querySelectorAll('.visually-hidden, .sr-only, [aria-hidden="true"]').forEach(el => el.remove());
                        // Get and clean the remaining text
                        return clone.textContent.replace(/\s+/g, ' ').trim();
                    })()) ||
                    (link.querySelector('img') ? link.querySelector('img').getAttribute('alt') : '') ||
                    'Unknown',
                click_position: parseInt(link.getAttribute('data-ga-position'), 10) || null,
                event_option: link.getAttribute('data-ga-event-option'),
                event_indecision_count: link.closest('[data-ga-indecision-count]') ?
                    link.closest('[data-ga-indecision-count]').getAttribute('data-ga-indecision-count') : null,
            };

            if (!params.event_category || !params.event_subcategory) {
                // Determine category, subcategory, based on link context.
                // should be handled mostly by HTML properties, but not always possible.
                params = getEventDetails.getParametersForSpecialCases(link, params);
            }

            if (!params.click_position) {
                // Determine position in list if applicable
                params = getEventDetails.getPositionInList(link, params);
            }

            return params;
        },
        name(target) {
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
    }

    // Main handling functions
    const handleClick = {
        linkClick(event, isMiddleClick = false) {
            const target = event.target.closest('a, button, input');
            const eventName = getEventDetails.name(target);
            if (!eventName) { return; }

            const ep = getEventDetails.parameters(target);

            helpers.count_indecision(ep, eventName, target);

            helpers.all_log(ep, eventName, '# Pre GA'); // for debugging

            gtag('event', eventName, ep);

            handleClick.deferClick(eventName, event, target.getAttribute('href'), target.target === '_blank' || isMiddleClick);
        },
        optionChange(e) {
            const target = e.target;
            const searchWidget = target.closest(SELECTORS.SEARCH_WIDGET);
            if (!searchWidget) return;
            if (target.matches('input[type="checkbox"]')) {
                helpers.addOptionToSearchButton.checkbox(target, searchWidget);
            } else if (target.matches('input[type="radio"]')) {
                helpers.addOptionToSearchButton.radio(target, searchWidget);
            } else if (target.matches('[role="tabpanel"][data-ga-subcategory="tab-catalog"] select.selectpicker.btn-searchtype')) {
                helpers.addOptionToSearchButton.select(target, searchWidget);
            }
        },
        deferClick(eventName, event, href, isNewTab) {
            // defer links that navigate away

            if (href && ignoreDeferUrls.some(u => href.toLowerCase().includes(u))) {
                // Don't interfere with auth links
                return;
            }

            if (target.hasAttribute('data-toggle') || target.classList.contains('holdingslink')) {
                // Don't interfere with the ekkolightbox or with SFX FindIt holdings links.
                return;
            }

            if (href && !isNewTab && !(eventName === 'tab' && href && href.startsWith('#'))) {
                event.preventDefault(); // delay navigation just slightly
                setTimeout(() => {
                    window.location.href = href;
                }, 200); // give GA time to fire
            }
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        if (typeof jQuery === 'undefined') {
            console.error('track-everything.js requires jQuery');
            return;
        }

        // Apply the rules now on page load
        applyHtmlProperties(htmlPropertyRules);

        document.body.addEventListener('click', handleClick.linkClick, true);

        // Handle middle-clicks (auxclick) for links and buttons.
        document.body.addEventListener('auxclick', function (e) {
            if (e.button === 1) {
                handleClick.linkClick(e, true);
            }
        }, true);

        // Add options to the search widget search button on change.
        document.body.addEventListener('change', handleClick.optionChange, true);
    });

})();
