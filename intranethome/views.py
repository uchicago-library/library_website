import json
import re

from base.wagtail_hooks import (
    get_required_groups,
    has_permission,
    redirect_users_without_permissions,
)
from django.http import Http404
from django.shortcuts import render
from library_website.settings import MAIL_ALIASES_PATH
from wagtail.models import Site
import logging


def reading_and_converting(name_of_file):
    """
    Reads json text and converts it to python

    Args:
        name_of_file: the path to the file that contains the json

    Returns:
        the json data converted to a python dictionary
          OR
        a dictionary in the format {'error':'error'} to indiate that the file was not found
    """

    try:
        f = open(name_of_file, "r")
        json_text = f.read()
        f.close()    
        data_from_file = json.loads(json_text)
        return data_from_file
    except FileNotFoundError as e:
        logging.error(str(e))
        return {"error": "error"}
    except IOError as e:
        logging.error(str(e))
        return {"error": "error"}
    except json.JSONDecodeError as e:
        logging.error(str(e))
        return {"error": "error"}

def helper_function_order_number_aliases_last(all_aliases):
    """
    A helper function for the function below  which ensures that numerical aliases are ordered least to greatest at the end of the data, and the rest is sorted in abc

    Args:
        all_aliases: the unordered list of all of the aliases in the data

    Returns:
        an ordered list of the aliases
    """

    list_of_numbers = []

    for alias in all_aliases:
        if alias[0] in "0123456789":
            list_of_numbers.append(alias)

    for number in list_of_numbers:
        all_aliases.remove(number)
        all_aliases.append(number)

    return all_aliases


def get_list_of_sorted_aliases(data_from_file):
    """
    The function that selects for the alias values and sorts them while ignoring capitalization

    Args:
       data_from_file: all of the data that is pulled from the json file and converted to python

    Returns:
       a list of the fully ordered aliases after further being sorted by the helper function above
    """

    aliases = list({k for (k, v) in data_from_file.items()})
    aliases.sort(key=str.lower)

    aliases = helper_function_order_number_aliases_last(aliases)

    return aliases


def filter_by_value(original_alias_list, filter_value):
    """
    Filters the complete list of aliases by letter or number based on user input

    Args:
       original_alias_list: the full value of aliases that will filtered from

       filter_value: the value that is being used as the filter (e.g. a letter like 'c', 'number' for all numerical aliases or '' to display all)

    Returns:
       a list of the filtered aliases
    """

    filtered_alias_list = []

    for alias in original_alias_list:

        # if the filter is number
        if filter_value == "number":
            if alias[0] in "0123456789":
                filtered_alias_list.append(alias)

        # if the filter is a single letter
        elif filter_value != "":
            if alias[0] == filter_value:
                filtered_alias_list.append(alias)

        # if the filter is nothing, indicating that all values should be displayed
        else:
            return original_alias_list

    return filtered_alias_list


def uniforming_into_list_of_dict(notes_or_emails):
    """
    Converts all of the emails and notes into the same format (lists of dictionaries) in order to be able to work with the data more easiily

    Args:
       notes_or_emails: a single note or email dictionary (option 1 or 3) or a list of notes and emails (option 2) that will be converted into the correct format

       Possible Inputs:

          option 1: single key dictionary with key = 'email' and value with a local or gobal email
            {'email': 'postmaster'}

          option 2: list of single dictionaries with  key = 'email' and value with a single local or global email, in one of 3 formats
            [{'email': 'lhauglan@midway.uchicago.edu'}, ..., {'email': 'd-larsen@uchicago.edu'}]
            [{'email': 'fierrom@uchicago.edu (Maria Fierro)'}, ..., {'email': 'hartj@uchicago.edu (Jenny Hart)'}]
            [{'email': 'Ariel Erbacher\t\t<aaescotese@uchicago.edu>'}, ..., {'email': 'Amy Boucher\t\t<aebouch@emory.edu>'}]

          option 3: dictionary with key = 'note'
            {'note': 'emails go to command: "|/usr/local/mailman/mail/mailman post access-ip'}

    Returns:
       the properly formatted list of dictionaries
    """

    # selecting for option 1 or 3 in order to put them into both into lists
    if type(notes_or_emails) == dict:

        # putting each dictionary inside of a list
        # email version:
        # i.e. {'email': 'postmaster'} ->
        #      [{'email': 'postmaster'}]
        # note version:
        # i.e. {'note': 'emails go to command: "|/usr/local/mailman/mail/mailman post access-ip'} ->
        # [{'note': 'emails go to command: "|/usr/local/mailman/mail/mailman post access-ip'}]
        return [({k: v for (k, v) in notes_or_emails.items()})]

    # selecting for option 2 to return the input as is
    else:
        return notes_or_emails


