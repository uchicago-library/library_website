from django.shortcuts import render
import json
import re
from django.http import Http404
from wagtail.models import Site
from base.wagtail_hooks import (get_required_groups, has_permission, redirect_users_without_permissions
)
from library_website.settings import MAIL_ALIASES_PATH


# purpose of function: reading json text and converting to python
# input: name of file
# output: python text from the read in file
def reading_and_converting(name_of_file):
    try:
        f = open(name_of_file, "r")
    except FileNotFoundError:
        #todo: log this error
        return {"error":"error"} 
    except IOError:
        #todo: log this error
        return {"error":"error"} 
    else:
        json_text = f.read()
        f.close()
    
        data_from_file = json.loads(json_text)
        return data_from_file

# purpose of function: helper function for get_list_of_aliases to move numbers to the end
# input: the list of aliases in the original order with numbers in front
# output: the re-ordered list of aliases
def helper_function_order_number_aliases_last(all_aliases):
    list_of_numbers = []

    for alias in all_aliases:
        if alias[0] in "0123456789":
            list_of_numbers.append(alias)

    for number in list_of_numbers:
        all_aliases.remove(number)
        all_aliases.append(number)

    return all_aliases

# purpose of function: pulling the aliases of the data and creating an organized list
# input: the python data from the file
# output: a sorted list of the aliases
def get_list_of_sorted_aliases(data_from_file):
    aliases = list({ k for (k,v) in data_from_file.items() })
    aliases.sort(key=str.lower)

    aliases = helper_function_order_number_aliases_last(aliases)

    return aliases

# purpose of function: filtering the alias values to only return a subset of them based on user input
# input: the full list of aliases and the value which they are filtered by
# output: a subset of the aliases based on the filter
def filter_by_value(original_alias_list, filter_value): 
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

# purpose of function: formatting the different types of data into lists of dictionaries
# input: each individual dictionary
# output: a formatted dictionary
def uniforming_into_list_of_dict(note_or_email):
    
    # option 1: single key dictionary with key = 'email' and value with a local or gobal email
    #   {'email': 'postmaster'}

    # option 2: list of single dictionaries with  key = 'email' and value with a single local or global email, in one of 3 formats
    #   [{'email': 'lhauglan@midway.uchicago.edu'}, ..., {'email': 'd-larsen@uchicago.edu'}]
    #   [{'email': 'fierrom@uchicago.edu (Maria Fierro)'}, ..., {'email': 'hartj@uchicago.edu (Jenny Hart)'}]
    #   [{'email': 'Ariel Erbacher\t\t<aaescotese@uchicago.edu>'}, ..., {'email': 'Amy Boucher\t\t<aebouch@emory.edu>'}]

    # option 3: dictionary with key = 'note'
    #   {'note': 'emails go to command: "|/usr/local/mailman/mail/mailman post access-ip'}

    # selecting for option 1 or 3 in order to put them into both into lists
        if(type(note_or_email) == dict):

            # putting each dictionary inside of a list
            # email version:
            # i.e. {'email': 'postmaster'} ->
            #      [{'email': 'postmaster'}]
            # note version:
            # i.e. {'note': 'emails go to command: "|/usr/local/mailman/mail/mailman post access-ip'} ->
                # [{'note': 'emails go to command: "|/usr/local/mailman/mail/mailman post access-ip'}]
            return [({ k:v for (k,v) in note_or_email.items() })]
        
        # selecting for option 2 to return the input as is
        else:
            return note_or_email

# purpose: formatting option 1
# input: an unformatted option 1
# output: a formatted option 1     
def helper_function_triangle_brackets(triangle_brackets_email):
    formatted_triangle_bracket_list = []
    formatted_triangle_bracket_list.append(triangle_brackets_email[1].strip())
    formatted_triangle_bracket_list.append(triangle_brackets_email[2])
    formatted_triangle_bracket_list.append(triangle_brackets_email[0])
    return formatted_triangle_bracket_list

# purpose: formatting option 2
# input: an unformatted option 2
# output: a formatted option 2
def helper_function_parentheses(parentheses_email):
    formatted_parentheses_email = []
    formatted_parentheses_email.append(parentheses_email[2])
    formatted_parentheses_email.append(parentheses_email[1].strip())
    formatted_parentheses_email.append(parentheses_email[0])
    return formatted_parentheses_email

