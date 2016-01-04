/*
 * October 2, 2012
 * Added code to try to guess affiliation and subject area. 
 */

function clearCookie(name, domain, path){
	try {
	    function Get_Cookie( check_name ) {
	            // first we'll split this cookie up into name/value
	            // pairs
	            // note: document.cookie only returns name=value, not
	            // the other components
	            var a_all_cookies = document.cookie.split(';'),
					a_temp_cookie = '',
					cookie_name = '',
					cookie_value = '',
		            b_cookie_found = false;
	    
	            for ( i = 0; i < a_all_cookies.length; i++ ) {
                    // now we'll split apart each name=value pair
                    a_temp_cookie = a_all_cookies[i].split( '=' );
    
                    // and trim left/right whitespace while we're at it
                    cookie_name = a_temp_cookie[0].replace(/^\s+|\s+$/g,
'');
    
                    // if the extracted name matches passed check_name
                    if ( cookie_name == check_name ) {
                        b_cookie_found = true;
                        // we need to handle case where cookie has no
                        // value but exists (no = sign, that is):
                        if ( a_temp_cookie.length > 1 ) {
                            cookie_value = unescape(
a_temp_cookie[1].replace(/^\s+|\s+$/g, '') );
                        }
                        // note that in cases where cookie is
                        // initialized but no value, null is returned
                        return cookie_value;
                        break;
                    }
                    a_temp_cookie = null;
                    cookie_name = '';
	            }
	            if ( !b_cookie_found ) {
	              return null;
	            }
	        }
	        if (Get_Cookie(name)) {
                var domain = domain || document.domain;
                var path = path || "/";
                document.cookie = name + "=; expires=" + new Date + "; domain=" + domain + "; path=" + path;
	        }
	}
	catch(err) {}    
};
clearCookie('__utma','.uchicago.edu','/');
clearCookie('__utmb','.uchicago.edu','/');
clearCookie('__utmc','.uchicago.edu','/');
clearCookie('__utmz','.uchicago.edu','/');

