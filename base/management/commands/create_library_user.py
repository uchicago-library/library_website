import sys

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.db.models.base import ObjectDoesNotExist


class Command(BaseCommand):
    """
    Create a new user in the auth_user table if the user doesn't already exist
    or update the user's information if the user already exists. Maske sure
    all users are assigned to the proper groups.

    Example:
        python manage.py create_library_user 'elmerfud' 'Elmer' 'Fud' 'efud@loonytoons.com' False -ia=False
    """

    help = "Create a user in the auth_user table."

    REQUIRED_GROUP_NAMES = {1: "Library", 2: "Editors"}

    # Exception table for non-standard names.
    # Should be removed when first_name and
    # last_name are returned in the directory feed
    PROTECTED_NAMES = {"nelson3": {0: "Tonya", 1: "Mullins-Nelson"}}

    def add_arguments(self, parser):
        """
        Add required positional options and optional
        named arguments.
        """
        # Required positional options
        parser.add_argument("username", nargs="+", type=str)
        parser.add_argument("first_name", nargs="+", type=str)
        parser.add_argument("last_name", nargs="+", type=str)
        parser.add_argument("email", nargs="+", type=str)
        parser.add_argument("is_staff", nargs="+", type=bool)

        # Optional named arguments
        parser.add_argument(
            "-ia",
            "--is_active",
            action="store",
            nargs=1,
            help="Set whether or not a user should be active in the system.",
        )

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this
        method. It may return a Unicode string which will be printed to
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        # Convenience variables for required fields.
        # Save in a dict so we can pass an unspecified
        # numer or arguments to the get_or_create method.
        try:
            kwargs = {
                "username": options["username"][0],
                "first_name": options["first_name"][0],
                "last_name": options["last_name"][0],
                "email": options["email"][0],
                "is_staff": options["is_staff"][0],
            }
        except:  # noqa: E722
            sys.exit(1)

        # Fix non-standard names in the execption table
        if kwargs["username"] in self.PROTECTED_NAMES:
            kwargs["first_name"] = self.PROTECTED_NAMES[kwargs["username"]][0]
            kwargs["last_name"] = self.PROTECTED_NAMES[kwargs["username"]][1]

        # Get required groups all Library fulltime staff
        # must belong to both of these groups.
        try:
            library_group = Group.objects.get(name=self.REQUIRED_GROUP_NAMES[1])
            editors_group = Group.objects.get(name=self.REQUIRED_GROUP_NAMES[2])
        except ObjectDoesNotExist:
            self.stdout.write(
                'Either the "%s" or "%s" group doesn\'t exist.'
                % (self.REQUIRED_GROUP_NAMES[1], self.REQUIRED_GROUP_NAMES[2])
            )
            self.stdout.write(
                "Make sure both of these groups have been created and try running the command again."
            )
            sys.exit(1)

        # Convenience variables for optional fields
        try:
            # Weirdness requires this ternary operator
            # because for some reason booleans are passed
            # through differently when run from the
            # commandline vs. in code.
            kwargs["is_active"] = (
                True
                if options["is_active"][0] == "True" or options["is_active"][0] == "T"
                else False
            )
        except:  # noqa: E722
            pass

        # See if the user is already in the system.
        # Update the user if he or she is already in the system.
        try:
            # Required fields
            user = User.objects.get(username=kwargs["username"])
            user.first_name = kwargs["first_name"]
            user.last_name = kwargs["last_name"]
            user.email = kwargs["email"]

            # Optional fields
            try:
                user.is_active = kwargs["is_active"]
            except:  # noqa: E722
                pass

            user.save()

            # Add the user to the proper groups
            if not user.groups.filter(name=self.REQUIRED_GROUP_NAMES[1]).exists():
                library_group.user_set.add(user)
            if not user.groups.filter(name=self.REQUIRED_GROUP_NAMES[2]).exists():
                editors_group.user_set.add(user)
            retval = '(0, "%s")' % kwargs["username"]

        # Create the user if he or she didn't exist.
        except:  # noqa: E722
            user = User.objects.create(**kwargs)
            library_group.user_set.add(user)
            editors_group.user_set.add(user)
            retval = '(1, "%s")' % kwargs["username"]

        return retval
