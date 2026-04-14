const agsForm = document.getElementById("ags_form");

agsForm.addEventListener("submit", function(event) {
    event.preventDefault();
    const msg = "Are you sure you want overwrite the previous AGS spreadsheet?";
    const confirmed = confirm (msg);
    if (confirmed) {
	this.submit();
    } else {
	() => {};
    }
});
