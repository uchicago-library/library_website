from django.test import SimpleTestCase

from .views import (
    comparison,
    convert_list_to_dict,
    parse_file,
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
        pre_sort = {
            "banana": [{"email": "banana@uchicago.edu"}],
            "APPLE": [{"email": "APPLE@uchicago.edu"}, {"note": "APPLES ARE GOOD"}],
            "1Candy": [{"email": "1Candy@uchicago.edu"}],
            "2Candy": [
                {"email": "2Candy@uchicago.edu"},
                {"email": "1_plus_1_Candy@uchicago.edu"},
            ],
            "1dumplings": [{"note": "1 dumplings are good"}],
        }
        post_sort = {
            "APPLE": [{"email": "APPLE@uchicago.edu"}, {"note": "APPLES ARE GOOD"}],
            "banana": [{"email": "banana@uchicago.edu"}],
            "1Candy": [{"email": "1Candy@uchicago.edu"}],
            "1dumplings": [{"note": "1 dumplings are good"}],
            "2Candy": [
                {"email": "2Candy@uchicago.edu"},
                {"email": "1_plus_1_Candy@uchicago.edu"},
            ],
        }
        self.assertEqual(sort_aliases(pre_sort), post_sort)

    def test_convert(self):

        raw = [
            {
                "plain_email": [
                    {"email": "i_am_plain@lib.uchicago.edu"},
                ]
            },
            {
                "triangle_brackets": [
                    {"email": "One-Tab Triangle\t<onetab@uchicago.edu>"},
                    {"email": "Two-Tab Triangle\t\t<twotab@uchicago.edu>"},
                ]
            },
            {"parentheses": [{"email": "parens@uchicago.edu (I Am Parentheses)"}]},
            {"local": [{"email": "catforum"}]},
            {"note": [{"note": "it's a note with emails@in.it for testing"}]},
            {
                "mixed": [
                    {"email": "parens@uchicago.edu (Surprise Parens!) "},
                    {"email": "surprise_plain@lib.uchicago.edu"},
                ]
            },
        ]

        expected = {
            "local": [{"local": "catforum"}],
            "mixed": [
                {
                    "parentheses": [
                        "Surprise Parens!",
                        "parens@uchicago.edu",
                        "parens@uchicago.edu (Surprise Parens!)",
                    ]
                },
                {"plain_email": "surprise_plain@lib.uchicago.edu"},
            ],
            "note": [{"note": "note: it's a note with emails@in.it for testing"}],
            "parentheses": [
                {
                    "parentheses": [
                        "I Am Parentheses",
                        "parens@uchicago.edu",
                        "parens@uchicago.edu (I Am Parentheses)",
                    ]
                }
            ],
            "plain_email": [{"plain_email": "i_am_plain@lib.uchicago.edu"}],
            "triangle_brackets": [
                {
                    "triangle_brackets": [
                        "One-Tab Triangle",
                        "onetab@uchicago.edu",
                        "One-Tab Triangle\t<onetab@uchicago.edu>",
                    ]
                },
                {
                    "triangle_brackets": [
                        "Two-Tab Triangle",
                        "twotab@uchicago.edu",
                        "Two-Tab Triangle\t\t<twotab@uchicago.edu>",
                    ]
                },
            ],
        }

        expected_p = {
            "parentheses": [
                {
                    "parentheses": [
                        "I Am Parentheses",
                        "parens@uchicago.edu",
                        "parens@uchicago.edu (I Am Parentheses)",
                    ]
                }
            ],
            "plain_email": [{"plain_email": "i_am_plain@lib.uchicago.edu"}],
        }

        expected_P = expected_p

        expected_l = {"local": [{"local": "catforum"}]}

        expected_L = expected_l

        self.assertEqual(convert_list_to_dict(raw), expected)
        self.assertEqual(convert_list_to_dict(raw, filt="p"), expected_p)
        self.assertEqual(convert_list_to_dict(raw, filt="P"), expected_P)
        self.assertEqual(convert_list_to_dict(raw, filt="l"), expected_l)
        self.assertEqual(convert_list_to_dict(raw, filt="L"), expected_L)
        self.assertEqual(convert_list_to_dict(raw, filt="*"), expected)
        self.assertEqual(convert_list_to_dict(raw, filt=""), expected)

    def test_bad_filepath(self):
        bad_json = parse_file("this_doesnt_exist.json")

        def is_error(js):
            try:
                _ = js["error"]
                return True
            except KeyError:
                return False

        self.assertTrue(is_error(bad_json))
