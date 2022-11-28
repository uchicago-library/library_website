from django.core.management.base import BaseCommand
from wagtail.models import Site


class Command(BaseCommand):
    """
    Updates data for a site with a given hostname.

    Required args:
        hostname: string, current hostname of the Wagtail
        site object to be updated

    Optional args:
        new_host: string, a new and different hostname for
        the site

    Returns:
        None, saves an updated version of the Wagtail site
        object with the given input parameters
    """
    help = 'Updates a Wagtail site object with the given arguments. \
            Can be used to change the hostname of a site.'

    def add_arguments(self, parser):
        """
        Add required positional options and optional
        named arguments.
        """
        # Required positional options
        parser.add_argument('hostname', nargs='+', type=str)

        # Optional named arguments
        parser.add_argument(
            '-nh',
            '--new_host',
            action='store',
            nargs=1,
            help='Change the site hostname.'
        )

        parser.add_argument(
            '-p',
            '--port',
            action='store',
            nargs=1,
            help='Change the site port.'
        )

    def handle(self, *args, **options):
        """
        Meat of the command.
        """
        # Required args
        current_host = options['hostname'][0]

        # Optional args
        new_host = options['new_host'][0] if options['new_host'] else None
        new_port = options['port'][0] if options['port'] else None

        site_obj = Site.objects.get(hostname=current_host)

        if new_host:
            site_obj.hostname = new_host

        if new_port:
            if not new_port.isdigit():
                raise ValueError('The new port must be numeric')
            site_obj.port = new_port

        site_obj.save()
