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
    
