String.prototype.endsWith = function(suffix) {
    return this.indexOf(suffix, this.length - suffix.length) !== -1; 
};

clickHeatSite = 'www.lib';
clickHeatServer = 'https://www.lib.uchicago.edu/clickheat/click.php';
        
var paths = {}
paths['/']                                  = 'kiosk';
paths['/crerar/']                           = 'kiosk.crerar';
paths['/eck/']                              = 'kiosk.eckhart';
paths['/law/']                              = 'kiosk.law';
paths['/mansueto/']                         = 'kiosk.mansueto';
paths['/spaces/joseph-regenstein-library/'] = 'pages.regenstein';
paths['/scrc/']                             = 'pages.scrc';
paths['/research/help/ask-librarian/']      = 'pages.ask';

if (window.location.pathname in paths) {
    clickHeatGroup = paths[window.location.pathname];
    initClickHeat();
}
