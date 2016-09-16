import sys
from django.core.management.base import BaseCommand, CommandError
from django.core import management
from django.db.models.base import ObjectDoesNotExist
from units.models import UnitPage
from public.models import LocationPage

class Command(BaseCommand):
    """
    Assigns a LocationPage to multiple UnitPages by matching 
    against a title string. Only a partial string match is 
    required. If a UnitPage title contains part of the string
    a locaation is assigned. Only applies to UnitPages that 
    don't have a location set.

    Args:
        title_fragment: string, part of a UnitPage title.

        location: integer, LocationPage id to assign to all
        UnitPages that are matched.

    Returns:
        None but updates multiple UnitPages.
    """
    help = 'Assigns a LocationPage to multiple UnitPages by matching against part of a title.'

    def add_arguments(self, parser):
        """
        Add required positional options and optional
        named arguments.
        """
        # Required positional options
        parser.add_argument('title_fragment', nargs='+', type=str)
        parser.add_argument('location', nargs='+', type=int)

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this
        method. It may return a Unicode string which will be printed to
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """
        kwargs = { 'title_fragment': options['title_fragment'][0],
                   'location': options['location'][0] }

        try:
            units = UnitPage.objects.all().filter(location=None)
            matched_units = units.filter(title__contains=kwargs['title_fragment'])
            count = str(matched_units.count())

            location_name = LocationPage.objects.get(id=kwargs['location']).title

            for unit in matched_units:
                management.call_command('assign_unit_location', str(unit.id), str(kwargs['location']))
            self.stdout.write(count + ' UnitPages were assigned a location of ' + location_name)
        except ObjectDoesNotExist:
            self.stdout.write('Something went wrong')
            sys.exit(1)

