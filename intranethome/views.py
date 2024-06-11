import json
import re
from functools import cmp_to_key
from string import ascii_lowercase, ascii_uppercase

from base.wagtail_hooks import (
    get_required_groups,
    has_permission,
    redirect_users_without_permissions,
)
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import ProgrammingError
from django.shortcuts import render
from library_website.settings import MAIL_ALIASES_PATH
from site_settings.models import ContactInfo
from wagtail.models import Site

try:
    message_text = ContactInfo.objects.first().report_a_problem
except (ProgrammingError, AttributeError):
    message_text = ""

parse_error_message = {
    "error": {
        "link_url": message_text,
    }
}


def parse_file(filepath):
    """
    Parse the mail aliases json into a Python dictionary.  Does not
    attempt to handle for syntactically invalid JSON.

    Args:
        filepath: string file path to the JSON

    Returns:
        output: error dictionary when the filepath is bad, ok followed
        by the parse result if the filepath is good
    """

    try:
        with open(filepath) as f:
            contents = f.read()
            return {"ok": json.loads(contents)}
    except (FileNotFoundError, PermissionError):
        return parse_error_message


def get_first_key(dct):
    """
    Return the first key in a dictionary.  Useful for dealing with
    single-key dictionaries, which are common in our mail aliases JSON.

    Args:
        dct: a dictionary

    Returns:
        key: a dictionary key
    """
    key = ""
    for k, v in dct.items():
        key = k
        break
    return key


def comparison(tup1, tup2):
    """
    Custom comparison function for alphanumerically sorting a dictionary
    by mail alias keys.

    Args:
        str1: one alias
        str2: another alias

    Returns:
        integer: a value that tells the sort_aliases function which
        alias is "smaller" and should go first
    """
    str1 = tup1[0].lower()
    str2 = tup2[0].lower()

    def cmp(a, b):
        return (a > b) - (a < b)

    def starts_with_number(string):
        return string[0].isnumeric()

    if starts_with_number(str1) and not (starts_with_number(str2)):
        return 1
    elif not (starts_with_number(str1)) and starts_with_number(str2):
        return -1
    else:
        return cmp(str1, str2)


def sort_aliases(js):
    """
    Sorts the mail aliases dictionary by alias.

    Args:
        js: the parsed JSON read from disk

    Returns:
        the same dictionary, sorted by alias according to comparison
    """
    return dict(sorted(js.items(), key=cmp_to_key(comparison)))


def figure_out_email(unparsed_email):
    """
    Classifies an email address string into one of four categories: note,
    plain email, angle brackets email, parens email, or local alias.

    Returns a dictionary whose key is the classification and whose value is a
    string in the case of notes and plain emails, and a list in the case of
    syntactically complex email strings.

    Args:
        a string representing an email address

    Returns:
        a parse result showing how the email address will display
    """

    def helper_triangle_brackets(tri_match):
        """
        A function to parse angle bracket emails.

        Args:
            tri_match: a regular expression match object
        Returns:
            a list consisting of the name, the email address, and the
            original string
        """
        return [
            tri_match[1].strip(),
            tri_match[2],
            tri_match[0],
        ]

    def helper_parentheses(paren_match):
        """
        A function to parse parenthesis emails.

        Args:
            paren_match: a regular expression match object

        Returns:
            a list consisting of the name, the email address, and the
            original string
        """
        return [
            paren_match[2],
            paren_match[1].strip(),
            paren_match[0],
        ]

    triangle_match = re.search("(.*)<(.*)>", unparsed_email)
    paren_match = re.search("(.*)\s*\((.*)\)", unparsed_email)
    bare_email_match = re.search(".*@.*", unparsed_email)

    if triangle_match:
        return {"triangle_brackets": helper_triangle_brackets(triangle_match)}
    elif paren_match:
        return {"parentheses": helper_parentheses(paren_match)}
    elif bare_email_match:
        return {"plain_email": unparsed_email}
    else:
        return {"local": unparsed_email}


def include_alias(alias, filt):
    """
    Filter predicate for a/b/c/Number/etc. in the top menu.

    Args:
        alias: mail alias string
        filt: filter string from the URL params (a/b/c/etc.)

    Returns:
        a boolean
    """
    if filt == "number":
        return alias[0].isdigit()
    elif filt.isalpha() and len(filt) == 1:
        return alias[0].lower() == filt.lower()
    else:
        return True


def convert_list_to_dict(aliases_json, filt=""):
    """
    Transforms initial JSON parse from mail aliases file into JSON
    representing what Wagtail will display in the template.

    Args:
        aliases_json: dictionary parse result of parse_file
        filt: filter string from the URL params (a/b/c/etc.)

    Returns:
        aliases: a dictionary containing all mail aliases data to be
        passed into the context
    """

    def values(alias_dct):
        return alias_dct[get_first_key(alias_dct)]

    def note_or_email(dct):
        first = get_first_key(dct)
        if first == "note":
            return {"note": "note: " + dct["note"]}
        elif first == "email":
            return figure_out_email(dct["email"])
        else:
            return {}

    aliases = sort_aliases(
        {
            get_first_key(dct): [note_or_email(entry) for entry in values(dct)]
            for dct in aliases_json
            if values(dct) and include_alias(get_first_key(dct), filt)
        }
    )

    return aliases


def mail_aliases_view(request, *args, **kwargs):
    """
    View for mail aliases page.

    Args: http request, regexp-ed string

    Returns: http response
    """

    parsed_file = parse_file(MAIL_ALIASES_PATH)

    loop_homepage = Site.objects.get(site_name="Loop").root_page

    # check whether user has permission to be on Loop; redirect if not
    if not has_permission(request.user, get_required_groups(loop_homepage)):
        return redirect_users_without_permissions(loop_homepage, request, None, None)

    try:
        alias_filter = kwargs["alias_filter"].lower()
    except KeyError:
        alias_filter = ""

    try:
        _ = parsed_file["error"]
        context = parsed_file
    except KeyError:
        final_data = convert_list_to_dict(parsed_file["ok"], alias_filter)
        context = {"final_data": final_data}

    return render(request, "intranethome/mail_aliases.html", context)
