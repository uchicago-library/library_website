const isProxyLink = (link) => {
    url = URL.parse(link);
    hostname = url.hostname ? url.hostname : null;
    return hostname == "proxy-redirector-test.lib.uchicago.edu";
};

const proxify = (link) => {
    const uri = encodeURIComponent (link.trim());
    const scheme = "https";
    const hostname = "proxy-redirector-test.lib.uchicago.edu";
    const route = "login";
    const querystring = "url=" + uri;
    const output = scheme + "://" + hostname + "/" + route + "?" + querystring;
    return isProxyLink (link) ? link : output;
};

const proxifyForm = (form) => {
    const link = form.value;
    const proxified = proxify (link);
    form.value = proxified;
    document.getElementById ("copy_button").hidden = false;
    document.getElementById ("proxied_link").innerHTML = "proxified link: " + proxified;
};

const copyLink = (form) => {
    form.select ();
    document.execCommand ("copy");
};

const displayText = (newText) => {
    if (newText.trim()) {
	document.getElementById ("original_link").innerHTML = "original link: " + newText;
    } else {};
};
