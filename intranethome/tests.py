from base.result import is_ok, is_error
from django.test import SimpleTestCase
from .views import comparison, convert_list_to_dict, parse_file, sort_aliases
from .ags import (xlsx_to_df,
                  validate_xlsx,
                  validate_dataframe,
                  diff_rows,
                  pad_with_empties)


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


with open("intranethome/test_data/export.xlsx", "rb") as f:
    good_xlsx = f.read()


with open("intranethome/test_data/export_bad_sheet_name.xlsx", "rb") as f:
    bad_sheet_name_xlsx = f.read()


with open("intranethome/test_data/export_bad_yearend_field.xlsx", "rb") as f:
    bad_column_field_xlsx = f.read()


rows1 = [["", "abc"], ["", "def"]]
rows2 = [["", "def"], ["", "ghi"]]


class test_ags_upload(SimpleTestCase):


    def test_good_xlsx_reads(self):
        df = xlsx_to_df(good_xlsx)
        self.assertTrue(is_ok(df))


    def test_bad_sheet_name_fails(self):
        df = xlsx_to_df(bad_sheet_name_xlsx)
        self.assertTrue(is_error(df))


    def test_bad_column_name_xlsx_reads(self):
        df = xlsx_to_df(bad_column_field_xlsx)
        self.assertTrue(is_ok(df))


    def test_bad_column_name_validate_df_fails(self):
        df = xlsx_to_df(bad_column_field_xlsx)
        validated = validate_dataframe(df)
        self.assertTrue(is_error(validated))


    def test_bad_column_validate_xlsx_fails(self):
        xlsx_result = validate_xlsx(bad_column_field_xlsx)
        self.assertTrue(is_error(xlsx_result))


    def test_diff_rows_one_diff(self):
        expected = (1,
                    1,
                    [('', '', ['', 'def']),
                     ('-', 'background-color:  #fce6e9;', ['', 'abc']),
                     ('+', 'background-color:  #e4f7ea;', ['', 'ghi'])])
        self.assertEqual(diff_rows(rows1, rows2), expected)


    def test_diff_rows_no_diffs(self):
        expected = (0, 0, [('', '', ['', 'def']), ('', '', ['', 'ghi'])])
        self.assertEqual(diff_rows(rows2, rows2), expected)


    def test_diff_rows_empties(self):
        self.assertEqual(diff_rows([],[]), (0,0,[]))

    
    def test_pad_with_empties(self):
        lst = [1,2,3]
        expected = [('', 'table-active', 1),
                    ('', 'table-active', 2),
                    ('', 'table-active', 3)]
        self.assertEqual(pad_with_empties(lst), expected)
