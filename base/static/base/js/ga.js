(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','//www.google-analytics.com/analytics.js','ga');

ga('create', 'UA-34607019-1', 'auto');
ga('send', 'pageview');

function relocate(href) {
    window.location = href
}

$(document).ready(function() {
    function looplinkclick(category, action, link, link_event) {
        var t = $(link).text().trim();
        var target = $(link).attr('target');
        if (target == '_blank') {
            ga('send', 'event', category, action, t);
        } else {
            var href = $(link).attr('href');
            if (href) {
                link_event.preventDefault();
                ga('send', 'event', category, action, t, {
                    hitCallback: relocate(href)
                });
            }
        }
    }

    /* main navigation links */
    $('ul.nav a').click(function (e) {
        looplinkclick('MainNavigation', 'click', $(this), e); 
    });
    /* Homepage sidebar */
    $('.swside-home a').click(function (e) {
        looplinkclick('HomepageSidebar', 'click', $(this), e); 
    });
    /* TOC page links */
    $('.sw-toc a').click(function (e) {
        looplinkclick('TOCLinks', 'click', $(this), e); 
    });
});