def helper_function_triangle_brackets(triangle_brackets_email):
    """
    A helper function that formats trinagle brackets

    Args:
       triangle_brackets_email: an email in the format of triangle brackets

    Returns:
       a formatted dicionary of a list of the data in the triangle brackets email
    """

    formatted_triangle_bracket_list = []
    formatted_triangle_bracket_list.append(triangle_brackets_email[1].strip())
    formatted_triangle_bracket_list.append(triangle_brackets_email[2])
    formatted_triangle_bracket_list.append(triangle_brackets_email[0])
    return formatted_triangle_bracket_list


def helper_function_parentheses(parentheses_email):
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


def format_splitting(email):
    """
    A function that formats all of the emails in order for them to be easier to represent in the template and removes all values with 'distro-6052'

    Args:
       email: the unformatted email string

       Possible Inputs:

         option 1: triangle brackets
           'Ariel Erbacher\t\t<aaescotese@uchicago.edu>' ->
           {'triangle_brackets': ['Ariel Erbacher', 'aaescotese@uchicago.edu', 'Ariel Erbacher\t\t<aaescotese@uchicago.edu>']}

         option 2: parentheses
           'hartj@uchicago.edu (Jenny Hart)' ->
           {'parentheses': ['Jenny Hart', 'hartj@uchicago.edu', 'hartj@uchicago.edu (Jenny Hart)']}

         option 3: plain email
           'lhauglan@midway.uchicago.edu' ->
           {'plain_email': 'lhauglan@midway.uchicago.edu'}

         option 4: local email
           'postmaster' ->
           {'local': 'postmaster'}

    Returns:
       a dictionary that is formatted by option 1, 2, 3, or 4 depending on the type of email it was
    """

    parsed_email = {}

    # checking for distro in order to remove it later
    if "distro-6052" in email:
        return -1

    # selecting for option 1
    triangle_brackets = re.search("(.*)<(.*)>", email)

    # selecting for option 2
    parentheses = re.search("(.*)\s*\((.*)\)", email)

    # selecting for option 3
    if not triangle_brackets and not parentheses:
        plain_email = re.search(".*@.*", email)

    # selectig for option 1
    if triangle_brackets:
        parsed_email["triangle_brackets"] = helper_function_triangle_brackets(
            triangle_brackets
        )

    # secting for option 2
    elif parentheses:
        parsed_email["parentheses"] = helper_function_parentheses(parentheses)

    # selecting for option 3
    elif plain_email:
        parsed_email["plain_email"] = plain_email[0]

    # selecting for option 4
    else:
        parsed_email["local"] = email

    return parsed_email


def mail_aliases_view(request):
    """
    The main function that calls all of the other functions and runs  the mail alias page

    Args:
       request: allows the page to load and run

    Returns:
       the request, a path to the corresponding template and the dictionary of the alias data that the template helps display
    """
    error = {}
    cleaned_data = {}

    loop_homepage = Site.objects.get(site_name="Loop").root_page
    if not has_permission(request.user, get_required_groups(loop_homepage)):
        return redirect_users_without_permissions(loop_homepage, request, None, None)

    file_data = reading_and_converting('/tmp/chicken.json')

    if "error" in file_data:
        error = file_data

    else:

        # grabs /mailaliases/*the_filter_value*
        url = request.get_full_path()

        # pulls *the_filter_value* out
        alias_filter = re.search("\/mailaliases\/([^\/]*)\/?", url)[1]

        # returns a 404 if the filter is not either
        #   1. nothing (indicating no filter)
        #   2. "number" (indicating aliases starting with a number)
        #   3. any single letter indicating aliases starting with that letter
        if (
            alias_filter != ""
            and alias_filter != "number"
            and (
                len(alias_filter) != 1
                or alias_filter not in "abcdefghijklmnopqrstuvwxyz"
            )
        ):
            raise Http404

        aliases = get_list_of_sorted_aliases(file_data)

        filtered_aliases = filter_by_value(aliases, alias_filter)

        for alias in filtered_aliases:

            final_list_of_notes_and_emails = []

            file_data[alias][0] = uniforming_into_list_of_dict(
                file_data[alias][0])

            # variable indicating the location within the list
            for email_or_note in file_data[alias][0]:

                # bypassing the 'email' key in all of the dictionaries and just using the value
                # i.e {'email': 'postmaster'} ->
                #     'postmaster'
                if "email" in email_or_note:

                    email_after_parsing = format_splitting(
                        email_or_note["email"])

                    # if distro is not  present
                    if email_after_parsing != -1:
                        final_list_of_notes_and_emails.append(
                            email_after_parsing)

                if "note" in email_or_note:
                    final_list_of_notes_and_emails.append(email_or_note)

            # in case distro was the only value, this removes the associated alias
            if final_list_of_notes_and_emails != []:
                cleaned_data[alias] = final_list_of_notes_and_emails

    context = {"cleaned_data": cleaned_data, "error": error}
    return render(request, "intranethome/mail_aliases.html", context)
