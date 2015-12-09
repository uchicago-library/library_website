from django.db import models

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
    
