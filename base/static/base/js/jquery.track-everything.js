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
}( jQuery ));

    /* Track outbound links. 
    $('a[href^="http"]').click(function(e) {
        var link = $(this).attr('href');
        ga('send', 'event', 'outbound', 'click', link, {
            'transport': 'beacon',
            'hitCallback': function() { document.location = url; }
        });
    });
    */
