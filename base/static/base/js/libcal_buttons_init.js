// Script to initiate myscheduler on each "Schedule Appointment" button on the page.
jQuery(document).ready(function() {
    jQuery.getScript("https://api3.libcal.com/js/myscheduler.min.js", function() {
        jQuery('[id^="mysched_"]').each(function() {
            var id_num = this.id.replace('mysched_', '');
            jQuery(this).LibCalMySched({
                iid: 482, 
                lid: 0, 
                gid: 0, 
                uid: id_num, 
                width: 560, 
                height: 680, 
                title: 'Make an Appointment', 
                domain: 'https://api3.libcal.com'
            });
        });
    });
});

