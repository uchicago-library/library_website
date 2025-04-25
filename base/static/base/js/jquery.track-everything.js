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
        if (link.closest('#global-navbar')) { // main navbar
            params.event_category = params.event_category || 'navigation';
            const listParent = link.closest('ul, ol');
            params.event_subcategory = params.event_subcategory ||
                (listParent ? listParent.getAttribute('aria-labelledby') : null) ||
                params.label || 'navigation';

        } else if (link.closest('#navbar-right')) { // shortcuts
            params.event_category = params.event_category || 'navbar-shortcuts';
            params.event_subcategory = params.event_subcategory || 'navbar-shortcuts';

        } else if (link.closest('footer')) { // footer
            params.event_category = params.event_category || 'footer';
            const listParent = link.closest('ul, ol');
            params.event_subcategory = params.event_subcategory ||
                (listParent ? listParent.getAttribute('aria-labelledby') : null) || 'footer';

        } else if (link.closest('.widget, [id*="widget"]')) { // any widget
            params.event_category = params.event_category || 'widget';
            const widgetParent = link.closest('.widget, [id*="widget"]');
            params.event_subcategory = params.event_subcategory ||
                (widgetParent?.id.includes('widget') ? widgetParent.id : null) || null;

        } else if (link.closest('[class^="sidebar"], [role="complementary"], [id*="sidebar"]')) { // any sidebar
            params.event_category = 'sidebar';
            const sidebarParent = link.closest('[class^="sidebar"], [id*="sidebar"]');
            params.event_subcategory = link.getAttribute('data-ga-subcategory') ||
                (sidebarParent?.id.includes('sidebar') ? sidebarParent.id : '') ||
                (sidebarParent?.className.split(' ').find(c => c.includes('sidebar')) || null);

        } else { // main content
            params.event_category = params.event_category || 'main';
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

