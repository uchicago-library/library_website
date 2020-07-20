import requests
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.test import TestCase

from public.utils import doi_lookup, mk_url

example_doi1 = "10.1007/s11050-007-9022-y"
example_doi2 = "10.1017/S0960129518000324"


class IdresolveTest(SimpleTestCase):

    fixtures = ['test.json']

    def test_idresolve_is_up(self):
        assert doi_lookup(example_doi1) is not None
        assert doi_lookup(example_doi2) is not None

    def test_doi_graceful_fail(self):
        try:
            doi_lookup(example_doi1)
            doi_lookup(example_doi2)
        except requests.ConnectionError:
            self.fail("Idresolve service is not up.")

    def test_doi_good_status_code(self):
        resp1 = requests.get(mk_url(example_doi1))
        resp2 = requests.get(mk_url(example_doi1))
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)

    def test_valid_idresolve_url(self):
        validate = URLValidator()
        result1 = doi_lookup(example_doi1)
        result2 = doi_lookup(example_doi1)
        try:
            validate(result1[:-1])
            validate(result2[:-1])
        except ValidationError:
            self.fail("Idresolve not returning valid SFX url.")
