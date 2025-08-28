const proxify = (link) => {
    const uri = encodeURIComponent (link.trim());
    const scheme = "https";
    const hostname = "proxy-redirector-test.lib.uchicago.edu";
    const route = "login";
    const querystring = "url=" + uri;
    const output = scheme + "://" + hostname + "/" + route + "?" + querystring;
    return output;
};

const proxifyForm = (form, pbutton, pdisplay) => {
    pbutton = document.getElementById("pbutton");
    pbutton.classList.remove("btn-secondary");
    pbutton.classList.add("btn-primary");
    const link = form.value;
    const proxified = proxify (link);
    document.getElementById ("copy_button").hidden = false;
    pdisplay.value = link ? proxified : pdisplay.value;
};

const copyLink = (form) => {
    form.select ();
    document.execCommand ("copy");
};
