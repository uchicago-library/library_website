/* This contains the Loop UA. */
/* analytics_debug.js for testing, analytics.js for production. */
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

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
        // Store subnetclass.
        ga('set', 'dimension1', data);
    });
    //$('body').track({ debug: true });
    $('body').track();
});
    
    
