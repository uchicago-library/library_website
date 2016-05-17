/* This contains the Loop UA. */
/* analytics_debug.js for testing, analytics.js for production. */
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics_debug.js','ga');

ga('create', 'UA-15705691-1', 'auto');
/* Enhanced link attribution */
ga('require', 'linkid');
/* Skipping _setDomainName for now. Does it cause too much trouble? */
/* Anonymize IP */
ga('set', 'anonymizeIp', true);
ga('send', 'pageview');

$(document).ready(function() {
    var q = 'https://www.lib.uchicago.edu/cgi-bin/subnetclass?jsoncallback=?';
    $.getJSON(q, function(data) {
        /* Store subnetclass. */
        ga('set', 'dimension1', data);
    });

    // Homepage widget. 
    
    // Track outbound links. 
    $('a[href^="http"]').click(function(e) {
        var link = $(this).attr('href');
        ga('send', 'event', 'outbound', 'click', link, {
            'transport': 'beacon',
            'hitCallback': function() { document.location = url; }
        });
    });
    
    // Top bar.
    // #navbar-right
    // Deal with the building pulldown. 
    // Otherwise, eventCategory=topNav, eventAction=click, eventLabel= (the text of the link, but be sure to ignore the building pulldown.) 
    
    // #navbar-right #buildingHoursDropdown
    
    // TopNav links- everything but the building hours pulldown. 
    $('#navbar-right a').not('li.dropdown a').click(function(e) {
        var linktext = $(e.target).text().trim();
        ga('send', 'event', {
            eventCategory: 'topNavLink',
            eventAction: 'click',
            eventLabel: linktext,
            transport: 'beacon'
        });
    });
});
    
    
