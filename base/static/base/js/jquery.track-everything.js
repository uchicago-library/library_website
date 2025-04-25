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
        NAVBAR_RIGHT: '#navbar-right',
        WIDGET: '.widget, [id*="widget"]',
        SIDEBAR: '[class^="sidebar"], [id*="sidebar"]'
    };

    const CATEGORIES = {
        NAVIGATION: 'navigation',
        SHORTCUTS: 'navbar-shortcuts',
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
                (link.textContent.replace(/\s+/g, ' ').trim()) ||
                link.getAttribute('title') ||
                (link.querySelector('img') ? link.querySelector('img').getAttribute('alt') : '') ||
                'Unknown',
            click_position: null,
        };

        // Determine category, subcategory, based on link context.
        if (link.closest(SELECTORS.GLOBAL_NAV)) { // main navbar
            params.event_category = params.event_category || CATEGORIES.NAVIGATION;
            const listParent = link.closest('ul, ol');
            params.event_subcategory = params.event_subcategory ||
                (listParent ? listParent.getAttribute('aria-labelledby') : null) ||
                params.label || CATEGORIES.NAVIGATION;

        } else if (link.closest(SELECTORS.NAVBAR_RIGHT)) { // shortcuts
            params.event_category = params.event_category || CATEGORIES.SHORTCUTS;
            params.event_subcategory = params.event_subcategory || CATEGORIES.SHORTCUTS;

        } else if (link.closest('footer')) { // footer
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
            params.event_category = CATEGORIES.SIDEBAR;
            const sidebarParent = link.closest(SELECTORS.SIDEBAR);
            params.event_subcategory = link.getAttribute('data-ga-subcategory') ||
                (sidebarParent?.id.includes('sidebar') ? sidebarParent.id : '') ||
                (sidebarParent?.className.split(' ').find(c => c.includes('sidebar')) || null);

        } else { // main content
            params.event_category = params.event_category || CATEGORIES.MAIN;
            params.event_subcategory = params.event_category || link.closest('[id]').getAttribute('id');
        }

        // Get link position if in a list
        if (link.getAttribute('data-ga-position')) {
            params.event_subcategory = params.event_subcategory || 'list';
            params.click_position = parseInt(link.getAttribute('data-ga-position'), 10);
        } else {
            const parentLi = link.closest('li');
            if (parentLi) {
                params.event_subcategory = params.event_subcategory || 'list';
                params.click_position = Array.from(parentLi.parentElement.children).indexOf(parentLi) + 1;
            } else {
                const parentNews = link.closest('.news-wrap');
                if (parentNews) {
                    params.event_subcategory = params.event_subcategory || 'news-list';
                    params.click_position = Array.from(parentNews.children).indexOf(link.closest('.newsblock')) + 1;
                } else {
                    const parentNews = link.closest('.news-stories');
                    if (parentNews) {
                        params.event_subcategory = params.event_subcategory || 'news-list';
                        params.click_position = Array.from(parentNews.children).indexOf(link.closest('article')) + 1;
                    }
                }
            }
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
            target.matches('input[type="radio"]')) {
            return 'checkbox';
        }
        // Check if element is an <a>
        else if (target.matches('a') || target.matches('button')) {
            return 'click';
        }
        // return false and do not trigger a GA4 event
        else {
            return false;
        }
    }

    // Function to handle link clicks and send events to GA4.
    function handleLinkClick(event) {
        event.preventDefault(); // Prevents default behavior like following links
        event.stopPropagation(); // Stops event from bubbling up
        const target = event.target.closest('a, button, input');
        const eventName = getEventName(target);
        if (eventName) {
            const ep = getEventParameters(target);
            // gtag('event', eventName, eventParams);
            console.log("Event Name: " + eventName + "\n" + ep.event_category + "\n" + ep.event_subcategory + "\n" + ep.event_label + "\n" + ep.click_position);
        } else {
            console.log("No click event. Event name: " + eventName)
            console.log("No click event. Event name: " + eventName + ". event.target.tagName: " + event.target.tagName)
        }
    }

    // Attach a single event listener to the document body using event delegation.
    // document.body.addEventListener('click', debounce(handleLinkClick, 200));
    document.body.addEventListener('click', handleLinkClick);
})();

