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

    function update(data) {
		var yearRe = new RegExp('[0-9]{4}');
	
		var getKeys = function(obj) {
			var keys = [];
			for(var key in obj) {
				keys.push(key);
			}
			return keys;
		}

		var getSeasons = function(records) {
			var seasons = new Array();
			$.each(records, function(i, r) {
				switch (r['season']) {
					case 'Winter':
						var season = r['year'] + '-01';
						break;
					case 'Spring':
						var season = r['year'] + '-04';
						break;
					case 'Summer':
						var season = r['year'] + '-07';
						break;
					case 'Fall':
						var season = r['year'] + '-10';
						break;
				}
				seasons[season] = true;
			});
			return getKeys(seasons);
		}

		var getRecordsForSeason = function(records, year, season) {
			var out = new Array();
			$.each(records, function(i, r) {
				if (r['year'] == year && r['season'] == season) {
					out.push(r);
				}
			});
			return out;
		}

		function getUrlPath() {
			return window.location.href.replace(/\?.*$/, '');
		}

		/* 
		 * s = pretty printed string.
		 * t = title.
		 * l = link.
		 */
		var getFields = function(s, t, l) {
			// remove the course name from the pretty string.
			var s = s.replace(t + ' ', '');
	
			// execute a regular expression to get some of the other parts. 
			var r = yearRe.exec(s);
	
			// get the year
			var year = r[0];
	
			// get the instructor
			var prof = s.substring(0, r['index'] - 1);
	
			// get the season
			var seasonStart = s.indexOf(' ', r['index'] + 4) + 1;
			var seasonStop = s.indexOf(' ', seasonStart);
			var season = s.substring(seasonStart, seasonStop);
	
			// get the kind of document
			var doc = s.substring(seasonStop + 1);
	
			return {
				'title': t,
				'prof': prof,
				'year': year,
				'season': season,
				'doc': doc,
				'link': l
			};
		}

		/* Update the title of the directory listing. */
		var length = data['title'].length;	

		var title = data['title'][length - 1]['pretty'];
		$('#dirbrowsetitle').html(title);

		var links = new Array();

		/* 
		 * If is entry in the directory listing is itself a directory,
		 * then create a link to this page with an updated 'path'
		 * parameter. 
		 * 
		 * Otherwise, create a link to the file specified in the 
		 * data that came in from the backend.
		 */

		if (data['content'][0]['type'] == 'dir') {
			var ul = $('<ul></ul>').appendTo($('#dirbrowse'));
			$.each(data['content'], function(i, d) {
				var params = getUrlVars();
				params.path = d.path;

				var hash = [];
				$.each(params, function(k, v) {
					hash.push(k + "=" + escape(v));
				});

				path = getUrlPath() + "?" + hash.join('&');
				ul.append('<li><a href="' + path + '">' + d['pretty'] + '</a></li>');
			});
		} else if (data['content'][0]['type'] == 'file') {
			/* 
			 * Build an object of data for each class, grouped by
			 * professor.
			 */
			var profs = {};
			$.each(data['content'], function(i, d) {
				var fields = getFields(d['pretty'], title, d['link']);
				var prof = fields['prof'];
				if (!(prof in profs)) {
					profs[prof] = new Array();
				}
				profs[prof].push(fields);
			});

			$.each(getKeys(profs), function(i1, p) {
				$('#dirbrowse').append('<h3>' + p + '</h3>');

				var ul = $('<ul></ul>').appendTo('#dirbrowse');

				var lis = new Array();
				var seasons = getSeasons(profs[p]);
				$.each(getSeasons(profs[p]), function(i2, s) {
					var chunks = s.split('-');
					var year = chunks[0];
					switch (chunks[1]) {
						case '01':
							var season = 'Winter';
							break;
						case '04':
							var season = 'Spring';
							break;
						case '07':
							var season = 'Summer';
							break;
						case '10':
							var season = 'Fall';
							break;
					};
					var links = new Array();
					$.each(getRecordsForSeason(profs[p], year, season), function(i3, r) {
						if (i3 == 0) {
							links.push('<a href="' + r['link'] + '">' + season + ' ' + year + ' ' + r['doc'] + '</a>');
						} else {
							links.push('<a href="' + r['link'] + '">' + r['doc'] + '</a>');
						}
					});
					lis.push('<li>' + links.join(' - ') + '</li>');
				});
				ul.append(lis.reverse().join(''));
			});
		}
    }

    $('#dirbrowse').dirbrowse({
        initialpath: '.',
        project: 'law-exams',
        update: update
    }); 

    function on_homepage() {
        return location.href.match(/\?.*path\=/) === null;
    }

    /*
     * It takes a certain amount of time for the content to appear on
     * the page. The following function loops until the content appears
     * on the page. 
     */

    var interval_id = 0;
    function process_dirbrowse() {
        if (on_homepage()) {
            $('#nonhomepagecontent').hide();
            $('#dirbrowsetitle').text('');

            if ($('#dirbrowse li').size() > 0) {
                clearInterval(interval_id);
                /* Add elements in reverse order before the ul in
                 * dirbrowse. There is probably a good way to do this.
                 */
                $('#dirbrowse').prepend("<h3>Second and Third Year Courses</h3>");

                var ul = $('<ul></ul>').prependTo('#dirbrowse');
                $.each(
                    ['Civil_Procedure', 'Contracts', 'Criminal_Law', 'Elements', 'Property', 'Torts'],
                    function(i, v) {
                        var e = 'a[href $= "path=' + v + '"]';
                        var li = $(e).parent('li');
                        $(li).appendTo(ul);
                    }
                );
                $('#dirbrowse').prepend("<h3>First Year Courses</h3>");
            }
        } else {
            $('#homepagecontent').hide();
    }

    /* Clean up links to files that we aren't interested in. */
    $("li a[href*='path=undefined']").remove();

    }
    interval_id = setInterval(process_dirbrowse, 100);
});
