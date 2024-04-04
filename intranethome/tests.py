from django.test import SimpleTestCase

# TODO: write new tests to reflect the updated code in views.py

from intranethome.views import (
    formatting,
    comparison,
)

class test_mail_aliases_view(SimpleTestCase):
    def test_comparison(self):
        alias1 = "banana"
        alias2 = "APPLE"
        alias3 = "1Candy"
        alias4 = "2Candy"
        alias5 = "1dumplings"
        self.assertEqual(comparison(alias1, alias2), 1)
        self.assertEqual(comparison(alias1, alias3), -1)
        self.assertEqual(comparison(alias3, alias4), -1)
        self.assertEqual(comparison(alias3, alias5), -1)

    def test_formatting(self):
        list_of_options = []
        option1_triangle_brackets = "I am triangle\t \t<i_am_triangle@uchicago.edu>"
        option2_parentheses = "i_am_parentheses@uchicago.edu (I am parentheses)"
        option3_plain_email = "i_am_plain@uchicago.edu"
        option4_local = "i_am_local"
        list_of_options.append(option1_triangle_brackets)
        list_of_options.append(option2_parentheses)
        list_of_options.append(option3_plain_email)
        list_of_options.append(option4_local)
        
        self.assertEqual(
            formatting(list_of_options), 
            [   {
                    "triangle_brackets": [
                        "I am triangle",
                        "i_am_triangle@uchicago.edu",
                        option1_triangle_brackets,
                    ]
                },
                {
                    "parentheses": [
                        "I am parentheses",
                        "i_am_parentheses@uchicago.edu",
                        option2_parentheses,
                    ]
                },
                {"plain_email": option3_plain_email},
                {"local": option4_local}])