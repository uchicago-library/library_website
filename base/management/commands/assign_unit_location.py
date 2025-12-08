import sys

from django.core.management.base import BaseCommand
from django.db.models.base import ObjectDoesNotExist

from public.models import LocationPage
from units.models import UnitPage


class Command(BaseCommand):
    """
    Assigns a LocationPage to a UnitPage location field. This is used
    to update a singular UnitPage by assigning it a location.

    Args:
        unit: integer, UnitPage id.

        location: integer, LocationPage id.

    Returns:
        None but saves an updated version of the unit page.
    """

    help = "Assigns a LocationPage to a UnitPage location field for one page"

    def add_arguments(self, parser):
        """
        Add required positional options and optional
        named arguments.
        """
        # Required positional options
        parser.add_argument("unit", nargs="+", type=int)
        parser.add_argument("location", nargs="+", type=int)

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this
        method. It may return a Unicode string which will be printed to
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """
        kwargs = {"unit": options["unit"][0], "location": options["location"][0]}

        try:
            unitpage = UnitPage.objects.all().get(id=kwargs["unit"])
            locationpage = LocationPage.objects.all().get(id=kwargs["location"])
            unitpage.location = locationpage
            unitpage.save()
        except ObjectDoesNotExist:
            self.stdout.write(
                "Either the the UnitPage or LocationPage provided does not exist"
            )
            sys.exit(1)