// ASYNCHRONOUS GOOGLE ANALYTICS CODE.
// http://code.google.com/apis/analytics/docs/tracking/asyncTracking.html


	/* Hack to work around sites that use JQuery's noconflict rule (the
	 * news site does this.) */
	if ($ == undefined) 
		$ = jQuery;

	/* load Google Analytics script. */
	(function() {
		var ga = document.createElement('script'); 
		ga.type = 'text/javascript'; 
		ga.async = true;
		ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
		(document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(ga);
	})();

	/* Set up GA global variable. */
	var _gaq = _gaq || [];

	var q = 'https://www.lib.uchicago.edu/cgi-bin/subnetclass?jsoncallback=?';

	$(document).ready(function() {
		$.getJSON(q, function(data) { 
			/* Enhanced link attribution */
			var pluginUrl = '//www.google-analytics.com/plugins/ga/inpage_linkid.js';
			_gaq.push(['_require', 'inpage_linkid', pluginUrl]);

			/* Generate stats for .uchicago.edu and subdomains. */
			_gaq.push(['_setAccount', 'UA-15705691-1']);
			/* This seems to need to happen second. If you do other stuff
			 * first, you'll end up with multiple copies of the cookies for
			 * different domains. */
			_gaq.push(['_setDomainName', '.lib.uchicago.edu']);
			_gaq.push(['_setCustomVar', 1, 'Location', data]); 
			/*
			if (data != 'Library Staff' || true) {
				if (window.location.hostname == 'guides.lib.uchicago.edu') {
					var guide = $.trim($('#guide_header_title').text());
					var guides = _getVisitorCustomVar(3);
					if (guides == '') {
						guides = guide;
					} else {
						guides = guides.split('|');
						if (guides.indexOf(guide) == -1) {
							guides.push(guide);
						}
						guides.sort();
						guides = guides.join('|');
					}
					_gaq.push(['_setCustomVar', 3, 'Subject Guide', guides, 1]); 
				}
				if (window.location.hostname == 'www.lib.uchicago.edu' && window.location.pathname == '/e/visitors.html') {
					_gaq.push(['_setCustomVar', 4, 'Affiliation', 'Visitor', 1]); 
				}
				if (window.location.hostname == 'www.lib.uchicago.edu' && window.location.pathname == '/e/faculty.html') {
					_gaq.push(['_setCustomVar', 4, 'Affiliation', 'Faculty', 1]); 
				}
				if (window.location.hostname == 'www.lib.uchicago.edu' && window.location.pathname == '/e/students.html') {
					_gaq.push(['_setCustomVar', 4, 'Affiliation', 'Student', 1]); 
				}
				if (window.location.hostname == 'www.lib.uchicago.edu' && window.location.pathname == '/e/staff.html') {
					_gaq.push(['_setCustomVar', 4, 'Affiliation', 'University Staff', 1]); 
				}
				if (window.location.hostname == 'www.lib.uchicago.edu' && window.location.pathname == '/e/alumnifriends/') {
					_gaq.push(['_setCustomVar', 4, 'Affiliation', 'Alum', 1]); 
				}
			}
			*/
			_gaq.push(['_gat._anonymizeIp']);
			_gaq.push(['_trackPageview']);
		});
    
        // Track outbound links. 
        $('a[href^="http"]').click(function(e) {
            _gaq.push(['_setAccount', 'UA-15705691-1']);
            _gaq.push(['_trackEvent', 'Outbound', 'Click', $(this).attr('href')]);
        });

		// SEARCH WIDGET TRACKING
		// Be sure we're on the homepage. 
        setTimeout(function() { 
		if ($('#t_catalogs, #t_articles, #t_ejournals, #t_ebooks, #t_quicklinks').length == 5) {
			// User clicks a search widget tab
			$('.ajaxtabs a').click(function(e) {
		        //e.preventDefault();
				var tabtext = $(e.target).text().trim();
				//console.log('search-widget-tab-click ' + tabtext);
		        _gaq.push(['_trackEvent', 'search-widget-tab-click', 'Click', tabtext]);
			});
			
			// User clicks a radio button
			$('div.target form.radiotabs input[type="radio"]').change(function(e) {
		        //e.preventDefault();
				var tabtext = $('.ajaxtabs a.active').text().trim();
				var radiobuttontext = $(this).parents('div.target').find('input[type="radio"]:checked').next('label').text().trim();
		        var value = tabtext + '-' + radiobuttontext;
				//console.log('search-widget-radio-button-click ' + value);
		        _gaq.push(['_trackEvent', 'search-widget-radio-button-click', 'Click', value]);
			});
			
			// User changes a pulldown on the search widget
			$('div.target select').change(function(e) {
		        //e.preventDefault();
				var tabtext = $('.ajaxtabs a.active').text().trim();
				var pulldowntext = $(e.target).val().trim();
		        var value = tabtext + '-' + pulldowntext;
				//console.log('search-widget-pulldown-change ' + value);
		        _gaq.push(['_trackEvent', 'search-widget-pulldown-change', 'Change', value]);
			});
			
			// User submits a form from the search widget. 
			$('div.target form').submit(function(e) {
		        //e.preventDefault();
				var tabtext = $('.ajaxtabs a.active').text().trim();
				var radiobuttontext = $(this).parents('div.target').find('input[type="radio"]:checked').next('label').text().trim();
		        var value = tabtext + '-' + radiobuttontext;
				//console.log('search-widget-form-submit ' + value);
		        _gaq.push(['_trackEvent', 'search-widget-form-submit', 'Submit', value]);
			});
			
			// User clicks a link to get directly to a tool. 
			$('div.target a.button').click(function(e) {
		        //e.preventDefault();
				var tabtext = $('.ajaxtabs a.active').text().trim();
				var linktext = $(e.target).text().trim();
		        var value = tabtext + '-' + linktext;
				//console.log('search-widget-tool-link ' + value);
		        _gaq.push(['_trackEvent', 'search-widget-tool-link', 'Click', value]);
			});
			
			// User clicks a 'what is this searching?' link
			$('div.target p.msg_head').click(function(e) {
		        //e.preventDefault();
				var tabtext = $('.ajaxtabs a.active').text().trim();
		        //console.log('search-widget-what-is-this-searching ' + tabtext);
		        _gaq.push(['_trackEvent', 'search-widget-what-is-this-searching', 'Click', tabtext]);
			});
			
			// User clicks a search widget quicklink. 
			$('#t_quicklinks a').click(function(e) {
		        //e.preventDefault();
				var linktext = $(e.target).text().trim();
		        //console.log('search-widget-quick-links ' + linktext);
		        _gaq.push(['_trackEvent', 'search-widget-quick-links', 'Click', linktext]);
			});
		}
        }, 1000);
		// END SEARCH WIDGET TRACKING
	
	});

