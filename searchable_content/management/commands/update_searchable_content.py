import datetime
import json
import re

import pytz
import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand

from library_website.settings import (
    LIBGUIDES_API_ASSETS_AZ_ENDPOINT,
    LIBGUIDES_API_GUIDES_ENDPOINT,
    LIBGUIDES_API_OAUTH_TOKEN_ENDPOINT,
    LIBGUIDES_CLIENT_ID,
    LIBGUIDES_CLIENT_SECRET,
)
from searchable_content.models import (
    LibGuidesAssetsSearchableContent,
    LibGuidesSearchableContent,
)


def get_guide_body(url):
    """Get the body of a webpage.

    Arguments:
    url

    Returns:
    the webpage body, as a BeautifulSoup object.
    """

    if not url[0:4] == "http":
        url = "http:{}".format(url)

    return BeautifulSoup(requests.get(url).text, "lxml").find("body")


def get_guide_text(url):
    """Get the text of a webpage, omitting HTML tags.

    Arguments:
    url

    Returns:
    the webpage text, as a string.
    """

    html = get_guide_body(url)

    try:
        for h in html.findAll(["form", "nav", "script"]):
            h.extract()
    except AttributeError:
        pass

    try:
        html.find("a", {"id": "s-lg-public-skiplink"}).extract()
    except AttributeError:
        pass

    try:
        for h in html.findAll("div", {"class": "mobile-topnav"}):
            h.extract()
    except AttributeError:
        pass

    try:
        html.find("div", {"id": "s-lib-footer-public"}).extract()
    except AttributeError:
        pass

    try:
        for h in html.findAll("ol", {"class": "breadcrumb"}):
            h.extract()
    except AttributeError:
        pass

    try:
        for h in html.findAll("span", {"class": "sr-only"}):
            h.extract()
    except AttributeError:
        pass

    try:
        html.find("ul", {"id": "navbar-right"}).extract()
    except AttributeError:
        pass

    return html.text


def get_guide_subjects(url):
    """Get the subjects of a given libguide.

    Arguments:
    url

    Returns:
    a list of guide subjects.
    """

    li = get_guide_body(url).find("li", {"id": "s-lg-guide-header-subjects"})

    subjects = []
    try:
        for a in li.findAll("a"):
            subjects.append(a.text)
    except AttributeError:
        pass
    return subjects


def update_libguides_assets():
    """Load the assets from libguides into Wagtail as non-page objects that are
    available to the search index by using the libguides API. If records in
    the libguides API are newer, update records in Wagtail. Delete records
    that don't exist in the libguides API.

    Arguments:
    none

    Returns:
    none
    """

    access_token = json.loads(
        requests.post(
            LIBGUIDES_API_OAUTH_TOKEN_ENDPOINT,
            data={
                "client_id": LIBGUIDES_CLIENT_ID,
                "client_secret": LIBGUIDES_CLIENT_SECRET,
                "grant_type": "client_credentials",
            },
        ).text
    )["access_token"]

    assets = json.loads(
        requests.get(
            LIBGUIDES_API_ASSETS_AZ_ENDPOINT,
            headers={"Authorization": "Bearer " + access_token},
        ).text
    )

    strip_tags = re.compile("<.*?>")

    identifiers = []

    for asset in assets:
        identifier = asset["id"]
        identifiers.append(identifier)

        datestamp = pytz.utc.localize(
            datetime.datetime.strptime(asset["updated"], "%Y-%m-%d %H:%M:%S")
        )

        try:
            if (
                LibGuidesAssetsSearchableContent.objects.get(
                    identifier=identifier
                ).datestamp
                == datestamp
            ):
                # if the asset exists in Wagtail and is newer than or equal to the
                # date already present in the system, continue with the next asset.
                continue
        except:  # noqa: E722
            # if this asset doesn't exist in Wagtail, add it.
            pass

        record_url = asset["url"]
        if record_url == "":
            continue

        try:
            more_info = re.sub(strip_tags, " ", asset["meta"]["more_info"])
        except:  # noqa: E722
            more_info = ""

        try:
            LibGuidesAssetsSearchableContent.objects.update_or_create(
                identifier=identifier,
                title=asset["name"][:255],
                datestamp=datestamp,
                url=record_url,
                description=more_info,
                content="",
            )
        except:  # noqa: E722
            pass

    # delete records that weren't present in the data.
    LibGuidesAssetsSearchableContent.objects.exclude(
        identifier__in=identifiers
    ).delete()


def get_guide_tags(url):
    """Get the tags of a given libguide.

    Arguments:
    url

    Returns:
    a list of guide tags.
    """

    li = get_guide_body(url).find("li", {"id": "s-lg-guide-header-tags"})

    tags = []
    try:
        for a in li.findAll("a"):
            tags.append(a.text)
    except AttributeError:
        pass
    return tags


def update_libguides_guides():
    """Load the guides from libguides into Wagtail as non-page objects that are
    available to the search index by using the libguides API. If records in
    the libguides API are newer, update records in Wagtail. Delete records
    that don't exist in the libguides API.

    Arguments:
    none

    Returns:
    none
    """

    guides = json.loads(requests.get(LIBGUIDES_API_GUIDES_ENDPOINT).text)

    identifiers = []

    for guide in guides:
        status_label = guide["status_label"]
        if status_label != "Published":
            continue

        identifier = guide["id"]
        identifiers.append(identifier)

        datestamp = pytz.utc.localize(
            datetime.datetime.strptime(guide["updated"], "%Y-%m-%d %H:%M:%S")
        )

        try:
            if (
                LibGuidesSearchableContent.objects.get(identifier=identifier).datestamp
                == datestamp
            ):
                # if the guide exists in Wagtail and is newer than or equal to the
                # date already present in the system, continue with the next asset.
                continue
        except:  # noqa: E722
            # if this guide doesn't exist in Wagtail, add it.
            pass

        record_url = guide["url"]
        if record_url == "":
            continue

        content = get_guide_text(record_url)

        try:
            LibGuidesSearchableContent.objects.update_or_create(
                content=content,
                datestamp=datestamp,
                description=guide["description"],
                identifier=identifier,
                subjects=" ".join(get_guide_subjects(record_url)),
                tags=" ".join(get_guide_tags(record_url)),
                title=guide["name"][:255],
                url=record_url,
            )
        except:  # noqa: E722
            pass

    # delete records that weren't present in the data.
    LibGuidesSearchableContent.objects.exclude(identifier__in=identifiers).delete()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--clean", default=False, action="store_true")
        parser.add_argument("--libguides-assets", default=False, action="store_true")
        parser.add_argument("--libguides-guides", default=False, action="store_true")

    def handle(self, *args, **options):
        if not (
            options["clean"]
            or options["libguides_assets"]
            or options["libguides_guides"]
        ):
            print(
                "Usage: python manage.py update_searchable_content [--clean] [--libguides-assets] [--libguides-guides]"
            )
            return
        if options["clean"]:
            LibGuidesSearchableContent.objects.all().delete()
            LibGuidesAssetsSearchableContent.objects.all().delete()
        if options["libguides_assets"]:
            update_libguides_assets()
        if options["libguides_guides"]:
            update_libguides_guides()
