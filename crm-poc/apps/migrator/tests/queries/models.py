from django.db import models
from migrator.models import CDMSModel
from migrator.managers import CDMSManager
from migrator.cdms_migrator import BaseCDMSMigrator


class MigratorManager(CDMSManager):
    use_for_related_fields = True


class SimpleMigrator(BaseCDMSMigrator):
    fields = {
        'name': 'Name',
    }
    service = 'Simple'


class SimpleObj(CDMSModel):
    name = models.CharField(max_length=250)

    objects = MigratorManager()
    django_objects = models.Manager()
    cdms_migrator = SimpleMigrator()
