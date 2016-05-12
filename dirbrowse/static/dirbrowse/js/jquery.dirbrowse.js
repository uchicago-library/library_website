/* jquery.dirbrowse.js
 * 
 * rev. 2010/12/16 jej
 * 
 * This script communicates with a server keith set up to pull
 * directory listings.
 * 
 * ex: $('#someul').dirbrowse();
 *
 * options:
 *  initialpath
 *  project
 *  update
 */

(function($) {
	function getUrlVars() {
		var vars = {}, hash;
		
		var paramstring = window.location.href.replace(/^[^?]*\?*/, '');

		var hashes = [];
		if (paramstring)
			hashes = paramstring.split('&');

		for(var i = 0; i < hashes.length; i++) {
			hash = hashes[i].split('=');
			vars[hash[0]] = decodeURIComponent(hash[1]);
		}
		return vars;
	}

	$.fn.dirbrowse = function(options) {
		var self = this;

		/* set the path to the value of the url parameter 'path' that was
		 * passed to this page. If there is no path parameter, use the value of
		 * the 'initialpath' parameter passed to this plugin.
	 	 */

		var path = '';
		var params = getUrlVars();

		if (params['path'])
			path = params['path'];
		else
			path = options['initialpath'];

		var q = 'http://www.lib.uchicago.edu/cgi-bin/dirbrowse';
		q += '?project=' + options['project'];
		q += '&path=' + path;
		q += '&jsoncallback=?';

		/* Make sure no underscore timestamp parameter gets sent to the
		 * backend. */
		$.ajaxSetup({
			'cache': true
		});

		$.getJSON(q, function(data) { 
            options['update'](data);
		});
	};
})(jQuery);

