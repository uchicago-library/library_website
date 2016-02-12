from django.db import models
from django.db.models import Q

from staff.models import StaffPage

# Create your models here.
class DirectoryUnit(models.Model):
    # e.g. Administration
    name = models.CharField(max_length=255)

    # e.g. D'Angelo Law Library - Administration. for pulldowns, etc.
    fullName = models.CharField(max_length=1020, default='')

    # by default, deletes will cascade and remove children. 
    parentUnit = models.ForeignKey('DirectoryUnit', null=True)

    # the source of this data in the directory api. 
    xmlUrl = models.CharField(max_length=255)

    def __str__(self):
        return self.fullName

    def get_parent_library_name(self):
        special_names = {
            'Science Libraries': 'Crerar Library',
            'Mansueto': 'Mansueto Library'
        }

        ancestors = self.get_ancestors(True)
        while True:
            if not ancestors:
                return 'Regenstein Library'

            ancestor = ancestors.pop(0)
            if ancestor.name in ['Science Libraries', 'D\'Angelo Law Library', 'Eckhart Library', 'Social Service Administration Library (SSA)', 'Special Collections Research Center', 'Mansueto', 'Mansueto Library']:
                if ancestor.name in special_names:
                    return special_names[ancestor.name]
                else:
                    return ancestor.name

    def get_descendants(self, include_self = False):
        need_to_check = [self]
        checked = []
        descendants = []

        while True: 
            if not need_to_check:
                break

            current_unit = need_to_check.pop()
            for child in DirectoryUnit.objects.filter(parentUnit=current_unit):
                if not child in descendants:
                    descendants.append(child)
                if not child in checked and not child in need_to_check:
                    need_to_check.append(child)
            checked.append(current_unit)

        if include_self:
            descendants.append(self)

        return descendants

    def get_ancestors(self, include_self = False):
        ancestors = []

        if include_self:
            current_unit = self
        else:
            current_unit = self.parentUnit

        while True:
            if not current_unit:
                break
            ancestors.append(current_unit)
            current_unit = current_unit.parentUnit

        return ancestors
    
    class Meta:
        ordering = ['fullName']
   
class UnitSupervisor(models.Model): 
    # when a unit is deleted, columns in this table that refer to it are automatically deleted as well.
    unit = models.ForeignKey('DirectoryUnit', null=True, on_delete=models.CASCADE)

    # when a supervisor is removed from the system, leave the row in this table. 
    supervisor = models.ForeignKey(StaffPage, null=True, on_delete=models.SET_NULL)
