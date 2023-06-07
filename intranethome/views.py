from django.shortcuts import render
from pathlib import Path
import json
import re

def mail_aliases_view(request):
    f = open("intranethome/keith_json.txt", "r")
    json_text = f.read()
    f.close()

    python_text = json.loads(json_text)

    keys = list({ k for (k,v) in python_text.items() })
    keys.sort()

    cleaned_data = {}

    for key in keys:
        if(type(python_text[key][0]) == dict):
            if 'note' in python_text[key][0].keys():
                python_text[key][0] = [({ k:v for (k,v) in python_text[key][0].items() })]
            else:
                python_text[key][0] = [({ k:v[0] for (k,v) in python_text[key][0].items() })]

        integer = 0
        for email in python_text[key][0]:
            if 'email' in email:
                python_text[key][0][integer] = email['email']

                ### splitting up formatted emails and people 
                ### putting the email itself into the last slot
                
                location = {}
                tringle_brackets = re.search("(.*)<(.*)>", email['email'])
                parentheses = re.search("(.*)\s*\((.*)\)", email['email'])
                if (not tringle_brackets and not parentheses):
                    plain_email = re.search(".*@.*", email['email'])
                
                if(tringle_brackets):
                    location["triangle_brackets"] = []
                    location["triangle_brackets"].append(tringle_brackets[1].strip())
                    location["triangle_brackets"].append(tringle_brackets[2])
                    location["triangle_brackets"].append(tringle_brackets[0])
                
                elif(parentheses):
                    location["parentheses"] = []
                    location["parentheses"].append(parentheses[2])
                    location["parentheses"].append(parentheses[1])
                    location["parentheses"].append(parentheses[0])

                elif(plain_email):
                    location["plain_email"] = (plain_email[0])

                else:
                    location["local"] = (email['email'])
            
                python_text[key][0][integer] = location

            integer += 1
        
        cleaned_data[key] = python_text[key][0]

    context = {'cleaned_data' : cleaned_data}
    return render(request, 'intranethome/mail_aliases.html', context)
