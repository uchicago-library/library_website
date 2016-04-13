# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from staff.models import StaffPage
from units.models import UnitPage

class Command (BaseCommand):
    """
    Update the alphabetical directory names: e.g.
    Administration, D'Angelo Law Library.

    Example: 
        python manage.py update_alphabetical_directory_names
    """

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this 
        method. It may return a Unicode string which will be printed to 
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        output = []

        data = (
            ("Administration", "Administration"),
            ("Adminstrative Services", "Adminstrative Services"),
            ("Collection Services", "Collection Services"),
            ("Collection Services - Administration", "Administration, Collection Services"),
            ("Collection Services - Preservation - Binding & Shelf Preparations", "Binding & Shelf Preparations"),
            ("Collection Services - Preservation - Conservation", "Conservation"),
            ("Collection Services - Preservation - Digitization", "Digitization"),
            ("Collection Services - Technical Services - Acquisitions & Rapid Cataloging", "Acquisitions & Rapid Cataloging"),
            ("Collection Services - Technical Services - Continuing Resources Orders & Cataloging", "Continuing Resources Orders & Cataloging"),
            ("Collection Services - Technical Services - Data Management Services", "Data Management Services"),
            ("Collection Services - Technical Services - Monographic Cataloging", "Monographic Cataloging"),
            ("D'Angelo Law Library - Administration", "Administration, D'Angelo Law Library"),
            ("D'Angelo Law Library - Law Technical Services", "Law Technical Services, D'Angelo Law Library"),
            ("D'Angelo Law Library - Law User Services", "Law User Services, D'Angelo Law Library"),
            ("D'Angelo Law Library - Law User Services - Access Services", "Access Services, D'Angelo Law Library"),
            ("D'Angelo Law Library - Law User Services - Reference", "Reference, D'Angelo Law Library"),
            ("Digital Services - Administration", "Administration, Digital Services"),
            ("Digital Services - eCUIP", "eCUIP"),
            ("Digital Services - Digital Library Development Center (DLDC)", "Digital Library Development Center (DLDC)"),
            ("Science Libraries - Administration", "Administration, Science Libraries"),
            ("Science Libraries - Astronomy and Astrophysics", "Astronomy and Astrophysics"),
            ("Science Libraries - Biochemistry and Molecular Biology", "Biochemistry and Molecular Biology"),
            ("Science Libraries - Chemistry", "Chemistry"),
            ("Science Libraries - Computer Science", "Computer Science"),
            ("Science Libraries - Crerar Library Access Services", "Crerar Library Access Services, Science Libraries"),
            ("Science Libraries - Ecology and Evolution", "Ecology and Evolution"),
            ("Science Libraries - Geophysical Sciences", "Geophysical Sciences"),
            ("Science Libraries - Human Genetics", "Human Genetics"),
            ("Science Libraries - Mathematics", "Mathematics"),
            ("Science Libraries - Medicine", "Medicine"),
            ("Science Libraries - Microbiology", "Microbiology"),
            ("Science Libraries - Molecular Genetics and Cell Biology", "Molecular Genetics and Cell Biology"),
            ("Science Libraries - Neurobiology", "Neurobiology"),
            ("Science Libraries - Nursing", "Nursing"),
            ("Science Libraries - Organismal Biology and Anatomy", "Organismal Biology and Anatomy"),
            ("Science Libraries - Pharmacological and Physiological Sciences", "Pharmacological and Physiological Sciences"),
            ("Science Libraries - Physics", "Physics"),
            ("Science Libraries - Science Technical Services", "Science Technical Services, Science Libraries"),
            ("Science Libraries - Science and Medicine, History of", "Science and Medicine, History of"),
            ("Science Libraries - Statistics", "Statistics"),
            ("Science Libraries - Technology", "Technology"),
            ("Special Collections Research Center - SCRC Administration", "SCRC Administration, Special Collections Research Center"),
            ("Special Collections Research Center - SCRC Archives and Manuscripts", "SCRC Archives and Manuscripts, Special Collections Research Center"),
            ("Special Collections Research Center - SCRC Collection Management", "SCRC Collection Management, Special Collections Research Center"),
            ("Special Collections Research Center - SCRC Exhibits", "SCRC Exhibits, Special Collections Research Center"),
            ("Special Collections Research Center - SCRC Rare Books", "SCRC Rare Books, Special Collections Research Center"),
            ("Special Collections Research Center - SCRC Reader Services", "SCRC Reader Services, Special Collections Research Center"),
            ("User Services - Access Services - Mansueto", "Mansueto"),
            ("User Services - Access Services - Assessment", "Assessment"),
            ("User Services - Administration", "Administration, User Services"),
            ("User Services - Collection Management and Special Projects", "Collection Management and Special Projects"),
            ("User Services - Collection Management and Special Projects - Library Special Projects", "Library Special Projects"),
            ("User Services - Collection Management and Special Projects - Regenstein Bookstacks", "Regenstein Bookstacks"),
            ("User Services - Collection Management and Special Projects - Regenstein Reading Rooms", "Regenstein Reading Rooms"),
            ("User Services - Collection Management and Special Projects - Regenstein Search Services", "Regenstein Search Services"),
            ("Collection Services - Administrative and Desktop Systems (ADS)", "Administrative and Desktop Systems (ADS)"),
            ("Adminstrative Services - Budget", "Budget"),
            ("Adminstrative Services - Building Services", "Building Services"),
            ("Collection Services - Collections Support - Gifts", "Gifts"),
            ("Collection Services - Collections Support - Payments", "Payments"),
            ("Collection Services - Collections Support - Vendor Relations", "Vendor Relations"),
            ("Administration - Communications", "Communications"),
            ("D'Angelo Law Library - Administration", "Administration, D'Angelo Law Library"),
            ("D'Angelo Law Library - Acquisitions", "Acquisitions, D'Angelo Law Library"),
            ("D'Angelo Law Library - Cataloging", "Cataloging, D'Angelo Law Library"),
            ("D'Angelo Law Library - Circulation", "Circulation, D'Angelo Law Library"),
            ("D'Angelo Law Library - Documents", "Documents, D'Angelo Law Library"),
            ("D'Angelo Law Library - Foreign and International Law", "Foreign and International Law, D'Angelo Law Library"),
            ("D'Angelo Law Library - Processing", "Processing, D'Angelo Law Library"),
            ("D'Angelo Law Library - Recording", "Recording, D'Angelo Law Library"),
            ("D'Angelo Law Library - Reference", "Reference, D'Angelo Law Library"),
            ("D'Angelo Law Library - Technical Services", "Technical Services, D'Angelo Law Library"),
            ("Administration - Development", "Development, Administration"),
            ("Digital Services", "Digital Services"),
            ("Administration - Director's Office", "Director's Office"),
            ("User Services - Dissertation Office", "Dissertation Office"),
            ("User Services - Access Services - Document Delivery", "Document Delivery"),
            ("User Services - Access Services - Document Delivery - Borrowing Orders", "Borrowing Orders, Document Delivery"),
            ("User Services - Access Services - Document Delivery - Lending Orders", "Lending Orders, Document Delivery"),
            ("Science Libraries - Eckhart Library", "Eckhart Library"),
            ("Collection Services - Electronic Resources Management (ERM)", "Electronic Resources Management (ERM)"),
            ("Adminstrative Services - Human Resources", "Human Resources"),
            ("User Services - Access Services - ID & Privileges Office & Entry Control", "ID & Privileges Office & Entry Control"),
            ("Collection Services - Integrated Library Systems (ILS)", "Integrated Library Systems (ILS)"),
            ("Library - Regenstein Library", "Regenstein Library"),
            ("Library - Circulation", "Circulation"),
            ("Library - Claims", "Claims"),
            ("Library - Entry Control", "Entry Control"),
            ("Library - Microforms", "Microforms"),
            ("Library - Music", "Music"),
            ("Library - Periodicals", "Periodicals"),
            ("Library - Privileges", "Privileges"),
            ("Library - Recalls", "Recalls"),
            ("Library - Reference", "Reference"),
            ("Library - Search Services", "Search Services"),
            ("Collection Services - Preservation - Administration", "Administration, Preservation"),
            ("Collection Services - Preservation - Conservation", "Conservation"),
            ("Collection Services - Preservation - Digitization", "Digitization"),
            ("User Services - Reference, Instruction, and Outreach - Ask a Librarian", "Ask a Librarian"),
            ("Science Libraries - Administration", "Administration, Science Libraries"),
            ("Science Libraries - Circulation", "Circulation, Science Libraries"),
            ("Science Libraries - Computer Search Service", "Computer Search Service, Science Libraries"),
            ("Science Libraries - Course Reserves", "Course Reserves, Science Libraries"),
            ("Science Libraries - Reference", "Reference, Science Libraries"),
            ("Science Libraries - Reference Workroom", "Reference Workroom, Science Libraries"),
            ("Science Libraries - Stacks, Searches, and Recalls", "Stacks, Searches, and Recalls, Science Libraries"),
            ("Science Libraries - Technical Processing", "Technical Processing, Science Libraries"),
            ("Adminstrative Services - Shipping and Receiving", "Shipping and Receiving"),
            ("Area Studies, Humanities, and Social Sciences - Social Service Administration Library (SSA)", "Social Service Administration Library (SSA)"),
            ("Special Collections Research Center", "Special Collections Research Center"),
            ("Special Collections Research Center - Digital Projects", "Digital Projects, Special Collections Research Center"),
            ("Special Collections Research Center - Preservation", "Preservation, Special Collections Research Center"),
            ("Collection Services - Technical Services - Administration", "Administration, Technical Services"),
            ("Collection Services - Technical Services - Continuing Resources Cataloging", "Continuing Resources Cataloging"),
            ("Collection Services - Technical Services - Continuing Resources Orders", "Continuing Resources Orders"),
            ("Collection Services - Technical Services - Data Management Services", "Data Management Services"),
            ("Collection Services - Technical Services - Monographic Cataloging", "Monographic Cataloging"),
            ("Collection Services - Technical Services - Monographic Orders", "Monographic Orders"),
            ("Collection Services - Technical Services - Piece Processing", "Piece Processing"),
            ("Collection Services - Technical Services - Receiving (line 1)", "Receiving (line 1), Technical Services"),
            ("Collection Services - Technical Services - Receiving (line 2)", "Receiving (line 2), Technical Services"),
            ("Science Libraries - Crerar Reference Desk", "Crerar Reference Desk, Science Libraries"),
            ("Library - Ex Libris Cafe", "Ex Libris Cafe"),
            ("Library", "Library"),
            ("Special Collections Research Center", "Special Collections Research Center"),
            ("Area Studies, Humanities, and Social Sciences - Map Collection", "Map Collection"),
            ("Science Libraries", "Science Libraries"),
            ("User Services - Reference, Instruction, and Outreach", "Reference, Instruction, and Outreach")
        )

        jej = StaffPage.objects.get(cnetid='jej')

        units_updated = 0
        for d in data:
            u = UnitPage.objects.get(title = d[0])
            if not u.alphabetical_directory_name == d[1]:
                u.alphabetical_directory_name = d[1]
                if not u.page_maintainer:
                    u.page_maintainer = jej
                if not u.editor:
                    u.editor = jej
                u.save()
                units_updated = units_updated + 1

        output.append(str(units_updated) + " units updated.")

        return "\n".join(output)
    


