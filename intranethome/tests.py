from django.test import SimpleTestCase

# TODO: write new tests to reflect the updated code in views.py

from intranethome.views import (
    comparison,
    get_sorted_aliases,
    formatting,
    filter_by_value,
    parse_file,
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

    def test_get_sorted_aliases(self):
        aliaslist = []
        alias1 = {"banana": [{"email": "banana@uchicago.edu"}]}
        alias2 = {"APPLE": [{"email": "APPLE@uchicago.edu"}, {"note": "APPLES ARE GOOD"}]}
        alias3 = {"1Candy": [{"email": "1Candy@uchicago.edu"}]}
        alias4 = {"2Candy": [{"email": "2Candy@uchicago.edu"}, {"email": "1_plus_1_Candy@uchicago.edu"}]}
        alias5 = {"1dumplings": [{"note": "1 dumplings are good"}]}
        aliaslist.append(alias1)
        aliaslist.append(alias2)
        aliaslist.append(alias3)
        aliaslist.append(alias4)
        aliaslist.append(alias5)
        self.assertEqual(get_sorted_aliases(aliaslist), 
                         ["APPLE", "banana", "1Candy", "1dumplings", "2Candy"])

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
        
    def test_filter_by_value(self):
        aliaslist = []
        alias1 = "banana"
        alias2 = "BAD_APPLE"
        alias3 = "1Candy"
        alias4 = "2Candy"
        alias5 = "1dumplings"
        aliaslist.append(alias1)
        aliaslist.append(alias2)
        aliaslist.append(alias3)
        aliaslist.append(alias4)
        aliaslist.append(alias5)
        self.assertEqual(filter_by_value(aliaslist, ""), aliaslist)
        self.assertEqual(filter_by_value(aliaslist, "b"), ["banana", "BAD_APPLE"])
        self.assertEqual(filter_by_value(aliaslist, "number"), ["1Candy", "2Candy", "1dumplings"])

    def test_missing_MAIL_ALIASES_PATH(self):
        path = "bad_path.json"
        self.assertEqual(parse_file(path), -1)
