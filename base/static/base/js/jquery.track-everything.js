(function ($) {
	$.fn.track = function(options) {
		// Set defaults
		var defaults = {
			outbound: true,
			debug: false
		};
		var settings = $.extend(defaults, options);

		$.expr[':'].external = function(obj){
			return !obj.href.match(/^mailto:/) && !obj.href.match(/^tel:/) && !obj.href.match(/^#/) && (obj.hostname.replace(/^www\./i, '') != document.location.hostname.replace(/^www\./i, ''));
		};

		pushEvent = function (params) {
			var gauEventInfo = {
				'hitType'      : 'event',
				'eventCategory': params['category'],
				'eventAction'  : params['action']
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
		return this.each(function() {
            $('*[data-ga-category][data-ga-action][data-ga-label]').each(function() {
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
                            'action'  : $(this).attr('data-ga-action'),
                            'label'   : $(this).attr('data-ga-label')
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
                            'action'  : $(this).attr('data-ga-action'),
                            'label'   : $(this).attr('data-ga-label')
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
                            'action'  : $(this).attr('data-ga-action'),
                            'label'   : $(this).attr('data-ga-label')
                        });
                    });
                }
            });

            // Outbound links.
			if (settings.outbound) {
                $(this).find("a:external").each(function() {
                    // Skip anything that has been tracked already.
                    if ($(this).is('[data-ga-tracked]')) {
                        return;
                    }
                    $(this).attr("data-ga-tracked", "on");
				    $(this).on("click.track-everything keypress.track-everything", function (e) {
					    pushEvent({
                            'category': $(this).attr('data-ga-category'),
                            'action'  : $(this).attr('data-ga-action'),
                            'label'   : $(this).attr('data-ga-label')
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
                'action'  : 'click',
                'label'   : 'View all'
            });
        });
        $('#widget-explore-research-guides-view-all').attr("data-ga-tracked", "on");

        // All other links .
        $('#widget-explore-research-guides a').not('#widget-explore-research-guides-view-all').each(function() {
            $(this).on('click.track-everything keypress.track-everything', function (e) {
	            pushEvent({
                    'category': 'Guides and Course Support',
                    'action'  : 'click',
                    'label'   : $(this).text()
                });
            });
            $(this).attr("data-ga-tracked", "on");
        });

        // Featured Library Expert
        // View all link. 
        $('#widget-featured-library-expert-view-all').on('click.track-everything keypress.track-everything', function (e) {
	        pushEvent({
                'category': 'Featured Library Expert',
                'action'  : 'click',
                'label'   : 'View all'
            });
        });
        $('#widget-featured-library-expert-view-all').attr("data-ga-tracked", "on");

        // All other links .
        $('#widget-featured-library-expert a').not('#widget-featured-library-expert-view-all').each(function() {
            $(this).on('click.track-everything keypress.track-everything', function (e) {
	            pushEvent({
                    'category': 'Featured Library Expert',
                    'action'  : 'click',
                    'label'   : $(this).text()
                });
            });
            $(this).attr("data-ga-tracked", "on");
        });

        // Quick Links
        $('#widget-quicklinks a').each(function() {
            $(this).on('click.track-everything keypress.track-everything', function (e) {
		        pushEvent({
                    'category': 'Quicklinks',
                    'action'  : 'click',
                    'label'   : $(this).text()
                });
            });
            $(this).attr("data-ga-tracked", "on");
        });

        // Spaces
        $('#widget-spaces a').each(function() {
            $(this).on('click.track-everything keypress.track-everything', function (e) {
                var title = $(this).parents('p').text().split('    ').pop();
		        pushEvent({
                    'category': 'Spaces',
                    'action'  : 'click',
                    'label'   : title
                });
            });
            $(this).attr("data-ga-tracked", "on");
        });

        // Workshops and Events
        $('#widget-workshops-and-events a').each(function() {
            $(this).on('click.track-everything keypress.track-everything', function (e) {
	            pushEvent({
                    'category': 'Workshops and Events',
                    'action'  : 'click',
                    'label'   : $(this).text()
                });
            });
            $(this).attr("data-ga-tracked", "on");
        });

        // Social Media
        $('#widget-social-media a').each(function() {
            $(this).on('click.track-everything keypress.track-everything', function (e) {
	            pushEvent({
                    'category': 'Social Media',
                    'action'  : 'click',
                    'label'   : $(this).text()
                });
            });
            $(this).attr("data-ga-tracked", "on");
        });
    });

    // News
    var interval = setInterval(function() {
        console.log($('.newsblock').length);
        if ($('.newsblock').length == 0) {
            return;
        } else {
            clearInterval(interval);
            // View all link. 
            $('#widget-news-view-all').on('click.track-everything keypress.track-everything', function (e) {
	            pushEvent({
                    'category': 'News',
                    'action'  : 'click',
                    'label'   : 'View all'
                });
            });
            $('#widget-news-view-all').attr("data-ga-tracked", "on");

            // All other links .
            $('#widget-news a').not('#widget-news-view-all').each(function() {
                $(this).on('click.track-everything keypress.track-everything', function (e) {
                    var title = $(this).parents('.newsblock').find('a').eq(1).text();
	                pushEvent({
                        'category': 'News',
                        'action'  : 'click',
                        'label'   : title
                    });
                });
                $(this).attr("data-ga-tracked", "on");
            });
        }
    }, 100);
}( jQuery ));

