from django.test import SimpleTestCase

from intranethome.views import (
    format_splitting,
    reading_and_converting,
    uniforming_into_list_of_dict,
)


class test_mail_aliases_view(SimpleTestCase):
    def test_uniforming_into_list_of_dict(self):
        option1 = {"email": "email@email.uchicago.edu"}
        option2 = [
            {"email": "localemail"},
            {"email": "globalemail@uchicago.edu"},
            {"email": "anotheremail@uchicago.edu"},
        ]
        option3 = {"note": "take notes"}
        self.assertEqual(uniforming_into_list_of_dict(option1), [option1])
        self.assertEqual(uniforming_into_list_of_dict(option2), option2)
        self.assertEqual(uniforming_into_list_of_dict(option3), [option3])

    def test_format_splitting(self):
        option1_triangle_brackets = "I am triangle\t \t<i_am_triangle@uchicago.edu>"
        option2_parentheses = "i_am_parentheses@uchicago.edu (I am parentheses)"
        option3_plain_email = "i_am_plain@uchicago.edu"
        option4_local = "i_am_local"
        option5_distro = "i_am_distro-6052"
        self.assertEqual(
            format_splitting(option1_triangle_brackets),
            {
                "triangle_brackets": [
                    "I am triangle",
                    "i_am_triangle@uchicago.edu",
                    option1_triangle_brackets,
                ]
            },
        )
        self.assertEqual(
            format_splitting(option2_parentheses),
            {
                "parentheses": [
                    "I am parentheses",
                    "i_am_parentheses@uchicago.edu",
                    option2_parentheses,
                ]
            },
        )
        self.assertEqual(
            format_splitting(option3_plain_email), {"plain_email": option3_plain_email}
        )
        self.assertEqual(format_splitting(option4_local), {"local": option4_local})
        self.assertEqual(format_splitting(option5_distro), -1)

    def test_reading_and_converting_error_case(self):
        incorrect_file_url = "/intranethome/alias.json"
        self.assertEqual(reading_and_converting(incorrect_file_url), {"error": "error"})
