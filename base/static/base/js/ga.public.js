/* This contains the Loop UA. 
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','//www.google-analytics.com/analytics.js','ga');

ga('create', 'UA-34607019-1', 'auto');
ga('send', 'pageview');
*/

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
        _gaq.push(['_gat._anonymizeIp']);
        _gaq.push(['_trackPageview']);
    });

    // Homepage widget. 
    
    // Track outbound links. 
    $('a[href^="http"]').click(function(e) {
        _gaq.push(['_setAccount', 'UA-15705691-1']);
        _gaq.push(['_trackEvent', 'Outbound', 'Click', $(this).attr('href')]);
    });
    
    // Top bar.
    // #navbar-right
    // Deal with the building pulldown. 
    // Otherwise, eventCategory=topNav, eventAction=click, eventLabel= (the text of the link, but be sure to ignore the building pulldown.) 
    
    // #navbar-right #buildingHoursDropdown
    
    // TopNav links- everything but the building hours pulldown. 
    $('#navbar-right a').not('li.dropdown a').click(function(e) {
        var linktext = $(e.target).text().trim();
        if (testing_mode) {
            console.log('search-widget-tab-click ' + linktext);
        } else {
            _gaq.push(['_trackEvent', 'search-widget-tab-click', 'Click', linktext]);
        }
    });
});
    
    