# purpose: coverting the formatted emails into dictionaries keyed by type with a list of values
# input: the actual email value
# output: a dictionary of a list of the email format
def format_splitting(email):
    
    # option 1: triangle brackets
    #   'Ariel Erbacher\t\t<aaescotese@uchicago.edu>' ->
    #   {'triangle_brackets': ['Ariel Erbacher', 'aaescotese@uchicago.edu', 'Ariel Erbacher\t\t<aaescotese@uchicago.edu>']}

    # option 2: parentheses
    #   'hartj@uchicago.edu (Jenny Hart)' ->
    #   {'parentheses': ['Jenny Hart', 'hartj@uchicago.edu', 'hartj@uchicago.edu (Jenny Hart)']}

    # option 3: plain email
    #   'lhauglan@midway.uchicago.edu' ->
    #   {'plain_email': 'lhauglan@midway.uchicago.edu'}

    # option 4: local email
    #   'postmaster' ->
    #   {'local': 'postmaster'}
    
    parsed_email = {}

    # checking for distro in order to remove it later
    if "distro-6052" in email:
        return -1

    # selecting for option 1
    triangle_brackets = re.search("(.*)<(.*)>", email)

    # selecting for option 2
    parentheses = re.search("(.*)\s*\((.*)\)", email)

    # selecting for option 3
    if (not triangle_brackets and not parentheses):
        plain_email = re.search(".*@.*", email)

    # selectig for option 1           
    if(triangle_brackets):
        parsed_email["triangle_brackets"] = helper_function_triangle_brackets(triangle_brackets)

    # secting for option 2     
    elif(parentheses):
        parsed_email["parentheses"] = helper_function_parentheses(parentheses)

    # selecting for option 3
    elif(plain_email):
        parsed_email["plain_email"] = plain_email[0]

    # selecting for option 4
    else:
        parsed_email["local"] = email

    return parsed_email

def mail_aliases_view(request):
    error = {}
    cleaned_data = {}

    loop_homepage = Site.objects.get(site_name='Loop').root_page
    if not has_permission(request.user, get_required_groups(loop_homepage)):
        return redirect_users_without_permissions(
            loop_homepage, request, None, None
        )

    file_data = reading_and_converting(MAIL_ALIASES_PATH)
    
    if "error" in file_data:
        error = file_data

    else:

        # grabs /mailaliases/*the_filter_value*
        url = request.get_full_path()

        # pulls *the_filter_value* out
        try:
            alias_filter = re.search("\/mailaliases\/([^\/]*)\/?", url)[1]
        except:
            alias_filter = ""

        # returns a 404 if the filter is not either
        #   1. nothing (indicating no filter) 
        #   2. "number" (indicating aliases starting with a number)
        #   3. any single letter indicating aliases starting with that letter
        if alias_filter!="" and alias_filter!="number" and (len(alias_filter) !=1 or  alias_filter not in "abcdefghijklmnopqrstuvwxyz"):
            raise Http404

        aliases = get_list_of_sorted_aliases(file_data)

        filtered_aliases = filter_by_value(aliases, alias_filter)

        for alias in filtered_aliases:

            final_list_of_notes_and_emails = []

            file_data[alias][0] = uniforming_into_list_of_dict(file_data[alias][0])

            # variable indicating the location within the list
            for email_or_note in file_data[alias][0]:

                # bypassing the 'email' key in all of the dictionaries and just using the value
                # i.e {'email': 'postmaster'} ->
                #     'postmaster'
                if 'email' in email_or_note:      

                    email_after_parsing = format_splitting(email_or_note['email'])

                    # if distro is not  present
                    if email_after_parsing != -1:
                        final_list_of_notes_and_emails.append(email_after_parsing)          

                if 'note' in email_or_note:     
                    final_list_of_notes_and_emails.append(email_or_note)

            # in case distro was the only value, this removes the associated alias
            if final_list_of_notes_and_emails != []:
                cleaned_data[alias] = final_list_of_notes_and_emails

    context = {'cleaned_data' : cleaned_data,
               'error' : error}
    return render(request, 'intranethome/mail_aliases.html', context)
