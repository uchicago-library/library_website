$(document).ready(function() {
  function getUrlVars() {
    var vars = {}; var hash;
		
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
    var yearRe = /[0-9]{4}/;
	
    var getKeys = function(obj) {
      return Object.keys(obj);
    }

    var getSeasons = function(records) {
      var seasons = {};
      $.each(records, function(i, r) {
        var season;
        switch (r['season']) {
          case 'Fall':
            season = r['year'] + '-10';
            break;
          case 'Winter':
            season = r['year'] + '-01';
            break;
          case 'Spring':
            season = r['year'] + '-04';
            break;
          case 'Summer':
            season = r['year'] + '-07';
            break;
          default:
            season = r['year'] + '-00';
            break;
        }
        seasons[season] = true;
      });
      // Sort seasons by year then by season order (Fall, Winter, Spring, Summer)
      return Object.keys(seasons).sort(function(a, b) {
        var yearA = parseInt(a.split('-')[0], 10);
        var yearB = parseInt(b.split('-')[0], 10);
        var monthA = parseInt(a.split('-')[1], 10);
        var monthB = parseInt(b.split('-')[1], 10);
        if (yearA !== yearB) return yearA - yearB;
        return monthA - monthB; // This maintains the new order
      });
    }

    var getRecordsForSeason = function(records, year, season) {
      var out = new Array();
      $.each(records, function(i, r) {
        if (r['year'] == year) {
          // Match season based on the new order
          var seasonCode = {
            '10': 'Fall', '01': 'Winter', '04': 'Spring', '07': 'Summer'
          }[season.split('-')[1]];
          if (r['season'] === seasonCode) {
            out.push(r);
          }
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
      s = s.replace(t + ' ', '');
	
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

        var path = getUrlPath() + "?" + hash.join('&');
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

        var profUl = $('<ul></ul>').appendTo('#dirbrowse');

        var lis = new Array();
        var seasons = getSeasons(profs[p]);
        $.each(seasons, function(i2, s) {
          var chunks = s.split('-');
          var year = chunks[0];
          var month = chunks[1];
          var season = {
            '10': 'Fall', '01': 'Winter', '04': 'Spring', '07': 'Summer'
          }[month];
          var seasonLinks = [];
          $.each(getRecordsForSeason(profs[p], year, s), function(i3, r) {
            if (i3 == 0) {
              seasonLinks.push('<a href="' + r['link'] + '">' + season + ' ' + year + ' ' + r['doc'] + '</a>');
            } else {
              seasonLinks.push('<a href="' + r['link'] + '">' + r['doc'] + '</a>');
            }
          });
          lis.push('<li>' + seasonLinks.join(' - ') + '</li>');
        });
        profUl.append(lis.reverse().join(''));
      });
    }
  }

  $('#dirbrowse').dirbrowse({
    initialpath: '.',
    project: 'law-exams',
    update: update
  }); 

  function onHomepage() {
    return location.href.match(/\?.*path\=/) === null;
  }

  /*
     * It takes a certain amount of time for the content to appear on
     * the page. The following function loops until the content appears
     * on the page. 
     */

  var intervalId = 0;
  function processDirbrowse() {
    if (onHomepage()) {
      $('#nonhomepagecontent').hide();
      $('#dirbrowsetitle').text('');

      if ($('#dirbrowse li').size() > 0) {
        clearInterval(intervalId);
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
  intervalId = setInterval(processDirbrowse, 100);
});
