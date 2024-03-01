from argparse import REMAINDER
from ast import Name, alias
from multiprocessing import process
from django.http import HttpResponse
from django.shortcuts import render
from functools import cmp_to_key
from library_website.settings import MAIL_ALIASES_PATH
import json
import re

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

def each_list(list_of_dicts, alias_value):
    # run this inside of each mail alias
    i = 0

    def email_or_note(dct):
        if 'email' in dct.keys():
            return list(dct.values())
        else:
            return [ ("note: " + x) for x in list(dct.values()) ]

    while i < len(list_of_dicts):
        if alias_value in list_of_dicts[i]:
            return sum([email_or_note(x) for x in list_of_dicts[i][alias_value]],[])
        i+=1

def flatten(xss):
    '''
    Flattens multiple layers of lists into a single list

    Args:
        xss: list that needs to be flattened

    Returns:
        list: the flattened list
    '''
    return [x for xs in xss for x in xs]

def starts_with_number(string):
    '''
    Checks if the first position in a string is a number

    Args:
        string: string that needs to be checked

    Returns:
        boolean: true if the string starts with a number and false otherwise
    '''
    return string[0].isnumeric()

def cmp(a, b):
    return (a > b) - (a < b)

def comparison(str1, str2):    
    '''
    Lemma function for get_sorted_aliases to know where an alias should be sorted relative to another alias

    Args:
        str1: one alias
        str2: another alias

    Returns:
        integer: a value that tells the get_sorted_alias function, which alias is "smaller" and should go first
    '''
    if starts_with_number(str1.lower()) and not(starts_with_number(str2.lower())):
        return 1
    elif not(starts_with_number(str1.lower())) and starts_with_number(str2.lower()):
        return -1
    else:
        return cmp(str1.lower(), str2.lower())
    

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

def get_sorted_aliases(parsed_data):
    '''
    Sorts the aliases

    Args:
        parsed_data: all of the json data converted into python

    Returns:
        list: the sorted aliases
    '''
    return sorted(flatten([list(x.keys()) for x in parsed_data]), key=cmp_to_key(comparison))

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

def formatting(list):
    if len(list) == 0:
        return -1
    new_list = []
    for email in list:
        parsed_email = {}

        # selecting for option 1
        triangle_brackets = re.search("(.*)<(.*)>", email)

        # selecting for option 2
        parentheses = re.search("(.*)\s*\((.*)\)", email)

        # selecting for option 3
        if not triangle_brackets and not parentheses:
            plain_email = re.search(".*@.*", email)

        # selectig for option 1
        if triangle_brackets:
            parsed_email["triangle_brackets"] = helper_function_triangle_brackets(triangle_brackets)

        # secting for option 2
        elif parentheses:
            parsed_email["parentheses"] = helper_function_parentheses(parentheses)

        # selecting for option 3
        elif plain_email:
            parsed_email["plain_email"] = plain_email[0]

        #elif email == "note":
            #parsed_email["note"] = {"note" : whatever.value}

        # selecting for option 4
        else:
            parsed_email["local"] = email
        
        new_list.append(parsed_email)

    return new_list

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



def mail_aliases_view(request):
    parsed_file = parse_file(MAIL_ALIASES_PATH)
    aliases = get_sorted_aliases(parsed_file)
    
    # grabs /mailaliases/*the_filter_value*
    url = request.get_full_path()

    # pulls *the_filter_value* out
    alias_filter = re.search("\/mailaliases\/([^\/]*)\/?", url)[1]

    # returns a full list if the filter is not either
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
        alias_filter = ""
    
    filtered_aliases = filter_by_value(aliases, alias_filter)
    final_data = {}
    for alias in filtered_aliases:
        alias_data = formatting(each_list(parsed_file, alias))
        if alias_data != -1:
            final_data[alias] = alias_data
      

    context = {'final_data': final_data}
    # f = open("/Users/irina1/tmp/dude", "w")
    # f.write(json.dumps(final_data))
    # f.close()
    return render(request, 'intranethome/mail_aliases.html', context)



# def matts_function(json):
#     return [each_list(l) for l in json]


#[ {k:v for k,v in dct.items()} for dct in p ]
#[ {alias:[e_dict for e_dict in emails] for alias,emails in alias_dict.items()} for alias_dict in p ]


# define this function:

# it makes this:

# [{'email': 'larisa walsh\t<walshl@uchicago.edu>'},
#  {'email': 'Kristin Martin\t<kmarti@uchicago.edu>'}]

# into this:

# ['larisa walsh\t<walshl@uchicago.edu>', 'Kristin Martin\t<kmarti@uchicago.edu>']

# and it makes this:

# [{'note' : 'this is a note'}]

# into this:

# ['note: this is a note']

# def adjust_emails(list_of_email_dicts):
#     pass

# [ {alias:[e_dict for e_dict in emails] for alias,emails in alias_dict.items()} for alias_dict in p ]
# [ {alias:(adjust_emails(emails)) for alias,emails in alias_dict.items()} for alias_dict in p ]
