const proxify = (link) => {
  const uri = encodeURIComponent (link.trim());
  const scheme = "https";
  const hostname = "proxy-redirector-test.lib.uchicago.edu";
  const route = "login";
  const querystring = "url=" + uri;
  const output = scheme + "://" + hostname + "/" + route + "?" + querystring;
  return output;
};

const proxifyForm = (form, pdisplay) => { // eslint-disable-line no-unused-vars
  form.reportValidity();
  const pbutton = document.getElementById("pbutton");
  const cbutton = document.getElementById("copy_button");
  pbutton.classList.remove("btn-primary");
  pbutton.classList.add("btn-secondary");
  cbutton.classList.remove("btn-secondary");
  cbutton.classList.add("btn-primary");
  const link = form.value;
  const proxified = proxify (link);
  if (form.checkValidity()) {
    pdisplay.value = link ? proxified : pdisplay.value;
    cbutton.disabled = false;
  }
};


const copyLink = (form) => { // eslint-disable-line no-unused-vars
  form.select ();
  document.execCommand ("copy");
};
