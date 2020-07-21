import requests
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.test import TestCase, SimpleTestCase

from library_website.settings import IDRESOLVE_URL
from public.utils import doi_lookup, doi_lookup_base_url, mk_url

example_doi1 = "10.1007/s11050-007-9022-y"
example_doi2 = "10.1017/S0960129518000324"
bad_url = "https://not-an-actual-api-I-just-made-it-up.com?"
bad_doi = "NOT_A_DOI"


class IdresolveTest(SimpleTestCase):

    fixtures = ['test.json']

    def test_idresolve_is_up(self):
        """
        check that idresolve returns a response when given a valid DOI and
        base URL

        """
        assert doi_lookup(example_doi1) is not None
        assert doi_lookup(example_doi2) is not None

    def test_good_url_no_exception(self):
        """
        ensure no exception gets thrown when trying to connect to
        idresolve at the correct URL

        """
        try:
            doi_lookup(example_doi1)
            doi_lookup(example_doi2)
        except requests.ConnectionError:
            self.fail("Idresolve service is not up.")

    def test_bad_url_no_exception(self):
        """
        ensure no exception gets thrown when trying to connect to
        idresolve at the wrong URL
        """
        try:
            doi_lookup_base_url(example_doi1, bad_url)
            doi_lookup_base_url(example_doi2, bad_url)
        except requests.ConnectionError as exception:
            self.fail("public.utils doi_lookup raised %s"
                      % str(exception)
                      )

    def test_bad_doi_returns_none(self):
        """
        ensure a request to idresolve with an ill-formed DOI fails
        gracefully (i.e. returns None)

        """
        resp = doi_lookup_base_url(bad_doi, IDRESOLVE_URL)
        assert resp is None

    def test_doi_good_status_code(self):
        """
        check that a good URL and DOI return a response with a 200 status
        code

        """
        resp1 = requests.get(mk_url(example_doi1, IDRESOLVE_URL))
        resp2 = requests.get(mk_url(example_doi2, IDRESOLVE_URL))
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)

    def test_valid_idresolve_url(self):
        """
        check that idresolve returned a well-formed URL that the Wagtail
        app can perform a redirect to

        """
        validate = URLValidator()
        result1 = doi_lookup(example_doi1)
        result2 = doi_lookup(example_doi1)
        try:
            validate(result1[:-1])
            validate(result2[:-1])
        except ValidationError:
            self.fail("Idresolve not returning valid SFX url.")
