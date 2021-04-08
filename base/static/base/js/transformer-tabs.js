var Tabs = {

  init: function() {
    this.bindUIfunctions();
    this.pageLoadCorrectTab();
  },

  bindUIfunctions: function() {

    // Delegation
    $(document)
      .on("click", ".transformer-tabs a[href^='#']:not('.active')", function(event) {
        Tabs.changeTab(this.hash);
        event.preventDefault();
      })
      .on("click", ".transformer-tabs a.active", function(event) {
        Tabs.toggleMobileMenu(event, this);
        event.preventDefault();
      })
      .on("click", "#web-search a", function(event) {
        Tabs.changeTab(this.hash);
        event.preventDefault();
      });

  },

  changeTab: function(hash) {
    if (hash) {
        var anchor = $("[href=" + hash + "]");
        var div = $(hash);

        // activate correct anchor (visually)
        anchor.addClass("active").parent().siblings().find("a").removeClass("active");

        // activate correct div (visually)
        div.addClass("active").siblings().removeClass("active");

        // update URL, no history addition
        // You'd have this active in a real situation, but it causes issues in an <iframe> (like here on CodePen) in Firefox. So commenting out.
        // window.history.replaceState("", "", hash);

        // Close menu, in case mobile
        anchor.closest("ul").removeClass("open");
    }
  },

  // If the page has a hash on load, go to that tab
  pageLoadCorrectTab: function() {
    this.changeTab(document.location.hash);
  },

  toggleMobileMenu: function(event, el) {
    $(el).closest("ul").toggleClass("open");
  }

}

Tabs.init();

// propagate an input element's content to all the other forms in the
// search box
const propagate = (element) => {

    // get all the forms on the search box page
    const form1 = document.getElementById("search_form1");
    const form2 = document.getElementById("search_form2");
    const form3 = document.getElementById("search_form3");
    const form4 = document.getElementById("search_form4");
    const form5 = document.getElementById("search_form5");

    const all_the_forms = [ form1, form2, form3, form4, form5 ];

    // propagate content of input element out to other forms
    var i;
    for (i = 0; i < all_the_forms.length; i++) {
	all_the_forms[i].value = element.value
    }
};
