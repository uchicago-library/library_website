$(document).ready(function() {
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

	function getUrlPath() {
		return window.location.href.replace(/\?.*$/, '');
	}

    function update(data) {
        var params = getUrlVars();

		/* Update the title of the directory listing if we're not on the main page. */
        if (params['path'] && params['path'] != '.') {
		    var length = data['title'].length;	
		    $('#dirbrowsetitle').html(data['title'][length - 1]['pretty']);
        }

		var links = new Array();
		$.each(data['content'], function(i, d) {
			/* 
			 * If is entry in the directory listing is itself a directory,
			 * then create a link to this page with an updated 'path'
			 * parameter. 
			 * 
			 * Otherwise, create a link to the file specified in the 
			 * data that came in from the backend.
			 */

			if (d['type'] == 'dir') {
				var params = getUrlVars();
				params.path = d.path;

				var hash = [];
				$.each(params, function(k, v) {
					hash.push(k + "=" + escape(v));
				});

				path = getUrlPath() + "?" + hash.join('&');

			} else if (d['type'] == 'file') {
				path = d['link'];
			} else {
				return;
			}
			links.push('<li><a href="' + path + '">' + d['pretty'] + '</a></li>');
		});
		$('#dirbrowse').html(links.join(''));
    }

    $('#dirbrowse').dirbrowse({
        initialpath: '.',
        project: 'physics',
        update: update
    });
});
