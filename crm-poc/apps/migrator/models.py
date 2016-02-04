from django.db import models
from django.db import transaction
from django.core.exceptions import ValidationError

from model_utils.models import TimeStampedModel

from cdms_api import api

from .utils import parse_cdms_date


class CDMSModel(TimeStampedModel):
    cdms_pk = models.CharField(max_length=255, blank=True)

    cdms_migrator = None  # should be subclass of migrator.cdms_migrator.BaseCDMSMigrator

    def save_without_cdms(self, *args, **kwargs):
        super(CDMSModel, self).save(*args, **kwargs)

    def clean(self):
        super(CDMSModel, self).clean()

        cdms_data, changed = self._get_cdms_obj()
        if changed:
            # this shouldn't happen often as django 'gets' the object
            # at each request and when we get, we update as well so
            # the this conflict happens only if there's a cdms write
            # between the django get and the save (very unlikely).
            conflicting_fields = self.cdms_migrator.get_conflicting_fields(self, cdms_data)
            if conflicting_fields:
                raise ValidationError({
                    field: 'cdms change: {cdms}, your change: {yours}'.format(
                        cdms=conflicting_data['theirs'],
                        yours=conflicting_data['yours']
                    ) for field, conflicting_data in conflicting_fields.items()
                })

    def _get_cdms_obj(self):
        if not self.pk:
            return (None, False)

        cdms_data = api.get(self.cdms_migrator.service, self.cdms_pk)
        cdms_modified_on = parse_cdms_date(cdms_data['ModifiedOn'])

        change_delta = (cdms_modified_on - self.modified).total_seconds()

        if change_delta < -2:
            raise Exception('Django Model changed without being syncronised to CDMS, this should not happen')

        changed = change_delta > 2
        return (cdms_data, changed)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.pk:
                # save this
                super(CDMSModel, self).save(*args, *kwargs)

                # create in cdms
                cdms_data = self.cdms_migrator.update_cdms_data_from_local(self, {})

                cdms_obj = api.create(self.cdms_migrator.service, data=cdms_data)
                self.cdms_pk = cdms_obj['{service}Id'.format(service=self.cdms_migrator.service)]
                self.__class__.objects.filter(pk=self.pk).update(cdms_pk=self.cdms_pk)
            else:
                # get from cdms
                cdms_data, changed = self._get_cdms_obj()
                if changed:
                    # should never happen if self.clean called before saving
                    raise Exception()

                # save this
                super(CDMSModel, self).save(*args, *kwargs)

                cdms_data = self.cdms_migrator.update_cdms_data_from_local(self, cdms_data)
                cdms_obj = api.update(self.cdms_migrator.service, guid=self.cdms_pk, data=cdms_data)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            super(CDMSModel, self).delete(*args, **kwargs)

            api.delete(self.cdms_migrator.service, guid=self.cdms_pk)

    def sync_from_cdms(self):
        with transaction.atomic():
            # get from cdms
            cdms_data, changed = self._get_cdms_obj()
            if not cdms_data or not changed:
                return False

            self.cdms_migrator.update_local_from_cdms_data(self, cdms_data)
            self.save_without_cdms()
            api.update(self.cdms_migrator.service, guid=self.cdms_pk, data=cdms_data)
            return True

    class Meta:
        abstract = True
