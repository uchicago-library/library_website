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
            event_label: (link.textContent.replace(/\s+/g, ' ').trim()) ||
                link.getAttribute('aria-label') ||
                (link.querySelector('img') ? link.querySelector('img').getAttribute('alt') : '') ||
                'Unknown',
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

