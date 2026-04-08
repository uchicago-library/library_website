const agsForm = document.getElementById("ags_form");

agsForm.addEventListener ('submit', function (event) {
    event.preventDefault();
    const msg = "Are you sure you want overwrite the previous AGS spreadsheet?";
    if (confirm(msg)) {
	agsForm.submit();
    } else {
	() => {};
    }
});
