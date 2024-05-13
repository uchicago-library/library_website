function singleAccordionToggle() {
    var panel = this.nextElementSibling;
    if (panel.style.maxHeight) {
	panel.style.maxHeight = null;
    }
    else {
	panel.style.maxHeight = 0;
    }
}

function enableButtonListening(){
    const accordionElements = document.getElementsByClassName("accordion");
    var i;

    for (i = 0; i < accordionElements.length; i++) {
	accordionElements[i].addEventListener("click", singleAccordionToggle);
    }
}

function expandAll(){
    const accordionElements = document.getElementsByClassName("accordion");
    var i;

    for (i = 0; i < accordionElements.length; i++) {
	var panel = accordionElements[i].nextElementSibling;
	panel.style.maxHeight = null;
    }
}

function contractAll(){
    const accordionElements = document.getElementsByClassName("accordion");
    var i;

    for (i = 0; i < accordionElements.length; i++) {
	var panel = accordionElements[i].nextElementSibling;
	panel.style.maxHeight = 0;
    }
}

enableButtonListening();
contractAll();
