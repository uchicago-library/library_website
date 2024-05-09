from django.test import SimpleTestCase

from .views import (comparison,
                    sort_aliases,
                    )


class test_mail_aliases_view(SimpleTestCase):

    def test_comparison(self):
        alias1 = ("banana", "")
        alias2 = ("APPLE", "")
        alias3 = ("1Candy", "")
        alias4 = ("2Candy", "")
        alias5 = ("1dumplings", "")
        self.assertEqual(comparison(alias1, alias2), 1)
        self.assertEqual(comparison(alias1, alias3), -1)
        self.assertEqual(comparison(alias3, alias4), -1)
        self.assertEqual(comparison(alias3, alias5), -1)

    def test_sort_aliases(self):
        pre_sort = {"banana": [{"email": "banana@uchicago.edu"}],
                    "APPLE": [{"email": "APPLE@uchicago.edu"},
                              {"note": "APPLES ARE GOOD"}],
                    "1Candy": [{"email": "1Candy@uchicago.edu"}],
                    "2Candy": [{"email": "2Candy@uchicago.edu"},
                               {"email": "1_plus_1_Candy@uchicago.edu"}],
                    "1dumplings": [{"note": "1 dumplings are good"}]}
        post_sort = {'APPLE': [{'email': 'APPLE@uchicago.edu'},
                               {'note': 'APPLES ARE GOOD'}],
                     'banana': [{'email': 'banana@uchicago.edu'}],
                     '1Candy': [{'email': '1Candy@uchicago.edu'}],
                     '1dumplings': [{'note': '1 dumplings are good'}],
                     '2Candy': [{'email': '2Candy@uchicago.edu'},
                                {'email': '1_plus_1_Candy@uchicago.edu'}]}
        self.assertEqual(sort_aliases(pre_sort), post_sort)

    # def test_formatting(self):
    #     raw = [
    #         {
    #             "triangle_brackets": [
    #                 "I am triangle",
    #                 "i_am_triangle@uchicago.edu",
    #                 "I am triangle\t \t<i_am_triangle@uchicago.edu>",
    #             ]
    #         },
    #         {
    #             "parentheses": [
    #                 "I am parentheses",
    #                 "i_am_parentheses@uchicago.edu",
    #                 "i_am_parentheses@uchicago.edu (I am parentheses)",
    #             ]
    #         },
    #         {"plain_email": "i_am_plain@uchicago.edu"},
    #         {"local": "i_am_local"},
    #         {"note": "i_am_a_note"},
    #     ]
        
    #     self.assertEqual(
    #         formatting(list_of_options), 
    #         )

