$(document).ready(function(){
    /* 
     * Collection browse pages "Limit to digital materials" button. 
     */

    // hide the submit button if javascript is enabled. 
    $('#checkboxebooks').closest('form').find('input[type="submit"]').hide();
    // when the checkbox is clicked, submit the form automatically. 
    $('#checkboxebooks').change(function() {
        $(this).closest('form').submit();
    });
});
