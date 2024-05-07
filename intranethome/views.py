from argparse import REMAINDER
from ast import Name, alias
from base.wagtail_hooks import (
    get_required_groups,
    has_permission,
    redirect_users_without_permissions,
)
from multiprocessing import process
from django.http import HttpResponse
from django.shortcuts import render
from functools import cmp_to_key
from library_website.settings import MAIL_ALIASES_PATH
import json
import re
from wagtail.models import Site


def parse_file(filepath):
    '''
    Opens and reads the json data and converts it into python

    Args:
        filepath: string file path to access the json

    Returns:
        output: dictionary that contains all of the converted json data
    '''

    with open(filepath) as f:
        contents = f.read()
        return json.loads(contents)


def get_first_key(dct):
    key = ""
    for k, v in dct.items():
        key = k
        break
    return key


def comparison2(tup1, tup2):
    '''
    Lemma function for get_sorted_aliases to know where an alias
    should be sorted relative to another alias

    Args:
        str1: one alias
        str2: another alias

    Returns:
        integer: a value that tells the get_sorted_alias function, which
        alias is "smaller" and should go first

    '''
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


def figure_out_email(unparsed_email):

    def helper_triangle_brackets(triangle_brackets_email):
        """
        A helper function that formats triangle brackets

        Args:
           a regular expression match object
        Returns:
           a list consisting of the name, the email address, and the
           original string

        """
        tb_list = []
        tb_list.append(triangle_brackets_email[1].strip())
        tb_list.append(triangle_brackets_email[2])
        tb_list.append(triangle_brackets_email[0])
        return tb_list

    def helper_parentheses(parentheses_email):
        """
        A helper function that formats parentheses emails
        Args:
           parenthese_email: an email in the format of parentheses
        Returns:
           a formatted dicionary of a list of the data in the parentheses email
        """

        formatted_parentheses_email = []
        formatted_parentheses_email.append(parentheses_email[2])
        formatted_parentheses_email.append(parentheses_email[1].strip())
        formatted_parentheses_email.append(parentheses_email[0])
        return formatted_parentheses_email

    triangle_match = re.search("(.*)<(.*)>", unparsed_email)
    paren_match = re.search("(.*)\s*\((.*)\)", unparsed_email)
    bare_email_match = re.search(".*@.*", unparsed_email)

    if triangle_match:
        return {"triangle_brackets":
                helper_triangle_brackets(triangle_match)}
    elif paren_match:
        return {"parentheses": helper_parentheses(paren_match)}
    elif bare_email_match:
        return {"plain_email": unparsed_email}
    else:
        return {"local": unparsed_email}


def convert_list_to_dict(aliases_json, filt=[]):

    def values(alias_dct):
        return alias_dct[get_first_key(alias_dct)]

    def sort_aliases(js):
        return dict(sorted(js.items(), key=cmp_to_key(comparison2)))

    def categorize_entry(dct):
        first = get_first_key(dct)
        if first == "note":
            return {"note": "note: " + dct["note"]}
        elif first == "email":
            return figure_out_email(dct["email"])
        else:
            return {}

    def include_alias(alias, filt):
        if filt == "number":
            return alias[0].isdigit()
        elif filt.isalpha() and len(filt) == 1:
            return alias[0].lower() == filt.lower()
        else:
            return True

    aliases = sort_aliases(
        {get_first_key(dct): [categorize_entry(entry)
                              for entry
                              in values(dct)]
         for dct
         in aliases_json
         if values(dct)
         and include_alias(get_first_key(dct), filt)}
    )

    return aliases


def mail_aliases_view(request, *args, **kwargs):
    parsed_file = parse_file(MAIL_ALIASES_PATH)

    # <Page: Loop>
    loop_homepage = (
        Site.objects.get(site_name="Loop").root_page
    )

    if not has_permission(request.user, get_required_groups(loop_homepage)):
        return redirect_users_without_permissions(loop_homepage,
                                                  request,
                                                  None,
                                                  None)

    try:
        alias_filter = kwargs["alias_filter"].lower()
    except KeyError:
        alias_filter = ""

    final_data = convert_list_to_dict(parsed_file, alias_filter)

    context = {'final_data': final_data}
    return render(request, 'intranethome/mail_aliases.html', context)
