from django.core.management.base import BaseCommand
from lib_collections.models import ExhibitPage, ExhibitPageStaffContacts


class Command(BaseCommand):
    """
    Migrate existing single staff_contact values to the new repeatable
    exhibit_page_staff_contacts field.

    This command finds all ExhibitPage instances with a staff_contact value
    and creates corresponding ExhibitPageStaffContacts entries.

    Args:
        None

    Returns:
        None, but creates ExhibitPageStaffContacts entries and prints progress.
    """

    help = 'Migrate existing staff_contact data to repeatable staff_contacts field'

    def handle(self, *args, **options):
        """
        The actual logic of the command.
        """
        # Find all ExhibitPages with a staff_contact
        exhibits_with_staff = ExhibitPage.objects.filter(
            staff_contact__isnull=False
        ).select_related('staff_contact')

        total_count = exhibits_with_staff.count()
        migrated_count = 0
        skipped_count = 0

        self.stdout.write(f'Found {total_count} exhibits with staff contacts to migrate.')

        for exhibit in exhibits_with_staff:
            # Check if this staff contact is already in the repeatable field
            existing = ExhibitPageStaffContacts.objects.filter(
                page=exhibit, staff=exhibit.staff_contact
            ).exists()

            if existing:
                self.stdout.write(
                    self.style.WARNING(
                        f'Skipping "{exhibit.title}" - staff contact already exists '
                        f'in repeatable field'
                    )
                )
                skipped_count += 1
                continue

            # Create the new staff contact entry
            ExhibitPageStaffContacts.objects.create(
                page=exhibit, staff=exhibit.staff_contact
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Migrated staff contact for "{exhibit.title}" -> '
                    f'"{exhibit.staff_contact.title}"'
                )
            )
            migrated_count += 1

        # Print summary
        self.stdout.write(self.style.SUCCESS('\n=== Migration Summary ==='))
        self.stdout.write(f'Total exhibits with staff contacts: {total_count}')
        self.stdout.write(self.style.SUCCESS(f'Successfully migrated: {migrated_count}'))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f'Skipped (already exists): {skipped_count}'))
        self.stdout.write(
            self.style.SUCCESS(
                '\nMigration complete! You can now update templates and code to use '
                'the new exhibit_page_staff_contacts field.'
            )
        )
