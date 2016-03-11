from django.db import models
from migrator.models import CDMSModel
from migrator.managers import CDMSManager
from migrator.cdms_migrator import BaseCDMSMigrator

from cdms_api import fields as cdms_fields


class MigratorManager(CDMSManager):
    use_for_related_fields = True


class SimpleMigrator(BaseCDMSMigrator):
    fields = {
        'name': cdms_fields.StringField('Name'),
        'dt_field': cdms_fields.DateTimeField('DateTimeField'),
        'int_field': cdms_fields.IntegerField('IntField'),
    }
    service = 'Simple'


class RelatedObj(models.Model):
    pass


class SimpleObj(CDMSModel):
    name = models.CharField(max_length=250)
    dt_field = models.DateTimeField(null=True)
    int_field = models.IntegerField(null=True)

    d_field = models.DateField(null=True)
    fk_obj = models.ForeignKey(RelatedObj, null=True)

    objects = MigratorManager()
    django_objects = models.Manager()
    cdms_migrator = SimpleMigrator()

    class Meta:
        ordering = ['modified']
