import sys
from django.core.management.base import BaseCommand, CommandError
from django.db.models.base import ObjectDoesNotExist
from django.contrib.auth.models import User
from ._load_initial_staff_data import get_all_library_cnetids, get_individual_info
from django.core import management
from io import StringIO
import ast

class Command(BaseCommand):
    """
    Create or update all library users in the auth_user table based
    on the findings in the uchicago directory feed.
    """

    def add_arguments(self, parser):
        """
        Add required positional options and optional
        named arguments.
        """
        # Required positional options
        #parser.add_argument('test', nargs='+', type=str)

    def handle(self, *args, **options):
        
        self.stdout.write('Importing user list...' )
        cnetids = get_all_library_cnetids()
        self.stdout.write('Adding new and updating existing user accounts...' )

        new_users = set([])
        updated_users = set([])

        for cnetid in cnetids:
            info = get_individual_info(cnetid)
            name_list = info['displayName'].split()
            try:
                if len(name_list) > 2:
                    first_name = name_list[0]
                    last_name = name_list[2]
                else:
                    first_name = name_list[0]
                    last_name = name_list[1]
            except:
                first_name = ''
                last_name = ''

            string = StringIO()
            management.call_command('create_library_user', cnetid, first_name, last_name, info['email'], 'False', is_active='True', stdout=string)
            temp = ast.literal_eval(string.getvalue())
            if temp[0] == 0:
                updated_users.add(temp[1])
            elif temp[0] == 1:
                new_users.add(temp[1])
            string.close()

        return self._format_output(new_users, updated_users)


    def _fast_concat(self, users):
        """
        Use a generator to concatonate users quickly.

        Args:
            users: set of cnetid strings.
        """
        for user in users:
            yield user + '\n'
            

    def _format_output(self, new_users, existing_users):
        """
        Format output for stdout and print a report
        on user accounts that were created and updated 
        in the system.

        Args:
            new_users: set of cnetid strings
            
            existing_users: set of cnetid strings

        Returns:
            string
        """

        pretty_bar = '\n------------------------------------------------------'

        new_user_string = 'The following new users were created in the system:%s \n' % pretty_bar
        existing_user_string = 'The following existing user accounts were updated:%s \n' % pretty_bar
        outlier_user_string = 'The following users are renegades in the system:%s \n' % pretty_bar

        new_user_string += ''.join(self._fast_concat(new_users))
        existing_user_string += ''.join(self._fast_concat(existing_users))
        outlier_user_string += ''.join(self._fast_concat(self.get_outlier_users()))
        
        return '\n' + existing_user_string + '\n' + new_user_string + '\n' + outlier_user_string + '\n'


    def get_outlier_users(self, cnetids=set([])):
        """
        Gets all the users in the system that aren't in the 
        sanctioned list of cnetids.

        Args: 
            cnetids: optional, set of cnet ids. If this argument
            is not provided, the directory api will be queried.

        Returns:
            set of usernames who aren't in the sanctioned list
            of cnetids. 
        """
        if cnetids == set([]):
            cnetids = cnetids = get_all_library_cnetids()

        current_users_in_db = self.get_all_usernames_as_set()

        return current_users_in_db.difference(cnetids)


    def get_all_usernames_as_set(self):
        """
        Get all of the usernames in the system.

        Returns:
            set of usernames found in the database.
        """
        users = User.objects.all()
        retval = set([])
        for user in users:
            retval.add(user.username)
        return retval
